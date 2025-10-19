"""
Shared house style for Figures 3.6A–C
Implements consistent styling, colors, fonts, and helpers
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

# ============================================================================
# Canvas and DPI
# ============================================================================
CANVAS_WIDTH_PX = 1800
CANVAS_HEIGHT_PX = 1200
DPI = 100  # Base DPI for all exports

# ============================================================================
# Typography
# ============================================================================
FONT_FAMILY = ['Helvetica', 'Arial', 'sans-serif']
FONT_SIZES = {
    'title': 28,          # Panel titles
    'axis_label': 22,     # Axis labels
    'tick_label': 16,     # Tick labels
    'note': 18,           # In-plot notes
    'caption': 15,        # Figure captions
}

# ============================================================================
# Colors (color-blind robust palette)
# ============================================================================
COLORS = {
    'primary': '#1F78B4',      # Deep blue (main curves)
    'secondary': '#457B9D',    # Steel blue (secondary curves)
    'contrast': '#B3007D',     # Magenta (contrast)
    'grid': '#E5E7EB',         # Light gray grid
    'amber': '#F4A261',        # Conversion band overlay
    'gray_line': '#9CA3AF',    # Dotted centerline
    'text_dark': '#1F2937',    # Dark text
}

# ============================================================================
# Grid styling
# ============================================================================
GRID_LINEWIDTH = 0.8  # px
GRID_ALPHA = 0.8

# ============================================================================
# Axis ranges and ticks
# ============================================================================
OMEGA_N_RANGE = (0.2, 2.2)
OMEGA_N_TICKS = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]

RI_RANGE = (0.0, 2.0)
RI_TICKS = [0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0]

# Conversion window
CONVERSION_WINDOW = (0.8, 1.2)
CONVERSION_CENTER = 1.0

# ============================================================================
# Apply house style globally
# ============================================================================
def apply_house_style():
    """Apply global Matplotlib RC parameters for house style"""
    plt.rcParams.update({
        'font.family': FONT_FAMILY[0],
        'font.sans-serif': FONT_FAMILY,
        'font.size': FONT_SIZES['tick_label'],
        'axes.labelsize': FONT_SIZES['axis_label'],
        'axes.titlesize': FONT_SIZES['title'],
        'axes.titleweight': 'bold',
        'xtick.labelsize': FONT_SIZES['tick_label'],
        'ytick.labelsize': FONT_SIZES['tick_label'],
        'legend.fontsize': FONT_SIZES['note'],
        'legend.frameon': False,
        'axes.grid': True,
        'axes.axisbelow': True,
        'grid.color': COLORS['grid'],
        'grid.linewidth': GRID_LINEWIDTH,
        'grid.alpha': GRID_ALPHA,
        'axes.facecolor': 'white',
        'figure.facecolor': 'white',
        'savefig.facecolor': 'white',
        'savefig.edgecolor': 'none',
        'savefig.dpi': DPI,
        'figure.dpi': DPI,
    })

# ============================================================================
# Axis setup helpers
# ============================================================================
def setup_omega_n_axis(ax, label_pos='bottom'):
    """Configure normalized frequency axis ω/N"""
    ax.set_xlim(*OMEGA_N_RANGE)
    ax.set_xticks(OMEGA_N_TICKS)
    if label_pos == 'bottom':
        ax.set_xlabel(r'$\omega/N$', fontsize=FONT_SIZES['axis_label'], labelpad=8)
    ax.tick_params(axis='x', labelsize=FONT_SIZES['tick_label'])
    ax.grid(True, color=COLORS['grid'], linewidth=GRID_LINEWIDTH, alpha=GRID_ALPHA)

def setup_ri_axis(ax, label_pos='left'):
    """Configure Richardson number axis Ri"""
    ax.set_xlim(*RI_RANGE) if label_pos == 'bottom' else ax.set_ylim(*RI_RANGE)
    ticks = RI_TICKS
    
    if label_pos == 'left':
        ax.set_ylim(*RI_RANGE)
        ax.set_yticks(ticks)
        ax.set_ylabel(r'$Ri$', fontsize=FONT_SIZES['axis_label'], labelpad=8)
        ax.tick_params(axis='y', labelsize=FONT_SIZES['tick_label'])
    elif label_pos == 'bottom':
        ax.set_xlim(*RI_RANGE)
        ax.set_xticks(ticks)
        ax.set_xlabel(r'$Ri$', fontsize=FONT_SIZES['axis_label'], labelpad=8)
        ax.tick_params(axis='x', labelsize=FONT_SIZES['tick_label'])
    
    ax.grid(True, color=COLORS['grid'], linewidth=GRID_LINEWIDTH, alpha=GRID_ALPHA)

# ============================================================================
# Conversion band overlay
# ============================================================================
def add_conversion_band(ax, ri_range=(0.0, 2.0), orientation='vertical'):
    """
    Add translucent amber conversion window overlay
    
    Parameters
    ----------
    ax : matplotlib axes
    ri_range : tuple
        Range for vertical span (if orientation='vertical') or horizontal span
    orientation : str
        'vertical' for ω/N on x-axis, 'horizontal' for ω/N on y-axis
    """
    if orientation == 'vertical':
        # ω/N on x-axis
        ax.axvspan(CONVERSION_WINDOW[0], CONVERSION_WINDOW[1], 
                   color=COLORS['amber'], alpha=0.20, zorder=1)
        ax.axvline(CONVERSION_CENTER, color=COLORS['gray_line'], 
                  linestyle=':', linewidth=1.0, alpha=0.7, zorder=2)
    else:
        # ω/N on y-axis
        ax.axhspan(CONVERSION_WINDOW[0], CONVERSION_WINDOW[1], 
                   color=COLORS['amber'], alpha=0.20, zorder=1)
        ax.axhline(CONVERSION_CENTER, color=COLORS['gray_line'], 
                  linestyle=':', linewidth=1.0, alpha=0.7, zorder=2)

# ============================================================================
# Text elements
# ============================================================================
def add_panel_title(ax, title, loc='top-left'):
    """Add panel title inside axes"""
    x_pos = 0.02 if 'left' in loc else 0.98
    y_pos = 0.98 if 'top' in loc else 0.02
    ha = 'left' if 'left' in loc else 'right'
    va = 'top' if 'top' in loc else 'bottom'
    
    ax.text(x_pos, y_pos, title, transform=ax.transAxes,
            fontsize=FONT_SIZES['title'], weight='bold',
            ha=ha, va=va)

def add_caption(ax, caption, y_offset=-0.15):
    """Add italicized caption below axes"""
    ax.text(0.5, y_offset, caption, transform=ax.transAxes,
            fontsize=FONT_SIZES['caption'], style='italic',
            ha='center', va='top')

# ============================================================================
# Colorbar styling
# ============================================================================
def colorbar_style(fig, mappable, ax, label=''):
    """Create styled colorbar"""
    cbar = fig.colorbar(mappable, ax=ax, pad=0.02, aspect=30)
    cbar.set_label(label, fontsize=FONT_SIZES['note'], labelpad=12)
    cbar.ax.tick_params(labelsize=FONT_SIZES['tick_label'] - 2)
    return cbar
