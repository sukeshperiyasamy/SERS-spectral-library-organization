"""Analysis of the 7 Oct 2026 SERS spectra (E:\\sukesh\\10-oct-2026): NAM, LPS and LTA on etched silicon.

Reads the raw files (never modifies them), processes them with the library's pipeline v3 (lib2.py),
tests the target bands against the substrate blank and a bare-silicon reference, and writes the tables,
figures and results.json used by build_report.py.
"""
import os,re,sys,json,glob,warnings,collections
warnings.filterwarnings('ignore')
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.abspath(os.path.join(HERE,'..'))
REPO=os.path.abspath(os.path.join(OUT,'..'))
sys.path.insert(0,os.path.join(REPO,'SERS_Sepsis_Spectral_Library','08_Methodology','code'))
import numpy as np,pandas as pd,lib2
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.stats import mannwhitneyu
RAW=os.environ.get('OCT_RAW',r"E:\sukes h\10-oct-2026".replace(' ',''))
BARE=os.path.join(REPO,'5-6-2026','pure silicone 10s-20p-3ac multispot')
LIBREF=os.path.join(REPO,'SERS_Sepsis_Spectral_Library','03_Reference_Spectra')
FIG=r'C:/Users/sukes/AppData/Local/Temp/claude/C--Users-sukes-Downloads-sukesh/f9c0734c-e0bb-4f52-a4e5-d9f33e9bce00/scratchpad/sersfinal/figures'; TAB=r'C:/Users/sukes/AppData/Local/Temp/claude/C--Users-sukes-Downloads-sukesh/f9c0734c-e0bb-4f52-a4e5-d9f33e9bce00/scratchpad/sersfinal/tables'; os.makedirs(FIG,exist_ok=True); os.makedirs(TAB,exist_ok=True)
X=np.arange(400,1801,1.0); rng=np.random.default_rng(11)
plt.rcParams.update({'font.family':'Arial','font.size':9})
COL={'blank':'#555555','NAM':'#1f5fa8','LPS':'#b5421c','LTA':'#2a7d46','bare':'#999999'}
def natkey(s): return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)',s)]
def load(folder,label):
    out=[]
    for f in sorted(os.listdir(folder),key=natkey):
        if not f.lower().endswith('.csv'): continue
        meta,rs,dk,raw,ds=lib2.read_any(os.path.join(folder,f))
        if len(rs)==0: continue
        pr=lib2.process_v3h(rs,ds,raw)
        corr=np.interp(X,pr['x'],pr['corr']); w=(X>=505)&(X<=535); i=np.argmax(corr[w])
        t=pd.to_datetime(meta.get('Date',''),errors='coerce')
        out.append(dict(group=label,file=f,time=t,power=int(float(meta['laser_powerlevel'])),it=float(meta['integration times(sec)']),acc=int(float(meta['average number'])),
                        corr=corr,noise=float(pr['noise']),si=float(corr[w][i]),sipos=float(X[w][i]),
                        spk640=float(ds[640]-0.5*(ds[639]+ds[641])),spk700=float(ds[700]-0.5*(ds[699]+ds[701])),rawmax=float(raw[(rs>=400)&(rs<=1800)].max())))
    return out
spec=[]
spec+=load(os.path.join(RAW,'blank-5mlhf-45-di-6mgagno3','blank'),'blank')
spec+=load(os.path.join(RAW,'blank-5mlhf-45-di-6mgagno3','nam-1'),'nam-1')
spec+=load(os.path.join(RAW,'blank-5mlhf-45-di-6mgagno3','nam-2'),'nam-2')
spec+=load(os.path.join(RAW,'lps','lps2'),'lps2')
spec+=load(os.path.join(RAW,'lps','lps1'),'lps1')
spec+=load(os.path.join(RAW,'lta','lta2'),'lta2')
bare=load(BARE,'bare') if os.path.isdir(BARE) else []
for s in spec+bare: s['mol']={'blank':'blank','nam-1':'NAM','nam-2':'NAM','lps1':'LPS','lps2':'LPS','lta2':'LTA','bare':'bare'}[s['group']]
def peaks(s):
    p,pr=find_peaks(s['corr'],prominence=3*s['noise'],width=3); return X[p],pr['prominences']/s['noise']
