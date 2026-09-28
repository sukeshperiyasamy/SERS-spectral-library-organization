# NAM session 24 Sep 2026 (originally saved under "lps" folder names; operator confirmed NAM on 27 Sep 2026)
import os,pickle,hashlib,numpy as np,pandas as pd
from lib2 import LIB
D=pickle.load(open('lf1.pkl','rb')); df=D['df'].copy(); P0=D['P']
df['library_file_old']=df.library_file
df['library_file']=df.library_file.str.replace('LPS_Bulk_','NAM_Bulk_',regex=False)
df['category']=df.category.replace({'LPS_Bulk':'NAM_Bulk'})
P={nf:P0[of] for of,nf in zip(df.library_file_old,df.library_file)}
md5=lambda p: hashlib.md5(open(p,'rb').read()).hexdigest()
bad=0
for i,rw in df.iterrows():
  cp=os.path.join(LIB,'01_Raw_Data_Renamed',rw.category,rw.library_file)
  if md5(cp)!=rw.md5: bad+=1
  p=P[rw.library_file]['p']; out=os.path.join(LIB,'02_Processed_Spectra','NAM' if rw.category=='NAM_Bulk' else 'Glass_Blank',rw.library_file.replace('.csv','_processed.csv'))
  samp='NAM bulk powder on glass slide (original folder named "lps" in error; identity confirmed as NAM by operator on 27 Sep 2026)' if rw.category=='NAM_Bulk' else 'Empty glass slide (blank), NAM session 24 Sep 2026'
  hdr=[f'# Library name: {rw.library_file}',f'# Original raw file (unchanged): bulk-lps-24-09-26/{rw.original_folder}/{rw.original_file}',f'# Sample: {samp}',
   f'# Acquired: {rw.acq_time} | Instrument: B&W Tek i-Raman Plus BWS465-785H | Laser {rw.laser_nm} nm | Objective: not recorded in file (probe_name empty)',
   f'# Laser power level: {rw.power} % (instrument setting; not converted to mW) | Integration: {rw.integration_s:g} s | Accumulations: {rw.accumulations}',
   f'# QC: {rw.QC} {rw.QC_reason} | noise {rw.noise:.1f} | SNR(929) {rw.snr929:.1f} | ripple residual {rw.ripple_ds:.1f} | dark median {rw.dark_median:.0f} | saturated px 400-1800: {rw.n_sat_400_1800}'+(f' | {rw.note}' if rw.note else ''),
   '# Pipeline v3: hot-pixel interpolation (CCD px 640, 700); crop 400-1800 cm-1; MAD spike removal (z>6, width<=2 px); Savitzky-Golay 11/3; ALS baseline lambda=1e5 p=0.01 10 it; min-max normalisation',
   '# Columns: Raw = raw counts (incl. dark); DarkSubtracted = instrument dark-subtracted; HotPixelFixed; Despiked; Smoothed; Baseline (ALS); BaselineCorrected (counts); Normalised (0-1, shape only)']
  t=pd.DataFrame({'Raman_Shift_cm-1':p['x'],'Raw_counts':p['raw'],'DarkSubtracted_counts':p['ds'],'HotPixelFixed_counts':p['ds_hotfix'],'Despiked_counts':p['despiked'],
    'Smoothed_counts':p['smooth'],'Baseline_counts':p['base'],'BaselineCorrected_counts':p['corr'],'Normalised_0to1':p['norm']}).round(5)
  if os.path.exists(out): raise SystemExit('exists '+out)
  with open(out,'w') as fh: fh.write('\n'.join(hdr)+'\n'); t.to_csv(fh,index=False)
D2=dict(D); D2['df']=df; D2['P']=P
pickle.dump(D2,open('ln1.pkl','wb'))
print('md5 mismatches',bad,'written',len(df))
