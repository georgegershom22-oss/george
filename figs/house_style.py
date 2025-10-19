"""
Shared Matplotlib house style for Figures 3.6A–C.
Outputs are sized to 1800×1200 px (landscape) with white background.
Typeface: Helvetica/Arial fallback; sizes per spec.
Grid: light gray (#E5E7EB), 0.8 px, major ticks only.
Color palette and helpers for overlays (conversion band) provided.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple, Optional

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# Canvas constants
CANVAS_PX = (1800, 1200)  # width, height in pixels
DPI = 100  # ensures inches * DPI = pixels
FIGSIZE_IN = (CANVAS_PX[0] / DPI, CANVAS_PX[1] / DPI)

# Typography (points)
PT_TITLE = 28
PT_AXIS_LABEL = 22
PT_TICK = 16
PT_INPLOT = 19  # 18–20 pt
PT_CAPTION = 15

# Colors
COLOR_GRID = "#E5E7EB"
COLOR_AXIS = "#111827"
COLOR_NOTE = "#111827"
COLOR_BAND = "#F4A261"  # conversion window overlay
COLOR_CENTERLINE = "#9CA3AF"

# Curve palette
COLOR_BLUE = "#1F78B4"        # deep blue
COLOR_STEEL = "#457B9D"       # secondary steel blue
COLOR_MAGENTA = "#B3007D"     # contrast magenta

# Grid width in points so that it renders ~0.8 px at 100 dpi.
# 1 point at 100 dpi is ~1.333 px (since 72 pt per inch).
# We want ~0.8 px -> ~0.6 pt.
GRID_LINEWIDTH_PT = 0.6
AX_LINEWIDTH_PT = 1.0

# Colormap for heatmaps: darker = higher intensity (use reversed cividis)
HEATMAP_CMAP = mpl.colormaps.get("cividis_r")


def apply_base_style():
    """Apply global Matplotlib rcParams for the house style."""
    mpl.rcdefaults()

    # Fonts: prefer Helvetica/Arial; fall back to DejaVu Sans
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans", "Liberation Sans"],
        "figure.dpi": DPI,
        "savefig.dpi": DPI,
        "figure.figsize": FIGSIZE_IN,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.titlesize": PT_TITLE,
        "axes.titleweight": "bold",
        "axes.labelsize": PT_AXIS_LABEL,
        "axes.labelcolor": COLOR_AXIS,
        "axes.edgecolor": COLOR_AXIS,
        "axes.linewidth": AX_LINEWIDTH_PT,
        "xtick.color": COLOR_AXIS,
        "ytick.color": COLOR_AXIS,
        "xtick.labelsize": PT_TICK,
        "ytick.labelsize": PT_TICK,
        "grid.color": COLOR_GRID,
        "grid.linewidth": GRID_LINEWIDTH_PT,
        "grid.linestyle": "-",
        "axes.grid": True,
        "axes.grid.axis": "both",
        "axes.grid.which": "major",
        "legend.frameon": False,
        "legend.loc": "upper right",
        "legend.fontsize": PT_TICK,
        "lines.linewidth": 3.0,
    })


def configure_shared_axes(ax: mpl.axes.Axes,
                           x_kind: Optional[str] = None,
                           y_kind: Optional[str] = None,
                           show_legend: bool = False,
                           ) -> None:
    """Configure shared axis ticks and grid per spec.

    x_kind: 'omega_over_N' or 'time' or None
    y_kind: 'Ri' or 'omega_over_N' or None
    """
    if x_kind == "omega_over_N":
        ax.set_xlim(0.2, 2.2)
        ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
        ax.set_xlabel("ω/N")
    elif x_kind == "time":
        ax.set_xlim(0, 60)
        ax.set_xticks(np.arange(0, 61, 10))
        ax.set_xlabel("time t (s)")

    if y_kind == "Ri":
        ax.set_ylim(0.0, 2.0)
        ax.set_yticks([0.0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
        ax.set_ylabel("Ri")
    elif y_kind == "omega_over_N":
        ax.set_ylim(0.2, 2.2)
        ax.set_yticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
        ax.set_ylabel("ω/N")

    if show_legend:
        ax.legend(loc="upper right", frameon=False)


@dataclass
class ConversionBandSpec:
    x_min: float = 0.8
    x_max: float = 1.2
    color: str = COLOR_BAND
    alpha: float = 0.20
    centerline_color: str = COLOR_CENTERLINE
    centerline_width: float = 1.0
    centerline_style: str = (0, (1, 3))  # dotted


def draw_conversion_band(ax: mpl.axes.Axes,
                         band: ConversionBandSpec = ConversionBandSpec(),
                         axis: str = "x",
                         ) -> None:
    """Overlay translucent amber conversion band (0.8–1.2) and dotted centerline at 1.

    axis: 'x' to draw a vertical band (ω/N on x-axis), 'y' for a horizontal band (ω/N on y-axis).
    """
    if axis == "x":
        ax.axvspan(band.x_min, band.x_max, color=band.color, alpha=band.alpha, zorder=1)
        ax.axvline(1.0, color=band.centerline_color, linewidth=band.centerline_width,
                   linestyle=band.centerline_style, zorder=2)
    elif axis == "y":
        ax.axhspan(band.x_min, band.x_max, color=band.color, alpha=band.alpha, zorder=1)
        ax.axhline(1.0, color=band.centerline_color, linewidth=band.centerline_width,
                   linestyle=band.centerline_style, zorder=2)
    else:
        return


def add_panel_title(ax: mpl.axes.Axes, title: str) -> None:
    ax.set_title(title, loc="left", weight="bold")


def add_caption(ax: mpl.axes.Axes, caption: str) -> None:
    # Place caption inside canvas under the x-axis area; use axes fraction coords
    ax.text(0.0, -0.18, caption, transform=ax.transAxes, ha="left", va="top",
            fontsize=PT_CAPTION, fontstyle="italic", color=COLOR_AXIS)


def add_horizontal_guide(ax: mpl.axes.Axes, y: float, label: Optional[str] = None) -> None:
    ax.axhline(y, color=COLOR_CENTERLINE, linestyle=(0, (6, 4)), linewidth=1.0)
    if label:
        ax.text(0.01, y + 0.02 * (ax.get_ylim()[1] - ax.get_ylim()[0]), label,
                transform=ax.get_yaxis_transform(), fontsize=PT_INPLOT,
                color=COLOR_NOTE)


def ensure_canvas(fig: mpl.figure.Figure) -> None:
    # Force exact pixel size
    fig.set_size_inches(FIGSIZE_IN[0], FIGSIZE_IN[1])
    fig.set_dpi(DPI)


def save_figure(fig: mpl.figure.Figure, basename: str, outdir: str = "/workspace/out/figures") -> None:
    ensure_canvas(fig)
    png_path = f"{outdir}/{basename}.png"
    svg_path = f"{outdir}/{basename}.svg"
    # Do not use bbox_inches="tight" to preserve exact 1800×1200 px canvas
    fig.savefig(png_path, facecolor="white")
    fig.savefig(svg_path, facecolor="white")


def add_colorbar(fig: mpl.figure.Figure, im, label: str, ticks: Optional[Tuple[float, ...]] = None,
                 ax: Optional[mpl.axes.Axes] = None, pad: float = 0.02, shrink: float = 1.0):
    cbar = fig.colorbar(im, ax=ax, pad=pad, shrink=shrink)
    cbar.ax.set_ylabel(label, rotation=90, va="center", fontsize=PT_AXIS_LABEL)
    if ticks is not None:
        cbar.set_ticks(ticks)
    # Tick labels size
    cbar.ax.tick_params(labelsize=PT_TICK)
    return cbar


def seed_rng(seed: int = 42) -> np.random.Generator:
    return np.random.default_rng(seed)
