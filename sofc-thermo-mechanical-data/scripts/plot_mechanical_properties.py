#!/usr/bin/env python3
"""
Plot mechanical properties (elastic modulus, strength) vs temperature.
Generates publication-quality figure: fig02_elastic_modulus_vs_temperature.png
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Define paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
FIGURES_DIR = SCRIPT_DIR.parent / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

# Material colors
COLORS = {
    '8YSZ': '#1f77b4',
    'GDC': '#ff7f0e',
    'Ni-YSZ': '#2ca02c',
    'LSCF': '#d62728',
    'LSM': '#9467bd',
    'Crofer22APU': '#8c564b'
}

def plot_mechanical_properties():
    """Create two-panel figure showing elastic modulus and strength vs temperature."""
    # Read data
    df = pd.read_csv(DATA_DIR / '02_mechanical_properties.csv', comment='#')
    
    # Create figure with two subplots
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot 1: Elastic Modulus vs Temperature
    ax1 = axes[0]
    for material in COLORS.keys():
        data = df[df['Material'] == material]
        ax1.plot(data['Temperature_C'], data['Elastic_Modulus_GPa'], 
                label=material, color=COLORS[material], linewidth=2.5, 
                marker='o', markersize=4, markevery=5)
    
    ax1.set_xlabel('Temperature (°C)', fontsize=12)
    ax1.set_ylabel('Elastic Modulus (GPa)', fontsize=12)
    ax1.set_title('(a) Elastic Modulus vs Temperature', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10, loc='best')
    ax1.set_ylim(0, 250)
    
    # Plot 2: Flexural Strength vs Temperature
    ax2 = axes[1]
    for material in COLORS.keys():
        data = df[df['Material'] == material]
        ax2.plot(data['Temperature_C'], data['Flexural_Strength_MPa'], 
                label=material, color=COLORS[material], linewidth=2.5, 
                marker='s', markersize=4, markevery=5)
    
    ax2.set_xlabel('Temperature (°C)', fontsize=12)
    ax2.set_ylabel('Flexural Strength (MPa)', fontsize=12)
    ax2.set_title('(b) Flexural Strength vs Temperature', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10, loc='best')
    
    # Overall title with disclaimer
    fig.suptitle('Mechanical Properties vs Temperature (Synthetic/Illustrative Data)', 
                 fontsize=14, fontweight='bold', y=1.00)
    
    plt.tight_layout()
    
    # Save figure
    output_path = FIGURES_DIR / 'fig02_mechanical_properties.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved {output_path.name}")
    plt.close()


if __name__ == "__main__":
    plot_mechanical_properties()
