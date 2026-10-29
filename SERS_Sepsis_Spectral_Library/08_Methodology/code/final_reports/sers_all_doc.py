"""Word report for all SERS sessions. Run sers_all.py first; numbers come from sers_all_results.pkl."""
import os, pickle, numpy as np, pandas as pd
import fr_docs as FD
OUT = r"C:\Users\sukes\Downloads\sukesh\Final_Submission\09_SERS_All_Sessions"
P = pickle.load(open(os.path.join(OUT, '04_Tables', 'sers_all_results.pkl'), 'rb'))
SESS, IDX, R6, R6S, BD, VD, SI, BGL, F = P['SESS'], P['IDX'], P['R6'], P['R6S'], P['BD'], P['VD'], P['SI'], P['BGL'], P['FIGS']
R2 = '20mMAg-8p6mlHF'
def med(ses, sub, pw, it):
    v = R6[(R6.session == ses) & (R6['sub'] == sub) & (R6.power == pw) & (R6.it == it) & (R6.conc == '')].snr1509
    return float(v.median()), len(v)
def dmy(d): return f'{d[6:]}.{d[4:6]}.{d[:4]}'
s5 = {t: med('S5', f'{R2}-{t}min', 5, 5) for t in (2, 5, 10)}
s7 = med('S7', f'{R2}-2min', 5, 5)
s3 = {c: med('S3', c, 10, 5) for c in sorted(R6[R6.session == 'S3']['sub'].unique())}
s3best = max(s3, key=lambda c: s3[c][0])
s2 = {c: med('S2', c, 10, 10) for c in ('3min', '4min', '5min', '6min')}
conc = R6[(R6.session == 'S4') & R6.conc.str.contains('M')].groupby('conc').agg(n=('snr1509', 'size'), med=('snr1509', 'median'), gate=('gate', 'sum'))
order = ['1nM', '10nM', '100nM', '1uM', '10uM', '1mM']; conc = conc.reindex([c for c in order if c in conc.index])
bare = SI[SI.role == 'bare']; si_all = IDX[(IDX.duplicate_of == '') & (IDX.si_height_counts > 50)].si_peak_cm
nrep = int(BD.reproducible.sum())

d = FD.Doc('SERS Measurements on Etched Silicon: All Sessions', 'R6G, NAM, LTA and LPS on silver-etched silicon chips: data arrangement, processing and analysis')
d.h1('Summary')
d.p(f"This report collects every SERS spectrum measured on the silver-etched silicon chips: {P['n']} files in eight sessions "
    f"({P['n_uniq']} unique spectra; one file was a byte-for-byte duplicate). All files were copied, renamed to one naming rule, "
    "processed with the same pipeline as the bulk library, and tested with the same detection rules. The arrangement of the data is described in Section 3.")
d.b(f"The chips are SERS-active. R6G gave its standard band set in every session where it was measured. The strongest chip was the 20 mM AgNO3 recipe with a 2 min etch: the median SNR of the 1509 cm-1 band was {s5[2][0]:.0f} (n = {s5[2][1]}). The 10 min etch gave {s5[10][0]:.0f} and the 5 min etch {s5[5][0]:.0f}, at the same settings.", 'Substrate activity.')
d.b(f"Chips made with 6 mg AgNO3 and 5 or 10 mL HF gave a much weaker R6G signal: a median 1509 cm-1 SNR of 0 to 31 at power 10. The best of the eight such chips was the 6 min etch with 10 mL HF.", 'Recipe effect.')
d.b(f"A second 2 min chip made with the 20 mM recipe gave a median SNR of {s7[0]:.0f} (n = {s7[1]}), about {s5[2][0]/s7[0]:.0f} times below the first. Chip-to-chip reproducibility is therefore not yet established.", 'Reproducibility.')
d.b("None of the three biomarkers met the detection rule in any session. NAM was measured in five sessions, LTA in two and LPS in one. The verdict was NOT DETECTED in every session that had a blank. The one session without a blank is INCONCLUSIVE.", 'Biomarkers.')
d.b("The etched chips without analyte show their own recurring bands, near 963, 1393, 855, 1006, 1132 and 1237 cm-1. Some of these lie close to LTA and LPS target bands. A same-session blank is therefore essential before any band is assigned to an analyte.", 'Substrate background.')
d.h1('Data collected')
d.table(['Session', 'Measured', 'What was measured', 'Spectra', 'Blank'],
        [[r.session, dmy(SESS[r.session][0]), r.description, f'{r.unique_spectra}', r.blank_available] for r in P['SES'].itertuples()],
        [1.5, 2.1, 9.4, 1.6, 1.4], 'Sessions. Spectra = unique files; Blank = substrate without analyte measured in the same session.')
