#!/usr/bin/env python3
"""
Welding Dataset Analyzer and Visualization Tool
==============================================

This module provides comprehensive analysis and visualization capabilities
for the welding dataset.

Author: AI Assistant
Date: 2024
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class WeldingDatasetAnalyzer:
    """
    Comprehensive analyzer for welding datasets
    """
    
    def __init__(self, dataset_path):
        """Initialize analyzer with dataset"""
        self.dataset = pd.read_csv(dataset_path)
        self.setup_plotting()
        
    def setup_plotting(self):
        """Setup plotting parameters"""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def basic_statistics(self):
        """Generate basic statistical summary"""
        print("=" * 60)
        print("BASIC DATASET STATISTICS")
        print("=" * 60)
        
        print(f"Total samples: {len(self.dataset)}")
        print(f"Total features: {len(self.dataset.columns)}")
        print(f"Memory usage: {self.dataset.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Input parameters summary
        input_cols = [col for col in self.dataset.columns if col in [
            'anode_material', 'cathode_material', 'surface_finish', 'welding_technique'
        ]]
        
        print(f"\nInput Parameters Distribution:")
        for col in input_cols:
            print(f"\n{col}:")
            print(self.dataset[col].value_counts())
        
        # Numerical parameters summary
        numerical_cols = self.dataset.select_dtypes(include=[np.number]).columns
        print(f"\nNumerical Parameters Summary:")
        print(self.dataset[numerical_cols].describe())
        
        return self.dataset[numerical_cols].describe()
    
    def correlation_analysis(self):
        """Perform correlation analysis"""
        print("\n" + "=" * 60)
        print("CORRELATION ANALYSIS")
        print("=" * 60)
        
        # Select numerical columns
        numerical_cols = self.dataset.select_dtypes(include=[np.number]).columns
        
        # Calculate correlation matrix
        corr_matrix = self.dataset[numerical_cols].corr()
        
        # Plot correlation heatmap
        plt.figure(figsize=(20, 16))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='RdBu_r', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
        plt.title('Correlation Matrix of Welding Parameters and Performance Metrics', 
                 fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig('correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Find high correlations
        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    high_corr.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_val))
        
        print(f"\nHigh Correlations (|r| > 0.7):")
        for var1, var2, corr in sorted(high_corr, key=lambda x: abs(x[2]), reverse=True):
            print(f"{var1} <-> {var2}: {corr:.3f}")
        
        return corr_matrix
    
    def performance_analysis(self):
        """Analyze performance metrics"""
        print("\n" + "=" * 60)
        print("PERFORMANCE METRICS ANALYSIS")
        print("=" * 60)
        
        # Key performance metrics
        perf_metrics = [
            'thermal_cycles_to_failure', 'high_temp_strength_MPa', 'fatigue_cycles_1e6',
            'thermal_performance_W_mK', 'creep_resistance_MPa', 'interfacial_stability'
        ]
        
        # Create subplots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        for i, metric in enumerate(perf_metrics):
            if metric in self.dataset.columns:
                # Distribution
                axes[i].hist(self.dataset[metric], bins=50, alpha=0.7, edgecolor='black')
                axes[i].set_title(f'Distribution of {metric}')
                axes[i].set_xlabel(metric)
                axes[i].set_ylabel('Frequency')
                
                # Add statistics
                mean_val = self.dataset[metric].mean()
                std_val = self.dataset[metric].std()
                axes[i].axvline(mean_val, color='red', linestyle='--', 
                               label=f'Mean: {mean_val:.2f}')
                axes[i].axvline(mean_val + std_val, color='orange', linestyle='--', 
                               label=f'+1σ: {mean_val + std_val:.2f}')
                axes[i].axvline(mean_val - std_val, color='orange', linestyle='--', 
                               label=f'-1σ: {mean_val - std_val:.2f}')
                axes[i].legend()
        
        plt.tight_layout()
        plt.savefig('performance_distributions.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Performance by welding technique
        if 'welding_technique' in self.dataset.columns:
            plt.figure(figsize=(15, 10))
            
            for i, metric in enumerate(perf_metrics):
                if metric in self.dataset.columns:
                    plt.subplot(2, 3, i+1)
                    sns.boxplot(data=self.dataset, x='welding_technique', y=metric)
                    plt.title(f'{metric} by Welding Technique')
                    plt.xticks(rotation=45)
            
            plt.tight_layout()
            plt.savefig('performance_by_technique.png', dpi=300, bbox_inches='tight')
            plt.show()
    
    def material_analysis(self):
        """Analyze material combinations"""
        print("\n" + "=" * 60)
        print("MATERIAL COMBINATION ANALYSIS")
        print("=" * 60)
        
        if 'anode_material' in self.dataset.columns and 'cathode_material' in self.dataset.columns:
            # Create material combination column
            self.dataset['material_combination'] = (
                self.dataset['anode_material'] + '-' + self.dataset['cathode_material']
            )
            
            # Count combinations
            combo_counts = self.dataset['material_combination'].value_counts()
            print("Material Combinations:")
            print(combo_counts)
            
            # Performance by material combination
            perf_metrics = ['thermal_cycles_to_failure', 'high_temp_strength_MPa']
            
            fig, axes = plt.subplots(1, 2, figsize=(15, 6))
            
            for i, metric in enumerate(perf_metrics):
                if metric in self.dataset.columns:
                    # Get top 10 combinations
                    top_combos = combo_counts.head(10).index
                    subset = self.dataset[self.dataset['material_combination'].isin(top_combos)]
                    
                    sns.boxplot(data=subset, x='material_combination', y=metric, ax=axes[i])
                    axes[i].set_title(f'{metric} by Material Combination')
                    axes[i].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig('performance_by_material_combination.png', dpi=300, bbox_inches='tight')
            plt.show()
    
    def process_optimization_analysis(self):
        """Analyze process parameter optimization opportunities"""
        print("\n" + "=" * 60)
        print("PROCESS OPTIMIZATION ANALYSIS")
        print("=" * 60)
        
        # Key process parameters
        process_params = ['power_W', 'force_N', 'time_s', 'amplitude_um', 'speed_mm_s']
        target_metric = 'thermal_cycles_to_failure'
        
        if target_metric in self.dataset.columns:
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            axes = axes.flatten()
            
            for i, param in enumerate(process_params):
                if param in self.dataset.columns and not self.dataset[param].isna().all():
                    # Scatter plot
                    axes[i].scatter(self.dataset[param], self.dataset[target_metric], 
                                   alpha=0.6, s=20)
                    axes[i].set_xlabel(param)
                    axes[i].set_ylabel(target_metric)
                    axes[i].set_title(f'{param} vs {target_metric}')
                    
                    # Add trend line
                    valid_data = self.dataset.dropna(subset=[param, target_metric])
                    if len(valid_data) > 10:
                        z = np.polyfit(valid_data[param], valid_data[target_metric], 1)
                        p = np.poly1d(z)
                        axes[i].plot(valid_data[param], p(valid_data[param]), 
                                   "r--", alpha=0.8)
            
            plt.tight_layout()
            plt.savefig('process_optimization_analysis.png', dpi=300, bbox_inches='tight')
            plt.show()
    
    def interactive_visualization(self):
        """Create interactive visualizations using Plotly"""
        print("\n" + "=" * 60)
        print("INTERACTIVE VISUALIZATIONS")
        print("=" * 60)
        
        # 3D scatter plot of key parameters
        if all(col in self.dataset.columns for col in ['power_W', 'force_N', 'thermal_cycles_to_failure']):
            fig = px.scatter_3d(
                self.dataset, 
                x='power_W', 
                y='force_N', 
                z='thermal_cycles_to_failure',
                color='welding_technique',
                size='weld_strength_MPa',
                hover_data=['anode_material', 'cathode_material', 'surface_finish'],
                title='3D Visualization: Power vs Force vs Thermal Cycles to Failure'
            )
            fig.write_html('interactive_3d_plot.html')
            print("Interactive 3D plot saved as 'interactive_3d_plot.html'")
        
        # Parallel coordinates plot
        if 'welding_technique' in self.dataset.columns:
            # Select key numerical columns for parallel plot
            parallel_cols = ['power_W', 'force_N', 'time_s', 'thermal_cycles_to_failure', 
                           'weld_strength_MPa', 'porosity_percent']
            parallel_cols = [col for col in parallel_cols if col in self.dataset.columns]
            
            if len(parallel_cols) > 3:
                fig = px.parallel_coordinates(
                    self.dataset, 
                    dimensions=parallel_cols,
                    color='welding_technique',
                    title='Parallel Coordinates Plot of Key Parameters'
                )
                fig.write_html('parallel_coordinates_plot.html')
                print("Parallel coordinates plot saved as 'parallel_coordinates_plot.html'")
    
    def generate_ml_insights(self):
        """Generate insights for ML model development"""
        print("\n" + "=" * 60)
        print("ML MODEL DEVELOPMENT INSIGHTS")
        print("=" * 60)
        
        # Feature importance analysis (correlation with target)
        target = 'thermal_cycles_to_failure'
        if target in self.dataset.columns:
            numerical_cols = self.dataset.select_dtypes(include=[np.number]).columns
            correlations = self.dataset[numerical_cols].corr()[target].abs().sort_values(ascending=False)
            
            print("Feature Correlations with Target (thermal_cycles_to_failure):")
            print(correlations.head(10))
            
            # Plot feature importance
            plt.figure(figsize=(10, 8))
            correlations.head(15).plot(kind='barh')
            plt.title('Feature Importance (Correlation with Thermal Cycles to Failure)')
            plt.xlabel('Absolute Correlation')
            plt.tight_layout()
            plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
            plt.show()
        
        # Data quality assessment
        print(f"\nData Quality Assessment:")
        print(f"Missing values: {self.dataset.isnull().sum().sum()}")
        print(f"Duplicate rows: {self.dataset.duplicated().sum()}")
        
        # Outlier detection
        numerical_cols = self.dataset.select_dtypes(include=[np.number]).columns
        outlier_counts = {}
        for col in numerical_cols:
            Q1 = self.dataset[col].quantile(0.25)
            Q3 = self.dataset[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = ((self.dataset[col] < lower_bound) | (self.dataset[col] > upper_bound)).sum()
            outlier_counts[col] = outliers
        
        print(f"\nOutlier counts (IQR method):")
        for col, count in sorted(outlier_counts.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"{col}: {count} outliers")
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("\n" + "=" * 60)
        print("GENERATING COMPREHENSIVE ANALYSIS REPORT")
        print("=" * 60)
        
        # Run all analyses
        self.basic_statistics()
        corr_matrix = self.correlation_analysis()
        self.performance_analysis()
        self.material_analysis()
        self.process_optimization_analysis()
        self.interactive_visualization()
        self.generate_ml_insights()
        
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print("Generated files:")
        print("- correlation_heatmap.png")
        print("- performance_distributions.png")
        print("- performance_by_technique.png")
        print("- performance_by_material_combination.png")
        print("- process_optimization_analysis.png")
        print("- feature_importance.png")
        print("- interactive_3d_plot.html")
        print("- parallel_coordinates_plot.html")

def main():
    """Main function to run analysis"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python dataset_analyzer.py <dataset_file.csv>")
        return
    
    dataset_path = sys.argv[1]
    
    try:
        analyzer = WeldingDatasetAnalyzer(dataset_path)
        analyzer.generate_report()
    except FileNotFoundError:
        print(f"Error: Dataset file '{dataset_path}' not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()