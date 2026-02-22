# SOFC Dataset Package - Quick Start Demo

This guide demonstrates how to use the SOFC thermo-mechanical dataset package.

## Installation

```bash
cd sofc_thermo_mechanical_dataset
pip install -r requirements.txt
```

## Quick Demo

### 1. Generate All Dataset Files (1 command)

```bash
cd scripts
python generate_all_datasets.py
```

**Output:**
```
============================================================
SOFC Thermo-Mechanical Dataset Generator
============================================================

WARNING: All data is SYNTHETIC/ILLUSTRATIVE
Based on published literature ranges for educational use only

Generating dataset files in: ../data

✓ Generated 01_thermal_properties.csv (66 rows)
✓ Generated 02_mechanical_properties.csv (66 rows)
✓ Generated 03_creep_parameters_norton.csv (13 rows)
✓ Generated 04_creep_curves_NiYSZ.csv (101 rows)
✓ Generated 05_CTE_mismatch_thermal_stress.csv (11 rows)
✓ Generated 06_polarization_curves.csv (61 rows)
✓ Generated 07_thermal_cycling_degradation.csv (30 rows)
✓ Generated 08_strain_hardening_FEM_input.csv (12 rows)
✓ Generated 09_temperature_distribution.csv (441 rows)
✓ Generated 10_stress_evolution_thermal_cycle.csv (47 rows)
✓ Generated 11_cell_geometry.csv (10 rows)
✓ Generated 12_operating_conditions.csv (12 rows)
✓ Generated 13_residual_stress.csv (12 rows)
✓ Generated 14_redox_cycling.csv (11 rows)
✓ Generated 15_FEM_input_summary.csv (30 rows)

============================================================
✓ All 15 CSV files generated successfully!
============================================================
```

### 2. Generate All Figures (8 commands)

```bash
python plot_thermal_properties.py
python plot_mechanical_properties.py
python plot_creep_curves.py
python plot_CTE_mismatch.py
python plot_polarization_curves.py
python plot_thermal_cycling.py
python plot_stress_evolution.py
python plot_temperature_contours.py
```

Each command outputs:
```
✓ Generated [figure_name].png and [figure_name].pdf
  Saved to: ../figures
```

### 3. Package Data for Distribution

```bash
python generate_zip.py
```

**Output:**
```
✓ Added README.txt to archive
✓ Added 01_thermal_properties.csv
✓ Added 02_mechanical_properties.csv
...
✓ Added 15_FEM_input_summary.csv

============================================================
✓ Successfully created: sofc_data.zip
  Location: ../
  Size: 19.8 KB
  Files: 15 CSV files + README.txt
============================================================
```

## Sample Data Analysis

### Example 1: Plot CTE for a Single Material

```python
import csv
import matplotlib.pyplot as plt

# Load data
data = []
with open('../data/01_thermal_properties.csv', 'r') as f:
    lines = [line for line in f if not line.startswith('#')]
    reader = csv.DictReader(lines)
    for row in reader:
        if row['Material'] == '8YSZ':
            data.append((float(row['Temperature_C']), 
                        float(row['CTE_1e-6_per_K'])))

# Plot
temps, ctes = zip(*data)
plt.plot(temps, ctes, 'o-')
plt.xlabel('Temperature (°C)')
plt.ylabel('CTE (×10⁻⁶ K⁻¹)')
plt.title('8YSZ Thermal Expansion')
plt.grid(True, alpha=0.3)
plt.show()
```

### Example 2: Find Peak Power from Polarization Curve

```python
import csv

with open('../data/06_polarization_curves.csv', 'r') as f:
    lines = [line for line in f if not line.startswith('#')]
    reader = csv.DictReader(lines)
    
    max_power_800 = 0
    optimal_current = 0
    
    for row in reader:
        power = float(row['Power_800C_W_per_cm2'])
        if power > max_power_800:
            max_power_800 = power
            optimal_current = float(row['Current_Density_A_per_cm2'])
    
    print(f"Peak power at 800°C: {max_power_800:.4f} W/cm²")
    print(f"Optimal current density: {optimal_current:.3f} A/cm²")
```

### Example 3: Calculate CTE Mismatch

```python
import csv

with open('../data/05_CTE_mismatch_thermal_stress.csv', 'r') as f:
    lines = [line for line in f if not line.startswith('#')]
    reader = csv.DictReader(lines)
    
    for row in reader:
        if row['Temperature_C'] == '800':
            print("At 800°C operating temperature:")
            print(f"  CTE(Ni-YSZ): {row['CTE_NiYSZ']} ×10⁻⁶ K⁻¹")
            print(f"  CTE(8YSZ):   {row['CTE_8YSZ']} ×10⁻⁶ K⁻¹")
            print(f"  Mismatch:    {row['Delta_CTE_Anode_Electrolyte']} ×10⁻⁶ K⁻¹")
            print(f"  Thermal stress: {row['Thermal_Stress_Anode_Interface_MPa']} MPa")
```

## Use Cases

### For FEM Simulations

Use `15_FEM_input_summary.csv` for quick reference of all material properties at key temperatures, formatted for direct input into Abaqus, ANSYS, or COMSOL.

### For Creep Analysis

1. Use `03_creep_parameters_norton.csv` for Norton power-law constants
2. Use `04_creep_curves_NiYSZ.csv` for validation curves
3. Use `08_strain_hardening_FEM_input.csv` for time-hardening FEM models

### For Thermal Stress Analysis

1. Use `05_CTE_mismatch_thermal_stress.csv` for interfacial stress estimates
2. Use `10_stress_evolution_thermal_cycle.csv` for transient stress profiles
3. Use `13_residual_stress.csv` for initial conditions

### For Electrochemical Modeling

1. Use `06_polarization_curves.csv` for I-V characteristics at different temperatures
2. Use `12_operating_conditions.csv` for test matrix scenarios
3. Use `07_thermal_cycling_degradation.csv` for degradation models

## Important Reminders

⚠️ **All data is SYNTHETIC/ILLUSTRATIVE**
- Based on published literature ranges
- NOT for use as ground truth without verification
- Intended for educational and demonstration purposes
- Validate with experimental data before production use

📚 **For real data:**
- See `open_data_sources.md` for links to 13 public SOFC datasets
- Cite original literature sources when referencing values
- Use NIST databases for certified material properties

## Support

For questions about the dataset package:
- Check `README.md` for full documentation
- Review `PACKAGE_SUMMARY.md` for implementation details
- See `VERIFICATION_CHECKLIST.md` for complete requirements list

---

**Package Version:** 1.0  
**Last Updated:** February 2026  
**Python:** 3.8+  
**Dependencies:** matplotlib ≥3.7.0, numpy ≥1.24.0