for s in spec+bare: s['pk'],s['snr']=peaks(s)
M={m:[s for s in spec if s['mol']==m] for m in ('blank','NAM','LPS','LTA')}
def det(s,pos,tol=5.0):
    ok=[(q,a) for q,a in zip(s['pk'],s['snr']) if abs(q-pos)<=tol]; return (True,max(a for _,a in ok)) if ok else (False,0.0)
def height(s,pos,tol=5.0):
    w=(X>=pos-tol)&(X<=pos+tol); return float(s['corr'][w].max())
T={'NAM':[('541',541.0),('829',829.0),('870.5',870.5),('929',929.0),('955',955.0),('1023',1022.7),('1127',1127.0)],
   'LPS':[('425',424.8),('766',765.5),('861',861.1),('989',989.0),('997',995.8),('1080',1080.5),('1330',1330.0)],
   'LTA':[('802',802.2),('861.5',861.5),('1092',1091.8),('1131',1131.0),('1225-1250',1237.5),('1450',1450.0),('1459',1458.8)]}
SRC={'NAM':'bulk NAM reference','LPS':'bulk LPS reference (425, 766, 861, 997, 1080); 989 and 1330 from the SERS literature rule','LTA':'bulk LTA reference (802, 861.5, 1092, 1459); 1131, 1225-1250 and 1450 from the SERS rule'}
rows=[]
for mol,targets in T.items():
    for lab,pos in targets:
        a=M[mol]; b=M['blank']
        ra=[height(s,pos)/s['si'] for s in a]; rb=[height(s,pos)/s['si'] for s in b]
        try: p=mannwhitneyu(ra,rb,alternative='greater').pvalue
        except Exception: p=np.nan
        rows.append(dict(molecule=mol,band=lab,position=pos,detected_sample=sum(det(s,pos)[0] for s in a),n_sample=len(a),detected_blank=sum(det(s,pos)[0] for s in b),n_blank=len(b),
                         detected_bare_Si=sum(det(s,pos)[0] for s in bare),n_bare_Si=len(bare),median_snr_when_detected=float(np.median([det(s,pos)[1] for s in a if det(s,pos)[0]])) if any(det(s,pos)[0] for s in a) else 0.0,
                         median_height_over_Si_sample=float(np.median(ra)),median_height_over_Si_blank=float(np.median(rb)),p_greater_than_blank=float(p)))
bands=pd.DataFrame(rows)
# chance test
chance={}
for mol,targets in T.items():
    a=M[mol]; real=float(np.mean([[det(s,pos)[0] for s in a] for _,pos in targets])); sims=[]
    for _ in range(400):
        sh=rng.uniform(20,80)*rng.choice([-1,1]); sims.append(np.mean([[det(s,pos+sh)[0] for s in a] for _,pos in targets]))
    chance[mol]=dict(real=real,mean=float(np.mean(sims)),sd=float(np.std(sims)),p=float(np.mean(np.array(sims)>=real)),sims=[float(v) for v in sims])
# reproducible band set in the LPS session (found by clustering peaks absent from blank and bare Si)
def catalogue(ss,tol=4):
    allp=sorted(q for s in ss for q in s['pk']); cl=[]
    for p in allp:
        if cl and p-cl[-1][-1]<=tol: cl[-1].append(p)
        else: cl.append([p])
    return [float(np.mean(c)) for c in cl]
