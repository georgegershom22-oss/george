#!/usr/bin/env python3
"""
Comprehensive Dataset Generator for ML-Driven Inverse Design of Welding Parameters

This module generates a realistic dataset for welding parameter optimization,
covering input parameters, characterization metrics, and performance validation.
"""

import numpy as np
import pandas as pd
import json
import h5py
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy.stats import norm, uniform, beta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class MaterialProperties:
    """Material properties for welding simulation"""
    name: str
    thermal_conductivity: float  # W/m·K
    electrical_conductivity: float  # S/m
    melting_point: float  # °C
    density: float  # kg/m³
    specific_heat: float  # J/kg·K
    thermal_expansion: float  # 1/K
    yield_strength: float  # MPa
    ultimate_strength: float  # MPa

class WeldingDatasetGenerator:
    """Main class for generating comprehensive welding datasets"""
    
    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        np.random.seed(random_seed)
        
        # Define material properties
        self.materials = {
            'Copper': MaterialProperties(
                name='Copper', thermal_conductivity=400, electrical_conductivity=5.96e7,
                melting_point=1085, density=8960, specific_heat=385, 
                thermal_expansion=16.5e-6, yield_strength=33, ultimate_strength=210
            ),
            'Aluminum': MaterialProperties(
                name='Aluminum', thermal_conductivity=237, electrical_conductivity=3.77e7,
                melting_point=660, density=2700, specific_heat=900,
                thermal_expansion=23.1e-6, yield_strength=95, ultimate_strength=186
            ),
            'Steel': MaterialProperties(
                name='Steel', thermal_conductivity=50, electrical_conductivity=7.0e6,
                melting_point=1538, density=7850, specific_heat=460,
                thermal_expansion=12.0e-6, yield_strength=250, ultimate_strength=400
            ),
            'Nickel': MaterialProperties(
                name='Nickel', thermal_conductivity=90, electrical_conductivity=1.43e7,
                melting_point=1455, density=8900, specific_heat=444,
                thermal_expansion=13.4e-6, yield_strength=103, ultimate_strength=317
            ),
            'Titanium': MaterialProperties(
                name='Titanium', thermal_conductivity=22, electrical_conductivity=2.38e6,
                melting_point=1668, density=4500, specific_heat=523,
                thermal_expansion=8.6e-6, yield_strength=880, ultimate_strength=950
            )
        }
        
        # Welding techniques and their parameter ranges
        self.welding_techniques = {
            'Ultrasonic_Welding': {
                'power_range': (50, 2000),  # W
                'amplitude_range': (10, 100),  # µm
                'force_range': (50, 2000),  # N
                'time_range': (0.1, 2.0),  # s
                'frequency': 20000  # Hz
            },
            'Laser_Welding': {
                'power_range': (100, 5000),  # W
                'speed_range': (1, 50),  # mm/s
                'pulse_frequency_range': (1, 1000),  # Hz
                'pulse_duration_range': (0.1, 20),  # ms
                'spot_size_range': (0.1, 2.0)  # mm
            },
            'Resistance_Spot_Welding': {
                'current_range': (1000, 10000),  # A
                'voltage_range': (1, 10),  # V
                'time_range': (0.01, 1.0),  # s
                'force_range': (100, 5000)  # N
            },
            'Friction_Stir_Welding': {
                'rotation_speed_range': (100, 2000),  # RPM
                'travel_speed_range': (0.5, 20),  # mm/s
                'force_range': (1000, 20000),  # N
                'tool_diameter_range': (3, 20)  # mm
            }
        }
        
        # Surface finish options
        self.surface_finishes = [
            'As_received', 'Polished', 'Rough', 'Oxidized', 'Coated_Zn', 
            'Coated_Ni', 'Anodized', 'Etched', 'Cleaned_Acetone', 'Cleaned_Alcohol'
        ]
        
        # Coating types
        self.coatings = [
            'None', 'Zinc', 'Nickel', 'Tin', 'Silver', 'Gold', 'Aluminum_Oxide', 
            'Titanium_Nitride', 'Diamond_Like_Carbon', 'Polymer'
        ]

    def generate_input_parameters(self, n_samples: int = 10000) -> pd.DataFrame:
        """Generate input parameters (Part 1 of the dataset)"""
        print(f"Generating {n_samples} input parameter samples...")
        
        data = []
        
        for i in range(n_samples):
            # Base materials selection
            anode_material = np.random.choice(list(self.materials.keys()))
            cathode_material = np.random.choice(list(self.materials.keys()))
            
            # Ensure different materials for anode and cathode
            while cathode_material == anode_material:
                cathode_material = np.random.choice(list(self.materials.keys()))
            
            # Tab thickness (µm) - realistic range for battery applications
            tab_thickness = np.random.uniform(50, 500)
            
            # Surface finish and coating
            surface_finish = np.random.choice(self.surface_finishes)
            coating = np.random.choice(self.coatings)
            
            # Welding technique selection
            technique = np.random.choice(list(self.welding_techniques.keys()))
            technique_params = self.welding_techniques[technique]
            
            # Generate technique-specific parameters
            if technique == 'Ultrasonic_Welding':
                power = np.random.uniform(*technique_params['power_range'])
                amplitude = np.random.uniform(*technique_params['amplitude_range'])
                force = np.random.uniform(*technique_params['force_range'])
                time = np.random.uniform(*technique_params['time_range'])
                speed = None
                pulse_frequency = technique_params['frequency']
                current = None
                voltage = None
                rotation_speed = None
                travel_speed = None
                tool_diameter = None
                pulse_duration = None
                spot_size = None
                
            elif technique == 'Laser_Welding':
                power = np.random.uniform(*technique_params['power_range'])
                amplitude = None
                force = None
                time = None
                speed = np.random.uniform(*technique_params['speed_range'])
                pulse_frequency = np.random.uniform(*technique_params['pulse_frequency_range'])
                current = None
                voltage = None
                rotation_speed = None
                travel_speed = None
                tool_diameter = None
                pulse_duration = np.random.uniform(*technique_params['pulse_duration_range'])
                spot_size = np.random.uniform(*technique_params['spot_size_range'])
                
            elif technique == 'Resistance_Spot_Welding':
                power = None
                amplitude = None
                force = np.random.uniform(*technique_params['force_range'])
                time = np.random.uniform(*technique_params['time_range'])
                speed = None
                pulse_frequency = None
                current = np.random.uniform(*technique_params['current_range'])
                voltage = np.random.uniform(*technique_params['voltage_range'])
                rotation_speed = None
                travel_speed = None
                tool_diameter = None
                pulse_duration = None
                spot_size = None
                
            elif technique == 'Friction_Stir_Welding':
                power = None
                amplitude = None
                force = np.random.uniform(*technique_params['force_range'])
                time = None
                speed = None
                pulse_frequency = None
                current = None
                voltage = None
                rotation_speed = np.random.uniform(*technique_params['rotation_speed_range'])
                travel_speed = np.random.uniform(*technique_params['travel_speed_range'])
                tool_diameter = np.random.uniform(*technique_params['tool_diameter_range'])
                pulse_duration = None
                spot_size = None
            
            # Environmental conditions
            pre_heat_temperature = np.random.uniform(20, 200)  # °C
            humidity = np.random.uniform(20, 80)  # %
            atmospheric_pressure = np.random.uniform(95, 105)  # kPa
            
            # Additional process parameters
            weld_position = np.random.choice(['Flat', 'Horizontal', 'Vertical', 'Overhead'])
            joint_type = np.random.choice(['Butt', 'Lap', 'T-Joint', 'Corner', 'Edge'])
            joint_geometry = np.random.choice(['Square', 'V-Groove', 'U-Groove', 'J-Groove'])
            
            # Material preparation parameters
            cleaning_method = np.random.choice(['None', 'Acetone', 'Alcohol', 'Ultrasonic', 'Plasma'])
            pre_treatment = np.random.choice(['None', 'Annealing', 'Stress_Relief', 'Solution_Treatment'])
            
            sample = {
                'sample_id': f'WS_{i+1:06d}',
                'anode_material': anode_material,
                'cathode_material': cathode_material,
                'tab_thickness_um': tab_thickness,
                'surface_finish': surface_finish,
                'coating': coating,
                'welding_technique': technique,
                'power_w': power,
                'amplitude_um': amplitude,
                'force_n': force,
                'time_s': time,
                'speed_mm_s': speed,
                'pulse_frequency_hz': pulse_frequency,
                'current_a': current,
                'voltage_v': voltage,
                'rotation_speed_rpm': rotation_speed,
                'travel_speed_mm_s': travel_speed,
                'tool_diameter_mm': tool_diameter,
                'pulse_duration_ms': pulse_duration,
                'spot_size_mm': spot_size,
                'pre_heat_temperature_c': pre_heat_temperature,
                'humidity_percent': humidity,
                'atmospheric_pressure_kpa': atmospheric_pressure,
                'weld_position': weld_position,
                'joint_type': joint_type,
                'joint_geometry': joint_geometry,
                'cleaning_method': cleaning_method,
                'pre_treatment': pre_treatment
            }
            
            data.append(sample)
        
        return pd.DataFrame(data)

    def generate_characterization_metrics(self, input_df: pd.DataFrame) -> pd.DataFrame:
        """Generate characterization and quality metrics (Part 2 of the dataset)"""
        print("Generating characterization and quality metrics...")
        
        char_data = []
        
        for _, row in input_df.iterrows():
            # Get material properties
            anode_props = self.materials[row['anode_material']]
            cathode_props = self.materials[row['cathode_material']]
            
            # Calculate theoretical weld parameters
            power = row['power_w'] if pd.notna(row['power_w']) else 0
            force = row['force_n'] if pd.notna(row['force_n']) else 0
            time = row['time_s'] if pd.notna(row['time_s']) else 0
            amplitude = row['amplitude_um'] if pd.notna(row['amplitude_um']) else 0
            
            # Weld nugget size (mm) - based on power, force, and time
            if power > 0 and force > 0 and time > 0:
                # Empirical relationship for nugget size
                nugget_diameter = 2.5 * np.sqrt(power * time / (force * 1000)) + np.random.normal(0, 0.1)
                nugget_diameter = max(0.5, min(8.0, nugget_diameter))  # Realistic bounds
            else:
                nugget_diameter = np.random.uniform(1.0, 6.0)
            
            # Weld penetration depth (mm)
            penetration_depth = nugget_diameter * np.random.uniform(0.3, 0.8)
            
            # Contact resistance (mΩ) - influenced by materials and surface finish
            base_resistance = 1.0 / (anode_props.electrical_conductivity + cathode_props.electrical_conductivity) * 1e6
            surface_factor = 1.0
            if row['surface_finish'] in ['Rough', 'Oxidized']:
                surface_factor = 1.5
            elif row['surface_finish'] in ['Polished', 'Cleaned_Acetone']:
                surface_factor = 0.8
            
            contact_resistance = base_resistance * surface_factor * np.random.uniform(0.8, 1.2)
            
            # Shear strength (MPa) - based on materials and process parameters
            base_strength = min(anode_props.yield_strength, cathode_props.yield_strength)
            process_factor = 1.0
            if power > 0 and force > 0:
                process_factor = min(2.0, 1.0 + (power * time) / (force * 1000) * 0.1)
            
            shear_strength = base_strength * process_factor * np.random.uniform(0.7, 1.3)
            
            # Tensile strength (MPa)
            tensile_strength = shear_strength * np.random.uniform(1.2, 1.8)
            
            # Hardness (HV) - Vickers hardness
            base_hardness = (anode_props.yield_strength + cathode_props.yield_strength) / 2 * 0.3
            hardness = base_hardness * np.random.uniform(0.8, 1.5)
            
            # Porosity percentage
            porosity = np.random.beta(2, 8) * 5  # Most welds have low porosity
            
            # Crack density (cracks per mm²)
            crack_density = np.random.exponential(0.1)
            
            # Weld width (mm)
            weld_width = nugget_diameter * np.random.uniform(1.0, 1.5)
            
            # Heat affected zone width (mm)
            haz_width = weld_width * np.random.uniform(0.5, 1.0)
            
            # Microstructure quality score (0-100)
            microstructure_score = 100 - porosity * 10 - crack_density * 5
            microstructure_score = max(0, min(100, microstructure_score))
            
            # Bond quality index (0-100)
            bond_quality = (microstructure_score + (100 - contact_resistance * 10) + 
                          (shear_strength / base_strength * 50)) / 3
            bond_quality = max(0, min(100, bond_quality))
            
            # Electrical conductivity (S/m)
            electrical_conductivity = 1.0 / contact_resistance * 1e-3
            
            # Thermal conductivity (W/m·K)
            thermal_conductivity = (anode_props.thermal_conductivity + cathode_props.thermal_conductivity) / 2
            thermal_conductivity *= np.random.uniform(0.8, 1.2)
            
            char_sample = {
                'sample_id': row['sample_id'],
                'nugget_diameter_mm': nugget_diameter,
                'penetration_depth_mm': penetration_depth,
                'weld_width_mm': weld_width,
                'haz_width_mm': haz_width,
                'contact_resistance_mohm': contact_resistance,
                'electrical_conductivity_s_m': electrical_conductivity,
                'thermal_conductivity_w_mk': thermal_conductivity,
                'shear_strength_mpa': shear_strength,
                'tensile_strength_mpa': tensile_strength,
                'hardness_hv': hardness,
                'porosity_percent': porosity,
                'crack_density_per_mm2': crack_density,
                'microstructure_score': microstructure_score,
                'bond_quality_index': bond_quality,
                'weld_quality_class': 'A' if bond_quality > 80 else 'B' if bond_quality > 60 else 'C'
            }
            
            char_data.append(char_sample)
        
        return pd.DataFrame(char_data)

    def generate_performance_metrics(self, input_df: pd.DataFrame, char_df: pd.DataFrame) -> pd.DataFrame:
        """Generate performance and validation metrics (Part 3 of the dataset)"""
        print("Generating performance and validation metrics...")
        
        perf_data = []
        
        for _, (input_row, char_row) in enumerate(zip(input_df.iterrows(), char_df.iterrows())):
            input_row = input_row[1]
            char_row = char_row[1]
            
            # Temperature cycling parameters
            min_temp = np.random.uniform(-40, -20)  # °C
            max_temp = np.random.uniform(60, 85)    # °C
            cycle_count = np.random.randint(100, 2000)
            ramp_rate = np.random.uniform(1, 10)    # °C/min
            
            # Calculate thermal stress based on material properties and temperature range
            anode_props = self.materials[input_row['anode_material']]
            cathode_props = self.materials[input_row['cathode_material']]
            
            temp_range = max_temp - min_temp
            thermal_stress = (anode_props.thermal_expansion + cathode_props.thermal_expansion) / 2 * temp_range * 1000
            
            # Fatigue life prediction (cycles to failure)
            base_fatigue_life = 1000
            if char_row['bond_quality_index'] > 80:
                quality_factor = 2.0
            elif char_row['bond_quality_index'] > 60:
                quality_factor = 1.0
            else:
                quality_factor = 0.5
            
            # Process parameter effects on fatigue
            process_factor = 1.0
            if pd.notna(input_row['power_w']) and pd.notna(input_row['force_n']):
                power_density = input_row['power_w'] / (char_row['nugget_diameter_mm'] ** 2)
                process_factor = 1.0 + power_density / 1000  # Higher power density improves fatigue
            
            fatigue_life = base_fatigue_life * quality_factor * process_factor * np.random.uniform(0.5, 2.0)
            
            # Electrical resistance change after cycling (%)
            resistance_change = np.random.exponential(5) * (1 + thermal_stress / 1000)
            resistance_change = min(50, resistance_change)  # Cap at 50%
            
            # Mechanical strength retention (%)
            strength_retention = 100 - resistance_change * 0.5 - np.random.exponential(2)
            strength_retention = max(20, strength_retention)
            
            # Failure mode prediction
            if resistance_change > 30:
                failure_mode = 'Electrical'
            elif strength_retention < 50:
                failure_mode = 'Mechanical'
            else:
                failure_mode = 'Thermal_Fatigue'
            
            # Reliability metrics
            mttf = fatigue_life * np.random.uniform(0.8, 1.2)  # Mean time to failure
            reliability_95 = 0.95 if fatigue_life > cycle_count else 0.5
            
            # Thermal performance
            thermal_resistance = 1.0 / char_row['thermal_conductivity_w_mk'] * 1000  # K/W
            thermal_resistance_change = resistance_change * 0.3  # Thermal follows electrical
            
            # Creep resistance (time to 1% strain at 80°C)
            creep_resistance = char_row['hardness_hv'] * 1000 / thermal_stress
            creep_resistance *= np.random.uniform(0.5, 2.0)
            
            # Corrosion resistance (based on materials and surface treatment)
            corrosion_resistance = 50  # Base value
            if input_row['coating'] in ['Gold', 'Silver', 'Nickel']:
                corrosion_resistance += 30
            elif input_row['coating'] in ['Zinc', 'Tin']:
                corrosion_resistance += 20
            elif input_row['surface_finish'] in ['Anodized', 'Oxidized']:
                corrosion_resistance += 15
            
            corrosion_resistance += np.random.uniform(-10, 10)
            corrosion_resistance = max(0, min(100, corrosion_resistance))
            
            # Performance score (0-100)
            performance_score = (reliability_95 * 40 + 
                               (100 - resistance_change) * 0.3 + 
                               strength_retention * 0.2 + 
                               corrosion_resistance * 0.1)
            
            perf_sample = {
                'sample_id': input_row['sample_id'],
                'min_temperature_c': min_temp,
                'max_temperature_c': max_temp,
                'cycle_count': cycle_count,
                'ramp_rate_c_per_min': ramp_rate,
                'thermal_stress_mpa': thermal_stress,
                'fatigue_life_cycles': fatigue_life,
                'resistance_change_percent': resistance_change,
                'strength_retention_percent': strength_retention,
                'failure_mode': failure_mode,
                'mttf_hours': mttf,
                'reliability_95_percent': reliability_95,
                'thermal_resistance_k_w': thermal_resistance,
                'thermal_resistance_change_percent': thermal_resistance_change,
                'creep_resistance_hours': creep_resistance,
                'corrosion_resistance_index': corrosion_resistance,
                'performance_score': performance_score,
                'pass_fail': 'PASS' if performance_score > 70 else 'FAIL'
            }
            
            perf_data.append(perf_sample)
        
        return pd.DataFrame(perf_data)

    def generate_complete_dataset(self, n_samples: int = 10000) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Generate the complete welding dataset"""
        print(f"Generating complete welding dataset with {n_samples} samples...")
        
        # Generate all three parts
        input_df = self.generate_input_parameters(n_samples)
        char_df = self.generate_characterization_metrics(input_df)
        perf_df = self.generate_performance_metrics(input_df, char_df)
        
        return input_df, char_df, perf_df

    def save_dataset(self, input_df: pd.DataFrame, char_df: pd.DataFrame, perf_df: pd.DataFrame, 
                    base_filename: str = "welding_dataset"):
        """Save dataset in multiple formats"""
        print("Saving dataset in multiple formats...")
        
        # Save as CSV files
        input_df.to_csv(f"{base_filename}_input_parameters.csv", index=False)
        char_df.to_csv(f"{base_filename}_characterization_metrics.csv", index=False)
        perf_df.to_csv(f"{base_filename}_performance_metrics.csv", index=False)
        
        # Combine all data into a single CSV
        combined_df = input_df.merge(char_df, on='sample_id').merge(perf_df, on='sample_id')
        combined_df.to_csv(f"{base_filename}_complete.csv", index=False)
        
        # Save as JSON
        dataset_dict = {
            'metadata': {
                'description': 'Comprehensive dataset for ML-driven inverse design of welding parameters',
                'total_samples': len(input_df),
                'generated_date': pd.Timestamp.now().isoformat(),
                'random_seed': self.random_seed
            },
            'input_parameters': input_df.to_dict('records'),
            'characterization_metrics': char_df.to_dict('records'),
            'performance_metrics': perf_df.to_dict('records')
        }
        
        with open(f"{base_filename}_complete.json", 'w') as f:
            json.dump(dataset_dict, f, indent=2, default=str)
        
        # Save as HDF5 for efficient storage (using h5py directly to avoid locking issues)
        try:
            with h5py.File(f"{base_filename}_complete.h5", 'w') as f:
                # Store metadata
                f.attrs['description'] = 'Welding parameters dataset'
                f.attrs['total_samples'] = len(input_df)
                f.attrs['generated_date'] = pd.Timestamp.now().isoformat()
                
                # Store dataframes as datasets
                f.create_dataset('input_parameters', data=input_df.to_records(index=False))
                f.create_dataset('characterization_metrics', data=char_df.to_records(index=False))
                f.create_dataset('performance_metrics', data=perf_df.to_records(index=False))
        except Exception as e:
            print(f"Warning: Could not save HDF5 file: {e}")
            print("Continuing with other formats...")
        
        print(f"Dataset saved as:")
        print(f"  - {base_filename}_input_parameters.csv")
        print(f"  - {base_filename}_characterization_metrics.csv")
        print(f"  - {base_filename}_performance_metrics.csv")
        print(f"  - {base_filename}_complete.csv")
        print(f"  - {base_filename}_complete.json")
        print(f"  - {base_filename}_complete.h5")

    def generate_analysis_report(self, input_df: pd.DataFrame, char_df: pd.DataFrame, perf_df: pd.DataFrame):
        """Generate statistical analysis report"""
        print("Generating analysis report...")
        
        report = {
            'dataset_overview': {
                'total_samples': len(input_df),
                'input_parameters_count': len(input_df.columns),
                'characterization_metrics_count': len(char_df.columns),
                'performance_metrics_count': len(perf_df.columns)
            },
            'material_distribution': input_df['anode_material'].value_counts().to_dict(),
            'welding_technique_distribution': input_df['welding_technique'].value_counts().to_dict(),
            'quality_distribution': char_df['weld_quality_class'].value_counts().to_dict(),
            'performance_distribution': perf_df['pass_fail'].value_counts().to_dict(),
            'statistical_summary': {
                'input_parameters': input_df.describe().to_dict(),
                'characterization_metrics': char_df.describe().to_dict(),
                'performance_metrics': perf_df.describe().to_dict()
            }
        }
        
        with open('welding_dataset_analysis.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print("Analysis report saved as welding_dataset_analysis.json")

def main():
    """Main function to generate the complete dataset"""
    print("=" * 80)
    print("WELDING PARAMETERS DATASET GENERATOR")
    print("=" * 80)
    
    # Initialize generator
    generator = WeldingDatasetGenerator(random_seed=42)
    
    # Generate dataset
    input_df, char_df, perf_df = generator.generate_complete_dataset(n_samples=10000)
    
    # Save dataset
    generator.save_dataset(input_df, char_df, perf_df, "welding_dataset")
    
    # Generate analysis report
    generator.generate_analysis_report(input_df, char_df, perf_df)
    
    print("\n" + "=" * 80)
    print("DATASET GENERATION COMPLETE!")
    print("=" * 80)
    print(f"Generated {len(input_df)} samples")
    print(f"Input parameters: {len(input_df.columns)} features")
    print(f"Characterization metrics: {len(char_df.columns)} features")
    print(f"Performance metrics: {len(perf_df.columns)} features")
    print("\nFiles created:")
    print("- welding_dataset_input_parameters.csv")
    print("- welding_dataset_characterization_metrics.csv")
    print("- welding_dataset_performance_metrics.csv")
    print("- welding_dataset_complete.csv")
    print("- welding_dataset_complete.json")
    print("- welding_dataset_complete.h5")
    print("- welding_dataset_analysis.json")

if __name__ == "__main__":
    main()