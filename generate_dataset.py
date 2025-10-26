#!/usr/bin/env python3
"""
Comprehensive Dataset Generator for Digital Banking Fraud Control Research
Generates realistic data for Nigeria and Ghana with proper statistical relationships
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import json
import os

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

class BankingFraudDatasetGenerator:
    def __init__(self, sample_size=5000):
        self.sample_size = sample_size
        self.data = {}
        
        # Country-specific parameters
        self.country_params = {
            1: {  # Nigeria
                'name': 'Nigeria',
                'currency': 'NGN',
                'population_urban': 0.52,
                'avg_income': 150000,  # NGN per month
                'digital_adoption': 0.35,
                'fraud_rate': 0.28
            },
            2: {  # Ghana
                'name': 'Ghana', 
                'currency': 'GHS',
                'population_urban': 0.58,
                'avg_income': 2000,  # GHS per month
                'digital_adoption': 0.42,
                'fraud_rate': 0.22
            }
        }
    
    def generate_demographics(self):
        """Generate demographic variables with realistic distributions"""
        print("Generating demographic data...")
        
        # Country distribution (60% Nigeria, 40% Ghana)
        countries = np.random.choice([1, 2], size=self.sample_size, p=[0.6, 0.4])
        
        # Age distribution (18-65, skewed towards younger adults)
        ages = np.random.gamma(2, 8, self.sample_size) + 18
        ages = np.clip(ages, 18, 65).astype(int)
        
        # Gender distribution (slight male bias in banking)
        genders = np.random.choice([1, 2, 3], size=self.sample_size, p=[0.52, 0.46, 0.02])
        
        # Education levels (realistic distribution for West Africa)
        education = np.random.choice([1, 2, 3, 4, 5, 6], size=self.sample_size, 
                                   p=[0.08, 0.15, 0.25, 0.30, 0.18, 0.04])
        
        # Income levels (country-specific)
        income_levels = []
        for country in countries:
            if country == 1:  # Nigeria
                income = np.random.choice([1, 2, 3, 4, 5, 6], p=[0.15, 0.25, 0.30, 0.20, 0.08, 0.02])
            else:  # Ghana
                income = np.random.choice([1, 2, 3, 4, 5, 6], p=[0.12, 0.20, 0.35, 0.25, 0.06, 0.02])
            income_levels.append(income)
        
        # Urban vs Rural (country-specific)
        urban_rural = []
        for country in countries:
            urban_prob = self.country_params[country]['population_urban']
            urban_rural.append(np.random.choice([1, 2], p=[urban_prob, 1-urban_prob]))
        
        self.data.update({
            'Country': countries,
            'Age': ages,
            'Gender': genders,
            'Education': education,
            'Income_Level': income_levels,
            'Urban_Rural': urban_rural
        })
    
    def generate_banking_profile(self):
        """Generate banking-related variables with realistic patterns"""
        print("Generating banking profile data...")
        
        # Bank type (correlated with country and age)
        bank_types = []
        for i, (country, age) in enumerate(zip(self.data['Country'], self.data['Age'])):
            if country == 1:  # Nigeria
                # Higher digital adoption in younger age groups
                if age < 30:
                    bank_type = np.random.choice([1, 2, 3], p=[0.45, 0.40, 0.15])
                elif age < 45:
                    bank_type = np.random.choice([1, 2, 3], p=[0.60, 0.30, 0.10])
                else:
                    bank_type = np.random.choice([1, 2, 3], p=[0.75, 0.20, 0.05])
            else:  # Ghana
                if age < 30:
                    bank_type = np.random.choice([1, 2, 3], p=[0.40, 0.45, 0.15])
                elif age < 45:
                    bank_type = np.random.choice([1, 2, 3], p=[0.55, 0.35, 0.10])
                else:
                    bank_type = np.random.choice([1, 2, 3], p=[0.70, 0.25, 0.05])
            bank_types.append(bank_type)
        
        # Years with account (correlated with age and bank type)
        years_with_account = []
        for age, bank_type in zip(self.data['Age'], bank_types):
            if bank_type == 2:  # Digital-only banks are newer
                max_years = min(age - 18, 8)
            else:
                max_years = age - 18
            years = np.random.randint(0, max_years + 1)
            years_with_account.append(years)
        
        # Frequency of use (correlated with bank type and age)
        frequency_use = []
        for bank_type, age, years in zip(bank_types, self.data['Age'], years_with_account):
            if bank_type == 2:  # Digital banks - higher frequency
                if age < 35:
                    freq = np.random.choice([1, 2, 3, 4, 5], p=[0.30, 0.35, 0.25, 0.08, 0.02])
                else:
                    freq = np.random.choice([1, 2, 3, 4, 5], p=[0.20, 0.30, 0.30, 0.15, 0.05])
            else:  # Traditional banks
                if age < 35:
                    freq = np.random.choice([1, 2, 3, 4, 5], p=[0.15, 0.25, 0.35, 0.20, 0.05])
                else:
                    freq = np.random.choice([1, 2, 3, 4, 5], p=[0.10, 0.20, 0.30, 0.30, 0.10])
            frequency_use.append(freq)
        
        self.data.update({
            'Bank_Type': bank_types,
            'Years_with_Account': years_with_account,
            'Frequency_of_Use': frequency_use
        })
    
    def generate_fraud_experience(self):
        """Generate fraud experience and related variables"""
        print("Generating fraud experience data...")
        
        # Past victim status (correlated with country, age, and banking profile)
        past_victim = []
        for i, (country, age, bank_type, frequency) in enumerate(zip(
            self.data['Country'], self.data['Age'], 
            self.data['Bank_Type'], self.data['Frequency_of_Use']
        )):
            base_prob = self.country_params[country]['fraud_rate']
            
            # Digital bank users slightly more likely to be victims
            if bank_type == 2:
                base_prob *= 1.2
            
            # Higher frequency users more exposed
            if frequency <= 2:  # Daily/Weekly
                base_prob *= 1.3
            elif frequency == 3:  # Monthly
                base_prob *= 1.1
            
            # Younger users more likely to be victims (less cautious)
            if age < 30:
                base_prob *= 1.4
            elif age < 45:
                base_prob *= 1.1
            
            victim = np.random.random() < min(base_prob, 0.6)  # Cap at 60%
            past_victim.append(int(victim))
        
        # Additional fraud-related variables
        fraud_awareness = []
        fraud_concern = []
        security_knowledge = []
        
        for i, (victim, age, education, bank_type) in enumerate(zip(
            past_victim, self.data['Age'], 
            self.data['Education'], self.data['Bank_Type']
        )):
            # Fraud awareness (1-5 scale)
            awareness = 3 + np.random.normal(0, 0.8)
            if victim:
                awareness += 0.5  # Victims more aware
            if education >= 4:  # Higher education
                awareness += 0.3
            if bank_type == 2:  # Digital bank users
                awareness += 0.2
            awareness = np.clip(awareness, 1, 5)
            fraud_awareness.append(round(awareness, 1))
            
            # Fraud concern (1-5 scale)
            concern = 3 + np.random.normal(0, 0.7)
            if victim:
                concern += 0.8  # Victims more concerned
            if age > 45:  # Older users more concerned
                concern += 0.3
            concern = np.clip(concern, 1, 5)
            fraud_concern.append(round(concern, 1))
            
            # Security knowledge (1-5 scale)
            knowledge = 2.5 + np.random.normal(0, 0.9)
            if education >= 5:  # Higher education
                knowledge += 0.5
            if bank_type == 2:  # Digital bank users
                knowledge += 0.3
            if age < 35:  # Younger users
                knowledge += 0.2
            knowledge = np.clip(knowledge, 1, 5)
            security_knowledge.append(round(knowledge, 1))
        
        self.data.update({
            'Past_Victim': past_victim,
            'Fraud_Awareness': fraud_awareness,
            'Fraud_Concern': fraud_concern,
            'Security_Knowledge': security_knowledge
        })
    
    def generate_additional_variables(self):
        """Generate additional variables for comprehensive analysis"""
        print("Generating additional variables...")
        
        # Technology adoption
        tech_adoption = []
        smartphone_usage = []
        internet_usage = []
        
        for age, education, urban, bank_type in zip(
            self.data['Age'], self.data['Education'],
            self.data['Urban_Rural'], self.data['Bank_Type']
        ):
            # Technology adoption (1-5 scale)
            tech = 2.5 + np.random.normal(0, 0.8)
            if age < 35:
                tech += 0.8
            elif age < 50:
                tech += 0.3
            if education >= 4:
                tech += 0.4
            if urban == 1:
                tech += 0.3
            if bank_type == 2:
                tech += 0.5
            tech = np.clip(tech, 1, 5)
            tech_adoption.append(round(tech, 1))
            
            # Smartphone usage (1-5 scale)
            smartphone = 3 + np.random.normal(0, 0.7)
            if age < 40:
                smartphone += 0.5
            if bank_type == 2:
                smartphone += 0.4
            smartphone = np.clip(smartphone, 1, 5)
            smartphone_usage.append(round(smartphone, 1))
            
            # Internet usage (1-5 scale)
            internet = 2.8 + np.random.normal(0, 0.8)
            if age < 35:
                internet += 0.6
            if education >= 4:
                internet += 0.4
            if urban == 1:
                internet += 0.3
            internet = np.clip(internet, 1, 5)
            internet_usage.append(round(internet, 1))
        
        # Trust in banking system
        trust_banking = []
        trust_digital = []
        
        for country, victim, age, bank_type in zip(
            self.data['Country'], self.data['Past_Victim'],
            self.data['Age'], self.data['Bank_Type']
        ):
            # Trust in traditional banking (1-5 scale)
            trust_trad = 3.2 + np.random.normal(0, 0.6)
            if victim:
                trust_trad -= 0.5
            if age > 50:
                trust_trad += 0.3
            if country == 2:  # Ghana slightly higher trust
                trust_trad += 0.2
            trust_trad = np.clip(trust_trad, 1, 5)
            trust_banking.append(round(trust_trad, 1))
            
            # Trust in digital banking (1-5 scale)
            trust_dig = 2.8 + np.random.normal(0, 0.7)
            if victim:
                trust_dig -= 0.3
            if age < 35:
                trust_dig += 0.4
            if bank_type == 2:
                trust_dig += 0.5
            if education >= 4:
                trust_dig += 0.2
            trust_dig = np.clip(trust_dig, 1, 5)
            trust_digital.append(round(trust_dig, 1))
        
        # Financial literacy
        financial_literacy = []
        for education, age, income in zip(
            self.data['Education'], self.data['Age'], self.data['Income_Level']
        ):
            literacy = 2.5 + np.random.normal(0, 0.8)
            if education >= 4:
                literacy += 0.6
            if income >= 4:
                literacy += 0.3
            if age >= 25 and age <= 45:  # Peak earning years
                literacy += 0.2
            literacy = np.clip(literacy, 1, 5)
            financial_literacy.append(round(literacy, 1))
        
        # Risk tolerance
        risk_tolerance = []
        for age, gender, income, education in zip(
            self.data['Age'], self.data['Gender'], 
            self.data['Income_Level'], self.data['Education']
        ):
            risk = 2.8 + np.random.normal(0, 0.7)
            if age < 30:
                risk += 0.4
            elif age > 50:
                risk -= 0.3
            if gender == 1:  # Male
                risk += 0.2
            if income >= 5:
                risk += 0.3
            if education >= 5:
                risk += 0.2
            risk = np.clip(risk, 1, 5)
            risk_tolerance.append(round(risk, 1))
        
        self.data.update({
            'Tech_Adoption': tech_adoption,
            'Smartphone_Usage': smartphone_usage,
            'Internet_Usage': internet_usage,
            'Trust_Traditional_Banking': trust_banking,
            'Trust_Digital_Banking': trust_digital,
            'Financial_Literacy': financial_literacy,
            'Risk_Tolerance': risk_tolerance
        })
    
    def generate_control_variables(self):
        """Generate additional control variables"""
        print("Generating control variables...")
        
        # Marital status
        marital_status = []
        for age in self.data['Age']:
            if age < 25:
                status = np.random.choice([1, 2, 3, 4], p=[0.70, 0.20, 0.08, 0.02])
            elif age < 35:
                status = np.random.choice([1, 2, 3, 4], p=[0.30, 0.50, 0.15, 0.05])
            elif age < 50:
                status = np.random.choice([1, 2, 3, 4], p=[0.15, 0.60, 0.20, 0.05])
            else:
                status = np.random.choice([1, 2, 3, 4], p=[0.10, 0.55, 0.25, 0.10])
            marital_status.append(status)
        
        # Employment status
        employment = []
        for age, education in zip(self.data['Age'], self.data['Education']):
            if age < 22:
                emp = np.random.choice([1, 2, 3, 4], p=[0.20, 0.60, 0.15, 0.05])
            elif age < 65:
                if education >= 4:
                    emp = np.random.choice([1, 2, 3, 4], p=[0.70, 0.15, 0.10, 0.05])
                else:
                    emp = np.random.choice([1, 2, 3, 4], p=[0.60, 0.20, 0.15, 0.05])
            else:
                emp = np.random.choice([1, 2, 3, 4], p=[0.10, 0.20, 0.60, 0.10])
            employment.append(emp)
        
        # Household size
        household_size = []
        for age, marital in zip(self.data['Age'], marital_status):
            if age < 25:
                size = np.random.poisson(3.5)
            elif age < 35:
                if marital == 2:  # Married
                    size = np.random.poisson(4.2)
                else:
                    size = np.random.poisson(2.8)
            elif age < 50:
                if marital == 2:
                    size = np.random.poisson(4.8)
                else:
                    size = np.random.poisson(3.2)
            else:
                if marital == 2:
                    size = np.random.poisson(3.5)
                else:
                    size = np.random.poisson(2.0)
            size = max(1, min(size, 10))  # Reasonable bounds
            household_size.append(size)
        
        self.data.update({
            'Marital_Status': marital_status,
            'Employment_Status': employment,
            'Household_Size': household_size
        })
    
    def create_dataframe(self):
        """Create and return the final DataFrame"""
        print("Creating final dataset...")
        
        df = pd.DataFrame(self.data)
        
        # Add derived variables
        df['Age_Group'] = pd.cut(df['Age'], bins=[17, 25, 35, 45, 55, 65], 
                                labels=['18-24', '25-34', '35-44', '45-54', '55-65'])
        
        df['Education_Level'] = df['Education'].map({
            1: 'No formal', 2: 'Primary', 3: 'Secondary', 
            4: 'Diploma', 5: 'Bachelor', 6: 'Postgraduate'
        })
        
        df['Bank_Type_Name'] = df['Bank_Type'].map({
            1: 'Traditional Commercial', 2: 'Digital-Only Bank', 3: 'Microfinance'
        })
        
        df['Country_Name'] = df['Country'].map({1: 'Nigeria', 2: 'Ghana'})
        
        # Reorder columns for better organization
        column_order = [
            'Country', 'Country_Name', 'Age', 'Age_Group', 'Gender', 'Education', 'Education_Level',
            'Income_Level', 'Urban_Rural', 'Marital_Status', 'Employment_Status', 'Household_Size',
            'Bank_Type', 'Bank_Type_Name', 'Years_with_Account', 'Frequency_of_Use',
            'Past_Victim', 'Fraud_Awareness', 'Fraud_Concern', 'Security_Knowledge',
            'Tech_Adoption', 'Smartphone_Usage', 'Internet_Usage',
            'Trust_Traditional_Banking', 'Trust_Digital_Banking',
            'Financial_Literacy', 'Risk_Tolerance'
        ]
        
        df = df[column_order]
        
        return df
    
    def generate_dataset(self):
        """Generate the complete dataset"""
        print(f"Generating comprehensive dataset with {self.sample_size} observations...")
        
        self.generate_demographics()
        self.generate_banking_profile()
        self.generate_fraud_experience()
        self.generate_additional_variables()
        self.generate_control_variables()
        
        df = self.create_dataframe()
        
        print(f"Dataset generated successfully with {len(df)} observations and {len(df.columns)} variables")
        return df

def main():
    """Main function to generate and save the dataset"""
    print("=" * 60)
    print("COMPREHENSIVE DIGITAL BANKING FRAUD CONTROL DATASET GENERATOR")
    print("=" * 60)
    
    # Generate dataset
    generator = BankingFraudDatasetGenerator(sample_size=5000)
    df = generator.generate_dataset()
    
    # Create output directory
    os.makedirs('/workspace/dataset', exist_ok=True)
    
    # Save in multiple formats
    print("\nSaving dataset in multiple formats...")
    
    # CSV format
    csv_path = '/workspace/dataset/banking_fraud_dataset.csv'
    df.to_csv(csv_path, index=False)
    print(f"✓ CSV saved: {csv_path}")
    
    # Excel format
    excel_path = '/workspace/dataset/banking_fraud_dataset.xlsx'
    df.to_excel(excel_path, index=False, sheet_name='Banking_Fraud_Data')
    print(f"✓ Excel saved: {excel_path}")
    
    # JSON format
    json_path = '/workspace/dataset/banking_fraud_dataset.json'
    df.to_json(json_path, orient='records', indent=2)
    print(f"✓ JSON saved: {json_path}")
    
    # Create data dictionary
    data_dict = {
        'dataset_info': {
            'name': 'Digital Banking Fraud Control Research Dataset',
            'description': 'Comprehensive dataset for analyzing digital banking fraud control mechanisms',
            'sample_size': len(df),
            'variables': len(df.columns),
            'countries': ['Nigeria', 'Ghana'],
            'generated_date': datetime.now().isoformat()
        },
        'variable_definitions': {
            'Country': '1=Nigeria, 2=Ghana',
            'Age': 'Continuous variable (18-65)',
            'Gender': '1=Male, 2=Female, 3=Other/Prefer not to say',
            'Education': '1=No formal, 2=Primary, 3=Secondary, 4=Diploma, 5=Bachelor, 6=Postgraduate',
            'Income_Level': '1=Very Low, 2=Low, 3=Below Average, 4=Average, 5=Above Average, 6=High',
            'Urban_Rural': '1=Urban, 2=Rural',
            'Bank_Type': '1=Traditional Commercial, 2=Digital-Only Bank, 3=Microfinance',
            'Years_with_Account': 'Number of years with current bank account',
            'Frequency_of_Use': '1=Daily, 2=Weekly, 3=Monthly, 4=Quarterly, 5=Less than monthly',
            'Past_Victim': '1=Yes, 0=No - Have you ever been a victim of bank fraud?',
            'Fraud_Awareness': '1-5 scale: How aware are you of banking fraud risks?',
            'Fraud_Concern': '1-5 scale: How concerned are you about banking fraud?',
            'Security_Knowledge': '1-5 scale: How knowledgeable are you about banking security?',
            'Tech_Adoption': '1-5 scale: General technology adoption level',
            'Smartphone_Usage': '1-5 scale: Smartphone usage frequency',
            'Internet_Usage': '1-5 scale: Internet usage frequency',
            'Trust_Traditional_Banking': '1-5 scale: Trust in traditional banking',
            'Trust_Digital_Banking': '1-5 scale: Trust in digital banking',
            'Financial_Literacy': '1-5 scale: Financial literacy level',
            'Risk_Tolerance': '1-5 scale: Risk tolerance level',
            'Marital_Status': '1=Single, 2=Married, 3=Divorced, 4=Widowed',
            'Employment_Status': '1=Employed, 2=Student, 3=Unemployed, 4=Retired',
            'Household_Size': 'Number of people in household'
        }
    }
    
    dict_path = '/workspace/dataset/data_dictionary.json'
    with open(dict_path, 'w') as f:
        json.dump(data_dict, f, indent=2)
    print(f"✓ Data dictionary saved: {dict_path}")
    
    # Generate summary statistics
    summary_path = '/workspace/dataset/dataset_summary.txt'
    with open(summary_path, 'w') as f:
        f.write("DATASET SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total Observations: {len(df)}\n")
        f.write(f"Total Variables: {len(df.columns)}\n\n")
        
        f.write("COUNTRY DISTRIBUTION:\n")
        f.write(str(df['Country_Name'].value_counts()) + "\n\n")
        
        f.write("GENDER DISTRIBUTION:\n")
        f.write(str(df['Gender'].value_counts()) + "\n\n")
        
        f.write("BANK TYPE DISTRIBUTION:\n")
        f.write(str(df['Bank_Type_Name'].value_counts()) + "\n\n")
        
        f.write("FRAUD VICTIM RATE:\n")
        f.write(f"Overall: {df['Past_Victim'].mean():.2%}\n")
        f.write(f"Nigeria: {df[df['Country']==1]['Past_Victim'].mean():.2%}\n")
        f.write(f"Ghana: {df[df['Country']==2]['Past_Victim'].mean():.2%}\n\n")
        
        f.write("DESCRIPTIVE STATISTICS:\n")
        f.write(str(df.describe()))
    
    print(f"✓ Summary statistics saved: {summary_path}")
    
    print("\n" + "=" * 60)
    print("DATASET GENERATION COMPLETE!")
    print("=" * 60)
    print(f"Files created in /workspace/dataset/:")
    print(f"  - banking_fraud_dataset.csv")
    print(f"  - banking_fraud_dataset.xlsx") 
    print(f"  - banking_fraud_dataset.json")
    print(f"  - data_dictionary.json")
    print(f"  - dataset_summary.txt")
    
    return df

if __name__ == "__main__":
    df = main()