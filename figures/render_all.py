from __future__ import annotations

import os

from .fig_3_7a import plot_a
from .fig_3_7b_common import plot_b1, plot_b2
from .fig_3_7c1 import plot_c1
from .house_style import apply_rc_params


OUT_DIR = os.path.join(os.path.dirname(__file__), 'out')


def main() -> None:
    apply_rc_params()

    os.makedirs(OUT_DIR, exist_ok=True)
    # 3.7A
    plot_a(os.path.join(OUT_DIR, 'figure_3_7A'))
    # 3.7B1
    plot_b1(os.path.join(OUT_DIR, 'figure_3_7B1'))
    # 3.7B2
    plot_b2(os.path.join(OUT_DIR, 'figure_3_7B2'))
    # 3.7C1
    plot_c1(os.path.join(OUT_DIR, 'figure_3_7C1'))


if __name__ == '__main__':
    main()
