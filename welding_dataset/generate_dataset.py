#!/usr/bin/env python3
"""
Generator for a comprehensive, physics-inspired dataset for ML-driven inverse design of welding parameters.
Outputs:
- inputs.csv: Design space variables (controllable inputs)
- quality.csv: Forward-problem quality and characterization metrics (post-weld immediate)
- performance.csv: Validation metrics under thermal cycling (inverse-design targets)
- combined.csv: All columns merged by sample_id
- metadata.json: Schema with units and descriptions
- welding_dataset.zip: Archive containing all above files

Run:
  python3 generate_dataset.py --n 5000 --out ./output
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import statistics
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple
from zipfile import ZipFile, ZIP_DEFLATED


# -----------------------------
# Data definitions and helpers
# -----------------------------

@dataclass(frozen=True)
class MaterialProps:
    name: str
    resistivity_ohm_m: float  # Electrical resistivity (Ω·m)
    density_kg_m3: float      # Density (kg/m^3)
    thermal_conductivity_w_mk: float  # Thermal conductivity (W/mK)
    specific_heat_j_kgk: float  # Specific heat capacity (J/kgK)
    cte_1_k: float  # Coefficient of thermal expansion (1/K)


MATERIALS: Dict[str, MaterialProps] = {
    "Copper": MaterialProps("Copper", 1.68e-8, 8960, 400.0, 385.0, 16.5e-6),
    "Aluminum": MaterialProps("Aluminum", 2.82e-8, 2700, 237.0, 900.0, 23.0e-6),
    "Nickel": MaterialProps("Nickel", 6.99e-8, 8900, 91.0, 440.0, 13.0e-6),
    "StainlessSteel": MaterialProps("StainlessSteel", 7.00e-7, 8000, 16.0, 500.0, 17.0e-6),
    "Titanium": MaterialProps("Titanium", 4.20e-7, 4500, 22.0, 520.0, 8.6e-6),
}

# Surface finish / coating factors influencing contact resistance and bondability
COATING_CONTACT_FACTOR: Dict[str, float] = {
    "bare": 1.00,
    "oxide_heavy": 2.00,
    "nickel_plated": 0.90,
    "tin_plated": 0.95,
    "silver_plated": 0.80,
    "gold_plated": 0.75,
    "brushed": 0.90,
    "graphite_coated": 1.20,
}

WELDING_TECHNIQUES = ["USW", "Laser", "RSW"]  # Ultrasonic, Laser, Resistance Spot

# Pair-specific intermetallic tendency multiplier (Cu-Al high, similar metals low)
INTERMETALLIC_TENDENCY: Dict[Tuple[str, str], float] = {}
MATERIAL_NAMES = list(MATERIALS.keys())
for a in MATERIAL_NAMES:
    for b in MATERIAL_NAMES:
        if a == b:
            INTERMETALLIC_TENDENCY[(a, b)] = 0.4
        else:
            pair = {a, b}
            if pair == {"Copper", "Aluminum"}:
                INTERMETALLIC_TENDENCY[(a, b)] = 1.6
            elif pair == {"Aluminum", "Nickel"}:
                INTERMETALLIC_TENDENCY[(a, b)] = 1.3
            elif pair == {"Copper", "Nickel"}:
                INTERMETALLIC_TENDENCY[(a, b)] = 1.0
            elif pair == {"Copper", "StainlessSteel"}:
                INTERMETALLIC_TENDENCY[(a, b)] = 1.2
            elif pair == {"Aluminum", "StainlessSteel"}:
                INTERMETALLIC_TENDENCY[(a, b)] = 1.4
            else:
                INTERMETALLIC_TENDENCY[(a, b)] = 1.1


def bounded(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def normal(mu: float, sigma: float) -> float:
    # Box-Muller transform for reproducible normal without numpy
    u1 = random.random()
    u2 = random.random()
    z0 = math.sqrt(-2.0 * math.log(max(1e-12, u1))) * math.cos(2 * math.pi * u2)
    return mu + sigma * z0


# -----------------------------
# Core generators
# -----------------------------

@dataclass
class InputRow:
    sample_id: int
    anode_material: str
    cathode_material: str
    tab_thickness_um: float
    surface_coating: str
    welding_technique: str
    # Shared geometry/environment
    tab_width_mm: float
    overlap_length_mm: float
    preheat_celsius: float
    # USW params
    usw_power_w: float | None
    usw_amplitude_um: float | None
    usw_force_n: float | None
    usw_time_ms: float | None
    # Laser params
    laser_power_w: float | None
    laser_speed_mm_s: float | None
    laser_pulse_frequency_hz: float | None
    laser_energy_per_pulse_j: float | None
    laser_spot_diameter_mm: float | None
    # RSW params
    rsw_current_ka: float | None
    rsw_voltage_v: float | None
    rsw_weld_time_ms: float | None
    rsw_squeeze_time_ms: float | None
    rsw_hold_time_ms: float | None
    rsw_force_n: float | None


@dataclass
class QualityRow:
    sample_id: int
    effective_energy_j: float
    energy_density_j_mm2: float
    peak_temperature_c: float
    fused_area_mm2: float
    nugget_diameter_mm: float
    porosity_pct: float
    spatter_mass_mg: float
    intermetallic_thickness_um: float
    hardness_hv: float
    bond_integrity_score: float
    immediate_shear_strength_n: float
    joint_resistance_mohm: float


@dataclass
class PerformanceRow:
    sample_id: int
    cycles_to_failure: int
    resistance_growth_pct_1000: float
    retained_strength_pct_1000: float
    delamination_probability: float
    failure_mode: str


def choose_material_pair() -> Tuple[str, str]:
    # Bias towards Cu-Al and Cu-Cu pairs as common in battery tabs
    pairs = [
        ("Copper", "Aluminum"), ("Copper", "Copper"), ("Aluminum", "Aluminum"),
        ("Copper", "Nickel"), ("Aluminum", "Nickel"), ("Copper", "StainlessSteel"),
        ("Aluminum", "StainlessSteel"), ("Copper", "Titanium"), ("Aluminum", "Titanium"),
    ]
    weights = [0.22, 0.18, 0.10, 0.12, 0.10, 0.10, 0.10, 0.04, 0.04]
    r = random.random()
    acc = 0.0
    for (i, w) in enumerate(weights):
        acc += w
        if r <= acc:
            return pairs[i]
    return pairs[-1]


def pick_coating() -> str:
    options = list(COATING_CONTACT_FACTOR.keys())
    weights = [0.20, 0.05, 0.20, 0.15, 0.10, 0.05, 0.15, 0.10]
    r = random.random()
    acc = 0.0
    for i, w in enumerate(weights):
        acc += w
        if r <= acc:
            return options[i]
    return options[-1]


def pick_welding_technique() -> str:
    weights = [0.45, 0.35, 0.20]  # USW, Laser, RSW
    r = random.random()
    acc = 0.0
    for i, w in enumerate(weights):
        acc += w
        if r <= acc:
            return WELDING_TECHNIQUES[i]
    return WELDING_TECHNIQUES[-1]


def generate_input_row(sample_id: int) -> InputRow:
    anode, cathode = choose_material_pair()
    coating = pick_coating()
    technique = pick_welding_technique()

    # Geometry and environment
    tab_thickness_um = bounded(normal(120.0, 40.0), 20.0, 300.0)
    tab_width_mm = bounded(normal(6.0, 2.0), 2.0, 12.0)
    overlap_length_mm = bounded(normal(6.0, 2.0), 2.0, 12.0)
    preheat_celsius = bounded(normal(40.0, 20.0), 20.0, 120.0)

    # Initialize all params as None
    params = {
        "usw_power_w": None,
        "usw_amplitude_um": None,
        "usw_force_n": None,
        "usw_time_ms": None,
        "laser_power_w": None,
        "laser_speed_mm_s": None,
        "laser_pulse_frequency_hz": None,
        "laser_energy_per_pulse_j": None,
        "laser_spot_diameter_mm": None,
        "rsw_current_ka": None,
        "rsw_voltage_v": None,
        "rsw_weld_time_ms": None,
        "rsw_squeeze_time_ms": None,
        "rsw_hold_time_ms": None,
        "rsw_force_n": None,
    }

    if technique == "USW":
        params["usw_power_w"] = bounded(normal(1500.0, 400.0), 500.0, 3000.0)
        params["usw_amplitude_um"] = bounded(normal(30.0, 8.0), 10.0, 60.0)
        params["usw_force_n"] = bounded(normal(700.0, 250.0), 100.0, 1500.0)
        params["usw_time_ms"] = bounded(normal(300.0, 120.0), 50.0, 800.0)
    elif technique == "Laser":
        params["laser_power_w"] = bounded(normal(600.0, 250.0), 100.0, 2000.0)
        params["laser_speed_mm_s"] = bounded(normal(40.0, 20.0), 5.0, 200.0)
        # Randomly choose pulsed vs CW-like behavior
        if random.random() < 0.6:
            params["laser_pulse_frequency_hz"] = bounded(normal(200.0, 80.0), 10.0, 1000.0)
            params["laser_energy_per_pulse_j"] = bounded(normal(0.8, 0.4), 0.05, 5.0)
        else:
            params["laser_pulse_frequency_hz"] = 0.0
            params["laser_energy_per_pulse_j"] = 0.0
        params["laser_spot_diameter_mm"] = bounded(normal(0.20, 0.07), 0.05, 0.50)
    else:  # RSW
        params["rsw_current_ka"] = bounded(normal(12.0, 4.0), 2.0, 30.0)
        params["rsw_voltage_v"] = bounded(normal(3.0, 1.0), 1.0, 10.0)
        params["rsw_weld_time_ms"] = bounded(normal(180.0, 60.0), 50.0, 400.0)
        params["rsw_squeeze_time_ms"] = bounded(normal(100.0, 30.0), 50.0, 200.0)
        params["rsw_hold_time_ms"] = bounded(normal(100.0, 30.0), 50.0, 200.0)
        params["rsw_force_n"] = bounded(normal(2000.0, 600.0), 500.0, 4000.0)

    return InputRow(
        sample_id=sample_id,
        anode_material=anode,
        cathode_material=cathode,
        tab_thickness_um=tab_thickness_um,
        surface_coating=coating,
        welding_technique=technique,
        tab_width_mm=tab_width_mm,
        overlap_length_mm=overlap_length_mm,
        preheat_celsius=preheat_celsius,
        usw_power_w=params["usw_power_w"],
        usw_amplitude_um=params["usw_amplitude_um"],
        usw_force_n=params["usw_force_n"],
        usw_time_ms=params["usw_time_ms"],
        laser_power_w=params["laser_power_w"],
        laser_speed_mm_s=params["laser_speed_mm_s"],
        laser_pulse_frequency_hz=params["laser_pulse_frequency_hz"],
        laser_energy_per_pulse_j=params["laser_energy_per_pulse_j"],
        laser_spot_diameter_mm=params["laser_spot_diameter_mm"],
        rsw_current_ka=params["rsw_current_ka"],
        rsw_voltage_v=params["rsw_voltage_v"],
        rsw_weld_time_ms=params["rsw_weld_time_ms"],
        rsw_squeeze_time_ms=params["rsw_squeeze_time_ms"],
        rsw_hold_time_ms=params["rsw_hold_time_ms"],
        rsw_force_n=params["rsw_force_n"],
    )


def compute_effective_energy_and_metrics(inp: InputRow) -> Tuple[QualityRow, PerformanceRow]:
    # Geometry conversions
    area_mm2 = inp.tab_width_mm * inp.overlap_length_mm
    area_m2 = area_mm2 * 1e-6  # 1 mm^2 = 1e-6 m^2
    thickness_m = inp.tab_thickness_um * 1e-6

    anode = MATERIALS[inp.anode_material]
    cathode = MATERIALS[inp.cathode_material]

    # Effective thermal mass per area (J/K per m^2), simplified 1D slab
    thermal_mass_per_area = (
        0.5 * thickness_m * anode.density_kg_m3 * anode.specific_heat_j_kgk
        + 0.5 * thickness_m * cathode.density_kg_m3 * cathode.specific_heat_j_kgk
    )  # J/K per m^2

    # Contact resistance baseline scaled by coating and surface effects
    base_resistivity = 0.5 * (anode.resistivity_ohm_m + cathode.resistivity_ohm_m)
    coating_factor = COATING_CONTACT_FACTOR[inp.surface_coating]
    contact_resistance_ohm = base_resistivity * coating_factor / max(1e-12, area_m2)

    # Technique-specific energy deposition and coupling efficiency
    if inp.welding_technique == "USW":
        time_s = (inp.usw_time_ms or 0.0) / 1000.0
        power_w = inp.usw_power_w or 0.0
        force_n = inp.usw_force_n or 0.0
        amplitude_um = inp.usw_amplitude_um or 0.0

        # Coupling efficiency: bell-shaped vs amplitude; improved with adequate force
        amplitude_opt_um = 32.0
        amplitude_sigma = 10.0
        amplitude_eff = math.exp(-((amplitude_um - amplitude_opt_um) ** 2) / (2 * amplitude_sigma**2))
        force_eff = logistic((force_n - 600.0) / 250.0)
        thickness_eff = logistic((220.0 - inp.tab_thickness_um) / 60.0)
        coupling = 0.35 + 0.55 * amplitude_eff * force_eff * thickness_eff

        effective_energy_j = power_w * time_s * coupling

    elif inp.welding_technique == "Laser":
        time_s = max(0.02, area_mm2 / max(1e-6, (inp.laser_speed_mm_s or 1.0) * (inp.laser_spot_diameter_mm or 0.2)))
        power_w = inp.laser_power_w or 0.0
        pulse_f = inp.laser_pulse_frequency_hz or 0.0
        e_pulse = inp.laser_energy_per_pulse_j or 0.0
        spot_d_mm = max(0.05, inp.laser_spot_diameter_mm or 0.2)

        absorption = 0.25 + 0.20 * logistic((power_w - 400.0) / 200.0)
        # Pulsed addition to power-equivalent energy
        pulsed_j = pulse_f * e_pulse * time_s
        cw_j = power_w * time_s
        raw_j = cw_j + pulsed_j
        effective_energy_j = raw_j * absorption

    else:  # RSW
        time_s = (inp.rsw_weld_time_ms or 0.0) / 1000.0
        current_a = (inp.rsw_current_ka or 0.0) * 1000.0
        # Joule heating I^2 R t; include squeeze effect via force and voltage shape via simple factor
        squeeze_eff = logistic(((inp.rsw_force_n or 0.0) - 1500.0) / 500.0)
        voltage_factor = logistic(((inp.rsw_voltage_v or 0.0) - 2.0) / 1.0)
        effective_energy_j = (current_a ** 2) * contact_resistance_ohm * time_s * (0.3 + 0.5 * squeeze_eff * voltage_factor)

    # Energy density per area (J/mm^2)
    energy_density_j_mm2 = effective_energy_j / max(1e-12, area_mm2)

    # Peak temperature rise (C) ~ energy / (thermal mass per area * area) with conduction losses
    conduction_factor = 0.6 + 0.4 * logistic(((anode.thermal_conductivity_w_mk + cathode.thermal_conductivity_w_mk) / 2.0 - 50.0) / 50.0)
    delta_t = effective_energy_j / max(1e-12, thermal_mass_per_area * area_m2) * (0.7 / conduction_factor)
    peak_temperature_c = inp.preheat_celsius + delta_t

    # Fused area and nugget diameter estimation (saturating with energy density)
    saturation_scale = 8.0  # J/mm^2 scale to saturate fusion
    fused_fraction = logistic((energy_density_j_mm2 - 1.2) / (saturation_scale / 6.0))
    # Pressure helps fusion for USW and RSW, focus quality helps for Laser (spot size)
    if inp.welding_technique == "USW":
        pressure_eff = logistic(((inp.usw_force_n or 0.0) - 600.0) / 250.0)
        fused_fraction *= 0.85 + 0.25 * pressure_eff
    elif inp.welding_technique == "RSW":
        pressure_eff = logistic(((inp.rsw_force_n or 0.0) - 1500.0) / 500.0)
        fused_fraction *= 0.80 + 0.30 * pressure_eff
    else:
        spot_quality = logistic((0.3 - (inp.laser_spot_diameter_mm or 0.3)) / 0.08)
        fused_fraction *= 0.80 + 0.30 * spot_quality

    fused_area_mm2 = bounded(area_mm2 * fused_fraction, 0.2, area_mm2)
    nugget_diameter_mm = 2.0 * math.sqrt(fused_area_mm2 / math.pi)

    # Porosity: U-shaped vs normalized energy; minimum near sweet spot ~ 3 J/mm^2
    energy_norm = energy_density_j_mm2 / 3.0
    porosity_base = 5.0 + 18.0 * (energy_norm - 1.0) ** 2
    porosity_coating = 3.0 * (COATING_CONTACT_FACTOR[inp.surface_coating] - 1.0)
    porosity_pct = bounded(normal(porosity_base + porosity_coating, 2.0), 0.2, 35.0)

    # Spatter increases when energy too high or amplitude too large for USW / high power for Laser
    spatter_base = 3.0 * max(0.0, energy_norm - 1.2) ** 2
    if inp.welding_technique == "USW":
        spatter_base += 0.015 * max(0.0, (inp.usw_amplitude_um or 0.0) - 35.0)
    elif inp.welding_technique == "Laser":
        spatter_base += 0.0015 * max(0.0, (inp.laser_power_w or 0.0) - 800.0)
    spatter_mass_mg = bounded(normal(spatter_base, 0.8), 0.0, 25.0)

    # Intermetallic growth with energy and pair tendency; higher for Laser/RSW than USW
    pair_key = (inp.anode_material, inp.cathode_material)
    im_tendency = INTERMETALLIC_TENDENCY.get(pair_key, 1.0)
    process_factor = {"USW": 0.7, "Laser": 1.2, "RSW": 1.0}[inp.welding_technique]
    intermetallic_thickness_um = bounded(normal( (0.6 + 1.5 * energy_norm) * im_tendency * process_factor, 0.35), 0.05, 12.0)

    # Hardness HV increases with IM and peak temperature to a point
    hardness_hv = bounded(80.0 + 12.0 * intermetallic_thickness_um + 0.02 * (peak_temperature_c - inp.preheat_celsius), 50.0, 350.0)

    # Bond integrity 0..1 increases with fused area and decreases with porosity and excessive IM
    im_penalty = 0.15 * max(0.0, intermetallic_thickness_um - 3.0)
    bond_integrity = bounded(0.2 + 0.65 * fused_fraction - 0.012 * porosity_pct - im_penalty + normal(0.0, 0.03), 0.0, 1.0)

    # Immediate shear strength ~ fused area and good IM (bell-shaped vs IM)
    im_shape = math.exp(-((intermetallic_thickness_um - 2.0) ** 2) / (2 * 1.6 ** 2))
    immediate_shear_strength_n = bounded( 50.0 + 45.0 * fused_area_mm2 * (0.6 + 0.6 * im_shape) + normal(0.0, 15.0), 20.0, 6000.0)

    # Electrical joint resistance: decreases with fused area; increases with porosity & IM
    joint_resistance_mohm = bounded( 1e3 * contact_resistance_ohm + 0.35 * (1.0 / max(0.1, fused_fraction)) + 0.06 * porosity_pct + 0.05 * intermetallic_thickness_um + normal(0.0, 0.15), 0.02, 25.0)

    # Performance under thermal cycling
    # CTE mismatch penalty (average absolute mismatch)
    cte_mismatch = abs(anode.cte_1_k - cathode.cte_1_k)
    mismatch_factor = 1.0 + 22.0 * cte_mismatch  # scale to ~1..2.5

    # Cycles to failure scaled by bond integrity, IM (penalize > 4um), porosity, and mismatch
    cycles_base = 400.0 + 3800.0 * bond_integrity
    im_cycle_penalty = 0.10 * max(0.0, intermetallic_thickness_um - 4.0) ** 1.2
    porosity_penalty = 0.012 * porosity_pct
    cycles_to_failure = int(bounded(normal(cycles_base / (1.0 + im_cycle_penalty + porosity_penalty) / mismatch_factor, 120.0), 50.0, 10000.0))

    # Resistance growth after 1000 cycles increases with IM and porosity and mismatch, decreases with fused_fraction
    resistance_growth_pct_1000 = bounded(normal( 5.0 + 2.5 * im_tendency + 0.22 * intermetallic_thickness_um + 0.18 * porosity_pct + 12.0 * (1.0 - fused_fraction) + 16.0 * cte_mismatch, 2.0), 0.0, 120.0)

    # Retained strength after 1000 cycles correlates with cycles_to_failure & bond integrity
    retained_strength_pct_1000 = bounded(normal( 55.0 + 42.0 * bond_integrity - 0.8 * intermetallic_thickness_um - 0.25 * porosity_pct - 28.0 * cte_mismatch, 5.0), 5.0, 100.0)

    # Delamination probability via logistic of bad conditions
    delam_logit = -3.0 + 1.2 * (1.0 - bond_integrity) + 0.25 * intermetallic_thickness_um + 0.06 * porosity_pct + 6.0 * cte_mismatch
    delamination_probability = bounded( logistic(delam_logit) + normal(0.0, 0.03), 0.0, 1.0)

    # Failure mode selection
    if delamination_probability > 0.6 and intermetallic_thickness_um > 3.5:
        failure_mode = "interfacial_delamination"
    elif retained_strength_pct_1000 < 35.0:
        failure_mode = "brittle_intermetallic"
    elif porosity_pct > 18.0:
        failure_mode = "porosity_cracking"
    elif fused_fraction < 0.35:
        failure_mode = "insufficient_fusion"
    else:
        failure_mode = random.choice(["pullout", "tearing", "mixed"])  # relatively healthy modes

    quality = QualityRow(
        sample_id=inp.sample_id,
        effective_energy_j=effective_energy_j,
        energy_density_j_mm2=energy_density_j_mm2,
        peak_temperature_c=peak_temperature_c,
        fused_area_mm2=fused_area_mm2,
        nugget_diameter_mm=nugget_diameter_mm,
        porosity_pct=porosity_pct,
        spatter_mass_mg=spatter_mass_mg,
        intermetallic_thickness_um=intermetallic_thickness_um,
        hardness_hv=hardness_hv,
        bond_integrity_score=bond_integrity,
        immediate_shear_strength_n=immediate_shear_strength_n,
        joint_resistance_mohm=joint_resistance_mohm,
    )

    performance = PerformanceRow(
        sample_id=inp.sample_id,
        cycles_to_failure=cycles_to_failure,
        resistance_growth_pct_1000=resistance_growth_pct_1000,
        retained_strength_pct_1000=retained_strength_pct_1000,
        delamination_probability=delamination_probability,
        failure_mode=failure_mode,
    )

    return quality, performance


# -----------------------------
# IO
# -----------------------------

INPUT_FIELDS = [
    "sample_id", "anode_material", "cathode_material", "tab_thickness_um", "surface_coating",
    "welding_technique", "tab_width_mm", "overlap_length_mm", "preheat_celsius",
    "usw_power_w", "usw_amplitude_um", "usw_force_n", "usw_time_ms",
    "laser_power_w", "laser_speed_mm_s", "laser_pulse_frequency_hz", "laser_energy_per_pulse_j", "laser_spot_diameter_mm",
    "rsw_current_ka", "rsw_voltage_v", "rsw_weld_time_ms", "rsw_squeeze_time_ms", "rsw_hold_time_ms", "rsw_force_n",
]

QUALITY_FIELDS = [
    "sample_id", "effective_energy_j", "energy_density_j_mm2", "peak_temperature_c", "fused_area_mm2",
    "nugget_diameter_mm", "porosity_pct", "spatter_mass_mg", "intermetallic_thickness_um", "hardness_hv",
    "bond_integrity_score", "immediate_shear_strength_n", "joint_resistance_mohm",
]

PERFORMANCE_FIELDS = [
    "sample_id", "cycles_to_failure", "resistance_growth_pct_1000", "retained_strength_pct_1000",
    "delamination_probability", "failure_mode",
]


SCHEMA_METADATA = {
    "inputs": {
        "anode_material": {"unit": "-", "description": "Base material on anode side"},
        "cathode_material": {"unit": "-", "description": "Base material on cathode side"},
        "tab_thickness_um": {"unit": "um", "description": "Tab thickness"},
        "surface_coating": {"unit": "-", "description": "Surface finish or coating"},
        "welding_technique": {"unit": "-", "description": "USW, Laser, or RSW"},
        "tab_width_mm": {"unit": "mm", "description": "Tab width"},
        "overlap_length_mm": {"unit": "mm", "description": "Overlap length"},
        "preheat_celsius": {"unit": "C", "description": "Pre-heat temperature"},
        "usw_power_w": {"unit": "W", "description": "USW peak power"},
        "usw_amplitude_um": {"unit": "um", "description": "USW vibration amplitude"},
        "usw_force_n": {"unit": "N", "description": "USW clamping force"},
        "usw_time_ms": {"unit": "ms", "description": "USW weld duration"},
        "laser_power_w": {"unit": "W", "description": "Laser power"},
        "laser_speed_mm_s": {"unit": "mm/s", "description": "Laser welding speed"},
        "laser_pulse_frequency_hz": {"unit": "Hz", "description": "Laser pulse frequency (if pulsed)"},
        "laser_energy_per_pulse_j": {"unit": "J", "description": "Laser energy per pulse (if pulsed)"},
        "laser_spot_diameter_mm": {"unit": "mm", "description": "Laser spot diameter"},
        "rsw_current_ka": {"unit": "kA", "description": "RSW current"},
        "rsw_voltage_v": {"unit": "V", "description": "RSW voltage"},
        "rsw_weld_time_ms": {"unit": "ms", "description": "RSW weld time"},
        "rsw_squeeze_time_ms": {"unit": "ms", "description": "RSW squeeze time"},
        "rsw_hold_time_ms": {"unit": "ms", "description": "RSW hold time"},
        "rsw_force_n": {"unit": "N", "description": "RSW electrode force"},
    },
    "quality": {
        "effective_energy_j": {"unit": "J", "description": "Effective energy deposited"},
        "energy_density_j_mm2": {"unit": "J/mm^2", "description": "Energy per area"},
        "peak_temperature_c": {"unit": "C", "description": "Peak joint temperature"},
        "fused_area_mm2": {"unit": "mm^2", "description": "Fused/bonded area"},
        "nugget_diameter_mm": {"unit": "mm", "description": "Weld nugget diameter equivalent"},
        "porosity_pct": {"unit": "%", "description": "Porosity percentage"},
        "spatter_mass_mg": {"unit": "mg", "description": "Spatter mass"},
        "intermetallic_thickness_um": {"unit": "um", "description": "Intermetallic layer thickness"},
        "hardness_hv": {"unit": "HV", "description": "Vickers hardness near joint"},
        "bond_integrity_score": {"unit": "0-1", "description": "Bond integrity score"},
        "immediate_shear_strength_n": {"unit": "N", "description": "Immediate shear strength"},
        "joint_resistance_mohm": {"unit": "mOhm", "description": "Joint electrical resistance"},
    },
    "performance": {
        "cycles_to_failure": {"unit": "cycles", "description": "Thermal cycles to failure (-40..85C)"},
        "resistance_growth_pct_1000": {"unit": "%", "description": "Resistance growth after 1000 cycles"},
        "retained_strength_pct_1000": {"unit": "%", "description": "Retained shear strength after 1000 cycles"},
        "delamination_probability": {"unit": "0-1", "description": "Probability of delamination"},
        "failure_mode": {"unit": "-", "description": "Dominant failure mode"},
    },
}


def write_csv(path: str, fieldnames: List[str], rows: List[dict]) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_metadata(path: str) -> None:
    with open(path, "w") as f:
        json.dump(SCHEMA_METADATA, f, indent=2)


def zip_outputs(zip_path: str, files: List[str], base_dir: str) -> None:
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for file in files:
            arcname = os.path.relpath(file, base_dir)
            zf.write(file, arcname)


# -----------------------------
# Main
# -----------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5000, help="Number of samples to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--out", type=str, default="./output", help="Output directory")
    args = parser.parse_args()

    random.seed(args.seed)

    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    inputs: List[InputRow] = []
    qualities: List[QualityRow] = []
    performances: List[PerformanceRow] = []

    for i in range(args.n):
        inp = generate_input_row(sample_id=i + 1)
        quality, performance = compute_effective_energy_and_metrics(inp)
        inputs.append(inp)
        qualities.append(quality)
        performances.append(performance)

    # Convert rows to dicts
    input_dicts = [
        {
            "sample_id": r.sample_id,
            "anode_material": r.anode_material,
            "cathode_material": r.cathode_material,
            "tab_thickness_um": round(r.tab_thickness_um, 3),
            "surface_coating": r.surface_coating,
            "welding_technique": r.welding_technique,
            "tab_width_mm": round(r.tab_width_mm, 3),
            "overlap_length_mm": round(r.overlap_length_mm, 3),
            "preheat_celsius": round(r.preheat_celsius, 3),
            "usw_power_w": round(r.usw_power_w, 6) if r.usw_power_w is not None else None,
            "usw_amplitude_um": round(r.usw_amplitude_um, 6) if r.usw_amplitude_um is not None else None,
            "usw_force_n": round(r.usw_force_n, 6) if r.usw_force_n is not None else None,
            "usw_time_ms": round(r.usw_time_ms, 6) if r.usw_time_ms is not None else None,
            "laser_power_w": round(r.laser_power_w, 6) if r.laser_power_w is not None else None,
            "laser_speed_mm_s": round(r.laser_speed_mm_s, 6) if r.laser_speed_mm_s is not None else None,
            "laser_pulse_frequency_hz": round(r.laser_pulse_frequency_hz, 6) if r.laser_pulse_frequency_hz is not None else None,
            "laser_energy_per_pulse_j": round(r.laser_energy_per_pulse_j, 6) if r.laser_energy_per_pulse_j is not None else None,
            "laser_spot_diameter_mm": round(r.laser_spot_diameter_mm, 6) if r.laser_spot_diameter_mm is not None else None,
            "rsw_current_ka": round(r.rsw_current_ka, 6) if r.rsw_current_ka is not None else None,
            "rsw_voltage_v": round(r.rsw_voltage_v, 6) if r.rsw_voltage_v is not None else None,
            "rsw_weld_time_ms": round(r.rsw_weld_time_ms, 6) if r.rsw_weld_time_ms is not None else None,
            "rsw_squeeze_time_ms": round(r.rsw_squeeze_time_ms, 6) if r.rsw_squeeze_time_ms is not None else None,
            "rsw_hold_time_ms": round(r.rsw_hold_time_ms, 6) if r.rsw_hold_time_ms is not None else None,
            "rsw_force_n": round(r.rsw_force_n, 6) if r.rsw_force_n is not None else None,
        }
        for r in inputs
    ]

    quality_dicts = [
        {
            "sample_id": r.sample_id,
            "effective_energy_j": round(r.effective_energy_j, 6),
            "energy_density_j_mm2": round(r.energy_density_j_mm2, 6),
            "peak_temperature_c": round(r.peak_temperature_c, 3),
            "fused_area_mm2": round(r.fused_area_mm2, 6),
            "nugget_diameter_mm": round(r.nugget_diameter_mm, 6),
            "porosity_pct": round(r.porosity_pct, 6),
            "spatter_mass_mg": round(r.spatter_mass_mg, 6),
            "intermetallic_thickness_um": round(r.intermetallic_thickness_um, 6),
            "hardness_hv": round(r.hardness_hv, 6),
            "bond_integrity_score": round(r.bond_integrity_score, 6),
            "immediate_shear_strength_n": round(r.immediate_shear_strength_n, 6),
            "joint_resistance_mohm": round(r.joint_resistance_mohm, 6),
        }
        for r in qualities
    ]

    performance_dicts = [
        {
            "sample_id": r.sample_id,
            "cycles_to_failure": int(r.cycles_to_failure),
            "resistance_growth_pct_1000": round(r.resistance_growth_pct_1000, 6),
            "retained_strength_pct_1000": round(r.retained_strength_pct_1000, 6),
            "delamination_probability": round(r.delamination_probability, 6),
            "failure_mode": r.failure_mode,
        }
        for r in performances
    ]

    inputs_csv = os.path.join(out_dir, "inputs.csv")
    quality_csv = os.path.join(out_dir, "quality.csv")
    performance_csv = os.path.join(out_dir, "performance.csv")
    combined_csv = os.path.join(out_dir, "combined.csv")
    metadata_json = os.path.join(out_dir, "metadata.json")

    write_csv(inputs_csv, INPUT_FIELDS, input_dicts)
    write_csv(quality_csv, QUALITY_FIELDS, quality_dicts)
    write_csv(performance_csv, PERFORMANCE_FIELDS, performance_dicts)

    # Merge
    perf_map = {r["sample_id"]: r for r in performance_dicts}
    qual_map = {r["sample_id"]: r for r in quality_dicts}
    combined_rows: List[dict] = []
    for inp_row in input_dicts:
        sid = inp_row["sample_id"]
        combined = {**inp_row, **qual_map[sid], **perf_map[sid]}
        combined_rows.append(combined)

    write_csv(combined_csv, INPUT_FIELDS + QUALITY_FIELDS[1:] + PERFORMANCE_FIELDS[1:], combined_rows)

    # Metadata
    write_metadata(metadata_json)

    # Zip
    zip_path = os.path.join(out_dir, "welding_dataset.zip")
    zip_outputs(zip_path, [inputs_csv, quality_csv, performance_csv, combined_csv, metadata_json], base_dir=out_dir)

    print(f"Generated {len(inputs)} samples.")
    print(f"Outputs written to: {out_dir}")
    print(f"Archive: {zip_path}")


if __name__ == "__main__":
    main()
