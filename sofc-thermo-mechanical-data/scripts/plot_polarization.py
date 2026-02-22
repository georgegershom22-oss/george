#!/usr/bin/env python3
"""
Plot I-V and I-P polarization curves at three temperatures.
Generates publication-quality figure: fig05_polarization_curves.png
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Define paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
FIGURES_DIR = SCRIPT_DIR.parent / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

def plot_polarization():
    """Create dual-axis I-V and I-P polarization curves."""
    # Read data
    df = pd.read_csv(DATA_DIR / '06_polarization_curves.csv', comment='#')
    
    # Create figure
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Temperature colors
    temps = [750, 800, 850]
    colors = ['#3498db', '#e74c3c', '#f39c12']
    
    # Plot I-V curves (solid lines)
    for i, T in enumerate(temps):
        ax1.plot(df['Current_Density_A_per_cm2'], df[f'Voltage_{T}C_V'], 
                color=colors[i], linewidth=2.5, linestyle='-', 
                label=f'{T}°C')
    
    ax1.set_xlabel('Current Density (A cm⁻²)', fontsize=12)
    ax1.set_ylabel('Cell Voltage (V)', fontsize=12, color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.set_ylim(0, 1.2)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=11, title='Temperature')
    
    # Create second y-axis for power density
    ax2 = ax1.twinx()
    
    # Plot I-P curves (dashed lines)
    for i, T in enumerate(temps):
        ax2.plot(df['Current_Density_A_per_cm2'], df[f'Power_{T}C_W_per_cm2'], 
                color=colors[i], linewidth=2.5, linestyle='--')
    
    ax2.set_ylabel('Power Density (W cm⁻²)', fontsize=12, color='black')
    ax2.tick_params(axis='y', labelcolor='black')
    ax2.set_ylim(0, None)
    
    # Title
    ax1.set_title('Polarization Curves: Voltage (solid) and Power (dashed)\n(Synthetic/Illustrative Data)', 
                 fontsize=13, fontweight='bold')
    
    # Add annotations for line styles
    ax1.text(0.05, 0.95, 'Solid lines: I-V\nDashed lines: I-P', 
            transform=ax1.transAxes, fontsize=10, 
            verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Save figure
    output_path = FIGURES_DIR / 'fig05_polarization_curves.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved {output_path.name}")
    plt.close()


if __name__ == "__main__":
    plot_polarization()
