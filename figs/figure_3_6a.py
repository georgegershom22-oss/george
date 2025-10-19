"""
Figure 3.6A — Shear-dominance index on (Ri, ω/N)
Bright = shear-mediated loss most influential
"""

import numpy as np
import matplotlib.pyplot as plt
from house_style import *

def generate_sdi_data(ri_range, omega_n_range, n_ri=100, n_omega=100):
    """Generate shear-dominance index data with physics-based structure"""
    ri = np.linspace(ri_range[0], ri_range[1], n_ri)
    omega_n = np.linspace(omega_n_range[0], omega_n_range[1], n_omega)
    Ri, OmegaN = np.meshgrid(ri, omega_n, indexing='ij')
    
    # Initialize SDI array
    SDI = np.zeros_like(Ri)
    
    # High SDI lobe: concentrated for low-moderate Ri and near conversion window
    # Peak around (Ri ≈ 0.4, ω/N ≈ 1)
    ri_center = 0.4
    omega_center = 1.0
    ri_width = 0.3
    omega_width = 0.4
    
    # Gaussian-like peak in the main lobe
    ri_factor = np.exp(-((Ri - ri_center) / ri_width)**2)
    omega_factor = np.exp(-((OmegaN - omega_center) / omega_width)**2)
    main_lobe = ri_factor * omega_factor
    
    # Rapid decay with stability (Ri → 1-2)
    stability_decay = np.exp(-Ri / 0.8)
    
    # High-frequency suppression (ω/N ≳ 1.4-1.6)
    freq_suppression = np.where(OmegaN > 1.4, 
                               np.exp(-((OmegaN - 1.4) / 0.3)**2), 1.0)
    
    # Sub-buoyancy tail: weaker tongue extending into ω/N < 1 at very low Ri
    sub_buoyancy = np.where((OmegaN < 1.0) & (Ri < 0.3), 
                          0.3 * np.exp(-((OmegaN - 0.8) / 0.2)**2) * 
                          np.exp(-((Ri - 0.1) / 0.15)**2), 0.0)
    
    # Combine all effects
    SDI = main_lobe * stability_decay * freq_suppression + sub_buoyancy
    
    # Ensure values are in [0, 1] range
    SDI = np.clip(SDI, 0, 1)
    
    return ri, omega_n, SDI

def create_figure_3_6a():
    """Create Figure 3.6A - Shear-dominance index heatmap"""
    # Generate data
    ri, omega_n, SDI = generate_sdi_data(RI_RANGE, OMEGA_N_RANGE)
    
    # Create figure
    fig = create_figure()
    ax = fig.add_subplot(111)
    
    # Create heatmap
    colormap = get_heatmap_colormap()
    im = ax.imshow(SDI, extent=[OMEGA_N_RANGE[0], OMEGA_N_RANGE[1], 
                               RI_RANGE[0], RI_RANGE[1]], 
                   aspect='auto', origin='lower', cmap=colormap, 
                   interpolation='bilinear')
    
    # Setup axes
    setup_omega_n_axis(ax, xlabel=True)
    setup_ri_axis(ax, ylabel=True)
    
    # Add conversion window overlay
    add_conversion_window(ax)
    
    # Add marginal stability guide
    add_marginal_stability_guide(ax)
    
    # Add colorbar
    add_colorbar(fig, ax, im, 'Shear-dominance index (0–1)', 
                ticks=[0, 0.25, 0.5, 0.75, 1.0])
    
    # Add title
    add_panel_title(ax, 'Figure 3.6A — Shear-dominance index SDI(Ri,ω/N)')
    
    # Add caption
    caption = ('Bright regions indicate parameter pairs where shear-mediated loss dominates; '
              'peak influence occurs near ω/N ≈ 1 under marginal Ri, and decays at higher '
              'Ri or ω/N > 1.')
    add_caption(ax, caption)
    
    return fig

if __name__ == '__main__':
    fig = create_figure_3_6a()
    save_figure(fig, 'figure_3_6a')
    plt.show()