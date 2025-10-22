"""
Data Validation and Analysis Script for Nigerian SME Innovation Dataset
=======================================================================
This script performs data quality checks and generates detailed statistical analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def load_data(filepath='/workspace/nigerian_sme_innovation_dataset/data/nigerian_sme_innovation_data.csv'):
    """Load the dataset"""
    print("Loading dataset...")
    df = pd.read_csv(filepath)
    print(f"✓ Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    return df

def data_quality_checks(df):
    """Perform comprehensive data quality checks"""
    print("\n" + "="*60)
    print("DATA QUALITY CHECKS")
    print("="*60)
    
    # Missing values
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("✓ No missing values found")
    else:
        print(f"⚠ Found {missing.sum()} missing values:")
        print(missing[missing > 0])
    
    # Duplicates
    duplicates = df.duplicated().sum()
    if duplicates == 0:
        print("✓ No duplicate rows found")
    else:
        print(f"⚠ Found {duplicates} duplicate rows")
    
    # Data types
    print("\n✓ Data Types Summary:")
    print(f"  - Numeric columns: {df.select_dtypes(include=['float64', 'int64']).shape[1]}")
    print(f"  - Text columns: {df.select_dtypes(include=['object']).shape[1]}")
    print(f"  - Date columns: {df.select_dtypes(include=['datetime64']).shape[1]}")
    
    # Range checks for Likert scales
    likert_cols = [col for col in df.columns if any(x in col for x in 
                   ['digital_tools_', 'advanced_tech_', 'process_', 'product_', 
                    'business_model_', 'driver_', 'constraint_', 'performance_', 'growth_'])]
    
    out_of_range = 0
    for col in likert_cols:
        if col in df.columns and df[col].dtype in ['float64', 'int64']:
            if (df[col] < 1).any() or (df[col] > 5).any():
                out_of_range += 1
                print(f"⚠ {col}: Values outside 1-5 range")
    
    if out_of_range == 0:
        print(f"✓ All {len(likert_cols)} Likert scale variables within valid range (1-5)")
    
    # Logical consistency checks
    print("\n✓ Logical Consistency Checks:")
    
    # Check if firms with no employees have turnover
    no_emp_with_turnover = df[(df['num_employees'] == 0) & (df['annual_turnover_million_naira'] > 0)]
    if len(no_emp_with_turnover) == 0:
        print("  - ✓ Employee-turnover consistency valid")
    else:
        print(f"  - ⚠ {len(no_emp_with_turnover)} firms with 0 employees but positive turnover")
    
    # Check age consistency
    age_issue = df[df['owner_age'] < df['firm_age_years'] + 18]
    if len(age_issue) == 0:
        print("  - ✓ Owner age consistency valid")
    else:
        print(f"  - ⚠ {len(age_issue)} owners younger than expected given firm age")
    
    return True

def descriptive_statistics(df):
    """Generate descriptive statistics"""
    print("\n" + "="*60)
    print("DESCRIPTIVE STATISTICS")
    print("="*60)
    
    # Firmographics
    print("\n1. FIRMOGRAPHICS")
    print("-"*40)
    print(f"Average firm age: {df['firm_age_years'].mean():.1f} years (SD: {df['firm_age_years'].std():.1f})")
    print(f"Average employees: {df['num_employees'].mean():.1f} (SD: {df['num_employees'].std():.1f})")
    print(f"Average turnover: ₦{df['annual_turnover_million_naira'].mean():.1f}M (SD: {df['annual_turnover_million_naira'].std():.1f})")
    print(f"Average owner age: {df['owner_age'].mean():.1f} years")
    print(f"Digital literacy: {df['digital_literacy_score'].mean():.1f}/10")
    
    # Gender distribution
    print(f"\nGender Distribution:")
    for gender, count in df['owner_gender'].value_counts().items():
        print(f"  - {gender}: {count} ({count/len(df)*100:.1f}%)")
    
    # Education distribution
    print(f"\nEducation Levels:")
    for edu, count in df['owner_education_level'].value_counts().items():
        print(f"  - {edu}: {count} ({count/len(df)*100:.1f}%)")

def correlation_analysis(df):
    """Analyze correlations between key variables"""
    print("\n" + "="*60)
    print("CORRELATION ANALYSIS")
    print("="*60)
    
    # Key relationships
    key_vars = [
        'innovation_overall_score',
        'constraint_overall_score', 
        'performance_subjective_score',
        'objective_turnover_growth_percent',
        'digital_literacy_score',
        'num_employees',
        'firm_age_years'
    ]
    
    corr_matrix = df[key_vars].corr()
    
    print("\nKey Correlations with Performance:")
    perf_corr = corr_matrix['performance_subjective_score'].sort_values(ascending=False)
    for var, corr in perf_corr.items():
        if var != 'performance_subjective_score':
            print(f"  - {var}: {corr:.3f}")
    
    print("\nKey Correlations with Innovation:")
    inn_corr = corr_matrix['innovation_overall_score'].sort_values(ascending=False)
    for var, corr in inn_corr.items():
        if var != 'innovation_overall_score':
            print(f"  - {var}: {corr:.3f}")
    
    # Statistical significance tests
    print("\n✓ Statistical Significance Tests:")
    
    # Test: Innovation vs Performance
    r, p = stats.pearsonr(df['innovation_overall_score'], df['performance_subjective_score'])
    print(f"  - Innovation → Performance: r={r:.3f}, p={'<0.001' if p < 0.001 else f'{p:.3f}'}")
    
    # Test: Constraints vs Performance
    r, p = stats.pearsonr(df['constraint_overall_score'], df['performance_subjective_score'])
    print(f"  - Constraints → Performance: r={r:.3f}, p={'<0.001' if p < 0.001 else f'{p:.3f}'}")
    
    return corr_matrix

def segment_analysis(df):
    """Analyze different segments"""
    print("\n" + "="*60)
    print("SEGMENT ANALYSIS")
    print("="*60)
    
    # By Zone
    print("\n1. PERFORMANCE BY GEOPOLITICAL ZONE")
    print("-"*40)
    zone_perf = df.groupby('geo_political_zone').agg({
        'performance_subjective_score': 'mean',
        'innovation_overall_score': 'mean',
        'constraint_overall_score': 'mean',
        'objective_turnover_growth_percent': 'mean'
    }).round(2)
    
    zone_perf = zone_perf.sort_values('performance_subjective_score', ascending=False)
    print(zone_perf.to_string())
    
    # By Industry
    print("\n2. PERFORMANCE BY INDUSTRY")
    print("-"*40)
    ind_perf = df.groupby('industry_sector').agg({
        'performance_subjective_score': 'mean',
        'innovation_overall_score': 'mean',
        'digital_literacy_score': 'mean',
        'objective_profit_margin_percent': 'mean'
    }).round(2)
    
    ind_perf = ind_perf.sort_values('performance_subjective_score', ascending=False)
    print(ind_perf.head(10).to_string())
    
    # By Firm Size
    print("\n3. PERFORMANCE BY FIRM SIZE")
    print("-"*40)
    
    # Create size categories
    df['size_category'] = pd.cut(df['num_employees'], 
                                 bins=[0, 10, 50, 250],
                                 labels=['Micro (1-9)', 'Small (10-49)', 'Medium (50-250)'])
    
    size_perf = df.groupby('size_category').agg({
        'performance_subjective_score': 'mean',
        'innovation_overall_score': 'mean',
        'constraint_financial_score': 'mean',
        'objective_employee_growth_percent': 'mean'
    }).round(2)
    
    print(size_perf.to_string())

def innovation_adoption_patterns(df):
    """Analyze innovation adoption patterns"""
    print("\n" + "="*60)
    print("INNOVATION ADOPTION PATTERNS")
    print("="*60)
    
    # Technology adoption rates
    print("\n1. TECHNOLOGY ADOPTION RATES (Mean Scores)")
    print("-"*40)
    
    tech_cols = [col for col in df.columns if 'digital_tools_' in col]
    tech_adoption = df[tech_cols].mean().sort_values(ascending=False)
    
    for col, score in tech_adoption.items():
        clean_name = col.replace('digital_tools_', '').replace('_', ' ').title()
        print(f"  - {clean_name}: {score:.2f}/5.0")
    
    # Advanced tech adoption
    print("\n2. ADVANCED TECHNOLOGY ADOPTION (Mean Scores)")
    print("-"*40)
    
    adv_cols = [col for col in df.columns if 'advanced_tech_' in col]
    adv_adoption = df[adv_cols].mean().sort_values(ascending=False)
    
    for col, score in adv_adoption.items():
        clean_name = col.replace('advanced_tech_', '').replace('_', ' ').upper()
        print(f"  - {clean_name}: {score:.2f}/5.0")
    
    # Innovation types comparison
    print("\n3. INNOVATION TYPES COMPARISON")
    print("-"*40)
    
    innovation_types = {
        'Technology': df['innovation_technology_score'].mean(),
        'Process': df['innovation_process_score'].mean(),
        'Product': df['innovation_product_score'].mean(),
        'Business Model': df['innovation_business_model_score'].mean()
    }
    
    for inn_type, score in sorted(innovation_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {inn_type}: {score:.2f}/5.0")

def constraint_analysis(df):
    """Analyze constraints faced by SMEs"""
    print("\n" + "="*60)
    print("CONSTRAINT ANALYSIS")
    print("="*60)
    
    # Top individual constraints
    print("\n1. TOP 10 CONSTRAINTS (Highest Scores)")
    print("-"*40)
    
    constraint_cols = [col for col in df.columns if 'constraint_' in col and 
                      col not in ['constraint_overall_score', 'constraint_financial_score',
                                 'constraint_human_capital_score', 'constraint_infrastructure_score',
                                 'constraint_regulatory_score', 'constraint_market_score']]
    
    constraints = df[constraint_cols].mean().sort_values(ascending=False).head(10)
    
    for i, (col, score) in enumerate(constraints.items(), 1):
        clean_name = col.replace('constraint_', '').replace('_', ' ').title()
        print(f"  {i}. {clean_name}: {score:.2f}/5.0")
    
    # Constraint categories
    print("\n2. CONSTRAINT CATEGORIES RANKING")
    print("-"*40)
    
    constraint_cats = {
        'Market': df['constraint_market_score'].mean(),
        'Infrastructure': df['constraint_infrastructure_score'].mean(),
        'Human Capital': df['constraint_human_capital_score'].mean(),
        'Regulatory': df['constraint_regulatory_score'].mean(),
        'Financial': df['constraint_financial_score'].mean()
    }
    
    for cat, score in sorted(constraint_cats.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {cat}: {score:.2f}/5.0")

def generate_visualizations(df):
    """Generate key visualizations"""
    print("\n" + "="*60)
    print("GENERATING VISUALIZATIONS")
    print("="*60)
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Nigerian SME Innovation Dataset - Key Insights', fontsize=16, y=1.02)
    
    # 1. Innovation vs Performance
    ax = axes[0, 0]
    ax.scatter(df['innovation_overall_score'], df['performance_subjective_score'], 
              alpha=0.5, s=20)
    ax.set_xlabel('Innovation Score')
    ax.set_ylabel('Performance Score')
    ax.set_title('Innovation vs Performance')
    z = np.polyfit(df['innovation_overall_score'], df['performance_subjective_score'], 1)
    p = np.poly1d(z)
    ax.plot(df['innovation_overall_score'].sort_values(), 
           p(df['innovation_overall_score'].sort_values()), "r-", alpha=0.8)
    
    # 2. Performance by Zone
    ax = axes[0, 1]
    zone_perf = df.groupby('geo_political_zone')['performance_subjective_score'].mean().sort_values()
    zone_perf.plot(kind='barh', ax=ax, color='skyblue')
    ax.set_xlabel('Performance Score')
    ax.set_title('Performance by Geopolitical Zone')
    
    # 3. Industry Distribution
    ax = axes[0, 2]
    industry_counts = df['industry_sector'].value_counts().head(6)
    ax.pie(industry_counts.values, labels=industry_counts.index, autopct='%1.1f%%')
    ax.set_title('Industry Distribution (Top 6)')
    
    # 4. Constraint Heatmap
    ax = axes[1, 0]
    constraint_by_zone = df.groupby('geo_political_zone')[
        ['constraint_financial_score', 'constraint_human_capital_score',
         'constraint_infrastructure_score', 'constraint_market_score']
    ].mean()
    
    im = ax.imshow(constraint_by_zone.T.values, cmap='YlOrRd', aspect='auto')
    ax.set_xticks(range(len(constraint_by_zone.index)))
    ax.set_xticklabels(constraint_by_zone.index, rotation=45, ha='right')
    ax.set_yticks(range(len(constraint_by_zone.columns)))
    ax.set_yticklabels(['Financial', 'Human Capital', 'Infrastructure', 'Market'])
    ax.set_title('Constraints by Zone (Heatmap)')
    plt.colorbar(im, ax=ax)
    
    # 5. Digital Adoption Distribution
    ax = axes[1, 1]
    ax.hist(df['digital_literacy_score'], bins=20, edgecolor='black', alpha=0.7)
    ax.set_xlabel('Digital Literacy Score')
    ax.set_ylabel('Frequency')
    ax.set_title('Digital Literacy Distribution')
    ax.axvline(df['digital_literacy_score'].mean(), color='red', 
              linestyle='--', label=f'Mean: {df["digital_literacy_score"].mean():.1f}')
    ax.legend()
    
    # 6. Growth Metrics
    ax = axes[1, 2]
    growth_metrics = {
        'Turnover': df['objective_turnover_growth_percent'].mean(),
        'Employees': df['objective_employee_growth_percent'].mean(),
        'Profit Margin': df['objective_profit_margin_percent'].mean()
    }
    ax.bar(growth_metrics.keys(), growth_metrics.values(), color=['green', 'blue', 'orange'])
    ax.set_ylabel('Percentage (%)')
    ax.set_title('Average Growth Metrics')
    
    plt.tight_layout()
    
    # Save figure
    output_path = '/workspace/nigerian_sme_innovation_dataset/data/analysis_visualizations.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Visualizations saved to: {output_path}")
    
    plt.show()

def export_analysis_report(df, output_path='/workspace/nigerian_sme_innovation_dataset/data/detailed_analysis_report.txt'):
    """Export detailed analysis report"""
    import sys
    from io import StringIO
    
    # Capture all output
    old_stdout = sys.stdout
    sys.stdout = buffer = StringIO()
    
    print("="*70)
    print("NIGERIAN SME INNOVATION DATASET - DETAILED ANALYSIS REPORT")
    print("="*70)
    print(f"\nGenerated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Dataset: {df.shape[0]} SMEs, {df.shape[1]} variables")
    
    # Run all analyses
    data_quality_checks(df)
    descriptive_statistics(df)
    correlation_analysis(df)
    segment_analysis(df)
    innovation_adoption_patterns(df)
    constraint_analysis(df)
    
    # Get the output
    report_content = buffer.getvalue()
    sys.stdout = old_stdout
    
    # Save to file
    with open(output_path, 'w') as f:
        f.write(report_content)
    
    print(f"\n✓ Detailed analysis report saved to: {output_path}")
    
    return report_content

def main():
    """Main execution function"""
    print("\n" + "="*70)
    print("NIGERIAN SME INNOVATION DATASET - VALIDATION & ANALYSIS")
    print("="*70)
    
    # Load data
    df = load_data()
    
    # Run analyses
    data_quality_checks(df)
    descriptive_statistics(df)
    corr_matrix = correlation_analysis(df)
    segment_analysis(df)
    innovation_adoption_patterns(df)
    constraint_analysis(df)
    
    # Generate visualizations
    generate_visualizations(df)
    
    # Export report
    export_analysis_report(df)
    
    print("\n" + "="*70)
    print("✓ ANALYSIS COMPLETE!")
    print("="*70)
    print("\nOutputs generated:")
    print("  1. analysis_visualizations.png - Key charts and graphs")
    print("  2. detailed_analysis_report.txt - Comprehensive text report")
    print("  3. Console output - Summary of all findings")
    
    return df, corr_matrix

if __name__ == "__main__":
    df, corr_matrix = main()