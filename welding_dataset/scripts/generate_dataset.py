#!/usr/bin/env python
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import asdict

import pandas as pd

# Ensure project root is on sys.path so that `src.*` imports work
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.generators.physics_generator import generate_many


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic welding dataset")
    parser.add_argument("--rows", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--outdir", type=str, default="data/synthetic")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    records_ip = []
    records_cm = []
    records_pm = []

    for ip, cm, pm in generate_many(args.rows, args.seed):
        records_ip.append(asdict(ip))
        records_cm.append(asdict(cm))
        records_pm.append(asdict(pm))

    df_ip = pd.DataFrame(records_ip)
    df_cm = pd.DataFrame(records_cm)
    df_pm = pd.DataFrame(records_pm)

    df_ip.to_csv(os.path.join(args.outdir, "input_parameters.csv"), index=False)
    df_cm.to_csv(os.path.join(args.outdir, "characterization_metrics.csv"), index=False)
    df_pm.to_csv(os.path.join(args.outdir, "performance_metrics.csv"), index=False)

    # Merge for convenience
    df_all = pd.concat([df_ip, df_cm, df_pm], axis=1)
    df_all.to_csv(os.path.join(args.outdir, "welding_dataset_all.csv"), index=False)

    # basic splits
    # ensure splits directory exists
    splits_dir = os.path.join("data", "splits")
    os.makedirs(splits_dir, exist_ok=True)

    n = len(df_all)
    train_end = int(0.8 * n)
    val_end = int(0.9 * n)
    df_all.iloc[:train_end].to_csv(os.path.join(splits_dir, "train.csv"), index=False)
    df_all.iloc[train_end:val_end].to_csv(os.path.join(splits_dir, "val.csv"), index=False)
    df_all.iloc[val_end:].to_csv(os.path.join(splits_dir, "test.csv"), index=False)

    # Write a simple data dictionary for convenience
    dict_rows = [
        {"column": "anode_material", "unit": "-", "description": "Anode material (e.g., Cu)"},
        {"column": "cathode_material", "unit": "-", "description": "Cathode material (e.g., Al)"},
        {"column": "tab_thickness_um", "unit": "µm", "description": "Tab thickness controlling heat dissipation"},
        {"column": "surface_finish", "unit": "-", "description": "Surface coating/finish"},
        {"column": "welding_technique", "unit": "-", "description": "USW, Laser, or RSW"},
        {"column": "power", "unit": "W or J", "description": "Peak power (USW/RSW) or pulse energy (Laser)"},
        {"column": "amplitude_um", "unit": "µm", "description": "USW vibration amplitude"},
        {"column": "force_n", "unit": "N", "description": "Clamping/forge force"},
        {"column": "pressure_mpa", "unit": "MPa", "description": "Applied pressure"},
        {"column": "time_s", "unit": "s", "description": "Weld duration"},
        {"column": "speed_mm_s", "unit": "mm/s", "description": "Laser welding speed"},
        {"column": "pulse_frequency_hz", "unit": "Hz", "description": "Laser pulse frequency"},
        {"column": "preheat_c", "unit": "°C", "description": "Preheat temperature"},
        {"column": "max_interface_temperature_c", "unit": "°C", "description": "Max interface temperature"},
        {"column": "heat_input_j", "unit": "J", "description": "Estimated heat input"},
        {"column": "bond_area_mm2", "unit": "mm^2", "description": "Estimated bonded area"},
        {"column": "porosity_pct", "unit": "%", "description": "Porosity percentage"},
        {"column": "void_fraction_pct", "unit": "%", "description": "Void fraction percentage"},
        {"column": "interface_resistance_mohm", "unit": "mΩ", "description": "Interface electrical resistance"},
        {"column": "nugget_diameter_mm", "unit": "mm", "description": "Equivalent nugget diameter"},
        {"column": "haze_color_index", "unit": "-", "description": "Oxidation/haze index"},
        {"column": "surface_roughness_ra_um", "unit": "µm", "description": "Surface roughness Ra"},
        {"column": "thermal_cycling_cycles_to_failure", "unit": "cycles", "description": "Thermal cycling life"},
        {"column": "resistance_growth_pct_after_cycling", "unit": "%", "description": "Resistance growth after cycling"},
        {"column": "shear_strength_mpa", "unit": "MPa", "description": "Shear strength"},
        {"column": "peel_strength_n", "unit": "N", "description": "Peel strength"},
        {"column": "fracture_mode", "unit": "-", "description": "Failure mode"},
        {"column": "microcrack_density_per_mm", "unit": "1/mm", "description": "Microcrack density"},
    ]
    pd.DataFrame(dict_rows).to_csv(os.path.join(args.outdir, "data_dictionary.csv"), index=False)

    print(f"Wrote: {args.outdir}/input_parameters.csv, characterization_metrics.csv, performance_metrics.csv, welding_dataset_all.csv")
    print("Wrote: data/splits/train.csv, val.csv, test.csv")


if __name__ == "__main__":
    main()
