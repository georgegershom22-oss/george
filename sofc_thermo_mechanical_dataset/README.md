# SOFC Thermo-Mechanical Dataset Package

## PhD Thesis: "Numerical and Experimental Investigation on Thermo-Mechanical Behavior of SOFC at High Temperatures"

---

## ⚠️ **IMPORTANT DISCLAIMER** ⚠️

**ALL DATA IN THIS PACKAGE IS SYNTHETIC/ILLUSTRATIVE AND FOR EDUCATIONAL PURPOSES ONLY**

- All CSV files contain **SYNTHETIC DATA** generated based on published literature ranges and theoretical models
- This data is **NOT experimental data** from actual SOFC measurements
- **DO NOT use this data as ground truth** for research, engineering design, or commercial applications without independent verification
- The data is intended to demonstrate typical ranges, trends, and analysis workflows for SOFC thermo-mechanical investigations
- Always validate findings with peer-reviewed literature, experimental measurements, or certified material databases

---

## Project Overview

This package provides a comprehensive, well-organized dataset for investigating the thermo-mechanical behavior of Solid Oxide Fuel Cells (SOFCs) at high temperatures. It includes:

- **15 CSV data files** with temperature-dependent properties, creep behavior, thermal cycling degradation, and FEM inputs
- **8 Python visualization scripts** for generating publication-quality figures
- **1 Master data generation script** that creates all CSV files
- **1 ZIP packaging script** for data distribution
- **Complete documentation** with references to open-access SOFC datasets

## Materials Covered

The dataset includes properties for six key SOFC materials:
1. **8YSZ** (8 mol% Yttria-Stabilized Zirconia) - Electrolyte
2. **GDC** (Gadolinium-Doped Ceria) - Buffer layer / Electrolyte
3. **Ni-YSZ** (Nickel-Yttria-Stabilized Zirconia cermet) - Anode
4. **LSCF** (Lanthanum Strontium Cobalt Ferrite) - Cathode
5. **LSM** (Lanthanum Strontium Manganite) - Cathode
6. **Crofer 22 APU** - Ferritic steel interconnect

## Literature References Used for Calibration

The synthetic data in this package is based on property ranges and trends reported in:

### Thermal Properties:
- Hayashi et al. (2005) "Thermal expansion coefficient of yttria stabilized zirconia for various yttria contents"
- Sameshima et al. (1999) "Thermal expansion of rare-earth-doped ceria ceramics"
- Pihlatie et al. (2009) "Mechanical properties of NiO/Ni-YSZ composites depending on temperature, porosity and redox cycling"
- Atkinson & Selcuk (2000) "Mechanical behaviour of ceramic oxygen ion-conducting membranes"
- Mori & Hishinuma (2003) "Thermal and mechanical properties of perovskite-type oxide cathode materials"
- ThyssenKrupp VDM (2010) "Crofer 22 APU Material Data Sheet No. 4046"

### Mechanical Properties:
- Selcuk & Atkinson (1997) "Elastic properties of ceramic oxides used in solid oxide fuel cells"
- Morales et al. (2006) "Mechanical characterization of SOFC materials"
- Radovic & Lara-Curzio (2004) "Mechanical properties of tape cast nickel-based anode materials for SOFC before and after reduction in hydrogen"

### Creep Behavior:
- Huang & Goodenough (1998) "Creep of yttria-stabilized zirconia in SOFC environments"
- Yakabe et al. (2001) "3-D model calculation for planar SOFC" (FZ Jülich data)
- Clague et al. (2012) "Finite element and analytical stress analysis of a solid oxide fuel cell" (Tohoku University data)

### Electrochemical Performance:
- Chan & Xia (2001) "Anode micro model of solid oxide fuel cell"
- Zhu & Kee (2003) "Modeling elementary heterogeneous chemistry and electrochemistry in solid-oxide fuel cells"
- O'Hayre et al. (2006) "Fuel Cell Fundamentals" (Wiley)

## Dataset Description

### CSV Files in `data/` Directory

