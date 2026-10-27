# LTA bulk re-acquisition: exploratory step (QC classes, core mean, bands) before the reference is written
import os,pickle,warnings
warnings.filterwarnings('ignore')
import numpy as np,pandas as pd
from scipy.signal import find_peaks
from lib2 import X,LIB
H=os.path.dirname(os.path.abspath(__file__))
df=pd.read_pickle(os.path.join(H,'lt1_qc.pkl')); st=pickle.load(open(os.path.join(H,'lt1_store.pkl'),'rb'))
spots=df[(df.category=='LTA_Bulk')&(df.orig.str.extract(r'(\d+)')[0].astype(int)>=9)].copy(); spots['n']=spots.orig.str.extract(r'(\d+)')[0].astype(int)
blanks=df[df.category=='Glass_Blank']
bl=np.mean([st[('Glass_Blank',o)]['corr'] for o in blanks.orig],axis=0)
spots['sat']=spots.nsat>0
prov=spots[(~spots.sat)&(spots.ripple<=50)&(spots.snr1092>=10)&(spots.glass_ratio<8)]
core0=np.mean([st[('LTA_Bulk',o)]['norm'] for o in prov.orig],axis=0)
GZ=(X>=1308)&(X<=1455)
def r_core(o):
    n=st[('LTA_Bulk',o)]['norm']; return float(np.corrcoef(n[~GZ],core0[~GZ])[0,1])
spots['r_core']=[r_core(o) for o in spots.orig]
print(spots[['orig','ripple','nsat','snr1092','glass_ratio','rLTA_apr','r_core']].round(2).to_string())
good=spots[(~spots.sat)&(spots.ripple<=50)&(spots.snr1092>=10)&(spots.glass_ratio<8)&(spots.r_core>=0.8)]
print('strict core n=',len(good),list(good.n))
ext=spots[(~spots.sat)&(spots.ripple<=60)&(spots.snr1092>=10)&(spots.glass_ratio<8)&(spots.r_core>=0.8)]
print('extended core (ripple<=60) n=',len(ext),list(ext.n))
M=np.mean([st[('LTA_Bulk',o)]['corr'] for o in good.orig],axis=0)
SD=np.std([st[('LTA_Bulk',o)]['corr'] for o in good.orig],axis=0,ddof=1)
nz=float(good.noise.mean())
pk,pr=find_peaks(M,prominence=4*nz/np.sqrt(len(good)),distance=4)
print('noise',round(nz,1),'peaks in the mean:')
for ii,j in enumerate(pk):
    print(f'  {X[j]:7.1f} h={M[j]:7.0f} SD={SD[j]:6.0f} CV={100*SD[j]/M[j]:5.1f}% prom={pr["prominences"][ii]:7.0f} blank={bl[j]:6.0f} ({100*bl[j]/M[j]:4.0f}% of band){"  GLASS ZONE" if 1308<=X[j]<=1455 else ""}')
# April comparison
a=pd.read_csv(os.path.join(LIB,'03_Reference_Spectra','LTA','LTA_Bulk_Reference_Mean_SD.csv'),comment='#'); an=np.interp(X,a.iloc[:,0].values,a['Normalised_mean'].values)
nm=(M-M.min())/(M.max()-M.min()); print('r new mean vs April LTA ref:',round(float(np.corrcoef(nm[~GZ],an[~GZ])[0,1]),3))
mk=pd.read_csv(os.path.join(LIB,'03_Reference_Spectra','LTA','LTA_Reference_Marker_Peaks.csv')); print(mk[['role','nominal','pos_mean','height_mean']].to_string())
