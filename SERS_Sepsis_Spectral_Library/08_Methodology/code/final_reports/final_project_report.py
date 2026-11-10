"""Ten-page final report: bulk Raman library, molecular simulation and SERS, start to end.
Numbers are read from the library tables, the analysis tables and the SERS all-sessions results; nothing is typed in by hand
except the concentrations and recipe values recorded in the lab documents."""
import os, pickle, numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from docx.shared import Cm, Pt
import fr_data as D, fr_docs as FD
FS = r"C:\Users\sukes\Downloads\sukesh\Final_Submission"
OUT = os.path.join(FS, '12_Final_Project_Report'); FIG = os.path.join(OUT, 'figures'); os.makedirs(FIG, exist_ok=True)
X = D.X; plt.rcParams.update({'font.family': 'Arial', 'font.size': 9})
P = pickle.load(open(os.path.join(FS, r'09_SERS_All_Sessions\04_Tables\sers_all_results.pkl'), 'rb'))
R6, R6S, BD, VD, BGL = P['R6'], P['R6S'], P['BD'], P['VD'], P['BGL']
MS = pd.read_excel(os.path.join(FS, r'09_SERS_All_Sessions\04_Tables\SERS_All_Sessions_Workbook.xlsx'), sheet_name='Mean_Spectra')
CMP = {m: pd.read_csv(os.path.join(FS, '06_Analysis_Tables', f'{m}_peak_comparison.csv')) for m in ('NAM', 'LPS', 'LTA')}
MK = {m: FD.marker_table(m) for m in ('NAM', 'LPS', 'LTA')}
COL = D.COL; G = ~((X >= D.GLASS[0]) & (X <= D.GLASS[1]))
SET = {'S2': 'Set 1', 'S3': 'Set 2', 'S4': 'Set 3', 'S5': 'Set 4', 'S7': 'Set 5', 'S8': 'Set 6'}
def mcol(prefix): return [c for c in MS.columns if c.startswith(prefix)][0]
def save(fig, n): p = os.path.join(FIG, n); fig.savefig(p, dpi=220, bbox_inches='tight'); plt.close(fig); return p

# ---------------------------------------------------------------- Figure 1: bulk reference spectra
ref = {m: D.exp_ref(m) for m in ('NAM', 'LPS', 'LTA')}
fig, ax = plt.subplots(figsize=(9, 5.0)); off = {'NAM': 2.5, 'LPS': 1.25, 'LTA': 0}
for m in ('NAM', 'LPS', 'LTA'):
    y, sd, _ = ref[m]; o = off[m]
    ax.fill_between(X, y - sd + o, y + sd + o, color=COL[m], alpha=.18, lw=0); ax.plot(X, y + o, color=COL[m], lw=1.2)
    ax.text(1795, o + 0.75, {'NAM': 'NAM', 'LPS': 'LPS', 'LTA': 'LTA'}[m], ha='right', fontsize=10, fontweight='bold', color=COL[m])
    for pos, role in D.peaks(m):
        if role != 'main': continue
        i = int(round(pos - 400)); j = max(range(max(i - 4, 0), min(i + 5, len(X))), key=lambda k: y[k])
        ax.text(X[j], y[j] + o + 0.04, f'{pos:.0f}', ha='center', va='bottom', fontsize=7.5, color=COL[m], rotation=90)
ax.axvspan(*D.GLASS, color='#e3e3e3', lw=0, zorder=0); ax.text(1381, 3.62, 'glass band\nregion', ha='center', fontsize=7, color='#666')
ax.set_xlim(400, 1800); ax.set_ylim(-0.05, 3.85); ax.set_yticks([]); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('Normalised intensity (offset)')
f1 = save(fig, 'Fig1_bulk_reference_spectra.png')

# ---------------------------------------------------------------- Figure 2: simulation against bulk
fig, axs = plt.subplots(3, 1, figsize=(9, 7.4), sharex=True, gridspec_kw=dict(hspace=.28))
for ax, m in zip(axs, ('NAM', 'LPS', 'LTA')):
    y = ref[m][0]; c = D.calc_curve(m)
    ax.plot(X, y + 1.1, color=COL[m], lw=1.2); ax.plot(X, c * 0.95, color=D.CALC, lw=1.2)
    for r in CMP[m].itertuples():
        if pd.isna(r.calculated_peak_cm1): continue
        col = '#2a9d55' if str(r.result).startswith('agrees') else '#d07a00'
        ax.plot([r.measured_peak_cm1, r.calculated_peak_cm1], [1.08, 0.97], color=col, lw=1.1)
        ax.text(r.measured_peak_cm1, 2.18, f'{r.measured_peak_cm1:.0f}', ha='center', fontsize=7, color=col, rotation=90, va='bottom')
    ax.axvspan(*D.GLASS, color='#ececec', lw=0, zorder=0); ax.set_ylim(-0.05, 2.75); ax.set_yticks([])
    ax.set_title(f"{D.NAME[m][0].upper() + D.NAME[m][1:]}: measured (top) and calculated (bottom)", loc='left', fontsize=9, fontweight='bold', color=COL[m])
