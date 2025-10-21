#!/usr/bin/env python3
import csv
import json
import math
import os
import random
from datetime import datetime
from typing import List, Dict, Any

# Seed for reproducibility
random.seed(42)

OUTPUT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

# Nigeria states and a small LGA sample per state (not exhaustive; illustrative)
NIGERIA_STATES = [
    "Abia","Adamawa","Akwa Ibom","Anambra","Bauchi","Bayelsa","Benue","Borno","Cross River","Delta",
    "Ebonyi","Edo","Ekiti","Enugu","FCT","Gombe","Imo","Jigawa","Kaduna","Kano","Katsina","Kebbi",
    "Kogi","Kwara","Lagos","Nasarawa","Niger","Ogun","Ondo","Osun","Oyo","Plateau","Rivers","Sokoto",
    "Taraba","Yobe","Zamfara"
]

STATE_TO_SAMPLE_LGAS = {
    "Lagos": ["Ikeja", "Eti-Osa", "Alimosho", "Lagos Island"],
    "Ogun": ["Ado-Odo/Ota", "Ijebu Ode", "Sagamu"],
    "Anambra": ["Nnewi North", "Awka South", "Onitsha North"],
    "FCT": ["Abuja Municipal", "Bwari"],
    "Rivers": ["Port Harcourt", "Obio/Akpor"],
    "Kano": ["Kano Municipal", "Tarauni", "Nasarawa"],
}

SECTORS = [
    "Agriculture", "Manufacturing", "Construction", "Trade", "ICT", "Finance", "Transportation", "Hospitality"
]

INDUSTRIAL_CLUSTERS = [
    {"name": "Ikeja Industrial Estate", "state": "Lagos", "lga": "Ikeja", "type": "Industrial Estate", "lat": 6.602, "lng": 3.351},
    {"name": "Agbara Industrial Estate", "state": "Ogun", "lga": "Ado-Odo/Ota", "type": "Industrial Estate", "lat": 6.538, "lng": 3.071},
    {"name": "Nnewi Manufacturing Cluster", "state": "Anambra", "lga": "Nnewi North", "type": "Manufacturing Hub", "lat": 6.018, "lng": 6.910},
    {"name": "Trans-Amadi Industrial Layout", "state": "Rivers", "lga": "Port Harcourt", "type": "Industrial Layout", "lat": 4.824, "lng": 7.036},
]

COMMERCIAL_BUILDINGS = [
    {"name": "Ikeja City Mall", "state": "Lagos", "lga": "Ikeja", "category": "Mall", "lat": 6.600, "lng": 3.342},
    {"name": "Jabi Lake Mall", "state": "FCT", "lga": "Abuja Municipal", "category": "Mall", "lat": 9.068, "lng": 7.441},
    {"name": "Eko Hotels & Suites", "state": "Lagos", "lga": "Eti-Osa", "category": "Hotel", "lat": 6.427, "lng": 3.421},
    {"name": "Tinapa Business Resort", "state": "Cross River", "lga": "Calabar Municipal", "category": "Commercial Complex", "lat": 4.984, "lng": 8.347},
]

POLICY_REGULATORY = [
    {
        "policy": "National Energy Policy",
        "issuer": "Federal Ministry of Power",
        "year": 2013,
        "focus": "Energy access, generation mix, renewable targets",
        "relevance_to_sofc": "Sets diversification and efficiency goals compatible with SOFC deployment",
        "source": "https://www.power.gov.ng/",  # placeholder landing page
    },
    {
        "policy": "Renewable Energy Master Plan",
        "issuer": "Federal Ministry of Power",
        "year": 2012,
        "focus": "Renewable penetration targets, enabling policies",
        "relevance_to_sofc": "Highlights clean energy pathways where SOFCs can complement",
        "source": "https://www.power.gov.ng/",  # placeholder
    },
    {
        "policy": "Nigeria Gas Master Plan",
        "issuer": "Federal Ministry of Petroleum Resources",
        "year": 2008,
        "focus": "Domestic gas supply obligation, gas to power, pricing",
        "relevance_to_sofc": "Prioritizes domestic gas utilization which can fuel SOFCs",
        "source": "https://www.petroleumresources.gov.ng/",  # placeholder
    },
    {
        "policy": "NERC Mini-Grid Regulation",
        "issuer": "NERC",
        "year": 2016,
        "focus": "Permitting, tariffs, interconnection for mini-grids",
        "relevance_to_sofc": "Framework for distributed generation projects including SOFC-based systems",
        "source": "https://nerc.gov.ng/",  # placeholder
    },
    {
        "policy": "Import Duty & VAT Schedule for Power Equipment",
        "issuer": "Nigeria Customs / FIRS",
        "year": 2020,
        "focus": "Tariff lines affecting generation equipment",
        "relevance_to_sofc": "Affects landed costs of SOFC stacks, balance of plant",
        "source": "https://customs.gov.ng/",  # placeholder
    },
]

