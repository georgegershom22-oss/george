from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from house_style import (
    STYLE,
    create_canvas,
    set_freq_axis,
    style_grid,
    overlay_conversion_band,
    add_caption,
    add_colorbar,
    show_heatmap,
    save_figure,
)


def generate_left_panel(nf: int = 240, nt: int = 300, t_max: float = 60.0):
    # Thin ridge near wn=1 with slight waviness in time
    t = np.linspace(0, t_max, nt)
    wn = np.linspace(STYLE.freq_min, STYLE.freq_max, nf)
    T, WN = np.meshgrid(t, wn)

    center = 1.0 + 0.03 * np.sin(2 * np.pi * T / 20.0)  # gentle undulation
    ridge = np.exp(-((WN - center) / 0.045) ** 2)

    background = 0.05 * np.ones_like(ridge)
    Z = 0.9 * ridge + background

    # Normalize 0..1
    Z -= Z.min()
    Z /= Z.max() if Z.max() > 0 else 1.0
    return wn, t, Z


def generate_right_panel(nf: int = 240, nt: int = 300, t_max: float = 60.0):
    # Intermittent broadband bursts with occasional oblique streaks
    t = np.linspace(0, t_max, nt)
    wn = np.linspace(STYLE.freq_min, STYLE.freq_max, nf)
    T, WN = np.meshgrid(t, wn)

    rng = np.random.default_rng(42)

    # Base band near 1 (less coherent than left)
    base = 0.35 * np.exp(-((WN - 1.0) / 0.12) ** 2)

    # Intermittent bursts: sum of moving 2D Gaussians in time–freq
    Z = base.copy()
    num_bursts = 10
    for k in range(num_bursts):
        t0 = rng.uniform(5, 55)
        w0 = rng.uniform(0.6, 1.8)
        sig_t = rng.uniform(2.0, 6.0)
        sig_w = rng.uniform(0.08, 0.22)
        amp = rng.uniform(0.6, 1.0)
        burst = amp * np.exp(-((T - t0) / sig_t) ** 2) * np.exp(-((WN - w0) / sig_w) ** 2)
        Z += burst

    # Oblique streaks (intrusions)
    for slope in (-0.012, 0.009):
        tline = rng.uniform(10, 40)
        wline = 0.9 + slope * (T - tline)
        streak = 0.35 * np.exp(-((WN - wline) / 0.09) ** 2)
        Z += streak

    # Mild texture/jitter
    Z += 0.05 * rng.standard_normal(Z.shape)

    # Normalize 0..1
    Z -= Z.min()
    Z /= Z.max() if Z.max() > 0 else 1.0
    return wn, t, Z


def main() -> None:
    # 40 px gutter between panels
    fig, axes = create_canvas(ncols=2, wspace_px=40.0)
    axL, axR = axes.ravel()

    # Left: high Ri
    wnL, tL, ZL = generate_left_panel()
    imL = show_heatmap(axL, ZL, extent=(tL.min(), tL.max(), wnL.min(), wnL.max()))
    axL.set_xlim(0, 60)
    axL.set_xticks(np.arange(0, 61, 10))
    axL.set_xlabel(r"Time $t$ (s)")
    set_freq_axis(axL, axis="y")
    style_grid(axL)
    overlay_conversion_band(axL, align_to="y")

    # Tiny annotation
    axL.text(0.03, 0.92, "narrow conversion-band modulation", transform=axL.transAxes,
             fontsize=STYLE.note_size_pt, color=STYLE.deep_blue)

    add_caption(axL, r"High $R_i$: fluctuation energy concentrated in a narrow conversion band.")

    # Right: marginal Ri
    wnR, tR, ZR = generate_right_panel()
    imR = show_heatmap(axR, ZR, extent=(tR.min(), tR.max(), wnR.min(), wnR.max()))
    axR.set_xlim(0, 60)
    axR.set_xticks(np.arange(0, 61, 10))
    axR.set_xlabel(r"Time $t$ (s)")
    set_freq_axis(axR, axis="y")
    style_grid(axR)
    overlay_conversion_band(axR, align_to="y")

    # Micro-labels with arrows
    axR.annotate("intermittent broadband bursts", xy=(40, 1.65), xytext=(48, 2.05),
                 textcoords="data", fontsize=STYLE.note_size_pt, color=STYLE.deep_blue,
                 arrowprops=dict(arrowstyle="->", color=STYLE.deep_blue, lw=1.5))
    axR.annotate("enhanced spread beyond conversion", xy=(25, 1.35), xytext=(12, 1.95),
                 textcoords="data", fontsize=STYLE.note_size_pt, color=STYLE.steel_blue,
                 arrowprops=dict(arrowstyle="->", color=STYLE.steel_blue, lw=1.5))

    add_caption(axR, r"Marginal $R_i$: intermittent broadband activity indicates shear-mediated variability.")

    # Shared color scale; use the right panel's image for colorbar, but values are normalized
    # Place to the right of right panel
    add_colorbar(fig, imR, label="TL fluctuation intensity (arb.)", ax=[axL, axR])

    save_figure(fig, "/workspace/out/figures/figure_3_6b")


if __name__ == "__main__":
    main()
