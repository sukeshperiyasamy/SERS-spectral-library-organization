# LTA bulk re-acquisition 28 Oct 2026: figures L1-L5 (reads lt4_result.pkl)
import os,pickle,numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from lib2 import X,LIB
H=os.path.dirname(os.path.abspath(__file__)); R=pickle.load(open(os.path.join(H,'lt4_result.pkl'),'rb'))
OUT=os.path.join(LIB,'04_Figures','LTA_Reference_20261028'); os.makedirs(OUT,exist_ok=True)
plt.rcParams.update({'font.family':'Arial','font.size':9})
spots,blanks,core,ext=R['spots'],R['blanks'],R['core'],R['ext']; bands=R['bands']; GZ=(X>=1308)&(X<=1455)
QC={'PASS':'#2a7d46','REVIEW':'#e08e0b','EXCLUDE':'#7f7f7f','FAIL':'#c0392b'}
def sv(fig,n): fig.tight_layout(); fig.savefig(os.path.join(OUT,n),dpi=200); plt.close(fig)
# L1 dark-subtracted spectra by QC class
fig,ax=plt.subplots(figsize=(10,4.2))
for b in blanks: ax.plot(X,b['dsx'],color='#aaaaaa',lw=.7)
for q in ('FAIL','EXCLUDE','REVIEW','PASS'):
    for s in [s for s in spots if s['QC']==q]: ax.plot(X,s['dsx'],color=QC[q],lw=.6,alpha=.8)
for q,c in QC.items(): ax.plot([],[],color=c,label=f"{q} (n={sum(1 for s in spots if s['QC']==q)})")
ax.plot([],[],color='#aaaaaa',label='28 Oct blanks (n=8, polystyrene-like)'); ax.axvspan(1308,1455,color='#dddddd',alpha=.4)
ax.set_xlim(400,1800); ax.set_ylim(-500,20000); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('dark-subtracted counts'); ax.legend(frameon=False,fontsize=8,ncol=3); ax.spines[['top','right']].set_visible(False)
ax.set_title('LTA session 28 Oct 2026: every spectrum, coloured by QC class (axis cut at 20,000 counts)',loc='left',fontweight='bold',fontsize=9.5); sv(fig,'FigL1_All_Spectra_by_QC.png')
# L2 processed core spectra
fig,ax=plt.subplots(figsize=(10,4.2))
for s in spots:
    if s['n'] in core: ax.plot(X,s['corr'],color='#2a7d46',lw=.7,alpha=.55)
ax.plot(X,R['Mc'],color='k',lw=1.5,label='mean of the 10 reference spots'); ax.plot(X,R['BL'],color='#888888',lw=1.1,ls='--',label='28 Oct blank (mean of 8; polystyrene-like)')
ax.axvspan(1308,1455,color='#dddddd',alpha=.4); ax.set_xlim(400,1800); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('baseline-corrected counts'); ax.legend(frameon=False,fontsize=8); ax.spines[['top','right']].set_visible(False)
ax.set_title('Processed reference spots (pipeline v3) and the glass blank',loc='left',fontweight='bold',fontsize=9.5); sv(fig,'FigL2_Reference_Spots_Processed.png')
# L3 reference with classified bands
CC={'C1':'#1f4e79','C2':'#2e8b57','C3':'#888888','C4':'#b8860b'}
fig,ax=plt.subplots(figsize=(10,4.4)); k=X<=1800
ax.fill_between(X,R['Mc']-R['SDc'],R['Mc']+R['SDc'],color='#bfe3cd',alpha=.7,lw=0,label='mean ± SD'); ax.plot(X,R['Mc'],color='#1a9a5b',lw=1.4,label='mean (n = 10)'); ax.plot(X,R['Medc'],color='k',lw=.9,ls=':',label='median'); ax.plot(X,R['a_med']*R['GT'],color='#888888',lw=.9,ls='--',label='glass (28 Sep template, scaled to the median spot)')
ax.axvspan(1308,1455,color='#dddddd',alpha=.4)
for r in bands.itertuples():
    c=r._1[:2]
    if c in ('C1','C2') or (c=='C3' and r.detected.split('/')[0]!='0' and r.band in (798,1009)):
        j=int(np.argmin(abs(X-r.band))); ax.text(r.band,R['Mc'][j]+(R['SDc'][j] if True else 0)+60,f'{r.band:.0f}',rotation=90,ha='center',va='bottom',fontsize=8,color=CC[c])