d.figure(F['overview'], 'Number of spectra per session, by sample type.')
d.p("Laser power is the software power level recorded in each file header (% of maximum). It was not converted to mW, because the power at the sample was never measured. "
    "Concentrations are given only where the folder or file name states them; otherwise they are listed as Not recorded.")
d.h1('How the data are arranged')
d.p('All material is in Final_Submission/09_SERS_All_Sessions:')
for a, b in (('01_Raw_Spectra_Renamed', 'renamed copies of the raw files, one folder per session (S1_20260606 to S8_20261007). Each copy was checked against the original by MD5. The originals were not changed.'),
             ('02_Processed_Spectra', 'one processed file per spectrum with the same name. The first line gives the original raw path.'),
             ('03_Figures', 'all figures in this report (PNG, 200 dpi).'),
             ('04_Tables', 'SERS_All_Sessions_Workbook.xlsx and CSV copies of its sheets.'),
             ('05_Earlier_Analyses_from_mtp', 'the earlier R6G DFT-validation outputs and the session S4 analysis, copied unchanged from the mtp repository.'),
             ('06_Reports', 'this report.')):
    d.b(b, a + ':')
d.p('File name rule: SERS_<analyte[-concentration]>_<YYYYMMDD>_<substrate code>_P<power level>pct_T<s>s_A<accumulations>_S<nn>.csv, '
    'for example SERS_R6G_20260812_20mMAg-8p6mlHF-2min_P005pct_T5s_A03_S01.csv.')
d.table(['Substrate code', 'Meaning'],
        [['6mgAg-5mlHF', '45 mL DI water + 5 mL HF + 6 mg AgNO3 (handwritten recipe note; sessions S4 and S8)'],
         ['<t>min-<v>mlHF', 'Session S3: <t> min etch with <v> mL HF in the bath (substrates labelled 3m to 6m)'],
         ['3min ... 6min', 'Session S2: substrates labelled 3m to 6m; HF volume not recorded'],
         ['20mMAg-8p6mlHF-<t>min', '0.170 g AgNO3 + 8.6 mL HF made up to 50 mL DI (20 mM AgNO3), etched <t> min (sessions S5, S7)'],
         ['AgNO3-wafer, AgNO3-sub', 'AgNO3/HF-treated substrate; recipe or etch time not recorded'],
         ['PlainSi', 'Plain silicon wafer, not etched'], ['NoSub', 'R6G labelled "raw"; support not recorded (no silicon peak in these spectra)']],
        [4.6, 11.4], 'Substrate codes used in the file names.')
d.table(['Workbook sheet', 'Content'],
        [['README', 'Rules, naming, processing and detection criteria'], ['Sessions', 'One row per session'],
         ['File_Index', 'One row per file: original path, new name, settings, MD5, duplicate flag, silicon peak, noise'],
         ['R6G_Spectra / R6G_Summary', 'R6G bands found in each spectrum; median 1509 cm-1 SNR per chip and setting'],
         ['Biomarker_Bands / Biomarker_Verdicts', 'Each target band per session against the blank; verdict per session'],
         ['Silicon_Reference', 'Silicon peak position and height per session'], ['Substrate_Background', 'Bands that recur in the blanks'],
         ['Mean_Spectra', 'Mean spectrum of every group (signal / silicon peak)'], ['Earlier_R6G_DFT', 'Key numbers of the earlier R6G DFT validation']],
        [5.2, 10.8], 'Sheets of SERS_All_Sessions_Workbook.xlsx.')
d.h1('Processing and detection rules')
for t in ('Pipeline v3 of the bulk library (lib2.process_v3h): dark subtraction, hot-pixel fix at pixels 640 and 700, crop to 400-1800 cm-1, despiking, Savitzky-Golay smoothing (11/3) and ALS baseline. Noise = 1.4826 x MAD of the residual.',
          'A band is present when a peak lies within 5 cm-1 of the target, is at least 3 pixels wide and has SNR >= 3. The width rule rejects single-pixel artefacts, such as the earlier apparent LTA band at 1095 cm-1, which came from pixel 640.',
          'Heights are divided by the silicon peak of the same spectrum, so that spots and settings can be pooled.',
          'A band is reproducible when it is present in at least half of the spots, absent from every same-session blank, and taller than in the blank (one-sided Mann-Whitney test, p < 0.05).',
          'Verdict: NAM needs two reproducible marker bands; LPS needs 989 and 1330 cm-1; LTA needs a phosphate band (1092 or 1225-1250 cm-1) and a lipid band (1131 or 1450 cm-1). If only one of the two is met, the verdict is POSSIBLY DETECTED. A session without a blank is INCONCLUSIVE.',
          'R6G gate: SNR of the 1509 cm-1 band >= 10. Target R6G bands: 612, 774, 1183, 1310, 1362, 1509, 1575 and 1650 cm-1.'):
    d.b(t)
