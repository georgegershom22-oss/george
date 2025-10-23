# SOFC Low-Fidelity Simulation Dataset

## Overview
This dataset contains **10,200 samples** of low-fidelity (LF) SOFC (Solid Oxide Fuel Cell) simulations, generated using a 1D system-level lumped electrochemical model. The dataset is designed for multi-fidelity machine learning applications and thermal management optimization.

**Generated:** 2025-10-23  
**Model Type:** 1D Lumped Parameter Electrochemical Model  
**Simulation Domain:** Global stack-level performance

## Dataset Structure

### Files
```
sofc_lf_dataset/
├── sofc_lf_main_dataset.csv       # Main simulation results (2.3 MB)
├── sofc_lf_vi_curves.json         # V-I characteristic curves (9.6 MB)
├── dataset_summary.txt            # Statistical summary
└── README.md                      # This file
```

## Data Description

### Input Parameters (Features)
| Parameter | Description | Unit | Range | Mean ± Std |
|-----------|-------------|------|-------|------------|
| `temperature` | Operating temperature | °C | 700-900 | 798.8 ± 57.5 |
| `fuel_utilization` | Fuel utilization factor | - | 0.6-0.9 | 0.751 ± 0.087 |
| `anode_porosity` | Anode electrode porosity | - | 0.25-0.45 | 0.350 ± 0.057 |
| `anode_thickness` | Anode thickness | μm | 300-700 | 499.5 ± 115.6 |
| `cathode_thickness` | Cathode thickness | μm | 30-70 | 49.9 ± 11.6 |
| `electrolyte_thickness` | Electrolyte thickness | μm | 8-15 | 11.5 ± 2.0 |
| `active_area` | Active cell area | cm² | 80-120 | 100.0 ± 11.5 |

### Output Parameters (Targets)
| Parameter | Description | Unit | Range | Mean ± Std |
|-----------|-------------|------|-------|------------|
| `operating_voltage` | Cell voltage at 8000 A/m² | V | 0.50-0.86 | 0.726 ± 0.065 |
| `stack_temperature` | Stack temperature | °C | 716.9-909.6 | 811.6 ± 55.0 |
| `electrochemical_efficiency` | η = V_cell / V_thermoneutral | - | 0.34-0.58 | 0.490 ± 0.044 |
| `open_circuit_voltage` | OCV (zero current) | V | 1.37-1.39 | 1.381 ± 0.007 |
| `max_power_density` | Peak power density | W/m² | 3995-14639 | 9032 ± 2307 |

### V-I Curve Data
Each sample includes a complete voltage-current characteristic curve with 25 data points:
- `vi_current_densities`: Array of current density values (A/m²)
- `vi_voltages`: Corresponding cell voltage values (V)

## Physical Model

### Electrochemical Model Components

1. **Nernst Voltage (Thermodynamic Potential)**
   ```
   E = E₀ - (RT/2F) * ln(P_H2 * P_O2^0.5 / P_H2O)
   ```

2. **Activation Losses (Butler-Volmer)**
   - Anode: η_act,a = (RT/2F) * arcsinh(i/2i₀,a)
   - Cathode: η_act,c = (RT/4F) * arcsinh(i/2i₀,c)

3. **Ohmic Losses**
   - η_ohm = i * ASR (Area-Specific Resistance)
   - Includes electrolyte and electrode resistances

4. **Concentration Losses (Mass Transport)**
   - η_conc = (RT/nF) * ln(1 - i/i_L)

5. **Cell Voltage**
   ```
   V_cell = E_nernst - η_act - η_ohm - η_conc
   ```

### Temperature-Dependent Properties
- **Electrolyte conductivity (YSZ):** σ_e = 3.34×10⁴ * exp(-10300/T)
- **Exchange current densities:** Function of temperature and porosity
- **Diffusion coefficients:** Temperature-dependent Knudsen diffusion

## Data Quality

✓ **No missing values** (0/10200)  
✓ **No duplicates** (0/10200)  
✓ **Physically consistent** (all outputs within realistic bounds)  
✓ **Latin Hypercube Sampling** for comprehensive parameter space coverage

## Key Correlations

**Factors most correlated with operating voltage:**
1. Electrochemical efficiency: 1.0000 (by definition)
2. Max power density: 0.8938
3. Temperature: 0.8480
4. Open circuit voltage: 0.8480
5. Stack temperature: 0.8421

## Usage Examples

### Python - Load and Explore Dataset
```python
import pandas as pd
import json

# Load main dataset
df = pd.read_csv('sofc_lf_main_dataset.csv')

# Load V-I curves
with open('sofc_lf_vi_curves.json', 'r') as f:
    vi_data = json.load(f)

# Example: Get data for sample 0
sample_0 = df.iloc[0]
vi_curve_0 = vi_data[0]

print(f"Temperature: {sample_0['temperature']:.1f} °C")
print(f"Operating Voltage: {sample_0['operating_voltage']:.3f} V")
print(f"Efficiency: {sample_0['electrochemical_efficiency']:.3f}")
```

### Machine Learning Example
```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# Define features and target
features = ['temperature', 'fuel_utilization', 'anode_porosity', 
            'anode_thickness', 'cathode_thickness', 
            'electrolyte_thickness', 'active_area']
target = 'operating_voltage'

X = df[features]
y = df[target]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
score = model.score(X_test, y_test)
print(f"R² Score: {score:.4f}")
```

## Applications

This dataset is suitable for:

1. **Multi-Fidelity Machine Learning**
   - Train surrogate models for SOFC performance prediction
   - Transfer learning with high-fidelity data
   - Uncertainty quantification

2. **Design Optimization**
   - Optimize cell geometry and operating conditions
   - Balance performance vs. durability trade-offs
   - Sensitivity analysis

3. **Control Systems**
   - Develop model predictive control algorithms
   - Real-time performance estimation
   - Adaptive thermal management

4. **Digital Twin Development**
   - Fast approximations for real-time monitoring
   - Anomaly detection and diagnostics
   - Remaining useful life prediction

## Limitations

- **1D Model:** Does not capture spatial gradients within cells
- **Steady-State:** No transient dynamics included
- **Single-Cell Focus:** Stack-level effects simplified
- **Idealized Gases:** Pure H2/O2 operation assumed
- **No Degradation:** Long-term aging effects not included

## Citation

If you use this dataset, please cite:
```
SOFC Low-Fidelity Simulation Dataset (2025)
Generated using 1D lumped electrochemical model
10,200 samples with parametric sweep of operating conditions
```

## Contact

For questions or issues with this dataset, please refer to the generation script:
`generate_sofc_lf_dataset.py`

## Version History

- **v1.0** (2025-10-23): Initial release with 10,200 samples
  - 7 input parameters
  - 5 output metrics
  - 25-point V-I curves per sample
  - Latin Hypercube Sampling for parameter generation

## License

This dataset is provided for research and educational purposes.
