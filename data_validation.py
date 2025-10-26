#!/usr/bin/env python3
"""
Data Validation and Analysis Script for Banking Fraud Dataset
Comprehensive validation of data quality and relationships
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json

class DatasetValidator:
    def __init__(self, df):
        self.df = df
        self.validation_results = {}
    
    def basic_validation(self):
        """Perform basic data quality checks"""
        print("Performing basic data validation...")
        
        results = {
            'total_observations': len(self.df),
            'total_variables': len(self.df.columns),
            'missing_values': self.df.isnull().sum().sum(),
            'duplicate_rows': self.df.duplicated().sum(),
            'data_types': dict(self.df.dtypes),
            'memory_usage': self.df.memory_usage(deep=True).sum() / 1024**2  # MB
        }
        
        # Check for missing values by column
        missing_by_column = self.df.isnull().sum()
        results['missing_by_column'] = missing_by_column[missing_by_column > 0].to_dict()
        
        self.validation_results['basic'] = results
        return results
    
    def demographic_validation(self):
        """Validate demographic variables"""
        print("Validating demographic variables...")
        
        results = {}
        
        # Country distribution
        country_counts = self.df['Country'].value_counts()
        results['country_distribution'] = country_counts.to_dict()
        
        # Age validation
        age_stats = self.df['Age'].describe()
        results['age_statistics'] = age_stats.to_dict()
        results['age_outliers'] = len(self.df[(self.df['Age'] < 18) | (self.df['Age'] > 65)])
        
        # Gender distribution
        gender_counts = self.df['Gender'].value_counts()
        results['gender_distribution'] = gender_counts.to_dict()
        
        # Education distribution
        education_counts = self.df['Education'].value_counts()
        results['education_distribution'] = education_counts.to_dict()
        
        # Income level validation
        income_stats = self.df['Income_Level'].describe()
        results['income_statistics'] = income_stats.to_dict()
        
        self.validation_results['demographics'] = results
        return results
    
    def banking_profile_validation(self):
        """Validate banking profile variables"""
        print("Validating banking profile variables...")
        
        results = {}
        
        # Bank type distribution
        bank_type_counts = self.df['Bank_Type'].value_counts()
        results['bank_type_distribution'] = bank_type_counts.to_dict()
        
        # Years with account validation
        years_stats = self.df['Years_with_Account'].describe()
        results['years_with_account_statistics'] = years_stats.to_dict()
        results['years_outliers'] = len(self.df[self.df['Years_with_Account'] > 30])
        
        # Frequency of use distribution
        frequency_counts = self.df['Frequency_of_Use'].value_counts()
        results['frequency_distribution'] = frequency_counts.to_dict()
        
        # Cross-tabulation: Bank type vs Country
        bank_country_crosstab = pd.crosstab(self.df['Bank_Type'], self.df['Country'])
        results['bank_type_by_country'] = bank_country_crosstab.to_dict()
        
        self.validation_results['banking_profiles'] = results
        return results
    
    def fraud_experience_validation(self):
        """Validate fraud experience variables"""
        print("Validating fraud experience variables...")
        
        results = {}
        
        # Past victim distribution
        victim_counts = self.df['Past_Victim'].value_counts()
        results['victim_distribution'] = victim_counts.to_dict()
        results['victim_rate'] = self.df['Past_Victim'].mean()
        
        # Fraud incidents for victims only
        victims_df = self.df[self.df['Past_Victim'] == 1]
        if len(victims_df) > 0:
            incidents_stats = victims_df['Fraud_Incidents'].describe()
            results['fraud_incidents_statistics'] = incidents_stats.to_dict()
            
            # Fraud types analysis
            fraud_types = victims_df['Fraud_Types'].str.split('; ').explode()
            fraud_type_counts = fraud_types.value_counts()
            results['fraud_types_distribution'] = fraud_type_counts.to_dict()
            
            # Fraud amounts analysis
            amounts_stats = victims_df['Fraud_Amount'].describe()
            results['fraud_amounts_statistics'] = amounts_stats.to_dict()
            
            # Resolution status
            resolution_counts = victims_df['Fraud_Resolution'].value_counts()
            results['resolution_distribution'] = resolution_counts.to_dict()
        
        # Cross-tabulation: Victim status by Bank type
        victim_bank_crosstab = pd.crosstab(self.df['Past_Victim'], self.df['Bank_Type'])
        results['victim_by_bank_type'] = victim_bank_crosstab.to_dict()
        
        # Cross-tabulation: Victim status by Country
        victim_country_crosstab = pd.crosstab(self.df['Past_Victim'], self.df['Country'])
        results['victim_by_country'] = victim_country_crosstab.to_dict()
        
        self.validation_results['fraud_experience'] = results
        return results
    
    def additional_variables_validation(self):
        """Validate additional variables"""
        print("Validating additional variables...")
        
        results = {}
        
        # Continuous variables
        continuous_vars = ['Tech_Adoption', 'Risk_Tolerance', 'Financial_Literacy', 
                          'Trust_Banking', 'Mobile_Usage', 'Internet_Quality']
        
        for var in continuous_vars:
            if var in self.df.columns:
                stats_dict = self.df[var].describe().to_dict()
                results[f'{var}_statistics'] = stats_dict
                
                # Check for values outside 1-5 range
                out_of_range = len(self.df[(self.df[var] < 1) | (self.df[var] > 5)])
                results[f'{var}_out_of_range'] = out_of_range
        
        # Categorical variables
        categorical_vars = ['Employment_Status', 'Marital_Status', 'Urban_Rural']
        
        for var in categorical_vars:
            if var in self.df.columns:
                counts = self.df[var].value_counts()
                results[f'{var}_distribution'] = counts.to_dict()
        
        self.validation_results['additional_variables'] = results
        return results
    
    def correlation_analysis(self):
        """Perform correlation analysis"""
        print("Performing correlation analysis...")
        
        # Select numeric variables for correlation
        numeric_vars = self.df.select_dtypes(include=[np.number]).columns
        correlation_matrix = self.df[numeric_vars].corr()
        
        # Find high correlations (>0.7 or <-0.7)
        high_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    high_correlations.append({
                        'var1': correlation_matrix.columns[i],
                        'var2': correlation_matrix.columns[j],
                        'correlation': corr_value
                    })
        
        results = {
            'correlation_matrix': correlation_matrix.to_dict(),
            'high_correlations': high_correlations
        }
        
        self.validation_results['correlations'] = results
        return results
    
    def statistical_tests(self):
        """Perform statistical tests"""
        print("Performing statistical tests...")
        
        results = {}
        
        # Chi-square test: Bank type vs Victim status
        contingency_table = pd.crosstab(self.df['Bank_Type'], self.df['Past_Victim'])
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        results['bank_type_victim_chi2'] = {
            'chi2_statistic': chi2,
            'p_value': p_value,
            'degrees_of_freedom': dof
        }
        
        # Chi-square test: Country vs Victim status
        contingency_table2 = pd.crosstab(self.df['Country'], self.df['Past_Victim'])
        chi2_2, p_value_2, dof_2, expected_2 = stats.chi2_contingency(contingency_table2)
        results['country_victim_chi2'] = {
            'chi2_statistic': chi2_2,
            'p_value': p_value_2,
            'degrees_of_freedom': dof_2
        }
        
        # T-test: Age difference between victims and non-victims
        victims_age = self.df[self.df['Past_Victim'] == 1]['Age']
        non_victims_age = self.df[self.df['Past_Victim'] == 0]['Age']
        t_stat, t_p_value = stats.ttest_ind(victims_age, non_victims_age)
        results['age_victim_ttest'] = {
            't_statistic': t_stat,
            'p_value': t_p_value
        }
        
        self.validation_results['statistical_tests'] = results
        return results
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("Generating summary report...")
        
        report = {
            'dataset_overview': {
                'total_observations': len(self.df),
                'total_variables': len(self.df.columns),
                'missing_values_total': self.df.isnull().sum().sum(),
                'duplicate_rows': self.df.duplicated().sum()
            },
            'key_findings': {
                'fraud_victim_rate': f"{self.df['Past_Victim'].mean()*100:.1f}%",
                'most_common_bank_type': self.df['Bank_Type'].mode().iloc[0],
                'country_distribution': self.df['Country'].value_counts().to_dict(),
                'average_age': f"{self.df['Age'].mean():.1f} years"
            },
            'data_quality_score': self.calculate_quality_score(),
            'validation_results': self.validation_results
        }
        
        return report
    
    def calculate_quality_score(self):
        """Calculate overall data quality score"""
        score = 100
        
        # Deduct for missing values
        missing_pct = (self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100
        score -= missing_pct * 2
        
        # Deduct for duplicates
        duplicate_pct = (self.df.duplicated().sum() / len(self.df)) * 100
        score -= duplicate_pct * 5
        
        # Check for logical inconsistencies
        if 'Age' in self.df.columns:
            invalid_ages = len(self.df[(self.df['Age'] < 18) | (self.df['Age'] > 65)])
            invalid_age_pct = (invalid_ages / len(self.df)) * 100
            score -= invalid_age_pct * 3
        
        return max(0, min(100, score))
    
    def save_validation_report(self, output_path='/workspace/validation_report.json'):
        """Save validation report to file"""
        report = self.generate_summary_report()
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Validation report saved to: {output_path}")
        return output_path

def main():
    """Main validation function"""
    print("=" * 60)
    print("BANKING FRAUD DATASET VALIDATION")
    print("=" * 60)
    
    # Load dataset
    df = pd.read_csv('/workspace/banking_fraud_dataset.csv')
    print(f"Loaded dataset with {len(df)} observations and {len(df.columns)} variables")
    
    # Initialize validator
    validator = DatasetValidator(df)
    
    # Run all validations
    validator.basic_validation()
    validator.demographic_validation()
    validator.banking_profile_validation()
    validator.fraud_experience_validation()
    validator.additional_variables_validation()
    validator.correlation_analysis()
    validator.statistical_tests()
    
    # Generate and save report
    report_path = validator.save_validation_report()
    
    # Print summary
    report = validator.generate_summary_report()
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Data Quality Score: {report['data_quality_score']:.1f}/100")
    print(f"Total Observations: {report['dataset_overview']['total_observations']:,}")
    print(f"Missing Values: {report['dataset_overview']['missing_values_total']}")
    print(f"Duplicate Rows: {report['dataset_overview']['duplicate_rows']}")
    print(f"Fraud Victim Rate: {report['key_findings']['fraud_victim_rate']}")
    print(f"Average Age: {report['key_findings']['average_age']}")
    
    print("\nCountry Distribution:")
    for country, count in report['key_findings']['country_distribution'].items():
        print(f"  {country}: {count:,} ({count/len(df)*100:.1f}%)")
    
    print(f"\nDetailed validation report saved to: {report_path}")
    
    return validator

if __name__ == "__main__":
    validator = main()