d.h1('Instrument check: the silicon peak')
d.p(f"The silicon peak was found at a median {si_all.median():.0f} cm-1 over all spectra in which it was clear (textbook value about 520.7 cm-1). "
    f"On plain silicon it was at {', '.join(f'{r.si_pos_median:.0f}' for r in bare.itertuples())} cm-1 (sessions {', '.join(bare.session)}). "
    "This agrees with the fixed offset of -2 to -3 cm-1 found earlier, which is why a tolerance of 5 cm-1 is used for every band.")
d.figure(F['silicon'], 'Left: silicon peak position in every spectrum, by session (black bar = median). Right: mean spectrum of plain silicon and of the etched chips without analyte, divided by the silicon peak.')
d.h1('Substrate activity: R6G')
d.figure(F['r6g_spectra'], 'Mean R6G SERS spectrum of each chip group, each scaled to its tallest band. The dotted lines are the standard R6G bands; the measured bands sit 2-4 cm-1 lower because of the calibration offset.')
d.figure(F['r6g_snr'], 'SNR of the 1509 cm-1 band in each spot, by chip. Only spots measured at the same settings are compared within a panel. The red line is the gate (SNR 10). Log scale.')
rows = [['S5', '20 mM AgNO3, 2 min', 'power 5, 5 s, 3 acc', f'{s5[2][0]:.0f}', s5[2][1]], ['S5', '20 mM AgNO3, 10 min', 'power 5, 5 s, 3 acc', f'{s5[10][0]:.0f}', s5[10][1]],
        ['S5', '20 mM AgNO3, 5 min', 'power 5, 5 s, 3 acc', f'{s5[5][0]:.0f}', s5[5][1]], ['S7', '20 mM AgNO3, 2 min (second chip)', 'power 5, 5 s, 3 acc', f'{s7[0]:.0f}', s7[1]]]
rows += [['S3', c.replace('min-', ' min, ').replace('mlHF', ' mL HF'), 'power 10, 5 s, 5 acc', f'{v[0]:.1f}', v[1]] for c, v in sorted(s3.items(), key=lambda kv: -kv[1][0])]
rows += [['S2', c.replace('min', ' min'), 'power 10, 10 s, 3 acc', f'{v[0]:.1f}', v[1]] for c, v in s2.items()]
d.table(['Session', 'Chip', 'Settings', 'Median SNR 1509', 'n'], rows, [1.5, 5.6, 4.0, 2.8, 1.2], 'Median SNR of the R6G 1509 cm-1 band per chip.')
d.p(f"The 20 mM AgNO3 recipe with a 2 min etch gave by far the strongest signal. Its SNR was about {s5[2][0]/s5[10][0]:.1f} times that of the 10 min etch and about {s5[2][0]/max(s5[5][0],1):.0f} times that of the 5 min etch. "
    "The order 2 > 10 > 5 min is not monotonic, which suggests that the etch time is not the only factor. Only one chip was made per condition, so the order may also reflect chip-to-chip variation. "
    f"The 6 mg AgNO3 chips were weaker by more than an order of magnitude. Among them, the 6 min etch with 10 mL HF ({s3[s3best][0]:.0f}) was the only clearly better chip. "
    f"The second 2 min chip (S7) reached {s7[0]:.0f}. It is SERS-active, but well below the first chip.")
if 'r6g_conc' in F:
    d.figure(F['r6g_conc'], 'Session S4: SNR of the 1509 cm-1 band against the R6G concentration given in the file names.')
    d.table(['R6G', 'n', 'Median SNR 1509', 'Spots with SNR >= 10'], [[c, int(r.n), f'{r.med:.1f}', int(r.gate)] for c, r in conc.iterrows()], [3, 1.5, 3.5, 4], 'Session S4: R6G concentration series (power 10, 10 s, 4 acc).')
    d.p("The 1509 cm-1 band passed the gate in some spots down to 100 nM to 1 uM. It was not found at 1 and 10 nM. The signal was lower at 1 mM than at 10 uM. "
        "This is consistent with aggregation or self-quenching at high concentration, but it was not tested. With 2 to 5 spots per concentration, this is an observed lowest concentration, not a limit of detection.")
d.h1('Substrate background')
d.p("Bands that appear in at least a quarter of the chip blanks (spectra without analyte) are listed below. The band near 963 cm-1 is consistent with the second-order silicon phonon band. "
    "The others have no assigned source. They may come from residues of the etch bath, the rinse or the storage, but this was not tested.")
d.table(['Window (cm-1)', 'Median position', 'Blanks with the band'], [[r.window, f'{r.median_pos:.0f}', f'{r.spectra_with_peak} / {r.n_spectra}'] for r in BGL[BGL.role == 'blank'].itertuples()],
        [3.5, 3.5, 4.5], 'Recurring bands in the etched chips without analyte.')
