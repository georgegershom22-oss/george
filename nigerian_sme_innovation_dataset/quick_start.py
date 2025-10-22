#!/usr/bin/env python3
"""
Quick Start Guide for Nigerian SME Innovation Dataset
=====================================================
Run this script to get started with the dataset immediately.
"""

import pandas as pd
import numpy as np
import os

def quick_start():
    print("="*70)
    print("NIGERIAN SME INNOVATION DATASET - QUICK START")
    print("="*70)
    
    # Check if dataset exists
    data_path = 'data/nigerian_sme_innovation_data.csv'
    if not os.path.exists(data_path):
        print("\n❌ Dataset not found! Please run the generation script first:")
        print("   python3 scripts/generate_sme_dataset.py")
        return
    
    # Load the dataset
    print("\n📊 Loading dataset...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df):,} SME records with {len(df.columns)} variables")
    
    # Quick statistics
    print("\n📈 Quick Statistics:")
    print("-"*40)
    print(f"Average Innovation Score: {df['innovation_overall_score'].mean():.2f}/5.0")
    print(f"Average Constraint Score: {df['constraint_overall_score'].mean():.2f}/5.0")
    print(f"Average Performance Score: {df['performance_subjective_score'].mean():.2f}/5.0")
    print(f"Average Digital Literacy: {df['digital_literacy_score'].mean():.1f}/10.0")
    print(f"Average Firm Size: {df['num_employees'].mean():.0f} employees")
    print(f"Average Annual Turnover: ₦{df['annual_turnover_million_naira'].mean():.1f}M")
    
    # Top performing sectors
    print("\n🏆 Top Performing Sectors:")
    print("-"*40)
    sector_perf = df.groupby('industry_sector')['performance_subjective_score'].mean().sort_values(ascending=False)
    for sector, perf in sector_perf.head(5).items():
        print(f"  {sector}: {perf:.2f}/5.0")
    
    # Geographic insights
    print("\n🗺️ Geographic Distribution:")
    print("-"*40)
    zone_dist = df['geo_political_zone'].value_counts()
    for zone, count in zone_dist.head(6).items():
        print(f"  {zone}: {count:,} SMEs ({count/len(df)*100:.1f}%)")
    
    # Correlation insights
    print("\n🔗 Key Correlations with Performance:")
    print("-"*40)
    correlations = {
        'Innovation': df['innovation_overall_score'].corr(df['performance_subjective_score']),
        'Digital Literacy': df['digital_literacy_score'].corr(df['performance_subjective_score']),
        'Constraints': df['constraint_overall_score'].corr(df['performance_subjective_score']),
        'Firm Age': df['firm_age_years'].corr(df['performance_subjective_score'])
    }
    for var, corr in sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True):
        direction = "↑" if corr > 0 else "↓"
        print(f"  {var}: {corr:+.3f} {direction}")
    
    # Sample code snippets
    print("\n💻 Quick Code Examples:")
    print("-"*40)
    print("\n# Load the dataset:")
    print("import pandas as pd")
    print("df = pd.read_csv('data/nigerian_sme_innovation_data.csv')")
    
    print("\n# Filter high-performing SMEs:")
    print("high_performers = df[df['performance_subjective_score'] > 3.5]")
    
    print("\n# Analyze by industry:")
    print("industry_stats = df.groupby('industry_sector').agg({")
    print("    'innovation_overall_score': 'mean',")
    print("    'performance_subjective_score': 'mean',")
    print("    'num_employees': 'mean'")
    print("})")
    
    print("\n# Create innovation categories:")
    print("df['innovation_category'] = pd.cut(df['innovation_overall_score'],")
    print("    bins=[0, 2, 3, 5],")
    print("    labels=['Low', 'Medium', 'High'])")
    
    # Next steps
    print("\n🚀 Next Steps:")
    print("-"*40)
    print("1. Explore the Jupyter notebook: notebooks/ml_analysis_demo.ipynb")
    print("2. Read the data dictionary: documentation/data_dictionary.md")
    print("3. Run validation script: python3 scripts/validate_and_analyze.py")
    print("4. View visualizations: data/analysis_visualizations.png")
    
    print("\n" + "="*70)
    print("✓ Quick start complete! Happy analyzing! 🎉")
    print("="*70)
    
    return df

if __name__ == "__main__":
    df = quick_start()