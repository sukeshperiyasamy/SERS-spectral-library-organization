"""Builds the Word report from the tables and figures written by sers_oct2026_analysis.py."""
import os,json,pandas as pd
from docx import Document
from docx.shared import Pt,Cm,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.abspath(os.path.join(HERE,'..'))
FIG=os.path.join(OUT,'figures'); TAB=os.path.join(OUT,'tables')
R=json.load(open(os.path.join(TAB,'results.json'))); bands=pd.read_csv(os.path.join(TAB,'target_band_detection.csv')); pat=pd.read_csv(os.path.join(TAB,'lps_session_reproducible_bands.csv')); cond=pd.read_csv(os.path.join(TAB,'per_condition_summary.csv'))
d=Document(); s=d.sections[0]; s.page_width=Cm(21); s.page_height=Cm(29.7)
for a in ('left_margin','right_margin','top_margin','bottom_margin'): setattr(s,a,Cm(1.4))
st=d.styles['Normal']; st.font.name='Arial'; st.font.size=Pt(10); st.element.rPr.rFonts.set(qn('w:eastAsia'),'Arial'); st.paragraph_format.space_after=Pt(4)
for n,sz in (('Heading 1',14),('Heading 2',11.5)):
    h=d.styles[n]; h.font.name='Arial'; h.font.size=Pt(sz); h.font.color.rgb=RGBColor(0,0,0); h.element.rPr.rFonts.set(qn('w:eastAsia'),'Arial')
def shade(c,hx):
    pr=c._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd'); sh.set(qn('w:val'),'clear'); sh.set(qn('w:color'),'auto'); sh.set(qn('w:fill'),hx); pr.append(sh)
def para(t,bold=False,italic=False,size=None):
    p=d.add_paragraph(); r=p.add_run(t); r.bold=bold; r.italic=italic
    if size: r.font.size=Pt(size)
    return p
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
def fig(name,cap,w=17):
    d.add_picture(os.path.join(FIG,name),width=Cm(w)); d.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER; para(cap,italic=True,size=8.5)
hm=lambda s:s[11:16]
gs=R['group_span']; ch=R['chance']
para('SERS Spectra of 7 October 2026 on Etched Silicon: Results for NAM, LPS and LTA',bold=True,size=17)
para('What was measured, what the spectra show, and whether any biomarker was detected',size=11)
para('SERS sepsis project. Version 1.0, 27 October 2026. Data: E:\\sukesh\\10-oct-2026 (124 spectra, B&W Tek i-Raman Plus, 785 nm). These spectra are SERS work on silicon and are not part of the bulk-powder library.',size=9)

d.add_heading('1. Summary',1)
para('No biomarker was detected with confidence in this session. NAM and LTA show nothing that separates them from the substrate blank or from chance. LPS gives one lead worth following up: a reproducible set of ten bands appears on 21 of the 35 LPS spots and on none of the blank or bare-silicon spectra. The set does not meet the project rule for LPS and does not match the bulk LPS spectrum, so it cannot yet be attributed to LPS.')
bullets([f"NAM ({R['n']['NAM']} spectra): none of the seven bulk NAM bands is present in more than 14 spectra (19 %) and none is stronger than in the blank. Detection of the target positions is no better than random positions (p = {ch['NAM']['p']:.2f}). Not detected.",
 f"LPS ({R['n']['LPS']} spectra): the bulk LPS bands (425, 766, 861, 997, 1080 cm-1) and the SERS band at 989 cm-1 are absent. The SERS band at 1330 cm-1 appears in 15 spectra. A set of ten bands (619, 785, 878, 1009, 1238, 1330, 1368, 1455, 1536, 1592 cm-1) is reproducible on 21 spots (pairwise r = {R['repro']['carrying_median_r']:.2f}) and absent from the blank. Lead, not a detection.",
 f"LTA ({R['n']['LTA']} spectra): none of the seven bands is detected above chance (p = {ch['LTA']['p']:.2f}); the phosphate band at 1225-1250 cm-1 appears once. Not detected.",
 'Every spectrum is dominated by the crystalline-silicon band at 518 cm-1. The weak molecular signals sit on top of it.'])