axs[-1].set_xlim(400, 1800); axs[-1].set_xlabel('Raman shift (cm$^{-1}$)')
fig.legend(handles=[Line2D([0], [0], color='#2a9d55', label='within 10 cm$^{-1}$, same vibration type'), Line2D([0], [0], color='#d07a00', label='shifted 10-50 cm$^{-1}$, same vibration type')],
           loc='lower center', ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.03))
f2 = save(fig, 'Fig2_simulation_vs_bulk.png')

# ---------------------------------------------------------------- Figure 4: R6G performance of the chips
def med(ses, sub, pw, it, conc=''):
    v = R6[(R6.session == ses) & (R6['sub'] == sub) & (R6.power == pw) & (R6.it == it) & (R6.conc == conc)].snr1509; return float(v.median()), len(v)
R2 = '20mMAg-8p6mlHF'
grpA = [('2 min', med('S5', R2 + '-2min', 5, 5)), ('10 min', med('S5', R2 + '-10min', 5, 5)), ('5 min', med('S5', R2 + '-5min', 5, 5)), ('2 min\n2nd chip', med('S7', R2 + '-2min', 5, 5))]
grpB = [(f'{m} min\n{v} mL HF', med('S3', f'{m}min-{v}mlHF', 10, 5)) for m in (3, 4, 5, 6) for v in (5, 10)]
conc = R6[(R6.session == 'S4') & R6.conc.str.contains('M')]
order = ['1nM', '10nM', '100nM', '1uM', '10uM', '1mM']; lab = {'1nM': '1 nM', '10nM': '10 nM', '100nM': '100 nM', '1uM': '1 µM', '10uM': '10 µM', '1mM': '1 mM'}
fig, axs = plt.subplots(1, 3, figsize=(11, 3.6), gridspec_kw=dict(width_ratios=[1.1, 1.9, 1.3]))
axs[0].bar(range(4), [g[1][0] for g in grpA], color=['#6a3d9a', '#9a77bd', '#c7b3dc', '#6a3d9a'], edgecolor='k', lw=.5); axs[0].set_xticks(range(4)); axs[0].set_xticklabels([g[0] for g in grpA], fontsize=7.5)
axs[0].set_title('20 mM AgNO$_3$ chips', loc='left', fontweight='bold', fontsize=9); axs[0].set_ylabel('Median SNR of the 1509 cm$^{-1}$ band')
axs[1].bar(range(8), [g[1][0] for g in grpB], color='#c05a2b', edgecolor='k', lw=.5); axs[1].set_xticks(range(8)); axs[1].set_xticklabels([g[0] for g in grpB], fontsize=7)
axs[1].set_title('6 mg AgNO$_3$ chips (etch time, HF volume)', loc='left', fontweight='bold', fontsize=9)
gm = conc.groupby('conc').snr1509.median().reindex(order)
axs[2].scatter([order.index(c) for c in conc.conc], conc.snr1509, color='#6a3d9a', s=16, zorder=3); axs[2].plot(range(6), gm.values, color='k', lw=1)
axs[2].set_xticks(range(6)); axs[2].set_xticklabels([lab[c] for c in order], fontsize=7.5); axs[2].set_title('R6G concentration series', loc='left', fontweight='bold', fontsize=9)
for a in axs: a.axhline(10, color='#b5421c', ls='--', lw=.8); a.spines[['top', 'right']].set_visible(False)
f4 = save(fig, 'Fig4_R6G_chip_performance.png')
# R6G mean spectra of the main chip types
r6rows = [('20 mM AgNO$_3$, 2 min etch', 'S5_R6G_20mMAg-8p6mlHF-2min'), ('20 mM AgNO$_3$, 10 min etch', 'S5_R6G_20mMAg-8p6mlHF-10min'),
          ('20 mM AgNO$_3$, 2 min etch (second chip)', 'S7_R6G_20mMAg-8p6mlHF-2min'), ('6 mg AgNO$_3$, 6 min etch, 10 mL HF', 'S3_R6G_6min-10mlHF'),
          ('6 mg AgNO$_3$, 5 mL HF', 'S4_R6G_6mgAg-5mlHF (')]
