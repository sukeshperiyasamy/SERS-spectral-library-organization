import os,pickle,numpy as np,pandas as pd,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from lib2 import LIB
D=pickle.load(open('lr2.pkl','rb'));E=pickle.load(open('lr3.pkl','rb'));BT=pickle.load(open('lr6.pkl','rb'));df=pickle.load(open('lr7_df.pkl','rb'));G5=pickle.load(open('lr5.pkl','rb'))
P=D['P'];x=D['x'];ks=E['ks'];fin=E['fin']
GZ=(x>=1308)&(x<=1455);keep=~GZ
def nz(c): c=c-c[keep].min(); return c/c[keep].max()
OUT=os.path.join(LIB,'04_Figures','LPS_Reference_20260928');os.makedirs(OUT,exist_ok=True)
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
LC='#1baf7a';GC='#8a8985';FC='#c0392b'
def gz(a): a.axvspan(1308,1455,color=GC,alpha=.13,lw=0)
def save(f,n): f.tight_layout();f.savefig(os.path.join(OUT,n),dpi=200);plt.close(f)
cc={'C1':'#1f4e79','C2':'#2e8b57','C3':GC,'C4':'#b8860b'}
# R1 raw + processed
f,ax=plt.subplots(2,1,figsize=(10,7.5),sharex=True)
for k in fin.library_file:
  p=P[k]['p'];ok=k in ks
  ax[0].plot(x,p['ds'],c=LC if ok else FC,lw=.6); ax[1].plot(x,nz(p['corr'])+(0 if ok else 1.4),c=LC if ok else FC,lw=.6)
for a in ax: gz(a)
ax[0].set_ylabel('Dark-subtracted counts');ax[0].set_title('A. As recorded (green = 10 reference spectra, red = S13 excluded, glass-dominated)',loc='left')
ax[1].set_ylabel('Normalised');ax[1].set_title('B. Processed (pipeline v3), normalised outside the glass zone; S13 offset +1.4',loc='left');ax[1].set_xlabel('Raman shift (cm$^{-1}$)');ax[1].set_xlim(400,1800)
f.suptitle('Fig. R1  LPS reference set, 60 % / 40 s / 5 acc (E. coli O111:B4, Sigma L2630)',x=.01,ha='left',fontsize=10);save(f,'FigR1_LPS_Reference_Spectra_All.png')
# R2 mean/median/SD with bands
f,a=plt.subplots(figsize=(10,4.8));mn,md,sd=E['mn'],E['md'],E['sd']
a.fill_between(x,mn-sd,mn+sd,color=LC,alpha=.25,lw=0,label='mean ± SD');a.plot(x,mn,c=LC,lw=1.2,label='mean (n = 10)');a.plot(x,md,c='k',lw=.7,ls=':',label='median');gz(a)
for _,r in BT.iterrows():
  j=np.argmin(abs(x-r.band));a.annotate(f'{r.band:.0f}',(x[j],mn[j]+sd[j]+.03),rotation=90,fontsize=7,ha='center',va='bottom',color=cc[r['class'][:2]])
