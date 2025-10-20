#!/usr/bin/env python3
"""
Figure 3.7A — Composite attenuation concept (block diagram)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np

# House style settings
DPI = 100
WIDTH_PX = 2000
HEIGHT_PX = 1400
FIGSIZE = (WIDTH_PX / DPI, HEIGHT_PX / DPI)

# Colors
CLASSICAL_COLOR = '#6B7280'
CONVERSION_COLOR = '#F4A261'
CONVERSION_DARK = '#C06A00'
INTERFACIAL_COLOR = '#6A4C93'
SHEAR_COLOR = '#2A9D8F'
GRID_COLOR = '#E5E7EB'
CENTERLINE_COLOR = '#9CA3AF'

# Font sizes (pt)
TITLE_SIZE = 28
LABEL_SIZE = 22
TICK_SIZE = 16
NOTE_SIZE = 18
LEGEND_SIZE = 16
CAPTION_SIZE = 15

# Create figure
fig = plt.figure(figsize=FIGSIZE, facecolor='white', dpi=DPI)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Title
ax.text(50, 95, 'Figure 3.7A — Composite attenuation concept',
        ha='center', va='top', fontsize=TITLE_SIZE, fontweight='bold',
        fontfamily='sans-serif')

# === (A) Inputs column (left) ===
inputs_x = 12
inputs_y = 70
inputs_width = 15
inputs_height = 35

# Input box
input_box = FancyBboxPatch((inputs_x, inputs_y - inputs_height), inputs_width, inputs_height,
                           boxstyle="round,pad=0.3", edgecolor='black', facecolor='white',
                           linewidth=2)
ax.add_patch(input_box)

ax.text(inputs_x + inputs_width/2, inputs_y - 2, 'Inputs',
        ha='center', va='top', fontsize=LABEL_SIZE, fontweight='bold',
        fontfamily='sans-serif')

# Input items with bullets
input_items = [
    r'$\omega/N$ (frequency ratio)',
    r'$Ri$ (stability)',
    r'$k\delta$ (interface thickness)',
    r'$C_Z$, $A_t$ (contrast)',
    r'Geometry: $\theta$, $r$'
]

y_pos = inputs_y - 6
for item in input_items:
    # Bullet
    circle = Circle((inputs_x + 1, y_pos), 0.3, color='black')
    ax.add_patch(circle)
    # Text
    ax.text(inputs_x + 2, y_pos, item, ha='left', va='center',
            fontsize=NOTE_SIZE - 2, fontfamily='sans-serif')
    y_pos -= 5.5

    # Arrow to center
    arrow = FancyArrowPatch((inputs_x + inputs_width, y_pos + 2.5),
                           (37, 58),
                           arrowstyle='->', mutation_scale=15, linewidth=1.5,
                           color='black', alpha=0.6)
    ax.add_patch(arrow)

# === (B) Similarity space cue (center-top) ===
sim_x = 35
sim_y = 85
sim_width = 26
sim_height = 16

# Small thumbnail map
ax.text(sim_x + sim_width/2, sim_y + 1, 'Similarity space',
        ha='center', va='bottom', fontsize=NOTE_SIZE - 2, fontweight='bold',
        fontfamily='sans-serif')

# Create mini axes for similarity plot
sim_ax = fig.add_axes([sim_x/100, (sim_y - sim_height)/100, sim_width/100, sim_height/100])
sim_ax.set_xlim(0.2, 2.2)
sim_ax.set_ylim(0, 2)
sim_ax.set_xlabel(r'$\omega/N$', fontsize=NOTE_SIZE - 2)
sim_ax.set_ylabel(r'$Ri$', fontsize=NOTE_SIZE - 2)
sim_ax.tick_params(labelsize=TICK_SIZE - 4)
sim_ax.grid(True, color=GRID_COLOR, linewidth=0.8)

# Overlay soft regions
sim_ax.axvspan(0.8, 1.2, alpha=0.15, color=CONVERSION_COLOR, label='conversion belt')
sim_ax.fill_between([0.2, 2.2], [0, 0], [0.5, 0.5], alpha=0.1, color=SHEAR_COLOR, label='shear-favored')
sim_ax.fill_between([0.2, 0.8], [1.2, 1.2], [2, 2], alpha=0.1, color=CLASSICAL_COLOR, label='near-classical')

sim_ax.text(1.0, 0.3, 'conversion\nbelt', ha='center', va='center',
            fontsize=TICK_SIZE - 4, color=CONVERSION_DARK, fontstyle='italic')
sim_ax.text(0.5, 0.25, 'shear-\nfavored', ha='center', va='center',
            fontsize=TICK_SIZE - 4, color=SHEAR_COLOR, fontstyle='italic')

# === (C) Mechanism weighting module (center-middle) ===
mech_x = 35
mech_y = 60
mech_width = 28
mech_height = 13

# Module box
mech_box = FancyBboxPatch((mech_x, mech_y - mech_height), mech_width, mech_height,
                          boxstyle="round,pad=0.5", edgecolor='black', facecolor='#F9FAFB',
                          linewidth=2.5)
ax.add_patch(mech_box)

ax.text(mech_x + mech_width/2, mech_y - 1, 'Mechanism weighting\n(shares sum to 1)',
        ha='center', va='top', fontsize=NOTE_SIZE, fontweight='bold',
        fontfamily='sans-serif')

# Stacked bar showing mechanism shares
bar_x = mech_x + 2
bar_y = mech_y - 6.5
bar_width = mech_width - 4
bar_height = 2

# Example shares
shares = [0.35, 0.40, 0.15, 0.10]  # Classical, Conversion, Interfacial, Shear
colors = [CLASSICAL_COLOR, CONVERSION_COLOR, INTERFACIAL_COLOR, SHEAR_COLOR]
labels = ['Classical', 'Conversion', 'Interfacial', 'Shear']

cumsum = 0
for share, color, label in zip(shares, colors, labels):
    width = share * bar_width
    rect = mpatches.Rectangle((bar_x + cumsum, bar_y), width, bar_height,
                              facecolor=color, edgecolor='white', linewidth=1)
    ax.add_patch(rect)
    # Label in center of segment
    ax.text(bar_x + cumsum + width/2, bar_y + bar_height/2, label,
            ha='center', va='center', fontsize=TICK_SIZE - 2,
            color='white', fontweight='bold', fontfamily='sans-serif')
    cumsum += width

# Sum annotation
ax.text(mech_x + mech_width + 1.5, bar_y + bar_height/2, r'$\sum w_i = 1$',
        ha='left', va='center', fontsize=NOTE_SIZE, fontfamily='sans-serif')

# Guidance note
ax.text(mech_x + mech_width/2, mech_y - mech_height + 1.5,
        'shares guided by §3.2 similarity & §3.4–3.6 scalings',
        ha='center', va='bottom', fontsize=TICK_SIZE - 2, fontstyle='italic',
        fontfamily='sans-serif')

# === (D) Combination node (center-bottom) ===
combo_x = 49
combo_y = 35

# Sigma node
ax.text(combo_x, combo_y, r'$\Sigma$', ha='center', va='center',
        fontsize=32, fontweight='bold', bbox=dict(boxstyle='circle', 
        facecolor='white', edgecolor='black', linewidth=2))

ax.text(combo_x, combo_y - 3.5, 'Composite\nattenuation', ha='center', va='top',
        fontsize=NOTE_SIZE - 2, fontweight='bold', fontfamily='sans-serif')

# Arrow from weighting to combo
arrow1 = FancyArrowPatch((mech_x + mech_width/2, mech_y - mech_height),
                        (combo_x, combo_y + 2),
                        arrowstyle='->', mutation_scale=20, linewidth=2.5,
                        color='black')
ax.add_patch(arrow1)

# Priors back-arrow (dotted)
arrow2 = FancyArrowPatch((combo_x - 5, combo_y + 1),
                        (mech_x + mech_width/2, mech_y - mech_height + 1),
                        arrowstyle='<-', mutation_scale=15, linewidth=1.5,
                        color='black', linestyle='dotted')
ax.add_patch(arrow2)
ax.text(combo_x - 10, combo_y + 3, 'priors', ha='center', va='bottom',
        fontsize=TICK_SIZE - 2, fontstyle='italic', fontfamily='sans-serif')

# Posterior arrow forward
arrow3 = FancyArrowPatch((combo_x + 2, combo_y),
                        (70, combo_y),
                        arrowstyle='->', mutation_scale=20, linewidth=2.5,
                        color='black')
ax.add_patch(arrow3)
ax.text(combo_x + 10, combo_y + 2, 'posterior\n(with data)', ha='center', va='bottom',
        fontsize=TICK_SIZE - 2, fontfamily='sans-serif')

# === (E) Outputs column (right) ===
outputs_x = 72
outputs_y = 70
outputs_width = 18
outputs_height = 35

# Output box
output_box = FancyBboxPatch((outputs_x, outputs_y - outputs_height), outputs_width, outputs_height,
                           boxstyle="round,pad=0.3", edgecolor='black', facecolor='white',
                           linewidth=2)
ax.add_patch(output_box)

ax.text(outputs_x + outputs_width/2, outputs_y - 2, 'Predicted/Measured\nOutputs',
        ha='center', va='top', fontsize=LABEL_SIZE, fontweight='bold',
        fontfamily='sans-serif')

# Output items
output_items = [
    r'TL($\omega$) curve',
    r'Coherence $\gamma^2(\omega)$',
    r'PSD($\omega$) width'
]

y_pos = outputs_y - 10
for item in output_items:
    # Bullet
    circle = Circle((outputs_x + 1.5, y_pos), 0.3, color='black')
    ax.add_patch(circle)
    # Text
    ax.text(outputs_x + 3, y_pos, item, ha='left', va='center',
            fontsize=NOTE_SIZE - 2, fontfamily='sans-serif')
    y_pos -= 6

# Design implications note
ax.text(outputs_x + outputs_width/2, outputs_y - outputs_height + 7,
        'Design implications:\nChoose $\\omega$, $\\theta$, $Ri$, $k\\delta$\nto target mechanisms;\nupdate priors with data.',
        ha='center', va='bottom', fontsize=TICK_SIZE - 1, fontstyle='italic',
        bbox=dict(boxstyle='round', facecolor='#FEF3C7', alpha=0.3),
        fontfamily='sans-serif')

# === Legend (bottom-right) ===
legend_x = 70
legend_y = 15

legend_items = [
    ('Classical', CLASSICAL_COLOR),
    ('Mode conversion', CONVERSION_COLOR),
    ('Interfacial', INTERFACIAL_COLOR),
    ('Shear-mediated', SHEAR_COLOR)
]

ax.text(legend_x, legend_y + 3, 'Mechanisms:', ha='left', va='bottom',
        fontsize=LEGEND_SIZE, fontweight='bold', fontfamily='sans-serif')

y_pos = legend_y
for label, color in legend_items:
    rect = mpatches.Rectangle((legend_x, y_pos - 0.5), 2, 1.2,
                              facecolor=color, edgecolor='black', linewidth=0.5)
    ax.add_patch(rect)
    ax.text(legend_x + 3, y_pos, label, ha='left', va='center',
            fontsize=LEGEND_SIZE - 2, fontfamily='sans-serif')
    y_pos -= 2.5

# === Caption ===
caption = ('Figure 3.7A. Composite attenuation concept. Similarity variables feed a mechanism-weighting '
          'module that yields shares summing to unity; these combine into a composite prediction of '
          'attenuation and observables used to set priors and design experiments.')

ax.text(50, 5, caption, ha='center', va='bottom',
        fontsize=CAPTION_SIZE, fontstyle='italic', fontfamily='sans-serif',
        wrap=True)

# Save
plt.savefig('/workspace/figure_3_7A.png', dpi=DPI, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print("Figure 3.7A saved to /workspace/figure_3_7A.png")
plt.close()
