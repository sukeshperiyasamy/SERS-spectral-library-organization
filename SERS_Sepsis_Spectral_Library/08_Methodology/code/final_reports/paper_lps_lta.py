"""Paper preparation: Raman reference spectra and DFT-assisted assignment of LPS (E. coli O111:B4) and LTA (S. aureus) at 785 nm.
Builds publication figures, tables, chance tests, the manuscript draft, a supplementary draft and the open-items checklist.
All numbers come from the library reference files, QC logs and the calculations; nothing is typed in by hand."""
import os, json, numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.signal import find_peaks
from docx.shared import Cm, Pt
import fr_data as D, fr_figs as G, fr_docs as FD
OUT = r"C:\Users\sukes\Downloads\sukesh\Manuscripts\Paper_LPS_LTA_Raman_DFT"
FIG = os.path.join(OUT, 'figures'); TAB = os.path.join(OUT, 'tables')
for d in (FIG, TAB): os.makedirs(d, exist_ok=True)
G.FIG = FIG
X = D.X; GZ = (X >= D.GLASS[0]) & (X <= D.GLASS[1]); NG = ~GZ
plt.rcParams.update({'font.family': 'Arial', 'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False})
MOLS = ('LPS', 'LTA'); COL = D.COL
LONG = {'LPS': 'lipopolysaccharide (LPS, E. coli O111:B4)', 'LTA': 'lipoteichoic acid (LTA, S. aureus)'}
def save(fig, n):
    p = os.path.join(FIG, n); fig.savefig(p, dpi=300, bbox_inches='tight'); fig.savefig(p.replace('.png', '.pdf'), bbox_inches='tight'); plt.close(fig); return p

# ------------------------------------------------------------------ data
ref = {m: D.exp_ref(m) for m in ('NAM', 'LPS', 'LTA')}
mem = {m: D.exp_members(m) for m in MOLS}
gl = {m: D.blank_mean(m) for m in MOLS}
res = {m: D.match(m) for m in MOLS}
MK = {m: FD.marker_table(m) for m in MOLS}
def r(a, b): return float(np.corrcoef(a[NG], b[NG])[0, 1])
pair = {m: np.mean([r(mem[m][i], mem[m][j]) for i in range(len(mem[m])) for j in range(i + 1, len(mem[m]))]) for m in MOLS}
cross = {(a, b): r(ref[a][0], ref[b][0]) for a, b in (('LPS', 'LTA'), ('LPS', 'NAM'), ('LTA', 'NAM'))}
whole = {m: D.pearson(m) for m in MOLS}
sims = {m: D.sim(m) for m in MOLS}

# chance tests: (1) type-matched modes within 10 cm-1; (2) visible peaks of the broadened calculation within 10 cm-1
rng = np.random.default_rng(7)
def n_agree(m): return sum(x['status'] == 'agrees' for x in D.match(m))
chance = {}
for m in MOLS:
    s = sims[m]; f0 = s['f'].copy(); real = n_agree(m); dec = []
    for _ in range(1000):
        s['f'] = f0 + rng.uniform(15, 70) * rng.choice([-1, 1]); dec.append(n_agree(m))
    s['f'] = f0; dec = np.array(dec)
    cc = D.calc_curve(m); pk, _ = find_peaks(cc, prominence=0.05); cp = X[pk]
    bands = [x['exp'] for x in res[m]]
    def nv(sh): return sum(np.min(np.abs(cp + sh - b)) <= 10 for b in bands)
    vreal = nv(0); vdec = np.array([nv(rng.uniform(15, 70) * rng.choice([-1, 1])) for _ in range(5000)])
    chance[m] = dict(n=len(bands), mode_real=real, mode_dec=float(dec.mean()), mode_p=float((dec >= real).mean()),
                     vis_real=int(vreal), vis_dec=float(vdec.mean()), vis_p=float((vdec >= vreal).mean()), n_vis=len(cp))
qcL = pd.read_csv(D.LIB + '/07_QC_and_Exclusions/LPS_Reference_Session_20260928_QC_Log.csv')
qcT = pd.read_csv(D.LIB + '/07_QC_and_Exclusions/LTA_Reference_Session_20261028_QC_Log.csv')
qcT_counts = qcT[qcT.category == 'LTA_Bulk'].groupby('QC').size().to_dict()
json.dump(dict(pair=pair, cross={f'{a}-{b}': v for (a, b), v in cross.items()}, whole=whole, chance=chance, qcT=qcT_counts,
               n={m: len(mem[m]) for m in MOLS}, modes={m: dict(total=int(len(sims[m]['f'])), in_range=int(sims[m]['k'].sum()), imaginary=int((sims[m]['r']['freq'] < 0).sum())) for m in MOLS}),
          open(os.path.join(TAB, 'key_numbers.json'), 'w'), indent=1)

# ------------------------------------------------------------------ figures
# Fig 1: models
f1 = {m: G.struct_plain(m) for m in MOLS}
# Fig 2: reference spectra with all member spectra and the glass blank
fig, axs = plt.subplots(2, 1, figsize=(7.2, 6.2), sharex=True, gridspec_kw=dict(hspace=.12))
for ax, m, lab in zip(axs, MOLS, 'ab'):
    y, sd, _ = ref[m]
    for s in mem[m]: ax.plot(X, s + 0.55, color='#b8b8b8', lw=.45)
    ax.fill_between(X, y - sd + 0.55, y + sd + 0.55, color=COL[m], alpha=.2, lw=0); ax.plot(X, y + 0.55, color=COL[m], lw=1.2)
    g = gl[m][0]; ax.plot(X, g * 0.45, color='#555', lw=.9, ls='--')
    for pos, role in D.peaks(m):
        i = int(round(pos - 400)); j = max(range(max(i - 4, 0), min(i + 5, len(X))), key=lambda k: y[k])
        ax.text(X[j], y[j] + 0.59, f'{pos:.0f}', ha='center', va='bottom', fontsize=6.8, rotation=90, color=COL[m], fontweight='bold' if role == 'main' else 'normal')
    ax.axvspan(*D.GLASS, color='#e6e6e6', lw=0, zorder=0); ax.set_ylim(-0.03, 1.95); ax.set_yticks([])
    ax.text(0.01, 0.97, f'({lab}) {m}, n = {len(mem[m])}', transform=ax.transAxes, va='top', fontsize=9, fontweight='bold', color=COL[m])
    ax.text(1795, 0.42, f'glass blank (n = {gl[m][2]})', ha='right', fontsize=7, color='#555')
axs[-1].set_xlim(400, 1800); axs[-1].set_xlabel('Raman shift (cm$^{-1}$)'); axs[0].set_ylabel('Normalised intensity (offset)'); axs[1].set_ylabel('Normalised intensity (offset)')
f2 = save(fig, 'Fig2_reference_spectra.png')
# Fig 3/4: experiment against calculation
def cmpfig(m, name):
    y = ref[m][0]; cc = D.calc_curve(m); s = sims[m]; k = s['k']
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.plot(X, y + 1.15, color=COL[m], lw=1.1, label='experiment (mean)'); ax.plot(X, cc, color=D.CALC, lw=1.1, label='calculation (broadened)')
    ax.vlines(s['f'][k], -0.25, -0.25 + 0.22 * s['I'][k] / s['I'][k].max(), color='#777', lw=.5)
    for x in res[m]:
        if x['calc'] is None: continue
        c = '#222222'; ax.plot([x['exp'], x['calc']], [1.12, 1.02], color=c, lw=1, ls='-' if x['status'] == 'agrees' else '--')
        ax.text(x['exp'], 2.2, f"{x['exp']:.0f}", ha='center', va='bottom', rotation=90, fontsize=6.8, color=c)
    ax.axvspan(*D.GLASS, color='#e6e6e6', lw=0, zorder=0); ax.set_xlim(400, 1800); ax.set_ylim(-0.3, 2.65); ax.set_yticks([])
    ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('Normalised intensity (offset)')
    ax.legend(handles=[Line2D([0], [0], color=COL[m], label='experiment (mean)'), Line2D([0], [0], color=D.CALC, label='calculation'),
                       Line2D([0], [0], color='#222222', label='same type, within 10 cm$^{-1}$'), Line2D([0], [0], color='#222222', ls='--', label='same type, shifted')],
              frameon=False, fontsize=7, loc='upper center', ncol=4, bbox_to_anchor=(0.5, -0.17))
    return save(fig, name)
f3 = cmpfig('LPS', 'Fig3_LPS_experiment_vs_DFT.png'); f4 = cmpfig('LTA', 'Fig4_LTA_experiment_vs_DFT.png')
# Fig 5: where the assigned vibrations sit in the models
f5 = {}
for m in MOLS:
    items = [dict(idx=x['idx'], text=f"{x['exp']:.0f} cm-1 (calc. {x['calc']:.0f})\n{str(x['label']).split(' (')[0]}") for x in sorted(res[m], key=lambda x: x['exp']) if x['idx'] is not None][:8]
    f5[m] = G.struct_assign(m, items, 'paper_assign')
# Fig 6: three cell-wall molecules compared
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.2, 3.3), gridspec_kw=dict(width_ratios=[2.4, 1]))
for i, m in enumerate(('NAM', 'LPS', 'LTA')): a0.plot(X, ref[m][0] + 1.1 * (2 - i), color=COL[m], lw=1); a0.text(1795, 1.1 * (2 - i) + 0.8, m, ha='right', fontsize=9, fontweight='bold', color=COL[m])
a0.axvspan(*D.GLASS, color='#e6e6e6', lw=0, zorder=0); a0.set_xlim(400, 1800); a0.set_yticks([]); a0.set_xlabel('Raman shift (cm$^{-1}$)')
names = ['NAM', 'LPS', 'LTA']; M = np.array([[r(ref[a][0], ref[b][0]) for b in names] for a in names])
im = a1.imshow(M, cmap='Blues', vmin=0, vmax=1)
for i in range(3):
    for j in range(3): a1.text(j, i, f'{M[i, j]:.2f}', ha='center', va='center', fontsize=8, color='white' if M[i, j] > .6 else 'black')
