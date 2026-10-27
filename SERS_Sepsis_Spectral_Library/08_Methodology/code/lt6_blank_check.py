# LTA session 28 Oct 2026: do the "glass blanks" look like glass only? Compare with the 28 Sep glass blanks and the 9 Feb polystyrene-like spectra.
import os,glob,pickle,warnings
warnings.filterwarnings('ignore')
import numpy as np,pandas as pd
from scipy.signal import find_peaks
from lib2 import read_any,process_v3h,LIB,X
H=os.path.dirname(os.path.abspath(__file__)); R=pickle.load(open(os.path.join(H,'lt4_result.pkl'),'rb'))
def proc(p):
    meta,rs,dk,raw,ds=read_any(p); pr=process_v3h(rs,ds,raw); return np.interp(X,pr['x'],pr['corr']),np.interp(X,pr['x'],pr['norm']),pr['noise']
BL=R['BL']; blm=(BL-BL.min())/(BL.max()-BL.min())
pk,pr_=find_peaks(BL,prominence=60,width=3); print('blank (28 Oct) peaks:',[(round(float(X[j])),round(float(BL[j]))) for j in pk])
# old glass blanks of 28 Sep (short unsaturated blank) and 29 May
rd=os.path.join(LIB,'01_Raw_Data_Renamed')
old=sorted(glob.glob(os.path.join(rd,'Glass_Blank','Glass_Blank_20260928_P060pct_T05s_A01_S0*_short.csv')))+sorted(glob.glob(os.path.join(rd,'Glass_Blank','Glass_Blank_20260529_*S01.csv')))
polys=sorted(glob.glob(os.path.join(rd,'Excluded','Unconfirmed_LabelledLTA_20260209*.csv')))[:12]
print('old blanks',[os.path.basename(o) for o in old][:3],'| 9 Feb files',len(polys))
GZ=(X>=1308)&(X<=1455)
def r(a,b):
    k=~GZ; return float(np.corrcoef(a[k],b[k])[0,1])
for o in old[:3]:
    c,n,nz=proc(o); print('r(new blank mean, old glass blank %s)=%.2f'%(os.path.basename(o)[12:40],r(blm,n)))
if polys:
    P=np.mean([proc(p)[1] for p in polys],axis=0); print('r(new blank mean, 9 Feb polystyrene-like mean) =%.2f'%r(blm,P))
    pp,_=find_peaks(P,prominence=0.05,width=2); print('9 Feb mean peaks:',[round(float(X[j])) for j in pp])
# do the LTA spots carry the same sharp bands?
PSB=[621,1001,1031,1155,1583,1602]
for s in R['spots']:
    if s['n'] in R['core']:
        c=s['corr']; sn=s['noise']; out=[]
        for b in PSB:
            w=(X>=b-4)&(X<=b+4); out.append(round(float(c[w].max()/sn),1))
        print('SP_%d SNR at PS bands %s'%(s['n'],out))
print('blank mean SNR at PS bands',[round(float(BL[(X>=b-4)&(X<=b+4)].max()/np.mean([b_['noise'] for b_ in R['blanks']])),1) for b in PSB])
