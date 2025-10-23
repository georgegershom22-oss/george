from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

import random
import math


@dataclass
class SOFCInputs:
    operating_temperature_c: float  # 700-900 C
    fuel_utilization: float         # 0.6-0.9
    current_density_a_per_cm2: float  # 0.1-1.5 A/cm^2
    anode_porosity: float           # 0.2-0.5


@dataclass
class SOFCOutputs:
    voltage_curve_a_per_cm2: List[float]
    voltage_curve_v: List[float]
    t_stack_c: float
    eta_elec: float


class SOFCSurrogate1D:
    """
    A simplified 1D lumped SOFC stack surrogate.

    The model captures key trends:
    - Nernst open-circuit voltage decreases slightly with higher temperature and utilization.
    - Activation and ohmic losses increase with current density and decrease with temperature.
    - Concentration losses worsen with higher utilization and lower porosity.

    This is NOT a high-fidelity solver; it is a parametric, smooth surrogate to emulate
    low-fidelity data generation for ML workflows.
    """

    def __init__(self, vi_points: int = 50, seed: int | None = 42) -> None:
        self.vi_points = vi_points
        self.random = random.Random(seed)

    @staticmethod
    def _linspace(start: float, stop: float, num: int) -> List[float]:
        if num <= 1:
            return [float(stop)]
        step = (stop - start) / (num - 1)
        return [start + i * step for i in range(num)]

    @staticmethod
    def _clip(value: float, low: float, high: float) -> float:
        return low if value < low else high if value > high else value

    def _nernst_ocv(self, t_k: float, fu: float) -> float:
        # Base OCV at reference conditions
        e0 = 1.1  # V at ~800C for H2/H2O
        # Temperature effect (mild negative slope around reference 800C ~ 1073K)
        ref_t = 1073.15
        temp_coeff = -1.0e-4  # V/K
        # Fuel utilization reduces effective partial pressures -> lower OCV
        fu_coeff = -0.08  # V per unit utilization (0-1)
        return e0 + temp_coeff * (t_k - ref_t) + fu_coeff * (fu - 0.75)

    def _activation_loss(self, j: List[float], t_k: float) -> List[float]:
        # Butler-Volmer-like trend: ~ a * ln(j + j0)
        a_ref = 0.08  # V scaling
        j0 = 0.02  # exchange-like offset A/cm^2
        # Lower losses at higher T
        t_ref = 1073.15
        t_factor = max(0.5, 1.2 - 0.0004 * (t_k - t_ref))
        return [a_ref * t_factor * math.log1p(val / j0) for val in j]

    def _ohmic_loss(self, j: List[float], t_k: float, porosity: float) -> List[float]:
        # Effective area-specific resistance decreasing with T and increasing with lower porosity
        asr_ref = 0.4  # ohm*cm^2 at ref T and porosity
        t_ref = 1073.15
        # T dependence
        asr_t = asr_ref * (1.0 - 0.0008 * (t_k - t_ref))
        # Porosity effect: lower porosity -> higher ASR
        asr = asr_t * (1.15 - 0.6 * porosity)
        return [asr * val for val in j]

    def _concentration_loss(self, j: List[float], fu: float, porosity: float) -> List[float]:
        # Increase sharply near limiting current; worsen with higher fu and lower porosity
        j_lim = max(1e-3, 2.0 * porosity * (1.05 - fu))  # A/cm^2
        b = 0.08  # V scaling
        losses: List[float] = []
        for val in j:
            ratio = max(0.0, min(0.99, val / j_lim))
            losses.append(-b * math.log(1.0 - ratio))
        return losses

    def simulate(self, inputs: SOFCInputs) -> SOFCOutputs:
        t_k = inputs.operating_temperature_c + 273.15
        fu = inputs.fuel_utilization
        por = inputs.anode_porosity

        # Generate VI sweep from small to chosen peak current
        j_max = max(0.2, min(1.5, inputs.current_density_a_per_cm2))
        j = self._linspace(0.01, j_max, self.vi_points)

        ocv = self._nernst_ocv(t_k, fu)
        eta_act = self._activation_loss(j, t_k)
        eta_ohm = self._ohmic_loss(j, t_k, por)
        eta_conc = self._concentration_loss(j, fu, por)

        v: List[float] = []
        for a, b, c in zip(eta_act, eta_ohm, eta_conc):
            val = ocv - a - b - c
            v.append(self._clip(val, 0.05, 1.2))

        # Stack temperature rises with current density and ohmic heating, with noise
        # trapezoidal integration of j*v over j
        heat_gen = 0.0
        for i in range(1, len(j)):
            y_prev = j[i - 1] * v[i - 1]
            y_curr = j[i] * v[i]
            x_prev = j[i - 1]
            x_curr = j[i]
            heat_gen += 0.5 * (y_prev + y_curr) * (x_curr - x_prev)
        t_rise = 20.0 * heat_gen  # C, arbitrary scaling for surrogate
        noise = self.random.gauss(0.0, 2.0)
        t_stack_c = float(self._clip(inputs.operating_temperature_c + t_rise + noise, 600.0, 1000.0))

        # Electrochemical efficiency surrogate: favors moderate fu and mid-current
        avg_j = float(sum(j) / len(j))
        eff_base = 0.6 + 0.15 * (1.0 - abs(fu - 0.75) / 0.25)
        eff_penalty = 0.12 * (avg_j / 1.0)  # higher j penalizes efficiency
        eta_elec = float(self._clip(eff_base - eff_penalty, 0.2, 0.85))

        return SOFCOutputs(
            voltage_curve_a_per_cm2=j,
            voltage_curve_v=v,
            t_stack_c=t_stack_c,
            eta_elec=eta_elec,
        )


def sample_inputs(rng: random.Random) -> SOFCInputs:
    t_c = rng.uniform(700.0, 900.0)
    fu = rng.uniform(0.6, 0.9)
    j = rng.uniform(0.1, 1.5)
    por = rng.uniform(0.2, 0.5)
    return SOFCInputs(t_c, fu, j, por)
