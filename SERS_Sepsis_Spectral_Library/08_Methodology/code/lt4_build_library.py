# LTA bulk re-acquisition (28 Oct 2026, 80 % / 45 s / 2 acc): copy, process, QC, reference, bands, figures and library tables.
# Run without arguments for a dry run (prints QC classes and bands); with --apply it writes into the library.
import os,sys,re,shutil,hashlib,csv,pickle,warnings
warnings.filterwarnings('ignore')
import numpy as np,pandas as pd
from scipy.signal import find_peaks,savgol_filter
from lib2 import read_any,process_v3h,LIB,ROOT,X
APPLY='--apply' in sys.argv
SRC=os.path.join(ROOT,'bulk-lta'); H=os.path.dirname(os.path.abspath(__file__))
md5=lambda p:hashlib.md5(open(p,'rb').read()).hexdigest()
DATE='20261028'; COND='P080pct_T45s_A02'
GZ=(X>=1308)&(X<=1455)
def natkey(s): return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)',s)]
def refspec(a):
    d=pd.read_csv(os.path.join(LIB,'03_Reference_Spectra',a,f'{a}_Bulk_Reference_Mean_SD.csv'),comment='#'); return np.interp(X,d.iloc[:,0].values,d['Normalised_mean'].values)
REF={a:refspec(a) for a in ('NAM','LPS','LTA')}
# ---------------- 1. inventory and processing
items=[]
for i in range(1,9): items.append(dict(src=f'glass blank/SP_{i}.csv',cat='Glass_Blank',new=f'Glass_Blank_{DATE}_{COND}_S{i:02d}.csv',n=i,role='matched glass blank (80 % / 45 s / 2 acc)'))
for i in range(9,37): items.append(dict(src=f'45sec-80p-2acc-diffrentspot/SP_{i}.csv',cat='LTA_Bulk',new=f'LTA_Bulk_{DATE}_{COND}_S{i:02d}.csv',n=i,role='LTA spot'))
for it in items:
    p=os.path.join(SRC,it['src']); meta,rs,dk,raw,ds=read_any(p); m=(rs>=400)&(rs<=1800)
    pr=process_v3h(rs,ds,raw); x=pr['x']
    hp=pr['ds']-savgol_filter(pr['ds'],31,2); rm=(x>=1550)&(x<=1800)
    it.update(meta=meta,pr=pr,dark=float(np.median(dk[m])),raw_med=float(np.median(raw[m])),raw_max=float(raw[m].max()),nsat=int((raw[m]>=65535).sum()),ripple=float(np.std(hp[rm])),noise=float(pr['noise']),
              corr=np.interp(X,x,pr['corr']),norm=np.interp(X,x,pr['norm']),dsx=np.interp(X,x,pr['ds']),acq=meta.get('Date',''),power=int(float(meta['laser_powerlevel'])),int_s=float(meta['integration times(sec)']),acc=int(float(meta['average number'])),md5=md5(p))
blanks=[i for i in items if i['cat']=='Glass_Blank']; spots=[i for i in items if i['cat']=='LTA_Bulk']
BL=np.mean([b['corr'] for b in blanks],axis=0)
# glass template from the 28 Sep glass blanks (60 % / 5 s / 1 acc, unsaturated); the 28 Oct blanks are polystyrene-like (see QC) and are not used as the glass template
tm=[]
for nm_ in ('Glass_Blank_20260928_P060pct_T05s_A01_S01_short.csv','Glass_Blank_20260928_P060pct_T05s_A01_S02_short.csv'):
    meta_,rs_,dk_,raw_,ds_=read_any(os.path.join(LIB,'01_Raw_Data_Renamed','Glass_Blank',nm_)); p_=process_v3h(rs_,ds_,raw_); tm.append(np.interp(X,p_['x'],p_['corr']))
