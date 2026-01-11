#!/usr/bin/env python3
"""
Sweep KS vs N (same-geometry null)
----------------------------------
For each cutoff N, this script:
1) Loads the base embedding up to N (first N rows of the E1 dataset).
2) Generates a same-geometry Cramér null model on those points.
3) Samples M centers from the full embedding.
4) Computes local densities rho_R(x) for real and null events using KDTree radius counts.
5) Computes KS statistic and p-value for rho distributions.
6) Saves results to results/ks_vs_N_same_geometry.csv

Assumptions:
- E1_base_log_espiral_1M.csv contains columns: x, y, is_prime
- Rows are ordered by n (so taking first k rows corresponds to n up to N)
"""

import math
import os
import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from scipy.stats import ks_2samp

# ------------------------
# CONFIG
# ------------------------
BASE_DATA = "./data/E1_base_log_espiral_1M.csv"
REAL_LABEL = "is_prime"

# Choose N values (must be <= dataset size)
N_VALUES = [200_000, 400_000, 600_000, 800_000, 1_000_000]

# Density parameters
RADIUS = 10.0
SAMPLE_SIZE = 50_000
SEED = 42

# Output
OUTCSV = "./results/ks_vs_N_same_geometry.csv"
os.makedirs(os.path.dirname(OUTCSV), exist_ok=True)

# ------------------------
# HELPERS
# ------------------------
def ensure_dirs():
    os.makedirs(os.path.dirname(OUTCSV), exist_ok=True)

def make_null_same_geometry(df_real: pd.DataFrame, seed: int) -> pd.DataFrame:
    """
    Same-geometry Cramér-type null:
    X_n ~ Bernoulli(p(n)), p(n)=c/log(n), with c calibrated to match total prime count.
    We assume df_real rows correspond to n increasing from 2 upward.
    """
    rng = np.random.default_rng(seed)

    # infer n from row index if n column absent
    if "n" in df_real.columns:
        n_vals = df_real["n"].to_numpy()
    else:
        # if dataset starts at n=2 and is ordered, approximate:
        # row 0 -> n=2
        n_vals = np.arange(2, 2 + len(df_real), dtype=np.int64)

    # real prime count
    real_prime_count = int(df_real[REAL_LABEL].sum())

    # avoid log(0) etc
    logn = np.log(n_vals.astype(float))
    logn[logn == 0] = 1.0

    # p(n) = c/log(n). Choose c so that sum p(n) ≈ real_prime_count
    # c = real_prime_count / sum(1/log(n))
    denom = np.sum(1.0 / logn)
    c = real_prime_count / denom

    p = c / logn
    p = np.clip(p, 0.0, 1.0)

    is_null = (rng.random(len(df_real)) < p).astype(int)

    df_null = df_real[["x", "y"]].copy()
    df_null["is_prime_null"] = is_null
    return df_null, c, real_prime_count, int(is_null.sum())

def density(points: np.ndarray, tree: KDTree, r: float) -> np.ndarray:
    # KDTree query_ball_point is stable; list comprehension is okay for 50k
    return np.array([len(tree.query_ball_point(pt, r=r)) for pt in points], dtype=np.int64)

# ------------------------
# MAIN
# ------------------------
def main():
    ensure_dirs()

    np.random.seed(SEED)

    # Load once, then slice
    df_base = pd.read_csv(BASE_DATA, engine="python")

    rows_total = len(df_base)
    results = []

    for N in N_VALUES:
        if N > rows_total:
            print(f"[skip] N={N} exceeds dataset rows={rows_total}")
            continue

        df_real = df_base[df_base["n"] <= N].copy()

        # Generate null on same geometry for this N
        df_null, c, n_real, n_null = make_null_same_geometry(df_real, seed=SEED)

        # Sample centers from full embedding (real geometry)
        sample_idx = np.random.choice(len(df_real), size=min(SAMPLE_SIZE, len(df_real)), replace=False)
        sample_points = df_real.loc[sample_idx, ["x", "y"]].to_numpy()

        # Build event trees
        coords_real = df_real[df_real[REAL_LABEL] == 1][["x", "y"]].to_numpy()
        coords_null = df_null[df_null["is_prime_null"] == 1][["x", "y"]].to_numpy()

        tree_real = KDTree(coords_real)
        tree_null = KDTree(coords_null)

        rho_real = density(sample_points, tree_real, RADIUS)
        rho_null = density(sample_points, tree_null, RADIUS)

        ks_stat, ks_p = ks_2samp(rho_real, rho_null)

        mean_real = float(rho_real.mean())
        mean_null = float(rho_null.mean())

        print(
            f"N={N:>8d}: mean(real)={mean_real:>10.2f} | mean(null)={mean_null:>10.2f} "
            f"| KS={ks_stat:.4f} | p={ks_p:.2e} | primes={n_real} | null={n_null} | c={c:.6f}"
        )

        results.append({
            "N": N,
            "R": RADIUS,
            "sample_size": int(len(sample_points)),
            "mean_rho_real": mean_real,
            "mean_rho_null": mean_null,
            "KS": float(ks_stat),
            "p_value": float(ks_p),
            "n_real_primes": int(n_real),
            "n_null_events": int(n_null),
            "c": float(c),
            "seed": SEED,
        })

    out = pd.DataFrame(results)
    out.to_csv(OUTCSV, index=False)
    print("\nSaved:", OUTCSV)

if __name__ == "__main__":
    main()
