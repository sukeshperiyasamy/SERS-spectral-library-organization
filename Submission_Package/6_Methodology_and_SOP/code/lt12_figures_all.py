# LTA session 28 Oct 2026, all data: figures FigL1-L13 (reads lt11_result.pkl)
import os,pickle,numpy as np,pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D
from lib2 import X,LIB
H=os.path.dirname(os.path.abspath(__file__)); R=pickle.load(open(os.path.join(H,'lt11_result.pkl'),'rb'))
d,rec,PL,bands,ct,GT=R['d'],R['rec'],R['PL'],R['bands'],R['ct'],R['GT']; POOL=set(R['POOL'])
OUT=os.path.join(LIB,'04_Figures','LTA_Reference_20261028'); os.makedirs(OUT,exist_ok=True); plt.rcParams.update({'font.family':'Arial','font.size':9})
GZ=(X>=1308)&(X<=1455); QCC={'PASS':'#2a7d46','REVIEW':'#e08e0b','EXCLUDE':'#7f7f7f','FAIL':'#c0392b','FLAG-DARK':'#8e44ad'}
def sv(fig,n): fig.tight_layout(); fig.savefig(os.path.join(OUT,n),dpi=200); plt.close(fig)
sp=d[d.role=='spot'].copy(); ss=d[d.role=='samespot'].copy(); bl=d[(d.role=='blank')&(d.QC!='BLANK-SUSPECT')].copy()
d['t']=pd.to_datetime(d.acq); sp['t']=pd.to_datetime(sp.acq); ss['t']=pd.to_datetime(ss.acq)
# L1 all LTA spectra by QC class
fig,ax=plt.subplots(figsize=(10,4.4))
for q in ('FLAG-DARK','FAIL','EXCLUDE','REVIEW','PASS'):
    for r in sp[sp.QC==q].itertuples(): ax.plot(X,rec[r.rel]['dsx'],color=QCC[q],lw=.5,alpha=.7)
for q,c in QCC.items(): ax.plot([],[],color=c,label=f"{q} (n={int((sp.QC==q).sum())})")
ax.axvspan(1308,1455,color='#dddddd',alpha=.4); ax.set_xlim(400,1800); ax.set_ylim(-1000,22000); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('dark-subtracted counts (as recorded)'); ax.legend(frameon=False,fontsize=8,ncol=3); ax.spines[['top','right']].set_visible(False)
ax.set_title(f'All {len(sp)} independent LTA spots of 28 Oct 2026, coloured by QC class (axis cut at 22,000 counts)',loc='left',fontweight='bold',fontsize=9.5); sv(fig,'FigL1_All_Spectra_by_QC.png')
# L2 pooled reference spots
fig,ax=plt.subplots(figsize=(10,4.2)); mem=sp[sp.lib.isin(POOL)]
for r in mem.itertuples(): ax.plot(X,rec[r.rel]['corr'],color='#2a7d46' if r.int_s==45 else '#1f5fa8',lw=.6,alpha=.55)
ax.plot(X,PL['Mc'],color='k',lw=1.5,label=f'mean of {len(mem)} reference spots'); ax.plot([],[],color='#2a7d46',label='80 %, 45 s, 2 acc'); ax.plot([],[],color='#1f5fa8',label='80 %, 30 s, 3 acc')
ax.axvspan(1308,1455,color='#dddddd',alpha=.4); ax.set_xlim(400,1800); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('baseline-corrected counts'); ax.legend(frameon=False,fontsize=8); ax.spines[['top','right']].set_visible(False)
ax.set_title('Reference v2.1: the 17 passing spots of the two clean-dark conditions and their mean',loc='left',fontweight='bold',fontsize=9.5); sv(fig,'FigL2_Reference_Spots_Processed.png')
# L3 bands
CC={'C1':'#1f4e79','C2':'#2e8b57','C3':'#888888','C4':'#b8860b'}
fig,ax=plt.subplots(figsize=(10,4.4)); a_med=np.median([rec[r.rel]['glass_a'] for r in mem.itertuples()])
ax.fill_between(X,PL['Mc']-PL['SDc'],PL['Mc']+PL['SDc'],color='#bfe3cd',alpha=.7,lw=0); ax.plot(X,PL['Mc'],color='#1a9a5b',lw=1.4); ax.plot(X,PL['Medc'],color='k',lw=.9,ls=':'); ax.plot(X,a_med*GT,color='#888888',lw=.9,ls='--'); ax.axvspan(1308,1455,color='#dddddd',alpha=.4)
for r in bands.itertuples():
    c=r._1[:2]
    if c in('C1','C2'): j=int(np.argmin(abs(X-r.band))); ax.text(r.band,PL['Mc'][j]+PL['SDc'][j]+60,f'{r.band:.0f}',rotation=90,ha='center',va='bottom',fontsize=8,color=CC[c])
