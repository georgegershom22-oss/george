"""
Figure 3.6C — Coherent fraction vs Ri and PSD broadening under marginal Ri
Left: Coherent fraction decreasing with Ri
Right: Power spectral density comparison between high and marginal Ri
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

def generate_coherent_fraction(Ri):
    """
    Generate coherent fraction data:
    - Monotone decreasing from ~0.95 at Ri=2 to ~0.5 at Ri≈0.25
    - Localized deeper notch (to ~0.4) centered Ri≈0.3−0.5
    """
    # Base monotone decreasing curve
    base = 0.95 - 0.45 * (1 - np.exp(-2 * (2.0 - Ri)))
    
    # Add localized dip around Ri = 0.3-0.5
    dip_center = 0.4
    dip_width = 0.15
    dip_depth = 0.15
    dip = dip_depth * np.exp(-((Ri - dip_center) / dip_width)**2)
    
    coherent = base - dip
    
    # Ensure smooth transitions
    from scipy.ndimage import gaussian_filter1d
    coherent = gaussian_filter1d(coherent, sigma=2)
    
    # Add small variability in the dip region
    variability = np.zeros_like(coherent)
    dip_mask = (Ri >= 0.3) & (Ri <= 0.5)
    variability[dip_mask] = 0.02
    
    return np.clip(coherent, 0.35, 0.95), variability

def generate_psd_data(omega_N):
    """
    Generate PSD data for high Ri and marginal Ri cases
    """
    # High Ri: narrow peak near ω/N≈1
    center_high = 1.0
    width_high = 0.15
    psd_high = np.exp(-((omega_N - center_high) / width_high)**2)
    
    # Marginal Ri: broader peak/plateau
    center_marginal = 1.0
    width_marginal = 0.35  # Much broader
    psd_marginal = np.exp(-((omega_N - center_marginal) / width_marginal)**2)
    
    # Add slight plateau effect for marginal
    plateau_mask = (omega_N >= 0.8) & (omega_N <= 1.2)
    psd_marginal[plateau_mask] = np.maximum(psd_marginal[plateau_mask], 0.7)
    
    # Normalize
    psd_high /= np.max(psd_high)
    psd_marginal /= np.max(psd_marginal)
    
    # Smooth
    from scipy.ndimage import gaussian_filter1d
    psd_high = gaussian_filter1d(psd_high, sigma=1)
    psd_marginal = gaussian_filter1d(psd_marginal, sigma=1)
    
    return psd_high, psd_marginal

def create_figure_3_6c():
    # Set up figure with two subpanels
    fig = plt.figure(figsize=(18, 12), facecolor='white')
    
    # Create subplots
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    
    # LEFT PANEL: Coherent fraction vs Ri
    Ri = np.linspace(0.0, 2.0, 300)
    coherent, variability = generate_coherent_fraction(Ri)
    
    # Plot main curve
    ax1.plot(Ri, coherent, color='#1F78B4', linewidth=3, label='Coherent fraction')
    
    # Add shaded region for variability around dip
    dip_mask = (Ri >= 0.3) & (Ri <= 0.5)
    ax1.fill_between(Ri[dip_mask], 
                     coherent[dip_mask] - variability[dip_mask]*2,
                     coherent[dip_mask] + variability[dip_mask]*2,
                     color='#457B9D', alpha=0.2)
    
    # Configure left panel
    ax1.set_xlim(0.0, 2.0)
    ax1.set_ylim(0, 1)
    ax1.set_xlabel('Ri', fontsize=22)
    ax1.set_ylabel('Coherent fraction', fontsize=22)
    ax1.set_xticks([0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
    ax1.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax1.tick_params(axis='both', which='major', labelsize=16)
    ax1.grid(True, color='#E5E7EB', linewidth=0.8, alpha=0.8)
    ax1.set_axisbelow(True)
    
    # Add micro-notes to left panel
    ax1.annotate('stable: high\ncoherent fraction', 
                xy=(1.5, 0.85), xytext=(1.7, 0.75),
                fontsize=16, ha='center', style='italic',
                arrowprops=dict(arrowstyle='->', color='#666666', lw=1))
    
    ax1.annotate('marginal: extra loss\n& variability', 
                xy=(0.4, 0.45), xytext=(0.8, 0.25),
                fontsize=16, ha='center', style='italic',
                arrowprops=dict(arrowstyle='->', color='#666666', lw=1))
    
    # RIGHT PANEL: PSD broadening
    omega_N = np.linspace(0.2, 2.2, 300)
    psd_high, psd_marginal = generate_psd_data(omega_N)
    
    # Plot PSDs
    line_high, = ax2.plot(omega_N, psd_high, color='#1F78B4', 
                         linewidth=3, linestyle='-', label='High Ri')
    line_marginal, = ax2.plot(omega_N, psd_marginal, color='#457B9D', 
                             linewidth=3, linestyle='--', label='Marginal Ri')
    
    # Add amber band overlay
    band = Rectangle((0.8, 0), 0.4, 1.0,
                    facecolor='#F4A261', alpha=0.2,
                    edgecolor='none', zorder=1)
    ax2.add_patch(band)
    
    # Add dotted line at ω/N = 1.0
    ax2.axvline(x=1.0, color='#9CA3AF', linestyle=':', linewidth=1, zorder=2)
    
    # Add bandwidth arrows
    # Find half-power points for both curves
    half_power = 0.5
    
    # High Ri bandwidth
    idx_high = np.where(psd_high >= half_power)[0]
    if len(idx_high) > 0:
        bw_high_left = omega_N[idx_high[0]]
        bw_high_right = omega_N[idx_high[-1]]
        ax2.annotate('', xy=(bw_high_left, 0.45), xytext=(bw_high_right, 0.45),
                    arrowprops=dict(arrowstyle='<->', color='#1F78B4', lw=2))
        ax2.text((bw_high_left + bw_high_right)/2, 0.42, 'BW', 
                fontsize=14, ha='center', color='#1F78B4')
    
    # Marginal Ri bandwidth
    idx_marginal = np.where(psd_marginal >= half_power)[0]
    if len(idx_marginal) > 0:
        bw_marginal_left = omega_N[idx_marginal[0]]
        bw_marginal_right = omega_N[idx_marginal[-1]]
        ax2.annotate('', xy=(bw_marginal_left, 0.35), xytext=(bw_marginal_right, 0.35),
                    arrowprops=dict(arrowstyle='<->', color='#457B9D', lw=2))
        ax2.text((bw_marginal_left + bw_marginal_right)/2, 0.32, 'BW', 
                fontsize=14, ha='center', color='#457B9D')
    
    # Configure right panel
    ax2.set_xlim(0.2, 2.2)
    ax2.set_ylim(0, 1)
    ax2.set_xlabel('ω/N', fontsize=22)
    ax2.set_ylabel('Normalized PSD', fontsize=22)
    ax2.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax2.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax2.tick_params(axis='both', which='major', labelsize=16)
    ax2.grid(True, color='#E5E7EB', linewidth=0.8, alpha=0.8)
    ax2.set_axisbelow(True)
    
    # Add micro-note near dashed curve
    ax2.annotate('broader PSD under\nmarginal Ri', 
                xy=(1.3, 0.6), xytext=(1.6, 0.75),
                fontsize=16, ha='center', style='italic',
                arrowprops=dict(arrowstyle='->', color='#457B9D', lw=1))
    
    # Add legend inside right panel
    ax2.legend(loc='upper right', fontsize=16, framealpha=0.9)
    
    # Add main title
    fig.suptitle('Figure 3.6C — Coherence loss and spectral broadening with decreasing Ri',
                fontsize=28, fontweight='bold', y=0.98)
    
    # Add caption
    caption = ("Coherent fraction drops with decreasing Ri and shows a localized dip near marginal Ri; "
              "spectra broaden under marginal Ri.")
    fig.text(0.5, 0.05, caption, fontsize=18, ha='center', style='italic')
    
    # Adjust layout
    plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.15, wspace=0.3)
    
    return fig

if __name__ == "__main__":
    fig = create_figure_3_6c()
    
    # Save in multiple formats
    fig.savefig('figure_3_6c.png', dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig('figure_3_6c.pdf', bbox_inches='tight', facecolor='white')
    fig.savefig('figure_3_6c.svg', bbox_inches='tight', facecolor='white')
    
    plt.show()
    print("Figure 3.6C saved as PNG, PDF, and SVG")