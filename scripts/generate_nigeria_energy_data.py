#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generator: Nigerian Energy & Resource Data (fabricated, seeded)

Datasets produced under /data:
- electricity/
  - generation_capacity.csv
  - neso_daily_load_allocation.csv
  - grid_reliability_saidi_saifi.csv
  - electricity_tariffs.csv
- fossil_fuels/
  - gas_reserves_production.csv
  - gas_flare_sites.csv
  - gas_flare_sites.geojson
  - gas_flare_daily.csv
  - gas_pipeline_network.geojson
  - fuel_prices_monthly.csv
  - gas_pipeline_quality_composition.csv
- renewables/
  - agricultural_waste_by_state.csv
  - livestock_population_by_state.csv

For every *.csv and *.geojson, a sibling *.metadata.json is created describing schema, units, and sources.
"""

from __future__ import annotations

import csv
import json
import math
import os
from pathlib import Path
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import random
from typing import Dict, List, Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ELEC_DIR = DATA_DIR / "electricity"
FOSSIL_DIR = DATA_DIR / "fossil_fuels"
REN_DIR = DATA_DIR / "renewables"
GIS_DIR = DATA_DIR / "gis"

DEFAULT_SEED = 20251021
NOW_ISO = datetime.utcnow().isoformat()

# --- Reference lists ---
NIGERIA_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno",
    "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "FCT Abuja", "Gombe",
    "Imo", "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara",
    "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo", "Plateau",
    "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara"
]

DISCOS = [
    "Abuja DISCO", "Benin DISCO", "Eko DISCO", "Enugu DISCO", "Ibadan DISCO",
    "Ikeja DISCO", "Jos DISCO", "Kaduna DISCO", "Kano DISCO", "Port Harcourt DISCO", "Yola DISCO"
]

REGIONS = {
    "North Central": ["Benue", "Kogi", "Kwara", "Nasarawa", "Niger", "Plateau", "FCT Abuja"],
    "North East": ["Adamawa", "Bauchi", "Borno", "Gombe", "Taraba", "Yobe"],
    "North West": ["Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Sokoto", "Zamfara"],
    "South East": ["Abia", "Anambra", "Ebonyi", "Enugu", "Imo"],
    "South South": ["Akwa Ibom", "Bayelsa", "Cross River", "Delta", "Edo", "Rivers"],
    "South West": ["Ekiti", "Lagos", "Ogun", "Ondo", "Osun", "Oyo"],
}

# For DISCO to rough macro-region mapping (not exact)
DISCO_REGION = {
    "Abuja DISCO": "North Central",
    "Benin DISCO": "South South",
    "Eko DISCO": "South West",
    "Enugu DISCO": "South East",
    "Ibadan DISCO": "South West",
    "Ikeja DISCO": "South West",
    "Jos DISCO": "North Central",
    "Kaduna DISCO": "North West",
    "Kano DISCO": "North West",
    "Port Harcourt DISCO": "South South",
    "Yola DISCO": "North East",
}

ENERGY_SOURCES = ["Gas", "Hydro", "Solar", "Wind", "Biomass", "Others"]
TARIFF_CUSTOMERS = ["Residential", "Commercial", "Industrial", "Premium"]

# Niger Delta approximate flare site coordinates (fabricated but plausible)
FLARE_SITES = [
    {"name": "Escravos", "lat": 5.605, "lon": 5.198},
    {"name": "Forcados", "lat": 5.300, "lon": 5.450},
    {"name": "Bonny", "lat": 4.457, "lon": 7.170},
    {"name": "Brass", "lat": 4.318, "lon": 6.241},
    {"name": "Ebocha", "lat": 5.558, "lon": 6.666},
    {"name": "Ughelli", "lat": 5.493, "lon": 6.006},
    {"name": "Ogbogu", "lat": 5.288, "lon": 6.604},
    {"name": "Utorogu", "lat": 5.416, "lon": 5.871},
    {"name": "Agbada", "lat": 4.963, "lon": 6.400},
    {"name": "Nembe", "lat": 4.536, "lon": 6.404},
    {"name": "Obite", "lat": 4.965, "lon": 6.656},
    {"name": "Soku", "lat": 4.625, "lon": 6.701},
    {"name": "Bonga Offshore", "lat": 4.250, "lon": 5.200},
    {"name": "Akpo Offshore", "lat": 4.300, "lon": 5.700},
    {"name": "Egina Offshore", "lat": 4.350, "lon": 6.000},
]

# Pipeline nodes for toy network
PIPELINE_NODES = {
    "Lagos": (6.5244, 3.3792),
    "Warri": (5.5544, 5.7932),
    "Escravos": (5.6050, 5.1980),
    "Port Harcourt": (4.8156, 7.0498),
    "Abuja": (9.0765, 7.3986),
    "Kaduna": (10.5105, 7.4165),
    "Kano": (12.0022, 8.5919),
    "Benin City": (6.3350, 5.6037),
    "Ajaokuta": (7.5649, 6.6548),
}

PIPELINE_SEGMENTS = [
    ("Escravos", "Warri"),
    ("Warri", "Benin City"),
    ("Benin City", "Lagos"),
    ("Warri", "Port Harcourt"),
    ("Warri", "Ajaokuta"),
    ("Ajaokuta", "Abuja"),
    ("Abuja", "Kaduna"),
    ("Kaduna", "Kano"),
]

@dataclass
class MetaField:
    name: str
    description: str
    unit: str | None = None
    dtype: str | None = None


def ensure_dirs() -> None:
    for d in [DATA_DIR, ELEC_DIR, FOSSIL_DIR, REN_DIR, GIS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, fieldnames: List[str], rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_geojson(path: Path, feature_collection: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(feature_collection, f, ensure_ascii=False)


def write_metadata(data_path: Path, *, title: str, description: str,
                   fields: List[MetaField], sources: List[str], 
                   notes: str | None = None, seed: int = DEFAULT_SEED) -> None:
    meta = {
        "title": title,
        "description": description,
        "data_file": str(data_path.relative_to(ROOT)),
        "generated_at_utc": NOW_ISO,
        "seed": seed,
        "schema": [
            {"name": f.name, "description": f.description, "unit": f.unit, "dtype": f.dtype}
            for f in fields
        ],
        "sources": sources,
        "notes": notes,
        "license": "CC-BY-4.0 (fabricated synthetic dataset)",
        "disclaimer": (
            "This dataset is fabricated for research and testing. Values are synthetic and "+
            "calibrated to be plausible for Nigeria; verify against authoritative sources before use."
        ),
    }
    meta_path = data_path.with_suffix(data_path.suffix + ".metadata.json")
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


# --- Utility random helpers (seeded) ---

def bounded_gauss(mu: float, sigma: float, lo: float, hi: float) -> float:
    """Gaussian clipped to [lo, hi]."""
    x = random.gauss(mu, sigma)
    return max(lo, min(hi, x))


def triangular_scaled(center: float, spread: float, lo: float, hi: float) -> float:
    left = max(lo, center - spread)
    right = min(hi, center + spread)
    return random.triangular(left, right, center)


# --- Dataset builders ---

def build_generation_capacity(seed: int) -> None:
    path = ELEC_DIR / "generation_capacity.csv"
    years = list(range(2015, 2026))

    # Installed capacity ranges (MW), fabricated but plausible
    installed_ranges = {
        "Gas": (8000, 13000),
        "Hydro": (2500, 4500),
        "Solar": (50, 1200),
        "Wind": (0, 100),
        "Biomass": (0, 150),
        "Others": (0, 300),
    }
    # Available capacity as fraction of installed (Nigeria often constrained)
    avail_frac_ranges = {
        "Gas": (0.30, 0.60),
        "Hydro": (0.55, 0.80),
        "Solar": (0.15, 0.30),
        "Wind": (0.10, 0.25),
        "Biomass": (0.30, 0.50),
        "Others": (0.20, 0.40),
    }

    rows: List[Dict[str, Any]] = []
    for year in years:
        for src in ENERGY_SOURCES:
            lo, hi = installed_ranges[src]
            # trend gently over time
            trend = (year - years[0]) / max(1, (years[-1] - years[0]))
            install_mu = lo + (hi - lo) * (0.3 + 0.5 * trend)
            installed = bounded_gauss(install_mu, (hi - lo) * 0.08, lo, hi)
            af_lo, af_hi = avail_frac_ranges[src]
            avail_frac = triangular_scaled((af_lo + af_hi) / 2, (af_hi - af_lo) / 3, af_lo, af_hi)
            available = installed * avail_frac
            rows.append({
                "year": year,
                "source": src,
                "installed_capacity_mw": round(installed, 1),
                "available_capacity_mw": round(available, 1),
                "available_fraction": round(available / installed if installed > 0 else 0.0, 3),
            })

    write_csv(path, ["year", "source", "installed_capacity_mw", "available_capacity_mw", "available_fraction"], rows)
    write_metadata(
        path,
        title="National Generation Capacity by Source (Installed vs Available)",
        description=(
            "Fabricated installed and available generation capacity (MW) for Nigeria by source, 2015-2025."
        ),
        fields=[
            MetaField("year", "Calendar year", None, "int"),
            MetaField("source", "Generation source category", None, "str"),
            MetaField("installed_capacity_mw", "Installed/Nameplate capacity", "MW", "float"),
            MetaField("available_capacity_mw", "Available capacity reflective of constraints", "MW", "float"),
            MetaField("available_fraction", "Available/Installed ratio", None, "float"),
        ],
        sources=[
            "NERC (https://nerc.gov.ng)",
            "TCN/NESO (https://tcn.org.ng)",
            "World Bank reports (https://worldbank.org)",
            "Nigeria Electricity Hub (https://www.nigeriaelectricityhub.com)",
        ],
        seed=seed,
    )


def build_neso_daily_load_allocation(seed: int, days: int = 365) -> None:
    path = ELEC_DIR / "neso_daily_load_allocation.csv"
    start_date = date.today() - timedelta(days=days)
    total_sys_mw_mu = 4200
    total_sys_mw_sigma = 600

    # Weights per DISCO (fabricated based on load/population share)
    weights = {
        "Abuja DISCO": 0.11,
        "Benin DISCO": 0.09,
        "Eko DISCO": 0.10,
        "Enugu DISCO": 0.09,
        "Ibadan DISCO": 0.11,
        "Ikeja DISCO": 0.12,
        "Jos DISCO": 0.07,
        "Kaduna DISCO": 0.08,
        "Kano DISCO": 0.10,
        "Port Harcourt DISCO": 0.09,
        "Yola DISCO": 0.04,
    }
    assert abs(sum(weights.values()) - 1.0) < 1e-6

    rows: List[Dict[str, Any]] = []
    for i in range(days):
        dt = start_date + timedelta(days=i)
        total = max(1800.0, bounded_gauss(total_sys_mw_mu, total_sys_mw_sigma, 1800, 6500))
        for disco, w in weights.items():
            alloc = total * w * bounded_gauss(1.0, 0.06, 0.82, 1.18)
            transmitted = max(0.0, alloc * bounded_gauss(0.92, 0.04, 0.80, 0.99))
            load_shed = max(0.0, alloc - transmitted)
            rows.append({
                "date": dt.isoformat(),
                "disco": disco,
                "allocated_mw": round(alloc, 1),
                "transmitted_mw": round(transmitted, 1),
                "load_shedding_mw": round(load_shed, 1),
            })

    write_csv(path, ["date", "disco", "allocated_mw", "transmitted_mw", "load_shedding_mw"], rows)
    write_metadata(
        path,
        title="NESO Daily Load Allocation (Fabricated)",
        description=(
            "Synthetic daily load allocation and transmitted supply by DISCO, last 365 days."
        ),
        fields=[
            MetaField("date", "ISO date", None, "date"),
            MetaField("disco", "Distribution company", None, "str"),
            MetaField("allocated_mw", "NESO allocated MW to DISCO", "MW", "float"),
            MetaField("transmitted_mw", "Estimated MW delivered to DISCO", "MW", "float"),
            MetaField("load_shedding_mw", "Allocated minus transmitted", "MW", "float"),
        ],
        sources=[
            "TCN/NESO operational reports (https://tcn.org.ng)",
        ],
        seed=seed,
    )


def build_reliability(seed: int) -> None:
    path = ELEC_DIR / "grid_reliability_saidi_saifi.csv"
    years = [2020, 2021, 2022, 2023, 2024]
    rows: List[Dict[str, Any]] = []

    for disco in DISCOS:
        region = DISCO_REGION[disco]
        base_saidi = random.uniform(30000, 110000)  # minutes/customer-year (500h - 1833h)
        base_saifi = random.uniform(150, 800)       # interruptions/customer-year
        for y in years:
            drift = 1.0 + (y - years[0]) * random.uniform(-0.05, 0.04)
            saidi = max(10000, base_saidi * drift * random.uniform(0.85, 1.15))
            saifi = max(40, base_saifi * drift * random.uniform(0.80, 1.20))
            rows.append({
                "year": y,
                "disco": disco,
                "region": region,
                "saidi_minutes_per_cust": int(saidi),
                "saifi_interruptions_per_cust": round(saifi, 1),
                "estimation_method": "survey-based synthetic",
            })

    write_csv(path, ["year", "disco", "region", "saidi_minutes_per_cust", "saifi_interruptions_per_cust", "estimation_method"], rows)
    write_metadata(
        path,
        title="Grid Reliability Metrics (SAIDI/SAIFI) by DISCO (Synthetic)",
        description=(
            "Fabricated reliability indices per DISCO based on survey-like assumptions, 2020-2024."
        ),
        fields=[
            MetaField("year", "Calendar year", None, "int"),
            MetaField("disco", "Distribution company", None, "str"),
            MetaField("region", "Macro-region grouping", None, "str"),
            MetaField("saidi_minutes_per_cust", "System Average Interruption Duration Index", "minutes", "int"),
            MetaField("saifi_interruptions_per_cust", "System Average Interruption Frequency Index", "count", "float"),
            MetaField("estimation_method", "How this value was estimated", None, "str"),
        ],
        sources=[
            "NERC reliability publications (https://nerc.gov.ng)",
            "World Bank ESMAP surveys (https://esmap.org)",
        ],
        seed=seed,
    )


def build_tariffs(seed: int) -> None:
    path = ELEC_DIR / "electricity_tariffs.csv"
    effective = date.today().replace(day=1)

    rows: List[Dict[str, Any]] = []
    for disco in DISCOS:
        base = random.uniform(90, 140)  # NGN/kWh baseline for residential
        for cust in TARIFF_CUSTOMERS:
            multiplier = {
                "Residential": 1.0,
                "Commercial": random.uniform(1.1, 1.5),
                "Industrial": random.uniform(1.3, 1.8),
                "Premium": random.uniform(1.8, 2.5),
            }[cust]
            rate = base * multiplier * random.uniform(0.95, 1.10)
            rows.append({
                "effective_date": effective.isoformat(),
                "disco": disco,
                "customer_category": cust,
                "tariff_ngn_per_kwh": round(rate, 2),
                "currency": "NGN",
                "tariff_type": "grid",
            })

    write_csv(path, ["effective_date", "disco", "customer_category", "tariff_ngn_per_kwh", "currency", "tariff_type"], rows)
    write_metadata(
        path,
        title="Electricity Tariffs by DISCO and Customer Category (Synthetic)",
        description=(
            "Fabricated current tariffs in NGN/kWh for Residential, Commercial, Industrial, Premium customer classes."
        ),
        fields=[
            MetaField("effective_date", "Tariff effective date (first of month)", None, "date"),
            MetaField("disco", "Distribution company", None, "str"),
            MetaField("customer_category", "Customer category", None, "str"),
            MetaField("tariff_ngn_per_kwh", "Tariff rate", "NGN/kWh", "float"),
            MetaField("currency", "Currency", None, "str"),
            MetaField("tariff_type", "Grid or special/premium", None, "str"),
        ],
        sources=["NERC tariff orders (https://nerc.gov.ng)"] ,
        seed=seed,
    )


def build_gas_reserves_production(seed: int) -> None:
    path = FOSSIL_DIR / "gas_reserves_production.csv"
    years = list(range(2000, 2025))

    rows: List[Dict[str, Any]] = []
    reserves_tcf = 185.0
    for y in years:
        # gentle trend upwards with noise
        reserves_tcf = max(150.0, reserves_tcf + random.uniform(-1.0, 2.5))
        production_mmscf_d = bounded_gauss(6500 + (y - 2000) * 15, 400, 3000, 9000)
        rows.append({
            "year": y,
            "proven_reserves_tcf": round(reserves_tcf, 1),
            "production_mmscf_per_day": int(production_mmscf_d),
        })

    write_csv(path, ["year", "proven_reserves_tcf", "production_mmscf_per_day"], rows)
    write_metadata(
        path,
        title="Natural Gas Reserves and Production (Synthetic)",
        description="Fabricated annual proven gas reserves (Tcf) and daily production (mmscf/d) for Nigeria.",
        fields=[
            MetaField("year", "Calendar year", None, "int"),
            MetaField("proven_reserves_tcf", "Proven gas reserves", "Tcf", "float"),
            MetaField("production_mmscf_per_day", "Average daily production", "mmscf/d", "int"),
        ],
        sources=[
            "NNPC/NEITI reports (https://nnpcgroup.com)",
            "DPR/NUPRC statistics (https://nuprc.gov.ng)",
            "BP/WB energy outlooks",
        ],
        seed=seed,
    )


def build_gas_flare_sites_and_daily(seed: int, days: int = 365) -> None:
    sites_path = FOSSIL_DIR / "gas_flare_sites.csv"
    sites_geojson_path = FOSSIL_DIR / "gas_flare_sites.geojson"
    daily_path = FOSSIL_DIR / "gas_flare_daily.csv"

    # Assign a base flaring level per site (mscf/d)
    site_rows: List[Dict[str, Any]] = []
    site_bases: Dict[str, float] = {}
    for s in FLARE_SITES:
        base = random.uniform(5_000, 120_000)  # mscf/d
        site_bases[s["name"]] = base
        site_rows.append({
            "site_name": s["name"],
            "latitude": s["lat"],
            "longitude": s["lon"],
            "avg_flared_mscf_per_day": int(base),
            "state_guess": "Rivers" if s["lon"] > 6.0 else "Delta",
        })

    write_csv(sites_path, ["site_name", "latitude", "longitude", "avg_flared_mscf_per_day", "state_guess"], site_rows)
    write_metadata(
        sites_path,
        title="Gas Flare Sites (Synthetic)",
        description="Fabricated major flare sites in the Niger Delta with average flaring rates.",
        fields=[
            MetaField("site_name", "Flare site name", None, "str"),
            MetaField("latitude", "Site latitude", "deg", "float"),
            MetaField("longitude", "Site longitude", "deg", "float"),
            MetaField("avg_flared_mscf_per_day", "Average flared gas", "mscf/d", "int"),
            MetaField("state_guess", "Approximate Nigerian state for site", None, "str"),
        ],
        sources=[
            "GGFR/World Bank flaring data (https://www.worldbank.org/en/programs/gasflaring)",
        ],
        seed=seed,
    )

    # GeoJSON points
    features = []
    for r in site_rows:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [r["longitude"], r["latitude"]]},
            "properties": {
                "site_name": r["site_name"],
                "avg_flared_mscf_per_day": r["avg_flared_mscf_per_day"],
                "state_guess": r["state_guess"],
            },
        })
    write_geojson(sites_geojson_path, {"type": "FeatureCollection", "features": features})
    write_metadata(
        sites_geojson_path,
        title="Gas Flare Sites (GeoJSON, Synthetic)",
        description="GeoJSON points for fabricated flare sites.",
        fields=[
            MetaField("geometry", "Point coordinates [lon, lat]", None, "geojson"),
            MetaField("properties.site_name", "Flare site name", None, "str"),
            MetaField("properties.avg_flared_mscf_per_day", "Average flared gas", "mscf/d", "int"),
            MetaField("properties.state_guess", "Approximate state", None, "str"),
        ],
        sources=["GGFR/World Bank"],
        seed=seed,
    )

    # Daily time series per site
    start_date = date.today() - timedelta(days=days)
    daily_rows: List[Dict[str, Any]] = []
    for i in range(days):
        dt = start_date + timedelta(days=i)
        for name, base in site_bases.items():
            daily = max(0.0, random.gauss(base, base * 0.12))
            # seasonal adjustment (wet/dry)
            seasonal = 1.0 + 0.08 * math.sin(2 * math.pi * (dt.timetuple().tm_yday / 365.0))
            daily *= seasonal
            daily_rows.append({
                "date": dt.isoformat(),
                "site_name": name,
                "flared_mscf": int(daily),
            })

    write_csv(daily_path, ["date", "site_name", "flared_mscf"], daily_rows)
    write_metadata(
        daily_path,
        title="Gas Flaring Daily Time Series (Synthetic)",
        description="Fabricated daily flaring volumes by site for the past 365 days.",
        fields=[
            MetaField("date", "ISO date", None, "date"),
            MetaField("site_name", "Flare site name", None, "str"),
            MetaField("flared_mscf", "Gas flared on date", "mscf", "int"),
        ],
        sources=["GGFR/World Bank"],
        seed=seed,
    )


def build_pipeline_network_geojson(seed: int) -> None:
    path = FOSSIL_DIR / "gas_pipeline_network.geojson"
    features = []

    for a, b in PIPELINE_SEGMENTS:
        lat_a, lon_a = PIPELINE_NODES[a]
        lat_b, lon_b = PIPELINE_NODES[b]
        # Simple straight segment; add slight jitter points for realism
        coords = [
            [lon_a, lat_a],
            [ (lon_a + lon_b)/2 + random.uniform(-0.3, 0.3), (lat_a + lat_b)/2 + random.uniform(-0.3, 0.3) ],
            [lon_b, lat_b],
        ]
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {"from": a, "to": b, "diameter_in": random.choice([24, 30, 36])},
        })

    write_geojson(path, {"type": "FeatureCollection", "features": features})
    write_metadata(
        path,
        title="Natural Gas Pipeline Network (Synthetic GeoJSON)",
        description="Fabricated Nigerian gas pipeline segments connecting major nodes.",
        fields=[
            MetaField("geometry", "LineString coordinates [lon, lat]", None, "geojson"),
            MetaField("properties.from", "Start node", None, "str"),
            MetaField("properties.to", "End node", None, "str"),
            MetaField("properties.diameter_in", "Nominal diameter", "inches", "int"),
        ],
        sources=[
            "NNPC/NGC maps (https://nnpcgroup.com)",
        ],
        seed=seed,
    )


def build_fuel_prices_monthly(seed: int) -> None:
    path = FOSSIL_DIR / "fuel_prices_monthly.csv"
    # Monthly series 2023-01 to current month
    start = date(2023, 1, 1)
    end = date.today().replace(day=1)

    months: List[date] = []
    cur = start
    while cur <= end:
        months.append(cur)
        # move to next month
        if cur.month == 12:
            cur = date(cur.year + 1, 1, 1)
        else:
            cur = date(cur.year, cur.month + 1, 1)

    rows: List[Dict[str, Any]] = []
    # base trajectories (NGN/litre), capturing subsidy removal in mid-2023
    petrol_base = 190.0
    diesel_base = 700.0

    for m in months:
        t = (m.year - 2023) * 12 + (m.month - 1)
        petrol_trend = petrol_base + 40 * max(0, t - 5) + random.uniform(-15, 15)
        diesel_trend = diesel_base + 25 * t + random.uniform(-40, 40)
        for st in NIGERIA_STATES:
            # state variation
            pv = petrol_trend * random.uniform(0.92, 1.10)
            dv = diesel_trend * random.uniform(0.90, 1.12)
            rows.append({
                "month": m.isoformat(),
                "state": st,
                "petrol_retail_price_ngn_per_l": round(pv, 1),
                "diesel_retail_price_ngn_per_l": round(dv, 1),
                "currency": "NGN",
            })

    write_csv(path, ["month", "state", "petrol_retail_price_ngn_per_l", "diesel_retail_price_ngn_per_l", "currency"], rows)
    write_metadata(
        path,
        title="Retail Fuel Prices by State (Monthly, Synthetic)",
        description="Fabricated monthly petrol and diesel retail prices by state from 2023-01.",
        fields=[
            MetaField("month", "Month (first day)", None, "date"),
            MetaField("state", "Nigerian state", None, "str"),
            MetaField("petrol_retail_price_ngn_per_l", "Petrol (PMS) retail price", "NGN/litre", "float"),
            MetaField("diesel_retail_price_ngn_per_l", "Diesel (AGO) retail price", "NGN/litre", "float"),
            MetaField("currency", "Currency", None, "str"),
        ],
        sources=[
            "NBS PMS/AGO price watch (https://nigerianstat.gov.ng)",
        ],
        seed=seed,
    )


def build_renewables_agri_waste(seed: int) -> None:
    path = REN_DIR / "agricultural_waste_by_state.csv"
    residue_types = ["rice_husk", "maize_cobs", "sugarcane_bagasse", "cassava_peels", "palm_kernel_shells", "groundnut_shells"]
    year = date.today().year - 1

    rows: List[Dict[str, Any]] = []
    for st in NIGERIA_STATES:
        intensity = random.uniform(0.6, 1.4)
        for r in residue_types:
            base = {
                "rice_husk": 180_000,
                "maize_cobs": 220_000,
                "sugarcane_bagasse": 260_000,
                "cassava_peels": 300_000,
                "palm_kernel_shells": 240_000,
                "groundnut_shells": 160_000,
            }[r]
            qty = base * intensity * random.uniform(0.7, 1.3)
            rows.append({
                "year": year,
                "state": st,
                "residue_type": r,
                "residue_quantity_tons": int(qty),
            })

    write_csv(path, ["year", "state", "residue_type", "residue_quantity_tons"], rows)
    write_metadata(
        path,
        title="Agricultural Residues by State (Synthetic)",
        description="Fabricated annual quantities of key agricultural residues by state for bioenergy potential.",
        fields=[
            MetaField("year", "Calendar year", None, "int"),
            MetaField("state", "Nigerian state", None, "str"),
            MetaField("residue_type", "Residue category", None, "str"),
            MetaField("residue_quantity_tons", "Residue quantity", "metric tons", "int"),
        ],
        sources=[
            "FAO crop statistics (https://www.fao.org)",
            "NBS agricultural output (https://nigerianstat.gov.ng)",
        ],
        seed=seed,
    )


def build_renewables_livestock(seed: int) -> None:
    path = REN_DIR / "livestock_population_by_state.csv"
    species = ["cattle", "goats", "sheep", "poultry", "pigs"]
    years = list(range(2020, date.today().year))

    rows: List[Dict[str, Any]] = []
    for st in NIGERIA_STATES:
        base_scale = random.uniform(0.6, 1.6)
        for sp in species:
            base = {
                "cattle": 350_000,
                "goats": 1_800_000,
                "sheep": 1_200_000,
                "poultry": 5_500_000,
                "pigs": 150_000,
            }[sp] * base_scale
            val = base
            for y in years:
                growth = random.uniform(0.97, 1.07)
                val = max(1_000, val * growth)
                rows.append({
                    "year": y,
                    "state": st,
                    "species": sp,
                    "population_headcount": int(val),
                })

    write_csv(path, ["year", "state", "species", "population_headcount"], rows)
    write_metadata(
        path,
        title="Livestock Population by State (Synthetic)",
        description="Fabricated livestock counts by state and species (2020 to last full year).",
        fields=[
            MetaField("year", "Calendar year", None, "int"),
            MetaField("state", "Nigerian state", None, "str"),
            MetaField("species", "Livestock species", None, "str"),
            MetaField("population_headcount", "Animal count", "head", "int"),
        ],
        sources=[
            "FMARD/NBS agriculture surveys",
        ],
        seed=seed,
    )


def build_gas_composition(seed: int) -> None:
    path = FOSSIL_DIR / "gas_pipeline_quality_composition.csv"
    regions = ["Delta-West", "Delta-East", "Offshore", "North Corridor", "Southwest" ]

    rows: List[Dict[str, Any]] = []
    for reg in regions:
        ch4 = random.uniform(0.88, 0.94)
        c2plus = random.uniform(0.04, 0.08)
        co2 = random.uniform(0.005, 0.03)
        n2 = max(0.0, 1.0 - (ch4 + c2plus + co2))
        lhv_mj_per_scm = 35.8 * ch4 + 63.0 * c2plus + 0.0 * co2 + 0.0 * n2
        rows.append({
            "region": reg,
            "methane_ch4_frac": round(ch4, 4),
            "c2_plus_frac": round(c2plus, 4),
            "co2_frac": round(co2, 4),
            "n2_frac": round(n2, 4),
            "lhv_mj_per_scm": round(lhv_mj_per_scm, 2),
        })

    write_csv(path, ["region", "methane_ch4_frac", "c2_plus_frac", "co2_frac", "n2_frac", "lhv_mj_per_scm"], rows)
    write_metadata(
        path,
        title="Pipeline Gas Quality and Composition (Synthetic)",
        description="Fabricated regional natural gas composition fractions and estimated lower heating value (LHV).",
        fields=[
            MetaField("region", "Pipeline corridor region", None, "str"),
            MetaField("methane_ch4_frac", "Methane mol fraction", None, "float"),
            MetaField("c2_plus_frac", "Ethane and heavier mol fraction", None, "float"),
            MetaField("co2_frac", "CO2 mol fraction", None, "float"),
            MetaField("n2_frac", "Nitrogen mol fraction", None, "float"),
            MetaField("lhv_mj_per_scm", "Lower heating value", "MJ/Sm^3", "float"),
        ],
        sources=[
            "NGC gas specs (indicative)",
        ],
        seed=seed,
    )


def build_provenance(seed: int) -> None:
    path = DATA_DIR / "provenance.json"
    payload = {
        "generated_at_utc": NOW_ISO,
        "seed": seed,
        "generator": "generate_nigeria_energy_data.py",
        "datasets": [
            "electricity/generation_capacity.csv",
            "electricity/neso_daily_load_allocation.csv",
            "electricity/grid_reliability_saidi_saifi.csv",
            "electricity/electricity_tariffs.csv",
            "fossil_fuels/gas_reserves_production.csv",
            "fossil_fuels/gas_flare_sites.csv",
            "fossil_fuels/gas_flare_sites.geojson",
            "fossil_fuels/gas_flare_daily.csv",
            "fossil_fuels/gas_pipeline_network.geojson",
            "fossil_fuels/fuel_prices_monthly.csv",
            "fossil_fuels/gas_pipeline_quality_composition.csv",
            "renewables/agricultural_waste_by_state.csv",
            "renewables/livestock_population_by_state.csv",
        ],
        "disclaimer": "All values are synthetic, intended for research/testing on SOFC and energy context.",
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main(seed: int = DEFAULT_SEED) -> None:
    random.seed(seed)
    ensure_dirs()

    build_generation_capacity(seed)
    build_neso_daily_load_allocation(seed)
    build_reliability(seed)
    build_tariffs(seed)

    build_gas_reserves_production(seed)
    build_gas_flare_sites_and_daily(seed)
    build_pipeline_network_geojson(seed)
    build_fuel_prices_monthly(seed)
    build_gas_composition(seed)

    build_renewables_agri_waste(seed)
    build_renewables_livestock(seed)

    build_provenance(seed)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate synthetic Nigeria energy/resource datasets")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed for reproducibility")
    args = parser.parse_args()
    main(seed=args.seed)
