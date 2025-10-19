# Quick Reference Card - Abaqus Acoustic TL Simulation

## One-Command Workflow

```bash
# Automated (recommended for beginners)
./run_simulation.sh

# Manual (for experts)
abaqus cae noGUI=abaqus_acoustic_tl_simulation.py
abaqus job=acoustic_tl_job interactive
abaqus python postprocess_tl.py acoustic_tl_job
python plot_tl.py
```

## Essential Parameters

| Parameter | Typical Values | Units | Location in Script |
|-----------|---------------|-------|-------------------|
| `freq_start` | 50-200 | Hz | `AcousticConfig.__init__()` |
| `freq_end` | 2000-5000 | Hz | `AcousticConfig.__init__()` |
| `freq_inc` | 10-50 | Hz | `AcousticConfig.__init__()` |
| `length` | 50-200 | m | Propagation distance |
| `height` | 30-100 | m | Domain depth |
| `rho` | 1000-1030 | kg/m³ | Density |
| `K` | 2.2e9-2.4e9 | Pa | Bulk modulus |
| `probe_separation` | 40-100 | m | TL measurement baseline |

## Material Properties Quick Calculator

```python
# Given: density (rho) and sound speed (c)
# Calculate: bulk modulus (K)
K = rho * c**2

# Example: Seawater at 15°C
rho = 1025.0        # kg/m³
c = 1500.0          # m/s
K = 1025 * 1500**2  # = 2.30625e9 Pa
```

## Common Sound Speeds

| Medium | c (m/s) | ρ (kg/m³) | K (Pa) |
|--------|---------|----------|--------|
| Air (20°C) | 343 | 1.2 | 1.4×10⁵ |
| Fresh water (20°C) | 1482 | 998 | 2.19×10⁹ |
| Seawater (15°C, surface) | 1500 | 1025 | 2.31×10⁹ |
| Seawater (5°C, deep) | 1490 | 1028 | 2.28×10⁹ |
| Soft sediment | 1463 | 1400 | 3.00×10⁹ |
| Sand | 1700 | 2000 | 5.78×10⁹ |

## Mesh Size Calculator

```python
# Target: 10-12 elements per wavelength at highest frequency
c_min = min([sqrt(K/rho) for each layer])
lambda_min = c_min / freq_max
element_size = lambda_min / 12

# Example:
c_min = 1480 m/s
freq_max = 5000 Hz
lambda_min = 1480 / 5000 = 0.296 m
element_size ≤ 0.296 / 12 = 0.025 m
```

## Transmission Loss Formulas

```
# Measured TL (from simulation)
TL = 20·log₁₀(|p_in| / |p_out|)  [dB]

# Attenuation coefficient (amplitude-based)
α = 0.1151 · TL / Δx  [Np/m]
α = TL / Δx            [dB/m]

# Attenuation coefficient (intensity-based)
α = 0.2303 · TL / Δx  [Np/m]

# Conversion
1 Np/m = 8.686 dB/m
```

## Expected TL Ranges (Order of Magnitude)

| Scenario | TL over 100 m | Physical Mechanism |
|----------|--------------|-------------------|
| Homogeneous water | ~0 dB | No loss (ideal) |
| Weak gradient | 5-15 dB | Smooth refraction |
| Ocean thermocline | 10-30 dB | Sound channel, mode coupling |
| Strong layering | 30-60 dB | Multiple reflections |
| Water-sediment | 50-100 dB | Large impedance mismatch |

## File Output Reference

| File | Contents | Use |
|------|----------|-----|
| `*.cae` | Abaqus model database | Open in CAE GUI |
| `*.inp` | Input file (keywords) | Text-editable, direct submission |
| `*.odb` | Results database | Open in Viewer |
| `*.dat` | Analysis log | Check for errors/warnings |
| `*.msg` | Job messages | Monitor progress |
| `*.sta` | Status file | Check convergence |
| `transmission_loss.csv` | TL(f) and α(f) data | Import to Excel/Python |
| `transmission_loss_results.png` | Plots | Quick visualization |

## Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|----------|
| Job fails immediately | Check `.dat` file for errors; verify material properties K>0, ρ>0 |
| All pressures = 0 | Verify incident wave direction, check step type is SSD Direct |
| TL > 200 dB | Check probe locations (not on boundary), verify non-reflecting BCs |
| Mesh warnings | Reduce `freq_end` or increase `target_elements_per_wavelength` |
| Out of memory (3D) | Reduce domain size, coarsen mesh, or use fewer frequency points |
| Negative TL | Probes reversed or near constructive interference node |

