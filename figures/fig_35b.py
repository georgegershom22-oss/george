from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from .house_style import (
    CanvasSpec,
    COLORS,
    px_to_pt,
    new_canvas,
    add_conversion_window,
    add_centerline,
    set_axes_labels,
    configure_frequency_axis,
    configure_unit_interval_axis,
    add_caption,
    save_figure,
)


def _envelope(F: np.ndarray) -> np.ndarray:
    """A gentle baseline envelope E(F) in [0.7, 1.0] that is smooth."""
    # Smooth, slightly varying envelope to avoid perfectly flat baseline
    return 0.92 - 0.06 * np.exp(-((F - 1.2) ** 2) / (2 * 0.5 ** 2))


def _gaussian_dips(F: np.ndarray, centers: np.ndarray, depths: np.ndarray, widths: np.ndarray) -> np.ndarray:
    """Product of Gaussian notches with given centers, depths (0..1), and widths (sigma)."""
    T = np.ones_like(F)
    for c, d, s in zip(centers, depths, widths):
        T *= (1.0 - d * np.exp(-((F - c) ** 2) / (2 * s ** 2)))
    return T


def _sharp_curve(F: np.ndarray) -> np.ndarray:
    # Quasi-periodic notch centers with roughly constant spacing ΔF
    centers = np.arange(0.55, 3.35, 0.24)
    # Depths 0.25–0.6 distributed with slight randomness for realism
    rng = np.random.default_rng(42)
    depths = rng.uniform(0.25, 0.6, size=centers.size)
    # Width ~ 3.5% of center frequency
    widths = 0.035 * centers
    T = _envelope(F) * _gaussian_dips(F, centers, depths, widths)
    return np.clip(T, 0.0, 1.0)


def _moderate_curve(F: np.ndarray) -> np.ndarray:
    # Fewer, shallower notches (skip every other sharp center)
    centers = np.arange(0.65, 3.25, 0.48)
    rng = np.random.default_rng(7)
    depths = rng.uniform(0.12, 0.35, size=centers.size)
    widths = 0.045 * centers
    T = _envelope(F) * _gaussian_dips(F, centers, depths, widths)
    return np.clip(T, 0.0, 1.0)


def _diffuse_curve(F: np.ndarray) -> np.ndarray:
    # Weak, broad undulation; essentially smooth
    base = _envelope(F)
    ripple = 0.03 * np.sin(2 * np.pi * (F - 0.2) / 1.4)
    T = base * (1.0 - ripple)
    return np.clip(T, 0.0, 1.0)


def draw_figure(ax: plt.Axes, tight_focus: bool = False, dpi: int = 300) -> None:
    # Axes limits and labels
    configure_frequency_axis(ax, tight_focus=tight_focus)
    configure_unit_interval_axis(ax)
    set_axes_labels(ax, xlabel=r"$\omega/N$", ylabel=r"Transmissivity $|T|^2$")

    # Overlays
    add_conversion_window(ax, 0.8, 1.2)
    add_centerline(ax, 1.0, dpi=dpi)

    # Domain
    x_min, x_max = ax.get_xlim()
    F = np.linspace(x_min, x_max, 2000)

    # Curves
    lw3 = px_to_pt(3.0, dpi)
    ax.plot(F, _sharp_curve(F), color=COLORS["magenta"], lw=lw3, label="Sharp / high-contrast")
    ax.plot(F, _moderate_curve(F), color=COLORS["deep_blue"], lw=lw3, label="Moderate")
    ax.plot(F, _diffuse_curve(F), color=COLORS["teal"], lw=lw3, label="Diffuse / low-contrast")

    # Optional baseline (homogeneous, dashed)
    baseline = _envelope(F)
    ax.plot(F, baseline, color=COLORS["dark_gray"], lw=px_to_pt(2.0, dpi), ls=(0, (8, 6)), alpha=0.8)

    # Double-headed arrow between two adjacent sharp notches to indicate Δ(ω/N) ≈ const.
    # Identify notches from centers used in _sharp_curve
    centers = np.arange(0.55, 3.35, 0.24)
    # Pick two adjacent centers near mid-band
    if len(centers) >= 2:
        c1_idx = len(centers) // 2
        c0_idx = c1_idx - 1
        c0, c1 = centers[c0_idx], centers[c1_idx]
        y_arrow = 0.92  # place arrow high above curves
        ax.annotate(
            "",
            xy=(c0, y_arrow),
            xytext=(c1, y_arrow),
            arrowprops=dict(arrowstyle="<->", color=COLORS["charcoal"], lw=px_to_pt(1.2, dpi)),
        )
        ax.text((c0 + c1) / 2.0, y_arrow + 0.03, r"$\Delta(\omega/N) \approx \text{const.}$",
                ha="center", va="bottom", fontsize=16)

    # Legend
    leg = ax.legend(loc="upper right", frameon=False)
    # Matplotlib >=3.8 exposes `legend_handles`; older versions used `legendHandles`.
    handles = getattr(leg, "legend_handles", None) or getattr(leg, "legendHandles", None)
    if handles:
        for lh in handles:
            try:
                lh.set_linewidth(lw3)
            except Exception:
                # Some handle types may not support linewidth adjustments
                pass


def generate(out_base: str, tight_focus: bool = False, export_svg: bool = True,
             export_pdf: bool = True, export_png: bool = True, dpi: int = 300) -> None:
    spec = CanvasSpec(dpi=dpi)
    fig, ax = new_canvas(spec)
    draw_figure(ax, tight_focus=tight_focus, dpi=dpi)
    add_caption(
        fig,
        "Figure 3.5B. Transmissivity vs normalized frequency across interface regimes. "
        "Sharp, high-contrast layers exhibit deep, frequent notches; moderate layers show "
        "gentler quasi-periodic structure; diffuse/low-contrast layers are nearly smooth.",
        spec,
    )
    save_figure(fig, out_base, export_svg=export_svg, export_pdf=export_pdf, export_png=export_png, dpi=dpi)
    plt.close(fig)