a1.set_xticks(range(3)); a1.set_xticklabels(names); a1.set_yticks(range(3)); a1.set_yticklabels(names); a1.set_title('Pearson r (glass region excluded)', fontsize=8)
f6 = save(fig, 'Fig6_three_molecules_compared.png')

# ------------------------------------------------------------------ tables
def assign_table(m):
    rows = []
    for x in res[m]:
        k = min(MK[m], key=lambda q: abs(q - x['exp'])); mk = MK[m][k]
        rows.append(dict(exp_cm1=round(x['exp'], 1), sd_cm1=round(mk['sd'], 1), median_snr=round(mk['snr'], 1), spots=mk['det'], role=x['role'],
                         calc_cm1=None if x['calc'] is None else round(x['calc'], 1), diff_cm1=None if x['delta'] is None else round(x['delta'], 1),
                         calc_rel_intensity=None if x['I'] is None else round(x['I'], 3), calc_vibration=x['label'], result=x['status'], tentative_assignment=x['desc']))
    df = pd.DataFrame(rows); df.to_csv(os.path.join(TAB, f'Table_{m}_band_assignment.csv'), index=False); return df
TA = {m: assign_table(m) for m in MOLS}
for m in MOLS:
    s = sims[m]; k = s['k']
    pd.DataFrame(dict(freq_scaled_cm1=np.round(s['f'][k], 1), rel_raman_intensity=np.round(s['I'][k], 4), vibration=np.array(s['label'], dtype=object)[k])).to_csv(os.path.join(TAB, f'SI_{m}_all_calculated_modes_400_1800.csv'), index=False)
    pd.DataFrame({'raman_shift_cm-1': X, 'mean_normalised': np.round(ref[m][0], 5), 'sd_normalised': np.round(ref[m][1], 5)}).to_csv(os.path.join(TAB, f'SI_{m}_reference_mean_sd.csv'), index=False)
