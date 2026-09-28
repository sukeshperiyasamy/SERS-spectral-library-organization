import sys,os,pickle,numpy as np,pandas as pd
from scipy.signal import savgol_filter
sys.path.insert(0,os.path.expanduser('~/work')); from lib2 import *
B,P,A,G,GZ=pickle.load(open(os.path.expanduser('~/work/v2.pkl'),'rb'))
rows=[]
for a,mk in [('NAM',[541,830,870,929,955,1023,1127]),('LTA',[802,861,1092,1459])]:
  R=B[B.in_reference&(B.cls==a)]
  for i in R.index:
    x=P[i]['x']; y=P[i]['despiked']; b0=als(savgol_filter(y,11,3))
    base_raw={}
    for lab,ys in [('none',y),('SG7/3',savgol_filter(y,7,3)),('SG11/3',savgol_filter(y,11,3)),('SG15/3',savgol_filter(y,15,3)),('SG21/3',savgol_filter(y,21,3))]:
      c=ys-b0
      for m in mk:
        w=(x>=m-8)&(x<=m+8); j=np.argmax(c[w]); rows.append(dict(test='smoothing',biomarker=a,setting=lab,peak=m,h=c[w][j],pos=x[w][j],i=i))
    ys=savgol_filter(y,11,3)
    for lam in [1e4,1e5,1e6]:
      for p in [0.001,0.01,0.05]:
        c=ys-als(ys,lam,p)
        for m in mk:
          w=(x>=m-8)&(x<=m+8); j=np.argmax(c[w]); rows.append(dict(test='ALS',biomarker=a,setting=f'lambda={lam:.0e}, p={p}',peak=m,h=c[w][j],pos=x[w][j],i=i))
D=pd.DataFrame(rows)
ref=D[(D.test=='smoothing')&(D.setting=='none')].set_index(['i','peak']).h
D['h_rel_to_unsmoothed']=D.apply(lambda r:r.h/ref[(r.i,r.peak)],axis=1)
refp=D[(D.test=='smoothing')&(D.setting=='none')].set_index(['i','peak']).pos
D['pos_shift']=D.apply(lambda r:r.pos-refp[(r.i,r.peak)],axis=1)
Sm=D[D.test=='smoothing'].groupby(['biomarker','setting']).agg(height_vs_unsmoothed=('h_rel_to_unsmoothed','mean'),max_abs_shift=('pos_shift',lambda s:s.abs().max())).reset_index()
base=D[(D.test=='ALS')&(D.setting=='lambda=1e+05, p=0.01')].set_index(['i','peak']).h
D2=D[D.test=='ALS'].copy(); D2['h_rel_to_default']=D2.apply(lambda r:r.h/base[(r.i,r.peak)],axis=1)
Al=D2.groupby(['biomarker','setting']).h_rel_to_default.agg(['mean','min','max']).reset_index()
# noise reduction by SG
nr=[]
for i in B[B.in_reference].index:
  y=P[i]['despiked']; x=P[i]['x']; w=(x>1700)&(x<1800)
  for win in [7,11,15,21]:
    ys=savgol_filter(y,win,3); nr.append(dict(biomarker=B.cls[i],window=win,noise_ratio=np.std(np.diff(ys[w]))/np.std(np.diff(y[w]))))
NR=pd.DataFrame(nr).groupby(['biomarker','window']).noise_ratio.mean().reset_index()
pickle.dump(dict(Sm=Sm,Al=Al,NR=NR),open(os.path.expanduser('~/work/sens.pkl'),'wb'))
print(Sm.round(3).to_string()); print(Al.round(3).to_string()); print(NR.round(3).to_string())
