#!/usr/bin/env python3
"""
Dataset Analysis and Visualization Tools for Welding ML Dataset
==============================================================

This script provides comprehensive analysis and visualization capabilities
for the welding dataset, including statistical summaries, correlation analysis,
and interactive plots for understanding the data relationships.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import warnings
warnings.filterwarnings('ignore')

class WeldingDatasetAnalyzer:
    """Comprehensive analysis tools for the welding dataset"""
    
    def __init__(self, data_path: str = "welding_ml_dataset_combined.parquet"):
        """Initialize analyzer with dataset"""
        self.data = pd.read_parquet(data_path)
        self.input_cols = [col for col in self.data.columns if col not in ['sample_id'] and 
                          not any(x in col for x in ['strength', 'resistance', 'width', 'penetration', 
                                                   'porosity', 'hardness', 'haz', 'intermetallic', 
                                                   'quality', 'cycles', 'temp', 'degradation', 
                                                   'retention', 'failure', 'conductivity', 'stress', 
                                                   'stability', 'fatigue'])]
        self.char_cols = [col for col in self.data.columns if any(x in col for x in 
                          ['strength', 'resistance', 'width', 'penetration', 'porosity', 
                           'hardness', 'haz', 'intermetallic', 'quality']) and col != 'sample_id']
        self.perf_cols = [col for col in self.data.columns if any(x in col for x in 
                          ['cycles', 'temp', 'degradation', 'retention', 'failure', 
                           'conductivity', 'stress', 'stability', 'fatigue']) and col != 'sample_id']
        
        print(f"Dataset loaded: {self.data.shape[0]} samples, {self.data.shape[1]} features")
        print(f"Input parameters: {len(self.input_cols)} features")
        print(f"Characterization metrics: {len(self.char_cols)} features")
        print(f"Performance metrics: {len(self.perf_cols)} features")
    
    def basic_statistics(self):
        """Generate basic statistical summary"""
        print("\n" + "="*80)
        print("BASIC STATISTICAL SUMMARY")
        print("="*80)
        
        # Input parameters summary
        print("\nINPUT PARAMETERS:")
        print("-" * 40)
        numeric_inputs = self.data[self.input_cols].select_dtypes(include=[np.number])
        print(numeric_inputs.describe())
        
        # Categorical inputs
        categorical_inputs = self.data[self.input_cols].select_dtypes(include=['object'])
        print(f"\nCategorical Inputs:")
        for col in categorical_inputs.columns:
            print(f"{col}: {self.data[col].value_counts().to_dict()}")
        
        # Characterization metrics
        print(f"\nCHARACTERIZATION METRICS:")
        print("-" * 40)
        print(self.data[self.char_cols].describe())
        
        # Performance metrics
        print(f"\nPERFORMANCE METRICS:")
        print("-" * 40)
        print(self.data[self.perf_cols].describe())
    
    def correlation_analysis(self):
        """Analyze correlations between features"""
        print("\n" + "="*80)
        print("CORRELATION ANALYSIS")
        print("="*80)
        
        # Select numeric columns for correlation
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        corr_matrix = self.data[numeric_cols].corr()
        
        # Find strongest correlations
        print("\nStrongest Positive Correlations (>0.7):")
        strong_pos = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if corr_val > 0.7:
                    strong_pos.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_val))
        
        for col1, col2, corr in sorted(strong_pos, key=lambda x: x[2], reverse=True)[:10]:
            print(f"  {col1} ↔ {col2}: {corr:.3f}")
        
        print("\nStrongest Negative Correlations (<-0.7):")
        strong_neg = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if corr_val < -0.7:
                    strong_neg.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_val))
        
        for col1, col2, corr in sorted(strong_neg, key=lambda x: x[2])[:10]:
            print(f"  {col1} ↔ {col2}: {corr:.3f}")
        
        return corr_matrix
    
    def material_analysis(self):
        """Analyze performance by material combinations"""
        print("\n" + "="*80)
        print("MATERIAL COMBINATION ANALYSIS")
        print("="*80)
        
        # Group by material combinations
        material_groups = self.data.groupby(['anode_material', 'cathode_material']).agg({
            'thermal_cycles_to_failure': ['mean', 'std', 'count'],
            'weld_quality_score': ['mean', 'std'],
            'weld_strength_mpa': ['mean', 'std'],
            'contact_resistance_ohm_m2': ['mean', 'std'],
            'max_operating_temp_c': ['mean', 'std']
        }).round(2)
        
        print("Performance by Material Combination:")
        print(material_groups)
        
        # Best performing combinations
        best_combinations = self.data.groupby(['anode_material', 'cathode_material'])['thermal_cycles_to_failure'].mean().sort_values(ascending=False)
        print(f"\nTop 5 Material Combinations (by thermal cycles):")
        for (anode, cathode), cycles in best_combinations.head().items():
            print(f"  {anode} + {cathode}: {cycles:.0f} cycles")
        
        return material_groups
    
    def technique_analysis(self):
        """Analyze performance by welding technique"""
        print("\n" + "="*80)
        print("WELDING TECHNIQUE ANALYSIS")
        print("="*80)
        
        technique_groups = self.data.groupby('welding_technique').agg({
            'thermal_cycles_to_failure': ['mean', 'std', 'count'],
            'weld_quality_score': ['mean', 'std'],
            'weld_strength_mpa': ['mean', 'std'],
            'contact_resistance_ohm_m2': ['mean', 'std'],
            'max_operating_temp_c': ['mean', 'std']
        }).round(2)
        
        print("Performance by Welding Technique:")
        print(technique_groups)
        
        # Technique comparison
        print(f"\nTechnique Ranking (by average thermal cycles):")
        technique_ranking = self.data.groupby('welding_technique')['thermal_cycles_to_failure'].mean().sort_values(ascending=False)
        for i, (technique, cycles) in enumerate(technique_ranking.items(), 1):
            print(f"  {i}. {technique}: {cycles:.0f} cycles")
        
        return technique_groups
    
    def failure_mode_analysis(self):
        """Analyze failure modes and their characteristics"""
        print("\n" + "="*80)
        print("FAILURE MODE ANALYSIS")
        print("="*80)
        
        failure_analysis = self.data.groupby('failure_mode').agg({
            'thermal_cycles_to_failure': ['mean', 'std', 'count'],
            'weld_quality_score': ['mean', 'std'],
            'weld_strength_mpa': ['mean', 'std'],
            'porosity_percent': ['mean', 'std'],
            'contact_resistance_ohm_m2': ['mean', 'std']
        }).round(2)
        
        print("Characteristics by Failure Mode:")
        print(failure_analysis)
        
        # Failure mode distribution
        failure_dist = self.data['failure_mode'].value_counts()
        print(f"\nFailure Mode Distribution:")
        for mode, count in failure_dist.items():
            percentage = (count / len(self.data)) * 100
            print(f"  {mode}: {count} samples ({percentage:.1f}%)")
        
        return failure_analysis
    
    def create_visualizations(self):
        """Create comprehensive visualizations"""
        print("\n" + "="*80)
        print("CREATING VISUALIZATIONS")
        print("="*80)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. Material combination heatmap
        self._plot_material_heatmap()
        
        # 2. Technique comparison
        self._plot_technique_comparison()
        
        # 3. Correlation heatmap
        self._plot_correlation_heatmap()
        
        # 4. Performance distribution
        self._plot_performance_distributions()
        
        # 5. Failure mode analysis
        self._plot_failure_analysis()
        
        # 6. Interactive 3D scatter plot
        self._create_interactive_plot()
        
        print("All visualizations saved to 'welding_analysis_plots/' directory")
    
    def _plot_material_heatmap(self):
        """Plot material combination performance heatmap"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Pivot tables for different metrics
        metrics = ['thermal_cycles_to_failure', 'weld_quality_score', 'weld_strength_mpa', 'max_operating_temp_c']
        titles = ['Thermal Cycles', 'Quality Score', 'Weld Strength (MPa)', 'Max Temperature (°C)']
        
        for i, (metric, title) in enumerate(zip(metrics, titles)):
            ax = axes[i//2, i%2]
            pivot = self.data.pivot_table(values=metric, index='anode_material', 
                                        columns='cathode_material', aggfunc='mean')
            sns.heatmap(pivot, annot=True, fmt='.0f', cmap='viridis', ax=ax)
            ax.set_title(f'{title} by Material Combination')
            ax.set_xlabel('Cathode Material')
            ax.set_ylabel('Anode Material')
        
        plt.tight_layout()
        plt.savefig('welding_analysis_plots/material_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_technique_comparison(self):
        """Plot welding technique comparison"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        techniques = self.data['welding_technique'].unique()
        
        # Box plots for different metrics
        metrics = ['thermal_cycles_to_failure', 'weld_quality_score', 'weld_strength_mpa', 'contact_resistance_ohm_m2']
        titles = ['Thermal Cycles', 'Quality Score', 'Weld Strength (MPa)', 'Contact Resistance (Ω·m²)']
        
        for i, (metric, title) in enumerate(zip(metrics, titles)):
            ax = axes[i//2, i%2]
            sns.boxplot(data=self.data, x='welding_technique', y=metric, ax=ax)
            ax.set_title(f'{title} by Welding Technique')
            ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('welding_analysis_plots/technique_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_correlation_heatmap(self):
        """Plot correlation heatmap"""
        plt.figure(figsize=(20, 16))
        
        # Select key numeric columns
        key_cols = ['power_w', 'time_s', 'force_n', 'preheat_temp_c', 'tab_thickness_um',
                   'weld_strength_mpa', 'contact_resistance_ohm_m2', 'porosity_percent',
                   'weld_quality_score', 'thermal_cycles_to_failure', 'max_operating_temp_c',
                   'strength_retention_percent', 'material_compatibility']
        
        corr_data = self.data[key_cols].corr()
        
        mask = np.triu(np.ones_like(corr_data, dtype=bool))
        sns.heatmap(corr_data, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                   square=True, cbar_kws={"shrink": .8})
        plt.title('Feature Correlation Heatmap', fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig('welding_analysis_plots/correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_performance_distributions(self):
        """Plot performance metric distributions"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        perf_metrics = ['thermal_cycles_to_failure', 'weld_quality_score', 'weld_strength_mpa',
                       'max_operating_temp_c', 'strength_retention_percent', 'porosity_percent']
        titles = ['Thermal Cycles', 'Quality Score', 'Weld Strength (MPa)', 
                 'Max Temperature (°C)', 'Strength Retention (%)', 'Porosity (%)']
        
        for i, (metric, title) in enumerate(zip(perf_metrics, titles)):
            ax = axes[i//3, i%3]
            sns.histplot(data=self.data, x=metric, kde=True, ax=ax)
            ax.set_title(f'Distribution of {title}')
            ax.set_xlabel(title)
        
        plt.tight_layout()
        plt.savefig('welding_analysis_plots/performance_distributions.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_failure_analysis(self):
        """Plot failure mode analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Failure mode distribution
        ax1 = axes[0, 0]
        failure_counts = self.data['failure_mode'].value_counts()
        ax1.pie(failure_counts.values, labels=failure_counts.index, autopct='%1.1f%%')
        ax1.set_title('Failure Mode Distribution')
        
        # Thermal cycles by failure mode
        ax2 = axes[0, 1]
        sns.boxplot(data=self.data, x='failure_mode', y='thermal_cycles_to_failure', ax=ax2)
        ax2.set_title('Thermal Cycles by Failure Mode')
        ax2.tick_params(axis='x', rotation=45)
        
        # Quality score by failure mode
        ax3 = axes[1, 0]
        sns.violinplot(data=self.data, x='failure_mode', y='weld_quality_score', ax=ax3)
        ax3.set_title('Quality Score by Failure Mode')
        ax3.tick_params(axis='x', rotation=45)
        
        # Porosity by failure mode
        ax4 = axes[1, 1]
        sns.boxplot(data=self.data, x='failure_mode', y='porosity_percent', ax=ax4)
        ax4.set_title('Porosity by Failure Mode')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('welding_analysis_plots/failure_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_interactive_plot(self):
        """Create interactive 3D scatter plot"""
        # Create interactive plot using plotly
        fig = px.scatter_3d(
            self.data, 
            x='power_w', 
            y='time_s', 
            z='thermal_cycles_to_failure',
            color='welding_technique',
            size='weld_quality_score',
            hover_data=['anode_material', 'cathode_material', 'failure_mode'],
            title='Interactive 3D Plot: Power vs Time vs Thermal Cycles',
            labels={'power_w': 'Power (W)', 'time_s': 'Time (s)', 'thermal_cycles_to_failure': 'Thermal Cycles'}
        )
        
        fig.write_html('welding_analysis_plots/interactive_3d_plot.html')
        print("Interactive 3D plot saved as 'welding_analysis_plots/interactive_3d_plot.html'")
    
    def generate_ml_insights(self):
        """Generate insights for ML model development"""
        print("\n" + "="*80)
        print("ML MODEL DEVELOPMENT INSIGHTS")
        print("="*80)
        
        # Feature importance analysis
        print("\n1. FEATURE IMPORTANCE ANALYSIS:")
        print("-" * 40)
        
        # Calculate correlations with target variable
        target = 'thermal_cycles_to_failure'
        numeric_data = self.data.select_dtypes(include=[np.number])
        correlations = numeric_data.corr()[target].abs().sort_values(ascending=False)
        
        print("Top 10 features most correlated with thermal cycles:")
        for i, (feature, corr) in enumerate(correlations.head(11).items(), 1):
            if feature != target:
                print(f"  {i}. {feature}: {corr:.3f}")
        
        # Data quality assessment
        print("\n2. DATA QUALITY ASSESSMENT:")
        print("-" * 40)
        
        missing_data = self.data.isnull().sum()
        if missing_data.sum() > 0:
            print("Missing values found:")
            for col, missing in missing_data[missing_data > 0].items():
                print(f"  {col}: {missing} ({missing/len(self.data)*100:.1f}%)")
        else:
            print("No missing values found - excellent data quality!")
        
        # Outlier analysis
        print("\n3. OUTLIER ANALYSIS:")
        print("-" * 40)
        
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        outlier_counts = {}
        
        for col in numeric_cols:
            Q1 = self.data[col].quantile(0.25)
            Q3 = self.data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = ((self.data[col] < lower_bound) | (self.data[col] > upper_bound)).sum()
            outlier_counts[col] = outliers
        
        high_outlier_cols = {k: v for k, v in outlier_counts.items() if v > len(self.data) * 0.05}
        if high_outlier_cols:
            print("Features with >5% outliers:")
            for col, count in high_outlier_cols.items():
                print(f"  {col}: {count} outliers ({count/len(self.data)*100:.1f}%)")
        else:
            print("No features have excessive outliers - good data distribution!")
        
        # Class balance for categorical targets
        print("\n4. TARGET VARIABLE ANALYSIS:")
        print("-" * 40)
        
        print(f"Thermal cycles range: {self.data[target].min():.0f} - {self.data[target].max():.0f}")
        print(f"Mean: {self.data[target].mean():.0f}, Std: {self.data[target].std():.0f}")
        
        # Failure mode distribution
        print(f"\nFailure mode distribution:")
        for mode, count in self.data['failure_mode'].value_counts().items():
            print(f"  {mode}: {count} ({count/len(self.data)*100:.1f}%)")
        
        return correlations
    
    def export_analysis_report(self):
        """Export comprehensive analysis report"""
        print("\n" + "="*80)
        print("EXPORTING ANALYSIS REPORT")
        print("="*80)
        
        # Create analysis directory
        import os
        os.makedirs('welding_analysis_plots', exist_ok=True)
        
        # Generate all analyses
        self.basic_statistics()
        corr_matrix = self.correlation_analysis()
        material_analysis = self.material_analysis()
        technique_analysis = self.technique_analysis()
        failure_analysis = self.failure_mode_analysis()
        correlations = self.generate_ml_insights()
        
        # Create visualizations
        self.create_visualizations()
        
        # Save analysis results
        analysis_results = {
            'dataset_info': {
                'total_samples': len(self.data),
                'total_features': len(self.data.columns),
                'input_features': len(self.input_cols),
                'characterization_features': len(self.char_cols),
                'performance_features': len(self.perf_cols)
            },
            'correlation_analysis': corr_matrix.to_dict(),
            'material_analysis': {str(k): {str(k2): v2 for k2, v2 in v.items()} for k, v in material_analysis.to_dict().items()},
            'technique_analysis': {str(k): {str(k2): v2 for k2, v2 in v.items()} for k, v in technique_analysis.to_dict().items()},
            'failure_analysis': {str(k): {str(k2): v2 for k2, v2 in v.items()} for k, v in failure_analysis.to_dict().items()},
            'feature_correlations': correlations.to_dict(),
            'data_quality': {
                'missing_values': self.data.isnull().sum().to_dict(),
                'outlier_analysis': {col: ((self.data[col] < self.data[col].quantile(0.25) - 1.5 * (self.data[col].quantile(0.75) - self.data[col].quantile(0.25))) | 
                                    (self.data[col] > self.data[col].quantile(0.75) + 1.5 * (self.data[col].quantile(0.75) - self.data[col].quantile(0.25)))).sum() 
                                    for col in self.data.select_dtypes(include=[np.number]).columns}
            }
        }
        
        with open('welding_analysis_plots/analysis_report.json', 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        print("\nAnalysis complete! Files saved:")
        print("- welding_analysis_plots/analysis_report.json")
        print("- welding_analysis_plots/material_heatmap.png")
        print("- welding_analysis_plots/technique_comparison.png")
        print("- welding_analysis_plots/correlation_heatmap.png")
        print("- welding_analysis_plots/performance_distributions.png")
        print("- welding_analysis_plots/failure_analysis.png")
        print("- welding_analysis_plots/interactive_3d_plot.html")

def main():
    """Main function to run complete analysis"""
    print("=" * 80)
    print("WELDING DATASET ANALYSIS TOOL")
    print("=" * 80)
    
    # Initialize analyzer
    analyzer = WeldingDatasetAnalyzer()
    
    # Run complete analysis
    analyzer.export_analysis_report()
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    main()