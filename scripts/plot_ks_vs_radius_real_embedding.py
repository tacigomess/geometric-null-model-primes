#!/usr/bin/env python3
"""
Figura 4 — KS vs raio de vizinhança R
Usa os dados gerados por sweep_radius_density_real_embedding.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ===============================
# Configurações
# ===============================
INPUT_CSV = "data/radius_sweep_real_embedding.csv"

OUT_FIG = "./figures/fig_ks_vs_radius_real_embedding.png"
os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)

plt.rcParams.update({
    "figure.figsize": (6, 4),
    "axes.grid": True
})

# ===============================
# Carregar dados
# ===============================
df = pd.read_csv(INPUT_CSV)

required_cols = {"R", "KS_statistic"}
if not required_cols.issubset(df.columns):
    raise ValueError("CSV deve conter colunas: R, KS_statistic")

# ===============================
# Plot
# ===============================
plt.plot(
    df["R"],
    df["KS_statistic"],
    marker="o",
    linewidth=2
)

plt.xlabel("Raio de vizinhança R")
plt.ylabel("Estatística KS")
plt.title("KS em função da escala espacial")

plt.tight_layout()
plt.savefig(OUT_FIG, dpi=300)
plt.close()

print(f"✔ Figura salva em: {OUT_FIG}")
