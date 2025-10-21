#!/usr/bin/env python3
"""
Scientific Figures Generator for Shared House Style
Generates Figures 3.9A-D with precise styling specifications
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib import font_manager
import matplotlib.patheffects as path_effects
from matplotlib.colors import LinearSegmentedColormap
import os

# Set up the shared house style
class ScientificFigureStyle:
    def __init__(self):
        # Canvas specifications
        self.canvas_width = 2000
        self.canvas_height = 1400
        self.dpi = 300
        
        # Color palette
        self.colors = {
            'classical': '#6B7280',  # dark gray
            'conversion': '#F4A261',  # amber
            'conversion_dark': '#C06A00',  # darker amber for lines
            'interfacial': '#6A4C93',  # purple
            'shear': '#2A9D8F',  # teal
            'primary_tl': '#1F78B4',  # deep blue
            'conversion_window': '#F4A261',  # amber for overlay
            'grid': '#E5E7EB',  # light gray
            'centerline': '#9CA3AF',  # faint gray
            'steel_blue': '#4A90E2'  # steel blue for Ri
        }
        
        # Typography
        self.font_family = 'DejaVu Sans'  # Fallback to DejaVu Sans since Helvetica not available
        self.title_size = 28
        self.axis_label_size = 22
        self.tick_label_size = 16
        self.note_size = 18
        self.caption_size = 15
        self.legend_size = 16
        self.math_subscript_scale = 0.7
        
        # Line specifications
        self.line_weights = {
            'primary': 3,
            'secondary': 2.5,
            'dashed': 2,
            'dotted_guide': 1.2,
            'grid': 0.8
        }
        
        # Dash patterns
        self.dash_patterns = {
            'dashed': (8, 6),
            'dotted': (1, 3)
        }
        
        # Conversion window specifications
        self.conversion_window = {
            'omega_min': 0.8,
            'omega_max': 1.2,
            'opacity': 0.2,
            'centerline_omega': 1.0
        }
        
        # Set matplotlib style
        plt.rcParams.update({
            'font.family': [self.font_family, 'Arial', 'sans-serif'],
            'font.size': self.tick_label_size,
            'axes.linewidth': 1.5,
            'axes.spines.top': False,
            'axes.spines.right': False,
            'axes.grid': True,
            'grid.color': self.colors['grid'],
            'grid.linewidth': self.line_weights['grid'],
            'grid.alpha': 0.8,
            'figure.dpi': self.dpi,
            'savefig.dpi': self.dpi,
            'savefig.bbox': 'tight',
            'savefig.pad_inches': 0.1
        })
    
    def create_figure(self, title=""):
        """Create a new figure with the specified canvas size"""
        fig, ax = plt.subplots(figsize=(self.canvas_width/100, self.canvas_height/100))
        ax.set_facecolor('white')
        return fig, ax
    
    def setup_axes(self, ax, xlabel="", ylabel="", title="", xlim=None, ylim=None, 
                   x_ticks=None, y_ticks=None, grid=True):
        """Setup axes with consistent styling"""
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=self.axis_label_size, fontweight='bold')
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=self.axis_label_size, fontweight='bold')
        if title:
            ax.set_title(title, fontsize=self.title_size, fontweight='bold', pad=20)
        
        if xlim:
            ax.set_xlim(xlim)
        if ylim:
            ax.set_ylim(ylim)
        
        if x_ticks:
            ax.set_xticks(x_ticks)
        if y_ticks:
            ax.set_yticks(y_ticks)
        
        if grid:
            ax.grid(True, color=self.colors['grid'], linewidth=self.line_weights['grid'], alpha=0.8)
        
        # Style the axes
        ax.tick_params(axis='both', which='major', labelsize=self.tick_label_size)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(1.5)
        ax.spines['bottom'].set_linewidth(1.5)
    
    def add_conversion_window(self, ax, y_min, y_max):
        """Add the conversion window overlay"""
        # Translucent amber band
        rect = patches.Rectangle(
            (self.conversion_window['omega_min'], y_min),
            self.conversion_window['omega_max'] - self.conversion_window['omega_min'],
            y_max - y_min,
            linewidth=0,
            facecolor=self.colors['conversion_window'],
            alpha=self.conversion_window['opacity'],
            zorder=0
        )
        ax.add_patch(rect)
        
        # Dotted centerline
        ax.axvline(
            x=self.conversion_window['centerline_omega'],
            color=self.colors['centerline'],
            linestyle=':',
            linewidth=self.line_weights['dotted_guide'],
            zorder=1
        )
    
    def add_legend(self, ax, labels, colors, linestyles=None, location='best'):
        """Add a legend with consistent styling"""
        if linestyles is None:
            linestyles = ['-'] * len(labels)
        
        handles = []
        for i, (label, color, style) in enumerate(zip(labels, colors, linestyles)):
            handle = plt.Line2D([0], [0], color=color, linestyle=style, 
                              linewidth=self.line_weights['primary'])
            handles.append(handle)
        
        legend = ax.legend(handles, labels, loc=location, fontsize=self.legend_size,
                          frameon=False, fancybox=False, shadow=False)
        return legend
    
    def add_caption(self, fig, text, x=0.5, y=0.02):
        """Add caption text below the figure"""
        fig.text(x, y, text, fontsize=self.caption_size, style='italic',
                ha='center', va='bottom', transform=fig.transFigure)
    
    def save_figures(self, fig, filename_base):
        """Save figure in both PNG and PDF formats"""
        # Create output directory
        os.makedirs('output', exist_ok=True)
        
        # Save PNG
        png_path = f'output/{filename_base}.png'
        fig.savefig(png_path, dpi=self.dpi, format='png', bbox_inches='tight')
        print(f"Saved: {png_path}")
        
        # Save PDF
        pdf_path = f'output/{filename_base}.pdf'
        fig.savefig(pdf_path, format='pdf', bbox_inches='tight')
        print(f"Saved: {pdf_path}")

# Initialize the style
style = ScientificFigureStyle()

def create_figure_3_9a():
    """Figure 3.9A — Frequency sweep signatures"""
    print("Creating Figure 3.9A...")
    
    fig, ax = style.create_figure()
    
    # Frequency range
    omega_n = np.linspace(0.2, 2.2, 1000)
    
    # Classical baseline (dark gray dashed)
    classical_tl = 20 + 15 * (omega_n - 0.2) / 2.0  # Gently rising with frequency
    
    # Continuous stratification (deep blue solid with broad bump)
    # Create a Gaussian-like bump centered at omega/N = 1
    bump_center = 1.0
    bump_width = 0.3  # FWHM ≈ 0.6
    bump_amplitude = 7  # +6-8 dB above classical
    bump = bump_amplitude * np.exp(-0.5 * ((omega_n - bump_center) / bump_width) ** 2)
    continuous_tl = classical_tl + bump
    
    # Continuous + interfaces (purple with notches)
    # Add narrow notches (4-6 dips, 6-12 dB deep, 3-5% wide)
    notch_positions = np.array([0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7])
    notch_width = 0.05  # 3-5% of range
    notch_depth = 9  # 6-12 dB deep
    
    continuous_interfaces_tl = continuous_tl.copy()
    for pos in notch_positions:
        if 0.4 <= pos <= 1.8:  # Only in the specified range
            notch_mask = np.abs(omega_n - pos) < notch_width
            continuous_interfaces_tl[notch_mask] -= notch_depth * np.exp(-0.5 * ((omega_n[notch_mask] - pos) / (notch_width/3)) ** 2)
    
    # Plot the curves
    ax.plot(omega_n, classical_tl, color=style.colors['classical'], 
            linestyle='--', linewidth=style.line_weights['dashed'], label='classical')
    
    ax.plot(omega_n, continuous_tl, color=style.colors['primary_tl'], 
            linewidth=style.line_weights['primary'], label='continuous')
    
    ax.plot(omega_n, continuous_interfaces_tl, color=style.colors['interfacial'], 
            linewidth=style.line_weights['primary'], label='continuous + interfaces (notches)')
    
    # Add conversion window overlay
    style.add_conversion_window(ax, 20, 80)
    
    # Add double-headed arrow for notch spacing
    arrow_start = 0.9
    arrow_end = 1.1
    ax.annotate('', xy=(arrow_end, 45), xytext=(arrow_start, 45),
                arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
    ax.text(1.0, 47, r'$\Delta(\omega/N) \approx$ const.', 
            ha='center', va='bottom', fontsize=style.note_size)
    
    # Micro-labels
    ax.text(0.6, 35, 'conversion bump (continuous)', 
            ha='center', va='center', fontsize=style.note_size, 
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax.text(1.4, 25, 'interfacial comb\n(continuous + interfaces)', 
            ha='center', va='center', fontsize=style.note_size,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Setup axes
    style.setup_axes(ax, 
                    xlabel=r'$\omega/N$', 
                    ylabel='Transmission Loss (dB)',
                    xlim=(0.2, 2.2), 
                    ylim=(20, 80),
                    x_ticks=[0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0],
                    y_ticks=range(20, 81, 10))
    
    # Add legend
    style.add_legend(ax, 
                    ['classical', 'continuous', 'continuous + interfaces (notches)'],
                    [style.colors['classical'], style.colors['primary_tl'], style.colors['interfacial']],
                    ['--', '-', '-'])
    
    # Add caption
    caption = ("Figure 3.9A. Frequency-sweep signatures: a broad conversion bump at "
               r"$\omega/N \approx 1$ for continuous stratification; adding sharp interfaces "
               "imposes narrow spectral notches on top of the bump.")
    style.add_caption(fig, caption)
    
    # Save figures
    style.save_figures(fig, 'figure_3_9a')
    plt.close(fig)

def create_figure_3_9b():
    """Figure 3.9B — Angle–frequency plate"""
    print("Creating Figure 3.9B...")
    
    fig, ax = style.create_figure()
    
    # Create angle-frequency grid
    omega_n = np.linspace(0.2, 2.2, 200)
    theta = np.linspace(0, 80, 100)
    Omega, Theta = np.meshgrid(omega_n, theta)
    
    # Create notch trajectories that shift with angle
    # Higher order notches shift upward-right with angle
    tl_data = np.zeros_like(Omega)
    
    # Base conversion bump (horizontal, angle-independent)
    bump_center = 1.0
    bump_width = 0.3
    conversion_bump = np.exp(-0.5 * ((Omega - bump_center) / bump_width) ** 2)
    tl_data += 0.3 * conversion_bump
    
    # Add notch trajectories that shift with angle
    # Create multiple notch families
    notch_families = [
        {'base_omega': 0.6, 'angle_shift': 0.002, 'width': 0.05, 'strength': 0.8},
        {'base_omega': 0.8, 'angle_shift': 0.0015, 'width': 0.04, 'strength': 0.9},
        {'base_omega': 1.0, 'angle_shift': 0.001, 'width': 0.03, 'strength': 1.0},
        {'base_omega': 1.2, 'angle_shift': 0.0008, 'width': 0.04, 'strength': 0.9},
        {'base_omega': 1.4, 'angle_shift': 0.0006, 'width': 0.05, 'strength': 0.8},
        {'base_omega': 1.6, 'angle_shift': 0.0004, 'width': 0.06, 'strength': 0.7}
    ]
    
    for family in notch_families:
        # Notch position shifts with angle
        notch_omega = family['base_omega'] + family['angle_shift'] * Theta
        notch_mask = (Omega >= family['base_omega'] - 0.2) & (Omega <= family['base_omega'] + 0.8)
        notch_strength = family['strength'] * np.exp(-0.5 * ((Omega - notch_omega) / family['width']) ** 2)
        tl_data += notch_strength * notch_mask
    
    # Create heatmap
    im = ax.imshow(tl_data, extent=[0.2, 2.2, 0, 80], aspect='auto', 
                   cmap='viridis', origin='lower', interpolation='bilinear')
    
    # Add conversion band overlay
    rect = patches.Rectangle((0.8, 0), 0.4, 80, linewidth=0,
                           facecolor=style.colors['conversion_window'],
                           alpha=0.3, zorder=1)
    ax.add_patch(rect)
    
    # Add dotted centerline
    ax.axvline(x=1.0, color=style.colors['centerline'], linestyle=':',
               linewidth=style.line_weights['dotted_guide'], zorder=2)
    
    # Add horizontal ruler arrow
    ax.annotate('', xy=(1.2, 75), xytext=(0.8, 75),
                arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
    ax.text(1.0, 77, 'conversion band (angle-independent)', 
            ha='center', va='bottom', fontsize=style.note_size)
    
    # Annotate one filament
    ax.annotate('interface-induced notch\nshifts with θ', 
                xy=(1.3, 40), xytext=(1.5, 30),
                arrowprops=dict(arrowstyle='->', color='white', lw=2),
                fontsize=style.note_size, color='white',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))
    
    # Setup axes
    style.setup_axes(ax,
                    xlabel=r'$\omega/N$',
                    ylabel=r'$\theta$ (degrees)',
                    xlim=(0.2, 2.2),
                    ylim=(0, 80),
                    x_ticks=[0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0],
                    y_ticks=[0, 15, 30, 45, 60, 75, 80])
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=20)
    cbar.set_label('TL (arb.)', fontsize=style.axis_label_size, fontweight='bold')
    cbar.ax.tick_params(labelsize=style.tick_label_size)
    
    # Add caption
    caption = ("Figure 3.9B. Angle–frequency plate: interface-induced notches shift with angle, "
               "while the conversion band remains centered at " + r"$\omega/N \approx 1$.")
    style.add_caption(fig, caption)
    
    # Save figures
    style.save_figures(fig, 'figure_3_9b')
    plt.close(fig)

def create_figure_3_9c():
    """Figure 3.9C — Time correlation"""
    print("Creating Figure 3.9C...")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(style.canvas_width/100, style.canvas_height/100),
                                   gridspec_kw={'height_ratios': [1, 1], 'hspace': 0.1})
    fig.patch.set_facecolor('white')
    
    # Time range
    time = np.linspace(0, 60, 1000)
    
    # Generate Ri(t) with low-Ri bursts
    ri_base = 0.8 + 0.3 * np.sin(2 * np.pi * time / 20)  # Base oscillation
    ri_bursts = np.zeros_like(time)
    
    # Add low-Ri bursts at specific times
    burst_times = [15, 25, 35, 45, 55]
    for burst_time in burst_times:
        burst_mask = np.abs(time - burst_time) < 3
        ri_bursts[burst_mask] = -0.4 * np.exp(-0.5 * ((time[burst_mask] - burst_time) / 1.5) ** 2)
    
    ri_data = ri_base + ri_bursts
    ri_data = np.clip(ri_data, 0, 2)  # Clip to 0-2 range
    
    # Generate coherence data
    coherence_base = 0.95 + 0.03 * np.sin(2 * np.pi * time / 15)  # High baseline with small oscillations
    
    # Add conversion dip (persistent trough)
    conversion_dip = 0.2 * np.exp(-0.5 * ((time - 30) / 8) ** 2)  # Dip around t=30
    coherence_data = coherence_base - conversion_dip
    
    # Add sharp drops aligned with low-Ri events
    for burst_time in burst_times:
        drop_mask = np.abs(time - burst_time) < 2
        coherence_data[drop_mask] -= 0.3 * np.exp(-0.5 * ((time[drop_mask] - burst_time) / 0.8) ** 2)
    
    coherence_data = np.clip(coherence_data, 0, 1)  # Clip to 0-1 range
    
    # Plot coherence (top panel)
    ax1.plot(time, coherence_data, color=style.colors['primary_tl'], 
             linewidth=style.line_weights['primary'], label=r'$\gamma^2(t)$')
    
    # Mark low-Ri bursts with vertical bands
    for burst_time in burst_times:
        if ri_data[np.argmin(np.abs(time - burst_time))] < 0.5:
            ax1.axvspan(burst_time - 1.5, burst_time + 1.5, 
                       color=style.colors['shear'], alpha=0.3, zorder=0)
            # Extend to top panel
            ax1.axvline(x=burst_time, color=style.colors['shear'], 
                       linestyle='--', alpha=0.5, linewidth=1)
    
    # Add micro-labels
    ax1.text(30, 0.3, 'conversion-band dip', ha='center', va='center',
             fontsize=style.note_size, bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax1.text(25, 0.1, 'low-Ri burst', ha='center', va='center',
             fontsize=style.note_size, bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Setup top panel
    style.setup_axes(ax1, ylabel=r'$\gamma^2(t)$', ylim=(0, 1),
                    y_ticks=[0, 0.25, 0.5, 0.75, 1.0])
    ax1.set_xticks([])  # Remove x-axis labels for top panel
    
    # Plot Ri(t) (bottom panel)
    ax2.plot(time, ri_data, color=style.colors['steel_blue'], 
             linewidth=style.line_weights['primary'], label=r'$Ri(t)$')
    
    # Mark low-Ri episodes with translucent teal bands
    for burst_time in burst_times:
        if ri_data[np.argmin(np.abs(time - burst_time))] < 0.5:
            ax2.axvspan(burst_time - 1.5, burst_time + 1.5, 
                       color=style.colors['shear'], alpha=0.3, zorder=0)
    
    # Setup bottom panel
    style.setup_axes(ax2, xlabel='Time (s)', ylabel=r'$Ri(t)$',
                    xlim=(0, 60), ylim=(0, 2),
                    x_ticks=range(0, 61, 10),
                    y_ticks=[0, 0.25, 0.5, 0.7, 1, 1.5, 2])
    
    # Add caption
    caption = ("Figure 3.9C. Time correlation between array coherence and " + r"$Ri(t)$: "
               "a persistent conversion-band dip plus intermittent losses coincident with low-" + r"$Ri$ bursts.")
    style.add_caption(fig, caption)
    
    # Save figures
    style.save_figures(fig, 'figure_3_9c')
    plt.close(fig)

def create_figure_3_9d():
    """Figure 3.9D — Mechanism-share waterfall"""
    print("Creating Figure 3.9D...")
    
    fig, ax = style.create_figure()
    
    # Define the four regimes and their shares
    regimes = ['High-Ri\ncontinuous', 'Marginal-Ri\ncontinuous', 'Layered\nsharp', 'Layered\ndiffuse']
    
    # Target shares (bottom to top in stack)
    shares = {
        'classical': [0.40, 0.30, 0.25, 0.45],      # Gray (bottom)
        'conversion': [0.50, 0.40, 0.20, 0.30],     # Amber
        'interfacial': [0.05, 0.05, 0.50, 0.15],    # Purple
        'shear': [0.05, 0.25, 0.05, 0.10]           # Teal (top)
    }
    
    colors = [style.colors['classical'], style.colors['conversion'], 
              style.colors['interfacial'], style.colors['shear']]
    
    # Create stacked bars
    x_pos = np.arange(len(regimes))
    width = 0.6
    
    # Plot stacked bars
    bottom = np.zeros(len(regimes))
    bars = []
    
    for i, (mechanism, color) in enumerate(zip(['classical', 'conversion', 'interfacial', 'shear'], colors)):
        bar = ax.bar(x_pos, shares[mechanism], width, bottom=bottom, 
                    color=color, edgecolor='white', linewidth=0.5, label=mechanism)
        bars.append(bar)
        
        # Add value labels in each segment
        for j, (x, y, share) in enumerate(zip(x_pos, bottom + np.array(shares[mechanism])/2, shares[mechanism])):
            if share > 0.08:  # Only label if segment is large enough
                ax.text(x, y, f'{share:.2f}', ha='center', va='center', 
                       fontsize=12, fontweight='bold', color='white' if share > 0.3 else 'black')
        
        bottom += shares[mechanism]
    
    # Setup axes
    style.setup_axes(ax, xlabel='Regime', ylabel='Share',
                    ylim=(0, 1), y_ticks=[0, 0.25, 0.5, 0.75, 1.0])
    
    # Set x-axis labels
    ax.set_xticks(x_pos)
    ax.set_xticklabels(regimes, rotation=0, fontsize=style.tick_label_size)
    
    # Add legend
    legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color, label=mechanism) 
                      for mechanism, color in zip(['Classical', 'Conversion', 'Interfacial', 'Shear'], colors)]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=style.legend_size,
             frameon=False, fancybox=False, shadow=False)
    
    # Add title
    ax.text(0.5, 1.05, 'Figure 3.9D — Mechanism-share waterfall (four canonical regimes)',
            transform=ax.transAxes, ha='center', va='bottom', 
            fontsize=style.title_size, fontweight='bold')
    
    # Add caption
    caption = ("Figure 3.9D. Mechanism shares (summing to unity) for four regimes: "
               "conversion dominates high-Ri continuous; shear rises under marginal Ri; "
               "interfacial loss peaks for layered sharp and weakens for layered diffuse.")
    style.add_caption(fig, caption)
    
    # Save figures
    style.save_figures(fig, 'figure_3_9d')
    plt.close(fig)

def main():
    """Generate all figures"""
    print("Generating scientific figures with shared house style...")
    print(f"Canvas size: {style.canvas_width} × {style.canvas_height} px")
    print(f"Output DPI: {style.dpi}")
    print()
    
    # Create all figures
    create_figure_3_9a()
    create_figure_3_9b()
    create_figure_3_9c()
    create_figure_3_9d()
    
    print("\nAll figures generated successfully!")
    print("Files saved in 'output/' directory:")
    print("- figure_3_9a.png/pdf")
    print("- figure_3_9b.png/pdf") 
    print("- figure_3_9c.png/pdf")
    print("- figure_3_9d.png/pdf")

if __name__ == "__main__":
    main()