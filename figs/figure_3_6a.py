#!/usr/bin/env python3
"""
Figure 3.6A — Shear-dominance index on (Ri, ω/N)
Bright regions indicate where shear-mediated attenuation dominates.
"""

import numpy as np
import matplotlib.pyplot as plt
from house_style import *


def generate_sdi_data():
    """Generate synthetic shear-dominance index data with realistic physics."""
    # Create coordinate grids
    omega_n = np.linspace(OMEGA_N_RANGE[0], OMEGA_N_RANGE[1], 200)
    ri = np.linspace(RI_RANGE[0], RI_RANGE[1], 150)
    Omega_N, Ri = np.meshgrid(omega_n, ri)
    
    # High SDI lobe: concentrated for low-moderate Ri and near conversion window
    # Peak centered around (Ri ≈ 0.4, ω/N ≈ 1)
    conversion_peak = np.exp(-((Omega_N - 1.0)**2 / (0.3**2)) - ((Ri - 0.4)**2 / (0.2**2)))
    
    # Rapid decay with stability (higher Ri)
    stability_decay = np.exp(-Ri / 0.5)
    
    # High-frequency suppression (ω/N > 1.4-1.6)
    freq_suppression = np.where(Omega_N > 1.4, 
                               np.exp(-(Omega_N - 1.4) / 0.3), 1.0)
    
    # Sub-buoyancy tail: weaker tongue extending into ω/N < 1 at very low Ri
    sub_buoyancy = np.where((Omega_N < 1.0) & (Ri < 0.3),
                           0.3 * np.exp(-((Omega_N - 0.7)**2 / (0.2**2)) - (Ri / 0.15)),
                           0.0)
    
    # Combine components
    sdi = (conversion_peak * stability_decay * freq_suppression + sub_buoyancy)
    
    # Add some realistic texture/noise
    noise = 0.05 * np.random.random(sdi.shape)
    sdi = np.clip(sdi + noise, 0, 1)
    
    return omega_n, ri, sdi


def create_figure_3_6a():
    """Create Figure 3.6A."""
    fig = setup_figure()
    ax = fig.add_subplot(111)
    
    # Generate data
    omega_n, ri, sdi = generate_sdi_data()
    
    # Create heatmap (darker = higher intensity)
    im = ax.imshow(sdi, extent=[OMEGA_N_RANGE[0], OMEGA_N_RANGE[1], 
                               RI_RANGE[0], RI_RANGE[1]], 
                  aspect='auto', origin='lower', cmap=get_cividis_reversed(),
                  vmin=0, vmax=1)
    
    # Setup axes
    setup_omega_n_axis(ax)
    setup_ri_axis(ax)
    
    # Add conversion window overlay
    add_conversion_window(ax)
    
    # Add marginal stability line
    add_marginal_stability_line(ax)
    
    # Add colorbar
    cbar_ticks = [0, 0.25, 0.5, 0.75, 1.0]
    add_colorbar(fig, im, "Shear-dominance index (0–1)", ticks=cbar_ticks)
    
    # Add title
    title = r"Figure 3.6A — Shear-dominance index $SDI(R_i,\omega/N)$"
    add_panel_title(ax, title)
    
    # Add caption
    caption = (r"Bright regions indicate parameter pairs where shear-mediated loss dominates; "
              r"peak influence occurs near $\omega/N \approx 1$ under marginal $R_i$, "
              r"and decays at higher $R_i$ or $\omega/N > 1$.")
    add_caption(fig, caption)
    
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    fig = create_figure_3_6a()
    save_figure(fig, "figure_3_6a")
    plt.show()