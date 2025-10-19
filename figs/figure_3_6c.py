#!/usr/bin/env python3
"""
Figure 3.6C — (Left) coherent fraction vs Ri; (Right) PSD broadening under marginal Ri
"""

import numpy as np
import matplotlib.pyplot as plt
from house_style import *


def generate_coherent_fraction_data():
    """Generate coherent fraction vs Ri data."""
    ri = np.linspace(RI_RANGE[0], RI_RANGE[1], 100)
    
    # Monotone decreasing from ~0.95 at Ri=2 to ~0.5 at Ri≈0.25
    base_coherence = 0.5 + 0.45 * (ri / 2.0)**0.8
    
    # Intermittent dip near marginal Ri (centered around Ri≈0.3-0.5)
    dip_center = 0.4
    dip_width = 0.2
    dip_depth = 0.15
    dip = dip_depth * np.exp(-((ri - dip_center)**2 / (dip_width**2)))
    
    coherent_fraction = base_coherence - dip
    
    # Variability band around the dip
    variability_upper = coherent_fraction + 0.05 * np.exp(-((ri - dip_center)**2 / (dip_width**2)))
    variability_lower = coherent_fraction - 0.05 * np.exp(-((ri - dip_center)**2 / (dip_width**2)))
    
    return ri, coherent_fraction, variability_upper, variability_lower


def generate_psd_data():
    """Generate PSD data for high vs marginal Ri."""
    omega_n = np.linspace(OMEGA_N_RANGE[0], OMEGA_N_RANGE[1], 200)
    
    # High Ri: narrowband peak centered near ω/N ≈ 1
    high_ri_psd = np.exp(-((omega_n - 1.0)**2 / (0.15**2)))
    
    # Marginal Ri: broader plateau/peak with wider bandwidth
    marginal_ri_psd = 0.8 * np.exp(-((omega_n - 1.0)**2 / (0.35**2))) + \
                     0.3 * np.exp(-((omega_n - 0.8)**2 / (0.25**2))) + \
                     0.2 * np.exp(-((omega_n - 1.3)**2 / (0.3**2)))
    
    # Add slight raggedness to marginal Ri curve
    raggedness = 0.05 * np.random.random(len(omega_n))
    marginal_ri_psd += raggedness
    
    # Normalize both to [0,1]
    high_ri_psd = high_ri_psd / np.max(high_ri_psd)
    marginal_ri_psd = marginal_ri_psd / np.max(marginal_ri_psd)
    
    return omega_n, high_ri_psd, marginal_ri_psd


def calculate_half_power_bandwidth(omega_n, psd):
    """Calculate half-power bandwidth."""
    half_max = np.max(psd) / 2
    indices = np.where(psd >= half_max)[0]
    if len(indices) > 0:
        return omega_n[indices[-1]] - omega_n[indices[0]]
    return 0


