"""
SOFC (Solid Oxide Fuel Cell) Low-Fidelity Simulation Framework
==============================================================

This module implements a 1D system-level lumped electrochemical model for SOFC
simulation, designed to generate large datasets for multi-fidelity training.

Based on fundamental SOFC electrochemical principles and thermodynamics.
"""

import numpy as np
import pandas as pd
from scipy.optimize import fsolve
from scipy.constants import R  # Gas constant
F = 96485.33212  # Faraday constant (C/mol)
import matplotlib.pyplot as plt
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

class SOFCModel:
    """
    1D System-Level Lumped Electrochemical SOFC Model
    
    This model captures the essential physics of SOFC operation including:
    - Electrochemical kinetics (Butler-Volmer equation)
    - Ohmic losses
    - Concentration polarization
    - Thermal effects
    - Mass transport limitations
    """
    
    def __init__(self):
        # Physical constants
        self.R = R  # Universal gas constant (J/mol·K)
        self.F = F  # Faraday constant (C/mol)
        
        # Default material properties (can be varied in parametric study)
        self.default_params = {
            # Operating conditions
            'T_op': 1073.15,  # Operating temperature (K) - 800°C
            'P_op': 101325,   # Operating pressure (Pa)
            
            # Fuel composition (H2/H2O/N2)
            'X_H2_in': 0.97,   # H2 mole fraction at inlet
            'X_H2O_in': 0.03,  # H2O mole fraction at inlet
            'X_N2_in': 0.0,    # N2 mole fraction at inlet
            
            # Air composition (O2/N2)
            'X_O2_in': 0.21,   # O2 mole fraction at inlet
            'X_N2_air_in': 0.79, # N2 mole fraction in air
            
            # Cell geometry and properties
            'A_cell': 0.01,    # Cell active area (m²)
            'L_electrolyte': 10e-6,  # Electrolyte thickness (m)
            'L_anode': 500e-6,       # Anode thickness (m)
            'L_cathode': 50e-6,      # Cathode thickness (m)
            
            # Material properties
            'sigma_electrolyte': 3.34e4 * np.exp(-10300/1073.15),  # Electrolyte conductivity (S/m)
            'sigma_anode': 9.5e7 / 1073.15,     # Anode conductivity (S/m)
            'sigma_cathode': 4.2e7 / 1073.15,   # Cathode conductivity (S/m)
            
            # Electrochemical parameters
            'i0_anode': 6500,    # Anode exchange current density (A/m²)
            'i0_cathode': 2000,  # Cathode exchange current density (A/m²)
            'alpha_a': 0.5,      # Anode charge transfer coefficient
            'alpha_c': 0.5,      # Cathode charge transfer coefficient
            
            # Porosity and tortuosity
            'epsilon_anode': 0.4,    # Anode porosity
            'epsilon_cathode': 0.4,  # Cathode porosity
            'tau_anode': 3.0,        # Anode tortuosity
            'tau_cathode': 3.0,      # Cathode tortuosity
            
            # Mass transport
            'D_H2': 1.0e-4,      # H2 diffusivity (m²/s)
            'D_H2O': 1.0e-4,     # H2O diffusivity (m²/s)
            'D_O2': 1.0e-4,      # O2 diffusivity (m²/s)
            
            # Fuel utilization
            'U_f': 0.85,         # Fuel utilization factor
        }
    
    def nernst_voltage(self, T, P_H2, P_H2O, P_O2):
        """
        Calculate the Nernst voltage (theoretical open circuit voltage)
        
        Parameters:
        -----------
        T : float
            Temperature (K)
        P_H2, P_H2O, P_O2 : float
            Partial pressures (Pa)
        
        Returns:
        --------
        float
            Nernst voltage (V)
        """
        # Standard Gibbs free energy change for H2 + 1/2 O2 -> H2O
        # Approximation: ΔG° = -241,830 + 44.36*T (J/mol)
        delta_G0 = -241830 + 44.36 * T
        
        # Nernst equation
        E_nernst = -delta_G0 / (2 * self.F) + (self.R * T) / (2 * self.F) * np.log(
            (P_H2 * np.sqrt(P_O2)) / P_H2O
        )
        
        return E_nernst
    
    def ohmic_resistance(self, params):
        """
        Calculate total ohmic resistance
        
        Parameters:
        -----------
        params : dict
            Model parameters
            
        Returns:
        --------
        float
            Total ohmic resistance (Ω·m²)
        """
        # Temperature-dependent conductivities
        T = params['T_op']
        
        # Electrolyte resistance (dominant)
        R_electrolyte = params['L_electrolyte'] / (
            3.34e4 * np.exp(-10300/T)
        )
        
        # Electrode resistances
        R_anode = params['L_anode'] / (9.5e7 / T)
        R_cathode = params['L_cathode'] / (4.2e7 / T)
        
        return R_electrolyte + R_anode + R_cathode
    
    def activation_overpotential(self, i, params, electrode='anode'):
        """
        Calculate activation overpotential using Butler-Volmer equation
        
        Parameters:
        -----------
        i : float
            Current density (A/m²)
        params : dict
            Model parameters
        electrode : str
            'anode' or 'cathode'
            
        Returns:
        --------
        float
            Activation overpotential (V)
        """
        T = params['T_op']
        
        if electrode == 'anode':
            i0 = params['i0_anode']
            alpha = params['alpha_a']
        else:
            i0 = params['i0_cathode']
            alpha = params['alpha_c']
        
        # Temperature correction for exchange current density
        i0_T = i0 * np.exp(-5000/T + 5000/1073.15)
        
        # Butler-Volmer equation (simplified for high overpotentials)
        if abs(i) < 1e-6:
            return 0.0
        
        eta_act = (self.R * T) / (alpha * self.F) * np.log(abs(i) / i0_T)
        
        return eta_act if i > 0 else -eta_act
    
    def concentration_overpotential(self, i, params):
        """
        Calculate concentration overpotential due to mass transport limitations
        
        Parameters:
        -----------
        i : float
            Current density (A/m²)
        params : dict
            Model parameters
            
        Returns:
        --------
        float
            Concentration overpotential (V)
        """
        T = params['T_op']
        
        # Limiting current density (simplified)
        i_lim_anode = 2 * self.F * params['D_H2'] * params['epsilon_anode'] / (
            params['tau_anode'] * params['L_anode']
        ) * params['X_H2_in'] * params['P_op'] / (self.R * T)
        
        i_lim_cathode = 4 * self.F * params['D_O2'] * params['epsilon_cathode'] / (
            params['tau_cathode'] * params['L_cathode']
        ) * params['X_O2_in'] * params['P_op'] / (self.R * T)
        
        i_lim = min(i_lim_anode, i_lim_cathode)
        
        # Concentration overpotential
        if abs(i) >= 0.95 * i_lim:
            return float('inf')  # Mass transport limit reached
        
        eta_conc = (self.R * T) / (2 * self.F) * np.log(1 / (1 - abs(i) / i_lim))
        
        return eta_conc
    
    def cell_voltage(self, i, params):
        """
        Calculate cell voltage for given current density
        
        Parameters:
        -----------
        i : float
            Current density (A/m²)
        params : dict
            Model parameters
            
        Returns:
        --------
        float
            Cell voltage (V)
        """
        # Partial pressures (simplified - assume uniform)
        P_H2 = params['X_H2_in'] * params['P_op']
        P_H2O = params['X_H2O_in'] * params['P_op']
        P_O2 = params['X_O2_in'] * params['P_op']
        
        # Nernst voltage
        E_nernst = self.nernst_voltage(params['T_op'], P_H2, P_H2O, P_O2)
        
        # Overpotentials
        eta_act_anode = self.activation_overpotential(i, params, 'anode')
        eta_act_cathode = self.activation_overpotential(i, params, 'cathode')
        eta_ohmic = i * self.ohmic_resistance(params)
        eta_conc = self.concentration_overpotential(i, params)
        
        # Cell voltage
        V_cell = E_nernst - eta_act_anode - eta_act_cathode - eta_ohmic - eta_conc
        
        return V_cell
    
    def stack_temperature(self, i, params, n_cells=1):
        """
        Calculate stack temperature considering heat generation and removal
        
        Parameters:
        -----------
        i : float
            Current density (A/m²)
        params : dict
            Model parameters
        n_cells : int
            Number of cells in stack
            
        Returns:
        --------
        float
            Stack temperature (K)
        """
        # Heat generation rate (W/m²)
        V_cell = self.cell_voltage(i, params)
        E_nernst = self.nernst_voltage(
            params['T_op'], 
            params['X_H2_in'] * params['P_op'],
            params['X_H2O_in'] * params['P_op'],
            params['X_O2_in'] * params['P_op']
        )
        
        # Heat generation = (E_nernst - V_cell) * i
        q_gen = (E_nernst - V_cell) * i
        
        # Simplified heat balance (assume convective cooling)
        # ΔT = q_gen / (h * A) where h is heat transfer coefficient
        h_conv = 100  # W/m²·K (typical for forced convection)
        
        delta_T = q_gen / h_conv
        T_stack = params['T_op'] + delta_T
        
        return T_stack
    
    def electrochemical_efficiency(self, i, params):
        """
        Calculate electrochemical efficiency
        
        Parameters:
        -----------
        i : float
            Current density (A/m²)
        params : dict
            Model parameters
            
        Returns:
        --------
        float
            Electrochemical efficiency (-)
        """
        V_cell = self.cell_voltage(i, params)
        E_nernst = self.nernst_voltage(
            params['T_op'], 
            params['X_H2_in'] * params['P_op'],
            params['X_H2O_in'] * params['P_op'],
            params['X_O2_in'] * params['P_op']
        )
        
        if E_nernst <= 0:
            return 0.0
        
        eta_elec = V_cell / E_nernst
        
        return max(0.0, eta_elec)  # Ensure non-negative
    
    def generate_vi_curve(self, params, i_max=10000, n_points=50):
        """
        Generate voltage-current (V-I) characteristic curve
        
        Parameters:
        -----------
        params : dict
            Model parameters
        i_max : float
            Maximum current density (A/m²)
        n_points : int
            Number of points in curve
            
        Returns:
        --------
        tuple
            (current_densities, voltages)
        """
        current_densities = np.linspace(0, i_max, n_points)
        voltages = []
        
        for i in current_densities:
            try:
                V = self.cell_voltage(i, params)
                if np.isfinite(V) and V > 0:
                    voltages.append(V)
                else:
                    voltages.append(0.0)
            except:
                voltages.append(0.0)
        
        return current_densities, np.array(voltages)
    
    def simulate_single_case(self, params):
        """
        Simulate a single SOFC case and extract key outputs
        
        Parameters:
        -----------
        params : dict
            Model parameters
            
        Returns:
        --------
        dict
            Simulation results
        """
        # Generate V-I curve
        i_range, V_range = self.generate_vi_curve(params)
        
        # Find operating point (maximum power density)
        power_density = i_range * V_range
        max_power_idx = np.argmax(power_density)
        
        i_operating = i_range[max_power_idx]
        V_operating = V_range[max_power_idx]
        
        # Calculate key outputs at operating point
        T_stack = self.stack_temperature(i_operating, params)
        eta_elec = self.electrochemical_efficiency(i_operating, params)
        
        # Additional metrics
        power_density_max = np.max(power_density)
        
        results = {
            # Operating point
            'current_density_op': i_operating,
            'voltage_op': V_operating,
            'power_density_max': power_density_max,
            
            # Key outputs
            'T_stack': T_stack,
            'eta_elec': eta_elec,
            
            # V-I curve characteristics
            'V_ocv': V_range[0],  # Open circuit voltage
            'i_max': i_range[np.where(V_range > 0.1)[0][-1]] if np.any(V_range > 0.1) else 0,
            
            # Input parameters (for reference)
            'T_op': params['T_op'],
            'U_f': params['U_f'],
            'epsilon_anode': params['epsilon_anode'],
            'X_H2_in': params['X_H2_in'],
        }
        
        return results


