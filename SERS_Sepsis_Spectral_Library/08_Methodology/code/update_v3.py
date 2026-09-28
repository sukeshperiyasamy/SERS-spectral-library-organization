import sys,os,pickle,shutil,numpy as np,pandas as pd
sys.path.insert(0,os.path.expanduser('~/work')); from lib2 import *
B,P,A,G,GZ=pickle.load(open(os.path.expanduser('~/work/v2.pkl'),'rb'))
D=pickle.load(open(os.path.expanduser('~/work/reaudit60.pkl'),'rb'))
cls_rows=[]
for _,d in D.iterrows():
  i=B.index[B.new_name==d.file][0]
  if d.power==70:
    cat='A – Valid candidate'; st='Valid – supporting (70%/60 s/5 acc)'; grp='Valid'
    reason=f'Detector saturated only at the laser line ({d.sat_shift_range} cm-1, {d.n_sat_pixels} pixel). In 400–1800 cm-1: max raw {d.raw_max_fp:.0f} counts (< 65 535), no negative counts, SNR {d.snr:.1f}, r = {d.r_ref_exglass:.3f} vs NAM reference. Retained as supporting NAM spectrum (separate acquisition group, not merged into reference).'
  elif 'samespot' in d.orig:
    cat='C – Distorted'; st='Excluded – distorted (negative counts)'; grp='Excluded'
    reason=f'Laser-line saturation only ({d.sat_shift_range} cm-1), but the stored dark reference is abnormally high (median {d.dark_median_fp:.0f} vs 1 959 counts in the 70 % set), giving negative dark-subtracted counts in {100*d.neg_frac:.0f} % of 400–1800 cm-1 (min {d.ds_min_fp:.0f}); r = {d.r_ref_exglass:.2f}. Unreliable.'
  else:
    cat='C – Distorted'; st='Excluded – distorted (abnormal dark / ripple)'; grp='Excluded'
    reason=f'Laser-line saturation only ({d.sat_shift_range} cm-1); 400–1800 cm-1 not saturated (max raw {d.raw_max_fp:.0f}). Dark reference elevated (median {d.dark_median_fp:.0f} vs 1 959) and strong high-frequency ripple: noise {d.noise:.0f} counts (reference ≈ 26), r = {d.r_ref_exglass:.2f}. Fingerprint unreliable.'
  B.loc[i,['qc_status','qc_reason','qc_group']]=[st,reason,grp]
  cls_rows.append(dict(file=d.file,original=d.orig,power=d.power,category=cat,decision=st,saturated_pixels=d.n_sat_pixels,saturated_shift=d.sat_shift_range,
     max_raw_400_1800=round(d.raw_max_fp),dark_median=round(d.dark_median_fp),min_dark_subtracted=round(d.ds_min_fp),neg_fraction_pct=round(100*d.neg_frac,1),noise=round(d.noise,1),SNR=round(d.snr,1),r_vs_reference=round(d.r_ref_exglass,3),reason=reason))
  # move files
  if grp=='Valid' and B.loc[i,'raw_folder']=='Excluded':
    src=os.path.join(LIB,'01_Raw_Data_Renamed','Excluded',B.loc[i,'new_name_raw']); dst=os.path.join(LIB,'01_Raw_Data_Renamed','NAM_Bulk',B.loc[i,'new_name_raw'])
    if os.path.exists(src) and not os.path.exists(dst): os.rename(src,dst)
    ps=os.path.join(LIB,'07_QC_and_Exclusions','Processed_Excluded_Spectra',B.loc[i,'new_name'].replace('.csv','_processed.csv')); pd_=os.path.join(LIB,'02_Processed_Spectra','NAM',os.path.basename(ps))
    if os.path.exists(ps) and not os.path.exists(pd_): os.rename(ps,pd_)
    # fix QC line in processed header
    with open(pd_) as fh: t=fh.read()
    t=t.replace('# QC: Saturated (laser line only)','# QC: Valid – supporting (70%/60 s/5 acc; laser-line saturation only, fingerprint unsaturated)'); open(pd_,'w').write(t)
    B.loc[i,'raw_folder']='NAM_Bulk'
B['supporting_group']=B.qc_status.str.startswith('Valid – supporting')
pickle.dump((B,P,A,G,GZ),open(os.path.expanduser('~/work/v2.pkl'),'wb'))
C=pd.DataFrame(cls_rows); C.to_csv(os.path.join(LIB,'07_QC_and_Exclusions','NAM_60s_ReAudit_Classification.csv'),index=False)
pickle.dump(C,open(os.path.expanduser('~/work/reaudit_cls.pkl'),'wb'))
print(C[['file','category','decision']].to_string()); print(B.raw_folder.value_counts())
