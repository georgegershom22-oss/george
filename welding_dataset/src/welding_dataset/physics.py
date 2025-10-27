from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Tuple

THERMAL_CONDUCTIVITY_W_MK = {
    "Cu": 401.0,
    "Al": 237.0,
    "Ni": 90.7,
    "SS304": 16.2,
    "SS316": 16.3,
    "CuNi": 29.0,
}

ELECTRICAL_RESISTIVITY_UOHM_CM = {
    "Cu": 1.68,
    "Al": 2.82,
    "Ni": 6.99,
    "SS304": 72.0,
    "SS316": 74.0,
    "CuNi": 49.0,
}

SURFACE_FINISH_CONTACT_FACTOR = {
    "bare": 1.00,
    "nickel_plated": 0.95,
    "tin_plated": 0.90,
    "silver_plated": 0.92,
    "anodized": 1.20,
    "oxidized": 1.15,
}

@dataclass
class MaterialPair:
    anode: str
    cathode: str

    def effective_thermal_conductivity(self) -> float:
        k1 = THERMAL_CONDUCTIVITY_W_MK[self.anode]
        k2 = THERMAL_CONDUCTIVITY_W_MK[self.cathode]
        return 2 * k1 * k2 / (k1 + k2)

    def effective_resistivity(self) -> float:
        r1 = ELECTRICAL_RESISTIVITY_UOHM_CM[self.anode]
        r2 = ELECTRICAL_RESISTIVITY_UOHM_CM[self.cathode]
        return 0.5 * (r1 + r2)


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def compute_heat_input_j(technique: str, power_or_energy: float, time_ms_or_s: float) -> float:
    if technique == "laser":
        return power_or_energy  # treat as pulse energy (J)
    # ultrasonic or resistance spot: power (W) * time (s)
    time_s = time_ms_or_s / 1000.0 if time_ms_or_s > 10 else time_ms_or_s
    return power_or_energy * time_s


def estimate_energy_density_j_mm2(heat_j: float, beam_diameter_mm: float) -> float:
    area = math.pi * (beam_diameter_mm / 2.0) ** 2
    return heat_j / max(area, 1e-6)


def estimate_nugget_and_area(technique: str, force_n: float | None, amplitude_um: float | None,
                             speed_mm_s: float | None, heat_density: float,
                             mat: MaterialPair, thickness_um: float) -> Tuple[float, float]:
    k_eff = mat.effective_thermal_conductivity()
    thickness_mm = thickness_um / 1000.0

    if technique == "ultrasonic":
        force_term = math.log1p((force_n or 50.0) / 50.0)
        amplitude_term = math.log1p((amplitude_um or 15.0) / 10.0)
        cooling = 1.0 / math.sqrt(k_eff)
        nugget_d_mm = clamp(0.2 + 0.6 * amplitude_term + 0.3 * force_term + 0.4 * math.log1p(heat_density) - 0.1 * thickness_mm * cooling, 0.1, 3.0)
    elif technique == "laser":
        speed_term = 0.5 if not speed_mm_s else clamp(1.5 - 0.1 * math.log1p(speed_mm_s), 0.1, 1.5)
        nugget_d_mm = clamp(0.1 + 0.8 * math.log1p(heat_density) * speed_term - 0.05 * thickness_mm, 0.05, 2.5)
    else:  # resistance_spot
        force_term = math.log1p((force_n or 100.0) / 100.0)
        nugget_d_mm = clamp(0.2 + 0.5 * force_term + 0.5 * math.log1p(heat_density) - 0.1 * thickness_mm, 0.1, 3.5)

    area_mm2 = math.pi * (nugget_d_mm / 2) ** 2
    return nugget_d_mm, area_mm2


def estimate_max_temp_c(heat_j: float, mat: MaterialPair, thickness_um: float, preheat_c: float) -> float:
    k_eff = mat.effective_thermal_conductivity()
    thickness_mm = thickness_um / 1000.0
    base = preheat_c + 40.0 + 120.0 * math.log1p(heat_j) - 25.0 * math.log1p(k_eff) - 15.0 * thickness_mm
    return clamp(base, preheat_c, preheat_c + 800.0)


def estimate_interface_resistance_milliohm(surface_finish: str, pressure_mpa: float | None,
                                           roughness_factor: float = 1.0) -> float:
    base = 5.0 * SURFACE_FINISH_CONTACT_FACTOR[surface_finish] * roughness_factor
    if pressure_mpa is not None:
        base *= 1.0 / math.sqrt(1.0 + pressure_mpa)
    return clamp(base, 0.1, 30.0)


def estimate_porosity_percent(technique: str, heat_density: float, max_temp_c: float) -> float:
    if technique == "laser":
        porosity = 8.0 / (1.0 + math.exp(-0.02 * (max_temp_c - 600))) + 2.0 * math.exp(-0.05 * heat_density)
    elif technique == "ultrasonic":
        porosity = 3.0 + 2.0 * math.exp(-0.03 * heat_density)
    else:
        porosity = 5.0 + 1.5 * math.exp(-0.02 * heat_density)
    return clamp(porosity, 0.1, 30.0)


def estimate_misalignment_um(force_n: float | None, amplitude_um: float | None, speed_mm_s: float | None) -> float:
    jitter = 30.0
    if amplitude_um:
        jitter += 40.0 / math.sqrt(1.0 + amplitude_um)
    if force_n:
        jitter *= 1.0 / math.sqrt(1.0 + force_n / 100.0)
    if speed_mm_s:
        jitter *= 1.0 + 0.002 * speed_mm_s
    return clamp(jitter, 2.0, 200.0)


def estimate_mechanical_strengths(nugget_area_mm2: float, mat: MaterialPair, porosity_percent: float) -> Tuple[float, float]:
    baseline_mpa = 120.0 * math.sqrt(nugget_area_mm2) * math.log1p(mat.effective_thermal_conductivity()) / 5.0
    tensile_shear_mpa = clamp(baseline_mpa * (1.0 - 0.005 * porosity_percent), 5.0, 600.0)
    peel_strength_n_mm = clamp(2.5 * tensile_shear_mpa ** 0.7, 1.0, 500.0)
    return tensile_shear_mpa, peel_strength_n_mm


def estimate_validation_performance(forward: dict, mat: MaterialPair, preheat_c: float) -> Tuple[int, float, float, float]:
    area = forward["weld_area_mm2"]
    res_mohm = forward["interfacial_resistance_milliohm"]
    porosity = forward["porosity_percent"]
    tensile = forward["tensile_shear_strength_mpa"]

    cycles = int(clamp(200 + 80 * area - 10 * res_mohm - 3 * porosity + 0.5 * tensile + 0.1 * preheat_c, 0, 5000))
    resistance_growth = clamp(0.5 * res_mohm + 0.1 * porosity - 0.02 * tensile + 0.01 * preheat_c, 0.0, 50.0)
    crack_length = clamp(0.1 + 0.02 * porosity + 0.0005 * tensile - 0.0001 * cycles, 0.0, 20.0)
    delam = clamp(0.5 * porosity + 0.1 * res_mohm - 0.05 * math.sqrt(area), 0.0, 80.0)
    return cycles, resistance_growth, crack_length, delam