ax.set_xlim(400,1800); ax.set_ylim(-300,3000); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('baseline-corrected counts'); ax.spines[['top','right']].set_visible(False)
ax.legend([Line2D([],[],color='#1a9a5b',lw=1.4),Line2D([],[],color='k',ls=':'),Line2D([],[],color='#888888',ls='--'),Line2D([],[],c=CC['C1'],marker='s',ls=''),Line2D([],[],c=CC['C2'],marker='s',ls='')],['mean ± SD (n = 17)','median','glass shape (clean 80 %/30 s/3 blank, scaled)','C1 primary','C2 supporting'],frameon=False,fontsize=7.5,ncol=2,loc='upper right')
ax.set_title('LTA reference v2.1 (pooled, n = 17): mean, median, SD and classified bands',loc='left',fontweight='bold',fontsize=9.5); sv(fig,'FigL3_LTA_Reference_Bands.png')
# L4 comparison
def refspec(a,f=None):
    q=pd.read_csv(os.path.join(LIB,'03_Reference_Spectra',a,f or f'{a}_Bulk_Reference_Mean_SD.csv'),comment='#'); return np.interp(X,q.iloc[:,0].values,q['Normalised_mean'].values)
fig,ax=plt.subplots(figsize=(10,4.4)); off=0
for lab,y,c in ((f'LTA v2.1 pooled (n={len(mem)})',PL['Nm'],'#1a9a5b'),('LTA 3 Apr 2026 (n=4)',refspec('LTA'),'#6bb98a'),('LPS reference',refspec('LPS'),'#b5421c'),('NAM reference',refspec('NAM'),'#1f5fa8')):
    ax.plot(X,y+off,color=c,lw=1.2); ax.text(1795,off+0.55,lab,ha='right',fontsize=8,color=c); off+=1.15
ax.axvspan(1308,1455,color='#dddddd',alpha=.4); ax.set_xlim(400,1800); ax.set_yticks([]); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.spines[['top','right','left']].set_visible(False)
c=R['cmp']; rA=float(np.corrcoef(PL['Nm'][~GZ],refspec('LTA')[~GZ])[0,1]); ax.set_title(f"Normalised references: pooled LTA vs April LTA r = {rA:.2f}; vs LPS r = {c['r_pool_vs_LPS']:.2f}; vs NAM r = {c['r_pool_vs_NAM']:.2f}",loc='left',fontweight='bold',fontsize=9.5); sv(fig,'FigL4_LTA_vs_Other_References.png')
# L5 QC by condition (stacked)
fig,axs=plt.subplots(1,2,figsize=(10,3.8),gridspec_kw={'width_ratios':[1.5,1]})
lab=[f"{int(r.power)} %, {r.int_s:g} s, {int(r.acc)} acc" for r in ct.itertuples()]; bot=np.zeros(len(ct))
for q,col in (('PASS','PASS'),('REVIEW','REVIEW'),('EXCLUDE','EXCLUDE'),('FAIL','FAIL'),('FLAG_DARK','FLAG-DARK')):
    v=ct[q].values.astype(float); axs[0].barh(range(len(ct)),v,left=bot,color=QCC[col],label=col); bot+=v