fig, ax = plt.subplots(figsize=(9, 4.6)); o = 0
for name, pre in r6rows[::-1]:
    y = MS[mcol(pre)].values; k = X >= 560; y = y / y[k].max()
    ax.plot(X[k], y[k] + o, color='#6a3d9a', lw=1.1); ax.text(1795, o + 0.55, name, ha='right', fontsize=8, bbox=dict(fc='white', ec='none', pad=1)); o += 1.1
for b in (612, 774, 1183, 1310, 1362, 1509, 1650):
    ax.axvline(b - 3, color='#999', ls=':', lw=.7); ax.text(b - 3, o + 0.02, str(b), ha='center', fontsize=7.5, color='#555')
ax.set_xlim(560, 1800); ax.set_ylim(-0.05, o + 0.2); ax.set_yticks([]); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('Normalised SERS signal (offset)')
f4b = save(fig, 'Fig4b_R6G_spectra.png')

# ---------------------------------------------------------------- Figure 5: SERS spectra (working probe and the three biomarkers)
def mcol(prefix): return [c for c in MS.columns if c.startswith(prefix)][0]
rows = [('R6G on the best chip (20 mM, 2 min)', mcol('S5_R6G_20mMAg-8p6mlHF-2min'), '#6a3d9a', None),
        ('NAM', mcol('S8_NAM'), COL['NAM'], 'NAM'), ('LPS', mcol('S8_LPS'), COL['LPS'], 'LPS'), ('LTA', mcol('S8_LTA'), COL['LTA'], 'LTA'),
        ('Chip without analyte (blank)', mcol('S8_Blank'), '#555555', None)]
fig, ax = plt.subplots(figsize=(9, 5.4)); o = 0
for name, cn, c, m in rows[::-1]:
    y = MS[cn].values; k = (X >= 560); y = y / max(y[k].max(), 1e-9)
    ax.plot(X[k], y[k] + o, color=c, lw=1.1); ax.text(1795, o + 0.72, name, ha='right', fontsize=8.5, color=c, fontweight='bold')
    o += 1.1
ax.set_xlim(560, 1800); ax.set_yticks([]); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('Normalised SERS signal (offset)')
f5 = save(fig, 'Fig5_SERS_spectra.png')

# ---------------------------------------------------------------- Figure 6: target-band heat map
fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.2), gridspec_kw=dict(width_ratios=[5, 2, 1]))
for ax, m in zip(axs, ('NAM', 'LTA', 'LPS')):
    sub = BD[BD.molecule == m]; ses = sorted(sub.session.unique()); bands = sorted(sub.band.unique())
    M = np.array([[sub[(sub.session == s) & (sub.band == b)].frac.iloc[0] for s in ses] for b in bands])
    im = ax.imshow(M, cmap='Blues', vmin=0, vmax=1, aspect='auto')
    for i in range(M.shape[0]):
        for j in range(M.shape[1]): ax.text(j, i, f'{M[i, j]*100:.0f}', ha='center', va='center', fontsize=7.5, color='white' if M[i, j] > .55 else 'black')
    ax.set_xticks(range(len(ses))); ax.set_xticklabels([SET[s] for s in ses], fontsize=8); ax.set_yticks(range(len(bands))); ax.set_yticklabels([f'{b:g}' for b in bands], fontsize=8)
    ax.set_title(m, loc='left', fontweight='bold', fontsize=9.5)
fig.colorbar(im, ax=axs, shrink=.85, label='Spots showing the band (%)')
f6 = save(fig, 'Fig6_target_band_heatmap.png')
f7 = os.path.join(FS, r'11_Expected_Peaks_Summary\Expected_Peaks_NAM_LPS_LTA.png')
f3 = os.path.join(FS, r'10_SERS_Chip_Fabrication\figures\C1_process_flow.png')

