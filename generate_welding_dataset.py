import numpy as np
import pandas as pd
from datetime import datetime
import json

np.random.seed(42)

def generate_comprehensive_welding_dataset(n_samples=5000):
    """
    Generate a comprehensive dataset for ML-driven inverse design of welding parameters.
    Includes realistic physical correlations and multi-objective optimization targets.
    """
    
    print(f"Generating {n_samples} welding samples with realistic physical correlations...")
    
    # ===== PART 1: INPUT PARAMETERS (DESIGN SPACE) =====
    
    # Base Materials
    anode_materials = ['Cu-101', 'Cu-110', 'Cu-C10100', 'Cu-ETP']
    cathode_materials = ['Al-1060', 'Al-1100', 'Al-3003', 'Al-6061']
    
    data = {
        # Material Properties
        'anode_material': np.random.choice(anode_materials, n_samples),
        'cathode_material': np.random.choice(cathode_materials, n_samples),
        'anode_thickness_um': np.random.uniform(100, 500, n_samples),
        'cathode_thickness_um': np.random.uniform(100, 500, n_samples),
        'surface_finish': np.random.choice(['bare', 'nickel_plated', 'tin_plated', 'anodized'], n_samples),
        'surface_roughness_ra_um': np.random.uniform(0.1, 5.0, n_samples),
        
        # Welding Technique
        'welding_technique': np.random.choice(['USW', 'Laser', 'RSW', 'CMW'], n_samples),
    }
    
    # Technique-specific parameters with realistic ranges
    data['power_w'] = np.zeros(n_samples)
    data['amplitude_um'] = np.zeros(n_samples)
    data['force_n'] = np.zeros(n_samples)
    data['time_ms'] = np.zeros(n_samples)
    data['speed_mm_s'] = np.zeros(n_samples)
    data['pulse_frequency_hz'] = np.zeros(n_samples)
    data['pulse_energy_j'] = np.zeros(n_samples)
    data['current_ka'] = np.zeros(n_samples)
    
    for i in range(n_samples):
        technique = data['welding_technique'][i]
        
        if technique == 'USW':  # Ultrasonic Welding
            data['power_w'][i] = np.random.uniform(1000, 4000)
            data['amplitude_um'][i] = np.random.uniform(20, 60)
            data['force_n'][i] = np.random.uniform(1000, 3500)
            data['time_ms'][i] = np.random.uniform(100, 800)
            data['pulse_frequency_hz'][i] = 20000  # Fixed for USW
            
        elif technique == 'Laser':  # Laser Welding
            data['power_w'][i] = np.random.uniform(500, 3000)
            data['pulse_energy_j'][i] = np.random.uniform(1, 50)
            data['speed_mm_s'][i] = np.random.uniform(10, 100)
            data['pulse_frequency_hz'][i] = np.random.uniform(50, 1000)
            data['time_ms'][i] = np.random.uniform(5, 100)
            
        elif technique == 'RSW':  # Resistance Spot Welding
            data['current_ka'][i] = np.random.uniform(5, 25)
            data['force_n'][i] = np.random.uniform(2000, 5000)
            data['time_ms'][i] = np.random.uniform(100, 500)
            data['power_w'][i] = data['current_ka'][i] ** 2 * 0.0001 * 1000  # P=I²R approximation
            
        elif technique == 'CMW':  # Cold Metal Welding
            data['force_n'][i] = np.random.uniform(5000, 15000)
            data['speed_mm_s'][i] = np.random.uniform(1, 20)
            data['time_ms'][i] = np.random.uniform(200, 1000)
    
    # Environmental conditions
    data['preheat_temp_c'] = np.random.uniform(20, 80, n_samples)
    data['ambient_humidity_percent'] = np.random.uniform(30, 70, n_samples)
    data['ambient_temp_c'] = np.random.uniform(18, 28, n_samples)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # ===== PART 2: CHARACTERIZATION & QUALITY METRICS (FORWARD PROBLEM) =====
    
    print("Generating characterization and quality metrics...")
    
    # Calculate energy density (key parameter)
    df['energy_density_j_mm2'] = np.zeros(n_samples)
    for i in range(n_samples):
        if df['welding_technique'][i] == 'USW':
            # Energy = Power × Time
            energy = df['power_w'][i] * df['time_ms'][i] / 1000
            # Approximate weld area
            area = (df['amplitude_um'][i] / 50) ** 2 * 25  # mm²
            df.loc[i, 'energy_density_j_mm2'] = energy / max(area, 1)
        elif df['welding_technique'][i] == 'Laser':
            df.loc[i, 'energy_density_j_mm2'] = df['pulse_energy_j'][i] / (df['speed_mm_s'][i] * 0.5)
        elif df['welding_technique'][i] == 'RSW':
            energy = df['power_w'][i] * df['time_ms'][i] / 1000
            area = 10  # typical spot size
            df.loc[i, 'energy_density_j_mm2'] = energy / area
        else:  # CMW
            df.loc[i, 'energy_density_j_mm2'] = df['force_n'][i] / 100
    
    # Weld geometry
    df['weld_width_mm'] = 2 + 3 * (df['energy_density_j_mm2'] / df['energy_density_j_mm2'].max()) + np.random.normal(0, 0.3, n_samples)
    df['weld_width_mm'] = np.clip(df['weld_width_mm'], 1, 8)
    
    df['weld_length_mm'] = 3 + 5 * (df['energy_density_j_mm2'] / df['energy_density_j_mm2'].max()) + np.random.normal(0, 0.5, n_samples)
    df['weld_length_mm'] = np.clip(df['weld_length_mm'], 2, 12)
    
    df['penetration_depth_um'] = 50 + 200 * (df['energy_density_j_mm2'] / df['energy_density_j_mm2'].max()) + np.random.normal(0, 20, n_samples)
    df['penetration_depth_um'] = np.clip(df['penetration_depth_um'], 30, 300)
    
    # Intermetallic layer thickness (CuAl2 formation - critical for performance)
    # Higher energy → thicker IMC layer (can be detrimental if too thick)
    base_imc = 0.5 + 4 * (df['energy_density_j_mm2'] / df['energy_density_j_mm2'].max())
    df['imc_thickness_um'] = base_imc + np.random.normal(0, 0.5, n_samples)
    df['imc_thickness_um'] = np.clip(df['imc_thickness_um'], 0.2, 10)
    
    # Electrical resistance (lower is better)
    # Influenced by IMC thickness (U-shaped: too thin = poor bonding, too thick = brittle)
    optimal_imc = 2.0
    imc_deviation = np.abs(df['imc_thickness_um'] - optimal_imc)
    df['contact_resistance_microohm'] = 50 + 150 * (imc_deviation / 5) + np.random.normal(0, 10, n_samples)
    df['contact_resistance_microohm'] = np.clip(df['contact_resistance_microohm'], 20, 500)
    
    # Mechanical strength
    # Peak shear strength achieved at moderate energy density
    normalized_energy = df['energy_density_j_mm2'] / df['energy_density_j_mm2'].max()
    df['shear_strength_mpa'] = 30 + 100 * normalized_energy * (1 - 0.5 * normalized_energy) + np.random.normal(0, 8, n_samples)
    df['shear_strength_mpa'] = np.clip(df['shear_strength_mpa'], 15, 120)
    
    df['peel_strength_n_mm'] = 5 + 25 * normalized_energy * (1 - 0.4 * normalized_energy) + np.random.normal(0, 2, n_samples)
    df['peel_strength_n_mm'] = np.clip(df['peel_strength_n_mm'], 3, 35)
    
    # Defects
    df['porosity_percent'] = np.clip(np.random.exponential(2, n_samples) * (normalized_energy > 0.7).astype(float) * 2, 0, 15)
    df['crack_density_per_mm2'] = np.clip(np.random.poisson(1, n_samples) * (normalized_energy > 0.8).astype(float), 0, 20)
    df['void_fraction_percent'] = np.clip(np.random.exponential(1.5, n_samples) * (normalized_energy < 0.3).astype(float) * 3, 0, 12)
    
    # Surface quality
    df['surface_roughness_post_weld_um'] = df['surface_roughness_ra_um'] * (1 + 0.5 * normalized_energy) + np.random.normal(0, 0.5, n_samples)
    df['surface_roughness_post_weld_um'] = np.clip(df['surface_roughness_post_weld_um'], 0.1, 15)
    
    # Thermal measurements during welding
    df['peak_temperature_c'] = 150 + 600 * normalized_energy + np.random.normal(0, 30, n_samples)
    df['peak_temperature_c'] = np.clip(df['peak_temperature_c'], 100, 900)
    
    df['cooling_rate_c_per_s'] = 10 + 100 * normalized_energy + np.random.normal(0, 10, n_samples)
    df['cooling_rate_c_per_s'] = np.clip(df['cooling_rate_c_per_s'], 5, 200)
    
    # Microstructure (grain size)
    df['grain_size_um'] = 50 - 30 * normalized_energy + np.random.normal(0, 5, n_samples)
    df['grain_size_um'] = np.clip(df['grain_size_um'], 5, 60)
    
    # ===== PART 3: PERFORMANCE & VALIDATION METRICS (INVERSE DESIGN TARGETS) =====
    
    print("Generating performance metrics under thermal cycling...")
    
    # Thermal cycling simulation (-40°C to +85°C)
    n_cycles = np.random.randint(100, 2000, n_samples)
    df['thermal_cycles_tested'] = n_cycles
    
    # Resistance evolution (key failure mode)
    # Good welds: stable resistance. Bad welds: rapid increase
    quality_factor = 1 - (imc_deviation / 5) - (df['porosity_percent'] / 20) - (df['crack_density_per_mm2'] / 30)
    quality_factor = np.clip(quality_factor, 0.1, 1.0)
    
    # Resistance increase after cycling (%)
    base_increase = 5 + 80 * (1 - quality_factor)
    cycle_effect = (n_cycles / 1000) * (1 - quality_factor) * 20
    df['resistance_increase_percent'] = base_increase + cycle_effect + np.random.normal(0, 5, n_samples)
    df['resistance_increase_percent'] = np.clip(df['resistance_increase_percent'], 0, 200)
    
    # Mechanical strength retention (%)
    df['strength_retention_percent'] = 100 * quality_factor * (1 - 0.3 * (n_cycles / 2000)) + np.random.normal(0, 5, n_samples)
    df['strength_retention_percent'] = np.clip(df['strength_retention_percent'], 20, 100)
    
    # Fatigue life (cycles to failure)
    df['fatigue_life_cycles'] = 1000 * quality_factor ** 2 * (1 + np.random.uniform(-0.3, 0.3, n_samples))
    df['fatigue_life_cycles'] = np.clip(df['fatigue_life_cycles'], 100, 3000).astype(int)
    
    # Delamination progression
    df['delamination_area_percent'] = np.clip((1 - quality_factor) * 30 * (n_cycles / 1000) + np.random.normal(0, 3, n_samples), 0, 80)
    
    # IMC layer evolution (growth during cycling)
    df['imc_growth_rate_nm_per_cycle'] = (df['imc_thickness_um'] / 2) * (1 - quality_factor) + np.random.normal(0, 0.5, n_samples)
    df['imc_growth_rate_nm_per_cycle'] = np.clip(df['imc_growth_rate_nm_per_cycle'], 0, 10)
    
    # Corrosion resistance (mass loss)
    df['corrosion_mass_loss_mg_cm2'] = 0.5 + 5 * (1 - quality_factor) * (df['ambient_humidity_percent'] / 50) + np.random.normal(0, 0.3, n_samples)
    df['corrosion_mass_loss_mg_cm2'] = np.clip(df['corrosion_mass_loss_mg_cm2'], 0, 10)
    
    # Overall quality score (composite metric for classification/ranking)
    df['quality_score'] = (
        0.3 * (1 - df['resistance_increase_percent'] / 200) +
        0.25 * (df['strength_retention_percent'] / 100) +
        0.2 * (df['fatigue_life_cycles'] / 3000) +
        0.15 * (1 - df['delamination_area_percent'] / 80) +
        0.1 * (1 - df['porosity_percent'] / 15)
    )
    df['quality_score'] = np.clip(df['quality_score'], 0, 1)
    
    # Quality classification
    df['quality_class'] = pd.cut(df['quality_score'], 
                                   bins=[0, 0.4, 0.6, 0.8, 1.0],
                                   labels=['Poor', 'Fair', 'Good', 'Excellent'])
    
    # Pass/Fail criteria (automotive battery standard)
    df['pass_fail'] = (
        (df['resistance_increase_percent'] < 30) &
        (df['strength_retention_percent'] > 70) &
        (df['fatigue_life_cycles'] > 800) &
        (df['delamination_area_percent'] < 20) &
        (df['contact_resistance_microohm'] < 200)
    ).astype(int)
    
    # Add manufacturing batch and timestamp
    df['batch_id'] = np.random.randint(1, 51, n_samples)
    df['timestamp'] = pd.date_range(start='2023-01-01', periods=n_samples, freq='15min')
    
    # Add sample ID
    df['sample_id'] = [f'WS_{str(i+1).zfill(6)}' for i in range(n_samples)]
    
    # Reorder columns logically
    column_order = ['sample_id', 'timestamp', 'batch_id', 
                    # Input parameters
                    'anode_material', 'cathode_material', 'anode_thickness_um', 'cathode_thickness_um',
                    'surface_finish', 'surface_roughness_ra_um', 'welding_technique',
                    'power_w', 'amplitude_um', 'force_n', 'time_ms', 'speed_mm_s', 
                    'pulse_frequency_hz', 'pulse_energy_j', 'current_ka',
                    'preheat_temp_c', 'ambient_temp_c', 'ambient_humidity_percent',
                    'energy_density_j_mm2',
                    # Characterization metrics
                    'weld_width_mm', 'weld_length_mm', 'penetration_depth_um',
                    'imc_thickness_um', 'contact_resistance_microohm',
                    'shear_strength_mpa', 'peel_strength_n_mm',
                    'porosity_percent', 'crack_density_per_mm2', 'void_fraction_percent',
                    'surface_roughness_post_weld_um', 'peak_temperature_c', 'cooling_rate_c_per_s',
                    'grain_size_um',
                    # Performance metrics
                    'thermal_cycles_tested', 'resistance_increase_percent', 'strength_retention_percent',
                    'fatigue_life_cycles', 'delamination_area_percent', 'imc_growth_rate_nm_per_cycle',
                    'corrosion_mass_loss_mg_cm2', 'quality_score', 'quality_class', 'pass_fail']
    
    df = df[column_order]
    
    return df

