import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Set up the figure with exact specifications
fig, ax = plt.subplots(figsize=(20, 14))  # 2000x1400 px at 100 DPI
ax.set_xlim(0, 20)
ax.set_ylim(0, 14)

# Color scheme
colors = {
    'classical': '#6B7280',
    'conversion': '#F4A261', 
    'interfacial': '#6A4C93',
    'shear': '#2A9D8F',
    'amber_band': '#F4A261',
    'dotted_line': '#9CA3AF',
    'grid': '#E5E7EB'
}

# Font settings
title_font = {'fontsize': 28, 'fontweight': 'bold', 'fontfamily': 'sans-serif'}
label_font = {'fontsize': 22, 'fontfamily': 'sans-serif'}
tick_font = {'fontsize': 16, 'fontfamily': 'sans-serif'}
note_font = {'fontsize': 18, 'fontfamily': 'sans-serif'}
caption_font = {'fontsize': 15, 'style': 'italic', 'fontfamily': 'sans-serif'}

# Main title
ax.text(10, 13.5, 'Figure 3.7C1 — Mechanism shares vs kδ (interface sharpness), fixed ω/N = 1', 
        ha='center', va='center', **title_font)

# Set up the plot area
plot_x_min, plot_x_max = 2, 18
plot_y_min, plot_y_max = 2, 12
ax.set_xlim(plot_x_min, plot_x_max)
ax.set_ylim(plot_y_min, plot_y_max)

# Grid lines
for x in np.linspace(plot_x_min, plot_x_max, 11):  # 10 intervals
    ax.axvline(x, color=colors['grid'], linewidth=0.8, alpha=0.7)
for y in np.linspace(plot_y_min, plot_y_max, 5):  # 4 intervals
    ax.axhline(y, color=colors['grid'], linewidth=0.8, alpha=0.7)

# X-axis (kδ from 0.1 to 3, log scale)
k_delta_vals = np.logspace(np.log10(0.1), np.log10(3), 100)
x_vals = plot_x_min + (np.log10(k_delta_vals) - np.log10(0.1)) / (np.log10(3) - np.log10(0.1)) * (plot_x_max - plot_x_min)

# Define mechanism shares for fixed ω/N = 1
def interfacial_share_kdelta(k_delta):
    """Highest for sharp layers (low kδ), monotone decrease toward ~0.10 by kδ≈3"""
    # Start high at kδ=0.1 (~0.55-0.65) and decrease to ~0.10 at kδ=3
    return 0.60 * np.exp(-k_delta / 0.8) + 0.10

def classical_share_kdelta(k_delta):
    """Complementary increase as kδ grows (e.g., ~0.20 at 0.1 → ~0.45 at 3)"""
    # Start low at kδ=0.1 (~0.20) and increase to ~0.45 at kδ=3
    return 0.20 + 0.25 * (1 - np.exp(-k_delta / 1.5))

def conversion_share_kdelta(k_delta):
    """Roughly constant (e.g., 0.20-0.30) with at most a mild hump near kδ~1"""
    base = 0.25
    # Add a very subtle hump near kδ=1
    hump = 0.05 * np.exp(-((k_delta - 1.0) / 0.5)**2)
    return base + hump

def shear_share_kdelta(k_delta):
    """Small and nearly flat (≤0.10) since Ri and shear are not being swept"""
    return 0.05 + 0.03 * np.exp(-((k_delta - 1.0) / 1.0)**2)

# Calculate shares
interfacial_shares = interfacial_share_kdelta(k_delta_vals)
classical_shares = classical_share_kdelta(k_delta_vals)
conversion_shares = conversion_share_kdelta(k_delta_vals)
shear_shares = shear_share_kdelta(k_delta_vals)

# Normalize to ensure they sum to 1
total_shares = interfacial_shares + classical_shares + conversion_shares + shear_shares
interfacial_shares = interfacial_shares / total_shares
classical_shares = classical_shares / total_shares
conversion_shares = conversion_shares / total_shares
shear_shares = shear_shares / total_shares

