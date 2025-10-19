from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from figures.common_style import (
    make_figure,
    add_content_axes,
    add_panel_title,
    add_caption,
    configure_line_axes,
    save_all,
    COLORS,
    px_to_pt,
    dash_pixels,
)


def reflectivity_family(theta_deg: np.ndarray, kind: str) -> np.ndarray:
    theta = np.radians(theta_deg)

    # Baseline increasing with obliquity
    base = 0.18 + 0.55 * np.sin(theta) ** 2

    # Interference term strength and angular density depend on kind (kδ)
    if kind == "thin":  # kδ=0.1
        alpha = 0.12
        beta = 2.5
    elif kind == "resonant":  # kδ=1
        alpha = 0.22
        beta = 3.8
    elif kind == "thick":  # kδ=3
        alpha = 0.07
        beta = 1.6
    else:
        raise ValueError("unknown kind")

    phi0 = 0.6
    interference = alpha * np.cos(phi0 + beta * np.sin(theta)) ** 2

    R2 = base + interference - 0.15  # offset to keep within [0,1]
    return np.clip(R2, 0.0, 1.0)


def main():
    fig = make_figure()
    ax = add_content_axes(fig)

    x_ticks = [0, 15, 30, 45, 60, 75, 80]
    y_ticks = np.round(np.arange(0.0, 1.01, 0.1), 2)
    configure_line_axes(
        ax,
        x_label=r"Incidence angle $\theta$ (deg)",
        y_label=r"Reflectivity $|R|^2$",
        x_ticks=x_ticks,
        y_ticks=y_ticks,
        x_lim=(0.0, 80.0),
        y_lim=(0.0, 1.0),
    )

    theta = np.linspace(0.0, 80.0, 1601)
    R2_thin = reflectivity_family(theta, "thin")
    R2_res = reflectivity_family(theta, "resonant")
    R2_thick = reflectivity_family(theta, "thick")

    ax.plot(theta, R2_thin, color=COLORS["purple"], linewidth=px_to_pt(3), label=r"$k\delta=0.1$ (thin/sharp)")
    ax.plot(theta, R2_res, color=COLORS["orange"], linewidth=px_to_pt(3), label=r"$k\delta=1$ (resonant)")
    ax.plot(theta, R2_thick, color=COLORS["teal"], linewidth=px_to_pt(3), label=r"$k\delta=3$ (thick/diffuse)")

    # Optional vertical dotted guide at 55°
    ax.axvline(55.0, color=COLORS["dotted_gray"], linewidth=px_to_pt(1.0), linestyle=(0, (px_to_pt(2.0), px_to_pt(2.0))))

    # Callouts
    ax.text(42, 0.78, "sharp layers → strong angular lobes", color=COLORS["purple"], fontsize=16)
    ax.text(58, 0.28, "diffuse layers → muted angular dependence", color=COLORS["teal"], fontsize=16)

    leg = ax.legend(loc="upper right", frameon=False, fontsize=16, title=" ")
    ax.text(0.985, 0.88, r"$C_Z$ fixed; $\,\omega/N$ fixed (representative)", transform=ax.transAxes,
            ha="right", va="top", fontsize=12, color=COLORS["charcoal"]) 

    add_panel_title(fig, "Figure 3.5C — Reflectivity vs incidence angle")
    add_caption(fig, (
        "Figure 3.5C. Reflectivity vs incidence for thickness parameter $k\delta$ at fixed contrast. "
        "Thin/sharp layers yield pronounced obliquity-dependent lobes; diffuse layers produce smoother, muted trends."
    ))

    save_all(fig, "Figure_3_5C")


if __name__ == "__main__":
    main()
