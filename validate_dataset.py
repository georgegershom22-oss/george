#!/usr/bin/env python3
"""
Dataset Validation Script
Validates the integrity and completeness of the Nigerian SME Innovation dataset
"""

import pandas as pd
import sys
from pathlib import Path

def validate_file(filename, expected_rows=None, expected_cols=None):
    """Validate a single CSV file"""
    try:
        df = pd.read_csv(filename)
        
        # Check for missing values
        missing = df.isnull().sum().sum()
        
        # Check expected dimensions
        rows, cols = df.shape
        
        status = "✓ PASS"
        issues = []
        
        if expected_rows and rows != expected_rows:
            issues.append(f"Expected {expected_rows} rows, got {rows}")
            status = "✗ FAIL"
        
        if expected_cols and cols != expected_cols:
            issues.append(f"Expected {expected_cols} cols, got {cols}")
            status = "✗ FAIL"
        
        if missing > 0:
            issues.append(f"{missing} missing values")
            status = "⚠ WARN"
        
        return {
            'file': filename,
            'status': status,
            'rows': rows,
            'cols': cols,
            'missing': missing,
            'issues': issues
        }
    except Exception as e:
        return {
            'file': filename,
            'status': "✗ ERROR",
            'rows': 0,
            'cols': 0,
            'missing': 0,
            'issues': [str(e)]
        }

def main():
    print("="*80)
    print("NIGERIAN SME INNOVATION DATASET - VALIDATION REPORT")
    print("="*80)
    
    # Define expected file structures
    files = [
        ('macroeconomic_indicators.csv', 10, 11),
        ('broadband_penetration_by_state.csv', 100, 9),
        ('sectoral_growth_rates.csv', 10, 20),
        ('technology_adoption_indices.csv', 10, 16),
        ('sme_landscape_indicators.csv', 10, 21),
        ('innovation_adoption_barriers.csv', 60, 17),
        ('regional_summary_statistics.csv', 60, 17),
        ('policy_and_external_factors.csv', 10, 21),
    ]
    
    results = []
    total_rows = 0
    total_cols_unique = set()
    all_passed = True
    
    print("\nVALIDATING CSV FILES:")
    print("-" * 80)
    
    for filename, exp_rows, exp_cols in files:
        result = validate_file(filename, exp_rows, exp_cols)
        results.append(result)
        
        status_symbol = result['status']
        print(f"{status_symbol} {filename:45s} [{result['rows']:3d} × {result['cols']:2d}]")
        
        if result['issues']:
            for issue in result['issues']:
                print(f"    └─ {issue}")
        
        if result['status'] != "✓ PASS":
            all_passed = False
        
        total_rows += result['rows']
        
        # Count unique columns (rough estimate)
        if result['rows'] > 0:
            try:
                df = pd.read_csv(filename)
                total_cols_unique.update(df.columns)
            except:
                pass
    
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(f"Total CSV files:        {len(files)}")
    print(f"Total rows:             {total_rows}")
    print(f"Total unique columns:   {len(total_cols_unique)}")
    print(f"Validation status:      {'✓ ALL PASSED' if all_passed else '✗ SOME FAILED'}")
    
    # Check for documentation files
    print("\n" + "="*80)
    print("DOCUMENTATION FILES")
    print("="*80)
    
    doc_files = [
        'DATA_DICTIONARY.md',
        'README.md',
        'DATASET_SUMMARY.txt',
        'dataset_structure.txt',
        'analysis_starter.py',
        'requirements.txt'
    ]
    
    for doc_file in doc_files:
        if Path(doc_file).exists():
            size = Path(doc_file).stat().st_size / 1024
            print(f"✓ {doc_file:35s} ({size:.1f} KB)")
        else:
            print(f"✗ {doc_file:35s} (MISSING)")
            all_passed = False
    
    # Test basic data loading
    print("\n" + "="*80)
    print("DATA LOADING TEST")
    print("="*80)
    
    try:
        macro = pd.read_csv('macroeconomic_indicators.csv')
        tech = pd.read_csv('technology_adoption_indices.csv')
        
        # Check year ranges
        print(f"✓ Macroeconomic data: {macro['Year'].min()} - {macro['Year'].max()}")
        print(f"✓ Technology data: {tech['Year'].min()} - {tech['Year'].max()}")
        
        # Check sample values
        print(f"✓ 2024 GDP Growth: {macro[macro['Year']==2024]['GDP_Growth_Rate_Percent'].values[0]:.2f}%")
        print(f"✓ 2024 FinTech Adoption: {tech[tech['Year']==2024]['FinTech_Adoption_Rate_Percent'].values[0]:.1f}%")
        
    except Exception as e:
        print(f"✗ Data loading failed: {e}")
        all_passed = False
    
    # Test merge capability
    print("\n" + "="*80)
    print("MERGE CAPABILITY TEST")
    print("="*80)
    
    try:
        regional = pd.read_csv('regional_summary_statistics.csv')
        barriers = pd.read_csv('innovation_adoption_barriers.csv')
        policy = pd.read_csv('policy_and_external_factors.csv')
        
        # Test regional merge
        merged_regional = regional.merge(barriers, on=['Year', 'Region'])
        print(f"✓ Regional + Barriers merge: {merged_regional.shape}")
        
        # Test national context addition
        merged_full = merged_regional.merge(policy, on='Year')
        print(f"✓ + Policy data merge: {merged_full.shape}")
        print(f"✓ Final dataset has {merged_full.shape[1]} variables")
        
    except Exception as e:
        print(f"✗ Merge test failed: {e}")
        all_passed = False
    
    # Final verdict
    print("\n" + "="*80)
    if all_passed:
        print("✓ ✓ ✓  DATASET VALIDATION PASSED  ✓ ✓ ✓")
        print("="*80)
        print("\nDataset is ready for analysis!")
        print("Run: python analysis_starter.py")
        return 0
    else:
        print("✗ ✗ ✗  DATASET VALIDATION FAILED  ✗ ✗ ✗")
        print("="*80)
        print("\nPlease check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
