#!/usr/bin/env python3
"""
ML-Driven Inverse Design for Welding Parameters

This script implements machine learning approaches for inverse design of welding parameters,
allowing users to specify desired performance targets and get optimal parameter recommendations.

Features:
- Multi-objective optimization
- Constraint handling
- Uncertainty quantification
- Parameter sensitivity analysis
- Real-time optimization

Author: AI Assistant
Date: 2025-10-27
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from scipy.optimize import minimize, differential_evolution
from scipy.stats import norm
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class WeldingInverseDesign:
    def __init__(self, dataset_path):
        """
        Initialize the inverse design system
        
        Args:
            dataset_path (str): Path to the welding dataset
        """
        self.dataset_path = dataset_path
        self.df = None
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_cols = []
        self.target_cols = []
        self.bounds = {}
        
    def load_and_prepare_data(self):
        """Load and prepare the dataset for modeling"""
        print("Loading and preparing dataset...")
        
        self.df = pd.read_csv(self.dataset_path)
        
        # Handle categorical variables
        categorical_cols = ['anode_material', 'cathode_material', 'surface_coating', 'welding_technique']
        
        for col in categorical_cols:
            if col in self.df.columns:
                le = LabelEncoder()
                self.df[f'{col}_encoded'] = le.fit_transform(self.df[col])
                self.encoders[col] = le
        
        # Define feature columns (input parameters)
        self.feature_cols = [
            'anode_material_encoded', 'cathode_material_encoded', 'surface_coating_encoded',
            'welding_technique_encoded', 'tab_thickness_um', 'power_W', 'amplitude_um',
            'force_N', 'time_s', 'speed_mm_s', 'pulse_frequency_Hz', 'preheat_temp_C',
            'humidity_percent', 'atmospheric_pressure_Pa'
        ]
        
        # Define target columns (performance metrics)
        self.target_cols = [
            'thermal_fatigue_life_cycles', 'long_term_reliability_score',
            'resistance_drift_percent', 'mechanical_degradation_percent',
            'weld_strength_MPa', 'electrical_resistance_uOhm'
        ]
        
        # Remove any missing feature columns
        self.feature_cols = [col for col in self.feature_cols if col in self.df.columns]
        self.target_cols = [col for col in self.target_cols if col in self.df.columns]
        
        # Define parameter bounds for optimization
        self.bounds = {
            'anode_material_encoded': (0, len(self.encoders['anode_material'].classes_) - 1),
            'cathode_material_encoded': (0, len(self.encoders['cathode_material'].classes_) - 1),
            'surface_coating_encoded': (0, len(self.encoders['surface_coating'].classes_) - 1),
            'welding_technique_encoded': (0, len(self.encoders['welding_technique'].classes_) - 1),
            'tab_thickness_um': (50, 500),
            'power_W': (50, 8000),
            'amplitude_um': (0, 50),
            'force_N': (0, 5000),
            'time_s': (0.001, 10),
            'speed_mm_s': (0, 3000),
            'pulse_frequency_Hz': (0, 40000),
            'preheat_temp_C': (-10, 80),
            'humidity_percent': (20, 80),
            'atmospheric_pressure_Pa': (95000, 105000)
        }
        
        print(f"Dataset prepared with {len(self.feature_cols)} features and {len(self.target_cols)} targets")
        return self.df
    
    def train_surrogate_models(self):
        """Train surrogate models for each performance metric"""
        print("Training surrogate models...")
        
        X = self.df[self.feature_cols].fillna(0)
        
        for target in self.target_cols:
            print(f"Training model for {target}...")
            
            y = self.df[target].fillna(self.df[target].median())
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            self.scalers[target] = scaler
            
            # Train ensemble model (Random Forest + Gradient Boosting)
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
            gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            
            rf_model.fit(X_train_scaled, y_train)
            gb_model.fit(X_train_scaled, y_train)
            
            # Create ensemble
            rf_pred = rf_model.predict(X_test_scaled)
            gb_pred = gb_model.predict(X_test_scaled)
            ensemble_pred = 0.6 * rf_pred + 0.4 * gb_pred
            
            # Evaluate ensemble
            r2 = r2_score(y_test, ensemble_pred)
            rmse = np.sqrt(mean_squared_error(y_test, ensemble_pred))
            
            print(f"  R²: {r2:.3f}, RMSE: {rmse:.3f}")
            
            # Store models
            self.models[target] = {
                'rf': rf_model,
                'gb': gb_model,
                'r2': r2,
                'rmse': rmse
            }
        
        print("Surrogate models trained successfully")
        return self.models
    
    def predict_performance(self, parameters):
        """
        Predict performance metrics for given parameters
        
        Args:
            parameters (dict or array): Welding parameters
            
        Returns:
            dict: Predicted performance metrics
        """
        if isinstance(parameters, dict):
            # Convert dict to array
            param_array = np.array([parameters.get(col, 0) for col in self.feature_cols])
        else:
            param_array = np.array(parameters)
        
        param_array = param_array.reshape(1, -1)
        
        predictions = {}
        uncertainties = {}
        
        for target in self.target_cols:
            if target in self.models:
                # Scale parameters
                param_scaled = self.scalers[target].transform(param_array)
                
                # Ensemble prediction
                rf_pred = self.models[target]['rf'].predict(param_scaled)[0]
                gb_pred = self.models[target]['gb'].predict(param_scaled)[0]
                ensemble_pred = 0.6 * rf_pred + 0.4 * gb_pred
                
                predictions[target] = ensemble_pred
                
                # Estimate uncertainty (standard deviation of individual predictions)
                uncertainties[target] = abs(rf_pred - gb_pred) / 2
        
        return predictions, uncertainties
    
    def objective_function(self, parameters, targets, weights=None):
        """
        Multi-objective function for optimization
        
        Args:
            parameters (array): Parameter values
            targets (dict): Target performance values
            weights (dict): Weights for each objective
            
        Returns:
            float: Weighted objective value (to minimize)
        """
        if weights is None:
            weights = {target: 1.0 for target in targets.keys()}
        
        predictions, _ = self.predict_performance(parameters)
        
        total_error = 0
        for target, target_value in targets.items():
            if target in predictions:
                if 'fatigue_life' in target or 'reliability' in target or 'strength' in target:
                    # For metrics where higher is better
                    error = max(0, (target_value - predictions[target]) / target_value)
                else:
                    # For metrics where lower is better (drift, degradation, resistance)
                    error = max(0, (predictions[target] - target_value) / target_value)
                
                total_error += weights.get(target, 1.0) * error**2
        
        return total_error
    
    def optimize_parameters(self, targets, weights=None, method='differential_evolution', 
                          constraints=None, n_iterations=1000):
        """
        Optimize welding parameters for target performance
        
        Args:
            targets (dict): Target performance values
            weights (dict): Weights for each objective
            method (str): Optimization method
            constraints (list): Additional constraints
            n_iterations (int): Number of optimization iterations
            
        Returns:
            dict: Optimal parameters and predicted performance
        """
        print(f"Optimizing parameters for targets: {targets}")
        
        # Create bounds array
        bounds_array = [self.bounds[col] for col in self.feature_cols]
        
        # Define constraint functions
        def constraint_function(params):
            """Ensure parameter combinations are physically realistic"""
            constraints_satisfied = []
            
            # Technique-specific constraints
            technique_idx = int(params[self.feature_cols.index('welding_technique_encoded')])
            technique_name = self.encoders['welding_technique'].inverse_transform([technique_idx])[0]
            
            power_idx = self.feature_cols.index('power_W')
            amplitude_idx = self.feature_cols.index('amplitude_um')
            force_idx = self.feature_cols.index('force_N')
            speed_idx = self.feature_cols.index('speed_mm_s')
            
            if technique_name == 'USW':
                # Ultrasonic welding constraints
                constraints_satisfied.append(params[amplitude_idx] - 5)  # Min amplitude
                constraints_satisfied.append(50 - params[amplitude_idx])  # Max amplitude
                constraints_satisfied.append(params[force_idx] - 100)    # Min force
            elif technique_name == 'Laser':
                # Laser welding constraints
                constraints_satisfied.append(params[speed_idx] - 1)      # Min speed
                constraints_satisfied.append(200 - params[speed_idx])    # Max speed
                constraints_satisfied.append(1 - params[force_idx])      # No force for laser
            elif technique_name == 'RSW':
                # Resistance spot welding constraints
                constraints_satisfied.append(params[force_idx] - 500)    # Min force
                constraints_satisfied.append(5000 - params[force_idx])   # Max force
            
            # Energy density constraints
            time_idx = self.feature_cols.index('time_s')
            thickness_idx = self.feature_cols.index('tab_thickness_um')
            
            energy_density = params[power_idx] * params[time_idx] / (params[thickness_idx] / 1000)
            constraints_satisfied.append(energy_density - 100)    # Min energy density
            constraints_satisfied.append(50000 - energy_density)  # Max energy density
            
            return constraints_satisfied
        
        # Optimization
        if method == 'differential_evolution':
            result = differential_evolution(
                lambda x: self.objective_function(x, targets, weights),
                bounds_array,
                maxiter=n_iterations,
                seed=42,
                polish=True
            )
        else:
            # Use scipy minimize with initial guess
            x0 = np.array([np.mean(bound) for bound in bounds_array])
            result = minimize(
                lambda x: self.objective_function(x, targets, weights),
                x0,
                bounds=bounds_array,
                method='L-BFGS-B'
            )
        
        if result.success:
            optimal_params = result.x
            
            # Convert to parameter dictionary
            param_dict = {col: optimal_params[i] for i, col in enumerate(self.feature_cols)}
            
            # Round categorical parameters
            for col in ['anode_material_encoded', 'cathode_material_encoded', 
                       'surface_coating_encoded', 'welding_technique_encoded']:
                if col in param_dict:
                    param_dict[col] = int(round(param_dict[col]))
            
            # Predict performance with optimal parameters
            predictions, uncertainties = self.predict_performance(optimal_params)
            
            # Convert encoded categories back to names
            decoded_params = param_dict.copy()
            for col in ['anode_material', 'cathode_material', 'surface_coating', 'welding_technique']:
                if f'{col}_encoded' in param_dict:
                    encoded_val = int(param_dict[f'{col}_encoded'])
                    decoded_params[col] = self.encoders[col].inverse_transform([encoded_val])[0]
            
            return {
                'optimal_parameters': decoded_params,
                'predicted_performance': predictions,
                'uncertainties': uncertainties,
                'optimization_success': True,
                'objective_value': result.fun
            }
        else:
            return {
                'optimization_success': False,
                'message': result.message
            }
    
    def sensitivity_analysis(self, base_parameters, target_metric, perturbation=0.1):
        """
        Perform sensitivity analysis for a given parameter set
        
        Args:
            base_parameters (dict): Base parameter values
            target_metric (str): Target metric to analyze
            perturbation (float): Relative perturbation for sensitivity
            
        Returns:
            dict: Sensitivity indices for each parameter
        """
        print(f"Performing sensitivity analysis for {target_metric}...")
        
        # Convert base parameters to array
        base_array = np.array([base_parameters.get(col, 0) for col in self.feature_cols])
        
        # Get base prediction
        base_pred, _ = self.predict_performance(base_array)
        base_value = base_pred[target_metric]
        
        sensitivities = {}
        
        for i, param in enumerate(self.feature_cols):
            # Create perturbed parameter sets
            param_high = base_array.copy()
            param_low = base_array.copy()
            
            # Handle categorical vs continuous parameters
            if 'encoded' in param:
                # For categorical, try adjacent values
                current_val = int(base_array[i])
                param_high[i] = min(current_val + 1, self.bounds[param][1])
                param_low[i] = max(current_val - 1, self.bounds[param][0])
            else:
                # For continuous, use relative perturbation
                delta = abs(base_array[i] * perturbation)
                if delta == 0:  # Handle zero values
                    delta = (self.bounds[param][1] - self.bounds[param][0]) * 0.01
                param_high[i] = min(base_array[i] + delta, self.bounds[param][1])
                param_low[i] = max(base_array[i] - delta, self.bounds[param][0])
            
            # Get predictions for perturbed parameters
            pred_high, _ = self.predict_performance(param_high)
            pred_low, _ = self.predict_performance(param_low)
            
            # Calculate sensitivity (normalized)
            if param_high[i] != param_low[i]:
                sensitivity = (pred_high[target_metric] - pred_low[target_metric]) / (param_high[i] - param_low[i])
                # Normalize by base value to get relative sensitivity
                normalized_sensitivity = abs(sensitivity * base_array[i] / base_value) if base_value != 0 else 0
            else:
                normalized_sensitivity = 0
            
            sensitivities[param] = normalized_sensitivity
        
        # Sort by sensitivity
        sensitivities = dict(sorted(sensitivities.items(), key=lambda x: x[1], reverse=True))
        
        print("Top 5 most sensitive parameters:")
        for i, (param, sens) in enumerate(list(sensitivities.items())[:5]):
            print(f"  {i+1}. {param}: {sens:.4f}")
        
        return sensitivities
    
    def generate_design_space_exploration(self, n_samples=1000):
        """
        Generate design space exploration data
        
        Args:
            n_samples (int): Number of design points to generate
            
        Returns:
            DataFrame: Design space exploration results
        """
        print(f"Generating design space exploration with {n_samples} samples...")
        
        # Generate random parameter combinations
        design_points = []
        
        for _ in range(n_samples):
            params = {}
            for param in self.feature_cols:
                if 'encoded' in param:
                    # Categorical parameter
                    params[param] = np.random.randint(self.bounds[param][0], self.bounds[param][1] + 1)
                else:
                    # Continuous parameter
                    params[param] = np.random.uniform(self.bounds[param][0], self.bounds[param][1])
            
            design_points.append(params)
        
        # Predict performance for all design points
        results = []
        for params in design_points:
            param_array = np.array([params[col] for col in self.feature_cols])
            predictions, uncertainties = self.predict_performance(param_array)
            
            result = params.copy()
            result.update(predictions)
            result.update({f'{k}_uncertainty': v for k, v in uncertainties.items()})
            results.append(result)
        
        exploration_df = pd.DataFrame(results)
        
        # Add decoded categorical variables
        for col in ['anode_material', 'cathode_material', 'surface_coating', 'welding_technique']:
            if f'{col}_encoded' in exploration_df.columns:
                encoded_vals = exploration_df[f'{col}_encoded'].astype(int)
                exploration_df[col] = self.encoders[col].inverse_transform(encoded_vals)
        
        print("Design space exploration completed")
        return exploration_df
    
    def create_optimization_report(self, optimization_results, save_path='/workspace'):
        """
        Create a comprehensive optimization report
        
        Args:
            optimization_results (dict): Results from optimization
            save_path (str): Path to save the report
        """
        if not optimization_results['optimization_success']:
            print("Optimization failed, cannot create report")
            return
        
        report = f"""