ax.set_xlim(400,1800); ax.set_ylim(-300,3000); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('baseline-corrected counts'); ax.spines[['top','right']].set_visible(False)
from matplotlib.lines import Line2D
h=ax.get_legend_handles_labels(); ax.legend(h[0]+[Line2D([],[],c=CC[c],marker='s',ls='',label=l) for c,l in (('C1','C1 primary'),('C2','C2 supporting'),('C3','C3 glass/background'))],h[1]+['C1 primary','C2 supporting','C3 glass / background'],frameon=False,fontsize=7.5,ncol=2,loc='upper right')
ax.set_title('LTA bulk reference v2 (28 Oct 2026): mean, median, SD and classified bands',loc='left',fontweight='bold',fontsize=9.5); sv(fig,'FigL3_LTA_Reference_Bands.png')
# L4 comparison
import pandas as pd
def refspec(a):
    d=pd.read_csv(os.path.join(LIB,'03_Reference_Spectra',a,f'{a}_Bulk_Reference_Mean_SD.csv'),comment='#'); return np.interp(X,d.iloc[:,0].values,d['Normalised_mean'].values)
fig,ax=plt.subplots(figsize=(10,4.4)); off=0
for lab,y,c in (('LTA 28 Oct 2026 (n=10)',R['Nm'],'#1a9a5b'),('LTA 3 Apr 2026 (n=4)',refspec('LTA'),'#6bb98a'),('LPS reference',refspec('LPS'),'#b5421c'),('NAM reference',refspec('NAM'),'#1f5fa8')):
    ax.plot(X,y+off,color=c,lw=1.2); ax.text(1795,off+0.55,lab,ha='right',fontsize=8,color=c); off+=1.15
ax.axvspan(1308,1455,color='#dddddd',alpha=.4); ax.set_xlim(400,1800); ax.set_yticks([]); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.spines[['top','right','left']].set_visible(False)
cm=R['cmp']; ax.set_title(f"Normalised references: the new LTA matches April (r = {cm['LTA']:.2f}); LPS r = {cm['LPS']:.2f}, NAM r = {cm['NAM']:.2f}",loc='left',fontweight='bold',fontsize=9.5); sv(fig,'FigL4_LTA_vs_Other_References.png')
# L5 QC overview
fig,axs=plt.subplots(2,2,figsize=(10,6.2)); n=[s['n'] for s in spots]
axs[0,0].bar(n,[s['ripple'] for s in spots],color=[QC[s['QC']] for s in spots]); axs[0,0].axhline(50,color='k',ls='--',lw=.8); axs[0,0].set_title('Ripple per spot (limit 50)',fontsize=9,loc='left',fontweight='bold'); axs[0,0].set_ylabel('counts')
axs[0,1].bar(n,[s['raw_max'] for s in spots],color=[QC[s['QC']] for s in spots]); axs[0,1].axhline(65535,color='k',ls='--',lw=.8); axs[0,1].set_title('Highest raw count per spot (saturation 65,535)',fontsize=9,loc='left',fontweight='bold')
axs[1,0].bar(n,[s['snr1092'] for s in spots],color=[QC[s['QC']] for s in spots]); axs[1,0].axhline(10,color='k',ls='--',lw=.8); axs[1,0].set_title('SNR of the 1092 cm$^{-1}$ band (minimum 10)',fontsize=9,loc='left',fontweight='bold'); axs[1,0].set_xlabel('spot (SP_n)')
axs[1,1].scatter([np.sqrt(s['raw_med']) for s in spots],[s['ripple'] for s in spots],c=[QC[s['QC']] for s in spots],s=22); axs[1,1].scatter([np.sqrt(b['raw_med']) for b in blanks],[b['ripple'] for b in blanks],marker='s',c='#aaaaaa',s=22,label='28 Oct blanks'); axs[1,1].axhline(50,color='k',ls='--',lw=.8)
axs[1,1].set_xlabel('square root of the median raw count'); axs[1,1].set_ylabel('ripple (counts)'); axs[1,1].set_title('Ripple rises with signal in the spots; blanks sit apart',fontsize=9,loc='left',fontweight='bold'); axs[1,1].legend(frameon=False,fontsize=7.5)
for q,c in QC.items(): axs[0,0].bar([0],[0],color=c,label=q)
axs[0,0].legend(frameon=False,fontsize=7.5,ncol=2)
for a in axs.ravel(): a.spines[['top','right']].set_visible(False)
sv(fig,'FigL5_QC_Overview.png'); print(os.listdir(OUT))
