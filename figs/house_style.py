from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple, Optional

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# --- Canvas and typography ---
FIG_WIDTH_PX = 1800
FIG_HEIGHT_PX = 1200
DPI = 150  # Ensures 1800x1200 when figsize=(12,8)
FIG_SIZE_IN = (FIG_WIDTH_PX / DPI, FIG_HEIGHT_PX / DPI)

# Font sizes (points)
TITLE_PT = 28
AXIS_LABEL_PT = 22
TICK_PT = 16
NOTE_PT = 19  # in-plot notes 18–20 pt
CAPTION_PT = 15

# Colors
COLORS = {
    "deep_blue": "#1F78B4",
    "steel_blue": "#457B9D",
    "magenta": "#B3007D",
    "grid_gray": "#E5E7EB",
    "centerline_gray": "#9CA3AF",
    "amber": "#F4A261",
}

# Heatmap colormap: darker = higher intensity
HEATMAP_CMAP = "cividis_r"

# Shared axes ticks
OMEGA_TICKS = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
RI_TICKS = [0.0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0]
PSD_TICKS = [0.0, 0.25, 0.5, 0.75, 1.0]

# Grid linewidth: 0.8 px -> points
GRID_LW_PT = 0.8 * 72.0 / DPI
CENTERLINE_LW_PT = 1.0 * 72.0 / DPI
CURVE_LW_PT = 3.0  # in points, visually ~3 px at ~150 dpi


def apply_mpl_defaults() -> None:
    mpl.rcParams.update({
        # Figure
        "figure.figsize": FIG_SIZE_IN,
        "figure.dpi": DPI,
        "savefig.dpi": DPI,
        # Fonts
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "mathtext.fontset": "dejavusans",
        # Axes
        "axes.titlesize": TITLE_PT,
        "axes.labelsize": AXIS_LABEL_PT,
        "axes.grid": True,
        "axes.grid.which": "major",
        "axes.edgecolor": "black",
        # Grid
        "grid.color": COLORS["grid_gray"],
        "grid.linewidth": GRID_LW_PT,
        "grid.alpha": 1.0,
        # Ticks
        "xtick.labelsize": TICK_PT,
        "ytick.labelsize": TICK_PT,
        # Legend
        "legend.frameon": False,
        "legend.fontsize": TICK_PT,
    })


def new_canvas() -> plt.Figure:
    """Create a new 1800x1200 px figure canvas."""
    fig = plt.figure(figsize=FIG_SIZE_IN, dpi=DPI, constrained_layout=False)
    return fig


def set_omega_over_N_axis(ax: plt.Axes) -> None:
    ax.set_xlim(0.2, 2.2)
    ax.set_xticks(OMEGA_TICKS)
    ax.set_xlabel(r"$\omega/N$")


def set_Ri_axis(ax: plt.Axes) -> None:
    ax.set_ylim(0.0, 2.0)
    ax.set_yticks(RI_TICKS)
    ax.set_ylabel(r"$R_i$")


@dataclass
class ConversionBandStyle:
    x0: float = 0.8
    x1: float = 1.2
    color: str = COLORS["amber"]
    alpha: float = 0.20
    centerline_color: str = COLORS["centerline_gray"]
    centerline_lw_pt: float = CENTERLINE_LW_PT


def add_conversion_band(ax: plt.Axes, orientation: str = "vertical", style: ConversionBandStyle = ConversionBandStyle()) -> None:
    """Add translucent amber conversion band and dotted centerline.
    orientation: 'vertical' for x in [0.8,1.2]; 'horizontal' for y in [0.8,1.2]
    """
    if orientation == "vertical":
        ax.axvspan(style.x0, style.x1, color=style.color, alpha=style.alpha, zorder=1)
        ax.axvline(1.0, color=style.centerline_color, lw=style.centerline_lw_pt, ls=(0, (2, 3)), zorder=2)
    elif orientation == "horizontal":
        ax.axhspan(style.x0, style.x1, color=style.color, alpha=style.alpha, zorder=1)
        ax.axhline(1.0, color=style.centerline_color, lw=style.centerline_lw_pt, ls=(0, (2, 3)), zorder=2)
    else:
        raise ValueError("orientation must be 'vertical' or 'horizontal'")


def add_title_inside(ax: plt.Axes, title: str) -> None:
    ax.text(0.01, 0.98, title, transform=ax.transAxes, va="top", ha="left", fontsize=TITLE_PT, fontweight="bold")


def add_caption(fig: plt.Figure, caption: str) -> None:
    fig.text(0.5, 0.02, caption, ha="center", va="bottom", fontsize=CAPTION_PT, style="italic")


def add_colorbar(fig: plt.Figure, mappable, ax: plt.Axes, label: str, ticks: Optional[list] = None) -> mpl.colorbar.Colorbar:
    cbar = fig.colorbar(mappable, ax=ax, pad=0.02)
    cbar.set_label(label, fontsize=AXIS_LABEL_PT)
    if ticks is not None:
        cbar.set_ticks(ticks)
    cbar.ax.tick_params(labelsize=TICK_PT)
    return cbar


def add_marginal_stability_line(ax: plt.Axes) -> None:
    ax.axhline(0.25, color=COLORS["centerline_gray"], lw=CENTERLINE_LW_PT, ls=(0, (4, 4)))
    ax.text(0.995, 0.255, "marginal stability", transform=ax.get_yaxis_transform(), ha="right", va="bottom", fontsize=TICK_PT)


def save_figure(fig: plt.Figure, out_base: str) -> Tuple[str, str]:
    png_path = f"{out_base}.png"
    svg_path = f"{out_base}.svg"
    fig.savefig(png_path, dpi=DPI, facecolor="white", bbox_inches="tight")
    fig.savefig(svg_path, dpi=DPI, facecolor="white", bbox_inches="tight")
    return png_path, svg_path


# Initialize defaults on import
apply_mpl_defaults()
