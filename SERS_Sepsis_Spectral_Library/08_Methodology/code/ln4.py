import pickle,os,numpy as np,pandas as pd,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from lib2 import LIB
N=pickle.load(open('ln1.pkl','rb'));Q=pickle.load(open('ln3.pkl','rb'));OLD=pickle.load(open('ln2_old.pkl','rb'))
df=N['df'];P=N['P'];x=N['x'];BT=Q['BT'];CMP=Q['CMP'];refmean=Q['refmean']
OUT=os.path.join(LIB,'04_Figures','NAM_Session_20260924');os.makedirs(OUT,exist_ok=True)
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
PC={60:'#1baf7a',70:'#2a78d6',80:'#9467bd',90:'#eb6834'};GC='#8a8985';FC='#c0392b';RC='#222222'
GZ=(x>=1308)&(x<=1455);keep=~GZ
def gz(a): a.axvspan(1308,1455,color=GC,alpha=.13,lw=0)
def nz(c): c=c-c[keep].min(); return c/c[keep].max()
def save(f,n): f.tight_layout(); f.savefig(os.path.join(OUT,n),dpi=200); plt.close(f)
df['t']=pd.to_datetime(df.acq_time)
# N1
f,ax=plt.subplots(2,1,figsize=(9,5.5),sharex=True)
for pw in (60,70,80,90):
  s=df[df.power==pw]
  for cat,mk in (('NAM_Bulk','o'),('Glass_Blank','s')):
    q=s[s.category==cat]; ax[0].scatter(q.t,q.dark_median,c=PC[pw],marker=mk,s=22,label=f'{pw}% {"NAM" if cat=="NAM_Bulk" else "blank"}')
    if cat=='NAM_Bulk':
      ok=q[q.QC=='PASS'];bad=q[q.QC!='PASS'];ax[1].scatter(ok.t,ok.ripple_ds,c=PC[pw],s=22);ax[1].scatter(bad.t,bad.ripple_ds,facecolors='none',edgecolors=PC[pw],s=30,lw=1.2)
ax[0].set_ylabel('Dark-frame median (counts)');ax[0].legend(ncol=4,fontsize=7,frameon=False)
ax[1].axhline(50,ls='--',c=FC,lw=.8);ax[1].set_ylabel('Residual ripple 1550–1800 cm$^{-1}$\n(filled = PASS, open = FAIL)');ax[1].set_xlabel('Acquisition time, 24 Sep 2026 (instrument clock)')
ax[0].set_title('Fig. N1  Dark-frame level and residual ripple over the NAM session',loc='left')
save(f,'FigN1_Session_Timeline_Dark_and_Ripple.png')
# N2
f,axs=plt.subplots(2,2,figsize=(10,6.5),sharex=True)
for a,pw in zip(axs.flat,(60,70,80,90)):
  s=df[(df.power==pw)&(df.category=='NAM_Bulk')]
  for _,rw in s.iterrows(): p=P[rw.library_file]['p'];a.plot(p['x'],p['ds'],lw=.6,c=PC[pw] if rw.QC=='PASS' else FC,alpha=.85)
  gz(a);a.set_title(f'{pw}% / 30 s / 5 acc — {int((s.QC=="PASS").sum())}/{len(s)} PASS',loc='left');a.set_ylabel('Dark-subtracted counts')
for a in axs[1]: a.set_xlabel('Raman shift (cm$^{-1}$)')
f.suptitle('Fig. N2  NAM spectra as recorded (dark-subtracted). Coloured = PASS, red = FAIL (ripple)',x=.01,ha='left',fontsize=10)
save(f,'FigN2_Raw_Spectra_by_Power.png')
# N3 blanks
f,a=plt.subplots(figsize=(9,4))
for pw in (60,70,80,90):
  for _,rw in df[(df.power==pw)&(df.category=='Glass_Blank')].iterrows(): a.plot(P[rw.library_file]['p']['x'],P[rw.library_file]['p']['raw'],c=PC[pw],lw=.7)