def generate_parameter_space(n_samples=10200):
    """
    Generate parameter space for parametric sweep
    
    Parameters:
    -----------
    n_samples : int
        Number of samples to generate
        
    Returns:
    --------
    list
        List of parameter dictionaries
    """
    np.random.seed(42)  # For reproducibility
    
    parameter_sets = []
    
    for i in range(n_samples):
        # Base parameters
        base_params = SOFCModel().default_params.copy()
        
        # Vary key parameters within realistic ranges
        params = base_params.copy()
        
        # Operating temperature (700-900°C)
        params['T_op'] = np.random.uniform(973.15, 1173.15)  # 700-900°C in Kelvin
        
        # Fuel utilization (0.6-0.95)
        params['U_f'] = np.random.uniform(0.6, 0.95)
        
        # Anode porosity (0.2-0.6)
        params['epsilon_anode'] = np.random.uniform(0.2, 0.6)
        
        # Cathode porosity (0.2-0.6)
        params['epsilon_cathode'] = np.random.uniform(0.2, 0.6)
        
        # Fuel composition variation
        params['X_H2_in'] = np.random.uniform(0.8, 0.99)
        params['X_H2O_in'] = 1.0 - params['X_H2_in']
        
        # Exchange current densities (±50% variation)
        params['i0_anode'] = base_params['i0_anode'] * np.random.uniform(0.5, 1.5)
        params['i0_cathode'] = base_params['i0_cathode'] * np.random.uniform(0.5, 1.5)
        
        # Electrolyte thickness (5-20 μm)
        params['L_electrolyte'] = np.random.uniform(5e-6, 20e-6)
        
        # Operating pressure (1-5 atm)
        params['P_op'] = np.random.uniform(101325, 505625)
        
        parameter_sets.append(params)
    
    return parameter_sets


