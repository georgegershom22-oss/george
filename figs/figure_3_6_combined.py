#!/usr/bin/env python3
"""
Figure 3.6 (Combined A–C) — Shear-mediated loss influences
Single composite figure with three panels arranged vertically
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.gridspec import GridSpec
from house_style import (
    apply_house_style, setup_omega_n_axis, setup_ri_axis,
    add_conversion_band, add_panel_title, add_caption, colorbar_style,
    COLORS, CANVAS_WIDTH_PX, CANVAS_HEIGHT_PX
)

# Extended canvas for three panels stacked vertically
COMBINED_HEIGHT = 3200  # px, accommodate three rows
DPI = 100

apply_house_style()

# Create figure with extended height
fig = plt.figure(figsize=(CANVAS_WIDTH_PX/DPI, COMBINED_HEIGHT/DPI), dpi=DPI, facecolor='white')

# GridSpec layout: 3 rows for A, B, C with appropriate height ratios
gs = GridSpec(3, 1, figure=fig, height_ratios=[1.0, 1.0, 1.0], 
              hspace=0.15, left=0.08, right=0.92, top=0.96, bottom=0.03)

# ============================================================================
# Panel A: Shear-dominance index heatmap
# ============================================================================
ax_a = fig.add_subplot(gs[0, 0])

omega_n = np.linspace(0.2, 2.2, 200)
ri_vals = np.linspace(0.0, 2.0, 150)
Omega, Ri = np.meshgrid(omega_n, ri_vals)

# Shear-dominance index: bright lobe near conversion window at low Ri
center_omega = 1.0
center_ri = 0.4
sigma_omega = 0.25
sigma_ri = 0.3
peak_sdi = 0.95

SDI = peak_sdi * np.exp(-((Omega - center_omega)**2 / (2*sigma_omega**2) + 
                           (Ri - center_ri)**2 / (2*sigma_ri**2)))

# Add sub-buoyancy tail
tail_mask = (Omega < 0.9) & (Ri < 0.3)
SDI += 0.25 * np.exp(-((Omega - 0.6)**2 / 0.15 + (Ri - 0.15)**2 / 0.05)) * tail_mask

# Decay at high frequency
decay_factor = np.exp(-np.maximum(0, (Omega - 1.4) / 0.4)**2)
SDI *= decay_factor

# Smooth decay with Ri
ri_decay = np.exp(-((Ri - 0.4) / 1.2)**2.5)
SDI *= ri_decay
SDI = np.clip(SDI, 0, 1)

# Plot heatmap (darker = higher)
im_a = ax_a.pcolormesh(Omega, Ri, SDI, cmap='cividis_r', shading='gouraud', 
                       vmin=0, vmax=1, rasterized=True)

setup_omega_n_axis(ax_a, label_pos='bottom')
setup_ri_axis(ax_a, label_pos='left')
add_conversion_band(ax_a, ri_range=(0.0, 2.0))

# Marginal stability guide
ax_a.axhline(0.25, color='#6B7280', linestyle='--', linewidth=1.2, alpha=0.6)
ax_a.text(0.25, 0.28, 'marginal stability', fontsize=16, color='#374151', 
          verticalalignment='bottom')

add_panel_title(ax_a, r'Figure 3.6A — Shear-dominance index $\mathit{SDI}(Ri,\omega/N)$')

# Colorbar
cbar_a = colorbar_style(fig, im_a, ax_a, label='Shear-dominance index (0–1)')
cbar_a.set_ticks([0, 0.25, 0.5, 0.75, 1.0])

# Caption inside bottom
caption_a = (r"Bright regions indicate parameter pairs where shear-mediated loss dominates; "
             r"peak influence occurs near $\omega/N\!\approx\!1$ under marginal $Ri$, "
             r"and decays at higher $Ri$ or $\omega/N>1$.")
ax_a.text(0.5, -0.16, caption_a, transform=ax_a.transAxes, fontsize=15, 
          style='italic', ha='center', va='top')

# ============================================================================
# Panel B: Time–frequency TL fluctuation intensity (side-by-side)
# ============================================================================
# Create nested GridSpec for two subpanels
gs_b = GridSpec(1, 2, figure=fig, width_ratios=[1, 1], wspace=0.08,
                left=0.08, right=0.88, top=0.63, bottom=0.36)

ax_b_left = fig.add_subplot(gs_b[0, 0])
ax_b_right = fig.add_subplot(gs_b[0, 1])

time = np.linspace(0, 60, 300)
omega_n_b = np.linspace(0.2, 2.2, 200)
T, Omega_b = np.meshgrid(time, omega_n_b)

# Left: high Ri - narrow conversion band
center_band = 1.0
bandwidth = 0.15
intensity_left = 0.7 * np.exp(-((Omega_b - center_band) / bandwidth)**2)
# Add slight time modulation
time_mod = 1 + 0.15 * np.sin(2 * np.pi * T / 20) * np.exp(-((Omega_b - center_band) / 0.2)**2)
TL_left = intensity_left * time_mod
TL_left = np.clip(TL_left, 0, 1)

# Right: marginal Ri - intermittent broadband bursts
# Base conversion band
TL_right = 0.3 * np.exp(-((Omega_b - center_band) / 0.25)**2)
# Add intermittent bursts
np.random.seed(42)
n_bursts = 8
for _ in range(n_bursts):
    t_burst = np.random.uniform(5, 55)
    omega_burst = np.random.uniform(0.5, 1.8)
    width_t = np.random.uniform(3, 8)
    width_omega = np.random.uniform(0.3, 0.6)
    intensity = np.random.uniform(0.6, 0.95)
    
    burst = intensity * np.exp(-(((T - t_burst) / width_t)**2 + 
                                  ((Omega_b - omega_burst) / width_omega)**2))
    TL_right += burst

TL_right = np.clip(TL_right, 0, 1)

# Plot both panels with shared colormap
vmax_common = 1.0
im_b_left = ax_b_left.pcolormesh(T, Omega_b, TL_left, cmap='cividis_r', 
                                 shading='gouraud', vmin=0, vmax=vmax_common, rasterized=True)
im_b_right = ax_b_right.pcolormesh(T, Omega_b, TL_right, cmap='cividis_r', 
                                   shading='gouraud', vmin=0, vmax=vmax_common, rasterized=True)

# Style left panel
ax_b_left.set_xlabel(r'Time $t$ (s)', fontsize=22, labelpad=8)
ax_b_left.set_ylabel(r'$\omega/N$', fontsize=22, labelpad=8)
ax_b_left.set_xlim(0, 60)
ax_b_left.set_ylim(0.2, 2.2)
ax_b_left.set_xticks([0, 10, 20, 30, 40, 50, 60])
ax_b_left.set_yticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
ax_b_left.tick_params(labelsize=16)
ax_b_left.grid(True, color='#E5E7EB', linewidth=0.8, alpha=0.8)
add_conversion_band(ax_b_left, ri_range=(0.2, 2.2), orientation='horizontal')
ax_b_left.text(0.5, 0.96, 'High $Ri$', transform=ax_b_left.transAxes, 
               fontsize=24, weight='bold', ha='center', va='top')
ax_b_left.text(30, 1.05, 'narrow conversion-band\nmodulation', fontsize=16, 
               ha='center', va='center', color='#1F2937')

# Style right panel
ax_b_right.set_xlabel(r'Time $t$ (s)', fontsize=22, labelpad=8)
ax_b_right.set_xlim(0, 60)
ax_b_right.set_ylim(0.2, 2.2)
ax_b_right.set_xticks([0, 10, 20, 30, 40, 50, 60])
ax_b_right.set_yticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
ax_b_right.set_yticklabels([])  # Share y-axis, no labels on right
ax_b_right.tick_params(labelsize=16)
ax_b_right.grid(True, color='#E5E7EB', linewidth=0.8, alpha=0.8)
add_conversion_band(ax_b_right, ri_range=(0.2, 2.2), orientation='horizontal')
ax_b_right.text(0.5, 0.96, 'Marginal $Ri$', transform=ax_b_right.transAxes, 
                fontsize=24, weight='bold', ha='center', va='top')
ax_b_right.annotate('intermittent\nbroadband bursts', xy=(45, 1.7), 
                   xytext=(50, 1.95), fontsize=16, ha='center',
                   arrowprops=dict(arrowstyle='->', lw=1.2, color='#1F2937'))
ax_b_right.text(15, 0.5, 'enhanced spread\nbeyond conversion', fontsize=16, 
                ha='center', va='center', color='#1F2937')

# Shared colorbar to the right
cbar_ax_b = fig.add_axes([0.90, 0.36, 0.015, 0.27])
cbar_b = fig.colorbar(im_b_right, cax=cbar_ax_b)
cbar_b.set_label('TL fluctuation intensity (arb.)', fontsize=18, labelpad=12)
cbar_b.ax.tick_params(labelsize=14)

# Panel B title
fig.text(0.08, 0.645, r'Figure 3.6B — Time–frequency TL fluctuation intensity', 
         fontsize=28, weight='bold', va='top')

# Captions inside panels
caption_left = r"High $Ri$: fluctuation energy concentrated in a narrow conversion band."
caption_right = r"Marginal $Ri$: intermittent broadband activity indicates shear-mediated variability."
ax_b_left.text(0.5, 0.04, caption_left, transform=ax_b_left.transAxes, 
               fontsize=15, style='italic', ha='center', va='bottom')
ax_b_right.text(0.5, 0.04, caption_right, transform=ax_b_right.transAxes, 
                fontsize=15, style='italic', ha='center', va='bottom')

# ============================================================================
# Panel C: Coherent fraction vs Ri (left) and PSD broadening (right)
# ============================================================================
gs_c = GridSpec(1, 2, figure=fig, width_ratios=[1, 1], wspace=0.12,
                left=0.08, right=0.92, top=0.32, bottom=0.06)

ax_c_left = fig.add_subplot(gs_c[0, 0])
ax_c_right = fig.add_subplot(gs_c[0, 1])

# Left: Coherent fraction vs Ri
ri_c = np.linspace(0.0, 2.0, 100)
coherent_base = 0.5 + 0.45 * (1 - np.exp(-((ri_c - 0.5) / 0.8)**2))
# Add intermittent dip
dip_center = 0.4
dip_width = 0.15
dip_depth = 0.1
dip = dip_depth * np.exp(-((ri_c - dip_center) / dip_width)**2)
coherent = coherent_base - dip
coherent = np.clip(coherent, 0, 1)

ax_c_left.plot(ri_c, coherent, color=COLORS['primary'], linewidth=3, label='Coherent fraction')

# Variability band around dip
band_mask = (ri_c >= 0.25) & (ri_c <= 0.55)
band_upper = coherent + 0.05 * band_mask
band_lower = coherent - 0.05 * band_mask
ax_c_left.fill_between(ri_c, band_lower, band_upper, where=band_mask, 
                       color=COLORS['secondary'], alpha=0.20)

setup_ri_axis(ax_c_left, label_pos='bottom')
ax_c_left.set_ylabel('Coherent fraction', fontsize=22, labelpad=8)
ax_c_left.set_ylim(0, 1)
ax_c_left.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax_c_left.tick_params(labelsize=16)
ax_c_left.grid(True, color='#E5E7EB', linewidth=0.8, alpha=0.8)

# Annotations
ax_c_left.annotate('stable: high\ncoherent fraction', xy=(1.6, 0.9), 
                  xytext=(1.3, 0.75), fontsize=18, ha='center',
                  arrowprops=dict(arrowstyle='->', lw=1.2, color='#1F2937'))
ax_c_left.annotate('marginal: additional\nloss & variability', xy=(0.4, 0.42), 
                  xytext=(0.7, 0.2), fontsize=18, ha='center',
                  arrowprops=dict(arrowstyle='->', lw=1.2, color='#1F2937'))

# Right: PSD broadening
omega_c = np.linspace(0.2, 2.2, 200)

# High Ri: narrow peak
psd_high = np.exp(-((omega_c - 1.0) / 0.15)**2)
psd_high /= psd_high.max()

# Marginal Ri: broader peak
psd_marginal = 0.7 * np.exp(-((omega_c - 1.0) / 0.35)**2) + \
               0.3 * np.exp(-((omega_c - 1.1) / 0.5)**2)
psd_marginal /= psd_marginal.max()
# Add raggedness
np.random.seed(123)
psd_marginal *= (1 + 0.08 * np.random.randn(len(omega_c)))
psd_marginal = np.clip(psd_marginal, 0, 1)

ax_c_right.plot(omega_c, psd_high, color=COLORS['primary'], linewidth=3, 
               linestyle='-', label=r'High $Ri$')
ax_c_right.plot(omega_c, psd_marginal, color=COLORS['secondary'], linewidth=3, 
               linestyle='--', label=r'Marginal $Ri$')

setup_omega_n_axis(ax_c_right, label_pos='bottom')
ax_c_right.set_ylabel('Normalized PSD', fontsize=22, labelpad=8)
ax_c_right.set_ylim(0, 1)
ax_c_right.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax_c_right.tick_params(labelsize=16)
ax_c_right.grid(True, color='#E5E7EB', linewidth=0.8, alpha=0.8)
add_conversion_band(ax_c_right, ri_range=(0, 1), orientation='vertical')

# Bandwidth arrows (optional)
# Find half-power points
def find_half_power(omega, psd):
    half_max = 0.5
    above = psd >= half_max
    if not any(above):
        return None, None
    indices = np.where(above)[0]
    return omega[indices[0]], omega[indices[-1]]

bw_high = find_half_power(omega_c, psd_high)
bw_marginal = find_half_power(omega_c, psd_marginal)

if bw_high[0] is not None:
    ax_c_right.annotate('', xy=(bw_high[1], 0.15), xytext=(bw_high[0], 0.15),
                       arrowprops=dict(arrowstyle='<->', lw=1.5, color=COLORS['primary']))
    ax_c_right.text((bw_high[0] + bw_high[1])/2, 0.18, 'BW', fontsize=16, 
                   ha='center', color=COLORS['primary'])

if bw_marginal[0] is not None:
    ax_c_right.annotate('', xy=(bw_marginal[1], 0.08), xytext=(bw_marginal[0], 0.08),
                       arrowprops=dict(arrowstyle='<->', lw=1.5, color=COLORS['secondary']))
    ax_c_right.text((bw_marginal[0] + bw_marginal[1])/2, 0.11, 'BW', fontsize=16, 
                   ha='center', color=COLORS['secondary'])

ax_c_right.text(1.7, 0.35, r'broader PSD under$\,$marginal $Ri$', fontsize=18, 
               ha='center', color='#1F2937')

ax_c_right.legend(loc='upper right', frameon=False, fontsize=18)

# Panel C title
fig.text(0.08, 0.335, r'Figure 3.6C — Coherence loss and spectral broadening with decreasing $Ri$', 
         fontsize=28, weight='bold', va='top')

# Caption beneath both subpanels
caption_c = (r"Coherent fraction declines monotonically with a superposed dip near marginal $Ri$; "
             r"spectra broaden under marginal $Ri$, indicating enhanced shear-mediated variability.")
fig.text(0.5, 0.03, caption_c, fontsize=15, style='italic', ha='center', va='bottom')

# ============================================================================
# Save combined figure
# ============================================================================
output_dir = '/workspace/out/figures'
import os
os.makedirs(output_dir, exist_ok=True)

plt.savefig(f'{output_dir}/figure_3_6_combined.png', dpi=DPI, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.savefig(f'{output_dir}/figure_3_6_combined.svg', bbox_inches='tight', 
            facecolor='white', edgecolor='none')

print(f"✓ Combined Figure 3.6 (A–C) saved to {output_dir}/")
print(f"  → figure_3_6_combined.png ({CANVAS_WIDTH_PX}×{COMBINED_HEIGHT} px)")
print(f"  → figure_3_6_combined.svg (vector)")
