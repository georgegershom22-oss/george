from __future__ import annotations
import random
import math
from typing import List, Dict, Any
import numpy as np
import pandas as pd
from pydantic import ValidationError

from .schema import (
    DatasetRow,
    InputParameters,
    ForwardMetrics,
    PerformanceMetrics,
    DatasetMetadata,
)
from .physics import (
    MaterialPair,
    compute_heat_input_j,
    estimate_energy_density_j_mm2,
    estimate_nugget_and_area,
    estimate_max_temp_c,
    estimate_interface_resistance_milliohm,
    estimate_porosity_percent,
    estimate_misalignment_um,
    estimate_mechanical_strengths,
    estimate_validation_performance,
)

MATERIALS = ["Cu", "Al", "Ni", "SS304", "SS316", "CuNi"]
SURFACE_FINISHES = ["bare", "nickel_plated", "tin_plated", "silver_plated", "anodized", "oxidized"]
TECHNIQUES = ["ultrasonic", "laser", "resistance_spot"]


def sample_inputs(n: int, seed: int = 42) -> List[InputParameters]:
    rng = random.Random(seed)
    inputs: List[InputParameters] = []
    for _ in range(n):
        technique = rng.choice(TECHNIQUES)
        anode = rng.choice(MATERIALS)
        cathode = rng.choice([m for m in MATERIALS if m != anode or rng.random() < 0.3])
        thickness_um = rng.uniform(50, 1000)
        surface = rng.choice(SURFACE_FINISHES)

        if technique == "ultrasonic":
            power = rng.uniform(200.0, 4000.0)  # W
            amplitude_um = rng.uniform(5.0, 50.0)
            force_n = rng.uniform(30.0, 800.0)
            pressure_mpa = rng.uniform(0.1, 5.0)
            time_ms_or_s = rng.uniform(50.0, 1500.0)  # ms
            speed_mm_s = None
            pulse_freq_hz = None
        elif technique == "laser":
            power = rng.uniform(2.0, 80.0)  # treat as pulse energy J
            amplitude_um = None
            force_n = None
            pressure_mpa = None
            time_ms_or_s = rng.uniform(0.002, 0.05)  # s
            speed_mm_s = rng.uniform(1.0, 200.0)
            pulse_freq_hz = rng.uniform(10.0, 1000.0)
        else:  # resistance_spot
            power = rng.uniform(1000.0, 10000.0)  # W
            amplitude_um = None
            force_n = rng.uniform(100.0, 3000.0)
            pressure_mpa = rng.uniform(0.5, 15.0)
            time_ms_or_s = rng.uniform(50.0, 500.0)  # ms
            speed_mm_s = None
            pulse_freq_hz = None

        preheat_c = rng.uniform(15.0, 120.0)

        ip = InputParameters(
            anode_material=anode,
            cathode_material=cathode,
            tab_thickness_um=thickness_um,
            surface_finish=surface,
            technique=technique,
            power_w_or_energy_j=power,
            amplitude_um=amplitude_um,
            force_n=force_n,
            pressure_mpa=pressure_mpa,
            time_ms_or_s=time_ms_or_s,
            speed_mm_s=speed_mm_s,
            pulse_frequency_hz=pulse_freq_hz,
            preheat_temp_c=preheat_c,
        )
        inputs.append(ip)
    return inputs


def forward_simulate(ip: InputParameters, beam_diameter_mm: float = 0.6) -> ForwardMetrics:
    mat = MaterialPair(ip.anode_material, ip.cathode_material)

    heat_j = compute_heat_input_j(ip.technique, ip.power_w_or_energy_j, ip.time_ms_or_s)
    energy_density = estimate_energy_density_j_mm2(heat_j, beam_diameter_mm)
    nugget_d_mm, area_mm2 = estimate_nugget_and_area(
        ip.technique, ip.force_n, ip.amplitude_um, ip.speed_mm_s, energy_density, mat, ip.tab_thickness_um
    )
    max_temp_c = estimate_max_temp_c(heat_j, mat, ip.tab_thickness_um, ip.preheat_temp_c)
    inter_res_mohm = estimate_interface_resistance_milliohm(ip.surface_finish, ip.pressure_mpa)
    porosity_pct = estimate_porosity_percent(ip.technique, energy_density, max_temp_c)
    misalign_um = estimate_misalignment_um(ip.force_n, ip.amplitude_um, ip.speed_mm_s)
    tensile_mpa, peel_n_mm = estimate_mechanical_strengths(area_mm2, mat, porosity_pct)

    return ForwardMetrics(
        nugget_diameter_mm=nugget_d_mm,
        weld_area_mm2=area_mm2,
        max_interface_temp_c=max_temp_c,
        heat_input_j=heat_j,
        energy_density_j_mm2=energy_density,
        interfacial_resistance_milliohm=inter_res_mohm,
        porosity_percent=porosity_pct,
        misalignment_um=misalign_um,
        tensile_shear_strength_mpa=tensile_mpa,
        peel_strength_n_mm=peel_n_mm,
    )


