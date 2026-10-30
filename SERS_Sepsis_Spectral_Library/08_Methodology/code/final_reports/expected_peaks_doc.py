"""Combined summary: the expected (target) peaks of NAM, LPS and LTA from bulk Raman, simulation and SERS, in one figure and one table per molecule.
Numbers come from Final_Submission/06_Analysis_Tables, the library marker tables and the SERS all-sessions results."""
import os, pickle, numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import fr_docs as FD
FS = r"C:\Users\sukes\Downloads\sukesh\Final_Submission"
OUT = os.path.join(FS, '11_Expected_Peaks_Summary'); os.makedirs(OUT, exist_ok=True)
BD = pickle.load(open(os.path.join(FS, r'09_SERS_All_Sessions\04_Tables\sers_all_results.pkl'), 'rb'))['BD']
COL = {'NAM': '#1f5fa8', 'LPS': '#b5421c', 'LTA': '#2a7d46'}
LONG = {'NAM': 'N-acetylmuramic acid (NAM)', 'LPS': 'Lipopolysaccharide (LPS, E. coli O111:B4)', 'LTA': 'Lipoteichoic acid (LTA, S. aureus)'}
# expected peaks: position, priority (A/B/C), source, reason for targeting
EXP = {
 'NAM': [(929, 'A', 'bulk', 'Strongest NAM band in bulk; calculation agrees; most frequent NAM band in SERS so far. Lies in the 800-1000 window, clear of the bands of a boronic-acid capture layer.'),
         (955, 'A', 'bulk', 'Strong in bulk; seen in SERS spots; same window as 929, so the 929/955 pair is a compact NAM signature.'),
         (870.5, 'A', 'bulk', 'Strong in bulk; calculation agrees within 3 cm-1; completes the 870-955 ring-stretch group.'),
         (1022.7, 'B', 'bulk', 'Bulk and calculation agree within 2 cm-1; ring C-O stretch. Not yet seen in SERS.'),
         (1127, 'B', 'bulk', 'Bulk and calculation agree; C-O-C of the lactyl ether, a group specific to muramic acid. The etched-chip blank also shows a band near 1132, so it needs a clean blank.'),
         (829, 'B', 'bulk', 'Strong in bulk; calculation places the same vibration type 36 cm-1 lower. The 2 min chip blank shows a band here.'),
         (541, 'C', 'bulk', 'Strong in bulk, but only 23 cm-1 above the silicon peak (518) of the SERS chip, so it can be hidden by the silicon wing.')],
 'LPS': [(1330, 'A', 'lit', 'Published SERS marker of LPS on silver (C-H deformation, lipid A). Most frequent target band in our LPS SERS (15 of 35 spots). Not checkable in bulk, because it falls in the glass zone.'),
         (989, 'A', 'lit', 'Published SERS marker of LPS (C-H bending, carbohydrate). The detection rule needs it together with 1330. Not yet seen in our SERS.'),
         (424.8, 'B', 'bulk', 'Strongest bulk LPS band (SNR 38); calculation agrees within 3 cm-1; unique to LPS among the three molecules.'),
         (1080.5, 'B', 'bulk', 'Bulk primary marker; calculation agrees within 1 cm-1; sugar C-O and phosphate. Seen in 2 SERS spots.'),
         (765.5, 'C', 'bulk', 'Bulk supporting band; calculation agrees; no literature assignment.'),
         (995.8, 'C', 'bulk', 'Bulk supporting band; close to the published SERS band at 989, so the two may be the same vibration.'),
         (861.1, 'C', 'bulk', 'Bulk supporting band; also present in LTA, so it does not separate LPS from LTA.')],
 'LTA': [(1092, 'A', 'bulk', 'Strongest LTA band (SNR 30); symmetric PO2- stretch of the phosphodiester backbone; calculation agrees. The detection rule needs it with a lipid band.'),
         (539.3, 'A', 'bulk', 'Bulk primary marker; calculation agrees within 3 cm-1. Unique to LTA here, but close to the silicon peak on the SERS chip.'),
         (1460.1, 'B', 'bulk', 'CH2/CH3 bending of the lipid anchor; the lipid partner for 1092 in the detection rule. Calculation agrees in position.'),
         (799.1, 'B', 'bulk', 'O-P-O stretch of the phosphodiester; calculation agrees; a second phosphate marker.'),
         (861.9, 'B', 'bulk', 'Bulk primary marker; calculation agrees; shared with LPS, so it supports but does not identify LTA.'),
         (1131, 'C', 'lit', 'Fatty-acid C-C stretch from the published LPS SERS table (shared lipid chemistry). Seen in 8 of 20 LTA SERS spots, but also in the chip blank.'),
         (1237.5, 'C', 'lit', 'Antisymmetric PO2- stretch region (1225-1250), from the published functional-group literature. Overlaps a band of the etched-chip blank.')],
}
CMP = {m: pd.read_csv(os.path.join(FS, '06_Analysis_Tables', f'{m}_peak_comparison.csv')) for m in EXP}
MK = {m: FD.marker_table(m) for m in EXP}
def near(d, pos, tol=3):
    k = [x for x in d if abs(x - pos) <= tol]; return min(k, key=lambda x: abs(x - pos)) if k else None
