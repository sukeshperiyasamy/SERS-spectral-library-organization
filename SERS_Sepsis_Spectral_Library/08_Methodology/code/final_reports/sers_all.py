"""All SERS sessions (Jun-Oct 2026): copy and rename the raw files, process them with pipeline v3,
test R6G and biomarker bands, and write the workbook, figures and results used by sers_all_doc.py.
Raw files (E:\\sukesh) are only read; renamed copies are MD5-checked."""
import os, re, sys, json, hashlib, shutil, pickle, warnings, collections
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..')))
import numpy as np, pandas as pd, lib2
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.stats import mannwhitneyu
import fr_data as D

RAW = os.environ.get('SERS_RAW', r"E:\sukesh")
FS = r"C:\Users\sukes\Downloads\sukesh\Final_Submission"
OUT = os.path.join(FS, '09_SERS_All_Sessions')
DR, DP, DF, DT = (os.path.join(OUT, d) for d in ('01_Raw_Spectra_Renamed', '02_Processed_Spectra', '03_Figures', '04_Tables'))
for d in (DR, DP, DF, DT): os.makedirs(d, exist_ok=True)
X = np.arange(400, 1801, 1.0)
plt.rcParams.update({'font.family': 'Arial', 'font.size': 9})
COL = {'R6G': '#7b3fa0', 'NAM': '#1f5fa8', 'LPS': '#b5421c', 'LTA': '#2a7d46', 'Blank': '#555555', 'BareSi': '#999999', 'Unlabelled': '#b08a00'}

