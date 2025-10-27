"""
ML-Driven Inverse Design of Welding Parameters Dataset Generator

This script generates a comprehensive dataset for machine learning-based
inverse design of welding parameters, specifically for battery tab welding
applications (Cu-Al and similar joints).

The dataset includes:
1. Input Parameters (controllable design space)
2. Characterization & Quality Metrics (immediate measurements)
3. Performance & Validation Metrics (thermal cycling behavior)
"""

import numpy as np
import pandas as pd
from scipy import stats
import itertools

# Set random seed for reproducibility
np.random.seed(42)

# ============================================================================
# PART 1: INPUT PARAMETERS (DESIGN SPACE)
# ============================================================================

# Material combinations
anode_materials = ['Cu', 'Cu-Alloy', 'Ni-plated-Cu']
cathode_materials = ['Al', 'Al-Alloy-1050', 'Al-Alloy-3003', 'Al-Alloy-6061']
surface_finishes = ['As-Received', 'Cleaned', 'Ni-Plated', 'Zn-Coated', 'Oxide-Removed']

# Welding techniques
welding_techniques = ['Ultrasonic', 'Laser', 'Resistance-Spot']

# Parameter ranges for each technique
param_ranges = {
    'Ultrasonic': {
        'power_W': (500, 3500),
        'amplitude_um': (10, 50),
        'force_N': (200, 2000),
        'time_ms': (100, 1500),
        'frequency_Hz': (20000, 20000),  # Standard ultrasonic frequency
        'speed_mm_s': (0, 0),  # Not applicable
    },
    'Laser': {
        'power_W': (500, 6000),
        'amplitude_um': (0, 0),  # Not applicable
        'force_N': (0, 100),  # Minimal clamping
        'time_ms': (1, 50),  # Pulse duration
        'frequency_Hz': (10, 100),  # Pulse frequency
        'speed_mm_s': (10, 200),  # Welding speed
    },
    'Resistance-Spot': {
        'power_W': (1000, 8000),
        'amplitude_um': (0, 0),  # Not applicable
        'force_N': (500, 3000),
        'time_ms': (50, 500),
        'frequency_Hz': (0, 0),  # Not applicable
        'speed_mm_s': (0, 0),  # Not applicable
    }
}

# Geometric parameters
tab_thickness_um = [50, 100, 150, 200, 250, 300, 400, 500]
pre_heat_temp_C = [25, 40, 60, 80, 100]

# ============================================================================
# DATASET GENERATION
# ============================================================================

def generate_samples(n_samples=5000):
    """Generate random samples across the design space"""
    
    samples = []
    
    for _ in range(n_samples):
        # Random material combination
        anode = np.random.choice(anode_materials)
        cathode = np.random.choice(cathode_materials)
        surface = np.random.choice(surface_finishes)
        
        # Random technique
        technique = np.random.choice(welding_techniques)
        
        # Random parameters based on technique
        params = param_ranges[technique]
        power = np.random.uniform(*params['power_W'])
        amplitude = np.random.uniform(*params['amplitude_um']) if params['amplitude_um'][1] > 0 else 0
        force = np.random.uniform(*params['force_N']) if params['force_N'][1] > 0 else 0
        time_ms = np.random.uniform(*params['time_ms'])
        frequency = np.random.uniform(*params['frequency_Hz']) if params['frequency_Hz'][1] > 0 else 0
        speed = np.random.uniform(*params['speed_mm_s']) if params['speed_mm_s'][1] > 0 else 0
        
        # Geometric and environmental
        thickness = np.random.choice(tab_thickness_um)
        preheat = np.random.choice(pre_heat_temp_C)
        
        # Energy density calculation (technique-dependent)
        if technique == 'Ultrasonic':
            energy_density = power * time_ms / (thickness * 10)  # J/mm²
        elif technique == 'Laser':
            spot_size_mm2 = np.random.uniform(0.5, 3.0)
            energy_density = power * time_ms / (spot_size_mm2 * 1000)
        else:  # Resistance-Spot
            spot_size_mm2 = np.random.uniform(3, 10)
            energy_density = power * time_ms / (spot_size_mm2 * 1000)
        
        sample = {
            # Input parameters
            'anode_material': anode,
            'cathode_material': cathode,
            'surface_finish': surface,
            'welding_technique': technique,
            'power_W': power,
            'amplitude_um': amplitude,
            'force_N': force,
            'time_ms': time_ms,
            'frequency_Hz': frequency,
            'speed_mm_s': speed,
            'tab_thickness_um': thickness,
            'preheat_temp_C': preheat,
            'energy_density_J_mm2': energy_density,
        }
        
        samples.append(sample)
    
    return pd.DataFrame(samples)


