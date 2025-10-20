"""
Figure 3.7A - Composite attenuation concept (block diagram)
Publication-grade vector graphics
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np

# Style settings
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial']
plt.rcParams['mathtext.fontset'] = 'custom'
plt.rcParams['mathtext.rm'] = 'Arial'
plt.rcParams['mathtext.it'] = 'Arial:italic'
plt.rcParams['mathtext.bf'] = 'Arial:bold'

# Create figure
fig = plt.figure(figsize=(20, 14), dpi=100, facecolor='white')
ax = fig.add_subplot(111)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Color scheme
colors = {
    'classical': '#6B7280',
    'conversion': '#F4A261',
    'interfacial': '#6A4C93',
    'shear': '#2A9D8F',
    'grid': '#E5E7EB',
    'conversion_light': '#F4A261',
    'dotted_line': '#9CA3AF'
}

# (A) Inputs column (left)
input_x = 8
input_y = 45
box_width = 18
box_height = 35

# Input box
input_box = FancyBboxPatch((input_x, input_y), box_width, box_height,
                           boxstyle="round,pad=0.3", 
                           edgecolor='black', facecolor='white', linewidth=2)
ax.add_patch(input_box)

ax.text(input_x + box_width/2, input_y + box_height - 3, 'Inputs',
        fontsize=22, fontweight='bold', ha='center', va='top')

# Input items
inputs = [
    r'$\omega/N$ (frequency ratio)',
    r'$Ri$ (stability)',
    r'$k\delta$ (interface thickness)',
    r'$C_Z, A_t$ (contrast)',
    r'Geometry: $\theta, r$'
]

y_start = input_y + box_height - 8
for i, inp in enumerate(inputs):
    y_pos = y_start - i * 5.5
    # Bullet
    circle = plt.Circle((input_x + 1.5, y_pos), 0.3, color='black', zorder=10)
    ax.add_patch(circle)
    # Text
    ax.text(input_x + 3, y_pos, inp, fontsize=16, va='center', ha='left')
    
    # Arrow to center
    arrow = FancyArrowPatch((input_x + box_width, y_pos),
                           (38, 55 if i < 3 else 50),
                           arrowstyle='->', mutation_scale=15, 
                           linewidth=1.5, color='black', alpha=0.6)
    ax.add_patch(arrow)

# (B) Similarity space cue (center-top)
sim_x, sim_y = 40, 65
sim_w, sim_h = 26, 16

# Thumbnail axes
sim_box = Rectangle((sim_x, sim_y), sim_w, sim_h, 
                     edgecolor='black', facecolor='white', linewidth=1.5)
ax.add_patch(sim_box)

ax.text(sim_x + sim_w/2, sim_y + sim_h + 1.5, 'Similarity space',
        fontsize=18, ha='center', va='bottom', fontweight='bold')

# Axes labels
ax.text(sim_x + sim_w/2, sim_y - 1, r'$\omega/N$', fontsize=14, ha='center', va='top')
ax.text(sim_x - 1, sim_y + sim_h/2, r'$Ri$', fontsize=14, ha='right', va='center', rotation=90)

# Soft regions
conv_belt = Rectangle((sim_x + sim_w*0.3, sim_y + sim_h*0.3), sim_w*0.3, sim_h*0.4,
                       facecolor=colors['conversion'], alpha=0.2, edgecolor='none')
ax.add_patch(conv_belt)
ax.text(sim_x + sim_w*0.45, sim_y + sim_h*0.5, 'conversion\nbelt',
        fontsize=11, ha='center', va='center', style='italic')

shear_region = Rectangle((sim_x + sim_w*0.25, sim_y + sim_h*0.05), sim_w*0.35, sim_h*0.2,
                         facecolor=colors['shear'], alpha=0.2, edgecolor='none')
ax.add_patch(shear_region)
ax.text(sim_x + sim_w*0.42, sim_y + sim_h*0.15, 'shear-\nfavored',
        fontsize=10, ha='center', va='center', style='italic')

# (C) Mechanism weighting module (center-middle)
module_x, module_y = 35, 35
module_w, module_h = 32, 20

module_box = FancyBboxPatch((module_x, module_y), module_w, module_h,
                           boxstyle="round,pad=0.5", 
                           edgecolor='black', facecolor='#F9FAFB', linewidth=2.5)
ax.add_patch(module_box)

ax.text(module_x + module_w/2, module_y + module_h - 2, 
        'Mechanism weighting',
        fontsize=20, fontweight='bold', ha='center', va='top')
ax.text(module_x + module_w/2, module_y + module_h - 4.5, 
        '(shares sum to 1)',
        fontsize=16, ha='center', va='top', style='italic')

# Stacked bar
bar_y = module_y + 8
bar_h = 3
bar_x_start = module_x + 3
bar_width = module_w - 6

# Shares (example distribution)
shares = [0.35, 0.40, 0.15, 0.10]  # classical, conversion, interfacial, shear
colors_list = [colors['classical'], colors['conversion'], colors['interfacial'], colors['shear']]
labels = ['Classical', 'Mode\nconversion', 'Interfacial', 'Shear-\nmediated']

x_offset = bar_x_start
for i, (share, color, label) in enumerate(zip(shares, colors_list, labels)):
    width = share * bar_width
    rect = Rectangle((x_offset, bar_y), width, bar_h, 
                     facecolor=color, edgecolor='black', linewidth=1)
    ax.add_patch(rect)
    # Label
    if width > 3:
        ax.text(x_offset + width/2, bar_y + bar_h/2, label,
                fontsize=13, ha='center', va='center', color='white', fontweight='bold')
    x_offset += width

# Sum annotation
ax.text(module_x + module_w + 2, bar_y + bar_h/2, r'$\sum w_i = 1$',
        fontsize=16, ha='left', va='center', style='italic')

# Guidance note
ax.text(module_x + module_w/2, module_y + 2.5,
        'shares guided by §3.2 similarity & §3.4–3.6 scalings',
        fontsize=13, ha='center', va='bottom', style='italic', color='#4B5563')

# (D) Combination node (center-bottom)
sigma_x, sigma_y = 51, 22

# Sigma symbol
ax.text(sigma_x, sigma_y, r'$\Sigma$', fontsize=48, ha='center', va='center', 
        fontweight='bold', color='#1F2937')
ax.text(sigma_x, sigma_y - 4, 'Composite\nattenuation',
        fontsize=16, ha='center', va='top', fontweight='bold')

# Arrow from module to sigma
arrow1 = FancyArrowPatch((module_x + module_w/2, module_y),
                        (sigma_x, sigma_y + 4),
                        arrowstyle='->', mutation_scale=20, 
                        linewidth=2.5, color='black')
ax.add_patch(arrow1)

# Priors arrow (dotted back)
arrow_prior = FancyArrowPatch((sigma_x - 5, sigma_y + 2),
                             (module_x + module_w/2, module_y + 3),
                             arrowstyle='->', mutation_scale=15, 
                             linewidth=1.5, color='black', linestyle='dotted', alpha=0.7)
ax.add_patch(arrow_prior)
ax.text(module_x + module_w/2 - 5, module_y - 1, 'priors',
        fontsize=14, ha='center', va='top', style='italic', color='#6B7280')

# (E) Outputs column (right)
output_x = 72
output_y = 40
output_w = 20
output_h = 30

output_box = FancyBboxPatch((output_x, output_y), output_w, output_h,
                           boxstyle="round,pad=0.3", 
                           edgecolor='black', facecolor='white', linewidth=2)
ax.add_patch(output_box)

ax.text(output_x + output_w/2, output_y + output_h - 2, 
        'Predicted/Measured\nOutputs',
        fontsize=20, fontweight='bold', ha='center', va='top')

# Output icons
outputs = [
    r'TL($\omega$) curve',
    r'Coherence $\gamma^2(\omega)$',
    r'PSD($\omega$) width'
]

y_out = output_y + output_h - 8
for i, out in enumerate(outputs):
    y_pos = y_out - i * 6
    # Mini icon (simple line)
    x_icon = output_x + 2
    if i == 0:  # TL curve
        ax.plot([x_icon, x_icon+3], [y_pos, y_pos-0.5], 'k-', linewidth=2)
    elif i == 1:  # Coherence with dip
        x_pts = np.linspace(0, 3, 20)
        y_pts = y_pos - 0.5 * np.exp(-((x_pts-1.5)**2)/0.3)
        ax.plot(x_icon + x_pts, y_pts, 'k-', linewidth=2)
    else:  # PSD
        ax.plot([x_icon, x_icon+1.5, x_icon+3], [y_pos-0.3, y_pos, y_pos-0.3], 'k-', linewidth=2)
    
    ax.text(x_icon + 4, y_pos - 0.25, out, fontsize=16, va='center', ha='left')

# Arrow from sigma to outputs
arrow2 = FancyArrowPatch((sigma_x + 3, sigma_y),
                        (output_x, output_y + output_h/2),
                        arrowstyle='->', mutation_scale=20, 
                        linewidth=2.5, color='black')
ax.add_patch(arrow2)
ax.text(sigma_x + 6, sigma_y + 1, 'posterior\n(with data)',
        fontsize=14, ha='left', va='bottom', style='italic', color='#6B7280')

# Design implications note
design_box = FancyBboxPatch((output_x, output_y - 8), output_w, 6,
                           boxstyle="round,pad=0.2", 
                           edgecolor='#6B7280', facecolor='#F3F4F6', 
                           linewidth=1.5, linestyle='dashed')
ax.add_patch(design_box)
ax.text(output_x + output_w/2, output_y - 5, 
        r'Design implications:\nChoose $\omega, \theta, Ri, k\delta$ to\ntarget mechanisms;\nupdate priors with data.',
        fontsize=13, ha='center', va='center', style='italic')

# Legend (bottom-right)
legend_x = 70
legend_y = 8
ax.text(legend_x, legend_y + 10, 'Mechanisms:', fontsize=18, fontweight='bold', ha='left', va='bottom')

legend_items = [
    ('Classical', colors['classical']),
    ('Mode conversion', colors['conversion']),
    ('Interfacial', colors['interfacial']),
    ('Shear-mediated', colors['shear'])
]

for i, (label, color) in enumerate(legend_items):
    y_pos = legend_y + 8 - i * 2.5
    rect = Rectangle((legend_x, y_pos - 0.6), 2, 1.2, facecolor=color, edgecolor='black', linewidth=1)
    ax.add_patch(rect)
    ax.text(legend_x + 2.5, y_pos, label, fontsize=16, va='center', ha='left')

# Caption
caption_text = ("Figure 3.7A. Composite attenuation concept. Similarity variables feed a mechanism-weighting "
                "module that yields shares summing to unity; these combine into a composite prediction of "
                "attenuation and observables used to set priors and design experiments.")
ax.text(50, 2, caption_text, fontsize=15, ha='center', va='bottom', 
        style='italic', wrap=True, color='#1F2937')

plt.tight_layout()
plt.savefig('figure_3_7A.svg', format='svg', dpi=100, bbox_inches='tight', facecolor='white')
plt.savefig('figure_3_7A.png', format='png', dpi=100, bbox_inches='tight', facecolor='white')
print("Figure 3.7A saved as SVG and PNG")
plt.close()
