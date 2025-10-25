#!/usr/bin/env python3

import argparse
import json
import math
import os
import random
import sys
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

try:
    from PIL import Image
except Exception as e:
    print("PIL (pillow) is required. Please install via: pip install pillow", file=sys.stderr)
    raise

try:
    from scipy.ndimage import gaussian_filter, map_coordinates, laplace
except Exception as e:
    print("scipy is required. Please install via: pip install scipy", file=sys.stderr)
    raise


@dataclass
class CameraConfig:
    name: str
    width: int
    height: int
    baseline_pixels: float  # effective stereo baseline impact in pixels per unit W
    noise_std: float


@dataclass
class FurnaceConfig:
    num_zones: int
    ambient_c: float
    max_temp_c: float
    # thermal dynamics coefficients
    k_cool: float   # cooling/leak rate
    alpha_heat: float  # heater coupling strength
    sensor_noise_std: float


@dataclass
class RLConfig:
    action_dt_s: float  # seconds between actions
    w1: float
    w2: float
    w3: float
    target_density: float


@dataclass
class SimConfig:
    duration_s: float
    dic_fps: float
    width: int
    height: int
    seed: int
    output_root: str
    run_id: str
    cameras: List[CameraConfig]
    furnace: FurnaceConfig
    rl: RLConfig


def now_unix_ns() -> int:
    return time.time_ns()


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def generate_speckle(height: int, width: int, density: float, rng: np.random.Generator) -> np.ndarray:
    base = rng.random((height, width)).astype(np.float32)
    base = gaussian_filter(base, sigma=1.5)
    thr = np.quantile(base, 1.0 - density)
    speckle = (base > thr).astype(np.float32)
    # soften edges and add slight blur
    speckle = gaussian_filter(speckle, sigma=0.6)
    # rescale to 0..255
    speckle = (255.0 * (speckle - speckle.min()) / (speckle.ptp() + 1e-6)).astype(np.uint8)
    return speckle


def smoothstep(x: np.ndarray) -> np.ndarray:
    return x * x * (3 - 2 * x)


def zones_field(width: int, height: int, zone_values: np.ndarray) -> np.ndarray:
    """Create a smoothed field across 3 zones partitioned along X with soft transitions."""
    assert zone_values.shape == (3,)
    x = np.linspace(0.0, 1.0, width, dtype=np.float32)
    y = np.linspace(0.0, 1.0, height, dtype=np.float32)
    X, Y = np.meshgrid(x, y)
    # zone boundaries at 1/3, 2/3
    z0 = np.clip(1.0 - smoothstep((X - 1/6) / (1/6)), 0.0, 1.0)
    z1 = np.clip(smoothstep((X - 1/6) / (1/6)) * (1.0 - smoothstep((X - 3/6) / (1/6))), 0.0, 1.0)
    z2 = np.clip(smoothstep((X - 3/6) / (1/6)), 0.0, 1.0)
    wsum = z0 + z1 + z2 + 1e-6
    field = (zone_values[0] * z0 + zone_values[1] * z1 + zone_values[2] * z2) / wsum
    return field.astype(np.float32)


