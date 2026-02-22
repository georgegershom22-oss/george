#!/usr/bin/env python3
"""
Plot thermal properties (CTE, thermal conductivity, specific heat) vs temperature.
Generates publication-quality figure: fig01_CTE_vs_temperature.png
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Define paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
FIGURES_DIR = SCRIPT_DIR.parent / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

# Material colors (consistent across all plots)
COLORS = {
    '8YSZ': '#1f77b4',
    'GDC': '#ff7f0e',
    'Ni-YSZ': '#2ca02c',
    'LSCF': '#d62728',
    'LSM': '#9467bd',
    'Crofer22APU': '#8c564b'
}

def plot_thermal_properties():
    """Create three-panel figure showing thermal properties vs temperature."""
    # Read data
    df = pd.read_csv(DATA_DIR / '01_thermal_properties.csv', comment='#')
    
    # Create figure with three subplots
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    # Plot 1: CTE vs Temperature
    ax1 = axes[0]
    for material in COLORS.keys():
        data = df[df['Material'] == material]
        ax1.plot(data['Temperature_C'], data['CTE_1e-6_per_K'], 
                label=material, color=COLORS[material], linewidth=2, marker='o', 
                markersize=3, markevery=5)
    
    ax1.set_xlabel('Temperature (°C)', fontsize=12)
    ax1.set_ylabel('CTE (10⁻⁶ K⁻¹)', fontsize=12)
    ax1.set_title('(a) Coefficient of Thermal Expansion', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=9, loc='best')
    
    # Plot 2: Thermal Conductivity vs Temperature
    ax2 = axes[1]
    for material in COLORS.keys():
        data = df[df['Material'] == material]
        ax2.plot(data['Temperature_C'], data['Thermal_Conductivity_W_per_mK'], 
                label=material, color=COLORS[material], linewidth=2, marker='s', 
                markersize=3, markevery=5)
    
    ax2.set_xlabel('Temperature (°C)', fontsize=12)
    ax2.set_ylabel('Thermal Conductivity (W m⁻¹ K⁻¹)', fontsize=12)
    ax2.set_title('(b) Thermal Conductivity', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=9, loc='best')
    
    # Plot 3: Specific Heat vs Temperature
    ax3 = axes[2]
    for material in COLORS.keys():
        data = df[df['Material'] == material]
        ax3.plot(data['Temperature_C'], data['Specific_Heat_J_per_kgK'], 
                label=material, color=COLORS[material], linewidth=2, marker='^', 
                markersize=3, markevery=5)
    
    ax3.set_xlabel('Temperature (°C)', fontsize=12)
    ax3.set_ylabel('Specific Heat (J kg⁻¹ K⁻¹)', fontsize=12)
    ax3.set_title('(c) Specific Heat Capacity', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=9, loc='best')
    
    # Overall title with disclaimer
    fig.suptitle('Thermal Properties vs Temperature (Synthetic/Illustrative Data)', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    
    # Save figure
    output_path = FIGURES_DIR / 'fig01_thermal_properties.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved {output_path.name}")
    plt.close()


if __name__ == "__main__":
    plot_thermal_properties()
