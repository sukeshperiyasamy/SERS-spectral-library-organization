"""Builds 09_Reports/LPS_Findings_and_Parameters_Report.docx from the library files (QC logs, reference tables)
and the LPS results of the DFT and SERS work. Also draws the QC-by-power figure."""
import os,json,pandas as pd,numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt,Cm,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
HERE=os.path.dirname(os.path.abspath(__file__)); LIB=os.path.abspath(os.path.join(HERE,'..','..')); REPO=os.path.abspath(os.path.join(LIB,'..'))
F=os.path.join(LIB,'04_Figures'); QC=os.path.join(LIB,'07_QC_and_Exclusions'); REF=os.path.join(LIB,'03_Reference_Spectra','LPS')
os.makedirs(os.path.join(F,'LPS_Summary_20261027'),exist_ok=True)
scr=pd.read_csv(os.path.join(QC,'LPS_Session_20260928_QC_Log.csv')); rfs=pd.read_csv(os.path.join(QC,'LPS_Reference_Session_20260928_QC_Log.csv'))
mem=pd.read_csv(os.path.join(REF,'LPS_Reference_Members.csv')); mk=pd.read_csv(os.path.join(REF,'LPS_Reference_Marker_Peaks.csv'))
sers=json.load(open(os.path.join(REPO,'SERS_Results_Oct2026','tables','results.json'))); serst=pd.read_csv(os.path.join(REPO,'SERS_Results_Oct2026','tables','target_band_detection.csv')); serp=pd.read_csv(os.path.join(REPO,'SERS_Results_Oct2026','tables','lps_session_reproducible_bands.csv'))
dft=json.load(open(os.path.join(LIB,'05_Tables','DFT_vs_Experiment_results.json')))['LPS']
# ---------- figure: ripple and 425 SNR by condition
a=scr[scr.category=='LPS_Bulk'][['power','int_s','ripple','snr','QC']].rename(columns={'snr':'snr425'})
b=rfs[rfs.category=='LPS_Bulk'][['power','int_s','ripple','snr425','QC']]
allr=pd.concat([a,b],ignore_index=True)
fig,axs=plt.subplots(1,2,figsize=(10,3.6)); rng=np.random.default_rng(3)
for i,p in enumerate((60,70,80)):
    v=allr[allr.power==p]; ax=axs[0]; ax.plot(i+rng.uniform(-.12,.12,len(v)),v.ripple,'o',color='#b5421c',ms=5,alpha=.8)
axs[0].axhline(50,color='k',ls='--',lw=.8); axs[0].text(2.4,56,'limit 50 counts',ha='right',fontsize=7.5); axs[0].set_yscale('log'); axs[0].set_xticks([0,1,2]); axs[0].set_xticklabels(['60 %','70 %','80 %']); axs[0].set_ylabel('ripple (counts, log scale)'); axs[0].set_title('Fixed-pattern ripple by laser power',loc='left',fontsize=9.5,fontweight='bold')
d60=allr[(allr.power==60)&(allr.QC.isin(['PASS','SUPPORTING','REVIEW']))]
for i,t in enumerate((30,40)):
    v=d60[d60.int_s==t]; axs[1].plot(i+rng.uniform(-.12,.12,len(v)),v.snr425,'o',color='#1f5fa8',ms=5,alpha=.8); axs[1].plot([i-.25,i+.25],[v.snr425.median()]*2,'k',lw=1.3)
axs[1].axhline(10,color='k',ls='--',lw=.8); axs[1].set_xticks([0,1]); axs[1].set_xticklabels(['30 s','40 s']); axs[1].set_ylabel('SNR of the 425 cm$^{-1}$ band'); axs[1].set_title('Signal-to-noise at 60 % power',loc='left',fontsize=9.5,fontweight='bold')
for ax in axs: ax.spines[['top','right']].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(F,'LPS_Summary_20261027','LPS_QC_by_power_and_time.png'),dpi=200); plt.close(fig)
# ---------- document
d=Document(); s=d.sections[0]; s.page_width=Cm(21); s.page_height=Cm(29.7)
for k in ('left_margin','right_margin','top_margin','bottom_margin'): setattr(s,k,Cm(1.4))
st=d.styles['Normal']; st.font.name='Arial'; st.font.size=Pt(10); st.element.rPr.rFonts.set(qn('w:eastAsia'),'Arial'); st.paragraph_format.space_after=Pt(4)
for n,sz in (('Heading 1',14),('Heading 2',11.5)):
    h=d.styles[n]; h.font.name='Arial'; h.font.size=Pt(sz); h.font.color.rgb=RGBColor(0,0,0); h.element.rPr.rFonts.set(qn('w:eastAsia'),'Arial')
