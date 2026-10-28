LTA bulk reference — PRELIMINARY (library v3, 23 Sep 2026)
Condition: 785 nm, 80-95 %, 45 s, 2 acc; bulk powder on glass slide; 3 Apr 2026. n = 4 (spot independence not recorded).
Primary markers: 802, 861.5, 1092 cm-1; supporting 1459; 1367 = glass-associated.
Decision: RE-ACQUIRE 10-15 independent spots at 80 %, 45 s, 2 acc (+ 3 matched glass blanks).
Absolute intensities depend on ALS baseline settings (strong fluorescence) - compare only within this pipeline.

UPDATE 28 Oct 2026 - re-acquisition on glass (folder bulk-lta), STATUS: ESTABLISHED (pending operator confirmation)
Condition: 785 nm, 80 % / 45 s / 2 acc, bulk powder on glass slide, shutter-closed dark (dark median 1504-1512 counts). 28 spots measured (SP_9-SP_36) plus 8 blanks.
QC: PASS 10 (S11, S21-S24, S26, S29, S30, S32, S34), REVIEW 8 (ripple 50-58, brightest spots), EXCLUDE 3 (atypical shape: S12, S13, S25), FAIL 7 (saturated: S17-S20, S27; SNR < 10: S09, S10).
Reference v2 = mean of the 10 PASS spots: LTA_Bulk_Reference_20261028_Mean_SD.csv, LTA_Reference_20261028_Members.csv, LTA_Reference_20261028_Marker_Peaks.csv. The April 2026 files (n = 4) are kept unchanged.
Agreement: mean vs median r 0.993; strict set vs extended set (18 spots) r 0.986; mean pairwise r 0.905; r to the April reference 0.947; to LPS 0.50; to NAM 0.17 (glass zone excluded).
Primary markers (C1): 1092 (SNR 29), 539 (SNR 16), 861 (SNR 16). Supporting (C2): 419, 629, 723, 798, 1459, 1583, 1751. 1246 (phosphate region) is seen in 7 of 10 spots (C4).
Notes: the 8 glass blanks of 28 Oct show polystyrene-like bands (1000, 1030, 619, 1602) and do not match the 28 Sep glass blanks (r = 0.07); they are flagged and were not used for the glass estimate. SP_1-SP_8 in the spot folder are identical copies of the blanks and were not copied as spectra.
Sample supplier, lot and purity of the LTA are Not recorded. Report: 09_Reports/LTA_Bulk_Reference_Report_20261028.docx.

UPDATE 28 Oct 2026 (sample record): Sigma-Aldrich L2515-10MG, lipoteichoic acid from Staphylococcus aureus, lot 0000419622, source number 0000404178 (as given by the operator). Purity: Not recorded. Whether the 3 Apr 2026 data came from the same vial is not known.

UPDATE 28 Oct 2026 (same vial, purity): the 3 Apr 2026 data came from the same vial (operator). The label reads "bacterial cell wall polymer". Supplier pages found by web search (the product page itself could not be opened): lyophilised powder, CAS 56411-57-5, storage 2-8 C, described as a glycerol-phosphate polymer tethered to a lipid; no purity figure for L2515 is given. A published isolation method cited on the page reports > 99 % pure S. aureus LTA, but that is not a specification for this product. Purity: Not recorded; obtain the certificate of analysis for lot 0000419622.

UPDATE 28 Oct 2026 (supplier product sheet): the L2515 product information sheet (text supplied by the operator) is summarised in LTA_Sample_Product_Information_L2515.txt. It describes LTA as a linear polymer of phosphodiester-linked glycerol phosphate bound to a lipid (C2 usually glycosylated and/or D-alanylated), soluble in water at 5 mg/ml. It gives no purity figure and does not state the physical form, so purity remains Not recorded (certificate of analysis for the lot not obtained). This supersedes the web-search summary above for form and purity.


UPDATE 28 Oct 2026 (full session, all conditions): 99 LTA spectra (118 unique files incl. 19 blanks) at nine settings processed and placed by setting (see 01_Raw_Data_Renamed/LTA_Bulk/README_LTA_folders.txt). 55 spectra have a leaked dark (dark median 2,500-11,500 vs clean 1,333-1,680) and are flagged FLAG-DARK. With a clean dark, 80 %/30 s/3 acc passes 7 of 7 spots (no saturation), 80 %/45 s/2 acc 10 of 28, 70 %/60 s/2 acc 2 of 8.
Reference v2 (n = 10) unchanged. Pooled reference v2.1 = 10 spots at 80/45/2 + 7 at 80/30/3 (n = 17): files *_Pooled_*; agrees with v2 at r = 0.996, 30 s vs 45 s sets r = 0.979, mean vs median r = 0.997, mean pairwise r 0.93; r to LPS 0.50, to NAM 0.18. Primary bands 1092, 539, 862; supporting 419, 723, 798, 1010, 1459, 1751; uncertain 1247, 629, 1583. Glass blanks: first 8 polystyrene-like; blanks at 80/30/3 are clean glass. Recommended setting for new spots: 80 %/30 s/3 acc with a fresh shutter-closed dark. Report v2.0: 09_Reports/LTA_Bulk_Reference_Report_20261028.docx.
