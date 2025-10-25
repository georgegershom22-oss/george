# Quick Start Guide

## Phase 1: Foundational & Calibration Dataset

This guide will help you get started with the SOFC sintering dataset in 5 minutes.

---

## 📁 Dataset Location

```
/workspace/phase1_foundational_calibration_data/
```

---

## 🚀 Quick Access

### View Summary
```bash
cd phase1_foundational_calibration_data
cat DATASET_SUMMARY.txt
```

### Explore with Python
```bash
# Install dependencies (if needed)
pip install pandas numpy matplotlib seaborn

# Explore dataset
python3 dataset_loader.py --explore

# Generate all plots
python3 dataset_loader.py --plot all --save
```

---

## 📊 What's Included

### 1️⃣ Material Properties
- **Files**: 3 CSV files
- **Content**: Temperature-dependent properties (CTE, Young's Modulus, Viscosity, etc.)
- **Materials**: NiO-YSZ, YSZ, GDC, SDC
- **Temperature Range**: 25-1600°C

```python
import pandas as pd

# Load NiO-YSZ properties
nio_props = pd.read_csv('material_properties/nio_ysz_anode_properties.csv')
print(nio_props.head())

# Plot CTE vs temperature
import matplotlib.pyplot as plt
plt.plot(nio_props['Temperature_C'], nio_props['CTE_1e-6_K'])
plt.xlabel('Temperature (°C)')
plt.ylabel('CTE (10⁻⁶/K)')
plt.show()
```

### 2️⃣ Sintering Kinetics
- **Files**: 3 CSV files
- **Content**: Sintering stress, viscosities, densification rates
- **Experiments**: 50 densification measurements

```python
# Load sintering stress data
stress = pd.read_csv('sintering_kinetics/nio_ysz_sintering_stress.csv')

# Filter by temperature
data_1300 = stress[stress['Temperature_C'] == 1300]
print(data_1300)
```

### 3️⃣ Microstructural Evolution
- **Files**: 3 CSV files
- **Content**: Time-series microstructure data (porosity, grain size, pore size, tortuosity)
- **Points**: 96 time-series measurements

```python
# Load microstructure time-series
micro = pd.read_csv('microstructural_evolution/nio_ysz_microstructure_timeseries.csv')

# Plot porosity evolution
for temp in [1200, 1300, 1400]:
    data = micro[micro['Temperature_C'] == temp]
    plt.plot(data['Time_min'], data['Porosity_percent'], label=f'{temp}°C')

plt.xlabel('Time (min)')
plt.ylabel('Porosity (%)')
plt.legend()
plt.show()
```

### 4️⃣ Process Window Experiments
- **Files**: 5 CSV files
- **Content**: 60 sintering experiments with full characterization
- **Metrics**: Density, warpage, cracking, defects

```python
# Load experiments
exp = pd.read_csv('process_window_data/sintering_profile_experiments.csv')

# Find successful experiments (no cracking)
successful = exp[exp['Cracking'] == 'No']
print(f"Success rate: {len(successful)/len(exp)*100:.1f}%")

# Find best density without cracking
best = successful[successful['Final_Density_percent'] == successful['Final_Density_percent'].max()]
print(best[['Heating_Rate_C_min', 'Peak_Temperature_C', 'Hold_Time_min', 'Final_Density_percent']])
```

---

## 🎯 Common Use Cases

### Use Case 1: FEM Calibration
```python
# Load temperature-dependent properties for FEM input
nio_props = pd.read_csv('material_properties/nio_ysz_anode_properties.csv')

# Extract properties at specific temperature
temp = 1300  # °C
props_1300 = nio_props[nio_props['Temperature_C'] == temp].iloc[0]

print(f"At {temp}°C:")
print(f"  Young's Modulus: {props_1300['Youngs_Modulus_GPa']} GPa")
print(f"  CTE: {props_1300['CTE_1e-6_K']} × 10⁻⁶/K")
print(f"  Viscosity: {props_1300['Shear_Viscosity_Pa_s']:.2e} Pa·s")
```

### Use Case 2: RL Action Space Definition
```python
# Load action space boundaries
action_space = pd.read_csv('process_window_data/action_space_boundaries.csv')

# Get boundaries for NiO-YSZ
nio_actions = action_space[action_space['Material'] == 'NiO-YSZ']

for _, param in nio_actions.iterrows():
    print(f"{param['Parameter']:20s}: {param['Minimum_Value']:6.0f} - {param['Maximum_Value']:6.0f} {param['Unit']}")
```

### Use Case 3: Microstructure Prediction Validation
```python
# Load microstructure data
micro = pd.read_csv('microstructural_evolution/nio_ysz_microstructure_timeseries.csv')

# Get data at specific condition
condition = micro[(micro['Temperature_C'] == 1350) & (micro['Time_min'] == 240)]

print("Target microstructure at 1350°C after 240 min:")
print(f"  Porosity: {condition['Porosity_percent'].values[0]:.1f}%")
print(f"  Grain size: {condition['Mean_Grain_Size_um'].values[0]:.2f} μm")
print(f"  Tortuosity: {condition['Tortuosity'].values[0]:.2f}")
```

---

## 📖 Documentation

- **README.md**: Complete overview and usage guidelines
- **DATA_DICTIONARY.md**: All variable definitions with units
- **EXPERIMENTAL_METHODOLOGY.md**: Detailed measurement procedures
- **DATASET_SUMMARY.txt**: Quick reference statistics

---

## ✅ Quality Checks

### Check data integrity
```bash
python3 verify_dataset.py
```

### View statistics
```python
from dataset_loader import SOFCDatasetLoader

loader = SOFCDatasetLoader()
loader.print_summary()
```

---

## 🎨 Visualization Examples

### Material Properties
```python
from dataset_loader import SOFCDatasetLoader

loader = SOFCDatasetLoader()
loader.plot_material_properties(material='NiO-YSZ', save=True)
```

### Microstructure Evolution
```python
loader.plot_microstructure_evolution(material='NiO-YSZ', save=True)
```

### Process Window Analysis
```python
loader.plot_process_window(save=True)
```

---

## 💡 Pro Tips

1. **All CSV files have headers** - First row contains column names with units
2. **Missing data** - Represented as empty cells or NaN
3. **Consistent units** - Check DATA_DICTIONARY.md for all units
4. **Temperature range** - Material properties: 25-1600°C, Sintering: 1200-1500°C
5. **Replication** - Material properties measured in triplicate (n=3)

---

## 🔗 Key Relationships

```
Material Properties → FEM Input
         ↓
Sintering Kinetics → Model Calibration
         ↓
Process Parameters → Sintering Profile
         ↓
Microstructure Evolution ← Validate Models
         ↓
Final Properties (Density, Warpage, Defects)
```

---

## 📞 Need Help?

1. Check **DATA_DICTIONARY.md** for variable definitions
2. Review **EXPERIMENTAL_METHODOLOGY.md** for measurement details
3. Read **README.md** for comprehensive documentation
4. Use `dataset_loader.py` for data exploration examples

---

## 🎓 Example Workflow

```python
from dataset_loader import SOFCDatasetLoader
import pandas as pd
import numpy as np

# 1. Load all data
loader = SOFCDatasetLoader()
data = loader.load_all()

# 2. Explore dataset
loader.print_summary()

# 3. Analyze successful experiments
exp = data['experiments']
successful = exp[exp['Cracking'] == 'No']

# 4. Find optimal conditions
high_density = successful[successful['Final_Density_percent'] > 85]
low_warpage = high_density[high_density['Final_Warpage_mm'] < 0.20]

print("Optimal conditions found:")
print(low_warpage[['Heating_Rate_C_min', 'Peak_Temperature_C', 'Hold_Time_min', 
                   'Final_Density_percent', 'Final_Warpage_mm']])

# 5. Visualize results
loader.plot_process_window(save=True)
```

---

**Dataset Version**: 1.0  
**Last Updated**: 2025-10-25  
**Ready for**: FEM Calibration, Phase-Field Modeling, RL Training

---

Happy researching! 🚀