GT=np.mean(tm,axis=0); GT=GT/GT[GZ].max(); FIT=(X>=1290)&(X<=1520)
def nrm(y): return (y-y.min())/(y.max()-y.min())
r_blank_old=float(np.corrcoef(nrm(BL)[~GZ],nrm(np.mean(tm,axis=0))[~GZ])[0,1])
blank_ps=[(float(X[j]),float(BL[j])) for j in find_peaks(BL,prominence=60,width=3)[0]]
BLANK_NOTE='SUSPECT: sharp bands at 619, 1000, 1030, 1154, 1583 and 1602 cm-1 (strongest at 1000, polystyrene-like); r to the 28 Sep glass blanks = %.2f. Not used as the glass template'%r_blank_old
def hmax(c,p,t=6): w=(X>=p-t)&(X<=p+t); return float(c[w].max())
for s in spots:
    s['h1092']=hmax(s['corr'],1092); s['snr1092']=s['h1092']/s['noise']
    g=np.trapz(np.clip(s['corr'][GZ],0,None),X[GZ]); r8=np.trapz(np.clip(s['corr'][(X>=800)&(X<=1000)],0,None),X[(X>=800)&(X<=1000)]); s['glass_ratio']=float(g/r8) if r8>0 else np.nan
    for a in REF: s['r'+a]=float(np.corrcoef(s['norm'][~GZ],REF[a][~GZ])[0,1])
    Mx=np.vstack([GT[FIT],np.ones(FIT.sum()),X[FIT]]).T; s['glass_a']=float(np.linalg.lstsq(Mx,s['corr'][FIT],rcond=None)[0][0])
for b in blanks: b['glass_ratio']=np.nan
prov=[s for s in spots if s['nsat']==0 and s['ripple']<=50 and s['snr1092']>=10 and s['glass_ratio']<8]
core0=np.mean([s['norm'] for s in prov],axis=0)
for s in spots: s['r_core']=float(np.corrcoef(s['norm'][~GZ],core0[~GZ])[0,1])
def classify(s):
    if s['nsat']>0: return 'FAIL','saturated: %d pixels at 65535 in 400-1800 cm-1'%s['nsat']
    if s['snr1092']<10: return 'FAIL','SNR of the 1092 band %.1f (< 10): weak signal, spot probably off the powder'%s['snr1092']
    if s['glass_ratio']>=8: return 'EXCLUDE','glass-dominated (glass-zone / 800-1000 area ratio %.1f)'%s['glass_ratio']
    if s['r_core']<0.8: return 'EXCLUDE','atypical shape (r to the core mean %.2f < 0.80; r to April LTA %.2f): off-powder or glass-influenced spot'%(s['r_core'],s['rLTA'])
    if s['ripple']>50: return 'REVIEW','ripple %.1f counts (limit 50): marginal; brightest spots, ripple tracks noise'%s['ripple']
    return 'PASS',''
