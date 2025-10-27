"""
Data Analysis Script for Welding Parameters Dataset

This script performs comprehensive exploratory data analysis on the generated dataset.
Run this to understand the dataset characteristics and verify data quality.
"""

import pandas as pd
import numpy as np
import json
import glob
import os


def load_latest_dataset():
    """Load the most recently generated dataset"""
    csv_files = glob.glob('welding_dataset/welding_dataset_*.csv')
    if not csv_files:
        raise FileNotFoundError("No dataset found! Please run generate_welding_dataset.py first.")
    
    latest_file = max(csv_files, key=os.path.getctime)
    print(f"Loading dataset: {latest_file}")
    return pd.read_csv(latest_file)


def analyze_basic_stats(df):
    """Display basic dataset statistics"""
    print("\n" + "="*80)
    print("BASIC DATASET STATISTICS")
    print("="*80)
    
    print(f"\nDataset Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"\nMissing Values: {df.isnull().sum().sum()}")
    
    print("\n" + "-"*80)
    print("Data Types Distribution:")
    print(df.dtypes.value_counts())


def analyze_categorical_features(df):
    """Analyze categorical feature distributions"""
    print("\n" + "="*80)
    print("CATEGORICAL FEATURES ANALYSIS")
    print("="*80)
    
    categorical_cols = ['Anode_Material', 'Cathode_Material', 'Surface_Finish', 
                       'Welding_Technique', 'Chamber_Atmosphere', 'Electrode_Material']
    
    for col in categorical_cols:
        if col in df.columns:
            print(f"\n{col}:")
            print("-" * 60)
            value_counts = df[col].value_counts()
            for val, count in value_counts.items():
                pct = (count / len(df)) * 100
                bar = '█' * int(pct / 2)
                print(f"  {val:20s}: {count:4d} ({pct:5.1f}%) {bar}")


def analyze_material_combinations(df):
    """Analyze material pairing combinations"""
    print("\n" + "="*80)
    print("MATERIAL COMBINATION ANALYSIS")
    print("="*80)
    
    if 'Anode_Material' in df.columns and 'Cathode_Material' in df.columns:
        combinations = df.groupby(['Anode_Material', 'Cathode_Material']).size()
        combinations = combinations.sort_values(ascending=False)
        
        print("\nTop 10 Material Combinations:")
        print("-" * 60)
        for (anode, cathode), count in combinations.head(10).items():
            pct = (count / len(df)) * 100
            print(f"  {anode}-{cathode:10s}: {count:4d} samples ({pct:5.1f}%)")


def analyze_performance_metrics(df):
    """Analyze key performance metrics"""
    print("\n" + "="*80)
    print("PERFORMANCE METRICS ANALYSIS")
    print("="*80)
    
    performance_metrics = [
        'Thermal_Cycles_to_Failure',
        'Retained_Strength_%',
        'Resistance_Increase_%',
        'Overall_Performance_Score'
    ]
    
    for metric in performance_metrics:
        if metric in df.columns:
            print(f"\n{metric}:")
            print("-" * 60)
            
            data = df[metric]
            print(f"  Mean:        {data.mean():.2f}")
            print(f"  Median:      {data.median():.2f}")
            print(f"  Std Dev:     {data.std():.2f}")
            print(f"  Min:         {data.min():.2f}")
            print(f"  25th %ile:   {data.quantile(0.25):.2f}")
            print(f"  75th %ile:   {data.quantile(0.75):.2f}")
            print(f"  Max:         {data.max():.2f}")
            print(f"  IQR:         {data.quantile(0.75) - data.quantile(0.25):.2f}")


def analyze_quality_thresholds(df):
    """Analyze quality and performance thresholds"""
    print("\n" + "="*80)
    print("QUALITY THRESHOLD ANALYSIS")
    print("="*80)
    
    if 'Pass_Quality_Threshold' in df.columns:
        pass_quality = df['Pass_Quality_Threshold'].sum()
        pct = (pass_quality / len(df)) * 100
        print(f"\nPass Quality Threshold:      {pass_quality:4d} / {len(df)} ({pct:.1f}%)")
    
    if 'Pass_Performance_Threshold' in df.columns:
        pass_perf = df['Pass_Performance_Threshold'].sum()
        pct = (pass_perf / len(df)) * 100
        print(f"Pass Performance Threshold:  {pass_perf:4d} / {len(df)} ({pct:.1f}%)")
    
    if 'Optimal_Design' in df.columns:
        optimal = df['Optimal_Design'].sum()
        pct = (optimal / len(df)) * 100
        print(f"Optimal Designs (Both):      {optimal:4d} / {len(df)} ({pct:.1f}%)")
        
        print("\n" + "-"*60)
        print("Quality Gates Breakdown:")
        quality_breakdown = df.groupby(['Pass_Quality_Threshold', 
                                       'Pass_Performance_Threshold']).size()
        
        labels = {
            (0, 0): "Failed Both",
            (1, 0): "Quality OK, Performance Failed",
            (0, 1): "Performance OK, Quality Failed",
            (1, 1): "Passed Both (Optimal)"
        }
        
        for key, count in quality_breakdown.items():
            pct = (count / len(df)) * 100
            label = labels.get(key, str(key))
            print(f"  {label:35s}: {count:4d} ({pct:5.1f}%)")


def analyze_technique_performance(df):
    """Analyze performance by welding technique"""
    print("\n" + "="*80)
    print("PERFORMANCE BY WELDING TECHNIQUE")
    print("="*80)
    
    if 'Welding_Technique' in df.columns and 'Thermal_Cycles_to_Failure' in df.columns:
        print("\nMean Thermal Cycles to Failure by Technique:")
        print("-" * 60)
        
        technique_perf = df.groupby('Welding_Technique').agg({
            'Thermal_Cycles_to_Failure': ['mean', 'std', 'count'],
            'Overall_Performance_Score': 'mean',
            'Optimal_Design': 'sum'
        }).round(2)
        
        for technique in technique_perf.index:
            mean_cycles = technique_perf.loc[technique, ('Thermal_Cycles_to_Failure', 'mean')]
            std_cycles = technique_perf.loc[technique, ('Thermal_Cycles_to_Failure', 'std')]
            count = technique_perf.loc[technique, ('Thermal_Cycles_to_Failure', 'count')]
            perf_score = technique_perf.loc[technique, ('Overall_Performance_Score', 'mean')]
            optimal = technique_perf.loc[technique, ('Optimal_Design', 'sum')]
            
            print(f"\n  {technique}:")
            print(f"    Samples:              {count:.0f}")
            print(f"    Mean Cycles:          {mean_cycles:.0f} ± {std_cycles:.0f}")
            print(f"    Performance Score:    {perf_score:.1f}")
            print(f"    Optimal Designs:      {optimal:.0f} ({optimal/count*100:.1f}%)")


def analyze_correlations(df):
    """Analyze correlations with target variable"""
    print("\n" + "="*80)
    print("CORRELATION ANALYSIS")
    print("="*80)
    
    target = 'Thermal_Cycles_to_Failure'
    if target not in df.columns:
        print("Target variable not found!")
        return
    
    # Select only numeric columns
    numeric_df = df.select_dtypes(include=[np.number])
    
    # Calculate correlations with target
    correlations = numeric_df.corr()[target].sort_values(ascending=False)
    
    print(f"\nTop 15 Features Correlated with {target}:")
    print("-" * 60)
    
    for i, (feature, corr) in enumerate(correlations.head(15).items(), 1):
        if feature != target:
            bar = '█' * int(abs(corr) * 20)
            sign = '+' if corr > 0 else '-'
            print(f"{i:2d}. {feature:40s}: {sign}{abs(corr):.3f} {bar}")
    
    print(f"\nBottom 10 Features (Most Negative Correlation):")
    print("-" * 60)
    
    for i, (feature, corr) in enumerate(correlations.tail(10).items(), 1):
        if feature != target:
            bar = '█' * int(abs(corr) * 20)
            print(f"{i:2d}. {feature:40s}: {corr:+.3f} {bar}")


def analyze_input_output_relationship(df):
    """Analyze relationship between input parameters and performance"""
    print("\n" + "="*80)
    print("INPUT-OUTPUT RELATIONSHIP ANALYSIS")
    print("="*80)
    
    # Key input parameters
    input_params = ['Power_W', 'Amplitude_um', 'Force_N', 'Time_ms', 
                   'Preheat_Temperature_C', 'Cooling_Rate_C_per_s']
    
    # Key output metrics
    output_metrics = ['Weld_Strength_MPa', 'Joint_Resistance_mOhm', 
                     'Thermal_Cycles_to_Failure', 'Overall_Performance_Score']
    
    print("\nCorrelation Matrix (Inputs vs Key Outputs):")
    print("-" * 80)
    
    available_inputs = [col for col in input_params if col in df.columns]
    available_outputs = [col for col in output_metrics if col in df.columns]
    
    if available_inputs and available_outputs:
        corr_matrix = df[available_inputs + available_outputs].corr()
        
        # Print header
        print(f"{'Input Parameter':30s}", end='')
        for output in available_outputs:
            print(f"{output[:20]:>22s}", end='')
        print()
        print("-" * 110)
        
        # Print correlations
        for input_param in available_inputs:
            print(f"{input_param:30s}", end='')
            for output in available_outputs:
                corr = corr_matrix.loc[input_param, output]
                print(f"{corr:22.3f}", end='')
            print()


def generate_insights(df):
    """Generate actionable insights from the dataset"""
    print("\n" + "="*80)
    print("KEY INSIGHTS & RECOMMENDATIONS")
    print("="*80)
    
    insights = []
    
    # Optimal design rate
    if 'Optimal_Design' in df.columns:
        optimal_rate = df['Optimal_Design'].mean() * 100
        if optimal_rate < 30:
            insights.append(f"• Low optimal design rate ({optimal_rate:.1f}%) indicates challenging design space")
        elif optimal_rate > 50:
            insights.append(f"• High optimal design rate ({optimal_rate:.1f}%) suggests many good solutions exist")
    
    # Thermal cycling performance
    if 'Thermal_Cycles_to_Failure' in df.columns:
        mean_cycles = df['Thermal_Cycles_to_Failure'].mean()
        median_cycles = df['Thermal_Cycles_to_Failure'].median()
        if mean_cycles < 3000:
            insights.append(f"• Average thermal cycling performance is below 3000 cycles target")
        if median_cycles > mean_cycles:
            insights.append(f"• Performance distribution is left-skewed (many low performers)")
    
    # Best welding technique
    if 'Welding_Technique' in df.columns and 'Overall_Performance_Score' in df.columns:
        best_technique = df.groupby('Welding_Technique')['Overall_Performance_Score'].mean().idxmax()
        best_score = df.groupby('Welding_Technique')['Overall_Performance_Score'].mean().max()
        insights.append(f"• Best performing technique: {best_technique} (avg score: {best_score:.1f})")
    
    # Material combination
    if 'Anode_Material' in df.columns and 'Cathode_Material' in df.columns:
        best_combo = df.groupby(['Anode_Material', 'Cathode_Material'])['Thermal_Cycles_to_Failure'].mean().idxmax()
        insights.append(f"• Best material combination: {best_combo[0]}-{best_combo[1]}")
    
    # Critical quality metrics
    if 'Porosity_%' in df.columns and 'Thermal_Cycles_to_Failure' in df.columns:
        low_porosity = df[df['Porosity_%'] < 3]['Thermal_Cycles_to_Failure'].mean()
        high_porosity = df[df['Porosity_%'] > 10]['Thermal_Cycles_to_Failure'].mean()
        improvement = ((low_porosity - high_porosity) / high_porosity) * 100
        insights.append(f"• Low porosity (<3%) improves thermal cycling by {improvement:.0f}%")
    
    print("\n")
    for insight in insights:
        print(insight)
    
    print("\n\nRecommendations for ML Model:")
    print("-" * 60)
    print("1. Use gradient boosting models (XGBoost/LightGBM) as baseline")
    print("2. Create material mismatch features (thermal expansion, conductivity)")
    print("3. Engineer technique-specific feature subsets")
    print("4. Apply target encoding for categorical variables")
    print("5. Use cross-validation with stratification by welding technique")
    print("6. Consider multi-objective optimization for inverse design")
    print("7. Focus on Porosity_%, Residual_Stress, and Interfacial_Bonding_%")
    print("8. Validate model predictions with physical constraints")


def main():
    """Main analysis function"""
    print("\n" + "="*80)
    print("WELDING PARAMETERS DATASET - EXPLORATORY DATA ANALYSIS")
    print("="*80)
    
    try:
        # Load dataset
        df = load_latest_dataset()
        
        # Run analyses
        analyze_basic_stats(df)
        analyze_categorical_features(df)
        analyze_material_combinations(df)
        analyze_performance_metrics(df)
        analyze_quality_thresholds(df)
        analyze_technique_performance(df)
        analyze_correlations(df)
        analyze_input_output_relationship(df)
        generate_insights(df)
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE!")
        print("="*80)
        print("\nNext Steps:")
        print("1. Review the insights above")
        print("2. Start with example_ml_training.py for ML model development")
        print("3. Check README.md for detailed documentation")
        print("\n")
        
    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
