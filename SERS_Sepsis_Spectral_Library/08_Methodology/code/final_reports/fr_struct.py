"""Molecular structure drawing with atoms highlighted for chosen vibrations (RDKit)."""
import numpy as np,io
from rdkit import Chem
from rdkit.Chem import AllChem,rdDetermineBonds
from rdkit.Chem.Draw import rdMolDraw2D
import fr_data as D
PAL=[(0.84,0.15,0.16),(0.12,0.47,0.71),(0.17,0.63,0.17),(0.58,0.40,0.74),(1.0,0.50,0.05),(0.09,0.75,0.81),(0.89,0.47,0.76),(0.55,0.34,0.29),(0.50,0.50,0.50),(0.74,0.74,0.13)]
def mol_for(mol):
    if mol=='NAM':
        xyz=D.MTP+r"\02_DFT_Calculation\NAM_beta_optimised_geometry.xyz"
        m=Chem.MolFromXYZFile(xyz); rdDetermineBonds.DetermineBonds(m,charge=0)
    else:
        m=Chem.MolFromMolFile(D.SDF[mol],removeHs=False)
    return m
def heavy_map(m):
    hm={};c=0
    for a in m.GetAtoms():
        if a.GetAtomicNum()>1: hm[a.GetIdx()]=c; c+=1
    return hm
def heavy_weights(mol,idx):
    r=D.sim(mol)['r']; Z=r['Z']; d=r['disp'][idx]; m=np.array([D.F.MASS[z] for z in Z]); w=m*(d**2).sum(1); w=w/w.sum()
    nb=r['nb']; hw=np.zeros(len(Z))
    for a in range(len(Z)):
        if Z[a]==1: hw[nb[a][0]]+=w[a]
        else: hw[a]+=w[a]
    return hw
def draw(mol,modes,path,size=(1500,950),title=None):
    """modes: list of (mode_index) -> highlighted with colours PAL[i]"""
    m=mol_for(mol); assert [a.GetAtomicNum() for a in m.GetAtoms()]==list(D.sim(mol)['r']['Z']),'atom order differs'
    hm=heavy_map(m); mh=Chem.RemoveHs(m); AllChem.Compute2DCoords(mh)
    W=np.array([heavy_weights(mol,i) for i in modes]); cols={}
    for a in range(W.shape[1]):
        k=int(np.argmax(W[:,a]))
        if W[k,a]>=0.07 and a in hm: cols[hm[a]]=PAL[k%len(PAL)]
    d=rdMolDraw2D.MolDraw2DCairo(*size); o=d.drawOptions(); o.legendFontSize=24; o.bondLineWidth=2.2; o.addAtomIndices=False; o.highlightRadius=0.42
    o.setBackgroundColour((1,1,1,1))
    d.DrawMolecule(mh,highlightAtoms=list(cols.keys()),highlightAtomColors=cols,highlightBonds=[],legend=title or '')
    d.FinishDrawing(); open(path,'wb').write(d.GetDrawingText())
def draw_plain(mol,path,size=(1400,900)):
    m=mol_for(mol); mh=Chem.RemoveHs(m); AllChem.Compute2DCoords(mh)
    d=rdMolDraw2D.MolDraw2DCairo(*size); o=d.drawOptions(); o.bondLineWidth=2.2; o.setBackgroundColour((1,1,1,1))
    d.DrawMolecule(mh); d.FinishDrawing(); open(path,'wb').write(d.GetDrawingText())
