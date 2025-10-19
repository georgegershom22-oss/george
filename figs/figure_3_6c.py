from __future__ import annotations

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from house_style import (
    apply_house_style,
    set_common_frequency_axis,
    add_conversion_overlay,
    add_panel_title,
    add_caption,
    color_cycle_curves,
)


rng = np.random.default_rng(7)


def synthesize_coherent_fraction(ri: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Construct a monotone decreasing coherent fraction with a notch near Ri≈0.3–0.5.

    Returns (y, band_low, band_high) where band_* bound a variability band.
    """
    baseline = 0.95 - 0.25 * (2.0 - ri) / 2.0  # ~0.95 at Ri=2, ~0.70 at Ri=0
    # Ensure monotonic decreasing with Ri decreasing
    baseline = np.clip(baseline, 0.4, 0.98)

    # Notch around 0.4 with width ~0.15
    notch = 0.18 * np.exp(-((ri - 0.40) ** 2) / (2 * 0.10**2))
    y = baseline - notch

    # Variability band increased near notch
    band = 0.04 + 0.05 * np.exp(-((ri - 0.40) ** 2) / (2 * 0.12**2))
    low = np.clip(y - band, 0.0, 1.0)
    high = np.clip(y + band, 0.0, 1.0)
    return y, low, high


def synthesize_psds(w: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Create normalized PSDs: high Ri narrowband vs marginal Ri broader plateau."""
    # High Ri: narrow Gaussian centered at 1 with small shoulders
    high = np.exp(-((w - 1.0) ** 2) / (2 * 0.08**2)) + 0.06 * np.exp(-((w - 1.0) ** 2) / (2 * 0.20**2))
    high /= np.max(high)

    # Marginal Ri: broader, slightly ragged
    marginal = np.exp(-((w - 1.0) ** 2) / (2 * 0.22**2))
    marginal += 0.08 * np.sin(12 * (w - 0.2)) ** 2
    marginal += 0.05 * np.exp(-((w - 1.3) ** 2) / (2 * 0.18**2))
    marginal /= np.max(marginal)

    return high, marginal


def plot_figure_3_6c(save_path_png: str | None = None, save_path_svg: str | None = None) -> mpl.figure.Figure:
    fig = plt.figure(figsize=(18, 12), constrained_layout=False)
    apply_house_style(fig)

    # Layout: two subpanels side by side
    gs = fig.add_gridspec(nrows=1, ncols=2, left=0.07, right=0.96, top=0.90, bottom=0.14, wspace=0.16)

    ax_left = fig.add_subplot(gs[0, 0])
    ax_right = fig.add_subplot(gs[0, 1])

    # Left: coherent fraction vs Ri
    ri = np.linspace(0.0, 2.0, 400)
    y, ylow, yhigh = synthesize_coherent_fraction(ri)

    ax_left.set_xlim(0.0, 2.0)
    ax_left.set_xlabel("Ri")
    ax_left.set_ylim(0.0, 1.0)
    ax_left.set_ylabel("coherent fraction")
    ax_left.yaxis.set_major_locator(mpl.ticker.FixedLocator([0.0, 0.25, 0.5, 0.75, 1.0]))

    color_cycle_curves(ax_left)
    ax_left.plot(ri, y, color="#1F78B4", lw=3.0, solid_capstyle="round")
    # Variability band near marginal region
    ax_left.fill_between(ri, ylow, yhigh, color="#457B9D", alpha=0.20, edgecolor="none")

    # Arrowed micro-notes
    ax_left.annotate("stable: high coherent fraction", xy=(1.8, y[np.argmin(np.abs(ri-1.8))]), xytext=(1.4, 0.92),
                     arrowprops=dict(arrowstyle="->", lw=1.2, color="#111827"), fontsize=16)
    ax_left.annotate("marginal: additional loss & variability", xy=(0.4, y[np.argmin(np.abs(ri-0.4))]), xytext=(0.9, 0.5),
                     arrowprops=dict(arrowstyle="->", lw=1.2, color="#111827"), fontsize=16)

    # Right: PSD broadening
    w = np.linspace(0.2, 2.2, 600)
    high, marginal = synthesize_psds(w)

    set_common_frequency_axis(ax_right)
    ax_right.set_ylim(0.0, 1.0)
    ax_right.set_ylabel("normalized PSD")
    ax_right.yaxis.set_major_locator(mpl.ticker.FixedLocator([0.0, 0.25, 0.5, 0.75, 1.0]))

    color_cycle_curves(ax_right)
    ax_right.plot(w, high, color="#1F78B4", lw=3.0, label="high Ri")
    ax_right.plot(w, marginal, color="#457B9D", lw=3.0, ls=(0, (6, 5)), label="marginal Ri")

    # Optional half-power bandwidth bars
    def half_power_bandwidth(x, y, threshold=0.5):
        m = y >= threshold
        if not np.any(m):
            return None
        indices = np.where(m)[0]
        return x[indices[0]], x[indices[-1]]

    for curve, data, yoff in (("high", high, 0.04), ("marginal", marginal, -0.06)):
        bw = half_power_bandwidth(w, data, 0.5)
        if bw is not None:
            x0, x1 = bw
            ax_right.annotate("", xy=(x0, 0.02 + (0.12 if curve=="high" else 0.22)), xytext=(x1, 0.02 + (0.12 if curve=="high" else 0.22)),
                              arrowprops=dict(arrowstyle="|-|", lw=1.5, color="#111827"))
            ax_right.text((x0+x1)/2, 0.04 + (0.12 if curve=="high" else 0.22), "BW", ha="center", va="bottom", fontsize=15)

    add_conversion_overlay(ax_right)
    ax_right.text(1.55, 0.92, "broader PSD under marginal Ri", fontsize=16)

    ax_right.legend(loc="upper right", frameon=False)

    # Figure title and caption
    add_panel_title(ax_left, "Figure 3.6C — Coherence loss and spectral broadening with decreasing Ri")

    # Caption beneath both panels inside canvas
    fig.text(0.07, 0.06, "Coherent fraction declines monotonically with a superposed dip near marginal Ri; spectra broaden under marginal Ri, indicating enhanced shear-mediated variability.", fontsize=15, fontstyle="italic", ha="left", va="top")

    # Save
    if save_path_png:
        fig.savefig(save_path_png, bbox_inches="tight")
    if save_path_svg:
        fig.savefig(save_path_svg, bbox_inches="tight")

    return fig


if __name__ == "__main__":
    fig = plot_figure_3_6c(
        save_path_png="/workspace/out/figures/figure_3_6c.png",
        save_path_svg="/workspace/out/figures/figure_3_6c.svg",
    )
    plt.close(fig)
