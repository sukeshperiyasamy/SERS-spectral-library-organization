"""Builds NAM_SERS_Problem_Analysis.docx (and its figure) from the session table and the earlier project reports."""
import os,json,pandas as pd,numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt,Cm,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.abspath(os.path.join(HERE,'..')); REPO=os.path.abspath(os.path.join(OUT,'..'))
FIG=os.path.join(OUT,'figures'); os.makedirs(FIG,exist_ok=True)
ses=pd.read_csv(os.path.join(OUT,'tables','nam_sers_sessions.csv'))
oct_=json.load(open(os.path.join(REPO,'SERS_Results_Oct2026','tables','results.json')))['chance']['NAM']
ses.loc[ses.session=='7 Oct 2026',['nam_detect_fraction','nam_chance_mean','nam_chance_p']]=[oct_['real'],oct_['mean'],oct_['p']]
# ---- figure: detection fraction vs chance
fig,ax=plt.subplots(figsize=(8,3.4)); xs=np.arange(len(ses))
ax.bar(xs-0.2,ses.nam_detect_fraction*100,0.4,color='#1f5fa8',label='NAM target bands (real positions)'); ax.bar(xs+0.2,ses.nam_chance_mean*100,0.4,color='#bbbbbb',label='random positions (chance)')
ax.set_xticks(xs); ax.set_xticklabels([f"{r.session}\n({int(r.n_nam)} spectra)" for r in ses.itertuples()],fontsize=8); ax.set_ylabel('spectra with a band at the target (%)'); ax.legend(frameon=False,fontsize=8); ax.spines[['top','right']].set_visible(False)
ax.set_title('NAM target bands are not found above chance in any session',loc='left',fontweight='bold',fontsize=9.5)
fig.tight_layout(); fig.savefig(os.path.join(FIG,'N1_detection_vs_chance.png'),dpi=200); plt.close(fig)
# ---- document
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
def fig(path,cap,w=16):
    d.add_picture(path,width=Cm(w)); d.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER; para(cap,italic=True,size=8.5)
STRUCT=os.path.join(REPO,'..','mtp','10_Working_Archive','20-04','N-Acetyl-Muramic-Acid_Conformer3D_medium.png')
para('NAM: Why SERS Detection Has Not Been Achieved',bold=True,size=18)
para('What the data show, what the problem is, and what has to change',size=11)
para('SERS sepsis project. Version 1.0, 27 October 2026. Evidence: SERS sessions of 10-11 Jun, 4 Jul, 12-16 Aug and 7 Oct 2026, the bulk NAM library, and the project reports on NAM detection.',size=9)

d.add_heading('1. Summary',1)
para('NAM is finished on the bulk side but has no SERS result. The bulk powder spectrum is final and validated, and it gives seven target bands. In every SERS session so far, those bands have not been found above chance, although the substrate itself has been shown to enhance a reference dye. The evidence points to the molecule and the way it is presented to the surface, not to the instrument or the substrate.')
table(['Question','Answer'],[
 ['Is there a NAM reference spectrum?','Yes. Bulk powder on glass, 90 %, 30 s, 5 acc, 15 spectra; FINAL and checked on 21 independent spots (24 Sep 2026)'],
 ['Has NAM been detected by SERS?','No. Four sessions between June and October 2026, about 150 NAM spectra in the sessions analysed here plus the 12-16 Aug experiments, show no reproducible band'],
 ['Is the substrate the problem?','Probably not: on 12-16 Aug all eight R6G bands were found on all three substrates (R6G SNR up to 450 on the 2-minute etch). In June and July the R6G check gave weaker numbers (the SNR definitions differ), and in October none was recorded'],
 ['What is the problem?','NAM has no group that binds silver, so it does not stay in the enhanced region; it also scatters weakly and is not resonant at 785 nm. Without a capture layer little NAM reaches the hotspots'],
 ['What has to change?','Add capture chemistry (and decide which one; see Section 5), run R6G and a blank in every session, record the deposition, and avoid the 929 and 955 cm-1 bands where silicon scatters']],[5,13])

d.add_heading('2. What NAM has achieved',1)
bullets(['Bulk reference: 785 nm, 90 % power, 30 s, 5 accumulations, 15 spectra on glass (5 independent spots plus 10 repeats of one spot). The strongest band, 929 cm-1, is 919 +/- 36 counts.',
 'Target bands: 541, 829, 870.5, 929, 955, 1023 and 1127 cm-1 (primary); 457, 487, 1249 and 1589 cm-1 (supporting).',
 'Validation: 21 spectra from 24 Sep 2026 at 60, 70 and 80 % correlate with the reference at r = 0.98 to 0.99 and show all primary bands.',
 'Simulation: DFT of the isolated molecule agrees in position with 7 of the 11 library bands within 10 cm-1, which is not better than chance, so it supports only tentative assignments.',
 'The bulk spectra define what a SERS spectrum of NAM should contain, so the bulk side is not what is holding the project back.'])
