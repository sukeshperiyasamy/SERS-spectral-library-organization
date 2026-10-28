"""Figures for the nine final reports. Coloured curves on white; no dates, file names or version labels in titles, legends or captions."""
import os,io,glob,numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import fr_data as D,fr_struct as S
plt.rcParams.update({'font.family':'Arial','font.size':9.5,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white'})
FIG=r"C:\Users\sukes\AppData\Local\Temp\claude\C--Users-sukes-Downloads-sukesh\f9c0734c-e0bb-4f52-a4e5-d9f33e9bce00\scratchpad\figs"; os.makedirs(FIG,exist_ok=True)
ST={'agrees':'#2e8b57','shifted':'#e08a00','none':'#8a8a8a'}
STL={'agrees':'agrees (within 10 cm$^{-1}$)','shifted':'shifted, same vibration type','none':'no counterpart of that type'}
def glass(ax,lab=True):
    ax.axvspan(*D.GLASS,color='#d0d0d0',alpha=.55,lw=0)
    if lab: ax.text(sum(D.GLASS)/2,ax.get_ylim()[1]*0.97,'glass band zone',ha='center',va='top',fontsize=7.5,color='#555')
def label_peaks(ax,pk,col,y0=1.02,step=None):
    pk=sorted(pk); last=-1e9; lvl=0
    for p in pk:
        lvl=(lvl+1)%2 if p-last<45 else 0
        ax.text(p,y0+0.07*lvl,f'{p:.0f}',ha='center',va='bottom',fontsize=8,color=col,rotation=0); ax.plot([p,p],[y0-0.02,y0+0.03*0],color=col,lw=0.8); last=p
def save(fig,name): p=os.path.join(FIG,name); fig.savefig(p,dpi=200,bbox_inches='tight'); plt.close(fig); return p
# ------------------------------------------------------------------ experimental bulk
def bulk_full(m):
    mem=D.exp_members(m); mean,sd,_=D.exp_ref(m); pk=[p for p,_ in D.peaks(m)]; c=D.COL[m]
    fig,ax=plt.subplots(figsize=(9,4.2))
    for y in mem: ax.plot(D.X,y,color=c,alpha=.18,lw=.7)
    ax.fill_between(D.X,np.clip(mean-sd,0,None),mean+sd,color=c,alpha=.25,lw=0,label='mean ± 1 standard deviation')
    ax.plot(D.X,mean,color=c,lw=1.8,label=f'mean of {len(mem)} spectra')
    ax.set_xlim(400,1800); ax.set_ylim(0,1.28); glass(ax)
    label_peaks(ax,pk,c,y0=1.0)
    ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('Normalised intensity (0 to 1)'); ax.legend(frameon=False,loc='upper left',fontsize=8)
    ax.set_title(f'Experimental bulk Raman spectrum of {D.NAME[m]}: individual spectra and their mean',loc='left',fontweight='bold',fontsize=10)
    return save(fig,f'{m}_bulk_full.png'),len(mem)
def bulk_processing(m):
    mem=pd.read_csv(D.LIB+'/'+D.MEMBERS[m]); f=mem.library_file.iloc[len(mem)//2]; p=D.find_proc(f); d=D.read_proc(p); x=d['Raman_Shift_cm-1'].values; c=D.COL[m]
    fig,(a1,a2)=plt.subplots(2,1,figsize=(9,5.6),sharex=True)
    a1.plot(x,d['DarkSubtracted_counts'],color='#9a9a9a',lw=.8,label='measured signal (background-subtracted)'); a1.plot(x,d['Smoothed_counts'],color=c,lw=1.4,label='after spike removal and smoothing'); a1.plot(x,d['Baseline_counts'],color='#222',ls='--',lw=1.2,label='estimated slowly varying background')
    a1.set_ylabel('Signal (counts)'); a1.legend(frameon=False,fontsize=8,loc='upper right'); a1.set_title('Processing of one measured spectrum',loc='left',fontweight='bold',fontsize=10); a1.set_xlim(400,1800)
    a2.plot(x,d['BaselineCorrected_counts'],color=c,lw=1.4,label='after background (baseline) removal'); a2.axvspan(*D.GLASS,color='#d0d0d0',alpha=.55,lw=0)
    a2.set_ylabel('Signal (counts)'); a2.set_xlabel('Raman shift (cm$^{-1}$)'); a2.legend(frameon=False,fontsize=8,loc='upper right')
    return save(fig,f'{m}_bulk_processing.png')
def bulk_zoom(m,wins):
    mem=D.exp_members(m); mean,sd,_=D.exp_ref(m); pk=[p for p,_ in D.peaks(m)]; c=D.COL[m]; n=len(wins)
    fig,axs=plt.subplots(1,n,figsize=(3.2*n+0.4,3.3))
    for ax,(a,b) in zip(np.atleast_1d(axs),wins):
        k=(D.X>=a)&(D.X<=b)
        for y in mem: ax.plot(D.X[k],y[k],color=c,alpha=.18,lw=.7)
        ax.fill_between(D.X[k],np.clip(mean-sd,0,None)[k],(mean+sd)[k],color=c,alpha=.25,lw=0); ax.plot(D.X[k],mean[k],color=c,lw=1.8)
        top=(mean+sd)[k].max()*1.25; ax.set_ylim(0,top); ax.set_xlim(a,b)
        for p in pk:
            if a<=p<=b: i=np.argmin(abs(D.X-p)); ax.annotate(f'{p:.0f}',(p,mean[i]),xytext=(0,14),textcoords='offset points',ha='center',fontsize=8.5,arrowprops=dict(arrowstyle='-',color='#444',lw=.7))
        ax.set_xlabel('Raman shift (cm$^{-1}$)',fontsize=8.5)
    np.atleast_1d(axs)[0].set_ylabel('Normalised intensity'); fig.suptitle(f'Close-up of the main peaks of {D.NAME[m]}',x=0.01,ha='left',fontweight='bold',fontsize=10)
    fig.tight_layout(); return save(fig,f'{m}_bulk_zoom.png')
def bulk_glass(m):
    mean,sd,cnt=D.exp_ref(m); bn,bc,nb=D.blank_mean(m); c=D.COL[m]; pk=[p for p,_ in D.peaks(m)]; short=D.NAME[m].split(" (")[0]
    if m=='NAM':
        fig,a2=plt.subplots(1,1,figsize=(9,3.6))
    else:
        fig,(a1,a2)=plt.subplots(2,1,figsize=(9,5.6),sharex=True)
        a1.plot(D.X,cnt,color=c,lw=1.6,label=f'bulk {short} (mean)'); a1.plot(D.X,bc,color='#555',lw=1.4,label='glass blank, same settings')
        a1.axvspan(*D.GLASS,color='#d0d0d0',alpha=.5,lw=0); a1.set_ylabel('Signal (counts)'); a1.legend(frameon=False,fontsize=8,loc='upper right'); a1.set_title('Bulk sample compared with the glass blank, same instrument settings',loc='left',fontweight='bold',fontsize=10)
    a2.plot(D.X,mean,color=c,lw=1.6,label='sample (normalised)'); a2.plot(D.X,bn,color='#555',lw=1.2,label='glass blank (normalised to its own maximum)')
    a2.axvspan(*D.GLASS,color='#d0d0d0',alpha=.5,lw=0); a2.set_xlim(400,1800); a2.set_ylim(0,1.1); a2.set_ylabel('Normalised intensity'); a2.set_xlabel('Raman shift (cm$^{-1}$)'); a2.legend(frameon=False,fontsize=8,loc='upper left')
    if m=='NAM': a2.set_title('Bulk sample compared with the glass blank',loc='left',fontweight='bold',fontsize=10)
    for p in pk: a2.axvline(p,color=c,ls=':',lw=.8,alpha=.7)
    return save(fig,f'{m}_bulk_glass.png')
def bulk_select(m):
    fig,axs=plt.subplots(1,3,figsize=(10,3.3)); c=D.COL[m]
    if m=='LTA':
        q=pd.read_csv(D.LIB+'/07_QC_and_Exclusions/LTA_Reference_Session_20261028_QC_Log.csv'); q=q[q.category=='LTA_Bulk'].copy(); q['cond']=q.power.astype(int).astype(str)+'% / '+q.int_s.astype(int).astype(str)+' s / '+q.acc.astype(int).astype(str)
        q['ok']=~q.QC.str.contains('DARK'); g=q.groupby('cond').filter(lambda s:len(s)>=7); order=[o for o in ['80% / 30 s / 3','80% / 45 s / 2','70% / 30 s / 3','70% / 60 s / 2'] if o in set(g.cond)]
        cols=[('snr1092','Signal-to-noise of the main peak (1092)'),('ripple','Background ripple (counts, lower is better)'),('rREF','Correlation with the pooled mean')]
        for ax,(k,t) in zip(axs,cols):
            for i,o in enumerate(order):
                s=g[g.cond==o]; xs=np.random.default_rng(i).normal(i,.07,len(s)); ax.scatter(xs[s.ok.values],s[k][s.ok.values],color=c,s=22,label='reliable background' if i==0 else None); ax.scatter(xs[~s.ok.values],s[k][~s.ok.values],facecolors='none',edgecolors='#888',s=22,label='background contaminated by sample light' if i==0 else None)
            ax.set_xticks(range(len(order))); ax.set_xticklabels([o.replace(' / ','\n') for o in order],fontsize=7.5); ax.set_title(t,fontsize=8.5,loc='left')
        axs[0].legend(frameon=False,fontsize=6.8,loc='lower left'); axs[0].set_ylabel('laser power (% of max) / seconds / accumulations',fontsize=7)
        axs[0].set_ylabel('value')
    elif m=='NAM':
        q=pd.read_csv(D.LIB+'/07_QC_and_Exclusions/NAM_Session_20260924_QC_Log.csv'); q=q[q.category.str.contains('NAM')&(~q.QC.str.contains('SAT|FAIL|EXCL',regex=True))]
        order=sorted(q.power.unique()); cols=[('snr929','Signal-to-noise of the 929 peak'),('ripple_ds','Background ripple (counts)'),('r_NAM_ref','Correlation with the reference mean')]
        for ax,(k,t) in zip(axs,cols):
            for i,o in enumerate(order): s=q[q.power==o]; ax.scatter(np.random.default_rng(i).normal(i,.07,len(s)),s[k],color=c,s=22)
            ax.set_xticks(range(len(order))); ax.set_xticklabels([f'{int(o)}%' for o in order]); ax.set_title(t,fontsize=8.5,loc='left')
        axs[0].set_ylabel('value')
    else:
        plt.close(fig); fig,axs=plt.subplots(1,2,figsize=(7.6,3.3))
        q=pd.read_csv(D.LIB+'/07_QC_and_Exclusions/LPS_Reference_Session_20260928_QC_Log.csv'); q=q[(q.category=='LPS_Bulk')].copy(); q['cond']=q.power.astype(int).astype(str)+'% / '+q.int_s.astype(int).astype(str)+' s / '+q.acc.astype(int).astype(str)
        order=['60% / 30 s / 5','60% / 40 s / 5','70% / 30 s / 5']
        for ax,(k,t) in zip(axs,[('snr425','Signal-to-noise of the 425 peak'),('ripple','Background ripple (counts, lower is better)')]):
            for i,o in enumerate(order): s_=q[q.cond==o]; ax.scatter(np.random.default_rng(i).normal(i,.07,len(s_)),s_[k],color=c,s=22)
            ax.set_xticks(range(len(order))); ax.set_xticklabels([o.replace(' / ',chr(10)) for o in order],fontsize=7.5); ax.set_title(t,fontsize=8.5,loc='left')
        axs[0].set_ylabel('value')
    fig.suptitle('Choice of measurement condition (laser power as % of maximum / integration time / accumulations)',x=0.01,ha='left',fontweight='bold',fontsize=9.5); fig.tight_layout()
    return save(fig,f'{m}_bulk_select.png')
# ------------------------------------------------------------------ simulation
def struct_plain(m):
    S.draw_plain(m,os.path.join(FIG,f'{m}_struct_raw.png'),size=(1500,900) if m!='LPS' else (2200,1500))
    im=plt.imread(os.path.join(FIG,f'{m}_struct_raw.png')); fig,ax=plt.subplots(figsize=(9,5.3 if m!='LPS' else 6.6)); ax.imshow(im); ax.axis('off')
    ttl={'NAM':'N-acetylmuramic acid (beta form) used in the calculation','LTA':'Model of lipoteichoic acid used in the calculation','LPS':'Model of lipid A (core of lipopolysaccharide) used in the calculation'}[m]
    ax.set_title(ttl,loc='left',fontweight='bold',fontsize=10); return save(fig,f'{m}_struct.png')
def sim_spectrum(m,label_top=6):
    d=D.sim(m); k=d['k']; f=d['f'][k]; I=d['I'][k]; y=D.calc_curve(m); c=D.CALC
    fig,ax=plt.subplots(figsize=(9,3.9)); ax.plot(D.X,y,color=c,lw=1.6,label='calculated spectrum (broadened)'); ax.vlines(f,0,I/I.max()*0.9,color='#555',lw=.9,alpha=.7,label='individual calculated vibrations')
    top=np.argsort(-I)[:label_top]; last=[]
    for i in sorted(top,key=lambda i:f[i]):
        ax.annotate(f'{f[i]:.0f}',(f[i],I[i]/I.max()*0.9),xytext=(0,4),textcoords='offset points',ha='center',fontsize=8,color='#222')
    ax.set_xlim(400,1800); ax.set_ylim(0,1.12); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('Relative Raman intensity'); ax.legend(frameon=False,fontsize=8,loc='upper right')
    ax.set_title(f'Calculated Raman spectrum of the {D.NAME[m].split(" (")[0]} model',loc='left',fontweight='bold',fontsize=10)
    return save(fig,f'{m}_sim_spectrum.png')
def struct_assign(m,items,name):
    """items: list of dict(label text, mode idx)"""
    idx=[i['idx'] for i in items]; S.draw(m,idx,os.path.join(FIG,f'{m}_{name}_raw.png'),size=(1700,1050) if m!='LPS' else (2400,1600))
    im=plt.imread(os.path.join(FIG,f'{m}_{name}_raw.png')); fig=plt.figure(figsize=(9.5,6.2)); ax=fig.add_axes([0,0.0,0.68,1]); ax.imshow(im); ax.axis('off')
    ax2=fig.add_axes([0.69,0.05,0.31,0.9]); ax2.axis('off'); y=0.97
    for k,it in enumerate(items):
        ax2.add_patch(plt.Rectangle((0,y-0.035),0.07,0.045,color=S.PAL[k%len(S.PAL)],transform=ax2.transAxes)); ax2.text(0.1,y,it['text'],va='top',fontsize=7.6,transform=ax2.transAxes,wrap=True); y-=min(0.15,0.92/max(len(items),1))
    fig.suptitle(it.get('title',''),x=0.01,ha='left',fontsize=1,color='white')
    return save(fig,f'{m}_{name}.png')
# ------------------------------------------------------------------ comparison
def cmp_full(m,res):
    mean,sd,_=D.exp_ref(m); y=D.calc_curve(m); c=D.COL[m]
    fig,(a1,a2)=plt.subplots(2,1,figsize=(9.2,6),sharex=True,gridspec_kw=dict(hspace=.12))
    a1.fill_between(D.X,np.clip(mean-sd,0,None),mean+sd,color=c,alpha=.25,lw=0); a1.plot(D.X,mean,color=c,lw=1.6); a1.set_ylim(0,1.2); a1.set_ylabel('Experiment\n(normalised)')
    a2.plot(D.X,y,color=D.CALC,lw=1.5); a2.set_ylim(0,1.2); a2.set_xlim(400,1800); a2.set_ylabel('Calculation\n(normalised)'); a2.set_xlabel('Raman shift (cm$^{-1}$)')
    for ax in (a1,a2): ax.axvspan(*D.GLASS,color='#d0d0d0',alpha=.5,lw=0)
    a1.text(sum(D.GLASS)/2,1.17,'glass band zone',ha='center',fontsize=7.5,color='#555',va='top')
    for r in res:
        col=ST[r['status']]; a1.axvline(r['exp'],color=col,ls='--',lw=1); a1.text(r['exp'],1.0+0.0,f"{r['exp']:.0f}",rotation=90,ha='right',va='bottom',fontsize=7.8,color=col,bbox=dict(fc='white',ec='none',pad=.5,alpha=.7))
        if r['calc'] is not None: a2.axvline(r['calc'],color=col,ls='--',lw=1); a2.text(r['calc'],1.0,f"{r['calc']:.0f}",rotation=90,ha='right',va='bottom',fontsize=7.8,color=col,bbox=dict(fc='white',ec='none',pad=.5,alpha=.7))
    a1.legend(handles=[Line2D([0],[0],color=ST[s],ls='--',label=STL[s]) for s in ST if any(r['status']==s for r in res)],frameon=False,fontsize=7.5,loc='upper right',ncol=1)
    a1.set_title('Measured spectrum (top) and calculated spectrum (bottom): matching peaks are linked by colour',loc='left',fontweight='bold',fontsize=10)
    return save(fig,f'{m}_cmp_full.png')
def cmp_zoom(m,res,wins):
    mean,sd,_=D.exp_ref(m); d=D.sim(m); y=D.calc_curve(m); c=D.COL[m]; n=len(wins); cols=3 if n>3 else n; rows=int(np.ceil(n/cols))
    fig,axs=plt.subplots(rows,cols,figsize=(3.3*cols+.3,3.1*rows+.5)); axs=np.atleast_1d(axs).ravel()
    for ax,(a,b) in zip(axs,wins):
        k=(D.X>=a)&(D.X<=b); mx=mean[k].max(); my=y[k].max()
        ax.fill_between(D.X[k],0,mean[k]/mx,color=c,alpha=.28,lw=0); ax.plot(D.X[k],mean[k]/mx,color=c,lw=1.5,label='experiment')
        ax.plot(D.X[k],-1.15+y[k]/my,color=D.CALC,lw=1.4,label='calculation'); ax.axhline(-0.15,color='#bbb',lw=.5)
        for r in res:
            if a<=r['exp']<=b:
                col=ST[r['status']]; ax.plot([r['exp']]*2,[0,1.05],color=col,ls='--',lw=1); ax.text(r['exp'],1.1,f"{r['exp']:.0f}",ha='center',fontsize=8,color=col)
                if r['calc'] is not None and a<=r['calc']<=b:
                    ax.plot([r['calc']]*2,[-1.15,-0.15],color=col,ls='--',lw=1); ax.text(r['calc'],-1.28,f"{r['calc']:.0f}",ha='center',va='top',fontsize=8,color=col)
                    if abs(r['delta'])>10: ax.annotate('',xy=(r['calc'],0.5),xytext=(r['exp'],0.5),arrowprops=dict(arrowstyle='<->',color=col,lw=1.1)); ax.text((r['exp']+r['calc'])/2,0.56,f"{r['delta']:+.0f}",ha='center',fontsize=7.5,color=col)
        ax.set_xlim(a,b); ax.set_ylim(-1.5,1.35); ax.set_yticks([]); ax.set_xlabel('Raman shift (cm$^{-1}$)',fontsize=8.5)
    for ax in axs[n:]: ax.axis('off')
    axs[0].legend(frameon=False,fontsize=7.5,loc='upper left',bbox_to_anchor=(0,1.0))
    fig.suptitle('Close-ups: experiment (upper curve) and calculation (lower curve), each scaled to its tallest peak in the window',x=0.01,ha='left',fontweight='bold',fontsize=10); fig.tight_layout(); return save(fig,f'{m}_cmp_zoom.png')
def cmp_glass(m,res):
    mean,sd,cnt=D.exp_ref(m); bn,bc,nb=D.blank_mean(m); y=D.calc_curve(m); c=D.COL[m]
    fig,ax=plt.subplots(figsize=(9.2,4.6)); ax.plot(D.X,mean+2.3,color=c,lw=1.6,label='bulk sample (measured)'); ax.plot(D.X,bn+1.15,color='#555',lw=1.4,label='glass blank (measured)'); ax.plot(D.X,y,color=D.CALC,lw=1.5,label='calculated spectrum of the molecule')
    ax.axvspan(*D.GLASS,color='#d0d0d0',alpha=.5,lw=0)
    for r in res: ax.axvline(r['exp'],color=ST[r['status']],ls=':',lw=.9,alpha=.8)
    ax.set_xlim(400,1800); ax.set_ylim(0,3.6); ax.set_yticks([]); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('Normalised intensity (curves offset)')
    ax.legend(frameon=False,fontsize=8,loc='upper right'); ax.set_title('Which signals belong to the molecule and which to the glass slide',loc='left',fontweight='bold',fontsize=10)
    ax.text(sum(D.GLASS)/2,2.0,'glass band zone',ha='center',va='center',fontsize=7.5,color='#555',rotation=90)
    return save(fig,f'{m}_cmp_glass.png')
def cmp_shift(m,res):
    fig,ax=plt.subplots(figsize=(8.5,3.2)); r2=[r for r in res if r['delta'] is not None]; r2=sorted(r2,key=lambda r:r['exp'])
    ax.axhspan(-10,10,color='#2e8b57',alpha=.12,lw=0); ax.axhline(0,color='k',lw=.6)
    ax.bar(range(len(r2)),[r['delta'] for r in r2],color=[ST[r['status']] for r in r2],width=.6)
    ax.set_xticks(range(len(r2))); ax.set_xticklabels([f"{r['exp']:.0f}" for r in r2],fontsize=8); ax.set_xlabel('Experimental peak (cm$^{-1}$)'); ax.set_ylabel('Experiment minus calculation (cm$^{-1}$)')
    ax.set_title('Size and direction of the position difference for each matched peak (green band: within 10 cm$^{-1}$)',loc='left',fontweight='bold',fontsize=9.5); return save(fig,f'{m}_cmp_shift.png')
