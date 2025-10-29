from __future__ import annotations
import numpy as np
from typing import Dict, Tuple

LAYER_IDS = {
    "anode": 0,
    "electrolyte": 1,
    "cathode": 2,
    "interconnect": 3,
    "sealant": 4,
}


def build_grid(nx: int, ny: int, nz: int, params: Dict[str, float]) -> Dict[str, np.ndarray]:
    # Physical sizes (convert to meters)
    Lx = params["active_area_mm"] * 1e-3
    Ly = params["active_area_mm"] * 1e-3

    thicknesses_um = {
        "anode": params["anode_thickness_um"],
        "electrolyte": params["electrolyte_thickness_um"],
        "cathode": params["cathode_thickness_um"],
        "interconnect": params["interconnect_thickness_um"],
        "sealant": params["sealant_thickness_um"],
    }
    total_thick_m = sum(thicknesses_um.values()) * 1e-6

    # Uniform grid in x,y; non-uniform in z by assigning layer voxels proportionally
    x = np.linspace(0.0, Lx, nx)
    y = np.linspace(0.0, Ly, ny)

    # Assign z layers
    layer_thick_m = {k: v * 1e-6 for k, v in thicknesses_um.items()}
    layer_order = ["anode", "electrolyte", "cathode", "interconnect", "sealant"]
    layer_frac = np.array([layer_thick_m[k] / total_thick_m for k in layer_order])
    layer_cells = np.maximum(1, np.round(layer_frac * nz).astype(int))
    # Adjust to sum to nz
    diff = nz - int(layer_cells.sum())
    if diff != 0:
        # Add/subtract to the thickest layers first
        sort_idx = np.argsort(-layer_cells)
        i = 0
        while diff != 0:
            idx = sort_idx[i % len(sort_idx)]
            if diff > 0:
                layer_cells[idx] += 1
                diff -= 1
            else:
                if layer_cells[idx] > 1:
                    layer_cells[idx] -= 1
                    diff += 1
            i += 1

    z = np.linspace(0.0, total_thick_m, nz)

    # Layer id field over z
    layer_id_z = np.empty(nz, dtype=np.int32)
    start = 0
    for k, ncell in zip(layer_order, layer_cells):
        layer_id_z[start : start + ncell] = LAYER_IDS[k]
        start += ncell

    # Material fields per layer (scalar, simple mapping from params)
    # Thermal conductivity (W/mK)
    k_layer = np.array([
        params["thermal_conductivity_W_per_mK"],  # anode eff
        max(2.0, params["ionic_conductivity_S_per_m"] * 0.2),  # electrolyte proxy
        params["thermal_conductivity_W_per_mK"] * 0.8,  # cathode eff
        max(10.0, params["electronic_conductivity_S_per_m"] * 1e-4),  # interconnect
        1.5,  # sealant
    ])

    E_layer = np.array([
        params["youngs_modulus_GPa"] * 1e9 * 0.5,
        params["youngs_modulus_GPa"] * 1e9 * 0.8,
        params["youngs_modulus_GPa"] * 1e9 * 0.6,
        params["youngs_modulus_GPa"] * 1e9,
        params["youngs_modulus_GPa"] * 1e9 * 0.4,
    ])
    nu_layer = np.clip(params["poisson_ratio"], 0.2, 0.35)
    nu_layer = np.array([nu_layer]*5)
    alpha_layer = np.array([
        params["cte_1_per_K"],
        params["cte_1_per_K"] * 0.9,
        params["cte_1_per_K"] * 1.05,
        params["cte_1_per_K"] * 0.8,
        params["cte_1_per_K"] * 0.7,
    ])

    # Expand to 3D fields by z mapping
    k_field = k_layer[layer_id_z][None, None, :].repeat(nx, axis=0).repeat(ny, axis=1)
    E_field = E_layer[layer_id_z][None, None, :].repeat(nx, axis=0).repeat(ny, axis=1)
    nu_field = nu_layer[layer_id_z][None, None, :].repeat(nx, axis=0).repeat(ny, axis=1)
    alpha_field = alpha_layer[layer_id_z][None, None, :].repeat(nx, axis=0).repeat(ny, axis=1)

    # Mask volumes: anode indices in z
    anode_mask_z = layer_id_z == LAYER_IDS["anode"]

    return {
        "x": x,
        "y": y,
        "z": z,
        "layer_id_z": layer_id_z,
        "k_field": k_field,
        "E_field": E_field,
        "nu_field": nu_field,
        "alpha_field": alpha_field,
        "anode_mask_z": anode_mask_z,
        "layer_cells": {k: int(n) for k, n in zip(layer_order, layer_cells)},
        "total_thickness_m": total_thick_m,
        "Lx": Lx,
        "Ly": Ly,
    }
