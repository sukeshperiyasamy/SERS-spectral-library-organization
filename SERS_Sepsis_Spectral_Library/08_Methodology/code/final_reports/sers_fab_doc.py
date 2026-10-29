"""Word document on how the SERS chips were made, from the mtp project documents, the lab photos and the measured data."""
import os, glob, pickle, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PIL import Image
import fr_docs as FD
FS = r"C:\Users\sukes\Downloads\sukesh\Final_Submission"
OUT = os.path.join(FS, '10_SERS_Chip_Fabrication'); os.makedirs(os.path.join(OUT, 'figures'), exist_ok=True)
MTP = r"C:\Users\sukes\Downloads\mtp"
IMG = os.path.join(MTP, r"05_Experimental_Data\SERS_and_R6G_sessions\img sensor")
P = pickle.load(open(os.path.join(FS, r'09_SERS_All_Sessions\04_Tables\sers_all_results.pkl'), 'rb')); R6 = P['R6']
plt.rcParams.update({'font.family': 'Arial', 'font.size': 9})

# process flow
steps = [('1. Cut', 'n-type Si(100) wafer\nbroken into pieces\n(about 1 x 1 cm)'), ('2. Clean', 'acetone, IPA, DI water\n5 min ultrasonic each'),
         ('3. Oxide strip', '~10 % HF dip\n30-60 s, short DI rinse'), ('4. MACE etch', 'AgNO3 + HF in DI water\nplastic beaker, room temp.\n2-10 min'),
         ('5. Rinse, dry', 'DI water rinse\nN2 dry'), ('6. Check', 'visual: dark matte surface\nR6G test, Si peak, blank'),
         ('7. Deposit', 'drop-cast analyte\ndry'), ('8. Measure', '785 nm Raman\nmultiple spots')]
fig, ax = plt.subplots(figsize=(10, 4.2)); ax.axis('off'); ax.set_xlim(0, 4); ax.set_ylim(-0.25, 2.5)
cols = ['#dfe9f5', '#dfe9f5', '#fde3d6', '#fde3d6', '#dfe9f5', '#e3f1e6', '#efe4f5', '#efe4f5']
for i, ((h, t), c) in enumerate(zip(steps, cols)):
    x, y = i % 4, 1.3 if i < 4 else 0.05
    ax.add_patch(FancyBboxPatch((x + .06, y), .84, 1.0, boxstyle='round,pad=0.02', fc=c, ec='#444', lw=.8))
    ax.text(x + .48, y + .82, h, ha='center', va='center', fontweight='bold', fontsize=10); ax.text(x + .48, y + .38, t, ha='center', va='center', fontsize=8.5)
    if i % 4 < 3: ax.annotate('', xy=(x + 1.06, y + .5), xytext=(x + .92, y + .5), arrowprops=dict(arrowstyle='->', lw=1.2))
ax.annotate('', xy=(0.48, 1.07), xytext=(3.48, 1.28), arrowprops=dict(arrowstyle='->', lw=1.2, connectionstyle='arc3,rad=0.0'))
ax.text(2.0, -0.2, 'HF steps: fume hood, PP/PTFE ware, HF-rated gloves, calcium gluconate gel at hand', ha='center', fontsize=7.5, color='#b5421c')
flow = os.path.join(OUT, 'figures', 'C1_process_flow.png'); fig.savefig(flow, dpi=200, bbox_inches='tight'); plt.close(fig)
# photos (downscaled copies)
fs = sorted(glob.glob(os.path.join(IMG, '*.jpeg')))
PH = {}
for key, i in (('note', 25), ('weigh', 24), ('sonic', 11), ('chips', 16), ('raman', 23), ('dish', 1)):
    if i < len(fs):
        im = Image.open(fs[i]); im.thumbnail((1400, 1400)); p = os.path.join(OUT, 'figures', f'photo_{key}.jpg'); im.convert('RGB').save(p, quality=85); PH[key] = (p, os.path.basename(fs[i]))
def pair(a, b, name):
    fig, axs = plt.subplots(1, 2, figsize=(9, 4.6))
    for ax, k in zip(axs, (a, b)):
        ax.imshow(Image.open(PH[k][0])); ax.axis('off')
    for ax, l in zip(axs, 'ab'): ax.text(0.01, 0.99, l, transform=ax.transAxes, fontsize=12, fontweight='bold', va='top', color='white', bbox=dict(fc='black', ec='none', pad=2))
    p = os.path.join(OUT, 'figures', name); fig.savefig(p, dpi=170, bbox_inches='tight'); plt.close(fig); return p
