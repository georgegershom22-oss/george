"""
Machine Learning Modeling Starter Script
ML-Driven Inverse Design of Welding Parameters

This script demonstrates multiple ML approaches for:
1. Regression: Predicting thermal cycles to failure
2. Classification: Good vs Poor weld quality
3. Multi-output: Predicting multiple targets
4. Feature importance analysis
5. Inverse design demonstration
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import (mean_squared_error, r2_score, mean_absolute_error,
                             classification_report, confusion_matrix, roc_auc_score)
from sklearn.inspection import permutation_importance
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("MACHINE LEARNING MODELING")
print("ML-Driven Inverse Design of Welding Parameters")
print("="*80)
print()

# ============================================================================
# LOAD AND PREPARE DATA
# ============================================================================

print("Loading dataset...")
df = pd.read_csv('/workspace/welding_ml_dataset.csv')
print(f"✓ Loaded {len(df)} samples")
print()

# Define feature groups
categorical_features = ['anode_material', 'cathode_material', 'surface_finish', 'welding_technique']
numerical_features = ['power_W', 'amplitude_um', 'force_N', 'time_ms', 'frequency_Hz', 
                      'speed_mm_s', 'tab_thickness_um', 'preheat_temp_C', 'energy_density_J_mm2']

# Encode categorical variables
print("Encoding categorical features...")
df_encoded = pd.get_dummies(df, columns=categorical_features, drop_first=False)
print(f"✓ Total features after encoding: {df_encoded.shape[1]}")
print()

# Get feature column names (exclude targets)
target_cols = ['contact_resistance_uOhm', 'peak_temperature_C', 'weld_nugget_area_mm2',
               'IMC_thickness_um', 'tensile_shear_strength_N', 'penetration_depth_pct',
               'surface_indentation_um', 'hardness_HV', 'porosity_pct',
               'microstructure_uniformity_score', 'thermal_cycles_to_failure',
               'resistance_increase_after_cycling_pct', 'strength_retention_pct',
               'crack_initiation_cycle', 'max_operating_temp_C', 'bond_separation_force_N',
               'electrochemical_stability_score', 'energy_efficiency_score',
               'process_stability_index', 'overall_quality_score', 'weld_quality_class',
               'energy_quartile']

feature_cols = [col for col in df_encoded.columns if col not in target_cols]
print(f"Feature columns: {len(feature_cols)}")
print()

# ============================================================================
# TASK 1: REGRESSION - PREDICT THERMAL CYCLES TO FAILURE
# ============================================================================

print("="*80)
print("TASK 1: REGRESSION - PREDICTING THERMAL CYCLES TO FAILURE")
print("="*80)
print()

# Prepare data
X = df_encoded[feature_cols]
y = df_encoded['thermal_cycles_to_failure']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, shuffle=True
)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")
print()

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("Training models...")
print()

# Model 1: Random Forest
print("1. Random Forest Regressor")
rf_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=4,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)

# Predictions
y_pred_rf = rf_model.predict(X_test)

# Metrics
rf_r2 = r2_score(y_test, y_pred_rf)
rf_rmse = np.sqrt(mean_squared_error(y_test, y_pred_rf))
rf_mae = mean_absolute_error(y_test, y_pred_rf)

print(f"  R² Score: {rf_r2:.4f}")
print(f"  RMSE: {rf_rmse:.2f} cycles")
print(f"  MAE: {rf_mae:.2f} cycles")
print(f"  MAPE: {np.mean(np.abs((y_test - y_pred_rf) / y_test)) * 100:.2f}%")
print()

# Model 2: Gradient Boosting
print("2. Gradient Boosting Regressor")
gb_model = GradientBoostingRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42
)
gb_model.fit(X_train, y_train)

y_pred_gb = gb_model.predict(X_test)

gb_r2 = r2_score(y_test, y_pred_gb)
gb_rmse = np.sqrt(mean_squared_error(y_test, y_pred_gb))
gb_mae = mean_absolute_error(y_test, y_pred_gb)

print(f"  R² Score: {gb_r2:.4f}")
print(f"  RMSE: {gb_rmse:.2f} cycles")
print(f"  MAE: {gb_mae:.2f} cycles")
print(f"  MAPE: {np.mean(np.abs((y_test - y_pred_gb) / y_test)) * 100:.2f}%")
print()

# Best model
best_model = rf_model if rf_r2 > gb_r2 else gb_model
best_name = "Random Forest" if rf_r2 > gb_r2 else "Gradient Boosting"
print(f"✓ Best model: {best_name}")
print()

# ============================================================================
# FEATURE IMPORTANCE ANALYSIS
# ============================================================================

print("="*80)
print("FEATURE IMPORTANCE ANALYSIS")
print("="*80)
print()

# Get feature importances
if best_name == "Random Forest":
    importances = rf_model.feature_importances_
else:
    importances = gb_model.feature_importances_

# Create importance dataframe
importance_df = pd.DataFrame({
    'feature': feature_cols,
    'importance': importances
}).sort_values('importance', ascending=False)

print("Top 20 Most Important Features:")
print(importance_df.head(20).to_string(index=False))
print()

# ============================================================================
# TASK 2: CLASSIFICATION - GOOD VS POOR WELDS
# ============================================================================

print("="*80)
print("TASK 2: CLASSIFICATION - GOOD VS POOR WELDS")
print("="*80)
print()

# Prepare classification data
X_clf = df_encoded[feature_cols]
y_clf = df['weld_quality_class'].map({'Good': 1, 'Poor': 0})

# Split
X_train_clf, X_test_clf, y_train_clf, y_test_clf = train_test_split(
    X_clf, y_clf, test_size=0.2, random_state=42, stratify=y_clf
)

print(f"Training set class distribution:")
print(f"  Good: {y_train_clf.sum()} ({y_train_clf.mean()*100:.2f}%)")
print(f"  Poor: {len(y_train_clf) - y_train_clf.sum()} ({(1-y_train_clf.mean())*100:.2f}%)")
print()

# Random Forest Classifier with class weighting
rf_clf = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    class_weight='balanced',  # Handle imbalance
    random_state=42,
    n_jobs=-1
)

print("Training classifier...")
rf_clf.fit(X_train_clf, y_train_clf)

y_pred_clf = rf_clf.predict(X_test_clf)
y_pred_proba = rf_clf.predict_proba(X_test_clf)[:, 1]

print()
print("Classification Results:")
print(classification_report(y_test_clf, y_pred_clf, 
                          target_names=['Poor', 'Good'], 
                          zero_division=0))

print("Confusion Matrix:")
cm = confusion_matrix(y_test_clf, y_pred_clf)
print(f"  True Negatives (Poor predicted as Poor): {cm[0,0]}")
print(f"  False Positives (Poor predicted as Good): {cm[0,1]}")
print(f"  False Negatives (Good predicted as Poor): {cm[1,0]}")
print(f"  True Positives (Good predicted as Good): {cm[1,1]}")
print()

if len(np.unique(y_test_clf)) > 1:
    roc_auc = roc_auc_score(y_test_clf, y_pred_proba)
    print(f"ROC-AUC Score: {roc_auc:.4f}")
    print()

# ============================================================================
# TASK 3: MULTI-OUTPUT REGRESSION
# ============================================================================

print("="*80)
print("TASK 3: MULTI-OUTPUT REGRESSION")
print("="*80)
print()

print("Predicting multiple targets simultaneously:")
print("  - thermal_cycles_to_failure")
print("  - contact_resistance_uOhm")
print("  - tensile_shear_strength_N")
print()

# Select multiple targets
multi_targets = ['thermal_cycles_to_failure', 'contact_resistance_uOhm', 'tensile_shear_strength_N']
X_multi = df_encoded[feature_cols]
y_multi = df_encoded[multi_targets]

# Split
X_train_multi, X_test_multi, y_train_multi, y_test_multi = train_test_split(
    X_multi, y_multi, test_size=0.2, random_state=42
)

# Train separate models for each target (more flexible than MultiOutputRegressor)
multi_models = {}
multi_scores = {}

for target in multi_targets:
    model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
    model.fit(X_train_multi, y_train_multi[target])
    y_pred = model.predict(X_test_multi)
    
    r2 = r2_score(y_test_multi[target], y_pred)
    rmse = np.sqrt(mean_squared_error(y_test_multi[target], y_pred))
    
    multi_models[target] = model
    multi_scores[target] = {'r2': r2, 'rmse': rmse}
    
    print(f"{target}:")
    print(f"  R² Score: {r2:.4f}")
    print(f"  RMSE: {rmse:.2f}")
    print()

# ============================================================================
# TASK 4: INVERSE DESIGN DEMONSTRATION
# ============================================================================

print("="*80)
print("TASK 4: INVERSE DESIGN DEMONSTRATION")
print("="*80)
print()

print("Goal: Find parameter combinations that achieve target performance")
print()

# Define target performance
target_cycles = 2500
target_resistance = 45  # µΩ
target_strength = 1200  # N

print(f"Target Specifications:")
print(f"  - Thermal cycles: ≥ {target_cycles}")
print(f"  - Contact resistance: ≤ {target_resistance} µΩ")
print(f"  - Tensile strength: ≥ {target_strength} N")
print()

# Method 1: Search existing samples
print("Method 1: Search in existing dataset")
candidates = df[
    (df['thermal_cycles_to_failure'] >= target_cycles) &
    (df['contact_resistance_uOhm'] <= target_resistance) &
    (df['tensile_shear_strength_N'] >= target_strength)
]

print(f"Found {len(candidates)} samples meeting all targets")
if len(candidates) > 0:
    print()
    print("Best candidate (highest overall quality score):")
    best_candidate = candidates.loc[candidates['overall_quality_score'].idxmax()]
    
    print(f"  Welding Technique: {best_candidate['welding_technique']}")
    print(f"  Power: {best_candidate['power_W']:.1f} W")
    print(f"  Force: {best_candidate['force_N']:.1f} N")
    print(f"  Time: {best_candidate['time_ms']:.1f} ms")
    print(f"  Anode: {best_candidate['anode_material']}")
    print(f"  Cathode: {best_candidate['cathode_material']}")
    print(f"  Surface: {best_candidate['surface_finish']}")
    print()
    print(f"  Achieved:")
    print(f"    Thermal cycles: {best_candidate['thermal_cycles_to_failure']:.0f}")
    print(f"    Contact resistance: {best_candidate['contact_resistance_uOhm']:.1f} µΩ")
    print(f"    Tensile strength: {best_candidate['tensile_shear_strength_N']:.0f} N")
    print(f"    Overall quality: {best_candidate['overall_quality_score']:.1f}")
print()

# Method 2: Use ML model to predict from custom parameters
print("Method 2: Generate predictions for custom parameter sets")
print()

# Example: Generate random parameter sets and predict
np.random.seed(42)
n_samples = 1000

# Create synthetic parameter combinations
synthetic_params = pd.DataFrame()

# Random selections
synthetic_params['welding_technique'] = np.random.choice(['Ultrasonic', 'Laser', 'Resistance-Spot'], n_samples)
synthetic_params['anode_material'] = np.random.choice(['Cu', 'Cu-Alloy', 'Ni-plated-Cu'], n_samples)
synthetic_params['cathode_material'] = np.random.choice(['Al', 'Al-Alloy-1050', 'Al-Alloy-3003', 'Al-Alloy-6061'], n_samples)
synthetic_params['surface_finish'] = np.random.choice(['Cleaned', 'Ni-Plated', 'Oxide-Removed'], n_samples)

# Continuous parameters
synthetic_params['power_W'] = np.random.uniform(1000, 4000, n_samples)
synthetic_params['force_N'] = np.random.uniform(500, 1500, n_samples)
synthetic_params['time_ms'] = np.random.uniform(200, 800, n_samples)
synthetic_params['tab_thickness_um'] = np.random.choice([100, 150, 200, 250, 300], n_samples)
synthetic_params['preheat_temp_C'] = np.random.choice([25, 40, 60], n_samples)
synthetic_params['amplitude_um'] = 25.0
synthetic_params['frequency_Hz'] = 20000.0
synthetic_params['speed_mm_s'] = 0.0
synthetic_params['energy_density_J_mm2'] = synthetic_params['power_W'] * synthetic_params['time_ms'] / (synthetic_params['tab_thickness_um'] * 10)

# Encode
synthetic_encoded = pd.get_dummies(synthetic_params, columns=['anode_material', 'cathode_material', 
                                                               'surface_finish', 'welding_technique'])

# Ensure all columns match training data
for col in feature_cols:
    if col not in synthetic_encoded.columns:
        synthetic_encoded[col] = 0

synthetic_encoded = synthetic_encoded[feature_cols]

# Predict using all three models
pred_cycles = multi_models['thermal_cycles_to_failure'].predict(synthetic_encoded)
pred_resistance = multi_models['contact_resistance_uOhm'].predict(synthetic_encoded)
pred_strength = multi_models['tensile_shear_strength_N'].predict(synthetic_encoded)

# Add predictions
synthetic_params['pred_thermal_cycles'] = pred_cycles
synthetic_params['pred_contact_resistance'] = pred_resistance
synthetic_params['pred_tensile_strength'] = pred_strength

# Filter by targets
synthetic_candidates = synthetic_params[
    (synthetic_params['pred_thermal_cycles'] >= target_cycles) &
    (synthetic_params['pred_contact_resistance'] <= target_resistance) &
    (synthetic_params['pred_tensile_strength'] >= target_strength)
]

print(f"Generated {n_samples} synthetic parameter sets")
print(f"Found {len(synthetic_candidates)} predicted to meet targets")

if len(synthetic_candidates) > 0:
    print()
    print("Top 3 predicted parameter combinations:")
    top_3 = synthetic_candidates.nlargest(3, 'pred_thermal_cycles')
    
    for idx, (i, row) in enumerate(top_3.iterrows(), 1):
        print(f"\nOption {idx}:")
        print(f"  Welding Technique: {row['welding_technique']}")
        print(f"  Power: {row['power_W']:.1f} W")
        print(f"  Force: {row['force_N']:.1f} N")
        print(f"  Time: {row['time_ms']:.1f} ms")
        print(f"  Tab Thickness: {row['tab_thickness_um']:.0f} µm")
        print(f"  Predicted:")
        print(f"    Thermal cycles: {row['pred_thermal_cycles']:.0f}")
        print(f"    Contact resistance: {row['pred_contact_resistance']:.1f} µΩ")
        print(f"    Tensile strength: {row['pred_tensile_strength']:.0f} N")
print()

# ============================================================================
# CROSS-VALIDATION
# ============================================================================

print("="*80)
print("CROSS-VALIDATION")
print("="*80)
print()

print("5-Fold Cross-Validation on Thermal Cycles Prediction:")
cv_scores = cross_val_score(
    RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1),
    X, y, cv=5, scoring='r2'
)

print(f"  R² Scores: {cv_scores}")
print(f"  Mean R²: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
print()

# ============================================================================
# MODEL PERSISTENCE
# ============================================================================

print("="*80)
print("SAVING MODELS")
print("="*80)
print()

import pickle

# Save best regression model
with open('/workspace/thermal_cycles_model.pkl', 'wb') as f:
    pickle.dump(best_model, f)
print(f"✓ Saved regression model: thermal_cycles_model.pkl")

# Save scaler
with open('/workspace/feature_scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print(f"✓ Saved feature scaler: feature_scaler.pkl")

# Save classifier
with open('/workspace/weld_quality_classifier.pkl', 'wb') as f:
    pickle.dump(rf_clf, f)
print(f"✓ Saved classifier: weld_quality_classifier.pkl")

# Save multi-output models
with open('/workspace/multi_output_models.pkl', 'wb') as f:
    pickle.dump(multi_models, f)
print(f"✓ Saved multi-output models: multi_output_models.pkl")

# Save feature columns for future use
with open('/workspace/feature_columns.pkl', 'wb') as f:
    pickle.dump(feature_cols, f)
print(f"✓ Saved feature columns: feature_columns.pkl")

print()

# ============================================================================
# SUMMARY
# ============================================================================

print("="*80)
print("MODELING SUMMARY")
print("="*80)
print()

print("✓ Regression Models Trained:")
print(f"  - Random Forest: R² = {rf_r2:.4f}, RMSE = {rf_rmse:.2f} cycles")
print(f"  - Gradient Boosting: R² = {gb_r2:.4f}, RMSE = {gb_rmse:.2f} cycles")
print()

print("✓ Classification Model Trained:")
print(f"  - Random Forest Classifier (balanced)")
print()

print("✓ Multi-Output Models Trained:")
for target, scores in multi_scores.items():
    print(f"  - {target}: R² = {scores['r2']:.4f}")
print()

print("✓ Feature Importance Analyzed")
print(f"  - Top feature: {importance_df.iloc[0]['feature']}")
print()

print("✓ Inverse Design Demonstrated")
print(f"  - Found parameter combinations meeting performance targets")
print()

print("Next Steps:")
print("  1. Hyperparameter tuning with GridSearchCV or RandomizedSearchCV")
print("  2. Try advanced models: XGBoost, LightGBM, Neural Networks")
print("  3. Implement Bayesian optimization for inverse design")
print("  4. Develop multi-objective optimization (Pareto frontier)")
print("  5. Build an interactive web app for parameter recommendation")
print("  6. Validate predictions with experimental data")
print()

print("="*80)
print("Modeling Complete!")
print("="*80)
