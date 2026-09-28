import os,shutil,hashlib,pickle,numpy as np,pandas as pd
from scipy.signal import find_peaks,peak_widths
from lib2 import LIB
D=pickle.load(open('lp2.pkl','rb'));df=D['df'];P=D['P'];x=D['x']
GZ=(x>=1308)&(x<=1455);keep=~GZ;dx=np.mean(np.diff(x))
SRC=os.path.expanduser('~/mnt/sukesh/28-9-26-lps-bulk')
md5=lambda p: hashlib.md5(open(p,'rb').read()).hexdigest()
df['library_file']=[f"{r.category}_20260928_P{r.power:03d}pct_T{int(r.int_s)}s_A{r.acc:02d}_S{r.num:02d}.csv" for r in df.itertuples()]
# blanks numbered by acquisition order per power (already 1..n from names)
assert df.library_file.is_unique
for i,r in df.iterrows():
  src=os.path.join(SRC,r.orig); dst=os.path.join(LIB,'01_Raw_Data_Renamed',r.category,r.library_file)
  if os.path.exists(dst): raise SystemExit('exists '+dst)
  shutil.copy2(src,dst); df.loc[i,'md5']=md5(src); df.loc[i,'copy_ok']=md5(dst)==md5(src)
# core sets
df['in_core']=False
for pw in (60,70):
  m=(df.power==pw)&(df.category=='LPS_Bulk')&(df.QC=='PASS')
  df.loc[m&(df.r_to_others_mean>=0.85),'in_core']=True
  df.loc[m&(df.r_to_others_mean<0.85),'QC_reason']='Valid but glass-dominated (r to other spots %s < 0.85; high glass background) - excluded from mean'
df.loc[df.QC_reason.str.startswith('Valid but'),'QC']='REVIEW'
for i in df.index:
  if df.QC[i]=='REVIEW': df.loc[i,'QC_reason']='Valid but glass-dominated (r to other spots = %.2f < 0.85; strong glass background) - excluded from mean'%df.r_to_others_mean[i]
# blank features (outside saturation) with widths
BF={}
for pw in (60,70,80):
  s=df[(df.power==pw)&(df.category=='Glass_Blank')]; cb=np.mean([P[k]['p']['corr'] for k in s.key],0); nb=np.mean([P[k]['p']['noise'] for k in s.key])
  pk,_=find_peaks(cb,prominence=5*nb,distance=4); w=peak_widths(cb,pk,rel_height=.5)[0]*dx
  BF[pw]=dict(sat=(s.sat_from.min(),s.sat_to.max()),feat=[(x[k],ww) for k,ww in zip(pk,w) if 410<x[k]<1790])
# candidate bands: cluster peaks from core spectra
core=list(df[df.in_core].key); allp=[]
for k in core:
  c=P[k]['p']['corr'];n=P[k]['p']['noise'];pk,_=find_peaks(c,prominence=3*n,distance=4); allp+= [x[j] for j in pk if 410<x[j]<1790]
allp=np.sort(allp);cl=[];cur=[allp[0]]
for v in allp[1:]:
  if v-cur[-1]<=5: cur.append(v)
  else: cl.append(cur);cur=[v]
cl.append(cur)
cands=[np.median(c) for c in cl if len(c)>=0.4*len(core)]
LIT=[(550,'β(CH2) in ring','L1'),(680,'δ(C-O-C); fatty acid','L1'),(850,'ν(C-O-C) 1,4-glycosidic link','L1'),(988,'β(CH) carbohydrates','L1'),(1131,'ν(C-C) fatty acid','L1'),(1330,'δ(CH) phospholipid','L1'),(1450,'CH3/CH2 deformation','L1'),(543,'saccharide and lipid','L1'),(981,'saccharide and lipid','L1'),
 (735,'common LPS peak','L2'),(794,'common LPS peak','L2'),(894,'common LPS peak','L2'),(917,'common LPS peak','L2'),(1003,'common LPS peak','L2'),(1333,'common LPS peak (C-H def.)','L2'),(1592,'common LPS peak','L2'),(1614,'common LPS peak','L2'),(1103,'lipopolysaccharide (whole cells)','L3')]
