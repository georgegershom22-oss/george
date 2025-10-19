# Abaqus Acoustic Transmission Loss Simulation

**Complete Python implementation for acoustic propagation in stratified media**

## Overview

This package provides a comprehensive Abaqus-based simulation framework for computing **Transmission Loss (TL)** and **attenuation coefficient (α)** in vertically stratified acoustic media. It handles:

- ✅ **Layered stratification** (constant properties per layer)
- ✅ **Continuously graded** density and bulk modulus profiles
- ✅ **2D and 3D** acoustic domains
- ✅ **Harmonic frequency sweeps** (Steady-State Dynamics, Direct)
- ✅ **Incident plane wave** excitation
- ✅ **Non-reflecting boundaries** (impedance boundaries)
- ✅ **Automated post-processing** with TL(f) and α(f) extraction

## What Abaqus Simulates Here

### ✅ **WILL Simulate**

- Linear acoustics in quiescent media (Helmholtz equation)
- Layered or smoothly varying ρ (density) and K (bulk modulus)
- Scattering at impedance contrasts
- Acoustic-structure coupling (if walls/liners added)
- Frequency-dependent material properties

### ❌ **WON'T Simulate**

- Stratified fluid dynamics (internal waves, baroclinic vorticity)
- Mean flow effects
- Turbulence or nonlinear acoustics
- Time-domain transient analysis (this uses frequency-domain)

> **Note**: Abaqus measures the **net acoustic effect** of stratification. Complex fluid dynamics (internal waves, etc.) require separate CFD/PE modeling; their acoustic signature is captured here via the TL beyond classical losses.

---

## Files in This Package

| File | Description |
|------|-------------|
| `abaqus_acoustic_tl_simulation.py` | **Main model generator** - Creates complete Abaqus model via Python API |
| `postprocess_tl.py` | **Post-processor** - Extracts TL(f) and α(f) from ODB file |
| `acoustic_input_template.inp` | **Input file template** - Direct keyword approach with annotations |
| `config_example_ocean_thermocline.py` | Example: ocean thermocline with sound channel |
| `config_example_sediment_layers.py` | Example: water-sediment layers with strong impedance contrasts |
| `config_example_graded_profile.py` | Example: continuously graded medium |
| `config_example_3d_waveguide.py` | Example: 3D waveguide simulation |
| `README.md` | This file |

---

## Quick Start

### Prerequisites

- **Abaqus/CAE** (version 6.14 or later recommended)
- **Python 2.7** (Abaqus built-in Python) or Python 3.x for post-processing
- **NumPy** (for post-processing)
- **Matplotlib** (optional, for visualization)

### Workflow

```bash
# 1. Generate Abaqus model
abaqus cae noGUI=abaqus_acoustic_tl_simulation.py

# 2. Run simulation (interactive mode for testing, or submit via Job Manager)
abaqus job=acoustic_tl_job interactive

# 3. Post-process results
abaqus python postprocess_tl.py acoustic_tl_job

# 4. Visualize (requires matplotlib)
python plot_tl.py
```

---

## Detailed Usage

### 1. Model Generation

The main script `abaqus_acoustic_tl_simulation.py` contains a `AcousticConfig` class with all simulation parameters:

```python
class AcousticConfig:
    def __init__(self):
        # Model name
        self.model_name = 'AcousticTL_Stratified'
        self.job_name = 'acoustic_tl_job'
        
        # Geometry (2D or 3D)
        self.dimension = 2
        self.length = 100.0   # meters (propagation direction)
        self.height = 50.0    # meters (vertical)
        self.width = 10.0     # meters (3D only)
        
        # Frequency sweep
        self.freq_start = 100.0   # Hz
        self.freq_end = 5000.0    # Hz
        self.freq_inc = 25.0      # Hz
        
        # Stratification type
        self.stratification_type = 'layered'  # or 'graded'
        
        # Layers: (z_bottom, z_top, density, bulk_modulus)
        self.layers = [
            (0.0,  15.0, 1025.0, 2.306e9),
            (15.0, 30.0, 1015.0, 2.280e9),
            (30.0, 50.0, 1000.0, 2.250e9),
        ]
```

