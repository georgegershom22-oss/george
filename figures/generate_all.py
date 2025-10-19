from __future__ import annotations

import argparse
from pathlib import Path

from .fig_35a import generate as gen_35a
from .fig_35b import generate as gen_35b
from .fig_35c import generate as gen_35c


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate Figures 3.5A–C with house style")
    p.add_argument("outdir", type=Path, help="Output directory for figures")
    p.add_argument("--dpi", type=int, default=300)
    p.add_argument("--no-svg", action="store_true")
    p.add_argument("--no-pdf", action="store_true")
    p.add_argument("--no-png", action="store_true")
    p.add_argument("--tight-focus", action="store_true", help="Use 0.2–2.2 x-range for 3.5B")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    export_svg = not args.no_svg
    export_pdf = not args.no_pdf
    export_png = not args.no_png

    gen_35a(args.outdir / "fig_3_5A", export_svg=export_svg, export_pdf=export_pdf, export_png=export_png, dpi=args.dpi)
    gen_35b(args.outdir / "fig_3_5B", tight_focus=args.tight_focus, export_svg=export_svg, export_pdf=export_pdf, export_png=export_png, dpi=args.dpi)
    gen_35c(args.outdir / "fig_3_5C", export_svg=export_svg, export_pdf=export_pdf, export_png=export_png, dpi=args.dpi)


if __name__ == "__main__":
    main()
