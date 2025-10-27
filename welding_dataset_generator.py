#!/usr/bin/env python3
"""
Comprehensive Welding Parameter Dataset Generator for ML-Driven Inverse Design

This script generates a realistic dataset for machine learning applications in welding
parameter optimization, specifically targeting extreme-temperature cycling performance.

The dataset includes:
1. Input Parameters (Design Space) - Controllable welding parameters
2. Characterization & Quality Metrics (Forward Problem) - Immediate weld quality
3. Performance & Validation Metrics (Inverse Design Targets) - Long-term performance

Author: AI Assistant
Date: 2025-10-27
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

class WeldingDatasetGenerator:
    def __init__(self, n_samples=10000):
        """
        Initialize the welding dataset generator
        
        Args:
            n_samples (int): Number of samples to generate
        """
        self.n_samples = n_samples
        self.data = {}
        
        # Define material properties
        self.materials = {
            'anode': ['Cu', 'Cu-Ni', 'Cu-Be', 'Brass', 'Bronze'],
            'cathode': ['Al', 'Al-6061', 'Al-5052', 'Al-1100', 'Al-Mg'],
            'coatings': ['None', 'Ni-plated', 'Sn-plated', 'Ag-plated', 'Oxide-removed'],
            'techniques': ['USW', 'Laser', 'RSW', 'TIG', 'Friction']
        }
        
        # Material property lookup tables
        self.material_properties = {
            'Cu': {'conductivity': 401, 'melting_point': 1085, 'density': 8.96, 'hardness': 369},
            'Cu-Ni': {'conductivity': 45, 'melting_point': 1170, 'density': 8.9, 'hardness': 1200},
            'Cu-Be': {'conductivity': 105, 'melting_point': 1030, 'density': 8.25, 'hardness': 1380},
            'Brass': {'conductivity': 109, 'melting_point': 930, 'density': 8.5, 'hardness': 550},
            'Bronze': {'conductivity': 65, 'melting_point': 950, 'density': 8.8, 'hardness': 870},
            'Al': {'conductivity': 237, 'melting_point': 660, 'density': 2.70, 'hardness': 245},
            'Al-6061': {'conductivity': 167, 'melting_point': 582, 'density': 2.70, 'hardness': 950},
            'Al-5052': {'conductivity': 138, 'melting_point': 607, 'density': 2.68, 'hardness': 680},
            'Al-1100': {'conductivity': 222, 'melting_point': 643, 'density': 2.71, 'hardness': 230},
            'Al-Mg': {'conductivity': 154, 'melting_point': 630, 'density': 2.66, 'hardness': 750}
        }
        
    def generate_input_parameters(self):
        """Generate Part 1: Input Parameters (Design Space)"""
        print("Generating Input Parameters (Design Space)...")
        
        # Base Materials
        anode_materials = np.random.choice(self.materials['anode'], self.n_samples)
        cathode_materials = np.random.choice(self.materials['cathode'], self.n_samples)
        
        # Tab thickness (realistic range for battery applications)
        tab_thickness = np.random.lognormal(mean=np.log(150), sigma=0.4, size=self.n_samples)
        tab_thickness = np.clip(tab_thickness, 50, 500)  # 50-500 µm
        
        # Surface finish/coating
        surface_coating = np.random.choice(self.materials['coatings'], self.n_samples)
        
        # Welding technique
        welding_technique = np.random.choice(self.materials['techniques'], self.n_samples)
        
        # Generate technique-specific parameters
        power = np.zeros(self.n_samples)
        amplitude = np.zeros(self.n_samples)
        force = np.zeros(self.n_samples)
        time = np.zeros(self.n_samples)
        speed = np.zeros(self.n_samples)
        pulse_frequency = np.zeros(self.n_samples)
        
        for i, technique in enumerate(welding_technique):
            if technique == 'USW':  # Ultrasonic Welding
                power[i] = np.random.uniform(500, 3000)  # W
                amplitude[i] = np.random.uniform(10, 50)  # µm
                force[i] = np.random.uniform(200, 2000)  # N
                time[i] = np.random.uniform(0.1, 2.0)  # s
                speed[i] = 0  # Not applicable
                pulse_frequency[i] = np.random.uniform(15000, 40000)  # Hz
                
            elif technique == 'Laser':
                power[i] = np.random.uniform(100, 2000)  # W
                amplitude[i] = 0  # Not applicable
                force[i] = 0  # Not applicable for laser
                time[i] = np.random.uniform(0.001, 0.1)  # s (pulse duration)
                speed[i] = np.random.uniform(10, 200)  # mm/s
                pulse_frequency[i] = np.random.uniform(1, 10000)  # Hz
                
            elif technique == 'RSW':  # Resistance Spot Welding
                power[i] = np.random.uniform(1000, 8000)  # W
                amplitude[i] = 0  # Not applicable
                force[i] = np.random.uniform(1000, 5000)  # N
                time[i] = np.random.uniform(0.1, 1.0)  # s
                speed[i] = 0  # Not applicable
                pulse_frequency[i] = 50  # AC frequency
                
            elif technique == 'TIG':  # Tungsten Inert Gas
                power[i] = np.random.uniform(50, 300)  # W
                amplitude[i] = 0  # Not applicable
                force[i] = 0  # Not applicable
                time[i] = np.random.uniform(1, 10)  # s
                speed[i] = np.random.uniform(1, 10)  # mm/s
                pulse_frequency[i] = np.random.uniform(0.5, 200)  # Hz
                
            elif technique == 'Friction':
                power[i] = np.random.uniform(500, 2000)  # W
                amplitude[i] = np.random.uniform(0.1, 2.0)  # mm
                force[i] = np.random.uniform(500, 3000)  # N
                time[i] = np.random.uniform(0.5, 5.0)  # s
                speed[i] = np.random.uniform(100, 3000)  # rpm (converted to mm/s equivalent)
                pulse_frequency[i] = 0  # Not applicable
        
        # Environmental conditions
        preheat_temp = np.random.normal(25, 15, self.n_samples)  # °C
        preheat_temp = np.clip(preheat_temp, -10, 80)
        
        # Ambient conditions
        humidity = np.random.uniform(20, 80, self.n_samples)  # %
        atmospheric_pressure = np.random.normal(101325, 5000, self.n_samples)  # Pa
        
        # Store input parameters
        self.data['input_params'] = pd.DataFrame({
            'anode_material': anode_materials,
            'cathode_material': cathode_materials,
            'tab_thickness_um': tab_thickness,
            'surface_coating': surface_coating,
            'welding_technique': welding_technique,
            'power_W': power,
            'amplitude_um': amplitude,
            'force_N': force,
            'time_s': time,
            'speed_mm_s': speed,
            'pulse_frequency_Hz': pulse_frequency,
            'preheat_temp_C': preheat_temp,
            'humidity_percent': humidity,
            'atmospheric_pressure_Pa': atmospheric_pressure
        })
        
        print(f"Generated {self.n_samples} input parameter combinations")
        return self.data['input_params']
    
    def generate_characterization_metrics(self):
        """Generate Part 2: Characterization & Quality Metrics (Forward Problem)"""
        print("Generating Characterization & Quality Metrics...")
        
        if 'input_params' not in self.data:
            raise ValueError("Input parameters must be generated first")
        
        df = self.data['input_params'].copy()
        n = len(df)
        
        # Initialize arrays for quality metrics
        weld_strength = np.zeros(n)
        electrical_resistance = np.zeros(n)
        weld_area = np.zeros(n)
        heat_affected_zone = np.zeros(n)
        porosity = np.zeros(n)
        surface_roughness = np.zeros(n)
        microhardness = np.zeros(n)
        grain_size = np.zeros(n)
        
        # Calculate physics-based relationships
        for i in range(n):
            # Get material properties
            anode_props = self.material_properties[df.iloc[i]['anode_material']]
            cathode_props = self.material_properties[df.iloc[i]['cathode_material']]
            
            # Calculate energy density
            if df.iloc[i]['welding_technique'] in ['USW', 'RSW', 'TIG', 'Friction']:
                energy_density = df.iloc[i]['power_W'] * df.iloc[i]['time_s'] / (df.iloc[i]['tab_thickness_um'] / 1000)
            else:  # Laser
                energy_density = df.iloc[i]['power_W'] / df.iloc[i]['speed_mm_s'] if df.iloc[i]['speed_mm_s'] > 0 else 0
            
            # Weld strength (MPa) - depends on materials, energy, and force
            base_strength = min(anode_props['hardness'], cathode_props['hardness']) * 0.3
            energy_factor = 1 + np.tanh((energy_density - 1000) / 500) * 0.5
            force_factor = 1 + np.tanh((df.iloc[i]['force_N'] - 1000) / 500) * 0.3
            coating_factor = 1.2 if df.iloc[i]['surface_coating'] != 'None' else 1.0
            
            weld_strength[i] = base_strength * energy_factor * force_factor * coating_factor
            weld_strength[i] *= np.random.normal(1, 0.1)  # Add noise
            weld_strength[i] = max(10, weld_strength[i])  # Minimum strength
            
            # Electrical resistance (µΩ) - depends on materials and weld quality
            base_resistance = (1/anode_props['conductivity'] + 1/cathode_props['conductivity']) * 1000
            thickness_factor = df.iloc[i]['tab_thickness_um'] / 150  # Normalized to 150µm
            quality_factor = 1 / (weld_strength[i] / 100)  # Better welds have lower resistance
            
            electrical_resistance[i] = base_resistance * thickness_factor * quality_factor
            electrical_resistance[i] *= np.random.normal(1, 0.15)  # Add noise
            electrical_resistance[i] = max(1, electrical_resistance[i])
            
            # Weld area (mm²) - depends on energy and force
            if df.iloc[i]['welding_technique'] == 'Laser':
                weld_area[i] = np.pi * (0.1 + energy_density / 10000)**2
            else:
                weld_area[i] = np.pi * (0.5 + df.iloc[i]['force_N'] / 2000)**2
            weld_area[i] *= np.random.normal(1, 0.1)
            weld_area[i] = max(0.1, weld_area[i])
            
            # Heat Affected Zone (mm) - depends on energy input and thermal properties
            thermal_diffusivity = (anode_props['conductivity'] + cathode_props['conductivity']) / 2
            haz_base = np.sqrt(energy_density / thermal_diffusivity) * 0.01
            heat_affected_zone[i] = max(0.1, haz_base * np.random.normal(1, 0.2))
            
            # Porosity (%) - inversely related to weld quality
            porosity_base = max(0, 10 - weld_strength[i] / 50)
            porosity[i] = max(0, porosity_base * np.random.normal(1, 0.3))
            
            # Surface roughness (µm Ra) - depends on technique and parameters
            if df.iloc[i]['welding_technique'] == 'Laser':
                surface_roughness[i] = 0.5 + df.iloc[i]['speed_mm_s'] / 100
            elif df.iloc[i]['welding_technique'] == 'USW':
                surface_roughness[i] = 1.0 + df.iloc[i]['amplitude_um'] / 25
            else:
                surface_roughness[i] = 2.0 + np.random.uniform(-1, 1)
            surface_roughness[i] *= np.random.normal(1, 0.2)
            surface_roughness[i] = max(0.1, surface_roughness[i])
            
            # Microhardness (HV) - related to materials and heat treatment
            base_hardness = (anode_props['hardness'] + cathode_props['hardness']) / 2
            heat_treatment_factor = 1 + (energy_density - 1000) / 5000
            microhardness[i] = base_hardness * heat_treatment_factor * np.random.normal(1, 0.1)
            microhardness[i] = max(100, microhardness[i])
            
            # Grain size (µm) - inversely related to cooling rate
            cooling_rate = energy_density / (df.iloc[i]['time_s'] * 1000)
            grain_size[i] = 50 / np.sqrt(cooling_rate + 1) * np.random.normal(1, 0.2)
            grain_size[i] = max(1, grain_size[i])
        
        # Store characterization metrics
        self.data['characterization'] = pd.DataFrame({
            'weld_strength_MPa': weld_strength,
            'electrical_resistance_uOhm': electrical_resistance,
            'weld_area_mm2': weld_area,
            'heat_affected_zone_mm': heat_affected_zone,
            'porosity_percent': porosity,
            'surface_roughness_um': surface_roughness,
            'microhardness_HV': microhardness,
            'grain_size_um': grain_size,
            'energy_density_J_mm3': [df.iloc[i]['power_W'] * df.iloc[i]['time_s'] / (df.iloc[i]['tab_thickness_um'] / 1000) 
                                   if df.iloc[i]['welding_technique'] != 'Laser' 
                                   else df.iloc[i]['power_W'] / max(df.iloc[i]['speed_mm_s'], 0.1) 
                                   for i in range(n)]
        })
        
        print(f"Generated characterization metrics for {n} samples")
        return self.data['characterization']
    
    def generate_performance_metrics(self):
        """Generate Part 3: Performance & Validation Metrics (Inverse Design Targets)"""
        print("Generating Performance & Validation Metrics...")
        
        if 'characterization' not in self.data:
            raise ValueError("Characterization metrics must be generated first")
        
        df_input = self.data['input_params'].copy()
        df_char = self.data['characterization'].copy()
        n = len(df_input)
        
        # Temperature cycling parameters
        min_temp = np.random.uniform(-40, -20, n)  # °C
        max_temp = np.random.uniform(80, 150, n)   # °C
        cycle_count = np.random.randint(100, 10000, n)
        
        # Initialize performance arrays
        thermal_fatigue_life = np.zeros(n)
        resistance_drift = np.zeros(n)
        mechanical_degradation = np.zeros(n)
        crack_propagation_rate = np.zeros(n)
        thermal_shock_resistance = np.zeros(n)
        long_term_reliability = np.zeros(n)
        
        for i in range(n):
            # Get material properties
            anode_props = self.material_properties[df_input.iloc[i]['anode_material']]
            cathode_props = self.material_properties[df_input.iloc[i]['cathode_material']]
            
            # Temperature range stress
            temp_range = max_temp[i] - min_temp[i]
            thermal_stress = temp_range * abs(anode_props['density'] - cathode_props['density']) / 10
            
            # Thermal fatigue life (cycles to failure)
            base_fatigue = df_char.iloc[i]['weld_strength_MPa'] * 1000
            stress_factor = 1 / (1 + thermal_stress / 100)
            porosity_factor = 1 / (1 + df_char.iloc[i]['porosity_percent'] / 10)
            microstructure_factor = 100 / df_char.iloc[i]['grain_size_um']
            
            thermal_fatigue_life[i] = base_fatigue * stress_factor * porosity_factor * microstructure_factor
            thermal_fatigue_life[i] *= np.random.lognormal(0, 0.3)  # Log-normal distribution for fatigue
            thermal_fatigue_life[i] = max(100, thermal_fatigue_life[i])
            
            # Resistance drift (% change after cycling)
            base_drift = df_char.iloc[i]['electrical_resistance_uOhm'] / 100
            cycle_factor = np.log(cycle_count[i]) / 10
            quality_factor = df_char.iloc[i]['porosity_percent'] / 10
            
            resistance_drift[i] = (base_drift + cycle_factor + quality_factor) * np.random.normal(1, 0.2)
            resistance_drift[i] = max(0.1, resistance_drift[i])
            
            # Mechanical degradation (% strength loss)
            degradation_rate = (thermal_stress / 100) * (cycle_count[i] / 1000)
            mechanical_degradation[i] = degradation_rate * np.random.normal(1, 0.3)
            mechanical_degradation[i] = np.clip(mechanical_degradation[i], 0, 80)
            
            # Crack propagation rate (mm/cycle)
            base_crack_rate = 1e-6 * (thermal_stress / df_char.iloc[i]['weld_strength_MPa'])
            haz_factor = df_char.iloc[i]['heat_affected_zone_mm']
            crack_propagation_rate[i] = base_crack_rate * haz_factor * np.random.lognormal(0, 0.5)
            crack_propagation_rate[i] = max(1e-9, crack_propagation_rate[i])
            
            # Thermal shock resistance (J/m²)
            toughness_base = df_char.iloc[i]['weld_strength_MPa'] * df_char.iloc[i]['weld_area_mm2']
            grain_factor = 50 / df_char.iloc[i]['grain_size_um']
            thermal_shock_resistance[i] = toughness_base * grain_factor * np.random.normal(1, 0.2)
            thermal_shock_resistance[i] = max(10, thermal_shock_resistance[i])
            
            # Long-term reliability score (0-100)
            strength_score = min(100, df_char.iloc[i]['weld_strength_MPa'] / 5)
            resistance_score = max(0, 100 - df_char.iloc[i]['electrical_resistance_uOhm'])
            porosity_score = max(0, 100 - df_char.iloc[i]['porosity_percent'] * 10)
            fatigue_score = min(100, thermal_fatigue_life[i] / 1000)
            
            long_term_reliability[i] = (strength_score + resistance_score + porosity_score + fatigue_score) / 4
            long_term_reliability[i] *= np.random.normal(1, 0.1)
            long_term_reliability[i] = np.clip(long_term_reliability[i], 0, 100)
        
        # Store performance metrics
        self.data['performance'] = pd.DataFrame({
            'min_temp_C': min_temp,
            'max_temp_C': max_temp,
            'cycle_count': cycle_count,
            'thermal_fatigue_life_cycles': thermal_fatigue_life,
            'resistance_drift_percent': resistance_drift,
            'mechanical_degradation_percent': mechanical_degradation,
            'crack_propagation_rate_mm_cycle': crack_propagation_rate,
            'thermal_shock_resistance_J_m2': thermal_shock_resistance,
            'long_term_reliability_score': long_term_reliability,
            'temperature_range_C': max_temp - min_temp
        })
        
        print(f"Generated performance metrics for {n} samples")
        return self.data['performance']
    
    def create_combined_dataset(self):
        """Combine all parts into a single comprehensive dataset"""
        print("Creating combined dataset...")
        
        if not all(key in self.data for key in ['input_params', 'characterization', 'performance']):
            raise ValueError("All dataset parts must be generated first")
        
        # Combine all dataframes
        combined_df = pd.concat([
            self.data['input_params'],
            self.data['characterization'],
            self.data['performance']
        ], axis=1)
        
        # Add derived features
        combined_df['material_mismatch'] = [
            abs(self.material_properties[row['anode_material']]['melting_point'] - 
                self.material_properties[row['cathode_material']]['melting_point'])
            for _, row in combined_df.iterrows()
        ]
        
        combined_df['conductivity_ratio'] = [
            self.material_properties[row['anode_material']]['conductivity'] / 
            self.material_properties[row['cathode_material']]['conductivity']
            for _, row in combined_df.iterrows()
        ]
        
        combined_df['density_mismatch'] = [
            abs(self.material_properties[row['anode_material']]['density'] - 
                self.material_properties[row['cathode_material']]['density'])
            for _, row in combined_df.iterrows()
        ]
        
        # Add quality classifications
        combined_df['weld_quality_class'] = pd.cut(
            combined_df['long_term_reliability_score'], 
            bins=[0, 30, 60, 80, 100], 
            labels=['Poor', 'Fair', 'Good', 'Excellent']
        )
        
        combined_df['thermal_performance_class'] = pd.cut(
            combined_df['thermal_fatigue_life_cycles'], 
            bins=[0, 1000, 10000, 100000, np.inf], 
            labels=['Low', 'Medium', 'High', 'Excellent']
        )
        
        self.data['combined'] = combined_df
        print(f"Created combined dataset with {len(combined_df)} samples and {len(combined_df.columns)} features")
        return combined_df
    
    def save_dataset(self, base_path="/workspace"):
        """Save the complete dataset to files"""
        print("Saving dataset files...")
        
        if 'combined' not in self.data:
            self.create_combined_dataset()
        
        # Save individual parts
        self.data['input_params'].to_csv(f"{base_path}/welding_input_parameters.csv", index=False)
        self.data['characterization'].to_csv(f"{base_path}/welding_characterization_metrics.csv", index=False)
        self.data['performance'].to_csv(f"{base_path}/welding_performance_metrics.csv", index=False)
        
        # Save combined dataset
        self.data['combined'].to_csv(f"{base_path}/welding_complete_dataset.csv", index=False)
        
        # Save as pickle for Python use
        self.data['combined'].to_pickle(f"{base_path}/welding_complete_dataset.pkl")
        
        print(f"Dataset saved to {base_path}/")
        return f"{base_path}/welding_complete_dataset.csv"

def main():
    """Main function to generate the complete dataset"""
    print("=== Welding Parameter Dataset Generator ===")
    print("Generating comprehensive dataset for ML-driven inverse design...")
    
    # Initialize generator with large sample size
    generator = WeldingDatasetGenerator(n_samples=15000)
    
    # Generate all parts
    generator.generate_input_parameters()
    generator.generate_characterization_metrics()
    generator.generate_performance_metrics()
    
    # Create and save combined dataset
    combined_df = generator.create_combined_dataset()
    dataset_path = generator.save_dataset()
    
    print("\n=== Dataset Summary ===")
    print(f"Total samples: {len(combined_df)}")
    print(f"Total features: {len(combined_df.columns)}")
    print(f"Dataset saved to: {dataset_path}")
    
    # Display basic statistics
    print("\n=== Key Statistics ===")
    print("Welding Techniques Distribution:")
    print(combined_df['welding_technique'].value_counts())
    
    print("\nWeld Quality Distribution:")
    print(combined_df['weld_quality_class'].value_counts())
    
    print("\nThermal Performance Distribution:")
    print(combined_df['thermal_performance_class'].value_counts())
    
    return generator, combined_df

if __name__ == "__main__":
    generator, dataset = main()