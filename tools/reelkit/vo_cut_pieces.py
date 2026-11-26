import numpy as np,subprocess,json,sys
SR=48000
x=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i','bounce48.wav','-f','f32le','-'],capture_output=True).stdout,np.float32).copy()
H=480
lvl=lambda i: 20*np.log10(np.sqrt((x[i:i+H]**2).mean())+1e-9)
def quiet(t0,t1):
    c=[(lvl(i),i) for i in range(int(t0*SR),int(t1*SR),H//4)]; return min(c)
def refine(a,b,keep=0.12,w=0.3):
    la,ia=quiet(a-0.3,a+0.02); lb,ib=quiet(b-0.02,b+w)
    # tighten leading/trailing silence
    i=ia
    while i<ib and lvl(i)<-52: i+=H//4
    ia=max(ia,i-int(keep*SR))
    j=ib
    while j>ia and lvl(j)<-52: j-=H//4
    ib=min(ib,j+H+int(keep*SR))
    return ia,ib,la,lb
def tighten(seg):
    # shorten internal silences > 0.45s to 0.25s
    out=[];i=0;n=len(seg);run=None
    e=[20*np.log10(np.sqrt((seg[k:k+H]**2).mean())+1e-9) for k in range(0,n-H,H)]
    k=0;cuts=[]
    while k<len(e):
        if e[k]<-45:
            s=k
            while k<len(e) and e[k]<-45: k+=1
            if (k-s)*H/SR>0.45: cuts.append((s*H+int(0.125*SR),k*H-int(0.125*SR)))
        else: k+=1
    res=[];p=0;F=int(0.015*SR)
    for a,b in cuts:
        res.append(seg[p:a]); p=b
    res.append(seg[p:])
    return xfade(res),len(cuts)
def xfade(parts):
    F=int(0.015*SR); out=parts[0].copy()
    for q in parts[1:]:
        q=q.copy(); r=np.linspace(0,1,F)
        out[-F:]=out[-F:]*(1-r)+q[:F]*r; out=np.concatenate([out,q[F:]])
    return out
name=sys.argv[1]; P=json.loads(sys.argv[2])
pieces=[];segs=[];report=[]
for p in P:
    a,b=p[0],p[1]; ia,ib,la,lb=refine(a,b,w=(p[2] if len(p)>2 else 0.3)); pieces.append([round(ia/SR,3),round(ib/SR,3)])
    s=x[ia:ib].copy(); F=int(0.015*SR); s[:F]*=np.linspace(0,1,F); s[-F:]*=np.linspace(1,0,F)
    s,nc=tighten(s); segs.append(s); report.append((round(ia/SR,2),round(ib/SR,2),round(la,0),round(lb,0),nc))
gap=np.zeros(int(0.06*SR),np.float32)  # edges already carry ~0.12s each side
out=np.concatenate(sum([[s,gap] for s in segs],[])[:-1])
json.dump(pieces,open(name+'_pieces.json','w'))
st=np.stack([out,out],1)
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar','48000','-ac','2','-i','-','-c:a','pcm_s24le',name+'_vo.wav'],input=st.astype(np.float32).tobytes())
print(name,'len %.2fs'%(len(out)/SR)); [print(' ',r) for r in report]
