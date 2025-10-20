from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
from matplotlib.lines import Line2D

import house_style as hs


# --------------------------- Utility primitives --------------------------- #

def _px_to_fig(x_px: float, y_px: float) -> tuple[float, float]:
    """Convert absolute pixels (2000x1400 canvas) to figure coords [0,1]."""
    return x_px / 2000.0, y_px / 1400.0


def _rect(ax, left_px, bottom_px, width_px, height_px, **kwargs):
    x, y = _px_to_fig(left_px, bottom_px)
    w, h = _px_to_fig(width_px, height_px)
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=10",
                          linewidth=hs.LW_PRIMARY, facecolor="#FFFFFF",
                          edgecolor="#111111", mutation_aspect=1.0, **kwargs)
    ax.add_patch(rect)
    return rect


def _text(ax, x_px, y_px, text, size, weight=None, ha="left", va="center", color="#111111"):
    x, y = _px_to_fig(x_px, y_px)
    ax.text(x, y, text, fontsize=size, fontweight=weight, ha=ha, va=va, color=color)


def _circle(ax, cx_px, cy_px, r_px, **kwargs):
    cx, cy = _px_to_fig(cx_px, cy_px)
    r = _px_to_fig(r_px, 0)[0]
    c = Circle((cx, cy), r, **kwargs)
    ax.add_patch(c)
    return c


def _arrow(ax, x0_px, y0_px, x1_px, y1_px, lw=hs.LW_SECONDARY, style="->", color="#111111", dotted=False):
    x0, y0 = _px_to_fig(x0_px, y0_px)
    x1, y1 = _px_to_fig(x1_px, y1_px)
    ls = (0, (1.5, 3.0)) if dotted else "-"
    arr = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=12,
                          linewidth=lw, linestyle=ls, color=color)
    ax.add_patch(arr)
    return arr


# --------------------------- Figure 3.7A --------------------------------- #