def bulk_txt(m, pos):
    k = near(MK[m], pos)
    if k is None: return 'Not in bulk' + (' (glass zone)' if 1308 <= pos <= 1455 else '')
    v = MK[m][k]; return f"{k:g} (SNR {v['snr']:.0f}, {v['det']} spots)"
def sim_txt(m, pos):
    t = CMP[m]; r = t[(t.measured_peak_cm1 - pos).abs() <= 3]
    if m == 'LPS' and abs(pos - 1330) < 1: return '1338 (-8); C-H bending (CH2, CH3), from the LPS SERS vs simulation comparison', None
    if not len(r) or pd.isna(r.iloc[0].calculated_peak_cm1): return 'Not compared (not a bulk band)', None
    r = r.iloc[0]; return f"{r.calculated_peak_cm1:g} ({r.difference_cm1:+.0f}); {r.vibration_type}", r
def sers_txt(m, pos):
    t = BD[(BD.molecule == m) & ((BD.band - pos).abs() <= 5)]
    if not len(t): return 'Not in the SERS test list yet'
    r = t.loc[t.n_detected.idxmax()]
    if r.n_detected == 0: return f'Not seen ({int(t.n.sum())} spots, {t.session.nunique()} session' + ('s)' if t.session.nunique() > 1 else ')')
    b = '' if pd.isna(r.blank_detected) else f'; blank {int(r.blank_detected)}/{int(r.n_blank)}'
    return f'{int(r.n_detected)}/{int(r.n)} spots ({r.session}{b})'

# ---------------------------------------------------------------- the single figure: expected peaks only
H = {'A': 1.0, 'B': 0.68, 'C': 0.42}
fig, axs = plt.subplots(3, 1, figsize=(10, 7.2), sharex=True, gridspec_kw=dict(hspace=0.32))
for ax, m in zip(axs, ('NAM', 'LPS', 'LTA')):
    c = COL[m]; items = sorted(EXP[m], key=lambda e: e[0])
    for i, (pos, pr, src, _) in enumerate(items):
        h = H[pr]; open_ = src == 'lit'
        ax.plot([pos, pos], [0, h], color=c, lw=2.6 if pr == 'A' else 1.8, ls='--' if open_ else '-', solid_capstyle='butt')
        ax.plot(pos, h, 'o', ms=9 if pr == 'A' else 7, mfc='white' if open_ else c, mec=c, mew=1.6, zorder=3)
        dx = {'NAM': {929: -9, 955: 9}, 'LPS': {989: -14, 995.8: 22}}.get(m, {}).get(pos, 0)
        ax.text(pos + dx, h + 0.1, f'{pos:.0f}', ha='center', va='bottom', fontsize=9.5, fontweight='bold' if pr == 'A' else 'normal', color=c)
    ax.axhline(0, color='#444', lw=.8); ax.set_ylim(0, 1.45); ax.set_yticks([]); ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.set_title(LONG[m], loc='left', fontweight='bold', fontsize=10.5, color=c)
axs[-1].set_xlim(400, 1800); axs[-1].set_xlabel('Raman shift (cm$^{-1}$)', fontsize=10); axs[-1].tick_params(labelsize=9)
leg = [Line2D([0], [0], color='k', lw=2.6, marker='o', ms=9, label='Priority A: first target'), Line2D([0], [0], color='k', lw=1.8, marker='o', ms=7, label='Priority B: confirming band'),
       Line2D([0], [0], color='k', lw=1.2, marker='o', ms=5, label='Priority C: supporting band'),
       Line2D([0], [0], color='k', lw=1.8, ls='--', marker='o', mfc='white', ms=7, label='Expected from published SERS (not in our bulk)')]
fig.legend(handles=leg, loc='lower center', ncol=2, frameon=False, fontsize=8.5, bbox_to_anchor=(0.5, -0.06))
fig.suptitle('Expected Raman / SERS peaks of the three sepsis biomarkers', x=0.01, ha='left', fontweight='bold', fontsize=12)
FIG = os.path.join(OUT, 'Expected_Peaks_NAM_LPS_LTA.png'); fig.savefig(FIG, dpi=220, bbox_inches='tight'); plt.close(fig)

# ---------------------------------------------------------------- document
d = FD.Doc('Expected Peaks of NAM, LPS and LTA', 'Bulk Raman, molecular simulation and SERS combined: which bands to target in future SERS work, and why')
d.h1('Summary')
d.p("Three lines of evidence were combined for each biomarker. Bulk Raman of the pure biomarker shows which bands the molecule really has. "
    "The molecular simulation shows which vibration causes each band. The SERS measurements on silver-etched silicon show which bands have appeared on the chip so far. "
    "A band is listed as expected when the bulk spectrum and the simulation agree on it, or when it is a published SERS marker of the molecule.")
