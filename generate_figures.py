#!/usr/bin/env python3
"""
Generate scientific figures for thesis Chapter 3.8
Four publication-quality figures (A-D) with consistent styling
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import patches
from matplotlib.ticker import ScalarFormatter, LogFormatter, FuncFormatter
import matplotlib.font_manager as fm

# Set up matplotlib for publication quality
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['pdf.fonttype'] = 42  # TrueType fonts for PDF
plt.rcParams['ps.fonttype'] = 42   # TrueType fonts for PostScript
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['axes.labelsize'] = 22
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['ytick.labelsize'] = 16
plt.rcParams['legend.fontsize'] = 16
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300

# Common colors
COLOR_AMBER = '#F4A261'
COLOR_AMBER_ACCENT = '#C06A00'
COLOR_TEAL = '#2A9D8F'
COLOR_PURPLE = '#6A4C93'
COLOR_GRAY = '#6B7280'
COLOR_GRID = '#E5E7EB'
COLOR_DOTTED = '#9CA3AF'
COLOR_MAGENTA = '#B3007D'

# Common frequency axis settings
FREQ_RANGE = [0.2, 2.2]
FREQ_TICKS = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
CONVERSION_BAND = [0.8, 1.2]

def setup_figure():
    """Create a figure with the standard size and background"""
    fig = plt.figure(figsize=(20, 14), facecolor='white')
    return fig

def add_conversion_band(ax, alpha=0.2):
    """Add the translucent amber conversion band and centerline"""
    ax.axvspan(CONVERSION_BAND[0], CONVERSION_BAND[1], 
               color=COLOR_AMBER, alpha=alpha, zorder=1)
    ax.axvline(x=1.0, color=COLOR_DOTTED, linestyle=':', 
               linewidth=1.2, zorder=2)

def add_grid(ax):
    """Add the standard light gray grid"""
    ax.grid(True, which='major', color=COLOR_GRID, linewidth=0.8, alpha=1.0)
    ax.set_axisbelow(True)

def format_axes(ax, xlabel, ylabel, title=None):
    """Apply standard formatting to axes"""
    ax.set_xlabel(xlabel, fontsize=22, fontweight='normal')
    ax.set_ylabel(ylabel, fontsize=22, fontweight='normal')
    if title:
        ax.set_title(title, fontsize=28, fontweight='bold', pad=20)
    ax.tick_params(axis='both', which='major', labelsize=16)
    
def figure_3_8A():
    """Figure 3.8A - Predicted dominant pathway in (Ri, ω/N)"""
    print("Generating Figure 3.8A...")
    
    fig = setup_figure()
    ax = fig.add_subplot(111)
    
    # Create grid
    omega_N = np.linspace(0.2, 2.2, 200)
    Ri = np.linspace(0.0, 2.0, 150)
    X, Y = np.meshgrid(omega_N, Ri)
    
    # Create dominance index D(Ri, ω/N)
    # 0 = conversion-dominant (amber), 1 = shear-dominant (teal)
    # Conversion dominates near ω/N ≈ 1 for higher Ri
    # Shear dominates at low Ri
    
    # Create conversion strength (peaks at ω/N=1, stronger for high Ri)
    conversion_strength = np.exp(-2.0 * (X - 1.0)**2) * (1 / (1 + np.exp(-3*(Y - 0.7))))
    
    # Create shear strength (stronger for low Ri, peaks around ω/N=1 but broader)
    shear_strength = np.exp(-0.5 * (X - 1.0)**2) * (1 / (1 + np.exp(4*(Y - 0.5))))
    
    # Dominance index: 0 for conversion, 1 for shear
    D = shear_strength / (conversion_strength + shear_strength + 0.1)
    
    # Create custom colormap from amber to teal
    colors_list = [COLOR_AMBER, '#F7E3D0', '#E0E0E0', '#B8D4D0', COLOR_TEAL]
    n_bins = 100
    cmap = mcolors.LinearSegmentedColormap.from_list('amber_teal', colors_list, N=n_bins)
    
    # Plot heatmap
    im = ax.contourf(X, Y, D, levels=50, cmap=cmap, extend='neither')
    
    # Add activity contours
    # Conversion high-activity zones (solid amber)
    conv_activity = conversion_strength
    cs1 = ax.contour(X, Y, conv_activity, levels=[0.3, 0.6], 
                     colors=COLOR_AMBER_ACCENT, linewidths=2.5, linestyles='solid')
    
    # Shear high-activity zones (dashed teal)
    shear_activity = shear_strength
    cs2 = ax.contour(X, Y, shear_activity, levels=[0.4, 0.7], 
                     colors=COLOR_TEAL, linewidths=2.5, linestyles='dashed')
    
    # Add conversion band
    add_conversion_band(ax, alpha=0.15)
    
    # Add grid
    add_grid(ax)
    
    # Format axes
    ax.set_xlim(FREQ_RANGE)
    ax.set_ylim([0.0, 2.0])
    ax.set_xticks(FREQ_TICKS)
    ax.set_yticks([0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
    format_axes(ax, r'$\omega/N$', r'$Ri$', 
                'Predicted Dominant Pathway in Continuous Stratification')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, pad=0.02, aspect=30)
    cbar.set_label(r'Dominant pathway index $D$' + '\n(0 = conversion, 1 = shear)', 
                   fontsize=18)
    cbar.ax.tick_params(labelsize=14)
    
    # Add micro-labels
    ax.text(1.0, 1.3, 'conversion\nbasin', fontsize=18, ha='center', va='center',
            color=COLOR_AMBER_ACCENT, weight='normal')
    ax.text(1.5, 0.3, 'shear tongue\n(marginal $Ri$)', fontsize=18, ha='center', 
            va='center', color=COLOR_TEAL, weight='normal')
    
    # Add caption
    caption = ("Figure 3.8A. Predicted dominant pathway map for continuous stratification. "
              "Conversion dominates near $\\omega/N \\approx 1$ at higher $Ri$; "
              "shear dominates under marginal $Ri$, especially around the conversion band.")
    fig.text(0.5, 0.02, caption, fontsize=15, ha='center', style='italic')
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig('figure_3_8A.pdf', format='pdf', bbox_inches='tight')
    plt.savefig('figure_3_8A.png', format='png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Figure 3.8A saved as PDF and PNG")

def figure_3_8B():
    """Figure 3.8B - Layered regime map in (C_Z, kδ)"""
    print("Generating Figure 3.8B...")
    
    fig = setup_figure()
    ax = fig.add_subplot(111)
    
    # Create grid
    k_delta = np.logspace(-1, np.log10(3), 200)  # 0.1 to 3, log scale
    C_Z = np.linspace(0.0, 0.4, 150)
    X, Y = np.meshgrid(k_delta, C_Z)
    
    # Notch strength S: increases with C_Z, decreases with kδ
    # S = C_Z^1.5 / (1 + kδ^2)
    S = (Y**1.5) / (1 + X**2)
    S = S / S.max()  # Normalize to [0, 1]
    
    # Create colormap (light to dark)
    cmap = plt.colormaps['viridis']
    
    # Plot heatmap
    im = ax.contourf(X, Y, S, levels=50, cmap=cmap, extend='neither')
    
    # Add isolines
    cs = ax.contour(X, Y, S, levels=[0.2, 0.5, 0.8], 
                    colors='black', linewidths=1.5, linestyles='dashed', alpha=0.5)
    ax.clabel(cs, inline=True, fontsize=14, fmt={0.2: 'weak', 0.5: 'moderate', 0.8: 'strong'})
    
    # Add grid
    add_grid(ax)
    
    # Format axes
    ax.set_xscale('log')
    ax.set_xlim([0.1, 3])
    ax.set_ylim([0.0, 0.4])
    ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 3])
    ax.set_yticks([0.0, 0.1, 0.2, 0.3, 0.4])
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.xaxis.set_minor_formatter(ScalarFormatter())
    ax.tick_params(axis='x', which='minor', labelsize=0)
    
    format_axes(ax, r'$k\delta$', r'$C_Z = \frac{|Z_2 - Z_1|}{Z_2 + Z_1}$',
                'Layered Regime Map: Predicted Notch Strength')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, pad=0.02, aspect=30)
    cbar.set_label('Predicted notch strength (arb.)', fontsize=18)
    cbar.ax.tick_params(labelsize=14)
    
    # Add optional insets (simplified representation)
    # We'll add text annotations instead of actual TL(f) sketches
    ax.text(3.5, 0.35, 'Strong comb\n(dense, deep notches)', fontsize=14, 
            transform=ax.transData, bbox=dict(boxstyle="round,pad=0.3", 
            facecolor='white', edgecolor='gray', alpha=0.8))
    ax.text(3.5, 0.2, 'Moderate comb', fontsize=14, 
            transform=ax.transData, bbox=dict(boxstyle="round,pad=0.3", 
            facecolor='white', edgecolor='gray', alpha=0.8))
    ax.text(3.5, 0.05, 'Weak ripples', fontsize=14, 
            transform=ax.transData, bbox=dict(boxstyle="round,pad=0.3", 
            facecolor='white', edgecolor='gray', alpha=0.8))
    
    # Add caption
    caption = ("Figure 3.8B. Notch strength increases with impedance contrast $C_Z$ "
              "and decreases with interface thickness $k\\delta$; sharp, high-contrast "
              "layers produce strong comb-like reverberation.")
    fig.text(0.5, 0.02, caption, fontsize=15, ha='center', style='italic')
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig('figure_3_8B.pdf', format='pdf', bbox_inches='tight')
    plt.savefig('figure_3_8B.png', format='png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Figure 3.8B saved as PDF and PNG")

def figure_3_8C():
    """Figure 3.8C - Qualitative scaling of apparent attenuation vs ω/N"""
    print("Generating Figure 3.8C...")
    
    fig = setup_figure()
    ax = fig.add_subplot(111)
    
    # Create frequency array
    omega_N = np.linspace(0.2, 2.2, 500)
    
    # Define curves for different Ri values
    # Higher Ri = narrower peak, lower Ri = broader peak with skirts
    
    def attenuation_curve(omega_N, Ri):
        """Generate attenuation curve for given Ri"""
        # Base profile: peak at ω/N = 1
        peak_width = 0.15 + 0.4 * np.exp(-Ri)  # Width increases as Ri decreases
        peak_height = 65 - 25 * np.exp(-0.8*Ri)  # Peak height decreases as Ri decreases
        
        # Conversion peak (Gaussian-like)
        peak = peak_height * np.exp(-((omega_N - 1.0) / peak_width)**2)
        
        # Broadband skirts (stronger for low Ri)
        skirt_strength = 15 * np.exp(-2*Ri)
        skirts = skirt_strength * (1 - np.exp(-2*((omega_N - 1.0)/1.5)**2))
        
        # Background attenuation
        background = 25 + 5 * np.sin(2 * np.pi * omega_N / 4)
        
        # Total attenuation
        total = background + peak + skirts
        return np.clip(total, 20, 80)
    
    # Plot curves for different Ri values
    Ri_values = [1.5, 1.0, 0.6, 0.3]
    colors = ['#0040A0', '#4080B0', COLOR_TEAL, COLOR_MAGENTA]
    styles = ['solid', 'solid', 'solid', 'dashed']
    labels = [f'$Ri = {ri}$' for ri in Ri_values]
    
    for Ri, color, style, label in zip(Ri_values, colors, styles, labels):
        TL = attenuation_curve(omega_N, Ri)
        linewidth = 3 if style == 'solid' else 2.5
        ax.plot(omega_N, TL, color=color, linestyle=style, 
                linewidth=linewidth, label=label)
    
    # Add conversion band
    add_conversion_band(ax, alpha=0.15)
    
    # Add grid
    add_grid(ax)
    
    # Format axes
    ax.set_xlim(FREQ_RANGE)
    ax.set_ylim([20, 80])
    ax.set_xticks(FREQ_TICKS)
    ax.set_yticks(range(20, 90, 10))
    format_axes(ax, r'$\omega/N$', 'Apparent Attenuation (dB)',
                'Attenuation Scaling with Richardson Number')
    
    # Add annotations
    ax.annotate('peak widens as $Ri \\downarrow$', 
                xy=(1.0, 55), xytext=(1.4, 60),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1.5),
                fontsize=18, ha='center')
    
    ax.annotate('skirts grow\n(broadband loss)', 
                xy=(1.6, 40), xytext=(1.8, 50),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1.5),
                fontsize=18, ha='center')
    
    # Add legend
    ax.legend(loc='upper left', frameon=False, fontsize=18)
    
    # Add caption
    caption = ("Figure 3.8C. Apparent attenuation vs $\\omega/N$ for selected $Ri$. "
              "Decreasing $Ri$ broadens the conversion peak and raises broadband skirts.")
    fig.text(0.5, 0.02, caption, fontsize=15, ha='center', style='italic')
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig('figure_3_8C.pdf', format='pdf', bbox_inches='tight')
    plt.savefig('figure_3_8C.png', format='png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Figure 3.8C saved as PDF and PNG")

def figure_3_8D():
    """Figure 3.8D - Notch depth vs kδ for several impedance contrasts"""
    print("Generating Figure 3.8D...")
    
    fig = setup_figure()
    ax = fig.add_subplot(111)
    
    # Create kδ array (log scale)
    k_delta = np.logspace(-1, np.log10(3), 200)  # 0.1 to 3
    
    # Define curves for different C_Z values
    C_Z_values = [0.05, 0.10, 0.20, 0.30]
    colors = ['#B0B0B0', COLOR_PURPLE, '#4A2C63', '#2A1C43']
    
    def notch_depth(k_delta, C_Z):
        """Calculate notch depth for given kδ and C_Z"""
        # Initial depth proportional to C_Z
        initial_depth = 20 * (C_Z / 0.3)**0.8
        
        # Decay with kδ
        decay_factor = 1 / (1 + 2 * k_delta**1.5)
        
        # Minimum depth
        min_depth = 2 * C_Z / 0.05
        
        depth = initial_depth * decay_factor + min_depth * (1 - decay_factor)
        return depth
    
    # Plot curves
    for C_Z, color in zip(C_Z_values, colors):
        depth = notch_depth(k_delta, C_Z)
        label = f'$C_Z = {C_Z:.2f}$'
        ax.plot(k_delta, depth, color=color, linewidth=2.5, label=label)
    
    # Add grid
    add_grid(ax)
    
    # Format axes
    ax.set_xscale('log')
    ax.set_xlim([0.1, 3])
    ax.set_ylim([0, 20])
    ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 3])
    ax.set_yticks(range(0, 25, 5))
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.xaxis.set_minor_formatter(ScalarFormatter())
    ax.tick_params(axis='x', which='minor', labelsize=0)
    
    format_axes(ax, r'$k\delta$', 'Notch Depth (dB)',
                'Notch Depth vs Interface Thickness')
    
    # Add bottom axis brace/annotations
    ax.text(0.1, -2, 'thin', fontsize=16, ha='center', va='top')
    ax.text(1.0, -2, 'resonant', fontsize=16, ha='center', va='top')
    ax.text(3.0, -2, 'thick', fontsize=16, ha='center', va='top')
    
    # Draw braces
    ax.annotate('', xy=(0.1, -1), xytext=(0.3, -1),
                arrowprops=dict(arrowstyle='|-|', color='gray', lw=1))
    ax.annotate('', xy=(0.7, -1), xytext=(1.4, -1),
                arrowprops=dict(arrowstyle='|-|', color='gray', lw=1))
    ax.annotate('', xy=(2, -1), xytext=(3, -1),
                arrowprops=dict(arrowstyle='|-|', color='gray', lw=1))
    
    # Add legend
    ax.legend(loc='upper right', frameon=False, fontsize=18)
    
    # Add caption
    caption = ("Figure 3.8D. Notch depth decreases as interface thickness $k\\delta$ "
              "increases and increases with impedance contrast $C_Z$.")
    fig.text(0.5, 0.02, caption, fontsize=15, ha='center', style='italic')
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig('figure_3_8D.pdf', format='pdf', bbox_inches='tight')
    plt.savefig('figure_3_8D.png', format='png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Figure 3.8D saved as PDF and PNG")

def main():
    """Generate all figures"""
    print("="*60)
    print("Generating Thesis Figures 3.8A-D")
    print("="*60)
    
    # Generate each figure
    figure_3_8A()
    figure_3_8B()
    figure_3_8C()
    figure_3_8D()
    
    print("="*60)
    print("All figures generated successfully!")
    print("Output files:")
    print("  - figure_3_8A.pdf/png - Dominant pathway heatmap")
    print("  - figure_3_8B.pdf/png - Layered regime map")
    print("  - figure_3_8C.pdf/png - Apparent attenuation curves")
    print("  - figure_3_8D.pdf/png - Notch depth curves")
    print("="*60)

if __name__ == "__main__":
    main()