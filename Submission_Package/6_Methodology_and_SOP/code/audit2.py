import sys,os,re,pickle,numpy as np,pandas as pd
sys.path.insert(0,os.path.expanduser('~/work')); from lib2 import *
BULK={}
for f in ['NAM-15secs and power15-75-2sets','5sec-power5-80 and 2set','10sec-power5-80-2set','15sec-power5-80andset2','20sec-power5-80and set2','25sec-power5-80 and set2',
 '4-4-26/NAM multispot','4-4-26/35sec80power','4-4-26/40-80 nam','4-4-26/diffrent 3sec 80-100','4-4-26/samespot35sec diffrent power',
 '29-05-26/NAM-70p-10s-3acc','29-05-26/NAM-70p-10s-5ac','29-05-26/NAM-90p-10s-3ac','29-05-26/NAM-90p-10s-5ac','29-05-26/70p-5ac-10s-diifrentpoint',
 '29-05-26/70p-5ac-30s-diifrentspot','29-05-26/70p-60s-5ac-diifrentpoint','29-05-26/90p-30s-5ac-diifrentpoint','29-05-26/90p-30s-5acc-samespot',
 '29-05-26/90p-60s-5a-samespot','29-05-26/90p-60s-5ac-diffrentspot']: BULK[f]='NAM'
for f in ['4-4-26/LTA/45sec diffrent powrset2','4-4-26/LTA/10sec,diffrenpower,10set','4-4-26/5sec,30,50 power 10 set','4-4-26/LTA/30sec50power15set']: BULK[f]='LTA'
for f in ['13-4-26/lps/20-20-5','14-426/lps']: BULK[f]='LPS'
BULK['9-2-2026/20sec20power-variable location LTA']='SUSPECT'
rows=[]
for dp,dn,fn in os.walk(ROOT):
  rel_d=os.path.relpath(dp,ROOT)
  if rel_d.startswith(('SERS_Sepsis_Spectral_Library','_to_delete')): continue
  for f in sorted(fn):
    if not f.lower().endswith(('.csv','.txtr')): continue
    rel=os.path.join(rel_d,f) if rel_d!='.' else f
    meta,rs,dk,raw,ds=read_any(os.path.join(ROOT,rel))
    cls=BULK.get(rel_d,'OUT_OF_SCOPE')
    if rel_d=='29-05-26/glass slide empty': cls='GLASS' if f.startswith('glassslide') else 'NAM'
    d=dict(orig=rel,folder=rel_d,fmt=os.path.splitext(f)[1][1:],cls=cls,date=meta.get('Date','')[:19],
      power=meta.get('laser_powerlevel',''),int_s=meta.get('integration times(sec)',''),int_unit=meta.get('integration times unit',''),acc=meta.get('average number',''),
      laser_nm=meta.get('laser_wavelength',''),instrument=f"{meta.get('title','')} / {meta.get('model','')}",
      objective=meta.get('probe_name','') or 'not recorded in file (probe_name empty)',software=meta.get('File Version',''),
      npts=len(rs),rs_min=round(rs.min(),1) if len(rs) else None,rs_max=round(rs.max(),1) if len(rs) else None,
      raw_max=float(raw.max()) if len(rs) else None,ds_max=float(ds.max()) if len(rs) else None,ds_min=float(ds.min()) if len(rs) else None,
      saturated=bool(len(rs) and raw.max()>=65000))
    low=rel.lower(); d['spot_type']='same spot' if 'same' in low else ('different spot' if any(k in low for k in ['diff','multi','point','variable']) else 'not stated')
    rows.append(d)
A=pd.DataFrame(rows)
# folder-derived dates when header lacks one
A['date']=A.date.where(A.date!='',None)
for c in ['power','int_s','acc']: A[c]=pd.to_numeric(A[c],errors='coerce')
pickle.dump(A,open(os.path.expanduser('~/work/audit.pkl'),'wb'))
print(len(A)); print(A.cls.value_counts()); print(A[A.date.isna()][['orig','cls']].to_string()); print(A.npts.value_counts().head()); print(A.int_unit.value_counts())
print(A[A.cls!='OUT_OF_SCOPE'].objective.unique())
