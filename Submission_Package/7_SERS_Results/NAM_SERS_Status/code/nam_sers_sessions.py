"""NAM and R6G detection across the SERS sessions of 10-11 Jun, 4 Jul and 7 Oct 2026.
Reads raw files only. Uses the library pipeline v3 and the same detection rule as SERS_Results_Oct2026."""
import os,re,sys,json,warnings,collections
warnings.filterwarnings('ignore')
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.abspath(os.path.join(HERE,'..')); REPO=os.path.abspath(os.path.join(OUT,'..'))
sys.path.insert(0,os.path.join(REPO,'SERS_Sepsis_Spectral_Library','08_Methodology','code'))
import numpy as np,pandas as pd,lib2
from scipy.signal import find_peaks
X=np.arange(400,1801,1.0); rng=np.random.default_rng(5)
NAM=[541.0,829.0,870.5,929.0,955.0,1022.7,1127.0]
R6G=[612,774,1183,1310,1362,1509,1575,1650]
def load(folder):
    out=[]
    for dp,dn,fn in os.walk(folder):
        for f in sorted(fn):
            if not f.lower().endswith('.csv'): continue
            try:
                meta,rs,dk,raw,ds=lib2.read_any(os.path.join(dp,f))
                if len(rs)==0: continue
                pr=lib2.process_v3h(rs,ds,raw); c=np.interp(X,pr['x'],pr['corr'])
                p,pp=find_peaks(c,prominence=3*pr['noise'],width=3)
                out.append(dict(file=f,sub=os.path.relpath(dp,folder),power=meta.get('laser_powerlevel'),it=meta.get('integration times(sec)'),acc=meta.get('average number'),pk=X[p],snr=pp['prominences']/pr['noise']))
            except Exception as e: pass
    return out
def det(s,pos,tol=5.0):
    ok=[a for q,a in zip(s['pk'],s['snr']) if abs(q-pos)<=tol]; return (True,max(ok)) if ok else (False,0.0)
S=[('10-11 Jun 2026','NAM on silver-etched silicon (3 to 6 etch-label folders)',[os.path.join(REPO,'10-6-26',d) for d in ('nam-3m','nam-3m final','nam-4m','nam-5m','nam 6m','Nam-diifrentspot')],[os.path.join(REPO,'10-6-26',d) for d in ('r6g-3mfinal','r6g-4m','r6g-5m','r6g 6m','r6g-1mgml-10sec-5p-3ac')]),
   ('4 Jul 2026','NAM on 5 ml HF / 6 mg AgNO3 substrate',[os.path.join(REPO,'04-07-2026','namon5hf6mgagno3')],[os.path.join(REPO,'04-07-2026','r6g'),os.path.join(REPO,'04-07-2026','r6g-sensor')]),
   ('7 Oct 2026','NAM on etched silicon (nam-1, nam-2)',[os.path.join(r"E:\sukesh\10-oct-2026\blank-5mlhf-45-di-6mgagno3",d) for d in ('nam-1','nam-2')],[])]
rows=[]
for name,desc,nf,rf in S:
    nam=[s for f in nf if os.path.isdir(f) for s in load(f)]; r6=[s for f in rf if os.path.isdir(f) for s in load(f)]
    real=float(np.mean([[det(s,p)[0] for s in nam] for p in NAM])) if nam else np.nan
    sims=[np.mean([[det(s,p+sh)[0] for s in nam] for p in NAM]) for sh in (rng.uniform(20,80,300)*rng.choice([-1,1],300))] if nam else []
    perband={str(int(round(p))):int(sum(det(s,p)[0] for s in nam)) for p in NAM}
    r1509=[det(s,1509.0) for s in r6]; nb=[sum(det(s,b)[0] for b in R6G) for s in r6]
    rows.append(dict(session=name,description=desc,n_nam=len(nam),n_r6g=len(r6),nam_detect_fraction=real,nam_chance_mean=float(np.mean(sims)) if sims else np.nan,nam_chance_p=float(np.mean(np.array(sims)>=real)) if sims else np.nan,
                     nam_max_snr=float(max([max([a for q,a in zip(s['pk'],s['snr']) if abs(q-p)<=5]+[0]) for s in nam for p in NAM] or [0])),per_band=json.dumps(perband),
                     r6g_1509_detected=int(sum(d[0] for d in r1509)),r6g_median_snr_1509=float(np.median([d[1] for d in r1509])) if r6 else np.nan,r6g_median_bands_of_8=float(np.median(nb)) if nb else np.nan))
df=pd.DataFrame(rows); os.makedirs(os.path.join(OUT,'tables'),exist_ok=True); df.to_csv(os.path.join(OUT,'tables','nam_sers_sessions.csv'),index=False,encoding='utf-8-sig')
pd.set_option('display.width',250); pd.set_option('display.max_columns',20); print(df.round(3).to_string())
