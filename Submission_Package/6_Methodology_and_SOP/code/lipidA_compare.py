# Whole-molecule (shortened Kdo2-lipid A, B3LYP/3-21G) vs the library LPS reference; same tests as dft_compare_1.py
import runpy,os,json,numpy as np,pandas as pd
ns=runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)),'dft_compare_1.py'))
X,G,ref,libbands,nmatch,decoy,gauss,mm,data,R=[ns[k] for k in ('X','G','ref','libbands','nmatch','decoy','gauss','mm','data','R')]
L=ns['L']; SIM=r"C:\Users\sukes\Downloads\sukesh\lps output simulation"
a=pd.read_csv(os.path.join(SIM,'lipidA_raman_act.csv')); nu=a.freq_cm_1.values*0.965 if 'freq_cm_1' in a else a.iloc[:,0].values*0.965; S=a.iloc[:,1].values
nu0=1e7/785; I=S*(nu0-nu)**4/(nu*(1-np.exp(-1.4388*nu/298.15))); I=I/I.max()
k=(nu>=400)&(nu<=1800); modes=nu[k]; act=I[k]; act=act/act.max()
e=ref('LPS'); bands=libbands('LPS'); strong=modes[act>=0.15]
res=dict(n_modes=int(len(modes)),n_strong=int(len(strong)),bands=[])
for b,role in bands:
    i=np.argmin(np.abs(modes-b)); res['bands'].append(dict(exp=b,role=role,calc=float(modes[i]),delta=float(b-modes[i]),act=float(act[i])))
for tol in (5,10,18):
    r=nmatch(bands,modes,tol); dc=decoy(bands,modes,tol); rs=nmatch(bands,strong,tol); dcs=decoy(bands,strong,tol)
    res[f't{tol}']=dict(real=int(r),decoy_mean=float(dc.mean()),decoy_sd=float(dc.std()),p=float((dc>=r).mean()),real_strong=int(rs),decoy_strong_mean=float(dcs.mean()),p_strong=float((dcs>=rs).mean()))
d_=np.array([b['delta'] for b in res['bands']]); res['mae']=float(np.mean(np.abs(d_)))
sp=mm(gauss(modes,act)); res['r_whole']=float(np.corrcoef(sp[G],e[G])[0,1])
fr=R['LPS']; res['frag_r_equal']=fr['r_equal']; res['frag_mae']=fr['mae']; res['frag']={t:fr[t] for t in('t5','t10','t18')}; res['frag_bands']=fr['bands']
# smoothed (SIM csv) spectrum
s=pd.read_csv(os.path.join(SIM,'lipidA_spectrum_785nm.csv')); sp2=mm(np.interp(X,s.iloc[:,0].values,s.iloc[:,1].values)); res['r_whole_csv']=float(np.corrcoef(sp2[G],e[G])[0,1])
# lipid A + fragments combined (NNLS)
from scipy.optimize import nnls
comps={'Lipid A model':sp}; fd=data['LPS']
for f in np.unique(fd['label']): comps[f]=gauss(fd['modes'][fd['label']==f],fd['act'][fd['label']==f])
A=np.array([c[G] for c in comps.values()]).T; w,_=nnls(A,e[G]); fit=A@w
res['nnls_all']=dict(r=float(np.corrcoef(fit,e[G])[0,1]),weights={k_:float(v/w.sum()) for k_,v in zip(comps,w)})
comps2={k_:v for k_,v in comps.items() if k_!='Lipid A model'}; A2=np.array([c[G] for c in comps2.values()]).T; w2,_=nnls(A2,e[G]); res['nnls_frag_r']=float(np.corrcoef(A2@w2,e[G])[0,1])
# literature SERS bands vs computed and vs experimental peaks
lit={850:None,989:None,1131:None,1330:None}
for p in lit:
    j=np.argmin(np.abs(modes-p)); strongest=modes[(np.abs(modes-p)<=25)][np.argmax(act[(np.abs(modes-p)<=25)])]
    lit[p]=dict(nearest=float(modes[j]),nearest_act=float(act[j]),strongest_within25=float(strongest))
res['lit']=lit
res['top_modes']=[(float(m),float(x)) for m,x in sorted(zip(modes,act),key=lambda t:-t[1])[:12]]
json.dump(res,open(os.path.join(L,'05_Tables','LipidA_vs_LPS_results.json'),'w'),indent=1)
print(json.dumps({k_:v for k_,v in res.items() if k_ not in('frag_bands',)},indent=1))
