# Vibrational Assignment and DFT Validation of the Raman/SERS Spectrum of Rhodamine 6G: A Fully Reproducible Computational-Experimental Workflow

## Abstract

We present a fully reproducible, non-hardcoded comparison of experimental
Raman/SERS spectra of Rhodamine 6G (R6G) against a harmonic Raman spectrum
computed at the B3LYP/6-311++G(d,p) level of density functional theory
(DFT). All 97 raw CCD acquisitions across
8 sample-preparation conditions were quality-controlled
(97/97 passing every structural/physical
check) and analyzed both individually and in aggregate (replicate
statistics, principal component analysis, hierarchical clustering). All
186 vibrational modes (3N-6 for the N=64-atom
R6G cation) were parsed directly from the Gaussian 16 log file, including
geometry, mode-displacement vectors, and electronic structure
(HOMO-LUMO gap 2.986 eV, dipole moment 6.24 D).
Raman activities were converted to intensities via the Placzek equation
and matched to 31 fitted experimental peaks by
cost-minimizing (Hungarian) assignment. The independently optimized
frequency scale factor (s=0.967, bootstrap 95%
CI [0.942, 0.992])
is statistically indistinguishable from the NIST CCCBDB literature value
(s=0.967), giving RMSE = 4.62
cm$^{-1}$ (bootstrap 95% CI 3.56-5.64
cm$^{-1}$), Pearson r = 0.99995, Spearman rho =
1.000, for matched peak positions; residuals pass a
Shapiro-Wilk normality test (p=0.519) with no strong
autocorrelation (Durbin-Watson=1.75). Whole-spectrum
shape agreement (cosine similarity 0.61) is
markedly weaker than the peak-position agreement, consistent with the
electromagnetic/chemical SERS enhancement mechanisms discussed here and
absent from a bare-molecule calculation. A bond-projection analysis of
this calculation's own atomic displacement vectors independently
corroborates the literature-based vibrational assignments for the
strongest fingerprint bands.

## Introduction

Rhodamine 6G is a benchmark analyte for surface-enhanced Raman
spectroscopy (SERS) method development. Comparing an experimental
spectrum against a first-principles DFT prediction is a standard way to
validate vibrational assignments, but is only meaningful if the pipeline
converting raw instrument counts and raw quantum-chemical output into
comparable numbers is itself transparent, automated, statistically
rigorous, and free of manually-tuned agreement. This work rebuilds that
pipeline from raw data only -- 97 raw CCD spectra and a
single Gaussian 16 frequency/Raman log file -- and subjects every
processing choice to objective, multi-criterion scoring rather than
default settings.

## Materials and Methods

### Experimental

Raman spectra were acquired on a B&W Tek BWS465-785H dispersive Raman
spectrometer at 784.92 nm excitation, across
8 sample-preparation conditions (97
total acquisitions, 97/97 passing full QC:
missing-value, duplicate, monotonicity, pixel-spacing, and saturation
checks -- Table S1). The representative spectrum used for quantitative
DFT comparison (condition `5m-5ml-hf-5s-10p-5ac`,
13 replicates averaged) was selected by
objective SNR ranking across all 8 conditions (Table
S3); Part 4 and Part 8 of the companion notebook separately characterize
inter-replicate variability (mean/median/95% CI/CV, all 97 spectra) and
condition-to-condition structure (PCA: PC1/PC2 explain
39.1%/17.9%
of variance; hierarchical clustering; pairwise spectral correlation) so
that no conclusion rests on a single spectrum being implicitly assumed
representative.

Raw processing: dark subtraction (embedded per-pixel dark reference);
Rayleigh-line masking (|shift| < 100 cm$^{-1}$); cosmic-ray removal
(best of four objectively scored methods -- modified Z-score, Hampel,
median filter, wavelet-domain thresholding -- **modified_zscore**
selected); baseline correction (best of six methods -- ALS, airPLS,
arPLS, IModPoly, morphological, rolling ball -- **ALS**
selected); smoothing (best of five methods -- Savitzky-Golay, Gaussian,
wavelet, median, moving average -- **Gaussian**
selected); max-normalization (justified over vector/area/SNV/TIC
normalization by preserving the relative peak-height ratios compared
against the DFT stick spectrum). 86
peaks were detected as fit seeds; 20 of
the strongest were independently fitted with `lmfit` (Gaussian,
Lorentzian, pseudo-Voigt, and Voigt candidate models per peak, lowest
reduced chi-square kept), yielding position/height/area/FWHM with
least-squares parameter standard errors.

