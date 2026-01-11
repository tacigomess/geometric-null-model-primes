#!/usr/bin/env python3
"""
Plot CDF: real vs null (same geometry)
-------------------------------------
Generates the empirical CDF of local densities
around sampled points for real primes and
the calibrated null model.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

# -----------------------------
# CONFIG
# -----------------------------
REAL_DATA = "./data/E1_base_log_espiral_1M.csv"
REAL_LABEL = "is_prime"
NULL_DATA = "./data/null_on_real_embedding.csv"

SAMPLE_SIZE = 50_000
RADIUS = 10.0
SEED = 42
OUT_FIG = "./figures/fig_cdf_real_vs_null_R10.png"
os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)

np.random.seed(SEED)

# -----------------------------
# LOAD DATA
# -----------------------------
df_real = pd.read_csv(REAL_DATA)
df_null = pd.read_csv(NULL_DATA)

# Sample neutral points
idx = np.random.choice(len(df_real), size=SAMPLE_SIZE, replace=False)
sample_points = df_real.loc[idx, ["x", "y"]].values

# Event coordinates
coords_real = df_real[df_real[REAL_LABEL] == 1][["x", "y"]].values
coords_null = df_null[df_null["is_prime_null"] == 1][["x", "y"]].values

tree_real = KDTree(coords_real)
tree_null = KDTree(coords_null)

def density(points, tree, r):
    return np.array([
        len(tree.query_ball_point(pt, r=r))
        for pt in points
    ])

rho_real = density(sample_points, tree_real, RADIUS)
rho_null = density(sample_points, tree_null, RADIUS)

# -----------------------------
# CDF PLOT
# -----------------------------
def ecdf(x):
    xs = np.sort(x)
    ys = np.arange(1, len(xs) + 1) / len(xs)
    return xs, ys

x_r, y_r = ecdf(rho_real)
x_n, y_n = ecdf(rho_null)

plt.figure(figsize=(7, 5))
plt.plot(x_r, y_r, label="Real primes", linewidth=2)
plt.plot(x_n, y_n, label="Null (same geometry)", linestyle="--", linewidth=2)

plt.xlabel("Local density ρ")
plt.ylabel("CDF")
plt.title("CDF of local prime density (R = 10)")
plt.legend()
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(OUT_FIG, dpi=300)
plt.show()

print(f"✔ CDF figure saved to {OUT_FIG}")
