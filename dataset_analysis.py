import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class WeldingDatasetAnalyzer:
    def __init__(self, dataset_path='welding_dataset.csv'):
        """Initialize the dataset analyzer"""
        self.dataset = pd.read_csv(dataset_path)
        self.scaler = StandardScaler()
        
    def basic_statistics(self):
        """Generate basic statistics and data quality report"""
        print("=== Dataset Basic Statistics ===")
        print(f"Dataset shape: {self.dataset.shape}")
        print(f"Features: {len(self.dataset.columns)}")
        print(f"Samples: {len(self.dataset)}")
        
        print("\n=== Data Quality Report ===")
        print("Missing values:")
        missing = self.dataset.isnull().sum()
        print(missing[missing > 0])
        
        print("\n=== Feature Categories ===")
        input_params = [col for col in self.dataset.columns if col in [
            'anode_material', 'cathode_material', 'tab_thickness_um', 'surface_finish',
            'welding_technique', 'power_w', 'amplitude_um', 'force_n', 'time_ms',
            'speed_mm_s', 'pulse_frequency_hz', 'preheat_temperature_c',
            'material_compatibility', 'thermal_mismatch', 'electrical_mismatch'
        ]]
        
        quality_metrics = [col for col in self.dataset.columns if col in [
            'weld_strength_mpa', 'contact_resistance_mohm', 'penetration_depth_um',
            'weld_width_um', 'porosity_percent', 'microhardness_hv'
        ]]
        
        performance_metrics = [col for col in self.dataset.columns if col in [
            'thermal_cycles_to_failure', 'resistance_degradation_rate_percent_per_cycle',
            'mechanical_degradation_rate_percent_per_cycle', 'temperature_coefficient_resistance_ppm_per_c',
            'creep_rate_um_per_cycle'
        ]]
        
        print(f"Input Parameters: {len(input_params)}")
        print(f"Quality Metrics: {len(quality_metrics)}")
        print(f"Performance Metrics: {len(performance_metrics)}")
        
        return input_params, quality_metrics, performance_metrics
    
    def correlation_analysis(self):
        """Perform comprehensive correlation analysis"""
        print("\n=== Correlation Analysis ===")
        
        # Select numeric columns for correlation
        numeric_cols = self.dataset.select_dtypes(include=[np.number]).columns
        corr_matrix = self.dataset[numeric_cols].corr()
        
        # Find strongest correlations
        corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.5:  # Strong correlation threshold
                    corr_pairs.append({
                        'feature1': corr_matrix.columns[i],
                        'feature2': corr_matrix.columns[j],
                        'correlation': corr_val
                    })
        
        # Sort by absolute correlation
        corr_pairs.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        print("Strongest Correlations (|r| > 0.5):")
        for pair in corr_pairs[:10]:
            print(f"  {pair['feature1']} <-> {pair['feature2']}: {pair['correlation']:.3f}")
        
        return corr_matrix, corr_pairs
    
    def material_analysis(self):
        """Analyze material combinations and their effects"""
        print("\n=== Material Analysis ===")
        
        # Material combination analysis
        material_combinations = self.dataset.groupby(['anode_material', 'cathode_material']).agg({
            'weld_strength_mpa': ['mean', 'std', 'count'],
            'thermal_cycles_to_failure': ['mean', 'std'],
            'weld_quality_score': ['mean', 'std']
        }).round(3)
        
        print("Material Combination Performance:")
        print(material_combinations)
        
        # Best performing combinations
        best_combinations = material_combinations.sort_values(
            ('weld_quality_score', 'mean'), ascending=False
        ).head(5)
        
        print("\nTop 5 Material Combinations by Quality Score:")
        print(best_combinations)
        
        return material_combinations
    
    def welding_technique_analysis(self):
        """Analyze welding technique performance"""
        print("\n=== Welding Technique Analysis ===")
        
        technique_performance = self.dataset.groupby('welding_technique').agg({
            'weld_strength_mpa': ['mean', 'std'],
            'contact_resistance_mohm': ['mean', 'std'],
            'porosity_percent': ['mean', 'std'],
            'thermal_cycles_to_failure': ['mean', 'std'],
            'weld_quality_score': ['mean', 'std'],
            'process_efficiency': ['mean', 'std']
        }).round(3)
        
        print("Welding Technique Performance:")
        print(technique_performance)
        
        # Technique ranking
        technique_ranking = technique_performance.sort_values(
            ('weld_quality_score', 'mean'), ascending=False
        )
        
        print("\nTechnique Ranking by Quality Score:")
        for i, (technique, row) in enumerate(technique_ranking.iterrows(), 1):
            print(f"{i}. {technique}: {row[('weld_quality_score', 'mean')]:.3f}")
        
        return technique_performance
    
    def process_parameter_optimization(self):
        """Analyze process parameter optimization opportunities"""
        print("\n=== Process Parameter Optimization Analysis ===")
        
        # Power optimization
        power_analysis = self.dataset.groupby(pd.cut(self.dataset['power_w'], bins=5)).agg({
            'weld_strength_mpa': 'mean',
            'porosity_percent': 'mean',
            'weld_quality_score': 'mean',
            'process_efficiency': 'mean'
        }).round(3)
        
        print("Power Level Analysis:")
        print(power_analysis)
        
        # Force optimization
        force_analysis = self.dataset.groupby(pd.cut(self.dataset['force_n'], bins=5)).agg({
            'weld_strength_mpa': 'mean',
            'contact_resistance_mohm': 'mean',
            'weld_quality_score': 'mean'
        }).round(3)
        
        print("\nForce Level Analysis:")
        print(force_analysis)
        
        # Time optimization
        time_analysis = self.dataset.groupby(pd.cut(self.dataset['time_ms'], bins=5)).agg({
            'weld_strength_mpa': 'mean',
            'porosity_percent': 'mean',
            'weld_quality_score': 'mean'
        }).round(3)
        
        print("\nTime Level Analysis:")
        print(time_analysis)
        
        return power_analysis, force_analysis, time_analysis
    
    def quality_vs_performance_analysis(self):
        """Analyze relationship between quality metrics and performance metrics"""
        print("\n=== Quality vs Performance Analysis ===")
        
        # Quality-Performance correlation
        quality_cols = ['weld_strength_mpa', 'contact_resistance_mohm', 'porosity_percent', 'microhardness_hv']
        performance_cols = ['thermal_cycles_to_failure', 'resistance_degradation_rate_percent_per_cycle', 
                           'mechanical_degradation_rate_percent_per_cycle']
        
        quality_perf_corr = self.dataset[quality_cols + performance_cols].corr()
        quality_perf_corr = quality_perf_corr.loc[quality_cols, performance_cols]
        
        print("Quality-Performance Correlations:")
        print(quality_perf_corr.round(3))
        
        # Performance prediction from quality
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score
        
        X_quality = self.dataset[quality_cols]
        y_performance = self.dataset['thermal_cycles_to_failure']
        
        lr = LinearRegression()
        lr.fit(X_quality, y_performance)
        y_pred = lr.predict(X_quality)
        r2 = r2_score(y_performance, y_pred)
        
        print(f"\nPerformance Prediction from Quality (R²): {r2:.3f}")
        
        return quality_perf_corr
    
    def create_interactive_visualizations(self):
        """Create interactive visualizations using Plotly"""
        print("\n=== Creating Interactive Visualizations ===")
        
        # 1. Material Performance Scatter Plot
        fig1 = px.scatter(
            self.dataset, 
            x='weld_strength_mpa', 
            y='thermal_cycles_to_failure',
            color='welding_technique',
            size='weld_quality_score',
            hover_data=['anode_material', 'cathode_material', 'power_w', 'force_n'],
            title='Weld Strength vs Thermal Cycles by Technique'
        )
        fig1.write_html('interactive_material_performance.html')
        
        # 2. Process Parameter Effects
        fig2 = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Power vs Strength', 'Force vs Resistance', 
                          'Time vs Porosity', 'Power vs Quality Score'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Power vs Strength
        fig2.add_trace(
            go.Scatter(x=self.dataset['power_w'], y=self.dataset['weld_strength_mpa'],
                      mode='markers', name='Power vs Strength', marker=dict(size=4)),
            row=1, col=1
        )
        
        # Force vs Resistance
        fig2.add_trace(
            go.Scatter(x=self.dataset['force_n'], y=self.dataset['contact_resistance_mohm'],
                      mode='markers', name='Force vs Resistance', marker=dict(size=4)),
            row=1, col=2
        )
        
        # Time vs Porosity
        fig2.add_trace(
            go.Scatter(x=self.dataset['time_ms'], y=self.dataset['porosity_percent'],
                      mode='markers', name='Time vs Porosity', marker=dict(size=4)),
            row=2, col=1
        )
        
        # Power vs Quality Score
        fig2.add_trace(
            go.Scatter(x=self.dataset['power_w'], y=self.dataset['weld_quality_score'],
                      mode='markers', name='Power vs Quality', marker=dict(size=4)),
            row=2, col=2
        )
        
        fig2.update_layout(height=800, title_text="Process Parameter Effects")
        fig2.write_html('interactive_process_parameters.html')
        
        # 3. Material Combination Heatmap
        material_pivot = self.dataset.pivot_table(
            values='weld_quality_score', 
            index='anode_material', 
            columns='cathode_material', 
            aggfunc='mean'
        )
        
        fig3 = px.imshow(
            material_pivot.values,
            x=material_pivot.columns,
            y=material_pivot.index,
            color_continuous_scale='RdYlBu_r',
            title='Material Combination Quality Score Heatmap'
        )
        fig3.write_html('interactive_material_heatmap.html')
        
        print("Interactive visualizations saved:")
        print("- interactive_material_performance.html")
        print("- interactive_process_parameters.html")
        print("- interactive_material_heatmap.html")
    
    def generate_optimization_recommendations(self):
        """Generate optimization recommendations based on analysis"""
        print("\n=== Optimization Recommendations ===")
        
        # Find optimal parameter ranges
        high_quality = self.dataset[self.dataset['weld_quality_score'] > 0.8]
        
        if len(high_quality) > 0:
            print("High-Quality Weld Parameter Ranges:")
            print(f"  Power: {high_quality['power_w'].min():.0f} - {high_quality['power_w'].max():.0f} W")
            print(f"  Force: {high_quality['force_n'].min():.0f} - {high_quality['force_n'].max():.0f} N")
            print(f"  Time: {high_quality['time_ms'].min():.0f} - {high_quality['time_ms'].max():.0f} ms")
            print(f"  Amplitude: {high_quality['amplitude_um'].min():.0f} - {high_quality['amplitude_um'].max():.0f} µm")
            
            print(f"\nBest Material Combinations for High Quality:")
            best_materials = high_quality.groupby(['anode_material', 'cathode_material'])['weld_quality_score'].mean().sort_values(ascending=False).head(3)
            for (anode, cathode), score in best_materials.items():
                print(f"  {anode}-{cathode}: {score:.3f}")
            
            print(f"\nBest Welding Techniques for High Quality:")
            best_techniques = high_quality.groupby('welding_technique')['weld_quality_score'].mean().sort_values(ascending=False)
            for technique, score in best_techniques.items():
                print(f"  {technique}: {score:.3f}")
        
        # Process efficiency recommendations
        efficient_welds = self.dataset[self.dataset['process_efficiency'] > 0.7]
        
        if len(efficient_welds) > 0:
            print(f"\nProcess Efficiency Recommendations:")
            print(f"  Average Power for Efficiency: {efficient_welds['power_w'].mean():.0f} W")
            print(f"  Average Force for Efficiency: {efficient_welds['force_n'].mean():.0f} N")
            print(f"  Average Time for Efficiency: {efficient_welds['time_ms'].mean():.0f} ms")
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive analysis report"""
        print("=== COMPREHENSIVE WELDING DATASET ANALYSIS REPORT ===")
        
        # Basic statistics
        input_params, quality_metrics, performance_metrics = self.basic_statistics()
        
        # Correlation analysis
        corr_matrix, corr_pairs = self.correlation_analysis()
        
        # Material analysis
        material_combinations = self.material_analysis()
        
        # Technique analysis
        technique_performance = self.welding_technique_analysis()
        
        # Process parameter optimization
        power_analysis, force_analysis, time_analysis = self.process_parameter_optimization()
        
        # Quality vs performance analysis
        quality_perf_corr = self.quality_vs_performance_analysis()
        
        # Optimization recommendations
        self.generate_optimization_recommendations()
        
        # Create visualizations
        self.create_interactive_visualizations()
        
        print("\n=== Analysis Complete ===")
        print("All analysis results and visualizations have been generated.")

def main():
    print("=== Welding Dataset Comprehensive Analysis ===")
    
    # Initialize analyzer
    analyzer = WeldingDatasetAnalyzer()
    
    # Generate comprehensive report
    analyzer.generate_comprehensive_report()

if __name__ == "__main__":
    main()