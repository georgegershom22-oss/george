# Experimental Methodology Documentation

## Overview

This document provides detailed information about the experimental procedures, instrumentation, and analysis methods used to generate the Phase 1 foundational and calibration dataset for SOFC sintering optimization.

## Sample Preparation

### Materials Sourcing

**NiO-YSZ Composite**
- NiO powder: Sigma-Aldrich, 99.9% purity, d50 = 0.8 μm
- YSZ powder: Tosoh TZ-8Y, 8 mol% Y2O3, d50 = 0.5 μm
- Mixing ratio: 50:50 vol% (NiO:YSZ)
- Ball milling: 24 hours in ethanol with YSZ media

**YSZ Electrolyte**
- Powder: Tosoh TZ-8Y, 8 mol% Y2O3, d50 = 0.6 μm
- As-received powder used without further processing

**GDC and SDC**
- GDC: Gd0.2Ce0.8O2-x, Fuel Cell Materials, d50 = 0.7 μm
- SDC: Sm0.2Ce0.8O2-x, Fuel Cell Materials, d50 = 0.65 μm

### Green Body Fabrication

**Tape Casting Process**
1. Slurry preparation
   - Powder loading: 40 wt% solids
   - Binder: PVB (polyvinyl butyral), 3 wt% of powder
   - Plasticizer: DBP (dibutyl phthalate), 2 wt% of powder
   - Solvent: Ethanol/toluene (1:1)
   - Dispersant: Triton X-100, 1 wt% of powder

2. Casting parameters
   - Doctor blade gap: 200-500 μm (adjusted for final thickness)
   - Casting speed: 1 cm/s
   - Drying: 24 hours at room temperature

3. Cutting and lamination
   - Sample size: 50 mm x 50 mm
   - Lamination: 70°C, 10 MPa for 5 minutes (if multi-layer)

**Uniaxial Pressing (alternative method)**
- Powder preparation: With 2 wt% PVA binder
- Die size: 50 mm diameter
- Pressing pressure: 50-150 MPa
- Drying: 80°C for 2 hours

### Binder Burnout

Standard burnout profile used for all samples:
- 1°C/min to 300°C, hold 2 hours (solvent/plasticizer removal)
- 0.5°C/min to 600°C, hold 4 hours (binder decomposition)
- Cool naturally to room temperature
- Atmosphere: Air with adequate ventilation

## Material Property Characterization

### Coefficient of Thermal Expansion (CTE)

**Instrument**: Netzsch DIL 402 C push-rod dilatometer

**Procedure**:
1. Sample geometry: 25 mm length x 5 mm diameter cylinders
2. Sample preparation: Pre-sintered to full density
3. Measurement conditions:
   - Temperature range: 25°C to 1600°C
   - Heating/cooling rate: 5°C/min
   - Atmosphere: Air (50 ml/min flow)
   - Push rod: Alumina
4. Calibration: Using NIST SRM alumina standard
5. CTE calculation: Linear regression of thermal expansion curve

**Data Analysis**:
- Instantaneous CTE: α(T) = (1/L0)(dL/dT)
- Temperature intervals: 25°C increments
- Uncertainty: ±0.5% from triplicate measurements

### Elastic Properties

**Instrument**: KLA iNano nanoindenter with Berkovich tip

**Procedure**:
1. Sample preparation:
   - Polished to 1 μm diamond finish
   - Ultrasonic cleaning in ethanol
2. Indentation parameters:
   - Loading rate: 10 mN/s
   - Maximum load: 500 mN
   - Hold time: 10 seconds
   - Unloading: 5 seconds
3. Temperature control: Heated sample stage (25-800°C)
4. Measurements: 25 indents per temperature per sample

**Data Analysis**:
- Youngs modulus: Oliver-Pharr method
- Poisson ratio: Combined with ultrasonic measurements
- High-temperature data: Extrapolation using power-law fits

### Thermal Conductivity

**Instrument**: Netzsch LFA 467 HyperFlash laser flash apparatus

