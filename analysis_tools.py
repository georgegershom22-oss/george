#!/usr/bin/env python3
"""
Analysis and Visualization Tools for Welding Dataset
===================================================

This module provides comprehensive analysis and visualization tools for the 
ML-driven inverse design welding dataset.

Features:
- Statistical analysis and correlation studies
- Interactive visualizations
- Feature importance analysis
- Performance prediction models
- Inverse design optimization tools

Author: AI Assistant
Date: 2025-10-27
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class WeldingDatasetAnalyzer:
    """Comprehensive analysis tools for the welding dataset."""
    
    def __init__(self, dataset_path: str = 'welding_dataset'):
        """Initialize the analyzer with dataset path."""
        self.dataset_path = dataset_path
        self.data = {}
        self.combined_data = None
        self.numerical_cols = []
        self.categorical_cols = []
        self.target_cols = []
        
    def load_data(self):
        """Load all dataset files."""
        print("Loading welding dataset...")
        
        # Load individual parts
        self.data['input'] = pd.read_csv(f'{self.dataset_path}/input_parameters.csv')
        self.data['characterization'] = pd.read_csv(f'{self.dataset_path}/characterization_metrics.csv')
        self.data['performance'] = pd.read_csv(f'{self.dataset_path}/performance_metrics.csv')
        
        # Load combined dataset
        self.combined_data = pd.read_csv(f'{self.dataset_path}/complete_dataset.csv')
        
        # Identify column types
        self._identify_column_types()
        
        print(f"Loaded dataset with {len(self.combined_data)} samples and {len(self.combined_data.columns)} features")
        return self.combined_data
    
    def _identify_column_types(self):
        """Identify numerical, categorical, and target columns."""
        # Exclude sample_id
        all_cols = [col for col in self.combined_data.columns if col != 'sample_id']
        
        # Numerical columns
        self.numerical_cols = self.combined_data[all_cols].select_dtypes(include=[np.number]).columns.tolist()
        
        # Categorical columns
        self.categorical_cols = self.combined_data[all_cols].select_dtypes(exclude=[np.number]).columns.tolist()
        
        # Target columns (performance metrics)
        performance_cols = self.data['performance'].columns.tolist()
        performance_cols.remove('sample_id')
        self.target_cols = performance_cols
    
    def generate_summary_statistics(self):
        """Generate comprehensive summary statistics."""
        print("\n" + "="*80)
        print("DATASET SUMMARY STATISTICS")
        print("="*80)
        
        # Basic info
        print(f"Total Samples: {len(self.combined_data)}")
        print(f"Total Features: {len(self.combined_data.columns) - 1}")  # Exclude sample_id
        print(f"Numerical Features: {len(self.numerical_cols)}")
        print(f"Categorical Features: {len(self.categorical_cols)}")
        print(f"Target Variables: {len(self.target_cols)}")
        
        # Missing values
        missing_values = self.combined_data.isnull().sum()
        if missing_values.sum() > 0:
            print(f"\nMissing Values: {missing_values.sum()}")
            print(missing_values[missing_values > 0])
        else:
            print("\nNo missing values detected")
        
        # Numerical statistics
        print("\nNumerical Features Summary:")
        numerical_stats = self.combined_data[self.numerical_cols].describe()
        print(numerical_stats.round(3))
        
        # Categorical features
        print(f"\nCategorical Features:")
        for col in self.categorical_cols:
            unique_vals = self.combined_data[col].nunique()
            print(f"  {col}: {unique_vals} unique values")
        
        return numerical_stats
    
    def plot_correlation_matrix(self, figsize=(20, 16)):
        """Plot correlation matrix for numerical features."""
        plt.figure(figsize=figsize)
        
        # Calculate correlation matrix
        corr_matrix = self.combined_data[self.numerical_cols].corr()
        
        # Create heatmap
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=False, cmap='RdBu_r', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": 0.5})
        
        plt.title('Correlation Matrix - Welding Dataset Features', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{self.dataset_path}/correlation_matrix.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return corr_matrix
    
    def analyze_feature_importance(self, target_variable='reliability_score'):
        """Analyze feature importance for a target variable."""
        print(f"\nAnalyzing feature importance for: {target_variable}")
        
        # Prepare data
        X = self.combined_data[self.numerical_cols].fillna(0)
        y = self.combined_data[target_variable]
        
        # Train Random Forest
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X, y)
        
        # Get feature importance
        importance_df = pd.DataFrame({
            'feature': X.columns,
            'importance': rf.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Plot top 20 features
        plt.figure(figsize=(12, 8))
        top_features = importance_df.head(20)
        sns.barplot(data=top_features, x='importance', y='feature', palette='viridis')
        plt.title(f'Top 20 Feature Importance for {target_variable}', fontsize=14, fontweight='bold')
        plt.xlabel('Feature Importance')
        plt.tight_layout()
        plt.savefig(f'{self.dataset_path}/feature_importance_{target_variable}.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return importance_df
    
    def plot_parameter_distributions(self):
        """Plot distributions of key input parameters."""
        # Key parameters to visualize
        key_params = [
            'power_W', 'time_s', 'force_N', 'tab_thickness_um',
            'preheat_temperature_C', 'surface_roughness_um'
        ]
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.ravel()
        
        for i, param in enumerate(key_params):
            if param in self.combined_data.columns:
                self.combined_data[param].hist(bins=50, ax=axes[i], alpha=0.7, color='skyblue', edgecolor='black')
                axes[i].set_title(f'Distribution of {param}', fontweight='bold')
                axes[i].set_xlabel(param)
                axes[i].set_ylabel('Frequency')
                axes[i].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.dataset_path}/parameter_distributions.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_performance_metrics(self):
        """Plot distributions of performance metrics."""
        performance_metrics = [
            'reliability_score', 'cycle_life_score', 'resistance_drift_percent',
            'tensile_strength_retention_percent', 'fatigue_life_cycles'
        ]
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.ravel()
        
        for i, metric in enumerate(performance_metrics):
            if metric in self.combined_data.columns:
                if i < len(axes):
                    self.combined_data[metric].hist(bins=50, ax=axes[i], alpha=0.7, color='lightcoral', edgecolor='black')
                    axes[i].set_title(f'Distribution of {metric}', fontweight='bold')
                    axes[i].set_xlabel(metric)
                    axes[i].set_ylabel('Frequency')
                    axes[i].grid(True, alpha=0.3)
        
        # Remove empty subplot
        if len(performance_metrics) < len(axes):
            fig.delaxes(axes[-1])
        
        plt.tight_layout()
        plt.savefig(f'{self.dataset_path}/performance_distributions.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def analyze_material_combinations(self):
        """Analyze performance by material combinations."""
        # Create material combination column
        self.combined_data['material_combo'] = (
            self.combined_data['anode_material'] + ' - ' + self.combined_data['cathode_material']
        )
        
        # Performance by material combination
        material_performance = self.combined_data.groupby('material_combo').agg({
            'reliability_score': ['mean', 'std', 'count'],
            'cycle_life_score': ['mean', 'std'],
            'resistance_drift_percent': ['mean', 'std'],
            'contact_resistance_mohm': ['mean', 'std']
        }).round(3)
        
        print("\nPerformance by Material Combination:")
        print(material_performance)
        
        # Plot reliability by material combination
        plt.figure(figsize=(14, 8))
        material_reliability = self.combined_data.groupby('material_combo')['reliability_score'].mean().sort_values(ascending=False)
        
        sns.barplot(x=material_reliability.values, y=material_reliability.index, palette='viridis')
        plt.title('Average Reliability Score by Material Combination', fontsize=14, fontweight='bold')
        plt.xlabel('Average Reliability Score')
        plt.tight_layout()
        plt.savefig(f'{self.dataset_path}/material_performance.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return material_performance
    
    def analyze_welding_techniques(self):
        """Analyze performance by welding technique."""
        technique_performance = self.combined_data.groupby('welding_technique').agg({
            'reliability_score': ['mean', 'std', 'count'],
            'cycle_life_score': ['mean', 'std'],
            'weld_quality_score': ['mean', 'std'],
            'contact_resistance_mohm': ['mean', 'std']
        }).round(3)
        
        print("\nPerformance by Welding Technique:")
        print(technique_performance)
        
        # Box plot of reliability by technique
        plt.figure(figsize=(12, 8))
        sns.boxplot(data=self.combined_data, x='welding_technique', y='reliability_score', palette='Set2')
        plt.xticks(rotation=45)
        plt.title('Reliability Score Distribution by Welding Technique', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{self.dataset_path}/technique_performance.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return technique_performance
    
    def create_interactive_dashboard(self):
        """Create an interactive dashboard using Plotly."""
        print("Creating interactive dashboard...")
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Reliability vs Cycle Life', 'Power vs Quality Score',
                          'Material Performance', 'Technique Comparison'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Scatter plot: Reliability vs Cycle Life
        fig.add_trace(
            go.Scatter(
                x=self.combined_data['cycle_life_score'],
                y=self.combined_data['reliability_score'],
                mode='markers',
                marker=dict(
                    color=self.combined_data['weld_quality_score'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Weld Quality")
                ),
                text=self.combined_data['welding_technique'],
                name='Samples'
            ),
            row=1, col=1
        )
        
        # Power vs Quality
        fig.add_trace(
            go.Scatter(
                x=self.combined_data['power_W'],
                y=self.combined_data['weld_quality_score'],
                mode='markers',
                marker=dict(color='blue', opacity=0.6),
                name='Power vs Quality'
            ),
            row=1, col=2
        )
        
        # Material performance
        material_avg = self.combined_data.groupby('material_combo')['reliability_score'].mean().sort_values(ascending=False)
        fig.add_trace(
            go.Bar(
                x=material_avg.values,
                y=material_avg.index,
                orientation='h',
                marker=dict(color='green'),
                name='Material Performance'
            ),
            row=2, col=1
        )
        
        # Technique comparison
        technique_avg = self.combined_data.groupby('welding_technique')['reliability_score'].mean()
        fig.add_trace(
            go.Bar(
                x=technique_avg.index,
                y=technique_avg.values,
                marker=dict(color='red'),
                name='Technique Performance'
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            title_text="Welding Dataset Interactive Dashboard",
            showlegend=False
        )
        
        # Save as HTML
        fig.write_html(f'{self.dataset_path}/interactive_dashboard.html')
        print(f"Interactive dashboard saved to: {self.dataset_path}/interactive_dashboard.html")
        
        return fig
    
    def perform_pca_analysis(self):
        """Perform Principal Component Analysis."""
        print("\nPerforming PCA analysis...")
        
        # Prepare data
        X = self.combined_data[self.numerical_cols].fillna(0)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Perform PCA
        pca = PCA()
        X_pca = pca.fit_transform(X_scaled)
        
        # Plot explained variance
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        plt.plot(range(1, len(pca.explained_variance_ratio_) + 1), 
                pca.explained_variance_ratio_, 'bo-')
        plt.xlabel('Principal Component')
        plt.ylabel('Explained Variance Ratio')
        plt.title('PCA Explained Variance')
        plt.grid(True)
        
        plt.subplot(1, 2, 2)
        cumsum = np.cumsum(pca.explained_variance_ratio_)
        plt.plot(range(1, len(cumsum) + 1), cumsum, 'ro-')
        plt.xlabel('Number of Components')
        plt.ylabel('Cumulative Explained Variance')
        plt.title('Cumulative Explained Variance')
        plt.grid(True)
        plt.axhline(y=0.95, color='k', linestyle='--', label='95%')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(f'{self.dataset_path}/pca_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Find number of components for 95% variance
        n_components_95 = np.argmax(cumsum >= 0.95) + 1
        print(f"Components needed for 95% variance: {n_components_95}")
        
        return pca, X_pca
    
    def cluster_analysis(self, n_clusters=5):
        """Perform clustering analysis on the dataset."""
        print(f"\nPerforming clustering analysis with {n_clusters} clusters...")
        
        # Prepare data
        X = self.combined_data[self.numerical_cols].fillna(0)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Add cluster labels to data
        self.combined_data['cluster'] = clusters
        
        # Analyze clusters
        cluster_summary = self.combined_data.groupby('cluster').agg({
            'reliability_score': ['mean', 'std'],
            'cycle_life_score': ['mean', 'std'],
            'power_W': ['mean', 'std'],
            'welding_technique': lambda x: x.mode().iloc[0],
            'material_combo': lambda x: x.mode().iloc[0]
        }).round(3)
        
        print("Cluster Summary:")
        print(cluster_summary)
        
        # Plot clusters using PCA
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=clusters, cmap='viridis', alpha=0.6)
        plt.colorbar(scatter)
        plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
        plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
        plt.title('Welding Dataset Clusters (PCA Projection)')
        plt.grid(True, alpha=0.3)
        plt.savefig(f'{self.dataset_path}/cluster_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return kmeans, clusters
    
    def build_prediction_models(self):
        """Build and evaluate prediction models for key performance metrics."""
        print("\nBuilding prediction models...")
        
        # Key target variables
        targets = ['reliability_score', 'cycle_life_score', 'resistance_drift_percent']
        
        # Prepare features
        feature_cols = [col for col in self.numerical_cols if col not in targets]
        X = self.combined_data[feature_cols].fillna(0)
        
        models = {}
        results = {}
        
        for target in targets:
            print(f"\nBuilding model for: {target}")
            
            y = self.combined_data[target]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train models
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            
            rf_model.fit(X_train_scaled, y_train)
            gb_model.fit(X_train_scaled, y_train)
            
            # Predictions
            rf_pred = rf_model.predict(X_test_scaled)
            gb_pred = gb_model.predict(X_test_scaled)
            
            # Evaluate
            rf_r2 = r2_score(y_test, rf_pred)
            gb_r2 = r2_score(y_test, gb_pred)
            rf_mae = mean_absolute_error(y_test, rf_pred)
            gb_mae = mean_absolute_error(y_test, gb_pred)
            
            results[target] = {
                'RandomForest': {'R2': rf_r2, 'MAE': rf_mae},
                'GradientBoosting': {'R2': gb_r2, 'MAE': gb_mae}
            }
            
            models[target] = {
                'RandomForest': rf_model,
                'GradientBoosting': gb_model,
                'scaler': scaler,
                'features': feature_cols
            }
            
            print(f"  Random Forest - R²: {rf_r2:.3f}, MAE: {rf_mae:.3f}")
            print(f"  Gradient Boosting - R²: {gb_r2:.3f}, MAE: {gb_mae:.3f}")
        
        return models, results
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive analysis report."""
        print("\n" + "="*80)
        print("GENERATING COMPREHENSIVE ANALYSIS REPORT")
        print("="*80)
        
        # Load data if not already loaded
        if self.combined_data is None:
            self.load_data()
        
        # Generate all analyses
        summary_stats = self.generate_summary_statistics()
        corr_matrix = self.plot_correlation_matrix()
        
        # Feature importance for key targets
        importance_reliability = self.analyze_feature_importance('reliability_score')
        importance_cycle_life = self.analyze_feature_importance('cycle_life_score')
        
        # Distribution plots
        self.plot_parameter_distributions()
        self.plot_performance_metrics()
        
        # Material and technique analysis
        material_perf = self.analyze_material_combinations()
        technique_perf = self.analyze_welding_techniques()
        
        # Advanced analyses
        pca, X_pca = self.perform_pca_analysis()
        kmeans, clusters = self.cluster_analysis()
        
        # Prediction models
        models, model_results = self.build_prediction_models()
        
        # Interactive dashboard
        dashboard = self.create_interactive_dashboard()
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE!")
        print("="*80)
        print(f"All visualizations and results saved to: {self.dataset_path}/")
        print("Files generated:")
        print("  - correlation_matrix.png")
        print("  - feature_importance_*.png")
        print("  - parameter_distributions.png")
        print("  - performance_distributions.png")
        print("  - material_performance.png")
        print("  - technique_performance.png")
        print("  - pca_analysis.png")
        print("  - cluster_analysis.png")
        print("  - interactive_dashboard.html")
        
        return {
            'summary_stats': summary_stats,
            'correlations': corr_matrix,
            'feature_importance': {
                'reliability': importance_reliability,
                'cycle_life': importance_cycle_life
            },
            'material_performance': material_perf,
            'technique_performance': technique_perf,
            'pca': pca,
            'clusters': kmeans,
            'models': models,
            'model_results': model_results
        }


def main():
    """Main function to run comprehensive analysis."""
    print("Welding Dataset Analysis Tools")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = WeldingDatasetAnalyzer('welding_dataset')
    
    # Load data
    data = analyzer.load_data()
    
    # Generate comprehensive report
    results = analyzer.generate_comprehensive_report()
    
    print("\nAnalysis complete! Check the welding_dataset folder for all outputs.")
    
    return analyzer, results


if __name__ == "__main__":
    analyzer, results = main()