# Rewrites the LPS parts of three reports with the whole-molecule lipid A model (lps output simulation, 27-28 Oct 2026).
# Edits the existing .docx files in place (builder scripts of the originals are lost); makes a backup copy once in ../_backup_before_lipidA
import os,re,copy,json,shutil
from docx import Document
from docx.shared import Pt,Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph
from docx.table import Table
L=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..')); REP=os.path.join(L,'09_Reports'); FIG=os.path.join(L,'04_Figures','LipidA_Model_20261028')
BK=os.path.join(L,'_backup_before_lipidA'); os.makedirs(BK,exist_ok=True)
F={'dft':'DFT_vs_Experimental_Comparison_NAM_LPS_LTA.docx','sim':'Simulation_Methods_and_Spectra_NAM_LPS_LTA.docx','lps':'LPS_Findings_and_Parameters_Report.docx'}
for f in F.values():
    if not os.path.exists(os.path.join(BK,f)): shutil.copy(os.path.join(REP,f),os.path.join(BK,f))
R=json.load(open(os.path.join(L,'05_Tables','LipidA_vs_LPS_results.json')))
B=R['bands']; FB=R['frag_bands']
# ---------------------------------------------------------------- helpers
def settext(p,text):
    rs=p.runs
    if rs:
        rs[0].text=text
        for r in rs[1:]: r._r.getparent().remove(r._r)
    else: p.add_run(text)
def rep(p,old,new):
    for r in p.runs:
        if old in r.text: r.text=r.text.replace(old,new); return True
    if old in p.text: settext(p,p.text.replace(old,new)); return True
    return False
def find_p(doc,start,style=None):
    for p in doc.paragraphs:
        if p.text.strip().startswith(start) and (style is None or p.style.name.startswith(style)): return p
    raise KeyError(start)
def cellset(c,text):
    p=c.paragraphs[0]
    if p.runs: settext(p,text)
    else: p.add_run(text)
    for extra in c.paragraphs[1:]: extra._p.getparent().remove(extra._p)
def addrow(t,vals):
    new=copy.deepcopy(t.rows[-1]._tr); t._tbl.append(new); row=t.rows[-1]
    for c,v in zip(row.cells,vals): cellset(c,v)
    return row
def shade(c,hx):
    pr=c._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd'); sh.set(qn('w:val'),'clear'); sh.set(qn('w:color'),'auto'); sh.set(qn('w:fill'),hx); pr.append(sh)
class Ins:
    """append new blocks after an anchor element (paragraph or table)"""
    def __init__(s,doc,anchor): s.d=doc; s.cur=anchor if not hasattr(anchor,'_p') else anchor._p
    def _put(s,el): s.cur.addnext(el); s.cur=el
    def h(s,text,lvl=2): p=s.d.add_heading(text,lvl); s._put(p._p)
    def p(s,text,italic=False,size=None):
        p=s.d.add_paragraph(); r=p.add_run(text); r.italic=italic
        if size: r.font.size=Pt(size)
        s._put(p._p); return p
    def b(s,text): p=s.d.add_paragraph(text,style='List Bullet'); s._put(p._p)
    def fig(s,path,cap,w=17):
        s.d.add_picture(path,width=Cm(w)); p=s.d.paragraphs[-1]; p.alignment=WD_ALIGN_PARAGRAPH.CENTER; s._put(p._p)
        c=s.d.add_paragraph(); r=c.add_run(cap); r.italic=True; r.font.size=Pt(8.5); s._put(c._p)
    def t(s,head,rows,widths,fs=8):
        t=s.d.add_table(rows=1,cols=len(head)); t.style='Table Grid'
        for i,x in enumerate(head):
            c=t.rows[0].cells[i]; c.text=''; r=c.paragraphs[0].add_run(x); r.bold=True; r.font.size=Pt(fs); shade(c,'D9D9D9')
        for row in rows:
            cs=t.add_row().cells
            for i,x in enumerate(row): cs[i].text=''; cs[i].paragraphs[0].add_run(str(x)).font.size=Pt(fs)
        for row in t.rows:
            for i,w in enumerate(widths): row.cells[i].width=Cm(w)
        s._put(t._tbl); sp=s.d.add_paragraph(); s._put(sp._p)
def remove_between(doc,h1,h2,keep=()):
    """remove body elements after paragraph h1 up to (not including) h2; return list of kept elements"""
    body=doc.element.body; els=list(body.iterchildren()); a=els.index(h1._p); b=els.index(h2._p); kept=[]
    for el in els[a+1:b]:
        if id(el) in keep: kept.append(el); continue
        body.remove(el)
    return kept
def renumber(doc):
    """renumber 'Figure N.' captions in order and update 'Figure N' mentions in running text"""
    caps=[p for p in doc.paragraphs if re.match(r'^Figure \d+\.',p.text)]
    old=[int(re.match(r'^Figure (\d+)\.',p.text).group(1)) for p in caps]; mp={}
    for i,p in enumerate(caps,1): mp[(old[i-1],i)]=1
    # captions: assign new numbers; mentions: only for old numbers that are unique in the original sequence
    for i,p in enumerate(caps,1):
        o=old[i-1]; rep(p,f'Figure {o}.',f'Figure {i}.')
    return old
def lipid_numbers():
    o={}
    for t in('t5','t10','t18'): o[t]=R[t]
    return o