axs[0].set_yticks(range(len(ct))); axs[0].set_yticklabels(lab,fontsize=7.5); axs[0].set_xlabel('independent spots'); axs[0].legend(frameon=False,fontsize=7.5,loc='lower right'); axs[0].set_title('QC outcome by condition',loc='left',fontweight='bold',fontsize=9.5)
cd=sp[~sp.leak]; g=cd.groupby(['power','int_s','acc']); pr=(g.QC.apply(lambda s:(s=='PASS').mean()*100)); axs[1].barh(range(len(pr)),pr.values,color='#2a7d46'); axs[1].set_yticks(range(len(pr))); axs[1].set_yticklabels([f"{int(a)} %, {b:g} s, {int(c)} acc (n={len(g.get_group((a,b,c)))})" for a,b,c in pr.index],fontsize=7.5); axs[1].set_xlim(0,100); axs[1].set_xlabel('% PASS (clean-dark spots only)'); axs[1].set_title('Pass rate with a clean dark',loc='left',fontweight='bold',fontsize=9.5)
for a in axs: a.spines[['top','right']].set_visible(False)
sv(fig,'FigL5_QC_Overview.png')
# L6 / L7 / L8 peaks
GRP={'phosphate':('#c0392b','Phosphodiester (PO$_2^-$)'),'backbone':('#1f5fa8','Glycerol / backbone skeleton'),'lipid':('#e08e0b','Lipid chain (CH$_2$)'),'ester':('#8e44ad','Ester C=O'),'unk':('#7f7f7f','Not assigned')}
PEAKS=[(419,'unk','skeletal'),(539,'backbone','skeletal'),(629,'unk',''),(723,'lipid','CH$_2$ rock'),(798,'phosphate','O-P-O / C-O-P'),(862,'backbone','C-C, C-O-C'),(1010,'unk',''),(1092,'phosphate','PO$_2^-$ sym.'),(1247,'phosphate','PO$_2^-$ asym.'),(1459,'lipid','CH$_2$ bend'),(1583,'unk',''),(1751,'ester','C=O')]
fig,ax=plt.subplots(figsize=(10,4.8)); Mc,SD=PL['Mc'],PL['SDc']
ax.fill_between(X,Mc-SD,Mc+SD,color='#cfe6d8',lw=0); ax.plot(X,Mc,color='#1a6b45',lw=1.4); ax.axvspan(1308,1455,color='#dddddd',alpha=.4); ax.text(1380,2750,'glass zone',ha='center',fontsize=7.5,color='#777777')
for p,gk,lb in PEAKS:
    j=int(np.argmin(abs(X-p))); top=Mc[j]+SD[j]; cc=GRP[gk][0]; ax.vlines(p,Mc[j],top+120,color=cc,lw=1.2); ax.text(p,top+160,f'{p}',rotation=90,ha='center',va='bottom',fontsize=8.5,color=cc,fontweight='bold')
    if lb: ax.text(p,-470,lb,rotation=90,ha='center',va='top',fontsize=6.8,color=cc)
for gk,(cc,l) in GRP.items(): ax.plot([],[],'s',color=cc,label=l)
ax.set_xlim(400,1800); ax.set_ylim(-1500,3000); ax.set_xlabel('Raman shift (cm$^{-1}$)',labelpad=2); ax.set_ylabel('baseline-corrected counts'); ax.legend(frameon=False,fontsize=8,ncol=3,loc='upper left'); ax.spines[['top','right']].set_visible(False)
ax.set_title('LTA reference v2.1: labelled peaks coloured by the part of the molecule they are consistent with (tentative)',loc='left',fontweight='bold',fontsize=9.5); sv(fig,'FigL6_LTA_Peaks_Annotated.png')
fig,axs=plt.subplots(3,3,figsize=(10,7)); sel=[539,723,798,862,1092,1247,1459,1751,419]; C=PL['C']
for ax,p in zip(axs.ravel(),sel):
    gk=[x for x in PEAKS if x[0]==p][0][1]; cc=GRP[gk][0]; m=(X>=p-45)&(X<=p+45)
    for y in C: ax.plot(X[m],y[m],color=cc,alpha=.2,lw=.7)
    ax.plot(X[m],Mc[m],color=cc,lw=1.6); ax.axvline(p,color=cc,ls=':',lw=.8); ax.set_title(f'{p} cm$^{{-1}}$',fontsize=9.5,color=cc,fontweight='bold'); ax.spines[['top','right']].set_visible(False); ax.tick_params(labelsize=7)
fig.suptitle(f'Each labelled band in the {len(C)} reference spots (thin lines) and their mean (thick line)',x=.01,ha='left',fontsize=9.5,fontweight='bold'); sv(fig,'FigL7_LTA_Peak_Zooms.png')
fig,ax=plt.subplots(figsize=(10,4.3)); ax.set_xlim(0,100); ax.set_ylim(0,44); ax.axis('off')
def box(x,y,w,hh,c,t,fs=9): ax.add_patch(FancyBboxPatch((x,y),w,hh,boxstyle='round,pad=0.3,rounding_size=1',fc=c,ec='#444444',lw=.8,alpha=.85)); ax.text(x+w/2,y+hh/2,t,ha='center',va='center',fontsize=fs,color='white',fontweight='bold')
box(2,22,16,12,'#e08e0b','lipid anchor\n(hydrophobic)')
for i,x in enumerate((26,48,70)):
    box(x,22,16,12,'#1f5fa8','glycerol\n(C-C-C)'); box(x+17.5,22,3.3,12,'#c0392b','P',9); ax.plot([x+16,x+17.5],[28,28],color='#444444',lw=1.2)
    if i<2: ax.plot([x+20.8,x+26],[28,28],color='#444444',lw=1.2)
    box(x+2,36.5,12,5,'#8e44ad','D-Ala / glycosyl',7.5); ax.plot([x+8,x+8],[34,36.5],color='#444444',lw=1)
