#!/usr/bin/env python3
import csv
import json
import os
import random
import math
from datetime import datetime
from collections import defaultdict

random.seed(42)

BASE_DIR = "/workspace/data/socio_political_demographic"
DEM_DIR = os.path.join(BASE_DIR, "demographics")
IND_DIR = os.path.join(BASE_DIR, "industrial")
POL_DIR = os.path.join(BASE_DIR, "policy")
PER_DIR = os.path.join(BASE_DIR, "perception")
AGG_DIR = os.path.join(BASE_DIR, "aggregates")
META_DIR = os.path.join(BASE_DIR, "metadata")

YEAR = 2025

# Nigeria states including FCT
STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno",
    "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "Gombe", "Imo", "Jigawa",
    "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger",
    "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe",
    "Zamfara", "FCT"
]

# Approximate areas in km^2 (fabricated but plausible, compiled for realism)
STATE_AREAS_KM2 = {
    "Abia": 6320, "Adamawa": 36917, "Akwa Ibom": 7081, "Anambra": 4865, "Bauchi": 49119,
    "Bayelsa": 10773, "Benue": 34059, "Borno": 70898, "Cross River": 20156, "Delta": 17698,
    "Ebonyi": 6353, "Edo": 17802, "Ekiti": 6353, "Enugu": 7161, "Gombe": 18768, "Imo": 5530,
    "Jigawa": 23154, "Kaduna": 46053, "Kano": 20131, "Katsina": 24192, "Kebbi": 36800,
    "Kogi": 29833, "Kwara": 36825, "Lagos": 3577, "Nasarawa": 27117, "Niger": 76363,
    "Ogun": 16762, "Ondo": 15500, "Osun": 9251, "Oyo": 28454, "Plateau": 30913,
    "Rivers": 11077, "Sokoto": 25973, "Taraba": 54473, "Yobe": 45502, "Zamfara": 39762,
    "FCT": 7315
}

# Approximate population weights (fabricated, skewing to known large states)
BASE_POP_WEIGHTS = {
    "Lagos": 0.125, "Kano": 0.095, "Kaduna": 0.05, "Rivers": 0.045, "Oyo": 0.05, "Katsina": 0.038,
    "Bauchi": 0.033, "Benue": 0.03, "Borno": 0.032, "Delta": 0.032, "Niger": 0.025, "Ogun": 0.028,
    "Anambra": 0.03, "Akwa Ibom": 0.03, "Imo": 0.025, "Abia": 0.02, "Edo": 0.02, "Kogi": 0.02,
    "Plateau": 0.018, "Kwara": 0.017, "Sokoto": 0.02, "Zamfara": 0.017, "Adamawa": 0.02,
    "Ondo": 0.022, "Osun": 0.02, "Enugu": 0.018, "Jigawa": 0.024, "Gombe": 0.014, "Taraba": 0.017,
    "Yobe": 0.016, "Ebonyi": 0.013, "Bayelsa": 0.01, "Cross River": 0.017, "Kebbi": 0.017,
    "Nasarawa": 0.016, "FCT": 0.027
}

# Actual LGA lists for some key areas; for others we'll fabricate names
LAGOS_LGAS = [
    "Agege", "Ajeromi-Ifelodun", "Alimosho", "Amuwo-Odofin", "Apapa", "Badagry", "Epe",
    "Eti-Osa", "Ibeju-Lekki", "Ifako-Ijaiye", "Ikeja", "Ikorodu", "Kosofe", "Lagos Island",
    "Lagos Mainland", "Mushin", "Ojo", "Oshodi-Isolo", "Shomolu", "Surulere"
]
FCT_LGAS = ["Abaji", "Abuja Municipal", "Bwari", "Gwagwalada", "Kuje", "Kwali"]

