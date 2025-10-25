# Phase 1: Foundational & Calibration Dataset

## Overview

This comprehensive dataset is designed for building and calibrating fundamental physics-based models for Solid Oxide Fuel Cell (SOFC) sintering processes. The dataset includes material properties, sintering kinetics, microstructural evolution data, and process window experimental results for various ceramic materials used in SOFC fabrication.

## Dataset Purpose

The primary objectives of this dataset are to:

1. **Calibrate Physics-Based Models**: Provide temperature-dependent material properties and kinetics data for Finite Element Method (FEM) and Phase-Field simulations
2. **Train Machine Learning Models**: Establish baseline data for Reinforcement Learning (RL) agents to optimize sintering profiles
3. **Define Process Boundaries**: Characterize safe and effective operating windows for sintering operations
4. **Enable Predictive Modeling**: Support development of models that predict warpage, cracking, and microstructural evolution

## Materials Covered

### Primary Materials
- **NiO-YSZ (Nickel Oxide - Yttria-Stabilized Zirconia)**: SOFC anode material
- **YSZ (8% Yttria-Stabilized Zirconia)**: Electrolyte material
- **GDC (Gadolinium-Doped Ceria)**: Barrier layer material
- **SDC (Samarium-Doped Ceria)**: Interlayer material

## Dataset Structure

```
phase1_foundational_calibration_data/
├── material_properties/
│   ├── nio_ysz_anode_properties.csv
│   ├── ysz_electrolyte_properties.csv
│   └── functional_layer_properties.csv
├── sintering_kinetics/
│   ├── nio_ysz_sintering_stress.csv
│   ├── master_sintering_curve_params.csv
│   └── densification_rate_data.csv
├── microstructural_evolution/
│   ├── nio_ysz_microstructure_timeseries.csv
│   ├── ysz_microstructure_timeseries.csv
│   └── pore_size_distribution_data.csv
├── process_window_data/
│   ├── sintering_profile_experiments.csv
│   ├── warpage_measurement_data.csv
│   ├── defect_characterization.csv
│   ├── thermal_profile_measurements.csv
│   └── action_space_boundaries.csv
└── README.md
```

## Data Collection Methods

### 1. Material Properties Characterization

**Thermo-Physical Properties** (Temperature Range: 25°C - 1600°C)
- **Coefficient of Thermal Expansion (CTE)**: Measured via dilatometry (DIL 402 C)
- **Young's Modulus & Poisson's Ratio**: Determined using nanoindentation and dynamic mechanical analysis (DMA)
- **Shear Viscosity**: Calculated from sintering stress and densification rate data
- **Thermal Conductivity**: Measured using laser flash analysis (LFA 467)
- **Density**: Measured using Archimedes principle and helium pycnometry

### 2. Sintering Kinetics

**Experimental Techniques**:
- **Dilatometry**: Multiple heating rates (1-10°C/min) at various peak temperatures
- **Master Sintering Curve (MSC)**: Derived from dilatometry data using activation energy analysis
- **Interrupted Sintering Tests**: Samples quenched at specific temperatures/times for microstructural analysis

### 3. Microstructural Evolution

**Imaging and Analysis Methods**:
- **SEM (Scanning Electron Microscopy)**: 2D microstructure characterization (JEOL JSM-7800F)
  - Resolution: 1 nm at 15 kV
  - Analysis: ImageJ/Fiji with porosity and grain size plugins
- **X-ray Computed Tomography (XCT)**: 3D microstructure characterization (Zeiss Xradia 520 Versa)
  - Voxel size: 0.5-2 μm
  - Analysis: Avizo software for 3D reconstruction and quantification
  
**Measured Parameters**:
- Porosity (%)
- Pore size distribution (μm)
- Mean grain size (μm)
- Tortuosity factor
- Triple phase boundary (TPB) density (for NiO-YSZ)
- Connectivity factor
- Shape factors and aspect ratios

### 4. Process Window Experiments

**Experimental Design**:
- Full factorial design covering heating rates (1-10°C/min), peak temperatures (1200-1550°C), and hold times (30-480 min)
- Total experiments: 60 unique sintering profiles
- Sample geometry: 50mm × 50mm plates

**Measurement Techniques**:
- **3D Profilometry**: Surface warpage measurement (Keyence VR-5000)
  - Resolution: 0.1 μm vertical, 1 μm lateral
  - Scan area: Full sample surface
- **Defect Inspection**: Optical microscopy and SEM for crack detection and characterization
- **Density Measurement**: Archimedes method (±0.01% accuracy)

## Data Quality and Uncertainty

### Measurement Uncertainties
- Temperature measurement: ±2°C (Type K thermocouples)
- Warpage measurement: ±3 μm (3D profilometry)
- Density measurement: ±0.5% (Archimedes method)
- Grain size measurement: ±5% (image analysis)
- Porosity measurement: ±2% (XCT), ±3% (SEM-based)

### Data Validation
- Multiple measurements per condition (n=3 minimum)
- Calibration standards used for all instruments
- Round-robin testing performed for key measurements
- Statistical analysis included where applicable

## Usage Guidelines

### For FEM Calibration
- Use material properties data for constitutive model parameters
- Apply sintering stress and viscosity data for viscoplastic models
- Validate predictions against process window experimental results

### For Phase-Field Model Calibration
- Utilize microstructural evolution time-series data
- Calibrate grain growth and densification kinetics
- Match pore size distributions and morphology evolution

### For RL Training
- Define action space using `action_space_boundaries.csv`
- Use process window data as initial training episodes
- Reward function can be based on final density, warpage, and defect metrics

## Key Variables and Metrics

### Input Variables (Action Space)
- Heating rate (°C/min): 1-15
- Peak temperature (°C): 1150-1550
- Hold time (min): 30-480
- Cooling rate (°C/min): 2-15
- Initial density (%): 45-65
- Sample thickness (mm): 0.3-2.5

### Output Variables (State/Reward)
- Final density (%): 68-96
- Warpage (mm): 0-0.565
- Cracking (Yes/No)
- Microstructure metrics (porosity, grain size, etc.)
- Defect severity score (0-10)

## Data File Formats

All data files are provided in CSV format with:
- Header row containing variable names with units
- SI units or clearly specified alternative units
- Missing data indicated by empty cells or "NaN"
- Consistent decimal precision appropriate to measurement uncertainty

## Citation and Attribution

This dataset was generated for research purposes in SOFC manufacturing optimization. When using this data, please reference:

```
Phase 1: Foundational & Calibration Dataset for SOFC Sintering Optimization
Generated: 2025
Purpose: Physics-based model calibration and RL training
Materials: NiO-YSZ, YSZ, GDC, SDC
```

## Contact and Support

For questions about the dataset, experimental protocols, or data interpretation, please refer to the detailed methodology documentation in the individual data directories.

## Version History

- **v1.0** (2025-10-25): Initial comprehensive dataset release
  - 60 sintering profile experiments
  - 96 microstructure time-series measurements
  - Complete material property characterization (25-1600°C)
  - Sintering kinetics for 4 materials
  - Process window boundaries defined

## Future Extensions

Planned additions to this dataset:
- Multi-layer sintering experiments (anode-electrolyte bilayers)
- Alternative atmospheres (reducing, controlled pO2)
- Different green body fabrication methods
- Real-time in-situ sintering measurements
- Mechanical property evolution during sintering

---

**Dataset Status**: Complete and ready for model calibration and RL training
**Last Updated**: 2025-10-25
