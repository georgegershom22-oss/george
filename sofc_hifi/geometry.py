from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
from scipy.ndimage import gaussian_filter

from .config import LAYER_ORDER, LayerNames


@dataclass
class Grid:
    nx: int
    ny: int
    nz: int
    lx: float  # meters
    ly: float  # meters
    lz: float  # meters

    @property
    def dx(self) -> float:
        return self.lx / self.nx

    @property
    def dy(self) -> float:
        return self.ly / self.ny

    @property
    def dz(self) -> float:
        return self.lz / self.nz


@dataclass
class LayerSpec:
    name: str
    thickness_m: float


def build_layers(total_thicknesses: Dict[str, float]) -> Tuple[Tuple[LayerSpec, ...], Dict[str, slice]]:
    layers = []
    z_slices: Dict[str, slice] = {}
    z_start = 0
    # Discrete layer assignment along z will be handled after grid is known
    for name in LAYER_ORDER:
        layers.append(LayerSpec(name=name, thickness_m=float(total_thicknesses[name])))
    return tuple(layers), z_slices


def assign_layer_indices(grid: Grid, layers: Tuple[LayerSpec, ...]) -> Dict[str, slice]:
    """Assign contiguous z-index ranges to each layer preserving thickness proportion."""
    total_thickness = sum(l.thickness_m for l in layers)
    z_positions = np.linspace(0.0, total_thickness, grid.nz + 1)

    # Compute target end positions of each layer
    z_end_targets = np.cumsum([l.thickness_m for l in layers])

    z_slices: Dict[str, slice] = {}
    z_prev = 0
    for l, z_end in zip(layers, z_end_targets):
        # find index where z_positions exceeds z_end
        idx_end = int(np.searchsorted(z_positions, z_end, side="right"))
        idx_end = min(max(idx_end, z_prev + 1), grid.nz)  # ensure at least 1 cell
        z_slices[l.name] = slice(z_prev, idx_end)
        z_prev = idx_end
    # ensure last goes to end
    last_name = layers[-1].name
    z_slices[last_name] = slice(z_slices[last_name].start, grid.nz)
    return z_slices


def make_property_fields(
    grid: Grid,
    z_slices: Dict[str, slice],
    materials: Dict[str, Dict[str, float]],
    heterogeneity_strength: float = 0.1,
    heterogeneity_length_scales: Tuple[float, float, float] = (0.2, 0.2, 0.2),
) -> Dict[str, np.ndarray]:
    """Construct 3D property fields per voxel, with smooth heterogeneity.

    The heterogeneity is generated as a smooth random field with zero mean, scaled
    by `heterogeneity_strength` relative to the base (layer-constant) value.
    """
    nx, ny, nz = grid.nx, grid.ny, grid.nz

    fields: Dict[str, np.ndarray] = {}

    # Initialize per-layer base arrays then add heterogeneity
    def layer_constant_to_field(prop_key: str, default: float = 0.0) -> np.ndarray:
        arr = np.full((nx, ny, nz), default, dtype=np.float32)
        for layer_name, zsl in z_slices.items():
            base_val = float(materials[layer_name].get(prop_key, default))
            arr[:, :, zsl] = base_val
        return arr

    # Base fields
    sigma_e = layer_constant_to_field("sigma_electronic")
    sigma_i = layer_constant_to_field("sigma_ionic")
    k_th = layer_constant_to_field("k_thermal")
    E = layer_constant_to_field("youngs_modulus")
    nu = layer_constant_to_field("poisson_ratio")
    alpha = layer_constant_to_field("cte")
    porosity = layer_constant_to_field("porosity")

    # Smooth heterogeneity per property (same random field shared to keep correlations plausible)
    rng = np.random.default_rng()
    base_noise = rng.standard_normal((nx, ny, nz)).astype(np.float32)

    # Convert length scale fractions into Gaussian sigmas in voxels
    sigmas = (
        max(1.0, heterogeneity_length_scales[0] * nx),
        max(1.0, heterogeneity_length_scales[1] * ny),
        max(1.0, heterogeneity_length_scales[2] * nz),
    )
    smooth_noise = gaussian_filter(base_noise, sigma=sigmas, mode="reflect")
    smooth_noise /= (np.std(smooth_noise) + 1e-8)

    def apply_hetero(field: np.ndarray) -> np.ndarray:
        return (field * (1.0 + heterogeneity_strength * smooth_noise)).astype(np.float32)

    fields["sigma_e"] = np.clip(apply_hetero(sigma_e), 1e-3, np.inf)
    fields["sigma_i"] = np.clip(apply_hetero(sigma_i), 1e-3, np.inf)
    fields["k_th"] = np.clip(apply_hetero(k_th), 1e-3, np.inf)
    fields["E"] = np.clip(apply_hetero(E), 1e6, np.inf)
    fields["nu"] = np.clip(apply_hetero(nu), 0.05, 0.49)
    fields["alpha"] = np.clip(apply_hetero(alpha), 1e-7, np.inf)
    fields["porosity"] = np.clip(apply_hetero(porosity), 0.0, 0.95)

    # Exchange current densities only for anode/cathode; create 3D fields localized near electrolyte interfaces
    j0 = np.zeros((nx, ny, nz), dtype=np.float32)
    for side_layer in (LayerNames.ANODE, LayerNames.CATHODE):
        if f"j0_exchange" in materials[side_layer]:
            zsl = z_slices[side_layer]
            # Use a 2-voxel-thick band adjacent to electrolyte interface for reaction zone
            if side_layer == LayerNames.ANODE:
                band = slice(zsl.stop - 2 if zsl.stop - zsl.start >= 2 else zsl.start, zsl.stop)
            else:
                band = slice(zsl.start, min(zsl.start + 2, zsl.stop))
            val = float(materials[side_layer]["j0_exchange"])
            j0[:, :, band] = val
    fields["j0"] = j0

    return fields
