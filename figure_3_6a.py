#!/usr/bin/env python3
"""
Figure 3.6A — Shear-dominance index on (Ri, ω/N)
Publication-quality figure following shared house style specifications.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

# Shared house style settings
plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 16,  # tick labels
    'axes.labelsize': 22,  # axis labels
    'axes.titlesize': 28,  # panel titles
    'axes.linewidth': 0.8,
    'grid.linewidth': 0.8,
    'grid.color': '#E5E7EB',
    'axes.grid': True,
    'axes.axisbelow': True,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white'
})

def create_shear_dominance_data(omega_N, Ri):
    """
    Create synthetic shear-dominance index data following the physics described:
    - High SDI lobe for low-moderate Ri (≲0.6) near conversion window (0.8-1.2 in ω/N)
    - Bright horizontally elongated island centered at (Ri≈0.4, ω/N≈1)
    - Rapid decay with stability as Ri→1-2
    - High-frequency suppression for ω/N≳1.4-1.6
    - Sub-buoyancy tail extending into ω/N<1 at very low Ri
    """
    OMEGA_N, RI = np.meshgrid(omega_N, Ri)
    
    # Main lobe: Gaussian-like peak centered at (ω/N≈1, Ri≈0.4)
    main_peak = np.exp(-((OMEGA_N - 1.0)**2 / (0.3**2) + (RI - 0.4)**2 / (0.2**2)))
    
    # Horizontal elongation in frequency direction
    freq_elongation = np.exp(-((OMEGA_N - 1.0)**2 / (0.5**2)))
    
    # Stability decay: exponential decay for high Ri
    stability_decay = np.exp(-(RI - 0.4)**2 / (0.8**2)) * np.exp(-np.maximum(0, RI - 0.6) / 0.3)
    
    # High-frequency suppression
    freq_suppression = np.exp(-np.maximum(0, OMEGA_N - 1.4) / 0.4)
    
    # Sub-buoyancy tail for low Ri and ω/N < 1
    sub_buoyancy = 0.3 * np.exp(-RI / 0.2) * np.exp(-np.maximum(0, 1.0 - OMEGA_N) / 0.3)
    
    # Combine all components
    sdi = main_peak * freq_elongation * stability_decay * freq_suppression + sub_buoyancy
    
    # Normalize to 0-1 range
    sdi = np.clip(sdi / np.max(sdi), 0, 1)
    
    return sdi

def main():
    # Create figure with specified canvas size
    fig, ax = plt.subplots(1, 1, figsize=(18, 12), dpi=100)
    
    # Define axes ranges as specified
    omega_N = np.linspace(0.2, 2.2, 200)
    Ri = np.linspace(0.0, 2.0, 150)
    
    # Generate shear-dominance index data
    sdi_data = create_shear_dominance_data(omega_N, Ri)
    
    # Create heatmap using Viridis colormap (darker = higher intensity)
    im = ax.imshow(sdi_data, extent=[0.2, 2.2, 0.0, 2.0], 
                   aspect='auto', origin='lower', cmap='viridis', 
                   vmin=0, vmax=1, interpolation='bilinear')
    
    # Set axes properties
    ax.set_xlabel(r'$\omega/N$', fontsize=22)
    ax.set_ylabel(r'$R_i$', fontsize=22)
    
    # Set tick positions and labels as specified
    omega_ticks = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
    ri_ticks = [0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0]
    
    ax.set_xticks(omega_ticks)
    ax.set_yticks(ri_ticks)
    ax.set_xticklabels([f'{x:.1f}' for x in omega_ticks], fontsize=16)
    ax.set_yticklabels([f'{y:.2f}' if y < 1 else f'{y:.1f}' for y in ri_ticks], fontsize=16)
    
    # Add conversion window overlay (translucent amber band)
    conversion_band = Rectangle((0.8, 0.0), 0.4, 2.0, 
                               facecolor='#F4A261', alpha=0.2, 
                               edgecolor='none', zorder=10)
    ax.add_patch(conversion_band)
    
    # Add dotted centerline at ω/N = 1
    ax.axvline(x=1.0, color='#9CA3AF', linestyle=':', linewidth=1, zorder=11)
    
    # Add optional horizontal guide at Ri = 0.25
    ax.axhline(y=0.25, color='#6B7280', linestyle='--', linewidth=1, alpha=0.7, zorder=11)
    ax.text(1.8, 0.28, 'marginal stability', fontsize=18, 
            ha='center', va='bottom', color='#374151')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=30, pad=0.02)
    cbar.set_label('Shear-dominance index (0–1)', fontsize=22, labelpad=20)
    cbar.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
    cbar.ax.tick_params(labelsize=16)
    
    # Add title
    ax.text(0.02, 0.98, r'Figure 3.6A — Shear-dominance index $SDI(R_i,\omega/N)$', 
            transform=ax.transAxes, fontsize=28, fontweight='bold',
            verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Add caption
    caption_text = (r"Bright regions indicate parameter pairs where shear-mediated loss dominates; "
                   r"peak influence occurs near $\omega/N \approx 1$ under marginal $R_i$, "
                   r"and decays at higher $R_i$ or $\omega/N > 1$.")
    
    ax.text(0.5, -0.12, caption_text, transform=ax.transAxes, 
            fontsize=15, style='italic', ha='center', va='top',
            wrap=True)
    
    # Set limits and grid
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(0.0, 2.0)
    ax.grid(True, alpha=0.3)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure
    plt.savefig('figure_3_6a.png', dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.savefig('figure_3_6a.pdf', bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print("Figure 3.6A created successfully!")
    plt.show()

if __name__ == "__main__":
    main()