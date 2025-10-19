"""
Shared house style for Figures 3.6A–C
Canvas: 1800 × 1200 px (landscape), white background
Typography: Helvetica/Arial with specified point sizes
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Canvas and DPI settings for exact 1800×1200 px output
CANVAS_WIDTH_PX = 1800
CANVAS_HEIGHT_PX = 1200
DPI = 150  # 1800/12 = 150 for 12-inch figure width

# Typography (point sizes)
PANEL_TITLE_SIZE = 28
AXIS_LABEL_SIZE = 22
TICK_LABEL_SIZE = 16
INPLOT_NOTE_SIZE = 18
CAPTION_SIZE = 15
SUBSCRIPT_SCALE = 0.7

# Colors
GRID_COLOR = '#E5E7EB'
GRID_LINEWIDTH = 0.8

# Conversion window
CONVERSION_BAND_COLOR = '#F4A261'
CONVERSION_BAND_ALPHA = 0.2
CONVERSION_CENTER_COLOR = '#9CA3AF'
CONVERSION_CENTER_LINEWIDTH = 1.0

# Color palette
DEEP_BLUE = '#1F78B4'
STEEL_BLUE = '#457B9D'
CONTRAST_MAGENTA = '#B3007D'

# Common axis ranges
OMEGA_N_RANGE = (0.2, 2.2)
OMEGA_N_TICKS = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
RI_RANGE = (0.0, 2.0)
RI_TICKS = [0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0]

def setup_figure(width_inch=12, height_inch=8):
    """Create figure with exact pixel dimensions and house style."""
    fig = plt.figure(figsize=(width_inch, height_inch), dpi=DPI, facecolor='white')
    
    # Set font
    plt.rcParams.update({
        'font.family': ['Helvetica', 'Arial', 'sans-serif'],
        'font.size': TICK_LABEL_SIZE,
        'axes.labelsize': AXIS_LABEL_SIZE,
        'axes.titlesize': PANEL_TITLE_SIZE,
        'xtick.labelsize': TICK_LABEL_SIZE,
        'ytick.labelsize': TICK_LABEL_SIZE,
        'legend.fontsize': INPLOT_NOTE_SIZE,
        'axes.grid': True,
        'grid.color': GRID_COLOR,
        'grid.linewidth': GRID_LINEWIDTH,
        'axes.axisbelow': True,
        'legend.frameon': False,
    })
    
    return fig

def setup_omega_n_axis(ax, show_xlabel=True):
    """Configure ω/N axis with standard range and ticks."""
    ax.set_xlim(OMEGA_N_RANGE)
    ax.set_xticks(OMEGA_N_TICKS)
    if show_xlabel:
        ax.set_xlabel('ω/N', fontsize=AXIS_LABEL_SIZE)

def setup_ri_axis(ax, show_ylabel=True):
    """Configure Ri axis with standard range and ticks."""
    ax.set_ylim(RI_RANGE)
    ax.set_yticks(RI_TICKS)
    if show_ylabel:
        ax.set_ylabel('$R_i$', fontsize=AXIS_LABEL_SIZE)

def add_conversion_window(ax):
    """Add amber conversion band and dotted centerline."""
    # Amber band
    band = patches.Rectangle((0.8, RI_RANGE[0]), 0.4, RI_RANGE[1] - RI_RANGE[0],
                           facecolor=CONVERSION_BAND_COLOR, alpha=CONVERSION_BAND_ALPHA,
                           edgecolor='none', zorder=1)
    ax.add_patch(band)
    
    # Dotted centerline at ω/N = 1
    ax.axvline(x=1.0, color=CONVERSION_CENTER_COLOR, linewidth=CONVERSION_CENTER_LINEWIDTH,
               linestyle=':', zorder=2)

def add_panel_title(ax, title, loc='upper left'):
    """Add panel title inside axes."""
    ax.text(0.02, 0.98, title, transform=ax.transAxes, fontsize=PANEL_TITLE_SIZE,
            fontweight='bold', verticalalignment='top', horizontalalignment='left')

def add_caption(ax, caption):
    """Add caption below x-axis."""
    ax.text(0.5, -0.15, caption, transform=ax.transAxes, fontsize=CAPTION_SIZE,
            style='italic', horizontalalignment='center', verticalalignment='top')

def add_colorbar(fig, im, ax, label, ticks=None):
    """Add colorbar with house style."""
    cbar = fig.colorbar(im, ax=ax, shrink=0.8, aspect=30)
    cbar.set_label(label, fontsize=AXIS_LABEL_SIZE)
    if ticks is not None:
        cbar.set_ticks(ticks)
    cbar.ax.tick_params(labelsize=TICK_LABEL_SIZE)
    return cbar

def save_figure(fig, filepath_base):
    """Save figure in PNG and SVG formats with exact dimensions."""
    fig.savefig(f"{filepath_base}.png", dpi=DPI, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    fig.savefig(f"{filepath_base}.svg", bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print(f"Saved: {filepath_base}.png and {filepath_base}.svg")