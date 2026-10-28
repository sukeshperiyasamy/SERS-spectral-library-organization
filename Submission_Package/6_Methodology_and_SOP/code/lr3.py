import pickle,numpy as np,pandas as pd
from scipy.signal import savgol_filter,find_peaks,peak_widths
from lib2 import process_v3h
D=pickle.load(open('lr2.pkl','rb'));df=D['df'];P=D['P'];x=D['x']
GZ=(x>=1308)&(x<=1455);keep=~GZ;dx=np.mean(np.diff(x))
def nz(c): c=c-c[keep].min(); return c/c[keep].max()
fin=df[(df.library_file.str.contains('P060pct_T40s_A05_S(1[0-9]|20)'))&(df.category=='LPS_Bulk')].copy()
# QC
def qc(r):
  if r.nsat>0: return 'FAIL','saturated'
  if r.ripple>50: return 'FAIL','ripple > 50'
  if r.snr425<10: return 'FAIL','SNR < 10'
  if r.glass_ratio>8: return 'EXCLUDE','glass-dominated spot (glass-zone/800-1000 area ratio %.1f; r to LPS screening mean %.2f)'%(r.glass_ratio,r.rLPS28)
  return 'PASS',''
q=fin.apply(qc,axis=1);fin['QC']=[a for a,b in q];fin['QC_reason']=[b for a,b in q]
ks=list(fin[fin.QC=='PASS'].library_file)
N=np.array([nz(P[k]['p']['corr']) for k in ks]);rr=np.corrcoef(N[:,keep]);iu=np.triu_indices(len(ks),1)
for i,k in enumerate(ks): fin.loc[fin.library_file==k,'r_to_others']=(rr[i].sum()-1)/(len(ks)-1)
print(fin[['library_file','QC','QC_reason','r_to_others']].to_string())
print('pairwise r mean %.3f min %.3f'%(rr[iu].mean(),rr[iu].min()))
# dark-excess intensity correction estimate: excess = dark - true dark frame(check S02, same session end) ; regress smoothed excess on ds
tf=P['Check_20260928_P060pct_T40s_A05_ShutterClosedFrame_S02.csv']['raw']
w=(D['P'][ks[0]]['rs']>=400)&(D['P'][ks[0]]['rs']<=1800)
for k in ks:
  q=P[k]; ex=savgol_filter(q['dk']-tf,61,2)[w]; s=savgol_filter(q['raw']-tf,61,2)[w]  # true sample light
  a=np.polyfit(s,ex,1)[0]; fin.loc[fin.library_file==k,'dark_light_fraction']=a; fin.loc[fin.library_file==k,'intensity_factor']=1/(1-a)
print(fin[['library_file','dark_excess','dark_light_fraction','intensity_factor']].round(3).to_string())
C=np.array([P[k]['p']['corr'] for k in ks])
mn,md,sd=N.mean(0),np.median(N,0),N.std(0,ddof=1)
print('mean vs median r %.4f; frac |mean-median|<SD %.3f'%(np.corrcoef(mn,md)[0,1],np.mean(abs(mn-md)<sd)))
pickle.dump(dict(fin=fin,ks=ks,N=N,C=C,mn=mn,md=md,sd=sd),open('lr3.pkl','wb'))
