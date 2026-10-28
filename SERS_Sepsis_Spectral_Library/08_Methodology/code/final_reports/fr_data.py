"""Data loading and peak matching for the nine final reports (experimental bulk, simulation, comparison)."""
import os,glob,pickle,numpy as np,pandas as pd
import fr_modes as F
ROOT=r"C:\Users\sukes\Downloads\sukesh"; LIB=ROOT+r"\SERS_Sepsis_Spectral_Library"; SIMD=ROOT+r"\simulation"; MTP=r"C:\Users\sukes\Downloads\mtp\05_Experimental_Data\NAM\NAM_Raman_Archive"
X=np.arange(400,1801,1.0); GLASS=(1308,1455)
COL={'NAM':'#1b6ca8','LPS':'#c0392b','LTA':'#2a7d46'}; CALC='#e08a00'
NAME={'NAM':'N-acetylmuramic acid (NAM)','LPS':'lipopolysaccharide (LPS)','LTA':'lipoteichoic acid (LTA)'}
LOGS={'LTA':SIMD+r"\lta output simulation\quick_B3LYP-3-21G\lta_model.out",'LPS':SIMD+r"\lps output simulation\lipidA_short.out",'NAM':MTP+r"\02_DFT_Calculation\NAM_beta_Gaussian16_B3LYP-D3BJ_6-311++Gdp.log"}
SDF={'LTA':SIMD+r"\lta output simulation\quick_B3LYP-3-21G\lta_model.sdf",'LPS':SIMD+r"\lps output simulation\lipidA_short.sdf"}
SCALE={'LTA':0.965,'LPS':0.965}
MEMBERS={'NAM':'03_Reference_Spectra/NAM/NAM_Reference_Members.csv','LPS':'03_Reference_Spectra/LPS/LPS_Reference_Members.csv','LTA':'03_Reference_Spectra/LTA/LTA_Reference_20261028_Pooled_Members.csv'}
REFCSV={'NAM':'03_Reference_Spectra/NAM/NAM_Bulk_Reference_Mean_SD.csv','LPS':'03_Reference_Spectra/LPS/LPS_Bulk_Reference_Mean_SD.csv','LTA':'03_Reference_Spectra/LTA/LTA_Bulk_Reference_20261028_Pooled_Mean_SD.csv'}
MARK={'NAM':'03_Reference_Spectra/NAM/NAM_Reference_Marker_Peaks.csv','LPS':'03_Reference_Spectra/LPS/LPS_Reference_Marker_Peaks.csv','LTA':'03_Reference_Spectra/LTA/LTA_Reference_20261028_Pooled_Marker_Peaks.csv'}
# expected vibration family and plain description for every experimental peak (tentative; from the group-frequency assignments of the study)
FAM={'SK':'skeletal / ring deformation','PO':'phosphate P-O motion','CC':'C-O and C-C stretching','HB':'C-H / N-H / O-H bending','CO':'C=O stretch'}
EXPECT={
 'NAM':{457:(('SK',),'pyranose-ring skeletal deformation'),487:(('SK',),'skeletal deformation'),541:(('SK',),'ring deformation, C-C-O / C-C-C'),
        829:(('CC',),'C-O-C and ring stretching (sugar "anomeric" region)'),870.5:(('CC',),'C-O-C and C-C ring stretching'),929:(('CC',),'C-O-C / C-C stretching (lactyl side chain may contribute)'),
        955:(('CC','HB'),'C-C stretching or CH3 rocking (tentative)'),1022.7:(('CC',),'C-O / C-C stretching of the ring'),1127:(('CC',),'C-O-C stretching (lactyl ether / ring)'),
        1248.7:(('CC','HB'),'no firm assignment (amide III or C-H deformation region)'),1589.5:(('HB','CO'),'no firm assignment')},
 'LPS':{424.8:(('SK',),'low-frequency skeletal / ring deformation (not assigned in the literature)'),765.5:(('CC','SK','PO'),'no assignment in the literature'),861.1:(('CC',),'glycosidic C-O-C and sugar ring modes'),
        995.8:(('CC','HB'),'C-H bending or sugar C-O-C'),1080.5:(('CC','PO'),'C-O stretching of sugars and / or symmetric PO2- stretch')},
 'LTA':{418.4:(('SK','PO'),'low-frequency skeletal deformation (no firm assignment)'),539.3:(('SK',),'skeletal / ring deformation'),722.6:(('CC',),'C-O / C-C stretching (no firm assignment)'),
        799.1:(('PO','CC'),'O-P-O stretching of the phosphodiester (P-O-C ester stretching)'),861.9:(('CC',),'C-C and C-O-C stretching of glycerol and sugar'),1010.6:(('CC',),'C-O / C-C stretching'),
        1092.0:(('PO',),'symmetric PO2- stretch of the phosphodiester backbone'),1460.1:(('HB',),'CH2 / CH3 bending'),1750.8:(('CO',),'ester C=O stretch (supported by the calculation only)')}}