ax.plot([18,26],[28,28],color='#444444',lw=1.2); ax.text(91,28,'... n repeats',fontsize=9,va='center'); ax.plot([86.8,90],[28,28],color='#444444',lw=1.2)
def note(x,t,cc,y=14): ax.text(x,y,t,ha='center',va='top',fontsize=8,color=cc,linespacing=1.4)
note(10,'1459, 723\nCH$_2$ of the\nlipid chains','#e08e0b'); note(34,'862, 539, 419\nglycerol skeleton\n(C-C, C-O-C, deformations)','#1f5fa8'); note(55.5,'1092, 1247, 798\nphosphodiester\nPO$_2^-$ and O-P-O','#c0392b'); note(80,'1751\nester C=O\n(D-alanyl, lipid)','#8e44ad')
ax.text(50,3,'Schematic of S. aureus LTA as described by the supplier: phosphodiester-linked glycerol phosphate bound to a lipid; C2 usually glycosylated and/or D-alanylated. Band assignments are tentative.',ha='center',fontsize=7.5,color='#444444')
ax.set_title('Where the bands are consistent with sitting in the LTA molecule',loc='left',fontweight='bold',fontsize=9.5); sv(fig,'FigL8_LTA_Structure_Map.png')
# L9 condition comparison (clean-dark spots)
cd=sp[~sp.leak].copy(); cd['cond']=[f"{int(r.power)} %, {r.int_s:g} s, {int(r.acc)} acc" for r in cd.itertuples()]
order=['80 %, 45 s, 2 acc','80 %, 30 s, 3 acc','70 %, 60 s, 2 acc','50 %, 40 s, 2 acc']; order=[o for o in order if o in set(cd.cond)]
fig,axs=plt.subplots(1,4,figsize=(10,3.4))
for ax,(col,lbl,fn) in zip(axs,(('raw_max','highest raw count',None),('ripple','ripple (counts)',50),('snr1092','SNR of 1092',10),('h1092','height of 1092 (counts)',None))):
    vals=[[rec[x][{'raw_max':'rawmax','ripple':'ripple','snr1092':'snr','h1092':'h1092'}[col]] for x in cd[cd.cond==o].rel] for o in order]
    ax.boxplot(vals,labels=[o.replace(', ','\n') for o in order],widths=.55); ax.set_title(lbl,fontsize=9,loc='left',fontweight='bold'); ax.tick_params(labelsize=6.5)
    if fn: ax.axhline(fn,color='k',ls='--',lw=.8)
    if col=='raw_max': ax.axhline(65535,color='k',ls='--',lw=.8)
    ax.spines[['top','right']].set_visible(False)
sv(fig,'FigL9_Condition_Comparison.png')
# L10 dark check
fig,axs=plt.subplots(1,2,figsize=(10,3.8),gridspec_kw={'width_ratios':[1.6,1]}); a=d[d.role!='blank'].copy(); a['t']=pd.to_datetime(a.acq)
a['dk']=[rec[r.rel]['dark'] for r in a.itertuples()]
cl=a[~a.leak]; lk=a[a.leak]; axs[0].scatter(cl.t,cl.dk,s=14,color='#2a7d46',label=f'clean dark (n={len(cl)})'); axs[0].scatter(lk.t,lk.dk,s=14,color='#8e44ad',label=f'dark with sample light (n={len(lk)})')
for v,t in ((1333,'30 s x 3'),(1510,'45 s x 2'),(1680,'60 s x 2')): axs[0].axhline(v,color='#999999',lw=.6,ls=':')
axs[0].set_yscale('log'); axs[0].set_ylabel('dark median (counts)'); axs[0].xaxis.set_major_formatter(md.DateFormatter('%H:%M')); axs[0].legend(frameon=False,fontsize=7.5); axs[0].set_title('Dark frame level of every spectrum through the day',loc='left',fontweight='bold',fontsize=9.5)
b=a[(a.int_s==45)&(a.acc==2)]; axs[1].scatter(b.apply(lambda r:rec[r.rel]['dark_excess'],axis=1).clip(lower=1),b.apply(lambda r:rec[r.rel]['snr'],axis=1),s=14,color='#1f5fa8'); axs[1].set_xscale('log'); axs[1].set_xlabel('dark excess over clean (counts, log)'); axs[1].set_ylabel('SNR of 1092'); axs[1].set_title('45 s x 2: signal vs dark excess',loc='left',fontweight='bold',fontsize=9.5)
for ax in axs: ax.spines[['top','right']].set_visible(False)
sv(fig,'FigL10_Dark_Check.png')
# L11 same-spot series
fig,axs=plt.subplots(1,2,figsize=(10,3.6)); ser=ss.groupby(['sub','power','int_s','acc'])
for (sub,pw,it,ac),g in ser:
    g=g.sort_values('t'); idx=np.arange(1,len(g)+1); h1=np.array([rec[x]['h1092'] for x in g.rel]); h2=np.array([hh for hh in (np.interp(0,[0],[0]) for _ in g.rel)])
    lab=f"{int(pw)} %, {it:g} s, {int(ac)} acc"+(' (dark leak)' if g.leak.any() else ''); ls='--' if g.leak.any() else '-'
    axs[0].plot(idx,h1/h1[0],ls,marker='o',ms=3,label=lab+f' [{sub.split("/")[-1][:14]}]')
    r1459=[ (lambda c:float(c[(X>=1453)&(X<=1465)].max()/c[(X>=1086)&(X<=1098)].max()))(rec[x]['corr']) for x in g.rel]; axs[1].plot(idx,r1459,ls,marker='o',ms=3)
