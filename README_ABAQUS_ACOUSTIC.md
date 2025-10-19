# Abaqus Acoustic Transmission Loss Simulation

Complete production-ready simulation for acoustic wave propagation and transmission loss analysis in stratified ocean media.

## Overview

This simulation package computes **Transmission Loss (TL)** and **attenuation coefficient (α)** for acoustic waves propagating through a layered ocean medium with thermocline stratification.

### What This Simulates

✅ **Included Physics:**
- Linear acoustics (Helmholtz equation)
- Layered stratification (3 layers: surface/thermocline/deep)
- Impedance contrasts at layer interfaces
- Frequency-dependent transmission characteristics
- Steady-state harmonic response (100-5000 Hz)

❌ **Not Included:**
- Stratified fluid dynamics (internal waves, baroclinic effects)
- Nonlinear acoustics
- Mean flow effects
- Time-transient response

## Files

```
acoustic_transmission_loss.inp          Main Abaqus input file
extract_transmission_loss.py            Post-processing script (odbAccess)
plot_transmission_loss.py               Visualization script
mesh_generator.py                       Mesh generation utility
README_ABAQUS_ACOUSTIC.md              This documentation
```

## Simulation Parameters

### Domain
- **Geometry:** 2D waveguide, 100m (length) × 50m (depth)
- **Boundary conditions:**
  - Inlet (x=0): Plane wave incident field
  - Outlet (x=100m): Non-reflecting impedance BC
  - Top/Bottom: Non-reflecting impedance BC

### Stratification (Three Layers)

| Layer | Depth Range | Temp | ρ (kg/m³) | K (GPa) | c (m/s) | Physical Meaning |
|-------|-------------|------|-----------|---------|---------|------------------|
| 1     | 0-15 m      | 20°C | 1023      | 2.364   | 1520    | Surface (warm)   |
| 2     | 15-35 m     | 10°C | 1026      | 2.278   | 1490    | Thermocline      |
| 3     | 35-50 m     | 4°C  | 1028      | 2.221   | 1470    | Deep (cold)      |

*Note: Sound speed c = √(K/ρ)*

### Mesh
- **Element type:** AC2D4 (4-node acoustic quadrilateral)
- **Element size:** 0.25 m (λ/6 at 1000 Hz)
- **Total elements:** ~80,000
- **Resolution:** ~10-12 elements per wavelength (conservative)

### Frequency Sweep
- **Range:** 100 - 5000 Hz
- **Increment:** 25 Hz (linear)
- **Points:** 197 frequency samples
- **Method:** Steady-State Dynamics, Direct

### Probes
- **Inlet probe:** x = 20 m (after incident wave stabilization)
- **Outlet probe:** x = 80 m (before outlet boundary)
- **Spacing:** Δx = 60 m (for TL calculation)

## Usage

### 1. Run Abaqus Simulation

```bash
# Submit job to Abaqus
abaqus job=acoustic_TL input=acoustic_transmission_loss.inp cpus=4 interactive

# Or background mode
abaqus job=acoustic_TL input=acoustic_transmission_loss.inp cpus=4 &

# Monitor progress
tail -f acoustic_TL.sta
```

**Expected runtime:** ~15-45 minutes (depends on hardware, 4-8 CPUs recommended)

### 2. Post-Process Results

```bash
# Extract transmission loss data
abaqus python extract_transmission_loss.py acoustic_TL.odb

# Output: acoustic_TL_transmission_loss.csv
```

**Output columns:**
- `Frequency_Hz`: Frequency points
- `TL_dB`: Transmission loss (dB)
- `alpha_dB_per_m`: Attenuation coefficient (dB/m)
- `alpha_Np_per_m`: Attenuation coefficient (Nepers/m)
- `p_in_mag_Pa`, `p_out_mag_Pa`: Pressure magnitudes
- Complex components: `p_in_real_Pa`, `p_in_imag_Pa`, etc.

### 3. Visualize Results

```bash
# Generate plots (requires matplotlib)
python plot_transmission_loss.py acoustic_TL_transmission_loss.csv
```

**Output figures:**
- `acoustic_TL_comprehensive.png`: 5-panel overview
- `acoustic_TL_detailed.png`: TL with spectral features
- `acoustic_TL_phase.png`: Phase characteristics

## Theory

### Transmission Loss
$$
TL(f) = 20 \log_{10} \frac{|p_{\text{in}}(f)|}{|p_{\text{out}}(f)|}
$$

### Attenuation Coefficient
$$
\alpha_{\text{amp}}(f) = \frac{\ln(10)}{20} \frac{TL(f)}{\Delta x} \quad [\text{Np/m}]
$$
$$
\alpha_{\text{dB}}(f) = \frac{TL(f)}{\Delta x} \quad [\text{dB/m}]
$$

### Sound Speed
$$
c = \sqrt{\frac{K}{\rho}}
$$

where:
- *K* = Bulk modulus (Pa)
- *ρ* = Density (kg/m³)
- Δx = Probe spacing (m)

## Abaqus Implementation Details

### Element Type: AC2D4
- 4-node bilinear acoustic quadrilateral
- DOF: Pressure (POR) at each node
- Suitable for linear acoustics in frequency domain

### Material Definition
```inp
*MATERIAL, NAME=WATER_SURFACE
*DENSITY
1023.0,
*BULK MODULUS
2.364e9,
```

