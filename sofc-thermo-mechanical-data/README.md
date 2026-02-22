# SOFC Thermo-Mechanical Dataset Package

## Numerical and Experimental Investigation on Thermo-Mechanical Behavior of SOFC at High Temperatures

---

## ⚠️ CRITICAL DISCLAIMER - SYNTHETIC DATA

**ALL DATA IN THIS PACKAGE IS SYNTHETIC AND ILLUSTRATIVE**

This dataset contains **synthetic/illustrative data** based on published literature ranges but **NOT actual experimental measurements**. The data is intended for:
- **Educational purposes**
- **Template development**
- **Model testing and validation**
- **Demonstration of data structures**

**DO NOT use this data directly in publications or research without replacing it with actual measured data from cited original sources.**

Users must cite and use original experimental measurements for any publication or research work. This package serves as a template and organizational framework only.

---

## Overview

This package provides a comprehensive, well-organized collection of temperature-dependent thermal, mechanical, electrochemical, and microstructural data for Solid Oxide Fuel Cell (SOFC) materials and systems. It includes:

- **16 CSV template files** with synthetic data representing typical ranges from literature
- **Python scripts** for data generation and visualization
- **Publication-quality plotting tools** for creating figures
- **Complete documentation** with references to original data sources

## Package Contents

### CSV Dataset Files (`data/`)

| File | Description | Rows | Key Parameters |
|------|-------------|------|----------------|
| `01_thermal_properties.csv` | Temperature-dependent thermal properties | 240 | k, Cp, CTE, ρ for 6 materials (25-1000°C) |
| `02_mechanical_properties.csv` | Temperature-dependent mechanical properties | 240 | E, ν, strength, KIC, Weibull for 6 materials |
| `03_creep_parameters_norton.csv` | Norton power law creep parameters | 20 | n, Q, A for Ni-YSZ variants |
| `04_creep_curves.csv` | Creep strain vs time curves | 101 | ε(t) at multiple T and σ (0-500h) |
| `05_CTE_mismatch_thermal_stress.csv` | CTE mismatch and thermal stress | 40 | ΔCTE, σ_thermal for material interfaces |
| `06_polarization_curves.csv` | Electrochemical I-V-P curves | 125 | V, P at 750, 800, 850°C (0-1.24 A/cm²) |
| `07_thermal_cycling_degradation.csv` | Thermal cycling degradation | 303 | Performance vs cycle number (3 ramp rates) |
| `08_strain_hardening_constants.csv` | FEM creep input constants | 16 | C1-C4 for Abaqus/ANSYS |
| `09_temperature_distribution.csv` | 2D cell temperature distribution | 1050 | T(x,y) for steady, startup, load change |
| `10_stress_evolution_thermal_cycle.csv` | Stress evolution during thermal cycling | 221 | σ vs time: heating→dwell→cooling |
| `11_cell_geometry.csv` | Cell layer dimensions & specifications | 10 | Thickness, porosity, grain size |
| `12_operating_conditions.csv` | Operating condition matrix | 11 | 11 test scenarios with T, flow, composition |
| `13_residual_stress.csv` | Residual stress measurements | 12 | XRD and neutron diffraction data |
| `14_redox_cycling.csv` | Redox cycling effects | 13 | Chemical strain, degradation vs cycles |
| `15_FEM_input_summary.csv` | Quick-reference FEM material table | 16 | Single-row summary of key properties |
| `16_references.csv` | Literature references with DOIs | 14 | Key papers for each data type |

### Materials Included

1. **8YSZ** - 8 mol% Yttria-Stabilized Zirconia (electrolyte)
2. **GDC** - Gadolinium-Doped Ceria (buffer layer)
3. **Ni-YSZ** - Nickel-YSZ cermet (anode)
4. **LSCF** - Lanthanum Strontium Cobalt Ferrite (cathode)
5. **LSM** - Lanthanum Strontium Manganite (cathode)
6. **Crofer22APU** - Ferritic steel interconnect

### Python Scripts (`scripts/`)

#### Data Generation
- `generate_all_datasets.py` - Master script to regenerate all 16 CSV files with synthetic data

