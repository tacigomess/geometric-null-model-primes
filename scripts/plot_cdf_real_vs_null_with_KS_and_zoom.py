#!/usr/bin/env python3
"""
CDF with KS marker and zoom inset (paper-ready)
-----------------------------------------------
Plots:
- empirical CDFs (real vs null)
- vertical segment marking the KS statistic
- zoomed inset around the KS region
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from scipy.stats import ks_2samp
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# -----------------------------
# CONFIG
# -----------------------------
REAL_DATA = "./data/E1_base_log_espiral_1M.csv"
REAL_LABEL = "is_prime"
NULL_DATA = "./data/null_on_real_embedding.csv"

SAMPLE_SIZE = 50_000
RADIUS = 10.0
SEED = 42
OUT_FIG = "./figures/fig_cdf_real_vs_null_R10_KS_zoom.png"
os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)

np.random.seed(SEED)

# -----------------------------
# LOAD DATA
# -----------------------------
df_real = pd.read_csv(REAL_DATA)
df_null = pd.read_csv(NULL_DATA)

idx = np.random.choice(len(df_real), size=SAMPLE_SIZE, replace=False)
sample_points = df_real.loc[idx, ["x", "y"]].values

coords_real = df_real[df_real[REAL_LABEL] == 1][["x", "y"]].values
coords_null = df_null[df_null["is_prime_null"] == 1][["x", "y"]].values

tree_real = KDTree(coords_real)
tree_null = KDTree(coords_null)

def density(points, tree, r):
    return np.array([len(tree.query_ball_point(pt, r=r)) for pt in points])

rho_real = density(sample_points, tree_real, RADIUS)
rho_null = density(sample_points, tree_null, RADIUS)

# -----------------------------
# ECDF
# -----------------------------
def ecdf(x):
    xs = np.sort(x)
    ys = np.arange(1, len(xs) + 1) / len(xs)
    return xs, ys

x_r, y_r = ecdf(rho_real)
x_n, y_n = ecdf(rho_null)

# -----------------------------
# KS LOCATION
# -----------------------------
cdf_r_interp = np.interp(x_r, x_n, y_n)
diff = np.abs(y_r - cdf_r_interp)
ks_idx = np.argmax(diff)

x_ks = x_r[ks_idx]
y_r_ks = y_r[ks_idx]
y_n_ks = cdf_r_interp[ks_idx]
ks_value = diff[ks_idx]

# -----------------------------
# MAIN PLOT
# -----------------------------
fig, ax = plt.subplots(figsize=(7.5, 5.5))

ax.plot(x_r, y_r, label="Real primes", linewidth=2)
ax.plot(x_n, y_n, "--", label="Null (same geometry)", linewidth=2)

# KS marker
ax.vlines(x_ks, y_r_ks, y_n_ks, colors="black", linewidth=2)
ax.scatter([x_ks], [y_r_ks], color="black", zorder=5)
ax.scatter([x_ks], [y_n_ks], color="black", zorder=5)

ax.text(
    x_ks * 1.002,
    (y_r_ks + y_n_ks) / 2,
    f"KS = {ks_value:.3f}",
    va="center",
    fontsize=10
)

ax.set_xlabel("Local density ρ")
ax.set_ylabel("CDF")
ax.set_title("CDF of local prime density (R = 10)")
ax.legend()
ax.grid(alpha=0.3)

# -----------------------------
# ZOOM INSET
# -----------------------------
axins = inset_axes(ax, width="40%", height="40%", loc="lower right")

axins.plot(x_r, y_r, linewidth=2)
axins.plot(x_n, y_n, "--", linewidth=2)

axins.vlines(x_ks, y_r_ks, y_n_ks, colors="black", linewidth=2)

x_margin = 500
y_margin = 0.08

axins.set_xlim(x_ks - x_margin, x_ks + x_margin)
axins.set_ylim(
    min(y_r_ks, y_n_ks) - y_margin,
    max(y_r_ks, y_n_ks) + y_margin
)

axins.set_xticks([])
axins.set_yticks([])
axins.grid(alpha=0.2)

# -----------------------------
# SAVE
# -----------------------------
plt.tight_layout()
plt.savefig(OUT_FIG, dpi=300)
plt.show()

print(f"✔ Figure with KS and zoom saved to {OUT_FIG}")
