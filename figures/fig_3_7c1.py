from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from .house_style import (
    apply_rc_params,
    new_figure,
    style_share_axis,
    add_caption,
    save_figure,
    COLORS,
    PRIMARY_LW,
    SECONDARY_LW,
    DASH,
    FONT_SIZES,
    add_mechanism_legend,
)


def plot_c1(out_base: str) -> None:
    apply_rc_params()
    fig = new_figure()
    ax = fig.add_axes([0.10, 0.12, 0.80, 0.74])

    # Axes styling
    ax.set_xscale('log')
    ax.set_xlim(0.1, 3.0)
    ax.set_xticks([0.1, 0.2, 0.5, 1.0, 2.0, 3.0])
    ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
    ax.get_xaxis().set_minor_formatter(plt.NullFormatter())
    ax.grid(True, which='major', axis='both', color=COLORS['grid'], linewidth=0.8)

    style_share_axis(ax)
    ax.set_title("Figure 3.7C1 — Mechanism shares vs kδ (interface sharpness), fixed ω/N=1")
    ax.set_xlabel("kδ")
    ax.set_ylabel("Share (0–1)")

    # Data along kδ
    kd = np.logspace(np.log10(0.1), np.log10(3.0), 600)

    # Interfacial highest at low kd and monotonically decreases
    interf_raw = 1.8 * (kd ** -0.9)
    # Classical increases with kd
    classical_raw = 0.5 + 0.6 * (1 - np.exp(-1.5 * (kd - 0.1)))
    # Conversion roughly constant with a very mild bump near kd~1
    conv_raw = 0.55 + 0.06 * np.exp(-0.5 * ((np.log10(kd) - 0.0) / 0.25) ** 2)
    # Shear small and nearly flat
    shear_raw = 0.22 + 0.02 * np.cos(np.log(kd) * 2.0)

    total = interf_raw + classical_raw + conv_raw + shear_raw
    w_interf = interf_raw / total
    w_class = classical_raw / total
    w_conv = conv_raw / total
    w_shear = shear_raw / total

    # Stacked area in order: classical, conversion, interfacial, shear
    ax.stackplot(
        kd,
        w_class, w_conv, w_interf, w_shear,
        colors=[COLORS['classical'], COLORS['conversion'], COLORS['interfacial'], COLORS['shear']],
        linewidth=0,
    )

    # Mini gauge beneath x-axis
    # Draw small bracket-like markers at 0.1, 1, 3 with labels
    y0 = -0.12
    for x, label in [(0.1, 'thin'), (1.0, 'resonant'), (3.0, 'thick')]:
        ax.annotate('', xy=(x, y0 + 0.02), xytext=(x, y0 - 0.02), xycoords=('data', 'axes fraction'),
                    arrowprops=dict(arrowstyle='-[,widthB=2.0', lw=1.2, color='#9CA3AF'))
        ax.text(x, y0 - 0.06, label, ha='center', va='top', fontsize=FONT_SIZES['tick'])
    ax.text(1.0, y0 + 0.06, 'thin → resonant → thick', ha='center', va='bottom', fontsize=FONT_SIZES['note'])

    add_mechanism_legend(ax, loc='upper right')

    add_caption(fig, "Figure 3.7C1. Interfacial share peaks for sharp, high-contrast transitions (low kδ) and decays as the interface becomes diffuse (large kδ). Classical share increases complementarily; conversion and shear change little at fixed ω/N.")

    save_figure(fig, out_base)
    plt.close(fig)