def generate_metadata():
    """Generate comprehensive metadata about the dataset"""
    metadata = {
        "dataset_name": "ML-Driven Inverse Design of Welding Parameters - Battery Tab Joining",
        "version": "1.0.0",
        "generation_date": datetime.now().isoformat(),
        "description": "Comprehensive synthetic dataset for machine learning-driven inverse design of dissimilar metal welding (Cu-Al) for battery tab connections. Includes process parameters, characterization metrics, and long-term performance data under thermal cycling.",
        "total_samples": 5000,
        "application": "Electric vehicle battery pack manufacturing",
        "material_system": "Copper anode to Aluminum cathode joining",
        
        "parameter_groups": {
            "input_parameters": {
                "description": "Controllable welding process parameters (design space)",
                "count": 18,
                "parameters": [
                    {"name": "anode_material", "type": "categorical", "values": ["Cu-101", "Cu-110", "Cu-C10100", "Cu-ETP"]},
                    {"name": "cathode_material", "type": "categorical", "values": ["Al-1060", "Al-1100", "Al-3003", "Al-6061"]},
                    {"name": "anode_thickness_um", "type": "continuous", "range": [100, 500], "unit": "µm"},
                    {"name": "cathode_thickness_um", "type": "continuous", "range": [100, 500], "unit": "µm"},
                    {"name": "surface_finish", "type": "categorical", "values": ["bare", "nickel_plated", "tin_plated", "anodized"]},
                    {"name": "welding_technique", "type": "categorical", "values": ["USW", "Laser", "RSW", "CMW"]},
                    {"name": "power_w", "type": "continuous", "range": [500, 4000], "unit": "W"},
                    {"name": "force_n", "type": "continuous", "range": [1000, 15000], "unit": "N"},
                    {"name": "time_ms", "type": "continuous", "range": [5, 1000], "unit": "ms"}
                ]
            },
            "characterization_metrics": {
                "description": "Immediate quality metrics after welding (forward problem outputs)",
                "count": 15,
                "metrics": [
                    "weld_width_mm", "weld_length_mm", "penetration_depth_um", "imc_thickness_um",
                    "contact_resistance_microohm", "shear_strength_mpa", "peel_strength_n_mm",
                    "porosity_percent", "crack_density_per_mm2", "void_fraction_percent",
                    "peak_temperature_c", "cooling_rate_c_per_s", "grain_size_um"
                ]
            },
            "performance_metrics": {
                "description": "Long-term performance under thermal cycling (inverse design targets)",
                "count": 8,
                "metrics": [
                    "resistance_increase_percent", "strength_retention_percent", "fatigue_life_cycles",
                    "delamination_area_percent", "imc_growth_rate_nm_per_cycle", "corrosion_mass_loss_mg_cm2",
                    "quality_score", "pass_fail"
                ],
                "target_optimization": {
                    "minimize": ["resistance_increase_percent", "delamination_area_percent", "imc_growth_rate_nm_per_cycle"],
                    "maximize": ["strength_retention_percent", "fatigue_life_cycles", "quality_score"]
                }
            }
        },
        
        "welding_techniques": {
            "USW": "Ultrasonic Welding - High frequency vibration with clamping force",
            "Laser": "Laser Welding - Focused beam melting with precise energy control",
            "RSW": "Resistance Spot Welding - Joule heating through electrical current",
            "CMW": "Cold Metal Welding - Solid-state bonding through high pressure"
        },
        
        "thermal_cycling_conditions": {
            "temperature_range": "−40°C to +85°C",
            "cycle_duration": "30 minutes per cycle",
            "test_standard": "IEC 62660-2 (Battery testing)",
            "cycles_tested": "100 to 2000 cycles"
        },
        
        "quality_criteria": {
            "automotive_grade": {
                "resistance_increase_max": "30%",
                "strength_retention_min": "70%",
                "fatigue_life_min": "800 cycles",
                "delamination_max": "20%",
                "contact_resistance_max": "200 µΩ"
            }
        },
        
        "ml_applications": [
            "Multi-objective optimization of welding parameters",
            "Inverse design: predict parameters for target performance",
            "Quality prediction from process parameters",
            "Failure mode classification",
            "Process window optimization",
            "Digital twin development",
            "Transfer learning across welding techniques"
        ],
        
        "recommended_models": [
            "Gradient Boosting (XGBoost, LightGBM) for regression tasks",
            "Neural Networks for inverse design mapping",
            "Gaussian Process Regression for uncertainty quantification",
            "Random Forest for feature importance analysis",
            "Multi-task learning for simultaneous prediction of multiple outputs"
        ],
        
        "data_splits": {
            "training": "70% (3500 samples)",
            "validation": "15% (750 samples)",
            "test": "15% (750 samples)",
            "note": "Stratified splitting recommended based on welding_technique and quality_class"
        },
        
        "feature_engineering_suggestions": [
            "Create interaction terms (e.g., energy_density = power × time / area)",
            "Polynomial features for non-linear relationships",
            "Technique-specific feature subsets",
            "Dimensionality reduction (PCA) for correlated features",
            "Domain knowledge: IMC thickness has optimal range (1-3 µm)"
        ],
        
        "physical_correlations": [
            "Higher energy density → thicker IMC layer",
            "Optimal IMC thickness (2 µm) → lowest contact resistance",
            "Excessive energy → increased porosity and cracking",
            "Higher thermal cycles → greater performance degradation",
            "Quality factor inversely proportional to resistance increase"
        ],
        
        "limitations": [
            "Synthetic data generated with physically-informed correlations",
            "Real-world data may have additional complex interactions",
            "Material property variations not fully captured",
            "Equipment-specific variations not modeled",
            "Long-term aging effects beyond thermal cycling not included"
        ],
        
        "citation": "Generated dataset for research and educational purposes in ML-driven materials processing optimization",
        "license": "CC BY-NC-SA 4.0 - Attribution-NonCommercial-ShareAlike"
    }
    
    return metadata

