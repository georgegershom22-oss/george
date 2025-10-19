#!/usr/bin/env python3
import argparse
import os
from dataclasses import dataclass
from typing import Iterable, List

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


# -----------------------------
# Global style configuration
# -----------------------------

def apply_global_style() -> None:
    mpl.rcParams.update({
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "black",
        "axes.linewidth": 2.0,  # axes 2 px
        "lines.linewidth": 3.0,  # curves 3 px
        "grid.color": "#E5E7EB",  # light gray
        "grid.linewidth": 0.8,  # 0.8 px
        "grid.alpha": 1.0,
        "xtick.color": "black",
        "ytick.color": "black",
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        # Typography
        "axes.titlesize": 28,
        "axes.titleweight": "bold",
        "axes.labelsize": 22,
        "xtick.labelsize": 16,
        "ytick.labelsize": 16,
        # PDF/SVG font embedding settings
        "pdf.fonttype": 42,  # TrueType, keep text selectable in PDF
        "svg.fonttype": "none",  # keep text as text in SVG
        # Legend
        "legend.frameon": False,
        # Dashes
        "lines.dash_capstyle": "round",
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
    })


# -----------------------------
# Shared constants / helpers
# -----------------------------

CB_DEEP_BLUE = "#1F78B4"
CB_STEEL_BLUE = "#457B9D"
CB_AMBER = "#F4A261"
GRID_COLOR = "#E5E7EB"
CENTERLINE_COLOR = "#9CA3AF"
OPTIONAL_MAGENTA = "#B3007D"

DEFAULT_CMAP = "cividis_r"  # darker = higher


@dataclass
class ExportSpec:
    output_dir: str
    formats: List[str]
    dpi: int


def ensure_output_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def save_figure(fig: mpl.figure.Figure, base_name: str, spec: ExportSpec) -> None:
    for fmt in spec.formats:
        out_path = os.path.join(spec.output_dir, f"{base_name}.{fmt}")
        if fmt.lower() == "png":
            fig.savefig(out_path, dpi=spec.dpi, bbox_inches="tight")
        else:
            fig.savefig(out_path, bbox_inches="tight")
        print(f"Saved: {out_path}")


# -----------------------------
# Utility drawing primitives
# -----------------------------


def add_conversion_band_on_x(ax: mpl.axes.Axes, x_min: float = 0.8, x_max: float = 1.2) -> None:
    ax.add_patch(
        Rectangle(
            (x_min, ax.get_ylim()[0]),
            x_max - x_min,
            ax.get_ylim()[1] - ax.get_ylim()[0],
            facecolor=CB_AMBER,
            alpha=0.20,
            zorder=0,
            lw=0,
        )
    )
    ax.axvline(1.0, color=CENTERLINE_COLOR, lw=1.0, ls=(0, (2, 3)))


def add_conversion_band_on_y(ax: mpl.axes.Axes, y_min: float = 0.8, y_max: float = 1.2) -> None:
    ax.add_patch(
        Rectangle(
            (ax.get_xlim()[0], y_min),
            ax.get_xlim()[1] - ax.get_xlim()[0],
            y_max - y_min,
            facecolor=CB_AMBER,
            alpha=0.20,
            zorder=0,
            lw=0,
        )
    )
    ax.axhline(1.0, color=CENTERLINE_COLOR, lw=1.0, ls=(0, (2, 3)))


# -----------------------------
# Figure 3.6A — SDI(Ri, ω/N)
# -----------------------------


