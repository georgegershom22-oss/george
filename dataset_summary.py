#!/usr/bin/env python3
"""
SOFC Dataset Summary and Statistics
===================================

This script provides a comprehensive summary of the generated SOFC foundational dataset.
"""

import os
import pandas as pd
import h5py
import json
from datetime import datetime

def get_file_size_mb(filepath):
    """Get file size in MB"""
    if os.path.exists(filepath):
        return os.path.getsize(filepath) / (1024 * 1024)
    return 0

def count_data_points(filepath):
    """Count data points in CSV file"""
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        return len(df)
    return 0

def main():
    print("="*80)
    print("SOFC FOUNDATIONAL & CALIBRATION DATASET SUMMARY")
    print("="*80)
    print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    dataset_dir = "/workspace/sofc_datasets"
    
    # Dataset overview
    print("📊 DATASET OVERVIEW")
    print("-" * 40)
    
    total_files = 0
    total_size = 0
    total_data_points = 0
    
    # Material Properties
    print("\n🔬 MATERIAL PROPERTIES")
    print("-" * 30)
    mp_dir = f"{dataset_dir}/material_properties"
    mp_files = os.listdir(mp_dir)
    mp_size = sum(get_file_size_mb(f"{mp_dir}/{f}") for f in mp_files)
    mp_points = sum(count_data_points(f"{mp_dir}/{f}") for f in mp_files if f.endswith('.csv'))
    
    print(f"  Files: {len(mp_files)}")
    print(f"  Size: {mp_size:.2f} MB")
    print(f"  Data Points: {mp_points:,}")
    print(f"  Materials: 4 (NiO-YSZ, YSZ, LSCF, GDC)")
    print(f"  Temperature Range: 25°C - 1400°C")
    print(f"  Properties: 10 per material")
    
    total_files += len(mp_files)
    total_size += mp_size
    total_data_points += mp_points
    
    # Sintering Kinetics
    print("\n⚗️ SINTERING KINETICS")
    print("-" * 30)
    sk_dir = f"{dataset_dir}/sintering_kinetics"
    sk_files = os.listdir(sk_dir)
    sk_size = sum(get_file_size_mb(f"{sk_dir}/{f}") for f in sk_files)
    sk_points = sum(count_data_points(f"{sk_dir}/{f}") for f in sk_files if f.endswith('.csv'))
    
    print(f"  Files: {len(sk_files)}")
    print(f"  Size: {sk_size:.2f} MB")
    print(f"  Data Points: {sk_points:,}")
    print(f"  Materials: 4")
    print(f"  Temperature Range: 800°C - 1400°C")
    print(f"  Density Range: 0.5 - 0.99")
    print(f"  Parameters: 4 per material")
    
    total_files += len(sk_files)
    total_size += sk_size
    total_data_points += sk_points
    
    # Microstructural Evolution
    print("\n🔬 MICROSTRUCTURAL EVOLUTION")
    print("-" * 30)
    me_dir = f"{dataset_dir}/microstructural_evolution"
    me_files = os.listdir(me_dir)
    me_size = sum(get_file_size_mb(f"{me_dir}/{f}") for f in me_files)
    me_points = sum(count_data_points(f"{me_dir}/{f}") for f in me_files if f.endswith('.csv'))
    
    print(f"  Files: {len(me_files)}")
    print(f"  Size: {me_size:.2f} MB")
    print(f"  Data Points: {me_points:,}")
    print(f"  Temperatures: 8 (800°C - 1400°C)")
    print(f"  Time Points: 8 (0 - 3600s)")
    print(f"  Metrics: 4 (porosity, grain size, pore size, tortuosity)")
    print(f"  Images: 64 (8 temps × 8 times)")
    
    total_files += len(me_files)
    total_size += me_size
    total_data_points += me_points
    
    # Process Window
    print("\n⚙️ PROCESS WINDOW")
    print("-" * 30)
    pw_dir = f"{dataset_dir}/process_window"
    pw_files = os.listdir(pw_dir)
    pw_size = sum(get_file_size_mb(f"{pw_dir}/{f}") for f in pw_files)
    pw_points = sum(count_data_points(f"{pw_dir}/{f}") for f in pw_files if f.endswith('.csv'))
    
    print(f"  Files: {len(pw_files)}")
    print(f"  Size: {pw_size:.2f} MB")
    print(f"  Data Points: {pw_points:,}")
    print(f"  Process Combinations: 864")
    print(f"  Input Parameters: 4 (heating rate, temperature, time, atmosphere)")
    print(f"  Output Metrics: 8 (density, warpage, cracking, etc.)")
    print(f"  Success Rate: 86.01%")
    
    total_files += len(pw_files)
    total_size += pw_size
    total_data_points += pw_points
    
    # Visualizations
    print("\n📈 VISUALIZATIONS")
    print("-" * 30)
    viz_dir = f"{dataset_dir}/visualizations"
    if os.path.exists(viz_dir):
        viz_files = os.listdir(viz_dir)
        viz_size = sum(get_file_size_mb(f"{viz_dir}/{f}") for f in viz_files)
        print(f"  Files: {len(viz_files)}")
        print(f"  Size: {viz_size:.2f} MB")
        print(f"  Formats: PNG (high resolution)")
        print(f"  Coverage: All dataset components")
        
        total_files += len(viz_files)
        total_size += viz_size
    
    # Total Summary
    print("\n" + "="*80)
    print("📋 TOTAL DATASET SUMMARY")
    print("="*80)
    print(f"  Total Files: {total_files}")
    print(f"  Total Size: {total_size:.2f} MB")
    print(f"  Total Data Points: {total_data_points:,}")
    print(f"  Dataset Components: 4")
    print(f"  Materials: 4")
    print(f"  Process Conditions: 864")
    print(f"  Microstructural Images: 64")
    print(f"  Visualization Plots: 4")
    
    # Data Quality
    print("\n🔍 DATA QUALITY")
    print("-" * 30)
    
    # Load validation report
    validation_file = f"{dataset_dir}/validation_report.json"
    if os.path.exists(validation_file):
        with open(validation_file, 'r') as f:
            validation = json.load(f)
        
        print(f"  Overall Status: {validation['overall_status']}")
        print(f"  Datasets Validated: {validation['datasets_validated']}")
        print(f"  Total Issues: {validation['total_issues']}")
        
        for dataset, results in validation['summary'].items():
            status_icon = "✅" if results['status'] == 'PASS' else "⚠️"
            print(f"    {status_icon} {dataset.replace('_', ' ').title()}: {results['status']}")
    else:
        print("  Validation report not found")
    
    # File Structure
    print("\n📁 FILE STRUCTURE")
    print("-" * 30)
    print("  sofc_datasets/")
    print("  ├── dataset_metadata.json")
    print("  ├── validation_report.json")
    print("  ├── material_properties/")
    print("  │   ├── combined_material_properties.h5")
    print("  │   ├── material_summary.csv")
    print("  │   └── [4 material files]")
    print("  ├── sintering_kinetics/")
    print("  │   ├── combined_sintering_kinetics.h5")
    print("  │   └── [4 material files]")
    print("  ├── microstructural_evolution/")
    print("  │   ├── microstructural_evolution.h5")
    print("  │   └── microstructural_summary.csv")
    print("  ├── process_window/")
    print("  │   ├── process_window_data.csv")
    print("  │   ├── process_analysis.json")
    print("  │   └── process_summary_statistics.csv")
    print("  └── visualizations/")
    print("      └── [4 visualization files]")
    
    # Usage Examples
    print("\n💻 USAGE EXAMPLES")
    print("-" * 30)
    print("  # Load material properties")
    print("  import pandas as pd")
    print("  df = pd.read_csv('sofc_datasets/material_properties/NiO_YSZ_anode_properties.csv')")
    print()
    print("  # Load process window data")
    print("  df = pd.read_csv('sofc_datasets/process_window/process_window_data.csv')")
    print()
    print("  # Load HDF5 data")
    print("  import h5py")
    print("  with h5py.File('sofc_datasets/material_properties/combined_material_properties.h5', 'r') as f:")
    print("      data = f['NiO_YSZ_anode']['youngs_modulus_Pa'][:]")
    
    # Applications
    print("\n🎯 APPLICATIONS")
    print("-" * 30)
    print("  • FEM Model Calibration")
    print("  • Phase-Field Model Calibration")
    print("  • RL Agent Training")
    print("  • Process Optimization")
    print("  • Material Property Analysis")
    print("  • Sintering Behavior Studies")
    
    print("\n" + "="*80)
    print("✅ DATASET GENERATION COMPLETE!")
    print("="*80)
    print(f"All data saved to: {dataset_dir}")
    print("Ready for Phase 1 model calibration and RL agent training!")

if __name__ == "__main__":
    main()