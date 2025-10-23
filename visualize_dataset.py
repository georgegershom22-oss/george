"""
SOFC Dataset Visualization Script
Creates plots to explore the generated low-fidelity dataset
"""

import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def load_data(data_dir='sofc_lf_dataset'):
    """Load the SOFC dataset"""
    df = pd.read_csv(f'{data_dir}/sofc_lf_main_dataset.csv')
    
    with open(f'{data_dir}/sofc_lf_vi_curves.json', 'r') as f:
        vi_data = json.load(f)
    
    return df, vi_data

def plot_parameter_distributions(df, output_dir='sofc_lf_dataset/figures'):
    """Plot distributions of input parameters"""
    Path(output_dir).mkdir(exist_ok=True)
    
    input_params = [
        ('temperature', 'Temperature (°C)'),
        ('fuel_utilization', 'Fuel Utilization'),
        ('anode_porosity', 'Anode Porosity'),
        ('anode_thickness', 'Anode Thickness (μm)'),
        ('cathode_thickness', 'Cathode Thickness (μm)'),
        ('electrolyte_thickness', 'Electrolyte Thickness (μm)'),
        ('active_area', 'Active Area (cm²)')
    ]
    
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    axes = axes.flatten()
    
    for idx, (param, label) in enumerate(input_params):
        ax = axes[idx]
        ax.hist(df[param], bins=50, edgecolor='black', alpha=0.7)
        ax.set_xlabel(label, fontsize=10)
        ax.set_ylabel('Frequency', fontsize=10)
        ax.set_title(f'Distribution of {label}', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    # Hide unused subplots
    for idx in range(len(input_params), len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/input_parameter_distributions.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_dir}/input_parameter_distributions.png")
    plt.close()

def plot_output_distributions(df, output_dir='sofc_lf_dataset/figures'):
    """Plot distributions of output parameters"""
    Path(output_dir).mkdir(exist_ok=True)
    
    output_params = [
        ('operating_voltage', 'Operating Voltage (V)'),
        ('stack_temperature', 'Stack Temperature (°C)'),
        ('electrochemical_efficiency', 'Electrochemical Efficiency'),
        ('open_circuit_voltage', 'Open Circuit Voltage (V)'),
        ('max_power_density', 'Max Power Density (W/m²)')
    ]
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes = axes.flatten()
    
    for idx, (param, label) in enumerate(output_params):
        ax = axes[idx]
        ax.hist(df[param], bins=50, edgecolor='black', alpha=0.7, color='coral')
        ax.set_xlabel(label, fontsize=10)
        ax.set_ylabel('Frequency', fontsize=10)
        ax.set_title(f'Distribution of {label}', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    # Hide unused subplot
    axes[-1].axis('off')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/output_parameter_distributions.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_dir}/output_parameter_distributions.png")
    plt.close()

def plot_vi_curves_sample(df, vi_data, num_samples=10, output_dir='sofc_lf_dataset/figures'):
    """Plot sample V-I curves"""
    Path(output_dir).mkdir(exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot random samples
    np.random.seed(42)
    sample_indices = np.random.choice(len(df), size=num_samples, replace=False)
    
    for idx in sample_indices:
        sample = vi_data[idx]
        i_vals = np.array(sample['vi_current_densities'])
        v_vals = np.array(sample['vi_voltages'])
        temp = df.iloc[idx]['temperature']
        
        ax.plot(i_vals / 1000, v_vals, alpha=0.6, linewidth=2, 
                label=f'T={temp:.0f}°C' if idx < 5 else '')
    
    ax.set_xlabel('Current Density (kA/m²)', fontsize=12)
    ax.set_ylabel('Cell Voltage (V)', fontsize=12)
    ax.set_title('Sample V-I Characteristic Curves', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/sample_vi_curves.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_dir}/sample_vi_curves.png")
    plt.close()

def plot_correlation_matrix(df, output_dir='sofc_lf_dataset/figures'):
    """Plot correlation matrix"""
    Path(output_dir).mkdir(exist_ok=True)
    
    # Select key parameters
    params = [
        'temperature', 'fuel_utilization', 'anode_porosity',
        'operating_voltage', 'stack_temperature', 
        'electrochemical_efficiency', 'max_power_density'
    ]
    
    corr_matrix = df[params].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm', 
                center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                ax=ax)
    ax.set_title('Correlation Matrix of Key Parameters', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/correlation_matrix.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_dir}/correlation_matrix.png")
    plt.close()

def plot_temperature_effects(df, output_dir='sofc_lf_dataset/figures'):
    """Plot temperature effects on performance"""
    Path(output_dir).mkdir(exist_ok=True)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Temperature vs Operating Voltage
    axes[0, 0].scatter(df['temperature'], df['operating_voltage'], 
                       alpha=0.3, s=10, c=df['anode_porosity'], cmap='viridis')
    axes[0, 0].set_xlabel('Temperature (°C)', fontsize=11)
    axes[0, 0].set_ylabel('Operating Voltage (V)', fontsize=11)
    axes[0, 0].set_title('Temperature vs Operating Voltage', fontsize=12, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Temperature vs Efficiency
    axes[0, 1].scatter(df['temperature'], df['electrochemical_efficiency'], 
                       alpha=0.3, s=10, c=df['fuel_utilization'], cmap='plasma')
    axes[0, 1].set_xlabel('Temperature (°C)', fontsize=11)
    axes[0, 1].set_ylabel('Electrochemical Efficiency', fontsize=11)
    axes[0, 1].set_title('Temperature vs Efficiency', fontsize=12, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Temperature vs Max Power
    axes[1, 0].scatter(df['temperature'], df['max_power_density'] / 1000, 
                       alpha=0.3, s=10, c=df['anode_porosity'], cmap='coolwarm')
    axes[1, 0].set_xlabel('Temperature (°C)', fontsize=11)
    axes[1, 0].set_ylabel('Max Power Density (kW/m²)', fontsize=11)
    axes[1, 0].set_title('Temperature vs Max Power Density', fontsize=12, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Temperature vs Stack Temperature
    axes[1, 1].scatter(df['temperature'], df['stack_temperature'], 
                       alpha=0.3, s=10)
    axes[1, 1].plot([700, 900], [700, 900], 'r--', linewidth=2, label='T_stack = T_op')
    axes[1, 1].set_xlabel('Operating Temperature (°C)', fontsize=11)
    axes[1, 1].set_ylabel('Stack Temperature (°C)', fontsize=11)
    axes[1, 1].set_title('Operating vs Stack Temperature', fontsize=12, fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].legend()
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/temperature_effects.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_dir}/temperature_effects.png")
    plt.close()

def plot_power_curves(df, vi_data, output_dir='sofc_lf_dataset/figures'):
    """Plot power density curves"""
    Path(output_dir).mkdir(exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Get temperature bins
    temp_bins = pd.cut(df['temperature'], bins=5)
    temp_centers = [interval.mid for interval in temp_bins.cat.categories]
    
    # Plot one curve per temperature bin
    for idx, (interval, group) in enumerate(df.groupby(temp_bins)):
        if len(group) > 0:
            sample_idx = group.index[0]
            sample = vi_data[sample_idx]
            i_vals = np.array(sample['vi_current_densities'])
            v_vals = np.array(sample['vi_voltages'])
            p_vals = i_vals * v_vals / 1000  # Power in kW/m²
            
            ax.plot(i_vals / 1000, p_vals, linewidth=2.5, 
                    label=f'T ≈ {interval.mid:.0f}°C')
    
    ax.set_xlabel('Current Density (kA/m²)', fontsize=12)
    ax.set_ylabel('Power Density (kW/m²)', fontsize=12)
    ax.set_title('Power Density Curves at Different Temperatures', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/power_curves.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_dir}/power_curves.png")
    plt.close()

def main():
    """Main visualization function"""
    print("="*70)
    print("SOFC Dataset Visualization")
    print("="*70)
    
    # Load data
    print("\n[1/7] Loading dataset...")
    df, vi_data = load_data()
    print(f"  ✓ Loaded {len(df)} samples")
    
    # Create visualizations
    print("\n[2/7] Plotting input parameter distributions...")
    plot_parameter_distributions(df)
    
    print("\n[3/7] Plotting output parameter distributions...")
    plot_output_distributions(df)
    
    print("\n[4/7] Plotting sample V-I curves...")
    plot_vi_curves_sample(df, vi_data)
    
    print("\n[5/7] Plotting correlation matrix...")
    plot_correlation_matrix(df)
    
    print("\n[6/7] Plotting temperature effects...")
    plot_temperature_effects(df)
    
    print("\n[7/7] Plotting power density curves...")
    plot_power_curves(df, vi_data)
    
    print("\n" + "="*70)
    print("Visualization Complete!")
    print("="*70)
    print("All figures saved in: sofc_lf_dataset/figures/")
    print("="*70)

if __name__ == "__main__":
    main()
