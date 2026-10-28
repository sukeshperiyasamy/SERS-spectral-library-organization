"""Mode-character analysis of Gaussian frequency output: which atoms move in each calculated vibration.
Reads the displacement table of a Gaussian log (freq=raman) and the final geometry, shares the motion among atom groups
(kinetic-energy weight = mass x displacement^2) and gives each mode a tentative character label.
Displacements are printed to two decimals in the log, so labels are tentative."""
import re,numpy as np
MASS={1:1.008,6:12.011,7:14.007,8:15.999,15:30.974,16:32.06}
COV={1:.31,6:.76,7:.71,8:.66,15:1.07,16:1.05}
def parse(log):
    txt=open(log,errors='ignore').read().split('\n')
    # last standard orientation
    idx=[i for i,l in enumerate(txt) if 'Standard orientation' in l][-1]
    Z=[];XYZ=[]; j=idx+5
    while not txt[j].startswith(' ---'):
        f=txt[j].split(); Z.append(int(f[1])); XYZ.append([float(f[3]),float(f[4]),float(f[5])]); j+=1
    Z=np.array(Z); XYZ=np.array(XYZ); n=len(Z)
    # frequency blocks of the last (frequency) job
    fr=[];act=[];dsp=[]
    i=0
    start=[k for k,l in enumerate(txt) if l.strip().startswith('Frequencies --')]
    for k in start:
        fs=[float(x) for x in txt[k].split('--')[1].split()]
        a=None
        for q in range(k,k+8):
            if 'Raman Activ' in txt[q]: a=[float(x) for x in txt[q].split('--')[1].split()]
        hdr=[q for q in range(k,k+14) if txt[q].strip().startswith('Atom  AN')][0]
        blk=np.zeros((len(fs),n,3))
        for r in range(n):
            f=txt[hdr+1+r].split(); v=[float(x) for x in f[2:]]
            for m in range(len(fs)): blk[m,r]=v[3*m:3*m+3]
        fr+=fs; act+=(a if a else [np.nan]*len(fs)); dsp.append(blk)
    return Z,XYZ,np.array(fr),np.array(act),np.concatenate(dsp)
def graph(Z,XYZ):
    n=len(Z); D=np.linalg.norm(XYZ[:,None]-XYZ[None],axis=2); nb=[[] for _ in range(n)]
    for a in range(n):
        for b in range(a+1,n):
            if D[a,b]<1.25*(COV[Z[a]]+COV[Z[b]]): nb[a].append(b); nb[b].append(a)
    return nb,D
def groups(Z,XYZ):
    nb,D=graph(Z,XYZ); n=len(Z); g=['C']*n
    for a in range(n):
        z=Z[a]
        if z==15: g[a]='P'
        elif z==7: g[a]='N'
        elif z==1:
            g[a]='H_C' if Z[nb[a][0]]==6 else 'H_NO'
        elif z==8:
            if any(Z[b]==15 for b in nb[a]): g[a]='O_P'
            elif len(nb[a])==1 and Z[nb[a][0]]==6 and D[a,nb[a][0]]<1.30: g[a]='O_CO'
            else: g[a]='O'
    for a in range(n):
        if Z[a]==6 and any(g[b]=='O_CO' for b in nb[a]): g[a]='C_CO'
    return g,nb
def shares(Z,XYZ,disp):
    g,nb=groups(Z,XYZ); m=np.array([MASS[z] for z in Z]); keys=['P','O_P','O_CO','C_CO','N','H_C','H_NO','O','C']
    out=np.zeros((len(disp),len(keys)))
    for i,d in enumerate(disp):
        w=m*(d**2).sum(1); w=w/w.sum()
        for k,key in enumerate(keys): out[i,k]=w[[a for a in range(len(g)) if g[a]==key]].sum()
    return keys,out,g,nb,np.array([(m*(d**2).sum(1)/ (m*(d**2).sum(1)).sum()) for d in disp])
def label(f,s,keys):
    S=dict(zip(keys,s)); H=S['H_C']+S['H_NO']; PO=S['P']+S['O_P']; CO=S['C_CO']+S['O_CO']
    if f>=1650 and CO>=0.40: return 'C=O stretch (ester / carbonyl)'
    if f>=1450 and (S['N']+S['H_NO'])>=0.35: return 'N-H bending (ammonium / amide)'
    if PO>=0.45: return 'phosphate P-O stretch' if f>=900 else 'phosphate P-O deformation'
    if H>=0.55 and f>=1300: return 'C-H / O-H bending (CH2, CH3)'
    if H>=0.55: return 'C-H bending / CH2 rocking and twisting'
    if f<650: return 'skeletal / ring deformation'
    if f<1250: return 'C-O and C-C stretching (sugar / glycerol backbone)'
    return 'mixed C-H bending and C-O stretching'
def analyse(log):
    Z,XYZ,fr,act,disp=parse(log); keys,sh,g,nb,_=shares(Z,XYZ,disp)
    lab=[label(f,s,keys) for f,s in zip(fr,sh)]
    return dict(Z=Z,XYZ=XYZ,freq=fr,act=act,disp=disp,keys=keys,share=sh,label=np.array(lab),groups=g,nb=nb)
