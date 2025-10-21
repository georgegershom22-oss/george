#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import json
import math
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple

# Deterministic pseudo-random helpers (no external deps)
class DeterministicRNG:
    def __init__(self, seed: int = 1337):
        self.state = seed & 0xFFFFFFFF

    def _next(self) -> int:
        # xorshift32
        x = self.state
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= (x >> 17) & 0xFFFFFFFF
        x ^= (x << 5) & 0xFFFFFFFF
        self.state = x & 0xFFFFFFFF
        return self.state

    def uniform(self, a: float, b: float) -> float:
        return a + (self._next() / 0xFFFFFFFF) * (b - a)

    def choice(self, seq: List):
        if not seq:
            raise ValueError("empty sequence")
        idx = int(self.uniform(0, len(seq)))
        return seq[min(idx, len(seq) - 1)]

    def normal(self, mu: float, sigma: float) -> float:
        # Box-Muller transform
        u1 = max(self.uniform(1e-9, 1.0), 1e-9)
        u2 = max(self.uniform(1e-9, 1.0), 1e-9)
        z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2 * math.pi * u2)
        return mu + z0 * sigma


BASE_DIR = "/workspace/data/nigeria_energy"
ELECTRICITY_DIR = os.path.join(BASE_DIR, "electricity")
FOSSIL_DIR = os.path.join(BASE_DIR, "fossil")
RENEWABLES_DIR = os.path.join(BASE_DIR, "renewables")
GIS_DIR = os.path.join(BASE_DIR, "gis")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

