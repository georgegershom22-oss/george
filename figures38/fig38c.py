from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from .house_style import (
    apply_house_style,
    add_conversion_band,
    configure_common_frequency_axis,
    add_caption,
    FONTS,
    TEAL,
)


COLORS = {
    1.5: "#0B3C5D",  # deep blue
    1.0: "#4F6D7A",  # steel blue
    0.6: TEAL,        # teal
    0.3: "#B3007D",  # magenta
}


def _curve(x: np.ndarray, ri: float) -> np.ndarray:
    # Baseline TL level
    base = 30.0

    # Conversion peak around x=1, width narrows with higher Ri
    width = np.interp(ri, [0.3, 1.5], [0.5, 0.15])
    height = np.interp(ri, [0.3, 1.5], [15.0, 38.0])
    peak = height * np.exp(-0.5 * ((x - 1.0) / width) ** 2)

    # Broadband skirts increase as Ri decreases; symmetric shoulders
    skirts = np.interp(ri, [0.3, 1.5], [18.0, 2.0])
    shoulder = skirts * (
        np.exp(-((x - 0.8) / 0.25) ** 2) + np.exp(-((x - 1.35) / 0.35) ** 2)
    )

    y = base + peak + shoulder
    return y


def plot(fig=None, ax=None):
    apply_house_style()
    if fig is None or ax is None:
        fig, ax = plt.subplots()

    x = np.linspace(0.2, 2.2, 600)

    sequences = [1.5, 1.0, 0.6, 0.3]
    for ri in sequences:
        y = _curve(x, ri)
        if ri == 0.3:
            ax.plot(x, y, color=COLORS[ri], dashes=(6, 6), linewidth=3.0, label=r$fR_i={ri}$")
        else:
            ax.plot(x, y, color=COLORS[ri], linewidth=3.0, label=fr"$R_i={ri}$")

    # Axes and overlays
    configure_common_frequency_axis(ax)
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(20, 80)
    ax.set_yticks(np.arange(20, 81, 10))
    ax.set_xlabel(r"$\omega/N$")
    ax.set_ylabel("TL (dB)")
    ax.set_title("Figure 3.8C — Qualitative scaling of apparent attenuation vs ω/N at selected Ri")

    add_conversion_band(ax)

    # Arrow notes
    ax.annotate(
        "peak widens as Ri↓",
        xy=(1.0, 68),
        xytext=(1.45, 76),
        arrowprops=dict(arrowstyle="->", color="#374151", lw=2),
        fontsize=FONTS.note,
    )
    ax.annotate(
        "skirts grow (broadband loss)",
        xy=(1.45, 54),
        xytext=(1.8, 72),
        arrowprops=dict(arrowstyle="->", color="#374151", lw=2),
        fontsize=FONTS.note,
    )

    # Legend inside axes
    ax.legend(loc="upper left", title="Selected $R_i$")

    # Caption
    add_caption(
        fig,
        (
            "Figure 3.8C. Apparent attenuation vs ω/N for selected Ri. Decreasing Ri broadens the conversion "
            "peak and raises broadband skirts."
        ),
    )

    return fig, ax


if __name__ == "__main__":
    plot()
    plt.show()
