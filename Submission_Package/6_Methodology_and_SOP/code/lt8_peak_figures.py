# LTA reference v2: annotated peaks, zooms, structure map, and how the bands relate (ratios and correlations). Writes FigL6-L8 and lt8_stats.pkl
import os,pickle,numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,Circle
from lib2 import X,LIB
H=os.path.dirname(os.path.abspath(__file__)); R=pickle.load(open(os.path.join(H,'lt4_result.pkl'),'rb'))
OUT=os.path.join(LIB,'04_Figures','LTA_Reference_20261028'); plt.rcParams.update({'font.family':'Arial','font.size':9})
spots=R['spots']; core=[s for s in spots if s['n'] in R['core']]; ext=[s for s in spots if s['n'] in R['ext']]
GRP={'phosphate':('#c0392b','Phosphodiester (PO$_2^-$)'),'backbone':('#1f5fa8','Glycerol / backbone skeleton'),'lipid':('#e08e0b','Lipid chain (CH$_2$)'),'ester':('#8e44ad','Ester C=O'),'unk':('#7f7f7f','Not assigned')}
PEAKS=[(419,'unk','skeletal'),(539,'backbone','skeletal'),(629,'unk',''),(723,'lipid','CH$_2$ rock'),(798,'phosphate','O-P-O / C-O-P'),(861,'backbone','C-C, C-O-C'),(1092,'phosphate','PO$_2^-$ sym.'),(1246,'phosphate','PO$_2^-$ asym.'),(1459,'lipid','CH$_2$ bend'),(1583,'unk',''),(1751,'ester','C=O')]
def h(s,p,t=6): w=(X>=p-t)&(X<=p+t); return float(s['corr'][w].max())
# ---------- stats: ratio to 1092 and correlations
rows=[]
for p,g,_ in PEAKS:
    r=np.array([h(s,p)/h(s,1092) for s in core]); rows.append((p,g,float(np.median(r)),float(100*np.std(r,ddof=1)/np.mean(r))))
H_=np.array([[h(s,p) for p,_,_ in PEAKS] for s in ext]); C=np.corrcoef(H_.T); idx={p:i for i,(p,_,_) in enumerate(PEAKS)}
pairs=[(1092,798),(1092,861),(1092,1246),(1092,539),(1092,1459),(1459,723),(1092,1751),(1459,1751)]
cor=[(a,b,float(C[idx[a],idx[b]])) for a,b in pairs]
pickle.dump(dict(ratios=rows,cor=cor,n_ext=len(ext)),open(os.path.join(H,'lt8_stats.pkl'),'wb')); print([(p,round(m,2),round(c,1)) for p,g,m,c in rows]); print([(a,b,round(c,2)) for a,b,c in cor])
# ---------- L6 annotated spectrum
fig,ax=plt.subplots(figsize=(10,4.8)); Mc,SD=R['Mc'],R['SDc']
ax.fill_between(X,Mc-SD,Mc+SD,color='#cfe6d8',lw=0); ax.plot(X,Mc,color='#1a6b45',lw=1.4); ax.axvspan(1308,1455,color='#dddddd',alpha=.4); ax.text(1380,2750,'glass zone',ha='center',fontsize=7.5,color='#777777')
for p,g,lab in PEAKS:
    j=int(np.argmin(abs(X-p))); top=Mc[j]+SD[j]; c=GRP[g][0]
    ax.vlines(p,Mc[j],top+120,color=c,lw=1.2); ax.text(p,top+160,f'{p}',rotation=90,ha='center',va='bottom',fontsize=8.5,color=c,fontweight='bold')
    if lab: ax.text(p,-470,lab,rotation=90,ha='center',va='top',fontsize=6.8,color=c)
