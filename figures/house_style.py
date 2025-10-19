from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt

# ---------- Constants: Canvas and Style ----------

CANVAS_WIDTH_PX = 2000
CANVAS_HEIGHT_PX = 1400
DEFAULT_DPI = 300

# Margins in pixels (L/R/T/B)
MARGIN_LEFT_PX = 90
MARGIN_RIGHT_PX = 90
MARGIN_TOP_PX = 80
MARGIN_BOTTOM_PX = 110


def px_to_pt(px: float, dpi: int = DEFAULT_DPI) -> float:
    """Convert pixels (at given DPI) to points for Matplotlib linewidths, etc."""
    return px * 72.0 / float(dpi)


# Color palette (color-blind safe where applicable)
COLORS = {
    "deep_blue": "#1F78B4",   # primary curve
    "steel_blue": "#457B9D",  # secondary/envelope
    "magenta": "#B3007D",     # high-contrast accent
    "purple": "#6A4C93",      # kδ=0.1 curve
    "orange": "#F05A28",      # rays and kδ=1 curve
    "teal": "#2A9D8F",        # diffuse curve
    "amber": "#F4A261",       # conversion window band
    "dark_gray": "#555555",   # classical baseline
    "grid": "#E5E7EB",        # subtle grid
    "guide": "#9CA3AF",       # dotted guides
    "charcoal": "#333333",
    "white": "#FFFFFF",
}


def apply_global_rcparams(dpi: int = DEFAULT_DPI) -> None:
    """Apply global rcParams for typography and vector-friendly output."""
    mpl.rcParams.update({
        # Typography
        "font.family": ["Arial", "Helvetica", "DejaVu Sans"],
        "axes.titlesize": 28,
        "axes.labelsize": 22,
        "xtick.labelsize": 16,
        "ytick.labelsize": 16,
        "legend.fontsize": 16,
        # Lines
        "axes.linewidth": px_to_pt(2, dpi),  # ~2 px axes
        "grid.color": COLORS["grid"],
        "grid.linewidth": px_to_pt(0.8, dpi),
        "grid.alpha": 1.0,
        # Save / Vector
        "savefig.dpi": dpi,
        "svg.fonttype": "none",  # keep text as text
        "pdf.fonttype": 42,       # TrueType fonts
        # Mathtext (plain, thesis-friendly)
        "mathtext.fontset": "dejavusans",
        "mathtext.default": "regular",
    })


@dataclass
class CanvasSpec:
    width_px: int = CANVAS_WIDTH_PX
    height_px: int = CANVAS_HEIGHT_PX
    dpi: int = DEFAULT_DPI
    margin_left_px: int = MARGIN_LEFT_PX
    margin_right_px: int = MARGIN_RIGHT_PX
    margin_top_px: int = MARGIN_TOP_PX
    margin_bottom_px: int = MARGIN_BOTTOM_PX

    @property
    def figsize_inches(self) -> Tuple[float, float]:
        return (self.width_px / self.dpi, self.height_px / self.dpi)

    @property
    def axes_rect(self) -> Tuple[float, float, float, float]:
        """Return [left, bottom, width, height] in figure fraction coordinates."""
        left = self.margin_left_px / self.width_px
        right = 1.0 - (self.margin_right_px / self.width_px)
        bottom = self.margin_bottom_px / self.height_px
        top = 1.0 - (self.margin_top_px / self.height_px)
        return (left, bottom, right - left, top - bottom)


def new_canvas(spec: CanvasSpec | None = None) -> Tuple[plt.Figure, plt.Axes]:
    """Create a new figure and a main axes area obeying margins."""
    spec = spec or CanvasSpec()
    apply_global_rcparams(spec.dpi)
    fig = plt.figure(figsize=spec.figsize_inches, dpi=spec.dpi, facecolor=COLORS["white"])
    ax = fig.add_axes(spec.axes_rect, facecolor=COLORS["white"])  # manual margins
    _style_axes(ax, spec)
    return fig, ax


def _style_axes(ax: plt.Axes, spec: CanvasSpec) -> None:
    # Axis line and ticks
    spine_lw = px_to_pt(2, spec.dpi)
    for spine in ax.spines.values():
        spine.set_linewidth(spine_lw)
        spine.set_color("black")
    ax.tick_params(axis="both", which="both",
                   width=px_to_pt(2, spec.dpi),
                   length=6.5,  # in points; visually appropriate
                   direction="out",
                   color="black")
    # Grid (major only)
    ax.grid(True, which="major")
    ax.grid(False, which="minor")


def add_caption(fig: plt.Figure, text: str, spec: CanvasSpec | None = None) -> None:
    """Add an in-canvas caption (italic, 15 pt) above bottom margin."""
    spec = spec or CanvasSpec()
    y = (spec.margin_bottom_px - 10) / spec.height_px  # slight inset above bottom
    fig.text(0.5, y, text, ha="center", va="bottom", fontsize=15, style="italic")


def add_conversion_window(ax: plt.Axes, x0: float = 0.8, x1: float = 1.2, zorder: int = -10) -> None:
    ax.axvspan(x0, x1, color=COLORS["amber"], alpha=0.20, zorder=zorder)


def add_centerline(ax: plt.Axes, x: float = 1.0, dpi: int = DEFAULT_DPI) -> None:
    ax.axvline(x, color=COLORS["guide"], linewidth=px_to_pt(1.0, dpi), linestyle=(0, (1.0, 3.0)))


def set_axes_labels(ax: plt.Axes, xlabel: str | None = None, ylabel: str | None = None) -> None:
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)


def save_figure(fig: plt.Figure, out_base: str, export_svg: bool = True, export_pdf: bool = True,
                export_png: bool = True, dpi: int = DEFAULT_DPI) -> None:
    """Save figure to out_base with SVG/PDF/PNG as requested."""
    if export_svg:
        fig.savefig(f"{out_base}.svg", bbox_inches="tight", facecolor=COLORS["white"])  # text preserved
    if export_pdf:
        fig.savefig(f"{out_base}.pdf", bbox_inches="tight", facecolor=COLORS["white"])  # embed fonts
    if export_png:
        fig.savefig(f"{out_base}.png", bbox_inches="tight", facecolor=COLORS["white"], dpi=dpi)


# Convenience: tick helper for fractional x locations used in the series
FREQ_TICKS = [0.2, 0.5, 0.8, 1.0, 1.2, 2.0, 3.0]


def configure_frequency_axis(ax: plt.Axes, x_min: float = 0.2, x_max: float = 3.5,
                             tight_focus: bool = False) -> None:
    if tight_focus:
        x_max = min(x_max, 2.2)
    ax.set_xlim(x_min, x_max)
    ax.set_xticks(FREQ_TICKS)


def configure_unit_interval_axis(ax: plt.Axes) -> None:
    ax.set_ylim(0.0, 1.0)
    ax.set_yticks([i / 10.0 for i in range(0, 11)])