def figure_3_7a() -> None:
    hs.configure_matplotlib()
    fig = hs.new_figure("Figure 3.7A — Composite attenuation concept")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()

    # Layout guides (pixels)
    left_margin = 80
    right_margin = 80
    inputs_w = 300
    outputs_w = 360

    # (A) Inputs column
    inputs_h = 680
    inputs_bottom = 360
    inputs_box = _rect(ax, left_margin, inputs_bottom, inputs_w, inputs_h)
    _text(ax, left_margin + 20, inputs_bottom + inputs_h - 40, "Inputs", hs.LABEL_SIZE, weight="bold")

    bullet_y0 = inputs_bottom + inputs_h - 110
    bullet_gap = 70
    bullets = [
        ("$\\omega/N$ (frequency ratio)",),
        ("$Ri$ (stability)",),
        ("$k\\delta$ (optical thickness)",),
        ("$C_Z,\; A_t$ (contrast)",),
        ("Geometry: $\\theta$ (incidence), $r$ (range)",),
    ]
    for i, (label,) in enumerate(bullets):
        y = bullet_y0 - i * bullet_gap
        _circle(ax, left_margin + 26, y, 6, facecolor="#111111")
        _text(ax, left_margin + 46, y, label, hs.NOTE_SIZE)
        # Thin arrow from bullet to central module region
        _arrow(ax, left_margin + inputs_w + 10, y, 900, y, lw=hs.LW_SECONDARY, color="#333333")

    # (B) Similarity space cue (thumbnail)
    thumb_w, thumb_h = 520, 320
    thumb_left = 740
    thumb_bottom = 980
    thumb = _rect(ax, thumb_left, thumb_bottom, thumb_w, thumb_h)
    _text(ax, thumb_left + 10, thumb_bottom + thumb_h + 32, "Similarity space (cue)", hs.NOTE_SIZE, weight="bold")

    # Draw simple axes inside thumbnail
    tx0, ty0 = thumb_left + 60, thumb_bottom + 60
    tx1, ty1 = thumb_left + thumb_w - 40, thumb_bottom + thumb_h - 40
    # Axes lines
    _arrow(ax, tx0, ty0, tx1, ty0, style="-|>")
    _arrow(ax, tx0, ty0, tx0, ty1, style="-|>")
    _text(ax, tx1, ty0 - 24, "$\\omega/N$", hs.TICK_SIZE, ha="right", va="top")
    _text(ax, tx0 - 24, ty1, "$Ri$", hs.TICK_SIZE, ha="right", va="bottom")

    # Soft regions: conversion belt near omega/N ~ 1, shear-favored upper-left, near-classical lower-right
    # Approximate with translucent rectangles/ovals (simplified)
    cx0, cx1 = tx0 + 140, tx0 + 380
    cy0, cy1 = ty0 + 40, ty1 - 80
    # Conversion belt (amber wash)
    rect_conv = FancyBboxPatch(_px_to_fig(cx0, (cy0 + cy1) / 2 - 40), *_px_to_fig(cx1 - cx0, 80),
                               boxstyle="round,pad=0.0,rounding_size=30", transform=ax.transAxes,
                               facecolor=hs.COLORS["conversion"], edgecolor=None, alpha=0.20)
    # Note: we add via figure coords directly; simpler to add as a rectangle patch in data coords of figure
    ax.add_patch(rect_conv)
    _text(ax, (cx0 + cx1) / 2, (cy0 + cy1) / 2 + 60, "conversion belt", hs.TICK_SIZE, ha="center")

    _text(ax, tx0 + 40, ty1 - 20, "shear-favored", hs.TICK_SIZE, color=hs.COLORS["shear"]) 
    _text(ax, tx1 - 20, ty0 + 20, "near-classical", hs.TICK_SIZE, ha="right", color=hs.COLORS["classical"]) 

    # (C) Mechanism weighting module
    mod_w, mod_h = 560, 260
    mod_left = 720
    mod_bottom = 600
    module = _rect(ax, mod_left, mod_bottom, mod_w, mod_h)
    _text(ax, mod_left + 20, mod_bottom + mod_h - 36, "Mechanism weighting (shares sum to 1)", hs.LABEL_SIZE, weight="bold")

    # 100% stacked horizontal bar sample gauge
    gauge_left = mod_left + 24
    gauge_bottom = mod_bottom + 90
    gauge_w = mod_w - 48
    gauge_h = 42
    # Example shares at a chosen (Ri, omega/N, kδ, CZ)
    shares = [
        ("Classical", hs.COLORS["classical"], 0.38),
        ("Conversion", hs.COLORS["conversion"], 0.47),
        ("Interfacial", hs.COLORS["interfacial"], 0.08),
        ("Shear", hs.COLORS["shear"], 0.07),
    ]
    x_cursor = gauge_left
    handles = []
    for name, color, frac in shares:
        w = int(gauge_w * frac)
        bar = FancyBboxPatch(_px_to_fig(x_cursor, gauge_bottom), *_px_to_fig(w, gauge_h),
                             boxstyle="round,pad=0.0,rounding_size=6", facecolor=color,
                             edgecolor=color, linewidth=hs.LW_PRIMARY)
        ax.add_patch(bar)
        _text(ax, x_cursor + w / 2, gauge_bottom + gauge_h + 26, name, hs.TICK_SIZE, ha="center")
        handles.append(Line2D([0], [0], color=color, lw=hs.LW_PRIMARY))
        x_cursor += w

    # Sum-to-one tag and guidance
    _text(ax, mod_left + mod_w - 80, mod_bottom + 54, r"$\\sum w_i = 1$", hs.NOTE_SIZE, ha="right")
    _text(ax, mod_left + 20, mod_bottom + 28,
          "shares guided by §3.2 similarity & §3.4–3.6 scalings",
          int(hs.TICK_SIZE * 0.95))

    # (D) Combination node (Sigma)
    sigma_cx, sigma_cy = mod_left + mod_w / 2, mod_bottom - 80
    _circle(ax, sigma_cx, sigma_cy, 24, facecolor="#FFFFFF", edgecolor="#111111", linewidth=hs.LW_PRIMARY)
    _text(ax, sigma_cx, sigma_cy + 2, "Σ", hs.LABEL_SIZE, weight="bold", ha="center", va="center")
    _text(ax, sigma_cx, sigma_cy - 46, "Composite attenuation", hs.NOTE_SIZE, ha="center")

    # Arrow from module to sigma
    _arrow(ax, mod_left + mod_w / 2, mod_bottom, sigma_cx, sigma_cy + 26, lw=hs.LW_SECONDARY)

    # Two branches: priors (dotted back-arrow) and posterior forward
    # Priors dotted back to module
    _arrow(ax, sigma_cx - 80, sigma_cy, mod_left + 20, mod_bottom + mod_h - 20,
           lw=hs.LW_SECONDARY, dotted=True)
    _text(ax, mod_left + 24, mod_bottom + mod_h + 10, "priors", hs.TICK_SIZE)

    # Posterior forward to outputs
    post_x = 1600
    _arrow(ax, sigma_cx + 80, sigma_cy, post_x, sigma_cy, lw=hs.LW_SECONDARY)
    _text(ax, (sigma_cx + post_x) / 2, sigma_cy - 34, "posterior (with data)", hs.TICK_SIZE, ha="center")

    # (E) Outputs column
    outputs_h = 620
    outputs_bottom = 380
    outputs_box = _rect(ax, 2000 - right_margin - outputs_w, outputs_bottom, outputs_w, outputs_h)
    _text(ax, 2000 - right_margin - outputs_w + 20, outputs_bottom + outputs_h - 40,
          "Predicted / measured outputs", hs.LABEL_SIZE, weight="bold")

    # Small icons: TL(ω)
    icon_left = 2000 - right_margin - outputs_w + 30
    icon_w = outputs_w - 60
    row_gap = 150
    icon_y1 = outputs_bottom + outputs_h - 120
    # TL(ω) curve icon
    xs = np.linspace(0, 1, 60)
    ys = 0.6 - 0.15 * (xs ** 1.3)
    ax.plot(xs * _px_to_fig(icon_w, 0)[0] + _px_to_fig(icon_left, 0)[0],
            ys * _px_to_fig(0, outputs_h)[1] + _px_to_fig(0, icon_y1)[1],
            color="#111111", lw=hs.LW_SECONDARY, solid_capstyle='round', transform=ax.transAxes)
    _text(ax, icon_left, icon_y1 + 28, "TL($\\omega$)", hs.NOTE_SIZE)

    # Coherence γ^2(ω) with dip near 1
    icon_y2 = icon_y1 - row_gap
    ys2 = 0.7 - 0.35 * np.exp(-0.5 * ((xs - 0.55) / 0.12) ** 2)
    ax.plot(xs * _px_to_fig(icon_w, 0)[0] + _px_to_fig(icon_left, 0)[0],
            ys2 * _px_to_fig(0, outputs_h)[1] + _px_to_fig(0, icon_y2)[1],
            color="#111111", lw=hs.LW_SECONDARY, transform=ax.transAxes)
    _text(ax, icon_left, icon_y2 + 28, r"$\\gamma^2(\\omega)$", hs.NOTE_SIZE)

    # PSD(ω) width icon: narrow vs broad
    icon_y3 = icon_y2 - row_gap
    t = np.linspace(-2.5, 2.5, 120)
    narrow = np.exp(-t**2)
    broad = np.exp(-(t/1.6)**2)
    # Normalize for placement
    narrow = 0.25 * narrow / narrow.max()
    broad = 0.25 * broad / broad.max()
    # Map to axes coords region
    x_axis_len = _px_to_fig(icon_w, 0)[0]
    x0 = _px_to_fig(icon_left, 0)[0]
    y0 = _px_to_fig(0, icon_y3)[1]
    yscale = _px_to_fig(0, outputs_h)[1]
    x_norm = (t - t.min()) / (t.max() - t.min())
    ax.plot(x0 + x_norm * x_axis_len, y0 + (0.5 + narrow) * yscale, color="#111111", lw=hs.LW_SECONDARY, transform=ax.transAxes)
    ax.plot(x0 + x_norm * x_axis_len, y0 + (0.5 + broad) * yscale, color="#111111", lw=hs.LW_SECONDARY, linestyle=(0, (8, 6)), transform=ax.transAxes)
    _text(ax, icon_left, icon_y3 + 28, "PSD($\\omega$) width", hs.NOTE_SIZE)

    # Design implications note
    note_x = 2000 - right_margin - outputs_w + 20
    note_y = outputs_bottom + 40
    _arrow(ax, 2000 - right_margin - 40, note_y + 20, 2000 - right_margin - 80, note_y + 60, lw=hs.LW_SECONDARY)
    _text(ax, note_x, note_y,
          "Design implications: Choose $\\omega$, $\\theta$, $Ri$, $k\\delta$ to target mechanisms; update priors with data.",
          hs.TICK_SIZE)

    # Legend (bottom-right inside canvas)
    legend_items = [
        (Line2D([0], [0], color=hs.COLORS["classical"], lw=hs.LW_PRIMARY), "Classical"),
        (Line2D([0], [0], color=hs.COLORS["conversion"], lw=hs.LW_PRIMARY), "Mode conversion"),
        (Line2D([0], [0], color=hs.COLORS["interfacial"], lw=hs.LW_PRIMARY), "Interfacial"),
        (Line2D([0], [0], color=hs.COLORS["shear"], lw=hs.LW_PRIMARY), "Shear-mediated"),
    ]
    hs.inside_legend(ax, legend_items, loc="lower right")

    # Caption
    hs.add_caption(fig, "Figure 3.7A. Composite attenuation concept. Similarity variables feed a mechanism-weighting module that yields shares summing to unity; these combine into a composite prediction of attenuation and observables used to set priors and design experiments.")

    fig.savefig("figures/figure_3_7A.svg", format="svg", bbox_inches="tight")
    plt.close(fig)


