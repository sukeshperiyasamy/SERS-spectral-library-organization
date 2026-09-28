import sys,os,pickle,numpy as np,pandas as pd,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.path.insert(0,os.path.expanduser('~/work')); from lib2 import *; from lit_v2 import MLIT
from scipy.signal import savgol_filter
B,P,A,G,GZ=pickle.load(open(os.path.expanduser('~/work/v2.pkl'),'rb')); PK=pickle.load(open(os.path.expanduser('~/work/an2.pkl'),'rb'))[0]
D=pickle.load(open(os.path.expanduser('~/work/an4.pkl'),'rb')); MM=D['MM']; g=D['g']
I=lambda i,k:np.interp(X,P[i]['x'],P[i][k])
COL={'NAM':'#2a78d6','LTA':'#eb6834','LPS':'#1baf7a','GLASS':'#8a8985'}; INK='#0b0b0b';INK2='#52514e';GRID='#e4e3df'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5,'axes.edgecolor':INK2,'axes.labelcolor':INK,'xtick.color':INK2,'ytick.color':INK2,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.color':GRID,'grid.linewidth':.6,'savefig.dpi':200})
F=os.path.join(LIB,'04_Figures')
def gz(ax,lab=False): ax.axvspan(X[GZ].min(),X[GZ].max(),color='#8a8985',alpha=.10,lw=0,label='Glass background zone (1308–1455)' if lab else None)
def fw(v): return f'{v:.1f}' if abs(v-round(v))>0.45 else f'{v:.0f}'
cond={'NAM':'90 % / 30 s / 5 acc, 785 nm, 30 May 2026','LTA':'80–95 % / 45 s / 2 acc, 785 nm, 3 Apr 2026'}
i=g['NAM_REF'][0]; r=B.loc[i]; meta,rs,dk,raw,ds=read_any(os.path.join(ROOT,r.orig)); pr=P[i]; x=pr['x']
fig,ax=plt.subplots(4,2,figsize=(9.6,11)); ax=ax.ravel()
m=(rs>-100)&(rs<2000)
ax[0].plot(rs[m],raw[m],color=INK,lw=.7,label='Raw counts'); ax[0].plot(rs[m],dk[m],color=COL['GLASS'],lw=.7,label='Dark frame'); ax[0].axvspan(400,1800,color=COL['NAM'],alpha=.08,lw=0,label='Analysis range 400–1800')
ax[0].set_yscale('log'); ax[0].set_title('1  Raw spectrum (full range, log scale)',loc='left',fontsize=9); ax[0].legend(fontsize=6.5,frameon=False); ax[0].set_ylabel('Counts')
ax[1].plot(x,pr['ds'],color=INK,lw=.7); j=np.argmin(abs(x-1189.5)); ax[1].annotate('fixed hot pixel\n1189.5 cm$^{-1}$',(x[j],pr['ds'][j]),xytext=(25,10),textcoords='offset points',fontsize=7,arrowprops=dict(arrowstyle='->',lw=.6))
ax[1].set_title('2  Cropped to 400–1800 cm$^{-1}$ (dark-subtracted)',loc='left',fontsize=9); ax[1].set_ylabel('Counts')
w=(x>1150)&(x<1230); ax[2].plot(x[w],pr['ds'][w],color='#e34948',lw=1,marker='o',ms=2.5,label='Before'); ax[2].plot(x[w],pr['despiked'][w],color=INK,lw=1.2,label='After hot-pixel / spike correction')
ax[2].set_title('3  Hot-pixel + spike removal (zoom)',loc='left',fontsize=9); ax[2].legend(fontsize=6.5,frameon=False)
w=(x>900)&(x<985); ax[3].plot(x[w],pr['despiked'][w],color=INK2,lw=.8,marker='o',ms=2,label='Despiked'); ax[3].plot(x[w],pr['smooth'][w],color=COL['NAM'],lw=1.4,label='Savitzky–Golay 11/3')
ax[3].set_title('4  Smoothing preserves peak position/shape (zoom)',loc='left',fontsize=9); ax[3].legend(fontsize=6.5,frameon=False)
ax[4].plot(x,pr['smooth'],color=INK,lw=.7,label='Smoothed'); ax[4].plot(x,pr['base'],color='#eda100',lw=1.5,label='ALS baseline (λ=1e5, p=0.01)'); ax[4].legend(fontsize=6.5,frameon=False)
ax[4].set_title('5  ALS baseline estimate',loc='left',fontsize=9); ax[4].set_ylabel('Counts')
ax[5].plot(x,pr['corr'],color=COL['NAM'],lw=.9); gz(ax[5],True); ax[5].legend(fontsize=6.5,frameon=False); ax[5].set_title('6  Baseline-corrected (counts retained)',loc='left',fontsize=9); ax[5].set_ylabel('Counts')
ax[6].plot(x,pr['norm'],color=COL['NAM'],lw=.9); ax[6].set_title('7  Min–max normalised (shape comparison only)',loc='left',fontsize=9); ax[6].set_ylabel('Normalised (0–1)')
res=pr['despiked']-pr['smooth']; ax[7].hist(res,bins=80,color=COL['GLASS']); ax[7].axvline(pr['noise'],color=INK,lw=.8,ls='--'); ax[7].axvline(-pr['noise'],color=INK,lw=.8,ls='--')
ax[7].set_title(f'8  Noise: robust SD of residual = {pr["noise"]:.1f} counts; SNR = {r.snr:.1f}',loc='left',fontsize=9); ax[7].set_xlabel('Residual (despiked − smoothed), counts'); ax[7].set_xlim(-6*pr['noise'],6*pr['noise'])
for a in ax[:7]: a.set_xlabel('Raman shift (cm$^{-1}$)')
fig.suptitle(f'Figure 1. Preprocessing pipeline applied to one NAM reference spectrum ({r.new_name_raw})',fontsize=10,x=0.01,ha='left')
plt.tight_layout(); plt.savefig(os.path.join(F,'Fig01_Preprocessing_Pipeline_Steps.png')); plt.close()
fig,ax=plt.subplots(2,1,figsize=(8,6.6),sharex=True)
for k in g['NAM_REF']:
  same='samespot' in B.orig[k]; ax[0].plot(X,I(k,'corr'),lw=.6,color=COL['NAM'] if not same else '#9fc3ee',alpha=.9)
