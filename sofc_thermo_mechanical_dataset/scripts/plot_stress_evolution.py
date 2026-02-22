#!/usr/bin/env python3
"""
Plot stress evolution during thermal cycle (heating-dwell-cooling).

DISCLAIMER: All data is SYNTHETIC/ILLUSTRATIVE, based on published literature ranges.

Output: 2-panel stacked figure showing temperature profile and stress in layers
"""

import csv
import os
import matplotlib.pyplot as plt
import matplotlib as mpl

# Set publication-quality defaults
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.size'] = 12
mpl.rcParams['figure.dpi'] = 300

def load_stress_evolution_data():
    """Load stress evolution data from CSV."""
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', '10_stress_evolution_thermal_cycle.csv')
    
    # Skip comment lines
    with open(data_file, 'r') as f:
        lines = [line for line in f if not line.startswith('#')]
    
    # Parse CSV
    reader = csv.DictReader(lines)
    
    data = {
        'time': [], 'temp': [], 'phase': [],
        'VM_anode': [], 'VM_electrolyte': [],
        'VM_cathode': [], 'VM_interconnect': []
    }
    
    for row in reader:
        data['time'].append(float(row['Time_s']) / 3600)  # Convert to hours
        data['temp'].append(float(row['Temperature_C']))
        data['phase'].append(row['Phase'])
        data['VM_anode'].append(float(row['VonMises_Anode_MPa']))
        data['VM_electrolyte'].append(float(row['VonMises_Electrolyte_MPa']))
        data['VM_cathode'].append(float(row['VonMises_Cathode_MPa']))
        data['VM_interconnect'].append(float(row['VonMises_Interconnect_MPa']))
    
    return data


def plot_stress_evolution():
    """Create 2-panel stacked figure with temperature and stress evolution."""
    data = load_stress_evolution_data()
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.suptitle('SYNTHETIC DATA — Based on Literature Ranges\nStress Evolution During Thermal Cycle',
                 fontsize=14, fontweight='bold', y=0.96)
    
    # Panel 1: Temperature profile
    ax1 = axes[0]
    ax1.plot(data['time'], data['temp'], '-k', linewidth=2.5)
    ax1.set_ylabel('Temperature (°C)', fontsize=12)
    ax1.set_title('(a) Thermal Cycle Profile', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0, 850])
    
    # Shade phases
    heating_end = 2600 / 3600
    dwell_end = 6200 / 3600
    ax1.axvspan(0, heating_end, alpha=0.2, color='red', label='Heating')
    ax1.axvspan(heating_end, dwell_end, alpha=0.2, color='yellow', label='Dwell')
    ax1.axvspan(dwell_end, data['time'][-1], alpha=0.2, color='blue', label='Cooling')
    ax1.legend(loc='upper left', fontsize=10)
    
    # Panel 2: Von Mises stress in each layer
    ax2 = axes[1]
    ax2.plot(data['time'], data['VM_anode'], '-o', label='Anode', linewidth=2, markersize=4, markevery=5)
    ax2.plot(data['time'], data['VM_electrolyte'], '-s', label='Electrolyte', linewidth=2, markersize=4, markevery=5)
    ax2.plot(data['time'], data['VM_cathode'], '-^', label='Cathode', linewidth=2, markersize=4, markevery=5)
    ax2.plot(data['time'], data['VM_interconnect'], '-d', label='Interconnect', linewidth=2, markersize=4, markevery=5)
    
    ax2.set_xlabel('Time (hours)', fontsize=12)
    ax2.set_ylabel('Von Mises Stress (MPa)', fontsize=12)
    ax2.set_title('(b) Stress Evolution in Each Layer', fontsize=12, fontweight='bold')
    ax2.legend(loc='best', framealpha=0.9, fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, data['time'][-1]])
    ax2.set_ylim([0, None])
    
    plt.tight_layout()
    
    # Save figure
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'figures')
    os.makedirs(output_dir, exist_ok=True)
    
    plt.savefig(os.path.join(output_dir, 'stress_evolution.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(output_dir, 'stress_evolution.pdf'), bbox_inches='tight')
    
    print("✓ Generated stress_evolution.png and stress_evolution.pdf")
    print(f"  Saved to: {output_dir}")


if __name__ == '__main__':
    plot_stress_evolution()
