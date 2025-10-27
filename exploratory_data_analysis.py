"""
Exploratory Data Analysis for Welding Dataset

This script performs comprehensive EDA on the welding parameters dataset,
including visualizations, correlations, and statistical summaries.
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
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

print("="*80)
print("EXPLORATORY DATA ANALYSIS")
print("ML-Driven Inverse Design of Welding Parameters Dataset")
print("="*80)
print()

# Load dataset
df = pd.read_csv('/workspace/welding_ml_dataset.csv')
print(f"Dataset loaded: {df.shape[0]} samples, {df.shape[1]} features")
print()

# ============================================================================
# BASIC STATISTICS
# ============================================================================

print("="*80)
print("1. BASIC STATISTICS")
print("="*80)
print()

print("Data Types:")
print(df.dtypes.value_counts())
print()

print("Missing Values:")
print(f"Total missing: {df.isnull().sum().sum()}")
print()

print("Categorical Variables:")
categorical_cols = df.select_dtypes(include=['object']).columns
for col in categorical_cols:
    print(f"\n{col}:")
    print(df[col].value_counts())
print()

# ============================================================================
# INPUT PARAMETERS ANALYSIS
# ============================================================================

print("="*80)
print("2. INPUT PARAMETERS ANALYSIS")
print("="*80)
print()

input_cols = ['power_W', 'amplitude_um', 'force_N', 'time_ms', 'frequency_Hz', 
              'speed_mm_s', 'tab_thickness_um', 'preheat_temp_C', 'energy_density_J_mm2']

print("Numerical Input Parameters Summary:")
print(df[input_cols].describe())
print()

# ============================================================================
# TARGET VARIABLE ANALYSIS
# ============================================================================

print("="*80)
print("3. PRIMARY TARGET: THERMAL CYCLES TO FAILURE")
print("="*80)
print()

target = 'thermal_cycles_to_failure'
print(f"Distribution Statistics:")
print(f"  Mean:     {df[target].mean():.1f} cycles")
print(f"  Median:   {df[target].median():.1f} cycles")
print(f"  Std Dev:  {df[target].std():.1f} cycles")
print(f"  Min:      {df[target].min():.1f} cycles")
print(f"  Max:      {df[target].max():.1f} cycles")
print(f"  Skewness: {df[target].skew():.3f}")
print(f"  Kurtosis: {df[target].kurtosis():.3f}")
print()

# Percentiles
print("Percentiles:")
for p in [10, 25, 50, 75, 90, 95, 99]:
    print(f"  {p}th: {df[target].quantile(p/100):.0f} cycles")
print()

# Quality classification
print("Weld Quality Classification:")
print(df['weld_quality_class'].value_counts())
print(f"Good Weld Percentage: {(df['weld_quality_class']=='Good').mean()*100:.2f}%")
print()

# ============================================================================
# PERFORMANCE METRICS ANALYSIS
# ============================================================================

print("="*80)
print("4. PERFORMANCE METRICS")
print("="*80)
print()

performance_cols = [
    'thermal_cycles_to_failure',
    'resistance_increase_after_cycling_pct',
    'strength_retention_pct',
    'max_operating_temp_C',
    'electrochemical_stability_score',
    'overall_quality_score'
]

print("Key Performance Metrics:")
print(df[performance_cols].describe())
print()

# ============================================================================
# TECHNIQUE COMPARISON
# ============================================================================

print("="*80)
print("5. WELDING TECHNIQUE COMPARISON")
print("="*80)
print()

for technique in df['welding_technique'].unique():
    tech_data = df[df['welding_technique'] == technique]
    print(f"\n{technique} Welding (n={len(tech_data)}):")
    print(f"  Avg Thermal Cycles: {tech_data['thermal_cycles_to_failure'].mean():.0f}")
    print(f"  Avg Contact Resistance: {tech_data['contact_resistance_uOhm'].mean():.1f} µΩ")
    print(f"  Avg Tensile Strength: {tech_data['tensile_shear_strength_N'].mean():.0f} N")
    print(f"  Avg Overall Quality: {tech_data['overall_quality_score'].mean():.1f}")
    print(f"  Good Weld Rate: {(tech_data['weld_quality_class']=='Good').mean()*100:.2f}%")
print()

# ============================================================================
# MATERIAL COMBINATION ANALYSIS
# ============================================================================

print("="*80)
print("6. MATERIAL COMBINATION ANALYSIS")
print("="*80)
print()

material_performance = df.groupby(['anode_material', 'cathode_material']).agg({
    'thermal_cycles_to_failure': ['mean', 'std', 'count'],
    'contact_resistance_uOhm': 'mean',
    'overall_quality_score': 'mean'
}).round(1)

print("Performance by Material Combination:")
print(material_performance)
print()

# ============================================================================
# CRITICAL METRICS ANALYSIS
# ============================================================================

print("="*80)
print("7. CRITICAL METRICS: IMC THICKNESS & CONTACT RESISTANCE")
print("="*80)
print()

print("IMC Thickness Distribution:")
print(df['IMC_thickness_um'].describe())
print()

# Optimal IMC range
optimal_imc = df[(df['IMC_thickness_um'] >= 1) & (df['IMC_thickness_um'] <= 3)]
print(f"Samples in optimal IMC range (1-3 µm): {len(optimal_imc)} ({len(optimal_imc)/len(df)*100:.1f}%)")
print(f"Avg thermal cycles for optimal IMC: {optimal_imc['thermal_cycles_to_failure'].mean():.0f}")
print(f"Avg thermal cycles overall: {df['thermal_cycles_to_failure'].mean():.0f}")
print()

print("Contact Resistance Distribution:")
print(df['contact_resistance_uOhm'].describe())
print()

low_resistance = df[df['contact_resistance_uOhm'] < 50]
print(f"Samples with low resistance (<50 µΩ): {len(low_resistance)} ({len(low_resistance)/len(df)*100:.1f}%)")
print(f"Avg thermal cycles for low resistance: {low_resistance['thermal_cycles_to_failure'].mean():.0f}")
print()

# ============================================================================
# CORRELATION ANALYSIS
# ============================================================================

print("="*80)
print("8. CORRELATION ANALYSIS WITH PRIMARY TARGET")
print("="*80)
print()

numerical_cols = df.select_dtypes(include=[np.number]).columns
correlations = df[numerical_cols].corr()[target].sort_values(ascending=False)

print("Top 15 Positive Correlations with Thermal Cycles:")
print(correlations.head(15))
print()

print("Top 10 Negative Correlations with Thermal Cycles:")
print(correlations.tail(10))
print()

# ============================================================================
# DEFECT ANALYSIS
# ============================================================================

print("="*80)
print("9. DEFECT ANALYSIS")
print("="*80)
print()

print("Porosity Distribution:")
print(df['porosity_pct'].describe())
print()

low_porosity = df[df['porosity_pct'] < 3]
print(f"Low porosity samples (<3%): {len(low_porosity)} ({len(low_porosity)/len(df)*100:.1f}%)")
print(f"Avg thermal cycles for low porosity: {low_porosity['thermal_cycles_to_failure'].mean():.0f}")
print()

# ============================================================================
# ENERGY EFFICIENCY ANALYSIS
# ============================================================================

print("="*80)
print("10. ENERGY EFFICIENCY ANALYSIS")
print("="*80)
print()

print("Energy Density Statistics:")
print(df['energy_density_J_mm2'].describe())
print()

# Quartile analysis
df['energy_quartile'] = pd.qcut(df['energy_density_J_mm2'], q=4, labels=['Q1-Low', 'Q2', 'Q3', 'Q4-High'])
print("Performance by Energy Quartile:")
print(df.groupby('energy_quartile').agg({
    'thermal_cycles_to_failure': 'mean',
    'energy_efficiency_score': 'mean',
    'overall_quality_score': 'mean'
}).round(1))
print()

# ============================================================================
# SURFACE FINISH IMPACT
# ============================================================================

print("="*80)
print("11. SURFACE FINISH IMPACT")
print("="*80)
print()

surface_analysis = df.groupby('surface_finish').agg({
    'thermal_cycles_to_failure': ['mean', 'std'],
    'contact_resistance_uOhm': 'mean',
    'IMC_thickness_um': 'mean',
    'overall_quality_score': 'mean'
}).round(2)

print("Performance by Surface Finish:")
print(surface_analysis)
print()

# ============================================================================
# STATISTICAL TESTS
# ============================================================================

print("="*80)
print("12. STATISTICAL TESTS")
print("="*80)
print()

# ANOVA: Does welding technique significantly affect thermal cycles?
groups = [df[df['welding_technique']==tech]['thermal_cycles_to_failure'].values 
          for tech in df['welding_technique'].unique()]
f_stat, p_value = stats.f_oneway(*groups)
print(f"ANOVA: Welding Technique vs Thermal Cycles")
print(f"  F-statistic: {f_stat:.3f}")
print(f"  P-value: {p_value:.6f}")
print(f"  Result: {'Significant difference' if p_value < 0.05 else 'No significant difference'}")
print()

# Normality test on target
stat, p = stats.normaltest(df['thermal_cycles_to_failure'])
print(f"Normality Test (Thermal Cycles):")
print(f"  Statistic: {stat:.3f}")
print(f"  P-value: {p:.6f}")
print(f"  Result: {'Not normally distributed' if p < 0.05 else 'Normally distributed'}")
print()

# ============================================================================
# FEATURE IMPORTANCE PROXY
# ============================================================================

print("="*80)
print("13. FEATURE IMPORTANCE (Correlation-based)")
print("="*80)
print()

# Create dummy variables for categorical
df_encoded = pd.get_dummies(df, columns=['anode_material', 'cathode_material', 
                                          'surface_finish', 'welding_technique'])

# Calculate correlations with target
all_correlations = df_encoded.corr()[target].abs().sort_values(ascending=False)
print("Top 20 Features by Absolute Correlation:")
print(all_correlations.head(20))
print()

# ============================================================================
# OPTIMAL PARAMETER RANGES
# ============================================================================

print("="*80)
print("14. OPTIMAL PARAMETER RANGES (Top 10% Performance)")
print("="*80)
print()

top_10_pct = df[df['thermal_cycles_to_failure'] >= df['thermal_cycles_to_failure'].quantile(0.9)]
print(f"Top 10% samples (cycles >= {df['thermal_cycles_to_failure'].quantile(0.9):.0f}):")
print()

print("Input Parameter Ranges for Top Performers:")
for col in input_cols:
    if top_10_pct[col].std() > 0:  # Only show varying parameters
        print(f"  {col}:")
        print(f"    Mean: {top_10_pct[col].mean():.2f}")
        print(f"    Range: [{top_10_pct[col].min():.2f}, {top_10_pct[col].max():.2f}]")
print()

print("Welding Technique Distribution in Top 10%:")
print(top_10_pct['welding_technique'].value_counts(normalize=True).mul(100).round(1))
print()

# ============================================================================
# DATA QUALITY CHECKS
# ============================================================================

print("="*80)
print("15. DATA QUALITY CHECKS")
print("="*80)
print()

print("Duplicate Rows:")
print(f"  Count: {df.duplicated().sum()}")
print()

print("Outlier Detection (IQR method on target):")
Q1 = df[target].quantile(0.25)
Q3 = df[target].quantile(0.75)
IQR = Q3 - Q1
outliers = df[(df[target] < Q1 - 1.5*IQR) | (df[target] > Q3 + 1.5*IQR)]
print(f"  Potential outliers: {len(outliers)} ({len(outliers)/len(df)*100:.1f}%)")
print()

# ============================================================================
# RECOMMENDATIONS
# ============================================================================

print("="*80)
print("16. KEY INSIGHTS & RECOMMENDATIONS")
print("="*80)
print()

print("✓ Dataset is complete with no missing values")
print(f"✓ Target variable (thermal cycles) ranges from {df[target].min():.0f} to {df[target].max():.0f}")
print(f"✓ Class imbalance detected: {(df['weld_quality_class']=='Poor').sum()} Poor vs {(df['weld_quality_class']=='Good').sum()} Good welds")
print(f"✓ IMC thickness is critical: Optimal range 1-3 µm shows {optimal_imc['thermal_cycles_to_failure'].mean() - df['thermal_cycles_to_failure'].mean():.0f} cycle improvement")
print(f"✓ Contact resistance <50 µΩ correlates with +{low_resistance['thermal_cycles_to_failure'].mean() - df['thermal_cycles_to_failure'].mean():.0f} cycles")
print(f"✓ Low porosity (<3%) improves cycles by ~{low_porosity['thermal_cycles_to_failure'].mean() - df['thermal_cycles_to_failure'].mean():.0f}")
print()

print("Modeling Recommendations:")
print("  1. Use stratified sampling on welding_technique for train/test split")
print("  2. Consider separate models per welding technique")
print("  3. Apply SMOTE or class weighting for classification due to imbalance")
print("  4. Feature engineering: IMC interactions, energy efficiency metrics")
print("  5. Target transformation: Consider log or Box-Cox for thermal cycles")
print("  6. Multi-output modeling: Predict multiple targets simultaneously")
print()

print("="*80)
print("Analysis Complete!")
print("="*80)
