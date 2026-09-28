import sys,os,pickle,shutil,numpy as np,pandas as pd
sys.path.insert(0,os.path.expanduser('~/work')); from lib2 import *
B,P=pickle.load(open(os.path.expanduser('~/work/qc.pkl'),'rb'))
A=pickle.load(open(os.path.expanduser('~/work/audit.pkl'),'rb'))
N=lambda i:np.interp(X,P[i]['x'],P[i]['norm'])
G=np.mean([N(i) for i in B[B.cls=='GLASS'].index],0); GLASSZONE=G>0.25
print('glass zone',X[GLASSZONE].min(),X[GLASSZONE].max())
# r excluding glass zone
for a in ['NAM','LTA']:
  ok=(B.cls==a)&(~B.saturated)&(B.snr>=10)
  M=np.mean([N(i) for i in B[ok].index],0)
  for i in B[B.cls==a].index: B.loc[i,'r_class_exglass']=np.corrcoef(N(i)[~GLASSZONE],M[~GLASSZONE])[0,1]
def qc(r):
  if r.cls=='SUSPECT': return ('Excluded','Contaminated / misidentified','Polystyrene-like pattern (620, 1001, 1031, 1155, 1602 cm-1); labelled LTA but does not match LTA reference. Retained for review.')
  if r.saturated and r.power>=90: return ('Excluded','Saturated + invalid dark subtraction','Detector saturated (65535) at the laser line (~ -2 cm-1). In 400-1800 cm-1 the raw signal is below saturation, but the dark-subtracted spectrum is distorted (negative counts, strong ripple, r = %.2f vs NAM mean). Unusable.'%r.r_class_exglass)
  if r.saturated: return ('Excluded','Saturated (laser line only)','Detector saturated (65535) only at the laser line (~ -2 cm-1). 400-1800 cm-1 region is NOT saturated (max raw %.0f counts) and shows a normal NAM pattern (r = %.2f). Excluded per project instruction; could be reinstated after PI review.'%(r.raw_max_fp,r.r_class_exglass))
  if r.cls=='GLASS': return ('Glass blank','Valid','Empty glass slide background (5% / 5 s / 1 acc) - not matched to sample settings.')
  if r.cls=='LPS': return ('Flagged','Signal not established','Valid acquisition, but no reproducible LPS band resolved; dominant ~1360 cm-1 feature matches glass-slide background. Not used as a reference.')
  if r.cls=='LTA' and r.r_class_exglass<0.5: return ('Flagged','Abnormal - review','Distorted spectrum (r = %.2f vs LTA class mean, glass region excluded) with low SNR; not explained by power/time. Not used as reference.'%r.r_class_exglass)
  if r.snr<10: return ('Valid','Low SNR','SNR %.1f < 10 at low power / short integration; genuine %s spectrum used only for parameter comparison.'%(r.snr,r.cls))
  if r.r_class_exglass<0.85: return ('Flagged','Review - higher noise','Correct %s band pattern but r = %.2f vs class mean; extra noise structure.'%(r.cls,r.r_class_exglass))
  return ('Valid','Valid','')
B['raw_max_fp']=[P[i]['raw'].max() for i in B.index]; B['ds_max_fp']=[P[i]['ds'].max() for i in B.index]; B['ds_min_fp']=[P[i]['ds'].min() for i in B.index]; B['sat_fingerprint']=B.raw_max_fp>=65000
B[['qc_group','qc_status','qc_reason']]=B.apply(lambda r:pd.Series(qc(r)),axis=1)
B['dt']=pd.to_datetime(B.date); B['ymd']=B.dt.dt.strftime('%Y%m%d')
B=B.sort_values(['cls','ymd','power','int_s','acc','dt','orig'])
B['rep']=B.groupby(['cls','ymd','power','int_s','acc']).cumcount()+1
pref={'NAM':'NAM_Bulk','LTA':'LTA_Bulk','LPS':'LPS_Bulk','GLASS':'Glass_Blank','SUSPECT':'Unconfirmed_LabelledLTA_Bulk'}
B['new_name']=B.apply(lambda r:f"{pref[r.cls]}_{r.ymd}_P{int(r.power):03d}pct_T{int(r.int_s):02d}s_A{int(r.acc):02d}_S{int(r.rep):02d}.csv",axis=1)
assert B.new_name.is_unique
rawdir={'NAM':'NAM_Bulk','LTA':'LTA_Bulk','LPS':'LPS_Bulk','GLASS':'Glass_Blank'}
procdir={'NAM':'NAM','LTA':'LTA','LPS':'LPS','GLASS':'Glass_Blank'}
B['raw_folder']=B.apply(lambda r:'Excluded' if r.qc_group=='Excluded' else rawdir[r.cls],axis=1)
# reference membership
B['in_reference']=False
B.loc[(B.cls=='NAM')&(B.qc_status=='Valid')&(B.power==90)&(B.int_s==30)&(B.acc==5),'in_reference']=True
B.loc[(B.cls=='LTA')&(B.qc_status=='Valid')&(B.int_s==45)&(B.power>=80)&(B.acc==2),'in_reference']=True
print(B.groupby(['cls','qc_status']).size()); print(B.groupby('cls').in_reference.sum())
# ---------- folders
for s in ['01_Raw_Data_Renamed/'+d for d in ['NAM_Bulk','LTA_Bulk','LPS_Bulk','Glass_Blank','Excluded']]+['02_Processed_Spectra/'+d for d in ['NAM','LTA','LPS','Glass_Blank']]+['03_Reference_Spectra/'+d for d in ['NAM','LTA','LPS']]+['04_Figures','05_Tables','06_Literature','07_QC_and_Exclusions']:
  os.makedirs(os.path.join(LIB,s),exist_ok=True)
