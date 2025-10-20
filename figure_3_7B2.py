"""
Figure 3.7B2 - Mechanism shares vs ω/N (Marginal Ri, continuous)
100% stacked area chart
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

# ω/N values
omega_N = np.array([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0, 2.2])
# Interpolate for smooth curves
omega_N_fine = np.linspace(0.2, 2.2, 200)

# Define shares for Marginal Ri case
# Classical: pedestal reduced ~0.25-0.35 in 0.8-1.3 band
classical_base = np.array([0.40, 0.38, 0.28, 0.25, 0.27, 0.35, 0.40, 0.42])
classical = np.interp(omega_N_fine, omega_N, classical_base)

# Mode conversion: still domed at 1.0, peak ~0.35-0.50 (slightly lower than B1)
conversion_base = np.array([0.12, 0.20, 0.35, 0.45, 0.38, 0.28, 0.18, 0.13])
conversion = np.interp(omega_N_fine, omega_N, conversion_base)

# Shear-mediated: broad rise in 0.8-1.3, peaking ~0.30-0.45, approaching conversion
shear_base = np.array([0.10, 0.12, 0.25, 0.40, 0.32, 0.18, 0.12, 0.10])
shear = np.interp(omega_N_fine, omega_N, shear_base)

# Interfacial: still small ≤0.10 for continuous background
interfacial_base = np.array([0.08, 0.07, 0.06, 0.05, 0.05, 0.06, 0.08, 0.08])
interfacial = np.interp(omega_N_fine, omega_N, interfacial_base)

# Normalize to ensure sum = 1
total = classical + conversion + interfacial + shear
classical = classical / total
conversion = conversion / total
interfacial = interfacial / total
shear = shear / total

# Conversion window (translucent amber)
ax.axvspan(0.8, 1.2, alpha=0.2, color=colors['conversion'], zorder=0)
ax.axvline(1.0, color=colors['dotted_line'], linewidth=1.2, linestyle='dotted', zorder=1)

# Create stacked areas (bottom to top: classical, conversion, interfacial, shear)
y_base = np.zeros_like(omega_N_fine)

# Classical (bottom)
ax.fill_between(omega_N_fine, y_base, y_base + classical, 
                color=colors['classical'], alpha=0.9, label='Classical', zorder=2)
y_base += classical

# Conversion
ax.fill_between(omega_N_fine, y_base, y_base + conversion, 
                color=colors['conversion'], alpha=0.9, label='Mode conversion', zorder=2)
y_base += conversion

# Interfacial
ax.fill_between(omega_N_fine, y_base, y_base + interfacial, 
                color=colors['interfacial'], alpha=0.9, label='Interfacial', zorder=2)
y_base += interfacial

# Shear (top)
ax.fill_between(omega_N_fine, y_base, y_base + shear, 
                color=colors['shear'], alpha=0.9, label='Shear-mediated', zorder=2)

# Add boundary lines for clarity
y_cum = np.zeros_like(omega_N_fine)
for share in [classical, conversion, interfacial, shear]:
    y_cum += share
    ax.plot(omega_N_fine, y_cum, 'k-', linewidth=0.5, alpha=0.3, zorder=3)

# Grid
ax.grid(True, which='major', color=colors['grid'], linewidth=0.8, alpha=1.0, zorder=1)
ax.set_axisbelow(True)

# Axes
ax.set_xlim(0.2, 2.2)
ax.set_ylim(0, 1.0)
ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_xlabel(r'$\omega/N$', fontsize=22, fontweight='normal')
ax.set_ylabel('Share', fontsize=22, fontweight='normal')
ax.tick_params(axis='both', labelsize=16)

# Title
ax.set_title(r'Mechanism shares vs $\omega/N$ (Marginal $Ri$, continuous)', 
             fontsize=28, fontweight='bold', pad=20)

# Annotations
ax.annotate(r'shear-mediated share\nexpands and can rival\nconversion near $\omega/N \sim 1$', 
            xy=(1.0, 0.85), xytext=(1.4, 0.92),
            fontsize=18, ha='left', va='center',
            arrowprops=dict(arrowstyle='->', lw=1.5, color='black'),
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black', linewidth=1))

ax.annotate('classical share\ndiminishes', 
            xy=(1.0, 0.13), xytext=(0.5, 0.08),
            fontsize=18, ha='center', va='top',
            arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))

# Legend
ax.legend(loc='upper left', fontsize=17, frameon=False, bbox_to_anchor=(0.02, 0.65))

# Caption (inside canvas)
caption_text = (r"Figure 3.7B2. For marginal $Ri$, shear-mediated loss broadens around the conversion band "
                r"and can rival conversion near $\omega/N \sim 1$; classical share correspondingly diminishes.")
fig.text(0.5, 0.08, caption_text, fontsize=15, ha='center', va='top', 
         style='italic', wrap=True, color='#1F2937')

plt.tight_layout(rect=[0, 0.12, 1, 1])
plt.savefig('figure_3_7B2.svg', format='svg', dpi=100, bbox_inches='tight', facecolor='white')
plt.savefig('figure_3_7B2.png', format='png', dpi=100, bbox_inches='tight', facecolor='white')
print("Figure 3.7B2 saved as SVG and PNG")
plt.close()
