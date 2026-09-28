import sys,os,pickle,json,numpy as np,pandas as pd
sys.path.insert(0,os.path.expanduser('~/work')); from lib2 import *; from lit_v2 import *
B,P,A,G,GZ=pickle.load(open(os.path.expanduser('~/work/v2.pkl'),'rb'))
PK,ALL,REP,BULK,COND,res=pickle.load(open(os.path.expanduser('~/work/an2.pkl'),'rb'))
D=pickle.load(open(os.path.expanduser('~/work/an4.pkl'),'rb')); CT=pickle.load(open(os.path.expanduser('~/work/crit.pkl'),'rb')); SE=pickle.load(open(os.path.expanduser('~/work/sens.pkl'),'rb'))
GRP=D['GRP'].set_index('group'); PKC=D['PKC']; QC=D['QC']
bn=BULK.set_index('analyte')
def fw(v): return f'{v:.1f}' if abs(v-round(v))>0.45 else f'{v:.0f}'
G_=lambda k,c: GRP.loc[k,c]
GO=pd.DataFrame([
 ['NAM',f"15 at reference condition (5 independent points + 10 repeats of one spot); 224 valid NAM spectra on 4 days",
  f"High: SNR {bn.loc['NAM','snr_mean']:.1f} ± {bn.loc['NAM','snr_sd']:.1f}; no saturation in 400–1800; stable baseline (~1360 counts)",
  f"High: pairwise r {G_('NAM_REF','r_pair_mean'):.3f} (min {G_('NAM_REF','r_pair_min'):.3f}); mean≈median (r {G_('NAM_REF','r_mean_median'):.4f}); 10 independent spots at 70 %/10 s: r {G_('NAM_VAL_70_10_5_diffpoint','r_pair_mean'):.3f}",
  "7/7 primary markers in 15/15 reference spectra, ≥ 98 % of valid spectra on every day and 10/10 independent spots; CV 4–6 %",
  "Markers outside glass zone; 93–95 % of height retained after glass-template correction; hot pixels corrected",
  "GO for spectral identity and marker peaks; TOP-UP RE-ACQUIRE for the final intensity reference",
  "Only 5 of the 15 reference spectra are independent spots and all come from one session, so spot-to-spot and day-to-day intensity variation at 90 %/30 s/5 acc is not yet established."],
 ['LTA',"4 at reference condition (spot independence not recorded); 9 valid in total; 1 day",
  f"Adequate: SNR {bn.loc['LTA','snr_mean']:.1f} ± {bn.loc['LTA','snr_sd']:.1f}; strong fluorescence background (~8 000 counts)",
  f"Moderate: pairwise r {G_('LTA_REF','r_pair_mean'):.3f} (min {G_('LTA_REF','r_pair_min'):.3f}); mean≈median (r {G_('LTA_REF','r_mean_median'):.4f}) but n = 4",
  "3 primary markers in 4/4 reference and ≥ 8/9 valid spectra; CV 9–13 %",
  "1367 glass-associated; 1459 on glass shoulder (82 % retained); absolute intensities depend on ALS settings (−40 % to +25 %)",
  "RE-ACQUIRE",
  "n = 4 < 10, single day, spot independence unknown; intensities strongly baseline-dependent."],
 ['LPS',"14 (10–20 % power only); 0 at a suitable condition",
  "Insufficient: strongest feature is the glass band; no LPS-specific band above noise after glass comparison",
  f"Poor: pairwise r {G_('LPS_ALL','r_pair_mean'):.2f} (range −0.47 to 1.0)",
  "No reproducible candidate band",
  "Dominated by glass band (1308–1455); fixed hot pixels at 1095.7 and 1189.5 cm-1",
  "RE-ACQUIRE",
  "No LPS fingerprint established; power too low; no matched blanks."]],
 columns=['Biomarker','Existing n','Quality','Reproducibility','Marker consistency','Background','Decision','Reason'])
ACQ=pd.DataFrame([
 ['NAM','PARTLY – YES for identity/markers; NO for final intensity reference','Excellent quality and marker reproducibility, but only 5 independent spots at the reference condition, one session','YES – top-up','785 nm, 90 %, 30 s, 5 acc (unchanged; no saturation, SNR ≈ 51)','10–15 independent spots (≥ 2 slides, ideally 2 days) + 3 matched glass blanks'],
 ['LTA','NO','n = 4, single day, spot independence unknown; baseline-sensitive intensities','YES','785 nm, 80 %, 45 s, 2 acc (lowest power in the 80–95 % plateau; SNR ≈ 27–28; max raw ≈ 16 000 counts)','10–15 independent spots + 3 matched glass blanks'],
 ['LPS','NO','Only 10–20 % power; spectrum dominated by glass band; no reproducible LPS band','YES','Screening: 785 nm, 70 / 80 / 90 %, 30 s, 5 acc; ≥ 5 spots per power + ≥ 3 matched blanks per power; then 10–15 spots at the selected power','10–15 at the selected condition']],
 columns=['Biomarker','Existing data sufficient?','Why','Re-acquisition needed?','Recommended condition','Target n'])
