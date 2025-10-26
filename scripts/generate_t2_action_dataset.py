#!/usr/bin/env python3
"""
Generate fabricated dataset for Section C: Time 2 (T2) Action variables.
Includes:
- SRB1..SRB5 (Likert 1-7) self-reported behaviors
- Objective scenario-based quiz responses and scores (5 scenarios, total 0-10)
- T1_Intention (Likert 1-7)
- Intention_Behavior_Gap (unstandardized residuals from OLS: SRB_Mean ~ T1_Intention)
- Reliability diagnostics (Cronbach's alpha for SRB and objective)
Outputs: CSV, Parquet, scenario bank CSV, metrics JSON, and a ZIP bundling all.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import pandas as pd


@dataclass
class Scenario:
    scenario_id: str
    prompt: str
    option_a: str
    option_b: str
    option_c: str
    score_a: int
    score_b: int
    score_c: int
    correct_option: str  # 'a' | 'b' | 'c'
    difficulty: float  # higher = harder


SCENARIOS: List[Scenario] = [
    Scenario(
        scenario_id="S1",
        prompt=(
            "You receive an SMS: 'Your account is locked. Click here to secure it: bit.ly/...'. "
            "What do you do?"
        ),
        option_a="Click the link immediately",
        option_b="Call your bank using the number on your card",
        option_c="Ignore it",
        score_a=0,
        score_b=2,
        score_c=1,
        correct_option="b",
        difficulty=0.3,
    ),
    Scenario(
        scenario_id="S2",
        prompt=(
            "Your banking app asks you to re-enter your password on a pop-up while the app is minimized."
        ),
        option_a="Enter the password into the pop-up",
        option_b="Re-open the app and use built-in login only",
        option_c="Screenshot it and email support later",
        score_a=0,
        score_b=2,
        score_c=1,
        correct_option="b",
        difficulty=0.5,
    ),
    Scenario(
        scenario_id="S3",
        prompt=(
            "You get an email: 'Security alert: verify your account within 24 hours' with a link to a site that looks similar to your bank."
        ),
        option_a="Click the link and verify immediately",
        option_b="Type your bank URL manually or use the app",
        option_c="Forward the email to a friend to ask",
        score_a=0,
        score_b=2,
        score_c=1,
        correct_option="b",
        difficulty=0.6,
    ),
    Scenario(
        scenario_id="S4",
        prompt=(
            "You receive a call claiming to be from your bank asking for your one-time 2FA code to fix a problem."
        ),
        option_a="Share the code because the caller sounds urgent",
        option_b="Decline and call the bank back using the official number",
        option_c="Hang up and do nothing",
        score_a=0,
        score_b=2,
        score_c=1,
        correct_option="b",
        difficulty=0.7,
    ),
    Scenario(
        scenario_id="S5",
        prompt=(
            "At a cafe, you connect to 'Free_Public_WiFi' and the banking app requests login."
        ),
        option_a="Proceed to login over public Wi-Fi",
        option_b="Use cellular data or wait for a trusted network",
        option_c="Use a VPN then login",
        score_a=0,
        score_b=2,
        score_c=1,
        correct_option="b",
        difficulty=0.8,
    ),
]


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def set_seed(seed: int) -> None:
    np.random.seed(seed)


def cronbach_alpha(items_2d: np.ndarray) -> float:
    """Compute Cronbach's alpha for items (n_samples x n_items)."""
    if items_2d.ndim != 2:
        raise ValueError("items_2d must be 2D array")
    n_items = items_2d.shape[1]
    if n_items < 2:
        return float("nan")
    item_vars = items_2d.var(axis=0, ddof=1)
    total_scores = items_2d.sum(axis=1)
    total_var = total_scores.var(ddof=1)
    if total_var <= 1e-12:
        return float("nan")
    alpha = (n_items / (n_items - 1.0)) * (1.0 - item_vars.sum() / total_var)
    return float(alpha)


def sample_likert_from_latent(
    latent: np.ndarray,
    base_mean: float = 4.5,
    base_sd: float = 1.2,
    noise_sd: float = 0.8,
    clip_min: int = 1,
    clip_max: int = 7,
) -> np.ndarray:
    """Linearly scale latent to Likert 1..7 with noise and clipping."""
    raw = base_mean + base_sd * latent + np.random.normal(0.0, noise_sd, size=latent.shape[0])
    rounded = np.rint(raw)
    clipped = np.clip(rounded, clip_min, clip_max)
    return clipped.astype(int)