def performance_simulate(ip: InputParameters, fwd: ForwardMetrics) -> PerformanceMetrics:
    mat = MaterialPair(ip.anode_material, ip.cathode_material)
    cycles, res_growth, crack_len, delam = estimate_validation_performance(fwd.model_dump(), mat, ip.preheat_temp_c)
    return PerformanceMetrics(
        cycles_to_failure_thermal=cycles,
        resistance_growth_percent=res_growth,
        crack_length_mm=crack_len,
        delamination_area_percent=delam,
    )


def rows_to_dataframe(rows: List[DatasetRow]) -> pd.DataFrame:
    records: List[Dict[str, Any]] = []
    for row in rows:
        r = {
            "id": row.id,
            # inputs
            "anode_material": row.inputs.anode_material,
            "cathode_material": row.inputs.cathode_material,
            "tab_thickness_um": row.inputs.tab_thickness_um,
            "surface_finish": row.inputs.surface_finish,
            "technique": row.inputs.technique,
            "power_w_or_energy_j": row.inputs.power_w_or_energy_j,
            "amplitude_um": row.inputs.amplitude_um,
            "force_n": row.inputs.force_n,
            "pressure_mpa": row.inputs.pressure_mpa,
            "time_ms_or_s": row.inputs.time_ms_or_s,
            "speed_mm_s": row.inputs.speed_mm_s,
            "pulse_frequency_hz": row.inputs.pulse_frequency_hz,
            "preheat_temp_c": row.inputs.preheat_temp_c,
            # forward
            "nugget_diameter_mm": row.forward.nugget_diameter_mm,
            "weld_area_mm2": row.forward.weld_area_mm2,
            "max_interface_temp_c": row.forward.max_interface_temp_c,
            "heat_input_j": row.forward.heat_input_j,
            "energy_density_j_mm2": row.forward.energy_density_j_mm2,
            "interfacial_resistance_milliohm": row.forward.interfacial_resistance_milliohm,
            "porosity_percent": row.forward.porosity_percent,
            "misalignment_um": row.forward.misalignment_um,
            "tensile_shear_strength_mpa": row.forward.tensile_shear_strength_mpa,
            "peel_strength_n_mm": row.forward.peel_strength_n_mm,
            # performance
            "cycles_to_failure_thermal": row.performance.cycles_to_failure_thermal,
            "resistance_growth_percent": row.performance.resistance_growth_percent,
            "crack_length_mm": row.performance.crack_length_mm,
            "delamination_area_percent": row.performance.delamination_area_percent,
        }
        records.append(r)
    df = pd.DataFrame.from_records(records)
    return df


def generate_dataset(n_rows: int, seed: int = 42) -> tuple[pd.DataFrame, DatasetMetadata]:
    ips = sample_inputs(n_rows, seed=seed)
    rows: List[DatasetRow] = []
    for i, ip in enumerate(ips):
        fwd = forward_simulate(ip)
        perf = performance_simulate(ip, fwd)
        row = DatasetRow(id=i, inputs=ip, forward=fwd, performance=perf)
        rows.append(row)

    df = rows_to_dataframe(rows)
    feature_names = [
        "anode_material","cathode_material","tab_thickness_um","surface_finish","technique","power_w_or_energy_j",
        "amplitude_um","force_n","pressure_mpa","time_ms_or_s","speed_mm_s","pulse_frequency_hz","preheat_temp_c"
    ]
    forward_targets = [
        "nugget_diameter_mm","weld_area_mm2","max_interface_temp_c","heat_input_j","energy_density_j_mm2",
        "interfacial_resistance_milliohm","porosity_percent","misalignment_um","tensile_shear_strength_mpa","peel_strength_n_mm"
    ]
    performance_targets = [
        "cycles_to_failure_thermal","resistance_growth_percent","crack_length_mm","delamination_area_percent"
    ]

    meta = DatasetMetadata(
        num_rows=len(df),
        feature_names=feature_names,
        forward_target_names=forward_targets,
        performance_target_names=performance_targets,
        notes=(
            "Synthetic dataset with physics-inspired heuristics for welding processes. "
            "Inputs span ultrasonic, laser, and resistance spot welding with materials Cu, Al, Ni, SS304, SS316, CuNi. "
            "Forward metrics represent immediate weld characteristics; performance metrics simulate outcomes after thermal cycling."
        ),
    )
    return df, meta
