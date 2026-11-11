import sys, numpy as np, subprocess
src,out=sys.argv[1],sys.argv[2]; sr=48000
x=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',src,'-f','f32le','-ac','1','-ar',str(sr),'-'],capture_output=True).stdout,np.float32).copy()
h=480;n=len(x)//h;fr=x[:n*h].reshape(n,h)
e=20*np.log10(np.sqrt((fr**2).mean(1))+1e-9)
F=np.abs(np.fft.rfft(fr*np.hanning(h),axis=1));fq=np.fft.rfftfreq(h,1/sr)
low=(F[:,fq<1000]**2).sum(1)/((F**2).sum(1)+1e-12)
sil=e<-150
cuts=[]
i=0
while i<n:
  if sil[i]:
    j=i
    while j<n and sil[j]: j+=1
    if j-i>=10:
      # tail before silence i
      k=i
      while k>0 and not sil[k-1] and low[k-1]<0.5 and e[k-1]<-35: k-=1
      if i-k>=6: cuts.append((k,i,'tail'))
      # lead after silence j
      k=j
      while k<n and not sil[k] and low[k]<0.5 and e[k]<-35: k+=1
      if k-j>=6: cuts.append((j,k,'lead'))
    i=j
  else: i+=1
F10=int(0.01*sr); y=x.copy()
keep=np.ones(len(x),bool)
for a,b,t in cuts:
  keep[a*h:b*h]=False
  print(f"trim {t} {a/100:.2f}-{b/100:.2f} max {e[a:b].max():.0f} dB")
# apply fades at new edges
idx=np.where(np.diff(keep.astype(int))!=0)[0]
for p in idx:
  if keep[p] and not keep[p+1]: y[max(0,p-F10+1):p+1]*=np.linspace(1,0,min(F10,p+1))
  elif not keep[p] and keep[p+1]: y[p+1:p+1+F10]*=np.linspace(0,1,len(y[p+1:p+1+F10]))
y=y[keep]
subprocess.run(['ffmpeg','-y','-v','error','-f','f32le','-ar',str(sr),'-ac','1','-i','-','-c:a','pcm_s24le',out],input=y.tobytes())
print(f"{len(x)/sr:.2f}s -> {len(y)/sr:.2f}s, {len(cuts)} trims")
