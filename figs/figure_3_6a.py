import numpy as np
import matplotlib.pyplot as plt
from figs.house_style import (
    apply_house_style, dark_colormap, omega_N_Ri_mesh,
    make_axes_omega_over_N, make_axes_Ri, add_conversion_overlay,
    add_panel_title, colorbar_right, add_caption, export
)


def synthetic_sdi(W, R):
    # Bright lobe centered near (Ri~0.4, w/N~1), decays with Ri and |w/N-1|
    lobe = np.exp(-((R - 0.4) ** 2) / (2 * 0.12 ** 2)) * np.exp(-((W - 1.0) ** 2) / (2 * 0.18 ** 2))
    # High-frequency suppression for w/N > 1.4-1.6
    hf_supp = np.exp(-np.maximum(0, W - 1.4) / 0.25)
    # Decay with stability towards Ri ~ 1-2
    ri_decay = np.exp(-np.maximum(0, R - 0.6) / 0.5)
    # Sub-buoyancy tail at low Ri extending below 1
    tail = 0.35 * np.exp(-R / 0.25) * np.exp(-((W - 0.8) ** 2) / (2 * 0.25 ** 2))
    sdi = lobe * hf_supp * ri_decay + tail
    sdi = np.clip(sdi, 0.0, 1.0)
    return sdi


def main():
    apply_house_style()

    W, R = omega_N_Ri_mesh()
    Z = synthetic_sdi(W, R)

    fig, ax = plt.subplots(1, 1)

    cmap = dark_colormap("cividis")
    im = ax.pcolormesh(W, R, Z, shading="auto", cmap=cmap, vmin=0.0, vmax=1.0)

    make_axes_omega_over_N(ax, add_conversion_band=True)
    make_axes_Ri(ax)

    # Optional dashed horizontal guide at Ri=0.25
    ax.axhline(0.25, color="#666666", linestyle=(0, (4, 3)), linewidth=1.2)
    ax.text(2.2, 0.25, "  marginal stability", va="center", ha="right", fontsize=18)

    add_panel_title(ax, "Figure 3.6A — Shear-dominance index SDI(Ri,ω/N)")

    cbar = colorbar_right(fig, im, label="Shear-dominance index (0–1)",
                          ticks=[0, 0.25, 0.5, 0.75, 1.0], ax=ax)
    cbar.ax.invert_yaxis()  # darker = higher (since colormap reversed for darkness)

    add_caption(fig, (
        "Bright regions indicate parameter pairs where shear-mediated loss dominates; "
        "peak influence occurs near ω/N≈1 under marginal Ri, and decays at higher Ri or ω/N>1."
    ))

    export(fig, "/workspace/out/figures/figure_3_6a")


if __name__ == "__main__":
    main()
