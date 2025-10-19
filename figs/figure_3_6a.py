from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

from house_style import (
    apply_base_style,
    configure_shared_axes,
    draw_conversion_band,
    add_panel_title,
    add_caption,
    add_horizontal_guide,
    add_colorbar,
    HEATMAP_CMAP,
    COLOR_BLUE,
    COLOR_STEEL,
    COLOR_MAGENTA,
    save_figure,
)


def synthetic_sdi(Ri: np.ndarray, wN: np.ndarray) -> np.ndarray:
    """Construct a qualitative SDI field matching the described physics.

    - Bright, elongated island near (Ri≈0.4, ω/N≈1), fades with Ri and high ω/N.
    - Sub-buoyancy tail for low Ri and ω/N < 1.
    Output in [0, 1].
    """
    # Centered lobe near Ri0, w0
    Ri0, w0 = 0.4, 1.0
    # Anisotropic Gaussian with stronger elongation along ω/N
    sigma_Ri_low = 0.15
    sigma_w = 0.20
    lobe = np.exp(-((Ri - Ri0) ** 2) / (2 * sigma_Ri_low ** 2) - ((wN - w0) ** 2) / (2 * sigma_w ** 2))

    # Fade with stability: exponential decay as Ri increases to 1–2
    fade_Ri = np.exp(-2.0 * np.maximum(0, Ri - 0.6))

    # High-frequency suppression beyond ~1.4–1.6
    hf_cut = 1.0 / (1.0 + np.exp(20 * (wN - 1.5)))  # smooth step decreasing after 1.5

    # Sub-buoyancy tail at very low Ri and ω/N < 1
    tail = np.exp(-((wN - 0.8) ** 2) / (2 * 0.25 ** 2)) * np.exp(-((Ri - 0.1) ** 2) / (2 * 0.10 ** 2))

    sdi = 1.2 * lobe * fade_Ri * hf_cut + 0.4 * tail

    # Normalize into [0,1]
    sdi -= sdi.min()
    maxv = sdi.max()
    if maxv > 0:
        sdi /= maxv
    return sdi


def plot_figure_3_6a():
    apply_base_style()

    fig, ax = plt.subplots(1, 1)
    configure_shared_axes(ax, x_kind="omega_over_N", y_kind="Ri")

    # Create grid
    w = np.linspace(0.2, 2.2, 400)
    Ri = np.linspace(0.0, 2.0, 400)
    W, R = np.meshgrid(w, Ri)
    Z = synthetic_sdi(R, W)

    im = ax.imshow(
        Z,
        origin="lower",
        extent=(w.min(), w.max(), Ri.min(), Ri.max()),
        aspect="auto",
        cmap=HEATMAP_CMAP,
        norm=Normalize(0, 1),
        interpolation="bilinear",
    )

    # Overlays and guides
    draw_conversion_band(ax, axis="x")
    add_horizontal_guide(ax, 0.25, label="marginal stability")

    # Title & labels & caption
    add_panel_title(ax, "Figure 3.6A — Shear-dominance index SDI(Ri,ω/N)")

    # Colorbar: darker = higher, ticks at 0..1
    add_colorbar(
        fig,
        im,
        label="Shear-dominance index (0–1)",
        ticks=(0.0, 0.25, 0.5, 0.75, 1.0),
        ax=ax,
        pad=0.02,
        shrink=0.95,
    )

    caption = (
        "Bright regions indicate parameter pairs where shear-mediated loss dominates; "
        "peak influence occurs near ω/N≈1 under marginal Ri, and decays at higher Ri or ω/N>1."
    )
    add_caption(ax, caption)

    save_figure(fig, "figure_3_6a")
    plt.close(fig)


if __name__ == "__main__":
    plot_figure_3_6a()
