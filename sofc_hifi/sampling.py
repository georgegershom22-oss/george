from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Tuple, List

import numpy as np
from scipy.stats.qmc import LatinHypercube, scale

from .config import (
    DEFAULT_OPERATING_RANGES,
    DEFAULT_GEOMETRY_RANGES,
    DEFAULT_MATERIAL_RANGES,
    LAYER_ORDER,
    LayerNames,
)


@dataclass
class SampledParameters:
    operating: Dict[str, float]
    geometry: Dict[str, float]
    materials: Dict[str, Dict[str, float]]  # materials[layer][prop]


def _ranges_to_bounds(ranges_dict: Dict[str, Tuple[float, float]]) -> Tuple[List[str], np.ndarray, np.ndarray]:
    keys = list(ranges_dict.keys())
    mins = np.array([ranges_dict[k][0] for k in keys], dtype=float)
    maxs = np.array([ranges_dict[k][1] for k in keys], dtype=float)
    return keys, mins, maxs


def sample_lhs(num_samples: int, seed: int | None = None) -> List[SampledParameters]:
    rng = np.random.default_rng(seed)

    # Build flat bounds arrays for operating, geometry
    op_ranges = DEFAULT_OPERATING_RANGES.__dict__
    op_keys, op_mins, op_maxs = _ranges_to_bounds(op_ranges)

    geo_ranges = DEFAULT_GEOMETRY_RANGES.__dict__
    geo_keys, geo_mins, geo_maxs = _ranges_to_bounds(geo_ranges)

    # Material ranges per-layer per-property; flatten keys like "anode.sigma_electronic"
    mat = DEFAULT_MATERIAL_RANGES
    material_specs: Dict[str, Dict[str, Tuple[float, float]]] = {
        "porosity": mat.porosity,
        "permeability": mat.permeability,
        "sigma_electronic": mat.sigma_electronic,
        "sigma_ionic": mat.sigma_ionic,
        "k_thermal": mat.k_thermal,
        "youngs_modulus": mat.youngs_modulus,
        "poisson_ratio": mat.poisson_ratio,
        "cte": mat.cte,
    }

    # exchange current only on electrodes
    j0_specs: Dict[str, Dict[str, Tuple[float, float]]] = {
        "j0_exchange": {
            LayerNames.ANODE: mat.j0_exchange[LayerNames.ANODE],
            LayerNames.CATHODE: mat.j0_exchange[LayerNames.CATHODE],
        }
    }

    flat_keys: List[str] = []
    mins_list: List[float] = []
    maxs_list: List[float] = []

    for prop_name, layers in {**material_specs, **j0_specs}.items():
        for layer in LAYER_ORDER:
            if layer not in layers:
                continue
            lo, hi = layers[layer]
            flat_keys.append(f"{layer}.{prop_name}")
            mins_list.append(lo)
            maxs_list.append(hi)

    mat_keys = flat_keys
    mat_mins = np.array(mins_list, dtype=float)
    mat_maxs = np.array(maxs_list, dtype=float)

    # Total dimension for LHS
    dim = len(op_keys) + len(geo_keys) + len(mat_keys)
    engine = LatinHypercube(d=dim, seed=seed)
    unit_samples = engine.random(n=num_samples)

    # Scale to physical ranges
    mins_all = np.concatenate([op_mins, geo_mins, mat_mins])
    maxs_all = np.concatenate([op_maxs, geo_maxs, mat_maxs])
    scaled = scale(unit_samples, mins_all, maxs_all)

    results: List[SampledParameters] = []
    for row in scaled:
        op_vals = row[0:len(op_keys)]
        geo_vals = row[len(op_keys):len(op_keys)+len(geo_keys)]
        mat_vals = row[len(op_keys)+len(geo_keys):]

        operating = {k: float(v) for k, v in zip(op_keys, op_vals)}
        geometry = {k: float(v) for k, v in zip(geo_keys, geo_vals)}

        materials: Dict[str, Dict[str, float]] = {layer: {} for layer in LAYER_ORDER}
        for k, v in zip(mat_keys, mat_vals):
            layer, prop = k.split(".", 1)
            materials[layer][prop] = float(v)

        results.append(SampledParameters(operating=operating, geometry=geometry, materials=materials))

    return results
