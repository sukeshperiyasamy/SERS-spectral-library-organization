import runpy,os,json,numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
ns=runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)),'dft_compare_1.py'))
X,G,ref,gauss,mm=[ns[k] for k in('X','G','ref','gauss','mm')]; L=ns['L']; SIM=r"C:\Users\sukes\Downloads\sukesh\lps output simulation"
r=json.load(open(os.path.join(L,'05_Tables','LipidA_vs_LPS_results.json')))
a=pd.read_csv(os.path.join(SIM,'lipidA_raman_act.csv')); nu=a.iloc[:,0].values*0.965; S=a.iloc[:,1].values
I=S*(1e7/785-nu)**4/(nu*(1-np.exp(-1.4388*nu/298.15))); I/=I.max(); k=(nu>=400)&(nu<=1800); modes,act=nu[k],I[k]
OUT=os.path.join(L,'04_Figures','LipidA_Model_20261028'); os.makedirs(OUT,exist_ok=True); plt.rcParams.update({'font.family':'Arial','font.size':9})
cc=lambda d:'#2e8b57' if abs(d)<=10 else '#e08e0b' if abs(d)<=18 else '#c0392b'
e=ref('LPS'); sp=mm(gauss(modes,act))
fig,(a1,a2)=plt.subplots(2,1,figsize=(10,6),sharex=True)
a1.fill_between(X,0,e,color='#b5421c',alpha=.3); a1.plot(X,e,color='#b5421c',lw=1.2); a1.axvspan(1308,1455,color='#bbb',alpha=.35)
for b in r['bands']:
    a1.axvline(b['exp'],color=cc(b['delta']),ls='--',lw=1); a2.axvline(b['exp'],color=cc(b['delta']),ls='--',lw=1,alpha=.8); a1.text(b['exp'],1.04,f"{b['exp']:.0f}",ha='center',fontsize=7.5,color=cc(b['delta']))
a1.set_ylim(0,1.25); a1.set_ylabel('Experimental\n(library reference, norm.)'); a1.set_title('LPS: library experimental spectrum (top) vs whole-molecule model, shortened Kdo2-lipid A (bottom)',loc='left',fontweight='bold',fontsize=9.5)
a2.axvspan(1308,1455,color='#bbb',alpha=.35); a2.plot(X,sp,'k',lw=1.1,label='model spectrum (12 cm$^{-1}$ broadening)'); a2.vlines(modes,0,act*0.9,color='#2c5aa0',lw=1,alpha=.6,label='calculated modes (scaled 0.965)')
a2.text(1516,0.93,'1516: probably overstated\n(amide, small basis)',fontsize=7,ha='center',color='#555')
a2.set_xlim(400,1800); a2.set_ylim(0,1.1); a2.set_ylabel('Model (norm.)'); a2.set_xlabel('Raman shift (cm$^{-1}$)'); a2.legend(frameon=False,fontsize=7.5,loc='upper left')
for ax in (a1,a2): ax.spines[['top','right']].set_visible(False)
fig.tight_layout(); fig.savefig(f'{OUT}/LPS_Exp_vs_LipidA_Model.png',dpi=200); plt.close(fig)
# whole vs fragments
fig,ax=plt.subplots(1,3,figsize=(11,3.6)); xs=np.arange(5); lab=[f"{b['exp']:.0f}" for b in r['bands']]; w=.38
d1=[b['delta'] for b in r['bands']]; d2=[b['delta'] for b in r['frag_bands']]
ax[0].bar(xs-w/2,d1,w,color='#2c5aa0',label='whole-molecule model'); ax[0].bar(xs+w/2,d2,w,color='#999',label='five fragments'); ax[0].axhspan(-10,10,color='#2e8b57',alpha=.12); ax[0].axhline(0,color='k',lw=.6)
ax[0].set_xticks(xs); ax[0].set_xticklabels(lab); ax[0].set_ylabel('experiment - calculated (cm$^{-1}$)'); ax[0].set_title('Position difference',loc='left',fontweight='bold',fontsize=9); ax[0].legend(frameon=False,fontsize=7)
ax[1].bar(xs-w/2,[b['act'] for b in r['bands']],w,color='#2c5aa0'); ax[1].bar(xs+w/2,[b['act'] for b in r['frag_bands']],w,color='#999')
ax[1].set_xticks(xs); ax[1].set_xticklabels(lab); ax[1].set_ylabel('calculated relative activity'); ax[1].set_title('Strength of the matched mode',loc='left',fontweight='bold',fontsize=9)
for ar,col,nm,v in ((ax[2],'#2c5aa0','whole',[r['r_whole'],r['frag_r_equal']]),):
    ar.bar([0,1],v,color=['#2c5aa0','#999']); ar.axhline(0,color='k',lw=.6); ar.set_xticks([0,1]); ar.set_xticklabels(['whole model','fragments\n(equal weights)']); ar.set_ylim(-.1,.5)
    ar.set_ylabel('whole-spectrum r'); ar.set_title('Shape agreement',loc='left',fontweight='bold',fontsize=9)
    for i,val in enumerate(v): ar.text(i,val+.015 if val>=0 else val-.05,f'{val:.2f}',ha='center',fontsize=8)
for q in ax: q.spines[['top','right']].set_visible(False)
fig.tight_layout(); fig.savefig(f'{OUT}/LPS_Whole_Molecule_vs_Fragments.png',dpi=200); plt.close(fig)
print('ok')
