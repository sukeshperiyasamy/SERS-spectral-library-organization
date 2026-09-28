import pickle,numpy as np,pandas as pd
from scipy.signal import find_peaks
D=pickle.load(open('lr2.pkl','rb'));E=pickle.load(open('lr3.pkl','rb'));F=pickle.load(open('lr4.pkl','rb'));G5=pickle.load(open('lr5.pkl','rb'))
P=D['P'];x=D['x'];ks=E['ks'];BT=F['BT'].copy();A=G5['A'];G=G5['G'];res=G5['res']
def hat(c,b): j=np.argmin(abs(x-b));return c[j-3:j+4].max()
for i,r in BT.iterrows():
  b=r.band; rel=[];gs=[];sa=[]
  for k in ks:
    c=P[k]['p']['corr'];n=P[k]['p']['noise'];rel.append(hat(c,b)/hat(c,425.4))
    j=np.argmin(abs(x-b));gs.append(A[k]*G[j]/max(hat(c,b),1));sa.append(hat(res[k],b)/n)
  BT.loc[i,'rel425_mean']=np.mean(rel);BT.loc[i,'rel425_cv']=100*np.std(rel,ddof=1)/np.mean(rel)
  BT.loc[i,'glass_share_pct']=100*np.median(gs);BT.loc[i,'snr_after_glass_removal']=np.median(sa)
def cls(r):
  if r.glass_zone and r.glass_share_pct>50: return 'C3 - glass zone (glass-dominated)'
  if r.in_blank or r.glass_share_pct>50: return 'C3 - background / glass'
  if r.det_frac>=1 and r.snr_median>=15 and r.glass_share_pct<25 and r.rel425_cv<=30: return 'C1 - primary marker'
  if r.det_frac>=0.8 and r.snr_after_glass_removal>=5 and r.glass_share_pct<25: return 'C2 - supporting peak'
  return 'C4 - uncertain / weak'
BT['class']=BT.apply(cls,axis=1)
BT.loc[BT.band.round()==1458,'note']='Exploratory: appears after subtracting the short-blank glass shape (8/10); consistent with CH2/CH3 deformation 1450 (LPS-1) - tentative'
BT.loc[BT.band.round()==425,'note']='Strongest LPS band; also in April 2026 and 28 Sep screening data; absent from blanks and NAM; no literature assignment'
BT.loc[BT.band.round()==1081,'note']='Broad band; glass Si-O feature at ~1091 contributes ~14 %; best literature match 1075 (LPS-3 normal Raman)'
pd.set_option('display.width',250)
print(BT[['band','detected','pos_mean','pos_sd','snr_median','rel425_mean','rel425_cv','glass_share_pct','snr_after_glass_removal','class']].round(2).to_string())
pickle.dump(BT,open('lr6.pkl','wb'))