def shade(c,hx):
    pr=c._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd'); sh.set(qn('w:val'),'clear'); sh.set(qn('w:color'),'auto'); sh.set(qn('w:fill'),hx); pr.append(sh)
def para(t,bold=False,italic=False,size=None):
    p=d.add_paragraph(); r=p.add_run(t); r.bold=bold; r.italic=italic
    if size: r.font.size=Pt(size)
def bullets(items):
    for t in items: d.add_paragraph(t,style='List Bullet')
def table(head,rows,widths,fs=8.5,fills=None):
    t=d.add_table(rows=1,cols=len(head)); t.style='Table Grid'
    for i,x in enumerate(head):
        c=t.rows[0].cells[i]; c.text=''; r=c.paragraphs[0].add_run(x); r.bold=True; r.font.size=Pt(fs); shade(c,'D9D9D9')
    for k,row in enumerate(rows):
        cs=t.add_row().cells
        for i,x in enumerate(row):
            cs[i].text=''; r=cs[i].paragraphs[0].add_run(str(x)); r.font.size=Pt(fs)
        if fills and fills[k]: shade(cs[-1],fills[k])
    for row in t.rows:
        for i,w in enumerate(widths): row.cells[i].width=Cm(w)
    d.add_paragraph()
def fig(path,cap,w=17):
    d.add_picture(path,width=Cm(w)); d.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER; para(cap,italic=True,size=8.5)
FR=os.path.join(F,'LPS_Reference_20260928'); FD=os.path.join(F,'DFT_Comparison_20261027'); FS=os.path.join(REPO,'SERS_Results_Oct2026','figures')
para('Lipopolysaccharide (LPS): Findings and Parameters',bold=True,size=18)
para('Bulk Raman reference, simulation and SERS results for E. coli O111:B4 LPS, with every setting used',size=11)
para('SERS sepsis project, bulk-powder Raman spectral library. Version 1.0, 27 October 2026. Sources: library v3.3 (QC logs, reference tables), the LPS fragment simulation, and the SERS session of 7 October 2026.',size=9)

d.add_heading('1. Summary',1)
para('A bulk-powder Raman reference spectrum of LPS has been established on a glass slide at 60 % laser power, 40 s and 5 accumulations (10 independent spots). Its two primary markers are the bands at 425 and 1080 cm-1, with supporting bands at 766, 861 and 997 cm-1. The spectrum is reproducible between spots (mean pairwise r = 0.92), clearly different from NAM (r = 0.17) and less similar to LTA (r = 0.52). The 425 cm-1 band is the strongest and has no assignment in the checked literature, so it is used as an empirical fingerprint.')
para('Two further pieces of work give weaker support. A DFT simulation of five LPS fragments reproduces the position of four of the five bands to within 5 cm-1, but this is no better than chance and the overall spectral shape does not match. A SERS session on etched silicon did not detect LPS by the project rule, although a reproducible set of ten bands appeared on 21 of 35 spots and is worth repeating.')
table(['Item','Result'],[
 ['Reference condition','785 nm, 60 % power, 40 s, 5 accumulations, bulk powder on glass, hand-closed dark'],
 ['Reference set','10 spots (S10-S12, S14-S20); S13 excluded as glass-dominated'],
 ['Primary markers','425 cm-1 (10/10 spots, SNR median 38) and 1080 cm-1 (10/10, SNR 15, broad)'],
 ['Supporting markers','766, 861 and 997 cm-1'],
 ['Reproducibility','Pairwise r 0.916; r to NAM 0.17; to LTA 0.52'],
 ['DFT (5 fragments)','4 of 5 bands within 5 cm-1 of a calculated mode, not above chance (p = %.2f); shape r = %.2f'%(dft['t5']['p'],dft['r_equal'])],
 ['SERS on silicon, 7 Oct 2026','Not detected by the project rule (989 and 1330 cm-1); a ten-band set seen on %d of %d spots, absent from the blank'%(sers['n_carry'],sers['n_lps'])],
 ['Main limits','Dark frames contained some sample light (intensities 3-34 % low); glass band hides 1308-1455 cm-1; no pure-LPS normal-Raman literature for this serotype']],[4.5,13.5])