def fam(label,f):
    l=label
    if l.startswith('phosphate P-O deformation'): return ('PO','SK')
    if l.startswith('phosphate'): return ('PO',)
    if l.startswith('skeletal'): return ('SK',)
    if l.startswith('C-O and C-C') or l.startswith('mixed'): return ('CC',)
    if l.startswith('C=O'): return ('CO',)
    return ('HB',)
def relabel(freq_s,share,keys,Z=None):
    out=[]
    for f,s in zip(freq_s,share):
        S=dict(zip(keys,s)); H=S['H_C']+S['H_NO']; PO=S['P']+S['O_P']; CO=S['C_CO']+S['O_CO']
        if f>=1500 and CO>=0.5: l='C=O stretch (carbonyl)'
        elif f>=1450 and (S['N']+S['H_NO'])>=0.35: l='N-H bending (ammonium / amide)'
        elif PO>=0.45: l='phosphate P-O stretch' if f>=900 else 'phosphate P-O deformation'
        elif H>=0.55 and f>=1300: l='C-H / O-H bending (CH2, CH3)'
        elif H>=0.55: l='C-H bending / CH2 rocking and twisting'
        elif f<650: l='skeletal / ring deformation'
        elif f<1250: l='C-O and C-C stretching (backbone)'
        else: l='mixed C-H bending and C-O stretching'
        out.append(l)
    return np.array(out)
_cache={}
def sim(mol):
    if mol in _cache: return _cache[mol]
    r=F.analyse(LOGS[mol])
    if mol=='NAM':
        nm=pd.read_csv(MTP+r"\02_DFT_Calculation\NAM_calculated_modes_all_111.csv"); fs=nm.freq_scaled.values; inten=nm.intensity.values/nm.intensity.values[(fs>=400)&(fs<=1800)].max()
        spec=pd.read_csv(MTP+r"\03_Processed_Results\DFT_simulated_spectrum.csv"); sx,sy=spec.raman_shift_cm1.values,spec.intensity_norm.values
    else:
        fs=r['freq']*SCALE[mol]; S=r['act']; nu0=1e7/785
        I=S*(nu0-fs)**4/(fs*(1-np.exp(-1.4388*fs/298.15))); inten=I/I[(fs>=400)&(fs<=1800)].max(); sx=None
    lab=relabel(fs,r['share'],r['keys']); k=(fs>=400)&(fs<=1800)
    d=dict(r=r,f=fs,I=inten,label=lab,k=k,fam=[fam(l,f) for l,f in zip(lab,fs)],spec=sx)
    if mol=='NAM': d['sx'],d['sy']=sx,sy
    _cache[mol]=d; return d
def broaden(f,I,fwhm=12):
    g=fwhm/2; y=np.zeros_like(X)
    for a,b in zip(f,I): y+=b*g**2/((X-a)**2+g**2)
    return y/y.max()
def calc_curve(mol):
    d=sim(mol)
    if mol=='NAM':
        y=np.interp(X,d['sx'],d['sy']); return (y-y.min())/(y.max()-y.min())
    return broaden(d['f'][d['k']],d['I'][d['k']],12)
def find_proc(name):
    p=glob.glob(LIB+r"\02_Processed_Spectra\**\%s"%name.replace('.csv','_processed.csv'),recursive=True); return p[0] if p else None
