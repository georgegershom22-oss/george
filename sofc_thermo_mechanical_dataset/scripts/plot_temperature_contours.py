#!/usr/bin/env python3
"""
Plot 2D temperature distribution contours on cell surface.

DISCLAIMER: All data is SYNTHETIC/ILLUSTRATIVE, based on published literature ranges.

Output: 3-panel contour plot showing temperature fields
"""

import csv
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

# Set publication-quality defaults
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.size'] = 12
mpl.rcParams['figure.dpi'] = 300

def load_temperature_data():
    """Load 2D temperature distribution data from CSV."""
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', '09_temperature_distribution.csv')
    
    # Skip comment lines
    with open(data_file, 'r') as f:
        lines = [line for line in f if not line.startswith('#')]
    
    # Parse CSV
    reader = csv.DictReader(lines)
    
    data = {'x': [], 'y': [], 'T_ss': [], 'T_startup': [], 'T_load': []}
    
    for row in reader:
        data['x'].append(float(row['Position_x_mm']))
        data['y'].append(float(row['Position_y_mm']))
        data['T_ss'].append(float(row['T_SteadyState_K']))
        data['T_startup'].append(float(row['T_Startup_K']))
        data['T_load'].append(float(row['T_LoadStep_K']))
    
    return data


def plot_temperature_contours():
    """Create 3-panel contour plots for temperature distribution."""
    data = load_temperature_data()
    
    # Reshape data to 2D grid (21x21 grid from 0-100mm in 5mm steps)
    X = np.array(data['x']).reshape(21, 21)
    Y = np.array(data['y']).reshape(21, 21)
    T_ss = np.array(data['T_ss']).reshape(21, 21)
    T_startup = np.array(data['T_startup']).reshape(21, 21)
    T_load = np.array(data['T_load']).reshape(21, 21)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('SYNTHETIC DATA — Based on Literature Ranges\n2D Temperature Distribution on Cell Surface (100×100 mm)',
                 fontsize=14, fontweight='bold', y=0.98)
    
    # Common colormap
    cmap = 'hot'
    
    # Panel 1: Steady-state
    ax1 = axes[0]
    contour1 = ax1.contourf(X, Y, T_ss, levels=20, cmap=cmap)
    cbar1 = plt.colorbar(contour1, ax=ax1)
    cbar1.set_label('Temperature (K)', fontsize=11)
    ax1.contour(X, Y, T_ss, levels=10, colors='black', linewidths=0.5, alpha=0.3)
    ax1.set_xlabel('x-position (mm)', fontsize=12)
    ax1.set_ylabel('y-position (mm)', fontsize=12)
    ax1.set_title('(a) Steady-State Operation', fontsize=12, fontweight='bold')
    ax1.set_aspect('equal')
    
    # Panel 2: Startup
    ax2 = axes[1]
    contour2 = ax2.contourf(X, Y, T_startup, levels=20, cmap=cmap)
    cbar2 = plt.colorbar(contour2, ax=ax2)
    cbar2.set_label('Temperature (K)', fontsize=11)
    ax2.contour(X, Y, T_startup, levels=10, colors='black', linewidths=0.5, alpha=0.3)
    ax2.set_xlabel('x-position (mm)', fontsize=12)
    ax2.set_ylabel('y-position (mm)', fontsize=12)
    ax2.set_title('(b) Startup (Transient)', fontsize=12, fontweight='bold')
    ax2.set_aspect('equal')
    
    # Panel 3: Load step
    ax3 = axes[2]
    contour3 = ax3.contourf(X, Y, T_load, levels=20, cmap=cmap)
    cbar3 = plt.colorbar(contour3, ax=ax3)
    cbar3.set_label('Temperature (K)', fontsize=11)
    ax3.contour(X, Y, T_load, levels=10, colors='black', linewidths=0.5, alpha=0.3)
    ax3.set_xlabel('x-position (mm)', fontsize=12)
    ax3.set_ylabel('y-position (mm)', fontsize=12)
    ax3.set_title('(c) Load Step (0.3 → 0.7 A/cm²)', fontsize=12, fontweight='bold')
    ax3.set_aspect('equal')
    
    plt.tight_layout()
    
    # Save figure
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'figures')
    os.makedirs(output_dir, exist_ok=True)
    
    plt.savefig(os.path.join(output_dir, 'temperature_contours.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(output_dir, 'temperature_contours.pdf'), bbox_inches='tight')
    
    print("✓ Generated temperature_contours.png and temperature_contours.pdf")
    print(f"  Saved to: {output_dir}")


if __name__ == '__main__':
    plot_temperature_contours()
