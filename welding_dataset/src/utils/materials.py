from dataclasses import dataclass
from typing import Dict, Tuple

# Simplified material property database relevant to welding physics.
# Values are approximate and intended for synthetic data generation.

@dataclass(frozen=True)
class Material:
    name: str
    density_kg_m3: float
    thermal_conductivity_w_mk: float
    specific_heat_j_kgk: float
    melting_point_c: float
    electrical_resistivity_ohm_m: float
    youngs_modulus_gpa: float
    poisson_ratio: float


MATERIAL_DB: Dict[str, Material] = {
    "Cu": Material(
        name="Cu",
        density_kg_m3=8960,
        thermal_conductivity_w_mk=401,
        specific_heat_j_kgk=385,
        melting_point_c=1085,
        electrical_resistivity_ohm_m=1.68e-8,
        youngs_modulus_gpa=110,
        poisson_ratio=0.34,
    ),
    "Al": Material(
        name="Al",
        density_kg_m3=2700,
        thermal_conductivity_w_mk=237,
        specific_heat_j_kgk=903,
        melting_point_c=660,
        electrical_resistivity_ohm_m=2.82e-8,
        youngs_modulus_gpa=69,
        poisson_ratio=0.33,
    ),
    "Ni": Material(
        name="Ni",
        density_kg_m3=8908,
        thermal_conductivity_w_mk=91,
        specific_heat_j_kgk=444,
        melting_point_c=1455,
        electrical_resistivity_ohm_m=6.99e-8,
        youngs_modulus_gpa=200,
        poisson_ratio=0.31,
    ),
    "SS304": Material(
        name="SS304",
        density_kg_m3=8000,
        thermal_conductivity_w_mk=16,
        specific_heat_j_kgk=500,
        melting_point_c=1400,
        electrical_resistivity_ohm_m=7.2e-7,
        youngs_modulus_gpa=193,
        poisson_ratio=0.30,
    ),
}


def effective_thermal_conductivity_pair(a: str, b: str) -> float:
    ka = MATERIAL_DB[a].thermal_conductivity_w_mk
    kb = MATERIAL_DB[b].thermal_conductivity_w_mk
    # Harmonic mean to reflect interface-limited conduction paths
    return 2 * ka * kb / (ka + kb)


def effective_resistivity_pair(a: str, b: str) -> float:
    ra = MATERIAL_DB[a].electrical_resistivity_ohm_m
    rb = MATERIAL_DB[b].electrical_resistivity_ohm_m
    # Parallel path analogy (lower bound)
    return (ra * rb) / (ra + rb)