# Approximate LGA counts (fabricated where unknown, aligned to common knowledge where possible)
STATE_LGA_COUNTS = {
    "Lagos": 20, "FCT": 6, "Kano": 44, "Rivers": 23, "Oyo": 33, "Kaduna": 23, "Delta": 25,
    "Edo": 18, "Imo": 27, "Enugu": 17, "Anambra": 21, "Abia": 17, "Ogun": 20, "Ondo": 18,
    "Osun": 30, "Benue": 23, "Kogi": 21, "Kwara": 16, "Niger": 25, "Taraba": 16, "Plateau": 17,
    "Nasarawa": 13, "Gombe": 11, "Bauchi": 20, "Yobe": 17, "Jigawa": 27, "Katsina": 34,
    "Kebbi": 21, "Sokoto": 23, "Zamfara": 14, "Adamawa": 21, "Akwa Ibom": 31, "Bayelsa": 8,
    "Borno": 27, "Cross River": 18, "Ebonyi": 13, "Ekiti": 16
}

MAJOR_INDUSTRIAL_CLUSTERS = [
    {"name": "Ikeja Industrial Estate", "state": "Lagos", "lga": "Ikeja", "type": "Industrial Estate", "sector_focus": "Mixed Manufacturing", "lat": 6.6018, "lon": 3.3515},
    {"name": "Apapa Port Zone", "state": "Lagos", "lga": "Apapa", "type": "Port/Logistics", "sector_focus": "Logistics", "lat": 6.4450, "lon": 3.3580},
    {"name": "Lekki Free Trade Zone", "state": "Lagos", "lga": "Ibeju-Lekki", "type": "Free Trade Zone", "sector_focus": "Petrochemicals/Manufacturing", "lat": 6.4300, "lon": 3.6050},
    {"name": "Agbara Industrial Estate", "state": "Ogun", "lga": "Ado-Odo/Ota", "type": "Industrial Estate", "sector_focus": "FMCG/Manufacturing", "lat": 6.5360, "lon": 3.0490},
    {"name": "Sango-Ota Industrial Cluster", "state": "Ogun", "lga": "Ado-Odo/Ota", "type": "Industrial Cluster", "sector_focus": "Mixed Manufacturing", "lat": 6.6980, "lon": 3.2513},
    {"name": "Nnewi Industrial Cluster", "state": "Anambra", "lga": "Nnewi North", "type": "Industrial Cluster", "sector_focus": "Automotive/Manufacturing", "lat": 6.0197, "lon": 6.9100},
    {"name": "Onitsha Industrial/Commercial Zone", "state": "Anambra", "lga": "Onitsha North", "type": "Commercial/Industrial", "sector_focus": "Trading/Manufacturing", "lat": 6.1667, "lon": 6.7833},
    {"name": "Ariaria/Osisioma Industrial Area", "state": "Abia", "lga": "Aba North", "type": "Industrial/Market", "sector_focus": "Light Manufacturing/Leather", "lat": 5.1126, "lon": 7.3733},
    {"name": "Port Harcourt Industrial Area", "state": "Rivers", "lga": "Obio/Akpor", "type": "Industrial Area", "sector_focus": "Oil & Gas Services", "lat": 4.8156, "lon": 7.0498},
    {"name": "Kano Industrial Area (Bompai/Sharada/Challawa)", "state": "Kano", "lga": "Kano Municipal", "type": "Industrial Area", "sector_focus": "Textiles/Chemicals", "lat": 12.0000, "lon": 8.5167},
    {"name": "Kaduna Industrial Area", "state": "Kaduna", "lga": "Kaduna North", "type": "Industrial Area", "sector_focus": "Textiles/Agro", "lat": 10.5167, "lon": 7.4333},
    {"name": "Warri Industrial/Logistics Area", "state": "Delta", "lga": "Udu", "type": "Industrial/Logistics", "sector_focus": "Oil & Gas Services", "lat": 5.5167, "lon": 5.7500},
    {"name": "Aba Mega Mall & Adjacent Industrial", "state": "Abia", "lga": "Aba South", "type": "Commercial/Industrial", "sector_focus": "Retail/Light Manufacturing", "lat": 5.1066, "lon": 7.3667}
]

SECTORS = ["Manufacturing", "Trade", "Services", "Agriculture", "ICT", "Energy"]
STAKEHOLDERS = ["Industrial Manager", "Community Leader", "DisCo Official", "Policymaker", "Engineer", "Academic", "Investor"]
INDUSTRY_TYPES = ["FMCG", "Cement", "Textile", "Food Processing", "Oil & Gas Services", "Hospitality", "Retail", "Automotive"]

