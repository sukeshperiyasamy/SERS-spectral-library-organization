import os,pickle,numpy as np,pandas as pd,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from lib2 import LIB
D=pickle.load(open('lp4.pkl','rb'));df=D['df'];P=D['P'];x=D['x'];BT=D['BT'];core=D['core']
GZ=(x>=1308)&(x<=1455);keep=~GZ
def nz(c): c=c-c[keep].min(); return c/c[keep].max()
OUT=os.path.join(LIB,'04_Figures','LPS_Session_20260928');os.makedirs(OUT,exist_ok=True)
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
PC={60:'#1baf7a',70:'#2a78d6',80:'#9467bd'};GC='#8a8985';FC='#c0392b'
def gz(a): a.axvspan(1308,1455,color=GC,alpha=.13,lw=0)
def save(f,n): f.tight_layout(); f.savefig(os.path.join(OUT,n),dpi=200); plt.close(f)
# P1 raw
f,axs=plt.subplots(2,2,figsize=(10,6.5))
for a,pw in zip(axs.flat[:3],(60,70,80)):
  s=df[(df.power==pw)&(df.category=='LPS_Bulk')]
  for _,r in s.iterrows(): a.plot(x,P[r.key]['p']['ds'],lw=.6,c=PC[pw] if r.QC=='PASS' else (GC if r.QC=='REVIEW' else FC))
  gz(a);a.set_title(f'LPS {pw}% / 30 s / 5 acc — {int((s.QC=="PASS").sum())} pass, {int((s.QC=="REVIEW").sum())} review, {int((s.QC=="FAIL").sum())} fail',loc='left',fontsize=9);a.set_ylabel('Dark-subtracted counts')
a=axs.flat[3]
for pw in (60,70,80):
  for k in df[(df.power==pw)&(df.category=='Glass_Blank')].key: a.plot(x,P[k]['p']['raw'],c=PC[pw],lw=.6)
a.axhline(65535,ls='--',c=FC,lw=.8);gz(a);a.set_title('Matched glass blanks (raw counts; dashed = detector max)',loc='left',fontsize=9)
for a in axs[1]: a.set_xlabel('Raman shift (cm$^{-1}$)')
f.suptitle('Fig. P1  LPS session 28 Sep 2026 as recorded. Coloured = PASS, grey = glass-dominated (review), red = FAIL (ripple)',x=.01,ha='left',fontsize=10)
save(f,'FigP1_Raw_Spectra_and_Blanks.png')
# P2 processed core per power + outliers
f,axs=plt.subplots(2,1,figsize=(10,6.5),sharex=True)
for a,pw in zip(axs,(60,70)):
  s=df[(df.power==pw)&(df.category=='LPS_Bulk')&(df.QC.isin(['PASS','REVIEW']))]
  for _,r in s.iterrows(): a.plot(x,nz(P[r.key]['p']['corr'])+(0 if r.in_core else 1.3),lw=.6,c=PC[pw] if r.in_core else 'k')
  gz(a);a.set_title(f'{pw}%: core spectra (n = {int(s.in_core.sum())}, coloured) and glass-dominated spot (black, offset +1.3)',loc='left');a.set_ylabel('Normalised')
axs[1].set_xlabel('Raman shift (cm$^{-1}$)');axs[1].set_xlim(400,1800)
f.suptitle('Fig. P2  Processed LPS spectra (pipeline v3), normalised outside the glass zone',x=.01,ha='left',fontsize=10)
save(f,'FigP2_Processed_Core_Spectra.png')
# P3 mean/median/sd 70 + 60 with bands
f,axs=plt.subplots(2,1,figsize=(10,7),sharex=True)
cc={'C1':'#1f4e79','C2':'#2e8b57','C3':GC,'C4':'#b8860b'}
for a,pw in zip(axs,(70,60)):
  Nm=np.array([nz(P[k]['p']['corr']) for k in core if k.startswith(str(pw))]);mn,md,sd=Nm.mean(0),np.median(Nm,0),Nm.std(0,ddof=1)
  a.fill_between(x,mn-sd,mn+sd,color=PC[pw],alpha=.25,lw=0,label='mean ± SD');a.plot(x,mn,c=PC[pw],lw=1.1,label=f'mean (n = {len(Nm)})');a.plot(x,md,c='k',lw=.7,ls=':',label='median');gz(a)
  for _,r in BT.iterrows():
    k=np.argmin(abs(x-r.band)); a.annotate(f'{r.band:.0f}',(x[k],mn[k]+sd[k]+.03),rotation=90,fontsize=7,ha='center',va='bottom',color=cc[r['class'][:2]])
  a.set_ylim(-.1,1.9);a.legend(fontsize=7,frameon=False,loc='upper right');a.set_title(f'{pw}% / 30 s / 5 acc',loc='left');a.set_ylabel('Normalised')
axs[1].set_xlabel('Raman shift (cm$^{-1}$)');axs[1].set_xlim(400,1800)
from matplotlib.lines import Line2D
axs[0].legend(handles=axs[0].get_legend_handles_labels()[0]+[Line2D([],[],c=v,marker='s',ls='',label={'C1':'C1 candidate primary','C2':'C2 candidate supporting (weak)','C3':'C3 glass/background','C4':'C4 uncertain'}[k]) for k,v in cc.items()],fontsize=7,frameon=False,loc='upper right',ncol=2)
f.suptitle('Fig. P3  LPS mean, median and SD of the core spectra with candidate bands (labels coloured by category)',x=.01,ha='left',fontsize=10)
save(f,'FigP3_Mean_Median_SD_Bands.png')
# P4 comparison
f,a=plt.subplots(figsize=(10,5))
m70=np.mean([nz(P[k]['p']['corr']) for k in core if k.startswith('70')],0);m60=np.mean([nz(P[k]['p']['corr']) for k in core if k.startswith('60')],0)
bl=np.mean([nz(P[k]['p']['corr']) for k in df[(df.power==60)&(df.category=='Glass_Blank')].key],0)
tr=[(m70,'LPS 28 Sep, 70% (n = 4)',PC[70]),(m60,'LPS 28 Sep, 60% (n = 8)',PC[60]),(nz(D['OLD']),'LPS 13 Apr 2026, 10–20% (library LPS_Bulk)','#eb6834'),(D['NAM'],'NAM reference','k'),(D['LTA'],'LTA preliminary reference','#9467bd'),(np.clip(bl,0,1.2),'Glass blank 60% (clipped)',GC)]
for i,(y,l,c) in enumerate(tr): a.plot(x,y+1.25*(len(tr)-1-i),c=c,lw=.8);a.text(1795,1.25*(len(tr)-1-i)+.55,l,ha='right',fontsize=7,color=c)
gz(a);a.set_yticks([]);a.set_xlim(400,1800);a.set_xlabel('Raman shift (cm$^{-1}$)')
a.set_title('Fig. P4  Comparison: new LPS means versus April LPS data, NAM and LTA references and a glass blank (offset)',loc='left',fontsize=9)
save(f,'FigP4_Comparison_References.png')
print(os.listdir(OUT))
