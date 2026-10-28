Analysis code used to build the library (Python 3; numpy, scipy, pandas, matplotlib, openpyxl). Run order:
audit2.py -> qc2.py -> build_v2.py (initial copy/rename/QC) -> reaudit60.py -> update_v3.py (60 s re-audit) ->
reprocess_v3.py (pipeline v3: hot-pixel fix, spike width guard, robust noise; rewrites processed CSVs) ->
analysis_v2.py -> nam70.py -> an4.py -> crit.py -> sens.py -> final_v3.py -> figs4.py -> excel_v2.py -> excel5.py -> litx.py
Core functions: lib2.py (read_any, hotpix_fix, despike_v3, als, process_v3h). Paths in the scripts point to ~/work and ~/mnt/sukesh (the analysis VM); adjust ROOT/LIB in lib2.py to rerun elsewhere.
Original raw files are only read, never written.
