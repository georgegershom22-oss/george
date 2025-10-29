from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
from tqdm import tqdm

from .sampling import sample_lhs, SampledParameters
from .geometry import Grid, build_layers, assign_layer_indices, make_property_fields
from .physics import (
    SolverGrid,
    solve_potential,
    compute_current_density,
    overpotential_from_current,
    solve_heat,
    compute_species_fields,
    compute_thermo_mechanics,
)
from .io_utils import save_sample_h5, write_manifest
from .config import LayerNames


def _make_dirichlet_masks(nx: int, ny: int, nz: int) -> Dict[str, np.ndarray]:
    mask_z0 = np.zeros((nx, ny, nz), dtype=bool)
    mask_z1 = np.zeros((nx, ny, nz), dtype=bool)
    mask_z0[:, :, 0] = True
    mask_z1[:, :, -1] = True

    mask_x0 = np.zeros((nx, ny, nz), dtype=bool)
    mask_x1 = np.zeros((nx, ny, nz), dtype=bool)
    mask_x0[0, :, :] = True
    mask_x1[-1, :, :] = True
    return {
        "z0": mask_z0,
        "z1": mask_z1,
        "x0": mask_x0,
        "x1": mask_x1,
    }


def _assemble_sigma_total(props: Dict[str, np.ndarray]) -> np.ndarray:
    # Combine ionic and electronic conductivities to a total effective conductivity for Laplace solve
    # Use simple sum as a crude proxy for parallel pathways
    return (props["sigma_e"] + props["sigma_i"]).astype(np.float32)


def _meta_from_sample(idx: int, grid: Grid, sp: SampledParameters) -> Dict[str, Any]:
    return {
        "attributes": {
            "generator": "sofc_hifi 0.1.0",
            "grid_nx": grid.nx,
            "grid_ny": grid.ny,
            "grid_nz": grid.nz,
            "grid_lx_m": grid.lx,
            "grid_ly_m": grid.ly,
            "grid_lz_m": grid.lz,
        },
        "operating": sp.operating,
        "geometry": sp.geometry,
        "materials": sp.materials,
    }


def generate_sample(idx: int, sp: SampledParameters, out_dir: Path, grid: Grid) -> str:
    nx, ny, nz = grid.nx, grid.ny, grid.nz
    masks = _make_dirichlet_masks(nx, ny, nz)

    # Construct layers and z-slices
    layers, _ = build_layers(
        {
            LayerNames.ANODE: sp.geometry["thickness_anode_m"],
            LayerNames.ELECTROLYTE: sp.geometry["thickness_electrolyte_m"],
            LayerNames.CATHODE: sp.geometry["thickness_cathode_m"],
        }
    )
    z_slices = assign_layer_indices(grid, layers)

    # Build property fields
    props = make_property_fields(grid, z_slices, sp.materials)

    # Electrochemical potential solve (Dirichlet at z=0, z=H)
    V_app = sp.operating["voltage_V"]
    dirichlet_phi = {
        "z0": (masks["z0"], V_app),
        "z1": (masks["z1"], 0.0),
    }

    g = SolverGrid(nx=nx, ny=ny, nz=nz, dx=grid.dx, dy=grid.dy, dz=grid.dz)
    sigma_total = _assemble_sigma_total(props)
    phi = solve_potential(dirichlet_phi, sigma_total, g)

    # Current density
    jx, jy, jz, jmag = compute_current_density(phi, sigma_total, g)

    # Heat source: ohmic + reaction heat (approximate)
    # ohmic loss density ~ j^2 / sigma_total (avoid divide by zero)
    q_ohm = (jmag * jmag) / np.maximum(sigma_total, 1e-6)

    # overpotential localized via j0 field; pick representative temperature for kinetics from inlets average
    T_in_mean = 0.5 * (sp.operating["inlet_T_air_K"] + sp.operating["inlet_T_fuel_K"])
    eta = overpotential_from_current(jmag, props["j0"], T_in_mean, alpha=0.5)
    q_rxn = jmag * np.abs(eta)

    q_vol = (q_ohm + q_rxn).astype(np.float32)

    # Thermal BCs: set Dirichlet at x=0, x=L to inlet temps; other boundaries insulated implicitly
    T_dirichlet = {
        "x0": (masks["x0"], float(sp.operating["inlet_T_fuel_K"])) ,
        "x1": (masks["x1"], float(sp.operating["inlet_T_air_K"])) ,
    }
    T = solve_heat(props["k_th"], q_vol, g, T_dirichlet)

    # Species fields restricted to anode region
    anode_mask = np.zeros((nx, ny, nz), dtype=bool)
    anode_mask[:, :, z_slices[LayerNames.ANODE]] = True
    c_h2, c_h2o = compute_species_fields(
        jmag=jmag,
        anode_mask=anode_mask,
        fuel_flow_rate_m3_per_s=float(sp.operating["fuel_flow_rate_m3_per_s"]),
        porosity=props["porosity"],
        g=g,
        c_h2_in=1.0,
    )

    # Thermo-mechanics approximations
    sigma_vm, eps_eq, ux, uy, uz = compute_thermo_mechanics(
        T=T,
        E=props["E"],
        nu=props["nu"],
        alpha=props["alpha"],
        T_ref=T_in_mean,
    )

    # Bundle outputs
    fields = {
        # potentials and current
        "phi": phi,
        "current_density_x": jx,
        "current_density_y": jy,
        "current_density_z": jz,
        "current_density_mag": jmag,
        # thermal
        "temperature_K": T,
        # species
        "H2_concentration": c_h2,
        "H2O_concentration": c_h2o,
        # mechanics
        "stress_von_mises_Pa": sigma_vm,
        "strain_eq": eps_eq,
        "displacement_x_m": ux,
        "displacement_y_m": uy,
        "displacement_z_m": uz,
    }

    # Save
    out_file = out_dir / f"run_{idx:05d}.h5"
    meta = _meta_from_sample(idx, grid, sp)
    save_sample_h5(out_file, idx, meta, fields)
    return str(out_file)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate synthetic high-fidelity SOFC multiphysics dataset (HDF5 per run)")
    ap.add_argument("--out-dir", type=str, required=True, help="Output directory for dataset files")
    ap.add_argument("--num-samples", type=int, default=10, help="Number of simulation runs to generate")
    ap.add_argument("--grid", type=int, nargs=3, default=[24, 24, 18], metavar=("NX", "NY", "NZ"), help="Grid resolution in x,y,z")
    ap.add_argument("--size-m", type=float, nargs=3, default=[0.05, 0.05, 0.001], metavar=("LX", "LY", "LZ"), help="Physical size in meters along x,y,z")
    ap.add_argument("--seed", type=int, default=42, help="Random seed for sampling")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    nx, ny, nz = args.grid
    lx, ly, lz = args.size_m
    grid = Grid(nx=nx, ny=ny, nz=nz, lx=lx, ly=ly, lz=lz)

    samples: List[SampledParameters] = sample_lhs(num_samples=args.num_samples, seed=args.seed)

    manifest: Dict[str, Any] = {
        "num_samples": args.num_samples,
        "grid": {"nx": nx, "ny": ny, "nz": nz, "lx_m": lx, "ly_m": ly, "lz_m": lz},
        "files": [],
    }

    for idx, sp in enumerate(tqdm(samples, desc="Generating", total=len(samples))):
        out_file = generate_sample(idx, sp, out_dir, grid)
        manifest["files"].append({
            "index": idx,
            "path": str(Path(out_file).name),
        })

    write_manifest(out_dir / "manifest.json", manifest)


if __name__ == "__main__":
    main()