# ------------------------------------------------------------------ catalogue of the raw folders
# session id, date, short description of the substrate and of the session
SESS = {
 'S1': ('20260606', 'Substrate check: AgNO3/HF-treated wafer and plain silicon'),
 'S2': ('20260610', 'NAM and R6G on substrates etched 3, 4, 5 and 6 min'),
 'S3': ('20260617', 'R6G on eight substrates: 3-6 min etch with 5 or 10 mL HF'),
 'S4': ('20260704', 'R6G concentration series, NAM 0.1 and 1 mg/mL, substrate blank'),
 'S5': ('20260812', '20 mM AgNO3 recipe, 2, 5 and 10 min etch: R6G, NAM and substrate blanks'),
 'S6': ('20260813', 'Plain silicon reference (settings series)'),
 'S7': ('20260814', '2 min etched substrates: R6G, NAM, LTA and substrate blanks'),
 'S8': ('20261007', 'Etched silicon (5 mL HF, 6 mg AgNO3): NAM, LPS, LTA and substrate blank'),
}
R1 = '6mgAg-5mlHF'   # 45 mL DI + 5 mL HF + 6 mg AgNO3 (handwritten recipe note)
R2 = '20mMAg-8p6mlHF'  # 0.170 g AgNO3 + 8.6 mL HF to 50 mL
A12 = '12-08-26-170g-agno3 and 8.6ml of hf total 50ml di-'
M12 = '12-08-26-multispot-5sec-5p-3ac-'
F14 = '14-08-2026-sers-r6g-nam-2m-1700g-8.6-etched-si'
# (folder relative to RAW, session, analyte, concentration, role, substrate code, substrate description)
CAT = [
 ('5-6-2026/agno3 empty wafer data multispot-10s-3ac-20p multispot', 'S1', 'Blank', '', 'blank', 'AgNO3-wafer', 'AgNO3/HF-treated wafer, recipe not recorded'),
 ('5-6-2026/pure silicone 10s-20p-3ac multispot', 'S1', 'BareSi', '', 'bare', 'PlainSi', 'Plain silicon wafer'),
 ('10-6-26/nam-3m', 'S2', 'NAM', '', 'sample', '3min', 'Etched substrate, label 3m (3 min etch)'),
 ('10-6-26/nam-3m final', 'S2', 'NAM', '', 'sample', '3min', 'Etched substrate, label 3m (3 min etch)'),
 ('10-6-26/nam-4m', 'S2', 'NAM', '', 'sample', '4min', 'Etched substrate, label 4m (4 min etch)'),
 ('10-6-26/nam-5m', 'S2', 'NAM', '', 'sample', '5min', 'Etched substrate, label 5m (5 min etch)'),
 ('10-6-26/nam 6m', 'S2', 'NAM', '', 'sample', '6min', 'Etched substrate, label 6m (6 min etch)'),
 ('10-6-26/Nam-diifrentspot', 'S2', 'NAM', '1mgmL', 'sample', 'AgNO3-sub', 'Etched substrate, etch time not recorded'),
 ('10-6-26/r6g-3mfinal', 'S2', 'R6G', '', 'sample', '3min', 'Etched substrate, label 3m (3 min etch)'),
 ('10-6-26/r6g-4m', 'S2', 'R6G', '', 'sample', '4min', 'Etched substrate, label 4m (4 min etch)'),
 ('10-6-26/r6g-5m', 'S2', 'R6G', '', 'sample', '5min', 'Etched substrate, label 5m (5 min etch)'),
 ('10-6-26/r6g 6m', 'S2', 'R6G', '', 'sample', '6min', 'Etched substrate, label 6m (6 min etch)'),
 ('10-6-26/r6g-1mgml-10sec-5p-3ac', 'S2', 'R6G', '1mgmL', 'sample', 'AgNO3-sub', 'Etched substrate, etch time not recorded'),
] + [(f'17-06-2026/{m}m-{v}ml-hf-5s-10p-5ac', 'S3', 'R6G', '', 'sample', f'{m}min-{v}mlHF', f'{m} min etch, {v} mL HF in the bath')
     for m in (3, 4, 5, 6) for v in (10, 5)] + [
 ('04-07-2026', 'S4', 'Unlabelled', '', 'unlabelled', R1, 'Folder root; sample not recorded'),
 ('04-07-2026/namon5hf6mgagno3', 'S4', 'NAM', 'file', 'sample', R1, '5 mL HF + 6 mg AgNO3 substrate'),
 ('04-07-2026/r6g', 'S4', 'R6G', '', 'sample', R1, '5 mL HF + 6 mg AgNO3 substrate'),
 ('04-07-2026/r6g-sensor', 'S4', 'R6G', 'file', 'sample', R1, '5 mL HF + 6 mg AgNO3 substrate (concentration series)'),
 ('04-07-2026/rawr6g', 'S4', 'R6G', '', 'reference', 'NoSub', 'R6G labelled raw; support not recorded'),
 ('04-07-2026/substarte', 'S4', 'Blank', '', 'blank', R1, '5 mL HF + 6 mg AgNO3 substrate, no analyte'),
 (A12 + '10min-dip-10m-etched/New folder', 'S5', 'Blank', '', 'blank', R2 + '-10min', '10 min etch, same spot, power series'),
 (A12 + '10min-dip-10m-etched/New folder/multispot-10-etch-10sec-5power-3acc', 'S5', 'Blank', '', 'blank', R2 + '-10min', '10 min etch, different spots'),
 (A12 + '5min-dip-5m-etched', 'S5', 'Blank', '', 'blank', R2 + '-5min', '5 min etch, power series'),
 (A12 + '5min-dip-5m-etched/5min-diffrent-spot-5sec-5power-3', 'S5', 'Blank', '', 'blank', R2 + '-5min', '5 min etch, different spots'),
 (M12 + '2m-etched-substate/nam', 'S5', 'NAM', '', 'sample', R2 + '-2min', '2 min etch'),
 (M12 + '2m-etched-substate/r6g', 'S5', 'R6G', '', 'sample', R2 + '-2min', '2 min etch'),
 (M12 + '5m-etched-substate/nam', 'S5', 'NAM', '', 'sample', R2 + '-5min', '5 min etch'),
 (M12 + '5m-etched-substate/r6g', 'S5', 'R6G', '', 'sample', R2 + '-5min', '5 min etch'),
 (M12 + '10m-etched-substate/nam', 'S5', 'NAM', '', 'sample', R2 + '-10min', '10 min etch'),
 (M12 + '10m-etched-substate/r6g', 'S5', 'R6G', '', 'sample', R2 + '-10min', '10 min etch'),
 ('13-08-2026-raw-si/substrate-1', 'S6', 'BareSi', '', 'bare', 'PlainSi', 'Plain silicon (raw Si), settings series'),
 (F14 + '/1m-etcheddata-', 'S7', 'Blank', '', 'blank', R2 + '-1min', 'Folder label 1m-etched; no analyte recorded'),
 (F14 + '/raw-si-2m-etched', 'S7', 'Blank', '', 'blank', R2 + '-2min', '2 min etch, substrate 1, no analyte'),
 (F14 + '/second-substratrate-2m-etched-rawsi-data-for-comparision', 'S7', 'Blank', '', 'blank', R2 + '-2min-sub2', '2 min etch, substrate 2, no analyte'),
 (F14 + '/r6g', 'S7', 'R6G', '', 'sample', R2 + '-2min', '2 min etch'),
 ('14-08-2026-NAM-2m-1700.g-8.6ml-', 'S7', 'NAM', '', 'sample', R2 + '-2min', '2 min etch'),
 ('14-08-26-lta-2m-etched', 'S7', 'LTA', '', 'sample', R2 + '-2min', '2 min etch'),
 ('10-oct-2026/blank-5mlhf-45-di-6mgagno3/blank', 'S8', 'Blank', '', 'blank', R1, 'Etched silicon, no analyte'),
 ('10-oct-2026/blank-5mlhf-45-di-6mgagno3/nam-1', 'S8', 'NAM', '', 'sample', R1, 'Etched silicon, set nam-1'),
 ('10-oct-2026/blank-5mlhf-45-di-6mgagno3/nam-2', 'S8', 'NAM', '', 'sample', R1, 'Etched silicon, set nam-2'),
 ('10-oct-2026/lps/lps2', 'S8', 'LPS', '', 'sample', R1, 'Etched silicon, set lps2'),
 ('10-oct-2026/lps/lps1', 'S8', 'LPS', '', 'sample', R1, 'Etched silicon, set lps1'),
 ('10-oct-2026/lta/lta2', 'S8', 'LTA', '', 'sample', R1, 'Etched silicon, set lta2'),
]
TARGET = {
 'R6G': [612, 774, 1183, 1310, 1362, 1509, 1575, 1650],
 'NAM': [541, 829, 870.5, 929, 955, 1022.7, 1127],
 'LTA': [802.2, 861.5, 1091.8, 1131, 1237.5, 1450, 1458.8],
 'LPS': [424.8, 765.5, 861.1, 989, 995.8, 1080.5, 1330],
}
# bands a detection requires (project rule)
REQ = {'NAM': ('at least two of the bulk NAM marker bands', [[541, 829, 870.5, 929, 955, 1022.7, 1127]], 2),
       'LPS': ('989 and 1330 cm-1', [[989], [1330]], None),
       'LTA': ('a phosphate band (1092 or 1225-1250) and a lipid band (1131 or 1450)', [[1091.8, 1237.5], [1131, 1450]], None)}

