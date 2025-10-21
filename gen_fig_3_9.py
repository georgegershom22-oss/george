#!/usr/bin/env python3
import os
import math
import argparse
import numpy as np
import matplotlib
# Use a headless backend for server environments and ensure PDF/PNG output works
matplotlib.use('Agg', force=True)
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

# Ensure we use our local style
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STYLE_PATH = os.path.join(SCRIPT_DIR, 'figs', 'house_style.mplstyle')
if os.path.exists(STYLE_PATH):
    plt.style.use(STYLE_PATH)

# Palette
COLORS = {
    'classical': '#6B7280',  # dark gray
    'mode_conv_fill': '#F4A261',  # amber (fill)
    'mode_conv_line': '#C06A00',  # darker amber for lines if needed
    'interfacial': '#6A4C93',  # purple
    'shear': '#2A9D8F',        # teal
    'primary_data': '#1F78B4', # deep blue
    'centerline': '#9CA3AF',   # faint gray for dotted centerline
}

AMBER_BAND_ALPHA = 0.20  # 18–22%

# Canvas target size: 2000x1400 px at 300 dpi -> inches
WIDTH_IN = 2000 / 300.0
HEIGHT_IN = 1400 / 300.0
PT_PER_PX = 72.0 / 300.0  # 0.24 pt per pixel at 300 dpi


def _new_figure(nrows=1, ncols=1, sharex=False, sharey=False, gridspec_kw=None):
    fig, axes = plt.subplots(
        nrows=nrows, ncols=ncols, sharex=sharex, sharey=sharey,
        figsize=(WIDTH_IN, HEIGHT_IN), gridspec_kw=gridspec_kw
    )
    # Leave space at bottom for caption inside canvas
    fig.subplots_adjust(bottom=0.18, left=0.12, right=0.98, top=0.92, hspace=0.25)
    return fig, axes


def _add_caption(fig, text):
    fig.text(0.5, 0.04, text, ha='center', va='center', fontsize=15, style='italic')


def _apply_common_axes_styling(ax):
    # Ensure only major grid lines (style handles this). Make ticks outward for clarity.
    ax.tick_params(axis='both', which='major', direction='out', length=6, width=1)


def _add_conversion_band(ax):
    ax.axvspan(0.8, 1.2, color=COLORS['mode_conv_fill'], alpha=AMBER_BAND_ALPHA, linewidth=0)
    # Dotted guide 1.2 px -> 0.288 pt; custom dot-gap in px converted to pt
    ax.axvline(1.0, color=COLORS['centerline'], linestyle=(0, (PT_PER_PX, PT_PER_PX * 4.0)), linewidth=1.2 * PT_PER_PX)


