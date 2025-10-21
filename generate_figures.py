#!/usr/bin/env python3
"""
Generate scientific figures 3.8A-D for thesis
Shared house style with consistent formatting
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches
from scipy.interpolate import griddata

# Set up matplotlib for publication quality
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 16,
    'axes.linewidth': 1.2,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'xtick.major.size': 6,
    'ytick.major.size': 6,
    'xtick.minor.size': 3,
    'ytick.minor.size': 3,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'legend.frameon': False,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1
})

# Color scheme
COLORS = {
    'conversion': '#F4A261',      # Amber
    'conversion_accent': '#C06A00',
    'shear': '#2A9D8F',          # Teal
    'interfacial': '#6A4C93',    # Purple
    'classical': '#6B7280',      # Dark gray
    'grid': '#E5E7EB',           # Light gray
    'centerline': '#9CA3AF',     # Gray for centerline
    'conversion_band': '#F4A261' # Amber for band
}

def create_custom_colormap():
    """Create custom colormap from amber to teal with neutral midpoint"""
    colors = ['#F4A261', '#F5F5F5', '#2A9D8F']  # Amber, light gray, teal
    n_bins = 256
    cmap = LinearSegmentedColormap.from_list('amber_teal', colors, N=n_bins)
    return cmap

def setup_figure(figsize=(20, 14)):
    """Set up figure with consistent styling"""
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_facecolor('white')
    return fig, ax

def add_conversion_band(ax, xlim, alpha=0.2):
    """Add translucent conversion band overlay"""
    band = patches.Rectangle((0.8, ax.get_ylim()[0]), 0.4, 
                           ax.get_ylim()[1] - ax.get_ylim()[0],
                           facecolor=COLORS['conversion_band'], 
                           alpha=alpha, zorder=1)
    ax.add_patch(band)
    
    # Add centerline
    ax.axvline(x=1.0, color=COLORS['centerline'], linestyle=':', 
               linewidth=1.2, alpha=0.8, zorder=2)

def figure_3_8a():
    """Figure 3.8A - Predicted dominant pathway in (Ri, ω/N)"""
    fig, ax = setup_figure()
    
    # Create grid
    omega_n = np.linspace(0.2, 2.2, 200)
    ri = np.linspace(0.0, 2.0, 150)
    Omega, Ri = np.meshgrid(omega_n, ri)
    
    # Create synthetic dominance index D(Ri, ω/N)
    # Conversion-dominant basin near ω/N ≈ 1 for high Ri
    # Shear-dominant tongue for low Ri
    D = np.zeros_like(Omega)
    
    # Conversion dominance: stronger near ω/N = 1 and higher Ri
    conversion_strength = np.exp(-((Omega - 1.0)**2) / 0.1) * (Ri / 2.0)**2
    conversion_strength = np.clip(conversion_strength, 0, 1)
    
    # Shear dominance: stronger for low Ri, especially around conversion band
    shear_strength = np.exp(-((Omega - 1.0)**2) / 0.2) * np.exp(-Ri / 0.3)
    shear_strength = np.clip(shear_strength, 0, 1)
    
    # Combine: D = 0 (conversion) to D = 1 (shear)
    D = shear_strength / (conversion_strength + shear_strength + 1e-10)
    
    # Create custom colormap
    cmap = create_custom_colormap()
    
    # Plot heatmap
    im = ax.contourf(Omega, Ri, D, levels=50, cmap=cmap, vmin=0, vmax=1)
    
    # Add activity contours
    # Conversion activity (solid amber contours)
    conversion_activity = conversion_strength
    ax.contour(Omega, Ri, conversion_activity, levels=[0.3, 0.6], 
               colors=[COLORS['conversion']], linewidths=2.5, linestyles='solid')
    
    # Shear activity (dashed teal contours)
    shear_activity = shear_strength
    ax.contour(Omega, Ri, shear_activity, levels=[0.3, 0.6], 
               colors=[COLORS['shear']], linewidths=2.5, linestyles='dashed')
    
    # Add conversion band overlay
    add_conversion_band(ax, (0.2, 2.2))
    
    # Formatting
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(0.0, 2.0)
    ax.set_xlabel('ω/N', fontsize=22, fontweight='bold')
    ax.set_ylabel('Ri', fontsize=22, fontweight='bold')
    ax.set_title('Predicted dominant pathway in (Ri, ω/N)', fontsize=28, fontweight='bold', pad=20)
    
    # Set ticks
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.set_yticks([0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
    
    # Add grid
    ax.grid(True, color=COLORS['grid'], linewidth=0.8, alpha=0.7)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=20)
    cbar.set_label('Dominant pathway index D (0 = conversion, 1 = shear)', 
                   fontsize=18, fontweight='bold')
    cbar.ax.tick_params(labelsize=16)
    
    # Add micro-labels
    ax.text(1.0, 1.5, 'conversion basin', fontsize=16, ha='center', 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    ax.text(0.6, 0.3, 'shear tongue\n(marginal Ri)', fontsize=16, ha='center',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    # Add caption
    caption = ("Figure 3.8A. Predicted dominant pathway map for continuous stratification. "
               "Conversion dominates near ω/N ≈ 1 at higher Ri; shear dominates under "
               "marginal Ri, especially around the conversion band.")
    ax.text(0.5, -0.15, caption, transform=ax.transAxes, ha='center', 
            fontsize=15, style='italic', wrap=True)
    
    plt.tight_layout()
    return fig

def figure_3_8b():
    """Figure 3.8B - Layered regime map in (CZ, kδ): predicted notch strength"""
    fig, ax = setup_figure()
    
    # Create grid
    k_delta = np.logspace(-1, np.log10(3), 200)  # 0.1 to 3 on log scale
    cz = np.linspace(0.00, 0.40, 150)
    K_delta, CZ = np.meshgrid(k_delta, cz)
    
    # Create synthetic notch strength S(CZ, kδ)
    # Increases with CZ, decreases with kδ
    S = CZ**2 * np.exp(-K_delta / 2.0)
    S = S / np.max(S)  # Normalize to [0,1]
    
    # Plot heatmap
    im = ax.contourf(K_delta, CZ, S, levels=50, cmap='viridis', vmin=0, vmax=1)
    
    # Add isolines
    levels = [0.2, 0.5, 0.8]
    labels = ['weak', 'moderate', 'strong']
    contours = ax.contour(K_delta, CZ, S, levels=levels, colors='white', 
                         linewidths=2, linestyles='dashed')
    
    # Add isoline labels manually at fixed positions
    ax.text(0.3, 0.15, 'weak', fontsize=14, ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    ax.text(0.8, 0.25, 'moderate', fontsize=14, ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    ax.text(1.5, 0.35, 'strong', fontsize=14, ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    # Formatting
    ax.set_xlim(0.1, 3.0)
    ax.set_ylim(0.00, 0.40)
    ax.set_xlabel('kδ', fontsize=22, fontweight='bold')
    ax.set_ylabel('CZ = |Z₂ - Z₁|/(Z₂ + Z₁)', fontsize=22, fontweight='bold')
    ax.set_title('Layered regime map: predicted notch strength', fontsize=28, fontweight='bold', pad=20)
    
    # Set ticks
    ax.set_xscale('log')
    ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 3])
    ax.set_yticks([0.00, 0.10, 0.20, 0.30, 0.40])
    
    # Add grid
    ax.grid(True, color=COLORS['grid'], linewidth=0.8, alpha=0.7)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=20)
    cbar.set_label('Predicted notch strength (arb.)', fontsize=18, fontweight='bold')
    cbar.ax.tick_params(labelsize=16)
    
    # Add caption
    caption = ("Figure 3.8B. Notch strength increases with impedance contrast CZ "
               "and decreases with interface thickness kδ; sharp, high-contrast layers "
               "produce strong comb-like reverberation.")
    ax.text(0.5, -0.15, caption, transform=ax.transAxes, ha='center', 
            fontsize=15, style='italic', wrap=True)
    
    plt.tight_layout()
    return fig

def figure_3_8c():
    """Figure 3.8C - Apparent attenuation vs ω/N at selected Ri"""
    fig, ax = setup_figure()
    
    # Create frequency axis
    omega_n = np.linspace(0.2, 2.2, 1000)
    
    # Define Ri values and their characteristics
    ri_values = [1.5, 1.0, 0.6, 0.3]
    colors = ['#1f77b4', '#2e8b57', COLORS['shear'], '#B3007D']  # Deep blue, steel blue, teal, magenta
    styles = ['solid', 'solid', 'solid', 'dashed']
    
    # Generate synthetic attenuation curves
    for i, (ri, color, style) in enumerate(zip(ri_values, colors, styles)):
        # Base conversion peak at ω/N = 1
        peak_center = 1.0
        peak_width = 0.1 + (1.5 - ri) * 0.15  # Wider for lower Ri
        peak_height = 70 - (1.5 - ri) * 10    # Lower for lower Ri
        
        # Conversion peak
        conversion_peak = peak_height * np.exp(-((omega_n - peak_center)**2) / (2 * peak_width**2))
        
        # Broadband skirts (stronger for lower Ri)
        skirt_strength = (1.5 - ri) * 15
        skirts = skirt_strength * (np.exp(-((omega_n - 0.8)**2) / 0.1) + 
                                  np.exp(-((omega_n - 1.3)**2) / 0.2))
        
        # Total attenuation
        attenuation = conversion_peak + skirts + 20  # Base level
        
        # Plot curve
        ax.plot(omega_n, attenuation, color=color, linewidth=3, 
                linestyle=style, label=f'Ri = {ri}')
    
    # Add conversion band overlay
    add_conversion_band(ax, (0.2, 2.2))
    
    # Add annotations
    ax.annotate('peak widens as Ri↓', xy=(1.0, 60), xytext=(1.3, 65),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                fontsize=16, ha='center')
    ax.annotate('skirts grow\n(broadband loss)', xy=(0.8, 45), xytext=(0.5, 50),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                fontsize=16, ha='center')
    
    # Formatting
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(20, 80)
    ax.set_xlabel('ω/N', fontsize=22, fontweight='bold')
    ax.set_ylabel('Apparent attenuation (dB)', fontsize=22, fontweight='bold')
    ax.set_title('Apparent attenuation vs ω/N at selected Ri', fontsize=28, fontweight='bold', pad=20)
    
    # Set ticks
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.set_yticks(range(20, 81, 10))
    
    # Add grid
    ax.grid(True, color=COLORS['grid'], linewidth=0.8, alpha=0.7)
    
    # Add legend
    ax.legend(loc='upper right', fontsize=18, frameon=False)
    
    # Add caption
    caption = ("Figure 3.8C. Apparent attenuation vs ω/N for selected Ri. "
               "Decreasing Ri broadens the conversion peak and raises broadband skirts.")
    ax.text(0.5, -0.15, caption, transform=ax.transAxes, ha='center', 
            fontsize=15, style='italic', wrap=True)
    
    plt.tight_layout()
    return fig

def figure_3_8d():
    """Figure 3.8D - Notch depth vs kδ for several impedance contrasts"""
    fig, ax = setup_figure()
    
    # Create kδ axis (log scale)
    k_delta = np.logspace(-1, np.log10(3), 200)  # 0.1 to 3
    
    # Define CZ values and colors
    cz_values = [0.05, 0.10, 0.20, 0.30]
    colors = ['#DDA0DD', COLORS['interfacial'], '#4B0082', '#2F1B69']  # Light purple to dark purple
    
    # Generate synthetic notch depth curves
    for cz, color in zip(cz_values, colors):
        # Notch depth decreases with kδ, increases with CZ
        # Base depth at kδ = 0.1
        base_depth = 4 + cz * 50  # 4-19 dB range
        decay_rate = 0.8 + cz * 0.5  # Faster decay for higher CZ
        
        depth = base_depth * np.exp(-decay_rate * (k_delta - 0.1))
        depth = np.clip(depth, 0, 20)  # Clamp to 0-20 dB range
        
        ax.plot(k_delta, depth, color=color, linewidth=3, 
                label=f'CZ = {cz:.2f}')
    
    # Add regime labels
    ax.text(0.1, 2, 'thin', fontsize=14, ha='center', va='bottom')
    ax.text(1.0, 2, 'resonant', fontsize=14, ha='center', va='bottom')
    ax.text(3.0, 2, 'thick', fontsize=14, ha='center', va='bottom')
    
    # Add brace
    brace = mpatches.FancyBboxPatch((0.1, 1), 2.9, 0.5, 
                                   boxstyle="round,pad=0.02", 
                                   facecolor='none', edgecolor='black', 
                                   linewidth=1)
    ax.add_patch(brace)
    
    # Formatting
    ax.set_xlim(0.1, 3.0)
    ax.set_ylim(0, 20)
    ax.set_xlabel('kδ', fontsize=22, fontweight='bold')
    ax.set_ylabel('Notch depth (dB)', fontsize=22, fontweight='bold')
    ax.set_title('Notch depth vs kδ for several impedance contrasts', fontsize=28, fontweight='bold', pad=20)
    
    # Set ticks
    ax.set_xscale('log')
    ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 3])
    ax.set_yticks(range(0, 21, 5))
    
    # Add grid
    ax.grid(True, color=COLORS['grid'], linewidth=0.8, alpha=0.7)
    
    # Add legend
    ax.legend(loc='upper right', fontsize=18, frameon=False)
    
    # Add caption
    caption = ("Figure 3.8D. Notch depth decreases as interface thickness kδ "
               "increases and increases with impedance contrast CZ.")
    ax.text(0.5, -0.15, caption, transform=ax.transAxes, ha='center', 
            fontsize=15, style='italic', wrap=True)
    
    plt.tight_layout()
    return fig

def main():
    """Generate all figures"""
    print("Generating Figure 3.8A...")
    fig_a = figure_3_8a()
    fig_a.savefig('figure_3_8a.pdf', format='pdf', dpi=300, bbox_inches='tight')
    fig_a.savefig('figure_3_8a.png', format='png', dpi=300, bbox_inches='tight')
    fig_a.savefig('figure_3_8a.svg', format='svg', bbox_inches='tight')
    plt.close(fig_a)
    
    print("Generating Figure 3.8B...")
    fig_b = figure_3_8b()
    fig_b.savefig('figure_3_8b.pdf', format='pdf', dpi=300, bbox_inches='tight')
    fig_b.savefig('figure_3_8b.png', format='png', dpi=300, bbox_inches='tight')
    fig_b.savefig('figure_3_8b.svg', format='svg', bbox_inches='tight')
    plt.close(fig_b)
    
    print("Generating Figure 3.8C...")
    fig_c = figure_3_8c()
    fig_c.savefig('figure_3_8c.pdf', format='pdf', dpi=300, bbox_inches='tight')
    fig_c.savefig('figure_3_8c.png', format='png', dpi=300, bbox_inches='tight')
    fig_c.savefig('figure_3_8c.svg', format='svg', bbox_inches='tight')
    plt.close(fig_c)
    
    print("Generating Figure 3.8D...")
    fig_d = figure_3_8d()
    fig_d.savefig('figure_3_8d.pdf', format='pdf', dpi=300, bbox_inches='tight')
    fig_d.savefig('figure_3_8d.png', format='png', dpi=300, bbox_inches='tight')
    fig_d.savefig('figure_3_8d.svg', format='svg', bbox_inches='tight')
    plt.close(fig_d)
    
    print("All figures generated successfully!")
    print("Files created:")
    print("- figure_3_8a.pdf/png/svg")
    print("- figure_3_8b.pdf/png/svg") 
    print("- figure_3_8c.pdf/png/svg")
    print("- figure_3_8d.pdf/png/svg")

if __name__ == "__main__":
    main()