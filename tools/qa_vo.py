"""Voiceover edit QA. Usage: python3 qa_vo.py SOURCE.wav pieces.json SOURCE_words.json
pieces.json: list of [start,end] seconds in SOURCE kept in order.
SOURCE_words.json: pocketsphinx words [[word,start,end],...] of SOURCE.
Flags: cut edges that are not quiet, words split by a cut, words repeated across a join, total length."""
import sys,json,subprocess,numpy as np
src,pj,wj=sys.argv[1:4]
x=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',src,'-af','pan=mono|c0=c0','-f','f32le','-'],capture_output=True).stdout,np.float32);sr=48000
P=json.load(open(pj)); W=[(w,s,e) for w,s,e in json.load(open(wj)) if not w.startswith(('<','['))]
def db(t0,t1): s=x[max(0,int(t0*sr)):int(t1*sr)]; return 20*np.log10(np.sqrt((s**2).mean())+1e-9)
def clean(w): return w.split('(')[0]
issues=[]; total=0
for i,(a,b) in enumerate(P):
    total+=b-a
    for t,side in ((a,'start'),(b,'end')):
        lvl=db(t-0.02,t+0.02)
        if lvl>-45: issues.append(f'piece {i+1} {side} {t:.2f}s: not quiet ({lvl:.0f} dB), check for a clipped sound')
        for w,s,e in W:
            if s+0.04<t<e-0.04: issues.append(f'piece {i+1} {side} {t:.2f}s: cuts through "{clean(w)}" ({s:.2f}-{e:.2f})')
    if i:
        prev=[clean(w) for w,s,e in W if P[i-1][0]<=s<P[i-1][1]][-3:]
        nxt=[clean(w) for w,s,e in W if a<=s<b][:3]
        for k in range(1,4):
            if prev[-k:]==nxt[:k] and prev[-k:]: issues.append(f'join {i}->{i+1}: repeats "{" ".join(nxt[:k])}" (prev ends "{" ".join(prev)}", next starts "{" ".join(nxt)}")')
        print(f'join {i}->{i+1}: ...{" ".join(prev)} | {" ".join(nxt)}...')
print(f'kept speech {total:.1f}s')
print('ISSUES' if issues else 'PASS'); [print(' -',s) for s in issues]