def compute_displacement_fields(width: int, height: int, t: float, T_zones: np.ndarray, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return U, V, W fields in pixels for this frame time."""
    # Thermal gradients induce in-plane expansion; zone imbalance induces curvature (W)
    T_field = zones_field(width, height, T_zones)
    x = np.linspace(-1.0, 1.0, width, dtype=np.float32)
    y = np.linspace(-1.0, 1.0, height, dtype=np.float32)
    X, Y = np.meshgrid(x, y)

    T_mean = float(T_zones.mean())
    dT = T_field - T_mean

    # In-plane displacement proportional to gradient and position (thermal expansion)
    alpha_T = 2.5e-3  # pixels per degree scaling
    U = alpha_T * dT * X * width
    V = alpha_T * dT * Y * height

    # Out-of-plane warpage modeled as quadratic bowl twisted by zone differences
    dz01 = float(T_zones[0] - T_zones[1])
    dz12 = float(T_zones[1] - T_zones[2])
    dz02 = float(T_zones[0] - T_zones[2])
    amp = 0.015 * (abs(dz01) + abs(dz12) + 0.5 * abs(dz02))  # pixels scale
    bowl = (0.4 * (X**2 + Y**2) + 0.2 * (X * Y))
    twist = 0.2 * (dz01 * X + dz12 * Y) / (abs(dz01) + abs(dz12) + 1e-6)
    W = amp * (bowl + twist)

    # Add tiny spatial noise
    if rng.random() < 0.5:
        U += gaussian_filter(rng.normal(scale=0.03, size=U.shape).astype(np.float32), sigma=1.0)
        V += gaussian_filter(rng.normal(scale=0.03, size=V.shape).astype(np.float32), sigma=1.0)
        W += gaussian_filter(rng.normal(scale=0.02, size=W.shape).astype(np.float32), sigma=1.3)

    return U.astype(np.float32), V.astype(np.float32), W.astype(np.float32)


def warp_image(img: np.ndarray, U: np.ndarray, V: np.ndarray) -> np.ndarray:
    """Warp grayscale image img by displacement fields U (x), V (y) in pixels."""
    h, w = img.shape
    yy, xx = np.meshgrid(np.arange(h, dtype=np.float32), np.arange(w, dtype=np.float32), indexing='ij')
    coords = np.array([np.clip(yy + V, 0, h - 1), np.clip(xx + U, 0, w - 1)])
    warped = map_coordinates(img.astype(np.float32), coords, order=1, mode='reflect')
    warped = np.clip(warped, 0, 255).astype(np.uint8)
    return warped


def compute_strains(U: np.ndarray, V: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    dUy, dUx = np.gradient(U)
    dVy, dVx = np.gradient(V)
    exx = dUx.astype(np.float32)
    eyy = dVy.astype(np.float32)
    exy = 0.5 * (dUy + dVx).astype(np.float32)
    return exx, eyy, exy


def principal_strain(exx: np.ndarray, eyy: np.ndarray, exy: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    trace = exx + eyy
    diff = exx - eyy
    rad = np.sqrt((diff * 0.5) ** 2 + exy ** 2)
    e1 = 0.5 * trace + rad
    e2 = 0.5 * trace - rad
    return e1, e2


def estimate_curvature(W: np.ndarray) -> float:
    # mean Laplacian magnitude as curvature proxy
    curv = laplace(W)
    return float(np.mean(np.abs(curv)))


def densification_progress(t: float, avg_temp_c: float) -> float:
    # Simple Arrhenius-like densification model mapped to 0..1
    # More heat and longer time -> closer to 1
    Ea_over_R = 8000.0  # arbitrary scaling
    T_K = avg_temp_c + 273.15
    rate = math.exp(-Ea_over_R / max(T_K, 1.0))
    x = 1.0 - math.exp(-rate * max(t, 0.0))
    return float(np.clip(x, 0.0, 1.0))


def save_image(path: str, arr: np.ndarray) -> None:
    Image.fromarray(arr).save(path, format='PNG')


def try_write_parquet(df: pd.DataFrame, path: str) -> None:
    wrote = False
    err = None
    for engine in ("pyarrow", "fastparquet"):
        try:
            df.to_parquet(path, engine=engine, index=False)
            wrote = True
            break
        except Exception as e:
            err = e
    if not wrote:
        # fallback to CSV
        csv_path = path.rsplit('.', 1)[0] + '.csv'
        df.to_csv(csv_path, index=False)


def generate_dataset(cfg: SimConfig) -> str:
    rng = np.random.default_rng(cfg.seed)

    # Paths
    run_dir = os.path.join(cfg.output_root, cfg.run_id)
    cam_dirs = {}
    for cam in cfg.cameras:
        cam_dir = os.path.join(run_dir, 'dic', cam.name)
        cam_frames = os.path.join(cam_dir, 'frames')
        ensure_dir(cam_frames)
        cam_dirs[cam.name] = {"root": cam_dir, "frames": cam_frames}
    derived_dir = os.path.join(run_dir, 'dic', 'derived')
    ensure_dir(derived_dir)
    furnace_dir = os.path.join(run_dir, 'furnace')
    ensure_dir(furnace_dir)
    rl_dir = os.path.join(run_dir, 'rl')
    ensure_dir(rl_dir)

    # Speckle for reference texture
    base_img = generate_speckle(cfg.height, cfg.width, density=0.5, rng=rng)

    n_frames = int(round(cfg.duration_s * cfg.dic_fps))
    dt = 1.0 / cfg.dic_fps
    t0_ns = now_unix_ns()

    # Furnace states
    zones = cfg.furnace.num_zones
    T = np.ones(zones, dtype=np.float32) * (cfg.furnace.ambient_c + 20.0)
    S = np.ones(zones, dtype=np.float32) * (cfg.furnace.ambient_c + 30.0)  # setpoints

    # Logs
    dic_timestamps: List[int] = []
    camA_index_rows: List[Dict] = []
    camB_index_rows: List[Dict] = []
    derived_index_rows: List[Dict] = []

    furnace_actions_rows: List[Dict] = []
    furnace_setpoints_rows: List[Dict] = []
    furnace_temps_rows: List[Dict] = []
    furnace_gas_rows: List[Dict] = []

    rl_rows: List[Dict] = []

    action_dt = cfg.rl.action_dt_s
    action_every_n = max(1, int(round(action_dt * cfg.dic_fps)))

    # Iterate frames
    summary_metrics: List[Dict] = []

    for k in range(n_frames):
        t = k * dt
        ts_ns = t0_ns + int(round(t * 1e9))
        dic_timestamps.append(ts_ns)

        # Occasionally update setpoints via actions
        if k % action_every_n == 0:
            # Random action: delta setpoint per zone
            dS = rng.normal(loc=0.0, scale=3.0, size=zones).astype(np.float32)
            # small correlation to keep smooth
            dS = np.clip(dS, -6.0, 6.0)
            S = np.clip(S + dS, cfg.furnace.ambient_c, cfg.furnace.max_temp_c)
            furnace_actions_rows.append({
                't_ns': ts_ns,
                **{f'delta_setpoint_zone{i+1}_C': float(dS[i]) for i in range(zones)},
            })
            furnace_setpoints_rows.append({
                't_ns': ts_ns,
                **{f'setpoint_zone{i+1}_C': float(S[i]) for i in range(zones)},
            })

        # Evolve temperatures (first-order lag to setpoints + cooling)
        dT = (
            -cfg.furnace.k_cool * (T - cfg.furnace.ambient_c)
            + cfg.furnace.alpha_heat * (S - T)
        ) * dt
        T = T + dT + rng.normal(scale=0.05, size=zones).astype(np.float32)
        T = np.clip(T, cfg.furnace.ambient_c, cfg.furnace.max_temp_c)

        furnace_temps_rows.append({
            't_ns': ts_ns,
            **{f'temperature_zone{i+1}_C': float(T[i]) for i in range(zones)},
            # proxy thermocouples near sample (3 points across X)
            'tc_left_C': float(T[0] + rng.normal(scale=cfg.furnace.sensor_noise_std)),
            'tc_mid_C': float(T[1] + rng.normal(scale=cfg.furnace.sensor_noise_std)),
            'tc_right_C': float(T[2] + rng.normal(scale=cfg.furnace.sensor_noise_std)),
        })

        # Gas sensors drift
        furnace_gas_rows.append({
            't_ns': ts_ns,
            'o2_percent': float(21.0 + 0.05 * math.sin(0.01 * k) + rng.normal(scale=0.02)),
            'h2o_ppm': float(800 + 20 * math.sin(0.02 * k) + rng.normal(scale=5.0)),
        })

        # Compute displacement fields
        U, V, W = compute_displacement_fields(cfg.width, cfg.height, t, T, rng)

        # Derived strains
        exx, eyy, exy = compute_strains(U, V)
        e1, e2 = principal_strain(exx, eyy, exy)
        vmax_strain = float(np.max(np.abs(e1)))
        hetero = float(np.std(e1))
        curv = estimate_curvature(W)

        # Densification estimate
        dens = densification_progress(t, float(T.mean()))

        summary_metrics.append({
            't_ns': ts_ns,
            'frame_idx': k,
            'max_principal_strain': vmax_strain,
            'strain_heterogeneity_std': hetero,
            'curvature_proxy': curv,
            'estimated_density': dens,
            'tc_left_C': furnace_temps_rows[-1]['tc_left_C'],
            'tc_mid_C': furnace_temps_rows[-1]['tc_mid_C'],
            'tc_right_C': furnace_temps_rows[-1]['tc_right_C'],
        })

        # Save derived full-field as NPZ (U,V,W, strains)
        np.savez_compressed(
            os.path.join(derived_dir, f'frame_{k:06d}.npz'),
            U=U.astype(np.float32), V=V.astype(np.float32), W=W.astype(np.float32),
            exx=exx.astype(np.float32), eyy=eyy.astype(np.float32), exy=exy.astype(np.float32)
        )
        derived_index_rows.append({'t_ns': ts_ns, 'frame_idx': k, 'path': f'dic/derived/frame_{k:06d}.npz'})

        # Camera A warp
        camA = cfg.cameras[0]
        imgA = warp_image(base_img, U, V)
        # add camera noise
        if camA.noise_std > 0:
            imgA = np.clip(imgA.astype(np.float32) + rng.normal(scale=camA.noise_std, size=imgA.shape), 0, 255).astype(np.uint8)
        pathA = os.path.join(cam_dirs[camA.name]['frames'], f'frame_{k:06d}.png')
        save_image(pathA, imgA)
        camA_index_rows.append({'t_ns': ts_ns, 'frame_idx': k, 'path': f'dic/{camA.name}/frames/frame_{k:06d}.png'})

        # Camera B warp with disparity due to W
        camB = cfg.cameras[1]
        disparity = camB.baseline_pixels * W
        imgB = warp_image(base_img, U + disparity, V)
        if camB.noise_std > 0:
            imgB = np.clip(imgB.astype(np.float32) + rng.normal(scale=camB.noise_std, size=imgB.shape), 0, 255).astype(np.uint8)
        pathB = os.path.join(cam_dirs[camB.name]['frames'], f'frame_{k:06d}.png')
        save_image(pathB, imgB)
        camB_index_rows.append({'t_ns': ts_ns, 'frame_idx': k, 'path': f'dic/{camB.name}/frames/frame_{k:06d}.png'})

    # Build RL transitions at action steps
    sm_df = pd.DataFrame(summary_metrics)
    # compute warpage_rate between frames (forward difference)
    sm_df = sm_df.sort_values('frame_idx').reset_index(drop=True)
    curv_diff = sm_df['curvature_proxy'].diff().fillna(0.0).values
    warpage_rate = curv_diff / dt

    # join furnace temps for tc metrics already included

    action_indices = list(range(0, n_frames, action_every_n))
    for i, k in enumerate(action_indices):
        k_next = action_indices[i+1] if i + 1 < len(action_indices) else min(k + action_every_n, n_frames - 1)
        row_s = sm_df.iloc[k]
        row_sp = sm_df.iloc[k_next]
        # get action at k, if exists
        if k < len(furnace_actions_rows):
            arow = furnace_actions_rows[k // action_every_n]
        else:
            arow = {'delta_setpoint_zone1_C': 0.0, 'delta_setpoint_zone2_C': 0.0, 'delta_setpoint_zone3_C': 0.0}

        # reward
        r = -(
            cfg.rl.w1 * abs(warpage_rate[k])
            + cfg.rl.w2 * abs(row_sp['max_principal_strain'])
            + cfg.rl.w3 * (cfg.rl.target_density - row_sp['estimated_density']) ** 2
        )
        rl_rows.append({
            't_ns': int(row_s['t_ns']),
            't_next_ns': int(row_sp['t_ns']),
            # state s
            's.max_principal_strain': float(row_s['max_principal_strain']),
            's.strain_heterogeneity_std': float(row_s['strain_heterogeneity_std']),
            's.curvature_proxy': float(row_s['curvature_proxy']),
            's.tc_left_C': float(row_s['tc_left_C']),
            's.tc_mid_C': float(row_s['tc_mid_C']),
            's.tc_right_C': float(row_s['tc_right_C']),
            's.time_in_cycle_s': float((row_s['frame_idx']) * dt),
            's.estimated_density': float(row_s['estimated_density']),
            # action a
            'a.delta_setpoint_zone1_C': float(arow.get('delta_setpoint_zone1_C', 0.0)),
            'a.delta_setpoint_zone2_C': float(arow.get('delta_setpoint_zone2_C', 0.0)),
            'a.delta_setpoint_zone3_C': float(arow.get('delta_setpoint_zone3_C', 0.0)),
            # reward r
            'r': float(r),
            # next state s'
            'sp.max_principal_strain': float(row_sp['max_principal_strain']),
            'sp.strain_heterogeneity_std': float(row_sp['strain_heterogeneity_std']),
            'sp.curvature_proxy': float(row_sp['curvature_proxy']),
            'sp.tc_left_C': float(row_sp['tc_left_C']),
            'sp.tc_mid_C': float(row_sp['tc_mid_C']),
            'sp.tc_right_C': float(row_sp['tc_right_C']),
            'sp.time_in_cycle_s': float((row_sp['frame_idx']) * dt),
            'sp.estimated_density': float(row_sp['estimated_density']),
        })

    # Save indices and logs
    pd.DataFrame(camA_index_rows).to_csv(os.path.join(cam_dirs[cfg.cameras[0].name]['root'], 'timestamps.csv'), index=False)
    pd.DataFrame(camB_index_rows).to_csv(os.path.join(cam_dirs[cfg.cameras[1].name]['root'], 'timestamps.csv'), index=False)
    pd.DataFrame(derived_index_rows).to_csv(os.path.join(derived_dir, 'timestamps.csv'), index=False)

    furnace_actions_df = pd.DataFrame(furnace_actions_rows)
    furnace_setpoints_df = pd.DataFrame(furnace_setpoints_rows)
    furnace_temps_df = pd.DataFrame(furnace_temps_rows)
    furnace_gas_df = pd.DataFrame(furnace_gas_rows)

    furnace_actions_df.to_csv(os.path.join(furnace_dir, 'actions.csv'), index=False)
    furnace_setpoints_df.to_csv(os.path.join(furnace_dir, 'setpoints.csv'), index=False)
    furnace_temps_df.to_csv(os.path.join(furnace_dir, 'temperatures.csv'), index=False)
    furnace_gas_df.to_csv(os.path.join(furnace_dir, 'gas.csv'), index=False)

    summary_df = pd.DataFrame(summary_metrics)
    try_write_parquet(summary_df, os.path.join(derived_dir, 'summary_metrics.parquet'))

    rl_df = pd.DataFrame(rl_rows)
    try_write_parquet(rl_df, os.path.join(rl_dir, 'transitions.parquet'))

    # State description
    state_desc = {
        'state_columns': [c for c in rl_df.columns if c.startswith('s.')],
        'action_columns': [c for c in rl_df.columns if c.startswith('a.')],
        'reward_column': 'r',
        'next_state_columns': [c for c in rl_df.columns if c.startswith('sp.')],
        'timestamps': {'t_ns': 'state time', 't_next_ns': 'next state time'},
    }
    with open(os.path.join(rl_dir, 'state_description.json'), 'w') as f:
        json.dump(state_desc, f, indent=2)

    # Metadata
    meta = {
        'run_id': cfg.run_id,
        'created_unix_ns': now_unix_ns(),
        'duration_s': cfg.duration_s,
        'dic_fps': cfg.dic_fps,
        'frame_count': n_frames,
        'width': cfg.width,
        'height': cfg.height,
        'seed': cfg.seed,
        'cameras': [asdict(c) for c in cfg.cameras],
        'furnace': asdict(cfg.furnace),
        'rl': asdict(cfg.rl),
        'paths': {
            'dic': os.path.join(run_dir, 'dic'),
            'furnace': furnace_dir,
            'rl': rl_dir,
        }
    }
    with open(os.path.join(run_dir, 'metadata.json'), 'w') as f:
        json.dump(meta, f, indent=2)

    return run_dir


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Generate synthetic Phase 2 dataset: DIC, furnace, RL tuples')
    p.add_argument('--duration', type=float, default=8.0, help='Duration in seconds')
    p.add_argument('--fps', type=float, default=20.0, help='DIC frame rate')
    p.add_argument('--width', type=int, default=256, help='Frame width')
    p.add_argument('--height', type=int, default=256, help='Frame height')
    p.add_argument('--seed', type=int, default=42, help='RNG seed')
    p.add_argument('--output-root', type=str, default='/workspace/datasets/phase2', help='Output root directory')
    p.add_argument('--run-id', type=str, default=None, help='Run identifier (default timestamp)')
    p.add_argument('--w1', type=float, default=1.0, help='Reward weight for warpage_rate')
    p.add_argument('--w2', type=float, default=5.0, help='Reward weight for max strain')
    p.add_argument('--w3', type=float, default=10.0, help='Reward weight for density error squared')
    p.add_argument('--action-dt', type=float, default=0.5, help='Seconds between actions')
    return p.parse_args()


def main() -> None:
    args = parse_args()
    run_id = args.run_id or time.strftime('run_%Y%m%d_%H%M%S')

    cameras = [
        CameraConfig(name='camera_A', width=args.width, height=args.height, baseline_pixels=0.0, noise_std=0.7),
        CameraConfig(name='camera_B', width=args.width, height=args.height, baseline_pixels=1.8, noise_std=0.7),
    ]

    furnace = FurnaceConfig(
        num_zones=3,
        ambient_c=25.0,
        max_temp_c=900.0,
        k_cool=0.08,
        alpha_heat=0.45,
        sensor_noise_std=0.5,
    )

    rl = RLConfig(
        action_dt_s=float(args.action_dt),
        w1=float(args.w1),
        w2=float(args.w2),
        w3=float(args.w3),
        target_density=1.0,
    )

    cfg = SimConfig(
        duration_s=float(args.duration),
        dic_fps=float(args.fps),
        width=int(args.width),
        height=int(args.height),
        seed=int(args.seed),
        output_root=str(args.output_root),
        run_id=run_id,
        cameras=cameras,
        furnace=furnace,
        rl=rl,
    )

    out_dir = generate_dataset(cfg)
    print(json.dumps({'dataset_dir': out_dir}, indent=2))


if __name__ == '__main__':
    main()
