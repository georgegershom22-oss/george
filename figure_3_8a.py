#!/usr/bin/env python3
"""
Figure 3.8A — Predicted dominant pathway in (Ri, ω/N) for continuous stratification
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as patches

# Set up the figure with the specified style
plt.rcParams['font.family'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['font.size'] = 16
plt.rcParams['axes.linewidth'] = 1.0

# Create figure with specified dimensions (2000x1400 px)
fig, ax = plt.subplots(figsize=(20, 14), dpi=100)
fig.patch.set_facecolor('white')

# Define axes ranges
omega_N = np.linspace(0.2, 2.2, 200)
Ri = np.linspace(0.0, 2.0, 200)
omega_N_grid, Ri_grid = np.meshgrid(omega_N, Ri)

# Create synthetic dominance index D(Ri, ω/N) ∈ [0,1]
# 0 (amber) ⇒ conversion-dominant; 1 (teal) ⇒ shear-dominant
# Conversion-dominant basin centered near ω/N ≈ 1 for moderate/high Ri (Ri ≳ 0.7)
# Shear-dominant tongue for low Ri (Ri ≲ 0.6), widest around conversion band

def dominance_index(omega_N, Ri):
    """Synthetic dominance index function"""
    # Conversion basin: strong near ω/N=1 and high Ri
    conversion_strength = np.exp(-((omega_N - 1.0)**2 / 0.3**2)) * np.exp(-((Ri - 1.2)**2 / 0.8**2))
    
    # Shear tongue: strong at low Ri, especially around ω/N=1
    shear_strength = np.exp(-((Ri - 0.3)**2 / 0.4**2)) * np.exp(-((omega_N - 1.0)**2 / 0.5**2))
    
    # Additional shear strength at very low Ri
    shear_strength += 0.5 * np.exp(-((Ri - 0.1)**2 / 0.2**2))
    
    # Normalize and create dominance index
    total_strength = conversion_strength + shear_strength + 0.1  # small baseline
    D = shear_strength / total_strength
    
    return np.clip(D, 0, 1)

D = dominance_index(omega_N_grid, Ri_grid)

# Create custom colormap: amber → light gray → teal
colors = ['#F4A261', '#F8F9FA', '#2A9D8F']  # amber, light gray, teal
n_bins = 256
cmap = LinearSegmentedColormap.from_list('amber_teal', colors, N=n_bins)

# Plot the heatmap
im = ax.imshow(D, extent=[0.2, 2.2, 0.0, 2.0], aspect='auto', origin='lower', 
               cmap=cmap, vmin=0, vmax=1, interpolation='bilinear')

# Add contours for activity zones
# Solid amber contours for conversion high-activity zone
conversion_activity = 1 - D  # High where D is low (conversion dominant)
conversion_levels = [0.6, 0.8]
cs_conversion = ax.contour(omega_N_grid, Ri_grid, conversion_activity, 
                          levels=conversion_levels, colors='#C06A00', linewidths=2.5)

# Dashed teal contours for shear high-activity zone
shear_activity = D  # High where D is high (shear dominant)
shear_levels = [0.6, 0.8]
cs_shear = ax.contour(omega_N_grid, Ri_grid, shear_activity, 
                     levels=shear_levels, colors='#2A9D8F', linewidths=2.5, linestyles='dashed')

# Add conversion window overlay (translucent amber for 0.8 ≤ ω/N ≤ 1.2)
conversion_band = patches.Rectangle((0.8, 0.0), 0.4, 2.0, 
                                   facecolor='#F4A261', alpha=0.2, zorder=3)
ax.add_patch(conversion_band)

# Add faint dotted centerline at ω/N = 1
ax.axvline(x=1.0, color='#9CA3AF', linewidth=1.2, linestyle=':', zorder=4)

# Set up axes
ax.set_xlim(0.2, 2.2)
ax.set_ylim(0.0, 2.0)

# Set ticks according to specifications
omega_ticks = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
Ri_ticks = [0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0]

ax.set_xticks(omega_ticks)
ax.set_yticks(Ri_ticks)

# Labels with proper formatting
ax.set_xlabel(r'$\omega/N$', fontsize=22, fontweight='normal')
ax.set_ylabel(r'$R_i$', fontsize=22, fontweight='normal')

# Tick label formatting
ax.tick_params(axis='both', which='major', labelsize=16, width=1.0, length=6)
for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontweight('normal')

# Grid (light gray, major ticks only)
ax.grid(True, color='#E5E7EB', linewidth=0.8, alpha=1.0, zorder=1)
ax.set_axisbelow(True)

# Add colorbar
cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=30, pad=0.02)
cbar.set_label('Dominant pathway index $D$ (0 = conversion, 1 = shear)', 
               fontsize=16, fontweight='normal')
cbar.ax.tick_params(labelsize=14)

# Add micro-labels for key features
ax.text(1.0, 1.4, 'conversion\nbasin', fontsize=18, ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='none'))

ax.text(1.0, 0.3, 'shear tongue\n(marginal $R_i$)', fontsize=18, ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='none'))

# Title
ax.set_title('Figure 3.8A', fontsize=28, fontweight='bold', pad=20)

# Caption (positioned below x-axis)
caption_text = ('Figure 3.8A. Predicted dominant pathway map for continuous stratification. '
                'Conversion dominates near $\\omega/N \\approx 1$ at higher $R_i$; '
                'shear dominates under marginal $R_i$, especially around the conversion band.')

fig.text(0.1, 0.02, caption_text, fontsize=15, style='italic', wrap=True, 
         ha='left', va='bottom', transform=fig.transFigure)

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(bottom=0.12)  # Make room for caption

# Save the figure
plt.savefig('/workspace/figure_3_8a.pdf', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.savefig('/workspace/figure_3_8a.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')

print("Figure 3.8A created successfully!")
plt.show()