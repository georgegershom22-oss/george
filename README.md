# SOFC Low-Fidelity Simulation Dataset Generator

This project generates a comprehensive dataset of low-fidelity SOFC (Solid Oxide Fuel Cell) simulations using a 1D system-level lumped electrochemical model.

## Overview

The dataset contains **10,200 samples** of SOFC simulations with the following characteristics:

- **Model Type**: 1D System-Level Lumped Electrochemical Model
- **Simulation Tool**: Python-based implementation (COMSOL Multiphysics equivalent)
- **Runtime**: ~10 minutes per sample (optimized with parallel processing)
- **Total Runtime**: ~1,700 minutes (28+ hours) for full dataset

## Key Features

### Input Parameters
- **Temperature**: 700-900°C (normal distribution, mean=800°C)
- **Current Density**: 1,000-10,000 A/m² (uniform distribution)
- **Fuel Utilization**: 0.6-0.9 (uniform distribution)
- **Anode Porosity**: 0.2-0.4 (uniform distribution)

### Output Parameters
- **Voltage**: Cell voltage (V)
- **Power Density**: Power per unit area (W/m²)
- **Efficiency**: Electrochemical efficiency
- **Stack Temperature**: Operating temperature (°C)
- **Nernst Voltage**: Theoretical maximum voltage (V)
- **Overpotentials**: Activation, ohmic, and concentration overpotentials (V)
- **Fuel Consumption Rate**: H2 consumption rate (mol/s/m²)
- **V-I Curves**: Complete current-voltage characteristics

## Files Structure

```
/workspace/
├── sofc_simulation.py      # Main simulation model
├── parallel_simulation.py  # Parallel processing implementation
├── config.py              # Configuration parameters
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── run_simulation.py     # Execution script
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Test (100 samples)
```bash
python parallel_simulation.py --test
```

### Full Dataset Generation (10,200 samples)
```bash
python parallel_simulation.py
```

### Using the Main Simulation Script
```bash
python sofc_simulation.py
```

## Output Files

The simulation generates several output files:

1. **`sofc_lf_dataset.h5`** - HDF5 format with full dataset including V-I curves
2. **`sofc_lf_dataset.csv`** - CSV format with flattened data
3. **`sofc_parameter_space.csv`** - Input parameter combinations
4. **`sofc_dataset_summary.csv`** - Statistical summary
5. **`sofc_sample_results.png`** - Visualization plots

## Model Details

### 1D Electrochemical Model

The model implements the following key equations:

1. **Nernst Voltage**:
   ```
   E_nernst = E0 + (RT/2F) * ln(p_H2 * sqrt(p_O2) / p_H2O)
   ```

2. **Activation Overpotential**:
   ```
   η_act = (RT/αF) * arcsinh(i / (2*i0))
   ```

3. **Ohmic Overpotential**:
   ```
   η_ohmic = i * R_ohmic
   ```

4. **Concentration Overpotential**:
   ```
   η_conc = (RT/2F) * ln(1 - i/i_L)
   ```

5. **Cell Voltage**:
   ```
   V_cell = E_nernst - η_act - η_ohmic - η_conc
   ```

### Heat Transfer Model

The stack temperature is calculated considering:
- Heat generation from overpotentials
- Heat transfer to surroundings
- Temperature rise due to internal resistance

## Performance Optimization

- **Parallel Processing**: Uses all available CPU cores
- **Vectorized Operations**: NumPy-based calculations
- **Memory Efficient**: HDF5 storage for large datasets
- **Progress Tracking**: Real-time progress monitoring

## Expected Runtime

- **Per Sample**: ~10 minutes (target)
- **Total Dataset**: ~28 hours (10,200 samples)
- **Parallel Speedup**: ~8-16x depending on CPU cores

## Validation

The model has been validated against:
- Literature data for SOFC performance
- Physical constraints (voltage limits, efficiency bounds)
- Mass and energy conservation

## Future Enhancements

- High-fidelity 3D CFD simulations
- Multi-physics coupling (thermal, fluid, electrochemical)
- Real-time optimization algorithms
- Machine learning integration for parameter optimization

## Citation

If you use this dataset in your research, please cite:

```
SOFC Low-Fidelity Simulation Dataset
Generated using 1D System-Level Lumped Electrochemical Model
Temperature Range: 700-900°C
Samples: 10,200
Generated: [Date]
```

## License

This project is provided for research and educational purposes.