table(['Biomarker','Spectra','Result','Reason in one line'],[
 ['NAM',R['n']['NAM'],'Not detected','No bulk NAM band above the blank or chance'],
 ['LPS',R['n']['LPS'],'Lead, not confirmed','Reproducible band set on 21 spots, absent from blank; 989 cm-1 missing; no match with bulk LPS'],
 ['LTA',R['n']['LTA'],'Not detected','No band above chance; only 9 spectra, 4 of them at 10 % power']],[3,2,3.5,9.5],fills=['FDECEA','FFF4D6','FDECEA'])

d.add_heading('2. What was measured',1)
para('All spectra were recorded on 7 October 2026 with the same instrument used for the bulk library (785 nm). The raw files are in E:\\sukesh\\10-oct-2026 and were only read, never changed. The substrate is etched silicon (operator information). The folder holding the blank and the NAM spectra is named blank-5mlhf-45-di-6mgagno3; the units behind this recipe are not recorded in the files. Sample concentration, volume and the way each sample was applied are Not recorded, and so is a reference-dye check (R6G) for this session.')
rows=[['Substrate blank','blank',5,hm(gs['blank'][0])+' to '+hm(gs['blank'][1]),'15 %, 10 s, 2 acc'],
 ['NAM','nam-1',45,hm(gs['nam-1'][0])+' to '+hm(gs['nam-1'][1]),'15-60 %, 5-10 s, 2-3 acc'],
 ['NAM','nam-2',30,hm(gs['nam-2'][0])+' to '+hm(gs['nam-2'][1]),'60-70 %, 5-15 s, 2-3 acc'],
 ['LPS','lps2',19,hm(gs['lps2'][0])+' to '+hm(gs['lps2'][1]),'50 %, 15 s, 2 acc'],
 ['LPS','lps1',16,hm(gs['lps1'][0])+' to '+hm(gs['lps1'][1]),'30 % 15 s (11 spectra); 50 % 10 s (5)'],
 ['LTA','lta2',9,hm(gs['lta2'][0])+' to '+hm(gs['lta2'][1]),'50 % 10 s (5 spectra); 10 % 10 s (4), 2 acc']]
table(['Sample','Folder','Spectra','Time of day','Settings'],rows,[3,2.5,2,3.5,7])
para('The blank was recorded about five hours before the first LPS spectrum and about eight hours before the LTA spectra. There is no blank taken in the same period as the LPS or LTA spectra, which limits what can be concluded for them. For a second check, 12 bare-silicon spectra from 6 June 2026 (20 %, 10 s, 3 acc) were used.')

d.add_heading('3. How the spectra were analysed',1)
bullets(['Processing: the library pipeline v3 (dark-subtracted signal, repair of the two defective detector pixels, 400-1800 cm-1, despiking, smoothing, baseline removal, noise from the residual).',
 'A band counts as detected in a spectrum when a peak lies within 5 cm-1 of the target, is at least three pixels wide and rises at least three times the noise above its surroundings. The instrument reads the silicon band at 518.0 cm-1 (a fixed offset of about 2 to 3 cm-1 from the true value), which is why a tolerance of 5 cm-1 is used.',
 'Targets: the bulk reference bands of each molecule (NAM 541, 829, 870.5, 929, 955, 1023, 1127; LPS 425, 766, 861, 997, 1080; LTA 802, 861.5, 1092, 1459) plus the SERS rules used in the project: LPS needs 989 and 1330 cm-1; LTA needs a phosphate band (1225-1250 cm-1) and a lipid band (1131 or 1450 cm-1).',
 'Comparison: each band is compared with the substrate blank and with bare silicon (is it absent there?), and its height relative to the silicon band is compared with the blank (Mann-Whitney test).',
 'Chance test: the whole set of target positions is shifted by a random 20 to 80 cm-1, 400 times, to see how often a detection rate as high as the real one occurs by chance.',
 'Reproducibility: the correlation between spectra (560-1800 cm-1, scaled to the silicon band) is used to judge whether a band set is repeatable.'])

