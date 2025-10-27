#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Material:
    name: str
    cte_ppm_per_C: float  # Coefficient of thermal expansion (ppm/°C)
    resistivity_ohm_m: float
    hardness_HV: float
    melting_C: float


MATERIALS: Dict[str, Material] = {
    "Cu": Material("Cu", cte_ppm_per_C=16.5, resistivity_ohm_m=1.68e-8, hardness_HV=50, melting_C=1085),
    "Al": Material("Al", cte_ppm_per_C=23.0, resistivity_ohm_m=2.82e-8, hardness_HV=30, melting_C=660),
    "Ni": Material("Ni", cte_ppm_per_C=13.4, resistivity_ohm_m=6.99e-8, hardness_HV=110, melting_C=1455),
    "SS304": Material("SS304", cte_ppm_per_C=17.3, resistivity_ohm_m=7.20e-7, hardness_HV=200, melting_C=1400),
    "CuSn": Material("CuSn", cte_ppm_per_C=17.0, resistivity_ohm_m=8.0e-8, hardness_HV=80, melting_C=1000),
}

COATINGS = {
    # coating: (contact_resistance_factor (lower better), bondability_factor (higher better))
    "bare": (1.00, 1.00),
    "Ni_plated": (0.75, 1.15),
    "Sn_plated": (0.70, 1.10),
    "oxide_heavy": (1.40, 0.75),
    "graphite_coated": (0.90, 1.05),
}

TECHNIQUES = ["USW", "Laser", "RSW"]  # Ultrasonic, Laser, Resistance Spot


def logistic(x: np.ndarray, k: float = 4.0) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-k * (x - 1.0)))


def clamp(values: np.ndarray, low: float, high: float) -> np.ndarray:
    return np.clip(values, low, high)


@dataclass
class GeneratorConfig:
    n_samples: int
    seed: int
    train_ratio: float
    val_ratio: float


