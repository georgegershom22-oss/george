#!/usr/bin/env python3

import csv
import math
import os
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

# Reproducibility
DEFAULT_SEED = 42


@dataclass
class ItemSpec:
    construct: str
    code: str
    text: str
    reverse: bool = False


def make_codebook() -> List[ItemSpec]:
    # Multi-item 7-point Likert for all constructs
    return [
        # TPB - Attitude (semantic differentials)
        ItemSpec("ATT", "ATT1", "Following bank security steps is beneficial/harmful."),
        ItemSpec("ATT", "ATT2", "Following bank security steps is wise/foolish."),
        ItemSpec("ATT", "ATT3", "Following bank security steps is important/unimportant."),
        # TPB - Subjective Norm
        ItemSpec("SN", "SN1", "Most people important to me think I should follow these steps."),
        ItemSpec("SN", "SN2", "My family expects me to be diligent with my bank security."),
        # TPB - Perceived Behavioral Control
        ItemSpec("PBC", "PBC1", "Following all the security steps would be easy/difficult."),
        ItemSpec("PBC", "PBC2", "I have the resources, time, and knowledge to follow them."),
        ItemSpec("PBC", "PBC3", "Whether I follow them is entirely up to me."),
        # TPB - Intention (dependent at T1)
        ItemSpec("INT", "INT1", "I intend to follow all recommended security steps in the next 3 months."),
        ItemSpec("INT", "INT2", "I plan to make an effort to be more diligent."),
        # PMT - Threat Appraisal: Severity (expanded to multi-item)
        ItemSpec("SEV", "SEV1", "The financial loss from bank fraud would be severe for me."),
        ItemSpec("SEV", "SEV2", "Financial consequences of bank fraud would be very serious for me."),
        # PMT - Threat Appraisal: Vulnerability
        ItemSpec("VULN", "VULN1", "I am at high risk of experiencing bank fraud."),
        ItemSpec("VULN", "VULN2", "It is likely that I could be targeted by bank fraud."),
        # PMT - Coping Appraisal: Self-Efficacy
        ItemSpec("SE", "SE1", "I am confident I can perform the security steps correctly."),
        ItemSpec("SE", "SE2", "I have the ability to carry out all recommended security steps."),
        ItemSpec("SE", "SE3", "I can manage the security steps even if they are inconvenient."),
        # PMT - Coping Appraisal: Response Efficacy
        ItemSpec("RE", "RE1", "These security steps are effective in protecting me."),
        ItemSpec("RE", "RE2", "Following the steps significantly reduces my risk of fraud."),
        ItemSpec("RE", "RE3", "The recommended steps are a reliable way to enhance security."),
        # Past Behavior (Habit)
        ItemSpec("PB", "PB1", "In the past 3 months, I followed recommended security steps often."),
        ItemSpec("PB", "PB2", "In the past 3 months, I consistently adhered to bank security steps."),
    ]


def likertize(x: np.ndarray) -> np.ndarray:
    # Map continuous z to 1..7 via fixed thresholds (approx equal-prob bins)
    # Thresholds at standard normal quantiles for 1/7 increments
    qs = np.array([1, 2, 3, 4, 5, 6]) / 7.0
    th = np.quantile(np.random.normal(size=250000), qs)
    # Vectorized binning
    bins = np.digitize(x, th, right=False) + 1
    bins = np.clip(bins, 1, 7)
    return bins.astype(int)


