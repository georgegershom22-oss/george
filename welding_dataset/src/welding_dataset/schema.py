from __future__ import annotations
from typing import Literal, Optional, List
from pydantic import BaseModel, Field


# -------------------------
# Schema for dataset rows
# -------------------------

WeldingTechnique = Literal[
    "ultrasonic",
    "laser",
    "resistance_spot",
]

SurfaceFinish = Literal[
    "bare",
    "nickel_plated",
    "tin_plated",
    "silver_plated",
    "anodized",
    "oxidized",
]

Material = Literal[
    "Cu",
    "Al",
    "Ni",
    "SS304",
    "SS316",
    "CuNi",
]

class InputParameters(BaseModel):
    # Base materials
    anode_material: Material = Field(description="Anode base material")
    cathode_material: Material = Field(description="Cathode base material")
    tab_thickness_um: float = Field(ge=10, le=5000, description="Tab thickness in micrometers")
    surface_finish: SurfaceFinish = Field(description="Surface finish/coating")

    # Welding process
    technique: WeldingTechnique = Field(description="Welding technique")
    power_w_or_energy_j: float = Field(ge=0.0, description="Peak power (USW) or pulse energy (Laser)")
    amplitude_um: Optional[float] = Field(default=None, ge=0.0, description="USW vibration amplitude")
    force_n: Optional[float] = Field(default=None, ge=0.0, description="Clamping force (N)")
    pressure_mpa: Optional[float] = Field(default=None, ge=0.0, description="Contact pressure (MPa)")
    time_ms_or_s: float = Field(ge=0.1, description="Weld duration in ms (USW/RSW) or s (Laser)")
    speed_mm_s: Optional[float] = Field(default=None, ge=0.0, description="Laser scan speed in mm/s")
    pulse_frequency_hz: Optional[float] = Field(default=None, ge=0.0, description="Laser pulse frequency in Hz")

    # Environmental
    preheat_temp_c: float = Field(ge=-20, le=200, description="Preheat temperature in Celsius")


class ForwardMetrics(BaseModel):
    # Immediate, post-join measures
    nugget_diameter_mm: float = Field(ge=0.0)
    weld_area_mm2: float = Field(ge=0.0)
    max_interface_temp_c: float
    heat_input_j: float = Field(ge=0.0)
    energy_density_j_mm2: float = Field(ge=0.0)

    interfacial_resistance_milliohm: float = Field(ge=0.0)
    porosity_percent: float = Field(ge=0.0, le=100.0)
    misalignment_um: float = Field(ge=0.0)

    tensile_shear_strength_mpa: float = Field(ge=0.0)
    peel_strength_n_mm: float = Field(ge=0.0)


class PerformanceMetrics(BaseModel):
    # After thermal cycling / validation
    cycles_to_failure_thermal: int = Field(ge=0)
    resistance_growth_percent: float = Field(ge=0.0)
    crack_length_mm: float = Field(ge=0.0)
    delamination_area_percent: float = Field(ge=0.0, le=100.0)


class DatasetRow(BaseModel):
    id: int
    inputs: InputParameters
    forward: ForwardMetrics
    performance: PerformanceMetrics


class DatasetMetadata(BaseModel):
    version: str = "0.1.0"
    num_rows: int
    feature_names: List[str]
    forward_target_names: List[str]
    performance_target_names: List[str]
    notes: str
    license: str = "CC BY 4.0"
    citation: str = (
        "If you use this dataset, please cite: 'Synthetic Welding Parameters Dataset for ML-Driven Inverse Design, v0.1.0'."
    )
