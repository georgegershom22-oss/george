#!/usr/bin/env python3
"""
Foundational & Calibration Dataset Generator
- Thermo-physical properties vs temperature for materials
- Sintering kinetics data across T, density, hold time, heating rate
- Microstructure evolution (2D/3D) synthetic images + metrics (porosity, pore size dist, grain size proxy, tortuosity)
- Initial process window dataset with outcomes and RL bounds

Pure-Python (no 3rd-party deps) for portability.
"""
from __future__ import annotations
import csv
import json
import math
import os
import random
import statistics
import time
import zipfile
from collections import deque, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple, Iterable, Optional

DATASET_ROOT = "/workspace/datasets/foundational"
RNG_SEED = 1729

# ------------------------------
# Utilities
# ------------------------------

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def linspace(start: float, stop: float, num: int) -> List[float]:
    if num <= 1:
        return [float(start)]
    step = (stop - start) / (num - 1)
    return [start + i * step for i in range(num)]


def frange(start: float, stop: float, step: float) -> Iterable[float]:
    x = start
    while x <= stop + 1e-12:
        yield x
        x += step


def write_csv(path: str, header: List[str], rows: Iterable[Iterable[object]]) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)


def write_json(path: str, data: object) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def write_pgm(path: str, image: List[List[int]]) -> None:
    """Write a grayscale PGM (ASCII P2) image.
    image: 2D list of ints 0..255
    """
    h = len(image)
    w = len(image[0]) if h else 0
    ensure_dir(os.path.dirname(path))
    with open(path, "w") as f:
        f.write("P2\n")
        f.write(f"{w} {h}\n")
        f.write("255\n")
        for row in image:
            f.write(" ".join(str(max(0, min(255, int(v)))) for v in row))
            f.write("\n")


# ------------------------------
# Domain models (synthetic but physics-inspired)
# ------------------------------

@dataclass(frozen=True)
class Material:
    name: str
    # Baseline parameters at 20 C
    density_20: float  # kg/m^3
    E_20: float        # GPa
    nu_20: float       # -
    cte_20: float      # 1e-6/K
    # Temperature coefficients
    dE_dT: float       # GPa/K (negative)
    dnu_dT: float      # 1/K (small)
    dcte_dT: float     # (1e-6/K^2)
    # Sintering viscosity Arrhenius parameters
    mu0: float         # Pa*s pre-exponential
    Q_mu: float        # J/mol
    # Sintering stress scaling
    sigma0: float      # MPa at reference
    Q_sigma: float     # J/mol


def arrhenius(A: float, Q: float, T_K: float) -> float:
    R = 8.314462618  # J/mol-K
    return A * math.exp(-Q / (R * T_K))


def density_vs_temp(material: Material, T_C: float) -> float:
    # Approximate volumetric expansion: rho(T) = rho_20 / (1 + 3 * alpha * dT)
    alpha = (material.cte_20 * 1e-6) + (material.dcte_dT * 1e-6) * max(0.0, T_C - 20.0)
    dT = T_C - 20.0
    denom = max(1e-6, 1.0 + 3.0 * alpha * dT)
    return material.density_20 / denom


def E_vs_temp(material: Material, T_C: float) -> float:
    return max(0.05, material.E_20 + material.dE_dT * (T_C - 20.0))


def nu_vs_temp(material: Material, T_C: float) -> float:
    return min(0.49, max(0.15, material.nu_20 + material.dnu_dT * (T_C - 20.0)))


def cte_vs_temp(material: Material, T_C: float) -> float:
    return max(5.0, material.cte_20 + material.dcte_dT * max(0.0, T_C - 20.0))


def mu_sinter(material: Material, T_C: float, rho: float) -> float:
    # Shear viscosity for sintering: Arrhenius with strong density increase
    T_K = T_C + 273.15
    base = arrhenius(material.mu0, material.Q_mu, T_K)  # Pa*s
    dens_factor = (rho / max(1e-6, (1.0 - rho))) ** 1.2  # diverges near full density
    return base * dens_factor


def sigma_sinter(material: Material, T_C: float, rho: float) -> float:
    # Sintering stress: Arrhenius-like surface-energy-driven term scaled by porosity
    T_K = T_C + 273.15
    base = arrhenius(material.sigma0, material.Q_sigma, T_K)  # MPa
    porosity = max(0.0, 1.0 - rho)
    return base * (porosity ** 0.6)


