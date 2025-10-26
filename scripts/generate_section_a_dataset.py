#!/usr/bin/env python3
"""
Synthetic dataset generator for:
Section A: Demographic and Control Variables (Measured at T1)

Columns produced (code + label pairs where applicable):
- respondent_id
- Country, Country_label (1=Nigeria, 2=Ghana)
- Age (integer)
- Gender, Gender_label (1=Male, 2=Female, 3=Other/Prefer not to say)
- Education, Education_label (1=No formal, 2=Primary, 3=Secondary, 4=Vocational/Technical, 5=Undergraduate, 6=Postgraduate)
- Income_Level, Income_Level_label (ordinal bands in local currency, country-specific labels)
- Bank_Type, Bank_Type_label (1=Traditional Commercial, 2=Digital-Only Bank, 3=Microfinance)
- Years_with_Account (integer)
- Frequency_of_Use, Frequency_of_Use_label (1=Daily, 2=Several times a week, 3=Weekly, 4=Monthly, 5=Less than monthly)
- Past_Victim, Past_Victim_label (1=Yes, 0=No)

Usage:
  python scripts/generate_section_a_dataset.py --rows 10000 --outdir data --seed 42
"""
from __future__ import annotations
import argparse
import csv
import os
import random
from datetime import datetime
from typing import Dict, Tuple


COUNTRIES = {1: "Nigeria", 2: "Ghana"}
GENDERS = {1: "Male", 2: "Female", 3: "Other/Prefer not to say"}
EDUCATION = {
    1: "No formal",
    2: "Primary",
    3: "Secondary",
    4: "Vocational/Technical",
    5: "Undergraduate",
    6: "Postgraduate",
}
BANK_TYPES = {
    1: "Traditional Commercial",
    2: "Digital-Only Bank",
    3: "Microfinance",
}
FREQ = {
    1: "Daily",
    2: "Several times a week",
    3: "Weekly",
    4: "Monthly",
    5: "Less than monthly",
}

# Country-specific income bands (ordinal 1..5)
INCOME_BANDS_LABELS = {
    1: [
        "<₦50,000",
        "₦50,000–₦100,000",
        "₦100,001–₦250,000",
        "₦250,001–₦500,000",
        ">₦500,000",
    ],
    2: [
        "<₵500",
        "₵500–₵1,000",
        "₵1,001–₵2,500",
        "₵2,501–₵5,000",
        ">₵5,000",
    ],
}


def clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(value, max_value))


def sample_country() -> int:
    # Slightly larger Nigerian sample by default
    return 1 if random.random() < 0.6 else 2


def sample_age(country: int) -> int:
    # Triangular distribution: min=18, mode ~30/32, max=75
    mode = 32 if country == 1 else 30
    age = int(round(random.triangular(18, 75, mode)))
    return clamp(age, 18, 75)


def sample_gender(country: int) -> int:
    # Balanced distribution with small probability for Other/Prefer not to say
    r = random.random()
    if r < 0.495:
        return 1
    elif r < 0.495 + 0.495:
        return 2
    else:
        return 3


def sample_education(age: int, country: int) -> int:
    # Education increases with age modestly; distribution skewed to Secondary/Undergrad
    base_probs = [0.03, 0.10, 0.38, 0.10, 0.28, 0.11]  # sums to 1.00
    # Adjust by age bands
    if age < 22:
        base_probs = [0.05, 0.15, 0.45, 0.12, 0.20, 0.03]
    elif age > 45:
        base_probs = [0.02, 0.08, 0.30, 0.10, 0.30, 0.20]
    # Country tweak: Ghana slightly higher vocational share
    if country == 2:
        base_probs[3] += 0.03
        base_probs[2] -= 0.02
        base_probs[4] -= 0.01
    # Sample 1..6 using cumulative
    r = random.random()
    cum = 0.0
    for i, p in enumerate(base_probs, start=1):
        cum += p
        if r <= cum:
            return i
    return 6


def sample_income_level(country: int, education: int) -> int:
    # Ordinal 1..5, higher education -> higher income tendency
    # Base probs for 1..5
    base = [0.15, 0.25, 0.30, 0.20, 0.10]
    # Education influence
    shift = (education - 3) * 0.03  # -0.06 .. +0.09
    # Apply simple shift to move mass from low to high or vice versa
    adj = [base[0] - shift, base[1] - shift/2, base[2], base[3] + shift/2, base[4] + shift]
    # Normalize and clip to be safe
    total = sum(max(0.0, x) for x in adj)
    probs = [max(0.0, x) / total for x in adj]
    r = random.random()
    cum = 0.0
    for i, p in enumerate(probs, start=1):
        cum += p
        if r <= cum:
            return i
    return 5


