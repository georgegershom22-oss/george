#!/usr/bin/env python3
"""
Plot stress evolution during thermal cycle (heating, dwell, cooling).
Generates publication-quality figure: fig07_stress_evolution.png
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Define paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
FIGURES_DIR = SCRIPT_DIR.parent / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

def plot_stress_evolution():
    """Create stress evolution plot with phase shading."""
    # Read data
    df = pd.read_csv(DATA_DIR / '10_stress_evolution_thermal_cycle.csv', comment='#')
    
    # Create figure with two subplots (stress and temperature)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, 
                                    gridspec_kw={'height_ratios': [3, 1]})
    
    # Plot 1: Von Mises stress for all layers
    components = [
        ('VonMises_Anode_MPa', 'Anode (Ni-YSZ)', '#2ca02c'),
        ('VonMises_Electrolyte_MPa', 'Electrolyte (8YSZ)', '#1f77b4'),
        ('VonMises_Cathode_MPa', 'Cathode (LSCF)', '#d62728'),
        ('VonMises_Interconnect_MPa', 'Interconnect (Crofer)', '#8c564b'),
    ]
    
    for col, label, color in components:
        ax1.plot(df['Time_s'], df[col], label=label, 
                color=color, linewidth=2.5)
    
    # Add phase shading
    heating_end = 2600
    dwell_end = 6200
    ax1.axvspan(0, heating_end, alpha=0.15, color='orange', label='Heating')
    ax1.axvspan(heating_end, dwell_end, alpha=0.15, color='green', label='Dwell (800°C)')
    ax1.axvspan(dwell_end, df['Time_s'].max(), alpha=0.15, color='blue', label='Cooling')
    
    ax1.set_ylabel('Von Mises Stress (MPa)', fontsize=12)
    ax1.set_title('Stress Evolution During Thermal Cycle (Synthetic/Illustrative Data)', 
                 fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10, loc='upper left', ncol=2)
    ax1.set_ylim(0, None)
    
    # Plot 2: Temperature profile
    ax2.plot(df['Time_s'], df['Temperature_C'], 
            color='red', linewidth=2.5)
    ax2.fill_between(df['Time_s'], df['Temperature_C'], alpha=0.3, color='red')
    
    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Temperature (°C)', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 850)
    
    # Add phase labels on temperature plot
    ax2.text(heating_end/2, 850, 'Heating', ha='center', va='top', fontsize=11, fontweight='bold')
    ax2.text((heating_end+dwell_end)/2, 850, 'Dwell', ha='center', va='top', fontsize=11, fontweight='bold')
    ax2.text((dwell_end+df['Time_s'].max())/2, 850, 'Cooling', ha='center', va='top', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    
    # Save figure
    output_path = FIGURES_DIR / 'fig07_stress_evolution.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved {output_path.name}")
    plt.close()


if __name__ == "__main__":
    plot_stress_evolution()
