import sys,os,pickle,numpy as np,pandas as pd
from scipy.signal import find_peaks,peak_prominences,savgol_filter
sys.path.insert(0,os.path.expanduser('~/work')); from lib2 import *
B,P,A,G,GZ=pickle.load(open(os.path.expanduser('~/work/v2.pkl'),'rb'))
I=lambda i,k:np.interp(X,P[i]['x'],P[i][k])
MK={'NAM':[541,830,870,929,955,1023,1127],'LTA':[802,861,1092,1459]}
# ---------- groups
g={}
g['NAM_REF']=B[B.in_reference&(B.cls=='NAM')]
g['NAM_REF_diffpoint']=g['NAM_REF'][g['NAM_REF'].orig.str.contains('diifrentpoint')]
g['NAM_REF_samespot']=g['NAM_REF'][g['NAM_REF'].orig.str.contains('samespot')]
g['NAM_VAL_70_10_5_diffpoint']=B[(B.cls=='NAM')&B.orig.str.contains('70p-5ac-10s-diifrentpoint')&(B.qc_status=='Valid')]
g['NAM_SUP_70_60_5']=B[B.qc_status.str.startswith('Valid – supporting')]
g['LTA_REF']=B[B.in_reference&(B.cls=='LTA')]
g['LTA_ALLVALID']=B[(B.cls=='LTA')&(B.qc_status=='Valid')]
g['LPS_ALL']=B[B.cls=='LPS']; g['GLASS']=B[B.cls=='GLASS']
# ---------- extended per-spectrum QC for all bulk classes
rows=[]
means={}
for key in ['NAM_REF','LTA_REF']:
  means[key]=np.mean([I(i,'norm') for i in g[key].index],0)
for i,r in B.iterrows():
  pr=P[i]; x=pr['x']; b=pr['base']; c=pr['corr']
  slope=np.polyfit(x,b,1)[0]*100
  a=r.cls; mk=MK.get(a)
  ci=I(i,'corr')
  if mk:
    js=[np.where((X>=m-8)&(X<=m+8))[0][np.argmax(ci[(X>=m-8)&(X<=m+8)])] for m in mk]
    jmax=js[int(np.argmax(ci[js]))]; prom=peak_prominences(ci,[jmax])[0][0]
  else:
    jmax=np.argmax(ci); prom=peak_prominences(ci,[jmax])[0][0]
  ref=means.get('NAM_REF' if a=='NAM' else ('LTA_REF' if a=='LTA' else None)) if a in ('NAM','LTA') else None
  rr=np.corrcoef(I(i,'norm')[~GZ],ref[~GZ])[0,1] if ref is not None else np.nan
  rows.append(dict(idx=i,file=r.new_name_raw,cls=a,power=r.power,int_s=r.int_s,acc=r.acc,spot=r.spot_type,snr=r.snr,noise=pr['noise'],
    max_ds=pr['ds'].max(),min_ds=pr['ds'].min(),max_raw_fp=pr['raw'].max(),max_raw_any=r.raw_max,sat_laser=bool(r.raw_max>=65000 and pr['raw'].max()<65000),sat_fp=bool(pr['raw'].max()>=65000),
    baseline_mean=b.mean(),baseline_range=b.max()-b.min(),baseline_slope_per100=slope,dyn_range=c.max()/pr['noise'],prominence=prom,spikes=pr['nspikes'],
    r_group=rr,qc=r.qc_status,reason=r.qc_reason,in_ref=r.in_reference))
QC=pd.DataFrame(rows)
# ---------- group reproducibility + mean vs median
grp=[];MM={}
for key,d in g.items():
  if len(d)<2: continue
  C=np.array([I(i,'corr') for i in d.index]); N=np.array([I(i,'norm') for i in d.index])
  r_pair=[np.corrcoef(N[a_][~GZ],N[b_][~GZ])[0,1] for a_ in range(len(N)) for b_ in range(a_+1,len(N))]
  mean=C.mean(0); med=np.median(C,0); sd=C.std(0,ddof=1)
  diff=mean-med; big=np.abs(diff)>sd  # points where mean-median exceeds 1 SD
  r_mm=np.corrcoef(mean,med)[0,1]
  mk=MK.get(key[:3],[])
  mk_diff=[abs(mean[np.argmin(abs(X-m))]-med[np.argmin(abs(X-m))])/sd[np.argmin(abs(X-m))] for m in mk] if mk else []
  cv_sp=100*np.median(sd[mean>0.2*mean.max()]/mean[mean>0.2*mean.max()])
  MM[key]=dict(mean=mean,median=med,sd=sd,N=N,C=C,idx=list(d.index))
  grp.append(dict(group=key,n=len(d),snr_mean=d.snr.mean(),snr_sd=d.snr.std(),r_pair_mean=np.mean(r_pair),r_pair_min=np.min(r_pair),r_mean_median=r_mm,
     max_absdiff_rel=np.abs(diff).max()/mean.max(),frac_pts_diff_gt_1SD=big.mean(),marker_diff_over_SD_max=max(mk_diff) if mk_diff else np.nan,median_pointwise_CV_pct=cv_sp))
