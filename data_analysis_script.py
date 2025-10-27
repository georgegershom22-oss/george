import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import warnings
warnings.filterwarnings('ignore')

class WeldingDataAnalyzer:
    def __init__(self, dataset_path='welding_dataset.csv'):
        self.dataset_path = dataset_path
        self.df = None
        self.scaler = StandardScaler()
        
    def load_data(self):
        """Load the welding dataset"""
        print("Loading welding dataset...")
        self.df = pd.read_csv(self.dataset_path)
        print(f"Dataset loaded: {self.df.shape[0]} samples, {self.df.shape[1]} features")
        return self.df
    
    def basic_statistics(self):
        """Generate basic statistical analysis"""
        print("\n" + "="*60)
        print("BASIC STATISTICAL ANALYSIS")
        print("="*60)
        
        # Dataset overview
        print(f"\nDataset Overview:")
        print(f"Total samples: {len(self.df)}")
        print(f"Total features: {len(self.df.columns)}")
        print(f"Missing values: {self.df.isnull().sum().sum()}")
        
        # Categorical features
        categorical_features = ['anode_material', 'cathode_material', 'surface_finish', 
                              'welding_technique', 'primary_failure_mode']
        
        print(f"\nCategorical Features Distribution:")
        for feature in categorical_features:
            if feature in self.df.columns:
                print(f"\n{feature}:")
                value_counts = self.df[feature].value_counts()
                for value, count in value_counts.items():
                    percentage = (count / len(self.df)) * 100
                    print(f"  {value}: {count} ({percentage:.1f}%)")
        
        # Numerical features
        numerical_features = self.df.select_dtypes(include=[np.number]).columns
        print(f"\nNumerical Features Summary:")
        print(self.df[numerical_features].describe())
        
        return self.df[numerical_features].describe()
    
    def correlation_analysis(self):
        """Perform comprehensive correlation analysis"""
        print("\n" + "="*60)
        print("CORRELATION ANALYSIS")
        print("="*60)
        
        # Select numerical features
        numerical_features = self.df.select_dtypes(include=[np.number]).columns
        correlation_matrix = self.df[numerical_features].corr()
        
        # Create correlation heatmap
        plt.figure(figsize=(15, 12))
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm', 
                   center=0, square=True, fmt='.2f')
        plt.title('Feature Correlation Matrix')
        plt.tight_layout()
        plt.savefig('correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Find strong correlations
        print("\nStrong Correlations (|r| > 0.7):")
        strong_corr = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_val = correlation_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    strong_corr.append({
                        'Feature 1': correlation_matrix.columns[i],
                        'Feature 2': correlation_matrix.columns[j],
                        'Correlation': corr_val
                    })
        
        if strong_corr:
            strong_corr_df = pd.DataFrame(strong_corr)
            strong_corr_df = strong_corr_df.sort_values('Correlation', key=abs, ascending=False)
            print(strong_corr_df.to_string(index=False))
        else:
            print("No strong correlations found (|r| > 0.7)")
        
        return correlation_matrix
    
    def material_analysis(self):
        """Analyze material combinations and their effects"""
        print("\n" + "="*60)
        print("MATERIAL COMBINATION ANALYSIS")
        print("="*60)
        
        # Material combination frequency
        material_combinations = self.df.groupby(['anode_material', 'cathode_material']).size().reset_index(name='count')
        material_combinations = material_combinations.sort_values('count', ascending=False)
        
        print("\nMaterial Combination Frequency:")
        print(material_combinations.head(10).to_string(index=False))
        
        # Performance by material combination
        print("\nPerformance by Material Combination:")
        performance_by_material = self.df.groupby(['anode_material', 'cathode_material']).agg({
            'thermal_cycles_to_failure': 'mean',
            'weld_strength_mpa': 'mean',
            'material_compatibility': 'mean'
        }).round(2)
        
        performance_by_material = performance_by_material.sort_values('thermal_cycles_to_failure', ascending=False)
        print(performance_by_material.head(10).to_string())
        
        # Visualize material performance
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Material combination frequency
        top_combinations = material_combinations.head(10)
        axes[0, 0].barh(range(len(top_combinations)), top_combinations['count'])
        axes[0, 0].set_yticks(range(len(top_combinations)))
        axes[0, 0].set_yticklabels([f"{row['anode_material']}-{row['cathode_material']}" 
                                   for _, row in top_combinations.iterrows()])
        axes[0, 0].set_xlabel('Frequency')
        axes[0, 0].set_title('Top 10 Material Combinations')
        
        # Thermal cycles by material
        material_cycles = self.df.groupby('anode_material')['thermal_cycles_to_failure'].mean()
        axes[0, 1].bar(material_cycles.index, material_cycles.values)
        axes[0, 1].set_ylabel('Average Thermal Cycles')
        axes[0, 1].set_title('Thermal Cycles by Anode Material')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Weld strength by material
        material_strength = self.df.groupby('anode_material')['weld_strength_mpa'].mean()
        axes[1, 0].bar(material_strength.index, material_strength.values)
        axes[1, 0].set_ylabel('Average Weld Strength (MPa)')
        axes[1, 0].set_title('Weld Strength by Anode Material')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Material compatibility distribution
        axes[1, 1].hist(self.df['material_compatibility'], bins=30, alpha=0.7, edgecolor='black')
        axes[1, 1].set_xlabel('Material Compatibility')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].set_title('Material Compatibility Distribution')
        
        plt.tight_layout()
        plt.savefig('material_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return performance_by_material
    
    def welding_technique_analysis(self):
        """Analyze welding techniques and their performance"""
        print("\n" + "="*60)
        print("WELDING TECHNIQUE ANALYSIS")
        print("="*60)
        
        # Performance by welding technique
        technique_performance = self.df.groupby('welding_technique').agg({
            'thermal_cycles_to_failure': ['mean', 'std'],
            'weld_strength_mpa': ['mean', 'std'],
            'porosity_percent': ['mean', 'std'],
            'contact_resistance_ohm': ['mean', 'std']
        }).round(3)
        
        print("Performance by Welding Technique:")
        print(technique_performance)
        
        # Failure mode by technique
        failure_by_technique = pd.crosstab(self.df['welding_technique'], 
                                         self.df['primary_failure_mode'], 
                                         normalize='index') * 100
        
        print("\nFailure Mode Distribution by Technique (%):")
        print(failure_by_technique.round(1))
        
        # Visualize technique performance
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Thermal cycles by technique
        technique_cycles = self.df.groupby('welding_technique')['thermal_cycles_to_failure'].mean()
        axes[0, 0].bar(technique_cycles.index, technique_cycles.values)
        axes[0, 0].set_ylabel('Average Thermal Cycles')
        axes[0, 0].set_title('Thermal Cycles by Welding Technique')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Weld strength by technique
        technique_strength = self.df.groupby('welding_technique')['weld_strength_mpa'].mean()
        axes[0, 1].bar(technique_strength.index, technique_strength.values)
        axes[0, 1].set_ylabel('Average Weld Strength (MPa)')
        axes[0, 1].set_title('Weld Strength by Welding Technique')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Porosity by technique
        technique_porosity = self.df.groupby('welding_technique')['porosity_percent'].mean()
        axes[1, 0].bar(technique_porosity.index, technique_porosity.values)
        axes[1, 0].set_ylabel('Average Porosity (%)')
        axes[1, 0].set_title('Porosity by Welding Technique')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Failure mode distribution
        failure_by_technique.plot(kind='bar', ax=axes[1, 1], stacked=True)
        axes[1, 1].set_ylabel('Percentage')
        axes[1, 1].set_title('Failure Mode Distribution by Technique')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        plt.savefig('welding_technique_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return technique_performance
    
    def parameter_optimization_analysis(self):
        """Analyze parameter ranges for optimal performance"""
        print("\n" + "="*60)
        print("PARAMETER OPTIMIZATION ANALYSIS")
        print("="*60)
        
        # Define performance thresholds
        high_performance = self.df[
            (self.df['thermal_cycles_to_failure'] > self.df['thermal_cycles_to_failure'].quantile(0.8)) &
            (self.df['weld_strength_mpa'] > self.df['weld_strength_mpa'].quantile(0.8)) &
            (self.df['porosity_percent'] < self.df['porosity_percent'].quantile(0.2))
        ]
        
        print(f"High-performance samples: {len(high_performance)} ({len(high_performance)/len(self.df)*100:.1f}%)")
        
        # Parameter ranges for high performance
        numerical_params = ['power_w', 'amplitude_um', 'force_n', 'time_ms', 'speed_mm_s', 
                           'pulse_frequency_hz', 'preheat_temp_c', 'tab_thickness_um']
        
        print("\nParameter Ranges for High Performance:")
        for param in numerical_params:
            if param in self.df.columns:
                high_perf_range = high_performance[param]
                overall_range = self.df[param]
                
                print(f"\n{param}:")
                print(f"  High Performance: {high_perf_range.min():.2f} - {high_perf_range.max():.2f}")
                print(f"  Overall Range: {overall_range.min():.2f} - {overall_range.max():.2f}")
                print(f"  High Performance Mean: {high_perf_range.mean():.2f}")
                print(f"  Overall Mean: {overall_range.mean():.2f}")
        
        # Categorical parameter analysis
        categorical_params = ['anode_material', 'cathode_material', 'surface_finish', 'welding_technique']
        
        print("\nCategorical Parameters for High Performance:")
        for param in categorical_params:
            if param in self.df.columns:
                high_perf_counts = high_performance[param].value_counts()
                overall_counts = self.df[param].value_counts()
                
                print(f"\n{param}:")
                for value in high_perf_counts.index:
                    high_perf_pct = (high_perf_counts[value] / len(high_performance)) * 100
                    overall_pct = (overall_counts[value] / len(self.df)) * 100
                    print(f"  {value}: {high_perf_pct:.1f}% (vs {overall_pct:.1f}% overall)")
        
        return high_performance
    
    def dimensionality_reduction_analysis(self):
        """Perform PCA and t-SNE analysis"""
        print("\n" + "="*60)
        print("DIMENSIONALITY REDUCTION ANALYSIS")
        print("="*60)
        
        # Prepare data for dimensionality reduction
        numerical_features = self.df.select_dtypes(include=[np.number]).columns
        X = self.df[numerical_features].values
        X_scaled = self.scaler.fit_transform(X)
        
        # PCA Analysis
        print("Performing PCA analysis...")
        pca = PCA()
        X_pca = pca.fit_transform(X_scaled)
        
        # Explained variance
        explained_variance_ratio = pca.explained_variance_ratio_
        cumulative_variance = np.cumsum(explained_variance_ratio)
        
        print(f"First 10 components explain {cumulative_variance[9]:.1%} of variance")
        print(f"First 5 components explain {cumulative_variance[4]:.1%} of variance")
        
        # PCA visualization
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Explained variance
        axes[0, 0].plot(range(1, 11), explained_variance_ratio[:10], 'bo-')
        axes[0, 0].set_xlabel('Principal Component')
        axes[0, 0].set_ylabel('Explained Variance Ratio')
        axes[0, 0].set_title('PCA Explained Variance Ratio')
        axes[0, 0].grid(True)
        
        # Cumulative variance
        axes[0, 1].plot(range(1, 11), cumulative_variance[:10], 'ro-')
        axes[0, 1].set_xlabel('Principal Component')
        axes[0, 1].set_ylabel('Cumulative Explained Variance')
        axes[0, 1].set_title('PCA Cumulative Explained Variance')
        axes[0, 1].grid(True)
        
        # PCA scatter plot (first two components)
        scatter = axes[1, 0].scatter(X_pca[:, 0], X_pca[:, 1], c=self.df['thermal_cycles_to_failure'], 
                                   cmap='viridis', alpha=0.6)
        axes[1, 0].set_xlabel(f'PC1 ({explained_variance_ratio[0]:.1%})')
        axes[1, 0].set_ylabel(f'PC2 ({explained_variance_ratio[1]:.1%})')
        axes[1, 0].set_title('PCA: PC1 vs PC2 (colored by thermal cycles)')
        plt.colorbar(scatter, ax=axes[1, 0])
        
        # t-SNE analysis (on subset for performance)
        print("Performing t-SNE analysis...")
        n_samples = min(2000, len(X_scaled))
        indices = np.random.choice(len(X_scaled), n_samples, replace=False)
        X_subset = X_scaled[indices]
        
        tsne = TSNE(n_components=2, random_state=42, perplexity=30)
        X_tsne = tsne.fit_transform(X_subset)
        
        # t-SNE scatter plot
        scatter = axes[1, 1].scatter(X_tsne[:, 0], X_tsne[:, 1], 
                                   c=self.df.iloc[indices]['thermal_cycles_to_failure'], 
                                   cmap='viridis', alpha=0.6)
        axes[1, 1].set_xlabel('t-SNE 1')
        axes[1, 1].set_ylabel('t-SNE 2')
        axes[1, 1].set_title('t-SNE Visualization (colored by thermal cycles)')
        plt.colorbar(scatter, ax=axes[1, 1])
        
        plt.tight_layout()
        plt.savefig('dimensionality_reduction_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return X_pca, explained_variance_ratio
    
    def clustering_analysis(self):
        """Perform clustering analysis to identify weld quality groups"""
        print("\n" + "="*60)
        print("CLUSTERING ANALYSIS")
        print("="*60)
        
        # Prepare data for clustering
        numerical_features = self.df.select_dtypes(include=[np.number]).columns
        X = self.df[numerical_features].values
        X_scaled = self.scaler.fit_transform(X)
        
        # K-means clustering
        print("Performing K-means clustering...")
        kmeans = KMeans(n_clusters=4, random_state=42)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        # Add cluster labels to dataframe
        self.df['cluster'] = cluster_labels
        
        # Analyze clusters
        print("\nCluster Analysis:")
        cluster_summary = self.df.groupby('cluster').agg({
            'thermal_cycles_to_failure': ['mean', 'std'],
            'weld_strength_mpa': ['mean', 'std'],
            'porosity_percent': ['mean', 'std'],
            'material_compatibility': ['mean', 'std']
        }).round(2)
        
        print(cluster_summary)
        
        # Cluster characteristics
        print("\nCluster Characteristics:")
        for cluster_id in range(4):
            cluster_data = self.df[self.df['cluster'] == cluster_id]
            print(f"\nCluster {cluster_id} ({len(cluster_data)} samples):")
            
            # Most common materials
            anode_counts = cluster_data['anode_material'].value_counts()
            cathode_counts = cluster_data['cathode_material'].value_counts()
            technique_counts = cluster_data['welding_technique'].value_counts()
            
            print(f"  Top anode materials: {anode_counts.head(3).to_dict()}")
            print(f"  Top cathode materials: {cathode_counts.head(3).to_dict()}")
            print(f"  Top techniques: {technique_counts.head(3).to_dict()}")
            
            # Performance metrics
            print(f"  Avg thermal cycles: {cluster_data['thermal_cycles_to_failure'].mean():.0f}")
            print(f"  Avg weld strength: {cluster_data['weld_strength_mpa'].mean():.1f} MPa")
            print(f"  Avg porosity: {cluster_data['porosity_percent'].mean():.2f}%")
        
        # Visualize clusters
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Cluster distribution
        cluster_counts = self.df['cluster'].value_counts().sort_index()
        axes[0, 0].bar(cluster_counts.index, cluster_counts.values)
        axes[0, 0].set_xlabel('Cluster')
        axes[0, 0].set_ylabel('Number of Samples')
        axes[0, 0].set_title('Cluster Distribution')
        
        # Thermal cycles by cluster
        sns.boxplot(data=self.df, x='cluster', y='thermal_cycles_to_failure', ax=axes[0, 1])
        axes[0, 1].set_title('Thermal Cycles by Cluster')
        
        # Weld strength by cluster
        sns.boxplot(data=self.df, x='cluster', y='weld_strength_mpa', ax=axes[1, 0])
        axes[1, 0].set_title('Weld Strength by Cluster')
        
        # Porosity by cluster
        sns.boxplot(data=self.df, x='cluster', y='porosity_percent', ax=axes[1, 1])
        axes[1, 1].set_title('Porosity by Cluster')
        
        plt.tight_layout()
        plt.savefig('clustering_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return cluster_summary
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive analysis report"""
        print("\n" + "="*60)
        print("GENERATING COMPREHENSIVE ANALYSIS REPORT")
        print("="*60)
        
        # Load data
        self.load_data()
        
        # Run all analyses
        print("Running comprehensive analysis...")
        
        # Basic statistics
        basic_stats = self.basic_statistics()
        
        # Correlation analysis
        correlation_matrix = self.correlation_analysis()
        
        # Material analysis
        material_performance = self.material_analysis()
        
        # Welding technique analysis
        technique_performance = self.welding_technique_analysis()
        
        # Parameter optimization
        high_performance = self.parameter_optimization_analysis()
        
        # Dimensionality reduction
        X_pca, explained_variance = self.dimensionality_reduction_analysis()
        
        # Clustering analysis
        cluster_summary = self.clustering_analysis()
        
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE!")
        print("="*60)
        print("Generated files:")
        print("- correlation_heatmap.png")
        print("- material_analysis.png")
        print("- welding_technique_analysis.png")
        print("- dimensionality_reduction_analysis.png")
        print("- clustering_analysis.png")
        print("="*60)
        
        return {
            'basic_stats': basic_stats,
            'correlation_matrix': correlation_matrix,
            'material_performance': material_performance,
            'technique_performance': technique_performance,
            'high_performance': high_performance,
            'explained_variance': explained_variance,
            'cluster_summary': cluster_summary
        }

def main():
    # Initialize analyzer
    analyzer = WeldingDataAnalyzer()
    
    # Run comprehensive analysis
    results = analyzer.generate_comprehensive_report()
    
    print("\nAnalysis complete! Check the generated PNG files for visualizations.")

if __name__ == "__main__":
    main()