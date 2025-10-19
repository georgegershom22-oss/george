# Abaqus Acoustic Transmission Loss Simulation

A comprehensive Python framework for simulating acoustic transmission loss through stratified media using Abaqus/CAE and Abaqus/Standard.

## Overview

This framework provides complete tools for:
- **2D and 3D acoustic domain modeling**
- **Layered and continuously graded media**
- **Incident wave excitation with proper plane wave loading**
- **Non-reflecting boundary conditions**
- **Steady-state dynamics analysis (harmonic sweep)**
- **Automatic post-processing for TL(f) and α(f)**
- **Quality assurance and validation tools**

## Features

### What Abaqus Will Simulate
- ✅ Linear acoustics in quiescent media (Helmholtz equation)
- ✅ Layered or smoothly varying ρ, K (bulk modulus)
- ✅ Scattering at impedance contrasts
- ✅ Acoustic-structure coupling (if walls/liners included)
- ✅ Harmonic frequency sweeps using Steady-State Dynamics, Direct

### What It Won't Simulate
- ❌ Stratified fluid dynamics (internal waves/baroclinic vorticity)
- ❌ Nonlinear acoustics
- ❌ Mean flow effects

## File Structure

```
├── abaqus_acoustic_simulation.py    # Main CAE-based simulation class
├── abaqus_input_generator.py        # Keyword-based input file generator
├── post_processing_tools.py         # Comprehensive post-processing tools
├── run_complete_simulation.py       # Complete workflow examples
└── README.md                        # This file
```

## Quick Start

### 1. Basic 2D Layered Medium

```python
from abaqus_acoustic_simulation import AcousticSimulation

# Create simulation
sim = AcousticSimulation(model_name='LayeredMedium2D')
sim.create_model()

# Create 2D geometry
sim.create_2d_geometry(length=10.0, height=4.0)

# Define layers
layers = [
    {'name': 'WATER_BOTTOM', 'density': 1030.0, 'bulk_modulus': 2.4e9, 'thickness': 2.0},
    {'name': 'WATER_TOP', 'density': 1020.0, 'bulk_modulus': 2.2e9, 'thickness': 2.0}
]

# Create materials and partition geometry
sim.create_layered_materials(layers)
sim.partition_for_layers(layers, dimension='2D')
sim.assign_layered_sections(layers, dimension='2D')

# Create mesh (12 elements per wavelength at 2000 Hz)
sim.create_mesh(element_type='AC2D4', target_frequency=2000.0)

# Create assembly and analysis
sim.create_assembly()
sim.create_steady_state_step(freq_start=100.0, freq_end=3000.0, freq_inc=50.0)

# Apply loading and boundaries
sim.create_incident_wave(direction=(1.0, 0.0, 0.0))
sim.create_non_reflecting_boundaries()
sim.create_output_requests()

# Create and run job
sim.create_job(job_name='LayeredMedium2D', num_cpus=2)
sim.run_analysis(wait_for_completion=True)

# Post-process results
results = sim.post_process_transmission_loss()
sim.save_results(results, 'transmission_loss_results.csv')
```

### 2. 3D Graded Medium

```python
# Create 3D simulation with continuous gradients
sim = AcousticSimulation(model_name='GradedMedium3D')
sim.create_model()
sim.create_3d_geometry(length=8.0, height=3.0, width=2.0)

# Create analytical field for depth variation
sim.create_analytical_field(name='DepthField', expression='Z')

# Define property profiles
density_profile = [
    (0.0, 1020.0),    # Surface
    (1.5, 1025.0),    # Middle
    (3.0, 1030.0)     # Bottom
]

bulk_modulus_profile = [
    (0.0, 2.2e9),     # Surface
    (1.5, 2.3e9),     # Middle
    (3.0, 2.4e9)      # Bottom
]

# Create graded material
sim.create_graded_material('WATER_GRADED', density_profile, bulk_modulus_profile)
sim.assign_graded_section('WATER_GRADED', 'DepthField')

# Continue with mesh, analysis, etc...
```

### 3. Input File Generation (Keyword Approach)

```python
from abaqus_input_generator import AbaqusInputGenerator

# Create generator
gen = AbaqusInputGenerator('LayeredMedium2D')

# Generate mesh
gen.generate_2d_rectangular_mesh(length=10.0, height=4.0, nx=100, ny=40)

# Add materials
layers = [
    {'name': 'WATER_BOTTOM', 'density': 1030.0, 'bulk_modulus': 2.4e9},
    {'name': 'WATER_TOP', 'density': 1020.0, 'bulk_modulus': 2.2e9}
]
gen.add_layered_materials(layers)
gen.create_layered_element_sets([2.0, 4.0])

# Write input file
gen.write_input_file('layered_medium_2d.inp', '2D_LAYERED')

# Run in Abaqus/Standard
# abaqus job=layered_medium_2d input=layered_medium_2d.inp
```

### 4. Post-Processing

```python
from post_processing_tools import AcousticPostProcessor

# Process ODB file
processor = AcousticPostProcessor('simulation.odb')
processor.open_odb()
processor.extract_probe_data()

# Calculate transmission loss
probe_separation = 6.0  # meters between probes
results = processor.calculate_transmission_loss(probe_separation=probe_separation)

# Export results
processor.export_results('results.csv', format='csv')
processor.plot_results(save_plots=True)

# Quality assessment
quality = processor.quality_assessment()
processor.close_odb()
```

