import subprocess,numpy as np,sys,re,json
SR=48000
reel,track,off,name,c0,c1,out=sys.argv[1],sys.argv[2],float(sys.argv[3]),sys.argv[4],float(sys.argv[5]),float(sys.argv[6]),sys.argv[7]
def ld(f,ss=0,t=None):
    a=['ffmpeg','-v','error','-ss',str(ss),'-i',f]+(['-t',str(t)] if t else [])+['-ac','1','-ar',str(SR),'-f','f32le','-']
    return np.frombuffer(subprocess.run(a,capture_output=True).stdout,np.float32).copy()
def lufs(x):
    p=subprocess.run(['ffmpeg','-v','info','-nostats','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-af','ebur128','-f','null','-'],input=x.astype(np.float32).tobytes(),capture_output=True).stderr.decode()
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS',p)[-1])
v=np.load(name+'_v.npy'); env=np.load(name+'_env.npy')
# cut point: quietest 10ms in [c0,c1]
w=480; cand=[(np.sqrt((v[i:i+w]**2).mean()),i) for i in range(int(c0*SR),int(c1*SR),w//2)]
lvl,ci=min(cand); c=ci+w//2
vo=ld('bounce48.wav',90.30,8.90); f=int(0.015*SR); vo[:f]*=np.linspace(0,1,f); vo[-f:]*=np.linspace(1,0,f)
# match loudness of merch VO to reel speech
L_reel=lufs(v[int(3*SR):c]); L_vo=lufs(vo); gv=10**((L_reel-L_vo)/20)
pad=np.zeros(int(0.15*SR),np.float32)
ins=np.concatenate([pad,vo*gv,pad]); n_ins=len(ins)
newv=np.concatenate([v[:c],ins,v[c:]])
bed=float(np.median(env[c-int(2*SR):c]))
newenv=np.concatenate([env[:c],np.full(n_ins,bed),env[c:]])
N=len(newv); m=ld(track,off,N/SR+0.2)[:N]
mix=newv+newenv*m
pk=20*np.log10(np.abs(mix).max())
st=np.stack([mix,mix],1).astype(np.float32)
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-c:a','pcm_s24le',out],input=st.tobytes())
print(json.dumps(dict(name=name,cut=round(c/SR,3),cut_db=round(20*np.log10(lvl+1e-9),1),ins=round(n_ins/SR,3),gv=round(gv,3),bed=round(bed,4),peak=round(pk,1),L_mix=lufs(mix))))
