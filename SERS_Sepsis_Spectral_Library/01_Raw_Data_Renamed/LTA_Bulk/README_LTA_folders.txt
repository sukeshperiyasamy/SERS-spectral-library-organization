LTA bulk, session of 28 Oct 2026 (raw folder: bulk-lta)

One subfolder per setting: 2026-10-28_80pct_45s_2acc, _80pct_30s_3acc, _70pct_30s_3acc, _70pct_60s_2acc, _power_series_45s_2acc (30-70 % at 45 s x 2). 2026-04-03_April_preliminary holds the April files.
File names: LTA_Bulk_20261028_P<power>pct_T<s>s_A<acc>_S<nn>.csv; repeat scans on one spot end in _samespot (not independent, never used in a reference). Blanks: ../Glass_Blank/20261028_LTA_session.
LTA_20261028_File_Index.csv lists every original file, its library name and MD5 (all copies verified). Processed spectra: 02_Processed_Spectra/LTA (same folders), each with QC in its header.
Dark-frame warning: 55 of 99 LTA spectra have a dark that contains sample light (flagged FLAG-DARK); keep them as a record, do not use them in references. Best setting: 80 %, 30 s, 3 acc.

NOTE 28 Oct 2026: blanks S01-S08 (80 %/45 s/2 acc) were removed from this folder (moved to _to_delete/); they were polystyrene-like, not glass. S09-S13 remain.
