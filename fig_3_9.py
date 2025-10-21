#!/usr/bin/env python3
import os
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# ---------- Shared house style ----------
CANVAS_PX = (2000, 1400)
EXPORT_DPI = 300
FIGSIZE_IN = (CANVAS_PX[0] / EXPORT_DPI, CANVAS_PX[1] / EXPORT_DPI)

# Colors
COLORS = {
    "classical": "#6B7280",        # dark gray
    "conversion": "#F4A261",       # amber
    "conversion_dark": "#C06A00",  # darker amber for lines where needed
    "interfacial": "#6A4C93",      # purple
    "shear": "#2A9D8F",           # teal
    "primary": "#1F78B4",         # deep blue
    "grid": "#E5E7EB",            # light gray grid
    "centerline": "#9CA3AF",      # faint dotted centerline
}


def px_to_pt(px: float, dpi: int = EXPORT_DPI) -> float:
    # Convert pixels to points for linewidths at a given export DPI
    return 72.0 * (px / dpi)


def set_house_style():
    plt.rcParams.update({
        # Fonts
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 16,  # base tick label size
        "axes.titlesize": 28,
        "axes.titleweight": "bold",
        "axes.labelsize": 22,
        "legend.fontsize": 16,
        # Lines & caps
        "lines.linewidth": px_to_pt(2.0),
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
        # Grid
        "axes.grid": True,
        "grid.color": COLORS["grid"],
        "grid.linestyle": "-",
        "grid.linewidth": px_to_pt(0.8),
        # PDF embedding
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    })


# ---------- Utilities ----------

def new_fig_ax(nrows=1, ncols=1, sharex=False, height_ratios=None):
    if nrows == 1 and ncols == 1:
        fig, ax = plt.subplots(figsize=FIGSIZE_IN, dpi=EXPORT_DPI)
        return fig, ax
    else:
        if height_ratios is not None:
            from matplotlib.gridspec import GridSpec
            fig = plt.figure(figsize=FIGSIZE_IN, dpi=EXPORT_DPI)
            gs = GridSpec(nrows, ncols, figure=fig, height_ratios=height_ratios)
            axes = []
            for r in range(nrows):
                row_axes = []
                for c in range(ncols):
                    row_axes.append(fig.add_subplot(gs[r, c], sharex=(axes[0][0] if sharex and axes else None)))
                axes.append(row_axes)
            return fig, np.array(axes, dtype=object)
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, sharex=sharex, figsize=FIGSIZE_IN, dpi=EXPORT_DPI)
        return fig, axes


def save_figure(fig: plt.Figure, name: str, outdir: str = "output"):
    os.makedirs(outdir, exist_ok=True)
    png_path = os.path.join(outdir, f"{name}.png")
    pdf_path = os.path.join(outdir, f"{name}.pdf")
    fig.savefig(png_path, dpi=EXPORT_DPI, facecolor="white", bbox_inches="tight")
    fig.savefig(pdf_path, dpi=EXPORT_DPI, facecolor="white", bbox_inches="tight")
    print(f"Saved {png_path} and {pdf_path}")


# ---------- Figure 3.9A ----------