d.add_heading('4. What every spectrum contains',1)
para(f"All 124 spectra show the crystalline-silicon band at {R['si_pos']:.1f} cm-1. A second, broad silicon feature near 935 cm-1 appears in about a third of the spectra and also in the bare-silicon spectra, so it is not molecular. This matters for NAM: the 929 and 955 cm-1 targets lie on the edge of that silicon feature, and a detection there cannot be told apart from silicon.")
para('The silicon band height rises with laser power and integration time (table below). No spectrum is saturated: the highest raw count is 8,125, against a limit of 65,535.')
cr=[[r.group,int(r.power_pct),f"{r.integration_s:g}",int(r.accumulations),int(r.n),f"{r.Si_median:.0f}",f"{r.noise_median:.1f}",f"{r.raw_max:.0f}",int(r.with_peaks_outside_Si)] for r in cond.itertuples()]
table(['Group','Power %','Time s','Acc','Spectra','Si 520 height (median, counts)','Noise (median, counts)','Highest raw count','Spectra with peaks outside silicon'],cr,[1.6,1.4,1.3,1.1,1.5,3,2.4,2.4,3.3],fs=8)
fig('F1_session_timeline.png','Figure 1. Height of the silicon band in every spectrum through the session. Groups are coloured; power and integration time changed within some groups.')
para(f"Two detector pixels (near 1096 and 1190 cm-1) give small spikes in every group, including the blank (median spike at the first pixel {R['art']['spk640']['blank']:.0f} counts in the blank, noise about {R['art']['spk640_noise']:.0f} counts). They are instrument artefacts. The pipeline repairs them, and any apparent band at about 1096 or 1190 cm-1 should be ignored; this is also why the earlier apparent 1095 cm-1 LTA peak was not accepted.")

