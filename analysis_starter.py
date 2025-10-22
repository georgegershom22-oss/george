#!/usr/bin/env python3
"""
Nigerian SME Innovation Research - Data Analysis Starter Script

This script provides quick start functions for loading and exploring
the secondary dataset on innovation adoption in Nigerian SMEs.

Usage:
    python analysis_starter.py

Author: Generated for ML research on Nigerian SME innovation
Date: October 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

class SMEDataLoader:
    """Utility class for loading and managing SME datasets"""
    
    def __init__(self, data_dir='.'):
        """
        Initialize the data loader
        
        Args:
            data_dir (str): Directory containing the CSV files
        """
        self.data_dir = Path(data_dir)
        self.datasets = {}
        
    def load_all(self):
        """Load all CSV datasets"""
        files = {
            'macro': 'macroeconomic_indicators.csv',
            'broadband': 'broadband_penetration_by_state.csv',
            'sectors': 'sectoral_growth_rates.csv',
            'tech': 'technology_adoption_indices.csv',
            'sme': 'sme_landscape_indicators.csv',
            'barriers': 'innovation_adoption_barriers.csv',
            'regional': 'regional_summary_statistics.csv',
            'policy': 'policy_and_external_factors.csv'
        }
        
        for name, filename in files.items():
            filepath = self.data_dir / filename
            if filepath.exists():
                self.datasets[name] = pd.read_csv(filepath)
                print(f"✓ Loaded {name}: {self.datasets[name].shape}")
            else:
                print(f"✗ File not found: {filename}")
        
        return self.datasets
    
    def get_summary(self):
        """Print summary statistics for all loaded datasets"""
        if not self.datasets:
            print("No datasets loaded. Call load_all() first.")
            return
        
        print("\n" + "="*80)
        print("DATASET SUMMARY")
        print("="*80)
        
        for name, df in self.datasets.items():
            print(f"\n{name.upper()}")
            print("-" * 40)
            print(f"Shape: {df.shape}")
            print(f"Columns: {', '.join(df.columns[:5].tolist())}...")
            if 'Year' in df.columns:
                print(f"Time range: {df['Year'].min()} - {df['Year'].max()}")
            print(f"Memory: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")


def visualize_fintech_adoption(tech_df):
    """
    Visualize FinTech adoption trends
    
    Args:
        tech_df (pd.DataFrame): Technology adoption dataframe
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # FinTech Adoption Rate
    axes[0, 0].plot(tech_df['Year'], tech_df['FinTech_Adoption_Rate_Percent'], 
                    marker='o', linewidth=2, markersize=8, color='#2E86AB')
    axes[0, 0].set_title('FinTech Adoption Rate (%)', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Year')
    axes[0, 0].set_ylabel('Adoption Rate (%)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Mobile Money Users
    axes[0, 1].plot(tech_df['Year'], tech_df['Mobile_Money_Users_Million'], 
                    marker='s', linewidth=2, markersize=8, color='#A23B72')
    axes[0, 1].set_title('Mobile Money Users (Million)', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Year')
    axes[0, 1].set_ylabel('Users (Million)')
    axes[0, 1].grid(True, alpha=0.3)
    
    # ICT Development Index
    axes[1, 0].plot(tech_df['Year'], tech_df['ICT_Development_Index'], 
                    marker='^', linewidth=2, markersize=8, color='#F18F01')
    axes[1, 0].set_title('ICT Development Index', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Year')
    axes[1, 0].set_ylabel('Index Score')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Digital Payment Volume
    axes[1, 1].plot(tech_df['Year'], tech_df['Digital_Payment_Volume_Million_Transactions'], 
                    marker='d', linewidth=2, markersize=8, color='#6A994E')
    axes[1, 1].set_title('Digital Payment Volume (Million Transactions)', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Year')
    axes[1, 1].set_ylabel('Transactions (Million)')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('fintech_adoption_trends.png', dpi=300, bbox_inches='tight')
    print("\n✓ Saved: fintech_adoption_trends.png")
    plt.show()


def visualize_regional_barriers(barriers_df, year=2024):
    """
    Visualize innovation barriers by region
    
    Args:
        barriers_df (pd.DataFrame): Innovation barriers dataframe
        year (int): Year to analyze
    """
    # Filter for specific year
    df_year = barriers_df[barriers_df['Year'] == year].copy()
    
    # Select barrier columns
    barrier_cols = [col for col in df_year.columns if '_Percent' in col and col != 'Year']
    
    # Clean column names for display
    barrier_names = [col.replace('_Percent', '').replace('_', ' ') for col in barrier_cols]
    
    # Create heatmap data
    heatmap_data = df_year[['Region'] + barrier_cols].set_index('Region')[barrier_cols]
    heatmap_data.columns = barrier_names
    
    # Plot heatmap
    fig, ax = plt.subplots(figsize=(16, 8))
    sns.heatmap(heatmap_data.T, annot=True, fmt='.1f', cmap='RdYlGn_r', 
                cbar_kws={'label': 'Percentage (%)'},
                linewidths=0.5, ax=ax)
    ax.set_title(f'Innovation Adoption Barriers by Region ({year})', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Region', fontsize=12)
    ax.set_ylabel('Barrier Type', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(f'regional_barriers_{year}.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved: regional_barriers_{year}.png")
    plt.show()


def visualize_sme_evolution(sme_df):
    """
    Visualize SME sector evolution
    
    Args:
        sme_df (pd.DataFrame): SME landscape dataframe
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Total SMEs
    axes[0, 0].plot(sme_df['Year'], sme_df['Total_SMEs_Million'], 
                    marker='o', linewidth=2, markersize=8, color='#2E86AB')
    axes[0, 0].set_title('Total SMEs (Million)', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Year')
    axes[0, 0].set_ylabel('SMEs (Million)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # GDP Contribution
    axes[0, 1].plot(sme_df['Year'], sme_df['SME_GDP_Contribution_Percent'], 
                    marker='s', linewidth=2, markersize=8, color='#A23B72')
    axes[0, 1].set_title('SME GDP Contribution (%)', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Year')
    axes[0, 1].set_ylabel('GDP Contribution (%)')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Tech-Enabled SMEs
    axes[1, 0].plot(sme_df['Year'], sme_df['Tech_Enabled_SMEs_Percent'], 
                    marker='^', linewidth=2, markersize=8, color='#F18F01')
    axes[1, 0].set_title('Tech-Enabled SMEs (%)', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Year')
    axes[1, 0].set_ylabel('Percentage (%)')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Women vs Youth Ownership
    axes[1, 1].plot(sme_df['Year'], sme_df['Women_Owned_SMEs_Percent'], 
                    marker='o', linewidth=2, markersize=8, label='Women-Owned', color='#6A994E')
    axes[1, 1].plot(sme_df['Year'], sme_df['Youth_Owned_SMEs_Percent'], 
                    marker='s', linewidth=2, markersize=8, label='Youth-Owned', color='#E76F51')
    axes[1, 1].set_title('Demographic Ownership Trends', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Year')
    axes[1, 1].set_ylabel('Percentage (%)')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('sme_evolution.png', dpi=300, bbox_inches='tight')
    print("\n✓ Saved: sme_evolution.png")
    plt.show()


def analyze_regional_disparities(regional_df, year=2024):
    """
    Analyze and visualize regional ecosystem disparities
    
    Args:
        regional_df (pd.DataFrame): Regional summary dataframe
        year (int): Year to analyze
    """
    df_year = regional_df[regional_df['Year'] == year].copy()
    
    # Select key metrics
    metrics = {
        'Average_SME_Revenue_Million_NGN': 'Avg Revenue (₦M)',
        'Venture_Capital_Investment_Million_NGN': 'VC Investment (₦M)',
        'Innovation_Hubs_Count': 'Innovation Hubs',
        'Digital_Infrastructure_Score': 'Digital Infrastructure'
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes = axes.flatten()
    
    for idx, (col, label) in enumerate(metrics.items()):
        ax = axes[idx]
        data = df_year.sort_values(col, ascending=False)
        
        bars = ax.barh(data['Region'], data[col], color=plt.cm.viridis(np.linspace(0.3, 0.9, len(data))))
        ax.set_xlabel(label, fontsize=11)
        ax.set_title(f'{label} by Region ({year})', fontsize=12, fontweight='bold')
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, data[col])):
            ax.text(val, i, f'  {val:.1f}', va='center', fontsize=9)
        
        ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'regional_disparities_{year}.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved: regional_disparities_{year}.png")
    plt.show()


def correlation_analysis(datasets):
    """
    Perform correlation analysis between key variables
    
    Args:
        datasets (dict): Dictionary of loaded datasets
    """
    # Merge key datasets
    merged = datasets['regional'].merge(
        datasets['policy'], on='Year', how='left'
    )
    
    # Select variables for correlation
    corr_vars = [
        'Average_SME_Revenue_Million_NGN',
        'Venture_Capital_Investment_Million_NGN',
        'Digital_Infrastructure_Score',
        'Business_Incubators_Count',
        'Government_SME_Budget_Billion_NGN',
        'SME_Density_Per_1000_Population',
        'R_D_Expenditure_Percent_GDP'
    ]
    
    # Compute correlation matrix
    corr_matrix = merged[corr_vars].corr()
    
    # Visualize
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                center=0, square=True, linewidths=1,
                cbar_kws={'label': 'Correlation Coefficient'},
                ax=ax)
    ax.set_title('Correlation Matrix: SME Ecosystem Variables', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Rotate labels
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig('correlation_matrix.png', dpi=300, bbox_inches='tight')
    print("\n✓ Saved: correlation_matrix.png")
    plt.show()
    
    # Print top correlations
    print("\n" + "="*80)
    print("TOP CORRELATIONS WITH SME REVENUE")
    print("="*80)
    revenue_corrs = corr_matrix['Average_SME_Revenue_Million_NGN'].sort_values(ascending=False)
    for var, corr in revenue_corrs.items():
        if var != 'Average_SME_Revenue_Million_NGN':
            print(f"{var:50s}: {corr:6.3f}")


def main():
    """Main execution function"""
    print("="*80)
    print("NIGERIAN SME INNOVATION DATASET - QUICK START ANALYSIS")
    print("="*80)
    
    # Initialize loader
    loader = SMEDataLoader()
    
    # Load datasets
    print("\nLoading datasets...")
    datasets = loader.load_all()
    
    if not datasets:
        print("\n✗ No datasets found. Please ensure CSV files are in the current directory.")
        return
    
    # Print summary
    loader.get_summary()
    
    # Generate visualizations
    print("\n" + "="*80)
    print("GENERATING VISUALIZATIONS")
    print("="*80)
    
    if 'tech' in datasets:
        print("\n1. FinTech Adoption Trends...")
        visualize_fintech_adoption(datasets['tech'])
    
    if 'barriers' in datasets:
        print("\n2. Regional Innovation Barriers...")
        visualize_regional_barriers(datasets['barriers'], year=2024)
    
    if 'sme' in datasets:
        print("\n3. SME Sector Evolution...")
        visualize_sme_evolution(datasets['sme'])
    
    if 'regional' in datasets:
        print("\n4. Regional Disparities...")
        analyze_regional_disparities(datasets['regional'], year=2024)
    
    if 'regional' in datasets and 'policy' in datasets:
        print("\n5. Correlation Analysis...")
        correlation_analysis(datasets)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print("\nGenerated visualizations:")
    print("  • fintech_adoption_trends.png")
    print("  • regional_barriers_2024.png")
    print("  • sme_evolution.png")
    print("  • regional_disparities_2024.png")
    print("  • correlation_matrix.png")
    print("\nNext steps:")
    print("  1. Review DATA_DICTIONARY.md for variable descriptions")
    print("  2. Explore individual datasets using pandas")
    print("  3. Build predictive models using scikit-learn")
    print("  4. Conduct econometric analysis")
    print("="*80)


if __name__ == "__main__":
    main()
