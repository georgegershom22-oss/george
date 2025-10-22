#!/usr/bin/env python3
"""
Synthetic dataset generator for:
  Core Dataset 1: Primary Quantitative Survey (SME Innovation in Nigeria)

Generates a respondent-level dataset capturing firmographics, innovation adoption,
constraints, and performance outcomes with realistic correlations and Nigerian context.

Outputs:
- CSV dataset with item-level Likert responses and composite indices
- Variables dictionary CSV describing each variable

CLI:
  python scripts/generate_sme_innovation_dataset.py \
      --n 5000 \
      --seed 42 \
      --out-data data/core_dataset_sme_innovation.csv \
      --out-dict data/core_dataset_variables_dictionary.csv

This script uses numpy and pandas only.
"""
from __future__ import annotations

import argparse
import math
import os
import random
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Attempt lightweight imports and guide user if missing
try:
    import numpy as np
    import pandas as pd
except Exception as exc:  # pragma: no cover
    print(
        "This script requires numpy and pandas. Install with: pip install numpy pandas",
        file=sys.stderr,
    )
    raise


# -----------------------------
# Nigerian geography and sectors
# -----------------------------
@dataclass(frozen=True)
class StateInfo:
    state: str
    zone: str
    urban_bias: float  # probability of being urban if located here (relative, not absolute)


NIGERIA_STATES: List[StateInfo] = [
    StateInfo("Lagos", "South West", 0.92),
    StateInfo("Ogun", "South West", 0.64),
    StateInfo("Oyo", "South West", 0.66),
    StateInfo("Osun", "South West", 0.55),
    StateInfo("Ondo", "South West", 0.55),
    StateInfo("Ekiti", "South West", 0.52),
    StateInfo("Abuja FCT", "North Central", 0.90),
    StateInfo("Kwara", "North Central", 0.52),
    StateInfo("Kogi", "North Central", 0.45),
    StateInfo("Niger", "North Central", 0.44),
    StateInfo("Benue", "North Central", 0.42),
    StateInfo("Plateau", "North Central", 0.53),
    StateInfo("Kaduna", "North West", 0.58),
    StateInfo("Kano", "North West", 0.55),
    StateInfo("Katsina", "North West", 0.39),
    StateInfo("Kebbi", "North West", 0.35),
    StateInfo("Sokoto", "North West", 0.37),
    StateInfo("Jigawa", "North West", 0.32),
    StateInfo("Zamfara", "North West", 0.31),
    StateInfo("Borno", "North East", 0.42),
    StateInfo("Yobe", "North East", 0.35),
    StateInfo("Adamawa", "North East", 0.41),
    StateInfo("Taraba", "North East", 0.36),
    StateInfo("Gombe", "North East", 0.45),
    StateInfo("Bauchi", "North East", 0.40),
    StateInfo("Anambra", "South East", 0.68),
    StateInfo("Enugu", "South East", 0.69),
    StateInfo("Ebonyi", "South East", 0.46),
    StateInfo("Abia", "South East", 0.63),
    StateInfo("Imo", "South East", 0.61),
    StateInfo("Rivers", "South South", 0.75),
    StateInfo("Bayelsa", "South South", 0.54),
    StateInfo("Akwa Ibom", "South South", 0.58),
    StateInfo("Delta", "South South", 0.59),
    StateInfo("Cross River", "South South", 0.51),
    StateInfo("Edo", "South South", 0.62),
    StateInfo("Nasarawa", "North Central", 0.43),
    StateInfo("Benué", "North Central", 0.42),  # alias, keep both? we'll keep only Benue above
]
# Ensure uniqueness by state name
_seen = set()
NIGERIA_STATES = [s for s in NIGERIA_STATES if not (s.state in _seen or _seen.add(s.state))]

# Basic state sampling weights approximating population and SME density emphasis
STATE_WEIGHTS: Dict[str, float] = {
    "Lagos": 0.18,
    "Kano": 0.08,
    "Abuja FCT": 0.05,
    "Rivers": 0.05,
    "Kaduna": 0.04,
    "Oyo": 0.04,
    "Anambra": 0.035,
    "Ogun": 0.03,
    "Delta": 0.03,
    "Edo": 0.028,
    "Imo": 0.026,
    "Enugu": 0.024,
    # Others share remaining mass uniformly
}

# ISIC Rev.4 simplified mapping for major SME-relevant sectors
@dataclass(frozen=True)
class Sector:
    label: str
    isic_section: str  # e.g., C = Manufacturing, G = Wholesale/Retail, J = Information & Communication
    isic_2digit: str   # representative 2-digit code string
    weight: float      # sampling weight


SECTORS: List[Sector] = [
    Sector("Manufacturing", "C", "10", 0.20),  # Food products
    Sector("Retail & Wholesale", "G", "47", 0.28),
    Sector("IT & Professional Services", "J", "62", 0.10),
    Sector("Agriculture", "A", "01", 0.10),
    Sector("Hospitality & Food Services", "I", "56", 0.08),
    Sector("Construction", "F", "41", 0.06),
    Sector("Transport & Logistics", "H", "49", 0.06),
    Sector("Education & Health", "P/Q", "86", 0.06),
    Sector("Other Services", "S", "96", 0.06),
]


# -----------------------------
# Utilities
# -----------------------------
# Field of study options (module-level so both generator and dictionary can use it)
FIELD_OF_STUDY_OPTIONS: List[str] = [
    "Business/Management",
    "Engineering/Technology",
    "Sciences",
    "Arts/Social Sciences",
    "Agric/Environment",
    "Other",
]
FIELD_OF_STUDY_PROBS = np.array([0.28, 0.22, 0.12, 0.18, 0.10, 0.10])

