# ln0 (formerly lf1.py): first-pass processing + QC of session 24 Sep 2026. Originally written when the folder was believed to be LPS;
# output names/paths were corrected by ln1.py after the operator confirmed NAM (27 Sep 2026). Numerical processing is identical.
# LPS screening 24 Sep 2026 - step 1: inventory, renamed copies, v3 processing, QC
import os,glob,re,hashlib,shutil,pickle,numpy as np,pandas as pd
from scipy.signal import savgol_filter
from lib2 import read_any,process_v3h,LIB
SRC=os.path.join(LIB,'bulk-lps-24-09-26'); TAG='LPS_Screening_20260924'
RAWD=os.path.join(LIB,'01_Raw_Data_Renamed',TAG); PROD=os.path.join(LIB,'02_Processed_Spectra',TAG)
subs=[('60 power',60),('lps-diffrent power-70',70),('lps-diffrent-80 power',80),('lps-diffrent-90-power',90)]
md5=lambda p: hashlib.md5(open(p,'rb').read()).hexdigest()
refdir=os.path.join(LIB,'03_Reference_Spectra')
def refcol(b):
  d=pd.read_csv(glob.glob(f'{refdir}/{b}/*Mean_SD.csv')[0],comment='#'); return d
NAMd=refcol('NAM'); LTAd=refcol('LTA')
rows=[];P={}
for sub,pw in subs:
  fl=sorted(glob.glob(f'{SRC}/{sub}/*.csv'))
  info=[]
  for f in fl:
    m,rs,dk,raw,ds=read_any(f); n=os.path.basename(f)
    info.append((m.get('Date',''),f,n,m,rs,dk,raw,ds))
  info.sort(key=lambda t:t[0])
  cnt={'LPS':0,'Glass':0}
  for date,f,n,m,rs,dk,raw,ds in info:
    low=n.lower()
    if low.startswith('glass'): cat='Glass_Blank'; note=''
    elif low.startswith('class'): cat='Glass_Blank'; note='Original name "%s": classified as empty-glass blank from the data (saturated glass band, no sample bands); operator confirmation pending'%n
    else: cat='LPS_Bulk'; note=''
    key='Glass' if cat=='Glass_Blank' else 'LPS'; cnt[key]+=1
    # replicate number: from original numbering for spots, acquisition order for blanks
    if cat=='LPS_Bulk':
      num=int(re.findall(r'\d+',n)[-1])
    else: num=cnt['Glass']
    it=float(m.get('integration times(sec)','nan')); acc=int(float(m.get('average number','0'))); lp=int(float(m.get('laser_powerlevel','0')))
    d8=date[:10].replace('-','')
    new=f'{cat}_{d8}_P{lp:03d}pct_T{int(it)}s_A{acc:02d}_S{num:02d}.csv'
    dst=os.path.join(RAWD,cat,new); os.makedirs(os.path.dirname(dst),exist_ok=True)
    if not os.path.exists(dst): shutil.copy2(f,dst)
    ok=md5(f)==md5(dst)
    p=process_v3h(rs,ds,raw); w=(rs>=400)&(rs<=1800)
    hp=lambda y: y-savgol_filter(y,31,2); rw=(rs>1550)&(rs<1800)
    rip=float(hp(ds)[rw].std()); rip_raw=float(hp(raw)[rw].std()); rip_dark=float(hp(dk)[rw].std())
    sat=raw[w]>=65535
    rec=dict(power=lp,category=cat,original_folder=sub,original_file=n,library_file=new,md5=md5(f),copy_verified=ok,acq_time=date,
      integration_s=it,accumulations=acc,laser_nm=m.get('laser_wavelength',''),probe_name=m.get('probe_name','') or 'Not recorded',
      operator=m.get('operator','') or 'Not recorded',product=m.get('Product Name','') or 'Not recorded',lot=m.get('Lot No','') or 'Not recorded',
      dark_median=float(np.median(dk)),dark_hf=rip_dark,raw_hf=rip_raw,ripple_ds=rip,raw_max_400_1800=float(raw[w].max()),
      n_sat_400_1800=int(sat.sum()),sat_from=float(rs[w][sat].min()) if sat.any() else np.nan,sat_to=float(rs[w][sat].max()) if sat.any() else np.nan,
      raw_max_all=float(raw.max()),ds_min_400_1800=float(ds[w].min()),noise=p['noise'],n_spikes=p['nspikes'],spikes=';'.join(f'{v:.0f}' for v in p['spike_pos']),note=note)
    rows.append(rec); P[new]=dict(p=p,rec=rec,rs=rs,dk=dk,raw=raw,ds=ds)
df=pd.DataFrame(rows)
x=list(P.values())[0]['p']['x']
NAM=np.interp(x,NAMd.iloc[:,0],NAMd['Normalised_mean']); LTA=np.interp(x,LTAd.iloc[:,0],LTAd['Normalised_mean'])
old=[]
for f in sorted(glob.glob(f'{LIB}/01_Raw_Data_Renamed/LPS_Bulk/*.csv')):
  m,rs,dk,raw,ds=read_any(f); q=process_v3h(rs,ds,raw); old.append(np.interp(x,q['x'],q['norm']))
OLD=np.mean(old,0)
GZ=(x>=1308)&(x<=1455); keep=~GZ
r=lambda a,b: float(np.corrcoef(a[keep],b[keep])[0,1])
k929=np.argmin(abs(x-929))
for i,rw in df.iterrows():
  c=P[rw.library_file]['p']['corr']; h=c[k929-4:k929+5].max()
  df.loc[i,'r_NAM_ref']=r(c,NAM); df.loc[i,'r_LTA_ref']=r(c,LTA); df.loc[i,'r_oldLPS_mean']=r(c,OLD)
  df.loc[i,'h929_counts']=h; df.loc[i,'snr929']=h/rw.noise
def qc(rw):
  if rw.category=='Glass_Blank':
    return ('BLANK-SATURATED' if rw.n_sat_400_1800>0 else 'BLANK-OK'), ('Detector saturated %.0f-%.0f cm-1 (glass band); usable only outside this range'%(rw.sat_from,rw.sat_to) if rw.n_sat_400_1800>0 else '')
  if rw.n_sat_400_1800>0: return 'FAIL','Saturated in 400-1800 cm-1'
  if rw.ripple_ds>50: return 'FAIL','Dark-reference mismatch ripple (residual %.0f counts > 50)'%rw.ripple_ds
  if rw.snr929<10: return 'FAIL','SNR < 10'
  return 'PASS',''
q=df.apply(qc,axis=1); df['QC']=[a for a,b in q]; df['QC_reason']=[b for a,b in q]
pickle.dump(dict(df=df,P=P,x=x,NAM=NAM,LTA=LTA,OLD=OLD),open('lf1.pkl','wb'))
print(df[['power','category','original_file','library_file','copy_verified','dark_median','ripple_ds','noise','snr929','r_NAM_ref','QC']].to_string())
