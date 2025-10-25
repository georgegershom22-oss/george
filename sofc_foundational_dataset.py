#!/usr/bin/env python3
"""
SOFC Foundational & Calibration Dataset Generator
Phase 1: Complete dataset for physics-based model calibration

This script generates comprehensive datasets for:
1. Thermo-Physical Properties
2. Sintering Kinetics Data  
3. Microstructural Evolution Data
4. Initial Process Window Data

Author: AI Assistant
Date: 2025-10-25
"""

import numpy as np
import pandas as pd
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore')

class SOFCDatasetGenerator:
    def __init__(self, output_dir="sofc_dataset"):
        self.output_dir = output_dir
        self.create_output_directory()
        
        # Material compositions
        self.materials = {
            'anode': 'NiO-YSZ (60-40 vol%)',
            'electrolyte': '8YSZ (8 mol% Y2O3-ZrO2)',
            'functional_layer': 'NiO-YSZ (40-60 vol%)'
        }
        
        # Temperature ranges (°C)
        self.temp_range = np.linspace(20, 1400, 100)
        self.sintering_temps = np.linspace(1200, 1400, 50)
        
        print(f"Initializing SOFC Dataset Generator")
        print(f"Output directory: {self.output_dir}")
        print(f"Materials: {self.materials}")
    
    def create_output_directory(self):
        """Create output directory structure"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/thermophysical", exist_ok=True)
        os.makedirs(f"{self.output_dir}/sintering_kinetics", exist_ok=True)
        os.makedirs(f"{self.output_dir}/microstructure", exist_ok=True)
        os.makedirs(f"{self.output_dir}/process_window", exist_ok=True)
        os.makedirs(f"{self.output_dir}/plots", exist_ok=True)
    
    def generate_thermophysical_properties(self):
        """Generate comprehensive thermo-physical properties dataset"""
        print("\n=== Generating Thermo-Physical Properties Dataset ===")
        
        datasets = {}
        
        for material, composition in self.materials.items():
            print(f"Processing {material}: {composition}")
            
            # Coefficient of Thermal Expansion (CTE) - 1/K
            if material == 'anode':
                # NiO-YSZ composite behavior
                cte_base = 12.5e-6
                cte_temp_coeff = 2.3e-9
            elif material == 'electrolyte':
                # YSZ behavior
                cte_base = 10.8e-6
                cte_temp_coeff = 1.8e-9
            else:
                # Functional layer
                cte_base = 11.2e-6
                cte_temp_coeff = 2.0e-9
            
            cte = cte_base + cte_temp_coeff * self.temp_range + \
                  np.random.normal(0, cte_base * 0.02, len(self.temp_range))
            
            # Young's Modulus (GPa)
            if material == 'anode':
                E0 = 180  # Room temperature modulus
                temp_coeff = -0.08  # Temperature coefficient
            elif material == 'electrolyte':
                E0 = 210
                temp_coeff = -0.06
            else:
                E0 = 190
                temp_coeff = -0.07
            
            youngs_modulus = E0 * np.exp(temp_coeff * (self.temp_range - 20) / 1000) + \
                           np.random.normal(0, E0 * 0.05, len(self.temp_range))
            
            # Poisson's Ratio (dimensionless)
            poisson_base = 0.31 if material == 'electrolyte' else 0.28
            poisson_ratio = poisson_base + 0.02 * (self.temp_range - 20) / 1380 + \
                          np.random.normal(0, 0.01, len(self.temp_range))
            
            # Shear Viscosity for sintering (Pa·s)
            # Critical for sintering simulation
            if self.temp_range.max() > 1000:
                high_temp_mask = self.temp_range > 1000
                viscosity = np.full_like(self.temp_range, np.nan)
                
                # Arrhenius-type behavior for high temperatures
                A = 1e12 if material == 'anode' else 5e11  # Pre-exponential factor
                Q = 450000 if material == 'anode' else 420000  # Activation energy J/mol
                R = 8.314  # Gas constant
                
                T_kelvin = self.temp_range[high_temp_mask] + 273.15
                viscosity[high_temp_mask] = A * np.exp(Q / (R * T_kelvin)) + \
                                          np.random.lognormal(0, 0.1, np.sum(high_temp_mask))
            else:
                viscosity = np.full_like(self.temp_range, np.nan)
            
            # Density (g/cm³)
            if material == 'anode':
                density_base = 6.2  # NiO-YSZ composite
            elif material == 'electrolyte':
                density_base = 6.1  # YSZ
            else:
                density_base = 6.15
            
            # Thermal expansion effect on density
            density = density_base * (1 - 3 * cte * (self.temp_range - 20)) + \
                     np.random.normal(0, density_base * 0.01, len(self.temp_range))
            
            # Create dataset
            dataset = pd.DataFrame({
                'Temperature_C': self.temp_range,
                'CTE_per_K': cte,
                'Youngs_Modulus_GPa': youngs_modulus,
                'Poisson_Ratio': poisson_ratio,
                'Shear_Viscosity_Pa_s': viscosity,
                'Density_g_cm3': density,
                'Material': material,
                'Composition': composition
            })
            
            datasets[material] = dataset
            
            # Save individual material data
            filename = f"{self.output_dir}/thermophysical/{material}_properties.csv"
            dataset.to_csv(filename, index=False)
            print(f"  Saved: {filename}")
        
        # Combine all materials
        combined_df = pd.concat(datasets.values(), ignore_index=True)
        combined_filename = f"{self.output_dir}/thermophysical/all_materials_properties.csv"
        combined_df.to_csv(combined_filename, index=False)
        print(f"Combined dataset saved: {combined_filename}")
        
        # Generate plots
        self.plot_thermophysical_properties(datasets)
        
        return datasets
    
    def generate_sintering_kinetics_data(self):
        """Generate sintering kinetics parameters"""
        print("\n=== Generating Sintering Kinetics Dataset ===")
        
        datasets = {}
        
        for material, composition in self.materials.items():
            print(f"Processing sintering kinetics for {material}")
            
            # Create comprehensive parameter space
            temperatures = np.linspace(1200, 1400, 25)  # °C
            densities = np.linspace(0.45, 0.95, 20)  # Relative density
            hold_times = np.logspace(0, 3, 15)  # 1 to 1000 minutes
            
            # Create meshgrid for all combinations
            T_mesh, rho_mesh, t_mesh = np.meshgrid(temperatures, densities, hold_times, indexing='ij')
            
            # Flatten for DataFrame
            T_flat = T_mesh.flatten()
            rho_flat = rho_mesh.flatten()
            t_flat = t_mesh.flatten()
            
            # Sintering stress (MPa) - function of temperature and density
            # Higher at lower densities and higher temperatures
            sintering_stress = self.calculate_sintering_stress(T_flat, rho_flat, material)
            
            # Bulk viscosity (Pa·s) - Arrhenius behavior with density dependence
            bulk_viscosity = self.calculate_bulk_viscosity(T_flat, rho_flat, material)
            
            # Shear viscosity (Pa·s) - Related to bulk viscosity
            shear_viscosity = bulk_viscosity * 0.67  # Typical ratio for ceramics
            
            # Densification rate (1/s)
            densification_rate = self.calculate_densification_rate(T_flat, rho_flat, t_flat, material)
            
            # Grain growth rate (μm/s)
            grain_growth_rate = self.calculate_grain_growth_rate(T_flat, rho_flat, material)
            
            # Create dataset
            dataset = pd.DataFrame({
                'Temperature_C': T_flat,
                'Relative_Density': rho_flat,
                'Hold_Time_min': t_flat,
                'Sintering_Stress_MPa': sintering_stress,
                'Bulk_Viscosity_Pa_s': bulk_viscosity,
                'Shear_Viscosity_Pa_s': shear_viscosity,
                'Densification_Rate_per_s': densification_rate,
                'Grain_Growth_Rate_um_per_s': grain_growth_rate,
                'Material': material,
                'Composition': composition
            })
            
            datasets[material] = dataset
            
            # Save dataset
            filename = f"{self.output_dir}/sintering_kinetics/{material}_kinetics.csv"
            dataset.to_csv(filename, index=False)
            print(f"  Saved: {filename}")
        
        # Combined dataset
        combined_df = pd.concat(datasets.values(), ignore_index=True)
        combined_filename = f"{self.output_dir}/sintering_kinetics/all_materials_kinetics.csv"
        combined_df.to_csv(combined_filename, index=False)
        print(f"Combined kinetics dataset saved: {combined_filename}")
        
        # Generate master sintering curves
        self.generate_master_sintering_curves(datasets)
        
        return datasets
    
    def calculate_sintering_stress(self, T, rho, material):
        """Calculate sintering stress based on temperature and density"""
        # Base parameters by material
        if material == 'anode':
            sigma0 = 15.0  # MPa
            Q = 380000  # J/mol
        elif material == 'electrolyte':
            sigma0 = 12.0
            Q = 420000
        else:
            sigma0 = 13.5
            Q = 400000
        
        R = 8.314
        T_K = T + 273.15
        
        # Sintering stress increases with temperature and decreases with density
        stress = sigma0 * (1 - rho)**2 * np.exp(-Q / (R * T_K)) * 1e6
        
        # Add realistic noise
        noise = np.random.lognormal(0, 0.15, len(stress))
        return stress * noise
    
    def calculate_bulk_viscosity(self, T, rho, material):
        """Calculate bulk viscosity for sintering"""
        if material == 'anode':
            A = 1e15  # Pa·s
            Q = 450000  # J/mol
            n = 3.5  # Density exponent
        elif material == 'electrolyte':
            A = 5e14
            Q = 480000
            n = 4.0
        else:
            A = 7e14
            Q = 465000
            n = 3.7
        
        R = 8.314
        T_K = T + 273.15
        
        # Viscosity decreases with temperature, increases dramatically as density approaches 1
        viscosity = A * np.exp(Q / (R * T_K)) * (1 - rho)**(-n)
        
        # Add noise
        noise = np.random.lognormal(0, 0.2, len(viscosity))
        return viscosity * noise
    
    def calculate_densification_rate(self, T, rho, t, material):
        """Calculate densification rate"""
        # Rate decreases with density and time, increases with temperature
        if material == 'anode':
            k0 = 1e-4  # 1/s
            Q = 350000  # J/mol
        elif material == 'electrolyte':
            k0 = 5e-5
            Q = 380000
        else:
            k0 = 7e-5
            Q = 365000
        
        R = 8.314
        T_K = T + 273.15
        
        # Densification rate model
        rate = k0 * np.exp(-Q / (R * T_K)) * (1 - rho)**2 * t**(-0.1)
        
        # Ensure physical bounds
        rate = np.maximum(rate, 1e-8)
        
        # Add noise
        noise = np.random.lognormal(0, 0.25, len(rate))
        return rate * noise
    
    def calculate_grain_growth_rate(self, T, rho, material):
        """Calculate grain growth rate"""
        if material == 'anode':
            k0 = 1e-3  # μm/s
            Q = 320000  # J/mol
        elif material == 'electrolyte':
            k0 = 5e-4
            Q = 350000
        else:
            k0 = 7e-4
            Q = 335000
        
        R = 8.314
        T_K = T + 273.15
        
        # Grain growth accelerates with density (less porosity to pin boundaries)
        rate = k0 * np.exp(-Q / (R * T_K)) * rho**2
        
        # Add noise
        noise = np.random.lognormal(0, 0.3, len(rate))
        return rate * noise
    
    def generate_microstructural_evolution_data(self):
        """Generate microstructural evolution time-series data"""
        print("\n=== Generating Microstructural Evolution Dataset ===")
        
        datasets = {}
        
        # Sintering conditions for interrupted tests
        test_conditions = [
            {'temp': 1250, 'times': [0, 30, 60, 120, 240, 480]},  # minutes
            {'temp': 1300, 'times': [0, 15, 30, 60, 120, 240]},
            {'temp': 1350, 'times': [0, 10, 20, 40, 80, 160]},
            {'temp': 1400, 'times': [0, 5, 10, 20, 40, 80]}
        ]
        
        for material, composition in self.materials.items():
            print(f"Processing microstructural evolution for {material}")
            
            all_data = []
            
            for condition in test_conditions:
                temp = condition['temp']
                times = condition['times']
                
                for time in times:
                    # Generate microstructural parameters
                    data_point = self.generate_microstructure_snapshot(material, temp, time)
                    data_point.update({
                        'Material': material,
                        'Composition': composition,
                        'Temperature_C': temp,
                        'Time_min': time
                    })
                    all_data.append(data_point)
            
            # Convert to DataFrame
            dataset = pd.DataFrame(all_data)
            datasets[material] = dataset
            
            # Save dataset
            filename = f"{self.output_dir}/microstructure/{material}_evolution.csv"
            dataset.to_csv(filename, index=False)
            print(f"  Saved: {filename}")
        
        # Combined dataset
        combined_df = pd.concat(datasets.values(), ignore_index=True)
        combined_filename = f"{self.output_dir}/microstructure/all_materials_evolution.csv"
        combined_df.to_csv(combined_filename, index=False)
        print(f"Combined microstructure dataset saved: {combined_filename}")
        
        # Generate synthetic image metadata
        self.generate_image_metadata(datasets)
        
        return datasets
    
    def generate_microstructure_snapshot(self, material, temperature, time):
        """Generate microstructural parameters for a specific condition"""
        
        # Initial conditions (green body)
        if time == 0:
            return {
                'Porosity_fraction': 0.55 + np.random.normal(0, 0.02),
                'Average_Pore_Size_um': 2.5 + np.random.normal(0, 0.3),
                'Pore_Size_Std_um': 1.2 + np.random.normal(0, 0.1),
                'Average_Grain_Size_um': 0.8 + np.random.normal(0, 0.1),
                'Grain_Size_Std_um': 0.3 + np.random.normal(0, 0.05),
                'Tortuosity': 3.2 + np.random.normal(0, 0.2),
                'Connectivity_factor': 0.65 + np.random.normal(0, 0.05),
                'Surface_Area_m2_g': 8.5 + np.random.normal(0, 0.5)
            }
        
        # Evolution parameters based on material
        if material == 'anode':
            densification_rate = 0.8
            grain_growth_rate = 0.6
        elif material == 'electrolyte':
            densification_rate = 0.9
            grain_growth_rate = 0.4
        else:
            densification_rate = 0.85
            grain_growth_rate = 0.5
        
        # Temperature effect
        temp_factor = np.exp((temperature - 1250) / 150)
        
        # Time evolution (non-linear)
        time_factor = 1 - np.exp(-time / 100)
        
        # Calculate evolved properties
        initial_porosity = 0.55
        final_porosity = 0.05 + 0.1 * np.exp(-(temperature - 1200) / 100)
        porosity = initial_porosity - (initial_porosity - final_porosity) * \
                  densification_rate * temp_factor * time_factor
        porosity = max(porosity, 0.02)  # Physical minimum
        
        # Pore size evolution (decreases with time)
        initial_pore_size = 2.5
        pore_size = initial_pore_size * (0.3 + 0.7 * np.exp(-time * temp_factor / 50))
        
        # Grain size evolution (increases with time)
        initial_grain_size = 0.8
        grain_size = initial_grain_size * (1 + grain_growth_rate * temp_factor * 
                                         (time / 60)**0.3)
        
        # Tortuosity (decreases as pores become more connected)
        tortuosity = 3.2 - 1.5 * time_factor * temp_factor
        tortuosity = max(tortuosity, 1.2)
        
        # Connectivity (increases with densification)
        connectivity = 0.65 + 0.3 * time_factor * temp_factor
        connectivity = min(connectivity, 0.98)
        
        # Surface area (decreases with sintering)
        surface_area = 8.5 * np.exp(-time * temp_factor / 200)
        
        # Add realistic noise
        return {
            'Porosity_fraction': porosity + np.random.normal(0, 0.01),
            'Average_Pore_Size_um': pore_size + np.random.normal(0, pore_size * 0.1),
            'Pore_Size_Std_um': pore_size * 0.4 + np.random.normal(0, 0.1),
            'Average_Grain_Size_um': grain_size + np.random.normal(0, grain_size * 0.08),
            'Grain_Size_Std_um': grain_size * 0.35 + np.random.normal(0, 0.05),
            'Tortuosity': tortuosity + np.random.normal(0, 0.1),
            'Connectivity_factor': connectivity + np.random.normal(0, 0.02),
            'Surface_Area_m2_g': surface_area + np.random.normal(0, surface_area * 0.05)
        }
    
    def generate_process_window_data(self):
        """Generate initial process window dataset"""
        print("\n=== Generating Process Window Dataset ===")
        
        # Define process parameter ranges
        heating_rates = [1, 2, 3, 5, 8, 10, 15, 20]  # °C/min
        peak_temperatures = np.linspace(1200, 1400, 15)  # °C
        hold_times = [0, 15, 30, 60, 120, 240, 480]  # minutes
        atmospheres = ['air', 'reducing_10H2_90N2', 'reducing_5H2_95N2', 'inert_N2']
        
        all_experiments = []
        experiment_id = 1
        
        print(f"Generating {len(heating_rates) * len(peak_temperatures) * len(hold_times) * len(atmospheres)} experiments")
        
        for heating_rate in heating_rates:
            for peak_temp in peak_temperatures:
                for hold_time in hold_times:
                    for atmosphere in atmospheres:
                        
                        # Calculate outcomes based on physics
                        outcomes = self.calculate_process_outcomes(
                            heating_rate, peak_temp, hold_time, atmosphere
                        )
                        
                        experiment = {
                            'Experiment_ID': f'EXP_{experiment_id:04d}',
                            'Heating_Rate_C_per_min': heating_rate,
                            'Peak_Temperature_C': peak_temp,
                            'Hold_Time_min': hold_time,
                            'Atmosphere': atmosphere,
                            'Total_Cycle_Time_min': self.calculate_cycle_time(heating_rate, peak_temp, hold_time),
                            **outcomes
                        }
                        
                        all_experiments.append(experiment)
                        experiment_id += 1
        
        # Convert to DataFrame
        dataset = pd.DataFrame(all_experiments)
        
        # Save dataset
        filename = f"{self.output_dir}/process_window/sintering_experiments.csv"
        dataset.to_csv(filename, index=False)
        print(f"Process window dataset saved: {filename}")
        
        # Generate success/failure analysis
        self.analyze_process_window(dataset)
        
        return dataset
    
    def calculate_process_outcomes(self, heating_rate, peak_temp, hold_time, atmosphere):
        """Calculate sintering outcomes based on process parameters"""
        
        # Base success probability
        success_prob = 0.5
        
        # Temperature effects
        if 1250 <= peak_temp <= 1350:
            success_prob += 0.3
        elif peak_temp > 1380:
            success_prob -= 0.2  # Too hot, cracking risk
        elif peak_temp < 1220:
            success_prob -= 0.3  # Too cold, incomplete sintering
        
        # Heating rate effects
        if 2 <= heating_rate <= 5:
            success_prob += 0.2
        elif heating_rate > 10:
            success_prob -= 0.15  # Too fast, thermal stress
        elif heating_rate < 1:
            success_prob -= 0.1  # Too slow, grain growth
        
        # Hold time effects
        if 30 <= hold_time <= 120:
            success_prob += 0.15
        elif hold_time > 240:
            success_prob -= 0.1  # Excessive grain growth
        
        # Atmosphere effects
        if atmosphere == 'reducing_10H2_90N2':
            success_prob += 0.1  # Optimal for NiO reduction
        elif atmosphere == 'air':
            success_prob -= 0.05  # Oxidizing conditions
        
        # Ensure probability bounds
        success_prob = np.clip(success_prob, 0.05, 0.95)
        
        # Generate outcomes
        is_successful = np.random.random() < success_prob
        
        if is_successful:
            # Successful sintering
            warpage_max = np.random.uniform(0.01, 0.15)  # mm
            warpage_rms = warpage_max * 0.6
            cracking = False
            final_density = np.random.uniform(0.92, 0.98)
            
        else:
            # Failed sintering
            warpage_max = np.random.uniform(0.2, 2.0)  # mm
            warpage_rms = warpage_max * 0.7
            cracking = np.random.random() < 0.4  # 40% chance of cracking in failures
            final_density = np.random.uniform(0.75, 0.91)
        
        # Microstructure outcomes
        avg_grain_size = self.predict_grain_size(peak_temp, hold_time, heating_rate)
        porosity = 1 - final_density
        
        return {
            'Warpage_Max_mm': warpage_max,
            'Warpage_RMS_mm': warpage_rms,
            'Cracking': cracking,
            'Final_Relative_Density': final_density,
            'Final_Porosity_fraction': porosity,
            'Average_Grain_Size_um': avg_grain_size,
            'Success': is_successful,
            'Quality_Score': self.calculate_quality_score(warpage_max, cracking, final_density)
        }
    
    def predict_grain_size(self, temp, hold_time, heating_rate):
        """Predict final grain size based on process parameters"""
        # Base grain size model
        base_size = 0.8  # μm (initial)
        
        # Temperature effect (Arrhenius-type)
        temp_effect = np.exp((temp - 1300) / 100)
        
        # Time effect (power law)
        time_effect = (1 + hold_time / 60)**0.3
        
        # Heating rate effect (faster heating = smaller grains initially)
        heating_effect = (heating_rate / 5)**(-0.1)
        
        grain_size = base_size * temp_effect * time_effect * heating_effect
        
        # Add noise and ensure physical bounds
        grain_size *= np.random.uniform(0.8, 1.2)
        return np.clip(grain_size, 0.5, 15.0)
    
    def calculate_cycle_time(self, heating_rate, peak_temp, hold_time):
        """Calculate total sintering cycle time"""
        # Heat up from room temperature
        heat_up_time = (peak_temp - 25) / heating_rate
        
        # Hold time
        hold = hold_time
        
        # Cool down (assume natural cooling, faster than heating)
        cool_down_time = heat_up_time * 0.7
        
        return heat_up_time + hold + cool_down_time
    
    def calculate_quality_score(self, warpage, cracking, density):
        """Calculate overall quality score (0-100)"""
        score = 100
        
        # Warpage penalty
        score -= min(warpage * 50, 30)
        
        # Cracking penalty
        if cracking:
            score -= 40
        
        # Density bonus/penalty
        if density > 0.95:
            score += 10
        elif density < 0.85:
            score -= 20
        
        return max(score, 0)
    
    def generate_master_sintering_curves(self, kinetics_datasets):
        """Generate master sintering curves for each material"""
        print("\nGenerating master sintering curves...")
        
        for material, dataset in kinetics_datasets.items():
            # Create master sintering curve data
            temperatures = dataset['Temperature_C'].unique()
            
            msc_data = []
            
            for temp in temperatures:
                temp_data = dataset[dataset['Temperature_C'] == temp]
                
                # Calculate apparent activation energy and pre-exponential factor
                # This is simplified - real MSC requires more complex analysis
                
                for _, row in temp_data.iterrows():
                    if row['Relative_Density'] > 0.5 and row['Relative_Density'] < 0.95:
                        
                        # Master sintering curve parameter
                        theta = (temp + 273.15) * row['Hold_Time_min'] * 60  # T*t in K*s
                        
                        msc_data.append({
                            'Material': material,
                            'Temperature_C': temp,
                            'Theta_K_s': theta,
                            'Relative_Density': row['Relative_Density'],
                            'Densification_Rate_per_s': row['Densification_Rate_per_s']
                        })
            
            msc_df = pd.DataFrame(msc_data)
            filename = f"{self.output_dir}/sintering_kinetics/{material}_master_curve.csv"
            msc_df.to_csv(filename, index=False)
            print(f"  Master curve saved: {filename}")
    
    def generate_image_metadata(self, microstructure_datasets):
        """Generate metadata for synthetic SEM and X-ray CT images"""
        print("\nGenerating image metadata...")
        
        image_metadata = []
        image_id = 1
        
        for material, dataset in microstructure_datasets.items():
            for _, row in dataset.iterrows():
                
                # SEM images (2D)
                sem_metadata = {
                    'Image_ID': f'SEM_{image_id:05d}',
                    'Image_Type': 'SEM',
                    'Material': material,
                    'Temperature_C': row['Temperature_C'],
                    'Time_min': row['Time_min'],
                    'Magnification': np.random.choice([1000, 2000, 5000, 10000]),
                    'Pixel_Size_nm': np.random.uniform(10, 100),
                    'Image_Width_px': 2048,
                    'Image_Height_px': 2048,
                    'Porosity_fraction': row['Porosity_fraction'],
                    'Average_Pore_Size_um': row['Average_Pore_Size_um'],
                    'Average_Grain_Size_um': row['Average_Grain_Size_um'],
                    'Filename': f'sem_{material}_{row["Temperature_C"]}C_{row["Time_min"]}min_{image_id}.tif'
                }
                image_metadata.append(sem_metadata)
                image_id += 1
                
                # X-ray CT images (3D) - fewer samples due to longer acquisition time
                if np.random.random() < 0.3:  # 30% of samples have CT data
                    ct_metadata = {
                        'Image_ID': f'CT_{image_id:05d}',
                        'Image_Type': 'X-ray_CT',
                        'Material': material,
                        'Temperature_C': row['Temperature_C'],
                        'Time_min': row['Time_min'],
                        'Voxel_Size_um': np.random.uniform(0.5, 2.0),
                        'Volume_Width_vx': 1024,
                        'Volume_Height_vx': 1024,
                        'Volume_Depth_vx': 1024,
                        'Porosity_fraction': row['Porosity_fraction'],
                        'Average_Pore_Size_um': row['Average_Pore_Size_um'],
                        'Tortuosity': row['Tortuosity'],
                        'Connectivity_factor': row['Connectivity_factor'],
                        'Filename': f'ct_{material}_{row["Temperature_C"]}C_{row["Time_min"]}min_{image_id}.raw'
                    }
                    image_metadata.append(ct_metadata)
                    image_id += 1
        
        # Save image metadata
        metadata_df = pd.DataFrame(image_metadata)
        filename = f"{self.output_dir}/microstructure/image_metadata.csv"
        metadata_df.to_csv(filename, index=False)
        print(f"Image metadata saved: {filename} ({len(metadata_df)} images)")
    
    def analyze_process_window(self, dataset):
        """Analyze process window and identify optimal regions"""
        print("\nAnalyzing process window...")
        
        # Success rate analysis
        success_rate = dataset['Success'].mean()
        print(f"Overall success rate: {success_rate:.1%}")
        
        # Optimal parameter ranges
        successful = dataset[dataset['Success'] == True]
        
        if len(successful) > 0:
            optimal_ranges = {
                'Heating_Rate_C_per_min': [successful['Heating_Rate_C_per_min'].min(), 
                                         successful['Heating_Rate_C_per_min'].max()],
                'Peak_Temperature_C': [successful['Peak_Temperature_C'].min(), 
                                     successful['Peak_Temperature_C'].max()],
                'Hold_Time_min': [successful['Hold_Time_min'].min(), 
                                successful['Hold_Time_min'].max()]
            }
            
            # Save analysis
            analysis = {
                'success_rate': float(success_rate),
                'optimal_ranges': {k: [float(v[0]), float(v[1])] for k, v in optimal_ranges.items()},
                'best_experiments': successful.nlargest(10, 'Quality_Score')[
                    ['Experiment_ID', 'Heating_Rate_C_per_min', 'Peak_Temperature_C', 
                     'Hold_Time_min', 'Quality_Score']].astype(str).to_dict('records')
            }
            
            with open(f"{self.output_dir}/process_window/analysis.json", 'w') as f:
                json.dump(analysis, f, indent=2)
            
            print(f"Process window analysis saved")
    
    def plot_thermophysical_properties(self, datasets):
        """Generate plots for thermophysical properties"""
        print("Generating thermophysical property plots...")
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('Thermo-Physical Properties vs Temperature', fontsize=16)
        
        properties = ['CTE_per_K', 'Youngs_Modulus_GPa', 'Poisson_Ratio', 
                     'Density_g_cm3', 'Shear_Viscosity_Pa_s']
        
        for i, prop in enumerate(properties[:5]):
            ax = axes[i//3, i%3]
            
            for material, dataset in datasets.items():
                if prop == 'Shear_Viscosity_Pa_s':
                    # Only plot high temperature data for viscosity
                    mask = dataset['Temperature_C'] > 1000
                    if mask.any():
                        ax.semilogy(dataset.loc[mask, 'Temperature_C'], 
                                  dataset.loc[mask, prop], 
                                  label=material, marker='o', markersize=3)
                else:
                    ax.plot(dataset['Temperature_C'], dataset[prop], 
                           label=material, marker='o', markersize=2)
            
            ax.set_xlabel('Temperature (°C)')
            ax.set_ylabel(prop.replace('_', ' '))
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        # Remove empty subplot
        axes[1, 2].remove()
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/plots/thermophysical_properties.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  Thermophysical properties plot saved")
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("\n=== Generating Summary Report ===")
        
        report = {
            'dataset_info': {
                'generation_date': datetime.now().isoformat(),
                'materials': self.materials,
                'temperature_range_C': [float(self.temp_range.min()), float(self.temp_range.max())],
                'sintering_temp_range_C': [float(self.sintering_temps.min()), float(self.sintering_temps.max())]
            },
            'datasets': {
                'thermophysical_properties': {
                    'description': 'Temperature-dependent material properties for FEM modeling',
                    'parameters': ['CTE', 'Young\'s Modulus', 'Poisson\'s Ratio', 'Shear Viscosity', 'Density'],
                    'temperature_points': len(self.temp_range),
                    'materials': len(self.materials)
                },
                'sintering_kinetics': {
                    'description': 'Kinetic parameters for phase-field modeling',
                    'parameters': ['Sintering Stress', 'Bulk/Shear Viscosity', 'Densification Rate', 'Grain Growth Rate'],
                    'conditions': '25 temperatures × 20 densities × 15 time points',
                    'total_points': 25 * 20 * 15 * len(self.materials)
                },
                'microstructural_evolution': {
                    'description': 'Time-series microstructural data for model validation',
                    'parameters': ['Porosity', 'Pore Size', 'Grain Size', 'Tortuosity', 'Connectivity'],
                    'conditions': '4 temperatures × 6 time points × 3 materials',
                    'image_metadata': 'SEM and X-ray CT synthetic metadata'
                },
                'process_window': {
                    'description': 'Initial sintering experiments for RL training',
                    'parameters': ['Heating Rate', 'Peak Temperature', 'Hold Time', 'Atmosphere'],
                    'experiments': 8 * 15 * 7 * 4,
                    'outcomes': ['Warpage', 'Cracking', 'Density', 'Quality Score']
                }
            },
            'file_structure': {
                'thermophysical/': 'Material property datasets',
                'sintering_kinetics/': 'Kinetic parameters and master curves',
                'microstructure/': 'Microstructural evolution and image metadata',
                'process_window/': 'Sintering experiments and analysis',
                'plots/': 'Visualization plots'
            },
            'usage_notes': {
                'FEM_calibration': 'Use thermophysical properties for mechanical and thermal FEM models',
                'phase_field_calibration': 'Use sintering kinetics for phase-field model parameters',
                'validation': 'Use microstructural evolution data to validate model predictions',
                'RL_training': 'Use process window data as initial training set for reinforcement learning'
            }
        }
        
        # Save report
        with open(f"{self.output_dir}/dataset_summary.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Summary report saved: {self.output_dir}/dataset_summary.json")
        
        return report

def main():
    """Main function to generate complete SOFC dataset"""
    print("=" * 60)
    print("SOFC FOUNDATIONAL & CALIBRATION DATASET GENERATOR")
    print("Phase 1: Complete Physics-Based Model Calibration Data")
    print("=" * 60)
    
    # Initialize generator
    generator = SOFCDatasetGenerator()
    
    # Generate all datasets
    thermo_data = generator.generate_thermophysical_properties()
    kinetics_data = generator.generate_sintering_kinetics_data()
    microstructure_data = generator.generate_microstructural_evolution_data()
    process_data = generator.generate_process_window_data()
    
    # Generate summary
    summary = generator.generate_summary_report()
    
    print("\n" + "=" * 60)
    print("DATASET GENERATION COMPLETE!")
    print("=" * 60)
    print(f"Output directory: {generator.output_dir}")
    print(f"Total datasets: {len(summary['datasets'])}")
    print(f"Materials covered: {len(generator.materials)}")
    print("\nDataset summary:")
    for name, info in summary['datasets'].items():
        print(f"  • {name}: {info['description']}")
    
    print(f"\nAll data ready for FEM and Phase-Field model calibration!")

if __name__ == "__main__":
    main()