for s in spots: s['QC'],s['why']=classify(s)
for b in blanks: b['QC'],b['why']='BLANK-SUSPECT',BLANK_NOTE+'; no saturation (raw max %.0f)'%b['raw_max']
core=[s for s in spots if s['QC']=='PASS']; ext=[s for s in spots if s['QC'] in('PASS','REVIEW')]
print('QC:',{q:[s['n'] for s in spots if s['QC']==q] for q in ('PASS','REVIEW','EXCLUDE','FAIL')}); print('core n =',len(core),'extended n =',len(ext))
# ---------------- 2. reference
def stack(ss,k): return np.array([s[k] for s in ss])
Mc=stack(core,'corr').mean(0); Medc=np.median(stack(core,'corr'),axis=0); SDc=stack(core,'corr').std(0,ddof=1)
Nm=stack(core,'norm').mean(0); Nmed=np.median(stack(core,'norm'),axis=0); Nsd=stack(core,'norm').std(0,ddof=1); Dm=stack(core,'dsx').mean(0)
Me=stack(ext,'corr').mean(0); Ne=stack(ext,'norm').mean(0)
sens=float(np.corrcoef(Nm[~GZ],((Me-Me.min())/(Me.max()-Me.min()))[~GZ])[0,1]); mm_r=float(np.corrcoef(Nm[~GZ],Nmed[~GZ])[0,1])
cmp={a:float(np.corrcoef(Nm[~GZ],REF[a][~GZ])[0,1]) for a in REF}
print('mean vs median r',round(mm_r,4),'| strict vs extended mean r',round(sens,4),'| vs refs',{k:round(v,3) for k,v in cmp.items()})
pw=[float(np.corrcoef(a['norm'][~GZ],b['norm'][~GZ])[0,1]) for i,a in enumerate(core) for b in core[i+1:]]; print('pairwise r core mean',round(float(np.mean(pw)),3),'min',round(float(np.min(pw)),3))
# ---------------- 3. bands
nz=float(np.mean([s['noise'] for s in core])); pk,pp=find_peaks(Mc,prominence=4*nz/np.sqrt(len(core)),distance=4)
cands=[float(X[j]) for j in pk if 400<=X[j]<=1800]
bl_pk,_=find_peaks(BL,prominence=4*float(np.mean([b['noise'] for b in blanks]))/np.sqrt(len(blanks)),distance=4); BLP=[float(X[j]) for j in bl_pk]
rows=[]
for c in cands:
    dets=[];pos=[];hs=[];snr=[]
    for s in core:
        p,pr_=find_peaks(s['corr'],prominence=3*s['noise'],distance=4); sel=[(X[j],pr_['prominences'][i]) for i,j in enumerate(p) if abs(X[j]-c)<=6]
        h=hmax(s['corr'],c); hs.append(h); snr.append(h/s['noise'])
        if sel: dets.append(1); pos.append(float(sel[int(np.argmax([q for _,q in sel]))][0]))
        else: dets.append(0)
    mh=float(np.mean(hs)); mh3=float(np.mean([hmax(s['corr'],c,3) for s in core])); gw=(X>=c-3)&(X<=c+3); share=100*float(np.mean([max(s['glass_a']*GT[gw].max(),0) for s in core]))/mh3 if mh3>0 else np.nan   # glass share at the band position (+/-3 cm-1), 28 Sep glass template scaled per spot on 1290-1520 cm-1 (exploratory)
    rel=[h/s['h1092'] for h,s in zip(hs,core)]; relcv=100*np.std(rel,ddof=1)/np.mean(rel) if np.mean(rel)>0 else np.nan
    inb=False; gz=1308<=c<=1455
    det=sum(dets)/len(core)
    if gz and share>50: cl='C3 - glass zone (glass-dominated)'
    elif gz: cl='C3 - glass zone'
    elif inb and share>50 or share>50: cl='C3 - background / glass'
    elif det>=1 and np.median(snr)>=15 and share<25 and relcv<=30: cl='C1 - primary marker'
    elif det>=0.8 and np.median(snr)>=5 and share<25: cl='C2 - supporting peak'
    else: cl='C4 - uncertain / weak'
    rows.append(dict(**{'class':cl},band=round(c,1),detected=f'{sum(dets)}/{len(core)}',pos_mean=float(np.mean(pos)) if pos else c,pos_sd=float(np.std(pos)) if len(pos)>1 else 0.0,height_mean=mh,height_sd=float(np.std(hs,ddof=1)),height_cv=100*float(np.std(hs,ddof=1))/mh,snr_median=float(np.median(snr)),rel1092_cv=relcv,glass_share_pct=share,glass_zone=gz))
