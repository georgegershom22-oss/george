from __future__ import annotations

import itertools
import json
import math
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Tuple

import csv
import random

from .model import SOFCLumped1D


@dataclass
class SampleParams:
    temperature_C: float
    fuel_utilization: float
    anode_porosity: float
    j_max_A_per_m2: float
    curve_points: int


RNG_SEED = 42


def latin_hypercube(n: int, d: int, rng: random.Random) -> List[List[float]]:
    # Simple LHS sampler on [0,1]^d without numpy
    segments = []
    for i in range(n):
        row = []
        for _ in range(d):
            row.append((i + rng.random()) / n)
        segments.append(row)
    # Shuffle each column independently
    for k in range(d):
        rng.shuffle(segments)
    return segments


def sample_params(num_samples: int, rng: random.Random) -> List[SampleParams]:
    # Ranges
    T_min_C, T_max_C = 700.0, 900.0
    fu_min, fu_max = 0.6, 0.9
    eps_min, eps_max = 0.2, 0.5

    lhs = latin_hypercube(num_samples, 3, rng)
    temps_C = [T_min_C + (T_max_C - T_min_C) * row[0] for row in lhs]
    fu = [fu_min + (fu_max - fu_min) * row[1] for row in lhs]
    eps = [eps_min + (eps_max - eps_min) * row[2] for row in lhs]

    # Vary j_max with temperature for diversity
    j_max = [10000.0 + 7000.0 * (t - T_min_C) / (T_max_C - T_min_C) for t in temps_C]

    params = [
        SampleParams(
            temperature_C=float(t),
            fuel_utilization=float(f),
            anode_porosity=float(e),
            j_max_A_per_m2=float(jm),
            curve_points=60,
        )
        for t, f, e, jm in zip(temps_C, fu, eps, j_max)
    ]
    return params


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def generate(num_samples: int, output_dir: str, manifest_name: str = "manifest.csv", seed: int = RNG_SEED) -> None:
    _ensure_dir(output_dir)
    rng = random.Random(seed)
    model = SOFCLumped1D()

    manifest_rows: List[Dict] = []

    params_list = sample_params(num_samples, rng)

    curves_dir = os.path.join(output_dir, "curves")
    _ensure_dir(curves_dir)

    for idx, sp in enumerate(params_list):
        T_K = sp.temperature_C + 273.15
        j, V, T_stack, eta = model.vi_curve(
            temperature_K=T_K,
            fuel_utilization=sp.fuel_utilization,
            anode_porosity=sp.anode_porosity,
            j_max=sp.j_max_A_per_m2,
            num_points=sp.curve_points,
        )
        curve_fname = f"sample_{idx:06d}.csv"
        curve_path = os.path.join(curves_dir, curve_fname)
        with open(curve_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["current_density_A_per_m2", "voltage_V"])
            for a, b in zip(j, V):
                writer.writerow([f"{a:.6f}", f"{b:.6f}"])

        manifest_rows.append(
            {
                "sample_id": idx,
                "temperature_C": sp.temperature_C,
                "fuel_utilization": sp.fuel_utilization,
                "anode_porosity": sp.anode_porosity,
                "j_max_A_per_m2": sp.j_max_A_per_m2,
                "curve_points": sp.curve_points,
                "curve_file": os.path.relpath(curve_path, output_dir),
                "T_stack_K": float(T_stack),
                "eta_elec": float(eta),
            }
        )

    manifest_path = os.path.join(output_dir, manifest_name)
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "sample_id",
                "temperature_C",
                "fuel_utilization",
                "anode_porosity",
                "j_max_A_per_m2",
                "curve_points",
                "curve_file",
                "T_stack_K",
                "eta_elec",
            ],
        )
        writer.writeheader()
        for row in manifest_rows:
            writer.writerow(row)

    meta = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "num_samples": num_samples,
        "ranges": {
            "temperature_C": [700.0, 900.0],
            "fuel_utilization": [0.6, 0.9],
            "anode_porosity": [0.2, 0.5],
        },
        "notes": "Low-fidelity SOFC 1D lumped surrogate dataset",
    }
    with open(os.path.join(output_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"Wrote manifest to {manifest_path}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate LF SOFC dataset")
    parser.add_argument("--num-samples", type=int, required=True)
    parser.add_argument("--output-dir", type=str, required=True)
    parser.add_argument("--manifest-name", type=str, default="manifest.csv")
    parser.add_argument("--seed", type=int, default=RNG_SEED)
    args = parser.parse_args()

    generate(
        num_samples=args.num_samples,
        output_dir=args.output_dir,
        manifest_name=args.manifest_name,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
