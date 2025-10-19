#!/usr/bin/env python3
"""
Figure 3.5B - Transmission vs frequency for three regimes
Shows how finite thickness and contrast control spectral structure of transmission
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

# Set up the figure with house style
plt.style.use('default')
fig, ax = plt.subplots(figsize=(20, 14))  # 2000x1400 px at 100 dpi
fig.patch.set_facecolor('white')

# House style colors
colors = {
    'primary_blue': '#1F78B4',
    'steel_blue': '#457B9D', 
    'magenta': '#B3007D',
    'orange': '#F05A28',
    'teal': '#2A9D8F',
    'dark_gray': '#555555',
    'light_gray': '#E5E7EB',
    'amber': '#F4A261',
    'gray_guide': '#9CA3AF'
}

# Font settings
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 16,
    'axes.linewidth': 2,
    'lines.linewidth': 3,
    'lines.solid_capstyle': 'round',
    'patch.linewidth': 2,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'axes.labelsize': 22,
    'axes.titlesize': 28
})

# Set up axes
omega_N = np.linspace(0.2, 3.5, 1000)
ax.set_xlim(0.2, 3.5)
ax.set_ylim(0, 1)

# X-axis ticks and labels
x_ticks = [0.2, 0.5, 0.8, 1.0, 1.2, 2.0, 3.0]
ax.set_xticks(x_ticks)
ax.set_xticklabels([f'{x:.1f}' for x in x_ticks])
ax.set_xlabel(r'$\omega/N$', fontsize=22, fontweight='bold')

# Y-axis ticks and labels
y_ticks = np.arange(0, 1.1, 0.1)
ax.set_yticks(y_ticks)
ax.set_ylabel(r'Transmissivity $|T|^2$', fontsize=22, fontweight='bold')

# Grid
ax.grid(True, color=colors['light_gray'], linewidth=0.8, alpha=0.8)
ax.set_axisbelow(True)

# Conversion window band (0.8 ≤ ω/N ≤ 1.2)
conversion_rect = Rectangle((0.8, 0), 0.4, 1, facecolor=colors['amber'], alpha=0.2, zorder=1)
ax.add_patch(conversion_rect)

# Dotted centerline at ω/N = 1
ax.axvline(x=1.0, color=colors['gray_guide'], linestyle=':', linewidth=1, alpha=0.8, zorder=2)

# Generate transmission curves for three regimes

def generate_transmission_curve(omega_N, regime='sharp'):
    """Generate transmission curves with realistic spectral features"""
    
    # Base envelope (general frequency dependence)
    base_envelope = 0.85 - 0.15 * np.exp(-(omega_N - 1.0)**2 / 0.5)
    
    if regime == 'sharp':
        # Sharp/high-contrast: frequent, deep notches
        # Create quasi-periodic notches with varying depth and spacing
        transmission = base_envelope.copy()
        
        # Define notch centers (quasi-periodic spacing)
        notch_centers = []
        omega_current = 0.4
        while omega_current < 3.3:
            notch_centers.append(omega_current)
            # Spacing increases slightly with frequency
            delta_omega = 0.15 + 0.02 * omega_current
            omega_current += delta_omega
        
        # Add notches
        for center in notch_centers:
            if 0.2 <= center <= 3.5:
                # Notch depth varies (0.25 to 0.6 reduction in |T|²)
                depth = 0.3 + 0.3 * np.random.random()
                # Notch width (narrow, few % of center frequency)
                width = 0.03 * center + 0.01
                
                # Gaussian-like notch
                notch = depth * np.exp(-((omega_N - center) / width)**2)
                transmission -= notch
        
        # Ensure transmission stays in [0, 1]
        transmission = np.clip(transmission, 0, 1)
        
    elif regime == 'moderate':
        # Moderate: shallower, less frequent notches
        transmission = base_envelope.copy()
        
        # Fewer notch centers
        notch_centers = [0.5, 0.8, 1.1, 1.5, 2.0, 2.6, 3.1]
        
        for center in notch_centers:
            if 0.2 <= center <= 3.5:
                # Shallower notches
                depth = 0.15 + 0.15 * np.random.random()
                width = 0.05 * center + 0.02
                
                notch = depth * np.exp(-((omega_N - center) / width)**2)
                transmission -= notch
        
        transmission = np.clip(transmission, 0, 1)
        
    else:  # diffuse
        # Diffuse/low-contrast: weak, broad ripples
        transmission = base_envelope.copy()
        
        # Add gentle undulations
        ripple1 = 0.03 * np.sin(2 * np.pi * omega_N / 0.8)
        ripple2 = 0.02 * np.sin(2 * np.pi * omega_N / 1.3 + np.pi/3)
        ripple3 = 0.015 * np.sin(2 * np.pi * omega_N / 2.1 + np.pi/6)
        
        transmission += ripple1 + ripple2 + ripple3
        transmission = np.clip(transmission, 0, 1)
    
    return transmission

# Set random seed for reproducible results
np.random.seed(42)

# Generate the three curves
sharp_transmission = generate_transmission_curve(omega_N, 'sharp')
moderate_transmission = generate_transmission_curve(omega_N, 'moderate')
diffuse_transmission = generate_transmission_curve(omega_N, 'diffuse')

# Plot the curves
line_sharp = ax.plot(omega_N, sharp_transmission, color=colors['magenta'], linewidth=3, 
                    label='Sharp / high-contrast', zorder=5)
line_moderate = ax.plot(omega_N, moderate_transmission, color=colors['primary_blue'], linewidth=3, 
                       label='Moderate', zorder=4)
line_diffuse = ax.plot(omega_N, diffuse_transmission, color=colors['teal'], linewidth=3, 
                      label='Diffuse / low-contrast', zorder=3)

# Add homogeneous baseline (optional reference)
baseline = 0.8 * np.ones_like(omega_N)
ax.plot(omega_N, baseline, color=colors['dark_gray'], linestyle='--', linewidth=2, 
        alpha=0.7, label='Homogeneous baseline', zorder=2)

# Add spacing indicator between adjacent sharp notches
# Find two adjacent notches in the sharp curve for the arrow
sharp_minima = []
for i in range(1, len(sharp_transmission)-1):
    if (sharp_transmission[i] < sharp_transmission[i-1] and 
        sharp_transmission[i] < sharp_transmission[i+1] and
        sharp_transmission[i] < 0.6):  # Only significant minima
        sharp_minima.append((omega_N[i], sharp_transmission[i]))

# Select two adjacent minima for the arrow
if len(sharp_minima) >= 2:
    # Find a good pair in the middle range
    for i in range(len(sharp_minima)-1):
        if 1.0 <= sharp_minima[i][0] <= 2.5:
            x1, y1 = sharp_minima[i]
            x2, y2 = sharp_minima[i+1]
            
            # Draw double-headed arrow above the curve
            arrow_y = max(y1, y2) + 0.15
            ax.annotate('', xy=(x1, arrow_y), xytext=(x2, arrow_y),
                       arrowprops=dict(arrowstyle='<->', color='black', lw=2))
            
            # Add label
            mid_x = (x1 + x2) / 2
            ax.text(mid_x, arrow_y + 0.05, r'$\Delta(\omega/N) \approx$ const.', 
                   ha='center', va='bottom', fontsize=16, fontweight='bold')
            break

# Legend
legend_elements = [
    mpatches.Patch(color=colors['magenta'], label='Sharp / high-contrast'),
    mpatches.Patch(color=colors['primary_blue'], label='Moderate'), 
    mpatches.Patch(color=colors['teal'], label='Diffuse / low-contrast'),
    mpatches.Patch(color=colors['amber'], alpha=0.4, label='Conversion window'),
    mpatches.Patch(color=colors['dark_gray'], label='Homogeneous baseline')
]

legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=16, 
                  frameon=False, bbox_to_anchor=(0.98, 0.98))

# Set axes properties
ax.spines['top'].set_linewidth(2)
ax.spines['right'].set_linewidth(2)
ax.spines['bottom'].set_linewidth(2)
ax.spines['left'].set_linewidth(2)

# Caption
fig.text(0.5, 0.02, 
         'Figure 3.5B. Transmissivity vs normalized frequency across interface regimes. Sharp, high-contrast layers exhibit deep, frequent notches; moderate layers show gentler quasi-periodic structure; diffuse/low-contrast layers are nearly smooth.',
         fontsize=15, ha='center', style='italic', wrap=True)

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(bottom=0.1)

# Save figure
plt.savefig('/workspace/figure_3_5b.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('/workspace/figure_3_5b.pdf', bbox_inches='tight', facecolor='white')
plt.savefig('/workspace/figure_3_5b.svg', bbox_inches='tight', facecolor='white')

print("Figure 3.5B created successfully!")
plt.show()