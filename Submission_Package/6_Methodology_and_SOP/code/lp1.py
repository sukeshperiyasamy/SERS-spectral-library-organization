import os,glob,re,pickle,numpy as np,pandas as pd
from scipy.signal import savgol_filter,find_peaks
from lib2 import read_any,process_v3h,LIB
SRC=os.path.expanduser('~/mnt/sukesh/28-9-26-lps-bulk')
D=pickle.load(open('ln1.pkl','rb')); x=D['x']; NAM=D['NAM']; LTA=D['LTA']; OLD=D['OLD']
GZ=(x>=1308)&(x<=1455); keep=~GZ
rows=[];P={}
for f in sorted(glob.glob(SRC+'/*/*.csv')):
  m,rs,dk,raw,ds=read_any(f); n=os.path.basename(f); sub=os.path.basename(os.path.dirname(f))
  pw=int(float(m['laser_powerlevel'])); cat='Glass_Blank' if n.lower().startswith('glass') else 'LPS_Bulk'
  num=int(re.findall(r'\d+',n.replace('30s','').replace('60p','').replace('70p','').replace('80p','').replace('5ac',''))[-1])
  p=process_v3h(rs,ds,raw); w=(rs>=400)&(rs<=1800); rw=(rs>1550)&(rs<1800)
  hp=lambda y: y-savgol_filter(y,31,2)
  c=p['corr']; out=keep&(x>420)&(x<1780); k=np.argmax(np.where(out,c,-1e9))
  sat=raw[w]>=65535
  key=f'{pw}_{cat}_{num:02d}'
  rows.append(dict(key=key,power=pw,category=cat,orig=f'{sub}/{n}',num=num,acq=m.get('Date',''),int_s=float(m['integration times(sec)']),acc=int(float(m['average number'])),
    dark_med=float(np.median(dk)),ripple=float(hp(ds)[rw].std()),raw_max=float(raw[w].max()),nsat=int(sat.sum()),sat_from=float(rs[w][sat].min()) if sat.any() else np.nan,sat_to=float(rs[w][sat].max()) if sat.any() else np.nan,
    ds_med=float(np.median(ds[w])),noise=p['noise'],strong_pos=float(x[k]),strong_h=float(c[k]),snr=float(c[k]/p['noise']),nspk=p['nspikes'],
    rNAM=float(np.corrcoef(c[keep],NAM[keep])[0,1]),rLTA=float(np.corrcoef(c[keep],LTA[keep])[0,1]),rOLD=float(np.corrcoef(c[keep],OLD[keep])[0,1])))
  P[key]=dict(p=p,rs=rs,dk=dk,raw=raw,ds=ds)
df=pd.DataFrame(rows)
# r to own blank mean (outside glass zone? blanks saturate) : use full-range excluding saturated region of blanks
for pw in df.power.unique():
  B=[P[k]['p']['corr'] for k in df[(df.power==pw)&(df.category=='Glass_Blank')].key]
  bm=np.mean(B,0); lo=df[(df.power==pw)&(df.category=='Glass_Blank')].sat_from.min(); hi=df[(df.power==pw)&(df.category=='Glass_Blank')].sat_to.max()
  mk=~((x>=(lo if not np.isnan(lo) else 1e9)-20)&(x<=(hi if not np.isnan(hi) else -1)+20))
  for i in df[df.power==pw].index: df.loc[i,'rBlank']=float(np.corrcoef(P[df.key[i]]['p']['corr'][mk],bm[mk])[0,1])
pickle.dump(dict(df=df,P=P,x=x),open('lp1.pkl','wb'))
pd.set_option('display.width',250)
print(df[['key','orig','acq','dark_med','ripple','raw_max','nsat','ds_med','noise','strong_pos','strong_h','snr','rNAM','rLTA','rOLD','rBlank']].round(2).to_string())
