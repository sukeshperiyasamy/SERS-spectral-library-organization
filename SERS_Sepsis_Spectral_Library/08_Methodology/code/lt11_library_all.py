# LTA bulk session of 28 Oct 2026, all folders of bulk-lta: name, copy/move into the library, process, QC, references, bands, tables.
# Dry run (no arguments) prints the plan and QC summary. --apply writes into the library.
import os,re,sys,shutil,hashlib,csv,pickle,warnings
warnings.filterwarnings('ignore')
import numpy as np,pandas as pd
from scipy.signal import find_peaks,savgol_filter
from lib2 import read_any,process_v3h,LIB,ROOT,X
APPLY='--apply' in sys.argv
SRC=os.path.join(ROOT,'bulk-lta'); H=os.path.dirname(os.path.abspath(__file__)); GZ=(X>=1308)&(X<=1455); DATE='20261028'
md5=lambda p:hashlib.md5(open(p,'rb').read()).hexdigest()
d=pd.read_pickle(os.path.join(H,'lt9_unique.pkl'))                      # unique files (SP_1-8 of the spot folder are copies of the blanks)
R0=pickle.load(open(os.path.join(H,'lt4_result.pkl'),'rb')); REFN=R0['Nm']
def refspec(a):
    q=pd.read_csv(os.path.join(LIB,'03_Reference_Spectra',a,f'{a}_Bulk_Reference_Mean_SD.csv'),comment='#'); return np.interp(X,q.iloc[:,0].values,q['Normalised_mean'].values)
OTH={a:refspec(a) for a in ('NAM','LPS')}
# ---------- roles, groups, names
def spnum(o): return int(re.search(r'(\d+)',o).group(1))
def role(r):
    if r.folder in('glass blank','blank glass'): return 'blank'
    if 'same' in r['sub']: return 'samespot'
    return 'spot'
d['role']=d.apply(role,axis=1); d['sp']=d.orig.map(spnum); d=d.sort_values('acq').reset_index(drop=True)
CLEAN={(30.0,3):1333,(40.0,2):1443,(45.0,2):1510,(60.0,2):1680}
d['cat']=np.where(d.role=='blank','Glass_Blank','LTA_Bulk')
SUB={(80,45.0,2):'2026-10-28_80pct_45s_2acc',(80,30.0,3):'2026-10-28_80pct_30s_3acc',(70,30.0,3):'2026-10-28_70pct_30s_3acc',(70,60.0,2):'2026-10-28_70pct_60s_2acc'}
d['sub_lib']=[SUB.get((r.power,r.int_s,r.acc),'2026-10-28_power_series_45s_2acc') for r in d.itertuples()]
names=[None]*len(d)
for (cat,pw,it,ac),g in d.groupby(['cat','power','int_s','acc']):
    cnt=0
    if cat=='LTA_Bulk' and (pw,it,ac)==(80,45.0,2):                       # first block keeps S = SP number (S09-S36); same-spot scans follow
        sp_=g[g.role=='spot'];
        for i in sp_.index: names[i]=int(d.loc[i,'sp'])
        cnt=int(sp_.sp.max()); ss=g[g.role=='samespot']
        for i in ss.sort_values('acq').index: cnt+=1; names[i]=cnt
        continue
    if cat=='Glass_Blank' and (pw,it,ac)==(80,45.0,2):
        first=g[g.folder=='glass blank'].sort_values('acq');
        for k,i in enumerate(first.index,1): names[i]=k
        cnt=len(first)
        for i in g[g.folder!='glass blank'].sort_values('acq').index: cnt+=1; names[i]=cnt
        continue
    for i in g[g.role!='samespot'].sort_values('acq').index: cnt+=1; names[i]=cnt
    for i in g[g.role=='samespot'].sort_values('acq').index: cnt+=1; names[i]=cnt
