#!/usr/bin/env python3
"""
Figure 3.7B1 - Mechanism shares vs ω/N (High Ri, continuous)
100% stacked area chart showing mechanism shares under stable stratification
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from scipy.interpolate import interp1d

# Set up the figure
fig, ax = plt.subplots(figsize=(20, 14), dpi=100)
ax.set_facecolor('white')
fig.patch.set_facecolor('white')

# Define colors
colors = {
    'classical': '#6B7280',
    'conversion': '#F4A261',
    'interfacial': '#6A4C93',
    'shear': '#2A9D8F',
    'grid': '#E5E7EB',
    'dotted': '#9CA3AF',
    'amber_trans': '#F4A261'
}

# Title
ax.set_title('Figure 3.7B1 — Mechanism shares vs ω/N (High Ri, continuous)',
             fontsize=28, fontweight='bold', pad=20)

# Set up axes
ax.set_xlim(0.2, 2.2)
ax.set_ylim(0, 1)

# X-axis setup
ax.set_xlabel('ω/N', fontsize=22, fontstyle='italic')
x_ticks = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0, 2.2]
ax.set_xticks(x_ticks)
ax.set_xticklabels([str(x) for x in x_ticks], fontsize=16)

# Y-axis setup
ax.set_ylabel('Share', fontsize=22)
y_ticks = [0, 0.25, 0.5, 0.75, 1.0]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{y:.2f}' if y > 0 else '0' for y in y_ticks], fontsize=16)

# Grid
ax.grid(True, color=colors['grid'], linewidth=0.8, alpha=0.8)

# Generate x values for smooth curves
x = np.linspace(0.2, 2.2, 200)

# Define mechanism shares for High Ri case
# Classical: baseline ~0.35-0.45, slowly rising
classical_base = 0.40
classical = classical_base + 0.03 * (x - 1.0) + 0.02 * (x - 1.0)**2

# Mode conversion: broad dome centered at ω/N ≈ 1, peak ~0.45-0.60
conversion_peak = 0.52
conversion_width = 0.5
conversion = conversion_peak * np.exp(-((x - 1.0) / conversion_width)**2)
conversion[x < 0.5] *= np.exp(-2 * (0.5 - x[x < 0.5]))  # Taper at low end
conversion[x > 1.8] *= np.exp(-2 * (x[x > 1.8] - 1.8))  # Taper at high end

# Shear-mediated: low in high Ri, <0.10 with small shoulder around 0.9-1.2
shear = 0.05 + 0.08 * np.exp(-((x - 1.05) / 0.25)**2)

# Interfacial: minimal (≤0.10) in continuous case, nearly flat
interfacial = 0.05 * np.ones_like(x)

# Normalize to ensure sum = 1
total = classical + conversion + shear + interfacial
classical = classical / total
conversion = conversion / total
shear = shear / total
interfacial = interfacial / total

# Create stacked areas (bottom to top order)
ax.fill_between(x, 0, classical, 
                color=colors['classical'], alpha=1, label='Classical')

ax.fill_between(x, classical, classical + conversion,
                color=colors['conversion'], alpha=1, label='Mode conversion')

ax.fill_between(x, classical + conversion, classical + conversion + interfacial,
                color=colors['interfacial'], alpha=1, label='Interfacial')

ax.fill_between(x, classical + conversion + interfacial, 1.0,
                color=colors['shear'], alpha=1, label='Shear-mediated')

# Add conversion window (translucent amber band 0.8 ≤ ω/N ≤ 1.2)
ax.axvspan(0.8, 1.2, color=colors['amber_trans'], alpha=0.2, zorder=1)

# Add dotted centerline at ω/N = 1
ax.axvline(x=1.0, color=colors['dotted'], linewidth=1.2, linestyle=':', zorder=2)

# Add annotations with arrows
# Conversion peak annotation
peak_idx = np.argmax(conversion)
ax.annotate('conversion peak near ω/N ≈ 1',
            xy=(x[peak_idx], classical[peak_idx] + conversion[peak_idx]/2),
            xytext=(1.4, 0.7),
            fontsize=16,
            arrowprops=dict(arrowstyle='->', linewidth=1.5, color='black'))

# Classical baseline annotation
ax.annotate('classical baseline',
            xy=(1.8, classical[150]/2),
            xytext=(1.6, 0.15),
            fontsize=16,
            arrowprops=dict(arrowstyle='->', linewidth=1.5, color='black'))

# Secondary shear annotation
shear_peak_idx = np.argmax(shear)
ax.annotate('secondary shear\n(stable)',
            xy=(x[shear_peak_idx], classical[shear_peak_idx] + conversion[shear_peak_idx] + 
                interfacial[shear_peak_idx] + shear[shear_peak_idx]/2),
            xytext=(0.6, 0.92),
            fontsize=16,
            ha='center',
            arrowprops=dict(arrowstyle='->', linewidth=1.5, color='black'))

# Legend
ax.legend(loc='upper right', fontsize=16, frameon=False)

# Caption
fig.text(0.5, 0.05, 
         'Figure 3.7B1. Under high Ri and continuous stratification, mode conversion dominates near ω/N ≈ 1;\n' +
         'classical loss is the baseline; shear and interfacial contributions are secondary.',
         fontsize=15, ha='center', fontstyle='italic')

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('figure_3_7b1.png', dpi=100, bbox_inches='tight', facecolor='white')
plt.savefig('figure_3_7b1.pdf', dpi=100, bbox_inches='tight', facecolor='white')
plt.show()