axs[0].set_title('Height of 1092 relative to the first scan',loc='left',fontweight='bold',fontsize=9.5); axs[1].set_title('1459 / 1092 height ratio',loc='left',fontweight='bold',fontsize=9.5); axs[0].legend(frameon=False,fontsize=6.3); axs[0].set_xlabel('scan number on the same spot'); axs[1].set_xlabel('scan number on the same spot')
for a_ in axs: a_.spines[['top','right']].set_visible(False)
sv(fig,'FigL11_Same_Spot_Stability.png')
# L12 power series at 45 s x 2
ps=sp[(sp.int_s==45.0)&(sp.acc==2)].copy(); ps['h']=[rec[x]['h1092'] for x in ps.rel]; ps['raw']=[rec[x]['rawmax'] for x in ps.rel]
fig,axs=plt.subplots(1,2,figsize=(10,3.6))
for lk_,col,lab in ((True,'#8e44ad','dark with sample light'),(False,'#2a7d46','clean dark')):
    q=ps[ps.leak==lk_]; axs[0].scatter(q.power,q.h,s=16,color=col,label=lab); axs[1].scatter(q.power,q.raw,s=16,color=col)
axs[0].set_xlabel('laser power (%)'); axs[0].set_ylabel('height of 1092 (counts)'); axs[0].legend(frameon=False,fontsize=8); axs[0].set_title('Signal against power, 45 s x 2',loc='left',fontweight='bold',fontsize=9.5)
axs[1].set_xlabel('laser power (%)'); axs[1].set_ylabel('highest raw count'); axs[1].axhline(65535,color='k',ls='--',lw=.8); axs[1].set_title('Highest raw count',loc='left',fontweight='bold',fontsize=9.5)
for a_ in axs: a_.spines[['top','right']].set_visible(False)
sv(fig,'FigL12_Power_Series.png')
# L13 blanks
fig,ax=plt.subplots(figsize=(10,3.8)); gb=bl.copy()
for r in gb.itertuples():
    c=rec[r.rel]['corr']; col='#c0392b' if r.QC=='BLANK-SUSPECT' else ('#e08e0b' if r.QC=='BLANK-SATURATED' else '#2a7d46'); ax.plot(X,c/np.max(np.abs(c)),color=col,lw=.6,alpha=.7)
for q,col in (('BLANK-SUSPECT','#c0392b'),('BLANK-SATURATED','#e08e0b'),('BLANK-OK','#2a7d46')): ax.plot([],[],color=col,label=f"{q} (n={int((gb.QC==q).sum())})")
for p_ in (619,1000,1030,1602): ax.axvline(p_,color='#c0392b',ls=':',lw=.7)
ax.set_xlim(400,1800); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('baseline-corrected, scaled to the maximum'); ax.legend(frameon=False,fontsize=8); ax.spines[['top','right']].set_visible(False)
ax.set_title('The 11 glass blanks: saturated (orange) and clean (green); both match the 28 Sep glass',loc='left',fontweight='bold',fontsize=9.5); sv(fig,'FigL13_Blanks.png')
print(sorted(os.listdir(OUT)))
