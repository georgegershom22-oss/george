from __future__ import annotations

import math
from pathlib import Path
from typing import Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt

# ===== House style constants =====
FIG_W_PX = 2000
FIG_H_PX = 1400
FIG_DPI = 200  # yields 10in x 7in

# Canvas margins in pixels
MARGIN_L_PX = 90
MARGIN_R_PX = 90
MARGIN_T_PX = 80
MARGIN_B_PX = 110

# Derived content rect (in pixels)
CONTENT_W_PX = FIG_W_PX - MARGIN_L_PX - MARGIN_R_PX
CONTENT_H_PX = FIG_H_PX - MARGIN_T_PX - MARGIN_B_PX

# Colors (color-blind safe palette + neutrals)
COLORS = {
    "primary_blue": "#1F78B4",   # primary curve
    "steel_blue": "#457B9D",     # secondary
    "magenta": "#B3007D",        # accent / sharp-layer
    "purple": "#6A4C93",         # thin/sharp in 3.5C
    "teal": "#2A9D8F",           # diffuse/low-contrast / thick
    "orange": "#F05A28",         # acoustic rays; resonant in 3.5C
    "amber": "#F4A261",          # conversion window band
    "dark_gray": "#555555",      # classical baseline
    "dotted_gray": "#9CA3AF",    # dotted guides
    "grid_gray": "#E5E7EB",      # subtle grid
    "charcoal": "#333333",       # text / strokes
    "water_top": "#B3D7FF",      # stratified gradient (top)
    "water_bottom": "#0B3C5D",   # stratified gradient (bottom)
}

# Typography
FONTS = {
    "family": "sans-serif",
    "sans_serif": ["Helvetica", "Arial", "DejaVu Sans"],
    # Sizes in points
    "title": 28,
    "axis": 22,
    "ticks": 16,
    "legend": 16,
    "callout": 18,
    "caption": 15,
}

# Matplotlib global configuration for vector-clean outputs
mpl.rcParams.update({
    "figure.dpi": FIG_DPI,
    "savefig.dpi": 300,  # ensure crisp PNG export
    "font.family": FONTS["family"],
    "font.sans-serif": FONTS["sans_serif"],
    "mathtext.fontset": "dejavusans",
    "axes.titlesize": FONTS["title"],
    "axes.labelsize": FONTS["axis"],
    "xtick.labelsize": FONTS["ticks"],
    "ytick.labelsize": FONTS["ticks"],
    "axes.edgecolor": COLORS["charcoal"],
    "text.color": COLORS["charcoal"],
    "axes.labelcolor": COLORS["charcoal"],
    "xtick.color": COLORS["charcoal"],
    "ytick.color": COLORS["charcoal"],
    # Keep text editable in SVG/PDF; convert if needed downstream
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    # Lines
    "lines.solid_capstyle": "round",
})


def px_to_pt(pixels: float, dpi: float = FIG_DPI) -> float:
    """Convert pixels to points for linewidths/dashes.

    Matplotlib linewidth/dash units are points. 1pt = 1/72 in.
    """
    return pixels * 72.0 / dpi


def figure_pixels() -> Tuple[int, int, int]:
    """Return (width_px, height_px, dpi)."""
    return FIG_W_PX, FIG_H_PX, FIG_DPI


def make_figure() -> plt.Figure:
    """Create a figure with the exact 2000x1400 px canvas."""
    fig = plt.figure(figsize=(FIG_W_PX / FIG_DPI, FIG_H_PX / FIG_DPI), dpi=FIG_DPI, layout=None)
    fig.set_facecolor("white")
    return fig


def add_axes_in_pixels(fig: plt.Figure, left_px: float, bottom_px: float, width_px: float, height_px: float) -> plt.Axes:
    """Add axes using pixel-based placement relative to the full figure."""
    left = left_px / FIG_W_PX
    bottom = bottom_px / FIG_H_PX
    width = width_px / FIG_W_PX
    height = height_px / FIG_H_PX
    ax = fig.add_axes([left, bottom, width, height])
    return ax


def content_rect_px() -> Tuple[int, int, int, int]:
    """Return the content rectangle as (left_px, bottom_px, width_px, height_px)."""
    return MARGIN_L_PX, MARGIN_B_PX, CONTENT_W_PX, CONTENT_H_PX


def add_content_axes(fig: plt.Figure) -> plt.Axes:
    """Add a full content-area axes (inside margins)."""
    L, B, W, H = content_rect_px()
    return add_axes_in_pixels(fig, L, B, W, H)


def configure_line_axes(ax: plt.Axes, x_label: str, y_label: str, *,
                        x_ticks=None, y_ticks=None, x_lim=None, y_lim=None,
                        major_grid: bool = True) -> None:
    """Apply house style to a line-plot axes.

    - Major grid only, subtle gray
    - Axes spines 2 px; tick width 2 px
    """
    if x_lim is not None:
        ax.set_xlim(*x_lim)
    if y_lim is not None:
        ax.set_ylim(*y_lim)

    if x_ticks is not None:
        ax.set_xticks(x_ticks)
    if y_ticks is not None:
        ax.set_yticks(y_ticks)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    for spine in ax.spines.values():
        spine.set_linewidth(px_to_pt(2))
        spine.set_capstyle("round")

    ax.tick_params(width=px_to_pt(2), length=px_to_pt(8))

    if major_grid:
        ax.grid(True, which="major", color=COLORS["grid_gray"], linewidth=px_to_pt(0.8))
        ax.grid(False, which="minor")


def add_panel_title(fig: plt.Figure, text: str) -> None:
    """Panel title at top-left inside content area, 28 pt bold."""
    L, B, W, H = content_rect_px()
    # Place slightly below the top margin
    fig.text(
        (L + 4) / FIG_W_PX,  # tiny inset
        (B + H + 10) / FIG_H_PX,
        text,
        fontsize=FONTS["title"],
        fontweight="bold",
        ha="left",
        va="bottom",
    )


def add_caption(fig: plt.Figure, text: str) -> None:
    """Caption line inside canvas under the axes, 15 pt italics."""
    L, B, W, H = content_rect_px()
    fig.text(
        (L + 2) / FIG_W_PX,
        (B - 8) / FIG_H_PX,
        text,
        fontsize=FONTS["caption"],
        style="italic",
        ha="left",
        va="top",
    )


def ensure_outdir(outdir: Path | str) -> Path:
    out_path = Path(outdir)
    out_path.mkdir(parents=True, exist_ok=True)
    return out_path


def save_all(fig: plt.Figure, basename: str, outdir: Path | str = "figures/exports") -> None:
    out_path = ensure_outdir(outdir)
    stem = out_path / basename
    # SVG (master), PDF (submission), PNG 300 dpi (sharing)
    fig.savefig(stem.with_suffix(".svg"), transparent=False, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".pdf"), transparent=False, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".png"), dpi=300, transparent=False, bbox_inches="tight")


def dash_pixels(on_px: float, off_px: float) -> Tuple[float, float]:
    """Return (on, off) dash lengths in points from pixel specs."""
    return (px_to_pt(on_px), px_to_pt(off_px))
