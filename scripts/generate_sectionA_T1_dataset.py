#!/usr/bin/env python3
import argparse
import json
import math
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class CodeMap:
    country: Dict[int, str]
    gender: Dict[int, str]
    education: Dict[int, str]
    bank_type: Dict[int, str]
    freq_use: Dict[int, str]
    income_bands_ngn: Dict[int, str]
    income_bands_ghs: Dict[int, str]


CODEMAP = CodeMap(
    country={1: "Nigeria", 2: "Ghana"},
    gender={1: "Male", 2: "Female", 3: "Other/Prefer not to say"},
    education={
        1: "No formal education",
        2: "Primary",
        3: "Secondary",
        4: "Vocational/Technical",
        5: "Undergraduate",
        6: "Postgraduate",
    },
    bank_type={
        1: "Traditional Commercial",
        2: "Digital-Only Bank",
        3: "Microfinance",
    },
    freq_use={
        1: "Daily",
        2: "Several times a week",
        3: "Weekly",
        4: "Monthly",
        5: "Less than monthly",
    },
    income_bands_ngn={
        1: "< ₦50k",
        2: "₦50k–₦100k",
        3: "₦100k–₦200k",
        4: "₦200k–₦400k",
        5: "₦400k–₦800k",
        6: "₦800k–₦1.5m",
        7: "> ₦1.5m",
    },
    income_bands_ghs={
        1: "< GH₵1k",
        2: "GH₵1k–GH₵2k",
        3: "GH₵2k–GH₵4k",
        4: "GH₵4k–GH₵7k",
        5: "GH₵7k–GH₵12k",
        6: "GH₵12k–GH₵20k",
        7: "> GH₵20k",
    },
)


def clipped_normal(mean: float, sd: float, size: int, lo: float, hi: float, rng: np.random.Generator) -> np.ndarray:
    x = rng.normal(mean, sd, size)
    return np.clip(x, lo, hi)


def softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


