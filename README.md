# Welding Parameters Dataset for ML-Driven Inverse Design

## Overview

This comprehensive dataset is designed for machine learning-driven inverse design of welding parameters, specifically targeting battery manufacturing applications. The dataset contains **10,000 samples** with realistic welding process parameters, characterization metrics, and performance validation data.

## Dataset Structure

The dataset is divided into three core components:

### 1. Input Parameters (Design Space) - 28 Features
**What we can control in the welding process**

| Category | Parameter | Unit | Description |
|----------|-----------|------|-------------|
| **Base Materials** | Anode Material | - | Copper, Aluminum, Steel, Nickel, Titanium |
| | Cathode Material | - | Copper, Aluminum, Steel, Nickel, Titanium |
| | Tab Thickness | µm | Critical for heat dissipation (50-500 µm) |
| | Surface Finish | - | As_received, Polished, Rough, Oxidized, etc. |
| | Coating | - | None, Zinc, Nickel, Tin, Silver, Gold, etc. |
| **Welding Process** | Welding Technique | - | USW, Laser, Resistance Spot, Friction Stir |
| | Power | W | Peak power or pulse energy |
| | Amplitude | µm | Vibration amplitude (USW) |
| | Force/Pressure | N | Clamping force |
| | Time | s | Weld duration |
| | Speed | mm/s | Welding speed (Laser) |
| | Pulse Frequency | Hz | Pulse frequency (Laser) |
| | Current | A | Welding current (Resistance) |
| | Voltage | V | Welding voltage (Resistance) |
| | Rotation Speed | RPM | Tool rotation (Friction Stir) |
| | Travel Speed | mm/s | Tool travel (Friction Stir) |
| | Tool Diameter | mm | Tool size (Friction Stir) |
| | Pulse Duration | ms | Pulse duration (Laser) |
| | Spot Size | mm | Laser spot size |
| **Environmental** | Pre-heat Temperature | °C | Sample temperature before welding |
| | Humidity | % | Environmental humidity |
| | Atmospheric Pressure | kPa | Environmental pressure |
| | Weld Position | - | Flat, Horizontal, Vertical, Overhead |
| | Joint Type | - | Butt, Lap, T-Joint, Corner, Edge |
| | Joint Geometry | - | Square, V-Groove, U-Groove, J-Groove |
| | Cleaning Method | - | None, Acetone, Alcohol, Ultrasonic, Plasma |
| | Pre-treatment | - | None, Annealing, Stress Relief, Solution Treatment |

### 2. Characterization & Quality Metrics (Forward Problem Outputs) - 16 Features
**How we measure weld quality immediately after joining**

| Parameter | Unit | Description |
|-----------|------|-------------|
| Nugget Diameter | mm | Weld nugget size |
| Penetration Depth | mm | Weld penetration depth |
| Weld Width | mm | Total weld width |
| HAZ Width | mm | Heat affected zone width |
| Contact Resistance | mΩ | Electrical contact resistance |
| Electrical Conductivity | S/m | Electrical conductivity |
| Thermal Conductivity | W/m·K | Thermal conductivity |
| Shear Strength | MPa | Shear strength of weld |
| Tensile Strength | MPa | Tensile strength of weld |
| Hardness | HV | Vickers hardness |
| Porosity | % | Porosity percentage |
| Crack Density | /mm² | Cracks per unit area |
| Microstructure Score | 0-100 | Microstructure quality score |
| Bond Quality Index | 0-100 | Overall bond quality |
| Weld Quality Class | A/B/C | Quality classification |

### 3. Performance & Validation Metrics (Inverse Design Targets) - 18 Features
**How the weld performs under extreme temperature cycling**

| Parameter | Unit | Description |
|-----------|------|-------------|
| Min Temperature | °C | Minimum cycling temperature |
| Max Temperature | °C | Maximum cycling temperature |
| Cycle Count | - | Number of thermal cycles |
| Ramp Rate | °C/min | Temperature ramp rate |
| Thermal Stress | MPa | Calculated thermal stress |
| Fatigue Life | cycles | Predicted cycles to failure |
| Resistance Change | % | Electrical resistance change |
| Strength Retention | % | Mechanical strength retention |
| Failure Mode | - | Electrical/Mechanical/Thermal_Fatigue |
| MTTF | hours | Mean time to failure |
| Reliability (95%) | % | 95% reliability estimate |
| Thermal Resistance | K/W | Thermal resistance |
| Thermal Resistance Change | % | Thermal resistance change |
| Creep Resistance | hours | Time to 1% strain at 80°C |
| Corrosion Resistance | 0-100 | Corrosion resistance index |
| Performance Score | 0-100 | Overall performance score |
| Pass/Fail | PASS/FAIL | Performance classification |

## Files Generated

### Data Files
- `welding_dataset_input_parameters.csv` - Input parameters (10,000 × 28)
- `welding_dataset_characterization_metrics.csv` - Characterization metrics (10,000 × 16)
- `welding_dataset_performance_metrics.csv` - Performance metrics (10,000 × 18)
- `welding_dataset_complete.csv` - Combined dataset (10,000 × 62)
- `welding_dataset_complete.json` - JSON format with metadata
- `welding_dataset_complete.h5` - HDF5 format for efficient storage

