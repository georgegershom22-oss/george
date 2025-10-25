#!/usr/bin/env python3
"""
Dataset Loader and Explorer for Phase 1 Foundational & Calibration Data

This script provides utilities to load, explore, and visualize the 
SOFC sintering dataset.

Usage:
    python dataset_loader.py --explore
    python dataset_loader.py --plot material_properties
    python dataset_loader.py --summary

Author: Dataset Generation Script
Date: 2025-10-25
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import argparse
import warnings
warnings.filterwarnings('ignore')

# Set plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class SOFCDatasetLoader:
    """Loader class for SOFC sintering dataset"""
    
    def __init__(self, data_dir="phase1_foundational_calibration_data"):
        """
        Initialize dataset loader
        
        Args:
            data_dir: Path to dataset directory
        """
        self.data_dir = Path(data_dir)
        self.data = {}
        
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Dataset directory not found: {self.data_dir}")
    
    def load_all(self):
        """Load all dataset files"""
        print("Loading Phase 1 Dataset...")
        
        # Material properties
        self.data['nio_ysz_props'] = pd.read_csv(
            self.data_dir / 'material_properties' / 'nio_ysz_anode_properties.csv'
        )
        self.data['ysz_props'] = pd.read_csv(
            self.data_dir / 'material_properties' / 'ysz_electrolyte_properties.csv'
        )
        self.data['functional_props'] = pd.read_csv(
            self.data_dir / 'material_properties' / 'functional_layer_properties.csv'
        )
        
        # Sintering kinetics
        self.data['sintering_stress'] = pd.read_csv(
            self.data_dir / 'sintering_kinetics' / 'nio_ysz_sintering_stress.csv'
        )
        self.data['msc_params'] = pd.read_csv(
            self.data_dir / 'sintering_kinetics' / 'master_sintering_curve_params.csv'
        )
        self.data['densification_rate'] = pd.read_csv(
            self.data_dir / 'sintering_kinetics' / 'densification_rate_data.csv'
        )
        
        # Microstructural evolution
        self.data['nio_ysz_micro'] = pd.read_csv(
            self.data_dir / 'microstructural_evolution' / 'nio_ysz_microstructure_timeseries.csv'
        )
        self.data['ysz_micro'] = pd.read_csv(
            self.data_dir / 'microstructural_evolution' / 'ysz_microstructure_timeseries.csv'
        )
        self.data['pore_distribution'] = pd.read_csv(
            self.data_dir / 'microstructural_evolution' / 'pore_size_distribution_data.csv'
        )
        
        # Process window
        self.data['experiments'] = pd.read_csv(
            self.data_dir / 'process_window_data' / 'sintering_profile_experiments.csv'
        )
        self.data['warpage'] = pd.read_csv(
            self.data_dir / 'process_window_data' / 'warpage_measurement_data.csv'
        )
        self.data['defects'] = pd.read_csv(
            self.data_dir / 'process_window_data' / 'defect_characterization.csv'
        )
        self.data['thermal_profiles'] = pd.read_csv(
            self.data_dir / 'process_window_data' / 'thermal_profile_measurements.csv'
        )
        self.data['action_space'] = pd.read_csv(
            self.data_dir / 'process_window_data' / 'action_space_boundaries.csv'
        )
        
        print(f"✓ Loaded {len(self.data)} dataset files")
        return self.data
    
    def print_summary(self):
        """Print dataset summary statistics"""
        print("\n" + "="*80)
        print("PHASE 1 DATASET SUMMARY")
        print("="*80)
        
        if not self.data:
            self.load_all()
        
        # Material Properties Summary
        print("\n1. MATERIAL PROPERTIES")
        print("-" * 80)
        print(f"   NiO-YSZ properties:     {len(self.data['nio_ysz_props'])} temperature points")
        print(f"   YSZ properties:         {len(self.data['ysz_props'])} temperature points")
        print(f"   Functional layers:      {len(self.data['functional_props'])} data points")
        print(f"   Temperature range:      {self.data['nio_ysz_props']['Temperature_C'].min():.0f} - "
              f"{self.data['nio_ysz_props']['Temperature_C'].max():.0f}°C")
        
        # Sintering Kinetics Summary
        print("\n2. SINTERING KINETICS")
        print("-" * 80)
        print(f"   Sintering stress data:  {len(self.data['sintering_stress'])} measurements")
        print(f"   Densification rates:    {len(self.data['densification_rate'])} experiments")
        print(f"   Materials characterized: {len(self.data['msc_params'])} (NiO-YSZ, YSZ, GDC, SDC)")
        density_range = self.data['sintering_stress']['Relative_Density']
        print(f"   Density range:          {density_range.min():.2f} - {density_range.max():.2f}")
        
        # Microstructural Evolution Summary
        print("\n3. MICROSTRUCTURAL EVOLUTION")
        print("-" * 80)
        print(f"   NiO-YSZ time-series:    {len(self.data['nio_ysz_micro'])} measurements")
        print(f"   YSZ time-series:        {len(self.data['ysz_micro'])} measurements")
        print(f"   Pore distributions:     {len(self.data['pore_distribution'])} data points")
        nio_temps = self.data['nio_ysz_micro']['Temperature_C'].unique()
        print(f"   Temperatures studied:   {len(nio_temps)} levels ({nio_temps.min():.0f}-{nio_temps.max():.0f}°C)")
        nio_times = self.data['nio_ysz_micro']['Time_min'].unique()
        print(f"   Time points:            {len(nio_times)} (0-{nio_times.max():.0f} min)")
        
        # Process Window Summary
        print("\n4. PROCESS WINDOW EXPERIMENTS")
        print("-" * 80)
        print(f"   Total experiments:      {len(self.data['experiments'])} unique profiles")
        nio_exp = self.data['experiments'][self.data['experiments']['Material'] == 'NiO-YSZ']
        ysz_exp = self.data['experiments'][self.data['experiments']['Material'] == 'YSZ']
        print(f"   NiO-YSZ experiments:    {len(nio_exp)}")
        print(f"   YSZ experiments:        {len(ysz_exp)}")
        cracking = self.data['experiments']['Cracking'].value_counts()
        print(f"   Successful (no crack):  {cracking.get('No', 0)}")
        print(f"   Failed (cracked):       {cracking.get('Yes', 0)}")
        print(f"   Warpage measurements:   {len(self.data['warpage'])} points")
        print(f"   Defect characterization: {len(self.data['defects'])} samples")
        
        # Key Metrics
        print("\n5. KEY PERFORMANCE METRICS")
        print("-" * 80)
        exp_data = self.data['experiments']
        print(f"   Density achieved:       {exp_data['Final_Density_percent'].min():.1f} - "
              f"{exp_data['Final_Density_percent'].max():.1f}%")
        print(f"   Warpage range:          {exp_data['Final_Warpage_mm'].min():.3f} - "
              f"{exp_data['Final_Warpage_mm'].max():.3f} mm")
        print(f"   Success rate:           {(cracking.get('No', 0) / len(exp_data) * 100):.1f}%")
        
        # Action Space
        print("\n6. ACTION SPACE BOUNDARIES (for RL)")
        print("-" * 80)
        action_space = self.data['action_space']
        key_params = ['Heating_Rate', 'Peak_Temperature', 'Hold_Time', 'Cooling_Rate']
        for param in key_params:
            param_data = action_space[action_space['Parameter'] == param].iloc[0]
            print(f"   {param:20s}: {param_data['Minimum_Value']:6.0f} - "
                  f"{param_data['Maximum_Value']:6.0f} {param_data['Unit']}")
        
        print("\n" + "="*80)
        print("Dataset ready for FEM calibration, Phase-Field modeling, and RL training!")
        print("="*80 + "\n")
    
    def plot_material_properties(self, material='NiO-YSZ', save=False):
        """
        Plot temperature-dependent material properties
        
        Args:
            material: Material to plot ('NiO-YSZ', 'YSZ')
            save: Whether to save figures
        """
        if not self.data:
            self.load_all()
        
        # Select data
        if material == 'NiO-YSZ':
            data = self.data['nio_ysz_props']
        elif material == 'YSZ':
            data = self.data['ysz_props']
        else:
            raise ValueError("Material must be 'NiO-YSZ' or 'YSZ'")
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle(f'{material} Temperature-Dependent Properties', fontsize=16, fontweight='bold')
        
        # CTE
        axes[0, 0].plot(data['Temperature_C'], data['CTE_1e-6_K'], 'o-', linewidth=2)
        axes[0, 0].set_xlabel('Temperature (°C)')
        axes[0, 0].set_ylabel('CTE (10⁻⁶/K)')
        axes[0, 0].set_title('Coefficient of Thermal Expansion')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Young's Modulus
        axes[0, 1].plot(data['Temperature_C'], data['Youngs_Modulus_GPa'], 'o-', linewidth=2, color='orange')
        axes[0, 1].set_xlabel('Temperature (°C)')
        axes[0, 1].set_ylabel("Young's Modulus (GPa)")
        axes[0, 1].set_title("Elastic Modulus")
        axes[0, 1].grid(True, alpha=0.3)
        
        # Viscosity (log scale)
        axes[0, 2].semilogy(data['Temperature_C'], data['Shear_Viscosity_Pa_s'], 'o-', linewidth=2, color='green')
        axes[0, 2].set_xlabel('Temperature (°C)')
        axes[0, 2].set_ylabel('Shear Viscosity (Pa·s)')
        axes[0, 2].set_title('Viscosity (log scale)')
        axes[0, 2].grid(True, alpha=0.3)
        
        # Density
        axes[1, 0].plot(data['Temperature_C'], data['Density_kg_m3'], 'o-', linewidth=2, color='red')
        axes[1, 0].set_xlabel('Temperature (°C)')
        axes[1, 0].set_ylabel('Density (kg/m³)')
        axes[1, 0].set_title('Material Density')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Thermal Conductivity
        axes[1, 1].plot(data['Temperature_C'], data['Thermal_Conductivity_W_mK'], 'o-', linewidth=2, color='purple')
        axes[1, 1].set_xlabel('Temperature (°C)')
        axes[1, 1].set_ylabel('Thermal Conductivity (W/m·K)')
        axes[1, 1].set_title('Thermal Conductivity')
        axes[1, 1].grid(True, alpha=0.3)
        
        # Specific Heat
        axes[1, 2].plot(data['Temperature_C'], data['Specific_Heat_J_kgK'], 'o-', linewidth=2, color='brown')
        axes[1, 2].set_xlabel('Temperature (°C)')
        axes[1, 2].set_ylabel('Specific Heat (J/kg·K)')
        axes[1, 2].set_title('Heat Capacity')
        axes[1, 2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{material}_properties.png', dpi=300, bbox_inches='tight')
            print(f"Saved figure: {material}_properties.png")
        
        plt.show()
    
    def plot_microstructure_evolution(self, material='NiO-YSZ', save=False):
        """
        Plot microstructural evolution during sintering
        
        Args:
            material: Material to plot
            save: Whether to save figures
        """
        if not self.data:
            self.load_all()
        
        if material == 'NiO-YSZ':
            data = self.data['nio_ysz_micro']
        else:
            data = self.data['ysz_micro']
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'{material} Microstructural Evolution', fontsize=16, fontweight='bold')
        
        # Plot for each temperature
        temps = sorted(data['Temperature_C'].unique())
        colors = plt.cm.viridis(np.linspace(0, 1, len(temps)))
        
        # Porosity vs Time
        for i, temp in enumerate(temps):
            temp_data = data[data['Temperature_C'] == temp]
            axes[0, 0].plot(temp_data['Time_min'], temp_data['Porosity_percent'], 
                           'o-', label=f'{temp}°C', color=colors[i], linewidth=2)
        axes[0, 0].set_xlabel('Time (min)')
        axes[0, 0].set_ylabel('Porosity (%)')
        axes[0, 0].set_title('Porosity Evolution')
        axes[0, 0].legend(ncol=2, fontsize=8)
        axes[0, 0].grid(True, alpha=0.3)
        
        # Grain Size vs Time
        for i, temp in enumerate(temps):
            temp_data = data[data['Temperature_C'] == temp]
            axes[0, 1].plot(temp_data['Time_min'], temp_data['Mean_Grain_Size_um'], 
                           'o-', label=f'{temp}°C', color=colors[i], linewidth=2)
        axes[0, 1].set_xlabel('Time (min)')
        axes[0, 1].set_ylabel('Mean Grain Size (μm)')
        axes[0, 1].set_title('Grain Growth')
        axes[0, 1].legend(ncol=2, fontsize=8)
        axes[0, 1].grid(True, alpha=0.3)
        
        # Pore Size vs Time
        for i, temp in enumerate(temps):
            temp_data = data[data['Temperature_C'] == temp]
            axes[1, 0].plot(temp_data['Time_min'], temp_data['Mean_Pore_Size_um'], 
                           'o-', label=f'{temp}°C', color=colors[i], linewidth=2)
        axes[1, 0].set_xlabel('Time (min)')
        axes[1, 0].set_ylabel('Mean Pore Size (μm)')
        axes[1, 0].set_title('Pore Size Evolution')
        axes[1, 0].legend(ncol=2, fontsize=8)
        axes[1, 0].grid(True, alpha=0.3)
        
        # Tortuosity vs Porosity
        axes[1, 1].scatter(data['Porosity_percent'], data['Tortuosity'], 
                          c=data['Temperature_C'], cmap='viridis', s=50, alpha=0.7)
        axes[1, 1].set_xlabel('Porosity (%)')
        axes[1, 1].set_ylabel('Tortuosity')
        axes[1, 1].set_title('Tortuosity vs Porosity')
        axes[1, 1].grid(True, alpha=0.3)
        cbar = plt.colorbar(axes[1, 1].collections[0], ax=axes[1, 1])
        cbar.set_label('Temperature (°C)')
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{material}_microstructure.png', dpi=300, bbox_inches='tight')
            print(f"Saved figure: {material}_microstructure.png")
        
        plt.show()
    
    def plot_process_window(self, save=False):
        """
        Plot process window results
        
        Args:
            save: Whether to save figures
        """
        if not self.data:
            self.load_all()
        
        data = self.data['experiments']
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Process Window Analysis', fontsize=16, fontweight='bold')
        
        # Density vs Temperature (colored by heating rate)
        for rate in sorted(data['Heating_Rate_C_min'].unique()):
            rate_data = data[data['Heating_Rate_C_min'] == rate]
            axes[0, 0].scatter(rate_data['Peak_Temperature_C'], rate_data['Final_Density_percent'],
                              label=f'{rate} °C/min', alpha=0.7, s=80)
        axes[0, 0].set_xlabel('Peak Temperature (°C)')
        axes[0, 0].set_ylabel('Final Density (%)')
        axes[0, 0].set_title('Density vs Temperature')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Warpage vs Temperature
        axes[0, 1].scatter(data['Peak_Temperature_C'], data['Final_Warpage_mm'],
                          c=data['Heating_Rate_C_min'], cmap='plasma', s=80, alpha=0.7)
        axes[0, 1].set_xlabel('Peak Temperature (°C)')
        axes[0, 1].set_ylabel('Final Warpage (mm)')
        axes[0, 1].set_title('Warpage vs Temperature')
        axes[0, 1].grid(True, alpha=0.3)
        cbar = plt.colorbar(axes[0, 1].collections[0], ax=axes[0, 1])
        cbar.set_label('Heating Rate (°C/min)')
        
        # Cracking distribution
        crack_data = data.groupby(['Peak_Temperature_C', 'Cracking']).size().unstack(fill_value=0)
        crack_data.plot(kind='bar', stacked=True, ax=axes[1, 0], color=['green', 'red'], alpha=0.7)
        axes[1, 0].set_xlabel('Peak Temperature (°C)')
        axes[1, 0].set_ylabel('Number of Experiments')
        axes[1, 0].set_title('Cracking by Temperature')
        axes[1, 0].legend(['No Crack', 'Cracked'])
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # Density vs Warpage (colored by cracking)
        no_crack = data[data['Cracking'] == 'No']
        cracked = data[data['Cracking'] == 'Yes']
        axes[1, 1].scatter(no_crack['Final_Density_percent'], no_crack['Final_Warpage_mm'],
                          label='No Crack', color='green', alpha=0.7, s=80)
        axes[1, 1].scatter(cracked['Final_Density_percent'], cracked['Final_Warpage_mm'],
                          label='Cracked', color='red', alpha=0.7, s=80, marker='x')
        axes[1, 1].set_xlabel('Final Density (%)')
        axes[1, 1].set_ylabel('Final Warpage (mm)')
        axes[1, 1].set_title('Density vs Warpage')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            plt.savefig('process_window_analysis.png', dpi=300, bbox_inches='tight')
            print("Saved figure: process_window_analysis.png")
        
        plt.show()


def main():
    """Main function for command-line interface"""
    parser = argparse.ArgumentParser(
        description='SOFC Phase 1 Dataset Loader and Explorer'
    )
    parser.add_argument('--explore', action='store_true',
                       help='Print dataset summary')
    parser.add_argument('--plot', choices=['material_properties', 'microstructure', 'process_window', 'all'],
                       help='Generate plots')
    parser.add_argument('--material', choices=['NiO-YSZ', 'YSZ'], default='NiO-YSZ',
                       help='Material for plotting')
    parser.add_argument('--save', action='store_true',
                       help='Save generated plots')
    
    args = parser.parse_args()
    
    # Initialize loader
    loader = SOFCDatasetLoader()
    
    # Execute requested operations
    if args.explore:
        loader.print_summary()
    
    if args.plot:
        if args.plot in ['material_properties', 'all']:
            loader.plot_material_properties(material=args.material, save=args.save)
        
        if args.plot in ['microstructure', 'all']:
            loader.plot_microstructure_evolution(material=args.material, save=args.save)
        
        if args.plot in ['process_window', 'all']:
            loader.plot_process_window(save=args.save)
    
    # If no arguments, show summary
    if not any(vars(args).values()):
        loader.print_summary()


if __name__ == '__main__':
    main()