def calculate_quality_metrics(df):
    """
    Calculate immediate characterization and quality metrics
    These are physics-informed relationships with realistic noise
    """
    
    n = len(df)
    
    # Material property indices (normalized)
    material_conductivity = df['anode_material'].map({
        'Cu': 1.0, 'Cu-Alloy': 0.85, 'Ni-plated-Cu': 0.75
    }) * df['cathode_material'].map({
        'Al': 0.6, 'Al-Alloy-1050': 0.58, 'Al-Alloy-3003': 0.54, 'Al-Alloy-6061': 0.50
    })
    
    surface_quality = df['surface_finish'].map({
        'As-Received': 0.6, 'Cleaned': 0.8, 'Ni-Plated': 1.0, 
        'Zn-Coated': 0.9, 'Oxide-Removed': 0.85
    })
    
    # Normalize key input parameters
    energy_norm = (df['energy_density_J_mm2'] - df['energy_density_J_mm2'].min()) / \
                  (df['energy_density_J_mm2'].max() - df['energy_density_J_mm2'].min())
    
    force_norm = df['force_N'] / 3000.0
    thickness_norm = df['tab_thickness_um'] / 500.0
    preheat_norm = df['preheat_temp_C'] / 100.0
    
    # ========================================================================
    # IMMEDIATE QUALITY METRICS
    # ========================================================================
    
    # 1. Electrical Contact Resistance (µΩ) - Lower is better
    # Depends on: energy, force, surface quality, materials
    base_resistance = 50 + 150 * (1 - surface_quality) * (1 - material_conductivity)
    energy_effect = -30 * energy_norm + 20 * energy_norm**2  # Optimal zone exists
    force_effect = -20 * force_norm
    thickness_effect = 15 * thickness_norm
    
    df['contact_resistance_uOhm'] = np.maximum(
        base_resistance + energy_effect + force_effect + thickness_effect + 
        np.random.normal(0, 8, n), 
        10
    )
    
    # 2. Peak Weld Temperature (°C) - Must be controlled
    # Too high causes damage, too low causes poor bonding
    base_temp = 200 + df['preheat_temp_C']
    energy_temp = 400 * energy_norm**1.5
    thickness_reduction = -50 * thickness_norm  # Thicker tabs dissipate heat
    
    df['peak_temperature_C'] = (
        base_temp + energy_temp + thickness_reduction + 
        np.random.normal(0, 15, n)
    )
    
    # 3. Weld Nugget Area (mm²) - Bonded area
    base_area = 2.0
    energy_area = 12 * energy_norm - 3 * energy_norm**2  # Saturates at high energy
    force_area = 3 * force_norm
    
    df['weld_nugget_area_mm2'] = np.maximum(
        base_area + energy_area + force_area + 
        np.random.normal(0, 0.8, n),
        0.5
    )
    
    # 4. Intermetallic Compound (IMC) Layer Thickness (µm)
    # Critical for Cu-Al joints - too thick is brittle
    base_imc = 0.5
    temp_effect = 0.03 * (df['peak_temperature_C'] - 200)  # Grows with temperature
    time_effect = 0.02 * (df['time_ms'] / 100)
    
    df['IMC_thickness_um'] = np.maximum(
        base_imc + temp_effect + time_effect + 
        np.random.normal(0, 0.3, n),
        0.1
    )
    
    # 5. Initial Tensile Shear Strength (N) - Mechanical strength
    area_strength = df['weld_nugget_area_mm2'] * 150  # Base strength per unit area
    imc_penalty = -50 * np.maximum(df['IMC_thickness_um'] - 3, 0)  # Brittle IMC penalty
    surface_bonus = 100 * surface_quality
    
    df['tensile_shear_strength_N'] = np.maximum(
        area_strength + imc_penalty + surface_bonus + 
        np.random.normal(0, 50, n),
        100
    )
    
    # 6. Penetration Depth (% of thickness)
    penetration_base = 40  # percentage
    energy_penetration = 30 * energy_norm
    force_penetration = 10 * force_norm
    
    df['penetration_depth_pct'] = np.clip(
        penetration_base + energy_penetration + force_penetration + 
        np.random.normal(0, 5, n),
        10, 95
    )
    
    # 7. Surface Deformation/Indentation (µm)
    force_indent = 50 * force_norm
    energy_indent = 30 * energy_norm
    
    df['surface_indentation_um'] = np.maximum(
        force_indent + energy_indent + 
        np.random.normal(0, 8, n),
        0
    )
    
    # 8. Weld Nugget Hardness (HV - Vickers)
    base_hardness = 80
    energy_hardness = 60 * energy_norm
    imc_hardness = 40 * (df['IMC_thickness_um'] / 5)  # IMC is harder but brittle
    
    df['hardness_HV'] = (
        base_hardness + energy_hardness + imc_hardness + 
        np.random.normal(0, 8, n)
    )
    
    # 9. Porosity (% volume) - Defects
    base_porosity = 1.0
    poor_params = (energy_norm < 0.3) | (energy_norm > 0.9)
    high_speed = (df['speed_mm_s'] > 150)
    
    df['porosity_pct'] = np.clip(
        base_porosity + 
        3 * poor_params.astype(float) + 
        2 * high_speed.astype(float) + 
        np.random.exponential(1.5, n),
        0, 15
    )
    
    # 10. Microstructural uniformity score (0-100)
    uniformity_base = 50
    good_energy = 30 * np.exp(-5 * (energy_norm - 0.6)**2)
    good_force = 20 * force_norm * (1 - force_norm)  # Optimal at mid-range
    
    df['microstructure_uniformity_score'] = np.clip(
        uniformity_base + good_energy + good_force + 
        np.random.normal(0, 8, n),
        0, 100
    )
    
    # ========================================================================
    # PERFORMANCE METRICS (INVERSE DESIGN TARGETS)
    # ========================================================================
    
    # 11. Thermal Cycling Fatigue Life (cycles to failure)
    # This is the PRIMARY TARGET for inverse design
    base_cycles = 500
    
    # Factors that improve cycling life:
    good_imc = 2000 * np.exp(-0.5 * (df['IMC_thickness_um'] - 2.0)**2)  # Optimal ~2µm
    good_bonding = 15 * df['weld_nugget_area_mm2']
    good_strength = 3 * (df['tensile_shear_strength_N'] / 1000)
    low_porosity = 500 * (1 - df['porosity_pct'] / 15)
    good_microstructure = 10 * (df['microstructure_uniformity_score'] / 100)
    
    # Penalties:
    high_resistance_penalty = -300 * (df['contact_resistance_uOhm'] / 200)
    high_stress_penalty = -200 * (df['surface_indentation_um'] / 100)
    
    df['thermal_cycles_to_failure'] = np.maximum(
        base_cycles + good_imc + good_bonding + good_strength + 
        low_porosity + good_microstructure + 
        high_resistance_penalty + high_stress_penalty + 
        np.random.normal(0, 150, n),
        50
    ).astype(int)
    
    # 12. Resistance Increase After Cycling (%)
    # Measure degradation
    base_increase = 10
    poor_imc = 30 * np.maximum(df['IMC_thickness_um'] - 3, 0)
    initial_resistance_effect = 5 * (df['contact_resistance_uOhm'] / 100)
    porosity_effect = 8 * df['porosity_pct']
    
    df['resistance_increase_after_cycling_pct'] = np.clip(
        base_increase + poor_imc + initial_resistance_effect + 
        porosity_effect + np.random.normal(0, 5, n),
        0, 200
    )
    
    # 13. Strength Retention After Cycling (%)
    base_retention = 70
    good_quality = 20 * (df['microstructure_uniformity_score'] / 100)
    good_imc_retention = 15 * np.exp(-0.3 * (df['IMC_thickness_um'] - 2.5)**2)
    low_porosity_retention = 10 * (1 - df['porosity_pct'] / 15)
    
    df['strength_retention_pct'] = np.clip(
        base_retention + good_quality + good_imc_retention + 
        low_porosity_retention + np.random.normal(0, 5, n),
        20, 100
    )
    
    # 14. Crack Initiation Cycle
    # When do cracks start appearing?
    df['crack_initiation_cycle'] = (
        0.3 * df['thermal_cycles_to_failure'] + 
        np.random.normal(0, 50, n)
    ).clip(lower=10).astype(int)
    
    # 15. Maximum Operating Temperature (°C)
    # Safe operating temperature after cycling
    base_max_temp = 80
    quality_bonus = 20 * (df['microstructure_uniformity_score'] / 100)
    resistance_penalty = -15 * (df['contact_resistance_uOhm'] / 100)
    
    df['max_operating_temp_C'] = np.clip(
        base_max_temp + quality_bonus + resistance_penalty + 
        np.random.normal(0, 5, n),
        40, 120
    )
    
    # 16. Bond Separation Force After Cycling (N)
    # Residual strength
    df['bond_separation_force_N'] = (
        df['tensile_shear_strength_N'] * 
        (df['strength_retention_pct'] / 100) + 
        np.random.normal(0, 30, n)
    ).clip(lower=50)
    
    # 17. Electrochemical Stability Score (0-100)
    # Resistance to corrosion and oxidation
    material_stability = material_conductivity * 50
    surface_stability = surface_quality * 30
    low_defect_stability = 20 * (1 - df['porosity_pct'] / 15)
    
    df['electrochemical_stability_score'] = np.clip(
        material_stability + surface_stability + low_defect_stability + 
        np.random.normal(0, 5, n),
        0, 100
    )
    
    # 18. Energy Efficiency Score (0-100)
    # How efficiently was the weld created?
    efficient_energy = 50 * np.exp(-3 * (energy_norm - 0.5)**2)
    efficient_time = 30 * np.exp(-0.003 * df['time_ms'])
    good_result = 20 * (df['tensile_shear_strength_N'] / 1500)
    
    df['energy_efficiency_score'] = np.clip(
        efficient_energy + efficient_time + good_result + 
        np.random.normal(0, 5, n),
        0, 100
    )
    
    # 19. Process Stability Index (0-100)
    # How repeatable is this process?
    mid_range_params = (
        (energy_norm > 0.3) & (energy_norm < 0.8) &
        (force_norm > 0.2) & (force_norm < 0.7)
    )
    df['process_stability_index'] = np.clip(
        60 * mid_range_params.astype(float) + 
        20 * (df['microstructure_uniformity_score'] / 100) + 
        np.random.normal(0, 8, n),
        0, 100
    )
    
    # 20. Overall Quality Score (composite metric, 0-100)
    # Weighted combination of key metrics
    normalized_cycles = np.clip(df['thermal_cycles_to_failure'] / 3000, 0, 1)
    normalized_strength = np.clip(df['tensile_shear_strength_N'] / 1500, 0, 1)
    normalized_resistance = np.clip(1 - df['contact_resistance_uOhm'] / 200, 0, 1)
    
    df['overall_quality_score'] = (
        30 * normalized_cycles + 
        25 * normalized_strength + 
        20 * normalized_resistance + 
        15 * (df['microstructure_uniformity_score'] / 100) +
        10 * (df['electrochemical_stability_score'] / 100)
    ) + np.random.normal(0, 3, n)
    
    df['overall_quality_score'] = df['overall_quality_score'].clip(0, 100)
    
    # 21. Binary classification: Good vs Bad weld
    # Good if: high cycles, low resistance increase, good retention
    df['weld_quality_class'] = (
        (df['thermal_cycles_to_failure'] > 1500) & 
        (df['resistance_increase_after_cycling_pct'] < 30) &
        (df['strength_retention_pct'] > 60)
    ).astype(int).map({1: 'Good', 0: 'Poor'})
    
    return df


