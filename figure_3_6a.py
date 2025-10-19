"""
Figure 3.6A — Shear-dominance index on (Ri, ω/N)
Bright regions indicate where shear-mediated loss is most influential
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

def generate_shear_dominance_data(omega_N, Ri):
    """
    Generate synthetic shear-dominance index data with:
    - Bright, horizontally elongated island centered ~(Ri≈0.4, ω/N≈1)
    - Intensity decays as Ri→1−2 and for ω/N≳1.4
    - Weak tongue for ω/N<1 at very low Ri
    """
    OMEGA_N, RI = np.meshgrid(omega_N, Ri)
    
    # Main island centered at (Ri≈0.4, ω/N≈1)
    island_center_ri = 0.4
    island_center_omega = 1.0
    island_width_omega = 0.5
    island_width_ri = 0.25
    
    # Calculate distance from center for main island
    island = np.exp(-((RI - island_center_ri)**2 / (2 * island_width_ri**2) +
                      (OMEGA_N - island_center_omega)**2 / (2 * island_width_omega**2)))
    
    # Add weak tongue for ω/N < 1 at very low Ri
    tongue_mask = (OMEGA_N < 1.0) & (RI < 0.2)
    tongue = tongue_mask * 0.3 * np.exp(-RI / 0.1) * np.exp(-(1.0 - OMEGA_N)**2 / 0.5)
    
    # Combine components
    SDI = island * 0.9 + tongue
    
    # Apply decay for high Ri and high ω/N
    ri_decay = np.exp(-(RI - 0.4)**2 / 2.0) * (RI < 1.5) + 0.1 * (RI >= 1.5)
    omega_decay = np.exp(-(OMEGA_N - 1.0)**2 / 1.5)
    
    SDI *= ri_decay * omega_decay
    
    # Suppress extremes - fade top/bottom edges
    edge_fade_bottom = 1.0 - np.exp(-RI * 10)
    edge_fade_top = 1.0 - np.exp(-(2.0 - RI) * 5)
    SDI *= edge_fade_bottom * edge_fade_top
    
    # Normalize to [0, 1]
    SDI = np.clip(SDI / np.max(SDI), 0, 1)
    
    # Add some smooth variation
    noise = np.random.RandomState(42).randn(*SDI.shape) * 0.02
    SDI = np.clip(SDI + noise, 0, 1)
    
    # Apply smoothing for no blocky artifacts
    from scipy.ndimage import gaussian_filter
    SDI = gaussian_filter(SDI, sigma=1.5)
    
    return SDI

def create_figure_3_6a():
    # Set up figure with specified dimensions
    fig = plt.figure(figsize=(18, 12), facecolor='white')
    ax = fig.add_subplot(111)
    
    # Generate data
    omega_N = np.linspace(0.2, 2.2, 200)
    Ri = np.linspace(0.0, 2.0, 150)
    SDI = generate_shear_dominance_data(omega_N, Ri)
    
    # Create heatmap with Viridis colormap
    im = ax.pcolormesh(omega_N, Ri, SDI, shading='auto', cmap='viridis')
    
    # Add conversion window overlay (translucent amber)
    conversion_band = Rectangle((0.8, 0), 0.4, 2.0, 
                               facecolor='#F4A261', alpha=0.2, 
                               edgecolor='none', zorder=2)
    ax.add_patch(conversion_band)
    
    # Add dotted centerline at ω/N=1
    ax.axvline(x=1.0, color='#9CA3AF', linestyle=':', linewidth=1, zorder=3)
    
    # Optional dashed guide at Ri=0.25
    ax.axhline(y=0.25, color='#666666', linestyle='--', linewidth=1.5, 
               alpha=0.5, zorder=3)
    ax.text(2.1, 0.25, 'marginal stability', fontsize=18, 
            va='center', ha='right', style='italic', color='#666666')
    
    # Set axes limits and labels
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(0.0, 2.0)
    
    ax.set_xlabel('ω/N', fontsize=22, fontweight='normal')
    ax.set_ylabel('Ri', fontsize=22, fontweight='normal')
    
    # Set specific ticks
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.set_yticks([0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
    
    # Customize tick labels
    ax.tick_params(axis='both', which='major', labelsize=16)
    
    # Add grid
    ax.grid(True, color='#E5E7EB', linewidth=0.8, alpha=0.8)
    ax.set_axisbelow(True)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Shear-dominance index (0–1)', fontsize=20)
    cbar.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
    cbar.ax.tick_params(labelsize=16)
    
    # Add title inside top-left
    ax.text(0.02, 0.98, 'Figure 3.6A — SDI(Ri, ω/N)', 
            transform=ax.transAxes, fontsize=28, fontweight='bold',
            va='top', ha='left')
    
    # Add caption below axis
    caption = "Bright regions: shear-mediated loss dominates; peak near ω/N≈1 under marginal Ri."
    fig.text(0.5, 0.08, caption, fontsize=18, ha='center', style='italic')
    
    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)
    
    return fig

if __name__ == "__main__":
    fig = create_figure_3_6a()
    
    # Save in multiple formats
    fig.savefig('figure_3_6a.png', dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig('figure_3_6a.pdf', bbox_inches='tight', facecolor='white')
    fig.savefig('figure_3_6a.svg', bbox_inches='tight', facecolor='white')
    
    plt.show()
    print("Figure 3.6A saved as PNG, PDF, and SVG")