import sys,os,pickle,numpy as np,pandas as pd
sys.path.insert(0,os.path.expanduser('~/work')); from lib2 import *
A=pickle.load(open(os.path.expanduser('~/work/audit.pkl'),'rb'))
B=A[A.cls!='OUT_OF_SCOPE'].copy().reset_index(drop=True)
MARK={'NAM':[541,870,929,955,1023,1127],'LTA':[802,861,1092,1459],'SUSPECT':[620,1001,1031,1602]}
P={}
for i,r in B.iterrows():
  meta,rs,dk,raw,ds=read_any(os.path.join(ROOT,r.orig)); pr=process(rs,ds,raw); P[i]=pr
  ci=np.interp(X,pr['x'],pr['corr'])
  B.loc[i,'noise']=pr['noise']; B.loc[i,'nspikes']=pr['nspikes']; B.loc[i,'baseline_level']=float(np.median(pr['base']))
  B.loc[i,'snr_max']=ci.max()/pr['noise']
  mk=MARK.get(r.cls)
  if mk:
    h=[ci[(X>=m-8)&(X<=m+8)].max() for m in mk]; B.loc[i,'marker_max']=max(h); B.loc[i,'snr']=max(h)/pr['noise']
  else:
    B.loc[i,'marker_max']=np.nan; B.loc[i,'snr']=ci.max()/pr['noise']
# correlation vs class mean of unsaturated, snr>=10 spectra
for a in ['NAM','LTA']:
  ok=(B.cls==a)&(~B.saturated)&(B.snr>=10)
  M=np.mean([np.interp(X,P[i]['x'],P[i]['norm']) for i in B[ok].index],0)
  for i in B[B.cls==a].index: B.loc[i,'r_class']=np.corrcoef(np.interp(X,P[i]['x'],P[i]['norm']),M)[0,1]
pickle.dump((B,P),open(os.path.expanduser('~/work/qc.pkl'),'wb'))
pd.set_option('display.width',220)
print(B[(B.r_class<0.9)][['orig','power','int_s','acc','snr','r_class','saturated','nspikes']].to_string())
print(B.groupby('cls').nspikes.describe())