ph1 = pair('note', 'weigh', 'C2_recipe_note_and_weighing.png'); ph2 = pair('sonic', 'chips', 'C3_cleaning_and_chips.png'); ph3 = pair('dish', 'raman', 'C4_chips_and_instrument.png')
# performance by recipe (from the measured R6G data)
def med(ses, sub, pw, it):
    v = R6[(R6.session == ses) & (R6['sub'] == sub) & (R6.power == pw) & (R6.it == it) & (R6.conc == '')].snr1509; return float(v.median()), len(v)
R2 = '20mMAg-8p6mlHF'
perf = [('S5', '20 mM AgNO3, 2 min', med('S5', R2 + '-2min', 5, 5)), ('S5', '20 mM AgNO3, 10 min', med('S5', R2 + '-10min', 5, 5)),
        ('S5', '20 mM AgNO3, 5 min', med('S5', R2 + '-5min', 5, 5)), ('S7', '20 mM AgNO3, 2 min (2nd chip)', med('S7', R2 + '-2min', 5, 5))]
perf3 = [(f'{m} min, {v} mL HF', med('S3', f'{m}min-{v}mlHF', 10, 5)) for m in (3, 4, 5, 6) for v in (5, 10)]
fig, (a0, a1) = plt.subplots(1, 2, figsize=(10, 3.4), gridspec_kw=dict(width_ratios=[1, 1.6]))
a0.bar(range(4), [x[2][0] for x in perf], color=['#7b3fa0', '#a57cc0', '#c9b3d9', '#7b3fa0'], edgecolor='k', lw=.5)
a0.set_xticks(range(4)); a0.set_xticklabels(['2 min', '10 min', '5 min', '2 min\n(2nd chip)'], fontsize=8); a0.set_ylabel('Median SNR, R6G 1509 cm$^{-1}$')
a0.set_title('20 mM AgNO3 recipe\n(power 5, 5 s, 3 acc)', loc='left', fontweight='bold', fontsize=9)
a1.bar(range(8), [x[1][0] for x in perf3], color='#b5421c', edgecolor='k', lw=.5); a1.set_xticks(range(8)); a1.set_xticklabels([x[0] for x in perf3], rotation=30, ha='right', fontsize=7.5)
a1.set_title('6 mg AgNO3 recipe, 5 or 10 mL HF\n(power 10, 5 s, 5 acc)', loc='left', fontweight='bold', fontsize=9)
for a in (a0, a1): a.axhline(10, color='#555', ls='--', lw=.8); a.spines[['top', 'right']].set_visible(False)
pf = os.path.join(OUT, 'figures', 'C5_R6G_signal_by_recipe.png'); fig.savefig(pf, dpi=200, bbox_inches='tight'); plt.close(fig)

d = FD.Doc('SERS Chip Fabrication: Silver-Etched Silicon', 'How the chips were made, what was varied, how they performed and what is still open')
d.h1('Purpose and sources')
d.p("This document describes how the SERS chips used in the measurements were made. It is based on the project documents in the mtp repository, the photographs and handwritten note taken in the lab, and the measured R6G data. "
    "Where a value was not recorded, it is marked Not recorded. Proposed recipes that were never made are kept apart from the recipes that were used.")
d.table(['Source (mtp repository)', 'Used for'],
        [['02_Plans_SOPs_and_Strategy/SOP_MACE_NAM_SERS_Bench_Protocol_Aug2026.docx', 'Cleaning, oxide strip, MACE bath preparation, safety, batch record'],
         ['Claude_Code_Handoff/Experiment_Roadmap.md', 'Recipe used in the August sessions, etch times, open items, proposed Sensor A and B'],
         ['CLAUDE.md (project context)', 'Wafer specification, piece size, known gaps'],
         ['05_Experimental_Data/SERS_and_R6G_sessions/img sensor/', 'Handwritten recipe note, weighing, ultrasonic cleaning, chip photos'],
         ['05_Experimental_Data/SERS_and_R6G_sessions/r6g-from-my-pc/', 'R6G validation of the eight June substrates'],
         ['02_Plans_SOPs_and_Strategy/LPS_Substrate_Strategy.docx, SERS_Substrate_Procurement.md', 'Alternative substrate routes (not built)'],
         ['Final_Submission/09_SERS_All_Sessions', 'Measured R6G performance of each chip type']],
        [9.2, 6.8], 'Documents used.')