def simulate_latents(n: int, rng: np.random.Generator) -> Tuple[np.ndarray, List[str]]:
    # Latent constructs ordering
    constructs = ["ATT", "SN", "PBC", "SEV", "VULN", "SE", "RE", "PB"]

    # Specify latent correlation matrix (positive manifold with plausible structure)
    #            ATT  SN   PBC  SEV  VULN  SE   RE   PB
    corr = np.array([
        [1.00, 0.35, 0.45, 0.10, 0.10, 0.40, 0.35, 0.30],  # ATT
        [0.35, 1.00, 0.30, 0.10, 0.15, 0.25, 0.20, 0.20],  # SN
        [0.45, 0.30, 1.00, 0.05, 0.05, 0.55, 0.45, 0.40],  # PBC
        [0.10, 0.10, 0.05, 1.00, 0.40, 0.10, 0.10, 0.05],  # SEV
        [0.10, 0.15, 0.05, 0.40, 1.00, 0.10, 0.10, 0.05],  # VULN
        [0.40, 0.25, 0.55, 0.10, 0.10, 1.00, 0.50, 0.35],  # SE
        [0.35, 0.20, 0.45, 0.10, 0.10, 0.50, 1.00, 0.30],  # RE
        [0.30, 0.20, 0.40, 0.05, 0.05, 0.35, 0.30, 1.00],  # PB
    ], dtype=float)

    # Cholesky may fail if not PSD; fix by nearest PSD projection if needed
    # Eigen-decompose, floor small negatives
    w, V = np.linalg.eigh(corr)
    w = np.clip(w, 1e-6, None)
    corr_psd = (V * w) @ V.T
    L = np.linalg.cholesky(corr_psd)

    z = rng.normal(size=(n, len(constructs)))
    latents = z @ L.T  # N x K

    return latents, constructs


def build_measurement_matrix(codebook: List[ItemSpec]) -> Tuple[np.ndarray, List[str], Dict[str, List[int]]]:
    """Return Lambda (items x factors), item order, and mapping from construct->item indices.

    Note: This builds loadings only for the eight exogenous constructs.
    INT items are collected in by_construct but their loadings are added later.
    """
    constructs = ["ATT", "SN", "PBC", "SEV", "VULN", "SE", "RE", "PB"]
    by_construct: Dict[str, List[int]] = {}
    item_codes: List[str] = []

    # Assign loadings within plausible ranges
    loading_ranges = {
        "ATT": (0.70, 0.85),
        "SN": (0.65, 0.80),
        "PBC": (0.65, 0.85),
        "SEV": (0.60, 0.75),
        "VULN": (0.60, 0.75),
        "SE": (0.70, 0.85),
        "RE": (0.70, 0.85),
        "PB": (0.65, 0.80),
    }

    lam_rows: List[List[float]] = []
    for idx, it in enumerate(codebook):
        item_codes.append(it.code)
        lam = [0.0] * len(constructs)
        if it.construct in loading_ranges:
            low, high = loading_ranges[it.construct]
            lam[constructs.index(it.construct)] = random.uniform(low, high)
        lam_rows.append(lam)
        by_construct.setdefault(it.construct, []).append(idx)

    Lambda = np.array(lam_rows, dtype=float)
    return Lambda, item_codes, by_construct


def generate_dataset(n: int, seed: int = DEFAULT_SEED) -> Tuple[np.ndarray, List[ItemSpec], List[str], Dict[str, List[int]], np.ndarray, np.ndarray]:
    random.seed(seed)
    rng = np.random.default_rng(seed)

    codebook = make_codebook()
    # Latents for ATT,SN,PBC,SEV,VULN,SE,RE,PB
    latents, latent_names = simulate_latents(n, rng)

    # Structural model for INT (intention)
    # INT = beta * [ATT,SN,PBC,SEV,VULN,SE,RE,PB] + noise
    betas = np.array([0.35, 0.20, 0.30, 0.08, -0.05, 0.15, 0.20, 0.25])
    int_noise_sd = 0.60
    INT = latents @ betas + rng.normal(scale=int_noise_sd, size=n)

    # Add INT as an additional latent (index at end)
    latents_full = np.concatenate([latents, INT.reshape(-1, 1)], axis=1)
    latent_names_full = latent_names + ["INT"]

    # Measurement model
    Lambda, item_codes, by_construct = build_measurement_matrix(codebook)

    # Expand Lambda and by_construct to include INT items
    # We know INT has two items in codebook; create Lambda rows already created but factor not present
    # We need to add a column for INT in Lambda and place loadings for INT items
    k = len(latent_names_full)
    items = len(codebook)
    # Initialize full Lambda
    Lambda_full = np.zeros((items, k), dtype=float)
    # Copy original loadings for first 8 constructs
    Lambda_full[:, : Lambda.shape[1]] = Lambda
    # Set INT loadings for its items
    for idx in by_construct.get("INT", []):
        Lambda_full[idx, latent_names_full.index("INT")] = random.uniform(0.70, 0.85)

    # Unique variances (Theta) so that communalities are reasonable
    communalities = np.sum(Lambda_full ** 2, axis=1)
    unique_var = np.clip(1.0 - communalities, 0.15, 0.60)  # avoid too small uniques

    # Generate continuous item responses: x = Lambda * f + e
    # Standardize latents to unit variance (already roughly unit due to correlation matrix)
    F = (latents_full - latents_full.mean(axis=0)) / latents_full.std(axis=0)
    e = rng.normal(scale=np.sqrt(unique_var), size=(n, items))
    X_cont = F @ Lambda_full.T + e

    # Map to 1..7 Likert
    X_likert = likertize(X_cont)

    return X_likert, codebook, item_codes, by_construct, F, Lambda_full