d['S']=names
d['lib']=[f"{r.cat}_{DATE}_P{r.power:03d}pct_T{int(r.int_s):02d}s_A{r.acc:02d}_S{r.S:02d}"+('_samespot' if r.role=='samespot' else '')+'.csv' for r in d.itertuples()]
assert d.lib.is_unique
# ---------- processing
rec={}
for r in d.itertuples():
    meta,rs,dk,raw,ds=read_any(os.path.join(SRC,r.rel)); m=(rs>=400)&(rs<=1800); pr=process_v3h(rs,ds,raw); x=pr['x']
    hp=pr['ds']-savgol_filter(pr['ds'],31,2); rm=(x>=1550)&(x<=1800)
    rec[r.rel]=dict(meta=meta,pr=pr,corr=np.interp(X,x,pr['corr']),norm=np.interp(X,x,pr['norm']),dsx=np.interp(X,x,pr['ds']),rawmax=float(raw[m].max()),nsat=int((raw[m]>=65535).sum()),ripple=float(np.std(hp[rm])),noise=float(pr['noise']),dark=float(np.median(dk[m])))
def hmax(c,p,t=6): w=(X>=p-t)&(X<=p+t); return float(c[w].max())
# Sep glass template for blank QC
tm=[]
for nm_ in ('Glass_Blank_20260928_P060pct_T05s_A01_S01_short.csv','Glass_Blank_20260928_P060pct_T05s_A01_S02_short.csv'):
    meta_,rs_,dk_,raw_,ds_=read_any(os.path.join(LIB,'01_Raw_Data_Renamed','Glass_Blank',nm_)); p_=process_v3h(rs_,ds_,raw_); tm.append(np.interp(X,p_['x'],p_['corr']))
SEP=np.mean(tm,axis=0); nrm=lambda y:(y-y.min())/(y.max()-y.min())
# matched clean glass blank (80 % / 30 s / 3 acc) used as the glass template for the glass-share estimate
gb=[rec[r.rel]['corr'] for r in d.itertuples() if r.role=='blank' and (r.power,r.int_s,r.acc)==(80,30.0,3)]
GT=np.mean(gb,axis=0); GT=GT/GT[GZ].max(); FIT=(X>=1290)&(X<=1520)
for i,r in d.iterrows():
    e=rec[r.rel]; n=e['norm']; c=e['corr']; k=~GZ
    e['h1092']=hmax(c,1092); e['snr']=e['h1092']/e['noise']
    g=np.trapz(np.clip(c[GZ],0,None),X[GZ]); r8=np.trapz(np.clip(c[(X>=800)&(X<=1000)],0,None),X[(X>=800)&(X<=1000)]); e['glass_ratio']=float(g/r8) if r8>0 else np.nan
    e['rREF']=float(np.corrcoef(n[k],REFN[k])[0,1]); e['rNAM']=float(np.corrcoef(n[k],OTH['NAM'][k])[0,1]); e['rLPS']=float(np.corrcoef(n[k],OTH['LPS'][k])[0,1]); e['rSEP']=float(np.corrcoef(nrm(c)[k],nrm(SEP)[k])[0,1])
    exp=CLEAN.get((r.int_s,r.acc),np.nan); e['dark_expected']=exp; e['dark_excess']=e['dark']-exp if np.isfinite(exp) else np.nan; e['leak']=bool(np.isfinite(exp) and e['dark']-exp>150)
    Mx=np.vstack([GT[FIT],np.ones(FIT.sum()),X[FIT]]).T; e['glass_a']=float(np.linalg.lstsq(Mx,c[FIT],rcond=None)[0][0])
