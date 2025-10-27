from __future__ import annotations
import numpy as np
import pandas as pd


def compute_performance_targets(inputs: pd.DataFrame, forwards: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    n = len(inputs)
    cycles_to_failure = np.zeros(n)
    resistance_drift_mOhm_1000 = np.zeros(n)
    peel_strength_retained_pct = np.zeros(n)
    crack_growth_rate_mm_per_cycle = np.zeros(n)
    pass_1000_cycles = np.zeros(n, dtype=bool)
    failure_mode = np.empty(n, dtype=object)

    for i in range(n):
        tech = inputs.loc[i, "technique"]
        anode = inputs.loc[i, "anode_material"]
        cathode = inputs.loc[i, "cathode_material"]
        pressure = inputs.loc[i, "pressure_MPa"]
        preheat = inputs.loc[i, "preheat_temperature_C"]

        bond_area = forwards.loc[i, "bond_area_mm2"]
        porosity = forwards.loc[i, "porosity_fraction"]
        contact_R = forwards.loc[i, "contact_resistance_mOhm"]
        imc = forwards.loc[i, "IMC_thickness_um"]
        lap_N = forwards.loc[i, "immediate_lap_shear_strength_N"]

        mismatch_penalty = 1.0
        if ("Aluminum" in anode and "Copper" in cathode) or ("Copper" in anode and "Aluminum" in cathode):
            mismatch_penalty = 0.85
        elif ("Stainless" in anode) != ("Stainless" in cathode):
            mismatch_penalty = 0.9

        strength_term = np.log1p(bond_area) * (lap_N ** 0.3)
        porosity_term = (1.0 - 1.2 * porosity)
        imc_term = np.exp(-0.03 * (imc - 2.0) ** 2)
        pressure_term = 1.0 + 0.002 * pressure
        preheat_term = 1.0 + 0.002 * (preheat - 20)

        base_cycles = 200.0 * strength_term * porosity_term * imc_term * pressure_term * preheat_term * mismatch_penalty
        noise = rng.normal(0, 60)
        cycles = float(np.clip(base_cycles + noise, 20, 10000))
        cycles_to_failure[i] = cycles

        pass_1000_cycles[i] = cycles >= 1000

        drift = 0.4 * porosity * (1.0 + np.tanh(contact_R / 5)) + 0.1 * np.maximum(imc - 2.0, 0) + rng.normal(0, 0.1)
        resistance_drift_mOhm_1000[i] = float(np.clip(drift, 0.0, 10.0))

        retention = 100.0 * np.clip(0.95 * (1.0 - 0.5 * porosity) * (0.7 + 0.3 * np.tanh(cycles / 1500)), 0.0, 1.0)
        peel_strength_retained_pct[i] = float(np.clip(retention, 10.0, 100.0))

        crack_growth = 1e-4 * (1.0 + 2.0 * porosity) * (1.0 + 0.5 * (imc / 5.0)) * (1.0 + 0.2 * (contact_R / 5.0))
        crack_growth_rate_mm_per_cycle[i] = float(np.clip(crack_growth, 1e-5, 5e-3))

        if porosity > 0.25 and cycles < 1000:
            failure_mode[i] = "porosity_initiated"
        elif imc > 4.0 and cycles < 1500:
            failure_mode[i] = "IMC_brittle_fracture"
        elif contact_R > 8.0:
            failure_mode[i] = "electrical_heating"
        else:
            failure_mode[i] = "fatigue_interface"

    return pd.DataFrame({
        "cycles_to_failure_thermal": cycles_to_failure,
        "resistance_drift_mOhm_after_1000_cycles": resistance_drift_mOhm_1000,
        "peel_strength_retained_pct": peel_strength_retained_pct,
        "crack_growth_rate_mm_per_cycle": crack_growth_rate_mm_per_cycle,
        "pass_1000_cycles": pass_1000_cycles,
        "failure_mode": failure_mode,
    })
