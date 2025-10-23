from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import List

from sofc_surrogate import SOFCSurrogate1D, sample_inputs


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_vi_curve(sample_idx: int, j: List[float], v: List[float], out_dir: Path) -> str:
    fn = out_dir / f"vi_curve_{sample_idx:05d}.csv"
    with fn.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["current_density_A_per_cm2", "voltage_V"])
        for jj, vv in zip(j, v):
            writer.writerow([f"{jj:.6f}", f"{vv:.6f}"])
    return str(fn)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate LF SOFC dataset")
    parser.add_argument("--num-samples", type=int, default=10200)
    parser.add_argument("--out-dir", type=str, default="data/lf")
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--vi-points", type=int, default=50)
    parser.add_argument("--start-index", type=int, default=0, help="Starting sample index for filenames")
    args = parser.parse_args()

    # Local PRNG using random.Random seeded in surrogate
    out_dir = Path(args.out_dir)
    curves_dir = out_dir / "curves"
    ensure_dir(curves_dir)

    model = SOFCSurrogate1D(vi_points=args.vi_points, seed=args.seed)

    meta_rows: List[dict] = []

    for k in range(args.num_samples):
        sample_id = args.start_index + k
        inputs = sample_inputs(model.random)
        outputs = model.simulate(inputs)

        curve_path = write_vi_curve(sample_id, outputs.voltage_curve_a_per_cm2, outputs.voltage_curve_v, curves_dir)

        row = {
            "sample_id": sample_id,
            "operating_temperature_C": f"{inputs.operating_temperature_c:.3f}",
            "fuel_utilization": f"{inputs.fuel_utilization:.5f}",
            "current_density_A_per_cm2_max": f"{inputs.current_density_a_per_cm2:.5f}",
            "anode_porosity": f"{inputs.anode_porosity:.5f}",
            "vi_curve_path": curve_path,
            "T_stack_C": f"{outputs.t_stack_c:.3f}",
            "eta_elec": f"{outputs.eta_elec:.5f}",
        }
        meta_rows.append(row)

    ensure_dir(out_dir)
    meta_path = out_dir / "metadata.csv"
    # If metadata exists and start-index > 0, append; otherwise write header
    write_header = not meta_path.exists() or args.start_index == 0
    with meta_path.open("a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "sample_id",
                "operating_temperature_C",
                "fuel_utilization",
                "current_density_A_per_cm2_max",
                "anode_porosity",
                "vi_curve_path",
                "T_stack_C",
                "eta_elec",
            ],
        )
        if write_header:
            writer.writeheader()
        writer.writerows(meta_rows)

    print(f"Wrote metadata rows: {len(meta_rows)} -> {meta_path}")
    print(f"Curves in: {curves_dir}")


if __name__ == "__main__":
    main()
