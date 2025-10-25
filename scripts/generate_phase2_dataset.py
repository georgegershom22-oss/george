#!/usr/bin/env python3

from __future__ import annotations

import math
import os
import random
import shutil
import sys
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import yaml
from tqdm import tqdm

import imageio
import orjson
import cv2
import csv


@dataclass
class CameraConfig:
    name: str
    parallax_factor: float
    skew_x: float
    skew_y: float


@dataclass
class RewardWeights:
    w1_warpage_rate: float
    w2_max_strain: float
    w3_density_error_sq: float


@dataclass
class SimulationConfig:
    # Video and field resolution
    width_px: int = 480
    height_px: int = 480
    grid_downsample: int = 2  # compute fields at resolution/2 to reduce size
    fps: int = 60
    num_frames: int = 300

    # Speckle generation
    speckle_threshold: float = 0.55
    speckle_blur_sigma: float = 0.8
    speckle_contrast: float = 0.9

    # Temperature dynamics
    t_init_c: float = 500.0
    t_target_c: float = 1200.0
    num_zones: int = 3
    zone_time_constant_s: float = 4.0
    zone_coupling: float = 0.06
    sensor_noise_c: float = 0.7

    # Densification kinetics (toy model)
    rho_init: float = 0.60  # initial relative density
    rho_target: float = 0.95
    k0: float = 2.5e-3
    ea_over_r: float = 18000.0  # Ea/R in Kelvin

    # Displacement/warp scaling
    shrinkage_scale: float = 0.06
    warp_temp_sensitivity: float = 1.2e-4
    warp_smooth_sigma: float = 15.0

    # Rendering
    camera_0: CameraConfig = field(
        default_factory=lambda: CameraConfig("cam0", parallax_factor=0.0, skew_x=0.002, skew_y=0.0)
    )
    camera_1: CameraConfig = field(
        default_factory=lambda: CameraConfig("cam1", parallax_factor=0.18, skew_x=-0.001, skew_y=0.001)
    )

    # Reward
    reward_weights: RewardWeights = field(
        default_factory=lambda: RewardWeights(
            w1_warpage_rate=1.0, w2_max_strain=100.0, w3_density_error_sq=500.0
        )
    )

    # Random seed
    seed: int = 42


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def generate_speckle_texture(width: int, height: int, threshold: float, blur_sigma: float, contrast: float, rng: np.random.Generator) -> np.ndarray:
    base_noise = rng.random((height, width)).astype(np.float32)
    speckle = (base_noise > threshold).astype(np.float32)
    speckle = cv2.GaussianBlur(speckle, (0, 0), blur_sigma)
    speckle = (speckle - speckle.min()) / (speckle.max() - speckle.min() + 1e-8)
    speckle = (speckle * contrast + (1.0 - contrast)).clip(0.0, 1.0)
    speckle = (speckle * 255.0).astype(np.uint8)
    return speckle


def smooth2d(field: np.ndarray, sigma: float) -> np.ndarray:
    if sigma <= 0:
        return field
    ksize = max(3, int(round(sigma * 6)) | 1)
    return cv2.GaussianBlur(field, (ksize, ksize), sigmaX=sigma, sigmaY=sigma, borderType=cv2.BORDER_REFLECT)


