import runpy,os,json,numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
ns=runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)),'dft_compare_1.py'))
X,G,gauss,mm,nmatch,decoy,data,R,libbands=[ns[k] for k in('X','G','gauss','mm','nmatch','decoy','data','R','libbands')]; L=ns['L']
SIM=r"C:\Users\sukes\Downloads\sukesh\simulation\lta output simulation\quick_B3LYP-3-21G"
r=json.load(open(os.path.join(L,'05_Tables','LTAmodel_vs_LTA_results.json'))); lp=json.load(open(os.path.join(L,'05_Tables','LipidA_vs_LPS_results.json')))
rd=pd.read_csv(f"{L}/03_Reference_Spectra/LTA/LTA_Bulk_Reference_20261028_Pooled_Mean_SD.csv",comment='#'); e=np.interp(X,rd.iloc[:,0].values,rd['Normalised_mean'].values)
a=pd.read_csv(os.path.join(SIM,'lta_model_raman_act.csv')); nu=a.iloc[:,0].values*0.965; S=a.iloc[:,1].values
I=S*(1e7/785-nu)**4/(nu*(1-np.exp(-1.4388*nu/298.15))); I/=I.max(); k=(nu>=400)&(nu<=1800); modes,act=nu[k],I[k]/I[k].max()
OUT=os.path.join(L,'04_Figures','LTA_Model_20261028'); os.makedirs(OUT,exist_ok=True); plt.rcParams.update({'font.family':'Arial','font.size':9})
cc=lambda d:'#2e8b57' if abs(d)<=10 else '#e08e0b' if abs(d)<=18 else '#c0392b'
bands=[(b[0],b[1]) for b in r['bands_used']]
def overlay(name,title,sim_y,mod,ma,lab,col,extra):
    fig,(a1,a2)=plt.subplots(2,1,figsize=(10,6),sharex=True)
    a1.fill_between(X,0,e,color='#2a7d46',alpha=.3); a1.plot(X,e,color='#2a7d46',lw=1.2); a1.axvspan(1308,1455,color='#bbb',alpha=.35)
    blk=r['model']['bands'] if lab=='model' else r['frag']['bands']
    for b in blk:
        a1.axvline(b['exp'],color=cc(b['delta']),ls='--',lw=1); a2.axvline(b['exp'],color=cc(b['delta']),ls='--',lw=1,alpha=.8)
        a1.text(b['exp'],1.03,f"{b['exp']:.0f}",ha='center',fontsize=7.5,color=cc(b['delta']),rotation=90,va='bottom')
    a1.set_ylim(0,1.3); a1.set_ylabel('Experimental\n(pooled reference v2.1, n = 17)'); a1.set_title(title,loc='left',fontweight='bold',fontsize=9.5)
    a1.legend(handles=[Line2D([0],[0],color='#2e8b57',ls='--',label='within 10 cm$^{-1}$ of a mode'),Line2D([0],[0],color='#e08e0b',ls='--',label='10 to 18'),Line2D([0],[0],color='#c0392b',ls='--',label='more than 18')],fontsize=7,frameon=False,loc='upper right')
    a2.axvspan(1308,1455,color='#bbb',alpha=.35); a2.plot(X,sim_y,'k',lw=1.1,label=extra); a2.vlines(mod,0,ma*0.9,color=col,lw=1,alpha=.7,label='calculated modes')
    a2.set_xlim(400,1800); a2.set_ylim(0,1.1); a2.set_ylabel('Calculation (norm.)'); a2.set_xlabel('Raman shift (cm$^{-1}$)'); a2.legend(frameon=False,fontsize=7.5,loc='upper left')
    for ax in (a1,a2): ax.spines[['top','right']].set_visible(False)
    fig.tight_layout(); fig.savefig(f'{OUT}/{name}',dpi=200); plt.close(fig)
