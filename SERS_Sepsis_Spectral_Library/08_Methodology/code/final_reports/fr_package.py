"""Assembles the final submission folder: data, tables and index (the nine reports are built by fr_docs.py)."""
import os,shutil,glob,numpy as np,pandas as pd
import fr_data as D
OUT=r"C:\Users\sukes\Downloads\sukesh\Final_Submission"; L=D.LIB
def cp(src,dst,ignore=None):
    if os.path.isdir(src): shutil.copytree(src,dst,dirs_exist_ok=True,ignore=ignore)
    else: os.makedirs(os.path.dirname(dst),exist_ok=True); shutil.copy2(src,dst)
# ---- spectral library
SL=os.path.join(OUT,'04_Spectral_Library'); os.makedirs(SL,exist_ok=True)
cp(L+r"\03_Reference_Spectra",SL+r"\Reference_Spectra")
for sub in ('NAM','LPS','LTA','Glass_Blank'):
    cp(L+rf"\02_Processed_Spectra\{sub}",SL+rf"\Processed_Spectra\{sub}"); cp(L+rf"\01_Raw_Data_Renamed\{sub}_Bulk" if sub!='Glass_Blank' else L+r"\01_Raw_Data_Renamed\Glass_Blank",SL+rf"\Raw_Data_Renamed\{sub if sub=='Glass_Blank' else sub+'_Bulk'}")
cp(L+r"\05_Tables\Spectral_Library_Metadata_and_Peaks.xlsx",SL+r"\Spectral_Library_Metadata_and_Peaks.xlsx")
cp(L+r"\06_Literature",SL+r"\Literature")
cp(L+r"\07_QC_and_Exclusions",SL+r"\QC_Records",ignore=shutil.ignore_patterns('Processed_Excluded_Spectra','*.png'))
# ---- simulation data
SD=os.path.join(OUT,'05_Simulation_Data')
cp(D.MTP+r"\02_DFT_Calculation",SD+r"\NAM",ignore=shutil.ignore_patterns('alpha_*','*.png'))
cp(D.MTP+r"\03_Processed_Results\DFT_simulated_spectrum.csv",SD+r"\NAM\DFT_simulated_spectrum.csv")
cp(D.SIMD+r"\lta output simulation",SD+r"\LTA")
cp(D.SIMD+r"\lps output simulation",SD+r"\LPS")
# ---- analysis tables
AT=os.path.join(OUT,'06_Analysis_Tables'); os.makedirs(AT,exist_ok=True)
for m in ('NAM','LTA','LPS'):
    d=D.sim(m); k=d['k']; rows=[]
    for i in np.where(k)[0]: rows.append(dict(calculated_peak_cm1=round(float(d['f'][i]),1),relative_intensity=round(float(d['I'][i]),3),vibration_type=d['label'][i]))
    pd.DataFrame(rows).to_csv(AT+rf"\{m}_calculated_peaks_with_assignment.csv",index=False)
    pd.DataFrame([dict(measured_peak_cm1=round(r['exp'],1),role=r['role'],calculated_peak_cm1=None if r['calc'] is None else round(r['calc'],1),difference_cm1=None if r['delta'] is None else round(r['delta'],1),calculated_relative_intensity=None if r['I'] is None else round(r['I'],3),vibration_type=r['label'],result={'agrees':'agrees (within 10 cm-1)','shifted':'shifted, same vibration type','none':'not reproduced'}[r['status']],expected_assignment=r['desc']) for r in D.match(m)]).sort_values('measured_peak_cm1').to_csv(AT+rf"\{m}_peak_comparison.csv",index=False)
    mean,sd,_=D.exp_ref(m); pd.DataFrame(dict(raman_shift_cm1=D.X,measured_mean_normalised=mean.round(5),measured_sd_normalised=sd.round(5),calculated_normalised=D.calc_curve(m).round(5))).to_csv(AT+rf"\{m}_measured_and_calculated_spectra.csv",index=False)
print('done')