def simulate_dataset(n: int, seed: int) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
    set_seed(seed)

    # Latent structure: intention and behavior propensity moderately correlated
    corr = 0.48
    cov = np.array([[1.0, corr], [corr, 1.0]])
    mean = np.array([0.0, 0.0])
    latent_mv = np.random.multivariate_normal(mean, cov, size=n)
    latent_intention = latent_mv[:, 0]
    latent_behavior_propensity = latent_mv[:, 1]

    # Social desirability bias (inflates SRB, not objective)
    social_desirability_bias = np.random.normal(0.25, 0.30, size=n)  # mean +0.25 on Likert scale

    # T1 Intention Likert
    t1_intention = sample_likert_from_latent(latent_intention, base_mean=4.6, base_sd=1.1, noise_sd=0.7)

    # SRB items: item difficulties and loadings
    item_difficulties = np.array([-0.1, 0.0, 0.1, 0.2, -0.2])
    item_loadings = np.array([0.90, 0.85, 0.88, 0.82, 0.80])

    srb_items = []
    for j in range(5):
        latent_item = (
            item_loadings[j] * latent_behavior_propensity
            + 0.25 * np.random.normal(size=n)  # item-specific noise
            + 0.20 * social_desirability_bias
            + item_difficulties[j]
        )
        srb_j = sample_likert_from_latent(latent_item, base_mean=4.7, base_sd=1.0, noise_sd=0.6)
        srb_items.append(srb_j)
    srb_arr = np.vstack(srb_items).T  # n x 5

    # Objective scenarios: choose among a/b/c with probabilities based on propensity & difficulty
    def softmax(x: np.ndarray) -> np.ndarray:
        x = x - np.max(x, axis=1, keepdims=True)
        ex = np.exp(x)
        return ex / ex.sum(axis=1, keepdims=True)

    obj_choice_options = []  # list of arrays 'a','b','c'
    obj_scores = []  # list of arrays scores 0/1/2

    for sc in SCENARIOS:
        # Utility for each option as a function of behavior propensity and scenario difficulty
        # Encourage 'b' (best), then 'c', then 'a'
        u_a = -1.5 - 1.2 * latent_behavior_propensity + 0.8 * sc.difficulty
        u_b = 1.5 + 1.4 * latent_behavior_propensity - 0.6 * sc.difficulty
        u_c = 0.2 + 0.6 * latent_behavior_propensity - 0.2 * sc.difficulty
        logits = np.vstack([u_a, u_b, u_c]).T  # n x 3
        probs = softmax(logits)
        choices = []
        scores = []
        for i in range(n):
            c = np.random.choice(['a', 'b', 'c'], p=probs[i])
            if c == 'a':
                s = sc.score_a
            elif c == 'b':
                s = sc.score_b
            else:
                s = sc.score_c
            choices.append(c)
            scores.append(s)
        obj_choice_options.append(np.array(choices))
        obj_scores.append(np.array(scores))

    obj_scores_arr = np.vstack(obj_scores).T  # n x 5
    objective_total = obj_scores_arr.sum(axis=1)

    # Assemble dataframe
    df = pd.DataFrame({
        'participant_id': [f'P{i:05d}' for i in range(1, n + 1)],
        'T1_Intention': t1_intention,
    })

    for j in range(5):
        df[f'SRB{j+1}'] = srb_arr[:, j]

    df['SRB_Mean'] = df[[f'SRB{i}' for i in range(1, 6)]].mean(axis=1)

    for j, sc in enumerate(SCENARIOS):
        df[f'{sc.scenario_id}_Response'] = obj_choice_options[j]
        df[f'{sc.scenario_id}_Score'] = obj_scores_arr[:, j]

    df['Objective_Score_Total'] = objective_total
    # Alias to match requested variable name
    df['Objective_Score'] = df['Objective_Score_Total']

    # Reliability metrics
    alpha_srb = float(cronbach_alpha(srb_arr.astype(float)))
    alpha_obj = float(cronbach_alpha(obj_scores_arr.astype(float)))

    # Residuals: SRB_Mean ~ Intercept + T1_Intention (unstandardized)
    X = np.column_stack([np.ones(n), df['T1_Intention'].values.astype(float)])
    y = df['SRB_Mean'].values.astype(float)
    # OLS estimate b = (X'X)^-1 X'y
    XtX = X.T @ X
    try:
        XtX_inv = np.linalg.inv(XtX)
    except np.linalg.LinAlgError:
        XtX_inv = np.linalg.pinv(XtX)
    b = XtX_inv @ (X.T @ y)
    y_hat = X @ b
    residuals = y - y_hat
    df['Intention_Behavior_Gap'] = residuals

    # Secondary diagnostics
    metrics = {
        'n': n,
        'seed': seed,
        'cronbach_alpha_SRB5': alpha_srb,
        'cronbach_alpha_Objective5': alpha_obj,
        'ols_coefficients': {'intercept': float(b[0]), 'T1_Intention': float(b[1])},
        'correlations': {
            'corr_T1Intention_SRBMean': float(np.corrcoef(df['T1_Intention'], df['SRB_Mean'])[0, 1]),
            'corr_T1Intention_ObjectiveTotal': float(np.corrcoef(df['T1_Intention'], df['Objective_Score_Total'])[0, 1]),
            'corr_SRBMean_ObjectiveTotal': float(np.corrcoef(df['SRB_Mean'], df['Objective_Score_Total'])[0, 1]),
        },
        'notes': (
            "SRB items are influenced by a behavior propensity latent factor and a social desirability bias. "
            "Objective items depend on propensity and scenario difficulty; 'b' is optimal, 'c' is acceptable, 'a' is unsafe. "
            "Intention_Behavior_Gap is the unstandardized residual from regressing SRB_Mean on T1_Intention with an intercept."
        ),
    }

    # Scenario bank table
    scenario_rows = []
    for sc in SCENARIOS:
        scenario_rows.append({
            'scenario_id': sc.scenario_id,
            'prompt': sc.prompt,
            'option_a': sc.option_a,
            'option_b': sc.option_b,
            'option_c': sc.option_c,
            'score_a': sc.score_a,
            'score_b': sc.score_b,
            'score_c': sc.score_c,
            'correct_option': sc.correct_option,
            'difficulty': sc.difficulty,
        })
    scenario_bank_df = pd.DataFrame(scenario_rows)

    return df, scenario_bank_df, metrics


