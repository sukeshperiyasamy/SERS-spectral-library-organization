import pickle,numpy as np,pandas as pd
from scipy.signal import find_peaks,peak_widths,savgol_filter
D=pickle.load(open('lr2.pkl','rb'));E=pickle.load(open('lr3.pkl','rb'))
df=D['df'];P=D['P'];x=D['x'];ks=E['ks'];C=E['C'];fin=E['fin']
GZ=(x>=1308)&(x<=1455);keep=~GZ;dx=np.mean(np.diff(x))
noise={k:P[k]['p']['noise'] for k in ks}
allp=[]
for k in ks:
  c=P[k]['p']['corr'];pk,_=find_peaks(c,prominence=3*noise[k],distance=4);allp+=[x[j] for j in pk if 410<x[j]<1790]
allp=np.sort(allp);cl=[];cur=[allp[0]]
for v in allp[1:]:
  if v-cur[-1]<=5: cur.append(v)
  else: cl.append(cur);cur=[v]
cl.append(cur);cands=[np.median(c) for c in cl if len(c)>=0.4*len(ks)]
# blanks: unsaturated 40 s blank S03 + short blanks (full glass shape)
b3=P['Glass_Blank_20260928_P060pct_T40s_A05_S03.csv']['p'];sb=[P[f'Glass_Blank_20260928_P060pct_T05s_A01_S0{i}_short.csv']['p'] for i in (1,2)]
bc=b3['corr'];pkb,_=find_peaks(bc,prominence=5*b3['noise'],distance=4);wb=peak_widths(bc,pkb,rel_height=.5)[0]*dx
BF=[(x[j],w) for j,w in zip(pkb,wb) if 410<x[j]<1790]
sbc=np.mean([s['corr'] for s in sb],0);sbn=np.mean([s['noise'] for s in sb])/np.sqrt(2)
pks,_=find_peaks(sbc,prominence=5*sbn,distance=4);wsb=peak_widths(sbc,pks,rel_height=.5)[0]*dx
SBF=[(x[j],w) for j,w in zip(pks,wsb) if 410<x[j]<1790]
print('blank S03 features',[(round(a),round(b)) for a,b in BF]);print('short blank features',[(round(a),round(b)) for a,b in SBF])
LIT=[(550,'β(CH2) in ring','LPS-1 SERS'),(543,'δ(C-O-C) glycosidic ring','LPS-1 SERS'),(733,'β(C-O-C) carbohydrates','LPS-1 SERS'),(735,'common LPS peak','LPS-2 SERS'),(787,'ν(C-O) ring','LPS-1 SERS'),(794,'common LPS peak','LPS-2 SERS'),
 (850,'ν(C-O-C) 1,4-glycosidic','LPS-1 SERS'),(855,'δ(C-O-C)','LPS-1 SERS'),(894,'common LPS peak','LPS-2 SERS'),(917,'common LPS peak','LPS-2 SERS'),(973,'CH bending / C-O-C (lipid A/core)','LPS-3 normal Raman'),
 (981,'β(CH) lipid','LPS-1 SERS'),(988,'β(CH) carbohydrates','LPS-1 SERS'),(1003,'common LPS peak','LPS-2 SERS'),(1025,'ν(CO) carbohydrates','LPS-1 SERS'),(1075,'O-antigen','LPS-3 normal Raman'),(1087,'ν(C-O) lipid','LPS-1 SERS'),(1103,'LPS (whole cells)','LPS-7 Raman'),
 (1131,'ν(C-C) fatty acid','LPS-1 SERS'),(1309,'τ(CH3/CH2) lipid','LPS-1 SERS'),(1310,'C-H deformation (O-antigen/core)','LPS-3 normal Raman'),(1330,'δ(CH) phospholipid','LPS-1 SERS'),(1333,'common LPS peak (C-H def.)','LPS-2 SERS'),
 (1360,'C-H deformation (O-antigen/core)','LPS-3 normal Raman'),(1450,'CH2/CH3 deformation','LPS-1 SERS'),(1592,'common LPS peak','LPS-2 SERS'),(1610,'C=C stretch (lipid A/core)','LPS-3 normal Raman'),(1614,'common LPS peak','LPS-2 SERS')]
