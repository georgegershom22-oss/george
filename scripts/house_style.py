from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Tuple, Optional

import matplotlib as mpl
import matplotlib.pyplot as plt


POINTS_PER_INCH = 72.0


def px_to_pt(px: float, dpi: int = 300) -> float:
    """Convert pixels (at given dpi) to points for Matplotlib linewidths."""
    return px * POINTS_PER_INCH / float(dpi)


@dataclass(frozen=True)
class Palette:
    background: str = "#FFFFFF"
    grid: str = "#E5E7EB"  # light gray
    grid_lw_px: float = 0.8

    # Mechanism colors (consistent across thesis)
    classical: str = "#6B7280"  # dark gray
    mode_conversion: str = "#F4A261"  # amber (fills)
    mode_conversion_accent: str = "#C06A00"  # amber accent for lines
    interfacial: str = "#6A4C93"  # purple
    shear: str = "#2A9D8F"  # teal

    centerline: str = "#9CA3AF"  # faint dotted centerline


PALETTE = Palette()


def configure_matplotlib(dpi: int = 300) -> None:
    """Apply global rcParams for the thesis house style."""
    mpl.rcParams.update({
        # Canvas & saving
        "figure.dpi": dpi,
        "savefig.dpi": dpi,
        "figure.facecolor": PALETTE.background,
        "savefig.facecolor": PALETTE.background,
        # Fonts
        "font.family": ["Arial", "Helvetica", "DejaVu Sans", "Liberation Sans", "sans-serif"],
        "mathtext.default": "regular",
        # Keep text as text in SVG; embed TrueType in PDF
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        # Lines
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
        # Axes & grid
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.8,
        # Ticks
        "xtick.direction": "out",
        "ytick.direction": "out",
    })


def create_figure(figsize_px: Tuple[int, int] = (2000, 1400), dpi: int = 300) -> Tuple[plt.Figure, plt.Axes]:
    """Create a 2000×1400 px (default) figure with white background."""
    width_in = figsize_px[0] / dpi
    height_in = figsize_px[1] / dpi
    fig, ax = plt.subplots(figsize=(width_in, height_in), dpi=dpi, constrained_layout=True)
    fig.patch.set_facecolor(PALETTE.background)
    ax.set_facecolor("#FFFFFF")
    return fig, ax


def apply_typography(
    ax: plt.Axes,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    *,
    title_size: int = 28,
    label_size: int = 22,
    tick_size: int = 16,
    title_weight: str = "bold",
) -> None:
    """Apply titles and labels with specified type sizes."""
    if title is not None:
        ax.set_title(title, fontsize=title_size, fontweight=title_weight, pad=10)
    if xlabel is not None:
        ax.set_xlabel(xlabel, fontsize=label_size)
    if ylabel is not None:
        ax.set_ylabel(ylabel, fontsize=label_size)
    ax.tick_params(axis="both", labelsize=tick_size)


def apply_major_grid(ax: plt.Axes, dpi: int = 300) -> None:
    """Apply light gray major grid only."""
    ax.grid(True, which="major", color=PALETTE.grid, linewidth=px_to_pt(PALETTE.grid_lw_px, dpi=dpi))
    ax.grid(False, which="minor")


def set_shared_frequency_axis(ax: plt.Axes) -> None:
    """Set ω/N axis limits and ticks shared across figures."""
    ax.set_xlim(0.2, 2.2)
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])


def add_conversion_overlay(
    ax: plt.Axes,
    *,
    xmin: float = 0.8,
    xmax: float = 1.2,
    center: float = 1.0,
    alpha: float = 0.2,
    dpi: int = 300,
) -> None:
    """Overlay translucent conversion band and dotted centerline at ω/N=1."""
    ax.axvspan(xmin, xmax, color=PALETTE.mode_conversion, alpha=alpha, zorder=0)
    ax.axvline(
        center,
        color=PALETTE.centerline,
        linewidth=px_to_pt(1.2, dpi=dpi),
        linestyle=(0, (1, 3)),  # dotted
        zorder=5,
    )


def add_caption(fig: plt.Figure, caption: str, *, fontsize: int = 15) -> None:
    """Add caption inside canvas under the x-axis."""
    fig.text(0.5, 0.01, caption, ha="center", va="bottom", fontsize=fontsize, style="italic")


def colorbar_right(
    mappable,
    ax: plt.Axes,
    label: str,
    *,
    tick_size: int = 16,
    label_size: int = 18,
):
    cb = plt.colorbar(mappable, ax=ax, pad=0.02)
    cb.ax.tick_params(labelsize=tick_size)
    cb.set_label(label, fontsize=label_size)
    return cb


def ensure_output_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def save_all_formats(fig: plt.Figure, out_basepath: str, *, dpi: int = 300) -> None:
    """Save figure as SVG, PDF, and PNG (PNG at 300 dpi, 2000×1400 px by default)."""
    ensure_output_dir(os.path.dirname(out_basepath))
    fig.savefig(out_basepath + ".svg")
    fig.savefig(out_basepath + ".pdf")
    fig.savefig(out_basepath + ".png", dpi=dpi)
