#!/usr/bin/env python3
"""
Scientific Figure Generator for Figure 3.9A-D
Shared house style with precise styling specifications
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.font_manager as fm

# Shared house style constants
CANVAS_WIDTH = 2000
CANVAS_HEIGHT = 1400
DPI = 300

# Color palette (consistent across series)
COLORS = {
    'classical_viscous': '#6B7280',  # dark gray
    'mode_conversion': '#F4A261',    # amber
    'mode_conversion_dark': '#C06A00',  # darker amber for lines
    'interfacial_scattering': '#6A4C93',  # purple
    'shear_baroclinic': '#2A9D8F',   # teal
    'primary_data': '#1F78B4',       # deep blue
    'grid': '#E5E7EB',               # light gray
    'conversion_overlay': '#F4A261', # amber with transparency
    'centerline': '#9CA3AF',         # gray for dotted centerline
    'white': '#FFFFFF'
}

# Typography
FONTS = {
    'family': 'DejaVu Sans',  # Helvetica/Arial equivalent (widely available)
    'title_size': 28,
    'axis_label_size': 22,
    'tick_label_size': 16,
    'inplot_note_size': 18,
    'legend_size': 16,
    'caption_size': 15
}

# Line weights
LINE_WEIGHTS = {
    'primary': 3.0,
    'secondary': 2.5,
    'dashed_primary': 3.0,
    'dashed_secondary': 2.0,
    'dotted_guide': 1.2,
    'grid': 0.8
}

# Set up matplotlib defaults
plt.rcParams['font.family'] = FONTS['family']
plt.rcParams['font.size'] = FONTS['tick_label_size']
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['lines.solid_capstyle'] = 'round'
plt.rcParams['lines.solid_joinstyle'] = 'round'

def setup_figure(figsize_inches=None):
    """Set up figure with proper dimensions and styling"""
    if figsize_inches is None:
        figsize_inches = (CANVAS_WIDTH/DPI, CANVAS_HEIGHT/DPI)
    
    fig = plt.figure(figsize=figsize_inches, facecolor=COLORS['white'], dpi=DPI)
    return fig

def setup_axes(ax, xlabel, ylabel, xlim, ylim, xticks=None, yticks=None):
    """Apply consistent axis styling"""
    ax.set_xlabel(xlabel, fontsize=FONTS['axis_label_size'], fontweight='normal')
    ax.set_ylabel(ylabel, fontsize=FONTS['axis_label_size'], fontweight='normal')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    
    if xticks is not None:
        ax.set_xticks(xticks)
    if yticks is not None:
        ax.set_yticks(yticks)
    
    ax.tick_params(labelsize=FONTS['tick_label_size'])
    ax.grid(True, color=COLORS['grid'], linewidth=LINE_WEIGHTS['grid'], alpha=0.8)
    ax.set_facecolor(COLORS['white'])
    
    # Remove top and right spines for cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

def add_conversion_overlay(ax, alpha=0.2):
    """Add amber conversion window overlay (0.8 ≤ ω/N ≤ 1.2)"""
    # Amber band
    ylim = ax.get_ylim()
    conversion_band = patches.Rectangle((0.8, ylim[0]), 0.4, ylim[1]-ylim[0], 
                                      facecolor=COLORS['conversion_overlay'], 
                                      alpha=alpha, zorder=0)
    ax.add_patch(conversion_band)
    
    # Dotted centerline at ω/N = 1
    ax.axvline(x=1.0, color=COLORS['centerline'], linestyle=':', 
               linewidth=LINE_WEIGHTS['dotted_guide'], zorder=1)

def create_figure_3_9a():
    """Figure 3.9A — Frequency sweep signatures"""
    fig = setup_figure()
    ax = fig.add_subplot(111)
    
    # Frequency range
    omega_N = np.linspace(0.2, 2.2, 1000)
    
    # Define tick positions
    xticks = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
    yticks = np.arange(20, 90, 10)
    
    setup_axes(ax, 'ω/N', 'Transmission Loss TL (dB)', 
               (0.2, 2.2), (20, 80), xticks, yticks)
    
    # Classical baseline (dark gray dashed, gently rising)
    classical_tl = 25 + 8 * np.log10(omega_N / 0.2)  # Gentle rise with frequency
    ax.plot(omega_N, classical_tl, color=COLORS['classical_viscous'], 
            linestyle='--', linewidth=LINE_WEIGHTS['dashed_primary'], 
            label='Classical (homogeneous)', zorder=3)
    
    # Continuous stratification (deep blue with broad bump)
    # Broad bump centered at ω/N = 1, FWHM ≈ 0.6, peak +6-8 dB
    bump_center = 1.0
    bump_width = 0.6
    bump_height = 7.0  # +7 dB above classical
    
    # Gaussian-like bump
    bump = bump_height * np.exp(-0.5 * ((omega_N - bump_center) / (bump_width/2.355))**2)
    continuous_tl = classical_tl + bump
    
    ax.plot(omega_N, continuous_tl, color=COLORS['primary_data'], 
            linewidth=LINE_WEIGHTS['primary'], 
            label='Continuous stratification', zorder=4)
    
    # Continuous + interfaces (purple with notches)
    # Start with same broad bump, add narrow notches
    notch_positions = np.array([0.5, 0.7, 0.9, 1.1, 1.3, 1.5])  # 6 notches
    notch_depths = np.array([8, 10, 12, 10, 9, 7])  # Variable depths 6-12 dB
    notch_widths = 0.03  # 3% wide
    
    interfaces_tl = continuous_tl.copy()
    
    # Add notches as inverted Gaussians
    for pos, depth in zip(notch_positions, notch_depths):
        if 0.4 <= pos <= 1.8:  # Only in specified range
            notch = -depth * np.exp(-0.5 * ((omega_N - pos) / notch_widths)**2)
            interfaces_tl += notch
    
    ax.plot(omega_N, interfaces_tl, color=COLORS['interfacial_scattering'], 
            linewidth=LINE_WEIGHTS['primary'], 
            label='Continuous + interfaces', zorder=5)
    
    # Add conversion overlay
    add_conversion_overlay(ax, alpha=0.2)
    
    # Add annotation for notch spacing
    # Double-headed arrow between two adjacent notches
    arrow_y = 45
    arrow_start = notch_positions[2]  # 0.9
    arrow_end = notch_positions[3]    # 1.1
    
    ax.annotate('', xy=(arrow_end, arrow_y), xytext=(arrow_start, arrow_y),
                arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
    ax.text((arrow_start + arrow_end)/2, arrow_y + 3, 'Δ(ω/N) ≈ const.',
            ha='center', va='bottom', fontsize=FONTS['inplot_note_size'])
    
    # Micro-labels
    ax.text(1.0, continuous_tl[np.argmin(np.abs(omega_N - 1.0))] + 3,
            'conversion bump\n(continuous)', ha='center', va='bottom',
            fontsize=FONTS['inplot_note_size']-2, 
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax.text(0.9, interfaces_tl[np.argmin(np.abs(omega_N - 0.9))] - 8,
            'interfacial comb\n(continuous + interfaces)', ha='center', va='top',
            fontsize=FONTS['inplot_note_size']-2,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Legend
    ax.legend(loc='upper left', fontsize=FONTS['legend_size'], frameon=False)
    
    # Caption
    caption = ("Figure 3.9A. Frequency-sweep signatures: a broad conversion bump at "
              "ω/N ≈ 1 for continuous stratification; adding sharp interfaces imposes "
              "narrow spectral notches on top of the bump.")
    fig.text(0.1, 0.02, caption, fontsize=FONTS['caption_size'], 
             style='italic', wrap=True)
    
    plt.tight_layout()
    return fig

def create_figure_3_9b():
    """Figure 3.9B — Angle–frequency plate"""
    fig = setup_figure()
    ax = fig.add_subplot(111)
    
    # Create mesh
    omega_N = np.linspace(0.2, 2.2, 200)
    theta = np.linspace(0, 80, 160)
    Omega, Theta = np.meshgrid(omega_N, theta)
    
    # Define tick positions
    xticks = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
    yticks = [0, 15, 30, 45, 60, 75, 80]
    
    setup_axes(ax, 'ω/N', 'Incidence angle θ (°)', 
               (0.2, 2.2), (0, 80), xticks, yticks)
    
    # Create notch pattern (dark filaments that shift with angle)
    # Base transmission loss field
    TL = np.ones_like(Omega) * 30  # Base level
    
    # Add conversion band (horizontal amber strip near ω/N ≈ 1)
    conversion_mask = (Omega >= 0.8) & (Omega <= 1.2)
    TL[conversion_mask] += 15  # Higher TL in conversion band
    
    # Add interface-induced notches (slanted filaments)
    # Multiple notch trajectories that shift with angle
    for i in range(5):  # 5 notch orders
        # Each notch follows a trajectory: ω/N shifts with angle
        base_freq = 0.6 + i * 0.3  # Base frequencies
        freq_shift = 0.01 * Theta  # Frequency shifts with angle
        notch_freq = base_freq + freq_shift
        
        # Create notch as function of distance from trajectory
        for j in range(len(theta)):
            for k in range(len(omega_N)):
                dist = abs(omega_N[k] - notch_freq[j, k])
                if dist < 0.05:  # Notch width
                    notch_strength = 25 * np.exp(-(dist/0.02)**2)
                    TL[j, k] += notch_strength
    
    # Create perceptual colormap (darker = higher TL)
    colors = ['#f7f7f7', '#cccccc', '#969696', '#636363', '#252525']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('notch_depth', colors, N=n_bins)
    
    # Plot heatmap
    im = ax.imshow(TL, extent=[0.2, 2.2, 0, 80], aspect='auto', 
                   cmap=cmap, origin='lower', interpolation='bilinear')
    
    # Add conversion band overlay
    add_conversion_overlay(ax, alpha=0.15)
    
    # Add annotations
    ax.text(1.0, 70, 'conversion band\n(angle-independent)', 
            ha='center', va='center', fontsize=FONTS['inplot_note_size'],
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Annotate one filament
    ax.annotate('interface-induced notch\nshifts with θ', 
                xy=(1.5, 40), xytext=(1.8, 60),
                fontsize=FONTS['inplot_note_size']-2,
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cbar.set_label('TL (arb.)', fontsize=FONTS['axis_label_size'])
    
    # Caption
    caption = ("Figure 3.9B. Angle–frequency plate: interface-induced notches shift "
              "with angle, while the conversion band remains centered at ω/N ≈ 1.")
    fig.text(0.1, 0.02, caption, fontsize=FONTS['caption_size'], 
             style='italic', wrap=True)
    
    plt.tight_layout()
    return fig

def create_figure_3_9c():
    """Figure 3.9C — Time correlation"""
    fig = setup_figure()
    
    # Create two stacked panels with shared time axis
    ax1 = plt.subplot(2, 1, 1)  # Top panel - coherence
    ax2 = plt.subplot(2, 1, 2)  # Bottom panel - Ri(t)
    
    # Time axis
    time = np.linspace(0, 60, 600)
    xticks = np.arange(0, 70, 10)
    
    # Top panel: Array coherence γ²(t)
    # High most of the time (≳0.9), with conversion dip and sharp drops
    gamma2 = 0.95 + 0.03 * np.sin(0.1 * time)  # Base high coherence with small variation
    
    # Persistent conversion-band dip (broader, less deep)
    conversion_dip = 0.15 * np.exp(-0.5 * ((time - 30) / 8)**2)
    gamma2 -= conversion_dip
    
    # Sharp drops aligned with low-Ri episodes
    low_ri_times = [15, 25, 45, 52]
    for t_drop in low_ri_times:
        drop = 0.3 * np.exp(-0.5 * ((time - t_drop) / 1.5)**2)
        gamma2 -= drop
    
    gamma2 = np.clip(gamma2, 0, 1)  # Ensure valid range
    
    ax1.plot(time, gamma2, color=COLORS['primary_data'], 
             linewidth=LINE_WEIGHTS['primary'], zorder=3)
    
    ax1.set_ylabel('Array coherence γ²(t)\n(ω/N ≈ 1 band)', 
                   fontsize=FONTS['axis_label_size'])
    ax1.set_ylim(0, 1)
    ax1.set_xlim(0, 60)
    ax1.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax1.tick_params(labelsize=FONTS['tick_label_size'])
    ax1.grid(True, color=COLORS['grid'], linewidth=LINE_WEIGHTS['grid'], alpha=0.8)
    ax1.set_xticklabels([])  # Remove x-axis labels for top panel
    
    # Bottom panel: Ri(t)
    # Steel-blue line with low-Ri bursts
    ri_base = 1.2 + 0.3 * np.sin(0.05 * time) + 0.1 * np.sin(0.2 * time)
    
    # Add low-Ri bursts
    for t_burst in low_ri_times:
        burst = -0.8 * np.exp(-0.5 * ((time - t_burst) / 2)**2)
        ri_base += burst
    
    ri_base = np.clip(ri_base, 0.1, 2.0)  # Ensure valid range
    
    ax2.plot(time, ri_base, color='#4682B4', linewidth=LINE_WEIGHTS['primary'])
    
    # Mark low-Ri bursts with translucent teal bands
    for t_burst in low_ri_times:
        # Find the extent of the burst
        burst_mask = ri_base < 0.5
        burst_indices = np.where(burst_mask & (np.abs(time - t_burst) < 5))[0]
        if len(burst_indices) > 0:
            t_start = time[burst_indices[0]]
            t_end = time[burst_indices[-1]]
            
            # Add vertical band spanning both panels
            for ax in [ax1, ax2]:
                ylim = ax.get_ylim()
                band = patches.Rectangle((t_start, ylim[0]), t_end - t_start, 
                                       ylim[1] - ylim[0], 
                                       facecolor=COLORS['shear_baroclinic'], 
                                       alpha=0.2, zorder=0)
                ax.add_patch(band)
    
    ax2.set_xlabel('Time (s)', fontsize=FONTS['axis_label_size'])
    ax2.set_ylabel('Ri(t)', fontsize=FONTS['axis_label_size'])
    ax2.set_ylim(0, 2)
    ax2.set_xlim(0, 60)
    ax2.set_xticks(xticks)
    ax2.set_yticks([0, 0.25, 0.5, 0.7, 1, 1.5, 2])
    ax2.tick_params(labelsize=FONTS['tick_label_size'])
    ax2.grid(True, color=COLORS['grid'], linewidth=LINE_WEIGHTS['grid'], alpha=0.8)
    
    # Add vertical guides aligning coherence minima to low-Ri windows
    for t_guide in low_ri_times:
        for ax in [ax1, ax2]:
            ax.axvline(x=t_guide, color=COLORS['grid'], linestyle='-', 
                      linewidth=0.5, alpha=0.5, zorder=1)
    
    # Micro-labels
    ax1.text(30, 0.7, 'conversion-band dip', ha='center', va='center',
             fontsize=FONTS['inplot_note_size']-2,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax2.text(15, 0.3, 'low-Ri burst', ha='center', va='center',
             fontsize=FONTS['inplot_note_size']-2,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Caption
    caption = ("Figure 3.9C. Time correlation between array coherence and Ri(t): "
              "a persistent conversion-band dip plus intermittent losses coincident "
              "with low-Ri bursts.")
    fig.text(0.1, 0.02, caption, fontsize=FONTS['caption_size'], 
             style='italic', wrap=True)
    
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.1)  # Reduce space between panels
    return fig

def create_figure_3_9d():
    """Figure 3.9D — Mechanism-share waterfall"""
    fig = setup_figure()
    ax = fig.add_subplot(111)
    
    # Categories and their shares
    categories = ['High-Ri\ncontinuous', 'Marginal-Ri\ncontinuous', 
                  'Layered\nsharp', 'Layered\ndiffuse']
    
    # Target shares (qualitative proportions) - must sum to 1.0
    shares = {
        'classical': [0.40, 0.30, 0.25, 0.45],
        'conversion': [0.50, 0.40, 0.20, 0.30],
        'interfacial': [0.05, 0.05, 0.50, 0.15],
        'shear': [0.05, 0.25, 0.05, 0.10]
    }
    
    # Verify shares sum to 1
    for i in range(len(categories)):
        total = sum(shares[mechanism][i] for mechanism in shares.keys())
        print(f"{categories[i]}: total = {total:.2f}")
    
    # Colors for stacking (bottom to top)
    colors = [COLORS['classical_viscous'], COLORS['mode_conversion'], 
              COLORS['interfacial_scattering'], COLORS['shear_baroclinic']]
    labels = ['Classical', 'Conversion', 'Interfacial', 'Shear']
    mechanisms = ['classical', 'conversion', 'interfacial', 'shear']
    
    # Create stacked bar chart
    x_pos = np.arange(len(categories))
    bottoms = np.zeros(len(categories))
    
    bars = []
    for i, (mechanism, color, label) in enumerate(zip(mechanisms, colors, labels)):
        values = shares[mechanism]
        bars.append(ax.bar(x_pos, values, bottom=bottoms, color=color, 
                          label=label, width=0.6, edgecolor='white', linewidth=1))
        
        # Add value labels in each segment if space allows
        for j, (val, bottom) in enumerate(zip(values, bottoms)):
            if val > 0.08:  # Only label if segment is large enough
                ax.text(j, bottom + val/2, f'{val:.2f}', 
                       ha='center', va='center', fontsize=12, 
                       fontweight='bold', color='white')
        
        bottoms += values
    
    # Styling
    ax.set_xlabel('')  # Categories are labeled on x-axis
    ax.set_ylabel('Share', fontsize=FONTS['axis_label_size'])
    ax.set_ylim(0, 1)
    ax.set_xlim(-0.5, len(categories) - 0.5)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, fontsize=FONTS['tick_label_size'], rotation=0)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.tick_params(labelsize=FONTS['tick_label_size'])
    ax.grid(True, color=COLORS['grid'], linewidth=LINE_WEIGHTS['grid'], 
            alpha=0.8, axis='y')
    ax.set_axisbelow(True)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Legend
    ax.legend(loc='upper right', fontsize=FONTS['legend_size'], frameon=False)
    
    # Title
    ax.set_title('Figure 3.9D — Mechanism-share waterfall (four canonical regimes)',
                fontsize=FONTS['title_size'], fontweight='bold', pad=20)
    
    # Caption
    caption = ("Figure 3.9D. Mechanism shares (summing to unity) for four regimes: "
              "conversion dominates high-Ri continuous; shear rises under marginal Ri; "
              "interfacial loss peaks for layered sharp and weakens for layered diffuse.")
    fig.text(0.1, 0.02, caption, fontsize=FONTS['caption_size'], 
             style='italic', wrap=True)
    
    plt.tight_layout()
    return fig

def export_figures():
    """Export all figures as PNG (300 dpi) and PDF with embedded fonts"""
    figures = {
        'figure_3_9a': create_figure_3_9a(),
        'figure_3_9b': create_figure_3_9b(),
        'figure_3_9c': create_figure_3_9c(),
        'figure_3_9d': create_figure_3_9d()
    }
    
    for name, fig in figures.items():
        # Export PNG at 300 dpi
        fig.savefig(f'/workspace/{name}.png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        
        # Export PDF with embedded fonts
        fig.savefig(f'/workspace/{name}.pdf', bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        
        print(f"Exported {name}.png and {name}.pdf")
        
        # Close figure to free memory
        plt.close(fig)

if __name__ == "__main__":
    print("Generating scientific figures 3.9A-D...")
    export_figures()
    print("All figures generated successfully!")