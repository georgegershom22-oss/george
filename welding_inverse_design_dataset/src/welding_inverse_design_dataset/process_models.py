from __future__ import annotations
from typing import Dict, Tuple
import numpy as np
import pandas as pd

from .constants import TECHNIQUES, SURFACE_FINISHES, COATINGS, SURFACE_FINISH_RA_UM
from .materials import MATERIALS

Technique = str

MATERIAL_PAIRS = [
    ("Copper_Cu", "Aluminum_1100"),
    ("Copper_Cu", "Aluminum_1050"),
    ("Copper_Cu", "Copper_Cu"),
    ("Aluminum_1100", "Aluminum_1100"),
    ("Nickel_Ni", "Copper_Cu"),
    ("Stainless_304", "Aluminum_1100"),
    ("CuNi_70_30", "Copper_Cu"),
]

TECHNIQUE_PROBS = np.array([0.5, 0.3, 0.2])  # USW, Laser, RSW
PAIR_PROBS = np.array([0.25, 0.15, 0.2, 0.1, 0.15, 0.05, 0.1])
PAIR_PROBS = PAIR_PROBS / PAIR_PROBS.sum()


def sample_process_parameters(n: int, rng: np.random.Generator) -> pd.DataFrame:
    techniques = rng.choice(TECHNIQUES, size=n, p=TECHNIQUE_PROBS)
    pair_idx = rng.choice(len(MATERIAL_PAIRS), size=n, p=PAIR_PROBS)
    anodes = [MATERIAL_PAIRS[i][0] for i in pair_idx]
    cathodes = [MATERIAL_PAIRS[i][1] for i in pair_idx]

    surface_finishes = rng.choice(SURFACE_FINISHES, size=n)
    coatings = rng.choice(COATINGS, size=n, p=[0.6, 0.2, 0.15, 0.05])

    anode_thickness_um = np.array([
        rng.uniform(60, 180) if "Aluminum" in a else rng.uniform(60, 150)
        for a in anodes
    ])
    cathode_thickness_um = np.array([
        rng.uniform(60, 180) if "Aluminum" in c else rng.uniform(60, 150)
        for c in cathodes
    ])

    preheat_temp_C = rng.choice([20.0, 40.0, 60.0, 80.0, 100.0, 120.0], size=n, p=[0.25,0.2,0.2,0.15,0.1,0.1])

    tool_contact_area_mm2 = rng.uniform(4.0, 25.0, size=n)
    weld_length_mm = rng.uniform(2.0, 10.0, size=n)
    spot_diameter_um = rng.uniform(100.0, 800.0, size=n)

    power_W = np.zeros(n)
    pulse_energy_J = np.full(n, np.nan)
    amplitude_um = np.full(n, np.nan)
    force_N = np.zeros(n)
    time_ms = np.zeros(n)
    speed_mm_s = np.full(n, np.nan)
    pulse_frequency_Hz = np.full(n, np.nan)

    for i, tech in enumerate(techniques):
        if tech == "USW":
            power_W[i] = rng.uniform(400, 4000)
            amplitude_um[i] = rng.uniform(8, 50)
            force_N[i] = rng.uniform(200, 1200)
            time_ms[i] = rng.uniform(50, 1000)
        elif tech == "Laser":
            power_W[i] = rng.uniform(100, 2000)
            speed_mm_s[i] = rng.uniform(5, 200)
            pulse_frequency_Hz[i] = rng.uniform(100, 5000)
            time_ms[i] = (weld_length_mm[i] / max(speed_mm_s[i], 1e-3)) * 1000.0
            pulse_energy_J[i] = power_W[i] / max(pulse_frequency_Hz[i], 1e-6)
            force_N[i] = rng.uniform(50, 300)  # fixturing/clamping
        else:  # RSW
            power_W[i] = rng.uniform(1000, 8000)  # effective power proxy
            force_N[i] = rng.uniform(1000, 3000)
            time_ms[i] = rng.uniform(50, 400)

    pressure_MPa = force_N / np.maximum(tool_contact_area_mm2, 1e-6)

    df = pd.DataFrame({
        "technique": techniques,
        "anode_material": anodes,
        "cathode_material": cathodes,
        "anode_thickness_um": anode_thickness_um,
        "cathode_thickness_um": cathode_thickness_um,
        "surface_finish": surface_finishes,
        "coating": coatings,
        "preheat_temperature_C": preheat_temp_C,
        "tool_contact_area_mm2": tool_contact_area_mm2,
        "weld_length_mm": weld_length_mm,
        "spot_diameter_um": spot_diameter_um,
        "power_W": power_W,
        "pulse_energy_J": pulse_energy_J,
        "amplitude_um": amplitude_um,
        "force_N": force_N,
        "pressure_MPa": pressure_MPa,
        "time_ms": time_ms,
        "speed_mm_s": speed_mm_s,
        "pulse_frequency_Hz": pulse_frequency_Hz,
    })

    return df