#### Layered Configuration

For sharp interfaces (constant properties per layer):

```python
config.stratification_type = 'layered'
config.layers = [
    (z_bottom, z_top, density, bulk_modulus),
    # Add more layers...
]
```

#### Graded Configuration

For continuous variation (field-variable dependent):

```python
config.stratification_type = 'graded'
config.graded_params = {
    'rho_surface': 1000.0,    # kg/m³ at z=height
    'rho_bottom': 1025.0,     # kg/m³ at z=0
    'K_surface': 2.250e9,     # Pa
    'K_bottom': 2.306e9,      # Pa
    'profile': 'linear',      # or 'exponential'
}
```

### 2. Running the Simulation

#### From Abaqus/CAE GUI

1. Open Abaqus/CAE
2. File → Run Script → `abaqus_acoustic_tl_simulation.py`
3. Job Manager → Submit `acoustic_tl_job`

#### From Command Line

```bash
# Generate model
abaqus cae noGUI=abaqus_acoustic_tl_simulation.py

# Run job (interactive for immediate feedback)
abaqus job=acoustic_tl_job interactive

# Or submit to background
abaqus job=acoustic_tl_job
```

### 3. Post-Processing

```bash
abaqus python postprocess_tl.py acoustic_tl_job
```

This extracts:
- Complex pressure `POR` at probe locations
- Computes spatial average magnitudes
- Calculates `TL(f) = 20·log₁₀(|p_in|/|p_out|)` [dB]
- Calculates `α(f) = (ln(10)/20)·TL/Δx` [Np/m]

**Output files:**
- `transmission_loss.csv` - Full results table
- `plot_tl.py` - Auto-generated plotting script

### 4. Visualization

```bash
python plot_tl.py
```

Generates 4 plots:
1. Pressure magnitude vs frequency (inlet & outlet)
2. Transmission Loss vs frequency
3. Attenuation coefficient (Np/m)
4. Attenuation coefficient (dB/m)

---

## Physical Parameters

### Units (SI System)

| Quantity | Unit | Symbol |
|----------|------|--------|
| Length | meter | m |
| Mass | kilogram | kg |
| Time | second | s |
| Pressure | Pascal | Pa |
| Density | kg/m³ | ρ |
| Bulk Modulus | Pa | K |
| Frequency | Hertz | Hz |

### Acoustic Medium Properties

Abaqus requires two properties for acoustic media:

1. **Density** (ρ): Mass per unit volume [kg/m³]
2. **Bulk Modulus** (K): Volumetric stiffness [Pa]

Sound speed is derived: **c = √(K/ρ)** [m/s]

#### Typical Values

| Medium | ρ (kg/m³) | K (Pa) | c (m/s) |
|--------|-----------|--------|---------|
| Fresh water (20°C) | 998 | 2.19×10⁹ | 1482 |
| Seawater (surface) | 1025 | 2.31×10⁹ | 1500 |
| Seawater (deep) | 1050 | 2.42×10⁹ | 1520 |
| Soft sediment | 1400 | 3.00×10⁹ | 1463 |
| Hard sediment | 1800 | 7.20×10⁹ | 2000 |

### Mesh Requirements

**Rule of thumb**: 10-12 elements per wavelength at the **highest frequency**

```
λ_min = c_min / f_max
Element_size ≤ λ_min / 12
```

Example:
- c_min = 1480 m/s (slowest layer)
- f_max = 5000 Hz
- λ_min = 0.296 m
- Element_size ≤ 0.025 m

The script auto-calculates mesh size based on your configuration.

---

## Element Types

