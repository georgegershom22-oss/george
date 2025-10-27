#!/usr/bin/env python3
"""
Comprehensive Welding Dataset Generator for ML-Driven Inverse Design
====================================================================

This module generates a realistic, physics-based dataset for welding parameter optimization
with focus on extreme-temperature cycling performance.

Author: AI Assistant
Date: 2024
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class WeldingDatasetGenerator:
    """
    Generates comprehensive welding datasets with realistic physics-based relationships
    """
    
    def __init__(self, random_seed=42):
        """Initialize the dataset generator"""
        np.random.seed(random_seed)
        self.random_seed = random_seed
        
        # Material properties database
        self.materials = {
            'Cu': {
                'thermal_conductivity': 400,  # W/m·K
                'electrical_conductivity': 5.8e7,  # S/m
                'melting_point': 1085,  # °C
                'density': 8960,  # kg/m³
                'specific_heat': 385,  # J/kg·K
                'thermal_expansion': 16.5e-6,  # 1/K
                'yield_strength': 70e6,  # Pa
                'ultimate_strength': 220e6,  # Pa
                'fatigue_limit': 62e6,  # Pa
            },
            'Al': {
                'thermal_conductivity': 237,  # W/m·K
                'electrical_conductivity': 3.5e7,  # S/m
                'melting_point': 660,  # °C
                'density': 2700,  # kg/m³
                'specific_heat': 900,  # J/kg·K
                'thermal_expansion': 23.1e-6,  # 1/K
                'yield_strength': 95e6,  # Pa
                'ultimate_strength': 186e6,  # Pa
                'fatigue_limit': 62e6,  # Pa
            },
            'Ni': {
                'thermal_conductivity': 90,  # W/m·K
                'electrical_conductivity': 1.4e7,  # S/m
                'melting_point': 1455,  # °C
                'density': 8900,  # kg/m³
                'specific_heat': 444,  # J/kg·K
                'thermal_expansion': 13.4e-6,  # 1/K
                'yield_strength': 103e6,  # Pa
                'ultimate_strength': 317e6,  # Pa
                'fatigue_limit': 241e6,  # Pa
            },
            'Ti': {
                'thermal_conductivity': 22,  # W/m·K
                'electrical_conductivity': 2.4e6,  # S/m
                'melting_point': 1668,  # °C
                'density': 4500,  # kg/m³
                'specific_heat': 523,  # J/kg·K
                'thermal_expansion': 8.6e-6,  # 1/K
                'yield_strength': 880e6,  # Pa
                'ultimate_strength': 950e6,  # Pa
                'fatigue_limit': 400e6,  # Pa
            }
        }
        
        # Welding techniques and their characteristics
        self.welding_techniques = {
            'USW': {
                'power_range': (50, 2000),  # W
                'amplitude_range': (10, 100),  # µm
                'force_range': (50, 500),  # N
                'time_range': (0.1, 2.0),  # s
                'efficiency': 0.85,
                'heat_affected_zone': 0.1,  # mm
            },
            'Laser': {
                'power_range': (100, 5000),  # W
                'speed_range': (1, 50),  # mm/s
                'pulse_freq_range': (1, 1000),  # Hz
                'pulse_energy_range': (0.1, 10),  # J
                'efficiency': 0.75,
                'heat_affected_zone': 0.05,  # mm
            },
            'Resistance': {
                'power_range': (200, 3000),  # W
                'force_range': (100, 1000),  # N
                'time_range': (0.05, 1.0),  # s
                'current_range': (1000, 10000),  # A
                'efficiency': 0.90,
                'heat_affected_zone': 0.2,  # mm
            }
        }
        
        # Surface finishes and their properties
        self.surface_finishes = {
            'Bare': {'contact_resistance': 1e-6, 'bondability': 0.8},
            'Oxidized': {'contact_resistance': 1e-4, 'bondability': 0.3},
            'Coated_Ag': {'contact_resistance': 5e-7, 'bondability': 0.95},
            'Coated_Ni': {'contact_resistance': 2e-6, 'bondability': 0.85},
            'Roughened': {'contact_resistance': 8e-7, 'bondability': 0.9},
            'Polished': {'contact_resistance': 5e-7, 'bondability': 0.7}
        }
    
    def generate_input_parameters(self, n_samples=10000):
        """
        Generate input parameters for the welding process
        """
        print(f"Generating {n_samples} input parameter sets...")
        
        data = []
        
        for i in range(n_samples):
            # Base materials (randomly select anode and cathode)
            anode_material = np.random.choice(list(self.materials.keys()))
            cathode_material = np.random.choice(list(self.materials.keys()))
            
            # Ensure different materials for most cases (90% different, 10% same)
            if np.random.random() < 0.9:
                while cathode_material == anode_material:
                    cathode_material = np.random.choice(list(self.materials.keys()))
            
            # Tab thickness (realistic range for battery applications)
            tab_thickness = np.random.uniform(50, 500)  # µm
            
            # Surface finish
            surface_finish = np.random.choice(list(self.surface_finishes.keys()))
            
            # Welding technique
            technique = np.random.choice(list(self.welding_techniques.keys()))
            technique_params = self.welding_techniques[technique]
            
            # Technique-specific parameters
            if technique == 'USW':
                power = np.random.uniform(*technique_params['power_range'])
                amplitude = np.random.uniform(*technique_params['amplitude_range'])
                force = np.random.uniform(*technique_params['force_range'])
                time = np.random.uniform(*technique_params['time_range'])
                speed = np.nan
                pulse_frequency = np.nan
                pulse_energy = np.nan
                current = np.nan
                
            elif technique == 'Laser':
                power = np.random.uniform(*technique_params['power_range'])
                speed = np.random.uniform(*technique_params['speed_range'])
                pulse_frequency = np.random.uniform(*technique_params['pulse_freq_range'])
                pulse_energy = np.random.uniform(*technique_params['pulse_energy_range'])
                amplitude = np.nan
                force = np.nan
                time = np.nan
                current = np.nan
                
            else:  # Resistance
                power = np.random.uniform(*technique_params['power_range'])
                force = np.random.uniform(*technique_params['force_range'])
                time = np.random.uniform(*technique_params['time_range'])
                current = np.random.uniform(*technique_params['current_range'])
                amplitude = np.nan
                speed = np.nan
                pulse_frequency = np.nan
                pulse_energy = np.nan
            
            # Environmental conditions
            pre_heat_temp = np.random.uniform(20, 200)  # °C
            
            # Store the parameters
            sample = {
                'sample_id': f'weld_{i:06d}',
                'anode_material': anode_material,
                'cathode_material': cathode_material,
                'tab_thickness_um': tab_thickness,
                'surface_finish': surface_finish,
                'welding_technique': technique,
                'power_W': power,
                'amplitude_um': amplitude,
                'force_N': force,
                'time_s': time,
                'speed_mm_s': speed,
                'pulse_frequency_Hz': pulse_frequency,
                'pulse_energy_J': pulse_energy,
                'current_A': current,
                'pre_heat_temp_C': pre_heat_temp
            }
            
            data.append(sample)
        
        return pd.DataFrame(data)
    
    def calculate_heat_input(self, row):
        """Calculate heat input based on welding parameters"""
        technique = row['welding_technique']
        power = row['power_W']
        
        if technique == 'USW':
            time = row['time_s']
            efficiency = self.welding_techniques[technique]['efficiency']
            heat_input = power * time * efficiency
        elif technique == 'Laser':
            speed = row['speed_mm_s']
            efficiency = self.welding_techniques[technique]['efficiency']
            # Assume 1mm weld length for calculation
            time = 1.0 / speed if speed > 0 else 0.1
            heat_input = power * time * efficiency
        else:  # Resistance
            time = row['time_s']
            efficiency = self.welding_techniques[technique]['efficiency']
            heat_input = power * time * efficiency
            
        return heat_input
    
    def calculate_contact_resistance(self, row):
        """Calculate contact resistance based on materials and surface finish"""
        anode_mat = self.materials[row['anode_material']]
        cathode_mat = self.materials[row['cathode_material']]
        surface = self.surface_finishes[row['surface_finish']]
        
        # Base contact resistance from surface finish
        base_resistance = surface['contact_resistance']
        
        # Material compatibility factor
        thermal_diff = abs(anode_mat['thermal_conductivity'] - cathode_mat['thermal_conductivity'])
        thermal_diff_factor = 1 + (thermal_diff / 1000) * 0.1
        
        # Thickness effect (thinner = higher resistance)
        thickness_factor = 1 + (200 / row['tab_thickness_um']) * 0.2
        
        contact_resistance = base_resistance * thermal_diff_factor * thickness_factor
        
        return contact_resistance
    
    def calculate_weld_strength(self, row):
        """Calculate weld strength based on process parameters and materials"""
        anode_mat = self.materials[row['anode_material']]
        cathode_mat = self.materials[row['cathode_material']]
        
        # Base strength from weaker material
        base_strength = min(anode_mat['yield_strength'], cathode_mat['yield_strength'])
        
        # Heat input effect (optimal heat input range)
        heat_input = self.calculate_heat_input(row)
        optimal_heat = 1000  # J (optimal for most cases)
        heat_factor = 1 - abs(heat_input - optimal_heat) / optimal_heat * 0.3
        heat_factor = max(0.3, min(1.0, heat_factor))
        
        # Force effect (higher force = better contact)
        if not pd.isna(row['force_N']):
            force_factor = min(1.0, row['force_N'] / 300)  # 300N is optimal
        else:
            force_factor = 0.8  # Default for techniques without force control
        
        # Surface finish effect
        surface = self.surface_finishes[row['surface_finish']]
        surface_factor = surface['bondability']
        
        # Technique efficiency
        technique = self.welding_techniques[row['welding_technique']]
        technique_factor = technique['efficiency']
        
        weld_strength = base_strength * heat_factor * force_factor * surface_factor * technique_factor
        
        return weld_strength
    
    def calculate_heat_affected_zone(self, row):
        """Calculate heat affected zone size"""
        technique = self.welding_techniques[row['welding_technique']]
        base_haz = technique['heat_affected_zone']
        
        # Heat input effect
        heat_input = self.calculate_heat_input(row)
        heat_factor = 1 + (heat_input / 1000) * 0.5
        
        # Material thermal conductivity effect
        anode_mat = self.materials[row['anode_material']]
        cathode_mat = self.materials[row['cathode_material']]
        avg_thermal_cond = (anode_mat['thermal_conductivity'] + cathode_mat['thermal_conductivity']) / 2
        thermal_factor = 1 - (avg_thermal_cond / 1000) * 0.3
        
        haz_size = base_haz * heat_factor * thermal_factor
        
        return max(0.01, haz_size)  # Minimum 0.01mm
    
    def calculate_porosity(self, row):
        """Calculate porosity percentage in the weld"""
        # Base porosity from technique
        technique_porosity = {
            'USW': 0.5,
            'Laser': 0.2,
            'Resistance': 1.0
        }
        
        base_porosity = technique_porosity[row['welding_technique']]
        
        # Heat input effect (too much or too little heat increases porosity)
        heat_input = self.calculate_heat_input(row)
        optimal_heat = 1000
        heat_deviation = abs(heat_input - optimal_heat) / optimal_heat
        heat_factor = 1 + heat_deviation * 0.5
        
        # Force effect (insufficient force increases porosity)
        if not pd.isna(row['force_N']):
            force_factor = max(0.5, 1 - (300 - row['force_N']) / 300 * 0.3)
        else:
            force_factor = 0.9
        
        # Surface finish effect
        surface = self.surface_finishes[row['surface_finish']]
        surface_factor = 1 + (1 - surface['bondability']) * 0.5
        
        porosity = base_porosity * heat_factor * force_factor * surface_factor
        
        return min(10.0, max(0.1, porosity))  # Clamp between 0.1% and 10%
    
    def calculate_characterization_metrics(self, df):
        """
        Calculate characterization and quality metrics (forward problem outputs)
        """
        print("Calculating characterization and quality metrics...")
        
        results = []
        
        for idx, row in df.iterrows():
            # Basic calculations
            heat_input = self.calculate_heat_input(row)
            contact_resistance = self.calculate_contact_resistance(row)
            weld_strength = self.calculate_weld_strength(row)
            haz_size = self.calculate_heat_affected_zone(row)
            porosity = self.calculate_porosity(row)
            
            # Additional quality metrics
            # Weld width (correlates with heat input and technique)
            technique = self.welding_techniques[row['welding_technique']]
            base_width = 0.5  # mm
            width_factor = 1 + (heat_input / 2000) * 0.5
            weld_width = base_width * width_factor
            
            # Penetration depth (for laser welding)
            if row['welding_technique'] == 'Laser':
                penetration_depth = min(2.0, heat_input / 1000 * 0.5)
            else:
                penetration_depth = min(1.0, heat_input / 2000 * 0.3)
            
            # Microhardness (inversely related to heat input)
            anode_mat = self.materials[row['anode_material']]
            cathode_mat = self.materials[row['cathode_material']]
            base_hardness = (anode_mat['yield_strength'] + cathode_mat['yield_strength']) / 2 / 1e6
            heat_softening = 1 - (heat_input / 2000) * 0.2
            microhardness = base_hardness * max(0.5, heat_softening)
            
            # Electrical resistance (includes contact and bulk resistance)
            bulk_resistance = 1e-6  # Base bulk resistance
            total_resistance = contact_resistance + bulk_resistance
            
            # Thermal resistance (for heat dissipation)
            thermal_resistance = 1 / (anode_mat['thermal_conductivity'] + cathode_mat['thermal_conductivity']) * 1e3
            
            # Add realistic noise to measurements
            noise_factor = 0.05  # 5% noise
            
            result = {
                'sample_id': row['sample_id'],
                'heat_input_J': heat_input * (1 + np.random.normal(0, noise_factor)),
                'contact_resistance_Ohm': contact_resistance * (1 + np.random.normal(0, noise_factor)),
                'weld_strength_MPa': weld_strength * (1 + np.random.normal(0, noise_factor)),
                'heat_affected_zone_mm': haz_size * (1 + np.random.normal(0, noise_factor)),
                'porosity_percent': porosity * (1 + np.random.normal(0, noise_factor)),
                'weld_width_mm': weld_width * (1 + np.random.normal(0, noise_factor)),
                'penetration_depth_mm': penetration_depth * (1 + np.random.normal(0, noise_factor)),
                'microhardness_HV': microhardness * (1 + np.random.normal(0, noise_factor)),
                'total_resistance_Ohm': total_resistance * (1 + np.random.normal(0, noise_factor)),
                'thermal_resistance_K_W': thermal_resistance * (1 + np.random.normal(0, noise_factor))
            }
            
            results.append(result)
        
        return pd.DataFrame(results)
    
    def calculate_performance_metrics(self, char_df, input_df):
        """
        Calculate performance and validation metrics (inverse design targets)
        Focus on extreme-temperature cycling performance
        """
        print("Calculating performance and validation metrics...")
        
        results = []
        
        for idx, row in char_df.iterrows():
            # Get corresponding input parameters
            input_row = input_df.iloc[idx]
            
            # Get material properties
            anode_mat = self.materials[input_row['anode_material']]
            cathode_mat = self.materials[input_row['cathode_material']]
            
            # Base performance factors
            weld_strength = row['weld_strength_MPa']
            porosity = row['porosity_percent']
            haz_size = row['heat_affected_zone_mm']
            contact_resistance = row['contact_resistance_Ohm']
            
            # Thermal cycling performance (primary target)
            # Based on thermal expansion mismatch and weld quality
            thermal_expansion_diff = abs(anode_mat['thermal_expansion'] - cathode_mat['thermal_expansion'])
            thermal_mismatch_factor = 1 - (thermal_expansion_diff / 1e-5) * 0.3
            
            # Porosity effect on thermal cycling
            porosity_factor = 1 - (porosity / 10) * 0.4
            
            # Heat affected zone effect
            haz_factor = 1 - (haz_size / 1) * 0.2
            
            # Calculate cycles to failure
            base_cycles = 10000  # Base cycles for good welds
            thermal_cycles = base_cycles * thermal_mismatch_factor * porosity_factor * haz_factor
            
            # Add realistic variation
            thermal_cycles *= (1 + np.random.normal(0, 0.2))
            thermal_cycles = max(100, min(50000, thermal_cycles))  # Clamp realistic range
            
            # High temperature strength retention (at 200°C)
            temp_factor = 0.8  # 20% strength loss at high temp
            high_temp_strength = weld_strength * temp_factor * (1 - porosity / 20)
            
            # Fatigue life (cycles at 50% of yield strength)
            fatigue_stress = min(anode_mat['yield_strength'], cathode_mat['yield_strength']) * 0.5
            stress_ratio = fatigue_stress / (weld_strength * 1e6)  # Convert MPa to Pa
            
            if stress_ratio < 0.1:
                fatigue_cycles = 1e6  # Very high cycle life
            else:
                fatigue_cycles = 1e6 * (0.1 / stress_ratio) ** 3  # Power law relationship
            
            # Electrical performance under thermal cycling
            resistance_increase = 1 + (thermal_cycles / 10000) * 0.1  # 10% increase per 10k cycles
            final_resistance = contact_resistance * resistance_increase
            
            # Thermal performance (heat dissipation capability)
            thermal_conductivity_avg = (anode_mat['thermal_conductivity'] + cathode_mat['thermal_conductivity']) / 2
            thermal_performance = thermal_conductivity_avg * (1 - porosity / 20) * (1 - haz_size / 2)
            
            # Creep resistance (deformation under load at high temperature)
            creep_resistance = weld_strength * (1 - porosity / 15) * thermal_mismatch_factor
            
            # Interfacial stability (resistance to delamination)
            interfacial_stability = (1 - porosity / 10) * (1 - thermal_expansion_diff / 1e-5) * (1 - haz_size / 1)
            interfacial_stability = max(0.1, min(1.0, interfacial_stability))
            
            # Add noise to all measurements
            noise_factor = 0.1  # 10% noise for performance metrics
            
            result = {
                'sample_id': row['sample_id'],
                'thermal_cycles_to_failure': int(thermal_cycles * (1 + np.random.normal(0, noise_factor))),
                'high_temp_strength_MPa': high_temp_strength * (1 + np.random.normal(0, noise_factor)),
                'fatigue_cycles_1e6': fatigue_cycles / 1e6 * (1 + np.random.normal(0, noise_factor)),
                'resistance_after_cycling_Ohm': final_resistance * (1 + np.random.normal(0, noise_factor)),
                'thermal_performance_W_mK': thermal_performance * (1 + np.random.normal(0, noise_factor)),
                'creep_resistance_MPa': creep_resistance * (1 + np.random.normal(0, noise_factor)),
                'interfacial_stability': interfacial_stability * (1 + np.random.normal(0, noise_factor)),
                'thermal_expansion_mismatch_1e6_K': thermal_expansion_diff * 1e6 * (1 + np.random.normal(0, noise_factor))
            }
            
            results.append(result)
        
        return pd.DataFrame(results)
    
    def generate_complete_dataset(self, n_samples=10000):
        """
        Generate the complete welding dataset
        """
        print(f"Generating comprehensive welding dataset with {n_samples} samples...")
        
        # Generate input parameters
        input_df = self.generate_input_parameters(n_samples)
        
        # Calculate characterization metrics
        char_df = self.calculate_characterization_metrics(input_df)
        
        # Calculate performance metrics
        perf_df = self.calculate_performance_metrics(char_df, input_df)
        
        # Merge all dataframes
        complete_df = input_df.merge(char_df, on='sample_id').merge(perf_df, on='sample_id')
        
        return complete_df
    
    def save_dataset(self, df, filename='welding_dataset.csv'):
        """Save dataset to CSV file"""
        df.to_csv(filename, index=False)
        print(f"Dataset saved to {filename}")
        
        # Also save as Excel with multiple sheets
        excel_filename = filename.replace('.csv', '.xlsx')
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            # Input parameters
            input_cols = [col for col in df.columns if col in [
                'sample_id', 'anode_material', 'cathode_material', 'tab_thickness_um',
                'surface_finish', 'welding_technique', 'power_W', 'amplitude_um',
                'force_N', 'time_s', 'speed_mm_s', 'pulse_frequency_Hz',
                'pulse_energy_J', 'current_A', 'pre_heat_temp_C'
            ]]
            df[input_cols].to_excel(writer, sheet_name='Input_Parameters', index=False)
            
            # Characterization metrics
            char_cols = [col for col in df.columns if col in [
                'sample_id', 'heat_input_J', 'contact_resistance_Ohm', 'weld_strength_MPa',
                'heat_affected_zone_mm', 'porosity_percent', 'weld_width_mm',
                'penetration_depth_mm', 'microhardness_HV', 'total_resistance_Ohm',
                'thermal_resistance_K_W'
            ]]
            df[char_cols].to_excel(writer, sheet_name='Characterization_Metrics', index=False)
            
            # Performance metrics
            perf_cols = [col for col in df.columns if col in [
                'sample_id', 'thermal_cycles_to_failure', 'high_temp_strength_MPa',
                'fatigue_cycles_1e6', 'resistance_after_cycling_Ohm',
                'thermal_performance_W_mK', 'creep_resistance_MPa',
                'interfacial_stability', 'thermal_expansion_mismatch_1e6_K'
            ]]
            df[perf_cols].to_excel(writer, sheet_name='Performance_Metrics', index=False)
            
            # Complete dataset
            df.to_excel(writer, sheet_name='Complete_Dataset', index=False)
        
        print(f"Excel file saved to {excel_filename}")
        
        return filename, excel_filename

def main():
    """Main function to generate the dataset"""
    print("=" * 60)
    print("Welding Dataset Generator for ML-Driven Inverse Design")
    print("=" * 60)
    
    # Initialize generator
    generator = WeldingDatasetGenerator(random_seed=42)
    
    # Generate dataset
    n_samples = 15000  # Large dataset for comprehensive ML training
    dataset = generator.generate_complete_dataset(n_samples)
    
    # Save dataset
    csv_file, excel_file = generator.save_dataset(dataset)
    
    # Print dataset summary
    print(f"\nDataset Summary:")
    print(f"Total samples: {len(dataset)}")
    print(f"Input parameters: {len([col for col in dataset.columns if col in [
        'anode_material', 'cathode_material', 'tab_thickness_um', 'surface_finish',
        'welding_technique', 'power_W', 'amplitude_um', 'force_N', 'time_s',
        'speed_mm_s', 'pulse_frequency_Hz', 'pulse_energy_J', 'current_A', 'pre_heat_temp_C'
    ]])}")
    print(f"Characterization metrics: {len([col for col in dataset.columns if col in [
        'heat_input_J', 'contact_resistance_Ohm', 'weld_strength_MPa',
        'heat_affected_zone_mm', 'porosity_percent', 'weld_width_mm',
        'penetration_depth_mm', 'microhardness_HV', 'total_resistance_Ohm',
        'thermal_resistance_K_W'
    ]])}")
    print(f"Performance metrics: {len([col for col in dataset.columns if col in [
        'thermal_cycles_to_failure', 'high_temp_strength_MPa', 'fatigue_cycles_1e6',
        'resistance_after_cycling_Ohm', 'thermal_performance_W_mK', 'creep_resistance_MPa',
        'interfacial_stability', 'thermal_expansion_mismatch_1e6_K'
    ]])}")
    
    print(f"\nFiles created:")
    print(f"- {csv_file}")
    print(f"- {excel_file}")
    
    return dataset

if __name__ == "__main__":
    dataset = main()