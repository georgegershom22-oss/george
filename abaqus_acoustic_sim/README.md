# Abaqus Acoustic Transmission Loss Simulation Framework

## Complete Implementation for Stratified Media Acoustic Analysis

### Overview

This framework provides a comprehensive Abaqus-based solution for simulating acoustic transmission loss (TL) in stratified fluid media. It implements both discrete layered and continuous gradient stratification models, with full support for frequency-dependent analysis and post-processing.

### Features

- **Dual Stratification Models**:
  - Discrete layered media with sharp interfaces
  - Continuous gradients using field variables (thermocline-like profiles)
  
- **Complete Physics Implementation**:
  - Helmholtz equation solver for linear acoustics
  - Plane wave incidence with proper impedance matching
  - Non-reflecting boundary conditions (Sommerfeld radiation)
  - Frequency-dependent material properties
  
- **Automated Workflow**:
  - Python-based model generation in Abaqus/CAE
  - Parametric geometry and mesh generation
  - Frequency sweep analysis (100-5000 Hz)
  - Comprehensive post-processing and visualization

### Directory Structure

```
abaqus_acoustic_sim/
├── scripts/
│   └── acoustic_model_generator.py    # Main CAE model generator
├── input_files/
│   ├── acoustic_layered_2d.inp       # 2D layered model
│   ├── acoustic_gradient_2d.inp      # 2D gradient model
│   └── acoustic_3d_example.inp       # 3D model example
├── post_processing/
│   ├── extract_tl_alpha.py           # TL/absorption extraction
│   └── visualize_acoustic_field.py   # Field visualization
├── examples/
│   └── run_examples.sh               # Example execution scripts
└── docs/
    └── theory_notes.pdf              # Theoretical background

```

## Installation Requirements

### Software Requirements
- Abaqus 2020 or later (with Acoustic module license)
- Python 2.7/3.x (compatible with Abaqus Python)
- NumPy, SciPy, Matplotlib (for post-processing)
- FFmpeg (optional, for animations)

### Python Dependencies
```bash
pip install numpy scipy matplotlib pandas
```

## Quick Start Guide

### 1. Generate Model in Abaqus/CAE

#### Option A: Interactive CAE Session
```bash
# Start Abaqus CAE
abaqus cae

# In Python console or script editor:
execfile('scripts/acoustic_model_generator.py')

# Or for Python 3:
exec(open('scripts/acoustic_model_generator.py').read())
```

#### Option B: Command Line Execution
```bash
# Run model generation script
abaqus cae script=scripts/acoustic_model_generator.py

# Or run without GUI
abaqus cae noGUI=scripts/acoustic_model_generator.py
```

### 2. Run Pre-built Input Files

```bash
# Run layered model
abaqus job=acoustic_layered input=input_files/acoustic_layered_2d.inp cpus=4

# Run gradient model  
abaqus job=acoustic_gradient input=input_files/acoustic_gradient_2d.inp cpus=4

# Monitor job progress
abaqus job=acoustic_layered status
```

### 3. Post-Process Results

```bash
# Extract TL and absorption coefficient
abaqus python post_processing/extract_tl_alpha.py acoustic_layered.odb 6.0

# Create visualizations
abaqus python post_processing/visualize_acoustic_field.py acoustic_layered.odb 1000
```

## Detailed Usage Instructions

### Model Configuration

#### Geometry Parameters
Edit `acoustic_model_generator.py`:
```python
self.geometry = {
    'length': 10.0,      # Domain length (m)
    'width': 2.0,        # Domain width (m)  
    'height': 2.0        # Domain height (m) for 3D
}
```

#### Frequency Range
```python
self.frequency_params = {
    'f_min': 100.0,      # Min frequency (Hz)
    'f_max': 5000.0,     # Max frequency (Hz)
    'f_step': 25.0       # Frequency increment (Hz)
}
```

#### Mesh Resolution
```python
self.mesh_params = {
    'elem_per_wavelength': 12,  # λ/12 minimum
    'max_elem_size': 0.05,      # Maximum element size (m)
    'min_elem_size': 0.01       # Minimum element size (m)
}
```

