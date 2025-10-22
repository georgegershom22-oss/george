#!/usr/bin/env python3

import argparse
import json
import math
import random
import uuid
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


# ------------------------------
# Constants and reference data
# ------------------------------

NIGERIA_STATES_TO_ZONE: Dict[str, str] = {
    # North Central
    "Benue": "North Central",
    "Kogi": "North Central",
    "Kwara": "North Central",
    "Nasarawa": "North Central",
    "Niger": "North Central",
    "Plateau": "North Central",
    "FCT Abuja": "North Central",
    # North East
    "Adamawa": "North East",
    "Bauchi": "North East",
    "Borno": "North East",
    "Gombe": "North East",
    "Taraba": "North East",
    "Yobe": "North East",
    # North West
    "Jigawa": "North West",
    "Kaduna": "North West",
    "Kano": "North West",
    "Katsina": "North West",
    "Kebbi": "North West",
    "Sokoto": "North West",
    "Zamfara": "North West",
    # South East
    "Abia": "South East",
    "Anambra": "South East",
    "Ebonyi": "South East",
    "Enugu": "South East",
    "Imo": "South East",
    # South South
    "Akwa Ibom": "South South",
    "Bayelsa": "South South",
    "Cross River": "South South",
    "Delta": "South South",
    "Edo": "South South",
    "Rivers": "South South",
    # South West
    "Ekiti": "South West",
    "Lagos": "South West",
    "Ogun": "South West",
    "Ondo": "South West",
    "Osun": "South West",
    "Oyo": "South West",
}

ALL_STATES: List[str] = list(NIGERIA_STATES_TO_ZONE.keys())
ALL_ZONES: List[str] = sorted(set(NIGERIA_STATES_TO_ZONE.values()))

# Approximate sampling weights to reflect SME concentration in urban/industrial centers
STATE_SAMPLING_WEIGHTS: Dict[str, float] = {
    state: 1.0 for state in ALL_STATES
}
STATE_SAMPLING_WEIGHTS.update(
    {
        "Lagos": 6.0,
        "Kano": 3.0,
        "Rivers": 3.0,
        "FCT Abuja": 3.0,
        "Oyo": 2.0,
        "Ogun": 2.0,
        "Kaduna": 2.0,
        "Anambra": 2.0,
        "Delta": 2.0,
        "Abia": 1.5,
    }
)

# Base probability of Urban location by zone; state-specific overrides below
ZONE_TO_URBAN_PROB: Dict[str, float] = {
    "South West": 0.78,
    "South South": 0.62,
    "South East": 0.58,
    "North Central": 0.60,
    "North East": 0.42,
    "North West": 0.48,
}

STATE_URBAN_OVERRIDES: Dict[str, float] = {
    "Lagos": 0.95,
    "FCT Abuja": 0.90,
    "Rivers": 0.80,
}

# Simplified ISIC Rev.4 high-level section codes relevant for SMEs
INDUSTRIES: List[Tuple[str, str]] = [
    ("C", "Manufacturing"),
    ("G", "Wholesale/Retail Trade"),
    ("J", "Information & Communication (IT Services)"),
    ("A", "Agriculture, Forestry & Fishing"),
    ("I", "Accommodation & Food Service (Hospitality)"),
    ("H", "Transportation & Storage"),
    ("M", "Professional, Scientific & Technical Activities"),
    ("S", "Other Service Activities"),
]

INDUSTRY_WEIGHTS: Dict[str, float] = {
    "C": 0.18,
    "G": 0.35,
    "J": 0.08,
    "A": 0.10,
    "I": 0.10,
    "H": 0.07,
    "M": 0.06,
    "S": 0.06,
}

LEGAL_STRUCTURES: List[str] = [
    "Sole Proprietorship",
    "Partnership",
    "Limited Liability",
]
LEGAL_WEIGHTS: List[float] = [0.65, 0.15, 0.20]

EDUCATION_LEVELS: List[str] = [
    "Primary",
    "Secondary",
    "Diploma/OND",
    "Bachelor's",
    "Master's",
    "PhD",
]
EDU_WEIGHTS: List[float] = [0.05, 0.30, 0.25, 0.30, 0.08, 0.02]

FIELDS_OF_STUDY: List[str] = [
    "Business/Management",
    "Engineering",
    "Computer Science/IT",
    "Agriculture",
    "Arts/Humanities",
    "Other",
]

GENDERS: List[str] = ["Male", "Female", "Other/Prefer not to say"]
GENDER_WEIGHTS: List[float] = [0.62, 0.37, 0.01]

SIZE_CLASSES: List[str] = ["Micro", "Small", "Medium"]
SIZE_WEIGHTS: List[float] = [0.70, 0.25, 0.05]
SIZE_TO_EMP_RANGE: Dict[str, Tuple[int, int]] = {
    "Micro": (1, 9),
    "Small": (10, 49),
    "Medium": (50, 199),
}

LIKERT_VALUES = [1, 2, 3, 4, 5]


@dataclass
class Args:
    rows: int
    seed: int
    out_data_dir: str
    out_schema_dir: str
    out_metadata_dir: str


def softmax(x: np.ndarray) -> np.ndarray:
    z = x - np.max(x)
    e = np.exp(z)
    return e / e.sum()


def sample_with_weights(options: List[str], weights: List[float], n: int) -> List[str]:
    probs = np.array(weights, dtype=float)
    probs = probs / probs.sum()
    idx = np.random.choice(len(options), size=n, p=probs)
    return [options[i] for i in idx]


