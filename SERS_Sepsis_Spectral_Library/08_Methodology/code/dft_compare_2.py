import runpy,os,numpy as np,matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
ns=runpy.run_path(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)),"dft_compare_1.py"))
data,R,X,G,ref,nmatch,decoy,libbands,gauss=[ns[k] for k in ('data','R','X','G','ref','nmatch','decoy','libbands','gauss')]
OUT=r"C:\Users\sukes\Downloads\sukesh\SERS_Sepsis_Spectral_Library\04_Figures\DFT_Comparison_20261027"; os.makedirs(OUT,exist_ok=True)
plt.rcParams.update({'font.family':'Arial','font.size':9})
COL={'NAM':'#1f5fa8','LPS':'#b5421c','LTA':'#2a7d46'}
FC={'Glucosamine':'#8e44ad','Heptose':'#d35400','KDO':'#16a085','Myristic_Acid':'#7f8c8d','Phosphoric_Acid':'#c0392b','Glycerol-Phosphate':'#c0392b','D-Alanine':'#2980b9','GlcNAc':'#27ae60'}
def cc(d): return '#2e8b57' if abs(d)<=10 else '#e08e0b' if abs(d)<=18 else '#c0392b'
for a in ('NAM','LPS','LTA'):
    e=ref(a); d=data[a]; fig,(ax1,ax2)=plt.subplots(2,1,figsize=(10,6),sharex=True,gridspec_kw={'height_ratios':[1,1]})
    ax1.fill_between(X,0,e,color=COL[a],alpha=.3); ax1.plot(X,e,color=COL[a],lw=1.2)
    ax1.axvspan(1308,1455,color='#bbbbbb',alpha=.35)
    for b in R[a]['bands']:
        ax1.axvline(b['exp'],color=cc(b['delta']),ls='--',lw=1); ax1.text(b['exp'],1.02,f"{b['exp']:.0f}",ha='center',fontsize=7.5,color=cc(b['delta']),rotation=90,va='bottom')
        ax2.axvline(b['exp'],color=cc(b['delta']),ls='--',lw=1,alpha=.8)
    ax1.set_ylim(0,1.3); ax1.set_ylabel('Experimental\n(library reference, norm.)'); ax1.set_title(f'{a}: library experimental spectrum (top) vs DFT simulation (bottom)',loc='left',fontweight='bold')
    ax2.axvspan(1308,1455,color='#bbbbbb',alpha=.35)
    if a=='NAM': ax2.plot(X,d['sp'],color='k',lw=1.1,label='DFT simulated spectrum (broadened)')
    elif a=='LPS': ax2.plot(X,d['sp'],color='k',lw=1.1,label='fragment composite (equal weights)')
    else: ax2.plot(X,d['sp'],color='k',lw=1.1,label='fragment composite (equal weights)')
    for f in np.unique(d['label']) if a!='NAM' else [None]:
        k=(d['label']==f) if f else np.ones(len(d['modes']),bool)
        ax2.vlines(d['modes'][k],0,d['act'][k]/max(d['act'].max(),1e-9)*0.9,color=FC.get(f,'#555'),lw=1.3,alpha=.8,label=(f if f else 'calculated modes (scaled)'))
    ax2.set_xlim(400,1800); ax2.set_ylim(0,1.05); ax2.set_ylabel('DFT (norm.)'); ax2.set_xlabel('Raman shift (cm$^{-1}$)')
    ax2.legend(fontsize=7,ncol=3,frameon=False,loc='upper right')
    from matplotlib.lines import Line2D
    ax1.legend(handles=[Line2D([0],[0],color='#2e8b57',ls='--',label='within 10 cm$^{-1}$ of a DFT mode'),Line2D([0],[0],color='#e08e0b',ls='--',label='10 to 18 cm$^{-1}$'),Line2D([0],[0],color='#c0392b',ls='--',label='more than 18 cm$^{-1}$')],fontsize=7,frameon=False,loc='upper right')
    for ax in (ax1,ax2): ax.spines[['top','right']].set_visible(False)
    fig.tight_layout(); fig.savefig(f"{OUT}/{a}_Overlay_Exp_vs_DFT.png",dpi=200); plt.close(fig)
# decoy histograms
fig,axs=plt.subplots(1,3,figsize=(10,3))
for ax,a in zip(axs,('NAM','LPS','LTA')):
    bands=libbands(a); modes=data[a]['modes']; dc=decoy(bands,modes,10)
    ax.hist(dc,bins=np.arange(-.5,len(bands)+1.5,1),color='#bbbbbb',density=True)
    ax.axvline(R[a]['t10']['real'],color=COL[a],lw=2.5,label=f"real DFT: {R[a]['t10']['real']}/{len(bands)}")
    ax.set_title(f"{a} (p = {R[a]['t10']['p']:.2f})",fontsize=9); ax.set_xlabel('bands within 10 cm$^{-1}$ of a mode'); ax.legend(fontsize=7.5,frameon=False); ax.spines[['top','right']].set_visible(False)
axs[0].set_ylabel('fraction of random shifts')
fig.suptitle('Chance test: grey = DFT modes rigidly shifted by a random 15 to 70 cm$^{-1}$ (5000 trials); coloured line = real DFT',x=.01,ha='left',fontsize=9,fontweight='bold')
fig.tight_layout(); fig.savefig(f"{OUT}/D_Chance_Test.png",dpi=200); plt.close(fig)
# delta chart
fig,ax=plt.subplots(figsize=(10,3.4));
for a in ('NAM','LPS','LTA'):
    b=R[a]['bands']; ax.plot([x['exp'] for x in b],[x['delta'] for x in b],'o',color=COL[a],label=a,ms=6)
ax.axhspan(-10,10,color='#2e8b57',alpha=.12); ax.axhline(0,color='k',lw=.6); ax.set_xlabel('Experimental band (cm$^{-1}$)'); ax.set_ylabel('exp - nearest DFT mode (cm$^{-1}$)'); ax.legend(frameon=False); ax.spines[['top','right']].set_visible(False)
ax.set_title('Position difference of every library band from its nearest DFT mode (green = within 10 cm$^{-1}$)',loc='left',fontweight='bold',fontsize=9)
fig.tight_layout(); fig.savefig(f"{OUT}/E_Position_Differences.png",dpi=200); plt.close(fig)
print(os.listdir(OUT))
