"""
Figure 3.7C1 - Mechanism shares vs kδ (interface sharpness), fixed ω/N=1
100% stacked area chart with log x-axis
"""

import matplotlib.pyplot as plt
import numpy as np

# Style settings
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial']
plt.rcParams['mathtext.fontset'] = 'custom'
plt.rcParams['mathtext.rm'] = 'Arial'
plt.rcParams['mathtext.it'] = 'Arial:italic'

# Color scheme
colors = {
    'classical': '#6B7280',
    'conversion': '#F4A261',
    'conversion_dark': '#C06A00',
    'interfacial': '#6A4C93',
    'shear': '#2A9D8F',
    'grid': '#E5E7EB',
    'dotted_line': '#9CA3AF'
}

# Create figure
fig, ax = plt.subplots(figsize=(20, 14), dpi=100, facecolor='white')

# kδ values (log scale)
k_delta = np.array([0.1, 0.2, 0.5, 1.0, 2.0, 3.0])
# Interpolate for smooth curves (in log space)
k_delta_fine = np.logspace(np.log10(0.1), np.log10(3.0), 200)

# Define shares for kδ sweep at fixed ω/N = 1.0
# Interfacial: highest for sharp layers (low kδ), monotone decrease
interfacial_base = np.array([0.60, 0.50, 0.35, 0.20, 0.12, 0.10])
interfacial = np.interp(np.log10(k_delta_fine), np.log10(k_delta), interfacial_base)

# Classical: complementary increase as kδ grows
classical_base = np.array([0.20, 0.25, 0.35, 0.42, 0.45, 0.45])
classical = np.interp(np.log10(k_delta_fine), np.log10(k_delta), classical_base)

# Mode conversion: roughly constant, weak hump near kδ ~ 1
conversion_base = np.array([0.22, 0.23, 0.25, 0.30, 0.28, 0.25])
conversion = np.interp(np.log10(k_delta_fine), np.log10(k_delta), conversion_base)

# Shear: small and nearly flat
shear_base = np.array([0.08, 0.08, 0.08, 0.09, 0.09, 0.08])
shear = np.interp(np.log10(k_delta_fine), np.log10(k_delta), shear_base)

# Normalize to ensure sum = 1
total = classical + conversion + interfacial + shear
classical = classical / total
conversion = conversion / total
interfacial = interfacial / total
shear = shear / total

# Create stacked areas (bottom to top: classical, conversion, interfacial, shear)
y_base = np.zeros_like(k_delta_fine)

# Classical (bottom)
ax.fill_between(k_delta_fine, y_base, y_base + classical, 
                color=colors['classical'], alpha=0.9, label='Classical', zorder=2)
y_base += classical

# Conversion
ax.fill_between(k_delta_fine, y_base, y_base + conversion, 
                color=colors['conversion'], alpha=0.9, label='Mode conversion', zorder=2)
y_base += conversion

# Interfacial
ax.fill_between(k_delta_fine, y_base, y_base + interfacial, 
                color=colors['interfacial'], alpha=0.9, label='Interfacial', zorder=2)
y_base += interfacial

# Shear (top)
ax.fill_between(k_delta_fine, y_base, y_base + shear, 
                color=colors['shear'], alpha=0.9, label='Shear-mediated', zorder=2)

# Add boundary lines for clarity
y_cum = np.zeros_like(k_delta_fine)
for share in [classical, conversion, interfacial, shear]:
    y_cum += share
    ax.plot(k_delta_fine, y_cum, 'k-', linewidth=0.5, alpha=0.3, zorder=3)

# Grid
ax.grid(True, which='major', color=colors['grid'], linewidth=0.8, alpha=1.0, zorder=1)
ax.set_axisbelow(True)

# Axes (log scale)
ax.set_xscale('log')
ax.set_xlim(0.1, 3.0)
ax.set_ylim(0, 1.0)
ax.set_xticks([0.1, 0.2, 0.5, 1.0, 2.0, 3.0])
ax.set_xticklabels(['0.1', '0.2', '0.5', '1.0', '2.0', '3.0'])
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_xlabel(r'$k\delta$', fontsize=22, fontweight='normal')
ax.set_ylabel('Share', fontsize=22, fontweight='normal')
ax.tick_params(axis='both', labelsize=16)

# Title
ax.set_title(r'Mechanism shares vs $k\delta$ (interface sharpness), fixed $\omega/N = 1$', 
             fontsize=28, fontweight='bold', pad=20)

# Mini gauge beneath axis for thin → resonant → thick
ax.text(0.1, -0.08, 'thin', fontsize=18, ha='center', va='top', 
        transform=ax.transData, style='italic', color='#6B7280')
ax.text(1.0, -0.08, 'resonant', fontsize=18, ha='center', va='top', 
        transform=ax.transData, style='italic', color='#6B7280')
ax.text(3.0, -0.08, 'thick', fontsize=18, ha='center', va='top', 
        transform=ax.transData, style='italic', color='#6B7280')

# Arrows for thin → resonant → thick
ax.annotate('', xy=(0.2, -0.12), xytext=(0.8, -0.12),
            arrowprops=dict(arrowstyle='<->', lw=1.5, color='#6B7280'),
            transform=ax.transData, annotation_clip=False)
ax.annotate('', xy=(1.2, -0.12), xytext=(2.5, -0.12),
            arrowprops=dict(arrowstyle='<->', lw=1.5, color='#6B7280'),
            transform=ax.transData, annotation_clip=False)

# Annotations
ax.annotate('interfacial peak\n(sharp layers)', 
            xy=(0.1, 0.80), xytext=(0.25, 0.88),
            fontsize=18, ha='left', va='center',
            arrowprops=dict(arrowstyle='->', lw=1.5, color='black'),
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black', linewidth=1))

ax.annotate('interfacial decay\n(diffuse layers)', 
            xy=(3.0, 0.95), xytext=(2.0, 0.85),
            fontsize=18, ha='center', va='bottom',
            arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))

ax.annotate('classical increases', 
            xy=(2.5, 0.23), xytext=(1.5, 0.15),
            fontsize=18, ha='center', va='top',
            arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))

# Legend
ax.legend(loc='center left', fontsize=17, frameon=False, bbox_to_anchor=(0.02, 0.5))

# Caption (inside canvas)
caption_text = (r"Figure 3.7C1. Interfacial share peaks for sharp, high-contrast transitions (low $k\delta$) "
                r"and decays as the interface becomes diffuse (large $k\delta$). Classical share increases "
                r"complementarily; conversion and shear change little at fixed $\omega/N$.")
fig.text(0.5, 0.08, caption_text, fontsize=15, ha='center', va='top', 
         style='italic', wrap=True, color='#1F2937')

plt.tight_layout(rect=[0, 0.12, 1, 1])
plt.savefig('figure_3_7C1.svg', format='svg', dpi=100, bbox_inches='tight', facecolor='white')
plt.savefig('figure_3_7C1.png', format='png', dpi=100, bbox_inches='tight', facecolor='white')
print("Figure 3.7C1 saved as SVG and PNG")
plt.close()
