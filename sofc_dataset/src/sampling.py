from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from .config import ParameterRanges, default_ranges


def latin_hypercube(n_samples: int, n_dims: int, seed: int | None = None) -> np.ndarray:
    rng = np.random.default_rng(seed)
    # Stratify each dimension into n_samples bins
    cut = np.linspace(0, 1, n_samples + 1)
    u = rng.random((n_samples, n_dims))
    a = cut[:-1]
    b = cut[1:]
    # For each dimension, randomly permute the bins
    lhs = np.zeros_like(u)
    for j in range(n_dims):
        perm = rng.permutation(n_samples)
        lhs[:, j] = a[perm] + (b[perm] - a[perm]) * u[:, j]
    return lhs


def sample_parameters(n_samples: int, seed: int | None = None, ranges: ParameterRanges | None = None) -> pd.DataFrame:
    if ranges is None:
        ranges = default_ranges()

    # Define scalar parameters to sample
    param_specs: List[Tuple[str, Tuple[float, float]]] = [
        ("voltage_V", ranges.voltage_V),
        ("current_density_A_per_cm2", ranges.current_density_A_per_cm2),
        ("air_flow_sLpm", ranges.air_flow_sLpm),
        ("fuel_flow_sLpm", ranges.fuel_flow_sLpm),
        ("air_inlet_T_K", ranges.air_inlet_T_K),
        ("fuel_inlet_T_K", ranges.fuel_inlet_T_K),
        ("porosity", ranges.porosity),
        ("permeability_m2", ranges.permeability_m2),
        ("ionic_conductivity_S_per_m", ranges.ionic_conductivity_S_per_m),
        ("electronic_conductivity_S_per_m", ranges.electronic_conductivity_S_per_m),
        ("youngs_modulus_GPa", ranges.youngs_modulus_GPa),
        ("cte_1_per_K", ranges.cte_1_per_K),
        ("poisson_ratio", ranges.poisson_ratio),
        ("thermal_conductivity_W_per_mK", ranges.thermal_conductivity_W_per_mK),
        ("anode_thickness_um", ranges.anode_thickness_um),
        ("electrolyte_thickness_um", ranges.electrolyte_thickness_um),
        ("cathode_thickness_um", ranges.cathode_thickness_um),
        ("interconnect_thickness_um", ranges.interconnect_thickness_um),
        ("sealant_thickness_um", ranges.sealant_thickness_um),
        ("active_area_mm", ranges.active_area_mm),
        ("i0_A_per_cm2", ranges.i0_A_per_cm2),
        ("alpha", ranges.alpha),
    ]

    lhs = latin_hypercube(n_samples, len(param_specs), seed)

    data = {}
    for i, (name, (lo, hi)) in enumerate(param_specs):
        if name in ("num_flow_channels",):
            continue
        data[name] = lo + lhs[:, i] * (hi - lo)

    # Handle integer parameter separately
    rng = np.random.default_rng(seed)
    nchan_lo, nchan_hi = ranges.num_flow_channels
    data["num_flow_channels"] = rng.integers(nchan_lo, nchan_hi + 1, size=n_samples)

    df = pd.DataFrame(data)
    # Helpful derived parameters
    df["total_thickness_um"] = (
        df["anode_thickness_um"]
        + df["electrolyte_thickness_um"]
        + df["cathode_thickness_um"]
        + df["interconnect_thickness_um"]
        + df["sealant_thickness_um"]
    )
    return df
