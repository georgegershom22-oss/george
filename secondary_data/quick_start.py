#!/usr/bin/env python3
"""
Quick Start Script for Nigerian SME Innovation Dataset
Provides easy access to all datasets and basic analysis
"""

import pandas as pd
import os
import sys
from datetime import datetime

class SMEDataQuickStart:
    """Quick start class for accessing SME innovation datasets"""
    
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.datasets = {}
        print("="*60)
        print("NIGERIAN SME INNOVATION SECONDARY DATASET")
        print("Research: Leveraging ML for SME Innovation Analysis")
        print("="*60)
        
    def load_all_datasets(self):
        """Load all available datasets"""
        print("\nLoading all datasets...")
        
        dataset_paths = {
            'gdp_growth': 'macroeconomic/gdp_growth_rate.csv',
            'inflation': 'macroeconomic/inflation_rates.csv',
            'interest_rates': 'macroeconomic/interest_rates.csv',
            'broadband': 'macroeconomic/broadband_penetration.csv',
            'ease_business': 'macroeconomic/ease_of_doing_business.csv',
            'sectoral_growth': 'industry_specific/sectoral_growth_rates.csv',
            'sme_landscape': 'industry_specific/sme_landscape_data.csv',
            'fintech': 'technology_adoption/mobile_money_fintech_adoption.csv',
            'ict_index': 'technology_adoption/ict_development_index.csv'
        }
        
        for name, path in dataset_paths.items():
            full_path = os.path.join(self.base_path, path)
            try:
                self.datasets[name] = pd.read_csv(full_path)
                print(f"  ✓ Loaded {name}: {self.datasets[name].shape}")
            except Exception as e:
                print(f"  ✗ Failed to load {name}: {e}")
        
        print(f"\nSuccessfully loaded {len(self.datasets)} datasets")
        return self.datasets
    
    def get_dataset_info(self):
        """Display information about all datasets"""
        print("\n" + "="*60)
        print("DATASET INFORMATION")
        print("="*60)
        
        for name, df in self.datasets.items():
            print(f"\n{name.upper()}:")
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {', '.join(df.columns[:5])}...")
            print(f"  Memory: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")
    
    def get_latest_metrics(self):
        """Get latest key metrics"""
        print("\n" + "="*60)
        print("LATEST KEY METRICS (2024)")
        print("="*60)
        
        metrics = {}
        
        # GDP Growth
        if 'gdp_growth' in self.datasets:
            latest_gdp = self.datasets['gdp_growth'].iloc[-1]
            metrics['GDP Growth Rate'] = f"{latest_gdp['gdp_growth_rate']:.2f}%"
            metrics['SME GDP Contribution'] = f"{latest_gdp['sme_contribution_percent']:.1f}%"
        
        # Inflation
        if 'inflation' in self.datasets:
            latest_inflation = self.datasets['inflation'].iloc[-1]
            metrics['Headline Inflation'] = f"{latest_inflation['headline_inflation']:.1f}%"
            metrics['Food Inflation'] = f"{latest_inflation['food_inflation']:.1f}%"
        
        # Interest Rates
        if 'interest_rates' in self.datasets:
            latest_interest = self.datasets['interest_rates'].iloc[-1]
            metrics['Monetary Policy Rate'] = f"{latest_interest['monetary_policy_rate']:.2f}%"
            metrics['SME Lending Rate'] = f"{latest_interest['sme_lending_rate_average']:.1f}%"
        
        # Broadband
        if 'broadband' in self.datasets:
            national = self.datasets['broadband'][self.datasets['broadband']['state'] == 'NATIONAL AVERAGE'].iloc[0]
            metrics['National Broadband'] = f"{national['2024']:.1f}%"
            metrics['Urban Penetration'] = f"{national['urban_penetration_2024']:.1f}%"
            metrics['Rural Penetration'] = f"{national['rural_penetration_2024']:.1f}%"
        
        # SME Landscape
        if 'sme_landscape' in self.datasets:
            latest_sme = self.datasets['sme_landscape'].iloc[-1]
            metrics['Total SMEs'] = f"{latest_sme['total_smes_millions']:.1f} million"
            metrics['Tech-Enabled SMEs'] = f"{latest_sme['tech_enabled_smes_percent']:.1f}%"
            metrics['Fintech Adoption'] = f"{latest_sme['fintech_adoption_rate']:.1f}%"
            metrics['E-commerce Participation'] = f"{latest_sme['e_commerce_participation']:.1f}%"
        
        # Financial Inclusion
        if 'fintech' in self.datasets:
            latest_fintech = self.datasets['fintech'].iloc[-1]
            metrics['Financial Inclusion'] = f"{latest_fintech['financial_inclusion_rate']:.1f}%"
            metrics['Mobile Money Accounts'] = f"{latest_fintech['mobile_money_accounts_millions']:.1f} million"
        
        # ICT Index
        if 'ict_index' in self.datasets:
            latest_ict = self.datasets['ict_index'].iloc[-1]
            metrics['ICT Development Index'] = f"{latest_ict['ict_development_index']:.2f}"
            metrics['Internet Users'] = f"{latest_ict['internet_users_percent']:.1f}%"
        
        for key, value in metrics.items():
            print(f"  {key}: {value}")
        
        return metrics
    
    def export_summary(self, output_format='csv'):
        """Export summary statistics"""
        print("\n" + "="*60)
        print("EXPORTING SUMMARY STATISTICS")
        print("="*60)
        
        summaries = {}
        
        for name, df in self.datasets.items():
            # Get numeric columns only
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            if len(numeric_cols) > 0:
                summary = df[numeric_cols].describe().T
                summary['dataset'] = name
                summaries[name] = summary
        
        # Combine all summaries
        all_summaries = pd.concat(summaries.values(), ignore_index=True)
        
        # Export
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"summary_statistics_{timestamp}.{output_format}"
        
        if output_format == 'csv':
            all_summaries.to_csv(filename, index=False)
        elif output_format == 'excel':
            all_summaries.to_excel(filename, index=False)
        
        print(f"  Summary exported to: {filename}")
        print(f"  Total variables summarized: {len(all_summaries)}")
        
        return all_summaries
    
    def search_variable(self, keyword):
        """Search for variables across all datasets"""
        print(f"\n" + "="*60)
        print(f"SEARCHING FOR: '{keyword}'")
        print("="*60)
        
        results = []
        
        for dataset_name, df in self.datasets.items():
            matching_cols = [col for col in df.columns if keyword.lower() in col.lower()]
            
            if matching_cols:
                print(f"\n{dataset_name.upper()}:")
                for col in matching_cols:
                    print(f"  • {col}")
                    # Get sample values
                    if df[col].dtype in ['float64', 'int64']:
                        print(f"    Range: {df[col].min():.2f} - {df[col].max():.2f}")
                    else:
                        unique_count = df[col].nunique()
                        print(f"    Unique values: {unique_count}")
                    
                    results.append({
                        'dataset': dataset_name,
                        'variable': col,
                        'dtype': str(df[col].dtype)
                    })
        
        if not results:
            print(f"  No variables found matching '{keyword}'")
        
        return results
    
    def get_time_series(self, variable_name, dataset_name=None):
        """Extract time series for a specific variable"""
        print(f"\n" + "="*60)
        print(f"EXTRACTING TIME SERIES: {variable_name}")
        print("="*60)
        
        if dataset_name:
            if dataset_name in self.datasets:
                df = self.datasets[dataset_name]
                if variable_name in df.columns:
                    return df[['year', variable_name]] if 'year' in df.columns else df[variable_name]
                else:
                    print(f"  Variable '{variable_name}' not found in {dataset_name}")
        else:
            # Search all datasets
            for name, df in self.datasets.items():
                if variable_name in df.columns:
                    print(f"  Found in {name}")
                    return df[['year', variable_name]] if 'year' in df.columns else df[variable_name]
            
            print(f"  Variable '{variable_name}' not found in any dataset")
        
        return None
    
    def run_quick_analysis(self):
        """Run a quick analysis of the data"""
        print("\n" + "="*60)
        print("QUICK ANALYSIS RESULTS")
        print("="*60)
        
        # Innovation growth
        if 'sme_landscape' in self.datasets:
            sme_df = self.datasets['sme_landscape']
            sme_df = sme_df[sme_df['year'].notna()]
            
            start_tech = sme_df.iloc[0]['tech_enabled_smes_percent']
            end_tech = sme_df.iloc[-1]['tech_enabled_smes_percent']
            growth = ((end_tech - start_tech) / start_tech) * 100
            
            print(f"\n1. INNOVATION ADOPTION GROWTH:")
            print(f"   2015: {start_tech:.1f}% → 2024: {end_tech:.1f}%")
            print(f"   Total Growth: {growth:.1f}%")
        
        # Financial inclusion progress
        if 'fintech' in self.datasets:
            fintech_df = self.datasets['fintech']
            start_inclusion = fintech_df.iloc[0]['financial_inclusion_rate']
            end_inclusion = fintech_df.iloc[-1]['financial_inclusion_rate']
            
            print(f"\n2. FINANCIAL INCLUSION PROGRESS:")
            print(f"   2015: {start_inclusion:.1f}% → 2024: {end_inclusion:.1f}%")
            print(f"   Improvement: {end_inclusion - start_inclusion:.1f} percentage points")
        
        # Regional disparities
        if 'broadband' in self.datasets:
            broadband_df = self.datasets['broadband']
            broadband_df = broadband_df[broadband_df['state'] != 'NATIONAL AVERAGE']
            
            max_state = broadband_df.loc[broadband_df['2024'].idxmax()]
            min_state = broadband_df.loc[broadband_df['2024'].idxmin()]
            
            print(f"\n3. DIGITAL DIVIDE (2024):")
            print(f"   Highest: {max_state['state']} ({max_state['2024']:.1f}%)")
            print(f"   Lowest: {min_state['state']} ({min_state['2024']:.1f}%)")
            print(f"   Gap: {max_state['2024'] - min_state['2024']:.1f} percentage points")
        
        # Interest rate burden
        if 'interest_rates' in self.datasets:
            interest_df = self.datasets['interest_rates']
            avg_sme_rate = interest_df['sme_lending_rate_average'].mean()
            avg_mpr = interest_df['monetary_policy_rate'].mean()
            spread = avg_sme_rate - avg_mpr
            
            print(f"\n4. INTEREST RATE BURDEN:")
            print(f"   Average SME Lending Rate: {avg_sme_rate:.1f}%")
            print(f"   Average MPR: {avg_mpr:.1f}%")
            print(f"   Spread: {spread:.1f} percentage points")

def main():
    """Main execution function"""
    print("\nInitializing SME Innovation Dataset Quick Start...")
    
    qs = SMEDataQuickStart()
    
    # Load all datasets
    datasets = qs.load_all_datasets()
    
    # Display dataset info
    qs.get_dataset_info()
    
    # Show latest metrics
    qs.get_latest_metrics()
    
    # Run quick analysis
    qs.run_quick_analysis()
    
    # Export summary
    qs.export_summary()
    
    print("\n" + "="*60)
    print("QUICK START COMPLETE")
    print("="*60)
    print("\nDatasets are now available in the 'datasets' dictionary.")
    print("Use qs.search_variable('keyword') to search for specific variables.")
    print("Use qs.get_time_series('variable_name') to extract time series data.")
    
    return qs

if __name__ == "__main__":
    quick_start = main()