def natkey(s): return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]
def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()
def conc_from(fname):
    m = re.search(r'(\d+(?:\.\d+)?)\s*(nM|microM|mM|mgml)', fname, re.I)
    if not m: return ''
    u = {'nm': 'nM', 'microm': 'uM', 'mm': 'mM', 'mgml': 'mgmL'}[m.group(2).lower()]
    return m.group(1).replace('.', 'p') + u
def tcode(t): return (f'{t:g}').replace('.', 'p')

# ------------------------------------------------------------------ read, copy, rename, process
spec = []; seen = {}; counter = collections.Counter()
for rel, ses, an, conc, role, sub, subdesc in CAT:
    folder = os.path.join(RAW, *rel.split('/'))
    date = SESS[ses][0]
    for f in sorted((f for f in os.listdir(folder) if f.lower().endswith('.csv') and os.path.isfile(os.path.join(folder, f))), key=natkey):
        p = os.path.join(folder, f)
        meta, rs, dk, raw, ds = lib2.read_any(p)
        if len(rs) == 0: continue
        it = float(meta['integration times(sec)']) if 'integration times(sec)' in meta else float(meta.get('integration times(ms)', 'nan')) / 1000
        pw = int(float(meta['laser_powerlevel'])); acc = int(float(meta['average number']))
        c = conc_from(f) if conc == 'file' else conc
        a2 = an + (('-' + c) if c else '')
        counter[(ses, a2, sub)] += 1; n = counter[(ses, a2, sub)]
        new = f'SERS_{a2}_{date}_{sub}_P{pw:03d}pct_T{tcode(it)}s_A{acc:02d}_S{n:02d}.csv'
        sdir = os.path.join(DR, f'{ses}_{date}'); os.makedirs(sdir, exist_ok=True)
        dst = os.path.join(sdir, new); h = md5(p)
        if not os.path.exists(dst) or md5(dst) != h: shutil.copy2(p, dst)
        assert md5(dst) == h, dst
        dup = seen.get(h, ''); seen.setdefault(h, new)
        pr = lib2.process_v3h(rs, ds, raw)
        corr = np.interp(X, pr['x'], pr['corr']); w = (X >= 505) & (X <= 535); i = int(np.argmax(corr[w]))
        rmax = float(raw[(rs >= 400) & (rs <= 1800)].max())
        spec.append(dict(session=ses, date=date, folder=rel, file=f, new=new, analyte=an, conc=c, role=role, sub=sub, subdesc=subdesc,
                         power=pw, it=it, acc=acc, time=meta.get('Date', ''), md5=h, dup=dup, corr=corr, noise=float(pr['noise']),
                         si=float(corr[w][i]), sipos=float(X[w][i]), rawmax=rmax, sat=rmax >= 65000))
print(len(spec), 'spectra')
for s in spec:
    pk, pp = find_peaks(s['corr'], prominence=3 * s['noise'], width=3)
    s['pk'] = X[pk]; s['snr'] = pp['prominences'] / s['noise']; s['prom'] = pp['prominences']
# processed copies (one file per spectrum)
for s in spec:
    d = os.path.join(DP, f"{s['session']}_{s['date']}"); os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, s['new']), 'w', newline='') as fh:
        fh.write(f"# Original raw file (unchanged): {os.path.join(RAW, *s['folder'].split('/'), s['file'])}\n")
        fh.write('# Pipeline v3 (lib2.process_v3h): dark-subtracted, hot pixels 640/700 fixed, crop 400-1800, despike, SG 11/3, ALS baseline; values in counts\n')
        fh.write(f"# noise (counts) {s['noise']:.2f}; silicon peak {s['sipos']:.0f} cm-1, height {s['si']:.1f} counts\nraman_shift_cm-1,corrected_counts\n")
        for x, y in zip(X, s['corr']): fh.write(f'{x:.0f},{y:.3f}\n')
uniq = [s for s in spec if not s['dup']]

def det(s, pos, tol=5.0):
    ok = [(q, a, h) for q, a, h in zip(s['pk'], s['snr'], s['prom']) if abs(q - pos) <= tol]
    return (True, max(a for _, a, _ in ok), max(h for _, _, h in ok)) if ok else (False, 0.0, 0.0)
def height(s, pos, tol=5.0):
    w = (X >= pos - tol) & (X <= pos + tol); return float(s['corr'][w].max())

# ------------------------------------------------------------------ R6G: substrate activity
r6 = []
for s in uniq:
    if s['analyte'] != 'R6G': continue
    d = {b: det(s, b) for b in TARGET['R6G']}
    r6.append(dict(session=s['session'], new=s['new'], sub=s['sub'], conc=s['conc'], role=s['role'], power=s['power'], it=s['it'], acc=s['acc'],
                   n_bands=sum(v[0] for v in d.values()), snr1509=d[1509][1], h1509=d[1509][2], sat=s['sat'],
                   bands=' '.join(str(b) for b in TARGET['R6G'] if d[b][0]), gate=d[1509][1] >= 10))