d.b('929, 955 and 870 cm-1 (sugar-ring C-O / C-C stretching). 929 and 955 cm-1 are also the NAM bands seen most often on the SERS chip so far.', 'NAM:')
d.b('1330 and 989 cm-1 (published SERS markers of the lipid A and sugar parts), backed by the bulk bands at 425 and 1080 cm-1.', 'LPS:')
d.b('1092 cm-1 (phosphate backbone) together with 539 cm-1 and a lipid band near 1460 cm-1.', 'LTA:')
d.p("SERS status: a few of these bands appear in some SERS spots. None is yet reproducible against the substrate blank, so the bands are targets for the next experiments, not detections.")
d.h1('Expected peaks in one figure')
d.figure(FIG, 'Expected peaks only. The height of a bar shows its priority for SERS work, not its measured intensity. Solid bars: present in bulk Raman, with the vibration type taken from the simulation. Dashed bars: published SERS markers that our bulk measurement cannot check (1330 lies in the glass zone; 989 is close to bulk 996).')
d.h1('Why each peak is expected')
d.p('Bulk: position in the reference spectrum, with SNR and the number of spots that show the band. Simulation: calculated position (shift from bulk) and type of vibration. SERS so far: the session with the most spots showing the band, and how many blank spectra also show it.')
for m in ('NAM', 'LPS', 'LTA'):
    d.h2(LONG[m])
    rows = []
    for pos, pr, src, why in sorted(EXP[m], key=lambda e: ('ABC'.index(e[1]), e[0])):
        st, _ = sim_txt(m, pos)
        rows.append([f'{pos:g}', pr, bulk_txt(m, pos), st, sers_txt(m, pos), why])
    d.table(['Peak (cm-1)', 'Pri.', 'Bulk', 'Simulation', 'SERS so far', 'Why expected and targeted'], rows, [1.5, 0.9, 2.6, 3.3, 2.6, 5.7], f'Expected peaks of {m}.', fs=8)
d.h1('Which peaks tell the three molecules apart')
d.table(['Molecule', 'Bands found only in this molecule', 'Shared bands (not useful for identification)'],
        [['NAM', '929, 955, 1127 (lactyl ether), 829', '870 (near LPS/LTA 861)'],
         ['LPS', '425, 1330 (SERS), 989 (SERS)', '861 (also LTA), 1080 (close to LTA 1092)'],
         ['LTA', '1092 (phosphate, strongest), 539, 799', '861 (also LPS), 1460 (lipid, also LPS 1456)']],
        [2.2, 7.0, 7.4], 'Identifying and shared bands.')
d.p('For identification, look for a pattern of bands, not a single band. The pairs 929 + 955 (NAM), 1330 + 989 (LPS) and 1092 + 1460 (LTA) are the suggested minimum signatures.')
d.h1('Future work direction')
for lead, t in (('Chip:', 'Use the 20 mM AgNO3, 2 min recipe, which gave the strongest R6G signal. Make several chips and pass each through the R6G test (1509 cm-1, SNR >= 10) before any biomarker.'),
                ('Blank:', 'Measure each chip without analyte in the same session. The etched chips show their own bands near 855, 963, 1006, 1132, 1237 and 1393 cm-1, some close to the expected peaks.'),
                ('NAM:', 'Add a boronic-acid capture layer (MPBA) with a bare-silver control, and read the 870-955 cm-1 window, where the capture layer has no strong band.'),
                ('LPS:', 'Repeat on the best chip with more spots and a concentration series. Accept detection only if 1330 and 989 cm-1 appear together and are absent from the blank.'),
                ('LTA:', 'Use a fresh solution (LTA is stable only about 2 days at 4 C) and test a cysteamine layer. Accept detection only if 1092 cm-1 appears with a lipid band (1450-1460 or 1131).'),
                ('Silicon peak:', 'Bands within about 30 cm-1 of 518 cm-1 (NAM 541, LTA 539) can be masked by the silicon wing. Treat them as confirming bands, not primary ones.')):
    d.b(t, lead)
d.h1('Sources')
for t in ('Bulk: SERS_Sepsis_Spectral_Library/03_Reference_Spectra (NAM n = 15; LPS n = 10; LTA pooled v2.1, n = 17).', 'Simulation: Final_Submission/06_Analysis_Tables/<molecule>_peak_comparison.csv (NAM beta form; LPS lipid A model; LTA model).',
          'SERS: Final_Submission/09_SERS_All_Sessions (868 spectra, eight sessions), sheet Biomarker_Bands.',
          'Published SERS markers of LPS: Wu, Zhao and Zughaier (2021), Biosensors 11(7):234, DOI 10.3390/bios11070234 (989 and 1330 cm-1; also used for 1131 and 1450).'):
    d.b(t)
DOC = os.path.join(OUT, 'Expected_Peaks_NAM_LPS_LTA_Summary.docx'); d.save(DOC); print(DOC)
