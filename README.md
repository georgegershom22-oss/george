# Welding Parameter Dataset for ML-Driven Inverse Design

## Overview

This repository contains a comprehensive dataset and machine learning models for inverse design of welding parameters. The dataset includes realistic welding process parameters, quality metrics, and performance validation metrics under extreme temperature cycling conditions.

## Dataset Structure

### Input Parameters (15 features)
- **Base Materials**: Anode and cathode materials (Cu, Al, Ni, Ti)
- **Tab Thickness**: 50-500 µm range
- **Surface Finish**: Polished, Rough, Coated_Ag, Coated_Ni, Anodized
- **Welding Technique**: USW, Laser, Resistance_Spot, Friction_Stir
- **Process Parameters**: Power, Amplitude, Force, Time, Speed, Pulse Frequency
- **Environmental**: Pre-heat temperature
- **Derived Parameters**: Material compatibility, thermal mismatch, electrical mismatch

### Quality Metrics (6 features)
- **Weld Strength**: 10-150 MPa
- **Contact Resistance**: 0.1-2.0 mΩ
- **Penetration Depth**: 20-200 µm
- **Weld Width**: 50-300 µm
- **Porosity**: 0.1-10.0%
- **Microhardness**: 40-200 HV

### Performance Metrics (5 features)
- **Thermal Cycles to Failure**: 100-10,000 cycles
- **Resistance Degradation Rate**: 0.0001-0.01 %/cycle
- **Mechanical Degradation Rate**: 0.0001-0.005 %/cycle
- **Temperature Coefficient of Resistance**: 50-300 ppm/°C
- **Creep Rate**: 0.001-0.1 µm/cycle

## Files Generated

### Core Dataset Files
- `welding_dataset.csv` - Complete dataset (10,000 samples, 28 features)
- `welding_dataset.xlsx` - Excel file with multiple sheets
- `welding_dataset_ml_ready.csv` - ML-ready format with encoded variables
- `feature_importance.csv` - Feature importance rankings

### Analysis and Visualization
- `welding_dataset_analysis.png` - Comprehensive static visualizations
- `interactive_material_performance.html` - Interactive material performance plots
- `interactive_process_parameters.html` - Interactive process parameter effects
- `interactive_material_heatmap.html` - Material combination heatmap

### Machine Learning Models
- `welding_models.joblib` - Trained forward and inverse models
- `welding_dataset_generator.py` - Dataset generation script
- `inverse_design_model.py` - ML models for inverse design
- `dataset_analysis.py` - Comprehensive analysis tools

## Key Findings

### Material Performance
- **Best Material Combinations**: Ni-Ti (0.836), Ni-Cu (0.829), Ti-Ti (0.823)
- **Material Compatibility**: Strong correlation with thermal cycles to failure (r=0.729)
- **Thermal Mismatch**: Negative correlation with performance (r=-0.623)

### Welding Technique Ranking
1. **Friction_Stir**: Highest quality score (0.652)
2. **Resistance_Spot**: Good balance (0.602)
3. **USW**: Moderate performance (0.583)
4. **Laser**: Lower quality score (0.566)

### Process Parameter Optimization
- **Power Range**: 1,008-4,947 W for high-quality welds
- **Force Range**: 447-4,976 N for optimal performance
- **Time Range**: 83-997 ms for best results
- **Process Efficiency**: Average 1,814 W, 1,058 N, 242 ms

### Quality-Performance Correlations
- **Weld Strength ↔ Thermal Cycles**: Strong positive correlation (r=0.686)
- **Quality Score ↔ Thermal Cycles**: Strong positive correlation (r=0.713)
- **Performance Prediction**: R² = 0.511 from quality metrics

## Usage

### Generate Dataset
```bash
python3 welding_dataset_generator.py
```

### Run Analysis
```bash
python3 dataset_analysis.py
```

### Train Inverse Design Models
```bash
python3 inverse_design_model.py
```

### Use Inverse Design
```python
from inverse_design_model import WeldingInverseDesignModel

# Load trained model
model = WeldingInverseDesignModel()
model.load_models('welding_models.joblib')

# Define target requirements
target_quality = {
    'weld_strength_mpa': 120,
    'contact_resistance_mohm': 0.3,
    'porosity_percent': 1.5
}

target_performance = {
    'thermal_cycles_to_failure': 8000,
    'weld_quality_score': 0.85
}

material_constraints = {
    'anode_material': 'Cu',
    'cathode_material': 'Al',
    'welding_technique': 'USW'
}

# Get optimized parameters
result = model.optimize_parameters(target_quality, target_performance, material_constraints)
print(result['optimized_parameters'])
```

## Model Performance

### Forward Models (Parameters → Quality/Performance)
- **Weld Strength**: R² = 0.653 (Gradient Boosting)
- **Contact Resistance**: R² = 0.583 (Gradient Boosting)
- **Thermal Cycles**: R² = 0.620 (Gradient Boosting)
- **Quality Score**: R² = 0.586 (Gradient Boosting)

### Inverse Models (Quality/Performance → Parameters)
- **Process Parameters**: R² = 0.186 (Gradient Boosting)
- **Optimization**: Iterative refinement for improved accuracy

## Requirements

```
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.5.0
seaborn>=0.11.0
scikit-learn>=1.0.0
plotly>=5.0.0
openpyxl>=3.0.0
joblib>=1.0.0
```

## Applications

1. **Process Optimization**: Find optimal welding parameters for specific requirements
2. **Quality Prediction**: Predict weld quality from process parameters
3. **Material Selection**: Choose optimal material combinations
4. **Technique Selection**: Select best welding technique for application
5. **Performance Validation**: Predict long-term performance under thermal cycling

## Dataset Characteristics

- **Size**: 10,000 samples
- **Features**: 28 (15 input + 6 quality + 5 performance + 2 derived)
- **Missing Values**: None
- **Data Quality**: High (realistic parameter ranges and relationships)
- **Correlations**: Strong relationships between input parameters and outcomes

## Future Enhancements

1. **Additional Materials**: Expand material database
2. **More Techniques**: Include additional welding methods
3. **Real-time Optimization**: Online parameter adjustment
4. **Uncertainty Quantification**: Confidence intervals for predictions
5. **Multi-objective Optimization**: Pareto-optimal solutions

## Citation

If you use this dataset or models in your research, please cite:

```
Welding Parameter Dataset for ML-Driven Inverse Design
Generated using realistic material properties and process relationships
10,000 samples with 28 features covering input parameters, quality metrics, and performance validation
```

## License

This dataset and code are provided for research and educational purposes. Please ensure proper attribution when using or modifying the code.