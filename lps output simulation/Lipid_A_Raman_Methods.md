# Computed Raman spectrum of shortened Kdo2-lipid A: how it was made

Quick-reference calculation, single molecule, run 27-28 Oct 2026 on this PC.

## 1. Why this calculation was done
- Sample of interest: *E. coli* O111:B4 LPS (commercial, smooth LPS = lipid A + core oligosaccharide + O-antigen). It is a heterogeneous mixture of chains, so no single molecule matches the sample exactly.
- Goal: a computed Raman spectrum from **one whole molecule** (not a sum of fragment spectra) to assign bands in measured LPS spectra.
- Reference bands from the SERS endotoxin paper in `LPS/excelsheet/thesis report.txt`: 850 (glycosidic), 989 (Kdo / carbohydrate), 1131 (lipid chain), 1330 (phosphate / amide).
- The fragment approach used earlier (Kdo, glucosamine, heptose, myristic acid, phosphoric acid in `LPS/`) was set aside because a single-molecule spectrum was wanted.
- The full LPS is tens of thousands of atoms (impossible at any quantum level), and full Kdo2-lipid A (355 atoms) is too large for B3LYP/6-31+G(d,p) Raman on this PC. So the **backbone of Kdo2-lipid A with shortened acyl chains** was used as the model, as a quick reference first; a higher-level run is planned afterwards.

## 2. Where the structure came from
- PubChem compound **CID 5771770** (Kdo2-lipid A, *E. coli*): https://pubchem.ncbi.nlm.nih.gov/compound/5771770
- Downloaded as 2D SDF: `new lps/Structure2D_COMPOUND_CID_5771770.sdf`
- Checked after download: formula C110H202N2O39P2, 355 atoms, neutral, matches the expected formula.
- The CID was found through a GlyCosmos listing (LIPID MAPS id LMSL02000001). A second entry, CID 25244473, has a different formula (C110H196...) and was not used.
- PubChem leaves a few ring stereocentres unspecified. They could not be set, and the embedding picked them arbitrarily (one reasonable structure, not necessarily the global minimum).

