# SOFC Foundational & Calibration Dataset

## Phase 1: Complete Physics-Based Model Calibration Data

This repository contains a comprehensive dataset for Solid Oxide Fuel Cell (SOFC) sintering optimization, specifically designed for calibrating Finite Element Method (FEM) and Phase-Field models used in advanced manufacturing process optimization.

## 🎯 Purpose

The dataset enables:
- **FEM Model Calibration**: Thermo-mechanical modeling of sintering-induced deformation
- **Phase-Field Model Calibration**: Microstructural evolution during sintering
- **Reinforcement Learning Training**: Initial process window data for AI-driven optimization
- **Process Understanding**: Comprehensive material property and kinetics database

## 📊 Dataset Overview

### 1. Thermo-Physical Properties Dataset
**Purpose**: Calibrate FEM models for thermal and mechanical behavior

**Materials Covered**:
- **Anode**: NiO-YSZ (60-40 vol%)
- **Electrolyte**: 8YSZ (8 mol% Y₂O₃-ZrO₂)
- **Functional Layer**: NiO-YSZ (40-60 vol%)

**Properties Included**:
- Coefficient of Thermal Expansion (CTE)
- Young's Modulus
- Poisson's Ratio
- Shear Viscosity (for sintering)
- Density

**Temperature Range**: 20°C to 1400°C (100 data points)

**Experimental Methods Simulated**:
- Dynamical Mechanical Analysis (DMA)
- Dilatometry
- Nanoindentation

### 2. Sintering Kinetics Dataset
**Purpose**: Calibrate Phase-Field models for densification and microstructural evolution

**Parameter Space**:
- **Temperature**: 1200-1400°C (25 points)
- **Relative Density**: 0.45-0.95 (20 points)
- **Hold Time**: 1-1000 minutes (15 points)
- **Total Combinations**: 18,750 per material

**Kinetic Parameters**:
- Sintering Stress (MPa)
- Bulk and Shear Viscosity (Pa·s)
- Densification Rate (1/s)
- Grain Growth Rate (μm/s)

**Includes**: Master Sintering Curve data for each material

### 3. Microstructural Evolution Dataset
**Purpose**: Validate model predictions against experimental microstructural data

**Test Conditions**:
- **Temperatures**: 1250°C, 1300°C, 1350°C, 1400°C
- **Time Series**: 0 to 480 minutes (interrupted tests)
- **Analysis Methods**: SEM (2D) and X-ray CT (3D)

**Microstructural Parameters**:
- Porosity fraction and pore size distribution
- Grain size and distribution
- Tortuosity and connectivity
- Specific surface area

**Image Metadata**: Synthetic SEM and X-ray CT image parameters for 500+ samples

### 4. Initial Process Window Dataset
**Purpose**: Provide baseline data for reinforcement learning agent training

**Process Parameters**:
- **Heating Rate**: 1-20°C/min (8 levels)
- **Peak Temperature**: 1200-1400°C (15 levels)
- **Hold Time**: 0-480 minutes (7 levels)
- **Atmosphere**: Air, Reducing (10% H₂), Reducing (5% H₂), Inert N₂

**Outcomes Measured**:
- Warpage (max and RMS, mm)
- Cracking (yes/no)
- Final density and porosity
- Grain size
- Overall quality score (0-100)

**Total Experiments**: 3,360 process parameter combinations

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd sofc-dataset

# Install dependencies
pip install -r requirements.txt
```

### Generate Complete Dataset

```bash
# Generate all datasets (recommended)
python sofc_foundational_dataset.py

