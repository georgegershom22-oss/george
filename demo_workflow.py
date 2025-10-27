#!/usr/bin/env python3
"""
Complete Workflow Demo for Welding Parameter Dataset
This script demonstrates the full pipeline from dataset generation to inverse design optimization.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from inverse_design_model import WeldingInverseDesignModel
import warnings
warnings.filterwarnings('ignore')

def demo_complete_workflow():
    """Demonstrate the complete workflow from dataset to optimization"""
    
    print("=" * 80)
    print("WELDING PARAMETER DATASET - COMPLETE WORKFLOW DEMO")
    print("=" * 80)
    
    # Load the dataset
    print("\n1. LOADING DATASET")
    print("-" * 40)
    dataset = pd.read_csv('welding_dataset.csv')
    print(f"✓ Dataset loaded: {dataset.shape[0]} samples, {dataset.shape[1]} features")
    print(f"✓ Input parameters: 15")
    print(f"✓ Quality metrics: 6") 
    print(f"✓ Performance metrics: 5")
    print(f"✓ Derived features: 2")
    
    # Load trained models
    print("\n2. LOADING TRAINED MODELS")
    print("-" * 40)
    model = WeldingInverseDesignModel()
    model.load_models('welding_models.joblib')
    print("✓ Forward models loaded (parameters → quality/performance)")
    print("✓ Inverse models loaded (quality/performance → parameters)")
    print("✓ Model scalers and encoders loaded")
    
    # Demonstrate forward prediction
    print("\n3. FORWARD PREDICTION DEMO")
    print("-" * 40)
    
    # Example process parameters
    example_params = {
        'anode_material': 'Cu',
        'cathode_material': 'Al', 
        'welding_technique': 'USW',
        'surface_finish': 'Polished',
        'power_w': 1500,
        'force_n': 2000,
        'time_ms': 300,
        'amplitude_um': 50,
        'speed_mm_s': 0,
        'pulse_frequency_hz': 30,
        'tab_thickness_um': 200,
        'preheat_temperature_c': 100
    }
    
    print("Example Process Parameters:")
    for param, value in example_params.items():
        print(f"  {param}: {value}")
    
    # Convert to feature vector and predict
    param_vector = model._params_to_vector(example_params)
    predicted_outcomes = model._predict_outcomes(param_vector)
    
    print("\nPredicted Quality/Performance:")
    for metric, value in predicted_outcomes.items():
        print(f"  {metric}: {value:.2f}")
    
    # Demonstrate inverse design scenarios
    print("\n4. INVERSE DESIGN SCENARIOS")
    print("-" * 40)
    
    scenarios = [
        {
            'name': 'High-Strength Application',
            'target_quality': {'weld_strength_mpa': 140, 'porosity_percent': 1.0},
            'target_performance': {'thermal_cycles_to_failure': 9000},
            'constraints': {'anode_material': 'Cu', 'cathode_material': 'Al', 'welding_technique': 'USW'}
        },
        {
            'name': 'Low-Resistance Application', 
            'target_quality': {'contact_resistance_mohm': 0.2, 'weld_strength_mpa': 100},
            'target_performance': {'weld_quality_score': 0.8},
            'constraints': {'anode_material': 'Cu', 'cathode_material': 'Cu', 'welding_technique': 'Laser'}
        },
        {
            'name': 'High-Performance Application',
            'target_quality': {'weld_strength_mpa': 120, 'porosity_percent': 0.5},
            'target_performance': {'thermal_cycles_to_failure': 12000, 'weld_quality_score': 0.9},
            'constraints': {'anode_material': 'Ni', 'cathode_material': 'Ti', 'welding_technique': 'Friction_Stir'}
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\nScenario {i}: {scenario['name']}")
        print("Target Requirements:")
        for metric, value in {**scenario['target_quality'], **scenario['target_performance']}.items():
            print(f"  {metric}: {value}")
        
        # Simple inverse design
        simple_result = model.inverse_design(
            scenario['target_quality'], 
            scenario['target_performance'], 
            scenario['constraints']
        )
        
        print("Recommended Parameters:")
        for param, value in simple_result.items():
            if isinstance(value, (int, float)):
                print(f"  {param}: {value:.2f}")
            else:
                print(f"  {param}: {value}")
        
        # Optimized inverse design
        optimized_result = model.optimize_parameters(
            scenario['target_quality'],
            scenario['target_performance'], 
            scenario['constraints'],
            n_iterations=30
        )
        
        print("Optimized Parameters:")
        for param, value in optimized_result['optimized_parameters'].items():
            if isinstance(value, (int, float)):
                print(f"  {param}: {value:.2f}")
            else:
                print(f"  {param}: {value}")
        
        print(f"Optimization Score: {optimized_result['optimization_score']:.4f}")
    
    # Dataset statistics summary
    print("\n5. DATASET STATISTICS SUMMARY")
    print("-" * 40)
    
    print("Material Distribution:")
    material_counts = dataset['anode_material'].value_counts()
    for material, count in material_counts.items():
        print(f"  {material}: {count} samples")
    
    print("\nWelding Technique Distribution:")
    technique_counts = dataset['welding_technique'].value_counts()
    for technique, count in technique_counts.items():
        print(f"  {technique}: {count} samples")
    
    print("\nQuality Score Distribution:")
    quality_stats = dataset['weld_quality_score'].describe()
    print(f"  Mean: {quality_stats['mean']:.3f}")
    print(f"  Std: {quality_stats['std']:.3f}")
    print(f"  Min: {quality_stats['min']:.3f}")
    print(f"  Max: {quality_stats['max']:.3f}")
    
    print("\nPerformance Distribution (Thermal Cycles):")
    cycles_stats = dataset['thermal_cycles_to_failure'].describe()
    print(f"  Mean: {cycles_stats['mean']:.0f} cycles")
    print(f"  Std: {cycles_stats['std']:.0f} cycles")
    print(f"  Min: {cycles_stats['min']:.0f} cycles")
    print(f"  Max: {cycles_stats['max']:.0f} cycles")
    
    # Key insights
    print("\n6. KEY INSIGHTS")
    print("-" * 40)
    
    # Best performing combinations
    best_combinations = dataset.groupby(['anode_material', 'cathode_material'])['weld_quality_score'].mean().sort_values(ascending=False).head(3)
    print("Top 3 Material Combinations:")
    for (anode, cathode), score in best_combinations.items():
        print(f"  {anode}-{cathode}: {score:.3f}")
    
    # Best techniques
    best_techniques = dataset.groupby('welding_technique')['weld_quality_score'].mean().sort_values(ascending=False)
    print("\nTechnique Performance Ranking:")
    for i, (technique, score) in enumerate(best_techniques.items(), 1):
        print(f"  {i}. {technique}: {score:.3f}")
    
    # Process parameter insights
    high_quality = dataset[dataset['weld_quality_score'] > 0.8]
    if len(high_quality) > 0:
        print(f"\nHigh-Quality Weld Insights ({len(high_quality)} samples):")
        print(f"  Average Power: {high_quality['power_w'].mean():.0f} W")
        print(f"  Average Force: {high_quality['force_n'].mean():.0f} N")
        print(f"  Average Time: {high_quality['time_ms'].mean():.0f} ms")
    
    print("\n" + "=" * 80)
    print("WORKFLOW DEMO COMPLETE")
    print("=" * 80)
    print("\nGenerated Files:")
    print("✓ welding_dataset.csv - Complete dataset")
    print("✓ welding_dataset.xlsx - Excel format with sheets")
    print("✓ welding_dataset_ml_ready.csv - ML-ready format")
    print("✓ welding_models.joblib - Trained models")
    print("✓ welding_dataset_analysis.png - Static visualizations")
    print("✓ interactive_*.html - Interactive visualizations")
    print("✓ feature_importance.csv - Feature rankings")
    print("✓ README.md - Complete documentation")
    
    print("\nThe dataset is ready for:")
    print("• Process optimization and parameter tuning")
    print("• Quality prediction and validation")
    print("• Material selection and combination analysis")
    print("• Welding technique comparison")
    print("• Performance prediction under thermal cycling")
    print("• Machine learning model development")

if __name__ == "__main__":
    demo_complete_workflow()