os.makedirs(DEM_DIR, exist_ok=True)
os.makedirs(IND_DIR, exist_ok=True)
os.makedirs(POL_DIR, exist_ok=True)
os.makedirs(PER_DIR, exist_ok=True)
os.makedirs(AGG_DIR, exist_ok=True)
os.makedirs(META_DIR, exist_ok=True)

def normalize_weights(weights_dict):
    total = sum(weights_dict.get(s, 0.0) for s in STATES)
    remaining_states = [s for s in STATES if s not in weights_dict]
    remaining_weight = max(0.0, 1.0 - total)
    even_share = remaining_weight / len(remaining_states) if remaining_states else 0.0
    final = {s: weights_dict.get(s, 0.0) for s in STATES}
    for s in remaining_states:
        final[s] = even_share
    # If rounding drift, renormalize
    ssum = sum(final.values())
    return {k: v / ssum for k, v in final.items()}

POP_WEIGHTS = normalize_weights(BASE_POP_WEIGHTS)

NATIONAL_POP = 230_000_000  # fabricated national population baseline

# Urbanization baseline by state (fabricated with plausible skews)
URBAN_BASELINE = {
    "Lagos": 0.88, "FCT": 0.80, "Rivers": 0.62, "Oyo": 0.62, "Kano": 0.56, "Kaduna": 0.56,
    "Ogun": 0.58, "Anambra": 0.63, "Abia": 0.62, "Delta": 0.60, "Edo": 0.62, "Imo": 0.61
}

# LGA names mapping for a few states
KNOWN_LGAS = {
    "Lagos": LAGOS_LGAS,
    "FCT": FCT_LGAS
}

# Utility to fabricate LGA names for a state

def fabricate_lgas_for_state(state: str, count: int):
    if state in KNOWN_LGAS:
        lgas = KNOWN_LGAS[state]
        # If count differs (shouldn't), trim or extend
        if len(lgas) >= count:
            return lgas[:count], [False] * count
        else:
            extra = [f"{state} LGA {i+1}" for i in range(count - len(lgas))]
            return lgas + extra, ([False] * len(lgas)) + ([True] * len(extra))
    else:
        return [f"{state} LGA {i+1}" for i in range(count)], [True] * count

# Build per-state base data
STATE_DATA = {}
for state in STATES:
    pop = int(NATIONAL_POP * POP_WEIGHTS[state])
    area = STATE_AREAS_KM2.get(state, random.randint(6000, 60000))
    dens = pop / area if area > 0 else 0
    urb_share = URBAN_BASELINE.get(state, random.uniform(0.35, 0.65))
    # growth rates (annual %) fabricated
    urb_growth = round(random.uniform(1.5, 4.0), 2)
    rur_growth = round(random.uniform(0.5, 2.5), 2)
    STATE_DATA[state] = {
        "population": pop,
        "area_km2": area,
        "density": dens,
        "urban_share": urb_share,
        "rural_share": max(0.0, 1.0 - urb_share),
        "urban_growth_pct": urb_growth,
        "rural_growth_pct": rur_growth
    }

# Generate LGA distributions
STATE_TO_LGAS = {}
STATE_TO_LGA_SYNTH = {}
for state in STATES:
    count = STATE_LGA_COUNTS.get(state, random.randint(12, 30))
    lgas, synth_flags = fabricate_lgas_for_state(state, count)
    STATE_TO_LGAS[state] = lgas
    STATE_TO_LGA_SYNTH[state] = synth_flags

# Split state population/area to LGAs via Dirichlet weights

def dirichlet_split(total: float, parts: int):
    # alpha parameter > 0; use 1.0 for flat, skew slightly with 0.9-1.2
    alpha = [random.uniform(0.9, 1.2) for _ in range(parts)]
    samples = [random.gammavariate(a, 1.0) for a in alpha]
    ssum = sum(samples)
    return [total * (x / ssum) for x in samples]

