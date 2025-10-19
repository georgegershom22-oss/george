from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

from house_style import (
    new_canvas,
    set_omega_over_N_axis,
    add_conversion_band,
    add_title_inside,
    add_caption,
    add_colorbar,
    HEATMAP_CMAP,
    NOTE_PT,
    COLORS,
    save_figure,
)


def synth_scalogram(time: np.ndarray, w_on_N: np.ndarray, mode: str) -> np.ndarray:
    """Generate synthetic TL fluctuation intensity scalograms.
    mode='stable' (high Ri) or 'marginal' (near-critical Ri).
    Returns values roughly in 0..1.
    """
    T, W = np.meshgrid(time, w_on_N, indexing="xy")

    # Base conversion band near w/N=1
    band = np.exp(-((W - 1.0) ** 2) / (2 * (0.08 if mode == "stable" else 0.18) ** 2))
    band *= 0.6 if mode == "stable" else 0.4

    if mode == "stable":
        # Slight waviness over time
        ridge = band * (0.9 + 0.1 * np.sin(2 * np.pi * T / (len(time) * 0.6)))
        noise = 0.05 * np.random.default_rng(2).standard_normal(size=ridge.shape)
        S = np.clip(ridge + noise, 0.0, None)
    else:
        # Intermittent broadband bursts: random dark blotches with oblique streaks
        rng = np.random.default_rng(7)
        S = 0.10 * rng.random(size=band.shape)  # quiet background
        # Persistent but less coherent band
        S += band
        # Add sporadic bursts
        for _ in range(22):
            t0 = rng.uniform(time.min(), time.max())
            w0 = rng.uniform(0.5, 1.7)
            t_sigma = rng.uniform(1.2, 4.0)
            w_sigma = rng.uniform(0.12, 0.28)
            angle = rng.uniform(-0.8, 0.8)
            tt = (T - t0) * np.cos(angle) - (W - w0) * np.sin(angle)
            ww = (T - t0) * np.sin(angle) + (W - w0) * np.cos(angle)
            blob = np.exp(-(tt ** 2) / (2 * t_sigma ** 2) - (ww ** 2) / (2 * w_sigma ** 2))
            S += 0.9 * blob
        # Slight raggedness
        S += 0.05 * rng.standard_normal(size=S.shape)
        S = np.clip(S, 0.0, None)

    # Normalize
    S -= S.min()
    if S.max() > 0:
        S /= S.max()
    return S


def main() -> None:
    time = np.linspace(0.0, 60.0, 600)
    W = np.linspace(0.2, 2.2, 360)

    S_stable = synth_scalogram(time, W, mode="stable")
    S_marginal = synth_scalogram(time, W, mode="marginal")

    fig = new_canvas()

    # Layout: two equal panels with 40 px gutter -> in figure coords: 40 / 1800 ~ 0.0222 width
    gutter = 40 / 1800
    left = 0.08
    width = (1.0 - left - 0.06 - gutter - 0.05) / 2
    bottom = 0.12
    height = 0.76

    axL = fig.add_axes([left, bottom, width, height])
    axR = fig.add_axes([left + width + gutter, bottom, width, height])

    # Left panel (high Ri)
    imL = axL.imshow(
        S_stable.T,  # time on x, W on y after transpose
        origin="lower",
        aspect="auto",
        cmap=HEATMAP_CMAP,
        extent=[time.min(), time.max(), W.min(), W.max()],
        norm=Normalize(vmin=0.0, vmax=1.0),
        zorder=0,
    )
    axL.set_xlim(time.min(), time.max())
    axL.set_xticks(np.arange(0, 61, 10))
    axL.set_xlabel("time t (s)")
    set_omega_over_N_axis(axL)
    add_conversion_band(axL, orientation="horizontal")
    axL.text(0.03, 0.93, "narrow conversion-band modulation", transform=axL.transAxes, fontsize=NOTE_PT)

    # Right panel (marginal Ri)
    imR = axR.imshow(
        S_marginal.T,
        origin="lower",
        aspect="auto",
        cmap=HEATMAP_CMAP,
        extent=[time.min(), time.max(), W.min(), W.max()],
        norm=Normalize(vmin=0.0, vmax=1.0),
        zorder=0,
    )
    axR.set_xlim(time.min(), time.max())
    axR.set_xticks(np.arange(0, 61, 10))
    axR.set_xlabel("time t (s)")
    set_omega_over_N_axis(axR)
    add_conversion_band(axR, orientation="horizontal")

    # Micro-labels with arrows
    axR.annotate("intermittent broadband bursts", xy=(45, 1.6), xytext=(28, 2.0),
                 arrowprops=dict(arrowstyle="->", color="black", lw=1.0), fontsize=NOTE_PT)
    axR.annotate("enhanced spread beyond conversion", xy=(20, 1.35), xytext=(4, 1.95),
                 arrowprops=dict(arrowstyle="->", color="black", lw=1.0), fontsize=NOTE_PT)

    # Captions inside each panel, bottom
    axL.text(0.5, -0.16, "High $R_i$: fluctuation energy concentrated in a narrow conversion band.",
             transform=axL.transAxes, ha="center", va="top")
    axR.text(0.5, -0.16, "Marginal $R_i$: intermittent broadband activity indicates shear-mediated variability.",
             transform=axR.transAxes, ha="center", va="top")

    # Shared colorbar to right of right panel
    cbar = add_colorbar(fig, imR, axR, label="TL fluctuation intensity (arb.)")

    # Title
    add_title_inside(axL, r"Figure 3.6B — Time–frequency TL fluctuation intensity")

    # Save
    save_figure(fig, "/workspace/out/figures/figure_3_6b")


if __name__ == "__main__":
    main()
