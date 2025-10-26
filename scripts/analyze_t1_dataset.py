#!/usr/bin/env python3

import csv
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

try:
    import yaml  # type: ignore
except Exception:
    yaml = None


@dataclass
class Item:
    construct: str
    code: str
    text: str


def read_codebook(path: str) -> List[Item]:
    with open(path, "r") as f:
        if yaml is not None:
            raw = yaml.safe_load(f)
        else:
            import json
            raw = json.load(f)
    return [Item(construct=d["construct"], code=d["code"], text=d["text"]) for d in raw]


def read_items_csv(path: str) -> Tuple[np.ndarray, List[str]]:
    with open(path, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        item_headers = header[1:]  # skip respondent_id
        rows: List[List[float]] = []
        for r in reader:
            rows.append([float(x) for x in r[1:]])
    X = np.array(rows, dtype=float)
    return X, item_headers


def compute_cronbach_alpha(X: np.ndarray) -> float:
    # X: N x k (items of one construct)
    if X.shape[1] < 2:
        return float("nan")
    k = X.shape[1]
    variances = X.var(axis=0, ddof=1)
    total_var = X.sum(axis=1).var(ddof=1)
    if total_var <= 1e-12:
        return float("nan")
    alpha = (k / (k - 1.0)) * (1.0 - variances.sum() / total_var)
    return float(alpha)


def correlation_matrix(X: np.ndarray) -> np.ndarray:
    # Standardize columns
    Xs = (X - X.mean(axis=0)) / X.std(axis=0, ddof=1)
    return (Xs.T @ Xs) / (Xs.shape[0] - 1)


def kmo_test(R: np.ndarray) -> Tuple[float, np.ndarray]:
    # Kaiser-Meyer-Olkin overall and per-variable MSA
    p = R.shape[0]
    invR = np.linalg.inv(R)
    A = np.diag(1.0 / np.sqrt(np.diag(invR)))
    P = -A @ invR @ A  # partial correlations with diag=-1
    np.fill_diagonal(P, 0.0)
    r2 = R.copy()
    np.fill_diagonal(r2, 0.0)
    r2 **= 2
    p2 = P ** 2
    kmo_num = r2.sum()
    kmo_den = r2.sum() + p2.sum()
    overall = float(kmo_num / kmo_den)
    msa = (r2.sum(axis=0)) / (r2.sum(axis=0) + p2.sum(axis=0))
    return overall, msa


def bartlett_sphericity(R: np.ndarray, n: int) -> Tuple[float, int]:
    # Returns chi-square statistic and degrees of freedom. p-value omitted to avoid SciPy.
    p = R.shape[0]
    sign, logdet = np.linalg.slogdet(R)
    if sign <= 0:
        # Not positive definite; adjust slightly
        eigvals, eigvecs = np.linalg.eigh(R)
        eigvals = np.clip(eigvals, 1e-6, None)
        R = (eigvecs * eigvals) @ eigvecs.T
        sign, logdet = np.linalg.slogdet(R)
    chi2 = -(n - 1 - (2 * p + 5) / 6) * logdet
    df = p * (p - 1) // 2
    return float(chi2), int(df)


def smc_communalities(R: np.ndarray) -> np.ndarray:
    invR = np.linalg.inv(R)
    smc = 1.0 - 1.0 / np.diag(invR)
    smc = np.clip(smc, 0.1, 0.95)
    return smc


def paf(R: np.ndarray, m: int, max_iter: int = 200, tol: float = 1e-4) -> np.ndarray:
    p = R.shape[0]
    h2 = smc_communalities(R)
    for _ in range(max_iter):
        Rstar = R.copy()
        np.fill_diagonal(Rstar, h2)
        w, V = np.linalg.eigh(Rstar)
        idx = np.argsort(w)[::-1][:m]
        L = V[:, idx] @ np.diag(np.sqrt(np.clip(w[idx], 0, None)))
        h2_new = (L ** 2).sum(axis=1)
        if np.max(np.abs(h2_new - h2)) < tol:
            h2 = h2_new
            break
        h2 = h2_new
    return L


def varimax(Phi: np.ndarray, gamma: float = 1.0, q: int = 50, tol: float = 1e-6) -> np.ndarray:
    p, k = Phi.shape
    R = np.eye(k)
    for _ in range(q):
        Lambda = Phi @ R
        u, s, vh = np.linalg.svd(Phi.T @ (Lambda ** 3 - (gamma / p) * Lambda @ np.diag((Lambda ** 2).sum(axis=0))))
        R_new = u @ vh
        if np.allclose(R, R_new, atol=tol):
            break
        R = R_new
    return Phi @ R


def parallel_analysis(X: np.ndarray, B: int = 50, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(random_state)
    n, p = X.shape
    R = correlation_matrix(X)
    obs_eigs = np.linalg.eigvalsh(R)[::-1]
    rand_eigs = np.zeros((B, p))
    for b in range(B):
        Z = rng.normal(size=(n, p))
        Z = (Z - Z.mean(axis=0)) / Z.std(axis=0, ddof=1)
        Rb = (Z.T @ Z) / (n - 1)
        rand_eigs[b] = np.linalg.eigvalsh(Rb)[::-1]
    perc95 = np.percentile(rand_eigs, 95, axis=0)
    return obs_eigs, perc95


def block_one_factor_cfa(R_block: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    # Fit a 1-factor model to a block correlation matrix via eigen-decomposition
    w, V = np.linalg.eigh(R_block)
    v1 = V[:, np.argsort(w)[-1]]
    lmbda = v1 * np.sqrt(max(w.max(), 0))
    theta = np.clip(1.0 - lmbda ** 2, 0.05, 0.85)
    return lmbda.reshape(-1, 1), np.diag(theta)


def cfa_simple(R: np.ndarray, blocks: List[List[int]]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    # Estimate blockwise 1-factor loadings, then factor correlations via least squares on cross-blocks
    p = R.shape[0]
    m = len(blocks)
    lambdas = []
    thetas = []
    for b in blocks:
        Lb, Tb = block_one_factor_cfa(R[np.ix_(b, b)])
        lambdas.append(Lb)
        thetas.append(Tb)
    # Assemble Lambda
    L = np.zeros((p, m))
    for j, b in enumerate(blocks):
        L[np.ix_(b, [j])] = lambdas[j]
    # Estimate Phi (factor correlation matrix)
    Phi = np.eye(m)
    for a in range(m):
        for b in range(a + 1, m):
            La = L[np.ix_(blocks[a], [a])]
            Lb = L[np.ix_(blocks[b], [b])]
            M = La @ Lb.T  # p_a x p_b
            Rab = R[np.ix_(blocks[a], blocks[b])]
            num = float((M.ravel() @ Rab.ravel()))
            den = float((M.ravel() @ M.ravel()) + 1e-12)
            phi_ab = num / den
            Phi[a, b] = Phi[b, a] = phi_ab
    # Unique variances
    Theta = np.zeros((p, p))
    offset = 0
    for j, b in enumerate(blocks):
        Theta[np.ix_(b, b)] = thetas[j]
    # Model-implied R
    R_model = L @ Phi @ L.T + Theta
    resid = R - R_model
    srmr = float(np.sqrt(np.mean((resid[np.triu_indices(p, k=1)]) ** 2)))
    return L, Phi, Theta, srmr


def save_reliability_reports(X: np.ndarray, items: List[Item], out_dir: str):
    # Group by construct
    by_c: Dict[str, List[int]] = {}
    for j, it in enumerate(items):
        by_c.setdefault(it.construct, []).append(j)
    rows = [("construct", "k_items", "alpha")]
    for c, idxs in by_c.items():
        alpha = compute_cronbach_alpha(X[:, idxs])
        rows.append((c, len(idxs), alpha))
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "reliability.csv"), "w", newline="") as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow(r)


def save_efa_reports(X: np.ndarray, items: List[Item], out_dir: str, n_factors: int = None):
    R = correlation_matrix(X)
    n = X.shape[0]
    kmo_overall, msa = kmo_test(R)
    chi2, df = bartlett_sphericity(R, n)
    obs_eigs, pa95 = parallel_analysis(X, B=50, random_state=123)
    if n_factors is None:
        n_factors = int(np.sum(obs_eigs > pa95))
        n_factors = max(1, n_factors)
    L_paf = paf(R, n_factors)
    L_rot = varimax(L_paf)
    # Save summaries
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "efa_summary.txt"), "w") as f:
        f.write(f"KMO overall: {kmo_overall:.3f}\n")
        f.write("MSA per item (order matches items CSV):\n")
        f.write(",".join([f"{x:.3f}" for x in msa.tolist()]) + "\n")
        f.write(f"Bartlett chi2: {chi2:.1f}, df={df}\n")
        f.write("Observed eigenvalues vs 95th percentile random:\n")
        for i, (o, r) in enumerate(zip(obs_eigs.tolist(), pa95.tolist()), start=1):
            f.write(f"  Factor {i}: observed={o:.3f}, PA95={r:.3f}\n")
        f.write(f"Selected factors: {n_factors}\n")
    # Loadings CSV
    with open(os.path.join(out_dir, "efa_loadings.csv"), "w", newline="") as f:
        w = csv.writer(f)
        header = ["item_code", "construct"] + [f"F{i+1}" for i in range(L_rot.shape[1])]
        w.writerow(header)
        for j, it in enumerate(items):
            w.writerow([it.code, it.construct] + [f"{x:.3f}" for x in L_rot[j, :].tolist()])


