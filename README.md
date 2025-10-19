# Abaqus Acoustic Transmission Loss Simulation Suite

A comprehensive suite for simulating acoustic transmission loss in stratified marine environments using Abaqus. This implementation covers both layered and continuous gradient stratification cases with full automation from model creation to post-processing.

## Overview

This simulation suite implements the complete workflow described in your specifications:

- **Linear acoustics** in quiescent media using Helmholtz equation
- **Layered or continuous stratification** with varying density (ρ) and bulk modulus (K)
- **Harmonic frequency sweeps** using Steady-State Dynamics, Direct
- **Incident wave loading** with proper plane wave implementation
- **Non-reflecting boundaries** using acoustic impedance conditions
- **Automated post-processing** for transmission loss (TL) and attenuation coefficient (α)

## Files Included

### Input Files
- `acoustic_transmission_loss_layered.inp` - Complete Abaqus input file for layered stratification
- `acoustic_transmission_loss_gradient.inp` - Complete Abaqus input file for continuous gradient

### Python Scripts
- `create_acoustic_model.py` - Abaqus/CAE script for automated model creation
- `acoustic_postprocess.py` - Post-processing script for TL and α calculations
- `run_simulation.py` - Master script for complete workflow automation
- `material_properties.py` - Utility for generating material property tables

### Documentation
- `README.md` - This comprehensive guide
- `THEORY.md` - Theoretical background and equations
- `EXAMPLES.md` - Example use cases and parameter studies

## Quick Start

### Method 1: Using Pre-built Input Files

```bash
# Submit layered model
abaqus job=acoustic_layered input=acoustic_transmission_loss_layered.inp

# Submit gradient model  
abaqus job=acoustic_gradient input=acoustic_transmission_loss_gradient.inp

# Post-process results
abaqus python acoustic_postprocess.py acoustic_layered.odb 190.0
abaqus python acoustic_postprocess.py acoustic_gradient.odb 190.0
```

### Method 2: Using CAE Automation

```bash
# Create models in Abaqus/CAE
abaqus cae -noGUI create_acoustic_model.py

# Or run interactively in CAE
# execfile('create_acoustic_model.py')
```

### Method 3: Complete Automation

```bash
# Run complete workflow
python run_simulation.py --layered --gradient --frequency-range 100 5000 25
```

## Model Parameters

### Geometry
- **Length**: 200 m (waveguide length)
- **Width**: 10 m (waveguide width)
- **Element size**: ~2 m (λ/10 at 750 Hz in water)

### Frequency Range
- **Start**: 100 Hz
- **End**: 5000 Hz  
- **Increment**: 25 Hz
- **Total points**: 197 frequencies

### Material Properties

#### Layered Stratification
| Layer | Depth (m) | Density (kg/m³) | Bulk Modulus (Pa) | Sound Speed (m/s) |
|-------|-----------|-----------------|-------------------|-------------------|
| 1     | 0-50      | 1000           | 2.20×10⁹         | 1483             |
| 2     | 50-100    | 1015           | 2.25×10⁹         | 1489             |
| 3     | 100-150   | 1025           | 2.30×10⁹         | 1497             |
| 4     | 150-200   | 1030           | 2.32×10⁹         | 1500             |

#### Continuous Gradient
- **Density**: ρ(z) = 1000 + 0.15z kg/m³
- **Bulk Modulus**: K(z) = 2.2×10⁹ + 600000z Pa
- **Sound Speed**: c(z) = √(K(z)/ρ(z)) m/s

### Boundary Conditions
- **Inlet**: Incident plane wave (unit amplitude, y-direction)
- **Outlet**: Non-reflecting (Sommerfeld radiation condition)
- **Sides**: Non-reflecting (lateral boundaries)

### Probe Locations
- **Input probe**: 25 m from inlet
- **Output probe**: 25 m from outlet
- **Separation**: 190 m (for TL calculation)

## Theoretical Background

### Governing Equations

The simulation solves the Helmholtz equation for acoustic pressure:
```
∇²p + k²p = 0
```

Where:
- p = complex acoustic pressure
- k = ω/c = wavenumber
- ω = 2πf = angular frequency
- c = √(K/ρ) = sound speed

### Transmission Loss Calculation

Transmission Loss (TL) in dB:
```
TL(f) = 20 log₁₀(|p_in(f)|/|p_out(f)|)
```

Attenuation coefficient (amplitude-based):
```
α(f) = (ln(10)/20) × TL(f) / Δx
```

Where Δx is the probe separation distance.

### Stratification Effects

#### Layered Media
- **Impedance contrasts** at layer boundaries cause reflections
- **Refraction** occurs due to sound speed changes
- **Modal effects** from waveguide geometry

#### Continuous Gradients
- **Smooth refraction** without discrete reflections
- **Ray bending** following Snell's law in continuously varying media
- **Turning points** where rays reflect due to sound speed gradients

## Element Types and Meshing

### Acoustic Elements
- **2D**: AC2D4 (4-node quadrilateral)
- **Alternative**: AC2D3 (3-node triangle) for complex geometries

### Mesh Requirements
- **Resolution**: ≥10 elements per wavelength
- **At 5000 Hz**: λ_min ≈ 0.3 m → element size ≤ 0.03 m
- **Current mesh**: 2 m elements suitable for frequencies up to ~750 Hz
- **For higher frequencies**: Reduce element size proportionally

### Mesh Refinement Guidelines
```python
# Calculate required element size
f_max = 5000  # Hz
c_min = 1483  # m/s (minimum sound speed)
lambda_min = c_min / f_max  # minimum wavelength
element_size_max = lambda_min / 10  # elements per wavelength
```

## Abaqus Implementation Details

