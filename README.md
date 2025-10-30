# SOFC High-Fidelity Numerical Dataset Generator

This repository contains a comprehensive framework for generating high-fidelity numerical datasets for Solid Oxide Fuel Cell (SOFC) thermo-mechanics simulations. The dataset is designed for training Physics-Informed Neural Networks (PINNs) and other data-driven models for real-time performance and stress prediction.

## Overview

The dataset generator solves coupled multi-physics equations including:
- **Electrochemistry**: Current density and overpotential distribution
- **Thermal Transport**: Temperature distribution throughout the cell
- **Mechanical Stress**: Von Mises stress, strain tensors, and displacement fields
- **Species Transport**: H₂ and H₂O concentration distributions

## Dataset Structure

### Input Parameters (Features)

#### Operating Conditions
- Voltage/Current Density
- Air/Fuel Flow Rates
- Inlet Temperatures (fuel and air)

#### Material Properties (for each layer: anode, electrolyte, cathode, interconnect)
- Porosity
- Permeability
- Ionic/Electronic Conductivity
- Young's Modulus
- Coefficient of Thermal Expansion (CTE)
- Thermal Conductivity
- Other material properties

#### Geometric Parameters
- Thickness of each layer
- Active area
- Flow channel design parameters

### Output Fields (Labels)

#### Electrochemical Fields
- Current density distribution [A/m²]
- Overpotential distribution [V]

#### Thermal Fields
- Temperature distribution T(x,y,z) [K]

#### Stress/Strain Fields
- Von Mises stress [Pa]
- Strain tensor components (xx, yy, zz, xy, xz, yz)
- Displacement fields (u, v, w) [m]

#### Species Fields
- H₂ concentration distribution [mol/m³]
- H₂O concentration distribution [mol/m³]

## Installation

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Generate a dataset with default settings (100 samples):
```bash
python generate_dataset.py
```

### Advanced Usage

Generate a larger dataset with custom grid resolution:
```bash
python generate_dataset.py --n-samples 500 --grid-resolution 60 60 40 --output-dir my_dataset
```

### Command Line Options

- `--n-samples`: Number of simulation runs to generate (default: 100)
- `--output-dir`: Output directory for dataset (default: sofc_dataset)
- `--grid-resolution`: Grid resolution as three integers nx ny nz (default: 50 50 30)
- `--seed`: Random seed for reproducibility (default: 42)
- `--batch-size`: Batch size for processing (default: 10)

### Example: Generate Large Dataset

```bash
python generate_dataset.py \
    --n-samples 1000 \
    --grid-resolution 80 80 50 \
    --output-dir sofc_large_dataset \
    --seed 12345
```

## Output Structure

The generator creates the following files:

```
output_dir/
├── sofc_dataset.h5          # Main HDF5 dataset file
├── metadata.json            # Dataset metadata and information
└── parameter_ranges.csv     # Parameter ranges for reference
```

### HDF5 Dataset Structure

```
sofc_dataset.h5
├── inputs/
│   └── parameters           # (n_samples, n_parameters) input parameters
├── outputs/
│   ├── current_density      # (n_samples, nx, ny, nz)
│   ├── overpotential        # (n_samples, nx, ny, nz)
│   ├── temperature          # (n_samples, nx, ny, nz)
│   ├── von_mises_stress     # (n_samples, nx, ny, nz)
│   ├── strain_xx, yy, zz, xy, xz, yz  # (n_samples, nx, ny, nz) each
│   ├── displacement_u, v, w # (n_samples, nx, ny, nz) each
│   ├── c_H2                 # (n_samples, nx, ny, nz)
│   └── c_H2O                # (n_samples, nx, ny, nz)
└── metadata/
    ├── parameter_names      # List of parameter names
    ├── grid_resolution      # Grid dimensions
    ├── n_samples            # Number of samples
    └── statistics/          # Statistical summaries for each field
```

## Loading the Dataset

### Python Example

```python
import h5py
import numpy as np

# Load dataset
with h5py.File('sofc_dataset/sofc_dataset.h5', 'r') as f:
    # Get input parameters
    inputs = f['inputs/parameters'][:]  # Shape: (n_samples, n_parameters)
    
    # Get output fields
    temperatures = f['outputs/temperature'][:]  # Shape: (n_samples, nx, ny, nz)
    current_densities = f['outputs/current_density'][:]
    stresses = f['outputs/von_mises_stress'][:]
    
    # Get metadata
    param_names = [name.decode() for name in f['metadata/parameter_names'][:]]
    grid_res = tuple(f['metadata/grid_resolution'][:])
    n_samples = int(f['metadata/n_samples'][()])
    
    print(f"Dataset contains {n_samples} samples")
    print(f"Grid resolution: {grid_res}")
    print(f"Input parameters: {len(param_names)}")
    
    # Get statistics
    temp_mean = f['metadata/statistics/temperature/mean'][()]
    temp_std = f['metadata/statistics/temperature/std'][()]
    
    print(f"Temperature: mean={temp_mean:.2f} K, std={temp_std:.2f} K")
```

### Using with PyTorch/TensorFlow

```python
import torch
import h5py

# Load data as PyTorch tensors
with h5py.File('sofc_dataset/sofc_dataset.h5', 'r') as f:
    inputs = torch.tensor(f['inputs/parameters'][:])
    temperatures = torch.tensor(f['outputs/temperature'][:])
    
    # Use for training...
```

## Physics Models

The simulator implements simplified but physically consistent models:

1. **Electrochemistry**: Butler-Volmer kinetics with temperature-dependent exchange currents
2. **Thermal Transport**: Conduction, convection, and reaction heat generation
3. **Mechanics**: Linear elasticity with thermal expansion (Hooke's law)
4. **Species Transport**: Diffusion and convection with electrochemical consumption/production

## Parameter Sampling

The dataset uses **Latin Hypercube Sampling (LHS)** to efficiently explore the parameter space. This ensures good coverage of the input parameter space while maintaining reasonable computational cost.

## Computational Considerations

- **Grid Resolution**: Higher resolution (e.g., 80×80×50) provides more detailed field data but increases computation time
- **Number of Samples**: More samples provide better coverage but take longer to generate
- **Storage**: Each sample with grid 50×50×30 and ~15 output fields requires approximately 5-10 MB (compressed)
- **Generation Time**: Approximately 1-5 seconds per sample depending on grid resolution

## Citation

If you use this dataset generator, please cite:

```
Physics-Informed Data-Driven Modeling of SOFC Thermo-Mechanics 
for Real-Time Performance and Stress Prediction
```

## License

This code is provided for research purposes.

## Contact

For questions or issues, please refer to the project repository or contact the development team.