def write_outputs(df: pd.DataFrame, scenario_bank_df: pd.DataFrame, metrics: dict, out_dir: str) -> dict:
    ensure_dir(out_dir)

    csv_path = os.path.join(out_dir, 't2_action_dataset.csv')
    parquet_path = os.path.join(out_dir, 't2_action_dataset.parquet')
    scenario_bank_path = os.path.join(out_dir, 'scenario_bank.csv')
    metrics_path = os.path.join(out_dir, 'metrics.json')
    zip_path = os.path.join(out_dir, 't2_action_dataset_bundle.zip')

    df.to_csv(csv_path, index=False)
    try:
        df.to_parquet(parquet_path, index=False)
    except Exception as e:
        # Fallback: skip parquet if pyarrow missing
        parquet_error = str(e)
        parquet_path = None
    else:
        parquet_error = None

    scenario_bank_df.to_csv(scenario_bank_path, index=False)

    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)

    # Create ZIP bundle
    import zipfile
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(csv_path, arcname=os.path.basename(csv_path))
        if parquet_path is not None:
            zf.write(parquet_path, arcname=os.path.basename(parquet_path))
        zf.write(scenario_bank_path, arcname=os.path.basename(scenario_bank_path))
        zf.write(metrics_path, arcname=os.path.basename(metrics_path))

    return {
        'csv': csv_path,
        'parquet': parquet_path,
        'scenario_bank': scenario_bank_path,
        'metrics': metrics_path,
        'zip': zip_path,
        'parquet_error': parquet_error,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate fabricated T2 action dataset")
    parser.add_argument('--n', type=int, default=5000, help='Number of participants')
    parser.add_argument('--seed', type=int, default=7, help='Random seed')
    parser.add_argument('--out_dir', type=str, default=os.path.join('data', 't2_action'), help='Output directory')
    args = parser.parse_args()

    out_dir = args.out_dir
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(os.getcwd(), out_dir)
    ensure_dir(out_dir)

    df, scenario_bank_df, metrics = simulate_dataset(n=args.n, seed=args.seed)
    paths = write_outputs(df, scenario_bank_df, metrics, out_dir)

    # Print a compact summary to stdout
    print(json.dumps({
        'shape': list(df.shape),
        'paths': {k: v for k, v in paths.items() if k != 'parquet_error'},
        'metrics': {
            'cronbach_alpha_SRB5': metrics['cronbach_alpha_SRB5'],
            'cronbach_alpha_Objective5': metrics['cronbach_alpha_Objective5'],
            'ols_coefficients': metrics['ols_coefficients'],
            'correlations': metrics['correlations'],
        },
        'parquet_error': paths['parquet_error'],
        'head': df.head(3).to_dict(orient='records'),
    }, indent=2))

    return 0


if __name__ == '__main__':
    sys.exit(main())
