# Computed Raman spectrum of an LTA model: how it was made

Quick-reference calculation, single molecule, run 28 Oct 2026 on this PC. Companion to `new lps/output/Lipid_A_Raman_Methods.md`.

## 1. Why this calculation was done
- LTA (lipoteichoic acid) is the Gram-positive counterpart of LPS. *S. aureus* LTA is a polymer of about 23 glycerol-phosphate repeats on a Glc2-diacylglycerol membrane anchor. Position 2 of each glycerol can be unsubstituted, esterified with D-alanine, or carry N-acetylglucosamine.
- Same goal as lipid A: one computed spectrum from **one whole molecule** (not a sum of fragment spectra) to help assign bands in measured spectra.
- The real polymer is far too large, so a short model carrying all three substituent types was used, at a quick level first.

## 2. Where the structure came from
- There is **no single PubChem entry** for LTA (a polymer), so the structure was built, not downloaded.
- The alpha-GlcNAc unit uses the stereochemistry of `LTA/N-Acetyl-D-Glucosamine/N-Acetyl-D-Glucosamine.sdf` (a beta-anomer, R at C1). The anomeric tag was flipped to give the alpha-anomer (S at C1), because LTA GlcNAc is alpha-linked.
- D-alanine stereo set to R (D) on both esters, checked with RDKit CIP labels.

## 3. The model (`build_lta.py`, RDKit 2026.03.3)
- Three glycerol-phosphate units joined by **two phosphodiester links**.
- D-alanine ester on each of the two outer glycerols.
- alpha-GlcNAc on the central glycerol.
- Ionised: each phosphodiester -1 (two), each alanine amine NH3+ (two). **Net charge 0.**
- Formula **C23H45N3O20P2, 93 atoms.**
- SMILES: `CC(=O)N[C@@H]1[C@@H](O)[C@H](O)[C@@H](CO)O[C@@H]1O[C@H](COP(=O)([O-])OC[C@H](OC(=O)[C@@H](C)[NH3+])CO)COP(=O)([O-])OC[C@H](OC(=O)[C@@H](C)[NH3+])CO`
- 3D structure: 300 ETKDGv3 conformers (seed 7), each MMFF-optimised; the lowest-energy one (MMFF energy -311.4 kcal/mol) was used as the starting geometry (`lta_model.sdf`).

## 4. Gaussian settings (Gaussian 16W Revision C.01)
| Job | Route | Notes |
|---|---|---|
| 1 | `# opt pm6` | gas phase, default optimisation criteria, charge 0 |
| 2 | `# opt freq=raman b3lyp/3-21g geom=allcheck guess=read` | gas phase, full optimisation then analytic Raman frequencies |

- Resources: `%nprocshared=28`, `%mem=54GB`.
- Same quick level as lipid A (B3LYP/3-21G, gas phase). One difference: the PM6 stage here used default convergence, not `opt=loose`.
- The job was queued to start automatically after the lipid A job finished.

## 5. What happened in the run
- Started about 09:00 on 28 Oct, right after lipid A finished (08:57).
- PM6 stage finished 09:29.
- B3LYP/3-21G optimisation: converged at **step 75** ("Stationary point found"), finished 12:16.
- Raman frequencies: 49 minutes, **normal termination 13:05**.
- 273 modes (3N-6 = 273), **no imaginary frequencies**, so a true minimum. Lowest mode 31 cm-1.

## 6. How the spectrum was made (`make_spectrum.py`)
- Harmonic frequencies and Raman activities from the Gaussian log (`lta_model_raman_act.csv`).
- Frequencies scaled by **0.965** (typical B3LYP value; **not fitted or benchmarked for 3-21G**).
- Intensity at 785 nm, 298.15 K: I = S (v0 - v)^4 / ( v (1 - exp(-hcv/kT)) ).
- Lorentzian broadening, FWHM 12 cm-1; 200-3300 cm-1; normalised to the tallest peak.

## 7. Results
Strongest features (scaled, cm-1; relative height in the fingerprint region):
- 689 (1.00), 1490 (0.80), 1503 (0.66), 816 (0.33), 654 (0.34), 1325 (0.34), 1240 (0.32), 914 (0.31), 972 (0.30), 1006 (0.29).
- No reference band list for LTA was supplied, so no match table is given. The assignments below are **not verified**:
  - 1490-1503 is probably the NH3+ / amide region.
  - The strong 689 band is probably a phosphate P-O-C or ring deformation mode.
- Mode-by-mode assignments need a check of the vibrational displacements in GaussView (open `lta_model.out`).

## 8. Limitations - read before using the spectrum
- **Quick level**: gas phase, B3LYP/3-21G. Positions are approximate, intensities distorted, especially for charged groups.
- **Peaks at about 2410, 2510 and 2700-2800 cm-1 are probably artefacts**: strongly hydrogen-bonded N-H/O-H stretches between the NH3+ groups and the phosphates, which happen without water around. Ignore that region.
- **Short chain**: 3 glycerol-phosphate units instead of about 23, and **no Glc2-diacylglycerol anchor**. Repeating-unit bands will be under-represented relative to a real polymer, and chain-end effects are exaggerated.
- **Stereochemistry assumed**: the two glycerol arms were set to the same configuration, not checked against the S. aureus sn-glycerol-1-phosphate form.
- No counter-ions (Na+, Mg2+, Ca2+) and no water.
- Comparison with experiment: activities are orientation-averaged (comparable to powder or solution). Compare peak positions, not absolute intensities. SERS spectra should be compared for positions only.

## 9. Planned next step
Rerun at B3LYP/6-31G(d) or the NAM level with water (PCM), starting from this geometry; this model is small, so it is a cheaper test than lipid A. Consider a longer chain (4-5 units) and adding the anchor.

## 10. Files in this folder
- `lta_model.gjf`: Gaussian input (both jobs)
- `lta_model.sdf`: starting 3D structure (before optimisation)
- `lta_model.out`: full Gaussian log
- `lta_model_raman_act.csv`: frequencies and activities (unscaled)
- `lta_model_spectrum_785nm.csv` / `.png`: scaled, broadened 785 nm spectrum
- `make_spectrum.py`: spectrum script (`python make_spectrum.py lta_model`)
- `build_lta.py`: builds the model and the Gaussian input
- `LTA_Raman_Methods.md`: this document
