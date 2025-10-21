#!/usr/bin/env python3
"""
Generate Figure 3.9A-D: Scientific figures with precise styling
Exports PNG (300 dpi) and vector PDF with embedded fonts
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import MultipleLocator, FixedLocator
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# SHARED STYLE CONFIGURATION
# ============================================================================

# Canvas
DPI = 300
WIDTH_PX = 2000
HEIGHT_PX = 1400
WIDTH_IN = WIDTH_PX / DPI
HEIGHT_IN = HEIGHT_PX / DPI

# Typography (convert pt to inches for matplotlib)
PT_TO_IN = 1/72
TITLE_SIZE = 28
AXIS_LABEL_SIZE = 22
TICK_LABEL_SIZE = 16
IN_PLOT_SIZE = 18
LEGEND_SIZE = 17
CAPTION_SIZE = 15
MATH_SUBSCRIPT_RATIO = 0.7

# Colors
COLOR_CLASSICAL = '#6B7280'  # dark gray
COLOR_CONVERSION = '#F4A261'  # amber
COLOR_CONVERSION_DARK = '#C06A00'  # darker amber
COLOR_INTERFACIAL = '#6A4C93'  # purple
COLOR_SHEAR = '#2A9D8F'  # teal
COLOR_PRIMARY = '#1F78B4'  # deep blue
COLOR_GRID = '#E5E7EB'  # light gray
COLOR_GUIDE = '#9CA3AF'  # guide gray

# Line weights
LW_PRIMARY = 3.0
LW_SECONDARY = 2.25
LW_GRID = 0.8
LW_DOTTED = 1.2

# Conversion window
CONVERSION_BAND = (0.8, 1.2)
CONVERSION_CENTER = 1.0
CONVERSION_ALPHA = 0.20

# Font configuration
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
plt.rcParams['mathtext.fontset'] = 'custom'
plt.rcParams['mathtext.sf'] = 'sans'
plt.rcParams['pdf.fonttype'] = 42  # TrueType fonts in PDF
plt.rcParams['ps.fonttype'] = 42


# ============================================================================
# FIGURE 3.9A — Frequency sweep signatures
# ============================================================================

def create_figure_3_9A():
    """Conversion bump and interfacial notches"""
    
    fig, ax = plt.subplots(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI)
    fig.patch.set_facecolor('white')
    
    # Generate frequency array
    omega_N = np.linspace(0.2, 2.2, 1000)
    
    # 1. Classical baseline (gently rising, no bump)
    TL_classical = 30 + 8 * np.log10(omega_N / 0.5)
    
    # 2. Continuous stratification (broad bump centered at ω/N = 1)
    # Create Gaussian-like bump
    bump_amplitude = 7  # dB
    bump_center = 1.0
    bump_width = 0.6 / 2.355  # FWHM to sigma
    bump = bump_amplitude * np.exp(-0.5 * ((omega_N - bump_center) / bump_width)**2)
    TL_continuous = TL_classical + bump
    
    # 3. Continuous + interfaces (add narrow notches)
    TL_interfaces = TL_continuous.copy()
    
    # Add 5 quasi-periodic notches across 0.4-1.8
    notch_centers = np.array([0.5, 0.7, 0.95, 1.25, 1.6])
    for i, center in enumerate(notch_centers):
        notch_depth = 8 + np.random.uniform(-2, 2)  # 6-12 dB
        notch_width = 0.04 * (1 + 0.3 * i / len(notch_centers))  # Weakly increasing width
        notch = notch_depth * np.exp(-0.5 * ((omega_N - center) / notch_width)**2)
        TL_interfaces += notch
    
    # Plot curves
    ax.plot(omega_N, TL_classical, color=COLOR_CLASSICAL, linewidth=LW_SECONDARY,
            linestyle='--', dashes=(8, 6), label='Classical (homogeneous)', zorder=3)
    ax.plot(omega_N, TL_continuous, color=COLOR_PRIMARY, linewidth=LW_PRIMARY,
            solid_capstyle='round', solid_joinstyle='round',
            label='Continuous stratification', zorder=4)
    ax.plot(omega_N, TL_interfaces, color=COLOR_INTERFACIAL, linewidth=LW_PRIMARY,
            solid_capstyle='round', solid_joinstyle='round',
            label='Continuous + interfaces', zorder=5)
    
    # Conversion band overlay
    ax.axvspan(CONVERSION_BAND[0], CONVERSION_BAND[1], 
               color=COLOR_CONVERSION, alpha=CONVERSION_ALPHA, zorder=1)
    ax.axvline(CONVERSION_CENTER, color=COLOR_GUIDE, linewidth=LW_DOTTED,
               linestyle=':', zorder=2)
    
    # Double-headed arrow for notch spacing
    arrow_y = 58
    arrow_x1, arrow_x2 = 0.7, 0.95
    ax.annotate('', xy=(arrow_x2, arrow_y), xytext=(arrow_x1, arrow_y),
                arrowprops=dict(arrowstyle='<->', color='k', lw=1.5))
    ax.text((arrow_x1 + arrow_x2) / 2, arrow_y + 2, r'$\Delta(\omega/N) \approx$ const.',
            ha='center', va='bottom', fontsize=IN_PLOT_SIZE)
    
    # Micro-labels
    ax.text(1.0, 42, 'conversion bump\n(continuous)', ha='center', va='center',
            fontsize=IN_PLOT_SIZE-2, color=COLOR_PRIMARY, style='italic')
    ax.text(1.6, 62, 'interfacial comb\n(notches)', ha='center', va='center',
            fontsize=IN_PLOT_SIZE-2, color=COLOR_INTERFACIAL, style='italic')
    
    # Axes configuration
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(20, 80)
    ax.set_xlabel(r'Normalized frequency $\omega/N$', fontsize=AXIS_LABEL_SIZE, fontweight='normal')
    ax.set_ylabel('Transmission loss TL (dB)', fontsize=AXIS_LABEL_SIZE, fontweight='normal')
    ax.set_title('Figure 3.9A — Frequency sweep signatures', 
                 fontsize=TITLE_SIZE, fontweight='bold', pad=20)
    
    # Ticks
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.set_yticks(np.arange(20, 81, 10))
    ax.tick_params(labelsize=TICK_LABEL_SIZE, which='both', direction='out')
    
    # Grid
    ax.grid(True, color=COLOR_GRID, linewidth=LW_GRID, which='major', alpha=1.0)
    ax.set_axisbelow(True)
    
    # Legend
    ax.legend(loc='upper left', fontsize=LEGEND_SIZE, frameon=False)
    
    # Caption
    caption = (r'Figure 3.9A. Frequency-sweep signatures: a broad conversion bump at '
               r'$\omega/N\!\approx\!1$ for continuous stratification; '
               r'adding sharp interfaces imposes narrow spectral notches on top of the bump.')
    fig.text(0.5, 0.02, caption, ha='center', va='bottom',
             fontsize=CAPTION_SIZE, style='italic', wrap=True)
    
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    
    return fig


# ============================================================================
# FIGURE 3.9B — Angle–frequency plate
# ============================================================================

def create_figure_3_9B():
    """Notch motion with angle; conversion band fixed"""
    
    fig, ax = plt.subplots(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI)
    fig.patch.set_facecolor('white')
    
    # Create meshgrid
    omega_N = np.linspace(0.2, 2.2, 400)
    theta = np.linspace(0, 80, 300)
    OMEGA_N, THETA = np.meshgrid(omega_N, theta)
    
    # Generate heatmap data (darker = higher TL or notch depth)
    # Start with baseline
    TL = 40 + 5 * np.log10(OMEGA_N / 0.5) + 0.1 * THETA
    
    # Add conversion band (horizontal, angle-independent)
    conversion_mask = (OMEGA_N >= 0.8) & (OMEGA_N <= 1.2)
    TL[conversion_mask] += 10
    
    # Add interface-induced notches that shift with angle
    # These appear as slanted dark filaments
    for mode_n in range(1, 6):
        # Each mode creates a notch line that shifts with angle
        # Frequency of notch depends on angle: omega/N = a + b*theta + c*mode_n
        notch_center = 0.4 + 0.3 * mode_n + 0.008 * THETA
        notch_width = 0.03
        notch_depth = 15 * np.exp(-0.5 * ((OMEGA_N - notch_center) / notch_width)**2)
        TL += notch_depth
    
    # Plot heatmap
    im = ax.pcolormesh(OMEGA_N, THETA, TL, cmap='YlOrRd', shading='auto', 
                       vmin=TL.min(), vmax=TL.max())
    
    # Conversion band overlays
    ax.axhline(y=40, xmin=(1.0-0.2)/(2.2-0.2), xmax=(1.0-0.2)/(2.2-0.2),
               color=COLOR_GUIDE, linewidth=LW_DOTTED, linestyle=':', zorder=10)
    ax.axvline(CONVERSION_CENTER, color=COLOR_GUIDE, linewidth=LW_DOTTED,
               linestyle=':', zorder=10)
    
    # Horizontal ruler arrow for conversion band
    ax.annotate('', xy=(1.2, 10), xytext=(0.8, 10),
                arrowprops=dict(arrowstyle='<->', color='white', lw=2))
    ax.text(1.0, 15, 'conversion band\n(angle-independent)', ha='center', va='bottom',
            fontsize=IN_PLOT_SIZE, color='white', weight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=COLOR_CONVERSION_DARK, alpha=0.7))
    
    # Annotate one notch filament
    ax.annotate('interface-induced\nnotch shifts with $\\theta$', 
                xy=(1.6, 60), xytext=(1.85, 45),
                fontsize=IN_PLOT_SIZE-2, color='white', weight='bold',
                arrowprops=dict(arrowstyle='->', color='white', lw=2),
                bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.6))
    
    # Axes configuration
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(0, 80)
    ax.set_xlabel(r'Normalized frequency $\omega/N$', fontsize=AXIS_LABEL_SIZE)
    ax.set_ylabel(r'Incidence angle $\theta$ (degrees)', fontsize=AXIS_LABEL_SIZE)
    ax.set_title('Figure 3.9B — Angle–frequency plate', 
                 fontsize=TITLE_SIZE, fontweight='bold', pad=20)
    
    # Ticks
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.set_yticks([0, 15, 30, 45, 60, 75, 80])
    ax.tick_params(labelsize=TICK_LABEL_SIZE)
    
    # Grid
    ax.grid(True, color=COLOR_GRID, linewidth=LW_GRID, alpha=0.5, zorder=5)
    ax.set_axisbelow(True)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, pad=0.02)
    cbar.set_label('TL (arb.)', fontsize=AXIS_LABEL_SIZE, rotation=270, labelpad=30)
    cbar.ax.tick_params(labelsize=TICK_LABEL_SIZE)
    
    # Caption
    caption = (r'Figure 3.9B. Angle–frequency plate: interface-induced notches shift with angle, '
               r'while the conversion band remains centered at $\omega/N\!\approx\!1$.')
    fig.text(0.5, 0.02, caption, ha='center', va='bottom',
             fontsize=CAPTION_SIZE, style='italic')
    
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    
    return fig


# ============================================================================
# FIGURE 3.9C — Time correlation
# ============================================================================

def create_figure_3_9C():
    """Array coherence vs Ri(t)"""
    
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI)
    fig.patch.set_facecolor('white')
    
    # Create GridSpec for two stacked panels
    gs = GridSpec(2, 1, figure=fig, height_ratios=[1, 1], hspace=0.15,
                  top=0.92, bottom=0.08, left=0.08, right=0.96)
    
    ax_top = fig.add_subplot(gs[0])
    ax_bottom = fig.add_subplot(gs[1], sharex=ax_top)
    
    # Time array
    t = np.linspace(0, 60, 1000)
    
    # Generate Ri(t) with low-Ri bursts
    Ri = 1.0 + 0.3 * np.sin(2 * np.pi * t / 30) + 0.2 * np.sin(2 * np.pi * t / 12)
    
    # Add sharp low-Ri bursts
    burst_times = [15, 28, 42, 52]
    for bt in burst_times:
        burst = 0.6 * np.exp(-0.5 * ((t - bt) / 1.5)**2)
        Ri -= burst
    
    # Ensure Ri stays positive
    Ri = np.maximum(Ri, 0.1)
    
    # Generate coherence γ²(t)
    gamma2 = 0.92 - 0.05 * np.sin(2 * np.pi * t / 30)
    
    # Add conversion-band dip (persistent trough)
    conversion_dip = 0.15 * np.exp(-0.5 * ((t - 30) / 8)**2)
    gamma2 -= conversion_dip
    
    # Add sharp drops aligned with low-Ri bursts
    for bt in burst_times:
        drop = 0.2 * np.exp(-0.5 * ((t - bt) / 2)**2)
        gamma2 -= drop
    
    gamma2 = np.clip(gamma2, 0, 1)
    
    # Plot top panel (coherence)
    ax_top.plot(t, gamma2, color=COLOR_PRIMARY, linewidth=LW_PRIMARY,
                solid_capstyle='round', solid_joinstyle='round')
    
    # Mark conversion dip
    ax_top.annotate('conversion-band dip', xy=(30, 0.75), xytext=(35, 0.65),
                    fontsize=IN_PLOT_SIZE-2, arrowprops=dict(arrowstyle='->', lw=1.5))
    
    # Plot bottom panel (Ri)
    ax_bottom.plot(t, Ri, color='#4682B4', linewidth=LW_PRIMARY,
                   solid_capstyle='round', solid_joinstyle='round')
    
    # Mark low-Ri bursts with translucent teal bands spanning both panels
    for bt in burst_times:
        x_start = bt - 3
        x_end = bt + 3
        
        # Band in bottom panel
        ax_bottom.axvspan(x_start, x_end, color=COLOR_SHEAR, alpha=0.25, zorder=0)
        
        # Extend band into top panel
        ax_top.axvspan(x_start, x_end, color=COLOR_SHEAR, alpha=0.25, zorder=0)
        
        # Vertical guide line
        ax_top.axvline(bt, color=COLOR_GRID, linewidth=0.8, linestyle='--', alpha=0.6, zorder=1)
        ax_bottom.axvline(bt, color=COLOR_GRID, linewidth=0.8, linestyle='--', alpha=0.6, zorder=1)
    
    # Label one low-Ri burst
    ax_bottom.text(burst_times[1], 0.1, 'low-$Ri$ burst', ha='center', va='bottom',
                   fontsize=IN_PLOT_SIZE-2, style='italic')
    
    # Configure top panel
    ax_top.set_ylabel(r'Coherence $\gamma^2(t)$' + '\n' + r'(band near $\omega/N\!\approx\!1$)',
                      fontsize=AXIS_LABEL_SIZE)
    ax_top.set_ylim(0, 1)
    ax_top.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax_top.tick_params(labelsize=TICK_LABEL_SIZE, labelbottom=False)
    ax_top.grid(True, color=COLOR_GRID, linewidth=LW_GRID, alpha=1.0, zorder=0)
    ax_top.set_axisbelow(True)
    ax_top.set_title('Figure 3.9C — Time correlation', 
                     fontsize=TITLE_SIZE, fontweight='bold', pad=20)
    
    # Configure bottom panel
    ax_bottom.set_xlabel('Time (s)', fontsize=AXIS_LABEL_SIZE)
    ax_bottom.set_ylabel(r'Richardson number $Ri(t)$', fontsize=AXIS_LABEL_SIZE)
    ax_bottom.set_xlim(0, 60)
    ax_bottom.set_ylim(0, 2)
    ax_bottom.set_xticks(np.arange(0, 61, 10))
    ax_bottom.set_yticks([0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
    ax_bottom.tick_params(labelsize=TICK_LABEL_SIZE)
    ax_bottom.grid(True, color=COLOR_GRID, linewidth=LW_GRID, alpha=1.0, zorder=0)
    ax_bottom.set_axisbelow(True)
    
    # Caption
    caption = (r'Figure 3.9C. Time correlation between array coherence and $Ri(t)$: '
               r'a persistent conversion-band dip plus intermittent losses coincident '
               r'with low-$Ri$ bursts.')
    fig.text(0.5, 0.01, caption, ha='center', va='bottom',
             fontsize=CAPTION_SIZE, style='italic')
    
    return fig


# ============================================================================
# FIGURE 3.9D — Mechanism-share waterfall
# ============================================================================

def create_figure_3_9D():
    """Stacked shares for four canonical regimes"""
    
    fig, ax = plt.subplots(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI)
    fig.patch.set_facecolor('white')
    
    # Categories
    categories = [
        'High-$Ri$\ncontinuous',
        'Marginal-$Ri$\ncontinuous',
        'Layered\nsharp',
        'Layered\ndiffuse'
    ]
    
    # Shares (classical, conversion, interfacial, shear) - must sum to 1
    shares = np.array([
        [0.40, 0.48, 0.08, 0.04],  # High-Ri continuous
        [0.30, 0.42, 0.05, 0.23],  # Marginal-Ri continuous
        [0.25, 0.20, 0.50, 0.05],  # Layered sharp
        [0.43, 0.30, 0.15, 0.12],  # Layered diffuse
    ])
    
    # Verify shares sum to 1
    for i, cat in enumerate(categories):
        assert abs(shares[i].sum() - 1.0) < 0.01, f"{cat} shares don't sum to 1"
    
    n_cats = len(categories)
    x = np.arange(n_cats)
    width = 0.6
    
    # Stack order: Classical, Conversion, Interfacial, Shear
    colors = [COLOR_CLASSICAL, COLOR_CONVERSION, COLOR_INTERFACIAL, COLOR_SHEAR]
    labels = ['Classical', 'Conversion', 'Interfacial', 'Shear']
    
    # Create stacked bars
    bottom = np.zeros(n_cats)
    
    for i in range(4):
        bars = ax.bar(x, shares[:, i], width, bottom=bottom, 
                     color=colors[i], label=labels[i], 
                     edgecolor='white', linewidth=1.5)
        
        # Add value labels inside bars
        for j, (bar, val) in enumerate(zip(bars, shares[:, i])):
            if val > 0.08:  # Only label if there's enough space
                height = bar.get_height()
                y_pos = bottom[j] + height / 2
                ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
                       f'{val:.2f}', ha='center', va='center',
                       fontsize=TICK_LABEL_SIZE-2, color='white', weight='bold')
        
        bottom += shares[:, i]
    
    # Axes configuration
    ax.set_ylabel('Share', fontsize=AXIS_LABEL_SIZE)
    ax.set_ylim(0, 1)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=AXIS_LABEL_SIZE-2)
    ax.tick_params(axis='y', labelsize=TICK_LABEL_SIZE)
    ax.tick_params(axis='x', length=0)
    
    # Grid
    ax.grid(True, axis='y', color=COLOR_GRID, linewidth=LW_GRID, alpha=1.0, zorder=0)
    ax.set_axisbelow(True)
    
    # Legend
    ax.legend(loc='upper right', fontsize=LEGEND_SIZE, frameon=False, ncol=2)
    
    # Title
    ax.set_title('Figure 3.9D — Mechanism-share waterfall (four canonical regimes)',
                 fontsize=TITLE_SIZE, fontweight='bold', pad=20)
    
    # Caption
    caption = (r'Figure 3.9D. Mechanism shares (summing to unity) for four regimes: '
               r'conversion dominates high-$Ri$ continuous; shear rises under marginal $Ri$; '
               r'interfacial loss peaks for layered sharp and weakens for layered diffuse.')
    fig.text(0.5, 0.02, caption, ha='center', va='bottom',
             fontsize=CAPTION_SIZE, style='italic')
    
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    
    return fig


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Generate all four figures"""
    
    print("Generating Figure 3.9A — Frequency sweep signatures...")
    fig_A = create_figure_3_9A()
    # Save with exact dimensions (no bbox_inches='tight' to ensure exact 2000x1400 px)
    fig_A.savefig('/workspace/Figure_3_9A.png', dpi=DPI,
                  facecolor='white', edgecolor='none')
    fig_A.savefig('/workspace/Figure_3_9A.pdf', bbox_inches='tight',
                  facecolor='white', edgecolor='none')
    plt.close(fig_A)
    print("  ✓ Saved Figure_3_9A.png and Figure_3_9A.pdf")
    
    print("\nGenerating Figure 3.9B — Angle–frequency plate...")
    fig_B = create_figure_3_9B()
    fig_B.savefig('/workspace/Figure_3_9B.png', dpi=DPI,
                  facecolor='white', edgecolor='none')
    fig_B.savefig('/workspace/Figure_3_9B.pdf', bbox_inches='tight',
                  facecolor='white', edgecolor='none')
    plt.close(fig_B)
    print("  ✓ Saved Figure_3_9B.png and Figure_3_9B.pdf")
    
    print("\nGenerating Figure 3.9C — Time correlation...")
    fig_C = create_figure_3_9C()
    fig_C.savefig('/workspace/Figure_3_9C.png', dpi=DPI,
                  facecolor='white', edgecolor='none')
    fig_C.savefig('/workspace/Figure_3_9C.pdf', bbox_inches='tight',
                  facecolor='white', edgecolor='none')
    plt.close(fig_C)
    print("  ✓ Saved Figure_3_9C.png and Figure_3_9C.pdf")
    
    print("\nGenerating Figure 3.9D — Mechanism-share waterfall...")
    fig_D = create_figure_3_9D()
    fig_D.savefig('/workspace/Figure_3_9D.png', dpi=DPI,
                  facecolor='white', edgecolor='none')
    fig_D.savefig('/workspace/Figure_3_9D.pdf', bbox_inches='tight',
                  facecolor='white', edgecolor='none')
    plt.close(fig_D)
    print("  ✓ Saved Figure_3_9D.png and Figure_3_9D.pdf")
    
    print("\n" + "="*70)
    print("All figures generated successfully!")
    print("="*70)
    print("\nOutput files:")
    print("  • Figure_3_9A.png / .pdf — Frequency sweep signatures")
    print("  • Figure_3_9B.png / .pdf — Angle–frequency plate")
    print("  • Figure_3_9C.png / .pdf — Time correlation")
    print("  • Figure_3_9D.png / .pdf — Mechanism-share waterfall")
    print("\nExport specifications:")
    print(f"  • PNG: {DPI} dpi, {WIDTH_PX} × {HEIGHT_PX} px")
    print("  • PDF: Vector format with embedded fonts")


if __name__ == '__main__':
    main()
