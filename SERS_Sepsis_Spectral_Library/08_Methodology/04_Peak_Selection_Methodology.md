# Peak detection, promotion and assignment

1. Detection: in each baseline-corrected replicate, local maxima with prominence ≥ 5 × noise (scipy.signal.find_peaks, min. distance 5 points).
2. For each candidate band (±8 cm-1 window): mean position ± SD, mean intensity ± SD, CV, SNR, prominence, detection frequency (reference group, every measurement day, independent-spot set).
3. Promotion criteria (sheet 19; thresholds are project conventions):
   - C1 Reproducibility: detected in all reference spectra; ≥ 95 % of valid spectra on every measurement day (NAM) or ≥ 8/9 valid spectra (LTA); all independent spots (NAM).
   - C2 Signal: SNR ≥ 15 and intensity CV ≤ 15 %.
   - C3 Background separation: outside glass zone 1308–1455 cm-1; ≥ 90 % of height retained after exploratory glass-template correction; ≥ 75 cm-1 from the processing-range edges (ALS end effects); not a fixed pixel or contamination band.
   - C4 Chemical plausibility: position within a documented group-frequency region for a functional group present in the molecule.
4. Categories: Primary = C1–C4; Supporting = all reference spectra and ≥ 90 % overall but fails ≥ 1 criterion; Glass/background = inside glass zone and removed by glass correction; Uncertain = otherwise.
5. Literature: evidence types are kept separate — pure-compound Raman of the biomarker (none found), pure related compounds (reviews), biological-sample Raman/FTIR, SERS. Confidence: High = compound-specific normal-Raman match; Moderate = established group frequency consistent with the known structure plus related compound-class evidence; Low = general group-frequency region only; Uncertain = no assignment.
6. Wording: "observed experimental Raman band", "candidate marker peak", "literature-consistent band", "proposed vibrational assignment (tentative)". A band never "proves" identity.