## 3. How the model was built (`new lps/build_model.py`, RDKit 2026.03.3)
1. Read the SDF and took its SMILES with the PubChem stereochemistry.
2. **Shortened the six acyl chains**: C14 acyl to butyryl; the C11 tails of the 3-acyloxy chains to propyl; the C12 acyl to butyryl. Backbone kept complete: 2 glucosamines, 2 Kdo, 2 phosphates, 2 amides, all stereo tags.
3. **Ionised for water at near-neutral pH**: both Kdo carboxylates to COO-, both phosphate monoesters to one negative charge each. Net charge **-4**. No counter-ions included.
4. Result: C60H98N2O39P2 (4-), **201 atoms**.
5. 3D structure: 300 conformers by ETKDGv3 (random seed 7), each optimised with MMFF; lowest-energy one (#110, MMFF energy 139.7 kcal/mol) used as the starting geometry. Saved as `lipidA_short.sdf`.
6. Wrote the Gaussian input `lipidA_short.gjf`.

## 4. Gaussian settings (Gaussian 16W Revision C.01, `C:\G16W\g16.exe`)
Two linked jobs in one input:

| Job | Route | Notes |
|---|---|---|
| 1 | `# opt=loose pm6` | gas phase, loose optimisation, charge -4, singlet |
| 2 | `# opt freq=raman b3lyp/3-21g geom=allcheck guess=read` | gas phase, full optimisation then analytic Raman frequencies |

- Resources: `%nprocshared=28`, `%mem=54GB` (28 logical threads of an i7-14700, 64 GB machine).
- Environment variables needed from the command line: `GAUSS_EXEDIR=C:\G16W`, `GAUSS_SCRDIR=C:\G16W\Scratch` (the first launch failed without them).
- Run history: an earlier version used PM6 in water (PCM) and was far too slow, then a B3LYP/6-31G(d) in-water plan was replaced by this quick level at the user's request. The abandoned PM6/PCM run is archived in `old_pm6_pcm/`.

## 5. What happened in the run
- Job 1 (PM6): about 55 minutes, finished 14:26 on 27 Oct.
- Job 2 optimisation: about 8-9 minutes per step, converged at **step 109** (all four convergence criteria met, "Stationary point found").
- Job 2 frequencies: 4 h 42 min. **Normal termination 08:57 on 28 Oct.**
- Frequencies: 597 modes (3N-6 = 597). **No imaginary frequencies**, so the structure is a true minimum. Lowest mode 11 cm-1, highest 3495 cm-1.

## 6. How the spectrum was made (`make_spectrum.py`)
- Input: harmonic frequencies and Raman activities S from the Gaussian log (`lipidA_raman_act.csv`).
- Frequencies multiplied by a scale factor of **0.965**. This is a typical value for B3LYP, **not fitted or benchmarked for 3-21G** here.
- Intensity at 785 nm and 298.15 K: I = S (v0 - v)^4 / ( v (1 - exp(-hcv/kT)) ), with v0 = 1e7/785 cm-1.
- Each peak broadened with a Lorentzian, FWHM 12 cm-1; plotted 200-3300 cm-1, normalised to the tallest peak.
- Outputs: `lipidA_spectrum_785nm.csv` and `.png`.

## 7. Results
Compared with the reference SERS bands:

| Reference (cm-1) | Computed (cm-1) | Comment |
|---|---|---|
| 850 glycosidic | 845, 856 | good |
| 989 Kdo / carbohydrate | 993 (strongest in 900-1000 region) | good |
| 1131 lipid chain | weak 1139 | weak, expected: chains cut to C4 |
| 1330 phosphate / amide | 1314, 1338 | within about 15 cm-1 |

## 8. Limitations - read before using the spectrum
- **Quick level**: gas phase, B3LYP/3-21G (no diffuse or polarisation functions). Peak positions are approximate and intensities are distorted, especially for charged groups.
- **Peaks at about 2420, 2590 and 2750 cm-1 are artefacts**: strongly hydrogen-bonded O-H stretches to the charged groups, which happen in gas phase with no water. Ignore that region.
- **The strong 1512 cm-1 band** is probably an amide N-H / C-N mode that the small basis overstates. This assignment was not verified; do not trust the relative height.
- **Cut chains**: CH2/CH3 bands (about 1440 and 2850-3000 cm-1) are under-represented. Do not compare those regions with experiment.
- **Missing parts of the real sample**: core oligosaccharide beyond Kdo, and the O111 O-antigen are not in the model.
- **Comparison with experiment**: Gaussian activities are already orientation-averaged, so they correspond to powder or solution. Use peak positions to assign bands; do not compare absolute intensities. Powder and aggregate effects, counter-ions (Na+, Ca2+, Mg2+) and water bands in solution all shift or hide bands. SERS spectra change relative intensities and should only be compared for positions.

## 9. Planned next step
Rerun at a higher level: B3LYP/6-31G(d) or the NAM level (B3LYP/6-31+G(d,p)) with water (PCM), starting from this optimised geometry. Expect days of run time. A model of LTA (3 glycerol-phosphate units, 2 D-Ala esters, alpha-GlcNAc, 93 atoms, same quick level) is in `../new lta/`.

## 10. Files in this folder
- `lipidA_short.gjf`: Gaussian input (both jobs)
- `lipidA_short.sdf`: starting 3D structure of the model (before optimisation)
- `lipidA_short.out`: full Gaussian log (34 MB)
- `lipidA_raman_act.csv`: frequencies and Raman activities (unscaled)
- `lipidA_spectrum_785nm.csv` / `.png`: scaled, broadened 785 nm spectrum
- `make_spectrum.py`: script that produces the spectrum (`python make_spectrum.py lipidA`)
- `Lipid_A_Raman_Methods.md`: this document
- Build script, one level up: `../build_model.py`
