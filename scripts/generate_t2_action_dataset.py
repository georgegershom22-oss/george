#!/usr/bin/env python3
"""
Generate T2 (Action) dataset with:
- SRB1..SRB5 (1-7 Likert)
- Objective scenarios (5 items; per-item choice and score; total score)
- Intention_T1 (1-7)
- Intention_Behavior_Gap (unstandardized residual: SRB_Mean ~ Intention_T1)

Outputs:
- t2_action.csv (record-level dataset)
- objective_scenarios.csv (scenario texts, options, scoring)
- t2_codebook.csv (variable names and descriptions)
- ZIP archive containing the above

CLI:
  python generate_t2_action_dataset.py --n 2000 --seed 42 --outdir /workspace/data/t2
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import random
import statistics
import sys
import time
import zipfile
from typing import Dict, List, Tuple

try:
    import numpy as np  # Optional; script has fallbacks if unavailable
except Exception:  # pragma: no cover
    np = None  # type: ignore


def sigmoid(x: float) -> float:
    # Numerically stable-ish sigmoid
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def discretize_to_likert(value: float, min_val: int = 1, max_val: int = 7) -> int:
    return max(min_val, min(max_val, int(round(value))))


def clip(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


def generate_latents(n: int, seed: int) -> Tuple[List[float], List[float], List[float]]:
    """Generate latent variables for Intention (LI), Behavior (LB), Objective competence (OC).
    Target correlations (approx):
      corr(LI, LB) ~= 0.6, corr(LB, OC) ~= 0.4, corr(LI, OC) ~= 0.3
    """
    rng = random.Random(seed)
    if np is not None:
        mean = np.zeros(3)
        corr = np.array([
            [1.0, 0.6, 0.3],
            [0.6, 1.0, 0.4],
            [0.3, 0.4, 1.0],
        ])
        # Convert correlation to covariance (std=1)
        cov = corr
        latents = np.random.default_rng(seed).multivariate_normal(mean=mean, cov=cov, size=n)
        LI = latents[:, 0].tolist()
        LB = latents[:, 1].tolist()
        OC = latents[:, 2].tolist()
        return LI, LB, OC

    # Fallback without numpy: construct OC from LI and LB to approximate correlations
    LI = [rng.gauss(0.0, 1.0) for _ in range(n)]
    e2 = [rng.gauss(0.0, 1.0) for _ in range(n)]
    LB = [0.6 * li + math.sqrt(1 - 0.6 ** 2) * e for li, e in zip(LI, e2)]
    # Choose weights to approximate corr targets: see analysis
    a, b = 0.15, 0.30
    e3 = [rng.gauss(0.0, 1.0) for _ in range(n)]
    resid_scale = math.sqrt(max(1e-6, 1.0 - a * a - b * b - 2 * a * b * 0.6))
    OC = [a * li + b * lb + resid_scale * e for li, lb, e in zip(LI, LB, e3)]
    return LI, LB, OC


def generate_intention_t1(LI: List[float], seed: int) -> List[float]:
    rng = random.Random(seed + 11)
    # Scale latent to 1-7 Likert-like continuous
    intentions = []
    for li in LI:
        noise = rng.gauss(0.0, 0.7)
        val = 4.0 + 1.0 * li + noise
        intentions.append(clip(val, 1.0, 7.0))
    return intentions


def generate_srb_items(LB: List[float], seed: int) -> Tuple[List[List[int]], List[float]]:
    rng = random.Random(seed + 21)
    # Five items with small difficulty/bias differences
    item_biases = [-0.30, -0.10, 0.0, 0.10, 0.25]
    item_noise_sd = [0.60, 0.65, 0.70, 0.60, 0.65]
    all_items: List[List[int]] = [[] for _ in range(5)]
    srb_mean: List[float] = []

    for i, lb in enumerate(LB):
        scores_row: List[int] = []
        for b, sd in zip(item_biases, item_noise_sd):
            noise = rng.gauss(0.0, sd)
            val = 4.0 + 0.95 * lb + b + noise
            scores_row.append(discretize_to_likert(val))
        for j in range(5):
            all_items[j].append(scores_row[j])
        srb_mean.append(sum(scores_row) / 5.0)

    return all_items, srb_mean


def build_objective_scenarios() -> List[Dict[str, object]]:
    # Each scenario defines option texts and score mapping
    scenarios = [
        {
            "id": "Q1",
            "text": (
                "You receive an SMS: 'Your account is locked. Click here to secure it: "
                "bit.ly/...'. What do you do?"
            ),
            "options": [
                {"label": "a", "text": "Click the link immediately", "score": 0},
                {
                    "label": "b",
                    "text": "Call your bank using the number on your card",
                    "score": 2,
                },
                {"label": "c", "text": "Ignore it", "score": 1},
            ],
            # Thresholds tune difficulty and middle-choice tendency
            "p2_threshold": 0.10,
            "p1_bias": 0.10,
        },
        {
            "id": "Q2",
            "text": (
                "You're on public Wi‑Fi and need to check your bank balance. What do you do?"
            ),
            "options": [
                {
                    "label": "a",
                    "text": "Log in to your bank directly over public Wi‑Fi",
                    "score": 0,
                },
                {
                    "label": "b",
                    "text": "Use mobile data or a trusted VPN before logging in",
                    "score": 2,
                },
                {
                    "label": "c",
                    "text": "Use a private/incognito browser window on public Wi‑Fi",
                    "score": 1,
                },
            ],
            "p2_threshold": 0.05,
            "p1_bias": 0.00,
        },
        {
            "id": "Q3",
            "text": (
                "An email says: 'Unusual login detected—update password here' with a link."
                " What do you do?"
            ),
            "options": [
                {"label": "a", "text": "Click the link to update password", "score": 0},
                {
                    "label": "b",
                    "text": "Report phishing; navigate to bank manually to check",
                    "score": 2,
                },
                {"label": "c", "text": "Delete the email", "score": 1},
            ],
            "p2_threshold": 0.00,
            "p1_bias": 0.05,
        },
        {
            "id": "Q4",
            "text": (
                "An ATM shows an error and has a sticker with a support number to call."
                " What do you do?"
            ),
            "options": [
                {"label": "a", "text": "Call the number on the ATM sticker", "score": 0},
                {
                    "label": "b",
                    "text": "Use the official bank app/support to verify/report",
                    "score": 2,
                },
                {
                    "label": "c",
                    "text": "Use another ATM and monitor account closely",
                    "score": 1,
                },
            ],
            "p2_threshold": 0.15,
            "p1_bias": 0.10,
        },
        {
            "id": "Q5",
            "text": (
                "You get a call 'from your bank' asking for a one‑time passcode to verify your account."
                " What do you do?"
            ),
            "options": [
                {"label": "a", "text": "Provide the passcode to the caller", "score": 0},
                {
                    "label": "b",
                    "text": "Refuse and call the bank back using the official number",
                    "score": 2,
                },
                {"label": "c", "text": "Hang up and block the number", "score": 1},
            ],
            "p2_threshold": 0.05,
            "p1_bias": 0.15,
        },
    ]
    return scenarios


def sample_objective_response(oc: float, scenario: Dict[str, object], rng: random.Random) -> Tuple[str, int]:
    # Probability of optimal (score=2) increases with objective competence minus threshold
    p2 = sigmoid(oc - float(scenario["p2_threshold"]))
    # If not optimal, probability of middle option increases with oc + bias
    p1 = sigmoid(oc + float(scenario["p1_bias"]))

    r = rng.random()
    if r < p2:
        target_score = 2
    else:
        r2 = rng.random()
        target_score = 1 if r2 < p1 else 0

    # Map to an option label with that score
    options = [opt for opt in scenario["options"] if int(opt["score"]) == target_score]
    chosen = rng.choice(options)
    return str(chosen["label"]), int(chosen["score"])


def compute_ols_residuals(y: List[float], x: List[float]) -> List[float]:
    # Unstandardized residuals from y ~ b0 + b1*x
    # Use numpy if available; otherwise use closed-form with means
    assert len(y) == len(x)
    n = len(y)
    if n == 0:
        return []
    if np is not None:
        X = np.column_stack([np.ones(n), np.array(x)])
        beta, *_ = np.linalg.lstsq(X, np.array(y), rcond=None)
        y_hat = (X @ beta).tolist()
        return [yi - yhi for yi, yhi in zip(y, y_hat)]
    # Fallback closed-form OLS
    mx = statistics.fmean(x)
    my = statistics.fmean(y)
    cov_xy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / n
    var_x = sum((xi - mx) ** 2 for xi in x) / n
    if var_x <= 1e-12:
        # Degenerate case; return centered y as residuals
        return [yi - my for yi in y]
    b1 = cov_xy / var_x
    b0 = my - b1 * mx
    return [yi - (b0 + b1 * xi) for xi, yi in zip(x, y)]


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_csv(path: str, header: List[str], rows: List[List[object]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for row in rows:
            w.writerow(row)


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate T2 Action dataset with objective scenarios and residual gap")
    parser.add_argument("--n", type=int, default=2000, help="Number of participants (rows)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--outdir",
        type=str,
        default="/workspace/data/t2",
        help="Output directory for CSVs and ZIP",
    )
    args = parser.parse_args(argv)

    n = int(args.n)
    seed = int(args.seed)
    outdir = os.path.abspath(args.outdir)
    ensure_dir(outdir)

    # 1) Latents
    LI, LB, OC = generate_latents(n=n, seed=seed)

    # 2) Observed Intention_T1 (1-7 continuous bounded)
    intention_t1 = generate_intention_t1(LI, seed=seed)

    # 3) SRB items (1-7 integers) and mean
    srb_items, srb_mean = generate_srb_items(LB, seed=seed)

    # 4) Objective scenarios
    scenarios = build_objective_scenarios()
    rng = random.Random(seed + 31)

    obj_choices: List[List[str]] = [[] for _ in range(len(scenarios))]
    obj_scores: List[List[int]] = [[] for _ in range(len(scenarios))]

    for i in range(n):
        oc = OC[i]
        for si, sc in enumerate(scenarios):
            choice, score = sample_objective_response(oc, sc, rng)
            obj_choices[si].append(choice)
            obj_scores[si].append(score)

    obj_total = [sum(scores_row[i] for scores_row in obj_scores) for i in range(n)]
    obj_percent = [round(100.0 * t / (2 * len(scenarios)), 2) for t in obj_total]

    # 5) Residual gap: SRB_Mean ~ Intention_T1
    gap = compute_ols_residuals(y=srb_mean, x=intention_t1)

    # 6) Write main dataset
    header = (
        ["participant_id", "Intention_T1"]
        + [f"SRB{j+1}" for j in range(5)]
        + ["SRB_Mean"]
        + sum([[f"Objective_{sc['id']}_Choice", f"Objective_{sc['id']}_Score"] for sc in scenarios], [])
        + ["Objective_Score_Total", "Objective_Score_Percent", "Intention_Behavior_Gap"]
    )

    rows: List[List[object]] = []
    for i in range(n):
        row: List[object] = [i + 1, round(intention_t1[i], 2)]
        row += [srb_items[j][i] for j in range(5)]
        row += [round(srb_mean[i], 3)]
        for si in range(len(scenarios)):
            row += [obj_choices[si][i], obj_scores[si][i]]
        row += [obj_total[i], obj_percent[i], round(gap[i], 4)]
        rows.append(row)

    main_csv = os.path.join(outdir, "t2_action.csv")
    write_csv(main_csv, header, rows)

    # 7) Write scenarios metadata
    scen_header = [
        "scenario_id",
        "scenario_text",
        "option_a_text",
        "option_a_score",
        "option_b_text",
        "option_b_score",
        "option_c_text",
        "option_c_score",
    ]
    scen_rows: List[List[object]] = []
    for sc in scenarios:
        opts = sc["options"]
        scen_rows.append([
            sc["id"],
            sc["text"],
            opts[0]["text"],
            opts[0]["score"],
            opts[1]["text"],
            opts[1]["score"],
            opts[2]["text"],
            opts[2]["score"],
        ])

    scen_csv = os.path.join(outdir, "objective_scenarios.csv")
    write_csv(scen_csv, scen_header, scen_rows)

    # 8) Write codebook
    codebook_rows = [
        [
            "participant_id",
            "Unique participant row identifier (1..N)",
        ],
        [
            "Intention_T1",
            "Time 1 intention to perform banking security behaviors (1-7, bounded)",
        ],
    ]
    for j, text in enumerate(
        [
            "Check bank statement for unauthorized transactions (1=Never, 7=Always)",
            "Use strong, unique passwords for banking (1=Never, 7=Always)",
            "Enable two-factor authentication (1=Never, 7=Always)",
            "Log out of banking apps/sites after use (1=Never, 7=Always)",
            "Verify a text/email alert before clicking a link (1=Never, 7=Always)",
        ]
    ):
        codebook_rows.append([f"SRB{j+1}", text])
    codebook_rows.append(["SRB_Mean", "Mean of SRB1..SRB5 (1-7)"])

    for sc in scenarios:
        codebook_rows.append(
            [
                f"Objective_{sc['id']}_Choice",
                f"Choice (a/b/c) for objective scenario {sc['id']}",
            ]
        )
        codebook_rows.append(
            [
                f"Objective_{sc['id']}_Score",
                f"Score (0/1/2) for objective scenario {sc['id']}",
            ]
        )

    codebook_rows += [
        [
            "Objective_Score_Total",
            "Sum of objective scenario scores (0-10)",
        ],
        [
            "Objective_Score_Percent",
            "Objective score as percent (0-100)",
        ],
        [
            "Intention_Behavior_Gap",
            "Residuals from OLS: SRB_Mean ~ Intention_T1 (unstandardized)",
        ],
    ]

    codebook_csv = os.path.join(outdir, "t2_codebook.csv")
    write_csv(codebook_csv, ["variable", "description"], codebook_rows)

    # 9) Zip bundle
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    zip_path = os.path.join(outdir, f"t2_action_dataset_{timestamp}.zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(main_csv, arcname=os.path.basename(main_csv))
        zf.write(scen_csv, arcname=os.path.basename(scen_csv))
        zf.write(codebook_csv, arcname=os.path.basename(codebook_csv))

    # Console summary
    try:
        mean_gap = statistics.fmean(gap)
        std_gap = statistics.pstdev(gap)
        mean_srb = statistics.fmean(srb_mean)
        mean_int = statistics.fmean(intention_t1)
        mean_obj = statistics.fmean(obj_total)
    except Exception:
        mean_gap = std_gap = mean_srb = mean_int = mean_obj = float("nan")

    print("Wrote:")
    print(f"  - {main_csv}")
    print(f"  - {scen_csv}")
    print(f"  - {codebook_csv}")
    print(f"  - {zip_path}")
    print("\nSummary stats (approx):")
    print(f"  SRB_Mean: mean={mean_srb:.3f}")
    print(f"  Intention_T1: mean={mean_int:.3f}")
    print(f"  Objective_Score_Total (0-10): mean={mean_obj:.3f}")
    print(f"  Intention_Behavior_Gap: mean={mean_gap:.4f}, sd={std_gap:.4f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