def read_proc(p):
    d=pd.read_csv(p,comment='#'); return d
def exp_members(mol):
    m=pd.read_csv(LIB+'/'+MEMBERS[mol]); out=[]
    for f in m.library_file:
        p=find_proc(f)
        if p: d=read_proc(p); out.append(np.interp(X,d['Raman_Shift_cm-1'],d['Normalised_0to1']));
    return np.array(out)
def exp_ref(mol):
    r=pd.read_csv(LIB+'/'+REFCSV[mol],comment='#'); c='Normalised_mean'
    return np.interp(X,r.iloc[:,0],r[c]),np.interp(X,r.iloc[:,0],r['Normalised_SD']),np.interp(X,r.iloc[:,0],r['BaselineCorrected_mean_counts'])
def peaks(mol):
    m=pd.read_csv(LIB+'/'+MARK[mol],comment='#'); cc='class' if 'class' in m.columns else 'role'
    m=m[m['glass_zone']==False] if 'glass_zone' in m.columns else m
    out=[]
    for _,r in m.iterrows():
        c=str(r[cc]);
        if c.startswith(('C1','C2','Primary','Supporting')): out.append((float(r.pos_mean) if 'pos_mean' in m.columns else float(r.band),'main' if c.startswith(('C1','Primary')) else 'supporting'))
    return out
def blank_mean(mol):
    pat={'NAM':'Glass_Blank_20260529_P005pct_T05s_A01_S0*_processed.csv','LPS':'Glass_Blank_20260928_P060pct_T40s_A05_S03_processed.csv'}
    if mol in pat: ps=glob.glob(LIB+r"\02_Processed_Spectra\Glass_Blank\\"+pat[mol])
    else:
        q=pd.read_csv(LIB+'/07_QC_and_Exclusions/LTA_Reference_Session_20261028_QC_Log.csv'); b=q[(q.category=='Glass_Blank')&(q.QC!='BLANK-SUSPECT')&(q.QC!='BLANK-SATURATED')]
        ps=[find_proc(f) for f in b.library_file]
    ys=[];cs=[]
    for p in ps:
        if not p: continue
        d=read_proc(p); ys.append(np.interp(X,d['Raman_Shift_cm-1'],d['Normalised_0to1'])); cs.append(np.interp(X,d['Raman_Shift_cm-1'],d['BaselineCorrected_counts']))
    return np.mean(ys,0),np.mean(cs,0),len(ys)
def match(mol,tol_shift=50):
    d=sim(mol); res=[]; f=d['f']; I=d['I']; k=d['k']
    for pos,role in peaks(mol):
        key=min(EXPECT[mol],key=lambda a:abs(a-pos)); fams,desc=EXPECT[mol][key]
        cand=[i for i in np.where(k&(I>=0.02))[0] if abs(f[i]-pos)<=tol_shift and any(x in fams for x in d['fam'][i])]
        nearest=int(np.argmin(np.where(k,np.abs(f-pos),1e9)))
        if cand:
            # prefer the closest mode of the expected type; among modes within 4 cm-1 of that one, take the strongest
            i0=min(cand,key=lambda i:abs(f[i]-pos)); near=[i for i in cand if abs(f[i]-f[i0])<=4]; i=max(near,key=lambda i:I[i])
            dl=pos-f[i]; st='agrees' if abs(dl)<=10 else 'shifted'
            res.append(dict(exp=pos,role=role,calc=float(f[i]),delta=float(dl),I=float(I[i]),label=d['label'][i],status=st,desc=desc,idx=int(i),near_calc=float(f[nearest]),near_label=d['label'][nearest],near_I=float(I[nearest])))
        else:
            res.append(dict(exp=pos,role=role,calc=None,delta=None,I=None,label=None,status='none',desc=desc,idx=None,near_calc=float(f[nearest]),near_label=d['label'][nearest],near_I=float(I[nearest])))
    return res
def pearson(mol):
    e,_,_=exp_ref(mol); c=calc_curve(mol); G=~((X>=GLASS[0])&(X<=GLASS[1])); return float(np.corrcoef(e[G],c[G])[0,1])
