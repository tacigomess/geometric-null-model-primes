#!/usr/bin/env python3
"""
Null model on REAL embedding (recommended)
------------------------------------------
Uses the exact (x,y) positions from the real dataset and
samples pseudo-primes with Cramér-like probability, optionally
calibrated to match the total number of real primes.

Outputs:
- data/null_on_real_embedding.csv
"""

import math
import numpy as np
import pandas as pd

REAL_DATA = "./data/E1_base_log_espiral_1M.csv"
REAL_LABEL = "is_prime"
OUT_PATH = "./data/null_on_real_embedding.csv"

SEED = 42
CALIBRATE_TO_MATCH_COUNT = True  # match #events exactly
np.random.seed(SEED)

df = pd.read_csv(REAL_DATA)

# Ensure n exists
if "n" not in df.columns:
    raise ValueError("REAL_DATA must contain column 'n'.")

N = int(df["n"].max())

# Real prime count
pi_N = int(df[df[REAL_LABEL] == 1].shape[0])

# Base weights w(n)=1/log(n)
w = 1.0 / np.log(df["n"].values)

if CALIBRATE_TO_MATCH_COUNT:
    # Choose c so that sum(c*w) = pi(N)  =>  c = pi/sum(w)
    c = pi_N / w.sum()
else:
    c = 1.0

p = np.clip(c * w, 0.0, 1.0)
is_null = (np.random.rand(len(df)) < p).astype(int)

df_out = df[["n", "x", "y"]].copy()
# keep geometry columns if you have them
for col in ["r", "theta", "z"]:
    if col in df.columns:
        df_out[col] = df[col]

df_out["is_prime_null"] = is_null
df_out.to_csv(OUT_PATH, index=False)

print(f"✔ Null model saved to {OUT_PATH}")
print(f"Real primes: {pi_N} | Null events: {int(is_null.sum())} | c={c:.6g}")