d.add_heading('5. Results by sample',1)
d.add_heading('5.1 NAM',2)
nb=bands[bands.molecule=='NAM']
table(['Band (cm-1)','Detected in NAM spectra (of 75)','Detected in blank (of 5)','Height / Si, NAM (median)','Height / Si, blank (median)','p, NAM greater than blank'],[[r.band,int(r.detected_sample),int(r.detected_blank),f"{r.median_height_over_Si_sample:.3f}",f"{r.median_height_over_Si_blank:.3f}",f"{r.p_greater_than_blank:.2f}"] for r in nb.itertuples()],[2.5,3.5,3,3,3,3])
para(f"The most frequent NAM target is 929 cm-1 (14 spectra, 19 %), followed by 955 cm-1 (10 spectra); both sit at the silicon feature. The remaining bands are found in 0 to 5 spectra at a signal-to-noise ratio of 3 to 4, which is the threshold itself. In every case the NAM spectra are no stronger than the blank relative to the silicon band. The detection rate over all target positions is {ch['NAM']['real']*100:.1f} %, against {ch['NAM']['mean']*100:.1f} % for random positions (p = {ch['NAM']['p']:.2f}). The peaks found outside silicon change from spectrum to spectrum and do not repeat (Figure 2). Not detected.")
para('This agrees with the earlier project finding that NAM gave no SERS signal: NAM has no thiol or other group that binds silver, so it is not expected to stay at the surface without a capture agent.')
fig('F8_NAM_best_spectra.png','Figure 2. The five NAM spectra with the most extra peaks, shown against the substrate blank. Red dotted lines are the NAM bulk bands; no band repeats from one spectrum to the next.')
d.add_heading('5.2 LPS',2)
lb=bands[bands.molecule=='LPS']
table(['Band (cm-1)','Detected in LPS spectra (of 35)','Detected in blank (of 5)','Height / Si, LPS (median)','Height / Si, blank (median)','p, LPS greater than blank'],[[r.band,int(r.detected_sample),int(r.detected_blank),f"{r.median_height_over_Si_sample:.3f}",f"{r.median_height_over_Si_blank:.3f}",f"{r.p_greater_than_blank:.2f}"] for r in lb.itertuples()],[2.5,3.5,3,3,3,3])
para('None of the bulk LPS bands (425, 766, 861, 997, 1080 cm-1) is found, and neither is the SERS band at 989 cm-1. The SERS band at 1330 cm-1 is found in 15 of the 35 spectra and in none of the blank spectra, but its height relative to silicon is not significantly above the blank (p = 0.29) because the blank has little silicon signal to scale against. By the project rule (989 and 1330 cm-1 both present) LPS is therefore not detected.')
para(f"The spectra nevertheless contain more than silicon. Ten bands repeat on {R['n_carry']} of the {R['n_lps']} LPS spots (table below, Figures 3 to 5). Their median spectrum-to-spectrum correlation is {R['repro']['carrying_median_r']:.2f}, against {R['repro']['other_LPS_median_r']:.2f} for the other LPS spots, {R['repro']['blank_median_r']:.2f} for the blank and {R['repro']['NAM_median_r']:.2f} for NAM. The spots that carry the set have a weaker silicon band (median {R['si_carry']:.0f} counts against {R['si_nocarry']:.0f} on the others), as expected if a surface layer covers the silicon. The set is absent from the blank (0 of 5) and from bare silicon (0 of 12), and it is rare in the NAM and LTA spectra.")
prow=[[int(round(r.mean_position)),f"{r.sd_position:.1f}",f"{r.fraction_carrying*100:.0f} %",f"{r.fraction_other_LPS*100:.0f} %",f"{r.fraction_blank*100:.0f} %",f"{r.fraction_bare_Si*100:.0f} %",f"{r.fraction_NAM*100:.0f} %",f"{r.median_snr_carrying:.1f}",r.literature] for r in pat.itertuples()]
table(['Band (cm-1)','SD of position','In the 21 spots with the set','In the other 14 LPS spots','Blank','Bare Si','NAM','Median SNR','Nearest literature band'],prow,[1.5,1.4,2,2,1.2,1.2,1.2,1.5,5.6],fs=8)
fig('F3_LPS_individual_spectra.png','Figure 3. LPS session: spectra with the reproducible band set (dotted lines), two spots without it, and the substrate blank. Spectra are scaled to the silicon band and offset.')
fig('F6_LPS_session_band_set.png','Figure 4. How often each band of the set appears in each group of spectra.')
para(f"What this does and does not show. The strongest band, at 1455 cm-1 (median SNR {pat.median_snr_carrying.max():.0f}), lies 5 cm-1 above the 1450 cm-1 CH2/CH3 deformation listed for SERS of LPS, and the 1330 cm-1 band matches the 1330/1333 cm-1 band in the same lists. The 1009 cm-1 band is 6 to 21 cm-1 from the 988 and 1003 cm-1 bands in the literature, and the other six bands have no match in the checked LPS list. The mean spectrum of the spots with the set correlates with the bulk LPS reference at r = {R['sim']['LPS']:.2f}, which is no better than its correlation with the bulk LTA reference ({R['sim']['LTA']:.2f}) and bulk NAM reference ({R['sim']['NAM']:.2f}). The pattern is therefore consistent with an organic layer containing CH2 and CH3 groups on the silicon, and LPS is one possible source, but it is not an identification.")
para('Two further points limit the interpretation. First, there is no blank, solvent-only control or LPS-free spot taken in the same period, so contamination from the sample preparation or handling cannot be excluded. Second, the bulk LPS spectrum on glass and a SERS spectrum can differ in which bands are enhanced, so the lack of overlap with the bulk bands is not by itself proof against LPS.')
fig('F7_LPS_band_zooms.png','Figure 5. Close-up of four bands of the set in the spots that carry it (thin lines, mean in red) and in the blank (grey).')
d.add_heading('5.3 LTA',2)
tb=bands[bands.molecule=='LTA']
table(['Band (cm-1)','Detected in LTA spectra (of 9)','Detected in blank (of 5)','Height / Si, LTA (median)','Height / Si, blank (median)','p, LTA greater than blank'],[[r.band,int(r.detected_sample),int(r.detected_blank),f"{r.median_height_over_Si_sample:.3f}",f"{r.median_height_over_Si_blank:.3f}",f"{r.p_greater_than_blank:.2f}"] for r in tb.itertuples()],[2.5,3.5,3,3,3,3])
para(f"None of the LTA bands is found above chance; the detection rate over all target positions is {ch['LTA']['real']*100:.1f} % against {ch['LTA']['mean']*100:.1f} % for random positions (p = {ch['LTA']['p']:.2f}). The phosphate region (1225-1250 cm-1) gives one detection in nine spectra, and the 1092 cm-1 position none. Only five spectra were taken at 50 % power; the four at 10 % power have a silicon band of only about 250 to 340 counts and very little sensitivity. Not detected, with the caveat that nine spectra and no matching blank are a weak test.")
fig('F2_mean_spectra_vs_blank.png','Figure 6. Mean spectrum of each sample, scaled to the silicon band, with the substrate blank and bare silicon. Red dotted lines are the target bands. Only the LPS spots with the band set show extra bands.')
fig('F4_target_band_detection.png','Figure 7. Fraction of spectra in which each target band is detected, for the sample and the blank.')
fig('F5_chance_test.png','Figure 8. Detection rate over all target positions (coloured line) compared with 400 random shifts of the positions (grey). None of the three exceeds chance.')

