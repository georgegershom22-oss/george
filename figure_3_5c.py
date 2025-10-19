#!/usr/bin/env python3
"""
Figure 3.5C - Reflectivity vs incidence angle at fixed contrast for different kδ
Shows angular dependence of reflectivity at fixed contrast while varying phase-thickness
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

# Set up the figure with house style
plt.style.use('default')
fig, ax = plt.subplots(figsize=(20, 14))  # 2000x1400 px at 100 dpi
fig.patch.set_facecolor('white')

# House style colors
colors = {
    'primary_blue': '#1F78B4',
    'steel_blue': '#457B9D', 
    'magenta': '#B3007D',
    'orange': '#F05A28',
    'teal': '#2A9D8F',
    'purple': '#6A4C93',
    'dark_gray': '#555555',
    'light_gray': '#E5E7EB',
    'amber': '#F4A261',
    'gray_guide': '#9CA3AF'
}

# Font settings
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 16,
    'axes.linewidth': 2,
    'lines.linewidth': 3,
    'lines.solid_capstyle': 'round',
    'patch.linewidth': 2,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'axes.labelsize': 22,
    'axes.titlesize': 28
})

# Set up axes
theta_deg = np.linspace(0, 80, 400)
ax.set_xlim(0, 80)
ax.set_ylim(0, 1)

# X-axis ticks and labels
x_ticks = [0, 15, 30, 45, 60, 75, 80]
ax.set_xticks(x_ticks)
ax.set_xticklabels([f'{x}°' for x in x_ticks])
ax.set_xlabel(r'Incidence angle $\theta$', fontsize=22, fontweight='bold')

# Y-axis ticks and labels
y_ticks = np.arange(0, 1.1, 0.1)
ax.set_yticks(y_ticks)
ax.set_ylabel(r'Reflectivity $|R|^2$', fontsize=22, fontweight='bold')

# Grid (major and minor)
ax.grid(True, color=colors['light_gray'], linewidth=0.8, alpha=0.8)
ax.set_axisbelow(True)

# Optional: Add minor grid for y-axis
y_minor_ticks = np.arange(0, 1.05, 0.05)
ax.set_yticks(y_minor_ticks, minor=True)
ax.grid(True, which='minor', color=colors['light_gray'], linewidth=0.4, alpha=0.5)

def generate_reflectivity_curve(theta_deg, k_delta):
    """
    Generate reflectivity curves with realistic angular dependence
    Combines baseline angular trend with interference effects scaled by kδ
    """
    theta_rad = np.radians(theta_deg)
    
    # Base reflectivity (increases with obliquity)
    # Fresnel-like behavior but simplified
    base_reflectivity = 0.1 + 0.3 * (np.sin(theta_rad))**2
    
    # Interference term that depends on kδ
    # Phase accumulation depends on angle and thickness
    phase_factor = k_delta * np.sin(theta_rad)
    
    if k_delta == 0.1:
        # Thin/sharp: higher base reflectivity, clear oscillatory lobes
        interference = 0.25 * np.cos(8 * phase_factor + np.pi/4)**2
        reflectivity = base_reflectivity + 0.2 + interference
        
    elif k_delta == 1.0:
        # Resonant thickness: pronounced lobes from strong interference
        interference = 0.35 * np.cos(3 * phase_factor)**2
        reflectivity = base_reflectivity + 0.1 + interference
        
    else:  # k_delta == 3.0
        # Thick/diffuse: smoothed angular trend, muted oscillations
        interference = 0.1 * np.cos(1.5 * phase_factor + np.pi/6)**2
        reflectivity = base_reflectivity + 0.05 + interference
    
    # Add some realistic modulation
    if k_delta == 0.1:
        # Additional fine structure for thin layers
        fine_structure = 0.08 * np.cos(15 * phase_factor + np.pi/3)**2
        reflectivity += fine_structure
    elif k_delta == 1.0:
        # Strong angular modulation for resonant case
        modulation = 0.15 * np.sin(2 * phase_factor + np.pi/2)**2
        reflectivity += modulation
    
    # Ensure reflectivity stays in [0, 1]
    reflectivity = np.clip(reflectivity, 0, 1)
    
    return reflectivity

# Generate the three curves for different kδ values
k_delta_values = [0.1, 1.0, 3.0]
curve_colors = [colors['purple'], colors['orange'], colors['teal']]
curve_labels = [r'$k\delta = 0.1$', r'$k\delta = 1$', r'$k\delta = 3$']

reflectivity_curves = []
for k_delta, color, label in zip(k_delta_values, curve_colors, curve_labels):
    reflectivity = generate_reflectivity_curve(theta_deg, k_delta)
    reflectivity_curves.append(reflectivity)
    
    ax.plot(theta_deg, reflectivity, color=color, linewidth=3, 
           label=label, zorder=5)

# Add optional dotted guide at specific angle (e.g., 35° or 55°)
guide_angle = 35
ax.axvline(x=guide_angle, color=colors['gray_guide'], linestyle=':', 
          linewidth=1.5, alpha=0.7, zorder=2)

# Add callout arrows and labels
# "sharp layers → strong angular lobes" near purple curve maxima
purple_curve = reflectivity_curves[0]
# Find a maximum in the purple curve
max_indices = []
for i in range(1, len(purple_curve)-1):
    if (purple_curve[i] > purple_curve[i-1] and 
        purple_curve[i] > purple_curve[i+1] and
        purple_curve[i] > 0.6 and
        20 <= theta_deg[i] <= 60):
        max_indices.append(i)

if max_indices:
    idx = max_indices[len(max_indices)//2]  # Pick a middle maximum
    x_pos = theta_deg[idx]
    y_pos = purple_curve[idx]
    
    ax.annotate('sharp layers → strong angular lobes', 
               xy=(x_pos, y_pos), xytext=(x_pos - 15, y_pos + 0.15),
               arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
               fontsize=14, ha='center', va='bottom',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))

# "diffuse layers → muted angular dependence" near teal curve
teal_curve = reflectivity_curves[2]
# Find a representative point on the teal curve
teal_idx = len(teal_curve) // 2  # Middle of the curve
x_pos_teal = theta_deg[teal_idx]
y_pos_teal = teal_curve[teal_idx]

ax.annotate('diffuse layers → muted angular dependence', 
           xy=(x_pos_teal, y_pos_teal), xytext=(x_pos_teal + 10, y_pos_teal - 0.15),
           arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
           fontsize=14, ha='center', va='top',
           bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))

# Legend
legend_elements = [
    mpatches.Patch(color=colors['purple'], label=r'$k\delta = 0.1$'),
    mpatches.Patch(color=colors['orange'], label=r'$k\delta = 1$'), 
    mpatches.Patch(color=colors['teal'], label=r'$k\delta = 3$')
]

legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=18, 
                  frameon=False, bbox_to_anchor=(0.98, 0.98))

# Add small text under legend
ax.text(0.98, 0.85, r'$C_Z$ fixed; $\omega/N$ fixed', 
        transform=ax.transAxes, fontsize=14, ha='right', va='top',
        style='italic',
        bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
ax.text(0.98, 0.80, '(representative)', 
        transform=ax.transAxes, fontsize=14, ha='right', va='top',
        style='italic',
        bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))

# Set axes properties
ax.spines['top'].set_linewidth(2)
ax.spines['right'].set_linewidth(2)
ax.spines['bottom'].set_linewidth(2)
ax.spines['left'].set_linewidth(2)

# Caption
fig.text(0.5, 0.02, 
         r'Figure 3.5C. Reflectivity vs incidence for thickness parameter $k\delta$ at fixed contrast. Thin/sharp layers yield pronounced obliquity-dependent lobes; diffuse layers produce smoother, muted trends.',
         fontsize=15, ha='center', style='italic', wrap=True)

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(bottom=0.1)

# Save figure
plt.savefig('/workspace/figure_3_5c.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('/workspace/figure_3_5c.pdf', bbox_inches='tight', facecolor='white')
plt.savefig('/workspace/figure_3_5c.svg', bbox_inches='tight', facecolor='white')

print("Figure 3.5C created successfully!")
plt.show()