MATERIALS: List[Material] = [
    Material(
        name="NiO-YSZ",
        density_20=6400.0,  # kg/m3
        E_20=200.0,         # GPa
        nu_20=0.30,
        cte_20=12.0,        # um/m-K
        dE_dT=-0.03,        # GPa/K
        dnu_dT=2e-5,        # 1/K
        dcte_dT=0.004,      # um/m-K^2
        mu0=1e8,            # Pa*s
        Q_mu=380e3,         # J/mol
        sigma0=50.0,        # MPa
        Q_sigma=120e3,      # J/mol
    ),
    Material(
        name="YSZ",
        density_20=6000.0,
        E_20=210.0,
        nu_20=0.31,
        cte_20=10.5,
        dE_dT=-0.028,
        dnu_dT=1.5e-5,
        dcte_dT=0.003,
        mu0=5e7,
        Q_mu=360e3,
        sigma0=45.0,
        Q_sigma=110e3,
    ),
    Material(
        name="Functional-Layer",
        density_20=5500.0,
        E_20=150.0,
        nu_20=0.28,
        cte_20=11.5,
        dE_dT=-0.025,
        dnu_dT=2.2e-5,
        dcte_dT=0.0035,
        mu0=2e8,
        Q_mu=400e3,
        sigma0=55.0,
        Q_sigma=130e3,
    ),
]


# ------------------------------
# 1) Thermo-physical properties curves
# ------------------------------

def generate_thermo_physical_properties(root: str) -> None:
    out_path = os.path.join(root, "materials", "thermo_physical_properties.csv")
    header = [
        "material", "T_C", "CTE_1e6_perK", "E_GPa", "nu", "mu_sinter_Pa_s", "density_kg_m3",
    ]
    rows: List[List[object]] = []
    for m in MATERIALS:
        for T_C in frange(20.0, 1500.0, 20.0):
            rho = 0.5 + 0.5 * min(1.0, (T_C - 20.0) / (1500.0 - 20.0))  # synthetic evolving green->dense
            rows.append([
                m.name,
                round(T_C, 2),
                round(cte_vs_temp(m, T_C), 4),
                round(E_vs_temp(m, T_C), 4),
                round(nu_vs_temp(m, T_C), 5),
                round(mu_sinter(m, T_C, rho), 6),
                round(density_vs_temp(m, T_C), 3),
            ])
    write_csv(out_path, header, rows)


# ------------------------------
# 2) Sintering kinetics (master curves)
# ------------------------------

def densification_rate_K(T_C: float, rho: float, mat: Material) -> float:
    """Synthetic densification rate drho/dt in 1/h.
    Use Arrhenius temp factor and porosity power-law.
    """
    T_K = T_C + 273.15
    K = arrhenius(5e4, 350e3, T_K)  # arbitrary 1/h
    return K * max(1e-6, (1.0 - rho)) ** 1.4


def simulate_hold_density(T_C: float, rho0: float, hold_h: float, mat: Material, dt_h: float = 0.02) -> float:
    """Forward Euler integrate densification during isothermal hold."""
    rho = rho0
    t = 0.0
    while t < hold_h and rho < 0.999:
        drho = densification_rate_K(T_C, rho, mat) * dt_h
        rho = min(0.999, rho + drho)
        t += dt_h
    return rho


