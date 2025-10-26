#!/usr/bin/env python3
import argparse
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler

# EFA
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity

# CFA / SEM
from semopy import Model
from semopy import calc_stats


@dataclass
class ConstructSpec:
    name: str
    items: List[str]


def set_seed(seed: int):
    np.random.seed(seed)


def likert_discretize(x: np.ndarray, num_categories: int = 7) -> np.ndarray:
    """Discretize a continuous vector to Likert categories 1..num_categories using quantile bins."""
    # Robustly handle constant arrays
    x = np.asarray(x).reshape(-1)
    if np.std(x) < 1e-8:
        return np.ones_like(x, dtype=int) * ((num_categories + 1) // 2)
    # Convert to ranks -> uniform -> bins
    u = stats.rankdata(x, method="average") / (len(x) + 1)
    bins = np.linspace(0.0, 1.0, num_categories + 1)[1:-1]
    cats = np.digitize(u, bins) + 1
    return cats.astype(int)


def simulate_latents(n: int, seed: int) -> pd.DataFrame:
    """Simulate exogenous latent constructs with a plausible correlation structure."""
    set_seed(seed)
    # Latents: ATT, SN, PBC, SEV, VUL, SEFF, REFF, PB
    latent_names = [
        "ATT_lat", "SN_lat", "PBC_lat", "SEV_lat", "VUL_lat", "SEFF_lat", "REFF_lat", "PB_lat"
    ]
    # Reasonable correlation matrix (positive relationships among adaptive constructs, moderate threat correlations)
    # Values chosen to yield stable EFA/CFA and realistic interrelations
    R = np.array([
        [1.00, 0.35, 0.45, 0.15, 0.20, 0.40, 0.35, 0.30],  # ATT
        [0.35, 1.00, 0.30, 0.10, 0.15, 0.25, 0.20, 0.25],  # SN
        [0.45, 0.30, 1.00, 0.10, 0.15, 0.50, 0.35, 0.40],  # PBC
        [0.15, 0.10, 0.10, 1.00, 0.40, 0.10, 0.10, 0.05],  # SEV
        [0.20, 0.15, 0.15, 0.40, 1.00, 0.15, 0.10, 0.10],  # VUL
        [0.40, 0.25, 0.50, 0.10, 0.15, 1.00, 0.45, 0.40],  # SEFF
        [0.35, 0.20, 0.35, 0.10, 0.10, 0.45, 1.00, 0.35],  # REFF
        [0.30, 0.25, 0.40, 0.05, 0.10, 0.40, 0.35, 1.00],  # PB
    ])
    # Ensure positive definiteness (jitter if needed)
    eigvals = np.linalg.eigvalsh(R)
    if np.min(eigvals) < 1e-6:
        R += np.eye(R.shape[0]) * (1e-6 - np.min(eigvals) + 1e-6)

    L = np.linalg.cholesky(R)
    Z = np.random.normal(size=(n, R.shape[0]))
    X = Z @ L.T
    df = pd.DataFrame(X, columns=latent_names)
    return df


def generate_measurement(latent: np.ndarray, loadings: List[float]) -> np.ndarray:
    """Generate continuous item indicators given a latent vector and standardized loadings."""
    latent = np.asarray(latent).reshape(-1)
    items = []
    for lam in loadings:
        e = np.random.normal(size=len(latent))
        # Standardized: var(item) = lam^2 + (1 - lam^2) = 1
        item = lam * latent + np.sqrt(max(1e-6, 1.0 - lam ** 2)) * e
        items.append(item)
    return np.column_stack(items)


def cronbach_alpha(X: np.ndarray) -> float:
    """Compute Cronbach's alpha for items in columns."""
    X = np.asarray(X)
    k = X.shape[1]
    if k < 2:
        return np.nan
    item_vars = X.var(axis=0, ddof=1)
    total_var = X.sum(axis=1).var(ddof=1)
    if total_var <= 0:
        return np.nan
    alpha = (k / (k - 1.0)) * (1.0 - item_vars.sum() / total_var)
    return float(alpha)


def build_dataset(n: int, seed: int) -> Tuple[pd.DataFrame, Dict[str, ConstructSpec], pd.DataFrame]:
    """Generate the full dataset (items only; Likert-scaled) and return it along with specs and continuous copy."""
    latents = simulate_latents(n, seed)

    # Define constructs and loadings (high but realistic)
    specs = {
        "ATT": ConstructSpec("ATT", ["ATT1", "ATT2", "ATT3"]),
        "SN": ConstructSpec("SN", ["SN1", "SN2"]),
        "PBC": ConstructSpec("PBC", ["PBC1", "PBC2", "PBC3"]),
        "SEV": ConstructSpec("SEV", ["SEV1", "SEV2", "SEV3"]),
        "VUL": ConstructSpec("VUL", ["VUL1", "VUL2", "VUL3"]),
        "SEFF": ConstructSpec("SEFF", ["SEFF1", "SEFF2", "SEFF3"]),
        "REFF": ConstructSpec("REFF", ["REFF1", "REFF2", "REFF3"]),
        "PB": ConstructSpec("PB", ["PB1", "PB2", "PB3"]),
        "INT": ConstructSpec("INT", ["INT1", "INT2"]),
    }

    loadings_map = {
        "ATT": [0.85, 0.82, 0.80],
        "SN": [0.86, 0.82],
        "PBC": [0.80, 0.78, 0.75],
        "SEV": [0.78, 0.75, 0.72],
        "VUL": [0.80, 0.77, 0.74],
        "SEFF": [0.84, 0.82, 0.80],
        "REFF": [0.82, 0.80, 0.78],
        "PB": [0.86, 0.83, 0.80],
        "INT": [0.88, 0.85],
    }

    # Structural influence for INT latent
    b_ATT = 0.35
    b_SN = 0.20
    b_PBC = 0.30
    b_SEFF = 0.25
    b_REFF = 0.20
    b_SEV = 0.12
    b_VUL = 0.10
    b_PB = 0.25
    resid_int_sd = np.sqrt(max(1e-6, 1.0 - (b_ATT**2 + b_SN**2 + b_PBC**2 + b_SEFF**2 + b_REFF**2 + b_SEV**2 + b_VUL**2 + b_PB**2) * 0.5))

    # Generate continuous measurement for each construct
    continuous_items: Dict[str, np.ndarray] = {}

    # Exogenous constructs first
    for c in ["ATT", "SN", "PBC", "SEV", "VUL", "SEFF", "REFF", "PB"]:
        continuous_items[c] = generate_measurement(latents[f"{c}_lat"].values, loadings_map[c])

    # INT latent depends on others
    int_lat = (
        b_ATT * latents["ATT_lat"].values
        + b_SN * latents["SN_lat"].values
        + b_PBC * latents["PBC_lat"].values
        + b_SEFF * latents["SEFF_lat"].values
        + b_REFF * latents["REFF_lat"].values
        + b_SEV * latents["SEV_lat"].values
        + b_VUL * latents["VUL_lat"].values
        + b_PB * latents["PB_lat"].values
        + np.random.normal(scale=resid_int_sd, size=n)
    )
    continuous_items["INT"] = generate_measurement(int_lat, loadings_map["INT"])

    # Build DataFrames
    cont_df_parts = []
    likert_df_parts = []
    for c, spec in specs.items():
        arr = continuous_items[c]
        cont_df_parts.append(pd.DataFrame(arr, columns=spec.items))
        # Discretize per-item independently to maintain variability
        likert_cols = {}
        for j, col in enumerate(spec.items):
            likert_cols[col] = likert_discretize(arr[:, j], num_categories=7)
        likert_df_parts.append(pd.DataFrame(likert_cols))

    cont_df = pd.concat(cont_df_parts, axis=1)
    likert_df = pd.concat(likert_df_parts, axis=1)

    # Add respondent id
    likert_df.insert(0, "respondent_id", np.arange(1, n + 1))
    cont_df.insert(0, "respondent_id", np.arange(1, n + 1))

    return likert_df, specs, cont_df


def create_codebook(specs: Dict[str, ConstructSpec]) -> pd.DataFrame:
    """Create a codebook with item texts and sources."""
    entries = []
    # Item texts (adapted from TPB/PMT validated wordings; anchors 1=Strongly Disagree, 7=Strongly Agree)
    item_texts = {
        # Attitude (semantic differential adapted to agreement statement for data coding)
        "ATT1": "Following bank security steps is beneficial for me.",
        "ATT2": "Following bank security steps is wise.",
        "ATT3": "Following bank security steps is important.",
        # Subjective Norm
        "SN1": "Most people important to me think I should follow bank security steps.",
        "SN2": "My family expects me to be diligent with bank security.",
        # Perceived Behavioral Control
        "PBC1": "For me, following all recommended security steps would be easy.",
        "PBC2": "I have the resources, time, and knowledge to follow the steps.",
        "PBC3": "Whether I follow the steps is entirely up to me.",
        # Intention
        "INT1": "I intend to follow all recommended security steps in the next 3 months.",
        "INT2": "I plan to make an effort to be more diligent with security steps.",
        # Threat Appraisal: Severity
        "SEV1": "The financial loss from bank fraud would be severe for me.",
        "SEV2": "Bank fraud would have serious negative consequences for me.",
        "SEV3": "Experiencing bank fraud would be highly damaging to me.",
        # Threat Appraisal: Vulnerability
        "VUL1": "I am at high risk of experiencing bank fraud.",
        "VUL2": "I feel vulnerable to bank fraud.",
        "VUL3": "It is likely that I could be a victim of bank fraud.",
        # Coping Appraisal: Self-Efficacy
        "SEFF1": "I am confident I can perform the security steps correctly.",
        "SEFF2": "I can follow the security steps even if they are time-consuming.",
        "SEFF3": "I can follow security steps even without help from others.",
        # Coping Appraisal: Response Efficacy
        "REFF1": "The recommended security steps are effective at protecting me.",
        "REFF2": "Following the security steps will reduce my risk of bank fraud.",
        "REFF3": "Using the security steps significantly lowers the chance of fraud.",
        # Past Behavior (habit)
        "PB1": "In the past 3 months, I followed recommended security steps frequently.",
        "PB2": "In the past 3 months, I was consistent in following security steps.",
        "PB3": "In the past 3 months, I made security steps part of my routine.",
    }

    sources = {
        "ATT": "Ajzen (1991) Theory of Planned Behavior",
        "SN": "Ajzen (1991) Theory of Planned Behavior",
        "PBC": "Ajzen (1991) Theory of Planned Behavior",
        "INT": "Ajzen (1991) Theory of Planned Behavior",
        "SEV": "Rogers (1983) Protection Motivation Theory; Maddux & Rogers (1983)",
        "VUL": "Rogers (1983) Protection Motivation Theory; Maddux & Rogers (1983)",
        "SEFF": "Bandura (1977, 1997); Maddux & Rogers (1983)",
        "REFF": "Rogers (1983) Protection Motivation Theory; Witte (1992)",
        "PB": "Habit/Past behavior constructs in TPB extensions (e.g., Ouellette & Wood, 1998)",
    }

    for construct, spec in specs.items():
        for item in spec.items:
            entries.append({
                "variable": item,
                "construct": construct,
                "item_text": item_texts.get(item, ""),
                "scale": "1=Strongly Disagree, 7=Strongly Agree",
                "direction": "Positive",
                "source": sources.get(construct, "")
            })
    return pd.DataFrame(entries)


def run_efa(df_items: pd.DataFrame, n_factors: int) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, float]]:
    # KMO and Bartlett
    kmo_all, kmo_model = calculate_kmo(df_items.values)
    chi2, p = calculate_bartlett_sphericity(df_items.values)

    fa = FactorAnalyzer(n_factors=n_factors, rotation='oblimin', method='ml')
    fa.fit(df_items.values)
    loadings = pd.DataFrame(fa.loadings_, index=df_items.columns, columns=[f"F{i+1}" for i in range(n_factors)])
    # Factor correlation matrix (Phi)
    phi = pd.DataFrame(fa.phi_, index=[f"F{i+1}" for i in range(n_factors)], columns=[f"F{i+1}" for i in range(n_factors)])
    stats_out = {"KMO_model": float(kmo_model), "Bartlett_chi2": float(chi2), "Bartlett_p": float(p)}
    return loadings, phi, stats_out


