from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from house_style import (
    apply_base_style,
    configure_shared_axes,
    draw_conversion_band,
    add_caption,
    add_colorbar,
    save_figure,
    PT_INPLOT,
    COLOR_BLUE,
    COLOR_STEEL,
)


def synthetic_coherent_fraction(Ri: np.ndarray):
    # Monotone decreasing from ~0.95 at Ri=2 to ~0.5 at Ri=0.25, with notch around 0.3–0.5
    base = 0.5 + 0.45 * np.tanh(2.0 * (Ri - 0.25))  # increases with Ri
    base = (base - base.min()) / (base.max() - base.min())  # 0..1
    # Scale to ~0.5..0.95
    cf = 0.5 + 0.45 * base
    # Notch (dip) around 0.3–0.5
    notch = 0.12 * np.exp(-((Ri - 0.4) ** 2) / (2 * 0.08 ** 2))
    cf = np.clip(cf - notch, 0, 1)
    return cf


def synthetic_psd(w: np.ndarray, kind="narrow"):
    # Gaussian-like normalized PSD centered at 1.0
    center = 1.0
    if kind == "narrow":
        bw = 0.10
        peaky = np.exp(-((w - center) ** 2) / (2 * bw ** 2))
        peaky += 0.15 * np.exp(-((w - center) ** 2) / (2 * (2*bw) ** 2))
        psd = peaky
    else:
        bw = 0.25
        plateau = np.exp(-((w - center) ** 2) / (2 * bw ** 2))
        plateau += 0.10 * np.random.default_rng(5).standard_normal(w.shape)
        psd = np.clip(plateau, 0, None)
    # Normalize to 0..1
    psd -= psd.min()
    if psd.max() > 0:
        psd /= psd.max()
    return psd


def plot_figure_3_6c():
    apply_base_style()

    fig, (axL, axR) = plt.subplots(1, 2, gridspec_kw=dict(wspace=0.15))

    # Left: coherent fraction vs Ri
    Ri = np.linspace(0.0, 2.0, 400)
    cf = synthetic_coherent_fraction(Ri)

    configure_shared_axes(axL, x_kind="Ri", y_kind=None)
    axL.set_xlim(0.0, 2.0)
    axL.set_xlabel("Ri")
    axL.set_ylim(0.0, 1.0)
    axL.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    axL.set_ylabel("coherent fraction")

    axL.plot(Ri, cf, color=COLOR_BLUE, linewidth=3.0)

    # Variability band around the notch region 0.3–0.5
    notch_min, notch_max = 0.3, 0.5
    idx = (Ri >= notch_min) & (Ri <= notch_max)
    band_y0 = np.clip(cf[idx] - 0.06, 0, 1)
    band_y1 = np.clip(cf[idx] + 0.06, 0, 1)
    axL.fill_between(Ri[idx], band_y0, band_y1, color="#457B9D", alpha=0.20)

    # Arrow notes
    axL.annotate("stable: high coherent fraction", xy=(1.7, 0.9), xytext=(1.1, 0.95),
                 arrowprops=dict(arrowstyle="->"))
    axL.annotate("marginal: additional loss & variability", xy=(0.42, cf[(np.abs(Ri-0.42)).argmin()]),
                 xytext=(0.75, 0.6), arrowprops=dict(arrowstyle="->"))

    # Right: PSD broadening
    w = np.linspace(0.2, 2.2, 600)
    configure_shared_axes(axR, x_kind="omega_over_N", y_kind=None)
    axR.set_ylim(0.0, 1.0)
    axR.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    axR.set_ylabel("normalized PSD")

    psd_narrow = synthetic_psd(w, kind="narrow")
    psd_broad = synthetic_psd(w, kind="broad")

    axR.plot(w, psd_narrow, color=COLOR_BLUE, linewidth=3.0, label="high Ri")
    axR.plot(w, psd_broad, color=COLOR_STEEL, linewidth=3.0, linestyle=(0, (6, 4)), label="marginal Ri")

    # Optional half-power bandwidth bars
    def half_power_band(x, y, center=1.0):
        half = 0.5
        # Find crossings around center
        left = x[x < center]
        right = x[x > center]
        yl = y[x < center]
        yr = y[x > center]
        try:
            wl = left[np.argmin(np.abs(yl - half))]
            wr = right[np.argmin(np.abs(yr - half))]
            return wl, wr
        except Exception:
            return None

    for curve, color, yoff, tag in [
        (psd_narrow, COLOR_BLUE, 0.06, "BW"),
        (psd_broad, COLOR_STEEL, -0.06, "BW"),
    ]:
        hp = half_power_band(w, curve)
        if hp is not None:
            wl, wr = hp
            y0 = 0.05 if curve is psd_narrow else 0.12
            axR.annotate("", xy=(wl, y0), xytext=(wr, y0),
                         arrowprops=dict(arrowstyle="<->", color="#111827"))
            axR.text((wl + wr) / 2, y0 + yoff, "BW", ha="center")

    axR.text(1.55, 0.85, "broader PSD under marginal Ri")
    axR.legend(loc="upper right", frameon=False)

    # Title on top
    fig.suptitle("Figure 3.6C — Coherence loss and spectral broadening with decreasing Ri", x=0.06, ha='left')

    # Captions below panels
    add_caption(axL, "Coherent fraction declines monotonically with a superposed dip near marginal Ri.")
    add_caption(axR, "Spectra broaden under marginal Ri, indicating enhanced shear-mediated variability.")

    save_figure(fig, "figure_3_6c")
    plt.close(fig)


if __name__ == "__main__":
    plot_figure_3_6c()
