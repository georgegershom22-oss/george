from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch

from .house_style import (
    apply_rc_params,
    new_figure,
    save_figure,
    COLORS,
    FONT_SIZES,
    PRIMARY_LW,
    SECONDARY_LW,
    DASH,
    add_caption,
)


def _rounded_box(ax, x, y, w, h, label=None, fontsize=None):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=10",
                         linewidth=1.5, edgecolor='black', facecolor='white')
    ax.add_patch(box)
    if label:
        ax.text(x + w/2, y + h - 0.06, label, ha='center', va='top', fontsize=fontsize or FONT_SIZES['axis_label'], weight='bold')
    return box


def _arrow(ax, x1, y1, x2, y2, color='black', lw=1.5, style='simple'): 
    arr = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='->', mutation_scale=12,
                          linewidth=lw, color=color)
    ax.add_patch(arr)


def plot_a(out_base: str) -> None:
    apply_rc_params()
    fig = new_figure()
    # Use a full-canvas axes in normalized (0..1) coordinates; turn off
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()

    # Layout constants (normalized by 2000x1400 canvas)
    # Left inputs column ~300 px wide
    px_w, px_h = 2000.0, 1400.0
    def nx(px):
        return px / px_w
    def ny(px):
        return px / px_h

    margin_l = nx(100)
    margin_r = nx(110)
    column_w_inputs = nx(300)
    column_w_outputs = nx(360)

    # Inputs box
    inputs_x = margin_l
    inputs_y = ny(220)
    inputs_h = ny(760)
    inputs_box = _rounded_box(ax, inputs_x, inputs_y, column_w_inputs, inputs_h, label='Inputs', fontsize=FONT_SIZES['axis_label'])

    # Inputs list with bullets and thin arrows to center module
    items = [
        ("ω/N (frequency ratio)",),
        ("Ri (stability)",),
        ("kδ (interface optical thickness)",),
        ("CZ, At",),
        ("θ (incidence), r (range)",),
    ]
    bullet_r = ny(8)
    line_y = inputs_y + inputs_h - ny(110)
    line_x = inputs_x + nx(24)
    line_gap = ny(120)

    for idx, (label,) in enumerate(items):
        cy = line_y - idx * line_gap
        cx = line_x
        ax.add_patch(Circle((cx, cy), bullet_r, facecolor='black', edgecolor='none'))
        # Label
        ax.text(cx + nx(20), cy, label, ha='left', va='center', fontsize=FONT_SIZES['note'])
        # Thin arrow to center module
        _arrow(ax, inputs_x + column_w_inputs + nx(10), cy, nx(980), cy, color='black', lw=1.5)

    # Add small 'contrast' tag near CZ, At
    ax.add_patch(Rectangle((nx(320), line_y - 3 * line_gap - ny(18)), nx(90), ny(30), facecolor='#F3F4F6', edgecolor='#9CA3AF', linewidth=1.0))
    ax.text(nx(320 + 45), line_y - 3 * line_gap - ny(3), 'contrast', ha='center', va='top', fontsize=FONT_SIZES['tick'])

    # Similarity space cue (center-top ~520x320 px)
    sim_w = nx(520)
    sim_h = ny(320)
    sim_x = nx(740)
    sim_y = ny(960)
    sim = _rounded_box(ax, sim_x, sim_y, sim_w, sim_h, label='Similarity space (Ri vs ω/N)')

    sim_ax = fig.add_axes([sim_x, sim_y, sim_w, sim_h])
    sim_ax.set_xlim(0.2, 2.2)
    sim_ax.set_ylim(0.0, 2.0)
    sim_ax.set_xlabel('ω/N')
    sim_ax.set_ylabel('Ri')
    sim_ax.tick_params(labelsize=FONT_SIZES['tick'])
    sim_ax.grid(True, color='#E5E7EB', linewidth=0.8)
    # soft regions: conversion belt, shear-favored, near-classical
    sim_ax.add_patch(Rectangle((0.8, 0.0), 0.4, 2.0, facecolor=COLORS['conversion'], alpha=0.15, edgecolor='none'))
    sim_ax.add_patch(Rectangle((0.6, 0.0), 1.0, 0.5, facecolor=COLORS['shear'], alpha=0.12, edgecolor='none'))
    sim_ax.add_patch(Rectangle((0.2, 1.2), 2.0, 0.8, facecolor=COLORS['classical'], alpha=0.10, edgecolor='none'))
    sim_ax.text(1.0, 1.8, 'near-classical', color=COLORS['classical'], ha='center', va='center', fontsize=FONT_SIZES['tick'])
    sim_ax.text(1.0, 0.25, 'shear-favored', color=COLORS['shear'], ha='center', va='center', fontsize=FONT_SIZES['tick'])
    sim_ax.text(1.0, 1.1, 'conversion belt', color=COLORS['conversion_dark'], ha='center', va='center', fontsize=FONT_SIZES['tick'])

    # Mechanism weighting module (center-middle ~560x260 px)
    mw_w = nx(560)
    mw_h = ny(260)
    mw_x = nx(720)
    mw_y = ny(560)
    mw_box = _rounded_box(ax, mw_x, mw_y, mw_w, mw_h, label='Mechanism weighting (shares sum to 1)')

    # Inside: 100% stacked horizontal bar (sample shares)
    gauge_margin = ny(50)
    gx0 = mw_x + nx(30)
    gy0 = mw_y + gauge_margin
    g_w = mw_w - nx(60)
    g_h = ny(40)
    # sample shares
    s_class, s_conv, s_interf, s_shear = 0.36, 0.44, 0.08, 0.12
    # classical
    ax.add_patch(Rectangle((gx0, gy0), g_w * s_class, g_h, facecolor=COLORS['classical'], edgecolor='none'))
    # conversion
    ax.add_patch(Rectangle((gx0 + g_w * s_class, gy0), g_w * s_conv, g_h, facecolor=COLORS['conversion'], edgecolor='none'))
    # interfacial
    ax.add_patch(Rectangle((gx0 + g_w * (s_class + s_conv), gy0), g_w * s_interf, g_h, facecolor=COLORS['interfacial'], edgecolor='none'))
    # shear
    ax.add_patch(Rectangle((gx0 + g_w * (s_class + s_conv + s_interf), gy0), g_w * s_shear, g_h, facecolor=COLORS['shear'], edgecolor='none'))

    ax.text(gx0, gy0 + g_h + ny(20), 'Classical   Conversion   Interfacial   Shear-mediated', fontsize=FONT_SIZES['note'], ha='left', va='bottom')
    ax.text(mw_x + mw_w - nx(20), mw_y + ny(20), '∑wi=1', fontsize=FONT_SIZES['note'], ha='right', va='bottom')
    ax.text(mw_x + nx(30), mw_y + ny(20), 'shares guided by §3.2 similarity & §3.4–3.6 scalings', fontsize=FONT_SIZES['tick'], ha='left', va='bottom')

    # Combination node (center-bottom)
    node_x = mw_x + mw_w/2
    node_y = ny(430)
    ax.add_patch(Circle((node_x, node_y), ny(32), facecolor='white', edgecolor='black', linewidth=1.2))
    ax.text(node_x, node_y, 'Σ', ha='center', va='center', fontsize=FONT_SIZES['axis_label'], weight='bold')
    ax.text(node_x, node_y - ny(48), 'Composite attenuation', ha='center', va='top', fontsize=FONT_SIZES['note'])
    _arrow(ax, node_x, mw_y, node_x, node_y + ny(28), lw=2.0)

    # Priors dotted back-arrow to the weighting box
    ax.annotate('priors', xy=(mw_x + nx(40), mw_y + mw_h + ny(10)), xytext=(mw_x - nx(140), mw_y + ny(20)),
                arrowprops=dict(arrowstyle='->', linestyle=DASH['dotted'], color='#374151', lw=1.8), fontsize=FONT_SIZES['note'])

    # Posterior solid arrow to outputs
    outputs_x = 1 - margin_r - column_w_outputs
    outputs_y = ny(240)
    outputs_h = ny(820)
    outputs_box = _rounded_box(ax, outputs_x, outputs_y, column_w_outputs, outputs_h, label='Predicted / measured outputs')
    _arrow(ax, node_x + nx(20), node_y, outputs_x - nx(20), node_y, lw=2.2)

    # Outputs icons
    # TL(ω) curve icon
    ax.text(outputs_x + nx(20), outputs_y + outputs_h - ny(110), 'TL(ω)', fontsize=FONT_SIZES['note'], ha='left', va='center')
    ax.add_patch(Rectangle((outputs_x + nx(20), outputs_y + outputs_h - ny(200)), nx(300), ny(80), facecolor='white', edgecolor='#9CA3AF'))
    ax.plot([outputs_x + nx(30), outputs_x + nx(300)], [outputs_y + outputs_h - ny(180), outputs_y + outputs_h - ny(140)], color='#111827', linewidth=2.0)
    # γ²(ω) icon with dip near 1
    ax.text(outputs_x + nx(20), outputs_y + outputs_h - ny(320), 'γ²(ω)', fontsize=FONT_SIZES['note'], ha='left', va='center')
    ax.add_patch(Rectangle((outputs_x + nx(20), outputs_y + outputs_h - ny(410)), nx(300), ny(80), facecolor='white', edgecolor='#9CA3AF'))
    ax.plot([outputs_x + nx(30), outputs_x + nx(120), outputs_x + nx(210), outputs_x + nx(300)],
            [outputs_y + outputs_h - ny(360), outputs_y + outputs_h - ny(390), outputs_y + outputs_h - ny(340), outputs_y + outputs_h - ny(330)],
            color='#111827', linewidth=2.0)
    # PSD(ω) width icon
    ax.text(outputs_x + nx(20), outputs_y + outputs_h - ny(520), 'PSD(ω)', fontsize=FONT_SIZES['note'], ha='left', va='center')
    ax.add_patch(Rectangle((outputs_x + nx(20), outputs_y + outputs_h - ny(610)), nx(300), ny(80), facecolor='white', edgecolor='#9CA3AF'))
    ax.plot([outputs_x + nx(60), outputs_x + nx(120), outputs_x + nx(180), outputs_x + nx(240)],
            [outputs_y + outputs_h - ny(560), outputs_y + outputs_h - ny(520), outputs_y + outputs_h - ny(560), outputs_y + outputs_h - ny(520)],
            color='#111827', linewidth=2.0)

    # Design implications note
    ax.annotate('Design implications: Choose ω, θ, Ri, kδ to target mechanisms; update priors with data.',
                xy=(outputs_x + column_w_outputs - nx(20), outputs_y + ny(40)), xytext=(outputs_x + column_w_outputs - nx(20), outputs_y - ny(40)),
                ha='right', va='top', fontsize=FONT_SIZES['note'], arrowprops=dict(arrowstyle='->'))

    # Legend (bottom-right)
    lx = outputs_x + nx(20)
    ly = ny(120)
    sw = nx(30)
    gap = nx(12)
    entries = [
        (COLORS['classical'], 'Classical'),
        (COLORS['conversion'], 'Mode conversion'),
        (COLORS['interfacial'], 'Interfacial'),
        (COLORS['shear'], 'Shear-mediated'),
    ]
    ax.text(lx, ly + ny(40), 'Legend', fontsize=FONT_SIZES['legend'], ha='left', va='bottom')
    for i, (c, label) in enumerate(entries):
        y = ly - i * ny(34)
        ax.add_patch(Rectangle((lx, y), sw, ny(18), facecolor=c, edgecolor='none'))
        ax.text(lx + sw + gap, y + ny(9), label, ha='left', va='center', fontsize=FONT_SIZES['legend'])

    # Caption inside canvas
    add_caption(fig, (
        "Figure 3.7A. Composite attenuation concept. Similarity variables feed a mechanism-weighting module that yields shares "
        "summing to unity; these combine into a composite prediction of attenuation and observables used to set priors and design experiments."
    ))

    save_figure(fig, out_base)
    plt.close(fig)