d.p("Several of these bands lie close to biomarker targets: 855 (LPS 861, LTA 861.5), 1006 (LPS 997), 1132 (LTA 1131) and 1237 (LTA 1225-1250). "
    "Without a same-session blank, such bands could be mistaken for the analyte.")
d.h1('Biomarkers: NAM, LTA and LPS')
d.table(['Session', 'Molecule', 'Spots', 'Blank spots', 'Most frequent target band', 'Verdict'],
        [[r.session, r.molecule, r.n, r.n_blank, f'{r.most_frequent_band:g} ({r.most_frequent_frac*100:.0f} %)', r.verdict] for r in VD.itertuples()],
        [1.5, 1.8, 1.4, 1.9, 4.6, 3.6], 'Verdict per session. The most frequent band is the target band found in the largest share of spots.')
d.figure(F['heat'], 'Percentage of spots in which each target band was found, by session.')
for mol, txt in (('NAM', "NAM was measured in five sessions on four chip types. No marker band reached the reproducibility rule. The most frequent was 929 cm-1 in session S8 (19 % of spots). That band was not taller than in the blank, and the other markers were rare. The verdict agrees with the earlier finding that NAM is not detected on bare silver. NAM has no thiol or other strong silver-binding group, so it may not adsorb in the hot spots. Capture chemistry such as a boronic-acid layer was proposed but has not been tested."),
                 ('LTA', "LTA was measured on the 2 min chip (S7) and on the session S8 chip. In S7 the 1131 cm-1 band was found in 40 % of spots. The blanks of that session also show a band at 1132 cm-1, so it is not reproducible against the blank. The strongest features of the S7 LTA mean (about 963, 1393 and 1600 cm-1) are also in the blank. They are consistent with substrate background. No phosphate band was reproducible."),
                 ('LPS', "LPS was measured only in session S8. The 1330 cm-1 band was found in 43 % of spots, but it was not taller than in the blank, and 989 cm-1 was not found. The separate LPS document describes a band set that recurs in many LPS spots and is not in the blank. It is consistent with an LPS-related signal, but it does not include the target bands, so the target-band rule is not met.")):
    d.h2(mol)
    d.figure(F[mol], f'{mol}: bulk reference (top), mean SERS spectrum (middle) and same-session blank (bottom) for each session. Each target band is marked with the number of spots in which it was found. Green = reproducible; orange = found in some spots but not reproducible; grey = not found.')
    d.p(txt)
d.h1('Interpretation')
for t in ('The chips are SERS-active for R6G, a molecule that adsorbs strongly and is resonance-enhanced. The recipe matters: 20 mM AgNO3 gave a much stronger signal than 6 mg AgNO3 (about 0.7 mM in 50 mL).',
          'The very large spread between two chips of the same recipe shows that fabrication is not yet reproducible. The best R6G result therefore describes one chip, not the process.',
          'The biomarkers were not detected under the target-band rule. The likely reasons are weak adsorption on bare silver (NAM, LTA) and a substrate background that overlaps the target region. The data do not separate these causes.',
          'Every biomarker session that had a blank showed bands that would look like analyte bands without that blank. Same-session blanks on the same chip type are essential.'):
    d.b(t)
d.h1('Limitations')
for t in ('Laser power at the sample (mW) was never measured; only the software level is known.', 'HF stock concentration was not recorded (49 % is assumed in the fabrication notes).',
          'One chip per fabrication condition; no repeat batches.', 'No SEM, EDS or UV-Vis characterisation of the chips.', 'Session S2 has no blank; the 2 min chip in S5 has no blank of its own.',
          'Analyte concentrations and drop volumes are missing for many folders (Not recorded).', 'The meaning of some folder labels (for example 1m-etcheddata) is read from the name only.'):
    d.b(t)
d.h1('Recommended next steps')
for t in ('Make three or more chips with the 20 mM AgNO3, 2 min recipe in one batch and on separate days, and test each with R6G before any biomarker.',
          'Measure a same-session blank on every chip, at the settings used for the analyte.', 'Record analyte concentration, drop volume, drying time and the time between etching and measurement for every chip.',
          'Measure the laser power at the sample and confirm the HF stock concentration.', 'For NAM and LTA, test capture layers (boronic acid for NAM, cysteamine for LTA) against a bare-silver control.',
          'Characterise the best and the worst chip by SEM, to link the silver morphology to the SERS signal.'):
    d.b(t)
os.makedirs(os.path.join(OUT, '06_Reports'), exist_ok=True)
d.save(os.path.join(OUT, '06_Reports', 'SERS_All_Sessions_Analysis_Report.docx')); print('saved')
