from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Tuple, List, Optional

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


# Shared color palette
COLORS = {
    "classical": "#6B7280",        # neutral dark grey
    "conversion": "#F4A261",       # amber (fill)
    "conversion_dark": "#C06A00",  # darker amber for lines if needed
    "interfacial": "#6A4C93",      # purple
    "shear": "#2A9D8F",           # teal
    "grid": "#E5E7EB",            # light grey for grid
    "guide": "#9CA3AF",           # dotted guide line color
}

FONT_SIZES = {
    "title": 28,
    "axis_label": 22,
    "tick": 16,
    "note": 18,
    "legend": 16,
    "caption": 15,
}

DASH = {
    "dashed": (0, (8, 6)),
    "dotted": (0, (1, 4)),
}

PRIMARY_LW = 3.0
SECONDARY_LW = 2.2
GUIDE_LW = 1.2
GRID_LW = 0.8

CANVAS_PX = (2000, 1400)


def apply_rc_params() -> None:
    """Apply shared rcParams for typography and line aesthetics."""
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "Liberation Sans"],
        "axes.titlesize": FONT_SIZES["title"],
        "axes.labelsize": FONT_SIZES["axis_label"],
        "xtick.labelsize": FONT_SIZES["tick"],
        "ytick.labelsize": FONT_SIZES["tick"],
        "legend.fontsize": FONT_SIZES["legend"],
        "axes.edgecolor": "black",
        "axes.linewidth": 1.2,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
        "savefig.facecolor": "white",
        "figure.facecolor": "white",
    })


def new_figure() -> mpl.figure.Figure:
    """Create a new 2000x1400 px figure."""
    # Choose dpi such that pixels match requested canvas
    dpi = 100  # 20x14 inches -> 2000x1400 px
    fig = plt.figure(figsize=(CANVAS_PX[0] / dpi, CANVAS_PX[1] / dpi), dpi=dpi)
    return fig


def add_conversion_window(ax: mpl.axes.Axes, xlim: Tuple[float, float], ylim: Tuple[float, float],
                          low: float = 0.8, high: float = 1.2) -> None:
    """Add translucent amber band in [low, high] and dotted centerline at 1."""
    rect = Rectangle((low, ylim[0]), high - low, ylim[1] - ylim[0],
                     facecolor=COLORS["conversion"], alpha=0.20, edgecolor="none", zorder=0)
    ax.add_patch(rect)
    ax.axvline(1.0, color=COLORS["guide"], linewidth=GUIDE_LW, linestyle=DASH["dotted"], zorder=1)


def style_frequency_axis(ax: mpl.axes.Axes) -> None:
    """Configure a frequency axis ω/N∈[0.2,2.2] with specified ticks and grid."""
    ax.set_xlim(0.2, 2.2)
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.grid(True, which="major", color=COLORS["grid"], linewidth=GRID_LW)
    ax.grid(False, which="minor")


def style_share_axis(ax: mpl.axes.Axes) -> None:
    ax.set_ylim(0.0, 1.0)
    ax.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    ax.grid(True, which="major", axis="y", color=COLORS["grid"], linewidth=GRID_LW)


def add_caption(fig: mpl.figure.Figure, text: str) -> None:
    fig.text(0.5, 0.02, text, ha="center", va="bottom", fontsize=FONT_SIZES["caption"], style="italic")


def save_figure(fig: mpl.figure.Figure, out_base: str) -> None:
    os.makedirs(os.path.dirname(out_base), exist_ok=True)
    # Save SVG (vector)
    fig.savefig(out_base + ".svg", bbox_inches="tight")
    # Save PNG at exact canvas size
    fig.savefig(out_base + ".png", dpi=fig.dpi, bbox_inches="tight")


@dataclass
class LegendItem:
    label: str
    color: str


def add_mechanism_legend(ax: mpl.axes.Axes, loc: str = "lower right") -> None:
    handles = [
        mpl.lines.Line2D([0], [0], color=COLORS["classical"], lw=PRIMARY_LW, label="Classical"),
        mpl.lines.Line2D([0], [0], color=COLORS["conversion"], lw=PRIMARY_LW, label="Mode conversion"),
        mpl.lines.Line2D([0], [0], color=COLORS["interfacial"], lw=PRIMARY_LW, label="Interfacial"),
        mpl.lines.Line2D([0], [0], color=COLORS["shear"], lw=PRIMARY_LW, label="Shear-mediated"),
    ]
    leg = ax.legend(handles=handles, loc=loc, frameon=False)
    for txt in leg.get_texts():
        txt.set_fontsize(FONT_SIZES["legend"]) 
