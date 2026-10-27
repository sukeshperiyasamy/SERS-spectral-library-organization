SERS Sepsis Project - Bulk Powder Raman Spectral Library (NAM, LTA, LPS)
Version 2.1 - 23 September 2026 (NAM 60 s re-audit; final peak hierarchy; LTA preliminary; LPS pending) - prepared by Sukesh Periyasamy (JRF)

Samples: bulk (neat) powders measured directly on glass slides.
Instrument: B&W Tek i-Raman Plus BWS465-785H (BTC665N-785H-SYS), 785 nm. Processed range 400-1800 cm-1.
Laser power = instrument power level (%), not converted to mW. Objective not recorded in raw headers.

01_Raw_Data_Renamed    byte-identical renamed copies of the original files (originals untouched)
02_Processed_Spectra   one processed CSV per spectrum (raw, dark-subtracted, baseline, baseline-corrected, normalised)
03_Reference_Spectra   NAM and LTA mean +/- SD references; LPS pending (see README inside)
04_Figures             Figures 1-7 of the report
05_Tables              Spectral_Library_Metadata_and_Peaks.xlsx
06_Literature          references, literature band list, experimental-vs-literature assignments
07_QC_and_Exclusions   QC log, excluded/flagged list, QC figures, processed excluded spectra
Bulk_Spectral_Library_Report_NAM_LTA_LPS.docx   final report

Naming: <Analyte>_Bulk_<YYYYMMDD>_P<power>pct_T<time>s_A<acc>_S<rep>.csv ; Glass_Blank_<YYYYMMDD>_P..pct_T..s_A.._S...csv
Future measurements: NAM 90%/30s/5acc; LTA 80%/45s/2acc; LPS 70/80/90% 30s 5acc screening; glass blank at identical settings.

v2.1 changes:
- NAM 60 s x 5 acc re-audited individually: 3 x 70 % = class A (valid, supporting group; moved Excluded -> NAM_Bulk),
  10 x 90 % = class C (distorted; remain in Excluded). None saturated inside 400-1800 cm-1.
- NAM primary markers: 541, 829, 870, 929, 955, 1023, 1127 cm-1 (829 promoted); supporting 457, 487, 1249.
- LTA = PRELIMINARY bulk reference (n = 4): primary 802, 861.5, 1092; supporting 1459; 1367 = glass-associated.
- LPS reference spectrum pending controlled glass-slide measurement.
- New: 06_Literature/Literature_Peak_Assignments.xlsx; 07_QC_and_Exclusions/NAM_60s_ReAudit_Classification.csv

v3 (23 Sep 2026) — traceable workflow edition:
- Pipeline v3: fixed hot-pixel correction (CCD pixels 640/700), spike removal with width guard (v2.1 clipped sharp NAM bands by ~11-12 %),
  robust (MAD) noise. All processed spectra regenerated; every stage stored as a column.
- NAM: GO for identity/markers; interim reference n = 15 (5 independent spots) -> top-up >= 10 independent spots at 90 %/30 s/5 acc.
  Intensity 917 +/- 37 counts (929 cm-1), SNR 51.1 +/- 4.7.
- LTA: RE-ACQUIRE 10-15 spots at 80 %/45 s/2 acc. Preliminary intensity 1110 +/- 98 counts (1092 cm-1), SNR 28.5 +/- 1.0.
- LPS: RE-ACQUIRE — 70/80/90 % x 30 s x 5 acc screening with matched glass blanks.
- New: 08_Methodology (workflow, preprocessing, QC, peak selection, acquisition SOP, log template, code);
  Fig01-Fig09 workflow figures (v2.1 figures archived); workbook Traceability_Table + sheets 15-25.

--- 27 Sep 2026 (v3.1): NAM validation session 24 Sep 2026 added ---
The raw folder bulk-lps-24-09-26 was named "lps" in error; the operator checked the bottle on 27 Sep 2026: the powder was NAM.
(An LPS-labelled analysis from 24 Sep was withdrawn and moved to ../_to_delete/LPS_mislabel_20260924_superseded.)
Originals: bulk-lps-24-09-26/ (unchanged; README_SAMPLE_IDENTITY.txt added). Copies: 01_Raw_Data_Renamed/NAM_Bulk/NAM_Bulk_20260924_* (41)
and Glass_Blank/Glass_Blank_20260924_* (16), MD5 verified. Processed: 02_Processed_Spectra/NAM and Glass_Blank.
Figures: 04_Figures/NAM_Session_20260924 (N1-N9). Workbook sheets 26-32. QC: 07_QC_and_Exclusions/NAM_Session_20260924_QC_Log.csv.
Reference: 03_Reference_Spectra/NAM/NAM_Validation_20260924_* + README update (reference files unchanged).
Reports: NAM_Bulk_Validation_Report_20260924.docx; main report updated to v3.1 (Section 15A).
Result: 21/41 pass QC (failures = dark-reference ripple). New independent spots SUPPORT the NAM reference
(markers 21/21, positions <= 1.5 cm-1, primary relative intensities within +/-7 %). Condition unchanged (90/30/5); still interim:
>= 4 more clean independent spots at 90/30/5 needed. LPS: no data yet; 70/80/90 % screening still required.