ax[0].plot([],[],color=COL['NAM'],label='Different points (n = 5)'); ax[0].plot([],[],color='#9fc3ee',label='Same spot, repeated (n = 10)'); gz(ax[0],True)
ax[0].legend(fontsize=7,frameon=False); ax[0].set_ylabel('Counts (baseline-corrected)'); ax[0].set_title('(a) Reference group, 90 % / 30 s / 5 acc (n = 15; 30 May 2026)',loc='left',fontsize=9)
Mr=MM['NAM_REF']['mean']; Mr=Mr/Mr.max()
for k in g['NAM_VAL_70_10_5_diffpoint']: ax[1].plot(X,I(k,'norm'),lw=.6,color='#86b4ec')
ax[1].plot(X,Mr,color=INK,lw=1.1,label='Reference mean (normalised)'); ax[1].plot([],[],color='#86b4ec',label='Independent spots, 70 % / 10 s / 5 acc (n = 10)'); gz(ax[1])
ax[1].legend(fontsize=7,frameon=False); ax[1].set_ylabel('Normalised'); ax[1].set_xlabel('Raman shift (cm$^{-1}$)'); ax[1].set_xlim(400,1800)
ax[1].set_title('(b) Independent-spot validation set vs reference mean (29–30 May 2026)',loc='left',fontsize=9)
fig.suptitle('Figure 2. All valid NAM bulk spectra used for the reference and its independent-spot validation',fontsize=10,x=0.01,ha='left')
plt.tight_layout(); plt.savefig(os.path.join(F,'Fig02_NAM_All_Valid_Spectra.png')); plt.close()
def meanmed(a,key,num,title):
  mm=MM[key]; mean,med,sd=mm['mean'],mm['median'],mm['sd']; n=len(mm['idx'])
  fig,ax=plt.subplots(2,1,figsize=(8,6),sharex=True,gridspec_kw=dict(height_ratios=[2.2,1]))
  gz(ax[0],True); ax[0].fill_between(X,mean-sd,mean+sd,color=COL[a],alpha=.18,lw=0,label='Mean ± 1 SD')
  ax[0].plot(X,mean,color=COL[a],lw=1.4,label=f'Mean (n = {n})'); ax[0].plot(X,med,color=INK,lw=.8,ls='--',label='Median')
  for _,p in PK[(PK.analyte==a)].iterrows():
    j=np.argmin(abs(X-p.pos_mean))
    if p.role=='Primary marker': ax[0].annotate(fw(p.pos_mean),(X[j],mean[j]+sd[j]),xytext=(0,3),textcoords='offset points',ha='center',fontsize=7.5,fontweight='bold')
    elif p.role=='Supporting peak': ax[0].plot(X[j],mean[j]+sd[j]+0.03*mean.max(),'o',ms=3.5,mfc='white',mec=INK2)
  ax[0].plot([],[],'o',ms=3.5,mfc='white',mec=INK2,label='Supporting peak'); ax[0].legend(fontsize=7,frameon=False,ncol=2); ax[0].set_ylabel('Counts (baseline-corrected)')
  ax[0].set_title(f'(a) {cond[a]}; primary markers labelled',loc='left',fontsize=9)
  ax[1].fill_between(X,-sd,sd,color=COL['GLASS'],alpha=.25,lw=0,label='± 1 SD'); ax[1].plot(X,mean-med,color=INK,lw=.8,label='Mean − median'); ax[1].axhline(0,color=INK2,lw=.5)
  ax[1].legend(fontsize=7,frameon=False); ax[1].set_ylabel('Counts'); ax[1].set_xlabel('Raman shift (cm$^{-1}$)'); ax[1].set_xlim(400,1800)
  r_=np.corrcoef(mean,med)[0,1]; ax[1].set_title(f'(b) Mean − median lies inside ±1 SD everywhere; r(mean, median) = {r_:.4f}',loc='left',fontsize=9)
  fig.suptitle(title,fontsize=10,x=0.01,ha='left'); plt.tight_layout(); plt.savefig(os.path.join(F,f'Fig0{num}_{a}_Mean_vs_Median_SD.png')); plt.close()
