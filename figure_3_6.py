#!/usr/bin/env python3
"""
Figure 3.6: Shear-dominance analysis visualization
Following shared house style specifications
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
from scipy import signal, ndimage
import warnings
warnings.filterwarnings('ignore')

# Set up the shared house style
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial'],
    'font.size': 22,
    'axes.labelsize': 22,
    'axes.titlesize': 28,
    'axes.titleweight': 'bold',
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'legend.fontsize': 18,
    'figure.titlesize': 28,
    'axes.grid': True,
    'grid.color': '#E5E7EB',
    'grid.linewidth': 0.8,
    'grid.alpha': 1.0,
    'axes.axisbelow': True,
    'legend.frameon': False,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.linewidth': 1.2,
    'xtick.major.width': 1.0,
    'ytick.major.width': 1.0,
    'xtick.major.size': 5,
    'ytick.major.size': 5,
})

# Color palette
DEEP_BLUE = '#1F78B4'
STEEL_BLUE = '#457B9D'
MAGENTA = '#B3007D'
AMBER = '#F4A261'
GRAY_DOTTED = '#9CA3AF'

def create_shear_dominance_index(omega_N, Ri):
    """Generate shear-dominance index data"""
    O, R = np.meshgrid(omega_N, Ri)
    
    # Create SDI with physics-based structure
    # Peak near Ri ≈ 0.4, ω/N ≈ 1
    center_omega = 1.0
    center_ri = 0.4
    
    # Main lobe - horizontally elongated
    gaussian_omega = np.exp(-((O - center_omega) / 0.3)**2)
    gaussian_ri = np.exp(-((R - center_ri) / 0.25)**2)
    main_lobe = gaussian_omega * gaussian_ri
    
    # Rapid decay with stability
    stability_decay = np.exp(-1.5 * np.maximum(R - 0.6, 0))
    
    # High-frequency suppression
    freq_suppression = 1.0 / (1.0 + np.maximum(O - 1.4, 0)**2)
    
    # Sub-buoyancy tail at low Ri
    sub_buoy_tail = 0.3 * np.exp(-R / 0.2) * np.exp(-((O - 0.6) / 0.4)**2)
    
    # Combine components
    SDI = main_lobe * stability_decay * freq_suppression + sub_buoy_tail
    
    # Normalize to [0, 1]
    SDI = SDI / np.max(SDI)
    
    # Smooth slightly
    SDI = ndimage.gaussian_filter(SDI, sigma=0.5)
    
    return SDI

def add_conversion_window(ax):
    """Add the conversion window overlay"""
    rect = patches.Rectangle((0.8, 0), 0.4, 2.0, 
                            linewidth=0, 
                            edgecolor='none',
                            facecolor=AMBER, 
                            alpha=0.2,
                            zorder=1)
    ax.add_patch(rect)
    ax.axvline(x=1.0, color=GRAY_DOTTED, linestyle=':', linewidth=1, zorder=2)

# ============================================================================
# Figure 3.6A - Shear-dominance index
# ============================================================================

def create_figure_3_6A():
    """Create Figure 3.6A - Shear-dominance index heatmap"""
    
    fig = plt.figure(figsize=(18, 12), facecolor='white', dpi=100)
    ax = fig.add_subplot(111)
    
    # Generate data
    omega_N = np.linspace(0.2, 2.2, 200)
    Ri = np.linspace(0.0, 2.0, 150)
    SDI = create_shear_dominance_index(omega_N, Ri)
    
    # Create heatmap
    im = ax.pcolormesh(omega_N, Ri, SDI, cmap='viridis', shading='auto', zorder=0)
    
    # Add conversion window
    add_conversion_window(ax)
    
    # Add marginal stability line
    ax.axhline(y=0.25, color='#666666', linestyle='--', linewidth=1, alpha=0.6)
    ax.text(2.15, 0.25, 'marginal stability', fontsize=14, 
            va='center', ha='right', style='italic', color='#666666')
    
    # Set axes
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(0.0, 2.0)
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.set_yticks([0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
    
    # Labels
    ax.set_xlabel(r'$\omega/N$', fontsize=22)
    ax.set_ylabel(r'$Ri$', fontsize=22)
    
    # Title
    ax.set_title(r'Figure 3.6A — Shear-dominance index $SDI(Ri, \omega/N)$', 
                fontsize=28, fontweight='bold', loc='left', pad=20)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, pad=0.02)
    cbar.set_label('Shear-dominance index (0–1)', fontsize=18)
    cbar.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
    cbar.ax.tick_params(labelsize=14)
    
    # Caption
    fig.text(0.5, 0.06, 
            'Bright regions indicate parameter pairs where shear-mediated loss dominates; '
            r'peak influence occurs near $\omega/N ≈ 1$ under marginal $Ri$, '
            r'and decays at higher $Ri$ or $\omega/N > 1$.',
            ha='center', fontsize=15, style='italic', wrap=True)
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.12)
    return fig

# ============================================================================
# Figure 3.6B - Time-frequency TL fluctuation intensity
# ============================================================================

def create_time_frequency_data(t, omega_N, high_Ri=True):
    """Generate time-frequency data for TL fluctuation"""
    T, O = np.meshgrid(t, omega_N)
    
    if high_Ri:
        # Narrow conversion band, steady
        base = np.exp(-((O - 1.0) / 0.1)**2)
        # Add slight waviness
        waviness = 0.05 * np.sin(2 * np.pi * T / 20)
        data = base * (1 + waviness)
    else:
        # Marginal Ri - intermittent broadband bursts
        # Persistent band near ω/N ≈ 1
        persistent = 0.3 * np.exp(-((O - 1.0) / 0.3)**2)
        
        # Intermittent bursts
        burst_data = np.zeros_like(T)
        np.random.seed(42)
        
        # Create several bursts at random times
        burst_times = [15, 28, 42, 51]
        for bt in burst_times:
            time_window = np.exp(-((T - bt) / 3)**2)
            freq_spread = 0.4 + 0.3 * np.random.random()
            freq_center = 0.6 + 0.8 * np.random.random()
            freq_window = np.exp(-((O - freq_center) / freq_spread)**2)
            burst_data += time_window * freq_window * (0.7 + 0.3 * np.random.random())
        
        # Add oblique streaks
        for i in range(3):
            t0 = 10 + 40 * np.random.random()
            slope = 0.01 + 0.02 * np.random.random()
            streak = np.exp(-((O - 0.8 - slope * (T - t0)) / 0.15)**2) * \
                    np.exp(-((T - t0) / 5)**2)
            burst_data += 0.5 * streak
        
        data = persistent + burst_data
    
    # Normalize and add some noise
    data = data / np.max(data)
    data += 0.05 * np.random.randn(*data.shape)
    data = np.maximum(data, 0)
    
    return data

def create_figure_3_6B():
    """Create Figure 3.6B - Time-frequency TL fluctuation intensity"""
    
    fig = plt.figure(figsize=(18, 12), facecolor='white', dpi=100)
    
    # Create two panels with gutter
    gs = GridSpec(1, 2, figure=fig, wspace=0.15, hspace=0.0,
                  left=0.08, right=0.92, top=0.88, bottom=0.15)
    
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])
    
    # Generate data
    t = np.linspace(0, 60, 300)
    omega_N = np.linspace(0.2, 2.2, 200)
    
    data_high_Ri = create_time_frequency_data(t, omega_N, high_Ri=True)
    data_marginal_Ri = create_time_frequency_data(t, omega_N, high_Ri=False)
    
    # Determine common color scale
    vmin = 0
    vmax = max(np.max(data_high_Ri), np.max(data_marginal_Ri))
    
    # Left panel - High Ri
    im1 = ax1.pcolormesh(t, omega_N, data_high_Ri, cmap='viridis', 
                         vmin=vmin, vmax=vmax, shading='auto', zorder=0)
    add_conversion_window(ax1)
    
    # Annotation for left panel
    ax1.annotate('narrow conversion-band\nmodulation', xy=(30, 1.0), 
                xytext=(40, 1.5), fontsize=18,
                arrowprops=dict(arrowstyle='->', color='white', lw=1),
                color='white', ha='center')
    
    # Right panel - Marginal Ri
    im2 = ax2.pcolormesh(t, omega_N, data_marginal_Ri, cmap='viridis',
                         vmin=vmin, vmax=vmax, shading='auto', zorder=0)
    add_conversion_window(ax2)
    
    # Annotations for right panel
    ax2.annotate('intermittent\nbroadband bursts', xy=(15, 1.3),
                xytext=(10, 1.8), fontsize=18,
                arrowprops=dict(arrowstyle='->', color='white', lw=1),
                color='white')
    
    ax2.annotate('enhanced spread\nbeyond conversion', xy=(42, 0.6),
                xytext=(50, 0.4), fontsize=18,
                arrowprops=dict(arrowstyle='->', color='white', lw=1),
                color='white')
    
    # Set axes for both panels
    for ax in [ax1, ax2]:
        ax.set_xlim(0, 60)
        ax.set_ylim(0.2, 2.2)
        ax.set_xticks([0, 10, 20, 30, 40, 50, 60])
        ax.set_yticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
        ax.set_xlabel('Time (s)', fontsize=22)
    
    ax1.set_ylabel(r'$\omega/N$', fontsize=22)
    ax2.set_ylabel('')  # No ylabel for right panel
    
    # Panel captions
    ax1.text(0.5, -0.18, r'High $Ri$: fluctuation energy concentrated in a narrow conversion band.',
            transform=ax1.transAxes, ha='center', fontsize=15, style='italic')
    
    ax2.text(0.5, -0.18, r'Marginal $Ri$: intermittent broadband activity indicates shear-mediated variability.',
            transform=ax2.transAxes, ha='center', fontsize=15, style='italic')
    
    # Single colorbar for both panels
    cbar = plt.colorbar(im2, ax=[ax1, ax2], pad=0.02)
    cbar.set_label('TL fluctuation intensity (arb.)', fontsize=18)
    cbar.ax.tick_params(labelsize=14)
    
    # Main title
    fig.suptitle('Figure 3.6B — Time–frequency TL fluctuation intensity', 
                fontsize=28, fontweight='bold', x=0.08, y=0.95, ha='left')
    
    return fig

# ============================================================================
# Figure 3.6C - Coherent fraction and PSD broadening
# ============================================================================

def create_figure_3_6C():
    """Create Figure 3.6C - Coherent fraction vs Ri and PSD broadening"""
    
    fig = plt.figure(figsize=(18, 12), facecolor='white', dpi=100)
    
    # Create two subpanels
    gs = GridSpec(1, 2, figure=fig, wspace=0.3, hspace=0.0,
                  left=0.08, right=0.95, top=0.88, bottom=0.15)
    
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])
    
    # Left panel - Coherent fraction vs Ri
    Ri_vals = np.linspace(0.0, 2.0, 200)
    
    # Base monotonic decrease
    coherent_base = 0.5 + 0.45 * (1 - np.exp(-2 * (2.0 - Ri_vals)))
    
    # Add notch near marginal Ri
    notch_center = 0.4
    notch_width = 0.2
    notch_depth = 0.1
    notch = notch_depth * np.exp(-((Ri_vals - notch_center) / notch_width)**2)
    coherent_fraction = coherent_base - notch
    
    # Plot main curve
    ax1.plot(Ri_vals, coherent_fraction, color=DEEP_BLUE, linewidth=3)
    
    # Add variability band around notch
    notch_region = (Ri_vals >= 0.25) & (Ri_vals <= 0.55)
    ax1.fill_between(Ri_vals[notch_region], 
                     coherent_fraction[notch_region] - 0.05,
                     coherent_fraction[notch_region] + 0.05,
                     color=STEEL_BLUE, alpha=0.2)
    
    # Annotations
    ax1.annotate('stable: high\ncoherent fraction', xy=(1.5, 0.85),
                fontsize=16, ha='center')
    ax1.annotate('marginal: additional\nloss & variability', xy=(0.4, 0.35),
                xytext=(0.7, 0.25), fontsize=16,
                arrowprops=dict(arrowstyle='->', color='black', lw=1))
    
    # Set axes
    ax1.set_xlim(0.0, 2.0)
    ax1.set_ylim(0, 1.0)
    ax1.set_xticks([0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
    ax1.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax1.set_xlabel(r'$Ri$', fontsize=22)
    ax1.set_ylabel('Coherent fraction', fontsize=22)
    ax1.grid(True, color='#E5E7EB', linewidth=0.8)
    
    # Right panel - PSD broadening
    omega_N_vals = np.linspace(0.2, 2.2, 500)
    
    # High Ri PSD - narrow peak
    psd_high_ri = np.exp(-((omega_N_vals - 1.0) / 0.15)**2)
    
    # Marginal Ri PSD - broader with some structure
    psd_marginal_base = np.exp(-((omega_N_vals - 1.0) / 0.35)**2)
    # Add some raggedness
    np.random.seed(123)
    noise = 0.05 * np.random.randn(len(omega_N_vals))
    noise = ndimage.gaussian_filter1d(noise, 5)
    psd_marginal = psd_marginal_base * (1 + noise)
    psd_marginal = np.maximum(psd_marginal, 0)
    
    # Normalize
    psd_high_ri = psd_high_ri / np.max(psd_high_ri)
    psd_marginal = psd_marginal / np.max(psd_marginal)
    
    # Plot curves
    ax2.plot(omega_N_vals, psd_high_ri, color=DEEP_BLUE, linewidth=3, 
            label=r'High $Ri$', linestyle='-')
    ax2.plot(omega_N_vals, psd_marginal, color=STEEL_BLUE, linewidth=3,
            label=r'Marginal $Ri$', linestyle='--')
    
    # Add bandwidth indicators
    # Find half-power points
    half_power = 0.5
    
    # High Ri bandwidth
    idx_high = np.where(psd_high_ri >= half_power)[0]
    if len(idx_high) > 0:
        bw_high_start = omega_N_vals[idx_high[0]]
        bw_high_end = omega_N_vals[idx_high[-1]]
        ax2.annotate('', xy=(bw_high_start, 0.48), xytext=(bw_high_end, 0.48),
                    arrowprops=dict(arrowstyle='<->', color=DEEP_BLUE, lw=1.5))
        ax2.text((bw_high_start + bw_high_end)/2, 0.45, 'BW', 
                fontsize=14, ha='center', color=DEEP_BLUE)
    
    # Marginal Ri bandwidth
    idx_marginal = np.where(psd_marginal >= half_power)[0]
    if len(idx_marginal) > 0:
        bw_marginal_start = omega_N_vals[idx_marginal[0]]
        bw_marginal_end = omega_N_vals[idx_marginal[-1]]
        ax2.annotate('', xy=(bw_marginal_start, 0.52), xytext=(bw_marginal_end, 0.52),
                    arrowprops=dict(arrowstyle='<->', color=STEEL_BLUE, lw=1.5))
        ax2.text((bw_marginal_start + bw_marginal_end)/2, 0.55, 'BW',
                fontsize=14, ha='center', color=STEEL_BLUE)
    
    # Add annotation
    ax2.annotate(r'broader PSD under' + '\n' + r'marginal $Ri$', xy=(1.3, 0.7),
                fontsize=16, ha='center')
    
    # Add conversion window
    add_conversion_window(ax2)
    
    # Set axes
    ax2.set_xlim(0.2, 2.2)
    ax2.set_ylim(0, 1.05)
    ax2.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax2.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax2.set_xlabel(r'$\omega/N$', fontsize=22)
    ax2.set_ylabel('Normalized PSD', fontsize=22)
    ax2.grid(True, color='#E5E7EB', linewidth=0.8)
    ax2.legend(loc='upper right', fontsize=18)
    
    # Main title
    fig.suptitle(r'Figure 3.6C — Coherence loss and spectral broadening with decreasing $Ri$',
                fontsize=28, fontweight='bold', x=0.08, y=0.95, ha='left')
    
    # Caption
    fig.text(0.5, 0.06,
            r'Coherent fraction declines monotonically with a superposed dip near marginal $Ri$; '
            r'spectra broaden under marginal $Ri$, indicating enhanced shear-mediated variability.',
            ha='center', fontsize=15, style='italic', wrap=True)
    
    return fig

# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__":
    print("Generating Figure 3.6A - Shear-dominance index...")
    fig_3_6A = create_figure_3_6A()
    fig_3_6A.savefig('figure_3_6A.png', dpi=150, bbox_inches='tight', facecolor='white')
    fig_3_6A.savefig('figure_3_6A.pdf', bbox_inches='tight', facecolor='white')
    print("  Saved: figure_3_6A.png and figure_3_6A.pdf")
    
    print("\nGenerating Figure 3.6B - Time-frequency TL fluctuation intensity...")
    fig_3_6B = create_figure_3_6B()
    fig_3_6B.savefig('figure_3_6B.png', dpi=150, bbox_inches='tight', facecolor='white')
    fig_3_6B.savefig('figure_3_6B.pdf', bbox_inches='tight', facecolor='white')
    print("  Saved: figure_3_6B.png and figure_3_6B.pdf")
    
    print("\nGenerating Figure 3.6C - Coherent fraction and PSD broadening...")
    fig_3_6C = create_figure_3_6C()
    fig_3_6C.savefig('figure_3_6C.png', dpi=150, bbox_inches='tight', facecolor='white')
    fig_3_6C.savefig('figure_3_6C.pdf', bbox_inches='tight', facecolor='white')
    print("  Saved: figure_3_6C.png and figure_3_6C.pdf")
    
    print("\nAll figures generated successfully!")
    plt.show()