R6 = pd.DataFrame(r6)
R6S = (R6.groupby(['session', 'sub', 'conc', 'role', 'power', 'it', 'acc'])
       .agg(n=('new', 'size'), median_bands=('n_bands', 'median'), median_snr1509=('snr1509', 'median'),
            q25_snr1509=('snr1509', lambda v: v.quantile(.25)), q75_snr1509=('snr1509', lambda v: v.quantile(.75)),
            median_height1509=('h1509', 'median'), gate_pass=('gate', 'sum'), saturated=('sat', 'sum')).reset_index())

# ------------------------------------------------------------------ biomarkers against the same-session blank
BLANKS = {'S4': ['Blank'], 'S5': ['Blank'], 'S7': ['Blank'], 'S8': ['Blank']}
BLANK_NOTE = {'S2': 'No blank was measured in this session.',
              'S5': 'Blanks are from the 5 and 10 min substrates; the 2 min substrate had no blank.',
              'S7': 'Blanks: two 2 min substrates and the 1 min substrate, all without analyte.',
              'S4': 'Blank: the same substrate type without analyte.', 'S8': 'Blank: the same etched silicon without analyte.'}
rows = []; verd = []
for mol in ('NAM', 'LTA', 'LPS'):
    for ses in sorted({s['session'] for s in uniq if s['analyte'] == mol}):
        S = [s for s in uniq if s['session'] == ses and s['analyte'] == mol]
        B = [s for s in uniq if s['session'] == ses and s['role'] == 'blank']
        res = {}
        for b in TARGET[mol]:
            hs = [height(s, b) / max(s['si'], 1e-9) for s in S]; dd = [det(s, b) for s in S]
            hb = [height(s, b) / max(s['si'], 1e-9) for s in B]; db = [det(s, b) for s in B]
            nd = sum(x[0] for x in dd); nb = sum(x[0] for x in db)
            p = float(mannwhitneyu(hs, hb, alternative='greater').pvalue) if B else float('nan')
            rep = bool(B) and nd / len(S) >= 0.5 and nb == 0 and p < 0.05
            res[b] = rep
            rows.append(dict(session=ses, molecule=mol, band=b, n_detected=nd, n=len(S), frac=nd / len(S),
                             blank_detected=nb if B else None, n_blank=len(B), median_snr=float(np.median([x[1] for x in dd if x[0]])) if nd else 0.0,
                             h_sample=float(np.median(hs)), h_blank=float(np.median(hb)) if B else float('nan'), p=p, reproducible=rep))
        label, groups, k = REQ[mol]
        if not B: v = 'INCONCLUSIVE'
        else:
            if k: ok = sum(res[b] for b in groups[0]); v = 'DETECTED' if ok >= k else ('POSSIBLY DETECTED' if ok == 1 else 'NOT DETECTED')
            else:
                g = [any(res[b] for b in grp) for grp in groups]; v = 'DETECTED' if all(g) else ('POSSIBLY DETECTED' if any(g) else 'NOT DETECTED')
        best = max(TARGET[mol], key=lambda b: sum(det(s, b)[0] for s in S))
        verd.append(dict(session=ses, molecule=mol, n=len(S), n_blank=len(B), rule=label, verdict=v,
                         most_frequent_band=best, most_frequent_frac=sum(det(s, best)[0] for s in S) / len(S), blank_note=BLANK_NOTE.get(ses, '')))
BD = pd.DataFrame(rows); VD = pd.DataFrame(verd)

# ------------------------------------------------------------------ silicon reference and substrate background
SI = (pd.DataFrame([dict(session=s['session'], analyte=s['analyte'], role=s['role'], sipos=s['sipos'], si=s['si']) for s in uniq])
      .groupby(['session', 'role']).agg(n=('sipos', 'size'), si_pos_median=('sipos', 'median'), si_pos_sd=('sipos', 'std'), si_height_median=('si', 'median')).reset_index())
bgrows = []
for s in uniq:
    if s['role'] not in ('blank', 'bare'): continue
    for q, a in zip(s['pk'], s['snr']):
        if not 505 <= q <= 535: bgrows.append(dict(session=s['session'], role=s['role'], sub=s['sub'], pos=float(q), snr=float(a)))
BG = pd.DataFrame(bgrows)
def recurring(df, n_tot, tol=6):
    out = []
    for c in np.arange(560, 1800, 2.0):
        k = df[(df.pos - c).abs() <= tol]
        if len(k): out.append((c, k.pos.median(), len(set(zip(k.session, k.index))) / n_tot))
    return out
bg_list = []
for role in ('blank', 'bare'):
    nn = sum(1 for s in uniq if s['role'] == role)
    sub = BG[BG.role == role]
    if len(sub) == 0: continue
    hist, edges = np.histogram(sub.pos, bins=np.arange(560, 1810, 10))
    for h, e in zip(hist, edges):
        if h / nn >= 0.25:
            k = sub[(sub.pos >= e) & (sub.pos < e + 10)]
            bg_list.append(dict(role=role, window=f'{e:.0f}-{e+10:.0f}', median_pos=round(float(k.pos.median()), 1), spectra_with_peak=int(h), n_spectra=nn, frac=h / nn))
