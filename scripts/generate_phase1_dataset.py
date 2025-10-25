#!/usr/bin/env python3
import argparse
import json
import math
import os
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

import h5py
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
from skimage import measure, morphology, segmentation, util
from skimage.morphology import ball, disk
from tifffile import imwrite

R_GAS = 8.314462618  # J/(mol*K)


@dataclass
class MaterialParams:
    name: str
    density_g_cm3_20C: float
    E0_GPa: float
    E_soften_ref_C: float
    poisson_20C: float
    poisson_slope_per_1000C: float
    cte_1e6_per_K_20C: float
    cte_slope_per_1000C: float
    eta0_shear_Pa_s: float
    Q_eta_kJ_per_mol: float
    Q_dens_kJ_per_mol: float
    K0_dens_per_s: float
    m_visc_exp: float
    n_dens_exp: float
    gamma0_J_per_m2: float
    grain_um_init: float


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def ensure_dirs(paths: List[str]) -> None:
    for p in paths:
        os.makedirs(p, exist_ok=True)


def temperature_grid(T_min_C=20.0, T_max_C=1600.0, n=81) -> np.ndarray:
    return np.linspace(T_min_C, T_max_C, n)


def thermo_physical_curves(params: MaterialParams, T_C: np.ndarray) -> pd.DataFrame:
    T_K = T_C + 273.15
    # CTE in 1/K scaled by 1e-6
    cte = (
        params.cte_1e6_per_K_20C
        + params.cte_slope_per_1000C * (T_C - 20.0) / 1000.0
    )  # in 1e-6/K

    # Young's modulus softening roughly linear with temperature fraction to a ref
    T_ref = params.E_soften_ref_C
    soften = np.clip((T_C - 20.0) / max(T_ref - 20.0, 1.0), 0.0, 1.0)
    E_GPa = params.E0_GPa * (1.0 - 0.6 * soften)

    # Poisson ratio slightly increases with T
    nu = params.poisson_20C + params.poisson_slope_per_1000C * (T_C - 20.0) / 1000.0
    nu = np.clip(nu, 0.2, 0.35)

    # Density decreases slightly with thermal expansion (approx volumetric alpha ~ 3*cte)
    alpha = cte * 1e-6  # 1/K
    # Integrate alpha approximately over deltaT
    deltaT = T_C - 20.0
    volumetric_strain = 3.0 * alpha * deltaT
    rho = params.density_g_cm3_20C / (1.0 + volumetric_strain)

    # Shear viscosity for sintering (effective), Arrhenius decrease with T
    Q_eta = params.Q_eta_kJ_per_mol * 1000.0
    eta = params.eta0_shear_Pa_s * np.exp(Q_eta / (R_GAS * T_K))

    df = pd.DataFrame(
        {
            "material": params.name,
            "temperature_C": T_C,
            "CTE_1e-6_per_K": cte,
            "YoungsModulus_GPa": E_GPa,
            "PoissonRatio": nu,
            "Density_g_cm3": rho,
            "ShearViscosity_Pa_s": eta,
        }
    )
    return df


def kinetics_grid(
    params: MaterialParams,
    temps_C: np.ndarray,
    densities: np.ndarray,
    hold_times_min: np.ndarray,
) -> pd.DataFrame:
    # Effective viscosities and sintering stress model
    rows = []
    Q_eta = params.Q_eta_kJ_per_mol * 1000.0
    Q_d = params.Q_dens_kJ_per_mol * 1000.0
    for T_C in temps_C:
        T_K = T_C + 273.15
        arrhenius_eta = np.exp(Q_eta / (R_GAS * T_K))
        arrhenius_d = np.exp(-Q_d / (R_GAS * T_K))
        # Surface energy decreases mildly with T
        gamma = params.gamma0_J_per_m2 * (1.0 - 0.1 * (T_C - 20.0) / 1600.0)
        gamma = max(gamma, 0.2 * params.gamma0_J_per_m2)
        for rho in densities:
            # Grain size grows with density (coarsening), simple relation
            grain_um = params.grain_um_init * (1.0 + 2.5 * (rho - densities.min()) / (densities.max() - densities.min()))
            # Viscosities strongly increase as porosity vanishes
            porosity = max(1e-6, 1.0 - rho)
            bulk_visc = 3.0 * params.eta0_shear_Pa_s * arrhenius_eta / (porosity ** params.m_visc_exp)
            shear_visc = params.eta0_shear_Pa_s * arrhenius_eta / (porosity ** (params.m_visc_exp - 0.5))
            # Sintering stress scales with gamma and curvature ~ 1/grain_size
            sigma_s_MPa = 1e-6 * gamma / max(grain_um * 1e-6, 1e-12)
            for ht in hold_times_min:
                dens_rate = params.K0_dens_per_s * arrhenius_d * (porosity ** params.n_dens_exp)
                rows.append(
                    {
                        "material": params.name,
                        "temperature_C": T_C,
                        "density": rho,
                        "hold_time_min": ht,
                        "sintering_stress_MPa": sigma_s_MPa,
                        "bulk_viscosity_Pa_s": bulk_visc,
                        "shear_viscosity_Pa_s": shear_visc,
                        "densification_rate_1_per_s": dens_rate,
                        "grain_size_um": grain_um,
                    }
                )
    return pd.DataFrame(rows)