# ============================================================================
# MAIN EXECUTION
# ============================================================================

print("="*80)
print("ML-DRIVEN INVERSE DESIGN OF WELDING PARAMETERS")
print("Dataset Generator")
print("="*80)
print()

print("Generating input parameter combinations...")
df = generate_samples(n_samples=5000)
print(f"✓ Generated {len(df)} samples across design space")
print()

print("Calculating quality metrics (physics-informed model)...")
df = calculate_quality_metrics(df)
print(f"✓ Calculated {len(df.columns)} total features and targets")
print()

# Save dataset
output_file = '/workspace/welding_ml_dataset.csv'
df.to_csv(output_file, index=False)
print(f"✓ Dataset saved to: {output_file}")
print()

# Generate summary statistics
print("="*80)
print("DATASET SUMMARY")
print("="*80)
print()
print(f"Total Samples: {len(df)}")
print(f"Total Features: {len(df.columns)}")
print()

print("Input Parameters (13):")
input_cols = ['anode_material', 'cathode_material', 'surface_finish', 
              'welding_technique', 'power_W', 'amplitude_um', 'force_N', 
              'time_ms', 'frequency_Hz', 'speed_mm_s', 'tab_thickness_um', 
              'preheat_temp_C', 'energy_density_J_mm2']
for col in input_cols:
    print(f"  - {col}")