def figure_3_9A():
    fig, ax = new_fig_ax()

    # Axes setup
    ax.set_facecolor("white")
    ax.set_xlim(0.2, 2.2)
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.set_xlabel("ω/N")
    ax.set_ylim(20, 80)
    ax.set_yticks(np.arange(20, 81, 10))
    ax.set_ylabel("TL (dB)")

    # Amber band 0.8–1.2 and dotted centerline at 1
    ax.axvspan(0.8, 1.2, color=COLORS["conversion"], alpha=0.20, zorder=0)
    ax.axvline(1.0, color=COLORS["centerline"], linestyle=(0, (px_to_pt(1), px_to_pt(3))), linewidth=px_to_pt(1.2))

    x = np.linspace(0.2, 2.2, 1500)

    # Classical baseline (gently rising)
    baseline = 45 + 8 * (x - 0.2) / (2.0)  # ~45 to ~53 dB

    # Continuous bump centered near 1, FWHM ~ 0.6, +6–8 dB
    fwhm = 0.6
    sigma = fwhm / (2 * math.sqrt(2 * math.log(2)))
    bump = 7.0 * np.exp(-0.5 * ((x - 1.0) / sigma) ** 2)

    y_continuous = baseline + bump

    # Continuous + interfaces: add narrow notches (4–6 dips)
    notch_centers = np.array([0.5, 0.75, 1.05, 1.32, 1.60])
    notch_depths = np.array([8, 10, 12, 9, 7])  # dB dips
    y_interfaces = y_continuous.copy()
    for c, d in zip(notch_centers, notch_depths):
        frac = 0.04  # 4% width
        notch_fwhm = frac * max(c, 0.5)
        notch_sigma = notch_fwhm / (2 * math.sqrt(2 * math.log(2)))
        y_interfaces -= d * np.exp(-0.5 * ((x - c) / notch_sigma) ** 2)

    # Plot
    ax.plot(x, baseline, linestyle=(0, (px_to_pt(8), px_to_pt(6))), color=COLORS["classical"],
            linewidth=px_to_pt(2.5), label="classical")
    ax.plot(x, y_continuous, color=COLORS["primary"], linewidth=px_to_pt(3.0), label="continuous")
    ax.plot(x, y_interfaces, color=COLORS["interfacial"], linewidth=px_to_pt(2.5), label="continuous + interfaces (notches)")

    # Double-headed arrow spanning two adjacent notches
    x0, x1 = notch_centers[1], notch_centers[2]
    y_arrow = 76
    ax.annotate("", xy=(x0, y_arrow), xytext=(x1, y_arrow),
                arrowprops=dict(arrowstyle="<->", color=COLORS["centerline"], linewidth=px_to_pt(1.2)))
    ax.text((x0 + x1) / 2, y_arrow + 1.5, "Δ(ω/N) ≈ const.",
            ha="center", va="bottom", fontsize=18, color=COLORS["centerline"]) 

    # Micro-labels
    ax.text(1.45, y_continuous[np.searchsorted(x, 1.45)] + 3, "conversion bump (continuous)",
            color=COLORS["primary"], fontsize=18)
    ax.text(1.15, y_interfaces[np.searchsorted(x, 1.15)] - 10, "interfacial comb (continuous + interfaces)",
            color=COLORS["interfacial"], fontsize=18)

    # Legend inside axes, frame off
    leg = ax.legend(frameon=False, loc="upper left")

    # Title and caption
    ax.set_title("Figure 3.9A — Frequency sweep signatures")
    fig.text(0.5, 0.02,
             ("Figure 3.9A. Frequency-sweep signatures: a broad conversion bump at ω/N≈1 "
              "for continuous stratification; adding sharp interfaces imposes narrow spectral notches on top of the bump."),
             ha="center", va="bottom", fontsize=15, style="italic")

    return fig


# ---------- Figure 3.9B ----------

