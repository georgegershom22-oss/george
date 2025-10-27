"""
Dataset Visualization Script
Generates comprehensive plots to understand the welding dataset
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

print("="*80)
print("WELDING DATASET VISUALIZATION")
print("="*80)

# Load data
print("\nLoading dataset...")
df = pd.read_csv('welding_dataset_full.csv')
print(f"✓ Loaded {len(df)} samples")

# Create output directory for plots
import os
if not os.path.exists('plots'):
    os.makedirs('plots')
print("✓ Created 'plots' directory for saving figures")

# ===== 1. OVERALL STATISTICS =====
print("\n[1] Generating summary statistics...")

fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Quality score distribution
axes[0, 0].hist(df['quality_score'], bins=50, edgecolor='black', alpha=0.7)
axes[0, 0].axvline(df['quality_score'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {df["quality_score"].mean():.3f}')
axes[0, 0].set_xlabel('Quality Score', fontsize=12)
axes[0, 0].set_ylabel('Frequency', fontsize=12)
axes[0, 0].set_title('Quality Score Distribution', fontsize=14, fontweight='bold')
axes[0, 0].legend()

# Quality class distribution
quality_counts = df['quality_class'].value_counts()
axes[0, 1].bar(quality_counts.index, quality_counts.values, edgecolor='black', alpha=0.7)
axes[0, 1].set_xlabel('Quality Class', fontsize=12)
axes[0, 1].set_ylabel('Count', fontsize=12)
axes[0, 1].set_title('Quality Class Distribution', fontsize=14, fontweight='bold')
for i, v in enumerate(quality_counts.values):
    axes[0, 1].text(i, v + 50, str(v), ha='center', fontweight='bold')

# Welding technique distribution
tech_counts = df['welding_technique'].value_counts()
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
axes[1, 0].bar(tech_counts.index, tech_counts.values, color=colors, edgecolor='black', alpha=0.7)
axes[1, 0].set_xlabel('Welding Technique', fontsize=12)
axes[1, 0].set_ylabel('Count', fontsize=12)
axes[1, 0].set_title('Welding Technique Distribution', fontsize=14, fontweight='bold')
for i, v in enumerate(tech_counts.values):
    axes[1, 0].text(i, v + 20, str(v), ha='center', fontweight='bold')

# Pass/Fail distribution
pass_counts = df['pass_fail'].value_counts()
axes[1, 1].pie(pass_counts.values, labels=['Fail', 'Pass'], autopct='%1.1f%%', 
               colors=['#FF6B6B', '#95E1D3'], startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'})
axes[1, 1].set_title(f'Pass/Fail Distribution\n(Pass Rate: {df["pass_fail"].mean()*100:.1f}%)', 
                      fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('plots/01_overall_statistics.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/01_overall_statistics.png")
plt.close()

# ===== 2. KEY CORRELATIONS =====
print("[2] Generating correlation analysis...")

fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Energy density vs quality score
axes[0, 0].scatter(df['energy_density_j_mm2'], df['quality_score'], alpha=0.3, s=10)
axes[0, 0].set_xlabel('Energy Density (J/mm²)', fontsize=12)
axes[0, 0].set_ylabel('Quality Score', fontsize=12)
axes[0, 0].set_title('Energy Density vs Quality Score', fontsize=14, fontweight='bold')
z = np.polyfit(df['energy_density_j_mm2'], df['quality_score'], 2)
p = np.poly1d(z)
x_smooth = np.linspace(df['energy_density_j_mm2'].min(), df['energy_density_j_mm2'].max(), 100)
axes[0, 0].plot(x_smooth, p(x_smooth), 'r-', linewidth=2, label='Polynomial fit')
axes[0, 0].legend()

# IMC thickness vs contact resistance (critical U-shaped relationship)
axes[0, 1].scatter(df['imc_thickness_um'], df['contact_resistance_microohm'], alpha=0.3, s=10, c=df['quality_score'], cmap='RdYlGn')
axes[0, 1].set_xlabel('IMC Thickness (µm)', fontsize=12)
axes[0, 1].set_ylabel('Contact Resistance (µΩ)', fontsize=12)
axes[0, 1].set_title('IMC Thickness vs Contact Resistance\n(Optimal ~2µm)', fontsize=14, fontweight='bold')
axes[0, 1].axvline(2, color='red', linestyle='--', linewidth=2, label='Optimal (~2µm)')
axes[0, 1].legend()
cbar = plt.colorbar(axes[0, 1].collections[0], ax=axes[0, 1])
cbar.set_label('Quality Score', fontsize=10)

# Resistance increase vs fatigue life
axes[1, 0].scatter(df['resistance_increase_percent'], df['fatigue_life_cycles'], 
                   alpha=0.3, s=10, c=df['quality_score'], cmap='RdYlGn')
axes[1, 0].set_xlabel('Resistance Increase (%)', fontsize=12)
axes[1, 0].set_ylabel('Fatigue Life (cycles)', fontsize=12)
axes[1, 0].set_title('Resistance Increase vs Fatigue Life', fontsize=14, fontweight='bold')
axes[1, 0].axvline(30, color='red', linestyle='--', linewidth=2, label='Pass threshold')
axes[1, 0].axhline(800, color='red', linestyle='--', linewidth=2)
axes[1, 0].legend()

# Porosity vs quality score
axes[1, 1].scatter(df['porosity_percent'], df['quality_score'], alpha=0.3, s=10)
axes[1, 1].set_xlabel('Porosity (%)', fontsize=12)
axes[1, 1].set_ylabel('Quality Score', fontsize=12)
axes[1, 1].set_title('Porosity vs Quality Score', fontsize=14, fontweight='bold')
z = np.polyfit(df['porosity_percent'], df['quality_score'], 1)
p = np.poly1d(z)
axes[1, 1].plot(df['porosity_percent'].sort_values(), p(df['porosity_percent'].sort_values()), 
                'r-', linewidth=2, label='Linear fit')
axes[1, 1].legend()

plt.tight_layout()
plt.savefig('plots/02_key_correlations.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/02_key_correlations.png")
plt.close()

# ===== 3. TECHNIQUE COMPARISON =====
print("[3] Generating technique comparison...")

fig, axes = plt.subplots(2, 2, figsize=(15, 12))

techniques = df['welding_technique'].unique()

# Quality score by technique
df.boxplot(column='quality_score', by='welding_technique', ax=axes[0, 0])
axes[0, 0].set_xlabel('Welding Technique', fontsize=12)
axes[0, 0].set_ylabel('Quality Score', fontsize=12)
axes[0, 0].set_title('Quality Score by Technique', fontsize=14, fontweight='bold')
axes[0, 0].get_figure().suptitle('')  # Remove default title

# Pass rate by technique
pass_rates = df.groupby('welding_technique')['pass_fail'].mean() * 100
axes[0, 1].bar(pass_rates.index, pass_rates.values, color=colors, edgecolor='black', alpha=0.7)
axes[0, 1].set_xlabel('Welding Technique', fontsize=12)
axes[0, 1].set_ylabel('Pass Rate (%)', fontsize=12)
axes[0, 1].set_title('Pass Rate by Technique', fontsize=14, fontweight='bold')
axes[0, 1].axhline(df['pass_fail'].mean()*100, color='red', linestyle='--', linewidth=2, label='Overall average')
axes[0, 1].legend()
for i, v in enumerate(pass_rates.values):
    axes[0, 1].text(i, v + 1, f'{v:.1f}%', ha='center', fontweight='bold')

# Resistance increase by technique
df.boxplot(column='resistance_increase_percent', by='welding_technique', ax=axes[1, 0])
axes[1, 0].set_xlabel('Welding Technique', fontsize=12)
axes[1, 0].set_ylabel('Resistance Increase (%)', fontsize=12)
axes[1, 0].set_title('Resistance Increase by Technique', fontsize=14, fontweight='bold')
axes[1, 0].axhline(30, color='red', linestyle='--', linewidth=2, label='Pass threshold')
axes[1, 0].get_figure().suptitle('')
axes[1, 0].legend()

# Fatigue life by technique
df.boxplot(column='fatigue_life_cycles', by='welding_technique', ax=axes[1, 1])
axes[1, 1].set_xlabel('Welding Technique', fontsize=12)
axes[1, 1].set_ylabel('Fatigue Life (cycles)', fontsize=12)
axes[1, 1].set_title('Fatigue Life by Technique', fontsize=14, fontweight='bold')
axes[1, 1].axhline(800, color='red', linestyle='--', linewidth=2, label='Pass threshold')
axes[1, 1].get_figure().suptitle('')
axes[1, 1].legend()

plt.tight_layout()
plt.savefig('plots/03_technique_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/03_technique_comparison.png")
plt.close()

# ===== 4. PARAMETER SENSITIVITY =====
print("[4] Generating parameter sensitivity analysis...")

fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Power vs quality
axes[0, 0].scatter(df['power_w'], df['quality_score'], alpha=0.3, s=10, c=df['energy_density_j_mm2'], cmap='viridis')
axes[0, 0].set_xlabel('Power (W)', fontsize=12)
axes[0, 0].set_ylabel('Quality Score', fontsize=12)
axes[0, 0].set_title('Power vs Quality Score', fontsize=14, fontweight='bold')
cbar = plt.colorbar(axes[0, 0].collections[0], ax=axes[0, 0])
cbar.set_label('Energy Density', fontsize=10)

# Force vs quality
axes[0, 1].scatter(df['force_n'], df['quality_score'], alpha=0.3, s=10, c=df['imc_thickness_um'], cmap='plasma')
axes[0, 1].set_xlabel('Force (N)', fontsize=12)
axes[0, 1].set_ylabel('Quality Score', fontsize=12)
axes[0, 1].set_title('Force vs Quality Score', fontsize=14, fontweight='bold')
cbar = plt.colorbar(axes[0, 1].collections[0], ax=axes[0, 1])
cbar.set_label('IMC Thickness', fontsize=10)

# Time vs quality
axes[1, 0].scatter(df['time_ms'], df['quality_score'], alpha=0.3, s=10)
axes[1, 0].set_xlabel('Time (ms)', fontsize=12)
axes[1, 0].set_ylabel('Quality Score', fontsize=12)
axes[1, 0].set_title('Time vs Quality Score', fontsize=14, fontweight='bold')

# Peak temperature vs quality
axes[1, 1].scatter(df['peak_temperature_c'], df['quality_score'], alpha=0.3, s=10, c=df['porosity_percent'], cmap='Reds')
axes[1, 1].set_xlabel('Peak Temperature (°C)', fontsize=12)
axes[1, 1].set_ylabel('Quality Score', fontsize=12)
axes[1, 1].set_title('Peak Temperature vs Quality Score', fontsize=14, fontweight='bold')
cbar = plt.colorbar(axes[1, 1].collections[0], ax=axes[1, 1])
cbar.set_label('Porosity (%)', fontsize=10)

plt.tight_layout()
plt.savefig('plots/04_parameter_sensitivity.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/04_parameter_sensitivity.png")
plt.close()

# ===== 5. CORRELATION HEATMAP =====
print("[5] Generating correlation heatmap...")

# Select key numerical features
key_features = [
    'power_w', 'force_n', 'time_ms', 'energy_density_j_mm2',
    'imc_thickness_um', 'contact_resistance_microohm', 
    'shear_strength_mpa', 'porosity_percent',
    'resistance_increase_percent', 'fatigue_life_cycles',
    'quality_score'
]

corr_matrix = df[key_features].corr()

plt.figure(figsize=(14, 12))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', cmap='coolwarm', 
            center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8})
plt.title('Correlation Heatmap - Key Features', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('plots/05_correlation_heatmap.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/05_correlation_heatmap.png")
plt.close()

# ===== 6. DEFECT ANALYSIS =====
print("[6] Generating defect analysis...")

fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Defect distributions
axes[0, 0].hist(df['porosity_percent'], bins=30, edgecolor='black', alpha=0.7, color='coral')
axes[0, 0].set_xlabel('Porosity (%)', fontsize=12)
axes[0, 0].set_ylabel('Frequency', fontsize=12)
axes[0, 0].set_title('Porosity Distribution', fontsize=14, fontweight='bold')
axes[0, 0].axvline(5, color='red', linestyle='--', linewidth=2, label='Target <5%')
axes[0, 0].legend()

axes[0, 1].hist(df['crack_density_per_mm2'], bins=20, edgecolor='black', alpha=0.7, color='lightblue')
axes[0, 1].set_xlabel('Crack Density (per mm²)', fontsize=12)
axes[0, 1].set_ylabel('Frequency', fontsize=12)
axes[0, 1].set_title('Crack Density Distribution', fontsize=14, fontweight='bold')
axes[0, 1].axvline(3, color='red', linestyle='--', linewidth=2, label='Target <3')
axes[0, 1].legend()

# Defects vs quality
axes[1, 0].scatter(df['porosity_percent'], df['crack_density_per_mm2'], 
                   alpha=0.3, s=20, c=df['quality_score'], cmap='RdYlGn')
axes[1, 0].set_xlabel('Porosity (%)', fontsize=12)
axes[1, 0].set_ylabel('Crack Density (per mm²)', fontsize=12)
axes[1, 0].set_title('Porosity vs Crack Density', fontsize=14, fontweight='bold')
cbar = plt.colorbar(axes[1, 0].collections[0], ax=axes[1, 0])
cbar.set_label('Quality Score', fontsize=10)

# Combined defect index
df['defect_index'] = df['porosity_percent'] + df['crack_density_per_mm2'] + df['void_fraction_percent']
axes[1, 1].scatter(df['defect_index'], df['quality_score'], alpha=0.3, s=10)
axes[1, 1].set_xlabel('Combined Defect Index', fontsize=12)
axes[1, 1].set_ylabel('Quality Score', fontsize=12)
axes[1, 1].set_title('Combined Defects vs Quality Score', fontsize=14, fontweight='bold')
z = np.polyfit(df['defect_index'], df['quality_score'], 1)
p = np.poly1d(z)
axes[1, 1].plot(df['defect_index'].sort_values(), p(df['defect_index'].sort_values()), 
                'r-', linewidth=2, label=f'R² = {np.corrcoef(df["defect_index"], df["quality_score"])[0,1]**2:.3f}')
axes[1, 1].legend()

plt.tight_layout()
plt.savefig('plots/06_defect_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/06_defect_analysis.png")
plt.close()

# ===== 7. PERFORMANCE METRICS =====
print("[7] Generating performance metrics visualization...")

fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Thermal cycling effect
axes[0, 0].scatter(df['thermal_cycles_tested'], df['resistance_increase_percent'], alpha=0.3, s=10)
axes[0, 0].set_xlabel('Thermal Cycles Tested', fontsize=12)
axes[0, 0].set_ylabel('Resistance Increase (%)', fontsize=12)
axes[0, 0].set_title('Resistance Degradation vs Thermal Cycles', fontsize=14, fontweight='bold')
z = np.polyfit(df['thermal_cycles_tested'], df['resistance_increase_percent'], 1)
p = np.poly1d(z)
axes[0, 0].plot(df['thermal_cycles_tested'].sort_values(), p(df['thermal_cycles_tested'].sort_values()), 
                'r-', linewidth=2, label='Linear fit')
axes[0, 0].legend()

# Strength retention
axes[0, 1].hist(df['strength_retention_percent'], bins=30, edgecolor='black', alpha=0.7, color='lightgreen')
axes[0, 1].set_xlabel('Strength Retention (%)', fontsize=12)
axes[0, 1].set_ylabel('Frequency', fontsize=12)
axes[0, 1].set_title('Strength Retention Distribution', fontsize=14, fontweight='bold')
axes[0, 1].axvline(70, color='red', linestyle='--', linewidth=2, label='Pass threshold')
axes[0, 1].axvline(df['strength_retention_percent'].mean(), color='blue', linestyle='--', linewidth=2, label=f'Mean: {df["strength_retention_percent"].mean():.1f}%')
axes[0, 1].legend()

# Fatigue life distribution
axes[1, 0].hist(df['fatigue_life_cycles'], bins=30, edgecolor='black', alpha=0.7, color='gold')
axes[1, 0].set_xlabel('Fatigue Life (cycles)', fontsize=12)
axes[1, 0].set_ylabel('Frequency', fontsize=12)
axes[1, 0].set_title('Fatigue Life Distribution', fontsize=14, fontweight='bold')
axes[1, 0].axvline(800, color='red', linestyle='--', linewidth=2, label='Pass threshold')
axes[1, 0].axvline(df['fatigue_life_cycles'].mean(), color='blue', linestyle='--', linewidth=2, label=f'Mean: {df["fatigue_life_cycles"].mean():.0f}')
axes[1, 0].legend()

# Multi-metric performance
pass_samples = df[df['pass_fail'] == 1]
fail_samples = df[df['pass_fail'] == 0]
metrics = ['resistance_increase_percent', 'strength_retention_percent', 'fatigue_life_cycles']
x_pos = np.arange(len(metrics))
pass_means = [pass_samples[m].mean() for m in metrics]
fail_means = [fail_samples[m].mean() for m in metrics]
width = 0.35
axes[1, 1].bar(x_pos - width/2, pass_means, width, label='Pass', color='green', alpha=0.7)
axes[1, 1].bar(x_pos + width/2, fail_means, width, label='Fail', color='red', alpha=0.7)
axes[1, 1].set_xlabel('Performance Metrics', fontsize=12)
axes[1, 1].set_ylabel('Average Value', fontsize=12)
axes[1, 1].set_title('Pass vs Fail - Performance Comparison', fontsize=14, fontweight='bold')
axes[1, 1].set_xticks(x_pos)
axes[1, 1].set_xticklabels(['Resist. Inc. (%)', 'Strength Ret. (%)', 'Fatigue Life'], rotation=15)
axes[1, 1].legend()

plt.tight_layout()
plt.savefig('plots/07_performance_metrics.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/07_performance_metrics.png")
plt.close()

print("\n" + "="*80)
print("VISUALIZATION COMPLETE!")
print("="*80)
print("\nGenerated 7 comprehensive visualization files:")
print("   1. Overall Statistics - Quality distribution and pass rates")
print("   2. Key Correlations - Critical relationships in the data")
print("   3. Technique Comparison - Performance across welding methods")
print("   4. Parameter Sensitivity - Process parameter effects")
print("   5. Correlation Heatmap - Feature interdependencies")
print("   6. Defect Analysis - Defect patterns and impacts")
print("   7. Performance Metrics - Long-term reliability indicators")
print("\nAll plots saved in the 'plots/' directory")
print("="*80)
