#!/usr/bin/env python3
"""
Figure 3.7B2 — Mechanism shares vs ω/N (Marginal Ri, continuous)
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

# Frequency axis
omega_N = np.linspace(0.2, 2.2, 200)

# Define mechanism shares (modified for marginal Ri)
# Classical: reduced pedestal ~0.25-0.35 in 0.8-1.3 band
classical_base = 0.28 + 0.05 * (omega_N - 0.2) / 2.0
# Dip in the conversion/shear band
dip_factor = 1.0 - 0.25 * np.exp(-((omega_N - 1.05)**2) / 0.15)
classical = classical_base * dip_factor

# Mode conversion: dome at 1.0, peak ~0.35-0.50 (slightly lower than B1)
conversion = 0.42 * np.exp(-((omega_N - 1.0)**2) / 0.4) + 0.05

# Shear-mediated: broad rise in 0.8-1.3, peaking ~0.30-0.45
shear = 0.05 + 0.38 * np.exp(-((omega_N - 1.05)**2) / 0.12)

# Interfacial: still small (≤0.10)
interfacial = 0.05 + 0.02 * np.sin(omega_N * 2)

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

# Plot conversion band behind (translucent amber over 0.8-1.2)
ax.axvspan(0.8, 1.2, alpha=0.2, color=CONVERSION_COLOR, zorder=0)

# Dotted centerline at ω/N = 1
ax.axvline(1.0, color=CENTERLINE_COLOR, linestyle=':', linewidth=1.2, zorder=1)

# Stacked areas
ax.fill_between(omega_N, 0, y_classical, color=CLASSICAL_COLOR, alpha=0.9, 
                label='Classical', linewidth=0)
ax.fill_between(omega_N, y_classical, y_conversion, color=CONVERSION_COLOR, 
                alpha=0.9, label='Mode conversion', linewidth=0)
ax.fill_between(omega_N, y_conversion, y_interfacial, color=INTERFACIAL_COLOR, 
                alpha=0.9, label='Interfacial', linewidth=0)
ax.fill_between(omega_N, y_interfacial, y_shear, color=SHEAR_COLOR, 
                alpha=0.9, label='Shear-mediated', linewidth=0)

# Outline curves
ax.plot(omega_N, y_classical, color='white', linewidth=1, alpha=0.5)
ax.plot(omega_N, y_conversion, color='white', linewidth=1, alpha=0.5)
ax.plot(omega_N, y_interfacial, color='white', linewidth=1, alpha=0.5)

# Annotations
ax.annotate('shear-mediated share\nexpands and can rival\nconversion near $\\omega/N \\sim 1$', 
            xy=(1.05, 0.88), xytext=(1.5, 0.72),
            fontsize=NOTE_SIZE - 2, ha='left',
            arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='none'))

ax.annotate('classical share\ndiminishes', 
            xy=(0.95, 0.15), xytext=(0.5, 0.08),
            fontsize=NOTE_SIZE - 2, ha='center',
            arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='none'))

# Axes
ax.set_xlabel(r'$\omega/N$', fontsize=LABEL_SIZE, fontweight='normal', fontfamily='sans-serif')
ax.set_ylabel('Share', fontsize=LABEL_SIZE, fontweight='normal', fontfamily='sans-serif')
ax.set_xlim(0.2, 2.2)
ax.set_ylim(0, 1.0)

# Ticks
ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.tick_params(labelsize=TICK_SIZE)

# Grid
ax.grid(True, color=GRID_COLOR, linewidth=0.8, which='major')
ax.set_axisbelow(True)

# Title
ax.set_title('Figure 3.7B2 — Mechanism shares vs $\\omega/N$ (Marginal $Ri$, continuous)',
             fontsize=TITLE_SIZE, fontweight='bold', pad=20, fontfamily='sans-serif')

# Legend
legend = ax.legend(loc='upper right', frameon=False, fontsize=LEGEND_SIZE,
                   bbox_to_anchor=(0.98, 0.98))

# Caption
caption = ('Figure 3.7B2. For marginal $Ri$, shear-mediated loss broadens around the conversion band '
          'and can rival conversion near $\\omega/N \\sim 1$; classical share correspondingly diminishes.')

fig.text(0.5, 0.02, caption, ha='center', va='bottom',
         fontsize=CAPTION_SIZE, fontstyle='italic', fontfamily='sans-serif',
         wrap=True)

# Save
plt.tight_layout()
plt.savefig('/workspace/figure_3_7B2.png', dpi=DPI, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Figure 3.7B2 saved to /workspace/figure_3_7B2.png")
plt.close()
