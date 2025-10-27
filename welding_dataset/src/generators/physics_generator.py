from __future__ import annotations

import math
import random
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

import numpy as np

from src.utils.materials import MATERIAL_DB, effective_thermal_conductivity_pair, effective_resistivity_pair


@dataclass
class InputParameters:
    anode_material: str
    cathode_material: str
    tab_thickness_um: float
    surface_finish: str
    welding_technique: str  # USW, Laser, RSW
    power: float  # W for USW/RSW, J for Laser
    amplitude_um: float  # USW only
    force_n: float
    pressure_mpa: float
    time_s: float
    speed_mm_s: float  # Laser only
    pulse_frequency_hz: float  # Laser only
    preheat_c: float


@dataclass
class CharacterizationMetrics:
    max_interface_temperature_c: float
    heat_input_j: float
    bond_area_mm2: float
    porosity_pct: float
    void_fraction_pct: float
    interface_resistance_mohm: float
    nugget_diameter_mm: float
    haze_color_index: float
    surface_roughness_ra_um: float


@dataclass
class PerformanceMetrics:
    thermal_cycling_cycles_to_failure: int
    resistance_growth_pct_after_cycling: float
    shear_strength_mpa: float
    peel_strength_n: float
    fracture_mode: str
    microcrack_density_per_mm: float


SURFACE_FINISH_EFFECT = {
    "bare": {"resistance_factor": 1.0, "bondability": 1.0},
    "Ni": {"resistance_factor": 1.2, "bondability": 0.9},
    "Sn": {"resistance_factor": 0.9, "bondability": 1.1},
}

FRACTURE_MODES = ["interfacial", "pullout", "ductile", "mixed"]


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(value, hi))


def compute_heat_input(technique: str, power: float, time_s: float, pulse_frequency_hz: float) -> float:
    if technique == "Laser":
        # power treated as pulse energy (J); effective pulses = time * freq
        return power * max(1.0, time_s * max(1.0, pulse_frequency_hz))
    # USW/RSW: power in W
    return power * time_s


def estimate_interface_temperature(preheat_c: float, heat_input_j: float, thickness_um: float, k_eff: float) -> float:
    # Simple 1D slab estimate: deltaT ~ heat_input / (A * rho * Cp * L)
    # We collapse constants into a scale factor with thermal conductivity influence
    thickness_m = thickness_um * 1e-6
    scale = 1.0 / (1e4 + 5e3 * (k_eff / 100.0))
    delta_t = heat_input_j * scale / max(1e-6, thickness_m)
    return preheat_c + delta_t


def estimate_bond_area(technique: str, force_n: float, amplitude_um: float, time_s: float, speed_mm_s: float) -> float:
    if technique == "USW":
        # Bond area grows with plastic flow from amplitude and time under force
        return clamp(0.02 * force_n + 0.3 * amplitude_um + 15 * time_s, 1.0, 200.0)
    if technique == "Laser":
        # Overlap of beam path; slower speed -> larger area
        return clamp(5.0 + 300.0 * time_s / max(0.1, speed_mm_s), 1.0, 300.0)
    # RSW: force and time dominate nugget size
    return clamp(0.03 * force_n + 25.0 * time_s, 1.0, 250.0)


def estimate_porosity(technique: str, heat_input_j: float, speed_mm_s: float) -> float:
    if technique == "Laser":
        # Keyholing at high heat with slow speed
        base = 2.0 + 0.0008 * heat_input_j - 0.01 * speed_mm_s
    else:
        base = 1.0 + 0.0002 * heat_input_j
    return clamp(np.random.normal(base, 0.5), 0.0, 20.0)


def estimate_interface_resistance(surface_finish: str, resistivity_eff: float, bond_area_mm2: float) -> float:
    # Contact resistance ~ resistivity / contact area, modulated by finish
    finish = SURFACE_FINISH_EFFECT.get(surface_finish, {"resistance_factor": 1.0})
    area_m2 = max(1e-6, bond_area_mm2) * 1e-6
    r = (resistivity_eff / area_m2) * finish["resistance_factor"] * 1e6  # to mOhm
    return clamp(r, 0.01, 50.0)


def estimate_strengths(technique: str, bond_area_mm2: float, porosity_pct: float, materials: Tuple[str, str]) -> Tuple[float, float]:
    material_strength = min(MATERIAL_DB[materials[0]].youngs_modulus_gpa, MATERIAL_DB[materials[1]].youngs_modulus_gpa)
    area_factor = math.sqrt(max(1.0, bond_area_mm2))
    porosity_factor = 1.0 - 0.02 * porosity_pct
    shear = clamp(0.8 * area_factor * porosity_factor + 0.05 * material_strength, 5.0, 200.0)
    peel = clamp(3.0 * area_factor * porosity_factor + 0.2 * material_strength, 10.0, 2000.0)
    return shear, peel


def estimate_cycles_to_failure(interface_res_growth: float, shear_strength: float, temp: float) -> int:
    # More resistance growth and higher temperature reduce life; stronger joints last longer
    life = 2000 * (1.0 + 0.01 * shear_strength) / (1.0 + 0.2 * interface_res_growth + 0.002 * max(0.0, temp - 100))
    jitter = np.random.normal(0.0, 100.0)
    return int(clamp(life + jitter, 50.0, 20000.0))


