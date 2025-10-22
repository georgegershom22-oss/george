"""
Data Validation and Quality Assessment for Nigerian SME Secondary Dataset
Comprehensive validation routines to ensure data integrity and quality.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from typing import Dict, List, Tuple, Optional
import warnings
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataValidator:
    """
    Comprehensive data validation class for the Nigerian SME secondary dataset.
    """
    
    def __init__(self, datasets: Dict[str, Dict[str, pd.DataFrame]]):
        """
        Initialize validator with loaded datasets.
        
        Args:
            datasets: Dictionary of loaded datasets from DataLoader
        """
        self.datasets = datasets
        self.validation_results = {}
        
    def validate_completeness(self) -> Dict[str, Dict[str, float]]:
        """
        Validate data completeness across all datasets.
        
        Returns:
            Dictionary with completeness metrics
        """
        completeness_report = {}
        
        for category, datasets in self.datasets.items():
            completeness_report[category] = {}
            
            for name, df in datasets.items():
                # Overall completeness
                total_cells = len(df) * len(df.columns)
                missing_cells = df.isnull().sum().sum()
                completeness = ((total_cells - missing_cells) / total_cells) * 100
                
                # Column-wise completeness
                column_completeness = ((len(df) - df.isnull().sum()) / len(df) * 100).to_dict()
                
                # Time series completeness (if Date column exists)
                time_completeness = None
                if 'Date' in df.columns:
                    date_range = pd.date_range(df['Date'].min(), df['Date'].max(), freq='D')
                    actual_dates = len(df['Date'].unique())
                    expected_dates = len(date_range)
                    time_completeness = (actual_dates / expected_dates) * 100
                
                completeness_report[category][name] = {
                    'overall_completeness': completeness,
                    'column_completeness': column_completeness,
                    'time_completeness': time_completeness,
                    'missing_patterns': self._identify_missing_patterns(df)
                }
        
        self.validation_results['completeness'] = completeness_report
        return completeness_report
    
    def validate_consistency(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Validate data consistency within and across datasets.
        
        Returns:
            Dictionary with consistency issues
        """
        consistency_report = {}
        
        for category, datasets in self.datasets.items():
            consistency_report[category] = {}
            
            for name, df in datasets.items():
                issues = []
                
                # Check for duplicate records
                if df.duplicated().any():
                    duplicates = df.duplicated().sum()
                    issues.append(f"Found {duplicates} duplicate records")
                
                # Check date consistency
                if 'Date' in df.columns:
                    if df['Date'].isnull().any():
                        issues.append("Missing dates found")
                    
                    # Check for future dates
                    future_dates = df[df['Date'] > pd.Timestamp.now()]
                    if len(future_dates) > 0:
                        issues.append(f"Found {len(future_dates)} future dates")
                
                # Check numeric ranges
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    if col.endswith('_Percent'):
                        # Percentage values should be 0-100 (or reasonable range)
                        invalid_pct = df[(df[col] < 0) | (df[col] > 200)]
                        if len(invalid_pct) > 0:
                            issues.append(f"{col}: {len(invalid_pct)} values outside 0-200% range")
                    
                    elif 'Growth' in col:
                        # Growth rates should be reasonable (-50% to +100%)
                        invalid_growth = df[(df[col] < -50) | (df[col] > 100)]
                        if len(invalid_growth) > 0:
                            issues.append(f"{col}: {len(invalid_growth)} extreme growth values")
                    
                    elif 'Rate' in col and 'Percent' in col:
                        # Interest rates should be reasonable (0-50%)
                        invalid_rates = df[(df[col] < 0) | (df[col] > 50)]
                        if len(invalid_rates) > 0:
                            issues.append(f"{col}: {len(invalid_rates)} values outside 0-50% range")
                
                # Check categorical consistency
                categorical_cols = df.select_dtypes(include=['object']).columns
                for col in categorical_cols:
                    if col not in ['Date', 'Notes', 'Data_Source', 'Methodology']:
                        unique_values = df[col].nunique()
                        if unique_values > len(df) * 0.8:  # Too many unique values
                            issues.append(f"{col}: Suspiciously high cardinality ({unique_values} unique values)")
                
                consistency_report[category][name] = issues
        
        self.validation_results['consistency'] = consistency_report
        return consistency_report
    
    def validate_outliers(self, method: str = 'iqr') -> Dict[str, Dict[str, Dict[str, int]]]:
        """
        Detect outliers in numeric variables.
        
        Args:
            method: 'iqr', 'zscore', or 'both'
            
        Returns:
            Dictionary with outlier counts by variable
        """
        outlier_report = {}
        
        for category, datasets in self.datasets.items():
            outlier_report[category] = {}
            
            for name, df in datasets.items():
                variable_outliers = {}
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                
                for col in numeric_cols:
                    series = df[col].dropna()
                    if len(series) == 0:
                        continue
                    
                    outliers_iqr = 0
                    outliers_zscore = 0
                    
                    if method in ['iqr', 'both']:
                        Q1 = series.quantile(0.25)
                        Q3 = series.quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        outliers_iqr = len(series[(series < lower_bound) | (series > upper_bound)])
                    
                    if method in ['zscore', 'both']:
                        z_scores = np.abs(stats.zscore(series))
                        outliers_zscore = len(series[z_scores > 3])
                    
                    if method == 'iqr':
                        variable_outliers[col] = outliers_iqr
                    elif method == 'zscore':
                        variable_outliers[col] = outliers_zscore
                    else:  # both
                        variable_outliers[col] = {
                            'iqr_outliers': outliers_iqr,
                            'zscore_outliers': outliers_zscore
                        }
                
                outlier_report[category][name] = variable_outliers
        
        self.validation_results['outliers'] = outlier_report
        return outlier_report
    
    def validate_temporal_patterns(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Validate temporal patterns and trends in time series data.
        
        Returns:
            Dictionary with temporal validation results
        """
        temporal_report = {}
        
        for category, datasets in self.datasets.items():
            temporal_report[category] = {}
            
            for name, df in datasets.items():
                if 'Date' not in df.columns:
                    continue
                
                df_sorted = df.sort_values('Date')
                numeric_cols = df_sorted.select_dtypes(include=[np.number]).columns
                
                pattern_analysis = {}
                
                for col in numeric_cols:
                    series = df_sorted.set_index('Date')[col].dropna()
                    if len(series) < 3:
                        continue
                    
                    # Trend analysis
                    x = np.arange(len(series))
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, series.values)
                    
                    # Seasonality check (if enough data points)
                    seasonality_strength = 0
                    if len(series) >= 12:
                        # Simple seasonality measure using autocorrelation
                        try:
                            autocorr = series.autocorr(lag=4)  # Quarterly seasonality
                            seasonality_strength = abs(autocorr) if not np.isnan(autocorr) else 0
                        except:
                            seasonality_strength = 0
                    
                    # Volatility measure
                    volatility = series.std() / series.mean() if series.mean() != 0 else 0
                    
                    # Structural breaks (simple test)
                    mid_point = len(series) // 2
                    first_half_mean = series.iloc[:mid_point].mean()
                    second_half_mean = series.iloc[mid_point:].mean()
                    structural_break_indicator = abs(second_half_mean - first_half_mean) / first_half_mean if first_half_mean != 0 else 0
                    
                    pattern_analysis[col] = {
                        'trend_slope': slope,
                        'trend_r_squared': r_value**2,
                        'trend_p_value': p_value,
                        'seasonality_strength': seasonality_strength,
                        'volatility': volatility,
                        'structural_break_indicator': structural_break_indicator
                    }
                
                temporal_report[category][name] = pattern_analysis
        
        self.validation_results['temporal'] = temporal_report
        return temporal_report
    
    def validate_cross_dataset_consistency(self) -> Dict[str, List[str]]:
        """
        Validate consistency across different datasets.
        
        Returns:
            Dictionary with cross-dataset consistency issues
        """
        cross_validation_issues = {}
        
        # Check date range consistency
        date_ranges = {}
        for category, datasets in self.datasets.items():
            for name, df in datasets.items():
                if 'Date' in df.columns:
                    date_ranges[f"{category}_{name}"] = {
                        'min_date': df['Date'].min(),
                        'max_date': df['Date'].max(),
                        'count': len(df)
                    }
        
        # Identify datasets with significantly different date ranges
        if date_ranges:
            min_start = min([info['min_date'] for info in date_ranges.values()])
            max_end = max([info['max_date'] for info in date_ranges.values()])
            
            date_range_issues = []
            for dataset, info in date_ranges.items():
                coverage = (info['max_date'] - info['min_date']).days / (max_end - min_start).days
                if coverage < 0.5:  # Less than 50% coverage
                    date_range_issues.append(f"{dataset}: Limited temporal coverage ({coverage:.1%})")
            
            cross_validation_issues['date_range_consistency'] = date_range_issues
        
        # Check for logical relationships between related indicators
        logical_issues = []
        
        # Example: GDP growth and sectoral growth should be related
        try:
            gdp_data = self.datasets['macroeconomic']['gdp_growth']
            sectoral_data = self.datasets['industry']['sectoral_growth']
            
            # Merge on year for comparison
            gdp_annual = gdp_data.groupby(gdp_data['Date'].dt.year)['GDP_Growth_Rate_Percent'].mean()
            sectoral_annual = sectoral_data.groupby(sectoral_data['Date'].dt.year)['Manufacturing_Growth_Percent'].mean()
            
            common_years = set(gdp_annual.index) & set(sectoral_annual.index)
            if len(common_years) > 3:
                correlation = gdp_annual.loc[common_years].corr(sectoral_annual.loc[common_years])
                if abs(correlation) < 0.3:  # Weak correlation might indicate issues
                    logical_issues.append(f"Weak correlation between GDP and manufacturing growth: {correlation:.3f}")
        except Exception as e:
            logical_issues.append(f"Could not validate GDP-sectoral relationship: {str(e)}")
        
        cross_validation_issues['logical_consistency'] = logical_issues
        
        self.validation_results['cross_dataset'] = cross_validation_issues
        return cross_validation_issues
    
    def _identify_missing_patterns(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Identify patterns in missing data.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary describing missing data patterns
        """
        patterns = {}
        
        # Check if missing data is concentrated in specific time periods
        if 'Date' in df.columns:
            missing_by_date = df.groupby('Date').apply(lambda x: x.isnull().sum().sum())
            if missing_by_date.max() > missing_by_date.mean() * 2:
                worst_date = missing_by_date.idxmax()
                patterns['temporal_concentration'] = f"High missing data on {worst_date}"
        
        # Check if missing data is concentrated in specific columns
        missing_by_column = df.isnull().sum()
        if missing_by_column.max() > len(df) * 0.5:
            worst_column = missing_by_column.idxmax()
            patterns['column_concentration'] = f"Column '{worst_column}' has {missing_by_column.max()} missing values"
        
        # Check for systematic missing patterns
        missing_matrix = df.isnull()
        if len(missing_matrix.columns) > 1:
            # Check if certain columns are always missing together
            correlation_matrix = missing_matrix.corr()
            high_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr = correlation_matrix.iloc[i, j]
                    if corr > 0.8:
                        col1, col2 = correlation_matrix.columns[i], correlation_matrix.columns[j]
                        high_correlations.append(f"{col1} & {col2}: {corr:.3f}")
            
            if high_correlations:
                patterns['systematic_missing'] = "; ".join(high_correlations)
        
        return patterns
    
    def generate_validation_report(self, output_path: str = None) -> str:
        """
        Generate comprehensive validation report.
        
        Args:
            output_path: Path to save the report
            
        Returns:
            Report as string
        """
        # Run all validations
        self.validate_completeness()
        self.validate_consistency()
        self.validate_outliers()
        self.validate_temporal_patterns()
        self.validate_cross_dataset_consistency()
        
        report_lines = []
        report_lines.append("# Nigerian SME Secondary Dataset - Validation Report")
        report_lines.append(f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Completeness summary
        report_lines.append("## Data Completeness Summary")
        completeness = self.validation_results['completeness']
        for category, datasets in completeness.items():
            report_lines.append(f"\n### {category.upper()}")
            for name, metrics in datasets.items():
                report_lines.append(f"- **{name}**: {metrics['overall_completeness']:.1f}% complete")
                if metrics['time_completeness']:
                    report_lines.append(f"  - Temporal coverage: {metrics['time_completeness']:.1f}%")
                if metrics['missing_patterns']:
                    for pattern_type, pattern_desc in metrics['missing_patterns'].items():
                        report_lines.append(f"  - {pattern_type}: {pattern_desc}")
        
        # Consistency issues
        report_lines.append("\n## Data Consistency Issues")
        consistency = self.validation_results['consistency']
        total_issues = 0
        for category, datasets in consistency.items():
            category_issues = []
            for name, issues in datasets.items():
                if issues:
                    category_issues.extend([f"{name}: {issue}" for issue in issues])
                    total_issues += len(issues)
            
            if category_issues:
                report_lines.append(f"\n### {category.upper()}")
                for issue in category_issues:
                    report_lines.append(f"- {issue}")
        
        if total_issues == 0:
            report_lines.append("No major consistency issues detected.")
        
        # Outlier summary
        report_lines.append("\n## Outlier Detection Summary")
        outliers = self.validation_results['outliers']
        for category, datasets in outliers.items():
            report_lines.append(f"\n### {category.upper()}")
            for name, variables in datasets.items():
                outlier_vars = [var for var, count in variables.items() if count > 0]
                if outlier_vars:
                    report_lines.append(f"- **{name}**: Outliers detected in {len(outlier_vars)} variables")
                    for var in outlier_vars[:5]:  # Show top 5
                        count = variables[var]
                        report_lines.append(f"  - {var}: {count} outliers")
        
        # Temporal patterns
        report_lines.append("\n## Temporal Pattern Analysis")
        temporal = self.validation_results['temporal']
        for category, datasets in temporal.items():
            report_lines.append(f"\n### {category.upper()}")
            for name, patterns in datasets.items():
                strong_trends = [var for var, metrics in patterns.items() 
                               if metrics['trend_r_squared'] > 0.5 and metrics['trend_p_value'] < 0.05]
                if strong_trends:
                    report_lines.append(f"- **{name}**: Strong trends in {len(strong_trends)} variables")
                
                high_volatility = [var for var, metrics in patterns.items() 
                                 if metrics['volatility'] > 0.5]
                if high_volatility:
                    report_lines.append(f"- **{name}**: High volatility in {len(high_volatility)} variables")
        
        # Cross-dataset issues
        report_lines.append("\n## Cross-Dataset Validation")
        cross_issues = self.validation_results['cross_dataset']
        for issue_type, issues in cross_issues.items():
            if issues:
                report_lines.append(f"\n### {issue_type.replace('_', ' ').title()}")
                for issue in issues:
                    report_lines.append(f"- {issue}")
        
        # Overall assessment
        report_lines.append("\n## Overall Data Quality Assessment")
        
        # Calculate overall quality score
        avg_completeness = np.mean([
            metrics['overall_completeness'] 
            for datasets in completeness.values() 
            for metrics in datasets.values()
        ])
        
        quality_score = avg_completeness
        if total_issues > 10:
            quality_score -= 10
        elif total_issues > 5:
            quality_score -= 5
        
        report_lines.append(f"- **Overall Quality Score**: {quality_score:.1f}/100")
        report_lines.append(f"- **Average Completeness**: {avg_completeness:.1f}%")
        report_lines.append(f"- **Total Consistency Issues**: {total_issues}")
        
        if quality_score >= 85:
            report_lines.append("- **Assessment**: High quality dataset suitable for analysis")
        elif quality_score >= 70:
            report_lines.append("- **Assessment**: Good quality dataset with minor issues")
        elif quality_score >= 50:
            report_lines.append("- **Assessment**: Moderate quality dataset requiring attention to identified issues")
        else:
            report_lines.append("- **Assessment**: Dataset requires significant quality improvements")
        
        report_text = "\n".join(report_lines)
        
        # Save report if path provided
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            logger.info(f"Validation report saved to {output_path}")
        
        return report_text
    
    def create_validation_visualizations(self, output_dir: str = None):
        """
        Create visualizations for data validation results.
        
        Args:
            output_dir: Directory to save visualization files
        """
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Completeness heatmap
        plt.figure(figsize=(12, 8))
        completeness_data = []
        labels = []
        
        for category, datasets in self.validation_results['completeness'].items():
            for name, metrics in datasets.items():
                completeness_data.append(metrics['overall_completeness'])
                labels.append(f"{category}_{name}")
        
        plt.barh(labels, completeness_data)
        plt.xlabel('Completeness (%)')
        plt.title('Data Completeness by Dataset')
        plt.tight_layout()
        
        if output_dir:
            plt.savefig(output_path / 'completeness_chart.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Outlier summary
        if 'outliers' in self.validation_results:
            plt.figure(figsize=(10, 6))
            outlier_counts = []
            dataset_names = []
            
            for category, datasets in self.validation_results['outliers'].items():
                for name, variables in datasets.items():
                    total_outliers = sum(count for count in variables.values() if isinstance(count, int))
                    outlier_counts.append(total_outliers)
                    dataset_names.append(f"{category}_{name}")
            
            plt.bar(dataset_names, outlier_counts)
            plt.xlabel('Dataset')
            plt.ylabel('Total Outliers')
            plt.title('Outlier Count by Dataset')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            if output_dir:
                plt.savefig(output_path / 'outliers_chart.png', dpi=300, bbox_inches='tight')
            plt.show()

def main():
    """
    Example usage of the data validator.
    """
    from data_loader import NigerianSMEDataLoader
    
    # Load data
    loader = NigerianSMEDataLoader()
    datasets = loader.load_all_data()
    
    # Initialize validator
    validator = DataValidator(datasets)
    
    # Generate validation report
    report = validator.generate_validation_report("validation_report.md")
    print("Validation Report Generated")
    print("=" * 50)
    print(report[:1000] + "..." if len(report) > 1000 else report)
    
    # Create visualizations
    validator.create_validation_visualizations("validation_plots")

if __name__ == "__main__":
    main()