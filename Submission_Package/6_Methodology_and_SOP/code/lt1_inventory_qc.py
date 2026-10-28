# LTA bulk re-acquisition (folder bulk-lta, Oct 2026): inventory and QC of every spectrum (read only)
import os,re,pickle,warnings
warnings.filterwarnings('ignore')
import numpy as np,pandas as pd
from scipy.signal import savgol_filter,find_peaks
from lib2 import read_any,process_v3h,LIB,ROOT,X
SRC=os.path.join(ROOT,'bulk-lta')
def natkey(s): return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)',s)]
def refspec(a):
    d=pd.read_csv(os.path.join(LIB,'03_Reference_Spectra',a,f'{a}_Bulk_Reference_Mean_SD.csv'),comment='#'); return np.interp(X,d.iloc[:,0].values,d['Normalised_mean'].values)
REF={a:refspec(a) for a in ('NAM','LPS','LTA')}
GZ=(X>=1308)&(X<=1455)
rows=[];store={}
for folder,cat in (('45sec-80p-2acc-diffrentspot','LTA_Bulk'),('glass blank','Glass_Blank')):
    d=os.path.join(SRC,folder)
    for f in sorted(os.listdir(d),key=natkey):
        if not f.lower().endswith('.csv'): continue
        meta,rs,dk,raw,ds=read_any(os.path.join(d,f)); m=(rs>=400)&(rs<=1800)
        pr=process_v3h(rs,ds,raw); x=pr['x']; c=np.interp(X,x,pr['corr']); n=np.interp(X,x,pr['norm'])
        hp=pr['ds']-savgol_filter(pr['ds'],31,2); rm=(x>=1550)&(x<=1800); ripple=float(np.std(hp[rm]))
        sat=int((raw[m]>=65535).sum())
        def h(p,t=6):
            w=(X>=p-t)&(X<=p+t); return float(c[w].max())
        glass=float(np.trapz(np.clip(c[GZ],0,None),X[GZ])); ref800=float(np.trapz(np.clip(c[(X>=800)&(X<=1000)],0,None),X[(X>=800)&(X<=1000)])); gr=glass/ref800 if ref800>0 else np.nan
        nz=float(pr['noise']); k=~GZ
        r={a:float(np.corrcoef(n[k],REF[a][k])[0,1]) for a in REF}
        rows.append(dict(category=cat,folder=folder,orig=f,acq=meta.get('Date',''),power=int(float(meta['laser_powerlevel'])),int_s=float(meta['integration times(sec)']),acc=int(float(meta['average number'])),
                         dark_med=float(np.median(dk[m])),raw_med=float(np.median(raw[m])),raw_max=float(raw[m].max()),nsat=sat,ripple=ripple,noise=nz,
                         h802=h(802),h861=h(861.5),h1092=h(1092),h1459=h(1459),snr1092=h(1092)/nz,glass_ratio=gr,rLTA_apr=r['LTA'],rNAM=r['NAM'],rLPS=r['LPS'],nspikes=int(pr['nspikes']),strong_pos=float(X[np.argmax(np.where(GZ,-1e9,c))]),strong_h=float(np.max(np.where(GZ,-1e9,c)))))
        store[(cat,f)]=dict(corr=c,norm=n,ds=pr['ds'],x=x)
df=pd.DataFrame(rows); df.to_pickle(os.path.join(os.path.dirname(os.path.abspath(__file__)),'lt1_qc.pkl')); pickle.dump(store,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'lt1_store.pkl'),'wb'))
pd.set_option('display.width',260); pd.set_option('display.max_columns',40); pd.set_option('display.max_rows',100)
print(df.groupby(['category','power','int_s','acc']).size())
print(df[['category','orig','acq','dark_med','raw_max','nsat','ripple','noise','h1092','snr1092','glass_ratio','rLTA_apr','rNAM','rLPS']].round(2).to_string())
