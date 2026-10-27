# Builds 09_Reports/LTA_Bulk_Reference_Report_20261028.docx from the library tables written by lt4_build_library.py
import os,pickle,numpy as np,pandas as pd
from docx import Document
from docx.shared import Pt,Cm,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from lib2 import LIB
H=os.path.dirname(os.path.abspath(__file__)); R=pickle.load(open(os.path.join(H,'lt4_result.pkl'),'rb'))
q=pd.read_csv(os.path.join(LIB,'07_QC_and_Exclusions','LTA_Reference_Session_20261028_QC_Log.csv')); mem=pd.read_csv(os.path.join(LIB,'03_Reference_Spectra','LTA','LTA_Reference_20261028_Members.csv')); bands=pd.read_csv(os.path.join(LIB,'03_Reference_Spectra','LTA','LTA_Reference_20261028_Marker_Peaks.csv'))
mk_old=pd.read_csv(os.path.join(LIB,'03_Reference_Spectra','LTA','LTA_Reference_Marker_Peaks.csv'))
FIG=os.path.join(LIB,'04_Figures','LTA_Reference_20261028')
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
def fig(n,cap,w=17):
    d.add_picture(os.path.join(FIG,n),width=Cm(w)); d.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER; para(cap,italic=True,size=8.5)
sp=q[q.category=='LTA_Bulk']; core=sp[sp.QC=='PASS']; cm=R['cmp']
cls=lambda k:', '.join('S'+f.split('_S')[-1][:2] for f in sp[sp.QC==k].library_file)
para('LTA Bulk-Powder Raman Reference: Re-acquisition on Glass, 28 October 2026',bold=True,size=17)
para('Quality control, reference spectrum, bands, and the parameters that worked',size=11)
para('SERS sepsis project, bulk-powder Raman spectral library. Version 1.0, 28 October 2026. Raw data: bulk-lta (28 spots and 8 blanks). Supersedes the preliminary reference of 3 April 2026 (4 spectra), which is kept unchanged.',size=9)

d.add_heading('1. Summary',1)
para(f"The re-acquisition worked. Of 28 LTA spots measured at 80 % power, 45 s and 2 accumulations, {len(core)} pass every quality-control check and form a new reference. The new mean spectrum matches the April reference (r = {cm['LTA']:.2f}) and is clearly different from NAM (r = {cm['NAM']:.2f}) and LPS (r = {cm['LPS']:.2f}). The strongest band, 1092 cm-1, is present on every reference spot at a signal-to-noise ratio of about 29. Two points need attention before the next session: the eight blanks do not look like glass, and about one spot in three was lost to saturation or marginal ripple because the signal varies so much from spot to spot.")
table(['Item','Result'],[
 ['Condition','785 nm, 80 % power, 45 s, 2 accumulations, bulk powder on a glass slide, shutter-closed dark'],
 ['Spots measured',f'28 (SP_9 to SP_36) plus 8 blanks; SP_1 to SP_8 of the spot folder are copies of the blanks'],
 ['Quality control',f'PASS {len(sp[sp.QC=="PASS"])}, REVIEW {len(sp[sp.QC=="REVIEW"])} (ripple 50 to 58), EXCLUDE {len(sp[sp.QC=="EXCLUDE"])} (atypical shape), FAIL {len(sp[sp.QC=="FAIL"])} (5 saturated, 2 weak)'],
 ['Reference v2',f'Mean of {len(core)} spots; mean and median agree (r = {R["mm_r"]:.3f}); mean of all 18 PASS and REVIEW spots gives r = {R["sens"]:.3f}'],
 ['Primary bands','1092 cm-1 (SNR 29), 539 cm-1 (SNR 16), 861 cm-1 (SNR 16)'],
 ['Supporting bands','419, 629, 723, 798, 1459, 1583 and 1751 cm-1; 1246 cm-1 (phosphate region) is seen on 7 of 10 spots'],
 ['Identity',f"r to April LTA {cm['LTA']:.2f}; to LPS {cm['LPS']:.2f}; to NAM {cm['NAM']:.2f} (glass zone excluded)"],
 ['Sample','Sigma-Aldrich L2515-10MG, lipoteichoic acid from Staphylococcus aureus, lot 0000419622, source number 0000404178'],
 ['Not recorded','Purity (no figure on the supplier page found; lot certificate not obtained); objective']],[4,14])