# Utility functions

def ensure_dirs():
    subdirs = [
        "demographics", "industrial_commercial", "policy_regulatory", "social_perception", "metadata"
    ]
    for sd in subdirs:
        os.makedirs(os.path.join(OUTPUT_ROOT, sd), exist_ok=True)


def write_csv(path: str, rows: List[Dict[str, Any]]):
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def write_json(path: str, data: Any):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Demographics: population density, urban vs rural distribution, growth rates

def generate_demographics():
    demographics_rows: List[Dict[str, Any]] = []
    lga_rows: List[Dict[str, Any]] = []

    for state in NIGERIA_STATES:
        # Synthetic but plausible ranges
        area_km2 = random.uniform(3000, 75000)
        population_2020 = random.uniform(0.8, 16.0) * 1_000_000  # states vary widely
        population_2024 = population_2020 * random.uniform(1.04, 1.20)
        density_2024 = population_2024 / area_km2
        urban_share_2024 = random.uniform(0.30, 0.70)
        rural_share_2024 = 1 - urban_share_2024
        annual_growth_rate = (population_2024 / population_2020) ** (1/4) - 1

        demographics_rows.append({
            "state": state,
            "year": 2024,
            "area_km2": round(area_km2, 1),
            "population": int(population_2024),
            "population_density_per_km2": round(density_2024, 1),
            "urban_share": round(urban_share_2024, 3),
            "rural_share": round(rural_share_2024, 3),
            "annual_growth_rate": round(annual_growth_rate, 4),
            "source": "Synthetic; calibrated to NBS ranges"
        })

        # LGA samples
        lgas = STATE_TO_SAMPLE_LGAS.get(state, [])
        for lga in lgas:
            lga_population = population_2024 * random.uniform(0.02, 0.10)
            lga_area = area_km2 * random.uniform(0.01, 0.06)
            lga_density = lga_population / lga_area if lga_area > 0 else 0
            lga_urban_share = min(0.95, max(0.2, urban_share_2024 + random.uniform(-0.1, 0.15)))

            lga_rows.append({
                "state": state,
                "lga": lga,
                "year": 2024,
                "area_km2": round(lga_area, 1),
                "population": int(lga_population),
                "population_density_per_km2": round(lga_density, 1),
                "urban_share": round(lga_urban_share, 3),
                "rural_share": round(1 - lga_urban_share, 3),
                "source": "Synthetic; calibrated to NBS ranges"
            })

    write_csv(os.path.join(OUTPUT_ROOT, "demographics", "state_demographics_2024.csv"), demographics_rows)
    write_csv(os.path.join(OUTPUT_ROOT, "demographics", "lga_demographics_samples_2024.csv"), lga_rows)


# Industrial & commercial datasets

def generate_industrial_and_commercial():
    clusters_rows = []
    for c in INDUSTRIAL_CLUSTERS:
        clusters_rows.append({
            **c,
            "notes": "Hand-curated examples of major clusters",
            "source": "Public domain sources; verify with state investment bureaus"
        })

    buildings_rows = []
    for b in COMMERCIAL_BUILDINGS:
        buildings_rows.append({
            **b,
            "notes": "Representative large commercial sites relevant to baseload needs",
            "source": "Public domain sources"
        })

    write_csv(os.path.join(OUTPUT_ROOT, "industrial_commercial", "industrial_clusters.csv"), clusters_rows)
    write_csv(os.path.join(OUTPUT_ROOT, "industrial_commercial", "large_commercial_buildings.csv"), buildings_rows)


# SME data by sector and state (synthetic counts)

def generate_sme_data():
    rows = []
    for state in NIGERIA_STATES:
        total_smes = random.randint(5000, 120000)
        # distribute across sectors
        weights = [random.uniform(0.05, 0.2) for _ in SECTORS]
        s = sum(weights)
        weights = [w/s for w in weights]
        for sector, w in zip(SECTORS, weights):
            rows.append({
                "state": state,
                "sector": sector,
                "registered_smes": int(total_smes * w),
                "year": 2024,
                "source": "Synthetic; indicative; calibrate with CAC/NASME when available"
            })

    write_csv(os.path.join(OUTPUT_ROOT, "industrial_commercial", "smes_by_sector_state_2024.csv"), rows)


