import sys,os,pickle,numpy as np,pandas as pd
from scipy.signal import find_peaks,peak_prominences
sys.path.insert(0,os.path.expanduser('~/work')); from lib2 import *
B,P,A,G,GZ=pickle.load(open(os.path.expanduser('~/work/v2.pkl'),'rb'))
I=lambda i,k:np.interp(X,P[i]['x'],P[i][k])
groups={'REF 90%/30s/5acc':B[B.in_reference&(B.cls=='NAM')].index,'70%/60s/5acc':B[(B.cls=='NAM')&(B.int_s==60)&(B.power==70)].index}
CAND=[458,487,541,584,830,870,929,955,1023,1059,1127,1155,1249,1345,1392,1450,1589]
out=[];summ=[]
Mref=np.mean([I(i,'norm') for i in groups['REF 90%/30s/5acc']],0)
for g,idx in groups.items():
  C=np.array([I(i,'corr') for i in idx]); N=np.array([I(i,'norm') for i in idx]); nz=np.array([P[i]['noise'] for i in idx])
  det=[X[find_peaks(c,prominence=5*z,distance=5)[0]] for c,z in zip(C,nz)]
  for m in CAND:
    w=(X>=m-8)&(X<=m+8); pos=[];h=[];pr=[];snr=[];dn=0
    for k,c in enumerate(C):
      j=np.where(w)[0][np.argmax(c[w])]; pos.append(X[j]); h.append(c[j]); snr.append(c[j]/nz[k]); pr.append(peak_prominences(c,[j])[0][0])
      if len(det[k]) and np.min(abs(det[k]-X[j]))<=5: dn+=1
    out.append(dict(group=g,peak=m,n=len(idx),pos_mean=np.mean(pos),pos_sd=np.std(pos,ddof=1),h_mean=np.mean(h),h_sd=np.std(h,ddof=1),cv=100*np.std(h,ddof=1)/np.mean(h),snr=np.mean(snr),prom=np.mean(pr),prom_snr=np.mean(np.array(pr)/nz),freq=dn,rel=np.mean(h)/C.mean(0).max(),glass=bool(GZ[np.argmin(abs(X-m))])))
  pr_r=[np.corrcoef(N[a],N[b])[0,1] for a in range(len(N)) for b in range(a+1,len(N))]
  r_ref=[np.corrcoef(n[~GZ],Mref[~GZ])[0,1] for n in N]
  summ.append(dict(group=g,n=len(idx),snr_mean=np.mean([B.snr[i] for i in idx]),snr_sd=np.std([B.snr[i] for i in idx],ddof=1),pairwise_r=np.mean(pr_r),r_to_ref_mean_exglass=np.mean(r_ref),
     strongest_marker=np.mean([B.marker_max[i] for i in idx]),strongest_sd=np.std([B.marker_max[i] for i in idx],ddof=1),baseline=np.mean([B.baseline_level[i] for i in idx])))
# cross-day robustness: all Valid NAM spectra, per peak detection frequency by date
V=B[(B.cls=='NAM')&(B.qc_status=='Valid')]
cross=[]
for m in CAND:
  fr={}
  for d,g in V.groupby('ymd'):
    hit=0
    for i in g.index:
      c=I(i,'corr'); pk=X[find_peaks(c,prominence=5*P[i]['noise'],distance=5)[0]]
      if len(pk) and np.min(abs(pk-m))<=6: hit+=1
    fr[d]=100*hit/len(g)
  cross.append(dict(peak=m,**{f'det_{k}':round(v) for k,v in fr.items()},overall=round(np.mean(list(fr.values())))))
O=pd.DataFrame(out); S=pd.DataFrame(summ); CR=pd.DataFrame(cross)
pickle.dump((O,S,CR),open(os.path.expanduser('~/work/nam70.pkl'),'wb'))
pd.set_option('display.width',250)
print(S.round(3).to_string()); print(O.round(2).to_string()); print(CR.to_string()); print(V.groupby('ymd').size())