def simulate_dilatometry(
    params: MaterialParams,
    heating_rate_C_per_min: float,
    peak_temp_C: float,
    hold_time_min: float,
    initial_density: float,
    dt_s: float = 1.0,
) -> pd.DataFrame:
    # Simple densification model d(rho)/dt = K0*exp(-Q/RT)*(1-rho)^n
    Q = params.Q_dens_kJ_per_mol * 1000.0
    K0 = params.K0_dens_per_s
    n = params.n_dens_exp

    t_total_s = (peak_temp_C - 25.0) / (heating_rate_C_per_min / 60.0) + hold_time_min * 60.0
    steps = int(max(1, t_total_s // dt_s))
    rho = initial_density
    rho0 = initial_density

    times = []
    temps = []
    shrinkage_pct = []
    densities = []

    T_C = 25.0
    for i in range(steps + 1):
        t_s = i * dt_s
        # Temperature profile: linear ramp then hold
        T_ramp_end_s = (peak_temp_C - 25.0) / (heating_rate_C_per_min / 60.0)
        if t_s <= T_ramp_end_s:
            T_C = 25.0 + (heating_rate_C_per_min / 60.0) * t_s
        else:
            T_C = peak_temp_C
        T_K = T_C + 273.15
        dens_rate = K0 * math.exp(-Q / (R_GAS * T_K)) * (max(1e-8, 1.0 - rho) ** n)
        rho = min(0.9999, rho + dens_rate * dt_s)
        # Convert density change to linear shrinkage assuming volume change only
        vol_ratio = rho0 / rho
        lin_shrink = 1.0 - vol_ratio ** (1.0 / 3.0)

        times.append(t_s / 60.0)
        temps.append(T_C)
        shrinkage_pct.append(100.0 * max(0.0, lin_shrink))
        densities.append(rho)

    return pd.DataFrame(
        {
            "time_min": times,
            "temperature_C": temps,
            "linear_shrinkage_pct": shrinkage_pct,
            "relative_density": densities,
        }
    )


def generate_random_microstructure_2d(
    height: int,
    width: int,
    porosity: float,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, 1, size=(height, width))
    smoothed = gaussian_filter(noise, sigma=2.0)
    thresh = np.quantile(smoothed, porosity)
    pores = smoothed < thresh  # pores=True
    # Clean up small islands
    pores = morphology.remove_small_objects(pores, min_size=8)
    pores = morphology.remove_small_holes(pores, area_threshold=64)
    return pores


def sinter_step_binary(image: np.ndarray, radius: int) -> np.ndarray:
    # Solid phase is ~1 - pores
    solid = ~image
    closed = morphology.closing(solid, footprint=disk(radius))
    opened = morphology.opening(closed, footprint=disk(max(1, radius // 2)))
    return ~opened


def microstructure_metrics_2d(pores: np.ndarray) -> Dict[str, float]:
    h, w = pores.shape
    porosity = float(np.mean(pores))

    # Pore size distribution via labeled regions equivalent diameter
    labeled = measure.label(pores, connectivity=2)
    props = measure.regionprops(labeled)
    if props:
        pore_eq_diams = np.array([p.equivalent_diameter for p in props])
        pore_size_mean = float(np.mean(pore_eq_diams))
        pore_size_p95 = float(np.percentile(pore_eq_diams, 95))
    else:
        pore_size_mean = 0.0
        pore_size_p95 = 0.0

    # Characteristic length scale from solid distance transform
    solid = ~pores
    dist = morphology.distance_transform_edt(solid)
    grain_len_mean = float(2.0 * np.mean(dist[solid])) if np.any(solid) else 0.0

    # Tortuosity estimate: shortest path through pores left->right relative to width
    tau = np.nan
    try:
        labels = measure.label(pores, connectivity=2)
        left_labels = np.unique(labels[:, 0])
        right_labels = np.unique(labels[:, -1])
        conn = np.intersect1d(left_labels[left_labels > 0], right_labels[right_labels > 0])
        if conn.size > 0:
            # Approximate minimal geodesic using dynamic programming across columns
            cost = np.where(pores, 1.0, np.inf)
            dp = np.full_like(cost, np.inf, dtype=float)
            dp[:, 0] = cost[:, 0]
            for x in range(1, w):
                prev = dp[:, x - 1]
                dp[:, x] = cost[:, x] + np.minimum.reduce(
                    [prev, np.roll(prev, 1), np.roll(prev, -1)]
                )
            min_cost = float(np.nanmin(dp[:, -1]))
            tau = min_cost / w
    except Exception:
        tau = np.nan

    return {
        "porosity": porosity,
        "pore_eq_diam_mean_px": pore_size_mean,
        "pore_eq_diam_p95_px": pore_size_p95,
        "grain_char_length_mean_px": grain_len_mean,
        "tortuosity_left_right": float(tau) if not np.isnan(tau) else np.nan,
        "height_px": float(h),
        "width_px": float(w),
    }


def generate_microstructure_series_2d(
    out_dir: str,
    material: str,
    n_steps: int,
    size: Tuple[int, int],
    porosity_start: float,
    porosity_end: float,
    seed: int,
) -> pd.DataFrame:
    h, w = size
    series_metrics = []
    pores = generate_random_microstructure_2d(h, w, porosity_start, seed)
    for t in range(n_steps):
        # Interpolate porosity target
        target_porosity = porosity_start + (porosity_end - porosity_start) * (t / max(1, n_steps - 1))
        # Apply sintering steps until close to target porosity heuristic; use radius scaling
        radius = max(1, int(1 + 6 * (t / max(1, n_steps - 1))))
        pores = sinter_step_binary(pores, radius)
        # Adjust via random erosion/dilation to hit target roughly
        current_por = float(np.mean(pores))
        if current_por > target_porosity:
            # Erode pores a bit (dilate solid)
            pores = morphology.binary_erosion(pores, footprint=disk(1))
        elif current_por < target_porosity:
            pores = morphology.binary_dilation(pores, footprint=disk(1))
        # Save image and metrics
        img_path = os.path.join(out_dir, f"{material}_t{t:02d}.tif")
        imwrite(img_path, util.img_as_uint(~pores))  # save solid as white
        metrics = microstructure_metrics_2d(pores)
        metrics.update({"material": material, "time_idx": t, "image_path": os.path.relpath(img_path)})
        series_metrics.append(metrics)
    return pd.DataFrame(series_metrics)


def generate_microstructure_series_3d(
    out_dir: str,
    material: str,
    n_steps: int,
    size: Tuple[int, int, int],
    porosity_start: float,
    porosity_end: float,
    seed: int,
) -> pd.DataFrame:
    z, y, x = size
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, 1, size=(z, y, x))
    smoothed = gaussian_filter(noise, sigma=1.2)
    thresh = np.quantile(smoothed, porosity_start)
    pores = smoothed < thresh
    pores = morphology.remove_small_objects(pores, min_size=64)

    series_metrics = []
    for t in range(n_steps):
        radius = max(1, int(1 + 3 * (t / max(1, n_steps - 1))))
        solid = ~pores
        selem = ball(radius)
        solid = morphology.closing(solid, footprint=selem)
        solid = morphology.opening(solid, footprint=ball(max(1, radius // 2)))
        pores = ~solid
        # Adjust porosity roughly towards target
        target_por = porosity_start + (porosity_end - porosity_start) * (t / max(1, n_steps - 1))
        current_por = float(np.mean(pores))
        if current_por > target_por:
            pores = morphology.binary_erosion(pores, footprint=ball(1))
        elif current_por < target_por:
            pores = morphology.binary_dilation(pores, footprint=ball(1))

        vol_path = os.path.join(out_dir, f"{material}_t{t:02d}.h5")
        with h5py.File(vol_path, "w") as f:
            f.create_dataset("volume_pores_bool", data=pores.astype(np.uint8), compression="gzip")
        # Metrics
        porosity = float(np.mean(pores))
        # Bruggeman tortuosity approximation
        tau = 1.0 / max(1e-3, math.sqrt(porosity))
        series_metrics.append(
            {
                "material": material,
                "time_idx": t,
                "volume_path": os.path.relpath(vol_path),
                "porosity": porosity,
                "tortuosity_bruggeman": tau,
                "size_z": float(z),
                "size_y": float(y),
                "size_x": float(x),
            }
        )
    return pd.DataFrame(series_metrics)


def sample_process_window(
    materials: List[str],
    n_samples: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    atmospheres = ["Air", "Ar", "H2/N2"]

    rows = []
    for i in range(n_samples):
        material = random.choice(materials)
        heating_rate = float(rng.uniform(1.0, 20.0))  # C/min
        peak_temp = float(rng.uniform(1100.0, 1500.0))  # C
        hold_time = float(rng.uniform(0.25, 8.0))  # hours
        atmosphere = random.choice(atmospheres)

        # Effective sintering parameter (proxy for MSC):
        # psi ~ hold_time * exp(-Q/RT_peak) / heating_rate^0.2
        # Use material-specific Q via a mapping for realism
        Q_map_kJ = {
            "Anode_NiO-YSZ": 400.0,
            "AFL_NiO-YSZ": 420.0,
            "Electrolyte_YSZ": 480.0,
        }
        Q = Q_map_kJ.get(material, 420.0) * 1000.0
        T_K = peak_temp + 273.15
        psi = hold_time * 3600.0 * math.exp(-Q / (R_GAS * T_K)) / (heating_rate ** 0.2)

        # Atmosphere factor affecting defect chemistry and densification
        atm_factor = {"Air": 1.0, "Ar": 0.95, "H2/N2": 1.05}[atmosphere]
        psi_eff = psi * atm_factor

        # Map psi to final density in [0.85, 0.999]
        x = 1.0 - math.exp(-1e7 * psi_eff)
        final_density = 0.85 + 0.149 * min(1.0, x)  # cap at ~0.999

        # Warpage proxy: increases with heating rate and peak temp, decreases with hold
        # Also atmosphere: H2/N2 can reduce warpage for NiO reduction or increase, model slight reduction
        atm_warp = {"Air": 1.0, "Ar": 1.1, "H2/N2": 0.9}[atmosphere]
        warp = (
            0.05 * (heating_rate ** 0.9)
            + 0.0008 * max(0.0, peak_temp - 1200.0)
            - 0.01 * hold_time
        ) * atm_warp
        warp = max(0.0, warp)

        # Cracking probability based on warpage and fast heating at lower density
        logit = -3.0 + 1.2 * warp + 10.0 * max(0.0, 0.95 - final_density)
        crack_prob = 1.0 / (1.0 + math.exp(-logit))
        cracked = int(rng.random() < crack_prob)

        # Coarse microstructure label based on density and peak temp
        if final_density > 0.97 and peak_temp > 1350:
            micro = "coarse"
        elif final_density > 0.93:
            micro = "medium"
        else:
            micro = "fine"

        rows.append(
            {
                "material": material,
                "heating_rate_C_per_min": heating_rate,
                "peak_temp_C": peak_temp,
                "hold_time_h": hold_time,
                "atmosphere": atmosphere,
                "final_density": final_density,
                "warpage_mm": warp,
                "cracked": cracked,
                "coarse_microstructure": micro,
            }
        )

    return pd.DataFrame(rows)


def write_metadata(root: str) -> None:
    meta = {
        "name": "Phase 1: Foundational & Calibration Data (Synthetic)",
        "version": "0.1.0",
        "description": "Fabricated dataset for thermo-physical properties, sintering kinetics, microstructural evolution, and process windows for SOFC-like ceramics (NiO-YSZ anode, YSZ electrolyte, AFL).",
        "license": "CC BY 4.0",
        "disclaimer": "This dataset is fully synthetic, generated via physics-inspired models for development, benchmarking, and RL prototyping. Not for design-critical decisions without experimental validation.",
        "units": {
            "temperature_C": "Celsius",
            "CTE_1e-6_per_K": "1e-6/K",
            "YoungsModulus_GPa": "GPa",
            "PoissonRatio": "unitless",
            "Density_g_cm3": "g/cm^3",
            "ShearViscosity_Pa_s": "Pa*s",
            "sintering_stress_MPa": "MPa",
            "bulk_viscosity_Pa_s": "Pa*s",
            "shear_viscosity_Pa_s": "Pa*s",
            "densification_rate_1_per_s": "1/s",
            "time_min": "minutes",
            "linear_shrinkage_pct": "%",
            "relative_density": "unitless",
            "warpage_mm": "mm",
            "final_density": "unitless",
            "cracked": "0/1",
            "pore_eq_diam_mean_px": "pixels",
            "grain_char_length_mean_px": "pixels",
            "tortuosity_left_right": "unitless",
            "tortuosity_bruggeman": "unitless",
        },
        "generation_script": "scripts/generate_phase1_dataset.py",
    }
    meta_path = os.path.join(root, "metadata", "dataset_info.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Phase 1 synthetic dataset")
    parser.add_argument("--root", default="/workspace/datasets/phase1", help="Output root directory")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n_process_window", type=int, default=600)
    parser.add_argument("--micro2d_size", type=int, nargs=2, default=[256, 256])
    parser.add_argument("--micro2d_steps", type=int, default=12)
    parser.add_argument("--micro3d_size", type=int, nargs=3, default=[64, 64, 64])
    parser.add_argument("--micro3d_steps", type=int, default=6)
    args = parser.parse_args()

    seed_everything(args.seed)

    root = args.root
    dir_properties = os.path.join(root, "properties")
    dir_kinetics = os.path.join(root, "kinetics")
    dir_micro2d = os.path.join(root, "microstructure", "sem2d", "images")
    dir_micro2d_metrics = os.path.join(root, "microstructure", "sem2d")
    dir_micro3d = os.path.join(root, "microstructure", "ct3d", "volumes")
    dir_micro3d_metrics = os.path.join(root, "microstructure", "ct3d")
    dir_process = os.path.join(root, "process_window")
    dir_metadata = os.path.join(root, "metadata")

    ensure_dirs([dir_properties, dir_kinetics, dir_micro2d, dir_micro3d, dir_process, dir_metadata, dir_micro2d_metrics, dir_micro3d_metrics])

    materials = [
        MaterialParams(
            name="Anode_NiO-YSZ",
            density_g_cm3_20C=6.5,
            E0_GPa=160.0,
            E_soften_ref_C=1500.0,
            poisson_20C=0.29,
            poisson_slope_per_1000C=0.02,
            cte_1e6_per_K_20C=12.5,
            cte_slope_per_1000C=1.0,
            eta0_shear_Pa_s=1e3,
            Q_eta_kJ_per_mol=450.0,
            Q_dens_kJ_per_mol=380.0,
            K0_dens_per_s=1e5,
            m_visc_exp=3.5,
            n_dens_exp=2.2,
            gamma0_J_per_m2=0.8,
            grain_um_init=0.5,
        ),
        MaterialParams(
            name="Electrolyte_YSZ",
            density_g_cm3_20C=6.0,
            E0_GPa=210.0,
            E_soften_ref_C=1700.0,
            poisson_20C=0.30,
            poisson_slope_per_1000C=0.015,
            cte_1e6_per_K_20C=10.5,
            cte_slope_per_1000C=0.7,
            eta0_shear_Pa_s=5e3,
            Q_eta_kJ_per_mol=520.0,
            Q_dens_kJ_per_mol=450.0,
            K0_dens_per_s=2e4,
            m_visc_exp=4.0,
            n_dens_exp=2.5,
            gamma0_J_per_m2=1.0,
            grain_um_init=0.3,
        ),
        MaterialParams(
            name="AFL_NiO-YSZ",
            density_g_cm3_20C=6.3,
            E0_GPa=175.0,
            E_soften_ref_C=1550.0,
            poisson_20C=0.295,
            poisson_slope_per_1000C=0.018,
            cte_1e6_per_K_20C=12.0,
            cte_slope_per_1000C=0.9,
            eta0_shear_Pa_s=2e3,
            Q_eta_kJ_per_mol=480.0,
            Q_dens_kJ_per_mol=400.0,
            K0_dens_per_s=6e4,
            m_visc_exp=3.8,
            n_dens_exp=2.3,
            gamma0_J_per_m2=0.9,
            grain_um_init=0.4,
        ),
    ]

    # 1) Thermo-Physical properties
    T_C = temperature_grid(20.0, 1600.0, 81)
    prop_dfs = []
    for mp in materials:
        df = thermo_physical_curves(mp, T_C)
        out_path = os.path.join(dir_properties, f"{mp.name}_thermo_physical.csv")
        df.to_csv(out_path, index=False)
        prop_dfs.append(df)

    # 2) Sintering Kinetics: grid and dilatometry
    temps_grid = np.linspace(900.0, 1500.0, 16)
    densities = np.linspace(0.50, 0.99, 25)
    holds = np.linspace(0.0, 240.0, 9)  # minutes
    for mp in materials:
        dfk = kinetics_grid(mp, temps_grid, densities, holds)
        out_path = os.path.join(dir_kinetics, f"{mp.name}_kinetics_grid.csv")
        dfk.to_csv(out_path, index=False)
        # Dilatometry runs for multiple heating rates
        rates = [2.0, 5.0, 10.0, 20.0]
        init_rho = 0.55 if "Anode" in mp.name or "AFL" in mp.name else 0.60
        for r in rates:
            dfd = simulate_dilatometry(
                mp, heating_rate_C_per_min=r, peak_temp_C=1450.0, hold_time_min=60.0, initial_density=init_rho
            )
            dfd.to_csv(os.path.join(dir_kinetics, f"dilatometry_{mp.name}_{int(r)}Cmin.csv"), index=False)

    # 3) Microstructural Evolution Data (2D SEM-like and 3D CT-like)
    micro2d_all = []
    micro3d_all = []
    for mp in materials:
        # 2D
        poro_start = 0.40 if "Anode" in mp.name or "AFL" in mp.name else 0.30
        poro_end = 0.05 if "Anode" in mp.name or "AFL" in mp.name else 0.02
        m2d_dir = dir_micro2d
        df2d = generate_microstructure_series_2d(
            out_dir=m2d_dir,
            material=mp.name,
            n_steps=args.micro2d_steps,
            size=(args.micro2d_size[0], args.micro2d_size[1]),
            porosity_start=poro_start,
            porosity_end=poro_end,
            seed=args.seed + hash(mp.name) % 10000,
        )
        df2d.to_csv(os.path.join(dir_micro2d_metrics, f"metrics_{mp.name}_2d.csv"), index=False)
        micro2d_all.append(df2d)
        # 3D
        df3d = generate_microstructure_series_3d(
            out_dir=dir_micro3d,
            material=mp.name,
            n_steps=args.micro3d_steps,
            size=(args.micro3d_size[0], args.micro3d_size[1], args.micro3d_size[2]),
            porosity_start=poro_start,
            porosity_end=poro_end,
            seed=args.seed + 123 + hash(mp.name) % 10000,
        )
        df3d.to_csv(os.path.join(dir_micro3d_metrics, f"metrics_{mp.name}_3d.csv"), index=False)
        micro3d_all.append(df3d)

    # 4) Process Window Data
    dfpw = sample_process_window([m.name for m in materials], args.n_process_window, seed=args.seed)
    dfpw.to_csv(os.path.join(dir_process, "process_window.csv"), index=False)

    # Write global metadata
    write_metadata(root)

    # Write summary counts
    summary = {
        "properties_files": len(materials),
        "kinetics_grid_files": len(materials),
        "dilatometry_files": len(materials) * 4,
        "micro2d_images": len(os.listdir(dir_micro2d)),
        "micro2d_metrics_files": len(materials),
        "micro3d_volumes": len(os.listdir(dir_micro3d)),
        "micro3d_metrics_files": len(materials),
        "process_window_rows": int(dfpw.shape[0]),
    }
    with open(os.path.join(dir_metadata, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