def frac(ss,pos,tol=4): return float(np.mean([any(abs(q-pos)<=tol for q in s['pk']) for s in ss])) if ss else float('nan')
cands=[(p,frac(M['LPS'],p)) for p in catalogue(M['LPS'])]
PAT_POS=[619,785,878,1009,1238,1330,1368,1455,1536,1592]
def npat(s): return sum(any(abs(q-t)<=5 for q in s['pk']) for t in PAT_POS)
for s in spec+bare: s['npat']=npat(s)
carry=[s for s in M['LPS'] if s['npat']>=5]; nocarry=[s for s in M['LPS'] if s['npat']<5]
LITMAP={1330:'1330 and 1333 in the SERS LPS lists (LPS-1, LPS-2)',1455:'1450, CH2/CH3 deformation (LPS-1, SERS); 5 cm-1 above',1009:'988 (LPS-1) and 1003 (LPS-2); 6 to 21 cm-1 away'}
prow=[]
for t in PAT_POS:
    pos=[q for s in carry for q in s['pk'] if abs(q-t)<=5]
    prow.append(dict(band=t,mean_position=float(np.mean(pos)),sd_position=float(np.std(pos)),fraction_all_LPS=frac(M['LPS'],t,5),fraction_carrying=frac(carry,t,5),fraction_other_LPS=frac(nocarry,t,5),fraction_blank=frac(M['blank'],t,5),fraction_bare_Si=frac(bare,t,5),fraction_NAM=frac(M['NAM'],t,5),fraction_LTA=frac(M['LTA'],t,5),
                     median_snr_carrying=float(np.median([max(a for q,a in zip(s['pk'],s['snr']) if abs(q-t)<=5) for s in carry if any(abs(q-t)<=5 for q in s['pk'])])),literature=LITMAP.get(t,'no match in the checked LPS list')))
pat=pd.DataFrame(prow)
# reproducibility and similarity
def pr(ss,lo=560,hi=1800):
    m=(X>=lo)&(X<=hi); A=np.array([s['corr'][m]/s['si'] for s in ss]); C=np.corrcoef(A); iu=np.triu_indices(len(ss),1); return C[iu]
repro=dict(carrying_median_r=float(np.median(pr(carry))),other_LPS_median_r=float(np.median(pr(nocarry))),NAM_median_r=float(np.median(pr(M['NAM']))),blank_median_r=float(np.median(pr(M['blank']))))
meanc=np.mean([s['corr']/s['si'] for s in carry],axis=0); Gm=~((X>=1308)&(X<=1455))&~((X>=480)&(X<=560))
def ref(a):
    r=pd.read_csv(os.path.join(LIBREF,a,f'{a}_Bulk_Reference_Mean_SD.csv'),comment='#'); return np.interp(X,r.iloc[:,0].values,r['Normalised_mean'].values)
sim={a:float(np.corrcoef(meanc[Gm],ref(a)[Gm])[0,1]) for a in ('NAM','LPS','LTA')}
# per-spectrum and per-condition tables
ps=pd.DataFrame([dict(group=s['group'],file=s['file'],time=str(s['time']),power_pct=s['power'],integration_s=s['it'],accumulations=s['acc'],Si_520_height_counts=round(s['si'],1),Si_position=s['sipos'],noise_counts=round(s['noise'],1),raw_max_counts=s['rawmax'],
                      peaks_outside_Si=int(sum(1 for q in s['pk'] if not any(abs(q-t)<=8 for t in (518,935,940)))),LPS_pattern_bands_of_10=s['npat'],LPS_pattern_present=bool(s in carry)) for s in spec])
