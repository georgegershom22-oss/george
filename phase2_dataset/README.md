## Phase 2: Core Real-Time Training & Validation Data (Synthetic)

This project generates a high-fidelity synthetic dataset mimicking a real-time DIC and furnace control environment for RL training and Digital Twin validation.

Contents per run:
- Visual: Two-camera DIC-like videos (MP4) of a speckled surface undergoing deformation
- Fields: Downsampled full-field displacement (U,V,W) and strain (εxx, εyy, εxy) + principal strains
- Furnace: Time-synchronized actions (zone power and setpoint deltas) and sensors (thermocouples, gases)
- RL: State–action–reward–next_state tuples as Parquet
- Manifest: JSON indexed paths, timestamps, and schema references

### Quickstart

1) Install dependencies:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2) Generate dataset (3 train runs, 1 val run):
```bash
python scripts/generate_phase2_dataset.py --base-dir . --fps 30 --num-steps 300 --height 256 --width 256 --zones 3 --tcs 6 --downsample 2 --codec libx264
```

Add `--save-frames` to also export individual JPEG frames.

3) Outputs:
- Runs live under `runs/<split>/<run_id>/` with artifacts and `manifest.json`
- A top-level `runs/index.json` lists all generated runs
- A ZIP is created under `packaged/` for download, e.g. `packaged/phase2_dataset_*.zip`

### RL Tuple Definition
- State: `[max_principal_strain, strain_std, curvature_metric, warpage, warpage_rate, density, temp_tc_1..4, time_s]`
- Action: `power_delta_zone_*`, `setpoint_delta_zone_*`
- Reward: `- (w1*|warpage_rate| + w2*|max_strain| + w3*(target_density - density)^2)`
- Next-state: suffixed with `_next`; `done` is true on the last step

### Notes
- Cameras `A` and `B` have small yaw/pitch offsets to induce parallax-like motion from W.
- The displacement/strain fields are physics-inspired and smoothed for continuity.
- Temperatures follow a ramp/hold/ramp/hold/cooldown program with RL-like control perturbations.
