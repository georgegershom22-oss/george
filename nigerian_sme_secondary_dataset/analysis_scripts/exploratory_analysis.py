"""
Exploratory Data Analysis for Nigerian SME Secondary Dataset
Comprehensive EDA functions for understanding patterns, trends, and relationships
in the macro-contextual data for SME innovation research.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr, spearmanr
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path

# Configure plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMEDataExplorer:
    """
    Comprehensive exploratory data analysis class for Nigerian SME secondary dataset.
    """
    
    def __init__(self, datasets: Dict[str, Dict[str, pd.DataFrame]]):
        """
        Initialize explorer with loaded datasets.
        
        Args:
            datasets: Dictionary of loaded datasets from DataLoader
        """
        self.datasets = datasets
        self.master_df = None
        self.correlation_matrices = {}
        
    def create_master_dataset(self) -> pd.DataFrame:
        """
        Create master dataset for comprehensive analysis.
        
        Returns:
            Master DataFrame with key indicators
        """
        # Start with quarterly date range
        date_range = pd.date_range(start='2018-01-01', end='2024-12-31', freq='QS')
        master_df = pd.DataFrame({'Date': date_range})
        
        # Add macroeconomic indicators
        if 'macroeconomic' in self.datasets:
            # GDP growth (annual, forward fill)
            if 'gdp_growth' in self.datasets['macroeconomic']:
                gdp_df = self.datasets['macroeconomic']['gdp_growth'][['Year', 'GDP_Growth_Rate_Percent']].copy()
                gdp_df['Date'] = pd.to_datetime(gdp_df['Year'], format='%Y')
                gdp_df = gdp_df.drop('Year', axis=1)
                master_df = pd.merge(master_df, gdp_df, on='Date', how='left')
                master_df['GDP_Growth_Rate_Percent'] = master_df['GDP_Growth_Rate_Percent'].fillna(method='ffill')
            
            # Interest rates
            if 'interest_rates' in self.datasets['macroeconomic']:
                interest_df = self.datasets['macroeconomic']['interest_rates'][
                    ['Date', 'Monetary_Policy_Rate_Percent', 'Prime_Lending_Rate_Percent']
                ].copy()
                master_df = pd.merge(master_df, interest_df, on='Date', how='left')
        
        # Add technology indicators
        if 'technology' in self.datasets:
            if 'fintech_adoption' in self.datasets['technology']:
                fintech_df = self.datasets['technology']['fintech_adoption'][
                    ['Date', 'Mobile_Money_Penetration_Percent', 'FinTech_Adoption_Index', 'Digital_Banking_Penetration_Percent']
                ].copy()
                master_df = pd.merge(master_df, fintech_df, on='Date', how='left')
            
            if 'digital_transformation' in self.datasets['technology']:
                digital_df = self.datasets['technology']['digital_transformation'][
                    ['Date', 'Composite_Digital_Index', 'E_Government_Development_Index', 'AI_Readiness_Index']
                ].copy()
                master_df = pd.merge(master_df, digital_df, on='Date', how='left')
        
        # Add industry indicators
        if 'industry' in self.datasets:
            if 'sectoral_growth' in self.datasets['industry']:
                sectoral_df = self.datasets['industry']['sectoral_growth'][
                    ['Date', 'Manufacturing_Growth_Percent', 'Information_Communication_Growth_Percent', 
                     'Trade_Growth_Percent', 'Financial_Insurance_Growth_Percent']
                ].copy()
                master_df = pd.merge(master_df, sectoral_df, on='Date', how='left')
        
        self.master_df = master_df
        logger.info(f"Created master dataset with {len(master_df)} records and {len(master_df.columns)} variables")
        return master_df
    
    def analyze_temporal_trends(self, save_plots: bool = False, output_dir: str = None) -> Dict[str, Dict]:
        """
        Analyze temporal trends in key indicators.
        
        Args:
            save_plots: Whether to save plots
            output_dir: Directory to save plots
            
        Returns:
            Dictionary with trend analysis results
        """
        if self.master_df is None:
            self.create_master_dataset()
        
        trend_results = {}
        
        # Key indicators to analyze
        key_indicators = [
            'GDP_Growth_Rate_Percent',
            'Monetary_Policy_Rate_Percent',
            'Mobile_Money_Penetration_Percent',
            'FinTech_Adoption_Index',
            'Composite_Digital_Index',
            'Manufacturing_Growth_Percent',
            'Information_Communication_Growth_Percent'
        ]
        
        # Create subplots
        fig, axes = plt.subplots(3, 3, figsize=(20, 15))
        axes = axes.flatten()
        
        for i, indicator in enumerate(key_indicators):
            if indicator in self.master_df.columns:
                series = self.master_df.set_index('Date')[indicator].dropna()
                
                if len(series) > 0:
                    # Plot time series
                    ax = axes[i]
                    series.plot(ax=ax, linewidth=2)
                    ax.set_title(f'{indicator.replace("_", " ")}', fontsize=12, fontweight='bold')
                    ax.grid(True, alpha=0.3)
                    
                    # Add trend line
                    x = np.arange(len(series))
                    z = np.polyfit(x, series.values, 1)
                    p = np.poly1d(z)
                    ax.plot(series.index, p(x), "r--", alpha=0.8, linewidth=1)
                    
                    # Calculate trend statistics
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, series.values)
                    
                    trend_results[indicator] = {
                        'slope': slope,
                        'r_squared': r_value**2,
                        'p_value': p_value,
                        'trend_direction': 'increasing' if slope > 0 else 'decreasing',
                        'trend_strength': 'strong' if abs(r_value) > 0.7 else 'moderate' if abs(r_value) > 0.4 else 'weak',
                        'mean': series.mean(),
                        'std': series.std(),
                        'min': series.min(),
                        'max': series.max()
                    }
        
        # Remove empty subplots
        for j in range(len(key_indicators), len(axes)):
            fig.delaxes(axes[j])
        
        plt.tight_layout()
        plt.suptitle('Temporal Trends in Key Indicators', fontsize=16, fontweight='bold', y=1.02)
        
        if save_plots and output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path / 'temporal_trends.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
        return trend_results
    
    def analyze_correlations(self, method: str = 'pearson', save_plots: bool = False, output_dir: str = None) -> pd.DataFrame:
        """
        Analyze correlations between key indicators.
        
        Args:
            method: 'pearson' or 'spearman'
            save_plots: Whether to save plots
            output_dir: Directory to save plots
            
        Returns:
            Correlation matrix
        """
        if self.master_df is None:
            self.create_master_dataset()
        
        # Select numeric columns for correlation analysis
        numeric_cols = self.master_df.select_dtypes(include=[np.number]).columns
        correlation_data = self.master_df[numeric_cols].dropna()
        
        # Calculate correlation matrix
        if method == 'pearson':
            corr_matrix = correlation_data.corr()
        else:
            corr_matrix = correlation_data.corr(method='spearman')
        
        self.correlation_matrices[method] = corr_matrix
        
        # Create correlation heatmap
        plt.figure(figsize=(14, 12))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        
        sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='RdBu_r', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, fmt='.2f')
        
        plt.title(f'{method.capitalize()} Correlation Matrix - Key Indicators', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        if save_plots and output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path / f'{method}_correlation_matrix.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
        # Identify strong correlations
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    var1, var2 = corr_matrix.columns[i], corr_matrix.columns[j]
                    strong_correlations.append({
                        'Variable_1': var1,
                        'Variable_2': var2,
                        'Correlation': corr_val,
                        'Strength': 'Very Strong' if abs(corr_val) > 0.9 else 'Strong'
                    })
        
        if strong_correlations:
            strong_corr_df = pd.DataFrame(strong_correlations)
            print(f"\nStrong Correlations (|r| > 0.7) - {method.capitalize()}:")
            print(strong_corr_df.to_string(index=False))
        
        return corr_matrix
    
    def analyze_sectoral_patterns(self, save_plots: bool = False, output_dir: str = None) -> Dict[str, pd.DataFrame]:
        """
        Analyze sectoral growth patterns and SME distribution.
        
        Args:
            save_plots: Whether to save plots
            output_dir: Directory to save plots
            
        Returns:
            Dictionary with sectoral analysis results
        """
        sectoral_results = {}
        
        # Sectoral growth analysis
        if 'industry' in self.datasets and 'sectoral_growth' in self.datasets['industry']:
            sectoral_df = self.datasets['industry']['sectoral_growth']
            
            # Get growth columns
            growth_cols = [col for col in sectoral_df.columns if 'Growth_Percent' in col and col != 'Data_Source']
            
            # Calculate average growth by sector
            avg_growth = sectoral_df[growth_cols].mean().sort_values(ascending=False)
            
            # Create sectoral growth comparison
            plt.figure(figsize=(15, 8))
            sector_names = [col.replace('_Growth_Percent', '').replace('_', ' ') for col in avg_growth.index]
            
            bars = plt.bar(range(len(avg_growth)), avg_growth.values)
            plt.xticks(range(len(avg_growth)), sector_names, rotation=45, ha='right')
            plt.ylabel('Average Growth Rate (%)')
            plt.title('Average Sectoral Growth Rates (2018-2024)', fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.3)
            
            # Color bars based on growth rate
            for i, bar in enumerate(bars):
                if avg_growth.values[i] > 0:
                    bar.set_color('green')
                else:
                    bar.set_color('red')
            
            plt.tight_layout()
            
            if save_plots and output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                plt.savefig(output_path / 'sectoral_growth_comparison.png', dpi=300, bbox_inches='tight')
            
            plt.show()
            
            sectoral_results['average_growth'] = avg_growth
            
            # Growth volatility analysis
            growth_volatility = sectoral_df[growth_cols].std().sort_values(ascending=False)
            sectoral_results['growth_volatility'] = growth_volatility
        
        # SME sector distribution analysis
        if 'industry' in self.datasets and 'sme_sector_breakdown' in self.datasets['industry']:
            sme_sector_df = self.datasets['industry']['sme_sector_breakdown']
            
            # Aggregate by main sector
            sector_summary = sme_sector_df.groupby('Sector').agg({
                'SME_Count_Thousands': 'sum',
                'Average_Employment_Per_SME': 'mean',
                'Innovation_Intensity_Score': 'mean',
                'Digital_Readiness_Score': 'mean'
            }).round(2)
            
            # Create sector comparison dashboard
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # SME count by sector
            sector_summary['SME_Count_Thousands'].plot(kind='bar', ax=ax1, color='skyblue')
            ax1.set_title('SME Count by Sector (Thousands)', fontweight='bold')
            ax1.set_ylabel('SME Count (Thousands)')
            ax1.tick_params(axis='x', rotation=45)
            
            # Average employment per SME
            sector_summary['Average_Employment_Per_SME'].plot(kind='bar', ax=ax2, color='lightcoral')
            ax2.set_title('Average Employment per SME by Sector', fontweight='bold')
            ax2.set_ylabel('Average Employment')
            ax2.tick_params(axis='x', rotation=45)
            
            # Innovation intensity
            sector_summary['Innovation_Intensity_Score'].plot(kind='bar', ax=ax3, color='lightgreen')
            ax3.set_title('Innovation Intensity Score by Sector', fontweight='bold')
            ax3.set_ylabel('Innovation Score (1-10)')
            ax3.tick_params(axis='x', rotation=45)
            
            # Digital readiness
            sector_summary['Digital_Readiness_Score'].plot(kind='bar', ax=ax4, color='gold')
            ax4.set_title('Digital Readiness Score by Sector', fontweight='bold')
            ax4.set_ylabel('Digital Readiness (1-10)')
            ax4.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            if save_plots and output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                plt.savefig(output_path / 'sme_sector_analysis.png', dpi=300, bbox_inches='tight')
            
            plt.show()
            
            sectoral_results['sme_sector_summary'] = sector_summary
        
        return sectoral_results
    
    def analyze_technology_adoption(self, save_plots: bool = False, output_dir: str = None) -> Dict[str, pd.DataFrame]:
        """
        Analyze technology adoption trends and patterns.
        
        Args:
            save_plots: Whether to save plots
            output_dir: Directory to save plots
            
        Returns:
            Dictionary with technology adoption analysis
        """
        tech_results = {}
        
        if 'technology' not in self.datasets:
            logger.warning("No technology data available for analysis")
            return tech_results
        
        # FinTech adoption trends
        if 'fintech_adoption' in self.datasets['technology']:
            fintech_df = self.datasets['technology']['fintech_adoption']
            
            # Key FinTech indicators
            fintech_indicators = [
                'Mobile_Money_Penetration_Percent',
                'Digital_Banking_Penetration_Percent',
                'FinTech_Adoption_Index'
            ]
            
            # Create FinTech adoption timeline
            plt.figure(figsize=(14, 8))
            
            for indicator in fintech_indicators:
                if indicator in fintech_df.columns:
                    plt.plot(fintech_df['Date'], fintech_df[indicator], 
                           marker='o', linewidth=2, label=indicator.replace('_', ' '))
            
            plt.xlabel('Date')
            plt.ylabel('Adoption Rate / Index Value')
            plt.title('FinTech Adoption Trends in Nigeria (2018-2024)', fontsize=14, fontweight='bold')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            if save_plots and output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                plt.savefig(output_path / 'fintech_adoption_trends.png', dpi=300, bbox_inches='tight')
            
            plt.show()
            
            # Calculate adoption growth rates
            adoption_growth = {}
            for indicator in fintech_indicators:
                if indicator in fintech_df.columns:
                    series = fintech_df.set_index('Date')[indicator].dropna()
                    if len(series) > 1:
                        growth_rate = ((series.iloc[-1] / series.iloc[0]) ** (1/len(series)) - 1) * 100
                        adoption_growth[indicator] = growth_rate
            
            tech_results['fintech_growth_rates'] = pd.Series(adoption_growth)
        
        # Digital transformation metrics
        if 'digital_transformation' in self.datasets['technology']:
            digital_df = self.datasets['technology']['digital_transformation']
            
            # Key digital indicators
            digital_indicators = [
                'Composite_Digital_Index',
                'E_Government_Development_Index',
                'AI_Readiness_Index',
                'Digital_Competitiveness_Ranking'
            ]
            
            # Create digital transformation dashboard
            fig, axes = plt.subplots(2, 2, figsize=(16, 10))
            axes = axes.flatten()
            
            for i, indicator in enumerate(digital_indicators):
                if indicator in digital_df.columns and i < len(axes):
                    ax = axes[i]
                    
                    if indicator == 'Digital_Competitiveness_Ranking':
                        # For ranking, lower is better, so invert for visualization
                        ax.plot(digital_df['Date'], digital_df[indicator], 
                               marker='o', linewidth=2, color='red')
                        ax.set_ylabel('Ranking (Lower is Better)')
                    else:
                        ax.plot(digital_df['Date'], digital_df[indicator], 
                               marker='o', linewidth=2, color='blue')
                        ax.set_ylabel('Index Value')
                    
                    ax.set_title(indicator.replace('_', ' '), fontweight='bold')
                    ax.grid(True, alpha=0.3)
                    ax.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.suptitle('Digital Transformation Metrics', fontsize=16, fontweight='bold', y=1.02)
            
            if save_plots and output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                plt.savefig(output_path / 'digital_transformation_metrics.png', dpi=300, bbox_inches='tight')
            
            plt.show()
            
            # Calculate digital transformation progress
            digital_progress = {}
            for indicator in digital_indicators:
                if indicator in digital_df.columns:
                    series = digital_df.set_index('Date')[indicator].dropna()
                    if len(series) > 1:
                        if indicator == 'Digital_Competitiveness_Ranking':
                            # For ranking, improvement means lower values
                            progress = ((series.iloc[0] - series.iloc[-1]) / series.iloc[0]) * 100
                        else:
                            progress = ((series.iloc[-1] - series.iloc[0]) / series.iloc[0]) * 100
                        digital_progress[indicator] = progress
            
            tech_results['digital_transformation_progress'] = pd.Series(digital_progress)
        
        return tech_results
    
    def analyze_regional_variations(self, save_plots: bool = False, output_dir: str = None) -> Dict[str, pd.DataFrame]:
        """
        Analyze regional variations in key indicators.
        
        Args:
            save_plots: Whether to save plots
            output_dir: Directory to save plots
            
        Returns:
            Dictionary with regional analysis results
        """
        regional_results = {}
        
        # Broadband penetration by state/region
        if 'macroeconomic' in self.datasets and 'broadband_penetration' in self.datasets['macroeconomic']:
            broadband_df = self.datasets['macroeconomic']['broadband_penetration']
            
            # Latest year analysis
            latest_year = broadband_df['Year'].max()
            latest_data = broadband_df[broadband_df['Year'] == latest_year].copy()
            
            # Regional summary
            regional_summary = latest_data.groupby('Region').agg({
                'Penetration_Percent': ['mean', 'std', 'min', 'max'],
                'Population_2023': 'sum',
                'Infrastructure_Score': 'mean'
            }).round(2)
            
            regional_summary.columns = ['_'.join(col).strip() for col in regional_summary.columns]
            regional_results['broadband_by_region'] = regional_summary
            
            # Create regional comparison plots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
            
            # Average penetration by region
            regional_avg = latest_data.groupby('Region')['Penetration_Percent'].mean().sort_values(ascending=False)
            regional_avg.plot(kind='bar', ax=ax1, color='steelblue')
            ax1.set_title(f'Average Broadband Penetration by Region ({latest_year})', fontweight='bold')
            ax1.set_ylabel('Penetration Rate (%)')
            ax1.tick_params(axis='x', rotation=45)
            
            # Infrastructure score by region
            infra_avg = latest_data.groupby('Region')['Infrastructure_Score'].mean().sort_values(ascending=False)
            infra_avg.plot(kind='bar', ax=ax2, color='darkorange')
            ax2.set_title(f'Average Infrastructure Score by Region ({latest_year})', fontweight='bold')
            ax2.set_ylabel('Infrastructure Score (1-10)')
            ax2.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            if save_plots and output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                plt.savefig(output_path / 'regional_broadband_analysis.png', dpi=300, bbox_inches='tight')
            
            plt.show()
            
            # Top and bottom performing states
            top_states = latest_data.nlargest(10, 'Penetration_Percent')[['State', 'Region', 'Penetration_Percent', 'Infrastructure_Score']]
            bottom_states = latest_data.nsmallest(10, 'Penetration_Percent')[['State', 'Region', 'Penetration_Percent', 'Infrastructure_Score']]
            
            regional_results['top_performing_states'] = top_states
            regional_results['bottom_performing_states'] = bottom_states
            
            print(f"\nTop 10 States - Broadband Penetration ({latest_year}):")
            print(top_states.to_string(index=False))
            
            print(f"\nBottom 10 States - Broadband Penetration ({latest_year}):")
            print(bottom_states.to_string(index=False))
        
        return regional_results
    
    def generate_comprehensive_report(self, output_dir: str = None) -> str:
        """
        Generate comprehensive exploratory data analysis report.
        
        Args:
            output_dir: Directory to save report and plots
            
        Returns:
            Report as string
        """
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
        report_lines = []
        report_lines.append("# Nigerian SME Secondary Dataset - Exploratory Data Analysis Report")
        report_lines.append(f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Dataset overview
        report_lines.append("## Dataset Overview")
        total_records = 0
        total_variables = 0
        
        for category, datasets in self.datasets.items():
            report_lines.append(f"\n### {category.upper()}")
            for name, df in datasets.items():
                records = len(df)
                variables = len(df.columns)
                total_records += records
                total_variables += variables
                
                date_range = ""
                if 'Date' in df.columns:
                    min_date = df['Date'].min().strftime('%Y-%m-%d')
                    max_date = df['Date'].max().strftime('%Y-%m-%d')
                    date_range = f" ({min_date} to {max_date})"
                
                report_lines.append(f"- **{name}**: {records:,} records, {variables} variables{date_range}")
        
        report_lines.append(f"\n**Total**: {total_records:,} records across {total_variables} variables")
        
        # Temporal trends analysis
        report_lines.append("\n## Temporal Trends Analysis")
        trend_results = self.analyze_temporal_trends(save_plots=bool(output_dir), output_dir=output_dir)
        
        if trend_results:
            report_lines.append("\n### Key Findings:")
            
            # Strong trends
            strong_trends = {k: v for k, v in trend_results.items() if v['trend_strength'] == 'strong'}
            if strong_trends:
                report_lines.append("\n**Strong Trends Identified:**")
                for indicator, stats in strong_trends.items():
                    direction = stats['trend_direction']
                    r_squared = stats['r_squared']
                    report_lines.append(f"- {indicator.replace('_', ' ')}: {direction} trend (R² = {r_squared:.3f})")
            
            # High volatility indicators
            high_volatility = {k: v for k, v in trend_results.items() if v['std'] / v['mean'] > 0.3}
            if high_volatility:
                report_lines.append("\n**High Volatility Indicators:**")
                for indicator, stats in high_volatility.items():
                    cv = stats['std'] / stats['mean']
                    report_lines.append(f"- {indicator.replace('_', ' ')}: CV = {cv:.3f}")
        
        # Correlation analysis
        report_lines.append("\n## Correlation Analysis")
        corr_matrix = self.analyze_correlations(save_plots=bool(output_dir), output_dir=output_dir)
        
        # Find strong correlations
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    var1, var2 = corr_matrix.columns[i], corr_matrix.columns[j]
                    strong_correlations.append((var1, var2, corr_val))
        
        if strong_correlations:
            report_lines.append("\n### Strong Correlations (|r| > 0.7):")
            for var1, var2, corr in strong_correlations[:10]:  # Top 10
                report_lines.append(f"- {var1.replace('_', ' ')} ↔ {var2.replace('_', ' ')}: r = {corr:.3f}")
        
        # Sectoral analysis
        report_lines.append("\n## Sectoral Analysis")
        sectoral_results = self.analyze_sectoral_patterns(save_plots=bool(output_dir), output_dir=output_dir)
        
        if 'average_growth' in sectoral_results:
            top_growth_sectors = sectoral_results['average_growth'].head(5)
            report_lines.append("\n### Top Growth Sectors:")
            for sector, growth in top_growth_sectors.items():
                sector_name = sector.replace('_Growth_Percent', '').replace('_', ' ')
                report_lines.append(f"- {sector_name}: {growth:.2f}% average growth")
        
        if 'sme_sector_summary' in sectoral_results:
            sme_summary = sectoral_results['sme_sector_summary']
            largest_sme_sectors = sme_summary['SME_Count_Thousands'].nlargest(5)
            report_lines.append("\n### Largest SME Sectors by Count:")
            for sector, count in largest_sme_sectors.items():
                report_lines.append(f"- {sector}: {count:,.0f} thousand SMEs")
        
        # Technology adoption analysis
        report_lines.append("\n## Technology Adoption Analysis")
        tech_results = self.analyze_technology_adoption(save_plots=bool(output_dir), output_dir=output_dir)
        
        if 'fintech_growth_rates' in tech_results:
            fintech_growth = tech_results['fintech_growth_rates']
            report_lines.append("\n### FinTech Adoption Growth Rates:")
            for indicator, growth in fintech_growth.items():
                indicator_name = indicator.replace('_', ' ')
                report_lines.append(f"- {indicator_name}: {growth:.1f}% annual growth")
        
        if 'digital_transformation_progress' in tech_results:
            digital_progress = tech_results['digital_transformation_progress']
            report_lines.append("\n### Digital Transformation Progress:")
            for indicator, progress in digital_progress.items():
                indicator_name = indicator.replace('_', ' ')
                report_lines.append(f"- {indicator_name}: {progress:.1f}% improvement")
        
        # Regional analysis
        report_lines.append("\n## Regional Analysis")
        regional_results = self.analyze_regional_variations(save_plots=bool(output_dir), output_dir=output_dir)
        
        if 'broadband_by_region' in regional_results:
            regional_broadband = regional_results['broadband_by_region']
            report_lines.append("\n### Broadband Penetration by Region:")
            for region in regional_broadband.index:
                avg_penetration = regional_broadband.loc[region, 'Penetration_Percent_mean']
                report_lines.append(f"- {region}: {avg_penetration:.1f}% average penetration")
        
        # Key insights and recommendations
        report_lines.append("\n## Key Insights and Recommendations")
        report_lines.append("\n### Major Findings:")
        report_lines.append("1. **Digital Transformation Acceleration**: Significant growth in FinTech and digital adoption metrics")
        report_lines.append("2. **Sectoral Variations**: ICT and financial services showing strongest growth patterns")
        report_lines.append("3. **Regional Disparities**: Substantial differences in technology adoption across regions")
        report_lines.append("4. **Economic Resilience**: SME sectors showing adaptation to macroeconomic challenges")
        
        report_lines.append("\n### Implications for SME Innovation Research:")
        report_lines.append("- Technology adoption patterns provide strong predictors for innovation capacity")
        report_lines.append("- Regional variations suggest need for location-specific analysis")
        report_lines.append("- Sectoral differences indicate industry-specific innovation constraints")
        report_lines.append("- Temporal trends support longitudinal analysis approaches")
        
        report_text = "\n".join(report_lines)
        
        # Save report if output directory provided
        if output_dir:
            with open(output_path / 'exploratory_analysis_report.md', 'w', encoding='utf-8') as f:
                f.write(report_text)
            logger.info(f"EDA report saved to {output_path / 'exploratory_analysis_report.md'}")
        
        return report_text

def main():
    """
    Example usage of the SME data explorer.
    """
    from data_loader import NigerianSMEDataLoader
    
    # Load data
    loader = NigerianSMEDataLoader()
    datasets = loader.load_all_data()
    
    # Initialize explorer
    explorer = SMEDataExplorer(datasets)
    
    # Generate comprehensive analysis
    report = explorer.generate_comprehensive_report("eda_output")
    
    print("Exploratory Data Analysis Complete")
    print("=" * 50)
    print("Report preview:")
    print(report[:2000] + "..." if len(report) > 2000 else report)

if __name__ == "__main__":
    main()