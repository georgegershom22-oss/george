#!/usr/bin/env python3
"""
Machine Learning Models for Welding Parameter Inverse Design
===========================================================

This module implements various ML models for inverse design of welding parameters
to achieve target performance metrics.

Author: AI Assistant
Date: 2024
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.linear_model import Ridge, Lasso
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import xgboost as xgb
import lightgbm as lgb
import joblib
import warnings
warnings.filterwarnings('ignore')

class WeldingInverseDesignML:
    """
    Machine Learning models for inverse design of welding parameters
    """
    
    def __init__(self, dataset_path):
        """Initialize with dataset"""
        self.dataset = pd.read_csv(dataset_path)
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_columns = []
        self.target_columns = []
        self.setup_data()
    
    def setup_data(self):
        """Setup and preprocess the data"""
        print("Setting up data for ML models...")
        
        # Define feature columns (input parameters)
        self.feature_columns = [
            'tab_thickness_um', 'power_W', 'amplitude_um', 'force_N', 'time_s',
            'speed_mm_s', 'pulse_frequency_Hz', 'pulse_energy_J', 'current_A',
            'pre_heat_temp_C'
        ]
        
        # Define target columns (performance metrics)
        self.target_columns = [
            'thermal_cycles_to_failure', 'high_temp_strength_MPa', 'fatigue_cycles_1e6',
            'thermal_performance_W_mK', 'creep_resistance_MPa', 'interfacial_stability'
        ]
        
        # Categorical columns
        self.categorical_columns = ['anode_material', 'cathode_material', 'surface_finish', 'welding_technique']
        
        # Clean data - remove rows with missing target values
        self.dataset = self.dataset.dropna(subset=self.target_columns)
        
        print(f"Dataset shape after cleaning: {self.dataset.shape}")
        print(f"Features: {len(self.feature_columns)}")
        print(f"Targets: {len(self.target_columns)}")
    
    def prepare_features(self, X):
        """Prepare features for ML models"""
        # Handle missing values in numerical features
        for col in self.feature_columns:
            if col in X.columns:
                X[col] = X[col].fillna(X[col].median())
        
        # Encode categorical variables
        X_encoded = X.copy()
        for col in self.categorical_columns:
            if col in X.columns:
                le = LabelEncoder()
                X_encoded[col] = le.fit_transform(X[col].astype(str))
                self.encoders[col] = le
        
        return X_encoded
    
    def train_models(self):
        """Train multiple ML models for inverse design"""
        print("Training ML models for inverse design...")
        
        # Prepare data
        X = self.dataset[self.feature_columns + self.categorical_columns].copy()
        y = self.dataset[self.target_columns].copy()
        
        # Prepare features
        X_encoded = self.prepare_features(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_encoded, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers['features'] = scaler
        
        # Define models
        models_config = {
            'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
            'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'XGBoost': xgb.XGBRegressor(n_estimators=100, random_state=42),
            'LightGBM': lgb.LGBMRegressor(n_estimators=100, random_state=42),
            'NeuralNetwork': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42),
            'SVR': SVR(kernel='rbf'),
            'Ridge': Ridge(alpha=1.0),
            'Lasso': Lasso(alpha=0.1)
        }
        
        # Train models for each target
        results = {}
        
        for target in self.target_columns:
            print(f"\nTraining models for target: {target}")
            target_results = {}
            
            # Scale target
            y_scaler = StandardScaler()
            y_train_scaled = y_scaler.fit_transform(y_train[[target]])
            y_test_scaled = y_scaler.transform(y_test[[target]])
            self.scalers[f'target_{target}'] = y_scaler
            
            for name, model in models_config.items():
                try:
                    # Train model
                    model.fit(X_train_scaled, y_train_scaled.ravel())
                    
                    # Predictions
                    y_pred_scaled = model.predict(X_test_scaled)
                    y_pred = y_scaler.inverse_transform(y_pred_scaled.reshape(-1, 1))
                    
                    # Metrics
                    mse = mean_squared_error(y_test[target], y_pred)
                    rmse = np.sqrt(mse)
                    mae = mean_absolute_error(y_test[target], y_pred)
                    r2 = r2_score(y_test[target], y_pred)
                    
                    target_results[name] = {
                        'model': model,
                        'mse': mse,
                        'rmse': rmse,
                        'mae': mae,
                        'r2': r2,
                        'predictions': y_pred
                    }
                    
                    print(f"  {name}: R² = {r2:.3f}, RMSE = {rmse:.3f}")
                    
                except Exception as e:
                    print(f"  {name}: Error - {e}")
            
            # Find best model for this target
            best_model_name = max(target_results.keys(), 
                                key=lambda x: target_results[x]['r2'])
            best_model = target_results[best_model_name]['model']
            
            self.models[target] = {
                'model': best_model,
                'scaler': y_scaler,
                'performance': target_results[best_model_name]
            }
            
            results[target] = target_results
        
        # Save models
        self.save_models()
        
        return results, X_test, y_test
    
    def inverse_design(self, target_performance, constraints=None):
        """
        Perform inverse design to find welding parameters for target performance
        
        Args:
            target_performance: dict with target values for performance metrics
            constraints: dict with constraints on input parameters
        
        Returns:
            dict with recommended welding parameters
        """
        print("Performing inverse design...")
        
        if constraints is None:
            constraints = {}
        
        # Define parameter bounds
        param_bounds = {
            'tab_thickness_um': (50, 500),
            'power_W': (50, 5000),
            'amplitude_um': (10, 100),
            'force_N': (50, 1000),
            'time_s': (0.05, 2.0),
            'speed_mm_s': (1, 50),
            'pulse_frequency_Hz': (1, 1000),
            'pulse_energy_J': (0.1, 10),
            'current_A': (1000, 10000),
            'pre_heat_temp_C': (20, 200)
        }
        
        # Apply constraints
        for param, (min_val, max_val) in param_bounds.items():
            if param in constraints:
                if 'min' in constraints[param]:
                    param_bounds[param] = (constraints[param]['min'], param_bounds[param][1])
                if 'max' in constraints[param]:
                    param_bounds[param] = (param_bounds[param][0], constraints[param]['max'])
        
        # Optimization function
        def objective(params):
            # Create feature vector with all features (numerical + categorical)
            features = np.array(params).reshape(1, -1)
            
            # Add categorical features (use most common values)
            cat_features = []
            for cat_col in self.categorical_columns:
                if cat_col in self.encoders:
                    # Use most common categorical value
                    most_common = self.dataset[cat_col].mode()[0]
                    encoded_val = self.encoders[cat_col].transform([most_common])[0]
                    cat_features.append(encoded_val)
                else:
                    cat_features.append(0)
            
            # Combine numerical and categorical features
            all_features = np.concatenate([features, np.array(cat_features).reshape(1, -1)], axis=1)
            
            # Scale features
            features_scaled = self.scalers['features'].transform(all_features)
            
            # Predict all targets
            total_error = 0
            for target, target_value in target_performance.items():
                if target in self.models:
                    model = self.models[target]['model']
                    scaler = self.models[target]['scaler']
                    
                    pred_scaled = model.predict(features_scaled)
                    pred = scaler.inverse_transform(pred_scaled.reshape(-1, 1))[0, 0]
                    
                    # Weighted error (higher weight for more important targets)
                    weight = 1.0
                    if target == 'thermal_cycles_to_failure':
                        weight = 2.0  # Most important target
                    
                    error = weight * ((pred - target_value) / target_value) ** 2
                    total_error += error
            
            return total_error
        
        # Initial guess (middle of parameter ranges)
        initial_params = []
        for param in self.feature_columns:
            if param in param_bounds:
                min_val, max_val = param_bounds[param]
                initial_params.append((min_val + max_val) / 2)
            else:
                initial_params.append(0)
        
        # Bounds for optimization
        bounds = [param_bounds[param] for param in self.feature_columns if param in param_bounds]
        
        # Optimize
        from scipy.optimize import minimize
        result = minimize(objective, initial_params, bounds=bounds, method='L-BFGS-B')
        
        # Create result dictionary
        recommended_params = {}
        for i, param in enumerate(self.feature_columns):
            if param in param_bounds:
                recommended_params[param] = result.x[i]
        
        # Add categorical parameters (use most common values)
        for cat_col in self.categorical_columns:
            recommended_params[cat_col] = self.dataset[cat_col].mode()[0]
        
        # Predict performance with recommended parameters
        predicted_performance = self.predict_performance(recommended_params)
        
        return {
            'recommended_parameters': recommended_params,
            'predicted_performance': predicted_performance,
            'optimization_success': result.success,
            'optimization_message': result.message
        }
    
    def predict_performance(self, parameters):
        """Predict performance for given parameters"""
        # Prepare features
        feature_vector = []
        for param in self.feature_columns:
            if param in parameters:
                feature_vector.append(parameters[param])
            else:
                feature_vector.append(0)
        
        # Add categorical features
        for cat_col in self.categorical_columns:
            if cat_col in parameters:
                # Encode categorical value
                if cat_col in self.encoders:
                    encoded_val = self.encoders[cat_col].transform([parameters[cat_col]])[0]
                else:
                    encoded_val = 0
                feature_vector.append(encoded_val)
            else:
                feature_vector.append(0)
        
        # Scale features
        features_scaled = self.scalers['features'].transform([feature_vector])
        
        # Predict all targets
        predictions = {}
        for target in self.target_columns:
            if target in self.models:
                model = self.models[target]['model']
                scaler = self.models[target]['scaler']
                
                pred_scaled = model.predict(features_scaled)
                pred = scaler.inverse_transform(pred_scaled.reshape(-1, 1))[0, 0]
                predictions[target] = pred
        
        return predictions
    
    def save_models(self):
        """Save trained models"""
        print("Saving trained models...")
        
        # Save models
        for target, model_data in self.models.items():
            joblib.dump(model_data['model'], f'model_{target}.pkl')
        
        # Save scalers
        for name, scaler in self.scalers.items():
            joblib.dump(scaler, f'scaler_{name}.pkl')
        
        # Save encoders
        for name, encoder in self.encoders.items():
            joblib.dump(encoder, f'encoder_{name}.pkl')
        
        print("Models saved successfully!")
    
    def load_models(self):
        """Load trained models"""
        print("Loading trained models...")
        
        # Load models
        for target in self.target_columns:
            try:
                model = joblib.load(f'model_{target}.pkl')
                scaler = joblib.load(f'scaler_target_{target}.pkl')
                self.models[target] = {'model': model, 'scaler': scaler}
            except FileNotFoundError:
                print(f"Model for {target} not found")
        
        # Load scalers
        try:
            self.scalers['features'] = joblib.load('scaler_features.pkl')
        except FileNotFoundError:
            print("Feature scaler not found")
        
        # Load encoders
        for cat_col in self.categorical_columns:
            try:
                self.encoders[cat_col] = joblib.load(f'encoder_{cat_col}.pkl')
            except FileNotFoundError:
                print(f"Encoder for {cat_col} not found")
    
    def generate_optimization_report(self, target_performance, constraints=None):
        """Generate comprehensive optimization report"""
        print("=" * 60)
        print("WELDING PARAMETER OPTIMIZATION REPORT")
        print("=" * 60)
        
        # Perform inverse design
        result = self.inverse_design(target_performance, constraints)
        
        print(f"\nTarget Performance:")
        for metric, value in target_performance.items():
            print(f"  {metric}: {value}")
        
        print(f"\nRecommended Parameters:")
        for param, value in result['recommended_parameters'].items():
            if isinstance(value, float):
                print(f"  {param}: {value:.3f}")
            else:
                print(f"  {param}: {value}")
        
        print(f"\nPredicted Performance:")
        for metric, value in result['predicted_performance'].items():
            print(f"  {metric}: {value:.3f}")
        
        print(f"\nOptimization Status: {'Success' if result['optimization_success'] else 'Failed'}")
        print(f"Message: {result['optimization_message']}")
        
        # Calculate prediction accuracy
        print(f"\nPrediction Accuracy:")
        for metric in target_performance:
            if metric in result['predicted_performance']:
                target_val = target_performance[metric]
                pred_val = result['predicted_performance'][metric]
                error = abs(pred_val - target_val) / target_val * 100
                print(f"  {metric}: {error:.1f}% error")
        
        return result

def main():
    """Main function for ML model training and inverse design"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python inverse_design_ml.py <dataset_file.csv> [target_thermal_cycles]")
        return
    
    dataset_path = sys.argv[1]
    target_cycles = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
    
    # Initialize ML system
    ml_system = WeldingInverseDesignML(dataset_path)
    
    # Train models
    results, X_test, y_test = ml_system.train_models()
    
    # Example inverse design
    target_performance = {
        'thermal_cycles_to_failure': target_cycles,
        'high_temp_strength_MPa': 150,
        'interfacial_stability': 0.8
    }
    
    constraints = {
        'power_W': {'min': 100, 'max': 2000},
        'force_N': {'min': 100, 'max': 500}
    }
    
    # Generate optimization report
    optimization_result = ml_system.generate_optimization_report(target_performance, constraints)
    
    return ml_system, optimization_result

if __name__ == "__main__":
    ml_system, result = main()