#!/usr/bin/env python3
"""
Plot thermal properties (CTE, thermal conductivity, specific heat) vs temperature.

DISCLAIMER: All data is SYNTHETIC/ILLUSTRATIVE, based on published literature ranges.

Output: 3-panel figure showing temperature-dependent thermal properties
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

def load_thermal_data():
    """Load thermal properties data from CSV."""
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', '01_thermal_properties.csv')
    
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
            materials_data[mat] = {'T': [], 'k': [], 'Cp': [], 'CTE': []}
        
        materials_data[mat]['T'].append(float(row['Temperature_C']))
        materials_data[mat]['k'].append(float(row['Thermal_Conductivity_W_per_mK']))
        materials_data[mat]['Cp'].append(float(row['Specific_Heat_J_per_kgK']))
        materials_data[mat]['CTE'].append(float(row['CTE_1e-6_per_K']))
    
    return materials_data


def plot_thermal_properties():
    """Create 3-panel figure with thermal properties."""
    data = load_thermal_data()
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('SYNTHETIC DATA — Based on Literature Ranges\nThermal Properties of SOFC Materials', 
                 fontsize=14, fontweight='bold', y=1.00)
    
    # Panel 1: Coefficient of Thermal Expansion (CTE)
    ax1 = axes[0]
    for mat_name, mat_data in data.items():
        ax1.plot(mat_data['T'], mat_data['CTE'], '-o', label=mat_name, 
                color=COLORS[mat_name], linewidth=2, markersize=4)
    
    ax1.set_xlabel('Temperature (°C)', fontsize=12)
    ax1.set_ylabel('CTE (×10⁻⁶ K⁻¹)', fontsize=12)
    ax1.set_title('(a) Coefficient of Thermal Expansion', fontsize=12, fontweight='bold')
    ax1.legend(loc='best', framealpha=0.9, fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 1050])
    
    # Panel 2: Thermal Conductivity
    ax2 = axes[1]
    for mat_name, mat_data in data.items():
        ax2.plot(mat_data['T'], mat_data['k'], '-s', label=mat_name,
                color=COLORS[mat_name], linewidth=2, markersize=4)
    
    ax2.set_xlabel('Temperature (°C)', fontsize=12)
    ax2.set_ylabel('Thermal Conductivity (W m⁻¹ K⁻¹)', fontsize=12)
    ax2.set_title('(b) Thermal Conductivity', fontsize=12, fontweight='bold')
    ax2.legend(loc='best', framealpha=0.9, fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, 1050])
    
    # Panel 3: Specific Heat Capacity
    ax3 = axes[2]
    for mat_name, mat_data in data.items():
        ax3.plot(mat_data['T'], mat_data['Cp'], '-^', label=mat_name,
                color=COLORS[mat_name], linewidth=2, markersize=4)
    
    ax3.set_xlabel('Temperature (°C)', fontsize=12)
    ax3.set_ylabel('Specific Heat (J kg⁻¹ K⁻¹)', fontsize=12)
    ax3.set_title('(c) Specific Heat Capacity', fontsize=12, fontweight='bold')
    ax3.legend(loc='best', framealpha=0.9, fontsize=10)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim([0, 1050])
    
    plt.tight_layout()
    
    # Save figure
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'figures')
    os.makedirs(output_dir, exist_ok=True)
    
    plt.savefig(os.path.join(output_dir, 'thermal_properties.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(output_dir, 'thermal_properties.pdf'), bbox_inches='tight')
    
    print("✓ Generated thermal_properties.png and thermal_properties.pdf")
    print(f"  Saved to: {output_dir}")


if __name__ == '__main__':
    plot_thermal_properties()