ps.to_csv(os.path.join(TAB,'per_spectrum_summary.csv'),index=False,encoding='utf-8-sig')
bands.round(4).to_csv(os.path.join(TAB,'target_band_detection.csv'),index=False,encoding='utf-8-sig')
pat.round(4).to_csv(os.path.join(TAB,'lps_session_reproducible_bands.csv'),index=False,encoding='utf-8-sig')
cond=ps.groupby(['group','power_pct','integration_s','accumulations']).agg(n=('file','count'),Si_median=('Si_520_height_counts','median'),noise_median=('noise_counts','median'),raw_max=('raw_max_counts','max'),with_peaks_outside_Si=('peaks_outside_Si',lambda v:int((v>0).sum()))).reset_index()
cond.to_csv(os.path.join(TAB,'per_condition_summary.csv'),index=False,encoding='utf-8-sig')
art=dict(spk640={m:float(np.median([s['spk640'] for s in M[m]])) for m in M},spk700={m:float(np.median([s['spk700'] for s in M[m]])) for m in M},spk640_noise=float(np.median([s['noise'] for s in spec])))
res=dict(n={m:len(v) for m,v in M.items()},n_bare=len(bare),chance={m:{k:v for k,v in c.items() if k!='sims'} for m,c in chance.items()},repro=repro,sim=sim,n_carry=len(carry),n_lps=len(M['LPS']),
         si_carry=float(np.median([s['si'] for s in carry])),si_nocarry=float(np.median([s['si'] for s in nocarry])),art=art,
         t0=str(min(s['time'] for s in spec)),t1=str(max(s['time'] for s in spec)),
         group_span={g:[str(min(s['time'] for s in spec if s['group']==g)),str(max(s['time'] for s in spec if s['group']==g))] for g in ('blank','nam-1','nam-2','lps2','lps1','lta2')},
         si_pos=float(np.median([s['sipos'] for s in spec])),carry_files=[s['group']+'/'+s['file'] for s in carry],
         nam_scatter=[dict(file=s['file'],group=s['group'],peaks=[int(round(q)) for q,a in zip(s['pk'],s['snr']) if not any(abs(q-t)<=8 for t in (518,935,940))]) for s in M['NAM']])
json.dump(res,open(os.path.join(TAB,'results.json'),'w'),indent=1)
# ================= figures
def savefig(fig,name): fig.tight_layout(); fig.savefig(os.path.join(FIG,name),dpi=200); plt.close(fig)
# F1 timeline
fig,ax=plt.subplots(figsize=(10,3.6)); GC={'blank':COL['blank'],'nam-1':COL['NAM'],'nam-2':'#6c9bd2','lps2':COL['LPS'],'lps1':'#d9825f','lta2':COL['LTA']}
for g,c in GC.items():
    ss=[s for s in spec if s['group']==g]; ax.plot([s['time'] for s in ss],[s['si'] for s in ss],'o',color=c,ms=4,label=f'{g} (n={len(ss)})')
ax.set_yscale('log'); ax.set_ylabel('Si 520 band height (counts)'); ax.set_xlabel('Time of day (hours)'); ax.legend(frameon=False,fontsize=7.5,ncol=3); ax.spines[['top','right']].set_visible(False)
ax.set_title('Silicon band height through the session (every spectrum)',loc='left',fontweight='bold',fontsize=9.5); import matplotlib.dates as md; ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
savefig(fig,'F1_session_timeline.png')
# F2 mean spectra per molecule vs blank and bare Si
fig,axs=plt.subplots(3,1,figsize=(10,8.5),sharex=True)
mb=np.mean([s['corr']/s['si'] for s in M['blank']],axis=0); mbare=np.mean([s['corr']/s['si'] for s in bare],axis=0) if bare else None
for ax,mol in zip(axs,('NAM','LPS','LTA')):
    ss=M[mol];
    if mol=='LPS':
        ax.plot(X,meanc,color=COL[mol],lw=1.3,label=f'LPS spots with the reproducible band set (n={len(carry)})'); mo=np.mean([s['corr']/s['si'] for s in nocarry],axis=0); ax.plot(X,mo,color='#d9a08a',lw=1,label=f'LPS spots without it (n={len(nocarry)})')
    else: ax.plot(X,np.mean([s['corr']/s['si'] for s in ss],axis=0),color=COL[mol],lw=1.3,label=f'{mol} mean (n={len(ss)})')
    ax.plot(X,mb,color=COL['blank'],lw=1,label='substrate blank (n=5)')
    if mbare is not None: ax.plot(X,mbare,color=COL['bare'],lw=0.9,ls='--',label='bare silicon (n=%d)'%len(bare))
    for lab,pos in T[mol]: ax.axvline(pos,color='#c0392b',ls=':',lw=.8); ax.text(pos,ax.get_ylim()[1]*0.02,lab,rotation=90,fontsize=6.5,color='#c0392b',va='bottom',ha='right')
    ax.set_ylim(-0.35,1.1); ax.set_ylabel('counts / Si 520 height'); ax.legend(frameon=False,fontsize=7,loc='upper right'); ax.spines[['top','right']].set_visible(False)
    ax.set_title(f'{mol}: mean spectrum with the {mol} target bands (red dotted)',loc='left',fontsize=9,fontweight='bold')
