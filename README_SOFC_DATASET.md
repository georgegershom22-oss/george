# SOFC High-Fidelity Numerical Dataset

## Overview

This dataset contains high-fidelity 3D finite element analysis (FEA) simulation data for Solid Oxide Fuel Cell (SOFC) systems, designed for physics-informed machine learning applications in thermo-mechanical modeling.

**Thesis Topic:** Physics-Informed Data-Driven Modeling of SOFC Thermo-Mechanics for Real-Time Performance and Stress Prediction

## Dataset Description

### Purpose
This synthetic dataset is generated from multi-physics computational models to train data-driven models for real-time SOFC performance and stress prediction. It captures the complex coupling between electrochemical, thermal, mechanical, and species transport phenomena in SOFCs.

### Dataset Structure

The dataset is stored in HDF5 format (`sofc_dataset.h5`) with the following structure:

```
sofc_dataset.h5
├── inputs/
│   ├── parameters [n_samples × n_parameters]
│   └── parameter_names [n_parameters]
├── outputs/
│   ├── current_density [n_samples × nx × ny × nz]
│   ├── overpotential [n_samples × nx × ny × nz]
│   ├── temperature [n_samples × nx × ny × nz]
│   ├── von_mises_stress [n_samples × nx × ny × nz]
│   ├── strain [n_samples × nx × ny × nz]
│   ├── displacement [n_samples × nx × ny × nz]
│   ├── H2_concentration [n_samples × nx × ny × nz]
│   └── H2O_concentration [n_samples × nx × ny × nz]
└── mesh/
    ├── x [nx]
    ├── y [ny]
    └── z [nz]
```

## Input Parameters (Features)

### Operating Conditions
- **Voltage**: 0.6 - 0.9 V
- **Current Density**: 3,000 - 12,000 A/m²
- **Fuel Flow Rate**: 5×10⁻⁶ - 2×10⁻⁵ kg/s
- **Air Flow Rate**: 5×10⁻⁵ - 2×10⁻⁴ kg/s
- **Fuel Inlet Temperature**: 873 - 1073 K (600-800°C)
- **Air Inlet Temperature**: 873 - 1073 K

### Material Properties

#### Anode (Ni-YSZ)
- **Porosity**: 0.25 - 0.45
- **Permeability**: 10⁻¹² - 10⁻¹⁰ m²
- **Young's Modulus**: 30 - 80 GPa
- **Coefficient of Thermal Expansion (CTE)**: 10 - 13 ×10⁻⁶ K⁻¹

#### Electrolyte (YSZ)
- **Porosity**: 0.0 - 0.05
- **Young's Modulus**: 180 - 220 GPa
- **CTE**: 10 - 11 ×10⁻⁶ K⁻¹

#### Cathode (LSM/LSCF)
- **Porosity**: 0.25 - 0.45
- **Permeability**: 10⁻¹² - 10⁻¹⁰ m²
- **Young's Modulus**: 40 - 100 GPa
- **CTE**: 11 - 14 ×10⁻⁶ K⁻¹

### Geometric Parameters
- **Anode Thickness**: 1.3 - 1.7 mm
- **Electrolyte Thickness**: 0.2 - 0.4 mm
- **Cathode Thickness**: 1.0 - 1.4 mm
- **Active Area**: 0.008 - 0.012 m² (80-120 cm²)

### Conductivities
- **Ionic Conductivity**: 1×10³ - 1×10⁴ S/m
- **Electronic Conductivity**: 1×10⁴ - 1×10⁶ S/m

## Output Fields (Labels)

### Electrochemical Fields
- **Current Density Distribution**: Local current density in 3D space [A/m²]
- **Overpotential Distribution**: Activation and ohmic overpotentials [V]

### Thermal Fields
- **Temperature Distribution**: 3D temperature field T(x,y,z) [K]

### Mechanical Fields
- **Von Mises Stress**: Equivalent stress from thermo-mechanical loading [Pa]
- **Strain**: Total strain including thermal expansion [-]
- **Displacement**: Total displacement magnitude from thermal expansion [m]

