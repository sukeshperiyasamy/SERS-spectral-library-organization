# Acquisition SOP for re-acquisition (bulk powder directly on glass slides)
Instrument: B&W Tek i-Raman Plus BWS465-785H, 785 nm. No other substrate. Record the OBJECTIVE (it is not stored in the file header).

## Conditions (based on the existing-data analysis)
| Biomarker | Condition | Spectra | Blanks |
|---|---|---|---|
| NAM (top-up) | 90 %, 30 s, 5 acc | 10–15 independent spots (≥ 2 slides, ideally 2 days) | 3 empty-glass spectra, same settings |
| LTA | 80 %, 45 s, 2 acc | 10–15 independent spots | 3 empty-glass spectra, same settings |
| LPS screening | 70 %, 80 %, 90 % × 30 s × 5 acc | ≥ 5 independent spots per power | ≥ 3 empty-glass spectra per power |
| LPS final | selected power, 30 s, 5 acc | 10–15 independent spots | 3 empty-glass spectra |

## Procedure
1. Same glass-slide type/lot for sample and blank; note lot.
2. Spread a thin, flat layer of powder; record amount/preparation.
3. Focus on the powder surface; use a NEW spot for every replicate (record position). Do not repeat the same spot to increase n.
4. Acquire the matched empty-glass blank at exactly the same wavelength, power, integration, accumulations, objective and slide type.
5. After each spectrum check: raw max in 400–1800 cm-1 < 60 000 counts; no negative dark-subtracted counts; dark frame normal. If saturated: reduce power, then integration; document.
6. Name files: <Analyte>_Bulk_<YYYYMMDD>_P<power>pct_T<time>s_A<acc>_S<rep>.csv; blanks Glass_Blank_<YYYYMMDD>_P..pct_T..s_A.._S...csv.
7. Fill Acquisition_Log_Template.csv (one row per spectrum).

## LPS reference selection rule
Select the power giving the best combination of SNR, reproducibility (pairwise r, marker CV), intensity, absence of saturation and separation from the glass background (bands present in LPS + glass, absent from the matched blank, in most spots, SNR ≥ 10 after blank comparison).
