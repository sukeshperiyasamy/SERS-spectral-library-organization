import sys,os,pickle,numpy as np,pandas as pd
from scipy.signal import find_peaks,peak_prominences,peak_widths
sys.path.insert(0,os.path.expanduser('~/work')); from lib2 import *
B,P,A,G,GZ=pickle.load(open(os.path.expanduser('~/work/v2.pkl'),'rb'))
I=lambda i,k:np.interp(X,P[i]['x'],P[i][k])
V=B[(B.cls=='LTA')&(B.qc_status=='Valid')]; R=V[V.in_reference]
print('glass norm at 1459:',G[np.argmin(abs(X-1459))].round(3),' at 1440:',G[np.argmin(abs(X-1440))].round(3),' at 1367:',G[np.argmin(abs(X-1367))].round(3),'glass max at',X[np.argmax(G)])
pk=find_peaks(G,prominence=0.2)[0]; w=peak_widths(G,pk,0.5)[0]; print('glass band FWHM (cm-1):',w)
rows=[]
for m in [541,802,861,1092,1367,1459]:
  for name,S in [('ref',R),('all valid',V)]:
    hits=0;fw=[];h=[];hg=[];pos=[]
    for i in S.index:
      c=I(i,'corr'); nz=P[i]['noise']; p_,_=find_peaks(c,prominence=5*nz,distance=5); ww=(X>=m-10)&(X<=m+10)
      j=np.where(ww)[0][np.argmax(c[ww])]; pos.append(X[j]); h.append(c[j])
      aa=np.dot(c[GZ],G[GZ])/np.dot(G[GZ],G[GZ]); hg.append((c-aa*G)[j])
      if len(p_) and np.min(abs(X[p_]-X[j]))<=5:
        hits+=1; k=p_[np.argmin(abs(X[p_]-X[j]))]; fw.append(peak_widths(c,[k],0.5)[0][0])
    rows.append(dict(peak=m,set=name,n=len(S),detected=hits,pos=f'{np.mean(pos):.1f}±{np.std(pos,ddof=1):.1f}',fwhm=np.mean(fw) if fw else np.nan,h=np.mean(h),h_glasscorr=np.mean(hg),retained_pct=100*np.mean(hg)/np.mean(h)))
print(pd.DataFrame(rows).round(1).to_string()); print(V[['new_name','power','int_s','acc','snr']].to_string())
