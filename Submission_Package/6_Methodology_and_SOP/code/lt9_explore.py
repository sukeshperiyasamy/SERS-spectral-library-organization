# LTA bulk session of 28 Oct 2026, all folders: inventory by condition and QC (read only, nothing written to the library)
import os,re,pickle,hashlib,warnings
warnings.filterwarnings('ignore')
import numpy as np,pandas as pd
from scipy.signal import savgol_filter,find_peaks
from lib2 import read_any,process_v3h,LIB,ROOT,X
SRC=os.path.join(ROOT,'bulk-lta'); H=os.path.dirname(os.path.abspath(__file__)); GZ=(X>=1308)&(X<=1455)
def nk(s): return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)',s)]
md5=lambda p:hashlib.md5(open(p,'rb').read()).hexdigest()
R0=pickle.load(open(os.path.join(H,'lt4_result.pkl'),'rb')); REFN=R0['Nm']                      # reference v2 (80 %/45 s/2, n=10)
def refspec(a):
    d=pd.read_csv(os.path.join(LIB,'03_Reference_Spectra',a,f'{a}_Bulk_Reference_Mean_SD.csv'),comment='#'); return np.interp(X,d.iloc[:,0].values,d['Normalised_mean'].values)
OTH={a:refspec(a) for a in ('NAM','LPS')}
files=[]
for dp,dn,fn in os.walk(SRC):
    for f in fn:
        if f.lower().endswith('.csv'): files.append(os.path.join(dp,f))
rows=[];st={}
for p in files:
    rel=os.path.relpath(p,SRC).replace('\\','/')
    meta,rs,dk,raw,ds=read_any(p); m=(rs>=400)&(rs<=1800); pr=process_v3h(rs,ds,raw); x=pr['x']
    hp=pr['ds']-savgol_filter(pr['ds'],31,2); rm=(x>=1550)&(x<=1800)
    c=np.interp(X,x,pr['corr']); n=np.interp(X,x,pr['norm'])
    def h(q,t=6): w=(X>=q-t)&(X<=q+t); return float(c[w].max())
    g=np.trapz(np.clip(c[GZ],0,None),X[GZ]); r8=np.trapz(np.clip(c[(X>=800)&(X<=1000)],0,None),X[(X>=800)&(X<=1000)])
    k=~GZ
    rows.append(dict(rel=rel,folder=rel.split('/')[0],sub='/'.join(rel.split('/')[1:-1]),orig=rel.split('/')[-1],acq=meta['Date'],power=int(float(meta['laser_powerlevel'])),int_s=float(meta['integration times(sec)']),acc=int(float(meta['average number'])),
        dark=float(np.median(dk[m])),raw_med=float(np.median(raw[m])),raw_max=float(raw[m].max()),nsat=int((raw[m]>=65535).sum()),ripple=float(np.std(hp[rm])),noise=float(pr['noise']),
        h1092=h(1092),h1459=h(1459),h861=h(861),h539=h(539),h798=h(798),h1246=h(1246),h1751=h(1751),h1000=h(1001,4),snr1092=h(1092)/pr['noise'],glass_ratio=float(g/r8) if r8>0 else np.nan,
        rREF=float(np.corrcoef(n[k],REFN[k])[0,1]),rNAM=float(np.corrcoef(n[k],OTH['NAM'][k])[0,1]),rLPS=float(np.corrcoef(n[k],OTH['LPS'][k])[0,1]),md5=md5(p)))
    st[rel]=dict(corr=c,norm=n,ds=np.interp(X,x,pr['ds']))
df=pd.DataFrame(rows).sort_values('acq').reset_index(drop=True); df['t']=df.acq.str[11:19]
df.to_pickle(os.path.join(H,'lt9_all.pkl')); pickle.dump(st,open(os.path.join(H,'lt9_store.pkl'),'wb'))
pd.set_option('display.width',250); pd.set_option('display.max_columns',40); pd.set_option('display.max_rows',200)
d=df[~((df.folder=='45sec-80p-2acc-diffrentspot')&df.md5.isin(df[df.folder=='glass blank'].md5))].copy()          # SP_1-8 of the spot folder are copies of the blanks
print('files',len(df),'unique',len(d))
# classify roles
def role(r):
    if 'glass' in r.folder and r.folder!='diifrent 60s-2ac-70p': return 'blank'
    if 'same' in r['sub']: return 'samespot'
    return 'spot'
d['role']=d.apply(role,axis=1)
print(d.groupby(['role','power','int_s','acc']).agg(n=('orig','count'),rawmax_med=('raw_max','median'),ripple_med=('ripple','median'),snr_med=('snr1092','median'),h1092_med=('h1092','median'),nsat=('nsat',lambda v:int((v>0).sum())),rREF=('rREF','median')).round(2).to_string())
d.to_pickle(os.path.join(H,'lt9_unique.pkl'))
