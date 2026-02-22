#!/usr/bin/env python3
"""
Plot creep strain vs time curves at different stress and temperature conditions.
Generates publication-quality figure: fig04_creep_curves.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Define paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
FIGURES_DIR = SCRIPT_DIR.parent / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

def plot_creep_curves():
    """Create creep strain vs time plot for multiple conditions."""
    # Read data
    df = pd.read_csv(DATA_DIR / '04_creep_curves.csv', comment='#')
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Define curves to plot with labels and colors
    curves = [
        ('Strain_pct_5MPa_750C', '5 MPa, 750°C', 0),
        ('Strain_pct_10MPa_750C', '10 MPa, 750°C', 1),
        ('Strain_pct_10MPa_800C', '10 MPa, 800°C', 2),
        ('Strain_pct_15MPa_800C', '15 MPa, 800°C', 3),
        ('Strain_pct_10MPa_850C', '10 MPa, 850°C', 4),
        ('Strain_pct_20MPa_850C', '20 MPa, 850°C', 5),
    ]
    
    # Use warm colormap
    cmap = plt.cm.YlOrRd
    colors = [cmap(0.3 + i * 0.12) for i in range(len(curves))]
    
    for (col, label, idx) in curves:
        ax.plot(df['Time_hours'], df[col], label=label, 
               color=colors[idx], linewidth=2.5, marker='o', 
               markersize=4, markevery=15)
    
    ax.set_xlabel('Time (hours)', fontsize=12)
    ax.set_ylabel('Creep Strain (%)', fontsize=12)
    ax.set_title('Creep Strain Evolution (Ni-YSZ Anode)\n(Synthetic/Illustrative Data)', 
                fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11, loc='upper left', framealpha=0.9)
    ax.set_xlim(0, 500)
    ax.set_ylim(0, None)
    
    # Add annotation
    ax.text(0.98, 0.05, 'Norton Power Law: ε = A·t^b', 
           transform=ax.transAxes, fontsize=10, 
           verticalalignment='bottom', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # Save figure
    output_path = FIGURES_DIR / 'fig04_creep_curves.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved {output_path.name}")
    plt.close()


if __name__ == "__main__":
    plot_creep_curves()
