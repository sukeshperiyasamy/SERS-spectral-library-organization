# Preprocessing methodology (pipeline v3)
All steps are applied identically to every spectrum. Every intermediate stage is stored as a separate column in the processed CSV
(Raw, DarkSubtracted, HotPixelFixed, Despiked, Smoothed, Baseline, BaselineCorrected, Normalised). Raw files are never modified.

## Step 0 — Input and fixed hot-pixel correction
**What:** the instrument's dark-subtracted counts (Raw − Dark) are used. Two CCD pixels (index 640 → 1095.7 cm-1 and 700 → 1189.5 cm-1) are replaced by the mean of their two neighbours.
**Why:** these pixels were flagged in ≥ 59 spectra on 6 different dates and are visible in the dark frames — a fixed detector defect, not a Raman band or a cosmic ray. In the NAM reference spectra pixel 700 carried ≈ +950 counts; in the LPS spectra pixel 640 produced a sharp "band" near 1095 cm-1.
**Effect:** removes an artificial one-pixel feature; neighbouring data unchanged. **QC:** listed in each processed-file header. **Limitation:** assumes the defect list is complete; re-check with every new dark frame.

## Step 1 — Spectral cropping (400–1800 cm-1)
**What:** keep 400 ≤ Raman shift ≤ 1800 cm-1 (≈ 750 pixels).
**Why:** this is the molecular fingerprint region where skeletal, C–O/C–C, C–O–C, phosphate and CH-deformation bands of the three biomarkers occur. Below 400 cm-1 the Rayleigh/laser-line edge (≈ 0 cm-1; saturates at long integration) and filter edge dominate; above 1800 cm-1 the 785 nm detector response falls and the C–H stretch region (2800–3100) is outside this spectrometer's useful range.
**Excluded information:** low-frequency lattice modes and C–H/N–H/O–H stretching bands. **QC:** saturation is checked BOTH over the full range and inside 400–1800 (laser-line saturation alone is not a rejection reason).

## Step 2 — Cosmic-ray / spike removal
**What is a spike:** a cosmic ray (or random detector event) deposits charge in 1–2 pixels, giving a narrow, very intense feature at a random position in a single spectrum.
**Why remove:** a spike can be mistaken for a band, distorts smoothing and inflates peak heights.
**Method:** on the first difference d_i = x_{i+1} − x_i:
- MAD = median(|d_i − median(d)|)
- robust (modified) z-score z_i = 0.6745 · (d_i − median(d)) / MAD  (0.6745 makes MAD consistent with the SD of normal noise)
- candidate if |z_i| > 6 (project convention; ≈ 6 robust SDs, very unlikely for noise)
- **width guard (v3):** a candidate is accepted as a spike only if ≤ 2 pixels exceed half of its local excursion. Genuine Raman bands in these spectra are ≥ 3–4 pixels wide.
- accepted points (±1 pixel) are replaced by linear interpolation from unflagged neighbours.
**Why the width guard:** without it (v2.1) the z-test also fired on the steep flanks of the sharp crystalline NAM bands (≈ 5 points per spectrum at 460–960 cm-1) and clipped their apex; marker heights were under-estimated by 11–12 % on average. With the guard, 0 spikes are removed from the NAM and LTA reference spectra and genuine peaks are untouched.
**Preservation:** the un-despiked data remain in the DarkSubtracted/HotPixelFixed columns; positions of removed spikes are listed in the file header.

## Step 3 — Savitzky–Golay smoothing (window 11, order 3)
**Why:** reduces high-frequency detector/shot noise so that peak positions and heights can be measured reproducibly.
**How:** in a sliding window of 11 points a cubic polynomial is fitted by least squares and the centre point is replaced by the fitted value. Unlike moving averaging, the local polynomial follows curvature, so peak position and shape are largely preserved.
**Why 11/3 (project convention):** 11 points ≈ 20 cm-1; residual high-frequency noise falls to ≈ 25 % of the unsmoothed level.
**Measured effect (sheet 23):** peak positions shift ≤ 1 pixel (≤ 1.7 cm-1). The apex of the narrow NAM bands (FWHM ≈ 10 cm-1) is lowered by ≈ 16 % (SG 7/3: 6 %; 15/3: 26 %); the broad LTA bands by ≈ 3 %.
**Risk of over-smoothing:** larger windows merge close bands and flatten sharp ones; they do not create new bands. Absolute NAM intensities are therefore pipeline-specific; for future crystalline-powder work a 7/3 window may be considered (PI decision) — the current library keeps 11/3 for consistency.

## Step 4 — Asymmetric least-squares (ALS) baseline correction (λ = 1e5, p = 0.01)
**Background:** broad fluorescence, glass-slide background and instrument response add a slowly varying baseline under the Raman bands (NAM ≈ 1 360 counts; LTA ≈ 8 300 counts).
**Why:** band heights and shapes must be measured from a common zero level.
**Method (Eilers & Boelens):** find baseline z minimising  Σ w_i (y_i − z_i)² + λ Σ (Δ²z_i)²
- first term: fidelity to the data; second term: roughness penalty (second differences).
- λ (1e5) controls stiffness: larger λ → smoother baseline that cannot follow bands.
- p (0.01) sets asymmetric weights: w_i = p if y_i > z_i (points above the baseline, i.e. peaks, are almost ignored), 1 − p otherwise. Iterated 10 times.
**Why these values:** baseline follows the fluorescence envelope without cutting into bands 10–50 cm-1 wide.
**Effect on intensity (sheet 23):** NAM marker heights change < ±12 % over λ = 1e4–1e6 and p = 0.001–0.05; LTA heights change −40 % to +25 %, because LTA sits on a strong, curved fluorescence background. LTA absolute intensities are therefore parameter-dependent.
**Limitation:** the ALS baseline partly follows the broad glass band (FWHM ≈ 110 cm-1); a residual glass contribution remains in 1308–1455 cm-1, so bands in this zone are not used as primary markers.

## Step 5 — Min–max normalisation
x_norm = (x − x_min) / (x_max − x_min), applied to the baseline-corrected spectrum.
**Why:** removes differences in overall intensity (focus, packing density, power) so spectral SHAPES can be compared and correlated.
**Rule:** normalised data are never used to report bulk Raman counts. Raw, baseline-corrected and normalised spectra are kept as separate columns.

## Noise and SNR definitions
noise = 1.4826 · MAD(despiked − smoothed) (robust SD of the high-frequency residual);
SNR = height of the strongest marker band (baseline-corrected) / noise. v2.1 used the plain SD, which was inflated by sharp peaks.
