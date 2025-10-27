"""
Example ML Training Script for Welding Parameters Dataset

This script demonstrates:
1. Data loading and preprocessing
2. Feature engineering
3. Model training (multiple algorithms)
4. Model evaluation
5. Feature importance analysis
6. Basic inverse design optimization

Note: Uncomment the import statements and install required packages:
pip install scikit-learn xgboost lightgbm matplotlib seaborn
"""

import pandas as pd
import numpy as np
import glob
import os

# Uncomment these when you have the packages installed:
# from sklearn.model_selection import train_test_split, cross_val_score, GroupKFold
# from sklearn.preprocessing import StandardScaler, LabelEncoder
# from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
# from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
# import xgboost as xgb
# import lightgbm as lgb
# import matplotlib.pyplot as plt
# import seaborn as sns


def load_latest_dataset():
    """Load the most recently generated dataset"""
    csv_files = glob.glob('welding_dataset/welding_dataset_*.csv')
    if not csv_files:
        raise FileNotFoundError("No dataset found! Run generate_welding_dataset.py first.")
    
    latest_file = max(csv_files, key=os.path.getctime)
    print(f"Loading dataset: {latest_file}")
    return pd.read_csv(latest_file)


def create_material_features(df):
    """Create material property mismatch features"""
    
    # Material properties
    thermal_expansion = {
        'Cu': 16.5, 'Al': 23.1, 'Ni': 13.4, 
        'Steel': 11.0, 'Ti': 8.6
    }
    
    conductivity = {
        'Cu': 400, 'Al': 237, 'Ni': 91, 
        'Steel': 50, 'Ti': 22
    }
    
    melting_point = {
        'Cu': 1085, 'Al': 660, 'Ni': 1455, 
        'Steel': 1510, 'Ti': 1668
    }
    
    # Calculate mismatches
    df['thermal_expansion_mismatch'] = df.apply(
        lambda row: abs(thermal_expansion.get(row['Anode_Material'], 0) - 
                       thermal_expansion.get(row['Cathode_Material'], 0)),
        axis=1
    )
    
    df['conductivity_mismatch'] = df.apply(
        lambda row: abs(conductivity.get(row['Anode_Material'], 0) - 
                       conductivity.get(row['Cathode_Material'], 0)),
        axis=1
    )
    
    df['melting_point_diff'] = df.apply(
        lambda row: abs(melting_point.get(row['Anode_Material'], 0) - 
                       melting_point.get(row['Cathode_Material'], 0)),
        axis=1
    )
    
    return df


def create_engineered_features(df):
    """Create engineered features"""
    
    # Thickness ratio
    df['thickness_ratio'] = df['Anode_Thickness_um'] / (df['Cathode_Thickness_um'] + 1e-6)
    df['thickness_diff'] = abs(df['Anode_Thickness_um'] - df['Cathode_Thickness_um'])
    
    # Power density approximation
    df['power_per_time'] = df['Power_W'] / (df['Time_ms'] + 1)
    
    # Force per area approximation
    df['pressure_force_product'] = df['Pressure_MPa'] * df['Force_N']
    
    # Thermal gradient indicator
    df['thermal_gradient'] = df['Preheat_Temperature_C'] * df['Cooling_Rate_C_per_s']
    
    # Energy input
    df['total_energy'] = df['Power_W'] * df['Time_ms'] / 1000  # in Joules
    
    return df


