#!/usr/bin/env python3
import os
import math
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib import gridspec

# Global style and constants
DPI_EXPORT = 300
FIG_PX = (1800, 1200)
FIG_SIZE_IN = (FIG_PX[0] / DPI_EXPORT, FIG_PX[1] / DPI_EXPORT)

COLOR_DEEP_BLUE = "#1F78B4"
COLOR_STEEL_BLUE = "#457B9D"
COLOR_AMBER = "#F4A261"
COLOR_GRID = "#E5E7EB"
COLOR_CENTERLINE = "#9CA3AF"
COLOR_MAGENTA = "#B3007D"

CMAP_HEAT = "cividis_r"  # darker = higher (inverted)

# Typography
TITLE_SIZE = 28
LABEL_SIZE = 22
TICK_SIZE = 16
NOTE_SIZE = 18
NOTE_SIZE_BOLD = 20

# Line weights (in points)
AX_SPINE_LW = 2.0
CURVE_LW = 3.0
GRID_LW = 0.8
GUIDE_LW = 1.0


def configure_matplotlib():
    mpl.rcParams.update({
        "figure.dpi": DPI_EXPORT,
        "savefig.dpi": DPI_EXPORT,
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "mathtext.fontset": "dejavusans",
        "pdf.fonttype": 42,     # embed TrueType
        "ps.fonttype": 42,
        "svg.fonttype": "none",  # keep text as text
        "axes.grid": True,
        "grid.color": COLOR_GRID,
        "grid.linewidth": GRID_LW,
        "grid.alpha": 1.0,
        "axes.linewidth": AX_SPINE_LW,
        "axes.labelsize": LABEL_SIZE,
        "axes.titlesize": TITLE_SIZE,
        "xtick.labelsize": TICK_SIZE,
        "ytick.labelsize": TICK_SIZE,
        "lines.linewidth": CURVE_LW,
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
        "lines.dash_capstyle": "round",
    })


def set_spines(ax):
    for side in ["left", "right", "bottom", "top"]:
        ax.spines[side].set_linewidth(AX_SPINE_LW)


def add_conversion_band(ax, axis="x", band_min=0.8, band_max=1.2, dotted_at=1.0):
    if axis == "x":
        ax.axvspan(band_min, band_max, color=COLOR_AMBER, alpha=0.2, zorder=2)
        ax.axvline(dotted_at, color=COLOR_CENTERLINE, linestyle=":", linewidth=GUIDE_LW, zorder=3)
    else:
        ax.axhspan(band_min, band_max, color=COLOR_AMBER, alpha=0.2, zorder=2)
        ax.axhline(dotted_at, color=COLOR_CENTERLINE, linestyle=":", linewidth=GUIDE_LW, zorder=3)


def add_optional_marginal_guide(ax, ri_value=0.25):
    ax.axhline(ri_value, color=COLOR_CENTERLINE, linestyle="--", linewidth=GUIDE_LW)
    ax.text(0.995, ri_value + 0.03, "marginal stability", color=COLOR_CENTERLINE,
            ha="right", va="bottom", fontsize=NOTE_SIZE, transform=ax.get_yaxis_transform())


def finalize_axes(ax):
    set_spines(ax)
    ax.grid(True, which="major")


def save_all(fig, out_base):
    fig.savefig(out_base + ".png", dpi=DPI_EXPORT, bbox_inches="tight", facecolor="white")
    fig.savefig(out_base + ".pdf", bbox_inches="tight", facecolor="white")
    fig.savefig(out_base + ".svg", bbox_inches="tight", facecolor="white")


# -------------------- Figure 3.6A --------------------

