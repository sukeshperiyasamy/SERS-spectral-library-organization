import os,pickle,numpy as np,pandas as pd
from scipy.signal import find_peaks
from lib2 import LIB
N=pickle.load(open('ln1.pkl','rb')); df=N['df']; P=N['P']; x=N['x']; OLD=pickle.load(open('ln2_old.pkl','rb'))
GZ=(x>=1308)&(x<=1455); keep=~GZ
ref=pd.read_csv(os.path.join(LIB,'03_Reference_Spectra/NAM/NAM_Reference_Marker_Peaks.csv'))
MK=[(r.role,r.nominal,r.pos_mean,r.glass_zone) for r in ref.itertuples()]
def nz(c): c=c-c[keep].min(); return c/c[keep].max()
sets={}
sets['REF_90_30May_all15']=[(k,v['p']) for k,v in OLD.items()]
sets['REF_90_30May_indep5']=[(k,v['p']) for k,v in OLD.items() if v['spot']=='different spot']
for pw in (60,70,80,90):
  L=df[(df.power==pw)&(df.category=='NAM_Bulk')&(df.QC=='PASS')].library_file
  sets[f'NEW_{pw}_24Sep']=[(f,P[f]['p']) for f in L]
sets['NEW_all_pass_24Sep']=sum([sets[f'NEW_{pw}_24Sep'] for pw in (60,70,80,90)],[])
refmean=np.mean([nz(p['corr']) for _,p in sets['REF_90_30May_all15']],0)
def band(p,b):
  c=p['corr'];n=p['noise'];pk,_=find_peaks(c,prominence=3*n,distance=4)
  near=[k for k in pk if abs(x[k]-b)<=4]
  if not near: return None
  k=min(near,key=lambda k:abs(x[k]-b)); return x[k],c[k],c[k]/n
SS=[];BT=[]
for name,L in sets.items():
  Nm=np.array([nz(p['corr']) for _,p in L]); mn=Nm.mean(0); md=np.median(Nm,0)
  row=dict(set=name,n=len(L),r_mean_vs_REFmean=np.corrcoef(mn[keep],refmean[keep])[0,1])
  if len(L)>1:
    rr=np.corrcoef(Nm[:,keep]);iu=np.triu_indices(len(L),1);row.update(pairwise_r_mean=rr[iu].mean(),pairwise_r_min=rr[iu].min(),r_mean_median=np.corrcoef(mn,md)[0,1],
      frac_within_1SD=float(np.mean(np.abs(mn-md)<Nm.std(0,ddof=1))))
  row['noise_mean']=np.mean([p['noise'] for _,p in L])
  SS.append(row)
  for role,nom,rpos,gz in MK:
    res=[band(p,rpos) for _,p in L]; ok=[r for r in res if r]
    h929=[band(p,929) for _,p in L]
    rel=[r[1]/h[1] for r,h in zip(res,h929) if r and h]
    BT.append(dict(set=name,role=role,ref_pos=rpos,glass_zone=gz,detected=f'{len(ok)}/{len(L)}',det_frac=len(ok)/len(L),
      pos_mean=np.mean([r[0] for r in ok]) if ok else np.nan,pos_sd=np.std([r[0] for r in ok],ddof=1) if len(ok)>1 else np.nan,
      height_mean=np.mean([r[1] for r in ok]) if ok else np.nan,height_cv=100*np.std([r[1] for r in ok],ddof=1)/np.mean([r[1] for r in ok]) if len(ok)>1 else np.nan,
      snr_mean=np.mean([r[2] for r in ok]) if ok else np.nan,rel929_mean=np.mean(rel) if rel else np.nan,rel929_sd=np.std(rel,ddof=1) if len(rel)>1 else np.nan))
SS=pd.DataFrame(SS);BT=pd.DataFrame(BT)
# comparison: new vs ref (all15) on position and relative intensity
R=BT[BT.set=='REF_90_30May_all15'].set_index('ref_pos')
CMP=[]
for name in ['NEW_60_24Sep','NEW_70_24Sep','NEW_80_24Sep','NEW_90_24Sep','NEW_all_pass_24Sep']:
  S=BT[BT.set==name].set_index('ref_pos')
  for rp in R.index:
    CMP.append(dict(set=name,role=R.loc[rp,'role'],ref_pos=rp,glass_zone=R.loc[rp,'glass_zone'],ref_pos_nativeaxis=R.loc[rp,'pos_mean'],new_pos=S.loc[rp,'pos_mean'],
      dpos=S.loc[rp,'pos_mean']-R.loc[rp,'pos_mean'],new_detected=S.loc[rp,'detected'],ref_rel929=R.loc[rp,'rel929_mean'],new_rel929=S.loc[rp,'rel929_mean'],
      rel_change_pct=100*(S.loc[rp,'rel929_mean']/R.loc[rp,'rel929_mean']-1)))
CMP=pd.DataFrame(CMP)
pickle.dump(dict(sets={k:[f for f,_ in v] for k,v in sets.items()},SS=SS,BT=BT,CMP=CMP,refmean=refmean),open('ln3.pkl','wb'))
pd.set_option('display.width',250)
print(SS.round(4).to_string())
print(CMP[CMP.set=='NEW_all_pass_24Sep'].round(2).to_string())
print(CMP[CMP.set=='NEW_60_24Sep'][['ref_pos','dpos','new_detected','rel_change_pct']].round(1).to_string())
print(BT[BT.set.isin(['REF_90_30May_all15','NEW_60_24Sep','NEW_70_24Sep'])&BT.role.str.startswith('Primary')][['set','ref_pos','pos_mean','pos_sd','height_mean','height_cv','snr_mean']].round(1).to_string())
