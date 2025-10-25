# Data Dictionary - Phase 1 Foundational & Calibration Dataset

## Table of Contents
1. [Material Properties Data](#material-properties-data)
2. [Sintering Kinetics Data](#sintering-kinetics-data)
3. [Microstructural Evolution Data](#microstructural-evolution-data)
4. [Process Window Data](#process-window-data)

---

## Material Properties Data

### nio_ysz_anode_properties.csv

Temperature-dependent thermo-physical properties for NiO-YSZ anode composite.

| Variable Name | Unit | Description | Range | Measurement Method |
|--------------|------|-------------|-------|-------------------|
| Temperature_C | °C | Measurement temperature | 25-1600 | Type K thermocouple |
| CTE_1e-6_K | 10⁻⁶/K | Coefficient of thermal expansion | 11.2-15.9 | Dilatometry |
| Youngs_Modulus_GPa | GPa | Elastic modulus | 20.2-145.3 | Nanoindentation |
| Poissons_Ratio | - | Poisson's ratio | 0.28-0.37 | DMA/Nanoindentation |
| Shear_Viscosity_Pa_s | Pa·s | Viscosity for sintering | 7.8e5-1.2e15 | Calculated from sintering |
| Density_kg_m3 | kg/m³ | Material density | 5548-5850 | Helium pycnometry |
| Thermal_Conductivity_W_mK | W/(m·K) | Thermal conductivity | 3.2-8.1 | Laser flash analysis |
| Specific_Heat_J_kgK | J/(kg·K) | Specific heat capacity | 580-895 | DSC |

**Notes**: 
- Properties measured on fully dense samples except viscosity
- Viscosity data represents sintering stage behavior
- NiO-YSZ composition: 50-50 vol% mixture

### ysz_electrolyte_properties.csv

Temperature-dependent properties for 8YSZ (8 mol% Y₂O₃-stabilized ZrO₂) electrolyte.

| Variable Name | Unit | Description | Range | Measurement Method |
|--------------|------|-------------|-------|-------------------|
| Temperature_C | °C | Measurement temperature | 25-1600 | Type K thermocouple |
| CTE_1e-6_K | 10⁻⁶/K | Coefficient of thermal expansion | 10.5-13.6 | Dilatometry |
| Youngs_Modulus_GPa | GPa | Elastic modulus | 81.8-210.5 | Nanoindentation |
| Poissons_Ratio | - | Poisson's ratio | 0.31-0.37 | DMA/Nanoindentation |
| Shear_Viscosity_Pa_s | Pa·s | Viscosity for sintering | 7.8e9-2.5e16 | Calculated from sintering |
| Density_kg_m3 | kg/m³ | Material density | 5824-6050 | Helium pycnometry |
| Thermal_Conductivity_W_mK | W/(m·K) | Thermal conductivity | 2.5-5.6 | Laser flash analysis |
| Specific_Heat_J_kgK | J/(kg·K) | Specific heat capacity | 450-765 | DSC |

**Notes**:
- 8YSZ: 8 mol% Y₂O₃ stabilized cubic structure
- Higher sintering temperatures required compared to NiO-YSZ
- Excellent ionic conductivity above 600°C

### functional_layer_properties.csv

Properties for GDC (Gd₀.₂Ce₀.₈O₂₋ₓ) and SDC (Sm₀.₂Ce₀.₈O₂₋ₓ) functional layers.

| Variable Name | Unit | Description | Range | Measurement Method |
|--------------|------|-------------|-------|-------------------|
| Temperature_C | °C | Measurement temperature | 25-1600 | Type K thermocouple |
| CTE_1e-6_K | 10⁻⁶/K | Coefficient of thermal expansion | 10.8-14.2 | Dilatometry |
| Youngs_Modulus_GPa | GPa | Elastic modulus | 54.3-195.4 | Nanoindentation |
| Poissons_Ratio | - | Poisson's ratio | 0.29-0.36 | DMA/Nanoindentation |
| Shear_Viscosity_Pa_s | Pa·s | Viscosity for sintering | 5.5e8-2.2e15 | Calculated from sintering |
| Density_kg_m3 | kg/m³ | Material density | 5700-6100 | Helium pycnometry |
| Thermal_Conductivity_W_mK | W/(m·K) | Thermal conductivity | 2.7-6.0 | Laser flash analysis |
| Specific_Heat_J_kgK | J/(kg·K) | Specific heat capacity | 480-835 | DSC |
| Layer_Type | - | Material identifier | GDC_Barrier, SDC_Interlayer | - |

---

## Sintering Kinetics Data

### nio_ysz_sintering_stress.csv

Sintering stress and viscosity as functions of temperature, density, and time.

| Variable Name | Unit | Description | Range | Measurement Method |
|--------------|------|-------------|-------|-------------------|
| Temperature_C | °C | Sintering temperature | 1200-1500 | Type K thermocouple |
| Relative_Density | - | Relative density (ρ/ρₜₕ) | 0.55-0.90 | Archimedes method |
| Sintering_Stress_MPa | MPa | Driving stress for densification | 0.82-11.93 | Sinter-forging method |
| Bulk_Viscosity_Pa_s | Pa·s | Bulk viscosity | 8.0e5-4.5e8 | From densification rate |
| Shear_Viscosity_Pa_s | Pa·s | Shear viscosity | 6.7e5-3.8e8 | From densification rate |
| Heating_Rate_C_min | °C/min | Heating rate | 5 | Furnace control |
| Hold_Time_min | min | Isothermal hold time | 0-360 | Time measurement |
| Atmosphere | - | Sintering atmosphere | Air | Gas control |

**Notes**:
- Sintering stress increases with density and temperature
- Viscosity decreases exponentially with temperature
- Data critical for viscoplastic FEM models

### master_sintering_curve_params.csv

Parameters for Master Sintering Curve (MSC) models for each material.

| Variable Name | Unit | Description | Range | Derivation Method |
|--------------|------|-------------|-------|-------------------|
| Material | - | Material identifier | - | - |
| Activation_Energy_kJ_mol | kJ/mol | Activation energy for densification | 398.2-485.7 | Arrhenius analysis |
| Pre_exponential_Factor | 1/s | Pre-exponential factor | 8.95e11-5.82e13 | MSC fitting |
| Grain_Growth_Exponent_n | - | Grain growth exponent | 2.8-3.5 | Grain size analysis |
| Densification_Rate_Constant_K0 | 1/s | Rate constant at reference T | 1.24e8-3.42e8 | MSC fitting |
| Apparent_Activation_Energy_Q_kJ_mol | kJ/mol | Apparent activation energy | 398.2-485.7 | Temperature dependence |
| Critical_Density | - | Maximum achievable density | 0.92-0.95 | Experimental observation |
| Reference_Temperature_C | °C | Reference temperature | 1350-1450 | Model fitting |
| Gas_Constant_R | J/(mol·K) | Universal gas constant | 8.314 | Constant |

**Notes**:
- YSZ has highest activation energy (most temperature-sensitive)
- GDC shows fastest densification kinetics
- Parameters enable prediction of density vs. thermal history

### densification_rate_data.csv

Experimental densification rate measurements for various conditions.

| Variable Name | Unit | Description | Range | Measurement Method |
|--------------|------|-------------|-------|-------------------|
| Experiment_ID | - | Unique experiment identifier | EXP001-EXP050 | - |
| Material | - | Material type | NiO-YSZ, YSZ, GDC, SDC | - |
| Temperature_C | °C | Sintering temperature | 1200-1500 | Type K thermocouple |
| Initial_Density | - | Starting relative density | 0.50-0.55 | Archimedes method |
| Final_Density | - | Final relative density | 0.65-0.95 | Archimedes method |
| Time_min | min | Sintering duration | 120-240 | Time measurement |
| Densification_Rate_per_min | 1/min | Average densification rate | 0.000583-0.002917 | Calculated |
| Heating_Rate_C_min | °C/min | Heating rate to peak | 3-10 | Furnace control |
| Particle_Size_um | μm | Initial particle size (d₅₀) | 0.5-1.2 | Laser diffraction |
| Green_Density_percent | % | Green body density | 50-55 | Geometric measurement |

**Notes**:
- Densification rate = (Final_Density - Initial_Density) / Time_min
- Faster heating rates generally yield higher densification rates
- Smaller particle sizes enhance sintering kinetics

---

## Microstructural Evolution Data

### nio_ysz_microstructure_timeseries.csv

Time-series microstructural measurements during NiO-YSZ sintering.

| Variable Name | Unit | Description | Range | Measurement Method |
|--------------|------|-------------|-------|-------------------|
| Sample_ID | - | Unique sample identifier | MS001-MS056 | - |
| Temperature_C | °C | Sintering temperature | 1200-1500 | Type K thermocouple |
| Time_min | min | Sintering time | 0-360 | Time measurement |
| Porosity_percent | % | Total porosity | 5.5-45.0 | XCT/SEM image analysis |
| Mean_Pore_Size_um | μm | Average pore diameter | 0.42-2.85 | XCT 3D analysis |
| Pore_Size_Std_Dev_um | μm | Standard deviation of pore size | 0.24-1.42 | Statistical analysis |
| Mean_Grain_Size_um | μm | Average grain diameter | 0.82-9.98 | Linear intercept method |
| Grain_Size_Std_Dev_um | μm | Standard deviation of grain size | 0.28-4.95 | Statistical analysis |
| Tortuosity | - | Tortuosity factor (τ) | 1.35-4.82 | 3D path analysis (XCT) |
| Triple_Phase_Boundary_Density_um_um3 | μm/μm³ | TPB density | 0.185-0.662 | 3D segmentation analysis |
| Connectivity_Factor | - | Phase connectivity (0-1) | 0.42-0.99 | Percolation analysis |
| Imaging_Method | - | Characterization technique | SEM, XCT | - |

**Notes**:
- Time = 0 represents green body microstructure
- XCT used for times ≥120 min for better 3D characterization
- TPB density critical for electrochemical performance
- Connectivity factor: 1 = fully connected, 0 = isolated pores

### ysz_microstructure_timeseries.csv

Time-series microstructural measurements during YSZ sintering.

| Variable Name | Unit | Description | Range | Measurement Method |
|--------------|------|-------------|-------|-------------------|
| Sample_ID | - | Unique sample identifier | YSZ001-YSZ040 | - |
| Temperature_C | °C | Sintering temperature | 1300-1500 | Type K thermocouple |
| Time_min | min | Sintering time | 0-360 | Time measurement |
| Porosity_percent | % | Total porosity | 10.2-50.0 | XCT/SEM image analysis |
| Mean_Pore_Size_um | μm | Average pore diameter | 0.42-1.85 | XCT 3D analysis |
| Pore_Size_Std_Dev_um | μm | Standard deviation of pore size | 0.23-0.92 | Statistical analysis |
| Mean_Grain_Size_um | μm | Average grain diameter | 0.65-5.42 | Linear intercept method |
| Grain_Size_Std_Dev_um | μm | Standard deviation of grain size | 0.22-2.32 | Statistical analysis |
| Tortuosity | - | Tortuosity factor (τ) | 1.68-5.25 | 3D path analysis (XCT) |
| Ionic_Conductivity_S_cm | S/cm | Ionic conductivity (at temp) | 0.018-0.150 | AC impedance |
| Connectivity_Factor | - | Phase connectivity (0-1) | 0.38-0.97 | Percolation analysis |
| Imaging_Method | - | Characterization technique | SEM, XCT | - |

**Notes**:
- YSZ requires higher temperatures than NiO-YSZ
- Ionic conductivity measured in-situ during sintering
- Lower tortuosity preferred for electrolyte performance
- Connectivity critical for ionic transport

### pore_size_distribution_data.csv

Detailed pore size distribution data for selected samples.

| Variable Name | Unit | Description | Range | Measurement Method |
|--------------|------|-------------|-------|-------------------|
| Sample_ID | - | Reference to parent sample | MS001-YSZ040 | - |
| Temperature_C | °C | Sintering temperature | 1200-1500 | Type K thermocouple |
| Time_min | min | Sintering time | 0-360 | Time measurement |
| Pore_Size_Bin_um | μm | Pore size range | Various bins | Classification |
| Volume_Fraction_percent | % | Volume fraction in bin | 0.0-15.8 | XCT quantification |
| Number_Density_per_mm3 | 1/mm³ | Number of pores per volume | 0-582000 | 3D counting |
| Shape_Factor | - | Sphericity (0-1) | 0.68-0.97 | 3D shape analysis |
| Aspect_Ratio | - | Length/width ratio | 1.00-1.85 | 3D orientation analysis |

**Notes**:
- Pore size bins vary by material (smaller for YSZ)
- Shape factor: 1 = perfect sphere, lower = elongated
- Number density decreases dramatically with sintering
- Distribution evolves from broad to narrow with time

---

## Process Window Data

### sintering_profile_experiments.csv

Complete experimental matrix of sintering profiles and outcomes.

| Variable Name | Unit | Description | Range | Measurement Method |
|--------------|------|-------------|-------|-------------------|
| Experiment_ID | - | Unique experiment identifier | PWD001-PWD060 | - |
| Material | - | Material type | NiO-YSZ, YSZ | - |
| Heating_Rate_C_min | °C/min | Heating rate to peak | 1-10 | Furnace programming |
| Peak_Temperature_C | °C | Maximum temperature | 1200-1500 | Type K thermocouple |
| Hold_Time_min | min | Isothermal hold duration | 60-240 | Time control |
| Cooling_Rate_C_min | °C/min | Cooling rate from peak | 2-10 | Furnace programming |
| Atmosphere | - | Sintering atmosphere | Air | Gas control |
| Initial_Thickness_mm | mm | Green body thickness | 0.8-1.2 | Micrometer |
| Green_Density_percent | % | Initial relative density | 50-55 | Geometric measurement |
| Final_Density_percent | % | Final relative density | 68.2-95.2 | Archimedes method |
| Final_Warpage_mm | mm | Maximum surface deviation | 0.048-0.565 | 3D profilometry |
| Cracking | Yes/No | Presence of cracks | Binary | Optical/SEM inspection |
| Max_Warpage_Location | - | Location of maximum warpage | Edge, Corner | 3D map analysis |
| Comments | - | Experimental notes | Text | Observer notes |

**Notes**:
- Full factorial design covering key parameters
- Cracking more likely at high temperatures and fast rates
- Corner warpage indicates thermal gradient issues
- Baseline profiles defined for each material

### warpage_measurement_data.csv

Detailed 3D surface topography measurements for selected experiments.

| Variable Name | Unit | Description | Range | Measurement Method |
|--------------|------|-------------|-------|-------------------|
| Experiment_ID | - | Reference to parent experiment | PWD001-PWD051 | - |
| Material | - | Material type | NiO-YSZ, YSZ | - |
| Measurement_Method | - | Measurement technique | 3D_Profilometer | - |
| Point_X_mm | mm | X coordinate on sample | 0-50 | Position measurement |
| Point_Y_mm | mm | Y coordinate on sample | 0-50 | Position measurement |
| Height_Deviation_mm | mm | Z deviation from reference | 0-0.312 | Optical profilometry |
| Max_Slope_deg | degrees | Maximum local slope | 0.12-1.52 | Calculated from surface |
| Curvature_1_per_m | 1/m | Local curvature | 0.28-2.85 | Calculated from surface |
| Surface_Roughness_um | μm | RMS surface roughness | 1.85-5.12 | Profile analysis |
| Measurement_Uncertainty_mm | mm | Measurement uncertainty | 0.002-0.003 | Instrument specification |

**Notes**:
- Measurements at 6 points per sample (corners, edges, center)
- Reference plane defined at sample center
- Higher slopes indicate risk of cracking
- Surface roughness increases with temperature

### defect_characterization.csv

Comprehensive defect analysis for all experiments.

| Variable Name | Unit | Description | Range | Measurement Method |
|--------------|------|-------------|-------|-------------------|
| Experiment_ID | - | Reference to parent experiment | PWD001-PWD060 | - |
| Material | - | Material type | NiO-YSZ, YSZ | - |
| Defect_Type | - | Classification of defect | None, Surface_Pit, Microcrack, Through_Crack | Visual/SEM inspection |
| Defect_Location | - | Spatial location | None, Random, Edge, Corner | Mapping |
| Defect_Length_mm | mm | Maximum defect dimension | 0-48.5 | Optical measurement |
| Defect_Width_um | μm | Defect opening width | 0-725 | SEM measurement |
| Defect_Depth_um | μm | Defect depth | 0-1200 | Cross-section analysis |
| Number_of_Defects | count | Total defects observed | 0-45 | Visual counting |
| Severity_Score_1_10 | - | Defect severity rating | 0-10 | Expert assessment |
| Critical_Defect | Yes/No | Performance-limiting defect | Binary | Functional assessment |
| Formation_Stage | - | When defect formed | None, Heating, Hold, Cooling, Hold_Cooling | Thermal analysis |

**Notes**:
- Severity score: 0 = none, 1-3 = minor, 4-6 = moderate, 7-9 = severe, 10 = critical
- Through cracks always rated severity 9-10
- Most defects form during cooling due to thermal stress
- Edge/corner defects indicate thermal gradient problems

### thermal_profile_measurements.csv

Detailed thermal history measurements during sintering.

| Variable Name | Unit | Description | Range | Measurement Method |
|--------------|------|-------------|-------|-------------------|
| Experiment_ID | - | Reference to parent experiment | PWD001-PWD027 | - |
| Time_min | min | Elapsed time from start | 0-780 | Time measurement |
| Set_Temperature_C | °C | Controller setpoint | 25-1400 | Furnace programming |
| Measured_Temperature_Center_C | °C | Temperature at sample center | 25-1424 | Type K thermocouple |
| Measured_Temperature_Edge_C | °C | Temperature at sample edge | 25-1415 | Type K thermocouple |
| Measured_Temperature_Corner_C | °C | Temperature at sample corner | 24-1405 | Type K thermocouple |
| Temperature_Gradient_C_cm | °C/cm | Spatial temperature gradient | 0.05-4.38 | Calculated |
| Heating_Cooling_Rate_C_min | °C/min | Instantaneous rate | -44.6-10.24 | Calculated |
| Atmosphere_O2_percent | % | Oxygen concentration | 21.0 | Gas sensor |
| Sample_Position | - | Sample location in furnace | Center | Physical placement |

**Notes**:
- Multiple thermocouples embedded in sample
- Temperature gradient = (T_center - T_corner) / distance
- Negative rates indicate cooling
- Overshoot may occur during rapid heating

### action_space_boundaries.csv

Defined operational boundaries for process parameters (for RL action space).

| Variable Name | Unit | Description | Meaning |
|--------------|------|-------------|---------|
| Parameter | - | Process parameter name | Variable being constrained |
| Material | - | Material type | Applies to specific material or All |
| Minimum_Value | varies | Lower operational bound | Minimum safe/effective value |
| Maximum_Value | varies | Upper operational bound | Maximum safe/effective value |
| Optimal_Range_Min | varies | Lower bound of optimal range | Recommended minimum |
| Optimal_Range_Max | varies | Upper bound of optimal range | Recommended maximum |
| Unit | - | Parameter unit | Unit of measurement |
| Constraint_Type | - | Type of constraint | Process, Equipment, Material, Safety, Quality |
| Physical_Limit | varies | Absolute physical limit | Hard limit (equipment/physics) |
| Safety_Factor | - | Margin from physical limit | Ratio: Physical_Limit / Maximum_Value |

**Notes**:
- Action space for RL should respect Minimum_Value to Maximum_Value
- Optimal ranges based on experimental success rates
- Safety factors provide margin from equipment limits
- Constraint types indicate source of limitation

---

## Units and Conventions

### Standard SI Units
- Temperature: °C (Celsius)
- Length: mm, μm, m
- Mass: kg
- Time: min (minutes), s (seconds)
- Pressure/Stress: Pa, MPa
- Density: kg/m³, relative (ρ/ρₜₕ)

### Relative Quantities
- Relative Density: Ratio of actual to theoretical density (dimensionless, 0-1 or 0-100%)
- Tortuosity: Ratio of actual path length to straight-line distance (≥1)
- Connectivity Factor: Fraction of connected phase (0-1)

### Abbreviations
- CTE: Coefficient of Thermal Expansion
- DMA: Dynamic Mechanical Analysis
- DSC: Differential Scanning Calorimetry
- SEM: Scanning Electron Microscopy
- XCT: X-ray Computed Tomography
- TPB: Triple Phase Boundary
- MSC: Master Sintering Curve
- FEM: Finite Element Method

---

**Last Updated**: 2025-10-25
