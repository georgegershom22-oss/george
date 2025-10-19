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
    add_panel_title,
    add_caption,
    add_colorbar,
    show_heatmap,
    save_figure,
)


# Synthetic SDI field with qualitative behavior per spec
# - Bright, elongated island near (Ri≈0.4, w/N≈1)
# - Rapid decay as Ri → 1–2
# - Suppression for w/N ≳ 1.4–1.6
# - Weaker sub-buoyancy tongue at low Ri and w/N < 1

def synth_sdi(ri: np.ndarray, wn: np.ndarray) -> np.ndarray:
    # Core elongated Gaussian near (0.4, 1.0)
    core = np.exp(-((ri - 0.40) / 0.22) ** 2) * np.exp(-((wn - 1.00) / 0.18) ** 2)

    # Fade with increasing Ri (smoothly reduce beyond ~0.6)
    fade_ri = 1.0 / (1.0 + np.exp((ri - 0.60) / 0.10))  # ~1 below 0.6, decays above

    # High-frequency suppression beyond ~1.45
    suppress_hf = 1.0 / (1.0 + np.exp((wn - 1.45) / 0.06))

    # Sub-buoyancy tail at low Ri and wn < 1
    tail = 0.35 * np.exp(-((ri - 0.15) / 0.15) ** 2) * np.exp(-((wn - 0.75) / 0.22) ** 2)

    sdi = core * fade_ri * suppress_hf + tail

    # Normalize to [0, 1]
    sdi -= sdi.min()
    sdi_max = sdi.max() if sdi.max() > 0 else 1.0
    sdi /= sdi_max
    return sdi


def main() -> None:
    fig, axes = create_canvas()
    ax = axes.ravel()[0]

    # Domain
    wn = np.linspace(STYLE.freq_min, STYLE.freq_max, 400)  # w/N
    ri = np.linspace(STYLE.ri_min, STYLE.ri_max, 300)      # Ri
    WN, RI = np.meshgrid(wn, ri)

    Z = synth_sdi(RI, WN)

    # Heatmap
    extent = (STYLE.freq_min, STYLE.freq_max, STYLE.ri_min, STYLE.ri_max)
    im = show_heatmap(ax, Z, extent=extent, vmin=0.0, vmax=1.0)

    # Axes styling
    set_freq_axis(ax, axis="x")
    set_ri_axis(ax, axis="y")
    style_grid(ax)

    # Overlays & guides
    overlay_conversion_band(ax, align_to="x")
    ax.axhline(0.25, color=STYLE.steel_blue, linestyle=(0, (6, 4)), linewidth=2/3, alpha=0.9)
    ax.text(0.985, 0.25 + 0.03*(STYLE.ri_max-STYLE.ri_min), "marginal stability", color=STYLE.steel_blue,
            fontsize=STYLE.note_size_pt, ha="right", va="bottom")

    # Title & colorbar & caption
    add_panel_title(ax, r"Figure 3.6A — Shear-dominance index $SDI(R_i,\,\omega/N)$")
    cbar = add_colorbar(fig, im, label="Shear-dominance index (0–1)",
                        ticks=[0.0, 0.25, 0.5, 0.75, 1.0], ax=ax)
    add_caption(ax, "Bright regions indicate parameter pairs where shear-mediated loss dominates; "
                    "peak influence occurs near $\\omega/N\\approx1$ under marginal $R_i$, "
                    "and decays at higher $R_i$ or $\\omega/N>1$.")

    save_figure(fig, "/workspace/out/figures/figure_3_6a")


if __name__ == "__main__":
    main()
