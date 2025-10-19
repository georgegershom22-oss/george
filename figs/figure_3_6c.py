"""
Figure 3.6C — (Left) coherent fraction vs Ri; (Right) PSD broadening under marginal Ri
"""

import numpy as np
import matplotlib.pyplot as plt
from house_style import *

def generate_coherent_fraction_data(ri_range, n_points=200):
    """Generate coherent fraction data vs Ri"""
    ri = np.linspace(ri_range[0], ri_range[1], n_points)
    
    # Primary curve: monotone decreasing from ~0.95 at Ri=2 to ~0.5 at Ri≈0.25
    primary = 0.95 * np.exp(-ri / 1.2) + 0.5
    
    # Intermittent dip near marginal Ri: local notch centered around Ri≈0.3-0.5
    dip_center = 0.4
    dip_width = 0.15
    dip_depth = 0.4
    dip = dip_depth * np.exp(-((ri - dip_center) / dip_width)**2)
    
    coherent_fraction = primary - dip
    
    # Ensure values are in [0, 1] range
    coherent_fraction = np.clip(coherent_fraction, 0, 1)
    
    # Variability band for the intermittent region
    variability = 0.1 * np.exp(-((ri - dip_center) / (dip_width * 1.5))**2)
    
    return ri, coherent_fraction, variability

def generate_psd_data(omega_n_range, n_points=200):
    """Generate PSD data for high vs marginal Ri"""
    omega_n = np.linspace(omega_n_range[0], omega_n_range[1], n_points)
    
    # High Ri: narrowband peak centered near ω/N ≈ 1
    center_freq = 1.0
    high_ri_width = 0.15
    high_ri_psd = np.exp(-((omega_n - center_freq) / high_ri_width)**2)
    
    # Marginal Ri: broader plateau/peak, visibly wider half-power bandwidth
    marginal_ri_width = 0.4
    marginal_ri_psd = np.exp(-((omega_n - center_freq) / marginal_ri_width)**2)
    
    # Add some raggedness to marginal Ri curve
    raggedness = 0.1 * np.sin(10 * omega_n) * np.exp(-((omega_n - center_freq) / marginal_ri_width)**2)
    marginal_ri_psd += raggedness
    
    # Normalize both to [0, 1]
    high_ri_psd = high_ri_psd / np.max(high_ri_psd)
    marginal_ri_psd = marginal_ri_psd / np.max(marginal_ri_psd)
    
    return omega_n, high_ri_psd, marginal_ri_psd

