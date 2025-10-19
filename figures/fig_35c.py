from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from .house_style import (
    CanvasSpec,
    COLORS,
    px_to_pt,
    new_canvas,
    set_axes_labels,
    add_caption,
    save_figure,
)


def _reflectivity_family(theta_deg: np.ndarray, kdelta: float) -> np.ndarray:
    """Synthesize R^2(θ) with baseline + interference term controlled by kδ.
    Result is clipped to [0, 1].
    """
    theta_rad = np.deg2rad(theta_deg)
    # Baseline increases with obliquity (Snell-like trend), but kept moderate
    baseline = 0.15 + 0.35 * np.sin(theta_rad) ** 1.2
    # Interference term: amplitude scales with kδ regime
    if kdelta < 0.3:
        alpha = 0.12
        beta = 3.8
    elif kdelta < 2.0:
        alpha = 0.22
        beta = 5.0
    else:
        alpha = 0.08
        beta = 2.2
    phi0 = 0.4
    interference = alpha * np.cos(phi0 + beta * np.sin(theta_rad)) ** 2
    R2 = baseline + interference
    return np.clip(R2, 0.0, 1.0)


def draw_figure(ax: plt.Axes, dpi: int = 300, add_optional_guides: bool = True) -> None:
    # Axes
    ax.set_xlim(0, 80)
    ax.set_xticks([0, 15, 30, 45, 60, 75, 80])
    ax.set_ylim(0, 1)
    ax.set_yticks([i / 10.0 for i in range(0, 11)])
    set_axes_labels(ax, xlabel=r"Incidence $\theta$ (deg)", ylabel=r"Reflectivity $|R|^2$")

    theta = np.linspace(0, 80, 1500)

    lw3 = px_to_pt(3.0, dpi)

    # Curves for kδ = 0.1, 1, 3
    R2_thin = _reflectivity_family(theta, 0.1)
    R2_res = _reflectivity_family(theta, 1.0)
    R2_thick = _reflectivity_family(theta, 3.0)

    ax.plot(theta, R2_thin, color=COLORS["purple"], lw=lw3, label=r"$k\delta=0.1$")
    ax.plot(theta, R2_res, color=COLORS["orange"], lw=lw3, label=r"$k\delta=1$")
    ax.plot(theta, R2_thick, color=COLORS["teal"], lw=lw3, label=r"$k\delta=3$")

    # Optional dotted guide at 35° or 55°
    if add_optional_guides:
        for th in (55,):
            ax.axvline(th, color=COLORS["guide"], lw=px_to_pt(1.0, dpi), ls=(0, (1.0, 3.0)))

    # Arrowed labels
    # Find local maxima regions for annotations placement
    ax.text(50, 0.78, "sharp layers → strong angular lobes", color=COLORS["purple"], fontsize=18)
    ax.text(60, 0.38, "diffuse layers → muted angular dependence", color=COLORS["teal"], fontsize=18)

    # Legend with small note
    leg = ax.legend(loc="upper right", frameon=False, title=None)
    handles = getattr(leg, "legend_handles", None) or getattr(leg, "legendHandles", None)
    if handles:
        for lh in handles:
            try:
                lh.set_linewidth(lw3)
            except Exception:
                pass
    ax.text(0.98, 0.90, r"$C_Z$ fixed; $\omega/N$ fixed (representative)",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=14)


def generate(out_base: str, export_svg: bool = True, export_pdf: bool = True,
             export_png: bool = True, dpi: int = 300) -> None:
    spec = CanvasSpec(dpi=dpi)
    fig, ax = new_canvas(spec)
    draw_figure(ax, dpi=dpi)
    add_caption(
        fig,
        "Figure 3.5C. Reflectivity vs incidence for thickness parameter kδ at fixed contrast. "
        "Thin/sharp layers yield pronounced obliquity-dependent lobes; diffuse layers produce smoother, muted trends.",
        spec,
    )
    save_figure(fig, out_base, export_svg=export_svg, export_pdf=export_pdf, export_png=export_png, dpi=dpi)
    plt.close(fig)
