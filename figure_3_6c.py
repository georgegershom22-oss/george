#!/usr/bin/env python3
"""
Figure 3.6C — (Left) coherent fraction vs Ri; (Right) PSD broadening under marginal Ri
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

def coherent_fraction_curve(Ri):
    """
    Create coherent fraction vs Ri curve:
    - Monotone decreasing from ~0.95 at Ri=2 to ~0.5 at Ri≈0.25
    - Intermittent dip near marginal Ri: sharper local notch centered around Ri≈0.3-0.5
    """
    # Base monotonic decrease
    base_curve = 0.95 * np.exp(-0.3 * (2.0 - Ri)) + 0.5
    
    # Additional dip near marginal Ri
    dip_center = 0.4
    dip_width = 0.15
    dip_depth = 0.15
    
    dip = -dip_depth * np.exp(-((Ri - dip_center)**2) / (2 * dip_width**2))
    
    coherent_frac = base_curve + dip
    
    # Ensure reasonable bounds
    coherent_frac = np.clip(coherent_frac, 0.3, 1.0)
    
    return coherent_frac

def psd_curves(omega_N):
    """
    Create PSD curves for high vs marginal Ri:
    - High Ri: narrowband peak centered near ω/N≈1 with modest shoulders
    - Marginal Ri: broader plateau/peak, visibly wider half-power bandwidth
    """
    # High Ri curve: narrow peak
    high_ri_psd = np.exp(-((omega_N - 1.0)**2) / (2 * 0.15**2))
    
    # Marginal Ri curve: broader peak with some raggedness
    marginal_ri_psd = 0.9 * np.exp(-((omega_N - 1.0)**2) / (2 * 0.35**2))
    
    # Add some raggedness to marginal Ri curve
    np.random.seed(42)
    raggedness = 0.1 * np.random.randn(len(omega_N))
    raggedness = np.convolve(raggedness, np.ones(5)/5, mode='same')  # smooth the noise
    marginal_ri_psd += raggedness * marginal_ri_psd
    
    # Normalize both curves
    high_ri_psd = np.clip(high_ri_psd / np.max(high_ri_psd), 0, 1)
    marginal_ri_psd = np.clip(marginal_ri_psd / np.max(marginal_ri_psd), 0, 1)
    
    return high_ri_psd, marginal_ri_psd

def calculate_half_power_bandwidth(omega_N, psd):
    """Calculate half-power bandwidth for PSD curve"""
    max_psd = np.max(psd)
    half_power = max_psd / 2
    
    # Find indices where PSD crosses half-power level
    above_half = psd >= half_power
    if np.any(above_half):
        indices = np.where(above_half)[0]
        bw_start = omega_N[indices[0]]
        bw_end = omega_N[indices[-1]]
        bandwidth = bw_end - bw_start
        center = (bw_start + bw_end) / 2
        return bandwidth, center, bw_start, bw_end
    else:
        return 0, 1.0, 1.0, 1.0

def main():
    # Create figure with dual subpanel layout
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 12), dpi=100)
    
    # Adjust spacing between subpanels
    plt.subplots_adjust(wspace=0.3)
    
    # Left subpanel: Coherent fraction vs Ri
    Ri = np.linspace(0.0, 2.0, 200)
    coherent_frac = coherent_fraction_curve(Ri)
    
    # Plot main curve
    ax1.plot(Ri, coherent_frac, color='#1F78B4', linewidth=3, label='Coherent fraction')
    
    # Add variability band near marginal Ri
    marginal_region = (Ri >= 0.25) & (Ri <= 0.55)
    upper_band = coherent_frac + 0.05 * np.exp(-((Ri - 0.4)**2) / (2 * 0.1**2))
    lower_band = coherent_frac - 0.05 * np.exp(-((Ri - 0.4)**2) / (2 * 0.1**2))
    
    ax1.fill_between(Ri, lower_band, upper_band, 
                     where=marginal_region, alpha=0.2, color='#457B9D',
                     label='Increased variability')
    
    # Set axes properties
    ax1.set_xlabel(r'$R_i$', fontsize=22)
    ax1.set_ylabel('Coherent fraction', fontsize=22)
    
    # Set ticks
    ri_ticks = [0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0]
    coherent_ticks = [0, 0.25, 0.5, 0.75, 1.0]
    
    ax1.set_xticks(ri_ticks)
    ax1.set_yticks(coherent_ticks)
    ax1.set_xticklabels([f'{r:.2f}' if r < 1 else f'{r:.1f}' for r in ri_ticks], fontsize=16)
    ax1.set_yticklabels([f'{c:.2f}' for c in coherent_ticks], fontsize=16)
    
    # Add annotations
    ax1.annotate('stable: high\ncoherent fraction', xy=(1.5, 0.85), xytext=(1.2, 0.95),
                fontsize=18, ha='center', va='center',
                arrowprops=dict(arrowstyle='->', color='#374151', lw=2),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax1.annotate('marginal: additional\nloss & variability', xy=(0.4, 0.65), xytext=(0.7, 0.4),
                fontsize=18, ha='center', va='center',
                arrowprops=dict(arrowstyle='->', color='#374151', lw=2),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax1.set_xlim(0.0, 2.0)
    ax1.set_ylim(0.0, 1.0)
    ax1.grid(True, alpha=0.3)
    
    # Right subpanel: PSD broadening
    omega_N = np.linspace(0.2, 2.2, 200)
    high_ri_psd, marginal_ri_psd = psd_curves(omega_N)
    
    # Plot PSD curves
    ax2.plot(omega_N, high_ri_psd, color='#1F78B4', linewidth=3, 
             linestyle='-', label=r'High $R_i$')
    ax2.plot(omega_N, marginal_ri_psd, color='#457B9D', linewidth=3, 
             linestyle='--', label=r'Marginal $R_i$')
    
    # Calculate and show half-power bandwidths
    bw_high, center_high, start_high, end_high = calculate_half_power_bandwidth(omega_N, high_ri_psd)
    bw_marginal, center_marginal, start_marginal, end_marginal = calculate_half_power_bandwidth(omega_N, marginal_ri_psd)
    
    # Add bandwidth indicators
    y_offset_high = 0.15
    y_offset_marginal = 0.25
    
    ax2.annotate('', xy=(start_high, y_offset_high), xytext=(end_high, y_offset_high),
                arrowprops=dict(arrowstyle='<->', color='#1F78B4', lw=2))
    ax2.text(center_high, y_offset_high - 0.05, f'BW', ha='center', va='top', 
             fontsize=16, color='#1F78B4', weight='bold')
    
    ax2.annotate('', xy=(start_marginal, y_offset_marginal), xytext=(end_marginal, y_offset_marginal),
                arrowprops=dict(arrowstyle='<->', color='#457B9D', lw=2))
    ax2.text(center_marginal, y_offset_marginal - 0.05, f'BW', ha='center', va='top', 
             fontsize=16, color='#457B9D', weight='bold')
    
    # Add conversion window overlay
    conversion_band = Rectangle((0.8, 0.0), 0.4, 1.0, 
                               facecolor='#F4A261', alpha=0.2, 
                               edgecolor='none', zorder=1)
    ax2.add_patch(conversion_band)
    
    # Set axes properties
    ax2.set_xlabel(r'$\omega/N$', fontsize=22)
    ax2.set_ylabel('Normalized PSD', fontsize=22)
    
    # Set ticks
    omega_ticks = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
    psd_ticks = [0, 0.25, 0.5, 0.75, 1.0]
    
    ax2.set_xticks(omega_ticks)
    ax2.set_yticks(psd_ticks)
    ax2.set_xticklabels([f'{x:.1f}' for x in omega_ticks], fontsize=16)
    ax2.set_yticklabels([f'{p:.2f}' for p in psd_ticks], fontsize=16)
    
    # Add annotation
    ax2.annotate(r'broader PSD under marginal $R_i$', xy=(1.4, 0.7), xytext=(1.7, 0.9),
                fontsize=18, ha='center', va='center',
                arrowprops=dict(arrowstyle='->', color='#374151', lw=2),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax2.set_xlim(0.2, 2.2)
    ax2.set_ylim(0.0, 1.0)
    ax2.grid(True, alpha=0.3)
    
    # Add legends
    ax2.legend(loc='upper right', frameon=False, fontsize=18)
    
    # Add overall title
    fig.suptitle(r'Figure 3.6C — Coherence loss and spectral broadening with decreasing $R_i$', 
                fontsize=28, fontweight='bold', y=0.95)
    
    # Add caption
    caption_text = (r"Coherent fraction declines monotonically with a superposed dip near marginal $R_i$; "
                   r"spectra broaden under marginal $R_i$, indicating enhanced shear-mediated variability.")
    
    fig.text(0.5, 0.02, caption_text, fontsize=15, style='italic', 
             ha='center', va='bottom', wrap=True)
    
    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.9, bottom=0.1)
    
    # Save figure
    plt.savefig('figure_3_6c.png', dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.savefig('figure_3_6c.pdf', bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print("Figure 3.6C created successfully!")
    plt.show()

if __name__ == "__main__":
    main()