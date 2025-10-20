#!/usr/bin/env python3
"""
Figure 3.7A - Composite attenuation concept block diagram
A flow diagram showing inputs → mechanism weighting → composite attenuation → outputs
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
from matplotlib.patches import ConnectionPatch
import numpy as np

# Set up the figure
fig, ax = plt.subplots(figsize=(20, 14), dpi=100)
ax.set_xlim(0, 2000)
ax.set_ylim(0, 1400)
ax.axis('off')
ax.set_facecolor('white')
fig.patch.set_facecolor('white')

# Define colors
colors = {
    'classical': '#6B7280',
    'conversion': '#F4A261',
    'interfacial': '#6A4C93',
    'shear': '#2A9D8F',
    'text': '#000000',
    'light_grey': '#E5E7EB',
    'amber_trans': '#F4A261',
    'dotted': '#9CA3AF'
}

# Title
ax.text(1000, 1350, 'Figure 3.7A — Composite attenuation concept', 
        fontsize=28, fontweight='bold', ha='center', va='top')

# (A) Inputs column - left side
input_box_x, input_box_y = 100, 500
input_box_w, input_box_h = 300, 400

# Draw inputs box
inputs_rect = FancyBboxPatch((input_box_x, input_box_y), input_box_w, input_box_h,
                             boxstyle="round,pad=10", 
                             edgecolor='black', facecolor='#F8F9FA', linewidth=2)
ax.add_patch(inputs_rect)

# Inputs title
ax.text(input_box_x + input_box_w/2, input_box_y + input_box_h - 30, 'Inputs',
        fontsize=24, fontweight='bold', ha='center', va='center')

# Input items with bullets
input_items = [
    ('ω/N', 'frequency ratio'),
    ('Ri', 'stability'),
    ('kδ', 'interface optical thickness'),
    ('C_Z, A_t', 'contrast'),
    ('θ, r', 'geometry')
]

y_pos = input_box_y + input_box_h - 100
for symbol, desc in input_items:
    # Bullet
    circle = plt.Circle((input_box_x + 40, y_pos), 6, color=colors['classical'])
    ax.add_patch(circle)
    
    # Symbol text (using italic for mathematical notation)
    ax.text(input_box_x + 70, y_pos, symbol, fontsize=20, 
            fontstyle='italic', va='center')
    
    # Description in smaller text
    ax.text(input_box_x + 150, y_pos, f'({desc})', fontsize=14, 
            color='#6B7280', va='center')
    
    y_pos -= 60

# (B) Similarity space thumbnail - center-top
sim_space_x, sim_space_y = 740, 950
sim_space_w, sim_space_h = 520, 320

# Draw similarity space axes
ax.add_patch(Rectangle((sim_space_x, sim_space_y), sim_space_w, sim_space_h,
                       edgecolor='black', facecolor='white', linewidth=1.5))

# Add grid lines
for x in np.linspace(sim_space_x, sim_space_x + sim_space_w, 6):
    ax.plot([x, x], [sim_space_y, sim_space_y + sim_space_h], 
            color=colors['light_grey'], linewidth=0.8)

for y in np.linspace(sim_space_y, sim_space_y + sim_space_h, 5):
    ax.plot([sim_space_x, sim_space_x + sim_space_w], [y, y],
            color=colors['light_grey'], linewidth=0.8)

# Similarity space labels
ax.text(sim_space_x + sim_space_w/2, sim_space_y - 25, 'ω/N', 
        fontsize=18, fontstyle='italic', ha='center')
ax.text(sim_space_x - 25, sim_space_y + sim_space_h/2, 'Ri', 
        fontsize=18, fontstyle='italic', ha='center', rotation=90)

# Add x-axis ticks
x_ticks = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0, 2.2]
for i, tick in enumerate(x_ticks):
    x_pos = sim_space_x + (tick - 0.2) * sim_space_w / 2.0
    ax.text(x_pos, sim_space_y - 10, str(tick), fontsize=14, ha='center')

# Add y-axis ticks
y_ticks = [0, 0.5, 1.0, 1.5, 2.0]
for tick in y_ticks:
    y_pos = sim_space_y + tick * sim_space_h / 2.0
    ax.text(sim_space_x - 10, y_pos, str(tick), fontsize=14, ha='right', va='center')

# Add colored regions with low opacity
# Conversion belt (0.8 ≤ ω/N ≤ 1.2)
conv_x = sim_space_x + 0.6 * sim_space_w / 2.0
conv_w = 0.4 * sim_space_w / 2.0
ax.add_patch(Rectangle((conv_x, sim_space_y), conv_w, sim_space_h,
                       facecolor=colors['conversion'], alpha=0.2))
ax.text(conv_x + conv_w/2, sim_space_y + sim_space_h - 40, 'conversion\nbelt',
        fontsize=14, ha='center', va='center')

# Shear-favored region
shear_region = patches.Ellipse((sim_space_x + 0.3*sim_space_w, sim_space_y + 0.3*sim_space_h),
                               150, 100, angle=30, facecolor=colors['shear'], alpha=0.15)
ax.add_patch(shear_region)
ax.text(sim_space_x + 0.25*sim_space_w, sim_space_y + 0.25*sim_space_h, 
        'shear-\nfavored', fontsize=14, ha='center')

# Near-classical region
classical_region = patches.Ellipse((sim_space_x + 0.8*sim_space_w, sim_space_y + 0.7*sim_space_h),
                                   180, 120, angle=-20, facecolor=colors['classical'], alpha=0.1)
ax.add_patch(classical_region)
ax.text(sim_space_x + 0.75*sim_space_w, sim_space_y + 0.65*sim_space_h, 
        'near-\nclassical', fontsize=14, ha='center')

# (C) Mechanism weighting module - center-middle
module_x, module_y = 720, 570
module_w, module_h = 560, 260

# Draw module box
module_rect = FancyBboxPatch((module_x, module_y), module_w, module_h,
                             boxstyle="round,pad=10",
                             edgecolor='black', facecolor='#F8F9FA', linewidth=2)
ax.add_patch(module_rect)

# Module title
ax.text(module_x + module_w/2, module_y + module_h - 35, 
        'Mechanism weighting (shares sum to 1)',
        fontsize=22, fontweight='bold', ha='center')

# Draw stacked horizontal bar
bar_x, bar_y = module_x + 50, module_y + 100
bar_w, bar_h = module_w - 100, 60

# Mechanism shares (example distribution)
shares = [0.35, 0.40, 0.10, 0.15]  # Classical, Conversion, Interfacial, Shear
mech_colors = [colors['classical'], colors['conversion'], colors['interfacial'], colors['shear']]
mech_names = ['Classical', 'Mode conversion', 'Interfacial', 'Shear-mediated']

x_offset = 0
for i, (share, color, name) in enumerate(zip(shares, mech_colors, mech_names)):
    segment_width = share * bar_w
    ax.add_patch(Rectangle((bar_x + x_offset, bar_y), segment_width, bar_h,
                           facecolor=color, edgecolor='black', linewidth=1))
    
    # Add label if segment is wide enough
    if segment_width > 60:
        ax.text(bar_x + x_offset + segment_width/2, bar_y + bar_h/2, name,
                fontsize=14, ha='center', va='center', color='white' if i != 0 else 'black')
    
    x_offset += segment_width

# Sum notation
ax.text(bar_x + bar_w + 20, bar_y + bar_h/2, 'Σwᵢ = 1', 
        fontsize=16, fontstyle='italic', va='center')

# Note below
ax.text(module_x + module_w/2, module_y + 40,
        'shares guided by §3.2 similarity & §3.4–3.6 scalings',
        fontsize=13, ha='center', fontstyle='italic', color='#6B7280')

# Draw arrows from inputs to module
for i in range(5):
    y_start = input_box_y + input_box_h - 100 - i * 60
    arrow = FancyArrowPatch((input_box_x + input_box_w, y_start),
                           (module_x - 10, module_y + module_h/2),
                           arrowstyle='->', linewidth=1.5, color='black',
                           connectionstyle="arc3,rad=0.2")
    ax.add_patch(arrow)

# Arrow from similarity space to module
arrow = FancyArrowPatch((sim_space_x + sim_space_w/2, sim_space_y),
                       (module_x + module_w/2, module_y + module_h),
                       arrowstyle='->', linewidth=1.5, color='black',
                       connectionstyle="arc3,rad=-0.1")
ax.add_patch(arrow)

# (D) Combination node - center-bottom
sigma_x, sigma_y = 950, 380
sigma_size = 80

# Draw Sigma symbol
ax.text(sigma_x, sigma_y, 'Σ', fontsize=60, ha='center', va='center',
        fontweight='bold')
ax.text(sigma_x, sigma_y - 60, 'Composite attenuation', 
        fontsize=18, ha='center', va='center')

# Arrow from module to sigma
arrow = FancyArrowPatch((module_x + module_w/2, module_y),
                       (sigma_x, sigma_y + 40),
                       arrowstyle='->', linewidth=2, color='black')
ax.add_patch(arrow)

# Priors dotted back-arrow
arrow = FancyArrowPatch((sigma_x - 50, sigma_y),
                       (module_x + module_w/2 - 100, module_y - 10),
                       arrowstyle='->', linewidth=1.2, color=colors['dotted'],
                       linestyle='dotted', connectionstyle="arc3,rad=0.3")
ax.add_patch(arrow)
ax.text(sigma_x - 150, sigma_y - 50, 'priors', fontsize=14, 
        fontstyle='italic', color=colors['dotted'])

# Posterior arrow forward
arrow = FancyArrowPatch((sigma_x + 50, sigma_y),
                       (1450, sigma_y),
                       arrowstyle='->', linewidth=2, color='black')
ax.add_patch(arrow)
ax.text(sigma_x + 150, sigma_y - 30, 'posterior\n(with data)', 
        fontsize=14, ha='center')

# (E) Outputs column - right side
output_box_x, output_box_y = 1500, 500
output_box_w, output_box_h = 360, 400

# Draw outputs box
outputs_rect = FancyBboxPatch((output_box_x, output_box_y), output_box_w, output_box_h,
                              boxstyle="round,pad=10",
                              edgecolor='black', facecolor='#F8F9FA', linewidth=2)
ax.add_patch(outputs_rect)

# Outputs title
ax.text(output_box_x + output_box_w/2, output_box_y + output_box_h - 30,
        'Predicted / Measured outputs',
        fontsize=22, fontweight='bold', ha='center')

# Output items with icons
output_y = output_box_y + output_box_h - 120

# TL(ω) curve
x_icon = np.linspace(output_box_x + 40, output_box_x + 120, 50)
y_icon = output_y + 20 * np.exp(-0.05*(x_icon - output_box_x - 80)**2)
ax.plot(x_icon, y_icon, color='black', linewidth=2)
ax.text(output_box_x + 140, output_y, 'TL(ω)', fontsize=18, 
        fontstyle='italic', va='center')

# Coherence γ²(ω)
output_y -= 80
x_icon = np.linspace(output_box_x + 40, output_box_x + 120, 50)
y_icon = output_y + 15 * (1 - 0.4 * np.exp(-0.1*(x_icon - output_box_x - 80)**2))
ax.plot(x_icon, y_icon, color='black', linewidth=2)
ax.text(output_box_x + 140, output_y, 'Coherence γ²(ω)', fontsize=18,
        fontstyle='italic', va='center')

# PSD(ω) width
output_y -= 80
x_icon = np.linspace(output_box_x + 40, output_box_x + 120, 50)
y_icon1 = output_y + 20 * np.exp(-0.2*(x_icon - output_box_x - 70)**2)
y_icon2 = output_y + 20 * np.exp(-0.05*(x_icon - output_box_x - 70)**2)
ax.plot(x_icon, y_icon1, color='black', linewidth=2)
ax.plot(x_icon, y_icon2, color='black', linewidth=2, linestyle='--')
ax.text(output_box_x + 140, output_y, 'PSD(ω) width', fontsize=18,
        fontstyle='italic', va='center')

# Design implications note
ax.text(output_box_x + output_box_w/2, output_box_y - 50,
        'Design implications:\nChoose ω, θ, Ri, kδ to target mechanisms;\nupdate priors with data.',
        fontsize=15, ha='center', va='top', fontstyle='italic', color='#6B7280')

# Legend - bottom-right
legend_x, legend_y = 1500, 200
legend_items = [
    ('Classical', colors['classical']),
    ('Mode conversion', colors['conversion']),
    ('Interfacial', colors['interfacial']),
    ('Shear-mediated', colors['shear'])
]

ax.text(legend_x, legend_y + 40, 'Legend:', fontsize=16, fontweight='bold')
for i, (name, color) in enumerate(legend_items):
    y_pos = legend_y - i * 30
    ax.add_patch(Rectangle((legend_x, y_pos), 30, 20, facecolor=color))
    ax.text(legend_x + 40, y_pos + 10, name, fontsize=16, va='center')

# Caption
ax.text(1000, 100, 
        'Figure 3.7A. Composite attenuation concept. Similarity variables feed a mechanism-weighting module that yields shares\nsumming to unity; these combine into a composite prediction of attenuation and observables used to set priors and design experiments.',
        fontsize=15, ha='center', va='center', fontstyle='italic')

plt.tight_layout()
plt.savefig('figure_3_7a.png', dpi=100, bbox_inches='tight', facecolor='white')
plt.savefig('figure_3_7a.pdf', dpi=100, bbox_inches='tight', facecolor='white')
plt.show()