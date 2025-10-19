# Abaqus Acoustic Transmission Loss Simulation

This repository contains a complete Abaqus simulation setup for analyzing acoustic transmission loss in layered fluid media. The simulation implements the methodology described in the detailed acoustic analysis specifications.

## Overview

This simulation analyzes acoustic wave propagation through a stratified fluid medium with two layers having different acoustic properties:

- **Top Layer**: Density = 1025 kg/m³, Bulk Modulus = 2.306e9 Pa
- **Bottom Layer**: Density = 980 kg/m³, Bulk Modulus = 2.162e9 Pa

The analysis covers a frequency range from 100 Hz to 5000 Hz with 25 Hz increments.

## Files Description

### Core Simulation Files

1. **`acoustic_transmission_loss.inp`** - Main Abaqus input file
   - 2D acoustic waveguide geometry (10m × 2m)
   - Layered material properties
   - Steady-State Dynamics analysis
   - Incident wave excitation
   - Non-reflecting boundary conditions
   - Probe points for TL measurement

2. **`post_process_tl.py`** - Python post-processing script
   - Extracts pressure data from ODB file
   - Calculates Transmission Loss (TL)
   - Computes attenuation coefficient (α)
   - Generates plots and CSV output

3. **`run_simulation.py`** - Automated simulation runner
   - Executes Abaqus job
   - Runs post-processing
   - Manages file cleanup

## Simulation Features

### Geometry
- **Domain**: 2D rectangular waveguide (10m × 2m)
- **Mesh**: AC2D4 acoustic elements with ~λ/10 resolution
- **Layers**: Two horizontal layers with different acoustic properties

### Analysis Setup
- **Step Type**: Steady-State Dynamics, Direct
- **Frequency Range**: 100-5000 Hz (25 Hz increments)
- **Excitation**: Plane wave incident from inlet
- **Boundaries**: Non-reflecting impedance at outlet

### Materials
- **Top Layer**: Seawater-like properties (ρ=1025 kg/m³, K=2.306e9 Pa)
- **Bottom Layer**: Freshwater-like properties (ρ=980 kg/m³, K=2.162e9 Pa)

### Output
- **Field Output**: Complex pressure field at all nodes
- **History Output**: Pressure at probe locations
- **Probes**: Input (x=2m) and Output (x=8m) measurement planes

## Usage

### Method 1: Automated Execution
```bash
python run_simulation.py
```

### Method 2: Manual Execution
```bash
# Run Abaqus simulation
abaqus job=acoustic_tl_sim input=acoustic_transmission_loss.inp interactive

# Post-process results
python post_process_tl.py acoustic_tl_sim.odb
```

## Output Files

After successful execution, you'll get:

1. **`acoustic_results.csv`** - Tabulated results with:
   - Frequency (Hz)
   - Pressure In/Out (Pa)
   - Transmission Loss (dB)
   - Attenuation Coefficient (1/m)

2. **`acoustic_results.png`** - Plots showing:
   - TL vs Frequency
   - Attenuation Coefficient vs Frequency

3. **`acoustic_tl_sim.odb`** - Abaqus database for further analysis

## Key Calculations

### Transmission Loss
```
TL(f) = 20 * log₁₀(|P_in(f)| / |P_out(f)|)
```

### Attenuation Coefficient
```
α_amp(f) = (ln(10)/20) * TL(f) / Δx
```
Where Δx = 6m (distance between probe planes)

## Quality Assurance

The simulation includes several quality checks:

1. **Mesh Resolution**: Elements sized at ~λ/10 for accurate wave propagation
2. **Boundary Conditions**: Non-reflecting boundaries to prevent artificial reflections
3. **Material Consistency**: Acoustic properties satisfy c = √(K/ρ)
4. **Probe Placement**: Sufficient distance from boundaries to avoid edge effects

## Technical Specifications

### Element Types
- **AC2D4**: 4-node acoustic elements for 2D analysis
- **Mesh Density**: ~10-12 elements per wavelength

### Analysis Parameters
- **Linear Acoustics**: Helmholtz equation in quiescent media
- **Frequency Domain**: Steady-state harmonic analysis
- **No Mean Flow**: Linear perturbation about base state

### Boundary Conditions
- **Inlet**: Incident plane wave excitation
- **Outlet**: Non-reflecting impedance (Sommerfeld radiation)
- **Lateral**: Free boundaries (2D assumption)

## Troubleshooting

### Common Issues

1. **Abaqus not found**: Ensure Abaqus is installed and in PATH
2. **Memory issues**: Reduce mesh density or frequency range
3. **Convergence problems**: Check material properties and boundary conditions
4. **Missing ODB**: Verify simulation completed successfully

### Performance Tips

1. **Parallel Processing**: Use `cpus=N` in Abaqus command for multi-core systems
2. **Memory Management**: Adjust memory allocation in Abaqus environment
3. **Mesh Optimization**: Balance accuracy vs. computational cost

## Validation

The simulation can be validated by:

1. **Mesh Convergence**: Halve element size and compare results
2. **Boundary Independence**: Move probe planes and verify TL invariance
3. **Energy Conservation**: Check that TL increases with frequency
4. **Physical Bounds**: Ensure attenuation coefficient is positive

## References

- Abaqus Documentation: Acoustic Analysis
- WUSTL Engineering Classes: Acoustic Medium Properties
- Software VT Documentation: Steady-State Dynamics
- Dassault Systèmes: Acoustic Impedance Boundaries

## License

This simulation setup is provided for educational and research purposes. Please cite appropriately if used in publications.

## Contact

For questions or issues with this simulation setup, please refer to the Abaqus documentation or consult with acoustic simulation experts.