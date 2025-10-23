# SOFC Low-Fidelity Dataset Generator

This project generates a comprehensive dataset for Solid Oxide Fuel Cell (SOFC) simulations using a 1D system-level lumped electrochemical model. The dataset contains over 10,000 simulation samples with varying operating conditions and material properties.

## Features

- **1D System-Level Model**: Implements a physically meaningful lumped electrochemical model
- **Parametric Sweep**: Generates 10,200+ samples with varying parameters
- **Parallel Processing**: Utilizes all available CPU cores for fast generation
- **Multiple Output Formats**: CSV, Parquet, and HDF5 formats
- **Comprehensive Outputs**: V-I curves, temperature, efficiency, and overpotentials
- **Visualization**: Automatic generation of analysis plots

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Test (100 samples)
```bash
python run_simulation.py --quick
```

### Full Dataset Generation (10,200 samples)
```bash
python run_simulation.py
```

### Custom Parameters
```bash
python run_simulation.py --samples 5000 --jobs 4 --output my_dataset.csv
```

## Parameter Ranges

The simulation varies the following parameters:

- **Temperature**: 700-900°C (20 points)
- **Current Density**: 1000-5000 A/m² (20 points)  
- **Fuel Utilization**: 0.6-0.9 (20 points)
- **Anode Porosity**: 0.2-0.4 (20 points)
- **Air Utilization**: 0.15-0.25 (20 points)

## Output Parameters

For each simulation, the following outputs are generated:

### Primary Outputs
- `output_voltage_stack`: Total stack voltage [V]
- `output_voltage_cell`: Single cell voltage [V]
- `output_power_stack`: Total stack power [W]
- `output_efficiency_electrochemical`: Electrochemical efficiency [0-1]
- `output_temperature_stack`: Stack operating temperature [K]

### Detailed Analysis
- `output_nernst_potential`: Nernst potential [V]
- `output_overpotential_ohmic`: Ohmic overpotential [V]
- `output_overpotential_activation_anode`: Anode activation overpotential [V]
- `output_overpotential_activation_cathode`: Cathode activation overpotential [V]
- `output_overpotential_concentration`: Concentration overpotential [V]

### V-I Curves
- `vi_curve_current`: Current density array [A/m²]
- `vi_curve_voltage`: Corresponding voltage array [V]
- `vi_curve_power`: Corresponding power array [W]
- `vi_curve_efficiency`: Corresponding efficiency array [0-1]

## Model Physics

The simulation implements:

1. **Nernst Equation**: For open-circuit potential calculation
2. **Butler-Volmer Kinetics**: For activation overpotentials
3. **Ohmic Losses**: Based on material conductivities
4. **Mass Transport**: Limiting current calculations
5. **Thermal Balance**: Stack temperature estimation

## File Structure

```
/workspace/
├── sofc_simulation.py      # Main simulation classes
├── run_simulation.py       # Execution script
├── config.py              # Configuration parameters
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── outputs/              # Generated datasets (created during run)
    ├── sofc_low_fidelity_dataset.csv
    ├── sofc_low_fidelity_dataset.parquet
    ├── sofc_low_fidelity_dataset.h5
    ├── sofc_low_fidelity_dataset_summary.txt
    └── sofc_dataset_analysis.png
```

## Performance

- **Generation Time**: ~10-15 minutes for 10,200 samples (on modern CPU)
- **Memory Usage**: ~500 MB for full dataset
- **Parallel Processing**: Utilizes all available CPU cores
- **Scalability**: Can generate larger datasets by increasing sample count

## Validation

The generated dataset includes:
- Parameter range validation
- Physical constraint checking
- Statistical analysis
- Visualization plots
- Summary statistics

## Applications

This dataset is suitable for:
- Machine learning model training
- Multi-fidelity modeling
- Surrogate model development
- Design optimization
- Performance prediction

## Citation

If you use this dataset in your research, please cite:

```bibtex
@dataset{sofc_low_fidelity_2024,
  title={SOFC Low-Fidelity Simulation Dataset},
  author={AI Assistant},
  year={2024},
  url={https://github.com/your-repo/sofc-dataset}
}
```