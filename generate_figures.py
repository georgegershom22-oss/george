#!/usr/bin/env python3
"""
Generate scientific figures 3.8A-D for thesis
Following precise style guidelines for publication-quality output
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

# ============================================================================
# GLOBAL STYLE SETUP
# ============================================================================

# Set up matplotlib to use Helvetica/Arial
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
rcParams['font.size'] = 16
rcParams['axes.linewidth'] = 1.0
rcParams['grid.linewidth'] = 0.8
rcParams['lines.linewidth'] = 3.0
rcParams['patch.linewidth'] = 0.8

# Canvas size in inches (2000×1400 px at 100 dpi)
DPI = 100
FIGSIZE = (2000/DPI, 1400/DPI)

# Colors from specification
COLORS = {
    'viscous_thermal': '#6B7280',  # dark gray
    'conversion': '#F4A261',        # amber
    'conversion_accent': '#C06A00', # darker amber
    'scattering': '#6A4C93',        # purple
    'shear': '#2A9D8F',             # teal
    'grid': '#E5E7EB',              # light gray
    'centerline': '#9CA3AF',        # gray for dotted line
}

# Common frequency axis setup
OMEGA_N_TICKS = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
OMEGA_N_RANGE = [0.2, 2.2]
CONVERSION_BAND = [0.8, 1.2]


def setup_common_axes(ax, xlabel=r'$\omega/N$', ylabel='', xlim=OMEGA_N_RANGE):
    """Apply common styling to axes"""
    ax.set_xlabel(xlabel, fontsize=22, fontweight='normal')
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=22, fontweight='normal')
    ax.tick_params(labelsize=16, width=1.0, length=6)
    ax.grid(True, color=COLORS['grid'], linewidth=0.8, alpha=1.0)
    if xlim == OMEGA_N_RANGE:
        ax.set_xticks(OMEGA_N_TICKS)
    ax.set_xlim(xlim)
    ax.spines['top'].set_visible(True)
    ax.spines['right'].set_visible(True)
    for spine in ax.spines.values():
        spine.set_linewidth(1.0)


def add_conversion_band(ax, ylim):
    """Add amber conversion band overlay (0.8 ≤ ω/N ≤ 1.2)"""
    rect = Rectangle((CONVERSION_BAND[0], ylim[0]), 
                     CONVERSION_BAND[1] - CONVERSION_BAND[0],
                     ylim[1] - ylim[0],
                     facecolor=COLORS['conversion'], alpha=0.2, 
                     edgecolor='none', zorder=0)
    ax.add_patch(rect)
    
    # Dotted centerline at ω/N = 1
    ax.axvline(1.0, color=COLORS['centerline'], linestyle=':', 
              linewidth=1.2, zorder=1)


# ============================================================================
# FIGURE 3.8A - Dominant Pathway Map
# ============================================================================

def generate_figure_3_8A():
    """
    Figure 3.8A — Predicted dominant pathway in (Ri, ω/N) 
    for continuous stratification
    """
    print("Generating Figure 3.8A...")
    
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI, facecolor='white')
    
    # Create coordinate grids
    omega_n = np.linspace(0.2, 2.2, 400)
    ri = np.linspace(0.0, 2.0, 300)
    OMEGA_N, RI = np.meshgrid(omega_n, ri)
    
    # Dominance index: 0 = conversion, 1 = shear
    # Conversion-dominant basin near ω/N ≈ 1 for moderate/high Ri (≳0.7)
    # Shear-dominant tongue for low Ri (≲0.6), widest around conversion band
    
    # Create a schematic dominance field
    # Peak conversion activity at ω/N=1, Ri~1.0-1.5
    conversion_activity = np.exp(-((OMEGA_N - 1.0)**2 / 0.15)) * (1 / (1 + np.exp(-5*(RI - 0.7))))
    
    # Shear activity peaks at low Ri, around ω/N~0.8-1.2
    shear_activity = np.exp(-((OMEGA_N - 1.0)**2 / 0.25)) * np.exp(-((RI - 0.3)**2 / 0.15))
    # Add broadening at low Ri for higher ω/N
    shear_activity += 0.5 * np.exp(-((OMEGA_N - 1.5)**2 / 0.4)) * np.exp(-((RI - 0.4)**2 / 0.2))
    
    # Normalize and create dominance index
    total_activity = conversion_activity + shear_activity + 0.01
    D = shear_activity / total_activity  # 0=conversion, 1=shear
    
    # Create custom colormap: amber (0) -> light gray (0.5) -> teal (1)
    colors = [COLORS['conversion'], '#F5F5F5', COLORS['shear']]
    n_bins = 256
    cmap = LinearSegmentedColormap.from_list('conversion_shear', colors, N=n_bins)
    
    # Plot heatmap
    im = ax.pcolormesh(OMEGA_N, RI, D, cmap=cmap, shading='auto', 
                       vmin=0, vmax=1, rasterized=True)
    
    # Add conversion activity contours (solid amber)
    contour_levels_conv = [0.6, 0.8]
    cs1 = ax.contour(OMEGA_N, RI, conversion_activity / conversion_activity.max(),
                     levels=contour_levels_conv, colors=COLORS['conversion_accent'],
                     linewidths=2.5, linestyles='solid')
    
    # Add shear activity contours (dashed teal)
    contour_levels_shear = [0.5, 0.75]
    cs2 = ax.contour(OMEGA_N, RI, shear_activity / shear_activity.max(),
                     levels=contour_levels_shear, colors=COLORS['shear'],
                     linewidths=2.5, linestyles='dashed')
    
    # Overlay conversion band
    add_conversion_band(ax, [0.0, 2.0])
    
    # Axes setup
    setup_common_axes(ax, xlabel=r'$\omega/N$', ylabel=r'$Ri$')
    ax.set_ylim([0.0, 2.0])
    ax.set_yticks([0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Dominant pathway index $D$ (0 = conversion, 1 = shear)', 
                   fontsize=18, labelpad=10)
    cbar.ax.tick_params(labelsize=16)
    
    # Micro-labels
    ax.text(1.0, 1.3, 'conversion\nbasin', fontsize=18, ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                     edgecolor='none', alpha=0.8))
    ax.text(1.0, 0.3, 'shear tongue\n(marginal $Ri$)', fontsize=18, 
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                     edgecolor='none', alpha=0.8))
    
    # Title
    ax.set_title('Figure 3.8A — Dominant Pathway Map', fontsize=28, 
                fontweight='bold', pad=20)
    
    # Caption inside canvas
    caption = (r"Figure 3.8A. Predicted dominant pathway map for continuous stratification. "
               r"Conversion dominates near $\omega/N\!\approx\!1$ at higher $Ri$; "
               r"shear dominates under marginal $Ri$, especially around the conversion band.")
    fig.text(0.5, 0.02, caption, fontsize=15, ha='center', style='italic', 
            wrap=True)
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig('/workspace/figure_3_8A.png', dpi=300, bbox_inches='tight', 
                facecolor='white')
    plt.savefig('/workspace/figure_3_8A.pdf', bbox_inches='tight', 
                facecolor='white')
    print("✓ Figure 3.8A saved (PNG and PDF)")
    plt.close()


# ============================================================================
# FIGURE 3.8B - Layered Regime Map
# ============================================================================

def generate_figure_3_8B():
    """
    Figure 3.8B — Layered regime map in (Cz, kδ): 
    predicted notch strength
    """
    print("Generating Figure 3.8B...")
    
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI, facecolor='white')
    
    # Create coordinate grids (log scale for kδ)
    kdelta = np.logspace(np.log10(0.1), np.log10(3), 300)
    cz = np.linspace(0.0, 0.4, 250)
    KDELTA, CZ = np.meshgrid(kdelta, cz)
    
    # Notch strength: increases with Cz, decreases with kδ
    # S ∈ [0, 1]
    S = (CZ / 0.4) * np.exp(-KDELTA / 0.8)
    
    # Plot heatmap
    im = ax.pcolormesh(KDELTA, CZ, S, cmap='YlOrRd', shading='auto',
                       vmin=0, vmax=1, rasterized=True)
    
    # Add isolines
    levels = [0.2, 0.5, 0.75]
    labels = ['weak', 'moderate', 'strong']
    cs = ax.contour(KDELTA, CZ, S, levels=levels, colors='black',
                    linewidths=2.0, linestyles='dashed')
    ax.clabel(cs, inline=True, fontsize=18, fmt=lambda x: labels[levels.index(x)])
    
    # Axes setup (log scale for x)
    ax.set_xscale('log')
    ax.set_xlabel(r'$k\delta$', fontsize=22)
    ax.set_ylabel(r'$C_Z = \frac{|Z_2 - Z_1|}{Z_2 + Z_1}$', fontsize=22)
    ax.set_xlim([0.1, 3])
    ax.set_ylim([0.0, 0.4])
    ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 3])
    ax.set_xticklabels(['0.1', '0.2', '0.5', '1', '2', '3'])
    ax.set_yticks([0.0, 0.1, 0.2, 0.3, 0.4])
    ax.tick_params(labelsize=16, width=1.0, length=6)
    ax.grid(True, color=COLORS['grid'], linewidth=0.8, alpha=1.0, which='major')
    
    for spine in ax.spines.values():
        spine.set_linewidth(1.0)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Predicted notch strength (arb.)', fontsize=18, labelpad=10)
    cbar.ax.tick_params(labelsize=16)
    
    # Add bottom brace annotation
    ax.annotate('', xy=(0.1, -0.055), xytext=(0.3, -0.055),
                xycoords=('data', 'axes fraction'),
                arrowprops=dict(arrowstyle='<->', lw=1.5, color='black'))
    ax.text(0.2, -0.08, 'thin', fontsize=16, ha='center', 
           transform=ax.get_xaxis_transform())
    
    ax.annotate('', xy=(0.7, -0.055), xytext=(1.5, -0.055),
                xycoords=('data', 'axes fraction'),
                arrowprops=dict(arrowstyle='<->', lw=1.5, color='black'))
    ax.text(1.05, -0.08, 'resonant', fontsize=16, ha='center',
           transform=ax.get_xaxis_transform())
    
    ax.annotate('', xy=(2.0, -0.055), xytext=(3.0, -0.055),
                xycoords=('data', 'axes fraction'),
                arrowprops=dict(arrowstyle='<->', lw=1.5, color='black'))
    ax.text(2.5, -0.08, 'thick', fontsize=16, ha='center',
           transform=ax.get_xaxis_transform())
    
    # Title
    ax.set_title('Figure 3.8B — Notch Strength Regime Map', fontsize=28,
                fontweight='bold', pad=20)
    
    # Caption
    caption = (r"Figure 3.8B. Notch strength increases with impedance contrast $C_Z$ "
               r"and decreases with interface thickness $k\delta$; sharp, high-contrast "
               r"layers produce strong comb-like reverberation.")
    fig.text(0.5, 0.02, caption, fontsize=15, ha='center', style='italic',
            wrap=True)
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig('/workspace/figure_3_8B.png', dpi=300, bbox_inches='tight',
                facecolor='white')
    plt.savefig('/workspace/figure_3_8B.pdf', bbox_inches='tight',
                facecolor='white')
    print("✓ Figure 3.8B saved (PNG and PDF)")
    plt.close()


# ============================================================================
# FIGURE 3.8C - Attenuation vs ω/N
# ============================================================================

def generate_figure_3_8C():
    """
    Figure 3.8C — Qualitative scaling of apparent attenuation 
    vs ω/N at selected Ri
    """
    print("Generating Figure 3.8C...")
    
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI, facecolor='white')
    
    omega_n = np.linspace(0.2, 2.2, 500)
    
    # Define curves for different Ri values
    # As Ri decreases: peak becomes broader and lower, skirts grow
    
    def attenuation_curve(omega_n, ri, peak_pos=1.0):
        """Generate attenuation curve with peak at conversion frequency"""
        # Base peak (Gaussian)
        width = 0.1 + 0.3 * (1.5 - ri)  # Wider for lower Ri
        height = 60 + 15 * ri  # Higher peak for higher Ri
        peak = height * np.exp(-((omega_n - peak_pos)**2) / (2 * width**2))
        
        # Broadband skirts (increase as Ri decreases)
        skirt_level = 25 + 15 * (1.5 - ri)
        skirts = skirt_level * (1 - np.exp(-((omega_n - peak_pos)**2) / 2.0))
        
        return peak + skirts + 20  # Base level
    
    ri_values = [1.5, 1.0, 0.6, 0.3]
    colors_ri = ['#003f5c', '#58508d', COLORS['shear'], '#bc5090']
    linestyles = ['solid', 'solid', 'solid', 'dashed']
    linewidths = [3, 3, 3, 3]
    
    for ri, color, ls, lw in zip(ri_values, colors_ri, linestyles, linewidths):
        TL = attenuation_curve(omega_n, ri)
        label = f'$Ri = {ri}$'
        ax.plot(omega_n, TL, color=color, linestyle=ls, linewidth=lw, 
               label=label, solid_capstyle='round')
    
    # Overlay conversion band
    add_conversion_band(ax, [20, 80])
    
    # Axes setup
    setup_common_axes(ax, xlabel=r'$\omega/N$', ylabel='Transmission Loss (dB)')
    ax.set_ylim([20, 80])
    ax.set_yticks(np.arange(20, 81, 10))
    
    # Annotations
    ax.annotate('peak widens as $Ri\\downarrow$', xy=(1.0, 75), 
               xytext=(1.5, 72), fontsize=18,
               arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))
    
    ax.annotate('skirts grow\n(broadband loss)', xy=(1.7, 50),
               xytext=(1.9, 58), fontsize=18, ha='center',
               arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))
    
    # Legend
    ax.legend(loc='lower right', fontsize=18, frameon=False)
    
    # Title
    ax.set_title('Figure 3.8C — Attenuation vs Frequency', fontsize=28,
                fontweight='bold', pad=20)
    
    # Caption
    caption = (r"Figure 3.8C. Apparent attenuation vs $\omega/N$ for selected $Ri$. "
               r"Decreasing $Ri$ broadens the conversion peak and raises broadband skirts.")
    fig.text(0.5, 0.02, caption, fontsize=15, ha='center', style='italic')
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig('/workspace/figure_3_8C.png', dpi=300, bbox_inches='tight',
                facecolor='white')
    plt.savefig('/workspace/figure_3_8C.pdf', bbox_inches='tight',
                facecolor='white')
    print("✓ Figure 3.8C saved (PNG and PDF)")
    plt.close()


# ============================================================================
# FIGURE 3.8D - Notch Depth vs kδ
# ============================================================================

def generate_figure_3_8D():
    """
    Figure 3.8D — Notch depth vs kδ for several impedance contrasts Cz
    """
    print("Generating Figure 3.8D...")
    
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI, facecolor='white')
    
    kdelta = np.logspace(np.log10(0.1), np.log10(3), 200)
    
    # Notch depth curves for different Cz values
    # Depth decays with increasing kδ, grows with Cz
    
    def notch_depth(kdelta, cz):
        """Notch depth decreases with kδ, increases with Cz"""
        # Exponential decay with kδ, scaled by Cz
        base_depth = 50 * cz  # Max depth scales with Cz
        decay = np.exp(-kdelta / 0.6)  # Decay rate
        return base_depth * decay
    
    cz_values = [0.05, 0.10, 0.20, 0.30]
    colors_cz = ['#B8A8C8', COLORS['scattering'], '#4A3563', '#2A1A3D']
    
    for cz, color in zip(cz_values, colors_cz):
        depth = notch_depth(kdelta, cz)
        label = f'$C_Z = {cz:.2f}$'
        ax.plot(kdelta, depth, color=color, linewidth=3, 
               label=label, solid_capstyle='round')
    
    # Axes setup (log scale for x)
    ax.set_xscale('log')
    ax.set_xlabel(r'$k\delta$', fontsize=22)
    ax.set_ylabel('Notch depth (dB)', fontsize=22)
    ax.set_xlim([0.1, 3])
    ax.set_ylim([0, 20])
    ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 3])
    ax.set_xticklabels(['0.1', '0.2', '0.5', '1', '2', '3'])
    ax.set_yticks(np.arange(0, 21, 5))
    ax.tick_params(labelsize=16, width=1.0, length=6)
    ax.grid(True, color=COLORS['grid'], linewidth=0.8, alpha=1.0, which='major')
    
    for spine in ax.spines.values():
        spine.set_linewidth(1.0)
    
    # Add bottom brace annotation
    brace_y = -0.08
    ax.annotate('', xy=(0.1, brace_y), xytext=(0.3, brace_y),
                xycoords=('data', 'axes fraction'),
                arrowprops=dict(arrowstyle='<->', lw=1.5, color='black'))
    ax.text(0.2, brace_y - 0.04, 'thin', fontsize=16, ha='center',
           transform=ax.get_xaxis_transform())
    
    ax.annotate('', xy=(0.7, brace_y), xytext=(1.5, brace_y),
                xycoords=('data', 'axes fraction'),
                arrowprops=dict(arrowstyle='<->', lw=1.5, color='black'))
    ax.text(1.05, brace_y - 0.04, 'resonant', fontsize=16, ha='center',
           transform=ax.get_xaxis_transform())
    
    ax.annotate('', xy=(2.0, brace_y), xytext=(3.0, brace_y),
                xycoords=('data', 'axes fraction'),
                arrowprops=dict(arrowstyle='<->', lw=1.5, color='black'))
    ax.text(2.5, brace_y - 0.04, 'thick', fontsize=16, ha='center',
           transform=ax.get_xaxis_transform())
    
    # Legend
    ax.legend(loc='upper right', fontsize=18, frameon=False)
    
    # Title
    ax.set_title('Figure 3.8D — Notch Depth vs Interface Thickness', 
                fontsize=28, fontweight='bold', pad=20)
    
    # Caption
    caption = (r"Figure 3.8D. Notch depth decreases as interface thickness $k\delta$ "
               r"increases and increases with impedance contrast $C_Z$.")
    fig.text(0.5, 0.02, caption, fontsize=15, ha='center', style='italic')
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig('/workspace/figure_3_8D.png', dpi=300, bbox_inches='tight',
                facecolor='white')
    plt.savefig('/workspace/figure_3_8D.pdf', bbox_inches='tight',
                facecolor='white')
    print("✓ Figure 3.8D saved (PNG and PDF)")
    plt.close()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Generating Scientific Figures 3.8A-D")
    print("=" * 70)
    print()
    
    generate_figure_3_8A()
    generate_figure_3_8B()
    generate_figure_3_8C()
    generate_figure_3_8D()
    
    print()
    print("=" * 70)
    print("All figures generated successfully!")
    print("Output files:")
    print("  - figure_3_8A.png / .pdf")
    print("  - figure_3_8B.png / .pdf")
    print("  - figure_3_8C.png / .pdf")
    print("  - figure_3_8D.png / .pdf")
    print("=" * 70)
