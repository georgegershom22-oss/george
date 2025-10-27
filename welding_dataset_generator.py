"""
Comprehensive Welding Dataset Generator for ML-Driven Inverse Design
=====================================================================

This script generates a realistic dataset for inverse design of welding parameters
with focus on extreme temperature cycling performance.

Dataset includes:
1. Input Parameters (Design Space)
2. Characterization & Quality Metrics (Forward Problem Outputs)
3. Performance & Validation Metrics (Inverse Design Targets)
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

class WeldingDatasetGenerator:
    """Generate comprehensive welding dataset with physics-based correlations."""
    
    def __init__(self, n_samples: int = 5000):
        self.n_samples = n_samples
        
        # Material properties database
        self.material_properties = {
            'Copper': {
                'thermal_conductivity': 401,  # W/m·K
                'melting_point': 1085,  # °C
                'electrical_resistivity': 1.68e-8,  # Ω·m
                'yield_strength': 70,  # MPa
                'density': 8960,  # kg/m³
                'hardness': 50,  # HV
                'CTE': 16.5e-6  # Coefficient of thermal expansion (1/K)
            },
            'Aluminum': {
                'thermal_conductivity': 237,
                'melting_point': 660,
                'electrical_resistivity': 2.65e-8,
                'yield_strength': 40,
                'density': 2700,
                'hardness': 25,
                'CTE': 23.1e-6
            },
            'Nickel': {
                'thermal_conductivity': 91,
                'melting_point': 1455,
                'electrical_resistivity': 6.99e-8,
                'yield_strength': 148,
                'density': 8908,
                'hardness': 120,
                'CTE': 13.4e-6
            },
            'Steel_304': {
                'thermal_conductivity': 16.2,
                'melting_point': 1450,
                'electrical_resistivity': 7.2e-7,
                'yield_strength': 215,
                'density': 8000,
                'hardness': 150,
                'CTE': 17.3e-6
            }
        }
        
        # Coating properties
        self.coating_properties = {
            'None': {'resistance_multiplier': 1.0, 'strength_multiplier': 1.0},
            'Nickel': {'resistance_multiplier': 1.2, 'strength_multiplier': 1.15},
            'Tin': {'resistance_multiplier': 1.5, 'strength_multiplier': 0.95},
            'Silver': {'resistance_multiplier': 0.8, 'strength_multiplier': 1.1},
            'Oxide': {'resistance_multiplier': 3.0, 'strength_multiplier': 0.7}
        }
    
    def generate_input_parameters(self) -> pd.DataFrame:
        """Generate input parameters (design space)."""
        
        data = {}
        
        # Base Materials
        anode_materials = np.random.choice(
            ['Copper', 'Aluminum', 'Nickel', 'Steel_304'], 
            size=self.n_samples, 
            p=[0.5, 0.3, 0.15, 0.05]
        )
        cathode_materials = np.random.choice(
            ['Copper', 'Aluminum', 'Nickel'], 
            size=self.n_samples,
            p=[0.4, 0.45, 0.15]
        )
        
        data['anode_material'] = anode_materials
        data['cathode_material'] = cathode_materials
        
        # Tab Thickness (µm) - typical range for battery tabs
        data['anode_thickness_um'] = np.random.uniform(50, 500, self.n_samples)
        data['cathode_thickness_um'] = np.random.uniform(50, 500, self.n_samples)
        
        # Surface finish and coating
        data['anode_surface_roughness_um'] = np.random.lognormal(0, 0.5, self.n_samples)
        data['cathode_surface_roughness_um'] = np.random.lognormal(0, 0.5, self.n_samples)
        
        data['anode_coating'] = np.random.choice(
            ['None', 'Nickel', 'Tin', 'Silver', 'Oxide'],
            size=self.n_samples,
            p=[0.3, 0.25, 0.2, 0.15, 0.1]
        )
        data['cathode_coating'] = np.random.choice(
            ['None', 'Nickel', 'Tin', 'Silver', 'Oxide'],
            size=self.n_samples,
            p=[0.3, 0.25, 0.2, 0.15, 0.1]
        )
        
        # Welding Technique
        welding_techniques = np.random.choice(
            ['Ultrasonic', 'Laser', 'Resistance_Spot', 'Friction_Stir'],
            size=self.n_samples,
            p=[0.4, 0.35, 0.2, 0.05]
        )
        data['welding_technique'] = welding_techniques
        
        # Welding Process Parameters
        # Power/Energy depends on technique
        power_base = np.where(
            welding_techniques == 'Ultrasonic', 
            np.random.uniform(500, 3000, self.n_samples),  # Watts
            np.where(
                welding_techniques == 'Laser',
                np.random.uniform(100, 2000, self.n_samples),  # Watts
                np.where(
                    welding_techniques == 'Resistance_Spot',
                    np.random.uniform(2000, 8000, self.n_samples),  # Watts
                    np.random.uniform(1000, 4000, self.n_samples)  # Friction Stir
                )
            )
        )
        data['power_W'] = power_base
        
        # Pulse energy for laser (J)
        data['pulse_energy_J'] = np.where(
            welding_techniques == 'Laser',
            np.random.uniform(1, 50, self.n_samples),
            np.nan
        )
        
        # Amplitude for ultrasonic (µm)
        data['amplitude_um'] = np.where(
            welding_techniques == 'Ultrasonic',
            np.random.uniform(10, 60, self.n_samples),
            np.nan
        )
        
        # Force/Pressure (N and MPa)
        force_base = np.random.uniform(100, 2000, self.n_samples)
        data['clamping_force_N'] = force_base
        
        # Calculate pressure from force and approximate contact area
        contact_area_mm2 = np.random.uniform(5, 50, self.n_samples)
        data['pressure_MPa'] = force_base / contact_area_mm2
        
        # Weld time (ms)
        data['weld_time_ms'] = np.where(
            welding_techniques == 'Ultrasonic',
            np.random.uniform(100, 1500, self.n_samples),
            np.where(
                welding_techniques == 'Laser',
                np.random.uniform(1, 100, self.n_samples),
                np.where(
                    welding_techniques == 'Resistance_Spot',
                    np.random.uniform(50, 500, self.n_samples),
                    np.random.uniform(500, 5000, self.n_samples)
                )
            )
        )
        
        # Welding speed for laser (mm/s)
        data['welding_speed_mm_s'] = np.where(
            welding_techniques == 'Laser',
            np.random.uniform(10, 200, self.n_samples),
            np.nan
        )
        
        # Pulse frequency for laser (Hz)
        data['pulse_frequency_Hz'] = np.where(
            welding_techniques == 'Laser',
            np.random.uniform(10, 200, self.n_samples),
            np.nan
        )
        
        # Frequency for ultrasonic (kHz)
        data['ultrasonic_frequency_kHz'] = np.where(
            welding_techniques == 'Ultrasonic',
            np.random.choice([20, 40, 60], self.n_samples),
            np.nan
        )
        
        # Environmental conditions
        data['preheat_temperature_C'] = np.random.uniform(20, 150, self.n_samples)
        data['ambient_temperature_C'] = np.random.uniform(15, 35, self.n_samples)
        data['ambient_humidity_percent'] = np.random.uniform(20, 80, self.n_samples)
        
        # Shielding gas for laser
        data['shielding_gas'] = np.where(
            welding_techniques == 'Laser',
            np.random.choice(['Argon', 'Nitrogen', 'Helium', 'None'], self.n_samples),
            'None'
        )
        
        # Sample preparation
        data['cleaning_method'] = np.random.choice(
            ['Mechanical', 'Chemical', 'Plasma', 'None'],
            size=self.n_samples,
            p=[0.3, 0.3, 0.2, 0.2]
        )
        
        return pd.DataFrame(data)
    
    def calculate_heat_input(self, df: pd.DataFrame) -> np.ndarray:
        """Calculate total heat input to the weld (J/mm)."""
        heat_input = np.zeros(len(df))
        
        for i in range(len(df)):
            if df.loc[i, 'welding_technique'] == 'Laser':
                # For laser: Energy per unit length
                speed = df.loc[i, 'welding_speed_mm_s']
                power = df.loc[i, 'power_W']
                heat_input[i] = power / speed if speed > 0 else power
            else:
                # For other methods: Total energy / approximate weld length
                power = df.loc[i, 'power_W']
                time_s = df.loc[i, 'weld_time_ms'] / 1000
                heat_input[i] = power * time_s / 10  # Assume 10mm weld length
        
        return heat_input
    
    def calculate_characterization_metrics(self, input_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate characterization and quality metrics (forward problem outputs)."""
        
        metrics = {}
        n = len(input_df)
        
        # Calculate heat input
        heat_input = self.calculate_heat_input(input_df)
        metrics['heat_input_J_per_mm'] = heat_input
        
        # Weld geometry
        # Nugget diameter depends on heat input and pressure
        base_nugget = 2 + 0.01 * heat_input + 0.0005 * input_df['pressure_MPa'].values
        metrics['weld_nugget_diameter_mm'] = np.clip(
            base_nugget + np.random.normal(0, 0.3, n), 
            0.5, 15
        )
        
        # Penetration depth
        base_penetration = np.minimum(
            input_df['anode_thickness_um'].values * 0.6,
            input_df['cathode_thickness_um'].values * 0.6
        ) / 1000  # Convert to mm
        metrics['penetration_depth_mm'] = np.clip(
            base_penetration * (0.8 + 0.4 * np.random.random(n)),
            0.01, 0.5
        )
        
        # Weld width
        metrics['weld_width_mm'] = metrics['weld_nugget_diameter_mm'] * (0.9 + 0.2 * np.random.random(n))
        
        # Interface bond area (mm²)
        metrics['bond_area_mm2'] = np.pi * (metrics['weld_nugget_diameter_mm'] / 2) ** 2
        
        # Mechanical Properties
        # Base strength calculation considering materials and process
        anode_strength = np.array([
            self.material_properties[mat]['yield_strength'] 
            for mat in input_df['anode_material']
        ])
        cathode_strength = np.array([
            self.material_properties[mat]['yield_strength'] 
            for mat in input_df['cathode_material']
        ])
        
        # Use weaker material as base
        base_strength = np.minimum(anode_strength, cathode_strength)
        
        # Strength depends on heat input (too much or too little is bad)
        optimal_heat = 50  # J/mm
        heat_factor = np.exp(-((heat_input - optimal_heat) ** 2) / (2 * 30 ** 2))
        
        # Coating effect
        anode_coating_factor = np.array([
            self.coating_properties[coat]['strength_multiplier'] 
            for coat in input_df['anode_coating']
        ])
        cathode_coating_factor = np.array([
            self.coating_properties[coat]['strength_multiplier'] 
            for coat in input_df['cathode_coating']
        ])
        coating_factor = (anode_coating_factor + cathode_coating_factor) / 2
        
        # Surface roughness effect (too rough is bad)
        roughness_factor = 1 / (1 + 0.1 * (input_df['anode_surface_roughness_um'].values + 
                                            input_df['cathode_surface_roughness_um'].values))
        
        # Pressure effect (optimal range exists)
        pressure = input_df['pressure_MPa'].values
        pressure_factor = np.clip(pressure / 50, 0.5, 1.5)
        
        # Tensile strength (MPa)
        metrics['tensile_strength_MPa'] = np.clip(
            base_strength * heat_factor * coating_factor * roughness_factor * 
            pressure_factor * metrics['bond_area_mm2'] / 10 * 
            (0.9 + 0.2 * np.random.random(n)),
            5, 400
        )
        
        # Shear strength (typically 60-80% of tensile)
        metrics['shear_strength_MPa'] = metrics['tensile_strength_MPa'] * (0.6 + 0.2 * np.random.random(n))
        
        # Peel strength (N/mm)
        metrics['peel_strength_N_per_mm'] = np.clip(
            metrics['tensile_strength_MPa'] * 0.1 * (0.8 + 0.4 * np.random.random(n)),
            1, 50
        )
        
        # Microhardness (HV)
        # Welding typically increases hardness
        anode_hardness = np.array([
            self.material_properties[mat]['hardness'] 
            for mat in input_df['anode_material']
        ])
        cathode_hardness = np.array([
            self.material_properties[mat]['hardness'] 
            for mat in input_df['cathode_material']
        ])
        base_hardness = (anode_hardness + cathode_hardness) / 2
        
        # Heat input increases hardness (work hardening and grain refinement)
        hardness_multiplier = 1 + 0.3 * heat_factor * (0.9 + 0.2 * np.random.random(n))
        metrics['weld_hardness_HV'] = base_hardness * hardness_multiplier
        
        metrics['heat_affected_zone_hardness_HV'] = base_hardness * (1.1 + 0.1 * np.random.random(n))
        
        # Electrical Properties
        # Contact resistance (µΩ)
        anode_resistivity = np.array([
            self.material_properties[mat]['electrical_resistivity'] 
            for mat in input_df['anode_material']
        ])
        cathode_resistivity = np.array([
            self.material_properties[mat]['electrical_resistivity'] 
            for mat in input_df['cathode_material']
        ])
        
        # Coating resistance effect
        anode_resistance_factor = np.array([
            self.coating_properties[coat]['resistance_multiplier'] 
            for coat in input_df['anode_coating']
        ])
        cathode_resistance_factor = np.array([
            self.coating_properties[coat]['resistance_multiplier'] 
            for coat in input_df['cathode_coating']
        ])
        
        # Base contact resistance calculation
        base_resistance = ((anode_resistivity + cathode_resistivity) * 1e6 / 
                          metrics['bond_area_mm2'] * 
                          (anode_resistance_factor + cathode_resistance_factor))
        
        # Surface roughness increases resistance
        roughness_effect = 1 + 0.5 * (input_df['anode_surface_roughness_um'].values + 
                                       input_df['cathode_surface_roughness_um'].values)
        
        # Better bonding (higher strength) means lower resistance
        bond_quality = metrics['tensile_strength_MPa'] / 100
        resistance_reduction = 1 / (1 + 0.1 * bond_quality)
        
        metrics['contact_resistance_uOhm'] = np.clip(
            base_resistance * roughness_effect * resistance_reduction * 
            (0.8 + 0.4 * np.random.random(n)),
            10, 5000
        )
        
        # Bulk weld resistance (µΩ)
        metrics['weld_resistance_uOhm'] = metrics['contact_resistance_uOhm'] * (0.3 + 0.4 * np.random.random(n))
        
        # Current carrying capacity (A) - related to cross-sectional area and material
        current_density_limit = 3  # A/mm² (typical for copper)
        metrics['current_capacity_A'] = (metrics['bond_area_mm2'] * current_density_limit * 
                                        (0.8 + 0.4 * np.random.random(n)))
        
        # Thermal Properties
        # Thermal conductivity (W/m·K)
        anode_thermal_cond = np.array([
            self.material_properties[mat]['thermal_conductivity'] 
            for mat in input_df['anode_material']
        ])
        cathode_thermal_cond = np.array([
            self.material_properties[mat]['thermal_conductivity'] 
            for mat in input_df['cathode_material']
        ])
        
        # Weld thermal conductivity (often lower than base materials)
        metrics['weld_thermal_conductivity_W_mK'] = (
            (anode_thermal_cond + cathode_thermal_cond) / 2 * 
            (0.7 + 0.3 * heat_factor) * (0.9 + 0.2 * np.random.random(n))
        )
        
        # Thermal resistance (K/W)
        weld_thickness_mm = (input_df['anode_thickness_um'].values + 
                            input_df['cathode_thickness_um'].values) / 2000
        metrics['thermal_resistance_K_W'] = (
            weld_thickness_mm / (metrics['weld_thermal_conductivity_W_mK'] * 
                                metrics['bond_area_mm2'] / 1000)
        )
        
        # Microstructural Features
        # Grain size (µm) - finer grains often mean better properties
        base_grain_size = 50
        grain_refinement = np.exp(-heat_input / 100)  # High heat = coarser grains
        metrics['average_grain_size_um'] = np.clip(
            base_grain_size * (1 + 2 * (1 - grain_refinement)) * (0.8 + 0.4 * np.random.random(n)),
            5, 200
        )
        
        # Porosity (%) - defects
        # Better process control (optimal parameters) means less porosity
        porosity_base = 1.0  # 1% base porosity
        
        # High heat or low pressure increases porosity
        heat_porosity = 0.5 * np.abs(heat_input - optimal_heat) / optimal_heat
        pressure_porosity = 0.5 * (1 - np.clip(pressure / 50, 0, 1))
        
        # Coating oxide can increase porosity
        oxide_porosity = np.where(
            (input_df['anode_coating'] == 'Oxide') | (input_df['cathode_coating'] == 'Oxide'),
            1.0, 0.0
        )
        
        metrics['porosity_percent'] = np.clip(
            porosity_base + heat_porosity + pressure_porosity + oxide_porosity + 
            np.random.exponential(0.5, n),
            0, 15
        )
        
        # Intermetallic compound thickness (µm) - for dissimilar metals
        dissimilar_metals = input_df['anode_material'].values != input_df['cathode_material'].values
        metrics['intermetallic_thickness_um'] = np.where(
            dissimilar_metals,
            0.5 + 0.05 * heat_input * (0.8 + 0.4 * np.random.random(n)),
            0
        )
        
        # Crack density (cracks/mm²)
        # More likely with: high heat input, dissimilar materials, high thermal gradient
        anode_cte = np.array([
            self.material_properties[mat]['CTE'] 
            for mat in input_df['anode_material']
        ])
        cathode_cte = np.array([
            self.material_properties[mat]['CTE'] 
            for mat in input_df['cathode_material']
        ])
        cte_mismatch = np.abs(anode_cte - cathode_cte) * 1e6
        
        crack_probability = (0.1 * (heat_input / optimal_heat - 1) ** 2 + 
                            0.05 * cte_mismatch + 
                            0.02 * metrics['porosity_percent'])
        
        metrics['crack_density_per_mm2'] = np.clip(
            crack_probability * np.random.exponential(1, n),
            0, 10
        )
        
        # Surface quality
        metrics['surface_roughness_after_weld_um'] = (
            (input_df['anode_surface_roughness_um'].values + 
             input_df['cathode_surface_roughness_um'].values) / 2 * 
            (1.2 + 0.3 * np.random.random(n))
        )
        
        # Weld spatter (number of particles) - mainly for laser and resistance welding
        spatter_base = np.where(
            input_df['welding_technique'].values == 'Laser',
            np.random.poisson(5 + heat_input / 20, n),
            np.where(
                input_df['welding_technique'].values == 'Resistance_Spot',
                np.random.poisson(10 + heat_input / 30, n),
                np.random.poisson(1, n)
            )
        )
        metrics['weld_spatter_count'] = spatter_base
        
        # Discoloration/oxidation score (0-10)
        oxidation_base = 2.0
        oxidation_temp_effect = heat_input / 50
        oxidation_coating_effect = np.where(
            (input_df['anode_coating'] == 'Oxide') | (input_df['cathode_coating'] == 'Oxide'),
            3.0, 0.0
        )
        
        metrics['oxidation_score'] = np.clip(
            oxidation_base + oxidation_temp_effect + oxidation_coating_effect + 
            np.random.normal(0, 1, n),
            0, 10
        )
        
        return pd.DataFrame(metrics)
    
    def calculate_performance_metrics(self, input_df: pd.DataFrame, 
                                     char_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate performance and validation metrics (inverse design targets)."""
        
        metrics = {}
        n = len(input_df)
        
        # Thermal Cycling Test Parameters
        # Standard thermal cycling: -40°C to +85°C (automotive)
        # Extreme: -55°C to +150°C (aerospace/battery)
        metrics['thermal_cycle_min_temp_C'] = -40 - 15 * np.random.random(n)
        metrics['thermal_cycle_max_temp_C'] = 85 + 65 * np.random.random(n)
        metrics['thermal_cycle_rate_C_per_min'] = 5 + 15 * np.random.random(n)
        metrics['thermal_cycle_dwell_time_min'] = 10 + 20 * np.random.random(n)
        
        # Calculate thermal stress
        anode_cte = np.array([
            self.material_properties[mat]['CTE'] 
            for mat in input_df['anode_material']
        ])
        cathode_cte = np.array([
            self.material_properties[mat]['CTE'] 
            for mat in input_df['cathode_material']
        ])
        
        delta_temp = metrics['thermal_cycle_max_temp_C'] - metrics['thermal_cycle_min_temp_C']
        cte_mismatch = np.abs(anode_cte - cathode_cte)
        thermal_strain = cte_mismatch * delta_temp
        
        # Thermal stress (MPa) - simplified
        base_modulus = 100e3  # MPa (approximate)
        metrics['thermal_stress_MPa'] = thermal_strain * base_modulus / 1000
        
        # Fatigue Life (Cycles to Failure)
        # Based on: initial strength, thermal stress, porosity, cracks, intermetallics
        
        # Strength factor (higher initial strength = longer life)
        strength_factor = np.clip(char_df['tensile_strength_MPa'].values / 50, 0.5, 8)
        
        # Thermal stress factor (higher stress = shorter life)
        stress_factor = 1 / (1 + metrics['thermal_stress_MPa'] / 100)
        
        # Defect factor (porosity and cracks reduce life)
        defect_score = char_df['porosity_percent'].values / 10 + char_df['crack_density_per_mm2'].values / 5
        defect_factor = 1 / (1 + defect_score)
        
        # Intermetallic factor (thick intermetallics are brittle)
        intermetallic_factor = 1 / (1 + char_df['intermetallic_thickness_um'].values / 20)
        
        # Bond quality factor
        bond_factor = np.clip(char_df['bond_area_mm2'] / 10, 0.5, 5)
        
        # Base fatigue life
        base_cycles = 5000
        metrics['cycles_to_failure'] = np.clip(
            base_cycles * strength_factor * stress_factor * defect_factor * 
            intermetallic_factor * bond_factor * np.random.lognormal(0, 0.8, n),
            50, 100000
        ).astype(int)
        
        # Resistance degradation over cycling
        # Resistance typically increases over thermal cycling
        initial_resistance = char_df['contact_resistance_uOhm'].values
        
        # Degradation rate (%/1000 cycles)
        degradation_rate_base = 5  # 5% per 1000 cycles
        degradation_rate = (degradation_rate_base * 
                           (1 + 0.5 * np.random.random(n)) * 
                           (1 + 0.1 * char_df['porosity_percent'].values) * 
                           (1 + 0.2 * thermal_strain * 1e4))
        
        metrics['resistance_degradation_percent_per_1000cycles'] = degradation_rate
        
        # Final resistance at 50% of life
        cycles_at_50pct = metrics['cycles_to_failure'] * 0.5
        metrics['resistance_after_50pct_life_uOhm'] = (
            initial_resistance * (1 + degradation_rate * cycles_at_50pct / 1000 / 100)
        )
        
        # Strength degradation
        strength_degradation_rate = degradation_rate * 0.3  # Strength degrades slower than resistance
        metrics['strength_degradation_percent_per_1000cycles'] = strength_degradation_rate
        
        metrics['tensile_strength_after_50pct_life_MPa'] = (
            char_df['tensile_strength_MPa'].values * 
            (1 - strength_degradation_rate * cycles_at_50pct / 1000 / 100)
        )
        
        # Failure Mode Classification
        # 1: Interfacial (poor bonding)
        # 2: Ductile (base metal failure - good!)
        # 3: Brittle (intermetallic/grain boundary)
        # 4: Fatigue crack propagation
        # 5: Delamination
        
        failure_mode_prob = np.random.random(n)
        high_strength = char_df['tensile_strength_MPa'].values > 100
        high_defects = (char_df['porosity_percent'].values > 3) | (char_df['crack_density_per_mm2'].values > 2)
        thick_intermetallic = char_df['intermetallic_thickness_um'].values > 5
        
        metrics['primary_failure_mode'] = np.select(
            [high_strength & ~high_defects, thick_intermetallic, high_defects, failure_mode_prob < 0.3],
            [2, 3, 4, 5],
            default=1
        )
        
        # Crack propagation rate (mm/cycle)
        metrics['crack_propagation_rate_um_per_cycle'] = np.clip(
            0.001 * metrics['thermal_stress_MPa'] * 
            (1 + char_df['crack_density_per_mm2'].values) * 
            np.random.lognormal(-2, 0.5, n),
            0.0001, 1
        )
        
        # Deformation/Warpage after cycling (µm)
        metrics['permanent_deformation_um'] = np.clip(
            thermal_strain * 1e6 * (input_df['anode_thickness_um'].values + 
                                    input_df['cathode_thickness_um'].values) / 2 * 
            (0.5 + np.random.random(n)),
            0, 100
        )
        
        # Electrical Performance Degradation
        # Power dissipation increase (%)
        metrics['power_dissipation_increase_percent'] = (
            (metrics['resistance_after_50pct_life_uOhm'] / initial_resistance - 1) * 100
        )
        
        # Voltage drop increase at rated current (mV)
        rated_current = char_df['current_capacity_A'].values * 0.8  # 80% of capacity
        voltage_drop_initial = initial_resistance * 1e-6 * rated_current * 1000  # mV
        voltage_drop_final = metrics['resistance_after_50pct_life_uOhm'] * 1e-6 * rated_current * 1000
        metrics['voltage_drop_increase_mV'] = voltage_drop_final - voltage_drop_initial
        
        # Thermal performance degradation
        # Interface thermal resistance increase (%)
        metrics['thermal_resistance_increase_percent'] = (
            degradation_rate * 0.5 * (0.8 + 0.4 * np.random.random(n))
        )
        
        # Maximum operating temperature before failure (°C)
        # Based on materials and weld quality
        anode_melting = np.array([
            self.material_properties[mat]['melting_point'] 
            for mat in input_df['anode_material']
        ])
        cathode_melting = np.array([
            self.material_properties[mat]['melting_point'] 
            for mat in input_df['cathode_material']
        ])
        min_melting = np.minimum(anode_melting, cathode_melting)
        
        # Max operating temp is typically 60-70% of melting point
        safety_factor = 0.6 + 0.1 * (char_df['tensile_strength_MPa'].values / 200)
        metrics['max_operating_temp_C'] = min_melting * safety_factor
        
        # Long-term reliability metrics
        # Mean time to failure (hours) at rated conditions
        mtbf_base = 10000  # hours
        metrics['MTBF_hours'] = (
            mtbf_base * strength_factor * defect_factor * bond_factor * 
            np.random.lognormal(0, 0.3, n)
        )
        
        # Reliability at 10 years (%)
        # Using exponential reliability model
        ten_years_hours = 10 * 365 * 24
        metrics['reliability_10years_percent'] = (
            np.exp(-ten_years_hours / metrics['MTBF_hours']) * 100
        )
        
        # Environmental Resistance Scores (0-10, higher is better)
        # Corrosion resistance
        corrosion_resistance_base = 7.0
        anode_good_coating = (input_df['anode_coating'] == 'Nickel') | (input_df['anode_coating'] == 'Silver')
        cathode_good_coating = (input_df['cathode_coating'] == 'Nickel') | (input_df['cathode_coating'] == 'Silver')
        coating_benefit = np.where(
            anode_good_coating | cathode_good_coating,
            2.0, 0.0
        )
        porosity_penalty = char_df['porosity_percent'].values / 2
        metrics['corrosion_resistance_score'] = np.clip(
            corrosion_resistance_base + coating_benefit - porosity_penalty + 
            np.random.normal(0, 0.5, n),
            0, 10
        )
        
        # Vibration resistance
        metrics['vibration_resistance_score'] = np.clip(
            5 + 0.3 * char_df['tensile_strength_MPa'].values / 10 - 
            0.5 * char_df['crack_density_per_mm2'].values + 
            np.random.normal(0, 0.5, n),
            0, 10
        )
        
        # Shock resistance
        metrics['shock_resistance_score'] = np.clip(
            5 + 0.2 * char_df['shear_strength_MPa'].values / 10 - 
            0.3 * char_df['porosity_percent'].values + 
            np.random.normal(0, 0.5, n),
            0, 10
        )
        
        # Quality Classification
        # Based on cycles to failure and degradation rates
        excellent = (metrics['cycles_to_failure'] > 10000) & (degradation_rate < 5)
        good = (metrics['cycles_to_failure'] > 5000) & (degradation_rate < 10)
        acceptable = (metrics['cycles_to_failure'] > 1000) & (degradation_rate < 20)
        
        metrics['quality_class'] = np.select(
            [excellent, good, acceptable],
            ['Excellent', 'Good', 'Acceptable'],
            default='Poor'
        )
        
        # Overall performance score (0-100)
        # Weighted combination of key metrics
        cycle_score = np.clip(metrics['cycles_to_failure'] / 200, 0, 50)
        resistance_score = np.clip(50 - metrics['resistance_degradation_percent_per_1000cycles'], 0, 25)
        reliability_score = np.clip(metrics['reliability_10years_percent'] / 4, 0, 25)
        
        metrics['overall_performance_score'] = cycle_score + resistance_score + reliability_score
        
        return pd.DataFrame(metrics)
    
    def generate_complete_dataset(self) -> pd.DataFrame:
        """Generate complete dataset with all parts."""
        
        print("Generating input parameters...")
        input_df = self.generate_input_parameters()
        
        print("Calculating characterization metrics...")
        char_df = self.calculate_characterization_metrics(input_df)
        
        print("Calculating performance metrics...")
        perf_df = self.calculate_performance_metrics(input_df, char_df)
        
        # Combine all dataframes
        complete_df = pd.concat([input_df, char_df, perf_df], axis=1)
        
        # Add sample ID
        complete_df.insert(0, 'sample_id', [f'WS_{i:05d}' for i in range(len(complete_df))])
        
        # Add timestamp
        base_date = pd.Timestamp('2024-01-01')
        complete_df['collection_date'] = [
            base_date + pd.Timedelta(days=int(i/10)) 
            for i in range(len(complete_df))
        ]
        
        return complete_df
    
    def generate_statistical_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate statistical summary of the dataset."""
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        summary = df[numeric_cols].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95])
        summary.loc['variance'] = df[numeric_cols].var()
        summary.loc['skewness'] = df[numeric_cols].skew()
        summary.loc['kurtosis'] = df[numeric_cols].kurtosis()
        
        return summary


