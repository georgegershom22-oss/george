# Abaqus Acoustic Transmission Loss Simulation

A comprehensive Python framework for simulating acoustic transmission loss in stratified media using Abaqus/CAE. This package implements both layered and continuous gradient acoustic media with proper boundary conditions and post-processing capabilities.

## Features

- **Linear Acoustics**: Implements Helmholtz equation for quiescent media
- **Stratified Media**: Supports both layered and continuous gradient density/bulk modulus
- **Steady-State Dynamics**: Uses Direct method for harmonic frequency sweeps
- **Proper Boundary Conditions**: Incident wave excitation and non-reflecting boundaries
- **Acoustic Elements**: Uses AC2D4/AC3D8/AC3D20 elements with proper mesh density
- **Post-Processing**: Complete analysis tools for TL and absorption coefficient calculation

## Files Overview

### Main Scripts
- `abaqus_acoustic_transmission_loss.py` - Main simulation framework
- `abaqus_input_generator.py` - Direct .inp file generation
- `post_processing_utils.py` - Results analysis and visualization

### Key Classes

#### `AcousticTransmissionLossSimulation`
Main simulation class with methods for:
- Geometry creation (2D/3D)
- Material definition (layered/gradient)
- Mesh generation
- Boundary condition setup
- Analysis execution
- Results post-processing

#### `AbaqusInputGenerator`
Direct input file generation for:
- Node and element definitions
- Material properties
- Boundary conditions
- Analysis steps

#### `AcousticPostProcessor`
Results analysis including:
- Transmission loss calculation
- Absorption coefficient computation
- Data visualization
- Statistical analysis
- Results validation

## Quick Start

### 1. Basic Layered Medium Simulation

```python
from abaqus_acoustic_transmission_loss import AcousticTransmissionLossSimulation

# Initialize simulation
sim = AcousticTransmissionLossSimulation("MySimulation")

# Create 2D geometry
sim.create_geometry(geometry_type="2D", length=10.0, width=2.0)

# Define layered medium
layer_data = [
    {
        'name': 'Surface_Layer',
        'z_start': 0.0,
        'z_end': 1.0,
        'density': 1025.0,  # kg/m³
        'bulk_modulus': 2.306e9  # Pa
    },
    {
        'name': 'Deep_Layer',
        'z_start': 1.0,
        'z_end': 2.0,
        'density': 980.0,  # kg/m³
        'bulk_modulus': 2.162e9  # Pa
    }
]
sim.define_layered_medium(layer_data)

# Create mesh and run analysis
sim.create_mesh(element_size_factor=0.1)
sim.create_sets_and_surfaces()
sim.create_step()
sim.create_incident_wave()
sim.create_impedance_boundaries()
sim.create_output_requests()

# Run analysis
success = sim.run_analysis("MyJob")
if success:
    results = sim.post_process_results("MyJob")
    sim.save_results(results, "my_results.csv")
```

### 2. Continuous Gradient Medium

```python
# Define gradient medium
gradient_params = {
    'base_density': 1025.0,  # kg/m³
    'base_bulk_modulus': 2.306e9,  # Pa
    'density_gradient': -45.0,  # kg/m³/m
    'bulk_modulus_gradient': -0.144e9  # Pa/m
}

sim.define_gradient_medium(gradient_params)
```

### 3. Post-Processing Results

```python
from post_processing_utils import AcousticPostProcessor

# Load results
processor = AcousticPostProcessor(results)

# Generate plots
processor.plot_transmission_loss()
processor.plot_absorption_coefficient()
processor.plot_pressure_amplitudes()

# Export data
processor.export_results("processed_results.csv")

# Calculate statistics
stats = processor.calculate_statistics()
print(f"Mean TL: {stats['TL_mean']:.2f} dB")
```

## Physical Background

### Transmission Loss Calculation
```
TL(f) = 20 * log₁₀(|P_in(f)| / |P_out(f)|)
```

### Absorption Coefficient
```
α_amp(f) = (ln(10) / 20) * TL(f) / Δx
```

Where:
- `P_in(f)`, `P_out(f)` are complex pressure amplitudes at inlet/outlet
- `Δx` is the distance between probe points
- `f` is frequency

### Acoustic Properties
- **Density (ρ)**: Mass per unit volume (kg/m³)
- **Bulk Modulus (K)**: Compressibility (Pa)
- **Sound Speed**: c = √(K/ρ) (m/s)
- **Impedance**: Z = ρc (Pa·s/m)

## Model Setup Guidelines

### 1. Units
Use consistent SI units:
- Length: meters (m)
- Mass: kilograms (kg)
- Time: seconds (s)
- Pressure: Pascals (Pa)

### 2. Mesh Requirements
- Element size: ~λ/10 where λ = c/f_min
- Use acoustic elements: AC2D4, AC3D8, AC3D20
- Maintain element quality (avoid extreme aspect ratios)

### 3. Frequency Range
- Typical range: 100-5000 Hz
- Increment: 25-50 Hz
- Ensure sufficient resolution for phenomena of interest

### 4. Boundary Conditions
- **Inlet**: Incident wave with proper fluid properties
- **Outlet**: Non-reflecting impedance boundary
- **Lateral**: Non-reflecting (if 3D) or symmetry (if 2D)

## Validation and Quality Assurance

### Mesh Convergence
```python
# Test with different element sizes
element_sizes = [0.2, 0.1, 0.05]  # m
for size in element_sizes:
    sim.create_mesh(element_size_factor=size/λ_min)
    # Compare TL results
```

### Boundary Condition Check
- Move probe locations and verify TL invariance
- Check that boundaries are truly non-reflecting
- Validate incident wave properties

### Physical Validation
- Verify sound speed: c = √(K/ρ)
- Check for reasonable TL values (0-50 dB typical)
- Ensure absorption coefficient is positive

## Common Issues and Solutions

### 1. Convergence Problems
- Check material property consistency
- Verify boundary condition setup
- Ensure proper element types (acoustic elements)

### 2. Unphysical Results
- Validate material properties
- Check probe locations (avoid boundaries)
- Verify frequency range and mesh density

### 3. Memory Issues
- Use 2D models for initial testing
- Reduce frequency range or mesh density
- Consider modal analysis for very large models

## Example Applications

### 1. Underwater Acoustics
- Ocean stratification effects
- Sound propagation in layered media
- Bottom interaction modeling

### 2. Atmospheric Acoustics
- Temperature gradient effects
- Wind speed variations
- Ground impedance modeling

### 3. Industrial Applications
- Duct acoustics
- Silencer design
- Noise control systems

## Dependencies

- Abaqus/CAE 2020 or later
- Python 3.7+
- NumPy
- Matplotlib
- SciPy
- Pandas

## References

1. Abaqus Analysis User's Guide - Acoustic Elements
2. Abaqus Analysis User's Guide - Steady-State Dynamics
3. Abaqus Analysis User's Guide - Acoustic Impedance
4. Kinsler, L.E. et al. "Fundamentals of Acoustics"
5. Pierce, A.D. "Acoustics: An Introduction to Its Physical Principles and Applications"

## License

This code is provided for educational and research purposes. Please cite appropriately if used in publications.

## Support

For questions or issues, please refer to the Abaqus documentation or contact the development team.