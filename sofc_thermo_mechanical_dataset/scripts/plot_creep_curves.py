#!/usr/bin/env python3
"""
Plot creep strain vs time curves for Ni-YSZ anode at different stress-temperature conditions.

DISCLAIMER: All data is SYNTHETIC/ILLUSTRATIVE, based on published literature ranges.

Output: Single plot with 5 creep curves
"""

import csv
import os
import matplotlib.pyplot as plt
import matplotlib as mpl

# Set publication-quality defaults
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.size'] = 12
mpl.rcParams['figure.dpi'] = 300

def load_creep_data():
    """Load creep curves data from CSV."""
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', '04_creep_curves_NiYSZ.csv')
    
    # Skip comment lines
    with open(data_file, 'r') as f:
        lines = [line for line in f if not line.startswith('#')]
    
    # Parse CSV
    reader = csv.DictReader(lines)
    
    data = {
        'time': [],
        '5MPa_750C': [],
        '10MPa_800C': [],
        '15MPa_800C': [],
        '20MPa_850C': [],
        '10MPa_900C': []
    }
    
    for row in reader:
        data['time'].append(float(row['Time_hours']))
        data['5MPa_750C'].append(float(row['Strain_pct_5MPa_750C']))
        data['10MPa_800C'].append(float(row['Strain_pct_10MPa_800C']))
        data['15MPa_800C'].append(float(row['Strain_pct_15MPa_800C']))
        data['20MPa_850C'].append(float(row['Strain_pct_20MPa_850C']))
        data['10MPa_900C'].append(float(row['Strain_pct_10MPa_900C']))
    
    return data


def plot_creep_curves():
    """Create single plot with all creep curves."""
    data = load_creep_data()
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Plot all conditions
    ax.plot(data['time'], data['5MPa_750C'], '-o', label='5 MPa, 750°C', 
            linewidth=2, markersize=3, markevery=10)
    ax.plot(data['time'], data['10MPa_800C'], '-s', label='10 MPa, 800°C',
            linewidth=2, markersize=3, markevery=10)
    ax.plot(data['time'], data['15MPa_800C'], '-^', label='15 MPa, 800°C',
            linewidth=2, markersize=3, markevery=10)
    ax.plot(data['time'], data['20MPa_850C'], '-d', label='20 MPa, 850°C',
            linewidth=2, markersize=3, markevery=10)
    ax.plot(data['time'], data['10MPa_900C'], '-v', label='10 MPa, 900°C',
            linewidth=2, markersize=3, markevery=10)
    
    ax.set_xlabel('Time (hours)', fontsize=12)
    ax.set_ylabel('Creep Strain (%)', fontsize=12)
    ax.set_title('SYNTHETIC DATA — Based on Literature Ranges\nCreep Curves for Ni-8YSZ Anode (Norton Power-Law Model)',
                 fontsize=13, fontweight='bold')
    ax.legend(loc='best', framealpha=0.9, fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 500])
    ax.set_ylim([0, None])
    
    # Add note
    ax.text(0.98, 0.02, 'Material: Ni-8YSZ (40 vol% Ni, 30% porosity)\nAtmosphere: H₂-H₂O',
            transform=ax.transAxes, fontsize=9, verticalalignment='bottom',
            horizontalalignment='right', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    
    # Save figure
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'figures')
    os.makedirs(output_dir, exist_ok=True)
    
    plt.savefig(os.path.join(output_dir, 'creep_curves.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(output_dir, 'creep_curves.pdf'), bbox_inches='tight')
    
    print("✓ Generated creep_curves.png and creep_curves.pdf")
    print(f"  Saved to: {output_dir}")


if __name__ == '__main__':
    plot_creep_curves()
