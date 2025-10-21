from __future__ import annotations

from typing import Tuple

import numpy as np
from matplotlib.colors import LinearSegmentedColormap


# Colors
AMBER = "#F4A261"
TEAL = "#2A9D8F"
LIGHT_NEUTRAL = "#F3F4F6"  # very light gray midpoint


def dominance_cmap() -> LinearSegmentedColormap:
    """Amber (0) -> light neutral (0.5) -> teal (1). Darker at endpoints."""
    return LinearSegmentedColormap.from_list(
        "amber_neutral_teal",
        [
            (0.0, AMBER),
            (0.5, LIGHT_NEUTRAL),
            (1.0, TEAL),
        ],
        N=256,
    )


def strength_cmap() -> LinearSegmentedColormap:
    """Monotone light -> dark for strengths; reuse teal as dark endpoint."""
    return LinearSegmentedColormap.from_list(
        "strength_light_dark",
        ["#F8FAFC", "#CBD5E1", "#475569", TEAL],
        N=256,
    )
