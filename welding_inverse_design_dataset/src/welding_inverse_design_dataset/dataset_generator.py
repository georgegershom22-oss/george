from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit

from .process_models import sample_process_parameters
from .forward_models import compute_forward_outputs
from .performance_models import compute_performance_targets


COLUMN_SPECS: List[Dict[str, str]] = [
    {"name": "id", "unit": "-", "desc": "Unique row identifier"},
    {"name": "seed", "unit": "-", "desc": "Random seed used"},
    {"name": "technique", "unit": "-", "desc": "Welding technique: USW/Laser/RSW"},
    {"name": "anode_material", "unit": "-", "desc": "Anode material"},
    {"name": "cathode_material", "unit": "-", "desc": "Cathode material"},
    {"name": "anode_thickness_um", "unit": "um", "desc": "Anode thickness"},
    {"name": "cathode_thickness_um", "unit": "um", "desc": "Cathode thickness"},
    {"name": "surface_finish", "unit": "-", "desc": "Surface finish prior to weld"},
    {"name": "coating", "unit": "-", "desc": "Surface coating"},
    {"name": "preheat_temperature_C", "unit": "C", "desc": "Preheat temperature"},
    {"name": "tool_contact_area_mm2", "unit": "mm2", "desc": "Tool/electrode contact area"},
    {"name": "weld_length_mm", "unit": "mm", "desc": "Weld track length (laser)"},
    {"name": "spot_diameter_um", "unit": "um", "desc": "Laser spot diameter"},
    {"name": "power_W", "unit": "W", "desc": "Power"},
    {"name": "pulse_energy_J", "unit": "J", "desc": "Pulse energy (laser)"},
    {"name": "amplitude_um", "unit": "um", "desc": "Ultrasonic amplitude"},
    {"name": "force_N", "unit": "N", "desc": "Clamping/electrode force"},
    {"name": "pressure_MPa", "unit": "MPa", "desc": "Contact pressure"},
    {"name": "time_ms", "unit": "ms", "desc": "Weld duration"},
    {"name": "speed_mm_s", "unit": "mm/s", "desc": "Laser travel speed"},
    {"name": "pulse_frequency_Hz", "unit": "Hz", "desc": "Laser pulse frequency"},
    {"name": "energy_input_J", "unit": "J", "desc": "Effective energy input"},
    {"name": "linear_energy_density_J_per_mm", "unit": "J/mm", "desc": "Laser linear energy density"},
    {"name": "peak_temperature_C", "unit": "C", "desc": "Peak bulk temperature"},
    {"name": "interface_temperature_C", "unit": "C", "desc": "Peak interface temperature"},
    {"name": "HAZ_width_mm", "unit": "mm", "desc": "Heat-affected zone width"},
    {"name": "cooling_rate_C_per_s", "unit": "C/s", "desc": "Cooling rate"},
    {"name": "nugget_diameter_mm", "unit": "mm", "desc": "Weld nugget diameter"},
    {"name": "bond_area_mm2", "unit": "mm2", "desc": "Bonded area"},
    {"name": "contact_resistance_mOhm", "unit": "mOhm", "desc": "Initial contact resistance"},
    {"name": "porosity_fraction", "unit": "-", "desc": "Porosity fraction"},
    {"name": "void_count", "unit": "-", "desc": "Void count"},
    {"name": "immediate_lap_shear_strength_N", "unit": "N", "desc": "Immediate lap shear strength"},
    {"name": "microhardness_HV", "unit": "HV", "desc": "Microhardness in HAZ"},
    {"name": "IMC_thickness_um", "unit": "um", "desc": "Intermetallic layer thickness"},
    {"name": "cycles_to_failure_thermal", "unit": "cycles", "desc": "Cycles to failure under thermal cycling"},
    {"name": "resistance_drift_mOhm_after_1000_cycles", "unit": "mOhm", "desc": "Resistance drift after 1000 cycles"},
    {"name": "peel_strength_retained_pct", "unit": "%", "desc": "Peel strength retained after cycling"},
    {"name": "crack_growth_rate_mm_per_cycle", "unit": "mm/cycle", "desc": "Crack growth rate"},
    {"name": "pass_1000_cycles", "unit": "bool", "desc": "Pass/fail at 1000 cycles"},
    {"name": "failure_mode", "unit": "-", "desc": "Dominant failure mode"},
]


