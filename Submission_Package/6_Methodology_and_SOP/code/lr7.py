import os,pickle,numpy as np,pandas as pd
from lib2 import LIB
D=pickle.load(open('lr2.pkl','rb'));E=pickle.load(open('lr3.pkl','rb'));BT=pickle.load(open('lr6.pkl','rb'))
df=D['df'];P=D['P'];x=D['x'];ks=E['ks'];fin=E['fin']
inv=pd.read_pickle('lr_inv.pkl').set_index('library_file')
qcmap=fin.set_index('library_file')
def qcfor(f,r):
  if f in qcmap.index: q=qcmap.loc[f]; return q.QC,q.QC_reason
  if r.category=='Glass_Blank': return ('BLANK-SATURATED' if r.nsat>0 else 'BLANK-OK'),''
  if r.category=='Instrument_Checks': return 'CHECK',''
  if r.ripple>50: return 'FAIL','ripple > 50 (troubleshooting spectrum)'
  return 'SUPPORTING','valid spectrum but dark contained sample light / different condition - not used in reference'
for i,r in df.iterrows():
  a,b=qcfor(r.library_file,r); df.loc[i,'QC']=a; df.loc[i,'QC_reason']=b; df.loc[i,'original']=inv.loc[r.library_file,'original']; df.loc[i,'role']=inv.loc[r.library_file,'role']
df['in_reference']=df.library_file.isin(ks)
# processed CSVs
for _,r in df.iterrows():
  folder={'LPS_Bulk':'LPS','Glass_Blank':'Glass_Blank','Instrument_Checks':'Instrument_Checks'}[r.category]
  out=os.path.join(LIB,'02_Processed_Spectra',folder,r.library_file.replace('.csv','_processed.csv')); os.makedirs(os.path.dirname(out),exist_ok=True)
  if os.path.exists(out): continue
  p=P[r.library_file]['p']
  hdr=[f'# Library name: {r.library_file}',f'# Original raw file (unchanged): 28-9-26-lps-bulk/{r.original}',f'# Role: {r.role}',
   f'# Sample: LPS from E. coli O111:B4 (Sigma-Aldrich L2630, lot 0000442391), bulk powder on glass slide' if r.category=='LPS_Bulk' else f'# Sample: {r.category}',
   f'# Acquired (instrument clock): {r.acq} | B&W Tek i-Raman Plus BWS465-785H | 785 nm | Objective: not recorded in file',
   f'# Laser power level: {r.power} % (instrument setting) | Integration: {r.int_s:g} s | Accumulations: {r.acc}',
   f'# QC: {r.QC} {r.QC_reason} | dark median {r.dark_med:.0f} | ripple {r.ripple:.1f} | noise {r.noise:.1f} | 425 band SNR {r.snr425:.1f} | saturated px 400-1800: {r.nsat}',
   '# Pipeline v3: hot-pixel interpolation (CCD px 640, 700); crop 400-1800 cm-1; MAD spike removal (z>6, width<=2 px); Savitzky-Golay 11/3; ALS baseline lambda=1e5 p=0.01 10 it; min-max normalisation']
  t=pd.DataFrame({'Raman_Shift_cm-1':p['x'],'Raw_counts':p['raw'],'DarkSubtracted_counts':p['ds'],'HotPixelFixed_counts':p['ds_hotfix'],'Despiked_counts':p['despiked'],'Smoothed_counts':p['smooth'],'Baseline_counts':p['base'],'BaselineCorrected_counts':p['corr'],'Normalised_0to1':p['norm']}).round(5)
  with open(out,'w') as fh: fh.write('\n'.join(hdr)+'\n'); t.to_csv(fh,index=False)
pickle.dump(df,open('lr7_df.pkl','wb'))
print(df.QC.value_counts()); print(df[['library_file','QC']].to_string())
