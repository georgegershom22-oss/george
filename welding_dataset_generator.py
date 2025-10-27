import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class WeldingDatasetGenerator:
    def __init__(self, n_samples=10000, random_state=42):
        self.n_samples = n_samples
        self.random_state = random_state
        np.random.seed(random_state)
        
        # Define material properties and constraints
        self.materials = {
            'Cu': {'density': 8.96, 'thermal_conductivity': 401, 'melting_point': 1085, 'electrical_conductivity': 59.6},
            'Al': {'density': 2.70, 'thermal_conductivity': 237, 'melting_point': 660, 'electrical_conductivity': 37.7},
            'Ni': {'density': 8.90, 'thermal_conductivity': 91, 'melting_point': 1455, 'electrical_conductivity': 14.3},
            'Ti': {'density': 4.51, 'thermal_conductivity': 22, 'melting_point': 1668, 'electrical_conductivity': 2.4}
        }
        
        self.welding_techniques = ['USW', 'Laser', 'Resistance_Spot', 'Friction_Stir']
        self.surface_finishes = ['Polished', 'Rough', 'Coated_Ag', 'Coated_Ni', 'Anodized']
        
    def generate_input_parameters(self):
        """Generate realistic input parameters for welding"""
        data = {}
        
        # Base Materials (categorical)
        data['anode_material'] = np.random.choice(list(self.materials.keys()), self.n_samples)
        data['cathode_material'] = np.random.choice(list(self.materials.keys()), self.n_samples)
        
        # Tab Thickness (realistic range: 50-500 µm)
        data['tab_thickness_um'] = np.random.uniform(50, 500, self.n_samples)
        
        # Surface Finish
        data['surface_finish'] = np.random.choice(self.surface_finishes, self.n_samples)
        
        # Welding Technique
        data['welding_technique'] = np.random.choice(self.welding_techniques, self.n_samples)
        
        # Welding Process Parameters (technique-dependent)
        for i in range(self.n_samples):
            technique = data['welding_technique'][i]
            
            if technique == 'USW':
                data.setdefault('power_w', []).append(np.random.uniform(100, 2000))
                data.setdefault('amplitude_um', []).append(np.random.uniform(10, 100))
                data.setdefault('force_n', []).append(np.random.uniform(50, 500))
                data.setdefault('time_ms', []).append(np.random.uniform(50, 500))
                data.setdefault('speed_mm_s', []).append(0)  # Not applicable for USW
                data.setdefault('pulse_frequency_hz', []).append(np.random.uniform(20, 40))
                
            elif technique == 'Laser':
                data.setdefault('power_w', []).append(np.random.uniform(50, 1000))
                data.setdefault('amplitude_um', []).append(0)  # Not applicable for laser
                data.setdefault('force_n', []).append(np.random.uniform(10, 100))
                data.setdefault('time_ms', []).append(np.random.uniform(1, 50))
                data.setdefault('speed_mm_s', []).append(np.random.uniform(1, 100))
                data.setdefault('pulse_frequency_hz', []).append(np.random.uniform(1, 1000))
                
            elif technique == 'Resistance_Spot':
                data.setdefault('power_w', []).append(np.random.uniform(200, 5000))
                data.setdefault('amplitude_um', []).append(0)  # Not applicable
                data.setdefault('force_n', []).append(np.random.uniform(100, 2000))
                data.setdefault('time_ms', []).append(np.random.uniform(10, 200))
                data.setdefault('speed_mm_s', []).append(0)  # Not applicable
                data.setdefault('pulse_frequency_hz', []).append(0)  # Not applicable
                
            else:  # Friction_Stir
                data.setdefault('power_w', []).append(np.random.uniform(1000, 5000))
                data.setdefault('amplitude_um', []).append(0)  # Not applicable
                data.setdefault('force_n', []).append(np.random.uniform(500, 5000))
                data.setdefault('time_ms', []).append(np.random.uniform(100, 1000))
                data.setdefault('speed_mm_s', []).append(np.random.uniform(10, 200))
                data.setdefault('pulse_frequency_hz', []).append(0)  # Not applicable
        
        # Environmental Parameters
        data['preheat_temperature_c'] = np.random.uniform(20, 200, self.n_samples)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Add derived parameters
        df['material_compatibility'] = self._calculate_material_compatibility(df)
        df['thermal_mismatch'] = self._calculate_thermal_mismatch(df)
        df['electrical_mismatch'] = self._calculate_electrical_mismatch(df)
        
        return df
    
    def _calculate_material_compatibility(self, df):
        """Calculate material compatibility score"""
        compatibility = []
        for i in range(len(df)):
            anode = df.iloc[i]['anode_material']
            cathode = df.iloc[i]['cathode_material']
            
            # Simple compatibility based on melting point difference
            mp_diff = abs(self.materials[anode]['melting_point'] - self.materials[cathode]['melting_point'])
            comp_score = max(0, 1 - mp_diff / 1000)  # Normalize to 0-1
            compatibility.append(comp_score)
        
        return compatibility
    
    def _calculate_thermal_mismatch(self, df):
        """Calculate thermal expansion mismatch"""
        thermal_mismatch = []
        for i in range(len(df)):
            anode = df.iloc[i]['anode_material']
            cathode = df.iloc[i]['cathode_material']
            
            # Thermal conductivity ratio
            k_ratio = self.materials[anode]['thermal_conductivity'] / self.materials[cathode]['thermal_conductivity']
            mismatch = abs(np.log(k_ratio))  # Log scale for better distribution
            thermal_mismatch.append(mismatch)
        
        return thermal_mismatch
    
    def _calculate_electrical_mismatch(self, df):
        """Calculate electrical conductivity mismatch"""
        electrical_mismatch = []
        for i in range(len(df)):
            anode = df.iloc[i]['anode_material']
            cathode = df.iloc[i]['cathode_material']
            
            # Electrical conductivity ratio
            e_ratio = self.materials[anode]['electrical_conductivity'] / self.materials[cathode]['electrical_conductivity']
            mismatch = abs(np.log(e_ratio))
            electrical_mismatch.append(mismatch)
        
        return electrical_mismatch
    
    def generate_quality_metrics(self, df):
        """Generate realistic quality metrics based on input parameters"""
        quality_metrics = pd.DataFrame(index=df.index)
        
        # Weld Strength (MPa) - primary quality metric
        base_strength = 50 + np.random.normal(0, 10, self.n_samples)
        
        # Material compatibility effect
        comp_effect = df['material_compatibility'] * 30
        
        # Process parameter effects
        power_effect = np.clip(df['power_w'] / 1000, 0, 1) * 20
        force_effect = np.clip(df['force_n'] / 1000, 0, 1) * 15
        
        # Technique-specific effects
        technique_effects = {
            'USW': 10,
            'Laser': 15,
            'Resistance_Spot': 5,
            'Friction_Stir': 20
        }
        tech_effect = df['welding_technique'].map(technique_effects)
        
        quality_metrics['weld_strength_mpa'] = np.clip(
            base_strength + comp_effect + power_effect + force_effect + tech_effect + np.random.normal(0, 5, self.n_samples),
            10, 150
        )
        
        # Contact Resistance (mΩ) - lower is better
        base_resistance = 0.5 + np.random.exponential(0.3, self.n_samples)
        
        # Surface finish effect
        finish_effects = {
            'Polished': -0.2,
            'Rough': 0.3,
            'Coated_Ag': -0.4,
            'Coated_Ni': -0.1,
            'Anodized': 0.5
        }
        finish_effect = df['surface_finish'].map(finish_effects)
        
        # Electrical mismatch effect
        elec_effect = df['electrical_mismatch'] * 0.1
        
        quality_metrics['contact_resistance_mohm'] = np.clip(
            base_resistance + finish_effect + elec_effect + np.random.normal(0, 0.1, self.n_samples),
            0.1, 2.0
        )
        
        # Weld Penetration Depth (µm)
        base_penetration = 50 + np.random.exponential(20, self.n_samples)
        
        # Power and force effects
        power_pen_effect = np.clip(df['power_w'] / 1000, 0, 1) * 30
        force_pen_effect = np.clip(df['force_n'] / 1000, 0, 1) * 20
        
        quality_metrics['penetration_depth_um'] = np.clip(
            base_penetration + power_pen_effect + force_pen_effect + np.random.normal(0, 10, self.n_samples),
            20, 200
        )
        
        # Weld Width (µm)
        base_width = 100 + np.random.exponential(30, self.n_samples)
        
        # Technique and power effects
        width_tech_effects = {
            'USW': 0,
            'Laser': 20,
            'Resistance_Spot': -10,
            'Friction_Stir': 30
        }
        width_tech_effect = df['welding_technique'].map(width_tech_effects)
        
        quality_metrics['weld_width_um'] = np.clip(
            base_width + width_tech_effect + power_pen_effect + np.random.normal(0, 15, self.n_samples),
            50, 300
        )
        
        # Porosity (%) - lower is better
        base_porosity = np.random.exponential(2, self.n_samples)
        
        # Process parameter effects
        power_por_effect = -np.clip(df['power_w'] / 1000, 0, 1) * 1.5
        force_por_effect = -np.clip(df['force_n'] / 1000, 0, 1) * 1.0
        
        quality_metrics['porosity_percent'] = np.clip(
            base_porosity + power_por_effect + force_por_effect + np.random.normal(0, 0.5, self.n_samples),
            0.1, 10.0
        )
        
        # Microhardness (HV)
        base_hardness = 80 + np.random.normal(0, 15, self.n_samples)
        
        # Material and process effects
        material_hardness = {
            'Cu': 0,
            'Al': -20,
            'Ni': 30,
            'Ti': 40
        }
        mat_hardness = df['anode_material'].map(material_hardness)
        
        quality_metrics['microhardness_hv'] = np.clip(
            base_hardness + mat_hardness + power_effect + np.random.normal(0, 8, self.n_samples),
            40, 200
        )
        
        return quality_metrics
    
    def generate_performance_metrics(self, df, quality_metrics):
        """Generate performance metrics under extreme temperature cycling"""
        performance_metrics = pd.DataFrame(index=df.index)
        
        # Thermal Cycling Performance (cycles to failure)
        base_cycles = 1000 + np.random.exponential(500, self.n_samples)
        
        # Quality metric effects
        strength_effect = (quality_metrics['weld_strength_mpa'] - 50) * 20
        porosity_effect = -quality_metrics['porosity_percent'] * 50
        resistance_effect = -quality_metrics['contact_resistance_mohm'] * 200
        
        # Material compatibility effect
        comp_effect = df['material_compatibility'] * 1000
        
        # Thermal mismatch effect (negative)
        thermal_effect = -df['thermal_mismatch'] * 200
        
        performance_metrics['thermal_cycles_to_failure'] = np.clip(
            base_cycles + strength_effect + porosity_effect + resistance_effect + comp_effect + thermal_effect + np.random.normal(0, 100, self.n_samples),
            100, 10000
        )
        
        # Resistance Degradation Rate (%/cycle)
        base_degradation = 0.001 + np.random.exponential(0.0005, self.n_samples)
        
        # Quality and material effects
        porosity_degradation = quality_metrics['porosity_percent'] * 0.0002
        thermal_degradation = df['thermal_mismatch'] * 0.0001
        electrical_degradation = df['electrical_mismatch'] * 0.0001
        
        performance_metrics['resistance_degradation_rate_percent_per_cycle'] = np.clip(
            base_degradation + porosity_degradation + thermal_degradation + electrical_degradation + np.random.normal(0, 0.0001, self.n_samples),
            0.0001, 0.01
        )
        
        # Mechanical Degradation Rate (%/cycle)
        base_mech_degradation = 0.0005 + np.random.exponential(0.0003, self.n_samples)
        
        # Quality effects
        strength_degradation = -(quality_metrics['weld_strength_mpa'] - 50) * 0.00001
        hardness_degradation = -(quality_metrics['microhardness_hv'] - 80) * 0.000005
        
        performance_metrics['mechanical_degradation_rate_percent_per_cycle'] = np.clip(
            base_mech_degradation + strength_degradation + hardness_degradation + np.random.normal(0, 0.0001, self.n_samples),
            0.0001, 0.005
        )
        
        # Temperature Coefficient of Resistance (ppm/°C)
        base_tcr = 100 + np.random.normal(0, 20, self.n_samples)
        
        # Material and quality effects
        material_tcr = {
            'Cu': 0,
            'Al': 20,
            'Ni': -10,
            'Ti': 30
        }
        mat_tcr = df['anode_material'].map(material_tcr)
        
        quality_tcr = quality_metrics['contact_resistance_mohm'] * 10
        
        performance_metrics['temperature_coefficient_resistance_ppm_per_c'] = np.clip(
            base_tcr + mat_tcr + quality_tcr + np.random.normal(0, 10, self.n_samples),
            50, 300
        )
        
        # Creep Rate (µm/cycle)
        base_creep = 0.01 + np.random.exponential(0.005, self.n_samples)
        
        # Process and quality effects
        power_creep = df['power_w'] / 10000
        force_creep = df['force_n'] / 10000
        thermal_creep = df['thermal_mismatch'] * 0.01
        
        performance_metrics['creep_rate_um_per_cycle'] = np.clip(
            base_creep + power_creep + force_creep + thermal_creep + np.random.normal(0, 0.002, self.n_samples),
            0.001, 0.1
        )
        
        return performance_metrics
    
    def generate_complete_dataset(self):
        """Generate the complete welding dataset"""
        print("Generating input parameters...")
        input_params = self.generate_input_parameters()
        
        print("Generating quality metrics...")
        quality_metrics = self.generate_quality_metrics(input_params)
        
        print("Generating performance metrics...")
        performance_metrics = self.generate_performance_metrics(input_params, quality_metrics)
        
        # Combine all datasets
        complete_dataset = pd.concat([input_params, quality_metrics, performance_metrics], axis=1)
        
        # Add some derived features
        complete_dataset['weld_quality_score'] = (
            (complete_dataset['weld_strength_mpa'] / 150) * 0.3 +
            (1 - complete_dataset['contact_resistance_mohm'] / 2) * 0.2 +
            (1 - complete_dataset['porosity_percent'] / 10) * 0.2 +
            (complete_dataset['microhardness_hv'] / 200) * 0.1 +
            (complete_dataset['thermal_cycles_to_failure'] / 10000) * 0.2
        )
        
        complete_dataset['process_efficiency'] = (
            complete_dataset['weld_strength_mpa'] / (complete_dataset['power_w'] / 1000 + 1) * 0.5 +
            (1 - complete_dataset['porosity_percent'] / 10) * 0.5
        )
        
        return complete_dataset
    
    def save_dataset(self, dataset, filename='welding_dataset.csv'):
        """Save dataset to CSV"""
        dataset.to_csv(filename, index=False)
        print(f"Dataset saved to {filename}")
        
        # Also save as Excel with multiple sheets
        with pd.ExcelWriter('welding_dataset.xlsx', engine='openpyxl') as writer:
            # Input parameters
            input_cols = [col for col in dataset.columns if col in [
                'anode_material', 'cathode_material', 'tab_thickness_um', 'surface_finish',
                'welding_technique', 'power_w', 'amplitude_um', 'force_n', 'time_ms',
                'speed_mm_s', 'pulse_frequency_hz', 'preheat_temperature_c',
                'material_compatibility', 'thermal_mismatch', 'electrical_mismatch'
            ]]
            dataset[input_cols].to_excel(writer, sheet_name='Input_Parameters', index=False)
            
            # Quality metrics
            quality_cols = [col for col in dataset.columns if col in [
                'weld_strength_mpa', 'contact_resistance_mohm', 'penetration_depth_um',
                'weld_width_um', 'porosity_percent', 'microhardness_hv'
            ]]
            dataset[quality_cols].to_excel(writer, sheet_name='Quality_Metrics', index=False)
            
            # Performance metrics
            performance_cols = [col for col in dataset.columns if col in [
                'thermal_cycles_to_failure', 'resistance_degradation_rate_percent_per_cycle',
                'mechanical_degradation_rate_percent_per_cycle', 'temperature_coefficient_resistance_ppm_per_c',
                'creep_rate_um_per_cycle'
            ]]
            dataset[performance_cols].to_excel(writer, sheet_name='Performance_Metrics', index=False)
            
            # Complete dataset
            dataset.to_excel(writer, sheet_name='Complete_Dataset', index=False)
        
        print("Dataset also saved as Excel file with multiple sheets")
    
    def generate_visualizations(self, dataset):
        """Generate comprehensive visualizations of the dataset"""
        plt.style.use('seaborn-v0_8')
        fig = plt.figure(figsize=(20, 24))
        
        # 1. Input Parameters Distribution
        plt.subplot(4, 3, 1)
        dataset['welding_technique'].value_counts().plot(kind='bar')
        plt.title('Welding Technique Distribution')
        plt.xticks(rotation=45)
        
        plt.subplot(4, 3, 2)
        dataset['anode_material'].value_counts().plot(kind='bar')
        plt.title('Anode Material Distribution')
        
        plt.subplot(4, 3, 3)
        dataset['surface_finish'].value_counts().plot(kind='bar')
        plt.title('Surface Finish Distribution')
        plt.xticks(rotation=45)
        
        # 2. Quality Metrics Distribution
        plt.subplot(4, 3, 4)
        plt.hist(dataset['weld_strength_mpa'], bins=50, alpha=0.7)
        plt.title('Weld Strength Distribution')
        plt.xlabel('Strength (MPa)')
        
        plt.subplot(4, 3, 5)
        plt.hist(dataset['contact_resistance_mohm'], bins=50, alpha=0.7)
        plt.title('Contact Resistance Distribution')
        plt.xlabel('Resistance (mΩ)')
        
        plt.subplot(4, 3, 6)
        plt.hist(dataset['porosity_percent'], bins=50, alpha=0.7)
        plt.title('Porosity Distribution')
        plt.xlabel('Porosity (%)')
        
        # 3. Performance Metrics Distribution
        plt.subplot(4, 3, 7)
        plt.hist(dataset['thermal_cycles_to_failure'], bins=50, alpha=0.7)
        plt.title('Thermal Cycles to Failure')
        plt.xlabel('Cycles')
        
        plt.subplot(4, 3, 8)
        plt.hist(dataset['resistance_degradation_rate_percent_per_cycle'], bins=50, alpha=0.7)
        plt.title('Resistance Degradation Rate')
        plt.xlabel('%/cycle')
        
        plt.subplot(4, 3, 9)
        plt.hist(dataset['creep_rate_um_per_cycle'], bins=50, alpha=0.7)
        plt.title('Creep Rate')
        plt.xlabel('μm/cycle')
        
        # 4. Correlations
        plt.subplot(4, 3, 10)
        corr_matrix = dataset[['weld_strength_mpa', 'contact_resistance_mohm', 'porosity_percent', 
                              'thermal_cycles_to_failure', 'weld_quality_score']].corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title('Quality-Performance Correlations')
        
        # 5. Process Parameter Effects
        plt.subplot(4, 3, 11)
        technique_strength = dataset.groupby('welding_technique')['weld_strength_mpa'].mean()
        technique_strength.plot(kind='bar')
        plt.title('Average Strength by Technique')
        plt.xticks(rotation=45)
        
        plt.subplot(4, 3, 12)
        plt.scatter(dataset['power_w'], dataset['weld_strength_mpa'], alpha=0.5)
        plt.title('Power vs Weld Strength')
        plt.xlabel('Power (W)')
        plt.ylabel('Strength (MPa)')
        
        plt.tight_layout()
        plt.savefig('welding_dataset_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("Visualizations saved as 'welding_dataset_analysis.png'")
    
    def generate_ml_ready_dataset(self, dataset):
        """Prepare dataset for ML training"""
        # Encode categorical variables
        le_anode = LabelEncoder()
        le_cathode = LabelEncoder()
        le_surface = LabelEncoder()
        le_technique = LabelEncoder()
        
        dataset_ml = dataset.copy()
        dataset_ml['anode_material_encoded'] = le_anode.fit_transform(dataset['anode_material'])
        dataset_ml['cathode_material_encoded'] = le_cathode.fit_transform(dataset['cathode_material'])
        dataset_ml['surface_finish_encoded'] = le_surface.fit_transform(dataset['surface_finish'])
        dataset_ml['welding_technique_encoded'] = le_technique.fit_transform(dataset['welding_technique'])
        
        # Create feature matrix
        feature_cols = [
            'anode_material_encoded', 'cathode_material_encoded', 'tab_thickness_um',
            'surface_finish_encoded', 'welding_technique_encoded', 'power_w',
            'amplitude_um', 'force_n', 'time_ms', 'speed_mm_s', 'pulse_frequency_hz',
            'preheat_temperature_c', 'material_compatibility', 'thermal_mismatch', 'electrical_mismatch'
        ]
        
        X = dataset_ml[feature_cols]
        
        # Create target variables
        y_strength = dataset_ml['weld_strength_mpa']
        y_cycles = dataset_ml['thermal_cycles_to_failure']
        y_quality = dataset_ml['weld_quality_score']
        
        # Split data
        X_train, X_test, y_strength_train, y_strength_test = train_test_split(
            X, y_strength, test_size=0.2, random_state=42
        )
        
        # Train a simple model to demonstrate
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X_train, y_strength_train)
        
        y_pred = rf.predict(X_test)
        mse = mean_squared_error(y_strength_test, y_pred)
        r2 = r2_score(y_strength_test, y_pred)
        
        print(f"\nML Model Performance (Weld Strength Prediction):")
        print(f"R² Score: {r2:.3f}")
        print(f"RMSE: {np.sqrt(mse):.3f} MPa")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': rf.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\nTop 10 Most Important Features:")
        print(feature_importance.head(10))
        
        return X, y_strength, y_cycles, y_quality, feature_importance

