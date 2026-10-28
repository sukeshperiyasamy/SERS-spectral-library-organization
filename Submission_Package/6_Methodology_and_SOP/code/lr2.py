import os,pickle,numpy as np,pandas as pd
from scipy.signal import savgol_filter
from lib2 import read_any,process_v3h,LIB
inv=pd.read_pickle('lr_inv.pkl'); inv=inv[~inv.library_file.str.endswith('.txtr')].reset_index(drop=True)
R=pickle.load(open('lp4.pkl','rb')); x=R['x']; NAM=R['NAM'];LTA=R['LTA'];OLD=R['OLD']
GZ=(x>=1308)&(x<=1455);keep=~GZ
def nz(c): c=c-c[keep].min(); return c/c[keep].max()
m60=np.mean([nz(R['P'][k]['p']['corr']) for k in R['core'] if k.startswith('60')],0)
hp=lambda y: y-savgol_filter(y,31,2)
P={};out=[]
for i,r in inv.iterrows():
  f=os.path.join(LIB,'01_Raw_Data_Renamed',r.category,r.library_file)
  m,rs,dk,raw,ds=read_any(f); p=process_v3h(rs,ds,raw); w=(rs>=400)&(rs<=1800); rw=(rs>1550)&(rs<1800)
  c=p['corr']; k=np.argmin(abs(x-425)); h=c[k-3:k+4].max()
  sat=raw[w]>=65535
  d=dict(library_file=r.library_file,category=r.category,role=r.role,acq=m.get('Date',''),power=int(float(m['laser_powerlevel'])),int_s=float(m['integration times(sec)']),acc=int(float(m['average number'])),
    dark_med=float(np.median(dk[w])),raw_med=float(np.median(raw[w])),raw_max=float(raw[w].max()),nsat=int(sat.sum()),sat_from=float(rs[w][sat].min()) if sat.any() else np.nan,sat_to=float(rs[w][sat].max()) if sat.any() else np.nan,
    ripple=float(hp(ds)[rw].std()),noise=p['noise'],h425=float(h),snr425=float(h/p['noise']),nspikes=p['nspikes'],
    rNAM=float(np.corrcoef(c[keep],NAM[keep])[0,1]),rLTA=float(np.corrcoef(c[keep],LTA[keep])[0,1]),rLPSapr=float(np.corrcoef(c[keep],OLD[keep])[0,1]),rLPS28=float(np.corrcoef(c[keep],m60[keep])[0,1]),
    glass_ratio=float(np.trapezoid(c[GZ],x[GZ])/np.trapezoid(c[(x>800)&(x<1000)],x[(x>800)&(x<1000)])) if r.category=='LPS_Bulk' else np.nan)
  out.append(d); P[r.library_file]=dict(p=p,rs=rs,dk=dk,raw=raw,ds=ds)
df=pd.DataFrame(out)
# dark verification: true dark from shutter-closed frames at 40 s
chk=df[df.library_file.str.contains('T40s_A05_ShutterClosed')]
print(chk[['library_file','acq','raw_med','dark_med']].to_string())
true40=chk[chk.library_file.str.contains('Frame')].raw_med.mean()
df['dark_excess']=np.where(df.int_s==40,df.dark_med-true40,np.nan)
pickle.dump(dict(df=df,P=P,x=x,NAM=NAM,LTA=LTA,OLD=OLD,m60=m60,true40=true40),open('lr2.pkl','wb'))
pd.set_option('display.width',250)
print(df[['library_file','acq','dark_med','dark_excess','raw_max','nsat','ripple','noise','h425','snr425','rNAM','rLTA','rLPSapr','rLPS28','glass_ratio']].round(2).to_string())