def synth_sdi(Ri, W):
    # Ri: [0, 2], W: [0.2, 2.2]
    # Central horizontally-elongated island near (Ri ~ 0.4, W ~ 1)
    Ri0 = 0.40
    W0 = 1.0
    sigma_ri = 0.12
    sigma_w = 0.28

    island = np.exp(-((Ri - Ri0) ** 2) / (2 * sigma_ri ** 2)) * np.exp(-((W - W0) ** 2) / (2 * sigma_w ** 2))

    # Decay as Ri -> 1..2
    decay_ri = 1.0 / (1.0 + np.exp(4.0 * (Ri - 1.0)))

    # Decay for W >= 1.4
    decay_w = 1.0 / (1.0 + np.exp(12.0 * (W - 1.4)))

    # Weak tongue for W < 1 at very low Ri
    tongue = 0.25 * np.exp(-((W - 0.8) ** 2) / (2 * 0.08 ** 2)) * np.exp(-Ri / 0.08)

    sdi = island * decay_ri * decay_w + tongue

    # Fade extremes in Ri (top and bottom edges) with a smooth taper
    # Cosine taper near Ri=0 and Ri=2
    taper_bottom = 0.5 * (1 - np.cos(np.clip(Ri / 0.2, 0, 1) * np.pi))
    taper_top = 0.5 * (1 - np.cos(np.clip((2.0 - Ri) / 0.2, 0, 1) * np.pi))
    taper = np.minimum(1.0, np.minimum(taper_bottom, taper_top) + 0.85)  # keep center ~1, edges < 1
    sdi *= taper

    sdi = np.clip(sdi, 0.0, 1.0)
    return sdi


def figure_3_6A(output_dir: str):
    fig = plt.figure(figsize=FIG_SIZE_IN, constrained_layout=False)
    ax = fig.add_subplot(1, 1, 1)

    # Axes ranges and ticks
    x_min, x_max = 0.2, 2.2
    y_min, y_max = 0.0, 2.0
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.set_yticks([0.0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])

    ax.set_xlabel(r"$\omega/N$")
    ax.set_ylabel(r"$R_i$")

    # Grid major only
    finalize_axes(ax)

    # Data grid
    n_r, n_w = 600, 800
    Ri_vals = np.linspace(y_min, y_max, n_r)
    W_vals = np.linspace(x_min, x_max, n_w)
    Ri_grid, W_grid = np.meshgrid(Ri_vals, W_vals, indexing="ij")

    Z = synth_sdi(Ri_grid, W_grid)

    # Heatmap
    im = ax.imshow(
        Z,
        origin="lower",
        extent=(x_min, x_max, y_min, y_max),
        cmap=CMAP_HEAT,
        vmin=0.0,
        vmax=1.0,
        aspect="auto",
        interpolation="bilinear",
        zorder=1,
    )

    # Conversion window band and centerline (vertical)
    add_conversion_band(ax, axis="x", band_min=0.8, band_max=1.2, dotted_at=1.0)

    # Optional marginal stability guide at Ri=0.25
    add_optional_marginal_guide(ax, ri_value=0.25)

    # Title and caption inside the axes (top-left)
    ax.text(0.01, 0.98, r"Figure 3.6A — SDI($R_i$, $\omega/N$)",
            transform=ax.transAxes, ha="left", va="top", fontsize=TITLE_SIZE, fontweight="bold")

    ax.text(0.01, -0.18,
            "Darker regions: shear-mediated loss dominates; peak near $\\omega/N\\approx1$ under marginal $R_i$.",
            transform=ax.transAxes, ha="left", va="top", fontsize=NOTE_SIZE)

    # Colorbar on the right
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.06)
    cbar.set_label("Shear-dominance index (0–1)", fontsize=LABEL_SIZE)
    cbar.set_ticks([0.0, 0.25, 0.5, 0.75, 1.0])
    cbar.ax.tick_params(labelsize=TICK_SIZE)

    out_base = os.path.join(output_dir, "figure_3_6A")
    save_all(fig, out_base)
    plt.close(fig)


# -------------------- Figure 3.6B --------------------

