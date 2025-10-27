# Synthetic Welding Parameters Dataset Generator

This project generates a comprehensive synthetic dataset for ML-driven inverse design of welding parameters.

- Techniques: ultrasonic, laser, resistance spot
- Materials: Cu, Al, Ni, SS304, SS316, CuNi
- Outputs: CSV, Parquet, metadata JSON, schema JSON

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
python scripts/generate_welding_dataset.py --rows 20000 --seed 123
```

Artifacts will be written to `artifacts/`.
