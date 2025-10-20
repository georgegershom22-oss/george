#!/usr/bin/env python3
"""
Figure 3.7C1 - Mechanism shares vs kδ (interface sharpness)
100% stacked area chart showing how interfacial share depends on thickness parameter kδ
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
    'dotted': '#9CA3AF'
}

# Title
ax.set_title('Figure 3.7C1 — Mechanism shares vs kδ (interface sharpness), fixed ω/N = 1',
             fontsize=28, fontweight='bold', pad=20)

# Set up axes with log scale for x
ax.set_xscale('log')
ax.set_xlim(0.1, 3)
ax.set_ylim(0, 1)

# X-axis setup
ax.set_xlabel('kδ', fontsize=22, fontstyle='italic')
x_ticks = [0.1, 0.2, 0.5, 1, 2, 3]
ax.set_xticks(x_ticks)
ax.set_xticklabels([str(x) for x in x_ticks], fontsize=16)

# Y-axis setup
ax.set_ylabel('Share', fontsize=22)
y_ticks = [0, 0.25, 0.5, 0.75, 1.0]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{y:.2f}' if y > 0 else '0' for y in y_ticks], fontsize=16)

# Grid (only major ticks)
ax.grid(True, which='major', color=colors['grid'], linewidth=0.8, alpha=0.8)

# Generate x values for smooth curves (log-spaced)
x = np.logspace(np.log10(0.1), np.log10(3), 200)

# Define mechanism shares vs kδ at fixed ω/N = 1
# Interfacial: highest for sharp layers (low kδ), monotonic decrease
interfacial_max = 0.60
interfacial_min = 0.10
# Smooth monotonic decrease from max to min
interfacial = interfacial_max * np.exp(-1.5 * np.log10(x/0.1))
interfacial[interfacial < interfacial_min] = interfacial_min

# Classical: complementary increase as kδ grows
classical_min = 0.20
classical_max = 0.45
# Complementary to interfacial
classical = classical_min + (classical_max - classical_min) * (np.log10(x/0.1) / np.log10(30))
classical[classical > classical_max] = classical_max
classical[classical < classical_min] = classical_min

# Mode conversion: roughly constant with very subtle hump near kδ ~ 1
conversion = 0.25 * np.ones_like(x)
# Add very subtle hump
conversion += 0.03 * np.exp(-((np.log10(x) - np.log10(1)) / 0.5)**2)

# Shear-mediated: small and nearly flat (≤0.10)
shear = 0.08 * np.ones_like(x)

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

# Add mini gauge beneath x-axis
gauge_y = -0.08
# Draw arrows and labels
ax.annotate('', xy=(0.1, gauge_y), xytext=(0.15, gauge_y),
            xycoords=('data', 'axes fraction'),
            arrowprops=dict(arrowstyle='<->', linewidth=1.5, color='black'))
ax.text(0.12, gauge_y - 0.02, 'thin', fontsize=14, ha='center',
        transform=ax.get_xaxis_transform())

ax.annotate('', xy=(0.7, gauge_y), xytext=(1.4, gauge_y),
            xycoords=('data', 'axes fraction'),
            arrowprops=dict(arrowstyle='<->', linewidth=1.5, color='black'))
ax.text(1.0, gauge_y - 0.02, 'resonant', fontsize=14, ha='center',
        transform=ax.get_xaxis_transform())

ax.annotate('', xy=(2, gauge_y), xytext=(3, gauge_y),
            xycoords=('data', 'axes fraction'),
            arrowprops=dict(arrowstyle='<->', linewidth=1.5, color='black'))
ax.text(2.5, gauge_y - 0.02, 'thick', fontsize=14, ha='center',
        transform=ax.get_xaxis_transform())

# Add annotations
# Interfacial peak annotation
ax.annotate('Interfacial dominates\nfor sharp transitions',
            xy=(0.15, 0.3),
            xytext=(0.25, 0.6),
            fontsize=16,
            ha='center',
            arrowprops=dict(arrowstyle='->', linewidth=1.5, color='black'))

# Classical increase annotation
ax.annotate('Classical increases\nas interface diffuses',
            xy=(2.5, 0.2),
            xytext=(1.5, 0.15),
            fontsize=16,
            ha='center',
            arrowprops=dict(arrowstyle='->', linewidth=1.5, color='black'))

# Legend
ax.legend(loc='upper right', fontsize=16, frameon=False)

# Caption
fig.text(0.5, 0.05, 
         'Figure 3.7C1. Interfacial share peaks for sharp, high-contrast transitions (low kδ) and decays as the\n' +
         'interface becomes diffuse (large kδ). Classical share increases complementarily; conversion and shear change little at fixed ω/N.',
         fontsize=15, ha='center', fontstyle='italic')

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('figure_3_7c1.png', dpi=100, bbox_inches='tight', facecolor='white')
plt.savefig('figure_3_7c1.pdf', dpi=100, bbox_inches='tight', facecolor='white')
plt.show()