a.axhline(65535,ls='--',c=FC,lw=.8);a.text(410,66500,'detector maximum 65 535 counts',color=FC,fontsize=7);gz(a);a.set_xlim(400,1800)
a.set_ylabel('Raw counts');a.set_xlabel('Raman shift (cm$^{-1}$)');a.set_title('Fig. N3  Matched empty-glass blanks (16): all saturate across the glass band',loc='left')
save(f,'FigN3_Glass_Blanks_Saturation.png')
# N4 ripple
f,axs=plt.subplots(1,2,figsize=(10,3.6))
for a,name,t in zip(axs,('NAM_Bulk_20260924_P070pct_T30s_A05_S02.csv','NAM_Bulk_20260924_P090pct_T30s_A05_S02.csv'),('PASS: 70% S02','FAIL: 90% S02')):
  q=P[name]; m=(q['rs']>1500)&(q['rs']<1800)
  a.plot(q['rs'][m],q['raw'][m]-np.median(q['raw'][m]),c='k',lw=.7,label='raw (offset)');a.plot(q['rs'][m],q['dk'][m]-np.median(q['dk'][m]),c=GC,lw=.7,label='dark frame (offset)')
  a.plot(q['rs'][m],q['ds'][m]-np.median(q['ds'][m])-1500,c=FC,lw=.8,label='raw − dark (offset −1500)');a.set_title(t,loc='left');a.set_xlabel('Raman shift (cm$^{-1}$)')
axs[0].legend(fontsize=7,frameon=False);axs[0].set_ylabel('Counts (offset)')
f.suptitle('Fig. N4  Fixed-pattern detector ripple cancels only when raw and dark frames match',x=.01,ha='left',fontsize=10)
save(f,'FigN4_Ripple_Diagnostic.png')
# N5 new pass per power vs reference
f,axs=plt.subplots(4,1,figsize=(9,10),sharex=True)
for a,pw in zip(axs,(60,70,80,90)):
  L=Q['sets'][f'NEW_{pw}_24Sep']
  for fl in L: a.plot(x,nz(P[fl]['p']['corr']),c=PC[pw],lw=.6,alpha=.8)
  a.plot(x,refmean,c=RC,lw=.9,ls='--',label='NAM reference mean (90%/30 s/5 acc, 30 May 2026, n = 15)');gz(a);a.set_title(f'24 Sep 2026, {pw}%: QC-passed spectra (n = {len(L)})',loc='left');a.set_ylabel('Normalised')
axs[0].legend(fontsize=7,frameon=False,loc='upper right');axs[-1].set_xlabel('Raman shift (cm$^{-1}$)');axs[-1].set_xlim(400,1800)
f.suptitle('Fig. N5  New independent-spot NAM spectra overlaid on the existing NAM reference',x=.01,ha='left',fontsize=10)
save(f,'FigN5_New_PASS_Spectra_vs_Reference.png')
# N6 means + difference
f,ax=plt.subplots(2,1,figsize=(10,6),sharex=True,gridspec_kw=dict(height_ratios=[2.2,1]))
oldsd=np.array([nz(v['p']['corr']) for v in OLD.values()]).std(0,ddof=1)
ax[0].fill_between(x,refmean-oldsd,refmean+oldsd,color=GC,alpha=.35,lw=0,label='reference ± SD');ax[0].plot(x,refmean,c=RC,lw=1,label='reference mean (30 May, 90%)')
for pw in (60,70,80):
  m=np.mean([nz(P[f]['p']['corr']) for f in Q['sets'][f'NEW_{pw}_24Sep']],0); ax[0].plot(x,m,c=PC[pw],lw=.9,label=f'new mean {pw}% (n = {len(Q["sets"][f"NEW_{pw}_24Sep"])})')
  ax[1].plot(x,m-refmean,c=PC[pw],lw=.8)