# Or use the download utility
python download_dataset.py --generate-all
```

### Validate Dataset

```bash
# Validate all generated files
python download_dataset.py --validate
```

### Load Sample Data

```bash
# View sample data from each dataset
python download_dataset.py --load-sample
```

## 📁 File Structure

```
sofc_dataset/
├── thermophysical/
│   ├── anode_properties.csv
│   ├── electrolyte_properties.csv
│   ├── functional_layer_properties.csv
│   └── all_materials_properties.csv
├── sintering_kinetics/
│   ├── anode_kinetics.csv
│   ├── electrolyte_kinetics.csv
│   ├── functional_layer_kinetics.csv
│   ├── all_materials_kinetics.csv
│   ├── anode_master_curve.csv
│   ├── electrolyte_master_curve.csv
│   └── functional_layer_master_curve.csv
├── microstructure/
│   ├── anode_evolution.csv
│   ├── electrolyte_evolution.csv
│   ├── functional_layer_evolution.csv
│   ├── all_materials_evolution.csv
│   └── image_metadata.csv
├── process_window/
│   ├── sintering_experiments.csv
│   └── analysis.json
├── plots/
│   └── thermophysical_properties.png
├── dataset_summary.json
├── data_dictionary.json
└── validation_report.json
```

## 🔬 Data Usage Examples

### Loading Thermophysical Properties

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load all materials properties
df = pd.read_csv('sofc_dataset/thermophysical/all_materials_properties.csv')

# Plot CTE vs temperature for all materials
for material in df['Material'].unique():
    material_data = df[df['Material'] == material]
    plt.plot(material_data['Temperature_C'], 
             material_data['CTE_per_K'], 
             label=material)

plt.xlabel('Temperature (°C)')
plt.ylabel('CTE (1/K)')
plt.legend()
plt.show()
```

### Analyzing Sintering Kinetics

```python
# Load kinetics data
kinetics = pd.read_csv('sofc_dataset/sintering_kinetics/all_materials_kinetics.csv')

# Filter for specific conditions
anode_1300C = kinetics[
    (kinetics['Material'] == 'anode') & 
    (kinetics['Temperature_C'] == 1300)
]

# Plot densification rate vs density
plt.scatter(anode_1300C['Relative_Density'], 
           anode_1300C['Densification_Rate_per_s'])
plt.xlabel('Relative Density')
plt.ylabel('Densification Rate (1/s)')
plt.yscale('log')
plt.show()
```

### Process Window Analysis

```python
# Load process window data
experiments = pd.read_csv('sofc_dataset/process_window/sintering_experiments.csv')

# Analyze success rate by temperature
success_by_temp = experiments.groupby('Peak_Temperature_C')['Success'].mean()
print("Success rate by temperature:")
print(success_by_temp)

# Find optimal conditions
optimal = experiments[experiments['Quality_Score'] > 80]
print(f"Found {len(optimal)} high-quality experiments")
```

## 📈 Model Calibration Guidelines

### FEM Model Calibration

1. **Thermal Analysis**: Use temperature-dependent CTE and density data
2. **Mechanical Analysis**: Use Young's modulus and Poisson's ratio data
3. **Sintering Simulation**: Use shear viscosity data for viscoplastic models

### Phase-Field Model Calibration

1. **Densification**: Use sintering stress and bulk viscosity parameters
2. **Grain Growth**: Use grain growth rate data
3. **Validation**: Compare predictions with microstructural evolution data

### RL Agent Training

1. **State Space**: Use process parameters (heating rate, temperature, time)
2. **Action Space**: Define based on process window bounds
3. **Reward Function**: Use quality score and success metrics
4. **Initial Policy**: Train on successful experiments from process window data

## 🔍 Data Quality & Validation

- **Completeness**: All datasets include comprehensive parameter coverage
- **Physical Consistency**: All values respect physical bounds and relationships
- **Noise Modeling**: Realistic experimental noise added to all measurements
- **Cross-Validation**: Datasets are internally consistent across different views

## 📚 References & Background

This dataset is based on established models and experimental correlations from:

1. **Sintering Theory**: Rahaman, M.N. "Ceramic Processing and Sintering"
2. **Master Sintering Curves**: Su & Johnson (1996), Blaine & Park (2002)
3. **Material Properties**: NIST databases and literature compilations
4. **Phase-Field Modeling**: Chen & Wang (1996), Steinbach (2009)

## 🤝 Contributing

To extend or improve the dataset:

1. Fork the repository
2. Add new materials or extend parameter ranges
3. Validate new data using the provided tools
4. Submit a pull request with documentation

## 📄 License

This dataset is provided under the MIT License for research and educational purposes.

## 📞 Support

For questions or issues:
- Open an issue in this repository
- Check the data dictionary for field definitions
- Review validation reports for data quality metrics

---

**Generated**: 2025-10-25  
**Version**: 1.0  
**Total Dataset Size**: ~50MB  
**Materials**: 3 (Anode, Electrolyte, Functional Layer)  
**Data Points**: >100,000 across all datasets