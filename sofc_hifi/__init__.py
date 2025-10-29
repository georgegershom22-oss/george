"""SOFC High-Fidelity Synthetic Dataset Generator.

Provides tools to generate physics-informed synthetic multi-physics fields
for solid oxide fuel cell (SOFC) cells or stacks, including:
- Electrochemical potential and current density
- Thermal temperature distributions
- Species (H2, H2O) fields in the anode
- Thermo-mechanical stress, strain, and displacement approximations

All outputs are written as HDF5 files per simulation sample.
"""

__all__ = [
    "__version__",
]

__version__ = "0.1.0"
