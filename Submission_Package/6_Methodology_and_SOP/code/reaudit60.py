import sys,os,pickle,numpy as np,pandas as pd
sys.path.insert(0,os.path.expanduser('~/work')); from lib2 import *
B,P,A,G,GZ=pickle.load(open(os.path.expanduser('~/work/v2.pkl'),'rb'))
I=lambda i,k:np.interp(X,P[i]['x'],P[i][k])
ref=B[B.in_reference&(B.cls=='NAM')]; M=np.mean([I(i,'norm') for i in ref.index],0)
MK=[541,870,929,955,1023,1127]
S=B[(B.cls=='NAM')&(B.int_s==60)&(B.acc==5)]
rows=[]
for i,r in S.iterrows():
  meta,rs,dk,raw,ds=read_any(os.path.join(ROOT,r.orig))
  satpix=rs[raw>=65000]; fp=(rs>=400)&(rs<=1800)
  dsfp=ds[fp]; negfrac=(dsfp<0).mean()
  dkfp=dk[fp]; rawfp=raw[fp]
  c=I(i,'corr'); nz=P[i]['noise']
  h=[c[(X>=m-8)&(X<=m+8)].max() for m in MK]; pos=[X[(X>=m-8)&(X<=m+8)][np.argmax(c[(X>=m-8)&(X<=m+8)])] for m in MK]
  r_ex=np.corrcoef(I(i,'norm')[~GZ],M[~GZ])[0,1]
  # smoothness: ratio of noise to median signal
  rows.append(dict(file=r.new_name,orig=r.orig,power=r.power,n_sat_pixels=len(satpix),sat_shift_range=f"{satpix.min():.1f} to {satpix.max():.1f}" if len(satpix) else '',
    raw_max_fp=rawfp.max(),raw_min_fp=rawfp.min(),dark_median_fp=np.median(dkfp),ds_min_fp=dsfp.min(),ds_max_fp=dsfp.max(),neg_frac=negfrac,noise=nz,snr=max(h)/nz,r_ref_exglass=r_ex,
    marker_pos=','.join(f'{p:.0f}' for p in pos),marker_h=','.join(f'{x:.0f}' for x in h)))
D=pd.DataFrame(rows); pd.set_option('display.width',260); print(D.round(3).to_string())
pickle.dump(D,open(os.path.expanduser('~/work/reaudit60.pkl'),'wb'))