d.add_heading('2. Sample and instrument',1)
table(['Item','Detail'],[['Sample','Lipoteichoic acid from Staphylococcus aureus, Sigma-Aldrich L2515-10MG, lot 0000419622, source number 0000404178 (as given by the operator; the label reads bacterial cell wall polymer); powder placed directly on a glass slide. The same vial was used for the 3 Apr 2026 data (operator). The supplier product information sheet (L2515, sheet date 10/03, supplied by the operator) gives no purity figure and no physical form; the certificate of analysis for the lot has not been obtained, so purity is Not recorded. The supplier describes LTA as a linear polymer of phosphodiester-linked glycerol phosphate bound to a lipid, with the C2 position usually glycosylated and/or D-alanylated, and gives a water solubility of 5 mg/ml.'],
 ['Instrument','B&W Tek i-Raman Plus, BWS465-785H, 785 nm; usable range ends at 2842 cm-1 (no C-H stretching region)'],
 ['Laser power','80 % (instrument setting, not converted to mW)'],
 ['Time of measurement','28 Oct 2026, 02:11 to 04:30 (instrument clock): blanks 02:11 to 02:25, spots from 02:29'],
 ['Dark','Median dark 1504 to 1512 counts, in line with a shutter-closed dark (true dark about 1480 to 1525 counts)']],[4,14])

d.add_heading('3. Parameters used',1)
table(['Parameter','Setting'],[['Laser wavelength / power','785 nm / 80 %'],['Integration time / accumulations','45 s / 2'],['Spots','28 different spots on the powder (SP_9 to SP_36)'],['Blanks','8 spectra at the same settings (see Section 6)'],
 ['Processing','Pipeline v3: dark-subtracted signal; two defective detector pixels repaired; 400-1800 cm-1; despiking (MAD z > 6, width 2 pixels or less); Savitzky-Golay 11/3; ALS baseline (lambda 1e5, p 0.01, 10 iterations); noise = 1.4826 x MAD; min-max normalisation'],
 ['QC limits','No saturation in 400-1800 cm-1; ripple 50 counts or less; SNR 10 or more; glass-dominated spots excluded (area ratio above 8); atypical-shape spots excluded (r to the core mean below 0.80)'],
 ['Band classes','C1 primary (all spots, SNR 15 or more, glass share below 25 %, relative CV 30 % or less); C2 supporting (80 % of spots, SNR 5 or more); C3 glass; C4 uncertain'],
 ['Glass zone','1308-1455 cm-1, left out of all correlations']],[4.5,13.5])

