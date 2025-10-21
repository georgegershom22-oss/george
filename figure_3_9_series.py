#!/usr/bin/env python3
"""
Scientific Figure Series 3.9A-D
High-precision visualizations for acoustic transmission loss analysis
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
from matplotlib.gridspec import GridSpec
import matplotlib.colors as mcolors
from scipy.ndimage import gaussian_filter

# Configuration - Shared house style
FIGURE_SIZE = (20, 14)  # 2000x1400 px at 100 dpi
DPI = 100
EXPORT_DPI = 300

# Color palette
COLORS = {
    'classical': '#6B7280',      # dark gray
    'mode_conversion': '#F4A261', # amber
    'mode_conversion_dark': '#C06A00', # darker amber
    'interfacial': '#6A4C93',    # purple
    'shear': '#2A9D8F',          # teal
    'primary': '#1F78B4',        # deep blue
    'grid': '#E5E7EB',           # light gray
    'dotted': '#9CA3AF',         # gray for dotted guides
    'steel_blue': '#4682B4',     # steel blue for Ri
}

# Typography settings
FONT_TITLE = {'family': 'Arial', 'size': 28, 'weight': 'bold'}
FONT_AXIS_LABEL = {'family': 'Arial', 'size': 22}
FONT_TICK_LABEL = {'family': 'Arial', 'size': 16}
FONT_LEGEND = {'family': 'Arial', 'size': 16}
FONT_INPLOT = {'family': 'Arial', 'size': 20}
FONT_CAPTION = {'family': 'Arial', 'size': 15, 'style': 'italic'}

# Line styles
LINE_PRIMARY = 3.0
LINE_SECONDARY = 2.5
LINE_DASHED = (8, 6)
LINE_DOTTED = 1.2

def setup_axes(ax):
    """Apply shared styling to axes"""
    ax.set_facecolor('white')
    ax.grid(True, color=COLORS['grid'], linewidth=0.8, alpha=0.8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=FONT_TICK_LABEL['size'])

def add_conversion_band(ax, xlim):
    """Add amber conversion band overlay"""
    ax.axvspan(0.8, 1.2, alpha=0.2, color=COLORS['mode_conversion'], zorder=1)
    ax.axvline(1.0, color=COLORS['dotted'], linewidth=LINE_DOTTED, 
               linestyle=':', alpha=0.8, zorder=2)

def create_figure_3_9A():
    """Figure 3.9A - Frequency sweep signatures"""
    fig = plt.figure(figsize=FIGURE_SIZE, facecolor='white', dpi=DPI)
    ax = fig.add_subplot(111)
    
    # X-axis data
    omega_N = np.linspace(0.2, 2.2, 500)
    
    # Classical baseline - gently rising
    classical_TL = 35 + 15 * (omega_N - 0.2) / 2.0
    
    # Continuous stratification - broad bump centered at ω/N=1
    bump_center = 1.0
    bump_width = 0.3  # for FWHM ≈ 0.6
    bump_amplitude = 7
    bump = bump_amplitude * np.exp(-((omega_N - bump_center) / bump_width) ** 2)
    continuous_TL = classical_TL + bump
    
    # Continuous + interfaces - add narrow notches
    continuous_interfaces_TL = continuous_TL.copy()
    
    # Add 5 notches with quasi-periodic spacing
    notch_positions = [0.45, 0.75, 1.05, 1.40, 1.75]
    for pos in notch_positions:
        notch_width = 0.025
        notch_depth = 10
        notch_mask = np.exp(-((omega_N - pos) / notch_width) ** 2)
        continuous_interfaces_TL -= notch_depth * notch_mask
    
    # Plot lines
    ax.plot(omega_N, classical_TL, '--', color=COLORS['classical'], 
            linewidth=LINE_SECONDARY, label='Classical', dashes=LINE_DASHED)
    ax.plot(omega_N, continuous_TL, '-', color=COLORS['primary'], 
            linewidth=LINE_PRIMARY, label='Continuous')
    ax.plot(omega_N, continuous_interfaces_TL, '-', color=COLORS['interfacial'], 
            linewidth=LINE_PRIMARY, label='Continuous + interfaces', alpha=0.9)
    
    # Add conversion band
    add_conversion_band(ax, ax.get_xlim())
    
    # Add annotation for notch spacing
    arrow_props = dict(arrowstyle='<->', color='black', lw=1.5)
    ax.annotate('', xy=(notch_positions[1], 45), xytext=(notch_positions[2], 45),
                arrowprops=arrow_props)
    ax.text(0.9, 46, r'$\Delta(\omega/N) \approx$ const.', 
            fontsize=18, ha='center')
    
    # Add micro-labels
    ax.text(1.0, 52, 'conversion bump\n(continuous)', 
            fontsize=18, ha='center', va='bottom', color=COLORS['primary'])
    ax.text(1.6, 35, 'interfacial comb\n(continuous + interfaces)', 
            fontsize=18, ha='center', color=COLORS['interfacial'])
    
    # Axes setup
    setup_axes(ax)
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(20, 80)
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.set_yticks(range(20, 90, 10))
    
    ax.set_xlabel(r'Normalized frequency $\omega/N$', **FONT_AXIS_LABEL)
    ax.set_ylabel('Transmission Loss, TL (dB)', **FONT_AXIS_LABEL)
    
    # Legend
    ax.legend(loc='upper left', frameon=False, prop={'size': FONT_LEGEND['size']})
    
    # Caption
    fig.text(0.5, 0.02, 
             r'Figure 3.9A. Frequency-sweep signatures: a broad conversion bump at $\omega/N \approx 1$ for continuous stratification;'
             '\nadding sharp interfaces imposes narrow spectral notches on top of the bump.',
             ha='center', **FONT_CAPTION)
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    return fig

def create_figure_3_9B():
    """Figure 3.9B - Angle-frequency plate"""
    fig = plt.figure(figsize=FIGURE_SIZE, facecolor='white', dpi=DPI)
    ax = fig.add_subplot(111)
    
    # Create grid
    omega_N = np.linspace(0.2, 2.2, 200)
    theta = np.linspace(0, 80, 150)
    Omega, Theta = np.meshgrid(omega_N, theta)
    
    # Create base pattern - conversion band
    Z = np.zeros_like(Omega)
    
    # Add horizontal conversion band
    band_center = 1.0
    band_width = 0.2
    for i, om in enumerate(omega_N):
        band_strength = np.exp(-((om - band_center) / band_width) ** 2)
        Z[:, i] += 0.3 * band_strength
    
    # Add angle-dependent notches (filaments)
    num_notches = 5
    for n in range(num_notches):
        # Notch position shifts with angle
        base_pos = 0.4 + n * 0.35
        for j, th in enumerate(theta):
            # Notch shifts to higher frequency with angle
            notch_pos = base_pos + 0.008 * th
            if notch_pos < 2.2:
                idx = np.argmin(np.abs(omega_N - notch_pos))
                notch_width = 3  # width in grid points
                start = max(0, idx - notch_width)
                end = min(len(omega_N), idx + notch_width + 1)
                for k in range(start, end):
                    dist = abs(k - idx)
                    Z[j, k] += 0.8 * np.exp(-(dist/2)**2)
    
    # Smooth the data
    Z = gaussian_filter(Z, sigma=1.5)
    
    # Plot heatmap
    im = ax.pcolormesh(Omega, Theta, Z, cmap='viridis', shading='gouraud')
    
    # Add conversion band overlay
    ax.axvspan(0.8, 1.2, alpha=0.15, color=COLORS['mode_conversion'], zorder=10)
    ax.axvline(1.0, color=COLORS['dotted'], linewidth=LINE_DOTTED, 
               linestyle=':', alpha=0.8, zorder=11)
    
    # Add annotations
    ax.annotate('', xy=(0.8, 40), xytext=(1.2, 40),
                arrowprops=dict(arrowstyle='<->', color='white', lw=1.5))
    ax.text(1.0, 42, 'conversion band\n(angle-independent)', 
            fontsize=18, ha='center', color='white', weight='bold')
    
    ax.text(1.4, 60, 'interface-induced\nnotch shifts with θ', 
            fontsize=18, ha='center', color='white', weight='bold')
    
    # Axes setup
    setup_axes(ax)
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(0, 80)
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.set_yticks([0, 15, 30, 45, 60, 75, 80])
    ax.set_yticklabels(['0°', '15°', '30°', '45°', '60°', '75°', '80°'])
    
    ax.set_xlabel(r'Normalized frequency $\omega/N$', **FONT_AXIS_LABEL)
    ax.set_ylabel(r'Incidence angle $\theta$', **FONT_AXIS_LABEL)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('TL (arb.)', **FONT_AXIS_LABEL)
    cbar.ax.tick_params(labelsize=FONT_TICK_LABEL['size'])
    
    # Caption
    fig.text(0.5, 0.02, 
             r'Figure 3.9B. Angle–frequency plate: interface-induced notches shift with angle, while the conversion band remains centered at $\omega/N \approx 1$.',
             ha='center', **FONT_CAPTION)
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    return fig

def create_figure_3_9C():
    """Figure 3.9C - Time correlation"""
    fig = plt.figure(figsize=FIGURE_SIZE, facecolor='white', dpi=DPI)
    
    # Create two stacked panels
    gs = GridSpec(2, 1, height_ratios=[1, 1], hspace=0.15)
    ax_top = fig.add_subplot(gs[0])
    ax_bot = fig.add_subplot(gs[1])
    
    # Time axis
    time = np.linspace(0, 60, 600)
    
    # Generate Ri(t) data with low-Ri bursts
    Ri = 1.0 + 0.3 * np.sin(0.1 * time)
    # Add low-Ri bursts
    burst_times = [8, 22, 35, 48]
    for bt in burst_times:
        mask = np.exp(-((time - bt) / 2) ** 2)
        Ri -= 0.8 * mask
    Ri = np.clip(Ri, 0.2, 2.0)
    
    # Generate coherence data
    gamma2 = 0.95 * np.ones_like(time)
    # Persistent conversion dip around t=25-35
    conversion_mask = (time > 25) & (time < 35)
    gamma2[conversion_mask] -= 0.15
    # Drops aligned with low-Ri bursts
    for bt in burst_times:
        mask = np.exp(-((time - bt) / 1.5) ** 2)
        gamma2 -= 0.25 * mask
    gamma2 = np.clip(gamma2, 0.3, 1.0)
    
    # Plot top panel - coherence
    ax_top.plot(time, gamma2, '-', color=COLORS['primary'], linewidth=LINE_PRIMARY)
    ax_top.set_ylabel(r'Array coherence $\gamma^2(t)$', **FONT_AXIS_LABEL)
    ax_top.set_ylim(0, 1)
    ax_top.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax_top.set_xlim(0, 60)
    ax_top.set_xticklabels([])
    setup_axes(ax_top)
    
    # Plot bottom panel - Ri
    ax_bot.plot(time, Ri, '-', color=COLORS['steel_blue'], linewidth=LINE_SECONDARY)
    ax_bot.set_ylabel(r'$R_i(t)$', **FONT_AXIS_LABEL)
    ax_bot.set_xlabel('Time (s)', **FONT_AXIS_LABEL)
    ax_bot.set_ylim(0, 2)
    ax_bot.set_yticks([0, 0.25, 0.5, 0.7, 1, 1.5, 2])
    ax_bot.set_xlim(0, 60)
    ax_bot.set_xticks(range(0, 70, 10))
    setup_axes(ax_bot)
    
    # Add vertical bands for low-Ri bursts
    for bt in burst_times:
        width = 3
        # Span both panels
        for ax in [ax_top, ax_bot]:
            ax.axvspan(bt - width/2, bt + width/2, 
                      alpha=0.2, color=COLORS['shear'], zorder=1)
    
    # Add vertical guides
    for bt in burst_times:
        for ax in [ax_top, ax_bot]:
            ax.axvline(bt, color='gray', linewidth=0.8, 
                      linestyle='--', alpha=0.5, zorder=2)
    
    # Add labels
    ax_top.text(30, 0.75, 'conversion-band dip', 
               fontsize=18, ha='center', color=COLORS['primary'])
    ax_top.text(8, 0.5, r'low-$R_i$ burst', 
               fontsize=18, ha='center', color=COLORS['shear'])
    
    # Caption
    fig.text(0.5, 0.02, 
             r'Figure 3.9C. Time correlation between array coherence and $R_i(t)$: a persistent conversion-band dip plus intermittent losses coincident with low-$R_i$ bursts.',
             ha='center', **FONT_CAPTION)
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    return fig

def create_figure_3_9D():
    """Figure 3.9D - Mechanism-share waterfall"""
    fig = plt.figure(figsize=FIGURE_SIZE, facecolor='white', dpi=DPI)
    ax = fig.add_subplot(111)
    
    # Define regimes and their shares
    regimes = [
        r'High-$R_i$' '\ncontinuous',
        r'Marginal-$R_i$' '\ncontinuous',
        'Layered\nsharp',
        'Layered\ndiffuse'
    ]
    
    # Define shares for each regime (classical, conversion, interfacial, shear)
    shares = [
        [0.40, 0.48, 0.07, 0.05],  # High-Ri continuous
        [0.30, 0.42, 0.08, 0.20],  # Marginal-Ri continuous  
        [0.25, 0.20, 0.50, 0.05],  # Layered sharp
        [0.42, 0.30, 0.15, 0.13],  # Layered diffuse
    ]
    
    # Setup bar positions
    x = np.arange(len(regimes))
    width = 0.6
    
    # Create stacked bars
    bottom = np.zeros(len(regimes))
    
    # Colors and labels for each mechanism
    mechanisms = ['Classical', 'Conversion', 'Interfacial', 'Shear']
    colors = [COLORS['classical'], COLORS['mode_conversion'], 
              COLORS['interfacial'], COLORS['shear']]
    
    bars = []
    for i, (mechanism, color) in enumerate(zip(mechanisms, colors)):
        values = [shares[j][i] for j in range(len(regimes))]
        bar = ax.bar(x, values, width, bottom=bottom, color=color, 
                     label=mechanism, edgecolor='white', linewidth=1)
        bars.append(bar)
        
        # Add value labels
        for j, (rect, val) in enumerate(zip(bar, values)):
            if val > 0.08:  # Only show labels for segments > 8%
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width()/2., 
                       bottom[j] + height/2.,
                       f'{val:.2f}', ha='center', va='center',
                       color='white', fontsize=14, weight='bold')
        
        bottom += values
    
    # Axes setup
    setup_axes(ax)
    ax.set_ylim(0, 1)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(['0', '0.25', '0.5', '0.75', '1.0'])
    ax.set_ylabel('Share', **FONT_AXIS_LABEL)
    
    ax.set_xticks(x)
    ax.set_xticklabels(regimes, rotation=0, ha='center')
    ax.tick_params(axis='x', labelsize=FONT_TICK_LABEL['size'])
    
    # Legend
    ax.legend(loc='upper right', frameon=False, prop={'size': FONT_LEGEND['size']},
              ncol=2)
    
    # Title
    ax.set_title('Figure 3.9D — Mechanism-share waterfall (four canonical regimes)',
                 **FONT_TITLE, pad=20)
    
    # Caption
    fig.text(0.5, 0.02, 
             r'Figure 3.9D. Mechanism shares (summing to unity) for four regimes: conversion dominates high-$R_i$ continuous;'
             '\nshear rises under marginal $R_i$; interfacial loss peaks for layered sharp and weakens for layered diffuse.',
             ha='center', **FONT_CAPTION)
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    return fig

def main():
    """Generate all figures"""
    print("Generating Figure 3.9 series...")
    
    # Create all figures
    fig_3_9A = create_figure_3_9A()
    fig_3_9B = create_figure_3_9B()
    fig_3_9C = create_figure_3_9C()
    fig_3_9D = create_figure_3_9D()
    
    # Save figures
    for fig, name in zip([fig_3_9A, fig_3_9B, fig_3_9C, fig_3_9D],
                         ['3_9A', '3_9B', '3_9C', '3_9D']):
        # Save PNG at 300 dpi
        fig.savefig(f'figure_{name}.png', dpi=EXPORT_DPI, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        # Save PDF vector
        fig.savefig(f'figure_{name}.pdf', format='pdf', bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        print(f"  ✓ Saved figure_{name}.png and figure_{name}.pdf")
    
    # Show figures (optional) - disabled for headless mode
    # plt.show()
    
    print("\nAll figures generated successfully!")
    print("Files created:")
    print("  - figure_3_9A.png/pdf: Frequency sweep signatures")
    print("  - figure_3_9B.png/pdf: Angle-frequency plate")  
    print("  - figure_3_9C.png/pdf: Time correlation")
    print("  - figure_3_9D.png/pdf: Mechanism-share waterfall")

if __name__ == '__main__':
    main()