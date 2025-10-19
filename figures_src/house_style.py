from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Tuple, Optional

import matplotlib as mpl
import matplotlib.pyplot as plt

# --- Shared constants ---
CANVAS_PX = (1800, 1200)
DPI = 150  # will be adjusted so that px target is met

# Colors
DEEP_BLUE = "#1F78B4"
STEEL_BLUE = "#457B9D"
MAGENTA = "#B3007D"
GRID_GRAY = "#E5E7EB"
GUIDE_GRAY = "#9CA3AF"
AMBER = "#F4A261"

# Typography sizes (pt)
PT_TITLE = 28
PT_AXIS_LABEL = 22
PT_TICK = 16
PT_NOTE = 18
PT_NOTE_MAX = 20
PT_CAPTION = 15

# Axes ranges
OMEGA_OVER_N_XLIM = (0.2, 2.2)
OMEGA_OVER_N_TICKS = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
RI_YLIM = (0.0, 2.0)
RI_TICKS = [0.0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0]

@dataclass
class FigureCanvas:
    width_px: int = CANVAS_PX[0]
    height_px: int = CANVAS_PX[1]
    dpi: int = DPI

    def make_figure(self) -> mpl.figure.Figure:
        # Choose dpi so that pixels match target as closely as possible
        dpi = self.dpi
        width_in = self.width_px / dpi
        height_in = self.height_px / dpi
        fig = plt.figure(figsize=(width_in, height_in), dpi=dpi, facecolor="white")
        return fig


def apply_house_style() -> None:
    # Fonts: prefer Helvetica/Arial; fall back to DejaVu Sans
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "black",
        "axes.linewidth": 1.0,
        "axes.labelsize": PT_AXIS_LABEL,
        "axes.titlesize": PT_TITLE,
        "axes.titleweight": "bold",
        "axes.grid": True,
        "grid.color": GRID_GRAY,
        "grid.linewidth": 0.8/72*mpl.rcParams.get("figure.dpi", 100),  # approximately 0.8 px
        "grid.alpha": 1.0,
        "grid.linestyle": "-",
        "xtick.color": "black",
        "ytick.color": "black",
        "xtick.labelsize": PT_TICK,
        "ytick.labelsize": PT_TICK,
        "legend.frameon": False,
        "legend.loc": "upper right",
        "legend.fontsize": PT_TICK,
        "savefig.bbox": "tight",
        "savefig.facecolor": "white",
        "savefig.edgecolor": "white",
    })


def format_axes_common_frequency(ax: mpl.axes.Axes) -> None:
    ax.set_xlim(*OMEGA_OVER_N_XLIM)
    ax.set_xticks(OMEGA_OVER_N_TICKS)
    # Major grid only
    ax.grid(True, which="major")
    ax.grid(False, which="minor")
    ax.set_xlabel("ω/N")


def format_axes_common_ri(ax: mpl.axes.Axes, ylabel: Optional[str] = "Ri") -> None:
    ax.set_ylim(*RI_YLIM)
    ax.set_yticks(RI_TICKS)
    if ylabel:
        ax.set_ylabel(ylabel)
    # Major grid only
    ax.grid(True, which="major")
    ax.grid(False, which="minor")


def add_conversion_band(ax: mpl.axes.Axes) -> None:
    # Amber band 0.8 <= ω/N <= 1.2 at 20% opacity and dotted center line at 1
    ax.axvspan(0.8, 1.2, color=AMBER, alpha=0.20, ec=None, lw=0)
    ax.axvline(1.0, color=GUIDE_GRAY, lw=1.0, ls=(0, (1, 3)))


def add_marginal_stability_line(ax: mpl.axes.Axes) -> None:
    ax.axhline(0.25, color=GUIDE_GRAY, lw=1.0, ls=(0, (4, 4)))
    ax.text(ax.get_xlim()[0] + 0.02*(ax.get_xlim()[1]-ax.get_xlim()[0]), 0.25 + 0.03*(ax.get_ylim()[1]-ax.get_ylim()[0]),
            "marginal stability", fontsize=PT_NOTE, color=GUIDE_GRAY, va="bottom")


def add_caption(fig: mpl.figure.Figure, text: str) -> None:
    # Caption inside canvas under x-axis; use italics 15 pt
    fig.text(0.5, 0.03, text, ha="center", va="bottom", fontsize=PT_CAPTION, style="italic")


def add_panel_title(ax: mpl.axes.Axes, title: str) -> None:
    ax.set_title(title, loc="left", weight="bold")


def configure_colorbar(cb: mpl.colorbar.Colorbar, label: str, ticks: Optional[Iterable[float]] = None) -> None:
    cb.set_label(label)
    if ticks is not None:
        cb.set_ticks(list(ticks))


def ensure_axes_background(ax: mpl.axes.Axes) -> None:
    ax.set_facecolor("white")