d.add_heading('4. Findings',1)
d.add_heading('4.1 Quality control of the 28 spots',2)
table(['Class','Spots','Reason'],[['PASS',cls('PASS'),'All checks met; used for the reference'],['REVIEW',cls('REVIEW'),'Ripple 50 to 58 counts (limit 50); the brightest spots (SNR 26 to 34); kept as a check set'],['EXCLUDE',cls('EXCLUDE'),'Shape differs from the core (r to the core mean 0.48 to 0.76): off-powder or mixed spots'],['FAIL',cls('FAIL'),'S17-S20 and S27 saturated at 65,535 counts; S09 and S10 weak (SNR of the 1092 band 7 and 4)']],[2.2,6.8,9],fills=['EAF6EE','FFF4D6','F2F2F2','FDECEA'])
fig('FigL5_QC_Overview.png','Figure 1. QC per spot: ripple, highest raw count, SNR of the 1092 cm-1 band, and ripple against signal. Green = PASS, orange = REVIEW, grey = EXCLUDE, red = FAIL.')
para('The signal varies about 40 times between spots (highest raw count from 5,900 to 65,535), which is typical of powder focus and packing. The first spot (S09) satisfied the ripple check (29 counts) but was weak, so it did not count towards the reference. The ripple measured on the spots rises with the square root of the signal (r = 0.95 with the median raw count), so a spot that is very bright fails the ripple limit even though its signal-to-noise ratio is best. The glass-zone ratio of every spot is below 8 (highest 4.9).')
d.add_heading('4.2 Reference spectrum',2)
para(f"The reference is the mean of {len(core)} spots (S11, S21, S22, S23, S24, S26, S29, S30, S32, S34). Mean pairwise correlation between spots is {np.mean(R['pw']):.2f} (lowest {np.min(R['pw']):.2f}); the mean and median agree at r = {R['mm_r']:.3f}; adding the eight REVIEW spots changes the mean very little (r = {R['sens']:.3f}).")
fig('FigL3_LTA_Reference_Bands.png','Figure 2. LTA reference v2: mean, median and SD of 10 spots with the classified bands. The dashed line is the glass shape from the 28 Sep blanks scaled to the median spot; the grey block is the glass zone.')
mrows=[[r.spot,r.acq[11:16],f"{r.raw_max:.0f}",f"{r.ripple:.0f}",f"{r.snr1092:.0f}",f"{r.glass_ratio:.1f}",f"{r.r_core:.2f}",f"{r.rLTA_April:.2f}"] for r in mem.itertuples()]
table(['Spot','Time','Highest raw count','Ripple','SNR 1092','Glass ratio','r to core','r to April LTA'],mrows,[1.8,1.8,2.6,1.8,2,2,2,2.6],fs=8)
d.add_heading('4.3 Bands',2)
rows=[]
for r in bands.itertuples():
    c=r._1[:2]
    if c in('C1','C2') or r.band==1246: rows.append([f"{r.pos_mean:.1f}",{'C1':'Primary','C2':'Supporting','C4':'Uncertain'}.get(c,c),r.detected,f"{r.pos_sd:.1f}",f"{r.snr_median:.0f}",f"{r.height_cv:.0f} %",f"{r.glass_share_pct:.1f} %"])
