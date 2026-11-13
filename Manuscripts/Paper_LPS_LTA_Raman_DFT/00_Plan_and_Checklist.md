# Paper: Raman reference spectra and DFT-assisted band assignment of LPS and LTA at 785 nm

Scope decision: this paper covers **LPS (E. coli O111:B4) and LTA (S. aureus)**. NAM is used only as a comparison and is cited from the separate NAM Raman/DFT manuscript (mtp `05_Experimental_Data/NAM/NAM_Raman_Archive/05_Manuscript/v2_final`). Submit the NAM paper first, or at the same time, so that it can be cited.

Target journals: Spectrochimica Acta Part A, Journal of Raman Spectroscopy or Vibrational Spectroscopy.

## What is in this folder

| Item | File |
|---|---|
| Manuscript draft (abstract to references) | `Manuscript_Draft_LPS_LTA_Raman_DFT.docx` |
| Supplementary draft | `Supplementary_Draft_LPS_LTA.docx` |
| Figures (PNG 300 dpi and PDF) | `figures/` |
| Band-assignment tables, calculated mode lists, reference spectra, QC logs | `tables/` |
| Key numbers used in the text | `tables/key_numbers.json` |
| Build script (rerun after any data change) | `SERS_Sepsis_Spectral_Library/08_Methodology/code/final_reports/paper_lps_lta.py` |

## Main results in the draft

- LPS reference: n = 10 spots, 60 % / 40 s / 5 acc, mean pairwise r = 0.92. Primary bands 425 and 1080 cm-1; supporting bands 766, 861 and 996 cm-1.
- LTA reference: n = 17 spots (80 % / 45 s / 2 and 80 % / 30 s / 3), mean pairwise r = 0.93. Primary bands 1092, 539 and 862 cm-1; supporting bands 418, 723, 799, 1011, 1460 and 1751 cm-1.
- The spectra are distinct: LPS vs LTA r = 0.50; vs NAM r = 0.15 and 0.18.
- DFT: a mode of the expected type lies within 10 cm-1 of 5 of 5 LPS bands and 8 of 9 LTA bands.

## Critical issue found while preparing the paper

**The DFT agreement is not clearly better than chance.** The large models have many modes between 400 and 1800 cm-1 (lipid A 354, LTA 165). When the calculated frequencies are shifted at random by 15-70 cm-1, they still match:
- LPS: 4.6 of 5 bands on average (p = 0.56).
- LTA: 6.1 of 9 bands (p = 0.06).

Using only the visible peaks of the broadened calculated spectrum:
- LPS: 3 of 5 bands agree, against 1.9 by chance (p = 0.33).
- LTA: 3 of 9 bands agree, against 2.4 by chance (p = 0.44).

The calculated intensities do not resemble the experimental spectra (whole-spectrum r is about 0).

The draft states this openly. Reviewers at these journals will still question the assignments unless the calculation is improved. **This is the main work before submission.**

## Open items before submission

### Must do

1. **Better calculations** (the most important item):
   - Re-optimise and recompute frequencies at a larger basis set, at least 6-31G(d), ideally 6-31+G(d,p), or on smaller fragments of each model at B3LYP-D3/6-311++G(d,p).
   - Add an implicit solvent (or solid-state) model and check two or three conformers.
   - Fit or justify the scale factor for the chosen level.
   - Rerun the chance test. The aim is p < 0.05.
   - The higher-level LTA run started earlier was not finished.
2. **Literature check** to confirm novelty:
   - Search Scopus or Web of Science for normal Raman spectra of purified LPS and LTA.
   - Check the reference database of De Gelder et al. 2007 (J. Raman Spectrosc. 38, 1133) for LPS and LTA entries.
   - Check Ma et al. 2024 (Vibrational Spectroscopy; DFT of NAM) and any FT-Raman work on lipid A or Re-LPS.
3. **Measure the laser power at the sample** in mW, with a power meter at 60 % and 80 %.
4. **Wavenumber calibration check**: record a standard (silicon wafer, polystyrene or cyclohexane) and report the offset. Silicon gave 517-518 cm-1 in the SERS sessions.
5. **LTA purity**: obtain the certificate of analysis for lot 0000419622.
6. **Verify references [9]-[12]** and add the Gaussian 16 citation. Their DOIs are marked unverified in the draft.
7. **Authorship and permission**: agree the author list with the supervisor, and confirm that the funder agreement allows publication.

### Recommended

8. **More LPS spots with a fresh shutter-closed dark.** The current LPS darks contained some sample light, so absolute intensities may be 3-34 % low. Band positions are not affected.
9. **More LTA spots at 80 % / 30 s / 3 acc.** This repeat is still listed as pending in the library.
10. Add a figure of the calculated spectra alone (sticks plus envelope) to the supplementary information, with a table of mode composition for the matched modes.
11. Deposit the data (Zenodo or figshare) and add the DOI to the data availability statement.

### Notes for writing

- The glass band region (1308-1455 cm-1) is excluded throughout. Do not report bands there as markers.
- Laser power stays as % of maximum until it has been measured.
- Keep the wording tentative ("consistent with", "suggests").