**Procedure**:
1. Sample geometry: 10 mm diameter x 2 mm thickness
2. Coating: Graphite spray on both sides (IR absorption)
3. Measurement conditions:
   - Temperature range: 25°C to 1500°C
   - Atmosphere: Argon (99.999%)
   - Laser pulse: 0.3 ms duration
4. Heat capacity: DSC measurements on same samples
5. Density: Temperature-dependent values from dilatometry

**Data Analysis**:
- Thermal diffusivity: Cape-Lehman model
- Thermal conductivity: k = α × ρ × Cp
- Uncertainty: ±5% (combined sources)

## Sintering Kinetics Characterization

### Dilatometry

**Instrument**: Netzsch DIL 402 E horizontal pushrod dilatometer

**Procedure**:
1. Sample geometry: 5 mm diameter x 3-5 mm height green pellets
2. Heating rates tested: 1, 2, 3, 5, 7, 10°C/min
3. Peak temperatures: 1200, 1250, 1300, 1350, 1400, 1450, 1500°C
4. Hold times: 0, 30, 60, 120, 180, 240, 360 minutes
5. Atmosphere: Air (50 ml/min)
6. Data acquisition: 1 point per second

**Data Analysis**:
- Linear shrinkage: ΔL/L0 = (L - L0)/L0
- Densification: Assuming isotropic shrinkage, ρ/ρ0 = (1 + ΔL/L0)^-3
- Densification rate: dρ/dt from numerical differentiation
- Master Sintering Curve: Θ(T,t) = ∫[dt/T]exp(-Q/RT)

### Sinter-Forging

**Instrument**: Custom high-temperature mechanical testing system

**Procedure**:
1. Sample geometry: 10 mm diameter x 5 mm height
2. Uniaxial load: 1-50 MPa (varied by experiment)
3. Temperature: Isothermal at 1200-1450°C
4. Measurement: Simultaneous displacement and load
5. Atmosphere: Air

**Data Analysis**:
- Sintering stress: σs = (3/2)(dρ/dt)(η/ρ)
- Viscosity: From creep rate under applied stress
- Bulk and shear viscosity: From hydrostatic vs. deviatoric components

### Interrupted Sintering Tests

**Procedure**:
1. Sintering conditions: Various T-t profiles
2. Quenching: Rapid furnace opening, samples cool in air
3. Target temperatures: 1200, 1250, 1300, 1350, 1400, 1450, 1500°C
4. Time points: 0, 30, 60, 120, 180, 240, 360 minutes
5. Samples per condition: Minimum 3 for statistical validity

**Quality Control**:
- Temperature overshoot: <5°C monitored via control thermocouple
- Quench rate: >100°C/min in first minute verified
- Sample integrity: Visual inspection before characterization

## Microstructural Characterization

### Scanning Electron Microscopy (SEM)

**Instrument**: JEOL JSM-7800F field emission SEM

**Sample Preparation**:
1. Mounting: Cold-mount epoxy resin
2. Grinding: SiC papers (320, 600, 1200 grit)
3. Polishing: Diamond suspension (6, 3, 1, 0.25 μm)
4. Final polish: Colloidal silica (0.05 μm) for 30 minutes
5. Cleaning: Ultrasonic in DI water and ethanol
6. Coating: 5 nm Pt/Pd sputter coating

**Imaging Conditions**:
- Acceleration voltage: 15 kV
- Working distance: 10 mm
- Detector: Secondary electron (SEI) and backscattered (BEI)
- Magnifications: 500x, 2000x, 5000x, 10000x
- Images per sample: Minimum 10 random locations

**Image Analysis**:
- Software: ImageJ/Fiji with custom plugins
- Porosity: Threshold segmentation, area fraction calculation
- Pore size: Individual pore measurement, equivalent circular diameter
- Grain size: Linear intercept method (ASTM E112)
- Minimum features: 500 pores, 200 grains per sample

### X-ray Computed Tomography (XCT)

**Instrument**: Zeiss Xradia 520 Versa