table(['Band (cm-1)','Class','Found in','Position SD','SNR (median)','Height CV','Glass share (estimate)'],rows,[2,2.5,2,2,2.5,2.2,3.5],fs=8.5)
para('The three primary bands are present on all ten spots. The band at 1246 cm-1 lies in the 1225 to 1250 cm-1 phosphate region used in the project detection rule, and 1459 cm-1 is the lipid CH2 band, so the phosphate-plus-lipid combination (1092 with 1459, and 1246 on most spots) is present in the bulk powder. The glass share is a rough estimate: the 28 Sep glass shape was scaled to each spot on 1290 to 1520 cm-1; it is below 7 % at every band, so the glass slide contributes little under the powder.')
d.add_heading('4.4 Comparison with the preliminary April reference',2)
cmpr=[['802.2 (SD 5)','799.6','Broad; moves by 3 cm-1, within the position tolerance'],['861.5','861.6','Same'],['1091.8','1092.0','Same'],['1458.8','1460.3','Same within 2 cm-1'],['541.2 (uncertain)','539.2','Now reproducible on 10 of 10 spots; promoted to primary'],['1367 (glass, 1 of 4 spots)','1328 (glass zone)','Glass feature in the glass zone; not used']]
table(['April reference (cm-1)','28 Oct reference (cm-1)','Comment'],cmpr,[4,4,10],fs=8.5)
fig('FigL4_LTA_vs_Other_References.png',f"Figure 3. New LTA reference against the April LTA, LPS and NAM references (normalised). r to April = {cm['LTA']:.2f}.")
ST=pickle.load(open(os.path.join(H,'lt8_stats.pkl'),'rb')); RAT={p:(m,c) for p,g,m,c in ST['ratios']}; COR={(a,b):c for a,b,c in ST['cor']}
d.add_heading('5. What the peaks say and how they are related',1)
para('This section reads each labelled peak against the structure the supplier gives for S. aureus LTA: a linear polymer of phosphodiester-linked glycerol phosphate, bound to a lipid, with the C2 position of the glycerol usually glycosylated and/or D-alanylated. All assignments are tentative: they say what a band is consistent with, not what it proves.')
fig('FigL6_LTA_Peaks_Annotated.png','Figure 5. The reference spectrum with every labelled peak, coloured by the part of the molecule it is consistent with: red phosphodiester, blue glycerol skeleton, orange lipid chain, purple ester C=O, grey not assigned.')
d.add_heading('5.1 Peak by peak',2)
def rt(p): return f"{RAT[p][0]:.2f} (CV {RAT[p][1]:.0f} %)"
table(['Band (cm-1)','Found; height relative to 1092','Part of LTA it is consistent with','What the peak says','Caution'],[
 ['1092','10/10; 1.00','PO2- symmetric stretch of the phosphodiester, one in every repeat','The phosphate backbone is present. It is the strongest and most reliable band, and its height follows the amount of backbone in the focus','Phosphate groups also occur in phospholipids and nucleic acids, so the band alone is not specific (group frequency 1090-1095: Movasaghi 2007; Czamara 2015; Grunert 2018)'],
 ['1246','7/10; '+rt(1246),'PO2- asymmetric stretch region (1225-1250)','The second band of the phosphate pair; with 1092 it completes the PO2- signature','Weaker and broader, so seen on 7 of 10 spots; a protein impurity would add a band in the same region (purity not recorded)'],
 ['798','9/10; '+rt(798),'O-P-O / C-O-P stretching of the link between glycerol units','Phosphate bridges between the glycerol units','Region only; the April value of 813 cm-1 in the literature table is 13 cm-1 higher. Glass also scatters near 800 cm-1, but the glass estimate here is under 1 %'],
 ['861','10/10; '+rt(861),'C-C and C-O-C stretching of the glycerol (and any sugar) skeleton','The glycerol skeleton of the repeat','Carbohydrate region 800-950 (Wiercigroch 2017); not specific'],
 ['539','10/10; '+rt(539),'Skeletal deformation of the backbone (C-C-O, O-P-O)','Low-frequency fingerprint of the whole backbone; reproducible on every spot','No checked literature band; region only'],
 ['419','10/10; '+rt(419),'Skeletal deformation','Low-frequency fingerprint','Region only; close to the 425 cm-1 band of LPS, so use it only with the rest of the pattern'],
 ['723','10/10; '+rt(723),'CH2 rocking of long alkyl chains (general group frequency, not in the library tables)','The lipid anchor chains','Tentative; follows 1459'],
 ['1459','9/10; '+rt(1459),'CH2 scissoring of the lipid chains and glycerol CH2','Hydrocarbon is present (lipid anchor, glycerol)','Non-specific (Czamara 2015); lies next to the glass zone but is not affected by it'],
 ['1751','9/10; '+rt(1751),'Ester C=O stretching region','Ester links, such as D-alanyl esters on the glycerol and/or fatty-acid esters of the lipid','Weak; ester region taken from lipid group frequencies (Czamara 2015)'],
 ['629, 1583','8/10 each','Not assigned','No interpretation','Sharp bands near 619 and 1583 cm-1 also appear in the polystyrene-like blanks; check with a clean blank'],
 ['1328','10/10','Glass zone','Glass, not LTA','Never used as an LTA band']],[1.7,2.4,4.3,5,4.6],fs=7.5)
