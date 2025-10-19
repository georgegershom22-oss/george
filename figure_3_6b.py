#!/usr/bin/env python3
"""
Figure 3.6B — Time–frequency TL fluctuation intensity
Left: high Ri (narrow conversion band). Right: marginal Ri (intermittent, broadband bursts).
Publication-quality figure following shared house style specifications.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

# Shared house style settings
plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 16,  # tick labels
    'axes.labelsize': 22,  # axis labels
    'axes.titlesize': 28,  # panel titles
    'axes.linewidth': 0.8,
    'grid.linewidth': 0.8,
    'grid.color': '#E5E7EB',
    'axes.grid': True,
    'axes.axisbelow': True,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white'
})

def create_high_ri_data(time, omega_N):
    """
    Create time-frequency data for high Ri case:
    - Thin horizontal ridge confined to conversion band (0.8-1.2)
    - Nearly time-steady with slight waviness
    - Background elsewhere is quiet
    """
    T, OMEGA_N = np.meshgrid(time, omega_N)
    
    # Main conversion band activity
    conversion_activity = np.exp(-((OMEGA_N - 1.0)**2 / (0.15**2)))
    
    # Time modulation (slight waviness)
    time_modulation = 1.0 + 0.3 * np.sin(2 * np.pi * T / 20) * np.exp(-((OMEGA_N - 1.0)**2 / (0.2**2)))
    
    # Background noise (very low level)
    np.random.seed(42)
    background = 0.05 * np.random.random(T.shape)
    
    # Combine components
    intensity = conversion_activity * time_modulation + background
    
    # Normalize
    intensity = np.clip(intensity / np.max(intensity), 0, 1)
    
    return intensity

def create_marginal_ri_data(time, omega_N):
    """
    Create time-frequency data for marginal Ri case:
    - Intermittent dark bursts appearing sporadically in time
    - Broader in frequency (spanning well beyond 0.8–1.2)
    - Sometimes forming oblique streaks (intrusions)
    - Persistent but less coherent band near ω/N ≈ 1
    """
    T, OMEGA_N = np.meshgrid(time, omega_N)
    
    # Base conversion band (weaker and broader than high Ri case)
    base_activity = 0.4 * np.exp(-((OMEGA_N - 1.0)**2 / (0.3**2)))
    
    # Intermittent bursts
    np.random.seed(123)
    burst_times = [8, 15, 25, 35, 42, 52]
    burst_intensity = np.zeros_like(T)
    
    for bt in burst_times:
        # Temporal burst profile
        time_burst = np.exp(-((T - bt)**2 / (3**2)))
        
        # Frequency spread (broader than conversion band)
        freq_spread = np.exp(-((OMEGA_N - (1.0 + 0.2 * np.random.randn()))**2 / (0.5**2)))
        
        # Add oblique streaks occasionally
        if np.random.rand() > 0.5:
            oblique = np.exp(-((OMEGA_N - (1.0 + 0.1 * (T - bt)))**2 / (0.3**2)))
            freq_spread = np.maximum(freq_spread, 0.7 * oblique)
        
        burst_intensity += 0.8 * time_burst * freq_spread
    
    # Additional broadband activity
    broadband = 0.3 * np.random.random(T.shape) * np.exp(-((OMEGA_N - 1.0)**2 / (0.8**2)))
    
    # Combine all components
    intensity = base_activity + burst_intensity + broadband
    
    # Normalize
    intensity = np.clip(intensity / np.max(intensity), 0, 1)
    
    return intensity

def main():
    # Create figure with dual panel layout
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 12), dpi=100)
    
    # 40 px gutter between panels (adjust subplots)
    plt.subplots_adjust(wspace=0.15)
    
    # Define axes ranges
    time = np.linspace(0, 60, 200)  # 0 to 60 seconds
    omega_N = np.linspace(0.2, 2.2, 150)
    
    # Generate data for both panels
    high_ri_data = create_high_ri_data(time, omega_N)
    marginal_ri_data = create_marginal_ri_data(time, omega_N)
    
    # Use same colormap and scale for both panels
    vmin, vmax = 0, 1
    cmap = 'viridis'
    
    # Left panel: High Ri
    im1 = ax1.imshow(high_ri_data, extent=[0, 60, 0.2, 2.2], 
                     aspect='auto', origin='lower', cmap=cmap, 
                     vmin=vmin, vmax=vmax, interpolation='bilinear')
    
    # Right panel: Marginal Ri  
    im2 = ax2.imshow(marginal_ri_data, extent=[0, 60, 0.2, 2.2], 
                     aspect='auto', origin='lower', cmap=cmap, 
                     vmin=vmin, vmax=vmax, interpolation='bilinear')
    
    # Set axes properties for both panels
    for ax in [ax1, ax2]:
        ax.set_xlabel('Time (s)', fontsize=22)
        ax.set_ylabel(r'$\omega/N$', fontsize=22)
        
        # Set tick positions
        time_ticks = np.arange(0, 61, 10)
        omega_ticks = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
        
        ax.set_xticks(time_ticks)
        ax.set_yticks(omega_ticks)
        ax.set_xticklabels([f'{int(t)}' for t in time_ticks], fontsize=16)
        ax.set_yticklabels([f'{x:.1f}' for x in omega_ticks], fontsize=16)
        
        # Add conversion window overlay
        conversion_band = Rectangle((0, 0.8), 60, 0.4, 
                                   facecolor='#F4A261', alpha=0.2, 
                                   edgecolor='none', zorder=10)
        ax.add_patch(conversion_band)
        
        # Set limits and grid
        ax.set_xlim(0, 60)
        ax.set_ylim(0.2, 2.2)
        ax.grid(True, alpha=0.3)
    
    # Add annotations to left panel
    ax1.annotate('narrow conversion-band\nmodulation', xy=(30, 1.0), xytext=(45, 1.5),
                fontsize=18, ha='center', va='center',
                arrowprops=dict(arrowstyle='->', color='white', lw=2),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Add annotations to right panel
    ax2.annotate('intermittent broadband\nbursts', xy=(25, 1.4), xytext=(10, 1.8),
                fontsize=18, ha='center', va='center',
                arrowprops=dict(arrowstyle='->', color='white', lw=2),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax2.annotate('enhanced spread beyond\nconversion', xy=(42, 0.6), xytext=(50, 0.4),
                fontsize=18, ha='center', va='center',
                arrowprops=dict(arrowstyle='->', color='white', lw=2),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Add captions inside each panel (bottom)
    ax1.text(0.5, 0.05, r'High $R_i$: fluctuation energy concentrated in a narrow conversion band.',
            transform=ax1.transAxes, fontsize=15, style='italic',
            ha='center', va='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax2.text(0.5, 0.05, r'Marginal $R_i$: intermittent broadband activity indicates shear-mediated variability.',
            transform=ax2.transAxes, fontsize=15, style='italic',
            ha='center', va='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Add shared colorbar to the right of right panel
    cbar = plt.colorbar(im2, ax=[ax1, ax2], shrink=0.8, aspect=30, pad=0.02)
    cbar.set_label('TL fluctuation intensity (arb.)', fontsize=22, labelpad=20)
    cbar.ax.tick_params(labelsize=16)
    
    # Add overall title
    fig.suptitle('Figure 3.6B — Time–frequency TL fluctuation intensity', 
                fontsize=28, fontweight='bold', y=0.95)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure
    plt.savefig('figure_3_6b.png', dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.savefig('figure_3_6b.pdf', bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print("Figure 3.6B created successfully!")
    plt.show()

if __name__ == "__main__":
    main()