"""
Example ML Analysis Script for Welding Parameter Inverse Design Dataset

This script demonstrates:
1. Data loading and exploration
2. Feature engineering
3. Forward modeling (parameters → quality)
4. Inverse design (target quality → parameters)
5. Multi-objective optimization
"""

import numpy as np
import pandas as pd
import json
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("ML-DRIVEN INVERSE DESIGN OF WELDING PARAMETERS")
print("Example Analysis and Modeling Pipeline")
print("="*80)

# ===== 1. LOAD AND EXPLORE DATA =====
print("\n[1] Loading dataset...")
df_train = pd.read_csv('welding_dataset_train.csv')
df_val = pd.read_csv('welding_dataset_validation.csv')
df_test = pd.read_csv('welding_dataset_test.csv')

print(f"✓ Training set: {len(df_train)} samples")
print(f"✓ Validation set: {len(df_val)} samples")
print(f"✓ Test set: {len(df_test)} samples")

# Load metadata
with open('dataset_metadata.json', 'r') as f:
    metadata = json.load(f)

print(f"\n[2] Dataset Overview:")
print(f"   Total features: {len(df_train.columns)}")
print(f"   Input parameters: {metadata['parameter_groups']['input_parameters']['count']}")
print(f"   Characterization metrics: {metadata['parameter_groups']['characterization_metrics']['count']}")
print(f"   Performance metrics: {metadata['parameter_groups']['performance_metrics']['count']}")

# ===== 2. DATA PREPROCESSING =====
print("\n[3] Preprocessing data...")

# Define feature groups
input_features = [
    'anode_thickness_um', 'cathode_thickness_um', 'surface_roughness_ra_um',
    'power_w', 'amplitude_um', 'force_n', 'time_ms', 'speed_mm_s',
    'pulse_frequency_hz', 'pulse_energy_j', 'current_ka',
    'preheat_temp_c', 'ambient_temp_c', 'ambient_humidity_percent'
]

categorical_features = ['anode_material', 'cathode_material', 'surface_finish', 'welding_technique']

# Target variables for prediction
forward_targets = ['quality_score', 'resistance_increase_percent', 'fatigue_life_cycles']

# Encode categorical variables
def encode_categoricals(df, fit=False, encoders=None):
    df_encoded = df.copy()
    if encoders is None:
        encoders = {}
    
    for col in categorical_features:
        if fit:
            encoders[col] = LabelEncoder()
            df_encoded[col + '_encoded'] = encoders[col].fit_transform(df_encoded[col])
        else:
            df_encoded[col + '_encoded'] = encoders[col].transform(df_encoded[col])
    
    return df_encoded, encoders

df_train_encoded, encoders = encode_categoricals(df_train, fit=True)
df_val_encoded, _ = encode_categoricals(df_val, encoders=encoders)
df_test_encoded, _ = encode_categoricals(df_test, encoders=encoders)

# Create feature matrices
categorical_encoded = [col + '_encoded' for col in categorical_features]
all_features = input_features + categorical_encoded

X_train = df_train_encoded[all_features].fillna(0)
X_val = df_val_encoded[all_features].fillna(0)
X_test = df_test_encoded[all_features].fillna(0)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)

print(f"✓ Feature matrix shape: {X_train.shape}")
print(f"✓ Features: {len(all_features)}")

# ===== 3. FORWARD MODELING (Parameters → Quality) =====
print("\n[4] Training forward models (Parameters → Quality Metrics)...")
print("-" * 80)

forward_models = {}
forward_results = {}

