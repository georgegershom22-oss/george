import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.neural_network import MLPRegressor
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

class WeldingMLTrainer:
    def __init__(self, dataset_path='welding_dataset.csv'):
        self.dataset_path = dataset_path
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.models = {}
        self.results = {}
        
    def load_and_preprocess_data(self):
        """Load and preprocess the welding dataset"""
        print("Loading dataset...")
        self.df = pd.read_csv(self.dataset_path)
        
        # Separate features and targets
        self.input_features = ['anode_material', 'cathode_material', 'tab_thickness_um', 'surface_finish',
                              'welding_technique', 'power_w', 'amplitude_um', 'force_n', 'time_ms',
                              'speed_mm_s', 'pulse_frequency_hz', 'preheat_temp_c']
        
        self.quality_targets = ['material_compatibility', 'weld_strength_mpa', 'contact_resistance_ohm',
                               'weld_width_mm', 'penetration_depth_mm', 'porosity_percent']
        
        self.performance_targets = ['thermal_cycles_to_failure', 'resistance_degradation_rate',
                                   'strength_retention_percent']
        
        # Encode categorical variables
        categorical_features = ['anode_material', 'cathode_material', 'surface_finish', 'welding_technique']
        for feature in categorical_features:
            le = LabelEncoder()
            self.df[feature + '_encoded'] = le.fit_transform(self.df[feature])
            self.label_encoders[feature] = le
        
        # Create feature matrix
        self.feature_columns = [col + '_encoded' if col in categorical_features else col 
                               for col in self.input_features]
        self.X = self.df[self.feature_columns].values
        
        print(f"Dataset loaded: {self.X.shape[0]} samples, {self.X.shape[1]} features")
        
    def train_models(self):
        """Train multiple ML models for different targets"""
        print("\nTraining models...")
        
        # Define models
        self.models = {
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'XGBoost': xgb.XGBRegressor(n_estimators=100, random_state=42),
            'Ridge Regression': Ridge(alpha=1.0),
            'Lasso Regression': Lasso(alpha=0.1),
            'SVR': SVR(kernel='rbf', C=1.0, gamma='scale'),
            'Neural Network': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
        }
        
        # Train models for each target
        all_targets = self.quality_targets + self.performance_targets
        
        for target in all_targets:
            print(f"\nTraining models for {target}...")
            y = self.df[target].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                self.X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            target_results = {}
            
            for name, model in self.models.items():
                # Train model
                if name in ['Ridge Regression', 'Lasso Regression', 'SVR', 'Neural Network']:
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                
                # Calculate metrics
                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                target_results[name] = {
                    'MSE': mse,
                    'RMSE': rmse,
                    'MAE': mae,
                    'R2': r2,
                    'model': model
                }
                
                print(f"  {name}: R² = {r2:.4f}, RMSE = {rmse:.4f}")
            
            self.results[target] = target_results
    
    def hyperparameter_tuning(self, target='thermal_cycles_to_failure'):
        """Perform hyperparameter tuning for the best model"""
        print(f"\nPerforming hyperparameter tuning for {target}...")
        
        y = self.df[target].values
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, y, test_size=0.2, random_state=42
        )
        
        # XGBoost hyperparameter tuning
        xgb_params = {
            'n_estimators': [100, 200, 300],
            'max_depth': [3, 6, 9],
            'learning_rate': [0.01, 0.1, 0.2],
            'subsample': [0.8, 0.9, 1.0]
        }
        
        xgb_model = xgb.XGBRegressor(random_state=42)
        grid_search = GridSearchCV(
            xgb_model, xgb_params, cv=5, scoring='r2', n_jobs=-1
        )
        
        grid_search.fit(X_train, y_train)
        
        print(f"Best parameters: {grid_search.best_params_}")
        print(f"Best R² score: {grid_search.best_score_:.4f}")
        
        # Test best model
        y_pred = grid_search.predict(X_test)
        test_r2 = r2_score(y_test, y_pred)
        print(f"Test R² score: {test_r2:.4f}")
        
        return grid_search.best_estimator_
    
    def feature_importance_analysis(self, target='thermal_cycles_to_failure'):
        """Analyze feature importance for a specific target"""
        print(f"\nAnalyzing feature importance for {target}...")
        
        # Use Random Forest for feature importance
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        y = self.df[target].values
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, y, test_size=0.2, random_state=42
        )
        
        rf_model.fit(X_train, y_train)
        
        # Get feature importance
        importance = rf_model.feature_importances_
        feature_names = self.feature_columns
        
        # Create importance dataframe
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        print("\nTop 10 Most Important Features:")
        for i, row in importance_df.head(10).iterrows():
            print(f"  {row['feature']}: {row['importance']:.4f}")
        
        # Plot feature importance
        plt.figure(figsize=(10, 6))
        sns.barplot(data=importance_df.head(10), x='importance', y='feature')
        plt.title(f'Feature Importance for {target}')
        plt.xlabel('Importance')
        plt.tight_layout()
        plt.savefig(f'feature_importance_{target}.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return importance_df
    
    def inverse_design_example(self, target_cycles=2000, target_strength=150):
        """Example of inverse design: find parameters for specific targets"""
        print(f"\nInverse Design Example:")
        print(f"Target: {target_cycles} thermal cycles, {target_strength} MPa strength")
        
        # Train models for both targets
        y_cycles = self.df['thermal_cycles_to_failure'].values
        y_strength = self.df['weld_strength_mpa'].values
        
        # Use XGBoost for both
        cycles_model = xgb.XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42)
        strength_model = xgb.XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42)
        
        cycles_model.fit(self.X, y_cycles)
        strength_model.fit(self.X, y_strength)
        
        # Find samples closest to targets
        cycles_pred = cycles_model.predict(self.X)
        strength_pred = strength_model.predict(self.X)
        
        # Calculate distance from targets
        distance = np.sqrt((cycles_pred - target_cycles)**2 + (strength_pred - target_strength)**2)
        
        # Find best matches
        best_indices = np.argsort(distance)[:5]
        
        print("\nTop 5 Parameter Sets:")
        for i, idx in enumerate(best_indices):
            print(f"\nOption {i+1}:")
            print(f"  Thermal Cycles: {cycles_pred[idx]:.0f}")
            print(f"  Weld Strength: {strength_pred[idx]:.1f} MPa")
            print(f"  Distance from target: {distance[idx]:.2f}")
            
            # Show key parameters
            sample = self.df.iloc[idx]
            print(f"  Anode Material: {sample['anode_material']}")
            print(f"  Cathode Material: {sample['cathode_material']}")
            print(f"  Welding Technique: {sample['welding_technique']}")
            print(f"  Power: {sample['power_w']:.0f} W")
            print(f"  Force: {sample['force_n']:.0f} N")
            print(f"  Time: {sample['time_ms']:.0f} ms")
    
    def generate_report(self):
        """Generate comprehensive model performance report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE MODEL PERFORMANCE REPORT")
        print("="*60)
        
        # Create performance summary
        summary_data = []
        
        for target, target_results in self.results.items():
            for model_name, metrics in target_results.items():
                summary_data.append({
                    'Target': target,
                    'Model': model_name,
                    'R²': metrics['R2'],
                    'RMSE': metrics['RMSE'],
                    'MAE': metrics['MAE']
                })
        
        summary_df = pd.DataFrame(summary_data)
        
        # Best model for each target
        print("\nBEST MODEL FOR EACH TARGET:")
        print("-" * 40)
        
        for target in summary_df['Target'].unique():
            target_data = summary_df[summary_df['Target'] == target]
            best_model = target_data.loc[target_data['R²'].idxmax()]
            print(f"{target}:")
            print(f"  Model: {best_model['Model']}")
            print(f"  R²: {best_model['R²']:.4f}")
            print(f"  RMSE: {best_model['RMSE']:.4f}")
            print(f"  MAE: {best_model['MAE']:.4f}")
            print()
        
        # Overall best models
        print("OVERALL BEST MODELS (by R²):")
        print("-" * 40)
        
        best_models = summary_df.groupby('Model')['R²'].mean().sort_values(ascending=False)
        for model, avg_r2 in best_models.head(3).items():
            print(f"{model}: Average R² = {avg_r2:.4f}")
        
        # Save detailed results
        summary_df.to_csv('model_performance_summary.csv', index=False)
        print(f"\nDetailed results saved to 'model_performance_summary.csv'")
        
        return summary_df

def main():
    # Initialize trainer
    trainer = WeldingMLTrainer()
    
    # Load and preprocess data
    trainer.load_and_preprocess_data()
    
    # Train models
    trainer.train_models()
    
    # Hyperparameter tuning
    best_model = trainer.hyperparameter_tuning('thermal_cycles_to_failure')
    
    # Feature importance analysis
    trainer.feature_importance_analysis('thermal_cycles_to_failure')
    
    # Inverse design example
    trainer.inverse_design_example(target_cycles=2000, target_strength=150)
    
    # Generate comprehensive report
    trainer.generate_report()
    
    print("\n" + "="*60)
    print("ML TRAINING COMPLETE!")
    print("="*60)
    print("Generated files:")
    print("- model_performance_summary.csv")
    print("- feature_importance_thermal_cycles_to_failure.png")
    print("="*60)

if __name__ == "__main__":
    main()