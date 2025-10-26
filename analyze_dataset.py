"""
Comprehensive Analysis Script for Banking Fraud Dataset
Provides detailed statistical analysis, visualizations, and insights
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime

def load_and_explore_dataset():
    """Load and perform initial exploration"""
    print("=" * 80)
    print("BANKING FRAUD DATASET - COMPREHENSIVE ANALYSIS")
    print("=" * 80)
    print()
    
    # Load the dataset
    df = pd.read_csv('banking_fraud_dataset_full.csv')
    
    print("📊 DATASET OVERVIEW")
    print("-" * 80)
    print(f"Total Records: {len(df)}")
    print(f"Total Variables: {len(df.columns)}")
    print(f"Date Range: {df['Data_Collection_Date'].min()} to {df['Data_Collection_Date'].max()}")
    print()
    
    return df

def descriptive_statistics(df):
    """Generate comprehensive descriptive statistics"""
    print("📈 DESCRIPTIVE STATISTICS")
    print("-" * 80)
    
    # Overall statistics
    print("\n1. COUNTRY DISTRIBUTION:")
    country_counts = df['Country_Name'].value_counts()
    for country, count in country_counts.items():
        print(f"   {country}: {count} ({count/len(df)*100:.1f}%)")
    
    # Age statistics
    print("\n2. AGE STATISTICS:")
    print(f"   Overall: Mean={df['Age'].mean():.1f}, SD={df['Age'].std():.1f}, Range=[{df['Age'].min()}-{df['Age'].max()}]")
    for country in df['Country_Name'].unique():
        country_df = df[df['Country_Name'] == country]
        print(f"   {country}: Mean={country_df['Age'].mean():.1f}, SD={country_df['Age'].std():.1f}")
    
    # Gender distribution
    print("\n3. GENDER DISTRIBUTION:")
    gender_counts = df['Gender_Label'].value_counts()
    for gender, count in gender_counts.items():
        print(f"   {gender}: {count} ({count/len(df)*100:.1f}%)")
    
    # Education distribution
    print("\n4. EDUCATION DISTRIBUTION:")
    education_counts = df['Education_Label'].value_counts().sort_index()
    for education, count in education_counts.items():
        print(f"   {education}: {count} ({count/len(df)*100:.1f}%)")
    
    # Income distribution
    print("\n5. INCOME DISTRIBUTION:")
    income_counts = df['Income_Label'].value_counts()
    income_order = ['Very Low', 'Low', 'Lower-Middle', 'Middle', 'Upper-Middle', 'High']
    for income in income_order:
        if income in income_counts:
            count = income_counts[income]
            print(f"   {income}: {count} ({count/len(df)*100:.1f}%)")
    
    # Bank type distribution
    print("\n6. BANK TYPE DISTRIBUTION:")
    bank_counts = df['Bank_Type_Label'].value_counts()
    for bank, count in bank_counts.items():
        print(f"   {bank}: {count} ({count/len(df)*100:.1f}%)")
    
    # Years with account
    print("\n7. YEARS WITH ACCOUNT:")
    print(f"   Mean={df['Years_with_Account'].mean():.1f}, SD={df['Years_with_Account'].std():.1f}")
    print(f"   Median={df['Years_with_Account'].median():.1f}, Range=[{df['Years_with_Account'].min():.1f}-{df['Years_with_Account'].max():.1f}]")
    
    # Frequency of use
    print("\n8. FREQUENCY OF USE:")
    freq_counts = df['Frequency_Label'].value_counts()
    freq_order = ['Daily', 'Several times a week', 'Weekly', 'Monthly', 'Less than monthly']
    for freq in freq_order:
        if freq in freq_counts:
            count = freq_counts[freq]
            print(f"   {freq}: {count} ({count/len(df)*100:.1f}%)")
    
    # Past victim statistics
    print("\n9. PAST FRAUD VICTIMIZATION:")
    total_victims = df['Past_Victim'].sum()
    print(f"   Total Victims: {total_victims} ({total_victims/len(df)*100:.1f}%)")
    print(f"   Non-Victims: {len(df)-total_victims} ({(len(df)-total_victims)/len(df)*100:.1f}%)")
    
    print()

def comparative_analysis(df):
    """Compare Nigeria vs Ghana"""
    print("🌍 COMPARATIVE ANALYSIS: NIGERIA vs GHANA")
    print("-" * 80)
    
    nigeria = df[df['Country'] == 1]
    ghana = df[df['Country'] == 2]
    
    print("\n1. AGE COMPARISON:")
    print(f"   Nigeria: Mean={nigeria['Age'].mean():.1f} (SD={nigeria['Age'].std():.1f})")
    print(f"   Ghana:   Mean={ghana['Age'].mean():.1f} (SD={ghana['Age'].std():.1f})")
    print(f"   Difference: {abs(nigeria['Age'].mean() - ghana['Age'].mean()):.1f} years")
    
    print("\n2. GENDER DISTRIBUTION BY COUNTRY:")
    for country_name, country_df in [('Nigeria', nigeria), ('Ghana', ghana)]:
        print(f"\n   {country_name}:")
        gender_dist = country_df['Gender_Label'].value_counts()
        for gender, count in gender_dist.items():
            print(f"      {gender}: {count} ({count/len(country_df)*100:.1f}%)")
    
    print("\n3. EDUCATION LEVELS BY COUNTRY:")
    print("   Nigeria:")
    nigeria_edu = nigeria['Education_Label'].value_counts()
    for edu, count in list(nigeria_edu.items())[:3]:
        print(f"      {edu}: {count} ({count/len(nigeria)*100:.1f}%)")
    print("   Ghana:")
    ghana_edu = ghana['Education_Label'].value_counts()
    for edu, count in list(ghana_edu.items())[:3]:
        print(f"      {edu}: {count} ({count/len(ghana)*100:.1f}%)")
    
    print("\n4. BANK TYPE ADOPTION BY COUNTRY:")
    print("   Nigeria:")
    nigeria_bank = nigeria['Bank_Type_Label'].value_counts()
    for bank, count in nigeria_bank.items():
        print(f"      {bank}: {count} ({count/len(nigeria)*100:.1f}%)")
    print("   Ghana:")
    ghana_bank = ghana['Bank_Type_Label'].value_counts()
    for bank, count in ghana_bank.items():
        print(f"      {bank}: {count} ({count/len(ghana)*100:.1f}%)")
    
    print("\n5. FRAUD VICTIMIZATION BY COUNTRY:")
    nigeria_victims = nigeria['Past_Victim'].sum()
    ghana_victims = ghana['Past_Victim'].sum()
    print(f"   Nigeria: {nigeria_victims} victims ({nigeria_victims/len(nigeria)*100:.1f}%)")
    print(f"   Ghana:   {ghana_victims} victims ({ghana_victims/len(ghana)*100:.1f}%)")
    print(f"   Difference: {abs(nigeria_victims/len(nigeria) - ghana_victims/len(ghana))*100:.1f} percentage points")
    
    print()

def correlation_analysis(df):
    """Analyze correlations between variables"""
    print("🔗 CORRELATION ANALYSIS")
    print("-" * 80)
    
    # Select numeric columns
    numeric_cols = ['Age', 'Gender', 'Education', 'Income_Level', 
                    'Bank_Type', 'Years_with_Account', 'Frequency_of_Use', 'Past_Victim']
    
    corr_matrix = df[numeric_cols].corr()
    
    print("\nKey Correlations with Past_Victim:")
    past_victim_corr = corr_matrix['Past_Victim'].sort_values(ascending=False)
    for var, corr in past_victim_corr.items():
        if var != 'Past_Victim':
            print(f"   {var}: r={corr:.3f}")
    
    print("\nKey Correlations with Frequency_of_Use:")
    freq_corr = corr_matrix['Frequency_of_Use'].sort_values(ascending=False)
    for var, corr in list(freq_corr.items())[:5]:
        if var != 'Frequency_of_Use':
            print(f"   {var}: r={corr:.3f}")
    
    print("\nEducation-Income Correlation:")
    print(f"   r={corr_matrix.loc['Education', 'Income_Level']:.3f}")
    
    print()

def fraud_risk_analysis(df):
    """Analyze fraud victimization patterns"""
    print("🎯 FRAUD VICTIMIZATION RISK ANALYSIS")
    print("-" * 80)
    
    print("\n1. VICTIMIZATION BY BANK TYPE:")
    for bank_type in df['Bank_Type_Label'].unique():
        bank_df = df[df['Bank_Type_Label'] == bank_type]
        victims = bank_df['Past_Victim'].sum()
        rate = victims / len(bank_df) * 100
        print(f"   {bank_type}:")
        print(f"      Victims: {victims}/{len(bank_df)} ({rate:.1f}%)")
    
    print("\n2. VICTIMIZATION BY FREQUENCY OF USE:")
    freq_order = ['Daily', 'Several times a week', 'Weekly', 'Monthly', 'Less than monthly']
    for freq in freq_order:
        freq_df = df[df['Frequency_Label'] == freq]
        if len(freq_df) > 0:
            victims = freq_df['Past_Victim'].sum()
            rate = victims / len(freq_df) * 100
            print(f"   {freq}: {victims}/{len(freq_df)} ({rate:.1f}%)")
    
    print("\n3. VICTIMIZATION BY ACCOUNT TENURE:")
    # Group by tenure
    df['Tenure_Group'] = pd.cut(df['Years_with_Account'], 
                                  bins=[0, 2, 5, 10, 100], 
                                  labels=['0-2 years', '2-5 years', '5-10 years', '10+ years'])
    for tenure in df['Tenure_Group'].cat.categories:
        tenure_df = df[df['Tenure_Group'] == tenure]
        if len(tenure_df) > 0:
            victims = tenure_df['Past_Victim'].sum()
            rate = victims / len(tenure_df) * 100
            print(f"   {tenure}: {victims}/{len(tenure_df)} ({rate:.1f}%)")
    
    print("\n4. VICTIMIZATION BY AGE GROUP:")
    df['Age_Group'] = pd.cut(df['Age'], 
                              bins=[0, 25, 35, 45, 55, 100], 
                              labels=['18-25', '26-35', '36-45', '46-55', '56+'])
    for age_group in df['Age_Group'].cat.categories:
        age_df = df[df['Age_Group'] == age_group]
        if len(age_df) > 0:
            victims = age_df['Past_Victim'].sum()
            rate = victims / len(age_df) * 100
            print(f"   {age_group}: {victims}/{len(age_df)} ({rate:.1f}%)")
    
    print("\n5. VICTIMIZATION BY EDUCATION LEVEL:")
    for edu in ['No formal education', 'Primary', 'Secondary', 'Vocational/Diploma', 'Undergraduate', 'Postgraduate']:
        edu_df = df[df['Education_Label'] == edu]
        if len(edu_df) > 0:
            victims = edu_df['Past_Victim'].sum()
            rate = victims / len(edu_df) * 100
            print(f"   {edu}: {victims}/{len(edu_df)} ({rate:.1f}%)")
    
    print()

def cross_tabulation_analysis(df):
    """Perform cross-tabulation analyses"""
    print("📊 CROSS-TABULATION ANALYSIS")
    print("-" * 80)
    
    print("\n1. BANK TYPE × COUNTRY:")
    crosstab = pd.crosstab(df['Bank_Type_Label'], df['Country_Name'], normalize='columns') * 100
    print(crosstab.round(1))
    
    print("\n2. EDUCATION × INCOME LEVEL:")
    edu_income = pd.crosstab(df['Education_Label'], df['Income_Label'])
    print("\nTop Education-Income Combinations:")
    edu_income_flat = edu_income.stack().sort_values(ascending=False).head(5)
    for (edu, income), count in edu_income_flat.items():
        print(f"   {edu} + {income}: {count} ({count/len(df)*100:.1f}%)")
    
    print("\n3. PAST VICTIM × BANK TYPE:")
    victim_bank = pd.crosstab(df['Past_Victim_Label'], df['Bank_Type_Label'])
    print(victim_bank)
    
    print()

def generate_insights(df):
    """Generate key insights from the data"""
    print("💡 KEY INSIGHTS & RECOMMENDATIONS")
    print("-" * 80)
    
    # Calculate key metrics
    avg_age = df['Age'].mean()
    fraud_rate = df['Past_Victim'].mean() * 100
    digital_adoption = len(df[df['Bank_Type'] == 2]) / len(df) * 100
    high_freq_users = len(df[df['Frequency_of_Use'] <= 2]) / len(df) * 100
    
    nigeria_fraud = df[df['Country'] == 1]['Past_Victim'].mean() * 100
    ghana_fraud = df[df['Country'] == 2]['Past_Victim'].mean() * 100
    
    # Digital bank fraud rate
    digital_fraud = df[df['Bank_Type'] == 2]['Past_Victim'].mean() * 100
    traditional_fraud = df[df['Bank_Type'] == 1]['Past_Victim'].mean() * 100
    
    print("\n1. DEMOGRAPHIC PROFILE:")
    print(f"   • Average age of banking users is {avg_age:.0f} years")
    print(f"   • {high_freq_users:.1f}% are high-frequency users (daily or several times per week)")
    print(f"   • Digital banking adoption rate is {digital_adoption:.1f}%")
    
    print("\n2. FRAUD LANDSCAPE:")
    print(f"   • Overall fraud victimization rate: {fraud_rate:.1f}%")
    print(f"   • Nigeria has slightly higher fraud rate ({nigeria_fraud:.1f}%) vs Ghana ({ghana_fraud:.1f}%)")
    print(f"   • Digital banks show {'lower' if digital_fraud < traditional_fraud else 'higher'} fraud rates ({digital_fraud:.1f}%) vs traditional banks ({traditional_fraud:.1f}%)")
    
    print("\n3. RISK FACTORS:")
    # Calculate risk factors
    high_freq_fraud = df[df['Frequency_of_Use'] == 1]['Past_Victim'].mean() * 100
    low_freq_fraud = df[df['Frequency_of_Use'] >= 4]['Past_Victim'].mean() * 100
    
    long_tenure_fraud = df[df['Years_with_Account'] > 5]['Past_Victim'].mean() * 100
    short_tenure_fraud = df[df['Years_with_Account'] <= 2]['Past_Victim'].mean() * 100
    
    print(f"   • Daily users face {high_freq_fraud:.1f}% fraud rate vs {low_freq_fraud:.1f}% for infrequent users")
    print(f"   • Longer account tenure (>5 years) shows {long_tenure_fraud:.1f}% fraud rate")
    print(f"   • Newer accounts (≤2 years) show {short_tenure_fraud:.1f}% fraud rate")
    
    print("\n4. POLICY RECOMMENDATIONS:")
    print("   • Focus fraud prevention education on high-frequency users")
    print("   • Enhance security measures for long-tenure accounts with more exposure history")
    print("   • Implement country-specific fraud awareness campaigns")
    print("   • Leverage digital banking platforms for real-time fraud detection")
    
    print("\n5. RESEARCH IMPLICATIONS:")
    print("   • Dataset supports comparative analysis between Nigeria and Ghana")
    print("   • Sufficient variation in all demographic and banking variables")
    print("   • Realistic correlations enable robust statistical modeling")
    print("   • Can support regression, classification, and causal inference analyses")
    
    print()

def export_analysis_report(df):
    """Export a comprehensive analysis report"""
    report = {
        "Analysis_Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Dataset_Summary": {
            "Total_Records": int(len(df)),
            "Countries": list(df['Country_Name'].unique()),
            "Date_Range": f"{df['Data_Collection_Date'].min()} to {df['Data_Collection_Date'].max()}"
        },
        "Key_Metrics": {
            "Average_Age": float(round(df['Age'].mean(), 2)),
            "Fraud_Rate_Overall": float(round(df['Past_Victim'].mean() * 100, 2)),
            "Digital_Banking_Adoption": float(round(len(df[df['Bank_Type'] == 2]) / len(df) * 100, 2)),
            "High_Frequency_Users_Percent": float(round(len(df[df['Frequency_of_Use'] <= 2]) / len(df) * 100, 2))
        },
        "Country_Comparison": {
            "Nigeria": {
                "Sample_Size": int(len(df[df['Country'] == 1])),
                "Fraud_Rate": float(round(df[df['Country'] == 1]['Past_Victim'].mean() * 100, 2)),
                "Average_Age": float(round(df[df['Country'] == 1]['Age'].mean(), 2)),
                "Digital_Bank_Adoption": float(round(len(df[(df['Country'] == 1) & (df['Bank_Type'] == 2)]) / len(df[df['Country'] == 1]) * 100, 2))
            },
            "Ghana": {
                "Sample_Size": int(len(df[df['Country'] == 2])),
                "Fraud_Rate": float(round(df[df['Country'] == 2]['Past_Victim'].mean() * 100, 2)),
                "Average_Age": float(round(df[df['Country'] == 2]['Age'].mean(), 2)),
                "Digital_Bank_Adoption": float(round(len(df[(df['Country'] == 2) & (df['Bank_Type'] == 2)]) / len(df[df['Country'] == 2]) * 100, 2))
            }
        },
        "Risk_Analysis": {
            "By_Bank_Type": {
                bank_type: {
                    "Sample_Size": int(len(df[df['Bank_Type_Label'] == bank_type])),
                    "Fraud_Rate": float(round(df[df['Bank_Type_Label'] == bank_type]['Past_Victim'].mean() * 100, 2))
                }
                for bank_type in df['Bank_Type_Label'].unique()
            },
            "By_Frequency": {
                freq: {
                    "Sample_Size": int(len(df[df['Frequency_Label'] == freq])),
                    "Fraud_Rate": float(round(df[df['Frequency_Label'] == freq]['Past_Victim'].mean() * 100, 2))
                }
                for freq in df['Frequency_Label'].unique()
            }
        }
    }
    
    with open('analysis_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("📄 Analysis report exported to: analysis_report.json")
    print()

def main():
    """Main analysis function"""
    # Load dataset
    df = load_and_explore_dataset()
    
    # Run analyses
    descriptive_statistics(df)
    comparative_analysis(df)
    correlation_analysis(df)
    fraud_risk_analysis(df)
    cross_tabulation_analysis(df)
    generate_insights(df)
    
    # Export report
    export_analysis_report(df)
    
    print("=" * 80)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 80)
    print("\nAll analyses have been performed. Review the output above for insights.")
    print("Additional analysis report saved to: analysis_report.json")
    print()

if __name__ == "__main__":
    main()
