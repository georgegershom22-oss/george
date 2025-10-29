from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class ParameterRanges:
    # Operating conditions
    voltage_V: Tuple[float, float] = (0.6, 0.9)
    current_density_A_per_cm2: Tuple[float, float] = (0.1, 1.5)  # overall target average
    air_flow_sLpm: Tuple[float, float] = (1.0, 10.0)
    fuel_flow_sLpm: Tuple[float, float] = (0.5, 5.0)
    air_inlet_T_K: Tuple[float, float] = (973.15, 1173.15)  # 700C to 900C
    fuel_inlet_T_K: Tuple[float, float] = (973.15, 1173.15)

    # Material properties per layer (min, max). Layers: anode, electrolyte, cathode, interconnect, sealant
    # Effective properties for porous electrodes where applicable
    porosity: Tuple[float, float] = (0.25, 0.45)
    permeability_m2: Tuple[float, float] = (1e-14, 1e-12)
    ionic_conductivity_S_per_m: Tuple[float, float] = (5.0, 20.0)  # electrolyte
    electronic_conductivity_S_per_m: Tuple[float, float] = (1e4, 2e5)
    youngs_modulus_GPa: Tuple[float, float] = (50.0, 210.0)
    cte_1_per_K: Tuple[float, float] = (8e-6, 13e-6)
    poisson_ratio: Tuple[float, float] = (0.22, 0.35)
    thermal_conductivity_W_per_mK: Tuple[float, float] = (2.0, 15.0)

    # Geometry
    anode_thickness_um: Tuple[float, float] = (200.0, 800.0)
    electrolyte_thickness_um: Tuple[float, float] = (5.0, 30.0)
    cathode_thickness_um: Tuple[float, float] = (50.0, 200.0)
    interconnect_thickness_um: Tuple[float, float] = (500.0, 1500.0)
    sealant_thickness_um: Tuple[float, float] = (100.0, 300.0)
    active_area_mm: Tuple[float, float] = (10.0, 40.0)  # square: side length
    num_flow_channels: Tuple[int, int] = (3, 9)

    # Kinetics (for surrogate electrochem): exchange current density and transfer coefficient
    i0_A_per_cm2: Tuple[float, float] = (0.01, 0.5)
    alpha: Tuple[float, float] = (0.3, 0.7)


LAYER_ORDER = ["anode", "electrolyte", "cathode", "interconnect", "sealant"]


def default_ranges() -> ParameterRanges:
    return ParameterRanges()