BGL = pd.DataFrame(bg_list)

# ------------------------------------------------------------------ group means (for the workbook and figures)
def gmean(ss, norm='si'):
    if not ss: return None
    a = np.array([s['corr'] / (max(s['si'], 1e-9) if norm == 'si' else 1) for s in ss]); return a.mean(0), a.std(0)
means = {}
for s in uniq: means.setdefault((s['session'], s['analyte'], s['conc'], s['sub']), []).append(s)
MS = pd.DataFrame({'raman_shift_cm-1': X})
for k, ss in sorted(means.items()):
    MS['_'.join(x for x in k if x) + f' (n={len(ss)})'] = gmean(ss)[0]

# ------------------------------------------------------------------ figures
def save(fig, name): fig.savefig(os.path.join(DF, name), dpi=200, bbox_inches='tight'); plt.close(fig); return os.path.join(DF, name)
FIGS = {}
# overview
cnt = collections.Counter((s['session'], s['analyte']) for s in uniq)
fig, ax = plt.subplots(figsize=(9, 3.6)); order = list(SESS); left = np.zeros(len(order))
for an in ('R6G', 'NAM', 'LTA', 'LPS', 'Blank', 'BareSi', 'Unlabelled'):
    v = np.array([cnt[(o, an)] for o in order])
    if v.sum() == 0: continue
    ax.barh(range(len(order)), v, left=left, color=COL[an], label={'BareSi': 'plain silicon', 'Blank': 'substrate blank'}.get(an, an)); left += v
for i, o in enumerate(order): ax.text(left[i] + 3, i, f'{int(left[i])}', va='center', fontsize=8)
ax.set_yticks(range(len(order))); ax.set_yticklabels([f"{o}  {SESS[o][0][6:]}.{SESS[o][0][4:6]}.{SESS[o][0][:4]}" for o in order]); ax.invert_yaxis()
ax.set_xlabel('Number of spectra (duplicates removed)'); ax.legend(frameon=False, fontsize=8, ncol=4, loc='lower right'); ax.spines[['top', 'right']].set_visible(False)
ax.set_title('SERS spectra collected in each session', loc='left', fontweight='bold', fontsize=10); FIGS['overview'] = save(fig, 'F01_sessions_overview.png')
# silicon reference
fig, (a0, a1) = plt.subplots(1, 2, figsize=(10, 3.6), gridspec_kw=dict(width_ratios=[1, 1.4]))
ss = [s for s in uniq]; ses_l = list(SESS)
for i, o in enumerate(ses_l):
    v = [s['sipos'] for s in ss if s['session'] == o and s['si'] > 5 * s['noise']]
    if v: a0.scatter(np.full(len(v), i) + np.random.default_rng(i).uniform(-.18, .18, len(v)), v, s=8, color='#1f5fa8', alpha=.5); a0.plot([i - .3, i + .3], [np.median(v)] * 2, color='k', lw=1.5)
a0.axhline(520.7, color='#b5421c', ls='--', lw=1); a0.text(len(ses_l) - .5, 520.9, 'textbook 520.7', ha='right', fontsize=7.5, color='#b5421c')
a0.set_xticks(range(len(ses_l))); a0.set_xticklabels(ses_l); a0.set_ylabel('Silicon peak position (cm$^{-1}$)'); a0.set_ylim(512, 524)
a0.set_title('Silicon peak in every spectrum', loc='left', fontweight='bold', fontsize=9.5)
bare = [s for s in uniq if s['role'] == 'bare']; blk = [s for s in uniq if s['role'] == 'blank']
for lab, grp, c in (('plain silicon', bare, '#999999'), ('etched substrates, no analyte', blk, '#555555')):
    m = gmean(grp)[0]; a1.plot(X, m, color=c, lw=1.3, label=f'{lab} (n={len(grp)})')
a1.set_ylim(-0.05, 0.25); a1.set_xlim(400, 1800); a1.axvspan(480, 560, color='#ddd', lw=0); a1.text(520, 0.235, 'Si peak\n(off scale)', ha='center', va='top', fontsize=7)
a1.set_xlabel('Raman shift (cm$^{-1}$)'); a1.set_ylabel('Signal / silicon peak'); a1.legend(frameon=False, fontsize=8)
a1.set_title('Mean background of plain and etched silicon', loc='left', fontweight='bold', fontsize=9.5)
FIGS['silicon'] = save(fig, 'F02_silicon_reference_and_background.png')
# R6G mean spectra by session (normalised to the 1509 band)
def r6mean(sel):
    a = np.array([s['corr'] / max(height(s, 1509), 1e-9) for s in sel]); return a.mean(0)
grp = [('S2', None, 'S2: 3-6 min etch'), ('S3', None, 'S3: eight substrates'), ('S4', 'R6G-sub', 'S4: 5 mL HF + 6 mg AgNO3'),
       ('S5', R2 + '-2min', 'S5: 20 mM, 2 min'), ('S5', R2 + '-5min', 'S5: 20 mM, 5 min'), ('S5', R2 + '-10min', 'S5: 20 mM, 10 min'), ('S7', R2 + '-2min', 'S7: 20 mM, 2 min')]
