#!/usr/bin/env python3
"""
Plot polarization (I-V) and power density curves at three temperatures.

DISCLAIMER: All data is SYNTHETIC/ILLUSTRATIVE, based on published literature ranges.

Output: 2-panel figure showing voltage and power vs current density
"""

import csv
import os
import matplotlib.pyplot as plt
import matplotlib as mpl

# Set publication-quality defaults
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.size'] = 12
mpl.rcParams['figure.dpi'] = 300

def load_polarization_data():
    """Load polarization curves data from CSV."""
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', '06_polarization_curves.csv')
    
    # Skip comment lines
    with open(data_file, 'r') as f:
        lines = [line for line in f if not line.startswith('#')]
    
    # Parse CSV
    reader = csv.DictReader(lines)
    
    data = {
        'i': [],
        'V_750': [], 'P_750': [],
        'V_800': [], 'P_800': [],
        'V_850': [], 'P_850': []
    }
    
    for row in reader:
        data['i'].append(float(row['Current_Density_A_per_cm2']))
        data['V_750'].append(float(row['Voltage_750C_V']))
        data['P_750'].append(float(row['Power_750C_W_per_cm2']))
        data['V_800'].append(float(row['Voltage_800C_V']))
        data['P_800'].append(float(row['Power_800C_W_per_cm2']))
        data['V_850'].append(float(row['Voltage_850C_V']))
        data['P_850'].append(float(row['Power_850C_W_per_cm2']))
    
    return data


def plot_polarization_curves():
    """Create 2-panel figure with I-V and power density curves."""
    data = load_polarization_data()
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('SYNTHETIC DATA — Based on Literature Ranges\nPolarization Curves at Three Operating Temperatures',
                 fontsize=14, fontweight='bold', y=0.98)
    
    # Panel 1: I-V curves
    ax1 = axes[0]
    ax1.plot(data['i'], data['V_750'], '-o', label='750°C', linewidth=2, markersize=4, markevery=5)
    ax1.plot(data['i'], data['V_800'], '-s', label='800°C', linewidth=2, markersize=4, markevery=5)
    ax1.plot(data['i'], data['V_850'], '-^', label='850°C', linewidth=2, markersize=4, markevery=5)
    
    ax1.set_xlabel('Current Density (A cm⁻²)', fontsize=12)
    ax1.set_ylabel('Cell Voltage (V)', fontsize=12)
    ax1.set_title('(a) Current-Voltage Characteristics', fontsize=12, fontweight='bold')
    ax1.legend(loc='best', framealpha=0.9, fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 1.25])
    ax1.set_ylim([0, 1.2])
    
    # Panel 2: Power density curves
    ax2 = axes[1]
    ax2.plot(data['i'], data['P_750'], '-o', label='750°C', linewidth=2, markersize=4, markevery=5)
    ax2.plot(data['i'], data['P_800'], '-s', label='800°C', linewidth=2, markersize=4, markevery=5)
    ax2.plot(data['i'], data['P_850'], '-^', label='850°C', linewidth=2, markersize=4, markevery=5)
    
    ax2.set_xlabel('Current Density (A cm⁻²)', fontsize=12)
    ax2.set_ylabel('Power Density (W cm⁻²)', fontsize=12)
    ax2.set_title('(b) Power Density', fontsize=12, fontweight='bold')
    ax2.legend(loc='best', framealpha=0.9, fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, 1.25])
    ax2.set_ylim([0, None])
    
    # Add note
    ax1.text(0.02, 0.02, 'Fuel: H₂ 97% + H₂O 3%\nAir: O₂ 21% + N₂ 79%',
            transform=ax1.transAxes, fontsize=9, verticalalignment='bottom',
            horizontalalignment='left', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    
    # Save figure
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'figures')
    os.makedirs(output_dir, exist_ok=True)
    
    plt.savefig(os.path.join(output_dir, 'polarization_curves.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(output_dir, 'polarization_curves.pdf'), bbox_inches='tight')
    
    print("✓ Generated polarization_curves.png and polarization_curves.pdf")
    print(f"  Saved to: {output_dir}")


if __name__ == '__main__':
    plot_polarization_curves()
