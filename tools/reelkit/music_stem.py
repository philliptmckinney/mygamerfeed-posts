import subprocess,numpy as np,sys
SR=48000
def ld(f,ss=0,t=None):
    a=['ffmpeg','-v','error','-ss',str(ss),'-i',f]+(['-t',str(t)] if t else [])+['-ac','1','-ar',str(SR),'-f','f32le','-']
    return np.frombuffer(subprocess.run(a,capture_output=True).stdout,np.float32).copy()
reel,track,off,name=sys.argv[1],sys.argv[2],float(sys.argv[3]),sys.argv[4]
x=ld(reel); m=ld(track,off,len(x)/SR+0.1)[:len(x)]
W=int(0.05*SR); g=np.zeros(len(x)//W+1)
for i in range(0,len(x)-W,W):
    a=x[i:i+W]; b=m[i:i+W]; g[i//W]=np.dot(a,b)/(np.dot(b,b)+1e-9)
# smooth gain (music envelope is slow); median filter
from scipy.ndimage import median_filter
gs=median_filter(g,9)
env=np.interp(np.arange(len(x)),np.arange(len(gs))*W+W/2,gs)
v=x-env*m
np.save(name+'_x.npy',x); np.save(name+'_env.npy',env); np.save(name+'_v.npy',v)
res=lambda a,b: 20*np.log10(np.sqrt((a**2).mean())+1e-9)
d=len(x)/SR
print(name,'music env samples:',' '.join(f'{gs[int(t/0.05)]:.3f}' for t in np.arange(0,d,2)))
print('stem rms end 1.5s',res(v[-int(1.5*SR):],0),'orig',res(x[-int(1.5*SR):],0))
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-ar','16000','-c:a','pcm_s16le',name+'_v16.wav'],input=v.astype(np.float32).tobytes())