def save_cfa_reports(X: np.ndarray, items: List[Item], out_dir: str):
    # Build blocks by construct
    by_c: Dict[str, List[int]] = {}
    for j, it in enumerate(items):
        by_c.setdefault(it.construct, []).append(j)
    blocks = [by_c[c] for c in sorted(by_c.keys())]
    R = correlation_matrix(X)
    L, Phi, Theta, srmr = cfa_simple(R, blocks)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "cfa_summary.txt"), "w") as f:
        f.write(f"SRMR (overall): {srmr:.3f}\n")
        f.write("Factor correlations (Phi):\n")
        for i in range(Phi.shape[0]):
            row = ",".join([f"{Phi[i, j]:.3f}" for j in range(Phi.shape[1])])
            f.write(row + "\n")
    # Save blockwise SRMR too
    # Per-construct block fit
    with open(os.path.join(out_dir, "cfa_loadings.csv"), "w", newline="") as f:
        w = csv.writer(f)
        header = ["item_code", "construct", "loading"]
        w.writerow(header)
        # Map construct order to column in L
        construct_order = sorted(by_c.keys())
        for c_idx, c in enumerate(construct_order):
            for j in by_c[c]:
                w.writerow([items[j].code, items[j].construct, f"{L[j, c_idx]:.3f}"])


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Analyze T1 dataset: reliability, EFA, and simple CFA (numpy-only)")
    parser.add_argument("--data", default="/workspace/data/t1_items.csv", help="Path to item-level CSV")
    parser.add_argument("--codebook", default="/workspace/data/codebook.yaml", help="Path to codebook YAML/JSON")
    parser.add_argument("--out", default="/workspace/reports", help="Output directory for reports")
    args = parser.parse_args()

    items = read_codebook(args.codebook)
    X, headers = read_items_csv(args.data)

    # Ensure ordering matches the codebook; reorder columns if needed
    code_to_col = {h: i for i, h in enumerate(headers)}
    cols = [code_to_col[it.code] for it in items]
    X = X[:, cols]

    save_reliability_reports(X, items, args.out)
    save_efa_reports(X, items, args.out)
    save_cfa_reports(X, items, args.out)

    print("Analysis complete. Reports written to:", args.out)


if __name__ == "__main__":
    main()