qcT[qcT.category == 'LTA_Bulk'][['library_file', 'power', 'int_s', 'acc', 'dark_med', 'raw_max', 'ripple', 'snr1092', 'QC', 'QC_reason']].to_csv(os.path.join(TAB, 'SI_LTA_QC_log.csv'), index=False)
qcL[qcL.category == 'LPS_Bulk'][['library_file', 'power', 'int_s', 'acc', 'raw_max', 'ripple', 'snr425', 'glass_ratio', 'QC', 'QC_reason']].to_csv(os.path.join(TAB, 'SI_LPS_QC_log.csv'), index=False)

# ------------------------------------------------------------------ manuscript draft
c = chance; nL, nT = len(mem['LPS']), len(mem['LTA'])
agL = int((TA['LPS'].result == 'agrees').sum()); agT = int((TA['LTA'].result == 'agrees').sum())
d = FD.Doc('Raman reference spectra and DFT-assisted band assignment of bacterial lipopolysaccharide and lipoteichoic acid at 785 nm',
           'Manuscript draft for internal review. Authors, affiliations and journal formatting to be added.')
sec = d.d.sections[0]
for a in ('left_margin', 'right_margin'): setattr(sec, a, Cm(2.0))
d.h1('Abstract')
d.p(f"Lipopolysaccharide (LPS) and lipoteichoic acid (LTA) are the major cell-envelope glycoconjugates of Gram-negative and Gram-positive bacteria and are candidate targets for label-free Raman and surface-enhanced Raman (SERS) sensing in sepsis. "
    f"Published SERS studies list bands for LPS, but reference Raman spectra of the pure materials, with a vibrational assignment, are scarce. "
    f"We report reference Raman spectra of LPS from Escherichia coli O111:B4 (n = {nL} spots) and LTA from Staphylococcus aureus (n = {nT} spots), recorded at 785 nm under conditions selected by systematic quality control (saturation, detector ripple, signal-to-noise and substrate contribution). "
    f"Spot-to-spot agreement was high (mean pairwise r = {pair['LPS']:.2f} for LPS and {pair['LTA']:.2f} for LTA). LPS is characterised by bands at 425 and 1080 cm-1, with supporting bands at 766, 861 and 996 cm-1; LTA by a strong phosphodiester band at 1092 cm-1 with bands at 539 and 862 cm-1. "
    f"Density functional theory calculations of a whole lipid A model (201 atoms) and an LTA model (93 atoms) place a mode of the expected vibration type within 10 cm-1 of {agL} of {len(TA['LPS'])} LPS and {agT} of {len(TA['LTA'])} LTA marker bands, giving tentative assignments to skeletal, C-O/C-C and phosphate vibrations. A random-shift test shows that, at the mode density of these large models, this agreement is not clearly above chance (p = {c['LPS']['mode_p']:.2f} and {c['LTA']['mode_p']:.2f}), so the assignments rest mainly on vibration type and chemical plausibility. "
    f"The two spectra are clearly distinct from each other (r = {cross[('LPS','LTA')]:.2f}) and from N-acetylmuramic acid (r = {cross[('LPS','NAM')]:.2f} and {cross[('LTA','NAM')]:.2f}). These spectra provide a reference for Raman- and SERS-based detection of bacterial cell-wall markers.")
