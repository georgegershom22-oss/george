from __future__ import annotations

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from house_style import (
    apply_house_style,
    set_common_frequency_axis,
    set_common_ri_axis,
    add_conversion_overlay,
    add_panel_title,
    add_caption,
    make_colorbar,
    DEEP_BLUE,
    STEEL_BLUE,
    MAGENTA,
)


def synthesize_sdi(ri: np.ndarray, w_over_n: np.ndarray) -> np.ndarray:
    """Synthesize a plausible shear-dominance index field (0..1) with desired morphology.

    Bright lobe centered near (Ri≈0.4, ω/N≈1), decays with Ri, suppressed at high ω/N,
    with a weak low-Ri sub-buoyancy tongue for ω/N<1.
    """
    # Centered Gaussian lobe around (Ri0, w0)
    Ri0, w0 = 0.4, 1.0
    sigma_Ri_low, sigma_w = 0.20, 0.25
    lobe = np.exp(-((ri - Ri0) ** 2) / (2 * sigma_Ri_low**2)) * np.exp(-((w_over_n - w0) ** 2) / (2 * sigma_w**2))

    # Rapid decay with increasing Ri (additional factor)
    stable_decay = np.exp(-2.0 * np.maximum(ri - 0.6, 0.0))

    # High-frequency suppression for ω/N ≳ 1.5
    hf_suppress = 1.0 / (1.0 + np.exp((w_over_n - 1.5) / 0.10))

    # Sub-buoyancy tongue at low Ri and ω/N < 1
    low_ri = np.exp(-((ri - 0.15) ** 2) / (2 * 0.10**2))
    sub_buoy = low_ri * np.exp(-((w_over_n - 0.7) ** 2) / (2 * 0.25**2)) * 0.35

    sdi = lobe * stable_decay * hf_suppress + sub_buoy
    # Normalize to 0..1 for color scaling
    sdi -= sdi.min()
    sdi /= max(sdi.max(), 1e-9)
    return sdi


def plot_figure_3_6a(save_path_png: str | None = None, save_path_svg: str | None = None) -> mpl.figure.Figure:
    # Prepare figure
    fig, ax = plt.subplots(figsize=(18, 12), constrained_layout=False)
    apply_house_style(fig)

    # Axes setup
    set_common_frequency_axis(ax)
    set_common_ri_axis(ax)

    # Grid for heatmap
    w = np.linspace(0.2, 2.2, 400)
    r = np.linspace(0.0, 2.0, 300)
    W, R = np.meshgrid(w, r)
    Z = synthesize_sdi(R, W)

    # Colormap: use Viridis, darker = higher intensity -> standard Viridis is dark to bright.
    # We invert normalization so that higher values map to darker colors in a grayscale sense by using
    # a light-to-dark variant. Instead, use 'cividis' which is perceptually uniform and darker at high end.
    cmap = mpl.colormaps.get("cividis")

    # Display heatmap. Use extent to align axes in data coords.
    im = ax.imshow(
        Z,
        origin="lower",
        extent=(0.2, 2.2, 0.0, 2.0),
        aspect="auto",
        cmap=cmap,
        vmin=0.0,
        vmax=1.0,
        interpolation="bilinear",
        zorder=1,
    )

    # Conversion overlay and guides
    add_conversion_overlay(ax)

    # Optional dashed horizontal guide at Ri=0.25
    ax.axhline(0.25, color="#6B7280", linewidth=1.2, linestyle=(0, (4, 4)))
    ax.text(2.205, 0.25, "marginal stability", va="center", ha="right", fontsize=18)

    # Colorbar on the right
    cbar = make_colorbar(fig, im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Shear-dominance index (0–1)")
    cbar.set_ticks([0.0, 0.25, 0.5, 0.75, 1.0])

    # Title and caption
    add_panel_title(ax, "Figure 3.6A — Shear-dominance index SDI(Ri, ω/N)")
    add_caption(
        fig,
        ax,
        (
            "Bright regions indicate parameter pairs where shear-mediated loss dominates; peak influence occurs "
            "near ω/N≈1 under marginal Ri, and decays at higher Ri or ω/N>1."
        ),
    )

    # Legend style inside axes, frame off: nothing to add since heatmap only

    # Save outputs
    if save_path_png:
        fig.savefig(save_path_png, bbox_inches="tight")
    if save_path_svg:
        fig.savefig(save_path_svg, bbox_inches="tight")

    return fig


if __name__ == "__main__":
    fig = plot_figure_3_6a(
        save_path_png="/workspace/out/figures/figure_3_6a.png",
        save_path_svg="/workspace/out/figures/figure_3_6a.svg",
    )
    plt.close(fig)