**Scanning Parameters**:
1. Sample preparation: Cylindrical samples 2-3 mm diameter
2. Scan settings:
   - Source voltage: 80-140 kV (optimized per sample)
   - Power: 7 W
   - Exposure time: 3-10 seconds per projection
   - Projections: 1601 over 360 degrees
   - Voxel size: 0.5-2.0 μm (depending on sample size)
3. Scan duration: 4-8 hours per sample

**3D Reconstruction and Analysis**:
- Reconstruction: XMReconstructor (Zeiss)
- Visualization and analysis: Avizo 2020.2
- Segmentation:
  - Manual threshold selection
  - Watershed algorithm for pore separation
  - Manual correction as needed
- Measurements:
  - Porosity: Volume fraction
  - Pore size distribution: Individual pore volumes
  - Tortuosity: Geodesic distance / Euclidean distance
  - Connectivity: Percolation analysis
  - TPB density: 3-phase segmentation and interface detection

### Triple Phase Boundary (TPB) Analysis

**Specific to NiO-YSZ Composite**:

1. 3-Phase segmentation:
   - Phase 1: NiO (grayscale threshold)
   - Phase 2: YSZ (intermediate grayscale)
   - Phase 3: Pore (lowest grayscale)

2. TPB identification:
   - Voxels where all three phases meet
   - Edge detection algorithm
   - Verification with 2D SEM-BSE images

3. TPB density calculation:
   - Total TPB length (μm) / Sample volume (μm³)
   - Active TPB: Only percolating phases counted

## Sintering Experiments and Warpage Measurement

### Furnace Setup

**Equipment**: Nabertherm LHT 04/18 high-temperature box furnace

**Specifications**:
- Maximum temperature: 1800°C
- Heating elements: MoSi2
- Working volume: 4L (120 x 240 x 140 mm)
- Temperature uniformity: ±5°C at 1400°C (per manufacturer)
- Control: Programmable with 20 segments

**Sample Setup**:
1. Substrate: Porous alumina setter plate
2. Sample placement: Center of furnace
3. Thermocouples: 
   - Control TC: Adjacent to sample
   - Measurement TCs: Embedded at center, edge, and corner (some experiments)
4. Atmosphere: Air (natural convection)

### Sintering Profile Execution

**Standard Profile Components**:
1. Heating segment: Linear ramp at specified rate
2. Hold segment: Isothermal at peak temperature
3. Cooling segment: Controlled or natural cooling

**Monitoring**:
- Temperature: Logged every 10 seconds
- Temperature deviation: <±3°C from setpoint during hold
- Atmosphere: Visual check through observation port

**Post-Sintering**:
- Natural cooling to <100°C before removal
- Immediate visual inspection for obvious defects
- Photography for documentation

### 3D Profilometry for Warpage Measurement

**Instrument**: Keyence VR-5000 wide-area 3D measurement system

**Measurement Procedure**:
1. Sample cleaning: Compressed air to remove dust
2. Placement: On flat reference stage (granite surface plate)
3. Scan settings:
   - Measurement mode: High-accuracy (HDR)
   - Lens: 12x objective
   - Field of view: Multiple fields stitched
   - Vertical resolution: 0.1 μm
   - Lateral resolution: 1 μm
4. Stitching: Automatic with 10% overlap
5. Scan time: 3-5 minutes per sample

**Data Analysis**:
- Reference plane: Least-squares fit plane through sample
- Warpage: Maximum deviation from reference plane
- Location: X-Y coordinates of maximum warpage
- Curvature: Second derivative of surface
- Slope: First derivative, maximum value recorded
- Surface roughness: RMS of high-frequency components

**Uncertainty Analysis**:
- Instrument precision: ±0.1 μm (vertical)
- Repeatability: ±2 μm (from 5 repeat measurements)
- Total uncertainty: ±3 μm

## Defect Characterization

### Visual Inspection

