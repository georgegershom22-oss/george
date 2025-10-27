import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

class WeldingDatasetGenerator:
    def __init__(self, n_samples=10000, random_state=42):
        self.n_samples = n_samples
        self.random_state = random_state
        np.random.seed(random_state)
        
        # Define material properties and constraints
        self.materials = {
            'Cu': {'density': 8.96, 'thermal_conductivity': 401, 'melting_point': 1085, 'yield_strength': 70},
            'Al': {'density': 2.70, 'thermal_conductivity': 237, 'melting_point': 660, 'yield_strength': 95},
            'Ni': {'density': 8.90, 'thermal_conductivity': 91, 'melting_point': 1455, 'yield_strength': 200},
            'Ti': {'density': 4.51, 'thermal_conductivity': 22, 'melting_point': 1668, 'yield_strength': 880},
            'Steel': {'density': 7.85, 'thermal_conductivity': 50, 'melting_point': 1500, 'yield_strength': 250}
        }
        
        self.welding_techniques = ['USW', 'Laser', 'Resistance_Spot', 'Friction_Stir', 'Electron_Beam']
        self.surface_finishes = ['Polished', 'Rough', 'Coated', 'Anodized', 'Plated']
        
    def generate_input_parameters(self):
        """Generate realistic input parameters for welding"""
        data = {}
        
        # Base Materials
        data['anode_material'] = np.random.choice(list(self.materials.keys()), self.n_samples)
        data['cathode_material'] = np.random.choice(list(self.materials.keys()), self.n_samples)
        data['tab_thickness_um'] = np.random.uniform(50, 500, self.n_samples)
        data['surface_finish'] = np.random.choice(self.surface_finishes, self.n_samples)
        
        # Welding Process Parameters
        data['welding_technique'] = np.random.choice(self.welding_techniques, self.n_samples)
        
        # Power parameters (technique-dependent)
        data['power_w'] = np.random.uniform(100, 5000, self.n_samples)
        data['amplitude_um'] = np.random.uniform(10, 100, self.n_samples)
        data['force_n'] = np.random.uniform(100, 5000, self.n_samples)
        data['time_ms'] = np.random.uniform(10, 1000, self.n_samples)
        data['speed_mm_s'] = np.random.uniform(1, 50, self.n_samples)
        data['pulse_frequency_hz'] = np.random.uniform(1, 1000, self.n_samples)
        
        # Environmental
        data['preheat_temp_c'] = np.random.uniform(20, 300, self.n_samples)
        
        return pd.DataFrame(data)
    
    def calculate_material_compatibility(self, anode, cathode):
        """Calculate compatibility score between materials"""
        anode_props = self.materials[anode]
        cathode_props = self.materials[cathode]
        
        # Thermal expansion mismatch
        thermal_mismatch = abs(anode_props['thermal_conductivity'] - cathode_props['thermal_conductivity'])
        
        # Melting point difference
        melting_diff = abs(anode_props['melting_point'] - cathode_props['melting_point'])
        
        # Compatibility score (0-1, higher is better)
        compatibility = 1 - (thermal_mismatch / 1000 + melting_diff / 2000)
        return np.clip(compatibility, 0, 1)
    
    def calculate_weld_quality_metrics(self, df):
        """Calculate quality metrics based on input parameters"""
        quality_metrics = {}
        
        # Material compatibility
        compatibility = []
        for i in range(len(df)):
            comp = self.calculate_material_compatibility(
                df.iloc[i]['anode_material'], 
                df.iloc[i]['cathode_material']
            )
            compatibility.append(comp)
        quality_metrics['material_compatibility'] = compatibility
        
        # Weld strength (depends on force, time, and material properties)
        base_strength = []
        for i in range(len(df)):
            anode_strength = self.materials[df.iloc[i]['anode_material']]['yield_strength']
            cathode_strength = self.materials[df.iloc[i]['cathode_material']]['yield_strength']
            avg_strength = (anode_strength + cathode_strength) / 2
            
            # Influence of welding parameters
            force_factor = np.log1p(df.iloc[i]['force_n'] / 1000)
            time_factor = np.log1p(df.iloc[i]['time_ms'] / 100)
            
            strength = avg_strength * force_factor * time_factor * compatibility[i]
            base_strength.append(strength)
        
        quality_metrics['weld_strength_mpa'] = base_strength
        
        # Contact resistance (depends on surface finish, force, and materials)
        contact_resistance = []
        for i in range(len(df)):
            base_resistance = 0.001  # Base resistance in ohms
            
            # Surface finish effect
            surface_factors = {'Polished': 0.8, 'Rough': 1.2, 'Coated': 1.5, 'Anodized': 2.0, 'Plated': 0.9}
            surface_factor = surface_factors[df.iloc[i]['surface_finish']]
            
            # Force effect (higher force = lower resistance)
            force_factor = 1 / (1 + df.iloc[i]['force_n'] / 1000)
            
            # Material effect
            anode_cond = self.materials[df.iloc[i]['anode_material']]['thermal_conductivity']
            cathode_cond = self.materials[df.iloc[i]['cathode_material']]['thermal_conductivity']
            avg_conductivity = (anode_cond + cathode_cond) / 2
            conductivity_factor = 1 / (1 + avg_conductivity / 1000)
            
            resistance = base_resistance * surface_factor * force_factor * conductivity_factor
            contact_resistance.append(resistance)
        
        quality_metrics['contact_resistance_ohm'] = contact_resistance
        
        # Weld width (depends on power, time, and technique)
        weld_width = []
        for i in range(len(df)):
            base_width = 0.5  # Base width in mm
            
            # Power effect
            power_factor = np.sqrt(df.iloc[i]['power_w'] / 1000)
            
            # Time effect
            time_factor = np.sqrt(df.iloc[i]['time_ms'] / 100)
            
            # Technique effect
            technique_factors = {'USW': 1.0, 'Laser': 0.8, 'Resistance_Spot': 1.2, 'Friction_Stir': 1.5, 'Electron_Beam': 0.6}
            technique_factor = technique_factors[df.iloc[i]['welding_technique']]
            
            width = base_width * power_factor * time_factor * technique_factor
            weld_width.append(width)
        
        quality_metrics['weld_width_mm'] = weld_width
        
        # Penetration depth (depends on power, speed, and materials)
        penetration_depth = []
        for i in range(len(df)):
            base_depth = 0.2  # Base depth in mm
            
            # Power effect
            power_factor = np.sqrt(df.iloc[i]['power_w'] / 1000)
            
            # Speed effect (inverse relationship)
            speed_factor = 1 / (1 + df.iloc[i]['speed_mm_s'] / 10)
            
            # Material effect (thicker materials = deeper penetration needed)
            thickness_factor = np.sqrt(df.iloc[i]['tab_thickness_um'] / 100)
            
            depth = base_depth * power_factor * speed_factor * thickness_factor
            penetration_depth.append(depth)
        
        quality_metrics['penetration_depth_mm'] = penetration_depth
        
        # Porosity (depends on technique, environment, and materials)
        porosity = []
        for i in range(len(df)):
            base_porosity = 0.05  # Base porosity percentage
            
            # Technique effect
            technique_factors = {'USW': 0.8, 'Laser': 0.6, 'Resistance_Spot': 1.0, 'Friction_Stir': 0.4, 'Electron_Beam': 0.3}
            technique_factor = technique_factors[df.iloc[i]['welding_technique']]
            
            # Environmental effect
            temp_factor = 1 + (df.iloc[i]['preheat_temp_c'] - 20) / 1000
            
            # Material effect
            compatibility_factor = 1 - compatibility[i]
            
            porosity_val = base_porosity * technique_factor * temp_factor * (1 + compatibility_factor)
            porosity.append(min(porosity_val, 0.3))  # Cap at 30%
        
        quality_metrics['porosity_percent'] = porosity
        
        return pd.DataFrame(quality_metrics)
    
    def calculate_performance_metrics(self, df, quality_df):
        """Calculate performance metrics under extreme temperature cycling"""
        performance_metrics = {}
        
        # Thermal cycling resistance (number of cycles before failure)
        thermal_cycles = []
        for i in range(len(df)):
            base_cycles = 1000  # Base number of cycles
            
            # Material compatibility effect
            compatibility = quality_df.iloc[i]['material_compatibility']
            
            # Weld quality effect
            strength_factor = quality_df.iloc[i]['weld_strength_mpa'] / 100
            porosity_factor = 1 - quality_df.iloc[i]['porosity_percent']
            
            # Technique effect
            technique_factors = {'USW': 1.0, 'Laser': 1.2, 'Resistance_Spot': 0.8, 'Friction_Stir': 1.5, 'Electron_Beam': 1.3}
            technique_factor = technique_factors[df.iloc[i]['welding_technique']]
            
            # Environmental effect
            preheat_factor = 1 - (df.iloc[i]['preheat_temp_c'] - 20) / 1000
            
            cycles = base_cycles * compatibility * strength_factor * porosity_factor * technique_factor * preheat_factor
            thermal_cycles.append(max(int(cycles), 100))  # Minimum 100 cycles
        
        performance_metrics['thermal_cycles_to_failure'] = thermal_cycles
        
        # Resistance degradation rate (ohms per cycle)
        resistance_degradation = []
        for i in range(len(df)):
            base_degradation = 0.0001  # Base degradation rate
            
            # Material compatibility effect
            compatibility = quality_df.iloc[i]['material_compatibility']
            
            # Surface finish effect
            surface_factors = {'Polished': 0.8, 'Rough': 1.2, 'Coated': 1.0, 'Anodized': 0.9, 'Plated': 0.7}
            surface_factor = surface_factors[df.iloc[i]['surface_finish']]
            
            # Weld quality effect
            porosity_factor = 1 + quality_df.iloc[i]['porosity_percent']
            
            degradation = base_degradation * (1 - compatibility) * surface_factor * porosity_factor
            resistance_degradation.append(degradation)
        
        performance_metrics['resistance_degradation_rate'] = resistance_degradation
        
        # Mechanical strength retention (percentage after cycling)
        strength_retention = []
        for i in range(len(df)):
            base_retention = 0.95  # Base retention percentage
            
            # Material compatibility effect
            compatibility = quality_df.iloc[i]['material_compatibility']
            
            # Weld quality effect
            porosity_factor = 1 - quality_df.iloc[i]['porosity_percent']
            
            # Technique effect
            technique_factors = {'USW': 1.0, 'Laser': 1.1, 'Resistance_Spot': 0.9, 'Friction_Stir': 1.2, 'Electron_Beam': 1.1}
            technique_factor = technique_factors[df.iloc[i]['welding_technique']]
            
            retention = base_retention * compatibility * porosity_factor * technique_factor
            strength_retention.append(min(retention, 1.0))  # Cap at 100%
        
        performance_metrics['strength_retention_percent'] = strength_retention
        
        # Failure mode probability
        failure_modes = []
        for i in range(len(df)):
            # Calculate probabilities for different failure modes
            thermal_fatigue_prob = 0.3 * (1 - quality_df.iloc[i]['material_compatibility'])
            mechanical_fatigue_prob = 0.4 * (1 - quality_df.iloc[i]['weld_strength_mpa'] / 200)
            corrosion_prob = 0.2 * quality_df.iloc[i]['porosity_percent']
            delamination_prob = 0.1 * (1 - quality_df.iloc[i]['penetration_depth_mm'])
            
            # Normalize probabilities
            total_prob = thermal_fatigue_prob + mechanical_fatigue_prob + corrosion_prob + delamination_prob
            if total_prob > 0:
                thermal_fatigue_prob /= total_prob
                mechanical_fatigue_prob /= total_prob
                corrosion_prob /= total_prob
                delamination_prob /= total_prob
            
            # Select most likely failure mode
            probs = [thermal_fatigue_prob, mechanical_fatigue_prob, corrosion_prob, delamination_prob]
            failure_mode = ['Thermal_Fatigue', 'Mechanical_Fatigue', 'Corrosion', 'Delamination'][np.argmax(probs)]
            failure_modes.append(failure_mode)
        
        performance_metrics['primary_failure_mode'] = failure_modes
        
        return pd.DataFrame(performance_metrics)
    
    def generate_dataset(self):
        """Generate the complete welding dataset"""
        print("Generating input parameters...")
        input_df = self.generate_input_parameters()
        
        print("Calculating quality metrics...")
        quality_df = self.calculate_weld_quality_metrics(input_df)
        
        print("Calculating performance metrics...")
        performance_df = self.calculate_performance_metrics(input_df, quality_df)
        
        # Combine all data
        complete_df = pd.concat([input_df, quality_df, performance_df], axis=1)
        
        # Add some noise to make it more realistic
        noise_columns = ['weld_strength_mpa', 'contact_resistance_ohm', 'weld_width_mm', 
                        'penetration_depth_mm', 'porosity_percent', 'thermal_cycles_to_failure',
                        'resistance_degradation_rate', 'strength_retention_percent']
        
        for col in noise_columns:
            if col in complete_df.columns:
                noise = np.random.normal(0, 0.05, len(complete_df))
                complete_df[col] = complete_df[col] * (1 + noise)
        
        return complete_df
    
    def save_dataset(self, df, filename='welding_dataset.csv'):
        """Save dataset to CSV"""
        df.to_csv(filename, index=False)
        print(f"Dataset saved to {filename}")
        return filename
    
    def generate_summary_statistics(self, df):
        """Generate summary statistics and visualizations"""
        print("\n=== DATASET SUMMARY ===")
        print(f"Total samples: {len(df)}")
        print(f"Total features: {len(df.columns)}")
        
        print("\n=== INPUT PARAMETERS ===")
        input_cols = ['anode_material', 'cathode_material', 'tab_thickness_um', 'surface_finish',
                     'welding_technique', 'power_w', 'amplitude_um', 'force_n', 'time_ms',
                     'speed_mm_s', 'pulse_frequency_hz', 'preheat_temp_c']
        
        for col in input_cols:
            if col in df.columns:
                if df[col].dtype == 'object':
                    print(f"{col}: {df[col].value_counts().to_dict()}")
                else:
                    print(f"{col}: mean={df[col].mean():.2f}, std={df[col].std():.2f}")
        
        print("\n=== QUALITY METRICS ===")
        quality_cols = ['material_compatibility', 'weld_strength_mpa', 'contact_resistance_ohm',
                       'weld_width_mm', 'penetration_depth_mm', 'porosity_percent']
        
        for col in quality_cols:
            if col in df.columns:
                print(f"{col}: mean={df[col].mean():.2f}, std={df[col].std():.2f}")
        
        print("\n=== PERFORMANCE METRICS ===")
        performance_cols = ['thermal_cycles_to_failure', 'resistance_degradation_rate',
                           'strength_retention_percent', 'primary_failure_mode']
        
        for col in performance_cols:
            if col in df.columns:
                if df[col].dtype == 'object':
                    print(f"{col}: {df[col].value_counts().to_dict()}")
                else:
                    print(f"{col}: mean={df[col].mean():.2f}, std={df[col].std():.2f}")