def main():
    """Main function to generate and save the dataset."""
    
    print("="*80)
    print("Welding Dataset Generator for ML-Driven Inverse Design")
    print("="*80)
    print()
    
    # Generate dataset with 5000 samples
    generator = WeldingDatasetGenerator(n_samples=5000)
    
    print("Generating complete dataset...")
    dataset = generator.generate_complete_dataset()
    
    print(f"\nDataset generated successfully!")
    print(f"Total samples: {len(dataset)}")
    print(f"Total features: {len(dataset.columns)}")
    print()
    
    # Save complete dataset
    print("Saving complete dataset...")
    dataset.to_csv('/workspace/welding_dataset_complete.csv', index=False)
    print("✓ Saved: welding_dataset_complete.csv")
    
    # Save separate parts for easier analysis
    print("\nSaving dataset parts...")
    
    # Input parameters
    input_cols = ['sample_id', 'collection_date', 'anode_material', 'cathode_material',
                  'anode_thickness_um', 'cathode_thickness_um', 'anode_surface_roughness_um',
                  'cathode_surface_roughness_um', 'anode_coating', 'cathode_coating',
                  'welding_technique', 'power_W', 'pulse_energy_J', 'amplitude_um',
                  'clamping_force_N', 'pressure_MPa', 'weld_time_ms', 'welding_speed_mm_s',
                  'pulse_frequency_Hz', 'ultrasonic_frequency_kHz', 'preheat_temperature_C',
                  'ambient_temperature_C', 'ambient_humidity_percent', 'shielding_gas',
                  'cleaning_method']
    
    dataset[input_cols].to_csv('/workspace/welding_dataset_inputs.csv', index=False)
    print("✓ Saved: welding_dataset_inputs.csv")
    
    # Characterization metrics
    char_cols = [col for col in dataset.columns if col not in input_cols and 
                 not any(x in col.lower() for x in ['cycle', 'failure', 'degradation', 
                                                      'reliability', 'mtbf', 'resistance_score',
                                                      'vibration', 'shock', 'corrosion', 'quality_class',
                                                      'performance_score', 'thermal_stress', 'deformation'])]
    char_cols = ['sample_id'] + char_cols
    dataset[char_cols].to_csv('/workspace/welding_dataset_characterization.csv', index=False)
    print("✓ Saved: welding_dataset_characterization.csv")
    
    # Performance metrics
    perf_cols = ['sample_id'] + [col for col in dataset.columns if 
                                  any(x in col.lower() for x in ['cycle', 'failure', 'degradation', 
                                                                  'reliability', 'mtbf', 'resistance_score',
                                                                  'vibration', 'shock', 'corrosion',
                                                                  'quality_class', 'performance_score',
                                                                  'thermal_stress', 'deformation'])]
    dataset[perf_cols].to_csv('/workspace/welding_dataset_performance.csv', index=False)
    print("✓ Saved: welding_dataset_performance.csv")
    
    # Generate and save statistical summary
    print("\nGenerating statistical summary...")
    summary = generator.generate_statistical_summary(dataset)
    summary.to_csv('/workspace/welding_dataset_summary_statistics.csv')
    print("✓ Saved: welding_dataset_summary_statistics.csv")
    
    # Generate data dictionary
    print("\nGenerating data dictionary...")
    data_dict = generate_data_dictionary()
    with open('/workspace/welding_dataset_data_dictionary.txt', 'w') as f:
        f.write(data_dict)
    print("✓ Saved: welding_dataset_data_dictionary.txt")
    
    # Print dataset overview
    print("\n" + "="*80)
    print("DATASET OVERVIEW")
    print("="*80)
    print(f"\nShape: {dataset.shape}")
    print(f"\nColumn Groups:")
    print(f"  - Input Parameters: {len(input_cols)-2}")
    print(f"  - Characterization Metrics: {len(char_cols)-1}")
    print(f"  - Performance Metrics: {len(perf_cols)-1}")
    
    print(f"\nWelding Techniques Distribution:")
    print(dataset['welding_technique'].value_counts())
    
    print(f"\nMaterial Combinations (Top 10):")
    material_combo = dataset['anode_material'] + ' + ' + dataset['cathode_material']
    print(material_combo.value_counts().head(10))
    
    print(f"\nQuality Class Distribution:")
    print(dataset['quality_class'].value_counts())
    
    print(f"\nKey Performance Metrics:")
    print(f"  Cycles to Failure: {dataset['cycles_to_failure'].mean():.0f} ± {dataset['cycles_to_failure'].std():.0f}")
    print(f"  Resistance Degradation: {dataset['resistance_degradation_percent_per_1000cycles'].mean():.2f}% ± {dataset['resistance_degradation_percent_per_1000cycles'].std():.2f}%")
    print(f"  Overall Performance Score: {dataset['overall_performance_score'].mean():.1f} ± {dataset['overall_performance_score'].std():.1f}")
    
    print("\n" + "="*80)
    print("Dataset generation complete!")
    print("="*80)
    print("\nGenerated files:")
    print("  1. welding_dataset_complete.csv - Full dataset")
    print("  2. welding_dataset_inputs.csv - Input parameters only")
    print("  3. welding_dataset_characterization.csv - Characterization metrics")
    print("  4. welding_dataset_performance.csv - Performance metrics")
    print("  5. welding_dataset_summary_statistics.csv - Statistical summary")
    print("  6. welding_dataset_data_dictionary.txt - Feature descriptions")
    print()


