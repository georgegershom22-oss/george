from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

from house_style import (
    new_canvas,
    set_omega_over_N_axis,
    set_Ri_axis,
    add_conversion_band,
    add_title_inside,
    add_caption,
    add_colorbar,
    add_marginal_stability_line,
    HEATMAP_CMAP,
    COLORS,
    PSD_TICKS,
    save_figure,
)


def generate_sdi(Ri: np.ndarray, w_on_N: np.ndarray) -> np.ndarray:
    """Synthetic shear-dominance index field with qualitative features per spec (0..1)."""
    Ri_grid, W_grid = np.meshgrid(Ri, w_on_N, indexing="ij")

    # Core lobe near Ri~0.4, w/N~1 with horizontal elongation and rapid decay with Ri
    lobe = np.exp(-((Ri_grid - 0.4) ** 2) / (2 * 0.10 ** 2)) * np.exp(-((W_grid - 1.0) ** 2) / (2 * 0.25 ** 2))
    # High-frequency suppression for w/N >= 1.4-1.6
    hf_suppress = 1.0 / (1.0 + np.exp(8.0 * (W_grid - 1.5)))
    # Decay with stability Ri -> 2
    ri_decay = np.exp(-((Ri_grid - 0.4) / 1.2) ** 2)
    # Sub-buoyancy tail at very low Ri for w/N < 1
    tail = np.exp(-((Ri_grid - 0.1) ** 2) / (2 * 0.06 ** 2)) * np.exp(-((W_grid - 0.8) ** 2) / (2 * 0.20 ** 2))

    field = 0.8 * lobe * hf_suppress * ri_decay + 0.25 * tail

    # Normalize to 0..1
    field -= field.min()
    if field.max() > 0:
        field /= field.max()
    return field


def main() -> None:
    Ri = np.linspace(0.0, 2.0, 300)
    W = np.linspace(0.2, 2.2, 360)

    SDI = generate_sdi(Ri, W)

    fig = new_canvas()
    ax = fig.add_axes([0.10, 0.10, 0.74, 0.80])  # left, bottom, width, height

    # Plot heatmap with darker=higher using cividis_r
    im = ax.imshow(
        SDI,
        origin="lower",
        aspect="auto",
        cmap=HEATMAP_CMAP,
        extent=[W.min(), W.max(), Ri.min(), Ri.max()],
        norm=Normalize(vmin=0.0, vmax=1.0),
        zorder=0,
    )

    # Axes styling
    set_omega_over_N_axis(ax)
    set_Ri_axis(ax)

    # Overlays & guides
    add_conversion_band(ax, orientation="vertical")
    add_marginal_stability_line(ax)

    # Titles & labels
    add_title_inside(ax, r"Figure 3.6A — Shear-dominance index SDI($R_i,\,\omega/N$)")

    # Colorbar (right)
    cbar = add_colorbar(fig, im, ax, label="Shear-dominance index (0–1)", ticks=[0, 0.25, 0.5, 0.75, 1.0])

    # Caption
    add_caption(
        fig,
        "Bright regions indicate parameter pairs where shear-mediated loss dominates; peak influence occurs near "
        r"$\omega/N \approx 1$ under marginal $R_i$, and decays at higher $R_i$ or $\omega/N>1$.",
    )

    save_figure(fig, "/workspace/out/figures/figure_3_6a")


if __name__ == "__main__":
    main()
