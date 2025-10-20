from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from .house_style import (
    apply_rc_params,
    new_figure,
    add_conversion_window,
    style_frequency_axis,
    style_share_axis,
    add_caption,
    save_figure,
    COLORS,
    PRIMARY_LW,
    SECONDARY_LW,
    DASH,
    FONT_SIZES,
    add_mechanism_legend,
)


def _stacked_area(ax, x, w_classical, w_conversion, w_interfacial, w_shear):
    # Order: classical (bottom), conversion, interfacial, shear (top)
    ax.stackplot(
        x,
        w_classical, w_conversion, w_interfacial, w_shear,
        colors=[COLORS["classical"], COLORS["conversion"], COLORS["interfacial"], COLORS["shear"]],
        linewidth=0,
    )


def _annotate_conversion(ax):
    ax.annotate(
        "conversion peak near ω/N≈1",
        xy=(1.0, 0.9), xycoords=("data", "axes fraction"),
        xytext=(1.25, 0.93), textcoords=("data", "axes fraction"),
        arrowprops=dict(arrowstyle="->", color=COLORS["conversion_dark"], lw=SECONDARY_LW),
        fontsize=FONT_SIZES["note"], color=COLORS["conversion_dark"], ha="left",
    )


def plot_b1(out_base: str) -> None:
    apply_rc_params()
    fig = new_figure()
    ax = fig.add_axes([0.10, 0.12, 0.80, 0.74])  # [left, bottom, width, height]

    # Axes styling
    style_frequency_axis(ax)
    style_share_axis(ax)
    ax.set_title("Figure 3.7B1 — Mechanism shares vs ω/N (High Ri)")
    ax.set_xlabel("ω/N")
    ax.set_ylabel("Share (0–1)")

    # Conversion window and centerline
    add_conversion_window(ax, xlim=(0.2, 2.2), ylim=(0, 1))

    # Create x grid
    x = np.linspace(0.2, 2.2, 800)

    # Raw shapes (tuned for qualitative targets)
    # Conversion: broad dome centered at 1
    conv_raw = 1.2 * np.exp(-0.5 * ((x - 1.0) / 0.28) ** 2)
    # Classical: baseline pedestal slowly rising
    classical_raw = 0.55 + 0.10 * (x - 0.2) / (2.0)
    # Shear: small shoulder around 0.9–1.2
    shear_raw = 0.20 * np.exp(-0.5 * ((x - 1.05) / 0.22) ** 2) + 0.02
    # Interfacial: minimal and flat
    interf_raw = 0.08 + 0.02 * np.cos((x - 0.2) * 2.0)

    total = conv_raw + classical_raw + shear_raw + interf_raw
    w_conv = conv_raw / total
    w_class = classical_raw / total
    w_shear = shear_raw / total
    w_interf = interf_raw / total

    # Stacked area
    _stacked_area(ax, x, w_class, w_conv, w_interf, w_shear)

    # Overlays for guidance
    _annotate_conversion(ax)
    ax.annotate("classical baseline", xy=(0.35, 0.35), xycoords=("axes fraction", "axes fraction"),
                xytext=(0.20, 0.18), textcoords=("axes fraction", "axes fraction"),
                arrowprops=dict(arrowstyle="->", color=COLORS["classical"], lw=SECONDARY_LW),
                fontsize=FONT_SIZES["note"], color=COLORS["classical"], ha="left")
    ax.annotate("secondary shear (stable)", xy=(1.2, 0.90), xycoords=("data", "axes fraction"),
                xytext=(1.55, 0.75), textcoords=("data", "axes fraction"),
                arrowprops=dict(arrowstyle="->", color=COLORS["shear"], lw=SECONDARY_LW),
                fontsize=FONT_SIZES["note"], color=COLORS["shear"], ha="left")

    # Legend
    add_mechanism_legend(ax, loc="upper right")

    # Caption
    add_caption(fig, "Figure 3.7B1. Under high Ri and continuous stratification, mode conversion dominates near ω/N≈1; classical loss is the baseline; shear and interfacial contributions are secondary.")

    # Save
    save_figure(fig, out_base)
    plt.close(fig)


def plot_b2(out_base: str) -> None:
    apply_rc_params()
    fig = new_figure()
    ax = fig.add_axes([0.10, 0.12, 0.80, 0.74])

    style_frequency_axis(ax)
    style_share_axis(ax)
    ax.set_title("Figure 3.7B2 — Mechanism shares vs ω/N (Marginal Ri)")
    ax.set_xlabel("ω/N")
    ax.set_ylabel("Share (0–1)")

    add_conversion_window(ax, xlim=(0.2, 2.2), ylim=(0, 1))

    x = np.linspace(0.2, 2.2, 800)

    # Raw shapes tuned for marginal Ri
    conv_raw = 0.95 * np.exp(-0.5 * ((x - 1.0) / 0.30) ** 2)
    shear_raw = 0.85 * np.exp(-0.5 * ((x - 1.05) / 0.30) ** 2) + 0.06
    classical_raw = 0.45 + 0.06 * (x - 0.2) / (2.0)
    # Reduce classical within 0.8–1.3 to make room
    reduce_band = (x >= 0.8) & (x <= 1.3)
    classical_raw = classical_raw * (1.0 - 0.25 * reduce_band.astype(float))
    interf_raw = 0.07 + 0.02 * np.cos((x - 0.2) * 2.0)

    total = conv_raw + classical_raw + shear_raw + interf_raw
    w_conv = conv_raw / total
    w_class = classical_raw / total
    w_shear = shear_raw / total
    w_interf = interf_raw / total

    _stacked_area(ax, x, w_class, w_conv, w_interf, w_shear)

    ax.annotate("shear-mediated rises near ω/N∼1", xy=(1.05, 0.92), xycoords=("data", "axes fraction"),
                xytext=(1.5, 0.80), textcoords=("data", "axes fraction"),
                arrowprops=dict(arrowstyle="->", color=COLORS["shear"], lw=SECONDARY_LW),
                fontsize=FONT_SIZES["note"], color=COLORS["shear"], ha="left")

    add_mechanism_legend(ax, loc="upper right")

    add_caption(fig, "Figure 3.7B2. For marginal Ri, shear-mediated loss broadens around the conversion band and can rival conversion near ω/N∼1; classical share correspondingly diminishes.")

    save_figure(fig, out_base)
    plt.close(fig)