def fig_3_9A(out_dir):
    fig, ax = _new_figure()

    # Axes setup
    x = np.linspace(0.2, 2.2, 1600)
    ax.set_xlim(0.2, 2.2)
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    # Use non-math label to avoid mathtext parsing issues in headless environments
    ax.set_xlabel("ω/N")

    ax.set_ylabel('TL (dB)')
    ax.set_ylim(20, 80)
    ax.set_yticks(np.arange(20, 81, 10))
    ax.set_title('Figure 3.9A — Frequency sweep signatures')

    _apply_common_axes_styling(ax)
    _add_conversion_band(ax)

    # Classical baseline: gently rising
    baseline = 38.0 + 10.0 * (x - 0.2) / (2.2 - 0.2)
    classical_line, = ax.plot(
        x, baseline,
        color=COLORS['classical'],
        linewidth=2.5 * PT_PER_PX,  # 2.5 px
        dashes=(8 * PT_PER_PX, 6 * PT_PER_PX),  # 8–6 px pattern
        label='classical'
    )

    # Continuous stratification bump: Gaussian on top of baseline
    fwhm = 0.6
    sigma = fwhm / (2 * math.sqrt(2 * math.log(2)))
    bump = 7.0 * np.exp(-0.5 * ((x - 1.0) / sigma) ** 2)
    continuous = baseline + bump
    cont_line, = ax.plot(
        x, continuous,
        color=COLORS['primary_data'], linewidth=3.0 * PT_PER_PX, label='continuous'
    )

    # Continuous + interfaces: add narrow notches (4–6 dips across 0.4–1.8)
    notch_centers = np.array([0.45, 0.65, 0.88, 1.15, 1.45, 1.75])
    notch_depths = np.array([8, 10, 12, 9, 7, 6])  # dB dips (6–12 dB)
    # 3–5% wide relative to center -> convert to sigma in x
    rel_fwhm = np.array([0.035, 0.035, 0.04, 0.04, 0.045, 0.05])
    notch_sigma = (rel_fwhm / (2 * math.sqrt(2 * math.log(2)))) * notch_centers

    dips = np.zeros_like(x)
    for c, d, s in zip(notch_centers, notch_depths, notch_sigma):
        dips += d * np.exp(-0.5 * ((x - c) / s) ** 2)

    cont_interfaces = continuous - dips
    cont_interfaces = np.clip(cont_interfaces, 20, None)
    inter_line, = ax.plot(
        x, cont_interfaces,
        color=COLORS['interfacial'], linewidth=3.0 * PT_PER_PX, label='continuous + interfaces (notches)'
    )

    # Micro-labels
    ax.annotate('conversion bump (continuous)',
                xy=(1.0, baseline[np.argmin(np.abs(x-1.0))] + 6.2), xycoords='data',
                xytext=(1.35, 70), textcoords='data', fontsize=19,
                arrowprops=dict(arrowstyle='->', color=COLORS['primary_data']))

    # Identify two adjacent notches for the double-headed arrow (e.g., near 0.88 and 1.15)
    n1, n2 = 0.88, 1.15
    y_arrow = 46
    ax.annotate("Δ(ω/N) ≈ const.",
                xy=(n1, y_arrow), xytext=(n2, y_arrow), fontsize=18,
                arrowprops=dict(arrowstyle='<->', color=COLORS['centerline']))

    ax.annotate('interfacial comb (continuous + interfaces)',
                xy=(1.45, cont_interfaces[np.argmin(np.abs(x-1.45))] - 6),
                xytext=(1.55, 32), fontsize=19,
                arrowprops=dict(arrowstyle='->', color=COLORS['interfacial']))

    # Legend inside axes
    ax.legend(loc='upper left')

    # Caption
    _add_caption(fig, (
        'Figure 3.9A. Frequency-sweep signatures: a broad conversion bump at '
        'ω/N≈1 for continuous stratification; adding sharp interfaces imposes '
        'narrow spectral notches on top of the bump.'
    ))

    # Export
    base = os.path.join(out_dir, 'figure_3_9A')
    fig.savefig(base + '.png')
    fig.savefig(base + '.pdf')
    plt.close(fig)


def fig_3_9B(out_dir):
    fig, ax = _new_figure()
    ax.set_title('Figure 3.9B — Angle–frequency plate')

    # Domain
    x = np.linspace(0.2, 2.2, 900)
    theta_deg = np.linspace(0, 80, 360)
    X, TH = np.meshgrid(x, theta_deg)

    # Baseline conversion band (angle-independent)
    band_sigma = 0.6 / (2 * math.sqrt(2 * math.log(2)))
    band = 0.35 * np.exp(-0.5 * ((X - 1.0) / band_sigma) ** 2)

    # Notch trajectories: slanted filaments that shift with angle
    data = 0.15 * np.ones_like(X)  # base floor
    data += band

    # Create 5 families of slanted notches with smooth spacing variation
    rng_centers = np.array([0.55, 0.75, 1.0, 1.3, 1.6])
    slopes = np.array([0.25, 0.30, 0.35, 0.40, 0.45]) / 80.0  # per degree
    widths = np.array([0.025, 0.028, 0.03, 0.032, 0.035])

    for c0, m, w in zip(rng_centers, slopes, widths):
        center = c0 + m * TH  # upward-right slant
        sigma_n = (w / (2 * math.sqrt(2 * math.log(2))))
        notch = 0.65 * np.exp(-0.5 * ((X - center) / sigma_n) ** 2)
        data += notch

    # Normalize to 0..1 for plotting
    data = (data - data.min()) / (data.max() - data.min() + 1e-9)

    # Plot heatmap; darker = higher -> use reversed perceptual colormap
    im = ax.imshow(data, origin='lower', aspect='auto',
                   extent=[x.min(), x.max(), theta_deg.min(), theta_deg.max()],
                   cmap='magma_r', interpolation='bilinear')

    # Axes labels and ticks
    ax.set_xlabel("ω/N")
    ax.set_ylabel("θ (deg)")
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.set_yticks([0, 15, 30, 45, 60, 75, 80])
    _apply_common_axes_styling(ax)

    # Overlays: conversion band and centerline
    _add_conversion_band(ax)

    # Annotate the band with a thin horizontal ruler arrow label (placed near top)
    ax.annotate('conversion band (angle-independent)',
                xy=(0.9, 76), xytext=(1.25, 76), fontsize=18,
                arrowprops=dict(arrowstyle='<->', color=COLORS['mode_conv_line']))

    # Annotate a filament
    ax.annotate('interface-induced notch shifts with θ',
                xy=(1.35, 50), xytext=(1.6, 62), fontsize=18,
                arrowprops=dict(arrowstyle='->', color=COLORS['interfacial']))

    # Colorbar (small at right)
    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label('Notch depth (arb.)')

    # Caption
    _add_caption(fig, (
        'Figure 3.9B. Angle–frequency plate: interface-induced notches shift with angle, '
        'while the conversion band remains centered at ω/N≈1.'
    ))

    base = os.path.join(out_dir, 'figure_3_9B')
    fig.savefig(base + '.png')
    fig.savefig(base + '.pdf')
    plt.close(fig)