def main():
    print("=== Welding Parameter Dataset Generator ===")
    print("Generating comprehensive dataset for ML-driven inverse design...")
    
    # Generate dataset
    generator = WeldingDatasetGenerator(n_samples=10000)
    dataset = generator.generate_complete_dataset()
    
    print(f"\nDataset generated with {len(dataset)} samples")
    print(f"Features: {len(dataset.columns)}")
    
    # Display basic statistics
    print(f"\nDataset Statistics:")
    print(f"Input Parameters: {len([col for col in dataset.columns if col in ['anode_material', 'cathode_material', 'tab_thickness_um', 'surface_finish', 'welding_technique', 'power_w', 'amplitude_um', 'force_n', 'time_ms', 'speed_mm_s', 'pulse_frequency_hz', 'preheat_temperature_c', 'material_compatibility', 'thermal_mismatch', 'electrical_mismatch']])}")
    print(f"Quality Metrics: {len([col for col in dataset.columns if col in ['weld_strength_mpa', 'contact_resistance_mohm', 'penetration_depth_um', 'weld_width_um', 'porosity_percent', 'microhardness_hv']])}")
    print(f"Performance Metrics: {len([col for col in dataset.columns if col in ['thermal_cycles_to_failure', 'resistance_degradation_rate_percent_per_cycle', 'mechanical_degradation_rate_percent_per_cycle', 'temperature_coefficient_resistance_ppm_per_c', 'creep_rate_um_per_cycle']])}")
    
    # Save dataset
    generator.save_dataset(dataset)
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    generator.generate_visualizations(dataset)
    
    # Prepare ML-ready dataset
    print("\nPreparing ML-ready dataset...")
    X, y_strength, y_cycles, y_quality, feature_importance = generator.generate_ml_ready_dataset(dataset)
    
    # Save ML-ready dataset
    ml_dataset = pd.concat([X, y_strength, y_cycles, y_quality], axis=1)
    ml_dataset.to_csv('welding_dataset_ml_ready.csv', index=False)
    print("ML-ready dataset saved as 'welding_dataset_ml_ready.csv'")
    
    # Save feature importance
    feature_importance.to_csv('feature_importance.csv', index=False)
    print("Feature importance saved as 'feature_importance.csv'")
    
    print(f"\n=== Dataset Generation Complete ===")
    print(f"Files generated:")
    print(f"- welding_dataset.csv (complete dataset)")
    print(f"- welding_dataset.xlsx (Excel with multiple sheets)")
    print(f"- welding_dataset_ml_ready.csv (ML-ready format)")
    print(f"- feature_importance.csv (feature importance rankings)")
    print(f"- welding_dataset_analysis.png (comprehensive visualizations)")

if __name__ == "__main__":
    main()