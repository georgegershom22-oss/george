from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Arc
from matplotlib.lines import Line2D

from figures.common_style import (
    make_figure,
    add_axes_in_pixels,
    add_panel_title,
    add_caption,
    save_all,
    COLORS,
    px_to_pt,
    content_rect_px,
)


def add_main_panel(fig: plt.Figure):
    # Layout per spec (approx): main panel ~1200x1000 px, right column 260x3 stacked
    L, B, W, H = content_rect_px()

    main_w, main_h = 1200, 1000
    right_w = 260
    gap = 60

    # Center vertically inside content
    main_x = L
    main_y = B + (H - main_h) // 2

    main_ax = add_axes_in_pixels(fig, main_x, main_y, main_w, main_h)
    main_ax.set_xlim(0, 1)
    main_ax.set_ylim(0, 1)
    main_ax.set_aspect('auto')
    main_ax.axis('off')

    # Right column start
    right_x = L + main_w + gap
    # Stack of three microplots, 260x240 px each, with 40 px spacing
    micro_w, micro_h, micro_gap = right_w, 240, 40
    total_micros_h = 3 * micro_h + 2 * micro_gap
    start_y = B + (H - total_micros_h) // 2

    micro_axes = [
        add_axes_in_pixels(fig, right_x, start_y + (2 - i) * (micro_h + micro_gap), micro_w, micro_h)
        for i in range(3)
    ]
    for ax in micro_axes:
        ax.set_facecolor('white')

    return main_ax, micro_axes


def draw_stratified_gradient(ax: plt.Axes):
    ny, nx = 400, 20
    grad = np.linspace(0, 1, ny).reshape(ny, 1)
    # Build custom gradient RGB
    top = np.array([0xB3, 0xD7, 0xFF]) / 255.0
    bottom = np.array([0x0B, 0x3C, 0x5D]) / 255.0
    rgb = top * (1 - grad) + bottom * grad
    img = np.repeat(rgb, nx, axis=1)
    ax.imshow(img, extent=[0, 1, 0, 1], origin='lower', aspect='auto')


def draw_interface_band(ax: plt.Axes, center_y=0.5, thickness_px=40, main_h_px=1000):
    # Convert 40 px to axis fraction based on known main panel pixel height
    band_h = thickness_px / main_h_px
    y0 = center_y - band_h / 2
    rect = Rectangle((0.0, y0), 1.0, band_h, facecolor=COLORS['magenta'], alpha=0.20, edgecolor='none')
    ax.add_patch(rect)
    return y0, y0 + band_h


def draw_bracket_and_labels(ax: plt.Axes, y0: float, y1: float):
    # Draw simple right-hand bracket with label 'interface thickness δ'
    x = 0.99
    # vertical line
    ax.plot([x, x], [y0, y1], color=COLORS['charcoal'], linewidth=px_to_pt(2))
    # small ticks
    tick = 0.015
    ax.plot([x - tick, x], [y1, y1], color=COLORS['charcoal'], linewidth=px_to_pt(2))
    ax.plot([x - tick, x], [y0, y0], color=COLORS['charcoal'], linewidth=px_to_pt(2))

    ax.text(0.995, 0.5 * (y0 + y1), r"interface thickness $\,\delta$", ha='left', va='center', rotation=90, fontsize=16)
    ax.text(0.94, 0.5 * (y0 + y1) + 0.08, r"$A_t,\; C_Z$", ha='right', va='center', fontsize=16)


def draw_source_and_rays(ax: plt.Axes, y0: float, y1: float):
    # Piston/source at left
    src_center = (0.10, 0.55)
    circle = Circle(src_center, 0.03, facecolor="#E5E7EB", edgecolor=COLORS['charcoal'], linewidth=px_to_pt(2))
    ax.add_patch(circle)

    # Incident ray at angle theta relative to horizontal
    theta_deg = 35.0
    theta = np.radians(theta_deg)
    intercept = (0.42, 0.5)

    # Draw incident ray from source to intercept
    ray_inc = FancyArrowPatch(src_center, intercept, arrowstyle='-|>', mutation_scale=12,
                              linewidth=px_to_pt(3), color=COLORS['orange'])
    ax.add_patch(ray_inc)

    # Protractor arc showing theta
    arc = Arc((intercept[0] - 0.08, intercept[1]), width=0.16, height=0.16, angle=0,
              theta1=0, theta2=theta_deg, color=COLORS['charcoal'], linewidth=px_to_pt(1.2))
    ax.add_patch(arc)
    ax.text(intercept[0] - 0.02, intercept[1] + 0.025, r"$\theta$", fontsize=16)

    # Internal passes within band (fading)
    y_top, y_bot = y1, y0
    x0, x1 = intercept[0], intercept[0] + 0.2
    for i, (y_start, y_end) in enumerate([(y_top, y_bot), (y_bot, y_top), (y_top, y_bot)]):
        alpha = 0.6 * (0.65 ** i)
        ax.plot([x0 + 0.04 * i, x1 - 0.04 * i], [y_start, y_end], color=COLORS['orange'], linewidth=px_to_pt(2.2), alpha=alpha)

    # Reflected and transmitted rays
    refl_end = (intercept[0] - 0.25, 0.78)
    trans_end = (intercept[0] + 0.35, 0.22)
    ray_R = FancyArrowPatch(intercept, refl_end, arrowstyle='-|>', mutation_scale=12,
                            linewidth=px_to_pt(3), color=COLORS['steel_blue'])
    ray_T = FancyArrowPatch(intercept, trans_end, arrowstyle='-|>', mutation_scale=12,
                            linewidth=px_to_pt(3), color=COLORS['steel_blue'])
    ax.add_patch(ray_R)
    ax.add_patch(ray_T)

    ax.text(intercept[0] - 0.02, intercept[1] + 0.06, r"$R$", fontsize=16, color=COLORS['charcoal'])
    ax.text(intercept[0] + 0.04, intercept[1] - 0.06, r"$T$", fontsize=16, color=COLORS['charcoal'])