def classify(r,e):
    if r.role=='blank':
        if e['rSEP']<0.5: return 'BLANK-SUSPECT','not glass-like: sharp bands at 619, 1000, 1030, 1154, 1583 and 1602 cm-1 (polystyrene-like); r to the 28 Sep glass blanks = %.2f'%e['rSEP']
        if e['nsat']>0: return 'BLANK-SATURATED','glass band saturated (%d pixels at 65535); matches glass (r %.2f) but unusable as a full-condition blank'%(e['nsat'],e['rSEP'])
        return 'BLANK-OK','glass-like (r to the 28 Sep glass blanks %.2f), not saturated'%e['rSEP']
    if e['leak']: return 'FLAG-DARK','dark frame contains sample light: dark median %.0f vs clean %.0f (+%.0f counts); intensities under-estimated, ripple unreliable'%(e['dark'],e['dark_expected'],e['dark_excess'])
    if e['nsat']>0: return 'FAIL','saturated: %d pixels at 65535 in 400-1800 cm-1'%e['nsat']
    if e['snr']<10: return 'FAIL','SNR of the 1092 band %.1f (< 10): weak signal, spot probably off the powder'%e['snr']
    if e['glass_ratio']>=8: return 'EXCLUDE','glass-dominated (glass-zone / 800-1000 area ratio %.1f)'%e['glass_ratio']
    if e['rREF']<0.8: return 'EXCLUDE','atypical shape (r to the reference mean %.2f < 0.80): off-powder or glass-influenced spot'%e['rREF']
    if e['ripple']>50: return 'REVIEW','ripple %.1f counts (limit 50): marginal'%e['ripple']
    return 'PASS',''
qcs=[classify(r,rec[r.rel]) for r in d.itertuples()]; d['QC']=[q[0] for q in qcs]; d['why']=[q[1] for q in qcs]
d['leak']=[rec[r.rel]['leak'] for r in d.itertuples()]
POOL=d[(d.role=='spot')&(d.QC=='PASS')&(d.apply(lambda r:(r.power,r.int_s,r.acc) in ((80,45.0,2),(80,30.0,3)),axis=1))]
print(d.groupby(['role','sub_lib','QC']).size().unstack(fill_value=0).to_string())
print('pooled reference members:',len(POOL),POOL.groupby(['int_s']).size().to_dict())
# ---------- references
def build(ss):
    C=np.array([rec[r.rel]['corr'] for r in ss.itertuples()]); N=np.array([rec[r.rel]['norm'] for r in ss.itertuples()]); D=np.array([rec[r.rel]['dsx'] for r in ss.itertuples()])
    return dict(Mc=C.mean(0),Medc=np.median(C,axis=0),SDc=C.std(0,ddof=1),Nm=N.mean(0),Nmed=np.median(N,axis=0),Nsd=N.std(0,ddof=1),Dm=D.mean(0),C=C,N=N)