def generate_data_dictionary():
    """Generate detailed data dictionary for all features"""
    data_dict = {
        "Input_Parameters": {
            "sample_id": {"description": "Unique identifier for each weld sample", "type": "string", "example": "WS_000001"},
            "timestamp": {"description": "Timestamp of welding operation", "type": "datetime", "format": "YYYY-MM-DD HH:MM:SS"},
            "batch_id": {"description": "Manufacturing batch identifier", "type": "integer", "range": "1-50"},
            "anode_material": {"description": "Copper alloy grade for anode tab", "type": "categorical", "unit": "-"},
            "cathode_material": {"description": "Aluminum alloy grade for cathode tab", "type": "categorical", "unit": "-"},
            "anode_thickness_um": {"description": "Thickness of copper anode tab", "type": "float", "unit": "µm", "range": "100-500"},
            "cathode_thickness_um": {"description": "Thickness of aluminum cathode tab", "type": "float", "unit": "µm", "range": "100-500"},
            "surface_finish": {"description": "Surface treatment/coating on metal tabs", "type": "categorical", "unit": "-"},
            "surface_roughness_ra_um": {"description": "Average surface roughness before welding", "type": "float", "unit": "µm", "range": "0.1-5.0"},
            "welding_technique": {"description": "Welding process used", "type": "categorical", "values": ["USW", "Laser", "RSW", "CMW"]},
            "power_w": {"description": "Welding power (technique-dependent)", "type": "float", "unit": "W", "range": "500-4000"},
            "amplitude_um": {"description": "Vibration amplitude (USW only)", "type": "float", "unit": "µm", "range": "20-60"},
            "force_n": {"description": "Clamping/welding force", "type": "float", "unit": "N", "range": "1000-15000"},
            "time_ms": {"description": "Welding duration", "type": "float", "unit": "ms", "range": "5-1000"},
            "speed_mm_s": {"description": "Welding speed (Laser, CMW)", "type": "float", "unit": "mm/s", "range": "1-100"},
            "pulse_frequency_hz": {"description": "Pulse frequency (Laser, USW)", "type": "float", "unit": "Hz", "range": "50-20000"},
            "pulse_energy_j": {"description": "Pulse energy (Laser only)", "type": "float", "unit": "J", "range": "1-50"},
            "current_ka": {"description": "Welding current (RSW only)", "type": "float", "unit": "kA", "range": "5-25"},
            "preheat_temp_c": {"description": "Sample temperature before welding", "type": "float", "unit": "°C", "range": "20-80"},
            "ambient_temp_c": {"description": "Ambient room temperature", "type": "float", "unit": "°C", "range": "18-28"},
            "ambient_humidity_percent": {"description": "Relative humidity during welding", "type": "float", "unit": "%", "range": "30-70"},
            "energy_density_j_mm2": {"description": "Calculated energy per unit area", "type": "float", "unit": "J/mm²", "derived": True}
        },
        "Characterization_Metrics": {
            "weld_width_mm": {"description": "Width of weld nugget/joint", "type": "float", "unit": "mm", "range": "1-8"},
            "weld_length_mm": {"description": "Length of weld nugget/joint", "type": "float", "unit": "mm", "range": "2-12"},
            "penetration_depth_um": {"description": "Depth of material penetration", "type": "float", "unit": "µm", "range": "30-300"},
            "imc_thickness_um": {"description": "Intermetallic compound (CuAl2) layer thickness", "type": "float", "unit": "µm", "range": "0.2-10", "optimal": "1-3"},
            "contact_resistance_microohm": {"description": "Electrical contact resistance across joint", "type": "float", "unit": "µΩ", "range": "20-500", "target": "<100"},
            "shear_strength_mpa": {"description": "Maximum shear stress before failure", "type": "float", "unit": "MPa", "range": "15-120"},
            "peel_strength_n_mm": {"description": "Peel test force per unit width", "type": "float", "unit": "N/mm", "range": "3-35"},
            "porosity_percent": {"description": "Volumetric porosity in weld zone", "type": "float", "unit": "%", "range": "0-15", "target": "<5"},
            "crack_density_per_mm2": {"description": "Number of micro-cracks per unit area", "type": "float", "unit": "cracks/mm²", "range": "0-20", "target": "<3"},
            "void_fraction_percent": {"description": "Void/gap fraction at interface", "type": "float", "unit": "%", "range": "0-12", "target": "<5"},
            "surface_roughness_post_weld_um": {"description": "Surface roughness after welding", "type": "float", "unit": "µm", "range": "0.1-15"},
            "peak_temperature_c": {"description": "Maximum temperature during welding", "type": "float", "unit": "°C", "range": "100-900"},
            "cooling_rate_c_per_s": {"description": "Cooling rate after welding", "type": "float", "unit": "°C/s", "range": "5-200"},
            "grain_size_um": {"description": "Average grain size in weld zone", "type": "float", "unit": "µm", "range": "5-60"}
        },
        "Performance_Metrics": {
            "thermal_cycles_tested": {"description": "Number of thermal cycles performed (-40°C to +85°C)", "type": "integer", "range": "100-2000"},
            "resistance_increase_percent": {"description": "Percentage increase in contact resistance after cycling", "type": "float", "unit": "%", "range": "0-200", "target": "<30"},
            "strength_retention_percent": {"description": "Percentage of original strength retained after cycling", "type": "float", "unit": "%", "range": "20-100", "target": ">70"},
            "fatigue_life_cycles": {"description": "Number of cycles to mechanical failure", "type": "integer", "unit": "cycles", "range": "100-3000", "target": ">800"},
            "delamination_area_percent": {"description": "Percentage of interface showing delamination", "type": "float", "unit": "%", "range": "0-80", "target": "<20"},
            "imc_growth_rate_nm_per_cycle": {"description": "Rate of IMC layer growth during cycling", "type": "float", "unit": "nm/cycle", "range": "0-10", "target": "<2"},
            "corrosion_mass_loss_mg_cm2": {"description": "Mass loss due to corrosion during cycling", "type": "float", "unit": "mg/cm²", "range": "0-10", "target": "<2"},
            "quality_score": {"description": "Composite quality metric (0-1, higher is better)", "type": "float", "unit": "-", "range": "0-1", "target": ">0.8"},
            "quality_class": {"description": "Categorical quality classification", "type": "categorical", "values": ["Poor", "Fair", "Good", "Excellent"]},
            "pass_fail": {"description": "Binary pass/fail based on automotive standards", "type": "integer", "values": [0, 1], "1": "Pass", "0": "Fail"}
        }
    }
    
    return data_dict

