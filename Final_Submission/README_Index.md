# Final submission: Raman spectra and molecular simulation of NAM, LTA and LPS

Bulk (neat powder) Raman spectra measured on glass slides with a 785 nm instrument, and calculated Raman spectra of molecular models, for N-acetylmuramic acid (NAM), lipoteichoic acid (LTA) and lipopolysaccharide (LPS). Laser power is given as a percentage of the instrument maximum.

## Reports (nine Word documents)

| Folder | Document | Contents |
|---|---|---|
| 01_Bulk_Experimental_Reports | NAM_Bulk_Spectral_Analysis.docx | Reference spectrum, processing, main peaks, glass-slide check and choice of measurement condition for NAM |
| | LTA_Bulk_Spectral_Analysis.docx | The same for LTA; all LTA spectra compared to choose the condition |
| | LPS_Bulk_Spectral_Analysis.docx | The same for LPS |
| 02_Molecular_Simulation_Reports | NAM_Molecular_Simulation_Report.docx | Model, method, calculated spectrum and assignment of the main vibrations (whole NAM molecule) |
| | LTA_Molecular_Simulation_Report.docx | The same for the whole-molecule LTA model (glycerol-phosphate chain with D-alanine and N-acetylglucosamine) |
| | LPS_Molecular_Simulation_Report.docx | The same for the whole-molecule lipid A model |
| 03_Simulation_vs_Bulk_Reports | NAM_Simulation_vs_Bulk_Comparison.docx | Measured and calculated spectra, peak-by-peak comparison with shifted peaks marked separately and explained, close-ups, glass-slide comparison, structure assignment |
| | LTA_Simulation_vs_Bulk_Comparison.docx | The same for LTA |
| | LPS_Simulation_vs_Bulk_Comparison.docx | The same for LPS |

## Data

| Folder | Contents |
|---|---|
| 04_Spectral_Library | Reference spectra (mean ± SD, members, marker peaks); processed spectra; renamed copies of the raw spectra; metadata and peak workbook; literature table; quality-control records |
| 05_Simulation_Data | Final calculation files for NAM (beta form), LTA model and LPS (lipid A) model: structures, Gaussian inputs and outputs, calculated modes and spectra |
| 06_Analysis_Tables | For each molecule: calculated peaks with vibration type, peak-by-peak comparison with measurement, and the measured and calculated spectra on a common axis (data behind the figures) |

## How to read the comparison

A measured peak "agrees" when a calculated vibration of the expected type lies within 10 cm-1. It is "shifted, same vibration type" when the nearest calculated vibration of the same type is 10 to 50 cm-1 away: the peak is judged to come from the same bond or group but at a displaced position, and the reason for the shift is given. "Not reproduced" means no calculated vibration of that type lies within 50 cm-1. No spectrum was shifted or rescaled to improve agreement. The band near 1367 cm-1 (zone 1308 to 1455 cm-1) comes from the glass slide and is not used as evidence. Vibration types come from which atoms move in each calculated vibration and are tentative. The calculations support peak assignments but do not by themselves identify a molecule.