def likert_from_latent(latent: np.ndarray, bias: float = 0.0) -> np.ndarray:
    """Map a latent normal variable to 1..5 using symmetric cutpoints."""
    # Cutpoints for 5 categories on N(0,1)
    cuts = np.array([-0.8, -0.2, 0.2, 0.8]) + bias
    out = np.digitize(latent, cuts) + 1
    out = np.clip(out, 1, 5)
    return out


def clamp_array(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    return np.minimum(np.maximum(x, lo), hi)


def generate_base_demographics(n: int, rng: np.random.Generator) -> Dict[str, np.ndarray]:
    # States with weights
    states = np.array(ALL_STATES)
    weights = np.array([STATE_SAMPLING_WEIGHTS[s] for s in states], dtype=float)
    weights = weights / weights.sum()
    state_idx = rng.choice(len(states), size=n, p=weights)
    state = states[state_idx]
    zone = np.array([NIGERIA_STATES_TO_ZONE[s] for s in state])

    # Urban/Rural
    urban_prob = np.array(
        [STATE_URBAN_OVERRIDES.get(s, ZONE_TO_URBAN_PROB[NIGERIA_STATES_TO_ZONE[s]]) for s in state]
    )
    is_urban = rng.random(n) < urban_prob
    urban_rural = np.where(is_urban, "Urban", "Rural")

    # Industry (ISIC code + label)
    codes = [c for c, _ in INDUSTRIES]
    labels = [l for _, l in INDUSTRIES]
    ind_weights = np.array([INDUSTRY_WEIGHTS[c] for c in codes], dtype=float)
    ind_weights = ind_weights / ind_weights.sum()
    ind_idx = rng.choice(len(codes), size=n, p=ind_weights)
    industry_code = np.array([codes[i] for i in ind_idx])
    industry_label = np.array([labels[i] for i in ind_idx])

    # Legal structure
    legal = rng.choice(LEGAL_STRUCTURES, size=n, p=np.array(LEGAL_WEIGHTS) / sum(LEGAL_WEIGHTS))

    # Firm age (years) - Gamma-like skew, clipped
    firm_age_years = np.clip(rng.gamma(shape=2.2, scale=4.0, size=n), 0.5, 50.0)

    # Size class and employees
    size_class = rng.choice(SIZE_CLASSES, size=n, p=np.array(SIZE_WEIGHTS) / sum(SIZE_WEIGHTS))
    employees = np.empty(n, dtype=int)
    for sc in SIZE_CLASSES:
        mask = size_class == sc
        lo, hi = SIZE_TO_EMP_RANGE[sc]
        employees[mask] = rng.integers(lo, hi + 1, size=mask.sum())

    # Turnover simulation (Naira): revenue per employee varies by industry and urbanity
    industry_rev_multiplier = {
        "C": 1.25,
        "G": 0.90,
        "J": 1.40,
        "A": 0.60,
        "I": 0.85,
        "H": 0.95,
        "M": 1.30,
        "S": 0.80,
    }
    base_revenue_per_employee = 4_500_000.0  # NGN; rough SME scale
    rev_emp_mult = np.array([industry_rev_multiplier[c] for c in industry_code])
    urban_mult = np.where(is_urban, 1.10, 0.90)
    age_mult = clamp_array(1.0 + 0.02 * (firm_age_years - 5.0) - 0.0003 * (firm_age_years - 10.0) ** 2, 0.6, 1.6)
    # Lognormal noise factor
    noise = rng.lognormal(mean=0.0, sigma=0.6, size=n)
    turnover_naira = employees * base_revenue_per_employee * rev_emp_mult * urban_mult * age_mult * noise

    # Owner/Manager profile
    manager_age = np.clip(rng.normal(loc=40, scale=9.0, size=n), 20, 70).round(0).astype(int)
    gender = rng.choice(GENDERS, size=n, p=np.array(GENDER_WEIGHTS) / sum(GENDER_WEIGHTS))
    education = rng.choice(EDUCATION_LEVELS, size=n, p=np.array(EDU_WEIGHTS) / sum(EDU_WEIGHTS))
    field_of_study = rng.choice(FIELDS_OF_STUDY, size=n)
    prior_entre_exp = rng.random(n) < 0.42

    # Digital literacy score influenced by education and urbanity
    edu_to_mean = {
        "Primary": 35,
        "Secondary": 48,
        "Diploma/OND": 58,
        "Bachelor's": 70,
        "Master's": 78,
        "PhD": 82,
    }
    dl_mean = np.array([edu_to_mean[e] for e in education]) * np.where(is_urban, 1.05, 0.95)
    digital_literacy = clamp_array(rng.normal(loc=dl_mean, scale=12.0, size=n), 0, 100).round(0)

    # Firm ID
    firm_id = np.array([str(uuid.uuid4()) for _ in range(n)])

    return {
        "firm_id": firm_id,
        "state": state,
        "geo_zone": zone,
        "urban_rural": urban_rural,
        "industry_isic": industry_code,
        "industry_label": industry_label,
        "firm_age_years": firm_age_years.round(1),
        "size_class": size_class,
        "employees_full_time": employees,
        "turnover_naira": turnover_naira,
        "legal_structure": legal,
        "manager_age": manager_age,
        "manager_gender": gender,
        "manager_education": education,
        "manager_field_of_study": field_of_study,
        "manager_prior_entre_experience": prior_entre_exp,
        "manager_digital_literacy_score": digital_literacy.astype(int),
    }


def generate_innovation_blocks(n: int, base: Dict[str, np.ndarray], rng: np.random.Generator) -> Dict[str, np.ndarray]:
    # Latent innovation orientation influenced by digital literacy, urban, size, industry
    industry_bias = {
        "J": 0.55,  # IT
        "M": 0.25,
        "C": 0.15,
        "G": 0.05,
        "I": 0.05,
        "H": 0.00,
        "S": -0.05,
        "A": -0.10,
    }
    industry_b = np.array([industry_bias[c] for c in base["industry_isic"]])
    urban_b = np.where(base["urban_rural"] == "Urban", 0.20, -0.15)
    size_b = np.where(base["size_class"] == "Medium", 0.25, np.where(base["size_class"] == "Small", 0.10, -0.05))
    dl_z = (base["manager_digital_literacy_score"].astype(float) - 50.0) / 20.0

    innovation_orientation = (
        0.45 * dl_z + 0.25 * urban_b + 0.30 * size_b + 0.35 * industry_b + rng.normal(0, 0.7, n)
    )

    # Digital presence flags (binary) derived from orientation
    p_website = 0.25 + 0.18 * (innovation_orientation + 1.0) + 0.10 * (base["industry_isic"] == "J")
    p_social = 0.40 + 0.22 * (innovation_orientation + 1.0)
    p_online_pay = 0.20 + 0.20 * (innovation_orientation + 1.0) + 0.06 * (base["industry_isic"] == "G")
    has_website = rng.random(n) < clamp_array(p_website, 0.05, 0.98)
    uses_social_media = rng.random(n) < clamp_array(p_social, 0.10, 0.99)
    accepts_online_payments = rng.random(n) < clamp_array(p_online_pay, 0.05, 0.95)

    level_of_digitization_score = (
        (has_website.astype(int) + uses_social_media.astype(int) + accepts_online_payments.astype(int)) / 3.0
    ) * 100.0

    # Technological Innovation - Digital Tools Adoption (6 items)
    L = innovation_orientation[:, None] + rng.normal(0, 0.8, size=(n, 6))
    digital_tools = likert_from_latent(L)
    (
        b_computers,
        b_accounting,
        b_crm,
        b_ecommerce,
        b_cloud,
        b_social,
    ) = [digital_tools[:, i] for i in range(6)]

    # Advanced Tech Adoption (4 items) - sparser overall
    L_adv = innovation_orientation[:, None] - 0.4 + rng.normal(0, 0.9, size=(n, 4))
    adv_items = likert_from_latent(L_adv)
    (
        b_ai_ml,
        b_iot,
        b_blockchain,
        b_robotics,
    ) = [adv_items[:, i] for i in range(4)]

    # Process Innovation (3 items)
    L_proc = innovation_orientation[:, None] + rng.normal(0, 0.8, size=(n, 3))
    proc_items = likert_from_latent(L_proc)
    (
        b_new_methods,
        b_supply_chain_software,
        b_support_techniques,
    ) = [proc_items[:, i] for i in range(3)]

    # Product/Service Innovation (2 items)
    L_prod = innovation_orientation[:, None] + rng.normal(0, 0.8, size=(n, 2))
    prod_items = likert_from_latent(L_prod)
    (
        b_new_or_improved_last3y,
        b_new_product_launch_frequency,
    ) = [prod_items[:, i] for i in range(2)]

    # Business Model Innovation (3 items)
    L_bmi = innovation_orientation[:, None] + rng.normal(0, 0.8, size=(n, 3))
    bmi_items = likert_from_latent(L_bmi)
    (
        b_rev_model_changes,
        b_value_prop_changes,
        b_customer_engagement_changes,
    ) = [bmi_items[:, i] for i in range(3)]

    # Innovation Drivers (3 items)
    driver_bias = 0.15
    L_drv = innovation_orientation[:, None] + driver_bias + rng.normal(0, 0.8, size=(n, 3))
    drv_items = likert_from_latent(L_drv)
    (
        b_competitive_pressure,
        b_customer_demand,
        b_top_mgmt_attitude,
    ) = [drv_items[:, i] for i in range(3)]

    # Indices (means on 1..5 scale)
    tech_index = (
        b_computers + b_accounting + b_crm + b_ecommerce + b_cloud + b_social
    ) / 6.0
    adv_index = (b_ai_ml + b_iot + b_blockchain + b_robotics) / 4.0
    proc_index = (b_new_methods + b_supply_chain_software + b_support_techniques) / 3.0
    prod_index = (b_new_or_improved_last3y + b_new_product_launch_frequency) / 2.0
    bmi_index = (b_rev_model_changes + b_value_prop_changes + b_customer_engagement_changes) / 3.0
    drivers_index = (b_competitive_pressure + b_customer_demand + b_top_mgmt_attitude) / 3.0

    innovation_composite_index = (
        0.35 * tech_index + 0.15 * adv_index + 0.20 * proc_index + 0.15 * prod_index + 0.15 * bmi_index
    )

    return {
        # Digital presence
        "has_website": has_website,
        "uses_social_media": uses_social_media,
        "accepts_online_payments": accepts_online_payments,
        "level_of_digitization_score": level_of_digitization_score,
        # Digital tools (6)
        "B_Tech_DigitalTools_Computers": b_computers,
        "B_Tech_DigitalTools_Accounting": b_accounting,
        "B_Tech_DigitalTools_CRM": b_crm,
        "B_Tech_DigitalTools_Ecommerce": b_ecommerce,
        "B_Tech_DigitalTools_Cloud": b_cloud,
        "B_Tech_DigitalTools_SocialMedia": b_social,
        # Advanced tech (4)
        "B_Tech_Advanced_AI_ML": b_ai_ml,
        "B_Tech_Advanced_IoT": b_iot,
        "B_Tech_Advanced_Blockchain": b_blockchain,
        "B_Tech_Advanced_Robotics": b_robotics,
        # Process (3)
        "B_Process_NewMethods": b_new_methods,
        "B_Process_SupplyChainSoftware": b_supply_chain_software,
        "B_Process_SupportTechniques": b_support_techniques,
        # Product/Service (2)
        "B_Product_NewOrImproved_Last3Y": b_new_or_improved_last3y,
        "B_Product_NewLaunch_Frequency": b_new_product_launch_frequency,
        # Business Model Innovation (3)
        "B_BMI_RevenueModel_Changes": b_rev_model_changes,
        "B_BMI_ValueProp_Changes": b_value_prop_changes,
        "B_BMI_CustomerEngagement_Changes": b_customer_engagement_changes,
        # Drivers (3)
        "B_Drivers_CompetitivePressure": b_competitive_pressure,
        "B_Drivers_CustomerDemand": b_customer_demand,
        "B_Drivers_TopMgmtAttitude": b_top_mgmt_attitude,
        # Indices
        "TechnologicalInnovationIndex": tech_index,
        "AdvancedTechAdoptionIndex": adv_index,
        "ProcessInnovationIndex": proc_index,
        "ProductInnovationIndex": prod_index,
        "BusinessModelInnovationIndex": bmi_index,
        "InnovationDriversIndex": drivers_index,
        "InnovationCompositeIndex": innovation_composite_index,
    }


def generate_constraints(n: int, base: Dict[str, np.ndarray], rng: np.random.Generator) -> Dict[str, np.ndarray]:
    # Zone and rurality influence constraints
    zone = base["geo_zone"]
    is_urban = base["urban_rural"] == "Urban"

    zone_infra_bias = {
        "South West": -0.10,
        "South South": -0.05,
        "South East": -0.02,
        "North Central": 0.05,
        "North East": 0.25,
        "North West": 0.15,
    }
    infra_b = np.array([zone_infra_bias[z] for z in zone]) + np.where(is_urban, -0.08, 0.10)

    # Financial constraints heavier for micro firms and young firms
    size_b = np.where(base["size_class"] == "Micro", 0.25, np.where(base["size_class"] == "Small", 0.08, -0.15))
    age_b = clamp_array(0.20 - 0.02 * (base["firm_age_years"].astype(float) - 2.0), -0.10, 0.25)

    # Regulatory constraints by zone (some variability) and industry
    industry_reg_bias = {
        "C": 0.10,
        "G": 0.05,
        "J": -0.08,
        "A": 0.05,
        "I": 0.02,
        "H": 0.06,
        "M": -0.05,
        "S": 0.03,
    }
    reg_b = np.array([industry_reg_bias[c] for c in base["industry_isic"]])

    # Latent constraint scores
    L_fin = 0.4 * size_b + 0.3 * age_b + rng.normal(0, 0.8, n)
    L_hc = 0.25 * size_b + rng.normal(0, 0.9, n) + np.where(is_urban, -0.05, 0.10)
    L_infra = 0.6 * infra_b + rng.normal(0, 0.9, n)
    L_reg = 0.3 * reg_b + rng.normal(0, 0.8, n) + np.where(zone == "North East", 0.10, 0.0)
    L_mkt = rng.normal(0, 0.9, n) + np.where(base["industry_isic"] == "G", 0.10, 0.0)

    # Map to Likert where higher = stronger constraint (worse), except regulatory effectiveness
    fin_access_credit = likert_from_latent(L_fin + 0.15)  # difficulty accessing credit
    fin_cost_of_innovation = likert_from_latent(L_fin + 0.10)
    fin_internal_capital_insufficient = likert_from_latent(L_fin + 0.20)

    hc_skill_gap = likert_from_latent(L_hc + 0.20)
    hc_training_cost = likert_from_latent(L_hc + 0.10)
    hc_mgmt_capability_gap = likert_from_latent(L_hc + 0.05)

    infra_power_unreliable = likert_from_latent(L_infra + 0.35)
    infra_internet_poor_expensive = likert_from_latent(L_infra + 0.10)
    infra_logistics_challenges = likert_from_latent(L_infra + 0.15)

    reg_burden = likert_from_latent(L_reg + 0.10)
    reg_corruption_informal_charges = likert_from_latent(L_reg + 0.15)
    reg_support_effectiveness = likert_from_latent(-L_reg + -0.05)  # higher = more effective (positive)

    mkt_competition_intensity = likert_from_latent(L_mkt + 0.20)
    mkt_demand_uncertainty = likert_from_latent(L_mkt + 0.10)
    mkt_limited_international_access = likert_from_latent(L_mkt + 0.10)

    # Indices (higher means stronger constraint for the category)
    fin_idx = (fin_access_credit + fin_cost_of_innovation + fin_internal_capital_insufficient) / 3.0
    hc_idx = (hc_skill_gap + hc_training_cost + hc_mgmt_capability_gap) / 3.0
    infra_idx = (infra_power_unreliable + infra_internet_poor_expensive + infra_logistics_challenges) / 3.0
    reg_idx = (reg_burden + reg_corruption_informal_charges + (6 - reg_support_effectiveness)) / 3.0
    mkt_idx = (mkt_competition_intensity + mkt_demand_uncertainty + mkt_limited_international_access) / 3.0

    constraint_composite_index = 0.30 * fin_idx + 0.20 * hc_idx + 0.25 * infra_idx + 0.15 * reg_idx + 0.10 * mkt_idx

    return {
        # Financial
        "C_Financial_Difficulty_Access_Credit": fin_access_credit,
        "C_Financial_Cost_of_Innovation": fin_cost_of_innovation,
        "C_Financial_Internal_Capital_Insufficient": fin_internal_capital_insufficient,
        # Human Capital
        "C_HC_Skilled_Employees_Difficult": hc_skill_gap,
        "C_HC_Training_Cost_High": hc_training_cost,
        "C_HC_Mgmt_Leadership_Capability_Low": hc_mgmt_capability_gap,
        # Infrastructure
        "C_Infra_Power_Unreliable": infra_power_unreliable,
        "C_Infra_Internet_Poor_Expensive": infra_internet_poor_expensive,
        "C_Infra_Logistics_Challenges": infra_logistics_challenges,
        # Regulatory & Institutional
        "C_Reg_Burden_Regulations_Taxes": reg_burden,
        "C_Reg_Corruption_Informal_Charges": reg_corruption_informal_charges,
        "C_Reg_Support_Programs_Effectiveness": reg_support_effectiveness,  # higher is better
        # Market
        "C_Mkt_Competition_Intensity": mkt_competition_intensity,
        "C_Mkt_Demand_Uncertainty": mkt_demand_uncertainty,
        "C_Mkt_Limited_International_Access": mkt_limited_international_access,
        # Indices
        "Constraints_Financial_Index": fin_idx,
        "Constraints_HumanCapital_Index": hc_idx,
        "Constraints_Infrastructure_Index": infra_idx,
        "Constraints_Regulatory_Index": reg_idx,
        "Constraints_Market_Index": mkt_idx,
        "Constraints_Composite_Index": constraint_composite_index,
    }


def generate_performance(n: int, base: Dict[str, np.ndarray], innovation: Dict[str, np.ndarray], constraints: Dict[str, np.ndarray], rng: np.random.Generator) -> Dict[str, np.ndarray]:
    # Structural effects: innovation boosts, constraints reduce
    innov = innovation["InnovationCompositeIndex"].astype(float)
    constr = constraints["Constraints_Composite_Index"].astype(float)

    # Subjective performance items (higher is better)
    latent_perf = 0.55 * (innov - 3.0) - 0.45 * (constr - 3.0) + rng.normal(0, 0.8, n)

    sp_profit_growth = likert_from_latent(latent_perf + 0.10)
    sp_sales_growth = likert_from_latent(latent_perf + 0.15)
    sp_market_share = likert_from_latent(latent_perf + 0.05)
    sp_roi = likert_from_latent(latent_perf)
    sp_overall_satisfaction = likert_from_latent(latent_perf + 0.10)

    subjective_perf_index = (
        sp_profit_growth + sp_sales_growth + sp_market_share + sp_roi + sp_overall_satisfaction
    ) / 5.0

    # Objective performance
    # Profit margin influenced by innovation and constraints
    base_margin = 0.10 + 0.05 * (innov - 3.0) - 0.04 * (constr - 3.0) + rng.normal(0, 0.04, n)
    profit_margin = clamp_array(base_margin, -0.15, 0.35)
    turnover_naira = base["turnover_naira"].astype(float)
    profit_naira = profit_margin * turnover_naira

    # Employee growth rate
    emp_growth_rate = clamp_array(0.01 + 0.08 * (innov - 3.0) - 0.06 * (constr - 3.0) + rng.normal(0, 0.07, n), -0.35, 0.80)

    # Branches/clients growth
    size_factor = np.where(base["size_class"] == "Micro", 0.4, np.where(base["size_class"] == "Small", 0.9, 1.6))
    expected_branches = clamp_array(0.10 * (innov - 2.5) * size_factor + 0.15, 0.0, 3.0)
    num_new_branches = rng.poisson(lam=expected_branches)

    expected_clients = clamp_array(4.0 * (innov - 2.0) * size_factor + 8.0, 0.5, 80.0)
    num_new_clients = rng.poisson(lam=expected_clients)

    # Non-financial growth indicators (Likert, higher is better)
    nf_product_lines = likert_from_latent(latent_perf + 0.10)
    nf_quality_improved = likert_from_latent(latent_perf + 0.15)
    nf_customer_satisfaction_retention = likert_from_latent(latent_perf + 0.20)

    # Missingness for sensitive numeric fields
    expose_numeric = rng.random(n) < 0.60  # 60% provide numeric
    turnover_reported = np.where(expose_numeric, turnover_naira, np.nan)
    profit_reported = np.where(expose_numeric, profit_naira, np.nan)

    # Ranges for turnover/profit (if numeric missing, still provide range)
    def to_range(values: np.ndarray, bins: List[float]) -> np.ndarray:
        labels = [
            "0-1m",
            "1-5m",
            "5-20m",
            "20-100m",
            "100-500m",
            ">500m",
        ]
        idx = np.digitize(values, bins, right=True)
        idx = np.clip(idx, 0, len(labels) - 1)
        return np.array([labels[i] for i in idx])

    turnover_bins = [1_000_000, 5_000_000, 20_000_000, 100_000_000, 500_000_000]
    profit_bins = [250_000, 1_000_000, 5_000_000, 20_000_000, 100_000_000]

    turnover_range = to_range(np.nan_to_num(turnover_naira, nan=0.0), turnover_bins)
    profit_range = to_range(np.nan_to_num(np.abs(profit_naira), nan=0.0), profit_bins)

    return {
        # Subjective performance (Likert)
        "D_Subj_Profitability_Growth": sp_profit_growth,
        "D_Subj_Sales_Growth": sp_sales_growth,
        "D_Subj_MarketShare_Growth": sp_market_share,
        "D_Subj_ROI": sp_roi,
        "D_Subj_Overall_Satisfaction": sp_overall_satisfaction,
        "SubjectivePerformanceIndex": subjective_perf_index,
        # Objective performance
        "turnover_naira_reported": turnover_reported,
        "turnover_range": turnover_range,
        "profit_naira_reported": profit_reported,
        "profit_range": profit_range,
        "employee_growth_rate": emp_growth_rate,
        "employee_growth_percent": (emp_growth_rate * 100.0),
        "num_new_branches": num_new_branches,
        "num_new_clients": num_new_clients,
        # Non-financial growth (Likert)
        "D_NonFin_ProductLines_Increase": nf_product_lines,
        "D_NonFin_Quality_Improved": nf_quality_improved,
        "D_NonFin_Customer_Satisfaction_Retention": nf_customer_satisfaction_retention,
    }


def build_variable_dictionary(df: pd.DataFrame) -> pd.DataFrame:
    # Minimal, high-signal dictionary
    records: List[Dict[str, str]] = []

    def add(name: str, section: str, label: str, vtype: str, scale: str = "", allowed: str = "", derived: bool = False):
        records.append(
            {
                "variable": name,
                "section": section,
                "label": label,
                "type": vtype,
                "scale": scale,
                "allowed_values": allowed,
                "derived": "yes" if derived else "no",
            }
        )

    likert_allowed = "1-5 (1=Strongly Disagree, 5=Strongly Agree)"

    # Section A
    add("firm_id", "A", "Anonymized Firm ID (UUID)", "string")
    add("state", "A", "State", "string", allowed=",".join(ALL_STATES))
    add("geo_zone", "A", "Geo-Political Zone", "string", allowed=",".join(ALL_ZONES))
    add("urban_rural", "A", "Location Type", "string", allowed="Urban,Rural")
    add("industry_isic", "A", "ISIC Section Code", "string", allowed=",".join([c for c, _ in INDUSTRIES]))
    add("industry_label", "A", "Industry Label", "string")
    add("firm_age_years", "A", "Firm Age (years)", "number")
    add("size_class", "A", "SME Size Class", "string", allowed=",".join(SIZE_CLASSES))
    add("employees_full_time", "A", "Full-time Employees", "integer")
    add("turnover_naira", "A", "Estimated Annual Turnover (NGN)", "number", derived=True)
    add("legal_structure", "A", "Legal Structure", "string", allowed=",".join(LEGAL_STRUCTURES))
    add("manager_age", "A", "Owner/Manager Age", "integer")
    add("manager_gender", "A", "Owner/Manager Gender", "string", allowed=",".join(GENDERS))
    add("manager_education", "A", "Highest Education Level", "string", allowed=",".join(EDUCATION_LEVELS))
    add("manager_field_of_study", "A", "Field of Study", "string", allowed=",".join(FIELDS_OF_STUDY))
    add("manager_prior_entre_experience", "A", "Prior Entrepreneurial Experience", "boolean")
    add("manager_digital_literacy_score", "A", "Digital Literacy Score (0-100)", "integer", scale="0-100")

    # Section B - many Likert
    for col in [
        "B_Tech_DigitalTools_Computers",
        "B_Tech_DigitalTools_Accounting",
        "B_Tech_DigitalTools_CRM",
        "B_Tech_DigitalTools_Ecommerce",
        "B_Tech_DigitalTools_Cloud",
        "B_Tech_DigitalTools_SocialMedia",
        "B_Tech_Advanced_AI_ML",
        "B_Tech_Advanced_IoT",
        "B_Tech_Advanced_Blockchain",
        "B_Tech_Advanced_Robotics",
        "B_Process_NewMethods",
        "B_Process_SupplyChainSoftware",
        "B_Process_SupportTechniques",
        "B_Product_NewOrImproved_Last3Y",
        "B_Product_NewLaunch_Frequency",
        "B_BMI_RevenueModel_Changes",
        "B_BMI_ValueProp_Changes",
        "B_BMI_CustomerEngagement_Changes",
        "B_Drivers_CompetitivePressure",
        "B_Drivers_CustomerDemand",
        "B_Drivers_TopMgmtAttitude",
    ]:
        add(col, "B", col.replace("_", " "), "integer", scale=likert_allowed)

    add("has_website", "B", "Has Business Website", "boolean")
    add("uses_social_media", "B", "Uses Social Media for Business", "boolean")
    add("accepts_online_payments", "B", "Accepts Online/Digital Payments", "boolean")
    add("level_of_digitization_score", "B", "Digital Presence Composite (0-100)", "number", scale="0-100", derived=True)

    for name, label in [
        ("TechnologicalInnovationIndex", "Technological Innovation Index (mean of 6 items)"),
        ("AdvancedTechAdoptionIndex", "Advanced Technology Adoption Index (mean of 4 items)"),
        ("ProcessInnovationIndex", "Process Innovation Index (mean of 3 items)"),
        ("ProductInnovationIndex", "Product/Service Innovation Index (mean of 2 items)"),
        ("BusinessModelInnovationIndex", "Business Model Innovation Index (mean of 3 items)"),
        ("InnovationDriversIndex", "Innovation Drivers Index (mean of 3 items)"),
        ("InnovationCompositeIndex", "Innovation Composite Index (weighted)"),
    ]:
        add(name, "B", label, "number", scale="1-5", derived=True)

    # Section C - Constraints
    for col in [
        "C_Financial_Difficulty_Access_Credit",
        "C_Financial_Cost_of_Innovation",
        "C_Financial_Internal_Capital_Insufficient",
        "C_HC_Skilled_Employees_Difficult",
        "C_HC_Training_Cost_High",
        "C_HC_Mgmt_Leadership_Capability_Low",
        "C_Infra_Power_Unreliable",
        "C_Infra_Internet_Poor_Expensive",
        "C_Infra_Logistics_Challenges",
        "C_Reg_Burden_Regulations_Taxes",
        "C_Reg_Corruption_Informal_Charges",
        "C_Reg_Support_Programs_Effectiveness",
        "C_Mkt_Competition_Intensity",
        "C_Mkt_Demand_Uncertainty",
        "C_Mkt_Limited_International_Access",
    ]:
        add(col, "C", col.replace("_", " "), "integer", scale=likert_allowed)

    for name, label in [
        ("Constraints_Financial_Index", "Financial Constraints Index (mean of 3 items)"),
        ("Constraints_HumanCapital_Index", "Human Capital Constraints Index (mean of 3 items)"),
        ("Constraints_Infrastructure_Index", "Infrastructure Constraints Index (mean of 3 items)"),
        ("Constraints_Regulatory_Index", "Regulatory Constraints Index (mean of 3 items, effectiveness inverted)"),
        ("Constraints_Market_Index", "Market Constraints Index (mean of 3 items)"),
        ("Constraints_Composite_Index", "Constraints Composite Index (weighted)"),
    ]:
        add(name, "C", label, "number", scale="1-5", derived=True)

    # Section D - Performance
    for col in [
        "D_Subj_Profitability_Growth",
        "D_Subj_Sales_Growth",
        "D_Subj_MarketShare_Growth",
        "D_Subj_ROI",
        "D_Subj_Overall_Satisfaction",
        "D_NonFin_ProductLines_Increase",
        "D_NonFin_Quality_Improved",
        "D_NonFin_Customer_Satisfaction_Retention",
    ]:
        add(col, "D", col.replace("_", " "), "integer", scale=likert_allowed)

    add("SubjectivePerformanceIndex", "D", "Subjective Performance Index (mean of 5 items)", "number", scale="1-5", derived=True)

    add("turnover_naira_reported", "D", "Annual Turnover (NGN, reported)", "number")
    add("turnover_range", "D", "Annual Turnover Range (NGN)", "string", allowed="0-1m,1-5m,5-20m,20-100m,100-500m,>500m")
    add("profit_naira_reported", "D", "Annual Profit (NGN, reported)", "number")
    add("profit_range", "D", "Annual Profit Range (NGN)", "string", allowed="0-250k,250k-1m,1-5m,5-20m,20-100m,>100m")
    add("employee_growth_rate", "D", "Employee Growth Rate (ratio)", "number")
    add("employee_growth_percent", "D", "Employee Growth Rate (%)", "number")
    add("num_new_branches", "D", "Number of New Branches (3y)", "integer")
    add("num_new_clients", "D", "Number of New Clients (3y)", "integer")

    # Ensure all DataFrame columns are included (fallback entries for any missing)
    for c in df.columns:
        if not any(r["variable"] == c for r in records):
            add(c, "?", c, str(df[c].dtype))

    return pd.DataFrame.from_records(records)


def build_json_schema(df: pd.DataFrame) -> Dict:
    def likert_schema(desc: str) -> Dict:
        return {
            "type": "integer",
            "minimum": 1,
            "maximum": 5,
            "description": desc + " (1=Strongly Disagree, 5=Strongly Agree)",
        }

    props: Dict[str, Dict] = {}

    # Predefined schemas
    props["firm_id"] = {"type": "string", "description": "Anonymized Firm ID (UUID)"}
    props["state"] = {"type": "string", "enum": ALL_STATES, "description": "State"}
    props["geo_zone"] = {"type": "string", "enum": ALL_ZONES, "description": "Geo-Political Zone"}
    props["urban_rural"] = {"type": "string", "enum": ["Urban", "Rural"], "description": "Location Type"}
    props["industry_isic"] = {
        "type": "string",
        "enum": [c for c, _ in INDUSTRIES],
        "description": "ISIC Section Code",
    }
    props["industry_label"] = {"type": "string", "description": "Industry Label"}
    props["firm_age_years"] = {"type": "number", "minimum": 0}
    props["size_class"] = {"type": "string", "enum": SIZE_CLASSES}
    props["employees_full_time"] = {"type": "integer", "minimum": 0}
    props["turnover_naira"] = {"type": ["number", "null"], "minimum": 0}
    props["legal_structure"] = {"type": "string", "enum": LEGAL_STRUCTURES}
    props["manager_age"] = {"type": "integer", "minimum": 15, "maximum": 100}
    props["manager_gender"] = {"type": "string", "enum": GENDERS}
    props["manager_education"] = {"type": "string", "enum": EDUCATION_LEVELS}
    props["manager_field_of_study"] = {"type": "string", "enum": FIELDS_OF_STUDY}
    props["manager_prior_entre_experience"] = {"type": "boolean"}
    props["manager_digital_literacy_score"] = {"type": "integer", "minimum": 0, "maximum": 100}

    # Likert blocks
    for col in [
        "B_Tech_DigitalTools_Computers",
        "B_Tech_DigitalTools_Accounting",
        "B_Tech_DigitalTools_CRM",
        "B_Tech_DigitalTools_Ecommerce",
        "B_Tech_DigitalTools_Cloud",
        "B_Tech_DigitalTools_SocialMedia",
        "B_Tech_Advanced_AI_ML",
        "B_Tech_Advanced_IoT",
        "B_Tech_Advanced_Blockchain",
        "B_Tech_Advanced_Robotics",
        "B_Process_NewMethods",
        "B_Process_SupplyChainSoftware",
        "B_Process_SupportTechniques",
        "B_Product_NewOrImproved_Last3Y",
        "B_Product_NewLaunch_Frequency",
        "B_BMI_RevenueModel_Changes",
        "B_BMI_ValueProp_Changes",
        "B_BMI_CustomerEngagement_Changes",
        "B_Drivers_CompetitivePressure",
        "B_Drivers_CustomerDemand",
        "B_Drivers_TopMgmtAttitude",
        "C_Financial_Difficulty_Access_Credit",
        "C_Financial_Cost_of_Innovation",
        "C_Financial_Internal_Capital_Insufficient",
        "C_HC_Skilled_Employees_Difficult",
        "C_HC_Training_Cost_High",
        "C_HC_Mgmt_Leadership_Capability_Low",
        "C_Infra_Power_Unreliable",
        "C_Infra_Internet_Poor_Expensive",
        "C_Infra_Logistics_Challenges",
        "C_Reg_Burden_Regulations_Taxes",
        "C_Reg_Corruption_Informal_Charges",
        "C_Reg_Support_Programs_Effectiveness",
        "C_Mkt_Competition_Intensity",
        "C_Mkt_Demand_Uncertainty",
        "C_Mkt_Limited_International_Access",
        "D_Subj_Profitability_Growth",
        "D_Subj_Sales_Growth",
        "D_Subj_MarketShare_Growth",
        "D_Subj_ROI",
        "D_Subj_Overall_Satisfaction",
        "D_NonFin_ProductLines_Increase",
        "D_NonFin_Quality_Improved",
        "D_NonFin_Customer_Satisfaction_Retention",
    ]:
        props[col] = likert_schema(col.replace("_", " "))

    # Indices and flags
    for col in [
        "TechnologicalInnovationIndex",
        "AdvancedTechAdoptionIndex",
        "ProcessInnovationIndex",
        "ProductInnovationIndex",
        "BusinessModelInnovationIndex",
        "InnovationDriversIndex",
        "InnovationCompositeIndex",
        "Constraints_Financial_Index",
        "Constraints_HumanCapital_Index",
        "Constraints_Infrastructure_Index",
        "Constraints_Regulatory_Index",
        "Constraints_Market_Index",
        "Constraints_Composite_Index",
        "SubjectivePerformanceIndex",
        "level_of_digitization_score",
    ]:
        props[col] = {"type": "number"}

    for col in ["has_website", "uses_social_media", "accepts_online_payments"]:
        props[col] = {"type": "boolean"}

    # Objective numeric outcomes
    props["turnover_naira_reported"] = {"type": ["number", "null"], "minimum": 0}
    props["turnover_range"] = {
        "type": "string",
        "enum": ["0-1m", "1-5m", "5-20m", "20-100m", "100-500m", ">500m"],
    }
    props["profit_naira_reported"] = {"type": ["number", "null"]}
    props["profit_range"] = {
        "type": "string",
        "enum": ["0-250k", "250k-1m", "1-5m", "5-20m", "20-100m", ">100m"],
    }
    props["employee_growth_rate"] = {"type": "number"}
    props["employee_growth_percent"] = {"type": "number"}
    props["num_new_branches"] = {"type": "integer", "minimum": 0}
    props["num_new_clients"] = {"type": "integer", "minimum": 0}

    # Fallback for any remaining columns
    for c in df.columns:
        if c not in props:
            # Infer type
            series = df[c]
            if pd.api.types.is_integer_dtype(series):
                props[c] = {"type": "integer"}
            elif pd.api.types.is_bool_dtype(series):
                props[c] = {"type": "boolean"}
            elif pd.api.types.is_float_dtype(series):
                props[c] = {"type": "number"}
            else:
                props[c] = {"type": "string"}

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Core Dataset 1: Primary Quantitative Survey (Synthetic)",
        "description": "Structured SME survey dataset for Nigerian SMEs: Innovation, Constraints, and Performance.",
        "type": "object",
        "properties": props,
        "additionalProperties": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic SME survey dataset for Nigeria (Core Dataset 1)")
    parser.add_argument("--rows", type=int, default=2000, help="Number of firms (rows) to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--out-data-dir", type=str, default="/workspace/data", help="Output directory for data")
    parser.add_argument("--out-schema-dir", type=str, default="/workspace/schemas", help="Output directory for JSON schema")
    parser.add_argument("--out-metadata-dir", type=str, default="/workspace/metadata", help="Output directory for variable dictionary")

    a = parser.parse_args()
    rng = np.random.default_rng(a.seed)

    # Generate sections
    base = generate_base_demographics(a.rows, rng)
    innov = generate_innovation_blocks(a.rows, base, rng)
    constraints = generate_constraints(a.rows, base, rng)
    perf = generate_performance(a.rows, base, innov, constraints, rng)

    # Assemble DataFrame
    df = pd.DataFrame({**base, **innov, **constraints, **perf})

    # Type cleanup
    bool_cols = ["has_website", "uses_social_media", "accepts_online_payments", "manager_prior_entre_experience"]
    for c in bool_cols:
        df[c] = df[c].astype(bool)

    # Write data
    csv_path = f"{a.out_data_dir.rstrip('/')}/core_dataset1.csv"
    parquet_path = f"{a.out_data_dir.rstrip('/')}/core_dataset1.parquet"
    schema_path = f"{a.out_schema_dir.rstrip('/')}/core_dataset1_schema.json"
    dict_path = f"{a.out_metadata_dir.rstrip('/')}/core_dataset1_dictionary.csv"

    # Ensure directories exist
    for p in [a.out_data_dir, a.out_schema_dir, a.out_metadata_dir]:
        pd.Path(p).mkdir(parents=True, exist_ok=True) if hasattr(pd, "Path") else None

    df.to_csv(csv_path, index=False)
    try:
        df.to_parquet(parquet_path, index=False)
    except Exception as e:
        # Fallback if parquet engine missing
        print(f"Warning: Parquet export failed: {e}")

    # Variable dictionary
    vdict = build_variable_dictionary(df)
    vdict.to_csv(dict_path, index=False)

    # JSON schema
    jschema = build_json_schema(df)
    with open(schema_path, "w", encoding="utf-8") as f:
        json.dump(jschema, f, ensure_ascii=False, indent=2)

    print("Generated:")
    print(" - " + csv_path)
    print(" - " + parquet_path)
    print(" - " + dict_path)
    print(" - " + schema_path)


if __name__ == "__main__":
    main()