def build_semopy_model(specs: Dict[str, ConstructSpec]) -> str:
    lines = []
    # Measurement model
    for name, spec in specs.items():
        rhs = " + ".join(spec.items)
        lines.append(f"{name} =~ {rhs}")
    # Structural: INT regressed on predictors
    lines.append("INT ~ ATT + SN + PBC + SEFF + REFF + SEV + VUL + PB")
    return "\n".join(lines)


def compute_cr_ave(loadings: np.ndarray, resid_vars: np.ndarray) -> Tuple[float, float]:
    lam = np.asarray(loadings).reshape(-1)
    theta = np.asarray(resid_vars).reshape(-1)
    # Guard
    if len(lam) == 0:
        return np.nan, np.nan
    # Composite Reliability (CR) and Average Variance Extracted (AVE)
    sum_lam = lam.sum()
    cr = (sum_lam ** 2) / ((sum_lam ** 2) + theta.sum())
    ave = (lam ** 2).sum() / ((lam ** 2).sum() + theta.sum())
    return float(cr), float(ave)


def run_cfa_and_reliability(likert_df: pd.DataFrame, specs: Dict[str, ConstructSpec]) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, float], pd.DataFrame]:
    # Build SEM model
    model_desc = build_semopy_model(specs)
    # Fit
    m = Model(model_desc)
    data = likert_df.drop(columns=["respondent_id"]).copy()
    # Standardize items for SEM to stabilize fitting
    scaler = StandardScaler()
    data_std = pd.DataFrame(scaler.fit_transform(data.values), columns=data.columns)
    m.fit(data_std)
    stats = calc_stats(m)

    # Extract standardized solution
    est = m.inspect(std_est=True)
    # Loadings
    load_rows = est[est["op"] == "~".replace("~", "=~")]  # safeguard if API changes
    # semopy uses op '=~' for loadings
    loadings_df = est[est["op"] == "=~"][["lval", "rval", "Estimate"]].rename(columns={"lval": "factor", "rval": "item", "Estimate": "loading"})
    # Residual variances (items)
    resid_df = est[(est["op"] == "~~") & (est["lval"] == est["rval"])]

    # Paths for INT
    paths_df = est[(est["op"] == "~") & (est["lval"] == "INT")][["lval", "rval", "Estimate"]].rename(columns={"lval": "dv", "rval": "predictor", "Estimate": "beta"})

    # Reliability per construct
    rel_rows = []
    for name, spec in specs.items():
        # Cronbach alpha (on standardized items)
        X = data_std[spec.items].values
        alpha = cronbach_alpha(X)
        # For CR/AVE, get loadings and residual variances
        lams = loadings_df[loadings_df["factor"] == name]["loading"].values
        # Residual variances for items
        theta = []
        for item in spec.items:
            row = resid_df[resid_df["lval"] == item]
            if not row.empty:
                theta.append(float(row["Estimate"].values[0]))
        if len(theta) != len(lams):
            # fallback approximation assuming standardized model
            theta = list(1.0 - (lams ** 2))
        cr, ave = compute_cr_ave(lams, np.array(theta))
        rel_rows.append({
            "construct": name,
            "num_items": len(spec.items),
            "alpha": alpha,
            "CR": cr,
            "AVE": ave,
        })
    reliability_df = pd.DataFrame(rel_rows)

    # Fit indices of interest
    fit_indices = {
        k: float(stats.__dict__[k]) for k in [
            "n_params", "logl", "aic", "bic", "rmsea", "srmr", "gfi", "agfi", "cfi", "tli", "df", "chi2"
        ] if hasattr(stats, k)
    }

    return loadings_df, paths_df, fit_indices, reliability_df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    os.makedirs("/workspace/data", exist_ok=True)
    os.makedirs("/workspace/outputs", exist_ok=True)

    # Build dataset
    likert_df, specs, cont_df = build_dataset(args.n, args.seed)

    # Save dataset (Likert items only)
    data_path = "/workspace/data/t1_dataset.csv"
    likert_df.to_csv(data_path, index=False)

    # Save continuous (for reference)
    cont_path = "/workspace/data/t1_dataset_continuous.csv"
    cont_df.to_csv(cont_path, index=False)

    # Codebook
    codebook_df = create_codebook(specs)
    codebook_path = "/workspace/outputs/codebook_t1.csv"
    codebook_df.to_csv(codebook_path, index=False)

    # Correlation matrix
    corr = likert_df.drop(columns=["respondent_id"]).corr()
    corr_path = "/workspace/outputs/correlation_matrix.csv"
    corr.to_csv(corr_path)

    # EFA on all items (choose number of factors = theoretical)
    all_item_cols = [c for c in likert_df.columns if c != "respondent_id"]
    efa_loadings, efa_phi, efa_stats = run_efa(likert_df[all_item_cols], n_factors=9)
    efa_loadings.to_csv("/workspace/outputs/efa_loadings.csv")
    efa_phi.to_csv("/workspace/outputs/efa_factor_correlations.csv")
    with open("/workspace/outputs/efa_stats.json", "w") as f:
        json.dump(efa_stats, f, indent=2)

    # CFA / SEM
    loadings_df, paths_df, fit_indices, reliability_df = run_cfa_and_reliability(likert_df, specs)
    loadings_df.to_csv("/workspace/outputs/cfa_loadings.csv", index=False)
    paths_df.to_csv("/workspace/outputs/cfa_paths_INT.csv", index=False)
    with open("/workspace/outputs/cfa_fit_indices.json", "w") as f:
        json.dump(fit_indices, f, indent=2)
    reliability_df.to_csv("/workspace/outputs/reliability.csv", index=False)

    # KMO & Bartlett already saved as part of EFA stats

    print("Saved:\n -", data_path, "\n -", cont_path, "\n -", codebook_path)
    print("Outputs in /workspace/outputs: correlation_matrix.csv, efa_*, cfa_*, reliability.csv")


if __name__ == "__main__":
    main()
