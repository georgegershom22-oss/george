# Abaqus Acoustic Simulation Examples

This document provides detailed examples of using the acoustic transmission loss simulation suite for various scenarios and parameter studies.

## Example 1: Basic Layered Stratification

### Scenario
Simulate transmission loss through a 4-layer ocean stratification representing typical coastal waters.

### Parameters
- **Frequency range**: 100-2000 Hz
- **Waveguide**: 200m × 10m
- **Layers**: Surface mixed layer, thermocline, deep water, bottom water

### Setup
```bash
# Create and run layered model
python run_simulation.py --layered --freq-start 100 --freq-end 2000 --freq-inc 25 --submit --wait --post-process
```

### Material Properties
| Layer | Depth (m) | Density (kg/m³) | Sound Speed (m/s) | Description |
|-------|-----------|-----------------|-------------------|-------------|
| 1     | 0-50      | 1000           | 1483             | Surface mixed layer |
| 2     | 50-100    | 1015           | 1489             | Thermocline |
| 3     | 100-150   | 1025           | 1497             | Deep water |
| 4     | 150-200   | 1030           | 1500             | Bottom water |

### Expected Results
- **Low frequencies (100-500 Hz)**: Minimal transmission loss (~1-5 dB)
- **Mid frequencies (500-1000 Hz)**: Moderate loss due to stratification (~5-15 dB)
- **High frequencies (1000-2000 Hz)**: Higher loss from scattering (~15-30 dB)

### Analysis
```python
# Load and analyze results
import pandas as pd
results = pd.read_csv('acoustic_results.csv')

# Find frequency of maximum transmission loss
max_tl_freq = results.loc[results['Transmission_Loss_dB'].idxmax(), 'Frequency_Hz']
print(f"Maximum TL at {max_tl_freq} Hz")

# Calculate average attenuation coefficient
avg_alpha = results['Attenuation_Coeff_per_m'].mean()
print(f"Average attenuation: {avg_alpha:.6f} m⁻¹")
```

## Example 2: Continuous Gradient Stratification

### Scenario
Model a smooth thermocline with continuous density and sound speed gradients.

### Parameters
- **Frequency range**: 200-5000 Hz
- **Gradient**: Linear increase in density and sound speed with depth
- **Profile**: ρ(z) = 1000 + 0.15z, c(z) = 1483 + 0.085z

### Setup
```bash
# Create gradient model with custom parameters
python run_simulation.py --gradient --freq-start 200 --freq-end 5000 --length 300 --submit
```

### Custom Material Profile
```python
# Create custom gradient profile
from material_properties import AcousticMaterialProperties

props = AcousticMaterialProperties()
profile = props.create_gradient_profile(
    depth_max=300,
    density_params=(1000.0, 0.15),    # Base density + gradient
    sound_speed_params=(1483.0, 0.085), # Base speed + gradient
    num_points=60
)

# Export to Abaqus format
props.export_to_abaqus_gradient(profile, 'custom_gradient.inp')
props.plot_profile(profile)
```

### Expected Results
- **Smooth TL variation**: No sharp peaks from layer reflections
- **Ray refraction effects**: Gradual increase in TL with frequency
- **Modal interference**: Complex frequency-dependent patterns

## Example 3: Frequency Sweep Comparison

### Scenario
Compare transmission loss between layered and gradient models across a wide frequency range.

### Setup
```bash
# Run both models with identical geometry
python run_simulation.py --both --freq-start 50 --freq-end 8000 --freq-inc 50 --submit --wait --post-process
```

### Post-Processing Comparison
```python
import matplotlib.pyplot as plt
import pandas as pd

# Load results from both models
layered_results = pd.read_csv('acoustic_layered_results.csv')
gradient_results = pd.read_csv('acoustic_gradient_results.csv')

# Plot comparison
plt.figure(figsize=(12, 8))
plt.subplot(2, 1, 1)
plt.plot(layered_results['Frequency_Hz'], layered_results['Transmission_Loss_dB'], 
         'b-', label='Layered', linewidth=2)
plt.plot(gradient_results['Frequency_Hz'], gradient_results['Transmission_Loss_dB'], 
         'r-', label='Gradient', linewidth=2)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Transmission Loss (dB)')
plt.title('TL Comparison: Layered vs Gradient')
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(2, 1, 2)
plt.plot(layered_results['Frequency_Hz'], layered_results['Attenuation_Coeff_per_m'], 
         'b-', label='Layered', linewidth=2)
plt.plot(gradient_results['Frequency_Hz'], gradient_results['Attenuation_Coeff_per_m'], 
         'r-', label='Gradient', linewidth=2)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Attenuation Coefficient (m⁻¹)')
plt.title('Attenuation Comparison: Layered vs Gradient')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('tl_comparison.png', dpi=300)
plt.show()
```