def generate_sdi_field(ri: np.ndarray, omega_ratio: np.ndarray) -> np.ndarray:
    # Create 2D grid
    X, Y = np.meshgrid(omega_ratio, ri)

    # Base horizontally-elongated island centered at (Ri≈0.4, ω/N≈1)
    sigma_x = 0.25
    sigma_y = 0.12
    island = np.exp(-((X - 1.0) ** 2) / (2 * sigma_x**2) - ((Y - 0.4) ** 2) / (2 * sigma_y**2))

    # Additional decay for ω/N beyond ~1.4
    high_freq_decay = 1.0 / (1.0 + np.exp((X - 1.4) / 0.05))

    # Weak shear-driven tongue at very low Ri when ω/N < 1
    tongue_center = 0.8
    tongue_width_x = 0.12
    tongue_strength = 0.45
    tongue = tongue_strength * np.exp(-((X - tongue_center) ** 2) / (2 * tongue_width_x**2)) * np.exp(-(Y) / 0.15)

    # Fade at top/bottom edges in Ri for smoothness
    def logistic(u: np.ndarray, s: float = 0.06) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-u / s))

    low_ri_taper = logistic(Y - 0.04)
    high_ri_taper = logistic((2.0 - Y) - 0.04)
    ri_taper = low_ri_taper * high_ri_taper

    Z = (1.10 * island + tongue) * high_freq_decay

    # Gentle suppression of large Ri (Ri→1–2) to enforce decay with Ri
    ri_decay = 1.0 / (1.0 + np.exp((Y - 0.9) / 0.20))
    Z *= ri_decay

    # Apply Ri taper for smooth boundaries
    Z *= ri_taper

    # Normalize 0–1
    Z -= Z.min()
    if Z.max() > 0:
        Z /= Z.max()
    return Z


def figure_36A(spec: ExportSpec, cmap: str = DEFAULT_CMAP) -> None:
    # Canvas size: 1800x1200 px at 300 dpi => 6x4 in
    fig, ax = plt.subplots(figsize=(6, 4), constrained_layout=False)

    # Axes ranges
    x_ticks = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
    y_ticks = [0.0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0]
    x_min, x_max = 0.2, 2.2
    y_min, y_max = 0.0, 2.0

    # Data grid
    x = np.linspace(x_min, x_max, 500)
    y = np.linspace(y_min, y_max, 400)
    Z = generate_sdi_field(y, x)

    im = ax.imshow(
        Z,
        extent=[x_min, x_max, y_min, y_max],
        origin="lower",
        aspect="auto",
        cmap=cmap,
        vmin=0.0,
        vmax=1.0,
        interpolation="bilinear",
        zorder=1,
    )

    # Grid and bands
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)
    ax.grid(True, which="major")
    add_conversion_band_on_x(ax, 0.8, 1.2)

    # Optional dashed guide at Ri=0.25
    ax.axhline(0.25, color=CENTERLINE_COLOR, lw=1.2, ls=(0, (6, 4)))
    ax.text(
        2.22,
        0.25,
        "marginal stability",
        va="center",
        ha="right",
        fontsize=18,
        color="black",
        backgroundcolor=(1, 1, 1, 0.75),
    )

    # Labels and title
    ax.set_xlabel(r"$\omega/N$")
    ax.set_ylabel(r"$R_i$")
    ax.set_title(r"Figure 3.6A — SDI($R_i$, $\omega/N$)", loc="left", pad=10)

    # Caption inside, below axis
    ax.text(
        0.5,
        -0.17,
        "Darker regions: shear-mediated loss dominates; peak near $\\omega/N\\approx1$ under marginal $R_i$.",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=18,
    )

    # Colorbar on right
    cbar = fig.colorbar(im, ax=ax, pad=0.02)
    cbar.set_label("Shear-dominance index (0–1)", fontsize=20)
    cbar.set_ticks([0.0, 0.25, 0.5, 0.75, 1.0])

    save_figure(fig, "figure_3_6A", spec)
    plt.close(fig)


# ------------------------------------------
# Figure 3.6B — Time–frequency TL fluctuation
# ------------------------------------------


def synth_tl_high_ri(time_s: np.ndarray, omega_ratio: np.ndarray) -> np.ndarray:
    T, F = np.meshgrid(time_s, omega_ratio, indexing="ij")

    # Narrow ridge near ω/N ≈ 1, nearly time-steady
    center_f = 1.0 + 0.03 * np.sin(2 * np.pi * T / 60.0)
    sigma_f = 0.06
    ridge = np.exp(-((F - center_f) ** 2) / (2 * sigma_f**2))

    # Very low background
    background = 0.03 * np.exp(-((F - 1.0) ** 2) / (2 * 0.35**2))

    Z = 1.1 * ridge + background
    Z -= Z.min()
    if Z.max() > 0:
        Z /= Z.max()
    return Z