### Species Transport Fields
- **H₂ Concentration**: Hydrogen molar concentration in anode [mol/m³]
- **H₂O Concentration**: Water vapor molar concentration in anode [mol/m³]

## Physics Models

The dataset incorporates the following physics-based models:

1. **Electrochemistry**: Butler-Volmer kinetics for charge transfer reactions
2. **Thermal Transport**: Heat generation from electrochemical reactions and joule heating
3. **Mechanical**: Thermo-mechanical stress from thermal expansion and CTE mismatch
4. **Species Transport**: Mass conservation with electrochemical consumption/production

## Sampling Method

**Latin Hypercube Sampling (LHS)** is used to efficiently explore the high-dimensional parameter space with good coverage and minimal clustering.

## Usage

### Loading the Dataset

```python
import h5py
import numpy as np

# Load dataset
with h5py.File('sofc_dataset/sofc_dataset.h5', 'r') as f:
    # Load input parameters
    params = f['inputs/parameters'][:]
    param_names = [name.decode() for name in f['inputs/parameter_names'][:]]
    
    # Load output fields (example: temperature)
    temperature = f['outputs/temperature'][:]
    
    # Load mesh coordinates
    x = f['mesh/x'][:]
    y = f['mesh/y'][:]
    z = f['mesh/z'][:]

print(f"Dataset shape: {params.shape}")
print(f"Temperature field shape: {temperature.shape}")
```

### Example: Training a Neural Network

```python
import h5py
from sklearn.model_selection import train_test_split
import tensorflow as tf

# Load dataset
with h5py.File('sofc_dataset/sofc_dataset.h5', 'r') as f:
    X = f['inputs/parameters'][:]
    y_temp = f['outputs/temperature'][:]
    y_stress = f['outputs/von_mises_stress'][:]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y_temp, test_size=0.2, random_state=42)

# Build model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_shape=(X.shape[1],)),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dense(np.prod(y_temp.shape[1:]))
])

model.compile(optimizer='adam', loss='mse')
model.fit(X_train, y_train.reshape(len(y_train), -1), 
          epochs=100, validation_split=0.2)
```

## File Structure

```
sofc_dataset/
├── sofc_dataset.h5           # Main HDF5 dataset file
├── metadata.json             # Dataset metadata and configuration
└── dataset_summary.json      # Statistical summary of inputs/outputs
```

## Dataset Statistics

- **Number of Samples**: 100 (configurable)
- **Grid Resolution**: 50 × 50 × 20 (50,000 points per sample)
- **Total Data Points**: 5,000,000
- **Input Parameters**: 24
- **Output Fields**: 8 (3D fields)

## Applications

This dataset is suitable for:

1. **Physics-Informed Neural Networks (PINNs)** for SOFC modeling
2. **Reduced-Order Modeling (ROM)** for real-time prediction
3. **Multi-fidelity modeling** combining simulation and experimental data
4. **Uncertainty quantification** in SOFC operation
5. **Design optimization** of SOFC geometries and materials
6. **Digital twin development** for SOFC systems

## Citation

If you use this dataset, please cite:

```
@dataset{sofc_high_fidelity_2025,
  title={High-Fidelity SOFC Multi-Physics Simulation Dataset},
  author={Generated for Physics-Informed Data-Driven Modeling},
  year={2025},
  description={3D FEA dataset for SOFC thermo-mechanical modeling}
}
```

## Generation Details

- **Generation Date**: See metadata.json
- **Computational Model**: Coupled multi-physics FEA/CFD
- **Sampling Method**: Latin Hypercube Sampling
- **Grid Type**: Regular Cartesian grid
- **Coordinate System**: Cartesian (x, y, z)

## Contact & Support

For questions about the dataset or to report issues, please refer to the thesis documentation.

## License

This dataset is generated for research purposes as part of the thesis:
"Physics-Informed Data-Driven Modeling of SOFC Thermo-Mechanics for Real-Time Performance and Stress Prediction"