d.add_heading('5.2 How the peaks are related',2)
bullets(["By chemical group. The two phosphate bands (1092 and 1246) belong together as the symmetric and asymmetric stretch of the same PO2- group; 798 adds the O-P-O link. 861, 539 and 419 describe the glycerol skeleton. 1459 and 723 come from CH2 in the lipid chains, and 1751 from the ester links. Figure 7 maps these groups onto the molecule.",
 f"Between spots. The heights of all bands rise and fall together (correlation with 1092: 798 r = {COR[(1092,798)]:.2f}, 861 r = {COR[(1092,861)]:.2f}, 1459 r = {COR[(1092,1459)]:.2f}, 1751 r = {COR[(1092,1751)]:.2f}, 1246 r = {COR[(1092,1246)]:.2f}, 539 r = {COR[(1092,539)]:.2f}), because every band depends on how much powder is in the focus. This alone does not show a common origin.",
 "Ratios to 1092. What is more informative is that the ratios stay steady from spot to spot: 798 and 861 vary least (CV 4.5 % and 7.5 %), the lipid bands 1459 and 723 vary a little more (12 % and 14 %), and the weakest bands vary most (1246 about 22 %). A steady ratio is what one material gives, and the tight ratios of the backbone bands fit their sharing one unit.",
 f"Backbone to lipid. 1459 follows 1092 closely (r = {COR[(1092,1459)]:.2f}) and 723 follows 1459 (r = {COR[(1459,723)]:.2f}); the lipid-to-backbone ratio (1459/1092 = {RAT[1459][0]:.2f}) is steady, as expected when the lipid is covalently bound to the polymer and not a separate component.",
 "Ester to chain. 1751 follows both 1459 and 1092 (r = 0.94), in line with ester links on the polymer."])
table(['Band (cm-1)','Median height / height at 1092','CV between spots'],[[p,f"{RAT[p][0]:.2f}",f"{RAT[p][1]:.1f} %"] for p in (798,861,539,1459,723,419,1246,1751)],[3,5,4],fs=8.5)
fig('FigL7_LTA_Peak_Zooms.png','Figure 6. The main bands in the 10 reference spots (thin lines) and their mean (thick line).')
fig('FigL8_LTA_Structure_Map.png','Figure 7. Schematic of S. aureus LTA as the supplier describes it, with the bands that are consistent with each part. The drawing is generic and does not show the chain length or which substituent sits on which glycerol.')
d.add_heading('5.3 What the pattern says as a whole',2)
bullets(['A phosphodiester-linked glycerol backbone (1092, 1246, 798, 861), a hydrocarbon lipid part (1459, 723) and ester groups (1751) are all present in one reproducible spectrum. This is what the supplier describes for S. aureus LTA.',
 'It does not show which substituent (D-alanine or a sugar) is present, how long the chain is, or how pure the sample is. Protein or nucleic-acid impurities, and other phosphate lipids, would add bands in the same regions.',
 'It differs from LPS: the strongest LTA band is 1092 cm-1, whereas the strongest LPS band is 425 cm-1, and the overall correlation is only 0.50. Both carry phosphate and sugar-like bands, which is why they are not unrelated. NAM has no phosphate and correlates at 0.17.',
 'Identity therefore rests on the supplier record (Sigma L2515, S. aureus, lot 0000419622) together with this pattern. The wording stays "consistent with LTA".'])
