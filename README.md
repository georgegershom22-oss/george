# ML-Driven Inverse Design of Welding Parameters Dataset

## Overview

This comprehensive dataset is designed for machine learning-driven inverse design of welding parameters, with a specific focus on extreme temperature cycling performance. The dataset contains **15,000 samples** with realistic, physics-informed data covering three critical aspects of welding optimization.

## Dataset Structure

The dataset is divided into three core components:

### 1. Input Parameters (Design Space) - 20 Features
**What we can control in the welding process**

| Category | Parameter | Unit | Description |
|----------|-----------|------|-------------|
| **Base Materials** | Anode Material | - | Copper, Aluminum, Nickel, Titanium |
| | Cathode Material | - | Copper, Aluminum, Nickel, Titanium |
| | Tab Thickness | µm | Critical for heat dissipation (10-500 µm) |
| | Surface Finish | - | Polished, Rough, Anodized, Coated, Oxidized |
| **Welding Process** | Welding Technique | - | USW, Laser, Resistance Spot, Friction Stir |
| | Power | W | Peak power (100-15,000 W) |
| | Amplitude | µm | Vibration amplitude (USW only) |
| | Force/Pressure | N | Clamping force (10-10,000 N) |
| | Time | s | Weld duration (0.001-30 s) |
| | Speed | mm/s | Welding speed (Laser/Friction Stir) |
| | Pulse Frequency | Hz | Pulse frequency (Laser only) |
| **Environmental** | Preheat Temperature | °C | Sample temperature before welding |
| | Weld Angle | deg | Welding angle (0-45°) |
| | Overlap Ratio | - | Material overlap ratio (0.1-0.9) |
| | Atmosphere | - | Air, Argon, Nitrogen, Vacuum |
| **Derived Features** | Material Compatibility | - | Compatibility score (0-100) |
| | Process Intensity | - | Power × Time |
| | Energy Density | - | Power / Area approximation |
| | Thermal Mass | - | Thickness × Density × Specific Heat |

### 2. Characterization & Quality Metrics (Forward Problem) - 10 Features
**Immediate post-weld measurements**

| Metric | Unit | Range | Description |
|--------|------|-------|-------------|
| Weld Strength | MPa | 0-4,710 | Ultimate tensile strength of weld |
| Contact Resistance | Ω·m² | 2×10⁻⁹ - 2×10⁻⁶ | Electrical contact resistance |
| Weld Width | mm | 0.1-50 | Width of weld joint |
| Penetration | mm | 0.05-25 | Depth of weld penetration |
| Porosity | % | 0-20 | Percentage of voids in weld |
| Microhardness | HV | 50-1,000 | Vickers hardness of weld zone |
| HAZ Width | mm | 0.1-15 | Heat-affected zone width |
| Intermetallic Thickness | µm | 0-50 | Thickness of intermetallic compounds |
| Weld Quality Score | - | 44-100 | Overall quality assessment (0-100) |

### 3. Performance & Validation Metrics (Inverse Design Targets) - 11 Features
**Long-term thermal cycling performance**

| Metric | Unit | Range | Description |
|--------|------|-------|-------------|
| Thermal Cycles to Failure | cycles | 100-66,668 | Number of thermal cycles before failure |
| Max Operating Temperature | °C | 222-1,168 | Maximum safe operating temperature |
| Resistance Degradation Rate | Ω/cycle | 10⁻¹⁵ - 10⁻⁹ | Rate of resistance increase per cycle |
| Strength Retention | % | 50-100 | Percentage of strength retained after cycling |
| Failure Mode | - | 4 types | Predicted failure mechanism |
| Joint Thermal Conductivity | W/m·K | 5-400 | Thermal conductivity of joint |
| Stress Concentration Factor | - | 1.0-5.0 | Geometric stress concentration |
| Thermal Fatigue Life | cycles | 80-80,000 | Fatigue life under thermal cycling |
| Electrical Stability Score | - | 0-100 | Electrical performance stability |
| Thermal Stability Score | - | 0-100 | Thermal performance stability |

## Material Properties Database

The dataset includes realistic material properties for four common welding materials:

| Material | Thermal Conductivity (W/m·K) | Electrical Conductivity (S/m) | Thermal Expansion (1/K) | Yield Strength (MPa) | Melting Point (K) |
|----------|------------------------------|-------------------------------|-------------------------|---------------------|-------------------|
| Copper | 400 | 5.8×10⁷ | 16.5×10⁻⁶ | 200 | 1,357 |
| Aluminum | 237 | 3.5×10⁷ | 23.1×10⁻⁶ | 95 | 933 |
| Nickel | 91 | 1.4×10⁷ | 13.4×10⁻⁶ | 200 | 1,728 |
| Titanium | 22 | 2.4×10⁶ | 8.6×10⁻⁶ | 880 | 1,941 |

## Failure Modes

The dataset includes four distinct failure modes based on material and process characteristics:

1. **Thermal Fatigue** (63.8%): High thermal expansion mismatch
2. **General Degradation** (30.0%): Normal wear and aging
3. **Crack Propagation** (5.9%): High porosity and defects
4. **Electrical Overheating** (0.3%): High contact resistance