if os.path.exists(STRUCT): fig(STRUCT,'Figure 1. NAM (N-acetylmuramic acid, C11H19NO8): an N-acetylated amino sugar carrying a lactyl (carboxylic acid) ether. It has no thiol, no free amine and no aromatic ring.',w=6)

d.add_heading('3. The SERS attempts',1)
para('Four sets of NAM-on-substrate measurements exist. The August experiments were analysed in the earlier project report; the other three were analysed here with the same pipeline and rule as the October session (a peak within 5 cm-1 of the target, at least three pixels wide and at least three times the noise above its surroundings).')
rows=[['12-16 Aug 2026','Ag on black silicon (2, 5 and 10 min etch); 1 mg/mL NAM (3.41 mM)','177 (R6G and NAM)','No band reproducible; highest SNR 2.4 to 3.3, never repeated','All 8 R6G bands on all substrates; SNR 450 (2 min), 31 (5 min), 220 (10 min)']]
for r in ses.itertuples():
    r6=f"1509 cm-1 found in {int(r.r6g_1509_detected)} of {int(r.n_r6g)} spectra, median SNR {r.r6g_median_snr_1509:.1f}" if r.n_r6g>0 else 'Not recorded for this session'
    rows.append([r.session,r.description,int(r.n_nam),f"{r.nam_detect_fraction*100:.1f} % of target positions detected vs {r.nam_chance_mean*100:.1f} % by chance (p = {r.nam_chance_p:.2f}); highest SNR {r.nam_max_snr:.1f}",r6])
table(['Session','Substrate and sample','NAM spectra','NAM result','R6G control'],rows,[2.2,4.2,1.8,5.3,4.5],fs=8)
para('The earlier report (August) is the strongest test: the substrates were shown to be active and NAM still gave nothing. In June and July the R6G band at 1509 cm-1 was found, but at a much lower signal-to-noise ratio than in August, and the SNR values are not directly comparable between reports because the noise was defined differently. In October no R6G was measured, so the activity of that batch is not known. The small July set (7 NAM spectra) cannot support a conclusion on its own.')
fig(os.path.join(FIG,'N1_detection_vs_chance.png'),'Figure 2. Fraction of NAM spectra with a band at the seven target positions, compared with random positions, for the three sessions analysed here.',w=13)
d.add_heading('3.1 The October session in detail',2)
para('The 75 NAM spectra of 7 Oct 2026 (15 to 70 % power, 5 to 15 s) show the silicon band at 518 cm-1 and little else. The most frequent target, 929 cm-1, is found in 14 spectra (19 %), and 955 cm-1 in 10, but both lie on a broad second-order silicon feature near 935 cm-1 that also appears in bare silicon, so they cannot be attributed to NAM. The other five bands are found in 0 to 5 spectra. Peaks outside silicon appear in many spectra but at different positions each time and none repeats. See the report in SERS_Results_Oct2026 for the full analysis.')
if os.path.exists(os.path.join(REPO,'SERS_Results_Oct2026','figures','F8_NAM_best_spectra.png')): fig(os.path.join(REPO,'SERS_Results_Oct2026','figures','F8_NAM_best_spectra.png'),'Figure 3. The five October NAM spectra with the most extra peaks, against the NAM bulk bands (red dotted). No band repeats between spectra.',w=16)

d.add_heading('4. What the problem is',1)
para('Why a dye works and NAM does not on the same substrate:')
table(['What strong SERS needs','R6G','NAM'],[
 ['Resonance near 785 nm','Dye that absorbs near the excitation; extra resonance enhancement','No chromophore; not resonant at 785 nm'],
 ['Large Raman cross-section','Conjugated aromatic system, strong scatterer','Saturated sugar acid; weak scatterer'],
 ['A group that binds silver','Cationic, adsorbs readily to silver','No thiol; the nitrogen is an amide; only the carboxylate and hydroxyls remain'],
 ['Stays within a few nm of the metal','Yes, because it adsorbs','Not controlled: in a dried droplet most NAM is away from the hotspots']],[4,6,8],fs=8.5)
para('Ranked causes, from the project reports and the data:')
table(['Rank','Cause','Evidence','Status'],[
 [1,'NAM does not bind to silver, so it is not concentrated in the enhanced region','R6G adsorbs and gives SNR 450 on the same spots; NAM gives none. SERS enhancement falls off within a few nanometres','Most probable primary cause'],
 [2,'Weak, non-resonant Raman cross-section','Bulk NAM bands need 30 s at 90 % power on glass; SERS must supply a large gain','Strong contributing factor'],
 [3,'Droplet spreading and ring-shaped drying','Black silicon is hydrophilic; the deposit sits at the edge of the wetted area','Contributing; fix with smaller drops or a barrier'],
 [4,'Low concentration','1 mg/mL (3.41 mM) is high by SERS standards; but effective surface concentration depends on adsorption, not bulk','Unlikely primary; not excluded'],
 [5,'Substrate not active','Excluded in August (R6G, all eight bands). Weaker in June and July; not measured in October','Excluded for August only'],
 [6,'Measurement and analysis artefacts','Hot pixels near 1096 and 1190 cm-1 (a false LTA peak was caught); silicon second-order band at 935 cm-1 overlaps NAM 929 and 955; blanks recorded in other sessions','Handled by the 3-pixel rule; blanks still needed'],
 [7,'Missing records','October: concentration, volume, deposition, capture layer and R6G check are not recorded','Limits what can be concluded']],[1,5.3,8,3.7],fs=8)