d.h1('Principle')
d.p("The chips are made by metal-assisted chemical etching (MACE) in one step. A silicon piece is placed in a mixture of silver nitrate and hydrofluoric acid. "
    "Silver ions take electrons from the silicon and are deposited on it as silver nanoparticles. The silicon under each particle is oxidised, and HF dissolves the oxide, so the particles sink into the surface and leave pits. "
    "The surface turns dark and matte (black silicon). The silver particles and the narrow gaps between them are the SERS-active sites. The silicon underneath gives a sharp peak near 518-520 cm-1, which serves as an internal reference in every spectrum.")
d.p("Etch time and the AgNO3 and HF concentrations control the size and spacing of the silver particles and the depth of the etch. This is why they were the variables tested.")
d.h1('Materials')
d.table(['Item', 'Specification', 'Status'],
        [['Silicon wafer', 'n-type, (100), 1-10 ohm cm, single-side polished, prime grade, CZ', 'Confirmed by the user (18 Sep 2026)'],
         ['Chip size', 'Wafer broken into pieces, about 1 x 1 cm', 'From the note and photos'],
         ['Silver nitrate (AgNO3)', 'ACS reagent grade, solid', 'Lot Not recorded'],
         ['Hydrofluoric acid (HF)', 'Concentrated stock, assumed 48-49 %', 'Concentration not confirmed'],
         ['Solvents', 'Acetone, isopropanol, DI water', 'Grade Not recorded'],
         ['Labware', 'Polypropylene or PTFE beakers and tweezers (HF etches glass)', 'From the note ("plastic only")'],
         ['Drying', 'Nitrogen gas stream', 'From the note']],
        [3.4, 7.6, 5.0], 'Materials.')
d.h1('Process')
d.figure(flow, 'Process flow from wafer to measurement.')
d.h2('Cutting and cleaning')
for t in ('Break the wafer into pieces (the note says four pieces per wafer; the chips are about 1 x 1 cm).', 'Clean: acetone, then isopropanol, then DI water, 5 min in the ultrasonic bath each.',
          'Optional piranha clean (3:1 H2SO4 : 30 % H2O2) is described in the SOP. There is no record that it was used.'):
    d.b(t)
d.h2('Oxide strip')
d.p('Dip in about 10 % HF (4.1 mL of 49 % HF + 15.9 mL DI water) for 30-60 s. Rinse briefly in DI water, dry with N2 and go straight to the etch bath, before the native oxide regrows. The record does not show whether this step was used in every session.')
d.h2('MACE etch: the recipes actually used')
d.table(['Recipe', 'Bath', 'AgNO3', 'HF (if 49 % stock)', 'Etch time', 'Sessions'],
        [['A', '45 mL DI + 5 mL HF + 6 mg AgNO3', '0.71 mM', 'about 2.9 M', '3-6 min; Not recorded in S4, S8', 'S2, S3 (5 mL), S4, S8'],
         ['A-10', '45 mL DI + 10 mL HF + 6 mg AgNO3 (DI volume assumed as in A)', 'about 0.64 mM', 'about 5.3 M', '3-6 min', 'S3 (10 mL)'],
         ['B', '0.170 g AgNO3 + 8.6 mL HF, made up to 50 mL DI', '20.0 mM', 'about 5.0 M', '2, 5, 10 min (1 min label in S7)', 'S5, S7']],
        [1.3, 5.0, 1.9, 2.4, 3.2, 2.4], 'Etch-bath recipes used for the measured chips. Molarities are calculated; the HF value assumes a 49 % stock (28.9 M).')
for t in ('Dissolve the AgNO3 in the DI water first, in a plastic beaker, out of bright light. Then add the HF in the fume hood (acid into solution). Use the bath at once.',
          'Immerse the pieces at room temperature without stirring for the set time.',
          'Rinse in a full beaker of DI water (several changes), then dry under a gentle N2 stream.',
          'A good chip looks dark and matte compared with the shiny wafer. Note it in the batch record if it does not.'):
    d.b(t)
d.figure(ph1, f'a: handwritten recipe note (45 mL DI water, 5 mL HF, plastic beakers only, 6 mg AgNO3, etch, rinse beaker, N2 dry). b: weighing about 6 mg AgNO3 on the balance. Photos {PH["note"][1]} and {PH["weigh"][1]}.')
d.figure(ph2, f'a: ultrasonic bath used for cleaning. b: session S3 chips labelled 3m-6m with 5 or 10 mL HF. Photos {PH["sonic"][1]} and {PH["chips"][1]}.')
d.h2('Sample deposition and measurement')
for t in ('Drop-cast the analyte solution on the etched area and let it dry. Volumes and drying times were Not recorded for most sessions; 2-3 uL drops are planned in the roadmap.',
          'Measure with the 785 nm B&W Tek i-Raman Plus (BWS465-785H, BTC665N-785H-SYS probe), 400-1800 cm-1, on several spots per chip.',
          'Laser power is set as a software level (% of maximum). The power at the sample in mW was never measured.'):
    d.b(t)
