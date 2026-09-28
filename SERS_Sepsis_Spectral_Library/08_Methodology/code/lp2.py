import pickle,numpy as np,pandas as pd
from scipy.signal import savgol_filter
from lib2 import process_v3h
D=pickle.load(open('lp1.pkl','rb'));df=D['df'];P=D['P'];x=D['x']
N=pickle.load(open('ln1.pkl','rb'));NAM=N['NAM'];LTA=N['LTA'];OLD=N['OLD']
GZ=(x>=1308)&(x<=1455);keep=~GZ
df['note']=''
for k in ['60_LPS_Bulk_06','60_LPS_Bulk_07']:
  q=P[k]; ds=q['raw']-q['dk']; p=process_v3h(q['rs'],ds,q['raw']); q['p']=p; q['ds']=ds
  i=df.index[df.key==k][0]; c=p['corr']; out=keep&(x>420)&(x<1780); kk=np.argmax(np.where(out,c,-1e9))
  hp=lambda y: y-savgol_filter(y,31,2); rw=(q['rs']>1550)&(q['rs']<1800)
  df.loc[i,['noise','strong_pos','strong_h','snr','ripple','rNAM','rLTA','rOLD']]=[p['noise'],x[kk],c[kk],c[kk]/p['noise'],hp(ds)[rw].std(),np.corrcoef(c[keep],NAM[keep])[0,1],np.corrcoef(c[keep],LTA[keep])[0,1],np.corrcoef(c[keep],OLD[keep])[0,1]]
  df.loc[i,'note']='Instrument software applied Savitzky-Golay smoothing to the stored dark-subtracted column (header Data Pretreat_0); dark-subtracted recomputed as Raw - Dark (same definition as all other files)'
def nz(c): c=c-c[keep].min(); return c/c[keep].max()
def qc(r):
  if r.category=='Glass_Blank': return ('BLANK-SATURATED' if r.nsat>0 else 'BLANK-OK'),''
  if r.nsat>0: return 'FAIL','Saturated in 400-1800'
  if r.ripple>50: return 'FAIL','Ripple (fixed-pattern residual %.0f > 50 counts)'%r.ripple
  if r.snr<10: return 'FAIL','SNR < 10'
  return 'PASS',''
q=df.apply(qc,axis=1);df['QC']=[a for a,b in q];df['QC_reason']=[b for a,b in q]
# reproducibility within each power among PASS; flag r to set mean <0.85
for pw in (60,70,80):
  s=df[(df.power==pw)&(df.category=='LPS_Bulk')&(df.QC=='PASS')]
  if len(s)<2: continue
  Nm={k:nz(P[k]['p']['corr']) for k in s.key}; mn=np.mean(list(Nm.values()),0)
  for i in s.index:
    k=df.key[i]; others=np.mean([v for kk,v in Nm.items() if kk!=k],0)
    df.loc[i,'r_to_others_mean']=np.corrcoef(Nm[k][keep],others[keep])[0,1]
    df.loc[i,'r_to_others_full']=np.corrcoef(Nm[k],others)[0,1]
pickle.dump(dict(df=df,P=P,x=x,NAM=NAM,LTA=LTA,OLD=OLD),open('lp2.pkl','wb'))
pd.set_option('display.width',250)
print(df[df.category=='LPS_Bulk'][['key','ds_med','noise','strong_pos','snr','ripple','rNAM','rOLD','rBlank','r_to_others_mean','r_to_others_full','QC']].round(3).to_string())