## Example 4: Mesh Convergence Study

### Scenario
Verify mesh independence by testing different element sizes.

### Setup
```bash
# Test three mesh densities
python run_simulation.py --layered --element-size 4.0 --freq-end 1000  # Coarse
python run_simulation.py --layered --element-size 2.0 --freq-end 1000  # Medium
python run_simulation.py --layered --element-size 1.0 --freq-end 1000  # Fine
```

### Convergence Analysis
```python
# Compare results at different mesh densities
mesh_sizes = [4.0, 2.0, 1.0]
tl_values = []  # Store TL at 500 Hz for each mesh

for size in mesh_sizes:
    results = pd.read_csv(f'acoustic_results_mesh_{size}.csv')
    tl_500 = results[results['Frequency_Hz'] == 500]['Transmission_Loss_dB'].iloc[0]
    tl_values.append(tl_500)

# Check convergence
for i in range(1, len(tl_values)):
    diff = abs(tl_values[i] - tl_values[i-1])
    print(f"Mesh {mesh_sizes[i-1]} to {mesh_sizes[i]}: TL difference = {diff:.3f} dB")

# Plot convergence
plt.figure(figsize=(8, 6))
plt.plot(mesh_sizes, tl_values, 'bo-', linewidth=2, markersize=8)
plt.xlabel('Element Size (m)')
plt.ylabel('Transmission Loss at 500 Hz (dB)')
plt.title('Mesh Convergence Study')
plt.grid(True, alpha=0.3)
plt.gca().invert_xaxis()  # Smaller elements on right
plt.savefig('mesh_convergence.png', dpi=300)
plt.show()
```

## Example 5: Realistic Ocean Profile

### Scenario
Use oceanographic data to create a realistic stratification profile.

### Setup
```python
from material_properties import AcousticMaterialProperties
import numpy as np

props = AcousticMaterialProperties()

# Create realistic ocean profile using Mackenzie equation
depths = np.linspace(0, 200, 21)
temperatures = []
salinities = []

for d in depths:
    if d < 20:
        # Surface mixed layer
        T = 18.0
        S = 34.5
    elif d < 80:
        # Thermocline
        T = 18.0 - 12.0 * (d - 20) / 60.0
        S = 34.5 + 0.5 * (d - 20) / 60.0
    else:
        # Deep water
        T = 6.0 - 2.0 * (d - 80) / 120.0
        S = 35.0

    temperatures.append(T)
    salinities.append(S)

# Calculate properties
densities = []
sound_speeds = []
bulk_moduli = []

for d, T, S in zip(depths, temperatures, salinities):
    rho = props.unesco_density(T, S, d)
    c = props.mackenzie_sound_speed(T, S, d)
    K = props.bulk_modulus_from_sound_density(c, rho)
    
    densities.append(rho)
    sound_speeds.append(c)
    bulk_moduli.append(K)

# Create profile
realistic_profile = {
    'name': 'Realistic Ocean Profile',
    'type': 'gradient',
    'depths': depths.tolist(),
    'temperatures': temperatures,
    'salinities': salinities,
    'densities': densities,
    'sound_speeds': sound_speeds,
    'bulk_moduli': bulk_moduli
}

# Export and visualize
props.save_profile(realistic_profile, 'realistic_ocean_profile.json')
props.export_to_abaqus_gradient(realistic_profile, 'realistic_materials.inp')
props.plot_profile(realistic_profile, plot_filename='realistic_ocean_profile.png')
```

### Expected Results
- **Sound channel effects**: Minimum sound speed creates acoustic waveguide
- **SOFAR channel**: Enhanced propagation at certain depths
- **Frequency dependence**: Different behavior for low vs high frequencies

## Example 6: Parameter Sensitivity Study

### Scenario
Study sensitivity to key parameters: density contrast, sound speed gradient, frequency range.