overlay('LTA_Exp_vs_Model.png','LTA: library experimental spectrum (top) vs whole-molecule model (bottom)',mm(gauss(modes,act)),modes,act,'model','#2c5aa0','model spectrum (12 cm$^{-1}$ broadening)')
fd=data['LTA']; overlay('LTA_Exp_vs_Fragments.png','LTA: library experimental spectrum (top) vs three-fragment calculation (bottom)',fd['sp'],fd['modes'],fd['act']/fd['act'].max(),'frag','#777','fragment composite (equal weights)')
fig,ax=plt.subplots(1,3,figsize=(11.5,3.6)); xs=np.arange(len(bands)); lab=[f"{b[0]:.0f}" for b in bands]; w=.38
d1=[b['delta'] for b in r['model']['bands']]; d2=[b['delta'] for b in r['frag']['bands']]
ax[0].bar(xs-w/2,d1,w,color='#2c5aa0',label='whole-molecule model'); ax[0].bar(xs+w/2,d2,w,color='#999',label='three fragments'); ax[0].axhspan(-10,10,color='#2e8b57',alpha=.12); ax[0].axhline(0,color='k',lw=.6)
ax[0].set_xticks(xs); ax[0].set_xticklabels(lab,fontsize=7.5); ax[0].set_ylabel('experiment - calculated (cm$^{-1}$)'); ax[0].set_title('Position difference',loc='left',fontweight='bold',fontsize=9); ax[0].legend(frameon=False,fontsize=7)
ax[1].bar(xs-w/2,[b['act'] for b in r['model']['bands']],w,color='#2c5aa0'); ax[1].bar(xs+w/2,[b['act'] for b in r['frag']['bands']],w,color='#999')
ax[1].set_xticks(xs); ax[1].set_xticklabels(lab,fontsize=7.5); ax[1].set_ylabel('calculated relative activity'); ax[1].set_title('Strength of the matched mode',loc='left',fontweight='bold',fontsize=9)
v=[r['model']['r_whole'],r['frag']['r_whole']]; ax[2].bar([0,1],v,color=['#2c5aa0','#999']); ax[2].axhline(0,color='k',lw=.6); ax[2].set_xticks([0,1]); ax[2].set_xticklabels(['whole model','fragments\n(equal weights)']); ax[2].set_ylim(-.1,.5); ax[2].set_ylabel('whole-spectrum r'); ax[2].set_title('Shape agreement',loc='left',fontweight='bold',fontsize=9)
for i,val in enumerate(v): ax[2].text(i,val+.015 if val>=0 else val-.05,f'{val:.2f}',ha='center',fontsize=8)
for q in ax: q.spines[['top','right']].set_visible(False)
fig.tight_layout(); fig.savefig(f'{OUT}/LTA_Model_vs_Fragments.png',dpi=200); plt.close(fig)
# chance test and differences for every calculation (replace figures D and E of 27 Oct)
sets=[]
sets.append(('NAM','#1f5fa8',libbands('NAM'),data['NAM']['modes'],R['NAM']['t10']['real'],[b['delta'] for b in R['NAM']['bands']]))
sets.append(('LPS fragments','#b5421c',libbands('LPS'),data['LPS']['modes'],R['LPS']['t10']['real'],[b['delta'] for b in R['LPS']['bands']]))
ua=pd.read_csv(os.path.join(L,'08_Methodology','simulation','LPS_LipidA_Model_20261028','lipidA_raman_act.csv')); un=ua.iloc[:,0].values*0.965; uk=(un>=400)&(un<=1800)
sets.append(('LPS lipid A model','#7a1f0c',libbands('LPS'),un[uk],lp['t10']['real'],[b['delta'] for b in lp['bands']]))
sets.append(('LTA fragments','#6fae83',bands,fd['modes'],r['frag']['t10']['real'],[b['delta'] for b in r['frag']['bands']]))
sets.append(('LTA model','#2a7d46',bands,modes,r['model']['t10']['real'],[b['delta'] for b in r['model']['bands']]))
fig,axs=plt.subplots(1,5,figsize=(13,3))
for ax,(nm,col,bb,mo,real,_) in zip(axs,sets):
    dc=decoy(bb,mo,10); ax.hist(dc,bins=np.arange(-.5,len(bb)+1.5,1),color='#bbb',density=True); ax.axvline(real,color=col,lw=2.5,label=f'real: {real}/{len(bb)}')
    ax.set_title(f'{nm} (p = {(dc>=real).mean():.2f})',fontsize=8.5); ax.set_xlabel('bands within 10 cm$^{-1}$',fontsize=8); ax.legend(fontsize=7,frameon=False); ax.spines[['top','right']].set_visible(False)
axs[0].set_ylabel('fraction of random shifts')
fig.suptitle('Chance test at 10 cm$^{-1}$: grey = modes shifted by a random 15 to 70 cm$^{-1}$ (5000 trials); coloured line = real calculation',x=.01,ha='left',fontsize=9,fontweight='bold')
fig.tight_layout(); fig.savefig(f'{OUT}/D_Chance_Test_all.png',dpi=200); plt.close(fig)
fig,ax=plt.subplots(figsize=(10,3.4))
for nm,col,bb,_,_,dl in sets: ax.plot([b[0] for b in bb],dl,'o',color=col,label=nm,ms=5.5,alpha=.85)
ax.axhspan(-10,10,color='#2e8b57',alpha=.12); ax.axhline(0,color='k',lw=.6); ax.set_xlabel('Experimental band (cm$^{-1}$)'); ax.set_ylabel('exp - nearest mode (cm$^{-1}$)'); ax.legend(frameon=False,fontsize=7.5,ncol=5); ax.spines[['top','right']].set_visible(False); ax.set_ylim(-40,65)
ax.set_title('Position difference of every library band from its nearest calculated mode (green = within 10 cm$^{-1}$)',loc='left',fontweight='bold',fontsize=9)
fig.tight_layout(); fig.savefig(f'{OUT}/E_Position_Differences_all.png',dpi=200); plt.close(fig)
print(os.listdir(OUT))