fig, ax = plt.subplots(figsize=(9.2, 6.4)); off = 0
for ses, sub, lab in grp:
    sel = [s for s in uniq if s['analyte'] == 'R6G' and s['session'] == ses and s['role'] == 'sample' and not s['sat']]
    if sub == 'R6G-sub': sel = [s for s in sel if s['sub'] == R1 and not s['conc']]
    elif sub: sel = [s for s in sel if s['sub'] == sub]
    if not sel: continue
    m = r6mean(sel); k = X >= 560; m = m / m[k].max()
    ax.plot(X[k], m[k] + off, color=COL['R6G'], lw=1.1); ax.text(1795, off + 0.55, f'{lab} (n={len(sel)})', ha='right', fontsize=8, bbox=dict(fc='white', ec='none', pad=1))
    off += 1.15
for b in TARGET['R6G']: ax.axvline(b, color='#7b3fa0', ls=':', lw=.7, alpha=.6); ax.text(b, off + 0.02, f'{b}', ha='center', fontsize=7.5, color='#7b3fa0', rotation=90, va='bottom')
ax.set_xlim(560, 1800); ax.set_yticks([]); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('Normalised signal (offset)')
ax.set_title('R6G SERS spectra: mean of each substrate group, scaled to its tallest band', loc='left', fontweight='bold', fontsize=10)
FIGS['r6g_spectra'] = save(fig, 'F03_R6G_mean_spectra.png')
# R6G 1509 SNR by substrate
fig, axs = plt.subplots(1, 3, figsize=(11, 3.8), gridspec_kw=dict(width_ratios=[2.2, 1, 1.2]))
def box(ax, data, labels, title):
    data = [np.clip(v, 0.8, None) for v in data]
    ax.boxplot(data, widths=.55, showfliers=False, medianprops=dict(color='k'))
    for i, v in enumerate(data): ax.scatter(np.full(len(v), i + 1) + np.random.default_rng(i).uniform(-.15, .15, len(v)), v, s=9, color=COL['R6G'], alpha=.6, zorder=3)
    ax.set_xticks(range(1, len(labels) + 1)); ax.set_xticklabels(labels, fontsize=7.5, rotation=30, ha='right'); ax.axhline(10, color='#b5421c', ls='--', lw=.9)
    ax.set_title(title, loc='left', fontweight='bold', fontsize=9); ax.spines[['top', 'right']].set_visible(False)
s3 = [f'{m}min-{v}mlHF' for m in (3, 4, 5, 6) for v in (5, 10)]
box(axs[0], [R6[(R6.session == 'S3') & (R6['sub'] == c)].snr1509.values for c in s3], [c.replace('min-', ' min, ').replace('mlHF', ' mL HF') for c in s3], 'S3: power 10, 5 s, 5 acc')
s2 = ['3min', '4min', '5min', '6min']
box(axs[1], [R6[(R6.session == 'S2') & (R6['sub'] == c) & (R6.power == 10) & (R6.it == 10)].snr1509.values for c in s2], [c.replace('min', ' min') for c in s2], 'S2: power 10, 10 s')
s5 = [R2 + '-2min', R2 + '-5min', R2 + '-10min']
box(axs[2], [R6[(R6.session == 'S5') & (R6['sub'] == c) & (R6.power == 5) & (R6.it == 5)].snr1509.values for c in s5], ['2 min', '5 min', '10 min'], 'S5: power 5, 5 s, 3 acc')
axs[0].set_ylabel('SNR of the 1509 cm$^{-1}$ band')
for a in axs: a.set_yscale('log'); a.set_ylim(0.6, 1500); a.axhline(0.8, color='#bbb', lw=.6)
axs[0].text(0.6, 0.85, 'band not found (plotted at 0.8)', fontsize=7, color='#777')
FIGS['r6g_snr'] = save(fig, 'F04_R6G_1509_SNR_by_substrate.png')
# R6G concentration series
cs = R6[(R6.session == 'S4') & R6.conc.str.contains('M')].copy()
if len(cs):
    def molar(c): n = float(c[:-2].replace('p', '.')); return n * {'nM': 1e-9, 'uM': 1e-6, 'mM': 1e-3}[c[-2:]]
    cs['M'] = cs.conc.map(molar)
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.scatter(cs.M, cs.snr1509, color=COL['R6G'], s=20, zorder=3)
    g = cs.groupby('M').snr1509.median(); ax.plot(g.index, g.values, color='k', lw=1)
    ax.set_xscale('log'); ax.axhline(10, color='#b5421c', ls='--', lw=.9); ax.set_xlabel('R6G concentration (mol/L, from the file names)'); ax.set_ylabel('SNR of the 1509 cm$^{-1}$ band')
    ax.set_title('S4: R6G concentration series (power 10, 10 s, 4 acc)', loc='left', fontweight='bold', fontsize=9.5); ax.spines[['top', 'right']].set_visible(False)
    FIGS['r6g_conc'] = save(fig, 'F05_R6G_concentration_series.png')
