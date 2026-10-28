import os,pickle,numpy as np,pandas as pd
from scipy.signal import find_peaks
from lib2 import LIB,read_any,process_v3h
N=pickle.load(open('ln1.pkl','rb')); df=N['df']; P=N['P']; x=N['x']
mem=pd.read_csv(os.path.join(LIB,'03_Reference_Spectra/NAM/NAM_Reference_Members.csv'))
OLD={}
for _,m in mem.iterrows():
  f=os.path.join(LIB,'01_Raw_Data_Renamed/NAM_Bulk',m.library_file)
  meta,rs,dk,raw,ds=read_any(f); p=process_v3h(rs,ds,raw); OLD[m.library_file]=dict(p=p,spot=m.spot,rs=rs)
x0=list(OLD.values())[0]['p']['x']
print('axis identical old vs new:',np.allclose(x0,x),'max diff %.3f'%np.max(abs(x0-x)))
meta_new,_,_,_,_=read_any(os.path.join(LIB,'01_Raw_Data_Renamed/NAM_Bulk',df[df.category=='NAM_Bulk'].library_file.iloc[0]))
meta_old,_,_,_,_=read_any(os.path.join(LIB,'01_Raw_Data_Renamed/NAM_Bulk',mem.library_file.iloc[0]))
for k in ['coefs_a0','coefs_a1','coefs_a2','coefs_a3','laser_wavelength']: print(k,meta_old.get(k),meta_new.get(k))
pickle.dump(OLD,open('ln2_old.pkl','wb'))
print(mem.spot.value_counts())
