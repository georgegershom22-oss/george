import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

class EnhancedWeldingDatasetGenerator:
    def __init__(self, n_samples=50000):
        self.n_samples = n_samples
        self.rng = np.random.RandomState(42)
        
        # Extended material properties database
        self.materials = {
            'Cu': {'density': 8.96, 'thermal_conductivity': 400, 'melting_point': 1085, 
                   'electrical_conductivity': 5.96e7, 'yield_strength': 33, 'tensile_strength': 210,
                   'thermal_expansion': 16.5e-6, 'specific_heat': 385, 'hardness': 35},
            'Al': {'density': 2.70, 'thermal_conductivity': 237, 'melting_point': 660,
                   'electrical_conductivity': 3.77e7, 'yield_strength': 95, 'tensile_strength': 186,
                   'thermal_expansion': 23.1e-6, 'specific_heat': 900, 'hardness': 15},
            'Ni': {'density': 8.90, 'thermal_conductivity': 91, 'melting_point': 1455,
                   'electrical_conductivity': 1.43e7, 'yield_strength': 103, 'tensile_strength': 317,
                   'thermal_expansion': 13.4e-6, 'specific_heat': 444, 'hardness': 80},
            'Ti': {'density': 4.51, 'thermal_conductivity': 22, 'melting_point': 1668,
                   'electrical_conductivity': 0.56e7, 'yield_strength': 880, 'tensile_strength': 950,
                   'thermal_expansion': 8.6e-6, 'specific_heat': 523, 'hardness': 200},
            'Steel': {'density': 7.85, 'thermal_conductivity': 50, 'melting_point': 1500,
                      'electrical_conductivity': 1.0e7, 'yield_strength': 250, 'tensile_strength': 400,
                      'thermal_expansion': 12.0e-6, 'specific_heat': 460, 'hardness': 120},
            'Ag': {'density': 10.49, 'thermal_conductivity': 429, 'melting_point': 962,
                   'electrical_conductivity': 6.30e7, 'yield_strength': 55, 'tensile_strength': 125,
                   'thermal_expansion': 18.9e-6, 'specific_heat': 235, 'hardness': 25},
            'Au': {'density': 19.32, 'thermal_conductivity': 317, 'melting_point': 1064,
                   'electrical_conductivity': 4.52e7, 'yield_strength': 95, 'tensile_strength': 130,
                   'thermal_expansion': 14.2e-6, 'specific_heat': 129, 'hardness': 20},
            'Zn': {'density': 7.13, 'thermal_conductivity': 116, 'melting_point': 420,
                   'electrical_conductivity': 1.69e7, 'yield_strength': 28, 'tensile_strength': 37,
                   'thermal_expansion': 30.2e-6, 'specific_heat': 388, 'hardness': 30}
        }
        
        # Welding techniques with more details
        self.welding_techniques = ['USW', 'Laser', 'Resistance_Spot', 'Friction_Stir', 'Electron_Beam', 
                                 'TIG', 'MIG', 'Plasma', 'Ultrasonic_Spot', 'Diffusion_Bonding']
        
        # Surface finishes with properties
        self.surface_finishes = {
            'Polished': {'roughness': 0.1, 'contact_resistance_factor': 0.8, 'cost_factor': 1.2},
            'Rough': {'roughness': 2.0, 'contact_resistance_factor': 1.2, 'cost_factor': 0.8},
            'Coated': {'roughness': 0.5, 'contact_resistance_factor': 1.5, 'cost_factor': 1.5},
            'Anodized': {'roughness': 1.0, 'contact_resistance_factor': 2.0, 'cost_factor': 2.0},
            'Plated': {'roughness': 0.3, 'contact_resistance_factor': 1.1, 'cost_factor': 1.3},
            'Etched': {'roughness': 1.5, 'contact_resistance_factor': 1.4, 'cost_factor': 1.1},
            'Passivated': {'roughness': 0.8, 'contact_resistance_factor': 1.3, 'cost_factor': 1.4}
        }
        
        # Environmental conditions
        self.environments = ['Clean_Room', 'Laboratory', 'Factory_Floor', 'Outdoor', 'Controlled_Atmosphere']
        
    def generate_input_parameters(self):
        """Generate comprehensive input parameters for the welding process"""
        data = {}
        
        # Base Materials
        data['anode_material'] = self.rng.choice(list(self.materials.keys()), self.n_samples)
        data['cathode_material'] = self.rng.choice(list(self.materials.keys()), self.n_samples)
        data['tab_thickness_um'] = self.rng.normal(100, 20, self.n_samples).clip(50, 200)
        data['surface_finish'] = self.rng.choice(list(self.surface_finishes.keys()), self.n_samples)
        
        # Welding Process Parameters
        data['welding_technique'] = self.rng.choice(self.welding_techniques, self.n_samples)
        
        # Power parameters (technique-dependent with more realistic distributions)
        power_data = []
        for technique in data['welding_technique']:
            if technique == 'USW':
                power_data.append(self.rng.normal(2000, 500, 1)[0])
            elif technique == 'Laser':
                power_data.append(self.rng.normal(500, 100, 1)[0])
            elif technique == 'Resistance_Spot':
                power_data.append(self.rng.normal(3000, 800, 1)[0])
            elif technique == 'Friction_Stir':
                power_data.append(self.rng.normal(1500, 300, 1)[0])
            elif technique == 'Electron_Beam':
                power_data.append(self.rng.normal(800, 200, 1)[0])
            elif technique == 'TIG':
                power_data.append(self.rng.normal(200, 50, 1)[0])
            elif technique == 'MIG':
                power_data.append(self.rng.normal(400, 100, 1)[0])
            elif technique == 'Plasma':
                power_data.append(self.rng.normal(600, 150, 1)[0])
            elif technique == 'Ultrasonic_Spot':
                power_data.append(self.rng.normal(1000, 200, 1)[0])
            else:  # Diffusion_Bonding
                power_data.append(self.rng.normal(50, 10, 1)[0])
        data['power_w'] = np.array(power_data)
        
        # Technique-specific parameters
        data['amplitude_um'] = np.where(data['welding_technique'] == 'USW', 
                                      self.rng.normal(25, 5, self.n_samples).clip(10, 50),
                                      np.nan)
        
        data['force_n'] = self.rng.normal(500, 100, self.n_samples).clip(200, 1000)
        data['pressure_mpa'] = data['force_n'] / (np.pi * (2.5**2))
        
        # Time parameters with technique-specific ranges
        time_data = []
        for technique in data['welding_technique']:
            if technique in ['USW', 'Resistance_Spot', 'Ultrasonic_Spot']:
                time_data.append(self.rng.normal(100, 20, 1)[0])  # ms
            elif technique in ['Laser', 'Electron_Beam', 'TIG', 'MIG', 'Plasma']:
                time_data.append(self.rng.normal(50, 10, 1)[0])   # ms
            elif technique == 'Friction_Stir':
                time_data.append(self.rng.normal(500, 100, 1)[0]) # ms
            else:  # Diffusion_Bonding
                time_data.append(self.rng.normal(3600000, 600000, 1)[0]) # ms (1 hour)
        data['weld_time_ms'] = np.array(time_data)
        data['weld_time_s'] = data['weld_time_ms'] / 1000
        
        # Speed parameters
        data['speed_mm_s'] = np.where(data['welding_technique'].isin(['Laser', 'TIG', 'MIG', 'Plasma']),
                                    self.rng.normal(10, 2, self.n_samples).clip(5, 20),
                                    np.nan)
        
        # Pulse parameters
        data['pulse_frequency_hz'] = np.where(data['welding_technique'].isin(['Laser', 'TIG', 'MIG']),
                                            self.rng.normal(1000, 200, self.n_samples).clip(500, 2000),
                                            np.nan)
        
        # Environmental conditions
        data['preheat_temp_c'] = self.rng.normal(25, 10, self.n_samples).clip(20, 100)
        data['environment'] = self.rng.choice(self.environments, self.n_samples)
        data['humidity_percent'] = self.rng.normal(45, 15, self.n_samples).clip(20, 80)
        data['atmospheric_pressure_kpa'] = self.rng.normal(101.3, 5, self.n_samples).clip(95, 110)
        
        # Additional process parameters
        data['weld_angle_deg'] = self.rng.normal(90, 10, self.n_samples).clip(60, 120)
        data['weld_position'] = self.rng.choice(['Flat', 'Horizontal', 'Vertical', 'Overhead'], self.n_samples)
        data['shielding_gas'] = self.rng.choice(['Argon', 'Helium', 'CO2', 'Nitrogen', 'None'], self.n_samples)
        data['filler_material'] = self.rng.choice(['Same_as_Base', 'Different_Alloy', 'None'], self.n_samples)
        
        return pd.DataFrame(data)
    
    def calculate_quality_metrics(self, input_df):
        """Calculate comprehensive quality metrics"""
        quality_data = {}
        
        # Get material properties
        anode_props = [self.materials[mat] for mat in input_df['anode_material']]
        cathode_props = [self.materials[mat] for mat in input_df['cathode_material']]
        
        # Weld strength (MPa) - enhanced calculation
        base_strength = np.array([min(anode['tensile_strength'], cathode['tensile_strength']) 
                                for anode, cathode in zip(anode_props, cathode_props)])
        
        technique_multiplier = {
            'USW': 0.8, 'Laser': 0.9, 'Resistance_Spot': 0.7, 'Friction_Stir': 0.95, 
            'Electron_Beam': 0.85, 'TIG': 0.88, 'MIG': 0.82, 'Plasma': 0.87,
            'Ultrasonic_Spot': 0.75, 'Diffusion_Bonding': 0.98
        }
        
        strength_multiplier = np.array([technique_multiplier[tech] for tech in input_df['welding_technique']])
        force_factor = (input_df['force_n'] / 500) ** 0.3
        quality_data['weld_strength_mpa'] = base_strength * strength_multiplier * force_factor * (1 + 0.1 * np.random.normal(0, 1, self.n_samples))
        
        # Contact resistance (mOhm) - enhanced calculation
        base_resistance = np.array([1 / (anode['electrical_conductivity'] + cathode['electrical_conductivity']) 
                                  for anode, cathode in zip(anode_props, cathode_props)]) * 1e6
        
        surface_factors = [self.surface_finishes[finish]['contact_resistance_factor'] for finish in input_df['surface_finish']]
        quality_data['contact_resistance_mohm'] = base_resistance * surface_factors * (1 + 0.2 * np.random.normal(0, 1, self.n_samples))
        
        # Weld geometry - enhanced calculations
        width_data = []
        depth_data = []
        for i, technique in enumerate(input_df['welding_technique']):
            if technique == 'USW':
                width = 2.0 + 0.1 * input_df['amplitude_um'].iloc[i] + 0.01 * input_df['weld_time_ms'].iloc[i]
                depth = 0.5 + 0.02 * input_df['amplitude_um'].iloc[i] + 0.005 * input_df['weld_time_ms'].iloc[i]
            elif technique == 'Laser':
                width = 1.5 + 0.05 * input_df['power_w'].iloc[i] + 0.02 * input_df['speed_mm_s'].iloc[i]
                depth = 0.3 + 0.01 * input_df['power_w'].iloc[i] + 0.005 * input_df['speed_mm_s'].iloc[i]
            elif technique == 'Resistance_Spot':
                width = 3.0 + 0.02 * input_df['force_n'].iloc[i] + 0.01 * input_df['weld_time_ms'].iloc[i]
                depth = 0.8 + 0.01 * input_df['force_n'].iloc[i] + 0.005 * input_df['weld_time_ms'].iloc[i]
            elif technique == 'Friction_Stir':
                width = 4.0 + 0.01 * input_df['power_w'].iloc[i] + 0.02 * input_df['weld_time_ms'].iloc[i]
                depth = 1.0 + 0.005 * input_df['power_w'].iloc[i] + 0.01 * input_df['weld_time_ms'].iloc[i]
            elif technique == 'Electron_Beam':
                width = 1.0 + 0.03 * input_df['power_w'].iloc[i] + 0.01 * input_df['weld_time_ms'].iloc[i]
                depth = 0.2 + 0.01 * input_df['power_w'].iloc[i] + 0.005 * input_df['weld_time_ms'].iloc[i]
            elif technique in ['TIG', 'MIG', 'Plasma']:
                width = 2.5 + 0.03 * input_df['power_w'].iloc[i] + 0.02 * input_df['speed_mm_s'].iloc[i]
                depth = 0.6 + 0.01 * input_df['power_w'].iloc[i] + 0.005 * input_df['speed_mm_s'].iloc[i]
            elif technique == 'Ultrasonic_Spot':
                width = 1.8 + 0.08 * input_df['amplitude_um'].iloc[i] + 0.01 * input_df['weld_time_ms'].iloc[i]
                depth = 0.4 + 0.015 * input_df['amplitude_um'].iloc[i] + 0.003 * input_df['weld_time_ms'].iloc[i]
            else:  # Diffusion_Bonding
                width = 5.0 + 0.01 * input_df['power_w'].iloc[i] + 0.001 * input_df['weld_time_ms'].iloc[i]
                depth = 2.0 + 0.005 * input_df['power_w'].iloc[i] + 0.0005 * input_df['weld_time_ms'].iloc[i]
            width_data.append(width)
            depth_data.append(depth)
        
        quality_data['weld_width_mm'] = np.array(width_data)
        quality_data['weld_depth_mm'] = np.array(depth_data)
        
        # Porosity percentage - enhanced calculation
        base_porosity = np.random.normal(2, 1, self.n_samples).clip(0, 10)
        technique_porosity = {
            'USW': 0.8, 'Laser': 0.6, 'Resistance_Spot': 1.2, 'Friction_Stir': 0.4, 
            'Electron_Beam': 0.5, 'TIG': 0.7, 'MIG': 0.9, 'Plasma': 0.8,
            'Ultrasonic_Spot': 0.6, 'Diffusion_Bonding': 0.2
        }
        porosity_multiplier = np.array([technique_porosity[tech] for tech in input_df['welding_technique']])
        environmental_factor = 1 + 0.1 * input_df['preheat_temp_c'] / 100 + 0.05 * input_df['humidity_percent'] / 100
        quality_data['porosity_percent'] = base_porosity * porosity_multiplier * environmental_factor
        
        # Microhardness (HV) - enhanced calculation
        base_hardness = np.array([(anode['hardness'] + cathode['hardness']) / 2 
                                for anode, cathode in zip(anode_props, cathode_props)])
        
        process_hardness = input_df['force_n'] * 0.1 + input_df['power_w'] * 0.05
        quality_data['microhardness_hv'] = base_hardness + process_hardness + np.random.normal(0, 10, self.n_samples)
        
        # Additional quality metrics
        quality_data['weld_penetration_ratio'] = quality_data['weld_depth_mm'] / input_df['tab_thickness_um'] * 1000
        quality_data['weld_aspect_ratio'] = quality_data['weld_width_mm'] / quality_data['weld_depth_mm']
        quality_data['weld_volume_mm3'] = np.pi * (quality_data['weld_width_mm'] / 2) ** 2 * quality_data['weld_depth_mm']
        
        # Weld efficiency - comprehensive calculation
        strength_factor = quality_data['weld_strength_mpa'] / 1000
        resistance_factor = 1 / quality_data['contact_resistance_mohm']
        porosity_factor = 1 / (quality_data['porosity_percent'] + 0.1)
        efficiency = strength_factor * resistance_factor * porosity_factor * 100
        quality_data['weld_efficiency_percent'] = np.clip(efficiency, 0, 100)
        
        return pd.DataFrame(quality_data)
    
    def calculate_performance_metrics(self, input_df, quality_df):
        """Calculate comprehensive performance metrics under extreme conditions"""
        performance_data = {}
        
        # Thermal cycling parameters
        n_cycles = self.rng.normal(1000, 200, self.n_samples).clip(500, 2000)
        temp_range = self.rng.normal(150, 30, self.n_samples).clip(100, 250)
        max_temp = self.rng.normal(200, 50, self.n_samples).clip(150, 300)
        min_temp = max_temp - temp_range
        
        # Fatigue life (cycles) - enhanced calculation
        base_fatigue = np.array([min(anode['tensile_strength'], cathode['tensile_strength']) 
                               for anode, cathode in zip([self.materials[mat] for mat in input_df['anode_material']],
                                                       [self.materials[mat] for mat in input_df['cathode_material']])]) / 10
        
        quality_factor = quality_df['weld_efficiency_percent'] / 100
        thermal_factor = 1 / (1 + temp_range / 200)
        material_factor = np.array([min(anode['thermal_conductivity'], cathode['thermal_conductivity']) 
                                  for anode, cathode in zip([self.materials[mat] for mat in input_df['anode_material']],
                                                          [self.materials[mat] for mat in input_df['cathode_material']])]) / 400
        
        performance_data['fatigue_life_cycles'] = base_fatigue * quality_factor * thermal_factor * material_factor * (1 + 0.3 * np.random.normal(0, 1, self.n_samples))
        
        # Thermal resistance degradation (%)
        base_degradation = temp_range * 0.1 + n_cycles * 0.001
        material_factor = np.array([1 / (anode['thermal_conductivity'] + cathode['thermal_conductivity']) 
                                  for anode, cathode in zip([self.materials[mat] for mat in input_df['anode_material']],
                                                          [self.materials[mat] for mat in input_df['cathode_material']])]) * 1000
        
        performance_data['thermal_resistance_degradation_percent'] = base_degradation * material_factor * (1 + 0.2 * np.random.normal(0, 1, self.n_samples))
        
        # Electrical resistance increase (%)
        base_increase = temp_range * 0.05 + n_cycles * 0.0005
        surface_factors = [self.surface_finishes[finish]['contact_resistance_factor'] for finish in input_df['surface_finish']]
        performance_data['electrical_resistance_increase_percent'] = base_increase * surface_factors * (1 + 0.15 * np.random.normal(0, 1, self.n_samples))
        
        # Additional performance metrics
        performance_data['thermal_cycling_stress_mpa'] = temp_range * 10 + np.random.normal(0, 5, self.n_samples)
        performance_data['creep_deformation_mm'] = n_cycles * 0.001 + temp_range * 0.01 + np.random.normal(0, 0.1, self.n_samples)
        performance_data['oxidation_rate_mg_cm2_h'] = temp_range * 0.1 + np.random.normal(0, 0.5, self.n_samples)
        
        # Weld integrity score (0-100) - comprehensive calculation
        integrity = (quality_df['weld_efficiency_percent'] * 0.3 + 
                    (100 - performance_data['thermal_resistance_degradation_percent']) * 0.25 +
                    (100 - performance_data['electrical_resistance_increase_percent']) * 0.25 +
                    (100 - performance_data['creep_deformation_mm'] * 100) * 0.2)
        performance_data['weld_integrity_score'] = np.clip(integrity, 0, 100)
        
        # Failure mode prediction - enhanced
        failure_modes = []
        for i in range(self.n_samples):
            if performance_data['fatigue_life_cycles'][i] < 500:
                failure_modes.append('Fatigue')
            elif performance_data['thermal_resistance_degradation_percent'][i] > 50:
                failure_modes.append('Thermal')
            elif performance_data['electrical_resistance_increase_percent'][i] > 30:
                failure_modes.append('Electrical')
            elif performance_data['creep_deformation_mm'][i] > 0.5:
                failure_modes.append('Creep')
            elif performance_data['oxidation_rate_mg_cm2_h'][i] > 10:
                failure_modes.append('Oxidation')
            else:
                failure_modes.append('None')
        
        performance_data['predicted_failure_mode'] = failure_modes
        
        # Cost analysis
        technique_costs = {
            'USW': 1.0, 'Laser': 2.5, 'Resistance_Spot': 0.8, 'Friction_Stir': 3.0, 
            'Electron_Beam': 4.0, 'TIG': 1.5, 'MIG': 1.2, 'Plasma': 2.0,
            'Ultrasonic_Spot': 1.1, 'Diffusion_Bonding': 5.0
        }
        base_cost = np.array([technique_costs[tech] for tech in input_df['welding_technique']])
        material_cost = np.array([(anode['density'] + cathode['density']) / 2 
                                for anode, cathode in zip([self.materials[mat] for mat in input_df['anode_material']],
                                                        [self.materials[mat] for mat in input_df['cathode_material']])]) / 10
        surface_cost = np.array([self.surface_finishes[finish]['cost_factor'] for finish in input_df['surface_finish']])
        
        performance_data['estimated_cost_per_weld'] = base_cost * material_cost * surface_cost * (1 + 0.2 * np.random.normal(0, 1, self.n_samples))
        
        return pd.DataFrame(performance_data)
    
    def generate_complete_dataset(self):
        """Generate the complete enhanced welding dataset"""
        print("Generating enhanced input parameters...")
        input_df = self.generate_input_parameters()
        
        print("Calculating enhanced quality metrics...")
        quality_df = self.calculate_quality_metrics(input_df)
        
        print("Calculating enhanced performance metrics...")
        performance_df = self.calculate_performance_metrics(input_df, quality_df)
        
        # Combine all data
        complete_df = pd.concat([input_df, quality_df, performance_df], axis=1)
        
        return complete_df
    
    def save_dataset(self, df, filename='enhanced_welding_dataset.csv'):
        """Save the dataset to CSV"""
        df.to_csv(filename, index=False)
        print(f"Enhanced dataset saved to {filename}")
        return filename
    
    def generate_comprehensive_visualizations(self, df):
        """Generate comprehensive visualizations for the dataset"""
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(3, 4, figsize=(24, 18))
        
        # Weld strength distribution
        axes[0, 0].hist(df['weld_strength_mpa'], bins=50, alpha=0.7, color='skyblue')
        axes[0, 0].set_title('Weld Strength Distribution')
        axes[0, 0].set_xlabel('Strength (MPa)')
        axes[0, 0].set_ylabel('Frequency')
        
        # Contact resistance vs technique
        technique_resistance = df.groupby('welding_technique')['contact_resistance_mohm'].mean()
        axes[0, 1].bar(technique_resistance.index, technique_resistance.values, color='lightcoral')
        axes[0, 1].set_title('Average Contact Resistance by Technique')
        axes[0, 1].set_ylabel('Resistance (mOhm)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Weld efficiency vs technique
        technique_efficiency = df.groupby('welding_technique')['weld_efficiency_percent'].mean()
        axes[0, 2].bar(technique_efficiency.index, technique_efficiency.values, color='lightgreen')
        axes[0, 2].set_title('Average Weld Efficiency by Technique')
        axes[0, 2].set_ylabel('Efficiency (%)')
        axes[0, 2].tick_params(axis='x', rotation=45)
        
        # Material combination analysis
        material_combinations = df.groupby(['anode_material', 'cathode_material'])['weld_strength_mpa'].mean().unstack()
        sns.heatmap(material_combinations, annot=True, fmt='.0f', cmap='viridis', ax=axes[0, 3])
        axes[0, 3].set_title('Weld Strength by Material Combination')
        
        # Fatigue life distribution
        axes[1, 0].hist(df['fatigue_life_cycles'], bins=50, alpha=0.7, color='gold')
        axes[1, 0].set_title('Fatigue Life Distribution')
        axes[1, 0].set_xlabel('Cycles')
        axes[1, 0].set_ylabel('Frequency')
        
        # Thermal degradation vs technique
        technique_thermal = df.groupby('welding_technique')['thermal_resistance_degradation_percent'].mean()
        axes[1, 1].bar(technique_thermal.index, technique_thermal.values, color='orange')
        axes[1, 1].set_title('Average Thermal Degradation by Technique')
        axes[1, 1].set_ylabel('Degradation (%)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        # Weld integrity score distribution
        axes[1, 2].hist(df['weld_integrity_score'], bins=50, alpha=0.7, color='purple')
        axes[1, 2].set_title('Weld Integrity Score Distribution')
        axes[1, 2].set_xlabel('Integrity Score')
        axes[1, 2].set_ylabel('Frequency')
        
        # Failure mode distribution
        failure_counts = df['predicted_failure_mode'].value_counts()
        axes[1, 3].pie(failure_counts.values, labels=failure_counts.index, autopct='%1.1f%%')
        axes[1, 3].set_title('Predicted Failure Modes')
        
        # Cost analysis
        technique_cost = df.groupby('welding_technique')['estimated_cost_per_weld'].mean()
        axes[2, 0].bar(technique_cost.index, technique_cost.values, color='red')
        axes[2, 0].set_title('Average Cost per Weld by Technique')
        axes[2, 0].set_ylabel('Cost (relative units)')
        axes[2, 0].tick_params(axis='x', rotation=45)
        
        # Weld geometry analysis
        axes[2, 1].scatter(df['weld_width_mm'], df['weld_depth_mm'], alpha=0.6, c=df['weld_efficiency_percent'], cmap='viridis')
        axes[2, 1].set_title('Weld Geometry vs Efficiency')
        axes[2, 1].set_xlabel('Width (mm)')
        axes[2, 1].set_ylabel('Depth (mm)')
        
        # Environmental impact
        env_performance = df.groupby('environment')['weld_integrity_score'].mean()
        axes[2, 2].bar(env_performance.index, env_performance.values, color='green')
        axes[2, 2].set_title('Weld Integrity by Environment')
        axes[2, 2].set_ylabel('Integrity Score')
        axes[2, 2].tick_params(axis='x', rotation=45)
        
        # Correlation heatmap
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        corr_matrix = df[numeric_cols].corr()
        sns.heatmap(corr_matrix.iloc[:10, :10], annot=True, fmt='.2f', cmap='coolwarm', ax=axes[2, 3])
        axes[2, 3].set_title('Parameter Correlations')
        
        plt.tight_layout()
        plt.savefig('enhanced_welding_dataset_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("Enhanced visualizations saved to enhanced_welding_dataset_analysis.png")

def main():
    # Generate enhanced dataset
    generator = EnhancedWeldingDatasetGenerator(n_samples=50000)
    dataset = generator.generate_complete_dataset()
    
    # Save dataset
    filename = generator.save_dataset(dataset)
    
    # Generate visualizations
    generator.generate_comprehensive_visualizations(dataset)
    
    # Display comprehensive statistics
    print("\nEnhanced Dataset Statistics:")
    print(f"Total samples: {len(dataset)}")
    print(f"Total features: {len(dataset.columns)}")
    print("\nInput Parameters:")
    print(f"- Materials: {dataset['anode_material'].nunique()} anode, {dataset['cathode_material'].nunique()} cathode")
    print(f"- Techniques: {dataset['welding_technique'].nunique()}")
    print(f"- Surface finishes: {dataset['surface_finish'].nunique()}")
    print(f"- Environments: {dataset['environment'].nunique()}")
    
    print("\nQuality Metrics:")
    print(f"- Weld strength: {dataset['weld_strength_mpa'].mean():.1f} ± {dataset['weld_strength_mpa'].std():.1f} MPa")
    print(f"- Contact resistance: {dataset['contact_resistance_mohm'].mean():.2f} ± {dataset['contact_resistance_mohm'].std():.2f} mOhm")
    print(f"- Weld efficiency: {dataset['weld_efficiency_percent'].mean():.1f} ± {dataset['weld_efficiency_percent'].std():.1f}%")
    print(f"- Weld aspect ratio: {dataset['weld_aspect_ratio'].mean():.2f} ± {dataset['weld_aspect_ratio'].std():.2f}")
    
    print("\nPerformance Metrics:")
    print(f"- Fatigue life: {dataset['fatigue_life_cycles'].mean():.0f} ± {dataset['fatigue_life_cycles'].std():.0f} cycles")
    print(f"- Thermal degradation: {dataset['thermal_resistance_degradation_percent'].mean():.1f} ± {dataset['thermal_resistance_degradation_percent'].std():.1f}%")
    print(f"- Weld integrity: {dataset['weld_integrity_score'].mean():.1f} ± {dataset['weld_integrity_score'].std():.1f}")
    print(f"- Estimated cost: {dataset['estimated_cost_per_weld'].mean():.2f} ± {dataset['estimated_cost_per_weld'].std():.2f}")
    
    print(f"\nEnhanced dataset saved to: {filename}")
    return dataset

if __name__ == "__main__":
    dataset = main()