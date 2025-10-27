#!/usr/bin/env python3
from pathlib import Path
import sys
import os

# Ensure src/ is importable when running from repo root
CURR = Path(__file__).resolve()
ROOT = CURR.parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from welding_inverse_design_dataset.dataset_generator import main

if __name__ == "__main__":
    main()