# --------------------------- Figure 3.7B1 -------------------------------- #

def _shares_b1(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    # Conversion: broad dome ~ peak 0.5–0.6 at x=1
    conv = 0.55 * np.exp(-0.5 * ((x - 1.0) / 0.40) ** 2)
    # Shear: small, shoulder near 1 (<= 0.10)
    shear = 0.03 + 0.07 * np.exp(-0.5 * ((x - 1.0) / 0.35) ** 2)
    # Interfacial: minimal, nearly flat (<= 0.10)
    interf = 0.06 + 0.01 * np.cos((x - 0.2) * np.pi / 2.0)
    interf = np.clip(interf, 0.04, 0.09)
    # Classical: remainder to 1, yields ~0.35–0.45 baseline near mid band
    classical = 1.0 - (conv + shear + interf)
    # Ensure no negatives from tails
    classical = np.clip(classical, 0.05, None)
    total = classical + conv + interf + shear
    # Normalize to exactly 1
    classical /= total
    conv /= total
    interf /= total
    shear /= total
    return classical, conv, interf, shear


def figure_3_7b1() -> None:
    hs.configure_matplotlib()
    fig = hs.new_figure("Figure 3.7B1 — Mechanism shares vs $\\omega/N$ (High $Ri$)")
    ax = fig.add_subplot(1, 1, 1)

    x = np.linspace(0.2, 2.2, 600)
    classical, conv, interf, shear = _shares_b1(x)

    # Amber conversion window and dotted centerline
    hs.add_conversion_window(ax, 0.8, 1.2)

    # Stacked areas: bottom->top classical, conversion, interfacial, shear
    ax.stackplot(x, classical, conv, interf, shear,
                 colors=[hs.COLORS[c] for c in ("classical", "conversion", "interfacial", "shear")],
                 linewidth=0.0)

    # Axes styling
    hs.style_axes_common(ax, xlabel=r"$\\omega/N$", ylabel="Share (0–1)",
                         xlim=(0.2, 2.2), ylim=(0.0, 1.0),
                         xticks=[0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0],
                         yticks=[0.0, 0.25, 0.5, 0.75, 1.0])

    # Small annotations
    ax.annotate("conversion peak near $\\omega/N \\approx 1$",
                xy=(1.0, classical[np.argmin(abs(x-1.0))] + conv[np.argmin(abs(x-1.0))]/2),
                xytext=(1.35, 0.85),
                arrowprops=dict(arrowstyle="->", lw=hs.LW_SECONDARY), fontsize=hs.NOTE_SIZE)
    ax.annotate("classical baseline",
                xy=(0.6, classical[np.argmin(abs(x-0.6))]/2), xytext=(0.35, 0.25),
                arrowprops=dict(arrowstyle="->", lw=hs.LW_SECONDARY), fontsize=hs.NOTE_SIZE)
    ax.annotate("secondary shear (stable)",
                xy=(1.15, 1 - shear[np.argmin(abs(x-1.15))]/2), xytext=(1.55, 0.65),
                arrowprops=dict(arrowstyle="->", lw=hs.LW_SECONDARY), fontsize=hs.NOTE_SIZE)

    # Legend inside
    legend_items = [
        (Line2D([0], [0], color=hs.COLORS["classical"], lw=hs.LW_PRIMARY), "Classical"),
        (Line2D([0], [0], color=hs.COLORS["conversion"], lw=hs.LW_PRIMARY), "Mode conversion"),
        (Line2D([0], [0], color=hs.COLORS["interfacial"], lw=hs.LW_PRIMARY), "Interfacial"),
        (Line2D([0], [0], color=hs.COLORS["shear"], lw=hs.LW_PRIMARY), "Shear-mediated"),
    ]
    hs.inside_legend(ax, legend_items, loc="upper right")

    hs.add_caption(fig, "Figure 3.7B1. Under high $Ri$ and continuous stratification, mode conversion dominates near $\\omega/N \\approx 1$; classical loss is the baseline; shear and interfacial contributions are secondary.")

    fig.savefig("figures/figure_3_7B1.svg", format="svg", bbox_inches="tight")
    plt.close(fig)


# --------------------------- Figure 3.7B2 -------------------------------- #

def _shares_b2(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    # Conversion: domed but slightly lower than B1
    conv = 0.45 * np.exp(-0.5 * ((x - 1.0) / 0.42) ** 2)
    # Shear: broader rise 0.8–1.3, up to ~0.35–0.45
    shear = 0.06 + 0.36 * np.exp(-0.5 * ((x - 1.05) / 0.38) ** 2)
    # Interfacial: still small
    interf = 0.05 + 0.01 * np.cos((x - 0.2) * np.pi / 2.0)
    interf = np.clip(interf, 0.04, 0.09)
    classical = 1.0 - (conv + shear + interf)
    classical = np.clip(classical, 0.02, None)
    total = classical + conv + interf + shear
    classical /= total
    conv /= total
    interf /= total
    shear /= total
    return classical, conv, interf, shear


def figure_3_7b2() -> None:
    hs.configure_matplotlib()
    fig = hs.new_figure("Figure 3.7B2 — Mechanism shares vs $\\omega/N$ (Marginal $Ri$)")
    ax = fig.add_subplot(1, 1, 1)

    x = np.linspace(0.2, 2.2, 600)
    classical, conv, interf, shear = _shares_b2(x)

    hs.add_conversion_window(ax, 0.8, 1.2)

    ax.stackplot(x, classical, conv, interf, shear,
                 colors=[hs.COLORS[c] for c in ("classical", "conversion", "interfacial", "shear")],
                 linewidth=0.0)

    hs.style_axes_common(ax, xlabel=r"$\\omega/N$", ylabel="Share (0–1)",
                         xlim=(0.2, 2.2), ylim=(0.0, 1.0),
                         xticks=[0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0],
                         yticks=[0.0, 0.25, 0.5, 0.75, 1.0])

    ax.annotate("shear-mediated share expands and can rival conversion near $\\omega/N\\sim 1$",
                xy=(1.05, classical[np.argmin(abs(x-1.05))] + conv[np.argmin(abs(x-1.05))] + interf[np.argmin(abs(x-1.05))] + shear[np.argmin(abs(x-1.05))]/2),
                xytext=(1.5, 0.85),
                arrowprops=dict(arrowstyle="->", lw=hs.LW_SECONDARY), fontsize=hs.NOTE_SIZE)

    legend_items = [
        (Line2D([0], [0], color=hs.COLORS["classical"], lw=hs.LW_PRIMARY), "Classical"),
        (Line2D([0], [0], color=hs.COLORS["conversion"], lw=hs.LW_PRIMARY), "Mode conversion"),
        (Line2D([0], [0], color=hs.COLORS["interfacial"], lw=hs.LW_PRIMARY), "Interfacial"),
        (Line2D([0], [0], color=hs.COLORS["shear"], lw=hs.LW_PRIMARY), "Shear-mediated"),
    ]
    hs.inside_legend(ax, legend_items, loc="upper right")

    hs.add_caption(fig, "Figure 3.7B2. For marginal $Ri$, shear-mediated loss broadens around the conversion band and can rival conversion near $\\omega/N\\sim 1$; classical share correspondingly diminishes.")

    fig.savefig("figures/figure_3_7B2.svg", format="svg", bbox_inches="tight")
    plt.close(fig)


# --------------------------- Figure 3.7C1 -------------------------------- #

def _shares_c1(kd: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    # Interfacial: high at low kd, monotone decrease to ~0.10 by kd~3
    interfacial = 0.10 + 0.50 * (kd / 0.1) ** (-0.70)
    interfacial = np.clip(interfacial, 0.10, 0.65)
    # Conversion: roughly constant (0.20–0.30), mild bump near kd~1
    conversion = 0.24 + 0.04 * np.exp(-0.5 * (np.log10(kd) / 0.25) ** 2)
    conversion = np.clip(conversion, 0.20, 0.30)
    # Shear: small and nearly flat (<= 0.10)
    shear = 0.05 + 0.01 * np.cos(np.log(kd + 1))
    shear = np.clip(shear, 0.03, 0.08)
    # Classical: remainder to 1
    classical = 1.0 - (interfacial + conversion + shear)
    classical = np.clip(classical, 0.05, None)
    total = classical + conversion + interfacial + shear
    classical /= total
    conversion /= total
    interfacial /= total
    shear /= total
    return classical, conversion, interfacial, shear


def figure_3_7c1() -> None:
    hs.configure_matplotlib()
    fig = hs.new_figure("Figure 3.7C1 — Mechanism shares vs $k\\delta$ (interface sharpness), fixed $\\omega/N=1$")
    ax = fig.add_subplot(1, 1, 1)

    kd = np.logspace(np.log10(0.1), np.log10(3.0), 500)
    classical, conversion, interfacial, shear = _shares_c1(kd)

    # Stacked areas across kd (log x-axis)
    ax.stackplot(kd, classical, conversion, interfacial, shear,
                 colors=[hs.COLORS[c] for c in ("classical", "conversion", "interfacial", "shear")],
                 linewidth=0.0)

    ax.set_xscale('log')
    hs.style_axes_common(ax, xlabel=r"$k\\delta$", ylabel="Share (0–1)",
                         xlim=(0.1, 3.0), ylim=(0.0, 1.0),
                         xticks=[0.1, 0.2, 0.5, 1.0, 2.0, 3.0],
                         yticks=[0.0, 0.25, 0.5, 0.75, 1.0])
    # Matplotlib won't place log xticks via style_axes_common unless we set minor off
    ax.set_xticks([0.1, 0.2, 0.5, 1.0, 2.0, 3.0])
    ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
    ax.ticklabel_format(style='plain', axis='x')

    # Mini-gauge beneath x-axis
    y_min, y_max = ax.get_ylim()
    y_text = y_min - 0.10 * (y_max - y_min)
    for xv in [0.1, 1.0, 3.0]:
        ax.plot([xv, xv], [y_min - 0.03, y_min + 0.005], color="#111111", lw=hs.LW_DOTTED, clip_on=False)
    ax.text(0.1, y_text, "thin", ha="center", va="top", fontsize=hs.TICK_SIZE)
    ax.text(1.0, y_text, "resonant", ha="center", va="top", fontsize=hs.TICK_SIZE)
    ax.text(3.0, y_text, "thick", ha="center", va="top", fontsize=hs.TICK_SIZE)
    ax.plot([0.1, 3.0], [y_min - 0.045, y_min - 0.045], color="#111111", lw=hs.LW_DOTTED, clip_on=False)

    legend_items = [
        (Line2D([0], [0], color=hs.COLORS["classical"], lw=hs.LW_PRIMARY), "Classical"),
        (Line2D([0], [0], color=hs.COLORS["conversion"], lw=hs.LW_PRIMARY), "Mode conversion"),
        (Line2D([0], [0], color=hs.COLORS["interfacial"], lw=hs.LW_PRIMARY), "Interfacial"),
        (Line2D([0], [0], color=hs.COLORS["shear"], lw=hs.LW_PRIMARY), "Shear-mediated"),
    ]
    hs.inside_legend(ax, legend_items, loc="upper right")

    hs.add_caption(fig, "Figure 3.7C1. Interfacial share peaks for sharp, high-contrast transitions (low $k\\delta$) and decays as the interface becomes diffuse (large $k\\delta$). Classical share increases complementarily; conversion and shear change little at fixed $\\omega/N$.")

    fig.savefig("figures/figure_3_7C1.svg", format="svg", bbox_inches="tight")
    plt.close(fig)


# --------------------------- Entrypoint ----------------------------------- #

def main():
    figure_3_7a()
    figure_3_7b1()
    figure_3_7b2()
    figure_3_7c1()


if __name__ == "__main__":
    main()