def set_random_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def softclip(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    return np.minimum(np.maximum(x, lo), hi)


def likert_from_latent(latent: np.ndarray, thresholds: Optional[List[float]] = None) -> np.ndarray:
    """Map a latent normal to Likert 1-5 using thresholds.
    thresholds are z-score cut points between categories (4 thresholds).
    """
    if thresholds is None:
        thresholds = [-0.9, -0.2, 0.4, 1.2]
    bins = np.digitize(latent, thresholds) + 1
    return bins.astype(int)


def sample_states(n: int) -> Tuple[np.ndarray, np.ndarray]:
    states = [s.state for s in NIGERIA_STATES]
    zones = {s.state: s.zone for s in NIGERIA_STATES}

    # Build sampling weights vector
    base_w = np.array([STATE_WEIGHTS.get(s, None) for s in states], dtype=float)
    remaining = 1.0 - np.nansum(base_w)
    # assign uniform weight to unspecified states
    mask = np.isnan(base_w)
    if mask.any():
        base_w[mask] = remaining / mask.sum()
    base_w = base_w / base_w.sum()

    sampled_states = np.random.choice(states, size=n, p=base_w)
    sampled_zones = np.array([zones[s] for s in sampled_states])
    return sampled_states, sampled_zones


def sample_urban(n: int, states: np.ndarray, base_urban_rate: float = 0.64) -> np.ndarray:
    # Urban probability modulated by state's urban_bias
    bias_map = {s.state: s.urban_bias for s in NIGERIA_STATES}
    probs = np.array([softclip(np.array([base_urban_rate * bias_map.get(st, 0.55)]), 0.2, 0.97)[0] for st in states])
    return (np.random.rand(n) < probs).astype(int)


def sample_sector(n: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    labels = [s.label for s in SECTORS]
    weights = np.array([s.weight for s in SECTORS], dtype=float)
    weights = weights / weights.sum()
    idx = np.random.choice(len(SECTORS), size=n, p=weights)
    labels_arr = np.array([SECTORS[i].label for i in idx])
    sections_arr = np.array([SECTORS[i].isic_section for i in idx])
    code_arr = np.array([SECTORS[i].isic_2digit for i in idx])
    return labels_arr, sections_arr, code_arr


def sample_legal_structure(n: int) -> np.ndarray:
    choices = [
        ("Sole Proprietorship", 0.58),
        ("Partnership", 0.16),
        ("Limited Liability", 0.24),
        ("Cooperative/Other", 0.02),
    ]
    labels, probs = zip(*choices)
    return np.random.choice(labels, size=n, p=np.array(probs))


def truncated_normal(mean: float, sd: float, lo: float, hi: float, size: int) -> np.ndarray:
    x = np.random.normal(mean, sd, size)
    return softclip(x, lo, hi)


def generate_firmographics(n: int, seed: int) -> Dict[str, np.ndarray]:
    set_random_seed(seed)
    states, zones = sample_states(n)
    urban = sample_urban(n, states)
    sector_label, isic_section, isic_2digit = sample_sector(n)

    # Firm age (years): skew to younger firms
    firm_age = np.round(truncated_normal(mean=8.5, sd=6.0, lo=0.5, hi=40.0, size=n)).astype(int)

    # Employees: micro predominance with long tail
    # Use a zero-inflated lognormal-like approach mapped to 1-200
    size_latent = np.random.lognormal(mean=1.6, sigma=0.8, size=n)  # median ~5
    employees = np.clip(np.round(size_latent + 1).astype(int), 1, 200)

    # Annual turnover (NGN): lognormal tied to employees and sector
    sector_turnover_multiplier = {
        "Manufacturing": 1.4,
        "Retail & Wholesale": 1.0,
        "IT & Professional Services": 1.3,
        "Agriculture": 0.9,
        "Hospitality & Food Services": 0.95,
        "Construction": 1.2,
        "Transport & Logistics": 1.1,
        "Education & Health": 0.9,
        "Other Services": 0.8,
    }
    base_log_turnover = (
        np.log(np.maximum(employees, 1))
        + np.array([math.log(sector_turnover_multiplier[s]) for s in sector_label])
        + np.random.normal(14.0, 0.6, size=n)  # around exp(14) ~ 1.2M; scaled by employees
    )
    annual_turnover = np.exp(base_log_turnover)

    # Legal structure
    legal_structure = sample_legal_structure(n)

    # Owner/Manager demographics
    owner_age = np.clip(np.round(np.random.normal(39, 9, size=n)).astype(int), 18, 70)
    gender = np.random.choice(["Male", "Female"], size=n, p=[0.62, 0.38])
    education_levels = [
        ("Primary", 0.06),
        ("Secondary", 0.32),
        ("Tertiary", 0.46),
        ("Postgraduate", 0.16),
    ]
    edu_labels, edu_probs = zip(*education_levels)
    education = np.random.choice(edu_labels, size=n, p=np.array(edu_probs))

    field_of_study = np.random.choice(FIELD_OF_STUDY_OPTIONS, size=n, p=FIELD_OF_STUDY_PROBS)

    prior_entre_exp = np.random.choice([0, 1], size=n, p=[0.45, 0.55])

    # Digital literacy 0-100: higher for tertiary/postgrad, lower with age, higher urban
    edu_score_map = {"Primary": 32, "Secondary": 48, "Tertiary": 68, "Postgraduate": 78}
    base_dl = np.array([edu_score_map[e] for e in education])
    dl = base_dl + 6 * urban - 0.25 * (owner_age - 35) + np.random.normal(0, 8, size=n)
    dl = softclip(dl, 5, 100)

    # Firm IDs
    firm_id = np.array([f"F{seed:02d}{i:06d}" for i in range(n)])

    # Urban/Rural as labels
    urban_rural = np.where(urban == 1, "Urban", "Rural")

    return {
        "firm_id": firm_id,
        "state": states,
        "geo_zone": zones,
        "location_type": urban_rural,
        "sector": sector_label,
        "isic_section": isic_section,
        "isic_2digit": isic_2digit,
        "firm_age_years": firm_age,
        "employees_full_time": employees,
        "annual_turnover_naira": annual_turnover,
        "legal_structure": legal_structure,
        "owner_age": owner_age,
        "owner_gender": gender,
        "owner_education": education,
        "owner_field_of_study": field_of_study,
        "owner_prior_entre_experience": prior_entre_exp,
        "owner_digital_literacy_0_100": dl,
    }


# -----------------------------
# Latent constructs and items
# -----------------------------
@dataclass
class LatentConstructs:
    # Innovation drivers
    competition_pressure: np.ndarray
    customer_demand_for_innovation: np.ndarray
    top_mgmt_attitude: np.ndarray

    # Innovation adoption
    digital_tools_adoption: np.ndarray
    advanced_tech_adoption: np.ndarray
    process_innovation: np.ndarray
    product_innovation: np.ndarray
    business_model_innovation: np.ndarray
    level_of_digitization: np.ndarray

    # Constraints
    financial_constraints: np.ndarray
    human_capital_constraints: np.ndarray
    infrastructure_constraints: np.ndarray
    regulatory_constraints: np.ndarray
    market_constraints: np.ndarray

    # Performance (latent for subjective items)
    perf_profitability_growth: np.ndarray
    perf_sales_growth: np.ndarray
    perf_market_share_growth: np.ndarray
    perf_roi: np.ndarray
    perf_overall_satisfaction: np.ndarray


@dataclass
class ObjectivePerformance:
    annual_turnover_naira: np.ndarray
    profit_naira: np.ndarray
    turnover_band: np.ndarray
    profit_band: np.ndarray
    employee_growth_rate_pct: np.ndarray
    num_new_branches_clients: np.ndarray
    non_financial_new_lines: np.ndarray
    non_financial_quality_improved: np.ndarray
    non_financial_customer_satisfaction: np.ndarray


TURNOVER_BANDS = [
    ("< ₦1m", 0, 1e6),
    ("₦1m–₦5m", 1e6, 5e6),
    ("₦5m–₦20m", 5e6, 2e7),
    ("₦20m–₦100m", 2e7, 1e8),
    ("> ₦100m", 1e8, float("inf")),
]

PROFIT_BANDS = [
    ("Loss/Break-even", -float("inf"), 5e5),
    ("₦0.5m–₦2m", 5e5, 2e6),
    ("₦2m–₦10m", 2e6, 1e7),
    ("₦10m–₦50m", 1e7, 5e7),
    ("> ₦50m", 5e7, float("inf")),
]


def to_band(values: np.ndarray, bands: List[Tuple[str, float, float]]) -> np.ndarray:
    labels = []
    for v in values:
        label = bands[-1][0]
        for name, lo, hi in bands:
            if lo <= v < hi:
                label = name
                break
        labels.append(label)
    return np.array(labels)


def compute_latents(F: Dict[str, np.ndarray], seed: int) -> LatentConstructs:
    n = len(next(iter(F.values())))
    rng = np.random.default_rng(seed + 101)

    # Convenience vectors
    urban = (F["location_type"] == "Urban").astype(int)
    size_log = np.log(F["employees_full_time"] + 0.1)
    dl = F["owner_digital_literacy_0_100"] / 100.0

    # Sector effects
    sec = F["sector"]
    is_it = (sec == "IT & Professional Services").astype(float)
    is_manu = (sec == "Manufacturing").astype(float)
    is_retail = (sec == "Retail & Wholesale").astype(float)

    # Zone infrastructure baseline (South West/South South better infra; North East/West lower)
    zone = F["geo_zone"]
    zone_infra_baseline = (
        0.15 * (zone == "South West").astype(float)
        + 0.10 * (zone == "South South").astype(float)
        + 0.05 * (zone == "South East").astype(float)
        - 0.10 * (zone == "North West").astype(float)
        - 0.12 * (zone == "North East").astype(float)
    )

    # Innovation drivers (Likert-oriented latent ~ N(0,1))
    competition_pressure = rng.normal(0, 1, n) + 0.25 * is_retail + 0.15 * urban
    customer_demand = rng.normal(0, 1, n) + 0.20 * is_retail + 0.20 * urban
    top_mgmt = rng.normal(0, 1, n) + 0.40 * dl + 0.15 * (F["owner_prior_entre_experience"]).astype(float)

    # Innovation adoption latents
    digital_tools = (
        rng.normal(0, 1, n)
        + 0.65 * dl
        + 0.25 * urban
        + 0.20 * is_it
        + 0.10 * np.log1p(F["firm_age_years"])  # time to adopt basics
    )

    level_digitization = (
        rng.normal(0, 1, n)
        + 0.60 * dl
        + 0.25 * urban
        + 0.20 * is_it
        + 0.12 * size_log
    )

    advanced_tech = (
        rng.normal(0, 1, n)
        + 0.45 * level_digitization
        + 0.20 * is_it
        + 0.18 * is_manu
        + 0.12 * size_log
        - 0.10 * (F["owner_age"] > 50).astype(float)
    )

    process_innov = (
        rng.normal(0, 1, n)
        + 0.35 * digital_tools
        + 0.25 * level_digitization
        + 0.15 * competition_pressure
        + 0.10 * top_mgmt
    )

    product_innov = (
        rng.normal(0, 1, n)
        + 0.20 * advanced_tech
        + 0.25 * customer_demand
        + 0.15 * competition_pressure
        + 0.12 * top_mgmt
        + 0.10 * is_manu
    )

    biz_model_innov = (
        rng.normal(0, 1, n)
        + 0.30 * level_digitization
        + 0.25 * top_mgmt
        + 0.18 * customer_demand
    )

    # Constraints latents
    financial_constraints = (
        rng.normal(0, 1, n)
        + 0.25 * (F["legal_structure"] == "Sole Proprietorship").astype(float)
        - 0.20 * size_log
        + 0.10 * (F["owner_education"] == "Primary").astype(float)
    )

    human_constraints = (
        rng.normal(0, 1, n)
        + 0.25 * (1 - dl)
        + 0.15 * (1 - urban)
        + 0.15 * is_it  # IT firms report skill gaps
    )

    infra_constraints = rng.normal(0, 1, n) + (-0.60 * zone_infra_baseline) + 0.20 * (1 - urban)
    regulatory_constraints = rng.normal(0, 1, n) + 0.10 * is_retail + 0.10 * is_manu
    market_constraints = rng.normal(0, 1, n) + 0.30 * (1 - urban) + 0.20 * (1 - is_retail)

    # Performance latents (subjective) with moderation by constraints
    # Base economic scale ~ turnover and size
    econ_scale = 0.35 * np.log1p(F["annual_turnover_naira"]) + 0.25 * size_log

    # Innovation composite
    innov_composite = 0.25 * digital_tools + 0.25 * level_digitization + 0.25 * process_innov + 0.25 * product_innov

    # Constraints composite (higher = more constrained)
    constr_composite = 0.25 * financial_constraints + 0.20 * human_constraints + 0.30 * infra_constraints + 0.15 * regulatory_constraints + 0.10 * market_constraints

    interaction = 0.35 * innov_composite - 0.25 * constr_composite - 0.15 * innov_composite * softclip(constr_composite, -1.0, 2.0)

    base_perf = 0.30 * econ_scale + interaction

    perf_profit = rng.normal(0, 1, n) + base_perf
    perf_sales = rng.normal(0, 1, n) + base_perf + 0.10 * customer_demand
    perf_share = rng.normal(0, 1, n) + 0.85 * base_perf + 0.15 * competition_pressure
    perf_roi = rng.normal(0, 1, n) + base_perf
    perf_satisfaction = rng.normal(0, 1, n) + 0.8 * base_perf + 0.2 * top_mgmt

    return LatentConstructs(
        competition_pressure=competition_pressure,
        customer_demand_for_innovation=customer_demand,
        top_mgmt_attitude=top_mgmt,
        digital_tools_adoption=digital_tools,
        advanced_tech_adoption=advanced_tech,
        process_innovation=process_innov,
        product_innovation=product_innov,
        business_model_innovation=biz_model_innov,
        level_of_digitization=level_digitization,
        financial_constraints=financial_constraints,
        human_capital_constraints=human_constraints,
        infrastructure_constraints=infra_constraints,
        regulatory_constraints=regulatory_constraints,
        market_constraints=market_constraints,
        perf_profitability_growth=perf_profit,
        perf_sales_growth=perf_sales,
        perf_market_share_growth=perf_share,
        perf_roi=perf_roi,
        perf_overall_satisfaction=perf_satisfaction,
    )


def generate_items_from_latent(latent: np.ndarray, item_loadings: List[float], noise_sd: float = 0.8) -> np.ndarray:
    n = latent.shape[0]
    items = []
    for loading in item_loadings:
        x = loading * latent + np.random.normal(0, noise_sd, n)
        items.append(likert_from_latent(x))
    return np.vstack(items).T  # shape (n, k)


def compute_objective_performance(F: Dict[str, np.ndarray], L: LatentConstructs, seed: int) -> ObjectivePerformance:
    n = len(F["firm_id"])
    rng = np.random.default_rng(seed + 303)

    turnover = F["annual_turnover_naira"].copy().astype(float)

    # Profit margin influenced by innovation and constraints and sector
    sec = F["sector"]
    sector_margin = (
        0.08 * (sec == "Retail & Wholesale").astype(float)
        + 0.15 * (sec == "IT & Professional Services").astype(float)
        + 0.10 * (sec == "Manufacturing").astype(float)
        + 0.07 * (sec == "Hospitality & Food Services").astype(float)
        + 0.06 * (sec == "Transport & Logistics").astype(float)
        + 0.05 * (sec == "Agriculture").astype(float)
        + 0.04 * (sec == "Other Services").astype(float)
    )

    innov_effect = 0.02 * (L.level_of_digitization + L.process_innovation + L.product_innovation)
    constr_effect = -0.02 * (
        L.financial_constraints + L.human_capital_constraints + L.infrastructure_constraints
    )

    base_margin = 0.10 + sector_margin + 0.01 * np.log1p(F["employees_full_time"]) + 0.01 * (F["location_type"] == "Urban").astype(float)
    margin = softclip(base_margin + innov_effect + constr_effect + rng.normal(0, 0.02, n), 0.00, 0.45)

    profit = margin * turnover

    # Employee growth rate
    growth_rate = (
        rng.normal(0.05, 0.08, n)
        + 0.01 * L.product_innovation
        + 0.01 * L.process_innovation
        + 0.008 * L.level_of_digitization
        - 0.008 * (L.financial_constraints + L.infrastructure_constraints)
    )
    growth_rate = softclip(growth_rate, -0.20, 0.60) * 100.0

    # New branches/clients as count
    lambda_base = 0.5 + 0.3 * np.exp(0.4 * L.product_innovation) / (1 + np.exp(0.4 * L.product_innovation))
    lambda_base += 0.2 * (F["location_type"] == "Urban").astype(float)
    lambda_base += 0.2 * np.log1p(F["employees_full_time"]) / 3.0
    lambda_base = np.clip(lambda_base, 0.05, 5.0)
    new_clients = rng.poisson(lam=lambda_base)

    # Non-financial indicators as Likert via latent
    nf_lines = likert_from_latent(L.product_innovation + rng.normal(0, 0.8, n))
    nf_quality = likert_from_latent(0.6 * L.process_innovation + 0.3 * L.product_innovation + rng.normal(0, 0.8, n))
    nf_csat = likert_from_latent(0.5 * L.business_model_innovation + 0.3 * L.product_innovation + rng.normal(0, 0.8, n))

    # Bands
    turnover_band = to_band(turnover, TURNOVER_BANDS)
    profit_band = to_band(profit, PROFIT_BANDS)

    # Introduce some missingness for objective metrics (low response)
    miss_mask = rng.random(n) < 0.12  # 12% missing blockwise
    turnover_m = turnover.copy()
    profit_m = profit.copy()
    turnover_m[miss_mask] = np.nan
    profit_m[miss_mask] = np.nan

    return ObjectivePerformance(
        annual_turnover_naira=turnover_m,
        profit_naira=profit_m,
        turnover_band=turnover_band,
        profit_band=profit_band,
        employee_growth_rate_pct=growth_rate,
        num_new_branches_clients=new_clients,
        non_financial_new_lines=nf_lines,
        non_financial_quality_improved=nf_quality,
        non_financial_customer_satisfaction=nf_csat,
    )


def build_dataset(n: int, seed: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Section A
    F = generate_firmographics(n, seed)

    # Latents
    L = compute_latents(F, seed)

    # Section B items
    # Digital tools: computers, accounting, CRM, e-commerce, cloud, social media (6)
    B_digital_tools = generate_items_from_latent(L.digital_tools_adoption, [0.9, 0.8, 0.7, 0.7, 0.6, 0.7])

    # Advanced tech: AI/ML, IoT, blockchain, robotics (4) – rarer: skew thresholds up
    adv_noise = L.advanced_tech_adoption + np.random.normal(0, 1.0, n)
    B_adv = np.vstack([
        likert_from_latent(adv_noise - 0.4),
        likert_from_latent(adv_noise - 0.2),
        likert_from_latent(adv_noise - 0.6),
        likert_from_latent(adv_noise - 0.8),
    ]).T

    # Process innovation: production/delivery, supply chain SW, support techniques (accounting, HR) (3)
    B_process = generate_items_from_latent(L.process_innovation, [0.8, 0.8, 0.7])

    # Product/service innovation: new/improved goods/services, frequency of launches (2)
    B_product = generate_items_from_latent(L.product_innovation, [0.85, 0.80])

    # Business model innovation: revenue models, value proposition, customer engagement (3)
    B_bmi = generate_items_from_latent(L.business_model_innovation, [0.8, 0.75, 0.7])

    # Drivers: competition, customer demand, top mgmt attitude (3)
    B_drivers = np.vstack([
        likert_from_latent(L.competition_pressure),
        likert_from_latent(L.customer_demand_for_innovation),
        likert_from_latent(L.top_mgmt_attitude),
    ]).T

    # Composite indices (1-5 and 0-100 scaled where relevant)
    comp_digital_tools = B_digital_tools.mean(axis=1)
    comp_adv = B_adv.mean(axis=1)
    comp_process = B_process.mean(axis=1)
    comp_product = B_product.mean(axis=1)
    comp_bmi = B_bmi.mean(axis=1)
    comp_level_digitization = likert_from_latent(L.level_of_digitization).astype(float)
    comp_level_digitization_score_0_100 = ((comp_level_digitization - 1) / 4.0) * 100.0

    # Section C: Constraints items
    C_financial = generate_items_from_latent(L.financial_constraints, [0.8, 0.8, 0.75])
    C_human = generate_items_from_latent(L.human_capital_constraints, [0.8, 0.8, 0.75])
    C_infra = generate_items_from_latent(L.infrastructure_constraints, [0.85, 0.8, 0.75])
    C_reg = generate_items_from_latent(L.regulatory_constraints, [0.7, 0.7, 0.65])
    C_market = generate_items_from_latent(L.market_constraints, [0.75, 0.7, 0.65])

    # Section D: Subjective performance items
    D_subj = np.vstack([
        likert_from_latent(L.perf_profitability_growth),
        likert_from_latent(L.perf_sales_growth),
        likert_from_latent(L.perf_market_share_growth),
        likert_from_latent(L.perf_roi),
        likert_from_latent(L.perf_overall_satisfaction),
    ]).T
    comp_perf_subjective = D_subj.mean(axis=1)

    # Objective performance
    OP = compute_objective_performance(F, L, seed)

    # Build DataFrame
    df = pd.DataFrame({k: v for k, v in F.items()})

    # Section B columns
    B_cols = {
        "B1_digital_tools_computers": B_digital_tools[:, 0],
        "B1_digital_tools_accounting_software": B_digital_tools[:, 1],
        "B1_digital_tools_crm": B_digital_tools[:, 2],
        "B1_digital_tools_ecommerce": B_digital_tools[:, 3],
        "B1_digital_tools_cloud": B_digital_tools[:, 4],
        "B1_digital_tools_social_media": B_digital_tools[:, 5],
        "B2_advanced_ai_ml": B_adv[:, 0],
        "B2_advanced_iot": B_adv[:, 1],
        "B2_advanced_blockchain": B_adv[:, 2],
        "B2_advanced_robotics": B_adv[:, 3],
        "B3_process_new_methods": B_process[:, 0],
        "B3_process_supply_chain_software": B_process[:, 1],
        "B3_process_support_techniques": B_process[:, 2],
        "B4_product_new_or_improved": B_product[:, 0],
        "B4_product_launch_frequency": B_product[:, 1],
        "B5_bmi_revenue_model_changes": B_bmi[:, 0],
        "B5_bmi_value_prop_changes": B_bmi[:, 1],
        "B5_bmi_customer_engagement_changes": B_bmi[:, 2],
        "B6_drivers_competitive_pressure": B_drivers[:, 0],
        "B6_drivers_customer_demand": B_drivers[:, 1],
        "B6_drivers_top_mgmt_attitude": B_drivers[:, 2],
    }

    for k, v in B_cols.items():
        df[k] = v.astype(int)

    # Composite indices
    df["B_comp_digital_tools_mean_1_5"] = comp_digital_tools
    df["B_comp_advanced_tech_mean_1_5"] = comp_adv
    df["B_comp_process_innovation_mean_1_5"] = comp_process
    df["B_comp_product_innovation_mean_1_5"] = comp_product
    df["B_comp_bmi_mean_1_5"] = comp_bmi
    df["B_comp_level_digitization_1_5"] = comp_level_digitization
    df["B_comp_level_digitization_score_0_100"] = comp_level_digitization_score_0_100

    # Section C columns
    C_cols = {
        "C1_financial_access_to_credit": C_financial[:, 0],
        "C1_financial_cost_of_innovation": C_financial[:, 1],
        "C1_financial_internal_capital_sufficiency": C_financial[:, 2],
        "C2_human_skill_shortage": C_human[:, 0],
        "C2_human_training_cost": C_human[:, 1],
        "C2_human_mgmt_capability_for_change": C_human[:, 2],
        "C3_infra_power_reliability": C_infra[:, 0],
        "C3_infra_internet_quality_cost": C_infra[:, 1],
        "C3_infra_logistics_access": C_infra[:, 2],
        "C4_regulatory_burden_taxes": C_reg[:, 0],
        "C4_regulatory_corruption_informal_charges": C_reg[:, 1],
        "C4_regulatory_govt_program_effectiveness": C_reg[:, 2],
        "C5_market_competition_intensity": C_market[:, 0],
        "C5_market_demand_uncertainty": C_market[:, 1],
        "C5_market_international_access": C_market[:, 2],
    }
    for k, v in C_cols.items():
        df[k] = v.astype(int)

    # Section D subjective
    df["D1_subj_profitability_growth"] = D_subj[:, 0].astype(int)
    df["D1_subj_sales_growth"] = D_subj[:, 1].astype(int)
    df["D1_subj_market_share_growth"] = D_subj[:, 2].astype(int)
    df["D1_subj_roi"] = D_subj[:, 3].astype(int)
    df["D1_subj_overall_perf_satisfaction"] = D_subj[:, 4].astype(int)
    df["D_comp_subjective_performance_mean_1_5"] = comp_perf_subjective

    # Objective performance
    df["D2_obj_annual_turnover_naira"] = OP.annual_turnover_naira
    df["D2_obj_profit_naira"] = OP.profit_naira
    df["D2_obj_turnover_band"] = OP.turnover_band
    df["D2_obj_profit_band"] = OP.profit_band
    df["D2_obj_employee_growth_rate_pct"] = OP.employee_growth_rate_pct
    df["D2_obj_num_new_branches_clients"] = OP.num_new_branches_clients

    # Non-financial
    df["D3_nonfin_increase_product_lines"] = OP.non_financial_new_lines.astype(int)
    df["D3_nonfin_quality_improved"] = OP.non_financial_quality_improved.astype(int)
    df["D3_nonfin_customer_satisfaction_retention"] = OP.non_financial_customer_satisfaction.astype(int)

    # Re-order columns roughly by section
    base_cols = [
        "firm_id",
        "state",
        "geo_zone",
        "location_type",
        "sector",
        "isic_section",
        "isic_2digit",
        "firm_age_years",
        "employees_full_time",
        "annual_turnover_naira",
        "legal_structure",
        "owner_age",
        "owner_gender",
        "owner_education",
        "owner_field_of_study",
        "owner_prior_entre_experience",
        "owner_digital_literacy_0_100",
    ]

    df = df[
        base_cols
        + list(B_cols.keys())
        + [
            "B_comp_digital_tools_mean_1_5",
            "B_comp_advanced_tech_mean_1_5",
            "B_comp_process_innovation_mean_1_5",
            "B_comp_product_innovation_mean_1_5",
            "B_comp_bmi_mean_1_5",
            "B_comp_level_digitization_1_5",
            "B_comp_level_digitization_score_0_100",
        ]
        + list(C_cols.keys())
        + [
            "D1_subj_profitability_growth",
            "D1_subj_sales_growth",
            "D1_subj_market_share_growth",
            "D1_subj_roi",
            "D1_subj_overall_perf_satisfaction",
            "D_comp_subjective_performance_mean_1_5",
        ]
        + [
            "D2_obj_annual_turnover_naira",
            "D2_obj_profit_naira",
            "D2_obj_turnover_band",
            "D2_obj_profit_band",
            "D2_obj_employee_growth_rate_pct",
            "D2_obj_num_new_branches_clients",
        ]
        + [
            "D3_nonfin_increase_product_lines",
            "D3_nonfin_quality_improved",
            "D3_nonfin_customer_satisfaction_retention",
        ]
    ]

    # Variables dictionary
    dict_rows: List[Dict[str, str]] = []

    def add_dict(var: str, label: str, section: str, vtype: str, scale: str, values: str, notes: str = "") -> None:
        dict_rows.append(
            {
                "variable": var,
                "label": label,
                "section": section,
                "type": vtype,
                "scale": scale,
                "values": values,
                "notes": notes,
            }
        )

    # Section A dict
    add_dict("firm_id", "Firm ID (anonymized)", "A", "string", "id", "e.g., F42000001")
    add_dict("state", "Location: State", "A", "categorical", "nominal", ", ".join(sorted({s.state for s in NIGERIA_STATES})))
    add_dict("geo_zone", "Geo-political zone", "A", "categorical", "nominal", "North Central, North East, North West, South East, South South, South West")
    add_dict("location_type", "Location type", "A", "categorical", "binary", "Urban, Rural")
    add_dict("sector", "Industry/Sector (label)", "A", "categorical", "nominal", ", ".join([s.label for s in SECTORS]))
    add_dict("isic_section", "ISIC section code", "A", "categorical", "nominal", "A, C, F, G, H, I, J, P/Q, S")
    add_dict("isic_2digit", "ISIC representative 2-digit code", "A", "string", "code", "E.g., 10=Food, 47=Retail, 62=IT")
    add_dict("firm_age_years", "Firm age (years of operation)", "A", "integer", "ratio", ">=0")
    add_dict("employees_full_time", "Full-time employees", "A", "integer", "ratio", "1-200 typical")
    add_dict("annual_turnover_naira", "Annual turnover (NGN)", "A", "numeric", "ratio", "Continuous, may be missing")
    add_dict("legal_structure", "Legal structure", "A", "categorical", "nominal", "Sole Proprietorship, Partnership, Limited Liability, Cooperative/Other")
    add_dict("owner_age", "Owner/Manager age", "A", "integer", "ratio", "18-70 customary")
    add_dict("owner_gender", "Owner/Manager gender", "A", "categorical", "nominal", "Male, Female")
    add_dict("owner_education", "Owner/Manager education", "A", "categorical", "ordinal", "Primary < Secondary < Tertiary < Postgraduate")
    add_dict("owner_field_of_study", "Field of study", "A", "categorical", "nominal", ", ".join(FIELD_OF_STUDY_OPTIONS))
    add_dict("owner_prior_entre_experience", "Prior entrepreneurial experience", "A", "binary", "0/1", "1 = Yes")
    add_dict("owner_digital_literacy_0_100", "Digital literacy score (0-100)", "A", "numeric", "index", "Higher is better")

    # Section B dict (items)
    B_labels = [
        ("B1_digital_tools_computers", "Extent of use: computers"),
        ("B1_digital_tools_accounting_software", "Extent of use: accounting software"),
        ("B1_digital_tools_crm", "Extent of use: CRM"),
        ("B1_digital_tools_ecommerce", "Extent of use: e-commerce platforms"),
        ("B1_digital_tools_cloud", "Extent of use: cloud"),
        ("B1_digital_tools_social_media", "Extent of use: social media for business"),
        ("B2_advanced_ai_ml", "Use of AI/ML for analytics"),
        ("B2_advanced_iot", "Use of IoT in operations"),
        ("B2_advanced_blockchain", "Use of blockchain"),
        ("B2_advanced_robotics", "Use of robotics"),
        ("B3_process_new_methods", "Adoption of new production/delivery methods"),
        ("B3_process_supply_chain_software", "Implementation of supply chain/logistics software"),
        ("B3_process_support_techniques", "Use of new supporting techniques (accounting, HR)"),
        ("B4_product_new_or_improved", "New or significantly improved goods/services (last 3 years)"),
        ("B4_product_launch_frequency", "Frequency of new product launches"),
        ("B5_bmi_revenue_model_changes", "Changes in revenue models (subscription, freemium, etc.)"),
        ("B5_bmi_value_prop_changes", "Changes in value proposition"),
        ("B5_bmi_customer_engagement_changes", "Changes in customer engagement strategies"),
        ("B6_drivers_competitive_pressure", "Perceived competitive pressure"),
        ("B6_drivers_customer_demand", "Customer demand for innovation"),
        ("B6_drivers_top_mgmt_attitude", "Top management attitude towards innovation"),
    ]
    for var, label in B_labels:
        add_dict(var, label, "B", "Likert", "1-5", "1=Strongly disagree ... 5=Strongly agree")

    # Section B dict (composites)
    add_dict("B_comp_digital_tools_mean_1_5", "Composite: Digital tools (mean)", "B", "numeric", "1-5", "Mean of B1 items")
    add_dict("B_comp_advanced_tech_mean_1_5", "Composite: Advanced tech (mean)", "B", "numeric", "1-5", "Mean of B2 items")
    add_dict("B_comp_process_innovation_mean_1_5", "Composite: Process innovation (mean)", "B", "numeric", "1-5", "Mean of B3 items")
    add_dict("B_comp_product_innovation_mean_1_5", "Composite: Product/service innovation (mean)", "B", "numeric", "1-5", "Mean of B4 items")
    add_dict("B_comp_bmi_mean_1_5", "Composite: Business model innovation (mean)", "B", "numeric", "1-5", "Mean of B5 items")
    add_dict("B_comp_level_digitization_1_5", "Level of digitization (ordinal)", "B", "numeric", "1-5", "Derived from latent digitization")
    add_dict("B_comp_level_digitization_score_0_100", "Digitization score (0-100)", "B", "numeric", "0-100", "Scaled from 1-5 index")

    # Section C dict
    C_labels = [
        ("C1_financial_access_to_credit", "Financial constraint: access to credit"),
        ("C1_financial_cost_of_innovation", "Financial constraint: cost of innovation"),
        ("C1_financial_internal_capital_sufficiency", "Financial constraint: sufficiency of internal capital"),
        ("C2_human_skill_shortage", "Human capital: difficulty finding skilled employees"),
        ("C2_human_training_cost", "Human capital: cost of training"),
        ("C2_human_mgmt_capability_for_change", "Human capital: management capability for change"),
        ("C3_infra_power_reliability", "Infrastructure: reliability of electricity/power supply"),
        ("C3_infra_internet_quality_cost", "Infrastructure: quality and cost of internet"),
        ("C3_infra_logistics_access", "Infrastructure: access to reliable logistics and transportation"),
        ("C4_regulatory_burden_taxes", "Regulatory: burden of regulations and taxes"),
        ("C4_regulatory_corruption_informal_charges", "Regulatory: corruption and informal charges"),
        ("C4_regulatory_govt_program_effectiveness", "Regulatory: effectiveness of government support programs"),
        ("C5_market_competition_intensity", "Market: intensity of competition"),
        ("C5_market_demand_uncertainty", "Market: uncertainty of demand"),
        ("C5_market_international_access", "Market: access to international markets"),
    ]
    for var, label in C_labels:
        add_dict(var, label, "C", "Likert", "1-5", "1=Strongly disagree ... 5=Strongly agree")

    # Section D dict
    D_labels = [
        ("D1_subj_profitability_growth", "Subjective: profitability growth (last 3 years)"),
        ("D1_subj_sales_growth", "Subjective: sales growth (last 3 years)"),
        ("D1_subj_market_share_growth", "Subjective: market share growth (last 3 years)"),
        ("D1_subj_roi", "Subjective: ROI"),
        ("D1_subj_overall_perf_satisfaction", "Subjective: overall performance satisfaction"),
        ("D_comp_subjective_performance_mean_1_5", "Composite: subjective performance (mean)", "D", "numeric", "1-5", "Mean of D1 items"),
        ("D2_obj_annual_turnover_naira", "Objective: annual turnover (NGN)", "D", "numeric", "ratio", "May be missing"),
        ("D2_obj_profit_naira", "Objective: profit (NGN)", "D", "numeric", "ratio", "May be missing"),
        ("D2_obj_turnover_band", "Objective: turnover band", "D", "categorical", "ordinal", "<₦1m, ₦1m–₦5m, ₦5m–₦20m, ₦20m–₦100m, >₦100m"),
        ("D2_obj_profit_band", "Objective: profit band", "D", "categorical", "ordinal", "Loss/Break-even, ₦0.5m–₦2m, ₦2m–₦10m, ₦10m–₦50m, >₦50m"),
        ("D2_obj_employee_growth_rate_pct", "Objective: employee growth rate (%)", "D", "numeric", "ratio", "-20 to 60 typical"),
        ("D2_obj_num_new_branches_clients", "Objective: number of new branches/clients", "D", "integer", "count", "Non-negative"),
        ("D3_nonfin_increase_product_lines", "Non-financial: increased product/service lines", "D", "Likert", "1-5", "Derived from innovation latents"),
        ("D3_nonfin_quality_improved", "Non-financial: improved quality", "D", "Likert", "1-5", "Derived from innovation latents"),
        ("D3_nonfin_customer_satisfaction_retention", "Non-financial: customer satisfaction/retention", "D", "Likert", "1-5", "Derived from innovation latents"),
    ]

    for rec in D_labels:
        if len(rec) == 2:
            var, label = rec
            add_dict(var, label, "D", "Likert", "1-5", "1=Strongly disagree ... 5=Strongly agree")
        elif len(rec) == 6:
            var, label, section, vtype, scale, values = rec
            add_dict(var, label, section, vtype, scale, values)
        else:
            raise ValueError(f"Unexpected D_labels entry length for {rec}")

    dict_df = pd.DataFrame(dict_rows)

    return df, dict_df


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic Nigerian SME innovation survey dataset")
    parser.add_argument("--n", type=int, default=5000, help="Number of firms (rows)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--out-data", type=str, default="data/core_dataset_sme_innovation.csv", help="Output dataset CSV path")
    parser.add_argument("--out-dict", type=str, default="data/core_dataset_variables_dictionary.csv", help="Output variables dictionary CSV path")

    args = parser.parse_args()

    # Ensure output directories exist
    for path in [args.out_data, args.out_dict]:
        out_dir = os.path.dirname(os.path.abspath(path))
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

    df, dict_df = build_dataset(n=args.n, seed=args.seed)

    # Save
    df.to_csv(args.out_data, index=False)
    dict_df.to_csv(args.out_dict, index=False)

    # Print a brief summary to stdout
    print(f"Wrote dataset: {args.out_data} with {len(df)} rows and {len(df.columns)} columns")
    print(f"Wrote dictionary: {args.out_dict} with {len(dict_df)} variables described")


if __name__ == "__main__":
    main()