### Material Definition
```
*MATERIAL, NAME=WATER_LAYER
*DENSITY
1025.,
*BULK MODULUS  
2.306e9,
```

### Incident Wave Loading
```
*INCIDENT WAVE INTERACTION PROPERTY, NAME=PLANEWAVE
*INCIDENT WAVE FLUID PROPERTY
1025., 1500.
*INCIDENT WAVE INTERACTION, NAME=INC1, PROPERTY=PLANEWAVE
SURF_INLET, 0., 1., 0.
```

### Non-Reflecting Boundaries
```
*IMPEDANCE, TYPE=NONREFLECTING
SURF_OUTLET,
SURF_LEFT,
SURF_RIGHT,
```

### Field Variable Implementation (Gradient Case)
```
*MATERIAL, NAME=WATER_GRADIENT
*DENSITY, DEPENDENCIES=1
1000.,     0.
1030.,   200.
*BULK MODULUS, DEPENDENCIES=1
2.2e9,     0.
2.32e9,  200.
```

## Post-Processing

### Automatic Processing
The `acoustic_postprocess.py` script automatically:
1. Extracts complex pressure data from probe locations
2. Calculates pressure magnitudes and phases
3. Computes transmission loss TL(f)
4. Calculates attenuation coefficient α(f)
5. Generates plots and exports CSV data

### Manual Processing in Abaqus/Viewer
1. **Create XY Data** → **ODB field output** → **Pressure magnitude**
2. **Select probe node sets** (PROBE_IN, PROBE_OUT)
3. **Operate** → **Average** over probe nodes
4. **Combine** data to calculate TL = 20*log10(P_in/P_out)

### Output Files
- `acoustic_results.csv` - Tabulated TL and α data
- `acoustic_transmission_loss.png` - Comprehensive plots
- Console summary with statistics

## Validation and Quality Assurance

### Mesh Convergence
```bash
# Test different element sizes
python run_simulation.py --element-size 4.0  # coarse
python run_simulation.py --element-size 2.0  # medium  
python run_simulation.py --element-size 1.0  # fine
```

### Boundary Effects
- Move probe locations to test boundary influence
- Results should be invariant if boundaries are truly non-reflecting
- Keep probes ≥0.5λ from boundaries

### Physical Consistency
- Verify c = √(K/ρ) for all materials
- Check impedance matching at interfaces
- Validate frequency-dependent behavior

## Common Issues and Solutions

### Convergence Problems
- **Symptom**: Job fails with convergence errors
- **Solution**: Check material properties, reduce frequency increment

### Mesh Quality
- **Symptom**: Oscillatory or non-physical results
- **Solution**: Refine mesh, check element aspect ratios

### Boundary Reflections
- **Symptom**: Standing wave patterns, non-monotonic TL
- **Solution**: Move boundaries farther, verify impedance conditions

### Memory Issues
- **Symptom**: Out of memory errors for large frequency ranges
- **Solution**: Reduce frequency range, use frequency subsets

## Advanced Usage

### Custom Material Properties
Edit the layer properties in `create_acoustic_model.py`:
```python
self.layer_properties = [
    {'depth_range': (0, 50), 'density': 1000.0, 'bulk_modulus': 2.2e9},
    {'depth_range': (50, 100), 'density': 1015.0, 'bulk_modulus': 2.25e9},
    # Add more layers as needed
]
```

### Frequency-Dependent Materials
Implement dispersion using frequency-dependent tables:
```
*BULK MODULUS, FREQUENCY
2.2e9,   100.
2.25e9, 1000.
2.3e9,  5000.
```

### 3D Extensions
Modify for 3D simulations:
- Change to AC3D8 elements
- Add z-dimension to geometry
- Consider computational cost (scales as N³)

## Performance Optimization

### Parallel Processing
```bash
# Use multiple CPUs
abaqus job=acoustic_model cpus=8 mp_mode=threads
```

### Memory Management
```bash
# Increase memory allocation
abaqus job=acoustic_model memory="8gb"
```

### Frequency Batching
For large frequency ranges, split into batches:
```python
# Process 100-1000 Hz first
# Then 1000-5000 Hz separately
# Combine results in post-processing
```

## References and Documentation

### Abaqus Documentation
- **Acoustic Elements**: Section 29.2.1
- **Steady-State Dynamics**: Section 6.3.6
- **Incident Wave Loading**: Section 34.4.1
- **Acoustic Impedance**: Section 34.2.1

### Theoretical References
- Jensen, F.B., et al. "Computational Ocean Acoustics" (2011)
- Pierce, A.D. "Acoustics: An Introduction to Its Physical Principles" (1989)
- Medwin, H. & Clay, C.S. "Fundamentals of Acoustical Oceanography" (1998)

## Support and Troubleshooting

### Log Files
Check these files for diagnostics:
- `job_name.log` - General job information
- `job_name.msg` - Detailed messages and warnings
- `job_name.dat` - Input echo and element information
- `job_name.sta` - Status and convergence information

### Common Error Messages
- **"Acoustic medium requires density and bulk modulus"**
  - Solution: Verify both properties are defined for all materials

- **"Incident wave direction not normalized"**
  - Solution: Ensure direction vector has unit magnitude

- **"Non-reflecting boundary failed"**
  - Solution: Check surface definitions and orientations

### Getting Help
1. Check Abaqus documentation for acoustic procedures
2. Verify input file syntax against examples
3. Test with simplified geometry first
4. Use Abaqus/CAE to validate model setup

## License and Citation

This simulation suite is provided for educational and research purposes. When using this code in publications, please cite:

```
Abaqus Acoustic Transmission Loss Simulation Suite
Generated for marine acoustic propagation studies
Based on Abaqus finite element acoustic procedures
```

---

*Last updated: 2024*
*Compatible with: Abaqus 2020 and later*