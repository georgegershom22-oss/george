"""
Welding Dataset Analysis and Visualization
==========================================

This script provides comprehensive analysis and visualization of the
generated welding dataset for inverse design applications.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class WeldingDatasetAnalyzer:
    """Comprehensive analysis and visualization of welding dataset."""
    
    def __init__(self, dataset_path: str):
        """Load dataset."""
        print(f"Loading dataset from {dataset_path}...")
        self.df = pd.read_csv(dataset_path)
        print(f"Loaded {len(self.df)} samples with {len(self.df.columns)} features")
        
    def basic_statistics(self):
        """Print basic statistics about the dataset."""
        print("\n" + "="*80)
        print("BASIC DATASET STATISTICS")
        print("="*80)
        
        print(f"\nDataset Shape: {self.df.shape}")
        print(f"Memory Usage: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        print("\nMissing Values:")
        missing = self.df.isnull().sum()
        missing = missing[missing > 0]
        if len(missing) > 0:
            print(missing)
        else:
            print("No missing values!")
        
        print("\nData Types:")
        print(self.df.dtypes.value_counts())
        
        print("\nNumerical Features Summary:")
        numeric_df = self.df.select_dtypes(include=[np.number])
        print(f"Number of numerical features: {len(numeric_df.columns)}")
        
        print("\nCategorical Features:")
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        print(f"Number of categorical features: {len(categorical_cols)}")
        for col in categorical_cols:
            if col not in ['sample_id', 'collection_date']:
                print(f"\n{col}:")
                print(self.df[col].value_counts())
    
    def plot_distributions(self, output_prefix='welding_plot'):
        """Plot distributions of key variables."""
        print("\nGenerating distribution plots...")
        
        # Key performance metrics
        key_metrics = [
            'cycles_to_failure',
            'resistance_degradation_percent_per_1000cycles',
            'tensile_strength_MPa',
            'contact_resistance_uOhm',
            'overall_performance_score',
            'heat_input_J_per_mm'
        ]
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.ravel()
        
        for idx, metric in enumerate(key_metrics):
            ax = axes[idx]
            
            # Histogram with KDE
            ax.hist(self.df[metric], bins=50, alpha=0.7, edgecolor='black', density=True)
            
            # Fit and plot normal distribution
            mu, sigma = self.df[metric].mean(), self.df[metric].std()
            x = np.linspace(self.df[metric].min(), self.df[metric].max(), 100)
            ax.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2, 
                   label=f'Normal(μ={mu:.1f}, σ={sigma:.1f})')
            
            ax.set_xlabel(metric.replace('_', ' ').title(), fontsize=10)
            ax.set_ylabel('Density', fontsize=10)
            ax.set_title(f'Distribution: {metric}', fontsize=11, fontweight='bold')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'/workspace/{output_prefix}_distributions.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_prefix}_distributions.png")
        plt.close()
    
    def plot_correlations(self, output_prefix='welding_plot'):
        """Plot correlation matrices."""
        print("\nGenerating correlation plots...")
        
        # Select key numerical features
        key_features = [
            'power_W', 'pressure_MPa', 'weld_time_ms', 'heat_input_J_per_mm',
            'tensile_strength_MPa', 'contact_resistance_uOhm', 'porosity_percent',
            'weld_nugget_diameter_mm', 'bond_area_mm2',
            'cycles_to_failure', 'resistance_degradation_percent_per_1000cycles',
            'overall_performance_score'
        ]
        
        correlation_df = self.df[key_features].corr()
        
        # Plot correlation matrix
        fig, ax = plt.subplots(figsize=(14, 12))
        
        # Create mask for upper triangle
        mask = np.triu(np.ones_like(correlation_df, dtype=bool))
        
        # Plot heatmap
        sns.heatmap(correlation_df, mask=mask, annot=True, fmt='.2f', 
                   cmap='coolwarm', center=0, square=True, linewidths=1,
                   cbar_kws={"shrink": 0.8}, ax=ax, vmin=-1, vmax=1)
        
        ax.set_title('Correlation Matrix: Key Features', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(f'/workspace/{output_prefix}_correlations.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_prefix}_correlations.png")
        plt.close()
    
    def plot_process_comparisons(self, output_prefix='welding_plot'):
        """Compare different welding processes."""
        print("\nGenerating process comparison plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Cycles to failure by technique
        ax = axes[0, 0]
        techniques = self.df['welding_technique'].unique()
        data_to_plot = [self.df[self.df['welding_technique'] == t]['cycles_to_failure'] 
                       for t in techniques]
        bp = ax.boxplot(data_to_plot, labels=techniques, patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')
        ax.set_ylabel('Cycles to Failure', fontsize=11)
        ax.set_title('Thermal Cycling Life by Welding Technique', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        
        # 2. Resistance degradation by technique
        ax = axes[0, 1]
        data_to_plot = [self.df[self.df['welding_technique'] == t]['resistance_degradation_percent_per_1000cycles'] 
                       for t in techniques]
        bp = ax.boxplot(data_to_plot, labels=techniques, patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('lightcoral')
        ax.set_ylabel('Resistance Degradation (%/1000 cycles)', fontsize=11)
        ax.set_title('Resistance Degradation by Welding Technique', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        
        # 3. Performance score by material combination
        ax = axes[1, 0]
        self.df['material_combo'] = self.df['anode_material'] + '\n+\n' + self.df['cathode_material']
        combo_stats = self.df.groupby('material_combo')['overall_performance_score'].agg(['mean', 'std'])
        combo_stats = combo_stats.sort_values('mean', ascending=False).head(8)
        
        x_pos = np.arange(len(combo_stats))
        ax.bar(x_pos, combo_stats['mean'], yerr=combo_stats['std'], 
              alpha=0.7, capsize=5, color='lightgreen', edgecolor='black')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(combo_stats.index, fontsize=8)
        ax.set_ylabel('Overall Performance Score', fontsize=11)
        ax.set_title('Top Material Combinations', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        ax.tick_params(axis='x', rotation=45)
        
        # 4. Quality class distribution
        ax = axes[1, 1]
        quality_counts = self.df['quality_class'].value_counts()
        colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
        wedges, texts, autotexts = ax.pie(quality_counts.values, labels=quality_counts.index,
                                           autopct='%1.1f%%', colors=colors, startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        ax.set_title('Quality Class Distribution', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'/workspace/{output_prefix}_process_comparison.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_prefix}_process_comparison.png")
        plt.close()
    
    def plot_material_effects(self, output_prefix='welding_plot'):
        """Analyze material effects on performance."""
        print("\nGenerating material effects plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Coating effects on resistance
        ax = axes[0, 0]
        coating_resistance = self.df.groupby('anode_coating')['contact_resistance_uOhm'].mean().sort_values()
        coating_resistance.plot(kind='barh', ax=ax, color='skyblue', edgecolor='black')
        ax.set_xlabel('Average Contact Resistance (µΩ)', fontsize=11)
        ax.set_ylabel('Anode Coating', fontsize=11)
        ax.set_title('Effect of Coating on Contact Resistance', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        # 2. Coating effects on strength
        ax = axes[0, 1]
        coating_strength = self.df.groupby('anode_coating')['tensile_strength_MPa'].mean().sort_values(ascending=False)
        coating_strength.plot(kind='barh', ax=ax, color='lightcoral', edgecolor='black')
        ax.set_xlabel('Average Tensile Strength (MPa)', fontsize=11)
        ax.set_ylabel('Anode Coating', fontsize=11)
        ax.set_title('Effect of Coating on Tensile Strength', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        # 3. Material compatibility (same vs dissimilar)
        ax = axes[1, 0]
        self.df['same_material'] = self.df['anode_material'] == self.df['cathode_material']
        same_vs_diff = self.df.groupby('same_material')['cycles_to_failure'].agg(['mean', 'std'])
        x_pos = [0, 1]
        labels = ['Dissimilar\nMetals', 'Same\nMetal']
        ax.bar(x_pos, same_vs_diff['mean'], yerr=same_vs_diff['std'], 
              alpha=0.7, capsize=10, color=['#e74c3c', '#2ecc71'], edgecolor='black')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels)
        ax.set_ylabel('Average Cycles to Failure', fontsize=11)
        ax.set_title('Material Compatibility Effect on Thermal Cycling', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        # 4. Thickness effects
        ax = axes[1, 1]
        thickness_bins = pd.cut(self.df['anode_thickness_um'], bins=5)
        thickness_performance = self.df.groupby(thickness_bins)['overall_performance_score'].mean()
        thickness_labels = [f'{int(interval.left)}-{int(interval.right)}' 
                           for interval in thickness_performance.index]
        ax.plot(range(len(thickness_performance)), thickness_performance.values, 
               marker='o', linewidth=2, markersize=8, color='purple')
        ax.set_xticks(range(len(thickness_performance)))
        ax.set_xticklabels(thickness_labels, rotation=45)
        ax.set_xlabel('Anode Thickness (µm)', fontsize=11)
        ax.set_ylabel('Overall Performance Score', fontsize=11)
        ax.set_title('Effect of Tab Thickness on Performance', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'/workspace/{output_prefix}_material_effects.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_prefix}_material_effects.png")
        plt.close()
    
    def plot_parameter_optimization(self, output_prefix='welding_plot'):
        """Show parameter optimization landscapes."""
        print("\nGenerating parameter optimization plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Filter for ultrasonic welding only for clearer visualization
        usw_df = self.df[self.df['welding_technique'] == 'Ultrasonic'].copy()
        
        # 1. Power vs Pressure (color = cycles to failure)
        ax = axes[0, 0]
        scatter = ax.scatter(usw_df['power_W'], usw_df['pressure_MPa'], 
                           c=usw_df['cycles_to_failure'], cmap='RdYlGn',
                           s=50, alpha=0.6, edgecolors='black', linewidth=0.5)
        ax.set_xlabel('Power (W)', fontsize=11)
        ax.set_ylabel('Pressure (MPa)', fontsize=11)
        ax.set_title('Ultrasonic Welding: Power vs Pressure\n(Color = Cycles to Failure)', 
                    fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Cycles to Failure', fontsize=10)
        
        # 2. Heat Input vs Performance Score
        ax = axes[0, 1]
        ax.hexbin(self.df['heat_input_J_per_mm'], self.df['overall_performance_score'],
                 gridsize=30, cmap='YlOrRd', mincnt=1)
        ax.set_xlabel('Heat Input (J/mm)', fontsize=11)
        ax.set_ylabel('Overall Performance Score', fontsize=11)
        ax.set_title('Heat Input Optimization\n(Hexbin Density)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # 3. Strength vs Resistance (color = quality class)
        ax = axes[1, 0]
        quality_colors = {'Excellent': '#2ecc71', 'Good': '#3498db', 
                         'Acceptable': '#f39c12', 'Poor': '#e74c3c'}
        for quality in quality_colors:
            mask = self.df['quality_class'] == quality
            ax.scatter(self.df.loc[mask, 'tensile_strength_MPa'], 
                      self.df.loc[mask, 'contact_resistance_uOhm'],
                      c=quality_colors[quality], label=quality, alpha=0.6, s=30)
        ax.set_xlabel('Tensile Strength (MPa)', fontsize=11)
        ax.set_ylabel('Contact Resistance (µΩ)', fontsize=11)
        ax.set_title('Strength vs Resistance Trade-off', fontsize=12, fontweight='bold')
        ax.set_yscale('log')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        
        # 4. Defects vs Performance
        ax = axes[1, 1]
        self.df['total_defects'] = (self.df['porosity_percent'] + 
                                   self.df['crack_density_per_mm2'] * 2)
        scatter = ax.scatter(self.df['total_defects'], self.df['cycles_to_failure'],
                           c=self.df['tensile_strength_MPa'], cmap='viridis',
                           s=50, alpha=0.6, edgecolors='black', linewidth=0.5)
        ax.set_xlabel('Total Defect Score', fontsize=11)
        ax.set_ylabel('Cycles to Failure', fontsize=11)
        ax.set_title('Impact of Defects on Fatigue Life\n(Color = Tensile Strength)', 
                    fontsize=12, fontweight='bold')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3)
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Tensile Strength (MPa)', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'/workspace/{output_prefix}_optimization.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_prefix}_optimization.png")
        plt.close()
    
    def feature_importance_analysis(self, output_prefix='welding_plot'):
        """Analyze feature importance using Random Forest."""
        print("\nPerforming feature importance analysis...")
        
        # Prepare data
        # Select numerical input features
        input_features = [
            'anode_thickness_um', 'cathode_thickness_um',
            'anode_surface_roughness_um', 'cathode_surface_roughness_um',
            'power_W', 'clamping_force_N', 'pressure_MPa', 'weld_time_ms',
            'preheat_temperature_C', 'ambient_temperature_C', 'ambient_humidity_percent'
        ]
        
        # Add encoded categorical features
        df_encoded = self.df.copy()
        categorical_features = ['welding_technique', 'anode_material', 'cathode_material',
                              'anode_coating', 'cathode_coating', 'cleaning_method']
        
        for col in categorical_features:
            dummies = pd.get_dummies(df_encoded[col], prefix=col)
            df_encoded = pd.concat([df_encoded, dummies], axis=1)
            input_features.extend(dummies.columns)
        
        # Remove rows with NaN in input features
        df_clean = df_encoded[input_features + ['cycles_to_failure']].dropna()
        
        X = df_clean[input_features]
        y = df_clean['cycles_to_failure']
        
        # Train Random Forest
        print("Training Random Forest model...")
        rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X, y)
        
        # Get feature importance
        importance_df = pd.DataFrame({
            'feature': input_features,
            'importance': rf.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Plot top 20 features
        fig, ax = plt.subplots(figsize=(12, 10))
        top_features = importance_df.head(20)
        
        colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(top_features)))
        ax.barh(range(len(top_features)), top_features['importance'], color=colors, edgecolor='black')
        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels([f.replace('_', ' ') for f in top_features['feature']], fontsize=9)
        ax.set_xlabel('Feature Importance', fontsize=11)
        ax.set_title('Top 20 Features for Predicting Cycles to Failure\n(Random Forest)', 
                    fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        ax.invert_yaxis()
        
        plt.tight_layout()
        plt.savefig(f'/workspace/{output_prefix}_feature_importance.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_prefix}_feature_importance.png")
        plt.close()
        
        # Save importance scores
        importance_df.to_csv(f'/workspace/{output_prefix}_feature_importance.csv', index=False)
        print(f"✓ Saved: {output_prefix}_feature_importance.csv")
    
    def pca_analysis(self, output_prefix='welding_plot'):
        """Perform PCA analysis."""
        print("\nPerforming PCA analysis...")
        
        # Select numerical features
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        # Exclude ID and date columns
        feature_cols = [col for col in numerical_cols 
                       if col not in ['sample_id', 'collection_date']]
        
        # Handle missing values
        df_pca = self.df[feature_cols].fillna(self.df[feature_cols].mean())
        
        # Standardize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_pca)
        
        # PCA
        pca = PCA()
        X_pca = pca.fit_transform(X_scaled)
        
        # Plot variance explained
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Cumulative variance
        ax = axes[0]
        cumsum_var = np.cumsum(pca.explained_variance_ratio_)
        ax.plot(range(1, len(cumsum_var)+1), cumsum_var, marker='o', linewidth=2)
        ax.axhline(y=0.95, color='r', linestyle='--', label='95% Variance')
        ax.axhline(y=0.90, color='orange', linestyle='--', label='90% Variance')
        ax.set_xlabel('Number of Components', fontsize=11)
        ax.set_ylabel('Cumulative Explained Variance', fontsize=11)
        ax.set_title('PCA: Cumulative Variance Explained', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_xlim(0, 50)  # Focus on first 50 components
        
        # 2D projection colored by quality class
        ax = axes[1]
        quality_colors = {'Excellent': '#2ecc71', 'Good': '#3498db', 
                         'Acceptable': '#f39c12', 'Poor': '#e74c3c'}
        
        for quality in quality_colors:
            mask = self.df['quality_class'] == quality
            ax.scatter(X_pca[mask, 0], X_pca[mask, 1], 
                      c=quality_colors[quality], label=quality, 
                      alpha=0.6, s=20, edgecolors='none')
        
        ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)', fontsize=11)
        ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)', fontsize=11)
        ax.set_title('PCA: First Two Principal Components', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'/workspace/{output_prefix}_pca.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_prefix}_pca.png")
        plt.close()
        
        # Calculate components needed for 90% and 95% variance
        n_90 = np.argmax(cumsum_var >= 0.90) + 1
        n_95 = np.argmax(cumsum_var >= 0.95) + 1
        print(f"  Components for 90% variance: {n_90}")
        print(f"  Components for 95% variance: {n_95}")
    
    def generate_summary_report(self, output_path='/workspace/welding_analysis_report.txt'):
        """Generate comprehensive text summary."""
        print("\nGenerating summary report...")
        
        report = []
        report.append("="*80)
        report.append("WELDING DATASET ANALYSIS REPORT")
        report.append("="*80)
        report.append("")
        
        # Dataset Overview
        report.append("DATASET OVERVIEW")
        report.append("-" * 80)
        report.append(f"Total Samples: {len(self.df)}")
        report.append(f"Total Features: {len(self.df.columns)}")
        report.append(f"Date Range: {self.df['collection_date'].min()} to {self.df['collection_date'].max()}")
        report.append("")
        
        # Welding Techniques
        report.append("WELDING TECHNIQUES DISTRIBUTION")
        report.append("-" * 80)
        for tech, count in self.df['welding_technique'].value_counts().items():
            pct = count / len(self.df) * 100
            report.append(f"{tech:20s}: {count:5d} ({pct:5.1f}%)")
        report.append("")
        
        # Material Combinations
        report.append("TOP 10 MATERIAL COMBINATIONS")
        report.append("-" * 80)
        material_combo = self.df['anode_material'] + ' + ' + self.df['cathode_material']
        for combo, count in material_combo.value_counts().head(10).items():
            pct = count / len(self.df) * 100
            report.append(f"{combo:30s}: {count:5d} ({pct:5.1f}%)")
        report.append("")
        
        # Quality Distribution
        report.append("QUALITY CLASS DISTRIBUTION")
        report.append("-" * 80)
        for quality, count in self.df['quality_class'].value_counts().items():
            pct = count / len(self.df) * 100
            report.append(f"{quality:15s}: {count:5d} ({pct:5.1f}%)")
        report.append("")
        
        # Key Performance Metrics
        report.append("KEY PERFORMANCE METRICS")
        report.append("-" * 80)
        
        metrics = {
            'Cycles to Failure': 'cycles_to_failure',
            'Resistance Degradation (%/1000cyc)': 'resistance_degradation_percent_per_1000cycles',
            'Tensile Strength (MPa)': 'tensile_strength_MPa',
            'Contact Resistance (µΩ)': 'contact_resistance_uOhm',
            'Overall Performance Score': 'overall_performance_score',
            'Heat Input (J/mm)': 'heat_input_J_per_mm',
            'Porosity (%)': 'porosity_percent',
            'MTBF (hours)': 'MTBF_hours'
        }
        
        for name, col in metrics.items():
            mean = self.df[col].mean()
            std = self.df[col].std()
            median = self.df[col].median()
            min_val = self.df[col].min()
            max_val = self.df[col].max()
            report.append(f"\n{name}:")
            report.append(f"  Mean ± Std: {mean:.2f} ± {std:.2f}")
            report.append(f"  Median: {median:.2f}")
            report.append(f"  Range: [{min_val:.2f}, {max_val:.2f}]")
        report.append("")
        
        # Performance by Technique
        report.append("PERFORMANCE BY WELDING TECHNIQUE")
        report.append("-" * 80)
        for tech in self.df['welding_technique'].unique():
            tech_df = self.df[self.df['welding_technique'] == tech]
            report.append(f"\n{tech}:")
            report.append(f"  Avg Cycles to Failure: {tech_df['cycles_to_failure'].mean():.0f}")
            report.append(f"  Avg Performance Score: {tech_df['overall_performance_score'].mean():.1f}")
            report.append(f"  Avg Resistance Degradation: {tech_df['resistance_degradation_percent_per_1000cycles'].mean():.2f}%")
            report.append(f"  Excellent Quality %: {(tech_df['quality_class']=='Excellent').sum()/len(tech_df)*100:.1f}%")
        report.append("")
        
        # Material Compatibility
        report.append("MATERIAL COMPATIBILITY ANALYSIS")
        report.append("-" * 80)
        same_material = self.df[self.df['anode_material'] == self.df['cathode_material']]
        diff_material = self.df[self.df['anode_material'] != self.df['cathode_material']]
        
        report.append(f"\nSame Material Joints ({len(same_material)} samples):")
        report.append(f"  Avg Cycles to Failure: {same_material['cycles_to_failure'].mean():.0f}")
        report.append(f"  Avg Performance Score: {same_material['overall_performance_score'].mean():.1f}")
        
        report.append(f"\nDissimilar Material Joints ({len(diff_material)} samples):")
        report.append(f"  Avg Cycles to Failure: {diff_material['cycles_to_failure'].mean():.0f}")
        report.append(f"  Avg Performance Score: {diff_material['overall_performance_score'].mean():.1f}")
        report.append(f"  Avg Intermetallic Thickness: {diff_material['intermetallic_thickness_um'].mean():.2f} µm")
        report.append("")
        
        # Coating Effects
        report.append("COATING EFFECTS")
        report.append("-" * 80)
        report.append("\nAverage Contact Resistance by Coating:")
        for coating in self.df['anode_coating'].dropna().unique():
            avg_res = self.df[self.df['anode_coating'] == coating]['contact_resistance_uOhm'].mean()
            report.append(f"  {str(coating):10s}: {avg_res:8.1f} µΩ")
        
        report.append("\nAverage Tensile Strength by Coating:")
        for coating in self.df['anode_coating'].dropna().unique():
            avg_strength = self.df[self.df['anode_coating'] == coating]['tensile_strength_MPa'].mean()
            report.append(f"  {str(coating):10s}: {avg_strength:8.1f} MPa")
        report.append("")
        
        # Correlation Insights
        report.append("KEY CORRELATIONS WITH CYCLES TO FAILURE")
        report.append("-" * 80)
        
        correlation_features = [
            'tensile_strength_MPa', 'porosity_percent', 'crack_density_per_mm2',
            'bond_area_mm2', 'heat_input_J_per_mm', 'contact_resistance_uOhm',
            'intermetallic_thickness_um', 'thermal_stress_MPa'
        ]
        
        correlations = []
        for feature in correlation_features:
            corr = self.df[['cycles_to_failure', feature]].corr().iloc[0, 1]
            correlations.append((feature, corr))
        
        correlations.sort(key=lambda x: abs(x[1]), reverse=True)
        
        for feature, corr in correlations:
            direction = "positive" if corr > 0 else "negative"
            report.append(f"{feature:40s}: {corr:7.3f} ({direction})")
        report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS FOR INVERSE DESIGN")
        report.append("-" * 80)
        
        # Find best parameters - use top 10% as reference
        top_samples = self.df.nlargest(int(len(self.df) * 0.1), 'overall_performance_score')
        
        report.append("\nCharacteristics of Top 10% Performance Welds:")
        report.append(f"  Typical Cycles to Failure: {top_samples['cycles_to_failure'].median():.0f}")
        report.append(f"  Typical Tensile Strength: {top_samples['tensile_strength_MPa'].median():.1f} MPa")
        report.append(f"  Typical Contact Resistance: {top_samples['contact_resistance_uOhm'].median():.1f} µΩ")
        report.append(f"  Typical Porosity: {top_samples['porosity_percent'].median():.2f}%")
        report.append(f"  Typical Heat Input: {top_samples['heat_input_J_per_mm'].median():.1f} J/mm")
        
        report.append("\nMost Common Configurations for Top Performance:")
        if len(top_samples['welding_technique'].mode()) > 0:
            report.append(f"  Welding Technique: {top_samples['welding_technique'].mode()[0]}")
        report.append(f"  Material Compatibility: {(top_samples['anode_material'] == top_samples['cathode_material']).sum() / len(top_samples) * 100:.1f}% same material")
        if len(top_samples['anode_coating'].dropna().mode()) > 0:
            report.append(f"  Most Common Anode Coating: {top_samples['anode_coating'].dropna().mode()[0]}")
        if len(top_samples['cathode_coating'].dropna().mode()) > 0:
            report.append(f"  Most Common Cathode Coating: {top_samples['cathode_coating'].dropna().mode()[0]}")
        report.append("")
        
        report.append("Process Parameter Ranges for Top Performance:")
        param_ranges = {
            'Power (W)': 'power_W',
            'Pressure (MPa)': 'pressure_MPa',
            'Weld Time (ms)': 'weld_time_ms',
            'Preheat Temp (°C)': 'preheat_temperature_C'
        }
        
        for name, col in param_ranges.items():
            q25 = top_samples[col].quantile(0.25)
            q75 = top_samples[col].quantile(0.75)
            median = top_samples[col].median()
            report.append(f"  {name:20s}: {q25:.1f} - {q75:.1f} (median: {median:.1f})")
        
        report.append("")
        report.append("="*80)
        report.append("END OF REPORT")
        report.append("="*80)
        
        # Save report
        with open(output_path, 'w') as f:
            f.write('\n'.join(report))
        
        print(f"✓ Saved: {output_path}")
        
        # Also print to console
        print("\n" + '\n'.join(report))
    
    def run_full_analysis(self):
        """Run complete analysis pipeline."""
        print("\n" + "="*80)
        print("RUNNING FULL ANALYSIS PIPELINE")
        print("="*80)
        
        self.basic_statistics()
        self.plot_distributions()
        self.plot_correlations()
        self.plot_process_comparisons()
        self.plot_material_effects()
        self.plot_parameter_optimization()
        self.feature_importance_analysis()
        self.pca_analysis()
        self.generate_summary_report()
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE!")
        print("="*80)
        print("\nGenerated files:")
        print("  - welding_plot_distributions.png")
        print("  - welding_plot_correlations.png")
        print("  - welding_plot_process_comparison.png")
        print("  - welding_plot_material_effects.png")
        print("  - welding_plot_optimization.png")
        print("  - welding_plot_feature_importance.png")
        print("  - welding_plot_feature_importance.csv")
        print("  - welding_plot_pca.png")
        print("  - welding_analysis_report.txt")
        print()


def main():
    """Main execution function."""
    print("Welding Dataset Analysis")
    print("="*80)
    
    # Check if dataset exists
    import os
    if not os.path.exists('/workspace/welding_dataset_complete.csv'):
        print("ERROR: Dataset not found!")
        print("Please run welding_dataset_generator.py first to generate the dataset.")
        return
    
    # Create analyzer
    analyzer = WeldingDatasetAnalyzer('/workspace/welding_dataset_complete.csv')
    
    # Run full analysis
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()