### 2D Acoustics
- **AC2D4**: 4-node bilinear quadrilateral
- **AC2D8**: 8-node biquadratic quadrilateral (higher order)

### 3D Acoustics
- **AC3D8**: 8-node trilinear brick
- **AC3D20**: 20-node triquadratic brick (higher order)

> **Default**: AC2D4 (2D) or AC3D8 (3D) - sufficient for most applications

---

## Boundary Conditions

### 1. Incident Wave (Excitation)

Applied to **inlet surface** (x=0):

```python
*INCIDENT WAVE INTERACTION PROPERTY
*INCIDENT WAVE FLUID PROPERTY
rho, c   # Incident medium properties
*INCIDENT WAVE INTERACTION
surface, direction_x, direction_y, direction_z, amplitude
```

- Enforces proper velocity-pressure relation for incoming wave
- Avoids artificial reflections at inlet
- **Amplitude**: typically 1.0 Pa (can be scaled in post-processing)

### 2. Non-Reflecting Boundaries (Impedance)

Applied to **outlet, top, bottom** surfaces:

```python
*IMPEDANCE, TYPE=NONREFLECTING
surface_name,
```

- Implements Sommerfeld radiation condition
- Minimizes spurious reflections at domain truncation
- Essential for simulating infinite/semi-infinite domains

---

## Output and Results

### Field Output

- **POR**: Acoustic pressure (complex: real + imaginary)
- **PENER**: Acoustic energy density

### History Output

- **POR** at probe node sets (Probe_In, Probe_Out)
- Complex pressure time series at each frequency

### Post-Processed Quantities

1. **Transmission Loss**:
   ```
   TL(f) = 20·log₁₀(|p_in|/|p_out|)  [dB]
   ```

2. **Attenuation Coefficient** (amplitude-based):
   ```
   α(f) = (ln(10)/20)·TL(f)/Δx  [Np/m]
   α(f) = TL(f)/Δx              [dB/m]
   ```

3. **Attenuation Coefficient** (intensity-based):
   ```
   α(f) = (ln(10)/10)·TL(f)/Δx  [Np/m]
   ```

Where:
- Δx = probe separation distance
- 1 Np (Neper) ≈ 8.686 dB

---

## Example Configurations

### 1. Ocean Thermocline

```bash
# Edit config in abaqus_acoustic_tl_simulation.py
# Use layers from config_example_ocean_thermocline.py

abaqus cae noGUI=abaqus_acoustic_tl_simulation.py
abaqus job=ocean_thermocline_tl interactive
abaqus python postprocess_tl.py ocean_thermocline_tl
```

**Scenario**: Sound channel with minimum speed in thermocline  
**Expected TL**: 10-30 dB over 100 m  
**Physics**: Ray bending toward sound speed minimum

### 2. Sediment Layers

```bash
# Use config_example_sediment_layers.py configuration

abaqus cae noGUI=abaqus_acoustic_tl_simulation.py
abaqus job=sediment_layers_tl interactive
abaqus python postprocess_tl.py sediment_layers_tl
```

**Scenario**: Water-sediment interface with multiple layers  
**Expected TL**: 40-80 dB over 90 m  
**Physics**: Strong impedance contrasts, multiple reflections

### 3. Graded Profile

```bash
# Use config_example_graded_profile.py configuration

abaqus cae noGUI=abaqus_acoustic_tl_simulation.py
abaqus job=graded_profile_tl interactive
abaqus python postprocess_tl.py graded_profile_tl
```

**Scenario**: Continuous density/bulk modulus variation  
**Expected TL**: 5-15 dB over 60 m  
**Physics**: Smooth refraction, no sharp reflections

### 4. 3D Waveguide

```bash
# Use config_example_3d_waveguide.py configuration
# WARNING: Computationally expensive!

abaqus cae noGUI=abaqus_acoustic_tl_simulation.py
abaqus job=waveguide_3d_tl cpus=4
abaqus python postprocess_tl.py waveguide_3d_tl
```

