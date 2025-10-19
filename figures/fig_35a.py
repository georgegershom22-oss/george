from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Arc

from .house_style import (
    CanvasSpec,
    COLORS,
    new_canvas,
    px_to_pt,
    add_caption,
    save_figure,
)


def _draw_water_column(ax: plt.Axes, dpi: int) -> None:
    # Main panel rectangle (approx 1200x1000 px equivalent within axes)
    # We'll use axes-relative units: left ~0.05, width ~0.63, height ~0.72
    left, bottom, width, height = 0.05, 0.18, 0.63, 0.72

    # Gradient: approximate with multiple horizontal bands
    num_bands = 80
    for i in range(num_bands):
        y0 = bottom + height * i / num_bands
        y1 = bottom + height * (i + 1) / num_bands
        t = i / (num_bands - 1)
        # Top light blue to bottom deep blue
        color = _lerp_color((0xB3/255, 0xD7/255, 0xFF/255), (0x0B/255, 0x3C/255, 0x5D/255), t)
        ax.add_patch(Rectangle((left, y0), width, y1 - y0, transform=ax.transAxes,
                               facecolor=color, edgecolor='none', zorder=-20))

    # Border frame of the main panel (optional subtle outline)
    ax.add_patch(Rectangle((left, bottom), width, height, transform=ax.transAxes,
                           fill=False, edgecolor=COLORS['grid'], linewidth=px_to_pt(1.2, dpi), zorder=10))

    # Return useful geometry for later elements
    return left, bottom, width, height


def _lerp_color(c0, c1, t):
    return tuple((1 - t) * c0[i] + t * c1[i] for i in range(3))


def _draw_interface_band(ax: plt.Axes, panel_rect, dpi: int) -> tuple[float, float, float, float]:
    left, bottom, width, height = panel_rect
    band_th = 0.04  # ~40 px relative; depends on axes scaling
    band_y = bottom + 0.5 * height - 0.5 * band_th
    rect = Rectangle((left, band_y), width, band_th, transform=ax.transAxes,
                     facecolor=COLORS['magenta'], alpha=0.20, edgecolor='none', zorder=-5)
    ax.add_patch(rect)

    # Bracket on right with label δ
    bracket_x = left + width + 0.02
    y0 = band_y
    y1 = band_y + band_th
    lw = px_to_pt(2.0, dpi)
    ax.plot([bracket_x, bracket_x], [y0, y1], transform=ax.transAxes, color=COLORS['charcoal'], lw=lw)
    ax.plot([bracket_x - 0.01, bracket_x], [y0, y0], transform=ax.transAxes, color=COLORS['charcoal'], lw=lw)
    ax.plot([bracket_x - 0.01, bracket_x], [y1, y1], transform=ax.transAxes, color=COLORS['charcoal'], lw=lw)
    ax.text(bracket_x + 0.008, (y0 + y1) / 2, r"interface thickness $\delta$", transform=ax.transAxes,
            va='center', ha='left', fontsize=18)

    return band_y, band_th


def _draw_layer_tags(ax: plt.Axes, panel_rect, band_y, band_th):
    left, bottom, width, height = panel_rect
    ax.text(left + width - 0.02, band_y + band_th + 0.02, r"upper: $\rho_1,\, c_1$",
            transform=ax.transAxes, ha='right', va='bottom', fontsize=16, color=COLORS['charcoal'])
    ax.text(left + width - 0.02, band_y - 0.02, r"lower: $\rho_2,\, c_2$",
            transform=ax.transAxes, ha='right', va='top', fontsize=16, color=COLORS['charcoal'])
    ax.text(left + width + 0.02, band_y + 0.5 * band_th, r"$A_t,\, C_Z$",
            transform=ax.transAxes, ha='left', va='center', fontsize=16, color=COLORS['charcoal'])


