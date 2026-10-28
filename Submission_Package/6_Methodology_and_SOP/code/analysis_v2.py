import sys,os,pickle,numpy as np,pandas as pd
from scipy.signal import find_peaks,peak_prominences
sys.path.insert(0,os.path.expanduser('~/work')); from lib2 import *
B,P,A,G,GZ=pickle.load(open(os.path.expanduser('~/work/v2.pkl'),'rb'))
I=lambda i,k:np.interp(X,P[i]['x'],P[i][k])
from lit_v2 import MLIT
MARK={'NAM':[(m,MLIT[('NAM',m)][0]) for m in [541,830,870,929,955,1023,1127,458,487,1249,584,1059,1155,1589,1346,1393,1451]],
      'LTA':[(m,MLIT[('LTA',m)][0]) for m in [802,861,1092,1459,541,1367]]}
res={}
peakrows=[];allpk=[];reprows=[];bulkrows=[]
for a in ['NAM','LTA']:
  R=B[B.in_reference]; R=R[R.cls==a]; idx=list(R.index)
  C=np.array([I(i,'corr') for i in idx]); Nn=np.array([I(i,'norm') for i in idx]); DS=np.array([I(i,'ds') for i in idx]); RAW=np.array([I(i,'raw') for i in idx])
  noise=np.array([P[i]['noise'] for i in idx])
  # glass-template exploratory correction: fit a*G on glass zone
  Cg=[]
  for c in C:
    aa=np.dot(c[GZ],G[GZ])/np.dot(G[GZ],G[GZ]); Cg.append(c-max(aa,0)*G)
  Cg=np.array(Cg)
  # all reproducible peaks (data-driven)
  det=[]
  for c,nz in zip(C,noise):
    pk,_=find_peaks(c,prominence=5*nz,distance=5); det.append(X[pk])
  cand=np.concatenate(det); used=np.zeros(len(cand),bool); clusters=[]
  for v in np.sort(cand):
    near=[d[np.argmin(abs(d-v))] for d in det if len(d) and abs(d[np.argmin(abs(d-v))]-v)<=5]
    clusters.append((round(np.mean(near)),len(near)))
  cl={}
  for c,nn in clusters:
    if not any(abs(c-k)<=5 for k in cl): cl[c]=nn
  M=C.mean(0)
  for c,nn in sorted(cl.items()):
    j=np.argmin(abs(X-c)); allpk.append(dict(analyte=a,peak_cm1=c,replicates_detected=nn,n=len(idx),frequency_pct=100*nn/len(idx),rel_intensity=M[j]/M.max(),glass_zone=bool(GZ[j])))
  for m,role in MARK[a]:
    w=(X>=m-8)&(X<=m+8); pos=[];h=[];hg=[];pr=[];snr=[];raw=[];ds=[];det_n=0
    for k,(c,nz) in enumerate(zip(C,noise)):
      jj=np.where(w)[0][np.argmax(c[w])]; pos.append(X[jj]); h.append(c[jj]); snr.append(c[jj]/nz)
      pr.append(peak_prominences(c,[jj])[0][0]); raw.append(RAW[k][jj]); ds.append(DS[k][jj]); hg.append(Cg[k][jj])
      if len(det[k]) and np.min(abs(det[k]-X[jj]))<=5: det_n+=1
    peakrows.append(dict(analyte=a,role=role,nominal=m,pos_mean=np.mean(pos),pos_sd=np.std(pos,ddof=1),height_mean=np.mean(h),height_sd=np.std(h,ddof=1),cv=100*np.std(h,ddof=1)/np.mean(h),
      snr_mean=np.mean(snr),prom_mean=np.mean(pr),rel=np.mean(h)/C.mean(0).max(),raw_counts=np.mean(raw),ds_counts=np.mean(ds),glass_corr_height=np.mean(hg),glass_zone=bool(GZ[np.argmin(abs(X-np.mean(pos)))]),
      n_detected=det_n,n=len(idx)))
  # reproducibility
  r_pairs=[np.corrcoef(Nn[p],Nn[q])[0,1] for p in range(len(idx)) for q in range(p+1,len(idx))]
  r_mean=[np.corrcoef(n_,Nn.mean(0))[0,1] for n_ in Nn]
  reprows.append(dict(analyte=a,n=len(idx),pairwise_r_mean=np.mean(r_pairs),pairwise_r_min=np.min(r_pairs),r_to_mean_mean=np.mean(r_mean),r_to_mean_min=np.min(r_mean)))
  bulkrows.append(dict(analyte=a,condition=f"{int(R.power.min())}{'' if R.power.min()==R.power.max() else '-%d'%R.power.max()}% / {int(R.int_s.iloc[0])} s / {int(R.acc.iloc[0])} acc",n=len(idx),
     max_raw_counts_mean=R.raw_max_fp.mean(),max_raw_counts_sd=R.raw_max_fp.std(),max_ds_counts_mean=R.ds_max_fp.mean(),max_ds_counts_sd=R.ds_max_fp.std(),baseline_mean=R.baseline_level.mean(),
     strongest_marker_height_mean=R.marker_max.mean(),strongest_marker_height_sd=R.marker_max.std(),cv=100*R.marker_max.std()/R.marker_max.mean(),snr_mean=R.snr.mean(),snr_sd=R.snr.std(),dates=', '.join(sorted(R.ymd.unique()))))
  res[a]=dict(idx=idx,C=C,N=Nn,DS=DS,Cg=Cg,R=R)
PK=pd.DataFrame(peakrows); ALL=pd.DataFrame(allpk); REP=pd.DataFrame(reprows); BULK=pd.DataFrame(bulkrows)
# parameter conditions table
cond=[]
for a in ['NAM','LTA','LPS']:
  d=B[(B.cls==a)]
  for (pw,t,ac),g in d.groupby(['power','int_s','acc']):
    ok=g[~g.saturated]
    rr=np.nan
    if len(ok)>1:
      Nn=np.array([I(i,'norm') for i in ok.index]); rr=np.mean([np.corrcoef(Nn[p],Nn[q])[0,1] for p in range(len(ok)) for q in range(p+1,len(ok))])
    cond.append(dict(analyte=a,power=pw,int_s=t,acc=ac,n=len(g),n_valid=(g.qc_status=='Valid').sum(),n_saturated=int(g.saturated.sum()),snr_mean=g.snr.mean(),snr_sd=g.snr.std(),
      marker_height_mean=g.marker_max.mean() if a!='LPS' else np.nan,cv=100*g.marker_max.std()/g.marker_max.mean() if a!='LPS' else np.nan,
      baseline_mean=g.baseline_level.mean(),max_raw_mean=g.raw_max_fp.mean(),pairwise_r=rr,dates=', '.join(sorted(g.ymd.unique())),
      reference='YES' if g.in_reference.any() else ''))
COND=pd.DataFrame(cond)
pickle.dump((PK,ALL,REP,BULK,COND,res),open(os.path.expanduser('~/work/an2.pkl'),'wb'))
pd.set_option('display.width',250)
print(PK.round(2).to_string()); print(REP.round(3).to_string()); print(BULK.round(1).to_string())
print(ALL[(ALL.frequency_pct>=75)&(ALL.rel_intensity>=0.3)].round(2).to_string())