def create_figure_3_6c():
    """Create Figure 3.6C with dual subpanels."""
    fig = setup_figure()
    
    # Create two subplots
    ax1 = fig.add_subplot(121)  # Left: coherent fraction vs Ri
    ax2 = fig.add_subplot(122)  # Right: PSD broadening
    
    # Left subpanel: Coherent fraction vs Ri
    ri, coherent_fraction, var_upper, var_lower = generate_coherent_fraction_data()
    
    # Plot main curve
    ax1.plot(ri, coherent_fraction, color=COLORS['deep_blue'], linewidth=3, 
            label='Coherent fraction')
    
    # Add variability band around marginal Ri
    mask = (ri >= 0.2) & (ri <= 0.6)
    ax1.fill_between(ri[mask], var_lower[mask], var_upper[mask], 
                    color=COLORS['steel_blue'], alpha=COLORS['uncertainty_alpha'],
                    label='Variability')
    
    # Setup left axes
    ax1.set_xlim(RI_RANGE)
    ax1.set_xticks(RI_TICKS)
    ax1.set_xlabel(r'$R_i$', fontsize=FONT_SIZES['axis_label'])
    ax1.set_ylim(0, 1)
    ax1.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax1.set_ylabel('Coherent fraction', fontsize=FONT_SIZES['axis_label'])
    ax1.grid(True, color=GRID_COLOR, linewidth=GRID_LINEWIDTH)
    
    # Add annotations
    ax1.annotate("stable: high\ncoherent fraction", xy=(1.5, 0.85), xytext=(1.6, 0.7),
                fontsize=FONT_SIZES['in_plot_note']-2,
                arrowprops=dict(arrowstyle='->', color='black', alpha=0.7))
    
    ax1.annotate("marginal: additional\nloss & variability", xy=(0.4, 0.45), xytext=(0.8, 0.3),
                fontsize=FONT_SIZES['in_plot_note']-2,
                arrowprops=dict(arrowstyle='->', color='black', alpha=0.7))
    
    # Right subpanel: PSD broadening
    omega_n, high_ri_psd, marginal_ri_psd = generate_psd_data()
    
    # Plot PSDs
    ax2.plot(omega_n, high_ri_psd, color=COLORS['deep_blue'], linewidth=3, 
            linestyle='-', label=r'High $R_i$')
    ax2.plot(omega_n, marginal_ri_psd, color=COLORS['steel_blue'], linewidth=3, 
            linestyle='--', label=r'Marginal $R_i$')
    
    # Setup right axes
    setup_omega_n_axis(ax2)
    ax2.set_ylim(0, 1)
    ax2.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax2.set_ylabel('Normalized PSD', fontsize=FONT_SIZES['axis_label'])
    ax2.grid(True, color=GRID_COLOR, linewidth=GRID_LINEWIDTH)
    
    # Add conversion window overlay
    add_conversion_window(ax2)
    
    # Calculate and show bandwidth bars (optional)
    bw_high = calculate_half_power_bandwidth(omega_n, high_ri_psd)
    bw_marginal = calculate_half_power_bandwidth(omega_n, marginal_ri_psd)
    
    # Add bandwidth indicators
    ax2.annotate('', xy=(1.0 - bw_high/2, 0.15), xytext=(1.0 + bw_high/2, 0.15),
                arrowprops=dict(arrowstyle='<->', color=COLORS['deep_blue'], lw=2))
    ax2.text(1.0, 0.1, f'BW', ha='center', va='top', 
            fontsize=FONT_SIZES['in_plot_note']-4, color=COLORS['deep_blue'])
    
    ax2.annotate('', xy=(1.0 - bw_marginal/2, 0.05), xytext=(1.0 + bw_marginal/2, 0.05),
                arrowprops=dict(arrowstyle='<->', color=COLORS['steel_blue'], lw=2))
    ax2.text(1.0, 0.01, f'BW', ha='center', va='top', 
            fontsize=FONT_SIZES['in_plot_note']-4, color=COLORS['steel_blue'])
    
    # Add note about broader PSD
    ax2.text(0.95, 0.6, r"broader PSD under" + "\n" + r"marginal $R_i$",
            transform=ax2.transAxes, fontsize=FONT_SIZES['in_plot_note']-2,
            ha='right', va='center', 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    # Add legends
    ax1.legend(loc='upper right', frameon=False)
    ax2.legend(loc='upper right', frameon=False)
    
    # Overall title
    fig.suptitle(r"Figure 3.6C — Coherence loss and spectral broadening with decreasing $R_i$", 
                fontsize=FONT_SIZES['panel_title'], fontweight='bold', y=0.95)
    
    # Caption
    caption = (r"Coherent fraction declines monotonically with a superposed dip near marginal $R_i$; "
              r"spectra broaden under marginal $R_i$, indicating enhanced shear-mediated variability.")
    add_caption(fig, caption)
    
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    fig = create_figure_3_6c()
    save_figure(fig, "figure_3_6c")
    plt.show()