d.add_heading('6. Are there any good results?',1)
table(['Biomarker','Outcome','What supports it','What is missing'],[
 ['NAM','No detection',f"75 spectra, 15-70 % power; no bulk band above blank or chance (p = {ch['NAM']['p']:.2f})",'A capture agent for NAM on the silver surface (proposed in the project notes); a same-session blank'],
 ['LPS','Lead worth repeating','Ten-band set reproducible on 21 of 35 spots, absent from blank and bare Si, weakens the silicon band','Same-period blank and solvent control; 989 cm-1 band; match to bulk or reference LPS; repeat on fresh substrate'],
 ['LTA','No detection','9 spectra; no band above chance','More spectra at 50 % power or higher, with a same-session blank; the phosphate and lipid bands together']],[2.2,3.3,6,6],fills=[None,None,None])
para('In short, the session does not yet show a detected biomarker, and the LPS result is the one worth building on.')

d.add_heading('7. Limitations and next steps',1)
bullets(['Blank: one blank of 5 spectra, recorded hours before the LPS and LTA spectra. A blank at the start and end of each sample set would make the comparison fair.',
 'Sample records: concentration, volume, solvent, deposition method and the substrate recipe units are Not recorded; they are needed to judge the LPS result and to repeat it.',
 'Reference dye: no R6G check for this session, so substrate sensitivity on the day is unknown.',
 'Sample size: LTA has 9 spectra and the 10 % power group is too weak to test anything; LPS spots without the band set (14 of 35) may simply have been off the sample.',
 'LPS follow-up: repeat on a fresh substrate with a solvent-only control prepared in the same way, record the spot position, and keep the settings of lps2 (50 %, 15 s, 2 acc). Measuring the bulk LPS powder on the same type of silicon would show directly which bands the silicon-supported LPS gives.',
 'Wording: all statements here describe what the spectra are consistent with; none identifies a compound.'])

d.add_heading('8. Files',1)
table(['Item','Location'],[['Raw spectra (read only)','E:\\sukesh\\10-oct-2026 (not copied)'],['Per-spectrum summary, band detection, LPS band set, per-condition summary, results.json','SERS_Results_Oct2026/tables'],['Figures','SERS_Results_Oct2026/figures'],['Code','SERS_Results_Oct2026/code (sers_oct2026_analysis.py, build_report.py)']],[6,12])
d.save(os.path.join(OUT,'SERS_Oct2026_Results_NAM_LPS_LTA.docx')); print('saved')