PL=build(POOL); r45=build(POOL[POOL.int_s==45.0]); r30=build(POOL[POOL.int_s==30.0])
cmp_={'r_pool_vs_v2':float(np.corrcoef(PL['Nm'][~GZ],REFN[~GZ])[0,1]),'r_30_vs_45':float(np.corrcoef(r30['Nm'][~GZ],r45['Nm'][~GZ])[0,1]),'r_pool_vs_NAM':float(np.corrcoef(PL['Nm'][~GZ],OTH['NAM'][~GZ])[0,1]),'r_pool_vs_LPS':float(np.corrcoef(PL['Nm'][~GZ],OTH['LPS'][~GZ])[0,1]),'mm':float(np.corrcoef(PL['Nm'][~GZ],PL['Nmed'][~GZ])[0,1])}
pw=[float(np.corrcoef(PL['N'][i][~GZ],PL['N'][j][~GZ])[0,1]) for i in range(len(POOL)) for j in range(i+1,len(POOL))]
cmp_['pair_mean']=float(np.mean(pw)); cmp_['pair_min']=float(np.min(pw)); print({k:round(v,3) for k,v in cmp_.items()})
# bands of the pooled reference
nz=float(np.mean([rec[r.rel]['noise'] for r in POOL.itertuples()])); pk,_=find_peaks(PL['Mc'],prominence=4*nz/np.sqrt(len(POOL)),distance=4)
rows=[]
for j in pk:
    c=float(X[j])
    if not 400<=c<=1800: continue
    dets=[];pos=[];hs=[];snr=[]
    for r in POOL.itertuples():
        e=rec[r.rel]; p,pr_=find_peaks(e['corr'],prominence=3*e['noise'],distance=4); sel=[(X[q],pr_['prominences'][i]) for i,q in enumerate(p) if abs(X[q]-c)<=6]
        h=hmax(e['corr'],c); hs.append(h); snr.append(h/e['noise']); dets.append(1 if sel else 0)
        if sel: pos.append(float(sel[int(np.argmax([z for _,z in sel]))][0]))
    mh=float(np.mean(hs)); mh3=float(np.mean([hmax(rec[r.rel]['corr'],c,3) for r in POOL.itertuples()])); gw=(X>=c-3)&(X<=c+3)
    share=100*float(np.mean([max(rec[r.rel]['glass_a']*GT[gw].max(),0) for r in POOL.itertuples()]))/mh3 if mh3>0 else np.nan
    rel=[hh/rec[r.rel]['h1092'] for hh,r in zip(hs,POOL.itertuples())]; relcv=100*np.std(rel,ddof=1)/np.mean(rel) if np.mean(rel)>0 else np.nan
    gz=1308<=c<=1455; det=sum(dets)/len(POOL)
    if gz: cl='C3 - glass zone'
    elif share>50: cl='C3 - background / glass'
    elif det>=1 and np.median(snr)>=15 and share<25 and relcv<=30: cl='C1 - primary marker'
    elif det>=0.8 and np.median(snr)>=5 and share<25: cl='C2 - supporting peak'
    else: cl='C4 - uncertain / weak'
    rows.append({'class':cl,'band':round(c,1),'detected':f'{sum(dets)}/{len(POOL)}','pos_mean':float(np.mean(pos)) if pos else c,'pos_sd':float(np.std(pos)) if len(pos)>1 else 0.0,'height_mean':mh,'height_sd':float(np.std(hs,ddof=1)),'height_cv':100*float(np.std(hs,ddof=1))/mh,'snr_median':float(np.median(snr)),'rel1092_cv':relcv,'glass_share_pct':share,'glass_zone':gz})
bands=pd.DataFrame(rows); pd.set_option('display.width',250); pd.set_option('display.max_columns',20); print(bands.round(1).to_string())
# condition table
ct=[]
for (role_,pw_,it_,ac_),g in d[d.role=='spot'].groupby(['role','power','int_s','acc']):
    ct.append(dict(power=pw_,int_s=it_,acc=ac_,n=len(g),PASS=int((g.QC=='PASS').sum()),REVIEW=int((g.QC=='REVIEW').sum()),EXCLUDE=int((g.QC=='EXCLUDE').sum()),FAIL=int((g.QC=='FAIL').sum()),FLAG_DARK=int((g.QC=='FLAG-DARK').sum()),
        dark_med=float(np.median([rec[x]['dark'] for x in g.rel])),raw_max_med=float(np.median([rec[x]['rawmax'] for x in g.rel])),ripple_med=float(np.median([rec[x]['ripple'] for x in g.rel])),snr_med=float(np.median([rec[x]['snr'] for x in g.rel])),h1092_med=float(np.median([rec[x]['h1092'] for x in g.rel])),rREF_med=float(np.median([rec[x]['rREF'] for x in g.rel]))))