axs[-1].set_xlabel('Raman shift (cm$^{-1}$)'); axs[-1].set_xlim(400,1800)
savefig(fig,'F2_mean_spectra_vs_blank.png')
# F3 LPS individual spectra stack
fig,ax=plt.subplots(figsize=(10,6.2)); show=[s for s in carry][:8]; off=0
for s in show:
    y=s['corr']/s['si']; ax.plot(X,y+off,color=COL['LPS'],lw=.9); ax.text(1795,off+0.05,f"{s['group']}/{s['file'][:-4]}",fontsize=6.5,ha='right'); off+=0.55
for s in [s for s in nocarry][:2]: ax.plot(X,s['corr']/s['si']+off,color='#d9a08a',lw=.9); ax.text(1795,off+0.05,f"{s['group']}/{s['file'][:-4]} (no pattern)",fontsize=6.5,ha='right'); off+=0.55
ax.plot(X,mb+off,color=COL['blank'],lw=.9); ax.text(1795,off+0.05,'substrate blank (mean)',fontsize=6.5,ha='right')
for t in PAT_POS: ax.axvline(t,color='#999999',ls=':',lw=.7); ax.text(t,off+0.75,str(t),rotation=90,fontsize=7,ha='center',va='bottom')
ax.set_xlim(400,1800); ax.set_ylim(-0.3,off+1.2); ax.set_yticks([]); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.spines[['top','right','left']].set_visible(False)
ax.set_title('LPS session: individual spectra with the reproducible band set (dotted lines), a spot without it, and the blank',loc='left',fontweight='bold',fontsize=9.5)
savefig(fig,'F3_LPS_individual_spectra.png')
# F4 detection of target bands
fig,axs=plt.subplots(1,3,figsize=(10,3.6))
for ax,mol in zip(axs,('NAM','LPS','LTA')):
    b=bands[bands.molecule==mol]; xs=np.arange(len(b)); ax.bar(xs-0.2,b.detected_sample/b.n_sample,0.4,color=COL[mol],label=f'{mol} spectra (n={M[mol].__len__()})'); ax.bar(xs+0.2,b.detected_blank/b.n_blank,0.4,color=COL['blank'],label='blank (n=5)')
    ax.set_xticks(xs); ax.set_xticklabels(b.band,rotation=45,fontsize=7.5); ax.set_ylim(0,1); ax.set_title(mol,fontsize=9.5,fontweight='bold'); ax.legend(frameon=False,fontsize=7); ax.spines[['top','right']].set_visible(False)
axs[0].set_ylabel('fraction of spectra with the band')
savefig(fig,'F4_target_band_detection.png')
# F5 chance test
fig,axs=plt.subplots(1,3,figsize=(10,3))
for ax,mol in zip(axs,('NAM','LPS','LTA')):
    ax.hist(chance[mol]['sims'],bins=20,color='#bbbbbb'); ax.axvline(chance[mol]['real'],color=COL[mol],lw=2.5,label='real target positions'); ax.set_title(f"{mol} (p = {chance[mol]['p']:.2f})",fontsize=9); ax.set_xlabel('mean detection fraction'); ax.legend(frameon=False,fontsize=7.5); ax.spines[['top','right']].set_visible(False)
