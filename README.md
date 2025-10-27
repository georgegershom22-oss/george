# ML-Driven Inverse Design of Welding Parameters Dataset

## Overview
This comprehensive dataset is designed for machine learning-driven inverse design of welding parameters, focusing on the relationship between input welding parameters and performance under extreme temperature cycling conditions.

## Dataset Structure

### Part 1: Input Parameters (Features for ML Model)
The experimental/simulation matrix includes:

#### Base Materials
- **Anode Material**: Copper (Cu), Aluminum (Al), Nickel (Ni), Titanium (Ti), Steel
- **Cathode Material**: Same material options as anode
- **Tab Thickness**: 50-500 μm (critical for heat dissipation)
- **Surface Finish/Coating**: Polished, Rough, Coated, Anodized, Plated

#### Welding Process Parameters
- **Welding Technique**: USW, Laser, Resistance Spot, Friction Stir, Electron Beam
- **Power**: 100-5000 W (peak power for USW or pulse energy for laser)
- **Amplitude**: 10-100 μm (for USW vibration amplitude)
- **Force/Pressure**: 100-5000 N (clamping force)
- **Time**: 10-1000 ms (weld duration)
- **Speed**: 1-50 mm/s (for laser welding speed)
- **Pulse Frequency**: 1-1000 Hz (for laser)

#### Environmental
- **Pre-heat Temperature**: 20-300°C (simulates hot manufacturing environment)

### Part 2: Characterization & Quality Metrics (Forward Problem Outputs)
Immediate post-welding quality measurements:

- **Material Compatibility**: 0-1 score based on thermal and mechanical properties
- **Weld Strength**: MPa (depends on force, time, and material properties)
- **Contact Resistance**: Ohms (affected by surface finish, force, and materials)
- **Weld Width**: mm (depends on power, time, and technique)
- **Penetration Depth**: mm (depends on power, speed, and materials)
- **Porosity**: Percentage (depends on technique, environment, and materials)

### Part 3: Performance & Validation Metrics (Inverse Design Targets)
Ultimate performance under extreme temperature cycling:

- **Thermal Cycles to Failure**: Number of cycles before failure
- **Resistance Degradation Rate**: Ohms per cycle
- **Strength Retention**: Percentage after cycling
- **Primary Failure Mode**: Thermal Fatigue, Mechanical Fatigue, Corrosion, Delamination

## Dataset Generation

The dataset is generated using realistic physical relationships between parameters:

1. **Material Compatibility**: Based on thermal conductivity mismatch and melting point differences
2. **Weld Strength**: Influenced by material yield strength, welding force, time, and compatibility
3. **Contact Resistance**: Affected by surface finish, clamping force, and material conductivity
4. **Performance Metrics**: Calculated based on material compatibility, weld quality, and technique

## Usage

### Installation
```bash
pip install -r requirements.txt
```

### Generate Dataset
```bash
python welding_dataset_generator.py
```

This will create:
- `welding_dataset.csv`: The complete dataset (10,000 samples)
- `welding_dataset_analysis.png`: Comprehensive analysis plots

### Dataset Statistics
- **Total Samples**: 10,000
- **Total Features**: 22
- **Input Parameters**: 12
- **Quality Metrics**: 6
- **Performance Metrics**: 4

## Key Features

### Realistic Physical Relationships
- Material properties based on real material data
- Welding parameter effects based on physical principles
- Performance degradation models based on fatigue and thermal cycling

### Comprehensive Coverage
- Multiple welding techniques
- Various material combinations
- Wide parameter ranges
- Realistic environmental conditions

### ML-Ready Format
- Clean, structured data
- Proper scaling and normalization
- Balanced class distributions
- Rich feature interactions

## Applications

This dataset is ideal for:
- **Inverse Design**: Predicting optimal welding parameters for desired performance
- **Quality Prediction**: Estimating weld quality from process parameters
- **Failure Analysis**: Understanding failure modes and their causes
- **Process Optimization**: Finding parameter combinations for specific requirements
- **Material Selection**: Choosing optimal material combinations

## Technical Details

### Data Generation Algorithm
1. **Input Parameter Generation**: Random sampling within realistic ranges
2. **Quality Metric Calculation**: Physics-based relationships between inputs and outputs
3. **Performance Metric Calculation**: Long-term behavior under thermal cycling
4. **Noise Addition**: Realistic measurement noise (5% standard deviation)

### Validation
- Material property data from literature
- Welding parameter ranges from industry standards
- Performance models based on fatigue and thermal cycling research

## File Structure
```
├── welding_dataset_generator.py    # Main dataset generation script
├── requirements.txt                # Python dependencies
├── README.md                      # This file
├── welding_dataset.csv            # Generated dataset (after running)
└── welding_dataset_analysis.png   # Analysis plots (after running)
```

## Citation
If you use this dataset in your research, please cite:
```
ML-Driven Inverse Design of Welding Parameters Dataset
Generated for research in welding process optimization and quality prediction
```

## License
This dataset is provided for research and educational purposes. Please ensure proper attribution when using in publications or commercial applications.