def synth_timefreq_left(t, w):
    # Thin, nearly time-steady ridge confined to conversion band
    T, W = np.meshgrid(t, w, indexing="ij")

    center = 1.0 + 0.03 * np.sin(2 * np.pi * T / 60.0)
    sigma = 0.06
    ridge = np.exp(-((W - center) ** 2) / (2 * sigma ** 2))

    # Slight amplitude modulation
    amp = 0.7 + 0.1 * np.cos(2 * np.pi * T / 30.0)
    Z = amp * ridge

    # Very quiet background
    Z += 0.03 * np.exp(-((W - 1.3) ** 2) / (2 * 0.2 ** 2))
    Z = np.clip(Z, 0.0, 1.0)
    return Z


def synth_timefreq_right(t, w, rng):
    # Intermittent, dark bursts; broader frequency spread; some oblique streaks
    T, W = np.meshgrid(t, w, indexing="ij")

    Z = 0.05 * np.exp(-((W - 1.3) ** 2) / (2 * 0.3 ** 2))  # low background

    num_bursts = 7
    for _ in range(num_bursts):
        t0 = float(rng.uniform(5, 50))
        dt = float(rng.uniform(3, 10))
        w_center0 = float(rng.uniform(0.7, 1.1))
        w_slope = float(rng.uniform(-0.01, 0.01))  # oblique
        sigma_w = float(rng.uniform(0.10, 0.25))
        amp = float(rng.uniform(0.5, 0.95))

        w_center_time = w_center0 + w_slope * (T - t0)
        time_envelope = np.exp(-((T - t0) ** 2) / (2 * (0.35 * dt) ** 2))
        freq_envelope = np.exp(-((W - w_center_time) ** 2) / (2 * sigma_w ** 2))
        Z += amp * time_envelope * freq_envelope

    Z = np.clip(Z, 0.0, 1.0)
    return Z


def figure_3_6B(output_dir: str):
    fig = plt.figure(figsize=FIG_SIZE_IN, constrained_layout=False)
    gs = gridspec.GridSpec(nrows=1, ncols=3, width_ratios=[1, 1, 0.04], wspace=0.25)

    axL = fig.add_subplot(gs[0, 0])
    axR = fig.add_subplot(gs[0, 1], sharey=axL)
    cax = fig.add_subplot(gs[0, 2])

    # Axes ranges and ticks
    t_min, t_max = 0.0, 60.0
    w_min, w_max = 0.2, 2.2

    for ax in (axL, axR):
        ax.set_xlim(t_min, t_max)
        ax.set_ylim(w_min, w_max)
        ax.set_xticks(np.arange(0, 61, 10))
        ax.set_yticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
        ax.set_xlabel("t [s]")
        if ax is axL:
            ax.set_ylabel(r"$\omega/N$")
        finalize_axes(ax)

    # Data grids
    nt, nw = 500, 600
    t = np.linspace(t_min, t_max, nt)
    w = np.linspace(w_min, w_max, nw)

    rng = np.random.default_rng(7)
    ZL = synth_timefreq_left(t, w)
    ZR = synth_timefreq_right(t, w, rng)

    # Shared color limits
    vmax = max(ZL.max(), ZR.max())
    vmin = 0.0

    imL = axL.imshow(ZL, origin="lower", extent=(t_min, t_max, w_min, w_max), cmap=CMAP_HEAT,
                     vmin=vmin, vmax=vmax, aspect="auto", interpolation="bilinear", zorder=1)
    imR = axR.imshow(ZR, origin="lower", extent=(t_min, t_max, w_min, w_max), cmap=CMAP_HEAT,
                     vmin=vmin, vmax=vmax, aspect="auto", interpolation="bilinear", zorder=1)

    # Conversion band (horizontal) and centerline at 1.0
    for ax in (axL, axR):
        add_conversion_band(ax, axis="y", band_min=0.8, band_max=1.2, dotted_at=1.0)

    # Panel labels
    axL.text(0.02, 1.05, r"High $R_i$", transform=axL.transAxes, ha="left", va="bottom", fontsize=LABEL_SIZE, fontweight="bold")
    axR.text(0.02, 1.05, r"Marginal $R_i$", transform=axR.transAxes, ha="left", va="bottom", fontsize=LABEL_SIZE, fontweight="bold")

    # Micro-labels
    axL.text(0.02, 0.96, "narrow conversion-band modulation", transform=axL.transAxes,
             ha="left", va="top", fontsize=NOTE_SIZE)
    axR.text(0.02, 0.96, "intermittent broadband bursts", transform=axR.transAxes,
             ha="left", va="top", fontsize=NOTE_SIZE)
    axR.text(0.02, 0.90, "enhanced spread beyond conversion", transform=axR.transAxes,
             ha="left", va="top", fontsize=NOTE_SIZE)

    # Shared colorbar
    cbar = fig.colorbar(imR, cax=cax)
    cbar.set_label("TL fluctuation intensity (arb.)", fontsize=LABEL_SIZE)
    cbar.ax.tick_params(labelsize=TICK_SIZE)

    # Global header and caption
    fig.text(0.5, 0.98, r"Figure 3.6B — Time–frequency TL fluctuation intensity",
             ha="center", va="top", fontsize=TITLE_SIZE, fontweight="bold")

    # Caption inside below axes: place under left axes
    axL.text(0.01, -0.18,
             "High $R_i$: fluctuation energy confined to the conversion band. "
             "Marginal $R_i$: broadband, intermittent activity.",
             transform=axL.transAxes, ha="left", va="top", fontsize=NOTE_SIZE)

    out_base = os.path.join(output_dir, "figure_3_6B")
    save_all(fig, out_base)
    plt.close(fig)


