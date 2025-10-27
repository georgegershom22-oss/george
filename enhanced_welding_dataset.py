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
                                 'TIG', 'MIG', 'Plasma', 'Explosive', 'Diffusion_Bonding']
        
        # Surface finishes with properties
        self.surface_finishes = {
            'Polished': {'roughness': 0.1, 'contact_resistance_factor': 0.8, 'bondability': 0.9},
            'Rough': {'roughness': 2.0, 'contact_resistance_factor': 1.2, 'bondability': 0.7},
            'Coated': {'roughness': 0.5, 'contact_resistance_factor': 1.5, 'bondability': 0.8},
            'Anodized': {'roughness': 1.0, 'contact_resistance_factor': 2.0, 'bondability': 0.6},
            'Plated': {'roughness': 0.3, 'contact_resistance_factor': 1.1, 'bondability': 0.85},
            'Oxidized': {'roughness': 0.8, 'contact_resistance_factor': 1.8, 'bondability': 0.5},
            'Cleaned': {'roughness': 0.2, 'contact_resistance_factor': 0.9, 'bondability': 0.95}
        }
        
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
        
        # Power parameters (technique-dependent with realistic ranges)
        power_data = []
        for technique in data['welding_technique']:
            if technique == 'USW':
                power_data.append(self.rng.normal(2000, 500, 1)[0])  # W
            elif technique == 'Laser':
                power_data.append(self.rng.normal(500, 100, 1)[0])   # W
            elif technique == 'Resistance_Spot':
                power_data.append(self.rng.normal(3000, 800, 1)[0])  # W
            elif technique == 'Friction_Stir':
                power_data.append(self.rng.normal(1500, 300, 1)[0])  # W
            elif technique == 'Electron_Beam':
                power_data.append(self.rng.normal(800, 200, 1)[0])   # W
            elif technique == 'TIG':
                power_data.append(self.rng.normal(1200, 300, 1)[0])  # W
            elif technique == 'MIG':
                power_data.append(self.rng.normal(1800, 400, 1)[0])  # W
            elif technique == 'Plasma':
                power_data.append(self.rng.normal(600, 150, 1)[0])   # W
            elif technique == 'Explosive':
                power_data.append(self.rng.normal(5000, 1000, 1)[0]) # W
            else:  # Diffusion_Bonding
                power_data.append(self.rng.normal(200, 50, 1)[0])    # W
        data['power_w'] = np.array(power_data)
        
        # Amplitude (for USW)
        data['amplitude_um'] = np.where(data['welding_technique'] == 'USW', 
                                      self.rng.normal(25, 5, self.n_samples).clip(10, 50),
                                      np.nan)
        
        # Force/Pressure
        data['force_n'] = self.rng.normal(500, 100, self.n_samples).clip(200, 1000)
        data['pressure_mpa'] = data['force_n'] / (np.pi * (2.5**2))  # Assuming 5mm diameter
        
        # Time parameters
        data['weld_time_ms'] = self.rng.normal(100, 20, self.n_samples).clip(50, 300)
        data['weld_time_s'] = data['weld_time_ms'] / 1000
        
        # Speed (for Laser, TIG, MIG)
        speed_techniques = ['Laser', 'TIG', 'MIG', 'Plasma']
        data['speed_mm_s'] = np.where(np.isin(data['welding_technique'], speed_techniques),
                                    self.rng.normal(10, 2, self.n_samples).clip(5, 20),
                                    np.nan)
        
        # Pulse Frequency (for Laser, TIG, MIG)
        data['pulse_frequency_hz'] = np.where(np.isin(data['welding_technique'], speed_techniques),
                                            self.rng.normal(1000, 200, self.n_samples).clip(500, 2000),
                                            np.nan)
        
        # Environmental conditions
        data['preheat_temp_c'] = self.rng.normal(25, 10, self.n_samples).clip(20, 100)
        data['ambient_humidity_percent'] = self.rng.normal(45, 15, self.n_samples).clip(20, 80)
        data['ambient_pressure_kpa'] = self.rng.normal(101.3, 5, self.n_samples).clip(90, 110)
        
        # Additional process parameters
        data['weld_angle_degrees'] = self.rng.normal(90, 10, self.n_samples).clip(60, 120)
        data['electrode_diameter_mm'] = np.where(data['welding_technique'].isin(['TIG', 'MIG']),
                                               self.rng.normal(2.4, 0.5, self.n_samples).clip(1.0, 4.0),
                                               np.nan)
        data['shielding_gas_flow_lpm'] = np.where(data['welding_technique'].isin(['TIG', 'MIG', 'Plasma']),
                                                self.rng.normal(15, 3, self.n_samples).clip(8, 25),
                                                np.nan)
        
        # Material preparation parameters
        data['surface_roughness_um'] = np.array([self.surface_finishes[finish]['roughness'] 
                                                for finish in data['surface_finish']])
        data['cleaning_method'] = self.rng.choice(['Ultrasonic', 'Chemical', 'Mechanical', 'Plasma', 'None'], self.n_samples)
        data['pre_weld_heating_c'] = self.rng.normal(50, 20, self.n_samples).clip(20, 150)
        
        return pd.DataFrame(data)
    
    def calculate_quality_metrics(self, input_df):
        """Calculate comprehensive quality metrics based on input parameters"""
        quality_data = {}
        
        # Get material properties
        anode_props = [self.materials[mat] for mat in input_df['anode_material']]
        cathode_props = [self.materials[mat] for mat in input_df['cathode_material']]
        
        # Weld strength (MPa) - enhanced calculation
        base_strength = np.array([min(anode['tensile_strength'], cathode['tensile_strength']) 
                                for anode, cathode in zip(anode_props, cathode_props)])
        
        # Technique multiplier (more realistic)
        technique_multiplier = {
            'USW': 0.8, 'Laser': 0.9, 'Resistance_Spot': 0.7, 'Friction_Stir': 0.95, 
            'Electron_Beam': 0.85, 'TIG': 0.88, 'MIG': 0.82, 'Plasma': 0.75,
            'Explosive': 0.98, 'Diffusion_Bonding': 0.92
        }
        
        strength_multiplier = np.array([technique_multiplier[tech] for tech in input_df['welding_technique']])
        force_factor = (input_df['force_n'] / 500) ** 0.3
        time_factor = (input_df['weld_time_ms'] / 100) ** 0.2
        
        quality_data['weld_strength_mpa'] = (base_strength * strength_multiplier * force_factor * 
                                            time_factor * (1 + 0.1 * np.random.normal(0, 1, self.n_samples)))
        
        # Contact resistance (mOhm) - enhanced calculation
        base_resistance = np.array([1 / (anode['electrical_conductivity'] + cathode['electrical_conductivity']) 
                                  for anode, cathode in zip(anode_props, cathode_props)]) * 1e6
        
        surface_factors = np.array([self.surface_finishes[finish]['contact_resistance_factor'] 
                                  for finish in input_df['surface_finish']])
        
        # Add effect of cleaning method
        cleaning_factor = {'Ultrasonic': 0.9, 'Chemical': 0.95, 'Mechanical': 1.1, 'Plasma': 0.85, 'None': 1.2}
        cleaning_multiplier = np.array([cleaning_factor[method] for method in input_df['cleaning_method']])
        
        quality_data['contact_resistance_mohm'] = (base_resistance * surface_factors * cleaning_multiplier * 
                                                 (1 + 0.2 * np.random.normal(0, 1, self.n_samples)))
        
        # Weld geometry - enhanced calculations
        width_data = []
        depth_data = []
        for i, technique in enumerate(input_df['welding_technique']):
            if technique == 'USW':
                width = 2.0 + 0.1 * input_df['amplitude_um'].iloc[i] + 0.01 * input_df['weld_time_ms'].iloc[i]
                depth = 0.5 + 0.02 * input_df['amplitude_um'].iloc[i] + 0.005 * input_df['weld_time_ms'].iloc[i]
            elif technique in ['Laser', 'TIG', 'MIG', 'Plasma']:
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
            elif technique == 'Explosive':
                width = 5.0 + 0.1 * input_df['force_n'].iloc[i]
                depth = 2.0 + 0.05 * input_df['force_n'].iloc[i]
            else:  # Diffusion_Bonding
                width = 2.0 + 0.01 * input_df['power_w'].iloc[i] + 0.02 * input_df['weld_time_ms'].iloc[i]
                depth = 0.1 + 0.001 * input_df['power_w'].iloc[i] + 0.01 * input_df['weld_time_ms'].iloc[i]
            
            width_data.append(width)
            depth_data.append(depth)
        
        quality_data['weld_width_mm'] = np.array(width_data)
        quality_data['weld_depth_mm'] = np.array(depth_data)
        
        # Porosity percentage - enhanced calculation
        base_porosity = np.random.normal(2, 1, self.n_samples).clip(0, 10)
        technique_porosity = {
            'USW': 0.8, 'Laser': 0.6, 'Resistance_Spot': 1.2, 'Friction_Stir': 0.4, 
            'Electron_Beam': 0.5, 'TIG': 0.7, 'MIG': 0.9, 'Plasma': 0.8,
            'Explosive': 0.3, 'Diffusion_Bonding': 0.2
        }
        porosity_multiplier = np.array([technique_porosity[tech] for tech in input_df['welding_technique']])
        
        # Environmental effects
        humidity_factor = 1 + 0.01 * (input_df['ambient_humidity_percent'] - 45) / 45
        pressure_factor = 1 + 0.1 * (101.3 - input_df['ambient_pressure_kpa']) / 101.3
        
        quality_data['porosity_percent'] = (base_porosity * porosity_multiplier * humidity_factor * 
                                          pressure_factor * (1 + 0.1 * input_df['preheat_temp_c'] / 100))
        
        # Microhardness (HV) - enhanced calculation
        base_hardness = np.array([(anode['hardness'] + cathode['hardness']) / 2 
                                for anode, cathode in zip(anode_props, cathode_props)])
        
        process_hardness = input_df['force_n'] * 0.1 + input_df['power_w'] * 0.05
        preheat_factor = 1 - 0.001 * input_df['pre_weld_heating_c']
        
        quality_data['microhardness_hv'] = (base_hardness + process_hardness * preheat_factor + 
                                           np.random.normal(0, 10, self.n_samples))
        
        # Additional quality metrics
        quality_data['weld_penetration_ratio'] = quality_data['weld_depth_mm'] / input_df['tab_thickness_um'] * 1000
        quality_data['aspect_ratio'] = quality_data['weld_width_mm'] / quality_data['weld_depth_mm']
        
        # Weld efficiency - comprehensive calculation
        strength_score = np.clip(quality_data['weld_strength_mpa'] / 1000, 0, 1)
        resistance_score = np.clip(1 / quality_data['contact_resistance_mohm'], 0, 1)
        porosity_score = np.clip(1 / (1 + quality_data['porosity_percent']), 0, 1)
        hardness_score = np.clip(quality_data['microhardness_hv'] / 200, 0, 1)
        
        quality_data['weld_efficiency_percent'] = ((strength_score * 0.3 + resistance_score * 0.3 + 
                                                   porosity_score * 0.2 + hardness_score * 0.2) * 100)
        
        # Weld quality classification
        quality_data['weld_quality_class'] = pd.cut(quality_data['weld_efficiency_percent'], 
                                                   bins=[0, 60, 80, 90, 100], 
                                                   labels=['Poor', 'Fair', 'Good', 'Excellent'])
        
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
        base_fatigue = np.array([min(anode['melting_point'], cathode['melting_point']) 
                               for anode, cathode in zip([self.materials[mat] for mat in input_df['anode_material']],
                                                       [self.materials[mat] for mat in input_df['cathode_material']])]) / 10
        
        quality_factor = quality_df['weld_efficiency_percent'] / 100
        thermal_factor = 1 / (1 + temp_range / 200)
        material_factor = np.array([(anode['thermal_expansion'] + cathode['thermal_expansion']) / 2 
                                  for anode, cathode in zip([self.materials[mat] for mat in input_df['anode_material']],
                                                          [self.materials[mat] for mat in input_df['cathode_material']])]) * 1e6
        
        performance_data['fatigue_life_cycles'] = (base_fatigue * quality_factor * thermal_factor * 
                                                 (1 / (1 + material_factor)) * (1 + 0.3 * np.random.normal(0, 1, self.n_samples)))
        
        # Thermal resistance degradation (%)
        base_degradation = temp_range * 0.1 + n_cycles * 0.001
        material_thermal = np.array([1 / (anode['thermal_conductivity'] + cathode['thermal_conductivity']) 
                                   for anode, cathode in zip([self.materials[mat] for mat in input_df['anode_material']],
                                                           [self.materials[mat] for mat in input_df['cathode_material']])]) * 1000
        
        performance_data['thermal_resistance_degradation_percent'] = (base_degradation * material_thermal * 
                                                                    (1 + 0.2 * np.random.normal(0, 1, self.n_samples)))
        
        # Electrical resistance increase (%)
        base_increase = temp_range * 0.05 + n_cycles * 0.0005
        surface_factors = np.array([self.surface_finishes[finish]['contact_resistance_factor'] 
                                  for finish in input_df['surface_finish']])
        
        performance_data['electrical_resistance_increase_percent'] = (base_increase * surface_factors * 
                                                                    (1 + 0.15 * np.random.normal(0, 1, self.n_samples)))
        
        # Creep resistance (hours at elevated temperature)
        creep_base = np.array([(anode['melting_point'] + cathode['melting_point']) / 2 
                             for anode, cathode in zip([self.materials[mat] for mat in input_df['anode_material']],
                                                     [self.materials[mat] for mat in input_df['cathode_material']])])
        
        creep_factor = np.exp(-(max_temp - 100) / 100) * quality_factor
        performance_data['creep_resistance_hours'] = creep_base * creep_factor * (1 + 0.5 * np.random.normal(0, 1, self.n_samples))
        
        # Corrosion resistance (rating 1-10)
        corrosion_base = np.array([(anode['hardness'] + cathode['hardness']) / 20 
                                 for anode, cathode in zip([self.materials[mat] for mat in input_df['anode_material']],
                                                         [self.materials[mat] for mat in input_df['cathode_material']])])
        
        surface_protection = {'Polished': 0.8, 'Rough': 0.6, 'Coated': 1.2, 'Anodized': 1.5, 
                            'Plated': 1.0, 'Oxidized': 0.4, 'Cleaned': 0.9}
        surface_protection_factor = np.array([surface_protection[finish] for finish in input_df['surface_finish']])
        
        performance_data['corrosion_resistance_rating'] = np.clip(corrosion_base * surface_protection_factor * 
                                                                quality_factor * 10, 1, 10)
        
        # Weld integrity score (0-100) - comprehensive
        integrity = (quality_df['weld_efficiency_percent'] * 0.25 + 
                    (100 - performance_data['thermal_resistance_degradation_percent']) * 0.25 +
                    (100 - performance_data['electrical_resistance_increase_percent']) * 0.25 +
                    performance_data['corrosion_resistance_rating'] * 10 * 0.25)
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
            elif performance_data['corrosion_resistance_rating'][i] < 3:
                failure_modes.append('Corrosion')
            elif performance_data['creep_resistance_hours'][i] < 100:
                failure_modes.append('Creep')
            else:
                failure_modes.append('None')
        
        performance_data['predicted_failure_mode'] = failure_modes
        
        # Reliability metrics
        performance_data['reliability_score'] = performance_data['weld_integrity_score'] * 0.6 + \
                                              (100 - performance_data['thermal_resistance_degradation_percent']) * 0.4
        
        # Service life prediction (years)
        base_life = performance_data['fatigue_life_cycles'] / 1000  # Convert cycles to years (assuming 1000 cycles/year)
        quality_life_factor = quality_df['weld_efficiency_percent'] / 100
        performance_data['predicted_service_life_years'] = base_life * quality_life_factor * (1 + 0.2 * np.random.normal(0, 1, self.n_samples))
        
        return pd.DataFrame(performance_data)
    
    def generate_complete_dataset(self):
        """Generate the complete enhanced welding dataset"""
        print("Generating enhanced input parameters...")
        input_df = self.generate_input_parameters()
        
        print("Calculating comprehensive quality metrics...")
        quality_df = self.calculate_quality_metrics(input_df)
        
        print("Calculating performance metrics under extreme conditions...")
        performance_df = self.calculate_performance_metrics(input_df, quality_df)
        
        # Combine all data
        complete_df = pd.concat([input_df, quality_df, performance_df], axis=1)
        
        return complete_df
    
    def save_dataset(self, df, filename='enhanced_welding_dataset.csv'):
        """Save the enhanced dataset to CSV"""
        df.to_csv(filename, index=False)
        print(f"Enhanced dataset saved to {filename}")
        return filename
    
    def generate_comprehensive_visualizations(self, df):
        """Generate comprehensive visualizations for the enhanced dataset"""
        plt.style.use('seaborn-v0_8')
        fig = plt.figure(figsize=(24, 16))
        
        # Create a 4x4 grid of subplots
        gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
        
        # 1. Weld strength distribution
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.hist(df['weld_strength_mpa'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.set_title('Weld Strength Distribution', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Strength (MPa)')
        ax1.set_ylabel('Frequency')
        
        # 2. Contact resistance vs technique
        ax2 = fig.add_subplot(gs[0, 1])
        technique_resistance = df.groupby('welding_technique')['contact_resistance_mohm'].mean()
        bars = ax2.bar(technique_resistance.index, technique_resistance.values, color='lightcoral', edgecolor='black')
        ax2.set_title('Average Contact Resistance by Technique', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Resistance (mOhm)')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Weld efficiency vs technique
        ax3 = fig.add_subplot(gs[0, 2])
        technique_efficiency = df.groupby('welding_technique')['weld_efficiency_percent'].mean()
        ax3.bar(technique_efficiency.index, technique_efficiency.values, color='lightgreen', edgecolor='black')
        ax3.set_title('Average Weld Efficiency by Technique', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Efficiency (%)')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Quality class distribution
        ax4 = fig.add_subplot(gs[0, 3])
        quality_counts = df['weld_quality_class'].value_counts()
        ax4.pie(quality_counts.values, labels=quality_counts.index, autopct='%1.1f%%', startangle=90)
        ax4.set_title('Weld Quality Class Distribution', fontsize=12, fontweight='bold')
        
        # 5. Fatigue life distribution
        ax5 = fig.add_subplot(gs[1, 0])
        ax5.hist(df['fatigue_life_cycles'], bins=50, alpha=0.7, color='gold', edgecolor='black')
        ax5.set_title('Fatigue Life Distribution', fontsize=12, fontweight='bold')
        ax5.set_xlabel('Cycles')
        ax5.set_ylabel('Frequency')
        
        # 6. Thermal degradation vs technique
        ax6 = fig.add_subplot(gs[1, 1])
        technique_thermal = df.groupby('welding_technique')['thermal_resistance_degradation_percent'].mean()
        ax6.bar(technique_thermal.index, technique_thermal.values, color='orange', edgecolor='black')
        ax6.set_title('Average Thermal Degradation by Technique', fontsize=12, fontweight='bold')
        ax6.set_ylabel('Degradation (%)')
        ax6.tick_params(axis='x', rotation=45)
        
        # 7. Corrosion resistance distribution
        ax7 = fig.add_subplot(gs[1, 2])
        ax7.hist(df['corrosion_resistance_rating'], bins=20, alpha=0.7, color='purple', edgecolor='black')
        ax7.set_title('Corrosion Resistance Rating Distribution', fontsize=12, fontweight='bold')
        ax7.set_xlabel('Rating (1-10)')
        ax7.set_ylabel('Frequency')
        
        # 8. Weld integrity score distribution
        ax8 = fig.add_subplot(gs[1, 3])
        ax8.hist(df['weld_integrity_score'], bins=50, alpha=0.7, color='red', edgecolor='black')
        ax8.set_title('Weld Integrity Score Distribution', fontsize=12, fontweight='bold')
        ax8.set_xlabel('Integrity Score')
        ax8.set_ylabel('Frequency')
        
        # 9. Material combination heatmap
        ax9 = fig.add_subplot(gs[2, 0])
        material_combinations = df.groupby(['anode_material', 'cathode_material'])['weld_efficiency_percent'].mean().unstack()
        sns.heatmap(material_combinations, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax9)
        ax9.set_title('Weld Efficiency by Material Combination', fontsize=12, fontweight='bold')
        
        # 10. Failure mode distribution
        ax10 = fig.add_subplot(gs[2, 1])
        failure_counts = df['predicted_failure_mode'].value_counts()
        ax10.bar(failure_counts.index, failure_counts.values, color='darkred', edgecolor='black')
        ax10.set_title('Predicted Failure Mode Distribution', fontsize=12, fontweight='bold')
        ax10.set_ylabel('Count')
        ax10.tick_params(axis='x', rotation=45)
        
        # 11. Service life prediction
        ax11 = fig.add_subplot(gs[2, 2])
        ax11.hist(df['predicted_service_life_years'], bins=50, alpha=0.7, color='green', edgecolor='black')
        ax11.set_title('Predicted Service Life Distribution', fontsize=12, fontweight='bold')
        ax11.set_xlabel('Years')
        ax11.set_ylabel('Frequency')
        
        # 12. Reliability score distribution
        ax12 = fig.add_subplot(gs[2, 3])
        ax12.hist(df['reliability_score'], bins=50, alpha=0.7, color='navy', edgecolor='black')
        ax12.set_title('Reliability Score Distribution', fontsize=12, fontweight='bold')
        ax12.set_xlabel('Reliability Score')
        ax12.set_ylabel('Frequency')
        
        # 13. Weld geometry analysis
        ax13 = fig.add_subplot(gs[3, 0])
        ax13.scatter(df['weld_width_mm'], df['weld_depth_mm'], alpha=0.6, c=df['weld_efficiency_percent'], 
                    cmap='viridis', edgecolors='black', s=20)
        ax13.set_xlabel('Weld Width (mm)')
        ax13.set_ylabel('Weld Depth (mm)')
        ax13.set_title('Weld Geometry vs Efficiency', fontsize=12, fontweight='bold')
        cbar = plt.colorbar(ax13.collections[0], ax=ax13)
        cbar.set_label('Weld Efficiency (%)')
        
        # 14. Process parameter correlation
        ax14 = fig.add_subplot(gs[3, 1])
        process_params = ['power_w', 'force_n', 'weld_time_ms', 'weld_efficiency_percent']
        correlation_matrix = df[process_params].corr()
        sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax14)
        ax14.set_title('Process Parameter Correlations', fontsize=12, fontweight='bold')
        
        # 15. Environmental effects
        ax15 = fig.add_subplot(gs[3, 2])
        ax15.scatter(df['ambient_humidity_percent'], df['porosity_percent'], alpha=0.6, 
                    c=df['weld_efficiency_percent'], cmap='plasma', edgecolors='black', s=20)
        ax15.set_xlabel('Ambient Humidity (%)')
        ax15.set_ylabel('Porosity (%)')
        ax15.set_title('Environmental Effects on Porosity', fontsize=12, fontweight='bold')
        cbar = plt.colorbar(ax15.collections[0], ax=ax15)
        cbar.set_label('Weld Efficiency (%)')
        
        # 16. Performance vs Quality scatter
        ax16 = fig.add_subplot(gs[3, 3])
        ax16.scatter(df['weld_efficiency_percent'], df['weld_integrity_score'], alpha=0.6, 
                    c=df['fatigue_life_cycles'], cmap='inferno', edgecolors='black', s=20)
        ax16.set_xlabel('Weld Efficiency (%)')
        ax16.set_ylabel('Weld Integrity Score')
        ax16.set_title('Quality vs Performance', fontsize=12, fontweight='bold')
        cbar = plt.colorbar(ax16.collections[0], ax=ax16)
        cbar.set_label('Fatigue Life (cycles)')
        
        plt.suptitle('Comprehensive Welding Dataset Analysis', fontsize=16, fontweight='bold', y=0.98)
        plt.savefig('enhanced_welding_dataset_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("Comprehensive visualizations saved to enhanced_welding_dataset_analysis.png")

def main():
    # Generate enhanced dataset
    generator = EnhancedWeldingDatasetGenerator(n_samples=50000)
    dataset = generator.generate_complete_dataset()
    
    # Save dataset
    filename = generator.save_dataset(dataset)
    
    # Generate comprehensive visualizations
    generator.generate_comprehensive_visualizations(dataset)
    
    # Display comprehensive statistics
    print("\n" + "="*80)
    print("ENHANCED WELDING DATASET STATISTICS")
    print("="*80)
    print(f"Total samples: {len(dataset):,}")
    print(f"Total features: {len(dataset.columns)}")
    
    print("\nINPUT PARAMETERS:")
    print(f"- Materials: {dataset['anode_material'].nunique()} anode, {dataset['cathode_material'].nunique()} cathode")
    print(f"- Techniques: {dataset['welding_technique'].nunique()}")
    print(f"- Surface finishes: {dataset['surface_finish'].nunique()}")
    print(f"- Cleaning methods: {dataset['cleaning_method'].nunique()}")
    
    print("\nQUALITY METRICS:")
    print(f"- Weld strength: {dataset['weld_strength_mpa'].mean():.1f} ± {dataset['weld_strength_mpa'].std():.1f} MPa")
    print(f"- Contact resistance: {dataset['contact_resistance_mohm'].mean():.3f} ± {dataset['contact_resistance_mohm'].std():.3f} mOhm")
    print(f"- Weld efficiency: {dataset['weld_efficiency_percent'].mean():.1f} ± {dataset['weld_efficiency_percent'].std():.1f}%")
    print(f"- Porosity: {dataset['porosity_percent'].mean():.2f} ± {dataset['porosity_percent'].std():.2f}%")
    print(f"- Microhardness: {dataset['microhardness_hv'].mean():.1f} ± {dataset['microhardness_hv'].std():.1f} HV")
    
    print("\nPERFORMANCE METRICS:")
    print(f"- Fatigue life: {dataset['fatigue_life_cycles'].mean():.0f} ± {dataset['fatigue_life_cycles'].std():.0f} cycles")
    print(f"- Thermal degradation: {dataset['thermal_resistance_degradation_percent'].mean():.1f} ± {dataset['thermal_resistance_degradation_percent'].std():.1f}%")
    print(f"- Electrical resistance increase: {dataset['electrical_resistance_increase_percent'].mean():.1f} ± {dataset['electrical_resistance_increase_percent'].std():.1f}%")
    print(f"- Corrosion resistance: {dataset['corrosion_resistance_rating'].mean():.1f} ± {dataset['corrosion_resistance_rating'].std():.1f}/10")
    print(f"- Weld integrity: {dataset['weld_integrity_score'].mean():.1f} ± {dataset['weld_integrity_score'].std():.1f}")
    print(f"- Predicted service life: {dataset['predicted_service_life_years'].mean():.1f} ± {dataset['predicted_service_life_years'].std():.1f} years")
    
    print("\nQUALITY DISTRIBUTION:")
    quality_dist = dataset['weld_quality_class'].value_counts()
    for quality, count in quality_dist.items():
        print(f"- {quality}: {count:,} ({count/len(dataset)*100:.1f}%)")
    
    print("\nFAILURE MODE DISTRIBUTION:")
    failure_dist = dataset['predicted_failure_mode'].value_counts()
    for mode, count in failure_dist.items():
        print(f"- {mode}: {count:,} ({count/len(dataset)*100:.1f}%)")
    
    print(f"\nDataset saved to: {filename}")
    print("="*80)
    
    return dataset

if __name__ == "__main__":
    dataset = main()