para('A further point: there is no published SERS spectrum of free NAM in the literature searched by the project, which is consistent with the difficulty being in the molecule and not specific to this substrate.')

d.add_heading('5. What has to change',1)
para('Capture chemistry is the next step in the project plan, but the project documents do not fully agree on which one to use:')
table(['Option','Idea','Point to settle'],[
 ['4-mercaptophenylboronic acid (MPBA)','Thiol binds silver; boronic acid captures cis-diols. Listed as first priority in the August NAM report and the sensor strategy review','The NAM capture-strategy document notes that NAM has no free cis-diol (the ring positions are taken by the N-acetyl and lactyl groups), so boronic acid suits intact bacteria through LPS and teichoic acids better than free NAM'],
 ['Hydrazide at the reducing end','NAM is a reducing sugar; its open-chain aldehyde reacts with hydrazides','Also captures other reducing sugars such as glucose, so selectivity must be tested'],
 ['Cationic surface (for example cysteamine or chitosan)','Attracts the anionic carboxylate of NAM directly','Pre-existing layer would also attract other anions'],
 ['Bare silver first','Silver has some affinity for carboxylate and oxygen or nitrogen lone pairs','Already tried in August without success; a cheap control, not a solution']],[4,7,7],fs=8.5)
para('Whichever chemistry is chosen, the sessions should be set up so that a negative result is informative:')
bullets(['R6G on the same substrate batch in every session, with the 1509 cm-1 band at SNR 10 or more, before any NAM spectrum is taken.',
 'A blank and a solvent-only control recorded in the same session as the NAM spectra, at the same settings.',
 'Bare substrate and functionalised substrate with the same NAM solution and the same settings, side by side.',
 'A concentration series, with concentration changed only after the best substrate is fixed.',
 'A commercial SERS substrate or colloid as an independent check, to separate a substrate problem from a NAM problem.',
 'Targets that avoid silicon: use 541, 829, 870.5, 1023 and 1127 cm-1 and treat 929 and 955 cm-1 with care; the project reports also suggest a Raman-silent tag (alkyne or nitrile) on the capture layer.',
 'Smaller drops or a hydrophobic barrier to keep the sample where it is measured, and a record of volume, solvent and drying.',
 'Several independent substrates per condition, since only one substrate was made per etch time.'])

d.add_heading('6. Gaps in the records',1)
bullets(['7 Oct 2026: NAM concentration, volume, deposition and the capture layer (if any) are not recorded; there was no R6G check.',
 'Laser power at the sample was never measured in mW; only the instrument percentage is known.',
 'HF concentration for the substrate etch is assumed, not verified; no electron microscopy or EDS has been done, and no enhancement factor has been calculated.',
 'No same-session blank for the 2-minute substrate in August, and only one substrate per etch time, so reproducibility between substrates is not shown.',
 'The June set has R6G of a different concentration and etch-label folders whose labels are not explained in the files.'])

d.add_heading('7. Conclusion',1)
para('The reason NAM has no SERS result is that the experiments so far have not given NAM a way to reach the enhanced region, not that the equipment fails. The substrate has been shown to enhance a dye, NAM bands are absent above chance in all sessions, and the molecule has none of the features a silver surface needs to hold it. The next result worth having is a NAM spectrum on a surface that captures it, taken in a session with an R6G check and a blank, with a decision on the capture chemistry made first.')
d.add_heading('8. Files',1)
table(['Item','Location'],[['This report, tables, figure, code','NAM_SERS_Status/'],['October analysis','SERS_Results_Oct2026/'],['Earlier NAM reports (August)','mtp/01_Reports_and_Thesis/NAM_Detection_Experimental_Report_v2.docx; mtp/02_Plans_SOPs_and_Strategy/NAM_Capture_Strategies.docx; Critical_Evaluation_Sensor_Strategy_NAM_LPS_LTA_Aug2026.docx'],['Bulk NAM reference','SERS_Sepsis_Spectral_Library/03_Reference_Spectra/NAM'],['Raw data','10-6-26, 04-07-2026 (repo root); E:\\sukesh\\10-oct-2026']],[6,12])
d.save(os.path.join(OUT,'NAM_SERS_Problem_Analysis.docx')); print('saved')
