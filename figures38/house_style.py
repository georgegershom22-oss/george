from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import matplotlib as mpl


# Colors (hex)
AMBER = "#F4A261"
AMBER_ACCENT = "#C06A00"
TEAL = "#2A9D8F"
PURPLE = "#6A4C93"
DARK_GRAY = "#6B7280"  # classical viscous–thermal
GRID_GRAY = "#E5E7EB"
CENTERLINE_GRAY = "#9CA3AF"
BLACK_PURPLE = "#2E183A"
LIGHT_GRAY = "#F3F4F6"

# Canvas size in pixels
CANVAS_W = 2000
CANVAS_H = 1400
DPI = 200  # choose DPI; size in inches = px / DPI
FIGSIZE_INCHES = (CANVAS_W / DPI, CANVAS_H / DPI)


@dataclass
class Fonts:
    title: int = 28
    axis: int = 22
    tick: int = 16
    note: int = 18
    legend: int = 16
    caption: int = 15


FONTS = Fonts()


def apply_house_style() -> None:
    """Apply global Matplotlib rcParams per thesis house style."""
    mpl.rcParams.update(
        {
            # Figure
            "figure.figsize": FIGSIZE_INCHES,
            "figure.dpi": DPI,
            "figure.facecolor": "white",
            # Fonts
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
            "mathtext.default": "regular",
            # Lines
            "lines.linewidth": 3.0,
            "lines.solid_capstyle": "round",
            "lines.solid_joinstyle": "round",
            # Axes
            "axes.titlesize": FONTS.title,
            "axes.labelsize": FONTS.axis,
            "axes.edgecolor": "black",
            "axes.linewidth": 1.2,
            "axes.grid": True,
            "grid.color": GRID_GRAY,
            "grid.linewidth": 0.8,
            "grid.linestyle": "-",
            "axes.grid.which": "major",
            # Ticks
            "xtick.labelsize": FONTS.tick,
            "ytick.labelsize": FONTS.tick,
            "xtick.direction": "out",
            "ytick.direction": "out",
            # Legends
            "legend.frameon": False,
            "legend.fontsize": FONTS.legend,
            # Savefig
            "savefig.dpi": DPI,
            "savefig.facecolor": "white",
            "savefig.bbox": "tight",
            # Patch defaults (useful for overlays)
            "patch.antialiased": True,
        }
    )


def dashed_style(linewidth: float = 2.5) -> dict:
    return {"linewidth": linewidth, "dashes": (6, 6), "solid_capstyle": "round", "solid_joinstyle": "round"}


def dotted_style(linewidth: float = 1.2) -> dict:
    return {"linewidth": linewidth, "dashes": (1, 4), "solid_capstyle": "round", "solid_joinstyle": "round"}


def contour_style_primary(color: str, linewidth: float = 2.5, dashed: bool = False) -> dict:
    if dashed:
        style = dashed_style(linewidth)
    else:
        style = {"linewidth": linewidth}
    style.update({"color": color})
    return style


def amber_teal_diverging_colormap() -> mpl.colors.Colormap:
    """Two-endpoint ramp from amber (0) to teal (1) with pale neutral midpoint.

    Darker away from midpoint, light near 0.5.
    """
    # Create a custom diverging colormap with a light midpoint
    cdict = {
        "red": [
            (0.0, 244 / 255, 244 / 255),  # AMBER
            (0.5, 240 / 255, 240 / 255),  # very light neutral
            (1.0, 42 / 255, 42 / 255),  # TEAL-ish (red component low)
        ],
        "green": [
            (0.0, 162 / 255, 162 / 255),
            (0.5, 243 / 255, 243 / 255),
            (1.0, 157 / 255, 157 / 255),
        ],
        "blue": [
            (0.0, 97 / 255, 97 / 255),
            (0.5, 246 / 255, 246 / 255),
            (1.0, 143 / 255, 143 / 255),
        ],
    }
    return mpl.colors.LinearSegmentedColormap("amber_teal_lightmid", cdict)


def add_conversion_band(ax, x_min: float = 0.8, x_max: float = 1.2, alpha: float = 0.2):
    ax.axvspan(x_min, x_max, color=AMBER, alpha=alpha, lw=0)
    ax.axvline(1.0, color=CENTERLINE_GRAY, **dotted_style(1.2))


def configure_common_frequency_axis(ax, xticks=(0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0)):
    ax.set_xlim(0.2, 2.2)
    ax.set_xticks(xticks)


def add_caption(fig, text: str):
    fig.text(0.5, 0.02, text, ha="center", va="bottom", fontsize=FONTS.caption, style="italic")


def add_micro_label(ax, x: float, y: float, text: str, color: str = "black"):
    ax.text(x, y, text, fontsize=16, color=color, ha="left", va="center")


def make_colorbar(fig, ax, mappable, label: str):
    cbar = fig.colorbar(mappable, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label(label, fontsize=FONTS.axis)
    for tick in cbar.ax.get_yticklabels():
        tick.set_fontsize(FONTS.tick)
    return cbar