ct=pd.DataFrame(ct); print(ct.round(1).to_string())
pickle.dump(dict(d=d,rec={k:{kk:vv for kk,vv in v.items() if kk not in('pr','meta')} for k,v in rec.items()},POOL=list(POOL.lib),PL=PL,r45=r45,r30=r30,cmp=cmp_,pw=pw,bands=bands,ct=ct,GT=GT,SEP=SEP),open(os.path.join(H,'lt11_result.pkl'),'wb'))
if not APPLY: print('dry run: nothing written'); sys.exit()
# ---------- write into the library
RAW=os.path.join(LIB,'01_Raw_Data_Renamed'); PRC=os.path.join(LIB,'02_Processed_Spectra')
def target(cat,sub,name,proc=False):
    base=PRC if proc else RAW; folder='LTA' if (proc and cat=='LTA_Bulk') else cat
    sub2=sub if cat=='LTA_Bulk' else '20261028_LTA_session'
    return os.path.join(base,folder,sub2,name.replace('.csv','_processed.csv') if proc else name)
def flat(cat,name,proc=False):
    base=PRC if proc else RAW; folder='LTA' if (proc and cat=='LTA_Bulk') else cat
    return os.path.join(base,folder,name.replace('.csv','_processed.csv') if proc else name)
inv=[]
for r in d.itertuples():
    t=target(r.cat,r.sub_lib,r.lib); os.makedirs(os.path.dirname(t),exist_ok=True); s=os.path.join(SRC,r.rel); f=flat(r.cat,r.lib)
    if os.path.exists(f) and not os.path.exists(t):
        if md5(f)!=md5(s): raise SystemExit('different content '+f)
        os.replace(f,t)
    elif not os.path.exists(t): shutil.copy2(s,t)
    ok=md5(t)==md5(s); e=rec[r.rel]
    role_txt={'spot':'LTA spot','samespot':'same-spot repeat scan (not independent)','blank':'glass blank'}[r.role]
    sample=('LTA from Staphylococcus aureus, Sigma-Aldrich L2515-10MG, lot 0000419622, source number 0000404178 (label: bacterial cell wall polymer; no purity figure on the supplier product sheet, lot certificate not obtained; also the vial used on 3 Apr 2026), bulk powder on glass slide') if r.role!='blank' else 'Glass_Blank (empty glass slide, same settings as the LTA spots)'
    pr=e['pr']; hdr=[f"# Library name: {r.lib}",f"# Original raw file (unchanged): bulk-lta/{r.rel}",f"# Role: {role_txt}",f"# Sample: {sample}",f"# Acquired (instrument clock): {r.acq} | B&W Tek i-Raman Plus BWS465-785H | 785 nm | Objective: not recorded in file",f"# Laser power level: {r.power} % (instrument setting) | Integration: {r.int_s:g} s | Accumulations: {r.acc}",
        f"# QC: {r.QC}"+(f" ({r.why})" if r.why else '')+f" | dark median {e['dark']:.0f} | ripple {e['ripple']:.1f} | noise {e['noise']:.1f} | 1092 band SNR {e['snr']:.1f} | saturated px 400-1800: {e['nsat']}",
        "# Pipeline v3: hot-pixel interpolation (CCD px 640, 700); crop 400-1800 cm-1; MAD spike removal (z>6, width<=2 px); Savitzky-Golay 11/3; ALS baseline lambda=1e5 p=0.01 10 it; min-max normalisation"]
    out=target(r.cat,r.sub_lib,r.lib,proc=True); os.makedirs(os.path.dirname(out),exist_ok=True); fo=flat(r.cat,r.lib,proc=True)
    if os.path.exists(fo) and not os.path.exists(out): os.replace(fo,out)
    with open(out,'w',encoding='utf-8',newline='') as fh:
        fh.write('\n'.join(hdr)+'\nRaman_Shift_cm-1,Raw_counts,DarkSubtracted_counts,HotPixelFixed_counts,Despiked_counts,Smoothed_counts,Baseline_counts,BaselineCorrected_counts,Normalised_0to1\n')
        for k in range(len(pr['x'])): fh.write(f"{pr['x'][k]:.3f},{pr['raw'][k]:.1f},{pr['ds'][k]:.2f},{pr['ds_hotfix'][k]:.2f},{pr['despiked'][k]:.2f},{pr['smooth'][k]:.2f},{pr['base'][k]:.2f},{pr['corr'][k]:.2f},{pr['norm'][k]:.5f}\n")
    inv.append(dict(original='bulk-lta/'+r.rel,category=r.cat,subfolder=(r.sub_lib if r.cat=='LTA_Bulk' else '20261028_LTA_session'),library_file=r.lib,role=role_txt,md5=md5(s),copy_ok=ok))
