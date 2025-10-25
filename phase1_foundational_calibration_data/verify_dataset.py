#!/usr/bin/env python3
"""
Dataset Verification Script

Verifies the integrity and completeness of the Phase 1 dataset.

Usage:
    python verify_dataset.py
"""

import pandas as pd
from pathlib import Path
import sys

def verify_dataset():
    """Verify dataset integrity"""
    
    print("="*80)
    print("PHASE 1 DATASET VERIFICATION")
    print("="*80)
    
    base_path = Path(".")
    errors = []
    warnings = []
    
    # Expected files
    expected_files = {
        'material_properties/nio_ysz_anode_properties.csv': 19,
        'material_properties/ysz_electrolyte_properties.csv': 19,
        'material_properties/functional_layer_properties.csv': 38,
        'sintering_kinetics/nio_ysz_sintering_stress.csv': 56,
        'sintering_kinetics/master_sintering_curve_params.csv': 4,
        'sintering_kinetics/densification_rate_data.csv': 50,
        'microstructural_evolution/nio_ysz_microstructure_timeseries.csv': 56,
        'microstructural_evolution/ysz_microstructure_timeseries.csv': 40,
        'microstructural_evolution/pore_size_distribution_data.csv': 65,
        'process_window_data/sintering_profile_experiments.csv': 60,
        'process_window_data/warpage_measurement_data.csv': 54,
        'process_window_data/defect_characterization.csv': 60,
        'process_window_data/thermal_profile_measurements.csv': 153,
        'process_window_data/action_space_boundaries.csv': 22,
    }
    
    print("\n1. Checking file existence and row counts...")
    print("-" * 80)
    
    for file_path, expected_rows in expected_files.items():
        full_path = base_path / file_path
        
        if not full_path.exists():
            errors.append(f"✗ MISSING: {file_path}")
            print(f"✗ {file_path}: MISSING")
        else:
            try:
                df = pd.read_csv(full_path)
                actual_rows = len(df)
                
                if actual_rows == expected_rows:
                    print(f"✓ {file_path}: {actual_rows} rows")
                else:
                    warnings.append(f"Row count mismatch in {file_path}: expected {expected_rows}, got {actual_rows}")
                    print(f"⚠ {file_path}: {actual_rows} rows (expected {expected_rows})")
                    
            except Exception as e:
                errors.append(f"Error reading {file_path}: {str(e)}")
                print(f"✗ {file_path}: ERROR - {str(e)}")
    
    # Check documentation
    print("\n2. Checking documentation files...")
    print("-" * 80)
    
    doc_files = [
        'README.md',
        'DATA_DICTIONARY.md',
        'EXPERIMENTAL_METHODOLOGY.md',
        'DATASET_SUMMARY.txt',
        'dataset_loader.py',
    ]
    
    for doc_file in doc_files:
        if (base_path / doc_file).exists():
            print(f"✓ {doc_file}")
        else:
            warnings.append(f"Documentation file missing: {doc_file}")
            print(f"⚠ {doc_file}: MISSING")
    
    # Data integrity checks
    print("\n3. Data integrity checks...")
    print("-" * 80)
    
    # Check temperature ranges
    try:
        nio_props = pd.read_csv(base_path / 'material_properties/nio_ysz_anode_properties.csv')
        temp_min = nio_props['Temperature_C'].min()
        temp_max = nio_props['Temperature_C'].max()
        
        if temp_min == 25 and temp_max == 1600:
            print(f"✓ Temperature range: {temp_min}-{temp_max}°C")
        else:
            warnings.append(f"Unexpected temperature range: {temp_min}-{temp_max}°C")
            print(f"⚠ Temperature range: {temp_min}-{temp_max}°C (expected 25-1600)")
    except Exception as e:
        errors.append(f"Could not verify temperature range: {str(e)}")
    
    # Check process window completeness
    try:
        experiments = pd.read_csv(base_path / 'process_window_data/sintering_profile_experiments.csv')
        
        # Check for required columns
        required_cols = ['Heating_Rate_C_min', 'Peak_Temperature_C', 'Hold_Time_min', 
                        'Final_Density_percent', 'Final_Warpage_mm', 'Cracking']
        
        missing_cols = [col for col in required_cols if col not in experiments.columns]
        
        if not missing_cols:
            print(f"✓ Process window data complete: {len(experiments)} experiments")
        else:
            errors.append(f"Missing columns in experiments: {missing_cols}")
            print(f"✗ Process window missing columns: {missing_cols}")
            
        # Check value ranges
        if experiments['Final_Density_percent'].min() >= 60 and experiments['Final_Density_percent'].max() <= 100:
            print(f"✓ Density range: {experiments['Final_Density_percent'].min():.1f}-{experiments['Final_Density_percent'].max():.1f}%")
        else:
            warnings.append("Density values outside expected range")
            
    except Exception as e:
        errors.append(f"Could not verify process window data: {str(e)}")
    
    # Check microstructure data
    try:
        nio_micro = pd.read_csv(base_path / 'microstructural_evolution/nio_ysz_microstructure_timeseries.csv')
        
        # Check porosity decreases with time
        temps = nio_micro['Temperature_C'].unique()
        for temp in temps[:3]:  # Check first 3 temperatures
            temp_data = nio_micro[nio_micro['Temperature_C'] == temp].sort_values('Time_min')
            porosity_trend = temp_data['Porosity_percent'].diff().sum()
            
            if porosity_trend < 0:  # Should decrease (negative trend)
                continue
            else:
                warnings.append(f"Porosity not decreasing at {temp}°C")
        
        print(f"✓ Microstructure evolution data: {len(temps)} temperatures, {len(nio_micro['Time_min'].unique())} time points")
        
    except Exception as e:
        errors.append(f"Could not verify microstructure data: {str(e)}")
    
    # Summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    print(f"Total files checked: {len(expected_files) + len(doc_files)}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    
    if errors:
        print("\n⚠ ERRORS FOUND:")
        for error in errors:
            print(f"  • {error}")
    
    if warnings:
        print("\n⚠ WARNINGS:")
        for warning in warnings:
            print(f"  • {warning}")
    
    if not errors and not warnings:
        print("\n✓ ALL CHECKS PASSED - DATASET IS COMPLETE AND VALID")
        print("="*80)
        return 0
    elif errors:
        print("\n✗ DATASET HAS ERRORS - PLEASE REVIEW")
        print("="*80)
        return 1
    else:
        print("\n✓ DATASET IS VALID (with minor warnings)")
        print("="*80)
        return 0

if __name__ == '__main__':
    sys.exit(verify_dataset())
