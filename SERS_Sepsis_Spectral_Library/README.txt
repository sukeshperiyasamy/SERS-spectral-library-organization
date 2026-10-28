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

--- 27 Oct 2026: Simulation methods document; comparison document v1.1 ---
New: Simulation_Methods_and_Spectra_NAM_LPS_LTA.docx (v1.0): software, settings, spectra obtained and why fragments (not whole LPS/LTA) were simulated. Figures 04_Figures/Simulation_20261027 (S1-S4); code 08_Methodology/code/dft_simulation_figures.py.
Correction: DFT_vs_Experimental_Comparison_NAM_LPS_LTA.docx is now v1.1. LPS fragments were B3LYP/6-31G(d) gas phase (LPS documentation); LTA glycerol-phosphate fragment is a two-unit dianion (charge -2) in SMD water (LTA.gjf/LTA.LOG). v1.0 wrongly said basis set / charge state were Not recorded.

--- 27 Oct 2026: wording revised in the four new documents (marker explanation, DFT comparison, simulation methods, LTA checklist): formal "rules/how to read" boxes replaced by plain introductory text; no change to data or conclusions.

--- 27 Oct 2026: Simulation_Methods document now names Gaussian 16 only (earlier-version runs no longer listed).

--- 27 Oct 2026: Simulation_Methods document: the earlier NAM laptop run is listed again as a "Gaussian" job (version not stated in the document); all Gaussian 16 jobs unchanged.

--- 27 Oct 2026: Raw data map added ---
New folder Raw_Data_Index/ at the repo root (Raw_Data_Index.csv, Raw_Data_Subfolders.csv, README_Raw_Data_Map.md): every dated raw folder grouped by type, with measurement dates, settings and where it is used. No raw folder was moved, renamed or edited.

--- 27 Oct 2026: Raw data map regrouped by sample ---
Raw_Data_Index/README_Raw_Data_Map.md and Raw_Data_By_Analyte.csv now list the raw data under NAM, LPS and LTA (mixed folders split by subfolder, following what the library processed). No raw folder was moved.

--- 27 Oct 2026: Reports moved ---
All report .docx files moved from the library root into 09_Reports/ (git mv; content unchanged). Earlier entries above that name these files refer to their new location 09_Reports/.

--- 27 Oct 2026: mtp folder reorganised ---
The DFT input files under C:/Users/sukes/Downloads/mtp were moved into numbered folders (05_Experimental_Data/NAM, 05_Experimental_Data/LPS, 06_Simulation_DFT, 10_Working_Archive). Paths in the simulation and DFT comparison documents and in 08_Methodology/code/dft_compare_1.py and dft_simulation_figures.py were updated; dft_compare_1.py was re-run and gives identical results. The NAM alpha log is now NAM_Raman_Archive/nam-alpha.LOG (the copy in 02_DFT_Calculation was a duplicate).

--- 27 Oct 2026: LPS findings and parameters report ---
New: 09_Reports/LPS_Findings_and_Parameters_Report.docx (v1.0): sample, every acquisition, processing, QC and simulation parameter, bulk reference findings, DFT fragment comparison and the 7 Oct 2026 SERS result for LPS. Figure: 04_Figures/LPS_Summary_20261027; code 08_Methodology/code/build_lps_report.py.