def _draw_source_and_rays(ax: plt.Axes, panel_rect, band_y, band_th, dpi: int):
    left, bottom, width, height = panel_rect
    # Source disk
    src_cx = left + 0.02
    src_cy = bottom + 0.65 * height
    src_r = 0.02
    circ = plt.Circle((src_cx, src_cy), src_r, transform=ax.transAxes, facecolor="#DDDDDD",
                      edgecolor=COLORS['charcoal'], linewidth=px_to_pt(2.0, dpi), zorder=5)
    ax.add_patch(circ)

    # Incident ray at obliquity theta relative to horizontal
    theta_deg = 25
    theta_rad = np.deg2rad(theta_deg)
    # Start slightly to the right of the source, draw towards the interface band
    p0 = np.array([src_cx + src_r + 0.008, src_cy])
    # Compute intersection with band center line
    band_center = band_y + 0.5 * band_th
    dx = 0.5 * width
    dy = np.tan(-np.deg2rad(theta_deg)) * dx  # negative slope (downward)
    p1 = p0 + np.array([dx, dy])

    # Clip to within panel
    p1[0] = min(p1[0], left + width - 0.02)
    p1[1] = max(min(p1[1], bottom + height - 0.02), bottom + 0.02)

    arrowprops = dict(arrowstyle='-', color=COLORS['orange'], lw=px_to_pt(3.0, dpi),
                      shrinkA=0, shrinkB=0, mutation_scale=8)
    ax.add_patch(FancyArrowPatch(p0, p1, transform=ax.transAxes, **arrowprops))

    # Protractor arc for theta
    arc_r = 0.06
    arc = Arc((p0[0], p0[1]), arc_r, arc_r, angle=0, theta1=330, theta2=360,
              transform=ax.transAxes, color=COLORS['charcoal'], lw=px_to_pt(2.0, dpi))
    ax.add_patch(arc)
    ax.text(p0[0] + 0.06, p0[1] - 0.005, r"$\theta$", transform=ax.transAxes,
            fontsize=18, ha='left', va='top')

    # Internal multiple passes (thin segments within band)
    # Draw 3 bounces with fading opacity
    n_bounces = 3
    x_left = left + 0.10 * width
    x_right = left + 0.90 * width
    y_top = band_y + band_th
    y_bot = band_y
    alpha_vals = [0.8, 0.5, 0.25]
    for i in range(n_bounces):
        y = y_top if i % 2 == 0 else y_bot
        ax.plot([x_left, x_right], [y, y], transform=ax.transAxes, color=COLORS['orange'],
                lw=px_to_pt(2.0, dpi), alpha=alpha_vals[i], zorder=2)
        x_left += 0.03 * width
        x_right -= 0.03 * width

    # Reflected (R) and transmitted (T) rays near first interface crossing
    # Use the point where the incident ray meets the band center approximately
    cross_x = p1[0]
    cross_y = band_center
    # Reflected upward
    pr1 = np.array([cross_x - 0.20 * width, cross_y + 0.12 * height])
    ax.add_patch(FancyArrowPatch((cross_x, cross_y), pr1, transform=ax.transAxes, **arrowprops))
    ax.text(cross_x - 0.04, cross_y + 0.06, r"$R$", transform=ax.transAxes, fontsize=18, ha='right')
    # Transmitted downward
    pt1 = np.array([cross_x + 0.22 * width, cross_y - 0.14 * height])
    ax.add_patch(FancyArrowPatch((cross_x, cross_y), pt1, transform=ax.transAxes, **arrowprops))
    ax.text(cross_x + 0.05, cross_y - 0.06, r"$T$", transform=ax.transAxes, fontsize=18, ha='left')

    # Axes triad at lower-left interior; "z=0 at bottom"
    triad_origin = (left + 0.02, bottom + 0.03)
    ax.add_patch(FancyArrowPatch(triad_origin, (triad_origin[0] + 0.05, triad_origin[1]),
                                 transform=ax.transAxes, arrowstyle='-|>', color=COLORS['charcoal'],
                                 lw=px_to_pt(2.0, dpi)))
    ax.add_patch(FancyArrowPatch(triad_origin, (triad_origin[0], triad_origin[1] + 0.06),
                                 transform=ax.transAxes, arrowstyle='-|>', color=COLORS['charcoal'],
                                 lw=px_to_pt(2.0, dpi)))
    ax.text(triad_origin[0] + 0.055, triad_origin[1] - 0.005, 'x', transform=ax.transAxes, fontsize=14)
    ax.text(triad_origin[0] - 0.01, triad_origin[1] + 0.065, 'z', transform=ax.transAxes, fontsize=14)
    ax.text(triad_origin[0] - 0.005, triad_origin[1] - 0.02, 'z=0 at bottom', transform=ax.transAxes,
            fontsize=14, color=COLORS['charcoal'])


