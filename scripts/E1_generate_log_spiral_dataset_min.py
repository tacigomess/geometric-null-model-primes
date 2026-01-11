
#!/usr/bin/env python3
# E1_generate_log_spiral_dataset_min.py
# Gera a base em espiral logarítmica com halos (p95) e marcação de primos especiais.
# Dependências: numpy, pandas, scipy (KDTree)
import argparse, os, math
import numpy as np, pandas as pd
from scipy.spatial import KDTree

def is_prime(n:int) -> bool:
    if n < 2: return False
    if n % 2 == 0: return n == 2
    r = int(math.isqrt(n))
    f = 3
    while f <= r:
        if n % f == 0: return False
        f += 2
    return True

def mark_specials(df: pd.DataFrame) -> pd.DataFrame:
    primes = df.loc[df["is_prime"]==1, "n"].to_numpy()
    P = set(map(int, primes.tolist()))
    def twin(p):   return (p in P) and ((p-2 in P) or (p+2 in P))
    def sexy(p):   return (p in P) and ((p-6 in P) or (p+6 in P))
    def cousin(p): return (p in P) and ((p-4 in P) or (p+4 in P))
    def sophie(p): return (p in P) and (2*p + 1 in P)
    df["is_twin_prime"]      = df["n"].apply(lambda p: twin(int(p)))
    df["is_sexy_prime"]      = df["n"].apply(lambda p: sexy(int(p)))
    df["is_cousin_prime"]    = df["n"].apply(lambda p: cousin(int(p)))
    df["is_sophie_germain"]  = df["n"].apply(lambda p: sophie(int(p)))
    return df

def compute_density(df: pd.DataFrame, mode:str, z_factor:float, fixed_R:float) -> np.ndarray:
    # KDTree apenas com PRIMOS (densidade "entre primos")
    prime_xy = df.loc[df["is_prime"]==1, ["x","y"]].to_numpy()
    tree = KDTree(prime_xy) if len(prime_xy) > 0 else None
    rho = np.zeros(len(df), dtype=int)
    for i, row in enumerate(df.itertuples(index=False)):
        if tree is None:
            rho[i] = 0
            continue
        R = (math.sqrt(row.n) * z_factor) if mode == "adaptive" else fixed_R
        cnt = len(tree.query_ball_point([row.x, row.y], r=R))
        rho[i] = cnt
    return rho

def add_blocks(df: pd.DataFrame, block_size:int) -> pd.DataFrame:
    if block_size <= 0:
        df["block_id"] = -1
        return df
    start = int(df["n"].min())
    df["block_id"] = (df["n"].astype(int) - start) // block_size
    return df

def add_halos(df: pd.DataFrame, percentile:int=95, by_block:bool=False) -> pd.DataFrame:
    col = f"halo_p{percentile}_{'block' if by_block else 'global'}"
    df[col] = False
    if by_block:
        for bid, g in df.groupby("block_id"):
            prim = g.loc[g["is_prime"]==1, "z_refinado"]
            if len(prim) == 0:
                continue
            thr = np.percentile(prim, percentile)
            idx = (df["block_id"]==bid) & (df["is_prime"]==1) & (df["z_refinado"]>=thr)
            df.loc[idx, col] = True
    else:
        prim = df.loc[df["is_prime"]==1, "z_refinado"]
        if len(prim) > 0:
            thr = np.percentile(prim, percentile)
            idx = (df["is_prime"]==1) & (df["z_refinado"]>=thr)
            df.loc[idx, col] = True
    return df

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=200_000)
    ap.add_argument("--b", type=float, default=0.1, help="theta = b*n")
    ap.add_argument("--radius_mode", choices=["adaptive","fixed"], default="adaptive")
    ap.add_argument("--z_factor", type=float, default=0.1, help="R = sqrt(n)*z_factor (se adaptive)")
    ap.add_argument("--fixed_R", type=float, default=10.0, help="R fixo (se fixed)")
    ap.add_argument("--block_size", type=int, default=50_000)
    ap.add_argument("--percentile", type=int, default=95)
    ap.add_argument("--out_csv", type=str, default="data/E1_base_log_espiral.csv")
    args = ap.parse_args()

    n = np.arange(2, args.N+1, dtype=np.int64)
    theta = args.b * n.astype(float)
    r = np.log(n.astype(float))
    x = r * np.cos(theta)
    y = r * np.sin(theta)

    is_p = np.fromiter((1 if is_prime(int(k)) else 0 for k in n), count=len(n), dtype=np.int8)

    df = pd.DataFrame({"n": n, "x": x, "y": y, "r": r, "theta": theta, "is_prime": is_p})
    df["is_composite"] = (df["is_prime"] == 0)

    rho = compute_density(df, args.radius_mode, args.z_factor, args.fixed_R)
    df["prime_rho"] = rho
    df["z_refinado"] = df["prime_rho"] * np.log(df["n"].astype(float))

    df = add_blocks(df, args.block_size)
    df = mark_specials(df)
    df = add_halos(df, percentile=args.percentile, by_block=False)
    if args.block_size > 0:
        df = add_halos(df, percentile=args.percentile, by_block=True)

    os.makedirs(os.path.dirname(args.out_csv) or ".", exist_ok=True)
    df.to_csv(args.out_csv, index=False)
    print(f"✅ salvo: {args.out_csv}")
    print("Colunas:", ",".join(df.columns))

if __name__ == "__main__":
    main()