ax[1].fill_between(x,-oldsd,oldsd,color=GC,alpha=.35,lw=0);ax[1].axhline(0,c='k',lw=.5)
for a in ax: gz(a)
ax[0].legend(fontsize=7,frameon=False,ncol=2);ax[0].set_ylabel('Normalised');ax[1].set_ylabel('New − reference');ax[1].set_xlabel('Raman shift (cm$^{-1}$)');ax[1].set_xlim(400,1800)
ax[0].set_title('Fig. N6  Old reference versus new session: mean spectra (top) and difference (bottom; grey = reference ± SD)',loc='left')
save(f,'FigN6_Old_vs_New_Mean_Spectra.png')
# N7 marker validation
C=CMP[CMP.set=='NEW_all_pass_24Sep'].reset_index(drop=True)
f,ax=plt.subplots(1,2,figsize=(11,4))
col=[GC if g else ({'Primary marker':'#1f4e79','Supporting peak':'#2e8b57'}.get(r,'#b8860b')) for r,g in zip(C.role,C.glass_zone)]
lab=[f'{v:.0f}' for v in C.ref_pos]
ax[0].bar(range(len(C)),C.dpos,color=col);ax[0].axhspan(-1.8,1.8,color='#dfe9f5',zorder=0);ax[0].set_ylabel('Δ position new − reference (cm$^{-1}$)')
ax[0].text(len(C)-.5,1.9,'± 1 detector pixel (≈1.8 cm$^{-1}$)',ha='right',fontsize=7)
ax[1].bar(range(len(C)),C.rel_change_pct,color=col);ax[1].axhspan(-15,15,color='#dfe9f5',zorder=0);ax[1].set_ylabel('Change in relative intensity (I/I$_{929}$), %')
for a in ax: a.set_xticks(range(len(C)));a.set_xticklabels(lab,rotation=90,fontsize=7);a.axhline(0,c='k',lw=.5);a.set_xlabel('Reference band (cm$^{-1}$)')
ax[1].legend(handles=[Line2D([],[],c=c,marker='s',ls='',label=l) for c,l in (('#1f4e79','primary'),('#2e8b57','supporting'),('#b8860b','uncertain'),(GC,'glass zone'))],fontsize=7,frameon=False)
f.suptitle('Fig. N7  Marker validation, all 21 new QC-passed spectra: position shift (left) and relative-intensity change (right)',x=.01,ha='left',fontsize=10)
save(f,'FigN7_Marker_Validation.png')
# N8 intensity vs power
f,ax=plt.subplots(1,2,figsize=(10,3.8))
s=df[(df.category=='NAM_Bulk')]
for _,rw in s.iterrows(): ax[0].scatter(rw.power+np.random.uniform(-1,1),rw.h929_counts,c=PC[rw.power] if rw.QC=='PASS' else 'none',edgecolors=PC[rw.power],s=22)
r=BT[(BT.set=='REF_90_30May_all15')&(BT.ref_pos==929)].iloc[0]
ax[0].errorbar(92,r.height_mean,yerr=r.height_mean*r.height_cv/100,fmt='D',c=RC,ms=5,capsize=3,label='reference 30 May (90%, n = 15)')
ax[0].set_xlabel('Laser power (%)');ax[0].set_ylabel('929 cm$^{-1}$ band height (counts)');ax[0].legend(fontsize=7,frameon=False);ax[0].set_xticks([60,70,80,90])
for pw in (60,70,80,90):
  q=s[s.power==pw];ax[1].bar(pw,100*(q.QC=='PASS').mean(),width=6,color=PC[pw]);ax[1].text(pw,100*(q.QC=='PASS').mean()+2,f'{(q.QC=="PASS").sum()}/{len(q)}',ha='center',fontsize=8)
ax[1].set_xticks([60,70,80,90]);ax[1].set_xlabel('Laser power (%)');ax[1].set_ylabel('Spectra passing QC (%)')
f.suptitle('Fig. N8  Bulk intensity of the strongest NAM band versus power (filled = PASS) and QC pass rate',x=.01,ha='left',fontsize=10)
save(f,'FigN8_Intensity_vs_Power_and_PassRate.png')
# N9 60% set mean/median/sd
Nm=np.array([nz(P[f]['p']['corr']) for f in Q['sets']['NEW_60_24Sep']]);mn,md,sd=Nm.mean(0),np.median(Nm,0),Nm.std(0,ddof=1)
f,a=plt.subplots(figsize=(10,4.4));a.fill_between(x,mn-sd,mn+sd,color=PC[60],alpha=.25,lw=0,label='mean ± SD');a.plot(x,mn,c=PC[60],lw=1.1,label='mean (n = 11)');a.plot(x,md,c='k',lw=.7,ls=':',label='median');gz(a)
for _,rr in C.iterrows():
  k=np.argmin(abs(x-rr.new_pos)); a.annotate(f'{rr.new_pos:.0f}',(x[k],mn[k]+sd[k]+.02),rotation=90,fontsize=6.5,ha='center',va='bottom',color=GC if rr.glass_zone else ('#1f4e79' if rr.role.startswith('Primary') else ('#2e8b57' if rr.role.startswith('Supp') else '#b8860b')))
a.set_ylim(-.05,1.5);a.set_xlim(400,1800);a.legend(fontsize=7,frameon=False);a.set_xlabel('Raman shift (cm$^{-1}$)');a.set_ylabel('Normalised')
a.set_title('Fig. N9  Largest clean independent-spot set (60% / 30 s / 5 acc): mean, median, SD and reference bands',loc='left')
save(f,'FigN9_60pct_Set_Mean_Median_SD.png')
print(sorted(os.listdir(OUT)))