def generate_data_dictionary():
    """Generate comprehensive data dictionary."""
    
    return """
================================================================================
WELDING DATASET DATA DICTIONARY
================================================================================

This dataset contains comprehensive data for ML-driven inverse design of
welding parameters with focus on thermal cycling performance.

Total Samples: 5000
Collection Period: 2024-2025 (simulated)

================================================================================
PART 1: INPUT PARAMETERS (Design Space)
================================================================================

SAMPLE IDENTIFICATION
--------------------
sample_id                    : Unique sample identifier (WS_00000 to WS_04999)
collection_date              : Date of data collection

BASE MATERIALS
--------------
anode_material               : Anode material type
                              Values: Copper, Aluminum, Nickel, Steel_304
cathode_material             : Cathode material type
                              Values: Copper, Aluminum, Nickel
anode_thickness_um           : Anode tab thickness [µm]
                              Range: 50-500 µm
cathode_thickness_um         : Cathode tab thickness [µm]
                              Range: 50-500 µm

SURFACE PROPERTIES
------------------
anode_surface_roughness_um   : Anode surface roughness [µm]
                              Lognormal distribution, typical range: 0.5-5 µm
cathode_surface_roughness_um : Cathode surface roughness [µm]
                              Lognormal distribution, typical range: 0.5-5 µm
anode_coating                : Anode surface coating type
                              Values: None, Nickel, Tin, Silver, Oxide
cathode_coating              : Cathode surface coating type
                              Values: None, Nickel, Tin, Silver, Oxide

WELDING PROCESS PARAMETERS
---------------------------
welding_technique            : Welding method used
                              Values: Ultrasonic, Laser, Resistance_Spot, Friction_Stir
power_W                      : Welding power [W]
                              Range: 100-8000 W (depends on technique)
pulse_energy_J               : Laser pulse energy [J] (Laser only)
                              Range: 1-50 J
amplitude_um                 : Ultrasonic amplitude [µm] (Ultrasonic only)
                              Range: 10-60 µm
clamping_force_N             : Clamping force [N]
                              Range: 100-2000 N
pressure_MPa                 : Applied pressure [MPa]
                              Calculated from force and contact area
weld_time_ms                 : Weld duration [ms]
                              Range: 1-5000 ms (depends on technique)
welding_speed_mm_s           : Welding speed [mm/s] (Laser only)
                              Range: 10-200 mm/s
pulse_frequency_Hz           : Laser pulse frequency [Hz] (Laser only)
                              Range: 10-200 Hz
ultrasonic_frequency_kHz     : Ultrasonic frequency [kHz] (Ultrasonic only)
                              Values: 20, 40, 60 kHz

ENVIRONMENTAL CONDITIONS
------------------------
preheat_temperature_C        : Sample pre-heat temperature [°C]
                              Range: 20-150 °C
ambient_temperature_C        : Ambient temperature during welding [°C]
                              Range: 15-35 °C
ambient_humidity_percent     : Ambient relative humidity [%]
                              Range: 20-80%
shielding_gas                : Shielding gas type (mainly for Laser)
                              Values: Argon, Nitrogen, Helium, None

SAMPLE PREPARATION
------------------
cleaning_method              : Surface cleaning method before welding
                              Values: Mechanical, Chemical, Plasma, None

================================================================================
PART 2: CHARACTERIZATION & QUALITY METRICS (Forward Problem Outputs)
================================================================================

THERMAL/ENERGY METRICS
----------------------
heat_input_J_per_mm          : Total heat input per unit length [J/mm]
                              Critical parameter affecting weld quality

GEOMETRIC PROPERTIES
--------------------
weld_nugget_diameter_mm      : Weld nugget diameter [mm]
                              Range: 0.5-15 mm
penetration_depth_mm         : Weld penetration depth [mm]
                              Range: 0.01-0.5 mm
weld_width_mm                : Weld width at surface [mm]
                              Correlated with nugget diameter
bond_area_mm2                : Effective bonding area [mm²]
                              Critical for strength and conductivity

MECHANICAL PROPERTIES
---------------------
tensile_strength_MPa         : Tensile strength of weld joint [MPa]
                              Range: 5-400 MPa
                              Target: >100 MPa for good joints
shear_strength_MPa           : Shear strength of weld joint [MPa]
                              Typically 60-80% of tensile strength
peel_strength_N_per_mm       : Peel strength [N/mm]
                              Range: 1-50 N/mm
weld_hardness_HV             : Weld zone microhardness [HV]
                              Vickers hardness, typically increased vs base
heat_affected_zone_hardness_HV : HAZ microhardness [HV]
                              Typically slightly elevated vs base

ELECTRICAL PROPERTIES
---------------------
contact_resistance_uOhm      : Electrical contact resistance [µΩ]
                              Range: 10-5000 µΩ
                              Target: <100 µΩ for battery applications
weld_resistance_uOhm         : Bulk weld resistance [µΩ]
                              Typically lower than contact resistance
current_capacity_A           : Maximum current carrying capacity [A]
                              Based on cross-sectional area and material

THERMAL PROPERTIES
------------------
weld_thermal_conductivity_W_mK : Weld thermal conductivity [W/m·K]
                              Often lower than base materials
thermal_resistance_K_W       : Thermal resistance across joint [K/W]
                              Critical for heat dissipation

MICROSTRUCTURAL FEATURES
------------------------
average_grain_size_um        : Average grain size in weld zone [µm]
                              Range: 5-200 µm
                              Finer grains typically mean better properties
porosity_percent             : Porosity volume fraction [%]
                              Range: 0-15%
                              Target: <3% for good joints
intermetallic_thickness_um   : Intermetallic compound layer thickness [µm]
                              For dissimilar metal joints
                              Thick layers (>10 µm) can be detrimental
crack_density_per_mm2        : Crack density [cracks/mm²]
                              Range: 0-10
                              Target: <1 for good joints

SURFACE QUALITY
---------------
surface_roughness_after_weld_um : Surface roughness after welding [µm]
                              Typically increased vs pre-weld
weld_spatter_count           : Number of spatter particles
                              More common with laser and resistance welding
oxidation_score              : Surface oxidation/discoloration score
                              Scale: 0-10 (0=no oxidation, 10=severe)

================================================================================
PART 3: PERFORMANCE & VALIDATION METRICS (Inverse Design Targets)
================================================================================

THERMAL CYCLING TEST CONDITIONS
--------------------------------
thermal_cycle_min_temp_C     : Minimum temperature in cycle [°C]
                              Range: -55 to -40 °C
thermal_cycle_max_temp_C     : Maximum temperature in cycle [°C]
                              Range: 85 to 150 °C
thermal_cycle_rate_C_per_min : Heating/cooling rate [°C/min]
                              Range: 5-20 °C/min
thermal_cycle_dwell_time_min : Dwell time at extreme temperatures [min]
                              Range: 10-30 min
thermal_stress_MPa           : Calculated thermal stress [MPa]
                              Due to CTE mismatch

FATIGUE & LIFE METRICS
----------------------
cycles_to_failure            : Number of thermal cycles to failure
                              Range: 10-100,000 cycles
                              PRIMARY TARGET METRIC
                              Excellent: >10,000
                              Good: >5,000
                              Acceptable: >1,000
                              Poor: <1,000

DEGRADATION METRICS
-------------------
resistance_degradation_percent_per_1000cycles :
                              Resistance increase rate [%/1000 cycles]
                              Typical: 5-20%
                              Target: <5% for excellent performance
resistance_after_50pct_life_uOhm :
                              Contact resistance at 50% of life [µΩ]
strength_degradation_percent_per_1000cycles :
                              Strength decrease rate [%/1000 cycles]
                              Typically slower than resistance degradation
tensile_strength_after_50pct_life_MPa :
                              Tensile strength at 50% of life [MPa]

FAILURE ANALYSIS
----------------
primary_failure_mode         : Dominant failure mechanism
                              1: Interfacial (poor bonding)
                              2: Ductile (base metal - GOOD)
                              3: Brittle (intermetallic/grain boundary)
                              4: Fatigue crack propagation
                              5: Delamination
crack_propagation_rate_um_per_cycle :
                              Crack growth rate [µm/cycle]
                              Range: 0.0001-1 µm/cycle
permanent_deformation_um     : Permanent warpage after cycling [µm]
                              Range: 0-100 µm

ELECTRICAL PERFORMANCE DEGRADATION
-----------------------------------
power_dissipation_increase_percent :
                              Increase in I²R losses [%]
                              Directly related to resistance increase
voltage_drop_increase_mV     : Additional voltage drop at rated current [mV]
                              Critical for battery applications

THERMAL PERFORMANCE DEGRADATION
--------------------------------
thermal_resistance_increase_percent :
                              Increase in thermal resistance [%]
                              Due to interface degradation
max_operating_temp_C         : Maximum safe operating temperature [°C]
                              Based on materials and weld quality

LONG-TERM RELIABILITY
---------------------
MTBF_hours                   : Mean time between failures [hours]
                              At rated operating conditions
reliability_10years_percent  : Reliability after 10 years [%]
                              Using exponential reliability model

ENVIRONMENTAL RESISTANCE
------------------------
corrosion_resistance_score   : Corrosion resistance rating
                              Scale: 0-10 (10=excellent)
vibration_resistance_score   : Vibration resistance rating
                              Scale: 0-10 (10=excellent)
shock_resistance_score       : Mechanical shock resistance rating
                              Scale: 0-10 (10=excellent)

OVERALL QUALITY METRICS
-----------------------
quality_class                : Overall quality classification
                              Excellent: >10k cycles, <5% degradation
                              Good: >5k cycles, <10% degradation
                              Acceptable: >1k cycles, <20% degradation
                              Poor: Otherwise
overall_performance_score    : Composite performance score
                              Range: 0-100
                              Weighted combination of:
                                - Cycles to failure (0-50 pts)
                                - Resistance degradation (0-25 pts)
                                - Long-term reliability (0-25 pts)

================================================================================
KEY RELATIONSHIPS & PHYSICS
================================================================================

1. HEAT INPUT EFFECTS:
   - Optimal heat input (~50 J/mm) maximizes strength
   - Too low: incomplete bonding, high porosity
   - Too high: excessive melting, coarse grains, cracking

2. MATERIAL COMPATIBILITY:
   - Similar metals (Cu-Cu, Al-Al): easier to weld, longer life
   - Dissimilar metals: form intermetallics, reduced thermal cycling life
   - CTE mismatch drives thermal stress: σ = ΔT × ΔCTE × E

3. COATING EFFECTS:
   - Nickel, Silver: improve strength and reduce resistance
   - Tin: reduces resistance but may reduce strength
   - Oxide: increases resistance and porosity (undesirable)

4. DEFECT IMPACTS:
   - Porosity >3%: significantly reduces strength and life
   - Cracks: accelerate fatigue failure
   - Thick intermetallics (>10 µm): brittle, crack easily

5. THERMAL CYCLING DEGRADATION:
   - Resistance typically increases 5-20% per 1000 cycles
   - Strength degrades slower than resistance
   - Failure driven by: thermal stress, defects, intermetallics

6. PRESSURE EFFECTS:
   - Optimal pressure (~50 MPa) for ultrasonic welding
   - Too low: poor bonding
   - Too high: material thinning, inconsistent properties

================================================================================
USAGE RECOMMENDATIONS
================================================================================

FOR INVERSE DESIGN:
1. Target Metrics (outputs):
   - cycles_to_failure > 10,000
   - resistance_degradation_percent_per_1000cycles < 5
   - overall_performance_score > 75

2. Critical Input Parameters:
   - Material selection (similar metals preferred)
   - Heat input control (aim for ~50 J/mm)
   - Surface preparation (clean, smooth surfaces)
   - Coating selection (Nickel or Silver for best results)

3. Process Optimization:
   - Ultrasonic welding: good for thin, similar metals
   - Laser welding: precise control, good for small features
   - Resistance spot: high production rate

FOR MACHINE LEARNING:
1. Feature Engineering:
   - Create material compatibility features
   - Add thermal property ratios
   - Include process control quality indicators

2. Model Selection:
   - Regression for continuous targets (cycles, degradation rates)
   - Classification for quality classes
   - Multi-output models for simultaneous prediction

3. Validation:
   - Stratify by welding technique and material combination
   - Consider physics-based constraints in predictions
   - Use domain knowledge for feature importance

================================================================================
DATASET LIMITATIONS
================================================================================

1. This is a synthetic dataset based on physics-based models
2. Real-world data will have additional sources of variability
3. Some simplifications in material interactions
4. Does not include all possible failure modes
5. Statistical noise added to simulate measurement uncertainty

================================================================================
REFERENCES & STANDARDS
================================================================================

Relevant Standards:
- IEC 62281: Battery safety
- ISO 14731: Welding quality requirements
- SAE J2929: Battery safety evaluation
- MIL-STD-202G: Environmental testing

Material Properties:
- ASM Handbook: Materials properties database
- Various journal articles on dissimilar metal welding

================================================================================
END OF DATA DICTIONARY
================================================================================
"""


if __name__ == "__main__":
    main()
