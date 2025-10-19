#!/usr/bin/env python3
"""
Combined Figure 3.6A–C: Single publication-quality figure with three panels
- 3.6A: Shear-dominance index heatmap
- 3.6B: Time-frequency TL fluctuation intensity (two side-by-side panels)  
- 3.6C: Coherent fraction vs Ri (left) and PSD broadening (right)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import sys
import os

# Add the figs directory to path to import house_style
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from house_style import *

def generate_sdi_data():
    """Generate synthetic shear-dominance index data for 3.6A."""
    omega_n = np.linspace(OMEGA_N_RANGE[0], OMEGA_N_RANGE[1], 100)
    ri = np.linspace(RI_RANGE[0], RI_RANGE[1], 80)
    OMG, RI = np.meshgrid(omega_n, ri)
    
    # High SDI lobe: concentrated for low-moderate Ri and near conversion window
    # Peak at (Ri≈0.4, ω/N≈1)
    sdi_peak = np.exp(-((OMG - 1.0)**2 / (0.3**2) + (RI - 0.4)**2 / (0.2**2)))
    
    # Rapid decay with stability
    stability_decay = np.exp(-RI / 0.5)
    
    # High-frequency suppression
    freq_suppression = np.exp(-np.maximum(0, OMG - 1.4) / 0.3)
    
    # Sub-buoyancy tail
    sub_buoyancy = 0.3 * np.exp(-((OMG - 0.6)**2 / (0.4**2) + (RI - 0.2)**2 / (0.15**2)))
    
    # Combine effects
    sdi = (sdi_peak + sub_buoyancy) * stability_decay * freq_suppression
    
    # Normalize to 0-1 range
    sdi = sdi / np.max(sdi)
    
    return omega_n, ri, sdi

def generate_timefreq_data():
    """Generate synthetic time-frequency data for 3.6B."""
    t = np.linspace(0, 60, 300)  # 60 seconds
    omega_n = np.linspace(OMEGA_N_RANGE[0], OMEGA_N_RANGE[1], 100)
    T, OMG = np.meshgrid(t, omega_n)
    
    # High Ri case: narrow conversion band
    high_ri = np.exp(-((OMG - 1.0)**2 / (0.1**2))) * (1 + 0.3 * np.sin(T / 5))
    
    # Marginal Ri case: intermittent broadband bursts
    # Base conversion band activity
    base_activity = 0.5 * np.exp(-((OMG - 1.0)**2 / (0.15**2)))
    
    # Intermittent bursts
    burst_times = [15, 25, 40, 50]
    marginal_ri = base_activity.copy()
    
    for bt in burst_times:
        burst_mask = np.exp(-((T - bt)**2 / (3**2)))
        burst_freq = np.exp(-((OMG - 1.2)**2 / (0.8**2))) + 0.7 * np.exp(-((OMG - 0.7)**2 / (0.6**2)))
        marginal_ri += 2.0 * burst_mask * burst_freq
    
    # Add some noise
    marginal_ri += 0.1 * np.random.random(marginal_ri.shape)
    
    return t, omega_n, high_ri, marginal_ri

def generate_coherence_psd_data():
    """Generate synthetic data for 3.6C."""
    ri_vals = np.linspace(RI_RANGE[0], RI_RANGE[1], 100)
    omega_n_vals = np.linspace(OMEGA_N_RANGE[0], OMEGA_N_RANGE[1], 200)
    
    # Coherent fraction vs Ri (monotone decreasing with dip)
    coherent_base = 0.95 * np.exp(-ri_vals / 3.0) + 0.5
    # Add intermittent dip near marginal Ri
    dip_mask = np.exp(-((ri_vals - 0.4)**2 / (0.15**2)))
    coherent_fraction = coherent_base - 0.15 * dip_mask
    coherent_fraction = np.clip(coherent_fraction, 0.4, 0.95)
    
    # PSD data: narrow vs broad
    psd_high_ri = np.exp(-((omega_n_vals - 1.0)**2 / (0.15**2)))  # Narrow peak
    psd_marginal_ri = 0.8 * np.exp(-((omega_n_vals - 1.0)**2 / (0.35**2))) + \
                      0.4 * np.exp(-((omega_n_vals - 1.2)**2 / (0.25**2)))  # Broader
    
    # Normalize PSDs
    psd_high_ri = psd_high_ri / np.max(psd_high_ri)
    psd_marginal_ri = psd_marginal_ri / np.max(psd_marginal_ri)
    
    return ri_vals, omega_n_vals, coherent_fraction, psd_high_ri, psd_marginal_ri

def create_combined_figure():
    """Create the combined figure with all three panels."""
    
    # Create figure with proper aspect ratio for all panels
    fig = setup_figure(width_inch=16, height_inch=12)
    
    # Define subplot layout: 2 rows, with complex arrangement
    # Top row: 3.6A (left 2/3) and 3.6C-left (right 1/3)
    # Middle row: 3.6B (full width, two panels)
    # Bottom row: 3.6C-right (centered)
    
    # Create grid spec for complex layout
    gs = fig.add_gridspec(3, 6, height_ratios=[1, 1, 0.8], hspace=0.3, wspace=0.4)
    
    # ===== PANEL 3.6A: Shear-dominance index =====
    ax_3_6a = fig.add_subplot(gs[0, :4])  # Top row, left 4 columns
    
    omega_n, ri, sdi = generate_sdi_data()
    
    # Create heatmap with cividis (darker = higher)
    im_sdi = ax_3_6a.imshow(sdi, extent=[OMEGA_N_RANGE[0], OMEGA_N_RANGE[1], 
                                        RI_RANGE[0], RI_RANGE[1]], 
                           aspect='auto', origin='lower', cmap='cividis', vmin=0, vmax=1)
    
    setup_omega_n_axis(ax_3_6a, show_xlabel=True)
    setup_ri_axis(ax_3_6a, show_ylabel=True)
    add_conversion_window(ax_3_6a)
    
    # Add marginal stability guide
    ax_3_6a.axhline(y=0.25, color='gray', linewidth=1, linestyle='--', alpha=0.7)
    ax_3_6a.text(0.3, 0.3, 'marginal stability', fontsize=INPLOT_NOTE_SIZE-2, 
                color='gray', rotation=0)
    
    add_panel_title(ax_3_6a, 'Figure 3.6A — Shear-dominance index SDI($R_i$,ω/N)')
    
    # Add colorbar for 3.6A
    cbar_sdi = add_colorbar(fig, im_sdi, ax_3_6a, 'Shear-dominance index (0–1)', 
                           ticks=[0, 0.25, 0.5, 0.75, 1.0])
    
    # ===== PANEL 3.6B: Time-frequency TL fluctuation =====
    ax_3_6b_left = fig.add_subplot(gs[1, :3])   # Middle row, left 3 columns
    ax_3_6b_right = fig.add_subplot(gs[1, 3:])  # Middle row, right 3 columns
    
    t, omega_n_tf, high_ri_data, marginal_ri_data = generate_timefreq_data()
    
    # Shared color scale
    vmax_tf = max(np.max(high_ri_data), np.max(marginal_ri_data))
    
    # Left panel: High Ri
    im_high = ax_3_6b_left.imshow(high_ri_data, extent=[0, 60, OMEGA_N_RANGE[0], OMEGA_N_RANGE[1]], 
                                 aspect='auto', origin='lower', cmap='cividis', vmin=0, vmax=vmax_tf)
    
    ax_3_6b_left.set_xlabel('Time (s)', fontsize=AXIS_LABEL_SIZE)
    setup_omega_n_axis(ax_3_6b_left, show_xlabel=False)
    ax_3_6b_left.set_ylabel('ω/N', fontsize=AXIS_LABEL_SIZE)
    add_conversion_window(ax_3_6b_left)
    
    # Add annotation
    ax_3_6b_left.text(0.95, 0.85, 'narrow conversion-band\nmodulation', 
                     transform=ax_3_6b_left.transAxes, fontsize=INPLOT_NOTE_SIZE-2,
                     horizontalalignment='right', verticalalignment='top',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Right panel: Marginal Ri  
    im_marg = ax_3_6b_right.imshow(marginal_ri_data, extent=[0, 60, OMEGA_N_RANGE[0], OMEGA_N_RANGE[1]], 
                                  aspect='auto', origin='lower', cmap='cividis', vmin=0, vmax=vmax_tf)
    
    ax_3_6b_right.set_xlabel('Time (s)', fontsize=AXIS_LABEL_SIZE)
    setup_omega_n_axis(ax_3_6b_right, show_xlabel=False)
    ax_3_6b_right.set_yticklabels([])  # Remove y-tick labels for right panel
    add_conversion_window(ax_3_6b_right)
    
    # Add annotations with arrows
    ax_3_6b_right.annotate('intermittent broadband\nbursts', xy=(25, 1.5), xytext=(45, 1.8),
                          fontsize=INPLOT_NOTE_SIZE-2, ha='center',
                          arrowprops=dict(arrowstyle='->', color='white', lw=1.5),
                          bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7, edgecolor='white'),
                          color='white')
    
    ax_3_6b_right.text(0.05, 0.15, 'enhanced spread\nbeyond conversion', 
                      transform=ax_3_6b_right.transAxes, fontsize=INPLOT_NOTE_SIZE-2,
                      horizontalalignment='left', verticalalignment='bottom',
                      bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Add shared colorbar for 3.6B
    cbar_tf = add_colorbar(fig, im_marg, [ax_3_6b_left, ax_3_6b_right], 
                          'TL fluctuation intensity (arb.)')
    
    # Panel titles for 3.6B
    add_panel_title(ax_3_6b_left, 'Figure 3.6B — Time–frequency TL fluctuation intensity')
    
    # Captions inside panels
    ax_3_6b_left.text(0.5, 0.05, 'High $R_i$: fluctuation energy concentrated\nin a narrow conversion band', 
                     transform=ax_3_6b_left.transAxes, fontsize=CAPTION_SIZE,
                     style='italic', horizontalalignment='center', verticalalignment='bottom',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
    
    ax_3_6b_right.text(0.5, 0.05, 'Marginal $R_i$: intermittent broadband activity\nindicates shear-mediated variability', 
                      transform=ax_3_6b_right.transAxes, fontsize=CAPTION_SIZE,
                      style='italic', horizontalalignment='center', verticalalignment='bottom',
                      bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
    
    # ===== PANEL 3.6C: Coherence and PSD =====
    ax_3_6c_left = fig.add_subplot(gs[0, 4:])   # Top row, right 2 columns
    ax_3_6c_right = fig.add_subplot(gs[2, 1:5]) # Bottom row, centered 4 columns
    
    ri_vals, omega_n_vals, coherent_fraction, psd_high_ri, psd_marginal_ri = generate_coherence_psd_data()
    
    # Left subpanel: Coherent fraction vs Ri
    ax_3_6c_left.plot(ri_vals, coherent_fraction, color=DEEP_BLUE, linewidth=3, label='Coherent fraction')
    
    # Add variability band around marginal Ri
    band_mask = (ri_vals >= 0.25) & (ri_vals <= 0.55)
    band_lower = coherent_fraction - 0.05
    band_upper = coherent_fraction + 0.05
    ax_3_6c_left.fill_between(ri_vals[band_mask], band_lower[band_mask], band_upper[band_mask], 
                             color=STEEL_BLUE, alpha=0.2, label='Variability')
    
    setup_ri_axis(ax_3_6c_left, show_ylabel=False)
    ax_3_6c_left.set_xlabel('$R_i$', fontsize=AXIS_LABEL_SIZE)
    ax_3_6c_left.set_ylabel('Coherent fraction', fontsize=AXIS_LABEL_SIZE)
    ax_3_6c_left.set_ylim(0, 1)
    ax_3_6c_left.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    
    # Annotations
    ax_3_6c_left.annotate('stable: high\ncoherent fraction', xy=(1.5, 0.8), xytext=(1.2, 0.9),
                         fontsize=INPLOT_NOTE_SIZE-2, ha='center',
                         arrowprops=dict(arrowstyle='->', color=DEEP_BLUE))
    
    ax_3_6c_left.annotate('marginal: additional\nloss & variability', xy=(0.4, 0.55), xytext=(0.7, 0.3),
                         fontsize=INPLOT_NOTE_SIZE-2, ha='center',
                         arrowprops=dict(arrowstyle='->', color=DEEP_BLUE))
    
    # Right subpanel: PSD broadening
    ax_3_6c_right.plot(omega_n_vals, psd_high_ri, color=DEEP_BLUE, linewidth=3, 
                      linestyle='-', label='High $R_i$')
    ax_3_6c_right.plot(omega_n_vals, psd_marginal_ri, color=STEEL_BLUE, linewidth=3, 
                      linestyle='--', label='Marginal $R_i$')
    
    setup_omega_n_axis(ax_3_6c_right, show_xlabel=True)
    ax_3_6c_right.set_ylabel('Normalized PSD', fontsize=AXIS_LABEL_SIZE)
    ax_3_6c_right.set_ylim(0, 1)
    ax_3_6c_right.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    add_conversion_window(ax_3_6c_right)
    
    # Add legend
    ax_3_6c_right.legend(loc='upper right', frameon=False)
    
    # Add note about broadening
    ax_3_6c_right.text(0.7, 0.8, 'broader PSD under\nmarginal $R_i$', 
                      transform=ax_3_6c_right.transAxes, fontsize=INPLOT_NOTE_SIZE-2,
                      horizontalalignment='center',
                      bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7))
    
    # Panel titles for 3.6C
    add_panel_title(ax_3_6c_left, 'Figure 3.6C — Coherence loss and spectral broadening')
    
    # Overall figure caption
    fig.text(0.5, 0.02, 'Shear-mediated attenuation effects: (A) dominance index peaks near ω/N≈1 under marginal $R_i$; ' +
             '(B) time-frequency signatures show narrow vs broadband variability; ' +
             '(C) coherent fraction declines with spectral broadening under marginal $R_i$.', 
             fontsize=CAPTION_SIZE, style='italic', ha='center', va='bottom', wrap=True)
    
    return fig

def main():
    """Generate and save the combined figure."""
    print("Generating combined Figure 3.6A–C...")
    
    # Check for required packages
    try:
        import numpy as np
        import matplotlib.pyplot as plt
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install with: pip install numpy matplotlib")
        return
    
    # Generate figure
    fig = create_combined_figure()
    
    # Save outputs
    output_path = "../out/figures/figure_3_6_combined"
    save_figure(fig, output_path)
    
    print("Combined figure generation complete!")
    plt.show()

if __name__ == "__main__":
    main()