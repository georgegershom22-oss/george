#!/usr/bin/env python3
"""
Plot thermal cycling degradation data.

DISCLAIMER: All data is SYNTHETIC/ILLUSTRATIVE, based on published literature ranges.

Output: 2-panel figure showing peak power and degradation vs cycles
"""

import csv
import os
import matplotlib.pyplot as plt
import matplotlib as mpl

# Set publication-quality defaults
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.size'] = 12
mpl.rcParams['figure.dpi'] = 300

def load_thermal_cycling_data():
    """Load thermal cycling degradation data from CSV."""
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', '07_thermal_cycling_degradation.csv')
    
    # Skip comment lines
    with open(data_file, 'r') as f:
        lines = [line for line in f if not line.startswith('#')]
    
    # Parse CSV
    reader = csv.DictReader(lines)
    
    data = {5: {'cycles': [], 'power': [], 'deg': []},
            10: {'cycles': [], 'power': [], 'deg': []},
            20: {'cycles': [], 'power': [], 'deg': []}}
    
    for row in reader:
        ramp = int(row['Ramp_Rate_C_per_min'])
        data[ramp]['cycles'].append(int(row['Cycle_Number']))
        data[ramp]['power'].append(float(row['Peak_Power_W_per_cm2']))
        data[ramp]['deg'].append(float(row['Cumulative_Degradation_pct']))
    
    return data


def plot_thermal_cycling():
    """Create 2-panel figure with thermal cycling degradation."""
    data = load_thermal_cycling_data()
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('SYNTHETIC DATA — Based on Literature Ranges\nThermal Cycling Degradation (25 ↔ 800°C)',
                 fontsize=14, fontweight='bold', y=0.98)
    
    # Panel 1: Peak power vs cycles
    ax1 = axes[0]
    ax1.plot(data[5]['cycles'], data[5]['power'], '-o', label='5°C/min', linewidth=2, markersize=6)
    ax1.plot(data[10]['cycles'], data[10]['power'], '-s', label='10°C/min', linewidth=2, markersize=6)
    ax1.plot(data[20]['cycles'], data[20]['power'], '-^', label='20°C/min', linewidth=2, markersize=6)
    
    ax1.set_xlabel('Cycle Number', fontsize=12)
    ax1.set_ylabel('Peak Power Density (W cm⁻²)', fontsize=12)
    ax1.set_title('(a) Performance Degradation', fontsize=12, fontweight='bold')
    ax1.legend(title='Ramp Rate', loc='best', framealpha=0.9, fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 105])
    ax1.set_ylim([0, 0.7])
    
    # Panel 2: Cumulative degradation percentage
    ax2 = axes[1]
    ax2.plot(data[5]['cycles'], data[5]['deg'], '-o', label='5°C/min', linewidth=2, markersize=6)
    ax2.plot(data[10]['cycles'], data[10]['deg'], '-s', label='10°C/min', linewidth=2, markersize=6)
    ax2.plot(data[20]['cycles'], data[20]['deg'], '-^', label='20°C/min', linewidth=2, markersize=6)
    
    ax2.set_xlabel('Cycle Number', fontsize=12)
    ax2.set_ylabel('Cumulative Degradation (%)', fontsize=12)
    ax2.set_title('(b) Cumulative Degradation', fontsize=12, fontweight='bold')
    ax2.legend(title='Ramp Rate', loc='best', framealpha=0.9, fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, 105])
    ax2.set_ylim([0, None])
    
    # Add note
    ax1.text(0.98, 0.98, 'Operating: 800°C, 0.5 A/cm²\nH₂ 97% + H₂O 3%',
            transform=ax1.transAxes, fontsize=9, verticalalignment='top',
            horizontalalignment='right', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    
    # Save figure
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'figures')
    os.makedirs(output_dir, exist_ok=True)
    
    plt.savefig(os.path.join(output_dir, 'thermal_cycling.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(output_dir, 'thermal_cycling.pdf'), bbox_inches='tight')
    
    print("✓ Generated thermal_cycling.png and thermal_cycling.pdf")
    print(f"  Saved to: {output_dir}")


if __name__ == '__main__':
    plot_thermal_cycling()
