from __future__ import annotations

import math
import os
from typing import Tuple

import numpy as np
import matplotlib.pyplot as plt

from house_style import (
    PALETTE,
    configure_matplotlib,
    create_figure,
    apply_typography,
    apply_major_grid,
    set_shared_frequency_axis,
    add_conversion_overlay,
    add_caption,
    colorbar_right,
    px_to_pt,
    save_all_formats,
)
from colormaps import dominance_cmap, strength_cmap

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


# ------------------------ Helper fields (schematic) ------------------------ #

def dominance_field(Ri: np.ndarray, w_over_N: np.ndarray) -> np.ndarray:
    """Schematic dominance index D in [0,1]. 0=conversion (amber), 1=shear (teal).

    Structure: conversion basin near w/N=1 at higher Ri; shear tongue at low Ri.
    """
    W, R = np.meshgrid(w_over_N, Ri)

    # Conversion basin: Gaussian around w=1, stronger at higher Ri (via logistic in R)
    conv_peak = np.exp(-0.5 * ((W - 1.0) / 0.18) ** 2)
    conv_R_gain = 1.0 / (1.0 + np.exp(-12.0 * (R - 0.7)))  # ramps up above Ri~0.7
    conv_activity = conv_peak * conv_R_gain

    # Shear tongue: strongest at low Ri, centered around w=1 with broader tails to w>1
    shear_center = np.exp(-0.5 * ((W - 1.0) / 0.35) ** 2)
    shear_R_gain = 1.0 / (1.0 + np.exp(12.0 * (R - 0.5)))  # high for Ri<~0.5
    shear_activity = shear_center * shear_R_gain * (1.0 - 0.25 * np.tanh((W - 1.4) / 0.5))

    # Map activities into dominance index D in [0,1]
    # Use softmax-like mapping: D ~ shear / (shear + conv + eps)
    eps = 1e-6
    D = shear_activity / (shear_activity + conv_activity + eps)

    # Smooth and lightly bias towards 0.5 near low activity to produce pale neutral mid
    total_act = shear_activity + conv_activity
    low_act_mask = total_act < 0.2
    D = np.where(low_act_mask, 0.5 * D + 0.5 * 0.5, D)

    return np.clip(D, 0.0, 1.0)


def conversion_activity_levels(Ri: np.ndarray, w_over_N: np.ndarray) -> np.ndarray:
    W, R = np.meshgrid(w_over_N, Ri)
    conv_peak = np.exp(-0.5 * ((W - 1.0) / 0.18) ** 2)
    conv_R_gain = 1.0 / (1.0 + np.exp(-12.0 * (R - 0.7)))
    return conv_peak * conv_R_gain


def shear_activity_levels(Ri: np.ndarray, w_over_N: np.ndarray) -> np.ndarray:
    W, R = np.meshgrid(w_over_N, Ri)
    shear_center = np.exp(-0.5 * ((W - 1.0) / 0.35) ** 2)
    shear_R_gain = 1.0 / (1.0 + np.exp(12.0 * (R - 0.5)))
    return shear_center * shear_R_gain


# ------------------------------ Figure 3.8A ------------------------------ #