def synth_tl_marginal_ri(time_s: np.ndarray, omega_ratio: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    T, F = np.meshgrid(time_s, omega_ratio, indexing="ij")

    Z = np.zeros_like(T)

    # Intermittent bursts: random times, variable center frequencies and widths
    num_bursts = 9
    for _ in range(num_bursts):
        t0 = rng.uniform(5, 55)
        dt = rng.uniform(3, 8)
        f0 = rng.uniform(0.7, 1.5)
        sigma_f = rng.uniform(0.10, 0.22)
        amplitude = rng.uniform(0.6, 1.0)
        # Some oblique streaks: introduce slight time-dependent frequency drift
        drift = rng.uniform(-0.015, 0.015)
        f_center_t = f0 + drift * (T - t0)
        burst = amplitude * np.exp(-((T - t0) ** 2) / (2 * (dt**2))) * np.exp(-((F - f_center_t) ** 2) / (2 * sigma_f**2))
        Z = np.maximum(Z, burst)

    # Low-level broadband floor
    Z += 0.05 * rng.random(Z.shape)

    # Normalize
    Z -= Z.min()
    if Z.max() > 0:
        Z /= Z.max()
    return Z


def figure_36B(spec: ExportSpec, cmap: str = DEFAULT_CMAP, seed: int = 7) -> None:
    # Canvas size: 1800x1200 px at 300 dpi => 6x4 in
    fig = plt.figure(figsize=(6, 4), constrained_layout=False)
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 0.045], wspace=0.10)

    ax_left = fig.add_subplot(gs[0, 0])
    ax_right = fig.add_subplot(gs[0, 1], sharey=ax_left)
    cax = fig.add_subplot(gs[0, 2])

    # Axes setup
    t = np.linspace(0, 60, 600)
    fmin, fmax = 0.2, 2.2
    f = np.linspace(fmin, fmax, 400)

    rng = np.random.default_rng(seed)
    Z_left = synth_tl_high_ri(t, f)
    Z_right = synth_tl_marginal_ri(t, f, rng)

    vmin = 0.0
    vmax = max(Z_left.max(), Z_right.max())

    im_left = ax_left.imshow(
        Z_left.T,
        extent=[t.min(), t.max(), fmin, fmax],
        origin="lower",
        aspect="auto",
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        interpolation="bilinear",
        zorder=1,
    )

    im_right = ax_right.imshow(
        Z_right.T,
        extent=[t.min(), t.max(), fmin, fmax],
        origin="lower",
        aspect="auto",
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        interpolation="bilinear",
        zorder=1,
    )

    # Shared y-axis and identical frequency ticks
    y_ticks = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0]
    for ax in (ax_left, ax_right):
        ax.set_ylim(fmin, fmax)
        ax.set_yticks(y_ticks)
        ax.grid(True, which="major")
        ax.set_xlabel("t (s)")
        add_conversion_band_on_y(ax, 0.8, 1.2)

    ax_left.set_ylabel(r"$\omega/N$")

    # Titles & micro-labels
    fig.suptitle("Figure 3.6B — Time–frequency TL fluctuation intensity", x=0.06, y=0.995, ha="left")
    ax_left.text(0.5, 1.02, "High $R_i$", transform=ax_left.transAxes, ha="center", va="bottom", fontsize=20)
    ax_right.text(0.5, 1.02, "Marginal $R_i$", transform=ax_right.transAxes, ha="center", va="bottom", fontsize=20)

    ax_left.text(0.02, 0.96, "narrow conversion-band modulation", transform=ax_left.transAxes, ha="left", va="top", fontsize=18)
    ax_right.text(0.02, 0.96, "intermittent broadband bursts", transform=ax_right.transAxes, ha="left", va="top", fontsize=18)
    ax_right.text(0.02, 0.90, "enhanced spread beyond conversion", transform=ax_right.transAxes, ha="left", va="top", fontsize=18)

    # X ticks every 10 s
    x_ticks = list(range(0, 61, 10))
    for ax in (ax_left, ax_right):
        ax.set_xlim(0, 60)
        ax.set_xticks(x_ticks)

    # Shared colorbar on far right
    cbar = fig.colorbar(im_right, cax=cax)
    cbar.set_label("TL fluctuation intensity (arb.)", fontsize=20)

    # Caption inside, below axes
    ax_left.text(
        1.00,
        -0.20,
        "High $R_i$: fluctuation energy confined to the conversion band. Marginal $R_i$: broadband, intermittent activity.",
        transform=ax_right.transAxes,
        ha="right",
        va="top",
        fontsize=18,
    )

    save_figure(fig, "figure_3_6B", spec)
    plt.close(fig)


