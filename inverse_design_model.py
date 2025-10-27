import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.multioutput import MultiOutputRegressor
import joblib
import warnings
warnings.filterwarnings('ignore')

class WeldingInverseDesignModel:
    def __init__(self, dataset_path='welding_dataset.csv'):
        """Initialize the inverse design model"""
        self.dataset = pd.read_csv(dataset_path)
        self.scaler = StandardScaler()
        self.models = {}
        self.feature_importance = {}
        
    def prepare_data(self):
        """Prepare data for inverse design modeling"""
        # Encode categorical variables
        le_anode = LabelEncoder()
        le_cathode = LabelEncoder()
        le_surface = LabelEncoder()
        le_technique = LabelEncoder()
        
        df = self.dataset.copy()
        df['anode_material_encoded'] = le_anode.fit_transform(df['anode_material'])
        df['cathode_material_encoded'] = le_cathode.fit_transform(df['cathode_material'])
        df['surface_finish_encoded'] = le_surface.fit_transform(df['surface_finish'])
        df['welding_technique_encoded'] = le_technique.fit_transform(df['welding_technique'])
        
        # Store encoders for inverse transformation
        self.encoders = {
            'anode': le_anode,
            'cathode': le_cathode,
            'surface': le_surface,
            'technique': le_technique
        }
        
        # Define features and targets
        self.feature_cols = [
            'anode_material_encoded', 'cathode_material_encoded', 'tab_thickness_um',
            'surface_finish_encoded', 'welding_technique_encoded', 'power_w',
            'amplitude_um', 'force_n', 'time_ms', 'speed_mm_s', 'pulse_frequency_hz',
            'preheat_temperature_c', 'material_compatibility', 'thermal_mismatch', 'electrical_mismatch'
        ]
        
        # Target variables for inverse design
        self.target_cols = [
            'weld_strength_mpa', 'contact_resistance_mohm', 'porosity_percent',
            'thermal_cycles_to_failure', 'weld_quality_score'
        ]
        
        # Prepare feature and target matrices
        self.X = df[self.feature_cols].values
        self.y = df[self.target_cols].values
        
        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )
        
        # Scale features
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)
        
        print(f"Data prepared: {self.X.shape[0]} samples, {self.X.shape[1]} features, {self.y.shape[1]} targets")
        
    def train_forward_models(self):
        """Train forward models (parameters -> quality/performance)"""
        print("\nTraining forward models...")
        
        # Train individual models for each target
        for i, target in enumerate(self.target_cols):
            print(f"Training model for {target}...")
            
            # Random Forest
            rf = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
            rf.fit(self.X_train_scaled, self.y_train[:, i])
            
            # Gradient Boosting
            gb = GradientBoostingRegressor(n_estimators=200, random_state=42)
            gb.fit(self.X_train_scaled, self.y_train[:, i])
            
            # Neural Network
            nn = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
            nn.fit(self.X_train_scaled, self.y_train[:, i])
            
            # Evaluate models
            rf_score = rf.score(self.X_test_scaled, self.y_test[:, i])
            gb_score = gb.score(self.X_test_scaled, self.y_test[:, i])
            nn_score = nn.score(self.X_test_scaled, self.y_test[:, i])
            
            print(f"  Random Forest R²: {rf_score:.3f}")
            print(f"  Gradient Boosting R²: {gb_score:.3f}")
            print(f"  Neural Network R²: {nn_score:.3f}")
            
            # Choose best model
            best_model = max([(rf, rf_score), (gb, gb_score), (nn, nn_score)], key=lambda x: x[1])[0]
            self.models[f'forward_{target}'] = best_model
            
    def train_inverse_models(self):
        """Train inverse models (quality/performance -> parameters)"""
        print("\nTraining inverse models...")
        
        # For inverse design, we want to predict process parameters from desired outcomes
        # We'll use the quality/performance metrics as inputs and process parameters as outputs
        
        # Define inverse target parameters (key process parameters)
        inverse_target_cols = ['power_w', 'force_n', 'time_ms', 'amplitude_um', 'speed_mm_s']
        inverse_target_indices = [self.feature_cols.index(col) for col in inverse_target_cols]
        
        # Prepare inverse data
        y_inverse = self.X[:, inverse_target_indices]
        X_inverse = self.y
        
        # Split inverse data
        X_inv_train, X_inv_test, y_inv_train, y_inv_test = train_test_split(
            X_inverse, y_inverse, test_size=0.2, random_state=42
        )
        
        # Scale inverse data
        X_inv_train_scaled = StandardScaler().fit_transform(X_inv_train)
        X_inv_test_scaled = StandardScaler().fit_transform(X_inv_test)
        
        # Train multi-output inverse model
        print("Training inverse model (quality/performance -> process parameters)...")
        
        # Random Forest for inverse
        rf_inverse = MultiOutputRegressor(RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1))
        rf_inverse.fit(X_inv_train_scaled, y_inv_train)
        
        # Gradient Boosting for inverse
        gb_inverse = MultiOutputRegressor(GradientBoostingRegressor(n_estimators=200, random_state=42))
        gb_inverse.fit(X_inv_train_scaled, y_inv_train)
        
        # Evaluate inverse models
        rf_inv_score = rf_inverse.score(X_inv_test_scaled, y_inv_test)
        gb_inv_score = gb_inverse.score(X_inv_test_scaled, y_inv_test)
        
        print(f"  Random Forest Inverse R²: {rf_inv_score:.3f}")
        print(f"  Gradient Boosting Inverse R²: {gb_inv_score:.3f}")
        
        # Choose best inverse model
        best_inverse_model = max([(rf_inverse, rf_inv_score), (gb_inverse, gb_inv_score)], key=lambda x: x[1])[0]
        self.models['inverse'] = best_inverse_model
        self.inverse_scaler = StandardScaler()
        self.inverse_scaler.fit(X_inverse)
        
        # Store inverse target info
        self.inverse_target_cols = inverse_target_cols
        self.inverse_target_indices = inverse_target_indices
        
    def inverse_design(self, target_quality, target_performance, material_constraints=None):
        """
        Perform inverse design to find optimal welding parameters
        
        Args:
            target_quality: dict with target quality metrics
                e.g., {'weld_strength_mpa': 100, 'contact_resistance_mohm': 0.5, 'porosity_percent': 2.0}
            target_performance: dict with target performance metrics
                e.g., {'thermal_cycles_to_failure': 5000, 'weld_quality_score': 0.8}
            material_constraints: dict with material constraints
                e.g., {'anode_material': 'Cu', 'cathode_material': 'Al', 'welding_technique': 'USW'}
        
        Returns:
            dict with recommended welding parameters
        """
        # Prepare target vector
        target_vector = np.zeros(len(self.target_cols))
        for i, col in enumerate(self.target_cols):
            if col in target_quality:
                target_vector[i] = target_quality[col]
            elif col in target_performance:
                target_vector[i] = target_performance[col]
            else:
                # Use median value if not specified
                target_vector[i] = np.median(self.y[:, i])
        
        # Scale target vector
        target_vector_scaled = self.inverse_scaler.transform(target_vector.reshape(1, -1))
        
        # Predict process parameters
        predicted_params = self.models['inverse'].predict(target_vector_scaled)[0]
        
        # Create result dictionary
        result = {}
        for i, param in enumerate(self.inverse_target_cols):
            result[param] = predicted_params[i]
        
        # Add material constraints if provided
        if material_constraints:
            result.update(material_constraints)
        
        # Validate predictions
        result = self._validate_predictions(result)
        
        return result
    
    def _validate_predictions(self, predictions):
        """Validate and constrain predictions to realistic ranges"""
        # Define realistic ranges for each parameter
        ranges = {
            'power_w': (50, 5000),
            'force_n': (10, 5000),
            'time_ms': (1, 1000),
            'amplitude_um': (0, 100),
            'speed_mm_s': (0, 200)
        }
        
        for param, (min_val, max_val) in ranges.items():
            if param in predictions:
                predictions[param] = np.clip(predictions[param], min_val, max_val)
        
        return predictions
    
    def optimize_parameters(self, target_quality, target_performance, material_constraints=None, n_iterations=100):
        """
        Optimize welding parameters using iterative refinement
        
        Args:
            target_quality: dict with target quality metrics
            target_performance: dict with target performance metrics
            material_constraints: dict with material constraints
            n_iterations: number of optimization iterations
        
        Returns:
            dict with optimized welding parameters and predicted outcomes
        """
        print(f"\nOptimizing parameters for {n_iterations} iterations...")
        
        # Start with initial inverse design
        current_params = self.inverse_design(target_quality, target_performance, material_constraints)
        
        best_params = current_params.copy()
        best_score = float('inf')
        
        for iteration in range(n_iterations):
            # Convert current parameters to feature vector
            param_vector = self._params_to_vector(current_params)
            
            # Predict outcomes
            predicted_outcomes = self._predict_outcomes(param_vector)
            
            # Calculate score (lower is better)
            score = self._calculate_score(predicted_outcomes, target_quality, target_performance)
            
            if score < best_score:
                best_score = score
                best_params = current_params.copy()
            
            # Update parameters using gradient-like approach
            if iteration < n_iterations - 1:
                current_params = self._update_parameters(current_params, predicted_outcomes, 
                                                      target_quality, target_performance)
        
        # Final prediction with best parameters
        final_param_vector = self._params_to_vector(best_params)
        final_outcomes = self._predict_outcomes(final_param_vector)
        
        result = {
            'optimized_parameters': best_params,
            'predicted_outcomes': final_outcomes,
            'optimization_score': best_score,
            'iterations': n_iterations
        }
        
        return result
    
    def _params_to_vector(self, params):
        """Convert parameter dictionary to feature vector"""
        vector = np.zeros(len(self.feature_cols))
        
        # Map parameters to feature indices
        param_mapping = {
            'power_w': 'power_w',
            'force_n': 'force_n',
            'time_ms': 'time_ms',
            'amplitude_um': 'amplitude_um',
            'speed_mm_s': 'speed_mm_s'
        }
        
        for param, feature in param_mapping.items():
            if param in params and feature in self.feature_cols:
                idx = self.feature_cols.index(feature)
                vector[idx] = params[param]
        
        # Add material constraints
        if 'anode_material' in params:
            vector[0] = self.encoders['anode'].transform([params['anode_material']])[0]
        if 'cathode_material' in params:
            vector[1] = self.encoders['cathode'].transform([params['cathode_material']])[0]
        if 'surface_finish' in params:
            vector[3] = self.encoders['surface'].transform([params['surface_finish']])[0]
        if 'welding_technique' in params:
            vector[4] = self.encoders['technique'].transform([params['welding_technique']])[0]
        
        return vector.reshape(1, -1)
    
    def _predict_outcomes(self, param_vector):
        """Predict quality/performance outcomes from parameters"""
        param_vector_scaled = self.scaler.transform(param_vector)
        
        outcomes = {}
        for i, target in enumerate(self.target_cols):
            if f'forward_{target}' in self.models:
                prediction = self.models[f'forward_{target}'].predict(param_vector_scaled)[0]
                outcomes[target] = prediction
        
        return outcomes
    
    def _calculate_score(self, predicted, target_quality, target_performance):
        """Calculate optimization score"""
        score = 0
        
        for metric, target_value in target_quality.items():
            if metric in predicted:
                error = abs(predicted[metric] - target_value) / target_value
                score += error
        
        for metric, target_value in target_performance.items():
            if metric in predicted:
                error = abs(predicted[metric] - target_value) / target_value
                score += error
        
        return score
    
    def _update_parameters(self, current_params, predicted_outcomes, target_quality, target_performance):
        """Update parameters based on prediction errors"""
        updated_params = current_params.copy()
        
        # Simple gradient-like update
        learning_rate = 0.1
        
        for metric, target_value in {**target_quality, **target_performance}.items():
            if metric in predicted_outcomes:
                error = target_value - predicted_outcomes[metric]
                
                # Update relevant parameters based on feature importance
                if metric == 'weld_strength_mpa':
                    if 'power_w' in updated_params:
                        updated_params['power_w'] += learning_rate * error * 10
                    if 'force_n' in updated_params:
                        updated_params['force_n'] += learning_rate * error * 5
                
                elif metric == 'contact_resistance_mohm':
                    if 'force_n' in updated_params:
                        updated_params['force_n'] += learning_rate * error * 100
                
                elif metric == 'porosity_percent':
                    if 'power_w' in updated_params:
                        updated_params['power_w'] += learning_rate * error * 50
                    if 'force_n' in updated_params:
                        updated_params['force_n'] += learning_rate * error * 20
        
        return updated_params
    
    def save_models(self, filepath='welding_models.joblib'):
        """Save trained models"""
        model_data = {
            'models': self.models,
            'scaler': self.scaler,
            'inverse_scaler': self.inverse_scaler,
            'encoders': self.encoders,
            'feature_cols': self.feature_cols,
            'target_cols': self.target_cols,
            'inverse_target_cols': self.inverse_target_cols,
            'inverse_target_indices': self.inverse_target_indices
        }
        
        joblib.dump(model_data, filepath)
        print(f"Models saved to {filepath}")
    
    def load_models(self, filepath='welding_models.joblib'):
        """Load trained models"""
        model_data = joblib.load(filepath)
        
        self.models = model_data['models']
        self.scaler = model_data['scaler']
        self.inverse_scaler = model_data['inverse_scaler']
        self.encoders = model_data['encoders']
        self.feature_cols = model_data['feature_cols']
        self.target_cols = model_data['target_cols']
        self.inverse_target_cols = model_data['inverse_target_cols']
        self.inverse_target_indices = model_data['inverse_target_indices']
        
        # Load the dataset to get y values for median calculation
        if not hasattr(self, 'y'):
            dataset = pd.read_csv('welding_dataset.csv')
            self.prepare_data()
        
        print(f"Models loaded from {filepath}")

