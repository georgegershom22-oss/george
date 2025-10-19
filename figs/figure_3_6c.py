import numpy as np
import matplotlib.pyplot as plt
from figs.house_style import (
    apply_house_style, make_axes_omega_over_N, add_panel_title,
    add_caption, export, SOLID_DEEP_BLUE, DASHED_STEEL_BLUE,
    half_power_bandwidth
)


def coherent_fraction_curve(ri):
    # Monotone decreasing from ~0.95 at Ri=2 to ~0.5 at Ri=0.25, with a notch near 0.3–0.5
    base = 0.5 + 0.45 * (ri / 2.0)  # 0.5 at 0, 0.95 at 2
    notch = 0.12 * np.exp(-((ri - 0.38) ** 2) / (2 * 0.06 ** 2))
    return np.clip(base - notch, 0.0, 1.0)


def psd_curves(omega):
    # High Ri: narrow peak near 1
    high = np.exp(-((omega - 1.0) ** 2) / (2 * 0.08 ** 2))
    # Marginal Ri: broader peak
    marg = np.exp(-((omega - 1.0) ** 2) / (2 * 0.18 ** 2)) * (0.95 - 0.05 * np.sin(7 * omega))
    # Normalize to 1
    high /= high.max()
    marg /= marg.max()
    return high, marg


def main():
    apply_house_style()

    fig = plt.figure()

    # Layout: two subpanels side by side
    left = 0.08
    right_margin = 0.06
    gutter_px = 40
    gutter = gutter_px / (fig.dpi * fig.get_figwidth() * fig.dpi / fig.dpi)
    total_width = 1.0 - left - right_margin
    panel_width = (total_width - gutter) / 2.0
    panel_height = 0.7
    bottom = 0.2

    axL = fig.add_axes([left, bottom, panel_width, panel_height])
    axR = fig.add_axes([left + panel_width + gutter, bottom, panel_width, panel_height])

    # Left: coherent fraction vs Ri
    ri = np.linspace(0.0, 2.0, 400)
    y = coherent_fraction_curve(ri)

    axL.plot(ri, y, **SOLID_DEEP_BLUE, label="coherent fraction")
    axL.set_xlim(0.0, 2.0)
    axL.set_xticks([0.0, 0.5, 1.0, 1.5, 2.0])
    axL.set_ylim(0.0, 1.0)
    axL.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    axL.set_xlabel(r"$R_i$")
    axL.set_ylabel("coherent fraction")

    # Variability band around notch (steel-blue, 20% opacity)
    band_center = 0.42
    band_half_width = 0.14
    axL.axvspan(band_center - band_half_width, band_center + band_half_width,
                color="#457B9D", alpha=0.2)

    axL.annotate("stable: high coherent fraction", xy=(1.8, 0.9), xytext=(1.2, 0.95),
                 arrowprops=dict(arrowstyle="->"), fontsize=18)
    axL.annotate("marginal: additional loss & variability", xy=(0.42, y[np.argmin(np.abs(ri - 0.42))]),
                 xytext=(0.7, 0.55), arrowprops=dict(arrowstyle="->"), fontsize=18)

    # Right: PSD broadening under marginal Ri
    w = np.linspace(0.2, 2.2, 600)
    high, marg = psd_curves(w)

    axR.plot(w, high, **SOLID_DEEP_BLUE, label="high $R_i$")
    axR.plot(w, marg, **DASHED_STEEL_BLUE, label="marginal $R_i$")

    make_axes_omega_over_N(axR, add_conversion_band=True)
    axR.set_ylim(0.0, 1.05)
    axR.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    axR.set_ylabel("normalized PSD")

    # Optional half-power bandwidth bars
    # For high Ri curve (find ~0.5 crossings)
    def half_power_points(ycurve):
        level = 0.5
        idx = np.where(np.diff((ycurve >= level).astype(int)) != 0)[0]
        if idx.size >= 2:
            return w[idx[0]], w[idx[-1]]
        return 0.9, 1.1

    l_high, r_high = half_power_points(high)
    l_marg, r_marg = half_power_points(marg)

    half_power_bandwidth(axR, 1.0, l_high, r_high, 0.5, label="BW")
    half_power_bandwidth(axR, 1.0, l_marg, r_marg, 0.35, label="BW")

    axR.text(1.55, 0.82, "broader PSD under marginal $R_i$", fontsize=18)

    axR.legend(loc="upper right", frameon=False)

    add_panel_title(axL, "Figure 3.6C — Coherence loss and spectral broadening with decreasing $R_i$")

    add_caption(fig, (
        "Coherent fraction declines monotonically with a superposed dip near marginal $R_i$; "
        "spectra broaden under marginal $R_i$, indicating enhanced shear-mediated variability."
    ))

    export(fig, "/workspace/out/figures/figure_3_6c")


if __name__ == "__main__":
    main()