os.makedirs(ELECTRICITY_DIR, exist_ok=True)
os.makedirs(FOSSIL_DIR, exist_ok=True)
os.makedirs(RENEWABLES_DIR, exist_ok=True)
os.makedirs(GIS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

rng = DeterministicRNG(seed=20251021)

# Constants
DISCOS = [
    "AEDC",  # Abuja
    "BEDC",  # Benin
    "EEDC",  # Enugu
    "EKEDC", # Eko
    "IBEDC", # Ibadan
    "IKEDC", # Ikeja
    "JED",   # Jos
    "KAEDCO",# Kaduna
    "KEDCO", # Kano
    "PHED",  # Port Harcourt
    "YEDC",  # Yola
]

DISCO_SHARE_WEIGHTS = {
    # Rough, synthetic allocation weights summing ~1.0
    "AEDC": 0.11,
    "BEDC": 0.08,
    "EEDC": 0.07,
    "EKEDC": 0.10,
    "IBEDC": 0.14,
    "IKEDC": 0.12,
    "JED": 0.07,
    "KAEDCO": 0.08,
    "KEDCO": 0.09,
    "PHED": 0.08,
    "YEDC": 0.06,
}

NIGERIA_STATES = [
    "Abia","Adamawa","Akwa Ibom","Anambra","Bauchi","Bayelsa","Benue","Borno",
    "Cross River","Delta","Ebonyi","Edo","Ekiti","Enugu","Gombe","Imo","Jigawa",
    "Kaduna","Kano","Katsina","Kebbi","Kogi","Kwara","Lagos","Nasarawa","Niger",
    "Ogun","Ondo","Osun","Oyo","Plateau","Rivers","Sokoto","Taraba","Yobe","Zamfara",
    "FCT Abuja"
]

CROPS = [
    # Common crops aligned to residue streams for bioenergy
    {"name": "maize", "rpr": 0.27, "lhv_mj_per_kg": 17.0},
    {"name": "rice", "rpr": 0.23, "lhv_mj_per_kg": 15.0},
    {"name": "cassava", "rpr": 0.25, "lhv_mj_per_kg": 14.0},
    {"name": "sorghum", "rpr": 0.25, "lhv_mj_per_kg": 16.0},
    {"name": "sugarcane", "rpr": 0.30, "lhv_mj_per_kg": 9.0},  # bagasse
]

LIVESTOCK = [
    {"name": "cattle", "manure_kg_per_head_per_day": 25.0, "biogas_yield_m3_per_kg": 0.03},
    {"name": "goats", "manure_kg_per_head_per_day": 2.0, "biogas_yield_m3_per_kg": 0.028},
    {"name": "sheep", "manure_kg_per_head_per_day": 2.5, "biogas_yield_m3_per_kg": 0.028},
    {"name": "pigs", "manure_kg_per_head_per_day": 4.5, "biogas_yield_m3_per_kg": 0.045},
    {"name": "poultry", "manure_kg_per_head_per_day": 0.17, "biogas_yield_m3_per_kg": 0.065},
]

# Utility functions

def daterange(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def write_csv(path: str, header: List[str], rows: List[List]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def write_json(path: str, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


# Electricity datasets

def generate_capacity_by_source(start_year: int = 2015, end_year: int = 2025):
    sources = ["gas", "hydro", "solar", "wind", "biomass", "others"]
    rows: List[List] = []
    # Base installed capacity (MW) in 2015 (synthetic, plausible for Nigeria)
    base_installed = {
        "gas": 9000,
        "hydro": 3500,
        "solar": 50,
        "wind": 10,
        "biomass": 100,
        "others": 100,
    }
    for year in range(start_year, end_year + 1):
        growth_factor = 1.0 + 0.01 * (year - start_year)  # 1% per year baseline
        for s in sources:
            installed = base_installed[s] * growth_factor
            # add some project commissioning bumps
            if s == "solar":
                installed += max(0, (year - 2019)) * 30  # gradual solar additions
            if s == "gas":
                installed += 100 * max(0, (year - 2017))  # modest increments
            if s == "hydro":
                installed += 30 * max(0, (year - 2015))  # incremental refurbishments
            # available capacity: chronic derating due to outages, fuel constraints (35-55%)
            availability_ratio = 0.35 + 0.20 * (1.0 / (1.0 + math.exp(-0.3 * (year - 2020))))
            # Some random volatility per source
            availability_ratio *= (0.95 + 0.1 * (rng.uniform(0.0, 1.0)))
            available = installed * min(max(availability_ratio, 0.3), 0.65)
            # capacity factor proxy (synthetic)
            capacity_factor = min(max(0.25 + 0.15 * (installed / (installed + 2000.0)), 0.2), 0.7)
            rows.append([
                year,
                s,
                round(installed, 1),
                round(available, 1),
                round(capacity_factor, 3),
                "synthetic_fabricated",
                "NERC; TCN; World Bank (context); Nigeria Electricity Hub"
            ])
    write_csv(
        os.path.join(ELECTRICITY_DIR, "capacity_by_source_2015_2025.csv"),
        [
            "year","source","installed_mw","available_mw","capacity_factor_est",
            "provenance","sources"
        ],
        rows,
    )


def generate_grid_daily_generation(year: int = 2024):
    # produce daily total generation MW average and MWh energy
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    rows: List[List] = []
    for d in daterange(start, end):
        # base shape: weekdays slightly higher than weekends; seasonal wobble
        day_of_year = (d - date(year, 1, 1)).days + 1
        seasonal = 1.0 + 0.1 * math.sin(2 * math.pi * day_of_year / 365.0)
        weekday_factor = 1.05 if d.weekday() < 5 else 0.95
        noise = 1.0 + rng.normal(0.0, 0.03)
        avg_mw = max(2000.0, min(6000.0, 3800.0 * seasonal * weekday_factor * noise))
        energy_mwh = avg_mw * 24.0
        rows.append([d.isoformat(), round(avg_mw, 1), round(energy_mwh, 1), "synthetic_fabricated"])
    write_csv(
        os.path.join(ELECTRICITY_DIR, f"grid_daily_generation_{year}.csv"),
        ["date","avg_generation_mw","energy_mwh","provenance"],
        rows,
    )


def generate_neso_daily_allocation(year: int = 2024):
    # Use shares to allocate generation per disco
    gen_path = os.path.join(ELECTRICITY_DIR, f"grid_daily_generation_{year}.csv")
    daily: List[Tuple[str, float]] = []
    with open(gen_path, "r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            daily.append((r["date"], float(r["avg_generation_mw"])))
    rows: List[List] = []
    for d, total_mw in daily:
        # jitter the shares slightly day by day but preserve approximate sum
        jittered_shares = {}
        total_share = 0.0
        for disco in DISCOS:
            base = DISCO_SHARE_WEIGHTS[disco]
            jitter = rng.normal(0.0, 0.01)
            val = max(0.01, base * (1.0 + jitter))
            jittered_shares[disco] = val
            total_share += val
        for disco in DISCOS:
            share = jittered_shares[disco] / total_share
            alloc_mw = total_mw * share
            energy_mwh = alloc_mw * 24.0
            rows.append([d, disco, round(share, 5), round(alloc_mw, 1), round(energy_mwh, 1), "synthetic_fabricated", "NESO (context); TCN"])
    write_csv(
        os.path.join(ELECTRICITY_DIR, f"neso_daily_allocation_{year}.csv"),
        ["date","disco","share","allocated_mw","allocated_energy_mwh","provenance","sources"],
        rows,
    )


def generate_reliability_metrics(year: int = 2024):
    rows: List[List] = []
    for disco in DISCOS:
        # Very high outage metrics typical of under-supplied grid (synthetic)
        saidi = max(600.0, min(3500.0, rng.normal(2200.0, 400.0)))  # hours/year
        saifi = max(50.0, min(800.0, rng.normal(320.0, 80.0)))      # interruptions/year
        caidi = saidi / max(saifi, 1e-3)
        rows.append([
            year, disco, round(saidi, 1), round(saifi, 1), round(caidi, 2),
            "synthetic_estimate_from_surveys", "World Bank; NERC; TCN; academic surveys"
        ])
    write_csv(
        os.path.join(ELECTRICITY_DIR, f"reliability_metrics_{year}.csv"),
        ["year","disco","saidi_hours_per_year","saifi_interruptions_per_year","caidi_hours","provenance","sources"],
        rows,
    )


def generate_tariffs(start: date = date(2023,1,1), end: date = date(2025,10,1)):
    # Create monthly tariffs by disco, band (A-E, Premium) and class (residential, commercial, industrial)
    bands = ["A","B","C","D","E","Premium"]
    classes = ["residential","commercial","industrial"]
    rows: List[List] = []
    current = date(start.year, start.month, 1)

    def month_iter(d: date):
        y, m = d.year, d.month
        if m == 12:
            return date(y+1, 1, 1)
        return date(y, m+1, 1)

    while current <= end:
        # Macro price level (synthetic): inflationary trend post-2023
        months_since_2023 = (current.year - 2023) * 12 + (current.month - 1)
        inflation_factor = 1.0 + 0.015 * months_since_2023
        fx_pressure = 1.0 + 0.3 * (1.0 / (1.0 + math.exp(-0.2 * (months_since_2023 - 6))))
        base_rate = 45.0 * inflation_factor * fx_pressure  # NGN/kWh baseline
        for disco in DISCOS:
            disco_adjust = 0.9 + 0.25 * rng.uniform(0.0, 1.0)
            for band in bands:
                # Band multipliers: A highest, Premium special
                band_mult = {
                    "Premium": 4.0,
                    "A": 2.5,
                    "B": 2.0,
                    "C": 1.6,
                    "D": 1.3,
                    "E": 1.0,
                }[band]
                for cls in classes:
                    class_mult = {"residential": 1.0, "commercial": 1.1, "industrial": 1.15}[cls]
                    energy_ngn = base_rate * band_mult * class_mult * disco_adjust
                    # Fixed charges (synthetic) scale with band/class
                    fixed_ngn = 300.0 * band_mult * class_mult * (0.8 + 0.4 * rng.uniform(0.0, 1.0))
                    # Approx USD rate (synthetic FX):
                    ngn_per_usd = 1300.0  # placeholder FX
                    energy_usd = energy_ngn / ngn_per_usd
                    rows.append([
                        current.isoformat(), disco, band, cls,
                        round(energy_ngn, 2), round(fixed_ngn, 2), round(energy_usd, 4),
                        "synthetic_fabricated_from_policy_context", "NERC publications; media reports"
                    ])
        current = month_iter(current)

    write_csv(
        os.path.join(ELECTRICITY_DIR, "tariffs_monthly_2023_2025.csv"),
        ["period","disco","band","customer_class","energy_rate_ngn_per_kwh","fixed_charge_ngn_per_month","energy_rate_usd_per_kwh","provenance","sources"],
        rows,
    )


# Fossil datasets

def generate_gas_reserves_and_production(start_year: int = 2000, end_year: int = 2024):
    rows: List[List] = []
    # Proven reserves around ~200 Tcf, modest trend
    for year in range(start_year, end_year + 1):
        reserves_tcf = 160.0 + 2.0 * (year - start_year) + rng.normal(0.0, 1.5)
        # Daily production (bcf/d)
        production_bcfd = max(2.5, min(9.5, 4.0 + 0.12 * (year - 2000) + rng.normal(0.0, 0.5)))
        marketed_bcfd = production_bcfd * (0.78 + 0.06 * rng.uniform(0.0, 1.0))
        gas_to_power_bcfd = marketed_bcfd * (0.25 + 0.1 * rng.uniform(0.0, 1.0))
        rows.append([
            year, round(reserves_tcf, 1), round(production_bcfd, 2), round(marketed_bcfd, 2), round(gas_to_power_bcfd, 2),
            "synthetic_fabricated", "NNPC; NGC; DPR; OPEC; BP; IEA"
        ])
    write_csv(
        os.path.join(FOSSIL_DIR, "gas_reserves_production_2000_2024.csv"),
        ["year","proven_reserves_tcf","production_bcf_per_day","marketed_bcf_per_day","gas_to_power_bcf_per_day","provenance","sources"],
        rows,
    )


def generate_gas_flaring_sites_and_monthly():
    # Key synthetic sites with approximate coords
    sites = [
        {"site_id": "ESCRAVOS", "operator": "Chevron", "state": "Delta", "lat": 5.604, "lon": 5.198},
        {"site_id": "FORCADOS", "operator": "SPDC", "state": "Delta", "lat": 5.268, "lon": 5.486},
        {"site_id": "BONNY", "operator": "NLNG", "state": "Rivers", "lat": 4.453, "lon": 7.170},
        {"site_id": "UGHELLI", "operator": "NPDC", "state": "Delta", "lat": 5.500, "lon": 6.000},
        {"site_id": "QIT", "operator": "Mobil", "state": "Akwa Ibom", "lat": 4.335, "lon": 7.974},
        {"site_id": "BONGA", "operator": "SNEPCo", "state": "Offshore", "lat": 4.575, "lon": 6.500},
        {"site_id": "AGBAMI", "operator": "Chevron", "state": "Offshore", "lat": 4.000, "lon": 5.000},
    ]
    # Save sites CSV
    site_rows = []
    for s in sites:
        avg_flare_mscfd = 20_000 + 30_000 * rng.uniform(0.0, 1.0)  # per site synthetic
        site_rows.append([
            s["site_id"], s["operator"], s["state"], s["lat"], s["lon"], round(avg_flare_mscfd, 0),
            "synthetic_fabricated", "GGFR; NNPC; remote sensing studies"
        ])
    write_csv(
        os.path.join(FOSSIL_DIR, "gas_flaring_sites.csv"),
        ["site_id","operator","state","lat","lon","avg_flare_mscf_per_day","provenance","sources"],
        site_rows,
    )

    # Monthly flaring per site for 2023-2024
    def month_list(y1: int, m1: int, y2: int, m2: int) -> List[Tuple[int,int]]:
        out = []
        y, m = y1, m1
        while (y < y2) or (y == y2 and m <= m2):
            out.append((y, m))
            if m == 12:
                y += 1
                m = 1
            else:
                m += 1
        return out

    months = month_list(2023, 1, 2024, 12)
    monthly_rows = []
    for s in sites:
        # seasonality factor by month
        for (y, m) in months:
            base = 15_000 + 35_000 * rng.uniform(0.0, 1.0)
            seasonal = 1.0 + 0.1 * math.sin(2 * math.pi * (m / 12.0))
            value = base * seasonal
            monthly_rows.append([
                f"{y:04d}-{m:02d}", s["site_id"], round(value, 0),
                "mscfd", "synthetic_fabricated", "GGFR; NNPC; satellite"
            ])
    write_csv(
        os.path.join(FOSSIL_DIR, "gas_flaring_monthly_2023_2024.csv"),
        ["period","site_id","flared_volume","unit","provenance","sources"],
        monthly_rows,
    )


def generate_fuel_prices_state_monthly(start: date = date(2023,1,1), end: date = date(2025,10,1)):
    rows: List[List] = []
    current = date(start.year, start.month, 1)

    def month_iter(d: date):
        y, m = d.year, d.month
        if m == 12:
            return date(y+1, 1, 1)
        return date(y, m+1, 1)

    while current <= end:
        months_since_2023 = (current.year - 2023) * 12 + (current.month - 1)
        petrol_base = 180.0 if months_since_2023 < 5 else 550.0 + 12.0 * (months_since_2023 - 5)
        diesel_base = 700.0 + 18.0 * months_since_2023
        for st in NIGERIA_STATES:
            # regional variance
            geo_variance = 0.9 + 0.2 * rng.uniform(0.0, 1.0)
            petrol = petrol_base * geo_variance * (0.95 + 0.1 * rng.uniform(0.0, 1.0))
            diesel = diesel_base * geo_variance * (0.9 + 0.2 * rng.uniform(0.0, 1.0))
            rows.append([
                current.isoformat(), st, round(petrol, 2), round(diesel, 2), "NGN_per_litre",
                "synthetic_fabricated", "NNPC; NBS; PPPRA; media tracking"
            ])
        current = month_iter(current)

    write_csv(
        os.path.join(FOSSIL_DIR, "fuel_prices_state_monthly_2023_2025.csv"),
        ["period","state","petrol_price","diesel_price","unit","provenance","sources"],
        rows,
    )


# Renewables datasets

def generate_ag_waste_by_state(year: int = 2023):
    rows: List[List] = []
    for st in NIGERIA_STATES:
        # Synthetic crop production (tonnes) by state and crop
        for c in CROPS:
            base_crop = 150_000 + 500_000 * rng.uniform(0.0, 1.0)
            # Northern states slightly higher for cereals, southern for cassava/sugarcane
            north_bias = 1.1 if st in [
                "Kano","Kaduna","Katsina","Kebbi","Sokoto","Jigawa","Bauchi","Gombe","Yobe","Borno","Niger","Zamfara","Plateau","Taraba","Adamawa"] else 1.0
            south_bias = 1.12 if st in [
                "Ogun","Oyo","Osun","Ondo","Ekiti","Lagos","Edo","Delta","Rivers","Bayelsa","Cross River","Akwa Ibom","Imo","Abia","Anambra","Enugu","Ebonyi"] else 1.0
            crop_name = c["name"]
            if crop_name in ("maize","sorghum","rice"):
                prod = base_crop * north_bias
            elif crop_name in ("cassava","sugarcane"):
                prod = base_crop * south_bias
            else:
                prod = base_crop
            residue = prod * c["rpr"]
            recoverable = residue * (0.45 + 0.2 * rng.uniform(0.0, 1.0))
            lhv = c["lhv_mj_per_kg"]
            # Convert energy: MJ to MWh (1 MWh = 3.6e3 MJ); 1 tonne = 1000 kg
            energy_mwh = recoverable * 1000.0 * lhv / 3600.0
            rows.append([
                year, st, crop_name, round(prod, 0), round(residue, 0), round(recoverable, 0), lhv, round(energy_mwh, 1),
                "synthetic_estimate", "FAO; NBS; FMARD; literature on RPR"
            ])
    write_csv(
        os.path.join(RENEWABLES_DIR, f"ag_waste_by_state_{year}.csv"),
        ["year","state","crop","crop_production_tonnes","residue_tonnes","recoverable_residue_tonnes","lhv_mj_per_kg","energy_potential_mwh","provenance","sources"],
        rows,
    )


def generate_livestock_biogas(year: int = 2023):
    rows: List[List] = []
    for st in NIGERIA_STATES:
        for animal in LIVESTOCK:
            # Synthetic headcount by state (north higher for cattle etc.)
            base = 50_000 + 1_000_000 * rng.uniform(0.0, 1.0)
            if animal["name"] in ("cattle", "sheep", "goats") and st in [
                "Kano","Kaduna","Katsina","Kebbi","Sokoto","Jigawa","Bauchi","Gombe","Yobe","Borno","Niger","Zamfara","Plateau","Taraba","Adamawa"]:
                base *= 1.35
            if animal["name"] in ("poultry",) and st in ["Lagos","Ogun","Oyo","Rivers","Kano","Kaduna","Abia","Anambra","FCT Abuja"]:
                base *= 1.25
            headcount = int(base)
            manure_kg_day = headcount * animal["manure_kg_per_head_per_day"]
            biogas_m3_day = manure_kg_day * animal["biogas_yield_m3_per_kg"] * (0.6 + 0.2 * rng.uniform(0.0, 1.0))
            rows.append([
                year, st, animal["name"], headcount, round(manure_kg_day / 1000.0, 1), round(biogas_m3_day, 0),
                "synthetic_estimate", "FAO; NBS; FMARD; literature on biogas yields"
            ])
    write_csv(
        os.path.join(RENEWABLES_DIR, f"livestock_population_biogas_{year}.csv"),
        ["year","state","species","headcount","manure_tonnes_per_day","biogas_potential_nm3_per_day","provenance","sources"],
        rows,
    )


# GIS datasets

def generate_gas_pipeline_geojson():
    features = []
    def line_feature(name: str, coords: List[Tuple[float,float]], status: str, capacity_mmscfd: float):
        return {
            "type": "Feature",
            "properties": {
                "name": name,
                "status": status,
                "design_capacity_mmscfd": capacity_mmscfd,
                "provenance": "synthetic_traced_from_public_maps",
                "sources": "NNPC; NGC; media; WAGPCo"
            },
            "geometry": {"type": "LineString", "coordinates": [[lon, lat] for lat, lon in coords]},
        }

    # Approximate paths (lat, lon) tuples
    ELPS = [(5.6, 5.2), (6.2, 5.6), (6.5, 3.4)] # Escravos -> Warri -> Lagos
    AKK = [(7.93, 6.73), (9.25, 7.10), (10.52, 7.44)] # Ajaokuta -> Abuja -> Kaduna -> Kano (simplified)
    WAGP_NG = [(6.5, 3.4), (6.2, 2.9)] # Lagos -> West border (towards Benin)
    OB_OB = [(5.4, 6.9), (4.45, 7.17)] # Ob/Ob -> Bonny

    features.append(line_feature("ELPS", ELPS, "operational", 800.0))
    features.append(line_feature("AKK", AKK, "under_construction", 2000.0))
    features.append(line_feature("West African Gas Pipeline - Nigeria", WAGP_NG, "operational", 600.0))
    features.append(line_feature("Ob/Ob to Bonny", OB_OB, "operational", 300.0))

    geojson = {"type": "FeatureCollection", "features": features}
    write_json(os.path.join(GIS_DIR, "gas_pipeline_network.geojson"), geojson)


def generate_flare_sites_geojson():
    # Mirror of flaring sites CSV
    csv_path = os.path.join(FOSSIL_DIR, "gas_flaring_sites.csv")
    features = []
    with open(csv_path, "r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            features.append({
                "type": "Feature",
                "properties": {
                    "site_id": r["site_id"],
                    "operator": r["operator"],
                    "state": r["state"],
                    "avg_flare_mscf_per_day": float(r["avg_flare_mscf_per_day"]),
                    "provenance": r["provenance"],
                    "sources": r["sources"],
                },
                "geometry": {"type": "Point", "coordinates": [float(r["lon"]), float(r["lat"])]},
            })
    geojson = {"type": "FeatureCollection", "features": features}
    write_json(os.path.join(GIS_DIR, "flare_sites.geojson"), geojson)


# SOFC scenarios

def generate_sofc_scenarios():
    scenarios = []
    sizes_mw = [1, 5, 20]
    fuels = [
        {"fuel": "pipeline_natural_gas", "hhv_mmbtu_per_m3": 0.036, "ghg_kgco2_per_mmbtu": 53.1},
        {"fuel": "captured_flare_gas", "hhv_mmbtu_per_m3": 0.034, "ghg_kgco2_per_mmbtu": 52.5},
        {"fuel": "lng_or_lpg", "hhv_mmbtu_per_m3": 0.037, "ghg_kgco2_per_mmbtu": 54.0},
    ]
    gas_prices = [2.0, 3.0, 5.0, 8.0]  # USD/MMBtu
    capacity_factors = [0.6, 0.75, 0.9]

    rows: List[List] = []

    for size in sizes_mw:
        for fuel in fuels:
            for gas_price in gas_prices:
                for cf in capacity_factors:
                    # Assumptions
                    elec_eff = 0.55 + 0.05 * (size / 100.0)  # slightly higher for larger plants
                    elec_eff = min(elec_eff, 0.60)
                    capex_usd_per_kw = 4500.0 * (0.85 ** (math.log(size + 1, 2)))
                    opex_fixed_pct_capex = 0.03
                    lifetime_years = 20
                    wacc = 0.12

                    annual_mwh = size * 1000.0 * cf * 8760.0 / 1000.0
                    heat_rate_mmbtu_per_mwh = 3.412 / elec_eff  # 1 MWh = 3.412 MMBtu (electric), divide by efficiency
                    fuel_cost_usd_per_mwh = gas_price * heat_rate_mmbtu_per_mwh

                    capex_total = capex_usd_per_kw * size * 1000.0
                    crf = (wacc * (1 + wacc) ** lifetime_years) / ((1 + wacc) ** lifetime_years - 1)
                    annualized_capex = capex_total * crf
                    opex_fixed = capex_total * opex_fixed_pct_capex
                    opex_variable_per_mwh = 5.0  # USD/MWh synthetic

                    lcoe = (annualized_capex + opex_fixed + annual_mwh * (fuel_cost_usd_per_mwh + opex_variable_per_mwh)) / max(annual_mwh, 1e-6)

                    # Emissions intensity (kg CO2/kWh)
                    kgco2_per_mwh = fuel["ghg_kgco2_per_mmbtu"] * heat_rate_mmbtu_per_mwh
                    gco2_per_kwh = (kgco2_per_mwh * 1000.0) / 1000.0  # kg/MWh -> g/kWh

                    # Tariff competitiveness vs grid premium bands (rough)
                    competitive_vs_premium = lcoe < 0.25 * 1000 / 1300.0  # compare to ~NGN 250/kWh at 1300 FX

                    rows.append([
                        size, fuel["fuel"], gas_price, cf, round(elec_eff, 3), round(capex_usd_per_kw, 0),
                        round(lcoe, 4), round(fuel_cost_usd_per_mwh, 2), round(gco2_per_kwh, 1),
                        competitive_vs_premium, "synthetic_model"
                    ])

    write_csv(
        os.path.join(BASE_DIR, "sofc_scenarios.csv"),
        ["size_mw","fuel","gas_price_usd_per_mmbtu","capacity_factor","net_elec_efficiency","capex_usd_per_kw","lcoe_usd_per_kwh","fuel_cost_usd_per_mwh","emissions_gco2_per_kwh","competitive_vs_premium","provenance"],
        rows,
    )

    assumptions = {
        "notes": "All values are synthetic for scenario analysis; not official statistics.",
        "sources": [
            "DOE/NETL SOFC briefs", "Bloom Energy datasheets (context)", "NERC tariffs context", "IEA natural gas pricing context"
        ],
        "method": "Simple LCOE model with deterministic RNG to vary inputs.",
        "fx_assumption_ngn_per_usd": 1300.0,
        "efficiency_range": [0.55, 0.60],
        "lifetime_years": 20,
        "wacc": 0.12,
    }
    write_json(os.path.join(BASE_DIR, "sofc_assumptions.json"), assumptions)


# Metadata

def compile_metadata():
    metadata = {
        "dataset": "Nigerian Energy & Resource Data (synthetic/fabricated)",
        "topic": "Harnessing Domestic Gas for Power: SOFCs in Nigeria",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "provenance_categories": {
            "synthetic_fabricated": "Generated by script using plausible ranges informed by public context.",
            "synthetic_estimate": "Derived via simple models and ratios from plausible production figures.",
            "synthetic_traced_from_public_maps": "GIS coordinates approximated from public domain maps/articles.",
            "synthetic_model": "Outputs from simplified techno-economic model.",
        },
        "files": [
            {
                "path": "electricity/capacity_by_source_2015_2025.csv",
                "description": "Installed vs available capacity by source with capacity factor proxy.",
                "fields": {
                    "year": "Calendar year",
                    "source": "gas|hydro|solar|wind|biomass|others",
                    "installed_mw": "Installed nameplate (MW)",
                    "available_mw": "Estimated available (MW)",
                    "capacity_factor_est": "Proxy fraction 0-1",
                    "provenance": "synthetic_fabricated",
                    "sources": "Context sources consulted"
                }
            },
            {
                "path": "electricity/grid_daily_generation_2024.csv",
                "description": "Daily average grid generation and energy.",
                "fields": {"date": "ISO date", "avg_generation_mw": "MW", "energy_mwh": "MWh", "provenance": "synthetic_fabricated"}
            },
            {
                "path": "electricity/neso_daily_allocation_2024.csv",
                "description": "NESO daily allocation by Disco (synthetic shares).",
                "fields": {
                    "date": "ISO date",
                    "disco": "Distribution company",
                    "share": "Share of total (0-1)",
                    "allocated_mw": "MW",
                    "allocated_energy_mwh": "MWh",
                    "provenance": "synthetic_fabricated",
                    "sources": "NESO; TCN (context)"
                }
            },
            {
                "path": "electricity/reliability_metrics_2024.csv",
                "description": "SAIDI/SAIFI/CAIDI by Disco (survey-style synthetic).",
                "fields": {"year": "Year", "disco": "Disco", "saidi_hours_per_year": "Hours", "saifi_interruptions_per_year": "Count", "caidi_hours": "Hours", "provenance": "synthetic_estimate", "sources": "World Bank; NERC"}
            },
            {
                "path": "electricity/tariffs_monthly_2023_2025.csv",
                "description": "Monthly tariffs by Disco, band, and class.",
                "fields": {
                    "period": "YYYY-MM-01",
                    "disco": "Disco",
                    "band": "A-E or Premium",
                    "customer_class": "residential|commercial|industrial",
                    "energy_rate_ngn_per_kwh": "NGN/kWh",
                    "fixed_charge_ngn_per_month": "NGN/month",
                    "energy_rate_usd_per_kwh": "USD/kWh at synthetic FX",
                    "provenance": "synthetic_fabricated_from_policy_context",
                    "sources": "NERC publications; media"
                }
            },
            {
                "path": "fossil/gas_reserves_production_2000_2024.csv",
                "description": "Proven reserves and daily production (total, marketed, gas-to-power).",
                "fields": {
                    "year": "Year",
                    "proven_reserves_tcf": "Tcf",
                    "production_bcf_per_day": "bcf/d",
                    "marketed_bcf_per_day": "bcf/d",
                    "gas_to_power_bcf_per_day": "bcf/d",
                    "provenance": "synthetic_fabricated",
                    "sources": "NNPC; DPR; OPEC; IEA"
                }
            },
            {
                "path": "fossil/gas_flaring_sites.csv",
                "description": "Major flare sites with coordinates and average flaring.",
                "fields": {"site_id": "ID", "operator": "Operator", "state": "State/Offshore", "lat": "deg", "lon": "deg", "avg_flare_mscf_per_day": "mscfd", "provenance": "synthetic_fabricated", "sources": "GGFR; NNPC"}
            },
            {
                "path": "fossil/gas_flaring_monthly_2023_2024.csv",
                "description": "Monthly flared volumes by site (mscfd).",
                "fields": {"period": "YYYY-MM", "site_id": "ID", "flared_volume": "mscfd", "unit": "mscfd", "provenance": "synthetic_fabricated", "sources": "GGFR"}
            },
            {
                "path": "fossil/fuel_prices_state_monthly_2023_2025.csv",
                "description": "Monthly petrol and diesel retail prices by state (post-subsidy dynamics).",
                "fields": {"period": "YYYY-MM-01", "state": "State", "petrol_price": "NGN/litre", "diesel_price": "NGN/litre", "unit": "unit", "provenance": "synthetic_fabricated", "sources": "NNPC; NBS"}
            },
            {
                "path": "renewables/ag_waste_by_state_2023.csv",
                "description": "Crop residue availability and energy potential by state.",
                "fields": {
                    "year": "Year",
                    "state": "State",
                    "crop": "Crop",
                    "crop_production_tonnes": "t",
                    "residue_tonnes": "t",
                    "recoverable_residue_tonnes": "t",
                    "lhv_mj_per_kg": "MJ/kg",
                    "energy_potential_mwh": "MWh",
                    "provenance": "synthetic_estimate",
                    "sources": "FAO; NBS; FMARD"
                }
            },
            {
                "path": "renewables/livestock_population_biogas_2023.csv",
                "description": "Livestock headcount, manure and biogas potential by state.",
                "fields": {
                    "year": "Year",
                    "state": "State",
                    "species": "cattle|goats|sheep|pigs|poultry",
                    "headcount": "count",
                    "manure_tonnes_per_day": "t/day",
                    "biogas_potential_nm3_per_day": "Nm3/day",
                    "provenance": "synthetic_estimate",
                    "sources": "FAO; NBS; FMARD"
                }
            },
            {
                "path": "gis/gas_pipeline_network.geojson",
                "description": "Gas pipeline network (approximate lines).",
                "fields": {"name": "Pipeline name", "status": "operational|under_construction", "design_capacity_mmscfd": "mmscfd"}
            },
            {
                "path": "gis/flare_sites.geojson",
                "description": "Flare sites as point features.",
                "fields": {"site_id": "ID", "operator": "Operator", "avg_flare_mscf_per_day": "mscfd"}
            },
            {
                "path": "sofc_scenarios.csv",
                "description": "SOFC techno-economic scenarios (LCOE, emissions).",
                "fields": {
                    "size_mw": "MW",
                    "fuel": "pipeline_natural_gas|captured_flare_gas|lng_or_lpg",
                    "gas_price_usd_per_mmbtu": "USD/MMBtu",
                    "capacity_factor": "0-1",
                    "net_elec_efficiency": "0-1",
                    "capex_usd_per_kw": "USD/kW",
                    "lcoe_usd_per_kwh": "USD/kWh",
                    "fuel_cost_usd_per_mwh": "USD/MWh",
                    "emissions_gco2_per_kwh": "gCO2/kWh",
                    "competitive_vs_premium": "boolean",
                    "provenance": "synthetic_model"
                }
            },
            {
                "path": "sofc_assumptions.json",
                "description": "Assumptions used in SOFC scenario generator.",
                "fields": {"notes": "text", "sources": "list", "method": "text", "fx_assumption_ngn_per_usd": "number", "efficiency_range": "[min,max]", "lifetime_years": "years", "wacc": "fraction"}
            },
        ],
    }
    write_json(os.path.join(DOCS_DIR, "metadata.json"), metadata)


# Orchestration

def main():
    # Electricity
    generate_capacity_by_source(2015, 2025)
    generate_grid_daily_generation(2024)
    generate_neso_daily_allocation(2024)
    generate_reliability_metrics(2024)
    generate_tariffs(date(2023,1,1), date(2025,10,1))

    # Fossil
    generate_gas_reserves_and_production(2000, 2024)
    generate_gas_flaring_sites_and_monthly()
    generate_fuel_prices_state_monthly(date(2023,1,1), date(2025,10,1))

    # Renewables
    generate_ag_waste_by_state(2023)
    generate_livestock_biogas(2023)

    # GIS
    generate_gas_pipeline_geojson()
    generate_flare_sites_geojson()

    # SOFC
    generate_sofc_scenarios()

    # Metadata
    compile_metadata()


if __name__ == "__main__":
    main()
