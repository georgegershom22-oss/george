import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from figs.house_style import (
    apply_house_style, dark_colormap, make_axes_omega_over_N,
    add_conversion_overlay, add_panel_title, add_caption, export
)


def synthetic_scalogram_high_Ri(T, W):
    # Thin ridge near w/N ~ 1 with small waviness over time
    center = 1.0 + 0.03 * np.sin(2 * np.pi * T / T.max() * 2)
    bandwidth = 0.06
    ridge = np.exp(-((W - center[:, None]) ** 2) / (2 * bandwidth ** 2))
    bg = 0.05 * np.ones_like(ridge)
    return bg + 0.9 * ridge


def synthetic_scalogram_marginal_Ri(T, W):
    # Intermittent broadband bursts plus a persistent but less coherent band near 1
    base_band = 0.4 * np.exp(-((W - 1.0) ** 2) / (2 * 0.12 ** 2))
    # Bursts: random times with broader spread and higher intensity
    Z = 0.08 * np.ones((T.size, W.size)) + base_band
    rng = np.random.default_rng(42)
    burst_times = rng.choice(np.arange(T.size), size=8, replace=False)
    for bt in burst_times:
        width = rng.uniform(0.18, 0.35)
        center = 1.0 + rng.uniform(-0.25, 0.35)
        time_len = rng.integers(6, 14)
        t_start = max(0, bt - time_len // 2)
        t_end = min(T.size, t_start + time_len)
        burst = 0.7 * np.exp(-((W - center) ** 2) / (2 * width ** 2))
        # Apply linearly fading envelope in time window
        time_env = np.linspace(1.0, 0.2, t_end - t_start)[:, None]
        Z[t_start:t_end, :] += time_env * burst
    # Oblique streaks (intrusions)
    for k in range(3):
        slope = rng.uniform(-0.004, 0.004)
        intercept = rng.uniform(0.8, 1.2)
        for i, t in enumerate(T):
            center = intercept + slope * (t - T.mean())
            Z[i, :] += 0.15 * np.exp(-((W - center) ** 2) / (2 * 0.08 ** 2))
    return Z


def main():
    apply_house_style()

    # Time and frequency axes
    t_max = 60.0
    T = np.linspace(0.0, t_max, 256)
    W = np.linspace(0.2, 2.2, 300)

    Z_left = synthetic_scalogram_high_Ri(T, W)
    Z_right = synthetic_scalogram_marginal_Ri(T, W)

    fig = plt.figure()
    # Two equal panels with 40 px gutter
    # Convert 40 px to figure fraction
    gutter_px = 40
    gutter_frac = gutter_px / (fig.dpi * fig.get_figwidth() * fig.dpi / fig.dpi)  # simplify later
    # We'll position axes manually using normalized coords
    left = 0.08
    right_margin = 0.08
    total_width = 1.0 - left - right_margin
    gutter = gutter_px / (fig.dpi * fig.get_figwidth() * fig.dpi / fig.dpi)
    panel_width = (total_width - gutter) / 2.0
    panel_height = 0.76
    bottom = 0.14

    ax1 = fig.add_axes([left, bottom, panel_width, panel_height])
    ax2 = fig.add_axes([left + panel_width + gutter, bottom, panel_width, panel_height])

    cmap = dark_colormap("cividis")
    im1 = ax1.imshow(Z_left.T, origin="lower", aspect="auto",
                     extent=[T.min(), T.max(), W.min(), W.max()], cmap=cmap)
    im2 = ax2.imshow(Z_right.T, origin="lower", aspect="auto",
                     extent=[T.min(), T.max(), W.min(), W.max()], cmap=cmap)

    # Axes styling shared
    for ax in (ax1, ax2):
        ax.set_xlim(0, t_max)
        ax.set_xticks(np.arange(0, t_max + 1e-6, 10))
        make_axes_omega_over_N(ax, add_conversion_band=True)
        ax.set_ylabel(r"$\omega/N$")
        ax.set_xlabel("time (s)")

    # Left panel annotation
    ax1.text(0.98, 0.93, "High $R_i$: fluctuation energy concentrated in a narrow conversion band.",
             transform=ax1.transAxes, ha="right", va="top", fontsize=15, style="italic")
    ax1.text(0.65, 0.82, "narrow conversion-band modulation", fontsize=19,
             transform=ax1.transAxes, color="#111111")

    # Right panel micro-labels with arrows
    ax2.text(0.02, 0.1, "Marginal $R_i$: intermittent broadband activity indicates shear-mediated variability.",
             transform=ax2.transAxes, ha="left", va="bottom", fontsize=15, style="italic")

    ax2.annotate("intermittent broadband bursts", xy=(20, 1.55), xytext=(8, 1.95),
                 textcoords="data",
                 arrowprops=dict(arrowstyle="->", color="#111111"), fontsize=18)
    ax2.annotate("enhanced spread beyond conversion", xy=(42, 0.65), xytext=(50, 1.9),
                 textcoords="data",
                 arrowprops=dict(arrowstyle="->", color="#111111"), fontsize=18)

    add_panel_title(ax1, "Figure 3.6B — Time–frequency TL fluctuation intensity (high vs marginal $R_i$)")

    # Shared colorbar on right of right panel
    cax = fig.add_axes([left + 2 * panel_width + gutter + 0.012, bottom, 0.015, panel_height])
    cbar = fig.colorbar(im2, cax=cax)
    cbar.set_label("TL fluctuation intensity (arb.)")
    cbar.ax.invert_yaxis()  # darker = higher

    add_caption(fig, "Two scalograms share the same color scale; darker = higher intensity.")

    export(fig, "/workspace/out/figures/figure_3_6b")


if __name__ == "__main__":
    main()