d.figure(ph3, f'a: chips on holders in a Petri dish, with drops of analyte solution drying on the etched area. b: the Raman instrument. Photos {PH["dish"][1]} and {PH["raman"][1]}.')
d.h1('Quality checks for every chip')
for t in ('Silicon peak: present near 517-518 cm-1 in every spectrum (calibration offset of about -2 to -3 cm-1).', 'R6G test: the 1509 cm-1 band must reach SNR >= 10 before a biomarker is measured on chips from that batch.',
          'Blank: measure the chip without analyte, at the same settings, in the same session.', 'Batch record: actual reagent amounts, HF lot, etch time, appearance, time from etching to measurement.'):
    d.b(t)
d.h1('How the recipes performed')
d.figure(pf, 'Median SNR of the R6G 1509 cm-1 band for each chip type, from the measured data. Dashed line = gate (SNR 10). Panels use different settings and are not directly comparable.')
d.table(['Chip', 'Median SNR 1509', 'n'], [[x[1], f'{x[2][0]:.0f}', x[2][1]] for x in perf] + [[f'6 mg AgNO3, {x[0]}', f'{x[1][0]:.1f}', x[1][1]] for x in perf3],
        [7, 3.5, 1.5], 'R6G 1509 cm-1 band per chip type.')
b2, b10, b5 = perf[0][2][0], perf[1][2][0], perf[2][2][0]
d.p(f"Recipe B with a 2 min etch gave the strongest chip (median SNR {b2:.0f}). The 10 min etch was next ({b10:.0f}), and the 5 min etch was weakest ({b5:.0f}). "
    f"A second chip of the same 2 min recipe reached {perf[3][2][0]:.0f}. The difference between the two 2 min chips is larger than the difference between etch times, so chip-to-chip variation is a main open issue. "
    "Recipe A, with about 30 times less silver, gave a much weaker signal. Among the eight recipe A chips, the 6 min etch with 10 mL HF was clearly the best. This suggests that more silver deposition, through a longer etch or more HF, helps this recipe, but each condition was tested on one chip only.")
d.h1('Proposed recipes that were not made')
d.table(['Name', 'Idea', 'Steps (as planned)'],
        [['Sensor A, two-step MACE', 'Separate the silicon etch from the silver growth', '10 min etch with recipe B, strip Ag in dilute HNO3, re-deposit Ag in 5 mM AgNO3 + 1 mL HF / 50 mL for 30, 60 or 120 s'],
         ['Sensor B, HF/H2O2 MACE', 'Etch rate set by the oxidant', 'Seed Ag (5 mM AgNO3 + 1 mL HF / 50 mL, 60 s), then etch in about 4.8 M HF + 0.1 M H2O2 for 5, 15 or 30 min'],
         ['AgNO3 series', 'Particle density from silver concentration', '5, 10, 20, 40, 80 mM AgNO3 at a fixed 2 min etch'],
         ['Capture layers', 'Bring weakly binding analytes to the silver', 'Boronic acid (MPBA) for NAM; cysteamine for LTA; always against a bare-silver control'],
         ['Porous silicon', 'Higher surface area', 'Anodisation needs p-type or backside illumination for n-type; MACE-based porosity preferred near term']],
        [3.6, 4.4, 8.0], 'Proposed routes from the roadmap and strategy documents. None has been fabricated.')
d.h1('Safety')
for t in ('Concentrated HF causes deep, delayed burns and systemic toxicity. Work only in a fume hood, never alone, with HF-rated gloves over nitrile, a face shield and an apron.',
          'Keep 2.5 % calcium gluconate gel at the bench. After any contact, rinse with water, apply the gel and seek medical help.',
          'Use only PP or PTFE ware for HF. Collect HF and silver waste separately as hazardous waste; never pour it into the drain.'):
    d.b(t)
d.h1('Open items')
for t in ('HF stock concentration (assumed 49 %) and lot.', 'Exact etch time and bath for sessions S4 and S8.', 'Laser power at the sample in mW.',
          'SEM/EDS of the chips, so that particle size and coverage can be linked to the SERS signal.', 'Repeat chips per recipe, to measure batch reproducibility.',
          'Time between etching and measurement (silver tarnishes in air).'):
    d.b(t)
d.save(os.path.join(OUT, 'SERS_Chip_Fabrication_Process.docx')); print('saved')
