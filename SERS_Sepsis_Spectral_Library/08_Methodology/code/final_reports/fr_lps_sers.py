"""LPS: SERS spectrum (reproducible band set) compared with the whole-molecule lipid A calculation and the bulk LPS reference."""
import os,runpy,numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import fr_data as D,fr_figs as G,fr_struct as SS,fr_docs as FD
S=r"C:\Users\sukes\AppData\Local\Temp\claude\C--Users-sukes-Downloads-sukesh\f9c0734c-e0bb-4f52-a4e5-d9f33e9bce00\scratchpad\sersfinal"
ns=runpy.run_path(r"C:\Users\sukes\Downloads\sukesh\SERS_Results_Oct2026\code\sers_final_figs.py")
X=D.X; carry=ns['carry']; spec=ns['spec']; B=pd.read_csv(S+r"\tables\lps_session_reproducible_bands.csv")
C=np.array([s['corr']/s['si'] for s in carry]); mean=C.mean(0); sd=C.std(0)
blank=np.mean([s['corr']/s['si'] for s in spec if s['group']=='blank'],0)
sim=D.sim('LPS'); calc=D.calc_curve('LPS'); bulk,_,_=D.exp_ref('LPS')
# expected vibration families for SERS bands (published SERS assignments of LPS); None = not assigned
EXP={619:None,785:None,878:None,1009:(('CC','HB'),'C-H bending / sugar C-O-C (published bands at 988 and 1003)'),1238:None,1330:(('HB',),'C-H deformation (published bands at 1330 and 1333)'),1368:None,1455:(('HB',),'CH2 / CH3 deformation (published band at 1450)'),1536:None,1592:None}
res=[]
for _,r in B.iterrows():
    pos=float(r.mean_position); key=int(r.band); fam=EXP[key]; f=sim['f']; I=sim['I']; k=sim['k']
    pool=[i for i in np.where(k&(I>=0.02))[0] if abs(f[i]-pos)<=50 and (fam is None or any(x in fam[0] for x in sim['fam'][i]))]
    if pool:
        i0=min(pool,key=lambda i:abs(f[i]-pos)); near=[i for i in pool if abs(f[i]-f[i0])<=4]; i=max(near,key=lambda i:I[i]); dl=pos-f[i]
        st='agrees' if abs(dl)<=10 else 'shifted'; res.append(dict(exp=pos,key=key,calc=float(f[i]),delta=float(dl),I=float(I[i]),label=str(sim['label'][i]),idx=int(i),typed=fam is not None,status=st,desc=fam[1] if fam else 'not assigned',snr=float(r.median_snr_carrying),lit=r.literature,sd=float(r.sd_position)))
    else: res.append(dict(exp=pos,key=key,calc=None,delta=None,I=None,label=None,idx=None,typed=fam is not None,status='none',desc=fam[1] if fam else 'not assigned',snr=float(r.median_snr_carrying),lit=r.literature,sd=float(r.sd_position)))
G_=(~((X>=480)&(X<=560)))
def mm(y,m): y=y[m]; return y
r_calc=float(np.corrcoef(mean[G_],calc[G_])[0,1]); r_bulk=float(np.corrcoef(mean[G_&~((X>=1308)&(X<=1455))],bulk[G_&~((X>=1308)&(X<=1455))])[0,1])
# chance test (position only, nearest calculated mode within 10, all modes)
rng=np.random.default_rng(5); modes=sim['f'][sim['k']]; bands=[r['exp'] for r in res]
def cnt(sh): return sum(np.min(np.abs(modes+sh-b))<=10 for b in bands)
real=cnt(0); dec=np.array([cnt(rng.uniform(15,70)*rng.choice([-1,1])) for _ in range(5000)]); p=float((dec>=real).mean())
ST=G.ST
OUTF=S+r"\lps_figs"; os.makedirs(OUTF,exist_ok=True)
def save(fig,n): p_=os.path.join(OUTF,n); fig.savefig(p_,dpi=200,bbox_inches='tight'); plt.close(fig); return p_
# --- fig 1 SERS spectrum
fig,ax=plt.subplots(figsize=(9,3.9)); c=D.COL['LPS']
ax.fill_between(X,mean-sd,mean+sd,color=c,alpha=.22,lw=0); ax.plot(X,mean,color=c,lw=1.6,label=f'LPS spots carrying the band set (n={len(carry)}), mean ± 1 SD'); ax.plot(X,blank,color='#555',lw=1,label='substrate blank (n=5)')
ax.set_xlim(400,1800); ax.set_ylim(-0.1,0.5); ax.axvspan(480,560,color='#d0d0d0',alpha=.5,lw=0); ax.text(520,0.47,'silicon peak\n(518, off scale)',ha='center',va='top',fontsize=7.5,color='#444')
for r in res: ax.text(r['exp'],max(mean[int(r['exp']-400)]+sd[int(r['exp']-400)],0)+0.012,f"{r['exp']:.0f}",ha='center',fontsize=8,color=c)
ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('Signal / silicon peak height'); ax.legend(frameon=False,fontsize=8,loc='upper right')
ax.set_title('SERS spectrum of LPS on etched silicon: the reproducible band set',loc='left',fontweight='bold',fontsize=10); f1=save(fig,'L1.png')
# --- fig 2 three panels
fig,(a0,a1,a2)=plt.subplots(3,1,figsize=(9.2,7.6),sharex=True,gridspec_kw=dict(hspace=.12))
a0.plot(X,bulk,color='#7a7a7a',lw=1.4); a0.axvspan(*D.GLASS,color='#d0d0d0',alpha=.5,lw=0); a0.set_ylabel('Bulk LPS\n(normalised)'); a0.set_ylim(0,1.25)
for p_,_ in D.peaks('LPS'): a0.axvline(p_,color='#7a7a7a',ls=':',lw=.9); a0.text(p_,1.02,f'{p_:.0f}',ha='center',fontsize=7.5,color='#555')
a0.set_title('Bulk LPS (top), SERS of LPS (middle) and calculated lipid A model (bottom)',loc='left',fontweight='bold',fontsize=10)
m=mean.copy(); a1.fill_between(X,np.clip(m-sd,-1,None)/0.35,(m+sd)/0.35,color=c,alpha=.22,lw=0); a1.plot(X,m/0.35,color=c,lw=1.5); a1.axvspan(480,560,color='#d0d0d0',alpha=.5,lw=0); a1.set_ylim(-0.25,1.25); a1.set_ylabel('SERS\n(scaled)')
a2.plot(X,calc,color=D.CALC,lw=1.4); a2.set_ylim(0,1.25); a2.set_ylabel('Calculation\n(normalised)'); a2.set_xlim(400,1800); a2.set_xlabel('Raman shift (cm$^{-1}$)'); a2.axvspan(*D.GLASS,color='#d0d0d0',alpha=.5,lw=0)
for r in res:
    col=ST[r['status']]; a1.axvline(r['exp'],color=col,ls='--',lw=1); a1.text(r['exp'],1.0,f"{r['exp']:.0f}",rotation=90,ha='right',va='bottom',fontsize=7.5,color=col,bbox=dict(fc='white',ec='none',pad=.4,alpha=.7))
    if r['calc'] is not None: a2.axvline(r['calc'],color=col,ls='--',lw=1); a2.text(r['calc'],1.0,f"{r['calc']:.0f}",rotation=90,ha='right',va='bottom',fontsize=7.5,color=col,bbox=dict(fc='white',ec='none',pad=.4,alpha=.7))
