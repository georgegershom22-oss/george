#!/usr/bin/env python3
"""
Comprehensive Dataset Generator for ML-Driven Inverse Design of Welding Parameters
================================================================================

This script generates a realistic, physics-informed dataset for welding parameter optimization
with focus on extreme temperature cycling performance. The dataset includes:

1. Input Parameters (Design Space): Controllable welding process variables
2. Characterization Metrics (Forward Problem): Immediate post-weld quality measurements  
3. Performance Metrics (Inverse Design Targets): Long-term thermal cycling performance

The data generation incorporates realistic material properties, process physics,
and failure mechanisms to enable effective ML model training.
"""

import numpy as np
import pandas as pd
import json
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

# Set random seeds for reproducibility
np.random.seed(42)
random.seed(42)

@dataclass
class MaterialProperties:
    """Material property definitions for realistic data generation"""
    name: str
    thermal_conductivity: float  # W/m·K
    electrical_conductivity: float  # S/m
    thermal_expansion: float  # 1/K
    yield_strength: float  # MPa
    melting_point: float  # K
    density: float  # kg/m³
    specific_heat: float  # J/kg·K
    contact_resistance: float  # Ω·m²

# Material database
MATERIALS = {
    'copper': MaterialProperties(
        name='Copper',
        thermal_conductivity=400,
        electrical_conductivity=5.8e7,
        thermal_expansion=16.5e-6,
        yield_strength=200,
        melting_point=1357,
        density=8960,
        specific_heat=385,
        contact_resistance=1e-8
    ),
    'aluminum': MaterialProperties(
        name='Aluminum',
        thermal_conductivity=237,
        electrical_conductivity=3.5e7,
        thermal_expansion=23.1e-6,
        yield_strength=95,
        melting_point=933,
        density=2700,
        specific_heat=900,
        contact_resistance=2e-8
    ),
    'nickel': MaterialProperties(
        name='Nickel',
        thermal_conductivity=91,
        electrical_conductivity=1.4e7,
        thermal_expansion=13.4e-6,
        yield_strength=200,
        melting_point=1728,
        density=8900,
        specific_heat=444,
        contact_resistance=5e-8
    ),
    'titanium': MaterialProperties(
        name='Titanium',
        thermal_conductivity=22,
        electrical_conductivity=2.4e6,
        thermal_expansion=8.6e-6,
        yield_strength=880,
        melting_point=1941,
        density=4500,
        specific_heat=523,
        contact_resistance=1e-7
    )
}

