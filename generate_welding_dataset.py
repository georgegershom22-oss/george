"""
ML-Driven Inverse Design of Welding Parameters - Dataset Generator

This script generates a comprehensive dataset for training ML models to predict
optimal welding parameters for extreme-temperature cycling applications.

Dataset Structure:
1. Input Parameters (Design Space) - Controllable welding process variables
2. Characterization & Quality Metrics - Immediate post-weld measurements
3. Performance & Validation Metrics - Long-term thermal cycling performance
"""

import numpy as np
import pandas as pd
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

class WeldingDatasetGenerator:
    """Generate realistic welding parameter dataset with correlations"""
    
    def __init__(self, n_samples=2000):
        self.n_samples = n_samples
        self.data = {}
        
        # Material properties database
        self.material_properties = {
            'Cu': {'conductivity': 400, 'melting_point': 1085, 'thermal_expansion': 16.5},
            'Al': {'conductivity': 237, 'melting_point': 660, 'thermal_expansion': 23.1},
            'Ni': {'conductivity': 91, 'melting_point': 1455, 'thermal_expansion': 13.4},
            'Steel': {'conductivity': 50, 'melting_point': 1510, 'thermal_expansion': 11.0},
            'Ti': {'conductivity': 22, 'melting_point': 1668, 'thermal_expansion': 8.6}
        }
        
    def generate_input_parameters(self):
        """Part 1: Generate input parameters (design space)"""
        
        # Base Materials
        anode_materials = ['Cu', 'Cu', 'Cu', 'Al', 'Ni']  # Cu-heavy for battery applications
        cathode_materials = ['Al', 'Al', 'Cu', 'Ni', 'Steel']
        
        self.data['Anode_Material'] = np.random.choice(anode_materials, self.n_samples)
        self.data['Cathode_Material'] = np.random.choice(cathode_materials, self.n_samples)
        
        # Tab thickness (typical range for battery tabs)
        self.data['Anode_Thickness_um'] = np.random.uniform(100, 500, self.n_samples)
        self.data['Cathode_Thickness_um'] = np.random.uniform(100, 500, self.n_samples)
        
        # Surface finish / coating
        surface_finishes = ['Bare', 'Electroplated', 'Anodized', 'Passivated', 'Coated']
        self.data['Surface_Finish'] = np.random.choice(surface_finishes, self.n_samples)
        
        # Welding technique
        welding_techniques = ['Ultrasonic', 'Laser', 'Resistance_Spot', 'TIG', 'Friction_Stir']
        self.data['Welding_Technique'] = np.random.choice(welding_techniques, self.n_samples)
        
        # Initialize technique-specific parameters
        self.data['Power_W'] = np.zeros(self.n_samples)
        self.data['Amplitude_um'] = np.zeros(self.n_samples)
        self.data['Force_N'] = np.zeros(self.n_samples)
        self.data['Pressure_MPa'] = np.zeros(self.n_samples)
        self.data['Time_ms'] = np.zeros(self.n_samples)
        self.data['Speed_mm_s'] = np.zeros(self.n_samples)
        self.data['Pulse_Frequency_Hz'] = np.zeros(self.n_samples)
        self.data['Pulse_Energy_J'] = np.zeros(self.n_samples)
        
        # Generate technique-specific parameters
        for i in range(self.n_samples):
            technique = self.data['Welding_Technique'][i]
            
            if technique == 'Ultrasonic':
                self.data['Power_W'][i] = np.random.uniform(1000, 3000)
                self.data['Amplitude_um'][i] = np.random.uniform(20, 60)
                self.data['Force_N'][i] = np.random.uniform(500, 2000)
                self.data['Pressure_MPa'][i] = self.data['Force_N'][i] / 100  # Approximate
                self.data['Time_ms'][i] = np.random.uniform(100, 1000)
                
            elif technique == 'Laser':
                self.data['Power_W'][i] = np.random.uniform(500, 3000)
                self.data['Speed_mm_s'][i] = np.random.uniform(10, 100)
                self.data['Pulse_Frequency_Hz'][i] = np.random.uniform(10, 100)
                self.data['Pulse_Energy_J'][i] = np.random.uniform(1, 20)
                self.data['Time_ms'][i] = np.random.uniform(50, 500)
                
            elif technique == 'Resistance_Spot':
                self.data['Power_W'][i] = np.random.uniform(2000, 5000)
                self.data['Force_N'][i] = np.random.uniform(1000, 3000)
                self.data['Pressure_MPa'][i] = self.data['Force_N'][i] / 80
                self.data['Time_ms'][i] = np.random.uniform(200, 1500)
                
            elif technique == 'TIG':
                self.data['Power_W'][i] = np.random.uniform(500, 2000)
                self.data['Speed_mm_s'][i] = np.random.uniform(5, 50)
                self.data['Time_ms'][i] = np.random.uniform(1000, 5000)
                
            elif technique == 'Friction_Stir':
                self.data['Force_N'][i] = np.random.uniform(2000, 5000)
                self.data['Speed_mm_s'][i] = np.random.uniform(1, 20)
                self.data['Time_ms'][i] = np.random.uniform(5000, 20000)
        
        # Environmental parameters
        self.data['Preheat_Temperature_C'] = np.random.uniform(20, 150, self.n_samples)
        self.data['Ambient_Humidity_%'] = np.random.uniform(30, 70, self.n_samples)
        self.data['Chamber_Atmosphere'] = np.random.choice(['Air', 'Argon', 'Nitrogen', 'Vacuum'], self.n_samples)
        
        # Additional process parameters
        self.data['Cooling_Rate_C_per_s'] = np.random.uniform(5, 50, self.n_samples)
        self.data['Electrode_Material'] = np.random.choice(['Copper', 'Tungsten', 'Molybdenum'], self.n_samples)
        self.data['Gap_Distance_mm'] = np.random.uniform(0, 0.5, self.n_samples)
        
    def calculate_material_mismatch(self, idx):
        """Calculate material property mismatch factor"""
        anode = self.data['Anode_Material'][idx]
        cathode = self.data['Cathode_Material'][idx]
        
        if anode not in self.material_properties or cathode not in self.material_properties:
            return 0.5
        
        anode_props = self.material_properties[anode]
        cathode_props = self.material_properties[cathode]
        
        # Calculate thermal expansion mismatch
        expansion_mismatch = abs(anode_props['thermal_expansion'] - cathode_props['thermal_expansion']) / 20
        
        # Calculate conductivity mismatch
        conductivity_mismatch = abs(anode_props['conductivity'] - cathode_props['conductivity']) / 400
        
        # Calculate melting point difference
        melting_mismatch = abs(anode_props['melting_point'] - cathode_props['melting_point']) / 1000
        
        return (expansion_mismatch + conductivity_mismatch + melting_mismatch) / 3
    
    def generate_characterization_metrics(self):
        """Part 2: Generate characterization & quality metrics (forward problem outputs)"""
        
        # Initialize arrays
        n = self.n_samples
        
        # Calculate quality factors based on input parameters
        quality_factors = np.zeros(n)
        
        for i in range(n):
            # Base quality factor
            qf = 0.5
            
            # Material compatibility
            material_mismatch = self.calculate_material_mismatch(i)
            qf -= material_mismatch * 0.3
            
            # Technique-specific quality adjustments
            technique = self.data['Welding_Technique'][i]
            
            if technique == 'Ultrasonic':
                # Optimal power range: 1500-2500W
                power = self.data['Power_W'][i]
                if 1500 <= power <= 2500:
                    qf += 0.2
                else:
                    qf -= abs(power - 2000) / 5000
                
                # Optimal amplitude: 30-45 um
                amplitude = self.data['Amplitude_um'][i]
                if 30 <= amplitude <= 45:
                    qf += 0.15
                else:
                    qf -= abs(amplitude - 37.5) / 100
                    
            elif technique == 'Laser':
                # Optimal power: 1000-2000W
                power = self.data['Power_W'][i]
                if 1000 <= power <= 2000:
                    qf += 0.2
                    
                # Speed-power correlation
                speed = self.data['Speed_mm_s'][i]
                if 30 <= speed <= 60:
                    qf += 0.15
                    
            elif technique == 'Resistance_Spot':
                # Higher power and pressure generally better
                if self.data['Power_W'][i] > 3500 and self.data['Pressure_MPa'][i] > 25:
                    qf += 0.25
                    
            # Surface finish effect
            if self.data['Surface_Finish'][i] in ['Electroplated', 'Anodized']:
                qf += 0.1
            elif self.data['Surface_Finish'][i] == 'Bare':
                qf -= 0.05
                
            # Preheat effect
            preheat = self.data['Preheat_Temperature_C'][i]
            if 60 <= preheat <= 100:
                qf += 0.1
            elif preheat > 120:
                qf -= 0.1
                
            # Atmosphere effect
            if self.data['Chamber_Atmosphere'][i] in ['Argon', 'Nitrogen', 'Vacuum']:
                qf += 0.1
                
            # Thickness effect - similar thicknesses are better
            thickness_diff = abs(self.data['Anode_Thickness_um'][i] - self.data['Cathode_Thickness_um'][i])
            qf -= thickness_diff / 1000
            
            quality_factors[i] = np.clip(qf, 0, 1)
        
        # Generate correlated quality metrics
        noise_level = 0.15
        
        # Weld Strength (tensile)
        self.data['Weld_Strength_MPa'] = 50 + quality_factors * 150 + np.random.normal(0, noise_level * 50, n)
        self.data['Weld_Strength_MPa'] = np.clip(self.data['Weld_Strength_MPa'], 10, 250)
        
        # Joint Resistance (lower is better)
        self.data['Joint_Resistance_mOhm'] = 10 - quality_factors * 8 + np.random.normal(0, noise_level * 2, n)
        self.data['Joint_Resistance_mOhm'] = np.clip(self.data['Joint_Resistance_mOhm'], 0.5, 15)
        
        # Nugget Diameter
        self.data['Nugget_Diameter_mm'] = 2 + quality_factors * 4 + np.random.normal(0, noise_level * 0.5, n)
        self.data['Nugget_Diameter_mm'] = np.clip(self.data['Nugget_Diameter_mm'], 1, 8)
        
        # Penetration Depth
        self.data['Penetration_Depth_um'] = 100 + quality_factors * 300 + np.random.normal(0, noise_level * 50, n)
        self.data['Penetration_Depth_um'] = np.clip(self.data['Penetration_Depth_um'], 50, 500)
        
        # Heat Affected Zone (HAZ) Width - smaller is often better
        self.data['HAZ_Width_mm'] = 5 - quality_factors * 3 + np.random.normal(0, noise_level * 0.5, n)
        self.data['HAZ_Width_mm'] = np.clip(self.data['HAZ_Width_mm'], 0.5, 6)
        
        # Porosity (lower is better)
        self.data['Porosity_%'] = 15 - quality_factors * 12 + np.random.normal(0, noise_level * 3, n)
        self.data['Porosity_%'] = np.clip(self.data['Porosity_%'], 0.1, 20)
        
        # Surface Roughness (lower is better for most applications)
        self.data['Surface_Roughness_um'] = 10 - quality_factors * 7 + np.random.normal(0, noise_level * 2, n)
        self.data['Surface_Roughness_um'] = np.clip(self.data['Surface_Roughness_um'], 0.5, 15)
        
        # Microhardness
        self.data['Microhardness_HV'] = 100 + quality_factors * 200 + np.random.normal(0, noise_level * 30, n)
        self.data['Microhardness_HV'] = np.clip(self.data['Microhardness_HV'], 50, 400)
        
        # Grain Size (smaller usually better)
        self.data['Grain_Size_um'] = 50 - quality_factors * 30 + np.random.normal(0, noise_level * 10, n)
        self.data['Grain_Size_um'] = np.clip(self.data['Grain_Size_um'], 5, 60)
        
        # Visual Quality Score (1-10)
        self.data['Visual_Quality_Score'] = 3 + quality_factors * 6 + np.random.normal(0, noise_level * 1.5, n)
        self.data['Visual_Quality_Score'] = np.clip(self.data['Visual_Quality_Score'], 1, 10)
        
        # Interfacial Bonding Quality (%)
        self.data['Interfacial_Bonding_%'] = 40 + quality_factors * 55 + np.random.normal(0, noise_level * 10, n)
        self.data['Interfacial_Bonding_%'] = np.clip(self.data['Interfacial_Bonding_%'], 20, 100)
        
        # Crack Density (immediate)
        self.data['Initial_Crack_Density_per_mm2'] = 2 - quality_factors * 1.8 + np.random.normal(0, noise_level * 0.3, n)
        self.data['Initial_Crack_Density_per_mm2'] = np.clip(self.data['Initial_Crack_Density_per_mm2'], 0, 3)
        
        # Residual Stress
        self.data['Residual_Stress_MPa'] = 150 - quality_factors * 100 + np.random.normal(0, noise_level * 30, n)
        self.data['Residual_Stress_MPa'] = np.clip(self.data['Residual_Stress_MPa'], 10, 250)
        
        # Store quality factors for next step
        self.quality_factors = quality_factors
        
    def generate_performance_metrics(self):
        """Part 3: Generate performance & validation metrics (inverse design targets)"""
        
        n = self.n_samples
        noise_level = 0.12
        
        # Use quality factors from characterization step
        qf = self.quality_factors
        
        # Additional performance factor based on material properties
        performance_factors = qf.copy()
        
        for i in range(n):
            material_mismatch = self.calculate_material_mismatch(i)
            
            # Thermal cycling performance heavily affected by thermal expansion mismatch
            performance_factors[i] -= material_mismatch * 0.4
            
            # Surface finish critical for long-term performance
            if self.data['Surface_Finish'][i] in ['Electroplated', 'Coated']:
                performance_factors[i] += 0.15
                
            # Controlled atmosphere helps
            if self.data['Chamber_Atmosphere'][i] in ['Argon', 'Nitrogen', 'Vacuum']:
                performance_factors[i] += 0.1
                
            # Lower porosity is critical
            if self.data['Porosity_%'][i] < 3:
                performance_factors[i] += 0.15
            elif self.data['Porosity_%'][i] > 10:
                performance_factors[i] -= 0.2
                
            # Low residual stress helps
            if self.data['Residual_Stress_MPa'][i] < 80:
                performance_factors[i] += 0.1
        
        performance_factors = np.clip(performance_factors, 0, 1)
        
        # Thermal Cycle Count to Failure (primary target)
        self.data['Thermal_Cycles_to_Failure'] = (500 + performance_factors * 9500 + 
                                                   np.random.normal(0, noise_level * 2000, n)).astype(int)
        self.data['Thermal_Cycles_to_Failure'] = np.clip(self.data['Thermal_Cycles_to_Failure'], 100, 12000)
        
        # Retained Strength After Cycling (%)
        self.data['Retained_Strength_%'] = 30 + performance_factors * 65 + np.random.normal(0, noise_level * 15, n)
        self.data['Retained_Strength_%'] = np.clip(self.data['Retained_Strength_%'], 20, 100)
        
        # Resistance Increase After Cycling (%)
        self.data['Resistance_Increase_%'] = 200 - performance_factors * 180 + np.random.normal(0, noise_level * 40, n)
        self.data['Resistance_Increase_%'] = np.clip(self.data['Resistance_Increase_%'], 5, 250)
        
        # Crack Density After Cycling
        self.data['Final_Crack_Density_per_mm2'] = 5 - performance_factors * 4 + np.random.normal(0, noise_level * 1, n)
        self.data['Final_Crack_Density_per_mm2'] = np.clip(self.data['Final_Crack_Density_per_mm2'], 0.1, 8)
        
        # Fatigue Life (cycles at room temperature)
        self.data['Fatigue_Life_Cycles'] = (10000 + performance_factors * 90000 + 
                                            np.random.normal(0, noise_level * 20000, n)).astype(int)
        self.data['Fatigue_Life_Cycles'] = np.clip(self.data['Fatigue_Life_Cycles'], 5000, 150000)
        
        # Maximum Operating Temperature before failure
        self.data['Max_Operating_Temp_C'] = 150 + performance_factors * 200 + np.random.normal(0, noise_level * 40, n)
        self.data['Max_Operating_Temp_C'] = np.clip(self.data['Max_Operating_Temp_C'], 100, 400)
        
        # Thermal Shock Resistance Score (1-10)
        self.data['Thermal_Shock_Score'] = 2 + performance_factors * 7 + np.random.normal(0, noise_level * 1.5, n)
        self.data['Thermal_Shock_Score'] = np.clip(self.data['Thermal_Shock_Score'], 1, 10)
        
        # Intermetallic Compound Growth Rate (um/1000 cycles) - lower is better
        self.data['IMC_Growth_Rate_um_per_1000cycles'] = 5 - performance_factors * 4 + np.random.normal(0, noise_level * 1, n)
        self.data['IMC_Growth_Rate_um_per_1000cycles'] = np.clip(self.data['IMC_Growth_Rate_um_per_1000cycles'], 0.1, 6)
        
        # Delamination Percentage After Cycling
        self.data['Delamination_%'] = 50 - performance_factors * 45 + np.random.normal(0, noise_level * 10, n)
        self.data['Delamination_%'] = np.clip(self.data['Delamination_%'], 0, 60)
        
        # Oxidation Resistance Score (1-10)
        self.data['Oxidation_Resistance_Score'] = 3 + performance_factors * 6 + np.random.normal(0, noise_level * 1.2, n)
        self.data['Oxidation_Resistance_Score'] = np.clip(self.data['Oxidation_Resistance_Score'], 1, 10)
        
        # Energy Efficiency Loss (%)
        self.data['Energy_Efficiency_Loss_%'] = 40 - performance_factors * 35 + np.random.normal(0, noise_level * 8, n)
        self.data['Energy_Efficiency_Loss_%'] = np.clip(self.data['Energy_Efficiency_Loss_%'], 2, 50)
        
        # Overall Performance Score (composite metric)
        self.data['Overall_Performance_Score'] = 20 + performance_factors * 75 + np.random.normal(0, noise_level * 10, n)
        self.data['Overall_Performance_Score'] = np.clip(self.data['Overall_Performance_Score'], 10, 100)
        
        # Cost estimate (USD per joint) - roughly inversely related to performance
        base_cost = np.random.uniform(0.05, 0.15, n)
        technique_cost = {'Ultrasonic': 0.1, 'Laser': 0.3, 'Resistance_Spot': 0.08, 
                         'TIG': 0.2, 'Friction_Stir': 0.25}
        for i in range(n):
            self.data['Cost_per_Joint_USD'] = base_cost
        
        # Add quality/performance indicators
        self.data['Pass_Quality_Threshold'] = (self.data['Visual_Quality_Score'] >= 6).astype(int)
        self.data['Pass_Performance_Threshold'] = (self.data['Thermal_Cycles_to_Failure'] >= 3000).astype(int)
        self.data['Optimal_Design'] = ((self.data['Pass_Quality_Threshold'] == 1) & 
                                       (self.data['Pass_Performance_Threshold'] == 1)).astype(int)
        
    def generate_dataset(self):
        """Generate complete dataset"""
        print("Generating ML-Driven Inverse Design Welding Dataset...")
        print(f"Number of samples: {self.n_samples}")
        print()
        
        print("Step 1/3: Generating input parameters (design space)...")
        self.generate_input_parameters()
        
        print("Step 2/3: Generating characterization & quality metrics...")
        self.generate_characterization_metrics()
        
        print("Step 3/3: Generating performance & validation metrics...")
        self.generate_performance_metrics()
        
        # Convert to DataFrame
        df = pd.DataFrame(self.data)
        
        print(f"\nDataset generated successfully!")
        print(f"Total features: {len(df.columns)}")
        print(f"Total samples: {len(df)}")
        
        return df
    
    def save_dataset(self, df, output_dir='welding_dataset'):
        """Save dataset in multiple formats"""
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as CSV
        csv_path = f'{output_dir}/welding_dataset_{timestamp}.csv'
        df.to_csv(csv_path, index=False)
        print(f"\n✓ Saved CSV: {csv_path}")
        
        # Save as Excel with multiple sheets
        excel_path = f'{output_dir}/welding_dataset_{timestamp}.xlsx'
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Complete_Dataset', index=False)
            
            # Create separate sheets for each category
            input_cols = [col for col in df.columns if any(x in col for x in 
                         ['Material', 'Thickness', 'Surface', 'Welding', 'Power', 
                          'Amplitude', 'Force', 'Pressure', 'Time', 'Speed', 'Pulse',
                          'Preheat', 'Humidity', 'Atmosphere', 'Cooling', 'Electrode', 'Gap'])]
            df[input_cols].to_excel(writer, sheet_name='Input_Parameters', index=False)
            
            char_cols = [col for col in df.columns if any(x in col for x in 
                        ['Strength', 'Resistance_mOhm', 'Nugget', 'Penetration', 'HAZ',
                         'Porosity', 'Roughness', 'Microhardness', 'Grain', 'Visual',
                         'Bonding', 'Initial_Crack', 'Residual'])]
            df[char_cols].to_excel(writer, sheet_name='Characterization_Metrics', index=False)
            
            perf_cols = [col for col in df.columns if any(x in col for x in 
                        ['Thermal_Cycles', 'Retained', 'Resistance_Increase', 'Final_Crack',
                         'Fatigue', 'Max_Operating', 'Thermal_Shock', 'IMC', 'Delamination',
                         'Oxidation', 'Energy', 'Performance_Score', 'Cost', 'Pass', 'Optimal'])]
            df[perf_cols].to_excel(writer, sheet_name='Performance_Metrics', index=False)
        
        print(f"✓ Saved Excel: {excel_path}")
        
        # Save as JSON
        json_path = f'{output_dir}/welding_dataset_{timestamp}.json'
        df.to_json(json_path, orient='records', indent=2)
        print(f"✓ Saved JSON: {json_path}")
        
        # Save data dictionary
        self.save_data_dictionary(df, output_dir, timestamp)
        
        # Save summary statistics
        self.save_summary_statistics(df, output_dir, timestamp)
        
        return csv_path, excel_path, json_path
    
    def save_data_dictionary(self, df, output_dir, timestamp):
        """Generate comprehensive data dictionary"""
        
        data_dict = {
            "Dataset Information": {
                "Name": "ML-Driven Inverse Design of Welding Parameters",
                "Version": "1.0",
                "Generated": timestamp,
                "Total Samples": len(df),
                "Total Features": len(df.columns),
                "Purpose": "Training ML models for inverse design of welding parameters optimized for extreme-temperature cycling"
            },
            
            "Feature Categories": {
                "Input Parameters (Design Space)": {
                    "Description": "Controllable welding process variables",
                    "Features": {
                        "Anode_Material": {"Type": "Categorical", "Description": "Anode material type", "Values": "Cu, Al, Ni, Steel, Ti"},
                        "Cathode_Material": {"Type": "Categorical", "Description": "Cathode material type", "Values": "Cu, Al, Ni, Steel, Ti"},
                        "Anode_Thickness_um": {"Type": "Continuous", "Unit": "µm", "Range": "100-500", "Description": "Thickness of anode tab"},
                        "Cathode_Thickness_um": {"Type": "Continuous", "Unit": "µm", "Range": "100-500", "Description": "Thickness of cathode tab"},
                        "Surface_Finish": {"Type": "Categorical", "Description": "Surface treatment/coating", "Values": "Bare, Electroplated, Anodized, Passivated, Coated"},
                        "Welding_Technique": {"Type": "Categorical", "Description": "Welding method used", "Values": "Ultrasonic, Laser, Resistance_Spot, TIG, Friction_Stir"},
                        "Power_W": {"Type": "Continuous", "Unit": "W", "Range": "500-5000", "Description": "Welding power (technique-dependent)"},
                        "Amplitude_um": {"Type": "Continuous", "Unit": "µm", "Range": "0-60", "Description": "Vibration amplitude (USW only)"},
                        "Force_N": {"Type": "Continuous", "Unit": "N", "Range": "0-5000", "Description": "Clamping force applied"},
                        "Pressure_MPa": {"Type": "Continuous", "Unit": "MPa", "Range": "0-60", "Description": "Welding pressure"},
                        "Time_ms": {"Type": "Continuous", "Unit": "ms", "Range": "50-20000", "Description": "Weld duration"},
                        "Speed_mm_s": {"Type": "Continuous", "Unit": "mm/s", "Range": "0-100", "Description": "Welding speed (Laser, TIG)"},
                        "Pulse_Frequency_Hz": {"Type": "Continuous", "Unit": "Hz", "Range": "0-100", "Description": "Pulse frequency (Laser)"},
                        "Pulse_Energy_J": {"Type": "Continuous", "Unit": "J", "Range": "0-20", "Description": "Energy per pulse (Laser)"},
                        "Preheat_Temperature_C": {"Type": "Continuous", "Unit": "°C", "Range": "20-150", "Description": "Sample temperature before welding"},
                        "Ambient_Humidity_%": {"Type": "Continuous", "Unit": "%", "Range": "30-70", "Description": "Relative humidity during welding"},
                        "Chamber_Atmosphere": {"Type": "Categorical", "Description": "Atmospheric conditions", "Values": "Air, Argon, Nitrogen, Vacuum"},
                        "Cooling_Rate_C_per_s": {"Type": "Continuous", "Unit": "°C/s", "Range": "5-50", "Description": "Post-weld cooling rate"},
                        "Electrode_Material": {"Type": "Categorical", "Description": "Electrode/tool material", "Values": "Copper, Tungsten, Molybdenum"},
                        "Gap_Distance_mm": {"Type": "Continuous", "Unit": "mm", "Range": "0-0.5", "Description": "Initial gap between parts"}
                    }
                },
                
                "Characterization & Quality Metrics (Forward Problem)": {
                    "Description": "Immediate post-weld measurements and quality indicators",
                    "Features": {
                        "Weld_Strength_MPa": {"Type": "Continuous", "Unit": "MPa", "Range": "10-250", "Target": "Higher is better"},
                        "Joint_Resistance_mOhm": {"Type": "Continuous", "Unit": "mΩ", "Range": "0.5-15", "Target": "Lower is better"},
                        "Nugget_Diameter_mm": {"Type": "Continuous", "Unit": "mm", "Range": "1-8", "Target": "Larger indicates better fusion"},
                        "Penetration_Depth_um": {"Type": "Continuous", "Unit": "µm", "Range": "50-500", "Target": "Adequate penetration needed"},
                        "HAZ_Width_mm": {"Type": "Continuous", "Unit": "mm", "Range": "0.5-6", "Target": "Smaller is often better"},
                        "Porosity_%": {"Type": "Continuous", "Unit": "%", "Range": "0.1-20", "Target": "Lower is critical"},
                        "Surface_Roughness_um": {"Type": "Continuous", "Unit": "µm", "Range": "0.5-15", "Target": "Lower is better"},
                        "Microhardness_HV": {"Type": "Continuous", "Unit": "HV", "Range": "50-400", "Target": "Indicates mechanical properties"},
                        "Grain_Size_um": {"Type": "Continuous", "Unit": "µm", "Range": "5-60", "Target": "Smaller usually better"},
                        "Visual_Quality_Score": {"Type": "Discrete", "Unit": "1-10", "Range": "1-10", "Target": "≥6 for acceptable quality"},
                        "Interfacial_Bonding_%": {"Type": "Continuous", "Unit": "%", "Range": "20-100", "Target": "Higher indicates better bonding"},
                        "Initial_Crack_Density_per_mm2": {"Type": "Continuous", "Unit": "cracks/mm²", "Range": "0-3", "Target": "Lower is critical"},
                        "Residual_Stress_MPa": {"Type": "Continuous", "Unit": "MPa", "Range": "10-250", "Target": "Lower is better for cycling"}
                    }
                },
                
                "Performance & Validation Metrics (Inverse Design Targets)": {
                    "Description": "Long-term performance under extreme-temperature cycling",
                    "Features": {
                        "Thermal_Cycles_to_Failure": {"Type": "Integer", "Unit": "cycles", "Range": "100-12000", "Target": "PRIMARY TARGET - maximize", "Importance": "Critical"},
                        "Retained_Strength_%": {"Type": "Continuous", "Unit": "%", "Range": "20-100", "Target": "Higher retention after cycling", "Importance": "High"},
                        "Resistance_Increase_%": {"Type": "Continuous", "Unit": "%", "Range": "5-250", "Target": "Minimize resistance growth", "Importance": "High"},
                        "Final_Crack_Density_per_mm2": {"Type": "Continuous", "Unit": "cracks/mm²", "Range": "0.1-8", "Target": "Lower indicates durability", "Importance": "High"},
                        "Fatigue_Life_Cycles": {"Type": "Integer", "Unit": "cycles", "Range": "5000-150000", "Target": "Maximize", "Importance": "Medium"},
                        "Max_Operating_Temp_C": {"Type": "Continuous", "Unit": "°C", "Range": "100-400", "Target": "Higher operating range", "Importance": "Medium"},
                        "Thermal_Shock_Score": {"Type": "Discrete", "Unit": "1-10", "Range": "1-10", "Target": "Higher is better", "Importance": "High"},
                        "IMC_Growth_Rate_um_per_1000cycles": {"Type": "Continuous", "Unit": "µm/1000 cycles", "Range": "0.1-6", "Target": "Lower growth rate", "Importance": "Medium"},
                        "Delamination_%": {"Type": "Continuous", "Unit": "%", "Range": "0-60", "Target": "Minimize delamination", "Importance": "High"},
                        "Oxidation_Resistance_Score": {"Type": "Discrete", "Unit": "1-10", "Range": "1-10", "Target": "Higher is better", "Importance": "Medium"},
                        "Energy_Efficiency_Loss_%": {"Type": "Continuous", "Unit": "%", "Range": "2-50", "Target": "Minimize loss", "Importance": "Medium"},
                        "Overall_Performance_Score": {"Type": "Continuous", "Unit": "0-100", "Range": "10-100", "Target": "Composite metric - maximize", "Importance": "High"}
                    }
                },
                
                "Quality Indicators": {
                    "Description": "Binary flags for threshold-based classification",
                    "Features": {
                        "Pass_Quality_Threshold": {"Type": "Binary", "Values": "0/1", "Description": "1 if Visual_Quality_Score ≥ 6"},
                        "Pass_Performance_Threshold": {"Type": "Binary", "Values": "0/1", "Description": "1 if Thermal_Cycles_to_Failure ≥ 3000"},
                        "Optimal_Design": {"Type": "Binary", "Values": "0/1", "Description": "1 if passes both quality and performance thresholds"}
                    }
                }
            },
            
            "Machine Learning Guidance": {
                "Recommended_Approaches": [
                    "Forward Problem: Regression to predict quality and performance metrics from input parameters",
                    "Inverse Design: Optimization or generative models to find input parameters that maximize performance",
                    "Multi-objective Optimization: Balance thermal cycling performance with cost and other constraints",
                    "Classification: Predict Optimal_Design flag for quality control"
                ],
                "Suggested_Models": [
                    "Gradient Boosting (XGBoost, LightGBM, CatBoost) for forward prediction",
                    "Neural Networks for complex non-linear relationships",
                    "Gaussian Process Regression for uncertainty quantification",
                    "Bayesian Optimization for inverse design",
                    "Generative Adversarial Networks (GANs) for parameter generation"
                ],
                "Feature_Engineering_Tips": [
                    "Create interaction features between material properties",
                    "Calculate material mismatch metrics (thermal expansion, conductivity)",
                    "Normalize power parameters by material melting points",
                    "Create technique-specific feature subsets",
                    "Consider polynomial features for process parameters"
                ],
                "Train_Test_Split": "Stratify by Welding_Technique and material combinations for representative splits",
                "Cross_Validation": "Use GroupKFold by material pairs to avoid data leakage"
            },
            
            "Data Quality Notes": {
                "Correlations": "Quality and performance metrics are realistically correlated with input parameters",
                "Noise": "15% noise added to simulate real-world variability and measurement uncertainty",
                "Material_Effects": "Material property mismatches (thermal expansion, conductivity) significantly affect thermal cycling performance",
                "Technique_Specific": "Some parameters only apply to specific welding techniques (stored as 0 when not applicable)",
                "Realistic_Ranges": "All parameter ranges based on industrial battery tab welding applications"
            }
        }
        
        dict_path = f'{output_dir}/data_dictionary_{timestamp}.json'
        with open(dict_path, 'w') as f:
            json.dump(data_dict, f, indent=2)
        
        print(f"✓ Saved Data Dictionary: {dict_path}")
        
        # Also save as text file for easy reading
        txt_path = f'{output_dir}/data_dictionary_{timestamp}.txt'
        with open(txt_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("ML-DRIVEN INVERSE DESIGN OF WELDING PARAMETERS - DATA DICTIONARY\n")
            f.write("="*80 + "\n\n")
            
            for section, content in data_dict.items():
                f.write(f"\n{'='*80}\n")
                f.write(f"{section.upper()}\n")
                f.write(f"{'='*80}\n\n")
                
                if isinstance(content, dict):
                    for key, value in content.items():
                        if isinstance(value, dict):
                            f.write(f"\n{key}:\n")
                            f.write("-" * 60 + "\n")
                            if 'Description' in value:
                                f.write(f"Description: {value['Description']}\n\n")
                            if 'Features' in value:
                                f.write("Features:\n")
                                for feat_name, feat_info in value['Features'].items():
                                    f.write(f"\n  • {feat_name}\n")
                                    for info_key, info_val in feat_info.items():
                                        f.write(f"    {info_key}: {info_val}\n")
                        elif isinstance(value, list):
                            f.write(f"{key}:\n")
                            for item in value:
                                f.write(f"  • {item}\n")
                        else:
                            f.write(f"{key}: {value}\n")
                else:
                    f.write(f"{content}\n")
        
        print(f"✓ Saved Data Dictionary (TXT): {txt_path}")
    
    def save_summary_statistics(self, df, output_dir, timestamp):
        """Generate summary statistics and visualizations info"""
        
        stats_path = f'{output_dir}/summary_statistics_{timestamp}.txt'
        
        with open(stats_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("DATASET SUMMARY STATISTICS\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Total Samples: {len(df)}\n")
            f.write(f"Total Features: {len(df.columns)}\n\n")
            
            # Categorical distributions
            f.write("\n" + "="*80 + "\n")
            f.write("CATEGORICAL FEATURE DISTRIBUTIONS\n")
            f.write("="*80 + "\n\n")
            
            categorical_cols = ['Anode_Material', 'Cathode_Material', 'Surface_Finish', 
                               'Welding_Technique', 'Chamber_Atmosphere', 'Electrode_Material']
            
            for col in categorical_cols:
                if col in df.columns:
                    f.write(f"\n{col}:\n")
                    f.write("-" * 60 + "\n")
                    value_counts = df[col].value_counts()
                    for val, count in value_counts.items():
                        pct = (count / len(df)) * 100
                        f.write(f"  {val}: {count} ({pct:.1f}%)\n")
            
            # Numerical statistics
            f.write("\n" + "="*80 + "\n")
            f.write("NUMERICAL FEATURE STATISTICS\n")
            f.write("="*80 + "\n\n")
            
            numerical_cols = df.select_dtypes(include=[np.number]).columns
            stats_df = df[numerical_cols].describe()
            
            f.write(stats_df.to_string())
            
            # Performance metrics summary
            f.write("\n\n" + "="*80 + "\n")
            f.write("KEY PERFORMANCE METRICS\n")
            f.write("="*80 + "\n\n")
            
            key_metrics = ['Thermal_Cycles_to_Failure', 'Retained_Strength_%', 
                          'Resistance_Increase_%', 'Overall_Performance_Score']
            
            for metric in key_metrics:
                if metric in df.columns:
                    f.write(f"\n{metric}:\n")
                    f.write("-" * 60 + "\n")
                    f.write(f"  Mean: {df[metric].mean():.2f}\n")
                    f.write(f"  Median: {df[metric].median():.2f}\n")
                    f.write(f"  Std Dev: {df[metric].std():.2f}\n")
                    f.write(f"  Min: {df[metric].min():.2f}\n")
                    f.write(f"  Max: {df[metric].max():.2f}\n")
                    f.write(f"  25th percentile: {df[metric].quantile(0.25):.2f}\n")
                    f.write(f"  75th percentile: {df[metric].quantile(0.75):.2f}\n")
            
            # Quality thresholds
            f.write("\n\n" + "="*80 + "\n")
            f.write("QUALITY THRESHOLD ANALYSIS\n")
            f.write("="*80 + "\n\n")
            
            if 'Pass_Quality_Threshold' in df.columns:
                pass_quality = df['Pass_Quality_Threshold'].sum()
                f.write(f"Samples passing quality threshold: {pass_quality} ({pass_quality/len(df)*100:.1f}%)\n")
            
            if 'Pass_Performance_Threshold' in df.columns:
                pass_performance = df['Pass_Performance_Threshold'].sum()
                f.write(f"Samples passing performance threshold: {pass_performance} ({pass_performance/len(df)*100:.1f}%)\n")
            
            if 'Optimal_Design' in df.columns:
                optimal = df['Optimal_Design'].sum()
                f.write(f"Optimal designs (pass both thresholds): {optimal} ({optimal/len(df)*100:.1f}%)\n")
        
        print(f"✓ Saved Summary Statistics: {stats_path}")


def main():
    """Main execution function"""
    
    print("\n" + "="*80)
    print("ML-DRIVEN INVERSE DESIGN OF WELDING PARAMETERS")
    print("Dataset Generator v1.0")
    print("="*80 + "\n")
    
    # Generate dataset
    generator = WeldingDatasetGenerator(n_samples=2000)
    df = generator.generate_dataset()
    
    # Save in multiple formats
    print("\nSaving dataset in multiple formats...")
    csv_path, excel_path, json_path = generator.save_dataset(df)
    
    print("\n" + "="*80)
    print("DATASET GENERATION COMPLETE!")
    print("="*80)
    print(f"\nGenerated {len(df)} samples with {len(df.columns)} features")
    print(f"\nFiles saved in: welding_dataset/")
    print("\nDataset includes:")
    print("  • Complete dataset (CSV, Excel, JSON)")
    print("  • Separate sheets for Input/Characterization/Performance")
    print("  • Comprehensive data dictionary")
    print("  • Summary statistics")
    print("\n" + "="*80 + "\n")
    
    # Display sample
    print("Sample of first 5 rows (selected columns):")
    print("-" * 80)
    sample_cols = ['Welding_Technique', 'Power_W', 'Weld_Strength_MPa', 
                   'Thermal_Cycles_to_Failure', 'Overall_Performance_Score', 'Optimal_Design']
    print(df[sample_cols].head())
    print("\n")
    
    return df


if __name__ == "__main__":
    df = main()