### Material Properties

#### Layered Stratification
```python
# Define layers (example: 5-layer ocean model)
layer_properties = [
    {'rho': 950.0, 'K': 2.00e9},   # Warm surface layer
    {'rho': 975.0, 'K': 2.05e9},   # Transition
    {'rho': 1000.0, 'K': 2.10e9},  # Middle layer
    {'rho': 1025.0, 'K': 2.15e9},  # Transition
    {'rho': 1050.0, 'K': 2.20e9}   # Cold deep layer
]
```

#### Continuous Gradient
```python
# Thermocline profile (tanh function)
gradient_type = 'tanh'  # Options: 'linear', 'exponential', 'tanh'

# Custom gradient via field variables
def custom_gradient(z_normalized):
    # z_normalized: 0 (top) to 1 (bottom)
    thermocline_center = 0.5
    thermocline_width = 0.1
    profile = 0.5 * (1 + np.tanh((z_normalized - thermocline_center) / 
                                  thermocline_width))
    rho = 950 + 100 * profile  # 950-1050 kg/m³
    K = 2.0e9 + 0.2e9 * profile  # 2.0-2.2 GPa
    return rho, K
```

### Running Simulations

#### Complete Workflow Example
```python
# In Abaqus/CAE Python:
from acoustic_model_generator import AcousticStratifiedModel

# Create model instance
model = AcousticStratifiedModel(model_name='MyAcousticTL')

# Configure parameters
model.geometry['length'] = 15.0  # 15m domain
model.frequency_params['f_max'] = 10000.0  # Up to 10 kHz

# Build layered model
job1 = model.build_layered_model(n_layers=7, dimension='2D')
job1.submit()
job1.waitForCompletion()

# Build gradient model
model2 = AcousticStratifiedModel(model_name='MyGradientTL')
job2 = model2.build_gradient_model(gradient_type='tanh', dimension='2D')
job2.submit()
job2.waitForCompletion()
```

### Post-Processing

#### Extract Transmission Loss
```python
from extract_tl_alpha import AcousticPostProcessor

# Initialize processor
processor = AcousticPostProcessor('acoustic_layered.odb', 
                                 probe_separation=6.0)

# Extract and calculate
processor.open_database()
processor.extract_pressure_data()
tl = processor.calculate_transmission_loss()
alpha = processor.calculate_absorption_coefficient()

# Fit models and export
processor.fit_absorption_models()
processor.export_to_csv('results.csv')
processor.plot_results(save_plots=True)
processor.close_database()
```

#### Visualize Acoustic Fields
```python
from visualize_acoustic_field import AcousticFieldVisualizer

# Create visualizer
viz = AcousticFieldVisualizer('acoustic_gradient.odb')

# Extract field at 1000 Hz
viz.extract_field_data(frequency_index=40)  # For 1000 Hz

# Create plots
viz.create_2d_contour_plot(1000.0, component='magnitude')
viz.create_2d_contour_plot(1000.0, component='phase')

# Animate wave propagation
viz.create_wave_animation(1000.0, output_file='wave_1khz.mp4')
```

## Physical Models and Theory

### Governing Equations

The simulation solves the Helmholtz equation for time-harmonic acoustics:
```
∇²p + k²p = 0
```
where:
- `p` = complex pressure amplitude
- `k = ω/c` = wavenumber
- `ω = 2πf` = angular frequency
- `c = √(K/ρ)` = sound speed

### Stratification Models

#### 1. Discrete Layers
- Sharp density/sound speed contrasts
- Reflection/transmission at interfaces
- Suitable for well-mixed layer models

#### 2. Continuous Gradients
- Smooth property variations
- Ray bending and mode coupling
- Realistic for thermoclines/haloclines

### Transmission Loss Calculation

```
TL(f) = 20 log₁₀(|p_in|/|p_out|) [dB]
```

### Absorption Coefficient

