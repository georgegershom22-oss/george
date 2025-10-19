# Abaqus Acoustic Transmission Loss Simulation Suite

## Overview

This comprehensive suite provides a complete framework for simulating acoustic wave propagation through stratified media using Abaqus, calculating transmission loss (TL) and absorption coefficients (α) across frequency spectra. The package supports both discrete layered media and continuously graded property distributions.

## Features

- **Full Abaqus Python automation** for model creation, meshing, and job submission
- **Layered and continuously graded** stratification models
- **Incident plane wave** excitation with proper impedance matching
- **Non-reflecting boundary conditions** using impedance formulations
- **Comprehensive post-processing** for TL and absorption coefficient extraction
- **Advanced visualization** including field plots, animations, and ray paths
- **Utility functions** for realistic ocean/atmospheric property modeling

## System Requirements

- Abaqus/CAE 2019 or later with Python scripting capability
- Python 2.7 (for Abaqus) or Python 3.6+ (for standalone post-processing)
- NumPy, SciPy, Matplotlib
- Optional: ffmpeg for animations

## File Structure

```
workspace/
│
├── abaqus_acoustic_tl_simulation.py  # Main Abaqus simulation script
├── post_process_tl.py                # TL/absorption calculation
├── acoustic_utilities.py             # Material property utilities
├── visualize_acoustic_fields.py      # Field visualization tools
├── acoustic_layered.inp              # Example layered medium input
├── acoustic_graded.inp               # Example graded medium input
└── README.md                         # This file
```

## Quick Start

### 1. Basic Simulation Run

Run the main simulation script in Abaqus/CAE:

```bash
abaqus cae script=abaqus_acoustic_tl_simulation.py
```

Or interactively in Abaqus Python:

```python
execfile('abaqus_acoustic_tl_simulation.py')
```

### 2. Post-Processing

After simulation completion, extract TL and absorption:

```bash
abaqus python post_process_tl.py TL_Layered.odb 6.0
```

Parameters:
- First argument: ODB file path
- Second argument: Probe separation distance (meters)

### 3. Visualization

Generate field plots and animations:

```bash
abaqus python visualize_acoustic_fields.py TL_Layered.odb
```

## Detailed Usage

### Main Simulation Script

The `AcousticTLSimulation` class provides complete control over the simulation:

```python
from abaqus_acoustic_tl_simulation import AcousticTLSimulation

# Initialize simulation
sim = AcousticTLSimulation(
    model_name='MyAcousticModel',
    job_name='MyAcousticJob'
)

# Configure parameters
sim.domain_length = 10.0      # meters
sim.domain_width = 2.0        # meters
sim.freq_start = 100.0        # Hz
sim.freq_end = 5000.0         # Hz
sim.freq_increment = 25.0     # Hz

# Run layered case
sim.run_layered_case()

# Or run graded case
sim.run_graded_case()
```

### Customizing Material Properties

#### Layered Medium

Modify the `create_materials_layered()` method:

```python
def create_materials_layered(self):
    # Layer 1: Custom properties
    mat1 = self.model.Material(name='Layer1')
    mat1.Density(table=((1020.0, ), ))      # kg/m³
    mat1.AcousticMedium(bulkModulus=2.25e9) # Pa
    
    # Add more layers as needed
    return [mat1, mat2, mat3]
```

#### Continuously Graded Medium

Define field-dependent properties:

```python
def create_materials_graded(self):
    mat = self.model.Material(name='Graded')
    
    # Density varies with field variable FV1
    density_table = [
        (1020.0, 0.0),   # ρ at FV1=0
        (1030.0, 0.5),   # ρ at FV1=0.5
        (1040.0, 1.0),   # ρ at FV1=1.0
    ]
    mat.Density(table=density_table, dependencies=1)
    
    # Similarly for bulk modulus
    return mat
```

### Using Input Files

For batch processing or HPC clusters, use the provided input files:

```bash
abaqus job=acoustic_layered input=acoustic_layered.inp cpus=4
abaqus job=acoustic_graded input=acoustic_graded.inp cpus=4
```

### Utility Functions

The `acoustic_utilities.py` module provides helper functions:

```python
from acoustic_utilities import AcousticMaterialProperties, OceanStratification

# Calculate water properties
props = AcousticMaterialProperties.water_properties(
    temperature=15.0,  # °C
    salinity=35.0,     # PSU
    pressure=100.0     # dbar
)
print(f"Density: {props['density']} kg/m³")
print(f"Sound speed: {props['sound_speed']} m/s")

# Generate ocean stratification
depths = np.linspace(0, 1000, 100)
profile = OceanStratification.canonical_deep_ocean(depths)
```

## Physical Model Details

### Governing Equation

The simulation solves the Helmholtz equation for linear acoustics:

```
∇²p + (ω/c)²p = 0
```

Where:
- p = complex pressure amplitude
- ω = angular frequency
- c = sound speed (c = √(K/ρ))

### Material Properties

Required acoustic properties:
- **Density (ρ)**: kg/m³
- **Bulk Modulus (K)**: Pa

Sound speed is derived: c = √(K/ρ)

### Boundary Conditions

1. **Incident Wave**: Planar wave with specified direction
2. **Non-reflecting**: Impedance Z = ρc at boundaries
3. **Rigid Walls**: Optional (∂p/∂n = 0)

### Transmission Loss Calculation

```
TL(f) = 20 log₁₀(|p_in|/|p_out|) [dB]
```

### Absorption Coefficient

Amplitude-based:
```
α_amp = (ln(10)/20) × TL/Δx [m⁻¹]
```

Intensity-based:
```
α_int = (ln(10)/10) × TL/Δx [m⁻¹]
```

## Mesh Considerations

### Element Types
- 2D: AC2D4 (4-node quadrilateral)
- 3D: AC3D8 (8-node hexahedral)

### Mesh Density
- Target: 10-12 elements per wavelength
- Element size: h ≤ λ_min/10
- λ_min = c/f_max

### Quality Checks
- Avoid high aspect ratios (> 5:1)
- Check for element distortion
- Verify node connectivity

## Frequency Sweep Parameters

### Linear Sweep
```python
frequencyRange=((100.0, 5000.0, 25.0, LINEAR), )
```

### Logarithmic Sweep
```python
frequencyRange=((100.0, 5000.0, 50, LOGARITHMIC), )
```

## Output Files

After running the complete workflow:

1. **Numerical Results**
   - `transmission_loss_results.csv`: TL and α vs frequency
   - `tl_summary.txt`: Statistical summary

2. **Visualizations**
   - `transmission_loss_plots.png`: TL/α spectra
   - `pressure_magnitude.png`: Field distribution
   - `wave_propagation.png`: Phase snapshots
   - `intensity_field.png`: Energy flow

3. **Reports**
   - `tl_report.html`: Complete HTML report

## Validation

### Analytical Solutions

For uniform medium, compare with:
- Plane wave: TL = α × L
- Spherical spreading: TL = 20 log₁₀(r)
- Cylindrical spreading: TL = 10 log₁₀(r)

### Convergence Studies

1. **Mesh convergence**: Halve element size
2. **Frequency resolution**: Double frequency points
3. **Domain size**: Extend boundaries

## Troubleshooting

### Common Issues

1. **"No pressure field found"**
   - Verify step type is Steady-State Dynamics, Direct
   - Check output request includes 'P' variable

2. **High TL at low frequencies**
   - Increase domain size (wavelength effects)
   - Check impedance boundary conditions

3. **Oscillations in TL curve**
   - Insufficient mesh density
   - Boundary reflections (move probes inward)

4. **Memory errors**
   - Reduce frequency points
   - Use coarser mesh
   - Enable disk-based solver

### Debug Mode

Enable verbose output in scripts:

```python
sim.debug_mode = True
processor.verbose = True
```

## Advanced Features

### Custom Stratification

Implement your own profile:

```python
class CustomStratification:
    @staticmethod
    def my_profile(depths, **params):
        # Your implementation
        return density, sound_speed
```

### Parallel Processing

For HPC environments:

```bash
abaqus job=acoustic cpus=8 mp_mode=mpi
```

### Parametric Studies

Use Python loops for parameter sweeps:

```python
for freq_max in [1000, 2000, 5000, 10000]:
    sim.freq_end = freq_max
    sim.job_name = f'TL_fmax_{freq_max}'
    sim.run_layered_case()
```

## Theory References

1. **Abaqus Acoustic Elements**: Abaqus Theory Manual, Section 2.9
2. **Ocean Acoustics**: Jensen et al., "Computational Ocean Acoustics"
3. **Absorption Models**: Francois & Garrison (1982), JASA
4. **Stratification Effects**: Brekhovskikh & Lysanov, "Fundamentals of Ocean Acoustics"

## Citation

If you use this simulation suite in your research, please cite:

```bibtex
@software{abaqus_acoustic_tl,
  title={Abaqus Acoustic Transmission Loss Simulation Suite},
  author={Acoustic Simulation Framework},
  year={2024},
  url={https://github.com/your-repo/acoustic-tl}
}
```

## License

This software is provided as-is for educational and research purposes. Commercial use requires appropriate Abaqus licensing.

## Support

For questions or issues:
1. Check the troubleshooting section
2. Review Abaqus documentation
3. Consult acoustic textbooks for theory

## Acknowledgments

This suite implements standard acoustic finite element methods as described in the Abaqus documentation and acoustic literature.