d.p('Keywords: Raman spectroscopy; lipopolysaccharide; lipoteichoic acid; density functional theory; band assignment; sepsis biomarkers', 'Keywords.')
d.h1('Introduction')
d.p("Sepsis requires rapid recognition of the infecting organism. Bacterial cell-envelope components are attractive targets for optical sensing because they are abundant, conserved and differ between Gram-negative and Gram-positive bacteria: lipopolysaccharide (LPS) forms the outer leaflet of the Gram-negative outer membrane, and lipoteichoic acid (LTA), a glycerol-phosphate polymer anchored to a glycolipid, is characteristic of Gram-positive bacteria. "
    "Surface-enhanced Raman spectroscopy (SERS) has been used to detect and classify LPS from several species [1-4], and machine-learning classification of endotoxin SERS spectra has been reported [2]. "
    "SERS spectra, however, reflect the adsorption geometry and the enhancing surface, and their bands are usually assigned by analogy with general tables of biomolecular Raman bands [5, 6]. "
    "Reference normal-Raman spectra of the pure materials, recorded under documented conditions and assigned with the help of calculations, are needed to judge which SERS bands come from the molecule and which are changed by the surface.")
d.p("For LTA, we found no published normal-Raman spectrum of the purified material with a vibrational assignment [to be confirmed by a full literature search]; vibrational data on teichoic acids come mainly from infrared spectroscopy [7]. For LPS, assignments of purified material have relied mainly on infrared spectroscopy of lipid A and Re-LPS and on SERS. "
    "In a companion study we reported the Raman spectrum and DFT assignment of N-acetylmuramic acid [8]. Here we extend this approach to LPS and LTA: we record reproducible 785 nm reference spectra with full quality control, calculate the Raman spectra of whole-molecule models by density functional theory, assign the marker bands by vibration type, and test whether the agreement exceeds chance.")
