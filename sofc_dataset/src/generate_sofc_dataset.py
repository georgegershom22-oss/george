from __future__ import annotations
import argparse
import os
from typing import Dict, Any
import numpy as np
from tqdm import tqdm

from .sampling import sample_parameters
from .geometry import build_grid
from .physics import (
    generate_current_density_interface,
    volumetric_heat_source_from_interface,
    solve_temperature,
    species_fields,
    thermoelastic_stress,
    approximate_displacement_z,
)
from .io_utils import write_run_h5, append_metadata_csv


def run_generation(
    out_dir: str,
    n_samples: int,
    nx: int,
    ny: int,
    nz: int,
    seed: int | None = None,
) -> str:
    rng = np.random.default_rng(seed)
    params_df = sample_parameters(n_samples=n_samples, seed=seed)

    meta_csv = os.path.join(out_dir, "metadata.csv")
    os.makedirs(out_dir, exist_ok=True)

    for idx in tqdm(range(n_samples), desc="Generating SOFC runs"):
        params_row = params_df.iloc[idx].to_dict()
        grid = build_grid(nx=nx, ny=ny, nz=nz, params=params_row)

        j_xy, eta_xy = generate_current_density_interface(params_row, grid, seed=rng.integers(0, 1<<31))
        q = volumetric_heat_source_from_interface(j_xy, eta_xy, grid)

        T = solve_temperature(q=q, k_field=grid["k_field"], params=params_row, grid=grid, n_iter=250)

        c_h2, c_h2o = species_fields(params_row, grid, j_xy)

        sigma_xx, sigma_yy, sigma_zz, tau_xy, tau_xz, tau_yz, von_mises = thermoelastic_stress(T, grid)
        uz = approximate_displacement_z(T, grid)

        fields = {
            "temperature_K": T.astype(np.float32),
            "current_density_A_per_m2": j_xy.astype(np.float32),
            "overpotential_V": eta_xy.astype(np.float32),
            "heat_source_W_per_m3": q.astype(np.float32),
            "sigma_xx_Pa": sigma_xx,
            "sigma_yy_Pa": sigma_yy,
            "sigma_zz_Pa": sigma_zz,
            "tau_xy_Pa": tau_xy,
            "tau_xz_Pa": tau_xz,
            "tau_yz_Pa": tau_yz,
            "von_mises_Pa": von_mises,
            "displacement_z_m": uz.astype(np.float32),
            "c_h2_mol_per_m3": c_h2.astype(np.float32),
            "c_h2o_mol_per_m3": c_h2o.astype(np.float32),
        }

        file_path = write_run_h5(out_dir=out_dir, run_id=idx, params=params_row, fields=fields)
        append_metadata_csv(csv_path=meta_csv, run_id=idx, file_path=file_path, params=params_row)

    return meta_csv


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic high-fidelity SOFC multi-physics dataset")
    parser.add_argument("--out", default="/workspace/sofc_dataset/data/sofc_hifi", help="Output directory")
    parser.add_argument("--n", type=int, default=10, help="Number of runs")
    parser.add_argument("--nx", type=int, default=64)
    parser.add_argument("--ny", type=int, default=64)
    parser.add_argument("--nz", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()
    meta = run_generation(out_dir=args.out, n_samples=args.n, nx=args.nx, ny=args.ny, nz=args.nz, seed=args.seed)
    print(f"Wrote metadata to: {meta}")


if __name__ == "__main__":
    main()