for target in forward_targets:
    print(f"\n   Target: {target}")
    
    y_train = df_train_encoded[target]
    y_val = df_val_encoded[target]
    y_test = df_test_encoded[target]
    
    # Train Gradient Boosting model
    model = GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Predictions
    y_pred_train = model.predict(X_train_scaled)
    y_pred_val = model.predict(X_val_scaled)
    y_pred_test = model.predict(X_test_scaled)
    
    # Metrics
    train_r2 = r2_score(y_train, y_pred_train)
    val_r2 = r2_score(y_val, y_pred_val)
    test_r2 = r2_score(y_test, y_pred_test)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    
    print(f"   Training R²:   {train_r2:.4f}")
    print(f"   Validation R²: {val_r2:.4f}")
    print(f"   Test R²:       {test_r2:.4f}")
    print(f"   Test MAE:      {test_mae:.4f}")
    print(f"   Test RMSE:     {test_rmse:.4f}")
    
    forward_models[target] = model
    forward_results[target] = {
        'train_r2': train_r2,
        'val_r2': val_r2,
        'test_r2': test_r2,
        'test_mae': test_mae,
        'test_rmse': test_rmse
    }
    
    # Feature importance (top 5)
    importances = model.feature_importances_
    indices = np.argsort(importances)[-5:]
    print(f"   Top 5 important features:")
    for idx in indices[::-1]:
        print(f"      {all_features[idx]}: {importances[idx]:.4f}")

# ===== 4. QUALITY CLASSIFICATION =====
print("\n" + "-" * 80)
print("[5] Binary classification (Pass/Fail prediction)...")

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

y_train_class = df_train_encoded['pass_fail']
y_val_class = df_val_encoded['pass_fail']
y_test_class = df_test_encoded['pass_fail']

clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
clf.fit(X_train_scaled, y_train_class)

y_pred_class = clf.predict(X_test_scaled)

accuracy = accuracy_score(y_test_class, y_pred_class)
precision = precision_score(y_test_class, y_pred_class)
recall = recall_score(y_test_class, y_pred_class)
f1 = f1_score(y_test_class, y_pred_class)

print(f"   Accuracy:  {accuracy:.4f}")
print(f"   Precision: {precision:.4f}")
print(f"   Recall:    {recall:.4f}")
print(f"   F1-Score:  {f1:.4f}")

# ===== 5. INVERSE DESIGN EXAMPLE =====
print("\n" + "-" * 80)
print("[6] Inverse Design: Finding optimal parameters for target performance...")
print("-" * 80)

# Define target specifications
target_specs = {
    'quality_score': 0.85,  # Target: High quality
    'resistance_increase_percent': 20.0,  # Target: <20% resistance increase
    'fatigue_life_cycles': 1500  # Target: >1500 cycles
}

print("\n   Target specifications:")
for key, value in target_specs.items():
    print(f"      {key}: {value}")

# Simple inverse design approach: Generate candidates and score them
print("\n   Searching for optimal parameters...")

# Generate parameter candidates by sampling from the training distribution
n_candidates = 1000
np.random.seed(42)

# Sample from actual parameter ranges
candidates = pd.DataFrame()
for feat in input_features:
    min_val = df_train[feat].min()
    max_val = df_train[feat].max()
    candidates[feat] = np.random.uniform(min_val, max_val, n_candidates)

# Sample categorical features
for feat in categorical_features:
    candidates[feat] = np.random.choice(df_train[feat].unique(), n_candidates)

# Encode and scale candidates
candidates_encoded, _ = encode_categoricals(candidates, encoders=encoders)
X_candidates = candidates_encoded[all_features].fillna(0)
X_candidates_scaled = scaler.transform(X_candidates)

# Predict performance for all candidates
predictions = {}
for target in forward_targets:
    predictions[target] = forward_models[target].predict(X_candidates_scaled)

# Calculate objective function (minimize deviation from targets)
def calculate_objective(predictions, targets):
    scores = []
    for target, target_value in targets.items():
        pred = predictions[target]
        if target == 'quality_score':
            # Maximize quality score
            score = 1 - np.abs(pred - target_value) / target_value
        elif target == 'resistance_increase_percent':
            # Minimize resistance increase
            score = 1 - np.maximum(0, pred - target_value) / 100
        elif target == 'fatigue_life_cycles':
            # Maximize fatigue life
            score = np.minimum(pred / target_value, 1.0)
        scores.append(score)
    return np.mean(scores, axis=0)