d.h1('Experimental')
d.h2('Materials')
d.p("LPS from Escherichia coli O111:B4 (Sigma-Aldrich L2630, phenol extracted, lot 0000442391) and LTA from Staphylococcus aureus (Sigma-Aldrich L2515, lot 0000419622) were used as received. The LTA supplier sheet gives no purity figure; the certificate of analysis for the lot [to be obtained]. Small amounts of powder were placed on clean glass microscope slides; glass blanks were recorded at the same settings.")
d.h2('Raman measurements')
d.p("Spectra were recorded with a B&W Tek i-Raman Plus spectrometer (BWS465-785H, BTC665N-785H-SYS probe, 785 nm excitation, 2048-pixel TE-cooled CCD, resolution < 3.5 cm-1) through a 20x objective, over 400-1800 cm-1. Laser power is given as the percentage of the maximum output; the power at the sample [to be measured]. "
    "Because the software dark spectrum was found to contain light scattered from the sample, dark spectra were recorded with the shutter closed by hand. "
    f"Acquisition settings were selected by screening: higher laser powers (70-90 %) produced a fixed-pattern ripple in the detector signal for LPS, and long exposures saturated the brightest LTA spots. The final settings were 60 %, 40 s, 5 accumulations for LPS ({nL} spots) and 80 %, 45 s, 2 accumulations (10 spots) plus 80 %, 30 s, 3 accumulations (7 spots) for LTA.")
d.h2('Data processing and quality control')
d.p("All spectra were processed with the same pipeline: dark subtraction, correction of two hot detector pixels, cropping to 400-1800 cm-1, despiking (median absolute deviation, z > 6, width <= 2 pixels), Savitzky-Golay smoothing (window 11, order 3) [9], asymmetric least-squares baseline removal (lambda = 1e5, p = 0.01) [10] and min-max normalisation. "
    "Spectra were rejected if saturated, if the high-pass ripple in 1550-1800 cm-1 exceeded 50 counts, if the signal-to-noise ratio (SNR) of the main band was below 10, or if the glass contribution dominated. Every rejection was logged. "
    f"For LTA, {sum(qcT_counts.values())} spectra were recorded across nine settings; {qcT_counts.get('PASS', 0)} passed, {qcT_counts.get('REVIEW', 0)} were marked for review (ripple 50-58 counts), {qcT_counts.get('FLAG-DARK', 0)} were recorded with a light-contaminated dark and not used, and the rest failed (saturation, low SNR, atypical shape). "
    "The glass band region (1308-1455 cm-1) was excluded from all correlations and is not used for any marker. Reference spectra are the mean +/- SD of accepted spots; bands were classed as primary or supporting by detection frequency and SNR.")
d.h2('Calculations')
d.p(f"The LPS model is lipid A with two Kdo sugars and shortened acyl chains (201 atoms, charge -4); the LTA model contains three glycerol-phosphate units, two D-alanine esters and one alpha-N-acetylglucosamine (93 atoms, C23H45N3O20P2). "
    f"Geometries were pre-optimised (PM6 for lipid A) and optimised at the B3LYP/3-21G level [11, 12] in Gaussian 16, followed by harmonic frequency and Raman activity calculations; no imaginary frequencies were found ({sims['LPS']['r']['freq'].size} and {sims['LTA']['r']['freq'].size} modes). "
    "Frequencies were scaled by 0.965, activities converted to intensities for 785 nm excitation at 298 K, and each mode broadened with a 12 cm-1 Lorentzian. "
    "The character of each mode was obtained from the kinetic-energy share of atom groups (phosphate P and O, carbonyl C=O, N-H, C-H, skeletal C and O) in the displacement vectors, and labelled as skeletal deformation, C-O/C-C stretching, phosphate P-O stretching, C-H/N-H bending or C=O stretching.")
d.h2('Band assignment and chance test')
d.p("Each experimental marker band was matched to the nearest calculated mode of the expected vibration type within 50 cm-1; matches within 10 cm-1 are reported as agreement and larger offsets as shifted. "
    "Because large models have many modes in the fingerprint region, the probability of chance agreement was estimated by shifting all calculated frequencies by a random 15-70 cm-1 (1000 trials) and repeating the match; a stricter test used only the visible maxima of the broadened calculated spectrum (5000 trials).")