a1.legend(handles=[Line2D([0],[0],color=ST[s],ls='--',label={'agrees':'agrees (within 10 cm$^{-1}$)','shifted':'shifted (10 to 50 cm$^{-1}$)','none':'no counterpart'}[s]) for s in ST if any(r['status']==s for r in res)],frameon=False,fontsize=7.5,loc='upper right')
f2=save(fig,'L2.png')
# --- fig 3 zooms
wins=[(590,660),(840,920),(960,1060),(1200,1280),(1300,1400),(1420,1500),(1510,1620)]
fig,axs=plt.subplots(3,3,figsize=(10.4,8.6)); axs=axs.ravel()
for ax,(a,b) in zip(axs,wins):
    k=(X>=a)&(X<=b); mx=max(mean[k].max(),1e-6); my=calc[k].max()
    ax.fill_between(X[k],0,np.clip(mean[k],0,None)/mx,color=c,alpha=.28,lw=0); ax.plot(X[k],mean[k]/mx,color=c,lw=1.4); ax.plot(X[k],-1.15+calc[k]/my,color=D.CALC,lw=1.3); ax.axhline(-0.15,color='#bbb',lw=.5)
    for r in res:
        if a<=r['exp']<=b:
            col=ST[r['status']]; ax.plot([r['exp']]*2,[0,1.05],color=col,ls='--',lw=1); ax.text(r['exp'],1.1,f"{r['exp']:.0f}",ha='center',fontsize=8,color=col)
            if r['calc'] is not None and a<=r['calc']<=b:
                ax.plot([r['calc']]*2,[-1.15,-0.15],color=col,ls='--',lw=1); ax.text(r['calc'],-1.28,f"{r['calc']:.0f}",ha='center',va='top',fontsize=8,color=col)
                if abs(r['delta'])>10: ax.annotate('',xy=(r['calc'],0.5),xytext=(r['exp'],0.5),arrowprops=dict(arrowstyle='<->',color=col,lw=1)); ax.text((r['exp']+r['calc'])/2,0.56,f"{r['delta']:+.0f}",ha='center',fontsize=7.5,color=col)
    ax.set_xlim(a,b); ax.set_ylim(-1.5,1.35); ax.set_yticks([]); ax.set_xlabel('Raman shift (cm$^{-1}$)',fontsize=8.5)
for ax in axs[len(wins):]: ax.axis('off')
axs[0].legend(handles=[Line2D([0],[0],color=c,label='SERS (mean)'),Line2D([0],[0],color=D.CALC,label='calculation')],frameon=False,fontsize=7.5,loc='upper left')
fig.suptitle('Close-ups: SERS (upper curve) and calculation (lower curve), each scaled to its tallest peak in the window',x=0.01,ha='left',fontweight='bold',fontsize=10); fig.tight_layout(); f3=save(fig,'L3.png')
# --- fig 4 structure
items=[dict(idx=r['idx'],text=f"{r['exp']:.0f} SERS / {r['calc']:.0f} calculated\n{r['label'].split(' (')[0]}") for r in sorted([r for r in res if r['idx'] is not None],key=lambda r:r['exp'])[:10]]
G.FIG=OUTF; f4=G.struct_assign('LPS',items,'sers_assign')
import pickle; pickle.dump(dict(res=res,r_calc=r_calc,r_bulk=r_bulk,real=real,dec_mean=float(dec.mean()),dec_sd=float(dec.std()),p=p,figs=[f1,f2,f3,f4],n=len(carry),nmodes=len(modes)),open(S+r'\lps_res.pkl','wb'))
print(r_calc,r_bulk,real,dec.mean(),p);
for r in res: print({k:(round(v,1) if isinstance(v,float) else v) for k,v in r.items() if k in('exp','calc','delta','I','label','status','typed')})
