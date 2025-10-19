"""
Shared house style for publication-quality figures.
Canvas: 1800 × 1200 px (landscape), white background.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Canvas dimensions (1800 × 1200 px)
CANVAS_WIDTH = 1800
CANVAS_HEIGHT = 1200
DPI = 150  # 1800/12 = 150 DPI for 12-inch width

# Typography
FONT_FAMILY = ['Helvetica', 'Arial', 'DejaVu Sans', 'sans-serif']
FONT_SIZES = {
    'panel_title': 28,
    'axis_label': 22,
    'tick_label': 16,
    'in_plot_note': 18,
    'caption': 15,
    'subscript_scale': 0.7
}

# Grid settings
GRID_COLOR = '#E5E7EB'
GRID_LINEWIDTH = 0.8

# Color palette (color-blind robust)
COLORS = {
    'deep_blue': '#1F78B4',
    'steel_blue': '#457B9D', 
    'contrast_magenta': '#B3007D',
    'conversion_amber': '#F4A261',
    'conversion_alpha': 0.2,
    'centerline_gray': '#9CA3AF',
    'uncertainty_alpha': 0.25
}

# Common axis ranges and ticks
OMEGA_N_RANGE = (0.2, 2.2)
OMEGA_N_TICKS = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
RI_RANGE = (0.0, 2.0)
RI_TICKS = [0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0]

# Conversion window
CONVERSION_WINDOW = (0.8, 1.2)
CONVERSION_CENTER = 1.0


def setup_figure(figsize_inches=None):
    """Setup figure with house style."""
    if figsize_inches is None:
        figsize_inches = (CANVAS_WIDTH/DPI, CANVAS_HEIGHT/DPI)
    
    # Set global font properties
    mpl.rcParams.update({
        'font.family': FONT_FAMILY,
        'font.size': FONT_SIZES['tick_label'],
        'axes.labelsize': FONT_SIZES['axis_label'],
        'axes.titlesize': FONT_SIZES['panel_title'],
        'xtick.labelsize': FONT_SIZES['tick_label'],
        'ytick.labelsize': FONT_SIZES['tick_label'],
        'legend.fontsize': FONT_SIZES['tick_label'],
        'figure.titlesize': FONT_SIZES['panel_title'],
        'axes.grid': True,
        'grid.color': GRID_COLOR,
        'grid.linewidth': GRID_LINEWIDTH,
        'axes.axisbelow': True,
        'legend.frameon': False,
        'figure.facecolor': 'white',
        'axes.facecolor': 'white'
    })
    
    fig = plt.figure(figsize=figsize_inches, dpi=DPI, facecolor='white')
    return fig


def setup_omega_n_axis(ax, label=True):
    """Setup normalized frequency axis with common range and ticks."""
    ax.set_xlim(OMEGA_N_RANGE)
    ax.set_xticks(OMEGA_N_TICKS)
    if label:
        ax.set_xlabel(r'$\omega/N$', fontsize=FONT_SIZES['axis_label'])


def setup_ri_axis(ax, label=True):
    """Setup Richardson number axis with common range and ticks."""
    ax.set_ylim(RI_RANGE)
    ax.set_yticks(RI_TICKS)
    if label:
        ax.set_ylabel(r'$R_i$', fontsize=FONT_SIZES['axis_label'])


def add_conversion_window(ax, alpha=None):
    """Add translucent amber conversion window overlay."""
    if alpha is None:
        alpha = COLORS['conversion_alpha']
    
    # Amber band
    ax.axvspan(CONVERSION_WINDOW[0], CONVERSION_WINDOW[1], 
              color=COLORS['conversion_amber'], alpha=alpha, zorder=0)
    
    # Dotted centerline
    ax.axvline(CONVERSION_CENTER, color=COLORS['centerline_gray'], 
              linestyle=':', linewidth=1, zorder=1)


def add_panel_title(ax, title, loc='upper left'):
    """Add panel title inside axes."""
    ax.text(0.02, 0.98, title, transform=ax.transAxes, 
           fontsize=FONT_SIZES['panel_title'], fontweight='bold',
           verticalalignment='top', horizontalalignment='left')


def add_caption(fig, caption, y_offset=0.02):
    """Add italic caption below x-axis."""
    fig.text(0.5, y_offset, caption, ha='center', va='bottom',
            fontsize=FONT_SIZES['caption'], style='italic')


def get_cividis_reversed():
    """Get Cividis colormap with darker = higher intensity."""
    return plt.cm.cividis_r


def add_colorbar(fig, mappable, label, ticks=None, ax_position=None):
    """Add colorbar with house style."""
    if ax_position is None:
        # Default position on right side
        cbar = fig.colorbar(mappable, ax=fig.axes, shrink=0.8, pad=0.02)
    else:
        cbar = fig.colorbar(mappable, ax=ax_position, shrink=0.8, pad=0.02)
    
    cbar.set_label(label, fontsize=FONT_SIZES['axis_label'])
    if ticks is not None:
        cbar.set_ticks(ticks)
    
    return cbar


def save_figure(fig, filename_base, output_dir='../out/figures'):
    """Save figure in PNG and SVG formats."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Save PNG with exact pixel dimensions
    png_path = f"{output_dir}/{filename_base}.png"
    fig.savefig(png_path, dpi=DPI, bbox_inches='tight', 
               facecolor='white', edgecolor='none')
    
    # Save SVG for vector graphics
    svg_path = f"{output_dir}/{filename_base}.svg"
    fig.savefig(svg_path, format='svg', bbox_inches='tight',
               facecolor='white', edgecolor='none')
    
    print(f"Saved: {png_path} and {svg_path}")
    return png_path, svg_path


def add_marginal_stability_line(ax, ri_value=0.25, label="marginal stability"):
    """Add horizontal dashed line for marginal stability."""
    ax.axhline(ri_value, color=COLORS['centerline_gray'], 
              linestyle='--', linewidth=1, alpha=0.7)
    
    # Add label
    ax.text(OMEGA_N_RANGE[1] * 0.95, ri_value + 0.05, label,
           fontsize=FONT_SIZES['in_plot_note'] - 2,
           ha='right', va='bottom', alpha=0.8)