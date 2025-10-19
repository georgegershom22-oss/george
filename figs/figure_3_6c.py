from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from house_style import (
    STYLE,
    create_canvas,
    set_freq_axis,
    set_ri_axis,
    style_grid,
    overlay_conversion_band,
    add_caption,
    save_figure,
)


def coherent_fraction_curve(ri: np.ndarray) -> np.ndarray:
    # Monotone decreasing from ~0.95 at Ri=2 to ~0.5 at Ri~0.25
    base = 0.95 - 0.30 * (2.0 - ri) / 1.75  # rough linear trend
    # Local notch around 0.3–0.5 down to ~0.4
    notch_center = 0.40
    notch = 0.12 * np.exp(-((ri - notch_center) / 0.09) ** 2)
    cf = base - notch
    # Clamp 0..1
    cf = np.clip(cf, 0.0, 1.0)
    return cf


def psd_curves(wn: np.ndarray):
    # High Ri: narrow peak near 1
    high = np.exp(-((wn - 1.0) / 0.10) ** 2)
    high /= high.max()

    # Marginal Ri: broader peak
    marginal = np.exp(-((wn - 1.0) / 0.22) ** 2)
    # slight raggedness
    rng = np.random.default_rng(7)
    marginal += 0.03 * rng.standard_normal(wn.shape)
    marginal = np.clip(marginal, 0.0, None)
    marginal /= marginal.max()
    return high, marginal


def add_bw_bar(ax: plt.Axes, center: float, half_power_bw: float, y: float, color: str, label: str):
    x0 = center - half_power_bw / 2.0
    x1 = center + half_power_bw / 2.0
    ax.hlines(y, x0, x1, color=color, linewidth=2.5)
    ax.annotate("", xy=(x0, y), xytext=(x1, y), arrowprops=dict(arrowstyle="<->", color=color, lw=2.5))
    ax.text(center, y - 0.07, label, color=color, ha="center", va="top", fontsize=STYLE.note_size_pt)


def main() -> None:
    fig, axes = create_canvas(ncols=2, wspace_px=40.0)
    axL, axR = axes.ravel()

    # Left subpanel — coherent fraction vs Ri
    ri = np.linspace(STYLE.ri_min, STYLE.ri_max, 400)
    cf = coherent_fraction_curve(ri)

    axL.plot(ri, cf, color=STYLE.deep_blue, linewidth=3.0)

    # Variability band near marginal Ri (0.3–0.5)
    band_lo = np.maximum(0.0, cf - 0.08)
    band_hi = np.minimum(1.0, cf + 0.06)
    mask = (ri >= 0.30) & (ri <= 0.50)
    axL.fill_between(ri[mask], band_lo[mask], band_hi[mask], color=STYLE.steel_blue, alpha=0.20)

    set_ri_axis(axL, axis="x")
    axL.set_ylim(0.0, 1.0)
    axL.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    axL.set_ylabel("Coherent fraction (0–1)")
    style_grid(axL)

    axL.text(0.03, 0.90, "stable: high coherent fraction", transform=axL.transAxes,
             fontsize=STYLE.note_size_pt, color=STYLE.deep_blue)
    axL.text(0.45, 0.25, "marginal: additional loss & variability", transform=axL.transAxes,
             fontsize=STYLE.note_size_pt, color=STYLE.steel_blue)

    # Right subpanel — PSD broadening
    wn = np.linspace(STYLE.freq_min, STYLE.freq_max, 800)
    high, marginal = psd_curves(wn)
    axR.plot(wn, high, color=STYLE.deep_blue, linewidth=3.0, label=r"High $R_i$")
    axR.plot(wn, marginal, color=STYLE.steel_blue, linewidth=3.0, linestyle=(0, (6, 4)), label=r"Marginal $R_i$")

    set_freq_axis(axR, axis="x")
    axR.set_ylim(0.0, 1.05)
    axR.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    axR.set_ylabel("Normalized PSD")
    style_grid(axR)

    # Optional BW bars
    add_bw_bar(axR, center=1.0, half_power_bw=0.22, y=0.25, color=STYLE.deep_blue, label="BW")
    add_bw_bar(axR, center=1.0, half_power_bw=0.48, y=0.15, color=STYLE.steel_blue, label="BW")

    axR.text(0.60, 0.80, "broader PSD under marginal $R_i$", transform=axR.transAxes,
             fontsize=STYLE.note_size_pt, color=STYLE.steel_blue)

    # Legends inside, upper-right, frame off
    axR.legend(loc="upper right")

    # Overall title and caption
    fig.suptitle(r"Figure 3.6C — Coherence loss and spectral broadening with decreasing $R_i$",
                 fontsize=STYLE.title_size_pt, fontweight="bold", x=0.01, ha="left")

    # Captions under axes
    add_caption(axL, r"Coherent fraction declines monotonically with a superposed dip near marginal $R_i$.")
    add_caption(axR, r"Spectra broaden under marginal $R_i$, indicating enhanced shear-mediated variability.")

    save_figure(fig, "/workspace/out/figures/figure_3_6c")


if __name__ == "__main__":
    main()
