#!/usr/bin/env python3
"""
Phase 2: Core Real-Time Training & Validation Data Generator

Generates synthetic real-time DIC streams (multi-camera videos + derived fields),
Synchronized furnace control/sensor streams, and fused RL tuples (s, a, r, s').

Outputs organized under runs/<run_id> with a manifest summarizing artifacts.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import shutil
import string
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

import imageio
import numpy as np
import pandas as pd
from PIL import Image
from scipy import ndimage


# -----------------------------
# Config and utilities
# -----------------------------

@dataclass
class CameraConfig:
    camera_id: str
    fx: float
    fy: float
    cx: float
    cy: float
    yaw_deg: float  # horizontal angle relative to surface normal
    pitch_deg: float  # vertical tilt
    baseline_mm: float  # not strictly used; documented for realism


@dataclass
class RunConfig:
    run_id: str
    split: str  # "train" or "val"
    seed: int
    fps: int
    num_steps: int
    height: int
    width: int
    downsample_fields_by: int  # downsample factor for fields (U,V,W, strains)
    num_zones: int  # furnace zones
    num_thermocouples: int
    gas_channels: Tuple[str, ...]  # e.g., ("O2_ppm", "H2_percent", "Ar_percent")
    weights: Tuple[float, float, float]  # w1,w2,w3 in reward
    save_frames: bool
    video_codec: str  # e.g., "libx264" or "h264"
    cameras: Tuple[CameraConfig, CameraConfig]


# -----------------------------
# Speckle generation
# -----------------------------

def generate_speckle_image(height: int, width: int, density: float = 0.08, min_radius: int = 1, max_radius: int = 3,
                            bg_level: int = 235, fg_level: int = 30, seed: int | None = None) -> np.ndarray:
    """Create a synthetic high-temp-suitable speckle pattern (grayscale 0-255)."""
    if seed is not None:
        rng = np.random.default_rng(seed)
    else:
        rng = np.random.default_rng()

    img = np.full((height, width), bg_level, dtype=np.uint8)
    num_speckles = int(density * height * width / ((min_radius + max_radius) / 2.0) ** 2)
    for _ in range(num_speckles):
        r = rng.integers(min_radius, max_radius + 1)
        y = rng.integers(r, height - r)
        x = rng.integers(r, width - r)
        yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
        mask = xx * xx + yy * yy <= r * r
        # Randomize speckle intensity slightly
        val = int(np.clip(rng.normal(fg_level, 10), 0, 255))
        img[y - r:y + r + 1, x - r:x + r + 1][mask] = val
    # Add mild perlin-like blur to soften edges for realism
    img = ndimage.gaussian_filter(img, sigma=0.6)
    return img.astype(np.uint8)


# -----------------------------
# Displacement and strain field synthesis
# -----------------------------

def _make_timebase(num_steps: int, fps: int) -> np.ndarray:
    return np.arange(num_steps, dtype=np.float64) / float(fps)


def simulate_displacement_fields(num_steps: int, height: int, width: int, fps: int,
                                 temp_profile: np.ndarray,
                                 seed: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate U, V, W fields with simple physics-inspired deformation over time.
    - W: out-of-plane warpage shaped as a smooth bowl + time-varying amplitude.
    - U, V: in-plane expansion/contraction driven by temperature and W curvature.

    Returns U, V, W of shape (T, H, W), in pixels (unit of displacement in image plane),
    with W also in pseudo-pixels so that small camera tilts translate W into apparent in-plane motion.
    """
    rng = np.random.default_rng(seed)
    yy, xx = np.meshgrid(np.linspace(-1, 1, height), np.linspace(-1, 1, width), indexing="ij")

    # Base spatial patterns
    r2 = xx ** 2 + yy ** 2
    bowl = -r2  # center-up bowl (negative means upward in our convention)
    saddle = xx * yy

    # Normalize patterns
    bowl /= np.max(np.abs(bowl)) + 1e-8
    saddle /= np.max(np.abs(saddle)) + 1e-8

    # Time envelopes coupled to temperature (normalized 0..1)
    temp_norm = (temp_profile - np.min(temp_profile)) / (np.ptp(temp_profile) + 1e-8)

    # Warpage amplitude grows with temperature and process progress, add small noise
    warpage_amp = 2.0 + 6.0 * temp_norm + 0.3 * ndimage.gaussian_filter(rng.standard_normal(num_steps), 1.0)

    # In-plane thermal expansion coefficient in px per normalized temp unit
    alpha_u = 1.2
    alpha_v = 1.0

    U = np.empty((num_steps, height, width), dtype=np.float32)
    V = np.empty_like(U)
    W = np.empty_like(U)

    # Mild spatial gradient for in-plane strain due to temperature gradient
    grad_x = 0.5 * xx
    grad_y = -0.4 * yy

    # Simulate a slow rotation/twist component over time for realism
    angles = 0.03 * np.sin(2 * np.pi * np.arange(num_steps) / max(10, fps // 2))

    for t in range(num_steps):
        amp = warpage_amp[t]
        w_t = amp * (0.75 * bowl + 0.25 * saddle)

        # In-plane expansion proportional to temp and coordinated with W curvature
        u_t = alpha_u * temp_norm[t] * (xx + 0.2 * ndimage.laplace(w_t)) + 0.3 * grad_x
        v_t = alpha_v * temp_norm[t] * (yy + 0.2 * ndimage.laplace(w_t)) + 0.3 * grad_y

        # Apply tiny global rotation per time
        theta = angles[t]
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        u_rot = cos_t * u_t - sin_t * v_t
        v_rot = sin_t * u_t + cos_t * v_t

        U[t] = u_rot
        V[t] = v_rot
        W[t] = w_t

    # Smooth fields over space for continuity
    for t in range(num_steps):
        U[t] = ndimage.gaussian_filter(U[t], sigma=0.8)
        V[t] = ndimage.gaussian_filter(V[t], sigma=0.8)
        W[t] = ndimage.gaussian_filter(W[t], sigma=1.1)

    return U, V, W


def compute_strain_fields(U: np.ndarray, V: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute strain tensor components from displacement fields U,V using finite differences.
    Returns (exx, eyy, exy, prin1, prin2) with shape (T, H, W).
    """
    # Gradients: dU/dx, dU/dy, dV/dx, dV/dy
    dUdy, dUdx = np.gradient(U, axis=(1, 2))
    dVdy, dVdx = np.gradient(V, axis=(1, 2))

    exx = dUdx.astype(np.float32)
    eyy = dVdy.astype(np.float32)
    exy = 0.5 * (dUdy + dVdx).astype(np.float32)

    trace = exx + eyy
    diff = exx - eyy
    rad = np.sqrt((diff * 0.5) ** 2 + exy ** 2)
    prin1 = 0.5 * trace + rad
    prin2 = 0.5 * trace - rad

    return exx, eyy, exy, prin1, prin2


def compute_curvature(W: np.ndarray) -> np.ndarray:
    """Curvature proxy: Laplacian magnitude of W per-frame (H,W)."""
    T = W.shape[0]
    curv = np.empty_like(W)
    for t in range(T):
        curv[t] = np.abs(ndimage.laplace(W[t]))
    return curv


# -----------------------------
# Camera image synthesis
# -----------------------------

def render_frame_from_fields(base_speckle: np.ndarray, U: np.ndarray, V: np.ndarray, W: np.ndarray,
                             cam: CameraConfig) -> np.ndarray:
    """
    Render a single camera frame given base speckle and displacement fields.
    We approximate 3D by projecting out-of-plane W into apparent in-plane motion
    based on yaw and pitch. This yields a realistic DIC-like speckle motion.
    """
    H, Wimg = base_speckle.shape
    # Apparent motion from out-of-plane displacement relative to camera angle
    yaw = math.radians(cam.yaw_deg)
    pitch = math.radians(cam.pitch_deg)
    w_scale_x = math.sin(yaw) * 0.8
    w_scale_y = math.sin(pitch) * 0.8

    U_eff = U + w_scale_x * W
    V_eff = V + w_scale_y * W

    yy, xx = np.meshgrid(np.arange(H, dtype=np.float32), np.arange(Wimg, dtype=np.float32), indexing="ij")
    map_y = yy + V_eff.astype(np.float32)
    map_x = xx + U_eff.astype(np.float32)

    # Sample with map_coordinates; mode='reflect' to handle borders
    warped = ndimage.map_coordinates(base_speckle.astype(np.float32), [map_y, map_x], order=1, mode='reflect')
    warped = np.clip(warped, 0, 255).astype(np.uint8)

    # Add a mild camera-specific vignette and noise
    yy_n = (yy / max(H - 1, 1) - 0.5)
    xx_n = (xx / max(Wimg - 1, 1) - 0.5)
    rad2 = xx_n ** 2 + yy_n ** 2
    vignette = 1.0 - 0.12 * rad2
    noise = np.random.default_rng().normal(0, 2.0, size=warped.shape)

    out = (warped.astype(np.float32) * vignette + noise).clip(0, 255).astype(np.uint8)
    return out


# -----------------------------
# Furnace control and sensors simulation
# -----------------------------

def simulate_furnace_and_sensors(num_steps: int, fps: int, num_zones: int, num_thermocouples: int,
                                 gas_channels: Tuple[str, ...],
                                 seed: int) -> Tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    """
    Simulate actions (zone power deltas and setpoint deltas) and sensors (temperatures, gas).

    Returns:
      actions_df: step-indexed actions with columns like power_delta_zoneA, setpoint_delta_zoneA, ...
      sensors_df: step-indexed sensors with thermocouple temperatures and gas readings
      setpoints: (T, num_zones) current setpoints in C
      temperatures: (T, num_thermocouples) measured temps in C near sample
    """
    rng = np.random.default_rng(seed)
    t = _make_timebase(num_steps, fps)

    zone_names = [f"zone_{i+1}" for i in range(num_zones)]
    tc_names = [f"tc_{i+1}" for i in range(num_thermocouples)]

    # Base program: ramp -> soak -> ramp2 -> soak2 -> cooldown
    # Define nominal setpoint program for each zone with slight variations
    sp_base = np.zeros((num_steps, num_zones), dtype=np.float32)

    def trapezoid_profile(t_arr: np.ndarray, t0: float, t1: float, hold1: float, t2: float, hold2: float,
                          plateau1: float, plateau2: float) -> np.ndarray:
        prof = np.zeros_like(t_arr)
        # Ramp up to plateau1
        mask1 = (t_arr >= t0) & (t_arr < t1)
        prof[mask1] = np.interp(t_arr[mask1], [t0, t1], [25.0, plateau1])
        # Hold1
        maskh1 = (t_arr >= t1) & (t_arr < hold1)
        prof[maskh1] = plateau1
        # Ramp to plateau2
        mask2 = (t_arr >= hold1) & (t_arr < t2)
        prof[mask2] = np.interp(t_arr[mask2], [hold1, t2], [plateau1, plateau2])
        # Hold2
        maskh2 = (t_arr >= t2) & (t_arr < hold2)
        prof[maskh2] = plateau2
        # Cooldown to ambient
        mask3 = t_arr >= hold2
        if np.any(mask3):
            end_t = t_arr[mask3][0]
            prof[mask3] = np.interp(t_arr[mask3], [end_t, end_t + 0.25 * (t2 - t0) + 1e-6], [plateau2, 50.0])
        return prof

    # Design durations based on total time
    total_time = t[-1] if len(t) > 0 else 0.0
    seg = max(total_time / 5.0, 1.0)
    base1 = rng.uniform(800, 1000)
    base2 = rng.uniform(1200, 1400)

    for z in range(num_zones):
        jitter = rng.uniform(-40, 40)
        sp_base[:, z] = trapezoid_profile(t, 0.0, seg, 2 * seg, 3 * seg, 4 * seg, base1 + jitter, base2 + jitter)

    # Actions: at each step, RL applies small deltas to zone power and setpoint
    # We'll simulate the deltas as a smoothed random walk to mimic control decisions
    power_deltas = 0.05 * ndimage.gaussian_filter(rng.standard_normal((num_steps, num_zones)), sigma=(3, 0))
    sp_deltas = 1.5 * ndimage.gaussian_filter(rng.standard_normal((num_steps, num_zones)), sigma=(3, 0))

    actions = {}
    for i, zn in enumerate(zone_names):
        actions[f"power_delta_{zn}"] = power_deltas[:, i]
        actions[f"setpoint_delta_{zn}"] = sp_deltas[:, i]

    actions_df = pd.DataFrame(actions)
    actions_df.insert(0, "step", np.arange(num_steps, dtype=np.int32))

    # Effective setpoints
    setpoints = sp_base + sp_deltas

    # Temperature dynamics: simple linear system with decay to setpoint + coupling + noise
    temperatures = np.zeros((num_steps, num_thermocouples), dtype=np.float32)
    temp_state = np.full(num_thermocouples, 25.0, dtype=np.float32)
    # Map TCs to zones (nearest zone influences strongest)
    tc_to_zone = np.array([i % num_zones for i in range(num_thermocouples)], dtype=np.int32)

    # Zone power effect acts as an acceleration term towards setpoint
    for t_idx in range(num_steps):
        for tc_idx in range(num_thermocouples):
            z = tc_to_zone[tc_idx]
            sp = setpoints[t_idx, z]
            # power influences approach rate; clamp between 0.6..1.4 for realism
            power_eff = np.clip(1.0 + power_deltas[t_idx, z], 0.6, 1.4)
            # Euler update
            k = 0.02 * power_eff  # heating rate coefficient per step
            temp_state[tc_idx] += k * (sp - temp_state[tc_idx])
            # Cross coupling from neighbors
            n1 = tc_to_zone[(tc_idx - 1) % num_thermocouples]
            n2 = tc_to_zone[(tc_idx + 1) % num_thermocouples]
            temp_state[tc_idx] += 0.004 * ((setpoints[t_idx, n1] - temp_state[tc_idx]) + (setpoints[t_idx, n2] - temp_state[tc_idx]))
            # Sensor noise
            temp_state[tc_idx] += 0.5 * rng.standard_normal()
        temperatures[t_idx] = temp_state

    # Gas channels respond to temperature and random purge events
    gas = np.zeros((num_steps, len(gas_channels)), dtype=np.float32)
    purge_events = (rng.random(num_steps) < 0.02).astype(np.float32)
    purge_trace = ndimage.gaussian_filter1d(purge_events, sigma=5)
    for gi, gname in enumerate(gas_channels):
        if "O2" in gname:
            gas[:, gi] = 50 + 20 * purge_trace + 10 * rng.standard_normal(num_steps)
        elif "H2" in gname:
            gas[:, gi] = 3.0 + 0.5 * purge_trace + 0.2 * rng.standard_normal(num_steps)
        else:  # Argon percent or others
            gas[:, gi] = 97.0 - 0.5 * purge_trace + 0.2 * rng.standard_normal(num_steps)

    sensors = {"step": np.arange(num_steps, dtype=np.int32)}
    for i, name in enumerate(tc_names):
        sensors[f"temp_{name}"] = temperatures[:, i]
    for i, name in enumerate(gas_channels):
        sensors[name] = gas[:, i]

    sensors_df = pd.DataFrame(sensors)

    return actions_df, sensors_df, setpoints.astype(np.float32), temperatures.astype(np.float32)


# -----------------------------
# Density/Process metrics and reward
# -----------------------------

def estimate_density_over_time(temperatures: np.ndarray, fps: int) -> np.ndarray:
    """
    Estimate densification curve from temperature exposure using a simple Arrhenius-like model
    integrated over time then passed through a logistic to stay in [0, 1].
    Returns density fraction in [0,1].
    """
    T = temperatures.mean(axis=1)  # average near-sample temperature over TCs
    # Normalize Kelvin-like measure; offset to avoid negatives
    T_K = T + 273.15
    # Arrhenius-esque rate constant (scaled for synthetic time base)
    rate = np.exp(-5000.0 / T_K)
    cumulative = np.cumsum(rate) / float(fps)
    # Logistic mapping to [0, 1]
    density = 1.0 / (1.0 + np.exp(-(cumulative - cumulative.mean()) / (cumulative.std() + 1e-6)))
    return density.astype(np.float32)


def compute_rl_metrics_and_reward(U: np.ndarray, V: np.ndarray, W: np.ndarray,
                                  exx: np.ndarray, eyy: np.ndarray, exy: np.ndarray,
                                  prin1: np.ndarray,
                                  density: np.ndarray,
                                  weights: Tuple[float, float, float],
                                  fps: int) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Compute per-step metrics required by the RL state and the instantaneous reward.
    Metrics: max_principal_strain, strain_std, curvature_metric, warpage, warpage_rate, density
    Reward = - (w1 * |warpage_rate| + w2 * |max_strain| + w3 * (target_density - current_density)^2)
    """
    T = U.shape[0]

    # Curvature from W
    curv = compute_curvature(W)

    # Metrics per frame
    max_principal = np.max(prin1.reshape(T, -1), axis=1)
    strain_std = np.std(prin1.reshape(T, -1), axis=1)
    warpage = np.max(np.abs(W.reshape(T, -1)), axis=1)

    # Warpage rate (per second magnitude)
    d_warp = np.diff(warpage, prepend=warpage[0]) * fps
    warpage_rate = np.abs(d_warp)

    # Curvature metric as spatial mean abs curvature
    curvature_metric = np.mean(np.abs(curv.reshape(T, -1)), axis=1)

    # Target density schedule ramps from 0.3 to 0.98 over time
    target_density = np.linspace(0.3, 0.98, T, dtype=np.float32)

    w1, w2, w3 = weights
    reward = - (w1 * warpage_rate + w2 * np.abs(max_principal) + w3 * (target_density - density) ** 2)

    df = pd.DataFrame({
        "step": np.arange(T, dtype=np.int32),
        "max_principal_strain": max_principal.astype(np.float32),
        "strain_std": strain_std.astype(np.float32),
        "curvature_metric": curvature_metric.astype(np.float32),
        "warpage": warpage.astype(np.float32),
        "warpage_rate": warpage_rate.astype(np.float32),
        "density": density.astype(np.float32),
        "target_density": target_density.astype(np.float32),
        "reward": reward.astype(np.float32),
    })

    return df, reward.astype(np.float32)


# -----------------------------
# RL tuple fusion
# -----------------------------

def build_rl_tuples(metrics_df: pd.DataFrame, actions_df: pd.DataFrame, sensors_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build (s, a, r, s') tuples as a tabular dataset. State uses metrics + key sensors + time.
    Next state columns are suffixed with _next.
    """
    df = metrics_df.merge(actions_df, on="step").merge(sensors_df, on="step")

    # State features
    state_cols = [
        "max_principal_strain", "strain_std", "curvature_metric", "warpage", "warpage_rate", "density",
    ]
    # Add key thermocouples (first 4 or all if fewer)
    tc_cols = [c for c in df.columns if c.startswith("temp_tc_")][:4]
    state_cols += tc_cols
    # Add time as normalized progress
    df["time_s"] = df["step"] / (df["step"].max() + 1e-6)
    state_cols.append("time_s")

    # Action columns
    action_cols = [c for c in df.columns if c.startswith("power_delta_zone_") or c.startswith("setpoint_delta_zone_")]

    # Reward
    reward_col = "reward"

    # Next-state creation by shifting state features by -1 step
    df_next = df[["step"] + state_cols].copy()
    df_next.columns = ["step"] + [f"{c}_next" for c in state_cols]
    tuples = df.merge(df_next, on="step", how="left")

    # Done flag for last step (no next state)
    tuples["done"] = False
    tuples.loc[tuples["step"] >= tuples["step"].max(), "done"] = True

    # Reorder columns: step, states..., actions..., reward, next_states..., done
    ordered_cols = ["step"] + state_cols + action_cols + [reward_col] + [f"{c}_next" for c in state_cols] + ["done"]
    tuples = tuples[ordered_cols]
    return tuples


# -----------------------------
# Video writing helpers
# -----------------------------

def write_video(frames: List[np.ndarray], out_path: str, fps: int, codec: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    writer = imageio.get_writer(out_path, fps=fps, codec=codec, quality=7)
    try:
        for frame in frames:
            writer.append_data(frame)
    finally:
        writer.close()


def save_frames(frames: List[np.ndarray], out_dir: str, prefix: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    for i, frame in enumerate(frames):
        Image.fromarray(frame).save(os.path.join(out_dir, f"{prefix}_{i:05d}.jpg"), quality=90)


# -----------------------------
# Run generation
# -----------------------------

def random_run_id(prefix: str = "run") -> str:
    ts = time.strftime("%Y%m%d_%H%M%S")
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{prefix}_{ts}_{rand}"


def generate_one_run(base_dir: str, cfg: RunConfig) -> Dict:
    run_dir = os.path.join(base_dir, cfg.split, cfg.run_id)
    frames_root = os.path.join(run_dir, "frames")
    videos_root = os.path.join(run_dir, "videos")
    fields_path = os.path.join(run_dir, "dic_fields_downsampled.npz")
    metrics_csv = os.path.join(run_dir, "dic_metrics.csv")
    actions_csv = os.path.join(run_dir, "furnace_actions.csv")
    sensors_csv = os.path.join(run_dir, "furnace_sensors.csv")
    rl_parquet = os.path.join(run_dir, "rl_tuples.parquet")
    manifest_path = os.path.join(run_dir, "manifest.json")

    os.makedirs(run_dir, exist_ok=True)

    rng = np.random.default_rng(cfg.seed)

    # Speckle base per run (shared across cameras)
    base_speckle = generate_speckle_image(cfg.height, cfg.width, seed=cfg.seed)

    # Furnace actions/sensors and temperature setpoints/temps
    actions_df, sensors_df, setpoints, temps = simulate_furnace_and_sensors(
        cfg.num_steps, cfg.fps, cfg.num_zones, cfg.num_thermocouples, cfg.gas_channels, seed=cfg.seed + 1
    )

    # Use average temperature to drive deformation fields
    temp_profile = temps.mean(axis=1)
    U, V, W = simulate_displacement_fields(cfg.num_steps, cfg.height, cfg.width, cfg.fps, temp_profile, seed=cfg.seed + 2)

    # Strain fields
    exx, eyy, exy, prin1, prin2 = compute_strain_fields(U, V)

    # Density and metrics + reward
    density = estimate_density_over_time(temps, cfg.fps)
    metrics_df, reward = compute_rl_metrics_and_reward(U, V, W, exx, eyy, exy, prin1, density, cfg.weights, cfg.fps)

    # RL tuples
    tuples_df = build_rl_tuples(metrics_df, actions_df, sensors_df)

    # Save RL tuples
    tuples_df.to_parquet(rl_parquet, index=False)

    # Save furnace CSVs
    actions_df.to_csv(actions_csv, index=False)
    sensors_df.to_csv(sensors_csv, index=False)

    # Save DIC downsampled fields to keep size reasonable
    ds = max(1, int(cfg.downsample_fields_by))
    U_ds = U[:, ::ds, ::ds]
    V_ds = V[:, ::ds, ::ds]
    W_ds = W[:, ::ds, ::ds]
    exx_ds = exx[:, ::ds, ::ds]
    eyy_ds = eyy[:, ::ds, ::ds]
    exy_ds = exy[:, ::ds, ::ds]
    prin1_ds = prin1[:, ::ds, ::ds]
    prin2_ds = prin2[:, ::ds, ::ds]
    np.savez_compressed(
        fields_path,
        U=U_ds, V=V_ds, W=W_ds, exx=exx_ds, eyy=eyy_ds, exy=exy_ds, prin1=prin1_ds, prin2=prin2_ds
    )

    # Save DIC metrics CSV (subset of metrics_df)
    metrics_df.to_csv(metrics_csv, index=False)

    # Render camera videos
    timestamps = (np.arange(cfg.num_steps) / float(cfg.fps)).tolist()
    cameras_info = []
    for cam in cfg.cameras:
        cam_dir = os.path.join(frames_root, cam.camera_id)
        cam_params_json = os.path.join(run_dir, f"camera_{cam.camera_id}.json")
        with open(cam_params_json, "w") as f:
            json.dump(asdict(cam), f, indent=2)

        frames: List[np.ndarray] = []
        for t_idx in range(cfg.num_steps):
            frame = render_frame_from_fields(base_speckle, U[t_idx], V[t_idx], W[t_idx], cam)
            frames.append(frame)

        video_path = os.path.join(videos_root, f"cam_{cam.camera_id}.mp4")
        write_video(frames, video_path, cfg.fps, cfg.video_codec)

        if cfg.save_frames:
            save_frames(frames, cam_dir, prefix=f"cam_{cam.camera_id}")

        cameras_info.append({
            "id": cam.camera_id,
            "video_path": os.path.relpath(video_path, run_dir),
            "frames_dir": os.path.relpath(cam_dir, run_dir),
            "camera_params_json": os.path.relpath(cam_params_json, run_dir),
        })

    # Manifest
    manifest = {
        "run_id": cfg.run_id,
        "split": cfg.split,
        "num_steps": cfg.num_steps,
        "fps": cfg.fps,
        "dic": {
            "timestamps": timestamps,
            "fields_downsampled_npz": os.path.relpath(fields_path, run_dir),
            "metrics_csv": os.path.relpath(metrics_csv, run_dir),
            "cameras": cameras_info,
        },
        "furnace": {
            "actions_csv": os.path.relpath(actions_csv, run_dir),
            "sensors_csv": os.path.relpath(sensors_csv, run_dir),
            "timestamps": timestamps,
        },
        "rl": {
            "tuples_parquet": os.path.relpath(rl_parquet, run_dir),
            "state_columns": [
                "max_principal_strain", "strain_std", "curvature_metric", "warpage", "warpage_rate", "density",
                "temp_tc_1", "temp_tc_2", "temp_tc_3", "temp_tc_4", "time_s"
            ],
            "action_columns": [c for c in tuples_df.columns if c.startswith("power_delta_zone_") or c.startswith("setpoint_delta_zone_")],
            "reward_column": "reward",
            "metadata": {
                "weights": cfg.weights,
            }
        }
    }

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    return manifest


def package_runs(base_dir: str, out_dir: str, archive_name: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    # Create a zip archive of the entire runs directory
    runs_dir = os.path.join(base_dir, "runs")
    archive_path = os.path.join(out_dir, f"{archive_name}.zip")
    if os.path.exists(archive_path):
        os.remove(archive_path)
    shutil.make_archive(archive_path[:-4], 'zip', runs_dir)
    return archive_path


# -----------------------------
# CLI
# -----------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic Phase 2 dataset (DIC + Furnace + RL tuples)")
    parser.add_argument("--base-dir", default=os.path.join(os.getcwd(), ".."), help="Project base directory (phase2_dataset)")
    parser.add_argument("--runs-out", default="runs", help="Subdirectory for runs")
    parser.add_argument("--split-train", type=int, default=3, help="Number of train runs")
    parser.add_argument("--split-val", type=int, default=1, help="Number of val runs")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--num-steps", type=int, default=300, help="Frames/time-steps per run")
    parser.add_argument("--height", type=int, default=256)
    parser.add_argument("--width", type=int, default=256)
    parser.add_argument("--downsample", type=int, default=2)
    parser.add_argument("--zones", type=int, default=3)
    parser.add_argument("--tcs", type=int, default=6)
    parser.add_argument("--save-frames", action="store_true")
    parser.add_argument("--codec", default="libx264")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--w1", type=float, default=1.0)
    parser.add_argument("--w2", type=float, default=5.0)
    parser.add_argument("--w3", type=float, default=20.0)

    args = parser.parse_args()

    base_dir = args.base_dir
    if not os.path.isdir(base_dir):
        raise FileNotFoundError(f"Base directory not found: {base_dir}")

    runs_dir = os.path.join(base_dir, args.runs_out)
    os.makedirs(runs_dir, exist_ok=True)

    rng = np.random.default_rng(args.seed)

    cams = (
        CameraConfig(camera_id="A", fx=800.0, fy=800.0, cx=args.width / 2, cy=args.height / 2, yaw_deg=8.0, pitch_deg=0.0, baseline_mm=50.0),
        CameraConfig(camera_id="B", fx=820.0, fy=820.0, cx=args.width / 2, cy=args.height / 2, yaw_deg=-8.0, pitch_deg=3.0, baseline_mm=70.0),
    )

    # Shared gas channel names
    gas_channels = ("O2_ppm", "H2_percent", "Ar_percent")

    all_manifests: List[Dict] = []

    def create_cfg(split: str, run_seed: int) -> RunConfig:
        return RunConfig(
            run_id=random_run_id(prefix=f"{split}"),
            split=split,
            seed=run_seed,
            fps=args.fps,
            num_steps=args.num_steps,
            height=args.height,
            width=args.width,
            downsample_fields_by=args.downsample,
            num_zones=args.zones,
            num_thermocouples=args.tcs,
            gas_channels=gas_channels,
            weights=(args.w1, args.w2, args.w3),
            save_frames=args.save_frames,
            video_codec=args.codec,
            cameras=cams,
        )

    # Generate train runs
    for i in range(args.split_train):
        cfg = create_cfg("train", int(rng.integers(0, 1_000_000)))
        manifest = generate_one_run(base_dir=runs_dir, cfg=cfg)
        all_manifests.append(manifest)

    # Generate val runs
    for i in range(args.split_val):
        cfg = create_cfg("val", int(rng.integers(0, 1_000_000)))
        manifest = generate_one_run(base_dir=runs_dir, cfg=cfg)
        all_manifests.append(manifest)

    # Save index of runs
    index_path = os.path.join(runs_dir, "index.json")
    with open(index_path, "w") as f:
        json.dump({"runs": all_manifests}, f, indent=2)

    # Package zip
    packaged_dir = os.path.join(base_dir, "packaged")
    archive_name = f"phase2_dataset_{time.strftime('%Y%m%d_%H%M%S')}"
    archive_path = package_runs(base_dir, packaged_dir, archive_name)

    print(json.dumps({
        "message": "Generation complete",
        "index_json": os.path.relpath(index_path, base_dir),
        "archive_zip": os.path.relpath(archive_path, base_dir),
        "num_runs": len(all_manifests)
    }, indent=2))


if __name__ == "__main__":
    main()