def prepare_data(df, target='Thermal_Cycles_to_Failure'):
    """Prepare data for ML training"""
    
    print("\nPreparing data for ML training...")
    
    # Create engineered features
    df = create_material_features(df)
    df = create_engineered_features(df)
    
    # Define feature groups
    input_features = [
        'Anode_Thickness_um', 'Cathode_Thickness_um',
        'Power_W', 'Amplitude_um', 'Force_N', 'Pressure_MPa',
        'Time_ms', 'Speed_mm_s', 'Pulse_Frequency_Hz', 'Pulse_Energy_J',
        'Preheat_Temperature_C', 'Ambient_Humidity_%',
        'Cooling_Rate_C_per_s', 'Gap_Distance_mm'
    ]
    
    quality_features = [
        'Weld_Strength_MPa', 'Joint_Resistance_mOhm', 'Nugget_Diameter_mm',
        'Penetration_Depth_um', 'HAZ_Width_mm', 'Porosity_%',
        'Surface_Roughness_um', 'Microhardness_HV', 'Grain_Size_um',
        'Visual_Quality_Score', 'Interfacial_Bonding_%',
        'Initial_Crack_Density_per_mm2', 'Residual_Stress_MPa'
    ]
    
    engineered_features = [
        'thermal_expansion_mismatch', 'conductivity_mismatch', 'melting_point_diff',
        'thickness_ratio', 'thickness_diff', 'power_per_time',
        'pressure_force_product', 'thermal_gradient', 'total_energy'
    ]
    
    categorical_features = [
        'Anode_Material', 'Cathode_Material', 'Surface_Finish',
        'Welding_Technique', 'Chamber_Atmosphere', 'Electrode_Material'
    ]
    
    # Combine features
    all_numeric_features = input_features + quality_features + engineered_features
    
    # Handle categorical features (simple label encoding for demo)
    df_encoded = df.copy()
    for col in categorical_features:
        if col in df_encoded.columns:
            # Simple frequency encoding
            freq_map = df_encoded[col].value_counts(normalize=True).to_dict()
            df_encoded[col + '_encoded'] = df_encoded[col].map(freq_map)
            all_numeric_features.append(col + '_encoded')
    
    # Select features that exist in the dataframe
    available_features = [f for f in all_numeric_features if f in df_encoded.columns]
    
    # Create X and y
    X = df_encoded[available_features].fillna(0)
    y = df_encoded[target]
    
    print(f"\nFeature matrix shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    print(f"Number of features: {len(available_features)}")
    
    return X, y, available_features


def train_example_models(X, y, feature_names):
    """Train example ML models and compare performance"""
    
    print("\n" + "="*80)
    print("MODEL TRAINING & EVALUATION")
    print("="*80)
    
    # Note: This is a template. Uncomment when packages are installed.
    
    print("\nTo train models, uncomment the code and install:")
    print("pip install scikit-learn xgboost lightgbm")
    print("\nExample code structure:")
    print("""
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train models
    models = {
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
        'XGBoost': xgb.XGBRegressor(n_estimators=100, random_state=42),
        'LightGBM': lgb.LGBMRegressor(n_estimators=100, random_state=42)
    }
    
    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        results[name] = {'RMSE': rmse, 'MAE': mae, 'R2': r2}
        print(f"{name}: RMSE={rmse:.2f}, MAE={mae:.2f}, R²={r2:.4f}")
    
    # Feature importance (for tree-based models)
    best_model = models['XGBoost']  # or choose best based on results
    importances = pd.DataFrame({
        'feature': feature_names,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\\nTop 10 Most Important Features:")
    print(importances.head(10))
    """)


def inverse_design_example():
    """Example of inverse design optimization"""
    
    print("\n" + "="*80)
    print("INVERSE DESIGN OPTIMIZATION EXAMPLE")
    print("="*80)
    
    print("\nInverse design aims to find optimal input parameters that maximize performance.")
    print("\nExample approach:")
    print("""
    1. Train forward model: inputs → performance
    2. Use optimization algorithm:
       - Bayesian Optimization (scikit-optimize)
       - Genetic Algorithm (DEAP)
       - Gradient-based (if differentiable)
    
    3. Define objective function:
       def objective(params):
           # Unpack parameters
           power, amplitude, force, time, temp = params
           
           # Predict performance
           X_new = create_feature_vector(params)
           predicted_cycles = model.predict(X_new)
           
           # Return negative (for minimization)
           return -predicted_cycles[0]
    
    4. Define constraints:
       - Parameter bounds (physical limits)
       - Quality thresholds (Visual_Quality_Score >= 6)
       - Cost constraints
    
    5. Run optimization:
       from scipy.optimize import minimize
       result = minimize(objective, x0=initial_guess, 
                        bounds=bounds, method='L-BFGS-B')
    
    6. Validate results:
       - Check if solution is physically feasible
       - Verify with forward model
       - Consider manufacturing constraints
    """)


def main():
    """Main training pipeline"""
    
    print("\n" + "="*80)
    print("WELDING PARAMETERS - ML TRAINING EXAMPLE")
    print("="*80)
    
    try:
        # Load data
        df = load_latest_dataset()
        print(f"\nDataset loaded: {df.shape[0]} samples, {df.shape[1]} features")
        
        # Prepare data
        X, y, feature_names = prepare_data(df, target='Thermal_Cycles_to_Failure')
        
        print("\n" + "-"*80)
        print("Data preparation complete!")
        print(f"Ready for ML training with {X.shape[1]} features")
        
        # Show example workflows
        train_example_models(X, y, feature_names)
        inverse_design_example()
        
        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("""
1. Install ML packages:
   pip install scikit-learn xgboost lightgbm matplotlib seaborn

2. Uncomment the training code in this script

3. Experiment with different models and hyperparameters

4. Try different target variables:
   - Thermal_Cycles_to_Failure (primary)
   - Overall_Performance_Score (composite)
   - Retained_Strength_% (specific metric)

5. Implement cross-validation for robust evaluation

6. Build inverse design optimization pipeline

7. Deploy best model for parameter prediction

For more details, see README.md
        """)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
