#!/usr/bin/env python3
"""
Comprehensive Dataset Analysis Script
Demonstrates the capabilities and insights from the banking fraud dataset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json

def load_and_explore_data():
    """Load and perform initial exploration of the dataset"""
    print("=" * 60)
    print("COMPREHENSIVE DATASET ANALYSIS")
    print("=" * 60)
    
    # Load dataset
    df = pd.read_csv('/workspace/banking_fraud_dataset.csv')
    print(f"Dataset loaded: {len(df)} observations, {len(df.columns)} variables")
    
    # Basic info
    print(f"\nDataset Shape: {df.shape}")
    print(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    return df

def demographic_analysis(df):
    """Comprehensive demographic analysis"""
    print("\n" + "=" * 40)
    print("DEMOGRAPHIC ANALYSIS")
    print("=" * 40)
    
    # Country distribution
    print("\nCountry Distribution:")
    country_dist = df['Country'].value_counts()
    for country, count in country_dist.items():
        pct = count / len(df) * 100
        print(f"  {country}: {count:,} ({pct:.1f}%)")
    
    # Age analysis
    print(f"\nAge Statistics:")
    print(f"  Mean: {df['Age'].mean():.1f} years")
    print(f"  Median: {df['Age'].median():.1f} years")
    print(f"  Range: {df['Age'].min()}-{df['Age'].max()} years")
    print(f"  Std Dev: {df['Age'].std():.1f} years")
    
    # Gender distribution
    print(f"\nGender Distribution:")
    gender_dist = df['Gender'].value_counts()
    gender_labels = {1: 'Male', 2: 'Female', 3: 'Other/Prefer not to say'}
    for gender, count in gender_dist.items():
        pct = count / len(df) * 100
        print(f"  {gender_labels[gender]}: {count:,} ({pct:.1f}%)")
    
    # Education distribution
    print(f"\nEducation Distribution:")
    edu_dist = df['Education'].value_counts().sort_index()
    edu_labels = {1: 'No formal', 2: 'Primary', 3: 'Secondary', 
                  4: 'Diploma/Cert', 5: "Bachelor's", 6: 'Postgraduate'}
    for edu, count in edu_dist.items():
        pct = count / len(df) * 100
        print(f"  {edu_labels[edu]}: {count:,} ({pct:.1f}%)")

def banking_profile_analysis(df):
    """Banking profile analysis"""
    print("\n" + "=" * 40)
    print("BANKING PROFILE ANALYSIS")
    print("=" * 40)
    
    # Bank type distribution
    print("\nBank Type Distribution:")
    bank_dist = df['Bank_Type'].value_counts()
    bank_labels = {1: 'Traditional Commercial', 2: 'Digital-Only Bank', 3: 'Microfinance'}
    for bank_type, count in bank_dist.items():
        pct = count / len(df) * 100
        print(f"  {bank_labels[bank_type]}: {count:,} ({pct:.1f}%)")
    
    # Years with account
    print(f"\nYears with Account:")
    print(f"  Mean: {df['Years_with_Account'].mean():.1f} years")
    print(f"  Median: {df['Years_with_Account'].median():.1f} years")
    print(f"  Range: {df['Years_with_Account'].min()}-{df['Years_with_Account'].max()} years")
    
    # Frequency of use
    print(f"\nFrequency of Use Distribution:")
    freq_dist = df['Frequency_of_Use'].value_counts().sort_index()
    freq_labels = {1: 'Daily', 2: 'Weekly', 3: 'Monthly', 4: 'Quarterly', 5: 'Less than monthly'}
    for freq, count in freq_dist.items():
        pct = count / len(df) * 100
        print(f"  {freq_labels[freq]}: {count:,} ({pct:.1f}%)")

def fraud_analysis(df):
    """Comprehensive fraud analysis"""
    print("\n" + "=" * 40)
    print("FRAUD EXPERIENCE ANALYSIS")
    print("=" * 40)
    
    # Overall fraud victimization
    total_victims = df['Past_Victim'].sum()
    victim_rate = df['Past_Victim'].mean() * 100
    print(f"\nOverall Fraud Victimization:")
    print(f"  Total Victims: {total_victims:,} ({victim_rate:.1f}%)")
    print(f"  Non-Victims: {len(df) - total_victims:,} ({100-victim_rate:.1f}%)")
    
    # Fraud by country
    print(f"\nFraud Victimization by Country:")
    country_fraud = df.groupby('Country')['Past_Victim'].agg(['count', 'sum', 'mean'])
    for country in country_fraud.index:
        total = country_fraud.loc[country, 'count']
        victims = country_fraud.loc[country, 'sum']
        rate = country_fraud.loc[country, 'mean'] * 100
        print(f"  {country}: {victims:,}/{total:,} ({rate:.1f}%)")
    
    # Fraud by bank type
    print(f"\nFraud Victimization by Bank Type:")
    bank_fraud = df.groupby('Bank_Type')['Past_Victim'].agg(['count', 'sum', 'mean'])
    bank_labels = {1: 'Traditional Commercial', 2: 'Digital-Only Bank', 3: 'Microfinance'}
    for bank_type in bank_fraud.index:
        total = bank_fraud.loc[bank_type, 'count']
        victims = bank_fraud.loc[bank_type, 'sum']
        rate = bank_fraud.loc[bank_type, 'mean'] * 100
        print(f"  {bank_labels[bank_type]}: {victims:,}/{total:,} ({rate:.1f}%)")
    
    # Fraud incidents analysis (victims only)
    victims_df = df[df['Past_Victim'] == 1]
    if len(victims_df) > 0:
        print(f"\nFraud Incidents Analysis (Victims Only):")
        print(f"  Mean Incidents: {victims_df['Fraud_Incidents'].mean():.1f}")
        print(f"  Median Incidents: {victims_df['Fraud_Incidents'].median():.1f}")
        print(f"  Range: {victims_df['Fraud_Incidents'].min()}-{victims_df['Fraud_Incidents'].max()}")
        
        # Fraud types
        print(f"\nMost Common Fraud Types:")
        fraud_types = victims_df['Fraud_Types'].str.split('; ').explode()
        type_counts = fraud_types.value_counts().head(5)
        for fraud_type, count in type_counts.items():
            pct = count / len(victims_df) * 100
            print(f"  {fraud_type}: {count:,} ({pct:.1f}%)")
        
        # Fraud amounts
        print(f"\nFraud Amount Analysis:")
        print(f"  Mean Amount: {victims_df['Fraud_Amount'].mean():,.2f}")
        print(f"  Median Amount: {victims_df['Fraud_Amount'].median():,.2f}")
        print(f"  Max Amount: {victims_df['Fraud_Amount'].max():,.2f}")

def psychological_analysis(df):
    """Psychological and behavioral analysis"""
    print("\n" + "=" * 40)
    print("PSYCHOLOGICAL & BEHAVIORAL ANALYSIS")
    print("=" * 40)
    
    # Continuous variables analysis
    psych_vars = ['Tech_Adoption', 'Risk_Tolerance', 'Financial_Literacy', 
                  'Trust_Banking', 'Mobile_Usage', 'Internet_Quality']
    
    print(f"\nPsychological Variables (1-5 Scale):")
    for var in psych_vars:
        mean_val = df[var].mean()
        std_val = df[var].std()
        print(f"  {var}: {mean_val:.2f} ± {std_val:.2f}")
    
    # Correlation analysis
    print(f"\nKey Correlations:")
    correlations = df[psych_vars + ['Past_Victim']].corr()['Past_Victim'].sort_values(ascending=False)
    for var, corr in correlations.items():
        if var != 'Past_Victim':
            print(f"  {var} vs Past_Victim: {corr:.3f}")

def statistical_tests(df):
    """Perform key statistical tests"""
    print("\n" + "=" * 40)
    print("STATISTICAL TESTS")
    print("=" * 40)
    
    # Chi-square test: Bank type vs Victim status
    contingency_table = pd.crosstab(df['Bank_Type'], df['Past_Victim'])
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
    print(f"\nChi-square Test: Bank Type vs Victim Status")
    print(f"  Chi-square statistic: {chi2:.3f}")
    print(f"  p-value: {p_value:.6f}")
    print(f"  Degrees of freedom: {dof}")
    print(f"  Significant: {'Yes' if p_value < 0.05 else 'No'} (α = 0.05)")
    
    # T-test: Age difference between victims and non-victims
    victims_age = df[df['Past_Victim'] == 1]['Age']
    non_victims_age = df[df['Past_Victim'] == 0]['Age']
    t_stat, t_p_value = stats.ttest_ind(victims_age, non_victims_age)
    print(f"\nT-test: Age Difference (Victims vs Non-Victims)")
    print(f"  T-statistic: {t_stat:.3f}")
    print(f"  p-value: {t_p_value:.6f}")
    print(f"  Mean age - Victims: {victims_age.mean():.1f}")
    print(f"  Mean age - Non-victims: {non_victims_age.mean():.1f}")
    print(f"  Significant: {'Yes' if t_p_value < 0.05 else 'No'} (α = 0.05)")

def generate_insights(df):
    """Generate key insights and recommendations"""
    print("\n" + "=" * 40)
    print("KEY INSIGHTS & RECOMMENDATIONS")
    print("=" * 40)
    
    insights = []
    
    # Fraud rate insights
    overall_rate = df['Past_Victim'].mean() * 100
    digital_rate = df[df['Bank_Type'] == 2]['Past_Victim'].mean() * 100
    traditional_rate = df[df['Bank_Type'] == 1]['Past_Victim'].mean() * 100
    
    insights.append(f"• Overall fraud victimization rate: {overall_rate:.1f}%")
    insights.append(f"• Digital bank users have {digital_rate:.1f}% fraud rate vs {traditional_rate:.1f}% for traditional banks")
    
    # Age insights
    victims_age_mean = df[df['Past_Victim'] == 1]['Age'].mean()
    non_victims_age_mean = df[df['Past_Victim'] == 0]['Age'].mean()
    insights.append(f"• Fraud victims are on average {victims_age_mean:.1f} years old vs {non_victims_age_mean:.1f} for non-victims")
    
    # Country insights
    nigeria_rate = df[df['Country'] == 'Nigeria']['Past_Victim'].mean() * 100
    ghana_rate = df[df['Country'] == 'Ghana']['Past_Victim'].mean() * 100
    insights.append(f"• Nigeria has {nigeria_rate:.1f}% fraud rate vs {ghana_rate:.1f}% in Ghana")
    
    # Technology insights
    tech_corr = df['Tech_Adoption'].corr(df['Past_Victim'])
    insights.append(f"• Technology adoption shows {tech_corr:.3f} correlation with fraud victimization")
    
    # Trust insights
    trust_corr = df['Trust_Banking'].corr(df['Past_Victim'])
    insights.append(f"• Trust in banking shows {trust_corr:.3f} correlation with fraud victimization")
    
    print("\nKey Findings:")
    for insight in insights:
        print(insight)
    
    print(f"\nResearch Recommendations:")
    print("• Focus on digital bank users as high-risk group")
    print("• Consider age-specific fraud prevention strategies")
    print("• Investigate country-specific fraud patterns")
    print("• Explore technology adoption as a risk factor")
    print("• Examine trust-building interventions")

def main():
    """Main analysis function"""
    # Load data
    df = load_and_explore_data()
    
    # Run analyses
    demographic_analysis(df)
    banking_profile_analysis(df)
    fraud_analysis(df)
    psychological_analysis(df)
    statistical_tests(df)
    generate_insights(df)
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print("This dataset is ready for advanced statistical analysis and machine learning applications.")
    print("All files are available in the /workspace directory.")

if __name__ == "__main__":
    main()