import csv, sys
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
name = sys.argv[1] if len(sys.argv) > 1 else "lipidA"
SCALE, FWHM, LASER_NM, T = 0.965, 12.0, 785.0, 298.15
rows = list(csv.reader(open(f"{name}_raman_act.csv")))[1:]
nu = np.array([float(r[0]) for r in rows]); S = np.array([float(r[1]) for r in rows])
nu_s = nu * SCALE
nu0 = 1e7 / LASER_NM
hc_k = 1.4388                                   # cm K
I = S * (nu0 - nu_s) ** 4 / (nu_s * (1 - np.exp(-hc_k * nu_s / T)))
x = np.linspace(200, 3300, 6200)
g = FWHM / 2
y = sum(i * g**2 / ((x - c) ** 2 + g**2) for i, c in zip(I, nu_s))
y /= y.max()
np.savetxt(f"{name}_spectrum_785nm.csv", np.c_[x, y], delimiter=",", header="wavenumber_cm-1,norm_intensity", comments="")
fig, ax = plt.subplots(2, 1, figsize=(10, 7))
ax[0].plot(x, y, "k", lw=1); ax[0].set_title(f"{name}: LTA model, B3LYP/3-21G quick reference, scaled {SCALE}, {LASER_NM:.0f} nm, FWHM {FWHM:.0f}")
m = (x >= 600) & (x <= 1800)
ax[1].plot(x[m], y[m] / y[m].max(), "k", lw=1); ax[1].set_title("Fingerprint region")
for a in ax:
    a.set_xlabel("Raman shift (cm$^{-1}$)"); a.set_ylabel("Norm. intensity")
for p in (850, 989, 1131, 1330):
    ax[1].axvline(p, color="r", ls=":", lw=0.8); ax[1].text(p, 1.02, str(p), color="r", fontsize=8, ha="center")
plt.tight_layout(); plt.savefig(f"{name}_spectrum_785nm.png", dpi=150)
# peak list in the fingerprint region
from scipy.signal import find_peaks
pk, _ = find_peaks(y[m] / y[m].max(), height=0.08, distance=15)
print("fingerprint peaks (cm-1, rel):", [(int(round(x[m][k])), round(float((y[m] / y[m].max())[k]), 2)) for k in pk])
