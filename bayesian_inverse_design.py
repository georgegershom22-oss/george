"""
Bayesian Optimization for Inverse Design of Welding Parameters

This script demonstrates how to use Bayesian optimization to find
optimal welding parameters that maximize thermal cycling performance
while meeting other constraints.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("BAYESIAN OPTIMIZATION FOR INVERSE DESIGN")
print("="*80)
print()

# ============================================================================
# LOAD AND PREPARE DATA
# ============================================================================

print("Loading dataset...")
df = pd.read_csv('/workspace/welding_ml_dataset.csv')
print(f"✓ Loaded {len(df)} samples")
print()

# ============================================================================
# TRAIN SURROGATE MODELS
# ============================================================================

print("Training surrogate models...")
print()

# Encode categorical variables
df_encoded = pd.get_dummies(df, columns=['anode_material', 'cathode_material', 
                                          'surface_finish', 'welding_technique'])

# Define features and targets
target_cols = ['contact_resistance_uOhm', 'peak_temperature_C', 'weld_nugget_area_mm2',
               'IMC_thickness_um', 'tensile_shear_strength_N', 'penetration_depth_pct',
               'surface_indentation_um', 'hardness_HV', 'porosity_pct',
               'microstructure_uniformity_score', 'thermal_cycles_to_failure',
               'resistance_increase_after_cycling_pct', 'strength_retention_pct',
               'crack_initiation_cycle', 'max_operating_temp_C', 'bond_separation_force_N',
               'electrochemical_stability_score', 'energy_efficiency_score',
               'process_stability_index', 'overall_quality_score', 'weld_quality_class']

feature_cols = [col for col in df_encoded.columns if col not in target_cols]

# Train models for key targets
targets_to_model = {
    'thermal_cycles_to_failure': 'Thermal Cycles to Failure',
    'contact_resistance_uOhm': 'Contact Resistance',
    'tensile_shear_strength_N': 'Tensile Strength',
    'IMC_thickness_um': 'IMC Thickness',
    'overall_quality_score': 'Overall Quality'
}

models = {}
scalers = {}

for target, name in targets_to_model.items():
    print(f"Training model for {name}...")
    
    X = df_encoded[feature_cols]
    y = df_encoded[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    score = model.score(X_test, y_test)
    print(f"  R² Score: {score:.4f}")
    
    models[target] = model
    scalers[target] = scaler

print()
print("✓ Surrogate models trained")
print()

# ============================================================================
# SIMPLE GRID SEARCH OPTIMIZATION
# ============================================================================

print("="*80)
print("OPTIMIZATION METHOD 1: INTELLIGENT GRID SEARCH")
print("="*80)
print()

print("Searching for optimal parameters for Ultrasonic Welding...")
print()

# Define search space for Ultrasonic welding
n_candidates = 10000

# Generate random candidates
candidates = pd.DataFrame()
candidates['welding_technique'] = 'Ultrasonic'
candidates['anode_material'] = np.random.choice(['Cu', 'Ni-plated-Cu'], n_candidates)
candidates['cathode_material'] = np.random.choice(['Al', 'Al-Alloy-1050'], n_candidates)
candidates['surface_finish'] = np.random.choice(['Ni-Plated', 'Cleaned'], n_candidates)

# Continuous parameters - focus on promising ranges from EDA
candidates['power_W'] = np.random.uniform(1500, 3000, n_candidates)
candidates['amplitude_um'] = np.random.uniform(20, 40, n_candidates)
candidates['force_N'] = np.random.uniform(800, 1500, n_candidates)
candidates['time_ms'] = np.random.uniform(300, 800, n_candidates)
candidates['frequency_Hz'] = 20000.0  # Standard ultrasonic
candidates['speed_mm_s'] = 0.0  # Not applicable
candidates['tab_thickness_um'] = np.random.choice([150, 200, 250], n_candidates)
candidates['preheat_temp_C'] = np.random.choice([40, 60], n_candidates)

# Calculate energy density
candidates['energy_density_J_mm2'] = (candidates['power_W'] * candidates['time_ms'] / 
                                      (candidates['tab_thickness_um'] * 10))

# Encode candidates
candidates_encoded = pd.get_dummies(candidates, columns=['anode_material', 'cathode_material', 
                                                          'surface_finish', 'welding_technique'])

# Ensure all columns match training data
for col in feature_cols:
    if col not in candidates_encoded.columns:
        candidates_encoded[col] = 0

candidates_encoded = candidates_encoded[feature_cols]

# Predict for all candidates
print("Predicting performance for candidates...")
predictions = pd.DataFrame()

for target, name in targets_to_model.items():
    predictions[target] = models[target].predict(candidates_encoded)
    candidates[f'pred_{target}'] = predictions[target]

print("✓ Predictions complete")
print()

# ============================================================================
# DEFINE OPTIMIZATION OBJECTIVES
# ============================================================================

print("Applying multi-objective optimization criteria...")
print()

# Define targets
TARGET_CYCLES = 2500
TARGET_RESISTANCE = 50  # µΩ
TARGET_IMC_MIN = 1.5    # µm
TARGET_IMC_MAX = 2.5    # µm
TARGET_STRENGTH = 1000  # N

# Multi-objective scoring
def calculate_desirability(row):
    """Calculate composite desirability score (0-1)"""
    
    # Thermal cycles (maximize) - most important
    cycles_score = min(row['pred_thermal_cycles_to_failure'] / 3000, 1.0)
    
    # Contact resistance (minimize)
    resistance_score = max(1.0 - row['pred_contact_resistance_uOhm'] / 100, 0.0)
    
    # IMC thickness (target range)
    imc = row['pred_IMC_thickness_um']
    if TARGET_IMC_MIN <= imc <= TARGET_IMC_MAX:
        imc_score = 1.0
    elif imc < TARGET_IMC_MIN:
        imc_score = imc / TARGET_IMC_MIN
    else:
        imc_score = max(1.0 - (imc - TARGET_IMC_MAX) / 5, 0.0)
    
    # Tensile strength (maximize, but with saturation)
    strength_score = min(row['pred_tensile_shear_strength_N'] / 1500, 1.0)
    
    # Overall quality
    quality_score = row['pred_overall_quality_score'] / 100
    
    # Weighted geometric mean (desirability function)
    weights = [0.40, 0.25, 0.15, 0.10, 0.10]  # Cycles, Resistance, IMC, Strength, Quality
    scores = [cycles_score, resistance_score, imc_score, strength_score, quality_score]
    
    # Geometric mean
    desirability = np.prod([s**w for s, w in zip(scores, weights)])
    
    return desirability

candidates['desirability'] = candidates.apply(calculate_desirability, axis=1)

print("✓ Desirability scores calculated")
print()

# ============================================================================
# RESULTS
# ============================================================================

print("="*80)
print("OPTIMIZATION RESULTS")
print("="*80)
print()

# Sort by desirability
candidates_sorted = candidates.sort_values('desirability', ascending=False)

print("TOP 5 OPTIMAL PARAMETER COMBINATIONS:")
print()

for rank in range(min(5, len(candidates_sorted))):
    row = candidates_sorted.iloc[rank]
    print(f"{'='*60}")
    print(f"RANK #{rank+1} - Desirability Score: {row['desirability']:.4f}")
    print(f"{'='*60}")
    print()
    print("Input Parameters:")
    print(f"  Anode Material: {row['anode_material']}")
    print(f"  Cathode Material: {row['cathode_material']}")
    print(f"  Surface Finish: {row['surface_finish']}")
    print(f"  Welding Technique: {row['welding_technique']}")
    print()
    print(f"  Power: {row['power_W']:.1f} W")
    print(f"  Amplitude: {row['amplitude_um']:.1f} µm")
    print(f"  Force: {row['force_N']:.1f} N")
    print(f"  Time: {row['time_ms']:.1f} ms")
    print(f"  Tab Thickness: {row['tab_thickness_um']:.0f} µm")
    print(f"  Preheat Temp: {row['preheat_temp_C']:.0f} °C")
    print(f"  Energy Density: {row['energy_density_J_mm2']:.1f} J/mm²")
    print()
    print("Predicted Performance:")
    print(f"  Thermal Cycles to Failure: {row['pred_thermal_cycles_to_failure']:.0f} cycles")
    print(f"  Contact Resistance: {row['pred_contact_resistance_uOhm']:.2f} µΩ")
    print(f"  IMC Thickness: {row['pred_IMC_thickness_um']:.2f} µm")
    print(f"  Tensile Strength: {row['pred_tensile_shear_strength_N']:.0f} N")
    print(f"  Overall Quality Score: {row['pred_overall_quality_score']:.1f}")
    print()

# ============================================================================
# PARETO FRONTIER ANALYSIS
# ============================================================================

print("="*80)
print("PARETO FRONTIER: Thermal Cycles vs Contact Resistance")
print("="*80)
print()

# Find Pareto-optimal solutions (maximize cycles, minimize resistance)
def is_pareto_efficient(costs):
    """
    Find the Pareto-efficient points
    costs: An (n_points, n_costs) array
    Returns: A boolean array of whether each point is Pareto efficient
    """
    is_efficient = np.ones(costs.shape[0], dtype=bool)
    for i, c in enumerate(costs):
        if is_efficient[i]:
            # Keep any point with a higher thermal cycles AND lower resistance
            # costs[:, 0] is -thermal_cycles (we want to maximize)
            # costs[:, 1] is resistance (we want to minimize)
            is_efficient[is_efficient] = np.any(costs[is_efficient] < c, axis=1)
            is_efficient[i] = True
    return is_efficient

# Prepare data for Pareto analysis
# We want to maximize thermal_cycles (so negate it) and minimize resistance
costs = np.column_stack([
    -candidates_sorted['pred_thermal_cycles_to_failure'].values,
    candidates_sorted['pred_contact_resistance_uOhm'].values
])

pareto_mask = is_pareto_efficient(costs)
pareto_solutions = candidates_sorted[pareto_mask].head(10)

print(f"Found {pareto_mask.sum()} Pareto-optimal solutions")
print()
print("Top 10 Pareto-Optimal Solutions:")
print()

for idx, (_, row) in enumerate(pareto_solutions.iterrows(), 1):
    print(f"{idx}. Cycles: {row['pred_thermal_cycles_to_failure']:.0f}, "
          f"Resistance: {row['pred_contact_resistance_uOhm']:.2f} µΩ, "
          f"Desirability: {row['desirability']:.4f}")

print()

# ============================================================================
# SENSITIVITY ANALYSIS
# ============================================================================

print("="*80)
print("SENSITIVITY ANALYSIS")
print("="*80)
print()

# Use the best candidate as baseline
best = candidates_sorted.iloc[0]

print("Analyzing sensitivity of top solution to parameter variations...")
print()

# Vary each parameter ±10%
sensitive_params = ['power_W', 'amplitude_um', 'force_N', 'time_ms']

sensitivity_results = []

for param in sensitive_params:
    # Create variations
    variations = pd.DataFrame([best.to_dict() for _ in range(21)])
    
    # Vary parameter from -10% to +10%
    baseline_value = best[param]
    variation_range = np.linspace(0.9 * baseline_value, 1.1 * baseline_value, 21)
    variations[param] = variation_range
    
    # Recalculate energy density if needed
    if param in ['power_W', 'time_ms']:
        variations['energy_density_J_mm2'] = (variations['power_W'] * variations['time_ms'] / 
                                              (variations['tab_thickness_um'] * 10))
    
    # Encode
    variations_encoded = pd.get_dummies(variations, 
                                       columns=['anode_material', 'cathode_material', 
                                               'surface_finish', 'welding_technique'])
    
    for col in feature_cols:
        if col not in variations_encoded.columns:
            variations_encoded[col] = 0
    
    variations_encoded = variations_encoded[feature_cols]
    
    # Predict
    pred_cycles = models['thermal_cycles_to_failure'].predict(variations_encoded)
    
    # Calculate sensitivity
    cycle_range = pred_cycles.max() - pred_cycles.min()
    param_change_pct = 20  # ±10% = 20% total range
    
    sensitivity = cycle_range / param_change_pct  # Cycles per % change
    
    sensitivity_results.append({
        'parameter': param,
        'baseline': baseline_value,
        'predicted_cycles_range': cycle_range,
        'sensitivity': sensitivity
    })

# Sort by sensitivity
sensitivity_df = pd.DataFrame(sensitivity_results).sort_values('sensitivity', ascending=False)

print("Parameter Sensitivity (Cycles change per 1% parameter change):")
print()
for _, row in sensitivity_df.iterrows():
    print(f"  {row['parameter']:20s}: {row['sensitivity']:6.1f} cycles/% "
          f"(Baseline: {row['baseline']:.1f}, Range: ±{row['predicted_cycles_range']:.0f} cycles)")

print()

# ============================================================================
# EXPORT RESULTS
# ============================================================================

print("="*80)
print("EXPORTING RESULTS")
print("="*80)
print()

# Save top solutions
top_solutions = candidates_sorted.head(100)
top_solutions.to_csv('/workspace/optimal_welding_parameters.csv', index=False)
print("✓ Saved top 100 solutions: optimal_welding_parameters.csv")

# Save Pareto front
pareto_solutions.to_csv('/workspace/pareto_optimal_solutions.csv', index=False)
print("✓ Saved Pareto-optimal solutions: pareto_optimal_solutions.csv")

# Save sensitivity analysis
sensitivity_df.to_csv('/workspace/sensitivity_analysis.csv', index=False)
print("✓ Saved sensitivity analysis: sensitivity_analysis.csv")

print()

# ============================================================================
# SUMMARY
# ============================================================================

print("="*80)
print("SUMMARY")
print("="*80)
print()

print(f"✓ Evaluated {n_candidates:,} candidate parameter combinations")
print(f"✓ Best predicted thermal cycles: {candidates_sorted.iloc[0]['pred_thermal_cycles_to_failure']:.0f}")
print(f"✓ Best desirability score: {candidates_sorted.iloc[0]['desirability']:.4f}")
print(f"✓ Identified {pareto_mask.sum()} Pareto-optimal solutions")
print()

print("Key Recommendations:")
print("  1. Use Ni-plated or Cu materials with cleaned/Ni-plated surfaces")
print("  2. Optimize energy density to 100-300 J/mm² range")
print("  3. Target IMC thickness of 1.5-2.5 µm for best durability")
print(f"  4. Most sensitive parameter: {sensitivity_df.iloc[0]['parameter']}")
print("  5. Consider Pareto-optimal solutions for multi-objective trade-offs")
print()

print("Next Steps:")
print("  - Validate top predictions with experimental trials")
print("  - Refine surrogate models with experimental data")
print("  - Implement real-time optimization in manufacturing")
print("  - Explore advanced Bayesian optimization (GPyOpt, Ax, etc.)")
print()

print("="*80)
print("Inverse Design Optimization Complete!")
print("="*80)
