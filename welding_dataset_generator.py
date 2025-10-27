import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class WeldingDatasetGenerator:
    def __init__(self, n_samples=10000):
        self.n_samples = n_samples
        self.rng = np.random.RandomState(42)
        
        # Material properties database
        self.materials = {
            'Cu': {'density': 8.96, 'thermal_conductivity': 400, 'melting_point': 1085, 'electrical_conductivity': 5.96e7},
            'Al': {'density': 2.70, 'thermal_conductivity': 237, 'melting_point': 660, 'electrical_conductivity': 3.77e7},
            'Ni': {'density': 8.90, 'thermal_conductivity': 91, 'melting_point': 1455, 'electrical_conductivity': 1.43e7},
            'Ti': {'density': 4.51, 'thermal_conductivity': 22, 'melting_point': 1668, 'electrical_conductivity': 0.56e7},
            'Steel': {'density': 7.85, 'thermal_conductivity': 50, 'melting_point': 1500, 'electrical_conductivity': 1.0e7}
        }
        
        # Welding techniques
        self.welding_techniques = ['USW', 'Laser', 'Resistance_Spot', 'Friction_Stir', 'Electron_Beam']
        
        # Surface finishes
        self.surface_finishes = ['Polished', 'Rough', 'Coated', 'Anodized', 'Plated']
        
    def generate_input_parameters(self):
        """Generate input parameters for the welding process"""
        data = {}
        
        # Base Materials
        data['anode_material'] = self.rng.choice(list(self.materials.keys()), self.n_samples)
        data['cathode_material'] = self.rng.choice(list(self.materials.keys()), self.n_samples)
        data['tab_thickness_um'] = self.rng.normal(100, 20, self.n_samples).clip(50, 200)
        data['surface_finish'] = self.rng.choice(self.surface_finishes, self.n_samples)
        
        # Welding Process Parameters
        data['welding_technique'] = self.rng.choice(self.welding_techniques, self.n_samples)
        
        # Power parameters (technique-dependent)
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
            else:  # Electron_Beam
                power_data.append(self.rng.normal(800, 200, 1)[0])   # W
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
        
        # Speed (for Laser)
        data['speed_mm_s'] = np.where(data['welding_technique'] == 'Laser',
                                    self.rng.normal(10, 2, self.n_samples).clip(5, 20),
                                    np.nan)
        
        # Pulse Frequency (for Laser)
        data['pulse_frequency_hz'] = np.where(data['welding_technique'] == 'Laser',
                                            self.rng.normal(1000, 200, self.n_samples).clip(500, 2000),
                                            np.nan)
        
        # Environmental
        data['preheat_temp_c'] = self.rng.normal(25, 10, self.n_samples).clip(20, 100)
        
        return pd.DataFrame(data)
    
    def calculate_quality_metrics(self, input_df):
        """Calculate quality metrics based on input parameters"""
        quality_data = {}
        
        # Get material properties
        anode_props = [self.materials[mat] for mat in input_df['anode_material']]
        cathode_props = [self.materials[mat] for mat in input_df['cathode_material']]
        
        # Weld strength (MPa) - depends on materials, force, and technique
        base_strength = np.array([min(anode['melting_point'], cathode['melting_point']) 
                                for anode, cathode in zip(anode_props, cathode_props)])
        
        # Technique multiplier
        technique_multiplier = {
            'USW': 0.8, 'Laser': 0.9, 'Resistance_Spot': 0.7, 
            'Friction_Stir': 0.95, 'Electron_Beam': 0.85
        }
        
        strength_multiplier = np.array([technique_multiplier[tech] for tech in input_df['welding_technique']])
        quality_data['weld_strength_mpa'] = base_strength * strength_multiplier * (input_df['force_n'] / 500) * (1 + 0.1 * np.random.normal(0, 1, self.n_samples))
        
        # Contact resistance (mOhm) - depends on materials and surface finish
        base_resistance = np.array([1 / (anode['electrical_conductivity'] + cathode['electrical_conductivity']) 
                                  for anode, cathode in zip(anode_props, cathode_props)]) * 1e6
        
        surface_multiplier = {'Polished': 0.8, 'Rough': 1.2, 'Coated': 1.5, 'Anodized': 2.0, 'Plated': 1.1}
        resistance_multiplier = np.array([surface_multiplier[finish] for finish in input_df['surface_finish']])
        
        quality_data['contact_resistance_mohm'] = base_resistance * resistance_multiplier * (1 + 0.2 * np.random.normal(0, 1, self.n_samples))
        
        # Weld width (mm) - depends on technique and parameters
        width_data = []
        for i, technique in enumerate(input_df['welding_technique']):
            if technique == 'USW':
                width = 2.0 + 0.1 * input_df['amplitude_um'].iloc[i] + 0.01 * input_df['weld_time_ms'].iloc[i]
            elif technique == 'Laser':
                width = 1.5 + 0.05 * input_df['power_w'].iloc[i] + 0.02 * input_df['speed_mm_s'].iloc[i]
            elif technique == 'Resistance_Spot':
                width = 3.0 + 0.02 * input_df['force_n'].iloc[i] + 0.01 * input_df['weld_time_ms'].iloc[i]
            elif technique == 'Friction_Stir':
                width = 4.0 + 0.01 * input_df['power_w'].iloc[i] + 0.02 * input_df['weld_time_ms'].iloc[i]
            else:  # Electron_Beam
                width = 1.0 + 0.03 * input_df['power_w'].iloc[i] + 0.01 * input_df['weld_time_ms'].iloc[i]
            width_data.append(width)
        
        quality_data['weld_width_mm'] = np.array(width_data)
        
        # Weld depth (mm) - similar logic
        depth_data = []
        for i, technique in enumerate(input_df['welding_technique']):
            if technique == 'USW':
                depth = 0.5 + 0.02 * input_df['amplitude_um'].iloc[i] + 0.005 * input_df['weld_time_ms'].iloc[i]
            elif technique == 'Laser':
                depth = 0.3 + 0.01 * input_df['power_w'].iloc[i] + 0.005 * input_df['speed_mm_s'].iloc[i]
            elif technique == 'Resistance_Spot':
                depth = 0.8 + 0.01 * input_df['force_n'].iloc[i] + 0.005 * input_df['weld_time_ms'].iloc[i]
            elif technique == 'Friction_Stir':
                depth = 1.0 + 0.005 * input_df['power_w'].iloc[i] + 0.01 * input_df['weld_time_ms'].iloc[i]
            else:  # Electron_Beam
                depth = 0.2 + 0.01 * input_df['power_w'].iloc[i] + 0.005 * input_df['weld_time_ms'].iloc[i]
            depth_data.append(depth)
        
        quality_data['weld_depth_mm'] = np.array(depth_data)
        
        # Porosity percentage - depends on technique and environmental conditions
        base_porosity = np.random.normal(2, 1, self.n_samples).clip(0, 10)
        technique_porosity = {
            'USW': 0.8, 'Laser': 0.6, 'Resistance_Spot': 1.2, 
            'Friction_Stir': 0.4, 'Electron_Beam': 0.5
        }
        porosity_multiplier = np.array([technique_porosity[tech] for tech in input_df['welding_technique']])
        quality_data['porosity_percent'] = base_porosity * porosity_multiplier * (1 + 0.1 * input_df['preheat_temp_c'] / 100)
        
        # Microhardness (HV) - depends on materials and process parameters
        base_hardness = np.array([(anode['melting_point'] + cathode['melting_point']) / 2 
                                for anode, cathode in zip(anode_props, cathode_props)]) / 10
        
        process_hardness = input_df['force_n'] * 0.1 + input_df['power_w'] * 0.05
        quality_data['microhardness_hv'] = base_hardness + process_hardness + np.random.normal(0, 10, self.n_samples)
        
        # Weld efficiency - overall quality metric
        efficiency = (quality_data['weld_strength_mpa'] / 1000) * (1 / quality_data['contact_resistance_mohm']) * (1 / quality_data['porosity_percent']) * 100
        quality_data['weld_efficiency_percent'] = np.clip(efficiency, 0, 100)
        
        return pd.DataFrame(quality_data)
    
    def calculate_performance_metrics(self, input_df, quality_df):
        """Calculate performance metrics under extreme temperature cycling"""
        performance_data = {}
        
        # Thermal cycling parameters
        n_cycles = self.rng.normal(1000, 200, self.n_samples).clip(500, 2000)
        temp_range = self.rng.normal(150, 30, self.n_samples).clip(100, 250)  # Temperature swing in °C
        
        # Fatigue life (cycles) - depends on materials, weld quality, and thermal cycling
        base_fatigue = np.array([min(anode['melting_point'], cathode['melting_point']) 
                               for anode, cathode in zip([self.materials[mat] for mat in input_df['anode_material']],
                                                       [self.materials[mat] for mat in input_df['cathode_material']])]) / 10
        
        quality_factor = quality_df['weld_efficiency_percent'] / 100
        thermal_factor = 1 / (1 + temp_range / 200)
        
        performance_data['fatigue_life_cycles'] = base_fatigue * quality_factor * thermal_factor * (1 + 0.3 * np.random.normal(0, 1, self.n_samples))
        
        # Thermal resistance degradation (%)
        base_degradation = temp_range * 0.1 + n_cycles * 0.001
        material_factor = np.array([1 / (anode['thermal_conductivity'] + cathode['thermal_conductivity']) 
                                  for anode, cathode in zip([self.materials[mat] for mat in input_df['anode_material']],
                                                          [self.materials[mat] for mat in input_df['cathode_material']])]) * 1000
        
        performance_data['thermal_resistance_degradation_percent'] = base_degradation * material_factor * (1 + 0.2 * np.random.normal(0, 1, self.n_samples))
        
        # Electrical resistance increase (%)
        base_increase = temp_range * 0.05 + n_cycles * 0.0005
        surface_factor = {'Polished': 0.8, 'Rough': 1.2, 'Coated': 1.5, 'Anodized': 2.0, 'Plated': 1.1}
        surface_multiplier = np.array([surface_factor[finish] for finish in input_df['surface_finish']])
        
        performance_data['electrical_resistance_increase_percent'] = base_increase * surface_multiplier * (1 + 0.15 * np.random.normal(0, 1, self.n_samples))
        
        # Weld integrity score (0-100)
        integrity = (quality_df['weld_efficiency_percent'] * 0.4 + 
                    (100 - performance_data['thermal_resistance_degradation_percent']) * 0.3 +
                    (100 - performance_data['electrical_resistance_increase_percent']) * 0.3)
        performance_data['weld_integrity_score'] = np.clip(integrity, 0, 100)
        
        # Failure mode prediction
        failure_modes = []
        for i in range(self.n_samples):
            if performance_data['fatigue_life_cycles'][i] < 500:
                failure_modes.append('Fatigue')
            elif performance_data['thermal_resistance_degradation_percent'][i] > 50:
                failure_modes.append('Thermal')
            elif performance_data['electrical_resistance_increase_percent'][i] > 30:
                failure_modes.append('Electrical')
            else:
                failure_modes.append('None')
        
        performance_data['predicted_failure_mode'] = failure_modes
        
        return pd.DataFrame(performance_data)
    
    def generate_complete_dataset(self):
        """Generate the complete welding dataset"""
        print("Generating input parameters...")
        input_df = self.generate_input_parameters()
        
        print("Calculating quality metrics...")
        quality_df = self.calculate_quality_metrics(input_df)
        
        print("Calculating performance metrics...")
        performance_df = self.calculate_performance_metrics(input_df, quality_df)
        
        # Combine all data
        complete_df = pd.concat([input_df, quality_df, performance_df], axis=1)
        
        return complete_df
    
    def save_dataset(self, df, filename='welding_dataset.csv'):
        """Save the dataset to CSV"""
        df.to_csv(filename, index=False)
        print(f"Dataset saved to {filename}")
        return filename
    
    def generate_visualizations(self, df):
        """Generate visualizations for the dataset"""
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
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
        
        plt.tight_layout()
        plt.savefig('welding_dataset_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("Visualizations saved to welding_dataset_analysis.png")

def main():
    # Generate dataset
    generator = WeldingDatasetGenerator(n_samples=10000)
    dataset = generator.generate_complete_dataset()
    
    # Save dataset
    filename = generator.save_dataset(dataset)
    
    # Generate visualizations
    generator.generate_visualizations(dataset)
    
    # Display basic statistics
    print("\nDataset Statistics:")
    print(f"Total samples: {len(dataset)}")
    print(f"Total features: {len(dataset.columns)}")
    print("\nInput Parameters:")
    print(f"- Materials: {dataset['anode_material'].nunique()} anode, {dataset['cathode_material'].nunique()} cathode")
    print(f"- Techniques: {dataset['welding_technique'].nunique()}")
    print(f"- Surface finishes: {dataset['surface_finish'].nunique()}")
    
    print("\nQuality Metrics:")
    print(f"- Weld strength: {dataset['weld_strength_mpa'].mean():.1f} ± {dataset['weld_strength_mpa'].std():.1f} MPa")
    print(f"- Contact resistance: {dataset['contact_resistance_mohm'].mean():.2f} ± {dataset['contact_resistance_mohm'].std():.2f} mOhm")
    print(f"- Weld efficiency: {dataset['weld_efficiency_percent'].mean():.1f} ± {dataset['weld_efficiency_percent'].std():.1f}%")
    
    print("\nPerformance Metrics:")
    print(f"- Fatigue life: {dataset['fatigue_life_cycles'].mean():.0f} ± {dataset['fatigue_life_cycles'].std():.0f} cycles")
    print(f"- Thermal degradation: {dataset['thermal_resistance_degradation_percent'].mean():.1f} ± {dataset['thermal_resistance_degradation_percent'].std():.1f}%")
    print(f"- Weld integrity: {dataset['weld_integrity_score'].mean():.1f} ± {dataset['weld_integrity_score'].std():.1f}")
    
    print(f"\nDataset saved to: {filename}")
    return dataset

if __name__ == "__main__":
    dataset = main()