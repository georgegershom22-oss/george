# SOFC Low-Fidelity (LF) Dataset Generator

This project generates a synthetic low-fidelity (LF) dataset for Solid Oxide Fuel Cell (SOFC) stack simulations, approximating a 1D lumped electrochemical model. It produces 10,200 samples with V-I curves, stack temperature, and electrochemical efficiency, emulating a parametric sweep similar to COMSOL.

## Outputs
- Per-sample CSV of the V-I curve (voltage vs current density)
- Master CSV of inputs and scalar outputs: T_stack and eta_elec

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/generate_dataset.py --num-samples 10200 --out-dir data/lf
```

## Notes
- This is a computationally light surrogate; it is not a physics solver.
- For real COMSOL-based generation, replace the surrogate `sofc_surrogate.py` with solver-coupled code.
