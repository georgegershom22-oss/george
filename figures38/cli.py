from __future__ import annotations

import argparse
import os
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")  # non-interactive backend for batch rendering

from .house_style import apply_house_style
from . import fig38a, fig38b, fig38c, fig38d


FORMATS = ["pdf", "svg", "png"]
DEFAULT_DPI = 200  # ensures 2000x1400 px for PNG given figsize


def _save(fig, out_base: Path, formats: list[str]):
    out_base.parent.mkdir(parents=True, exist_ok=True)
    for ext in formats:
        path = out_base.with_suffix(f".{ext}")
        if ext == "png":
            fig.savefig(path, dpi=DEFAULT_DPI)
        else:
            # keep text as text in vector outputs
            mpl.rcParams.update({
                "svg.fonttype": "none",
                "pdf.fonttype": 42,
                "ps.fonttype": 42,
            })
            fig.savefig(path)
        print(f"Saved {path}")


def render(which: str, outdir: str, formats: list[str]):
    apply_house_style()
    out_dir = Path(outdir)

    mapping = {
        "A": (fig38a.plot, "fig_3_8A"),
        "B": (fig38b.plot, "fig_3_8B"),
        "C": (fig38c.plot, "fig_3_8C"),
        "D": (fig38d.plot, "fig_3_8D"),
    }

    if which.lower() == "all":
        keys = ["A", "B", "C", "D"]
    else:
        keys = [which.upper()]

    for k in keys:
        plot_func, name = mapping[k]
        fig, _ = plot_func()
        _save(fig, out_dir / name, formats)
        # Avoid memory accumulation
        import matplotlib.pyplot as plt

        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Render Figures 3.8A–D with shared house style")
    parser.add_argument("which", help="Which figure to render: A, B, C, D, or 'all'", default="all", nargs="?")
    parser.add_argument("--outdir", default="outputs", help="Output directory")
    parser.add_argument("--formats", default=",".join(FORMATS), help="Comma-separated: pdf,svg,png")
    args = parser.parse_args()

    fmts = [f.strip() for f in args.formats.split(",") if f.strip() in FORMATS]
    if not fmts:
        fmts = FORMATS

    render(args.which, args.outdir, fmts)


if __name__ == "__main__":
    main()