def write_csv_item_level(path: str, data: np.ndarray, headers: List[str]):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["respondent_id"] + headers)
        for i in range(data.shape[0]):
            writer.writerow([i + 1] + list(map(int, data[i, :].tolist())))


def write_csv_construct_level(path: str, data_items: np.ndarray, codebook: List[ItemSpec], by_construct: Dict[str, List[int]]):
    constructs = sorted(by_construct.keys())
    # Ensure multi-item constructs produce means; singletons pass-through
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["respondent_id"] + constructs)
        for r in range(data_items.shape[0]):
            row = [r + 1]
            for c in constructs:
                idxs = by_construct[c]
                vals = data_items[r, idxs]
                row.append(float(np.mean(vals)))
            writer.writerow(row)


def write_codebook_yaml(path: str, codebook: List[ItemSpec]):
    try:
        import yaml  # type: ignore
    except Exception:
        yaml = None

    payload = []
    for it in codebook:
        payload.append({
            "construct": it.construct,
            "code": it.code,
            "text": it.text,
            "reverse": it.reverse,
        })

    if yaml is not None:
        with open(path, "w") as f:
            yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)
    else:
        # Fallback to JSON-like text
        import json

        with open(path, "w") as f:
            f.write(json.dumps(payload, indent=2))


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate T1 dataset for TPB+PMT constructs with Likert items.")
    parser.add_argument("--n", type=int, default=1500, help="Number of respondents")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed")
    args = parser.parse_args()

    n = args.n
    seed = args.seed

    X_likert, codebook, item_codes, by_construct, F, Lambda_full = generate_dataset(n=n, seed=seed)

    os.makedirs("/workspace/data", exist_ok=True)

    write_csv_item_level("/workspace/data/t1_items.csv", X_likert, item_codes)
    write_csv_construct_level("/workspace/data/t1_constructs.csv", X_likert, codebook, by_construct)
    write_codebook_yaml("/workspace/data/codebook.yaml", codebook)

    # Also save latent factor scores and loadings for diagnostic purposes
    np.savetxt("/workspace/data/latent_scores.csv", np.column_stack([np.arange(1, n + 1), F]), delimiter=",", fmt="%s",
               header=",".join(["respondent_id"] + [
                   "ATT","SN","PBC","SEV","VULN","SE","RE","PB","INT"
               ]), comments="")
    np.savetxt("/workspace/data/measurement_loadings.csv", Lambda_full, delimiter=",", fmt="%.4f",
               header=",".join(["ATT","SN","PBC","SEV","VULN","SE","RE","PB","INT"]), comments="")

    print("Generated:")
    print(" - /workspace/data/t1_items.csv")
    print(" - /workspace/data/t1_constructs.csv")
    print(" - /workspace/data/codebook.yaml")
    print(" - /workspace/data/latent_scores.csv")
    print(" - /workspace/data/measurement_loadings.csv")


if __name__ == "__main__":
    main()