# selection
sel=[]
for a,key in [('NAM','NAM_REF'),('LTA','LTA_REF')]:
  for i in D['g'][key]:
    r=B.loc[i]; q=QC[QC.idx==i].iloc[0]
    sel.append(dict(biomarker=a,file=r.new_name_raw,spot='same spot (repeat)' if 'samespot' in r.orig else ('different point' if 'diifrent' in r.orig else 'not recorded'),SNR=round(r.snr,1),
      max_raw_400_1800=round(r.raw_max_fp),saturated_400_1800='No',spikes=int(r.nspikes),r_to_group=round(q.r_group,3),baseline_mean=round(q.baseline_mean),selected='YES',reason='Passes all QC criteria; all spectra at the reference condition retained (no cherry-picking)'))
SEL=pd.DataFrame(sel)
# chemical assignment
CHEM=[
 ('NAM',541,'Pyranose-ring skeleton','Skeletal ring deformation δ(C–C–O)/δ(C–C–C)','Glucopyranose ring of MurNAc','Sugar-ring fingerprint (shared by hexosamines; not NAM-unique alone)','400–600 (region)','L6'),
 ('NAM',830,'Pyranose ring / anomeric centre','ν(C–O–C) ring and/or δ(C1–H) (anomeric region)','Ring C–O–C and anomeric C1','Carbohydrate ring mode','800–950 (region)','L6'),
 ('NAM',870,'Pyranose ring','ν(C–C)/ν(C–O–C) ring stretching','Glucopyranose ring','Carbohydrate ring mode','800–950 (region)','L6'),
 ('NAM',929,'Ring C–O–C / C–C; possibly lactyl C–C(OOH)','ν(C–O–C)/ν(C–C); lactyl contribution not verified','Ring and/or 3-O-lactyl side chain','Possibly distinguishes MurNAc (lactyl ether) from GlcNAc – unverified','800–950 (region)','L6, L5'),
 ('NAM',955,'C–C skeleton / CH3','ν(C–C) and/or CH3 rocking (N-acetyl or lactyl methyl)','Ring C–C; N-acetyl / lactyl CH3','General; tentative','~950–960 (edge of 800–950 region)','L5, L6'),
 ('NAM',1023,'C–O (C–OH)','ν(C–O)/ν(C–C), C–OH stretching','Ring hydroxyl-bearing carbons (C4, C6)','Carbohydrate C–O band','1000–1200 (region)','L6'),
 ('NAM',1127,'C–O–C ether / C–C','ν(C–O–C) (ring / 3-O-lactyl ether) or ν(C–C)','Ring oxygen and ether linkage','Carbohydrate C–O–C band','1000–1200 (region)','L6'),
 ('LTA',802,'Phosphodiester','ν(O–P–O) symmetric stretch','Poly(glycerol-phosphate) backbone','Backbone-specific for teichoic-acid-type polymers (with 1092)','~813','L5'),
 ('LTA',861,'Polyol / glycosyl C–C, C–O–C','ν(C–C)/ν(C–O–C)','Glycerol units and sugar substituents','General','800–950 (region)','L6'),
 ('LTA',1092,'Phosphodiester (PO2−)','ν_s(PO2−) symmetric stretch','Poly(glycerol-phosphate) backbone','Strongest LTA band; phosphodiester backbone','1090–1095','L5, L7 (+L8 IR, whole cells)'),
 ('LTA',1459,'CH2 (acyl chains, glycerol)','δ(CH2) scissoring','Glycolipid anchor fatty-acyl chains; glycerol CH2','Non-specific (all lipids / CH2-rich compounds)','1440–1460','L7'),
]
chem=[]
for a,m,fg,vib,comp,rel,lit,cit in CHEM:
  p=PK[(PK.analyte==a)&(PK.nominal==m)].iloc[0]; conf=MLIT[(a,m)][7]
  chem.append(dict(Biomarker=a,Category=p.role,Raman_shift=fw(p.pos_mean),Mean_SD=f'{p.pos_mean:.1f} ± {p.pos_sd:.1f}',Intensity=f'{p.height_mean:.0f} ± {p.height_sd:.0f} counts (rel. {p.rel:.2f})',SNR=round(p.snr_mean,1),
    Literature=lit,Molecular_vibration=vib,Functional_group=fg,Chemical_component=comp,Biomarker_relevance=rel,Citation=cit,Confidence=conf,Statement='Tentative assignment.'))