# April files: move into their own folder
for cat_,base_ in (('LTA_Bulk',RAW),):
    pass
for fn in sorted(os.listdir(os.path.join(RAW,'LTA_Bulk'))):
    p=os.path.join(RAW,'LTA_Bulk',fn)
    if os.path.isfile(p) and '_20260403_' in fn:
        t=os.path.join(RAW,'LTA_Bulk','2026-04-03_April_preliminary',fn); os.makedirs(os.path.dirname(t),exist_ok=True); os.replace(p,t)
for fn in sorted(os.listdir(os.path.join(PRC,'LTA'))):
    p=os.path.join(PRC,'LTA',fn)
    if os.path.isfile(p) and '_20260403_' in fn:
        t=os.path.join(PRC,'LTA','2026-04-03_April_preliminary',fn); os.makedirs(os.path.dirname(t),exist_ok=True); os.replace(p,t)
inv=pd.DataFrame(inv); print('placed',len(inv),'md5 ok',int(inv.copy_ok.sum()),'of',len(inv))
# QC log
qrows=[]
for r in d.itertuples():
    e=rec[r.rel]; qrows.append(dict(library_file=r.lib,subfolder=r.sub_lib if r.cat=='LTA_Bulk' else '20261028_LTA_session',category=r.cat,role=r.role,acq=r.acq,power=r.power,int_s=r.int_s,acc=r.acc,dark_med=round(e['dark'],1),dark_expected=e['dark_expected'],dark_excess=round(e['dark_excess'],1) if np.isfinite(e['dark_excess']) else np.nan,raw_max=e['rawmax'],nsat=e['nsat'],ripple=round(e['ripple'],2),noise=round(e['noise'],2),h1092=round(e['h1092'],1),snr1092=round(e['snr'],2),glass_ratio=round(e['glass_ratio'],2),rREF=round(e['rREF'],3),rNAM=round(e['rNAM'],3),rLPS=round(e['rLPS'],3),r_to_Sep_glass=round(e['rSEP'],3),QC=r.QC,QC_reason=r.why,original='bulk-lta/'+r.rel,in_reference=bool(r.lib in set(POOL.lib))))
qlog=pd.DataFrame(qrows); qlog.to_csv(os.path.join(LIB,'07_QC_and_Exclusions','LTA_Reference_Session_20261028_QC_Log.csv'),index=False,encoding='utf-8')
# exclusion log (append, no duplicates)
ex=os.path.join(LIB,'07_QC_and_Exclusions','Excluded_and_Flagged_Spectra.csv'); have={(x[0],x[1]) for x in csv.reader(open(ex,encoding='utf-8'))}; add=[]
for r in d.itertuples():
    if r.QC in('PASS','BLANK-OK'): continue
    dec={'FAIL':'FAIL','EXCLUDE':'EXCLUDED','REVIEW':'REVIEW (not in the reference)','FLAG-DARK':'FLAGGED - dark leak (not in the reference)','BLANK-SUSPECT':'FLAGGED - suspect blank','BLANK-SATURATED':'FLAGGED - blank saturated'}[r.QC]
    row=[r.lib,'bulk-lta/'+r.rel,'GLASS' if r.role=='blank' else 'LTA',r.power,f"{r.int_s:.1f}",r.acc,dec,r.why,(r.cat if r.cat=='Glass_Blank' else 'LTA_Bulk')+'/'+(r.sub_lib if r.cat=='LTA_Bulk' else '20261028_LTA_session')]
    if row[0].replace('.csv','')[-0:]=='' : pass
    add.append(row)