def simulate_controls(cfg: SimulationConfig, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    # Smooth ramp to target + small random increments as "actions"
    t = np.arange(cfg.num_frames) / cfg.fps
    ramp = cfg.t_init_c + (cfg.t_target_c - cfg.t_init_c) * (1 - np.exp(-t / (cfg.num_frames / cfg.fps / 3)))

    setpoints = np.zeros((cfg.num_frames, cfg.num_zones), dtype=np.float32)
    actions = np.zeros_like(setpoints)

    # Zone offsets introduce spatial gradients; add low-frequency random walk for each zone
    zone_offsets = rng.normal(0.0, 8.0, size=(cfg.num_frames, cfg.num_zones)).astype(np.float32)
    # Smooth with centered moving average window=21
    window = 21
    kernel = np.ones(window, dtype=np.float32) / float(window)
    pad_left = window // 2
    pad_right = window - 1 - pad_left
    for z in range(cfg.num_zones):
        series = zone_offsets[:, z]
        series_padded = np.pad(series, (pad_left, pad_right), mode="edge")
        smoothed = np.convolve(series_padded, kernel, mode="valid")
        zone_offsets[:, z] = smoothed.astype(np.float32)

    for k in range(cfg.num_frames):
        if k == 0:
            setpoints[k] = ramp[k] + zone_offsets[k]
            actions[k] = setpoints[k] - (cfg.t_init_c + zone_offsets[0])
        else:
            # Base ramp progression
            desired = ramp[k] + zone_offsets[k]
            # Action is the change we execute this step
            action_k = (desired - setpoints[k - 1])
            # Limit per-step changes
            max_step = 4.0
            action_k = np.clip(action_k, -max_step, max_step)
            actions[k] = action_k
            setpoints[k] = setpoints[k - 1] + action_k

    return setpoints, actions


def simulate_zone_temperatures(cfg: SimulationConfig, setpoints: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    temps = np.zeros_like(setpoints)
    alpha = 1.0 - math.exp(-1.0 / (cfg.zone_time_constant_s * cfg.fps))
    coupling = cfg.zone_coupling
    for k in range(cfg.num_frames):
        if k == 0:
            temps[k] = setpoints[k]
        else:
            prev = temps[k - 1]
            # Coupled first-order response
            coupled = prev + coupling * (prev.mean() - prev)
            temps[k] = coupled + alpha * (setpoints[k] - coupled)
        temps[k] += rng.normal(0.0, cfg.sensor_noise_c, size=temps[k].shape).astype(np.float32)
    return temps


def build_zone_influence_maps(height: int, width: int) -> np.ndarray:
    # Three Gaussian lobes across the sample surface
    yy, xx = np.meshgrid(np.linspace(-1, 1, height), np.linspace(-1, 1, width), indexing="ij")
    centers = [(-0.5, 0.0), (0.5, 0.0), (0.0, 0.5)]
    sigmas = [0.7, 0.7, 0.9]
    infl = []
    for (cx, cy), s in zip(centers, sigmas):
        g = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * s * s))).astype(np.float32)
        infl.append(g)
    infl = np.stack(infl, axis=-1)
    infl_sum = infl.sum(axis=-1, keepdims=True) + 1e-8
    infl /= infl_sum
    return infl  # shape (H, W, 3)


def temperature_field_from_zones(zone_temps_c: np.ndarray, influence_maps: np.ndarray) -> np.ndarray:
    # zone_temps_c shape (3,), influence_maps (H, W, 3)
    field = (influence_maps * zone_temps_c.reshape(1, 1, -1)).sum(axis=-1)
    return field.astype(np.float32)


def update_density(cfg: SimulationConfig, prev_rho: float, t_mean_c: float, dt_s: float) -> float:
    t_k = t_mean_c + 273.15
    rate = cfg.k0 * math.exp(-cfg.ea_over_r / max(t_k, 1.0)) * (cfg.rho_target - prev_rho)
    rho = prev_rho + rate * dt_s
    rho = float(np.clip(rho, 0.0, 0.999))
    return rho