def sample_bank_type(country: int, age: int) -> int:
    # Younger users more likely digital; microfinance slightly higher in Nigeria
    r = random.random()
    if age < 30:
        # higher digital share
        probs = (0.55, 0.30, 0.15) if country == 1 else (0.50, 0.38, 0.12)
    elif age < 50:
        probs = (0.65, 0.22, 0.13) if country == 1 else (0.60, 0.28, 0.12)
    else:
        probs = (0.72, 0.15, 0.13) if country == 1 else (0.68, 0.20, 0.12)
    c1 = probs[0]
    c2 = c1 + probs[1]
    if r < c1:
        return 1
    elif r < c2:
        return 2
    else:
        return 3


def sample_years_with_account(age: int) -> int:
    # Earliest realistic account opening around 10-18; keep within age-10
    max_years = max(0, age - 10)
    if max_years == 0:
        return 0
    # Triangular with mode around 5-7 years, bounded [0, max_years]
    mode = min(7, max(3, max_years // 4))
    years = int(round(random.triangular(0, max_years, mode)))
    return clamp(years, 0, max_years)


def sample_frequency_of_use(bank_type: int, age: int) -> int:
    # Daily/Several times a week more common for digital and middle-age
    if bank_type == 2:  # digital
        probs = [0.35, 0.30, 0.18, 0.12, 0.05]
    elif bank_type == 1:  # traditional
        probs = [0.28, 0.30, 0.20, 0.15, 0.07]
    else:  # microfinance
        probs = [0.18, 0.27, 0.23, 0.20, 0.12]
    # Age adjustment: older -> slightly less frequent daily use
    if age > 55:
        probs = [probs[0] - 0.05, probs[1] + 0.01, probs[2] + 0.02, probs[3] + 0.01, probs[4] + 0.01]
    elif age < 25:
        probs = [probs[0] + 0.03, probs[1] + 0.02, probs[2], probs[3] - 0.03, probs[4] - 0.02]
    # Normalize
    total = sum(max(0.0, x) for x in probs)
    probs = [max(0.0, x) / total for x in probs]
    r = random.random()
    cum = 0.0
    for i, p in enumerate(probs, start=1):
        cum += p
        if r <= cum:
            return i
    return 5


def sample_past_victim(bank_type: int, freq: int, country: int) -> int:
    # Base rate ~12%; higher for digital and higher usage; small country tweaks
    base = 0.12
    if bank_type == 2:
        base += 0.03
    elif bank_type == 3:
        base -= 0.01
    # Frequency adjustment: daily -> +0.03, several/week +0.02, weekly +0.01
    freq_adj = {1: 0.03, 2: 0.02, 3: 0.01, 4: 0.0, 5: -0.01}
    base += freq_adj.get(freq, 0.0)
    # Country tweak
    if country == 1:
        base += 0.01
    p = min(max(base, 0.01), 0.40)
    return 1 if random.random() < p else 0


def record_for_row(respondent_id: int) -> Dict[str, object]:
    country = sample_country()
    age = sample_age(country)
    gender = sample_gender(country)
    education = sample_education(age, country)
    income = sample_income_level(country, education)
    bank_type = sample_bank_type(country, age)
    years_acct = sample_years_with_account(age)
    freq = sample_frequency_of_use(bank_type, age)
    victim = sample_past_victim(bank_type, freq, country)

    return {
        "respondent_id": respondent_id,
        "Country": country,
        "Country_label": COUNTRIES[country],
        "Age": age,
        "Gender": gender,
        "Gender_label": GENDERS[gender],
        "Education": education,
        "Education_label": EDUCATION[education],
        "Income_Level": income,
        "Income_Level_label": INCOME_BANDS_LABELS[country][income - 1],
        "Bank_Type": bank_type,
        "Bank_Type_label": BANK_TYPES[bank_type],
        "Years_with_Account": years_acct,
        "Frequency_of_Use": freq,
        "Frequency_of_Use_label": FREQ[freq],
        "Past_Victim": victim,
        "Past_Victim_label": "Yes" if victim == 1 else "No",
    }


def write_codebook(path: str) -> None:
    rows = [
        {
            "variable": "respondent_id",
            "type": "integer",
            "coding": "1..N",
            "description": "Unique respondent identifier",
        },
        {
            "variable": "Country",
            "type": "integer",
            "coding": "1=Nigeria, 2=Ghana",
            "description": "Country of residence",
        },
        {
            "variable": "Country_label",
            "type": "string",
            "coding": "Nigeria/Ghana",
            "description": "Human-readable country label",
        },
        {
            "variable": "Age",
            "type": "integer",
            "coding": "18..75",
            "description": "Age in years (approximate continuous)",
        },
        {
            "variable": "Gender",
            "type": "integer",
            "coding": "1=Male, 2=Female, 3=Other/Prefer not to say",
            "description": "Self-reported gender",
        },
        {
            "variable": "Gender_label",
            "type": "string",
            "coding": "Male/Female/Other/Prefer not to say",
            "description": "Human-readable gender label",
        },
        {
            "variable": "Education",
            "type": "integer",
            "coding": "1=No formal, 2=Primary, 3=Secondary, 4=Vocational/Technical, 5=Undergraduate, 6=Postgraduate",
            "description": "Highest educational attainment (ordinal)",
        },
        {
            "variable": "Education_label",
            "type": "string",
            "coding": "See Education codes",
            "description": "Human-readable education label",
        },
        {
            "variable": "Income_Level",
            "type": "integer",
            "coding": "1..5 (ordinal; country-specific band labels)",
            "description": "Household monthly income band",
        },
        {
            "variable": "Income_Level_label",
            "type": "string",
            "coding": "Nigeria: <₦50k, ₦50–100k, ₦100–250k, ₦250–500k, >₦500k; Ghana: analogous in GHS",
            "description": "Human-readable income band label",
        },
        {
            "variable": "Bank_Type",
            "type": "integer",
            "coding": "1=Traditional Commercial, 2=Digital-Only Bank, 3=Microfinance",
            "description": "Primary bank type used",
        },
        {
            "variable": "Bank_Type_label",
            "type": "string",
            "coding": "See Bank_Type codes",
            "description": "Human-readable bank type label",
        },
        {
            "variable": "Years_with_Account",
            "type": "integer",
            "coding": "0..(Age-10)",
            "description": "Years with primary bank account",
        },
        {
            "variable": "Frequency_of_Use",
            "type": "integer",
            "coding": "1=Daily, 2=Several times a week, 3=Weekly, 4=Monthly, 5=Less than monthly",
            "description": "Primary banking usage frequency",
        },
        {
            "variable": "Frequency_of_Use_label",
            "type": "string",
            "coding": "See Frequency_of_Use codes",
            "description": "Human-readable frequency label",
        },
        {
            "variable": "Past_Victim",
            "type": "integer",
            "coding": "1=Yes, 0=No",
            "description": "Ever a victim of bank fraud",
        },
        {
            "variable": "Past_Victim_label",
            "type": "string",
            "coding": "Yes/No",
            "description": "Human-readable victimization indicator",
        },
    ]
    fieldnames = ["variable", "type", "coding", "description"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate(rows: int, outdir: str, seed: int | None = None) -> Tuple[str, str]:
    if seed is not None:
        random.seed(seed)
    os.makedirs(outdir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    dataset_path = os.path.join(outdir, f"section_a_dataset_{ts}.csv")
    codebook_path = os.path.join(outdir, f"section_a_codebook_{ts}.csv")

    fieldnames = [
        "respondent_id",
        "Country",
        "Country_label",
        "Age",
        "Gender",
        "Gender_label",
        "Education",
        "Education_label",
        "Income_Level",
        "Income_Level_label",
        "Bank_Type",
        "Bank_Type_label",
        "Years_with_Account",
        "Frequency_of_Use",
        "Frequency_of_Use_label",
        "Past_Victim",
        "Past_Victim_label",
    ]

    with open(dataset_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(1, rows + 1):
            writer.writerow(record_for_row(i))

    write_codebook(codebook_path)
    return dataset_path, codebook_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic Section A dataset")
    parser.add_argument("--rows", type=int, default=10000, help="Number of rows to generate")
    parser.add_argument("--outdir", type=str, default="data", help="Output directory for CSV files")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    args = parser.parse_args()

    dataset_path, codebook_path = generate(args.rows, args.outdir, args.seed)
    print(dataset_path)
    print(codebook_path)


if __name__ == "__main__":
    main()