# Policy & regulatory: structured summary rows

def generate_policy_regulatory():
    rows = []
    for p in POLICY_REGULATORY:
        rows.append({
            "policy": p["policy"],
            "issuer": p["issuer"],
            "year": p["year"],
            "focus": p["focus"],
            "relevance_to_sofc": p["relevance_to_sofc"],
            "source_url": p["source"],
            "note": "Verify official document versions and sections"
        })
    write_csv(os.path.join(OUTPUT_ROOT, "policy_regulatory", "policies_regulations.csv"), rows)


# Social perception: synthetic survey-like dataset

def generate_social_perception(n_samples: int = 1000):
    stakeholders = [
        "Industrial Manager", "Community Leader", "DisCo Official", "Policymaker", "Academic/Researcher", "Investor"
    ]
    regions = NIGERIA_STATES

    def likert(mu: float, sigma: float = 0.9):
        # Generate 1-5 scale rounded
        val = random.gauss(mu, sigma)
        return int(min(5, max(1, round(val))))

    rows = []
    for i in range(n_samples):
        role = random.choice(stakeholders)
        state = random.choice(regions)
        awareness = likert(3.0)
        acceptance = likert(3.2 if role in ("Industrial Manager", "Investor") else 2.8)
        perceived_cost_barrier = likert(3.6)
        perceived_reliability_benefit = likert(3.4)
        environmental_concern = likert(3.1)
        policy_support_expectation = likert(3.3)
        willingness_to_pilot = likert(3.0 if role != "Policymaker" else 2.7)

        rows.append({
            "respondent_id": f"R{i+1:04d}",
            "role": role,
            "state": state,
            "awareness_sofc": awareness,
            "acceptance_sofc": acceptance,
            "perceived_cost_barrier": perceived_cost_barrier,
            "perceived_reliability_benefit": perceived_reliability_benefit,
            "environmental_concern": environmental_concern,
            "policy_support_expectation": policy_support_expectation,
            "willingness_to_pilot": willingness_to_pilot,
            "year": 2024,
            "source": "Synthetic survey; use for scenario analysis only"
        })

    write_csv(os.path.join(OUTPUT_ROOT, "social_perception", "social_perception_survey_synthetic_2024.csv"), rows)


# Metadata for documentation and provenance

def write_metadata():
    meta = {
        "topic": "Harnessing Domestic Gas for Power: SOFCs in Nigeria",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "datasets": [
            {"path": "demographics/state_demographics_2024.csv", "description": "State-level population, density, urban/rural shares, growth, synthetic"},
            {"path": "demographics/lga_demographics_samples_2024.csv", "description": "Sample LGAs with demographic indicators, synthetic"},
            {"path": "industrial_commercial/industrial_clusters.csv", "description": "Key industrial clusters with coordinates"},
            {"path": "industrial_commercial/large_commercial_buildings.csv", "description": "Representative malls, hotels, complexes with coordinates"},
            {"path": "industrial_commercial/smes_by_sector_state_2024.csv", "description": "SMEs by sector per state, synthetic"},
            {"path": "policy_regulatory/policies_regulations.csv", "description": "Structured list of policies and regulations with links"},
            {"path": "social_perception/social_perception_survey_synthetic_2024.csv", "description": "Synthetic survey responses across roles and states"},
        ],
        "notes": [
            "Demographic and SME figures are synthetic approximations. Replace with NBS/CAC when available.",
            "Policy URLs are placeholders to institutional portals. Insert direct document links when collated.",
            "Coordinates are approximate for illustration; verify with GIS sources before siting decisions.",
        ],
        "sources": {
            "NBS": "https://nigerianstat.gov.ng/",
            "National Population Commission": "https://nationalpopulation.gov.ng/",
            "CAC": "https://www.cac.gov.ng/",
            "NASME": "https://nasme.org/",
            "NERC": "https://nerc.gov.ng/",
            "Federal Ministry of Power": "https://www.power.gov.ng/",
            "Federal Ministry of Petroleum Resources": "https://www.petroleumresources.gov.ng/",
            "Nigeria Customs": "https://customs.gov.ng/",
        }
    }
    write_json(os.path.join(OUTPUT_ROOT, "metadata", "dataset_manifest.json"), meta)


def main():
    ensure_dirs()
    generate_demographics()
    generate_industrial_and_commercial()
    generate_sme_data()
    generate_policy_regulatory()
    generate_social_perception(n_samples=1500)
    write_metadata()
    print(f"Datasets generated under: {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
