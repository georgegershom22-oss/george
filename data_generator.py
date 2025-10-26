#!/usr/bin/env python3
"""
Comprehensive Dataset Generator for Digital Banking Fraud Prevention Research
Generates realistic data for Section A: Demographic and Control Variables
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import json
import os

class BankingFraudDatasetGenerator:
    def __init__(self, sample_size=5000, seed=42):
        """
        Initialize the dataset generator
        
        Args:
            sample_size (int): Number of observations to generate
            seed (int): Random seed for reproducibility
        """
        self.sample_size = sample_size
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)
        
        # Country-specific parameters
        self.country_params = {
            'Nigeria': {
                'population_weights': 0.6,  # 60% Nigeria, 40% Ghana
                'income_bands': {
                    'NGN': [50000, 100000, 200000, 500000, 1000000, 2000000]
                },
                'bank_types': {
                    'Traditional Commercial': 0.45,
                    'Digital-Only Bank': 0.35,
                    'Microfinance': 0.20
                }
            },
            'Ghana': {
                'population_weights': 0.4,
                'income_bands': {
                    'GHS': [500, 1000, 2000, 5000, 10000, 20000]
                },
                'bank_types': {
                    'Traditional Commercial': 0.50,
                    'Digital-Only Bank': 0.30,
                    'Microfinance': 0.20
                }
            }
        }
    
    def generate_demographics(self):
        """Generate demographic variables"""
        print("Generating demographic variables...")
        
        # Country distribution
        countries = np.random.choice(
            ['Nigeria', 'Ghana'], 
            size=self.sample_size, 
            p=[0.6, 0.4]
        )
        
        # Age distribution (18-65, with higher concentration in 25-45)
        age = np.random.normal(35, 12, self.sample_size)
        age = np.clip(age, 18, 65).astype(int)
        
        # Gender distribution (slightly more male in banking context)
        gender = np.random.choice(
            [1, 2, 3],  # Male, Female, Other/Prefer not to say
            size=self.sample_size,
            p=[0.52, 0.45, 0.03]
        )
        
        # Education levels (ordinal 1-6)
        education = np.random.choice(
            [1, 2, 3, 4, 5, 6],  # No formal to Postgraduate
            size=self.sample_size,
            p=[0.05, 0.15, 0.25, 0.30, 0.20, 0.05]
        )
        
        # Income levels (country-specific)
        income_levels = []
        for country in countries:
            if country == 'Nigeria':
                income_bands = self.country_params['Nigeria']['income_bands']['NGN']
            else:
                income_bands = self.country_params['Ghana']['income_bands']['GHS']
            
            # Income distribution weighted towards middle bands
            income_band = np.random.choice(
                range(1, len(income_bands) + 1),
                p=[0.10, 0.20, 0.30, 0.25, 0.10, 0.05]
            )
            income_levels.append(income_band)
        
        return {
            'Country': countries,
            'Age': age,
            'Gender': gender,
            'Education': education,
            'Income_Level': income_levels
        }
    
    def generate_banking_profiles(self, countries):
        """Generate banking profile variables"""
        print("Generating banking profile variables...")
        
        bank_types = []
        years_with_account = []
        frequency_of_use = []
        
        for country in countries:
            # Bank type based on country-specific distribution
            if country == 'Nigeria':
                bank_type_probs = list(self.country_params['Nigeria']['bank_types'].values())
                bank_type_names = list(self.country_params['Nigeria']['bank_types'].keys())
            else:
                bank_type_probs = list(self.country_params['Ghana']['bank_types'].values())
                bank_type_names = list(self.country_params['Ghana']['bank_types'].keys())
            
            bank_type = np.random.choice(
                [1, 2, 3],  # Traditional, Digital-Only, Microfinance
                p=bank_type_probs
            )
            bank_types.append(bank_type)
            
            # Years with account (correlated with age and bank type)
            if bank_type == 2:  # Digital-only banks are newer
                years = np.random.exponential(3)  # Mean 3 years
            else:
                years = np.random.exponential(8)  # Mean 8 years for traditional
            
            years = min(int(years), 30)  # Cap at 30 years
            years_with_account.append(max(1, years))  # At least 1 year
            
            # Frequency of use (1=Daily to 5=Less than monthly)
            # Digital bank users tend to use more frequently
            if bank_type == 2:
                freq_probs = [0.25, 0.30, 0.25, 0.15, 0.05]  # More frequent use
            else:
                freq_probs = [0.15, 0.25, 0.30, 0.20, 0.10]  # Less frequent use
            
            frequency = np.random.choice([1, 2, 3, 4, 5], p=freq_probs)
            frequency_of_use.append(frequency)
        
        return {
            'Bank_Type': bank_types,
            'Years_with_Account': years_with_account,
            'Frequency_of_Use': frequency_of_use
        }
    
    def generate_experience_variables(self, countries, bank_types, years_with_account):
        """Generate fraud experience variables"""
        print("Generating fraud experience variables...")
        
        past_victim = []
        fraud_incidents = []
        fraud_types = []
        fraud_amounts = []
        fraud_resolution = []
        
        for i in range(len(countries)):
            # Base probability of being a fraud victim (15% overall)
            base_victim_prob = 0.15
            
            # Adjust based on bank type and years with account
            if bank_types[i] == 2:  # Digital-only banks
                victim_prob = base_victim_prob * 1.3  # 30% higher risk
            elif bank_types[i] == 3:  # Microfinance
                victim_prob = base_victim_prob * 0.8  # 20% lower risk
            else:
                victim_prob = base_victim_prob
            
            # More years with account = slightly higher risk
            victim_prob *= (1 + years_with_account[i] * 0.01)
            
            is_victim = np.random.random() < victim_prob
            past_victim.append(1 if is_victim else 0)
            
            if is_victim:
                # Number of fraud incidents (1-5, weighted towards 1-2)
                incidents = np.random.choice([1, 2, 3, 4, 5], p=[0.50, 0.30, 0.12, 0.05, 0.03])
                fraud_incidents.append(incidents)
                
                # Fraud types (multiple types possible)
                fraud_type_options = [
                    'Card Fraud', 'Phishing', 'Account Takeover', 'Mobile Banking Fraud',
                    'ATM Skimming', 'Social Engineering', 'Online Banking Fraud'
                ]
                num_types = min(incidents, 3)  # Max 3 different types
                selected_types = random.sample(fraud_type_options, num_types)
                fraud_types.append('; '.join(selected_types))
                
                # Fraud amounts (in local currency)
                if countries[i] == 'Nigeria':
                    amounts = np.random.lognormal(8, 1.5)  # NGN amounts
                    amounts = np.clip(amounts, 10000, 5000000)  # 10k to 5M NGN
                else:
                    amounts = np.random.lognormal(6, 1.5)  # GHS amounts
                    amounts = np.clip(amounts, 100, 50000)  # 100 to 50k GHS
                
                fraud_amounts.append(round(amounts, 2))
                
                # Fraud resolution (1=Resolved, 2=Partially Resolved, 3=Not Resolved)
                resolution = np.random.choice([1, 2, 3], p=[0.60, 0.25, 0.15])
                fraud_resolution.append(resolution)
            else:
                fraud_incidents.append(0)
                fraud_types.append('')
                fraud_amounts.append(0)
                fraud_resolution.append(0)
        
        return {
            'Past_Victim': past_victim,
            'Fraud_Incidents': fraud_incidents,
            'Fraud_Types': fraud_types,
            'Fraud_Amount': fraud_amounts,
            'Fraud_Resolution': fraud_resolution
        }
    
    def generate_additional_variables(self, countries, ages, education, bank_types):
        """Generate additional variables for comprehensive analysis"""
        print("Generating additional variables...")
        
        # Technology adoption level (1-5 scale)
        tech_adoption = []
        for i in range(len(countries)):
            base_score = 3
            if bank_types[i] == 2:  # Digital bank users
                base_score += 1
            if education[i] >= 4:  # Higher education
                base_score += 0.5
            if ages[i] < 30:  # Younger users
                base_score += 0.5
            
            score = np.random.normal(base_score, 0.8)
            score = np.clip(score, 1, 5)
            tech_adoption.append(round(score, 1))
        
        # Risk tolerance (1-5 scale)
        risk_tolerance = np.random.normal(3, 0.7, self.sample_size)
        risk_tolerance = np.clip(risk_tolerance, 1, 5)
        risk_tolerance = [round(x, 1) for x in risk_tolerance]
        
        # Financial literacy (1-5 scale)
        financial_literacy = []
        for i in range(len(countries)):
            base_score = 2.5
            if education[i] >= 4:
                base_score += 1
            if ages[i] > 25:  # More life experience
                base_score += 0.5
            
            score = np.random.normal(base_score, 0.6)
            score = np.clip(score, 1, 5)
            financial_literacy.append(round(score, 1))
        
        # Trust in banking system (1-5 scale)
        trust_banking = []
        for i in range(len(countries)):
            base_score = 3.5
            if bank_types[i] == 3:  # Microfinance users trust more
                base_score += 0.5
            if countries[i] == 'Ghana':  # Slightly higher trust in Ghana
                base_score += 0.2
            
            score = np.random.normal(base_score, 0.6)
            score = np.clip(score, 1, 5)
            trust_banking.append(round(score, 1))
        
        # Mobile phone usage (1-5 scale)
        mobile_usage = np.random.normal(4, 0.5, self.sample_size)
        mobile_usage = np.clip(mobile_usage, 1, 5)
        mobile_usage = [round(x, 1) for x in mobile_usage]
        
        # Internet access quality (1-5 scale)
        internet_quality = []
        for country in countries:
            if country == 'Nigeria':
                quality = np.random.normal(3, 0.8)  # Slightly lower in Nigeria
            else:
                quality = np.random.normal(3.5, 0.7)  # Better in Ghana
            
            quality = np.clip(quality, 1, 5)
            internet_quality.append(round(quality, 1))
        
        # Employment status
        employment = np.random.choice(
            [1, 2, 3, 4, 5],  # Full-time, Part-time, Self-employed, Unemployed, Student
            size=self.sample_size,
            p=[0.45, 0.15, 0.20, 0.10, 0.10]
        )
        
        # Marital status
        marital_status = np.random.choice(
            [1, 2, 3, 4],  # Single, Married, Divorced, Widowed
            size=self.sample_size,
            p=[0.35, 0.50, 0.10, 0.05]
        )
        
        # Urban vs Rural
        urban_rural = np.random.choice(
            [1, 2],  # Urban, Rural
            size=self.sample_size,
            p=[0.70, 0.30]
        )
        
        return {
            'Tech_Adoption': tech_adoption,
            'Risk_Tolerance': risk_tolerance,
            'Financial_Literacy': financial_literacy,
            'Trust_Banking': trust_banking,
            'Mobile_Usage': mobile_usage,
            'Internet_Quality': internet_quality,
            'Employment_Status': employment,
            'Marital_Status': marital_status,
            'Urban_Rural': urban_rural
        }
    
    def generate_dataset(self):
        """Generate the complete dataset"""
        print(f"Generating comprehensive dataset with {self.sample_size} observations...")
        
        # Generate core variables
        demographics = self.generate_demographics()
        banking_profiles = self.generate_banking_profiles(demographics['Country'])
        experience_vars = self.generate_experience_variables(
            demographics['Country'],
            banking_profiles['Bank_Type'],
            banking_profiles['Years_with_Account']
        )
        additional_vars = self.generate_additional_variables(
            demographics['Country'],
            demographics['Age'],
            demographics['Education'],
            banking_profiles['Bank_Type']
        )
        
        # Combine all variables
        all_data = {**demographics, **banking_profiles, **experience_vars, **additional_vars}
        
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Add unique ID
        df.insert(0, 'Participant_ID', range(1, len(df) + 1))
        
        # Add timestamp
        df['Data_Collection_Date'] = datetime.now().strftime('%Y-%m-%d')
        
        print(f"Dataset generated successfully with {len(df)} observations and {len(df.columns)} variables")
        
        return df
    
    def save_dataset(self, df, output_dir='/workspace'):
        """Save dataset in multiple formats"""
        print("Saving dataset in multiple formats...")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save as CSV
        csv_path = os.path.join(output_dir, 'banking_fraud_dataset.csv')
        df.to_csv(csv_path, index=False)
        print(f"CSV saved to: {csv_path}")
        
        # Save as Excel with multiple sheets
        excel_path = os.path.join(output_dir, 'banking_fraud_dataset.xlsx')
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Complete_Dataset', index=False)
            
            # Create summary sheet
            summary_data = {
                'Variable': df.columns.tolist(),
                'Data_Type': [str(df[col].dtype) for col in df.columns],
                'Missing_Values': [df[col].isnull().sum() for col in df.columns],
                'Unique_Values': [df[col].nunique() for col in df.columns]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Data_Summary', index=False)
            
            # Create country-specific sheets
            for country in df['Country'].unique():
                country_df = df[df['Country'] == country]
                sheet_name = f"{country}_Data"
                country_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"Excel file saved to: {excel_path}")
        
        # Save as JSON
        json_path = os.path.join(output_dir, 'banking_fraud_dataset.json')
        df.to_json(json_path, orient='records', indent=2)
        print(f"JSON saved to: {json_path}")
        
        # Save variable codebook
        codebook_path = os.path.join(output_dir, 'variable_codebook.json')
        codebook = self.generate_codebook()
        with open(codebook_path, 'w') as f:
            json.dump(codebook, f, indent=2)
        print(f"Codebook saved to: {codebook_path}")
        
        return {
            'csv': csv_path,
            'excel': excel_path,
            'json': json_path,
            'codebook': codebook_path
        }
    
    def generate_codebook(self):
        """Generate comprehensive variable codebook"""
        codebook = {
            "dataset_info": {
                "title": "Digital Banking Fraud Prevention Research Dataset",
                "description": "Comprehensive dataset for analyzing demographic and control variables in digital banking fraud prevention research",
                "sample_size": self.sample_size,
                "countries": ["Nigeria", "Ghana"],
                "generated_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            "variables": {
                "Participant_ID": {
                    "type": "integer",
                    "description": "Unique identifier for each participant",
                    "coding": "Sequential numbers starting from 1"
                },
                "Country": {
                    "type": "categorical",
                    "description": "Country of residence",
                    "coding": "1=Nigeria, 2=Ghana"
                },
                "Age": {
                    "type": "continuous",
                    "description": "Age in years",
                    "coding": "18-65 years, normally distributed around 35"
                },
                "Gender": {
                    "type": "categorical",
                    "description": "Gender identity",
                    "coding": "1=Male, 2=Female, 3=Other/Prefer not to say"
                },
                "Education": {
                    "type": "ordinal",
                    "description": "Highest level of education completed",
                    "coding": "1=No formal education, 2=Primary, 3=Secondary, 4=Diploma/Certificate, 5=Bachelor's, 6=Postgraduate"
                },
                "Income_Level": {
                    "type": "ordinal",
                    "description": "Income level in local currency bands",
                    "coding": "1-6 bands (country-specific): Nigeria (NGN): 50k, 100k, 200k, 500k, 1M, 2M+; Ghana (GHS): 500, 1k, 2k, 5k, 10k, 20k+"
                },
                "Bank_Type": {
                    "type": "categorical",
                    "description": "Type of primary banking institution",
                    "coding": "1=Traditional Commercial Bank, 2=Digital-Only Bank, 3=Microfinance Institution"
                },
                "Years_with_Account": {
                    "type": "continuous",
                    "description": "Number of years with current bank account",
                    "coding": "1-30 years, exponential distribution"
                },
                "Frequency_of_Use": {
                    "type": "ordinal",
                    "description": "Frequency of banking service usage",
                    "coding": "1=Daily, 2=Weekly, 3=Monthly, 4=Quarterly, 5=Less than monthly"
                },
                "Past_Victim": {
                    "type": "binary",
                    "description": "Whether participant has been a victim of bank fraud",
                    "coding": "1=Yes, 0=No"
                },
                "Fraud_Incidents": {
                    "type": "count",
                    "description": "Number of fraud incidents experienced",
                    "coding": "0-5 incidents (only for victims)"
                },
                "Fraud_Types": {
                    "type": "text",
                    "description": "Types of fraud experienced",
                    "coding": "Semicolon-separated list of fraud types"
                },
                "Fraud_Amount": {
                    "type": "continuous",
                    "description": "Total amount lost to fraud in local currency",
                    "coding": "Country-specific currency amounts"
                },
                "Fraud_Resolution": {
                    "type": "ordinal",
                    "description": "Resolution status of fraud incidents",
                    "coding": "1=Resolved, 2=Partially Resolved, 3=Not Resolved, 0=Not Applicable"
                },
                "Tech_Adoption": {
                    "type": "continuous",
                    "description": "Technology adoption level",
                    "coding": "1-5 scale (1=Very Low, 5=Very High)"
                },
                "Risk_Tolerance": {
                    "type": "continuous",
                    "description": "Financial risk tolerance",
                    "coding": "1-5 scale (1=Very Low, 5=Very High)"
                },
                "Financial_Literacy": {
                    "type": "continuous",
                    "description": "Self-reported financial literacy level",
                    "coding": "1-5 scale (1=Very Low, 5=Very High)"
                },
                "Trust_Banking": {
                    "type": "continuous",
                    "description": "Trust in banking system",
                    "coding": "1-5 scale (1=Very Low, 5=Very High)"
                },
                "Mobile_Usage": {
                    "type": "continuous",
                    "description": "Mobile phone usage frequency",
                    "coding": "1-5 scale (1=Very Low, 5=Very High)"
                },
                "Internet_Quality": {
                    "type": "continuous",
                    "description": "Perceived internet access quality",
                    "coding": "1-5 scale (1=Very Poor, 5=Excellent)"
                },
                "Employment_Status": {
                    "type": "categorical",
                    "description": "Current employment status",
                    "coding": "1=Full-time, 2=Part-time, 3=Self-employed, 4=Unemployed, 5=Student"
                },
                "Marital_Status": {
                    "type": "categorical",
                    "description": "Marital status",
                    "coding": "1=Single, 2=Married, 3=Divorced, 4=Widowed"
                },
                "Urban_Rural": {
                    "type": "categorical",
                    "description": "Location type",
                    "coding": "1=Urban, 2=Rural"
                },
                "Data_Collection_Date": {
                    "type": "date",
                    "description": "Date when data was collected",
                    "coding": "YYYY-MM-DD format"
                }
            }
        }
        return codebook

def main():
    """Main function to generate and save the dataset"""
    print("=" * 60)
    print("DIGITAL BANKING FRAUD PREVENTION RESEARCH DATASET GENERATOR")
    print("=" * 60)
    
    # Generate dataset
    generator = BankingFraudDatasetGenerator(sample_size=5000, seed=42)
    df = generator.generate_dataset()
    
    # Display basic statistics
    print("\nDataset Overview:")
    print(f"Total observations: {len(df)}")
    print(f"Total variables: {len(df.columns)}")
    print(f"Countries: {df['Country'].value_counts().to_dict()}")
    print(f"Bank types: {df['Bank_Type'].value_counts().to_dict()}")
    print(f"Fraud victims: {df['Past_Victim'].sum()} ({df['Past_Victim'].mean()*100:.1f}%)")
    
    # Save dataset
    file_paths = generator.save_dataset(df)
    
    print("\n" + "=" * 60)
    print("DATASET GENERATION COMPLETE!")
    print("=" * 60)
    print("Files created:")
    for format_type, path in file_paths.items():
        print(f"  {format_type.upper()}: {path}")
    
    return df

if __name__ == "__main__":
    df = main()