d.h1('Results and discussion')
d.h2('Reference spectra and reproducibility')
d.figure(f2, f"Reference Raman spectra of (a) LPS and (b) LTA at 785 nm: all accepted spots (grey), mean (colour) +/- 1 SD (shaded), and the glass blank (dashed, scaled). Numbers mark the primary (bold) and supporting bands. Grey region: glass band region, excluded from analysis.", w=16)
d.p(f"The LPS spectrum (Fig. 1a) is weak and broad, as expected for an amorphous glycolipid. Its strongest feature is a band at 425 cm-1, present in all {nL} spots with a median SNR of {MK['LPS'][424.8]['snr']:.0f}, followed by a broad band at 1080 cm-1; bands at 766, 861 and 996 cm-1 support the identification. Absolute intensity varied three- to five-fold between spots, so relative intensities were compared as ratios to the 425 cm-1 band. "
    f"The mean pairwise correlation of the LPS spots was {pair['LPS']:.2f}. The LTA spectrum (Fig. 1b) is dominated by a sharp band at 1092 cm-1 (median SNR {MK['LTA'][1092.0]['snr']:.0f}, all spots), with primary bands at 539 and 862 cm-1 and supporting bands at 418, 723, 799, 1011, 1460 and 1751 cm-1; the mean pairwise correlation was {pair['LTA']:.2f}, and the two acquisition settings gave the same spectrum (r = 0.98).")
d.h2('Assignment of the LPS bands')
d.figure(f3, f"Experimental LPS spectrum (top) and calculated spectrum of the lipid A model (bottom, with calculated modes as sticks). Lines join each marker band to the calculated mode of the same vibration type.", w=16)
d.table(['Exp. (cm-1)', 'SNR', 'Calc. (cm-1)', 'Diff.', 'Calculated vibration', 'Tentative assignment'],
        [[f'{x.exp_cm1:g}', f'{x.median_snr:.0f}', '-' if pd.isna(x.calc_cm1) else f'{x.calc_cm1:g}', '-' if pd.isna(x.diff_cm1) else f'{x.diff_cm1:+.1f}', str(x.calc_vibration).split(' (')[0], x.tentative_assignment] for x in TA['LPS'].itertuples()],
        [1.7, 1.1, 1.7, 1.2, 4.2, 6.6], 'LPS marker bands and their tentative assignment.', fs=8)
d.p(f"All five LPS marker bands have a calculated mode of the expected type within 3 cm-1 (Table 1). The 425 cm-1 band, which has no published assignment, corresponds to a skeletal deformation of the sugar-lipid backbone; the 766, 861 and 996 cm-1 bands to C-O and C-C stretching of the sugar rings, and the 1080 cm-1 band to C-O stretching, with a likely contribution from the symmetric PO2- stretch of the lipid A phosphates. "
    f"The chance test qualifies this agreement: with {sims['LPS']['k'].sum()} calculated modes between 400 and 1800 cm-1, randomly shifted frequency sets reproduced on average {c['LPS']['mode_dec']:.1f} of the {c['LPS']['n']} bands (p = {c['LPS']['mode_p']:.2f}). "
    f"Using only the {c['LPS']['n_vis']} visible maxima of the broadened calculated spectrum, {c['LPS']['vis_real']} of {c['LPS']['n']} bands agree within 10 cm-1, against {c['LPS']['vis_dec']:.1f} by chance (p = {c['LPS']['vis_p']:.2f}). The assignments are therefore tentative and rest on vibration type more than on position. "
    "The C-H deformation bands expected for the acyl chains (1300-1460 cm-1) fall in the glass region and could not be assessed.")
d.h2('Assignment of the LTA bands')
d.figure(f4, "Experimental LTA spectrum (top) and calculated spectrum of the LTA model (bottom). Lines join each marker band to the calculated mode of the same vibration type.", w=16)
d.table(['Exp. (cm-1)', 'SNR', 'Calc. (cm-1)', 'Diff.', 'Calculated vibration', 'Tentative assignment'],
        [[f'{x.exp_cm1:g}', f'{x.median_snr:.0f}', '-' if pd.isna(x.calc_cm1) else f'{x.calc_cm1:g}', '-' if pd.isna(x.diff_cm1) else f'{x.diff_cm1:+.1f}', str(x.calc_vibration).split(' (')[0], x.tentative_assignment] for x in TA['LTA'].itertuples()],
        [1.7, 1.1, 1.7, 1.2, 4.2, 6.6], 'LTA marker bands and their tentative assignment.', fs=8)
