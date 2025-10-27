"""
Visualization Script for Welding Dataset
Creates comprehensive plots and charts for data exploration
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 100

print("="*80)
print("CREATING VISUALIZATIONS")
print("="*80)
print()

# Load data
df = pd.read_csv('/workspace/welding_ml_dataset.csv')

# Create output directory for plots
import os
os.makedirs('/workspace/plots', exist_ok=True)

# ============================================================================
# 1. Target Variable Distribution
# ============================================================================

print("1. Creating target variable distribution plot...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Histogram
axes[0, 0].hist(df['thermal_cycles_to_failure'], bins=50, edgecolor='black', alpha=0.7)
axes[0, 0].set_xlabel('Thermal Cycles to Failure')
axes[0, 0].set_ylabel('Frequency')
axes[0, 0].set_title('Distribution of Thermal Cycles to Failure')
axes[0, 0].axvline(df['thermal_cycles_to_failure'].mean(), color='red', linestyle='--', label='Mean')
axes[0, 0].axvline(df['thermal_cycles_to_failure'].median(), color='green', linestyle='--', label='Median')
axes[0, 0].legend()

# Box plot by welding technique
df.boxplot(column='thermal_cycles_to_failure', by='welding_technique', ax=axes[0, 1])
axes[0, 1].set_title('Thermal Cycles by Welding Technique')
axes[0, 1].set_xlabel('Welding Technique')
axes[0, 1].set_ylabel('Thermal Cycles to Failure')
plt.sca(axes[0, 1])
plt.xticks(rotation=45)

# Violin plot
sns.violinplot(data=df, x='welding_technique', y='thermal_cycles_to_failure', ax=axes[1, 0])
axes[1, 0].set_title('Distribution by Welding Technique')
axes[1, 0].set_xlabel('Welding Technique')
axes[1, 0].set_ylabel('Thermal Cycles to Failure')
axes[1, 0].tick_params(axis='x', rotation=45)

# QQ plot
from scipy import stats
stats.probplot(df['thermal_cycles_to_failure'], dist="norm", plot=axes[1, 1])
axes[1, 1].set_title('Q-Q Plot (Normal Distribution)')

plt.tight_layout()
plt.savefig('/workspace/plots/01_target_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: plots/01_target_distribution.png")

# ============================================================================
# 2. Correlation Heatmap
# ============================================================================

print("2. Creating correlation heatmap...")
# Select numerical columns
numerical_cols = df.select_dtypes(include=[np.number]).columns
corr_data = df[numerical_cols].corr()

# Focus on top correlations with target
target_corr = corr_data['thermal_cycles_to_failure'].abs().sort_values(ascending=False).head(15)
important_features = target_corr.index.tolist()

fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(df[important_features].corr(), annot=True, fmt='.2f', cmap='coolwarm', 
            center=0, square=True, linewidths=1, ax=ax)
plt.title('Correlation Heatmap - Top 15 Features', fontsize=14, pad=20)
plt.tight_layout()
plt.savefig('/workspace/plots/02_correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: plots/02_correlation_heatmap.png")

# ============================================================================
# 3. IMC Thickness Analysis
# ============================================================================

print("3. Creating IMC thickness analysis plot...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# IMC distribution
axes[0, 0].hist(df['IMC_thickness_um'], bins=50, edgecolor='black', alpha=0.7)
axes[0, 0].axvspan(1, 3, alpha=0.2, color='green', label='Optimal Range (1-3 µm)')
axes[0, 0].set_xlabel('IMC Thickness (µm)')
axes[0, 0].set_ylabel('Frequency')
axes[0, 0].set_title('IMC Layer Thickness Distribution')
axes[0, 0].legend()

# Scatter: IMC vs Thermal Cycles
axes[0, 1].scatter(df['IMC_thickness_um'], df['thermal_cycles_to_failure'], alpha=0.3, s=10)
axes[0, 1].set_xlabel('IMC Thickness (µm)')
axes[0, 1].set_ylabel('Thermal Cycles to Failure')
axes[0, 1].set_title('IMC Thickness vs Performance')
axes[0, 1].axvspan(1, 3, alpha=0.2, color='green')

# Binned analysis
df['IMC_bin'] = pd.cut(df['IMC_thickness_um'], bins=[0, 1, 3, 5, 20], 
                       labels=['<1', '1-3 (Optimal)', '3-5', '>5'])
imc_grouped = df.groupby('IMC_bin')['thermal_cycles_to_failure'].mean()
imc_grouped.plot(kind='bar', ax=axes[1, 0], color='steelblue')
axes[1, 0].set_xlabel('IMC Thickness Range (µm)')
axes[1, 0].set_ylabel('Avg Thermal Cycles')
axes[1, 0].set_title('Performance by IMC Range')
axes[1, 0].tick_params(axis='x', rotation=45)

# IMC vs Contact Resistance
axes[1, 1].scatter(df['IMC_thickness_um'], df['contact_resistance_uOhm'], alpha=0.3, s=10)
axes[1, 1].set_xlabel('IMC Thickness (µm)')
axes[1, 1].set_ylabel('Contact Resistance (µΩ)')
axes[1, 1].set_title('IMC vs Contact Resistance')

plt.tight_layout()
plt.savefig('/workspace/plots/03_imc_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: plots/03_imc_analysis.png")

# ============================================================================
# 4. Energy Density Analysis
# ============================================================================

print("4. Creating energy density analysis plot...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Energy density distribution (log scale due to wide range)
axes[0, 0].hist(np.log10(df['energy_density_J_mm2']), bins=50, edgecolor='black', alpha=0.7)
axes[0, 0].set_xlabel('Log10(Energy Density) [J/mm²]')
axes[0, 0].set_ylabel('Frequency')
axes[0, 0].set_title('Energy Density Distribution (Log Scale)')

# Energy vs Cycles by technique
for technique in df['welding_technique'].unique():
    subset = df[df['welding_technique'] == technique]
    axes[0, 1].scatter(subset['energy_density_J_mm2'], subset['thermal_cycles_to_failure'], 
                      label=technique, alpha=0.4, s=10)
axes[0, 1].set_xlabel('Energy Density (J/mm²)')
axes[0, 1].set_ylabel('Thermal Cycles to Failure')
axes[0, 1].set_title('Energy Density vs Performance by Technique')
axes[0, 1].legend()
axes[0, 1].set_xlim(0, 2000)  # Focus on main distribution

# Energy efficiency score
axes[1, 0].hist(df['energy_efficiency_score'], bins=40, edgecolor='black', alpha=0.7)
axes[1, 0].set_xlabel('Energy Efficiency Score')
axes[1, 0].set_ylabel('Frequency')
axes[1, 0].set_title('Energy Efficiency Distribution')

# Efficiency vs Cycles
axes[1, 1].scatter(df['energy_efficiency_score'], df['thermal_cycles_to_failure'], alpha=0.3, s=10)
axes[1, 1].set_xlabel('Energy Efficiency Score')
axes[1, 1].set_ylabel('Thermal Cycles to Failure')
axes[1, 1].set_title('Efficiency vs Performance')

plt.tight_layout()
plt.savefig('/workspace/plots/04_energy_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: plots/04_energy_analysis.png")

# ============================================================================
# 5. Material Combinations
# ============================================================================

print("5. Creating material combination analysis plot...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Material combinations performance
material_combo = df.groupby(['anode_material', 'cathode_material'])['thermal_cycles_to_failure'].mean().unstack()
sns.heatmap(material_combo, annot=True, fmt='.0f', cmap='YlGnBu', ax=axes[0, 0])
axes[0, 0].set_title('Avg Thermal Cycles by Material Combination')
axes[0, 0].set_xlabel('Cathode Material')
axes[0, 0].set_ylabel('Anode Material')

# Surface finish impact
surface_perf = df.groupby('surface_finish')['thermal_cycles_to_failure'].mean().sort_values()
surface_perf.plot(kind='barh', ax=axes[0, 1], color='coral')
axes[0, 1].set_xlabel('Avg Thermal Cycles to Failure')
axes[0, 1].set_ylabel('Surface Finish')
axes[0, 1].set_title('Performance by Surface Finish')

# Anode material distribution
df.groupby('anode_material')['thermal_cycles_to_failure'].apply(
    lambda x: axes[1, 0].hist(x, alpha=0.5, label=x.name, bins=30)
)
axes[1, 0].set_xlabel('Thermal Cycles to Failure')
axes[1, 0].set_ylabel('Frequency')
axes[1, 0].set_title('Distribution by Anode Material')
axes[1, 0].legend(df['anode_material'].unique())

# Cathode material distribution
df.groupby('cathode_material')['thermal_cycles_to_failure'].apply(
    lambda x: axes[1, 1].hist(x, alpha=0.5, label=x.name, bins=30)
)
axes[1, 1].set_xlabel('Thermal Cycles to Failure')
axes[1, 1].set_ylabel('Frequency')
axes[1, 1].set_title('Distribution by Cathode Material')
axes[1, 1].legend(df['cathode_material'].unique(), fontsize=8)

plt.tight_layout()
plt.savefig('/workspace/plots/05_material_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: plots/05_material_analysis.png")

# ============================================================================
# 6. Process Parameters
# ============================================================================

print("6. Creating process parameters plot...")
fig, axes = plt.subplots(2, 3, figsize=(16, 10))

params = ['power_W', 'force_N', 'time_ms', 'tab_thickness_um', 'preheat_temp_C']
axes_flat = axes.flatten()

for idx, param in enumerate(params):
    axes_flat[idx].scatter(df[param], df['thermal_cycles_to_failure'], alpha=0.3, s=5)
    axes_flat[idx].set_xlabel(param.replace('_', ' ').title())
    axes_flat[idx].set_ylabel('Thermal Cycles to Failure')
    axes_flat[idx].set_title(f'{param.replace("_", " ").title()} vs Performance')
    
    # Add trend line
    z = np.polyfit(df[param], df['thermal_cycles_to_failure'], 1)
    p = np.poly1d(z)
    axes_flat[idx].plot(df[param].sort_values(), p(df[param].sort_values()), 
                       "r--", alpha=0.8, linewidth=2)

# Remove extra subplot
fig.delaxes(axes_flat[5])

plt.tight_layout()
plt.savefig('/workspace/plots/06_process_parameters.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: plots/06_process_parameters.png")

# ============================================================================
# 7. Quality Metrics
# ============================================================================

print("7. Creating quality metrics plot...")
fig, axes = plt.subplots(2, 3, figsize=(16, 10))

quality_metrics = [
    ('contact_resistance_uOhm', 'Contact Resistance (µΩ)'),
    ('tensile_shear_strength_N', 'Tensile Strength (N)'),
    ('porosity_pct', 'Porosity (%)'),
    ('microstructure_uniformity_score', 'Microstructure Uniformity'),
    ('overall_quality_score', 'Overall Quality Score')
]

for idx, (metric, label) in enumerate(quality_metrics):
    axes.flatten()[idx].scatter(df[metric], df['thermal_cycles_to_failure'], alpha=0.3, s=5)
    axes.flatten()[idx].set_xlabel(label)
    axes.flatten()[idx].set_ylabel('Thermal Cycles to Failure')
    axes.flatten()[idx].set_title(f'{label} vs Performance')

# Remove extra subplot
fig.delaxes(axes.flatten()[5])

plt.tight_layout()
plt.savefig('/workspace/plots/07_quality_metrics.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: plots/07_quality_metrics.png")

# ============================================================================
# 8. Degradation Metrics
# ============================================================================

print("8. Creating degradation metrics plot...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Resistance increase
axes[0, 0].scatter(df['thermal_cycles_to_failure'], df['resistance_increase_after_cycling_pct'], 
                  alpha=0.3, s=5)
axes[0, 0].set_xlabel('Thermal Cycles to Failure')
axes[0, 0].set_ylabel('Resistance Increase (%)')
axes[0, 0].set_title('Durability vs Resistance Degradation')

# Strength retention
axes[0, 1].scatter(df['thermal_cycles_to_failure'], df['strength_retention_pct'], 
                  alpha=0.3, s=5)
axes[0, 1].set_xlabel('Thermal Cycles to Failure')
axes[0, 1].set_ylabel('Strength Retention (%)')
axes[0, 1].set_title('Durability vs Strength Retention')

# Crack initiation
axes[1, 0].scatter(df['crack_initiation_cycle'], df['thermal_cycles_to_failure'], 
                  alpha=0.3, s=5)
axes[1, 0].plot([0, 3000], [0, 3000], 'r--', alpha=0.5, label='1:1 line')
axes[1, 0].set_xlabel('Crack Initiation Cycle')
axes[1, 0].set_ylabel('Thermal Cycles to Failure')
axes[1, 0].set_title('Crack Initiation vs Total Failure')
axes[1, 0].legend()

# Max operating temperature
axes[1, 1].scatter(df['max_operating_temp_C'], df['thermal_cycles_to_failure'], 
                  alpha=0.3, s=5)
axes[1, 1].set_xlabel('Max Operating Temperature (°C)')
axes[1, 1].set_ylabel('Thermal Cycles to Failure')
axes[1, 1].set_title('Operating Temperature vs Durability')

plt.tight_layout()
plt.savefig('/workspace/plots/08_degradation_metrics.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: plots/08_degradation_metrics.png")

# ============================================================================
# 9. Technique Comparison Dashboard
# ============================================================================

print("9. Creating technique comparison dashboard...")
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

techniques = df['welding_technique'].unique()
colors = {'Ultrasonic': 'blue', 'Laser': 'red', 'Resistance-Spot': 'green'}

# Main scatter plot
ax_main = fig.add_subplot(gs[0:2, 0:2])
for technique in techniques:
    subset = df[df['welding_technique'] == technique]
    ax_main.scatter(subset['energy_density_J_mm2'], subset['thermal_cycles_to_failure'], 
                   label=technique, alpha=0.4, s=20, color=colors.get(technique, 'gray'))
ax_main.set_xlabel('Energy Density (J/mm²)')
ax_main.set_ylabel('Thermal Cycles to Failure')
ax_main.set_title('Technique Comparison: Energy vs Performance', fontsize=14, fontweight='bold')
ax_main.legend()
ax_main.set_xlim(0, 1500)

# Histograms for each technique
for idx, technique in enumerate(techniques):
    ax = fig.add_subplot(gs[idx, 2])
    subset = df[df['welding_technique'] == technique]
    ax.hist(subset['thermal_cycles_to_failure'], bins=30, alpha=0.7, 
           color=colors.get(technique, 'gray'), edgecolor='black')
    ax.set_title(technique, fontsize=10)
    ax.set_xlabel('Thermal Cycles')
    ax.set_ylabel('Count')
    ax.axvline(subset['thermal_cycles_to_failure'].mean(), color='red', linestyle='--', 
              linewidth=2, label='Mean')
    ax.legend(fontsize=8)

# Box plots
ax_box = fig.add_subplot(gs[2, 0])
df.boxplot(column='thermal_cycles_to_failure', by='welding_technique', ax=ax_box)
ax_box.set_title('Distribution Comparison')
ax_box.set_xlabel('Technique')
ax_box.set_ylabel('Thermal Cycles')
plt.sca(ax_box)
plt.xticks(rotation=45, ha='right')

# Performance metrics table
ax_table = fig.add_subplot(gs[2, 1:])
ax_table.axis('tight')
ax_table.axis('off')

table_data = []
for technique in techniques:
    subset = df[df['welding_technique'] == technique]
    table_data.append([
        technique,
        f"{subset['thermal_cycles_to_failure'].mean():.0f}",
        f"{subset['contact_resistance_uOhm'].mean():.1f}",
        f"{subset['tensile_shear_strength_N'].mean():.0f}",
        f"{subset['overall_quality_score'].mean():.1f}"
    ])

table = ax_table.table(cellText=table_data, 
                      colLabels=['Technique', 'Avg Cycles', 'Avg Resistance\n(µΩ)', 
                                'Avg Strength\n(N)', 'Avg Quality'],
                      cellLoc='center', loc='center')
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 2)

plt.savefig('/workspace/plots/09_technique_dashboard.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: plots/09_technique_dashboard.png")

# ============================================================================
# 10. Multi-Dimensional Analysis (Pair Plot Sample)
# ============================================================================

print("10. Creating multi-dimensional analysis plot...")
# Sample data to avoid overcrowding
sample_df = df.sample(n=1000, random_state=42)

key_features = ['energy_density_J_mm2', 'IMC_thickness_um', 'contact_resistance_uOhm', 
                'thermal_cycles_to_failure', 'welding_technique']

# Create pair plot
g = sns.pairplot(sample_df[key_features], hue='welding_technique', 
                diag_kind='kde', plot_kws={'alpha': 0.5, 's': 20},
                height=2.5)
g.fig.suptitle('Multi-Dimensional Feature Relationships (n=1000 sample)', y=1.02, fontsize=14)
plt.savefig('/workspace/plots/10_pairplot.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved: plots/10_pairplot.png")

print()
print("="*80)
print(f"✓ All visualizations complete! Saved 10 plots to /workspace/plots/")
print("="*80)