def run_parametric_sweep(n_samples=10200, output_file='sofc_lf_dataset.csv'):
    """
    Run parametric sweep to generate low-fidelity SOFC dataset
    
    Parameters:
    -----------
    n_samples : int
        Number of samples to generate
    output_file : str
        Output CSV filename
        
    Returns:
    --------
    pandas.DataFrame
        Generated dataset
    """
    print(f"Generating {n_samples} low-fidelity SOFC simulations...")
    print("This may take several minutes...")
    
    # Initialize model
    model = SOFCModel()
    
    # Generate parameter space
    parameter_sets = generate_parameter_space(n_samples)
    
    # Run simulations
    results = []
    failed_simulations = 0
    
    for i, params in enumerate(tqdm(parameter_sets, desc="Running simulations")):
        try:
            result = model.simulate_single_case(params)
            
            # Add sample ID
            result['sample_id'] = i
            
            # Validate results
            if (result['eta_elec'] > 0 and result['eta_elec'] <= 1.0 and 
                result['T_stack'] > 0 and result['power_density_max'] > 0):
                results.append(result)
            else:
                failed_simulations += 1
                
        except Exception as e:
            failed_simulations += 1
            continue
    
    print(f"Completed {len(results)} successful simulations")
    print(f"Failed simulations: {failed_simulations}")
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"Dataset saved to {output_file}")
    
    return df


if __name__ == "__main__":
    # Generate the low-fidelity dataset
    dataset = run_parametric_sweep(n_samples=10200)
    
    # Display summary statistics
    print("\n" + "="*60)
    print("DATASET SUMMARY STATISTICS")
    print("="*60)
    print(f"Total samples: {len(dataset)}")
    print(f"Dataset shape: {dataset.shape}")
    print("\nKey output statistics:")
    print(dataset[['T_stack', 'eta_elec', 'power_density_max', 'V_ocv']].describe())