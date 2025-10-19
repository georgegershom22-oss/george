#!/usr/bin/env python3
"""
Generate Figure 3.6 A, B, C for shear-dominance analysis
with exact specifications for publication quality.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import gridspec
from matplotlib.patches import Rectangle
from scipy.ndimage import gaussian_filter

# Set up matplotlib for publication quality
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial']
plt.rcParams['mathtext.default'] = 'regular'

# Color scheme (colorblind-safe)
COLORS = {
    'deep_blue': '#1F78B4',
    'steel_blue': '#457B9D',
    'amber': '#F4A261',
    'grid': '#E5E7EB',
    'dotted': '#9CA3AF',
    'magenta': '#B3007D'
}

def create_shear_dominance_field(ri_vals, omega_n_vals):
    """
    Create synthetic shear-dominance index (SDI) field.
    Bright horizontally elongated island centered ~(Ri≈0.4, ω/N≈1).
    """
    RI, OMEGA_N = np.meshgrid(ri_vals, omega_n_vals, indexing='ij')
    
    # Main bright island centered at (Ri≈0.4, ω/N≈1)
    ri_center = 0.4
    omega_center = 1.0
    
    # Horizontal elongation (wider in ω/N direction)
    ri_width = 0.3
    omega_width = 0.6
    
    # Main Gaussian peak
    main_peak = np.exp(-((RI - ri_center)**2 / (2 * ri_width**2) + 
                         (OMEGA_N - omega_center)**2 / (2 * omega_width**2)))
    
    # Decay as Ri → 1-2
    decay_high_ri = np.exp(-((RI - 1.5)**2 / (2 * 0.5**2))) * 0.3
    
    # Weak tongue for ω/N < 1 at very low Ri (shear-driven tail)
    low_ri_tail = np.exp(-((RI - 0.15)**2 / (2 * 0.15**2))) * \
                  np.exp(-((OMEGA_N - 0.6)**2 / (2 * 0.4**2))) * 0.4
    low_ri_tail *= (OMEGA_N < 1.0)
    
    # Combine components
    sdi = main_peak + decay_high_ri + low_ri_tail
    
    # Decay for ω/N > 1.4
    sdi *= np.where(OMEGA_N > 1.4, 
                    np.exp(-((OMEGA_N - 1.4)**2 / (2 * 0.8**2))), 
                    1.0)
    
    # Suppress extremes: fade top/bottom edges
    edge_fade = np.exp(-((RI - 1.0)**2 / (2 * 2.0**2)))
    sdi *= 0.3 + 0.7 * edge_fade
    
    # Smooth and normalize
    sdi = gaussian_filter(sdi, sigma=1.5)
    sdi = np.clip(sdi / sdi.max(), 0, 1)
    
    return sdi

def add_conversion_band(ax, omega_n_range, alpha=0.2, add_centerline=True):
    """Add translucent amber conversion window overlay."""
    ylim = ax.get_ylim()
    rect = Rectangle((0.8, ylim[0]), 0.4, ylim[1] - ylim[0],
                     facecolor=COLORS['amber'], alpha=alpha, 
                     edgecolor='none', zorder=2)
    ax.add_patch(rect)
    
    if add_centerline:
        ax.axvline(1.0, color=COLORS['dotted'], linestyle=':', 
                   linewidth=1, zorder=3)

def figure_3_6a():
    """Generate Figure 3.6A - Shear-dominance index heatmap."""
    # Setup
    fig = plt.figure(figsize=(18, 12), dpi=100, facecolor='white')
    ax = fig.add_subplot(111)
    
    # Define axes
    ri_vals = np.linspace(0.0, 2.0, 200)
    omega_n_vals = np.linspace(0.2, 2.2, 200)
    
    # Generate SDI field
    sdi = create_shear_dominance_field(ri_vals, omega_n_vals)
    
    # Plot heatmap with viridis colormap (darker = higher)
    im = ax.imshow(sdi, extent=[omega_n_vals[0], omega_n_vals[-1], 
                                 ri_vals[0], ri_vals[-1]],
                   aspect='auto', origin='lower', cmap='viridis',
                   interpolation='bilinear', zorder=1)
    
    # Add conversion band overlay
    add_conversion_band(ax, omega_n_vals)
    
    # Optional dashed guide at Ri = 0.25
    ax.axhline(0.25, color=COLORS['dotted'], linestyle='--', 
               linewidth=1.2, zorder=3)
    ax.text(2.05, 0.25, 'marginal stability', 
            fontsize=18, va='center', ha='left')
    
    # Axes configuration
    ax.set_xlabel(r'$\omega/N$', fontsize=22, fontweight='normal')
    ax.set_ylabel(r'$R_i$', fontsize=22, fontweight='normal')
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(0.0, 2.0)
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.set_yticks([0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
    ax.tick_params(labelsize=16, width=2)
    
    # Grid
    ax.grid(True, color=COLORS['grid'], linewidth=0.8, alpha=1.0, which='major')
    ax.set_axisbelow(True)
    
    # Spine width
    for spine in ax.spines.values():
        spine.set_linewidth(2)
    
    # Colorbar
    cbar = fig.colorbar(im, ax=ax, pad=0.02, fraction=0.046)
    cbar.set_label('Shear-dominance index (0–1)', fontsize=20, fontweight='normal')
    cbar.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
    cbar.ax.tick_params(labelsize=16)
    
    # Title inside top-left
    ax.text(0.35, 1.85, r'Figure 3.6A — $SDI(R_i, \omega/N)$', 
            fontsize=28, fontweight='bold', ha='left', va='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='none'))
    
    # Caption inside, below axis
    caption = (r"Bright regions: shear-mediated loss dominates; "
               r"peak near $\omega/N \approx 1$ under marginal $R_i$.")
    ax.text(1.2, 0.15, caption, fontsize=18, ha='center', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='none'))
    
    plt.tight_layout()
    return fig

def create_time_freq_field(time_vals, omega_n_vals, scenario='high_ri'):
    """
    Create synthetic time-frequency TL fluctuation intensity.
    scenario: 'high_ri' or 'marginal_ri'
    """
    T, OMEGA_N = np.meshgrid(time_vals, omega_n_vals, indexing='ij')
    
    if scenario == 'high_ri':
        # Thin, time-steady ridge confined to amber band (0.8-1.2)
        intensity = np.exp(-((OMEGA_N - 1.0)**2 / (2 * 0.08**2)))
        # Add some temporal modulation
        intensity *= (1.0 + 0.15 * np.sin(2 * np.pi * T / 20))
        # Confine to conversion band
        intensity *= ((OMEGA_N >= 0.8) & (OMEGA_N <= 1.2))
        
    else:  # marginal_ri
        # Intermittent broadband bursts
        intensity = np.zeros_like(T)
        
        # Add several intermittent bursts
        burst_times = [8, 18, 28, 38, 48]
        for bt in burst_times:
            # Broader frequency spread
            burst = np.exp(-((T - bt)**2 / (2 * 3.0**2)))
            # Broader frequency content
            freq_profile = (np.exp(-((OMEGA_N - 1.0)**2 / (2 * 0.3**2))) * 0.8 +
                           np.exp(-((OMEGA_N - 0.7)**2 / (2 * 0.2**2))) * 0.4 +
                           np.exp(-((OMEGA_N - 1.4)**2 / (2 * 0.25**2))) * 0.5)
            intensity += burst[:, :] * freq_profile
        
        # Add some oblique streaks
        for i in range(len(time_vals)):
            for j in range(len(omega_n_vals)):
                if (i + 2*j) % 40 < 5:
                    intensity[i, j] += 0.1 * np.random.rand()
    
    intensity = gaussian_filter(intensity, sigma=1.0)
    intensity = np.clip(intensity / intensity.max() if intensity.max() > 0 else intensity, 0, 1)
    
    return intensity

def figure_3_6b():
    """Generate Figure 3.6B - Time-frequency TL fluctuation intensity."""
    # Setup: two panels side-by-side
    fig = plt.figure(figsize=(18, 12), dpi=100, facecolor='white')
    gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.08, 
                          left=0.08, right=0.88, top=0.92, bottom=0.15)
    
    # Define axes
    time_vals = np.linspace(0, 60, 300)
    omega_n_vals = np.linspace(0.2, 2.2, 200)
    
    # Create both panels
    scenarios = ['high_ri', 'marginal_ri']
    titles = [r'High $R_i$', r'Marginal $R_i$']
    axes = []
    images = []
    
    for idx, (scenario, title) in enumerate(zip(scenarios, titles)):
        ax = fig.add_subplot(gs[0, idx])
        axes.append(ax)
        
        # Generate field
        intensity = create_time_freq_field(time_vals, omega_n_vals, scenario)
        
        # Plot
        im = ax.imshow(intensity.T, extent=[time_vals[0], time_vals[-1],
                                            omega_n_vals[0], omega_n_vals[-1]],
                       aspect='auto', origin='lower', cmap='viridis',
                       interpolation='bilinear', zorder=1)
        images.append(im)
        
        # Add conversion band
        ax.axhspan(0.8, 1.2, facecolor=COLORS['amber'], alpha=0.2, zorder=2)
        ax.axhline(1.0, color=COLORS['dotted'], linestyle=':', 
                   linewidth=1, zorder=3)
        
        # Axes configuration
        ax.set_xlabel('Time $t$ (s)', fontsize=22)
        ax.set_xlim(0, 60)
        ax.set_xticks(np.arange(0, 70, 10))
        ax.set_ylim(0.2, 2.2)
        ax.set_yticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
        ax.tick_params(labelsize=16, width=2)
        
        if idx == 0:
            ax.set_ylabel(r'$\omega/N$', fontsize=22)
        else:
            ax.set_yticklabels([])
        
        # Grid
        ax.grid(True, color=COLORS['grid'], linewidth=0.8, alpha=1.0, which='major')
        ax.set_axisbelow(True)
        
        # Spines
        for spine in ax.spines.values():
            spine.set_linewidth(2)
        
        # Panel title
        ax.text(0.5, 1.05, title, fontsize=24, fontweight='bold',
                ha='center', va='bottom', transform=ax.transAxes)
        
        # Add micro-labels
        if scenario == 'high_ri':
            ax.text(30, 1.0, 'narrow conversion-band\nmodulation', 
                    fontsize=18, ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                             alpha=0.8, edgecolor='none'))
        else:
            ax.text(15, 1.6, 'intermittent\nbroadband bursts', 
                    fontsize=18, ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                             alpha=0.8, edgecolor='none'))
            ax.text(45, 0.5, 'enhanced spread\nbeyond conversion', 
                    fontsize=18, ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                             alpha=0.8, edgecolor='none'))
    
    # Shared colorbar on far right
    cbar_ax = fig.add_axes([0.90, 0.15, 0.02, 0.77])
    cbar = fig.colorbar(images[0], cax=cbar_ax)
    cbar.set_label('TL fluctuation intensity (arb.)', fontsize=20)
    cbar.ax.tick_params(labelsize=16)
    
    # Overall title
    fig.text(0.5, 0.97, 'Figure 3.6B — Time–frequency TL fluctuation intensity',
             fontsize=28, fontweight='bold', ha='center', va='top')
    
    # Caption
    caption = (r"High $R_i$: fluctuation energy confined to the conversion band. "
               r"Marginal $R_i$: broadband, intermittent activity.")
    fig.text(0.5, 0.08, caption, fontsize=18, ha='center', va='top',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='white', 
                     alpha=0.9, edgecolor='gray', linewidth=1))
    
    return fig

def figure_3_6c():
    """Generate Figure 3.6C - Coherent fraction and PSD broadening."""
    # Setup: two subpanels
    fig = plt.figure(figsize=(18, 12), dpi=100, facecolor='white')
    gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.15,
                          left=0.08, right=0.95, top=0.88, bottom=0.15)
    
    # LEFT PANEL: Coherent fraction vs Ri
    ax1 = fig.add_subplot(gs[0, 0])
    
    ri_vals = np.linspace(0.0, 2.0, 200)
    
    # Monotone decreasing from ~0.95 at Ri=2 to ~0.5 at Ri≈0.25
    coherent_frac = 0.5 + 0.45 * (1 / (1 + np.exp(-3 * (ri_vals - 0.8))))
    
    # Add localized deeper notch centered Ri ≈ 0.3-0.5 (to ~0.4)
    notch_center = 0.4
    notch_width = 0.15
    notch = -0.2 * np.exp(-((ri_vals - notch_center)**2 / (2 * notch_width**2)))
    coherent_frac += notch
    
    # Plot main curve
    ax1.plot(ri_vals, coherent_frac, color=COLORS['deep_blue'], 
             linewidth=3, solid_capstyle='round', solid_joinstyle='round')
    
    # Shaded variability region around notch
    notch_mask = (ri_vals >= 0.25) & (ri_vals <= 0.55)
    ax1.fill_between(ri_vals[notch_mask], 
                     coherent_frac[notch_mask] - 0.05,
                     coherent_frac[notch_mask] + 0.05,
                     color=COLORS['steel_blue'], alpha=0.2, zorder=1)
    
    # Axes configuration
    ax1.set_xlabel(r'$R_i$', fontsize=22)
    ax1.set_ylabel('Coherent fraction', fontsize=22)
    ax1.set_xlim(0.0, 2.0)
    ax1.set_ylim(0, 1)
    ax1.set_xticks([0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
    ax1.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax1.tick_params(labelsize=16, width=2)
    
    # Grid
    ax1.grid(True, color=COLORS['grid'], linewidth=0.8, alpha=1.0, which='major')
    ax1.set_axisbelow(True)
    
    # Spines
    for spine in ax1.spines.values():
        spine.set_linewidth(2)
    
    # Micro-notes
    ax1.text(1.5, 0.92, 'stable:\nhigh coherent fraction', 
             fontsize=18, ha='center', va='top',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                      alpha=0.8, edgecolor='none'))
    ax1.text(0.4, 0.3, 'marginal:\nextra loss &\nvariability', 
             fontsize=18, ha='center', va='top',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                      alpha=0.8, edgecolor='none'))
    
    # RIGHT PANEL: PSD broadening
    ax2 = fig.add_subplot(gs[0, 1])
    
    omega_n_vals = np.linspace(0.2, 2.2, 300)
    
    # High Ri: narrow peak near ω/N ≈ 1
    psd_high_ri = np.exp(-((omega_n_vals - 1.0)**2 / (2 * 0.12**2)))
    
    # Marginal Ri: broader peak/plateau
    psd_marginal = (0.7 * np.exp(-((omega_n_vals - 1.0)**2 / (2 * 0.35**2))) +
                    0.3 * np.exp(-((omega_n_vals - 0.85)**2 / (2 * 0.25**2))))
    
    # Normalize
    psd_high_ri /= psd_high_ri.max()
    psd_marginal /= psd_marginal.max()
    
    # Plot curves
    ax2.plot(omega_n_vals, psd_high_ri, color=COLORS['deep_blue'], 
             linewidth=3, linestyle='-', label=r'High $R_i$',
             solid_capstyle='round', solid_joinstyle='round')
    ax2.plot(omega_n_vals, psd_marginal, color=COLORS['steel_blue'], 
             linewidth=3, linestyle='--', label=r'Marginal $R_i$',
             solid_capstyle='round', solid_joinstyle='round', dashes=(8, 4))
    
    # Add conversion band overlay
    ax2.axvspan(0.8, 1.2, facecolor=COLORS['amber'], alpha=0.2, zorder=1)
    ax2.axvline(1.0, color=COLORS['dotted'], linestyle=':', linewidth=1, zorder=2)
    
    # Axes configuration
    ax2.set_xlabel(r'$\omega/N$', fontsize=22)
    ax2.set_ylabel('Normalized PSD', fontsize=22)
    ax2.set_xlim(0.2, 2.2)
    ax2.set_ylim(0, 1)
    ax2.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax2.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax2.tick_params(labelsize=16, width=2)
    
    # Grid
    ax2.grid(True, color=COLORS['grid'], linewidth=0.8, alpha=1.0, which='major')
    ax2.set_axisbelow(True)
    
    # Spines
    for spine in ax2.spines.values():
        spine.set_linewidth(2)
    
    # Legend
    ax2.legend(loc='upper right', fontsize=18, framealpha=0.9, 
              edgecolor='gray', frameon=True)
    
    # Micro-note
    ax2.text(1.5, 0.7, r'broader PSD under$\ $' + '\n' + r'marginal $R_i$', 
             fontsize=18, ha='center', va='center',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                      alpha=0.8, edgecolor='none'))
    
    # Optional bandwidth arrows (simplified as text markers)
    # High Ri bandwidth marker
    half_max_high = psd_high_ri.max() * 0.5
    idx_high = np.where(psd_high_ri >= half_max_high)[0]
    bw_high = omega_n_vals[idx_high[-1]] - omega_n_vals[idx_high[0]]
    
    # Marginal Ri bandwidth marker
    half_max_marg = psd_marginal.max() * 0.5
    idx_marg = np.where(psd_marginal >= half_max_marg)[0]
    bw_marg = omega_n_vals[idx_marg[-1]] - omega_n_vals[idx_marg[0]]
    
    # Draw bandwidth indicators
    ax2.annotate('', xy=(omega_n_vals[idx_high[-1]], 0.1), 
                xytext=(omega_n_vals[idx_high[0]], 0.1),
                arrowprops=dict(arrowstyle='<->', color=COLORS['deep_blue'], 
                               lw=2))
    ax2.text(1.0, 0.15, f'BW', fontsize=16, ha='center', 
            color=COLORS['deep_blue'], fontweight='bold')
    
    ax2.annotate('', xy=(omega_n_vals[idx_marg[-1]], 0.05), 
                xytext=(omega_n_vals[idx_marg[0]], 0.05),
                arrowprops=dict(arrowstyle='<->', color=COLORS['steel_blue'], 
                               lw=2))
    ax2.text(1.0, 0.08, f'BW', fontsize=16, ha='center', 
            color=COLORS['steel_blue'], fontweight='bold')
    
    # Overall title
    fig.text(0.5, 0.95, r'Figure 3.6C — Coherence loss and spectral broadening with decreasing $R_i$',
             fontsize=28, fontweight='bold', ha='center', va='top')
    
    # Caption
    caption = (r"Coherent fraction drops with decreasing $R_i$ and shows a localized dip near marginal $R_i$; "
               r"spectra broaden under marginal $R_i$.")
    fig.text(0.5, 0.08, caption, fontsize=18, ha='center', va='top',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='white', 
                     alpha=0.9, edgecolor='gray', linewidth=1))
    
    return fig

def main():
    """Generate all three figures."""
    print("Generating Figure 3.6A - Shear-dominance index heatmap...")
    fig_a = figure_3_6a()
    fig_a.savefig('figure_3_6a.png', dpi=300, bbox_inches='tight', facecolor='white')
    fig_a.savefig('figure_3_6a.pdf', bbox_inches='tight', facecolor='white')
    print("  ✓ Saved: figure_3_6a.png (300 dpi) and figure_3_6a.pdf")
    
    print("\nGenerating Figure 3.6B - Time-frequency TL fluctuation intensity...")
    fig_b = figure_3_6b()
    fig_b.savefig('figure_3_6b.png', dpi=300, bbox_inches='tight', facecolor='white')
    fig_b.savefig('figure_3_6b.pdf', bbox_inches='tight', facecolor='white')
    print("  ✓ Saved: figure_3_6b.png (300 dpi) and figure_3_6b.pdf")
    
    print("\nGenerating Figure 3.6C - Coherence loss and spectral broadening...")
    fig_c = figure_3_6c()
    fig_c.savefig('figure_3_6c.png', dpi=300, bbox_inches='tight', facecolor='white')
    fig_c.savefig('figure_3_6c.pdf', bbox_inches='tight', facecolor='white')
    print("  ✓ Saved: figure_3_6c.png (300 dpi) and figure_3_6c.pdf")
    
    print("\n" + "="*60)
    print("All figures generated successfully!")
    print("="*60)
    print("\nOutput files:")
    print("  - figure_3_6a.png / .pdf")
    print("  - figure_3_6b.png / .pdf")
    print("  - figure_3_6c.png / .pdf")
    print("\nEach figure exported as:")
    print("  • PNG at 300 dpi (for drafts)")
    print("  • PDF with vector graphics (for editing/publication)")

if __name__ == '__main__':
    main()