bands=pd.DataFrame(rows); pd.set_option('display.width',250); pd.set_option('display.max_columns',20); print(bands.round(1).to_string())
pickle.dump(dict(spots=spots,blanks=blanks,core=[s['n'] for s in core],ext=[s['n'] for s in ext],Mc=Mc,Medc=Medc,SDc=SDc,Nm=Nm,Nmed=Nmed,Nsd=Nsd,Dm=Dm,BL=BL,bands=bands,cmp=cmp,sens=sens,mm_r=mm_r,pw=pw,Ne=Ne,GT=GT,a_med=float(np.median([s['glass_a'] for s in core])),r_blank_old=r_blank_old),open(os.path.join(H,'lt4_result.pkl'),'wb'))
if not APPLY: print('dry run: nothing written'); sys.exit()
# ---------------- 4. write into the library
raw_dir={c:os.path.join(LIB,'01_Raw_Data_Renamed',c) for c in ('LTA_Bulk','Glass_Blank')}
proc_dir={c:os.path.join(LIB,'02_Processed_Spectra',c) for c in ('LTA','Glass_Blank')}
inv=[]
for it in items:
    d=os.path.join(raw_dir[it['cat']],it['new']); s=os.path.join(SRC,it['src'])
    if os.path.exists(d):
        if md5(d)!=md5(s): raise SystemExit('exists with different content: '+d)
    else: shutil.copy2(s,d)
    ok=md5(s)==md5(d); inv.append(dict(original='bulk-lta/'+it['src'],category=it['cat'],library_file=it['new'],role=it['role'],md5=it['md5'],copy_ok=ok))
    sample='LTA from Staphylococcus aureus, Sigma-Aldrich L2515-10MG, lot 0000419622, source number 0000404178 (purity not recorded), bulk powder on glass slide' if it['cat']=='LTA_Bulk' else 'Glass_Blank (empty glass slide, same settings as the LTA spots)'
    qc=f"# QC: {it['QC']} {('(' + it['why'] + ')') if it['why'] else ''} | dark median {it['dark']:.0f} | ripple {it['ripple']:.1f} | noise {it['noise']:.1f}"+(f" | 1092 band SNR {it['snr1092']:.1f}" if it['cat']=='LTA_Bulk' else '')+f" | saturated px 400-1800: {it['nsat']}"
    pr=it['pr']; hdr=[f"# Library name: {it['new']}",f"# Original raw file (unchanged): bulk-lta/{it['src']}",f"# Role: {it['role']}",f"# Sample: {sample}",
        f"# Acquired (instrument clock): {it['acq']} | B&W Tek i-Raman Plus BWS465-785H | 785 nm | Objective: not recorded in file",f"# Laser power level: {it['power']} % (instrument setting) | Integration: {it['int_s']:g} s | Accumulations: {it['acc']}",qc,
        "# Pipeline v3: hot-pixel interpolation (CCD px 640, 700); crop 400-1800 cm-1; MAD spike removal (z>6, width<=2 px); Savitzky-Golay 11/3; ALS baseline lambda=1e5 p=0.01 10 it; min-max normalisation"]
    out=os.path.join(proc_dir['LTA' if it['cat']=='LTA_Bulk' else 'Glass_Blank'],it['new'].replace('.csv','_processed.csv'))
    with open(out,'w',encoding='utf-8',newline='') as f:
        f.write('\n'.join(hdr)+'\nRaman_Shift_cm-1,Raw_counts,DarkSubtracted_counts,HotPixelFixed_counts,Despiked_counts,Smoothed_counts,Baseline_counts,BaselineCorrected_counts,Normalised_0to1\n')
        for k in range(len(pr['x'])): f.write(f"{pr['x'][k]:.3f},{pr['raw'][k]:.1f},{pr['ds'][k]:.2f},{pr['ds_hotfix'][k]:.2f},{pr['despiked'][k]:.2f},{pr['smooth'][k]:.2f},{pr['base'][k]:.2f},{pr['corr'][k]:.2f},{pr['norm'][k]:.5f}\n")
