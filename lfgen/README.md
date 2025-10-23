# Low-Fidelity SOFC Dataset Generator

This module generates a synthetic low-fidelity (LF) dataset for SOFC stacks using a fast 1D lumped surrogate model. It approximates COMSOL-style outputs for large-scale data generation.

Outputs per sample:
- V–I curve CSV (`curves/sample_XXXXXX.csv`)
- Stack temperature estimate (`T_stack_K` in manifest)
- Electrical efficiency estimate (`eta_elec` in manifest)

Usage:

```bash
python -m lfgen generate --num-samples 100 --output-dir /workspace/data/lf
```

Artifacts:
- `manifest.csv`: per-sample parameters and summary outputs
- `curves/*.csv`: V–I curves
- `meta.json`: dataset metadata