# -------------------- Figure 3.6C --------------------

def figure_3_6C(output_dir: str):
    fig = plt.figure(figsize=FIG_SIZE_IN, constrained_layout=False)
    gs = gridspec.GridSpec(nrows=1, ncols=2, width_ratios=[1, 1], wspace=0.25)

    axL = fig.add_subplot(gs[0, 0])  # Coherent fraction vs Ri
    axR = fig.add_subplot(gs[0, 1])  # PSD broadening

    # Left subpanel: coherent fraction vs Ri
    x_min, x_max = 0.0, 2.0
    y_min, y_max = 0.0, 1.0

    axL.set_xlim(x_min, x_max)
    axL.set_ylim(y_min, y_max)

    axL.set_xticks([0.0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
    axL.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])

    axL.set_xlabel(r"$R_i$")
    axL.set_ylabel("coherent fraction")
    finalize_axes(axL)

    ri = np.linspace(x_min, x_max, 400)

    # Monotone decreasing baseline: ~0.5 at Ri~0.25 to ~0.95 at Ri=2
    baseline = 0.55 + 0.45 * (ri / 2.0) ** 0.8

    # Localized deeper notch around 0.3–0.5 down to ~0.4
    notch_center = 0.40
    notch = 0.18 * np.exp(-((ri - notch_center) ** 2) / (2 * 0.08 ** 2))
    coherent = np.clip(baseline - notch, 0.0, 1.0)

    axL.plot(ri, coherent, color=COLOR_DEEP_BLUE, label="coherent fraction")

    # Variability shading around the notch (steel-blue, ~20% opacity)
    variability_low = np.maximum(0.0, coherent - 0.08)
    variability_high = np.minimum(1.0, coherent + 0.03)
    mask = (ri >= 0.30) & (ri <= 0.50)
    axL.fill_between(ri[mask], variability_low[mask], variability_high[mask],
                     color=COLOR_STEEL_BLUE, alpha=0.20, edgecolor="none")

    # Micro-notes
    axL.text(1.98, 0.93, "stable: high coherent fraction", ha="right", va="top", fontsize=NOTE_SIZE)
    axL.text(0.02, 0.15, "marginal: extra loss & variability", ha="left", va="bottom", fontsize=NOTE_SIZE)

    # Right subpanel: PSD broadening
    fx_min, fx_max = 0.2, 2.2
    fy_min, fy_max = 0.0, 1.0

    axR.set_xlim(fx_min, fx_max)
    axR.set_ylim(fy_min, fy_max)

    axR.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    axR.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])

    axR.set_xlabel(r"$\omega/N$")
    axR.set_ylabel("normalized PSD")
    finalize_axes(axR)

    f = np.linspace(fx_min, fx_max, 600)

    # High Ri: narrow peak near 1
    peak_center = 1.0
    high_sigma = 0.09
    psd_high = np.exp(-((f - peak_center) ** 2) / (2 * high_sigma ** 2))
    psd_high /= psd_high.max()

    # Marginal Ri: broader peak/plateau
    low_sigma = 0.22
    psd_low = np.exp(-((f - peak_center) ** 2) / (2 * low_sigma ** 2))
    psd_low /= psd_low.max()

    # Plot curves
    axR.plot(f, psd_high, color=COLOR_DEEP_BLUE, label=r"High $R_i$")
    axR.plot(f, psd_low, color=COLOR_STEEL_BLUE, linestyle=(0, (6, 6)), label=r"Marginal $R_i$")

    # Amber band and dotted centerline
    add_conversion_band(axR, axis="x", band_min=0.8, band_max=1.2, dotted_at=1.0)

    # Optional bandwidth arrows (double-headed) under each peak
    # Place at y ~ 0.12
    bw_y = 0.12
    # Half-power bandwidth approximations (where curve ~ 0.5)
    def half_power_width(sigma):
        # For Gaussian: exp(-x^2/(2 sigma^2)) = 0.5 -> x = sigma * sqrt(2 ln 2)
        return math.sqrt(2 * math.log(2)) * sigma

    hpw_high = half_power_width(high_sigma)
    hpw_low = half_power_width(low_sigma)

    axR.annotate("BW", xy=(peak_center - hpw_high, bw_y), xytext=(peak_center + hpw_high, bw_y),
                 arrowprops=dict(arrowstyle="<->", color=COLOR_DEEP_BLUE, linewidth=GUIDE_LW),
                 ha="center", va="center", fontsize=NOTE_SIZE, color=COLOR_DEEP_BLUE)

    axR.annotate("BW", xy=(peak_center - hpw_low, bw_y - 0.05), xytext=(peak_center + hpw_low, bw_y - 0.05),
                 arrowprops=dict(arrowstyle="<->", color=COLOR_STEEL_BLUE, linewidth=GUIDE_LW),
                 ha="center", va="center", fontsize=NOTE_SIZE, color=COLOR_STEEL_BLUE)

    # Micro-note near dashed curve
    axR.text(1.55, 0.55, r"broader PSD under marginal $R_i$", fontsize=NOTE_SIZE)

    # Legend inside
    leg = axR.legend(loc="upper right", frameon=False, fontsize=NOTE_SIZE)

    # Global header and caption
    fig.text(0.5, 0.98, r"Figure 3.6C — Coherence loss and spectral broadening with decreasing $R_i$",
             ha="center", va="top", fontsize=TITLE_SIZE, fontweight="bold")

    # Caption inside, below axes: place under left axes
    axL.text(0.01, -0.18,
             "Coherent fraction drops with decreasing $R_i$ and shows a localized dip near marginal $R_i$; "
             "spectra broaden under marginal $R_i$.",
             transform=axL.transAxes, ha="left", va="top", fontsize=NOTE_SIZE)

    out_base = os.path.join(output_dir, "figure_3_6C")
    save_all(fig, out_base)
    plt.close(fig)


# -------------------- Main --------------------

def main():
    configure_matplotlib()

    out_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(out_dir, exist_ok=True)

    figure_3_6A(out_dir)
    figure_3_6B(out_dir)
    figure_3_6C(out_dir)

    print(f"Saved figures to: {out_dir}")


if __name__ == "__main__":
    main()
