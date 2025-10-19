"""
Shared house style for Figures 3.6A-C
Canvas: 1800 × 1200 px (landscape), white background
Typeface: Helvetica/Arial with specified point sizes
Grid: light gray (#E5E7EB), thin (0.8 px), major ticks only
Color palette: color-blind robust
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.font_manager as fm

# Canvas specifications
CANVAS_WIDTH = 1800
CANVAS_HEIGHT = 1200
DPI = 100  # For exact pixel dimensions

# Typography specifications
FONT_FAMILY = 'sans-serif'  # Will try Helvetica/Arial, fallback to system sans
PANEL_TITLE_SIZE = 28
AXIS_LABEL_SIZE = 22
TICK_LABEL_SIZE = 16
IN_PLOT_NOTE_SIZE = 18
SUBSCRIPT_SIZE_RATIO = 0.7

# Grid specifications
GRID_COLOR = '#E5E7EB'
GRID_LINEWIDTH = 0.8

# Color palette (color-blind robust)
DEEP_BLUE = '#1F78B4'
STEEL_BLUE = '#457B9D'
MAGENTA = '#B3007D'
AMBER = '#F4A261'
CENTERLINE_COLOR = '#9CA3AF'

# Common axis specifications
OMEGA_N_RANGE = (0.2, 2.2)
OMEGA_N_TICKS = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
RI_RANGE = (0.0, 2.0)
RI_TICKS = [0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0]

# Conversion window specifications
CONVERSION_WINDOW_OPACITY = 0.2
CONVERSION_WINDOW_RANGE = (0.8, 1.2)
CENTERLINE_WIDTH = 1.0

def setup_figure_style():
    """Configure matplotlib with the house style"""
    plt.rcParams.update({
        'font.family': FONT_FAMILY,
        'font.size': TICK_LABEL_SIZE,
        'axes.linewidth': 1.0,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.grid': True,
        'grid.color': GRID_COLOR,
        'grid.linewidth': GRID_LINEWIDTH,
        'grid.alpha': 1.0,
        'xtick.direction': 'in',
        'ytick.direction': 'in',
        'xtick.major.size': 4,
        'ytick.major.size': 4,
        'xtick.minor.size': 0,
        'ytick.minor.size': 0,
        'legend.frameon': False,
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
    })

def create_figure(figsize=None, dpi=DPI):
    """Create a figure with the house style dimensions"""
    if figsize is None:
        figsize = (CANVAS_WIDTH/DPI, CANVAS_HEIGHT/DPI)
    fig = plt.figure(figsize=figsize, dpi=dpi, facecolor='white')
    return fig

def add_conversion_window(ax, y_range=None, opacity=CONVERSION_WINDOW_OPACITY):
    """Add the amber conversion window overlay"""
    if y_range is None:
        y_range = ax.get_ylim()
    
    # Amber band
    rect = patches.Rectangle(
        (CONVERSION_WINDOW_RANGE[0], y_range[0]),
        CONVERSION_WINDOW_RANGE[1] - CONVERSION_WINDOW_RANGE[0],
        y_range[1] - y_range[0],
        linewidth=0,
        facecolor=AMBER,
        alpha=opacity,
        zorder=1
    )
    ax.add_patch(rect)
    
    # Dotted centerline at ω/N = 1
    ax.axvline(x=1.0, color=CENTERLINE_COLOR, linestyle=':', 
               linewidth=CENTERLINE_WIDTH, alpha=0.8, zorder=2)

def add_marginal_stability_guide(ax, x_range=None):
    """Add horizontal guide at Ri = 0.25"""
    if x_range is None:
        x_range = ax.get_xlim()
    
    ax.axhline(y=0.25, color='gray', linestyle='--', 
               linewidth=0.8, alpha=0.6, zorder=2)
    ax.text(x_range[1] - 0.1, 0.25 + 0.05, 'marginal stability', 
            fontsize=IN_PLOT_NOTE_SIZE, ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))

def setup_omega_n_axis(ax, xlabel=True):
    """Setup ω/N axis with common specifications"""
    ax.set_xlim(OMEGA_N_RANGE)
    ax.set_xticks(OMEGA_N_TICKS)
    if xlabel:
        ax.set_xlabel('ω/N', fontsize=AXIS_LABEL_SIZE, fontweight='normal')
    ax.tick_params(axis='x', labelsize=TICK_LABEL_SIZE)

def setup_ri_axis(ax, ylabel=True):
    """Setup Ri axis with common specifications"""
    ax.set_ylim(RI_RANGE)
    ax.set_yticks(RI_TICKS)
    if ylabel:
        ax.set_ylabel('Ri', fontsize=AXIS_LABEL_SIZE, fontweight='normal')
    ax.tick_params(axis='y', labelsize=TICK_LABEL_SIZE)

def add_panel_title(ax, title, position='top-left', fontsize=PANEL_TITLE_SIZE):
    """Add panel title inside axes"""
    if position == 'top-left':
        ax.text(0.02, 0.98, title, transform=ax.transAxes, 
                fontsize=fontsize, fontweight='bold', va='top', ha='left',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
    elif position == 'top-center':
        ax.text(0.5, 0.98, title, transform=ax.transAxes, 
                fontsize=fontsize, fontweight='bold', va='top', ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))

def add_caption(ax, caption, position='bottom', fontsize=15, style='italic'):
    """Add caption inside axes"""
    if position == 'bottom':
        ax.text(0.5, 0.02, caption, transform=ax.transAxes, 
                fontsize=fontsize, style=style, ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))

def add_colorbar(fig, ax, mappable, label, ticks=None, position='right'):
    """Add colorbar with house style"""
    if position == 'right':
        cbar = fig.colorbar(mappable, ax=ax, shrink=0.8, aspect=20, pad=0.02)
    else:
        cbar = fig.colorbar(mappable, ax=ax, shrink=0.8, aspect=20, pad=0.02)
    
    cbar.set_label(label, fontsize=AXIS_LABEL_SIZE, fontweight='normal')
    cbar.ax.tick_params(labelsize=TICK_LABEL_SIZE)
    
    if ticks is not None:
        cbar.set_ticks(ticks)
    
    return cbar

def get_heatmap_colormap():
    """Get perceptually uniform colormap (Cividis) with darker = higher intensity"""
    return plt.cm.cividis

def add_uncertainty_band(ax, x, y, yerr, color, alpha=0.25):
    """Add uncertainty/intermittency band"""
    ax.fill_between(x, y - yerr, y + yerr, color=color, alpha=alpha, zorder=1)

def add_arrow_annotation(ax, text, xy, xytext, arrowprops=None, fontsize=IN_PLOT_NOTE_SIZE):
    """Add arrowed annotation"""
    if arrowprops is None:
        arrowprops = dict(arrowstyle='->', color='black', lw=1)
    
    ax.annotate(text, xy=xy, xytext=xytext, 
                fontsize=fontsize, ha='center', va='center',
                arrowprops=arrowprops,
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))

def save_figure(fig, filename, formats=['png', 'svg']):
    """Save figure in multiple formats with exact dimensions"""
    for fmt in formats:
        fig.savefig(f'/workspace/out/figures/{filename}.{fmt}', 
                   format=fmt, dpi=DPI, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')

# Initialize the style
setup_figure_style()