meanmed('NAM','NAM_REF',3,'Figure 3. NAM bulk reference — mean vs median spectrum with SD envelope (interim reference, n = 15)')
fig,ax=plt.subplots(figsize=(8,3.8)); gz(ax,True)
for k in g['LTA_ALLVALID']:
  ref=B.in_reference[k]; ax.plot(X,I(k,'corr'),lw=1.0 if ref else .6,color=COL['LTA'] if ref else '#f6b89b')
ax.plot([],[],color=COL['LTA'],label='Reference group 80–95 % / 45 s / 2 acc (n = 4)'); ax.plot([],[],color='#f6b89b',label='Other valid: 40–70 % / 10 s / 10 acc and 60 % / 45 s (n = 5)')
ax.legend(fontsize=7,frameon=False); ax.set_xlim(400,1800); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('Counts (baseline-corrected)')
ax.set_title('Figure 4. All valid LTA bulk spectra (3 Apr 2026, glass slide, 785 nm)',loc='left',fontsize=10)
plt.tight_layout(); plt.savefig(os.path.join(F,'Fig04_LTA_All_Valid_Spectra.png')); plt.close()
meanmed('LTA','LTA_REF',5,'Figure 5. LTA bulk PRELIMINARY reference — mean vs median with SD envelope (n = 4)')
L=B[B.cls=='LPS']; gl=B[B.cls=='GLASS']
fig,ax=plt.subplots(3,1,figsize=(8,8),sharex=True)
for k in L.index: ax[0].plot(X,I(k,'ds'),color=COL['LPS'],lw=.5,alpha=.6)
for k in gl.index: ax[0].plot(X,I(k,'ds'),color=COL['GLASS'],lw=.9)
ax[0].plot([],[],color=COL['LPS'],label='LPS bulk, 10–20 % power, 10–60 s (n = 14; 13 Apr 2026)'); ax[0].plot([],[],color=COL['GLASS'],label='Empty glass slide, 5 % / 5 s / 1 acc (n = 5; 29 May 2026)')
ax[0].legend(fontsize=7,frameon=False); ax[0].set_ylabel('Dark-subtracted counts'); ax[0].set_title('(a) As measured',loc='left',fontsize=9)
gz(ax[1])
for k in L.index: ax[1].plot(X,I(k,'norm'),color=COL['LPS'],lw=.5,alpha=.55)
ax[1].plot(X,G,color=COL['GLASS'],lw=2,label='Glass blank mean (normalised)'); ax[1].legend(fontsize=7,frameon=False); ax[1].set_ylabel('Normalised'); ax[1].set_title('(b) Normalised: dominant band coincides with the glass blank',loc='left',fontsize=9)
Lc=np.array([I(k,'corr')-max(np.dot(I(k,'corr')[GZ],G[GZ])/np.dot(G[GZ],G[GZ]),0)*G for k in L.index])
ax[2].fill_between(X,Lc.mean(0)-Lc.std(0,ddof=1),Lc.mean(0)+Lc.std(0,ddof=1),color=COL['LPS'],alpha=.2,lw=0); ax[2].plot(X,Lc.mean(0),color=COL['LPS'],lw=1.2,label='LPS after glass-template subtraction (mean ± SD)')
ax[2].axhline(0,color=INK2,lw=.6); ax[2].legend(fontsize=7,frameon=False); ax[2].set_ylabel('Counts'); ax[2].set_xlabel('Raman shift (cm$^{-1}$)'); ax[2].set_xlim(400,1800)
ax[2].set_title('(c) Exploratory only (blank not matched): no reproducible LPS band remains',loc='left',fontsize=9)
fig.suptitle('Figure 6. LPS bulk spectra and empty glass-slide blanks — no LPS reference established',fontsize=10,x=0.01,ha='left')
plt.tight_layout(); plt.savefig(os.path.join(F,'Fig06_LPS_and_Glass_Blanks.png')); plt.close()
fig,ax=plt.subplots(figsize=(8,5)); off=0; gz(ax)
items=[('Glass blank (empty slide; background, not a biomarker)',G,COL['GLASS'],None),('LPS — NO REFERENCE (pending controlled glass-slide measurement)',None,COL['LPS'],None),
 ('LTA — PRELIMINARY reference (n = 4), mean',MM['LTA_REF']['mean']/MM['LTA_REF']['mean'].max(),COL['LTA'],'LTA'),('NAM — interim reference (n = 15), mean',MM['NAM_REF']['mean']/MM['NAM_REF']['mean'].max(),COL['NAM'],'NAM')]
