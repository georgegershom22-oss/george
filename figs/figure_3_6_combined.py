from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from house_style import (
    apply_base_style,
    configure_shared_axes,
    draw_conversion_band,
    add_caption,
    add_colorbar,
    add_horizontal_guide,
    save_figure,
    HEATMAP_CMAP,
    PT_INPLOT,
    COLOR_BLUE,
    COLOR_STEEL,
)

# Import synthetic generators from earlier scripts without executing them
# Re-define lightweight versions here to avoid cross-file execution side effects

def synthetic_sdi(Ri: np.ndarray, wN: np.ndarray) -> np.ndarray:
    Ri0, w0 = 0.4, 1.0
    sigma_Ri_low = 0.15
    sigma_w = 0.20
    lobe = np.exp(-((Ri - Ri0) ** 2) / (2 * sigma_Ri_low ** 2) - ((wN - w0) ** 2) / (2 * sigma_w ** 2))
    fade_Ri = np.exp(-2.0 * np.maximum(0, Ri - 0.6))
    hf_cut = 1.0 / (1.0 + np.exp(20 * (wN - 1.5)))
    tail = np.exp(-((wN - 0.8) ** 2) / (2 * 0.25 ** 2)) * np.exp(-((Ri - 0.1) ** 2) / (2 * 0.10 ** 2))
    sdi = 1.2 * lobe * fade_Ri * hf_cut + 0.4 * tail
    sdi -= sdi.min()
    if sdi.max() > 0:
        sdi /= sdi.max()
    return sdi


def synthetic_scalogram(shape=(300, 300), mode="stable", rng=None):
    if rng is None:
        rng = np.random.default_rng(7)
    t_len, f_len = shape
    base = np.zeros(shape)
    f = np.linspace(0.2, 2.2, f_len)
    t = np.linspace(0, 60, t_len)
    ridge = np.exp(-((f - 1.0) ** 2) / (2 * 0.04 ** 2))
    ridge = ridge[None, :] * (0.6 + 0.1 * np.sin(2 * np.pi * t[:, None] / 40.0))
    if mode == "stable":
        base = ridge
        base += 0.03 * rng.standard_normal(shape)
        base = np.clip(base, 0, None)
    else:
        base = 0.25 * ridge
        for _ in range(14):
            tc = rng.uniform(5, 55)
            fc = rng.uniform(0.5, 1.8)
            t_bw = rng.uniform(3, 10)
            f_bw = rng.uniform(0.15, 0.45)
            amp = rng.uniform(0.5, 1.0)
            T, F = np.meshgrid(t, f, indexing="ij")
            blob = amp * np.exp(-((T - tc) ** 2) / (2 * t_bw ** 2) - ((F - fc) ** 2) / (2 * f_bw ** 2))
            blob *= np.exp(-0.5 * ((F - fc) - 0.01 * (T - tc)) ** 2 / (f_bw ** 2))
            base += blob
        base += 0.06 * rng.standard_normal(shape)
        base = np.clip(base, 0, None)
    base -= base.min()
    if base.max() > 0:
        base /= base.max()
    return base, t, f


def synthetic_coherent_fraction(Ri: np.ndarray):
    base = 0.5 + 0.45 * np.tanh(2.0 * (Ri - 0.25))
    base = (base - base.min()) / (base.max() - base.min())
    cf = 0.5 + 0.45 * base
    notch = 0.12 * np.exp(-((Ri - 0.4) ** 2) / (2 * 0.08 ** 2))
    cf = np.clip(cf - notch, 0, 1)
    return cf


def synthetic_psd(w: np.ndarray, kind="narrow"):
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
    psd -= psd.min()
    if psd.max() > 0:
        psd /= psd.max()
    return psd