d.add_heading('2. Sample and instrument',1)
table(['Item','Detail'],[
 ['Sample','Lipopolysaccharide from Escherichia coli O111:B4, Sigma-Aldrich L2630-10MG, lot 0000442391; phenol-extracted, smooth (S-type) LPS with lipid A, core oligosaccharide and O-antigen'],
 ['Form and storage','Lyophilised powder, off-white to faint yellow; supplier protein limit 3 % (Lowry-TCA); stored at 2 to 8 C. The label photo is in 03_Reference_Spectra/LPS; the source number is partly legible and should be checked on the certificate of analysis.'],
 ['Presentation','Powder placed directly on a glass slide; no other substrate'],
 ['Instrument','B&W Tek i-Raman Plus, BWS465-785H, 785 nm, software BWRam 4.15; usable range ends at 2842 cm-1, so the C-H stretching region is not available'],
 ['Laser power','Recorded as a percentage of the maximum (not converted to mW)'],
 ['Detector limit','65,535 counts (saturation)']],[4.5,13.5])

d.add_heading('3. Measurements and parameters used',1)
para('LPS was measured on four occasions. The table lists the settings of each; the reference condition was fixed only after the troubleshooting on 28 September.')
table(['Date','Purpose','Power','Time','Acc.','Spectra','Outcome'],[
 ['13 Apr 2026','First LPS test on glass','10-20 %','10-60 s','2-60','14','Weak signal dominated by the glass band; no reference possible'],
 ['24 Sep 2026','Folder labelled LPS','60-90 %','30 s','5','-','Bottle checked: powder was NAM; data moved to the NAM library'],
 ['27-28 Sep 2026','Power screening','60, 70, 80 %','30 s','5','19 + 10 blanks','60 %: 8 pass; 70 %: 4 pass; 80 %: 0 of 5 (ripple)'],
 ['28 Sep 2026','Troubleshooting','60, 70 %','5-40 s','1-5','check frames','Ripple at 70 % is in the collected light; software dark contained sample light'],
 ['28 Sep 2026','Reference acquisition','60 %','40 s','5','11 spots + blanks','10 spots accepted; S13 excluded']],[2.3,3.2,2,1.6,1.2,2.4,5.3],fs=8)
d.add_heading('3.1 Why 60 %, 40 s and 5 accumulations',2)
bullets(['Power: at 70 % and above a fixed-pattern ripple appears. In the screening session the ripple at 80 % was a median of 474 counts (limit 50), and three spots at 70 % failed in the reference session. At 60 % the median ripple was about 14 to 23 counts. The ripple comes from the instrument and is present in the collected light, so it cannot be removed by changing the dark.',
 'Integration time: 40 s instead of 30 s raised the signal-to-noise ratio of the 425 cm-1 band; it was 19 to 63 on the accepted spots.',
 'Accumulations: 5 were used throughout, as for NAM.',
 'Dark: in the troubleshooting test the software dark contained sample light (about 3,400 counts against a true dark of about 1,470 at 30 s x 5; the true dark at 40 s x 5 is about 1,480 to 1,525). The dark was therefore taken with the shutter closed by hand.',
 'Glass blanks: blanks at the full settings (30 s or 40 s, 5 acc) saturated the glass band in 12 of 13 cases, so short blanks (5 s, 1 acc) were used to remove the glass shape.'])