def main():
    print("=== Welding Inverse Design Model ===")
    
    # Initialize model
    model = WeldingInverseDesignModel()
    
    # Prepare data
    model.prepare_data()
    
    # Train models
    model.train_forward_models()
    model.train_inverse_models()
    
    # Save models
    model.save_models()
    
    # Example inverse design
    print("\n=== Example Inverse Design ===")
    
    target_quality = {
        'weld_strength_mpa': 120,
        'contact_resistance_mohm': 0.3,
        'porosity_percent': 1.5
    }
    
    target_performance = {
        'thermal_cycles_to_failure': 8000,
        'weld_quality_score': 0.85
    }
    
    material_constraints = {
        'anode_material': 'Cu',
        'cathode_material': 'Al',
        'welding_technique': 'USW',
        'surface_finish': 'Polished'
    }
    
    # Simple inverse design
    print("\nSimple Inverse Design:")
    simple_result = model.inverse_design(target_quality, target_performance, material_constraints)
    print("Recommended Parameters:")
    for param, value in simple_result.items():
        if isinstance(value, (int, float)):
            print(f"  {param}: {value:.2f}")
        else:
            print(f"  {param}: {value}")
    
    # Optimized inverse design
    print("\nOptimized Inverse Design:")
    optimized_result = model.optimize_parameters(target_quality, target_performance, material_constraints, n_iterations=50)
    
    print("Optimized Parameters:")
    for param, value in optimized_result['optimized_parameters'].items():
        if isinstance(value, (int, float)):
            print(f"  {param}: {value:.2f}")
        else:
            print(f"  {param}: {value}")
    
    print(f"\nOptimization Score: {optimized_result['optimization_score']:.4f}")
    print("Predicted Outcomes:")
    for metric, value in optimized_result['predicted_outcomes'].items():
        print(f"  {metric}: {value:.2f}")

if __name__ == "__main__":
    main()