# ===== GENERATE ALL FILES =====

print("="*80)
print("COMPREHENSIVE WELDING DATASET GENERATOR")
print("ML-Driven Inverse Design of Welding Parameters")
print("="*80)

# Generate main dataset
df_main = generate_comprehensive_welding_dataset(n_samples=5000)

# Save main dataset
print("\nSaving main dataset...")
df_main.to_csv('/workspace/welding_dataset_full.csv', index=False)
print(f"✓ Saved: welding_dataset_full.csv ({len(df_main)} samples)")

# Generate and save technique-specific datasets
print("\nGenerating technique-specific datasets...")
for technique in ['USW', 'Laser', 'RSW', 'CMW']:
    df_tech = df_main[df_main['welding_technique'] == technique].copy()
    df_tech.to_csv(f'/workspace/welding_dataset_{technique}.csv', index=False)
    print(f"✓ Saved: welding_dataset_{technique}.csv ({len(df_tech)} samples)")

# Save metadata
print("\nGenerating metadata...")
metadata = generate_metadata()
with open('/workspace/dataset_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)
print("✓ Saved: dataset_metadata.json")

# Save data dictionary
print("\nGenerating data dictionary...")
data_dict = generate_data_dictionary()
with open('/workspace/data_dictionary.json', 'w') as f:
    json.dump(data_dict, f, indent=2)
print("✓ Saved: data_dictionary.json")

# Generate summary statistics
print("\nGenerating summary statistics...")
summary_stats = df_main.describe(include='all').T
summary_stats.to_csv('/workspace/dataset_summary_statistics.csv')
print("✓ Saved: dataset_summary_statistics.csv")

# Generate correlation matrix for numerical features
print("\nGenerating correlation analysis...")
numerical_cols = df_main.select_dtypes(include=[np.number]).columns
correlation_matrix = df_main[numerical_cols].corr()
correlation_matrix.to_csv('/workspace/correlation_matrix.csv')
print("✓ Saved: correlation_matrix.csv")

# Generate quality class distribution
print("\nGenerating quality analysis...")
quality_analysis = {
    'quality_class_distribution': df_main['quality_class'].value_counts().to_dict(),
    'pass_rate_percent': (df_main['pass_fail'].sum() / len(df_main) * 100),
    'technique_pass_rates': df_main.groupby('welding_technique')['pass_fail'].mean().to_dict(),
    'average_quality_score': df_main['quality_score'].mean(),
    'average_metrics': {
        'resistance_increase': df_main['resistance_increase_percent'].mean(),
        'strength_retention': df_main['strength_retention_percent'].mean(),
        'fatigue_life': df_main['fatigue_life_cycles'].mean()
    }
}
with open('/workspace/quality_analysis.json', 'w') as f:
    json.dump(quality_analysis, f, indent=2)
print("✓ Saved: quality_analysis.json")

# Create sample splits for ML
print("\nCreating train/validation/test splits...")
from sklearn.model_selection import train_test_split

# Stratified split
df_train, df_temp = train_test_split(df_main, test_size=0.3, 
                                      stratify=df_main['quality_class'], 
                                      random_state=42)
# Second split without stratification to avoid errors with small groups
df_val, df_test = train_test_split(df_temp, test_size=0.5, 
                                     random_state=42)

df_train.to_csv('/workspace/welding_dataset_train.csv', index=False)
df_val.to_csv('/workspace/welding_dataset_validation.csv', index=False)
df_test.to_csv('/workspace/welding_dataset_test.csv', index=False)

print(f"✓ Saved: welding_dataset_train.csv ({len(df_train)} samples)")
print(f"✓ Saved: welding_dataset_validation.csv ({len(df_val)} samples)")
print(f"✓ Saved: welding_dataset_test.csv ({len(df_test)} samples)")

# Generate visualization recommendations
print("\nGenerating analysis recommendations...")
recommendations = """
RECOMMENDED ANALYSES AND VISUALIZATIONS
=========================================

1. EXPLORATORY DATA ANALYSIS
   - Distribution plots for all numerical features
   - Box plots comparing techniques
   - Correlation heatmap (see correlation_matrix.csv)
   - Pair plots for key parameters vs quality metrics

2. FEATURE IMPORTANCE
   - Random Forest feature importance
   - SHAP values for model interpretability
   - Permutation importance analysis
   - Partial dependence plots

3. PROCESS WINDOW OPTIMIZATION
   - 2D contour plots (e.g., power vs time → quality_score)
   - Multi-objective Pareto fronts
   - Process capability analysis (Cp, Cpk)

4. INVERSE DESIGN MODELS
   - Neural network: (target_performance) → (process_parameters)
   - Bayesian optimization for parameter search
   - Gaussian Process with uncertainty quantification

5. FAILURE PREDICTION
   - Classification models for pass/fail prediction
   - Survival analysis for fatigue life
   - Anomaly detection for defect prediction

6. TECHNIQUE COMPARISON
   - Statistical comparison (ANOVA, Kruskal-Wallis)
   - Technique-specific optimal parameter ranges
   - Cost-performance trade-off analysis

7. TEMPORAL ANALYSIS
   - Batch effects analysis
   - Process drift detection
   - Control charts (X-bar, R charts)

KEY INSIGHTS TO INVESTIGATE
============================

1. Optimal IMC thickness: ~2 µm balances strength and resistance
2. Energy density sweet spot: moderate levels avoid defects
3. Thermal cycling degradation: non-linear with initial quality
4. Technique-specific advantages:
   - USW: Best for thin foils, low IMC growth
   - Laser: High precision, narrow HAZ
   - RSW: Fast, economical for mass production
   - CMW: No heat, minimal IMC formation

MACHINE LEARNING PIPELINE
==========================

Step 1: Data Preprocessing
   - Handle technique-specific features (set unused to 0 or drop)
   - Normalize/standardize numerical features
   - One-hot encode categorical variables
   - Feature engineering (interaction terms)

Step 2: Forward Model (Process → Quality)
   - Target: quality_score, pass_fail, specific metrics
   - Models: XGBoost, Random Forest, Neural Network
   - Cross-validation with stratification

Step 3: Inverse Model (Performance → Process)
   - Target: process parameters
   - Given: desired performance metrics
   - Models: Conditional GAN, Mixture Density Network, Bayesian Optimization

Step 4: Multi-Objective Optimization
   - Objectives: Maximize (strength, fatigue_life), Minimize (resistance_increase, cost)
   - Algorithms: NSGA-II, MOEA/D, Bayesian Multi-Objective Optimization

Step 5: Uncertainty Quantification
   - Gaussian Processes for prediction intervals
   - Monte Carlo dropout for neural networks
   - Bootstrap aggregating for ensemble uncertainty

Step 6: Model Deployment
   - Real-time quality prediction
   - Parameter recommendation system
   - Process control feedback loop
"""

with open('/workspace/analysis_recommendations.txt', 'w') as f:
    f.write(recommendations)
print("✓ Saved: analysis_recommendations.txt")

# Final summary
print("\n" + "="*80)
print("DATASET GENERATION COMPLETE")
print("="*80)
print(f"\nTotal samples generated: {len(df_main)}")
print(f"Total features: {len(df_main.columns)}")
print(f"Pass rate: {quality_analysis['pass_rate_percent']:.1f}%")
print(f"Average quality score: {quality_analysis['average_quality_score']:.3f}")
print("\nQuality Distribution:")
for qual, count in quality_analysis['quality_class_distribution'].items():
    print(f"  {qual}: {count} samples ({count/len(df_main)*100:.1f}%)")
print("\nTechnique Distribution:")
for tech, count in df_main['welding_technique'].value_counts().items():
    pass_rate = quality_analysis['technique_pass_rates'][tech] * 100
    print(f"  {tech}: {count} samples (Pass rate: {pass_rate:.1f}%)")

print("\n" + "="*80)
print("FILES GENERATED:")
print("="*80)
print("1. welding_dataset_full.csv - Complete dataset (5000 samples)")
print("2. welding_dataset_USW.csv - Ultrasonic welding only")
print("3. welding_dataset_Laser.csv - Laser welding only")
print("4. welding_dataset_RSW.csv - Resistance spot welding only")
print("5. welding_dataset_CMW.csv - Cold metal welding only")
print("6. welding_dataset_train.csv - Training set (70%)")
print("7. welding_dataset_validation.csv - Validation set (15%)")
print("8. welding_dataset_test.csv - Test set (15%)")
print("9. dataset_metadata.json - Complete metadata and documentation")
print("10. data_dictionary.json - Detailed feature descriptions")
print("11. dataset_summary_statistics.csv - Statistical summary")
print("12. correlation_matrix.csv - Feature correlations")
print("13. quality_analysis.json - Quality metrics and pass rates")
print("14. analysis_recommendations.txt - Analysis guide")
print("="*80)
print("\nDataset ready for ML-driven inverse design research!")
print("Start with exploratory analysis or jump straight to modeling.")
print("="*80)