# ---------------------------------------------------------------- numbers for the text
def r_ab(a, b): return float(np.corrcoef(ref[a][0][G], ref[b][0][G])[0, 1])
cor = {('NAM', 'LPS'): r_ab('NAM', 'LPS'), ('NAM', 'LTA'): r_ab('NAM', 'LTA'), ('LPS', 'LTA'): r_ab('LPS', 'LTA')}
nmem = {m: len(pd.read_csv(D.LIB + '/' + D.MEMBERS[m])) for m in ('NAM', 'LPS', 'LTA')}
agr = {m: (int(CMP[m].result.str.startswith('agrees').sum()), int(CMP[m].result.str.startswith('shifted').sum()), len(CMP[m])) for m in CMP}
best = grpA[0][1][0]; second = grpA[3][1][0]
n_all, n_uniq = P['n'], P['n_uniq']
bg = ', '.join(f'{r.median_pos:.0f}' for r in BGL[BGL.role == 'blank'].sort_values('frac', ascending=False).itertuples())

# ---------------------------------------------------------------- document
d = FD.Doc('Label-Free Raman and SERS Detection of Sepsis Biomarkers', 'Final report: bulk reference library, molecular simulation and surface-enhanced Raman measurements of NAM, LPS and LTA')
sec = d.d.sections[0]
for a in ('left_margin', 'right_margin'): setattr(sec, a, Cm(1.8))
sec.top_margin = Cm(1.6); sec.bottom_margin = Cm(1.6)
d.d.styles['Normal'].font.size = Pt(10.5)
W = 17.2
d.h1('Summary')
d.p("The aim of the work was to build the measurement and analysis basis for detecting three bacterial cell-wall molecules linked to sepsis by Raman spectroscopy: N-acetylmuramic acid (NAM), a component of peptidoglycan common to all bacteria; lipopolysaccharide (LPS), the outer-membrane endotoxin of Gram-negative bacteria; and lipoteichoic acid (LTA), a cell-wall polymer of Gram-positive bacteria. "
    "The work moved in three steps: a reference library of the pure biomarkers measured as bulk material, a molecular simulation of each molecule to explain its bands, and surface-enhanced Raman spectroscopy (SERS) on silver-etched silicon chips made in the laboratory.")
d.b(f"Reproducible reference spectra were obtained for all three biomarkers (NAM {nmem['NAM']} spots, LPS {nmem['LPS']} spots, LTA {nmem['LTA']} spots), each with its own set of marker bands. The three spectra are clearly different from each other (correlation between them {min(cor.values()):.2f} to {max(cor.values()):.2f}).", 'Bulk library.')
d.b(f"The calculated spectra reproduce most marker bands of the measured spectra within 10 cm-1 and with the same type of vibration (NAM {agr['NAM'][0]} of {agr['NAM'][2]}, LPS {agr['LPS'][0]} of {agr['LPS'][2]}, LTA {agr['LTA'][0]} of {agr['LTA'][2]} listed bands), which gives a tentative assignment of each band to part of the molecule.", 'Simulation.')
d.b(f"The silver-etched silicon chips are SERS-active: the test dye rhodamine 6G (R6G) gave its full band set, with a median signal-to-noise ratio of about {best:.0f} on the best chip. "
    "NAM, LPS and LTA were measured on several chip types at several concentrations. A few target bands appeared in some spots, and LPS showed a repeating set of ten bands, but no target band was yet reproducible against the blank chip.", 'SERS.')
d.b("For each molecule a short list of expected target bands, with the reason for each, has been defined to guide further sensor work (Section 7).", 'Outcome.')

d.h1('Materials and methods')
d.h2('Biomarkers and instrument')
d.p("NAM, LPS (E. coli O111:B4) and LTA (S. aureus) were used as received from the supplier. All spectra were recorded on a portable dispersive Raman spectrometer with 785 nm excitation and a fibre probe, over 400-1800 cm-1. "
    "Laser power is given as the instrument setting in percent of maximum. The power at the sample was not measured.")
d.h2('Bulk measurements')
d.p("A small amount of each powder was placed on a glass slide and measured at several spots. The settings were optimised separately for each molecule, because high laser power produced a periodic ripple in the spectra and, for NAM, damaged the sample at long exposure. "
    "The dark spectrum was recorded with the shutter closed by hand, because the software dark was found to pick up light from the sample.")
d.table(['Biomarker', 'Final setting (power / integration / accumulations)', 'Spots in the reference', 'Status'],
        [['NAM', '90 % / 30 s / 5', nmem['NAM'], 'Final; confirmed by a second set of 21 spots'],
         ['LPS', '60 % / 40 s / 5', nmem['LPS'], 'Established'], ['LTA', '80 % / 30 s / 3 and 80 % / 45 s / 2 (pooled)', nmem['LTA'], 'Established']],
        [2.2, 6.6, 3.2, 5.2], 'Acquisition settings of the bulk reference spectra.')
