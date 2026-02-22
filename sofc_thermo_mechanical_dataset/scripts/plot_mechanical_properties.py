#!/usr/bin/env python3
"""
Plot mechanical properties (elastic modulus, flexural strength) vs temperature.

DISCLAIMER: All data is SYNTHETIC/ILLUSTRATIVE, based on published literature ranges.

Output: 2-panel figure showing temperature-dependent mechanical properties
"""

import csv
import os
import matplotlib.pyplot as plt
import matplotlib as mpl

# Set publication-quality defaults
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.size'] = 12
mpl.rcParams['figure.dpi'] = 300

# Consistent color scheme for all materials
COLORS = {
    '8YSZ': '#1f77b4',
    'GDC': '#ff7f0e',
    'Ni-YSZ': '#2ca02c',
    'LSCF': '#d62728',
    'LSM': '#9467bd',
    'Crofer 22 APU': '#8c564b'
}

def load_mechanical_data():
    """Load mechanical properties data from CSV."""
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', '02_mechanical_properties.csv')
    
    # Skip comment lines
    with open(data_file, 'r') as f:
        lines = [line for line in f if not line.startswith('#')]
    
    # Parse CSV
    reader = csv.DictReader(lines)
    
    # Organize data by material
    materials_data = {}
    for row in reader:
        mat = row['Material']
        if mat not in materials_data:
            materials_data[mat] = {'T': [], 'E': [], 'sigma': []}
        
        materials_data[mat]['T'].append(float(row['Temperature_C']))
        materials_data[mat]['E'].append(float(row['Elastic_Modulus_GPa']))
        materials_data[mat]['sigma'].append(float(row['Flexural_Strength_MPa']))
    
    return materials_data


def plot_mechanical_properties():
    """Create 2-panel figure with mechanical properties."""
    data = load_mechanical_data()
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('SYNTHETIC DATA — Based on Literature Ranges\nMechanical Properties of SOFC Materials',
                 fontsize=14, fontweight='bold', y=0.98)
    
    # Panel 1: Elastic Modulus
    ax1 = axes[0]
    for mat_name, mat_data in data.items():
        ax1.plot(mat_data['T'], mat_data['E'], '-o', label=mat_name,
                color=COLORS[mat_name], linewidth=2, markersize=5)
    
    ax1.set_xlabel('Temperature (°C)', fontsize=12)
    ax1.set_ylabel('Elastic Modulus (GPa)', fontsize=12)
    ax1.set_title('(a) Elastic Modulus', fontsize=12, fontweight='bold')
    ax1.legend(loc='best', framealpha=0.9, fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 1050])
    ax1.set_ylim([0, 250])
    
    # Panel 2: Flexural Strength
    ax2 = axes[1]
    for mat_name, mat_data in data.items():
        ax2.plot(mat_data['T'], mat_data['sigma'], '-s', label=mat_name,
                color=COLORS[mat_name], linewidth=2, markersize=5)
    
    ax2.set_xlabel('Temperature (°C)', fontsize=12)
    ax2.set_ylabel('Flexural Strength (MPa)', fontsize=12)
    ax2.set_title('(b) Flexural Strength', fontsize=12, fontweight='bold')
    ax2.legend(loc='best', framealpha=0.9, fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, 1050])
    
    plt.tight_layout()
    
    # Save figure
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'figures')
    os.makedirs(output_dir, exist_ok=True)
    
    plt.savefig(os.path.join(output_dir, 'mechanical_properties.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(output_dir, 'mechanical_properties.pdf'), bbox_inches='tight')
    
    print("✓ Generated mechanical_properties.png and mechanical_properties.pdf")
    print(f"  Saved to: {output_dir}")


if __name__ == '__main__':
    plot_mechanical_properties()