CHEM=pd.DataFrame(chem)
EVID={'L1':'SERS','L2':'SERS','L4':'SERS','L3':'Biological-sample Raman (whole cells)','L5':'Band compilation from biological tissues','L6':'Review of pure related compounds (carbohydrates)','L7':'Review of pure related compounds (lipids)','L8':'Biological-sample FTIR (whole cells)','L9':'NIR + DFT (pure compound; not Raman)','L10':'Normal Raman of related pure polymers (not accessed)','L11':'UV resonance Raman (not accessed)'}
tr=[]
for _,c in CT.iterrows():
  if c.category not in ('Primary marker','Supporting peak'): continue
  p=PK[(PK.analyte==c.biomarker)&(PK.nominal==c.peak)].iloc[0]; L_=MLIT[(c.biomarker,c.peak)]
  ev='; '.join(EVID.get(x.strip(),'') for x in L_[6].replace('(+L8 IR)','').split(',') if x.strip() in EVID) or '—'
  tr.append(dict(Biomarker=c.biomarker,Category=c.category,Experimental_peak=fw(p.pos_mean),SD=round(p.pos_sd,1),Intensity_counts=f'{p.height_mean:.0f} ± {p.height_sd:.0f}',CV_pct=round(p.cv,1),SNR=round(p.snr_mean,1),
    Replicate_frequency=f'{p.n_detected}/{p.n} ref; min day {c.min_day_detection_pct:.0f} %'+('' if c.biomarker=='LTA' else f'; indep. spots {c.independent_spot_set_pct:.0f} %'),
    Valid_spectrum='Yes (QC pass)',Reproducible=('Yes' if c.C1_reproducible else 'Partly'),Not_background=('Yes' if c.C3_background_separated else 'Partly (edge/glass)'),
    Literature_peak=L_[1],Assignment=L_[3],Evidence_type=ev,Citation=L_[6],Confidence=L_[7]))
TR=pd.DataFrame(tr)
CHG=pd.DataFrame([
 ['Spike removal','MAD z > 6 on first difference; 7-pt median replacement','Same criterion + width guard (≤ 2 px) + linear interpolation','v2.1 clipped the apex of sharp NAM bands (flagged 5.2 points/spectrum at 460–960 cm-1); marker heights were under-estimated by 11–12 % on average'],
 ['Hot pixels','Not handled','Fixed CCD pixels 640 (1095.7 cm-1) and 700 (1189.5 cm-1) interpolated','Same pixel flagged in ≥ 59 spectra on 6 dates and visible in dark frames (instrument artefact)'],
 ['Noise estimate','SD of (despiked − smoothed)','Robust SD (1.4826 × MAD) of the same residual','Sharp peaks inflated the SD; robust estimate reflects detector noise'],
 ['NAM strongest-marker intensity','820 ± 42 counts','%.0f ± %.0f counts'%(bn.loc['NAM','strongest_marker_height_mean'],bn.loc['NAM','strongest_marker_height_sd']),'Result of the spike-removal fix'],
 ['NAM SNR','31.7 ± 1.4','%.1f ± %.1f'%(bn.loc['NAM','snr_mean'],bn.loc['NAM','snr_sd']),'Result of robust noise + spike fix'],
 ['LTA strongest-marker intensity','1103 ± 94 counts','%.0f ± %.0f counts'%(bn.loc['LTA','strongest_marker_height_mean'],bn.loc['LTA','strongest_marker_height_sd']),'Broad LTA bands barely affected'],
 ['LTA SNR','27.6 ± 0.7','%.1f ± %.1f'%(bn.loc['LTA','snr_mean'],bn.loc['LTA','snr_sd']),''],
 ['NAM marker set','541, 829, 870, 929, 955, 1023, 1127','unchanged','Re-verified with v3 criteria'],
 ['NAM supporting peaks','457, 487, 1249','457, 487, 1249, 1589','1589 meets the supporting rule (100 % ref; 91 % overall detection)']],
 columns=['Item','v2.1','v3','Reason'])
out=dict(GO=GO,ACQ=ACQ,SEL=SEL,CHEM=CHEM,TR=TR,CHG=CHG)
pickle.dump(out,open(os.path.expanduser('~/work/final_v3.pkl'),'wb'))
print(TR.to_string()); print(CHG.to_string())
