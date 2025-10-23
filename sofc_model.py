"""
SOFC (Solid Oxide Fuel Cell) 1D System-Level Lumped Electrochemical Model
This module implements a low-fidelity simulation model for generating training data.

Based on electrochemical principles and thermodynamic models for SOFC systems.
"""

import numpy as np
import pandas as pd
from scipy.optimize import fsolve
from scipy.constants import R  # Gas constant
F = 96485.33212  # Faraday constant (C/mol)
import warnings
warnings.filterwarnings('ignore')

class SOFCModel:
    """
    1D System-Level Lumped Electrochemical Model for SOFC
    
    This model simulates the electrochemical behavior of a SOFC stack
    using lumped parameters and simplified physics-based equations.
    """
    
    def __init__(self):
        # Physical constants
        self.R = R  # Universal gas constant (8.314 J/mol·K)
        self.F = F  # Faraday constant (96485 C/mol)
        
        # Default material properties and geometric parameters
        self.default_params = {
            # Geometric parameters
            'cell_area': 100e-4,  # Cell active area (m²) - 100 cm²
            'anode_thickness': 500e-6,  # Anode thickness (m)
            'cathode_thickness': 50e-6,  # Cathode thickness (m)
            'electrolyte_thickness': 10e-6,  # Electrolyte thickness (m)
            
            # Material properties
            'anode_porosity': 0.4,  # Anode porosity (-)
            'cathode_porosity': 0.4,  # Cathode porosity (-)
            'anode_tortuosity': 3.0,  # Anode tortuosity (-)
            'cathode_tortuosity': 3.0,  # Cathode tortuosity (-)
            
            # Electrochemical parameters
            'exchange_current_density_anode': 6500,  # A/m²
            'exchange_current_density_cathode': 2500,  # A/m²
            'activation_energy_anode': 120e3,  # J/mol
            'activation_energy_cathode': 160e3,  # J/mol
            
            # Transport properties
            'ionic_conductivity_ref': 3.34e4,  # S/m at reference temperature
            'electronic_conductivity_anode': 9.5e4,  # S/m
            'electronic_conductivity_cathode': 8.0e4,  # S/m
            'ref_temperature': 1073.15,  # Reference temperature (K) - 800°C
            
            # Gas composition and flow
            'fuel_utilization': 0.85,  # Fuel utilization factor
            'air_utilization': 0.21,  # Air utilization factor
            'h2_inlet_fraction': 0.97,  # H2 mole fraction at inlet
            'h2o_inlet_fraction': 0.03,  # H2O mole fraction at inlet
            'o2_inlet_fraction': 0.21,  # O2 mole fraction at inlet
        }
    
    def nernst_voltage(self, temperature, p_h2, p_o2, p_h2o):
        """
        Calculate the Nernst voltage (thermodynamic equilibrium voltage)
        
        Args:
            temperature: Operating temperature (K)
            p_h2: Partial pressure of H2 (Pa)
            p_o2: Partial pressure of O2 (Pa)
            p_h2o: Partial pressure of H2O (Pa)
            
        Returns:
            Nernst voltage (V)
        """
        # Standard Gibbs free energy change for H2 + 1/2 O2 -> H2O
        # Temperature dependent correlation
        delta_g = -241830 + 44.36 * temperature  # J/mol
        
        # Nernst equation
        e_nernst = -delta_g / (2 * self.F) + (self.R * temperature) / (2 * self.F) * \
                   np.log((p_h2 * np.sqrt(p_o2)) / p_h2o)
        
        return e_nernst
    
    def activation_overpotential(self, current_density, temperature, params):
        """
        Calculate activation overpotential using Butler-Volmer equation
        
        Args:
            current_density: Current density (A/m²)
            temperature: Operating temperature (K)
            params: Dictionary of model parameters
            
        Returns:
            Tuple of (anode_overpotential, cathode_overpotential) in V
        """
        # Exchange current densities (temperature dependent)
        i0_anode = params['exchange_current_density_anode'] * \
                   np.exp(-params['activation_energy_anode'] / (self.R * temperature) + 
                          params['activation_energy_anode'] / (self.R * params['ref_temperature']))
        
        i0_cathode = params['exchange_current_density_cathode'] * \
                     np.exp(-params['activation_energy_cathode'] / (self.R * temperature) + 
                            params['activation_energy_cathode'] / (self.R * params['ref_temperature']))
        
        # Activation overpotentials (Tafel approximation for high current densities)
        eta_act_anode = (self.R * temperature) / (2 * self.F) * \
                        np.log(current_density / i0_anode)
        
        eta_act_cathode = (self.R * temperature) / (2 * self.F) * \
                          np.log(current_density / i0_cathode)
        
        return eta_act_anode, eta_act_cathode
    
    def ohmic_overpotential(self, current_density, temperature, params):
        """
        Calculate ohmic overpotential due to ionic and electronic resistances
        
        Args:
            current_density: Current density (A/m²)
            temperature: Operating temperature (K)
            params: Dictionary of model parameters
            
        Returns:
            Ohmic overpotential (V)
        """
        # Ionic conductivity (temperature dependent)
        sigma_ionic = params['ionic_conductivity_ref'] * \
                      np.exp(-10300 / temperature + 10300 / params['ref_temperature'])
        
        # Resistances
        r_ionic = params['electrolyte_thickness'] / sigma_ionic
        r_anode = params['anode_thickness'] / params['electronic_conductivity_anode']
        r_cathode = params['cathode_thickness'] / params['electronic_conductivity_cathode']
        
        # Total ohmic resistance
        r_total = r_ionic + r_anode + r_cathode
        
        # Ohmic overpotential
        eta_ohmic = current_density * r_total
        
        return eta_ohmic
    
    def concentration_overpotential(self, current_density, temperature, params):
        """
        Calculate concentration overpotential due to mass transport limitations
        
        Args:
            current_density: Current density (A/m²)
            temperature: Operating temperature (K)
            params: Dictionary of model parameters
            
        Returns:
            Tuple of (anode_overpotential, cathode_overpotential) in V
        """
        # Limiting current densities (simplified model)
        i_limit_anode = 15000 * (temperature / 1073.15)**1.5 * params['anode_porosity']
        i_limit_cathode = 8000 * (temperature / 1073.15)**1.5 * params['cathode_porosity']
        
        # Concentration overpotentials
        eta_conc_anode = (self.R * temperature) / (2 * self.F) * \
                         np.log(1 / (1 - current_density / i_limit_anode))
        
        eta_conc_cathode = (self.R * temperature) / (2 * self.F) * \
                           np.log(1 / (1 - current_density / i_limit_cathode))
        
        return eta_conc_anode, eta_conc_cathode
    
    def calculate_cell_voltage(self, current_density, temperature, params):
        """
        Calculate cell voltage for given current density and temperature
        
        Args:
            current_density: Current density (A/m²)
            temperature: Operating temperature (K)
            params: Dictionary of model parameters
            
        Returns:
            Cell voltage (V)
        """
        # Partial pressures (simplified - assume average values)
        p_h2 = 50000  # Pa
        p_o2 = 21000  # Pa
        p_h2o = 3000  # Pa
        
        # Nernst voltage
        e_nernst = self.nernst_voltage(temperature, p_h2, p_o2, p_h2o)
        
        # Limit current density to prevent extreme overpotentials
        current_density = min(current_density, 8000)  # Limit to 8000 A/m²
        
        try:
            # Overpotentials
            eta_act_anode, eta_act_cathode = self.activation_overpotential(current_density, temperature, params)
            eta_ohmic = self.ohmic_overpotential(current_density, temperature, params)
            eta_conc_anode, eta_conc_cathode = self.concentration_overpotential(current_density, temperature, params)
            
            # Limit overpotentials to reasonable values
            eta_act_anode = min(eta_act_anode, 0.5)
            eta_act_cathode = min(eta_act_cathode, 0.5)
            eta_ohmic = min(eta_ohmic, 0.3)
            eta_conc_anode = min(eta_conc_anode, 0.2)
            eta_conc_cathode = min(eta_conc_cathode, 0.2)
            
            # Cell voltage
            v_cell = e_nernst - eta_act_anode - eta_act_cathode - eta_ohmic - eta_conc_anode - eta_conc_cathode
            
            # Ensure minimum voltage
            v_cell = max(0.1, v_cell)  # Minimum 0.1V
            
        except:
            # Fallback calculation for numerical issues
            v_cell = max(0.1, e_nernst * 0.6)  # 60% of Nernst voltage
        
        return v_cell
    
    def calculate_stack_temperature(self, current_density, temperature_inlet, params):
        """
        Calculate stack temperature considering heat generation and removal
        
        Args:
            current_density: Current density (A/m²)
            temperature_inlet: Inlet temperature (K)
            params: Dictionary of model parameters
            
        Returns:
            Stack temperature (K)
        """
        # Heat generation due to overpotentials
        v_cell = self.calculate_cell_voltage(current_density, temperature_inlet, params)
        e_nernst = self.nernst_voltage(temperature_inlet, 50000, 21000, 3000)
        
        # Heat generation rate per unit area (W/m²)
        q_gen = current_density * (e_nernst - v_cell)
        
        # Simplified heat balance (assuming some heat removal)
        delta_t = q_gen / (1000 * 1000)  # Simplified heat capacity term
        
        t_stack = temperature_inlet + delta_t
        
        return t_stack
    
    def calculate_efficiency(self, current_density, temperature, params):
        """
        Calculate electrochemical efficiency
        
        Args:
            current_density: Current density (A/m²)
            temperature: Operating temperature (K)
            params: Dictionary of model parameters
            
        Returns:
            Electrochemical efficiency (-)
        """
        v_cell = self.calculate_cell_voltage(current_density, temperature, params)
        e_nernst = self.nernst_voltage(temperature, 50000, 21000, 3000)
        
        efficiency = v_cell / e_nernst
        
        return max(0.0, min(1.0, efficiency))  # Clamp between 0 and 1
    
    def generate_vi_curve(self, temperature, params, current_range=None):
        """
        Generate voltage-current (V-I) curve for given temperature and parameters
        
        Args:
            temperature: Operating temperature (K)
            params: Dictionary of model parameters
            current_range: Range of current densities to evaluate (A/m²)
            
        Returns:
            Tuple of (current_densities, voltages) arrays
        """
        if current_range is None:
            current_range = np.linspace(100, 6000, 50)  # A/m² - reduced max current
        
        voltages = []
        for i in current_range:
            try:
                v = self.calculate_cell_voltage(i, temperature, params)
                voltages.append(max(0.1, v))  # Ensure minimum voltage of 0.1V
            except:
                # Fallback: simple linear approximation
                e_nernst = self.nernst_voltage(temperature, 50000, 21000, 3000)
                v_approx = max(0.1, e_nernst - i * 0.0002)  # Simple linear drop
                voltages.append(v_approx)
        
        return current_range, np.array(voltages)
    
    def simulate_single_case(self, params):
        """
        Simulate a single SOFC case with given parameters
        
        Args:
            params: Dictionary of model parameters
            
        Returns:
            Dictionary containing simulation results
        """
        # Extract key parameters
        temperature = params.get('operating_temperature', 1073.15)  # K
        
        # Generate V-I curve
        current_densities, voltages = self.generate_vi_curve(temperature, params)
        
        # Calculate key metrics at operating point (middle of current range)
        i_op = current_densities[len(current_densities)//2]
        v_op = voltages[len(voltages)//2]
        
        # Calculate stack temperature and efficiency
        t_stack = self.calculate_stack_temperature(i_op, temperature, params)
        efficiency = self.calculate_efficiency(i_op, temperature, params)
        
        # Calculate power density
        power_density = i_op * v_op  # W/m²
        
        results = {
            'operating_temperature': temperature,
            'current_density_op': i_op,
            'voltage_op': v_op,
            'power_density': power_density,
            'stack_temperature': t_stack,
            'electrochemical_efficiency': efficiency,
            'max_voltage': np.max(voltages),
            'min_voltage': np.min(voltages[voltages > 0]),
            'max_current_density': np.max(current_densities),
            'vi_curve_current': current_densities.tolist(),
            'vi_curve_voltage': voltages.tolist(),
        }
        
        # Add input parameters to results
        for key, value in params.items():
            if key not in results:
                results[f'input_{key}'] = value
        
        return results