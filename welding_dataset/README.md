# Dataset for ML-Driven Inverse Design of Welding Parameters

This project generates a comprehensive, physics-inspired dataset for inverse design of welding parameters, spanning:

- Input Parameters (Design Space)
- Characterization & Quality Metrics (Forward Problem Outputs)
- Performance & Validation Metrics (Inverse Design Targets)

Includes scripts to generate synthetic data, optional fetchers for public welding datasets, schema definitions, and packaging utilities.

## Structure

- `src/` — dataset generator and utilities
- `data/` — generated data (raw, synthetic, processed, splits, artifacts)
- `scripts/` — CLI entry points
- `notebooks/` — exploration and demo notebooks

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_dataset.py --rows 100000 --seed 42
python scripts/package_dataset.py
```

Generated zip will appear in `data/artifacts/`.