a5=B[0]
def tb(d,*heads):
    for t in d.tables:
        if [c.text for c in t.rows[0].cells][:len(heads)]==list(heads): return t
    raise KeyError(heads)
# ================================================================= DFT comparison
def dft():
    d=Document(os.path.join(REP,F['dft']))
    rep(d.paragraphs[2],'Version 1.1, 27 October 2026','Version 1.2, 28 October 2026')
    rep(d.paragraphs[2],'(listed in Section 9)','(listed in Section 9); LPS whole-molecule model: SERS_Sepsis_Spectral_Library/08_Methodology/simulation/LPS_LipidA_Model_20261028 (Gaussian 16W, 27-28 Oct 2026)')
    settext(d.paragraphs[3],"The simulations reproduce the position of many individual bands, and the agreement is best for NAM, the only small molecule calculated as a whole. LPS now has two calculations: five separate fragments, and a whole-molecule model of Kdo2-lipid A with shortened acyl chains (201 atoms). The whole-molecule model puts all five library LPS bands within 2.4 cm-1 of a calculated mode (mean difference 1.2 cm-1, against 3.5 cm-1 for the fragments), and it has a strong calculated mode at 422 and 862 cm-1 where the fragments had very weak ones. The position agreement is, however, still no better than random chance, because the model has 354 modes between 400 and 1800 cm-1 and almost any band has a mode close to it. The overall spectral shapes do not match (correlation 0.1 or less for all three molecules; -0.01 for the lipid A model). The DFT results can support tentative assignments of individual bands, but they cannot be used to confirm identity, and several of the strongest experimental bands remain unexplained: NAM 829 and 955 cm-1, the assignment of LPS 425 cm-1, and LTA 802 cm-1.")
    # --- summary table
    t=tb(d,'Molecule','What was simulated')
    for r in t.rows:
        if r.cells[0].text=='LPS':
            cellset(r.cells[0],'LPS (5 fragments)'); cellset(r.cells[1],'Five separate fragments, not whole LPS')
    r=addrow(t,['LPS (whole-molecule model)','Kdo2-lipid A with shortened chains, 201 atoms, charge -4, B3LYP/3-21G, gas phase','5','5 / 5 / 5','1.2','4.6 (p = 0.57)','-0.01','Positions agree; not above chance; shape no'])
    # --- what was simulated table
    t=tb(d,'Item','NAM','LPS','LTA'); add={'What was calculated':' Also: whole-molecule model of Kdo2-lipid A (PubChem CID 5771770) with the six acyl chains shortened to C3-C4: C60H98N2O39P2, 201 atoms, charge -4.',
      'Why fragments':'. For the whole-molecule model the chains were cut because full Kdo2-lipid A (355 atoms) was too large for this PC at a higher level; the core sugars beyond Kdo and the O-antigen are not in it.',
      'Method':' Whole-molecule model: Gaussian 16W Rev C.01, PM6 pre-optimisation then B3LYP/3-21G opt freq=raman; 109 optimisation steps; 597 modes, no imaginary frequency.',
      'Environment':'; whole-molecule model: gas phase, no counter-ions',
      'Frequency scaling':'; whole-molecule model 0.965 (typical B3LYP value, not fitted for 3-21G)',
      'Modes in 400-1800 cm-1':'; whole-molecule model 354',
      'Modes per 100 cm-1':'; whole-molecule model 25.3'}
    for r in t.rows:
        k=r.cells[0].text
        if k in add: cellset(r.cells[2],r.cells[2].text+add[k])
    p13=find_p(d,'A calculation on a single small fragment')
    settext(p13,"A calculation on a single small fragment cannot reproduce a polymer. LPS has phosphorylated, acylated and branched sugars; LTA has a charged phosphodiester backbone. The five LPS fragments and the three LTA fragments contain none of the linkages between units, so bands that come from those linkages cannot appear in them. The whole-molecule LPS model does contain the glycosidic bond between the two glucosamines, the Kdo links, both phosphate esters and both amide links of the lipid A backbone, but not the long acyl chains, the outer core sugars or the O-antigen, so it is still a part of LPS and not the whole.")
    # --- LPS section: rebuild
    h5=find_p(d,'5. LPS','Heading 1'); h6=find_p(d,'6. LTA','Heading 1')
    els=list(d.element.body.iterchildren()); a,b=els.index(h5._p),els.index(h6._p)
    keep=[]
    for el in els[a+1:b]:
        if el.xpath('.//w:drawing'): keep.append(el); keep.append(el.getnext()); break      # old fragment overlay + caption
    for el in els[a+1:b]:
        if el not in keep: d.element.body.remove(el)
    frag_img,frag_cap=keep
    I=Ins(d,h5)
    I.h('5.1 What was calculated')
    I.p('Two calculations are compared with the same five library bands (the primary and supporting bands of the LPS reference, 60 %, 40 s, 5 acc, n = 10).')
    I.t(['','Five fragments','Whole-molecule model'],[
      ['What','KDO, D-glucosamine, heptose, myristic acid, phosphoric acid, each on its own','Kdo2-lipid A (E. coli, PubChem CID 5771770) with the six acyl chains shortened: 2 glucosamines, 2 Kdo, 2 phosphates, 2 amides, all in one molecule'],
      ['Atoms and charge','Not recorded for the fragments','201 atoms, C60H98N2O39P2, charge -4 (both Kdo carboxylates and both phosphates ionised), no counter-ions'],
      ['Level','B3LYP/6-31G(d), gas phase, scale 0.9613','PM6 then B3LYP/3-21G, gas phase, scale 0.965; Gaussian 16W Rev C.01'],
      ['Modes in 400-1800 cm-1','150 (10.7 per 100 cm-1)','354 (25.3 per 100 cm-1)'],
      ['Result file','dft_candidates_all.csv (mtp)','lipidA_raman_act.csv (lps output simulation)']],[3.4,6.6,8])
    I.h('5.2 Result')
    I.p(f"Whole-molecule model: all five bands have a calculated mode within {max(abs(x['delta']) for x in B):.1f} cm-1 (four of them within 1.1 cm-1); mean absolute difference {R['mae']:.1f} cm-1. The five fragments gave 4 of 5 within 5 cm-1 and a mean difference of {R['frag_mae']:.1f} cm-1; the 766 cm-1 band was 12.4 cm-1 away. Against random shifts of the calculated modes the whole-molecule model gets 5 of 5 within 5 cm-1 where chance gives {R['t5']['decoy_mean']:.1f} (p = {R['t5']['p']:.2f}), so the positions are not evidence of agreement: with 354 modes there is nearly always one close. The whole-spectrum correlation is {R['r_whole']:.2f}. The strongest calculated mode is at 1516 cm-1, which is weak in the experiment (0.05 of the 425 band), and the experimental 425 cm-1 band, the strongest in the spectrum, falls on a calculated mode of moderate strength.")
    I.fig(os.path.join(FIG,'LPS_Exp_vs_LipidA_Model.png'),'Figure 2. LPS. Top: library experimental reference (10 spectra). Bottom: whole-molecule model (shortened Kdo2-lipid A), calculated modes (blue sticks) and broadened spectrum. Dashed lines mark the experimental bands; all five are within 10 cm-1 of a calculated mode (green).')
    I.h('5.3 Band-by-band')
    rows=[]
    why={424.8:'Calculated mode at 422.4, relative activity 0.34. The fragments gave only a weak phosphoric-acid mode (0.06). The motion of the 422 mode was not analysed, so the band stays unassigned.',
         765.5:'Mode at 764.4, weak (0.08). The fragments were 12.4 cm-1 away. Position now agrees; the strength does not (the experimental band is among the stronger bands).',
         861.1:'Mode at 862.0, relative activity 0.37 (fragments: 0.02). Consistent with the sugar-ring region of the two glucosamines and Kdo.',
         995.8:'Nearest mode 996.2 is weak (0.08), but the strongest mode of the 900-1000 region lies at 994.7 (relative activity 0.72), 1 cm-1 away, so the band has a strong calculated counterpart.',
         1080.5:'Mode at 1079.5, activity 0.12 (fragments: 0.05). The band is broad and about 14 % glass-affected, so a 1 cm-1 agreement is not meaningful.'}
    for b,f in zip(B,FB):
        rows.append([f"{b['exp']:.1f}",b['role'],f"{b['calc']:.1f}",f"{b['delta']:+.1f}",f"{b['act']:.2f}",f"{f['calc']:.1f}",f"{f['delta']:+.1f}",f"{f['act']:.2f} ({f['label'].replace('_',' ').lower()})",'MATCH' ,why[round(b['exp'],1)]])
    I.t(['Exp. band (cm-1)','Class','Lipid A model: nearest mode','Exp - calc','Rel. activity','Fragments: nearest mode','Exp - calc','Rel. activity (fragment)','Verdict (model)','Why'],rows,[1.3,1.4,1.5,1.1,1.1,1.5,1.1,2.3,1.3,5.4],fs=7)
    I.h('5.4 What is happening and why')
    for x in ["Positions: the whole-molecule model is closer than the fragments (mean difference 1.2 against 3.5 cm-1) and explains the 766 cm-1 band that the fragments missed by 12 cm-1. Having the glycosidic, phosphate-ester and Kdo links in one molecule moves modes to where they are in the sample.",
      "Strength: at 425 and 861 cm-1 the model has modes of 0.34 and 0.37 of the maximum activity, against 0.06 and 0.02 for the fragments. These two bands are therefore no longer calculated as almost invisible. The model still puts its largest intensity in places where the measured LPS spectrum is weak: 1516 cm-1 (0.05 of the 425 band), 745 cm-1 (0.18) and 699 cm-1 (0.08).",
      "Not better than chance: a mode list this dense (25 per 100 cm-1) matches almost any set of five bands. Random shifts of 15 to 70 cm-1 give 4.4 to 4.7 matches of 5, so 5 of 5 is p = 0.47 to 0.66. Using only the stronger modes (activity 0.15 or more, 190 modes) gives 4 of 5 within 5 cm-1, chance 3.6 (p = 0.61). The fragments gave p = 0.32 to 0.68. Neither calculation can claim an agreement beyond chance.",
      f"Shape: the whole-spectrum correlation is {R['r_whole']:.2f}, compared with {R['frag_r_equal']:.2f} for the equal-weight fragment composite. The cut chains remove most of the CH2 and CH3 bands, the 1516 cm-1 mode (probably an amide mode that the small basis set overstates; not verified) dominates the model, and the three artefact peaks at 2420 to 2750 cm-1 lie outside the compared range.",
      f"Combining both: fitting the whole-molecule spectrum together with the five fragments (non-negative least squares) gives r = {R['nnls_all']['r']:.2f}, with a weight of {100*R['nnls_all']['weights']['Lipid A model']:.0f} % for the lipid A model; the five fragments alone give {R['nnls_frag_r']:.2f}. The model does not improve the fit, and these fitted weights are not the composition of LPS.",
      "Literature SERS bands of endotoxin (850, 989, 1131 and 1330 cm-1, from the thesis used for the model): the model has modes at 854, 989 to 995, 1137 (weak) and 1329 (and 1316), as reported in the model methods. These bands are SERS bands and are not all present as bands of the bulk spectrum, so this is a check on the model, not on the library spectrum."]: I.b(x)
    I.h('5.5 Whole-molecule model against the five fragments')
    I.p('The whole-molecule model is the better of the two calculations for band positions and for the strength of the 425 and 861 cm-1 modes. It is not better for the overall shape, and neither is better than chance for positions. The fragments remain useful for the regions the shortened model leaves out (long acyl chains, core sugars).')
    I.fig(os.path.join(FIG,'LPS_Whole_Molecule_vs_Fragments.png'),'Figure 3. LPS: whole-molecule model against the five fragments. Left: difference between each library band and the nearest calculated mode. Middle: calculated relative activity of that mode. Right: whole-spectrum correlation with the library reference.',w=17)
    frag_img.getparent().remove(frag_img); I._put(frag_img)
    I._put(frag_cap); cap=Paragraph(frag_cap,d._body); settext(cap,'Figure 4. LPS, fragment calculation. Top: library experimental reference. Bottom: scaled DFT modes of five fragments (coloured by fragment) and their equal-weight composite.')
    I.h('5.6 Likely reasons for the differences')
    for x in ["Shortened chains and missing core. The model has C3-C4 chains instead of C12-C14 and no heptose or O-antigen, so the lipid, core and outer-chain bands of real LPS are not represented. This is the largest limit of the whole-molecule model.",
      "Low level of theory. B3LYP/3-21G has no polarisation or diffuse functions; positions are approximate, intensities of charged groups are distorted and gas-phase hydrogen bonds to the charged groups produce artefact peaks at 2420 to 2750 cm-1. The 0.965 scale factor was not fitted for this level.",
      "Gas phase and charge -4 without counter-ions. The sample is a salt (Na+, Ca2+, Mg2+ counter-ions) in a powder; both change band positions and intensities.",
      "One conformer. A single low-energy shape of a flexible molecule was calculated; the stereocentres left open by PubChem were set by the embedding.",
      "Dense mode list. With 354 modes the position test cannot separate a real agreement from chance (Section 7).",
      "Different experimental reference from the older fragment work, as described in the earlier version of this document: the fragment results were first compared with an older LPS measurement; both models here use the library reference (60 %, 40 s, 5 acc)."]: I.b(x)
    # --- LTA section figure numbers and chance test table
    t=tb(d,'Molecule','Tolerance (cm-1)')
    for r in t.rows:
        if r.cells[0].text=='LPS': cellset(r.cells[0],'LPS (5 fragments)')
    # insert whole-model rows after the last LPS-fragment row
    lastlps=[r for r in t.rows if r.cells[0].text=='LPS (5 fragments)'][-1]._tr
    for tol,k in ((5,'t5'),(10,'t10'),(18,'t18')):
        v=R[k]; new=copy.deepcopy(lastlps); lastlps.addnext(new); lastlps=new
        row=[r for r in t.rows if r._tr is new][0]
        for c,val in zip(row.cells,['LPS (whole model)',str(tol),f"{v['real']} of 5",f"{v['decoy_mean']:.1f} +/- {v['decoy_sd']:.1f}",f"{v['p']:.2f}",f"{v['real_strong']} of 5 (chance {v['decoy_strong_mean']:.1f}, p = {v['p_strong']:.2f})"]): cellset(c,val)
    # --- conclusion table
    t=tb(d,'Question','NAM','LPS','LTA')
    new={'Do individual band positions agree?':'Yes: all 5 within 2.4 cm-1 (whole-molecule model); fragments: 4 of 5 within 5 cm-1, weak calculated activity',
         'Is that better than chance?':'No (p = 0.57 whole model; p = 0.68 fragments)',
         'Does the overall spectral shape agree?':'No (whole model r = -0.01; fragments 0.14, fitted 0.40)',
         'Are the strongest experimental bands explained?':'Partly: the model has modes of moderate strength at 422 and 862 for the 425 and 861 bands, but its strongest mode (1516) is weak in the experiment; 425 is not assigned to a group',
         'What can be claimed?':'Position consistency with sugar, phosphate and amide modes of lipid A; no firm assignment gained; 425 cm-1 stays unassigned',
         'Overall':'POSITIONS AGREE, not above chance; shape not matched; not demonstrated'}
    for r in t.rows:
        if r.cells[0].text in new: cellset(r.cells[2],new[r.cells[0].text])
    # --- 8.1 and sources and limitations
    p=find_p(d,'LPS: use larger models')
    settext(p,"LPS: the shortened Kdo2-lipid A is a first whole-molecule result. Next steps: rerun at B3LYP/6-31G(d) or B3LYP/6-31+G(d,p) with water (planned, days of run time), starting from the optimised geometry; keep longer acyl chains and add the core sugars beyond Kdo; add Na+ or Ca2+ counter-ions; look at which atoms move in the 422 and 862 cm-1 modes; and check the 1516 cm-1 mode against a larger basis set.")
    t=tb(d,'Item','File used')
    r=addrow(t,['LPS whole-molecule model (lipid A, 354 modes in range)','SERS_Sepsis_Spectral_Library\\08_Methodology\\simulation\\LPS_LipidA_Model_20261028 (copy of C:\\Users\\sukes\\Downloads\\sukesh\\lps output simulation): lipidA_raman_act.csv, lipidA_short.gjf, lipidA_short.out (Gaussian log), Lipid_A_Raman_Methods.md'])
    addrow(t,['Whole-molecule comparison results and code','05_Tables\\LipidA_vs_LPS_results.json; 08_Methodology\\code\\lipidA_compare.py, lipidA_figures.py, update_docs_lipidA.py; figures in 04_Figures\\LipidA_Model_20261028'])
    lim=find_p(d,'LPS and LTA calculated modes were taken')
    settext(lim,"LPS fragment and LTA calculated modes were taken from the exported files as supplied. The Gaussian logs for the five LPS fragments and for D-alanine and GlcNAc were not found, so their charge states and atom counts are Not recorded; the levels of theory are as documented. The LPS whole-molecule model has its full Gaussian log. Full simulation details are in Simulation_Methods_and_Spectra_NAM_LPS_LTA.docx.")
    anchor=find_p(d,'Only primary and supporting library bands')
    I=Ins(d,anchor)
    I.b('The LPS whole-molecule model is a shortened piece of lipid A at a low level (B3LYP/3-21G, gas phase). Its strong 1516 cm-1 mode is not verified, and the motions behind the 422 and 862 cm-1 modes were not analysed.')
    I.b('The LTA comparison in Section 6 still uses the preliminary April 2026 LTA reference (4 spectra). The new LTA reference of 28 Oct 2026 (17 spots) has not been compared with the LTA fragment calculations.')
    # figure renumbering: Figure 5,6 -> 6,7 ; LTA figure 3 -> 5
    for p in d.paragraphs:
        if re.match(r'^Figure 3\. LTA',p.text): rep(p,'Figure 3.','Figure 5.')
        elif re.match(r'^Figure 4\. Grey',p.text): rep(p,'Figure 4.','Figure 6.'); rep(p,'real DFT.','real DFT. LPS is the five-fragment calculation; the whole-molecule model is in the table below.')
        elif re.match(r'^Figure 5\. Difference',p.text): rep(p,'Figure 5.','Figure 7.')
        elif 'Figure 4 shows that it does not' in p.text: rep(p,'Figure 4 shows that it does not, for any of the three molecules.','Figure 6 and the table below show that it does not, for any of the three molecules, and the same holds for the LPS whole-molecule model.')
    d.save(os.path.join(REP,F['dft']))