inv=pd.DataFrame(inv); print('copied',len(inv),'md5 ok',int(inv.copy_ok.sum()))
# QC log
qlog=pd.DataFrame([dict(library_file=i['new'],category=i['cat'],role=i['role'],acq=i['acq'],power=i['power'],int_s=i['int_s'],acc=i['acc'],dark_med=round(i['dark'],1),raw_med=round(i['raw_med'],0),raw_max=i['raw_max'],nsat=i['nsat'],ripple=round(i['ripple'],2),noise=round(i['noise'],2),
                     h1092=round(i.get('h1092',np.nan),1),snr1092=round(i.get('snr1092',np.nan),2),glass_ratio=round(i.get('glass_ratio',np.nan),2),r_core=round(i.get('r_core',np.nan),3),rLTA_April=round(i.get('rLTA',np.nan),3),rNAM=round(i.get('rNAM',np.nan),3),rLPS=round(i.get('rLPS',np.nan),3),
                     QC=i['QC'],QC_reason=i['why'],original='bulk-lta/'+i['src'],in_reference=bool(i in core)) for i in items])
qlog.to_csv(os.path.join(LIB,'07_QC_and_Exclusions','LTA_Reference_Session_20261028_QC_Log.csv'),index=False,encoding='utf-8')
# exclusion log
ex=os.path.join(LIB,'07_QC_and_Exclusions','Excluded_and_Flagged_Spectra.csv'); rowsx=[]
for s in spots:
    if s['QC']!='PASS':
        dec={'FAIL':'FAIL','EXCLUDE':'EXCLUDED','REVIEW':'REVIEW (not in the reference)'}[s['QC']]; rowsx.append([s['new'],'bulk-lta/'+s['src'],'LTA',s['power'],f"{s['int_s']:.1f}",s['acc'],dec,s['why'],'LTA_Bulk'])
for i in range(1,9): rowsx.append(['(not copied)',f'bulk-lta/45sec-80p-2acc-diffrentspot/SP_{i}.csv','LTA',80,'45.0',2,'EXCLUDED - duplicate',f'Identical (MD5) to glass blank SP_{i}; not an LTA spectrum. The blank is in Glass_Blank/Glass_Blank_{DATE}_{COND}_S{i:02d}.csv','Not copied (identical file in Glass_Blank)'])
have={(r[0],r[1]) for r in csv.reader(open(ex,encoding='utf-8'))}
rowsx=[r for r in rowsx if (r[0],r[1]) not in have]
with open(ex,'a',newline='',encoding='utf-8') as f: csv.writer(f,lineterminator='\n').writerows(rowsx)
print('exclusion rows added:',len(rowsx))
# reference files
RD=os.path.join(LIB,'03_Reference_Spectra','LTA')
mem=[s['new'] for s in core]
head=[f'# LTA bulk powder on glass slide - REFERENCE v2 (28 Oct 2026; n = {len(core)} independent spots); supersedes the preliminary April 2026 reference (n = 4), which is kept unchanged as LTA_Bulk_Reference_Mean_SD.csv',
 '# Sample: LTA from Staphylococcus aureus, Sigma-Aldrich L2515-10MG, lot 0000419622, source number 0000404178 (purity not recorded)',
 '# Condition: 785 nm, 80 % laser power (instrument setting), 45 s, 2 accumulations; dark acquired with the shutter closed (dark median 1504-1512 counts); pipeline v3',
 '# Members: '+'; '.join(mem),
 f'# Representative spectrum = MEAN of normalised spectra (median agrees: r = {mm_r:.4f}); strict set (n = {len(core)}) vs extended set with marginal-ripple spots (n = {len(ext)}): r = {sens:.4f}. Absolute counts vary ~40x between spots (focus/packing); compare band ratios',
 '# Limitation: the glass contribution (marker file, glass_share_pct) is estimated from the 28 Sep glass template (exploratory); the glass blanks of 28 Oct show polystyrene-like bands (1000, 1030, 1602 cm-1) and are not used for that estimate']