def draw_layer_tags(ax: plt.Axes, y0: float, y1: float):
    ax.text(0.15, min(0.94, y1 + 0.05), r"upper: $\rho_1,\; c_1$", fontsize=16, ha='left', va='top', color=COLORS['charcoal'])
    ax.text(0.15, max(0.06, y0 - 0.05), r"lower: $\rho_2,\; c_2$", fontsize=16, ha='left', va='bottom', color=COLORS['charcoal'])


def draw_axes_triad(ax: plt.Axes):
    # Tiny x–z axes at lower-left interior; label 'z=0 at bottom'
    origin = (0.06, 0.08)
    x_end = (origin[0] + 0.08, origin[1])
    z_end = (origin[0], origin[1] + 0.10)
    ax.add_line(Line2D([origin[0], x_end[0]], [origin[1], x_end[1]], color=COLORS['charcoal'], linewidth=px_to_pt(2)))
    ax.add_line(Line2D([origin[0], z_end[0]], [origin[1], z_end[1]], color=COLORS['charcoal'], linewidth=px_to_pt(2)))
    ax.text(x_end[0] + 0.01, x_end[1], 'x', va='center', fontsize=14)
    ax.text(z_end[0], z_end[1] + 0.01, 'z', ha='center', fontsize=14)
    ax.text(origin[0] - 0.01, 0.005, 'z=0 at bottom', ha='left', va='bottom', fontsize=12)


def draw_microplots(fig: plt.Figure, axes: list[plt.Axes]):
    rho_ax, c0_ax, kdelta_ax = axes

    # Common z-domain
    z = np.linspace(0, 1, 501)

    # ρ(z): sharp → diffuse using tanh steepness
    def profile(z, z0=0.5, delta=0.02):
        return 0.5 * (1 + np.tanh((z - z0) / delta))

    rho_ax.plot(profile(z, delta=0.01), z, color=COLORS['primary_blue'], linewidth=px_to_pt(3), alpha=0.9, label='sharp')
    rho_ax.plot(profile(z, delta=0.03), z, color=COLORS['primary_blue'], linewidth=px_to_pt(2.5), alpha=0.7, label='moderate')
    rho_ax.plot(profile(z, delta=0.08), z, color=COLORS['primary_blue'], linewidth=px_to_pt(2.0), alpha=0.5, label='diffuse')

    rho_ax.set_xlim(0, 1)
    rho_ax.set_ylim(0, 1)
    rho_ax.set_xticks([])
    rho_ax.set_yticks([])
    for spine in rho_ax.spines.values():
        spine.set_visible(False)
    rho_ax.text(0.02, 0.95, r"$\rho(z)$", transform=rho_ax.transAxes, ha='left', va='top', fontsize=16)
    rho_ax.text(0.98, 0.10, 'sharp / moderate / diffuse', transform=rho_ax.transAxes, ha='right', va='bottom', fontsize=12)

    # c0(z): matching stepped → smooth (thin blue-gray)
    c0_ax.plot(profile(z, delta=0.01), z, color=COLORS['steel_blue'], linewidth=px_to_pt(2.2), alpha=0.9)
    c0_ax.plot(profile(z, delta=0.03), z, color=COLORS['steel_blue'], linewidth=px_to_pt(2.0), alpha=0.7)
    c0_ax.plot(profile(z, delta=0.08), z, color=COLORS['steel_blue'], linewidth=px_to_pt(1.8), alpha=0.6)
    c0_ax.set_xlim(0, 1)
    c0_ax.set_ylim(0, 1)
    c0_ax.set_xticks([])
    c0_ax.set_yticks([])
    for spine in c0_ax.spines.values():
        spine.set_visible(False)
    c0_ax.text(0.02, 0.95, r"$c_0(z)$", transform=c0_ax.transAxes, ha='left', va='top', fontsize=16)

    # kδ gauge
    for spine in kdelta_ax.spines.values():
        spine.set_visible(False)
    kdelta_ax.set_xticks([])
    kdelta_ax.set_yticks([])
    kdelta_ax.set_xlim(0, 1)
    kdelta_ax.set_ylim(0, 1)

    # Draw gauge line
    kdelta_ax.plot([0.1, 0.9], [0.25, 0.25], color=COLORS['charcoal'], linewidth=px_to_pt(2))

    # Ticks at 0.1, 1, 3 mapped to positions
    ticks = [(0.1, 0.2), (1.0, 0.5), (3.0, 0.8)]
    for val, xpos in ticks:
        kdelta_ax.plot([xpos, xpos], [0.22, 0.28], color=COLORS['charcoal'], linewidth=px_to_pt(2))
        kdelta_ax.text(xpos, 0.18, f"{val:g}", ha='center', va='top', fontsize=14)

    kdelta_ax.text(0.02, 0.85, r'"Optical thickness" $k\,\delta$', fontsize=16, ha='left', va='top')
    kdelta_ax.text(0.98, 0.60, 'thin → resonant → thick', fontsize=12, ha='right', va='center')

    # Tiny cartoons: magenta band with a few wavefront lines above each tick
    def cartoon(xc):
        yb = 0.38
        bh = 0.06
        rect = Rectangle((xc - 0.06, yb), 0.12, bh, facecolor=COLORS['magenta'], alpha=0.20, edgecolor='none')
        kdelta_ax.add_patch(rect)
        # wavefronts (three parallel lines crossing)
        for i in range(3):
            x0 = xc - 0.055 + i * 0.04
            kdelta_ax.plot([x0, x0 + 0.12], [yb - 0.03, yb + bh + 0.03], color=COLORS['orange'], linewidth=px_to_pt(1.2))

    for _, xpos in ticks:
        cartoon(xpos)