# ---------------------------------------------------------------
# Figure 3.6C — Coherence vs Ri; PSD broadening (High vs Marginal)
# ---------------------------------------------------------------


def synth_coherent_fraction(ri: np.ndarray) -> np.ndarray:
    # Monotone decreasing from ~0.95 at Ri=2 to ~0.5 at Ri≈0.25
    # Use a smooth logistic-like curve plus a localized notch near Ri≈0.3–0.5
    base = 0.45 + 0.5 / (1.0 + np.exp(-(ri - 0.8) / 0.35))  # ~0.5 at low Ri, ~0.95 at high Ri

    # Local notch centered ~0.38 with width ~0.12
    notch_center = 0.38
    notch_width = 0.12
    notch_depth = 0.12  # dip to ~0.4
    notch = notch_depth * np.exp(-((ri - notch_center) ** 2) / (2 * notch_width**2))

    cf = base - notch
    cf = np.clip(cf, 0.0, 1.0)
    return cf


def synth_psd_curves(omega_ratio: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # High Ri: deep-blue solid, narrow peak near ω/N ≈ 1
    high_center = 1.0
    high_sigma = 0.10
    psd_high = np.exp(-((omega_ratio - high_center) ** 2) / (2 * high_sigma**2))

    # Marginal Ri: steel-blue dashed, broader peak/plateau
    marg_sigma = 0.24
    psd_marg = np.exp(-((omega_ratio - high_center) ** 2) / (2 * marg_sigma**2))

    # Normalize both to max=1 for clean comparison
    psd_high /= psd_high.max()
    psd_marg /= psd_marg.max()
    return psd_high, psd_marg


def figure_36C(spec: ExportSpec) -> None:
    # Canvas size: 1800x1200 px at 300 dpi => 6x4 in
    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(6, 4), sharey=False, gridspec_kw={"wspace": 0.22})

    # Left: Coherent fraction vs Ri
    ri = np.linspace(0.0, 2.0, 600)
    cf = synth_coherent_fraction(ri)

    ax_l.plot(ri, cf, color=CB_DEEP_BLUE)

    # Shade variability region around the notch (Ri ≈ 0.3–0.5)
    shade_min, shade_max = 0.30, 0.50
    ax_l.axvspan(shade_min, shade_max, color=CB_STEEL_BLUE, alpha=0.20, lw=0)

    ax_l.set_xlim(0.0, 2.0)
    ax_l.set_ylim(0.0, 1.0)
    ax_l.set_xticks([0, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0])
    ax_l.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax_l.grid(True, which="major")
    ax_l.set_xlabel(r"$R_i$")
    ax_l.set_ylabel("coherent fraction")

    ax_l.text(0.02, 0.95, "stable: high coherent fraction", transform=ax_l.transAxes, va="top", fontsize=18)
    ax_l.text(0.02, 0.88, "marginal: extra loss & variability", transform=ax_l.transAxes, va="top", fontsize=18)

    # Right: PSD broadening (High vs Marginal)
    x_min, x_max = 0.2, 2.2
    omega_ratio = np.linspace(x_min, x_max, 800)
    psd_high, psd_marg = synth_psd_curves(omega_ratio)

    ax_r.plot(omega_ratio, psd_high, color=CB_DEEP_BLUE, lw=3.0, label="High $R_i$")
    ax_r.plot(omega_ratio, psd_marg, color=CB_STEEL_BLUE, lw=3.0, ls=(0, (6, 4)), label="Marginal $R_i$")

    ax_r.set_xlim(x_min, x_max)
    ax_r.set_ylim(0.0, 1.0)
    ax_r.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax_r.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax_r.grid(True, which="major")
    ax_r.set_xlabel(r"$\omega/N$")

    # Amber band 0.8–1.2 and dotted centerline at 1.0
    add_conversion_band_on_x(ax_r, 0.8, 1.2)

    # Optional bandwidth arrows under peaks
    # Compute approximate half-power widths
    def half_power_bandwidth(x: np.ndarray, y: np.ndarray, level: float = 0.5) -> tuple[float, float]:
        target = level * y.max()
        above = y >= target
        if not np.any(above):
            return (np.nan, np.nan)
        idx = np.where(above)[0]
        return (x[idx[0]], x[idx[-1]])

    hp_l, hp_r = half_power_bandwidth(omega_ratio, psd_high)
    mp_l, mp_r = half_power_bandwidth(omega_ratio, psd_marg)

    y_arrow = -0.08
    ax_r.annotate(
        "",
        xy=(hp_l, y_arrow),
        xytext=(hp_r, y_arrow),
        xycoords=("data", "axes fraction"),
        textcoords=("data", "axes fraction"),
        arrowprops=dict(arrowstyle="<->", color=CB_DEEP_BLUE, lw=2.0),
    )
    ax_r.text((hp_l + hp_r) / 2, y_arrow - 0.03, "BW", color=CB_DEEP_BLUE, ha="center", va="top", transform=ax_r.get_xaxis_transform(), fontsize=16)

    ax_r.annotate(
        "",
        xy=(mp_l, y_arrow - 0.12),
        xytext=(mp_r, y_arrow - 0.12),
        xycoords=("data", "axes fraction"),
        textcoords=("data", "axes fraction"),
        arrowprops=dict(arrowstyle="<->", color=CB_STEEL_BLUE, lw=2.0),
    )
    ax_r.text((mp_l + mp_r) / 2, y_arrow - 0.15, "BW", color=CB_STEEL_BLUE, ha="center", va="top", transform=ax_r.get_xaxis_transform(), fontsize=16)

    # Legend inside right subpanel
    ax_r.legend(loc="upper right", fontsize=16, frameon=False)

    # Header above both
    fig.suptitle("Figure 3.6C — Coherence loss and spectral broadening with decreasing $R_i$", x=0.06, y=0.995, ha="left")

    # Caption inside, below axes (anchored to right subplot)
    ax_r.text(
        1.00,
        -0.22,
        "Coherent fraction drops with decreasing $R_i$ and shows a localized dip near marginal $R_i$; spectra broaden under marginal $R_i$.",
        transform=ax_r.transAxes,
        ha="right",
        va="top",
        fontsize=18,
    )

    save_figure(fig, "figure_3_6C", spec)
    plt.close(fig)