def _draw_microplots(ax: plt.Axes, dpi: int):
    # Right column micro-plots, three axes stacked, frameless
    # Place within axes in figure fraction via inset axes
    col_left = 0.72
    col_width = 0.26
    h = 0.18
    gaps = 0.04

    # ρ(z)
    a1 = ax.inset_axes([col_left, 0.64, col_width, h])
    _style_micro_axes(a1)
    z = np.linspace(-1, 1, 400)
    for delta, lw, alpha, label in [(0.05, px_to_pt(3, dpi), 1.0, 'sharp'),
                                    (0.15, px_to_pt(2.5, dpi), 0.9, 'moderate'),
                                    (0.35, px_to_pt(2.0, dpi), 0.8, 'diffuse')]:
        rho = 0.5 * (1 + np.tanh(z / delta))
        a1.plot(rho, z, color=COLORS['deep_blue'], lw=lw, alpha=alpha)
    a1.text(0.02, 0.92, r"$\rho(z)$: sharp / moderate / diffuse", transform=a1.transAxes,
            fontsize=14, ha='left', va='top')

    # c0(z)
    a2 = ax.inset_axes([col_left, 0.40, col_width, h])
    _style_micro_axes(a2)
    for delta, lw in [(0.05, px_to_pt(2.2, dpi)), (0.15, px_to_pt(2.0, dpi)), (0.35, px_to_pt(1.8, dpi))]:
        c0 = 0.3 + 0.7 * (0.5 * (1 + np.tanh(z / delta)))
        a2.plot(c0, z, color=COLORS['steel_blue'], lw=lw)
    a2.text(0.02, 0.92, r"$c_0(z)$: stepped → smooth", transform=a2.transAxes,
            fontsize=14, ha='left', va='top')

    # kδ gauge
    a3 = ax.inset_axes([col_left, 0.16, col_width, h])
    _style_micro_axes(a3)
    a3.set_xlim(0, 3.2)
    a3.set_ylim(0, 1)
    # Gauge line
    a3.hlines(0.4, 0.2, 3.0, color=COLORS['charcoal'], lw=px_to_pt(2.0, dpi))
    # Ticks at 0.1, 1, 3
    for x, lab in [(0.1, '0.1'), (1.0, '1'), (3.0, '3')]:
        a3.vlines(x, 0.35, 0.45, color=COLORS['charcoal'], lw=px_to_pt(2.0, dpi))
        a3.text(x, 0.2, lab, ha='center', va='center', fontsize=14)
        # tiny cartoons above each tick
        _draw_plane_wave_cartoon(a3, x, 0.7)
    a3.text(0.02, 0.92, 'optical thickness kδ', transform=a3.transAxes, fontsize=14,
            ha='left', va='top')


def _style_micro_axes(a: plt.Axes) -> None:
    a.set_xticks([])
    a.set_yticks([])
    for s in a.spines.values():
        s.set_visible(False)


def _draw_plane_wave_cartoon(a: plt.Axes, cx: float, cy: float) -> None:
    # Draw 3 plane-wave crests as short horizontal lines
    dx = 0.22
    spacing = 0.03
    for i in range(3):
        a.hlines(cy + i * spacing, cx - dx * 0.8, cx + dx * 0.8, color=COLORS['charcoal'], lw=1.2)


def _draw_legend_box(ax: plt.Axes, panel_rect, dpi: int) -> None:
    left, bottom, width, height = panel_rect
    lx = left + width - 0.23
    ly = bottom + 0.08
    lw = px_to_pt(2.0, dpi)
    # Framelss legend: just samples + text (no box)
    # Orange line sample
    ax.plot([lx, lx + 0.06], [ly + 0.06, ly + 0.06], transform=ax.transAxes, color=COLORS['orange'], lw=px_to_pt(3.0, dpi))
    ax.text(lx + 0.07, ly + 0.06, 'acoustic rays', transform=ax.transAxes, va='center', fontsize=16)
    # Magenta translucent swatch
    ax.add_patch(Rectangle((lx, ly - 0.005), 0.06, 0.028, transform=ax.transAxes, facecolor=COLORS['magenta'], alpha=0.20, edgecolor='none'))
    ax.text(lx + 0.07, ly + 0.01, r"finite-thickness interface $\delta$", transform=ax.transAxes, va='center', fontsize=16)
    # Small note
    ax.text(lx, ly - 0.04, r"Amplitude/phase evolve via $k_z\,\delta$ inside the band", transform=ax.transAxes, fontsize=14)


def draw_figure(ax: plt.Axes, dpi: int = 300) -> None:
    panel_rect = _draw_water_column(ax, dpi)
    band_y, band_th = _draw_interface_band(ax, panel_rect, dpi)
    _draw_layer_tags(ax, panel_rect, band_y, band_th)
    _draw_source_and_rays(ax, panel_rect, band_y, band_th, dpi)
    _draw_microplots(ax, dpi)
    _draw_legend_box(ax, panel_rect, dpi)

    # Title inside panel area (panel title per house style)
    ax.text(0.05, 0.93, 'Finite-thickness interface geometry and controls', transform=ax.transAxes,
            fontsize=28, fontweight='bold', ha='left', va='top')


def generate(out_base: str, export_svg: bool = True, export_pdf: bool = True,
             export_png: bool = True, dpi: int = 300) -> None:
    spec = CanvasSpec(dpi=dpi)
    fig, ax = new_canvas(spec)
    draw_figure(ax, dpi=dpi)
    add_caption(
        fig,
        "Figure 3.5A. Geometry of a finite-thickness interface with contrast ($A_t$, $C_Z$), "
        "incidence $\theta$, and phase-thickness $k_z\,\delta$. Multiple internal traversals generate "
        "frequency- and angle-dependent R/T.",
        spec,
    )
    save_figure(fig, out_base, export_svg=export_svg, export_pdf=export_pdf, export_png=export_png, dpi=dpi)
    plt.close(fig)