for lab,y,c,a in items:
  if y is None: ax.text(900,off+0.4,'no reference spectrum',fontsize=8,color=c,ha='center')
  else: ax.plot(X,y+off,color=c,lw=1.3)
  ax.text(402,off+0.95,lab,fontsize=7.5,color=INK)
  if a:
    for _,p in PK[(PK.analyte==a)&(PK.role=='Primary marker')].iterrows():
      j=np.argmin(abs(X-p.pos_mean)); ax.plot(X[j],y[j]+off+0.05,'v',ms=4,color=c)
  off+=1.2
ax.set_yticks([]); ax.set_xlim(400,1800); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('Normalised intensity (offset)')
ax.set_title('Figure 7. Current reference spectra (▼ primary markers; grey band = glass zone)',loc='left',fontsize=10)
plt.tight_layout(); plt.savefig(os.path.join(F,'Fig07_Reference_Spectra_NAM_LTA_LPS.png')); plt.close()
rowsL=[('NAM',541,(400,600)),('NAM',830,(800,950)),('NAM',870,(800,950)),('NAM',929,(800,950)),('NAM',955,(800,950)),('NAM',1023,(1000,1200)),('NAM',1127,(1000,1200)),
 ('LTA',802,(808,818)),('LTA',861,(800,950)),('LTA',1092,(1088,1097)),('LTA',1459,(1440,1460))]
fig,ax=plt.subplots(figsize=(8,5.2))
for k,(a,m,(lo,hi)) in enumerate(rowsL[::-1]):
  p=PK[(PK.analyte==a)&(PK.nominal==m)].iloc[0]; y=k
  ax.add_patch(Rectangle((lo,y-0.3),hi-lo,0.6,color='#c3c2b7',alpha=.6,lw=0))
  ax.errorbar(p.pos_mean,y,xerr=max(p.pos_sd,0.5),fmt='o',ms=5,color=COL[a],ecolor=INK,capsize=2)
  ax.text(1605,y,f'{a} {fw(p.pos_mean)} ({p.role.split()[0].lower()}) — {MLIT[(a,m)][7]}',va='center',fontsize=7)
ax.scatter([894,1333],[-1,-1],marker='x',color=INK2,s=25,label='SERS LTA bands [L2] (not comparable to bulk)'); ax.text(1605,-1,'LTA SERS bands 894, 1333 [L2]',va='center',fontsize=7,color=INK2)
ax.add_patch(Rectangle((0,0),0,0,color='#c3c2b7',alpha=.6,label='Literature band / group-frequency region [L5–L7]'))
ax.plot([],[],'o',color=INK2,label='Experimental band (mean ± SD)')
ax.axvspan(X[GZ].min(),X[GZ].max(),color='#8a8985',alpha=.08,lw=0)
ax.set_yticks([]); ax.set_xlim(380,1960); ax.set_xticks(range(400,1601,200)); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.legend(fontsize=7,frameon=False,loc='lower left')
ax.set_title('Figure 8. Final marker peaks vs literature (text = confidence of the proposed assignment)',loc='left',fontsize=10)
plt.tight_layout(); plt.savefig(os.path.join(F,'Fig08_Marker_Peaks_vs_Literature.png')); plt.close()
fig=plt.figure(figsize=(9.5,7.5)); gs=fig.add_gridspec(2,3)
for c_,key,t in [(0,'NAM_REF','NAM reference (n = 15)'),(1,'LTA_REF','LTA reference (n = 4)')]:
  N=MM[key]['N']; Rm=np.corrcoef(N[:,~GZ]); axh=fig.add_subplot(gs[0,c_]); im=axh.imshow(Rm,vmin=0.9,vmax=1,cmap='Blues'); axh.set_title(f'({"ab"[c_]}) Pearson r, {t}',loc='left',fontsize=8.5); axh.grid(False); axh.set_xticks(range(len(N))); axh.set_yticks(range(len(N))); axh.tick_params(labelsize=6)
  plt.colorbar(im,ax=axh,fraction=.046); axh.set_xlabel('Spectrum'); axh.set_ylabel('Spectrum')
