#!/usr/bin/env python3
"""
Advanced Dataset Analysis and Visualization Tools for Welding Parameters Dataset
"""

import pandas as pd
import numpy as np
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
    """Advanced analysis tools for welding parameters dataset"""
    
    def __init__(self, input_df, char_df, perf_df):
        self.input_df = input_df
        self.char_df = char_df
        self.perf_df = perf_df
        self.combined_df = input_df.merge(char_df, on='sample_id').merge(perf_df, on='sample_id')
        
    def generate_correlation_analysis(self):
        """Generate comprehensive correlation analysis"""
        print("Generating correlation analysis...")
        
        # Select numeric columns for correlation
        numeric_cols = self.combined_df.select_dtypes(include=[np.number]).columns
        correlation_matrix = self.combined_df[numeric_cols].corr()
        
        # Create correlation heatmap
        plt.figure(figsize=(20, 16))
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
        plt.title('Welding Parameters Correlation Matrix', fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig('correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Find strongest correlations
        corr_pairs = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_val = correlation_matrix.iloc[i, j]
                if abs(corr_val) > 0.5:  # Strong correlation threshold
                    corr_pairs.append({
                        'feature1': correlation_matrix.columns[i],
                        'feature2': correlation_matrix.columns[j],
                        'correlation': corr_val
                    })
        
        corr_df = pd.DataFrame(corr_pairs).sort_values('correlation', key=abs, ascending=False)
        corr_df.to_csv('strong_correlations.csv', index=False)
        
        return correlation_matrix, corr_df
    
    def generate_material_analysis(self):
        """Analyze material-specific performance"""
        print("Generating material analysis...")
        
        # Material performance comparison
        material_perf = self.combined_df.groupby(['anode_material', 'cathode_material']).agg({
            'bond_quality_index': ['mean', 'std'],
            'performance_score': ['mean', 'std'],
            'fatigue_life_cycles': ['mean', 'std'],
            'reliability_95_percent': ['mean', 'std']
        }).round(2)
        
        material_perf.columns = ['_'.join(col).strip() for col in material_perf.columns]
        material_perf.to_csv('material_performance_analysis.csv')
        
        # Create material performance visualization
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Bond quality by material combination
        material_quality = self.combined_df.groupby(['anode_material', 'cathode_material'])['bond_quality_index'].mean().unstack()
        sns.heatmap(material_quality, annot=True, cmap='viridis', ax=axes[0,0])
        axes[0,0].set_title('Average Bond Quality by Material Combination')
        
        # Performance score distribution
        self.combined_df.boxplot(column='performance_score', by='anode_material', ax=axes[0,1])
        axes[0,1].set_title('Performance Score by Anode Material')
        
        # Fatigue life by welding technique
        self.combined_df.boxplot(column='fatigue_life_cycles', by='welding_technique', ax=axes[1,0])
        axes[1,0].set_title('Fatigue Life by Welding Technique')
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # Reliability by surface finish
        surface_reliability = self.combined_df.groupby('surface_finish')['reliability_95_percent'].mean().sort_values(ascending=False)
        surface_reliability.plot(kind='bar', ax=axes[1,1])
        axes[1,1].set_title('Reliability by Surface Finish')
        axes[1,1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('material_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return material_perf
    
    def generate_process_optimization_analysis(self):
        """Analyze process parameter optimization opportunities"""
        print("Generating process optimization analysis...")
        
        # Process parameter effects on quality
        process_effects = {}
        
        for technique in self.combined_df['welding_technique'].unique():
            tech_data = self.combined_df[self.combined_df['welding_technique'] == technique]
            
            if technique == 'Ultrasonic_Welding':
                params = ['power_w', 'amplitude_um', 'force_n', 'time_s']
            elif technique == 'Laser_Welding':
                params = ['power_w', 'speed_mm_s', 'pulse_frequency_hz', 'pulse_duration_ms']
            elif technique == 'Resistance_Spot_Welding':
                params = ['current_a', 'voltage_v', 'force_n', 'time_s']
            elif technique == 'Friction_Stir_Welding':
                params = ['rotation_speed_rpm', 'travel_speed_mm_s', 'force_n', 'tool_diameter_mm']
            else:
                continue
            
            # Calculate correlations with quality metrics
            tech_effects = {}
            for param in params:
                if param in tech_data.columns:
                    param_data = tech_data[param].dropna()
                    if len(param_data) > 10:  # Sufficient data
                        quality_corr = param_data.corr(tech_data.loc[param_data.index, 'bond_quality_index'])
                        perf_corr = param_data.corr(tech_data.loc[param_data.index, 'performance_score'])
                        tech_effects[param] = {
                            'quality_correlation': quality_corr,
                            'performance_correlation': perf_corr
                        }
            
            process_effects[technique] = tech_effects
        
        # Create process optimization visualization
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        for i, (technique, effects) in enumerate(process_effects.items()):
            if i >= 4:
                break
                
            ax = axes[i//2, i%2]
            
            params = list(effects.keys())
            quality_corrs = [effects[p]['quality_correlation'] for p in params]
            perf_corrs = [effects[p]['performance_correlation'] for p in params]
            
            x = np.arange(len(params))
            width = 0.35
            
            ax.bar(x - width/2, quality_corrs, width, label='Quality Correlation', alpha=0.8)
            ax.bar(x + width/2, perf_corrs, width, label='Performance Correlation', alpha=0.8)
            
            ax.set_xlabel('Parameters')
            ax.set_ylabel('Correlation Coefficient')
            ax.set_title(f'{technique} Parameter Effects')
            ax.set_xticks(x)
            ax.set_xticklabels(params, rotation=45)
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('process_optimization_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return process_effects
    
    def generate_ml_readiness_report(self):
        """Generate ML readiness and data quality report"""
        print("Generating ML readiness report...")
        
        report = {
            'data_quality': {
                'total_samples': len(self.combined_df),
                'missing_values': self.combined_df.isnull().sum().sum(),
                'missing_percentage': (self.combined_df.isnull().sum().sum() / (len(self.combined_df) * len(self.combined_df.columns))) * 100,
                'duplicate_rows': self.combined_df.duplicated().sum(),
                'numeric_features': len(self.combined_df.select_dtypes(include=[np.number]).columns),
                'categorical_features': len(self.combined_df.select_dtypes(include=['object']).columns)
            },
            'target_variable_analysis': {
                'bond_quality_distribution': self.combined_df['bond_quality_index'].describe().to_dict(),
                'performance_score_distribution': self.combined_df['performance_score'].describe().to_dict(),
                'class_balance': {
                    'quality_class': self.combined_df['weld_quality_class'].value_counts().to_dict(),
                    'pass_fail': self.combined_df['pass_fail'].value_counts().to_dict()
                }
            },
            'feature_importance_analysis': self._calculate_feature_importance(),
            'recommendations': self._generate_ml_recommendations()
        }
        
        # Save report
        import json
        with open('ml_readiness_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return report
    
    def _calculate_feature_importance(self):
        """Calculate preliminary feature importance"""
        numeric_cols = self.combined_df.select_dtypes(include=[np.number]).columns
        target_cols = ['bond_quality_index', 'performance_score']
        
        importance_scores = {}
        
        for target in target_cols:
            if target in numeric_cols:
                correlations = self.combined_df[numeric_cols].corr()[target].abs().sort_values(ascending=False)
                importance_scores[target] = correlations.head(20).to_dict()
        
        return importance_scores
    
    def _generate_ml_recommendations(self):
        """Generate ML modeling recommendations"""
        recommendations = []
        
        # Data quality recommendations
        missing_pct = (self.combined_df.isnull().sum().sum() / (len(self.combined_df) * len(self.combined_df.columns))) * 100
        if missing_pct > 5:
            recommendations.append("Consider imputation strategies for missing values")
        
        # Feature engineering recommendations
        recommendations.append("Consider creating interaction features between process parameters")
        recommendations.append("Normalize/scale numerical features before training")
        recommendations.append("Consider polynomial features for non-linear relationships")
        
        # Model recommendations
        recommendations.append("Try ensemble methods (Random Forest, XGBoost) for non-linear relationships")
        recommendations.append("Use neural networks for complex material-property interactions")
        recommendations.append("Consider multi-output regression for simultaneous quality prediction")
        
        # Validation recommendations
        recommendations.append("Use stratified sampling to maintain material distribution")
        recommendations.append("Implement time-series cross-validation for temporal data")
        recommendations.append("Consider domain-specific validation metrics")
        
        return recommendations
    
    def generate_interactive_dashboard(self):
        """Generate interactive Plotly dashboard"""
        print("Generating interactive dashboard...")
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Material Performance', 'Process Parameters', 
                          'Quality Distribution', 'Performance vs Quality',
                          'Fatigue Life Analysis', 'Failure Mode Distribution'),
            specs=[[{"type": "heatmap"}, {"type": "scatter"}],
                   [{"type": "histogram"}, {"type": "scatter"}],
                   [{"type": "box"}, {"type": "pie"}]]
        )
        
        # Material performance heatmap
        material_quality = self.combined_df.groupby(['anode_material', 'cathode_material'])['bond_quality_index'].mean().unstack()
        fig.add_trace(
            go.Heatmap(z=material_quality.values, 
                      x=material_quality.columns, 
                      y=material_quality.index,
                      colorscale='Viridis'),
            row=1, col=1
        )
        
        # Process parameters scatter
        fig.add_trace(
            go.Scatter(x=self.combined_df['power_w'], 
                      y=self.combined_df['bond_quality_index'],
                      mode='markers',
                      marker=dict(color=self.combined_df['performance_score'],
                                colorscale='Viridis',
                                showscale=True)),
            row=1, col=2
        )
        
        # Quality distribution
        fig.add_trace(
            go.Histogram(x=self.combined_df['bond_quality_index'], nbinsx=30),
            row=2, col=1
        )
        
        # Performance vs Quality
        fig.add_trace(
            go.Scatter(x=self.combined_df['bond_quality_index'], 
                      y=self.combined_df['performance_score'],
                      mode='markers',
                      marker=dict(color=self.combined_df['fatigue_life_cycles'],
                                colorscale='Plasma')),
            row=2, col=2
        )
        
        # Fatigue life by technique
        for technique in self.combined_df['welding_technique'].unique():
            tech_data = self.combined_df[self.combined_df['welding_technique'] == technique]
            fig.add_trace(
                go.Box(y=tech_data['fatigue_life_cycles'], name=technique),
                row=3, col=1
            )
        
        # Failure mode distribution
        failure_counts = self.combined_df['failure_mode'].value_counts()
        fig.add_trace(
            go.Pie(labels=failure_counts.index, values=failure_counts.values),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text="Welding Parameters Dataset Interactive Dashboard",
            showlegend=True,
            height=1200
        )
        
        # Save interactive dashboard
        fig.write_html("welding_dataset_dashboard.html")
        
        return fig

def main():
    """Main analysis function"""
    print("Loading dataset for analysis...")
    
    # Load the generated dataset
    input_df = pd.read_csv('welding_dataset_input_parameters.csv')
    char_df = pd.read_csv('welding_dataset_characterization_metrics.csv')
    perf_df = pd.read_csv('welding_dataset_performance_metrics.csv')
    
    # Initialize analyzer
    analyzer = WeldingDatasetAnalyzer(input_df, char_df, perf_df)
    
    print("Running comprehensive analysis...")
    
    # Run all analyses
    correlation_matrix, corr_df = analyzer.generate_correlation_analysis()
    material_perf = analyzer.generate_material_analysis()
    process_effects = analyzer.generate_process_optimization_analysis()
    ml_report = analyzer.generate_ml_readiness_report()
    dashboard = analyzer.generate_interactive_dashboard()
    
    print("\nAnalysis complete! Generated files:")
    print("- correlation_heatmap.png")
    print("- strong_correlations.csv")
    print("- material_performance_analysis.csv")
    print("- material_analysis.png")
    print("- process_optimization_analysis.png")
    print("- ml_readiness_report.json")
    print("- welding_dataset_dashboard.html")

if __name__ == "__main__":
    main()