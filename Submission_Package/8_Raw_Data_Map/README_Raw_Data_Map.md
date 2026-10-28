# Raw data map by sample

The dated raw-data folders are grouped here by sample: NAM, LPS and LTA. The folders themselves are not moved, renamed or edited, so the file paths recorded in the processed files, tables and reports stay valid. Where one dated folder holds more than one sample, each subfolder is listed under the sample it belongs to.

The same tables are in `Raw_Data_By_Analyte.csv`. `Raw_Data_Index.csv` has one row per dated folder and `Raw_Data_Subfolders.csv` one row per subfolder.

The assignment of a subfolder to a sample follows what the library processed from it (the `# Original raw file` line in each processed file). Dates and settings are read from the instrument file headers.

## NAM (N-acetylmuramic acid)

FINAL reference: 90 %, 30 s, 5 acc, 29-05-26 data (different-spot and same-spot sets). Validated by the 24 Sep 2026 session. The 28 Jan 2026 and 3 Apr 2026 data are not part of the reference.

332 files in 25 subfolders; 311 sample spectra and 21 glass blanks are processed in the library.

| Folder | Subfolder | Measured | Files | Settings | Sample spectra processed | Glass blanks processed |
|---|---|---|---|---|---|---|
| 10sec-power5-80-2set | (files directly in folder) | 2026-01-28 | 17 | 5-80 % power, 10 s, acc 2 | 17 | 0 |
| 15sec-power5-80andset2 | (files directly in folder) | 2026-01-28 | 16 | 5-80 % power, 15 s, acc 2 | 16 | 0 |
| 20sec-power5-80and set2 | (files directly in folder) | 2026-01-28 | 16 | 5-80 % power, 20 s, acc 2 | 16 | 0 |
| 25sec-power5-80 and set2 | (files directly in folder) | 2026-01-28 | 16 | 5-80 % power, 25 s, acc 2 | 16 | 0 |
| 5sec-power5-80 and 2set | (files directly in folder) | 2026-01-28 | 16 | 5-80 % power, 5 s, acc 2 | 16 | 0 |
| NAM-15secs and power15-75-2sets | (files directly in folder) | 2026-01-28 | 17 | 5-75 % power, 15 s, acc 2 | 17 | 0 |
| 4-4-26 | 35sec80power | 2026-04-03 | 6 | 80 % power, 35 s, acc 2 | 6 | 0 |
| 4-4-26 | 40-80 nam | 2026-04-03 | 8 | 80 % power, 40 s, acc 2 | 8 | 0 |
| 4-4-26 | NAM multispot | 2026-04-03 | 17 | 70-80 % power, 30 s, acc 2 | 17 | 0 |
| 4-4-26 | diffrent 3sec 80-100 | 2026-04-03 | 20 | 80-100 % power, 30 s, acc 2 | 20 | 0 |
| 4-4-26 | samespot35sec diffrent power | 2026-04-03 | 5 | 50-100 % power, 35 s, acc 2 | 5 | 0 |
| 29-05-26 | NAM-70p-10s-3acc | 2026-05-29 | 11 | 70 % power, 10 s, acc 3 | 11 | 0 |
| 29-05-26 | NAM-70p-10s-5ac | 2026-05-29 | 12 | 70 % power, 10 s, acc 5 | 12 | 0 |
| 29-05-26 | NAM-90p-10s-3ac | 2026-05-29 | 12 | 90 % power, 10 s, acc 3 | 12 | 0 |
| 29-05-26 | NAM-90p-10s-5ac | 2026-05-29 | 11 | 90 % power, 10 s, acc 5 | 11 | 0 |
| 29-05-26 | glass slide empty | 2026-05-29 | 44 | 5-90 % power, 5-10 s, acc 1/3/5 | 39 | 5 |
| 29-05-26 | 70p-5ac-10s-diifrentpoint | 2026-05-30 | 10 | 70 % power, 10 s, acc 5 | 10 | 0 |
| 29-05-26 | 70p-5ac-30s-diifrentspot | 2026-05-30 | 3 | 70 % power, 30 s, acc 5 | 3 | 0 |
| 29-05-26 | 70p-60s-5ac-diifrentpoint | 2026-05-30 | 3 | 70 % power, 60 s, acc 5 | 3 | 0 |
| 29-05-26 | 90p-30s-5ac-diifrentpoint | 2026-05-30 | 5 | 90 % power, 30 s, acc 5 | 5 | 0 |
| 29-05-26 | 90p-30s-5acc-samespot | 2026-05-30 | 10 | 90 % power, 30 s, acc 5 | 10 | 0 |
| SERS_Sepsis_Spectral_Library/bulk-lps-24-09-26 | 60 power | 2026-09-24 | 15 | 60 % power, 30 s, acc 5 | 11 | 4 |
| SERS_Sepsis_Spectral_Library/bulk-lps-24-09-26 | lps-diffrent power-70 | 2026-09-24 | 11 | 70 % power, 30 s, acc 5 | 8 | 3 |
| SERS_Sepsis_Spectral_Library/bulk-lps-24-09-26 | lps-diffrent-80 power | 2026-09-24 | 14 | 80 % power, 30 s, acc 5 | 9 | 5 |
| SERS_Sepsis_Spectral_Library/bulk-lps-24-09-26 | lps-diffrent-90-power | 2026-09-24 | 17 | 90 % power, 30 s, acc 5 | 13 | 4 |

