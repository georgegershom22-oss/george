#!/usr/bin/env python3
"""
Figure 3.6B — Time–frequency TL fluctuation intensity
Two equal panels side-by-side showing different Ri regimes.
Left: high Ri (narrow conversion band), Right: marginal Ri (intermittent broadband bursts)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.gridspec as gridspec

# Set up the figure with specified styling
plt.rcParams['font.family'] = 'DejaVu Sans'  # Use available font
plt.rcParams['mathtext.default'] = 'regular'

def create_high_ri_data(t_vals, omega_n_vals):
    """
    Create time-frequency data for high Ri regime:
    - Thin, nearly time-steady ridge confined to amber band (0.8–1.2)
    - Background quiet elsewhere
    """
    T, Omega_N = np.meshgrid(t_vals, omega_n_vals, indexing='ij')
    
    # Main ridge centered at ω/N ≈ 1.0, confined to conversion band
    ridge_center = 1.0
    ridge_width = 0.15  # Narrow band
    
    # Create steady ridge with slight time variation
    time_modulation = 1.0 + 0.1 * np.sin(2 * np.pi * T / 20)  # Slow modulation
    ridge_intensity = np.exp(-((Omega_N - ridge_center) / ridge_width)**2) * time_modulation
    
    # Confine to conversion band (0.8-1.2)
    conversion_mask = (Omega_N >= 0.8) & (Omega_N <= 1.2)
    ridge_intensity *= conversion_mask
    
    # Add very low background noise
    background = 0.05 * np.random.random(T.shape)
    
    # Combine
    intensity = ridge_intensity + background
    
    # Normalize
    intensity = np.clip(intensity / np.max(intensity), 0, 1)
    
    return intensity

def create_marginal_ri_data(t_vals, omega_n_vals):
    """
    Create time-frequency data for marginal Ri regime:
    - Intermittent, dark bursts appearing sporadically in time
    - Broader frequency spread (often beyond 0.8–1.2)
    - Some oblique streaks acceptable
    """
    T, Omega_N = np.meshgrid(t_vals, omega_n_vals, indexing='ij')
    
    # Initialize with low background
    intensity = 0.1 * np.random.random(T.shape)
    
    # Create intermittent bursts at random times
    np.random.seed(42)  # For reproducibility
    burst_times = [8, 15, 23, 31, 38, 47, 55]  # Irregular spacing
    
    for burst_time in burst_times:
        # Burst center frequency (can be outside conversion band)
        center_freq = 0.6 + 1.2 * np.random.random()  # Range 0.6-1.8
        
        # Burst characteristics
        time_width = 2 + 3 * np.random.random()  # Variable duration
        freq_width = 0.3 + 0.4 * np.random.random()  # Broad frequency spread
        max_intensity = 0.7 + 0.3 * np.random.random()  # Variable intensity
        
        # Create burst
        burst = max_intensity * np.exp(-((T - burst_time) / time_width)**2 - 
                                      ((Omega_N - center_freq) / freq_width)**2)
        
        # Add some oblique streaks (frequency drift)
        if np.random.random() > 0.5:
            drift_rate = 0.02 * (np.random.random() - 0.5)  # Small frequency drift
            drift_freq = center_freq + drift_rate * (T - burst_time)
            streak = 0.3 * max_intensity * np.exp(-((T - burst_time) / (time_width * 1.5))**2 - 
                                                  ((Omega_N - drift_freq) / (freq_width * 0.8))**2)
            burst += streak
        
        intensity += burst
    
    # Normalize
    intensity = np.clip(intensity / np.max(intensity), 0, 1)
    
    return intensity

def create_figure_3_6b():
    """Create Figure 3.6B with dual panels and shared colorbar."""
    
    # Create figure with two equal panels side-by-side
    fig = plt.figure(figsize=(20, 10))  # Wide for two panels
    fig.patch.set_facecolor('white')
    
    # Create gridspec for two panels plus colorbar
    gs = gridspec.GridSpec(1, 3, width_ratios=[1, 1, 0.05], wspace=0.3, hspace=0.1)
    
    # Define coordinate ranges
    t_vals = np.linspace(0, 60, 300)  # Time 0-60s
    omega_n_vals = np.linspace(0.2, 2.2, 200)  # ω/N range
    
    # Create data for both panels
    high_ri_data = create_high_ri_data(t_vals, omega_n_vals)
    marginal_ri_data = create_marginal_ri_data(t_vals, omega_n_vals)
    
    # Determine shared color scale
    vmax = max(np.max(high_ri_data), np.max(marginal_ri_data))
    
    # Left panel (High Ri)
    ax1 = fig.add_subplot(gs[0, 0])
    im1 = ax1.imshow(high_ri_data.T, extent=[0, 60, 0.2, 2.2], 
                     aspect='auto', origin='lower', cmap='viridis', vmin=0, vmax=vmax)
    
    # Right panel (Marginal Ri)
    ax2 = fig.add_subplot(gs[0, 1])
    im2 = ax2.imshow(marginal_ri_data.T, extent=[0, 60, 0.2, 2.2], 
                     aspect='auto', origin='lower', cmap='viridis', vmin=0, vmax=vmax)
    
    # Configure both panels
    for ax, title in zip([ax1, ax2], ['High $R_i$', 'Marginal $R_i$']):
        # Time axis (x)
        t_ticks = [0, 10, 20, 30, 40, 50, 60]
        ax.set_xticks(t_ticks)
        ax.set_xticklabels([f'{t}' for t in t_ticks], fontsize=16)
        ax.set_xlabel('$t$ (s)', fontsize=22)
        
        # Frequency axis (y)
        omega_ticks = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
        ax.set_yticks(omega_ticks)
        ax.set_yticklabels([f'{w:.1f}' for w in omega_ticks], fontsize=16)
        
        # Grid
        ax.grid(True, color='#E5E7EB', linewidth=0.8, alpha=1.0)
        ax.set_axisbelow(True)
        
        # Conversion window overlay (amber band 0.8-1.2)
        conversion_window = Rectangle((0, 0.8), 60, 0.4, 
                                     facecolor='#F4A261', alpha=0.2, 
                                     edgecolor='none', zorder=3)
        ax.add_patch(conversion_window)
        
        # Dotted centerline at ω/N = 1
        ax.axhline(y=1.0, color='#9CA3AF', linestyle=':', linewidth=1, zorder=4)
        
        # Panel title
        ax.text(0.5, 1.02, title, transform=ax.transAxes, fontsize=20, 
                fontweight='bold', horizontalalignment='center')
        
        # Axis line weights
        for spine in ax.spines.values():
            spine.set_linewidth(2)
    
    # Only left panel gets y-axis label
    ax1.set_ylabel(r'$\omega/N$', fontsize=22)
    
    # Remove y-axis labels from right panel (shared axis)
    ax2.set_yticklabels([])
    
    # Add micro-labels for each panel
    ax1.text(0.05, 0.95, 'narrow conversion-band\nmodulation', 
             transform=ax1.transAxes, fontsize=18, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax2.text(0.05, 0.95, 'intermittent broadband\nbursts', 
             transform=ax2.transAxes, fontsize=18, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax2.text(0.05, 0.75, 'enhanced spread beyond\nconversion', 
             transform=ax2.transAxes, fontsize=18, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Shared colorbar on the far right
    cbar_ax = fig.add_subplot(gs[0, 2])
    cbar = plt.colorbar(im2, cax=cbar_ax)
    cbar.set_label('TL fluctuation intensity (arb.)', fontsize=20, labelpad=15)
    cbar.ax.tick_params(labelsize=16)
    
    # Main title centered above both panels
    fig.suptitle('Figure 3.6B — Time–frequency TL fluctuation intensity', 
                 fontsize=28, fontweight='bold', y=0.95)
    
    # Caption below the panels
    caption_text = ('High $R_i$: fluctuation energy confined to the conversion band. '
                   'Marginal $R_i$: broadband, intermittent activity.')
    fig.text(0.5, 0.02, caption_text, fontsize=18, horizontalalignment='center',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    
    return fig

if __name__ == "__main__":
    # Create and save the figure
    fig = create_figure_3_6b()
    
    # Save as PNG (300 DPI) and PDF
    fig.savefig('figures/figure_3_6b.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    fig.savefig('figures/figure_3_6b.pdf', bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    fig.savefig('figures/figure_3_6b.svg', bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print("Figure 3.6B created successfully!")
    print("Files saved:")
    print("- figures/figure_3_6b.png (300 DPI)")
    print("- figures/figure_3_6b.pdf (vector)")
    print("- figures/figure_3_6b.svg (vector)")
    
    plt.show()