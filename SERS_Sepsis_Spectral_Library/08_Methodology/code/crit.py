import sys,os,pickle,numpy as np,pandas as pd
from scipy.signal import find_peaks
sys.path.insert(0,os.path.expanduser('~/work')); from lib2 import *; from lit_v2 import MLIT
B,P,A,G,GZ=pickle.load(open(os.path.expanduser('~/work/v2.pkl'),'rb'))
PK=pickle.load(open(os.path.expanduser('~/work/an2.pkl'),'rb'))[0]; O,S,CR=pickle.load(open(os.path.expanduser('~/work/nam70.pkl'),'rb'))
I=lambda i,k:np.interp(X,P[i]['x'],P[i][k])
def det(idx,m):
  n=0
  for i in idx:
    c=I(i,'corr'); pk,_=find_peaks(c,prominence=5*P[i]['noise'],distance=5)
    if len(pk) and np.min(abs(X[pk]-m))<=6: n+=1
  return 100*n/len(idx)
val=B[(B.cls=='NAM')&B.orig.str.contains('70p-5ac-10s-diifrentpoint')&(B.qc_status=='Valid')].index
ltav=B[(B.cls=='LTA')&(B.qc_status=='Valid')].index
rows=[]
for _,p in PK.iterrows():
  a=p.analyte; m=p.nominal
  if a=='NAM':
    cr=CR[CR.peak==(830 if m==830 else (458 if m==458 else m))]
    cr=CR[(CR.peak-m).abs()<=3]
    days=cr.iloc[0][[c for c in CR.columns if c.startswith('det_')]].astype(float) if len(cr) else None
    daymin=float(days.min()) if days is not None else np.nan; ext=det(val,p.pos_mean)
  else:
    daymin=det(ltav,p.pos_mean); ext=np.nan
  retained=100*p.glass_corr_height/p.height_mean
  edge=min(p.pos_mean-400,1800-p.pos_mean)
  c1=(p.n_detected==p.n) and (daymin>=95 if a=='NAM' else daymin>=88)
  c1v=(ext>=100) if a=='NAM' else True
  c2=(p.snr_mean>=15) and (p.cv<=15)
  c3=(not p.glass_zone) and (retained>=90) and edge>=75
  c4=MLIT[(a,m)][7] in ('Low','Moderate','High')
  rows.append(dict(biomarker=a,peak=m,position=f'{p.pos_mean:.1f} ± {p.pos_sd:.1f}',detected_ref=f'{p.n_detected}/{p.n}',
    min_day_detection_pct=daymin,independent_spot_set_pct=ext,snr=p.snr_mean,cv=p.cv,prominence=p.prom_mean,glass_zone=p.glass_zone,glass_retained_pct=retained,edge_distance=edge,
    C1_reproducible=c1 and c1v,C2_SNR_CV=c2,C3_background_separated=c3,C4_literature_plausible=c4,category=MLIT[(a,m)][0]))
CT=pd.DataFrame(rows); pickle.dump(CT,open(os.path.expanduser('~/work/crit.pkl'),'wb'))
pd.set_option('display.width',250); print(CT.round(1).to_string())
