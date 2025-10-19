#!/usr/bin/env python3
"""
Generate Figures 3.6A-C following the shared house style specifications.
Canvas: 1800 × 1200 px (landscape), white background
Typeface: Helvetica/Arial with specified sizes
Color palette: deep blue #1F78B4, steel blue #457B9D, magenta #B3007D
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.gridspec as gridspec

# Set up the house style
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 16,
    'axes.linewidth': 0.8,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.color': '#E5E7EB',
    'grid.linewidth': 0.8,
    'grid.alpha': 1.0,
    'xtick.major.size': 4,
    'ytick.major.size': 4,
    'xtick.minor.size': 0,
    'ytick.minor.size': 0,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'figure.dpi': 100,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1
})

# Color palette
DEEP_BLUE = '#1F78B4'
STEEL_BLUE = '#457B9D'
MAGENTA = '#B3007D'
AMBER = '#F4A261'
GRAY = '#9CA3AF'

# Common axis ranges
OMEGA_N_RANGE = (0.2, 2.2)
RI_RANGE = (0.0, 2.0)
OMEGA_N_TICKS = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
RI_TICKS = [0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0]

def create_conversion_overlay(ax, y_range=(0, 2.0)):
    """Add the amber conversion window overlay"""
    # Amber band
    rect = patches.Rectangle((0.8, y_range[0]), 0.4, y_range[1] - y_range[0], 
                           linewidth=0, facecolor=AMBER, alpha=0.2, zorder=1)
    ax.add_patch(rect)
    
    # Dotted centerline
    ax.axvline(x=1.0, color=GRAY, linestyle=':', linewidth=1, alpha=0.8, zorder=2)

def figure_3_6a():
    """Figure 3.6A — Shear-dominance index on (Ri, ω/N)"""
    fig, ax = plt.subplots(figsize=(18, 12))
    
    # Create meshgrid
    omega_n = np.linspace(OMEGA_N_RANGE[0], OMEGA_N_RANGE[1], 200)
    ri = np.linspace(RI_RANGE[0], RI_RANGE[1], 200)
    Omega_N, Ri = np.meshgrid(omega_n, ri)
    
    # Generate SDI pattern based on physics description
    # High SDI lobe: concentrated for low-moderate Ri and near conversion window
    sdi = np.zeros_like(Ri)
    
    # Main lobe near conversion window
    conversion_mask = (Omega_N >= 0.8) & (Omega_N <= 1.2)
    low_ri_mask = Ri <= 0.6
    
    # Create the main high SDI region
    center_omega = 1.0
    center_ri = 0.4
    sigma_omega = 0.15
    sigma_ri = 0.2
    
    gaussian_lobe = np.exp(-((Omega_N - center_omega)**2 / (2 * sigma_omega**2) + 
                            (Ri - center_ri)**2 / (2 * sigma_ri**2)))
    
    # Apply decay with stability
    stability_decay = np.exp(-(Ri - 0.2) / 0.8)
    stability_decay = np.clip(stability_decay, 0, 1)
    
    # High-frequency suppression
    freq_suppression = np.where(Omega_N > 1.4, np.exp(-(Omega_N - 1.4) / 0.3), 1)
    
    # Sub-buoyancy tail
    sub_buoyancy = np.where((Omega_N < 1.0) & (Ri < 0.3), 
                           np.exp(-(1.0 - Omega_N) / 0.2) * np.exp(-Ri / 0.1), 0)
    
    # Combine all effects
    sdi = gaussian_lobe * stability_decay * freq_suppression + 0.1 * sub_buoyancy
    sdi = np.clip(sdi, 0, 1)
    
    # Create heatmap
    im = ax.contourf(Omega_N, Ri, sdi, levels=50, cmap='viridis', vmin=0, vmax=1)
    
    # Add conversion overlay
    create_conversion_overlay(ax)
    
    # Add marginal stability line
    ax.axhline(y=0.25, color='red', linestyle='--', linewidth=1, alpha=0.7)
    ax.text(1.8, 0.27, 'marginal stability', fontsize=14, color='red', ha='right')
    
    # Set axes
    ax.set_xlim(OMEGA_N_RANGE)
    ax.set_ylim(RI_RANGE)
    ax.set_xticks(OMEGA_N_TICKS)
    ax.set_yticks(RI_TICKS)
    ax.set_xlabel('ω/N', fontsize=22)
    ax.set_ylabel('Ri', fontsize=22)
    ax.tick_params(labelsize=16)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=20)
    cbar.set_label('Shear-dominance index (0–1)', fontsize=18)
    cbar.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
    cbar.ax.tick_params(labelsize=16)
    
    # Title
    ax.text(0.02, 0.98, 'Figure 3.6A — Shear-dominance index SDI(Ri,ω/N)', 
            transform=ax.transAxes, fontsize=28, fontweight='bold', 
            verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Caption
    caption = ("Bright regions indicate parameter pairs where shear-mediated loss dominates; "
              "peak influence occurs near ω/N ≈ 1 under marginal Ri, and decays at higher Ri or ω/N > 1.")
    ax.text(0.5, -0.08, caption, transform=ax.transAxes, fontsize=15, 
            style='italic', ha='center', va='top')
    
    plt.tight_layout()
    return fig

def figure_3_6b():
    """Figure 3.6B — Time–frequency TL fluctuation intensity"""
    fig = plt.figure(figsize=(18, 12))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1], wspace=0.05)
    
    # Common time and frequency arrays
    time = np.linspace(0, 60, 300)
    omega_n = np.linspace(OMEGA_N_RANGE[0], OMEGA_N_RANGE[1], 200)
    T, Omega_N = np.meshgrid(time, omega_n)
    
    # Left panel: High Ri (narrow conversion band)
    ax_left = fig.add_subplot(gs[0])
    
    # Generate narrow conversion band activity
    tl_intensity_left = np.zeros_like(Omega_N)
    
    # Create a narrow ridge near ω/N = 1 with slight waviness
    for i, t in enumerate(time):
        phase = 0.1 * np.sin(2 * np.pi * t / 20)  # Slow modulation
        center_freq = 1.0 + phase
        # Create a narrow Gaussian peak at each time step
        freq_response = np.exp(-((omega_n - center_freq) / 0.05)**2)
        tl_intensity_left[:, i] = 0.8 * freq_response
    
    # Add some background noise
    noise = 0.1 * np.random.random(Omega_N.shape)
    tl_intensity_left += noise
    
    im_left = ax_left.contourf(T, Omega_N, tl_intensity_left, levels=50, cmap='viridis', vmin=0, vmax=1)
    
    # Add conversion overlay
    create_conversion_overlay(ax_left)
    
    # Add annotation
    ax_left.annotate('narrow conversion-band modulation', 
                    xy=(30, 1.0), xytext=(20, 1.5),
                    arrowprops=dict(arrowstyle='->', color='white', lw=2),
                    fontsize=14, color='white', ha='center')
    
    ax_left.set_xlim(0, 60)
    ax_left.set_ylim(OMEGA_N_RANGE)
    ax_left.set_xticks(np.arange(0, 61, 10))
    ax_left.set_yticks(OMEGA_N_TICKS)
    ax_left.set_xlabel('time t (s)', fontsize=22)
    ax_left.set_ylabel('ω/N', fontsize=22)
    ax_left.tick_params(labelsize=16)
    ax_left.set_title('High Ri', fontsize=20, fontweight='bold', pad=20)
    
    # Right panel: Marginal Ri (intermittent, broadband bursts)
    ax_right = fig.add_subplot(gs[1])
    
    # Generate intermittent broadband activity
    tl_intensity_right = np.zeros_like(Omega_N)
    
    # Create intermittent bursts
    burst_times = [10, 25, 35, 45, 55]  # Random burst times
    for burst_time in burst_times:
        burst_duration = 5 + np.random.random() * 10
        burst_start = max(0, burst_time - burst_duration/2)
        burst_end = min(60, burst_time + burst_duration/2)
        
        # Find time indices for this burst
        time_indices = np.where((time >= burst_start) & (time <= burst_end))[0]
        
        for t_idx in time_indices:
            # Broadband frequency content
            freq_center = 0.8 + np.random.random() * 0.8  # Random center frequency
            freq_width = 0.3 + np.random.random() * 0.4  # Variable width
            
            # Create burst with some irregularity
            burst_intensity = 0.6 + 0.4 * np.random.random()
            freq_response = burst_intensity * np.exp(-((omega_n - freq_center) / freq_width)**2)
            tl_intensity_right[:, t_idx] = np.maximum(tl_intensity_right[:, t_idx], freq_response)
    
    # Add some persistent but less coherent band near ω/N ≈ 1
    for i, t in enumerate(time):
        persistent_intensity = 0.3 + 0.2 * np.random.random()
        freq_response = persistent_intensity * np.exp(-((omega_n - 1.0) / 0.2)**2)
        tl_intensity_right[:, i] = np.maximum(tl_intensity_right[:, i], freq_response)
    
    im_right = ax_right.contourf(T, Omega_N, tl_intensity_right, levels=50, cmap='viridis', vmin=0, vmax=1)
    
    # Add conversion overlay
    create_conversion_overlay(ax_right)
    
    # Add annotations
    ax_right.annotate('intermittent broadband bursts', 
                     xy=(25, 1.5), xytext=(35, 1.8),
                     arrowprops=dict(arrowstyle='->', color='white', lw=2),
                     fontsize=14, color='white', ha='center')
    
    ax_right.annotate('enhanced spread beyond conversion', 
                     xy=(45, 0.6), xytext=(50, 0.3),
                     arrowprops=dict(arrowstyle='->', color='white', lw=2),
                     fontsize=14, color='white', ha='center')
    
    ax_right.set_xlim(0, 60)
    ax_right.set_ylim(OMEGA_N_RANGE)
    ax_right.set_xticks(np.arange(0, 61, 10))
    ax_right.set_yticks(OMEGA_N_TICKS)
    ax_right.set_xlabel('time t (s)', fontsize=22)
    ax_right.set_ylabel('ω/N', fontsize=22)
    ax_right.tick_params(labelsize=16)
    ax_right.set_title('Marginal Ri', fontsize=20, fontweight='bold', pad=20)
    
    # Add shared colorbar
    cbar = fig.colorbar(im_right, ax=[ax_left, ax_right], shrink=0.8, aspect=30, pad=0.02)
    cbar.set_label('TL fluctuation intensity (arb.)', fontsize=18)
    cbar.ax.tick_params(labelsize=16)
    
    # Add captions
    ax_left.text(0.5, -0.08, 'High Ri: fluctuation energy concentrated in a narrow conversion band.', 
                transform=ax_left.transAxes, fontsize=15, style='italic', ha='center', va='top')
    ax_right.text(0.5, -0.08, 'Marginal Ri: intermittent broadband activity indicates shear-mediated variability.', 
                 transform=ax_right.transAxes, fontsize=15, style='italic', ha='center', va='top')
    
    # Main title
    fig.suptitle('Figure 3.6B — Time–frequency TL fluctuation intensity', 
                fontsize=28, fontweight='bold', y=0.95)
    
    plt.tight_layout()
    return fig

def figure_3_6c():
    """Figure 3.6C — Coherent fraction vs Ri and PSD broadening"""
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(18, 12))
    
    # Left panel: Coherent fraction vs Ri
    ri_values = np.linspace(RI_RANGE[0], RI_RANGE[1], 200)
    
    # Primary curve: monotone decreasing
    coherent_fraction = 0.95 * np.exp(-(ri_values - 2.0) / 1.5)
    coherent_fraction = np.clip(coherent_fraction, 0, 1)
    
    # Add intermittent dip near marginal Ri
    dip_center = 0.4
    dip_width = 0.3
    dip_mask = np.abs(ri_values - dip_center) <= dip_width
    dip_strength = 0.3 * np.exp(-((ri_values - dip_center) / (dip_width/2))**2)
    coherent_fraction[dip_mask] -= dip_strength[dip_mask]
    coherent_fraction = np.clip(coherent_fraction, 0, 1)
    
    # Plot main curve
    ax_left.plot(ri_values, coherent_fraction, color=DEEP_BLUE, linewidth=3, label='Coherent fraction')
    
    # Add intermittent dip shading
    dip_indices = np.abs(ri_values - dip_center) <= dip_width
    ax_left.fill_between(ri_values[dip_indices], coherent_fraction[dip_indices], 
                        alpha=0.2, color=STEEL_BLUE, label='Increased variability')
    
    # Add annotations
    ax_left.annotate('stable: high coherent fraction', 
                    xy=(1.5, 0.8), xytext=(1.2, 0.9),
                    arrowprops=dict(arrowstyle='->', color=DEEP_BLUE, lw=2),
                    fontsize=14, color=DEEP_BLUE, ha='center')
    
    ax_left.annotate('marginal: additional loss & variability', 
                    xy=(0.4, 0.4), xytext=(0.7, 0.2),
                    arrowprops=dict(arrowstyle='->', color=STEEL_BLUE, lw=2),
                    fontsize=14, color=STEEL_BLUE, ha='center')
    
    ax_left.set_xlim(RI_RANGE)
    ax_left.set_ylim(0, 1)
    ax_left.set_xticks(RI_TICKS)
    ax_left.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax_left.set_xlabel('Ri', fontsize=22)
    ax_left.set_ylabel('Coherent fraction', fontsize=22)
    ax_left.tick_params(labelsize=16)
    ax_left.grid(True, alpha=0.3)
    
    # Right panel: PSD broadening
    omega_n = np.linspace(OMEGA_N_RANGE[0], OMEGA_N_RANGE[1], 200)
    
    # High Ri PSD: narrowband peak
    high_ri_psd = np.exp(-((omega_n - 1.0) / 0.1)**2) + 0.1 * np.exp(-((omega_n - 1.0) / 0.3)**2)
    high_ri_psd = high_ri_psd / np.max(high_ri_psd)
    
    # Marginal Ri PSD: broader plateau
    marginal_ri_psd = np.exp(-((omega_n - 1.0) / 0.25)**2) + 0.3 * np.exp(-((omega_n - 1.0) / 0.4)**2)
    marginal_ri_psd = marginal_ri_psd / np.max(marginal_ri_psd)
    
    # Add some raggedness to marginal Ri
    raggedness = 0.1 * np.random.random(len(omega_n))
    marginal_ri_psd += raggedness
    marginal_ri_psd = np.clip(marginal_ri_psd, 0, 1)
    
    # Plot both curves
    ax_right.plot(omega_n, high_ri_psd, color=DEEP_BLUE, linewidth=3, label='High Ri', linestyle='-')
    ax_right.plot(omega_n, marginal_ri_psd, color=STEEL_BLUE, linewidth=3, label='Marginal Ri', linestyle='--')
    
    # Add half-power bandwidth indicators
    # High Ri bandwidth
    high_ri_half_power = np.max(high_ri_psd) / 2
    high_ri_indices = high_ri_psd >= high_ri_half_power
    if np.any(high_ri_indices):
        high_ri_bw_start = omega_n[high_ri_indices][0]
        high_ri_bw_end = omega_n[high_ri_indices][-1]
        ax_right.annotate('', xy=(high_ri_bw_start, 0.1), xytext=(high_ri_bw_end, 0.1),
                         arrowprops=dict(arrowstyle='<->', color=DEEP_BLUE, lw=2))
        ax_right.text((high_ri_bw_start + high_ri_bw_end) / 2, 0.15, 'BW', 
                     ha='center', va='bottom', fontsize=12, color=DEEP_BLUE)
    
    # Marginal Ri bandwidth
    marginal_ri_half_power = np.max(marginal_ri_psd) / 2
    marginal_ri_indices = marginal_ri_psd >= marginal_ri_half_power
    if np.any(marginal_ri_indices):
        marginal_ri_bw_start = omega_n[marginal_ri_indices][0]
        marginal_ri_bw_end = omega_n[marginal_ri_indices][-1]
        ax_right.annotate('', xy=(marginal_ri_bw_start, 0.05), xytext=(marginal_ri_bw_end, 0.05),
                         arrowprops=dict(arrowstyle='<->', color=STEEL_BLUE, lw=2))
        ax_right.text((marginal_ri_bw_start + marginal_ri_bw_end) / 2, 0.1, 'BW', 
                     ha='center', va='bottom', fontsize=12, color=STEEL_BLUE)
    
    # Add annotation
    ax_right.annotate('broader PSD under marginal Ri', 
                     xy=(1.2, 0.6), xytext=(1.5, 0.8),
                     arrowprops=dict(arrowstyle='->', color=STEEL_BLUE, lw=2),
                     fontsize=14, color=STEEL_BLUE, ha='center')
    
    # Add conversion overlay
    create_conversion_overlay(ax_right, y_range=(0, 1))
    
    ax_right.set_xlim(OMEGA_N_RANGE)
    ax_right.set_ylim(0, 1)
    ax_right.set_xticks(OMEGA_N_TICKS)
    ax_right.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax_right.set_xlabel('ω/N', fontsize=22)
    ax_right.set_ylabel('Normalized PSD', fontsize=22)
    ax_right.tick_params(labelsize=16)
    ax_right.grid(True, alpha=0.3)
    ax_right.legend(fontsize=14, loc='upper right')
    
    # Main title
    fig.suptitle('Figure 3.6C — Coherence loss and spectral broadening with decreasing Ri', 
                fontsize=28, fontweight='bold', y=0.95)
    
    # Caption
    caption = ("Coherent fraction declines monotonically with a superposed dip near marginal Ri; "
              "spectra broaden under marginal Ri, indicating enhanced shear-mediated variability.")
    fig.text(0.5, 0.02, caption, ha='center', va='bottom', fontsize=15, style='italic')
    
    plt.tight_layout()
    return fig

def main():
    """Generate all three figures"""
    print("Generating Figure 3.6A...")
    fig_a = figure_3_6a()
    fig_a.savefig('figure_3_6a.png', dpi=300, bbox_inches='tight')
    fig_a.savefig('figure_3_6a.pdf', bbox_inches='tight')
    plt.close(fig_a)
    
    print("Generating Figure 3.6B...")
    fig_b = figure_3_6b()
    fig_b.savefig('figure_3_6b.png', dpi=300, bbox_inches='tight')
    fig_b.savefig('figure_3_6b.pdf', bbox_inches='tight')
    plt.close(fig_b)
    
    print("Generating Figure 3.6C...")
    fig_c = figure_3_6c()
    fig_c.savefig('figure_3_6c.png', dpi=300, bbox_inches='tight')
    fig_c.savefig('figure_3_6c.pdf', bbox_inches='tight')
    plt.close(fig_c)
    
    print("All figures generated successfully!")
    print("Files created:")
    print("- figure_3_6a.png/pdf")
    print("- figure_3_6b.png/pdf") 
    print("- figure_3_6c.png/pdf")

if __name__ == "__main__":
    main()