GEN={425:'carbohydrate skeletal δ(C-C-O)/δ(C-O-C) region (GEN-1 region I); O-P-O bending region (general) — no LPS literature band',
     860:'anomeric/glycosidic region; β-anomer C1-H ~898 (GEN-2)',898:'β-anomer C1-H deformation ~898 (GEN-2)',1080:'ν(C-O)/ν(C-C) sugar (GEN-1 region II); ν_s(PO2-) ~1080-1090 (GEN-5, GEN-6)',1125:'acyl-chain ν(C-C) 1060-1130 (GEN-5)'}
rows=[]
mc=C.mean(0)
for b in cands:
  pos=[];h=[];sn=[];hf=[]
  for k in ks:
    c=P[k]['p']['corr'];pk,_=find_peaks(c,prominence=3*noise[k],distance=4);nr=[j for j in pk if abs(x[j]-b)<=5]
    if nr:
      j=min(nr,key=lambda j:abs(x[j]-b));pos.append(x[j]);h.append(c[j]);sn.append(c[j]/noise[k]);hf.append(c[j]*float(fin.loc[fin.library_file==k,'intensity_factor'].iloc[0]))
  j=np.argmin(abs(x-b));j=j-3+np.argmax(mc[j-3:j+4]);fw=peak_widths(mc,[j],rel_height=.5)[0][0]*dx
  nm=E['mn'][j]
  bn=[f'{v:.0f} (FWHM {w:.0f})' for v,w in BF+SBF if abs(v-b)<=8]
  same=any(abs(v-b)<=8 and w<=3*fw for v,w in BF+SBF)
  lit='; '.join(f'{p} {a} [{s}]' for p,a,s in LIT if abs(p-b)<=12) or 'none within ±12'
  g=[v for kk,v in GEN.items() if abs(kk-b)<=15]
  rows.append(dict(band=round(b,1),detected=f'{len(pos)}/{len(ks)}',det_frac=len(pos)/len(ks),pos_mean=np.mean(pos) if pos else np.nan,pos_sd=np.std(pos,ddof=1) if len(pos)>1 else np.nan,
    height_median=np.median(h) if h else np.nan,height_mean=np.mean(h) if h else np.nan,height_cv=100*np.std(h,ddof=1)/np.mean(h) if len(h)>1 else np.nan,snr_median=np.median(sn) if sn else np.nan,snr_min=np.min(sn) if sn else np.nan,
    rel_425=nm, fwhm=fw,glass_zone=bool(1308<=b<=1455),blank_features=', '.join(bn) or 'none',in_blank=same,literature=lit,general=g[0] if g else '—'))
BT=pd.DataFrame(rows)
def cls(r):
  if r.glass_zone: return 'C3 - glass zone'
  if r.in_blank: return 'C3 - background (blank feature)'
  if r.det_frac>=1 and r.snr_median>=15 and r.band<1790: return 'C1 - primary marker'
  if r.det_frac>=0.9 and r.snr_median>=5: return 'C2 - supporting peak'
  return 'C4 - uncertain / weak'
BT['class']=BT.apply(cls,axis=1)
pickle.dump(dict(BT=BT,BF=BF,SBF=SBF,sbc=sbc,bc=bc),open('lr4.pkl','wb'))
pd.set_option('display.width',260);pd.set_option('display.max_colwidth',60)
print(BT[['band','detected','pos_mean','pos_sd','height_median','height_cv','snr_median','snr_min','rel_425','fwhm','blank_features','class']].round(2).to_string())
print(BT[['band','literature']].to_string())