# ================================================================= Simulation methods
def sim():
    d=Document(os.path.join(REP,F['sim']))
    rep(d.paragraphs[1],'the reasons for the fragment approach','the reasons for the fragment and shortened-molecule approaches')
    rep(d.paragraphs[2],'Version 1.0, 27 October 2026','Version 1.1, 28 October 2026')
    settext(d.paragraphs[3],"This document records the simulation work only; the comparison with the measured spectra is in a separate document. NAM was calculated as a whole molecule. For LPS there are two calculations: five separate fragments, and a model of the Kdo2-lipid A backbone with shortened acyl chains (201 atoms, run 27-28 Oct 2026). LTA was simulated as three separate fragments. The intact LPS and LTA molecules are too large and variable to calculate (Section 7), so no whole-LPS or whole-LTA spectrum was simulated. Settings that are not written in the available files are given as Not recorded.")
    t=d.tables[0]; add={'What was simulated':' Also: one model of Kdo2-lipid A with shortened chains (2 glucosamines, 2 Kdo, 2 phosphates, 2 amides)',
      'Number of atoms per calculation':'. Lipid A model: 201 (C60H98N2O39P2, charge -4)',
      'Software':'. Lipid A model: Gaussian 16W Rev C.01',
      'Method and basis set':'. Lipid A model: PM6 pre-optimisation, then B3LYP / 3-21G',
      'Environment':'. Lipid A model: gas phase, no counter-ions',
      'Frequency scale factor':'. Lipid A model: 0.965 (not fitted for 3-21G)',
      'Imaginary frequencies':'. Lipid A model: none (597 modes; true minimum)',
      'Spectra obtained':'. Lipid A model: 597 modes (354 in 400-1800 cm-1), broadened 785 nm spectrum 200-3300 cm-1',
      'Why this approach':'. Lipid A model: the largest piece of LPS that could be run on this PC with a whole-molecule calculation'}
    for r in t.rows:
        k=r.cells[0].text
        if k in add: cellset(r.cells[2],r.cells[2].text+add[k])
    t=d.tables[1]
    for r in t.rows:
        if r.cells[0].text=='Gaussian 16':
            cellset(r.cells[1],r.cells[1].text+' and the LPS lipid A model'); cellset(r.cells[2],r.cells[2].text+'; lipid A model: Gaussian 16W (Windows) Revision C.01, C:\\G16W\\g16.exe')
        if r.cells[0].text.startswith('RDKit'):
            cellset(r.cells[1],'Building the shortened Kdo2-lipid A model (version 2026.03.3: SMILES, chain shortening, ionisation, 300 conformers, MMFF) and the earlier lipid A proxy; writing Gaussian and ORCA inputs')
    t=d.tables[2]; addrow(t,['LPS shortened Kdo2-lipid A, Gaussian 16W (PM6, then B3LYP/3-21G)','28 shared','54 GB','PM6 about 55 min; 109 optimisation steps of about 8-9 min; frequencies 4 h 42 min (finished 28 Oct 2026, 08:57)'])
    # new subsection after 5.4 (last LPS bullet) -> before heading 6
    anchor=find_p(d,'Earlier LPS documentation reported weights')
    h=find_p(d,'5. LPS','Heading 1'); settext(h,'5. LPS: fragment simulation and whole-molecule model')
    I=Ins(d,anchor)
    I.h('5.5 Whole-molecule model: Kdo2-lipid A with shortened chains')
    I.p('Because fragments leave out the links between the parts of LPS, a model with the links in place was added. The full Kdo2-lipid A (355 atoms) was too large for a B3LYP/6-31+G(d,p) Raman calculation on this PC, so the acyl chains were shortened and the backbone kept complete. The intact LPS (core oligosaccharide and O-antigen of the O111 serotype) is not in the model.')
    I.t(['Item','Detail'],[
      ['Structure source','PubChem CID 5771770 (Kdo2-lipid A, E. coli), 2D SDF; formula C110H202N2O39P2, 355 atoms, neutral, as expected (found through the GlyCosmos listing, LIPID MAPS LMSL02000001). CID 25244473 has a different formula and was not used.'],
      ['Shortening','C14 acyl chains to butyryl, the C11 tails of the 3-acyloxy chains to propyl, the C12 acyl chain to butyryl. Kept: 2 glucosamines, 2 Kdo, 2 phosphates, 2 amides and the stereo tags given by PubChem.'],
      ['Charge state','Ionised for water at near-neutral pH: both Kdo carboxylates as COO-, both phosphate monoesters with one negative charge each; net charge -4; no counter-ions.'],
      ['Result','C60H98N2O39P2 (4-), 201 atoms'],
      ['3D structure','300 conformers by ETKDGv3 (random seed 7), each optimised with MMFF; the lowest (conformer 110, MMFF energy 139.7 kcal/mol) was the start geometry. PubChem leaves a few ring stereocentres open; the embedding set them, so this is one reasonable structure and not necessarily the lowest-energy one.'],
      ['Software','Gaussian 16W Revision C.01 (C:\\G16W\\g16.exe); 28 processors and 54 GB memory (i7-14700, 64 GB)'],
      ['Job 1','# opt=loose pm6, gas phase, charge -4, singlet (about 55 min, finished 14:26 on 27 Oct 2026)'],
      ['Job 2','# opt freq=raman b3lyp/3-21g geom=allcheck guess=read, gas phase; optimisation converged at step 109 (all four criteria met); frequency step 4 h 42 min; normal termination 08:57 on 28 Oct 2026'],
      ['Frequencies','597 modes (3N - 6); no imaginary frequency, so the structure is a true minimum; lowest 11 cm-1, highest 3495 cm-1'],
      ['Environment variables','GAUSS_EXEDIR=C:\\G16W and GAUSS_SCRDIR=C:\\G16W\\Scratch had to be set on the command line (the first launch failed without them)'],
      ['Earlier attempts','A PM6 run in water (PCM) was far too slow and a B3LYP/6-31G(d) in-water plan was replaced by this quick level; the abandoned PM6/PCM run is archived in old_pm6_pcm. The 119-atom lipid A proxy described in Section 7 gave no output.']],[3.6,14.4],fs=8)
    I.h('5.6 Processing of the lipid A calculation')
    I.t(['Step','Detail'],[
      ['Parse','Harmonic frequencies and Raman activities S read from the Gaussian log into lipidA_raman_act.csv (unscaled)'],
      ['Scale','x 0.965, a typical B3LYP value; not fitted or tested for 3-21G here'],
      ['Intensity','I = S (v0 - v)^4 / ( v (1 - exp(-hcv/kT)) ) at 785 nm and 298.15 K (v0 = 10^7/785 cm-1)'],
      ['Broaden','Lorentzian, FWHM 12 cm-1; 200 to 3300 cm-1; normalised to the tallest peak'],
      ['Script and outputs','make_spectrum.py (python make_spectrum.py lipidA) writes lipidA_spectrum_785nm.csv and .png']],[3.6,14.4],fs=8)
    I.h('5.7 Spectrum obtained and its limits')
    I.p('Of the 597 modes, 354 lie between 400 and 1800 cm-1 after scaling. Compared with the SERS endotoxin reference bands used for this model, the calculation has modes at 845 and 856 (850, glycosidic), near 993 (989, Kdo/carbohydrate; the strongest mode in the 900 to 1000 region), a weak mode at 1139 (1131, lipid chain, weak because the chains are cut), and 1314 and 1338 (1330, phosphate/amide).')
    I.fig(os.path.join(FIG,'..','..','08_Methodology','simulation','LPS_LipidA_Model_20261028','lipidA_spectrum_785nm.png'),'Figure 4. Whole-molecule lipid A model: calculated Raman spectrum at 785 nm (top, 200 to 3300 cm-1) and fingerprint region (bottom); red dotted lines mark the four reference bands.',w=15)
    for x in ["Quick level. Gas phase and B3LYP/3-21G (no diffuse or polarisation functions): positions are approximate and intensities, especially of charged groups, are distorted.",
      "Peaks near 2420, 2590 and 2750 cm-1 are artefacts: strongly hydrogen-bonded O-H stretches to the charged groups, which occur in the gas phase with no water. They lie outside the instrument range and should be ignored.",
      "The strong band at 1512 to 1516 cm-1 is probably an amide N-H / C-N mode that the small basis set overstates. This assignment was not checked, and its relative height should not be trusted.",
      "Cut chains: the CH2 and CH3 bands (about 1440 and 2850 to 3000 cm-1) are under-represented.",
      "Missing parts of the sample: the core oligosaccharide beyond Kdo and the O111 O-antigen. Counter-ions (Na+, Ca2+, Mg2+) and water are not included.",
      "Gaussian Raman activities are orientation-averaged, so they correspond to a powder or solution; peak positions are used for assignment, absolute intensities are not compared."]: I.b(x)
    # section 7 rewrite
    h7=find_p(d,'7. Why whole-molecule simulation was not done','Heading 1'); settext(h7,'7. Why intact LPS and LTA were not simulated whole')
    p=find_p(d,'The reasons below come from the project files')
    settext(p,'The reasons below come from the project files; general points are marked as such. For LPS, the shortened Kdo2-lipid A model of Section 5.5 is the largest whole-molecule calculation that was feasible; for LTA only fragments were run.')
    t=tb(d,'Reason','Evidence','Source')
    for r in t.rows:
        if r.cells[0].text.startswith('Even the best feasible model'):
            cellset(r.cells[0],'The best feasible LPS model is still a piece'); cellset(r.cells[1],'A 119-atom lipid A proxy (charge -2, two phosphates, four hexanoyl chains, no O-antigen, no core oligosaccharide, no secondary chains) was prepared for B3LYP/6-31G(d) and for ORCA, but no output was found. The model that was run is Kdo2-lipid A with shortened chains (201 atoms, charge -4, B3LYP/3-21G; Section 5.5). It has no O-antigen, no core sugars beyond Kdo and no full-length chains, so it is still not whole LPS.')
        if r.cells[0].text.startswith('Cost grows'):
            cellset(r.cells[1],r.cells[1].text+' Measured on this PC: the 201-atom lipid A model took about 55 min (PM6) and 109 optimisation steps of 8 to 9 min plus 4 h 42 min of frequencies at B3LYP/3-21G.')
    p=find_p(d,'Run the lipid A proxy or a two-to-three-unit')
    settext(p,'Rerun the lipid A model at B3LYP/6-31G(d) or B3LYP/6-31+G(d,p) with water (PCM) from the optimised geometry, expect days of run time; and run a two-to-three-unit glycerol-phosphate oligomer with D-alanine ester and counter-ions for LTA, on a workstation with enough memory.')
    anchor=find_p(d,'LPS fragment charge, atom counts')
    I=Ins(d,anchor)
    I.b('Lipid A model: gas phase, one conformer, B3LYP/3-21G, one scale factor not tested for this level, shortened chains, no counter-ions (details in Section 5.7).')
    p=find_p(d,'For LPS or LTA fragments use the route')
    settext(p,'For LPS or LTA fragments use the route and scale factor in Sections 5.2 and 6.2, and record charge and solvent. For the lipid A model use the two-job input in lipidA_short.gjf and make_spectrum.py (Section 5.6).')
    t=tb(d,'Content','Location')
    addrow(t,['LPS lipid A whole-molecule model','C:\\Users\\sukes\\Downloads\\sukesh\\lps output simulation (copy in SERS_Sepsis_Spectral_Library\\08_Methodology\\simulation\\LPS_LipidA_Model_20261028): lipidA_short.gjf (input), lipidA_short.out (Gaussian log, 34 MB), lipidA_short.sdf, lipidA_raman_act.csv, lipidA_spectrum_785nm.csv and .png, make_spectrum.py, Lipid_A_Raman_Methods.md'])
    for p in d.paragraphs:
        if p.text.startswith('Figure 4. LTA fragments'): rep(p,'Figure 4.','Figure 5.')
    d.save(os.path.join(REP,F['sim']))
