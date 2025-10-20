#!/usr/bin/env python3
"""
Figure 3.7C1 — Mechanism shares vs kδ (interface sharpness) at fixed ω/N
"""

import matplotlib.pyplot as plt
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
fig, ax = plt.subplots(figsize=FIGSIZE, facecolor='white', dpi=DPI)

# kδ axis (log scale)
kd = np.logspace(np.log10(0.1), np.log10(3), 200)

# Define mechanism shares
# Interfacial: highest for sharp layers (low kδ), ~0.55-0.65 at 0.1, monotone decrease to ~0.10 at 3
interfacial = 0.65 * np.exp(-kd / 0.8) + 0.08

# Classical: complementary increase (inverse of interfacial trend)
classical = 0.20 + 0.30 * (1 - np.exp(-kd / 0.8))

# Mode conversion: roughly constant 0.20-0.30 with mild bump near kδ ~ 1
conversion = 0.22 + 0.08 * np.exp(-((np.log(kd) - np.log(1.0))**2) / 0.3)

# Shear-mediated: small and nearly flat (≤0.10)
shear = 0.06 + 0.02 * np.sin(np.log(kd) * 2)

# Normalize to sum to 1
total = classical + conversion + shear + interfacial
classical /= total
conversion /= total
shear /= total
interfacial /= total

# Stack the areas (bottom to top: classical, conversion, interfacial, shear)
y_classical = classical
y_conversion = y_classical + conversion
y_interfacial = y_conversion + interfacial
y_shear = y_interfacial + shear  # Should equal 1

# Stacked areas
ax.fill_between(kd, 0, y_classical, color=CLASSICAL_COLOR, alpha=0.9, 
                label='Classical', linewidth=0)
ax.fill_between(kd, y_classical, y_conversion, color=CONVERSION_COLOR, 
                alpha=0.9, label='Mode conversion', linewidth=0)
ax.fill_between(kd, y_conversion, y_interfacial, color=INTERFACIAL_COLOR, 
                alpha=0.9, label='Interfacial', linewidth=0)
ax.fill_between(kd, y_interfacial, y_shear, color=SHEAR_COLOR, 
                alpha=0.9, label='Shear-mediated', linewidth=0)

# Outline curves
ax.plot(kd, y_classical, color='white', linewidth=1, alpha=0.5)
ax.plot(kd, y_conversion, color='white', linewidth=1, alpha=0.5)
ax.plot(kd, y_interfacial, color='white', linewidth=1, alpha=0.5)

# Annotations
ax.annotate('interfacial\npeak (sharp)', 
            xy=(0.12, 0.72), xytext=(0.25, 0.82),
            fontsize=NOTE_SIZE - 2, ha='left',
            arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='none'))

ax.annotate('classical\nrises (diffuse)', 
            xy=(2.5, 0.28), xytext=(1.5, 0.18),
            fontsize=NOTE_SIZE - 2, ha='center',
            arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='none'))

# Mini gauge beneath x-axis (thin → resonant → thick)
y_gauge = -0.13
ax.annotate('', xy=(0.1, y_gauge), xytext=(3, y_gauge),
            arrowprops=dict(arrowstyle='<->', color='black', lw=1.2))
ax.text(0.1, y_gauge - 0.04, 'thin', ha='center', va='top', 
        fontsize=TICK_SIZE - 2, fontfamily='sans-serif')
ax.text(1.0, y_gauge - 0.04, 'resonant', ha='center', va='top', 
        fontsize=TICK_SIZE - 2, fontfamily='sans-serif')
ax.text(3.0, y_gauge - 0.04, 'thick', ha='center', va='top', 
        fontsize=TICK_SIZE - 2, fontfamily='sans-serif')

# Axes
ax.set_xlabel(r'$k\delta$', fontsize=LABEL_SIZE, fontweight='normal', fontfamily='sans-serif')
ax.set_ylabel('Share', fontsize=LABEL_SIZE, fontweight='normal', fontfamily='sans-serif')
ax.set_xscale('log')
ax.set_xlim(0.1, 3)
ax.set_ylim(0, 1.0)

# Ticks
ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 3])
ax.set_xticklabels(['0.1', '0.2', '0.5', '1', '2', '3'])
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.tick_params(labelsize=TICK_SIZE)

# Grid
ax.grid(True, color=GRID_COLOR, linewidth=0.8, which='major')
ax.set_axisbelow(True)

# Title
ax.set_title('Figure 3.7C1 — Mechanism shares vs $k\\delta$ (interface sharpness), fixed $\\omega/N = 1$',
             fontsize=TITLE_SIZE, fontweight='bold', pad=20, fontfamily='sans-serif')

# Legend
legend = ax.legend(loc='upper right', frameon=False, fontsize=LEGEND_SIZE,
                   bbox_to_anchor=(0.98, 0.98))

# Caption
caption = ('Figure 3.7C1. Interfacial share peaks for sharp, high-contrast transitions (low $k\\delta$) '
          'and decays as the interface becomes diffuse (large $k\\delta$). Classical share increases '
          'complementarily; conversion and shear change little at fixed $\\omega/N$.')

fig.text(0.5, 0.02, caption, ha='center', va='bottom',
         fontsize=CAPTION_SIZE, fontstyle='italic', fontfamily='sans-serif',
         wrap=True)

# Save
plt.tight_layout()
plt.savefig('/workspace/figure_3_7C1.png', dpi=DPI, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Figure 3.7C1 saved to /workspace/figure_3_7C1.png")
plt.close()