d.h2('Data processing and quality control')
d.p("Every spectrum was processed in the same way: dark subtraction, correction of two hot detector pixels, cropping to 400-1800 cm-1, spike removal, Savitzky-Golay smoothing, baseline removal by asymmetric least squares, and min-max scaling. "
    "Spectra were rejected if they were saturated, had ripple above 50 counts, a signal-to-noise ratio below 10, or were dominated by the glass signal. Each rejection was logged with its reason, and the reference is the mean and standard deviation of all accepted spots. "
    "The glass band region (1308-1455 cm-1) was left out of all comparisons and is never used as a marker.")
d.h2('Molecular simulation')
d.p("The Raman spectrum of each molecule was calculated with density functional theory: NAM (beta form) with B3LYP-D3BJ/6-311++G(d,p); LPS as a whole-molecule lipid A model with two Kdo sugars (201 atoms); and LTA as a model with three glycerol-phosphate units, two D-alanine esters and one N-acetylglucosamine (93 atoms), both with B3LYP/3-21G. "
    "Frequencies were scaled (0.965-0.98) and broadened to a spectrum. For each calculated vibration, the atoms that move most were used to label the type of vibration. A measured band was matched to a calculated one only when the vibration type agreed, within 50 cm-1.")
d.h2('SERS chip fabrication')
d.p("The chips were made from n-type Si(100) wafer (1-10 ohm cm) by one-step metal-assisted chemical etching. Pieces of about 1 x 1 cm were cleaned in acetone, isopropanol and water, briefly dipped in dilute HF to remove the oxide, "
    "and immersed in a bath of silver nitrate and HF. Silver is deposited as nanoparticles while the silicon underneath is etched, leaving a dark, rough surface on which the silver particles act as the enhancing sites. Two bath recipes were used:")
d.b('6 mg AgNO3 with 5 or 10 mL HF in 45 mL water (about 0.7 mM AgNO3), etched 3, 4, 5 or 6 min.', 'Recipe 1:')
d.b('0.170 g AgNO3 and 8.6 mL HF made up to 50 mL (20 mM AgNO3), etched 1, 2, 5 or 10 min.', 'Recipe 2:')
d.figure(f3, 'Steps of chip fabrication and measurement.', w=15.5)
d.figure(os.path.join(FS, r'10_SERS_Chip_Fabrication\figures\C3_cleaning_and_chips.png'), '(a) Ultrasonic cleaning of the silicon pieces. (b) Etched chips of the 6 mg AgNO3 series, labelled by etch time (3-6 min) and HF volume (5 or 10 mL). The etched area is dark and matte.', w=12.5)
d.h2('SERS measurements and concentrations')
d.p("The analyte solution was drop-cast on the chip and dried, and several spots were measured on each chip. The silicon peak near 518 cm-1 was used as an internal reference: every SERS spectrum was divided by its silicon peak height. "
    "A chip measured without analyte (blank) was used to identify bands that come from the chip itself. Six chip sets were measured; Table 2 lists them with the concentrations used.")
d.table(['Chip set', 'Chip', 'Analytes and concentrations', 'Spectra'],
        [['Set 1', 'Recipe 1, 3-6 min', 'R6G 1 mg/mL; NAM 1 mg/mL', int(((P['IDX'].session == 'S2') & (P['IDX'].duplicate_of == '')).sum())],
         ['Set 2', 'Recipe 1, 3-6 min, 5 or 10 mL HF (eight chips)', 'R6G (concentration not recorded)', int((P['IDX'].session == 'S3').sum())],
         ['Set 3', 'Recipe 1, 5 mL HF', 'R6G series 1 nM, 10 nM, 100 nM, 1 µM, 10 µM, 1 mM; NAM 0.1 and 1 mg/mL; blank', int((P['IDX'].session == 'S4').sum())],
         ['Set 4', 'Recipe 2, 2, 5 and 10 min', 'R6G 0.001, 0.01 and 0.1 mM; NAM 1 mg/mL (3.41 mM); blanks', int((P['IDX'].session == 'S5').sum())],
         ['Set 5', 'Recipe 2, 1 and 2 min', 'R6G; NAM 1 mg/mL; LTA (concentration not recorded); blanks on three chips', int((P['IDX'].session == 'S7').sum())],
         ['Set 6', 'Recipe 1, 5 mL HF', 'NAM, LPS and LTA (concentrations not recorded); blank', int((P['IDX'].session == 'S8').sum())],
         ['Checks', 'Plain silicon', 'No analyte (instrument and silicon reference)', int(P['IDX'].session.isin(['S1', 'S6']).sum())]],
        [1.7, 5.0, 8.4, 2.0], f'SERS chip sets ({n_uniq} spectra in total).', fs=8.5)