### Setup
```python
# Parameter ranges to test
density_contrasts = [0.05, 0.10, 0.15, 0.20]  # kg/m³/m
sound_gradients = [0.05, 0.085, 0.12, 0.15]   # m/s/m
frequency_ranges = [(100, 1000), (500, 2500), (1000, 5000)]

results_matrix = {}

for rho_grad in density_contrasts:
    for c_grad in sound_gradients:
        for freq_range in frequency_ranges:
            # Create custom profile
            profile = props.create_gradient_profile(
                depth_max=200,
                density_params=(1000.0, rho_grad),
                sound_speed_params=(1483.0, c_grad)
            )
            
            # Export to Abaqus
            profile_name = f'profile_rho{rho_grad}_c{c_grad}_f{freq_range[0]}-{freq_range[1]}'
            props.export_to_abaqus_gradient(profile, f'{profile_name}.inp')
            
            # Run simulation (would need to modify input file frequency range)
            # Store results for analysis
            results_matrix[(rho_grad, c_grad, freq_range)] = profile_name
```

### Analysis
```python
# Analyze parameter sensitivity
import seaborn as sns

# Create sensitivity heatmap for transmission loss
tl_matrix = np.zeros((len(density_contrasts), len(sound_gradients)))

for i, rho_grad in enumerate(density_contrasts):
    for j, c_grad in enumerate(sound_gradients):
        # Load results and calculate average TL
        # (This would require running all simulations)
        avg_tl = calculate_average_tl(rho_grad, c_grad)
        tl_matrix[i, j] = avg_tl

# Plot heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(tl_matrix, 
            xticklabels=sound_gradients,
            yticklabels=density_contrasts,
            annot=True, fmt='.1f',
            cmap='viridis')
plt.xlabel('Sound Speed Gradient (m/s/m)')
plt.ylabel('Density Gradient (kg/m³/m)')
plt.title('Average Transmission Loss Sensitivity')
plt.savefig('parameter_sensitivity.png', dpi=300)
plt.show()
```

## Example 7: 3D Extension

### Scenario
Extend the 2D waveguide to 3D for more realistic modeling.

### Modifications Required
```python
# In create_acoustic_model.py, modify for 3D:

class Acoustic3DModelBuilder(AcousticModelBuilder):
    def __init__(self, model_name='Acoustic3D'):
        super().__init__(model_name)
        self.height = 50.0  # Add third dimension
    
    def create_3d_geometry(self):
        """Create 3D geometry"""
        # Create 3D sketch and extrude
        sketch = self.model.ConstrainedSketch(name='Waveguide3D', sheetSize=300.0)
        sketch.rectangle(point1=(0.0, 0.0), point2=(self.width, self.length))
        
        # Create 3D part
        self.part = self.model.Part(name='Waveguide3D', 
                                   dimensionality=THREE_D, 
                                   type=DEFORMABLE_BODY)
        self.part.BaseSolidExtrude(sketch=sketch, depth=self.height)
    
    def create_3d_mesh(self):
        """Create 3D mesh with AC3D8 elements"""
        instance = self.assembly.instances[f'{self.part.name}-1']
        
        # Set 3D acoustic element type
        elemType1 = mesh.ElemType(elemCode=AC3D8, elemLibrary=STANDARD)
        elemType2 = mesh.ElemType(elemCode=AC3D6, elemLibrary=STANDARD)
        
        cells = instance.cells
        pickedRegions = (cells,)
        self.assembly.setElementType(regions=pickedRegions, 
                                   elemTypes=(elemType1, elemType2))
        
        # Seed and mesh
        self.assembly.seedPartInstance(regions=(instance,), size=self.element_size)
        self.assembly.generateMesh(regions=(instance,))
```

### 3D Input File Template
```
*HEADING
** 3D Acoustic Transmission Loss Simulation
**
*NODE
** (3D node coordinates)
**
*ELEMENT, TYPE=AC3D8
** (3D element connectivity)
**
*MATERIAL, NAME=WATER_3D
*DENSITY
1025.,
*BULK MODULUS
2.31e9,
**
*SOLID SECTION, ELSET=ALL_ELEMENTS, MATERIAL=WATER_3D
**
*STEP, NAME=SSD_3D
*STEADY STATE DYNAMICS, DIRECT
100., 2000., 25.
**
*INCIDENT WAVE INTERACTION PROPERTY, NAME=PLANEWAVE_3D
*INCIDENT WAVE FLUID PROPERTY
1025., 1500.
**
*INCIDENT WAVE INTERACTION, NAME=INC_3D, PROPERTY=PLANEWAVE_3D
SURF_INLET, 0., 1., 0.
**
*IMPEDANCE, TYPE=NONREFLECTING
SURF_OUTLET,
SURF_SIDES,
**
*OUTPUT, FIELD
*NODE OUTPUT
P,
*END STEP
```

## Example 8: Validation Against Analytical Solutions

### Scenario
Validate simulation results against known analytical solutions for simple cases.