# Welding Parameter Optimization Report

## Optimization Results

### Target Performance Metrics
"""
        
        # Add target information if available
        if 'targets' in optimization_results:
            for target, value in optimization_results['targets'].items():
                report += f"- **{target}**: {value}\n"
        
        report += f"""

### Optimal Parameters
"""
        
        for param, value in optimization_results['optimal_parameters'].items():
            if not param.endswith('_encoded'):
                if isinstance(value, float):
                    report += f"- **{param}**: {value:.3f}\n"
                else:
                    report += f"- **{param}**: {value}\n"
        
        report += f"""

### Predicted Performance
"""
        
        for metric, value in optimization_results['predicted_performance'].items():
            uncertainty = optimization_results['uncertainties'].get(metric, 0)
            report += f"- **{metric}**: {value:.3f} ± {uncertainty:.3f}\n"
        
        report += f"""

### Optimization Quality
- **Objective Value**: {optimization_results['objective_value']:.6f}
- **Optimization Success**: {optimization_results['optimization_success']}

## Recommendations

### Implementation Guidelines
1. **Parameter Validation**: Verify that optimal parameters are within equipment capabilities
2. **Uncertainty Consideration**: Account for prediction uncertainties in process control
3. **Experimental Validation**: Conduct validation experiments with optimal parameters
4. **Process Monitoring**: Implement real-time monitoring of critical parameters