for i,r in B.iterrows():
  src=os.path.join(ROOT,r.orig); dst=os.path.join(LIB,'01_Raw_Data_Renamed',r.raw_folder,r.new_name)
  if r.fmt=='txtr':  # convert TXTR (semicolon) container to identical-content copy with .csv name? keep original bytes, note format
    dst=dst.replace('.csv','.txtr'); B.loc[i,'new_name_raw']=os.path.basename(dst)
  else: B.loc[i,'new_name_raw']=r.new_name
  shutil.copy2(src,dst)
  # processed (Excluded contaminated/saturated -> processed into Excluded? keep processed only for analyte folders + suspect under Excluded QC)
  pr=P[i]
  pfold=os.path.join(LIB,'02_Processed_Spectra',procdir.get(r.cls,'')) if r.cls in procdir else os.path.join(LIB,'07_QC_and_Exclusions','Processed_Excluded_Spectra')
  if r.qc_group=='Excluded': pfold=os.path.join(LIB,'07_QC_and_Exclusions','Processed_Excluded_Spectra')
  os.makedirs(pfold,exist_ok=True)
  hdr=[f'# Library name: {r.new_name}',f'# Original raw file (unchanged): {r.orig}',f'# Sample: {r.cls} bulk powder on glass slide' if r.cls not in('GLASS','SUSPECT') else f'# Sample: {r.cls}',
   f'# Acquired: {r.date} | Instrument: B&W Tek i-Raman Plus {r.instrument} | Laser {r.laser_nm} nm | Objective: {r.objective}',
   f'# Laser power level: {r.power:g} % (instrument setting; not converted to mW) | Integration: {r.int_s:g} s | Accumulations: {int(r.acc)}',
   f'# QC: {r.qc_status} | SNR {r.snr:.1f} | spikes removed {int(r.nspikes)} | saturated {r.saturated}',
   '# Pipeline: crop 400-1800 cm-1; MAD spike removal (z>6, 7-pt median); Savitzky-Golay 11/3; ALS baseline lambda=1e5 p=0.01; min-max normalisation',
   '# Columns: Raw = instrument raw counts (incl. dark); DarkSubtracted = instrument dark-subtracted counts; BaselineCorrected = smoothed - ALS baseline (counts); Normalised = min-max of BaselineCorrected (0-1)']
  out=pd.DataFrame({'Raman_Shift_cm-1':pr['x'].round(3),'Raw_counts':pr['raw'].round(2),'DarkSubtracted_counts':pr['ds'].round(2),'Despiked_counts':pr['despiked'].round(2),
     'Smoothed_counts':pr['smooth'].round(2),'Baseline_counts':pr['base'].round(2),'BaselineCorrected_counts':pr['corr'].round(2),'Normalised_0to1':pr['norm'].round(5)})
  fn=os.path.join(pfold,r.new_name.replace('.csv','_processed.csv'))
  with open(fn,'w') as fh: fh.write('\n'.join(hdr)+'\n'); out.to_csv(fh,index=False)
pickle.dump((B,P,A,G,GLASSZONE),open(os.path.expanduser('~/work/v2.pkl'),'wb'))
print('files', sum(len(f) for _,_,f in os.walk(LIB)))
