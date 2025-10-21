#!/usr/bin/env python3
"""
Figure 3.8B — Layered regime map in (CZ, kδ): predicted notch strength (schematic)
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
k_delta = np.logspace(-1, np.log10(3), 200)  # 0.1 to 3, log scale
C_Z = np.linspace(0.00, 0.40, 200)
k_delta_grid, C_Z_grid = np.meshgrid(k_delta, C_Z)

# Create synthetic notch strength S ∈ [0,1]
# Increases monotonically with C_Z, decreases with k_delta
def notch_strength(k_delta, C_Z):
    """Synthetic notch strength function"""
    # Strength increases with impedance contrast and decreases with interface thickness
    # Use exponential decay with k_delta and linear/power growth with C_Z
    S = (C_Z / 0.4)**1.5 * np.exp(-k_delta / 0.8)
    return np.clip(S, 0, 1)

S = notch_strength(k_delta_grid, C_Z_grid)

# Create colormap for notch strength (pale to dark)
colors = ['#F8F9FA', '#6B7280']  # light gray to dark gray
cmap = LinearSegmentedColormap.from_list('strength', colors, N=256)

# Plot the heatmap
im = ax.imshow(S, extent=[0.1, 3, 0.00, 0.40], aspect='auto', origin='lower', 
               cmap=cmap, vmin=0, vmax=1, interpolation='bilinear')

# Add three dashed isolines for weak/moderate/strong
weak_level = 0.2
moderate_level = 0.5
strong_level = 0.8

cs = ax.contour(k_delta_grid, C_Z_grid, S, 
                levels=[weak_level, moderate_level, strong_level], 
                colors=['#6B7280', '#4B5563', '#1F2937'], 
                linewidths=2, linestyles='dashed')

# Add labels for the contour lines
ax.clabel(cs, inline=True, fontsize=14, fmt={weak_level: 'weak', 
                                            moderate_level: 'moderate', 
                                            strong_level: 'strong'})

# Set up axes with log scale for x-axis
ax.set_xscale('log')
ax.set_xlim(0.1, 3)
ax.set_ylim(0.00, 0.40)

# Set ticks according to specifications
k_delta_ticks = [0.1, 0.2, 0.5, 1, 2, 3]
C_Z_ticks = [0.00, 0.10, 0.20, 0.30, 0.40]

ax.set_xticks(k_delta_ticks)
ax.set_xticklabels([f'{x:g}' for x in k_delta_ticks])
ax.set_yticks(C_Z_ticks)
ax.set_yticklabels([f'{x:.2f}' for x in C_Z_ticks])

# Labels with proper formatting
ax.set_xlabel(r'$k\delta$', fontsize=22, fontweight='normal')
ax.set_ylabel(r'$C_Z = \frac{|Z_2 - Z_1|}{Z_2 + Z_1}$', fontsize=22, fontweight='normal')

# Tick label formatting
ax.tick_params(axis='both', which='major', labelsize=16, width=1.0, length=6)
ax.tick_params(axis='x', which='minor', width=0.5, length=3)
for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontweight('normal')

# Grid (light gray, major ticks only)
ax.grid(True, color='#E5E7EB', linewidth=0.8, alpha=1.0, zorder=1, which='major')
ax.set_axisbelow(True)

# Add colorbar
cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=30, pad=0.02)
cbar.set_label('Predicted notch strength (arb.)', fontsize=16, fontweight='normal')
cbar.ax.tick_params(labelsize=14)

# Optional inset: tiny three-panel strip illustrating TL(f) sketches
# Create inset axes on the right margin
inset_width = 0.15
inset_height = 0.25
inset_x = 0.82
inset_y = 0.6

# Strong comb (top)
ax_inset1 = fig.add_axes([inset_x, inset_y + 0.15, inset_width, 0.08])
f_inset = np.linspace(0, 1, 100)
tl_strong = 30 + 15 * np.sin(20 * np.pi * f_inset) * np.exp(-f_inset * 2)
ax_inset1.plot(f_inset, tl_strong, 'k-', linewidth=1.5)
ax_inset1.set_ylim(10, 50)
ax_inset1.set_xlim(0, 1)
ax_inset1.set_xticks([])
ax_inset1.set_yticks([])
ax_inset1.text(0.5, 0.8, 'strong comb', transform=ax_inset1.transAxes, 
               ha='center', va='center', fontsize=10)
ax_inset1.spines['top'].set_visible(False)
ax_inset1.spines['right'].set_visible(False)

# Moderate comb (middle)
ax_inset2 = fig.add_axes([inset_x, inset_y + 0.05, inset_width, 0.08])
tl_moderate = 35 + 8 * np.sin(12 * np.pi * f_inset) * np.exp(-f_inset * 1.5)
ax_inset2.plot(f_inset, tl_moderate, 'k-', linewidth=1.5)
ax_inset2.set_ylim(20, 50)
ax_inset2.set_xlim(0, 1)
ax_inset2.set_xticks([])
ax_inset2.set_yticks([])
ax_inset2.text(0.5, 0.8, 'moderate', transform=ax_inset2.transAxes, 
               ha='center', va='center', fontsize=10)
ax_inset2.spines['top'].set_visible(False)
ax_inset2.spines['right'].set_visible(False)

# Weak ripples (bottom)
ax_inset3 = fig.add_axes([inset_x, inset_y - 0.05, inset_width, 0.08])
tl_weak = 40 + 3 * np.sin(6 * np.pi * f_inset) * np.exp(-f_inset * 1)
ax_inset3.plot(f_inset, tl_weak, 'k-', linewidth=1.5)
ax_inset3.set_ylim(35, 50)
ax_inset3.set_xlim(0, 1)
ax_inset3.set_xticks([])
ax_inset3.set_yticks([])
ax_inset3.text(0.5, 0.8, 'weak ripples', transform=ax_inset3.transAxes, 
               ha='center', va='center', fontsize=10)
ax_inset3.spines['top'].set_visible(False)
ax_inset3.spines['right'].set_visible(False)

# Add TL(f) label
fig.text(inset_x + inset_width/2, inset_y + 0.28, 'TL(f)', ha='center', va='bottom', 
         fontsize=12, fontweight='bold')

# Title
ax.set_title('Figure 3.8B', fontsize=28, fontweight='bold', pad=20)

# Caption (positioned below x-axis)
caption_text = ('Figure 3.8B. Notch strength increases with impedance contrast $C_Z$ '
                'and decreases with interface thickness $k\\delta$; sharp, high-contrast '
                'layers produce strong comb-like reverberation.')

fig.text(0.1, 0.02, caption_text, fontsize=15, style='italic', wrap=True, 
         ha='left', va='bottom', transform=fig.transFigure)

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(bottom=0.12, right=0.78)  # Make room for caption and insets

# Save the figure
plt.savefig('/workspace/figure_3_8b.pdf', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.savefig('/workspace/figure_3_8b.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')

print("Figure 3.8B created successfully!")
plt.show()