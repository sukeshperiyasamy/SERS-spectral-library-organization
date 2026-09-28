import sys,os,pickle,numpy as np,pandas as pd
sys.path.insert(0,os.path.expanduser('~/work')); from lib2 import *
B,P,A,G,GZ=pickle.load(open(os.path.expanduser('~/work/v2.pkl'),'rb'))
old=B[['snr','qc_status','marker_max']].copy()
MARK={'NAM':[541,870,929,955,1023,1127],'LTA':[802,861,1092,1459],'SUSPECT':[620,1001,1031,1602]}
P3={}
for i,r in B.iterrows():
  meta,rs,dk,raw,ds=read_any(os.path.join(ROOT,r.orig)); pr=process_v3h(rs,ds,raw); P3[i]=pr
  ci=np.interp(X,pr['x'],pr['corr'])
  B.loc[i,['noise','nspikes','baseline_level','snr_max']]=[pr['noise'],pr['nspikes'],float(np.median(pr['base'])),ci.max()/pr['noise']]
  B.at[i,'spike_pos']=';'.join(f'{s:.0f}' for s in pr['spike_pos'])
  mk=MARK.get(r.cls)
  if mk:
    h=[ci[(X>=m-8)&(X<=m+8)].max() for m in mk]; B.loc[i,'marker_max']=max(h); B.loc[i,'snr']=max(h)/pr['noise']
  else: B.loc[i,'snr']=ci.max()/pr['noise']; B.loc[i,'marker_max']=np.nan
  B.loc[i,['raw_max_fp','ds_max_fp','ds_min_fp']]=[pr['raw'].max(),pr['ds'].max(),pr['ds'].min()]
N=lambda i:np.interp(X,P3[i]['x'],P3[i]['norm'])
G=np.mean([N(i) for i in B[B.cls=='GLASS'].index],0)
for a in ['NAM','LTA']:
  ok=(B.cls==a)&(B.qc_status.str.startswith('Valid'))&(B.snr>=10)
  M=np.mean([N(i) for i in B[ok].index],0)
  for i in B[B.cls==a].index: B.loc[i,'r_class_exglass']=np.corrcoef(N(i)[~GZ],M[~GZ])[0,1]
# status re-evaluation only between Valid <-> Low SNR (other decisions unchanged)
flips=[]
for i,r in B.iterrows():
  if r.qc_status=='Valid' and r.snr<10: B.loc[i,['qc_status','qc_reason']]=['Low SNR',f'SNR {r.snr:.1f} < 10 (project convention) at low power / short integration; used only for parameter comparison.']; flips.append((r.new_name,'Valid->Low SNR'))
  elif r.qc_status=='Low SNR' and r.snr>=10 and r.cls in('NAM','LTA') and r.r_class_exglass>=0.85: B.loc[i,['qc_status','qc_reason']]=['Valid','']; flips.append((r.new_name,'Low SNR->Valid'))
print('status flips:',flips)
# write processed files at current locations
procdir={'NAM':'NAM','LTA':'LTA','LPS':'LPS','GLASS':'Glass_Blank'}
for i,r in B.iterrows():
  pr=P3[i]
  pfold=os.path.join(LIB,'07_QC_and_Exclusions','Processed_Excluded_Spectra') if r.raw_folder=='Excluded' else os.path.join(LIB,'02_Processed_Spectra',procdir[r.cls])
  fn=os.path.join(pfold,r.new_name.replace('.csv','_processed.csv'))
  hdr=[f'# Library name: {r.new_name}',f'# Original raw file (unchanged): {r.orig}',f'# Sample: {r.cls} bulk powder on glass slide' if r.cls not in('GLASS','SUSPECT') else f'# Sample: {r.cls}',
   f'# Acquired: {r.date} | Instrument: B&W Tek i-Raman Plus {r.instrument} | Laser {r.laser_nm} nm | Objective: {r.objective}',
   f'# Laser power level: {r.power:g} % (instrument setting; not converted to mW) | Integration: {r.int_s:g} s | Accumulations: {int(r.acc)}',
   f'# QC: {r.qc_status} | SNR {r.snr:.1f} | spikes removed {int(r.nspikes)} ({r.spike_pos or "none"}) | saturated anywhere {r.saturated} | saturated in 400-1800 {r.raw_max_fp>=65000}',
   '# Pipeline v3: fixed hot-pixel interpolation (CCD pixels 640, 700); crop 400-1800 cm-1; spike removal (MAD modified z of first difference > 6 AND width <= 2 px; linear interpolation); Savitzky-Golay 11/3; ALS baseline lambda=1e5 p=0.01; min-max normalisation',
   '# Columns: Raw = raw counts (incl. dark); DarkSubtracted = instrument dark-subtracted; HotPixelFixed; Despiked; Smoothed; Baseline (ALS); BaselineCorrected (counts); Normalised (0-1, shape only)']
  out=pd.DataFrame({'Raman_Shift_cm-1':pr['x'].round(3),'Raw_counts':pr['raw'].round(2),'DarkSubtracted_counts':pr['ds'].round(2),'HotPixelFixed_counts':pr['ds_hotfix'].round(2),'Despiked_counts':pr['despiked'].round(2),
     'Smoothed_counts':pr['smooth'].round(2),'Baseline_counts':pr['base'].round(2),'BaselineCorrected_counts':pr['corr'].round(2),'Normalised_0to1':pr['norm'].round(5)})
  with open(fn,'w') as fh: fh.write('\n'.join(hdr)+'\n'); out.to_csv(fh,index=False)
pickle.dump((B,P3,A,G,GZ),open(os.path.expanduser('~/work/v2.pkl'),'wb'))
d=pd.DataFrame({'old_snr':old.snr,'new_snr':B.snr,'old_h':old.marker_max,'new_h':B.marker_max})
R=B[B.in_reference]
print(R.groupby('cls')[['snr','marker_max']].agg(['mean','std']).round(2))
print('ref marker_max change %:',(100*(B.marker_max-old.marker_max)/old.marker_max)[B.in_reference].groupby(B.cls).mean().round(1).to_dict())
print(B.groupby(['cls','qc_status']).size())