class WeldingDatasetGenerator:
    """Main class for generating comprehensive welding datasets"""
    
    def __init__(self, n_samples: int = 10000):
        self.n_samples = n_samples
        self.materials = list(MATERIALS.keys())
        self.welding_techniques = ['USW', 'Laser', 'Resistance_Spot', 'Friction_Stir']
        self.surface_finishes = ['Polished', 'Rough', 'Anodized', 'Coated', 'Oxidized']
        
    def generate_input_parameters(self) -> pd.DataFrame:
        """Generate Part 1: Input Parameters (Design Space)"""
        print("Generating input parameters...")
        
        data = []
        
        for i in range(self.n_samples):
            # Base Materials
            anode_material = np.random.choice(self.materials)
            cathode_material = np.random.choice(self.materials)
            
            # Ensure different materials for most samples (realistic scenario)
            if np.random.random() < 0.8:
                while cathode_material == anode_material:
                    cathode_material = np.random.choice(self.materials)
            
            # Tab thickness (critical for heat dissipation)
            tab_thickness = np.random.lognormal(mean=np.log(100), sigma=0.3)  # µm
            
            # Surface finish
            surface_finish = np.random.choice(self.surface_finishes)
            
            # Welding technique
            welding_technique = np.random.choice(self.welding_techniques)
            
            # Technique-specific parameters
            if welding_technique == 'USW':
                power = np.random.uniform(500, 3000)  # W
                amplitude = np.random.uniform(10, 100)  # µm
                force = np.random.uniform(100, 2000)  # N
                time = np.random.uniform(0.1, 2.0)  # s
                speed = np.nan  # Not applicable
                pulse_frequency = np.nan  # Not applicable
                
            elif welding_technique == 'Laser':
                power = np.random.uniform(100, 2000)  # W
                amplitude = np.nan  # Not applicable
                force = np.random.uniform(10, 500)  # N (clamping force)
                time = np.random.uniform(0.001, 0.1)  # s
                speed = np.random.uniform(1, 50)  # mm/s
                pulse_frequency = np.random.uniform(1, 1000)  # Hz
                
            elif welding_technique == 'Resistance_Spot':
                power = np.random.uniform(1000, 10000)  # W
                amplitude = np.nan  # Not applicable
                force = np.random.uniform(500, 5000)  # N
                time = np.random.uniform(0.01, 1.0)  # s
                speed = np.nan  # Not applicable
                pulse_frequency = np.nan  # Not applicable
                
            else:  # Friction_Stir
                power = np.random.uniform(2000, 15000)  # W
                amplitude = np.nan  # Not applicable
                force = np.random.uniform(1000, 10000)  # N
                time = np.random.uniform(1, 30)  # s
                speed = np.random.uniform(10, 200)  # mm/s
                pulse_frequency = np.nan  # Not applicable
            
            # Environmental conditions
            preheat_temp = np.random.uniform(20, 200)  # °C
            
            # Additional process parameters
            weld_angle = np.random.uniform(0, 45)  # degrees
            overlap_ratio = np.random.uniform(0.1, 0.9)  # ratio
            atmosphere = np.random.choice(['Air', 'Argon', 'Nitrogen', 'Vacuum'])
            
            data.append({
                'sample_id': f'WS_{i:06d}',
                'anode_material': anode_material,
                'cathode_material': cathode_material,
                'tab_thickness_um': tab_thickness,
                'surface_finish': surface_finish,
                'welding_technique': welding_technique,
                'power_w': power,
                'amplitude_um': amplitude,
                'force_n': force,
                'time_s': time,
                'speed_mm_s': speed,
                'pulse_frequency_hz': pulse_frequency,
                'preheat_temp_c': preheat_temp,
                'weld_angle_deg': weld_angle,
                'overlap_ratio': overlap_ratio,
                'atmosphere': atmosphere
            })
        
        return pd.DataFrame(data)
    
    def calculate_characterization_metrics(self, input_df: pd.DataFrame) -> pd.DataFrame:
        """Generate Part 2: Characterization & Quality Metrics (Forward Problem)"""
        print("Calculating characterization metrics...")
        
        char_data = []
        
        for _, row in input_df.iterrows():
            # Get material properties
            anode_props = MATERIALS[row['anode_material']]
            cathode_props = MATERIALS[row['cathode_material']]
            
            # Calculate thermal properties
            avg_thermal_cond = (anode_props.thermal_conductivity + cathode_props.thermal_conductivity) / 2
            avg_electrical_cond = (anode_props.electrical_conductivity + cathode_props.electrical_conductivity) / 2
            
            # Weld strength (depends on materials, force, time)
            base_strength = min(anode_props.yield_strength, cathode_props.yield_strength)
            force_factor = min(row['force_n'] / 1000, 2.0)  # Normalize force
            time_factor = min(row['time_s'] * 10, 2.0)  # Normalize time
            
            # Add technique-specific effects
            if row['welding_technique'] == 'USW':
                technique_factor = 1.2  # USW generally good for dissimilar materials
            elif row['welding_technique'] == 'Laser':
                technique_factor = 1.0  # Good control
            elif row['welding_technique'] == 'Resistance_Spot':
                technique_factor = 0.8  # Can cause material degradation
            else:  # Friction_Stir
                technique_factor = 1.1  # Good for dissimilar materials
            
            weld_strength = base_strength * force_factor * time_factor * technique_factor
            weld_strength += np.random.normal(0, weld_strength * 0.1)  # Add noise
            
            # Contact resistance (depends on materials, surface finish, force)
            base_resistance = (anode_props.contact_resistance + cathode_props.contact_resistance) / 2
            
            # Surface finish effects
            finish_factors = {
                'Polished': 0.5,
                'Rough': 2.0,
                'Anodized': 3.0,
                'Coated': 1.5,
                'Oxidized': 4.0
            }
            
            contact_resistance = base_resistance * finish_factors[row['surface_finish']]
            contact_resistance /= (force_factor ** 0.5)  # Higher force reduces resistance
            contact_resistance += np.random.normal(0, contact_resistance * 0.2)
            
            # Weld width and penetration (depends on power, time, technique)
            if row['welding_technique'] == 'Laser':
                weld_width = np.sqrt(row['power_w'] * row['time_s'] / 1000) * np.random.uniform(0.8, 1.2)
                penetration = weld_width * np.random.uniform(0.3, 0.8)
            else:
                weld_width = np.sqrt(row['power_w'] * row['time_s'] / 500) * np.random.uniform(0.6, 1.4)
                penetration = weld_width * np.random.uniform(0.2, 0.6)
            
            # Porosity (defect indicator)
            porosity_base = 0.01  # 1% base porosity
            if row['atmosphere'] == 'Vacuum':
                porosity_base *= 0.1
            elif row['atmosphere'] == 'Argon':
                porosity_base *= 0.3
            elif row['atmosphere'] == 'Nitrogen':
                porosity_base *= 0.7
            
            # Higher power/time can increase porosity
            porosity = porosity_base * (1 + row['power_w'] / 5000) * (1 + row['time_s'] / 2)
            porosity += np.random.normal(0, porosity * 0.3)
            porosity = max(0, min(porosity, 0.2))  # Clamp between 0-20%
            
            # Microhardness (depends on materials, cooling rate)
            base_hardness = (anode_props.yield_strength + cathode_props.yield_strength) / 2
            cooling_rate = row['power_w'] / (row['time_s'] + 0.1)  # Approximate cooling rate
            hardness_factor = 1 + cooling_rate / 10000  # Faster cooling = harder
            microhardness = base_hardness * hardness_factor * np.random.uniform(0.8, 1.2)
            
            # Heat affected zone (HAZ) width
            haz_width = np.sqrt(row['power_w'] * row['time_s'] / 2000) * np.random.uniform(0.5, 1.5)
            
            # Intermetallic formation (for dissimilar materials)
            if row['anode_material'] != row['cathode_material']:
                intermetallic_thickness = np.sqrt(row['power_w'] * row['time_s'] / 10000) * np.random.uniform(0.1, 2.0)
            else:
                intermetallic_thickness = 0.0
            
            char_data.append({
                'sample_id': row['sample_id'],
                'weld_strength_mpa': max(0, weld_strength),
                'contact_resistance_ohm_m2': max(1e-10, contact_resistance),
                'weld_width_mm': max(0.1, weld_width),
                'penetration_mm': max(0.05, penetration),
                'porosity_percent': porosity * 100,
                'microhardness_hv': max(50, microhardness),
                'haz_width_mm': max(0.1, haz_width),
                'intermetallic_thickness_um': max(0, intermetallic_thickness),
                'weld_quality_score': self._calculate_quality_score(weld_strength, contact_resistance, porosity)
            })
        
        return pd.DataFrame(char_data)
    
    def _calculate_quality_score(self, strength: float, resistance: float, porosity: float) -> float:
        """Calculate overall weld quality score (0-100)"""
        # Normalize strength (0-100 scale)
        strength_score = min(100, max(0, (strength / 500) * 100))
        
        # Normalize resistance (lower is better, 0-100 scale)
        resistance_score = min(100, max(0, 100 - (resistance / 1e-6) * 10))
        
        # Normalize porosity (lower is better, 0-100 scale)
        porosity_score = min(100, max(0, 100 - porosity * 500))
        
        # Weighted average
        return (strength_score * 0.4 + resistance_score * 0.3 + porosity_score * 0.3)
    
    def calculate_performance_metrics(self, input_df: pd.DataFrame, char_df: pd.DataFrame) -> pd.DataFrame:
        """Generate Part 3: Performance & Validation Metrics (Inverse Design Targets)"""
        print("Calculating performance metrics...")
        
        perf_data = []
        
        for _, (input_row, char_row) in enumerate(zip(input_df.iterrows(), char_df.iterrows())):
            input_row = input_row[1]  # Get the Series from tuple
            char_row = char_row[1]
            
            # Get material properties
            anode_props = MATERIALS[input_row['anode_material']]
            cathode_props = MATERIALS[input_row['cathode_material']]
            
            # Thermal cycling performance (primary target)
            # Based on thermal expansion mismatch, contact resistance, and weld quality
            
            # Thermal expansion mismatch
            expansion_diff = abs(anode_props.thermal_expansion - cathode_props.thermal_expansion)
            
            # Base cycling life (number of cycles before failure)
            base_life = 10000  # Base cycles
            
            # Factors affecting thermal cycling life
            strength_factor = char_row['weld_strength_mpa'] / 200  # Normalize to typical strength
            resistance_factor = 1 / (1 + char_row['contact_resistance_ohm_m2'] / 1e-8)  # Lower resistance = better
            porosity_factor = 1 - char_row['porosity_percent'] / 100  # Lower porosity = better
            expansion_factor = 1 / (1 + expansion_diff * 1e6)  # Lower mismatch = better
            
            # Technique-specific factors
            if input_row['welding_technique'] == 'USW':
                technique_factor = 1.2  # Good for thermal cycling
            elif input_row['welding_technique'] == 'Laser':
                technique_factor = 1.0  # Good control
            elif input_row['welding_technique'] == 'Resistance_Spot':
                technique_factor = 0.7  # Can cause stress concentrations
            else:  # Friction_Stir
                technique_factor = 1.1  # Good for dissimilar materials
            
            # Calculate thermal cycling life
            thermal_cycles = base_life * strength_factor * resistance_factor * porosity_factor * expansion_factor * technique_factor
            thermal_cycles += np.random.normal(0, thermal_cycles * 0.2)  # Add noise
            thermal_cycles = max(100, thermal_cycles)  # Minimum 100 cycles
            
            # Temperature range capability
            # Based on material melting points and weld quality
            min_melting = min(anode_props.melting_point, cathode_props.melting_point)
            max_temp = min_melting * 0.6  # 60% of melting point for safety
            max_temp *= (1 + char_row['weld_quality_score'] / 1000)  # Better quality = higher temp capability
            max_temp += np.random.normal(0, max_temp * 0.05)
            
            # Electrical resistance degradation rate
            # How much resistance increases per thermal cycle
            base_degradation = 1e-12  # Base degradation rate
            degradation = base_degradation * (1 + expansion_diff * 1e6) * (1 + char_row['porosity_percent'] / 10)
            degradation = max(1e-15, degradation)  # Ensure positive before adding noise
            degradation += np.random.normal(0, abs(degradation) * 0.3)
            degradation = max(1e-15, degradation)
            
            # Mechanical strength retention
            # How much strength is retained after thermal cycling
            base_retention = 0.95  # 95% base retention
            retention = base_retention * (1 - char_row['porosity_percent'] / 200) * (1 - expansion_diff * 1e6 / 10)
            retention = max(0.5, min(1.0, retention))  # Clamp between 50-100%
            retention += np.random.normal(0, abs(retention) * 0.05)  # Use absolute value for scale
            retention = max(0.5, min(1.0, retention))  # Clamp again after noise
            
            # Failure mode prediction
            if expansion_diff > 5e-6:  # High thermal mismatch
                failure_mode = 'Thermal_Fatigue'
            elif char_row['porosity_percent'] > 5:  # High porosity
                failure_mode = 'Crack_Propagation'
            elif char_row['contact_resistance_ohm_m2'] > 1e-6:  # High resistance
                failure_mode = 'Electrical_Overheating'
            else:
                failure_mode = 'General_Degradation'
            
            # Thermal conductivity of joint
            # Affects heat dissipation during cycling
            joint_conductivity = (anode_props.thermal_conductivity + cathode_props.thermal_conductivity) / 2
            joint_conductivity *= (1 - char_row['porosity_percent'] / 100)  # Porosity reduces conductivity
            joint_conductivity *= (1 - char_row['intermetallic_thickness_um'] / 1000)  # Intermetallics reduce conductivity
            
            # Stress concentration factor
            # Based on weld geometry and defects
            stress_concentration = 1.0  # Base factor
            stress_concentration += char_row['porosity_percent'] / 50  # Porosity increases stress
            stress_concentration += char_row['haz_width_mm'] / 10  # Larger HAZ increases stress
            stress_concentration += abs(input_row['weld_angle_deg'] - 0) / 100  # Angle increases stress
            
            perf_data.append({
                'sample_id': input_row['sample_id'],
                'thermal_cycles_to_failure': int(thermal_cycles),
                'max_operating_temp_c': max_temp - 273.15,  # Convert to Celsius
                'resistance_degradation_rate': degradation,
                'strength_retention_percent': retention * 100,
                'failure_mode': failure_mode,
                'joint_thermal_conductivity': joint_conductivity,
                'stress_concentration_factor': stress_concentration,
                'thermal_fatigue_life': thermal_cycles * np.random.uniform(0.8, 1.2),
                'electrical_stability_score': self._calculate_electrical_stability(char_row, input_row),
                'thermal_stability_score': self._calculate_thermal_stability(char_row, input_row, anode_props, cathode_props)
            })
        
        return pd.DataFrame(perf_data)
    
    def _calculate_electrical_stability(self, char_row, input_row) -> float:
        """Calculate electrical stability score (0-100)"""
        # Based on contact resistance, porosity, and material compatibility
        resistance_score = max(0, 100 - (char_row['contact_resistance_ohm_m2'] / 1e-8) * 10)
        porosity_score = max(0, 100 - char_row['porosity_percent'] * 10)
        
        # Material compatibility
        anode_props = MATERIALS[input_row['anode_material']]
        cathode_props = MATERIALS[input_row['cathode_material']]
        conductivity_diff = abs(anode_props.electrical_conductivity - cathode_props.electrical_conductivity)
        compatibility_score = max(0, 100 - (conductivity_diff / 1e7) * 5)
        
        return (resistance_score * 0.4 + porosity_score * 0.3 + compatibility_score * 0.3)
    
    def _calculate_thermal_stability(self, char_row, input_row, anode_props, cathode_props) -> float:
        """Calculate thermal stability score (0-100)"""
        # Based on thermal expansion mismatch, joint conductivity, and weld quality
        expansion_diff = abs(anode_props.thermal_expansion - cathode_props.thermal_expansion)
        expansion_score = max(0, 100 - expansion_diff * 1e6 * 2)
        
        # Calculate joint conductivity from material properties
        joint_conductivity = (anode_props.thermal_conductivity + cathode_props.thermal_conductivity) / 2
        conductivity_score = min(100, (joint_conductivity / 300) * 100)
        quality_score = char_row['weld_quality_score']
        
        return (expansion_score * 0.4 + conductivity_score * 0.3 + quality_score * 0.3)
    
    def generate_complete_dataset(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Generate the complete three-part dataset"""
        print(f"Generating comprehensive welding dataset with {self.n_samples} samples...")
        
        # Generate all three parts
        input_df = self.generate_input_parameters()
        char_df = self.calculate_characterization_metrics(input_df)
        perf_df = self.calculate_performance_metrics(input_df, char_df)
        
        # Add some derived features
        input_df = self._add_derived_features(input_df)
        
        print(f"Dataset generation complete!")
        print(f"Input parameters: {input_df.shape}")
        print(f"Characterization metrics: {char_df.shape}")
        print(f"Performance metrics: {perf_df.shape}")
        
        return input_df, char_df, perf_df
    
    def _add_derived_features(self, input_df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features that might be useful for ML models"""
        # Material compatibility score
        input_df['material_compatibility'] = input_df.apply(
            lambda row: self._calculate_material_compatibility(row['anode_material'], row['cathode_material']), 
            axis=1
        )
        
        # Process intensity (power * time)
        input_df['process_intensity'] = input_df['power_w'] * input_df['time_s']
        
        # Energy density (power / area approximation)
        input_df['energy_density'] = input_df['power_w'] / (input_df['tab_thickness_um'] / 1000) ** 2
        
        # Thermal mass (thickness * density * specific heat)
        input_df['thermal_mass_anode'] = input_df.apply(
            lambda row: row['tab_thickness_um'] * MATERIALS[row['anode_material']].density * MATERIALS[row['anode_material']].specific_heat,
            axis=1
        )
        
        return input_df
    
    def _calculate_material_compatibility(self, anode: str, cathode: str) -> float:
        """Calculate material compatibility score (0-100)"""
        anode_props = MATERIALS[anode]
        cathode_props = MATERIALS[cathode]
        
        # Thermal expansion mismatch
        expansion_diff = abs(anode_props.thermal_expansion - cathode_props.thermal_expansion)
        expansion_score = max(0, 100 - expansion_diff * 1e6 * 2)
        
        # Melting point compatibility
        mp_diff = abs(anode_props.melting_point - cathode_props.melting_point)
        mp_score = max(0, 100 - mp_diff / 100)
        
        # Electrical conductivity compatibility
        cond_diff = abs(anode_props.electrical_conductivity - cathode_props.electrical_conductivity)
        cond_score = max(0, 100 - cond_diff / 1e7 * 2)
        
        return (expansion_score * 0.5 + mp_score * 0.3 + cond_score * 0.2)
    
    def save_dataset(self, input_df: pd.DataFrame, char_df: pd.DataFrame, perf_df: pd.DataFrame, 
                    base_filename: str = "welding_dataset"):
        """Save dataset in multiple formats"""
        print("Saving dataset...")
        
        # Save as CSV
        input_df.to_csv(f"{base_filename}_input_parameters.csv", index=False)
        char_df.to_csv(f"{base_filename}_characterization_metrics.csv", index=False)
        perf_df.to_csv(f"{base_filename}_performance_metrics.csv", index=False)
        
        # Save combined dataset
        combined_df = input_df.merge(char_df, on='sample_id').merge(perf_df, on='sample_id')
        combined_df.to_csv(f"{base_filename}_combined.csv", index=False)
        
        # Save as Parquet (more efficient)
        input_df.to_parquet(f"{base_filename}_input_parameters.parquet", index=False)
        char_df.to_parquet(f"{base_filename}_characterization_metrics.parquet", index=False)
        perf_df.to_parquet(f"{base_filename}_performance_metrics.parquet", index=False)
        combined_df.to_parquet(f"{base_filename}_combined.parquet", index=False)
        
        # Save metadata
        metadata = {
            'dataset_info': {
                'total_samples': len(input_df),
                'input_parameters': list(input_df.columns),
                'characterization_metrics': list(char_df.columns),
                'performance_metrics': list(perf_df.columns),
                'materials': list(MATERIALS.keys()),
                'welding_techniques': self.welding_techniques,
                'surface_finishes': self.surface_finishes
            },
            'material_properties': {k: {
                'name': v.name,
                'thermal_conductivity': v.thermal_conductivity,
                'electrical_conductivity': v.electrical_conductivity,
                'thermal_expansion': v.thermal_expansion,
                'yield_strength': v.yield_strength,
                'melting_point': v.melting_point,
                'density': v.density,
                'specific_heat': v.specific_heat,
                'contact_resistance': v.contact_resistance
            } for k, v in MATERIALS.items()}
        }
        
        with open(f"{base_filename}_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Dataset saved with base filename: {base_filename}")
        return combined_df

def main():
    """Main function to generate and save the dataset"""
    print("=" * 80)
    print("ML-Driven Inverse Design of Welding Parameters - Dataset Generator")
    print("=" * 80)
    
    # Generate dataset
    generator = WeldingDatasetGenerator(n_samples=15000)  # Large dataset
    input_df, char_df, perf_df = generator.generate_complete_dataset()
    
    # Save dataset
    combined_df = generator.save_dataset(input_df, char_df, perf_df, "welding_ml_dataset")
    
    # Print summary statistics
    print("\n" + "=" * 80)
    print("DATASET SUMMARY")
    print("=" * 80)
    
    print(f"\nInput Parameters ({input_df.shape[0]} samples, {input_df.shape[1]} features):")
    print(f"- Materials: {input_df['anode_material'].nunique()} anode, {input_df['cathode_material'].nunique()} cathode")
    print(f"- Techniques: {input_df['welding_technique'].value_counts().to_dict()}")
    print(f"- Power range: {input_df['power_w'].min():.1f} - {input_df['power_w'].max():.1f} W")
    print(f"- Time range: {input_df['time_s'].min():.3f} - {input_df['time_s'].max():.3f} s")
    
    print(f"\nCharacterization Metrics ({char_df.shape[0]} samples, {char_df.shape[1]} features):")
    print(f"- Weld strength: {char_df['weld_strength_mpa'].min():.1f} - {char_df['weld_strength_mpa'].max():.1f} MPa")
    print(f"- Contact resistance: {char_df['contact_resistance_ohm_m2'].min():.2e} - {char_df['contact_resistance_ohm_m2'].max():.2e} Ω·m²")
    print(f"- Porosity: {char_df['porosity_percent'].min():.2f} - {char_df['porosity_percent'].max():.2f} %")
    print(f"- Quality score: {char_df['weld_quality_score'].min():.1f} - {char_df['weld_quality_score'].max():.1f}")
    
    print(f"\nPerformance Metrics ({perf_df.shape[0]} samples, {perf_df.shape[1]} features):")
    print(f"- Thermal cycles: {perf_df['thermal_cycles_to_failure'].min()} - {perf_df['thermal_cycles_to_failure'].max()}")
    print(f"- Max temperature: {perf_df['max_operating_temp_c'].min():.1f} - {perf_df['max_operating_temp_c'].max():.1f} °C")
    print(f"- Strength retention: {perf_df['strength_retention_percent'].min():.1f} - {perf_df['strength_retention_percent'].max():.1f} %")
    print(f"- Failure modes: {perf_df['failure_mode'].value_counts().to_dict()}")
    
    print(f"\nFiles generated:")
    print("- welding_ml_dataset_input_parameters.csv/parquet")
    print("- welding_ml_dataset_characterization_metrics.csv/parquet") 
    print("- welding_ml_dataset_performance_metrics.csv/parquet")
    print("- welding_ml_dataset_combined.csv/parquet")
    print("- welding_ml_dataset_metadata.json")
    
    print("\n" + "=" * 80)
    print("Dataset generation complete! Ready for ML model training.")
    print("=" * 80)

if __name__ == "__main__":
    main()