def add_legend_box(ax: plt.Axes):
    # Legend box ~380x160 px in bottom-right of main panel
    # Map pixel dims to axis fraction assuming main panel is 1200x1000 px
    box_w_px, box_h_px = 380, 160
    frac_w = box_w_px / 1200
    frac_h = box_h_px / 1000
    x0 = 0.98 - frac_w
    y0 = 0.04

    # Background (frameless appearance; using subtle white to ensure readability on gradient)
    bg = Rectangle((x0, y0), frac_w, frac_h, transform=ax.transAxes, facecolor='white', alpha=0.85,
                   edgecolor='none', zorder=2)
    ax.add_patch(bg)

    # Samples
    # Orange line sample = "acoustic rays"
    ax.add_line(Line2D([x0 + 0.04 * frac_w, x0 + 0.40 * frac_w],
                       [y0 + 0.75 * frac_h, y0 + 0.75 * frac_h],
                       transform=ax.transAxes, color=COLORS['orange'], linewidth=px_to_pt(3), zorder=3))
    ax.text(x0 + 0.45 * frac_w, y0 + 0.75 * frac_h, 'acoustic rays', transform=ax.transAxes,
            ha='left', va='center', fontsize=14, zorder=3)

    # Magenta translucent swatch
    sw = Rectangle((x0 + 0.04 * frac_w, y0 + 0.40 * frac_h), 0.20 * frac_w, 0.18 * frac_h,
                   transform=ax.transAxes, facecolor=COLORS['magenta'], alpha=0.20, edgecolor='none', zorder=3)
    ax.add_patch(sw)
    ax.text(x0 + 0.28 * frac_w, y0 + 0.49 * frac_h, r'finite-thickness interface $\,\delta$', transform=ax.transAxes,
            ha='left', va='center', fontsize=14, zorder=3)

    # Small note
    ax.text(x0 + 0.04 * frac_w, y0 + 0.12 * frac_h,
            r"Amplitude/phase evolve via $k_z\,\delta$ inside the band",
            transform=ax.transAxes, ha='left', va='center', fontsize=12, color=COLORS['charcoal'], zorder=3)


def main():
    fig = make_figure()

    main_ax, micro_axes = add_main_panel(fig)

    # Main rectangle: stratified water column with vertical blue gradient
    draw_stratified_gradient(main_ax)

    # Interface band
    y0, y1 = draw_interface_band(main_ax, center_y=0.5, thickness_px=40, main_h_px=1000)

    # Bracket and labels
    draw_bracket_and_labels(main_ax, y0, y1)

    # Tags for layers
    draw_layer_tags(main_ax, y0, y1)

    # Rays + protractor
    draw_source_and_rays(main_ax, y0, y1)

    # Axes triad
    draw_axes_triad(main_ax)

    # Micro-plots (right column)
    draw_microplots(fig, micro_axes)

    # Legend box
    add_legend_box(main_ax)

    add_panel_title(fig, "Figure 3.5A — Finite-thickness interface geometry and controls")
    add_caption(fig, (
        "Figure 3.5A. Geometry of a finite-thickness interface with contrast $(A_t,\, C_Z)$, incidence $\theta$, "
        "and phase-thickness $k_z\,\delta$. Multiple internal traversals generate frequency- and angle-dependent R/T."
    ))

    save_all(fig, "Figure_3_5A")


if __name__ == "__main__":
    main()