def figure_3_9B():
    fig, ax = new_fig_ax()
    ax.set_facecolor("white")
    ax.set_xlim(0.2, 2.2)
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.set_xlabel("ω/N")
    ax.set_ylim(0, 80)
    ax.set_yticks([0, 15, 30, 45, 60, 75, 80])
    ax.set_ylabel("θ (deg)")

    # Grid configured by rcParams (major ticks only)

    # Data grid
    nx, ny = 900, 320
    x = np.linspace(0.2, 2.2, nx)
    theta = np.linspace(0, 80, ny)
    X, T = np.meshgrid(x, theta)

    # Base field: modest baseline bump near x=1 (angle-independent)
    sigma_band = 0.30
    base_bump = 0.6 * np.exp(-0.5 * ((X - 1.0) / sigma_band) ** 2)

    # Notch filaments that shift with angle (produce higher values = darker)
    Z = 0.15 * np.ones_like(X) + base_bump
    orders = [1, 2, 3, 4]
    for m in orders:
        # Inclined trajectory: center increases with angle
        center = 0.40 + 0.35 * m + (T / 80.0) * 0.24  # upward-right slant
        width = 0.035
        strength = 0.7 - 0.08 * (m - 1)
        Z += strength * np.exp(-0.5 * ((X - center) / width) ** 2)

    # Normalize to [0,1]
    Z = (Z - Z.min()) / (Z.max() - Z.min() + 1e-9)

    # Colormap: darker = higher
    cmap = plt.get_cmap("gray_r")
    im = ax.imshow(Z, origin="lower", aspect="auto",
                   extent=[0.2, 2.2, 0, 80], cmap=cmap, interpolation="bilinear")

    # Amber band 0.8–1.2 and dotted vertical centerline at 1.0
    ax.axvspan(0.8, 1.2, color=COLORS["conversion"], alpha=0.20)
    ax.axvline(1.0, color=COLORS["centerline"], linestyle=(0, (px_to_pt(1), px_to_pt(3))), linewidth=px_to_pt(1.2))

    # Ruler arrow indicating conversion band (angle-independent)
    ax.annotate("conversion band (angle-independent)", xy=(1.0, 72), xytext=(0.82, 72),
                ha="right", va="center",
                arrowprops=dict(arrowstyle="<-", color=COLORS["conversion_dark"], linewidth=px_to_pt(1.2)),
                fontsize=18, color=COLORS["conversion_dark"]) 

    # Annotate one filament
    ax.annotate("interface-induced notch shifts with θ", xy=(1.32, 45), xytext=(1.55, 58),
                arrowprops=dict(arrowstyle="->", color=COLORS["interfacial"], linewidth=px_to_pt(1.2)),
                fontsize=18, color=COLORS["interfacial"]) 

    # Colorbar at right (compact)
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.03)
    cbar.ax.set_ylabel("Notch depth (arb.)")

    ax.set_title("Figure 3.9B — Angle–frequency plate")
    fig.text(0.5, 0.02,
             ("Figure 3.9B. Angle–frequency plate: interface-induced notches shift with angle, while the conversion band remains "
              "centered at ω/N≈1."),
             ha="center", va="bottom", fontsize=15, style="italic")
    return fig


# ---------- Figure 3.9C ----------