# ================================================================= LPS findings
def lps():
    d=Document(os.path.join(REP,F['lps']))
    rep(d.paragraphs[2],'Version 1.0, 27 October 2026','Version 1.1, 28 October 2026'); rep(d.paragraphs[2],'the LPS fragment simulation','the LPS simulations (five fragments and a shortened lipid A model)')
    p=find_p(d,'Two further pieces of work give weaker support')
    settext(p,"Two further pieces of work give weaker support. DFT simulations were run in two ways: five LPS fragments (4 of 5 bands within 5 cm-1) and a whole-molecule model of Kdo2-lipid A with shortened chains (all 5 bands within 2.4 cm-1, with calculated modes of moderate strength at 422 and 862 cm-1). Neither agreement is better than chance (p = 0.68 and 0.57) and neither reproduces the overall spectral shape. A SERS session on etched silicon did not detect LPS by the project rule, although a reproducible set of ten bands appeared on 21 of 35 spots and is worth repeating.")
    t=d.tables[0]
    for r in t.rows:
        if r.cells[0].text.startswith('DFT'):
            cellset(r.cells[0],'DFT (5 fragments; shortened lipid A model)'); cellset(r.cells[1],'Fragments: 4 of 5 bands within 5 cm-1 (p = 0.32), shape r = 0.14. Whole-molecule model (201 atoms): 5 of 5 within 2.4 cm-1, not above chance (p = 0.47 to 0.66), shape r = -0.01')
    h=find_p(d,'5. Findings: simulation of LPS fragments'); settext(h,'5. Findings: simulation of LPS (fragments and shortened lipid A)')
    settext(find_p(d,'Intact LPS is too large and variable to calculate'),"Intact LPS is too large and variable to calculate, so two simplified models were used. First, five fragments were simulated separately and combined: KDO, L-glycero-D-manno-heptose, D-glucosamine, myristic acid and phosphoric acid. Second, a whole-molecule model was calculated: the backbone of Kdo2-lipid A (PubChem CID 5771770) with the six acyl chains shortened (201 atoms, charge -4, Gaussian 16W, PM6 then B3LYP/3-21G, gas phase, 109 optimisation steps, 597 modes, no imaginary frequency; run 27-28 Oct 2026). The full settings are in Simulation_Methods_and_Spectra_NAM_LPS_LTA.docx.")
    p=find_p(d,'Result: of the five bands, 4 lie within 5')
    settext(p,f"Result, fragments: of the five bands, 4 lie within 5 cm-1 and all five within 18 cm-1 of a calculated mode, but the five fragments together give about 11 modes per 100 cm-1, and random shifts give 3.1 of 5 within 5 cm-1 (p = 0.32). The 425 cm-1 band is the strongest in the experiment but the only calculated mode near it (phosphoric acid, 425.9 cm-1) is weak. The equal-weight composite correlates with the experimental spectrum at r = 0.14; with fitted weights r = 0.40 and R-squared is negative. Result, whole-molecule model: all five bands lie within 2.4 cm-1 of a calculated mode (mean difference 1.2 cm-1, against 3.5 for the fragments), including 766 cm-1, which the fragments missed by 12 cm-1. The modes at 422 and 862 cm-1 have 0.34 and 0.37 of the maximum calculated activity (fragments: 0.06 and 0.02). The model has 354 modes in 400 to 1800 cm-1 (25 per 100 cm-1), so random shifts give 4.4 of 5 within 5 cm-1 (p = 0.47) and the agreement in position is not evidence of a match. The whole-spectrum correlation is {R['r_whole']:.2f}: the model puts its strongest intensity at 1516 cm-1, where the measured spectrum is weak, and the shortened chains leave out the CH bands. The simulations support a few tentative assignments (for example 861 and 1080 cm-1 as sugar-ring modes) but do not explain the spectrum, and the origin of 425 cm-1 is still open.")
    cap=find_p(d,'Figure 5. Experimental LPS reference (top) and fragment simulation')
    I=Ins(d,cap)
    I.fig(os.path.join(FIG,'LPS_Exp_vs_LipidA_Model.png'),'Figure 6. Experimental LPS reference (top) and whole-molecule model, shortened Kdo2-lipid A (bottom). Dashed lines mark the experimental bands, all within 10 cm-1 of a calculated mode.')
    I.fig(os.path.join(FIG,'LPS_Whole_Molecule_vs_Fragments.png'),'Figure 7. Whole-molecule model against the five fragments: position difference, strength of the matched mode and whole-spectrum correlation.')
    # renumber the figures after the insert (old 6.. -> 8..)
    caps=[p for p in d.paragraphs if re.match(r'^Figure \d+\.',p.text)]
    seen=False; n=0
    for p in caps:
        m=int(re.match(r'^Figure (\d+)\.',p.text).group(1))
        if p.text.startswith('Figure 6. Experimental LPS') or p.text.startswith('Figure 7. Whole-molecule'): continue
        if m>=6: rep(p,f'Figure {m}.',f'Figure {m+2}.')
    for p in d.paragraphs:
        for m in sorted(set(int(x) for x in re.findall(r'Figure (\d+)',p.text)),reverse=True):
            if m>=6 and not re.match(r'^Figure \d+\.',p.text): rep(p,f'Figure {m}',f'Figure {m+2}')
    t=[t for t in d.tables if t.rows[0].cells[0].text=='Question'][0]
    for r in t.rows:
        if r.cells[0].text=='Does simulation explain it?': cellset(r.cells[1],'Only partly: a shortened lipid A model puts all five bands within 2.4 cm-1 and gives moderate strength at 425 and 861, but agreement in position is not better than chance and the shape does not match')
    t=[t for t in d.tables if t.rows[0].cells[0].text=='Content'][-1]
    for r in t.rows:
        if r.cells[0].text=='Figures': cellset(r.cells[1],r.cells[1].text+'; LipidA_Model_20261028')
    addrow(t,['Lipid A simulation','SERS_Sepsis_Spectral_Library/08_Methodology/simulation/LPS_LipidA_Model_20261028 (Gaussian log, input, spectrum); results 05_Tables/LipidA_vs_LPS_results.json'])
    d.save(os.path.join(REP,F['lps']))
if __name__=='__main__':
    import sys
    for k in sys.argv[1:] or ['dft','sim','lps']: globals()[k](); print('done',k)
