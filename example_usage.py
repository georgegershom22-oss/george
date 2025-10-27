#!/usr/bin/env python3
"""
Example Usage of Welding Parameter Dataset for ML-Driven Inverse Design

This script demonstrates various ways to use the welding parameter dataset
for research, industrial applications, and educational purposes.

Author: AI Assistant
Date: 2025-10-27
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

def example_1_basic_data_exploration():
    """Example 1: Basic dataset exploration and statistics"""
    print("=== Example 1: Basic Data Exploration ===")
    
    # Load the dataset
    df = pd.read_csv('welding_complete_dataset.csv')
    
    print(f"Dataset shape: {df.shape}")
    print(f"Number of welding techniques: {len(df['welding_technique'].unique())}")
    print(f"Welding techniques: {list(df['welding_technique'].unique())}")
    
    # Basic statistics
    print("\nBasic statistics for key performance metrics:")
    performance_cols = ['thermal_fatigue_life_cycles', 'long_term_reliability_score', 
                       'resistance_drift_percent', 'weld_strength_MPa']
    print(df[performance_cols].describe())
    
    # Correlation analysis
    print("\nTop correlations with reliability score:")
    correlations = df.select_dtypes(include=[np.number]).corr()['long_term_reliability_score']
    print(correlations.abs().sort_values(ascending=False).head(10))
    
    return df

def example_2_technique_comparison():
    """Example 2: Compare welding techniques performance"""
    print("\n=== Example 2: Welding Technique Comparison ===")
    
    df = pd.read_csv('welding_complete_dataset.csv')
    
    # Performance by technique
    technique_performance = df.groupby('welding_technique').agg({
        'long_term_reliability_score': ['mean', 'std', 'count'],
        'thermal_fatigue_life_cycles': ['mean', 'std'],
        'weld_strength_MPa': ['mean', 'std'],
        'resistance_drift_percent': ['mean', 'std']
    }).round(2)
    
    print("Performance by welding technique:")
    print(technique_performance)
    
    # Find best technique for each metric
    best_techniques = {}
    metrics = ['long_term_reliability_score', 'thermal_fatigue_life_cycles', 'weld_strength_MPa']
    
    for metric in metrics:
        best_technique = df.groupby('welding_technique')[metric].mean().idxmax()
        best_value = df.groupby('welding_technique')[metric].mean().max()
        best_techniques[metric] = (best_technique, best_value)
        print(f"\nBest technique for {metric}: {best_technique} ({best_value:.2f})")
    
    return technique_performance

def example_3_material_optimization():
    """Example 3: Material combination optimization"""
    print("\n=== Example 3: Material Combination Optimization ===")
    
    df = pd.read_csv('welding_complete_dataset.csv')
    
    # Create material combination column
    df['material_combo'] = df['anode_material'] + ' - ' + df['cathode_material']
    
    # Find best material combinations
    material_performance = df.groupby('material_combo').agg({
        'long_term_reliability_score': 'mean',
        'thermal_fatigue_life_cycles': 'mean',
        'electrical_resistance_uOhm': 'mean',
        'weld_strength_MPa': 'mean'
    }).round(2)
    
    # Sort by reliability score
    material_performance = material_performance.sort_values('long_term_reliability_score', ascending=False)
    
    print("Top 10 material combinations by reliability:")
    print(material_performance.head(10))
    
    # Effect of surface coating
    coating_effect = df.groupby('surface_coating')['long_term_reliability_score'].mean().sort_values(ascending=False)
    print("\nSurface coating effect on reliability:")
    print(coating_effect)
    
    return material_performance

def example_4_predictive_modeling():
    """Example 4: Build predictive models for performance metrics"""
    print("\n=== Example 4: Predictive Modeling ===")
    
    df = pd.read_csv('welding_complete_dataset.csv')
    
    # Prepare features
    categorical_cols = ['anode_material', 'cathode_material', 'surface_coating', 'welding_technique']
    
    # Encode categorical variables
    for col in categorical_cols:
        le = LabelEncoder()
        df[f'{col}_encoded'] = le.fit_transform(df[col])
    
    # Select features and target
    feature_cols = [col for col in df.columns if col.endswith('_encoded')] + [
        'tab_thickness_um', 'power_W', 'amplitude_um', 'force_N', 'time_s',
        'speed_mm_s', 'pulse_frequency_Hz', 'preheat_temp_C'
    ]
    
    X = df[feature_cols].fillna(0)
    y = df['long_term_reliability_score']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Evaluate model
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Model Performance:")
    print(f"  R² Score: {r2:.3f}")
    print(f"  RMSE: {np.sqrt(mse):.3f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 most important features:")
    print(feature_importance.head(10))
    
    return model, feature_importance

def example_5_parameter_optimization():
    """Example 5: Simple parameter optimization for target performance"""
    print("\n=== Example 5: Parameter Optimization ===")
    
    df = pd.read_csv('welding_complete_dataset.csv')
    
    # Define target performance
    target_reliability = 85
    target_fatigue_life = 100000
    
    # Filter data based on targets
    high_performance = df[
        (df['long_term_reliability_score'] >= target_reliability) &
        (df['thermal_fatigue_life_cycles'] >= target_fatigue_life)
    ]
    
    print(f"Found {len(high_performance)} samples meeting performance targets")
    print(f"({len(high_performance)/len(df)*100:.1f}% of total dataset)")
    
    if len(high_performance) > 0:
        # Analyze optimal parameter ranges
        continuous_params = ['power_W', 'force_N', 'time_s', 'tab_thickness_um', 'preheat_temp_C']
        
        print("\nOptimal parameter ranges for high performance:")
        for param in continuous_params:
            if param in high_performance.columns:
                param_data = high_performance[param]
                print(f"{param}:")
                print(f"  Range: {param_data.min():.2f} - {param_data.max():.2f}")
                print(f"  Mean: {param_data.mean():.2f} ± {param_data.std():.2f}")
                print(f"  Recommended: {param_data.quantile(0.25):.2f} - {param_data.quantile(0.75):.2f}")
        
        # Best categorical choices
        categorical_params = ['welding_technique', 'anode_material', 'cathode_material', 'surface_coating']
        
        print("\nBest categorical choices for high performance:")
        for param in categorical_params:
            if param in high_performance.columns:
                value_counts = high_performance[param].value_counts()
                percentages = value_counts / len(high_performance) * 100
                print(f"{param}:")
                for value, count in value_counts.head(3).items():
                    print(f"  {value}: {count} samples ({percentages[value]:.1f}%)")
    
    return high_performance

def example_6_failure_analysis():
    """Example 6: Analyze failure modes and poor performance"""
    print("\n=== Example 6: Failure Analysis ===")
    
    df = pd.read_csv('welding_complete_dataset.csv')
    
    # Define poor performance criteria
    poor_performance = df[
        (df['long_term_reliability_score'] < 40) |
        (df['thermal_fatigue_life_cycles'] < 10000) |
        (df['resistance_drift_percent'] > 5)
    ]
    
    print(f"Found {len(poor_performance)} samples with poor performance")
    print(f"({len(poor_performance)/len(df)*100:.1f}% of total dataset)")
    
    # Common failure characteristics
    print("\nCommon characteristics of poor performance:")
    
    # High porosity
    high_porosity = poor_performance[poor_performance['porosity_percent'] > 5]
    print(f"High porosity (>5%): {len(high_porosity)} samples ({len(high_porosity)/len(poor_performance)*100:.1f}%)")
    
    # Low weld strength
    low_strength = poor_performance[poor_performance['weld_strength_MPa'] < 100]
    print(f"Low weld strength (<100 MPa): {len(low_strength)} samples ({len(low_strength)/len(poor_performance)*100:.1f}%)")
    
    # High electrical resistance
    high_resistance = poor_performance[poor_performance['electrical_resistance_uOhm'] > 20]
    print(f"High electrical resistance (>20 µΩ): {len(high_resistance)} samples ({len(high_resistance)/len(poor_performance)*100:.1f}%)")
    
    # Technique analysis for failures
    print("\nFailure rate by welding technique:")
    for technique in df['welding_technique'].unique():
        technique_data = df[df['welding_technique'] == technique]
        technique_failures = poor_performance[poor_performance['welding_technique'] == technique]
        failure_rate = len(technique_failures) / len(technique_data) * 100
        print(f"  {technique}: {failure_rate:.1f}% failure rate")
    
    return poor_performance

def example_7_design_recommendations():
    """Example 7: Generate design recommendations"""
    print("\n=== Example 7: Design Recommendations ===")
    
    df = pd.read_csv('welding_complete_dataset.csv')
    
    print("Design Recommendations for High-Performance Welding:")
    print("\n1. WELDING TECHNIQUE SELECTION:")
    
    # Best techniques by application
    technique_scores = df.groupby('welding_technique').agg({
        'long_term_reliability_score': 'mean',
        'thermal_fatigue_life_cycles': 'mean',
        'weld_strength_MPa': 'mean',
        'electrical_resistance_uOhm': 'mean'
    })
    
    best_reliability = technique_scores['long_term_reliability_score'].idxmax()
    best_fatigue = technique_scores['thermal_fatigue_life_cycles'].idxmax()
    best_strength = technique_scores['weld_strength_MPa'].idxmax()
    
    print(f"  - For maximum reliability: {best_reliability}")
    print(f"  - For maximum fatigue life: {best_fatigue}")
    print(f"  - For maximum strength: {best_strength}")
    
    print("\n2. MATERIAL SELECTION:")
    
    # Best material combinations
    df['material_combo'] = df['anode_material'] + ' - ' + df['cathode_material']
    material_scores = df.groupby('material_combo')['long_term_reliability_score'].mean().sort_values(ascending=False)
    
    print("  Top 3 material combinations:")
    for i, (combo, score) in enumerate(material_scores.head(3).items()):
        print(f"    {i+1}. {combo}: {score:.1f} reliability score")
    
    print("\n3. PROCESS PARAMETERS:")
    
    # Optimal ranges for high performance (reliability > 80)
    high_perf = df[df['long_term_reliability_score'] > 80]
    
    if len(high_perf) > 0:
        print("  Recommended parameter ranges:")
        params = ['power_W', 'force_N', 'time_s', 'tab_thickness_um']
        for param in params:
            if param in high_perf.columns:
                q25 = high_perf[param].quantile(0.25)
                q75 = high_perf[param].quantile(0.75)
                print(f"    {param}: {q25:.1f} - {q75:.1f}")
    
    print("\n4. QUALITY CONTROL:")
    
    # Critical quality metrics
    quality_thresholds = {
        'porosity_percent': 3.0,
        'weld_strength_MPa': 200.0,
        'electrical_resistance_uOhm': 15.0
    }
    
    print("  Critical quality thresholds:")
    for metric, threshold in quality_thresholds.items():
        print(f"    {metric}: < {threshold}")
    
    print("\n5. RISK MITIGATION:")
    print("  - Monitor porosity levels closely")
    print("  - Control energy density to prevent overheating")
    print("  - Ensure proper surface preparation")
    print("  - Implement real-time process monitoring")
    print("  - Validate with thermal cycling tests")

def main():
    """Run all examples"""
    print("Welding Parameter Dataset - Example Usage")
    print("=" * 50)
    
    # Run all examples
    df = example_1_basic_data_exploration()
    technique_perf = example_2_technique_comparison()
    material_perf = example_3_material_optimization()
    model, importance = example_4_predictive_modeling()
    high_perf = example_5_parameter_optimization()
    poor_perf = example_6_failure_analysis()
    example_7_design_recommendations()
    
    print("\n" + "=" * 50)
    print("All examples completed successfully!")
    print("\nGenerated insights:")
    print("- Dataset exploration and statistics")
    print("- Welding technique performance comparison")
    print("- Material combination optimization")
    print("- Predictive model for reliability")
    print("- Parameter optimization guidelines")
    print("- Failure mode analysis")
    print("- Design recommendations")
    
    return {
        'dataset': df,
        'technique_performance': technique_perf,
        'material_performance': material_perf,
        'model': model,
        'feature_importance': importance,
        'high_performance_samples': high_perf,
        'poor_performance_samples': poor_perf
    }

if __name__ == "__main__":
    results = main()