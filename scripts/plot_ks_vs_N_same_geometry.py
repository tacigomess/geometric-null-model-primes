#!/usr/bin/env python3
"""
Plot KS vs N (same-geometry null)
---------------------------------
Reads results/ks_vs_N_same_geometry.csv and saves a figure.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

INCSV = "./results/ks_vs_N_same_geometry.csv"
OUTFIG = "./figures/fig_ks_vs_N_same_geometry.png"

os.makedirs(os.path.dirname(OUTFIG), exist_ok=True)

df = pd.read_csv(INCSV)

plt.figure(figsize=(8, 5))
plt.plot(df["N"], df["KS"], marker="o", linewidth=2)

plt.xlabel("N (cutoff)")
plt.ylabel("KS statistic")
plt.title("KS divergence vs N (same-geometry Cramér null)")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(OUTFIG, dpi=300)
plt.show()

print("Saved figure:", OUTFIG)
