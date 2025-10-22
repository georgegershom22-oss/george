import os
import json
from typing import Dict, List, Dict as TDict
import csv

from src.fetchers.world_bank import fetch_all as wb_fetch_all
from src.generators.synthetic_macro import generate_macro_series
from src.generators.broadband_by_state import generate_broadband_by_state
from src.generators.sectoral_growth import generate_sectoral_growth
from src.generators.tech_adoption import generate_mobile_money_adoption, generate_itu_idi
from src.utils.provenance import make_record, Artifact, save_record

START_YEAR = 2005
END_YEAR = 2024

RAW_DIR = "/workspace/data/raw"
PROC_DIR = "/workspace/data/processed"
COMB_DIR = "/workspace/data/combined"
PROV_DIR = "/workspace/data/provenance"


def ensure_dirs():
    for d in [RAW_DIR, PROC_DIR, COMB_DIR, PROV_DIR]:
        os.makedirs(d, exist_ok=True)


def run_world_bank() -> Dict[str, str]:
    wb_dir = os.path.join(RAW_DIR, "wb")
    paths = wb_fetch_all(wb_dir)
    prov = make_record(
        dataset_name="world_bank_macro",
        generator="src.fetchers.world_bank.fetch_all",
        source="https://api.worldbank.org",
        parameters={"country": "NGA", "indicators": list(paths.keys())},
        artifacts={k: Artifact(name=k, path=v, kind="raw", description=f"World Bank {k}") for k, v in paths.items()}
    )
    save_record(prov, os.path.join(PROV_DIR, "world_bank_macro.json"))
    return paths


