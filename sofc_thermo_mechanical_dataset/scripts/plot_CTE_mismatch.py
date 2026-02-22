#!/usr/bin/env python3
"""
Plot CTE comparison and interfacial thermal stress.

DISCLAIMER: All data is SYNTHETIC/ILLUSTRATIVE, based on published literature ranges.

Output: 2-panel figure showing CTE values and thermal stress at interfaces
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
    'Crofer': '#8c564b'
}

def load_CTE_data():
    """Load CTE mismatch data from CSV."""
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', '05_CTE_mismatch_thermal_stress.csv')
    
    # Skip comment lines
    with open(data_file, 'r') as f:
        lines = [line for line in f if not line.startswith('#')]
    
    # Parse CSV
    reader = csv.DictReader(lines)
    
    data = {
        'T': [],
        'CTE_8YSZ': [], 'CTE_GDC': [], 'CTE_NiYSZ': [],
        'CTE_LSCF': [], 'CTE_LSM': [], 'CTE_Crofer': [],
        'stress_anode': [], 'stress_LSCF': [], 'stress_LSM': []
    }
    
    for row in reader:
        data['T'].append(float(row['Temperature_C']))
        data['CTE_8YSZ'].append(float(row['CTE_8YSZ']))
        data['CTE_GDC'].append(float(row['CTE_GDC']))
        data['CTE_NiYSZ'].append(float(row['CTE_NiYSZ']))
        data['CTE_LSCF'].append(float(row['CTE_LSCF']))
        data['CTE_LSM'].append(float(row['CTE_LSM']))
        data['CTE_Crofer'].append(float(row['CTE_Crofer']))
        data['stress_anode'].append(float(row['Thermal_Stress_Anode_Interface_MPa']))
        data['stress_LSCF'].append(float(row['Thermal_Stress_LSCF_Interface_MPa']))
        data['stress_LSM'].append(float(row['Thermal_Stress_LSM_Interface_MPa']))
    
    return data


def plot_CTE_mismatch():
    """Create 2-panel figure with CTE comparison and thermal stress."""
    data = load_CTE_data()
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('SYNTHETIC DATA — Based on Literature Ranges\nCTE Mismatch and Interfacial Thermal Stress',
                 fontsize=14, fontweight='bold', y=0.98)
    
    # Panel 1: CTE comparison
    ax1 = axes[0]
    ax1.plot(data['T'], data['CTE_8YSZ'], '-o', label='8YSZ', color=COLORS['8YSZ'], linewidth=2, markersize=5)
    ax1.plot(data['T'], data['CTE_GDC'], '-s', label='GDC', color=COLORS['GDC'], linewidth=2, markersize=5)
    ax1.plot(data['T'], data['CTE_NiYSZ'], '-^', label='Ni-YSZ', color=COLORS['Ni-YSZ'], linewidth=2, markersize=5)
    ax1.plot(data['T'], data['CTE_LSCF'], '-d', label='LSCF', color=COLORS['LSCF'], linewidth=2, markersize=5)
    ax1.plot(data['T'], data['CTE_LSM'], '-v', label='LSM', color=COLORS['LSM'], linewidth=2, markersize=5)
    ax1.plot(data['T'], data['CTE_Crofer'], '-<', label='Crofer 22 APU', color=COLORS['Crofer'], linewidth=2, markersize=5)
    
    ax1.set_xlabel('Temperature (°C)', fontsize=12)
    ax1.set_ylabel('CTE (×10⁻⁶ K⁻¹)', fontsize=12)
    ax1.set_title('(a) Coefficient of Thermal Expansion', fontsize=12, fontweight='bold')
    ax1.legend(loc='best', framealpha=0.9, fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 1050])
    
    # Panel 2: Interfacial thermal stress
    ax2 = axes[1]
    ax2.plot(data['T'], data['stress_anode'], '-o', label='Anode/Electrolyte (Ni-YSZ/8YSZ)',
            color=COLORS['Ni-YSZ'], linewidth=2, markersize=5)
    ax2.plot(data['T'], data['stress_LSCF'], '-s', label='Cathode/Electrolyte (LSCF/8YSZ)',
            color=COLORS['LSCF'], linewidth=2, markersize=5)
    ax2.plot(data['T'], data['stress_LSM'], '-^', label='Cathode/Electrolyte (LSM/8YSZ)',
            color=COLORS['LSM'], linewidth=2, markersize=5)
    
    ax2.set_xlabel('Temperature (°C)', fontsize=12)
    ax2.set_ylabel('Biaxial Thermal Stress (MPa)', fontsize=12)
    ax2.set_title('(b) Interfacial Thermal Stress', fontsize=12, fontweight='bold')
    ax2.legend(loc='best', framealpha=0.9, fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, 1050])
    ax2.set_ylim([0, None])
    
    # Add note
    ax2.text(0.98, 0.98, 'Cooling from 1400°C\nsintering temperature',
            transform=ax2.transAxes, fontsize=9, verticalalignment='top',
            horizontalalignment='right', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    
    # Save figure
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'figures')
    os.makedirs(output_dir, exist_ok=True)
    
    plt.savefig(os.path.join(output_dir, 'CTE_mismatch.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(output_dir, 'CTE_mismatch.pdf'), bbox_inches='tight')
    
    print("✓ Generated CTE_mismatch.png and CTE_mismatch.pdf")
    print(f"  Saved to: {output_dir}")


if __name__ == '__main__':
    plot_CTE_mismatch()