def create_figure_3_6c():
    """Create Figure 3.6C - Coherent fraction vs Ri and PSD broadening"""
    # Generate data
    ri, coherent_fraction, variability = generate_coherent_fraction_data(RI_RANGE)
    omega_n, high_ri_psd, marginal_ri_psd = generate_psd_data(OMEGA_N_RANGE)
    
    # Create figure with two subpanels
    fig = create_figure()
    
    # Left subpanel - Coherent fraction vs Ri
    ax_left = fig.add_subplot(121)
    
    # Plot primary curve
    ax_left.plot(ri, coherent_fraction, color=DEEP_BLUE, linewidth=3, 
                label='Coherent fraction', zorder=3)
    
    # Add variability band around the dip region
    add_uncertainty_band(ax_left, ri, coherent_fraction, variability, 
                        STEEL_BLUE, alpha=0.2)
    
    # Setup axes
    ax_left.set_xlim(RI_RANGE)
    ax_left.set_xticks(RI_TICKS)
    ax_left.set_xlabel('Ri', fontsize=AXIS_LABEL_SIZE, fontweight='normal')
    ax_left.set_ylim(0, 1)
    ax_left.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax_left.set_ylabel('Coherent fraction', fontsize=AXIS_LABEL_SIZE, fontweight='normal')
    
    # Add annotations
    ax_left.annotate('stable: high coherent fraction', 
                    xy=(1.5, 0.8), xytext=(1.2, 0.9),
                    fontsize=IN_PLOT_NOTE_SIZE, ha='center', va='center',
                    arrowprops=dict(arrowstyle='->', color='black', lw=1),
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
    
    ax_left.annotate('marginal: additional loss & variability', 
                    xy=(0.4, 0.4), xytext=(0.6, 0.2),
                    fontsize=IN_PLOT_NOTE_SIZE, ha='center', va='center',
                    arrowprops=dict(arrowstyle='->', color='black', lw=1),
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
    
    # Right subpanel - PSD broadening
    ax_right = fig.add_subplot(122)
    
    # Plot both PSD curves
    ax_right.plot(omega_n, high_ri_psd, color=DEEP_BLUE, linewidth=3, 
                 label='High Ri', linestyle='-', zorder=3)
    ax_right.plot(omega_n, marginal_ri_psd, color=STEEL_BLUE, linewidth=3, 
                 label='Marginal Ri', linestyle='--', zorder=3)
    
    # Add half-power bandwidth bars (optional)
    # Find half-power points for high Ri
    half_power = 0.5
    high_ri_half_indices = np.where(high_ri_psd >= half_power)[0]
    if len(high_ri_half_indices) > 0:
        high_ri_bw_start = omega_n[high_ri_half_indices[0]]
        high_ri_bw_end = omega_n[high_ri_half_indices[-1]]
        ax_right.annotate('', xy=(high_ri_bw_end, half_power), 
                         xytext=(high_ri_bw_start, half_power),
                         arrowprops=dict(arrowstyle='<->', color=DEEP_BLUE, lw=2))
        ax_right.text((high_ri_bw_start + high_ri_bw_end) / 2, half_power + 0.05, 
                     'BW', ha='center', va='bottom', fontsize=IN_PLOT_NOTE_SIZE,
                     color=DEEP_BLUE, fontweight='bold')
    
    # Find half-power points for marginal Ri
    marginal_ri_half_indices = np.where(marginal_ri_psd >= half_power)[0]
    if len(marginal_ri_half_indices) > 0:
        marginal_ri_bw_start = omega_n[marginal_ri_half_indices[0]]
        marginal_ri_bw_end = omega_n[marginal_ri_half_indices[-1]]
        ax_right.annotate('', xy=(marginal_ri_bw_end, half_power - 0.1), 
                         xytext=(marginal_ri_bw_start, half_power - 0.1),
                         arrowprops=dict(arrowstyle='<->', color=STEEL_BLUE, lw=2))
        ax_right.text((marginal_ri_bw_start + marginal_ri_bw_end) / 2, half_power - 0.15, 
                     'BW', ha='center', va='top', fontsize=IN_PLOT_NOTE_SIZE,
                     color=STEEL_BLUE, fontweight='bold')
    
    # Setup axes
    setup_omega_n_axis(ax_right, xlabel=True)
    ax_right.set_ylim(0, 1)
    ax_right.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax_right.set_ylabel('Normalized PSD', fontsize=AXIS_LABEL_SIZE, fontweight='normal')
    
    # Add annotation
    ax_right.annotate('broader PSD under marginal Ri', 
                     xy=(1.2, 0.6), xytext=(1.5, 0.8),
                     fontsize=IN_PLOT_NOTE_SIZE, ha='center', va='center',
                     arrowprops=dict(arrowstyle='->', color='black', lw=1),
                     bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
    
    # Add conversion window to right panel
    add_conversion_window(ax_right, y_range=(0, 1))
    
    # Add title above both subpanels
    fig.suptitle('Figure 3.6C — Coherence loss and spectral broadening with decreasing Ri', 
                fontsize=PANEL_TITLE_SIZE, fontweight='bold', y=0.95)
    
    # Add caption beneath both subpanels
    caption = ('Coherent fraction declines monotonically with a superposed dip near marginal Ri; '
              'spectra broaden under marginal Ri, indicating enhanced shear-mediated variability.')
    fig.text(0.5, 0.02, caption, fontsize=15, style='italic', ha='center', va='bottom',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
    
    # Adjust layout
    plt.subplots_adjust(wspace=0.3, top=0.85, bottom=0.15)
    
    return fig

if __name__ == '__main__':
    fig = create_figure_3_6c()
    save_figure(fig, 'figure_3_6c')
    plt.show()