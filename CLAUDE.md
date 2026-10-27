# CLAUDE.md — SERS Sepsis Project: Bulk-Powder Raman Spectral Library

Read this first. It is the hand-off from the earlier Claude (Cowork) sessions (Sep 2026) so work can continue in Claude Code.
Owner: Sukesh Periyasamy (JRF, IIT Jodhpur). Audience for outputs: the professor and the funding company.

## 1. What this project is
A traceable reference library of **bulk (neat) powder** Raman spectra for three sepsis-related analytes:
- **NAM**: FINAL
- **LPS** (E. coli O111:B4 lipopolysaccharide): ESTABLISHED
- **LTA** (lipoteichoic acid): ESTABLISHED on 28 Oct 2026 (pending operator confirmation); the April 2026 reference was preliminary

These references support later SERS work.

## 2. Hard rules (never break)
1. **Raw files are read-only.** Never modify, overwrite, rename or delete an original raw file. The library holds MD5-verified *copies* in `01_Raw_Data_Renamed`.
2. **Substrate is always a glass slide.** All bulk measurements are on glass slides. Do not introduce or suggest other substrates.
3. **Do not invent metadata.** If something is not recorded, write "Not recorded". Laser power stays in **% of maximum**. Do not convert it to mW.
4. **Do not invent literature assignments.** Only cite sources that have been checked. Mark DOIs "unverified" if they could not be confirmed.
5. **Glass is not a biomarker.** The ~1367 cm⁻¹ band (zone 1308–1455 cm⁻¹) comes from the glass. Exclude that zone from correlations and never report it as an analyte marker.
6. **No cherry-picking.** Process every spectrum and apply QC rules. Log every exclusion with a reason in `07_QC_and_Exclusions/Excluded_and_Flagged_Spectra.csv`.
7. **Wording.** Use "tentative", "consistent with", "suggests". Never use "proves" or "confirms identity".
8. Do not delete data. Anything to discard goes to a `_to_delete/` folder, and the user deletes it.

## 3. Folder map (repo root = `C:\Users\sukes\Downloads\sukesh`)
- Dated folders (`4-4-26`, `29-05-26`, `28-9-26-lps-bulk`, …): **original raw data**. Out-of-scope SERS/R6G/MB/substrate folders are also here and are not part of the library.
- `SERS_Sepsis_Spectral_Library/`
  - `01_Raw_Data_Renamed/`: renamed raw copies (NAM_Bulk, LPS_Bulk, LTA_Bulk, Glass_Blank, Instrument_Checks, Excluded).
  - `02_Processed_Spectra/`: pipeline-v3 outputs, one per raw.
  - `03_Reference_Spectra/{NAM,LPS,LTA}/`: Mean ± SD references, members, marker peaks and a `README_*_status.txt` for each.
  - `04_Figures/`: Fig01–09; NAM_Session_20260924 (N1–N9); LPS_Session_20260928 (P1–P4); LPS_Reference_20260928 (R1–R5).
  - `05_Tables/Spectral_Library_Metadata_and_Peaks.xlsx`: sheets 1–42.
  - `06_Literature/`: `Literature_Peak_Assignments.xlsx` (incl. LPS_Comparison_20260928, LPS_Sources_20260928) and CSVs.
  - `07_QC_and_Exclusions/`: QC logs per session and the exclusion list.
  - `08_Methodology/`: methodology .md files, Lab Data-Recording SOP (.docx), recording template (.xlsx) and `code/`.
  - `bulk-lps-24-09-26/`: original raw files from 24 Sep. They are **NAM**; the folder name is wrong (see README_SAMPLE_IDENTITY.txt).
  - `09_Reports/` (.docx):
    - `Bulk_Spectral_Library_Report_NAM_LTA_LPS.docx` (main report, v3.3)
    - `NAM_Bulk_Validation_Report_20260924.docx`
    - `LPS_Bulk_Reference_Report_20260928.docx`
    - `LPS_Findings_and_Parameters_Report.docx` (all LPS findings and parameters: bulk, DFT, SERS)
    - `Bulk_Spectral_Marker_Explanation_NAM_LPS_LTA.docx` (target bands, per molecule)
    - `DFT_vs_Experimental_Comparison_NAM_LPS_LTA.docx` (v1.1)
    - `Simulation_Methods_and_Spectra_NAM_LPS_LTA.docx`
  - `Raw_Data_Index/` (repo root): map of the dated raw folders grouped by NAM, LPS and LTA.
  - `README.txt`: version history and change log. Append to it; never rewrite it.