# biomarkers: one panel per session, bulk on top, SERS mean, blank below
bulk = {m: D.exp_ref(m)[0] for m in ('NAM', 'LTA', 'LPS')}
def bio_fig(mol, name):
    sess = sorted({s['session'] for s in uniq if s['analyte'] == mol})
    fig, axs = plt.subplots(len(sess), 1, figsize=(9.2, 2.35 * len(sess) + 0.4), sharex=True, squeeze=False); axs = axs[:, 0]
    for ax, ses in zip(axs, sess):
        S = [s for s in uniq if s['session'] == ses and s['analyte'] == mol]; B = [s for s in uniq if s['session'] == ses and s['role'] == 'blank']
        mS = gmean(S)[0]; k = X >= 560; sc = max(mS[k].max(), 1e-6)
        ax.plot(X, bulk[mol] * 0.9 + 1.25, color='#7a7a7a', lw=1.1); ax.plot(X, mS / sc, color=COL[mol], lw=1.3)
        if B: mB = gmean(B)[0]; ax.plot(X, mB / max(mB[k].max(), 1e-6) * 0.8 - 0.95, color='#555', lw=1.1)
        for j, b in enumerate(TARGET[mol]):
            r = BD[(BD.session == ses) & (BD.molecule == mol) & (BD.band == b)].iloc[0]
            col = '#2a7d46' if r.reproducible else ('#c07a00' if r.frac > 0 else '#bbbbbb')
            ax.plot([b, b], [-0.95, 2.25], color=col, ls=':', lw=.9)
            ax.text(b, 2.28 + 0.42 * (j % 2), f"{b:g}: {int(r.n_detected)}/{int(r.n)}", ha='center', va='bottom', fontsize=6.5, color=col)
        ax.axvspan(480, 560, color='#e6e6e6', lw=0, zorder=4); ax.set_ylim(-1.0, 3.2); ax.set_yticks([])
        ax.text(1795, 2.0, 'bulk reference', fontsize=7, color='#555', ha='right'); ax.text(1795, 0.9, f'SERS mean (n={len(S)})', fontsize=7, color=COL[mol], ha='right')
        ax.text(1795, -0.3, f'blank, scaled separately (n={len(B)})' if B else 'no blank in this session', fontsize=7, color='#555', ha='right')
        ax.set_title(f'{ses}: {SESS[ses][1]}', loc='left', fontsize=8.5, fontweight='bold')
    axs[-1].set_xlim(400, 1800); axs[-1].set_xlabel('Raman shift (cm$^{-1}$)')
    fig.suptitle(f'{mol}: target bands in each session (label: spots with the band / spots measured)', x=0.01, ha='left', fontweight='bold', fontsize=10, y=1.0)
    fig.tight_layout(); return save(fig, name)
FIGS['NAM'] = bio_fig('NAM', 'F06_NAM_SERS_by_session.png'); FIGS['LTA'] = bio_fig('LTA', 'F07_LTA_SERS_by_session.png'); FIGS['LPS'] = bio_fig('LPS', 'F08_LPS_SERS_by_session.png')
# detection heatmap
fig, axs = plt.subplots(1, 3, figsize=(11, 3.4), gridspec_kw=dict(width_ratios=[5, 2, 1]))
for ax, mol in zip(axs, ('NAM', 'LTA', 'LPS')):
    sub = BD[BD.molecule == mol]; ses = sorted(sub.session.unique())
    M = np.array([[sub[(sub.session == s) & (sub.band == b)].frac.iloc[0] for s in ses] for b in TARGET[mol]])
    im = ax.imshow(M, cmap='Blues', vmin=0, vmax=1, aspect='auto')
    for i in range(M.shape[0]):
        for j in range(M.shape[1]): ax.text(j, i, f'{M[i, j]*100:.0f}', ha='center', va='center', fontsize=7.5, color='white' if M[i, j] > .55 else 'black')
    ax.set_xticks(range(len(ses))); ax.set_xticklabels(ses); ax.set_yticks(range(len(TARGET[mol]))); ax.set_yticklabels([f'{b:g}' for b in TARGET[mol]])
    ax.set_title(mol, loc='left', fontweight='bold', fontsize=9.5)
fig.colorbar(im, ax=axs, shrink=.8, label='Spots with the band (%)')
FIGS['heat'] = save(fig, 'F09_biomarker_band_detection_heatmap.png')

# ------------------------------------------------------------------ workbook
IDX = pd.DataFrame([dict(session=s['session'], measured=s['time'], analyte=s['analyte'], concentration=s['conc'] or 'Not recorded', role=s['role'],
                         substrate_code=s['sub'], substrate=s['subdesc'], laser_power_level_pct=s['power'], integration_s=s['it'], accumulations=s['acc'],
                         new_file=s['new'], original_folder=s['folder'], original_file=s['file'], md5=s['md5'], duplicate_of=s['dup'] or '',
                         saturated=s['sat'], raw_max_counts=round(s['rawmax']), si_peak_cm=s['sipos'], si_height_counts=round(s['si'], 1),
                         noise_counts=round(s['noise'], 2), n_peaks=len(s['pk'])) for s in spec])
SES = pd.DataFrame([dict(session=k, date=f'{v[0][:4]}-{v[0][4:6]}-{v[0][6:]}', description=v[1], spectra=int((IDX.session == k).sum()),
                         unique_spectra=int(((IDX.session == k) & (IDX.duplicate_of == '')).sum()),
                         analytes=', '.join(sorted(IDX[IDX.session == k].analyte.unique())), blank_available='yes' if k in BLANKS else 'no',
                         folders='; '.join(sorted(IDX[IDX.session == k].original_folder.unique()))) for k, v in SESS.items()])