--- 28 Oct 2026: LTA bulk re-acquisition added (folder bulk-lta) ---
28 LTA spots (SP_9-SP_36) and 8 blanks at 80 % / 45 s / 2 acc copied to 01_Raw_Data_Renamed (LTA_Bulk_20261028_*, Glass_Blank_20261028_*; MD5 verified, 36 of 36); SP_1-SP_8 of the spot folder are identical to the blanks and were not copied. Processed in 02_Processed_Spectra. QC: 10 PASS, 8 REVIEW, 3 EXCLUDE, 7 FAIL; QC log 07_QC_and_Exclusions/LTA_Reference_Session_20261028_QC_Log.csv; exclusion list updated.
Reference v2 (n = 10): 03_Reference_Spectra/LTA/*_20261028*; r to April 0.947. Primary bands 1092, 539, 861 cm-1. Workbook sheets 43-47. Figures 04_Figures/LTA_Reference_20261028 (FigL1-L5). Code 08_Methodology/code/lt1-lt7. The 28 Oct blanks look polystyrene-like and are flagged. Supplier/lot of the LTA not recorded.

--- 28 Oct 2026: LTA sample recorded ---
LTA: Sigma-Aldrich L2515-10MG, lipoteichoic acid from Staphylococcus aureus, lot 0000419622, source number 0000404178. Added to the headers of the 28 Oct processed spectra, reference v2, workbook sheet 47, the LTA report and CLAUDE.md. Purity not recorded; April vial not known.

--- 28 Oct 2026: LTA vial and purity ---
The 3 Apr 2026 LTA data are from the same vial as 28 Oct (operator). Purity: no figure found on the supplier pages (web search; page not opened); lot certificate not obtained. April processed headers updated with the sample line.

--- 28 Oct 2026: LTA product information sheet recorded ---
03_Reference_Spectra/LTA/LTA_Sample_Product_Information_L2515.txt (supplier structure description, solubility 5 mg/ml in water, storage). No purity figure on the sheet; purity Not recorded. Report and CLAUDE.md wording updated.

--- 28 Oct 2026: LTA report extended with the peak explanation ---
09_Reports/LTA_Bulk_Reference_Report_20261028.docx: new Section 5 (what each peak says, how the peaks are related, structure map from the supplier description). Figures FigL6-L8 in 04_Figures/LTA_Reference_20261028; code 08_Methodology/code/lt8_peak_figures.py. Sections 6-9 renumbered.

--- 28 Oct 2026: LTA full session added (bulk-lta, 126 files) ---
118 unique files (8 spot-folder files duplicate blanks) renamed, MD5-verified and filed by setting in 01_Raw_Data_Renamed/LTA_Bulk and Glass_Blank/20261028_LTA_session; processed copies in 02_Processed_Spectra/LTA; file index LTA_20261028_File_Index.csv. 55 of 99 LTA spectra flagged FLAG-DARK (leaked dark). Pooled reference v2.1 (n = 17) in 03_Reference_Spectra/LTA; v2 unchanged. Workbook sheets 43-48, QC log and exclusion log updated, figures FigL1-L13, code lt9-lt13. Report LTA_Bulk_Reference_Report_20261028.docx rebuilt as v2.0.

--- 28 Oct 2026: first 8 LTA-session blanks removed from the library ---
Library copies (raw and processed) of blanks S01-S08 (80 %, 45 s, 2 acc, polystyrene-like) moved to _to_delete/LTA_first8_polystyrene_blanks_20261028 at the operator's request. Exclusion-log entries stay as the record. Originals in bulk-lta unchanged. Glass_Blank/20261028_LTA_session now holds 11 clean or saturated glass blanks.

--- 28 Oct 2026: LTA report and Figure L13 rewritten without the first 8 blanks ---
Report v2.0 and FigL13 now describe only the 11 glass blanks; the polystyrene-like blanks are no longer mentioned (they are in _to_delete).

--- 28 Oct 2026: Submission_Package created ---
Submission_Package/ (repo root) holds copies of the reports, reference spectra, figures, tables, QC logs, methodology and SERS results with README_Contents.md. It is a copy; the library folders remain the source.

--- 28 Oct 2026: LPS whole-molecule lipid A model added to the comparison and reports ---
lps output simulation (shortened Kdo2-lipid A, 201 atoms, Gaussian 16W, PM6 then B3LYP/3-21G) copied to 08_Methodology/simulation/LPS_LipidA_Model_20261028. Compared with the LPS reference (all 5 bands within 2.4 cm-1; not above chance, p = 0.47-0.66; shape r = -0.01; fragments 4 of 5 within 5 cm-1, r = 0.14). DFT comparison (v1.2), Simulation methods (v1.1) and LPS findings (v1.1) rewritten; originals in _backup_before_lipidA. Results 05_Tables/LipidA_vs_LPS_results.json; figures 04_Figures/LipidA_Model_20261028; code lipidA_compare.py, lipidA_figures.py, update_docs_lipidA.py. Copied to Submission_Package.

--- 28 Oct 2026: LTA whole-molecule model added; LTA comparison redone against reference v2.1 ---
simulation/lta output simulation (3 glycerol-phosphate units, 2 D-Ala esters, 1 alpha-GlcNAc; C23H45N3O20P2, 93 atoms; Gaussian 16W, PM6 then B3LYP/3-21G; 273 modes, none imaginary) copied to 08_Methodology/simulation/LTA_Model_20261028. Compared with the pooled LTA reference v2.1 (n = 17), 9 primary/supporting bands: model 9 of 9 within 5 cm-1 (mean 2.5 cm-1; chance 6.1, p < 0.001 at 5 cm-1; p = 0.07 at 10 and 0.19 at 18), but matched modes are weak, strongest model modes (690, 1490-1510) are not in the measurement, whole-spectrum r = -0.01. Fragments against v2.1: 3/5/7 of 9, mean 15.8 cm-1, p 0.32-0.46, r = 0.09. DFT comparison (v1.3) and Simulation methods (v1.2) rewritten; originals in _backup_before_lta. Results 05_Tables/LTAmodel_vs_LTA_results.json; figures 04_Figures/LTA_Model_20261028; code lta_model_compare.py, lta_figures.py, update_docs_lta.py. Copied to Submission_Package. A higher-level LTA run (6-31+G(d,p), water) is still in progress and not included.