class WeldingDatasetGenerator:
    def __init__(self, config: GeneratorConfig) -> None:
        self.config = config
        self.rng = np.random.default_rng(config.seed)

    # --------------- Sampling helpers ---------------
    def _sample_materials(self, n: int) -> Tuple[np.ndarray, np.ndarray]:
        material_names = np.array(list(MATERIALS.keys()))
        probs = np.array([0.38, 0.30, 0.10, 0.15, 0.07])  # skew to Cu/Al
        anode_idx = self.rng.choice(len(material_names), size=n, p=probs)
        cathode_idx = self.rng.choice(len(material_names), size=n, p=probs)
        return material_names[anode_idx], material_names[cathode_idx]

    def _sample_coatings(self, n: int) -> np.ndarray:
        coating_names = np.array(list(COATINGS.keys()))
        probs = np.array([0.45, 0.20, 0.15, 0.10, 0.10])
        return coating_names[self.rng.choice(len(coating_names), size=n, p=probs)]

    def _sample_techniques(self, n: int) -> np.ndarray:
        probs = np.array([0.5, 0.3, 0.2])  # more USW
        return np.array(TECHNIQUES)[self.rng.choice(3, size=n, p=probs)]

    def _sample_inputs(self, n: int) -> Dict[str, np.ndarray]:
        techniques = self._sample_techniques(n)
        anode, cathode = self._sample_materials(n)
        coatings = self._sample_coatings(n)

        thickness_um = self.rng.uniform(50.0, 300.0, size=n)
        preheat_C = self.rng.uniform(20.0, 120.0, size=n)

        # Common inputs
        clamp_force_N = self.rng.uniform(100.0, 1200.0, size=n)
        clamp_pressure_MPa = self.rng.uniform(1.0, 18.0, size=n)
        weld_time_s = self.rng.uniform(0.05, 1.2, size=n)

        # Initialize technique-specific arrays
        power_W = np.zeros(n)
        amplitude_um = np.zeros(n)
        pulse_energy_J = np.zeros(n)
        pulse_frequency_Hz = np.zeros(n)
        weld_speed_mm_per_s = np.zeros(n)

        # USW parameters
        mask_usw = techniques == "USW"
        power_W[mask_usw] = self.rng.uniform(300.0, 3500.0, size=mask_usw.sum())
        amplitude_um[mask_usw] = self.rng.uniform(10.0, 60.0, size=mask_usw.sum())
        # Laser parameters
        mask_laser = techniques == "Laser"
        pulse_energy_J[mask_laser] = self.rng.uniform(0.2, 5.0, size=mask_laser.sum())
        pulse_frequency_Hz[mask_laser] = self.rng.uniform(50.0, 600.0, size=mask_laser.sum())
        weld_speed_mm_per_s[mask_laser] = self.rng.uniform(5.0, 200.0, size=mask_laser.sum())
        power_W[mask_laser] = pulse_energy_J[mask_laser] * pulse_frequency_Hz[mask_laser]
        # RSW parameters
        mask_rsw = techniques == "RSW"
        power_W[mask_rsw] = self.rng.uniform(1500.0, 20000.0, size=mask_rsw.sum())
        # time shorter typical for RSW, already covered by weld_time_s

        return {
            "welding_technique": techniques,
            "anode_material": anode,
            "cathode_material": cathode,
            "tab_thickness_um": thickness_um,
            "surface_coating": coatings,
            "power_W": power_W,
            "amplitude_um": amplitude_um,
            "clamp_force_N": clamp_force_N,
            "clamp_pressure_MPa": clamp_pressure_MPa,
            "weld_time_s": weld_time_s,
            "weld_speed_mm_per_s": weld_speed_mm_per_s,
            "pulse_energy_J": pulse_energy_J,
            "pulse_frequency_Hz": pulse_frequency_Hz,
            "preheat_C": preheat_C,
        }

    # --------------- Physics-inspired mappings ---------------
    def _pair_properties(self, anode: np.ndarray, cathode: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        cte_a = np.array([MATERIALS[a].cte_ppm_per_C for a in anode])
        cte_c = np.array([MATERIALS[c].cte_ppm_per_C for c in cathode])
        cte_mismatch = np.abs(cte_a - cte_c)

        hv_a = np.array([MATERIALS[a].hardness_HV for a in anode])
        hv_c = np.array([MATERIALS[c].hardness_HV for c in cathode])
        hv_avg = 0.5 * (hv_a + hv_c)

        melting_a = np.array([MATERIALS[a].melting_C for a in anode])
        melting_c = np.array([MATERIALS[c].melting_C for c in cathode])
        melting_gap = np.abs(melting_a - melting_c)

        return cte_mismatch, hv_avg, melting_gap

    def _effective_energy_index(self, inputs: Dict[str, np.ndarray]) -> np.ndarray:
        tech = inputs["welding_technique"]
        power_W = inputs["power_W"]
        amplitude_um = inputs["amplitude_um"]
        force_N = inputs["clamp_force_N"]
        time_s = inputs["weld_time_s"]
        pulse_energy_J = inputs["pulse_energy_J"]
        pulse_frequency_Hz = inputs["pulse_frequency_Hz"]
        speed_mm_s = inputs["weld_speed_mm_per_s"]

        idx = np.zeros_like(power_W)

        mask_usw = tech == "USW"
        # Frictional/plastic work term increases with amplitude*force and time
        idx[mask_usw] = (
            0.7 * power_W[mask_usw] * time_s[mask_usw]
            + 0.0006 * amplitude_um[mask_usw] * force_N[mask_usw] * time_s[mask_usw]
        ) / 1000.0

        mask_laser = tech == "Laser"
        line_energy = (
            pulse_energy_J[mask_laser] * pulse_frequency_Hz[mask_laser]
        ) / np.maximum(speed_mm_s[mask_laser], 1e-3)  # J/mm
        idx[mask_laser] = 0.9 * line_energy  # scale to comparable range

        mask_rsw = tech == "RSW"
        idx[mask_rsw] = 0.8 * power_W[mask_rsw] * time_s[mask_rsw] / 1000.0

        return idx

    def _optimal_energy_index(self, inputs: Dict[str, np.ndarray]) -> np.ndarray:
        thickness_um = inputs["tab_thickness_um"]
        preheat_C = inputs["preheat_C"]
        cte_mismatch, _, melting_gap = self._pair_properties(inputs["anode_material"], inputs["cathode_material"])

        # Dissimilarity factor increases energy demand
        dissimilarity = 1.0 + 0.003 * cte_mismatch + 0.0005 * melting_gap
        # Preheat reduces energy needed
        preheat_factor = 1.0 - 0.003 * np.maximum(preheat_C - 20.0, 0.0)
        preheat_factor = np.clip(preheat_factor, 0.7, 1.05)

        # Baseline energy need grows with thickness
        base_need = 0.25 * (thickness_um / 100.0)
        e_opt = base_need * dissimilarity * preheat_factor
        return e_opt

    def _coating_factors(self, coating: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        cr_factor = np.array([COATINGS[c][0] for c in coating])
        bond_factor = np.array([COATINGS[c][1] for c in coating])
        return cr_factor, bond_factor

    def _compute_outputs(self, inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        n = inputs["power_W"].shape[0]
        tech = inputs["welding_technique"]
        rng = self.rng

        e_idx = self._effective_energy_index(inputs)
        e_opt = self._optimal_energy_index(inputs)
        e_ratio = e_idx / np.maximum(e_opt, 1e-6)

        cte_mismatch, hv_avg, _ = self._pair_properties(inputs["anode_material"], inputs["cathode_material"])
        cr_factor, bond_factor = self._coating_factors(inputs["surface_coating"])

        # Porosity - U-shaped curve around e_ratio = 1
        porosity_pct = 5.0 + 45.0 * (e_ratio - 1.0) ** 2 + rng.normal(0.0, 2.0, n)
        porosity_pct = clamp(porosity_pct, 0.0, 60.0)

        # Penetration depth - saturating with energy ratio and thickness
        thickness_um = inputs["tab_thickness_um"]
        penetration_depth_um = (
            0.15 * thickness_um * logistic(e_ratio, k=3.0)
            + rng.normal(0.0, 8.0, n)
        )
        penetration_depth_um = clamp(penetration_depth_um, 5.0, 2.2 * thickness_um)

        # Bond area and nugget diameter (tech-specific trends)
        bond_area_mm2 = (
            2.5
            + 0.006 * inputs["clamp_force_N"]
            + 0.03 * inputs["amplitude_um"]
        ) * logistic(e_ratio, k=3.5) * (0.9 + 0.2 * bond_factor)
        bond_area_mm2 += rng.normal(0.0, 2.5, n)
        bond_area_mm2 = clamp(bond_area_mm2, 1.0, 120.0)

        nugget_diameter_mm = (
            0.6 * np.sqrt(np.maximum(e_idx, 1e-6)) * (tech != "USW").astype(float)
            + 0.25 * np.sqrt(np.maximum(bond_area_mm2, 1e-6)) * (tech == "USW").astype(float)
        )
        nugget_diameter_mm += rng.normal(0.0, 0.25, n)
        nugget_diameter_mm = clamp(nugget_diameter_mm, 0.2, 8.0)

        # Max temperature and HAZ width
        max_temperature_C = 25.0 + 180.0 * np.log1p(0.8 * e_idx) + rng.normal(0.0, 10.0, n)
        max_temperature_C = clamp(max_temperature_C, 40.0, 1200.0)

        haz_width_um = 12.0 + 30.0 * logistic(e_ratio, k=2.5)
        haz_width_um *= 1.15 * (tech != "USW").astype(float) + 0.9 * (tech == "USW").astype(float)
        haz_width_um += rng.normal(0.0, 4.0, n)
        haz_width_um = clamp(haz_width_um, 5.0, 350.0)

        # Contact resistance (initial)
        contact_resistance_mOhm = (
            3.2 * cr_factor
            - 0.06 * inputs["clamp_pressure_MPa"]
            - 0.002 * inputs["amplitude_um"]
            - 0.004 * inputs["preheat_C"]
            + 0.02 * porosity_pct
            + rng.normal(0.0, 0.08, n)
        )
        contact_resistance_mOhm = clamp(contact_resistance_mOhm, 0.15, 10.0)

        # Microhardness near interface
        microhardness_HV = hv_avg * (0.9 + 0.18 * logistic(e_ratio, k=2.0))
        microhardness_HV *= 1.0 - 0.003 * porosity_pct
        microhardness_HV += rng.normal(0.0, 6.0, n)
        microhardness_HV = clamp(microhardness_HV, 20.0, 380.0)

        # Intermetallic compound (IMC) thickness - stronger for dissimilar pairs
        dissimilar = (inputs["anode_material"] != inputs["cathode_material"]).astype(float)
        imc_thickness_um = (
            dissimilar
            * (0.02 * inputs["preheat_C"] + 0.03 * e_idx)
            * (1.0 + 0.015 * cte_mismatch)
            + rng.normal(0.0, 0.8, n)
        )
        imc_thickness_um = clamp(imc_thickness_um, 0.0, 60.0)

        # Strength metrics
        area_term = 0.8 * bond_area_mm2 + 2.2 * (nugget_diameter_mm ** 2)
        penetration_term = 0.9 * np.sqrt(np.maximum(penetration_depth_um, 1.0))
        porosity_penalty = (1.0 + 0.02 * porosity_pct)
        imc_penalty = 1.0 + 0.015 * imc_thickness_um

        tensile_shear_strength_N = (
            6.0 * area_term * penetration_term / (porosity_penalty * imc_penalty)
            + rng.normal(0.0, 30.0, n)
        )
        tensile_shear_strength_N = clamp(tensile_shear_strength_N, 50.0, 12000.0)

        peel_strength_N = (
            0.7 * tensile_shear_strength_N * (1.05 - 0.002 * porosity_pct)
            + rng.normal(0.0, 18.0, n)
        )
        peel_strength_N = clamp(peel_strength_N, 30.0, 10000.0)

        # Defect class based on energy ratio
        defect_class = np.full(n, "nominal", dtype=object)
        defect_class[e_ratio < 0.85] = "underweld"
        defect_class[e_ratio > 1.35] = "overweld"

        # Long-term performance under thermal cycling
        # Resistance growth rate (mOhm / 100 cycles)
        resistance_growth_rate_mOhm_per_100 = (
            0.03 + 0.06 * dissimilar + 0.002 * porosity_pct + 0.004 * imc_thickness_um
            + 0.001 * cte_mismatch + rng.normal(0.0, 0.01, n)
        )
        resistance_growth_rate_mOhm_per_100 = clamp(resistance_growth_rate_mOhm_per_100, 0.005, 1.5)

        # Cycles to failure: grows with initial strength, harmed by porosity/IMC/CTE mismatch and overheating
        overheat_penalty = np.maximum(e_ratio - 1.2, 0.0)
        cycles_to_failure = (
            120.0
            + 0.65 * tensile_shear_strength_N
            - 6.0 * porosity_pct
            - 8.0 * imc_thickness_um
            - 10.0 * cte_mismatch
            - 180.0 * overheat_penalty
            + rng.normal(0.0, 60.0, n)
        )
        cycles_to_failure = clamp(cycles_to_failure, 50.0, 10000.0)

        retained_strength_pct_after_1000 = (
            100.0
            - 0.6 * resistance_growth_rate_mOhm_per_100
            - 0.04 * porosity_pct
            - 0.09 * imc_thickness_um
            - 0.10 * cte_mismatch
            - 8.0 * overheat_penalty
            + rng.normal(0.0, 1.5, n)
        )
        retained_strength_pct_after_1000 = clamp(retained_strength_pct_after_1000, 20.0, 100.0)

        delamination_probability = (
            0.01 + 0.0018 * porosity_pct + 0.006 * overheat_penalty + 0.004 * imc_thickness_um / 10.0
            + 0.003 * cte_mismatch / 10.0
        )
        delamination_probability = clamp(delamination_probability, 0.0, 1.0)

        pass_1000_cycle = (cycles_to_failure >= 1000.0).astype(int)

        return {
            # Characterization & quality metrics (forward outputs)
            "bond_area_mm2": bond_area_mm2,
            "nugget_diameter_mm": nugget_diameter_mm,
            "penetration_depth_um": penetration_depth_um,
            "porosity_pct": porosity_pct,
            "max_temperature_C": max_temperature_C,
            "haz_width_um": haz_width_um,
            "contact_resistance_mOhm": contact_resistance_mOhm,
            "microhardness_HV": microhardness_HV,
            "tensile_shear_strength_N": tensile_shear_strength_N,
            "peel_strength_N": peel_strength_N,
            "imc_thickness_um": imc_thickness_um,
            "defect_class": defect_class,
            # Performance & validation metrics (targets)
            "cycles_to_failure": cycles_to_failure.astype(int),
            "retained_strength_pct_after_1000": retained_strength_pct_after_1000,
            "resistance_growth_mOhm_per_100cycles": resistance_growth_rate_mOhm_per_100,
            "delamination_probability": delamination_probability,
            "pass_1000_cycle": pass_1000_cycle,
        }

    def generate(self) -> pd.DataFrame:
        n = self.config.n_samples
        inputs = self._sample_inputs(n)
        outputs = self._compute_outputs(inputs)
        df = pd.DataFrame({**inputs, **outputs})

        # Cast appropriate dtypes
        categorical_cols = ["welding_technique", "anode_material", "cathode_material", "surface_coating", "defect_class"]
        for c in categorical_cols:
            df[c] = df[c].astype("category")
        return df


def build_schema(df: pd.DataFrame) -> Dict[str, Dict[str, str]]:
    # Human-readable schema with units and descriptions
    schema: Dict[str, Dict[str, str]] = {}

    def add(name: str, unit: str, desc: str) -> None:
        schema[name] = {"unit": unit, "description": desc}

    # Inputs
    add("welding_technique", "-", "Welding technique: USW (ultrasonic), Laser, RSW (resistance spot)")
    add("anode_material", "-", "Anode/base material")
    add("cathode_material", "-", "Cathode/base material")
    add("tab_thickness_um", "µm", "Tab thickness")
    add("surface_coating", "-", "Surface condition/coating of joining surfaces")
    add("power_W", "W", "Process power; for Laser equals pulse_energy_J * pulse_frequency_Hz")
    add("amplitude_um", "µm", "USW vibration amplitude (USW only)")
    add("clamp_force_N", "N", "Clamping force")
    add("clamp_pressure_MPa", "MPa", "Clamping pressure")
    add("weld_time_s", "s", "Weld duration")
    add("weld_speed_mm_per_s", "mm/s", "Travel speed (Laser only)")
    add("pulse_energy_J", "J", "Laser pulse energy (Laser only)")
    add("pulse_frequency_Hz", "Hz", "Laser pulse frequency (Laser only)")
    add("preheat_C", "°C", "Preheat temperature")

    # Forward outputs
    add("bond_area_mm2", "mm^2", "Bonded area estimate at interface")
    add("nugget_diameter_mm", "mm", "Equivalent nugget diameter")
    add("penetration_depth_um", "µm", "Weld penetration depth")
    add("porosity_pct", "%", "Volumetric porosity near weld")
    add("max_temperature_C", "°C", "Max temperature during weld (estimate)")
    add("haz_width_um", "µm", "Heat-affected zone width")
    add("contact_resistance_mOhm", "mΩ", "Initial contact resistance after weld")
    add("microhardness_HV", "HV", "Microhardness near interface")
    add("tensile_shear_strength_N", "N", "Initial tensile-shear strength")
    add("peel_strength_N", "N", "Initial peel strength")
    add("imc_thickness_um", "µm", "Intermetallic layer thickness (dissimilar joints)")
    add("defect_class", "-", "Underweld/overweld/nominal classification from energy ratio")

    # Performance targets
    add("cycles_to_failure", "cycles", "Cycles under thermal cycling to failure")
    add("retained_strength_pct_after_1000", "%", "Retained strength after 1000 cycles")
    add("resistance_growth_mOhm_per_100cycles", "mΩ/100cy", "Resistance growth rate under cycling")
    add("delamination_probability", "[0,1]", "Probability of delamination under cycling")
    add("pass_1000_cycle", "0/1", "Whether joint survives 1000 cycles")

    # Include dtypes
    types = {k: str(v) for k, v in df.dtypes.to_dict().items()}
    return {"columns": schema, "dtypes": types}


def split_and_save(df: pd.DataFrame, out_dir: str, train_ratio: float, val_ratio: float) -> None:
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    n = len(df)
    n_train = int(train_ratio * n)
    n_val = int(val_ratio * n)
    train_df = df.iloc[:n_train]
    val_df = df.iloc[n_train:n_train + n_val]
    test_df = df.iloc[n_train + n_val:]

    train_df.to_csv(f"{out_dir}/train.csv", index=False)
    val_df.to_csv(f"{out_dir}/val.csv", index=False)
    test_df.to_csv(f"{out_dir}/test.csv", index=False)

    schema = build_schema(df)
    with open(f"{out_dir}/schema.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate synthetic dataset for ML-driven inverse design of welding parameters")
    p.add_argument("--output-dir", type=str, required=True, help="Directory to write train/val/test and schema.json")
    p.add_argument("--n-samples", type=int, default=50000, help="Total number of rows to generate")
    p.add_argument("--seed", type=int, default=7, help="Random seed")
    p.add_argument("--train-ratio", type=float, default=0.8, help="Train split ratio")
    p.add_argument("--val-ratio", type=float, default=0.1, help="Validation split ratio")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = GeneratorConfig(n_samples=args.n_samples, seed=args.seed, train_ratio=args.train_ratio, val_ratio=args.val_ratio)
    gen = WeldingDatasetGenerator(cfg)
    df = gen.generate()
    split_and_save(df, args.output_dir, args.train_ratio, args.val_ratio)


if __name__ == "__main__":
    main()
