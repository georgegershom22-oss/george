#!/usr/bin/env python3
"""
Dataset Visualization Script
Creates key visualizations to demonstrate dataset patterns
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
plt.style.use('default')
sns.set_palette("husl")

def load_dataset():
    """Load the generated dataset"""
    return pd.read_csv('/workspace/dataset/banking_fraud_dataset.csv')

def create_visualizations(df):
    """Create comprehensive visualizations"""
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 16))
    
    # 1. Fraud rate by country and bank type
    ax1 = plt.subplot(3, 3, 1)
    fraud_by_country_bank = df.groupby(['Country_Name', 'Bank_Type_Name'])['Past_Victim'].mean().unstack()
    fraud_by_country_bank.plot(kind='bar', ax=ax1, width=0.8)
    ax1.set_title('Fraud Rate by Country and Bank Type', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Fraud Rate')
    ax1.set_xlabel('Country')
    ax1.legend(title='Bank Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Age distribution by fraud victim status
    ax2 = plt.subplot(3, 3, 2)
    df.boxplot(column='Age', by='Past_Victim', ax=ax2)
    ax2.set_title('Age Distribution by Fraud Victim Status', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Fraud Victim (0=No, 1=Yes)')
    ax2.set_ylabel('Age')
    
    # 3. Fraud awareness vs concern scatter plot
    ax3 = plt.subplot(3, 3, 3)
    colors = ['red' if x == 1 else 'blue' for x in df['Past_Victim']]
    ax3.scatter(df['Fraud_Awareness'], df['Fraud_Concern'], c=colors, alpha=0.6)
    ax3.set_title('Fraud Awareness vs Concern\n(Red=Victim, Blue=Non-Victim)', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Fraud Awareness')
    ax3.set_ylabel('Fraud Concern')
    
    # 4. Bank type distribution
    ax4 = plt.subplot(3, 3, 4)
    bank_counts = df['Bank_Type_Name'].value_counts()
    ax4.pie(bank_counts.values, labels=bank_counts.index, autopct='%1.1f%%', startangle=90)
    ax4.set_title('Bank Type Distribution', fontsize=12, fontweight='bold')
    
    # 5. Education level by fraud rate
    ax5 = plt.subplot(3, 3, 5)
    edu_fraud = df.groupby('Education_Level')['Past_Victim'].mean().sort_values(ascending=False)
    edu_fraud.plot(kind='bar', ax=ax5, color='skyblue')
    ax5.set_title('Fraud Rate by Education Level', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Fraud Rate')
    ax5.set_xlabel('Education Level')
    ax5.tick_params(axis='x', rotation=45)
    
    # 6. Technology adoption by age group
    ax6 = plt.subplot(3, 3, 6)
    tech_by_age = df.groupby('Age_Group')['Tech_Adoption'].mean()
    tech_by_age.plot(kind='bar', ax=ax6, color='lightgreen')
    ax6.set_title('Technology Adoption by Age Group', fontsize=12, fontweight='bold')
    ax6.set_ylabel('Tech Adoption Score')
    ax6.set_xlabel('Age Group')
    ax6.tick_params(axis='x', rotation=45)
    
    # 7. Trust in banking systems
    ax7 = plt.subplot(3, 3, 7)
    trust_data = df[['Trust_Traditional_Banking', 'Trust_Digital_Banking']].mean()
    trust_data.plot(kind='bar', ax=ax7, color=['darkblue', 'orange'])
    ax7.set_title('Average Trust in Banking Systems', fontsize=12, fontweight='bold')
    ax7.set_ylabel('Trust Score')
    ax7.set_xlabel('Banking Type')
    ax7.tick_params(axis='x', rotation=45)
    
    # 8. Income level distribution
    ax8 = plt.subplot(3, 3, 8)
    income_counts = df['Income_Level'].value_counts().sort_index()
    income_labels = ['Very Low', 'Low', 'Below Avg', 'Average', 'Above Avg', 'High']
    ax8.bar(range(len(income_counts)), income_counts.values, color='lightcoral')
    ax8.set_title('Income Level Distribution', fontsize=12, fontweight='bold')
    ax8.set_ylabel('Count')
    ax8.set_xlabel('Income Level')
    ax8.set_xticks(range(len(income_labels)))
    ax8.set_xticklabels(income_labels, rotation=45)
    
    # 9. Correlation heatmap
    ax9 = plt.subplot(3, 3, 9)
    numeric_vars = ['Age', 'Education', 'Income_Level', 'Past_Victim', 
                   'Fraud_Awareness', 'Fraud_Concern', 'Security_Knowledge', 
                   'Tech_Adoption', 'Trust_Traditional_Banking', 'Trust_Digital_Banking']
    corr_matrix = df[numeric_vars].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                square=True, ax=ax9, cbar_kws={'shrink': 0.8})
    ax9.set_title('Correlation Heatmap', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/workspace/dataset/dataset_visualizations.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Visualizations saved as 'dataset_visualizations.png'")

def create_summary_table(df):
    """Create a summary table of key statistics"""
    
    # Key statistics by country
    summary_stats = []
    
    for country in df['Country_Name'].unique():
        country_data = df[df['Country_Name'] == country]
        
        stats = {
            'Country': country,
            'Sample_Size': len(country_data),
            'Fraud_Rate': f"{country_data['Past_Victim'].mean():.1%}",
            'Avg_Age': f"{country_data['Age'].mean():.1f}",
            'Digital_Bank_%': f"{(country_data['Bank_Type'] == 2).mean():.1%}",
            'High_Education_%': f"{(country_data['Education'] >= 5).mean():.1%}",
            'Avg_Fraud_Awareness': f"{country_data['Fraud_Awareness'].mean():.2f}",
            'Avg_Security_Knowledge': f"{country_data['Security_Knowledge'].mean():.2f}",
            'Avg_Trust_Digital': f"{country_data['Trust_Digital_Banking'].mean():.2f}",
            'Avg_Trust_Traditional': f"{country_data['Trust_Traditional_Banking'].mean():.2f}"
        }
        summary_stats.append(stats)
    
    summary_df = pd.DataFrame(summary_stats)
    
    # Save summary table
    summary_df.to_csv('/workspace/dataset/country_summary_stats.csv', index=False)
    print("\nCountry Summary Statistics:")
    print(summary_df.to_string(index=False))
    
    return summary_df

def main():
    """Main visualization function"""
    print("Creating dataset visualizations...")
    
    # Load dataset
    df = load_dataset()
    
    # Create visualizations
    create_visualizations(df)
    
    # Create summary table
    create_summary_table(df)
    
    print("\nVisualization complete!")
    print("Files created:")
    print("  - dataset_visualizations.png")
    print("  - country_summary_stats.csv")

if __name__ == "__main__":
    main()