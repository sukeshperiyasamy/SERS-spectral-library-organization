# QC, replicate and representative-spectrum methodology

## Initial QC (before preprocessing)
| Check | Rule | Basis |
|---|---|---|
| Saturation | raw ≥ 65 000 counts. Checked over full range AND 400–1800 cm-1. Laser-line-only saturation is recorded but not a rejection reason. | 16-bit detector limit (physical) |
| Distortion | negative dark-subtracted counts, abnormal dark reference, strong ripple (noise ≫ group) → exclude | acquisition artefact |
| Contamination | foreign pattern, e.g. polystyrene 620/1001/1031/1602 cm-1 → exclude, keep for review | chemical identity |
| Identity | correlation with class mean (glass zone excluded) | see below |

## Post-processing QC (sheet 22_QC_Extended)
Metrics per spectrum: SNR, robust noise, max/min counts, baseline mean/range/slope, dynamic range (max/noise), strongest-marker prominence, spikes removed, Pearson r with group mean.
Acceptance (project conventions): SNR ≥ 10; r ≥ 0.85 with the glass zone 1308–1455 cm-1 excluded. Low-SNR spectra are kept (parameter comparison) but never used in a reference.
A spectrum that "looks different" is not rejected until the cause is checked (glass background, noise level, acquisition settings).

## Replicate comparison
- Pearson r between all pairs of normalised spectra (glass zone excluded).
- Spot independence is recorded: repeated acquisitions at one spot measure instrument repeatability; different spots measure sample heterogeneity. Only different spots count as independent replicates.
- NAM reference (90 %/30 s/5 acc): 5 different points + 10 same-spot repeats. Same-spot marker CV ≈ 1–2 %; different-point CV ≈ 5–7 %.

## Final 10–15 spectrum selection
All QC-passing spectra acquired at the reference condition are retained (no highest-intensity or best-looking selection). If fewer than 10 independent spectra pass, re-acquisition is recommended; the set is never filled with spectra from other conditions.

## Mean vs median
mean(ν) = (1/n) Σ x_i(ν);  median(ν) = median(x_1(ν) … x_n(ν)).
The mean is efficient when spectra scatter symmetrically; the median is robust to outliers. Rule: if r(mean, median) ≥ 0.999 and |mean − median| < 1 SD at every wavenumber, the population is consistent and the mean is used (median stored alongside). Results: NAM r = 0.9991, LTA r = 0.9990 → mean. LPS spectra are not mutually consistent (pairwise r down to −0.47) → no representative spectrum.