def figure_3_9C():
    fig, axes = new_fig_ax(nrows=2, ncols=1, sharex=True)
    ax_top, ax_bottom = axes
    for ax in (ax_top, ax_bottom):
        ax.set_facecolor("white")
        ax.set_xlim(0, 60)
        ax.grid(True)

    # Shared x-axis
    ax_bottom.set_xlabel("time (s)")

    # Time base
    t = np.linspace(0, 60, 1200)

    # Bottom: Ri(t) on 0→2 (steel-blue)
    # Create baseline variability and several low-Ri bursts
    rng = np.random.default_rng(42)
    baseline = 1.0 + 0.25 * np.sin(2 * np.pi * t / 24.0) + 0.15 * np.sin(2 * np.pi * t / 9.0 + 0.7)
    Ri = np.clip(baseline + 0.06 * rng.normal(size=t.size), 0, 2)

    # Define low-Ri windows
    windows = [(8, 12), (22, 26), (34, 37), (48, 52)]

    # Draw translucent teal bands spanning both panels to align events
    for (t0, t1) in windows:
        for ax in (ax_top, ax_bottom):
            ax.axvspan(t0, t1, color=COLORS["shear"], alpha=0.15, zorder=0)

    ax_bottom.plot(t, Ri, color="#4A6FA5", linewidth=px_to_pt(2.5))  # steel-blue
    ax_bottom.set_ylim(0, 2)
    ax_bottom.set_yticks([0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
    ax_bottom.set_ylabel("Rᵢ(t)")

    # Top: coherence gamma^2(t) (0→1), deep-blue line with persistent dip near when band at w/N≈1 is excited
    gamma2 = 0.94 + 0.03 * np.sin(2 * np.pi * t / 30.0)

    # Persistent dip region (e.g., 18–28 s) + sharp drops aligned with low-Ri bursts
    gamma2 -= 0.06 * np.exp(-0.5 * ((t - 23) / 4.0) ** 2)
    for (t0, t1) in windows:
        center = 0.5 * (t0 + t1)
        width = 0.45 * (t1 - t0)
        gamma2 -= 0.08 * np.exp(-0.5 * ((t - center) / width) ** 2)

    gamma2 = np.clip(gamma2, 0, 1)

    ax_top.plot(t, gamma2, color=COLORS["primary"], linewidth=px_to_pt(3.0))
    ax_top.set_ylim(0, 1)
    ax_top.set_ylabel("γ²(t) (band near ω/N ≈ 1)")

    # Vertical faint gray guides aligning minima to low-Ri windows
    for (t0, t1) in windows:
        ax_top.axvline(0.5 * (t0 + t1), color=COLORS["grid"], linestyle=(0, (px_to_pt(1), px_to_pt(4))), linewidth=px_to_pt(1.0))

    # Micro-labels
    ax_top.text(14.5, 0.80, "conversion-band dip", color=COLORS["primary"], fontsize=18)
    ax_bottom.text(9.0, 0.2, "low-Rᵢ burst", color=COLORS["shear"], fontsize=18)

    # Title and caption
    ax_top.set_title("Figure 3.9C — Time correlation")
    fig.text(0.5, 0.02,
             ("Figure 3.9C. Time correlation between array coherence and Rᵢ(t): a persistent conversion-band dip plus "
              "intermittent losses coincident with low-Rᵢ bursts."),
             ha="center", va="bottom", fontsize=15, style="italic")

    # Gutter between panels (approx 40 px at 300 dpi ≈ 0.133 in). Adjust layout
    fig.subplots_adjust(hspace=0.22)

    return fig


# ---------- Figure 3.9D ----------

def figure_3_9D():
    fig, ax = new_fig_ax()
    ax.set_facecolor("white")

    categories = [
        "High-Rᵢ continuous",
        "Marginal-Rᵢ continuous",
        "Layered sharp",
        "Layered diffuse",
    ]

    # Shares (must sum to 1 per column)
    # Order bottom→top: Classical (gray), Conversion (amber), Interfacial (purple), Shear (teal)
    shares = [
        {"Classical": 0.40, "Conversion": 0.48, "Interfacial": 0.06, "Shear": 0.06},
        {"Classical": 0.30, "Conversion": 0.38, "Interfacial": 0.02, "Shear": 0.30},
        {"Classical": 0.24, "Conversion": 0.20, "Interfacial": 0.52, "Shear": 0.04},
        {"Classical": 0.42, "Conversion": 0.33, "Interfacial": 0.15, "Shear": 0.10},
    ]

    colors = {
        "Classical": COLORS["classical"],
        "Conversion": COLORS["conversion"],
        "Interfacial": COLORS["interfacial"],
        "Shear": COLORS["shear"],
    }

    x = np.arange(len(categories))
    width = 0.6

    bottoms = np.zeros(len(categories))
    label_order = ["Classical", "Conversion", "Interfacial", "Shear"]

    for label in label_order:
        vals = np.array([col[label] for col in shares])
        ax.bar(x, vals, width, bottom=bottoms, color=colors[label], edgecolor="none", label=label)
        # in-band numeric labels if space
        for xi, v, b in zip(x, vals, bottoms):
            if v >= 0.08:
                ax.text(xi, b + v / 2.0, f"{v:.2f}", ha="center", va="center", fontsize=16, color="white")
        bottoms += vals

    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=0)
    ax.set_xlim(-0.5, len(categories) - 0.5)
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_ylabel("Share")

    # Legend if needed (compact)
    leg = ax.legend(frameon=False, loc="upper right")

    # Header and caption
    ax.set_title("Figure 3.9D — Mechanism-share waterfall (four canonical regimes)")
    fig.text(0.5, 0.02,
             ("Figure 3.9D. Mechanism shares (summing to unity) for four regimes: conversion dominates high-Rᵢ continuous; "
              "shear rises under marginal Rᵢ; interfacial loss peaks for layered sharp and weakens for layered diffuse."),
             ha="center", va="bottom", fontsize=15, style="italic")

    return fig


# ---------- Main ----------

def main():
    set_house_style()

    figA = figure_3_9A()
    save_figure(figA, "figure_3_9A")
    plt.close(figA)

    figB = figure_3_9B()
    save_figure(figB, "figure_3_9B")
    plt.close(figB)

    figC = figure_3_9C()
    save_figure(figC, "figure_3_9C")
    plt.close(figC)

    figD = figure_3_9D()
    save_figure(figD, "figure_3_9D")
    plt.close(figD)


if __name__ == "__main__":
    main()
