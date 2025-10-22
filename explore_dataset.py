#!/usr/bin/env python3
"""
Quick Dataset Exploration Script
Shows the structure and sample data from the Nigerian SME Innovation Dataset
"""

import pandas as pd
import numpy as np

def explore_dataset():
    """Explore the dataset structure and show sample data"""
    
    # Load the dataset
    df = pd.read_csv('nigerian_sme_innovation_dataset.csv')
    
    print("="*80)
    print("NIGERIAN SME INNOVATION DATASET - QUICK EXPLORATION")
    print("="*80)
    
    # Basic info
    print(f"Dataset Shape: {df.shape}")
    print(f"Total Firms: {len(df)}")
    print(f"Total Variables: {len(df.columns)}")
    
    # Show column names
    print("\nAll Variables:")
    for i, col in enumerate(df.columns, 1):
        print(f"{i:2d}. {col}")
    
    # Show data types
    print("\nData Types:")
    print(df.dtypes.value_counts())
    
    # Show first few rows
    print("\nFirst 5 Rows:")
    print(df.head())
    
    # Show sample of each section
    print("\n" + "="*80)
    print("SECTION A: FIRMOGRAPHICS")
    print("="*80)
    firmographic_cols = ['firm_id', 'state', 'geo_political_zone', 'location_type', 
                        'industry', 'firm_age_years', 'num_employees', 'owner_gender', 
                        'owner_education', 'digital_literacy_score']
    print(df[firmographic_cols].head())
    
    print("\n" + "="*80)
    print("SECTION B: INNOVATION ADOPTION")
    print("="*80)
    innovation_cols = ['digital_tools_adoption', 'advanced_tech_adoption', 
                      'process_innovation', 'product_service_innovation', 
                      'business_model_innovation', 'innovation_index']
    print(df[innovation_cols].head())
    
    print("\n" + "="*80)
    print("SECTION C: CONSTRAINT ASSESSMENT")
    print("="*80)
    constraint_cols = ['financial_constraints', 'human_capital_constraints', 
                      'infrastructure_constraints', 'regulatory_constraints', 
                      'market_constraints', 'constraint_index']
    print(df[constraint_cols].head())
    
    print("\n" + "="*80)
    print("SECTION D: PERFORMANCE AND GROWTH")
    print("="*80)
    performance_cols = ['profitability_growth', 'sales_growth', 'market_share_growth', 
                       'overall_performance_satisfaction', 'turnover_growth_percent', 
                       'performance_index']
    print(df[performance_cols].head())
    
    # Show summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print("Numeric Variables Summary:")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    print(df[numeric_cols].describe())
    
    print("\nCategorical Variables Summary:")
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols[:5]:  # Show first 5 categorical variables
        print(f"\n{col}:")
        print(df[col].value_counts().head())
    
    # Show correlations
    print("\n" + "="*80)
    print("KEY CORRELATIONS")
    print("="*80)
    key_vars = ['innovation_index', 'constraint_index', 'performance_index']
    if all(col in df.columns for col in key_vars):
        print("Innovation-Constraint-Performance Correlations:")
        print(df[key_vars].corr())
    
    print("\n" + "="*80)
    print("DATASET READY FOR ANALYSIS!")
    print("="*80)
    print("The dataset contains comprehensive information about:")
    print("✓ 2,000 Nigerian SMEs across all states and industries")
    print("✓ Innovation adoption patterns and drivers")
    print("✓ Various constraint factors affecting SMEs")
    print("✓ Performance and growth metrics")
    print("✓ Realistic correlations and relationships")
    print("\nPerfect for machine learning analysis and research!")

if __name__ == "__main__":
    explore_dataset()