from __future__ import annotations
from typing import Tuple
import numpy as np
import pandas as pd

from .materials import MATERIALS, Material
from .constants import COATING_ABSORPTION_BOOST


def _pair_props(anode: str, cathode: str) -> Tuple[Material, Material]:
    return MATERIALS[anode], MATERIALS[cathode]


def _effective_absorption(technique: str, an: Material, ca: Material, coating: str) -> float:
    if technique == "Laser":
        base = 0.5 * (an.laser_absorptivity_1 + ca.laser_absorptivity_1)
        base *= COATING_ABSORPTION_BOOST.get(coating, 1.0)
        return float(np.clip(base, 0.1, 0.95))
    if technique == "USW":
        return float(np.clip(0.5 * (an.ultrasonic_absorption_factor + ca.ultrasonic_absorption_factor), 0.6, 1.4))
    return 0.75  # RSW effective coupling proxy


def _effective_mass(an: Material, ca: Material, area_mm2: float, thickness_um_an: float, thickness_um_ca: float, technique: str, weld_length_mm: float, spot_diameter_um: float) -> float:
    area_m2 = area_mm2 * 1e-6
    thickness_m = (thickness_um_an + thickness_um_ca) * 1e-6
    if technique == "Laser":
        spot_m = max(spot_diameter_um, 50.0) * 1e-6
        track_area_m2 = spot_m * (weld_length_mm * 1e-3)
        area_m2 = max(area_m2, track_area_m2)
    density = 0.5 * (an.density_kg_m3 + ca.density_kg_m3)
    return density * area_m2 * max(thickness_m, 1e-6)


