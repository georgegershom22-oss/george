#!/usr/bin/env python3
"""
Comprehensive Dataset Analysis Script
Demonstrates the statistical relationships and patterns in the generated dataset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

def load_dataset():
    """Load the generated dataset"""
    df = pd.read_csv('/workspace/dataset/banking_fraud_dataset.csv')
    return df

def basic_descriptive_analysis(df):
    """Perform basic descriptive analysis"""
    print("=" * 80)
    print("COMPREHENSIVE DATASET ANALYSIS")
    print("=" * 80)
    
    print(f"\nDataset Overview:")
    print(f"Total Observations: {len(df):,}")
    print(f"Total Variables: {len(df.columns)}")
    print(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    print(f"\nMissing Values:")
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("✓ No missing values found")
    else:
        print(missing[missing > 0])
    
    return df

def demographic_analysis(df):
    """Analyze demographic characteristics"""
    print("\n" + "=" * 60)
    print("DEMOGRAPHIC ANALYSIS")
    print("=" * 60)
    
    # Country distribution
    print("\nCountry Distribution:")
    country_dist = df['Country_Name'].value_counts(normalize=True) * 100
    for country, pct in country_dist.items():
        print(f"  {country}: {pct:.1f}%")
    
    # Age analysis
    print(f"\nAge Statistics:")
    print(f"  Mean Age: {df['Age'].mean():.1f} years")
    print(f"  Median Age: {df['Age'].median():.1f} years")
    print(f"  Age Range: {df['Age'].min()}-{df['Age'].max()} years")
    
    # Gender distribution
    print(f"\nGender Distribution:")
    gender_dist = df['Gender'].value_counts(normalize=True) * 100
    gender_map = {1: 'Male', 2: 'Female', 3: 'Other/Prefer not to say'}
    for gender, pct in gender_dist.items():
        print(f"  {gender_map[gender]}: {pct:.1f}%")
    
    # Education distribution
    print(f"\nEducation Distribution:")
    edu_dist = df['Education_Level'].value_counts(normalize=True) * 100
    for edu, pct in edu_dist.items():
        print(f"  {edu}: {pct:.1f}%")
    
    # Income distribution
    print(f"\nIncome Level Distribution:")
    income_dist = df['Income_Level'].value_counts(normalize=True) * 100
    income_map = {1: 'Very Low', 2: 'Low', 3: 'Below Average', 
                 4: 'Average', 5: 'Above Average', 6: 'High'}
    for income, pct in income_dist.items():
        print(f"  {income_map[income]}: {pct:.1f}%")

def banking_profile_analysis(df):
    """Analyze banking profile characteristics"""
    print("\n" + "=" * 60)
    print("BANKING PROFILE ANALYSIS")
    print("=" * 60)
    
    # Bank type distribution
    print("\nBank Type Distribution:")
    bank_dist = df['Bank_Type_Name'].value_counts(normalize=True) * 100
    for bank_type, pct in bank_dist.items():
        print(f"  {bank_type}: {pct:.1f}%")
    
    # Years with account
    print(f"\nYears with Account:")
    print(f"  Mean: {df['Years_with_Account'].mean():.1f} years")
    print(f"  Median: {df['Years_with_Account'].median():.1f} years")
    print(f"  Range: {df['Years_with_Account'].min()}-{df['Years_with_Account'].max()} years")
    
    # Frequency of use
    print(f"\nFrequency of Use Distribution:")
    freq_dist = df['Frequency_of_Use'].value_counts(normalize=True) * 100
    freq_map = {1: 'Daily', 2: 'Weekly', 3: 'Monthly', 
                4: 'Quarterly', 5: 'Less than monthly'}
    for freq, pct in freq_dist.items():
        print(f"  {freq_map[freq]}: {pct:.1f}%")

def fraud_analysis(df):
    """Analyze fraud-related variables"""
    print("\n" + "=" * 60)
    print("FRAUD ANALYSIS")
    print("=" * 60)
    
    # Overall fraud victim rate
    overall_rate = df['Past_Victim'].mean() * 100
    print(f"\nOverall Fraud Victim Rate: {overall_rate:.1f}%")
    
    # Fraud rate by country
    print(f"\nFraud Rate by Country:")
    for country in df['Country_Name'].unique():
        country_data = df[df['Country_Name'] == country]
        rate = country_data['Past_Victim'].mean() * 100
        print(f"  {country}: {rate:.1f}%")
    
    # Fraud rate by bank type
    print(f"\nFraud Rate by Bank Type:")
    for bank_type in df['Bank_Type_Name'].unique():
        bank_data = df[df['Bank_Type_Name'] == bank_type]
        rate = bank_data['Past_Victim'].mean() * 100
        print(f"  {bank_type}: {rate:.1f}%")
    
    # Fraud rate by age group
    print(f"\nFraud Rate by Age Group:")
    for age_group in df['Age_Group'].unique():
        age_data = df[df['Age_Group'] == age_group]
        rate = age_data['Past_Victim'].mean() * 100
        print(f"  {age_group}: {rate:.1f}%")
    
    # Fraud awareness and concern statistics
    print(f"\nFraud Awareness Statistics:")
    print(f"  Mean: {df['Fraud_Awareness'].mean():.2f}")
    print(f"  Median: {df['Fraud_Awareness'].median():.2f}")
    print(f"  Std Dev: {df['Fraud_Awareness'].std():.2f}")
    
    print(f"\nFraud Concern Statistics:")
    print(f"  Mean: {df['Fraud_Concern'].mean():.2f}")
    print(f"  Median: {df['Fraud_Concern'].median():.2f}")
    print(f"  Std Dev: {df['Fraud_Concern'].std():.2f}")

def correlation_analysis(df):
    """Perform correlation analysis"""
    print("\n" + "=" * 60)
    print("CORRELATION ANALYSIS")
    print("=" * 60)
    
    # Select numeric variables for correlation
    numeric_vars = ['Age', 'Education', 'Income_Level', 'Years_with_Account', 
                   'Frequency_of_Use', 'Past_Victim', 'Fraud_Awareness', 
                   'Fraud_Concern', 'Security_Knowledge', 'Tech_Adoption',
                   'Trust_Traditional_Banking', 'Trust_Digital_Banking',
                   'Financial_Literacy', 'Risk_Tolerance']
    
    corr_matrix = df[numeric_vars].corr()
    
    # Key correlations with fraud victim status
    print("\nKey Correlations with Fraud Victim Status:")
    fraud_corr = corr_matrix['Past_Victim'].sort_values(ascending=False)
    for var, corr in fraud_corr.items():
        if var != 'Past_Victim':
            print(f"  {var}: {corr:.3f}")
    
    # Correlations between awareness, concern, and knowledge
    print(f"\nFraud-Related Variable Correlations:")
    fraud_vars = ['Fraud_Awareness', 'Fraud_Concern', 'Security_Knowledge']
    fraud_corr_subset = corr_matrix.loc[fraud_vars, fraud_vars]
    print(fraud_corr_subset.round(3))

def statistical_tests(df):
    """Perform statistical significance tests"""
    print("\n" + "=" * 60)
    print("STATISTICAL SIGNIFICANCE TESTS")
    print("=" * 60)
    
    # T-test: Fraud victim rate by country
    nigeria_victims = df[df['Country'] == 1]['Past_Victim']
    ghana_victims = df[df['Country'] == 2]['Past_Victim']
    
    t_stat, p_value = stats.ttest_ind(nigeria_victims, ghana_victims)
    print(f"\nT-test: Fraud Victim Rate by Country")
    print(f"  T-statistic: {t_stat:.3f}")
    print(f"  P-value: {p_value:.6f}")
    print(f"  Significant: {'Yes' if p_value < 0.05 else 'No'}")
    
    # Chi-square test: Bank type and fraud victim status
    contingency_table = pd.crosstab(df['Bank_Type'], df['Past_Victim'])
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
    print(f"\nChi-square Test: Bank Type vs Fraud Victim Status")
    print(f"  Chi-square statistic: {chi2:.3f}")
    print(f"  P-value: {p_value:.6f}")
    print(f"  Significant: {'Yes' if p_value < 0.05 else 'No'}")
    
    # ANOVA: Fraud awareness by age group
    age_groups = df['Age_Group'].unique()
    awareness_by_age = [df[df['Age_Group'] == group]['Fraud_Awareness'].values 
                       for group in age_groups if pd.notna(group)]
    
    f_stat, p_value = stats.f_oneway(*awareness_by_age)
    print(f"\nANOVA: Fraud Awareness by Age Group")
    print(f"  F-statistic: {f_stat:.3f}")
    print(f"  P-value: {p_value:.6f}")
    print(f"  Significant: {'Yes' if p_value < 0.05 else 'No'}")

def generate_insights(df):
    """Generate key insights from the dataset"""
    print("\n" + "=" * 60)
    print("KEY INSIGHTS")
    print("=" * 60)
    
    # Insight 1: Digital bank users and fraud
    digital_users = df[df['Bank_Type'] == 2]
    traditional_users = df[df['Bank_Type'] == 1]
    
    digital_fraud_rate = digital_users['Past_Victim'].mean() * 100
    traditional_fraud_rate = traditional_users['Past_Victim'].mean() * 100
    
    print(f"\n1. Digital vs Traditional Banking Fraud Rates:")
    print(f"   Digital-Only Banks: {digital_fraud_rate:.1f}%")
    print(f"   Traditional Banks: {traditional_fraud_rate:.1f}%")
    print(f"   Difference: {digital_fraud_rate - traditional_fraud_rate:.1f} percentage points")
    
    # Insight 2: Age and fraud vulnerability
    young_users = df[df['Age'] < 30]
    older_users = df[df['Age'] >= 45]
    
    young_fraud_rate = young_users['Past_Victim'].mean() * 100
    older_fraud_rate = older_users['Past_Victim'].mean() * 100
    
    print(f"\n2. Age and Fraud Vulnerability:")
    print(f"   Under 30: {young_fraud_rate:.1f}%")
    print(f"   45 and above: {older_fraud_rate:.1f}%")
    print(f"   Difference: {young_fraud_rate - older_fraud_rate:.1f} percentage points")
    
    # Insight 3: Education and security knowledge
    high_edu = df[df['Education'] >= 5]
    low_edu = df[df['Education'] <= 2]
    
    high_edu_security = high_edu['Security_Knowledge'].mean()
    low_edu_security = low_edu['Security_Knowledge'].mean()
    
    print(f"\n3. Education and Security Knowledge:")
    print(f"   High Education (Bachelor+): {high_edu_security:.2f}")
    print(f"   Low Education (Primary or less): {low_edu_security:.2f}")
    print(f"   Difference: {high_edu_security - low_edu_security:.2f} points")
    
    # Insight 4: Country differences
    nigeria_data = df[df['Country'] == 1]
    ghana_data = df[df['Country'] == 2]
    
    nigeria_digital_adoption = (nigeria_data['Bank_Type'] == 2).mean() * 100
    ghana_digital_adoption = (ghana_data['Bank_Type'] == 2).mean() * 100
    
    print(f"\n4. Digital Banking Adoption by Country:")
    print(f"   Nigeria: {nigeria_digital_adoption:.1f}%")
    print(f"   Ghana: {ghana_digital_adoption:.1f}%")
    print(f"   Difference: {ghana_digital_adoption - nigeria_digital_adoption:.1f} percentage points")

def main():
    """Main analysis function"""
    # Load dataset
    df = load_dataset()
    
    # Perform analyses
    basic_descriptive_analysis(df)
    demographic_analysis(df)
    banking_profile_analysis(df)
    fraud_analysis(df)
    correlation_analysis(df)
    statistical_tests(df)
    generate_insights(df)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    print("\nThis dataset provides rich opportunities for:")
    print("• Comparative analysis between Nigeria and Ghana")
    print("• Digital vs traditional banking behavior studies")
    print("• Fraud risk factor identification")
    print("• Demographic profiling of banking customers")
    print("• Technology adoption and trust analysis")
    print("• Statistical modeling and machine learning applications")

if __name__ == "__main__":
    main()