### Test Case 1: Homogeneous Medium
```python
# Analytical solution for plane wave in homogeneous medium
def analytical_tl_homogeneous(frequency, distance, absorption_coeff):
    """
    Calculate analytical TL for homogeneous medium
    TL = absorption_coeff * distance * 8.686  (convert to dB)
    """
    return absorption_coeff * distance * 8.686

# Compare with simulation
frequencies = np.linspace(100, 1000, 37)
distance = 190.0  # Probe separation
alpha_water = 1e-4  # Typical absorption in water (Np/m)

analytical_tl = [analytical_tl_homogeneous(f, distance, alpha_water) for f in frequencies]

# Load simulation results for homogeneous case
sim_results = pd.read_csv('homogeneous_results.csv')

# Plot comparison
plt.figure(figsize=(10, 6))
plt.plot(frequencies, analytical_tl, 'r--', label='Analytical', linewidth=2)
plt.plot(sim_results['Frequency_Hz'], sim_results['Transmission_Loss_dB'], 
         'b-', label='Abaqus Simulation', linewidth=2)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Transmission Loss (dB)')
plt.title('Validation: Homogeneous Medium')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('validation_homogeneous.png', dpi=300)
plt.show()
```

### Test Case 2: Two-Layer Interface
```python
# Analytical reflection coefficient for normal incidence
def reflection_coefficient(rho1, c1, rho2, c2):
    """Calculate reflection coefficient at interface"""
    Z1 = rho1 * c1  # Impedance 1
    Z2 = rho2 * c2  # Impedance 2
    R = (Z2 - Z1) / (Z2 + Z1)
    return R

def transmission_coefficient(rho1, c1, rho2, c2):
    """Calculate transmission coefficient at interface"""
    Z1 = rho1 * c1
    Z2 = rho2 * c2
    T = 2 * Z2 / (Z2 + Z1)
    return T

# Calculate for water-sediment interface
rho_water = 1025.0  # kg/m³
c_water = 1500.0    # m/s
rho_sediment = 1800.0  # kg/m³
c_sediment = 1600.0    # m/s

R = reflection_coefficient(rho_water, c_water, rho_sediment, c_sediment)
T = transmission_coefficient(rho_water, c_water, rho_sediment, c_sediment)

print(f"Reflection coefficient: {R:.4f}")
print(f"Transmission coefficient: {T:.4f}")
print(f"Transmission loss: {-20*np.log10(abs(T)):.2f} dB")
```

## Example 9: Performance Optimization

### Scenario
Optimize simulation performance for large parameter studies.

### Parallel Processing
```bash
# Use multiple CPUs
abaqus job=acoustic_model cpus=8 mp_mode=threads memory=16gb

# Or use job arrays for parameter studies
for freq_end in 1000 2000 3000 4000 5000; do
    abaqus job=acoustic_freq_${freq_end} input=acoustic_base.inp \
           cpus=4 memory=8gb &
done
wait  # Wait for all jobs to complete
```

### Memory Management
```python
# Optimize frequency increments for memory usage
def optimize_frequency_sweep(freq_start, freq_end, max_frequencies=200):
    """
    Calculate optimal frequency increment to stay within memory limits
    """
    total_range = freq_end - freq_start
    optimal_increment = total_range / max_frequencies
    
    # Round to reasonable value
    if optimal_increment < 10:
        increment = 10
    elif optimal_increment < 25:
        increment = 25
    elif optimal_increment < 50:
        increment = 50
    else:
        increment = 100
    
    actual_frequencies = int(total_range / increment) + 1
    print(f"Frequency range: {freq_start}-{freq_end} Hz")
    print(f"Increment: {increment} Hz")
    print(f"Total frequencies: {actual_frequencies}")
    
    return increment

# Use optimized increment
increment = optimize_frequency_sweep(100, 5000, max_frequencies=150)
```

### Batch Processing
```python
# Process multiple configurations in batch
configurations = [
    {'name': 'shallow_water', 'depth': 100, 'layers': 3},
    {'name': 'deep_water', 'depth': 500, 'layers': 5},
    {'name': 'continental_shelf', 'depth': 200, 'layers': 4}
]

for config in configurations:
    print(f"Processing {config['name']}...")
    
    # Create custom profile
    profile = create_custom_profile(config)
    
    # Run simulation
    job_name = f"acoustic_{config['name']}"
    run_abaqus_job(job_name, profile)
    
    # Post-process
    post_process_job(job_name)
    
    print(f"Completed {config['name']}")
```

## Example 10: Advanced Post-Processing

