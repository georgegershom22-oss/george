from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class Material:
    name: str
    thermal_conductivity_W_mK: float
    specific_heat_J_kgK: float
    density_kg_m3: float
    melting_point_C: float
    cte_1e6_per_K: float
    electrical_resistivity_uOhm_m: float
    laser_absorptivity_1: float
    ultrasonic_absorption_factor: float
    default_tab_thickness_um: float

MATERIALS: Dict[str, Material] = {
    # Representative values; not precise for any specific alloy temper
    "Copper_Cu": Material(
        name="Copper_Cu",
        thermal_conductivity_W_mK=385.0,
        specific_heat_J_kgK=385.0,
        density_kg_m3=8960.0,
        melting_point_C=1085.0,
        cte_1e6_per_K=16.5,
        electrical_resistivity_uOhm_m=1.68,
        laser_absorptivity_1=0.3,
        ultrasonic_absorption_factor=0.9,
        default_tab_thickness_um=100.0,
    ),
    "Aluminum_1100": Material(
        name="Aluminum_1100",
        thermal_conductivity_W_mK=237.0,
        specific_heat_J_kgK=900.0,
        density_kg_m3=2700.0,
        melting_point_C=660.0,
        cte_1e6_per_K=23.6,
        electrical_resistivity_uOhm_m=2.82,
        laser_absorptivity_1=0.2,
        ultrasonic_absorption_factor=0.85,
        default_tab_thickness_um=120.0,
    ),
    "Aluminum_1050": Material(
        name="Aluminum_1050",
        thermal_conductivity_W_mK=230.0,
        specific_heat_J_kgK=900.0,
        density_kg_m3=2710.0,
        melting_point_C=660.0,
        cte_1e6_per_K=23.5,
        electrical_resistivity_uOhm_m=2.75,
        laser_absorptivity_1=0.21,
        ultrasonic_absorption_factor=0.85,
        default_tab_thickness_um=110.0,
    ),
    "Nickel_Ni": Material(
        name="Nickel_Ni",
        thermal_conductivity_W_mK=90.0,
        specific_heat_J_kgK=440.0,
        density_kg_m3=8908.0,
        melting_point_C=1455.0,
        cte_1e6_per_K=13.4,
        electrical_resistivity_uOhm_m=6.99,
        laser_absorptivity_1=0.55,
        ultrasonic_absorption_factor=1.1,
        default_tab_thickness_um=80.0,
    ),
    "Stainless_304": Material(
        name="Stainless_304",
        thermal_conductivity_W_mK=16.0,
        specific_heat_J_kgK=500.0,
        density_kg_m3=8000.0,
        melting_point_C=1400.0,
        cte_1e6_per_K=17.3,
        electrical_resistivity_uOhm_m=72.0,
        laser_absorptivity_1=0.6,
        ultrasonic_absorption_factor=1.2,
        default_tab_thickness_um=100.0,
    ),
    "Steel_LowCarbon": Material(
        name="Steel_LowCarbon",
        thermal_conductivity_W_mK=50.0,
        specific_heat_J_kgK=490.0,
        density_kg_m3=7850.0,
        melting_point_C=1500.0,
        cte_1e6_per_K=12.0,
        electrical_resistivity_uOhm_m=100.0,
        laser_absorptivity_1=0.55,
        ultrasonic_absorption_factor=1.15,
        default_tab_thickness_um=120.0,
    ),
    "CuNi_70_30": Material(
        name="CuNi_70_30",
        thermal_conductivity_W_mK=29.0,
        specific_heat_J_kgK=380.0,
        density_kg_m3=8900.0,
        melting_point_C=1170.0,
        cte_1e6_per_K=16.0,
        electrical_resistivity_uOhm_m=49.0,
        laser_absorptivity_1=0.55,
        ultrasonic_absorption_factor=1.05,
        default_tab_thickness_um=90.0,
    ),
}
