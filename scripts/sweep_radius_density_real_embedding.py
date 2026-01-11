#!/usr/bin/env python3
"""
Sweep neighborhood radius R (same geometry null)
------------------------------------------------
Compares local prime densities around neutral sampled points
for multiple radii, using:
- real primes
- null primes sampled on the SAME geometric embedding
"""

import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from scipy.stats import ks_2samp

# -----------------------------
# CONFIGURATION
# -----------------------------
REAL_DATA = "./data/E1_base_log_espiral_1M.csv"
REAL_LABEL = "is_prime"
NULL_DATA = "./data/null_on_real_embedding.csv"

RADII = [2.0, 5.0, 10.0, 20.0]
SAMPLE_SIZE = 50_000
SEED = 42

np.random.seed(SEED)

# -----------------------------
# LOAD DATA
# -----------------------------
df_real = pd.read_csv(REAL_DATA)
df_null = pd.read_csv(NULL_DATA)

# Sample neutral points ONCE from the full embedding
sample_idx = np.random.choice(len(df_real), size=SAMPLE_SIZE, replace=False)
sample_points = df_real.loc[sample_idx, ["x", "y"]].values

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

# -----------------------------
# SWEEP OVER RADII
# -----------------------------
results = []

for R in RADII:
    rho_real = density(sample_points, tree_real, R)
    rho_null = density(sample_points, tree_null, R)

    ks_stat, ks_p = ks_2samp(rho_real, rho_null)

    results.append({
        "R": R,
        "mean_rho_real": rho_real.mean(),
        "mean_rho_null": rho_null.mean(),
        "KS_statistic": ks_stat,
        "p_value": ks_p
    })

    print(
        f"R={R:>5}: "
        f"mean(real)={rho_real.mean():.2f} | "
        f"mean(null)={rho_null.mean():.2f} | "
        f"KS={ks_stat:.4f} | p={ks_p:.2e}"
    )

# -----------------------------
# SAVE RESULTS
# -----------------------------
df_out = pd.DataFrame(results)
df_out.to_csv("./data/radius_sweep_real_embedding.csv", index=False)

print("\n✔ Radius sweep (same geometry null) saved to:")
print("  ./data/radius_sweep_real_embedding.csv")