fig(os.path.join(F,'LPS_Summary_20261027','LPS_QC_by_power_and_time.png'),'Figure 1. Left: ripple of every LPS spectrum by laser power (dashed line: limit of 50 counts). Right: signal-to-noise ratio of the 425 cm-1 band at 60 % power for 30 s and 40 s (bars mark the medians).')
d.add_heading('3.2 Processing and quality-control parameters',2)
table(['Step','Setting'],[
 ['Signal','Dark-subtracted signal = raw - dark; recomputed when the software had smoothed it'],
 ['Detector','Two defective pixels (about 1095.7 and 1189.5 cm-1) repaired'],
 ['Range','400-1800 cm-1'],
 ['Despiking','MAD z above 6, spike width 2 pixels or less'],
 ['Smoothing','Savitzky-Golay, window 11, order 3'],
 ['Baseline','Asymmetric least squares, lambda 1e5, p 0.01, 10 iterations'],
 ['Noise','1.4826 x MAD of (despiked - smoothed)'],
 ['Normalisation','Min-max; LPS intensities are compared as ratios to the 425 cm-1 band because counts vary 3-5 times between spots'],
 ['QC limits','No saturation in 400-1800 cm-1; ripple 50 counts or less; SNR 10 or more; glass-dominated spots excluded (glass-zone to 800-1000 cm-1 area ratio above 8)'],
 ['Glass zone','1308-1455 cm-1, left out of all correlations'],
 ['Band classes','C1 primary, C2 supporting, C3 glass or background, C4 uncertain']],[4,14])

d.add_heading('4. Findings: the bulk reference',1)
rip=mem.ripple; sn=mem.snr425
para(f"The reference is the mean of 10 spots. Ripple on these spots is {rip.min():.0f} to {rip.max():.0f} counts, the 425 cm-1 SNR is {sn.min():.0f} to {sn.max():.0f}, and the glass ratio is {mem.glass_ratio.min():.1f} to {mem.glass_ratio.max():.1f} (limit 8). Each spot correlates with the others at r = {mem.r_to_others.min():.2f} to {mem.r_to_others.max():.2f} and with NAM at only {mem.rNAM.min():.2f} to {mem.rNAM.max():.2f}.")
fig(os.path.join(FR,'FigR2_LPS_Reference_Mean_Median_SD_Bands.png'),'Figure 2. LPS bulk reference spectrum (mean, median and SD of 10 spots) with the classified bands. The grey block is the glass zone.')
d.add_heading('4.1 Bands',2)
cls={'C1':'Primary','C2':'Supporting','C3':'Glass / background','C4':'Uncertain'}
rows=[]
for r in mk.itertuples():
    c=r._1[:2]
    if c in('C1','C2'): rows.append([f"{r.pos_mean:.1f}",cls[c],r.detected,f"{r.pos_sd:.1f}",f"{r.snr_median:.0f}",f"{r.glass_share_pct:.0f} %",f"{r.fwhm:.0f}",r.literature if str(r.literature)!='nan' else 'none'])
table(['Band (cm-1)','Class','Found in','Position SD','SNR (median)','Glass share','FWHM','LPS literature band within 12 cm-1'],rows,[1.8,2.2,1.6,1.7,1.9,1.8,1.4,5.6],fs=8)
para('The 425 cm-1 band is present on all ten spots, is absent from the glass blanks and from NAM, and was also seen in the April 2026 data and the 28 September screening. No LPS literature band lies within 12 cm-1 of it, so it is used as an empirical marker. Its position is consistent with the low-frequency skeletal region of sugar rings. The 1080 cm-1 band is broad and about 14 % of its height overlaps the glass Si-O feature near 1091 cm-1; the closest literature value is 1075 cm-1 in the normal Raman spectrum of LPS powder (E. coli O55:B5). The weaker bands at 478, 541, 631, 656, 1124, 1248 and 1458 cm-1 are seen on only 4 to 8 of the 10 spots and are not used for identification; the glass bands at 1257 and 1657 cm-1 and the glass zone itself are never reported as LPS bands.')
d.add_heading('4.2 Identity and comparison with the other molecules',2)
table(['Comparison (glass zone excluded)','r','Meaning'],[['LPS screening, 28 Sep (60 %, 30 s)','0.98','Same material and spectrum'],['LPS, April 2026 (10-20 %)','0.80','Same pattern, noisier'],['LTA preliminary reference','0.52','Different material; shared broad cell-wall features'],['NAM reference','0.17','Not NAM; NAM markers 929, 955 and 1022 cm-1 absent']],[7,2,9])
fig(os.path.join(FR,'FigR5_LPS_vs_Other_References.png'),'Figure 3. LPS reference compared with the NAM and LTA references.')
d.add_heading('4.3 Literature comparison',2)
para('The 28 September bands were compared with the SERS lists (Wu 2021; Yang 2022), the normal-Raman spectrum of LPS powder (Verde 2021) and general carbohydrate and lipid group frequencies (Wiercigroch 2017; Czamara 2015). Only tentative interpretations are made.')
table(['Observed band (cm-1)','Tentative interpretation','Evidence'],[
 ['425','Unassigned; skeletal ring-deformation region','No LPS literature match'],
 ['539','Consistent with glycosidic ring deformation','Position match to SERS bands at 543 and 550'],
 ['765','Unassigned','No match'],
 ['860-900 (broad)','Consistent with glycosidic C-O-C and beta-anomeric sugar modes','Position match to SERS bands at 850 and 855'],
 ['997','Consistent with C-H bending or sugar C-O-C','SERS 988 and 1003; normal Raman within 24 cm-1'],
 ['1081','Consistent with C-O stretching of the O-antigen and core sugars and/or phosphate','Best match: normal Raman 1075 (difference +6)'],
 ['1126','Consistent with acyl-chain C-C stretching of lipid A','Position match to SERS 1131'],
 ['1308-1455','LPS C-H bending bands are expected here but cannot be separated from glass','Cannot be evaluated on glass slides']],[3.2,8,6.8],fs=8)
