import numpy as np,pandas as pd,json,os
from scipy.signal import find_peaks
from scipy.optimize import nnls
M=r"C:\Users\sukes\Downloads\mtp"; L=r"C:\Users\sukes\Downloads\sukesh\SERS_Sepsis_Spectral_Library"
rng=np.random.default_rng(7)
X=np.arange(400,1801,1.0); G=~((X>=1308)&(X<=1455))
def ref(a):
    r=pd.read_csv(f"{L}/03_Reference_Spectra/{a}/{a}_Bulk_Reference_Mean_SD.csv",comment='#')
    return np.interp(X,r.iloc[:,0].values,r['Normalised_mean'].values)
def libbands(a):
    m=pd.read_csv(f"{L}/03_Reference_Spectra/{a}/{a}_Reference_Marker_Peaks.csv")
    if a=='LPS':
        m=m[m['class'].str.startswith(('C1','C2'))]; return [(round(v,1),'Primary' if c.startswith('C1') else 'Supporting') for v,c in zip(m.pos_mean,m['class'])]
    m=m[(m.glass_zone==False)&m.role.str.startswith(('Primary','Supporting'))]
    return [(round(v,1),'Primary' if r.startswith('Primary') else 'Supporting') for v,r in zip(m.pos_mean,m.role)]
def gauss(modes,w,fwhm=12):
    s=fwhm/2.3548; y=np.zeros_like(X)
    for f,a in zip(modes,w): y+=a*np.exp(-0.5*((X-f)/s)**2)
    return y
def mm(y): return (y-y.min())/(y.max()-y.min())
def match(bands,modes,tol):
    out=[]
    for b,_ in bands:
        d=modes-b; i=np.argmin(np.abs(d)); out.append((b,modes[i],d[i]*-1))   # exp - calc
    return out
def nmatch(bands,modes,tol): return sum(abs(b-modes[np.argmin(np.abs(modes-b))])<=tol for b,_ in bands)
def decoy(bands,modes,tol,n=5000):
    res=[]
    for _ in range(n):
        s=rng.uniform(15,70)*rng.choice([-1,1]); res.append(nmatch(bands,modes+s,tol))
    return np.array(res)
R={}
# ---- NAM
nm=pd.read_csv(M+r"\NAM_Raman_Archive\02_DFT_Calculation\NAM_calculated_modes_all_111.csv")
nm=nm[(nm.freq_scaled>=400)&(nm.freq_scaled<=1800)]
sim=pd.read_csv(M+r"\NAM_Raman_Archive\03_Processed_Results\DFT_simulated_spectrum.csv")
data={'NAM':dict(modes=nm.freq_scaled.values,act=nm.intensity.values,label=nm.assignment.values),}
# ---- LPS
lp=pd.read_csv(M+r"\lps research\reanalysis_2026-08-30\dft_candidates_all.csv"); lp=lp[(lp.iloc[:,0]>=400)&(lp.iloc[:,0]<=1800)]
data['LPS']=dict(modes=lp.iloc[:,0].values,act=lp.activity.values/lp.activity.max(),label=lp.fragment.values)
# ---- LTA (from broadened curves, x*0.96)
ltd=pd.read_csv(r"C:\Users\sukes\Downloads\mtp\LTA-simulation-main\LTA-simulation-main\LTA_combined_data.csv")
lm=[];la=[];ll=[]; curves={}
for ds,g in ltd.groupby('Dataset'):
    x=g.RamanShift.values; y=g.Intensity_norm.values   # NOTE: csv RamanShift already x0.96? check below
    curves[ds]=(x,y)
    k=(x>=400)&(x<=1800); pk,_=find_peaks(y,prominence=0.04)
    for p in pk:
        if 400<=x[p]<=1800: lm.append(x[p]); la.append(y[p]); ll.append(ds)
data['LTA']=dict(modes=np.array(lm),act=np.array(la),label=np.array(ll))
for a in ('NAM','LPS','LTA'):
    d=data[a]; bands=libbands(a); modes=d['modes']; act=d['act']
    strong=modes[act>=0.15]
    res=dict(bands=[],n=len(bands),n_modes=int(len(modes)),n_strong=int(len(strong)))
    for b,role in bands:
        i=np.argmin(np.abs(modes-b));
        res['bands'].append(dict(exp=b,role=role,calc=float(modes[i]),delta=float(b-modes[i]),act=float(act[i]),label=str(d['label'][i])))
    for tol in (5,10,18):
        r=nmatch(bands,modes,tol); dc=decoy(bands,modes,tol); rs=nmatch(bands,strong,tol); dcs=decoy(bands,strong,tol)
        res[f't{tol}']=dict(real=int(r),decoy_mean=float(dc.mean()),decoy_sd=float(dc.std()),p=float((dc>=r).mean()),real_strong=int(rs),decoy_strong_mean=float(dcs.mean()),p_strong=float((dcs>=rs).mean()))
    d_=np.array([b['delta'] for b in res['bands']]); res['mae']=float(np.mean(np.abs(d_))); res['rmse']=float(np.sqrt(np.mean(d_**2)))
    # whole spectrum
    e=ref(a)
    if a=='NAM':
        sp=mm(np.interp(X,sim.raman_shift_cm1.values,sim.intensity_norm.values))
    elif a=='LPS':
        sp=mm(gauss(modes,act))
    else:
        sp=mm(sum(np.interp(X,*curves[k]) for k in curves)/3)
    res['r_equal']=float(np.corrcoef(sp[G],e[G])[0,1])
    # per-fragment NNLS
    if a=='NAM': comps={'NAM':sp}
    elif a=='LPS': comps={f:gauss(modes[d['label']==f],act[d['label']==f]) for f in np.unique(d['label'])}
    else: comps={k:np.interp(X,*curves[k]) for k in curves}
    A=np.array([c[G] for c in comps.values()]).T; w,_=nnls(A,e[G]); fit=A@w
    ss=((e[G]-fit)**2).sum(); st=((e[G]-e[G].mean())**2).sum()
    res['nnls']=dict(r=float(np.corrcoef(fit,e[G])[0,1]),R2=float(1-ss/st),weights={k:float(v/w.sum()) for k,v in zip(comps,w)})
    # ratio of modes to band range: density
    res['density_per_100']=float(len(modes)/14)
    R[a]=res
    data[a]['sp']=sp; data[a]['comps']=comps; data[a]['nnlsfit']=None
json.dump(R,open(os.path.join(L,'05_Tables','DFT_vs_Experiment_results.json'),'w'),indent=1)
print(json.dumps({a:{k:v for k,v in R[a].items() if k!='bands'} for a in R},indent=1))
for a in R:
    print(a);
    for b in R[a]['bands']: print(b)
print('LTA csv x range check', ltd.groupby('Dataset').RamanShift.agg(['min','max']))