axs=fig.add_subplot(gs[0,2])
for k,(cls,key) in enumerate([('NAM','NAM_REF'),('LTA','LTA_REF'),('NAM','NAM_VAL_70_10_5_diffpoint')]):
  s=B.loc[g[key],'snr']; axs.scatter([k]*len(s),s,color=COL[cls],s=14,alpha=.8)
axs.axhline(10,color=INK2,ls='--',lw=.8); axs.set_xticks([0,1,2]); axs.set_xticklabels(['NAM ref','LTA ref','NAM indep.\n70/10/5'],fontsize=7); axs.set_ylabel('SNR'); axs.set_title('(c) SNR per spectrum (--- acceptance 10)',loc='left',fontsize=8.5)
axc=fig.add_subplot(gs[1,:]); pk=PK[PK.role.isin(['Primary marker','Supporting peak'])].copy(); pk['lab']=pk.analyte+' '+pk.pos_mean.map(fw)
cols=[COL[a] if r_=='Primary marker' else '#c3c2b7' for a,r_ in zip(pk.analyte,pk.role)]
axc.bar(range(len(pk)),pk.cv,color=cols); axc.axhline(15,color=INK2,ls='--',lw=.8); axc.set_xticks(range(len(pk))); axc.set_xticklabels(pk.lab,rotation=45,fontsize=7,ha='right')
axc.set_ylabel('Intensity CV (%)'); axc.set_title('(d) Intensity CV of primary (coloured) and supporting (grey) peaks; --- 15 % criterion',loc='left',fontsize=8.5)
fig.suptitle('Figure 9. QC and reproducibility of the reference groups',fontsize=10,x=0.01,ha='left')
plt.tight_layout(); plt.savefig(os.path.join(F,'Fig09_QC_and_Reproducibility.png')); plt.close()
for a,key in [('NAM','NAM_REF'),('LTA','LTA_REF')]:
  mm=MM[key]; R=B.loc[mm['idx']]; d=os.path.join(LIB,'03_Reference_Spectra',a); N=mm['N']
  t=pd.DataFrame({'Raman_Shift_cm-1':X,'BaselineCorrected_mean_counts':mm['mean'].round(2),'BaselineCorrected_median_counts':mm['median'].round(2),'BaselineCorrected_SD_counts':mm['sd'].round(2),
     'DarkSubtracted_mean_counts':np.mean([I(k,'ds') for k in mm['idx']],0).round(2),'Normalised_mean':N.mean(0).round(5),'Normalised_median':np.median(N,0).round(5),'Normalised_SD':N.std(0,ddof=1).round(5)})
  status='INTERIM reference (5 independent spots + 10 same-spot repeats); top-up with >=10 independent spots recommended' if a=='NAM' else 'PRELIMINARY reference (n = 4); re-acquisition of 10-15 independent spots required'
  with open(os.path.join(d,f'{a}_Bulk_Reference_Mean_SD.csv'),'w') as fh:
    fh.write(f'# {a} bulk powder on glass slide - {status}\n# Condition: {cond[a]}; pipeline v3; representative spectrum = MEAN (median agrees)\n# Members: '+'; '.join(R.new_name)+'\n'); t.to_csv(fh,index=False)
  pd.DataFrame({'library_file':R.new_name,'original_file':R.orig,'date':R.date,'spot':R.spot_type,'power_pct':R.power,'int_s':R.int_s,'acc':R.acc,'SNR':R.snr.round(1)}).to_csv(os.path.join(d,f'{a}_Reference_Members.csv'),index=False)
  PK[PK.analyte==a][['role','nominal','pos_mean','pos_sd','height_mean','height_sd','cv','snr_mean','prom_mean','n_detected','n','glass_zone']].round(2).to_csv(os.path.join(d,f'{a}_Reference_Marker_Peaks.csv'),index=False)
print('ok')
