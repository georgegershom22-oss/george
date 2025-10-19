#!/usr/bin/env python3
"""
Figure 3.5 Generator - Publication Quality Figures
Generates Figures 3.5A, 3.5B, and 3.5C with consistent house style
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, Rectangle, Polygon, FancyBboxPatch, Circle
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as path_effects
from matplotlib import gridspec
import warnings
warnings.filterwarnings('ignore')

# House style colors (color-blind safe)
COLORS = {
    'primary_blue': '#1F78B4',
    'steel_blue': '#457B9D', 
    'magenta': '#B3007D',
    'dark_gray': '#555555',
    'amber': '#F4A261',
    'grid_gray': '#E5E7EB',
    'purple': '#6A4C93',
    'orange': '#F05A28',
    'teal': '#2A9D8F',
    'light_blue_gradient_top': '#B3D7FF',
    'dark_blue_gradient_bottom': '#0B3C5D',
    'light_gray': '#9CA3AF',
    'charcoal': '#333333'
}

# Figure dimensions
FIG_WIDTH_PX = 2000
FIG_HEIGHT_PX = 1400
DPI = 100
FIG_WIDTH_IN = FIG_WIDTH_PX / DPI
FIG_HEIGHT_IN = FIG_HEIGHT_PX / DPI

# Margins in pixels, converted to figure fraction
MARGIN_LEFT_PX = 90
MARGIN_RIGHT_PX = 90
MARGIN_TOP_PX = 80
MARGIN_BOTTOM_PX = 110

# Typography settings
FONT_FAMILY = 'Arial'
PANEL_TITLE_SIZE = 28
AXIS_LABEL_SIZE = 22
TICK_LABEL_SIZE = 16
CALLOUT_SIZE = 18
LEGEND_SIZE = 16
CAPTION_SIZE = 15

# Line weights
AXIS_LINEWIDTH = 2
PRIMARY_LINEWIDTH = 3
SECONDARY_LINEWIDTH = 2.5
MARKER_LINEWIDTH = 2
DOTTED_LINEWIDTH = 1.2

def setup_figure():
    """Create figure with house style settings"""
    fig = plt.figure(figsize=(FIG_WIDTH_IN, FIG_HEIGHT_IN), dpi=DPI, facecolor='white')
    plt.rcParams['font.family'] = FONT_FAMILY
    plt.rcParams['font.sans-serif'] = [FONT_FAMILY]
    plt.rcParams['mathtext.fontset'] = 'custom'
    plt.rcParams['mathtext.rm'] = FONT_FAMILY
    plt.rcParams['mathtext.it'] = f'{FONT_FAMILY}:italic'
    plt.rcParams['mathtext.bf'] = f'{FONT_FAMILY}:bold'
    return fig

def setup_axes(fig, left_frac, bottom_frac, width_frac, height_frac):
    """Create axes with proper positioning"""
    ax = fig.add_axes([left_frac, bottom_frac, width_frac, height_frac])
    return ax

def style_axes(ax, show_grid=True):
    """Apply house style to axes"""
    ax.spines['top'].set_linewidth(AXIS_LINEWIDTH)
    ax.spines['bottom'].set_linewidth(AXIS_LINEWIDTH)
    ax.spines['left'].set_linewidth(AXIS_LINEWIDTH)
    ax.spines['right'].set_linewidth(AXIS_LINEWIDTH)
    
    if show_grid:
        ax.grid(True, which='major', color=COLORS['grid_gray'], linewidth=0.8, alpha=1.0)
        ax.grid(False, which='minor')
        ax.set_axisbelow(True)
    
    ax.tick_params(axis='both', which='major', labelsize=TICK_LABEL_SIZE, width=MARKER_LINEWIDTH, length=6)
    ax.tick_params(axis='both', which='minor', width=MARKER_LINEWIDTH, length=3)

def create_figure_3_5a():
    """Create Figure 3.5A - Finite-thickness interface geometry and controls"""
    fig = setup_figure()
    
    # Main panel (left side)
    ax_main = setup_axes(fig, 0.06, 0.12, 0.6, 0.75)
    ax_main.set_xlim(0, 10)
    ax_main.set_ylim(0, 10)
    ax_main.set_aspect('equal')
    ax_main.axis('off')
    
    # Create gradient background for water column
    n_gradient = 100
    y_gradient = np.linspace(0, 10, n_gradient)
    for i in range(n_gradient - 1):
        color_ratio = i / (n_gradient - 1)
        r1, g1, b1 = tuple(int(COLORS['light_blue_gradient_top'][j:j+2], 16)/255 for j in (1, 3, 5))
        r2, g2, b2 = tuple(int(COLORS['dark_blue_gradient_bottom'][j:j+2], 16)/255 for j in (1, 3, 5))
        r = r1 * (1 - color_ratio) + r2 * color_ratio
        g = g1 * (1 - color_ratio) + g2 * color_ratio
        b = b1 * (1 - color_ratio) + b2 * color_ratio
        rect = Rectangle((0, y_gradient[i]), 10, y_gradient[i+1] - y_gradient[i],
                        facecolor=(r, g, b), edgecolor='none')
        ax_main.add_patch(rect)
    
    # Add finite-thickness interface band
    interface_y = 5
    interface_thickness = 0.8
    interface_band = Rectangle((0, interface_y - interface_thickness/2), 10, interface_thickness,
                               facecolor=COLORS['magenta'], alpha=0.2, edgecolor='none')
    ax_main.add_patch(interface_band)
    
    # Add bracket for interface thickness
    bracket_x = 9.2
    ax_main.plot([bracket_x, bracket_x], [interface_y - interface_thickness/2, interface_y + interface_thickness/2],
                'k-', linewidth=1.5)
    ax_main.plot([bracket_x - 0.1, bracket_x + 0.1], [interface_y - interface_thickness/2, interface_y - interface_thickness/2],
                'k-', linewidth=1.5)
    ax_main.plot([bracket_x - 0.1, bracket_x + 0.1], [interface_y + interface_thickness/2, interface_y + interface_thickness/2],
                'k-', linewidth=1.5)
    ax_main.text(bracket_x + 0.3, interface_y, r'interface thickness $\delta$', fontsize=CALLOUT_SIZE,
                va='center', ha='left')
    
    # Add layer property labels
    ax_main.text(1.5, interface_y + 1.2, r'upper: $\rho_1, c_1$', fontsize=TICK_LABEL_SIZE,
                ha='left', va='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    ax_main.text(1.5, interface_y - 1.2, r'lower: $\rho_2, c_2$', fontsize=TICK_LABEL_SIZE,
                ha='left', va='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    ax_main.text(8.5, interface_y, r'$A_t, C_Z$', fontsize=TICK_LABEL_SIZE,
                ha='center', va='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Add piston/source disk
    source_x, source_y = 1.5, 7.5
    source = Circle((source_x, source_y), 0.3, facecolor='lightgray', edgecolor=COLORS['charcoal'], linewidth=2)
    ax_main.add_patch(source)
    
    # Add incident ray
    incident_angle = 35  # degrees from horizontal
    incident_length = 3.5
    incident_end_x = source_x + incident_length * np.cos(np.radians(-incident_angle))
    incident_end_y = source_y + incident_length * np.sin(np.radians(-incident_angle))
    
    incident_ray = FancyArrowPatch((source_x, source_y), (incident_end_x, incident_end_y),
                                  arrowstyle='->', mutation_scale=20, linewidth=3,
                                  color=COLORS['orange'])
    ax_main.add_patch(incident_ray)
    
    # Add protractor arc for angle
    arc_radius = 1
    theta_arc = patches.Arc((source_x, source_y), 2*arc_radius, 2*arc_radius, angle=0,
                           theta1=-incident_angle, theta2=0, color='black', linewidth=1)
    ax_main.add_patch(theta_arc)
    ax_main.text(source_x + arc_radius*0.7, source_y - 0.3, r'$\theta$', fontsize=CALLOUT_SIZE, ha='center')
    
    # Add internal multiple passes inside the band (etalon effect)
    n_bounces = 3
    bounce_x_start = incident_end_x
    bounce_y = interface_y
    for i in range(n_bounces):
        alpha = 0.7 * (0.6 ** i)  # Fade with each bounce
        # Upward bounce
        if i > 0:
            ax_main.plot([bounce_x_start + i*0.5, bounce_x_start + i*0.5 + 0.3],
                        [bounce_y - interface_thickness/2, bounce_y + interface_thickness/2],
                        color=COLORS['orange'], linewidth=1.5, alpha=alpha)
        # Downward bounce
        if i < n_bounces - 1:
            ax_main.plot([bounce_x_start + i*0.5 + 0.3, bounce_x_start + (i+1)*0.5],
                        [bounce_y + interface_thickness/2, bounce_y - interface_thickness/2],
                        color=COLORS['orange'], linewidth=1.5, alpha=alpha)
    
    # Add reflected ray
    reflect_start_x = incident_end_x
    reflect_start_y = incident_end_y
    reflect_end_x = reflect_start_x + 2 * np.cos(np.radians(180 - incident_angle))
    reflect_end_y = reflect_start_y + 2 * np.sin(np.radians(180 - incident_angle))
    
    reflected_ray = FancyArrowPatch((reflect_start_x, reflect_start_y), (reflect_end_x, reflect_end_y),
                                   arrowstyle='->', mutation_scale=20, linewidth=3,
                                   color=COLORS['orange'], alpha=0.8)
    ax_main.add_patch(reflected_ray)
    ax_main.text(reflect_end_x - 0.5, reflect_end_y, r'$R$', fontsize=CALLOUT_SIZE + 2, fontweight='bold')
    
    # Add transmitted ray
    transmit_end_x = incident_end_x + 2 * np.cos(np.radians(-incident_angle))
    transmit_end_y = incident_end_y + 2 * np.sin(np.radians(-incident_angle))
    
    transmitted_ray = FancyArrowPatch((incident_end_x, incident_end_y), (transmit_end_x, transmit_end_y),
                                     arrowstyle='->', mutation_scale=20, linewidth=3,
                                     color=COLORS['orange'], alpha=0.8)
    ax_main.add_patch(transmitted_ray)
    ax_main.text(transmit_end_x + 0.3, transmit_end_y, r'$T$', fontsize=CALLOUT_SIZE + 2, fontweight='bold')
    
    # Add axes triad
    ax_main.arrow(0.5, 0.5, 0.5, 0, head_width=0.1, head_length=0.1, fc='black', ec='black')
    ax_main.arrow(0.5, 0.5, 0, 0.5, head_width=0.1, head_length=0.1, fc='black', ec='black')
    ax_main.text(1.1, 0.4, 'x', fontsize=14)
    ax_main.text(0.4, 1.1, 'z', fontsize=14)
    ax_main.text(0.5, 0.2, 'z=0 at bottom', fontsize=12, style='italic')
    
    # Right mini-column plots
    # Plot 1: ρ(z) across interface
    ax1 = setup_axes(fig, 0.72, 0.62, 0.22, 0.18)
    z_range = np.linspace(-2, 2, 500)
    
    # Three curves: sharp, moderate, diffuse
    rho_sharp = 0.5 * (1 + np.tanh(z_range / 0.1))
    rho_moderate = 0.5 * (1 + np.tanh(z_range / 0.5))
    rho_diffuse = 0.5 * (1 + np.tanh(z_range / 1.5))
    
    ax1.plot(z_range, rho_sharp, color=COLORS['primary_blue'], linewidth=2.5, alpha=0.9, label='sharp')
    ax1.plot(z_range, rho_moderate, color=COLORS['primary_blue'], linewidth=2, alpha=0.6, label='moderate')
    ax1.plot(z_range, rho_diffuse, color=COLORS['primary_blue'], linewidth=1.5, alpha=0.4, label='diffuse')
    
    ax1.set_xlabel(r'$z$', fontsize=14)
    ax1.set_ylabel(r'$\rho(z)$', fontsize=14)
    ax1.tick_params(labelsize=12)
    ax1.grid(True, alpha=0.3, linewidth=0.5)
    ax1.legend(fontsize=11, frameon=False, loc='right')
    
    # Plot 2: c₀(z) across interface
    ax2 = setup_axes(fig, 0.72, 0.40, 0.22, 0.18)
    
    c_sharp = 1500 + 50 * (1 + np.tanh(z_range / 0.1))
    c_moderate = 1500 + 50 * (1 + np.tanh(z_range / 0.5))
    c_diffuse = 1500 + 50 * (1 + np.tanh(z_range / 1.5))
    
    ax2.plot(z_range, c_sharp, color=COLORS['steel_blue'], linewidth=2.5, alpha=0.9)
    ax2.plot(z_range, c_moderate, color=COLORS['steel_blue'], linewidth=2, alpha=0.6)
    ax2.plot(z_range, c_diffuse, color=COLORS['steel_blue'], linewidth=1.5, alpha=0.4)
    
    ax2.set_xlabel(r'$z$', fontsize=14)
    ax2.set_ylabel(r'$c_0(z)$', fontsize=14)
    ax2.tick_params(labelsize=12)
    ax2.grid(True, alpha=0.3, linewidth=0.5)
    
    # Plot 3: Optical thickness gauge
    ax3 = setup_axes(fig, 0.72, 0.20, 0.22, 0.12)
    ax3.set_xlim(0, 3.5)
    ax3.set_ylim(0, 1)
    ax3.axis('off')
    
    # Draw scale
    ax3.plot([0.1, 3.2], [0.3, 0.3], 'k-', linewidth=2)
    
    # Add ticks and labels
    tick_positions = [0.1, 1, 3]
    tick_labels = ['0.1', '1', '3']
    descriptions = ['thin', 'resonant', 'thick']
    
    for pos, label, desc in zip(tick_positions, tick_labels, descriptions):
        ax3.plot([pos, pos], [0.25, 0.35], 'k-', linewidth=2)
        ax3.text(pos, 0.15, r'$k\delta=$' + label, fontsize=12, ha='center')
        ax3.text(pos, 0.55, desc, fontsize=11, ha='center', style='italic')
        
        # Add tiny wave cartoons
        x_wave = np.linspace(pos - 0.2, pos + 0.2, 50)
        y_wave = 0.75 + 0.1 * np.sin(2 * np.pi * (pos + 1) * (x_wave - pos))
        ax3.plot(x_wave, y_wave, color=COLORS['orange'], linewidth=1, alpha=0.7)
    
    ax3.text(1.65, 0.9, 'Optical thickness', fontsize=13, ha='center', fontweight='bold')
    
    # Legend box in bottom-right of main panel
    ax_legend = setup_axes(fig, 0.42, 0.15, 0.22, 0.12)
    ax_legend.set_xlim(0, 1)
    ax_legend.set_ylim(0, 1)
    ax_legend.axis('off')
    
    # Legend items
    ax_legend.plot([0.1, 0.3], [0.8, 0.8], color=COLORS['orange'], linewidth=3)
    ax_legend.text(0.35, 0.8, 'acoustic rays', fontsize=LEGEND_SIZE, va='center')
    
    # Magenta swatch
    rect = Rectangle((0.1, 0.45), 0.2, 0.15, facecolor=COLORS['magenta'], alpha=0.2, edgecolor='none')
    ax_legend.add_patch(rect)
    ax_legend.text(0.35, 0.52, r'finite-thickness interface $\delta$', fontsize=LEGEND_SIZE, va='center')
    
    ax_legend.text(0.1, 0.2, r'Amplitude/phase evolve via $k_z\delta$ inside the band',
                  fontsize=LEGEND_SIZE - 2, style='italic')
    
    # Caption
    caption_text = (r"Figure 3.5A. Geometry of a finite-thickness interface with contrast $(A_t, C_Z)$, "
                   r"incidence $\theta$, and phase-thickness $k_z\delta$. "
                   r"Multiple internal traversals generate frequency- and angle-dependent $R/T$.")
    fig.text(0.5, 0.04, caption_text, fontsize=CAPTION_SIZE, style='italic', ha='center')
    
    return fig

def create_figure_3_5b():
    """Create Figure 3.5B - Transmission vs frequency for three regimes"""
    fig = setup_figure()
    
    # Create main axes
    ax = setup_axes(fig, 0.08, 0.12, 0.84, 0.75)
    
    # X-axis: ω/N from 0.2 to 3.5
    omega_N = np.linspace(0.2, 3.5, 1000)
    
    # Generate transmission curves for three regimes
    
    # Sharp/high-contrast: frequent deep notches
    T_sharp = np.ones_like(omega_N)
    notch_centers = [0.45, 0.65, 0.85, 1.05, 1.25, 1.5, 1.8, 2.15, 2.55, 3.0]
    notch_depths = [0.35, 0.5, 0.4, 0.6, 0.45, 0.55, 0.4, 0.5, 0.35, 0.45]
    notch_widths = [0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06, 0.065, 0.07, 0.075]
    
    for center, depth, width in zip(notch_centers, notch_depths, notch_widths):
        gaussian_dip = 1 - depth * np.exp(-((omega_N - center) / width)**2)
        T_sharp *= gaussian_dip
    
    # Add overall envelope
    envelope = 0.95 - 0.05 * np.exp(-((omega_N - 1.0) / 2.0)**2)
    T_sharp *= envelope
    
    # Moderate: shallower, less frequent notches
    T_moderate = np.ones_like(omega_N)
    notch_centers_mod = [0.5, 0.9, 1.2, 1.7, 2.3, 2.9]
    notch_depths_mod = [0.15, 0.2, 0.25, 0.2, 0.15, 0.15]
    notch_widths_mod = [0.06, 0.07, 0.08, 0.09, 0.1, 0.11]
    
    for center, depth, width in zip(notch_centers_mod, notch_depths_mod, notch_widths_mod):
        gaussian_dip = 1 - depth * np.exp(-((omega_N - center) / width)**2)
        T_moderate *= gaussian_dip
    
    T_moderate *= (0.92 - 0.03 * np.exp(-((omega_N - 1.0) / 2.5)**2))
    
    # Diffuse/low-contrast: weak ripples
    T_diffuse = 0.88 + 0.05 * np.sin(3 * omega_N) * np.exp(-((omega_N - 1.5) / 2)**2)
    T_diffuse += 0.03 * np.sin(7 * omega_N) * np.exp(-((omega_N - 1.5) / 3)**2)
    
    # Add conversion window band
    ax.axvspan(0.8, 1.2, facecolor=COLORS['amber'], alpha=0.2, zorder=0)
    
    # Add dotted centerline at ω/N = 1
    ax.axvline(1.0, color=COLORS['light_gray'], linestyle=':', linewidth=DOTTED_LINEWIDTH, zorder=1)
    
    # Plot the three curves
    ax.plot(omega_N, T_sharp, color=COLORS['magenta'], linewidth=PRIMARY_LINEWIDTH, 
            label='Sharp / high-contrast', zorder=3)
    ax.plot(omega_N, T_moderate, color=COLORS['primary_blue'], linewidth=PRIMARY_LINEWIDTH,
            label='Moderate', zorder=3)
    ax.plot(omega_N, T_diffuse, color=COLORS['teal'], linewidth=PRIMARY_LINEWIDTH,
            label='Diffuse / low-contrast', zorder=3)
    
    # Optional: homogeneous baseline
    ax.plot(omega_N, np.ones_like(omega_N) * 0.85, color=COLORS['dark_gray'], 
            linestyle='--', linewidth=1.5, alpha=0.5, zorder=2)
    
    # Add arrow showing notch spacing
    idx1 = np.argmin(np.abs(omega_N - notch_centers[3]))
    idx2 = np.argmin(np.abs(omega_N - notch_centers[4]))
    arrow_y = T_sharp[idx1] + 0.15
    
    ax.annotate('', xy=(notch_centers[4], arrow_y), xytext=(notch_centers[3], arrow_y),
                arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
    ax.text((notch_centers[3] + notch_centers[4])/2, arrow_y + 0.05, 
            r'$\Delta(\omega/N) \approx$ const.', fontsize=CALLOUT_SIZE, ha='center')
    
    # Set axis properties
    ax.set_xlim(0.2, 3.5)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel(r'$\omega/N$', fontsize=AXIS_LABEL_SIZE)
    ax.set_ylabel(r'Transmissivity $|T|^2$', fontsize=AXIS_LABEL_SIZE)
    
    # Set ticks
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 2.0, 3.0])
    ax.set_yticks(np.arange(0, 1.1, 0.1))
    
    # Apply house style
    style_axes(ax)
    
    # Legend
    legend = ax.legend(loc='upper right', fontsize=LEGEND_SIZE, frameon=False)
    
    # Add amber window to legend
    from matplotlib.patches import Patch
    amber_patch = Patch(facecolor=COLORS['amber'], alpha=0.2, label='Conversion window')
    handles, labels = ax.get_legend_handles_labels()
    handles.append(amber_patch)
    labels.append('Conversion window')
    ax.legend(handles=handles, labels=labels, loc='upper right', fontsize=LEGEND_SIZE, frameon=False)
    
    # Caption
    caption_text = ("Figure 3.5B. Transmissivity vs normalized frequency across interface regimes. "
                   "Sharp, high-contrast layers exhibit deep, frequent notches; moderate layers show "
                   "gentler quasi-periodic structure; diffuse/low-contrast layers are nearly smooth.")
    fig.text(0.5, 0.04, caption_text, fontsize=CAPTION_SIZE, style='italic', ha='center')
    
    return fig

def create_figure_3_5c():
    """Create Figure 3.5C - Reflectivity vs incidence angle at fixed contrast"""
    fig = setup_figure()
    
    # Create main axes
    ax = setup_axes(fig, 0.08, 0.12, 0.84, 0.75)
    
    # X-axis: incidence angle θ from 0° to 80°
    theta_deg = np.linspace(0, 80, 500)
    theta_rad = np.deg2rad(theta_deg)
    
    # Generate reflectivity curves for different kδ values
    # Using a model that combines baseline reflectivity with interference terms
    
    # Baseline reflectivity (increases with angle)
    baseline = 0.1 + 0.3 * (np.sin(theta_rad))**2
    
    # kδ = 0.1 (thin/sharp): strong angular lobes
    phase_thin = 2 * np.pi * 0.1 * np.sin(theta_rad)
    interference_thin = 0.25 * np.cos(4 * phase_thin + np.pi/4)**2
    R_thin = np.clip(baseline + interference_thin, 0, 1)
    
    # Add more pronounced oscillations for thin layer
    R_thin += 0.15 * np.sin(6 * theta_rad)**2 * np.exp(-theta_deg/60)
    R_thin = np.clip(R_thin, 0, 1)
    
    # kδ = 1 (resonant): maximum angular modulation
    phase_resonant = 2 * np.pi * 1.0 * np.sin(theta_rad)
    interference_resonant = 0.35 * np.cos(2.5 * phase_resonant)**2
    R_resonant = np.clip(baseline * 0.8 + interference_resonant, 0, 1)
    
    # Add strong lobes
    R_resonant += 0.2 * np.cos(3 * theta_rad + np.pi/6)**2
    R_resonant = np.clip(R_resonant, 0, 1)
    
    # kδ = 3 (thick/diffuse): smooth, muted variation
    phase_thick = 2 * np.pi * 3.0 * np.sin(theta_rad)
    interference_thick = 0.05 * np.cos(8 * phase_thick)**2
    R_thick = baseline * 0.7 + interference_thick
    
    # Smooth out the thick curve
    from scipy.ndimage import gaussian_filter1d
    R_thick = gaussian_filter1d(R_thick, sigma=5)
    R_thick = np.clip(R_thick, 0, 1)
    
    # Plot the three curves
    ax.plot(theta_deg, R_thin, color=COLORS['purple'], linewidth=PRIMARY_LINEWIDTH,
            label=r'$k\delta = 0.1$', zorder=3)
    ax.plot(theta_deg, R_resonant, color=COLORS['orange'], linewidth=PRIMARY_LINEWIDTH,
            label=r'$k\delta = 1$', zorder=3)
    ax.plot(theta_deg, R_thick, color=COLORS['teal'], linewidth=PRIMARY_LINEWIDTH,
            label=r'$k\delta = 3$', zorder=3)
    
    # Add vertical guide at 35° or 55°
    guide_angle = 35
    ax.axvline(guide_angle, color=COLORS['light_gray'], linestyle=':', 
              linewidth=DOTTED_LINEWIDTH, alpha=0.7, zorder=1)
    
    # Add callout arrows and labels
    # Sharp layers arrow
    arrow_angle_1 = 25
    idx_1 = np.argmin(np.abs(theta_deg - arrow_angle_1))
    ax.annotate('sharp layers → strong angular lobes',
                xy=(arrow_angle_1, R_thin[idx_1]), xytext=(arrow_angle_1 + 10, R_thin[idx_1] + 0.2),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                fontsize=CALLOUT_SIZE, ha='left')
    
    # Diffuse layers arrow
    arrow_angle_2 = 55
    idx_2 = np.argmin(np.abs(theta_deg - arrow_angle_2))
    ax.annotate('diffuse layers → muted angular dependence',
                xy=(arrow_angle_2, R_thick[idx_2]), xytext=(arrow_angle_2 - 15, R_thick[idx_2] - 0.15),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                fontsize=CALLOUT_SIZE, ha='center')
    
    # Set axis properties
    ax.set_xlim(0, 80)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel(r'Incidence angle $\theta$ (degrees)', fontsize=AXIS_LABEL_SIZE)
    ax.set_ylabel(r'Reflectivity $|R|^2$', fontsize=AXIS_LABEL_SIZE)
    
    # Set ticks
    ax.set_xticks([0, 15, 30, 45, 60, 75])
    ax.set_yticks(np.arange(0, 1.1, 0.1))
    
    # Apply house style
    style_axes(ax)
    
    # Legend
    legend = ax.legend(loc='upper right', fontsize=LEGEND_SIZE, frameon=False)
    
    # Add note under legend
    ax.text(0.85, 0.55, r'$C_Z$ fixed; $\omega/N$ fixed (representative)',
           fontsize=LEGEND_SIZE - 2, transform=ax.transAxes, style='italic')
    
    # Caption
    caption_text = (r"Figure 3.5C. Reflectivity vs incidence for thickness parameter $k\delta$ at fixed contrast. "
                   "Thin/sharp layers yield pronounced obliquity-dependent lobes; "
                   "diffuse layers produce smoother, muted trends.")
    fig.text(0.5, 0.04, caption_text, fontsize=CAPTION_SIZE, style='italic', ha='center')
    
    return fig

def save_figure(fig, base_name):
    """Save figure in multiple formats"""
    # Save as PNG (300 DPI for publication)
    fig.savefig(f'{base_name}.png', dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"Saved: {base_name}.png")
    
    # Save as SVG (vector format for editing)
    fig.savefig(f'{base_name}.svg', format='svg', bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"Saved: {base_name}.svg")
    
    # Save as PDF (vector format for submission)
    fig.savefig(f'{base_name}.pdf', format='pdf', bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"Saved: {base_name}.pdf")

def main():
    """Generate all three figures"""
    print("Generating Figure 3.5A...")
    fig_3_5a = create_figure_3_5a()
    save_figure(fig_3_5a, 'figure_3_5a')
    
    print("\nGenerating Figure 3.5B...")
    fig_3_5b = create_figure_3_5b()
    save_figure(fig_3_5b, 'figure_3_5b')
    
    print("\nGenerating Figure 3.5C...")
    fig_3_5c = create_figure_3_5c()
    save_figure(fig_3_5c, 'figure_3_5c')
    
    print("\nAll figures generated successfully!")
    print("Files created:")
    print("  - figure_3_5a.png/svg/pdf")
    print("  - figure_3_5b.png/svg/pdf")
    print("  - figure_3_5c.png/svg/pdf")

if __name__ == "__main__":
    main()