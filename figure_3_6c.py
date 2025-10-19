#!/usr/bin/env python3
"""
Figure 3.6C — Coherent fraction vs Ri and PSD broadening under marginal Ri
Two subpanels: Left shows coherent fraction vs Ri, Right shows PSD comparison
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import matplotlib.gridspec as gridspec
from matplotlib.patches import ConnectionPatch

# Set up the figure with specified styling
plt.rcParams['font.family'] = 'DejaVu Sans'  # Use available font
plt.rcParams['mathtext.default'] = 'regular'

def create_coherent_fraction_data(ri_vals):
    """
    Create coherent fraction vs Ri data:
    - Monotone decreasing from ~0.95 at Ri=2 to ~0.5 at Ri≈0.25
    - Intermittent dip: localized deeper notch (to ~0.4) centered Ri≈0.3-0.5
    """
    # Base monotonic decrease
    base_fraction = 0.95 - 0.45 * (2.0 - ri_vals) / 2.0
    
    # Add the localized dip around Ri ≈ 0.3-0.5
    dip_center = 0.4
    dip_width = 0.15
    dip_depth = 0.15  # Additional drop
    
    dip_mask = np.exp(-((ri_vals - dip_center) / dip_width)**2)
    coherent_fraction = base_fraction - dip_depth * dip_mask
    
    # Ensure it doesn't go below reasonable bounds
    coherent_fraction = np.clip(coherent_fraction, 0.3, 1.0)
    
    # Add some variability around the dip region for shaded area
    variability = np.zeros_like(ri_vals)
    variability_mask = (ri_vals >= 0.25) & (ri_vals <= 0.55)
    variability[variability_mask] = 0.05 * np.sin(10 * ri_vals[variability_mask])
    
    return coherent_fraction, variability

def create_psd_data(omega_n_vals):
    """
    Create PSD data for both high and marginal Ri cases:
    - High Ri: narrow peak near ω/N ≈ 1
    - Marginal Ri: broader peak/plateau (wider half-power bandwidth)
    """
    # High Ri: narrow peak
    high_ri_center = 1.0
    high_ri_width = 0.1
    high_ri_psd = np.exp(-((omega_n_vals - high_ri_center) / high_ri_width)**2)
    
    # Marginal Ri: broader peak
    marginal_ri_center = 1.0
    marginal_ri_width = 0.25  # Much broader
    marginal_ri_psd = np.exp(-((omega_n_vals - marginal_ri_center) / marginal_ri_width)**2)
    
    # Add some asymmetry and plateau-like behavior for marginal case
    plateau_mask = (omega_n_vals >= 0.8) & (omega_n_vals <= 1.2)
    marginal_ri_psd[plateau_mask] = np.maximum(marginal_ri_psd[plateau_mask], 0.7)
    
    # Normalize both to same peak
    high_ri_psd /= np.max(high_ri_psd)
    marginal_ri_psd /= np.max(marginal_ri_psd)
    
    return high_ri_psd, marginal_ri_psd

def calculate_bandwidth(omega_vals, psd, half_power_level=0.5):
    """Calculate bandwidth at half-power points."""
    # Find indices where PSD crosses half-power level
    above_half = psd >= half_power_level
    if not np.any(above_half):
        return 0
    
    # Find first and last indices above half power
    indices = np.where(above_half)[0]
    if len(indices) < 2:
        return 0
    
    first_idx = indices[0]
    last_idx = indices[-1]
    
    # Interpolate for more precise bandwidth
    if first_idx > 0:
        # Linear interpolation for lower edge
        frac = (half_power_level - psd[first_idx-1]) / (psd[first_idx] - psd[first_idx-1])
        lower_freq = omega_vals[first_idx-1] + frac * (omega_vals[first_idx] - omega_vals[first_idx-1])
    else:
        lower_freq = omega_vals[first_idx]
    
    if last_idx < len(psd) - 1:
        # Linear interpolation for upper edge
        frac = (half_power_level - psd[last_idx]) / (psd[last_idx+1] - psd[last_idx])
        upper_freq = omega_vals[last_idx] + frac * (omega_vals[last_idx+1] - omega_vals[last_idx])
    else:
        upper_freq = omega_vals[last_idx]
    
    return upper_freq - lower_freq, lower_freq, upper_freq

def create_figure_3_6c():
    """Create Figure 3.6C with dual subpanels."""
    
    # Create figure with two subpanels
    fig = plt.figure(figsize=(18, 9))
    fig.patch.set_facecolor('white')
    
    # Create gridspec for two panels
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1], wspace=0.3)
    
    # Left subpanel — Coherent fraction vs Ri
    ax1 = fig.add_subplot(gs[0, 0])
    
    # Define Ri range and create data
    ri_vals = np.linspace(0.0, 2.0, 200)
    coherent_fraction, variability = create_coherent_fraction_data(ri_vals)
    
    # Plot main curve
    line1 = ax1.plot(ri_vals, coherent_fraction, color='#1F78B4', linewidth=3, 
                     label='Coherent fraction')[0]
    
    # Add shaded variability region around the dip
    dip_region = (ri_vals >= 0.25) & (ri_vals <= 0.55)
    upper_bound = coherent_fraction + np.abs(variability)
    lower_bound = coherent_fraction - np.abs(variability)
    
    ax1.fill_between(ri_vals[dip_region], 
                     lower_bound[dip_region], 
                     upper_bound[dip_region], 
                     color='#457B9D', alpha=0.2, 
                     label='Variability')
    
    # Configure left panel axes
    ri_ticks = [0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0]
    ax1.set_xticks(ri_ticks)
    ax1.set_xticklabels([f'{r:.2f}' if r != int(r) else f'{int(r)}' for r in ri_ticks], fontsize=16)
    ax1.set_xlabel('$R_i$', fontsize=22)
    
    cf_ticks = [0, 0.25, 0.5, 0.75, 1.0]
    ax1.set_yticks(cf_ticks)
    ax1.set_yticklabels([f'{cf:.2f}' if cf != int(cf) else f'{int(cf)}' for cf in cf_ticks], fontsize=16)
    ax1.set_ylabel('Coherent fraction', fontsize=22)
    
    ax1.set_xlim(0, 2.0)
    ax1.set_ylim(0, 1.0)
    
    # Grid
    ax1.grid(True, color='#E5E7EB', linewidth=0.8, alpha=1.0)
    ax1.set_axisbelow(True)
    
    # Micro-notes
    ax1.text(1.5, 0.9, 'stable: high coherent\nfraction', fontsize=18, 
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax1.text(0.4, 0.15, 'marginal: extra loss\n& variability', fontsize=18,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Right subpanel — PSD broadening
    ax2 = fig.add_subplot(gs[0, 1])
    
    # Define frequency range and create PSD data
    omega_n_vals = np.linspace(0.2, 2.2, 400)
    high_ri_psd, marginal_ri_psd = create_psd_data(omega_n_vals)
    
    # Plot PSDs
    line_high = ax2.plot(omega_n_vals, high_ri_psd, color='#1F78B4', linewidth=3, 
                        linestyle='-', label='High $R_i$')[0]
    line_marginal = ax2.plot(omega_n_vals, marginal_ri_psd, color='#457B9D', linewidth=3, 
                            linestyle='--', label='Marginal $R_i$')[0]
    
    # Configure right panel axes
    omega_ticks = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
    ax2.set_xticks(omega_ticks)
    ax2.set_xticklabels([f'{w:.1f}' for w in omega_ticks], fontsize=16)
    ax2.set_xlabel('$\\omega/N$', fontsize=22)
    
    psd_ticks = [0, 0.25, 0.5, 0.75, 1.0]
    ax2.set_yticks(psd_ticks)
    ax2.set_yticklabels([f'{p:.2f}' if p != int(p) else f'{int(p)}' for p in psd_ticks], fontsize=16)
    ax2.set_ylabel('Normalized PSD', fontsize=22)
    
    ax2.set_xlim(0.2, 2.2)
    ax2.set_ylim(0, 1.0)
    
    # Grid
    ax2.grid(True, color='#E5E7EB', linewidth=0.8, alpha=1.0)
    ax2.set_axisbelow(True)
    
    # Conversion window overlay (amber band 0.8-1.2)
    conversion_window = Rectangle((0.8, 0), 0.4, 1.0, 
                                 facecolor='#F4A261', alpha=0.2, 
                                 edgecolor='none', zorder=1)
    ax2.add_patch(conversion_window)
    
    # Dotted centerline at ω/N = 1
    ax2.axvline(x=1.0, color='#9CA3AF', linestyle=':', linewidth=1, zorder=2)
    
    # Calculate and show bandwidth differences
    bw_high, low_high, up_high = calculate_bandwidth(omega_n_vals, high_ri_psd)
    bw_marginal, low_marginal, up_marginal = calculate_bandwidth(omega_n_vals, marginal_ri_psd)
    
    # Add bandwidth arrows
    y_arrow = 0.15
    # High Ri bandwidth arrow
    ax2.annotate('', xy=(up_high, y_arrow), xytext=(low_high, y_arrow),
                arrowprops=dict(arrowstyle='<->', color='#1F78B4', lw=2))
    ax2.text((low_high + up_high)/2, y_arrow - 0.05, 'BW', fontsize=16, 
             color='#1F78B4', ha='center', fontweight='bold')
    
    # Marginal Ri bandwidth arrow
    y_arrow2 = 0.08
    ax2.annotate('', xy=(up_marginal, y_arrow2), xytext=(low_marginal, y_arrow2),
                arrowprops=dict(arrowstyle='<->', color='#457B9D', lw=2))
    ax2.text((low_marginal + up_marginal)/2, y_arrow2 - 0.05, 'BW', fontsize=16, 
             color='#457B9D', ha='center', fontweight='bold')
    
    # Legend inside right subpanel
    ax2.legend(loc='upper right', fontsize=16, framealpha=0.9)
    
    # Micro-note
    ax2.text(0.05, 0.95, 'broader PSD under\nmarginal $R_i$', 
             transform=ax2.transAxes, fontsize=18, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Set line weights for axes
    for ax in [ax1, ax2]:
        for spine in ax.spines.values():
            spine.set_linewidth(2)
    
    # Main title above both panels
    fig.suptitle('Figure 3.6C — Coherence loss and spectral broadening with decreasing $R_i$', 
                 fontsize=28, fontweight='bold', y=0.95)
    
    # Caption below the panels
    caption_text = ('Coherent fraction drops with decreasing $R_i$ and shows a localized dip near marginal $R_i$; '
                   'spectra broaden under marginal $R_i$.')
    fig.text(0.5, 0.02, caption_text, fontsize=18, horizontalalignment='center',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    
    return fig

if __name__ == "__main__":
    # Create and save the figure
    fig = create_figure_3_6c()
    
    # Save as PNG (300 DPI) and PDF
    fig.savefig('figures/figure_3_6c.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    fig.savefig('figures/figure_3_6c.pdf', bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    fig.savefig('figures/figure_3_6c.svg', bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print("Figure 3.6C created successfully!")
    print("Files saved:")
    print("- figures/figure_3_6c.png (300 DPI)")
    print("- figures/figure_3_6c.pdf (vector)")
    print("- figures/figure_3_6c.svg (vector)")
    
    plt.show()