def main():
    # Generate dataset
    generator = WeldingDatasetGenerator(n_samples=10000, random_state=42)
    dataset = generator.generate_dataset()
    
    # Save dataset
    filename = generator.save_dataset(dataset)
    
    # Generate summary
    generator.generate_summary_statistics(dataset)
    
    # Create visualizations
    plt.figure(figsize=(15, 10))
    
    # Correlation heatmap
    plt.subplot(2, 3, 1)
    numeric_cols = dataset.select_dtypes(include=[np.number]).columns
    correlation_matrix = dataset[numeric_cols].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
    plt.title('Feature Correlation Matrix')
    
    # Material distribution
    plt.subplot(2, 3, 2)
    material_counts = dataset['anode_material'].value_counts()
    plt.pie(material_counts.values, labels=material_counts.index, autopct='%1.1f%%')
    plt.title('Anode Material Distribution')
    
    # Welding technique distribution
    plt.subplot(2, 3, 3)
    technique_counts = dataset['welding_technique'].value_counts()
    plt.bar(technique_counts.index, technique_counts.values)
    plt.title('Welding Technique Distribution')
    plt.xticks(rotation=45)
    
    # Weld strength distribution
    plt.subplot(2, 3, 4)
    plt.hist(dataset['weld_strength_mpa'], bins=50, alpha=0.7)
    plt.title('Weld Strength Distribution')
    plt.xlabel('Weld Strength (MPa)')
    
    # Thermal cycles distribution
    plt.subplot(2, 3, 5)
    plt.hist(dataset['thermal_cycles_to_failure'], bins=50, alpha=0.7)
    plt.title('Thermal Cycles to Failure')
    plt.xlabel('Number of Cycles')
    
    # Failure mode distribution
    plt.subplot(2, 3, 6)
    failure_counts = dataset['primary_failure_mode'].value_counts()
    plt.bar(failure_counts.index, failure_counts.values)
    plt.title('Primary Failure Mode Distribution')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('welding_dataset_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"\nDataset generation complete! Saved to {filename}")
    print("Analysis plots saved to 'welding_dataset_analysis.png'")

if __name__ == "__main__":
    main()