d.add_heading('6. The blanks',1)
para(f"The eight blanks show sharp bands at 619, 1000, 1030, 1154, 1583 and 1602 cm-1, the strongest at 1000 cm-1 (SNR above 200), together with the broad glass band at about 1330 cm-1. Their correlation with the glass blanks of 28 September is only {R['r_blank_old']:.2f}. The pattern is polystyrene-like; the project flagged a polystyrene-like set on 9 February 2026, but the two were not compared directly here. The blanks are therefore flagged as suspect and were not used for the glass estimate. They show that something other than clean glass was measured: possible sources are a plastic surface, a contaminated slide or residue on the slide. The LTA spots do not carry the strongest of these bands (the 1000 cm-1 band is 6 to 10 times the noise on the spots, not 200), so the reference is not dominated by it, but the point should be settled with a clean blank.")
fig('FigL2_Reference_Spots_Processed.png','Figure 8. Baseline-corrected reference spots (green), their mean (black) and the mean of the 28 Oct blanks (dashed).')
d.add_heading('7. What to change in the next session',1)
table(['Issue','Evidence','Change'],[
 ['Blanks are not glass-like','Sharp bands at 1000 and 1030 cm-1 (SNR above 200); r = 0.07 to the 28 Sep glass blanks','Measure 3 blanks on the same clean glass slide used for the powder, away from the powder; clean the slide with the same solvent as before; note what the surface is'],
 ['Saturation on bright spots','Spots S17-S20 and S27 reach 65,535 counts; S12, S14 and S33 reach 62,000 to 65,000','Before the full 45 s spot, take a short test (5 s, 1 acc) and move on if its highest count is above about 6,000 (this predicts roughly 54,000 at 45 s, assuming counts scale with time); passing spots had 15,000 to 50,000'],
 ['Ripple limit and bright spots','Ripple follows the square root of the signal; 8 bright spots fall at 50 to 58 counts','Keep 80 %, 45 s, 2 acc and the ripple limit of 50; pick spots in the middle signal range rather than lowering power (the project found ripple grows above about 70 %)'],
 ['Weak first spots','S09 and S10 had SNR 7 and 4','Focus on a thick part of the powder before starting; the first spot must still show ripple of 50 or less'],
 ['Number of spots','10 pass; the plan was 12 to 15','Measure 5 more spots in the 15,000 to 50,000 count range to reach 15'],
 ['Duplicate files','SP_1 to SP_8 of the spot folder are the blank files (identical)','Keep blanks and spots in separate folders and check the file count before copying'],
 ['Sample record','Supplier, catalogue, lot and source number are now recorded; purity is not','Download the certificate of analysis for lot 0000419622 and record the purity; the April data came from the same vial'],
 ['Dark','Dark 1504 to 1512 counts, consistent with a shutter-closed dark','No change; keep closing the shutter by hand at the start and end']],[3.5,6,8.5],fs=8)
d.add_heading('8. Status and open points',1)
bullets(['Status of the LTA reference: ESTABLISHED, pending your confirmation (n = 10, one session, one powder).',
 'The main library report should be updated to v3.4 with a new section for this LTA reference once you confirm.',
 'The glass estimate is exploratory; it should be repeated with a clean glass blank.',
 'A second session or lot would test whether 1092, 539 and 861 cm-1 are reproducible beyond one powder.'])
d.add_heading('9. Files',1)
table(['Content','Location (SERS_Sepsis_Spectral_Library)'],[['Copies of the raw files','01_Raw_Data_Renamed/LTA_Bulk (LTA_Bulk_20261028_*) and Glass_Blank (Glass_Blank_20261028_*)'],['Processed spectra','02_Processed_Spectra/LTA and Glass_Blank'],['Reference, members, marker peaks','03_Reference_Spectra/LTA/*_20261028_* ; status in README_LTA_reference_status.txt'],['QC log and exclusions','07_QC_and_Exclusions/LTA_Reference_Session_20261028_QC_Log.csv ; Excluded_and_Flagged_Spectra.csv'],['Figures','04_Figures/LTA_Reference_20261028 (FigL1 to FigL5)'],['Workbook sheets','05_Tables/Spectral_Library_Metadata_and_Peaks.xlsx, sheets 43 to 47'],['Code','08_Methodology/code/lt1 to lt7'],['Original files','bulk-lta (unchanged)']],[5,13])
d.save(os.path.join(LIB,'09_Reports','LTA_Bulk_Reference_Report_20261028.docx')); print('saved')
