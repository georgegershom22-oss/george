from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple

R_UNIVERSAL = 8.314462618  # J/mol/K
FARADAY = 96485.33212  # C/mol


@dataclass
class OperatingPoint:
    temperature_K: float  # stack operating temperature [K]
    current_density_A_per_m2: float  # current density [A/m^2]
    fuel_utilization: float  # fraction 0..1
    anode_porosity: float  # fraction 0..1


@dataclass
class ModelParams:
    # Thermodynamics
    h2_partial_pressure_bar: float = 0.4
    h2o_partial_pressure_bar: float = 0.1
    o2_partial_pressure_bar: float = 0.21

    # Geometry and transport
    exchange_current_density_A_per_m2: float = 1e3
    membrane_resistance_ohm_m2: float = 0.08
    concentration_overpotential_coeff_V: float = 0.02

    # Empirical temperature scaling
    activation_energy_J_per_mol: float = 80e3
    ref_temperature_K: float = 1073.15  # 800 C


class SOFCLumped1D:
    """
    Low-fidelity 1D lumped SOFC stack model.

    This is a simplified, fast surrogate capturing main trends for dataset generation:
    - Nernst open-circuit voltage from partial pressures and temperature
    - Activation overpotential using Arrhenius-scaled exchange current density
    - Ohmic overpotential via area-specific resistance
    - Concentration (mass transport) overpotential via a simple log form

    Not for design; intended for generating synthetic multi-fidelity training data.
    """

    def __init__(self, params: ModelParams | None = None) -> None:
        self.params = params or ModelParams()

    def nernst_voltage(self, T: float) -> float:
        p = self.params
        # H2 + 1/2 O2 -> H2O
        # E = E0 + (R*T/(2F)) * ln( p_H2 * sqrt(p_O2) / p_H2O )
        E0 = 1.18  # effective reference OCV at ref conditions [V]
        term = (p.h2_partial_pressure_bar * math.sqrt(p.o2_partial_pressure_bar)) / max(
            p.h2o_partial_pressure_bar, 1e-6
        )
        return E0 + (R_UNIVERSAL * T / (2.0 * FARADAY)) * math.log(term)

    def arrhenius_i0(self, T: float) -> float:
        p = self.params
        # Arrhenius scaling of exchange current
        return p.exchange_current_density_A_per_m2 * math.exp(
            -p.activation_energy_J_per_mol / R_UNIVERSAL * (1.0 / T - 1.0 / p.ref_temperature_K)
        )

    def activation_overpotential(self, j: float, T: float) -> float:
        # Butler-Volmer high-field approximation (Tafel region)
        i0 = max(self.arrhenius_i0(T), 1e-12)
        if j <= 0:
            return 0.0
        return (R_UNIVERSAL * T / (2.0 * FARADAY)) * math.log(j / i0 + 1e-12)

    def ohmic_overpotential(self, j: float) -> float:
        return self.params.membrane_resistance_ohm_m2 * j

    def concentration_overpotential(self, j: float, fu: float, epsilon: float) -> float:
        # Simple limiting-current-like effect scaled by fuel utilization and porosity
        i_lim = 15000.0 * epsilon * (1.0 - fu + 1e-3)  # A/m^2
        i_lim = max(i_lim, 1e-6)
        if j >= 0.95 * i_lim:
            j = 0.95 * i_lim
        return self.params.concentration_overpotential_coeff_V * math.log(1.0 / (1.0 - j / i_lim))

    def cell_voltage(self, op: OperatingPoint) -> float:
        T = op.temperature_K
        j = max(op.current_density_A_per_m2, 0.0)
        fu = min(max(op.fuel_utilization, 0.0), 0.99)
        eps = min(max(op.anode_porosity, 0.05), 0.9)

        E = self.nernst_voltage(T)
        eta_act = self.activation_overpotential(j, T)
        eta_ohm = self.ohmic_overpotential(j)
        eta_conc = self.concentration_overpotential(j, fu, eps)
        V = max(E - (eta_act + eta_ohm + eta_conc), 0.0)
        return V

    def stack_temperature(self, base_T: float, j: float, fu: float) -> float:
        # Simple heat rise model: more current and higher utilization increase T
        delta_T = 20.0 + 60.0 * fu
        delta_T *= (j / 10000.0)
        return base_T + delta_T

    def electrical_efficiency(self, V: float, T: float) -> float:
        # Surrogate electrical efficiency based on fraction of OCV achieved
        E = self.nernst_voltage(T)
        if E <= 1e-6:
            return 0.0
        eff = 0.55 * (V / E)
        return float(min(max(eff, 0.0), 0.7))

    def vi_curve(
        self, temperature_K: float, fuel_utilization: float, anode_porosity: float, j_max: float = 15000.0, num_points: int = 50
    ) -> Tuple[List[float], List[float], float, float]:
        if num_points < 2:
            num_points = 2
        step = (j_max - 0.0) / (num_points - 1)
        j_vals: List[float] = [0.0 + i * step for i in range(num_points)]
        V_vals: List[float] = [
            self.cell_voltage(
                OperatingPoint(
                    temperature_K=temperature_K,
                    current_density_A_per_m2=float(j),
                    fuel_utilization=fuel_utilization,
                    anode_porosity=anode_porosity,
                )
            )
            for j in j_vals
        ]
        # Evaluate T_stack and efficiency at an operating point near max power
        power_vals = [j_vals[i] * V_vals[i] for i in range(len(j_vals))]
        idx_mp = max(range(len(power_vals)), key=lambda i: power_vals[i])
        j_mp = float(j_vals[idx_mp])
        V_mp = float(V_vals[idx_mp])
        T_stack = self.stack_temperature(temperature_K, j_mp, fuel_utilization)
        eta_elec = self.electrical_efficiency(V_mp, temperature_K)
        return j_vals, V_vals, T_stack, eta_elec