## Complete Workflow Example

```python
from run_complete_simulation import main

# Run complete parametric study
results = main()
```

This will create multiple simulation scenarios, generate input files, and demonstrate post-processing.

## Units and Conventions

- **Units**: SI system (m-kg-s-Pa)
- **Coordinate system**: X = propagation direction, Y = depth (for 2D), Z = width (for 3D)
- **Material properties**: Density ρ (kg/m³) and Bulk modulus K (Pa)
- **Sound speed**: c = √(K/ρ) (derived automatically)

## Element Types

- **2D**: AC2D4 (4-node), AC2D8 (8-node)
- **3D**: AC3D8 (8-node), AC3D20 (20-node)
- **Mesh density**: ≥10-12 elements per wavelength recommended

## Analysis Setup

### Steady-State Dynamics, Direct
- Linear harmonic analysis
- Frequency sweep (e.g., 100-5000 Hz)
- Complex pressure amplitude and phase output

### Boundary Conditions
- **Incident wave**: Proper plane wave loading using `*INCIDENT WAVE`
- **Non-reflecting**: Impedance boundaries using `*IMPEDANCE, TYPE=NONREFLECTING`
- **Probe locations**: Typically at 20% and 80% of domain length

### Material Definitions
```
*MATERIAL, NAME=WATER
*DENSITY
1025.,
*BULK MODULUS
2.306e9,
```

## Post-Processing Calculations

### Transmission Loss
```
TL(f) = 20 * log₁₀(|p_in(f)| / |p_out(f)|)
```

### Absorption Coefficient (Amplitude-based)
```
α_amp(f) = (ln(10)/20) * TL(f) / Δx
```

### Absorption Coefficient (Intensity-based)
```
α_int(f) = (ln(10)/10) * TL(f) / Δx
```

Where Δx is the distance between probe planes.

## Quality Assurance

### Mesh Resolution Test
- Halve element size
- TL(f) should change negligibly if properly resolved

### Boundary Check
- Move probe planes
- TL should be invariant with proper non-reflecting boundaries

### Validation Checks
- Element type confirmation (AC2D4/AC3D8)
- Property consistency: c = √(K/ρ)
- Frequency spacing consistency

## Common Pitfalls and Solutions

1. **Mesh too coarse**: Use ≥10 elements per wavelength
2. **Artificial reflections**: Ensure proper non-reflecting boundaries
3. **Property mismatch**: Verify ρ and K are consistent
4. **Zero pressures**: Check probe set definitions
5. **Excessive TL**: May indicate numerical issues

## Example Input File Structure

```
*HEADING
** 2D Layered Acoustic Medium
*NODE
1, 0.0, 0.0
2, 0.1, 0.0
...
*ELEMENT, TYPE=AC2D4
1, 1, 2, 3, 4
...
*MATERIAL, NAME=WATER_BOTTOM
*DENSITY
1030.,
*BULK MODULUS
2.4e9,
*SOLID SECTION, ELSET=BOTTOM_LAYER, MATERIAL=WATER_BOTTOM
*STEP, NAME=STEADY_STATE
*STEADY STATE DYNAMICS, DIRECT
100., 3000., 50.
*INCIDENT WAVE INTERACTION PROPERTY, NAME=PLANEWAVE
*INCIDENT WAVE FLUID PROPERTY
1025., 1500.
*INCIDENT WAVE INTERACTION, NAME=INC1, PROPERTY=PLANEWAVE
INLET, 1., 0., 0.
*IMPEDANCE, TYPE=NONREFLECTING
OUTLET,
LATERAL,
*OUTPUT, FIELD
*NODE OUTPUT
P
*OUTPUT, HISTORY
*NODE PRINT, NSET=PROBE_IN
P
*NODE PRINT, NSET=PROBE_OUT
P
*END STEP
```

## Requirements

- Abaqus/CAE and Abaqus/Standard
- Python 2.7 or 3.x (depending on Abaqus version)
- NumPy (for post-processing)
- Matplotlib (optional, for plotting)

## Running Simulations

### Using Abaqus/CAE
```python
# In Abaqus/CAE command line
execfile('abaqus_acoustic_simulation.py')
sim = example_layered_medium_2d()
sim.run_analysis()
```

### Using Abaqus/Standard (command line)
```bash
abaqus job=simulation_name input=input_file.inp cpus=2
```

### Post-processing
```bash
python post_processing_tools.py simulation.odb 6.0
```

## Advanced Features

### Parametric Studies
- Multiple layer configurations
- Gradient profile variations
- Frequency and mesh convergence studies

### Field Variable Dependencies
- Continuous property gradients
- Analytical field definitions
- Temperature-dependent properties

### Quality Assessment
- Automatic mesh validation
- Result quality scoring
- Warning detection

## References

- Abaqus Documentation: Acoustic elements and procedures
- Course notes on acoustic finite element methods
- Verification examples in Abaqus documentation

## License

This code is provided as-is for educational and research purposes.

## Support

For questions or issues, please refer to:
- Abaqus documentation for element types and procedures
- Acoustic finite element method references
- Example verification cases