## LPS (E. coli O111:B4 lipopolysaccharide)

ESTABLISHED reference: 60 %, 40 s, 5 acc, from 28-9-26-lps-bulk / 40-60-5-diffrentposition-. The 13 Apr 2026 data are screening runs without an established band.

73 files in 8 subfolders; 51 sample spectra and 15 glass blanks are processed in the library.

| Folder | Subfolder | Measured | Files | Settings | Sample spectra processed | Glass blanks processed |
|---|---|---|---|---|---|---|
| 13-4-26 | lps | 2026-04-13 | 9 | 10-20 % power, 10-60 s, acc 2/5/30/50 | 9 | 0 |
| 14-426 | lps | 2026-04-13 | 5 | 10-20 % power, 10-30 s, acc 2/50/60 | 5 | 0 |
| 28-9-26-lps-bulk | raw glass slide and 30s-60p-5a | 2026-09-27 to 2026-09-28 | 12 | 60 % power, 30 s, acc 5 | 9 | 3 |
| 28-9-26-lps-bulk | 30s-70p-5ac | 2026-09-28 | 8 | 70 % power, 30 s, acc 5 | 5 | 3 |
| 28-9-26-lps-bulk | 30s-80p-5a | 2026-09-28 | 9 | 80 % power, 30 s, acc 5 | 5 | 4 |
| 28-9-26-lps-bulk | 40-60-5-diffrentposition- | 2026-09-28 | 11 | 60 % power, 40 s, acc 5 | 11 | 0 |
| 28-9-26-lps-bulk | blank+short | 2026-09-28 | 6 | 60 % power, 5-40 s, acc 1/5 | 0 | 5 |
| 28-9-26-lps-bulk | unwanted | 2026-09-28 | 13 | 60-70 % power, 30-40 s, acc 5 | 7 | 0 |

## LTA (lipoteichoic acid)

PRELIMINARY reference from 4 spectra of 3 Apr 2026 (80-95 %, 45 s, 2 acc). Re-acquisition on glass is pending.

12 files in 2 subfolders; 12 sample spectra and 0 glass blanks are processed in the library.

| Folder | Subfolder | Measured | Files | Settings | Sample spectra processed | Glass blanks processed |
|---|---|---|---|---|---|---|
| 4-4-26 | 5sec,30,50 power 10 set | 2026-04-03 | 2 | 30-50 % power, 5 s, acc 10 | 2 | 0 |
| 4-4-26 | LTA | 2026-04-03 | 10 | 40-95 % power, 10-45 s, acc 2/10/15 | 10 | 0 |

## Notes on mixed or misleading folders

- `4-4-26` (spectra dated 3 Apr 2026) holds both NAM and LTA. The subfolders `LTA` and `5sec,30,50 power 10 set` were processed as LTA; the others as NAM.
- `29-05-26/glass slide empty` contains NAM spectra (replicate set R9, 39 files) and the 5 genuine empty-slide blanks.
- `SERS_Sepsis_Spectral_Library/bulk-lps-24-09-26` is NAM, not LPS, although its subfolders are named lps-... (see README_SAMPLE_IDENTITY.txt in that folder).
- `29-05-26/90p-60s-5a-samespot` and `90p-60s-5ac-diffrentspot` (90 %, 60 s) damaged the NAM sample; they are kept as excluded copies in `01_Raw_Data_Renamed/Excluded`.
- `28-9-26-lps-bulk/blank+short` contains glass blanks only.