def fig_3_9C(out_dir):
    # Two vertically stacked panels with shared time axis
    fig, axes = _new_figure(nrows=2, ncols=1, sharex=True,
                            gridspec_kw={'height_ratios': [1, 0.75]})
    ax_top, ax_bot = axes

    # Time domain
    t = np.linspace(0, 60, 1200)

    # Simulate Ri(t) on 0..2 with bursts below 0.4–0.5
    base_Ri = 1.0 + 0.25 * np.sin(2 * np.pi * t / 40.0)
    noise = 0.1 * np.random.default_rng(42).standard_normal(t.shape)
    Ri = np.clip(base_Ri + noise, 0, 2)

    # Inject low-Ri bursts at specific windows
    burst_windows = [(10, 14), (23, 27), (37, 41), (49, 54)]
    for t0, t1 in burst_windows:
        sel = (t >= t0) & (t <= t1)
        Ri[sel] = 0.25 + 0.1 * np.sin(2 * np.pi * (t[sel] - t0) / (t1 - t0))

    # Coherence gamma^2(t): high baseline with persistent dip plus extra sharp drops aligned to low-Ri
    gamma2 = 0.93 - 0.03 * np.sin(2 * np.pi * t / 30.0)
    # Persistent conversion-band dip around t ~ 30 s
    gamma2 -= 0.18 * np.exp(-0.5 * ((t - 30.0) / 6.0) ** 2)
    # Additional sharp drops aligned to low-Ri windows
    for t0, t1 in burst_windows:
        center = 0.5 * (t0 + t1)
        gamma2 -= 0.20 * np.exp(-0.5 * ((t - center) / 1.2) ** 2)
    gamma2 = np.clip(gamma2, 0.0, 1.0)

    # Plot low-Ri bands extending into top panel
    for t0, t1 in burst_windows:
        for ax in (ax_top, ax_bot):
            ax.axvspan(t0, t1, color=COLORS['shear'], alpha=0.18, linewidth=0)

    # Plot lines
    ax_top.plot(t, gamma2, color=COLORS['primary_data'], linewidth=3.0)
    ax_bot.plot(t, Ri, color='#4682B4', linewidth=2.5)  # steel-blue

    # Aligning guides (vertical faint gray at centers)
    for t0, t1 in burst_windows:
        center = 0.5 * (t0 + t1)
        for ax in (ax_top, ax_bot):
            ax.axvline(center, color=COLORS['centerline'], linestyle=(0, (1, 4)), linewidth=1.0)

    # Axes labels and ranges
    ax_top.set_ylabel("γ²(t) around ω/N≈1")
    ax_top.set_ylim(0, 1)
    ax_top.set_yticks(np.linspace(0, 1, 6))

    ax_bot.set_ylabel("Rᵢ(t)")
    ax_bot.set_ylim(0, 2)
    ax_bot.set_yticks([0, 0.25, 0.5, 0.7, 1, 1.5, 2])

    ax_bot.set_xlabel('time (s)')
    ax_bot.set_xlim(0, 60)
    ax_bot.set_xticks(np.arange(0, 61, 10))

    for ax in (ax_top, ax_bot):
        _apply_common_axes_styling(ax)

    # Micro-labels
    ax_top.annotate('conversion-band dip',
                    xy=(30, np.min(gamma2) + 0.05), xytext=(38, 0.35), fontsize=18,
                    arrowprops=dict(arrowstyle='->', color=COLORS['primary_data']))

    ax_bot.annotate(r'low-$R_i$ burst',
                    xy=(11.5, 0.22), xytext=(6, 0.55), fontsize=18,
                    arrowprops=dict(arrowstyle='->', color=COLORS['shear']))

    # Caption
    _add_caption(fig, (
        'Figure 3.9C. Time correlation between array coherence and '
        'Rᵢ(t): a persistent conversion-band dip plus intermittent losses coincident with low-Rᵢ bursts.'
    ))

    base = os.path.join(out_dir, 'figure_3_9C')
    fig.savefig(base + '.png')
    fig.savefig(base + '.pdf')
    plt.close(fig)


