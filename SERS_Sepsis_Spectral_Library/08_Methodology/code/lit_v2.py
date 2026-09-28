REFS=[
 dict(id='L1',cite='Wu X., Zhao Y., Zughaier S.M. Highly sensitive detection and differentiation of endotoxins derived from bacterial pathogens by surface-enhanced Raman scattering. Biosensors 2021, 11(7), 234.',doi='10.3390/bios11070234',biomarker='LPS / LOS',technique='SERS',source='Neisseria meningitidis LOS/LPS; enteric LPS',verified='Band table read from publisher page (MDPI)'),
 dict(id='L2',cite='Yang Y., Xu B., Haverstick J., Ibtehaz N., Muszyński A., Chen X., Chowdhury M.E.H., Zughaier S.M., Zhao Y. Differentiation and classification of bacterial endotoxins based on surface enhanced Raman scattering and advanced machine learning. Nanoscale 2022, 14(24), 8806–8817.',doi='10.1039/d2nr01277d',biomarker='LPS (multiple species), LTA (B. subtilis), PGN',technique='SERS, 785 nm, Ag nanorod array',source='Commercial endotoxins',verified='Read from publisher PDF (RSC); detailed assignments in their Table S6 (not accessed)'),
 dict(id='L3',cite='Saikia D., Tanan C.B., Dhananjaya G., Hungund B.S., Mahanta N., Singh S.P. Validating phosphoethanolamine modification as a potential spectral marker of colistin resistance. Analyst 2025, 150, 281–289.',doi='10.1039/d4an01228c',biomarker='LPS / lipid A (in whole cells)',technique='Raman, 532 nm, whole bacterial cells',source='A. baumannii, E. coli (whole cells)',verified='Read from publisher PDF (RSC)'),
 dict(id='L4',cite='Kumar A., Islam M.R., Zughaier S.M., Chen X., Zhao Y. Precision classification and quantitative analysis of bacteria biomarkers via surface-enhanced Raman spectroscopy and machine learning. Spectrochim. Acta A 2024, 320, 124627.',doi='10.1016/j.saa.2024.124627',biomarker='LTA (among 6 biomarkers)',technique='SERS',source='Commercial LTA',verified='Abstract only; LTA band positions not accessible'),
 dict(id='L5',cite='Movasaghi Z., Rehman S., Rehman I.U. Raman spectroscopy of biological tissues. Appl. Spectrosc. Rev. 2007, 42(5), 493–541.',doi='10.1080/05704920701551530',biomarker='General (group frequencies)',technique='Raman review',source='—',verified='Citation verified (Crossref)'),
 dict(id='L6',cite='Wiercigroch E., Szafraniec E., Czamara K., Pacia M.Z., Majzner K., Kochan K., Kaczor A., Baranska M., Malek K. Raman and infrared spectroscopy of carbohydrates: a review. Spectrochim. Acta A 2017, 185, 317–335.',doi='10.1016/j.saa.2017.05.045',biomarker='Carbohydrates (group frequencies)',technique='Raman/IR review',source='—',verified='Citation verified (Crossref)'),
 dict(id='L8',cite='Grunert T., Jovanovic D., Sirisarn W., et al. Analysis of Staphylococcus aureus wall teichoic acid glycoepitopes by Fourier Transform Infrared Spectroscopy provides novel insights into the staphylococcal glycocode. Sci. Rep. 2018, 8, 1889.',doi='10.1038/s41598-018-20222-6',biomarker='Wall teichoic acid (related to LTA backbone chemistry)',technique='FTIR, intact S. aureus cells',source='S. aureus whole cells',verified='Read from publisher page (Nature)'),
 dict(id='L9',cite='Zou B., Zhao X., Liao J., Zhao Y. Near-infrared activity analysis and identification of fungal and bacterial markers. Microchem. J. 2025, 208, 112552.',doi='10.1016/j.microc.2024.112552',biomarker='N-acetylmuramic acid, N-acetylglucosamine',technique='NIR + DFT-calculated IR',source='Pure compounds (NIR); calculated IR',verified='Abstract/summary only; no Raman band positions reported'),
 dict(id='L7',cite='Czamara K., Majzner K., Pacia M.Z., Kochan K., Kaczor A., Baranska M. Raman spectroscopy of lipids: a review. J. Raman Spectrosc. 2015, 46, 4–20.',doi='10.1002/jrs.4607',biomarker='Lipids / phospholipids (group frequencies)',technique='Raman review',source='—',verified='Citation verified (Crossref)'),
 dict(id='L10',cite='Bansil R., Yannas I.V., Stanley H.E. Raman spectroscopy: a structural probe of glycosaminoglycans. Biochim. Biophys. Acta 1978, 541, 535–542.',doi='10.1016/0304-4165(78)90163-0',biomarker='Glycosaminoglycans (N-acetylated amino-sugar polymers; related to NAM chemistry)',technique='Normal Raman, pure polysaccharides',source='Purified glycosaminoglycans',verified='Citation verified (Crossref); full text not accessed – band values not extracted'),
 dict(id='L11',cite='Study of N-acetylamino saccharides with synchrotron-based ultraviolet resonance Raman spectroscopy: in combination with ATR far-ultraviolet spectroscopy. J. Phys. Chem. Lett. 2025, 16(7), 1769–.',doi='10.1021/acs.jpclett.4c03435',biomarker='N-acetylamino saccharides (compounds not verified; NAM inclusion unknown)',technique='UV resonance Raman (not 785 nm normal Raman)',source='Pure saccharides',verified='Identified via Crossref/ACS; full text not accessible (403) – not used for assignments'),
]
# literature band rows
LITBANDS=[
 ('LPS','L1','SERS',550,'β(CH2) in ring'),('LPS','L1','SERS',680,'δ(C-O-C); fatty acid'),('LPS','L1','SERS',850,'ν(C-O-C) 1,4-glycosidic link'),('LPS','L1','SERS',988,'β(CH) carbohydrates'),
 ('LPS','L1','SERS',1131,'ν(C-C) fatty acid'),('LPS','L1','SERS',1330,'δ(CH) phospholipid'),('LPS','L1','SERS',1450,'CH3/CH2 deformation'),('LPS','L1','SERS (enteric LPS)',543,'saccharide and lipid'),('LPS','L1','SERS (enteric LPS)',981,'saccharide and lipid'),
 ('LPS','L2','SERS 785 nm',735,'common LPS peak (assignment in source SI)'),('LPS','L2','SERS 785 nm',794,'common LPS peak'),('LPS','L2','SERS 785 nm',894,'common LPS peak'),('LPS','L2','SERS 785 nm',917,'common LPS peak'),
 ('LPS','L2','SERS 785 nm',1003,'common LPS peak'),('LPS','L2','SERS 785 nm',1333,'common LPS peak (C-H deformation)'),('LPS','L2','SERS 785 nm',1592,'common LPS peak'),('LPS','L2','SERS 785 nm',1614,'common LPS peak'),
 ('LPS','L3','Raman 532 nm, whole cells',1103,'lipopolysaccharide (A. baumannii)'),
 ('LTA','L2','SERS 785 nm',894,'C-O-H deformation (shared with chitin)'),('LTA','L2','SERS 785 nm',1333,'C-H deformation (shared with PGN)'),
 ('Phosphodiester (LTA backbone)','L5','Raman group frequency',1090,'ν_s(PO2−) phosphodiester'),('Phosphodiester (LTA backbone)','L5','Raman group frequency',813,'ν(O-P-O) phosphodiester'),
 ('Lipid acyl chains','L7','Raman group frequency','1440–1460','δ(CH2) scissoring'),('Carbohydrate (NAM sugar ring)','L6','Raman group frequency','< 600','pyranose ring skeletal deformations'),
 ('Carbohydrate (NAM sugar ring)','L6','Raman group frequency','800–950','anomeric region: ν(C-O-C), δ(C-C-H)'),('Carbohydrate (NAM sugar ring)','L6','Raman group frequency','1000–1200','ν(C-O), ν(C-C), δ(C-O-H)'),
]
# per-marker comparison: analyte, exp nominal, lit peak, diff (text), assignment, citation, confidence, wording
NOPURE='No directly comparable pure-compound normal Raman reference identified in the searched literature.'
# key: (analyte, nominal) -> (category, lit peak, diff, assignment, source/sample, technique, citation, confidence)
MLIT={
 ('NAM',541):('Primary marker','400–600 (region)','within region','Proposed: pyranose-ring skeletal deformation δ(C-C-O)/δ(C-C-C)','General carbohydrates (review)','Raman group-frequency table','L6','Low'),
 ('NAM',830):('Primary marker','800–950 (region)','within region','Proposed: ν(C-O-C)/ring mode in the carbohydrate anomeric region','General carbohydrates (review)','Raman group-frequency table','L6','Low'),
 ('NAM',870):('Primary marker','800–950 (region)','within region','Proposed: ν(C-O-C)/ν(C-C) ring mode (anomeric region)','General carbohydrates (review)','Raman group-frequency table','L6','Low'),
 ('NAM',929):('Primary marker','800–950 (region)','within region','Proposed: ν(C-O-C)/ν(C-C); possible lactyl C-COOH contribution','General carbohydrates / biomolecules (reviews)','Raman group-frequency table','L6, L5','Low'),
 ('NAM',955):('Primary marker','800–950 (upper edge)','≈ +5 beyond region','Proposed: ν(C-C) / CH3 rocking (N-acetyl or lactyl methyl) – tentative','General biomolecules (review)','Raman group-frequency table','L5, L6','Low'),
 ('NAM',1023):('Primary marker','1000–1200 (region)','within region','Proposed: ν(C-O)/ν(C-C) (C-OH stretching) of sugar ring','General carbohydrates (review)','Raman group-frequency table','L6','Low'),
 ('NAM',1127):('Primary marker','1000–1200 (region)','within region','Proposed: ν(C-O-C) (3-O-lactyl ether / ring) or ν(C-C)','General carbohydrates (review)','Raman group-frequency table','L6','Low'),
 ('NAM',458):('Supporting peak','400–600 (region)','within region','Proposed: pyranose-ring skeletal deformation','General carbohydrates (review)','Raman group-frequency table','L6','Low'),
 ('NAM',487):('Supporting peak','400–600 (region)','within region','Proposed: skeletal deformation','General carbohydrates (review)','Raman group-frequency table','L6','Low'),
 ('NAM',1249):('Supporting peak','—','—','No assignment proposed (possible amide III / CH deformation region; not verified)','—','—','—','Uncertain'),
 ('NAM',584):('Uncertain','—','—','Unassigned','—','—','—','Uncertain'),
 ('NAM',1059):('Uncertain','—','—','Unassigned (detected in only 31 % of valid spectra)','—','—','—','Uncertain'),
 ('NAM',1155):('Uncertain','—','—','Unassigned','—','—','—','Uncertain'),
 ('NAM',1589):('Supporting peak','—','—','No assignment proposed (unassigned; reproducible)','—','—','—','Uncertain'),
 ('NAM',1346):('Uncertain','—','—','Sharp band inside glass zone; intensity confounded by glass (CV 17 %)','—','—','—','Uncertain'),
 ('NAM',1393):('Uncertain','—','—','Sharp band inside glass zone; intensity confounded by glass (CV 18 %)','—','—','—','Uncertain'),
 ('NAM',1451):('Uncertain','1440–1460 (CH2/CH3 def.)','≈ 0','Proposed: δ(CH2/CH3); inside glass zone','Lipids/biomolecules (review)','Raman group-frequency table','L7','Uncertain'),
 ('LTA',1092):('Primary marker','1090–1095 (ν_s PO2−)','≈ 0 to +2','Proposed: ν_s(PO2−) of phosphodiester (poly-glycerophosphate backbone)','Phosphodiesters/phospholipids (reviews); teichoic-acid phosphodiester region in IR of S. aureus cells','Raman group-frequency table; FTIR (whole cells)','L5, L7, L8','Moderate'),
 ('LTA',802):('Primary marker','~813 (ν O-P-O)','≈ −11','Proposed: ν(O-P-O) phosphodiester stretch','Nucleic acids/biomolecules (review)','Raman group-frequency table','L5','Low'),
 ('LTA',861):('Primary marker','800–950 (region)','within region','Proposed: ν(C-C)/ν(C-O-C) of glycerol / sugar substituents','General carbohydrates (review)','Raman group-frequency table','L6','Low'),
 ('LTA',1459):('Supporting peak','1440–1460 (δ CH2)','≈ 0 to +9','Proposed: δ(CH2) scissoring (acyl chains of glycolipid anchor); non-specific','Lipids (review)','Raman group-frequency table','L7','Low'),
 ('LTA',541):('Uncertain','400–600 (region)','within region','Unassigned (skeletal region; CV 27 %)','—','—','—','Uncertain'),
 ('LTA',1367):('Glass/background','—','—','Glass-associated feature (inside glass zone; removed by glass-template correction; 2/9 detected)','Empty glass slide (this work)','—','—','Not applicable'),
}
FUTURE=[('NAM','785 nm, 90 %, 30 s, 5 acc','Replicate at reference condition (independent spots/slides); matched glass blank'),
 ('LTA','785 nm, 80 %, 45 s, 2 acc','Preliminary reference (n = 4): add ≥ 6 independent spots (ideally a second day) to reach n ≥ 10; matched glass blank'),
 ('LPS','785 nm, 70 / 80 / 90 %, 30 s, 5 acc (screening)','≥ 5 independent spots per power on glass slide; select reference only after comparison with matched blank'),
 ('Glass blank','Same settings as the corresponding sample','Same instrument, wavelength, power, integration, accumulations, objective and slide type'),
 ('If saturation occurs','Reduce power and/or integration','Check raw counts in 400–1800 cm-1 and at the laser line; document the change')]
