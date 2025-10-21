#!/usr/bin/env python3
"""
Figure 3.8C — Qualitative scaling of apparent attenuation vs ω/N at selected Ri
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set up the figure with the specified style
plt.rcParams['font.family'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['font.size'] = 16
plt.rcParams['axes.linewidth'] = 1.0

# Create figure with specified dimensions (2000x1400 px)
fig, ax = plt.subplots(figsize=(20, 14), dpi=100)
fig.patch.set_facecolor('white')

# Define frequency range
omega_N = np.linspace(0.2, 2.2, 1000)

# Define the four Ri values and their properties
Ri_values = [1.5, 1.0, 0.6, 0.3]
colors = ['#1e3a8a', '#0f766e', '#2A9D8F', '#B3007D']  # deep blue, steel blue, teal, magenta
linestyles = ['-', '-', '-', '--']
labels = [f'$R_i = {ri}$' for ri in Ri_values]

def transmission_loss(omega_N, Ri):
    """
    Synthetic transmission loss function
    As Ri decreases: peak widens, gets lower, broadband skirts rise
    """
    # Base conversion peak centered at omega/N = 1
    peak_center = 1.0
    
    # Peak characteristics depend on Ri
    if Ri >= 1.5:
        # Narrow peak, high coherence elsewhere, minimal skirts
        peak_width = 0.15
        peak_height = 65
        baseline = 25
        skirt_strength = 0.5
    elif Ri >= 1.0:
        # Slightly broader peak, mild skirts
        peak_width = 0.20
        peak_height = 60
        baseline = 28
        skirt_strength = 2.0
    elif Ri >= 0.6:
        # Significantly broader peak, elevated skirts
        peak_width = 0.30
        peak_height = 52
        baseline = 32
        skirt_strength = 5.0
    else:  # Ri = 0.3
        # Flattish dome, prominent broadband shoulders
        peak_width = 0.45
        peak_height = 45
        baseline = 38
        skirt_strength = 8.0
    
    # Main conversion peak (Gaussian-like)
    main_peak = peak_height * np.exp(-((omega_N - peak_center)**2) / (2 * peak_width**2))
    
    # Broadband skirts (elevated loss away from peak)
    # More pronounced for lower Ri
    skirt_left = skirt_strength * np.exp(-((omega_N - 0.7)**2) / (2 * 0.3**2))
    skirt_right = skirt_strength * np.exp(-((omega_N - 1.4)**2) / (2 * 0.4**2))
    
    # Additional broadband elevation for very low Ri
    if Ri <= 0.6:
        broadband_floor = 3 * (0.6 - Ri) / 0.6  # Increases as Ri decreases
    else:
        broadband_floor = 0
    
    TL = baseline + main_peak + skirt_left + skirt_right + broadband_floor
    
    return TL

# Plot the curves
for i, (Ri, color, linestyle, label) in enumerate(zip(Ri_values, colors, linestyles, labels)):
    TL = transmission_loss(omega_N, Ri)
    ax.plot(omega_N, TL, color=color, linewidth=3, linestyle=linestyle, label=label)

# Add conversion window overlay (translucent amber for 0.8 ≤ ω/N ≤ 1.2)
conversion_band = patches.Rectangle((0.8, 20), 0.4, 60, 
                                   facecolor='#F4A261', alpha=0.2, zorder=1)
ax.add_patch(conversion_band)

# Add faint dotted centerline at ω/N = 1
ax.axvline(x=1.0, color='#9CA3AF', linewidth=1.2, linestyle=':', zorder=2)

# Set up axes
ax.set_xlim(0.2, 2.2)
ax.set_ylim(20, 80)

# Set ticks according to specifications
omega_ticks = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
TL_ticks = np.arange(20, 81, 10)

ax.set_xticks(omega_ticks)
ax.set_yticks(TL_ticks)

# Labels with proper formatting
ax.set_xlabel(r'$\omega/N$', fontsize=22, fontweight='normal')
ax.set_ylabel('Apparent attenuation (dB)', fontsize=22, fontweight='normal')

# Tick label formatting
ax.tick_params(axis='both', which='major', labelsize=16, width=1.0, length=6)
for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontweight('normal')

# Grid (light gray, major ticks only)
ax.grid(True, color='#E5E7EB', linewidth=0.8, alpha=1.0, zorder=0)
ax.set_axisbelow(True)

# Add arrow annotations
# "peak widens as Ri↓"
ax.annotate('peak widens as $R_i \\downarrow$', 
            xy=(1.0, 65), xytext=(1.4, 70),
            arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
            fontsize=18, ha='center', va='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='none'))

# "skirts grow (broadband loss)"
ax.annotate('skirts grow\n(broadband loss)', 
            xy=(0.6, 40), xytext=(0.4, 50),
            arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
            fontsize=18, ha='center', va='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='none'))

ax.annotate('', xy=(1.6, 45), xytext=(1.8, 55),
            arrowprops=dict(arrowstyle='->', color='black', lw=1.5))

# Legend (inside axes, frame off)
legend = ax.legend(loc='upper right', frameon=False, fontsize=18)
for text in legend.get_texts():
    text.set_fontweight('normal')

# Title
ax.set_title('Figure 3.8C', fontsize=28, fontweight='bold', pad=20)

# Caption (positioned below x-axis)
caption_text = ('Figure 3.8C. Apparent attenuation vs $\\omega/N$ for selected $R_i$. '
                'Decreasing $R_i$ broadens the conversion peak and raises broadband skirts.')

fig.text(0.1, 0.02, caption_text, fontsize=15, style='italic', wrap=True, 
         ha='left', va='bottom', transform=fig.transFigure)

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(bottom=0.12)  # Make room for caption

# Save the figure
plt.savefig('/workspace/figure_3_8c.pdf', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.savefig('/workspace/figure_3_8c.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')

print("Figure 3.8C created successfully!")
plt.show()