## Excluded bulk-powder data

| Folder | Subfolder | Measured | Files | Settings | Reason |
|---|---|---|---|---|---|
| 9-2-2026 | 20sec20power-variable location LTA | 2026-02-09 | 12 | 20 % power, 20 s, acc 2 | Spectra are polystyrene-like and not confirmed as LTA (labelled LTA, 9 Feb 2026). |
| 29-05-26 | 90p-60s-5a-samespot | 2026-05-30 | 5 | 90 % power, 60 s, acc 5 | Laser damaged the sample (90 %, 60 s); excluded. |
| 29-05-26 | 90p-60s-5ac-diffrentspot | 2026-05-30 | 5 | 90 % power, 60 s, acc 5 | Laser damaged the sample (90 %, 60 s); excluded. |

## Not part of the bulk-powder library

| Folder | Category | Measured | Files | What it is |
|---|---|---|---|---|
| MB 1ugml | Out of scope (not bulk powder) | 2026-01-15 | 3 | 15 Jan 2026, folder named MB 1ugml. |
| 2-2-26 | Out of scope (not bulk powder) | 2026-02-02 | 39 | 2 Feb 2026, subfolder 0.1ug-ml. Analyte not recorded in the file headers. |
| 5-6-2026 | Out of scope (SERS / substrate) | 2026-06-06 | 24 | 6 Jun 2026: AgNO3 empty wafer and pure silicon multispot. |
| New folder | Unsorted | 2026-06-10 | 4 | 4 CSV files dated 10 Jun 2026; no description in the folder or file headers. |
| 10-6-26 | Out of scope (SERS / substrate) | 2026-06-10 to 2026-06-11 | 120 | 10-11 Jun 2026: NAM and R6G on substrates; subfolders are labelled 3m, 4m, 5m and 6m (the label is not explained in the files) plus different-spot sets. |
| 17-06-2026 | Out of scope (SERS / substrate) | 2026-06-17 | 98 | 17 Jun 2026: substrate series; subfolders are labelled 3m to 6m with 5 ml or 10 ml HF (for example 3m-10ml-hf-5s-10p-5ac). |
| 04-07-2026 | Out of scope (SERS / substrate) | 2026-07-04 | 78 | 4 Jul 2026 substrate work: NAM on HF / AgNO3 substrate, R6G, R6G sensor, raw R6G, substrate. |
| sers-r6g-samespot | Out of scope (SERS) |  | 0 | Empty folder (no files). |

The 7 Oct 2026 spectra on etched silicon (`E:\sukesh\10-oct-2026`) are not in this repository; they are logged as excluded in `07_QC_and_Exclusions`.

## Finding the raw file behind a library spectrum

- Each file in `SERS_Sepsis_Spectral_Library/02_Processed_Spectra` starts with `# Original raw file (unchanged): <path>`, and the same path is in the `*_Reference_Members.csv` files under `03_Reference_Spectra`.
- `01_Raw_Data_Renamed` holds MD5-verified copies; the originals stay in the dated folders.
- New measurements: keep each session in its own dated folder and add its subfolders to `Raw_Data_By_Analyte.csv`.

## Added 28 Oct 2026

- `bulk-lta` (LTA, 28 Oct 2026): 36 spot-folder files and 8 blank files at 80 %, 45 s, 2 acc. SP_1 to SP_8 of the spot folder are identical to the blank files; 28 spots and 8 blanks are processed in the library (LTA reference v2).

- `bulk-lta` update (28 Oct 2026): the folder now holds 126 files in 8 subfolders (45sec-80p-2acc-diffrentspot 36, glass blank 8, diifrent 60s-2ac-70p 9, blank glass 11, 30sec-80p-3ac 20, 70power-60power mulispot 20, 30s-80p-3acc 11, 30sec-70p-3 accc 11). 8 files duplicate blanks, so 118 unique files (99 LTA spectra, 19 blanks) are in the library under LTA_Bulk by setting; see SERS_Sepsis_Spectral_Library/01_Raw_Data_Renamed/LTA_Bulk/LTA_20261028_File_Index.csv for the file-by-file map.
