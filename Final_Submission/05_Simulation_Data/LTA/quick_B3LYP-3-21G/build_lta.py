"""Single-molecule S. aureus-type LTA model: 3 glycerol-phosphate units (2 phosphodiesters),
D-Ala esters on the two terminal glycerols, alpha-GlcNAc on the central glycerol. Net charge 0."""
import itertools
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.rdMolDescriptors import CalcMolFormula

glcnac = "CC(=O)N[C@@H]1[C@@H](O)[C@H](O)[C@@H](CO)O[C@@H]1O"   # anomeric tag flipped vs the beta file -> alpha
tmpl = (glcnac + "[C{c2}H](COP(=O)([O-])OC[C{a}H](OC(=O)[C{x}H](C)[NH3+])CO)"
        "COP(=O)([O-])OC[C{b}H](OC(=O)[C{y}H](C)[NH3+])CO")
best = None
for c2, a, b, x, y in itertools.product(["@", "@@"], repeat=5):
    smi = tmpl.format(c2=c2, a=a, b=b, x=x, y=y)
    m = Chem.MolFromSmiles(smi)
    cip = dict(Chem.FindMolChiralCenters(m, useLegacyImplementation=False))
    ala = [v for k, v in cip.items() if m.GetAtomWithIdx(k).GetTotalNumHs() == 1
           and any(n.GetFormalCharge() == 1 for n in m.GetAtomWithIdx(k).GetNeighbors())]
    if ala == ["R", "R"] and a == b:        # D-Ala (R) on both, symmetric glycerol arms
        best = (smi, m); break
smi, m = best
print(smi, CalcMolFormula(m), Chem.GetFormalCharge(m))
print(Chem.FindMolChiralCenters(m, useLegacyImplementation=False))
open("lta_model.smi", "w").write(smi + "\n")

mh = Chem.AddHs(m)
ps = AllChem.ETKDGv3(); ps.randomSeed = 7; ps.useRandomCoords = True
cids = AllChem.EmbedMultipleConfs(mh, 300, ps)
e = [r[1] for r in AllChem.MMFFOptimizeMoleculeConfs(mh, maxIters=5000, numThreads=0)]
b = min(range(len(e)), key=e.__getitem__)
print(len(cids), "confs, atoms", mh.GetNumAtoms(), "E", round(e[b], 1))
conf = mh.GetConformer(cids[b])
xyz = "\n".join(f" {a.GetSymbol():2s} {conf.GetAtomPosition(a.GetIdx()).x:14.8f} "
                f"{conf.GetAtomPosition(a.GetIdx()).y:14.8f} {conf.GetAtomPosition(a.GetIdx()).z:14.8f}"
                for a in mh.GetAtoms())
gjf = f"""%nprocshared=20
%mem=50GB
%chk=lta_model.chk
# opt pm6

PM6 pre-optimisation of LTA model

{Chem.GetFormalCharge(mh)} 1
{xyz}

--Link1--
%nprocshared=20
%mem=50GB
%chk=lta_model.chk
# opt freq=raman b3lyp/6-31g(d) scrf=(pcm,solvent=water) geom=allcheck guess=read

"""
open("lta_model.gjf", "w", newline="\r\n").write(gjf)
Chem.MolToMolFile(mh, "lta_model.sdf", confId=cids[b])