# older rows of this session (written with the first version) are replaced by the current ones: drop rows whose original path is in bulk-lta/ and file name is the old flat name
old=list(csv.reader(open(ex,encoding='utf-8'))); head,body=old[0],old[1:]
cur={r.lib for r in d.itertuples()}
body=[b for b in body if not (b[1].startswith('bulk-lta/') and b[0]!='(not copied)')]
body+= [b for b in add]
for i in range(1,9): body.append(['(not copied)',f'bulk-lta/45sec-80p-2acc-diffrentspot/SP_{i}.csv','LTA',80,'45.0',2,'EXCLUDED - duplicate',f'Identical (MD5) to glass blank SP_{i}; not an LTA spectrum. The blank is in Glass_Blank/20261028_LTA_session/Glass_Blank_{DATE}_P080pct_T45s_A02_S{i:02d}.csv','Not copied (identical file in Glass_Blank)']) if not any(b[0]=='(not copied)' and b[1].endswith(f'SP_{i}.csv') and 'diffrentspot' in b[1] for b in body) else None
with open(ex,'w',newline='',encoding='utf-8') as f: w=csv.writer(f,lineterminator='\n'); w.writerow(head); w.writerows(body)
print('exclusion log rows now',len(body))
# reference files (v2 files stay unchanged; pooled files are new)
RD=os.path.join(LIB,'03_Reference_Spectra','LTA'); mem=list(POOL.lib)
head=[f'# LTA bulk powder on glass slide - REFERENCE v2.1 POOLED (28 Oct 2026; n = {len(POOL)} independent spots: {int((POOL.int_s==45).sum())} at 80 % / 45 s / 2 acc and {int((POOL.int_s==30).sum())} at 80 % / 30 s / 3 acc, all with a clean dark)',
 '# Sample: LTA from Staphylococcus aureus, Sigma-Aldrich L2515-10MG, lot 0000419622, source number 0000404178 (purity not recorded)',f"# Condition: 785 nm, 80 % laser power (instrument setting); two integration settings pooled because the normalised spectra agree (r = {cmp_['r_30_vs_45']:.3f}); shutter-closed dark; pipeline v3",
 '# Members: '+'; '.join(mem),f'# Representative spectrum = MEAN of normalised spectra (median agrees: r = {cmp_["mm"]:.4f}); absolute counts differ between the two settings and between spots, compare band ratios',
 '# The v2 reference (n = 10, 80 % / 45 s / 2 acc only) is kept unchanged as LTA_Bulk_Reference_20261028_Mean_SD.csv']
with open(os.path.join(RD,'LTA_Bulk_Reference_20261028_Pooled_Mean_SD.csv'),'w',encoding='utf-8',newline='') as f:
    f.write('\n'.join(head)+'\nRaman_Shift_cm-1,BaselineCorrected_mean_counts,BaselineCorrected_median_counts,BaselineCorrected_SD_counts,DarkSubtracted_mean_counts,Normalised_mean,Normalised_median,Normalised_SD\n')
    for k in range(len(X)): f.write(f"{X[k]:.1f},{PL['Mc'][k]:.2f},{PL['Medc'][k]:.2f},{PL['SDc'][k]:.2f},{PL['Dm'][k]:.2f},{PL['Nm'][k]:.5f},{PL['Nmed'][k]:.5f},{PL['Nsd'][k]:.5f}\n")