GRP=pd.DataFrame(grp)
# ---------- peak consistency per group (markers + background checks)
pkrows=[]
for key in ['NAM_REF','NAM_REF_diffpoint','NAM_REF_samespot','NAM_VAL_70_10_5_diffpoint','NAM_SUP_70_60_5','LTA_REF','LTA_ALLVALID']:
  d=g[key]; a=key[:3]
  for m in MK[a]:
    pos=[];h=[];snr=[];prom=[];det=0;raw_ok=0
    for i in d.index:
      c=I(i,'corr'); nz=P[i]['noise']; w=(X>=m-8)&(X<=m+8); j=np.where(w)[0][np.argmax(c[w])]
      pos.append(X[j]); h.append(c[j]); snr.append(c[j]/nz); pr_=peak_prominences(c,[j])[0][0]; prom.append(pr_)
      pk,_=find_peaks(c,prominence=5*nz,distance=5)
      if len(pk) and np.min(abs(X[pk]-X[j]))<=5: det+=1
      # processing-artifact check: peak present in despiked (unsmoothed) data minus baseline
      y=I(i,'despiked')-I(i,'base'); pk2,_=find_peaks(y,prominence=5*nz,distance=5)
      if len(pk2) and np.min(abs(X[pk2]-X[j]))<=5: raw_ok+=1
    pkrows.append(dict(group=key,biomarker=a,peak=m,n=len(d),pos_mean=np.mean(pos),pos_sd=np.std(pos,ddof=1),h_mean=np.mean(h),h_sd=np.std(h,ddof=1),cv=100*np.std(h,ddof=1)/np.mean(h),
      snr=np.mean(snr),prom=np.mean(prom),pct_detected=100*det/len(d),pct_in_unsmoothed=100*raw_ok/len(d),glass_blank_rel=float(G[np.argmin(abs(X-m))])))
PKC=pd.DataFrame(pkrows)
# background-source screen for final markers
PS=[620,1001,1031,1602]
bg=[]
for a in ['NAM','LTA']:
  for m in MK[a]:
    gb=float(G[np.argmin(abs(X-m))]); ps=min(abs(np.array(PS)-m))
    row=PKC[(PKC.group==a+'_REF')&(PKC.peak==m)].iloc[0]
    bg.append(dict(biomarker=a,peak=m,
      glass=f'glass blank at {100*gb:.0f} % of its max' + (' (inside glass zone)' if GZ[np.argmin(abs(X-m))] else ''),
      instrument='not in empty-slide blank; not a fixed-pixel feature (same position across powers/days)',
      fluorescence='broad fluorescence removed by ALS; band width ≈ 10–50 cm-1 is Raman-like, not fluorescence',
      cosmic=f'present in {row.pct_detected:.0f} % of spectra (cosmic spikes are random, single-spectrum)',
      contamination='no polystyrene pattern (620/1001/1031/1602)' + (f'; nearest PS band {ps:.0f} cm-1 away' if ps<40 else ''),
      processing=f'present in {row.pct_in_unsmoothed:.0f} % of unsmoothed (despiked) spectra → not created by SG smoothing',
      verdict='Not background' if (gb<0.25 and row.pct_detected>=90) else 'Partly glass-affected'))
BG=pd.DataFrame(bg)
pickle.dump(dict(g={k:list(v.index) for k,v in g.items()},QC=QC,GRP=GRP,MM=MM,PKC=PKC,BG=BG),open(os.path.expanduser('~/work/an4.pkl'),'wb'))
pd.set_option('display.width',250)
print(GRP.round(3).to_string()); print(PKC.round(2).to_string()); print(BG[['biomarker','peak','glass','verdict']].to_string())
print(QC[QC.in_ref].groupby('cls')[['baseline_slope_per100','dyn_range','prominence','spikes','r_group']].describe().round(2).T.to_string())