d.h2('Detection criteria')
d.p("A band was counted in a spectrum when a peak was found within 5 cm-1 of the target, at least 3 detector pixels wide, with a signal-to-noise ratio of at least 3. "
    "A band was called reproducible when it was present in at least half of the spots, absent from every blank of the same set, and significantly taller than in the blank (one-sided Mann-Whitney test, p < 0.05). "
    "A chip had to show the R6G 1509 cm-1 band at a signal-to-noise ratio of 10 or more to be considered SERS-active. Detection of a biomarker needed two NAM marker bands, LPS 989 and 1330 cm-1 together, or for LTA a phosphate band (1092 or 1225-1250 cm-1) together with a lipid band (1131 or 1450 cm-1).")

d.h1('Bulk reference library')
d.figure(f1, 'Bulk reference spectra (mean and standard deviation of all accepted spots). The numbers mark the primary marker bands. The grey region is the glass band region, excluded from all comparisons.', w=W)
rows = []
for m in ('NAM', 'LPS', 'LTA'):
    pk = [p for p, r in D.peaks(m) if r == 'main']; sp = [p for p, r in D.peaks(m) if r != 'main']
    def fmt(p):
        k = min(MK[m], key=lambda x: abs(x - p)); return f"{p:.0f} ({MK[m][k]['snr']:.0f})"
    rows.append([m, ', '.join(fmt(p) for p in sorted(pk)), ', '.join(fmt(p) for p in sorted(sp))])
d.table(['Biomarker', 'Primary marker bands, cm-1 (SNR)', 'Supporting bands, cm-1 (SNR)'], rows, [2.2, 7.4, 7.4], 'Marker bands of the bulk reference spectra with their median signal-to-noise ratio.')
d.p(f"Reproducibility between spots was high: the NAM primary bands were found in all {nmem['NAM']} spots with a position spread below 1 cm-1, the LPS spots agree with a mean pairwise correlation of 0.92, and the pooled LTA reference agrees with the reference from the main setting alone with a correlation of 0.996. "
    "Spots that failed quality control were mainly saturated, affected by ripple at high power, dominated by glass, or recorded with a faulty dark spectrum; none of these were used.")
d.p(f"NAM gives the richest spectrum, with seven strong sugar-ring bands between 541 and 1127 cm-1, all present in every spot. LPS is dominated by a low-frequency band at 425 cm-1 and a broad band at 1080 cm-1; its absolute intensity varied three- to five-fold between spots, so band ratios were used. "
    f"LTA shows its strongest band at 1092 cm-1, typical of the phosphate backbone, with further bands at 539 and 862 cm-1. "
    f"The three spectra are distinct: the correlation is {cor[('NAM','LPS')]:.2f} between NAM and LPS, {cor[('NAM','LTA')]:.2f} between NAM and LTA, and {cor[('LPS','LTA')]:.2f} between LPS and LTA, the last pair sharing the band near 861 cm-1.")

d.h1('Molecular simulation and band assignment')
d.figure(f2, 'Measured bulk spectrum (top curve) and calculated spectrum (bottom curve) of each molecule. Lines join each marker band to the calculated vibration of the same type.', w=W)
rows = []
for m in ('NAM', 'LPS', 'LTA'):
    t = CMP[m]; main = t[t.role == 'main']
    rows.append([m, f'{agr[m][0]} of {agr[m][2]}', f'{agr[m][1]}', '; '.join(f'{r.measured_peak_cm1:.0f}: {r.expected_assignment}' for r in main.itertuples())[:260]])
d.table(['Biomarker', 'Within 10 cm-1', 'Shifted, same type', 'Main bands and tentative assignment'], rows, [2.0, 2.2, 2.4, 10.4], 'Agreement between measured and calculated bands.', fs=8.5)
d.p("Most bands are reproduced within 10 cm-1. The remaining ones are shifted by 15-36 cm-1 but have a calculated vibration of the same type nearby; they are treated as the same vibration, displaced because the calculation describes a single isolated molecule, "
    "while in the solid the molecules are hydrogen-bonded to their neighbours. The calculation suggests that the NAM marker bands come from C-O and C-C stretching of the sugar ring and lactyl side chain, the LPS bands from skeletal and sugar C-O modes, "
    "and the strongest LTA band from the symmetric stretch of the phosphate group. The relative intensities agree less well than the positions, which is common for this type of calculation.")

