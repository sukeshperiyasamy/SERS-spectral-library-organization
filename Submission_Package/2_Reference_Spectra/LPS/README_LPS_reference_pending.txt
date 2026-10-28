LPS reference spectrum pending controlled glass-slide measurement.

Status: 23 Sep 2026 (v2.1). No LPS reference spectrum has been generated from the existing data.

Existing LPS bulk data (13 Apr 2026, 14 spectra, 10-20 % laser power) do not show a reproducible LPS band.
The dominant broad feature at ~1360-1370 cm-1 coincides with the empty glass-slide background and is NOT treated as an LPS peak.
All existing LPS spectra remain available in 01_Raw_Data_Renamed/LPS_Bulk and 02_Processed_Spectra/LPS.

A reference will be created here only after the planned glass-blank-controlled screening:
  LPS on glass slide at 70 %, 80 % and 90 % power, 785 nm, 30 s, 5 accumulations, >= 5 independent spots per power,
  plus an empty glass-slide blank at exactly the same wavelength / power / integration / accumulations / objective / glass-slide type.
No other substrate is used. The reference condition will be selected on SNR + reproducibility + intensity + absence of saturation + separation from the glass background (1308-1455 cm-1).
File names: LPS_Bulk_<YYYYMMDD>_P080pct_T30s_A05_S01.csv ; Glass_Blank_<YYYYMMDD>_P080pct_T30s_A05_S01.csv


UPDATE 28 Sep 2026 - LPS screening session (folder 28-9-26-lps-bulk; 60/70/80 % x 30 s x 5 acc; 19 LPS spectra + 10 blanks)
- QC: 60 %: 8 core + 1 glass-dominated; 70 %: 4 core + 1 glass-dominated; 80 %: 0/5 (fixed-pattern ripple). 90 % not measured.
- Identity: matches April 2026 LPS data (r 0.75-0.82), not NAM (r < 0.2). Candidate primary band 425 cm-1 (raw-data check confirms; not in blanks).
- Weak candidate bands 765, 997, 1081 (SNR 4-10); 1249 possibly glass; 1308-1455 glass-dominated.
- Best condition: 70 %. Reference still PENDING: collect 10-15 spots at 70 % / 30 s / 10 acc + matched blanks.
- Screening means saved here as *_NOT_REFERENCE.csv; bands in LPS_Screening_20260928_Candidate_Bands.csv; workbook sheets 33-36.

SAMPLE IDENTITY (from vial label photo, 28 Sep 2026; photo: LPS_vial_label_L2630_lot0000442391.jpg)
- Lipopolysaccharides from Escherichia coli O111:B4, Sigma-Aldrich L2630-10MG, Lot 0000442391 (source number partly legible on photo - confirm on CoA)
- Purified by phenol extraction; storage +2 to +8 C (label)
- Supplier specification (product page, checked 28 Sep 2026): lyophilized powder, off-white to faint yellow; <=3.00 % protein (Lowry-TCA);
  smooth (S-type) LPS containing lipid A, core oligosaccharide and O-antigen; lot-to-lot variability noted by supplier.
- Literature context: the only normal-Raman LPS powder spectrum found (Verde et al. 2021, doi:10.3389/fimmu.2021.758410) used a different
  serotype and purification (E. coli O55:B5, Sigma L6529, gel-filtration purified); SERS of O111:B4 LPS: Matar Abed et al. 2025 (ACS AMI).

SUPERSEDED 28 Sep 2026: LPS reference established - see README_LPS_reference_status.txt
