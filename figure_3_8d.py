#!/usr/bin/env python3
"""
Figure 3.8D — Notch depth vs kδ for several impedance contrasts CZ
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set up the figure with the specified style
plt.rcParams['font.family'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['font.size'] = 16
plt.rcParams['axes.linewidth'] = 1.0

# Create figure with specified dimensions (2000x1400 px)
fig, ax = plt.subplots(figsize=(20, 14), dpi=100)
fig.patch.set_facecolor('white')

# Define k_delta range (log scale)
k_delta = np.logspace(-1, np.log10(3), 1000)  # 0.1 to 3

# Define impedance contrasts and their properties
C_Z_values = [0.05, 0.10, 0.20, 0.30]
colors = ['#A78BFA', '#6A4C93', '#4C1D95', '#1E1B4B']  # light gray-purple to nearly black-purple
labels = [f'$C_Z = {cz:.2f}$' for cz in C_Z_values]

def notch_depth(k_delta, C_Z):
    """
    Synthetic notch depth function
    Depth decays with increasing kδ and grows with CZ
    """
    # Base depth scales with impedance contrast
    base_depth = C_Z * 60  # Scale factor to get reasonable dB values
    
    # Decay function - exponential decay with kδ
    # Slower decay for higher contrasts (they maintain depth better)
    decay_rate = 1.5 - C_Z * 2  # Higher CZ has slower decay
    decay_factor = np.exp(-k_delta / decay_rate)
    
    # Additional power law component for realistic behavior
    power_component = (0.1 / k_delta)**0.3
    
    depth = base_depth * decay_factor * power_component
    
    # Ensure minimum depth and realistic range
    depth = np.maximum(depth, base_depth * 0.1)  # Minimum 10% of base
    depth = np.minimum(depth, 20)  # Cap at 20 dB
    
    return depth

# Plot the curves
for i, (C_Z, color, label) in enumerate(zip(C_Z_values, colors, labels)):
    depth = notch_depth(k_delta, C_Z)
    ax.plot(k_delta, depth, color=color, linewidth=3, linestyle='-', label=label)

# Set up axes with log scale for x-axis
ax.set_xscale('log')
ax.set_xlim(0.1, 3)
ax.set_ylim(0, 20)

# Set ticks according to specifications
k_delta_ticks = [0.1, 0.2, 0.5, 1, 2, 3]
depth_ticks = np.arange(0, 21, 5)

ax.set_xticks(k_delta_ticks)
ax.set_xticklabels([f'{x:g}' for x in k_delta_ticks])
ax.set_yticks(depth_ticks)

# Labels with proper formatting
ax.set_xlabel(r'$k\delta$', fontsize=22, fontweight='normal')
ax.set_ylabel('Notch depth (dB)', fontsize=22, fontweight='normal')

# Tick label formatting
ax.tick_params(axis='both', which='major', labelsize=16, width=1.0, length=6)
ax.tick_params(axis='x', which='minor', width=0.5, length=3)
for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontweight('normal')

# Grid (light gray, major ticks only)
ax.grid(True, color='#E5E7EB', linewidth=0.8, alpha=1.0, zorder=0, which='major')
ax.set_axisbelow(True)

# Add bottom axis brace labeled "thin → resonant → thick"
brace_y = -2.5
brace_positions = [0.1, 1, 3]
brace_labels = ['thin', 'resonant', 'thick']

# Draw the brace
ax.annotate('', xy=(0.1, brace_y), xytext=(3, brace_y),
            arrowprops=dict(arrowstyle='|-|', color='black', lw=1.5),
            annotation_clip=False)

# Add labels at specific positions
for pos, label in zip(brace_positions, brace_labels):
    ax.text(pos, brace_y - 1, label, ha='center', va='top', fontsize=14,
            transform=ax.get_xaxis_transform(), clip_on=False)

# Add micro-labels on each curve (alternative to compact legend)
# Position labels at different k_delta values to avoid overlap
label_positions = [(2.5, 2), (2.2, 4.5), (1.8, 8.5), (1.5, 12)]
for i, (C_Z, color, (x_pos, y_pos)) in enumerate(zip(C_Z_values, colors, label_positions)):
    ax.text(x_pos, y_pos, f'$C_Z = {C_Z:.2f}$', color=color, fontsize=16, 
            fontweight='bold', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='none'))

# Alternative: Compact legend in upper-right
# legend = ax.legend(loc='upper right', frameon=False, fontsize=16)
# for text in legend.get_texts():
#     text.set_fontweight('normal')

# Title
ax.set_title('Figure 3.8D', fontsize=28, fontweight='bold', pad=20)

# Caption (positioned below x-axis)
caption_text = ('Figure 3.8D. Notch depth decreases as interface thickness $k\\delta$ '
                'increases and increases with impedance contrast $C_Z$.')

fig.text(0.1, 0.02, caption_text, fontsize=15, style='italic', wrap=True, 
         ha='left', va='bottom', transform=fig.transFigure)

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(bottom=0.15)  # Make room for caption and brace

# Save the figure
plt.savefig('/workspace/figure_3_8d.pdf', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.savefig('/workspace/figure_3_8d.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')

print("Figure 3.8D created successfully!")
plt.show()