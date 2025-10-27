#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

from welding_dataset.generator import generate_dataset


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic welding dataset with physics-inspired relationships.")
    parser.add_argument("--rows", type=int, default=5000, help="Number of rows to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--outdir", type=str, default=str(Path(__file__).resolve().parents[1] / "artifacts"), help="Output directory")
    parser.add_argument("--basename", type=str, default="welding_dataset", help="Base filename for outputs")
    parser.add_argument("--splits", type=str, default="0.8,0.1,0.1", help="Train,Val,Test split fractions")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df, meta = generate_dataset(args.rows, seed=args.seed)

    csv_path = outdir / f"{args.basename}.csv"
    parquet_path = outdir / f"{args.basename}.parquet"
    meta_path = outdir / f"{args.basename}.metadata.json"
    schema_path = outdir / f"{args.basename}.schema.json"

    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)

    # Train/Val/Test splits
    splits = [float(x) for x in args.splits.split(",")]
    assert np.isclose(sum(splits), 1.0, atol=1e-6), "Splits must sum to 1.0"
    n = len(df)
    n_train = int(splits[0] * n)
    n_val = int(splits[1] * n)
    idx = np.random.default_rng(args.seed).permutation(n)
    train_idx = idx[:n_train]
    val_idx = idx[n_train:n_train + n_val]
    test_idx = idx[n_train + n_val:]

    df.iloc[train_idx].to_parquet(outdir / f"{args.basename}.train.parquet", index=False)
    df.iloc[val_idx].to_parquet(outdir / f"{args.basename}.val.parquet", index=False)
    df.iloc[test_idx].to_parquet(outdir / f"{args.basename}.test.parquet", index=False)

    # Technique-specific subsets
    for tech in sorted(df["technique"].unique()):
        df[df["technique"] == tech].to_parquet(outdir / f"{args.basename}.{tech}.parquet", index=False)

    # Summary statistics and correlation matrix
    summary_path = outdir / f"{args.basename}.summary.json"
    corr_path = outdir / f"{args.basename}.corr.parquet"
    numeric_df = df.select_dtypes(include=["number"])  # only numeric for corr
    summary = numeric_df.describe().to_dict()
    pd.DataFrame(numeric_df.corr(numeric_only=True)).to_parquet(corr_path)
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    # Data dictionary
    data_dictionary = {
        "anode_material": {"unit": "-", "desc": "Anode base material"},
        "cathode_material": {"unit": "-", "desc": "Cathode base material"},
        "tab_thickness_um": {"unit": "um", "desc": "Tab thickness"},
        "surface_finish": {"unit": "-", "desc": "Surface finish/coating"},
        "technique": {"unit": "-", "desc": "Welding technique"},
        "power_w_or_energy_j": {"unit": "W or J", "desc": "Power (USW/RSW) or energy (Laser)"},
        "amplitude_um": {"unit": "um", "desc": "USW vibration amplitude"},
        "force_n": {"unit": "N", "desc": "Clamping force"},
        "pressure_mpa": {"unit": "MPa", "desc": "Contact pressure"},
        "time_ms_or_s": {"unit": "ms or s", "desc": "Weld duration"},
        "speed_mm_s": {"unit": "mm/s", "desc": "Laser weld speed"},
        "pulse_frequency_hz": {"unit": "Hz", "desc": "Laser pulse frequency"},
        "preheat_temp_c": {"unit": "C", "desc": "Preheat temperature"},
        "nugget_diameter_mm": {"unit": "mm", "desc": "Estimated nugget diameter"},
        "weld_area_mm2": {"unit": "mm^2", "desc": "Weld area"},
        "max_interface_temp_c": {"unit": "C", "desc": "Max interface temperature"},
        "heat_input_j": {"unit": "J", "desc": "Total heat input"},
        "energy_density_j_mm2": {"unit": "J/mm^2", "desc": "Energy density"},
        "interfacial_resistance_milliohm": {"unit": "mΩ", "desc": "Interfacial resistance"},
        "porosity_percent": {"unit": "%", "desc": "Porosity"},
        "misalignment_um": {"unit": "um", "desc": "Toolpath misalignment"},
        "tensile_shear_strength_mpa": {"unit": "MPa", "desc": "Tensile shear strength"},
        "peel_strength_n_mm": {"unit": "N/mm", "desc": "Peel strength"},
        "cycles_to_failure_thermal": {"unit": "cycles", "desc": "Thermal cycling to failure"},
        "resistance_growth_percent": {"unit": "%", "desc": "Resistance growth post-cycling"},
        "crack_length_mm": {"unit": "mm", "desc": "Crack length after cycling"},
        "delamination_area_percent": {"unit": "%", "desc": "Delamination area fraction"},
    }
    dict_path = outdir / f"{args.basename}.data_dictionary.json"
    with open(dict_path, "w") as f:
        json.dump(data_dictionary, f, indent=2)

    with open(meta_path, "w") as f:
        json.dump(meta.model_dump(), f, indent=2)

    # Save a simple inferred schema (dtypes) for convenience
    schema = {c: str(t) for c, t in df.dtypes.items()}
    with open(schema_path, "w") as f:
        json.dump(schema, f, indent=2)

    print(f"Wrote: {csv_path}")
    print(f"Wrote: {parquet_path}")
    print(f"Wrote: {meta_path}")
    print(f"Wrote: {schema_path}")
    print(f"Wrote: {outdir / (args.basename + '.train.parquet')}")
    print(f"Wrote: {outdir / (args.basename + '.val.parquet')}")
    print(f"Wrote: {outdir / (args.basename + '.test.parquet')}")
    print(f"Wrote: {summary_path}")
    print(f"Wrote: {corr_path}")
    print(f"Wrote: {dict_path}")


if __name__ == "__main__":
    main()
