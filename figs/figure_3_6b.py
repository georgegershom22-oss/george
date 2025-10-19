#!/usr/bin/env python3
"""
Figure 3.6B — Time–frequency TL fluctuation intensity
Left: high Ri (narrow conversion band). Right: marginal Ri (intermittent, broadband bursts).
"""

import numpy as np
import matplotlib.pyplot as plt
from house_style import *


def generate_tl_fluctuation_data(time_steps=300, freq_steps=100, scenario='high_ri'):
    """Generate synthetic TL fluctuation intensity data."""
    # Time and frequency grids
    time = np.linspace(0, 60, time_steps)  # 60 seconds
    omega_n = np.linspace(OMEGA_N_RANGE[0], OMEGA_N_RANGE[1], freq_steps)
    T, Omega_N = np.meshgrid(time, omega_n)
    
    if scenario == 'high_ri':
        # High Ri: narrow conversion-band modulation, time-steady
        conversion_band = np.exp(-((Omega_N - 1.0)**2 / (0.1**2)))  # Narrow band
        time_modulation = 1 + 0.2 * np.sin(2 * np.pi * T / 20)  # Slight waviness
        intensity = conversion_band * time_modulation
        
        # Add minimal background noise
        background = 0.05 * np.random.random(intensity.shape)
        intensity = intensity + background
        
    else:  # marginal_ri
        # Marginal Ri: intermittent broadband bursts
        # Persistent but less coherent band near ω/N ≈ 1
        persistent_band = 0.4 * np.exp(-((Omega_N - 1.0)**2 / (0.15**2)))
        
        # Intermittent bursts - create sporadic high-intensity regions
        n_bursts = 8
        burst_intensity = np.zeros_like(T)
        
        for i in range(n_bursts):
            # Random burst timing and characteristics
            t_center = np.random.uniform(5, 55)
            t_width = np.random.uniform(3, 8)
            omega_center = np.random.uniform(0.6, 1.8)
            omega_width = np.random.uniform(0.3, 0.8)
            amplitude = np.random.uniform(0.6, 1.0)
            
            # Create burst
            burst = amplitude * np.exp(-((T - t_center)**2 / (t_width**2)) - 
                                     ((Omega_N - omega_center)**2 / (omega_width**2)))
            burst_intensity += burst
        
        # Combine persistent band with bursts
        intensity = persistent_band + burst_intensity
        
        # Add background variability
        background = 0.1 * np.random.random(intensity.shape)
        intensity = intensity + background
    
    # Normalize and clip
    intensity = np.clip(intensity, 0, None)
    intensity = intensity / np.max(intensity)  # Normalize to [0,1]
    
    return time, omega_n, intensity


def create_figure_3_6b():
    """Create Figure 3.6B with dual panels."""
    fig = setup_figure()
    
    # Create two subplots with shared y-axis
    ax1 = fig.add_subplot(121)  # Left panel
    ax2 = fig.add_subplot(122, sharey=ax1)  # Right panel
    
    # Generate data for both scenarios
    time, omega_n, intensity_high_ri = generate_tl_fluctuation_data(scenario='high_ri')
    _, _, intensity_marginal_ri = generate_tl_fluctuation_data(scenario='marginal_ri')
    
    # Shared colormap limits for comparison
    vmax = max(np.max(intensity_high_ri), np.max(intensity_marginal_ri))
    
    # Left panel: High Ri
    im1 = ax1.imshow(intensity_high_ri, extent=[0, 60, OMEGA_N_RANGE[0], OMEGA_N_RANGE[1]], 
                    aspect='auto', origin='lower', cmap=get_cividis_reversed(),
                    vmin=0, vmax=vmax)
    
    ax1.set_xlabel('Time (s)', fontsize=FONT_SIZES['axis_label'])
    ax1.set_ylabel(r'$\omega/N$', fontsize=FONT_SIZES['axis_label'])
    ax1.set_xticks([0, 10, 20, 30, 40, 50, 60])
    ax1.set_ylim(OMEGA_N_RANGE)
    ax1.set_yticks(OMEGA_N_TICKS)
    
    # Add conversion window overlay to left panel
    add_conversion_window(ax1)
    
    # Add annotation for narrow conversion-band modulation
    ax1.text(0.95, 0.85, "narrow conversion-band\nmodulation", 
            transform=ax1.transAxes, fontsize=FONT_SIZES['in_plot_note']-2,
            ha='right', va='top', bbox=dict(boxstyle="round,pad=0.3", 
            facecolor='white', alpha=0.8))
    
    # Right panel: Marginal Ri
    im2 = ax2.imshow(intensity_marginal_ri, extent=[0, 60, OMEGA_N_RANGE[0], OMEGA_N_RANGE[1]], 
                    aspect='auto', origin='lower', cmap=get_cividis_reversed(),
                    vmin=0, vmax=vmax)
    
    ax2.set_xlabel('Time (s)', fontsize=FONT_SIZES['axis_label'])
    ax2.set_xticks([0, 10, 20, 30, 40, 50, 60])
    ax2.set_ylim(OMEGA_N_RANGE)
    ax2.set_yticks(OMEGA_N_TICKS)
    plt.setp(ax2.get_yticklabels(), visible=False)  # Hide y-tick labels on right panel
    
    # Add conversion window overlay to right panel
    add_conversion_window(ax2)
    
    # Add annotations for intermittent bursts
    ax2.annotate("intermittent broadband\nbursts", xy=(25, 1.6), xytext=(0.7, 0.85),
                textcoords='axes fraction', fontsize=FONT_SIZES['in_plot_note']-2,
                arrowprops=dict(arrowstyle='->', color='black', alpha=0.7),
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    ax2.annotate("enhanced spread\nbeyond conversion", xy=(40, 0.5), xytext=(0.3, 0.15),
                textcoords='axes fraction', fontsize=FONT_SIZES['in_plot_note']-2,
                arrowprops=dict(arrowstyle='->', color='black', alpha=0.7),
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    # Add single shared colorbar on the right
    cbar = add_colorbar(fig, im2, "TL fluctuation intensity (arb.)", ax_position=ax2)
    
    # Add captions inside each panel at bottom
    ax1.text(0.5, 0.05, r"High $R_i$: fluctuation energy concentrated in a narrow conversion band.",
            transform=ax1.transAxes, fontsize=FONT_SIZES['caption'], style='italic',
            ha='center', va='bottom', bbox=dict(boxstyle="round,pad=0.3", 
            facecolor='white', alpha=0.9))
    
    ax2.text(0.5, 0.05, r"Marginal $R_i$: intermittent broadband activity indicates shear-mediated variability.",
            transform=ax2.transAxes, fontsize=FONT_SIZES['caption'], style='italic',
            ha='center', va='bottom', bbox=dict(boxstyle="round,pad=0.3", 
            facecolor='white', alpha=0.9))
    
    # Overall title
    fig.suptitle("Figure 3.6B — Time–frequency TL fluctuation intensity", 
                fontsize=FONT_SIZES['panel_title'], fontweight='bold', y=0.95)
    
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    fig = create_figure_3_6b()
    save_figure(fig, "figure_3_6b")
    plt.show()