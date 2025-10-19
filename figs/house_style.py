"""
Shared house style for Figures 3.6A–C.
Outputs 1800×1200 px canvas (landscape) with consistent typography,
colors, grids, overlays, legends, and captions.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, Tuple

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize


# -----------------------------
# Constants and palette
# -----------------------------
@dataclass(frozen=True)
class HouseStyle:
    # Canvas
    canvas_width_px: int = 1800
    canvas_height_px: int = 1200
    dpi: int = 100  # 18×12 inches at 100 dpi -> 1800×1200 px

    # Typography (points)
    font_family: str = "sans-serif"
    font_sans_fallbacks: Tuple[str, ...] = (
        "Helvetica",
        "Arial",
        "DejaVu Sans",
        "Liberation Sans",
        "Nimbus Sans",
    )
    title_size_pt: int = 28
    label_size_pt: int = 22
    tick_size_pt: int = 16
    note_size_pt: int = 18  # in-plot notes 18–20 pt
    caption_size_pt: int = 15

    # Grid
    grid_color: str = "#E5E7EB"
    grid_px: float = 0.8  # thin 0.8 px

    # Conversion band
    conversion_color: str = "#F4A261"
    conversion_alpha: float = 0.20
    conversion_center_color: str = "#9CA3AF"
    conversion_center_px: float = 1.0

    # Palette (color-blind robust)
    deep_blue: str = "#1F78B4"   # primary
    steel_blue: str = "#457B9D"  # secondary
    contrast_magenta: str = "#B3007D"

    # Heatmap colormap (darker = higher)
    cmap_name: str = "cividis_r"  # reversed so darker = higher

    # Shared axes ticks
    freq_ticks: Tuple[float, ...] = (0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0)
    freq_min: float = 0.2
    freq_max: float = 2.2

    ri_ticks: Tuple[float, ...] = (0.0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0)
    ri_min: float = 0.0
    ri_max: float = 2.0


STYLE = HouseStyle()


# -----------------------------
# RC configuration
# -----------------------------

def apply_house_style() -> None:
    mpl.rcParams.update({
        "figure.dpi": STYLE.dpi,
        "savefig.dpi": STYLE.dpi,
        "figure.figsize": (STYLE.canvas_width_px / STYLE.dpi, STYLE.canvas_height_px / STYLE.dpi),
        "font.family": STYLE.font_family,
        "font.sans-serif": list(STYLE.font_sans_fallbacks),
        "axes.titlesize": STYLE.title_size_pt,
        "axes.labelsize": STYLE.label_size_pt,
        "axes.titleweight": "bold",
        "xtick.labelsize": STYLE.tick_size_pt,
        "ytick.labelsize": STYLE.tick_size_pt,
        "legend.frameon": False,
        "legend.fontsize": STYLE.tick_size_pt,
        "mathtext.fontset": "dejavusans",
    })


def points_from_pixels(px: float, dpi: int | None = None) -> float:
    if dpi is None:
        dpi = STYLE.dpi
    # 1 pt = 1/72 inch; px = dpi * inch => pt = 72 * inch = 72 * px / dpi
    return 72.0 * (px / float(dpi))


# -----------------------------
# Axes helpers
# -----------------------------

def set_freq_axis(ax: plt.Axes, axis: str = "x", label: str | None = None) -> None:
    label_text = label if label is not None else r"Normalized frequency $\omega/N$"
    if axis == "x":
        ax.set_xlim(STYLE.freq_min, STYLE.freq_max)
        ax.set_xticks(list(STYLE.freq_ticks))
        ax.set_xlabel(label_text)
    else:
        ax.set_ylim(STYLE.freq_min, STYLE.freq_max)
        ax.set_yticks(list(STYLE.freq_ticks))
        ax.set_ylabel(label_text)


def set_ri_axis(ax: plt.Axes, axis: str = "y", label: str | None = None) -> None:
    label_text = label if label is not None else r"$R_i$"
    if axis == "y":
        ax.set_ylim(STYLE.ri_min, STYLE.ri_max)
        ax.set_yticks(list(STYLE.ri_ticks))
        ax.set_ylabel(label_text)
    else:
        ax.set_xlim(STYLE.ri_min, STYLE.ri_max)
        ax.set_xticks(list(STYLE.ri_ticks))
        ax.set_xlabel(label_text)


def style_grid(ax: plt.Axes) -> None:
    lw_pt = points_from_pixels(STYLE.grid_px)
    ax.grid(True, which="major", color=STYLE.grid_color, linewidth=lw_pt)


def overlay_conversion_band(ax: plt.Axes, align_to: str = "x") -> None:
    # 0.8 <= omega/N <= 1.2 with dotted centerline at 1.0
    if align_to == "x":
        ax.axvspan(0.8, 1.2, color=STYLE.conversion_color, alpha=STYLE.conversion_alpha, lw=0)
        ax.axvline(1.0, color=STYLE.conversion_center_color, linestyle=(0, (2, 4)),
                   linewidth=points_from_pixels(STYLE.conversion_center_px))
    else:
        ax.axhspan(0.8, 1.2, color=STYLE.conversion_color, alpha=STYLE.conversion_alpha, lw=0)
        ax.axhline(1.0, color=STYLE.conversion_center_color, linestyle=(0, (2, 4)),
                   linewidth=points_from_pixels(STYLE.conversion_center_px))


def add_panel_title(ax: plt.Axes, text: str) -> None:
    ax.text(0.01, 0.99, text, transform=ax.transAxes, va="top", ha="left",
            fontsize=STYLE.title_size_pt, fontweight="bold")


def add_caption(ax: plt.Axes, text: str) -> None:
    # Place inside canvas, under x-axis area
    ax.text(0.5, -0.18, text, transform=ax.transAxes, va="top", ha="center",
            fontsize=STYLE.caption_size_pt, fontstyle="italic")


def add_colorbar(fig: plt.Figure, mappable, label: str, ticks: Iterable[float] | None = None,
                 ax: plt.Axes | None = None, pad: float = 0.02, shrink: float = 0.9) -> mpl.colorbar.Colorbar:
    cbar = fig.colorbar(mappable, ax=ax, pad=pad, shrink=shrink)
    cbar.outline.set_visible(False)
    if ticks is not None:
        cbar.set_ticks(list(ticks))
    cbar.ax.tick_params(labelsize=STYLE.tick_size_pt)
    cbar.set_label(label, fontsize=STYLE.label_size_pt)
    return cbar


def create_canvas(ncols: int = 1, nrows: int = 1, wspace_px: float | None = None, hspace_px: float | None = None):
    apply_house_style()
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(STYLE.canvas_width_px / STYLE.dpi,
                                                                STYLE.canvas_height_px / STYLE.dpi))
    # Normalize to array of axes
    if isinstance(axes, np.ndarray):
        pass
    else:
        axes = np.array([axes])

    # Pixel-based gutters
    if wspace_px is not None or hspace_px is not None:
        wspace = 0.0
        hspace = 0.0
        fig_w_in, fig_h_in = fig.get_size_inches()
        if wspace_px is not None:
            # wspace is a fraction of the average axes width
            axes_width_in = fig_w_in / max(1, ncols)
            wspace = (wspace_px / STYLE.dpi) / axes_width_in
        if hspace_px is not None:
            axes_height_in = fig_h_in / max(1, nrows)
            hspace = (hspace_px / STYLE.dpi) / axes_height_in
        fig.subplots_adjust(wspace=wspace, hspace=hspace)

    return fig, axes


def save_figure(fig: plt.Figure, out_basepath: str) -> None:
    os.makedirs(os.path.dirname(out_basepath), exist_ok=True)
    fig.savefig(out_basepath + ".png", facecolor="white", bbox_inches="tight")
    fig.savefig(out_basepath + ".svg", facecolor="white", bbox_inches="tight")


# -----------------------------
# Heatmap helper
# -----------------------------

def show_heatmap(ax: plt.Axes, Z: np.ndarray, extent: Tuple[float, float, float, float],
                 vmin: float = 0.0, vmax: float = 1.0, cmap: str | None = None):
    cmap_to_use = cmap or STYLE.cmap_name
    norm = Normalize(vmin=vmin, vmax=vmax)
    im = ax.imshow(Z, origin="lower", extent=extent, aspect="auto", cmap=cmap_to_use, norm=norm)
    return im
