#!/usr/bin/env python3
"""
SOFC Dataset Validation and Visualization Script
===============================================

This script validates the generated SOFC foundational datasets and creates
comprehensive visualizations to verify data quality and physical realism.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import h5py
import json
import os
from datetime import datetime

class SOFCDatasetValidator:
    """Validator for SOFC foundational datasets"""
    
    def __init__(self, dataset_dir="/workspace/sofc_datasets"):
        self.dataset_dir = dataset_dir
        self.validation_results = {}
        
    def validate_all_datasets(self):
        """Validate all generated datasets"""
        print("="*60)
        print("SOFC DATASET VALIDATION")
        print("="*60)
        
        # Validate each dataset type
        self.validate_material_properties()
        self.validate_sintering_kinetics()
        self.validate_microstructural_evolution()
        self.validate_process_window()
        
        # Generate validation report
        self.generate_validation_report()
        
        print("\n" + "="*60)
        print("VALIDATION COMPLETE!")
        print("="*60)
        
    def validate_material_properties(self):
        """Validate material properties data"""
        print("\nValidating Material Properties...")
        
        # Load material summary
        summary_df = pd.read_csv(f"{self.dataset_dir}/material_properties/material_summary.csv")
        
        validation_results = {
            'materials_count': len(summary_df),
            'properties_validated': True,
            'temperature_range': '25-1400°C',
            'issues': []
        }
        
        # Check for reasonable property values
        for _, row in summary_df.iterrows():
            material = row['Material']
            
            # Check Young's modulus (should be 100-300 GPa)
            if not (100 <= row['Youngs_Modulus_25C_GPa'] <= 300):
                validation_results['issues'].append(f"{material}: Young's modulus out of range")
            
            # Check CTE (should be 8-15 × 10⁻⁶ K⁻¹)
            if not (8e-6 <= row['CTE_25C_1perK'] <= 15e-6):
                validation_results['issues'].append(f"{material}: CTE out of range")
            
            # Check density (should be 5-8 g/cm³)
            if not (5 <= row['Density_25C_g_per_cm3'] <= 8):
                validation_results['issues'].append(f"{material}: Density out of range")
        
        # Load individual material data for detailed validation
        materials = ['NiO_YSZ_anode', 'YSZ_electrolyte', 'LSCF_cathode', 'GDC_interlayer']
        
        for material in materials:
            df = pd.read_csv(f"{self.dataset_dir}/material_properties/{material}_properties.csv")
            
            # Check temperature dependence trends
            if not np.all(np.diff(df['Youngs_Modulus_Pa']) <= 0):
                validation_results['issues'].append(f"{material}: Young's modulus should decrease with temperature")
            
            if not np.all(np.diff(df['CTE_1perK']) >= 0):
                validation_results['issues'].append(f"{material}: CTE should increase with temperature")
            
            if not np.all(np.diff(df['Density_kg_per_m3']) <= 0):
                validation_results['issues'].append(f"{material}: Density should decrease with temperature")
        
        validation_results['status'] = 'PASS' if len(validation_results['issues']) == 0 else 'WARNINGS'
        self.validation_results['material_properties'] = validation_results
        
        print(f"  Status: {validation_results['status']}")
        print(f"  Materials: {validation_results['materials_count']}")
        print(f"  Issues: {len(validation_results['issues'])}")
        
    def validate_sintering_kinetics(self):
        """Validate sintering kinetics data"""
        print("\nValidating Sintering Kinetics...")
        
        validation_results = {
            'materials_count': 4,
            'temperature_range': '800-1400°C',
            'density_range': '0.5-0.99',
            'issues': []
        }
        
        materials = ['NiO_YSZ_anode', 'YSZ_electrolyte', 'LSCF_cathode', 'GDC_interlayer']
        
        for material in materials:
            df = pd.read_csv(f"{self.dataset_dir}/sintering_kinetics/{material}_sintering_kinetics.csv")
            
            # Check sintering stress trends
            for temp in df['Temperature_C'].unique():
                temp_data = df[df['Temperature_C'] == temp]
                if not np.all(np.diff(temp_data['Sintering_Stress_Pa']) <= 0):
                    validation_results['issues'].append(f"{material}: Sintering stress should decrease with density")
            
            # Check viscosity trends
            for temp in df['Temperature_C'].unique():
                temp_data = df[df['Temperature_C'] == temp]
                if not np.all(np.diff(temp_data['Shear_Viscosity_Pa_s']) >= 0):
                    validation_results['issues'].append(f"{material}: Viscosity should increase with density")
            
            # Check for reasonable viscosity values (10⁶ to 10¹⁵ Pa·s)
            if not np.all((1e6 <= df['Shear_Viscosity_Pa_s']) & (df['Shear_Viscosity_Pa_s'] <= 1e15)):
                validation_results['issues'].append(f"{material}: Viscosity values out of reasonable range")
        
        validation_results['status'] = 'PASS' if len(validation_results['issues']) == 0 else 'WARNINGS'
        self.validation_results['sintering_kinetics'] = validation_results
        
        print(f"  Status: {validation_results['status']}")
        print(f"  Materials: {validation_results['materials_count']}")
        print(f"  Issues: {len(validation_results['issues'])}")
        
    def validate_microstructural_evolution(self):
        """Validate microstructural evolution data"""
        print("\nValidating Microstructural Evolution...")
        
        validation_results = {
            'temperatures': 8,
            'time_points': 8,
            'issues': []
        }
        
        # Load summary data
        df = pd.read_csv(f"{self.dataset_dir}/microstructural_evolution/microstructural_summary.csv")
        
        # Check porosity evolution (should decrease with time)
        for temp in df['Temperature_C'].unique():
            temp_data = df[df['Temperature_C'] == temp].sort_values('Time_s')
            if not np.all(np.diff(temp_data['Porosity']) <= 0):
                validation_results['issues'].append(f"Temperature {temp}°C: Porosity should decrease with time")
        
        # Check grain size evolution (should increase with time)
        for temp in df['Temperature_C'].unique():
            temp_data = df[df['Temperature_C'] == temp].sort_values('Time_s')
            if not np.all(np.diff(temp_data['Grain_Size_m']) >= 0):
                validation_results['issues'].append(f"Temperature {temp}°C: Grain size should increase with time")
        
        # Check tortuosity evolution (should increase as porosity decreases)
        for temp in df['Temperature_C'].unique():
            temp_data = df[df['Temperature_C'] == temp].sort_values('Time_s')
            if not np.all(np.diff(temp_data['Tortuosity']) >= 0):
                validation_results['issues'].append(f"Temperature {temp}°C: Tortuosity should increase with time")
        
        # Check for reasonable porosity values (0-0.5)
        if not np.all((0 <= df['Porosity']) & (df['Porosity'] <= 0.5)):
            validation_results['issues'].append("Porosity values out of reasonable range (0-0.5)")
        
        validation_results['status'] = 'PASS' if len(validation_results['issues']) == 0 else 'WARNINGS'
        self.validation_results['microstructural_evolution'] = validation_results
        
        print(f"  Status: {validation_results['status']}")
        print(f"  Temperatures: {validation_results['temperatures']}")
        print(f"  Issues: {len(validation_results['issues'])}")
        
    def validate_process_window(self):
        """Validate process window data"""
        print("\nValidating Process Window...")
        
        validation_results = {
            'total_combinations': 0,
            'success_rate': 0,
            'issues': []
        }
        
        # Load process window data
        df = pd.read_csv(f"{self.dataset_dir}/process_window/process_window_data.csv")
        validation_results['total_combinations'] = len(df)
        validation_results['success_rate'] = df['Success_Score'].mean()
        
        # Check for reasonable parameter ranges
        if not np.all((1 <= df['Heating_Rate_C_per_min']) & (df['Heating_Rate_C_per_min'] <= 20)):
            validation_results['issues'].append("Heating rate out of reasonable range (1-20°C/min)")
        
        if not np.all((1200 <= df['Peak_Temperature_C']) & (df['Peak_Temperature_C'] <= 1450)):
            validation_results['issues'].append("Peak temperature out of reasonable range (1200-1450°C)")
        
        if not np.all((30 <= df['Hold_Time_min']) & (df['Hold_Time_min'] <= 360)):
            validation_results['issues'].append("Hold time out of reasonable range (30-360 min)")
        
        # Check for reasonable output values
        if not np.all((0.5 <= df['Final_Density']) & (df['Final_Density'] <= 0.99)):
            validation_results['issues'].append("Final density out of reasonable range (0.5-0.99)")
        
        if not np.all(df['Warpage_um'] >= 0):
            validation_results['issues'].append("Warpage should be non-negative")
        
        if not np.all((0 <= df['Porosity']) & (df['Porosity'] <= 0.5)):
            validation_results['issues'].append("Porosity out of reasonable range (0-0.5)")
        
        validation_results['status'] = 'PASS' if len(validation_results['issues']) == 0 else 'WARNINGS'
        self.validation_results['process_window'] = validation_results
        
        print(f"  Status: {validation_results['status']}")
        print(f"  Combinations: {validation_results['total_combinations']}")
        print(f"  Success Rate: {validation_results['success_rate']:.2%}")
        print(f"  Issues: {len(validation_results['issues'])}")
        
    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        report = {
            'validation_date': datetime.now().isoformat(),
            'overall_status': 'PASS',
            'datasets_validated': len(self.validation_results),
            'total_issues': 0,
            'summary': {},
            'detailed_results': self.validation_results
        }
        
        # Calculate overall status
        for dataset, results in self.validation_results.items():
            report['total_issues'] += len(results['issues'])
            if results['status'] != 'PASS':
                report['overall_status'] = 'WARNINGS'
        
        # Generate summary
        report['summary'] = {
            'material_properties': {
                'status': self.validation_results['material_properties']['status'],
                'materials': self.validation_results['material_properties']['materials_count'],
                'issues': len(self.validation_results['material_properties']['issues'])
            },
            'sintering_kinetics': {
                'status': self.validation_results['sintering_kinetics']['status'],
                'materials': self.validation_results['sintering_kinetics']['materials_count'],
                'issues': len(self.validation_results['sintering_kinetics']['issues'])
            },
            'microstructural_evolution': {
                'status': self.validation_results['microstructural_evolution']['status'],
                'temperatures': self.validation_results['microstructural_evolution']['temperatures'],
                'issues': len(self.validation_results['microstructural_evolution']['issues'])
            },
            'process_window': {
                'status': self.validation_results['process_window']['status'],
                'combinations': self.validation_results['process_window']['total_combinations'],
                'success_rate': self.validation_results['process_window']['success_rate'],
                'issues': len(self.validation_results['process_window']['issues'])
            }
        }
        
        # Save validation report
        with open(f"{self.dataset_dir}/validation_report.json", 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\nValidation Report:")
        print(f"  Overall Status: {report['overall_status']}")
        print(f"  Datasets Validated: {report['datasets_validated']}")
        print(f"  Total Issues: {report['total_issues']}")
        print(f"  Report saved to: {self.dataset_dir}/validation_report.json")
        
    def create_visualizations(self):
        """Create comprehensive visualizations of the datasets"""
        print("\nGenerating Visualizations...")
        
        # Create visualization directory
        viz_dir = f"{self.dataset_dir}/visualizations"
        os.makedirs(viz_dir, exist_ok=True)
        
        # Material properties visualizations
        self._plot_material_properties(viz_dir)
        
        # Sintering kinetics visualizations
        self._plot_sintering_kinetics(viz_dir)
        
        # Microstructural evolution visualizations
        self._plot_microstructural_evolution(viz_dir)
        
        # Process window visualizations
        self._plot_process_window(viz_dir)
        
        print(f"  Visualizations saved to: {viz_dir}")
        
    def _plot_material_properties(self, viz_dir):
        """Create material properties visualizations"""
        materials = ['NiO_YSZ_anode', 'YSZ_electrolyte', 'LSCF_cathode', 'GDC_interlayer']
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Material Properties vs Temperature', fontsize=16)
        
        # Young's Modulus
        ax = axes[0, 0]
        for material in materials:
            df = pd.read_csv(f"{self.dataset_dir}/material_properties/{material}_properties.csv")
            ax.plot(df['Temperature_C'], df['Youngs_Modulus_Pa']/1e9, 
                   label=material.replace('_', ' '), linewidth=2)
        ax.set_xlabel('Temperature (°C)')
        ax.set_ylabel('Young\'s Modulus (GPa)')
        ax.set_title('Young\'s Modulus vs Temperature')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # CTE
        ax = axes[0, 1]
        for material in materials:
            df = pd.read_csv(f"{self.dataset_dir}/material_properties/{material}_properties.csv")
            ax.plot(df['Temperature_C'], df['CTE_1perK']*1e6, 
                   label=material.replace('_', ' '), linewidth=2)
        ax.set_xlabel('Temperature (°C)')
        ax.set_ylabel('CTE (×10⁻⁶ K⁻¹)')
        ax.set_title('Coefficient of Thermal Expansion vs Temperature')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Density
        ax = axes[1, 0]
        for material in materials:
            df = pd.read_csv(f"{self.dataset_dir}/material_properties/{material}_properties.csv")
            ax.plot(df['Temperature_C'], df['Density_kg_per_m3']/1000, 
                   label=material.replace('_', ' '), linewidth=2)
        ax.set_xlabel('Temperature (°C)')
        ax.set_ylabel('Density (g/cm³)')
        ax.set_title('Density vs Temperature')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Viscosity
        ax = axes[1, 1]
        for material in materials:
            df = pd.read_csv(f"{self.dataset_dir}/material_properties/{material}_properties.csv")
            ax.semilogy(df['Temperature_C'], df['Shear_Viscosity_Pa_s'], 
                       label=material.replace('_', ' '), linewidth=2)
        ax.set_xlabel('Temperature (°C)')
        ax.set_ylabel('Shear Viscosity (Pa·s)')
        ax.set_title('Shear Viscosity vs Temperature')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{viz_dir}/material_properties.png", dpi=300, bbox_inches='tight')
        plt.close()
        
    def _plot_sintering_kinetics(self, viz_dir):
        """Create sintering kinetics visualizations"""
        materials = ['NiO_YSZ_anode', 'YSZ_electrolyte', 'LSCF_cathode', 'GDC_interlayer']
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Sintering Kinetics', fontsize=16)
        
        # Sintering stress vs density
        ax = axes[0, 0]
        for material in materials:
            df = pd.read_csv(f"{self.dataset_dir}/sintering_kinetics/{material}_sintering_kinetics.csv")
            # Plot at 1200°C
            temp_data = df[df['Temperature_C'] == 1200]
            if not temp_data.empty:
                ax.plot(temp_data['Density'], temp_data['Sintering_Stress_Pa']/1e6, 
                       label=material.replace('_', ' '), linewidth=2, marker='o')
        ax.set_xlabel('Relative Density')
        ax.set_ylabel('Sintering Stress (MPa)')
        ax.set_title('Sintering Stress vs Density (1200°C)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Viscosity vs temperature
        ax = axes[0, 1]
        for material in materials:
            df = pd.read_csv(f"{self.dataset_dir}/sintering_kinetics/{material}_sintering_kinetics.csv")
            # Plot at 0.7 density
            density_data = df[df['Density'] == 0.7]
            if not density_data.empty:
                ax.semilogy(density_data['Temperature_C'], density_data['Shear_Viscosity_Pa_s'], 
                           label=material.replace('_', ' '), linewidth=2, marker='s')
        ax.set_xlabel('Temperature (°C)')
        ax.set_ylabel('Shear Viscosity (Pa·s)')
        ax.set_title('Shear Viscosity vs Temperature (ρ=0.7)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Densification rate
        ax = axes[1, 0]
        for material in materials:
            df = pd.read_csv(f"{self.dataset_dir}/sintering_kinetics/{material}_sintering_kinetics.csv")
            # Plot at 1200°C
            temp_data = df[df['Temperature_C'] == 1200]
            if not temp_data.empty:
                ax.plot(temp_data['Density'], temp_data['Densification_Rate_1per_s'], 
                       label=material.replace('_', ' '), linewidth=2, marker='^')
        ax.set_xlabel('Relative Density')
        ax.set_ylabel('Densification Rate (1/s)')
        ax.set_title('Densification Rate vs Density (1200°C)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 3D surface plot of sintering stress
        ax = axes[1, 1]
        material = 'NiO_YSZ_anode'  # Use one material for 3D plot
        df = pd.read_csv(f"{self.dataset_dir}/sintering_kinetics/{material}_sintering_kinetics.csv")
        
        # Create pivot table for 3D plotting
        pivot = df.pivot(index='Density', columns='Temperature_C', values='Sintering_Stress_Pa')
        
        im = ax.contourf(pivot.columns, pivot.index, pivot.values/1e6, levels=20, cmap='viridis')
        ax.set_xlabel('Temperature (°C)')
        ax.set_ylabel('Relative Density')
        ax.set_title(f'Sintering Stress Map - {material.replace("_", " ")}')
        plt.colorbar(im, ax=ax, label='Sintering Stress (MPa)')
        
        plt.tight_layout()
        plt.savefig(f"{viz_dir}/sintering_kinetics.png", dpi=300, bbox_inches='tight')
        plt.close()
        
    def _plot_microstructural_evolution(self, viz_dir):
        """Create microstructural evolution visualizations"""
        df = pd.read_csv(f"{self.dataset_dir}/microstructural_evolution/microstructural_summary.csv")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Microstructural Evolution During Sintering', fontsize=16)
        
        # Porosity evolution
        ax = axes[0, 0]
        for temp in sorted(df['Temperature_C'].unique()):
            temp_data = df[df['Temperature_C'] == temp].sort_values('Time_s')
            ax.plot(temp_data['Time_s']/60, temp_data['Porosity'], 
                   label=f'{temp}°C', linewidth=2, marker='o')
        ax.set_xlabel('Time (min)')
        ax.set_ylabel('Porosity')
        ax.set_title('Porosity Evolution')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Grain size evolution
        ax = axes[0, 1]
        for temp in sorted(df['Temperature_C'].unique()):
            temp_data = df[df['Temperature_C'] == temp].sort_values('Time_s')
            ax.plot(temp_data['Time_s']/60, temp_data['Grain_Size_m']*1e6, 
                   label=f'{temp}°C', linewidth=2, marker='s')
        ax.set_xlabel('Time (min)')
        ax.set_ylabel('Grain Size (μm)')
        ax.set_title('Grain Size Evolution')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Pore size evolution
        ax = axes[1, 0]
        for temp in sorted(df['Temperature_C'].unique()):
            temp_data = df[df['Temperature_C'] == temp].sort_values('Time_s')
            ax.plot(temp_data['Time_s']/60, temp_data['Pore_Size_m']*1e6, 
                   label=f'{temp}°C', linewidth=2, marker='^')
        ax.set_xlabel('Time (min)')
        ax.set_ylabel('Pore Size (μm)')
        ax.set_title('Pore Size Evolution')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Tortuosity evolution
        ax = axes[1, 1]
        for temp in sorted(df['Temperature_C'].unique()):
            temp_data = df[df['Temperature_C'] == temp].sort_values('Time_s')
            ax.plot(temp_data['Time_s']/60, temp_data['Tortuosity'], 
                   label=f'{temp}°C', linewidth=2, marker='d')
        ax.set_xlabel('Time (min)')
        ax.set_ylabel('Tortuosity')
        ax.set_title('Tortuosity Evolution')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{viz_dir}/microstructural_evolution.png", dpi=300, bbox_inches='tight')
        plt.close()
        
    def _plot_process_window(self, viz_dir):
        """Create process window visualizations"""
        df = pd.read_csv(f"{self.dataset_dir}/process_window/process_window_data.csv")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Process Window Analysis', fontsize=16)
        
        # Success rate by heating rate
        ax = axes[0, 0]
        success_by_hr = df.groupby('Heating_Rate_C_per_min')['Success_Score'].mean()
        ax.bar(success_by_hr.index, success_by_hr.values, alpha=0.7, color='skyblue')
        ax.set_xlabel('Heating Rate (°C/min)')
        ax.set_ylabel('Average Success Score')
        ax.set_title('Success Rate vs Heating Rate')
        ax.grid(True, alpha=0.3)
        
        # Success rate by temperature
        ax = axes[0, 1]
        success_by_temp = df.groupby('Peak_Temperature_C')['Success_Score'].mean()
        ax.bar(success_by_temp.index, success_by_temp.values, alpha=0.7, color='lightgreen')
        ax.set_xlabel('Peak Temperature (°C)')
        ax.set_ylabel('Average Success Score')
        ax.set_title('Success Rate vs Peak Temperature')
        ax.grid(True, alpha=0.3)
        
        # Warpage vs density
        ax = axes[1, 0]
        scatter = ax.scatter(df['Final_Density'], df['Warpage_um'], 
                           c=df['Success_Score'], cmap='RdYlGn', alpha=0.6)
        ax.set_xlabel('Final Density')
        ax.set_ylabel('Warpage (μm)')
        ax.set_title('Warpage vs Final Density')
        plt.colorbar(scatter, ax=ax, label='Success Score')
        ax.grid(True, alpha=0.3)
        
        # Process window heatmap
        ax = axes[1, 1]
        pivot = df.pivot_table(values='Success_Score', 
                              index='Heating_Rate_C_per_min', 
                              columns='Peak_Temperature_C', 
                              aggfunc='mean')
        im = ax.imshow(pivot.values, cmap='RdYlGn', aspect='auto')
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(pivot.columns)
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index)
        ax.set_xlabel('Peak Temperature (°C)')
        ax.set_ylabel('Heating Rate (°C/min)')
        ax.set_title('Process Window Heatmap')
        plt.colorbar(im, ax=ax, label='Success Score')
        
        plt.tight_layout()
        plt.savefig(f"{viz_dir}/process_window.png", dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    # Validate and visualize datasets
    validator = SOFCDatasetValidator()
    validator.validate_all_datasets()
    validator.create_visualizations()