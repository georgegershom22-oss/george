from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from .house_style import (
    apply_house_style,
    add_caption,
    make_colorbar,
    FONTS,
)


def _heatmap(nx: int = 420, ny: int = 320):
    # Axes: x = kδ (log), y = C_Z
    x = np.geomspace(0.1, 3.0, nx)
    y = np.linspace(0.0, 0.40, ny)
    X, Y = np.meshgrid(x, y)

    # Notch strength S increases with C_Z, decreases with kδ
    # Shape: stronger (dark) at small kδ and large C_Z
    k0 = 0.6
    alpha = 1.4
    beta = 1.1
    S = (Y / 0.40) ** beta * (1.0 / (1.0 + (X / k0) ** alpha))
    S = np.clip(S, 0.0, 1.0)

    return x, y, X, Y, S


def plot(fig=None, ax=None):
    apply_house_style()
    if fig is None or ax is None:
        fig, ax = plt.subplots()

    x, y, X, Y, S = _heatmap()

    # Use a grayscale reversed so darker = stronger
    mappable = ax.pcolormesh(
        X,
        Y,
        S,
        shading="auto",
        cmap="Greys_r",
        vmin=0.0,
        vmax=1.0,
        rasterized=False,
    )

    # Dashed isolines
    levels = [0.25, 0.5, 0.75]
    cs = ax.contour(X, Y, S, levels=levels, colors="#374151", linewidths=2.0, linestyles="--")
    fmt = {levels[0]: "weak", levels[1]: "moderate", levels[2]: "strong"}
    ax.clabel(cs, cs.levels, inline=True, fmt=fmt, fontsize=FONTS.tick)

    # Axes styling
    ax.set_xscale("log")
    ax.set_xlim(0.1, 3.0)
    ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 3])
    ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
    ax.set_xlabel(r"$k\delta$")

    ax.set_ylim(0.0, 0.40)
    ax.set_yticks([0.00, 0.10, 0.20, 0.30, 0.40])
    ax.set_ylabel(r"$C_Z = |Z_2 - Z_1|/(Z_2 + Z_1)$")

    ax.set_title("Figure 3.8B — Layered regime map in (C_Z, kδ): predicted notch strength")

    # Colorbar
    make_colorbar(fig, ax, mappable, label="Predicted notch strength (arb.)")

    # Caption
    add_caption(
        fig,
        (
            "Figure 3.8B. Notch strength increases with impedance contrast C_Z and decreases with interface "
            "thickness kδ; sharp, high-contrast layers produce strong comb-like reverberation."
        ),
    )

    return fig, ax


if __name__ == "__main__":
    plot()
    plt.show()
