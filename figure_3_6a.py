#!/usr/bin/env python3
"""
Figure 3.6A — Shear-dominance index on (Ri, ω/N)
Creates a heatmap showing shear-dominance index with specified styling and overlays.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

# Set up the figure with specified dimensions and styling
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['mathtext.default'] = 'regular'

def create_shear_dominance_data(ri_vals, omega_n_vals):
    """
    Create synthetic shear-dominance index data based on physical description:
    - Bright, horizontally elongated island centered ~(Ri≈0.4, ω/N≈1)
    - Intensity decays as Ri→1-2 and for ω/N≳1.4
    - Weak tongue for ω/N<1 at very low Ri (shear-driven tail)
    """
    Ri, Omega_N = np.meshgrid(ri_vals, omega_n_vals, indexing='ij')
    
    # Main bright island centered at (Ri≈0.4, ω/N≈1)
    main_peak = np.exp(-((Ri - 0.4)**2 / (0.3**2) + (Omega_N - 1.0)**2 / (0.25**2)))
    
    # Decay for higher Ri values
    high_ri_decay = np.exp(-(Ri - 0.4)**2 / (0.8**2)) * np.where(Ri > 0.4, 
                                                                  np.exp(-(Ri - 0.4) / 0.4), 1.0)
    
    # Decay for ω/N > 1.4
    high_omega_decay = np.where(Omega_N > 1.4, 
                               np.exp(-(Omega_N - 1.4) / 0.3), 1.0)
    
    # Weak tongue for ω/N < 1 at low Ri (shear-driven tail)
    shear_tail = np.where((Omega_N < 1.0) & (Ri < 0.3), 
                         0.3 * np.exp(-Ri / 0.15) * np.exp(-(1.0 - Omega_N) / 0.4), 0)
    
    # Combine components
    sdi = main_peak * high_ri_decay * high_omega_decay + shear_tail
    
    # Smooth fade at edges to avoid blocky artifacts
    edge_fade_ri = np.where(Ri < 0.05, Ri / 0.05, 1.0) * np.where(Ri > 1.9, (2.0 - Ri) / 0.1, 1.0)
    edge_fade_omega = np.where(Omega_N < 0.25, Omega_N / 0.25, 1.0) * np.where(Omega_N > 2.1, (2.2 - Omega_N) / 0.1, 1.0)
    
    sdi *= edge_fade_ri * edge_fade_omega
    
    # Normalize to 0-1 range
    sdi = np.clip(sdi / np.max(sdi), 0, 1)
    
    return sdi

def create_figure_3_6a():
    """Create Figure 3.6A with all specified styling and overlays."""
    
    # Create figure with specified size (1800x1200 px)
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    fig.patch.set_facecolor('white')
    
    # Define coordinate ranges
    omega_n_range = np.linspace(0.2, 2.2, 200)
    ri_range = np.linspace(0.0, 2.0, 160)
    
    # Create shear-dominance index data
    sdi_data = create_shear_dominance_data(ri_range, omega_n_range)
    
    # Create the heatmap using viridis colormap (darker = higher intensity)
    im = ax.imshow(sdi_data, extent=[0.2, 2.2, 0.0, 2.0], 
                   aspect='auto', origin='lower', cmap='viridis', vmin=0, vmax=1)
    
    # Set up axes with specified ticks and labels
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(0.0, 2.0)
    
    # x-axis ticks and labels
    x_ticks = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([f'{x:.1f}' for x in x_ticks], fontsize=16)
    ax.set_xlabel(r'$\omega/N$', fontsize=22, fontweight='normal')
    
    # y-axis ticks and labels
    y_ticks = [0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f'{y:.2f}' if y != int(y) else f'{int(y)}' for y in y_ticks], fontsize=16)
    ax.set_ylabel(r'$R_i$', fontsize=22, fontweight='normal')
    
    # Grid styling - light gray, major ticks only
    ax.grid(True, color='#E5E7EB', linewidth=0.8, alpha=1.0)
    ax.set_axisbelow(True)
    
    # Conversion window overlay (translucent amber for 0.8 ≤ ω/N ≤ 1.2)
    conversion_window = Rectangle((0.8, 0.0), 0.4, 2.0, 
                                 facecolor='#F4A261', alpha=0.2, 
                                 edgecolor='none', zorder=3)
    ax.add_patch(conversion_window)
    
    # Dotted centerline at ω/N = 1
    ax.axvline(x=1.0, color='#9CA3AF', linestyle=':', linewidth=1, zorder=4)
    
    # Optional dashed guide at Ri = 0.25 (marginal stability)
    ax.axhline(y=0.25, color='#9CA3AF', linestyle='--', linewidth=1.2, zorder=4)
    ax.text(0.25, 0.28, 'marginal stability', fontsize=18, color='#4B5563', 
            verticalalignment='bottom')
    
    # Colorbar on the right side
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Shear-dominance index (0–1)', fontsize=20, labelpad=15)
    cbar_ticks = [0, 0.25, 0.5, 0.75, 1.0]
    cbar.set_ticks(cbar_ticks)
    cbar.set_ticklabels([f'{t:.2f}' if t != int(t) else f'{int(t)}' for t in cbar_ticks])
    cbar.ax.tick_params(labelsize=16)
    
    # Title inside top-left
    ax.text(0.05, 0.95, r'Figure 3.6A — $SDI(R_i, \omega/N)$', 
            transform=ax.transAxes, fontsize=28, fontweight='bold',
            verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', 
                                              facecolor='white', alpha=0.8))
    
    # Caption inside, below axis
    caption_text = (r'Bright regions: shear-mediated loss dominates; '
                   r'peak near $\omega/N \approx 1$ under marginal $R_i$.')
    ax.text(0.5, 0.02, caption_text, transform=ax.transAxes, fontsize=18,
            horizontalalignment='center', verticalalignment='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Set line weights for axes
    for spine in ax.spines.values():
        spine.set_linewidth(2)
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # Create and save the figure
    fig = create_figure_3_6a()
    
    # Save as PNG (300 DPI) and PDF
    fig.savefig('figures/figure_3_6a.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    fig.savefig('figures/figure_3_6a.pdf', bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    fig.savefig('figures/figure_3_6a.svg', bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print("Figure 3.6A created successfully!")
    print("Files saved:")
    print("- figures/figure_3_6a.png (300 DPI)")
    print("- figures/figure_3_6a.pdf (vector)")
    print("- figures/figure_3_6a.svg (vector)")
    
    plt.show()