Amplitude absorption:
```
α_amp = (ln(10)/20) × TL/Δx [Np/m]
```

Intensity absorption:
```
α_int = (ln(10)/10) × TL/Δx [Np/m]
```

## Validation Examples

### Example 1: Homogeneous Medium
- Expected: TL ≈ 0 dB (no stratification)
- Simulated: TL < 0.5 dB (numerical precision)

### Example 2: Two-Layer System
- Analytical solution available for plane waves
- Agreement within 1% for adequate mesh resolution

### Example 3: Linear Gradient
- Comparison with WKB approximation
- Good agreement for gradual gradients

## Advanced Features

### Custom Material Properties

#### Frequency-Dependent Properties
```python
# In material definition
mat.AcousticMedium(
    bulkTable=[(K1, f1), (K2, f2), ...],  # Frequency-dependent K
    volumetricTable=[(rho1, f1), (rho2, f2), ...]  # Frequency-dependent ρ
)
```

#### Temperature-Dependent Properties
```python
# Define temperature field
model.Temperature(name='TempField', ...)

# Material with temperature dependence
mat.AcousticMedium(
    temperatureDependencyB=ON,
    bulkTable=[(K1, T1), (K2, T2), ...]
)
```

### Parallel Processing

```bash
# Multi-CPU execution
abaqus job=acoustic_model cpus=8 mp_mode=threads

# Domain decomposition for large models
abaqus job=acoustic_model cpus=16 parallel=domain
```

### Parametric Studies

```python
# Parameter sweep script
import numpy as np

frequencies = [100, 500, 1000, 2000, 5000]
layer_counts = [3, 5, 7, 10]

results = {}
for n_layers in layer_counts:
    model = AcousticStratifiedModel(f'TL_layers_{n_layers}')
    job = model.build_layered_model(n_layers=n_layers)
    job.submit()
    job.waitForCompletion()
    
    # Process results
    processor = AcousticPostProcessor(f'{job.name}.odb')
    processor.open_database()
    processor.extract_pressure_data()
    results[n_layers] = processor.calculate_transmission_loss()
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Convergence Problems
- **Issue**: SSD step fails to converge
- **Solution**: Check material properties consistency, ensure ρ and K are positive

#### 2. Unexpected TL Values
- **Issue**: Very high or negative TL
- **Solution**: Verify probe placement, check boundary conditions

#### 3. Memory Errors
- **Issue**: Out of memory for large 3D models
- **Solution**: Reduce mesh density, use domain decomposition

#### 4. Missing Pressure Output
- **Issue**: P field not available in ODB
- **Solution**: Ensure field output request includes 'P' variable

### Best Practices

1. **Mesh Convergence**: Always perform mesh refinement study
2. **Domain Size**: Keep probes > λ from boundaries
3. **Frequency Resolution**: Use adequate frequency points for smooth curves
4. **Material Properties**: Ensure c = √(K/ρ) is physically reasonable

## Output Files

### Simulation Outputs
- `*.odb` - Abaqus output database
- `*.dat` - ASCII results file
- `*.msg` - Message file with warnings/errors
- `*.sta` - Status file for monitoring

### Post-Processing Outputs
- `*_results.csv` - TL and absorption data
- `*_statistics.txt` - Summary statistics
- `*_plots.png` - TL and absorption plots
- `*.mp4` - Wave propagation animations

## References

1. Abaqus Acoustic Analysis Guide, Dassault Systèmes
2. Computational Ocean Acoustics, Jensen et al. (2011)
3. Fundamentals of Acoustics, Kinsler et al. (2000)
4. Ocean Acoustic Propagation by Finite Difference Methods, Lee & McDaniel (1988)

## Contact and Support

For questions or issues with this framework:
- Check Abaqus documentation for element types and keywords
- Verify acoustic module license availability
- Consult theory references for physical model limitations

## License

This framework is provided as-is for educational and research purposes.
Users should validate results against analytical solutions or experimental data
for their specific applications.

---

*Last Updated: 2025-10-19*
*Version: 1.0.0*