# LTA bulk re-acquisition: is the "ripple" fixed-pattern (instrument) or random noise? Is SP_1-8 of the spot folder a copy of the blanks?
import os,re,hashlib,pickle,warnings
warnings.filterwarnings('ignore')
import numpy as np,pandas as pd
from scipy.signal import savgol_filter
from lib2 import read_any,process_v3h,ROOT
SRC=os.path.join(ROOT,'bulk-lta'); H=os.path.dirname(os.path.abspath(__file__))
df=pd.read_pickle(os.path.join(H,'lt1_qc.pkl'))
md=lambda p:hashlib.md5(open(p,'rb').read()).hexdigest()
same=[md(os.path.join(SRC,'45sec-80p-2acc-diffrentspot',f'SP_{i}.csv'))==md(os.path.join(SRC,'glass blank',f'SP_{i}.csv')) for i in range(1,9)]
print('SP_1..8 of the spot folder identical to the glass blanks (MD5):',same)
def hp(folder,f):
    meta,rs,dk,raw,ds=read_any(os.path.join(SRC,folder,f)); pr=process_v3h(rs,ds,raw); x=pr['x']; y=pr['ds']; r=y-savgol_filter(y,31,2); m=(x>=1500)&(x<=1800); return r[m],pr['ds'][m].mean(),raw[(rs>=400)&(rs<=1800)].mean()
res={}
for i in range(1,9): res[('B',i)]=hp('glass blank',f'SP_{i}.csv')
for i in range(9,37): res[('S',i)]=hp('45sec-80p-2acc-diffrentspot',f'SP_{i}.csv')
keys=list(res); A=np.array([res[k][0] for k in keys]); C=np.corrcoef(A)
bl=[j for j,k in enumerate(keys) if k[0]=='B']; sp=[j for j,k in enumerate(keys) if k[0]=='S']
def mean_off(idx_a,idx_b):
    v=[C[a,b] for a in idx_a for b in idx_b if a!=b]; return float(np.mean(v)),float(np.median(v))
print('residual correlation 1500-1800 cm-1: blank-blank',mean_off(bl,bl),'spot-spot',mean_off(sp,sp),'blank-spot',mean_off(bl,sp))
# ripple vs signal
d=df.copy(); d['i']=range(len(d)); sub=d[(d.category=='LTA_Bulk')&(d.index>=8)]
print('corr(ripple, noise)',round(float(np.corrcoef(sub.ripple,sub.noise)[0,1]),3),'corr(ripple, sqrt(raw_med))',round(float(np.corrcoef(sub.ripple,np.sqrt(sub.raw_med))[0,1]),3))
print('ripple/noise ratio median spots',round(float((sub.ripple/sub.noise).median()),2),'blanks',round(float((d[d.category=="Glass_Blank"].ripple/d[d.category=="Glass_Blank"].noise).median()),2))
print('blank raw_med',d[d.category=='Glass_Blank'].raw_med.round(0).tolist()); print('spot raw_med first 6',sub.raw_med.round(0).head(6).tolist())
# first-spot ripple check (project rule: first spot ripple <= 50)
print('spot SP_9 ripple',float(sub.ripple.iloc[0]))
# time trend
print('time order ripple', sub[['orig','acq','ripple','raw_max']].head(8).to_string())
