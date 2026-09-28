# Data-analysis workflow — bulk-powder Raman reference library (NAM, LTA, LPS)
Version 3 · 23 Sep 2026 · B&W Tek i-Raman Plus BWS465-785H, 785 nm · bulk powder directly on glass slides

## Decision chain (a peak becomes a final marker only if every step is passed)
valid spectrum → reproducible spectrum → reproducible peak → peak not background → chemically plausible → literature-consistent

## Flow
```
Bulk powder
  ↓  placed directly on a glass slide (no other substrate)
Glass-slide measurement (785 nm; power %, integration, accumulations from file header)
  ↓
Raw Raman spectra (2048-pixel CCD; raw + dark + dark-subtracted columns)
  ↓  Initial QC: file readable, metadata complete, saturation check (full range AND 400–1800 cm-1),
  ↓  negative counts / abnormal dark reference, contamination pattern (e.g. polystyrene 620/1001/1031/1602)
Fixed hot-pixel correction (CCD pixels 640 and 700 = 1095.7 and 1189.5 cm-1)
  ↓
Spectral cropping 400–1800 cm-1
  ↓
Cosmic-ray / spike removal (MAD modified z of first difference > 6 AND width ≤ 2 pixels)
  ↓
Savitzky–Golay smoothing (window 11, order 3)
  ↓
ALS baseline correction (λ = 1e5, p = 0.01)
  ↓
Min–max normalisation (shape comparison only; counts kept separately)
  ↓
Post-processing QC (SNR, noise, baseline, prominence, spikes, correlation with group)
  ↓
Replicate comparison (Pearson r with glass zone 1308–1455 excluded; spot independence)
  ↓
10–15 valid, independent spectra per biomarker (if fewer → re-acquire; never fill with other conditions)
  ↓
Mean + median comparison (mean used if r(mean, median) ≥ 0.999 and |mean − median| < 1 SD everywhere)
  ↓
Representative reference spectrum (mean ± SD; median stored alongside)
  ↓
Peak detection (prominence ≥ 5 × noise in each replicate)
  ↓
Peak reproducibility (detection frequency within group, across days, in independent spots; position SD; intensity CV)
  ↓
Background screen (glass zone, glass-template correction, instrument pixels, fluorescence, cosmic, contamination, processing)
  ↓
Literature comparison (evidence type kept separate: pure-compound Raman / related pure compounds / biological samples / SERS)
  ↓
Chemical / functional-group assignment (TENTATIVE unless compound-specific evidence exists)
  ↓
Final biomarker marker peaks (primary / supporting / glass-background / uncertain)
  ↓
Spectral reference library (03_Reference_Spectra + 05_Tables/Traceability_Table)
```

## Where each step is documented
| Step | Method file | Data / table | Figure |
|---|---|---|---|
| Initial QC | 03_QC_Methodology.md | 05_Tables sheet 22_QC_Extended, 12_NAM_60s_ReAudit | QC1, QC2 (07_QC_and_Exclusions) |
| Preprocessing | 02_Preprocessing_Methodology.md | 02_Processed_Spectra (every stage stored as a column) | Fig01 |
| Parameter sensitivity | 02_Preprocessing_Methodology.md | sheet 23_Preprocessing_Sensitivity | — |
| Replicates / mean vs median | 03_QC_Methodology.md | sheets 17, 18 | Fig02–Fig05, Fig09 |
| Peaks | 04_Peak_Selection_Methodology.md | sheets 19, 21, Traceability_Table | Fig08 |
| Chemistry / literature | 04_Peak_Selection_Methodology.md | sheet 20; 06_Literature/Literature_Peak_Assignments.xlsx | Fig08 |
| Decisions / next measurements | 05_Acquisition_SOP.md | sheets 15, 16, 25 | Fig06, Fig07 |