objective_scores = calculate_objective(predictions, target_specs)

# Find best candidates
best_indices = np.argsort(objective_scores)[-5:][::-1]

print("\n   Top 5 recommended parameter sets:")
print("-" * 80)

for rank, idx in enumerate(best_indices, 1):
    print(f"\n   Rank #{rank} (Objective Score: {objective_scores[idx]:.4f})")
    print(f"      Technique: {candidates.iloc[idx]['welding_technique']}")
    print(f"      Power: {candidates.iloc[idx]['power_w']:.1f} W")
    print(f"      Force: {candidates.iloc[idx]['force_n']:.1f} N")
    print(f"      Time: {candidates.iloc[idx]['time_ms']:.1f} ms")
    print(f"      Anode: {candidates.iloc[idx]['anode_material']}, Thickness: {candidates.iloc[idx]['anode_thickness_um']:.1f} µm")
    print(f"      Cathode: {candidates.iloc[idx]['cathode_material']}, Thickness: {candidates.iloc[idx]['cathode_thickness_um']:.1f} µm")
    print(f"   Predicted Performance:")
    print(f"      Quality Score: {predictions['quality_score'][idx]:.4f} (target: {target_specs['quality_score']:.4f})")
    print(f"      Resistance Increase: {predictions['resistance_increase_percent'][idx]:.2f}% (target: <{target_specs['resistance_increase_percent']:.1f}%)")
    print(f"      Fatigue Life: {predictions['fatigue_life_cycles'][idx]:.0f} cycles (target: >{target_specs['fatigue_life_cycles']:.0f})")

# ===== 6. TECHNIQUE COMPARISON =====
print("\n" + "=" * 80)
print("[7] Technique Comparison Analysis...")
print("=" * 80)

technique_performance = df_test.groupby('welding_technique').agg({
    'quality_score': ['mean', 'std'],
    'resistance_increase_percent': ['mean', 'std'],
    'fatigue_life_cycles': ['mean', 'std'],
    'pass_fail': 'mean'
}).round(3)

print("\n   Average Performance by Technique:")
print(technique_performance)

# ===== 7. SAVE RESULTS =====
print("\n" + "=" * 80)
print("[8] Saving results...")

# Save forward model results
results_summary = {
    'forward_modeling': forward_results,
    'classification': {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1)
    },
    'inverse_design_targets': target_specs,
    'best_parameters': {
        f'rank_{i+1}': {
            'technique': candidates.iloc[idx]['welding_technique'],
            'power_w': float(candidates.iloc[idx]['power_w']),
            'force_n': float(candidates.iloc[idx]['force_n']),
            'time_ms': float(candidates.iloc[idx]['time_ms']),
            'objective_score': float(objective_scores[idx]),
            'predicted_quality_score': float(predictions['quality_score'][idx]),
            'predicted_resistance_increase': float(predictions['resistance_increase_percent'][idx]),
            'predicted_fatigue_life': float(predictions['fatigue_life_cycles'][idx])
        }
        for i, idx in enumerate(best_indices)
    }
}

with open('ml_results_summary.json', 'w') as f:
    json.dump(results_summary, f, indent=2)

print("✓ Results saved to ml_results_summary.json")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE!")
print("=" * 80)
print("\nKey Takeaways:")
print("1. Forward models successfully predict quality metrics from process parameters")
print("2. Inverse design approach identifies optimal parameter sets for target performance")
print("3. Different welding techniques show distinct performance characteristics")
print("4. Quality prediction achieves high accuracy with machine learning")
print("\nNext Steps:")
print("- Optimize hyperparameters for better model performance")
print("- Try deep learning models for inverse design")
print("- Implement multi-objective Pareto optimization")
print("- Perform uncertainty quantification")
print("- Deploy models for real-time process control")
print("=" * 80)