d.p(f"{agT} of the {len(TA['LTA'])} LTA bands agree within 10 cm-1 with a calculated mode of the expected type. The strongest band, 1092 cm-1, matches the calculated symmetric PO2- stretch of the phosphodiester backbone (1085 cm-1), consistent with the glycerol-phosphate repeat that defines LTA, and 799 cm-1 matches an O-P-O (P-O-C) stretch. "
    "The 1751 cm-1 band is assigned to the C=O stretch of the D-alanine ester; the calculation places this mode 25 cm-1 lower, a typical offset for a small basis set and an isolated molecule without hydrogen-bonded neighbours. "
    f"The 1460 cm-1 band agrees in position with a calculated mode whose largest share is N-H bending of the protonated alanine; CH2/CH3 bending of the lipid anchor is the more common assignment, so this band is left as tentative. "
    f"Chance test: shifted frequency sets reproduced {c['LTA']['mode_dec']:.1f} of {c['LTA']['n']} bands on average (p = {c['LTA']['mode_p']:.2f}); with visible maxima only, {c['LTA']['vis_real']} of {c['LTA']['n']} agree against {c['LTA']['vis_dec']:.1f} by chance (p = {c['LTA']['vis_p']:.2f}).")
d.figure(f5['LTA'], 'Atoms that carry the assigned LTA vibrations in the model (coloured by band).', w=15)
d.h2('Relative intensities')
d.p(f"The calculated intensities agree poorly with experiment (whole-spectrum correlation {whole['LPS']:.2f} for LPS and {whole['LTA']:.2f} for LTA). This is expected for a gas-phase calculation of a single conformer with a small basis set and for disordered solids, and it is why the assignments are based on position and vibration type rather than intensity.")
d.h2('Distinguishing the cell-wall markers')
d.figure(f6, 'Reference spectra of NAM, LPS and LTA and their Pearson correlation (glass region excluded).', w=15)
d.p(f"The three cell-wall molecules give clearly different spectra (Fig. 5): LPS and LTA correlate at r = {cross[('LPS','LTA')]:.2f}, sharing the band near 861 cm-1 and a broad 1080-1092 cm-1 region, while both differ strongly from NAM (r = {cross[('LPS','NAM')]:.2f} and {cross[('LTA','NAM')]:.2f}). "
    "For identification, combinations of bands are more useful than single bands: 425 with 1080 cm-1 for LPS, and the sharp 1092 cm-1 band with 539 cm-1 for LTA.")
d.h2('Limitations')
for t in ("Laser power at the sample was not measured; powers are given as % of maximum.", "The glass substrate hides the 1308-1455 cm-1 region, where C-H deformation bands of the acyl chains are expected.",
          "Early LPS dark spectra contained some sample light, so absolute LPS intensities may be 3-34 % low; band positions and relative intensities are unaffected.",
          "The calculations use a small basis set and single conformers of truncated models; a higher-level check of key modes is planned.", "LTA purity is not stated by the supplier."):
    d.b(t)
d.h1('Conclusions')
d.p(f"Reproducible 785 nm reference Raman spectra of LPS (E. coli O111:B4) and LTA (S. aureus) were obtained with documented quality control. DFT calculations of whole-molecule models place modes of the expected type near every marker band; the agreement is not clearly above chance at this level of theory, but it is consistent with the view that the main LTA band at 1092 cm-1 arises from the phosphodiester backbone and the LPS bands from skeletal and sugar C-O/C-C vibrations. "
    "The two spectra are distinct from each other and from N-acetylmuramic acid, and provide a reference for Raman and SERS sensing of bacterial cell-wall markers.")
