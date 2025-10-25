#!/usr/bin/env python3
"""
SOFC Dataset Downloader and Validator
Downloads and validates the comprehensive SOFC foundational dataset

This script provides utilities to:
1. Download pre-generated datasets
2. Validate data integrity
3. Load datasets for analysis
4. Generate additional synthetic data if needed

Usage:
    python download_dataset.py --generate-all
    python download_dataset.py --validate
    python download_dataset.py --load-sample
"""

import argparse
import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import json
import zipfile
import requests
from urllib.parse import urlparse
import hashlib

class SOFCDatasetDownloader:
    def __init__(self, base_dir="sofc_dataset"):
        self.base_dir = Path(base_dir)
        self.dataset_urls = {
            # These would be real URLs in production
            'thermophysical': 'https://example.com/sofc_thermophysical.csv',
            'kinetics': 'https://example.com/sofc_kinetics.csv',
            'microstructure': 'https://example.com/sofc_microstructure.csv',
            'process_window': 'https://example.com/sofc_process_window.csv'
        }
        
        # Expected file checksums for validation
        self.expected_checksums = {
            'all_materials_properties.csv': None,  # Will be calculated after generation
            'all_materials_kinetics.csv': None,
            'all_materials_evolution.csv': None,
            'sintering_experiments.csv': None
        }
    
    def download_dataset(self, dataset_name, url, output_path):
        """Download dataset from URL"""
        print(f"Downloading {dataset_name} from {url}")
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"  Downloaded: {output_path}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"  Failed to download {dataset_name}: {e}")
            return False
    
    def validate_dataset(self, file_path):
        """Validate dataset integrity"""
        if not file_path.exists():
            return False, f"File not found: {file_path}"
        
        try:
            # Try to load as CSV
            df = pd.read_csv(file_path)
            
            # Basic validation checks
            if df.empty:
                return False, "Dataset is empty"
            
            if df.isnull().all().any():
                return False, "Dataset contains columns with all null values"
            
            # Check for reasonable data ranges
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df[col].isna().all():
                    continue
                if np.isinf(df[col]).any():
                    return False, f"Column {col} contains infinite values"
            
            return True, f"Valid dataset with {len(df)} rows, {len(df.columns)} columns"
            
        except Exception as e:
            return False, f"Error reading dataset: {e}"
    
    def calculate_checksum(self, file_path):
        """Calculate MD5 checksum of file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def load_sample_data(self):
        """Load and display sample data from each dataset"""
        print("\n=== Loading Sample Data ===")
        
        dataset_files = {
            'Thermophysical Properties': self.base_dir / 'thermophysical' / 'all_materials_properties.csv',
            'Sintering Kinetics': self.base_dir / 'sintering_kinetics' / 'all_materials_kinetics.csv',
            'Microstructural Evolution': self.base_dir / 'microstructure' / 'all_materials_evolution.csv',
            'Process Window': self.base_dir / 'process_window' / 'sintering_experiments.csv'
        }
        
        for name, file_path in dataset_files.items():
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    print(f"\n{name}:")
                    print(f"  Shape: {df.shape}")
                    print(f"  Columns: {list(df.columns)}")
                    print(f"  Sample data:")
                    print(df.head(3).to_string(index=False))
                    
                    # Show basic statistics for numeric columns
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        print(f"  Statistics:")
                        stats = df[numeric_cols].describe()
                        print(stats.iloc[:3].round(4).to_string())  # Show count, mean, std
                        
                except Exception as e:
                    print(f"  Error loading {name}: {e}")
            else:
                print(f"\n{name}: File not found at {file_path}")
    
    def validate_all_datasets(self):
        """Validate all generated datasets"""
        print("\n=== Validating All Datasets ===")
        
        validation_results = {}
        
        # Find all CSV files in the dataset directory
        csv_files = list(self.base_dir.rglob("*.csv"))
        
        for csv_file in csv_files:
            relative_path = csv_file.relative_to(self.base_dir)
            is_valid, message = self.validate_dataset(csv_file)
            validation_results[str(relative_path)] = {
                'valid': is_valid,
                'message': message,
                'size_mb': csv_file.stat().st_size / (1024 * 1024),
                'checksum': self.calculate_checksum(csv_file) if is_valid else None
            }
            
            status = "✓" if is_valid else "✗"
            print(f"{status} {relative_path}: {message}")
        
        # Save validation report
        report_path = self.base_dir / "validation_report.json"
        with open(report_path, 'w') as f:
            json.dump(validation_results, f, indent=2)
        
        print(f"\nValidation report saved: {report_path}")
        
        # Summary
        valid_count = sum(1 for r in validation_results.values() if r['valid'])
        total_count = len(validation_results)
        total_size = sum(r['size_mb'] for r in validation_results.values())
        
        print(f"\nValidation Summary:")
        print(f"  Valid files: {valid_count}/{total_count}")
        print(f"  Total size: {total_size:.2f} MB")
        
        return validation_results
    
    def generate_data_dictionary(self):
        """Generate comprehensive data dictionary"""
        print("\n=== Generating Data Dictionary ===")
        
        data_dictionary = {
            "thermophysical_properties": {
                "description": "Temperature-dependent material properties for FEM modeling",
                "source": "Generated from literature models and experimental correlations",
                "fields": {
                    "Temperature_C": "Temperature in Celsius (20-1400°C)",
                    "CTE_per_K": "Coefficient of Thermal Expansion (1/K)",
                    "Youngs_Modulus_GPa": "Young's Modulus (GPa)",
                    "Poisson_Ratio": "Poisson's Ratio (dimensionless)",
                    "Shear_Viscosity_Pa_s": "Shear Viscosity for sintering (Pa·s)",
                    "Density_g_cm3": "Density (g/cm³)",
                    "Material": "Material type (anode, electrolyte, functional_layer)",
                    "Composition": "Material composition description"
                },
                "experimental_methods": [
                    "Dynamical Mechanical Analysis (DMA)",
                    "Dilatometry",
                    "Nanoindentation"
                ]
            },
            "sintering_kinetics": {
                "description": "Kinetic parameters for phase-field modeling",
                "source": "Master sintering curve models and densification theory",
                "fields": {
                    "Temperature_C": "Sintering temperature (1200-1400°C)",
                    "Relative_Density": "Relative density (0.45-0.95)",
                    "Hold_Time_min": "Hold time at temperature (1-1000 min)",
                    "Sintering_Stress_MPa": "Sintering stress (MPa)",
                    "Bulk_Viscosity_Pa_s": "Bulk viscosity (Pa·s)",
                    "Shear_Viscosity_Pa_s": "Shear viscosity (Pa·s)",
                    "Densification_Rate_per_s": "Densification rate (1/s)",
                    "Grain_Growth_Rate_um_per_s": "Grain growth rate (μm/s)"
                },
                "experimental_methods": [
                    "Dilatometry at multiple heating rates",
                    "Master sintering curve analysis",
                    "Interrupted sintering tests"
                ]
            },
            "microstructural_evolution": {
                "description": "Time-series microstructural data for model validation",
                "source": "Interrupted sintering experiments with SEM/CT analysis",
                "fields": {
                    "Temperature_C": "Sintering temperature (1250-1400°C)",
                    "Time_min": "Sintering time (0-480 min)",
                    "Porosity_fraction": "Porosity fraction (0-1)",
                    "Average_Pore_Size_um": "Average pore size (μm)",
                    "Pore_Size_Std_um": "Pore size standard deviation (μm)",
                    "Average_Grain_Size_um": "Average grain size (μm)",
                    "Grain_Size_Std_um": "Grain size standard deviation (μm)",
                    "Tortuosity": "Tortuosity factor",
                    "Connectivity_factor": "Pore connectivity factor",
                    "Surface_Area_m2_g": "Specific surface area (m²/g)"
                },
                "experimental_methods": [
                    "Quenched interrupted sintering",
                    "SEM imaging and analysis",
                    "X-ray Computed Tomography",
                    "Image analysis and quantification"
                ]
            },
            "process_window": {
                "description": "Initial sintering experiments for RL training",
                "source": "Systematic process parameter variation study",
                "fields": {
                    "Experiment_ID": "Unique experiment identifier",
                    "Heating_Rate_C_per_min": "Heating rate (1-20°C/min)",
                    "Peak_Temperature_C": "Peak sintering temperature (1200-1400°C)",
                    "Hold_Time_min": "Hold time at peak temperature (0-480 min)",
                    "Atmosphere": "Sintering atmosphere",
                    "Total_Cycle_Time_min": "Total cycle time (min)",
                    "Warpage_Max_mm": "Maximum warpage (mm)",
                    "Warpage_RMS_mm": "RMS warpage (mm)",
                    "Cracking": "Presence of cracks (boolean)",
                    "Final_Relative_Density": "Final relative density",
                    "Final_Porosity_fraction": "Final porosity fraction",
                    "Average_Grain_Size_um": "Final average grain size (μm)",
                    "Success": "Overall success (boolean)",
                    "Quality_Score": "Quality score (0-100)"
                },
                "experimental_methods": [
                    "3D profilometry for warpage measurement",
                    "Visual inspection for cracking",
                    "Density measurement",
                    "Microstructural analysis"
                ]
            }
        }
        
        # Save data dictionary
        dict_path = self.base_dir / "data_dictionary.json"
        with open(dict_path, 'w') as f:
            json.dump(data_dictionary, f, indent=2)
        
        print(f"Data dictionary saved: {dict_path}")
        return data_dictionary

def main():
    parser = argparse.ArgumentParser(description='SOFC Dataset Downloader and Validator')
    parser.add_argument('--generate-all', action='store_true', 
                       help='Generate all datasets locally')
    parser.add_argument('--validate', action='store_true',
                       help='Validate existing datasets')
    parser.add_argument('--load-sample', action='store_true',
                       help='Load and display sample data')
    parser.add_argument('--data-dict', action='store_true',
                       help='Generate data dictionary')
    parser.add_argument('--output-dir', default='sofc_dataset',
                       help='Output directory for datasets')
    
    args = parser.parse_args()
    
    downloader = SOFCDatasetDownloader(args.output_dir)
    
    if args.generate_all:
        print("Generating all SOFC datasets locally...")
        # Import and run the main generator
        try:
            from sofc_foundational_dataset import main as generate_main
            generate_main()
        except ImportError:
            print("Error: sofc_foundational_dataset.py not found. Please ensure it's in the same directory.")
            sys.exit(1)
    
    if args.validate:
        downloader.validate_all_datasets()
    
    if args.load_sample:
        downloader.load_sample_data()
    
    if args.data_dict:
        downloader.generate_data_dictionary()
    
    if not any([args.generate_all, args.validate, args.load_sample, args.data_dict]):
        parser.print_help()

if __name__ == "__main__":
    main()