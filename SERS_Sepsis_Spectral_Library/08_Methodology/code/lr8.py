import os,pickle,numpy as np,pandas as pd
from lib2 import LIB
D=pickle.load(open('lr2.pkl','rb'));E=pickle.load(open('lr3.pkl','rb'));BT=pickle.load(open('lr6.pkl','rb'));df=pickle.load(open('lr7_df.pkl','rb'))
P=D['P'];x=D['x'];ks=E['ks'];fin=E['fin'];C=E['C'];N=E['N']
RD=os.path.join(LIB,'03_Reference_Spectra','LPS')
hdr=['# LPS bulk powder on glass slide - REFERENCE (established 28 Sep 2026; n = 10 independent spots)',
 '# Sample: LPS from E. coli O111:B4, Sigma-Aldrich L2630, lot 0000442391 (phenol-extracted, smooth LPS)',
 '# Condition: 785 nm, 60 % laser power (instrument setting), 40 s, 5 accumulations; dark acquired before each spectrum; pipeline v3',
 '# Members: '+'; '.join(ks),
 '# Representative spectrum = MEAN of normalised spectra (median agrees: r = %.4f, |mean-median| < 1 SD at all points). Absolute counts vary ~3-5x between spots (focus/packing)'%np.corrcoef(E['mn'],E['md'])[0,1],
 '# Limitation: dark frames contained some sample light (dark median 1845-2090 vs true dark ~1480-1525); estimated intensity under-estimate 3-34 % (factor column in members file); band positions and shape unaffected']
t=pd.DataFrame({'Raman_Shift_cm-1':x,'BaselineCorrected_mean_counts':C.mean(0),'BaselineCorrected_median_counts':np.median(C,0),'BaselineCorrected_SD_counts':C.std(0,ddof=1),'Normalised_mean':E['mn'],'Normalised_median':E['md'],'Normalised_SD':E['sd']}).round(5)
with open(os.path.join(RD,'LPS_Bulk_Reference_Mean_SD.csv'),'w') as fh: fh.write('\n'.join(hdr)+'\n'); t.to_csv(fh,index=False)
mem=fin[fin.library_file.isin(ks)][['library_file','acq','dark_med','dark_excess','intensity_factor','ripple','noise','h425','snr425','glass_ratio','r_to_others','rNAM','rLPS28']].round(3)
mem=mem.merge(df[['library_file','original']],on='library_file');mem.to_csv(os.path.join(RD,'LPS_Reference_Members.csv'),index=False)
cols=['class','band','detected','pos_mean','pos_sd','height_median','height_mean','height_cv','snr_median','snr_min','rel425_mean','rel425_cv','fwhm','glass_share_pct','snr_after_glass_removal','blank_features','literature','general','note']
BT[cols].round(2).to_csv(os.path.join(RD,'LPS_Reference_Marker_Peaks.csv'),index=False)
open(os.path.join(RD,'README_LPS_reference_status.txt'),'w').write('''LPS bulk reference - STATUS: ESTABLISHED (28 Sep 2026)
Sample: LPS from E. coli O111:B4, Sigma-Aldrich L2630, lot 0000442391 (phenol extraction; smooth LPS). Label photo in this folder.
Condition: 785 nm, 60 % / 40 s / 5 acc, bulk powder on glass slide. n = 10 independent spots (S10-S12, S14-S20); S13 excluded (glass-dominated).
Why this condition: 70-90 % gave fixed-pattern ripple (instrument); 60 % was ripple-free; 40 s raised SNR of the 425 cm-1 band to 19-63.
Reproducibility: pairwise r (glass zone excluded) mean 0.916; mean vs median agree within 1 SD everywhere.
Identity: matches 28 Sep screening (r 0.98), April 2026 LPS (r 0.80); not NAM (r 0.17) or LTA (r 0.52).
Primary markers: 425 cm-1 (unassigned; strongest, 10/10, SNR median 38) and 1080 cm-1 (broad; 10/10, SNR 15; ~14 % glass contribution).
Supporting: 766, 861, 997 cm-1. Uncertain: 478, 541, 631, 656, 1124, 1248, 1458 (exploratory after glass removal). Glass/background: 1257, 1334 (glass zone), 1657.
Limitations: weak Raman scatterer; absolute counts vary 3-5x between spots; dark frames contained some sample light (intensity under-estimated 3-34 %);
glass band dominates 1308-1455 cm-1 (literature LPS C-H bands there cannot be confirmed); no pure-compound normal-Raman literature for this serotype.
Files: LPS_Bulk_Reference_Mean_SD.csv, LPS_Reference_Members.csv, LPS_Reference_Marker_Peaks.csv. Earlier screening files (*_NOT_REFERENCE.csv) kept for history.
''')
with open(os.path.join(RD,'README_LPS_reference_pending.txt'),'a') as fh: fh.write('\nSUPERSEDED 28 Sep 2026: LPS reference established - see README_LPS_reference_status.txt\n')
# QC log + exclusions
df.drop(columns=[c for c in ['t'] if c in df]).round(3).to_csv(os.path.join(LIB,'07_QC_and_Exclusions','LPS_Reference_Session_20260928_QC_Log.csv'),index=False)
ex=df[df.QC.isin(['EXCLUDE','FAIL','SUPPORTING'])]
pd.DataFrame({'a':ex.library_file,'b':'28-9-26-lps-bulk/'+ex.original,'c':'LPS','d':ex.power,'e':ex.int_s,'f':ex.acc,'g':ex.QC,'h':ex.QC_reason,'i':'LPS_Bulk'}).to_csv(os.path.join(LIB,'07_QC_and_Exclusions','Excluded_and_Flagged_Spectra.csv'),mode='a',header=False,index=False)
print(open(os.path.join(RD,'README_LPS_reference_status.txt')).read()[:200]); print(os.listdir(RD))