members=pd.DataFrame([dict(library_file=r.lib,subfolder=r.sub_lib,original_file='bulk-lta/'+r.rel,acq=r.acq,power_pct=r.power,int_s=r.int_s,acc=r.acc,dark_med=round(rec[r.rel]['dark'],1),raw_max=rec[r.rel]['rawmax'],ripple=round(rec[r.rel]['ripple'],2),noise=round(rec[r.rel]['noise'],2),h1092=round(rec[r.rel]['h1092'],1),snr1092=round(rec[r.rel]['snr'],1),glass_ratio=round(rec[r.rel]['glass_ratio'],2),rREF=round(rec[r.rel]['rREF'],3),rNAM=round(rec[r.rel]['rNAM'],3),rLPS=round(rec[r.rel]['rLPS'],3)) for r in POOL.itertuples()])
members.to_csv(os.path.join(RD,'LTA_Reference_20261028_Pooled_Members.csv'),index=False,encoding='utf-8'); bands.round(3).to_csv(os.path.join(RD,'LTA_Reference_20261028_Pooled_Marker_Peaks.csv'),index=False,encoding='utf-8')
# tables for the report
os.makedirs(os.path.join(LIB,'05_Tables'),exist_ok=True); ct.round(2).to_csv(os.path.join(LIB,'05_Tables','LTA_20261028_condition_comparison.csv'),index=False)
# workbook
import openpyxl
from openpyxl.styles import PatternFill,Font
wbp=os.path.join(LIB,'05_Tables','Spectral_Library_Metadata_and_Peaks.xlsx'); wb=openpyxl.load_workbook(wbp)
def addsheet(name,df):
    if name in wb.sheetnames: del wb[name]
    ws=wb.create_sheet(name); ws.append(list(df.columns))
    for c in ws[1]: c.fill=PatternFill('solid',fgColor='D9D9D9'); c.font=Font(bold=True)
    for r in df.itertuples(index=False): ws.append([None if (isinstance(v,float) and np.isnan(v)) else (v.item() if hasattr(v,'item') else v) for v in r])
    for i,col in enumerate(df.columns): ws.column_dimensions[openpyxl.utils.get_column_letter(i+1)].width=max(10,min(40,len(str(col))+4))
stat=pd.DataFrame([['Status','ESTABLISHED, pending operator confirmation (28 Oct 2026); pooled reference v2.1'],['Sample','LTA from Staphylococcus aureus, Sigma-Aldrich L2515-10MG, lot 0000419622, source number 0000404178 (purity not recorded; same vial as 3 Apr 2026)'],['Reference v2.1',f'n = {len(POOL)} spots (clean dark): {int((POOL.int_s==45).sum())} at 80 %/45 s/2 acc + {int((POOL.int_s==30).sum())} at 80 %/30 s/3 acc'],['Reference v2','n = 10 spots at 80 %/45 s/2 acc (unchanged)'],['Agreement',f'pooled vs v2 r {cmp_["r_pool_vs_v2"]:.3f}; 30 s vs 45 s mean r {cmp_["r_30_vs_45"]:.3f}; to LPS {cmp_["r_pool_vs_LPS"]:.2f}; to NAM {cmp_["r_pool_vs_NAM"]:.2f}'],['Primary markers',', '.join(f'{x.band:.0f}' for x in bands.itertuples() if x._1.startswith('C1'))],['Supporting',', '.join(f'{x.band:.0f}' for x in bands.itertuples() if x._1.startswith('C2'))],['Dark leak','%d of %d LTA spectra have a dark frame containing sample light (see the QC log)'%(int((d[d.role!="blank"].QC=="FLAG-DARK").sum()),int((d.role!="blank").sum()))]],columns=['Item','Value'])
addsheet('43_LTA_Ref_Inventory',inv); addsheet('44_LTA_Ref_QC',qlog); addsheet('45_LTA_Ref_Bands',bands.round(3)); addsheet('46_LTA_Ref_Members',members); addsheet('47_LTA_Final_Status',stat); addsheet('48_LTA_Conditions',ct.round(2)); wb.save(wbp)
inv.to_csv(os.path.join(H,'lt11_inventory.csv'),index=False); print('library updated')
