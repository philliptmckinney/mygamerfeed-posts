import subprocess,numpy as np,glob,sys
from numpy.fft import rfft,irfft
SR=4000
def ld(f,ss=None,t=None):
    a=['ffmpeg','-v','error']+(['-ss',str(ss)] if ss is not None else [])+['-i',f]+(['-t',str(t)] if t else [])+['-ac','1','-ar',str(SR),'-f','f32le','-']
    return np.frombuffer(subprocess.run(a,capture_output=True).stdout,np.float32)
tracks={f:ld(f) for f in glob.glob('/mnt/user-data/uploads/Music/*.mp3')}
for reel in sys.argv[1:]:
    d=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',reel],capture_output=True,text=True).stdout)
    q=ld(reel,d-1.8,1.6); q=q-q.mean()
    best=[]
    for f,x in tracks.items():
        n=len(x)+len(q); N=1<<int(np.ceil(np.log2(n)))
        c=irfft(rfft(x,N)*np.conj(rfft(q,N)),N)[:len(x)-len(q)]
        e=np.sqrt(np.convolve(x**2,np.ones(len(q)),'valid')[:len(c)])+1e-6
        nc=c/(e*np.linalg.norm(q)); i=nc.argmax(); best.append((nc[i],i/SR,f.split('/')[-1]))
    best.sort(reverse=True); print(reel.split('/')[-1], f'end={d:.2f}', [(round(a,3),round(b,2),n) for a,b,n in best[:2]])