def _write_csv(path: str, fieldnames: List[str], rows: List[TDict]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def run_macro(paths: Dict[str, str]):
    # GDP growth
    gdp_path = paths.get("gdp_growth")
    gdp = generate_macro_series(gdp_path if gdp_path and gdp_path.endswith('.csv') else None,
                                START_YEAR, END_YEAR, mean=3.0, phi=0.5, sigma=2.0, x0=5.0)
    gdp_out = os.path.join(PROC_DIR, "macro_gdp_growth.csv")
    _write_csv(gdp_out, ["year", "value"], gdp)

    # Inflation
    inf_path = paths.get("inflation")
    inf = generate_macro_series(inf_path if inf_path and inf_path.endswith('.csv') else None,
                                START_YEAR, END_YEAR, mean=12.0, phi=0.6, sigma=3.5, x0=11.0)
    inf_out = os.path.join(PROC_DIR, "macro_inflation.csv")
    _write_csv(inf_out, ["year", "value"], inf)

    # Lending interest rate
    lend_path = paths.get("lending_rate")
    lend = generate_macro_series(lend_path if lend_path and lend_path.endswith('.csv') else None,
                                 START_YEAR, END_YEAR, mean=14.0, phi=0.4, sigma=2.5, x0=16.0)
    lend_out = os.path.join(PROC_DIR, "macro_lending_rate.csv")
    _write_csv(lend_out, ["year", "value"], lend)

    prov = make_record(
        dataset_name="macro_timeseries",
        generator="src.generators.synthetic_macro.generate_macro_series",
        source="world_bank or synthetic",
        parameters={"years": [START_YEAR, END_YEAR]},
        artifacts={
            "gdp_growth": Artifact("gdp_growth", gdp_out, "processed", "GDP growth annual %"),
            "inflation": Artifact("inflation", inf_out, "processed", "Inflation annual %"),
            "lending_rate": Artifact("lending_rate", lend_out, "processed", "Lending rate %"),
        }
    )
    save_record(prov, os.path.join(PROV_DIR, "macro_timeseries.json"))


def run_broadband():
    bb = generate_broadband_by_state(END_YEAR, base_penetration_national=48.0)
    bb_out = os.path.join(PROC_DIR, "broadband_by_state.csv")
    _write_csv(bb_out, ["year", "state", "region", "broadband_penetration_pct"], bb)

    prov = make_record(
        dataset_name="broadband_by_state",
        generator="src.generators.broadband_by_state.generate_broadband_by_state",
        source="synthetic",
        parameters={"year": END_YEAR},
        artifacts={"broadband_by_state": Artifact("broadband_by_state", bb_out, "processed", "Broadband penetration by state")}
    )
    save_record(prov, os.path.join(PROV_DIR, "broadband_by_state.json"))


def run_sectoral_growth():
    sec = generate_sectoral_growth(START_YEAR, END_YEAR)
    sec_out = os.path.join(PROC_DIR, "sectoral_growth.csv")
    _write_csv(sec_out, ["year", "sector", "growth_rate_pct"], sec)
    prov = make_record(
        dataset_name="sectoral_growth",
        generator="src.generators.sectoral_growth.generate_sectoral_growth",
        source="synthetic",
        parameters={"years": [START_YEAR, END_YEAR]},
        artifacts={"sectoral_growth": Artifact("sectoral_growth", sec_out, "processed", "Sectoral growth rates")}
    )
    save_record(prov, os.path.join(PROV_DIR, "sectoral_growth.json"))


def run_tech_adoption():
    mm = generate_mobile_money_adoption(START_YEAR, END_YEAR)
    idi = generate_itu_idi(START_YEAR, END_YEAR)

    mm_out = os.path.join(PROC_DIR, "mobile_money_adoption.csv")
    idi_out = os.path.join(PROC_DIR, "itu_idi.csv")

    _write_csv(mm_out, ["year", "mobile_money_adoption_pct"], mm)
    _write_csv(idi_out, ["year", "itu_idi_index"], idi)

    prov = make_record(
        dataset_name="tech_adoption",
        generator="src.generators.tech_adoption",
        source="synthetic",
        parameters={"years": [START_YEAR, END_YEAR]},
        artifacts={
            "mobile_money": Artifact("mobile_money", mm_out, "processed", "Mobile money/FinTech adoption"),
            "itu_idi": Artifact("itu_idi", idi_out, "processed", "ITU ICT Development Index (synthetic)"),
        }
    )
    save_record(prov, os.path.join(PROV_DIR, "tech_adoption.json"))


def _read_csv(path: str) -> List[TDict]:
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def build_combined():
    gdp = _read_csv(os.path.join(PROC_DIR, "macro_gdp_growth.csv"))
    inf = _read_csv(os.path.join(PROC_DIR, "macro_inflation.csv"))
    lend = _read_csv(os.path.join(PROC_DIR, "macro_lending_rate.csv"))
    mm = _read_csv(os.path.join(PROC_DIR, "mobile_money_adoption.csv"))
    idi = _read_csv(os.path.join(PROC_DIR, "itu_idi.csv"))

    # Convert lists to dict keyed by year
    def to_map(rows: List[TDict], key: str, value_key: str) -> TDict[int, float]:
        m: TDict[int, float] = {}
        for r in rows:
            try:
                y = int(float(r[key]))
                v = float(r[value_key])
            except Exception:
                continue
            m[y] = v
        return m

    gdp_m = to_map(gdp, "year", "value")
    inf_m = to_map(inf, "year", "value")
    lend_m = to_map(lend, "year", "value")
    mm_m = to_map(mm, "year", "mobile_money_adoption_pct")
    idi_m = to_map(idi, "year", "itu_idi_index")

    years = sorted(set(gdp_m) | set(inf_m) | set(lend_m) | set(mm_m) | set(idi_m))
    combined_rows: List[TDict] = []
    for y in years:
        row: TDict = {
            "year": y,
            "gdp_growth_pct": gdp_m.get(y, ""),
            "inflation_pct": inf_m.get(y, ""),
            "lending_rate_pct": lend_m.get(y, ""),
            "mobile_money_adoption_pct": mm_m.get(y, ""),
            "itu_idi_index": idi_m.get(y, ""),
        }
        combined_rows.append(row)

    out = os.path.join(COMB_DIR, "macro_tech_combined.csv")
    _write_csv(out, [
        "year",
        "gdp_growth_pct",
        "inflation_pct",
        "lending_rate_pct",
        "mobile_money_adoption_pct",
        "itu_idi_index",
    ], combined_rows)

    prov = make_record(
        dataset_name="macro_tech_combined",
        generator="src.pipeline.build_dataset.build_combined",
        source="processed",
        parameters={},
        artifacts={"macro_tech_combined": Artifact("macro_tech_combined", out, "combined", "Combined macro + tech adoption")}
    )
    save_record(prov, os.path.join(PROV_DIR, "macro_tech_combined.json"))


def main():
    ensure_dirs()
    paths = run_world_bank()
    run_macro(paths)
    run_broadband()
    run_sectoral_growth()
    run_tech_adoption()
    build_combined()
    print("Dataset build complete. See /workspace/data for outputs.")


if __name__ == "__main__":
    main()
