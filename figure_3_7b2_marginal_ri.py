#!/usr/bin/env python3
"""
Figure 3.7B2 - Mechanism shares vs ω/N (Marginal Ri, continuous)
100% stacked area chart showing mechanism shares under marginal stability
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

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
ax.set_title('Figure 3.7B2 — Mechanism shares vs ω/N (Marginal Ri, continuous)',
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

# Define mechanism shares for Marginal Ri case
# Classical: reduced pedestal ~0.25-0.35 in 0.8-1.3 band
classical = 0.35 * np.ones_like(x)
# Reduce in conversion band
band_mask = (x >= 0.8) & (x <= 1.3)
classical[band_mask] = 0.30 - 0.05 * np.exp(-((x[band_mask] - 1.05) / 0.4)**2)

# Mode conversion: still domed at 1.0, peak ~0.35-0.50 (slightly lower than B1)
conversion_peak = 0.42
conversion_width = 0.5
conversion = conversion_peak * np.exp(-((x - 1.0) / conversion_width)**2)
conversion[x < 0.5] *= np.exp(-2 * (0.5 - x[x < 0.5]))
conversion[x > 1.8] *= np.exp(-2 * (x[x > 1.8] - 1.8))

# Shear-mediated: broad rise in 0.8-1.3, peaking ~0.30-0.45
shear = 0.10 * np.ones_like(x)
# Broad peak in conversion band
shear_band = (x >= 0.8) & (x <= 1.3)
shear[shear_band] = 0.35 * np.exp(-((x[shear_band] - 1.05) / 0.35)**2)
# Taper outside band
shear[x < 0.8] *= np.exp(-0.5 * (0.8 - x[x < 0.8])**2)
shear[x > 1.3] *= np.exp(-0.5 * (x[x > 1.3] - 1.3)**2)

# Interfacial: still small (≤0.10) for continuous background
interfacial = 0.06 * np.ones_like(x)

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

# Add annotation for expanded shear
shear_peak_idx = np.argmax(shear)
ax.annotate('shear-mediated share expands\nand can rival conversion near ω/N ~ 1',
            xy=(x[shear_peak_idx], classical[shear_peak_idx] + conversion[shear_peak_idx] + 
                interfacial[shear_peak_idx] + shear[shear_peak_idx]/2),
            xytext=(0.5, 0.75),
            fontsize=16,
            ha='center',
            arrowprops=dict(arrowstyle='->', linewidth=1.5, color='black'))

# Legend
ax.legend(loc='upper right', fontsize=16, frameon=False)

# Caption
fig.text(0.5, 0.05, 
         'Figure 3.7B2. For marginal Ri, shear-mediated loss broadens around the conversion band and can rival\n' +
         'conversion near ω/N ~ 1; classical share correspondingly diminishes.',
         fontsize=15, ha='center', fontstyle='italic')

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('figure_3_7b2.png', dpi=100, bbox_inches='tight', facecolor='white')
plt.savefig('figure_3_7b2.pdf', dpi=100, bbox_inches='tight', facecolor='white')
plt.show()