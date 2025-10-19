from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from house_style import (
    new_canvas,
    set_omega_over_N_axis,
    set_Ri_axis,
    add_conversion_band,
    add_title_inside,
    add_caption,
    COLORS,
    PSD_TICKS,
    CURVE_LW_PT,
    save_figure,
)


def synth_coherent_fraction(Ri: np.ndarray) -> tuple[np.ndarray, tuple[float, float]]:
    """Monotone decreasing coherent fraction with a notch near marginal Ri (~0.3–0.5)."""
    base = 0.95 - 0.25 * (2.0 - Ri) / 2.0  # ~0.95 at Ri=2, ~0.70 at Ri=0
    notch_center = 0.38
    notch_width = 0.12
    notch_depth = 0.18
    notch = notch_depth * np.exp(-0.5 * ((Ri - notch_center) / notch_width) ** 2)
    cf = np.clip(base - notch, 0.0, 1.0)
    band_lo, band_hi = notch_center - 0.12, notch_center + 0.12
    return cf, (band_lo, band_hi)


def synth_psd(W: np.ndarray, mode: str) -> np.ndarray:
    """PSD shapes: narrow (stable) vs broader (marginal). Normalized to max=1."""
    if mode == "stable":
        psd = np.exp(-0.5 * ((W - 1.0) / 0.12) ** 2) + 0.08 * np.exp(-0.5 * ((W - 0.8) / 0.20) ** 2)
    else:
        psd = np.exp(-0.5 * ((W - 1.0) / 0.28) ** 2) + 0.10 * np.exp(-0.5 * ((W - 0.9) / 0.30) ** 2)
        psd *= 1.02 - 0.06 * np.cos(10 * W)
    psd /= psd.max()
    return psd


def main() -> None:
    fig = new_canvas()

    # Layout: two subpanels
    left = 0.08
    bottom = 0.14
    width = 0.36
    height = 0.74
    gap = 0.08

    axL = fig.add_axes([left, bottom, width, height])
    axR = fig.add_axes([left + width + gap, bottom, width, height])

    # Left: coherent fraction vs Ri
    Ri = np.linspace(0.0, 2.0, 400)
    cf, (band_lo, band_hi) = synth_coherent_fraction(Ri)
    axL.plot(Ri, cf, color=COLORS["deep_blue"], lw=CURVE_LW_PT)
    axL.fill_between(Ri, 0, 1, where=(Ri >= band_lo) & (Ri <= band_hi), color=COLORS["steel_blue"], alpha=0.20, transform=axL.get_xaxis_transform())
    axL.set_xlim(0.0, 2.0)
    axL.set_xticks([0.0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
    axL.set_xlabel(r"$R_i$")
    axL.set_ylim(0.0, 1.0)
    axL.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    axL.set_ylabel("coherent fraction")
    axL.text(0.04, 0.90, "stable: high coherent fraction", transform=axL.transAxes)
    axL.text(0.38, 0.22, "marginal: additional loss & variability", transform=axL.transAxes)

    # Right: PSD broadening high vs marginal Ri
    W = np.linspace(0.2, 2.2, 600)
    psd_stable = synth_psd(W, mode="stable")
    psd_marginal = synth_psd(W, mode="marginal")

    axR.plot(W, psd_stable, color=COLORS["deep_blue"], lw=CURVE_LW_PT, label="High $R_i$")
    axR.plot(W, psd_marginal, color=COLORS["steel_blue"], lw=CURVE_LW_PT, ls=(0, (6, 4)), label="Marginal $R_i$")

    set_omega_over_N_axis(axR)
    axR.set_ylim(0.0, 1.0)
    axR.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    axR.set_ylabel("normalized PSD")

    # Optional BW arrows (simple double-headed under peaks)
    def add_bw(ax, center, halfwidth, y, color):
        ax.annotate("", xy=(center - halfwidth, y), xytext=(center + halfwidth, y),
                    arrowprops=dict(arrowstyle="<->", color=color, lw=1.2))
        ax.text(center, y - 0.07, "BW", color=color, ha="center", va="top")
    add_bw(axR, 1.0, 0.10, 0.15, COLORS["deep_blue"])  # stable
    add_bw(axR, 1.0, 0.24, 0.08, COLORS["steel_blue"])  # marginal

    add_conversion_band(axR, orientation="vertical")
    axR.text(1.40, 0.82, "broader PSD under marginal $R_i$", color=COLORS["steel_blue"])

    # Title & caption
    add_title_inside(axL, r"Figure 3.6C — Coherence loss and spectral broadening with decreasing $R_i$")
    add_caption(fig, "Coherent fraction declines monotonically with a superposed dip near marginal $R_i$; "
                    "spectra broaden under marginal $R_i$, indicating enhanced shear-mediated variability.")

    # Legend inside upper-right
    axR.legend(loc="upper right")

    save_figure(fig, "/workspace/out/figures/figure_3_6c")


if __name__ == "__main__":
    main()
