from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from house_style import (
    apply_base_style,
    configure_shared_axes,
    draw_conversion_band,
    add_caption,
    HEATMAP_CMAP,
    add_colorbar,
    save_figure,
    PT_INPLOT,
    COLOR_BLUE,
    COLOR_STEEL,
)


def synthetic_scalogram(shape=(300, 300), mode="stable", rng=None):
    if rng is None:
        rng = np.random.default_rng(7)
    t_len, f_len = shape
    base = np.zeros(shape)

    # frequency axis mapped to ω/N in [0.2,2.2]
    f = np.linspace(0.2, 2.2, f_len)
    t = np.linspace(0, 60, t_len)

    # Narrow ridge near ω/N≈1
    ridge = np.exp(-((f - 1.0) ** 2) / (2 * 0.04 ** 2))  # very narrow
    ridge = ridge[None, :] * (0.6 + 0.1 * np.sin(2 * np.pi * t[:, None] / 40.0))

    if mode == "stable":
        base = ridge
        noise = 0.03 * rng.standard_normal(shape)
        base += noise
        base = np.clip(base, 0, None)
    else:  # marginal Ri: intermittent broadband bursts
        base = 0.25 * ridge
        # Add sporadic bursts: random ellipses in time-frequency
        for _ in range(14):
            tc = rng.uniform(5, 55)
            fc = rng.uniform(0.5, 1.8)
            t_bw = rng.uniform(3, 10)
            f_bw = rng.uniform(0.15, 0.45)
            amp = rng.uniform(0.5, 1.0)
            T, F = np.meshgrid(t, f, indexing="ij")
            blob = amp * np.exp(-((T - tc) ** 2) / (2 * t_bw ** 2) - ((F - fc) ** 2) / (2 * f_bw ** 2))
            # Add slight oblique tilt
            blob *= np.exp(-0.5 * ((F - fc) - 0.01 * (T - tc)) ** 2 / (f_bw ** 2))
            base += blob
        # Add texture
        base += 0.06 * rng.standard_normal(shape)
        base = np.clip(base, 0, None)

    # Normalize per panel but we'll use shared colorbar by scaling to [0,1]
    base -= base.min()
    if base.max() > 0:
        base /= base.max()
    return base, t, f


def plot_figure_3_6b():
    apply_base_style()

    fig, (axL, axR) = plt.subplots(1, 2, gridspec_kw=dict(wspace=0.08))

    # Left panel: high Ri (stable)
    configure_shared_axes(axL, x_kind="time", y_kind="omega_over_N")
    dataL, t, f = synthetic_scalogram(mode="stable")
    imL = axL.imshow(
        dataL,
        origin="lower",
        extent=(t.min(), t.max(), f.min(), f.max()),
        aspect="auto",
        cmap=HEATMAP_CMAP,
        vmin=0, vmax=1,
        interpolation="bilinear",
    )
    # ω/N is on the y-axis here, so draw horizontal conversion band
    draw_conversion_band(axL, axis="y")
    axL.text(0.02, 0.92, "narrow conversion-band modulation", transform=axL.transAxes,
             fontsize=PT_INPLOT)
    add_caption(axL, "High Ri: fluctuation energy concentrated in a narrow conversion band.")

    # Right panel: marginal Ri
    configure_shared_axes(axR, x_kind="time", y_kind="omega_over_N")
    dataR, t, f = synthetic_scalogram(mode="marginal", rng=np.random.default_rng(9))
    imR = axR.imshow(
        dataR,
        origin="lower",
        extent=(t.min(), t.max(), f.min(), f.max()),
        aspect="auto",
        cmap=HEATMAP_CMAP,
        vmin=0, vmax=1,
        interpolation="bilinear",
    )
    draw_conversion_band(axR, axis="y")
    # Micro-labels with arrows
    axR.annotate("intermittent broadband bursts", xy=(40, 1.6), xytext=(48, 2.0),
                 arrowprops=dict(arrowstyle="->", color="#111827"), fontsize=PT_INPLOT)
    axR.annotate("enhanced spread beyond conversion", xy=(22, 1.35), xytext=(5, 1.95),
                 arrowprops=dict(arrowstyle="->", color="#111827"), fontsize=PT_INPLOT)
    add_caption(axR, "Marginal Ri: intermittent broadband activity indicates shear-mediated variability.")

    # Single shared colorbar for both panels, placed to the right
    cbar = add_colorbar(fig, imR, label="TL fluctuation intensity (arb.)", ax=[axL, axR], pad=0.02, shrink=0.95)

    save_figure(fig, "figure_3_6b")
    plt.close(fig)


if __name__ == "__main__":
    plot_figure_3_6b()
