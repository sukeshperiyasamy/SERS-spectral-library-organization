import pickle,numpy as np,pandas as pd
from scipy.signal import find_peaks,peak_widths
D=pickle.load(open('lr2.pkl','rb'));E=pickle.load(open('lr3.pkl','rb'));F=pickle.load(open('lr4.pkl','rb'))
P=D['P'];x=D['x'];ks=E['ks'];sbc=F['sbc'];BT=F['BT']
# glass template: short blank baseline-corrected, normalised to max in 1308-1455
G=sbc/sbc[(x>=1308)&(x<=1455)].max()
fit=(x>=1290)&(x<=1520)
res={};A={}
for k in ks:
  c=P[k]['p']['corr']
  # least squares c ~ a*G + linear on fit region
  M=np.vstack([G[fit],np.ones(fit.sum()),x[fit]]).T;co=np.linalg.lstsq(M,c[fit],rcond=None)[0];a=co[0]
  A[k]=a;res[k]=c-a*G
print('glass scale a per spectrum:',{k[-7:-4]:round(v) for k,v in A.items()})
# expected glass contribution at key bands relative to band height
for b in [425,478,541,766,861,997,1080,1124,1334,1457,1657]:
  j=np.argmin(abs(x-b));
  frac=[a*G[j]/max(P[k]['p']['corr'][j-3:j+4].max(),1) for k,a in A.items()]
  after=[res[k][j-3:j+4].max()/P[k]['p']['noise'] for k in ks]
  print(f'{b:5d}: glass share of band height median {100*np.median(frac):5.1f}% ; SNR after glass removal median {np.median(after):5.1f}')
# peaks in mean residual inside glass zone
R=np.array([res[k] for k in ks]);mr=R.mean(0);nz=np.mean([P[k]['p']['noise'] for k in ks])/np.sqrt(len(ks))
pk,_=find_peaks(mr,prominence=4*nz,distance=4)
print('residual peaks 1250-1520 after glass removal:',[round(x[j]) for j in pk if 1250<x[j]<1520])
for j in pk:
  if 1250<x[j]<1520:
    det=sum(any(abs(x[find_peaks(res[k],prominence=3*P[k]['p']['noise'],distance=4)[0]]-x[j])<=5) for k in ks)
    print('   ',round(x[j],1),'det',det,'/10')
pickle.dump(dict(G=G,A=A,res=res),open('lr5.pkl','wb'))
