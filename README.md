# Welding Dataset for ML-Driven Inverse Design

## Overview

This repository contains a comprehensive dataset for machine learning-driven inverse design of welding parameters, specifically focused on extreme-temperature cycling performance. The dataset is designed to enable the development of ML models that can predict optimal welding parameters to achieve target performance metrics.

## Dataset Structure

The dataset is divided into three core components:

### 1. Input Parameters (Design Space)
Parameters that can be controlled in the welding process:

- **Base Materials**: Anode and cathode materials (Cu, Al, Ni, Ti)
- **Tab Thickness**: Critical for heat dissipation (50-500 µm)
- **Surface Finish**: Affects contact resistance and bondability
- **Welding Technique**: USW, Laser, or Resistance welding
- **Process Parameters**: Power, force, time, amplitude, speed, etc.
- **Environmental**: Pre-heat temperature

### 2. Characterization & Quality Metrics (Forward Problem Outputs)
Immediate quality measurements after welding:

- Heat input and contact resistance
- Weld strength and microhardness
- Heat-affected zone size and porosity
- Weld geometry (width, penetration depth)
- Electrical and thermal resistance

### 3. Performance & Validation Metrics (Inverse Design Targets)
Long-term performance under extreme conditions:

- Thermal cycles to failure
- High-temperature strength retention
- Fatigue life and creep resistance
- Interfacial stability
- Thermal expansion mismatch

## Files

- `welding_dataset_generator.py`: Main dataset generation script
- `dataset_analyzer.py`: Comprehensive analysis and visualization tools
- `inverse_design_ml.py`: Machine learning models for inverse design
- `welding_dataset_analysis.ipynb`: Interactive Jupyter notebook
- `welding_dataset.csv`: Generated dataset (CSV format)
- `welding_dataset.xlsx`: Generated dataset (Excel format with multiple sheets)

## Key Features

### Physics-Based Relationships
- Realistic material property variations
- Heat transfer and thermal expansion calculations
- Contact resistance modeling
- Fatigue and creep behavior

### Comprehensive Coverage
- 15,000+ samples across multiple material combinations
- Three welding techniques with technique-specific parameters
- Realistic noise and measurement variations
- Balanced distribution across parameter space

### ML-Ready Format
- Clean, structured data with minimal missing values
- Proper encoding of categorical variables
- Normalized numerical features
- Clear separation of inputs and targets

## Usage

### Generate Dataset
```bash
python welding_dataset_generator.py
```

### Analyze Dataset
```bash
python dataset_analyzer.py welding_dataset.csv
```

### Train ML Models
```bash
python inverse_design_ml.py welding_dataset.csv
```

### Interactive Analysis
```bash
jupyter notebook welding_dataset_analysis.ipynb
```

## Dataset Statistics

- **Total Samples**: 15,000
- **Input Parameters**: 14 features
- **Characterization Metrics**: 10 features
- **Performance Metrics**: 8 features
- **Welding Techniques**: 3 (USW, Laser, Resistance)
- **Material Combinations**: 16 unique pairs
- **Data Completeness**: >95%

## Material Properties

The dataset includes realistic material properties for:
- **Copper (Cu)**: High thermal/electrical conductivity
- **Aluminum (Al)**: Lightweight, good conductivity
- **Nickel (Ni)**: High-temperature stability
- **Titanium (Ti)**: Excellent strength-to-weight ratio

## Welding Techniques

### Ultrasonic Welding (USW)
- Power range: 50-2000 W
- Amplitude: 10-100 µm
- Force: 50-500 N
- Time: 0.1-2.0 s

### Laser Welding
- Power range: 100-5000 W
- Speed: 1-50 mm/s
- Pulse frequency: 1-1000 Hz
- Pulse energy: 0.1-10 J

### Resistance Spot Welding
- Power range: 200-3000 W
- Force: 100-1000 N
- Time: 0.05-1.0 s
- Current: 1000-10000 A

## Performance Targets

The dataset is optimized for predicting:
- **Thermal Cycles to Failure**: 100-50,000 cycles
- **High-Temperature Strength**: 50-300 MPa
- **Fatigue Life**: 10^3-10^6 cycles
- **Interfacial Stability**: 0.1-1.0

## Machine Learning Applications

### Inverse Design
Given target performance metrics, predict optimal welding parameters:
- Process parameters (power, force, time)
- Material selection
- Surface preparation
- Environmental conditions

### Forward Prediction
Given welding parameters, predict:
- Immediate quality metrics
- Long-term performance
- Failure modes
- Optimization opportunities

### Multi-Objective Optimization
Balance competing objectives:
- Maximize thermal cycles to failure
- Minimize porosity
- Optimize electrical resistance
- Control heat-affected zone

## Dependencies

```
numpy>=1.21.0
pandas>=1.3.0
scipy>=1.7.0
scikit-learn>=1.0.0
matplotlib>=3.4.0
seaborn>=0.11.0
plotly>=5.0.0
openpyxl>=3.0.0
h5py>=3.1.0
xgboost>=1.5.0
lightgbm>=3.3.0
jupyter>=1.0.0
```

## Installation

```bash
pip install -r requirements.txt
```

## Citation

If you use this dataset in your research, please cite:

```bibtex
@dataset{welding_inverse_design_2024,
  title={Comprehensive Welding Dataset for ML-Driven Inverse Design},
  author={AI Assistant},
  year={2024},
  url={https://github.com/your-repo/welding-dataset}
}
```

## License

This dataset is provided under the MIT License. See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## Contact

For questions or support, please open an issue in the repository.