## Dataset Files

### Main Dataset Files
- `welding_ml_dataset_combined.csv/parquet` - Complete dataset (15,000 × 41)
- `welding_ml_dataset_input_parameters.csv/parquet` - Input parameters only
- `welding_ml_dataset_characterization_metrics.csv/parquet` - Characterization metrics only
- `welding_ml_dataset_performance_metrics.csv/parquet` - Performance metrics only
- `welding_ml_dataset_metadata.json` - Dataset metadata and material properties

### Analysis Files
- `welding_analysis_plots/analysis_report.json` - Statistical analysis results
- `welding_analysis_plots/material_heatmap.png` - Material combination performance
- `welding_analysis_plots/technique_comparison.png` - Welding technique comparison
- `welding_analysis_plots/correlation_heatmap.png` - Feature correlation matrix
- `welding_analysis_plots/performance_distributions.png` - Performance metric distributions
- `welding_analysis_plots/failure_analysis.png` - Failure mode analysis
- `welding_analysis_plots/interactive_3d_plot.html` - Interactive 3D visualization

## Key Features

### Physics-Informed Data Generation
- **Realistic Material Properties**: Based on actual material databases
- **Process Physics**: Incorporates thermal dynamics, electrical properties, and mechanical behavior
- **Failure Mechanisms**: Models realistic failure modes based on material science principles
- **Correlated Variables**: Features are correlated based on physical relationships

### Comprehensive Coverage
- **4 Welding Techniques**: Ultrasonic, Laser, Resistance Spot, Friction Stir
- **4 Materials**: Copper, Aluminum, Nickel, Titanium
- **5 Surface Finishes**: Polished, Rough, Anodized, Coated, Oxidized
- **4 Atmospheres**: Air, Argon, Nitrogen, Vacuum

### ML-Ready Format
- **No Missing Values**: Complete dataset with all features populated
- **Balanced Classes**: Reasonable distribution of failure modes and techniques
- **Normalized Ranges**: Features scaled to appropriate ranges for ML algorithms
- **Derived Features**: Additional engineered features for better model performance

## Usage Examples

### Loading the Dataset
```python
import pandas as pd

# Load complete dataset
df = pd.read_parquet('welding_ml_dataset_combined.parquet')

# Load specific components
input_params = pd.read_parquet('welding_ml_dataset_input_parameters.parquet')
char_metrics = pd.read_parquet('welding_ml_dataset_characterization_metrics.parquet')
perf_metrics = pd.read_parquet('welding_ml_dataset_performance_metrics.parquet')
```

### Basic Analysis
```python
# Dataset overview
print(f"Dataset shape: {df.shape}")
print(f"Features: {list(df.columns)}")

# Material combinations
print(df.groupby(['anode_material', 'cathode_material'])['thermal_cycles_to_failure'].mean())

# Technique performance
print(df.groupby('welding_technique')['thermal_cycles_to_failure'].mean().sort_values(ascending=False))
```

### ML Model Development
```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# Prepare features and target
X = df.drop(['sample_id', 'thermal_cycles_to_failure'], axis=1)
y = df['thermal_cycles_to_failure']

# Encode categorical variables
X = pd.get_dummies(X, columns=['anode_material', 'cathode_material', 'welding_technique', 
                               'surface_finish', 'atmosphere', 'failure_mode'])

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
score = model.score(X_test, y_test)
print(f"R² Score: {score:.3f}")
```

## Applications

### Primary Use Cases
1. **Inverse Design**: Predict optimal welding parameters for target performance
2. **Process Optimization**: Optimize welding parameters for specific material combinations
3. **Quality Prediction**: Predict weld quality and performance from process parameters
4. **Failure Analysis**: Understand failure mechanisms and improve reliability
5. **Material Selection**: Choose optimal material combinations for specific applications

### Research Applications
- **Multi-physics Modeling**: Study thermal, electrical, and mechanical interactions
- **Process Development**: Develop new welding techniques and parameters
- **Material Science**: Study intermetallic formation and material compatibility
- **Reliability Engineering**: Predict long-term performance under extreme conditions

## Technical Specifications

- **Total Samples**: 15,000
- **Total Features**: 41 (20 input + 10 characterization + 11 performance)
- **File Formats**: CSV, Parquet, JSON
- **Data Types**: Mixed (numeric, categorical, ordinal)
- **Missing Values**: None
- **Outliers**: <5% in any feature
- **Correlation Range**: -0.95 to +0.95

## Dependencies

```bash
pip install numpy pandas scipy scikit-learn matplotlib seaborn plotly pyarrow
```

## Citation

If you use this dataset in your research, please cite:

```
ML-Driven Inverse Design of Welding Parameters Dataset
Generated for extreme temperature cycling applications
Dataset includes 15,000 samples with physics-informed correlations
```

## License

This dataset is provided for research and educational purposes. Please ensure appropriate attribution when using in publications or commercial applications.

## Contact

For questions about the dataset or to request additional features, please refer to the dataset documentation or analysis tools provided.

---

**Note**: This dataset was generated using physics-informed models and realistic material properties. While the correlations and relationships are based on established principles, the specific values are synthetic and should be validated against experimental data for critical applications.