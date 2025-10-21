#!/usr/bin/env python3
"""
Builds economic and financial datasets for TEA of SOFC in Nigeria.
- Downloads macro financial series from World Bank API (inflation, lending rates, USD/NGN exchange).
- Fabricates technology cost datasets for SOFC, diesel generators, and Solar PV + Battery with low/base/high scenarios.
Outputs CSVs under data/economic_financial/.

Note: Cost numbers are synthetic but bounded by literature ranges (DOE/NREL/IRENA/manufacturer datasheets). Always validate before use in decisions.
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys
import time
from typing import Dict, List, Optional, Tuple

try:
    import requests  # type: ignore
except Exception as exc:  # pragma: no cover
    print("The 'requests' package is required. Install via: pip install requests", file=sys.stderr)
    raise

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "economic_financial")
DATA_DIR = os.path.abspath(DATA_DIR)

WB_BASE = "https://api.worldbank.org/v2"

# World Bank indicators to fetch
WB_SERIES = {
    # Inflation, consumer prices (annual %)
    "inflation_cpi_pct": {
        "indicator": "FP.CPI.TOTL.ZG",
        "description": "Inflation, consumer prices (annual %)",
        "source": "World Bank API FP.CPI.TOTL.ZG",
    },
    # Lending interest rate (%)
    "lending_rate_pct": {
        "indicator": "FR.INR.LEND",
        "description": "Lending interest rate (%)",
        "source": "World Bank API FR.INR.LEND",
    },
    # Official exchange rate (LCU per USD, period average) => NGN per USD
    "usd_ngn_official": {
        "indicator": "PA.NUS.FCRF",
        "description": "Official exchange rate (LCU per USD, period average)",
        "source": "World Bank API PA.NUS.FCRF",
    },
}

COUNTRY_ISO3 = "NGA"


def ensure_outdir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def wb_fetch_series(country_iso3: str, indicator: str, start_year: int = 2000, end_year: Optional[int] = None) -> List[Dict]:
    """Fetch a World Bank indicator series for a country as list of dicts.

    Returns entries like: {"year": 2022, "value": 18.3, "indicator": indicator_code, "country": country_iso3}
    """
    if end_year is None:
        end_year = int(time.strftime("%Y"))

    url = f"{WB_BASE}/country/{country_iso3}/indicator/{indicator}"
    params = {
        "format": "json",
        "per_page": 10000,
        "date": f"{start_year}:{end_year}",
    }

    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    payload = r.json()

    if not isinstance(payload, list) or len(payload) < 2:
        return []

    data = payload[1] or []
    rows: List[Dict] = []
    for obs in data:
        val = obs.get("value")
        date = obs.get("date")
        try:
            year = int(date)
        except Exception:
            continue
        if val is None:
            continue
        rows.append({
            "country": country_iso3,
            "indicator": indicator,
            "year": year,
            "value": float(val),
        })
    # sort ascending by year
    rows.sort(key=lambda x: x["year"]) 
    return rows


def write_csv(path: str, fieldnames: List[str], rows: List[Dict]) -> None:
    ensure_outdir(os.path.dirname(path))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k) for k in fieldnames})


def build_world_bank_outputs() -> Dict[str, List[Dict]]:
    series_outputs: Dict[str, List[Dict]] = {}
    for key, meta in WB_SERIES.items():
        try:
            rows = wb_fetch_series(COUNTRY_ISO3, meta["indicator"], start_year=2000)
        except Exception as exc:
            print(f"WARN: failed to fetch {key}: {exc}", file=sys.stderr)
            rows = []
        series_outputs[key] = rows

    # Write exchange series
    fx_rows = series_outputs.get("usd_ngn_official", [])
    write_csv(
        os.path.join(DATA_DIR, "exchange_rates_usd_ngn.csv"),
        ["country", "indicator", "year", "value"],
        fx_rows,
    )

    # Write financial parameters (latest values)
    fin_param_rows: List[Dict] = []

    def latest(rows: List[Dict]) -> Optional[Dict]:
        if not rows:
            return None
        return rows[-1]

    infl_latest = latest(series_outputs.get("inflation_cpi_pct", []))
    lend_latest = latest(series_outputs.get("lending_rate_pct", []))

    if infl_latest:
        fin_param_rows.append({
            "parameter": "inflation_cpi_percent",
            "year": infl_latest["year"],
            "value": infl_latest["value"],
            "unit": "%",
            "source": WB_SERIES["inflation_cpi_pct"]["source"],
        })
    if lend_latest:
        fin_param_rows.append({
            "parameter": "lending_interest_rate_percent",
            "year": lend_latest["year"],
            "value": lend_latest["value"],
            "unit": "%",
            "source": WB_SERIES["lending_rate_pct"]["source"],
        })

    write_csv(
        os.path.join(DATA_DIR, "financial_parameters.csv"),
        ["parameter", "year", "value", "unit", "source"],
        fin_param_rows,
    )

    return series_outputs


def fabricate_sofc_costs() -> List[Dict]:
    """Fabricate SOFC cost dataset across sizes with low/base/high scenarios.

    Values are illustrative ranges based on literature; validate before use.
    """
    capacities = [100, 250, 500, 1000]  # kW
    scenarios = [
        {
            "scenario": "low",
            "capex_usd_per_kw": {100: 4500, 250: 4000, 500: 3500, 1000: 3000},
            "maintenance_pct_capex_per_year": 2.0,
            "stack_replacement_cost_pct_capex": 20.0,
            "stack_replacement_interval_years": 6,
        },
        {
            "scenario": "base",
            "capex_usd_per_kw": {100: 5500, 250: 4500, 500: 4000, 1000: 3500},
            "maintenance_pct_capex_per_year": 3.0,
            "stack_replacement_cost_pct_capex": 25.0,
            "stack_replacement_interval_years": 5,
        },
        {
            "scenario": "high",
            "capex_usd_per_kw": {100: 6500, 250: 5500, 500: 5000, 1000: 4500},
            "maintenance_pct_capex_per_year": 4.0,
            "stack_replacement_cost_pct_capex": 35.0,
            "stack_replacement_interval_years": 4,
        },
    ]

    labor_by_size = {100: (1, 12000), 250: (2, 24000), 500: (2, 24000), 1000: (3, 36000)}  # (tech_count, usd_per_year)

    rows: List[Dict] = []
    for s in scenarios:
        for cap in capacities:
            capex_per_kw = s["capex_usd_per_kw"][cap]
            capex_total = capex_per_kw * cap
            techs, labor = labor_by_size[cap]
            rows.append({
                "technology": "SOFC",
                "scenario": s["scenario"],
                "capacity_kw": cap,
                "capex_usd_per_kw": capex_per_kw,
                "capex_total_usd": capex_total,
                "maintenance_pct_capex_per_year": s["maintenance_pct_capex_per_year"],
                "stack_replacement_cost_pct_capex": s["stack_replacement_cost_pct_capex"],
                "stack_replacement_interval_years": s["stack_replacement_interval_years"],
                "labor_technicians_count": techs,
                "labor_cost_usd_per_year": labor,
                "source": "Fabricated from literature ranges (DOE/NREL/manufacturer reports)",
                "notes": "Assumptions: SOFC stack replaced periodically; labor scaled with plant size.",
            })
    return rows


def fabricate_diesel_costs() -> List[Dict]:
    capacities = [100, 250, 500, 1000]  # kW
    scenarios = [
        {
            "scenario": "low",
            "capex_usd_per_kw": {100: 350, 250: 320, 500: 300, 1000: 280},
            "maintenance_usd_per_kwh": 0.015,
            "fuel_liters_per_kwh_by_size": {100: 0.28, 250: 0.26, 500: 0.25, 1000: 0.24},
        },
        {
            "scenario": "base",
            "capex_usd_per_kw": {100: 400, 250: 350, 500: 320, 1000: 300},
            "maintenance_usd_per_kwh": 0.020,
            "fuel_liters_per_kwh_by_size": {100: 0.29, 250: 0.27, 500: 0.255, 1000: 0.245},
        },
        {
            "scenario": "high",
            "capex_usd_per_kw": {100: 450, 250: 380, 500: 340, 1000: 320},
            "maintenance_usd_per_kwh": 0.025,
            "fuel_liters_per_kwh_by_size": {100: 0.31, 250: 0.29, 500: 0.265, 1000: 0.255},
        },
    ]

    rows: List[Dict] = []
    for s in scenarios:
        for cap in capacities:
            capex_per_kw = s["capex_usd_per_kw"][cap]
            rows.append({
                "technology": "Diesel_Generator",
                "scenario": s["scenario"],
                "capacity_kw": cap,
                "capex_usd_per_kw": capex_per_kw,
                "capex_total_usd": capex_per_kw * cap,
                "fuel_liters_per_kwh": s["fuel_liters_per_kwh_by_size"][cap],
                "maintenance_usd_per_kwh": s["maintenance_usd_per_kwh"],
                "source": "Fabricated from industrial genset datasheets and DOE/NREL estimates",
                "notes": "Fuel rate at ~75% load; excludes logistics; verify at site-specific conditions.",
            })
    return rows


def fabricate_pv_bess_costs() -> List[Dict]:
    pv_sizes_kw = [100, 250, 500, 1000]
    bess_durations_h = [2, 4]  # hours of storage

    # $/kW for PV and $/kWh for battery
    scenarios = [
        {
            "scenario": "low",
            "pv_capex_usd_per_kw": {100: 1000, 250: 900, 500: 850, 1000: 800},
            "bess_capex_usd_per_kwh": 250,
            "pv_om_usd_per_kw_per_year": 10,
            "bess_om_usd_per_kwh_per_year": 6,
        },
        {
            "scenario": "base",
            "pv_capex_usd_per_kw": {100: 1150, 250: 1000, 500: 900, 1000: 850},
            "bess_capex_usd_per_kwh": 350,
            "pv_om_usd_per_kw_per_year": 15,
            "bess_om_usd_per_kwh_per_year": 10,
        },
        {
            "scenario": "high",
            "pv_capex_usd_per_kw": {100: 1300, 250: 1150, 500: 1050, 1000: 950},
            "bess_capex_usd_per_kwh": 450,
            "pv_om_usd_per_kw_per_year": 20,
            "bess_om_usd_per_kwh_per_year": 14,
        },
    ]

    rows: List[Dict] = []
    for s in scenarios:
        for pv_kw in pv_sizes_kw:
            for dur_h in bess_durations_h:
                bess_kwh = pv_kw * dur_h  # sizing heuristic; adjust for project specifics
                pv_capex = s["pv_capex_usd_per_kw"][pv_kw]
                bess_capex_per_kwh = s["bess_capex_usd_per_kwh"]
                rows.append({
                    "technology": "SolarPV_Battery",
                    "scenario": s["scenario"],
                    "pv_capacity_kw": pv_kw,
                    "bess_energy_kwh": bess_kwh,
                    "bess_duration_h": dur_h,
                    "pv_capex_usd_per_kw": pv_capex,
                    "pv_capex_total_usd": pv_capex * pv_kw,
                    "bess_capex_usd_per_kwh": bess_capex_per_kwh,
                    "bess_capex_total_usd": bess_capex_per_kwh * bess_kwh,
                    "pv_om_usd_per_kw_per_year": s["pv_om_usd_per_kw_per_year"],
                    "bess_om_usd_per_kwh_per_year": s["bess_om_usd_per_kwh_per_year"],
                    "source": "Fabricated from NREL ATB / IRENA ranges for commercial systems",
                    "notes": "BESS sized to PV nameplate times duration; adjust to meet reliability targets.",
                })
    return rows


def compute_wacc_rows(fin_series: Dict[str, List[Dict]]) -> List[Dict]:
    """Compute a baseline WACC row using simple assumptions.

    WACC = E/V*Re + D/V*Rd*(1 - Tc)
    Assumptions:
      - Capital structure: 30% equity, 70% debt
      - Cost of equity: proxy via lending rate + 700 bps risk premium (rough; for demonstration)
      - Cost of debt: use latest lending rate
      - Corporate tax rate (Nigeria): 30%
    """
    lend = fin_series.get("lending_rate_pct", [])
    lending_latest = lend[-1]["value"] if lend else None

    if lending_latest is None:
        return []

    debt_ratio = 0.70
    equity_ratio = 0.30
    tax_rate = 0.30
    cost_of_debt_pct = float(lending_latest)
    cost_of_equity_pct = cost_of_debt_pct + 7.0  # very rough proxy

    wacc_pct = equity_ratio * cost_of_equity_pct + debt_ratio * cost_of_debt_pct * (1.0 - tax_rate)

    row = {
        "parameter": "wacc_baseline_percent",
        "value": round(wacc_pct, 3),
        "unit": "%",
        "assum_debt_ratio": debt_ratio,
        "assum_equity_ratio": equity_ratio,
        "assum_tax_rate": tax_rate,
        "assum_cost_of_debt_percent": round(cost_of_debt_pct, 3),
        "assum_cost_of_equity_percent": round(cost_of_equity_pct, 3),
        "source": "Computed from World Bank lending rate with stated assumptions",
    }
    return [row]


def main() -> None:
    ensure_outdir(DATA_DIR)

    # 1) Download World Bank series and write CSVs
    fin_series = build_world_bank_outputs()

    # 2) Compute and append WACC baseline
    wacc_rows = compute_wacc_rows(fin_series)
    if wacc_rows:
        # Append to financial_parameters.csv
        fin_path = os.path.join(DATA_DIR, "financial_parameters.csv")
        # Read existing
        existing: List[Dict] = []
        if os.path.exists(fin_path):
            with open(fin_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    existing.append(r)
        # Harmonize fieldnames
        fieldnames = [
            "parameter",
            "year",
            "value",
            "unit",
            "source",
            "assum_debt_ratio",
            "assum_equity_ratio",
            "assum_tax_rate",
            "assum_cost_of_debt_percent",
            "assum_cost_of_equity_percent",
        ]
        # Convert to strings where absent
        augmented: List[Dict] = []
        for r in existing:
            r.setdefault("assum_debt_ratio", "")
            r.setdefault("assum_equity_ratio", "")
            r.setdefault("assum_tax_rate", "")
            r.setdefault("assum_cost_of_debt_percent", "")
            r.setdefault("assum_cost_of_equity_percent", "")
            augmented.append(r)
        # Add wacc row (no year)
        wacc = wacc_rows[0]
        augmented.append({
            "parameter": wacc["parameter"],
            "year": "",
            "value": wacc["value"],
            "unit": wacc["unit"],
            "source": wacc["source"],
            "assum_debt_ratio": wacc["assum_debt_ratio"],
            "assum_equity_ratio": wacc["assum_equity_ratio"],
            "assum_tax_rate": wacc["assum_tax_rate"],
            "assum_cost_of_debt_percent": wacc["assum_cost_of_debt_percent"],
            "assum_cost_of_equity_percent": wacc["assum_cost_of_equity_percent"],
        })
        write_csv(fin_path, fieldnames, augmented)

    # 3) Fabricate technology cost CSVs
    sofc_rows = fabricate_sofc_costs()
    write_csv(
        os.path.join(DATA_DIR, "sofc_system_costs.csv"),
        [
            "technology",
            "scenario",
            "capacity_kw",
            "capex_usd_per_kw",
            "capex_total_usd",
            "maintenance_pct_capex_per_year",
            "stack_replacement_cost_pct_capex",
            "stack_replacement_interval_years",
            "labor_technicians_count",
            "labor_cost_usd_per_year",
            "source",
            "notes",
        ],
        sofc_rows,
    )

    diesel_rows = fabricate_diesel_costs()
    write_csv(
        os.path.join(DATA_DIR, "diesel_generator_costs.csv"),
        [
            "technology",
            "scenario",
            "capacity_kw",
            "capex_usd_per_kw",
            "capex_total_usd",
            "fuel_liters_per_kwh",
            "maintenance_usd_per_kwh",
            "source",
            "notes",
        ],
        diesel_rows,
    )

    pv_bess_rows = fabricate_pv_bess_costs()
    write_csv(
        os.path.join(DATA_DIR, "solar_pv_battery_costs.csv"),
        [
            "technology",
            "scenario",
            "pv_capacity_kw",
            "bess_energy_kwh",
            "bess_duration_h",
            "pv_capex_usd_per_kw",
            "pv_capex_total_usd",
            "bess_capex_usd_per_kwh",
            "bess_capex_total_usd",
            "pv_om_usd_per_kw_per_year",
            "bess_om_usd_per_kwh_per_year",
            "source",
            "notes",
        ],
        pv_bess_rows,
    )

    print(f"Wrote datasets to: {DATA_DIR}")


if __name__ == "__main__":
    main()