## Element Types Cheat Sheet

```
# 2D Acoustics
AC2D4   - 4-node quad (linear)          ✓ Default, good for most cases
AC2D8   - 8-node quad (quadratic)       ⚠ Higher accuracy, more expensive

# 3D Acoustics  
AC3D8   - 8-node brick (linear)         ✓ Default for 3D
AC3D20  - 20-node brick (quadratic)     ⚠ High accuracy, very expensive

# Integration points
Linear elements:   1 point (AC2D4, AC3D8)
Quadratic elements: 4/8 points (AC2D8, AC3D20)
```

## Boundary Condition Keywords

```python
# Incident wave (excitation)
*INCIDENT WAVE INTERACTION PROPERTY, NAME=...
*INCIDENT WAVE FLUID PROPERTY
rho, c
*INCIDENT WAVE INTERACTION, NAME=..., PROPERTY=...
surface, dir_x, dir_y, dir_z, amplitude

# Non-reflecting (absorbing)
*IMPEDANCE, TYPE=NONREFLECTING
surface_name,

# Fixed pressure (hard wall)
*BOUNDARY
node_set, 8, 8, 0.0   # DOF 8 = pressure

# Free surface (soft boundary)
# (No BC needed - natural BC is ∂p/∂n = 0)
```

## Abaqus Commands Quick Reference

```bash
# Run model generation
abaqus cae noGUI=script.py

# Submit job (interactive = see output immediately)
abaqus job=jobname interactive

# Submit job (background)
abaqus job=jobname cpus=4

# Check job status
abaqus job=jobname status

# Kill running job
abaqus job=jobname kill

# Post-process with Python
abaqus python script.py

# Open viewer
abaqus viewer odb=file.odb

# Convert ODB to CSV (example)
abaqus python -c "from odbAccess import *; odb=openOdb('file.odb'); ..."

# Check license status
abaqus licensing lmstat -a
```

## Directory Structure (After Running)

```
workspace/
├── abaqus_acoustic_tl_simulation.py    [Model generator]
├── postprocess_tl.py                   [Post-processor]
├── acoustic_input_template.inp         [Keyword template]
├── run_simulation.sh                   [Automation script]
├── config_example_*.py                 [Example configs]
├── advanced_customization_guide.py     [Advanced topics]
├── README.md                           [Full documentation]
├── QUICK_REFERENCE.md                  [This file]
│
├── AcousticTL_Stratified.cae           [Generated model]
├── acoustic_tl_job.inp                 [Input file]
├── acoustic_tl_job.odb                 [Results]
├── acoustic_tl_job.dat                 [Analysis log]
├── acoustic_tl_job.msg                 [Messages]
├── acoustic_tl_job.sta                 [Status]
│
├── transmission_loss.csv               [TL data]
├── plot_tl.py                          [Plot script]
└── transmission_loss_results.png       [Plots]
```

## Performance Estimates

| Model Size | Elements | Frequencies | Time (approx) | Memory |
|------------|----------|-------------|---------------|--------|
| Small 2D | ~5,000 | 100 | 1-5 min | <1 GB |
| Medium 2D | ~20,000 | 200 | 10-30 min | 1-2 GB |
| Large 2D | ~100,000 | 200 | 1-3 hours | 2-4 GB |
| Small 3D | ~50,000 | 50 | 30 min-2 hrs | 2-4 GB |
| Medium 3D | ~200,000 | 100 | 3-8 hours | 4-8 GB |
| Large 3D | ~1,000,000 | 100 | 10-24 hours | 8-16 GB |

*Times are approximate and depend on CPU speed, number of cores, and model complexity*

## Quick Validation Checklist

- [ ] Sound speed c = √(K/ρ) is physically realistic (1400-2000 m/s for water)
- [ ] Mesh has >10 elements per wavelength at highest frequency
- [ ] Probes are >0.5λ away from boundaries
- [ ] All surfaces except inlet have non-reflecting BCs
- [ ] Incident wave direction matches inlet normal (e.g., (1,0,0) for x-normal)
- [ ] Job completed without errors (check `.dat` file)
- [ ] TL values are positive and physically reasonable
- [ ] TL increases with frequency (typical for lossy media)

## Contact and Support

**Documentation**: See `README.md` for full details  
**Examples**: `config_example_*.py` files  
**Advanced**: `advanced_customization_guide.py`  
**Abaqus Docs**: https://abaqus-docs.mit.edu  

---

*Last updated: 2025-10-19*