# -----------------------------
# CLI
# -----------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Figures 3.6A–C with Matplotlib.")
    parser.add_argument("--figure", "-f", default="all", choices=["A", "B", "C", "all"], help="Which figure to generate")
    parser.add_argument("--out", "-o", default=os.path.join(os.path.dirname(__file__), "..", "figures"), help="Output directory for exported figures")
    parser.add_argument("--formats", "-F", nargs="+", default=["png", "pdf", "svg"], help="Output formats, e.g. png pdf svg")
    parser.add_argument("--dpi", type=int, default=300, help="DPI for PNG exports")
    parser.add_argument("--cmap", default=DEFAULT_CMAP, help="Matplotlib colormap (default: cividis_r; darker = higher)")
    parser.add_argument("--seed", type=int, default=7, help="RNG seed for synthetic data")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    apply_global_style()

    export_dir = os.path.abspath(args.out)
    ensure_output_dir(export_dir)

    spec = ExportSpec(output_dir=export_dir, formats=args.formats, dpi=args.dpi)

    if args.figure in ("A", "all"):
        figure_36A(spec, cmap=args.cmap)
    if args.figure in ("B", "all"):
        figure_36B(spec, cmap=args.cmap, seed=args.seed)
    if args.figure in ("C", "all"):
        figure_36C(spec)


if __name__ == "__main__":
    main()