h=[Line2D([],[],c=v,marker='s',ls='',label=l) for v,l in ((cc['C1'],'C1 primary marker'),(cc['C2'],'C2 supporting'),(cc['C4'],'C4 uncertain'),(cc['C3'],'C3 glass/background'))]
a.legend(handles=a.get_legend_handles_labels()[0]+h,fontsize=7,frameon=False,ncol=2,loc='upper right');a.set_ylim(-.1,1.9);a.set_xlim(400,1800);a.set_xlabel('Raman shift (cm$^{-1}$)');a.set_ylabel('Normalised intensity')
a.set_title('Fig. R2  LPS bulk reference spectrum: mean, median, SD and classified bands',loc='left');save(f,'FigR2_LPS_Reference_Mean_Median_SD_Bands.png')
# R3 glass analysis
f,ax=plt.subplots(2,1,figsize=(10,6.5),sharex=True)
for i in (1,2): ax[0].plot(x,P[f'Glass_Blank_20260928_P060pct_T05s_A01_S0{i}_short.csv']['raw'][(P[ks[0]]['rs']>=400)&(P[ks[0]]['rs']<=1800)],c=GC,lw=.7,label='short blank 5 s/1 acc (unsaturated)' if i==1 else None)
for n in ('S01','S02','S03'): ax[0].plot(x,P[f'Glass_Blank_20260928_P060pct_T40s_A05_{n}.csv']['p']['raw'],c='#9467bd',lw=.6,label='matched blanks 40 s/5 acc' if n=='S01' else None)
ax[0].axhline(65535,ls='--',c=FC,lw=.7);ax[0].set_yscale('log');ax[0].legend(fontsize=7,frameon=False);ax[0].set_ylabel('Raw counts (log)');ax[0].set_title('A. Glass blanks: the short blank records the full glass band without saturation',loc='left')
R=np.array([G5['res'][k] for k in ks]);Cm=np.array([P[k]['p']['corr'] for k in ks])
s=Cm.max(axis=1,keepdims=True)
ax[1].plot(x,(Cm/s).mean(0),c=LC,lw=1,label='LPS mean (as processed)');ax[1].plot(x,(R/s).mean(0)-.5,c='#1f4e79',lw=1,label='after subtracting scaled glass shape (offset -0.5)')
ax[1].plot(x,G5['G']*np.mean([G5['A'][k]/s[i,0] for i,k in enumerate(ks)]),c=GC,lw=.8,ls='--',label='fitted glass contribution')
gz(ax[1]);ax[1].legend(fontsize=7,frameon=False);ax[1].set_xlabel('Raman shift (cm$^{-1}$)');ax[1].set_xlim(400,1800);ax[1].set_ylabel('Scaled intensity')
ax[1].set_title('B. Exploratory glass removal: glass explains the 1300–1450 hump and ~14 % of the 1080 band; 425 cm$^{-1}$ unaffected',loc='left')
f.suptitle('Fig. R3  Glass-background characterisation',x=.01,ha='left',fontsize=10);save(f,'FigR3_Glass_Blanks_and_Glass_Removal.png')
# R4 dark verification + intensity
f,ax=plt.subplots(1,2,figsize=(11,3.8))
t=pd.to_datetime(fin.acq);ax[0].scatter(t,fin.dark_med,c=[LC if k in ks else FC for k in fin.library_file],s=25,label='dark used for LPS spectra')
ch=df[df.library_file.str.contains('T40s_A05_ShutterClosed')];ax[0].scatter(pd.to_datetime(ch.acq),ch.raw_med,marker='s',c='k',s=30,label='shutter-closed check frames (true dark)')
ax[0].axhline(D['true40'],ls='--',c='k',lw=.7);ax[0].set_ylabel('Median counts (400–1800 cm$^{-1}$)');ax[0].legend(fontsize=7,frameon=False);ax[0].set_title('A. Dark level vs true dark (40 s × 5)',loc='left');ax[0].tick_params(axis='x',rotation=30)
m=fin[fin.library_file.isin(ks)];lab=[k[-7:-4] for k in m.library_file]
ax[1].bar(lab,m.h425,color=LC,label='as recorded');ax[1].bar(lab,m.h425*(m.intensity_factor-1),bottom=m.h425,color='#b8e6d2',label='estimated under-estimate (dark light)')
ax[1].set_ylabel('425 cm$^{-1}$ band height (counts)');ax[1].legend(fontsize=7,frameon=False);ax[1].set_title('B. Bulk intensity per spot (3–5× spread from focus/packing)',loc='left')
f.suptitle('Fig. R4  Dark verification and bulk intensity',x=.01,ha='left',fontsize=10);save(f,'FigR4_Dark_Check_and_Intensity.png')
# R5 comparison
Rf=pickle.load(open('lp4.pkl','rb'));m60=D['m60']
f,a=plt.subplots(figsize=(10,5.2))
tr=[(mn,'LPS reference 28 Sep (60 %/40 s/5 acc, n = 10)',LC),(m60,'LPS screening 28 Sep (60 %/30 s/5 acc, n = 8)','#2a78d6'),(nz(D['OLD']),'LPS April 2026 (10–20 %)','#eb6834'),(D['LTA'],'LTA preliminary reference','#9467bd'),(D['NAM'],'NAM reference','k')]
for i,(y,l,c) in enumerate(tr): a.plot(x,y+1.25*(len(tr)-1-i),c=c,lw=.8);a.text(1795,1.25*(len(tr)-1-i)+.6,l,ha='right',fontsize=7,color=c)
for b in (425,1080): a.axvline(b,c=cc['C1'],lw=.6,ls=':')
gz(a);a.set_yticks([]);a.set_xlim(400,1800);a.set_xlabel('Raman shift (cm$^{-1}$)')
a.set_title('Fig. R5  LPS reference compared with earlier LPS data and the NAM and LTA references (offset; dotted = LPS primary markers)',loc='left',fontsize=9);save(f,'FigR5_LPS_vs_Other_References.png')
print(sorted(os.listdir(OUT)))
