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
    make_colorbar,
)


rng = np.random.default_rng(42)


def synthesize_scalogram(kind: str, T: int = 600, F: int = 300) -> np.ndarray:
    """Synthesize a time–frequency intensity field.

    kind = 'highRi' -> thin ridge near ω/N≈1, otherwise quiet.
    kind = 'marginal' -> intermittent bursts across frequency with a persistent band near 1.
    Returns array of shape (F, T) with values in 0..1.
    """
    t = np.linspace(0, 1, T)
    w = np.linspace(0.2, 2.2, F)
    W, Tm = np.meshgrid(w, t, indexing="ij")  # (F,T)

    base_noise = rng.normal(0.0, 0.03 if kind == "highRi" else 0.08, size=(F, T))

    # Conversion ridge centered at 1 with slight waviness
    ridge = np.exp(-((W - 1.0 - 0.02 * np.sin(8 * np.pi * Tm)) ** 2) / (2 * 0.03**2))
    ridge *= 0.6 if kind == "highRi" else 0.35

    if kind == "highRi":
        # Suppress energy away from conversion band strongly
        envelope = np.exp(-((W - 1.0) ** 2) / (2 * 0.12**2))
        field = ridge * envelope + base_noise
    else:
        # Intermittent bursts: a handful of random time windows with broad frequency support
        field = ridge + base_noise
        for _ in range(14):
            t0 = rng.uniform(0.0, 1.0)
            dt = rng.uniform(0.02, 0.08)
            burst_time = np.exp(-((Tm - t0) ** 2) / (2 * dt**2))
            f0 = rng.uniform(0.5, 1.6)
            bw = rng.uniform(0.25, 0.55)
            burst_freq = np.exp(-((W - f0) ** 2) / (2 * bw**2))
            amp = rng.uniform(0.4, 0.9)
            field += amp * burst_time * burst_freq
        # Slight oblique streaks
        slope = rng.uniform(-0.8, 0.8)
        field += 0.08 * np.exp(-((W - (1.0 + slope * (Tm - 0.5))) ** 2) / (2 * 0.20**2))

    # Normalize 0..1
    field -= field.min()
    field /= max(field.max(), 1e-9)
    return field


def plot_figure_3_6b(save_path_png: str | None = None, save_path_svg: str | None = None) -> mpl.figure.Figure:
    fig = plt.figure(figsize=(18, 12), constrained_layout=False)
    apply_house_style(fig)

    # Layout: two equal panels with 40 px gutter.
    # Use gridspec with width_ratios and wspace computed in axes fraction.
    gs = fig.add_gridspec(nrows=1, ncols=2, left=0.07, right=0.94, top=0.92, bottom=0.12, wspace=0.08)

    ax_left = fig.add_subplot(gs[0, 0])
    ax_right = fig.add_subplot(gs[0, 1], sharey=ax_left)

    # Common Y-axis (ω/N) and X-axis (time)
    for ax in (ax_left, ax_right):
        ax.set_ylim(0.2, 2.2)
        ax.set_ylabel("ω/N")
        ax.yaxis.set_major_locator(mpl.ticker.FixedLocator([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]))
        ax.yaxis.set_minor_locator(mpl.ticker.NullLocator())
        ax.set_xlim(0, 60)
        ax.set_xlabel("time (s)")
        ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(10))
        ax.xaxis.set_minor_locator(mpl.ticker.NullLocator())

    # Data
    F, T = 300, 600
    L = synthesize_scalogram("highRi", T=T, F=F)
    R = synthesize_scalogram("marginal", T=T, F=F)

    # Colormap: perceptual, darker = higher -> cividis with reversed norm not needed, cividis already dark-high.
    cmap = mpl.colormaps.get("cividis")

    # Show images (extent to map to axes)
    im_left = ax_left.imshow(L, origin="lower", extent=(0, 60, 0.2, 2.2), aspect="auto", cmap=cmap, vmin=0.0, vmax=1.0)
    im_right = ax_right.imshow(R, origin="lower", extent=(0, 60, 0.2, 2.2), aspect="auto", cmap=cmap, vmin=0.0, vmax=1.0)

    # Conversion band overlay on both
    add_conversion_overlay(ax_left)
    add_conversion_overlay(ax_right)

    # Micro-annotations
    ax_left.text(55.5, 1.05, "narrow conversion-band modulation", ha="right", va="center", fontsize=18)
    ax_right.annotate(
        "intermittent broadband bursts",
        xy=(35, 1.5), xycoords="data",
        xytext=(58, 2.05), textcoords="data",
        arrowprops=dict(arrowstyle="->", color="#111827", lw=1.2),
        fontsize=16,
    )
    ax_right.annotate(
        "enhanced spread beyond conversion",
        xy=(22, 1.35), xycoords="data",
        xytext=(7, 2.05), textcoords="data",
        arrowprops=dict(arrowstyle="->", color="#111827", lw=1.2),
        fontsize=16,
    )

    # Captions inside each panel (bottom)
    ax_left.text(0.0, -0.20, "High Ri: fluctuation energy concentrated in a narrow conversion band.", transform=ax_left.transAxes, fontsize=15, fontstyle="italic", ha="left", va="top")
    ax_right.text(0.0, -0.20, "Marginal Ri: intermittent broadband activity indicates shear-mediated variability.", transform=ax_right.transAxes, fontsize=15, fontstyle="italic", ha="left", va="top")

    # Titles and shared colorbar
    add_panel_title(ax_left, "Figure 3.6B — Time–frequency TL fluctuation intensity")

    # Shared colorbar at right of the right panel
    cbar = make_colorbar(fig, im_right, ax=ax_right, fraction=0.046, pad=0.02)
    cbar.set_label("TL fluctuation intensity (arb.)")

    # Save
    if save_path_png:
        fig.savefig(save_path_png, bbox_inches="tight")
    if save_path_svg:
        fig.savefig(save_path_svg, bbox_inches="tight")

    return fig


if __name__ == "__main__":
    fig = plot_figure_3_6b(
        save_path_png="/workspace/out/figures/figure_3_6b.png",
        save_path_svg="/workspace/out/figures/figure_3_6b.svg",
    )
    plt.close(fig)