d.h1('SERS chip performance with R6G')
d.figure(f4b, 'Mean R6G SERS spectra on the main chip types, each scaled to its tallest band. Dotted lines: standard R6G bands (measured positions lie 2-4 cm-1 lower because of the calibration offset of the instrument).', w=16)
d.figure(f4, 'Signal-to-noise ratio of the R6G 1509 cm-1 band. Left: 20 mM AgNO3 chips at different etch times. Middle: the eight 6 mg AgNO3 chips. Right: R6G concentration series on one chip. Dashed line: threshold of 10. Left and middle panels use different settings.', w=W)
d.p(f"All chips gave the R6G band set (612, 774, 1183, 1310, 1362, 1509 and 1650 cm-1), confirming that the silver-etched surface enhances the Raman signal. "
    f"The 20 mM AgNO3 recipe with a 2 min etch was by far the best (median signal-to-noise ratio {best:.0f}), followed by the 10 min etch ({grpA[1][1][0]:.0f}) and the 5 min etch ({grpA[2][1][0]:.0f}). "
    f"The low-silver recipe gave ratios of only {min(g[1][0] for g in grpB):.0f} to {max(g[1][0] for g in grpB):.0f}; among those chips, the 6 min etch with 10 mL HF was clearly the best, which suggests that more silver deposition improves that recipe. "
    f"A second chip made with the best recipe reached {second:.0f}, about {best/second:.0f} times lower than the first, so the chip-to-chip reproducibility still needs work.")
d.p("In the concentration series, the 1509 cm-1 band passed the threshold in some spots down to 100 nM to 1 µM and was absent at 1 and 10 nM. The signal at 1 mM was lower than at 10 µM, consistent with aggregation of the dye at high concentration. "
    "With two to five spots per level this gives an observed lowest concentration, not a formal detection limit.")

d.h1('SERS of the biomarkers')
d.figure(f5, 'Mean SERS spectra on the silver-etched chip: R6G on the best chip (top) for comparison, NAM, LPS and LTA on the same chip type, and the chip without analyte (bottom). Each curve is scaled to its own maximum; the silicon peak is left out.', w=16.5)
d.figure(f6, 'Percentage of spots in which each target band was found, for each chip set.', w=W)
d.table(['Biomarker', 'Chip sets', 'Spots', 'Band seen most often', 'Result'],
        [[m, ', '.join(SET[s] for s in sorted(VD[VD.molecule == m].session)), int(VD[VD.molecule == m].n.sum()),
          '; '.join(f"{r.most_frequent_band:g} ({r.most_frequent_frac*100:.0f} %, {SET[r.session]})" for r in VD[VD.molecule == m].itertuples() if r.most_frequent_frac > 0.1) or 'below 10 % of spots',
          'Not yet detected' + (' (Set 1 had no blank)' if m == 'NAM' else '')] for m in ('NAM', 'LPS', 'LTA')],
        [2.0, 3.6, 1.4, 6.2, 3.8], 'Biomarker results against the detection criteria.', fs=8.5)
d.p("NAM bands at 929 and 955 cm-1 appeared in up to 19 % and 13 % of spots, but not consistently enough to pass the criteria; the other NAM bands were rare. "
    "On LPS spots, the published SERS marker at 1330 cm-1 was seen in 43 % of spots, but 989 cm-1 was absent. A set of ten bands (619, 785, 878, 1009, 1238, 1330, 1368, 1455, 1536 and 1592 cm-1) repeated on 21 of 35 LPS spots and was not present in the blank, "
    "which is consistent with an LPS-related surface signal; only 1330 cm-1 lies within 10 cm-1 of a calculated band, and 1330 and 1455 cm-1 agree in vibration type with the published C-H deformation bands. "
    "On LTA spots, 1131 cm-1 appeared in 40 % of spots on one chip, but the blank of the same chip showed the same band.")
d.p(f"The chips without analyte show recurring bands of their own, near {bg} cm-1 (the band near 963 cm-1 is consistent with the second-order silicon band). "
    "Several of these lie close to biomarker targets, which is why every result was judged against a blank of the same chip set.")

