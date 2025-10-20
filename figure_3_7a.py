import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

# Set up the figure with exact specifications
fig, ax = plt.subplots(figsize=(20, 14))  # 2000x1400 px at 100 DPI
ax.set_xlim(0, 20)
ax.set_ylim(0, 14)
ax.axis('off')

# Color scheme
colors = {
    'classical': '#6B7280',
    'conversion': '#F4A261', 
    'interfacial': '#6A4C93',
    'shear': '#2A9D8F',
    'amber_band': '#F4A261',
    'dotted_line': '#9CA3AF'
}

# Font settings
title_font = {'fontsize': 28, 'fontweight': 'bold', 'fontfamily': 'sans-serif'}
label_font = {'fontsize': 22, 'fontfamily': 'sans-serif'}
tick_font = {'fontsize': 16, 'fontfamily': 'sans-serif'}
note_font = {'fontsize': 18, 'fontfamily': 'sans-serif'}
caption_font = {'fontsize': 15, 'style': 'italic', 'fontfamily': 'sans-serif'}

# Main title
ax.text(10, 13.5, 'Figure 3.7A — Composite attenuation concept', 
        ha='center', va='center', **title_font)

# (A) Inputs column (left, ~300 px wide)
inputs_box = FancyBboxPatch((0.5, 8), 3, 4, 
                           boxstyle="round,pad=0.1", 
                           facecolor='white', edgecolor='black', linewidth=2)
ax.add_patch(inputs_box)
ax.text(2, 11.8, 'Inputs', ha='center', va='center', **label_font)

# Input items with bullet points
input_items = [
    'ω/N (frequency ratio)',
    'Ri (stability)', 
    'kδ (interface optical thickness)',
    'CZ, At (impedance/Atwood)',
    'θ, r (incidence, range)'
]

y_positions = [11.2, 10.8, 10.4, 10.0, 9.6]
for i, (item, y) in enumerate(zip(input_items, y_positions)):
    # Bullet point
    ax.plot(0.8, y, 'o', markersize=4, color='black')
    # Text
    ax.text(1.0, y, item, va='center', **tick_font)

# Add "contrast" tag for CZ, At
ax.text(3.2, 10.0, 'contrast', ha='center', va='center', 
        fontsize=12, style='italic', color='gray')

# (B) Similarity space cue (center-top, ~520×320 px)
similarity_box = FancyBboxPatch((4.5, 9.5), 5.2, 3.2, 
                               boxstyle="round,pad=0.1",
                               facecolor='white', edgecolor='black', linewidth=1.5)
ax.add_patch(similarity_box)

# Similarity space axes
ax.plot([5, 9.5], [10.5, 10.5], 'k-', linewidth=1)  # x-axis
ax.plot([5, 5], [10.5, 12.5], 'k-', linewidth=1)    # y-axis

# Axis labels
ax.text(7.25, 10.2, 'ω/N', ha='center', va='center', **tick_font)
ax.text(4.7, 11.5, 'Ri', ha='center', va='center', **tick_font, rotation=90)

# Axis ticks
ax.plot([5, 5], [10.4, 10.6], 'k-', linewidth=1)  # y=0
ax.plot([9.5, 9.5], [10.4, 10.6], 'k-', linewidth=1)  # y=2
ax.plot([4.8, 5.2], [10.5, 10.5], 'k-', linewidth=1)  # x=0.2
ax.plot([4.8, 5.2], [12.5, 12.5], 'k-', linewidth=1)  # x=2.2

# Soft regions
conversion_region = patches.Ellipse((7.25, 11.5), 2.5, 1.2, 
                                   facecolor=colors['conversion'], alpha=0.3)
ax.add_patch(conversion_region)
ax.text(7.25, 11.5, 'conversion\nbelt', ha='center', va='center', 
        fontsize=12, style='italic')

shear_region = patches.Ellipse((6, 12.2), 1.5, 0.6, 
                              facecolor=colors['shear'], alpha=0.3)