def generate_sintering_kinetics(root: str) -> None:
    out_path = os.path.join(root, "sintering_kinetics", "kinetics_grid.csv")
    header = [
        "material", "heating_rate_C_per_min", "T_peak_C", "hold_time_h", "T_C", "rho", "sigma_s_MPa", "mu_bulk_Pa_s", "mu_shear_Pa_s",
    ]
    rows: List[List[object]] = []

    heating_rates = [2.0, 5.0, 10.0, 20.0]
    T_peaks = [1100.0, 1200.0, 1300.0, 1400.0]
    hold_times = [0.0, 0.5, 1.0, 2.0, 3.0, 4.0]

    for m in MATERIALS:
        for hr in heating_rates:
            for T_peak in T_peaks:
                for hold in hold_times:
                    # Construct a simple schedule: 20C -> T_peak at rate hr, then hold
                    ramp_minutes = max(0.0, (T_peak - 20.0) / hr)
                    T_list = [*linspace(20.0, T_peak, int(max(2, ramp_minutes // 5 + 2))), T_peak]
                    rho = 0.5  # green density
                    # Ramp densification (very low until ~0.7T_melt; we emulate with threshold)
                    for T in T_list:
                        if T > 800.0:
                            rho = min(0.95, rho + 1e-4 * max(0.0, T - 800.0))
                    # Hold densification
                    rho = simulate_hold_density(T_peak, rho, hold, m)
                    # Record properties at end-of-hold
                    sigma = sigma_sinter(m, T_peak, rho)
                    mu_s = mu_sinter(m, T_peak, rho)
                    mu_b = mu_s * 3.0  # simple bulk vs shear scaling
                    rows.append([
                        m.name, hr, T_peak, hold, T_peak, round(rho, 6), round(sigma, 6), round(mu_b, 6), round(mu_s, 6)
                    ])
    write_csv(out_path, header, rows)


# ------------------------------
# 3) Microstructure generation & metrics
# ------------------------------

# We generate binary microstructures (0: pore, 255: solid). For grains, we provide a scalar proxy metric.


def generate_random_binary_image(width: int, height: int, porosity: float) -> List[List[int]]:
    img = []
    for y in range(height):
        row = []
        for x in range(width):
            v = 0 if random.random() < porosity else 255
            row.append(v)
        img.append(row)
    return img


def smooth_image(img: List[List[int]], iterations: int = 1) -> List[List[int]]:
    h = len(img)
    w = len(img[0]) if h else 0
    cur = [row[:] for row in img]
    for _ in range(iterations):
        nxt = [[0]*w for _ in range(h)]
        for y in range(h):
            for x in range(w):
                solid_neighbors = 0
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        yy = y + dy
                        xx = x + dx
                        if 0 <= yy < h and 0 <= xx < w and cur[yy][xx] > 0:
                            solid_neighbors += 1
                # majority rule to reduce speckles
                if solid_neighbors >= 5:
                    nxt[y][x] = 255
                else:
                    nxt[y][x] = 0
        cur = nxt
    return cur


def shrink_pores(img: List[List[int]], strength: float) -> List[List[int]]:
    """Bias toward turning pores to solid proportional to strength (0..1)."""
    h = len(img)
    w = len(img[0]) if h else 0
    out = [[0]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if img[y][x] == 255:
                out[y][x] = 255
            else:
                # pore; convert to solid with probability based on neighborhood
                solid_neighbors = 0
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        yy = y + dy
                        xx = x + dx
                        if 0 <= yy < h and 0 <= xx < w and img[yy][xx] > 0:
                            solid_neighbors += 1
                p_close = min(0.95, strength * (solid_neighbors / 8.0))
                out[y][x] = 255 if random.random() < p_close else 0
    return out


def connected_components_2d(img: List[List[int]], pore: bool = True) -> List[int]:
    """Return sizes of connected components (4-neighborhood) for pore or solid."""
    h = len(img)
    w = len(img[0]) if h else 0
    target = 0 if pore else 255
    seen = [[False]*w for _ in range(h)]
    sizes: List[int] = []
    for y in range(h):
        for x in range(w):
            if seen[y][x] or img[y][x] != target:
                continue
            q = deque([(y, x)])
            seen[y][x] = True
            count = 0
            while q:
                yy, xx = q.popleft()
                count += 1
                for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    y2 = yy + dy
                    x2 = xx + dx
                    if 0 <= y2 < h and 0 <= x2 < w and not seen[y2][x2] and img[y2][x2] == target:
                        seen[y2][x2] = True
                        q.append((y2, x2))
            sizes.append(count)
    return sizes


def porosity_metric(img: List[List[int]]) -> float:
    h = len(img)
    w = len(img[0]) if h else 0
    pores = sum(1 for y in range(h) for x in range(w) if img[y][x] == 0)
    return pores / max(1, w * h)


def tortuosity_left_right(img: List[List[int]]) -> Optional[float]:
    """Shortest path tortuosity through pores from left to right; None if no path.
    Returns path_length / straight_distance.
    """
    h = len(img)
    w = len(img[0]) if h else 0
    # BFS layer from left-edge pore pixels to right-edge
    dist = [[-1]*w for _ in range(h)]
    q = deque()
    for y in range(h):
        if img[y][0] == 0:
            dist[y][0] = 0
            q.append((y, 0))
    while q:
        y, x = q.popleft()
        if x == w - 1:
            path_len = dist[y][x]
            straight = w - 1
            return (path_len + 1e-9) / max(1.0, straight)
        for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
            yy = y + dy
            xx = x + dx
            if 0 <= yy < h and 0 <= xx < w and img[yy][xx] == 0 and dist[yy][xx] < 0:
                dist[yy][xx] = dist[y][x] + 1
                q.append((yy, xx))
    return None


def grain_size_proxy_from_density(rho: float, base_grain_um: float = 0.5) -> float:
    # Grain size increases sharply as pores vanish near full density
    return base_grain_um * (1.0 + 8.0 * (rho - 0.5) ** 2)


def generate_microstructure_series(root: str) -> None:
    base_dir_2d = os.path.join(root, "microstructure", "2d")
    base_dir_3d = os.path.join(root, "microstructure", "3d")

    width, height = 256, 256
    t_steps_2d = 10
    t_steps_3d = 5

    profiles = [
        {"name": "slow", "heating_rate": 2.0, "T_peak": 1200.0, "hold_h": 2.0},
        {"name": "medium", "heating_rate": 10.0, "T_peak": 1300.0, "hold_h": 1.0},
        {"name": "fast", "heating_rate": 20.0, "T_peak": 1400.0, "hold_h": 0.5},
    ]

    metrics_header = [
        "material", "profile", "dim", "t_index", "porosity", "median_pore_size_px", "p95_pore_size_px", "grain_size_um_proxy", "tortuosity_lr",
    ]
    metrics_rows: List[List[object]] = []

    for m in MATERIALS:
        for profile in profiles:
            # Initialize a starting porosity based on material
            p0 = 0.45 if m.name == "NiO-YSZ" else (0.40 if m.name == "YSZ" else 0.50)
            # 2D series
            porosity_series = [max(0.02, p0 * (0.85 ** i)) for i in range(t_steps_2d)]
            img = generate_random_binary_image(width, height, porosity_series[0])
            img = smooth_image(img, iterations=2)
            for t_idx, por in enumerate(porosity_series):
                # progressively shrink pores
                strength = min(1.0, 0.1 + 0.1 * t_idx)
                img = shrink_pores(img, strength=strength)
                img = smooth_image(img, iterations=1)
                path_img = os.path.join(base_dir_2d, m.name, profile["name"], f"t{t_idx:02d}.pgm")
                write_pgm(path_img, img)
                # metrics
                pore_sizes = connected_components_2d(img, pore=True)
                med = statistics.median(pore_sizes) if pore_sizes else 0.0
                p95 = sorted(pore_sizes)[int(0.95 * len(pore_sizes))-1] if pore_sizes else 0.0
                rho = 1.0 - porosity_metric(img)
                tort = tortuosity_left_right(img)
                metrics_rows.append([
                    m.name, profile["name"], "2D", t_idx,
                    round(1.0 - rho, 6), round(med, 3), round(p95, 3), round(grain_size_proxy_from_density(rho), 6),
                    (round(tort, 6) if tort is not None else "NA"),
                ])

            # 3D series: generate as stacks of slices per t-step (vol size modest)
            depth = 32
            w3, h3 = 96, 96
            porosity_series_3d = [max(0.05, p0 * (0.80 ** i)) for i in range(t_steps_3d)]
            # Initialize volume as list of 2D images
            volume = [generate_random_binary_image(w3, h3, porosity_series_3d[0]) for _ in range(depth)]
            volume = [smooth_image(slice_, iterations=1) for slice_ in volume]
            for t_idx, por in enumerate(porosity_series_3d):
                # shrink per-slice pores
                volume = [shrink_pores(slice_, strength=min(1.0, 0.12 + 0.12 * t_idx)) for slice_ in volume]
                volume = [smooth_image(slice_, iterations=1) for slice_ in volume]
                # write slices
                slice_dir = os.path.join(base_dir_3d, m.name, profile["name"], f"t{t_idx:02d}")
                for z, slice_img in enumerate(volume):
                    write_pgm(os.path.join(slice_dir, f"z{z:03d}.pgm"), slice_img)
                # metrics from a central slice as proxy
                center = volume[len(volume)//2]
                pore_sizes = connected_components_2d(center, pore=True)
                med = statistics.median(pore_sizes) if pore_sizes else 0.0
                p95 = sorted(pore_sizes)[int(0.95 * len(pore_sizes))-1] if pore_sizes else 0.0
                rho = 1.0 - porosity_metric(center)
                tort = tortuosity_left_right(center)
                metrics_rows.append([
                    m.name, profile["name"], "3D", t_idx,
                    round(1.0 - rho, 6), round(med, 3), round(p95, 3), round(grain_size_proxy_from_density(rho), 6),
                    (round(tort, 6) if tort is not None else "NA"),
                ])

    write_csv(os.path.join(root, "microstructure", "metrics.csv"), metrics_header, metrics_rows)


# ------------------------------
# 4) Process window outcomes & RL bounds
# ------------------------------

def logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def generate_process_window(root: str) -> None:
    header = [
        "material", "heating_rate_C_per_min", "T_peak_C", "hold_time_h", "atmosphere", "final_density", "warpage_mm", "cracking",
        "grain_coarseness_index",
    ]
    rows: List[List[object]] = []
    atmospheres = ["air", "argon", "hydrogen", "vacuum"]

    for m in MATERIALS:
        for hr in [2.0, 5.0, 10.0, 20.0]:
            for T_peak in [1100.0, 1200.0, 1300.0, 1400.0, 1500.0]:
                for hold in [0.0, 0.5, 1.0, 2.0, 3.0, 4.0]:
                    for atm in atmospheres:
                        # Effective densification potential
                        T_K = T_peak + 273.15
                        dens_potential = logistic((T_peak - 1000.0) / 80.0) * (1.0 - math.exp(-hold / 1.0))
                        rho = min(0.997, 0.6 + 0.38 * dens_potential)
                        # Warpage model: increases with fast HR and high T due to gradients; some atmos effects
                        atm_factor = {"air": 1.0, "argon": 0.9, "hydrogen": 0.8, "vacuum": 1.1}[atm]
                        cte = cte_vs_temp(m, T_peak) * 1e-6
                        stiffness = E_vs_temp(m, min(1200.0, T_peak))
                        warpage = (0.15 + 0.08 * (hr / 20.0) ** 1.5) * atm_factor * (cte / 1e-5) * (150.0 / max(10.0, stiffness))
                        # cracking probability
                        crack_score = 3.0 * (hr / 20.0) + 2.0 * (T_peak - 1200.0) / 400.0 - 2.5 * hold + (atm_factor - 1.0)
                        cracking = 1 if random.random() < logistic(crack_score - 1.0) * 0.6 else 0
                        # Grain coarseness index
                        grain_idx = 1.0 + 4.0 * dens_potential + 0.5 * (T_peak - 1200.0) / 300.0
                        rows.append([
                            m.name, hr, T_peak, hold, atm, round(rho, 6), round(warage_clipped := max(0.0, warpage), 6), cracking,
                            round(grain_idx, 3),
                        ])
    write_csv(os.path.join(root, "process_window", "process_outcomes.csv"), header, rows)

    # RL bounds metadata
    bounds = {
        "action_space": {
            "heating_rate_C_per_min": {"min": 2.0, "max": 20.0, "step": 0.5},
            "T_peak_C": {"min": 1100.0, "max": 1500.0, "step": 10.0},
            "hold_time_h": {"min": 0.0, "max": 4.0, "step": 0.1},
            "atmosphere": {"values": atmospheres},
        },
        "state_outputs": [
            "final_density", "warpage_mm", "cracking", "grain_coarseness_index"
        ],
        "notes": "Synthetic, physics-inspired dataset for baseline RL training and calibration.",
    }
    write_json(os.path.join(root, "process_window", "rl_bounds.json"), bounds)


# ------------------------------
# Packaging
# ------------------------------

def zip_dataset(root: str) -> str:
    zip_path = os.path.join(root, "dataset.zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for dirpath, _, filenames in os.walk(root):
            # Skip the zip itself if re-running
            for fn in filenames:
                abs_fp = os.path.join(dirpath, fn)
                if abs_fp == zip_path:
                    continue
                rel = os.path.relpath(abs_fp, root)
                zf.write(abs_fp, arcname=rel)
    return zip_path


# ------------------------------
# Main
# ------------------------------

def main() -> None:
    random.seed(RNG_SEED)
    ensure_dir(DATASET_ROOT)
    t0 = time.time()

    generate_thermo_physical_properties(DATASET_ROOT)
    generate_sintering_kinetics(DATASET_ROOT)
    generate_microstructure_series(DATASET_ROOT)
    generate_process_window(DATASET_ROOT)

    zip_fp = zip_dataset(DATASET_ROOT)
    dt = time.time() - t0
    print(f"Dataset generated at {DATASET_ROOT}")
    print(f"Zipped bundle: {zip_fp}")
    print(f"Elapsed: {dt:.1f}s")


if __name__ == "__main__":
    main()