--- 28 Sep 2026: LPS screening session added (folder ../28-9-26-lps-bulk, originals unchanged) ---
Copies: 01_Raw_Data_Renamed/LPS_Bulk/LPS_Bulk_20260928_* (19) and Glass_Blank/Glass_Blank_20260928_* (10), MD5 verified.
Note: 60 % files S01-S04 and blanks carry instrument-clock date 27 Sep 2026 21:xx; named by session date 20260928. No file 5 at 60 %.
Processed: 02_Processed_Spectra/LPS, Glass_Blank. Figures: 04_Figures/LPS_Session_20260928 (P1-P4). Workbook sheets 33-36.
QC: 07_QC_and_Exclusions/LPS_Session_20260928_QC_Log.csv. LPS reference still pending (see 03_Reference_Spectra/LPS README).
Result: 60 %: 8 core, 70 %: 4 core (+1 glass-dominated each), 80 %: 0/5 (ripple). Best power 70 %. Candidate primary band 425 cm-1.
Next: 10-15 spots at 70 % / 30 s / 10 acc + matched blanks.

--- 28 Sep 2026 (v3.2): NAM reference declared FINAL (operator decision; no further NAM acquisition). Reference files unchanged; limitation documented (6 independent spots at 90/30/5, supported by 31 at other conditions). Workbook sheet 37; main report v3.2 (Sections 15A, 15B). ---

--- 28 Sep 2026 (v3.3): LPS REFERENCE ESTABLISHED ---
LPS from E. coli O111:B4 (Sigma L2630, lot 0000442391), 60 % / 40 s / 5 acc, n = 10 (S10-S12, S14-S20); S13 excluded (glass-dominated).
Primary markers 425 and 1080 cm-1; supporting 766, 861, 997 cm-1. Raw folder ../28-9-26-lps-bulk unchanged; copies in 01_Raw_Data_Renamed
(LPS_Bulk, Glass_Blank, new Instrument_Checks). Reference: 03_Reference_Spectra/LPS. Figures: 04_Figures/LPS_Reference_20260928 (R1-R5).
Workbook sheets 38-42. Report: LPS_Bulk_Reference_Report_20260928.docx; main report v3.3 (Section 15C). Code: 08_Methodology/code/lr1-lr9.py.
Instrument notes: ripple at >= 70 % power; close the shutter by hand before taking the dark (software dark leaks light).

--- 27 Oct 2026: 7 Oct 2026 data screened and EXCLUDED ---
E:/sukesh/10-oct-2026 (lta/lta2 SP_38-46; lps/lps1 SP_20-35; lps/lps2 SP_1-19; 44 spectra): operator confirmed these are on etched silicon (SERS work), not bulk powder on glass.
Dominated by ~517-520 cm-1 band (consistent with silicon); r ~0 vs NAM/LPS/LTA references. Logged in 07_QC_and_Exclusions/Excluded_and_Flagged_Spectra.csv. Raw files untouched and not copied into the library.
LTA reference remains PRELIMINARY (n = 4, 3 Apr 2026); bulk re-acquisition on glass (80 %/45 s/2 acc, 12-15 spots, 2-3 blanks, hand-closed dark) still to do.

--- 27 Oct 2026: Marker explanation document ---
New: Bulk_Spectral_Marker_Explanation_NAM_LPS_LTA.docx (v1.0): per-molecule explanation of target bands (why they appear, why chosen, tentative assignments, limits) for NAM, LPS and LTA.
Figures: 04_Figures/Marker_Explanation_20261027 (annotated references, marker zooms, three-way comparison). All numbers read from 03_Reference_Spectra and 06_Literature tables; no new assignments introduced.

--- 27 Oct 2026: DFT vs experiment comparison ---
New: DFT_vs_Experimental_Comparison_NAM_LPS_LTA.docx (v1.0); figures 04_Figures/DFT_Comparison_20261027; code 08_Methodology/code/dft_compare_1.py, dft_compare_2.py.
Result: DFT band positions agree for part of the bands (NAM 7/11, LPS 4/5, LTA 2/4 within 10 cm-1) but not better than a random-shift baseline (p 0.68-0.75); whole-spectrum r about 0.1. Used as supporting evidence only (consistent with), not identity confirmation. DFT inputs are in C:/Users/sukes/Downloads/mtp (not copied).