axs[0].set_ylabel('random shifts (400)')
savefig(fig,'F5_chance_test.png')
# F6 pattern bands bar chart
fig,ax=plt.subplots(figsize=(10,3.6)); xs=np.arange(len(pat)); w=0.15
for k,(col,lab,c) in enumerate([('fraction_carrying','LPS spots with the set',COL['LPS']),('fraction_other_LPS','other LPS spots','#d9a08a'),('fraction_NAM','NAM spectra',COL['NAM']),('fraction_LTA','LTA spectra',COL['LTA']),('fraction_blank','blank',COL['blank']),('fraction_bare_Si','bare silicon','#bbbbbb')]):
    ax.bar(xs+(k-2.5)*w,pat[col],w,color=c,label=lab)
ax.set_xticks(xs); ax.set_xticklabels([f"{int(round(v))}" for v in pat.mean_position]); ax.set_xlabel('band position (cm$^{-1}$)'); ax.set_ylabel('fraction of spectra'); ax.legend(frameon=False,fontsize=7,ncol=3); ax.spines[['top','right']].set_visible(False)
ax.set_title('How often each LPS-session band appears in each group',loc='left',fontweight='bold',fontsize=9.5)
savefig(fig,'F6_LPS_session_band_set.png')
# F7 zoom for key LPS bands
fig,axs=plt.subplots(1,4,figsize=(10,2.8))
for ax,(c,w_) in zip(axs,[(1330,45),(1455,45),(1009,45),(1238,45)]):
    m=(X>=c-w_)&(X<=c+w_)
    for s in carry: ax.plot(X[m],s['corr'][m]/s['si'],color=COL['LPS'],alpha=.25,lw=.6)
    ax.plot(X[m],meanc[m],color=COL['LPS'],lw=1.4,label='mean, spots with set'); ax.plot(X[m],mb[m],color=COL['blank'],lw=1.2,label='blank mean'); ax.set_title(f'{c} cm$^{{-1}}$',fontsize=9); ax.spines[['top','right']].set_visible(False)
axs[0].legend(frameon=False,fontsize=6.5); axs[0].set_ylabel('counts / Si 520')
savefig(fig,'F7_LPS_band_zooms.png')
# F8 NAM: selected spectra vs bulk bands
fig,ax=plt.subplots(figsize=(10,4.2)); sel=sorted(M['NAM'],key=lambda s:-sum(1 for q,a in zip(s['pk'],s['snr']) if not any(abs(q-t)<=8 for t in (518,935,940))))[:5]; off=0
for s in sel: ax.plot(X,s['corr']/s['si']+off,color=COL['NAM'],lw=.9); ax.text(1795,off+0.05,f"{s['group']}/{s['file'][:-4]} ({s['power']} %, {s['it']:g} s)",fontsize=6.5,ha='right'); off+=0.45
ax.plot(X,mb+off,color=COL['blank'],lw=.9); ax.text(1795,off+0.05,'substrate blank (mean)',fontsize=6.5,ha='right')
for lab,pos in T['NAM']: ax.axvline(pos,color='#c0392b',ls=':',lw=.8); ax.text(pos,off+0.55,lab,rotation=90,fontsize=7,ha='center',va='bottom',color='#c0392b')
ax.set_xlim(400,1800); ax.set_ylim(-0.3,off+1.1); ax.set_yticks([]); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.spines[['top','right','left']].set_visible(False)
ax.set_title('NAM: the five spectra with the most extra peaks, against the NAM bulk bands (red dotted)',loc='left',fontweight='bold',fontsize=9.5)
savefig(fig,'F8_NAM_best_spectra.png')
print('done',json.dumps({k:res[k] for k in ('n','n_bare','chance','repro','sim','n_carry','si_carry','si_nocarry','art')},indent=1))
print(bands.round(3).to_string()); print(pat.round(3).to_string())