RD = pd.DataFrame([
    ('Purpose', 'All SERS spectra from June to October 2026, renamed, processed and tested in one place.'),
    ('Raw source', RAW + ' (originals are never changed; 01_Raw_Spectra_Renamed holds MD5-checked copies)'),
    ('File name', 'SERS_<analyte[-concentration]>_<YYYYMMDD>_<substrate code>_P<power level>pct_T<s>s_A<acc>_S<nn>.csv'),
    ('Substrate code 6mgAg-5mlHF', '45 mL DI water + 5 mL HF + 6 mg AgNO3 (handwritten recipe note in the image folder)'),
    ('Substrate code 20mMAg-8p6mlHF-<t>min', '0.170 g AgNO3 + 8.6 mL HF made up to 50 mL DI (20 mM AgNO3), etched <t> min'),
    ('Substrate code <t>min-<v>mlHF', 'S3 substrates: <t> min etch with <v> mL HF in the bath (labels 3m-6m on the substrates)'),
    ('Laser power', 'Software power level as recorded in the file header (% of maximum); not converted to mW'),
    ('Processing', 'Pipeline v3 (lib2.process_v3h): dark-subtracted, hot pixels 640/700 fixed, crop 400-1800, despike, SG 11/3, ALS baseline'),
    ('Peak rule', 'A band is present when a peak lies within 5 cm-1, is at least 3 pixels wide and has SNR >= 3'),
    ('Reproducible band', 'Present in at least half of the spots, absent from every same-session blank, and taller than the blank (Mann-Whitney p < 0.05, heights / silicon peak)'),
    ('Verdict rule', 'NAM: two marker bands reproducible; LPS: 989 and 1330; LTA: a phosphate and a lipid band. One of two = POSSIBLY DETECTED; no blank = INCONCLUSIVE'),
    ('R6G gate', 'SNR of the 1509 cm-1 band >= 10'),
    ('Duplicates', 'Files with identical bytes are listed in duplicate_of and left out of every statistic'),
], columns=['item', 'description'])
mtp_key = r"C:\Users\sukes\Downloads\mtp\05_Experimental_Data\SERS_and_R6G_sessions\r6g-from-my-pc\outputs\key_numbers.json"
KEY = pd.DataFrame(sorted((k, json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in json.load(open(mtp_key)).items()), columns=['key', 'value']) if os.path.exists(mtp_key) else pd.DataFrame()
XL = os.path.join(DT, 'SERS_All_Sessions_Workbook.xlsx')
sheets = [('README', RD), ('Sessions', SES), ('File_Index', IDX), ('R6G_Spectra', R6), ('R6G_Summary', R6S), ('Biomarker_Bands', BD),
          ('Biomarker_Verdicts', VD), ('Silicon_Reference', SI), ('Substrate_Background', BGL), ('Mean_Spectra', MS), ('Earlier_R6G_DFT', KEY)]
with pd.ExcelWriter(XL, engine='openpyxl') as xw:
    for n, df in sheets: df.to_excel(xw, sheet_name=n, index=False)
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
wb = load_workbook(XL)
for ws in wb.worksheets:
    for c in ws[1]: c.font = Font(bold=True, name='Arial'); c.fill = PatternFill('solid', fgColor='D9D9D9'); c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = 'A2'
    for col in ws.columns:
        L = max(len(str(c.value)) if c.value is not None else 0 for c in list(col)[:200]); ws.column_dimensions[col[0].column_letter].width = min(max(10, L + 2), 60)
wb.save(XL)
for n, df in sheets[1:9]: df.to_csv(os.path.join(DT, f'{n}.csv'), index=False)

# earlier analyses kept in the mtp repository (copied, not changed)
MTP = r"C:\Users\sukes\Downloads\mtp\05_Experimental_Data\SERS_and_R6G_sessions"
DE = os.path.join(OUT, '05_Earlier_Analyses_from_mtp')
for src, dst in ((r'r6g-from-my-pc\outputs', 'R6G_substrate_DFT_validation_S3'), (r'04-07-2026\_analysis_report', 'Session_S4_analysis')):
    if os.path.isdir(os.path.join(MTP, src)): shutil.copytree(os.path.join(MTP, src), os.path.join(DE, dst), dirs_exist_ok=True)
for f in ('Research_Paper.md', 'Supplementary_Information.md', 'Findings_Report.txt'):
    p = os.path.join(MTP, 'r6g-from-my-pc', f)
    if os.path.exists(p): shutil.copy2(p, os.path.join(DE, 'R6G_substrate_DFT_validation_S3', f))

pickle.dump(dict(SESS=SESS, IDX=IDX, SES=SES, R6=R6, R6S=R6S, BD=BD, VD=VD, SI=SI, BGL=BGL, FIGS=FIGS, TARGET=TARGET, n=len(spec), n_uniq=len(uniq),
                 RAW=RAW), open(os.path.join(DT, 'sers_all_results.pkl'), 'wb'))
print(VD.to_string()); print(R6S.to_string()); print(SI.to_string()); print(BGL.to_string())
print('duplicates', int((IDX.duplicate_of != '').sum()), 'saturated', int(IDX.saturated.sum()))