for g,(c,l) in GRP.items(): ax.plot([],[],'s',color=c,label=l)
ax.set_xlim(400,1800); ax.set_ylim(-1500,3000); ax.set_xlabel('Raman shift (cm$^{-1}$)',labelpad=2); ax.set_ylabel('baseline-corrected counts'); ax.legend(frameon=False,fontsize=8,ncol=3,loc='upper left'); ax.spines[['top','right']].set_visible(False)
ax.set_title('LTA reference v2: the labelled peaks, coloured by the part of the molecule they are consistent with (tentative)',loc='left',fontweight='bold',fontsize=9.5)
fig.tight_layout(); fig.savefig(os.path.join(OUT,'FigL6_LTA_Peaks_Annotated.png'),dpi=200); plt.close(fig)
# ---------- L7 zooms
fig,axs=plt.subplots(3,3,figsize=(10,7)); sel=[539,723,798,861,1092,1246,1459,1751,419]
for ax,p in zip(axs.ravel(),sel):
    g=[x for x in PEAKS if x[0]==p][0][1]; c=GRP[g][0]; m=(X>=p-45)&(X<=p+45)
    for s in core: ax.plot(X[m],s['corr'][m],color=c,alpha=.25,lw=.7)
    ax.plot(X[m],R['Mc'][m],color=c,lw=1.6); ax.axvline(p,color=c,ls=':',lw=.8); ax.set_title(f'{p} cm$^{{-1}}$',fontsize=9.5,color=c,fontweight='bold'); ax.spines[['top','right']].set_visible(False); ax.tick_params(labelsize=7)
fig.suptitle('Each labelled band in the 10 reference spots (thin lines) and their mean (thick line)',x=.01,ha='left',fontsize=9.5,fontweight='bold'); fig.tight_layout(); fig.savefig(os.path.join(OUT,'FigL7_LTA_Peak_Zooms.png'),dpi=200); plt.close(fig)
# ---------- L8 structure map (schematic)
fig,ax=plt.subplots(figsize=(10,4.3)); ax.set_xlim(0,100); ax.set_ylim(0,44); ax.axis('off')
def box(x,y,w,hh,c,t,fs=9): ax.add_patch(FancyBboxPatch((x,y),w,hh,boxstyle='round,pad=0.3,rounding_size=1',fc=c,ec='#444444',lw=.8,alpha=.85)); ax.text(x+w/2,y+hh/2,t,ha='center',va='center',fontsize=fs,color='white',fontweight='bold')
box(2,22,16,12,'#e08e0b','lipid anchor\n(hydrophobic)')
for i,x in enumerate((26,48,70)):
    box(x,22,16,12,'#1f5fa8','glycerol\n(C-C-C)'); box(x+17.5,22,3.3,12,'#c0392b','P',9)
    ax.plot([x+16,x+17.5],[28,28],color='#444444',lw=1.2)
    if i<2: ax.plot([x+20.8,x+26],[28,28],color='#444444',lw=1.2)
    box(x+2,36.5,12,5,'#8e44ad','D-Ala / glycosyl',7.5); ax.plot([x+8,x+8],[34,36.5],color='#444444',lw=1)
ax.plot([18,26],[28,28],color='#444444',lw=1.2); ax.text(91,28,'... n repeats',fontsize=9,va='center'); ax.plot([86.8,90],[28,28],color='#444444',lw=1.2)
def note(x,t,c,y=14): ax.text(x,y,t,ha='center',va='top',fontsize=8,color=c,linespacing=1.4)
note(10,'1459, 723\nCH$_2$ of the\nlipid chains','#e08e0b'); note(34,'861, 539, 419\nglycerol skeleton\n(C-C, C-O-C, deformations)','#1f5fa8'); note(55.5,'1092, 1246, 798\nphosphodiester\nPO$_2^-$ and O-P-O','#c0392b'); note(80,'1751\nester C=O\n(D-alanyl, lipid)','#8e44ad')
ax.text(50,3,'Schematic of S. aureus LTA as described by the supplier: phosphodiester-linked glycerol phosphate bound to a lipid; C2 usually glycosylated and/or D-alanylated. Band assignments are tentative.',ha='center',fontsize=7.5,color='#444444')
ax.set_title('Where the bands are consistent with sitting in the LTA molecule',loc='left',fontweight='bold',fontsize=9.5)
fig.tight_layout(); fig.savefig(os.path.join(OUT,'FigL8_LTA_Structure_Map.png'),dpi=200); plt.close(fig); print(sorted(os.listdir(OUT)))
