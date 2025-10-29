from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


# Physical constants
FARADAY_CONSTANT = 96485.33212  # C/mol
GAS_CONSTANT = 8.314462618  # J/(mol*K)


@dataclass(frozen=True)
class LayerNames:
    ANODE: str = "anode"
    ELECTROLYTE: str = "electrolyte"
    CATHODE: str = "cathode"


LAYER_ORDER = [LayerNames.ANODE, LayerNames.ELECTROLYTE, LayerNames.CATHODE]


@dataclass
class OperatingRanges:
    voltage_V: Tuple[float, float] = (0.6, 0.9)
    current_density_A_per_cm2: Tuple[float, float] = (0.1, 1.5)
    air_flow_rate_m3_per_s: Tuple[float, float] = (1e-4, 1e-3)
    fuel_flow_rate_m3_per_s: Tuple[float, float] = (5e-5, 5e-4)
    inlet_T_air_K: Tuple[float, float] = (973.0, 1173.0)  # 700C to 900C
    inlet_T_fuel_K: Tuple[float, float] = (973.0, 1173.0)


@dataclass
class GeometryRanges:
    # Thickness ranges (meters)
    thickness_anode_m: Tuple[float, float] = (300e-6, 800e-6)
    thickness_electrolyte_m: Tuple[float, float] = (8e-6, 25e-6)
    thickness_cathode_m: Tuple[float, float] = (30e-6, 100e-6)
    # Active area (m^2) nominally 5x5 cm^2
    active_area_m2: Tuple[float, float] = (0.002, 0.003)  # 20-30 cm^2


@dataclass
class MaterialRanges:
    # Porosity (dimensionless 0-1)
    porosity: Dict[str, Tuple[float, float]] = None
    # Permeability (m^2)
    permeability: Dict[str, Tuple[float, float]] = None
    # Electronic conductivity (S/m)
    sigma_electronic: Dict[str, Tuple[float, float]] = None
    # Ionic conductivity (S/m)
    sigma_ionic: Dict[str, Tuple[float, float]] = None
    # Thermal conductivity (W/m/K)
    k_thermal: Dict[str, Tuple[float, float]] = None
    # Young's modulus (Pa)
    youngs_modulus: Dict[str, Tuple[float, float]] = None
    # Poisson's ratio (-)
    poisson_ratio: Dict[str, Tuple[float, float]] = None
    # Coefficient of thermal expansion (1/K)
    cte: Dict[str, Tuple[float, float]] = None
    # Exchange current density (A/m^2) for reaction kinetics at interfaces
    j0_exchange: Dict[str, Tuple[float, float]] = None

    def __post_init__(self) -> None:
        if self.porosity is None:
            self.porosity = {
                LayerNames.ANODE: (0.25, 0.45),
                LayerNames.ELECTROLYTE: (0.00, 0.05),
                LayerNames.CATHODE: (0.25, 0.40),
            }
        if self.permeability is None:
            self.permeability = {
                LayerNames.ANODE: (2e-12, 2e-11),
                LayerNames.ELECTROLYTE: (1e-20, 1e-19),
                LayerNames.CATHODE: (5e-13, 5e-12),
            }
        if self.sigma_electronic is None:
            self.sigma_electronic = {
                LayerNames.ANODE: (5e4, 2e5),     # S/m (e.g., Ni-YSZ cermet)
                LayerNames.ELECTROLYTE: (1.0, 5.0),  # nearly insulating electronically
                LayerNames.CATHODE: (1e4, 8e4),  # LSM/LSCF composite range
            }
        if self.sigma_ionic is None:
            self.sigma_ionic = {
                LayerNames.ANODE: (0.1, 5.0),
                LayerNames.ELECTROLYTE: (50.0, 250.0),  # YSZ ionic conductivity at high T
                LayerNames.CATHODE: (0.5, 10.0),
            }
        if self.k_thermal is None:
            self.k_thermal = {
                LayerNames.ANODE: (5.0, 15.0),
                LayerNames.ELECTROLYTE: (2.0, 3.0),
                LayerNames.CATHODE: (3.0, 7.0),
            }
        if self.youngs_modulus is None:
            self.youngs_modulus = {
                LayerNames.ANODE: (80e9, 160e9),
                LayerNames.ELECTROLYTE: (150e9, 220e9),
                LayerNames.CATHODE: (100e9, 180e9),
            }
        if self.poisson_ratio is None:
            self.poisson_ratio = {
                LayerNames.ANODE: (0.25, 0.31),
                LayerNames.ELECTROLYTE: (0.25, 0.31),
                LayerNames.CATHODE: (0.25, 0.31),
            }
        if self.cte is None:
            self.cte = {
                LayerNames.ANODE: (11e-6, 14e-6),
                LayerNames.ELECTROLYTE: (9e-6, 11e-6),
                LayerNames.CATHODE: (11e-6, 13e-6),
            }
        if self.j0_exchange is None:
            self.j0_exchange = {
                LayerNames.ANODE: (5e3, 5e4),      # A/m^2
                LayerNames.CATHODE: (1e3, 2e4),    # A/m^2
                # No j0 for electrolyte
            }


DEFAULT_OPERATING_RANGES = OperatingRanges()
DEFAULT_GEOMETRY_RANGES = GeometryRanges()
DEFAULT_MATERIAL_RANGES = MaterialRanges()
