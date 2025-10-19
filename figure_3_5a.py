#!/usr/bin/env python3
"""
Figure 3.5A - Finite-thickness interface geometry and controls
Publication-quality schematic showing interface geometry, contrast metrics, and phase-thickness effects
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, Arc, Rectangle
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patheffects as path_effects

# Set up the figure with house style
plt.style.use('default')
fig = plt.figure(figsize=(20, 14))  # 2000x1400 px at 100 dpi
fig.patch.set_facecolor('white')

# House style colors
colors = {
    'primary_blue': '#1F78B4',
    'steel_blue': '#457B9D', 
    'magenta': '#B3007D',
    'orange': '#F05A28',
    'teal': '#2A9D8F',
    'dark_gray': '#555555',
    'light_gray': '#E5E7EB',
    'amber': '#F4A261'
}

# Font settings
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 16,
    'axes.linewidth': 2,
    'lines.linewidth': 3,
    'lines.solid_capstyle': 'round',
    'patch.linewidth': 2
})

# Create main panel (left ~1200x1000 px equivalent)
ax_main = fig.add_axes([0.045, 0.08, 0.6, 0.71])  # Margins: 90px L, 80px top, 110px bottom
ax_main.set_xlim(0, 10)
ax_main.set_ylim(0, 10)
ax_main.set_aspect('equal')

# Create stratified water column with blue gradient
gradient_colors = ['#B3D7FF', '#0B3C5D']  # top to bottom
n_bands = 50
for i in range(n_bands):
    y_start = 10 - (i * 10 / n_bands)
    y_end = 10 - ((i + 1) * 10 / n_bands)
    # Interpolate color
    alpha = i / (n_bands - 1)
    color = [
        int((1 - alpha) * int(gradient_colors[0][1:3], 16) + alpha * int(gradient_colors[1][1:3], 16)),
        int((1 - alpha) * int(gradient_colors[0][3:5], 16) + alpha * int(gradient_colors[1][3:5], 16)),
        int((1 - alpha) * int(gradient_colors[0][5:7], 16) + alpha * int(gradient_colors[1][5:7], 16))
    ]
    color_hex = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
    rect = Rectangle((1, y_end), 8, y_start - y_end, facecolor=color_hex, edgecolor='none')
    ax_main.add_patch(rect)

# Add finite-thickness interface (horizontal magenta band)
interface_y = 5.0
interface_thickness = 0.8
interface_rect = Rectangle((1, interface_y - interface_thickness/2), 8, interface_thickness, 
                          facecolor=colors['magenta'], alpha=0.2, edgecolor=colors['magenta'], linewidth=2)
ax_main.add_patch(interface_rect)

# Add bracket for interface thickness
bracket_x = 9.2
ax_main.plot([bracket_x, bracket_x + 0.1], [interface_y - interface_thickness/2, interface_y - interface_thickness/2], 
             'k-', linewidth=2)
ax_main.plot([bracket_x, bracket_x + 0.1], [interface_y + interface_thickness/2, interface_y + interface_thickness/2], 
             'k-', linewidth=2)
ax_main.plot([bracket_x + 0.05, bracket_x + 0.05], 
             [interface_y - interface_thickness/2, interface_y + interface_thickness/2], 'k-', linewidth=2)
ax_main.text(bracket_x + 0.2, interface_y, r'interface thickness $\delta$', fontsize=18, va='center')

# Add layer property labels
ax_main.text(2, 7, r'upper: $\rho_1, c_1$', fontsize=16, bbox=dict(boxstyle="round,pad=0.3", 
             facecolor='white', alpha=0.8))
ax_main.text(2, 3, r'lower: $\rho_2, c_2$', fontsize=16, bbox=dict(boxstyle="round,pad=0.3", 
             facecolor='white', alpha=0.8))
ax_main.text(7, interface_y + 1, r'$A_t, C_Z$', fontsize=16, bbox=dict(boxstyle="round,pad=0.3", 
             facecolor='white', alpha=0.8))

# Add piston source
piston = plt.Circle((0.5, 6.5), 0.3, facecolor='lightgray', edgecolor='#333333', linewidth=2)
ax_main.add_patch(piston)

# Incidence geometry
theta_deg = 30  # incident angle
theta_rad = np.radians(theta_deg)
incident_start = (0.8, 6.2)
incident_end = (3.5, interface_y + 0.2)

# Incident ray
arrow_incident = FancyArrowPatch(incident_start, incident_end, 
                                arrowstyle='->', mutation_scale=20, 
                                color=colors['orange'], linewidth=3)
ax_main.add_patch(arrow_incident)

# Protractor arc for angle theta
arc_center = incident_end
arc = Arc(arc_center, 1.5, 1.5, angle=0, theta1=0, theta2=theta_deg, 
          color='black', linewidth=2)
ax_main.add_patch(arc)
ax_main.text(arc_center[0] + 0.8, arc_center[1] + 0.3, r'$\theta$', fontsize=20, fontweight='bold')

# Internal multiple passes (etalon-like)
for i in range(3):
    alpha = 0.6 - i * 0.2
    y_top = interface_y + interface_thickness/2
    y_bottom = interface_y - interface_thickness/2
    
    if i == 0:
        # First internal pass
        x_start = incident_end[0]
        x_end = x_start + 1.0
        ax_main.plot([x_start, x_end], [y_top, y_bottom], color=colors['orange'], 
                    linewidth=2, alpha=alpha)
    else:
        # Subsequent bounces
        x_start = incident_end[0] + i * 0.8
        x_end = x_start + 0.8
        if i % 2 == 1:
            ax_main.plot([x_start, x_end], [y_bottom, y_top], color=colors['orange'], 
                        linewidth=1.5, alpha=alpha)
        else:
            ax_main.plot([x_start, x_end], [y_top, y_bottom], color=colors['orange'], 
                        linewidth=1.5, alpha=alpha)

# Reflected ray R
reflect_start = (3.5, interface_y + 0.2)
reflect_end = (1.5, 8.5)
arrow_reflect = FancyArrowPatch(reflect_start, reflect_end, 
                               arrowstyle='->', mutation_scale=20, 
                               color=colors['orange'], linewidth=3)
ax_main.add_patch(arrow_reflect)
ax_main.text(2.2, 7.5, r'$R$', fontsize=24, fontweight='bold', color=colors['orange'])

# Transmitted ray T
transmit_start = (5.5, interface_y - 0.2)
transmit_end = (7.5, 1.5)
arrow_transmit = FancyArrowPatch(transmit_start, transmit_end, 
                                arrowstyle='->', mutation_scale=20, 
                                color=colors['orange'], linewidth=3)
ax_main.add_patch(arrow_transmit)
ax_main.text(6.8, 2.5, r'$T$', fontsize=24, fontweight='bold', color=colors['orange'])

# Axes triad
ax_main.arrow(1.2, 1.2, 0.8, 0, head_width=0.1, head_length=0.1, fc='black', ec='black')
ax_main.arrow(1.2, 1.2, 0, 0.8, head_width=0.1, head_length=0.1, fc='black', ec='black')
ax_main.text(2.1, 1.1, 'x', fontsize=14, fontweight='bold')
ax_main.text(1.1, 2.1, 'z', fontsize=14, fontweight='bold')
ax_main.text(1.2, 0.8, 'z=0 at bottom', fontsize=12)

# Remove axes for main panel
ax_main.set_xticks([])
ax_main.set_yticks([])
ax_main.spines['top'].set_visible(False)
ax_main.spines['right'].set_visible(False)
ax_main.spines['bottom'].set_visible(False)
ax_main.spines['left'].set_visible(False)

# Right mini-column (three frameless micro-plots)
plot_width = 0.13
plot_height = 0.17
plot_x = 0.7
plot_spacing = 0.02

# ρ(z) profiles
ax_rho = fig.add_axes([plot_x, 0.55, plot_width, plot_height])
z = np.linspace(-2, 2, 200)
delta_values = [0.1, 0.5, 1.5]  # sharp, moderate, diffuse
colors_rho = [colors['primary_blue'], colors['steel_blue'], colors['teal']]
alphas = [1.0, 0.8, 0.6]
linewidths = [3, 2.5, 2]

for i, (delta, color, alpha, lw) in enumerate(zip(delta_values, colors_rho, alphas, linewidths)):
    rho_profile = 0.5 * (1 + np.tanh(z / delta))  # tanh transition
    ax_rho.plot(rho_profile, z, color=color, linewidth=lw, alpha=alpha, 
                label=f'δ={delta}')

ax_rho.set_xlim(0, 1)
ax_rho.set_ylim(-2, 2)
ax_rho.set_ylabel(r'$\rho(z)$', fontsize=16, fontweight='bold')
ax_rho.text(0.02, 1.5, 'sharp', fontsize=12, color=colors_rho[0])
ax_rho.text(0.02, 0.5, 'moderate', fontsize=12, color=colors_rho[1])
ax_rho.text(0.02, -0.5, 'diffuse', fontsize=12, color=colors_rho[2])
ax_rho.grid(True, alpha=0.3)
ax_rho.tick_params(labelsize=12)

# c₀(z) profiles
ax_c = fig.add_axes([plot_x, 0.35, plot_width, plot_height])
for i, (delta, color, alpha, lw) in enumerate(zip(delta_values, colors_rho, alphas, linewidths)):
    c_profile = 1500 + 50 * np.tanh(z / delta)  # sound speed transition
    ax_c.plot(c_profile, z, color=color, linewidth=lw, alpha=alpha, linestyle='--')

ax_c.set_xlim(1450, 1550)
ax_c.set_ylim(-2, 2)
ax_c.set_ylabel(r'$c_0(z)$', fontsize=16, fontweight='bold')
ax_c.grid(True, alpha=0.3)
ax_c.tick_params(labelsize=12)

# Optical thickness gauge
ax_gauge = fig.add_axes([plot_x, 0.15, plot_width, plot_height])
k_delta_values = [0.1, 1, 3]
x_positions = [0.2, 0.5, 0.8]

for i, (kd, x_pos) in enumerate(zip(k_delta_values, x_positions)):
    ax_gauge.plot([x_pos, x_pos], [0, 0.1], 'k-', linewidth=2)
    ax_gauge.text(x_pos, -0.05, f'{kd}', fontsize=12, ha='center', fontweight='bold')
    
    # Tiny plane wave cartoons
    if kd == 0.1:
        label = 'thin'
        # Sharp wave
        wave_x = np.linspace(x_pos - 0.08, x_pos + 0.08, 50)
        wave_y = 0.3 + 0.05 * np.sin(20 * np.pi * (wave_x - x_pos))
    elif kd == 1:
        label = 'resonant'
        # Moderate oscillation
        wave_x = np.linspace(x_pos - 0.08, x_pos + 0.08, 50)
        wave_y = 0.3 + 0.05 * np.sin(10 * np.pi * (wave_x - x_pos))
    else:
        label = 'thick'
        # Smooth wave
        wave_x = np.linspace(x_pos - 0.08, x_pos + 0.08, 50)
        wave_y = 0.3 + 0.05 * np.sin(5 * np.pi * (wave_x - x_pos))
    
    ax_gauge.plot(wave_x, wave_y, color=colors['primary_blue'], linewidth=2)
    ax_gauge.text(x_pos, 0.45, label, fontsize=10, ha='center', fontweight='bold')

ax_gauge.set_xlim(0, 1)
ax_gauge.set_ylim(-0.1, 0.5)
ax_gauge.set_title('Optical thickness', fontsize=14, fontweight='bold')
ax_gauge.text(0.5, 0.6, r'$k\delta$', fontsize=16, ha='center', fontweight='bold')
ax_gauge.set_xticks([])
ax_gauge.set_yticks([])
ax_gauge.spines['top'].set_visible(False)
ax_gauge.spines['right'].set_visible(False)
ax_gauge.spines['bottom'].set_visible(False)
ax_gauge.spines['left'].set_visible(False)

# Legend box (bottom-right of main panel)
legend_x = 0.45
legend_y = 0.08
legend_width = 0.19
legend_height = 0.12
ax_legend = fig.add_axes([legend_x, legend_y, legend_width, legend_height])

# Orange line sample
ax_legend.plot([0.05, 0.25], [0.8, 0.8], color=colors['orange'], linewidth=3)
ax_legend.text(0.3, 0.8, 'acoustic rays', fontsize=14, va='center')

# Magenta translucent swatch
legend_rect = Rectangle((0.05, 0.5), 0.2, 0.15, facecolor=colors['magenta'], 
                       alpha=0.2, edgecolor=colors['magenta'])
ax_legend.add_patch(legend_rect)
ax_legend.text(0.3, 0.57, r'finite-thickness interface $\delta$', fontsize=14, va='center')

# Small note
ax_legend.text(0.05, 0.25, r'Amplitude/phase evolve via $k_z\delta$', fontsize=12, 
               style='italic', va='center')
ax_legend.text(0.05, 0.1, 'inside the band', fontsize=12, style='italic', va='center')

ax_legend.set_xlim(0, 1)
ax_legend.set_ylim(0, 1)
ax_legend.set_xticks([])
ax_legend.set_yticks([])
ax_legend.spines['top'].set_visible(False)
ax_legend.spines['right'].set_visible(False)
ax_legend.spines['bottom'].set_visible(False)
ax_legend.spines['left'].set_visible(False)

# Caption (inside canvas)
fig.text(0.5, 0.02, 
         r'Figure 3.5A. Geometry of a finite-thickness interface with contrast $(A_t, C_Z)$, incidence $\theta$, and phase-thickness $k_z\delta$. Multiple internal traversals generate frequency- and angle-dependent $R/T$.',
         fontsize=15, ha='center', style='italic', wrap=True)

plt.tight_layout()
plt.savefig('/workspace/figure_3_5a.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('/workspace/figure_3_5a.pdf', bbox_inches='tight', facecolor='white')
plt.savefig('/workspace/figure_3_5a.svg', bbox_inches='tight', facecolor='white')

print("Figure 3.5A created successfully!")
plt.show()