**Procedure**:
1. Lighting: Diffuse LED illumination
2. Magnification: 10x stereo microscope
3. Documentation: High-resolution photography
4. Classification:
   - None: No visible defects
   - Surface pits: Isolated surface depressions
   - Microcrack: Cracks <5 mm length, <50 μm opening
   - Through crack: Penetrates full thickness

### SEM Inspection

**For Detailed Defect Analysis**:
1. Sample preparation: As-sintered surface (no polishing)
2. Imaging: Secondary electron mode
3. Measurements:
   - Crack length: End-to-end measurement
   - Crack opening: Width at widest point
   - Crack depth: From fracture cross-sections

### Severity Scoring

**Scoring Criteria** (0-10 scale):
- 0: No defects
- 1-2: Minor surface pits, <10 total, <0.5 mm
- 3-4: Multiple pits or single microcrack
- 5-6: Multiple microcracks or pits near edges
- 7-8: Large microcracks or isolated through-crack
- 9-10: Multiple through-cracks or sample fragmentation

**Critical Defect Definition**:
- Any through-crack
- Microcrack at edge >5 mm
- Extensive network of surface cracks
- Any defect preventing functional use

## Data Processing and Quality Control

### Density Measurement (Archimedes Method)

**Equipment**: 
- Analytical balance: 0.1 mg readability
- Density kit with immersion vessel

**Procedure**:
1. Dry mass: Sample dried at 120°C for 2 hours, weighed in air
2. Saturated mass: Sample boiled in DI water 2 hours, weighed in air
3. Immersed mass: Sample weighed while suspended in water
4. Calculation: ρ = (Mdry)/(Msaturated - Mimmersed) × ρwater
5. Relative density: ρrelative = ρmeasured / ρtheoretical

**Theoretical Densities**:
- NiO: 6.67 g/cm³
- YSZ (8YSZ): 5.90 g/cm³
- NiO-YSZ (50-50 vol%): 6.05 g/cm³ (calculated)
- GDC: 7.22 g/cm³
- SDC: 7.14 g/cm³

**Uncertainty**: ±0.5% from replicate measurements

### Statistical Analysis

**Replication**:
- Material properties: n=3 samples per condition
- Sintering kinetics: n=3 samples per condition
- Microstructure: n=3 samples per condition (average of 10 images each)
- Process window: n=1 per unique condition (60 total conditions)

**Data Reporting**:
- Central tendency: Mean values reported
- Variability: Standard deviation calculated
- Outliers: Grubbs test (α = 0.05) applied
- Missing data: Indicated as empty cells or NaN

### Calibration and Standards

**Regular Calibrations**:
- Thermocouples: Monthly against NIST-traceable standard
- Balance: Daily with calibration weights
- Dilatometer: Quarterly with alumina standard
- Nanoindenter: Weekly with fused silica standard
- Laser flash: Per sample with Pyroceram standard

**Traceability**:
- All measurements traceable to NIST or equivalent standards
- Calibration certificates maintained
- Instrument logs recording all calibrations

## Safety and Environmental Considerations

**Safety Measures**:
- High-temperature operations: PPE including heat-resistant gloves, face shield
- Chemical handling: Fume hood for organic solvents
- X-ray systems: Radiation safety protocols, dosimetry badges
- SEM: Vacuum safety, high-voltage interlocks

**Waste Management**:
- Organic solvents: Collected and disposed as hazardous waste
- Ceramic dust: HEPA vacuum and dust control measures
- Polishing waste: Settled and disposed as solid waste

**Environmental Control**:
- Laboratory temperature: 20 ± 2°C
- Humidity: 40-60% RH
- Vibration isolation: For profilometry and nanoindentation

## References and Standards

**Applicable Standards**:
- ASTM E112: Grain size determination
- ASTM C373: Bulk density and water absorption
- ISO 15901: Pore size distribution (mercury porosimetry)
- ISO 18754: Nanoindentation testing

**Literature Methods**:
- Master Sintering Curve: Su & Johnson (1996)
- Phase-field sintering: Wang (2006)
- TPB quantification: Wilson et al. (2006)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-25
**Approved By**: Materials Characterization Laboratory