# Convert to y-coordinates (0 to 1 scale)
y_classical = plot_y_min + classical_shares * (plot_y_max - plot_y_min)
y_conversion = y_classical + conversion_shares * (plot_y_max - plot_y_min)
y_interfacial = y_conversion + interfacial_shares * (plot_y_max - plot_y_min)
y_shear = y_interfacial + shear_shares * (plot_y_max - plot_y_min)

# Draw stacked areas (bottom to top: classical, conversion, interfacial, shear)
ax.fill_between(x_vals, plot_y_min, y_classical, color=colors['classical'], alpha=0.8, label='Classical')
ax.fill_between(x_vals, y_classical, y_conversion, color=colors['conversion'], alpha=0.8, label='Mode conversion')
ax.fill_between(x_vals, y_conversion, y_interfacial, color=colors['interfacial'], alpha=0.8, label='Interfacial')
ax.fill_between(x_vals, y_interfacial, y_shear, color=colors['shear'], alpha=0.8, label='Shear-mediated')

# X-axis setup
ax.set_xlim(plot_x_min, plot_x_max)
ax.set_ylim(plot_y_min, plot_y_max)

# X-axis ticks and labels (log scale)
x_ticks = [0.1, 0.2, 0.5, 1, 2, 3]
x_tick_positions = [plot_x_min + (np.log10(tick) - np.log10(0.1)) / (np.log10(3) - np.log10(0.1)) * (plot_x_max - plot_x_min) for tick in x_ticks]
ax.set_xticks(x_tick_positions)
ax.set_xticklabels([str(tick) for tick in x_ticks], **tick_font)

# Y-axis setup
y_ticks = [0, 0.25, 0.5, 0.75, 1.0]
y_tick_positions = [plot_y_min + tick * (plot_y_max - plot_y_min) for tick in y_ticks]
ax.set_yticks(y_tick_positions)
ax.set_yticklabels([str(tick) for tick in y_ticks], **tick_font)

# Axis labels
ax.set_xlabel('kδ', **label_font)
ax.set_ylabel('Share (0-1)', **label_font)

# Add mini gauge beneath x-axis
gauge_positions = [0.1, 1, 3]
gauge_x_positions = [plot_x_min + (np.log10(pos) - np.log10(0.1)) / (np.log10(3) - np.log10(0.1)) * (plot_x_max - plot_x_min) for pos in gauge_positions]
gauge_labels = ['thin', 'resonant', 'thick']

for i, (x_pos, label) in enumerate(zip(gauge_x_positions, gauge_labels)):
    ax.text(x_pos, plot_y_min - 0.3, label, ha='center', va='top', fontsize=12, style='italic')
    # Add small vertical line
    ax.plot([x_pos, x_pos], [plot_y_min - 0.1, plot_y_min - 0.05], 'k-', linewidth=1)

# Add connecting lines for the gauge
ax.plot([gauge_x_positions[0], gauge_x_positions[1]], [plot_y_min - 0.2, plot_y_min - 0.2], 'k-', linewidth=0.8)
ax.plot([gauge_x_positions[1], gauge_x_positions[2]], [plot_y_min - 0.2, plot_y_min - 0.2], 'k-', linewidth=0.8)

# Legend
legend_elements = [
    patches.Patch(color=colors['classical'], label='Classical'),
    patches.Patch(color=colors['conversion'], label='Mode conversion'),
    patches.Patch(color=colors['interfacial'], label='Interfacial'),
    patches.Patch(color=colors['shear'], label='Shear-mediated')
]
ax.legend(handles=legend_elements, loc='upper right', frameon=False, fontsize=16)

# Caption
caption_text = ("Figure 3.7C1. Interfacial share peaks for sharp, high-contrast transitions "
                "(low kδ) and decays as the interface becomes diffuse (large kδ). Classical "
                "share increases complementarily; conversion and shear change little at fixed ω/N.")
ax.text(10, 1.5, caption_text, ha='center', va='center', **caption_font, 
        bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8))

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_linewidth(1.5)
ax.spines['bottom'].set_linewidth(1.5)

plt.tight_layout()
plt.savefig('figure_3_7c1.png', dpi=100, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.savefig('figure_3_7c1.pdf', bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.show()