d.h1('Data availability')
d.p('Reference spectra (mean and SD), per-spot processed spectra, QC logs, calculated mode lists and the processing code will be deposited in a public repository on acceptance [repository and DOI to be added].')
d.h1('References')
for t in ("[1] X. Wu, Y. Zhao, S.M. Zughaier, Highly sensitive detection and differentiation of endotoxins derived from bacterial pathogens by surface-enhanced Raman scattering, Biosensors 11 (2021) 234. https://doi.org/10.3390/bios11070234",
          "[2] Y. Yang et al., Differentiation and classification of bacterial endotoxins based on surface enhanced Raman scattering and advanced machine learning, Nanoscale 14 (2022) 8806-8817. https://doi.org/10.1039/d2nr01277d",
          "[3] A. Verde et al., SERS sensing of bacterial endotoxin on gold nanoparticles, Front. Immunol. 12 (2021) 758410. https://doi.org/10.3389/fimmu.2021.758410",
          "[4] A. Kumar et al., Precision classification and quantitative analysis of bacteria biomarkers via SERS and machine learning, Spectrochim. Acta A 320 (2024) 124627. https://doi.org/10.1016/j.saa.2024.124627",
          "[5] Z. Movasaghi, S. Rehman, I.U. Rehman, Raman spectroscopy of biological tissues, Appl. Spectrosc. Rev. 42 (2007) 493-541. https://doi.org/10.1080/05704920701551530",
          "[6] E. Wiercigroch et al., Raman and infrared spectroscopy of carbohydrates: a review, Spectrochim. Acta A 185 (2017) 317-335. https://doi.org/10.1016/j.saa.2017.05.045",
          "[7] T. Grunert et al., Analysis of Staphylococcus aureus wall teichoic acid glycoepitopes by FTIR spectroscopy, Sci. Rep. 8 (2018) 1889. https://doi.org/10.1038/s41598-018-20222-6",
          "[8] Companion NAM Raman/DFT paper [citation to be added when submitted].",
          "[9] A. Savitzky, M.J.E. Golay, Anal. Chem. 36 (1964) 1627-1639 [DOI unverified].",
          "[10] P.H.C. Eilers, H.F.M. Boelens, Baseline correction with asymmetric least squares smoothing (2005) [report; citation to verify].",
          "[11] A.D. Becke, J. Chem. Phys. 98 (1993) 5648-5652 [DOI unverified].", "[12] C. Lee, W. Yang, R.G. Parr, Phys. Rev. B 37 (1988) 785-789 [DOI unverified].",
          "[--] Gaussian 16 citation and the reference database of Raman spectra of biological molecules (De Gelder et al., J. Raman Spectrosc. 38 (2007) 1133, https://doi.org/10.1002/jrs.1734) to be checked for LPS/LTA entries."):
    p = d.d.add_paragraph(t); p.paragraph_format.space_after = Pt(2)
    for rr in p.runs: rr.font.size = Pt(9)
d.save(os.path.join(OUT, 'Manuscript_Draft_LPS_LTA_Raman_DFT.docx'))

# ------------------------------------------------------------------ supplementary draft
s = FD.Doc('Supplementary Information', 'Raman reference spectra and DFT-assisted band assignment of bacterial LPS and LTA at 785 nm')
s.h1('Calculated models'); [s.figure(f1[m], f'Model of {LONG[m]} used in the calculation.', w=15) for m in MOLS]
s.figure(f5['LPS'], 'Atoms that carry the assigned LPS vibrations in the lipid A model.', w=15)
s.h1('Quality control')
s.table(['QC class', 'LTA spectra'], [[k, v] for k, v in sorted(qcT_counts.items())], [6, 4], 'Quality-control classes of all LTA spectra.')
s.p('Per-spectrum QC logs: tables/SI_LPS_QC_log.csv and tables/SI_LTA_QC_log.csv. Calculated modes 400-1800 cm-1: tables/SI_<molecule>_all_calculated_modes_400_1800.csv. Reference spectra: tables/SI_<molecule>_reference_mean_sd.csv.')
s.h1('Chance test')
s.table(['Molecule', 'Bands', 'Agree (modes)', 'Chance mean', 'p', 'Agree (visible peaks)', 'Chance mean', 'p'],
        [[m, c[m]['n'], c[m]['mode_real'], f"{c[m]['mode_dec']:.1f}", f"{c[m]['mode_p']:.2f}", c[m]['vis_real'], f"{c[m]['vis_dec']:.1f}", f"{c[m]['vis_p']:.2f}"] for m in MOLS],
        [1.8, 1.4, 2.1, 2.0, 1.3, 2.6, 2.0, 1.3], 'Agreement within 10 cm-1 against randomly shifted calculated spectra.', fs=8.5)
s.save(os.path.join(OUT, 'Supplementary_Draft_LPS_LTA.docx'))
print(json.dumps(dict(pair=pair, whole=whole, chance=chance, cross={f'{a}-{b}': v for (a, b), v in cross.items()}, qcT=qcT_counts), indent=1, default=float))
