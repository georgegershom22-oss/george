# SOFC Thermo-Mechanical Dataset Package

## Overview

This package provides a comprehensive dataset for **Numerical and Experimental Investigation on Thermo-Mechanical Behavior of SOFC (Solid Oxide Fuel Cells) at High Temperatures**.

## ⚠️ IMPORTANT DISCLAIMER

**ALL DATA IN THIS PACKAGE IS SYNTHETIC/ILLUSTRATIVE AND GENERATED FOR EDUCATIONAL PURPOSES ONLY.**

- The data values are based on published literature ranges and typical values found in SOFC research
- This is NOT real experimental data
- Values are physically reasonable and representative but should not be cited as actual measurements
- For real experimental data, please refer to the sources listed in `DATA_SOURCES.md`
- This package serves as a template and educational resource for SOFC researchers

## Package Contents

### 1. Material Properties (`data/01_material_properties/`)

Thermophysical properties (CTE, thermal conductivity, elastic modulus, etc.) as functions of temperature (25-1000°C) for:

- **YSZ (Yttria-Stabilized Zirconia)** - Electrolyte material
- **Ni-YSZ (Nickel-YSZ)** - Anode material
- **LSM (Lanthanum Strontium Manganite)** - Cathode material
- **LSCF (Lanthanum Strontium Cobalt Ferrite)** - Alternative cathode
- **Crofer 22 APU** - Metallic interconnect material
- **Glass-Ceramic Sealant** - Sealing material
- **High-Temperature Mechanical Properties** - Fracture toughness, flexural strength, hardness, creep rates

### 2. Experimental Test Data (`data/02_experimental_test_data/`)

- **Thermal Cycling Tests**: Rapid (20°C/min) and slow (5°C/min) cycling data showing degradation
- **Thermal Shock Tests**: Quench experiments at various temperature drops
- **Isothermal Aging**: Long-term stability data at 800°C (up to 5000 hours)
- **Four-Point Bending**: Mechanical strength measurements at different temperatures
- **Compression Tests**: Compressive stress-strain behavior

### 3. Electrochemical Performance (`data/03_electrochemical_performance/`)

- **V-I Curves**: Voltage-current characteristics at 600-800°C
- **EIS Impedance**: Nyquist plot data from electrochemical impedance spectroscopy
- **ASR Degradation**: Area specific resistance evolution over time
- **OCV Measurements**: Open circuit voltage vs temperature

### 4. Microstructural Data (`data/04_microstructural_data/`)

- **Porosity Measurements**: Evolution under different operating conditions
- **Phase Analysis (XRD)**: X-ray diffraction patterns
- **Grain Size Data**: Grain growth during operation

### 5. Simulation Data (`data/05_simulation_data/`)

Finite element modeling results for a 100mm × 100mm planar SOFC:

- **Temperature Distribution**: Spatial temperature field
- **Stress Distribution**: Von Mises stress and stress tensor components
- **Displacement Field**: Thermal expansion-induced displacements
- **Failure Probability**: Weibull-based probabilistic failure analysis

### 6. Stack-Level Data (`data/06_stack_level_data/`)

- **Stack Voltage Cycling**: 5-cell stack performance over 1000 hours
- **Temperature Distribution**: Multiple thermocouple readings in stack
- **Gas Leakage Rates**: Seal degradation monitoring
- **Contact Resistance**: Evolution during thermal cycling

## Installation

### Requirements

- Python 3.7 or higher
- pip package manager

### Setup

```bash
# Navigate to the scripts directory
cd sofc_thermo_mechanical_dataset/scripts

# Install required packages
pip install -r requirements.txt
```

## Usage

### Generate Publication-Quality Figures

```bash
cd sofc_thermo_mechanical_dataset/scripts
python generate_figures.py
```

This will create 15+ high-resolution figures (300 DPI) in the `figures/` directory, including:

- Material property trends vs temperature
- Thermal cycling degradation plots
- V-I and power curves
- Nyquist plots (EIS)
- Temperature and stress distribution contours
- Failure probability heatmaps
- Microstructural evolution charts
- Stack performance monitoring

### Bundle CSV Files into ZIP

```bash
cd sofc_thermo_mechanical_dataset/scripts
python bundle_csv_to_zip.py
```

This creates `sofc_thermo_mechanical_data.zip` in the project root containing all CSV files organized by category.

### Load Data in Your Own Scripts

```python
import pandas as pd
from pathlib import Path

# Load material properties
ysz_data = pd.read_csv('data/01_material_properties/ysz_thermophysical_properties.csv', 
                       comment='#')

# Load V-I curves
vi_data = pd.read_csv('data/03_electrochemical_performance/vi_curves.csv', 
                      comment='#')

# Process and analyze...
```

## Data Structure

Each CSV file includes:
- **Header comment**: Disclaimer indicating synthetic nature of data
- **Column headers**: Descriptive names with units in parentheses
- **Data rows**: Physically reasonable values based on literature

## Data Sources

For legitimate experimental data and material properties, see `DATA_SOURCES.md`, which provides:

- Links to open-access SOFC datasets
- Material property datasheets
- Key research papers with experimental data
- General materials databases
- Government and national lab resources

## Citation

If you use this template/educational resource, please cite as:

```
SOFC Thermo-Mechanical Dataset Package (Synthetic/Illustrative)
Version 1.0 (2024)
https://github.com/georgegershom22-oss/george
Educational resource - NOT real experimental data
```

**For actual data**: Please cite the original sources listed in `DATA_SOURCES.md`

## License

- **Code/Scripts**: MIT License
- **Data (Synthetic)**: CC BY 4.0 (Creative Commons Attribution 4.0 International)

You are free to:
- Share and adapt the material
- Use for any purpose, including commercially

Under the following terms:
- Attribution: Give appropriate credit
- No additional restrictions

## Contributing

Contributions to improve this educational resource are welcome:

- Add more realistic data ranges based on published literature
- Improve visualization scripts
- Add additional analysis tools
- Update references in DATA_SOURCES.md

## Acknowledgments

This package was created as an educational resource and template for SOFC researchers. The synthetic data values are based on ranges reported in peer-reviewed literature. Users should always verify values against authoritative sources for their specific applications.

## Contact

For questions or suggestions, please open an issue on the GitHub repository.

---

**Remember**: This is synthetic/illustrative data for educational purposes. For real research, use data from actual experiments or validated sources!
