import os,re,glob,numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.image as mpimg
M=r"C:\Users\sukes\Downloads\mtp"; L=r"C:\Users\sukes\Downloads\sukesh\SERS_Sepsis_Spectral_Library"
OUT=L+r"\04_Figures\Simulation_20261027"; os.makedirs(OUT,exist_ok=True)
plt.rcParams.update({'font.family':'Arial','font.size':9})
# 1 structures
items=[("N-Acetyl-Muramic-Acid_Conformer3D_medium.png","NAM (whole molecule)"),("3-Deoxy-D-Manno-Octulosonic-Acid_Conformer3D_medium.png","KDO"),("L-Glycero-D-Manno-Heptose_Conformer3D_medium.png","Heptose"),("D-Glucosamine_Conformer3D_medium.png","D-Glucosamine"),("Myristic-Acid_Conformer3D_medium.png","Myristic acid"),("Phosphoric-Acid_Conformer3D_medium.png","Phosphoric acid")]
fig,axs=plt.subplots(2,3,figsize=(9,6))
for ax,(f,t) in zip(axs.ravel(),items):
    ax.imshow(mpimg.imread(M+r"\10_Working_Archive\20-04"+"\\"+f)); ax.set_title(t,fontsize=10,fontweight='bold'); ax.axis('off')
fig.suptitle('PubChem 3D conformers used as starting structures (NAM, and the five LPS fragments)',x=.01,ha='left',fontsize=10,fontweight='bold')
fig.tight_layout(); fig.savefig(OUT+r"\S1_Starting_Structures.png",dpi=200); plt.close(fig)
# 2 NAM
n=pd.read_csv(M+r"\05_Experimental_Data\NAM\NAM_Raman_Archive\02_DFT_Calculation\NAM_calculated_modes_all_111.csv"); s=pd.read_csv(M+r"\05_Experimental_Data\NAM\NAM_Raman_Archive\03_Processed_Results\DFT_simulated_spectrum.csv")
fig,ax=plt.subplots(figsize=(10,3.6)); k=(n.freq_scaled>=400)&(n.freq_scaled<=1800)
ax.vlines(n.freq_scaled[k],0,n.intensity[k],color='#1f5fa8',lw=1.3,label='scaled modes (Placzek intensity, 785 nm)')
ax.plot(s.raman_shift_cm1,s.intensity_norm*n.intensity[k].max(),color='k',lw=1,label='Lorentzian broadened, FWHM 10 cm$^{-1}$')
ax.set_xlim(400,1800); ax.set_xlabel('Raman shift (cm$^{-1}$)'); ax.set_ylabel('Relative intensity'); ax.legend(frameon=False,fontsize=8); ax.spines[['top','right']].set_visible(False)
ax.set_title(f'NAM, beta anomer, B3LYP-D3BJ/6-311++G(d,p): {int(k.sum())} of 111 modes fall in 400-1800 cm$^{{-1}}$',loc='left',fontweight='bold',fontsize=9.5)
fig.tight_layout(); fig.savefig(OUT+r"\S2_NAM_Simulated_Spectrum.png",dpi=200); plt.close(fig)
# 3 LPS fragments
files={'KDO':"3-Deoxy-D-Manno-Octulosonic Acid_raman_act.txt",'D-Glucosamine':"D-glucosamine-opt_raman_act.txt",'Heptose':"L-Glycero-D-Manno-Heptose-opt_raman_act.txt",'Myristic acid':"Myristic Acid-opt_raman_act.txt",'Phosphoric acid':"Phosphoric acid-opt_raman_act.txt"}
cols=['#16a085','#8e44ad','#d35400','#7f8c8d','#c0392b']
fig,axs=plt.subplots(5,1,figsize=(10,7.5),sharex=True)
for ax,(nm,f),c in zip(axs,files.items(),cols):
    pk=np.array([tuple(map(float,l.lstrip('# ').split())) for l in open(M+r"\05_Experimental_Data\LPS\lps research\lps sim"+"\\"+f,errors='ignore') if re.match(r'#\s+[\d.]+\s+[\d.]+\s*$',l)])
    x=pk[:,0]*0.9613; y=pk[:,1]; m=(x>=400)&(x<=1800)
    ax.vlines(x[m],0,y[m]/y[m].max(),color=c,lw=1.4); ax.set_ylabel(nm,rotation=0,ha='right',va='center',fontsize=8.5); ax.set_yticks([]); ax.spines[['top','right','left']].set_visible(False)
    ax.text(1795,0.8,f'{int(m.sum())} modes in range',ha='right',fontsize=8,color=c)
axs[-1].set_xlim(400,1800); axs[-1].set_xlabel('Raman shift (cm$^{-1}$), scaled x 0.9613'); axs[0].set_title('LPS fragments, B3LYP/6-31G(d): scaled Raman modes (each normalised to its strongest mode)',loc='left',fontweight='bold',fontsize=9.5)
fig.tight_layout(); fig.savefig(OUT+r"\S3_LPS_Fragment_Spectra.png",dpi=200); plt.close(fig)
# 4 LTA fragments
d=pd.read_csv(M+r"\06_Simulation_DFT\LTA-simulation-main\LTA-simulation-main\LTA_combined_data.csv")
fig,axs=plt.subplots(3,1,figsize=(10,5.5),sharex=True)
for ax,(nm,lab),c in zip(axs,[('Glycerol-Phosphate','Glycerol-phosphate\n(2 units, charge -2)'),('D-Alanine','D-alanine'),('GlcNAc','N-acetyl-D-\nglucosamine')],['#c0392b','#2980b9','#27ae60']):
    g=d[d.Dataset==nm]; ax.plot(g.RamanShift,g.Intensity_norm,color=c,lw=1.3); ax.fill_between(g.RamanShift,0,g.Intensity_norm,color=c,alpha=.2)
    ax.set_ylabel(lab,rotation=0,ha='right',va='center',fontsize=8.5); ax.set_yticks([]); ax.spines[['top','right','left']].set_visible(False)
axs[-1].set_xlim(400,1800); axs[-1].set_xlabel('Raman shift (cm$^{-1}$), scaled x 0.96'); axs[0].set_title('LTA fragments, B3LYP/6-31G(d) with SMD water: broadened Raman curves (normalised)',loc='left',fontweight='bold',fontsize=9.5)
fig.tight_layout(); fig.savefig(OUT+r"\S4_LTA_Fragment_Spectra.png",dpi=200); plt.close(fig)
print(os.listdir(OUT))