def compute_displacement_fields(cfg: SimulationConfig, t_field_c: np.ndarray, rho: float, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    h, w = t_field_c.shape
    yy, xx = np.meshgrid(np.linspace(-1, 1, h), np.linspace(-1, 1, w), indexing="ij")

    t_mean = float(t_field_c.mean())
    t_centered = t_field_c - t_mean
    t_centered = smooth2d(t_centered, sigma=cfg.warp_smooth_sigma)

    # Isotropic shrinkage proportional to densification
    shrink = cfg.shrinkage_scale * (rho - 0.5)
    u_shrink = -shrink * xx
    v_shrink = -shrink * yy

    # Thermally induced bending out-of-plane
    w_bend = cfg.warp_temp_sensitivity * (xx * xx - yy * yy) * t_centered
    w_bend += cfg.warp_temp_sensitivity * 0.5 * xx * yy * t_centered

    # Low-frequency spatial noise to mimic microstructural irregularities
    noise = rng.normal(0.0, 1.0, size=t_field_c.shape).astype(np.float32)
    noise = smooth2d(noise, sigma=25.0)
    w_noise = 1e-3 * noise

    # In-plane thermal expansion gradients
    grad_y, grad_x = np.gradient(t_centered)
    u_therm = 2e-5 * smooth2d(grad_x, sigma=7.0)
    v_therm = 2e-5 * smooth2d(grad_y, sigma=7.0)

    u = (u_shrink + u_therm).astype(np.float32)
    v = (v_shrink + v_therm).astype(np.float32)
    w_out = (w_bend + w_noise).astype(np.float32)

    return u, v, w_out


def compute_strain(u: np.ndarray, v: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Central differences with grid normalized to [-1, 1]
    h, w = u.shape
    # spacing ~ 2/(w-1) and 2/(h-1), but these are scale factors; for relative comparisons we can treat as 1
    dv_dy, dv_dx = np.gradient(v)
    du_dy, du_dx = np.gradient(u)
    exx = du_dx.astype(np.float32)
    eyy = dv_dy.astype(np.float32)
    exy = 0.5 * (du_dy + dv_dx).astype(np.float32)
    return exx, eyy, exy


def principal_strains(exx: np.ndarray, eyy: np.ndarray, exy: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    trace = exx + eyy
    det_term = ((exx - eyy) * 0.5) ** 2 + exy ** 2
    root = np.sqrt(np.maximum(det_term, 0.0).astype(np.float32))
    l1 = 0.5 * trace + root
    l2 = 0.5 * trace - root
    return l1.astype(np.float32), l2.astype(np.float32)


def curvature_metrics(w_out: np.ndarray) -> Tuple[float, float]:
    # Mean absolute curvature via Laplacian approximation; and max absolute curvature
    wyy, wxy = np.gradient(w_out)
    wyy_y, wyx_x = np.gradient(wyy), np.gradient(wxy)[1]
    lap = wyx_x + wyy_y
    mean_abs = float(np.mean(np.abs(lap)))
    max_abs = float(np.max(np.abs(lap)))
    return mean_abs, max_abs


def render_frame(base_speckle: np.ndarray, u: np.ndarray, v: np.ndarray, w_out: np.ndarray, cam: CameraConfig, rng: np.random.Generator) -> np.ndarray:
    h, w = base_speckle.shape
    yy, xx = np.meshgrid(np.arange(h, dtype=np.float32), np.arange(w, dtype=np.float32), indexing="ij")

    # Pixel-level displacement map (in pixels)
    # Scale normalized displacements (defined on [-1,1] coordinate grid) to pixels
    scale_x = w / 2.0
    scale_y = h / 2.0
    disp_x = u * scale_x + cam.parallax_factor * w_out * scale_x + cam.skew_x * (xx - w * 0.5)
    disp_y = v * scale_y + cam.parallax_factor * w_out * scale_y + cam.skew_y * (yy - h * 0.5)

    map_x = (xx - disp_x).astype(np.float32)
    map_y = (yy - disp_y).astype(np.float32)

    frame = cv2.remap(base_speckle, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    # Sensor/atmospheric heat shimmer blur and noise
    blur_sigma = rng.uniform(0.3, 1.0)
    frame = cv2.GaussianBlur(frame, (0, 0), blur_sigma)
    noise = rng.normal(0.0, 5.0, size=frame.shape).astype(np.float32)
    frame_f = np.clip(frame.astype(np.float32) + noise, 0.0, 255.0).astype(np.uint8)
    return frame_f


def sha256_of_file(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def save_npz_compressed(path: Path, arrays: Dict[str, np.ndarray]) -> None:
    # Convert to float16 where reasonable to reduce size
    arrays16: Dict[str, np.ndarray] = {}
    for k, v in arrays.items():
        if v.dtype in (np.float32, np.float64):
            arrays16[k] = v.astype(np.float16)
        else:
            arrays16[k] = v
    np.savez_compressed(str(path), **arrays16)


def main() -> None:
    cfg = SimulationConfig()
    rng = np.random.default_rng(cfg.seed)

    # Output directories
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    run_dir = Path("/workspace/data/phase2") / f"run_{timestamp}"
    dic_dir = run_dir / "dic"
    cam0_dir = dic_dir / cfg.camera_0.name
    cam1_dir = dic_dir / cfg.camera_1.name
    derived_dir = run_dir / "derived_fields"
    furnace_dir = run_dir / "furnace"
    rl_dir = run_dir / "rl"
    ensure_dir(cam0_dir)
    ensure_dir(cam1_dir)
    ensure_dir(derived_dir)
    ensure_dir(furnace_dir)
    ensure_dir(rl_dir)

    # Generate base speckle texture
    base_speckle = generate_speckle_texture(
        cfg.width_px, cfg.height_px, cfg.speckle_threshold, cfg.speckle_blur_sigma, cfg.speckle_contrast, rng
    )

    # Prepare zone influence maps (at full resolution)
    zone_influence = build_zone_influence_maps(cfg.height_px, cfg.width_px)

    # Controls and temperatures
    setpoints, actions = simulate_controls(cfg, rng)
    zone_temps = simulate_zone_temperatures(cfg, setpoints, rng)

    # Timebase
    timestamps = (np.arange(cfg.num_frames) / cfg.fps).astype(np.float64)

    # Video writers
    vid0_path = cam0_dir / "video.mp4"
    vid1_path = cam1_dir / "video.mp4"
    writer0 = imageio.get_writer(str(vid0_path), fps=cfg.fps, codec="libx264", quality=7)
    writer1 = imageio.get_writer(str(vid1_path), fps=cfg.fps, codec="libx264", quality=7)

    # Derived fields storage (downsample to reduce size)
    ds = max(1, cfg.grid_downsample)
    grid_h = cfg.height_px // ds
    grid_w = cfg.width_px // ds

    U_all = np.zeros((cfg.num_frames, grid_h, grid_w), dtype=np.float32)
    V_all = np.zeros_like(U_all)
    W_all = np.zeros_like(U_all)
    EXX_all = np.zeros_like(U_all)
    EYY_all = np.zeros_like(U_all)
    EXY_all = np.zeros_like(U_all)

    # Sensor rows for CSV writing later
    sensor_cols = [
        "timestamp_s",
        "zoneA_C",
        "zoneB_C",
        "zoneC_C",
        "sample_TC1_C",
        "sample_TC2_C",
        "o2_ppm",
        "chamber_pressure_torr",
        "relative_density",
        "densification_rate_s",
        "curvature_mean_abs",
        "curvature_max_abs",
        "max_principal_strain",
        "strain_std",
    ]
    sensors_rows: List[List[float]] = []

    # Controls rows for CSV
    controls_cols = [
        "timestamp_s",
        "setpoint_zoneA_C",
        "setpoint_zoneB_C",
        "setpoint_zoneC_C",
        "action_dZoneA_C",
        "action_dZoneB_C",
        "action_dZoneC_C",
    ]
    # We'll prepare controls_rows at the end for performance

    # RL tuples file
    tuples_path = rl_dir / "tuples.jsonl"
    tuples_f = tuples_path.open("wb")

    # Precompute coordinates for downsampled field extraction
    if ds > 1:
        # Use OpenCV resize for downsampling fields
        def downsample(arr: np.ndarray) -> np.ndarray:
            return cv2.resize(arr, (grid_w, grid_h), interpolation=cv2.INTER_AREA)
    else:
        def downsample(arr: np.ndarray) -> np.ndarray:
            return arr

    # Densification state
    rho = cfg.rho_init
    prev_curv_mean_abs = None

    # Sample thermocouples: pick two points in the field
    tc1_rc = (int(cfg.height_px * 0.35), int(cfg.width_px * 0.4))
    tc2_rc = (int(cfg.height_px * 0.65), int(cfg.width_px * 0.6))

    # Main simulation loop
    for k in tqdm(range(cfg.num_frames), desc="Generating frames"):
        t_field = temperature_field_from_zones(zone_temps[k], zone_influence)
        # Update density
        dt_s = 1.0 / cfg.fps
        rho_prev = rho
        rho = update_density(cfg, rho, float(t_field.mean()), dt_s)
        dens_rate = (rho - rho_prev) / dt_s

        # Displacement fields at full resolution
        u_full, v_full, w_full = compute_displacement_fields(cfg, t_field, rho, rng)

        # Derived strains
        exx_full, eyy_full, exy_full = compute_strain(u_full, v_full)
        l1, l2 = principal_strains(exx_full, eyy_full, exy_full)
        max_principal = float(np.max(np.abs(l1)))
        strain_std = float(np.std(l1))
        curv_mean_abs, curv_max_abs = curvature_metrics(w_full)

        # Downsample and store
        U_all[k] = downsample(u_full)
        V_all[k] = downsample(v_full)
        W_all[k] = downsample(w_full)
        EXX_all[k] = downsample(exx_full)
        EYY_all[k] = downsample(eyy_full)
        EXY_all[k] = downsample(exy_full)

        # Render frames
        frame0 = render_frame(base_speckle, u_full, v_full, w_full, cfg.camera_0, rng)
        frame1 = render_frame(base_speckle, u_full, v_full, w_full, cfg.camera_1, rng)
        writer0.append_data(frame0)
        writer1.append_data(frame1)

        # Sensors and metrics
        tc1_c = float(t_field[tc1_rc])
        tc2_c = float(t_field[tc2_rc])
        o2_ppm = float(5 + 0.5 * math.sin(0.01 * k) + np.random.normal(0.0, 0.1))
        pressure = float(760 - 10 * math.exp(-k / 100.0) + np.random.normal(0.0, 0.2))

        sensors_rows.append([
            float(timestamps[k]),
            float(zone_temps[k, 0]),
            float(zone_temps[k, 1]),
            float(zone_temps[k, 2]),
            tc1_c,
            tc2_c,
            o2_ppm,
            pressure,
            float(rho),
            float(dens_rate),
            float(curv_mean_abs),
            float(curv_max_abs),
            float(max_principal),
            float(strain_std),
        ])

        # RL tuple (except for last frame which has no next_state yet)
        if k > 0:
            warpage_rate = 0.0 if prev_curv_mean_abs is None else abs(curv_mean_abs - prev_curv_mean_abs) * cfg.fps
        else:
            warpage_rate = 0.0

        density_error = cfg.rho_target - float(rho)
        weights = cfg.reward_weights
        reward = -(
            weights.w1_warpage_rate * abs(warpage_rate)
            + weights.w2_max_strain * abs(max_principal)
            + weights.w3_density_error_sq * (density_error ** 2)
        )

        # State vector
        state = {
            "t_s": float(timestamps[k]),
            "dic_max_principal_strain": float(max_principal),
            "dic_strain_std": float(strain_std),
            "dic_curvature_mean_abs": float(curv_mean_abs),
            "thermal_zoneA_C": float(zone_temps[k, 0]),
            "thermal_zoneB_C": float(zone_temps[k, 1]),
            "thermal_zoneC_C": float(zone_temps[k, 2]),
            "sample_TC1_C": tc1_c,
            "sample_TC2_C": tc2_c,
            "process_time_s": float(timestamps[k]),
            "process_relative_density": float(rho),
            "process_densification_rate_s": float(dens_rate),
            "frame_index": int(k),
        }

        action = {
            "dZoneA_C": float(actions[k, 0]),
            "dZoneB_C": float(actions[k, 1]),
            "dZoneC_C": float(actions[k, 2]),
        }

        # Next state placeholder will be filled when k < num_frames-1; for last frame we skip writing a tuple
        if k < cfg.num_frames - 1:
            # We do not know next state's metrics yet; write tuple with s at k and s' to be computed next iter
            # To keep streaming simple, we will buffer last state and write when we have next_state
            pass

        # Store prev curvature for next warpage rate
        prev_curv_mean_abs = curv_mean_abs

        # To emit RL tuples with next_state, we will write them from the second frame onward, using previous cached state
        if k == 0:
            prev_state = state
            prev_reward = reward
            prev_action = action
            prev_frame_index = k
        else:
            next_state = state
            tuple_obj = {
                "t": float(timestamps[k - 1]),
                "state": prev_state,
                "action": prev_action,
                "reward": float(prev_reward),
                "next_t": float(timestamps[k]),
                "next_state": next_state,
                "refs": {
                    "cam0_video": str(vid0_path.relative_to(run_dir)),
                    "cam1_video": str(vid1_path.relative_to(run_dir)),
                    "frame_index": int(prev_frame_index),
                },
            }
            tuples_f.write(orjson.dumps(tuple_obj))
            tuples_f.write(b"\n")
            # Shift cache
            prev_state = state
            prev_reward = reward
            prev_action = action
            prev_frame_index = k

    # Close video writers and RL file
    writer0.close()
    writer1.close()
    tuples_f.close()

    # Save derived fields (stacked)
    fields_path = derived_dir / "fields_downsampled_fp16.npz"
    save_npz_compressed(
        fields_path,
        {
            "U": U_all,
            "V": V_all,
            "W": W_all,
            "EXX": EXX_all,
            "EYY": EYY_all,
            "EXY": EXY_all,
            "timestamps_s": timestamps.astype(np.float32),
        },
    )

    # Save sensors and controls
    sensors_csv = furnace_dir / "sensors.csv"
    controls_csv = furnace_dir / "controls.csv"
    # Write sensors CSV
    with sensors_csv.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(sensor_cols)
        writer.writerows(sensors_rows)
    # Build and write controls CSV
    with controls_csv.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(controls_cols)
        for k in range(cfg.num_frames):
            writer.writerow([
                float(timestamps[k]),
                float(setpoints[k, 0]),
                float(setpoints[k, 1]),
                float(setpoints[k, 2]),
                float(actions[k, 0]),
                float(actions[k, 1]),
                float(actions[k, 2]),
            ])

    # Metadata
    meta = {
        "purpose": "Phase 2: Core Real-Time Training & Validation Data",
        "description": {
            "visual_data": "Two-camera high-contrast speckle videos (synthetic).",
            "derived_data": "Downsampled full-field displacement (U,V,W) and strain (EXX,EYY,EXY) maps per frame.",
            "furnace_data": "Synchronized setpoints, actions (per-step setpoint changes), measured zone temps, gas, pressure.",
            "rl_tuples": "JSONL of state-action-reward-next_state with timestamps and video refs.",
        },
        "config": asdict(cfg),
        "cameras": [asdict(cfg.camera_0), asdict(cfg.camera_1)],
        "reward_weights": asdict(cfg.reward_weights),
        "files": {
            "cam0_video": str(vid0_path.relative_to(run_dir)),
            "cam1_video": str(vid1_path.relative_to(run_dir)),
            "derived_fields": str(fields_path.relative_to(run_dir)),
            "sensors_csv": str(sensors_csv.relative_to(run_dir)),
            "controls_csv": str(controls_csv.relative_to(run_dir)),
            "rl_tuples_jsonl": str(tuples_path.relative_to(run_dir)),
        },
    }
    with (run_dir / "metadata.yaml").open("w") as f:
        yaml.safe_dump(meta, f, sort_keys=False)

    # Checksums manifest
    manifest = {
        "run_dir": str(run_dir),
        "created_at": timestamp,
        "checksums": {},
    }
    for rel in meta["files"].values():
        p = run_dir / rel
        manifest["checksums"][rel] = sha256_of_file(p)
    with (run_dir / "manifest.json").open("wb") as f:
        f.write(orjson.dumps(manifest))

    print(f"Dataset generated at {run_dir}")


if __name__ == "__main__":
    main()