### Scenario
Advanced analysis of simulation results including modal analysis and ray tracing visualization.

### Modal Analysis
```python
def analyze_modal_structure(results_df, waveguide_height=10.0):
    """
    Analyze modal structure from transmission loss data
    """
    frequencies = results_df['Frequency_Hz'].values
    tl_values = results_df['Transmission_Loss_dB'].values
    
    # Find local minima (potential modal frequencies)
    from scipy.signal import find_peaks
    
    # Invert TL to find minima as peaks
    inverted_tl = -tl_values
    peaks, properties = find_peaks(inverted_tl, height=0, distance=10)
    
    modal_frequencies = frequencies[peaks]
    modal_tl = tl_values[peaks]
    
    print("Potential Modal Frequencies:")
    for i, (freq, tl) in enumerate(zip(modal_frequencies, modal_tl)):
        print(f"Mode {i+1}: {freq:.1f} Hz, TL = {tl:.2f} dB")
    
    # Plot modal analysis
    plt.figure(figsize=(12, 8))
    plt.subplot(2, 1, 1)
    plt.plot(frequencies, tl_values, 'b-', linewidth=1)
    plt.plot(modal_frequencies, modal_tl, 'ro', markersize=8, label='Modal frequencies')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Transmission Loss (dB)')
    plt.title('Modal Analysis')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Theoretical modal frequencies for rectangular waveguide
    c_avg = 1490.0  # Average sound speed
    theoretical_modes = []
    for n in range(1, 10):
        f_mode = n * c_avg / (2 * waveguide_height)
        if f_mode < frequencies[-1]:
            theoretical_modes.append(f_mode)
    
    plt.subplot(2, 1, 2)
    plt.stem(modal_frequencies, np.ones(len(modal_frequencies)), 
             'b-', basefmt='b-', label='Observed modes')
    plt.stem(theoretical_modes, 0.5*np.ones(len(theoretical_modes)), 
             'r-', basefmt='r-', label='Theoretical modes')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Mode Indicator')
    plt.title('Mode Comparison')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('modal_analysis.png', dpi=300)
    plt.show()
    
    return modal_frequencies, modal_tl

# Run modal analysis
modal_freqs, modal_tls = analyze_modal_structure(results)
```

### Ray Tracing Visualization
```python
def visualize_ray_paths(profile, source_depth=25, receiver_depth=175, 
                       frequencies=[500, 1000, 2000]):
    """
    Visualize ray paths through stratified medium
    """
    depths = np.array(profile['depths'])
    sound_speeds = np.array(profile['sound_speeds'])
    
    fig, axes = plt.subplots(len(frequencies), 1, figsize=(12, 4*len(frequencies)))
    if len(frequencies) == 1:
        axes = [axes]
    
    for i, freq in enumerate(frequencies):
        ax = axes[i]
        
        # Plot sound speed profile
        ax2 = ax.twinx()
        ax2.plot(sound_speeds, depths, 'g--', alpha=0.7, label='Sound speed')
        ax2.set_ylabel('Sound Speed (m/s)', color='g')
        ax2.tick_params(axis='y', labelcolor='g')
        
        # Simple ray tracing (Snell's law)
        # This is a simplified example - full ray tracing would be more complex
        ray_angles = np.linspace(-30, 30, 11)  # degrees
        
        for angle in ray_angles:
            # Calculate ray path using Snell's law
            ray_x = []
            ray_z = []
            
            # Start at source
            x, z = 0, source_depth
            ray_x.append(x)
            ray_z.append(z)
            
            # Simple straight-line approximation
            # (Real ray tracing would account for refraction)
            dx = 200.0  # Total distance
            dz = receiver_depth - source_depth
            
            ray_x.append(dx)
            ray_z.append(receiver_depth)
            
            ax.plot(ray_x, ray_z, 'b-', alpha=0.3, linewidth=0.5)
        
        # Mark source and receiver
        ax.plot(0, source_depth, 'ro', markersize=8, label='Source')
        ax.plot(200, receiver_depth, 'rs', markersize=8, label='Receiver')
        
        ax.set_xlabel('Range (m)')
        ax.set_ylabel('Depth (m)')
        ax.set_title(f'Ray Paths at {freq} Hz')
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    plt.tight_layout()
    plt.savefig('ray_tracing.png', dpi=300)
    plt.show()

# Visualize ray paths
visualize_ray_paths(gradient_profile)
```

These examples demonstrate the full capabilities of the acoustic transmission loss simulation suite, from basic setups to advanced analysis techniques. Each example can be adapted for specific research needs and oceanographic conditions.