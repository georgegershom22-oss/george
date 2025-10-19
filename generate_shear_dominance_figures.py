#!/usr/bin/env python3
"""
Generate Figure 3.6A, 3.6B, and 3.6C for shear-dominance analysis
Specifications: 1800×1200 px landscape, Helvetica/Arial typography, precise styling
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches
from scipy.ndimage import gaussian_filter
import os

# Set up matplotlib for high-quality output
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
plt.rcParams['font.size'] = 16
plt.rcParams['axes.linewidth'] = 2
plt.rcParams['lines.linewidth'] = 3
plt.rcParams['grid.linewidth'] = 0.8
plt.rcParams['grid.alpha'] = 0.7

# Color definitions (CB-safe)
DEEP_BLUE = '#1F78B4'
STEEL_BLUE = '#457B9D'
AMBER = '#F4A261'
GRID_COLOR = '#E5E7EB'
DOTTED_CENTERLINE = '#9CA3AF'
MAGENTA = '#B3007D'

def create_shear_dominance_data():
    """Generate synthetic shear-dominance index data based on physics"""
    # Create coordinate grids
    omega_n = np.linspace(0.2, 2.2, 200)
    ri = np.linspace(0.0, 2.0, 150)
    Omega_N, Ri = np.meshgrid(omega_n, ri)
    
    # Physics-based shear-dominance index
    # Bright island centered around (Ri≈0.4, ω/N≈1)
    center_ri = 0.4
    center_omega = 1.0
    
    # Distance from center
    dist_ri = np.abs(Ri - center_ri)
    dist_omega = np.abs(Omega_N - center_omega)
    
    # Main island: Gaussian-like decay
    main_island = np.exp(-(dist_ri**2 / 0.3**2 + dist_omega**2 / 0.4**2))
    
    # Decay as Ri approaches 1-2
    ri_decay = np.exp(-np.maximum(0, Ri - 0.6) / 0.4)
    
    # Decay for ω/N > 1.4
    omega_decay = np.exp(-np.maximum(0, Omega_N - 1.2) / 0.3)
    
    # Weak tongue for ω/N < 1 at very low Ri
    tongue = np.exp(-(dist_ri**2 / 0.1**2 + np.maximum(0, 1.0 - Omega_N)**2 / 0.2**2))
    tongue = tongue * (Ri < 0.3) * (Omega_N < 1.0) * 0.3
    
    # Combine all components
    sdi = main_island * ri_decay * omega_decay + tongue
    
    # Smooth the result
    sdi = gaussian_filter(sdi, sigma=1.0)
    
    # Normalize to 0-1 range
    sdi = (sdi - sdi.min()) / (sdi.max() - sdi.min())
    
    return omega_n, ri, sdi

def create_time_frequency_data():
    """Generate synthetic time-frequency TL fluctuation data"""
    time = np.linspace(0, 60, 300)
    omega_n = np.linspace(0.2, 2.2, 200)
    T, Omega_N = np.meshgrid(time, omega_n)
    
    # High Ri case: narrow, steady ridge in conversion band
    high_ri_data = np.zeros_like(T)
    conversion_mask = (Omega_N >= 0.8) & (Omega_N <= 1.2)
    high_ri_data[conversion_mask] = 0.8 + 0.2 * np.sin(2 * np.pi * T[conversion_mask] / 20)
    
    # Marginal Ri case: intermittent broadband bursts
    marginal_ri_data = np.zeros_like(T)
    
    # Add intermittent bursts
    burst_times = [10, 25, 35, 50]
    for t_burst in burst_times:
        # Time envelope
        time_env = np.exp(-((T - t_burst) / 8)**2)
        
        # Frequency spread (broader than conversion band)
        freq_center = 1.0 + 0.3 * np.sin(t_burst / 10)
        freq_spread = 0.6 + 0.2 * np.sin(t_burst / 15)
        freq_env = np.exp(-((Omega_N - freq_center) / freq_spread)**2)
        
        # Add some oblique streaks
        oblique = np.exp(-((Omega_N - freq_center - 0.1 * (T - t_burst)) / 0.3)**2)
        
        burst = time_env * (freq_env + 0.3 * oblique)
        marginal_ri_data += burst
    
    # Add some background noise
    marginal_ri_data += 0.1 * np.random.random(marginal_ri_data.shape)
    
    # Normalize both datasets
    high_ri_data = (high_ri_data - high_ri_data.min()) / (high_ri_data.max() - high_ri_data.min())
    marginal_ri_data = (marginal_ri_data - marginal_ri_data.min()) / (marginal_ri_data.max() - marginal_ri_data.min())
    
    return time, omega_n, high_ri_data, marginal_ri_data

def create_coherence_data():
    """Generate coherent fraction and PSD data"""
    ri_values = np.linspace(0.0, 2.0, 200)
    omega_n = np.linspace(0.2, 2.2, 200)
    
    # Coherent fraction: decreases from ~0.95 to ~0.5
    coherent_frac = 0.95 - 0.45 * (ri_values / 2.0)**2
    
    # Add localized dip near Ri ≈ 0.3-0.5
    dip_center = 0.4
    dip_width = 0.2
    dip_depth = 0.15
    dip = dip_depth * np.exp(-((ri_values - dip_center) / dip_width)**2)
    coherent_frac -= dip
    
    # Ensure values stay in [0, 1]
    coherent_frac = np.clip(coherent_frac, 0, 1)
    
    # PSD data
    # High Ri: narrow peak
    high_ri_psd = np.exp(-((omega_n - 1.0) / 0.15)**2)
    
    # Marginal Ri: broader peak
    marginal_ri_psd = np.exp(-((omega_n - 1.0) / 0.35)**2)
    
    # Normalize
    high_ri_psd = high_ri_psd / high_ri_psd.max()
    marginal_ri_psd = marginal_ri_psd / marginal_ri_psd.max()
    
    return ri_values, omega_n, coherent_frac, high_ri_psd, marginal_ri_psd

def create_figure_3_6a():
    """Create Figure 3.6A - Shear-dominance index heatmap"""
    fig, ax = plt.subplots(figsize=(18, 12))
    
    # Generate data
    omega_n, ri, sdi = create_shear_dominance_data()
    
    # Create heatmap
    im = ax.imshow(sdi, extent=[0.2, 2.2, 0.0, 2.0], aspect='auto', 
                   origin='lower', cmap='viridis', interpolation='bilinear')
    
    # Add amber conversion window overlay
    conversion_rect = patches.Rectangle((0.8, 0.0), 0.4, 2.0, 
                                       facecolor=AMBER, alpha=0.2, 
                                       edgecolor='none', zorder=1)
    ax.add_patch(conversion_rect)
    
    # Add dotted centerline
    ax.axvline(x=1.0, color=DOTTED_CENTERLINE, linestyle=':', linewidth=1, zorder=2)
    
    # Add optional dashed guide at Ri = 0.25
    ax.axhline(y=0.25, color=STEEL_BLUE, linestyle='--', linewidth=1.5, alpha=0.7, zorder=2)
    
    # Set up axes
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(0.0, 2.0)
    ax.set_xlabel('ω/N', fontsize=22, fontweight='bold')
    ax.set_ylabel('Ri', fontsize=22, fontweight='bold')
    
    # Set ticks
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.set_yticks([0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
    ax.tick_params(labelsize=16)
    
    # Grid
    ax.grid(True, color=GRID_COLOR, linewidth=0.8, alpha=0.7)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=20)
    cbar.set_label('Shear-dominance index (0–1)', fontsize=18, fontweight='bold')
    cbar.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
    cbar.ax.tick_params(labelsize=16)
    
    # Title
    ax.text(0.05, 0.95, 'Figure 3.6A — SDI(Ri, ω/N)', 
            transform=ax.transAxes, fontsize=28, fontweight='bold',
            verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', 
            facecolor='white', alpha=0.8))
    
    # Caption
    ax.text(0.5, 0.02, 'Bright regions: shear-mediated loss dominates; peak near ω/N≈1 under marginal Ri.', 
            transform=ax.transAxes, fontsize=18, ha='center', va='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Marginal stability label
    ax.text(2.15, 0.25, 'marginal\nstability', fontsize=16, ha='right', va='center',
            color=STEEL_BLUE, fontweight='bold')
    
    plt.tight_layout()
    return fig

def create_figure_3_6b():
    """Create Figure 3.6B - Time-frequency TL fluctuation intensity"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 12), sharey=True)
    
    # Generate data
    time, omega_n, high_ri_data, marginal_ri_data = create_time_frequency_data()
    
    # Left panel - High Ri
    im1 = ax1.imshow(high_ri_data, extent=[0, 60, 0.2, 2.2], aspect='auto', 
                     origin='lower', cmap='viridis', interpolation='bilinear')
    
    # Add amber conversion band
    conversion_rect1 = patches.Rectangle((0, 0.8), 60, 0.4, 
                                        facecolor=AMBER, alpha=0.2, 
                                        edgecolor='none', zorder=1)
    ax1.add_patch(conversion_rect1)
    ax1.axhline(y=1.0, color=DOTTED_CENTERLINE, linestyle=':', linewidth=1, zorder=2)
    
    ax1.set_xlim(0, 60)
    ax1.set_ylim(0.2, 2.2)
    ax1.set_xlabel('time t (s)', fontsize=22, fontweight='bold')
    ax1.set_ylabel('ω/N', fontsize=22, fontweight='bold')
    ax1.set_title('High Ri', fontsize=20, fontweight='bold', pad=20)
    ax1.set_xticks(np.arange(0, 61, 10))
    ax1.set_yticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax1.tick_params(labelsize=16)
    ax1.grid(True, color=GRID_COLOR, linewidth=0.8, alpha=0.7)
    
    # Micro-label for left panel
    ax1.text(0.02, 0.98, 'narrow conversion-band modulation', 
             transform=ax1.transAxes, fontsize=16, ha='left', va='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Right panel - Marginal Ri
    im2 = ax2.imshow(marginal_ri_data, extent=[0, 60, 0.2, 2.2], aspect='auto', 
                     origin='lower', cmap='viridis', interpolation='bilinear')
    
    # Add amber conversion band
    conversion_rect2 = patches.Rectangle((0, 0.8), 60, 0.4, 
                                        facecolor=AMBER, alpha=0.2, 
                                        edgecolor='none', zorder=1)
    ax2.add_patch(conversion_rect2)
    ax2.axhline(y=1.0, color=DOTTED_CENTERLINE, linestyle=':', linewidth=1, zorder=2)
    
    ax2.set_xlim(0, 60)
    ax2.set_ylim(0.2, 2.2)
    ax2.set_xlabel('time t (s)', fontsize=22, fontweight='bold')
    ax2.set_title('Marginal Ri', fontsize=20, fontweight='bold', pad=20)
    ax2.set_xticks(np.arange(0, 61, 10))
    ax2.tick_params(labelsize=16)
    ax2.grid(True, color=GRID_COLOR, linewidth=0.8, alpha=0.7)
    
    # Micro-labels for right panel
    ax2.text(0.02, 0.98, 'intermittent broadband bursts', 
             transform=ax2.transAxes, fontsize=16, ha='left', va='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    ax2.text(0.02, 0.92, 'enhanced spread beyond conversion', 
             transform=ax2.transAxes, fontsize=16, ha='left', va='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Shared colorbar
    fig.subplots_adjust(right=0.85)
    cbar_ax = fig.add_axes([0.87, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(im1, cax=cbar_ax)
    cbar.set_label('TL fluctuation intensity (arb.)', fontsize=18, fontweight='bold')
    cbar.ax.tick_params(labelsize=16)
    
    # Main title
    fig.suptitle('Figure 3.6B — Time–frequency TL fluctuation intensity', 
                 fontsize=28, fontweight='bold', y=0.95)
    
    # Caption
    fig.text(0.5, 0.05, 'High Ri: fluctuation energy confined to the conversion band. Marginal Ri: broadband, intermittent activity.', 
             ha='center', va='bottom', fontsize=18,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    return fig

def create_figure_3_6c():
    """Create Figure 3.6C - Coherence loss and spectral broadening"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 12))
    
    # Generate data
    ri_values, omega_n, coherent_frac, high_ri_psd, marginal_ri_psd = create_coherence_data()
    
    # Left panel - Coherent fraction vs Ri
    ax1.plot(ri_values, coherent_frac, color=DEEP_BLUE, linewidth=3, label='Coherent fraction')
    
    # Add shaded region for the dip
    dip_mask = (ri_values >= 0.3) & (ri_values <= 0.5)
    ax1.fill_between(ri_values[dip_mask], coherent_frac[dip_mask], 
                     alpha=0.2, color=STEEL_BLUE, zorder=0)
    
    ax1.set_xlim(0.0, 2.0)
    ax1.set_ylim(0.0, 1.0)
    ax1.set_xlabel('Ri', fontsize=22, fontweight='bold')
    ax1.set_ylabel('Coherent fraction', fontsize=22, fontweight='bold')
    ax1.set_xticks([0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
    ax1.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax1.tick_params(labelsize=16)
    ax1.grid(True, color=GRID_COLOR, linewidth=0.8, alpha=0.7)
    
    # Micro-notes
    ax1.text(0.7, 0.9, 'stable: high coherent fraction', fontsize=16, 
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    ax1.text(0.3, 0.3, 'marginal: extra loss & variability', fontsize=16,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Right panel - PSD broadening
    ax2.plot(omega_n, high_ri_psd, color=DEEP_BLUE, linewidth=3, label='High Ri', linestyle='-')
    ax2.plot(omega_n, marginal_ri_psd, color=STEEL_BLUE, linewidth=3, label='Marginal Ri', linestyle='--')
    
    # Add amber conversion band
    conversion_rect = patches.Rectangle((0.8, 0.0), 0.4, 1.0, 
                                       facecolor=AMBER, alpha=0.2, 
                                       edgecolor='none', zorder=0)
    ax2.add_patch(conversion_rect)
    ax2.axvline(x=1.0, color=DOTTED_CENTERLINE, linestyle=':', linewidth=1, zorder=1)
    
    ax2.set_xlim(0.2, 2.2)
    ax2.set_ylim(0.0, 1.0)
    ax2.set_xlabel('ω/N', fontsize=22, fontweight='bold')
    ax2.set_ylabel('Normalized PSD', fontsize=22, fontweight='bold')
    ax2.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax2.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax2.tick_params(labelsize=16)
    ax2.grid(True, color=GRID_COLOR, linewidth=0.8, alpha=0.7)
    
    # Add bandwidth arrows
    # High Ri bandwidth
    high_ri_half_max = 0.5
    high_ri_indices = np.where(high_ri_psd >= high_ri_half_max)[0]
    if len(high_ri_indices) > 0:
        high_ri_bw_start = omega_n[high_ri_indices[0]]
        high_ri_bw_end = omega_n[high_ri_indices[-1]]
        ax2.annotate('', xy=(high_ri_bw_end, 0.1), xytext=(high_ri_bw_start, 0.1),
                    arrowprops=dict(arrowstyle='<->', color=MAGENTA, lw=2))
        ax2.text((high_ri_bw_start + high_ri_bw_end)/2, 0.15, 'BW', 
                ha='center', va='bottom', fontsize=14, color=MAGENTA, fontweight='bold')
    
    # Marginal Ri bandwidth
    marginal_ri_half_max = 0.5
    marginal_ri_indices = np.where(marginal_ri_psd >= marginal_ri_half_max)[0]
    if len(marginal_ri_indices) > 0:
        marginal_ri_bw_start = omega_n[marginal_ri_indices[0]]
        marginal_ri_bw_end = omega_n[marginal_ri_indices[-1]]
        ax2.annotate('', xy=(marginal_ri_bw_end, 0.05), xytext=(marginal_ri_bw_start, 0.05),
                    arrowprops=dict(arrowstyle='<->', color=MAGENTA, lw=2))
        ax2.text((marginal_ri_bw_start + marginal_ri_bw_end)/2, 0.08, 'BW', 
                ha='center', va='bottom', fontsize=14, color=MAGENTA, fontweight='bold')
    
    # Micro-note
    ax2.text(0.05, 0.95, 'broader PSD under marginal Ri', fontsize=16,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Legend
    ax2.legend(loc='upper right', fontsize=16, framealpha=0.9)
    
    # Main title
    fig.suptitle('Figure 3.6C — Coherence loss and spectral broadening with decreasing Ri', 
                 fontsize=28, fontweight='bold', y=0.95)
    
    # Caption
    fig.text(0.5, 0.05, 'Coherent fraction drops with decreasing Ri and shows a localized dip near marginal Ri; spectra broaden under marginal Ri.', 
             ha='center', va='bottom', fontsize=18,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    return fig

def main():
    """Generate all three figures and export in multiple formats"""
    print("Generating Figure 3.6A - Shear-dominance index...")
    fig_a = create_figure_3_6a()
    
    print("Generating Figure 3.6B - Time-frequency TL fluctuation intensity...")
    fig_b = create_figure_3_6b()
    
    print("Generating Figure 3.6C - Coherence loss and spectral broadening...")
    fig_c = create_figure_3_6c()
    
    # Create output directory
    os.makedirs('figures', exist_ok=True)
    
    # Export figures
    formats = ['png', 'pdf', 'svg']
    dpi = 300
    
    for fmt in formats:
        print(f"Exporting figures as {fmt.upper()}...")
        fig_a.savefig(f'figures/Figure_3_6A.{fmt}', dpi=dpi, bbox_inches='tight', 
                     facecolor='white', edgecolor='none')
        fig_b.savefig(f'figures/Figure_3_6B.{fmt}', dpi=dpi, bbox_inches='tight', 
                     facecolor='white', edgecolor='none')
        fig_c.savefig(f'figures/Figure_3_6C.{fmt}', dpi=dpi, bbox_inches='tight', 
                     facecolor='white', edgecolor='none')
    
    print("All figures generated successfully!")
    print("Files saved in 'figures/' directory:")
    print("  - Figure_3_6A.{png,pdf,svg}")
    print("  - Figure_3_6B.{png,pdf,svg}")
    print("  - Figure_3_6C.{png,pdf,svg}")
    
    # Show figures
    plt.show()

if __name__ == "__main__":
    main()