# Write demographics/state-level
state_csv_path = os.path.join(DEM_DIR, "state_demographics.csv")
with open(state_csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow([
        "state", "year", "population_estimate", "area_km2", "population_density_per_km2",
        "urban_population_share", "rural_population_share", "urban_growth_rate_pct",
        "rural_growth_rate_pct", "source", "is_fabricated"
    ])
    for state, d in STATE_DATA.items():
        w.writerow([
            state, YEAR, d["population"], d["area_km2"], round(d["density"], 2),
            round(d["urban_share"], 3), round(d["rural_share"], 3), d["urban_growth_pct"],
            d["rural_growth_pct"], "NBS/NPCom (fabricated synthesis)", True
        ])

# Write demographics/LGA-level
lga_csv_path = os.path.join(DEM_DIR, "lga_demographics.csv")
with open(lga_csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow([
        "state", "lga", "year", "population_estimate", "area_km2", "population_density_per_km2",
        "is_synthetic_lga", "urban_population_share", "rural_population_share", "notes", "source",
        "is_fabricated"
    ])
    for state in STATES:
        lgas = STATE_TO_LGAS[state]
        synth_flags = STATE_TO_LGA_SYNTH[state]
        pop_splits = dirichlet_split(STATE_DATA[state]["population"], len(lgas))
        area_splits = dirichlet_split(STATE_DATA[state]["area_km2"], len(lgas))
        for i, lga in enumerate(lgas):
            pop_i = int(pop_splits[i])
            area_i = max(1.0, area_splits[i])
            dens_i = pop_i / area_i
            urb_share_i = min(0.95, max(0.1, random.gauss(STATE_DATA[state]["urban_share"], 0.05)))
            w.writerow([
                state, lga, YEAR, pop_i, round(area_i, 2), round(dens_i, 2), synth_flags[i],
                round(urb_share_i, 3), round(1 - urb_share_i, 3),
                ("Fabricated LGA name" if synth_flags[i] else "Actual LGA"),
                "NBS/NPCom (fabricated synthesis)", True
            ])

# Industrial clusters: expand base list and add a few synthetic hubs
industrial_rows = []
for c in MAJOR_INDUSTRIAL_CLUSTERS:
    row = {
        **c,
        "num_large_tenants_estimate": random.randint(10, 120),
        "grid_power_reliability_score": round(random.uniform(1.5, 3.8), 1),  # 1-5
        "captive_power_presence": random.random() < 0.7,
        "gas_supply_proximity_km": round(random.uniform(1.0, 60.0), 1),
        "notes": "Seeded from known hubs; parameters fabricated",
        "source": "CAC/State Investment Bureaus (fabricated synthesis)",
        "is_fabricated": True
    }
    industrial_rows.append(row)

# Add one synthetic industrial estate per top-10 population states if not present
pop_ranked = sorted(STATES, key=lambda s: STATE_DATA[s]["population"], reverse=True)
for state in pop_ranked[:10]:
    if not any(r["state"] == state for r in industrial_rows):
        industrial_rows.append({
            "name": f"{state} Industrial Estate",
            "state": state,
            "lga": STATE_TO_LGAS[state][0],
            "type": "Industrial Estate",
            "sector_focus": "Mixed Manufacturing",
            "lat": "",
            "lon": "",
            "num_large_tenants_estimate": random.randint(8, 60),
            "grid_power_reliability_score": round(random.uniform(1.7, 3.6), 1),
            "captive_power_presence": random.random() < 0.6,
            "gas_supply_proximity_km": round(random.uniform(5.0, 80.0), 1),
            "notes": "Synthetic anchor estate for modeling",
            "source": "CAC/State Investment Bureaus (fabricated synthesis)",
            "is_fabricated": True
        })

clusters_csv = os.path.join(IND_DIR, "industrial_clusters.csv")
with open(clusters_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow([
        "name", "state", "lga", "type", "sector_focus", "lat", "lon",
        "num_large_tenants_estimate", "grid_power_reliability_score", "captive_power_presence",
        "gas_supply_proximity_km", "notes", "source", "is_fabricated"
    ])
    for r in industrial_rows:
        w.writerow([
            r["name"], r["state"], r["lga"], r["type"], r["sector_focus"], r["lat"], r["lon"],
            r["num_large_tenants_estimate"], r["grid_power_reliability_score"],
            r["captive_power_presence"], r["gas_supply_proximity_km"], r["notes"], r["source"],
            r["is_fabricated"]
        ])

# SME by state & sector
sme_csv = os.path.join(IND_DIR, "sme_by_state_sector.csv")
with open(sme_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow([
        "state", "sector", "registered_smes_estimate", "micro_enterprises_estimate",
        "small_enterprises_estimate", "medium_enterprises_estimate", "year", "source",
        "is_fabricated"
    ])
    for state in STATES:
        pop = STATE_DATA[state]["population"]
        density = STATE_DATA[state]["density"]
        urban = STATE_DATA[state]["urban_share"]
        # Base SMEs scale with population and urbanization (fabricated formula)
        base_total = int((pop / 60) * (0.7 + 0.6 * urban) * (0.8 + 0.2 * min(density / 2000, 1)))
        # Avoid absurdly large numbers; cap sensibly
        base_total = min(base_total, 800_000)
        # Sector weights (fabricated)
        if state in ["Lagos", "Ogun", "Rivers", "Anambra", "Abia", "Kano", "Kaduna", "Oyo", "FCT", "Delta", "Edo"]:
            weights = {
                "Manufacturing": 0.22, "Trade": 0.28, "Services": 0.28, "Agriculture": 0.10, "ICT": 0.09, "Energy": 0.03
            }
        else:
            weights = {
                "Manufacturing": 0.16, "Trade": 0.25, "Services": 0.24, "Agriculture": 0.28, "ICT": 0.05, "Energy": 0.02
            }
        # Normalize just in case
        ssum = sum(weights.values())
        weights = {k: v / ssum for k, v in weights.items()}
        for sector in SECTORS:
            total = int(base_total * weights[sector] * random.uniform(0.85, 1.15))
            micro = int(total * 0.86)
            small = int(total * 0.12)
            medium = max(0, total - micro - small)
            w.writerow([state, sector, total, micro, small, medium, YEAR,
                        "CAC/NASSI/State Bureaus (fabricated synthesis)", True])

# Policy & Regulatory datasets
policies = [
    {
        "document_title": "National Renewable Energy and Energy Efficiency Policy (NREEEP)",
        "issuing_agency": "Federal Ministry of Power",
        "year": 2015,
        "policy_area": "Renewable Energy",
        "summary": "Sets targets and frameworks for renewable energy adoption and efficiency measures.",
        "url": "https://power.gov.ng/",  # placeholder
        "status": "In Force",
        "source": "FMP (summary fabricated)",
        "is_fabricated": True
    },
    {
        "document_title": "Renewable Energy Master Plan (REMP)",
        "issuing_agency": "Federal Ministry of Power",
        "year": 2012,
        "policy_area": "Renewable Energy",
        "summary": "Long-term roadmap for scaling renewable energy contributions to national mix.",
        "url": "https://power.gov.ng/",
        "status": "Guidance",
        "source": "FMP (summary fabricated)",
        "is_fabricated": True
    },
    {
        "document_title": "National Gas Policy",
        "issuing_agency": "Federal Ministry of Petroleum Resources",
        "year": 2017,
        "policy_area": "Gas Utilization",
        "summary": "Promotes domestic gas utilization for power and industry; pricing frameworks.",
        "url": "https://petroleumresources.gov.ng/",
        "status": "In Force",
        "source": "FMPR (summary fabricated)",
        "is_fabricated": True
    },
    {
        "document_title": "Domestic Gas Supply Obligation (DGSO)",
        "issuing_agency": "Federal Ministry of Petroleum Resources",
        "year": 2008,
        "policy_area": "Gas Supply",
        "summary": "Obligates gas suppliers to allocate a portion to the domestic market.",
        "url": "https://petroleumresources.gov.ng/",
        "status": "Operational",
        "source": "FMPR (summary fabricated)",
        "is_fabricated": True
    },
    {
        "document_title": "NERC Mini-Grid Regulation",
        "issuing_agency": "Nigerian Electricity Regulatory Commission",
        "year": 2016,
        "policy_area": "Mini-Grid",
        "summary": "Framework for 0-1 MW mini-grids (registration/permit), interconnection, tariffs.",
        "url": "https://nerc.gov.ng/",
        "status": "In Force",
        "source": "NERC (summary fabricated)",
        "is_fabricated": True
    },
    {
        "document_title": "Eligible Customer Regulation",
        "issuing_agency": "Nigerian Electricity Regulatory Commission",
        "year": 2017,
        "policy_area": "Market Access",
        "summary": "Allows large customers to purchase power directly from generators.",
        "url": "https://nerc.gov.ng/",
        "status": "In Force",
        "source": "NERC (summary fabricated)",
        "is_fabricated": True
    }
]

policies_csv = os.path.join(POL_DIR, "policies.csv")
with open(policies_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["document_title", "issuing_agency", "year", "policy_area", "summary", "url", "status", "source", "is_fabricated"])
    for p in policies:
        w.writerow([p[k] for k in ["document_title", "issuing_agency", "year", "policy_area", "summary", "url", "status", "source", "is_fabricated"]])

import_duties = [
    {"equipment_category": "Solid Oxide Fuel Cells", "hs_code_example": "8501/8502 (approx)", "import_duty_pct": 5.0, "vat_pct": 7.5, "levy_pct": 0.0, "notes": "Indicative; verify CET schedule", "source": "NCS/ECOWAS CET (fabricated)", "is_fabricated": True},
    {"equipment_category": "Gas Engines/Generators", "hs_code_example": "8502", "import_duty_pct": 10.0, "vat_pct": 7.5, "levy_pct": 0.0, "notes": "Indicative", "source": "NCS (fabricated)", "is_fabricated": True},
    {"equipment_category": "Gas Turbines", "hs_code_example": "8411", "import_duty_pct": 5.0, "vat_pct": 7.5, "levy_pct": 0.0, "notes": "Indicative", "source": "NCS (fabricated)", "is_fabricated": True},
    {"equipment_category": "Solar PV Modules", "hs_code_example": "8541", "import_duty_pct": 0.0, "vat_pct": 7.5, "levy_pct": 0.0, "notes": "Indicative duty reliefs may apply", "source": "NCS (fabricated)", "is_fabricated": True},
    {"equipment_category": "Inverters/Power Electronics", "hs_code_example": "8504", "import_duty_pct": 5.0, "vat_pct": 7.5, "levy_pct": 0.0, "notes": "Indicative", "source": "NCS (fabricated)", "is_fabricated": True},
    {"equipment_category": "Batteries (Li-ion)", "hs_code_example": "8507", "import_duty_pct": 5.0, "vat_pct": 7.5, "levy_pct": 0.0, "notes": "Indicative; EPR fees may apply", "source": "NCS (fabricated)", "is_fabricated": True},
    {"equipment_category": "Transformers/Switchgear", "hs_code_example": "8504/8537", "import_duty_pct": 10.0, "vat_pct": 7.5, "levy_pct": 0.0, "notes": "Indicative", "source": "NCS (fabricated)", "is_fabricated": True}
]

duties_csv = os.path.join(POL_DIR, "import_duties.csv")
with open(duties_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["equipment_category", "hs_code_example", "import_duty_pct", "vat_pct", "levy_pct", "notes", "source", "is_fabricated"])
    for d in import_duties:
        w.writerow([d[k] for k in ["equipment_category", "hs_code_example", "import_duty_pct", "vat_pct", "levy_pct", "notes", "source", "is_fabricated"]])

mini_grid_params = [
    {"parameter": "Registration Threshold", "value": 100, "unit": "kW", "notes": "<=100kW registration", "source": "NERC (fabricated summary)", "is_fabricated": True},
    {"parameter": "Permit Threshold", "value": "100kW-1MW", "unit": "range", "notes": "Permit required", "source": "NERC (fabricated summary)", "is_fabricated": True},
    {"parameter": "License Threshold", "value": ">1MW", "unit": "range", "notes": "Generation license", "source": "NERC (fabricated summary)", "is_fabricated": True},
    {"parameter": "Interconnection", "value": "Allowed", "unit": "text", "notes": "With Disco agreement", "source": "NERC (fabricated summary)", "is_fabricated": True}
]

mini_csv = os.path.join(POL_DIR, "mini_grid_regulations.csv")
with open(mini_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["parameter", "value", "unit", "notes", "source", "is_fabricated"])
    for r in mini_grid_params:
        w.writerow([r[k] for k in ["parameter", "value", "unit", "notes", "source", "is_fabricated"]])

# Social perception synthetic survey
num_respondents = 2000
survey_csv = os.path.join(PER_DIR, "social_perception_survey.csv")
with open(survey_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow([
        "respondent_id", "stakeholder_type", "state", "lga", "industry_type", "awareness_score_1_5",
        "acceptance_score_1_5", "perceived_benefits", "perceived_risks", "capex_concern_1_5",
        "opex_concern_1_5", "reliability_concern_1_5", "regulatory_barrier_score_1_5",
        "familiar_with_gas_price_volatility", "prefer_grid_integration", "prefer_isolated_minigrid",
        "purchase_intent_0_1", "comment", "source", "is_fabricated"
    ])
    for i in range(1, num_respondents + 1):
        state = random.choice(STATES)
        lga = random.choice(STATE_TO_LGAS[state])
        stakeholder = random.choice(STAKEHOLDERS)
        industry = random.choice(INDUSTRY_TYPES)
        # Awareness/acceptance skew higher in industrialized/urban states
        urb = STATE_DATA[state]["urban_share"]
        base = 2.6 + 2.0 * (urb - 0.5)
        awareness = min(5, max(1, int(round(random.gauss(base + 0.4, 0.9)))))
        acceptance = min(5, max(1, int(round(random.gauss(base, 0.9)))))
        capex = min(5, max(1, int(round(random.gauss(3.2, 0.8)))))
        opex = min(5, max(1, int(round(random.gauss(2.8, 0.8)))))
        reliability = min(5, max(1, int(round(random.gauss(3.1, 0.9)))))
        regulatory = min(5, max(1, int(round(random.gauss(3.0, 0.8)))))
        benefits = random.choice(["Lower OPEX", "Reliability", "Lower Emissions", "Long Life", "Scalable"])
        risks = random.choice(["Gas Price Volatility", "Technical Complexity", "Maintenance", "Capex", "Regulatory Risk"])
        vol = random.random() < 0.6
        grid_pref = random.random() < 0.55
        iso_pref = not grid_pref and (random.random() < 0.6)
        intent = 1 if (acceptance >= 3 and capex <= 3 and regulatory <= 3) else 0
        comment = ""
        w.writerow([
            f"R{i:05d}", stakeholder, state, lga, industry, awareness, acceptance, benefits, risks,
            capex, opex, reliability, regulatory, vol, grid_pref, iso_pref, intent, comment,
            "Primary (synthetic)", True
        ])

# Aggregated state-level summary
agg_csv = os.path.join(AGG_DIR, "state_summary.csv")
# First collect perception aggregates
perception_by_state = defaultdict(lambda: {
    "count": 0, "awareness_sum": 0, "acceptance_sum": 0, "regulatory_sum": 0
})

with open(survey_csv, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        s = row["state"]
        perception_by_state[s]["count"] += 1
        perception_by_state[s]["awareness_sum"] += int(row["awareness_score_1_5"])
        perception_by_state[s]["acceptance_sum"] += int(row["acceptance_score_1_5"])
        perception_by_state[s]["regulatory_sum"] += int(row["regulatory_barrier_score_1_5"])

# Industrial cluster counts by state
cluster_counts = defaultdict(int)
for r in industrial_rows:
    cluster_counts[r["state"]] += 1

# SME totals by state
sme_totals = defaultdict(int)
with open(sme_csv, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        sme_totals[row["state"]] += int(row["registered_smes_estimate"])

# Compute min/max for normalization
all_densities = [STATE_DATA[s]["density"] for s in STATES]
all_clusters = [cluster_counts[s] for s in STATES]
all_smes = [sme_totals[s] for s in STATES]

min_d, max_d = min(all_densities), max(all_densities)
min_c, max_c = min(all_clusters), max(all_clusters)
min_s, max_s = min(all_smes), max(all_smes)


def minmax(x, xmin, xmax):
    if xmax - xmin < 1e-9:
        return 0.0
    return (x - xmin) / (xmax - xmin)

with open(agg_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow([
        "state", "year", "population_estimate", "population_density_per_km2",
        "urban_population_share", "industrial_cluster_count", "sme_total_estimate",
        "avg_awareness", "avg_acceptance", "avg_regulatory_barrier", "sofc_adoption_potential_score",
        "recommended_strategy", "source", "is_fabricated"
    ])
    for state in STATES:
        pop = STATE_DATA[state]["population"]
        dens = STATE_DATA[state]["density"]
        urb = STATE_DATA[state]["urban_share"]
        clusters = cluster_counts[state]
        smes = sme_totals[state]
        p = perception_by_state[state]
        count = max(1, p["count"])
        avg_aw = p["awareness_sum"] / count
        avg_ac = p["acceptance_sum"] / count
        avg_reg = p["regulatory_sum"] / count
        score = (
            0.25 * minmax(dens, min_d, max_d)
            + 0.25 * minmax(clusters, min_c, max_c)
            + 0.20 * minmax(smes, min_s, max_s)
            + 0.15 * (avg_aw / 5.0)
            + 0.15 * (avg_ac / 5.0)
            - 0.10 * (avg_reg / 5.0)
        ) * 100.0
        score = max(0.0, min(100.0, score))
        if score >= 70:
            strategy = "Accelerate SOFC pilots with captive gas; pursue industrial parks first"
        elif score >= 50:
            strategy = "Target mixed industrial/commercial loads; pair with grid or mini-grids"
        else:
            strategy = "Focus on demos with anchor clients; build policy and awareness"
        w.writerow([
            state, YEAR, pop, round(dens, 2), round(urb, 3), clusters, smes,
            round(avg_aw, 2), round(avg_ac, 2), round(avg_reg, 2), round(score, 1), strategy,
            "Aggregated (fabricated synthesis)", True
        ])

# Manifest
manifest = {
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "year": YEAR,
    "datasets": {
        "demographics/state_demographics.csv": {
            "description": "State-level population, density, urban/rural shares (fabricated)",
            "records": len(STATES),
            "sources": ["NBS", "National Population Commission"],
            "fabricated": True
        },
        "demographics/lga_demographics.csv": {
            "description": "LGA-level population, density, urban/rural shares; synthetic LGAs flagged",
            "records": sum(len(STATE_TO_LGAS[s]) for s in STATES),
            "sources": ["NBS", "National Population Commission"],
            "fabricated": True
        },
        "industrial/industrial_clusters.csv": {
            "description": "Industrial clusters and estates with attributes (partially seeded, fabricated params)",
            "records": len(industrial_rows),
            "sources": ["CAC", "State Investment Bureaus"],
            "fabricated": True
        },
        "industrial/sme_by_state_sector.csv": {
            "description": "Registered SME estimates by state and sector (fabricated)",
            "records": len(STATES) * len(SECTORS),
            "sources": ["CAC", "NASME/NASSI", "State Investment Bureaus"],
            "fabricated": True
        },
        "policy/policies.csv": {
            "description": "Key national energy and gas policies (summaries fabricated)",
            "records": len(policies),
            "sources": ["FMP", "FMPR", "NERC"],
            "fabricated": True
        },
        "policy/import_duties.csv": {
            "description": "Indicative import duties for energy equipment (fabricated)",
            "records": len(import_duties),
            "sources": ["NCS", "ECOWAS CET"],
            "fabricated": True
        },
        "policy/mini_grid_regulations.csv": {
            "description": "Mini-grid regulatory parameters (fabricated summary)",
            "records": len(mini_grid_params),
            "sources": ["NERC"],
            "fabricated": True
        },
        "perception/social_perception_survey.csv": {
            "description": "Synthetic survey on SOFC awareness and acceptance",
            "records": num_respondents,
            "sources": ["Primary (Synthetic)"],
            "fabricated": True
        },
        "aggregates/state_summary.csv": {
            "description": "Aggregated state-level indicators and SOFC potential score",
            "records": len(STATES),
            "sources": ["Aggregated"],
            "fabricated": True
        }
    }
}

with open(os.path.join(META_DIR, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print("Dataset generation complete.")