ax.add_patch(shear_region)
ax.text(6, 12.2, 'shear-\nfavored', ha='center', va='center', 
        fontsize=10, style='italic')

classical_region = patches.Ellipse((8.5, 10.8), 1.5, 0.6, 
                                  facecolor=colors['classical'], alpha=0.3)
ax.add_patch(classical_region)
ax.text(8.5, 10.8, 'near-\nclassical', ha='center', va='center', 
        fontsize=10, style='italic')

# (C) Mechanism weighting module (center-middle, ~560×260 px)
weighting_box = FancyBboxPatch((4.2, 6.5), 5.6, 2.6, 
                              boxstyle="round,pad=0.15",
                              facecolor='white', edgecolor='black', linewidth=2)
ax.add_patch(weighting_box)
ax.text(7, 8.8, 'Mechanism weighting (shares sum to 1)', 
        ha='center', va='center', **label_font)

# Stacked horizontal bar
bar_y = 7.8
bar_width = 4.5
bar_height = 0.4

# Mechanism shares (example values)
shares = [0.35, 0.45, 0.05, 0.15]  # classical, conversion, interfacial, shear
mechanisms = ['Classical', 'Mode conversion', 'Interfacial', 'Shear-mediated']
mechanism_colors = [colors['classical'], colors['conversion'], 
                   colors['interfacial'], colors['shear']]

x_start = 5.2
x_pos = x_start
for i, (share, color, name) in enumerate(zip(shares, mechanism_colors, mechanisms)):
    width = share * bar_width
    rect = patches.Rectangle((x_pos, bar_y), width, bar_height, 
                           facecolor=color, edgecolor='black', linewidth=1)
    ax.add_patch(rect)
    
    # Label above the bar
    ax.text(x_pos + width/2, bar_y + 0.6, name, ha='center', va='center', 
            fontsize=14, fontweight='bold')
    
    x_pos += width

# Sum annotation
ax.text(9.8, 7.8, '∑wi = 1', ha='center', va='center', 
        fontsize=14, style='italic')

# Guidance text
ax.text(7, 7.2, 'shares guided by §3.2 similarity & §3.4–3.6 scalings', 
        ha='center', va='center', fontsize=12, style='italic')

# (D) Combination node (center-bottom)
sigma_x, sigma_y = 7, 5.5
sigma_circle = patches.Circle((sigma_x, sigma_y), 0.8, 
                            facecolor='white', edgecolor='black', linewidth=2)
ax.add_patch(sigma_circle)
ax.text(sigma_x, sigma_y, 'Σ', ha='center', va='center', 
        fontsize=24, fontweight='bold')
ax.text(sigma_x, sigma_y - 1.2, 'Composite\nattenuation', ha='center', va='center', 
        fontsize=14, fontweight='bold')

# Arrow from weighting to sigma
arrow1 = ConnectionPatch((7, 6.5), (sigma_x, sigma_y + 0.8), 
                        "data", "data", arrowstyle="->", 
                        shrinkA=5, shrinkB=5, mutation_scale=20, 
                        fc="black", linewidth=2)
ax.add_patch(arrow1)

# Priors back-arrow (dotted)
arrow2 = ConnectionPatch((sigma_x - 0.8, sigma_y), (6.2, 6.5), 
                        "data", "data", arrowstyle="->", 
                        shrinkA=5, shrinkB=5, mutation_scale=15, 
                        fc="black", linewidth=1.5, linestyle='--')
ax.add_patch(arrow2)
ax.text(6.5, 5.8, 'priors', ha='center', va='center', 
        fontsize=12, style='italic')

# Posterior arrow (solid)
arrow3 = ConnectionPatch((sigma_x + 0.8, sigma_y), (11.2, 5.5), 
                        "data", "data", arrowstyle="->", 
                        shrinkA=5, shrinkB=5, mutation_scale=20, 
                        fc="black", linewidth=2)
