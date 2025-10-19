# Quick Reference Guide - Abaqus Acoustic TL Analysis

## Essential Commands

### 1. Run Pre-Built Models
```bash
# Layered stratification (2D)
abaqus job=layered_2d input=input_files/acoustic_layered_2d.inp cpus=4

# Gradient stratification (2D)  
abaqus job=gradient_2d input=input_files/acoustic_gradient_2d.inp cpus=4

# 3D example
abaqus job=acoustic_3d input=input_files/acoustic_3d_example.inp cpus=8
```

### 2. Generate Custom Models
```python
# In Abaqus CAE Python console:
execfile('scripts/acoustic_model_generator.py')
model = AcousticStratifiedModel('MyModel')
job = model.build_layered_model(n_layers=5, dimension='2D')
job.submit()
```

### 3. Extract Results
```bash
# Basic TL extraction
abaqus python post_processing/extract_tl_alpha.py job.odb 6.0

# With visualization
abaqus python post_processing/visualize_acoustic_field.py job.odb 1000
```

## Key Input File Sections

### Material Definition (Layered)
```
*MATERIAL, NAME=WATER_LAYER1
*DENSITY
1000.0,
*ACOUSTIC MEDIUM
2.15E+09, 1000.0
```

### Material with Field Variables (Gradient)
```
*MATERIAL, NAME=WATER_GRADIENT
*DENSITY, DEPENDENCIES=1
950.0, 0.0   # (density, field_variable)
1050.0, 1.0
*ACOUSTIC MEDIUM, DEPENDENCIES=1
2.0E+09, 950.0, 0.0   # (K, rho, field_variable)
2.2E+09, 1050.0, 1.0
```

### Incident Wave
```
*INCIDENT WAVE INTERACTION PROPERTY, NAME=PLANE_WAVE, DEFINITION=PLANAR
*INCIDENT WAVE FLUID PROPERTY
1000.0, 1500.0  # density, sound_speed
1.0, 0.0, 100.0  # magnitude, angle, ref_frequency
```

### Non-Reflecting Boundaries
```
*IMPEDANCE, TYPE=NONREFLECTING
OUTLET, 1.0
```

### Frequency Sweep
```
*STEADY STATE DYNAMICS, DIRECT
100.0, 5000.0, 25.0, 1.0  # start, end, increment, bias
```

## Element Types

| Dimension | Element | Nodes | Order | Use Case |
|-----------|---------|-------|-------|----------|
| 2D | AC2D4 | 4 | Linear | Standard 2D |
| 2D | AC2D8 | 8 | Quadratic | High accuracy |
| 3D | AC3D8 | 8 | Linear | Standard 3D |
| 3D | AC3D20 | 20 | Quadratic | High accuracy |

## Mesh Guidelines

- **Minimum**: 10-12 elements per wavelength
- **Element size**: `h < λ_min / 10 = c_min / (10 × f_max)`
- **Example**: For f_max=5000 Hz, c=1500 m/s → h < 0.03 m

## Common Material Properties

| Medium | Density (kg/m³) | Bulk Modulus (Pa) | Sound Speed (m/s) |
|--------|----------------|-------------------|-------------------|
| Air (20°C) | 1.2 | 1.42×10⁵ | 343 |
| Fresh Water | 1000 | 2.15×10⁹ | 1465 |
| Seawater | 1025 | 2.31×10⁹ | 1500 |
| Warm Surface | 950 | 2.00×10⁹ | 1450 |
| Cold Deep | 1050 | 2.20×10⁹ | 1445 |

## Troubleshooting Quick Fixes

### High/Unexpected TL
```bash
# Check probe separation distance
grep "PROBE" input_file.inp
# Verify it matches post-processing parameter
```

### No Pressure Output
```
# Add to step definition:
*OUTPUT, FIELD
*NODE OUTPUT
P, POR
```

### Memory Issues
```bash
# Use domain decomposition
abaqus job=myjob cpus=8 parallel=domain

# Or reduce output frequency
*OUTPUT, FIELD, FREQUENCY=10
```

### Convergence Issues
```python
# Check material properties consistency
c_calculated = sqrt(K/rho)  # Should be ~1400-1600 m/s for water
```

## Post-Processing Formulas

**Transmission Loss:**
```
TL = 20 × log₁₀(|p_in| / |p_out|) [dB]
```

**Absorption Coefficient:**
```
α = (ln(10)/20) × TL / Δx [Np/m]
α_dB = 8.686 × α [dB/m]
```

**Phase Velocity:**
```
c_phase = λ × f = (2π/k) × f
where k = Δφ / Δx
```

## Performance Tips

1. **Frequency Points**: Use logarithmic spacing for wide bands
2. **Symmetry**: Use 2D models when possible (10x faster)
3. **Parallel**: Use all available CPUs
4. **Output**: Limit field output frequency for large models

## File Size Estimates

| Model Type | Elements | Frequencies | ODB Size |
|------------|----------|-------------|----------|
| 2D Small | 5,000 | 50 | ~50 MB |
| 2D Medium | 20,000 | 100 | ~400 MB |
| 2D Large | 100,000 | 200 | ~4 GB |
| 3D Small | 50,000 | 50 | ~2 GB |
| 3D Large | 500,000 | 100 | ~40 GB |

## Validation Checklist

- [ ] Mesh convergence (halve element size, check TL change < 2%)
- [ ] Domain size (probes > λ from boundaries)
- [ ] Impedance matching (incident wave properties = medium properties)
- [ ] Frequency resolution (smooth TL curves)
- [ ] Physical consistency (c = √(K/ρ) reasonable)
- [ ] Energy conservation (no artificial losses)

## Contact Support Commands

```bash
# Check Abaqus version and licenses
abaqus information=version
abaqus information=release
abaqus licensing lmstat -a

# Test acoustic element availability
abaqus findkeyword=AC2D4
abaqus findkeyword="ACOUSTIC MEDIUM"
```