d.add_heading('4.4 Instrument notes affecting the data',2)
bullets(['The software dark contained sample light, so intensities may be 3 to 34 % low. Band positions and ratios are not affected.',
 'Bulk intensity varies 3 to 5 times between spots (focus and packing); ratios to the 425 cm-1 band are therefore used.'])
fig(os.path.join(FR,'FigR4_Dark_Check_and_Intensity.png'),'Figure 4. Left: dark level used for the LPS spectra compared with shutter-closed check frames. Right: 425 cm-1 band height per spot and the estimated under-estimate.')

d.add_heading('5. Findings: simulation of LPS fragments',1)
para('Intact LPS is too large and variable to calculate, so five fragments were simulated separately and combined: KDO, L-glycero-D-manno-heptose, D-glucosamine, myristic acid and phosphoric acid.')
table(['Parameter','Setting'],[['Software','Gaussian (version not recorded in the files read)'],['Method and basis set','B3LYP / 6-31G(d); route: opt freq=raman scf=tight integral=ultrafine'],['Environment','Gas phase (no solvent keyword)'],['Start structures','PubChem 3D, molecular-mechanics pre-optimisation (200 steepest-descent and 500 conjugate-gradient steps)'],['Frequency scale factor','0.9613'],['Combination','Equal-weight average and non-negative least squares'],['Comparison with experiment','Nearest calculated mode to each primary and supporting band; random-shift chance test (5,000 shifts)']],[4.5,13.5])
para(f"Result: of the five bands, {dft['t5']['real']} lie within 5 cm-1 and all five within 18 cm-1 of a calculated mode, but the five fragments together give about {dft['density_per_100']:.0f} modes per 100 cm-1, and random shifts give {dft['t5']['decoy_mean']:.1f} of 5 within 5 cm-1 (p = {dft['t5']['p']:.2f}). The 425 cm-1 band is the strongest in the experiment but the only calculated mode near it (phosphoric acid, 425.9 cm-1) is weak. The equal-weight composite correlates with the experimental spectrum at r = {dft['r_equal']:.2f}; with fitted weights r = {dft['nnls']['r']:.2f} and R-squared is negative. The simulation therefore supports a few tentative assignments (for example 861 and 1080 cm-1 as sugar modes) but does not explain the spectrum.")
fig(os.path.join(FD,'LPS_Overlay_Exp_vs_DFT.png'),'Figure 5. Experimental LPS reference (top) and fragment simulation (bottom). Dashed lines mark the experimental bands, coloured by the distance to the nearest calculated mode.')