**Scenario**: Full 3D propagation with lateral spreading  
**Expected TL**: 15-25 dB over 40 m  
**Physics**: 3D spreading + stratification effects

---

## Troubleshooting

### Issue: Job fails with "Negative eigenvalues"

**Cause**: Material properties inconsistent or mesh quality poor  
**Solution**:
- Verify K > 0 and ρ > 0 for all layers
- Check sound speed c = √(K/ρ) is realistic
- Improve mesh quality (avoid extreme aspect ratios)

### Issue: Pressure output is all zeros

**Cause**: Incident wave not properly applied or step definition error  
**Solution**:
- Check incident wave direction matches inlet normal
- Verify step is `STEADY STATE DYNAMICS, DIRECT`
- Ensure acoustic medium properties are assigned

### Issue: Very high TL (>100 dB) or negative TL

**Cause**: Probe location issues or boundary reflection  
**Solution**:
- Check probe sets contain nodes (print node counts)
- Move probes away from boundaries (>0.5 wavelength)
- Verify non-reflecting BCs are applied to all exterior surfaces

### Issue: Mesh too coarse warnings

**Cause**: Element size too large for highest frequency  
**Solution**:
- Decrease `max_element_size` in config
- Increase `target_elements_per_wavelength` (default: 12)
- Reduce `freq_end` for initial testing

### Issue: 3D simulation runs out of memory

**Cause**: Too many elements (3D scales as L³)  
**Solution**:
- Reduce domain size
- Coarsen mesh (reduce `target_elements_per_wavelength` to 8-10)
- Reduce frequency points (increase `freq_inc`)
- Use more CPUs and memory allocation

---

## Advanced Topics

### Field-Variable Dependent Properties

For graded media, Abaqus uses **field variables** to spatially vary material properties:

1. Define analytical field `F1(x,y,z)` - typically `F1 = z` (vertical coordinate)
2. Create material tables: `ρ(F1)`, `K(F1)`
3. Assign initial field values to all nodes

Example (keyword approach):
```
*MATERIAL, NAME=WATER_GRADED
*DENSITY, DEPENDENCIES=1
1025.0,  0.0
1000.0, 50.0
*ACOUSTIC MEDIUM, BULK MODULUS, DEPENDENCIES=1
2.306E9,  0.0
2.250E9, 50.0

*INITIAL CONDITIONS, TYPE=FIELD, VARIABLE=1
node_number, z_coordinate
```

### Frequency-Dependent Materials

Abaqus supports frequency-dependent acoustic properties:

```
*ACOUSTIC MEDIUM, BULK MODULUS, FREQUENCY DEPENDENT
K1, f1
K2, f2
...
```

Useful for modeling:
- Dispersion
- Relaxation processes
- Frequency-dependent absorption

### Acoustic-Structure Coupling

To include elastic walls/liners:

1. Create **structural** part (elastic solid) alongside **acoustic** part
2. Define **acoustic-structural interface** at contact surface
3. Use **TIE constraint** or **surface-to-surface contact**
4. Specify **structural damping** for absorption

Element types:
- Acoustic: AC2D4, AC3D8
- Structural: CPS4, C3D8

---

## Validation and Verification

### Analytical Benchmarks

1. **Plane wave in homogeneous medium**:
   - TL = 0 dB (no loss)
   - Verify by setting all layers to same properties

2. **Single interface (layered, 2 layers)**:
   - Compare reflection coefficient to analytical:
     ```
     R = (Z₂ - Z₁)/(Z₂ + Z₁)
     TL_theory = -20·log₁₀(1 - |R|²)
     ```
   - Z = ρ·c (acoustic impedance)

3. **Mesh convergence**:
   - Run with elements/wavelength = 8, 10, 12, 15
   - TL(f) should converge to <1% difference

### Recommended Tests