NAMM=[541,829,870.5,929,955,1022.7,1127]
rows=[]
for b in cands:
  r=dict(band=round(b,1))
  for pw in (60,70):
    ks=[k for k in core if k.startswith(str(pw))]; pos=[];h=[];sn=[];fw=[]
    for k in ks:
      c=P[k]['p']['corr'];n=P[k]['p']['noise'];pk,_=find_peaks(c,prominence=3*n,distance=4)
      nr=[j for j in pk if abs(x[j]-b)<=5]
      if nr:
        j=min(nr,key=lambda j:abs(x[j]-b));pos.append(x[j]);h.append(c[j]);sn.append(c[j]/n)
    r[f'{pw}_det']=f'{len(pos)}/{len(ks)}';r[f'{pw}_frac']=len(pos)/len(ks)
    r[f'{pw}_pos']=np.mean(pos) if pos else np.nan;r[f'{pw}_pos_sd']=np.std(pos,ddof=1) if len(pos)>1 else np.nan
    r[f'{pw}_h']=np.mean(h) if h else np.nan;r[f'{pw}_cv']=100*np.std(h,ddof=1)/np.mean(h) if len(h)>1 else np.nan;r[f'{pw}_snr']=np.mean(sn) if sn else np.nan
  mc=np.mean([P[k]['p']['corr'] for k in core if k.startswith('70')],0);j=np.argmin(abs(x-b));j=j-3+np.argmax(mc[j-3:j+4])
  r['fwhm']=peak_widths(mc,[j],rel_height=.5)[0][0]*dx
  r['glass_zone']=bool(1308<=b<=1455)
  bn=[]
  for pw in (60,70):
    lo,hi=BF[pw]['sat']
    if lo-10<=b<=hi+10: bn.append(f'{pw}%: blank saturated')
    else:
      m=[(v,w) for v,w in BF[pw]['feat'] if abs(v-b)<=6]
      if m: bn.append(f'{pw}%: blank feature {m[0][0]:.0f} (FWHM {m[0][1]:.0f})'+(' - same width' if m[0][1]<=3*r['fwhm'] else ' - much broader, not same band'))
  r['blank']='; '.join(bn) if bn else 'not in blank'
  r['LPS_lit_within_10']='; '.join(f'{p} ({a}; {s})' for p,a,s in LIT if abs(p-b)<=10) or 'none'
  r['near_NAM_marker']=any(abs(m-b)<=4 for m in NAMM)
  rows.append(r)
BT=pd.DataFrame(rows)
def cls(r):
  if r.glass_zone: return 'C3 - glass zone (glass-dominated)'
  if 'same width' in r.blank: return 'C3 - background (in blank)'
  f=min(r['60_frac'],r['70_frac'])
  if f>=1 and r['70_snr']>=15 and r['70_cv']<=15: return 'C1 - candidate primary band'
  if f>=0.75: return 'C2 - candidate supporting band (weak)'
  return 'C4 - uncertain / weak'
BT['class']=BT.apply(cls,axis=1)
pickle.dump(dict(df=df,P=P,x=x,BT=BT,BF=BF,core=core,NAM=D['NAM'],LTA=D['LTA'],OLD=D['OLD']),open('lp4.pkl','wb'))
pd.set_option('display.width',260)
print(BT[['band','60_det','70_det','70_pos','70_pos_sd','70_h','70_cv','70_snr','60_h','60_cv','60_snr','fwhm','blank','LPS_lit_within_10','class']].round(1).to_string())
print({k:(v['sat'],[(round(a),round(b)) for a,b in v['feat']]) for k,v in BF.items()})
print(df.copy_ok.all(), df[['key','library_file','QC','QC_reason']].to_string())