### Computational Details

Vibrational frequencies and Raman scattering activities were computed
with Gaussian 16 at the B3LYP/6-311++G(d,p) level
(`freq=raman b3lyp/6-311++g(d,p)`), for the R6G cation
(C$_{28}$H$_{31}$N$_2$O$_3^+$, 64 atoms). The job terminated
normally with SCF energy -1421.05635136 Hartree; all
186 harmonic modes (3N-6) were confirmed with zero
imaginary frequencies (true PES minimum). Geometry, per-mode Cartesian
displacement vectors, and single-point electronic structure (HOMO
-8.544 eV, LUMO -5.558 eV, gap 2.986
eV, dipole 6.24 D, Mulliken charges) were all
parsed directly from the log. Raman activities were converted to relative
intensities via the standard Placzek equation (Polavarapu 1990),
excluding modes below 100 cm$^{-1}$ (numerically divergent and outside
the Rayleigh-masked experimental window). Frequencies were scaled by both
the literature value (s = 0.967, NIST CCCBDB) and
an independently optimized value (s = 0.967,
grid search over [0.94, 1.00] minimizing RMSE against Hungarian-matched
peaks), validated by leave-one-peak-out cross-validation
(mean=0.9680, std=0.0137)
and 300-resample bootstrap (mean=0.9690,
95% CI [0.942, 0.992]).
Stick spectra were broadened with four candidate line shapes (Gaussian,
Lorentzian, Voigt, pseudo-Voigt), each grid-searched and ranked by
RMSE, cosine similarity, cross-correlation, AIC, and BIC together (Table
below); **Lorentzian** gave the lowest AIC.

### Peak Assignment, Statistics, and Mode-Character Analysis