def fig_3_9D(out_dir):
    fig, ax = _new_figure()
    ax.set_title('Figure 3.9D — Mechanism-share waterfall (four canonical regimes)')

    categories = [
        'High-$R_i$\ncontinuous',
        'Marginal-$R_i$\ncontinuous',
        'Layered sharp',
        'Layered diffuse',
    ]

    # Shares (each sums to 1): Classical (gray), Conversion (amber), Interfacial (purple), Shear (teal)
    shares = [
        # Classical, Conversion, Interfacial, Shear
        [0.40, 0.48, 0.07, 0.05],  # High-Ri continuous
        [0.30, 0.38, 0.05, 0.27],  # Marginal-Ri continuous
        [0.25, 0.20, 0.52, 0.03],  # Layered sharp
        [0.42, 0.28, 0.14, 0.16],  # Layered diffuse
    ]

    shares = np.array(shares)
    bottoms = np.zeros(len(categories))

    labels = ['Classical', 'Conversion', 'Interfacial', 'Shear']
    colors = [COLORS['classical'], COLORS['mode_conv_fill'], COLORS['interfacial'], COLORS['shear']]

    x = np.arange(len(categories))
    bar_width = 0.6

    for i in range(4):
        bars = ax.bar(x, shares[:, i], bottom=bottoms, width=bar_width, color=colors[i], edgecolor='white', linewidth=0.8)
        # Add small in-band value labels if legible
        for rect, val in zip(bars, shares[:, i]):
            if val >= 0.12:  # space threshold
                ax.text(rect.get_x() + rect.get_width() / 2, rect.get_y() + rect.get_height() / 2,
                        f"{val:.2f}", ha='center', va='center', fontsize=14, color='white' if i in (2, 3) else 'black')
        bottoms += shares[:, i]

    ax.set_xlim(-0.5, len(categories) - 0.5)
    ax.set_ylim(0, 1)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_ylabel('Share')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=0)

    # Compact legend if needed
    ax.legend(labels, loc='upper right')

    _apply_common_axes_styling(ax)

    # Caption
    _add_caption(fig, (
        'Figure 3.9D. Mechanism shares (summing to unity) for four regimes: conversion dominates high-$R_i$ continuous; '
        'shear rises under marginal $R_i$; interfacial loss peaks for layered sharp and weakens for layered diffuse.'
    ))

    base = os.path.join(out_dir, 'figure_3_9D')
    fig.savefig(base + '.png')
    fig.savefig(base + '.pdf')
    plt.close(fig)


def generate(which, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    if which in ('A', 'all'):
        fig_3_9A(out_dir)
    if which in ('B', 'all'):
        fig_3_9B(out_dir)
    if which in ('C', 'all'):
        fig_3_9C(out_dir)
    if which in ('D', 'all'):
        fig_3_9D(out_dir)


def main():
    parser = argparse.ArgumentParser(description='Generate Figures 3.9A–D with shared house style.')
    parser.add_argument('which', choices=['A', 'B', 'C', 'D', 'all'], help='Which figure to generate')
    parser.add_argument('-o', '--out', default=os.path.join(SCRIPT_DIR, 'output'), help='Output directory')
    args = parser.parse_args()

    generate(args.which, args.out)


if __name__ == '__main__':
    main()