**File naming:** `<Analyte>_Bulk_<YYYYMMDD>_P<power3>pct_T<s>s_A<acc2>_S<rep2>.csv`, e.g. `LTA_Bulk_20260403_P080pct_T45s_A02_S01.csv`. Blanks: `Glass_Blank_<...>.csv`.

## 4. Instrument and acquisition
- B&W Tek i-Raman Plus BWS465-785H (BTC665N-785H-SYS), 785 nm. Usable range ends at 2842 cm⁻¹, so there is no C–H stretch region.
- **Ripple:** fixed-pattern ripple appears at ≥70–90 % power and is present in the collected light. It is analyte-dependent: LTA at 80 % was acceptable, LPS at 70 % was not.
- **Dark:** the software dark leaks sample light. **Always take the dark with the shutter closed by hand.** True dark ≈ 1480–1525 counts at 40 s × 5 and ≈ 1470 at 30 s × 5.
- Saturation limit: 65535 counts.

| Analyte | Setting | Status |
|---|---|---|
| NAM | 90 % / 30 s / 5 acc | FINAL (keep; more spots may be added later) |
| LPS | 60 % / 40 s / 5 acc | ESTABLISHED |
| LTA | 80 % / 45 s / 2 acc | ESTABLISHED (28 Oct 2026, n = 10); next: about 5 more mid-signal spots (raw max 15,000–50,000) and 3 clean glass blanks; hand-closed dark; first spot ripple ≤ 50 |

## 5. Processing pipeline v3 (`08_Methodology/code/lib2.py`, `process_v3h`)
1. Dark-subtracted signal: ds = raw − dark. Recompute it from raw − dark when the software applied smoothing ("Data Pretreat").
2. Hot-pixel fix: CCD pixels 640 and 700 (≈1095.7 and 1189.5 cm⁻¹).
3. Crop 400–1800 cm⁻¹.
4. Despike: MAD z > 6, spike width ≤ 2 px.
5. Savitzky–Golay smoothing, window 11, order 3.
6. ALS baseline: λ = 1e5, p = 0.01, 10 iterations.
7. Noise = 1.4826 · MAD(despiked − smoothed).
8. Min–max normalisation.
9. Correlations exclude the glass zone 1308–1455 cm⁻¹.

**QC rules**
- No saturation in 400–1800.
- Ripple (high-pass SD of ds in 1550–1800; SG 31/2 residual) ≤ 50 counts.
- SNR ≥ 10.
- Exclude glass-dominated spots (glass-zone / 800–1000 area ratio > 8).
- Band categories C1 (primary marker) to C4.
- For LPS, intensities are compared as ratios to the 425 cm⁻¹ band, because absolute counts vary 3–5× between spots.

`lib2.py` auto-detects the `sukesh` folder from its own location. You can override it with the `SUKESH_ROOT` environment variable. Python 3 needs numpy, scipy, pandas, matplotlib and openpyxl. Script order is in `code/README_code.txt`. Session scripts:
- `ln0–ln5`: NAM 24 Sep
- `lp1–lp6`: LPS screening 28 Sep
- `lr1–lr9`: LPS reference 28 Sep
- `lta_chk.py`

## 6. Current results

**NAM — FINAL**
- Reference: 90 %/30 s/5, n = 15 (30 May 2026).
- 929 band: 919 ± 36 counts.
- Primary markers: 541, 829, 870.5, 929, 955, 1023, 1127 cm⁻¹.
- Validated by 21 spots on 24 Sep (60/70/80 %).