ax.add_patch(arrow3)
ax.text(9.5, 5.2, 'posterior (with data)', ha='center', va='center', 
        fontsize=12, style='italic')

# (E) Outputs column (right, ~360 px wide)
outputs_box = FancyBboxPatch((11.5, 6), 3.6, 4, 
                            boxstyle="round,pad=0.1", 
                            facecolor='white', edgecolor='black', linewidth=2)
ax.add_patch(outputs_box)
ax.text(13.3, 9.8, 'Predicted / measured outputs', ha='center', va='center', **label_font)

# Output icons
# TL(ω) curve
omega_vals = np.linspace(0.2, 2.2, 50)
tl_vals = 20 * np.exp(-(omega_vals - 1)**2) + 5
tl_x = 12 + (omega_vals - 0.2) / 2 * 1.5
tl_y = 9.2 + tl_vals / 100
ax.plot(tl_x, tl_y, 'k-', linewidth=2)
ax.text(13.3, 9.0, 'TL(ω)', ha='center', va='center', fontsize=12)

# Coherence γ²(ω) 
coh_vals = 1 - 0.8 * np.exp(-(omega_vals - 1)**2 / 0.1)
coh_x = 12 + (omega_vals - 0.2) / 2 * 1.5
coh_y = 8.2 + coh_vals * 0.3
ax.plot(coh_x, coh_y, 'k-', linewidth=2)
ax.text(13.3, 7.8, 'γ²(ω)', ha='center', va='center', fontsize=12)

# PSD(ω) width
psd_narrow = 0.1 * np.exp(-(omega_vals - 1)**2 / 0.05) + 0.05
psd_broad = 0.3 * np.exp(-(omega_vals - 1)**2 / 0.2) + 0.1
psd_x = 12 + (omega_vals - 0.2) / 2 * 1.5
ax.plot(psd_x, 7.2 + psd_narrow, 'k-', linewidth=2)
ax.plot(psd_x, 6.8 + psd_broad, 'k-', linewidth=2)
ax.text(13.3, 6.6, 'PSD(ω)', ha='center', va='center', fontsize=12)

# Design implications
ax.text(13.3, 5.8, 'Design implications:', ha='center', va='center', 
        fontsize=12, fontweight='bold')
ax.text(13.3, 5.4, 'Choose ω, θ, Ri, kδ to target\nmechanisms; update priors with data.', 
        ha='center', va='center', fontsize=10, style='italic')

# Legend (bottom-right)
legend_x = 15
legend_y = 3.5
legend_items = ['Classical', 'Mode conversion', 'Interfacial', 'Shear-mediated']
legend_colors = [colors['classical'], colors['conversion'], 
                colors['interfacial'], colors['shear']]

for i, (item, color) in enumerate(zip(legend_items, legend_colors)):
    y_pos = legend_y - i * 0.4
    rect = patches.Rectangle((legend_x, y_pos - 0.1), 0.3, 0.2, 
                           facecolor=color, edgecolor='black', linewidth=1)
    ax.add_patch(rect)
    ax.text(legend_x + 0.4, y_pos, item, va='center', fontsize=14)

# Caption
caption_text = ("Figure 3.7A. Composite attenuation concept. Similarity variables feed a "
                "mechanism-weighting module that yields shares summing to unity; these combine "
                "into a composite prediction of attenuation and observables used to set priors "
                "and design experiments.")
ax.text(10, 1.5, caption_text, ha='center', va='center', **caption_font, 
        bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8))

# Input arrows to central module
for y in y_positions:
    arrow = ConnectionPatch((3.5, y), (4.2, 7.8), 
                          "data", "data", arrowstyle="->", 
                          shrinkA=5, shrinkB=5, mutation_scale=15, 
                          fc="black", linewidth=1.5)
    ax.add_patch(arrow)

plt.tight_layout()
plt.savefig('figure_3_7a.png', dpi=100, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.savefig('figure_3_7a.pdf', bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.show()