#### Visualization Scripts (Publication-Quality Figures)
- `plot_thermal_properties.py` - CTE, thermal conductivity, specific heat vs temperature
- `plot_mechanical_properties.py` - Elastic modulus and strength vs temperature
- `plot_creep_curves.py` - Creep strain vs time at multiple conditions
- `plot_polarization.py` - I-V and I-P curves at three temperatures
- `plot_thermal_cycling.py` - Degradation vs cycle number for different ramp rates
- `plot_stress_evolution.py` - Von Mises stress evolution during thermal cycle
- `plot_CTE_mismatch.py` - CTE comparison bar chart showing mismatch
- `plot_temperature_map.py` - 2D temperature contour map of cell surface

#### Utility
- `create_zip.py` - Package all CSV files into downloadable ZIP archive

### Generated Figures (`figures/`)

All plotting scripts generate publication-quality PNG figures (300 DPI, 12pt fonts) with consistent color scheme:
- 8YSZ: Blue (#1f77b4)
- GDC: Orange (#ff7f0e)
- Ni-YSZ: Green (#2ca02c)
- LSCF: Red (#d62728)
- LSM: Purple (#9467bd)
- Crofer22APU: Brown (#8c564b)

## Installation and Usage

### Prerequisites

Python 3.7+ with the following packages:

```bash
pip install -r requirements.txt
```

Required packages:
- matplotlib
- numpy
- pandas

### Generating Synthetic Data

To regenerate all CSV files with synthetic data:

```bash
cd scripts
python generate_all_datasets.py
```

This will create/overwrite all 16 CSV files in the `data/` directory.

### Creating Figures

To generate all publication-quality figures:

```bash
cd scripts
python plot_thermal_properties.py
python plot_mechanical_properties.py
python plot_creep_curves.py
python plot_polarization.py
python plot_thermal_cycling.py
python plot_stress_evolution.py
python plot_CTE_mismatch.py
python plot_temperature_map.py
```

Figures will be saved to the `figures/` directory.

### Creating Data Package ZIP

To package all CSV files for distribution:

```bash
cd scripts
python create_zip.py
```

This creates `sofc_phd_datasets.zip` in the project root containing all data files.

## Publicly Available SOFC Dataset Sources

For **actual measured data** (not synthetic), please use these publicly available SOFC datasets:

### Experimental Data Repositories

1. **Mendeley SOFC ANN Validation Dataset**
   - URL: https://data.mendeley.com/datasets/j8b9v4cb9d/1
   - Description: SOFC performance data for artificial neural network validation

2. **University of Alberta SOFC Dataset**
   - URL: https://www.selectdataset.com/dataset/7d0bf95928104c14faa33e6139a9804e
   - Description: Comprehensive SOFC experimental measurements

3. **TU Delft SOFC Thermodynamic Analysis**
   - URL: https://data.4tu.nl/articles/dataset/Thermodynamic_analysis_of_SOFC_system_for_alternative_fuels/21542106
   - Description: Thermodynamic data for SOFC with alternative fuels

4. **CMU/NETL SOFC Microstructures**
   - URL: https://edx.netl.doe.gov/dataset/sofc-microstructures-hsu-epting-mahbub-jps-2018
   - Description: 3D microstructure images and analysis

### Material Property Databases

5. **PNNL Alloy Database**
   - URL: https://www.osti.gov/biblio/15010553/
   - Description: High-temperature alloy properties for SOFC interconnects

6. **VDM Crofer 22 APU Technical Data**
   - URL: https://www.vdm-metals.com/fileadmin/user_upload/Downloads/Data_Sheets/Data_Sheet_VDM_Crofer_22_APU.pdf
   - Description: Official datasheet for Crofer 22 APU interconnect steel

7. **NIST Materials Data Repository**
   - URL: https://materialsdata.nist.gov/
   - Description: Curated materials property data from NIST

8. **MatWeb Material Property Database**
   - URL: https://www.matweb.com/
   - Description: Comprehensive material property database (search "YSZ", "Ni-YSZ", etc.)

### Research Corpora

9. **Bosch SOFC-Exp Text Mining Resources**
   - URL: https://github.com/boschresearch/sofc-exp_textmining_resources
   - Description: Annotated corpus for SOFC experimental data extraction

10. **Pihlatie PhD Thesis (DTU)**
    - URL: https://backend.orbit.dtu.dk/ws/portalfiles/portal/245196924/Thesis_Mikko_Pihlatie_P740.pdf
    - Description: Comprehensive thesis on SOFC mechanical behavior and reliability

## Key Literature References

The following peer-reviewed publications provide measured data ranges that informed this synthetic dataset:

| ID | Authors | Year | Topic | DOI |
|----|---------|------|-------|-----|
| REF01 | Atkinson et al. | 2004 | YSZ mechanical properties | 10.1016/j.ssi.2004.01.004 |
| REF02 | Laurencin et al. | 2008 | Ni-YSZ creep behavior | 10.1016/j.jpowsour.2008.02.103 |
| REF03 | Nakajo et al. | 2012 | Thermo-mechanical modeling | 10.1016/j.jpowsour.2012.01.114 |
| REF04 | Malzbender et al. | 2009 | SOFC component properties | 10.1016/j.ceramint.2008.11.005 |
| REF05 | Yakabe et al. | 2001 | Temperature distribution | 10.1016/S0378-7753(01)00610-2 |
| REF06 | Selimovic et al. | 2005 | Thermal cycling | 10.1016/j.jpowsour.2004.10.012 |
| REF07 | Lin et al. | 2009 | Residual stress measurements | 10.1016/j.actamat.2009.05.018 |
| REF08 | Pihlatie et al. | 2009 | Redox cycling effects | 10.1016/j.jpowsour.2009.01.021 |
| REF09 | Menzler et al. | 2010 | LSCF cathode properties | 10.1016/j.jpowsour.2010.06.042 |
| REF10 | Quadakkers et al. | 2007 | Crofer 22 APU characterization | 10.1016/j.msea.2006.11.127 |
| REF11 | Ni et al. | 2007 | Electrochemical modeling | 10.1149/1.2789389 |
| REF12 | Zhu & Kee | 2003 | Polarization modeling | 10.1016/S0378-7753(03)00742-6 |
| REF13 | Hagen et al. | 2006 | Degradation mechanisms | 10.1016/j.jpowsour.2006.04.080 |
| REF14 | Sun & Stimming | 2007 | SOFC materials review | 10.1016/j.jpowsour.2006.12.017 |

## Data Structure Details

### Temperature-Dependent Properties
Most thermal and mechanical properties vary with temperature following empirical relationships fitted to literature data. Temperature ranges from 25°C (room temperature) to 1000°C (operating range) in 25°C increments.

### Electrochemical Data
Polarization curves model:
- Open Circuit Voltage (OCV): Nernst equation
- Ohmic losses: R_ohm × j
- Activation losses: Tafel equation
- Concentration losses: limiting current density model

### Creep Behavior
Norton power law: ε̇ = A·σⁿ·exp(-Q/RT)
- Covers multiple Ni volume fractions (30-56 vol%)
- Multiple porosity levels (20-35%)
- Temperature range: 700-1000°C

### Thermal Stress Calculation
Biaxial stress from CTE mismatch: σ = E·Δα·ΔT/(1-ν)
- Reference temperature: 1400°C (sintering)
- Cooling to operating/room temperature
- Interface stresses between layers

## File Naming Convention

Files are numbered 01-16 for logical ordering:
- **01-02**: Fundamental material properties
- **03-04**: Creep behavior
- **05**: Thermal mismatch
- **06-07**: Electrochemical performance
- **08-10**: FEM and stress analysis
- **11-12**: Geometry and operating conditions
- **13-14**: Degradation mechanisms
- **15-16**: Reference data

## License

This dataset package is released under the **MIT License**.

```
MIT License

Copyright (c) 2024 SOFC Thermo-Mechanical Research

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Citation

If you use this dataset package structure or scripts in your work, please cite:

```
SOFC Thermo-Mechanical Dataset Package (2024)
Numerical and Experimental Investigation on Thermo-Mechanical Behavior of SOFC at High Temperatures
GitHub Repository: [Your Repository URL]
```

**Important**: Always cite original data sources from the references above when using actual measured data in publications.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add your improvements (new materials, properties, scripts)
4. Submit a pull request

Suggested improvements:
- Additional materials (ScYSZ, BCY, BSCF, etc.)
- More operating conditions
- Additional visualization scripts
- Validation against experimental data
- FEM input file generators for ANSYS/Abaqus/COMSOL

## Contact

For questions, suggestions, or collaboration:
- Open an issue on GitHub
- Contact: [Your contact information]

## Acknowledgments

This dataset package structure is inspired by best practices in materials data management and reproducible research. Data ranges are based on extensive literature review of peer-reviewed SOFC publications (2000-2024).

---

**Remember**: This is a template with synthetic data. Always use actual experimental measurements from cited sources for research and publications.