### Analysis Files
- `welding_dataset_analysis.json` - Statistical analysis report
- `correlation_heatmap.png` - Feature correlation visualization
- `strong_correlations.csv` - Strong correlation pairs (>0.5)
- `material_performance_analysis.csv` - Material-specific performance
- `material_analysis.png` - Material performance visualizations
- `process_optimization_analysis.png` - Process parameter effects
- `ml_readiness_report.json` - ML modeling recommendations
- `welding_dataset_dashboard.html` - Interactive Plotly dashboard

## Key Features

### Realistic Data Generation
- **Material Properties**: Based on real material databases with accurate thermal, electrical, and mechanical properties
- **Process Correlations**: Realistic relationships between process parameters and outcomes
- **Noise and Variability**: Appropriate experimental noise and measurement uncertainty
- **Physical Constraints**: Process parameters within realistic operating ranges

### Welding Techniques Covered
1. **Ultrasonic Welding (USW)**: Power, amplitude, force, time parameters
2. **Laser Welding**: Power, speed, pulse frequency, duration, spot size
3. **Resistance Spot Welding**: Current, voltage, force, time
4. **Friction Stir Welding**: Rotation speed, travel speed, force, tool diameter

### Material Combinations
- **Anode Materials**: Copper, Aluminum, Steel, Nickel, Titanium
- **Cathode Materials**: Copper, Aluminum, Steel, Nickel, Titanium
- **Surface Treatments**: 10 different surface finishes and coatings

### Quality Metrics
- **Immediate Quality**: Nugget size, strength, hardness, porosity
- **Electrical Performance**: Contact resistance, conductivity
- **Thermal Performance**: Thermal conductivity, heat affected zone
- **Long-term Performance**: Fatigue life, reliability, corrosion resistance

## Usage Examples

### Loading the Dataset
```python
import pandas as pd

# Load individual components
input_df = pd.read_csv('welding_dataset_input_parameters.csv')
char_df = pd.read_csv('welding_dataset_characterization_metrics.csv')
perf_df = pd.read_csv('welding_dataset_performance_metrics.csv')

# Load combined dataset
combined_df = pd.read_csv('welding_dataset_complete.csv')
```

### Basic Analysis
```python
# Material performance analysis
material_perf = combined_df.groupby(['anode_material', 'cathode_material']).agg({
    'bond_quality_index': 'mean',
    'performance_score': 'mean',
    'fatigue_life_cycles': 'mean'
})

# Process parameter effects
usw_data = combined_df[combined_df['welding_technique'] == 'Ultrasonic_Welding']
correlation = usw_data[['power_w', 'amplitude_um', 'force_n', 'bond_quality_index']].corr()
```

### ML Model Training
```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# Prepare features and targets
X = combined_df[['power_w', 'amplitude_um', 'force_n', 'time_s']].fillna(0)
y = combined_df['bond_quality_index']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
score = model.score(X_test, y_test)
print(f"Model R² score: {score:.3f}")
```

## Statistical Summary

### Dataset Overview
- **Total Samples**: 10,000
- **Input Features**: 28
- **Characterization Features**: 16
- **Performance Features**: 18
- **Total Features**: 62
- **Missing Values**: <1%

### Quality Distribution
- **Class A Welds**: ~25% (bond_quality_index > 80)
- **Class B Welds**: ~50% (bond_quality_index 60-80)
- **Class C Welds**: ~25% (bond_quality_index < 60)

### Performance Distribution
- **Pass Rate**: ~70% (performance_score > 70)
- **Fail Rate**: ~30% (performance_score ≤ 70)

## Applications

### 1. Inverse Design
- **Input**: Desired performance targets (fatigue life, reliability, etc.)
- **Output**: Optimal process parameters
- **Methods**: Neural networks, genetic algorithms, Bayesian optimization

### 2. Quality Prediction
- **Input**: Process parameters
- **Output**: Predicted weld quality and performance
- **Methods**: Regression models, ensemble methods

### 3. Process Optimization
- **Input**: Material constraints and quality requirements
- **Output**: Optimal welding parameters
- **Methods**: Multi-objective optimization, Pareto analysis

### 4. Failure Analysis
- **Input**: Process parameters and environmental conditions
- **Output**: Predicted failure modes and reliability
- **Methods**: Classification models, survival analysis

## Technical Specifications

### Data Generation
- **Random Seed**: 42 (reproducible)
- **Noise Level**: Realistic experimental uncertainty
- **Correlation Structure**: Based on physical relationships
- **Outlier Handling**: Natural process variation included

### File Formats
- **CSV**: Human-readable, compatible with most tools
- **JSON**: Structured format with metadata
- **HDF5**: Efficient storage for large datasets
- **HTML**: Interactive visualizations

### Validation
- **Physical Constraints**: All parameters within realistic ranges
- **Statistical Validation**: Proper correlation structure
- **Domain Knowledge**: Based on welding literature and expertise

## Citation

If you use this dataset in your research, please cite:

```
Welding Parameters Dataset for ML-Driven Inverse Design
Generated for battery manufacturing applications
Dataset Version: 1.0
Generated: 2024
```

## License

This dataset is provided for research and educational purposes. Please ensure appropriate attribution when using in publications or commercial applications.

## Contact

For questions about the dataset or to request additional features, please refer to the documentation or create an issue in the repository.

---

**Note**: This dataset is generated using realistic physical models and statistical relationships. While it provides a solid foundation for ML model development, validation with experimental data is recommended for production applications.