- **Mesh refinement study**: Halve element size, check TL change < 1 dB
- **Boundary position test**: Move outlet boundary, TL unchanged
- **Probe position test**: Move probes (keeping separation), verify TL

---

## References

### Abaqus Documentation

1. [Acoustic elements](https://abaqus-docs.mit.edu/2017/English/SIMACAEELMRefMap/simaelm-c-acousticelem.htm)
2. [Acoustic medium properties](https://abaqus-docs.mit.edu/2017/English/SIMACAEMATRefMap/simamat-c-acousticmedium.htm)
3. [Steady-State Dynamics, Direct](https://abaqus-docs.mit.edu/2017/English/SIMACAEANLRefMap/simaanl-c-steadystatedynamic.htm)
4. [Incident wave](https://abaqus-docs.mit.edu/2017/English/SIMACAEINTRefMap/simaint-c-incidentwave.htm)
5. [Acoustic impedance boundaries](https://abaqus-docs.mit.edu/2017/English/SIMACAEINTRefMap/simaint-c-acousticimpedance.htm)

### Technical Background

- **Helmholtz equation**: ∇²p + k²p = 0, k = ω/c
- **Transmission loss**: Energy ratio expressed in dB
- **Snell's law (refraction)**: sin(θ₁)/c₁ = sin(θ₂)/c₂
- **Impedance**: Z = ρc [Pa·s/m]

---

## License and Citation

This code is provided as-is for research and educational purposes.

**Citation**: If you use this code in published work, please cite:
```
Abaqus Acoustic Transmission Loss Simulation Framework
GitHub: [your-repo-url]
Date: 2025-10-19
```

---

## Contact and Support

For questions or issues:

1. Check Abaqus documentation (links above)
2. Verify input file syntax in `.dat` file
3. Review mesh quality in Abaqus/Viewer
4. Check material property units (SI system)

**Common mistakes**:
- ❌ Mixing units (e.g., cm and m)
- ❌ Using Young's modulus instead of bulk modulus
- ❌ Forgetting to apply non-reflecting BCs
- ❌ Placing probes too close to boundaries
- ❌ Insufficient mesh resolution at high frequency

---

## Appendix: Theory Summary

### Governing Equation

**Helmholtz equation** (frequency domain):
```
∇²p̃ + k²p̃ = 0
```
where:
- p̃ = complex pressure amplitude
- k = ω/c = wave number
- ω = 2πf = angular frequency

### Boundary Conditions

1. **Incident wave** (Dirichlet-like):
   ```
   p̃ = p₀·exp(i·k·x)  at inlet
   ```

2. **Non-reflecting** (Sommerfeld):
   ```
   ∂p̃/∂n + i·k·p̃ = 0  at outlet/boundaries
   ```

### Stratification Effects

**Snell's law** (layer interface):
```
k_x = ω·sin(θ)/c = constant across layers
```

**Reflection coefficient**:
```
R = (Z₂ - Z₁)/(Z₂ + Z₁)
Z = ρ·c (acoustic impedance)
```

**Transmission coefficient**:
```
T = 2·Z₂/(Z₂ + Z₁)
```

**Power transmission**:
```
|T|² = 1 - |R|²
TL = -10·log₁₀(|T|²) = -20·log₁₀(|T|)
```

### Attenuation

**Amplitude decay**:
```
p(x) = p₀·exp(-α·x)
```

**From measured TL**:
```
TL = 20·log₁₀(p_in/p_out)
α = (ln(10)/20)·TL/Δx  [Np/m]
α = 0.1151·TL/Δx       [Np/m]
```

**Intensity-based** (for power):
```
α = (ln(10)/10)·TL/Δx  [Np/m]
```

---

## Version History

- **v1.0** (2025-10-19): Initial release
  - 2D/3D acoustic simulations
  - Layered and graded stratification
  - Automated mesh generation
  - Post-processing with TL and α
  - Example configurations

---

**End of README**