### Risk Mitigation
- Monitor parameters with high sensitivity
- Implement feedback control for critical metrics
- Consider parameter tolerances based on uncertainties
- Plan contingency procedures for parameter deviations

---
Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Save report
        with open(f'{save_path}/optimization_report.md', 'w') as f:
            f.write(report)
        
        print(f"Optimization report saved to {save_path}/optimization_report.md")
        return report

def main():
    """Main function demonstrating inverse design capabilities"""
    print("=== ML-Driven Inverse Design for Welding Parameters ===")
    
    # Initialize inverse design system
    inverse_design = WeldingInverseDesign('/workspace/welding_complete_dataset.csv')
    
    # Load and prepare data
    inverse_design.load_and_prepare_data()
    
    # Train surrogate models
    inverse_design.train_surrogate_models()
    
    # Example optimization: High reliability and long fatigue life
    targets = {
        'long_term_reliability_score': 90,
        'thermal_fatigue_life_cycles': 50000,
        'resistance_drift_percent': 2.0,
        'mechanical_degradation_percent': 5.0
    }
    
    weights = {
        'long_term_reliability_score': 2.0,
        'thermal_fatigue_life_cycles': 1.5,
        'resistance_drift_percent': 1.0,
        'mechanical_degradation_percent': 1.0
    }
    
    print("\nOptimizing for high performance targets...")
    results = inverse_design.optimize_parameters(targets, weights)
    
    if results['optimization_success']:
        print("\nOptimization successful!")
        print("Optimal Parameters:")
        for param, value in results['optimal_parameters'].items():
            if not param.endswith('_encoded'):
                if isinstance(value, float):
                    print(f"  {param}: {value:.3f}")
                else:
                    print(f"  {param}: {value}")
        
        print("\nPredicted Performance:")
        for metric, value in results['predicted_performance'].items():
            uncertainty = results['uncertainties'].get(metric, 0)
            print(f"  {metric}: {value:.3f} ± {uncertainty:.3f}")
        
        # Sensitivity analysis
        print("\nPerforming sensitivity analysis...")
        sensitivities = inverse_design.sensitivity_analysis(
            results['optimal_parameters'], 
            'long_term_reliability_score'
        )
        
        # Create optimization report
        results['targets'] = targets
        inverse_design.create_optimization_report(results)
        
    else:
        print("Optimization failed:", results.get('message', 'Unknown error'))
    
    # Generate design space exploration
    print("\nGenerating design space exploration...")
    exploration_df = inverse_design.generate_design_space_exploration(n_samples=5000)
    exploration_df.to_csv('/workspace/design_space_exploration.csv', index=False)
    
    print("\n=== Inverse Design Complete ===")
    print("Files generated:")
    print("- optimization_report.md")
    print("- design_space_exploration.csv")
    
    return inverse_design, results

if __name__ == "__main__":
    inverse_design, results = main()