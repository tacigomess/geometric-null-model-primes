#!/usr/bin/env python3
"""
Compare density on sampled points (real embedding null)
-------------------------------------------------------
Computes prime density around randomly sampled points from the
real embedding, comparing:
- real primes vs null primes (same (x,y) geometry)
"""

import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from scipy.stats import ks_2samp

REAL_DATA = "./data/E1_base_log_espiral_1M.csv"
REAL_LABEL = "is_prime"
NULL_DATA = "./data/null_on_real_embedding.csv"

SAMPLE_SIZE = 50_000
RADIUS = 10.0
SEED = 42
np.random.seed(SEED)

df_real = pd.read_csv(REAL_DATA, engine="python")
df_null = pd.read_csv(NULL_DATA, engine="python")

# neutral sample points from the full space
sample_idx = np.random.choice(len(df_real), size=SAMPLE_SIZE, replace=False)
sample_points = df_real.loc[sample_idx, ["x", "y"]].values

# build event trees
coords_real = df_real[df_real[REAL_LABEL] == 1][["x", "y"]].values
coords_null = df_null[df_null["is_prime_null"] == 1][["x", "y"]].values

tree_real = KDTree(coords_real)
tree_null = KDTree(coords_null)

def density(points, tree, r):
    return np.array([len(tree.query_ball_point(pt, r=r)) for pt in points])

rho_real = density(sample_points, tree_real, RADIUS)
rho_null = density(sample_points, tree_null, RADIUS)

ks_stat, ks_p = ks_2samp(rho_real, rho_null)

print("==== Density on sampled points (same geometry) ====")
print(f"Mean density (real): {rho_real.mean():.3f}")
print(f"Mean density (null): {rho_null.mean():.3f}")
print("")
print("KS test:")
print(f"KS statistic = {ks_stat:.4f}")
print(f"p-value      = {ks_p:.2e}")
