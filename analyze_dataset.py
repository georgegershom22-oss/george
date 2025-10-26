#!/usr/bin/env python3
"""
Banking Security Dataset Analysis Script
Provides comprehensive analysis of the generated dataset including:
- Descriptive statistics
- Correlation analysis
- Intention-behavior gap analysis
- PBC moderation effects
- Data quality checks
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

def load_dataset():
    """Load the generated dataset"""
    return pd.read_csv('/workspace/banking_security_dataset.csv')

def descriptive_analysis(df):
    """Generate comprehensive descriptive statistics"""
    print("COMPREHENSIVE DESCRIPTIVE ANALYSIS")
    print("=" * 50)
    
    # Basic info
    print(f"Dataset Shape: {df.shape}")
    print(f"Missing Values: {df.isnull().sum().sum()}")
    print()
    
    # T1 Variables Summary
    print("T1 BASELINE VARIABLES")
    print("-" * 30)
    t1_vars = ['intention', 'pbc', 'attitude', 'subjective_norm']
    for var in t1_vars:
        print(f"{var}: M={df[var].mean():.2f}, SD={df[var].std():.2f}, Range=[{df[var].min()}, {df[var].max()}]")
    print()
    
    # T2 Self-Reported Behavior Summary
    print("T2 SELF-REPORTED BEHAVIOR (SRB)")
    print("-" * 40)
    srb_vars = ['SRB1_check_statements', 'SRB2_unique_passwords', 'SRB3_two_factor', 
                'SRB4_logout', 'SRB5_verify_alerts']
    for var in srb_vars:
        print(f"{var}: M={df[var].mean():.2f}, SD={df[var].std():.2f}, Range=[{df[var].min()}, {df[var].max()}]")
    print()
    
    # Objective Score Summary
    print("T2 OBJECTIVE BEHAVIORAL MEASURE")
    print("-" * 35)
    print(f"objective_score: M={df['objective_score'].mean():.2f}, SD={df['objective_score'].std():.2f}, Range=[{df['objective_score'].min()}, {df['objective_score'].max()}]")
    print()
    
    # Intention-Behavior Gap Summary
    print("INTENTION-BEHAVIOR GAP")
    print("-" * 25)
    print(f"intention_behavior_gap: M={df['intention_behavior_gap'].mean():.6f}, SD={df['intention_behavior_gap'].std():.2f}")
    print(f"Range=[{df['intention_behavior_gap'].min():.2f}, {df['intention_behavior_gap'].max():.2f}]")
    print()
    
    # Gap Categories
    gap_quartiles = np.percentile(df['intention_behavior_gap'], [25, 50, 75])
    print("Gap Categories (Quartiles):")
    print(f"Q1 (Underperformers): {gap_quartiles[0]:.2f}")
    print(f"Q2 (Median): {gap_quartiles[1]:.2f}")
    print(f"Q3 (Overperformers): {gap_quartiles[2]:.2f}")
    print()

def correlation_analysis(df):
    """Analyze correlations between key variables"""
    print("CORRELATION ANALYSIS")
    print("=" * 30)
    
    # Key variables for correlation
    key_vars = ['intention', 'pbc', 'attitude', 'subjective_norm', 
                'SRB1_check_statements', 'SRB2_unique_passwords', 'SRB3_two_factor',
                'SRB4_logout', 'SRB5_verify_alerts', 'objective_score', 'intention_behavior_gap']
    
    corr_matrix = df[key_vars].corr()
    
    print("Key Correlations:")
    print("-" * 20)
    
    # T1-T2 correlations
    print("T1 Intention → T2 Behaviors:")
    for srb in ['SRB1_check_statements', 'SRB2_unique_passwords', 'SRB3_two_factor', 
                'SRB4_logout', 'SRB5_verify_alerts']:
        corr = corr_matrix.loc['intention', srb]
        print(f"  {srb}: r = {corr:.3f}")
    
    print(f"  objective_score: r = {corr_matrix.loc['intention', 'objective_score']:.3f}")
    print()
    
    # PBC correlations
    print("PBC → T2 Behaviors:")
    for srb in ['SRB1_check_statements', 'SRB2_unique_passwords', 'SRB3_two_factor', 
                'SRB4_logout', 'SRB5_verify_alerts']:
        corr = corr_matrix.loc['pbc', srb]
        print(f"  {srb}: r = {corr:.3f}")
    
    print(f"  objective_score: r = {corr_matrix.loc['pbc', 'objective_score']:.3f}")
    print()
    
    # Intention-Behavior Gap correlations
    print("Intention-Behavior Gap Correlations:")
    print(f"  PBC: r = {corr_matrix.loc['pbc', 'intention_behavior_gap']:.3f}")
    print(f"  Attitude: r = {corr_matrix.loc['attitude', 'intention_behavior_gap']:.3f}")
    print(f"  Subjective Norm: r = {corr_matrix.loc['subjective_norm', 'intention_behavior_gap']:.3f}")
    print()

def intention_behavior_gap_analysis(df):
    """Detailed analysis of the intention-behavior gap"""
    print("INTENTION-BEHAVIOR GAP ANALYSIS")
    print("=" * 40)
    
    # Create behavior composite
    srb_vars = ['SRB1_check_statements', 'SRB2_unique_passwords', 'SRB3_two_factor', 
                'SRB4_logout', 'SRB5_verify_alerts']
    df['behavior_composite'] = df[srb_vars].mean(axis=1)
    
    # Gap statistics
    gap = df['intention_behavior_gap']
    print(f"Gap Mean: {gap.mean():.6f} (should be ~0 due to regression residuals)")
    print(f"Gap Standard Deviation: {gap.std():.3f}")
    print(f"Gap Range: [{gap.min():.3f}, {gap.max():.3f}]")
    print()
    
    # Categorize participants
    gap_quartiles = np.percentile(gap, [25, 50, 75])
    df['gap_category'] = pd.cut(gap, 
                               bins=[-np.inf, gap_quartiles[0], gap_quartiles[1], gap_quartiles[2], np.inf],
                               labels=['Underperformer', 'Slight Underperformer', 'Slight Overperformer', 'Overperformer'])
    
    print("Gap Categories Distribution:")
    print(df['gap_category'].value_counts().sort_index())
    print()
    
    # Analyze predictors of gap
    print("Predictors of Intention-Behavior Gap:")
    print("-" * 40)
    
    predictors = ['pbc', 'attitude', 'subjective_norm', 'age', 'education', 'tech_comfort', 
                  'previous_incident', 'perceived_threat', 'social_influence']
    
    for pred in predictors:
        if pred in df.columns:
            corr = df[pred].corr(gap)
            print(f"{pred}: r = {corr:.3f}")
    print()

def pbc_moderation_analysis(df):
    """Analyze PBC as a moderator of intention-behavior relationship"""
    print("PBC MODERATION ANALYSIS")
    print("=" * 30)
    
    # Create behavior composite
    srb_vars = ['SRB1_check_statements', 'SRB2_unique_passwords', 'SRB3_two_factor', 
                'SRB4_logout', 'SRB5_verify_alerts']
    df['behavior_composite'] = df[srb_vars].mean(axis=1)
    
    # Split by PBC levels
    pbc_median = df['pbc'].median()
    df['pbc_level'] = df['pbc'].apply(lambda x: 'High PBC' if x >= pbc_median else 'Low PBC')
    
    print("Intention-Behavior Correlation by PBC Level:")
    print("-" * 45)
    
    for level in ['Low PBC', 'High PBC']:
        subset = df[df['pbc_level'] == level]
        corr = subset['intention'].corr(subset['behavior_composite'])
        n = len(subset)
        print(f"{level} (n={n}): r = {corr:.3f}")
    
    print()
    
    # Test moderation effect
    from sklearn.linear_model import LinearRegression
    
    # Prepare data
    X = df[['intention', 'pbc']].copy()
    X['intention_pbc_interaction'] = X['intention'] * X['pbc']
    y = df['behavior_composite']
    
    # Fit model
    model = LinearRegression()
    model.fit(X, y)
    
    print("Moderation Model Results:")
    print("-" * 25)
    print(f"Intention coefficient: {model.coef_[0]:.3f}")
    print(f"PBC coefficient: {model.coef_[1]:.3f}")
    print(f"Intention × PBC interaction: {model.coef_[2]:.3f}")
    print(f"R²: {model.score(X, y):.3f}")
    print()

def data_quality_checks(df):
    """Perform data quality checks"""
    print("DATA QUALITY CHECKS")
    print("=" * 25)
    
    # Missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print("Missing Values Found:")
        for col, count in missing[missing > 0].items():
            print(f"  {col}: {count} ({count/len(df)*100:.1f}%)")
    else:
        print("✓ No missing values")
    print()
    
    # Outliers in key variables
    print("Outlier Detection (Z-scores > 3):")
    key_vars = ['intention', 'pbc', 'attitude', 'subjective_norm', 'objective_score']
    
    for var in key_vars:
        z_scores = np.abs(stats.zscore(df[var]))
        outliers = (z_scores > 3).sum()
        print(f"  {var}: {outliers} outliers ({outliers/len(df)*100:.1f}%)")
    print()
    
    # Range checks
    print("Range Validation:")
    print("-" * 20)
    
    # T1 variables should be 1-7
    t1_vars = ['intention', 'pbc', 'attitude', 'subjective_norm']
    for var in t1_vars:
        min_val, max_val = df[var].min(), df[var].max()
        if min_val >= 1 and max_val <= 7:
            print(f"✓ {var}: Range [{min_val}, {max_val}] - Valid")
        else:
            print(f"✗ {var}: Range [{min_val}, {max_val}] - Invalid")
    
    # SRB variables should be 1-7
    srb_vars = ['SRB1_check_statements', 'SRB2_unique_passwords', 'SRB3_two_factor', 
                'SRB4_logout', 'SRB5_verify_alerts']
    for var in srb_vars:
        min_val, max_val = df[var].min(), df[var].max()
        if min_val >= 1 and max_val <= 7:
            print(f"✓ {var}: Range [{min_val}, {max_val}] - Valid")
        else:
            print(f"✗ {var}: Range [{min_val}, {max_val}] - Invalid")
    
    # Objective score should be 0-10
    min_val, max_val = df['objective_score'].min(), df['objective_score'].max()
    if min_val >= 0 and max_val <= 10:
        print(f"✓ objective_score: Range [{min_val}, {max_val}] - Valid")
    else:
        print(f"✗ objective_score: Range [{min_val}, {max_val}] - Invalid")
    print()

def generate_summary_report(df):
    """Generate a comprehensive summary report"""
    print("DATASET SUMMARY REPORT")
    print("=" * 30)
    print()
    
    # Sample characteristics
    print("Sample Characteristics:")
    print(f"  Total participants: {len(df)}")
    print(f"  Age range: {df['age'].min()}-{df['age'].max()} years")
    print(f"  Gender distribution: {df['gender'].value_counts().to_dict()}")
    print(f"  Education levels: {df['education'].value_counts().sort_index().to_dict()}")
    print(f"  Previous security incidents: {df['previous_incident'].sum()} ({df['previous_incident'].mean()*100:.1f}%)")
    print()
    
    # Key findings
    print("Key Findings:")
    print("-" * 15)
    
    # Intention-behavior gap
    gap_std = df['intention_behavior_gap'].std()
    print(f"• Intention-behavior gap standard deviation: {gap_std:.3f}")
    print(f"  (Larger values indicate more variability in gap)")
    
    # PBC effect
    pbc_corr = df['pbc'].corr(df['intention_behavior_gap'])
    print(f"• PBC correlation with gap: {pbc_corr:.3f}")
    print(f"  (Negative values suggest higher PBC reduces gap)")
    
    # Objective vs self-reported
    srb_composite = df[['SRB1_check_statements', 'SRB2_unique_passwords', 'SRB3_two_factor', 
                        'SRB4_logout', 'SRB5_verify_alerts']].mean(axis=1)
    obj_srb_corr = df['objective_score'].corr(srb_composite)
    print(f"• Objective-Self-reported correlation: {obj_srb_corr:.3f}")
    print(f"  (Moderate correlation suggests convergent validity)")
    print()

def main():
    """Run comprehensive dataset analysis"""
    print("BANKING SECURITY DATASET ANALYSIS")
    print("=" * 50)
    print()
    
    # Load dataset
    df = load_dataset()
    
    # Run analyses
    descriptive_analysis(df)
    correlation_analysis(df)
    intention_behavior_gap_analysis(df)
    pbc_moderation_analysis(df)
    data_quality_checks(df)
    generate_summary_report(df)
    
    print("Analysis complete! Dataset is ready for research use.")
    print(f"Dataset saved at: /workspace/banking_security_dataset.csv")

if __name__ == "__main__":
    main()