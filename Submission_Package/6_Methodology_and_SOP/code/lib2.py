import os,numpy as np
from scipy.signal import savgol_filter,medfilt
from scipy import sparse
from scipy.sparse.linalg import spsolve
ROOT=os.environ.get('SUKESH_ROOT') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..'))  # sukesh folder (auto-detected; works on Windows and the VM)
LIB=os.path.join(ROOT,'SERS_Sepsis_Spectral_Library')
X=np.arange(400,1801,1.0)
def read_any(p):
  meta={};rows=[]
  with open(p,errors='ignore') as fh:
    lines=fh.read().replace('\r','').split('\n')
  sep=';' if any(l.startswith('Pixel;') for l in lines[:200]) else ','
  hdr=True
  for l in lines:
    if hdr:
      if l.startswith('Pixel'+sep): hdr=False; continue
      k,_,v=l.partition(sep); meta[k.strip()]=v.strip().rstrip(sep)
    else:
      q=l.split(sep)
      if len(q)>7:
        try: rows.append([float(q[3]),float(q[4]),float(q[6]),float(q[7])])
        except: pass
  a=np.array(rows) if rows else np.zeros((0,4))
  return meta,a[:,0],a[:,1],a[:,2],a[:,3]   # meta, raman shift, dark, raw, dark-subtracted
def despike(y,th=6):
  d=np.diff(y); med=np.median(d); mad=np.median(np.abs(d-med))+1e-9
  z=0.6745*(d-med)/mad; bad=np.zeros_like(y,bool); bad[1:]|=np.abs(z)>th
  # a spike produces +/- pair; count events as clusters
  idx=np.where(bad)[0]; n=0; last=-10
  for i in idx:
    if i-last>3: n+=1
    last=i
  y2=y.copy()
  if len(idx):
    mf=medfilt(y,7)
    for i in idx: lo,hi=max(0,i-2),min(len(y),i+3); y2[lo:hi]=mf[lo:hi]
  return y2,n
def als(y,lam=1e5,p=0.01,it=10):
  L=len(y); D=sparse.diags([1,-2,1],[0,-1,-2],shape=(L,L-2)); D=lam*D.dot(D.T); w=np.ones(L)
  for _ in range(it):
    W=sparse.spdiags(w,0,L,L); z=spsolve(W+D,w*y); w=p*(y>z)+(1-p)*(y<z)
  return z
def process(rs,ds,raw):
  m=(rs>=400)&(rs<=1800); x=rs[m]; r=raw[m]; y0=ds[m]
  y,nsp=despike(y0); ys=savgol_filter(y,11,3); b=als(ys); c=ys-b
  noise=float(np.std(y-savgol_filter(y,11,3)))
  mx=c.max() if c.max()>0 else 1
  return dict(x=x,raw=r,ds=y0,despiked=y,smooth=ys,base=b,corr=c,norm=(c-c.min())/(mx-c.min()),nspikes=nsp,noise=noise)

def despike_v3(y,th=6,maxw=2):
  """Whitaker-Hayes-type spike removal with width guard (v3).
  1) modified z-score of first difference: z = 0.6745*(d - median(d))/MAD(d); candidate if |z|>th
  2) a candidate is accepted as a spike only if the local excursion is narrow: <= maxw pixels above half of its height
     (cosmic rays / hot pixels are 1-2 pixels wide; genuine Raman bands here are >= 3-4 pixels wide)
  3) accepted points (+-1 pixel) are replaced by linear interpolation from unflagged neighbours."""
  y=np.asarray(y,float); d=np.diff(y); med=np.median(d); mad=np.median(np.abs(d-med))+1e-9
  z=0.6745*(d-med)/mad; cand=np.where(np.abs(z)>th)[0]
  cand=np.unique(np.concatenate([cand,cand+1])) if len(cand) else cand
  bad=np.zeros(len(y),bool); events=[]
  # cluster candidates
  groups=[];cur=[]
  for k in cand:
    if cur and k-cur[-1]>2: groups.append(cur); cur=[]
    cur.append(k)
  if cur: groups.append(cur)
  for grp in groups:
    k=grp[int(np.argmax(np.abs(y[grp]-np.median(y[max(0,grp[0]-8):grp[-1]+9]))))]
    lo,hi=max(0,k-8),min(len(y),k+9)
    loc=np.concatenate([y[lo:max(lo,k-3)],y[min(hi,k+4):hi]])
    if len(loc)<3: continue
    base=np.median(loc); e=y[k]-base
    if e==0: continue
    win=y[max(0,k-4):k+5]-base
    width=np.sum((win/e)>0.5)
    if width<=maxw:
      s,t=max(0,k-1),min(len(y)-1,k+1); bad[s:t+1]=True; events.append(k)
  y2=y.copy()
  if bad.any():
    good=np.where(~bad)[0]; y2[bad]=np.interp(np.where(bad)[0],good,y[good])
  return y2,len(events),events
def process_v3(rs,ds,raw):
  m=(rs>=400)&(rs<=1800); x=rs[m]; r=raw[m]; y0=ds[m]
  y,nsp,ev=despike_v3(y0); ys=savgol_filter(y,11,3); b=als(ys); c=ys-b
  res=y-ys; noise=float(1.4826*np.median(np.abs(res-np.median(res))))   # robust (MAD) noise of the high-frequency residual
  mx=c.max() if c.max()>0 else 1
  return dict(x=x,raw=r,ds=y0,despiked=y,smooth=ys,base=b,corr=c,norm=(c-c.min())/(mx-c.min()),nspikes=nsp,spike_pos=[float(x[k]) for k in ev],noise=noise)

HOT_PIXELS=[640,700]   # fixed defective CCD pixels (~1095.7 and ~1189.5 cm-1), identified in >=59 spectra on 6 dates and in dark frames
def hotpix_fix(ds):
  y=np.asarray(ds,float).copy()
  for k in HOT_PIXELS:
    if 1<=k<len(y)-1: y[k]=0.5*(y[k-1]+y[k+1])
  return y
def process_v3h(rs,ds,raw):
  dsf=hotpix_fix(ds); p=process_v3(rs,dsf,raw)
  m=(rs>=400)&(rs<=1800); p['ds']=ds[m]; p['ds_hotfix']=dsf[m]
  return p