| File | Description | Rows |
|------|-------------|------|
| `01_thermal_properties.csv` | Temperature-dependent thermal conductivity, specific heat, CTE, density for 6 materials (25-1000°C) | 66 |
| `02_mechanical_properties.csv` | Elastic modulus, Poisson's ratio, flexural strength, fracture toughness, Weibull modulus (25-1000°C) | 66 |
| `03_creep_parameters_norton.csv` | Norton power-law creep parameters for Ni-YSZ anode at different compositions and temperatures | 13 |
| `04_creep_curves_NiYSZ.csv` | Simulated creep strain vs. time curves for 5 stress-temperature conditions (0-500 hours) | 101 |
| `05_CTE_mismatch_thermal_stress.csv` | CTE values and calculated biaxial thermal stress at interfaces (25-1000°C) | 11 |
| `06_polarization_curves.csv` | Current-voltage (I-V) and power density curves at three operating temperatures (750-850°C) | 61 |
| `07_thermal_cycling_degradation.csv` | Performance degradation over 100 thermal cycles at three ramp rates (5, 10, 20 °C/min) | 30 |
| `08_strain_hardening_FEM_input.csv` | Time-hardening creep constants for FEM software (Abaqus/ANSYS format) | 12 |
| `09_temperature_distribution.csv` | 2D temperature field on 100×100 mm cell surface under different operating modes | 441 |
| `10_stress_evolution_thermal_cycle.csv` | Stress evolution in each layer during heating-dwell-cooling cycle | 176 |
| `11_cell_geometry.csv` | Layer-by-layer dimensions for anode-supported planar SOFC | 10 |
| `12_operating_conditions.csv` | Test matrix with 12 experimental scenarios | 12 |
| `13_residual_stress.csv` | Post-sintering residual stress from XRD/neutron diffraction | 12 |
| `14_redox_cycling.csv` | Chemical expansion and degradation during redox cycling | 11 |
| `15_FEM_input_summary.csv` | Quick-reference table of material properties at key temperatures for FEM | 30 |

**Total: 912 data rows across 15 files**

## Installation and Usage

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate All Dataset Files

```bash
cd scripts
python generate_all_datasets.py
```

This will create all 15 CSV files in the `data/` directory.

### 3. Generate Figures

Run individual plotting scripts to create publication-quality figures:

```bash
python plot_thermal_properties.py      # 3-panel: CTE, thermal conductivity, specific heat
python plot_mechanical_properties.py   # 2-panel: elastic modulus, flexural strength
python plot_creep_curves.py            # Creep strain vs. time for 5 conditions
python plot_CTE_mismatch.py            # CTE comparison and interfacial stress
python plot_polarization_curves.py     # I-V and power density curves
python plot_thermal_cycling.py         # Performance degradation over cycles
python plot_stress_evolution.py        # Stress evolution during thermal cycle
python plot_temperature_contours.py    # 2D temperature distribution contours
```

All figures will be saved as PNG and PDF in the `figures/` directory.

### 4. Package Data as ZIP

```bash
python generate_zip.py
```

This creates `sofc_data.zip` containing all CSV files.

## Figure Examples

The visualization scripts generate the following publication-ready figures (300 DPI, serif fonts):

1. **Thermal Properties** - Temperature-dependent CTE, thermal conductivity, and specific heat capacity
2. **Mechanical Properties** - Elastic modulus and flexural strength vs. temperature
3. **Creep Curves** - Time-dependent strain under constant stress (Norton power-law model)
4. **CTE Mismatch** - Coefficient of thermal expansion comparison and interfacial thermal stress
5. **Polarization Curves** - Current-voltage characteristics and power density at 750-850°C
6. **Thermal Cycling Degradation** - Peak power and area-specific resistance over 100 cycles
7. **Stress Evolution** - Von Mises stress in each layer during startup/shutdown
8. **Temperature Contours** - 2D spatial temperature distribution under different loads

## Data Format

All CSV files include:
- **Comment header lines** (starting with `#`) stating the synthetic nature of data
- **Column headers** with descriptive names and units
- **SI units** or explicitly stated units in column names
- **Source basis** column referencing literature used for calibration

Example header:
```
# SYNTHETIC/ILLUSTRATIVE DATA - Based on published literature ranges
# Topic: Thermo-mechanical behavior of SOFC at high temperatures
# DO NOT use as ground truth without independent verification
```

## Accessing Real SOFC Datasets

For actual experimental data, see `open_data_sources.md`, which provides links to:
- NETL EDX microstructure datasets (FIB-SEM tomography)
- Mendeley Data polarization curves
- 4TU.nl thermodynamic system models
- NIST material property databases
- University of Alberta polarization datasets
- Bosch SOFC experimental corpus

## Citation

If you use the structure or methodology of this dataset package in your work, please cite:

```
[Your Name] (2024). SOFC Thermo-Mechanical Dataset Package. 
PhD Thesis: "Numerical and Experimental Investigation on Thermo-Mechanical 
Behavior of SOFC at High Temperatures". [Your Institution].
```

**Note:** Cite the original literature sources (listed above) when referencing specific property values or trends.

## License

This dataset package is released under the MIT License. See LICENSE file for details.

The synthetic data is provided "as-is" without warranty of any kind. Users are responsible for validating any findings against authoritative sources.

## Contact

For questions about this dataset package, please open an issue in the repository or contact [your email].

---

**Version:** 1.0  
**Last Updated:** February 2026  
**Python Version:** 3.8+  
**Dependencies:** matplotlib ≥ 3.7.0, numpy ≥ 1.24.0