def sample_categorical(logits: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    # logits shape: (n, k)
    probs = softmax(logits)
    # cumulative for each row
    cum = probs.cumsum(axis=1)
    r = rng.random(size=probs.shape[0])[:, None]
    return (r > cum).sum(axis=1)


def generate_dataset(n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # Country distribution (slightly more Nigeria by population)
    country_probs = np.array([0.6, 0.4])
    country_idx = rng.choice([1, 2], size=n, p=country_probs)

    # Age (continuous): country- and education-sensitive; 18–70
    base_age_mean = np.where(country_idx == 1, 33.0, 35.0)
    base_age_sd = 10.0
    age = clipped_normal(base_age_mean, base_age_sd, n, lo=18, hi=70, rng=rng)
    age = np.round(age, 1)

    # Gender distribution with small Other proportion
    gender_probs = np.stack([
        np.full(n, 0.49),  # male
        np.full(n, 0.49),  # female
        np.full(n, 0.02),  # other
    ], axis=1)
    gender_draw = sample_categorical(np.log(gender_probs), rng) + 1  # 1..3

    # Education influenced by age (older cohorts slightly lower average education)
    # We'll compute logits for 6 categories using age
    edu_logits = np.zeros((n, 6))
    # Base intercepts roughly skewed to Secondary/Undergrad in urban samples
    base_intercepts = np.array([-1.8, -0.6, 0.6, 0.2, 0.4, -0.1])
    # Age effect: younger -> higher education odds up to age ~35; then flattens
    age_center = (age - 35.0) / 12.0
    edu_age_effect = np.stack([
        +0.1 * age_center,     # No formal slightly higher with age
        +0.05 * age_center,
        -0.10 * age_center,    # Secondary slightly younger
        -0.05 * age_center,
        -0.08 * age_center,    # Undergraduate more common younger cohorts
        -0.03 * age_center,    # Postgrad slightly younger
    ], axis=1)
    # Country effect: Ghana slightly higher tertiary attainment vs Nigeria in urban samples
    country_effect = np.where(country_idx == 2, 0.15, 0.0)
    edu_country = np.stack([
        -0.15 * (country_effect > 0),
        -0.10 * (country_effect > 0),
        +0.05 * (country_effect > 0),
        +0.05 * (country_effect > 0),
        +0.10 * (country_effect > 0),
        +0.05 * (country_effect > 0),
    ], axis=1)

    edu_logits = base_intercepts + edu_age_effect + edu_country
    edu_draw = sample_categorical(edu_logits, rng) + 1  # 1..6

    # Income level (1..7) influenced by education, age, and country
    # Create a score for income band selection
    edu_score = (edu_draw - 3) / 3.0  # centered around secondary-vocational
    age_score = (age - 30.0) / 15.0
    country_income_lift = np.where(country_idx == 1, 0.0, 0.1)  # Ghana bands differ but ordinal only

    inc_logits = np.zeros((n, 7))
    inc_base = np.array([-1.5, -0.5, 0.5, 0.8, 0.4, -0.1, -0.5])
    # Effects: higher edu -> higher bands; age modest effect
    inc_effect = np.stack([
        -0.3 * edu_score - 0.1 * age_score,
        -0.2 * edu_score - 0.05 * age_score,
        -0.1 * edu_score + 0.00 * age_score,
        +0.05 * edu_score + 0.05 * age_score,
        +0.12 * edu_score + 0.05 * age_score,
        +0.18 * edu_score + 0.03 * age_score,
        +0.25 * edu_score + 0.02 * age_score,
    ], axis=1)
    inc_country = np.stack([country_income_lift] * 7, axis=1)
    inc_logits = inc_base + inc_effect + 0.1 * inc_country
    inc_draw = sample_categorical(inc_logits, rng) + 1  # 1..7

    # Bank type influenced by age, education, income, and country
    # logits for 3 types
    bank_logits = np.zeros((n, 3))
    # Base preference leaning traditional
    bank_base = np.array([0.6, -0.2, -0.4])
    # Digital favored by younger and higher education; Microfinance favored by low income
    bank_age = (30.0 - age) / 15.0
    bank_edu = (edu_draw - 3) / 3.0
    bank_inc = (inc_draw - 4) / 3.0
    bank_country = np.where(country_idx == 1, 0.05, -0.05)  # Nigeria slightly more digital adoption
    bank_logits[:, 0] = bank_base[0] + (-0.2 * bank_age) + (-0.1 * bank_edu) + (-0.05 * bank_inc)
    bank_logits[:, 1] = bank_base[1] + (0.7 * bank_age) + (0.4 * bank_edu) + (0.1 * bank_inc) + (0.1 * bank_country)
    bank_logits[:, 2] = bank_base[2] + (-0.1 * bank_age) + (-0.2 * bank_edu) + (-0.3 * bank_inc)
    bank_draw = sample_categorical(bank_logits, rng) + 1  # 1..3

    # Years with account: constrained by age, newer accounts for digital-only
    # Minimum plausible account opening age ~ 15
    max_years = np.maximum(0, np.floor(age - 15)).astype(int)
    # Base years from a gamma-like distribution scaled to max_years
    base_years = np.minimum(max_years, (rng.gamma(shape=2.0, scale=3.0, size=n)).astype(int))
    # Adjust by bank type: digital-only newer, traditional older, microfinance moderate
    years_adjust = np.where(bank_draw == 2, -2, np.where(bank_draw == 1, +1, 0))
    years_with_acct = np.clip(base_years + years_adjust, 0, max_years)

    # Frequency of use (1..5): higher for digital-only and higher income; daily=1
    freq_logits = np.zeros((n, 5))
    freq_base = np.array([0.1, 0.2, 0.4, 0.2, 0.1])  # nominal prior leaning weekly/monthly
    # Convert base probs to logits
    freq_base_logits = np.log(freq_base)
    # Effects: digital, higher income -> more frequent (lower code)
    digital = (bank_draw == 2).astype(float)
    micro = (bank_draw == 3).astype(float)
    income_center = (inc_draw - 4) / 2.0
    # Build logits per category (1..5)
    for k in range(5):
        # lower k (more frequent) gets boost from digital & income; micro skews less frequent
        freq_logits[:, k] = (
            freq_base_logits[k]
            + (0.35 * digital * (2 - k))  # stronger toward daily/weekly
            + (0.15 * income_center * (2 - k))
            - (0.20 * micro * (k - 2))  # microfinance less frequent
        )
    freq_draw = sample_categorical(freq_logits, rng) + 1  # 1..5

    # Past victimization: base by country; adjusted by usage and tenure
    base_victim = np.where(country_idx == 1, -2.2, -2.4)  # ~10% vs ~8% base odds
    # More usage -> higher exposure; longer tenure -> more exposure; digital -> higher exposure
    exposure = (
        0.25 * (2 - (freq_draw - 3))  # daily=+0.5, weekly~0, less than monthly negative
        + 0.03 * np.clip(years_with_acct, 0, 25)
        + 0.25 * digital
        + 0.05 * bank_inc
    )
    victim_prob = 1.0 / (1.0 + np.exp(-(base_victim + exposure)))
    past_victim = (rng.random(n) < victim_prob).astype(int)

    # Assemble DataFrame
    df = pd.DataFrame(
        {
            "Country": country_idx,
            "Age": age,
            "Gender": gender_draw,
            "Education": edu_draw,
            "Income_Level": inc_draw,
            "Bank_Type": bank_draw,
            "Years_with_Account": years_with_acct,
            "Frequency_of_Use": freq_draw,
            "Past_Victim": past_victim,
        }
    )

    # Validations
    assert df["Country"].between(1, 2).all()
    assert df["Gender"].between(1, 3).all()
    assert df["Education"].between(1, 6).all()
    assert df["Income_Level"].between(1, 7).all()
    assert df["Bank_Type"].between(1, 3).all()
    assert df["Frequency_of_Use"].between(1, 5).all()
    assert df["Past_Victim"].isin([0, 1]).all()

    # Add label columns for readability (kept in export for convenience)
    df["Country_Label"] = df["Country"].map(CODEMAP.country)
    df["Gender_Label"] = df["Gender"].map(CODEMAP.gender)
    df["Education_Label"] = df["Education"].map(CODEMAP.education)
    df["Bank_Type_Label"] = df["Bank_Type"].map(CODEMAP.bank_type)
    df["Frequency_of_Use_Label"] = df["Frequency_of_Use"].map(CODEMAP.freq_use)

    # Income band label depends on country (local currency)
    income_label = []
    for c, lvl in zip(df["Country"].values, df["Income_Level"].values):
        if c == 1:
            income_label.append(CODEMAP.income_bands_ngn[lvl])
        else:
            income_label.append(CODEMAP.income_bands_ghs[lvl])
    df["Income_Band_Label"] = income_label

    return df


def write_dataset(df: pd.DataFrame, outdir: str, seed: int, n: int) -> Tuple[str, str]:
    os.makedirs(outdir, exist_ok=True)
    csv_path = os.path.join(outdir, "section_a_t1.csv")
    parquet_path = os.path.join(outdir, "section_a_t1.parquet")
    # Write CSV
    df.to_csv(csv_path, index=False)
    # Write Parquet if available
    try:
        df.to_parquet(parquet_path, index=False)
    except Exception:
        parquet_path = ""  # will be skipped in zipping
    return csv_path, parquet_path


def build_codebook(outdir: str) -> str:
    rows: List[Dict[str, str]] = []

    def codes_str(d: Dict[int, str]) -> str:
        return json.dumps({int(k): v for k, v in d.items()}, ensure_ascii=False)

    rows.append(
        {
            "variable": "Country",
            "label": "Country (1=Nigeria, 2=Ghana)",
            "type": "categorical:int",
            "codes": codes_str(CODEMAP.country),
            "allowed_range": "1..2",
            "notes": "Core variable for comparative analysis",
            "source_timepoint": "T1",
        }
    )
    rows.append(
        {
            "variable": "Age",
            "label": "Respondent age (years)",
            "type": "continuous:float",
            "codes": "{}",
            "allowed_range": "18..70",
            "notes": "Age truncated to [18,70]",
            "source_timepoint": "T1",
        }
    )
    rows.append(
        {
            "variable": "Gender",
            "label": "Gender (1=Male, 2=Female, 3=Other/Prefer not to say)",
            "type": "categorical:int",
            "codes": codes_str(CODEMAP.gender),
            "allowed_range": "1..3",
            "notes": "",
            "source_timepoint": "T1",
        }
    )
    rows.append(
        {
            "variable": "Education",
            "label": "Highest education (1=No formal to 6=Postgraduate)",
            "type": "ordinal:int",
            "codes": codes_str(CODEMAP.education),
            "allowed_range": "1..6",
            "notes": "",
            "source_timepoint": "T1",
        }
    )
    rows.append(
        {
            "variable": "Income_Level",
            "label": "Income band (local currency, ordinal)",
            "type": "ordinal:int",
            "codes": json.dumps(
                {
                    "NGN": {int(k): v for k, v in CODEMAP.income_bands_ngn.items()},
                    "GHS": {int(k): v for k, v in CODEMAP.income_bands_ghs.items()},
                },
                ensure_ascii=False,
            ),
            "allowed_range": "1..7",
            "notes": "Bands mapped by Country; see Income_Band_Label column",
            "source_timepoint": "T1",
        }
    )
    rows.append(
        {
            "variable": "Bank_Type",
            "label": "Primary bank type (1=Traditional, 2=Digital-Only, 3=Microfinance)",
            "type": "categorical:int",
            "codes": codes_str(CODEMAP.bank_type),
            "allowed_range": "1..3",
            "notes": "",
            "source_timepoint": "T1",
        }
    )
    rows.append(
        {
            "variable": "Years_with_Account",
            "label": "Years with primary bank account",
            "type": "discrete:int",
            "codes": "{}",
            "allowed_range": "0..55",
            "notes": "Constrained by Age-15 and bank type",
            "source_timepoint": "T1",
        }
    )
    rows.append(
        {
            "variable": "Frequency_of_Use",
            "label": "1=Daily to 5=Less than monthly",
            "type": "ordinal:int",
            "codes": codes_str(CODEMAP.freq_use),
            "allowed_range": "1..5",
            "notes": "Higher frequency associated with digital banks and higher income",
            "source_timepoint": "T1",
        }
    )
    rows.append(
        {
            "variable": "Past_Victim",
            "label": "Ever a victim of bank fraud? (1=Yes, 0=No)",
            "type": "binary:int",
            "codes": json.dumps({0: "No", 1: "Yes"}),
            "allowed_range": "0..1",
            "notes": "Probability increases with usage frequency, tenure, and digital banking",
            "source_timepoint": "T1",
        }
    )

    # Also include convenience label columns in codebook for completeness
    rows.extend(
        [
            {
                "variable": "Country_Label",
                "label": "Human-readable label for Country",
                "type": "string",
                "codes": codes_str(CODEMAP.country),
                "allowed_range": "",
                "notes": "Derived from Country",
                "source_timepoint": "T1",
            },
            {
                "variable": "Gender_Label",
                "label": "Human-readable label for Gender",
                "type": "string",
                "codes": codes_str(CODEMAP.gender),
                "allowed_range": "",
                "notes": "Derived from Gender",
                "source_timepoint": "T1",
            },
            {
                "variable": "Education_Label",
                "label": "Human-readable label for Education",
                "type": "string",
                "codes": codes_str(CODEMAP.education),
                "allowed_range": "",
                "notes": "Derived from Education",
                "source_timepoint": "T1",
            },
            {
                "variable": "Bank_Type_Label",
                "label": "Human-readable label for Bank_Type",
                "type": "string",
                "codes": codes_str(CODEMAP.bank_type),
                "allowed_range": "",
                "notes": "Derived from Bank_Type",
                "source_timepoint": "T1",
            },
            {
                "variable": "Frequency_of_Use_Label",
                "label": "Human-readable label for Frequency_of_Use",
                "type": "string",
                "codes": codes_str(CODEMAP.freq_use),
                "allowed_range": "",
                "notes": "Derived from Frequency_of_Use",
                "source_timepoint": "T1",
            },
            {
                "variable": "Income_Band_Label",
                "label": "Human-readable label for Income_Level in local currency",
                "type": "string",
                "codes": json.dumps(
                    {
                        "NGN": {int(k): v for k, v in CODEMAP.income_bands_ngn.items()},
                        "GHS": {int(k): v for k, v in CODEMAP.income_bands_ghs.items()},
                    },
                    ensure_ascii=False,
                ),
                "allowed_range": "",
                "notes": "Derived from Income_Level using Country",
                "source_timepoint": "T1",
            },
        ]
    )

    codebook = pd.DataFrame(rows)
    path = os.path.join(outdir, "section_a_t1_codebook.csv")
    codebook.to_csv(path, index=False)
    return path


def zip_outputs(outdir: str, files: List[str]) -> str:
    # Create a zip archive containing provided files
    import zipfile

    zip_path = os.path.join(outdir, "section_a_t1_dataset_v1.zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            if f and os.path.exists(f):
                arcname = os.path.basename(f)
                zf.write(f, arcname=arcname)
    return zip_path


def main():
    parser = argparse.ArgumentParser(description="Generate Section A (T1) synthetic dataset")
    parser.add_argument("--n", type=int, default=20000, help="Number of rows to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--outdir", type=str, default="./data", help="Output directory")

    args = parser.parse_args()

    df = generate_dataset(n=args.n, seed=args.seed)
    csv_path, parquet_path = write_dataset(df, args.outdir, seed=args.seed, n=args.n)
    codebook_path = build_codebook(args.outdir)
    zip_path = zip_outputs(args.outdir, [csv_path, parquet_path, codebook_path])

    print("Generated:")
    print(csv_path)
    if parquet_path:
        print(parquet_path)
    print(codebook_path)
    print(zip_path)


if __name__ == "__main__":
    main()
