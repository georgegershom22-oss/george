#!/usr/bin/env python3
"""
Plot thermal cycling degradation: power and voltage vs cycle number.
Generates publication-quality figure: fig06_thermal_cycling_degradation.png
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Define paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
FIGURES_DIR = SCRIPT_DIR.parent / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

def plot_thermal_cycling():
    """Create two-panel figure showing degradation vs thermal cycles."""
    # Read data
    df = pd.read_csv(DATA_DIR / '07_thermal_cycling_degradation.csv', comment='#')
    
    # Create figure with two subplots
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    # Ramp rate colors
    ramp_rates = [5, 10, 20]
    colors = ['#27ae60', '#f39c12', '#e74c3c']
    markers = ['o', 's', '^']
    
    # Plot 1: Peak Power vs Cycles
    ax1 = axes[0]
    for i, rr in enumerate(ramp_rates):
        data = df[df['Ramp_Rate_C_per_min'] == rr]
        ax1.plot(data['Cycle'], data['Peak_Power_W_per_cm2'], 
                label=f'{rr} °C/min', color=colors[i], linewidth=2.5,
                marker=markers[i], markersize=5, markevery=5)
    
    ax1.set_ylabel('Peak Power Density (W cm⁻²)', fontsize=12)
    ax1.set_title('(a) Power Degradation vs Thermal Cycles', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=11, loc='best', title='Ramp Rate')
    ax1.set_ylim(0.3, 0.7)
    
    # Plot 2: Voltage vs Cycles
    ax2 = axes[1]
    for i, rr in enumerate(ramp_rates):
        data = df[df['Ramp_Rate_C_per_min'] == rr]
        ax2.plot(data['Cycle'], data['Voltage_at_0p5Acm2_V'], 
                label=f'{rr} °C/min', color=colors[i], linewidth=2.5,
                marker=markers[i], markersize=5, markevery=5)
    
    ax2.set_xlabel('Cycle Number', fontsize=12)
    ax2.set_ylabel('Voltage at 0.5 A/cm² (V)', fontsize=12)
    ax2.set_title('(b) Voltage Degradation vs Thermal Cycles', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=11, loc='best', title='Ramp Rate')
    ax2.set_ylim(0.4, 0.8)
    
    # Overall title
    fig.suptitle('Thermal Cycling Degradation (25°C ↔ 800°C)\n(Synthetic/Illustrative Data)', 
                 fontsize=14, fontweight='bold', y=0.995)
    
    plt.tight_layout()
    
    # Save figure
    output_path = FIGURES_DIR / 'fig06_thermal_cycling_degradation.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved {output_path.name}")
    plt.close()


if __name__ == "__main__":
    plot_thermal_cycling()
