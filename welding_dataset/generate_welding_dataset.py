#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator: Dataset for ML-Driven Inverse Design of Welding Parameters

Creates three parts + combined dataset:
- Part 1: Input Parameters (Design Space)
- Part 2: Characterization & Quality Metrics (Forward Outputs)
- Part 3: Performance & Validation Metrics (Inverse Targets)

Also produces:
- Combined CSV
- Train/Val/Test splits (stratified by technique and reliability class)
- Sample subset
- Schema (JSON) with units and descriptions
- Metadata (JSON) with summary stats
- README.md (data dictionary)
- Zip archive bundling everything

This generator is designed to be deterministic (fixed seed) while producing
realistic, correlated variables with domain-inspired heuristics.
"""
from __future__ import annotations

import json
import math
import os
import random
import statistics
import zipfile
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# ------------------------------- Configuration -------------------------------
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
SPLITS_DIR = os.path.join(DATA_DIR, "splits")

DEFAULT_NUM_ROWS = 9000  # total rows across all techniques
TRAIN_FRAC, VAL_FRAC, TEST_FRAC = 0.70, 0.15, 0.15

TECHNIQUES = ["USW", "Laser", "RSW"]

MATERIALS = [
    {"name": "Copper", "symbol": "Cu", "thermal_cond_W_mK": 400.0, "melting_C": 1085.0, "resistivity_uOhm_cm": 1.68},
    {"name": "Aluminum", "symbol": "Al", "thermal_cond_W_mK": 237.0, "melting_C": 660.0, "resistivity_uOhm_cm": 2.82},
    {"name": "Nickel", "symbol": "Ni", "thermal_cond_W_mK": 91.0, "melting_C": 1455.0, "resistivity_uOhm_cm": 6.99},
    {"name": "StainlessSteel", "symbol": "SS304", "thermal_cond_W_mK": 16.0, "melting_C": 1400.0, "resistivity_uOhm_cm": 72.0},
]

COATINGS = [
    ("Bare", 0.40),
    ("Nickel-plated", 0.22),
    ("Tin-plated", 0.14),
    ("Oxide", 0.12),
    ("Carbon-coated", 0.07),
    ("Anodized", 0.05),
]

# Technique-specific parameter ranges (approximate, domain-inspired)
PARAM_RANGES = {
    "USW": {
        "power_W": (600, 2600),
        "amplitude_um": (15, 60),
        "force_N": (150, 1200),
        "weld_time_ms": (100, 600),
    },
    "Laser": {
        "power_W": (200, 3000),  # avg power if CW
        "pulse_energy_J": (0.4, 12.0),
        "pulse_frequency_Hz": (10, 300),
        "speed_mm_s": (5, 120),
        "weld_time_ms": (50, 3000),
    },
    "RSW": {
        "power_W": (1000, 8000),
        "force_N": (300, 2500),
        "weld_time_ms": (50, 500),
    },
}

ENV_RANGES = {
    "preheat_temp_C": (-10, 120),
    "ambient_humidity_pct": (10, 80),
}

TAB_THICKNESS_RANGE_UM = (30, 250)  # typical tab thickness range
CLAMP_AREA_RANGE_MM2 = (4.0, 25.0)

# Material pair weights per technique (for more realistic sampling)
PAIR_WEIGHTS = {
    "USW": {
        ("Cu", "Al"): 0.40,
        ("Al", "Al"): 0.20,
        ("Cu", "Cu"): 0.10,
        ("Ni", "Cu"): 0.15,
        ("Ni", "Al"): 0.10,
        ("SS304", "Ni"): 0.05,
    },
    "Laser": {
        ("Cu", "Cu"): 0.25,
        ("Ni", "Cu"): 0.20,
        ("Cu", "Al"): 0.25,
        ("Al", "Al"): 0.15,
        ("SS304", "Ni"): 0.10,
        ("Cu", "SS304"): 0.05,
    },
    "RSW": {
        ("Ni", "Cu"): 0.25,
        ("Cu", "Cu"): 0.20,
        ("SS304", "Ni"): 0.25,
        ("Cu", "Al"): 0.10,
        ("Al", "Al"): 0.10,
        ("Cu", "SS304"): 0.10,
    },
}

# ------------------------------ Helper functions -----------------------------

def _choose_coating() -> str:
    names, weights = zip(*COATINGS)
    return random.choices(names, weights=weights, k=1)[0]


def _material_by_symbol(symbol: str) -> Dict:
    for m in MATERIALS:
        if m["symbol"] == symbol:
            return m
    raise KeyError(symbol)


def _choose_material_pair(technique: str) -> Tuple[Dict, Dict]:
    weights = PAIR_WEIGHTS[technique]
    pairs, pair_w = zip(*weights.items())
    pair = random.choices(pairs, weights=pair_w, k=1)[0]
    a, c = pair
    return _material_by_symbol(a), _material_by_symbol(c)


def _uniform(a: float, b: float) -> float:
    return a + (b - a) * random.random()


def _normal(mean: float, sd: float) -> float:
    return float(np.random.normal(mean, sd))


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _technique_params(technique: str) -> Dict[str, float]:
    r = PARAM_RANGES[technique]
    p = {}
    if technique == "USW":
        p["power_W"] = _uniform(*r["power_W"])  # instantaneous power
        p["amplitude_um"] = _uniform(*r["amplitude_um"])
        p["force_N"] = _uniform(*r["force_N"])  # clamping force
        p["weld_time_ms"] = _uniform(*r["weld_time_ms"])
        # Not applicable for USW
        p["speed_mm_s"] = np.nan
        p["pulse_energy_J"] = np.nan
        p["pulse_frequency_Hz"] = np.nan
    elif technique == "Laser":
        p["power_W"] = _uniform(*r["power_W"])  # average power (CW) or equivalent
        p["speed_mm_s"] = _uniform(*r["speed_mm_s"])  # travel speed
        p["weld_time_ms"] = _uniform(*r["weld_time_ms"])  # duration on seam
        # Simulate mixed CW/pulsed regimes by sampling pulse params sometimes
        if random.random() < 0.7:
            p["pulse_energy_J"] = _uniform(*r["pulse_energy_J"])  # per pulse
            p["pulse_frequency_Hz"] = _uniform(*r["pulse_frequency_Hz"])  # pulses/s
        else:
            p["pulse_energy_J"] = np.nan
            p["pulse_frequency_Hz"] = np.nan
        # Not applicable for Laser
        p["amplitude_um"] = np.nan
        p["force_N"] = _uniform(150, 1000)  # fixturing force still matters
    elif technique == "RSW":
        p["power_W"] = _uniform(*r["power_W"])  # Joule heating proxy
        p["force_N"] = _uniform(*r["force_N"])  # electrode force
        p["weld_time_ms"] = _uniform(*r["weld_time_ms"])  # squeeze+hold window
        # Not applicable for RSW
        p["amplitude_um"] = np.nan
        p["speed_mm_s"] = np.nan
        p["pulse_energy_J"] = np.nan
        p["pulse_frequency_Hz"] = np.nan
    else:
        raise ValueError(technique)
    return p


def _compute_energy(technique: str, params: Dict[str, float]) -> Tuple[float, float]:
    """Returns (total_energy_J, linear_energy_density_J_per_mm or nan).
    """
    time_s = params["weld_time_ms"] / 1000.0
    if technique == "USW":
        # Efficiency accounts for mechanical->frictional heating; amplitude influences
        eff = 0.55 + 0.25 * (params["amplitude_um"] - 15) / (60 - 15)
        eff = _clamp(eff, 0.45, 0.80)
        energy_J = params["power_W"] * time_s * eff
        return energy_J, float("nan")
    if technique == "Laser":
        # CW baseline
        energy_cw = params["power_W"] * time_s
        # Pulsed contribution if present
        if not math.isnan(params["pulse_energy_J"]) and not math.isnan(params["pulse_frequency_Hz"]):
            pulses = params["pulse_frequency_Hz"] * time_s
            energy_pulsed = params["pulse_energy_J"] * pulses
        else:
            energy_pulsed = 0.0
        total_energy = 0.6 * energy_cw + 0.4 * energy_pulsed  # mixed assumption
        if not math.isnan(params["speed_mm_s"]) and params["speed_mm_s"] > 0:
            led = params["power_W"] / params["speed_mm_s"]  # J/mm
        else:
            led = float("nan")
        return total_energy, led
    if technique == "RSW":
        # Efficiency of Joule heating (contact-dependent)
        eff = 0.55 + 0.15 * random.random()
        # Slight upweight with higher force (better contact)
        eff *= (1.0 + 0.05 * (params["force_N"] - 300) / (2500 - 300))
        eff = _clamp(eff, 0.45, 0.80)
        energy_J = params["power_W"] * time_s * eff
        return energy_J, float("nan")
    raise ValueError(technique)


def _coating_contact_factor(coating: str) -> float:
    # Lower is better for contact resistance
    table = {
        "Nickel-plated": 0.7,
        "Tin-plated": 0.8,
        "Bare": 1.0,
        "Carbon-coated": 1.1,
        "Oxide": 1.6,
        "Anodized": 2.2,
    }
    return table.get(coating, 1.0)


def _material_strength_factor(a: Dict, c: Dict) -> float:
    # Rough baseline for static strength potential by pair
    pair = {frozenset({"Cu", "Cu"}): 1.15,
            frozenset({"Al", "Al"}): 0.95,
            frozenset({"Ni", "Ni"}): 1.10,
            frozenset({"SS304", "SS304"}): 1.05}.get(frozenset({a["symbol"], c["symbol"]}), 1.0)
    # Dissimilar metal adjustments
    is_cu_al = ({a["symbol"], c["symbol"]} == {"Cu", "Al"})
    if is_cu_al:
        pair *= 0.95  # IMC sensitivity
    if {a["symbol"], c["symbol"]} == {"Ni", "SS304"}:
        pair *= 1.10
    return pair


def _compute_characterization(
    technique: str,
    params: Dict[str, float],
    energy_J: float,
    led_J_per_mm: float,
    anode: Dict,
    cathode: Dict,
    tab_thickness_um: float,
    clamp_area_mm2: float,
    preheat_C: float,
    humidity_pct: float,
    coating: str,
) -> Dict[str, float]:
    cond = 0.5 * (anode["thermal_cond_W_mK"] + cathode["thermal_cond_W_mK"])  # W/m-K
    cond_factor = 1.0 + cond / 300.0  # higher -> more heat dissipation
    thickness_factor = 0.8 + (tab_thickness_um / 250.0)  # 0.8 .. 1.8

    # Pressure from force and clamp area
    force_N = params.get("force_N", np.nan)
    if math.isnan(force_N):
        force_N = _uniform(150, 1000)
    pressure_MPa = (force_N / (clamp_area_mm2 * 1e-6)) / 1e6  # N / m^2 -> MPa
    pressure_factor = 1.0 + 0.20 * _clamp((pressure_MPa - 5.0) / 20.0, -0.5, 1.5)

    effective_energy = energy_J / (cond_factor * thickness_factor) * pressure_factor

    # Nugget diameter model (bounded)
    d_mm = 0.85 * (effective_energy + 1e-6) ** 0.38
    if technique == "Laser" and not math.isnan(led_J_per_mm):
        d_mm *= _clamp(0.8 + 0.6 * _sigmoid((led_J_per_mm - 10) / 6), 0.6, 1.6)
    d_mm = _clamp(d_mm + _normal(0.0, 0.15), 0.3, 6.0)
    bond_area_mm2 = math.pi * (d_mm / 2) ** 2

    # Porosity model: rises with over/under energy, humidity, oxide
    tech_opt = {"USW": 200.0, "Laser": 400.0, "RSW": 300.0}[technique]
    tech_over = {"USW": 600.0, "Laser": 900.0, "RSW": 800.0}[technique]
    under = max(0.0, 1.0 - effective_energy / tech_opt)
    over = max(0.0, effective_energy / tech_over - 1.0)
    coating_factor = {"Oxide": 1.4, "Anodized": 1.6}.get(coating, 1.0)
    porosity_pct = 5.0 + 8.0 * under + 10.0 * over
    porosity_pct *= coating_factor * (1.0 + 0.004 * (humidity_pct - 40.0))
    porosity_pct = _clamp(porosity_pct + _normal(0.0, 1.5), 0.2, 35.0)

    # Intermetallic thickness (µm) — stronger dependence for Cu-Al
    is_cu_al = ({anode["symbol"], cathode["symbol"]} == {"Cu", "Al"})
    imc_base = 0.6 + 0.011 * effective_energy + 0.015 * max(0.0, preheat_C - 25.0)
    if is_cu_al:
        imc_base *= 1.4
    imc_thickness_um = _clamp(imc_base + _normal(0.0, 0.25), 0.1, 12.0)

    # Peak temperature and HAZ width
    peak_temp_C = _clamp(preheat_C + 90.0 + 0.6 * effective_energy / (1.0 + cond / 200.0), 100.0, 1200.0)
    haz_width_mm = _clamp(0.08 + 0.003 * effective_energy / (1.0 + cond / 300.0), 0.02, 3.5)

    # Electrical contact resistance (mΩ)
    base_contact_mOhm = 0.8 * _coating_contact_factor(coating)
    base_contact_mOhm *= 1.0 + 0.003 * (humidity_pct - 40.0)
    # Pressure reduces contact resistance; higher nugget size helps
    contact_resistance_mOhm = base_contact_mOhm / (1.0 + 0.012 * (pressure_MPa - 5.0))
    contact_resistance_mOhm /= _clamp(0.7 + 0.15 * d_mm, 0.8, 2.5)
    contact_resistance_mOhm = _clamp(contact_resistance_mOhm + _normal(0.0, 0.05), 0.08, 6.0)

    # Strength models (N)
    mat_factor = _material_strength_factor(anode, cathode)
    base_strength = 260.0 * bond_area_mm2 * mat_factor  # nominal scale
    # Penalize high porosity and too-thick IMC (> ~2.2 µm best)
    porosity_mult = _clamp(1.0 - 0.75 * (porosity_pct / 35.0), 0.55, 1.0)
    imc_opt = 2.2
    imc_penalty = _clamp(1.0 - 0.22 * abs(imc_thickness_um - imc_opt) / imc_opt, 0.55, 1.05)
    tensile_shear_strength_N = _clamp(base_strength * porosity_mult * imc_penalty + _normal(0.0, 30.0), 80.0, 6500.0)
    peel_strength_N = _clamp(0.65 * tensile_shear_strength_N + _normal(0.0, 20.0), 40.0, 4500.0)

    # Visual defects score (0-100): higher is better
    defect_score = 100.0
    defect_score -= 2.5 * porosity_pct
    defect_score -= 12.0 * max(0.0, imc_thickness_um - 6.0) / 6.0
    defect_score -= 8.0 * max(0.0, 0.9 - d_mm) / 0.9
    visual_defect_score = _clamp(defect_score + _normal(0.0, 4.0), 5.0, 100.0)

    # Microhardness HV (approx. combined influence)
    base_hv = 0.5 * (120.0 + 0.04 * (anode["melting_C"] + cathode["melting_C"]))
    microhardness_HV = _clamp(base_hv + 8.0 * (haz_width_mm - 0.3) + _normal(0.0, 5.0), 40.0, 380.0)

    # Immediate pass/fail heuristic
    pass_fail = (
        (d_mm >= 0.8) and (porosity_pct <= 12.0) and (contact_resistance_mOhm <= 2.0)
        and (tensile_shear_strength_N >= 300.0)
    )

    return {
        "nugget_diameter_mm": round(d_mm, 3),
        "bond_area_mm2": round(bond_area_mm2, 3),
        "porosity_pct": round(porosity_pct, 3),
        "imc_thickness_um": round(imc_thickness_um, 3),
        "peak_temp_C": round(peak_temp_C, 1),
        "haz_width_mm": round(haz_width_mm, 3),
        "contact_resistance_mOhm": round(contact_resistance_mOhm, 4),
        "tensile_shear_strength_N": round(tensile_shear_strength_N, 1),
        "peel_strength_N": round(peel_strength_N, 1),
        "visual_defect_score": round(visual_defect_score, 1),
        "microhardness_HV": round(microhardness_HV, 1),
        "forward_pass_fail": bool(pass_fail),
        "pressure_MPa": round(pressure_MPa, 3),
        "effective_energy_J": round(effective_energy, 3),
    }


def _compute_performance_targets(
    technique: str,
    char: Dict[str, float],
    anode: Dict,
    cathode: Dict,
    preheat_C: float,
    humidity_pct: float,
    coating: str,
) -> Dict[str, float]:
    # Factors
    porosity = char["porosity_pct"]
    imc = char["imc_thickness_um"]
    d_mm = char["nugget_diameter_mm"]
    contact_mOhm = char["contact_resistance_mOhm"]
    haz_mm = char["haz_width_mm"]
    tensile = char["tensile_shear_strength_N"]

    is_cu_al = ({anode["symbol"], cathode["symbol"]} == {"Cu", "Al"})

    # Resistance growth (% after 1000 cycles) increases with porosity, IMC, humidity, oxide
    coat_factor = {"Oxide": 1.25, "Anodized": 1.35}.get(coating, 1.0)
    res_growth = 4.0 + 0.6 * porosity + 0.9 * max(0.0, imc - 2.2) + 0.05 * max(0.0, humidity_pct - 30)
    if is_cu_al:
        res_growth *= 1.15
    res_growth *= coat_factor
    res_growth = _clamp(res_growth + _normal(0.0, 2.0), 1.0, 85.0)

    # Strength retention after 1000 cycles (%)
    base_ret = 96.0 - 0.45 * porosity - 1.8 * max(0.0, imc - 2.0) - 0.08 * max(0.0, preheat_C - 40)
    base_ret -= 1.2 * max(0.0, 0.9 - d_mm)
    base_ret += 0.02 * max(0.0, tensile - 1200.0) / 10.0
    if is_cu_al:
        base_ret -= 2.5
    strength_retention = _clamp(base_ret + _normal(0.0, 1.5), 30.0, 100.0)

    # Cycles to failure (thermal cycling) — broad distribution shaped by metrics
    reliability_score = 0.0
    reliability_score += 2.2 * _clamp((d_mm - 0.8) / 2.5, 0.0, 1.0)
    reliability_score += 2.0 * _clamp((12.0 - porosity) / 12.0, 0.0, 1.0)
    reliability_score += 1.6 * _clamp((2.5 - abs(imc - 2.0)) / 2.5, 0.0, 1.0)
    reliability_score += 1.0 * _clamp((1200.0 - contact_mOhm * 1000.0) / 1200.0, 0.0, 1.0)
    reliability_score += 0.5 * _clamp((haz_mm - 0.08) / 2.0, 0.0, 1.0)

    base_cycles = 600 + 1800 * reliability_score + 0.05 * tensile
    if is_cu_al:
        base_cycles *= 0.92
    cycles_to_failure = _clamp(base_cycles * (0.9 + 0.2 * random.random()) + _normal(0.0, 60.0), 80.0, 12000.0)

    # Crack growth (mm)
    crack_growth_mm = _clamp(0.05 + 0.02 * porosity + 0.015 * max(0.0, imc - 2.2) + _normal(0.0, 0.03), 0.0, 5.0)

    # Delamination probability
    delam_logit = -1.2 + 0.12 * porosity + 0.22 * max(0.0, imc - 2.0) - 0.5 * _clamp((d_mm - 0.8) / 2.0, 0.0, 1.0)
    delam_prob = _clamp(_sigmoid(delam_logit) + _normal(0.0, 0.03), 0.0, 1.0)

    # Reliability class
    if cycles_to_failure >= 3000 and strength_retention >= 90.0 and res_growth <= 15.0:
        reliability_class = "A"
    elif cycles_to_failure >= 1500 and strength_retention >= 75.0 and res_growth <= 35.0:
        reliability_class = "B"
    else:
        reliability_class = "C"

    return {
        "resistance_growth_pct_1000cyc": round(res_growth, 2),
        "strength_retention_pct_1000cyc": round(strength_retention, 2),
        "cycles_to_failure": int(round(cycles_to_failure)),
        "crack_growth_mm": round(crack_growth_mm, 3),
        "delamination_probability": round(delam_prob, 4),
        "reliability_class": reliability_class,
    }


# ------------------------------- Data generation -----------------------------

def _generate_rows(num_rows: int) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    rows_per_tech = num_rows // len(TECHNIQUES)

    for technique in TECHNIQUES:
        for _ in range(rows_per_tech):
            # Materials & environment
            anode, cathode = _choose_material_pair(technique)
            preheat_C = _uniform(*ENV_RANGES["preheat_temp_C"])  # °C
            humidity_pct = _uniform(*ENV_RANGES["ambient_humidity_pct"])  # %
            tab_thickness_um = _uniform(*TAB_THICKNESS_RANGE_UM)
            coating = _choose_coating()
            clamp_area_mm2 = _uniform(*CLAMP_AREA_RANGE_MM2)

            # Process params
            params = _technique_params(technique)
            energy_J, led = _compute_energy(technique, params)

            # Characterization results
            char = _compute_characterization(
                technique=technique,
                params=params,
                energy_J=energy_J,
                led_J_per_mm=led,
                anode=anode,
                cathode=cathode,
                tab_thickness_um=tab_thickness_um,
                clamp_area_mm2=clamp_area_mm2,
                preheat_C=preheat_C,
                humidity_pct=humidity_pct,
                coating=coating,
            )

            # Performance targets
            perf = _compute_performance_targets(
                technique=technique,
                char=char,
                anode=anode,
                cathode=cathode,
                preheat_C=preheat_C,
                humidity_pct=humidity_pct,
                coating=coating,
            )

            row: Dict[str, object] = {
                # Part 1: inputs
                "technique": technique,
                "anode_material": anode["name"],
                "anode_symbol": anode["symbol"],
                "cathode_material": cathode["name"],
                "cathode_symbol": cathode["symbol"],
                "tab_thickness_um": round(tab_thickness_um, 1),
                "surface_coating": coating,
                "power_W": round(params["power_W"], 2) if not math.isnan(params["power_W"]) else np.nan,
                "pulse_energy_J": round(params["pulse_energy_J"], 4) if not math.isnan(params["pulse_energy_J"]) else np.nan,
                "amplitude_um": round(params["amplitude_um"], 2) if not math.isnan(params["amplitude_um"]) else np.nan,
                "force_N": round(params["force_N"], 2) if not math.isnan(params["force_N"]) else np.nan,
                "weld_time_ms": round(params["weld_time_ms"], 1),
                "speed_mm_s": round(params["speed_mm_s"], 3) if not math.isnan(params["speed_mm_s"]) else np.nan,
                "pulse_frequency_Hz": round(params["pulse_frequency_Hz"], 3) if not math.isnan(params["pulse_frequency_Hz"]) else np.nan,
                "preheat_temp_C": round(preheat_C, 1),
                "ambient_humidity_pct": round(humidity_pct, 1),
                "clamp_area_mm2": round(clamp_area_mm2, 2),
                "linear_energy_density_J_per_mm": round(led, 4) if not (isinstance(led, float) and math.isnan(led)) else np.nan,
                "total_energy_input_J": round(energy_J, 3),
                # Part 2: characterization
                **char,
                # Part 3: performance targets
                **perf,
            }

            rows.append(row)

    # If num_rows not divisible by techniques, add a few extra randomized rows
    while len(rows) < num_rows:
        technique = random.choice(TECHNIQUES)
        anode, cathode = _choose_material_pair(technique)
        preheat_C = _uniform(*ENV_RANGES["preheat_temp_C"])  # °C
        humidity_pct = _uniform(*ENV_RANGES["ambient_humidity_pct"])  # %
        tab_thickness_um = _uniform(*TAB_THICKNESS_RANGE_UM)
        coating = _choose_coating()
        clamp_area_mm2 = _uniform(*CLAMP_AREA_RANGE_MM2)
        params = _technique_params(technique)
        energy_J, led = _compute_energy(technique, params)
        char = _compute_characterization(
            technique, params, energy_J, led, anode, cathode, tab_thickness_um, clamp_area_mm2, preheat_C, humidity_pct, coating
        )
        perf = _compute_performance_targets(technique, char, anode, cathode, preheat_C, humidity_pct, coating)
        rows.append({
            "technique": technique,
            "anode_material": anode["name"],
            "anode_symbol": anode["symbol"],
            "cathode_material": cathode["name"],
            "cathode_symbol": cathode["symbol"],
            "tab_thickness_um": round(tab_thickness_um, 1),
            "surface_coating": coating,
            "power_W": round(params["power_W"], 2) if not math.isnan(params["power_W"]) else np.nan,
            "pulse_energy_J": round(params["pulse_energy_J"], 4) if not math.isnan(params["pulse_energy_J"]) else np.nan,
            "amplitude_um": round(params["amplitude_um"], 2) if not math.isnan(params["amplitude_um"]) else np.nan,
            "force_N": round(params["force_N"], 2) if not math.isnan(params["force_N"]) else np.nan,
            "weld_time_ms": round(params["weld_time_ms"], 1),
            "speed_mm_s": round(params["speed_mm_s"], 3) if not math.isnan(params["speed_mm_s"]) else np.nan,
            "pulse_frequency_Hz": round(params["pulse_frequency_Hz"], 3) if not math.isnan(params["pulse_frequency_Hz"]) else np.nan,
            "preheat_temp_C": round(preheat_C, 1),
            "ambient_humidity_pct": round(humidity_pct, 1),
            "clamp_area_mm2": round(clamp_area_mm2, 2),
            "linear_energy_density_J_per_mm": round(led, 4) if not (isinstance(led, float) and math.isnan(led)) else np.nan,
            "total_energy_input_J": round(energy_J, 3),
            **char,
            **perf,
        })

    return rows


# ------------------------------- Output helpers ------------------------------

def _build_schema() -> Dict[str, Dict[str, str]]:
    # Minimal schema; kept in sync with column names
    def col(unit: str, desc: str, dtype: str = "number"):
        return {"unit": unit, "description": desc, "dtype": dtype}

    schema: Dict[str, Dict[str, str]] = {
        # Inputs
        "technique": col("-", "Welding technique used (USW/Laser/RSW)", "category"),
        "anode_material": col("-", "Anode/base material name", "category"),
        "anode_symbol": col("-", "Anode/base material symbol", "category"),
        "cathode_material": col("-", "Cathode/base material name", "category"),
        "cathode_symbol": col("-", "Cathode/base material symbol", "category"),
        "tab_thickness_um": col("µm", "Tab thickness"),
        "surface_coating": col("-", "Surface finish/coating", "category"),
        "power_W": col("W", "Power (USW/RSW avg; Laser avg if CW)"),
        "pulse_energy_J": col("J", "Laser pulse energy (if pulsed)"),
        "amplitude_um": col("µm", "USW vibration amplitude"),
        "force_N": col("N", "Clamping/electrode force"),
        "weld_time_ms": col("ms", "Weld dwell time"),
        "speed_mm_s": col("mm/s", "Laser travel speed"),
        "pulse_frequency_Hz": col("Hz", "Laser pulse repetition frequency"),
        "preheat_temp_C": col("°C", "Pre-heat temperature of samples"),
        "ambient_humidity_pct": col("%", "Ambient relative humidity"),
        "clamp_area_mm2": col("mm²", "Approximate clamp/electrode contact area"),
        "linear_energy_density_J_per_mm": col("J/mm", "Laser linear energy density (if available)"),
        "total_energy_input_J": col("J", "Estimated total energy input"),
        # Characterization
        "nugget_diameter_mm": col("mm", "Weld nugget diameter (post-join)"),
        "bond_area_mm2": col("mm²", "Bonded area (π·d²/4)"),
        "porosity_pct": col("%", "Measured porosity in weld region"),
        "imc_thickness_um": col("µm", "Intermetallic compound layer thickness"),
        "peak_temp_C": col("°C", "Peak temperature observed/estimated"),
        "haz_width_mm": col("mm", "Heat-affected zone width"),
        "contact_resistance_mOhm": col("mΩ", "Initial electrical contact resistance"),
        "tensile_shear_strength_N": col("N", "Tensile shear strength at room temperature"),
        "peel_strength_N": col("N", "Peel strength at room temperature"),
        "visual_defect_score": col("0-100", "Higher = fewer visual defects", "score"),
        "microhardness_HV": col("HV", "Microhardness (Vickers)"),
        "forward_pass_fail": col("bool", "Immediate pass/fail screen", "boolean"),
        "pressure_MPa": col("MPa", "Contact pressure derived from force/area"),
        "effective_energy_J": col("J", "Effective energy after conduction/pressure factors"),
        # Performance
        "resistance_growth_pct_1000cyc": col("%", "Resistance growth after 1000 thermal cycles"),
        "strength_retention_pct_1000cyc": col("%", "Strength retention after 1000 cycles"),
        "cycles_to_failure": col("cycles", "Cycles to failure in thermal cycling", "integer"),
        "crack_growth_mm": col("mm", "Crack growth after thermal cycling"),
        "delamination_probability": col("0-1", "Probability of delamination under cycling", "probability"),
        "reliability_class": col("A/B/C", "Performance class (A best)", "category"),
    }
    return schema


def _write_readme(schema: Dict[str, Dict[str, str]], total_rows: int) -> None:
    readme_path = os.path.join(ROOT_DIR, "README.md")
    lines: List[str] = []
    lines.append("# ML-Driven Inverse Design of Welding Parameters — Fabricated Dataset")
    lines.append("")
    lines.append("This package contains a fully fabricated, self-consistent dataset for research and prototyping.")
    lines.append("It is designed for both forward modeling (quality prediction) and inverse design (parameter selection for target reliability under thermal cycling).")
    lines.append("")
    lines.append("## Contents")
    lines.append("- `data/dataset.csv`: combined table with inputs, characterization, and performance targets")
    lines.append("- `data/part1_inputs.csv`: only input parameters (design space)")
    lines.append("- `data/part2_characterization.csv`: immediate post-join quality metrics")
    lines.append("- `data/part3_performance.csv`: thermal cycling performance/targets")
    lines.append("- `data/splits/train.csv`, `val.csv`, `test.csv`: ML splits (stratified)")
    lines.append("- `schema.json`: column units, types, and descriptions")
    lines.append("- `metadata.json`: dataset-level stats and provenance")
    lines.append("")
    lines.append("## Rows")
    lines.append(f"Total rows: {total_rows}")
    lines.append("")
    lines.append("## Key Columns (units)")
    for k, v in schema.items():
        lines.append(f"- **{k}** ({v['unit']}): {v['description']}")
    lines.append("")
    lines.append("## Notes")
    lines.append("- Values are fabricated using domain-inspired heuristics; they are not measured data.")
    lines.append("- Missing values appear in technique-specific columns that do not apply (e.g., `amplitude_um` for Laser).")
    lines.append("- Splits are stratified by `technique` and `reliability_class` with a fixed random seed for reproducibility.")
    lines.append("- This dataset is suitable for supervised ML (forward) and conditional generation/inverse design experiments.")

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _write_schema(schema: Dict[str, Dict[str, str]]) -> None:
    schema_path = os.path.join(ROOT_DIR, "schema.json")
    with open(schema_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)


def _write_metadata(df: pd.DataFrame) -> None:
    meta_path = os.path.join(ROOT_DIR, "metadata.json")
    meta = {
        "num_rows": int(df.shape[0]),
        "num_columns": int(df.shape[1]),
        "technique_counts": df["technique"].value_counts().to_dict(),
        "reliability_class_counts": df["reliability_class"].value_counts().to_dict(),
        "forward_pass_rate": float(df["forward_pass_fail"].mean()),
        "columns": list(df.columns),
        "seed": RANDOM_SEED,
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def _write_csvs(df: pd.DataFrame) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SPLITS_DIR, exist_ok=True)

    # Combined
    df.to_csv(os.path.join(DATA_DIR, "dataset.csv"), index=False)

    # Parts
    part1_cols = [
        "technique", "anode_material", "anode_symbol", "cathode_material", "cathode_symbol",
        "tab_thickness_um", "surface_coating", "power_W", "pulse_energy_J", "amplitude_um",
        "force_N", "weld_time_ms", "speed_mm_s", "pulse_frequency_Hz", "preheat_temp_C",
        "ambient_humidity_pct", "clamp_area_mm2", "linear_energy_density_J_per_mm", "total_energy_input_J"
    ]
    part2_cols = [
        "nugget_diameter_mm", "bond_area_mm2", "porosity_pct", "imc_thickness_um", "peak_temp_C",
        "haz_width_mm", "contact_resistance_mOhm", "tensile_shear_strength_N", "peel_strength_N",
        "visual_defect_score", "microhardness_HV", "forward_pass_fail", "pressure_MPa", "effective_energy_J"
    ]
    part3_cols = [
        "resistance_growth_pct_1000cyc", "strength_retention_pct_1000cyc", "cycles_to_failure",
        "crack_growth_mm", "delamination_probability", "reliability_class"
    ]

    df[part1_cols].to_csv(os.path.join(DATA_DIR, "part1_inputs.csv"), index=False)
    df[part2_cols].to_csv(os.path.join(DATA_DIR, "part2_characterization.csv"), index=False)
    df[part3_cols].to_csv(os.path.join(DATA_DIR, "part3_performance.csv"), index=False)

    # Sample
    sample_n = min(100, len(df))
    df.sample(n=sample_n, random_state=RANDOM_SEED).to_csv(os.path.join(DATA_DIR, "sample_100.csv"), index=False)

    # Splits (stratify by technique + reliability class)
    strat_key = df["technique"] + "_" + df["reliability_class"]
    groups = df.groupby(strat_key)
    train_parts, val_parts, test_parts = [], [], []

    rng = np.random.RandomState(RANDOM_SEED)
    for _, g in groups:
        idx = g.index.values
        rng.shuffle(idx)
        n = len(idx)
        n_train = int(round(n * TRAIN_FRAC))
        n_val = int(round(n * VAL_FRAC))
        n_test = n - n_train - n_val
        train_idx = idx[:n_train]
        val_idx = idx[n_train:n_train + n_val]
        test_idx = idx[n_train + n_val:]
        train_parts.append(df.loc[train_idx])
        val_parts.append(df.loc[val_idx])
        test_parts.append(df.loc[test_idx])

    train_df = pd.concat(train_parts).sample(frac=1.0, random_state=RANDOM_SEED)
    val_df = pd.concat(val_parts).sample(frac=1.0, random_state=RANDOM_SEED)
    test_df = pd.concat(test_parts).sample(frac=1.0, random_state=RANDOM_SEED)

    train_df.to_csv(os.path.join(SPLITS_DIR, "train.csv"), index=False)
    val_df.to_csv(os.path.join(SPLITS_DIR, "val.csv"), index=False)
    test_df.to_csv(os.path.join(SPLITS_DIR, "test.csv"), index=False)


def _zip_package() -> str:
    zip_path = os.path.join(ROOT_DIR, "welding_dataset_v1.zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        # Add README, schema, metadata
        for name in ["README.md", "schema.json", "metadata.json"]:
            p = os.path.join(ROOT_DIR, name)
            if os.path.exists(p):
                z.write(p, arcname=name)
        # Add data directory recursively
        for dirpath, _, filenames in os.walk(DATA_DIR):
            for fn in filenames:
                full = os.path.join(dirpath, fn)
                arc = os.path.relpath(full, ROOT_DIR)
                z.write(full, arcname=arc)
    return zip_path


# ------------------------------------- Main ----------------------------------

def main(num_rows: int = DEFAULT_NUM_ROWS) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    rows = _generate_rows(num_rows)
    df = pd.DataFrame(rows)

    _write_csvs(df)

    schema = _build_schema()
    _write_schema(schema)
    _write_metadata(df)
    _write_readme(schema, total_rows=len(df))

    zip_path = _zip_package()
    print(f"Wrote dataset rows: {len(df)}")
    print(f"Zip archive: {zip_path}")


if __name__ == "__main__":
    # Support NUM_ROWS env var override
    n_env = os.environ.get("NUM_ROWS")
    if n_env:
        try:
            n = int(n_env)
        except Exception:
            n = DEFAULT_NUM_ROWS
    else:
        n = DEFAULT_NUM_ROWS
    main(n)
