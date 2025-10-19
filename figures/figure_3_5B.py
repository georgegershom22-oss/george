from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Rectangle

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


def gaussian(x, mu, sigma):
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def build_transmissivity_curves(F: np.ndarray):
    rng = np.random.default_rng(42)
    # Baseline envelopes near unity
    base_sharp = 0.92 - 0.02 * (F - 1.0)  # gentle tilt
    base_moderate = 0.95 - 0.01 * (F - 1.0)
    base_diffuse = 0.97 - 0.005 * (F - 1.0)

    # Sharp/high-contrast: frequent, deep, narrow notches, quasi-periodic
    notch_centers_sharp = np.arange(0.45, 3.25, 0.25)
    T2_sharp = base_sharp.copy()
    for i, f0 in enumerate(notch_centers_sharp):
        depth = 0.25 + 0.35 * ((i % 5) / 4.0)  # cycle depths 0.25..0.6
        sigma = 0.035 * f0  # 3.5% of center frequency
        T2_sharp -= depth * gaussian(F, f0, sigma)

    # Moderate: fewer/shallower notches
    notch_centers_mod = np.arange(0.6, 3.1, 0.38)
    T2_mod = base_moderate.copy()
    for i, f0 in enumerate(notch_centers_mod):
        depth = 0.12 + 0.16 * ((i % 3) / 2.0)  # ~0.12..0.28
        sigma = 0.045 * f0
        T2_mod -= depth * gaussian(F, f0, sigma)

    # Diffuse/low-contrast: weak, broad undulations only
    T2_diff = base_diffuse.copy()
    T2_diff -= 0.03 * np.cos(2.0 * np.pi * F / 1.8) * np.exp(-0.5 * ((F - 1.5) / 1.8) ** 2)

    # Clamp to [0, 1]
    T2_sharp = np.clip(T2_sharp, 0.0, 1.0)
    T2_mod = np.clip(T2_mod, 0.0, 1.0)
    T2_diff = np.clip(T2_diff, 0.0, 1.0)

    return T2_sharp, T2_mod, T2_diff, notch_centers_sharp


def draw_spacing_arrow(ax: plt.Axes, x0: float, x1: float, y: float):
    arrow = FancyArrowPatch(
        (x0, y), (x1, y),
        arrowstyle="<->",
        mutation_scale=12,
        linewidth=px_to_pt(2),
        color=COLORS["charcoal"],
        linestyle=(0, dash_pixels(1.2, 3.0)),  # subtle dotted
    )
    ax.add_patch(arrow)
    ax.text(0.5 * (x0 + x1), y + 0.03, r"$\Delta(\omega/N) \;\approx\; \mathrm{const.}$", ha="center", va="bottom", fontsize=14)


def main():
    fig = make_figure()
    ax = add_content_axes(fig)

    # Axes spec
    F = np.linspace(0.2, 3.5, 2401)
    x_ticks = [0.2, 0.5, 0.8, 1.0, 1.2, 2.0, 3.0]
    y_ticks = np.round(np.arange(0.0, 1.01, 0.1), 2)
    configure_line_axes(
        ax,
        x_label=r"$\omega/N$",
        y_label=r"Transmissivity $|T|^2$",
        x_ticks=x_ticks,
        y_ticks=y_ticks,
        x_lim=(0.2, 3.5),
        y_lim=(0.0, 1.0),
    )

    # Amber conversion window 0.8-1.2 and dotted center line at 1
    ax.axvspan(0.8, 1.2, color=COLORS["amber"], alpha=0.20, zorder=0)
    ax.axvline(1.0, color=COLORS["dotted_gray"], linewidth=px_to_pt(1.0), linestyle=(0, dash_pixels(2.0, 2.0)))

    # Curves
    T2_sharp, T2_mod, T2_diff, sharp_centers = build_transmissivity_curves(F)

    ax.plot(F, T2_sharp, color=COLORS["magenta"], linewidth=px_to_pt(3), label="Sharp / high-contrast")
    ax.plot(F, T2_mod, color=COLORS["primary_blue"], linewidth=px_to_pt(3), label="Moderate")
    ax.plot(F, T2_diff, color=COLORS["teal"], linewidth=px_to_pt(3), label="Diffuse / low-contrast")

    # Optional baseline (homogeneous, no notches)
    ax.plot(F, 0.96 - 0.01 * (F - 1.0), color=COLORS["dark_gray"], linewidth=px_to_pt(2.0),
            linestyle=(0, dash_pixels(8.0, 6.0)), alpha=0.7)

    # Spacing arrow between two adjacent sharp notches near F~1.4..1.7
    # Pick two neighboring centers around 1.4..1.9
    centers = [c for c in sharp_centers if 1.1 <= c <= 1.9]
    if len(centers) >= 2:
        x0, x1 = centers[0], centers[1]
        draw_spacing_arrow(ax, x0, x1, y=0.88)

    # Legend with amber swatch proxy
    proxy_swatch = Rectangle((0, 0), 1, 1, facecolor=COLORS["amber"], alpha=0.20, edgecolor="none")
    handles = [
        Line2D([], [], color=COLORS["magenta"], linewidth=px_to_pt(3), label="Sharp / high-contrast"),
        Line2D([], [], color=COLORS["primary_blue"], linewidth=px_to_pt(3), label="Moderate"),
        Line2D([], [], color=COLORS["teal"], linewidth=px_to_pt(3), label="Diffuse / low-contrast"),
        proxy_swatch,
    ]
    labels = ["Sharp / high-contrast", "Moderate", "Diffuse / low-contrast", "Conversion window"]
    leg = ax.legend(handles, labels, loc="upper right", frameon=False, fontsize=16)

    add_panel_title(fig, "Figure 3.5B — Transmission vs frequency (three regimes)")
    add_caption(fig, (
        "Figure 3.5B. Transmissivity vs normalized frequency across interface regimes. "
        "Sharp, high-contrast layers exhibit deep, frequent notches; moderate layers show gentler quasi-periodic "
        "structure; diffuse/low-contrast layers are nearly smooth."
    ))

    save_all(fig, "Figure_3_5B")


if __name__ == "__main__":
    main()