print()

print("Immediate Quality Metrics (10):")
quality_cols = ['contact_resistance_uOhm', 'peak_temperature_C', 
                'weld_nugget_area_mm2', 'IMC_thickness_um', 
                'tensile_shear_strength_N', 'penetration_depth_pct',
                'surface_indentation_um', 'hardness_HV', 'porosity_pct',
                'microstructure_uniformity_score']
for col in quality_cols:
    print(f"  - {col}")
print()

print("Performance Metrics (11) - INVERSE DESIGN TARGETS:")
performance_cols = ['thermal_cycles_to_failure', 
                   'resistance_increase_after_cycling_pct',
                   'strength_retention_pct', 'crack_initiation_cycle',
                   'max_operating_temp_C', 'bond_separation_force_N',
                   'electrochemical_stability_score', 'energy_efficiency_score',
                   'process_stability_index', 'overall_quality_score',
                   'weld_quality_class']
for col in performance_cols:
    print(f"  - {col}")
print()

# Key statistics
print("="*80)
print("KEY STATISTICS")
print("="*80)
print()

print("Welding Techniques Distribution:")
print(df['welding_technique'].value_counts())
print()

print("Material Combinations:")
print(df.groupby(['anode_material', 'cathode_material']).size().head(10))
print()

print("Target Variable: Thermal Cycles to Failure")
print(f"  Mean: {df['thermal_cycles_to_failure'].mean():.0f} cycles")
print(f"  Std:  {df['thermal_cycles_to_failure'].std():.0f} cycles")
print(f"  Min:  {df['thermal_cycles_to_failure'].min():.0f} cycles")
print(f"  Max:  {df['thermal_cycles_to_failure'].max():.0f} cycles")
print()

print("Weld Quality Classification:")
print(df['weld_quality_class'].value_counts())
print(f"  Good Welds: {(df['weld_quality_class']=='Good').sum()} ({(df['weld_quality_class']=='Good').mean()*100:.1f}%)")
print()

print("Contact Resistance (µΩ):")
print(f"  Mean: {df['contact_resistance_uOhm'].mean():.1f}")
print(f"  Std:  {df['contact_resistance_uOhm'].std():.1f}")
print()

print("="*80)
print("Dataset generation complete!")
print("="*80)
