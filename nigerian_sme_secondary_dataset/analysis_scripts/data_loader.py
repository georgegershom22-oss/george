"""
Data Loader for Nigerian SME Secondary Dataset
Provides functions to load, validate, and preprocess the secondary dataset
for machine learning analysis of SME innovation adoption and constraints.
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
import warnings
from typing import Dict, List, Optional, Tuple, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NigerianSMEDataLoader:
    """
    Main class for loading and preprocessing Nigerian SME secondary dataset.
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize the data loader.
        
        Args:
            data_path: Path to the dataset directory
        """
        if data_path is None:
            self.data_path = Path(__file__).parent.parent
        else:
            self.data_path = Path(data_path)
        
        self.datasets = {}
        self.metadata = {}
        
    def load_macroeconomic_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all macroeconomic datasets.
        
        Returns:
            Dictionary of DataFrames with macroeconomic data
        """
        macro_path = self.data_path / "macroeconomic_data"
        macro_data = {}
        
        # GDP Growth Rate
        try:
            gdp_df = pd.read_csv(macro_path / "gdp_growth_rate.csv")
            gdp_df['Year'] = pd.to_datetime(gdp_df['Year'], format='%Y')
            macro_data['gdp_growth'] = gdp_df
            logger.info("Loaded GDP growth data: {} records".format(len(gdp_df)))
        except Exception as e:
            logger.error(f"Error loading GDP data: {e}")
        
        # Inflation Rate
        try:
            inflation_df = pd.read_csv(macro_path / "inflation_rate.csv")
            inflation_df['Date'] = pd.to_datetime(
                inflation_df['Year'].astype(str) + '-' + 
                inflation_df['Month'].astype(str).str.zfill(2) + '-01'
            )
            macro_data['inflation'] = inflation_df
            logger.info("Loaded inflation data: {} records".format(len(inflation_df)))
        except Exception as e:
            logger.error(f"Error loading inflation data: {e}")
        
        # Interest Rates
        try:
            interest_df = pd.read_csv(macro_path / "interest_rates.csv")
            interest_df['Date'] = pd.to_datetime(
                interest_df['Year'].astype(str) + '-' + 
                interest_df['Quarter'].str.replace('Q', '').astype(int).map({1: '01', 2: '04', 3: '07', 4: '10'}) + '-01'
            )
            macro_data['interest_rates'] = interest_df
            logger.info("Loaded interest rates data: {} records".format(len(interest_df)))
        except Exception as e:
            logger.error(f"Error loading interest rates data: {e}")
        
        # Broadband Penetration
        try:
            broadband_df = pd.read_csv(macro_path / "broadband_penetration_by_state.csv")
            # Reshape from wide to long format
            id_vars = ['State', 'Region', 'Population_2023', 'Urban_Rural_Classification', 
                      'Major_Telecom_Providers', 'Infrastructure_Score']
            value_vars = [col for col in broadband_df.columns if 'Penetration_Percent' in col]
            
            broadband_long = pd.melt(broadband_df, id_vars=id_vars, value_vars=value_vars,
                                   var_name='Year', value_name='Penetration_Percent')
            broadband_long['Year'] = broadband_long['Year'].str.extract('(\d{4})').astype(int)
            broadband_long['Date'] = pd.to_datetime(broadband_long['Year'], format='%Y')
            
            macro_data['broadband_penetration'] = broadband_long
            logger.info("Loaded broadband penetration data: {} records".format(len(broadband_long)))
        except Exception as e:
            logger.error(f"Error loading broadband data: {e}")
        
        # Ease of Doing Business
        try:
            eodb_df = pd.read_csv(macro_path / "ease_of_doing_business.csv")
            eodb_df['Date'] = pd.to_datetime(eodb_df['Year'], format='%Y')
            macro_data['ease_of_doing_business'] = eodb_df
            logger.info("Loaded ease of doing business data: {} records".format(len(eodb_df)))
        except Exception as e:
            logger.error(f"Error loading ease of doing business data: {e}")
        
        self.datasets['macroeconomic'] = macro_data
        return macro_data
    
    def load_industry_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all industry-specific datasets.
        
        Returns:
            Dictionary of DataFrames with industry data
        """
        industry_path = self.data_path / "industry_specific_data"
        industry_data = {}
        
        # Sectoral Growth Rates
        try:
            sectoral_df = pd.read_csv(industry_path / "sectoral_growth_rates.csv")
            sectoral_df['Date'] = pd.to_datetime(
                sectoral_df['Year'].astype(str) + '-' + 
                sectoral_df['Quarter'].str.replace('Q', '').astype(int).map({1: '01', 2: '04', 3: '07', 4: '10'}) + '-01'
            )
            industry_data['sectoral_growth'] = sectoral_df
            logger.info("Loaded sectoral growth data: {} records".format(len(sectoral_df)))
        except Exception as e:
            logger.error(f"Error loading sectoral growth data: {e}")
        
        # SME Landscape Reports
        try:
            sme_landscape_df = pd.read_csv(industry_path / "sme_landscape_reports.csv")
            sme_landscape_df['Date'] = pd.to_datetime(sme_landscape_df['Year'], format='%Y')
            industry_data['sme_landscape'] = sme_landscape_df
            logger.info("Loaded SME landscape data: {} records".format(len(sme_landscape_df)))
        except Exception as e:
            logger.error(f"Error loading SME landscape data: {e}")
        
        # SME Sector Breakdown
        try:
            sme_sector_df = pd.read_csv(industry_path / "sme_sector_breakdown.csv")
            # Reshape SME counts from wide to long
            id_vars = ['Sector', 'Sub_Sector', 'Average_Employment_Per_SME', 'Revenue_Range_Million_NGN',
                      'Innovation_Intensity_Score', 'Digital_Readiness_Score', 'Export_Potential_Score',
                      'Growth_Rate_2024_Percent', 'Key_Innovation_Areas', 'Major_Constraints', 
                      'Technology_Adoption_Level']
            value_vars = [col for col in sme_sector_df.columns if 'SMEs_Thousands' in col]
            
            sme_sector_long = pd.melt(sme_sector_df, id_vars=id_vars, value_vars=value_vars,
                                    var_name='Year', value_name='SME_Count_Thousands')
            sme_sector_long['Year'] = sme_sector_long['Year'].str.extract('(\d{4})').astype(int)
            sme_sector_long['Date'] = pd.to_datetime(sme_sector_long['Year'], format='%Y')
            
            industry_data['sme_sector_breakdown'] = sme_sector_long
            logger.info("Loaded SME sector breakdown data: {} records".format(len(sme_sector_long)))
        except Exception as e:
            logger.error(f"Error loading SME sector breakdown data: {e}")
        
        self.datasets['industry'] = industry_data
        return industry_data
    
    def load_technology_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all technology adoption datasets.
        
        Returns:
            Dictionary of DataFrames with technology data
        """
        tech_path = self.data_path / "technology_adoption_indices"
        tech_data = {}
        
        # Mobile Money/FinTech Adoption
        try:
            fintech_df = pd.read_csv(tech_path / "mobile_money_fintech_adoption.csv")
            fintech_df['Date'] = pd.to_datetime(
                fintech_df['Year'].astype(str) + '-' + 
                fintech_df['Quarter'].str.replace('Q', '').astype(int).map({1: '01', 2: '04', 3: '07', 4: '10'}) + '-01'
            )
            tech_data['fintech_adoption'] = fintech_df
            logger.info("Loaded FinTech adoption data: {} records".format(len(fintech_df)))
        except Exception as e:
            logger.error(f"Error loading FinTech data: {e}")
        
        # ICT Development Index
        try:
            ict_df = pd.read_csv(tech_path / "ict_development_index.csv")
            ict_df['Date'] = pd.to_datetime(ict_df['Year'], format='%Y')
            tech_data['ict_development'] = ict_df
            logger.info("Loaded ICT development data: {} records".format(len(ict_df)))
        except Exception as e:
            logger.error(f"Error loading ICT development data: {e}")
        
        # Digital Transformation Metrics
        try:
            digital_df = pd.read_csv(tech_path / "digital_transformation_metrics.csv")
            digital_df['Date'] = pd.to_datetime(
                digital_df['Year'].astype(str) + '-' + 
                digital_df['Quarter'].str.replace('Q', '').astype(int).map({1: '01', 2: '04', 3: '07', 4: '10'}) + '-01'
            )
            tech_data['digital_transformation'] = digital_df
            logger.info("Loaded digital transformation data: {} records".format(len(digital_df)))
        except Exception as e:
            logger.error(f"Error loading digital transformation data: {e}")
        
        self.datasets['technology'] = tech_data
        return tech_data
    
    def load_all_data(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Load all datasets.
        
        Returns:
            Dictionary containing all loaded datasets
        """
        logger.info("Loading all datasets...")
        
        self.load_macroeconomic_data()
        self.load_industry_data()
        self.load_technology_data()
        
        logger.info("All datasets loaded successfully")
        return self.datasets
    
    def create_master_dataset(self, frequency: str = 'quarterly') -> pd.DataFrame:
        """
        Create a master dataset by merging key indicators.
        
        Args:
            frequency: 'quarterly' or 'annual' for data aggregation
            
        Returns:
            Master DataFrame with key indicators
        """
        if not self.datasets:
            self.load_all_data()
        
        # Start with quarterly date range
        date_range = pd.date_range(start='2018-01-01', end='2024-12-31', freq='QS')
        master_df = pd.DataFrame({'Date': date_range})
        
        # Add macroeconomic indicators
        if 'macroeconomic' in self.datasets:
            # GDP growth (annual, forward fill for quarters)
            if 'gdp_growth' in self.datasets['macroeconomic']:
                gdp_df = self.datasets['macroeconomic']['gdp_growth'][['Year', 'GDP_Growth_Rate_Percent']].copy()
                gdp_df['Date'] = pd.to_datetime(gdp_df['Year'], format='%Y')
                gdp_df = gdp_df.drop('Year', axis=1)
                master_df = pd.merge(master_df, gdp_df, on='Date', how='left')
                master_df['GDP_Growth_Rate_Percent'] = master_df['GDP_Growth_Rate_Percent'].fillna(method='ffill')
            
            # Interest rates (quarterly)
            if 'interest_rates' in self.datasets['macroeconomic']:
                interest_df = self.datasets['macroeconomic']['interest_rates'][
                    ['Date', 'Monetary_Policy_Rate_Percent', 'Prime_Lending_Rate_Percent']
                ].copy()
                master_df = pd.merge(master_df, interest_df, on='Date', how='left')
        
        # Add technology indicators
        if 'technology' in self.datasets:
            # FinTech adoption (quarterly)
            if 'fintech_adoption' in self.datasets['technology']:
                fintech_df = self.datasets['technology']['fintech_adoption'][
                    ['Date', 'Mobile_Money_Penetration_Percent', 'FinTech_Adoption_Index']
                ].copy()
                master_df = pd.merge(master_df, fintech_df, on='Date', how='left')
            
            # Digital transformation (quarterly)
            if 'digital_transformation' in self.datasets['technology']:
                digital_df = self.datasets['technology']['digital_transformation'][
                    ['Date', 'Composite_Digital_Index', 'Digital_Competitiveness_Ranking']
                ].copy()
                master_df = pd.merge(master_df, digital_df, on='Date', how='left')
        
        # Add industry indicators
        if 'industry' in self.datasets:
            # Manufacturing growth (quarterly)
            if 'sectoral_growth' in self.datasets['industry']:
                sectoral_df = self.datasets['industry']['sectoral_growth'][
                    ['Date', 'Manufacturing_Growth_Percent', 'Information_Communication_Growth_Percent']
                ].copy()
                master_df = pd.merge(master_df, sectoral_df, on='Date', how='left')
        
        # Aggregate to annual if requested
        if frequency == 'annual':
            master_df['Year'] = master_df['Date'].dt.year
            numeric_cols = master_df.select_dtypes(include=[np.number]).columns
            master_df = master_df.groupby('Year')[numeric_cols].mean().reset_index()
            master_df['Date'] = pd.to_datetime(master_df['Year'], format='%Y')
        
        logger.info(f"Created master dataset with {len(master_df)} records and {len(master_df.columns)} variables")
        return master_df
    
    def validate_data_quality(self) -> Dict[str, Dict[str, float]]:
        """
        Validate data quality across all datasets.
        
        Returns:
            Dictionary with quality metrics for each dataset
        """
        if not self.datasets:
            self.load_all_data()
        
        quality_report = {}
        
        for category, datasets in self.datasets.items():
            quality_report[category] = {}
            
            for name, df in datasets.items():
                metrics = {
                    'completeness': (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
                    'record_count': len(df),
                    'variable_count': len(df.columns),
                    'date_range_years': (df['Date'].max() - df['Date'].min()).days / 365.25 if 'Date' in df.columns else 0,
                    'numeric_variables': len(df.select_dtypes(include=[np.number]).columns),
                    'categorical_variables': len(df.select_dtypes(include=['object']).columns)
                }
                
                quality_report[category][name] = metrics
        
        return quality_report
    
    def export_processed_data(self, output_path: str = None):
        """
        Export processed datasets to CSV files.
        
        Args:
            output_path: Directory to save processed files
        """
        if output_path is None:
            output_path = self.data_path / "processed_data"
        else:
            output_path = Path(output_path)
        
        output_path.mkdir(exist_ok=True)
        
        if not self.datasets:
            self.load_all_data()
        
        # Export master dataset
        master_df = self.create_master_dataset()
        master_df.to_csv(output_path / "master_dataset_quarterly.csv", index=False)
        
        master_annual = self.create_master_dataset(frequency='annual')
        master_annual.to_csv(output_path / "master_dataset_annual.csv", index=False)
        
        # Export individual processed datasets
        for category, datasets in self.datasets.items():
            category_path = output_path / category
            category_path.mkdir(exist_ok=True)
            
            for name, df in datasets.items():
                df.to_csv(category_path / f"{name}_processed.csv", index=False)
        
        logger.info(f"Exported processed data to {output_path}")

def main():
    """
    Example usage of the data loader.
    """
    # Initialize loader
    loader = NigerianSMEDataLoader()
    
    # Load all data
    datasets = loader.load_all_data()
    
    # Create master dataset
    master_df = loader.create_master_dataset()
    print(f"Master dataset shape: {master_df.shape}")
    print(f"Date range: {master_df['Date'].min()} to {master_df['Date'].max()}")
    
    # Validate data quality
    quality_report = loader.validate_data_quality()
    print("\nData Quality Report:")
    for category, datasets in quality_report.items():
        print(f"\n{category.upper()}:")
        for name, metrics in datasets.items():
            print(f"  {name}: {metrics['completeness']:.1f}% complete, {metrics['record_count']} records")
    
    # Export processed data
    loader.export_processed_data()
    print("\nProcessed data exported successfully")

if __name__ == "__main__":
    main()