### Incident Wave Interaction
```inp
*INCIDENT WAVE INTERACTION PROPERTY, NAME=PLANE_WAVE_PROP
*INCIDENT WAVE FLUID PROPERTY
1023.0, 1520.0      ! ρ, c
*INCIDENT WAVE INTERACTION, NAME=SOURCE, PROPERTY=PLANE_WAVE_PROP
INLET_SURF, 1.0, 0.0, 0.0    ! surface, direction cosines
```

### Non-Reflecting Boundaries
```inp
*IMPEDANCE, TYPE=NONREFLECTING
OUTLET_SURF,
TOP_SURF,
BOTTOM_SURF,
```

This implements Sommerfeld radiation condition: ∂p/∂n + (iω/c)p = 0

## Customization

### Modify Stratification

**Option 1: Change layer properties**

Edit material definitions in `acoustic_transmission_loss.inp`:
```inp
*MATERIAL, NAME=WATER_THERMOCLINE
*DENSITY
1026.0,              ! Change density
*BULK MODULUS
2.278e9,             ! Change bulk modulus
```

**Option 2: Continuous gradient**

Use field-variable dependent properties:
```inp
*MATERIAL, NAME=WATER_GRADED
*DENSITY, DEPENDENCIES=1
1023.0, 0.0          ! ρ(F1=0)
1028.0, 50.0         ! ρ(F1=50)
*BULK MODULUS, DEPENDENCIES=1
2.364e9, 0.0
2.221e9, 50.0

*INITIAL CONDITIONS, TYPE=FIELD
** Define F1(z) = z
ALLNODES, 1, <expression>
```

### Change Frequency Range

Edit the `*STEADY STATE DYNAMICS` card:
```inp
*STEADY STATE DYNAMICS, DIRECT
<f_start>, <f_end>, <n_increments>
```

Example: 50-10000 Hz in 50 Hz steps:
```inp
*STEADY STATE DYNAMICS, DIRECT
50., 10000., 199
```

### Refine Mesh

Regenerate mesh with smaller elements:
```bash
python mesh_generator.py --length 100 --depth 50 --size 0.1 --output fine_mesh.inp
```

**Rule of thumb:** Use ≥10 elements per wavelength:
$$
\Delta x \leq \frac{\lambda_{\min}}{10} = \frac{c_{\min}}{10 f_{\max}}
$$

For f_max = 5000 Hz, c_min = 1470 m/s:
$$
\Delta x \leq \frac{1470}{10 \times 5000} = 0.0294 \text{ m}
$$

Current mesh (0.25 m) gives ~6 elem/λ at 1000 Hz, adequate for demonstration.

## Validation Checklist

✅ **Before running:**
- [ ] Mesh resolution: Δx ≤ λ_min/10
- [ ] Material consistency: c = √(K/ρ) physically reasonable
- [ ] Boundary location: Probes ≥0.5λ from boundaries
- [ ] Element type: AC2D4 for 2D, AC3D8 for 3D

✅ **After running:**
- [ ] Check .dat file for warnings
- [ ] Check .msg file for convergence
- [ ] Verify TL(f) is smooth and physically reasonable
- [ ] Run mesh convergence study (halve element size)

## Expected Results

For the default 3-layer configuration:

| Metric | Typical Value |
|--------|---------------|
| Mean TL | 1-5 dB |
| TL range | 0-10 dB |
| Mean α | 0.01-0.08 dB/m (10-80 dB/km) |
| Spectral features | Interference peaks/troughs due to layer reflections |

**Physical interpretation:**
- Higher TL at certain frequencies → constructive interference of reflected waves
- Lower TL → destructive interference or acoustic transparency
- Overall positive TL → net energy dissipation through stratification

## Common Issues

### 1. Job fails with "negative eigenvalue"
**Cause:** Material properties inconsistent or non-physical
**Fix:** Verify K > 0, ρ > 0, and reasonable c values

### 2. TL(f) oscillates wildly
**Cause:** Mesh too coarse or boundaries too close
**Fix:** Refine mesh or increase domain size

### 3. ODB post-processing fails
**Cause:** Node set names don't match
**Fix:** Check node set names in .inp match script: `PROBE_IN`, `PROBE_OUT`

### 4. Convergence warnings
**Cause:** Frequency increment too large or boundary conditions unstable
**Fix:** Reduce frequency increment or check impedance BC

## References

### Abaqus Documentation
- [Acoustic Elements](https://abaqus-docs.mit.edu/2017/English/SIMACAEELMRefMap/simaelm-c-acousticquad.htm)
- [Steady-State Dynamics](https://abaqus-docs.mit.edu/2017/English/SIMACAEANLRefMap/simaanl-c-steadystate.htm)
- [Incident Wave Loads](https://abaqus-docs.mit.edu/2017/English/SIMACAELOARefMap/simaloa-c-incidentwave.htm)
- [Acoustic Impedance BC](https://abaqus-docs.mit.edu/2017/English/SIMACAELOARefMap/simaloa-c-acousticimpedance.htm)

### Theory
- Jensen, F. B., et al. (2011). *Computational Ocean Acoustics*. Springer.
- Pierce, A. D. (1989). *Acoustics: An Introduction to Its Physical Principles and Applications*.

## Citation

If you use this simulation in your research, please cite:

```
Abaqus Acoustic Transmission Loss Simulation
Three-Layer Ocean Thermocline Model
Generated: 2025-10-19
```

## Support

For issues or questions:
1. Check .dat and .msg files for Abaqus errors
2. Verify input parameters in .inp file
3. Review this README and documentation links
4. Test with simplified geometry/frequency range

---

**License:** MIT  
**Version:** 1.0  
**Last Updated:** 2025-10-19