**LPS — ESTABLISHED (28 Sep 2026)**
- Sample: Sigma L2630, lot 0000442391 (vial photo is in 03/LPS).
- Condition: 60 %/40 s/5, n = 10 (S10–S12, S14–S20). S13 was excluded as glass-dominated.
- Agreement: pairwise r 0.916; mean vs median r 0.982.
- C1 markers:
  - 425 cm⁻¹ (424.8 ± 0.9, SNR 38, unassigned in the literature)
  - 1080 cm⁻¹ (1080.5 ± 1.1, broad, SNR 15, ~14 % glass overlap)
- C2 markers: 766, 861, 997.
- Identity check: r = 0.98 vs screening, 0.80 vs April data, 0.52 vs LTA, 0.17 vs NAM.
- Limitation: earlier darks leaked light, so intensities may be 3–34 % low. This is documented in the report.

**LTA — ESTABLISHED (28 Oct 2026, pending confirmation): n = 10 spots at 80 %/45 s/2 acc; mean agrees with the April data (r = 0.947); primary bands 1092 (SNR 29), 539 and 861 cm⁻¹; supporting 419, 629, 723, 798, 1459, 1583, 1751. QC of 28 spots: 10 PASS, 8 REVIEW (ripple 50–58), 3 EXCLUDE, 7 FAIL (5 saturated). The 28 Oct blanks look polystyrene-like and need re-measuring. Report: 09_Reports/LTA_Bulk_Reference_Report_20261028.docx. Supplier/lot not recorded.**

**LTA — earlier PRELIMINARY reference (3 Apr 2026, n = 4: 80, 80, 90 and 95 % at 45 s/2 acc)**
- Primary markers: 802, 861.5, 1092 cm⁻¹ (1092: 1110 ± 98 counts, SNR ≈ 28).
- Supporting: 1459. Glass-associated: 1367.
- Ripple at 80 %/45 s/2 was 37–38, which passes. The 50 %/30 s/15 spectrum was distorted (ripple 154) and rejected.
- The 9 Feb 2026 files labelled "LTA" are polystyrene-like and excluded.

## 7. Reports and document generation
- Format: Word (.docx), A4, Arial, 1.4 cm margins.
- Tables have grey (D9D9D9) header rows. Callout boxes: note EAF2FB, warning FDECEA, OK EAF6EE.
- Sections are numbered; v3.3 adds §15A NAM validation, §15B LPS screening and §15C LPS reference.
- The old docx-js builder scripts were in a temporary cloud workspace and are **lost**. Rebuild with python-docx or the `docx` npm package. Take numbers from the CSV/XLSX files in 03/05/07; never retype them by hand.
- New versions get a new version number and date. Keep old versions, moving them to `_to_delete/` only if the user agrees.
- After every reporting change, update `README.txt` (append) and the workbook sheets.

## 8. Next steps
1. **LTA re-acquisition: done 28 Oct 2026** (see section 6). Remaining: confirm status, add supplier/lot, re-measure clean glass blanks, optionally 5 more spots, update the main report to v3.4. Original steps for reference:
   - Rename the copies and verify their MD5.
   - Run pipeline v3 and QC.
   - Build the reference (Mean ± SD) and marker peaks.
   - Compare with the April LTA data and check identity vs NAM and LPS.
   - Write the figures, workbook sheets, QC log and an LTA report, then update the main report to v3.4.
2. Optional: more NAM spots at 90 % after all three analytes are done.
3. Final combined report and three-way NAM/LPS/LTA discrimination summary for the funder.
4. Suggest reporting the ripple and dark-leak issues to the B&W Tek service engineer.

## 9. Git
Repo: `https://github.com/sukeshperiyasamy/SERS-spectral-library-organization` (private), branch `main`.
`.gitattributes` stores csv/txt/txtr/docx/xlsx/png/jpg as **binary**, so raw bytes are never converted. Keep it that way.
After each session: `git add -A && git commit -m "<what>" && git push`.
