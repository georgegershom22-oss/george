from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from .house_style import (
    apply_house_style,
    add_caption,
    PURPLE,
    FONTS,
)


def _depth_curve(k: np.ndarray, cz: float) -> np.ndarray:
    # Target approximate behaviors using a smooth monotone function
    # Peak depth scales roughly linearly with C_Z, then decays with k
    start_map = {0.05: 5.0, 0.10: 9.0, 0.20: 15.0, 0.30: 19.0}
    end_map = {0.05: 1.5, 0.10: 3.5, 0.20: 7.0, 0.30: 9.0}

    d0 = start_map.get(cz, 10.0)
    d_inf = end_map.get(cz, 3.0)

    # Decay in log-k with smoothness
    k0 = 0.3
    alpha = 1.2
    decay = 1.0 / (1.0 + (k / k0) ** alpha)

    # Blend to reach end values near k=3
    # Scale decay to match endpoints approximately
    scale = (d0 - d_inf)
    depth = d_inf + scale * decay

    return depth


def plot(fig=None, ax=None):
    apply_house_style()
    if fig is None or ax is None:
        fig, ax = plt.subplots()

    k = np.geomspace(0.1, 3.0, 400)

    series = [0.05, 0.10, 0.20, 0.30]
    colors = {
        0.05: "#B8A6C9",  # light gray-purple
        0.10: PURPLE,      # purple
        0.20: "#4E2E6C",  # darker purple
        0.30: "#1F1230",  # nearly black-purple
    }

    for cz in series:
        y = _depth_curve(k, cz)
        label = fr"$C_Z={cz:.2f}$"
        ax.plot(k, y, color=colors[cz], linewidth=3.0, label=label)

    # Axes
    ax.set_xscale("log")
    ax.set_xlim(0.1, 3.0)
    ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 3])
    ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
    ax.set_xlabel(r"$k\delta$")

    ax.set_ylim(0, 20)
    ax.set_yticks(np.arange(0, 21, 5))
    ax.set_ylabel("Notch depth (dB)")

    ax.set_title("Figure 3.8D — Notch depth vs kδ for several impedance contrasts C_Z")

    # Bottom axis brace / cue
    y0 = -1.5
    ax.annotate(
        "thin → resonant → thick",
        xy=(0.1, y0),
        xytext=(3.0, y0),
        xycoords=("data", "data"),
        textcoords=("data", "data"),
        ha="center",
        va="top",
        fontsize=FONTS.note,
    )

    # Legend
    ax.legend(loc="upper right", title=r"$C_Z$")

    # Caption
    add_caption(
        fig,
        (
            "Figure 3.8D. Notch depth decreases as interface thickness kδ increases and increases with impedance "
            "contrast C_Z."
        ),
    )

    return fig, ax


if __name__ == "__main__":
    plot()
    plt.show()
