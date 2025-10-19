import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

# Color palette
DEEP_BLUE = "#1F78B4"
STEEL_BLUE = "#457B9D"
MAGENTA = "#B3007D"
AMBER = "#F4A261"
GRID_GRAY = "#E5E7EB"
CENTERLINE_GRAY = "#9CA3AF"

# Shared axis ticks
OMEGA_OVER_N_TICKS = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
RI_TICKS = [0.0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0]

# Typography sizes (pt)
TITLE_PT = 28
AXIS_LABEL_PT = 22
TICK_PT = 16
IN_PLOT_NOTE_PT = 19
CAPTION_PT = 15

# Canvas size (pixels) and figure inches at 200 DPI
CANVAS_W = 1800
CANVAS_H = 1200
DPI = 200
FIGSIZE = (CANVAS_W / DPI, CANVAS_H / DPI)


def apply_house_style():
    mpl.rcParams.update({
        "figure.dpi": DPI,
        "savefig.dpi": DPI,
        "figure.figsize": FIGSIZE,
        "font.family": ["Helvetica", "Arial", "DejaVu Sans", "Liberation Sans", "sans-serif"],
        "axes.titlesize": TITLE_PT,
        "axes.labelsize": AXIS_LABEL_PT,
        "xtick.labelsize": TICK_PT,
        "ytick.labelsize": TICK_PT,
        "axes.grid": True,
        "grid.color": GRID_GRAY,
        "grid.linewidth": 0.8 / DPI * 72.0,  # approx 0.8 px
        "grid.linestyle": "-",
        "axes.grid.which": "major",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
    })


def make_axes_omega_over_N(ax, xlim=(0.2, 2.2), add_conversion_band=True):
    ax.set_xlim(*xlim)
    ax.set_xticks(OMEGA_OVER_N_TICKS)
    ax.set_xlabel(r"$\omega/N$")
    if add_conversion_band:
        add_conversion_overlay(ax)


def make_axes_Ri(ax, ylim=(0.0, 2.0)):
    ax.set_ylim(*ylim)
    ax.set_yticks(RI_TICKS)
    ax.set_ylabel(r"$R_i$")


def add_conversion_overlay(ax, xmin=0.8, xmax=1.2):
    ymin, ymax = ax.get_ylim()
    rect = Rectangle((xmin, ymin), xmax - xmin, ymax - ymin,
                     facecolor=AMBER, edgecolor="none", alpha=0.2, zorder=0.5)
    ax.add_patch(rect)
    ax.axvline(1.0, color=CENTERLINE_GRAY, linestyle=(0, (1, 3)), linewidth=1.0, zorder=0.6)


def colorbar_right(fig, im, label, ticks=None, ax=None, pad=0.02):
    cbar = fig.colorbar(im, ax=ax, pad=pad, ticks=ticks)
    cbar.set_label(label)
    return cbar


def dark_colormap(name="cividis"):
    # Ensure darker = higher intensity by reversing standard lightness perception
    # Cividis/Viridis already have dark low/high? We enforce darker= higher by reversing.
    return plt.get_cmap(name + "_r")


def add_panel_title(ax, text, loc="left"):
    ax.set_title(text, loc=loc, fontweight="bold")


def add_caption(fig, text):
    fig.text(0.5, 0.02, text, ha="center", va="bottom", fontsize=CAPTION_PT, style="italic")


def legend_in_upper_right(ax):
    ax.legend(loc="upper right", frameon=False)


def omega_N_Ri_mesh(n_omega=400, n_ri=300, omega_range=(0.2, 2.2), ri_range=(0.0, 2.0)):
    omega = np.linspace(*omega_range, n_omega)
    ri = np.linspace(*ri_range, n_ri)
    W, R = np.meshgrid(omega, ri)
    return W, R


def export(fig, path_base):
    png_path = f"{path_base}.png"
    svg_path = f"{path_base}.svg"
    fig.savefig(png_path, bbox_inches="tight")
    fig.savefig(svg_path, bbox_inches="tight")
    return png_path, svg_path

# Line styles helpers
SOLID_DEEP_BLUE = dict(color=DEEP_BLUE, linewidth=3.0)
DASHED_STEEL_BLUE = dict(color=STEEL_BLUE, linewidth=3.0, linestyle=(0, (6, 4)))


def half_power_bandwidth(ax, center_x, left_x, right_x, y_level, color=CENTERLINE_GRAY, label="BW"):
    ax.annotate("", xy=(left_x, y_level), xytext=(right_x, y_level),
                arrowprops=dict(arrowstyle='<->', color=color, linewidth=1.5))
    ax.text(center_x, y_level - 0.06 * ax.get_ylim()[1], label,
            ha="center", va="top", fontsize=TICK_PT, color=color)