def select_fracture_mode(porosity_pct: float, shear_strength: float) -> str:
    if porosity_pct > 10:
        return "interfacial"
    if shear_strength > 120:
        return "ductile"
    if 60 < shear_strength <= 120:
        return "mixed"
    return "pullout"


def generate_single(seed: int | None = None) -> Tuple[InputParameters, CharacterizationMetrics, PerformanceMetrics]:
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    anode = random.choice(list(MATERIAL_DB.keys()))
    cathode = random.choice(list(MATERIAL_DB.keys()))
    while cathode == anode:
        cathode = random.choice(list(MATERIAL_DB.keys()))

    technique = random.choice(["USW", "Laser", "RSW"])
    tab_thickness_um = random.uniform(50, 500)
    surface_finish = random.choice(["bare", "Ni", "Sn"])    
    preheat_c = random.uniform(20, 120)

    if technique == "Laser":
        power = random.uniform(0.2, 10.0)  # J per pulse
        time_s = random.uniform(0.02, 1.0)
        pulse_frequency_hz = random.uniform(100, 5000)
        speed_mm_s = random.uniform(10, 300)
        amplitude_um = 0.0
        force_n = random.uniform(50, 500)
        pressure_mpa = random.uniform(1.0, 10.0)
    elif technique == "USW":
        power = random.uniform(200, 4000)  # W
        time_s = random.uniform(0.05, 1.0)
        pulse_frequency_hz = 0.0
        speed_mm_s = 0.0
        amplitude_um = random.uniform(5, 50)
        force_n = random.uniform(200, 3000)
        pressure_mpa = random.uniform(2.0, 30.0)
    else:  # RSW
        power = random.uniform(500, 10000)  # W
        time_s = random.uniform(0.02, 0.3)
        pulse_frequency_hz = 0.0
        speed_mm_s = 0.0
        amplitude_um = 0.0
        force_n = random.uniform(1500, 6000)
        pressure_mpa = random.uniform(5.0, 50.0)

    heat_input_j = compute_heat_input(technique, power, time_s, pulse_frequency_hz)

    k_eff = effective_thermal_conductivity_pair(anode, cathode)
    rho_eff = effective_resistivity_pair(anode, cathode)

    max_temp_c = estimate_interface_temperature(preheat_c, heat_input_j, tab_thickness_um, k_eff)
    bond_area_mm2 = estimate_bond_area(technique, force_n, amplitude_um, time_s, speed_mm_s)
    porosity_pct = estimate_porosity(technique, heat_input_j, speed_mm_s)
    void_fraction_pct = clamp(np.random.normal(porosity_pct * 0.6, 0.4), 0.0, 25.0)
    interface_res_mohm = estimate_interface_resistance(surface_finish, rho_eff, bond_area_mm2)
    nugget_diameter_mm = clamp(math.sqrt(bond_area_mm2 / math.pi) * 2.0, 0.5, 20.0)
    haze_color_index = clamp(np.random.normal(0.2 * max_temp_c / 100.0, 0.3), 0.0, 10.0)
    surface_roughness = clamp(np.random.normal(0.5 + 0.01 * amplitude_um, 0.2), 0.05, 10.0)

    shear_strength_mpa, peel_strength_n = estimate_strengths(technique, bond_area_mm2, porosity_pct, (anode, cathode))
    resistance_growth_pct = clamp(np.random.normal(0.5 * porosity_pct + 0.02 * (max_temp_c - preheat_c), 1.5), 0.0, 200.0)
    cycles_to_failure = estimate_cycles_to_failure(resistance_growth_pct, shear_strength_mpa, max_temp_c)
    fracture_mode = select_fracture_mode(porosity_pct, shear_strength_mpa)
    microcrack_density = clamp(np.random.normal(0.1 * porosity_pct + 0.005 * max(0.0, max_temp_c - 200), 0.2), 0.0, 50.0)

    ip = InputParameters(
        anode_material=anode,
        cathode_material=cathode,
        tab_thickness_um=tab_thickness_um,
        surface_finish=surface_finish,
        welding_technique=technique,
        power=power,
        amplitude_um=amplitude_um,
        force_n=force_n,
        pressure_mpa=pressure_mpa,
        time_s=time_s,
        speed_mm_s=speed_mm_s,
        pulse_frequency_hz=pulse_frequency_hz,
        preheat_c=preheat_c,
    )

    cm = CharacterizationMetrics(
        max_interface_temperature_c=max_temp_c,
        heat_input_j=heat_input_j,
        bond_area_mm2=bond_area_mm2,
        porosity_pct=porosity_pct,
        void_fraction_pct=void_fraction_pct,
        interface_resistance_mohm=interface_res_mohm,
        nugget_diameter_mm=nugget_diameter_mm,
        haze_color_index=haze_color_index,
        surface_roughness_ra_um=surface_roughness,
    )

    pm = PerformanceMetrics(
        thermal_cycling_cycles_to_failure=cycles_to_failure,
        resistance_growth_pct_after_cycling=resistance_growth_pct,
        shear_strength_mpa=shear_strength_mpa,
        peel_strength_n=peel_strength_n,
        fracture_mode=fracture_mode,
        microcrack_density_per_mm=microcrack_density,
    )

    return ip, cm, pm


def generate_many(n: int, seed: int | None = None) -> List[Tuple[InputParameters, CharacterizationMetrics, PerformanceMetrics]]:
    rng = np.random.default_rng(seed)
    seeds = rng.integers(0, 2**32 - 1, size=n)
    return [generate_single(int(s)) for s in seeds]
