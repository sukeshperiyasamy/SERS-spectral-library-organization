# Whole-molecule LTA model (3 glycerol-phosphate units, 2 D-Ala, 1 alpha-GlcNAc; B3LYP/3-21G) vs the pooled LTA reference v2.1 (n = 17)
# and vs the fragment-sum calculation; same tests as dft_compare_1.py
import runpy,os,json,numpy as np,pandas as pd
ns=runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)),'dft_compare_1.py'))
X,G,nmatch,decoy,gauss,mm,data=[ns[k] for k in ('X','G','nmatch','decoy','gauss','mm','data')]
L=ns['L']; SIM=r"C:\Users\sukes\Downloads\sukesh\simulation\lta output simulation\quick_B3LYP-3-21G"
rd=pd.read_csv(f"{L}/03_Reference_Spectra/LTA/LTA_Bulk_Reference_20261028_Pooled_Mean_SD.csv",comment='#')
e=np.interp(X,rd.iloc[:,0].values,rd['Normalised_mean'].values)
mk=pd.read_csv(f"{L}/03_Reference_Spectra/LTA/LTA_Reference_20261028_Pooled_Marker_Peaks.csv",comment='#')
mk=mk[(mk.glass_zone==False)&mk['class'].str.startswith(('C1','C2'))]
bands=[(round(v,1),'Primary' if c.startswith('C1') else 'Supporting') for v,c in zip(mk.pos_mean,mk['class'])]
a=pd.read_csv(os.path.join(SIM,'lta_model_raman_act.csv')); nu=a.iloc[:,0].values*0.965; S=a.iloc[:,1].values
nu0=1e7/785; I=S*(nu0-nu)**4/(nu*(1-np.exp(-1.4388*nu/298.15))); I=I/I.max()
k=(nu>=400)&(nu<=1800); modes=nu[k]; act=I[k]/I[k].max(); strong=modes[act>=0.15]
def block(modes,act,strong):
    r=dict(n_modes=int(len(modes)),n_strong=int(len(strong)),bands=[])
    for b,role in bands:
        i=np.argmin(np.abs(modes-b)); r['bands'].append(dict(exp=b,role=role,calc=float(modes[i]),delta=float(b-modes[i]),act=float(act[i])))
    for tol in (5,10,18):
        n=nmatch(bands,modes,tol); dc=decoy(bands,modes,tol); ns_=nmatch(bands,strong,tol); dcs=decoy(bands,strong,tol)
        r[f't{tol}']=dict(real=int(n),decoy_mean=float(dc.mean()),decoy_sd=float(dc.std()),p=float((dc>=n).mean()),real_strong=int(ns_),p_strong=float((dcs>=ns_).mean()))
    d=np.array([b['delta'] for b in r['bands']]); r['mae']=float(np.mean(np.abs(d))); return r
res=dict(n_bands=len(bands),bands_used=bands); res['model']=block(modes,act,strong)
sp=mm(gauss(modes,act)); res['model']['r_whole']=float(np.corrcoef(sp[G],e[G])[0,1])
s=pd.read_csv(os.path.join(SIM,'lta_model_spectrum_785nm.csv')); sp2=mm(np.interp(X,s.iloc[:,0].values,s.iloc[:,1].values)); res['model']['r_whole_csv']=float(np.corrcoef(sp2[G],e[G])[0,1])
fd=data['LTA']; fm=fd['modes']; fa=fd['act']; res['frag']=block(fm,fa,fm[fa>=0.15]); fsp=ns['data']['LTA']['sp']; res['frag']['r_whole']=float(np.corrcoef(fsp[G],e[G])[0,1])
from scipy.optimize import nnls
comps=dict(ns['data']['LTA']['comps']); A=np.array([c[G] for c in comps.values()]).T; w,_=nnls(A,e[G]); res['frag']['nnls_r']=float(np.corrcoef(A@w,e[G])[0,1])
comps['LTA model']=sp; A=np.array([c[G] for c in comps.values()]).T; w,_=nnls(A,e[G]); res['nnls_all']=dict(r=float(np.corrcoef(A@w,e[G])[0,1]),weights={k_:float(v/w.sum()) for k_,v in zip(comps,w)})
# old (April) comparison reference for continuity
res['top_modes']=[(float(m),float(x)) for m,x in sorted(zip(modes,act),key=lambda t:-t[1])[:12]]
json.dump(res,open(os.path.join(L,'05_Tables','LTAmodel_vs_LTA_results.json'),'w'),indent=1)
print(json.dumps(res,indent=1))