def compute_forward_outputs(df: pd.DataFrame) -> pd.DataFrame:
    n = len(df)
    energy_J = np.zeros(n)
    linear_energy_density_J_per_mm = np.zeros(n)
    peak_temp_C = np.zeros(n)
    interface_temp_C = np.zeros(n)
    haz_width_mm = np.zeros(n)
    cooling_rate_C_per_s = np.zeros(n)
    nugget_diameter_mm = np.zeros(n)
    bond_area_mm2 = np.zeros(n)
    contact_res_mOhm = np.zeros(n)
    porosity_fraction = np.zeros(n)
    void_count = np.zeros(n)
    immediate_lap_shear_N = np.zeros(n)
    microhardness_HV = np.zeros(n)
    imc_thickness_um = np.zeros(n)

    rng = np.random.default_rng(42)

    for i, row in df.iterrows():
        an = MATERIALS[row.anode_material]
        ca = MATERIALS[row.cathode_material]
        absorb = _effective_absorption(row.technique, an, ca, str(row.coating))

        if row.technique == "Laser":
            time_s = max(row.time_ms, 1.0) / 1000.0
            energy_J[i] = row.power_W * time_s * absorb
            linear_energy_density_J_per_mm[i] = row.power_W / max(row.speed_mm_s, 1e-3) * absorb
        elif row.technique == "USW":
            time_s = max(row.time_ms, 1.0) / 1000.0
            energy_J[i] = row.power_W * time_s * absorb
            linear_energy_density_J_per_mm[i] = 0.0
        else:  # RSW
            time_s = max(row.time_ms, 1.0) / 1000.0
            energy_J[i] = row.power_W * time_s * absorb
            linear_energy_density_J_per_mm[i] = 0.0

        m_eff = _effective_mass(an, ca, float(row.tool_contact_area_mm2), float(row.anode_thickness_um), float(row.cathode_thickness_um), row.technique, float(row.weld_length_mm), float(row.spot_diameter_um))
        cp_eff = 0.5 * (an.specific_heat_J_kgK + ca.specific_heat_J_kgK)
        k_eff = 0.5 * (an.thermal_conductivity_W_mK + ca.thermal_conductivity_W_mK)

        base_dT = energy_J[i] / max(m_eff * cp_eff, 1e-9)
        conduction_loss = np.sqrt(max(k_eff, 1e-6)) * 2.0
        preheat = float(row.preheat_temperature_C)
        peak_temp_C[i] = preheat + max(base_dT - conduction_loss, 5.0)
        interface_temp_C[i] = preheat + max(base_dT * 0.7 - conduction_loss * 0.5, 3.0)

        haz_width_mm[i] = float(np.clip(0.02 + 0.001 * (energy_J[i] ** 0.6) / (np.sqrt(k_eff) + 1.0), 0.02, 2.5))
        cooling_rate_C_per_s[i] = float(np.clip(80 + 600 * (k_eff / (k_eff + 50)) - 0.5 * preheat, 20, 1000))

        if row.technique == "Laser":
            d = 0.05 + 0.5 * (linear_energy_density_J_per_mm[i] / (linear_energy_density_J_per_mm[i] + 30))
            nugget_diameter_mm[i] = float(np.clip(d * 5.0, 0.1, 5.0))
        elif row.technique == "RSW":
            d = 0.05 + 0.6 * (energy_J[i] / (energy_J[i] + 60))
            nugget_diameter_mm[i] = float(np.clip(d * 6.0, 0.1, 6.5))
        else:  # USW forms bonded area rather than nugget
            d = 0.05 + 0.5 * (energy_J[i] / (energy_J[i] + 40))
            nugget_diameter_mm[i] = float(np.clip(d * 4.0, 0.1, 4.5))

        ra_um = row.surface_finish  # string
        # holm-like: R ~ C / sqrt(P) scaled by roughness
        roughness = 1.0
        if isinstance(ra_um, str):
            roughness = {
                "as_rolled": 1.0,
                "brushed": 0.9,
                "electroplated_Ni": 0.7,
                "electroplated_Ag": 0.65,
                "tinned_Sn": 0.8,
                "anodized": 0.95,
                "oxidized": 1.3,
            }.get(ra_um, 1.0)
        base_const = 8.0 * np.sqrt(0.5 * (an.electrical_resistivity_uOhm_m + ca.electrical_resistivity_uOhm_m))
        contact_res_mOhm[i] = float(np.clip(base_const * roughness / np.sqrt(max(row.pressure_MPa, 0.1)), 0.05, 20.0))

        # bonded area relates to d and pressure; saturating behavior
        bond_area_mm2[i] = float(np.clip(np.pi * (nugget_diameter_mm[i] / 2) ** 2 * (1.0 + 0.3 * np.tanh((row.pressure_MPa - 50) / 100)), 0.2, 80.0))

        # porosity U-shaped vs energy density; add roughness and coating impacts
        ed = energy_J[i] / max(row.weld_length_mm, 1e-3)
        u_shape = ((ed - 20) / 20) ** 2
        porosity_fraction[i] = float(np.clip(0.02 + 0.08 * u_shape + 0.01 * (roughness - 1.0), 0.0, 0.6))
        void_count[i] = int(np.clip(rng.normal(5 * porosity_fraction[i] * bond_area_mm2[i] ** 0.3, 2.0), 0, 200))

        strength_factor = (bond_area_mm2[i] ** 0.6) * (1.0 - 0.5 * porosity_fraction[i])
        mismatch = abs(an.cte_1e6_per_K - ca.cte_1e6_per_K) / 25.0
        immediate_lap_shear_N[i] = float(np.clip(50 + 12 * strength_factor - 20 * mismatch + 5 * np.sqrt(max(row.pressure_MPa, 0.01)), 30, 4000))

        microhardness_HV[i] = float(np.clip(70 + 0.03 * peak_temp_C[i] + 0.2 * cooling_rate_C_per_s[i] ** 0.5, 60, 300))

        # intermetallic growth depends on temperature and time
        imc_thickness_um[i] = float(np.clip(0.01 * (interface_temp_C[i] ** 0.9) * (time_s ** 0.4) / 100.0, 0.01, 10.0))

    return pd.DataFrame({
        "energy_input_J": energy_J,
        "linear_energy_density_J_per_mm": linear_energy_density_J_per_mm,
        "peak_temperature_C": peak_temp_C,
        "interface_temperature_C": interface_temp_C,
        "HAZ_width_mm": haz_width_mm,
        "cooling_rate_C_per_s": cooling_rate_C_per_s,
        "nugget_diameter_mm": nugget_diameter_mm,
        "bond_area_mm2": bond_area_mm2,
        "contact_resistance_mOhm": contact_res_mOhm,
        "porosity_fraction": porosity_fraction,
        "void_count": void_count,
        "immediate_lap_shear_strength_N": immediate_lap_shear_N,
        "microhardness_HV": microhardness_HV,
        "IMC_thickness_um": imc_thickness_um,
    })
