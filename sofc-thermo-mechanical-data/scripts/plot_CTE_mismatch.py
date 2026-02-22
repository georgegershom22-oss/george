#!/usr/bin/env python3
"""
Plot CTE comparison as grouped bar chart at 25°C and 800°C.
Generates publication-quality figure: fig08_CTE_mismatch_bar.png
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

# Material colors
COLORS = {
    '8YSZ': '#1f77b4',
    'GDC': '#ff7f0e',
    'Ni-YSZ': '#2ca02c',
    'LSCF': '#d62728',
    'LSM': '#9467bd',
    'Crofer22APU': '#8c564b'
}

def plot_CTE_mismatch():
    """Create grouped bar chart of CTE values at two temperatures."""
    # Read data
    df = pd.read_csv(DATA_DIR / '05_CTE_mismatch_thermal_stress.csv', comment='#')
    
    # Extract CTE values at 25°C and 800°C
    cte_25 = df[df['Temperature_C'] == 25].iloc[0]
    cte_800 = df[df['Temperature_C'] == 800].iloc[0]
    
    materials = ['8YSZ', 'NiYSZ', 'LSCF', 'GDC', 'LSM', 'Crofer']
    cte_values_25 = [cte_25[f'CTE_{mat}'] for mat in materials]
    cte_values_800 = [cte_800[f'CTE_{mat}'] for mat in materials]
    
    # Material labels (clean for display)
    material_labels = ['8YSZ', 'Ni-YSZ', 'LSCF', 'GDC', 'LSM', 'Crofer\n22APU']
    material_keys = ['8YSZ', 'Ni-YSZ', 'LSCF', 'GDC', 'LSM', 'Crofer22APU']
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Bar positions
    x = np.arange(len(materials))
    width = 0.35
    
    # Create bars
    bars1 = ax.bar(x - width/2, cte_values_25, width, label='25°C', 
                   color=[COLORS[k] for k in material_keys], alpha=0.7, edgecolor='black')
    bars2 = ax.bar(x + width/2, cte_values_800, width, label='800°C', 
                   color=[COLORS[k] for k in material_keys], alpha=1.0, edgecolor='black')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=9)
    
    # Customize plot
    ax.set_xlabel('Material', fontsize=12)
    ax.set_ylabel('Coefficient of Thermal Expansion (10⁻⁶ K⁻¹)', fontsize=12)
    ax.set_title('CTE Comparison at 25°C and 800°C\n(Synthetic/Illustrative Data)', 
                fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(material_labels, fontsize=11)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 18)
    
    # Add reference line for 8YSZ (electrolyte)
    ax.axhline(y=cte_800['CTE_8YSZ'], color='gray', linestyle='--', 
              linewidth=1.5, alpha=0.5, label='8YSZ @ 800°C (ref)')
    
    # Add annotation about mismatch
    ax.text(0.98, 0.98, 'Higher CTE mismatch\n→ Greater thermal stress', 
           transform=ax.transAxes, fontsize=10, 
           verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    plt.tight_layout()
    
    # Save figure
    output_path = FIGURES_DIR / 'fig08_CTE_mismatch_bar.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved {output_path.name}")
    plt.close()


if __name__ == "__main__":
    plot_CTE_mismatch()