def plot_combined():
    apply_base_style()

    fig = plt.figure()
    # Layout: 2 rows
    # Row 1: 3.6A full width
    # Row 2: 3.6B (two panels) and 3.6C (two panels) side by side? The request says one single figure containing 3.6A–C.
    # We'll stack A on top, and place B (two panels) and C (two panels) beneath in two equal-width blocks.
    gs = GridSpec(nrows=2, ncols=2, height_ratios=[1.1, 1.0], width_ratios=[1.0, 1.0], hspace=0.25, wspace=0.10, figure=fig)

    # 3.6A occupies top row, both columns
    axA = fig.add_subplot(gs[0, :])
    configure_shared_axes(axA, x_kind="omega_over_N", y_kind="Ri")
    w = np.linspace(0.2, 2.2, 400)
    Ri = np.linspace(0.0, 2.0, 400)
    W, R = np.meshgrid(w, Ri)
    Z = synthetic_sdi(R, W)
    imA = axA.imshow(Z, origin="lower", extent=(w.min(), w.max(), Ri.min(), Ri.max()), aspect="auto", cmap=HEATMAP_CMAP, vmin=0, vmax=1, interpolation="bilinear")
    draw_conversion_band(axA, axis="x")
    add_horizontal_guide(axA, 0.25, label="marginal stability")
    axA.set_title("Figure 3.6A — Shear-dominance index SDI(Ri,ω/N)", loc="left")
    add_colorbar(fig, imA, label="Shear-dominance index (0–1)", ticks=(0.0,0.25,0.5,0.75,1.0), ax=axA, pad=0.01, shrink=0.95)
    add_caption(axA, "Bright regions indicate parameter pairs where shear-mediated loss dominates; peak influence occurs near ω/N≈1 under marginal Ri, and decays at higher Ri or ω/N>1.")

    # 3.6B on bottom-left: two subpanels sharing colorbar (to the right of the right subpanel)
    gsB = GridSpec(nrows=1, ncols=2, wspace=0.08, figure=fig, left=0.08, right=0.52, bottom=0.08, top=0.52)
    axB_L = fig.add_subplot(gsB[0,0])
    axB_R = fig.add_subplot(gsB[0,1])

    configure_shared_axes(axB_L, x_kind="time", y_kind="omega_over_N")
    dataL, tB, fB = synthetic_scalogram(mode="stable")
    imBL = axB_L.imshow(dataL, origin="lower", extent=(tB.min(), tB.max(), fB.min(), fB.max()), aspect="auto", cmap=HEATMAP_CMAP, vmin=0, vmax=1, interpolation="bilinear")
    draw_conversion_band(axB_L, axis="y")
    axB_L.text(0.02, 0.92, "narrow conversion-band modulation", transform=axB_L.transAxes, fontsize=PT_INPLOT)
    add_caption(axB_L, "High Ri: fluctuation energy concentrated in a narrow conversion band.")

    configure_shared_axes(axB_R, x_kind="time", y_kind="omega_over_N")
    dataR, tB, fB = synthetic_scalogram(mode="marginal", rng=np.random.default_rng(9))
    imBR = axB_R.imshow(dataR, origin="lower", extent=(tB.min(), tB.max(), fB.min(), fB.max()), aspect="auto", cmap=HEATMAP_CMAP, vmin=0, vmax=1, interpolation="bilinear")
    draw_conversion_band(axB_R, axis="y")
    axB_R.annotate("intermittent broadband bursts", xy=(40, 1.6), xytext=(48, 2.0), arrowprops=dict(arrowstyle="->", color="#111827"), fontsize=PT_INPLOT)
    axB_R.annotate("enhanced spread beyond conversion", xy=(22, 1.35), xytext=(5, 1.95), arrowprops=dict(arrowstyle="->", color="#111827"), fontsize=PT_INPLOT)
    add_caption(axB_R, "Marginal Ri: intermittent broadband activity indicates shear-mediated variability.")

    add_colorbar(fig, imBR, label="TL fluctuation intensity (arb.)", ax=[axB_L, axB_R], pad=0.02, shrink=0.92)

    # 3.6C on bottom-right: two subpanels
    gsC = GridSpec(nrows=1, ncols=2, wspace=0.15, figure=fig, left=0.56, right=0.98, bottom=0.08, top=0.52)
    axC_L = fig.add_subplot(gsC[0,0])
    axC_R = fig.add_subplot(gsC[0,1])

    # Left: coherent fraction vs Ri
    RiC = np.linspace(0.0, 2.0, 400)
    cf = synthetic_coherent_fraction(RiC)
    axC_L.set_xlim(0.0, 2.0)
    axC_L.set_xlabel("Ri")
    axC_L.set_ylim(0.0, 1.0)
    axC_L.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    axC_L.set_ylabel("coherent fraction")
    axC_L.plot(RiC, cf, color=COLOR_BLUE, linewidth=3.0)
    idx = (RiC >= 0.3) & (RiC <= 0.5)
    axC_L.fill_between(RiC[idx], np.clip(cf[idx]-0.06,0,1), np.clip(cf[idx]+0.06,0,1), color=COLOR_STEEL, alpha=0.20)
    axC_L.annotate("stable: high coherent fraction", xy=(1.7, 0.9), xytext=(1.1, 0.95), arrowprops=dict(arrowstyle="->"))
    axC_L.annotate("marginal: additional loss & variability", xy=(0.42, cf[(np.abs(RiC-0.42)).argmin()]), xytext=(0.75, 0.6), arrowprops=dict(arrowstyle="->"))
    add_caption(axC_L, "Coherent fraction declines monotonically with a superposed dip near marginal Ri.")

    # Right: PSD broadening
    wC = np.linspace(0.2, 2.2, 600)
    axC_R.set_xlim(0.2, 2.2)
    axC_R.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    axC_R.set_xlabel("ω/N")
    axC_R.set_ylim(0.0, 1.0)
    axC_R.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    axC_R.set_ylabel("normalized PSD")
    psd_n = synthetic_psd(wC, kind="narrow")
    psd_b = synthetic_psd(wC, kind="broad")
    axC_R.plot(wC, psd_n, color=COLOR_BLUE, linewidth=3.0, label="high Ri")
    axC_R.plot(wC, psd_b, color=COLOR_STEEL, linewidth=3.0, linestyle=(0, (6, 4)), label="marginal Ri")
    axC_R.legend(loc="upper right", frameon=False)
    # Bandwidth bars
    def hp_band(x, y):
        half = 0.5
        left = x[x < 1.0]
        right = x[x > 1.0]
        yl = y[x < 1.0]
        yr = y[x > 1.0]
        if len(left)==0 or len(right)==0: return None
        wl = left[np.argmin(np.abs(yl - half))]
        wr = right[np.argmin(np.abs(yr - half))]
        return wl, wr
    for curve, y0 in [(psd_n, 0.05), (psd_b, 0.12)]:
        hp = hp_band(wC, curve)
        if hp:
            wl, wr = hp
            axC_R.annotate("", xy=(wl, y0), xytext=(wr, y0), arrowprops=dict(arrowstyle="<->", color="#111827"))
            axC_R.text((wl+wr)/2, y0+0.06 if y0<0.1 else y0-0.06, "BW", ha="center")
    axC_R.text(1.55, 0.85, "broader PSD under marginal Ri")
    add_caption(axC_R, "Spectra broaden under marginal Ri, indicating enhanced shear-mediated variability.")

    # Overall figure title on the very top-left
    fig.suptitle("Figures 3.6A–C — Shared style suite", x=0.06, ha='left')

    save_figure(fig, "figure_3_6_combined")
    plt.close(fig)


if __name__ == "__main__":
    plot_combined()
