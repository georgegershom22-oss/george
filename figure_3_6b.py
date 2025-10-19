"""
Figure 3.6B — Time–frequency TL fluctuation intensity
Left panel: high Ri with narrow conversion band
Right panel: marginal Ri with intermittent broadband bursts
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.ndimage import gaussian_filter

def generate_high_ri_data(time, omega_N):
    """
    Generate data for high Ri case:
    - Thin, nearly time-steady ridge confined to amber band (0.8-1.2)
    - Background quiet elsewhere
    """
    T, OMEGA = np.meshgrid(time, omega_N)
    
    # Create narrow ridge centered at ω/N ≈ 1
    center = 1.0
    width = 0.15  # Narrow band
    
    # Time-steady with small modulation
    ridge = np.exp(-((OMEGA - center) / width)**2)
    
    # Add small time modulation
    time_modulation = 1 + 0.1 * np.sin(2 * np.pi * T / 20)
    ridge *= time_modulation
    
    # Ensure it's confined to conversion band
    band_mask = (OMEGA >= 0.8) & (OMEGA <= 1.2)
    ridge *= band_mask
    
    # Add very weak background noise
    noise = np.random.RandomState(42).randn(*ridge.shape) * 0.01
    data = ridge + np.abs(noise)
    
    # Smooth slightly
    data = gaussian_filter(data, sigma=0.5)
    
    return np.clip(data, 0, 1)

def generate_marginal_ri_data(time, omega_N):
    """
    Generate data for marginal Ri case:
    - Intermittent, dark bursts appearing sporadically in time
    - Broader frequency spread (often beyond 0.8-1.2)
    - Some oblique streaks acceptable
    """
    T, OMEGA = np.meshgrid(time, omega_N)
    data = np.zeros_like(T)
    
    # Random state for reproducibility
    rng = np.random.RandomState(43)
    
    # Create intermittent bursts
    n_bursts = 8
    for _ in range(n_bursts):
        # Random burst parameters
        t_center = rng.uniform(5, 55)
        omega_center = rng.uniform(0.6, 1.4)
        t_width = rng.uniform(2, 5)
        omega_width = rng.uniform(0.3, 0.6)  # Broader than high Ri
        intensity = rng.uniform(0.6, 1.0)
        
        # Create burst
        burst = intensity * np.exp(-((T - t_center) / t_width)**2 - 
                                   ((OMEGA - omega_center) / omega_width)**2)
        data += burst
    
    # Add some oblique streaks
    for _ in range(3):
        t_start = rng.uniform(10, 40)
        omega_start = rng.uniform(0.5, 1.5)
        slope = rng.uniform(-0.01, 0.01)
        width = rng.uniform(0.15, 0.25)
        length = rng.uniform(10, 20)
        
        streak_mask = (T >= t_start) & (T <= t_start + length)
        omega_streak = omega_start + slope * (T - t_start)
        streak = 0.5 * np.exp(-((OMEGA - omega_streak) / width)**2) * streak_mask
        data += streak
    
    # Add broader background activity
    background = 0.1 * np.exp(-((OMEGA - 1.0) / 0.8)**2)
    background *= (1 + 0.3 * np.sin(2 * np.pi * T / 15 + rng.randn()))
    data += background
    
    # Apply smoothing
    data = gaussian_filter(data, sigma=1.0)
    
    return np.clip(data, 0, 1)

def create_figure_3_6b():
    # Set up figure with two panels
    fig = plt.figure(figsize=(18, 12), facecolor='white')
    
    # Create subplots with shared y-axis
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122, sharey=ax1)
    
    # Generate data
    time = np.linspace(0, 60, 300)
    omega_N = np.linspace(0.2, 2.2, 200)
    
    data_high_ri = generate_high_ri_data(time, omega_N)
    data_marginal_ri = generate_marginal_ri_data(time, omega_N)
    
    # Plot left panel (High Ri)
    im1 = ax1.pcolormesh(time, omega_N, data_high_ri, shading='auto', 
                         cmap='viridis', vmin=0, vmax=1)
    
    # Add conversion window overlay
    band1 = Rectangle((0, 0.8), 60, 0.4, 
                      facecolor='#F4A261', alpha=0.2, 
                      edgecolor='none', zorder=2)
    ax1.add_patch(band1)
    ax1.axhline(y=1.0, color='#9CA3AF', linestyle=':', linewidth=1, zorder=3)
    
    # Plot right panel (Marginal Ri)
    im2 = ax2.pcolormesh(time, omega_N, data_marginal_ri, shading='auto', 
                         cmap='viridis', vmin=0, vmax=1)
    
    # Add conversion window overlay
    band2 = Rectangle((0, 0.8), 60, 0.4, 
                      facecolor='#F4A261', alpha=0.2, 
                      edgecolor='none', zorder=2)
    ax2.add_patch(band2)
    ax2.axhline(y=1.0, color='#9CA3AF', linestyle=':', linewidth=1, zorder=3)
    
    # Set axes limits and labels
    for ax in [ax1, ax2]:
        ax.set_xlim(0, 60)
        ax.set_ylim(0.2, 2.2)
        ax.set_xlabel('Time t (s)', fontsize=22)
        ax.set_xticks(np.arange(0, 70, 10))
        ax.tick_params(axis='both', which='major', labelsize=16)
        ax.grid(True, color='#E5E7EB', linewidth=0.8, alpha=0.8)
        ax.set_axisbelow(True)
    
    # Y-axis label only on left panel
    ax1.set_ylabel('ω/N', fontsize=22)
    ax1.set_yticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    
    # Hide y-axis labels on right panel
    plt.setp(ax2.get_yticklabels(), visible=False)
    
    # Add panel labels
    ax1.text(0.5, 1.05, 'High Ri', transform=ax1.transAxes, 
             fontsize=20, ha='center', fontweight='bold')
    ax2.text(0.5, 1.05, 'Marginal Ri', transform=ax2.transAxes, 
             fontsize=20, ha='center', fontweight='bold')
    
    # Add micro-labels
    ax1.text(0.5, 0.02, 'narrow conversion-band modulation', 
             transform=ax1.transAxes, fontsize=18, ha='center', 
             style='italic', color='#333333')
    
    ax2.text(0.5, 0.08, 'intermittent broadband bursts', 
             transform=ax2.transAxes, fontsize=18, ha='center', 
             style='italic', color='#333333')
    ax2.text(0.5, 0.02, 'enhanced spread beyond conversion', 
             transform=ax2.transAxes, fontsize=18, ha='center', 
             style='italic', color='#333333')
    
    # Add shared colorbar on far right
    cbar_ax = fig.add_axes([0.92, 0.25, 0.02, 0.5])
    cbar = plt.colorbar(im2, cax=cbar_ax)
    cbar.set_label('TL fluctuation intensity (arb.)', fontsize=20)
    cbar.ax.tick_params(labelsize=16)
    
    # Add main title
    fig.suptitle('Figure 3.6B — Time–frequency TL fluctuation intensity', 
                 fontsize=28, fontweight='bold', y=0.98)
    
    # Add caption
    caption = ("High Ri: fluctuation energy confined to the conversion band. "
               "Marginal Ri: broadband, intermittent activity.")
    fig.text(0.5, 0.05, caption, fontsize=18, ha='center', style='italic')
    
    # Adjust layout
    plt.subplots_adjust(left=0.08, right=0.90, top=0.92, bottom=0.15, 
                       wspace=0.05, hspace=0.2)
    
    return fig

if __name__ == "__main__":
    fig = create_figure_3_6b()
    
    # Save in multiple formats
    fig.savefig('figure_3_6b.png', dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig('figure_3_6b.pdf', bbox_inches='tight', facecolor='white')
    fig.savefig('figure_3_6b.svg', bbox_inches='tight', facecolor='white')
    
    plt.show()
    print("Figure 3.6B saved as PNG, PDF, and SVG")