def _make_schema() -> Dict:
    props = {}
    for spec in COLUMN_SPECS:
        t = "string"
        if spec["name"] in {"id", "void_count", "seed"}:
            t = "integer"
        elif spec["name"].startswith("pass_"):
            t = "boolean"
        elif spec["name"] in {"technique", "anode_material", "cathode_material", "surface_finish", "coating", "failure_mode"}:
            t = "string"
        else:
            t = "number"
        props[spec["name"]] = {"type": t, "description": spec["desc"], "unit": spec["unit"]}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Welding Inverse Design Dataset",
        "type": "object",
        "properties": props,
        "required": [s["name"] for s in COLUMN_SPECS],
        "additionalProperties": False,
    }


def _write_docs(base: Path, schema: Dict) -> None:
    docs = base / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "schema.json").write_text(json.dumps(schema, indent=2))

    lines = ["# Data Dictionary\n\n"]
    lines.append("| Column | Unit | Description |\n")
    lines.append("|---|---|---|\n")
    for s in COLUMN_SPECS:
        lines.append(f"| {s['name']} | {s['unit']} | {s['desc']} |\n")
    (docs / "data_dictionary.md").write_text("".join(lines))

    readme = f"""
# ML-Driven Inverse Design of Welding Parameters Dataset

This synthetic, physics-informed dataset provides three linked sections:
- Input Parameters (design space)
- Characterization & Quality Metrics (forward outputs)
- Performance & Validation Metrics (inverse design targets)

Files:
- data/processed/welding_dataset.parquet (primary)
- data/processed/welding_dataset.csv
- data/splits/train_ids.csv, val_ids.csv, test_ids.csv
- docs/schema.json (JSON Schema)
- docs/data_dictionary.md

License: CC BY 4.0
"""
    (docs / "README.md").write_text(readme.strip() + "\n")


def generate_dataset(n_samples: int, seed: int, out_dir: Path) -> Tuple[pd.DataFrame, Dict]:
    rng = np.random.default_rng(seed)

    inputs = sample_process_parameters(n_samples, rng)
    inputs.insert(0, "seed", seed)
    inputs.insert(0, "id", np.arange(n_samples, dtype=int))

    forwards = compute_forward_outputs(inputs)
    perf = compute_performance_targets(inputs.reset_index(drop=True), forwards.reset_index(drop=True), rng)

    df = pd.concat([inputs, forwards, perf], axis=1)

    schema = _make_schema()
    return df, schema


def stratified_splits(df: pd.DataFrame, seed: int) -> Dict[str, np.ndarray]:
    # stratify by technique and pass_1000_cycles
    y = df["technique"].astype(str) + "_" + df["pass_1000_cycles"].astype(str)
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.15, random_state=seed)
    idx = np.arange(len(df))
    train_idx, test_idx = next(splitter.split(idx, y))

    y_train = y.iloc[train_idx]
    splitter2 = StratifiedShuffleSplit(n_splits=1, test_size=0.1765, random_state=seed)  # 0.1765 of 0.85 ~ 0.15
    train_idx2, val_idx = next(splitter2.split(train_idx, y_train))
    train_final = train_idx[train_idx2]

    return {"train": train_final, "val": val_idx, "test": test_idx}


def save_all(df: pd.DataFrame, schema: Dict, splits: Dict[str, np.ndarray], base: Path) -> None:
    data_dir = base / "data" / "processed"
    split_dir = base / "data" / "splits"
    data_dir.mkdir(parents=True, exist_ok=True)
    split_dir.mkdir(parents=True, exist_ok=True)

    parquet_path = data_dir / "welding_dataset.parquet"
    csv_path = data_dir / "welding_dataset.csv"
    df.to_parquet(parquet_path, index=False)
    df.to_csv(csv_path, index=False)

    for k, ids in splits.items():
        pd.DataFrame({"id": ids}).to_csv(split_dir / f"{k}_ids.csv", index=False)

    _write_docs(base, schema)


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--out", type=str, default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()

    base = Path(args.out)
    df, schema = generate_dataset(args.n, args.seed, base)
    splits = stratified_splits(df, args.seed)
    save_all(df, schema, splits, base)

    print(f"Saved dataset with {len(df)} rows under {base}")


if __name__ == "__main__":
    main()
