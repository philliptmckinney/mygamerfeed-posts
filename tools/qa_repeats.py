"""Catch false starts and restarts that full-file transcription hides.
Usage: python3 qa_repeats.py EDIT.wav WHISPER_MODEL_DIR
Splits the edit at pauses (>=0.25s below -45 dB), transcribes every phrase on its own,
and flags phrases whose opening words repeat in the next phrase (a restart) or that end cut off."""
import sys,subprocess,numpy as np,re
from faster_whisper import WhisperModel
src,md=sys.argv[1],sys.argv[2]
x=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',src,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout,np.float32)
sr=16000;h=160;e=20*np.log10(np.sqrt((x[:len(x)//h*h].reshape(-1,h)**2).mean(1))+1e-9);q=e<-45;n=len(e)
ph=[];i=0;start=None
while i<n:
    if not q[i] and start is None: start=i
    if q[i] and start is not None:
        j=i
        while j<n and q[j]: j+=1
        if j-i>=25 or j>=n: ph.append((start,i)); start=None
        i=j; continue
    i+=1
if start is not None: ph.append((start,n))
m=WhisperModel(md,device='cpu',compute_type='int8')
T=[]
for a,b in ph:
    seg=x[a*h:b*h]
    if len(seg)<sr*0.12: continue
    s,_=m.transcribe(np.concatenate([np.zeros(4000,np.float32),seg,np.zeros(8000,np.float32)]),language='en',condition_on_previous_text=False)
    t=' '.join(z.text.strip() for z in s); T.append((a/100,b/100,t)); print(f'{a/100:6.2f}-{b/100:6.2f} {t}')
w=lambda t:re.findall(r"[a-z0-9']+",t.lower())
bad=0
for k in range(len(T)-1):
    A,B=w(T[k][2]),w(T[k+1][2])
    if len(A)>=2 and len(B)>=2 and A[:2]==B[:2]:
        print(f'RESTART? {T[k][0]:.2f}: "{T[k][2]}" then "{T[k+1][2]}"'); bad+=1
    if T[k][2].endswith(('...','-')):
        print(f'CUT OFF? {T[k][0]:.2f}: "{T[k][2]}"'); bad+=1
print('REPEATS PASS' if not bad else f'{bad} to check')
