#!/usr/bin/env python3
"""
Plot 2D temperature contour map of SOFC cell surface.
Generates publication-quality figure: fig09_temperature_contour.png
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

def plot_temperature_map():
    """Create 2D contour map of steady-state temperature distribution."""
    # Read data
    df = pd.read_csv(DATA_DIR / '09_temperature_distribution.csv', comment='#')
    
    # Get unique x and y coordinates
    x_unique = sorted(df['Position_x_mm'].unique())
    y_unique = sorted(df['Position_y_mm'].unique())
    
    # Create 2D grid
    X, Y = np.meshgrid(x_unique, y_unique)
    
    # Reshape temperature data to 2D array
    Z = df['T_SteadyState_K'].values.reshape(len(y_unique), len(x_unique))
    
    # Convert Kelvin to Celsius for display
    Z_celsius = Z - 273.15
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create contour plot
    levels = np.linspace(Z_celsius.min(), Z_celsius.max(), 15)
    contour = ax.contourf(X, Y, Z_celsius, levels=levels, cmap='hot')
    
    # Add contour lines
    contour_lines = ax.contour(X, Y, Z_celsius, levels=levels[::2], 
                               colors='black', linewidths=0.5, alpha=0.3)
    ax.clabel(contour_lines, inline=True, fontsize=8, fmt='%1.0f°C')
    
    # Add colorbar
    cbar = plt.colorbar(contour, ax=ax)
    cbar.set_label('Temperature (°C)', fontsize=12)
    
    # Customize plot
    ax.set_xlabel('Position x (mm)', fontsize=12)
    ax.set_ylabel('Position y (mm)', fontsize=12)
    ax.set_title('Steady-State Temperature Distribution (100×100 mm Cell)\n(Synthetic/Illustrative Data)', 
                fontsize=13, fontweight='bold')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2, linestyle='--', color='white')
    
    # Add annotations
    min_idx = np.unravel_index(Z_celsius.argmin(), Z_celsius.shape)
    max_idx = np.unravel_index(Z_celsius.argmax(), Z_celsius.shape)
    
    ax.plot(X[max_idx], Y[max_idx], 'r*', markersize=15, label='Hot spot')
    ax.plot(X[min_idx], Y[min_idx], 'b*', markersize=15, label='Cold spot')
    
    ax.legend(fontsize=11, loc='upper right')
    
    # Add temperature range annotation
    ax.text(0.02, 0.98, f'ΔT = {Z_celsius.max()-Z_celsius.min():.1f}°C', 
           transform=ax.transAxes, fontsize=11, 
           verticalalignment='top', horizontalalignment='left',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Save figure
    output_path = FIGURES_DIR / 'fig09_temperature_contour.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved {output_path.name}")
    plt.close()


if __name__ == "__main__":
    plot_temperature_map()
