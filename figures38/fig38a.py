from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

from .house_style import (
    apply_house_style,
    amber_teal_diverging_colormap,
    add_conversion_band,
    configure_common_frequency_axis,
    add_caption,
    add_micro_label,
    contour_style_primary,
    make_colorbar,
    AMBER,
    TEAL,
    FONTS,
)


def _fields(nx: int = 420, ny: int = 320):
    x = np.linspace(0.2, 2.2, nx)
    y = np.linspace(0.0, 2.0, ny)
    X, Y = np.meshgrid(x, y)

    # Conversion activity: centered at x=1.0, stronger for Ri >= ~0.7
    sigma_c = 0.18
    conv_x = np.exp(-0.5 * ((X - 1.0) / sigma_c) ** 2)
    conv_y_gate = 1.0 / (1.0 + np.exp(-10.0 * (Y - 0.7)))
    C = conv_x * conv_y_gate

    # Shear activity: strongest for low Ri ~0.3, widest around band, taper for x >= 1.4
    sigma_s = 0.28
    shear_x = np.exp(-0.5 * ((X - 1.0) / sigma_s) ** 2)
    shear_y_gate = 1.0 / (1.0 + np.exp(10.0 * (Y - 0.45)))  # high at low Ri
    taper_high_x = np.exp(-((np.maximum(0.0, X - 1.4)) / 0.5) ** 2)
    S = shear_x * shear_y_gate * taper_high_x

    # Dominance index: 0=conversion, 1=shear
    eps = 1e-6
    D = S / (C + S + eps)

    return x, y, X, Y, D, C, S


def plot(fig=None, ax=None):
    apply_house_style()
    if fig is None or ax is None:
        fig, ax = plt.subplots()

    x, y, X, Y, D, C, S = _fields()

    cmap = amber_teal_diverging_colormap()
    mappable = ax.pcolormesh(
        X,
        Y,
        D,
        cmap=cmap,
        shading="auto",
        vmin=0.0,
        vmax=1.0,
        rasterized=False,  # keep vector patches in PDF/SVG
    )

    # Activity contours
    conv_levels = [0.35, 0.6]
    shear_levels = [0.35, 0.6]

    cs_conv = ax.contour(
        X,
        Y,
        C,
        levels=conv_levels,
        **contour_style_primary(AMBER, linewidth=2.5, dashed=False),
    )
    cs_shear = ax.contour(
        X,
        Y,
        S,
        levels=shear_levels,
        **contour_style_primary(TEAL, linewidth=2.5, dashed=True),
    )

    # Legend proxies
    from matplotlib.lines import Line2D

    legend_elems = [
        Line2D([0], [0], color=AMBER, lw=2.5, label="conversion activity"),
        Line2D([0], [0], color=TEAL, lw=2.5, dashes=(6, 6), label="shear activity"),
    ]
    ax.legend(handles=legend_elems, loc="upper left")

    # Axes
    configure_common_frequency_axis(ax)
    ax.set_ylim(0.0, 2.0)
    ax.set_yticks([0.0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
    ax.set_xlabel(r"$\omega/N$")
    ax.set_ylabel(r"$R_i$")
    ax.set_title("Figure 3.8A — Predicted dominant pathway in (Ri, ω/N) for continuous stratification")

    # Overlays
    add_conversion_band(ax)

    # Micro-labels
    add_micro_label(ax, 1.02, 1.15, "conversion basin", color=AMBER)
    add_micro_label(ax, 0.9, 0.35, "shear tongue (marginal Ri)", color=TEAL)

    # Grid already configured; colorbar
    make_colorbar(fig, ax, mappable, label=r"Dominant pathway index $D$ (0 = conversion, 1 = shear)")

    # Caption
    add_caption(
        fig,
        (
            "Figure 3.8A. Predicted dominant pathway map for continuous stratification. "
            "Conversion dominates near ω/N≈1 at higher Ri; shear dominates under marginal Ri, "
            "especially around the conversion band."
        ),
    )

    return fig, ax


if __name__ == "__main__":
    plot()
    plt.show()
