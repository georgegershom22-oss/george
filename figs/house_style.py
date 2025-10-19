from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FixedLocator, FixedFormatter


AMBER = "#F4A261"
GRID_GRAY = "#E5E7EB"
CENTERLINE_GRAY = "#9CA3AF"
DEEP_BLUE = "#1F78B4"
STEEL_BLUE = "#457B9D"
MAGENTA = "#B3007D"


def apply_house_style(fig: mpl.figure.Figure | None = None) -> None:
    """Apply shared house style rcParams.

    - Canvas 1800x1200 px via figsize if figure provided.
    - Helvetica/Arial fallback.
    - Grid light gray, thin, major only.
    - Legend inside, frame off by default.
    """
    mpl.rcParams.update(
        {
            # Typography
            "font.family": ["Helvetica", "Arial", "DejaVu Sans", "Liberation Sans", "sans-serif"],
            "font.size": 16,  # baseline for tick labels; specific sizes set per element
            "axes.titlesize": 28,
            "axes.titleweight": "bold",
            "axes.labelsize": 22,
            "axes.labelweight": "regular",
            "xtick.labelsize": 16,
            "ytick.labelsize": 16,
            # Grid
            "axes.grid": True,
            "grid.color": GRID_GRAY,
            "grid.linewidth": 0.8 / 72.0 * mpl.rcParams.get("figure.dpi", 100),  # ~0.8 px
            "grid.alpha": 1.0,
            "axes.grid.which": "major",
            # Legend
            "legend.frameon": False,
            "legend.loc": "upper right",
            # Lines
            "lines.linewidth": 3.0,
            # Savefig defaults
            "savefig.dpi": 300,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )

    if fig is not None:
        # Set pixel-based canvas size (1800x1200 px) using current DPI
        dpi = fig.dpi if hasattr(fig, "dpi") else mpl.rcParams.get("figure.dpi", 100)
        fig.set_size_inches(1800 / dpi, 1200 / dpi)


def set_common_frequency_axis(ax: mpl.axes.Axes) -> None:
    """Configure x-axis for normalized frequency ω/N ranging 0.2→2.2 with specified ticks."""
    ax.set_xlim(0.2, 2.2)
    ax.set_xlabel("ω/N")
    ax.xaxis.set_major_locator(FixedLocator([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]))
    ax.xaxis.set_minor_locator(mpl.ticker.NullLocator())


def set_common_ri_axis(ax: mpl.axes.Axes) -> None:
    """Configure y-axis for stability Ri ranging 0.0→2.0 with specified ticks."""
    ax.set_ylim(0.0, 2.0)
    ax.set_ylabel("Ri")
    ax.yaxis.set_major_locator(FixedLocator([0.0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0]))
    ax.yaxis.set_minor_locator(mpl.ticker.NullLocator())


def add_conversion_overlay(ax: mpl.axes.Axes) -> None:
    """Add translucent amber band for 0.8 ≤ ω/N ≤ 1.2 and dotted centerline at ω/N=1."""
    # Vertical band
    ax.axvspan(0.8, 1.2, color=AMBER, alpha=0.20, zorder=0)
    # Dotted centerline
    ax.axvline(1.0, color=CENTERLINE_GRAY, linewidth=1.0, linestyle=(0, (1.5, 3)))


def add_panel_title(ax: mpl.axes.Axes, title: str) -> None:
    ax.set_title(title, loc="left", pad=8)


def add_caption(fig: mpl.figure.Figure, ax: mpl.axes.Axes, text: str) -> None:
    """Place a caption inside the canvas under x-axis, 15 pt italics."""
    # Using axes coordinates slightly below plotting area
    ax.text(
        0.0,
        -0.18,
        text,
        transform=ax.transAxes,
        fontsize=15,
        fontstyle="italic",
        va="top",
        ha="left",
        color="black",
    )


def color_cycle_curves(ax: mpl.axes.Axes) -> None:
    ax.set_prop_cycle(color=[DEEP_BLUE, STEEL_BLUE, MAGENTA])


def make_colorbar(fig: mpl.figure.Figure, mappable, ax: mpl.axes.Axes, **kwargs):
    cbar = fig.colorbar(mappable, ax=ax, **kwargs)
    cbar.outline.set_visible(False)
    return cbar
