import matplotlib as mpl
import matplotlib.pyplot as plt

# Shared house style constants
COLORS = {
    "classical": "#6B7280",       # neutral dark grey
    "conversion": "#F4A261",      # amber (translucent band)
    "conversion_dark": "#C06A00", # darker amber for curves if needed
    "interfacial": "#6A4C93",     # purple
    "shear": "#2A9D8F",          # teal
    "grid": "#E5E7EB",           # light grey grid
    "dotted": "#9CA3AF",         # dotted guide line color
}

# Typography
TITLE_SIZE = 28
LABEL_SIZE = 22
TICK_SIZE = 16
NOTE_SIZE = 19
CAPTION_SIZE = 15
LEGEND_SIZE = 17

# Line widths: points (pt); ~0.75 pt ≈ 1 px at ~96–100 dpi
LW_PRIMARY = 2.25   # ~3 px
LW_SECONDARY = 1.8  # ~2.4 px
LW_DOTTED = 0.9     # ~1.2 px
LW_GRID = 0.6       # ~0.8 px

# Figure dimensions in inches for 2000x1400 px at 100 dpi
FIG_DPI = 100
FIG_SIZE = (2000 / FIG_DPI, 1400 / FIG_DPI)


def configure_matplotlib() -> None:
    """Apply global rcParams according to the house style."""
    mpl.rcParams.update({
        "figure.dpi": FIG_DPI,
        "savefig.dpi": FIG_DPI,
        "figure.facecolor": "#FFFFFF",
        "axes.facecolor": "#FFFFFF",
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "Liberation Sans"],
        "axes.titlesize": TITLE_SIZE,
        "axes.labelsize": LABEL_SIZE,
        "xtick.labelsize": TICK_SIZE,
        "ytick.labelsize": TICK_SIZE,
        "legend.fontsize": LEGEND_SIZE,
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
        "axes.grid": False,
        "grid.color": COLORS["grid"],
        "grid.linewidth": LW_GRID,
        "grid.alpha": 1.0,
    })


def new_figure(title: str | None = None) -> plt.Figure:
    fig = plt.figure(figsize=FIG_SIZE, dpi=FIG_DPI)
    if title:
        fig.suptitle(title, fontweight="bold", x=0.02, ha="left", y=0.98)
    return fig


def style_axes_common(ax: plt.Axes, xlabel: str = "", ylabel: str = "",
                      xlim: tuple | None = None, ylim: tuple | None = None,
                      xticks: list | None = None, yticks: list | None = None,
                      show_grid: bool = True) -> None:
    if xlim:
        ax.set_xlim(*xlim)
    if ylim:
        ax.set_ylim(*ylim)
    if xticks is not None:
        ax.set_xticks(xticks)
    if yticks is not None:
        ax.set_yticks(yticks)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    # Grid - major only
    if show_grid:
        ax.grid(True, which="major", axis="both")
    # Turn off top/right spines for cleaner look
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)


def add_conversion_window(ax: plt.Axes, x0: float = 0.8, x1: float = 1.2,
                          y0: float | None = None, y1: float | None = None) -> None:
    """Amber translucent band and dotted centerline at x=1 for frequency panels."""
    if y0 is None or y1 is None:
        y0, y1 = ax.get_ylim()
    ax.axvspan(x0, x1, color=COLORS["conversion"], alpha=0.20, zorder=0)
    ax.axvline(1.0, color=COLORS["dotted"], linewidth=LW_DOTTED,
               linestyle=(0, (1.5, 3.0)), zorder=1)


def inside_legend(ax: plt.Axes, handles_labels: list[tuple], loc: str = "upper right") -> None:
    handles, labels = zip(*handles_labels)
    ax.legend(handles, labels, loc=loc, frameon=False)


def add_caption(fig: plt.Figure, text: str) -> None:
    fig.text(0.5, 0.02, text, ha="center", va="bottom",
             fontsize=CAPTION_SIZE, fontstyle="italic")