d.add_heading('6. Findings: SERS on etched silicon, 7 October 2026',1)
para('LPS was also measured on etched silicon with SERS. The full analysis is in SERS_Results_Oct2026; the settings and the main result are summarised here.')
table(['Parameter','Setting'],[['Instrument','B&W Tek i-Raman Plus, 785 nm'],['Substrate','Etched silicon (operator information); recipe units not recorded'],['Spectra','35: lps2 19 (50 %, 15 s, 2 acc); lps1 16 (30 %, 15 s, 2 acc x 11; 50 %, 10 s, 2 acc x 5)'],['Time','06:35 to 09:06 on 7 Oct 2026'],['Blank','Substrate blank of 5 spectra (15 %, 10 s, 2 acc) taken at 01:07 to 01:18; bare silicon of 6 Jun 2026 (12 spectra) as a second check'],['Detection rule','Peak within 5 cm-1 of the target, at least 3 pixels wide, prominence at least 3 times the noise; LPS needs 989 and 1330 cm-1'],['Not recorded','Sample concentration, volume, deposition method, R6G check']],[4.5,13.5])
st_=serst[serst.molecule=='LPS']
table(['Band (cm-1)','Detected in LPS spectra (of 35)','In blank (of 5)'],[[r.band,int(r.detected_sample),int(r.detected_blank)] for r in st_.itertuples()],[4,6,4])
para(f"None of the bulk LPS bands and not the 989 cm-1 band is found; 1330 cm-1 appears in 15 spectra. By the project rule LPS is therefore not detected. Ten bands do repeat on {sers['n_carry']} of {sers['n_lps']} spots (619, 785, 878, 1009, 1238, 1330, 1368, 1455, 1536 and 1592 cm-1). They are absent from the blank and bare silicon, the spots that carry them correlate at r = {sers['repro']['carrying_median_r']:.2f}, and the silicon band is weaker there ({sers['si_carry']:.0f} against {sers['si_nocarry']:.0f} counts). The set correlates with the bulk LPS reference at only r = {sers['sim']['LPS']:.2f}. It is consistent with an organic layer containing CH2 and CH3 groups on the silicon; LPS is one possible source, but without a same-period blank or solvent control contamination cannot be excluded.")
fig(os.path.join(FS,'F3_LPS_individual_spectra.png'),'Figure 6. LPS session on silicon: spots with the reproducible band set (dotted lines), two spots without it, and the substrate blank.')

d.add_heading('7. Overall status and next steps',1)
table(['Question','Answer'],[
 ['Is there an LPS bulk reference?','Yes: established 28 Sep 2026, 10 spots at 60 %, 40 s, 5 acc'],
 ['What identifies LPS in the bulk spectrum?','The 425 cm-1 band (strongest, unassigned) with the broad 1080 cm-1 band; supported by 766, 861 and 997 cm-1; NAM and LTA are separated'],
 ['Does simulation explain it?','Only partly; agreement in position is not better than chance'],
 ['Is LPS detected by SERS?','Not by the project rule; one reproducible band set is a lead'],
 ['What limits the results?','Dark light in the dark frames (intensities 3-34 % low), the glass band over 1308-1455 cm-1, one lot and one session, no same-period blank in the SERS work']],[6,12])
bullets(['Measure a second LPS lot or a second session on glass to test the 425 and 1080 cm-1 markers.',
 'Check the certificate of analysis for the source number of lot 0000442391.',
 'Take shutter-closed darks for every spectrum to remove the 3-34 % intensity uncertainty.',
 'For SERS: repeat on a fresh substrate with a solvent-only control and a blank in the same period, keep 50 %, 15 s, 2 acc, and record concentration, volume and deposition.',
 'Measure the bulk LPS powder on the same type of silicon to see which bands the silicon-supported LPS gives.'])
d.add_heading('8. Source files',1)
table(['Content','Location'],[['Reference spectrum, members, marker peaks, status','SERS_Sepsis_Spectral_Library/03_Reference_Spectra/LPS'],['QC logs','07_QC_and_Exclusions/LPS_Session_20260928_QC_Log.csv; LPS_Reference_Session_20260928_QC_Log.csv'],['Figures','04_Figures/LPS_Reference_20260928; LPS_Summary_20261027; DFT_Comparison_20261027'],['Earlier reports','09_Reports/LPS_Bulk_Reference_Report_20260928.docx; DFT_vs_Experimental_Comparison_NAM_LPS_LTA.docx; Simulation_Methods_and_Spectra_NAM_LPS_LTA.docx'],['SERS session','SERS_Results_Oct2026'],['Raw data','28-9-26-lps-bulk, 13-4-26, 14-426 (see Raw_Data_Index)']],[6,12])
d.save(os.path.join(LIB,'09_Reports','LPS_Findings_and_Parameters_Report.docx')); print('saved')