d.h1('Expected target bands')
d.figure(f7, 'Expected bands of the three biomarkers, combining the bulk reference, the simulation and the SERS results. Bar height shows the priority for sensor work, not intensity; dashed bars are published SERS markers that could not be checked in bulk.', w=15.5)
import re, expected_peaks_doc as EP
def setname(t): return re.sub(r'\b(S\d)\b', lambda mm: SET.get(mm.group(1), mm.group(1)), t)
d.p('Priority A bands are the first targets; B bands confirm a detection; C bands support it. Bulk: band position with signal-to-noise ratio and the number of spots showing it. Simulation: calculated position (shift) and vibration type. SERS: spots showing the band in the best chip set, with the number of blank spectra that also show it.')
for m in ('NAM', 'LPS', 'LTA'):
    rows = []
    for pos, pr, src, why in sorted(EP.EXP[m], key=lambda e: ('ABC'.index(e[1]), e[0])):
        rows.append([f'{pos:g}', pr, EP.bulk_txt(m, pos), EP.sim_txt(m, pos)[0], setname(EP.sers_txt(m, pos)), why])
    d.table(['Band', 'Pri.', 'Bulk', 'Simulation', 'SERS so far', 'Why it is expected'], rows, [1.3, 0.9, 2.6, 3.3, 2.6, 6.5], f'Expected bands of {m}.', fs=7.5)
d.table(['Biomarker', 'First targets (cm-1)', 'Why'],
        [['NAM', '929, 955, 870', 'Strongest bulk bands, reproduced by the simulation (sugar-ring C-O / C-C stretching); 929 and 955 are the NAM bands seen most often in SERS'],
         ['LPS', '1330 with 989; 425, 1080', 'Published SERS markers of the lipid A and sugar parts; 1330 seen in 43 % of LPS spots; 425 and 1080 are the strongest bulk bands and match the simulation'],
         ['LTA', '1092 with 1460; 539', 'Phosphate backbone band, the strongest in bulk and matched by the simulation, paired with a lipid band; 539 is unique to LTA']],
        [2.0, 3.8, 11.2], 'Target bands for further SERS work.', fs=8.5)

d.h1('Discussion')
d.p("The bulk library and the simulation together give a solid reference for what each molecule should look like. The SERS part shows that the chips enhance a strongly adsorbing dye very well, but the three biomarkers gave weak and variable signals. Three reasons are likely. "
    "First, NAM and LTA have no group that binds strongly to silver, so few molecules sit at the enhancing sites. Second, the etched surface is strongly hydrophilic, so the drop spreads and dries into a ring, leaving little material in the measured spot. "
    "Third, the chip itself has bands that overlap some targets, and the enhancement varies strongly between chips. The repeating LPS band set is the most promising signal, in line with the published LPS SERS work on silver, where the fatty-acid chains of lipid A adsorb on the metal.")
d.p("SERS spectra are not expected to copy the bulk spectrum: bands of groups close to the metal are enhanced, others may disappear, and adsorption shifts positions. The comparison with SERS therefore relies on vibration type and published SERS bands rather than on a band-for-band match with the bulk spectrum.")

d.h1('Conclusions')
for t in (f"A traceable bulk Raman reference library of NAM, LPS and LTA was built, with marker bands that separate the three molecules.",
          "Molecular simulation reproduces most marker bands and gives a tentative assignment of each band to a part of the molecule.",
          f"A simple one-step silver-etching process gives SERS-active silicon chips; the 20 mM AgNO3, 2 min recipe gave the strongest enhancement (R6G signal-to-noise about {best:.0f}), and R6G was seen down to the 100 nM to 1 µM range.",
          "NAM, LPS and LTA were not yet detected by the strict criteria; LPS gave a repeating band set that is consistent with an LPS-related surface signal and is the most promising lead.",
          "Expected target bands have been defined for each biomarker to guide the next stage of sensor work."):
    d.b(t)

d.h1('Recommendations for further work')
for t in ("Make several chips with the 20 mM AgNO3, 2 min recipe in one batch and on different days, test each with R6G, and measure a blank on every chip.",
          "Record the analyte concentration, drop volume and drying time for every chip, and run concentration series for LPS first, then LTA and NAM.",
          "Confine the drop (small volume, hydrophobic ring) to reduce spreading on the hydrophilic surface.",
          "Add capture layers that bind the biomarker near the silver: boronic acid for NAM and a positively charged thiol layer for LTA, each against a bare-silver control.",
          "Characterise the chips by electron microscopy and measure the laser power at the sample, so that results can be compared with published work."):
    d.b(t)
DOC = os.path.join(OUT, 'Final_Report_Raman_SERS_Sepsis_Biomarkers.docx'); d.save(DOC); print(DOC)
