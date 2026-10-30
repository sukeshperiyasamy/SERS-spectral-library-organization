# Final submission: Raman spectra and molecular simulation of NAM, LTA and LPS

Bulk pure biomarker Raman spectra measured with a 785 nm instrument, and calculated Raman spectra of molecular models, for N-acetylmuramic acid (NAM), lipoteichoic acid (LTA) and lipopolysaccharide (LPS). Laser power is given as a percentage of the instrument maximum.

## Reports (nine Word documents)

|Folder|Document|Contents|
|-|-|-|
|01\_Bulk\_Experimental\_Reports|NAM\_Bulk\_Spectral\_Analysis.docx|Reference spectrum, processing, main peaks, glass-slide check and choice of measurement condition for NAM|
||LTA\_Bulk\_Spectral\_Analysis.docx|The same for LTA; all LTA spectra compared to choose the condition|
||LPS\_Bulk\_Spectral\_Analysis.docx|The same for LPS|
|02\_Molecular\_Simulation\_Reports|NAM\_Molecular\_Simulation\_Report.docx|Model, method, calculated spectrum and assignment of the main vibrations (whole NAM molecule)|
||LTA\_Molecular\_Simulation\_Report.docx|The same for the whole-molecule LTA model (glycerol-phosphate chain with D-alanine and N-acetylglucosamine)|
||LPS\_Molecular\_Simulation\_Report.docx|The same for the whole-molecule lipid A model|
|03\_Simulation\_vs\_Bulk\_Reports|NAM\_Simulation\_vs\_Bulk\_Comparison.docx|Measured and calculated spectra, peak-by-peak comparison with shifted peaks marked separately and explained, close-ups, glass-slide comparison, structure assignment|
||LTA\_Simulation\_vs\_Bulk\_Comparison.docx|The same for LTA|
||LPS\_Simulation\_vs\_Bulk\_Comparison.docx|The same for LPS|

## Data

|Folder|Contents|
|-|-|
|04\_Spectral\_Library|Reference spectra (mean ± SD, members, marker peaks); processed spectra; renamed copies of the raw spectra; metadata and peak workbook; literature table; quality-control records|
|05\_Simulation\_Data|Final calculation files for NAM (beta form), LTA model and LPS (lipid A) model: structures, Gaussian inputs and outputs, calculated modes and spectra|
|06\_Analysis\_Tables|For each molecule: calculated peaks with vibration type, peak-by-peak comparison with measurement, and the measured and calculated spectra on a common axis (data behind the figures)|




## SERS report

| Folder | Document | Contents |
|---|---|---|
| 07_SERS_Report | SERS_Spectra_NAM_LPS_LTA_Report.docx | Surface-enhanced Raman spectra of NAM, LPS and LTA on etched silicon from the most recent session: what was measured, detection tests against the blank and chance, the reproducible LPS band set, and next steps |

## LPS: SERS compared with the simulation

| Folder | Document | Contents |
|---|---|---|
| 08_LPS_SERS_vs_Simulation | LPS_SERS_vs_Simulation_Comparison.docx | The ten reproducible SERS bands of LPS compared with the calculated lipid A spectrum and the bulk LPS spectrum, with matched and shifted bands marked, chance test and structure assignment |

## SERS: all sessions

| Folder | Contents |
|---|---|
| 09_SERS_All_Sessions | All 868 SERS spectra from eight sessions (June to October 2026), fetched from E:\sukesh and the mtp repository. 01 = renamed raw copies (MD5-checked), 02 = processed spectra, 03 = figures, 04 = SERS_All_Sessions_Workbook.xlsx and CSV tables, 05 = earlier analyses copied from mtp, 06 = SERS_All_Sessions_Analysis_Report.docx |
| 10_SERS_Chip_Fabrication | SERS_Chip_Fabrication_Process.docx: how the silver-etched silicon chips were made (from the mtp SOP, roadmap, lab note and photos), the recipes used, how each recipe performed with R6G, and the open items; figures and photos |

Folders 01 and 02 of 09_SERS_All_Sessions are not stored in git (about 200 MB). Run `SERS_Sepsis_Spectral_Library/08_Methodology/code/final_reports/sers_all.py` to rebuild them from E:\sukesh.

## Expected peaks (combined summary)

| Folder | Document | Contents |
|---|---|---|
| 11_Expected_Peaks_Summary | Expected_Peaks_NAM_LPS_LTA_Summary.docx | Bulk, simulation and SERS combined: one figure showing only the expected peaks of NAM, LPS and LTA, and a table per molecule explaining why each peak is expected and targeted, with the future work direction |