with open(os.path.join(RD,f'LTA_Bulk_Reference_20261028_Mean_SD.csv'),'w',encoding='utf-8',newline='') as f:
    f.write('\n'.join(head)+'\nRaman_Shift_cm-1,BaselineCorrected_mean_counts,BaselineCorrected_median_counts,BaselineCorrected_SD_counts,DarkSubtracted_mean_counts,Normalised_mean,Normalised_median,Normalised_SD\n')
    for k in range(len(X)): f.write(f'{X[k]:.1f},{Mc[k]:.2f},{Medc[k]:.2f},{SDc[k]:.2f},{Dm[k]:.2f},{Nm[k]:.5f},{Nmed[k]:.5f},{Nsd[k]:.5f}\n')
members=pd.DataFrame([dict(library_file=s['new'],original_file='bulk-lta/'+s['src'],acq=s['acq'],spot=f"SP_{s['n']}",power_pct=s['power'],int_s=s['int_s'],acc=s['acc'],dark_med=round(s['dark'],1),raw_max=s['raw_max'],ripple=round(s['ripple'],2),noise=round(s['noise'],2),h1092=round(s['h1092'],1),snr1092=round(s['snr1092'],1),glass_ratio=round(s['glass_ratio'],2),r_core=round(s['r_core'],3),rLTA_April=round(s['rLTA'],3),rNAM=round(s['rNAM'],3),rLPS=round(s['rLPS'],3)) for s in core])
members.to_csv(os.path.join(RD,'LTA_Reference_20261028_Members.csv'),index=False,encoding='utf-8')
bands.round(3).to_csv(os.path.join(RD,'LTA_Reference_20261028_Marker_Peaks.csv'),index=False,encoding='utf-8')
# workbook
import openpyxl
from openpyxl.styles import PatternFill,Font
wbp=os.path.join(LIB,'05_Tables','Spectral_Library_Metadata_and_Peaks.xlsx'); wb=openpyxl.load_workbook(wbp)
def addsheet(name,df,widths=None):
    if name in wb.sheetnames: del wb[name]
    ws=wb.create_sheet(name); ws.append(list(df.columns))
    for c in ws[1]: c.fill=PatternFill('solid',fgColor='D9D9D9'); c.font=Font(bold=True)
    for r in df.itertuples(index=False): ws.append([None if (isinstance(v,float) and np.isnan(v)) else (v.item() if hasattr(v,'item') else v) for v in r])
    for i,col in enumerate(df.columns): ws.column_dimensions[openpyxl.utils.get_column_letter(i+1)].width=max(10,min(40,len(str(col))+4))
addsheet('43_LTA_Ref_Inventory',inv); addsheet('44_LTA_Ref_QC',qlog); addsheet('45_LTA_Ref_Bands',bands.round(3)); addsheet('46_LTA_Ref_Members',members)
stat=pd.DataFrame([['Status','ESTABLISHED, pending operator confirmation (28 Oct 2026)'],['Sample','LTA from Staphylococcus aureus, Sigma-Aldrich L2515-10MG, lot 0000419622, source number 0000404178 (purity not recorded)'],['Condition','785 nm, 80 % / 45 s / 2 acc, bulk powder on glass, shutter-closed dark'],['Reference set',f'n = {len(core)} independent spots (SP_'+', SP_'.join(str(s["n"]) for s in core)+')'],['Extended set',f'n = {len(ext)} (adds marginal-ripple spots); r to strict mean {sens:.3f}'],['Comparison',f'r to April LTA {cmp["LTA"]:.2f}; to LPS {cmp["LPS"]:.2f}; to NAM {cmp["NAM"]:.2f} (glass zone excluded)'],['Primary markers',', '.join(f'{r.band:.0f}' for r in bands.itertuples() if r._1.startswith('C1'))],['Supporting',', '.join(f'{r.band:.0f}' for r in bands.itertuples() if r._1.startswith('C2'))]],columns=['Item','Value'])
addsheet('47_LTA_Final_Status',stat); wb.save(wbp)
inv.to_csv(os.path.join(H,'lt4_inventory.csv'),index=False); print('library updated')
