# Bulk-Powder Raman Spectral Library: NAM, LPS and LTA

SERS sepsis project. Reference Raman spectra of three neat powders measured on glass slides (B&W Tek i-Raman Plus, 785 nm, laser power in % of maximum).

Prepared by Sukesh Periyasamy (JRF, IIT Jodhpur). Package assembled 28 October 2026.

## Status

| Sample | Setting | Status |
|---|---|---|
| NAM (N-acetylmuramic acid) | 90 %, 30 s, 5 acc | Final (n = 15; validated by a second session) |
| LPS (E. coli O111:B4, Sigma L2630) | 60 %, 40 s, 5 acc | Established (n = 10) |
| LTA (S. aureus, Sigma L2515, lot 0000419622) | 80 %, 30 s, 3 acc (best); reference from 80 %, 45 s, 2 acc and 80 %, 30 s, 3 acc | Established, pending confirmation (reference v2.1, n = 17) |

## Contents

| Folder | What is in it |
|---|---|
| 1_Reports | Main library report, per-sample reports (NAM validation, LPS reference, LTA reference), LPS findings and parameters, marker explanation, DFT comparison, simulation methods |
| 2_Reference_Spectra | Mean ± SD reference spectra, members, marker peaks and a status note for NAM, LPS and LTA |
| 3_Figures | All report figures, by session |
| 4_Tables_and_Literature | Metadata and peaks workbook; literature peak assignments and sources |
| 5_QC_and_Exclusions | QC logs per session and the list of every excluded or flagged spectrum, with reasons |
| 6_Methodology_and_SOP | Processing and QC methodology, acquisition SOP, data-recording SOP and template, analysis code |
| 7_SERS_Results | SERS results of October 2026 and the NAM SERS status analysis (separate from the bulk library) |
| 8_Raw_Data_Map | Map of the original raw-data folders grouped by NAM, LPS and LTA |
| Library_Change_Log_README.txt | Version history of the library |

## Raw data

The original instrument files are kept unchanged in the project folder (dated folders and `bulk-lta`). The full library with renamed, MD5-verified copies of every raw file and one processed spectrum per raw file is in `SERS_Sepsis_Spectral_Library/`. This package holds the results, not the raw files.

## Reading order

1. `1_Reports/Bulk_Spectral_Library_Report_NAM_LTA_LPS.docx` (overview)
2. The report for each sample: NAM validation, LPS reference, LTA reference
3. `1_Reports/Bulk_Spectral_Marker_Explanation_NAM_LPS_LTA.docx` (why each target band was chosen)
4. `1_Reports/DFT_vs_Experimental_Comparison_NAM_LPS_LTA.docx` and `Simulation_Methods_and_Spectra_NAM_LPS_LTA.docx`

## Points to know

- The band near 1367 cm⁻¹ (zone 1308–1455 cm⁻¹) comes from the glass slide and is not an analyte marker.
- Band assignments are tentative ("consistent with"); they do not prove identity.
- Laser power is given as % of the instrument maximum and is not converted to mW.
- LTA: 55 of 99 spectra of 28 Oct 2026 have a dark frame that contains sample light. They are flagged and not used in any reference.
- Purity of the LTA lot is not recorded (certificate of analysis not yet obtained).
