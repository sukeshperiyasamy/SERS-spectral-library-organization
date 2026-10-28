# LTA session 28 Oct 2026: dark-frame check. Many files carry a dark with sample light in it (dark median far above the clean dark of the same integration time).
# Diagnostic: re-process those spectra with a clean dark spectrum of the same integration time / accumulations and see whether ripple and shape improve.
import os,re,pickle,warnings
warnings.filterwarnings('ignore')
import numpy as np,pandas as pd
from scipy.signal import savgol_filter
from lib2 import read_any,process_v3h,ROOT,X
SRC=os.path.join(ROOT,'bulk-lta'); H=os.path.dirname(os.path.abspath(__file__))
d=pd.read_pickle(os.path.join(H,'lt9_unique.pkl')); R0=pickle.load(open(os.path.join(H,'lt4_result.pkl'),'rb')); REFN=R0['Nm']; GZ=(X>=1308)&(X<=1455)
CLEAN={(30.0,3):1333,(40.0,2):1443,(45.0,2):1510,(60.0,2):1680}          # dark medians of the clean frames of this session (counts)
dk={}                                                                    # clean dark spectra per (int, acc)
raw_cache={}
for r in d.itertuples():
    k=(r.int_s,r.acc)
    p=os.path.join(SRC,r.rel); meta,rs,dark,raw,ds=read_any(p); raw_cache[r.rel]=(rs,dark,raw,ds)
    if k in CLEAN and abs(r.dark-CLEAN[k])<=40: dk.setdefault(k,[]).append(dark)
CD={k:np.median(np.array(v),axis=0) for k,v in dk.items()}
print('clean dark spectra from',{k:len(v) for k,v in dk.items()})
rows=[]
for r in d.itertuples():
    rs,dark,raw,ds=raw_cache[r.rel]; k=(r.int_s,r.acc); m=(rs>=400)&(rs<=1800)
    expect=CLEAN.get(k,np.nan); leak=bool(np.isfinite(expect) and r.dark-expect>150)
    out=dict(rel=r.rel,leak=leak,dark=r.dark,expect=expect,excess=r.dark-expect if np.isfinite(expect) else np.nan)
    if leak and k in CD:
        ds2=raw-CD[k]; pr=process_v3h(rs,ds2,raw); x=pr['x']; hp=pr['ds']-savgol_filter(pr['ds'],31,2); rm=(x>=1550)&(x<=1800)
        c=np.interp(X,x,pr['corr']); n=np.interp(X,x,pr['norm']); w=(X>=1086)&(X<=1098)
        out.update(ripple2=float(np.std(hp[rm])),noise2=float(pr['noise']),h1092_2=float(c[w].max()),snr2=float(c[w].max()/pr['noise']),rREF2=float(np.corrcoef(n[~GZ],REFN[~GZ])[0,1]),nsat2=r.nsat)
    rows.append(out)
q=pd.DataFrame(rows).drop(columns=['dark']); d=d.merge(q,on='rel'); d.to_pickle(os.path.join(H,'lt10_dark.pkl'))
sp=d[d.role.isin(['spot','samespot'])]
print('files with a leaked dark (excess > 150 counts):',int(sp.leak.sum()),'of',len(sp))
g=sp[sp.leak].groupby(['power','int_s','acc']).agg(n=('rel','count'),dark=('dark','median'),excess=('excess','median'),ripple=('ripple','median'),ripple2=('ripple2','median'),snr=('snr1092','median'),snr2=('snr2','median'),rREF=('rREF','median'),rREF2=('rREF2','median'),h1092=('h1092','median'),h1092_2=('h1092_2','median')).round(1)
print(g.to_string())
c=sp[~sp.leak].groupby(['power','int_s','acc']).agg(n=('rel','count'),dark=('dark','median'),ripple=('ripple','median'),snr=('snr1092','median'),rREF=('rREF','median')).round(1)
print('clean-dark files:'); print(c.to_string())