def figure_38A() -> None:
    dpi = 300
    configure_matplotlib(dpi=dpi)
    fig, ax = create_figure(figsize_px=(2000, 1400), dpi=dpi)

    # Domain
    w = np.linspace(0.2, 2.2, 400)
    Ri = np.linspace(0.0, 2.0, 300)

    D = dominance_field(Ri, w)

    im = ax.imshow(
        D,
        origin="lower",
        extent=[w.min(), w.max(), Ri.min(), Ri.max()],
        aspect="auto",
        cmap=dominance_cmap(),
        vmin=0.0,
        vmax=1.0,
        interpolation="bicubic",
    )

    # Activity contours
    conv_levels = [0.35, 0.55]
    shear_levels = [0.35, 0.55]
    conv_act = conversion_activity_levels(Ri, w)
    shear_act = shear_activity_levels(Ri, w)

    # Solid amber for conversion activity
    cs1 = ax.contour(
        w,
        Ri,
        conv_act,
        levels=conv_levels,
        colors=PALETTE.mode_conversion_accent,
        linewidths=px_to_pt(2.5, dpi=dpi),
    )

    # Dashed teal for shear activity
    cs2 = ax.contour(
        w,
        Ri,
        shear_act,
        levels=shear_levels,
        colors=PALETTE.shear,
        linewidths=px_to_pt(2.5, dpi=dpi),
        linestyles=(0, (8, 6)),
    )

    # Overlay band and centerline
    add_conversion_overlay(ax, dpi=dpi)

    # Axes & labels
    set_shared_frequency_axis(ax)
    ax.set_ylim(0.0, 2.0)
    ax.set_yticks([0.0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
    apply_typography(
        ax,
        title="Figure 3.8A — Dominant pathway in (Ri, ω/N)",
        xlabel="ω/N",
        ylabel="Ri",
    )
    apply_major_grid(ax, dpi=dpi)

    # Colorbar
    colorbar_right(im, ax, label="Dominant pathway index D (0 = conversion, 1 = shear)")

    # Micro-labels
    ax.text(1.05, 1.6, "conversion basin", color=PALETTE.mode_conversion_accent, fontsize=18)
    ax.text(1.15, 0.35, "shear tongue (marginal Ri)", color=PALETTE.shear, fontsize=18)

    # Caption
    add_caption(
        fig,
        "Figure 3.8A. Predicted dominant pathway map for continuous stratification. Conversion dominates near ω/N≈1 at higher Ri; shear dominates under marginal Ri, especially around the conversion band.",
    )

    # Legend-like labels for contour styles
    # Keep legend simple and inside axes without frame
    from matplotlib.lines import Line2D

    legend_lines = [
        Line2D([0], [0], color=PALETTE.mode_conversion_accent, lw=px_to_pt(3, dpi=dpi)),
        Line2D([0], [0], color=PALETTE.shear, lw=px_to_pt(3, dpi=dpi), linestyle=(0, (8, 6))),
    ]
    ax.legend(
        legend_lines,
        ["conversion activity", "shear activity"],
        loc="upper left",
        frameon=False,
        fontsize=16,
    )

    # Save
    save_all_formats(fig, os.path.join(OUTPUT_DIR, "figure_3_8A"), dpi=dpi)


# ------------------------------ Figure 3.8B ------------------------------ #

def notch_strength_field(CZ: np.ndarray, kdelta: np.ndarray) -> np.ndarray:
    """Schematic notch strength S in [0,1]: increases with CZ, decreases with kδ."""
    K, C = np.meshgrid(kdelta, CZ)
    # Monotone mapping; use logistic in log10(k) for smooth decay, and sqrt in CZ for stronger top-end
    k_term = 1.0 / (1.0 + np.exp(3.0 * (np.log10(K) - 0.0)))  # ~high at k<1, drops for k>1
    c_term = np.sqrt(np.clip(C, 0.0, 1.0)) / np.sqrt(0.4)
    S = np.clip(0.15 + 0.85 * (c_term * k_term), 0.0, 1.0)
    return S


def figure_38B() -> None:
    dpi = 300
    configure_matplotlib(dpi=dpi)
    fig, ax = create_figure(figsize_px=(2000, 1400), dpi=dpi)

    # Domain (log x)
    k = np.geomspace(0.1, 3.0, 300)
    CZ = np.linspace(0.0, 0.40, 240)

    S = notch_strength_field(CZ, k)

    im = ax.imshow(
        S,
        origin="lower",
        extent=[k.min(), k.max(), CZ.min(), CZ.max()],
        aspect="auto",
        cmap=strength_cmap(),
        vmin=0.0,
        vmax=1.0,
        interpolation="bicubic",
    )
    ax.set_xscale("log")

    # Isolines
    levels = [0.3, 0.6, 0.85]
    cs = ax.contour(
        k,
        CZ,
        S,
        levels=levels,
        colors=PALETTE.classical,
        linewidths=px_to_pt(2.0, dpi=dpi),
        linestyles=(0, (8, 6)),
    )
    fmt = {lvl: label for lvl, label in zip(levels, ["weak", "moderate", "strong"])}
    ax.clabel(cs, cs.levels, inline=True, fmt=fmt, fontsize=16)

    # Axes & labels
    ax.set_xlim(0.1, 3.0)
    ax.set_xticks([0.1, 0.2, 0.5, 1.0, 2.0, 3.0])
    ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
    ax.get_xaxis().set_minor_formatter(plt.NullFormatter())

    ax.set_ylim(0.00, 0.40)
    ax.set_yticks([0.00, 0.10, 0.20, 0.30, 0.40])

    apply_typography(
        ax,
        title="Figure 3.8B — Layered regime map in (CZ, kδ)",
        xlabel="kδ",
        ylabel="CZ = |Z₂−Z₁|/(Z₂+Z₁)",
    )
    apply_major_grid(ax, dpi=dpi)

    # Optional insets: three-strip TL(f) sketches at right margin
    # Keep tiny and schematic (lines only)
    inset_left = 0.82
    inset_width = 0.15
    heights = [0.72, 0.50, 0.28]
    for i, y in enumerate(heights):
        inset_ax = fig.add_axes([inset_left, y, inset_width, 0.12])
        inset_ax.set_facecolor("#FFFFFF")
        x = np.linspace(0, 1, 400)
        if i == 0:  # strong comb
            yv = -10 * np.log10(1 + 12 * np.sin(12 * np.pi * x) ** 2) + 1
        elif i == 1:  # moderate
            yv = -10 * np.log10(1 + 5 * np.sin(8 * np.pi * x) ** 2)
        else:  # weak ripples
            yv = -10 * np.log10(1 + 2 * np.sin(4 * np.pi * x) ** 2) + 1
        inset_ax.plot(x, yv, color=PALETTE.interfacial, lw=px_to_pt(2.0, dpi=dpi))
        inset_ax.set_xticks([])
        inset_ax.set_yticks([])
        for spine in inset_ax.spines.values():
            spine.set_visible(False)

    # Colorbar
    colorbar_right(im, ax, label="Predicted notch strength (arb.)")

    # Caption
    add_caption(
        fig,
        "Figure 3.8B. Notch strength increases with impedance contrast CZ and decreases with interface thickness kδ; sharp, high-contrast layers produce strong comb-like reverberation.",
    )

    save_all_formats(fig, os.path.join(OUTPUT_DIR, "figure_3_8B"), dpi=dpi)


# ------------------------------ Figure 3.8C ------------------------------ #

def attenuation_curves(w: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Schematic TL(dB) vs w for four Ri values.

    Shapes: a peak near w=1 whose width increases and height decreases with lower Ri,
    plus broadband skirts that rise as Ri decreases.
    """
    def base_curve(width: float, height: float, skirt: float) -> np.ndarray:
        peak = height * np.exp(-0.5 * ((w - 1.0) / width) ** 2)
        skirts = skirt * (np.exp(-((w - 0.8) / 0.6) ** 2) + np.exp(-((w - 1.4) / 0.5) ** 2))
        floor = 20 + 5 * np.ones_like(w)
        return floor + peak + skirts

    c15 = base_curve(width=0.10, height=45, skirt=1.0)  # Ri=1.5 deep blue
    c10 = base_curve(width=0.14, height=38, skirt=2.0)  # Ri=1.0 steel blue
    c06 = base_curve(width=0.22, height=30, skirt=5.0)  # Ri=0.6 teal
    c03 = base_curve(width=0.34, height=20, skirt=8.0)  # Ri=0.3 magenta dashed
    return c15, c10, c06, c03


def figure_38C() -> None:
    dpi = 300
    configure_matplotlib(dpi=dpi)
    fig, ax = create_figure(figsize_px=(2000, 1400), dpi=dpi)

    w = np.linspace(0.2, 2.2, 700)
    set_shared_frequency_axis(ax)

    c15, c10, c06, c03 = attenuation_curves(w)

    # Colors
    deep_blue = "#1E3A8A"
    steel_blue = "#4682B4"
    teal = PALETTE.shear
    magenta = "#B3007D"

    lw_primary = px_to_pt(3.0, dpi=dpi)

    ax.plot(w, c15, color=deep_blue, lw=lw_primary, label="Ri=1.5")
    ax.plot(w, c10, color=steel_blue, lw=lw_primary, label="Ri=1.0")
    ax.plot(w, c06, color=teal, lw=lw_primary, label="Ri=0.6")
    ax.plot(w, c03, color=magenta, lw=lw_primary, linestyle=(0, (8, 6)), label="Ri=0.3")

    # Y-axis range for TL in dB
    ax.set_ylim(20, 80)
    ax.set_yticks(np.arange(20, 81, 10))

    # Overlay band & centerline
    add_conversion_overlay(ax, dpi=dpi)

    # Annotations
    ax.annotate(
        "peak widens as Ri↓",
        xy=(1.0, c06[np.argmin(np.abs(w - 1.0))]),
        xytext=(1.45, 72),
        arrowprops=dict(arrowstyle="->", color="#374151", lw=px_to_pt(2, dpi=dpi)),
        fontsize=18,
    )
    ax.annotate(
        "skirts grow (broadband loss)",
        xy=(1.55, c03[np.argmin(np.abs(w - 1.55))]),
        xytext=(1.75, 56),
        arrowprops=dict(arrowstyle="->", color="#374151", lw=px_to_pt(2, dpi=dpi)),
        fontsize=18,
    )

    apply_typography(
        ax,
        title="Figure 3.8C — Apparent attenuation vs ω/N at selected Ri",
        xlabel="ω/N",
        ylabel="TL (dB)",
    )
    apply_major_grid(ax, dpi=dpi)

    # Legend inside axes
    leg = ax.legend(loc="upper left", frameon=False, fontsize=16)

    add_caption(
        fig,
        "Figure 3.8C. Apparent attenuation vs ω/N for selected Ri. Decreasing Ri broadens the conversion peak and raises broadband skirts.",
    )

    save_all_formats(fig, os.path.join(OUTPUT_DIR, "figure_3_8C"), dpi=dpi)


# ------------------------------ Figure 3.8D ------------------------------ #

def notch_depth_curves(k: np.ndarray, CZ_values: Tuple[float, ...]) -> dict[float, np.ndarray]:
    """Generate monotone-decreasing notch depth curves vs kδ for given CZ values."""
    curves: dict[float, np.ndarray] = {}
    for cz in CZ_values:
        # Depth ~ a(cz) * (k)^-b + d(cz), smoothly decreasing
        a = 22.0 * (cz / 0.30)
        b = 0.55
        d = 0.6 * (cz / 0.30)
        depth = a * (k ** (-b)) + d
        curves[cz] = depth
    return curves


def figure_38D() -> None:
    dpi = 300
    configure_matplotlib(dpi=dpi)
    fig, ax = create_figure(figsize_px=(2000, 1400), dpi=dpi)

    k = np.geomspace(0.1, 3.0, 400)
    CZ_vals = (0.05, 0.10, 0.20, 0.30)
    curves = notch_depth_curves(k, CZ_vals)

    colors = {
        0.05: "#C9B8D6",  # light gray-purple
        0.10: PALETTE.interfacial,  # purple
        0.20: "#4B2D6A",  # darker purple
        0.30: "#1B1028",  # nearly black-purple (optional)
    }

    lw_primary = px_to_pt(3.0, dpi=dpi)
    for cz, y in curves.items():
        style = dict(color=colors[cz], lw=lw_primary)
        ax.plot(k, y, **style, label=f"CZ={cz:.2f}")

    # Axes
    ax.set_xscale("log")
    ax.set_xlim(0.1, 3.0)
    ax.set_xticks([0.1, 0.2, 0.5, 1.0, 2.0, 3.0])
    ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())

    ax.set_ylim(0, 20)
    ax.set_yticks(np.arange(0, 21, 5))

    apply_typography(
        ax,
        title="Figure 3.8D — Notch depth vs kδ for several CZ",
        xlabel="kδ",
        ylabel="Notch depth (dB)",
    )
    apply_major_grid(ax, dpi=dpi)

    # Bottom axis brace and labels at 0.1, 1, 3
    y_brace = -1.0
    ax.annotate(
        "thin",
        xy=(0.1, 0.5), xytext=(0.1, 0.5), textcoords="data", ha="center", fontsize=16
    )
    ax.annotate(
        "resonant",
        xy=(1.0, 0.5), xytext=(1.0, 0.5), textcoords="data", ha="center", fontsize=16
    )
    ax.annotate(
        "thick",
        xy=(3.0, 0.5), xytext=(3.0, 0.5), textcoords="data", ha="center", fontsize=16
    )
    # A subtle brace line below axis (in axis coords):
    ax.plot([0.1, 1.0, 3.0], [0.5, 0.5, 0.5], color="#9CA3AF", lw=px_to_pt(1.2, dpi=dpi), transform=ax.get_xaxis_transform())

    # Legend inside axes
    ax.legend(loc="upper right", frameon=False, fontsize=16, title=None)

    add_caption(
        fig,
        "Figure 3.8D. Notch depth decreases as interface thickness kδ increases and increases with impedance contrast CZ.",
    )

    save_all_formats(fig, os.path.join(OUTPUT_DIR, "figure_3_8D"), dpi=dpi)


# ------------------------------------------------------------------------- #

def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    figure_38A()
    figure_38B()
    figure_38C()
    figure_38D()
    print(f"Saved figures to: {os.path.abspath(OUTPUT_DIR)}")


if __name__ == "__main__":
    main()