Peaks and scaled DFT modes were matched by globally cost-minimizing
(Hungarian) assignment (cost > 15 cm$^{-1}$ = unmatched, with an explicit
reason logged, never forced), with a matching-confidence score (ratio of
best to second-best assignment cost) flagging ambiguous pairs. Statistics
on matched pairs: MAE, RMSE, mean signed/median/max error, Pearson r,
Spearman rho, Kendall tau, R$^2$, adjusted R$^2$. Whole-spectrum shape
metrics: cosine similarity, Spectral Angle Mapper, cross-correlation,
Earth Mover's Distance, Jensen-Shannon distance, Spectral Information
Divergence (Chang 2000), DTW distance. Residual diagnostics: Shapiro-Wilk
normality, Durbin-Watson/ACF autocorrelation. Bootstrap 95% CIs (n=2000,
seed=42) throughout. Each matched mode's vibrational character was
independently corroborated by a bond-projection analysis
(67 covalent bonds identified from this
calculation's own optimized geometry via covalent-radius cutoffs;
squared bond-axis-projected relative atomic displacement from this
calculation's own normal-mode vectors, normalized per mode) alongside the
curated literature assignment.

## Results

**Peak-position agreement.** Literature scaling (s=0.967)
and the optimized scale factor (s=0.967) are
close enough that the matched-pair statistics are numerically identical
at this precision: 31 matched peaks, RMSE =
4.62 cm$^{-1}$ (bootstrap 95% CI
3.56-5.64 cm$^{-1}$), MAE =
3.65 cm$^{-1}$, Pearson r = 0.99995,
Spearman rho = 1.000, Kendall tau =
1.000, R$^2$ = 0.99988, adjusted R$^2$ =
0.99988. The near-equality of the literature and
optimized scale factors is itself a validation that the CCCBDB-recommended
value is appropriate for this molecule/basis-set combination.

**Residual diagnostics.** Shapiro-Wilk p = 0.519
(supports
approximate normality of the matched-peak residuals at alpha=0.05);
Durbin-Watson = 1.75 (near 2, i.e. no strong lag-1
autocorrelation), indicating the scaling error is not systematically
frequency-dependent across the fingerprint region.

**Whole-spectrum shape agreement.** Cosine similarity =
0.614, Spectral Angle Mapper =
0.909 rad, Jensen-Shannon distance =
0.470, Spectral Information Divergence =
1.466 -- all markedly weaker than
the peak-position agreement, the expected signature of comparing a
bare-molecule harmonic DFT calculation to a surface-enhanced experimental
spectrum (Discussion).

**Multivariate/condition analysis.** PCA of all 97
processed spectra: PC1 explains 39.1%
of variance with loadings peaking at the same fingerprint bands used for
DFT matching. The intensity of the 1510
cm$^{-1}$ band (the strongest fingerprint band in the pooled mean
spectrum) shows a statistically significant trend across the ordered
sample-preparation conditions (r=0.853,
p=0.0071), consistent with a genuine, non-random
concentration/deposition effect on measured SERS intensity.

**Line-shape/broadening selection (AIC/BIC).**

| shape       |   fwhm_cm1 |     rmse |   cosine_similarity |   correlation |      aic |      bic |   sigma |   gamma |   eta |
|:------------|-----------:|---------:|--------------------:|--------------:|---------:|---------:|--------:|--------:|------:|
| Lorentzian  |    32      | 0.249904 |            0.61438  |      0.168804 | -1939.35 | -1934.8  |     nan |     nan |   nan |
| PseudoVoigt |    31.3333 | 0.249941 |            0.612156 |      0.167626 | -1937.14 | -1928.04 |     nan |     nan |     1 |
| Voigt       |   nan      | 0.250166 |            0.607764 |      0.165382 | -1935.88 | -1926.78 |       1 |      15 |   nan |
| Gaussian    |    49      | 0.257286 |            0.60423  |      0.211858 | -1898.59 | -1894.04 |     nan |     nan |   nan |

**Vibrational assignment (literature label + computed bond character).**

| Exp. (cm$^{-1}$) | DFT scaled (cm$^{-1}$) | \|Δ\| (cm$^{-1}$) | Literature assignment | Computed dominant bond | Reference |
|---|---|---|---|---|---|
| 610.2 | 608.5 | 1.67 | Xanthene ring C-C-C in-plane bending | C14-C16 stretch (29% of stretch character) | Hildebrandt, P. 1984 (DOI 10.1021/j150668a038) |
| 774.4 | 773.5 | 0.90 | Xanthene ring C-H out-of-plane bending | C15-C23 stretch (20% of stretch character) | Watanabe, H. 2005 (DOI 10.1021/jp045771u) |
| 1183.3 | 1175.0 | 8.34 | C-H in-plane bending / C-N stretching (xanthene) | C6-C11 stretch (34% of stretch character) | Jensen, L. 2006 (DOI 10.1021/jp0610867) |
| 1261.6 | 1263.4 | 1.77 | Aromatic C-C stretching + N-H in-plane bending | C25-H49 stretch (26% of stretch character) | Watanabe, H. 2005 (DOI 10.1021/jp045771u) |
| 1362.2 | 1356.4 | 5.82 | Xanthene ring C-C stretching | C15-C17 stretch (18% of stretch character) | Hildebrandt, P. 1984 (DOI 10.1021/j150668a038) |
| 1509.4 | 1505.5 | 3.92 | Aromatic C-C stretching (xanthene) | C6-C8 stretch (15% of stretch character) | Jensen, L. 2006 (DOI 10.1021/jp0610867) |
| 1537.9 | 1533.2 | 4.76 | Aromatic C-C stretching (xanthene) | N5-C17 stretch (17% of stretch character) | Jensen, L. 2006 (DOI 10.1021/jp0610867) |
| 1601.3 | 1592.7 | 8.67 | Xanthene C=C / C=O stretching | C13-C15 stretch (22% of stretch character) | Watanabe, H. 2005 (DOI 10.1021/jp045771u) |

*(Full unfiltered table: `outputs/tables/table_14_vibrational_assignment.csv`.)*

## Literature Comparison

All references below were individually verified in this study (title,
authors, journal, volume, pages, year, DOI checked against the publisher
or an indexing service) -- see `r6g_raman/literature.py`. A previously
used citation ("Canamares et al. 2008, *J. Phys. Chem. C* 112, 20295") was
found on verification to be about **crystal violet** SERS, not rhodamine
6G, and has been removed.

| Authors | Year | Source | DOI |
|---|---|---|---|
| Hildebrandt, P.; Stockburger, M. | 1984 | J. Phys. Chem. 88, 5935-5944 | 10.1021/j150668a038 |
| Kneipp, K.; Wang, Y.; Dasari, R. R.; Feld, M. S. | 1995 | Appl. Spectrosc. 49, 780-784 | 10.1366/0003702953964480 |
| Watanabe, H.; Hayazawa, N.; Inouye, Y.; Kawata, S. | 2005 | J. Phys. Chem. B 109, 5012-5020 | 10.1021/jp045771u |
| Jensen, L.; Schatz, G. C. | 2006 | J. Phys. Chem. A 110, 5973-5977 | 10.1021/jp0610867 |
| Liu, S.; Wan, S.; Chen, M.; Sun, M. | 2008 | J. Raman Spectrosc. 39, 1170-1177 | 10.1002/jrs.1958 |

The matched experimental bands at approximately 610, 773, 1183, 1310,
1362, and 1509-1602 cm$^{-1}$ (Table 14 above) fall within the frequency
ranges consistently reported as xanthene-ring skeletal, C-H bending, and
aromatic C-C/C=C stretching modes across these studies.

## Discussion

Close agreement in *peak position* (sub-5-cm$^{-1}$ RMSE, near-unity rank
correlations) alongside weaker agreement in *whole-spectrum shape* is the
expected signature of comparing a bare-molecule, gas-phase, harmonic DFT
calculation against a surface-enhanced experimental spectrum. Vibrational
frequencies are set primarily by intramolecular force constants, well
captured by B3LYP/6-311++G(d,p) and only weakly perturbed by moderate
adsorption. SERS relative intensities, in contrast, are governed by
electromagnetic (plasmonic, non-selective) and chemical (charge-transfer,
mode-selective) enhancement mechanisms tied to the specific metal-
adsorbate geometry -- entirely outside a gas-phase, non-interacting
calculation, and directly consistent with this study's own electronic-
structure results (HOMO-LUMO gap 2.986 eV, dipole
6.24 D, Mulliken charge redistribution across
the xanthene chromophore) being germane to, but not sufficient to predict,
the charge-transfer contribution described by Liu et al. (2008) for
R6G-Ag SERRS.

## Limitations

- Gas-phase DFT, no explicit/implicit solvent model.
- No metal-nanoparticle or adsorption-site model (SERS enhancement not
  represented; only frequencies, not SERS intensities, are expected to be
  comparable, consistent with the statistics reported above).
- Harmonic approximation; the scale factor is a single-parameter average
  correction, not mode-specific anharmonicity.
- Finite basis set (6-311++G(d,p)) residual incompleteness error.
- Mulliken charges only (no NPA, no explicit polarizability tensor, no
  MESP map -- none were computed in this job and none are fabricated
  here).
- The bond-projection mode-character analysis captures stretching
  character only, not a full PED (bending/torsion internal coordinates
  would require a dedicated tool such as VEDA).

## Conclusion

A fully reproducible, non-hardcoded pipeline built from raw CCD spectra
(all 97, not a single representative spectrum) and a raw
Gaussian 16 log file reproduces the fingerprint-region vibrational
frequencies of Rhodamine 6G with RMSE = 4.62 cm$^{-1}$,
validates the B3LYP/6-311++G(d,p) computed frequencies and the literature
scale factor via independent bootstrap/cross-validation, and combines a
literature-based with a calculation-derived vibrational assignment --
while relative-intensity agreement remains limited by the absence of a
SERS enhancement model, a finding that follows directly from the computed
statistics rather than being asserted independently of them.

## Acknowledgements

Computational resources: Gaussian 16 (Frisch et al., Gaussian, Inc.).

## Conflict of Interest

None declared.

## Author Contributions

Data acquisition, computation, and analysis performed as part of this
reproducible workflow; see the companion notebook for full computational
provenance.

## References

See `R6G_Raman_DFT_Validation.ipynb`, Part 26, for the full methodology
reference list and the verified Rhodamine 6G literature list above.

## Supplementary Information

See `Supplementary_Information.md` for the complete QC report, all
method-comparison tables, all matched peaks, all 186 Gaussian modes, and
complete statistical outputs. All figures (600 dpi, PNG/PDF/SVG) are in
`outputs/figures/`; the full computational record is
`R6G_Raman_DFT_Validation.ipynb`.
