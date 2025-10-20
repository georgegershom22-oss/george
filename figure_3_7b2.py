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
ax.text(10, 13.5, 'Figure 3.7B2 — Mechanism shares vs ω/N (Marginal Ri)', 
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

# X-axis (ω/N from 0.2 to 2.2)
omega_n_vals = np.linspace(0.2, 2.2, 100)
x_vals = plot_x_min + (omega_n_vals - 0.2) / 2.0 * (plot_x_max - plot_x_min)

# Define mechanism shares for marginal Ri case
def classical_share_marginal(omega_n):
    """Classical pedestal reduced (~0.25-0.35) in 0.8-1.3 band"""
    base = 0.35
    # Reduce in the 0.8-1.3 band
    reduction = 0.1 * np.exp(-((omega_n - 1.05) / 0.25)**2)
    return base - reduction

def conversion_share_marginal(omega_n):
    """Still domed at 1.0, peak ~0.35-0.50 (slightly lower than B1)"""
    return 0.40 * np.exp(-((omega_n - 1.0) / 0.4)**2) + 0.15

def interfacial_share_marginal(omega_n):
    """Still small (≤0.10) for continuous background"""
    return 0.05 + 0.05 * np.exp(-((omega_n - 1.0) / 0.6)**2)

def shear_share_marginal(omega_n):
    """Broad rise in 0.8-1.3, peaking ~0.30-0.45, approaching conversion"""
    # Broad peak centered around 1.0, extending from 0.8 to 1.3
    peak_center = 1.0
    peak_width = 0.25
    peak_height = 0.35
    
    # Create a broad peak
    peak = peak_height * np.exp(-((omega_n - peak_center) / peak_width)**2)
    
    # Add some baseline
    baseline = 0.05
    
    # Decay outside the 0.8-1.3 band
    mask = (omega_n >= 0.8) & (omega_n <= 1.3)
    result = np.where(mask, peak + baseline, baseline + 0.1 * peak)
    
    return result

# Calculate shares
classical_shares = classical_share_marginal(omega_n_vals)
conversion_shares = conversion_share_marginal(omega_n_vals)
interfacial_shares = interfacial_share_marginal(omega_n_vals)
shear_shares = shear_share_marginal(omega_n_vals)

# Normalize to ensure they sum to 1
total_shares = classical_shares + conversion_shares + interfacial_shares + shear_shares
classical_shares = classical_shares / total_shares
conversion_shares = conversion_shares / total_shares
interfacial_shares = interfacial_shares / total_shares
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

# Add the translucent amber conversion band (0.8 ≤ ω/N ≤ 1.2)
band_x_min = plot_x_min + (0.8 - 0.2) / 2.0 * (plot_x_max - plot_x_min)
band_x_max = plot_x_min + (1.2 - 0.2) / 2.0 * (plot_x_max - plot_x_min)
ax.axvspan(band_x_min, band_x_max, ymin=0, ymax=1, color=colors['amber_band'], alpha=0.2, zorder=0)

# Add dotted centerline at ω/N = 1
centerline_x = plot_x_min + (1.0 - 0.2) / 2.0 * (plot_x_max - plot_x_min)
ax.axvline(centerline_x, color=colors['dotted_line'], linewidth=1.2, linestyle=':', zorder=1)

# X-axis setup
ax.set_xlim(plot_x_min, plot_x_max)
ax.set_ylim(plot_y_min, plot_y_max)

# X-axis ticks and labels
x_ticks = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
x_tick_positions = [plot_x_min + (tick - 0.2) / 2.0 * (plot_x_max - plot_x_min) for tick in x_ticks]
ax.set_xticks(x_tick_positions)
ax.set_xticklabels([str(tick) for tick in x_ticks], **tick_font)

# Y-axis setup
y_ticks = [0, 0.25, 0.5, 0.75, 1.0]
y_tick_positions = [plot_y_min + tick * (plot_y_max - plot_y_min) for tick in y_ticks]
ax.set_yticks(y_tick_positions)
ax.set_yticklabels([str(tick) for tick in y_ticks], **tick_font)

# Axis labels
ax.set_xlabel('ω/N', **label_font)
ax.set_ylabel('Share (0-1)', **label_font)

# Add annotation
ax.annotate('shear-mediated share expands and can rival conversion near ω/N ~ 1', 
           xy=(centerline_x, 0.6), xytext=(centerline_x + 2, 0.7),
           arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
           fontsize=14, ha='center')

# Legend
legend_elements = [
    patches.Patch(color=colors['classical'], label='Classical'),
    patches.Patch(color=colors['conversion'], label='Mode conversion'),
    patches.Patch(color=colors['interfacial'], label='Interfacial'),
    patches.Patch(color=colors['shear'], label='Shear-mediated')
]
ax.legend(handles=legend_elements, loc='upper right', frameon=False, fontsize=16)

# Caption
caption_text = ("Figure 3.7B2. For marginal Ri, shear-mediated loss broadens around the "
                "conversion band and can rival conversion near ω/N ~ 1; classical share "
                "correspondingly diminishes.")
ax.text(10, 1.5, caption_text, ha='center', va='center', **caption_font, 
        bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8))

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_linewidth(1.5)
ax.spines['bottom'].set_linewidth(1.5)

plt.tight_layout()
plt.savefig('figure_3_7b2.png', dpi=100, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.savefig('figure_3_7b2.pdf', bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.show()