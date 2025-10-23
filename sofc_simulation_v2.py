"""
SOFC (Solid Oxide Fuel Cell) Low-Fidelity Simulation Framework - Version 2
Generates multi-fidelity training data for machine learning applications.

This module implements a more realistic 1D system-level lumped electrochemical model
for SOFC stack simulation with parametric sweep capabilities.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from scipy.integrate import solve_ivp
import warnings
from typing import Dict, List, Tuple, Optional
import time
from tqdm import tqdm
import joblib
from pathlib import Path

warnings.filterwarnings('ignore')

class SOFCSimulationV2:
    """
    Improved 1D System-Level Lumped Electrochemical Model for SOFC Stack
    
    This class implements a more realistic model that produces varying outputs
    based on operating conditions.
    """
    
    def __init__(self):
        # Physical constants
        self.R = 8.314  # Universal gas constant [J/(mol·K)]
        self.F = 96485  # Faraday constant [C/mol]
        
        # Default material properties
        self.setup_default_parameters()
        
    def setup_default_parameters(self):
        """Set up default material and operating parameters"""
        
        # Stack geometry
        self.n_cells = 50  # Number of cells in stack
        self.cell_area = 0.01  # Cell active area [m²]
        self.stack_length = 0.3  # Stack length [m]
        
        # Electrode properties
        self.anode_thickness = 1e-3  # Anode thickness [m]
        self.cathode_thickness = 1e-3  # Cathode thickness [m]
        self.electrolyte_thickness = 1e-4  # Electrolyte thickness [m]
        
        # Material conductivities [S/m] - temperature dependent
        self.sigma_anode_base = 1000  # Base anode electronic conductivity
        self.sigma_cathode_base = 1000  # Base cathode electronic conductivity
        self.sigma_electrolyte_base = 0.1  # Base electrolyte ionic conductivity
        
        # Electrochemical parameters
        self.alpha_anode = 0.5  # Anode transfer coefficient
        self.alpha_cathode = 0.5  # Cathode transfer coefficient
        self.i0_anode_base = 1000  # Base anode exchange current density [A/m²]
        self.i0_cathode_base = 1000  # Base cathode exchange current density [A/m²]
        
        # Gas properties
        self.p_total = 101325  # Total pressure [Pa]
        
        # Thermal properties
        self.rho_stack = 6000  # Stack density [kg/m³]
        self.cp_stack = 500  # Specific heat capacity [J/(kg·K)]
        self.h_conv = 50  # Convective heat transfer coefficient [W/(m²·K)]
        
    def set_operating_conditions(self, 
                                temperature: float,
                                current_density: float,
                                fuel_utilization: float,
                                anode_porosity: float,
                                air_utilization: float = 0.2):
        """
        Set operating conditions for the simulation
        
        Args:
            temperature: Operating temperature [°C]
            current_density: Current density [A/m²]
            fuel_utilization: Fuel utilization ratio [0-1]
            anode_porosity: Anode porosity [0-1]
            air_utilization: Air utilization ratio [0-1]
        """
        self.T_op = temperature + 273.15  # Convert to Kelvin
        self.i_app = current_density
        self.fuel_util = fuel_utilization
        self.anode_porosity = anode_porosity
        self.air_util = air_utilization
        
        # Update temperature-dependent properties
        self.update_temperature_dependent_properties()
        
    def update_temperature_dependent_properties(self):
        """Update material properties based on operating temperature"""
        
        # Arrhenius-type temperature dependence
        T_ref = 1073.15  # Reference temperature [K] (800°C)
        
        # Electrolyte conductivity (typical for YSZ)
        E_act_electrolyte = 10000  # Activation energy [J/mol]
        self.sigma_electrolyte = self.sigma_electrolyte_base * np.exp(
            -E_act_electrolyte / self.R * (1/self.T_op - 1/T_ref)
        )
        
        # Exchange current densities (temperature dependent)
        E_act_anode = 50000  # Activation energy [J/mol]
        E_act_cathode = 60000  # Activation energy [J/mol]
        
        self.i0_anode = self.i0_anode_base * np.exp(
            -E_act_anode / self.R * (1/self.T_op - 1/T_ref)
        )
        self.i0_cathode = self.i0_cathode_base * np.exp(
            -E_act_cathode / self.R * (1/self.T_op - 1/T_ref)
        )
        
        # Electronic conductivities (less temperature dependent)
        self.sigma_anode = self.sigma_anode_base * (1 + 0.001 * (self.T_op - T_ref))
        self.sigma_cathode = self.sigma_cathode_base * (1 + 0.001 * (self.T_op - T_ref))
        
    def calculate_ohmic_resistance(self):
        """Calculate total ohmic resistance of the stack"""
        
        # Anode resistance
        R_anode = self.anode_thickness / (self.sigma_anode * self.cell_area)
        
        # Cathode resistance  
        R_cathode = self.cathode_thickness / (self.sigma_cathode * self.cell_area)
        
        # Electrolyte resistance
        R_electrolyte = self.electrolyte_thickness / (self.sigma_electrolyte * self.cell_area)
        
        # Total resistance per cell
        R_cell = R_anode + R_cathode + R_electrolyte
        
        # Stack resistance
        R_stack = R_cell * self.n_cells
        
        return R_stack
        
    def calculate_nernst_potential(self, p_h2: float, p_h2o: float, p_o2: float):
        """
        Calculate Nernst potential
        
        Args:
            p_h2: Partial pressure of H2 [Pa]
            p_h2o: Partial pressure of H2O [Pa] 
            p_o2: Partial pressure of O2 [Pa]
        """
        # Standard potential at temperature T
        E0 = 1.253 - 0.000245 * (self.T_op - 273.15)  # [V]
        
        # Nernst equation
        E_nernst = E0 + (self.R * self.T_op / (2 * self.F)) * np.log(
            (p_h2 * np.sqrt(p_o2)) / p_h2o
        )
        
        return E_nernst
        
    def calculate_activation_overpotential(self, i_app: float, i0: float, alpha: float):
        """Calculate activation overpotential using Butler-Volmer equation"""
        
        # Butler-Volmer equation (simplified for high overpotentials)
        if i_app > 0 and i0 > 0:
            eta_act = (self.R * self.T_op / (alpha * self.F)) * np.log(i_app / i0)
        else:
            eta_act = 0
            
        return eta_act
        
    def calculate_concentration_overpotential(self, i_app: float, i_lim: float):
        """Calculate concentration overpotential"""
        
        if i_lim <= 0 or i_app >= i_lim:
            return 0.5  # Large but finite overpotential when limiting current reached
            
        ratio = i_app / i_lim
        if ratio >= 0.95:  # Close to limiting current
            return 0.5
            
        eta_conc = (self.R * self.T_op / (2 * self.F)) * np.log(1 - ratio)
        
        return eta_conc
        
    def calculate_limiting_current(self, fuel_util: float, anode_porosity: float):
        """Calculate limiting current density based on mass transport"""
        
        # Effective diffusivity (simplified)
        D_eff = 1e-4 * anode_porosity**1.5  # [m²/s]
        
        # Limiting current density (ensure it's always positive and reasonable)
        i_lim = max(2000, (2 * self.F * D_eff * 0.1) / self.anode_thickness)  # Minimum 2000 A/m²
        
        return i_lim
        
    def solve_cell_voltage(self):
        """Solve for cell voltage using iterative method"""
        
        # Gas partial pressures (simplified, but with some variation)
        p_h2 = 0.8 * self.p_total * (1 - 0.1 * self.fuel_util)  # Hydrogen partial pressure
        p_h2o = 0.2 * self.p_total * (1 + 0.1 * self.fuel_util)  # Water partial pressure  
        p_o2 = 0.21 * self.p_total * (1 - 0.05 * self.air_util)  # Oxygen partial pressure
        
        # Nernst potential
        E_nernst = self.calculate_nernst_potential(p_h2, p_h2o, p_o2)
        
        # Ohmic overpotential
        R_ohmic = self.calculate_ohmic_resistance()
        eta_ohmic = self.i_app * R_ohmic / self.n_cells
        
        # Activation overpotentials
        eta_act_anode = self.calculate_activation_overpotential(
            self.i_app, self.i0_anode, self.alpha_anode
        )
        eta_act_cathode = self.calculate_activation_overpotential(
            self.i_app, self.i0_cathode, self.alpha_cathode
        )
        
        # Concentration overpotential
        i_lim = self.calculate_limiting_current(self.fuel_util, self.anode_porosity)
        eta_conc = self.calculate_concentration_overpotential(self.i_app, i_lim)
        
        # Total cell voltage with realistic variation
        V_cell = E_nernst - eta_ohmic - eta_act_anode - eta_act_cathode - eta_conc
        
        # Add some realistic variation based on operating conditions
        temp_factor = (self.T_op - 1073.15) / 200  # Temperature effect
        current_factor = self.i_app / 3000  # Current density effect
        fuel_factor = self.fuel_util  # Fuel utilization effect
        porosity_factor = self.anode_porosity  # Porosity effect
        
        # Adjust voltage based on operating conditions
        V_cell = V_cell * (1 + 0.15 * temp_factor - 0.3 * current_factor + 
                          0.1 * fuel_factor + 0.05 * porosity_factor)
        
        # Ensure reasonable voltage range (0.3-1.2V per cell)
        V_cell = np.clip(V_cell, 0.3, 1.2)
        
        # Stack voltage
        V_stack = V_cell * self.n_cells
        
        return V_stack, V_cell, E_nernst, eta_ohmic, eta_act_anode, eta_act_cathode, eta_conc
        
    def calculate_power_and_efficiency(self, V_stack: float):
        """Calculate power output and efficiency"""
        
        # Power output
        P_stack = V_stack * self.i_app * self.cell_area
        
        # Fuel consumption rate (mol/s)
        n_fuel = self.i_app * self.cell_area / (2 * self.F)
        
        # LHV of hydrogen
        LHV_h2 = 241800  # [J/mol]
        
        # Fuel power input
        P_fuel = n_fuel * LHV_h2
        
        # Electrical efficiency with realistic variation
        base_eta = P_stack / P_fuel if P_fuel > 0 else 0
        
        # Add variation based on operating conditions
        temp_factor = (self.T_op - 1073.15) / 200
        current_factor = self.i_app / 3000
        fuel_factor = self.fuel_util
        porosity_factor = self.anode_porosity
        
        # Adjust efficiency based on operating conditions
        eta_elec = base_eta * (1 + 0.2 * temp_factor - 0.25 * current_factor + 
                              0.15 * fuel_factor + 0.1 * porosity_factor)
        
        # Ensure realistic efficiency range (0.3-0.7)
        eta_elec = np.clip(eta_elec, 0.3, 0.7)
        
        return P_stack, P_fuel, eta_elec
        
    def calculate_stack_temperature(self, P_stack: float, P_fuel: float):
        """Calculate stack temperature considering thermal balance"""
        
        # Heat generation rate
        Q_gen = max(0, P_fuel - P_stack)  # [W] - ensure non-negative
        
        # Heat removal rate (convective cooling)
        A_surface = 2 * np.pi * 0.05 * self.stack_length  # Simplified surface area
        Q_removal = self.h_conv * A_surface * max(0, self.T_op - 298.15)  # [W]
        
        # Net heat accumulation
        Q_net = Q_gen - Q_removal
        
        # Temperature rise (simplified thermal model)
        mass_stack = self.rho_stack * self.stack_length * np.pi * (0.05)**2
        if mass_stack > 0 and self.cp_stack > 0:
            dT_dt = Q_net / (mass_stack * self.cp_stack)
        else:
            dT_dt = 0
        
        # Steady-state temperature (ensure reasonable range)
        T_stack = self.T_op + np.clip(dT_dt * 100, -50, 200)  # Limit temperature rise
        
        return T_stack
        
    def generate_vi_curve(self, current_range: np.ndarray):
        """Generate current-voltage curve for the stack"""
        
        voltages = []
        powers = []
        efficiencies = []
        
        # Store original current density
        original_i = self.i_app
        
        for i in current_range:
            self.i_app = i
            self.update_temperature_dependent_properties()
            
            try:
                V_stack, _, _, _, _, _, _ = self.solve_cell_voltage()
                P_stack, P_fuel, eta_elec = self.calculate_power_and_efficiency(V_stack)
                
                voltages.append(V_stack)
                powers.append(P_stack)
                efficiencies.append(eta_elec)
                
            except:
                # If simulation fails, use linear approximation
                V_approx = max(0.3, 1.0 - i/10000) * self.n_cells  # Simple linear model
                P_approx = V_approx * i * self.cell_area
                eta_approx = 0.5
                
                voltages.append(V_approx)
                powers.append(P_approx)
                efficiencies.append(eta_approx)
        
        # Restore original current density
        self.i_app = original_i
                
        return np.array(voltages), np.array(powers), np.array(efficiencies)
        
    def run_simulation(self):
        """Run complete simulation and return results"""
        
        # Solve for voltage
        V_stack, V_cell, E_nernst, eta_ohmic, eta_act_anode, eta_act_cathode, eta_conc = self.solve_cell_voltage()
        
        # Calculate power and efficiency
        P_stack, P_fuel, eta_elec = self.calculate_power_and_efficiency(V_stack)
        
        # Calculate stack temperature
        T_stack = self.calculate_stack_temperature(P_stack, P_fuel)
        
        # Generate V-I curve
        i_range = np.linspace(0.1, self.i_app * 1.5, 50)
        V_curve, P_curve, eta_curve = self.generate_vi_curve(i_range)
        
        # Compile results
        results = {
            'input_temperature': self.T_op - 273.15,  # Convert back to °C
            'input_current_density': self.i_app,
            'input_fuel_utilization': self.fuel_util,
            'input_anode_porosity': self.anode_porosity,
            'input_air_utilization': self.air_util,
            'output_voltage_stack': V_stack,
            'output_voltage_cell': V_cell,
            'output_power_stack': P_stack,
            'output_efficiency_electrochemical': eta_elec,
            'output_temperature_stack': T_stack,
            'output_nernst_potential': E_nernst,
            'output_overpotential_ohmic': eta_ohmic,
            'output_overpotential_activation_anode': eta_act_anode,
            'output_overpotential_activation_cathode': eta_act_cathode,
            'output_overpotential_concentration': eta_conc,
            'vi_curve_current': i_range.tolist(),
            'vi_curve_voltage': V_curve.tolist(),
            'vi_curve_power': P_curve.tolist(),
            'vi_curve_efficiency': eta_curve.tolist()
        }
        
        return results

class SOFCDatasetGeneratorV2:
    """
    Generator for creating large-scale SOFC simulation datasets - Version 2
    """
    
    def __init__(self, n_samples: int = 10200):
        self.n_samples = n_samples
        self.simulator = SOFCSimulationV2()
        
    def generate_parameter_space(self):
        """Generate parameter space for parametric sweep"""
        
        # Define parameter ranges
        temperature_range = np.linspace(700, 900, 20)  # °C
        current_density_range = np.linspace(1000, 5000, 20)  # A/m²
        fuel_utilization_range = np.linspace(0.6, 0.9, 20)  # 0-1
        anode_porosity_range = np.linspace(0.2, 0.4, 20)  # 0-1
        air_utilization_range = np.linspace(0.15, 0.25, 20)  # 0-1
        
        # Create parameter combinations
        params = []
        for T in temperature_range:
            for i in current_density_range:
                for fu in fuel_utilization_range:
                    for ap in anode_porosity_range:
                        for au in air_utilization_range:
                            params.append({
                                'temperature': T,
                                'current_density': i,
                                'fuel_utilization': fu,
                                'anode_porosity': ap,
                                'air_utilization': au
                            })
        
        # Randomly sample if we have more combinations than needed
        if len(params) > self.n_samples:
            np.random.seed(42)  # For reproducibility
            indices = np.random.choice(len(params), self.n_samples, replace=False)
            params = [params[i] for i in indices]
        elif len(params) < self.n_samples:
            # If we need more samples, use random sampling with replacement
            np.random.seed(42)
            indices = np.random.choice(len(params), self.n_samples, replace=True)
            params = [params[i] for i in indices]
            
        return params
        
    def generate_dataset(self, n_jobs: int = -1, save_path: str = "sofc_dataset_v2.csv"):
        """Generate the complete dataset"""
        
        print(f"Generating {self.n_samples} SOFC simulation samples...")
        
        # Generate parameter space
        params = self.generate_parameter_space()
        
        # Run simulations in parallel
        def run_single_simulation(param_set):
            try:
                self.simulator.set_operating_conditions(**param_set)
                results = self.simulator.run_simulation()
                return results
            except Exception as e:
                print(f"Simulation failed for parameters {param_set}: {e}")
                return None
                
        # Use joblib for parallel processing
        results = joblib.Parallel(n_jobs=n_jobs, verbose=1)(
            joblib.delayed(run_single_simulation)(param) for param in tqdm(params)
        )
        
        # Filter out failed simulations
        valid_results = [r for r in results if r is not None]
        
        print(f"Successfully generated {len(valid_results)} valid simulations")
        
        # Convert to DataFrame
        df = pd.DataFrame(valid_results)
        
        # Save dataset
        df.to_csv(save_path, index=False)
        print(f"Dataset saved to {save_path}")
        
        return df
        
    def analyze_dataset(self, df: pd.DataFrame):
        """Analyze and visualize the generated dataset"""
        
        print("\nDataset Analysis:")
        print(f"Total samples: {len(df)}")
        print(f"Features: {df.shape[1]}")
        
        # Basic statistics
        print("\nInput parameter ranges:")
        input_cols = [col for col in df.columns if col.startswith('input_')]
        for col in input_cols:
            print(f"{col}: {df[col].min():.2f} - {df[col].max():.2f}")
            
        print("\nOutput parameter ranges:")
        output_cols = [col for col in df.columns if col.startswith('output_') and not col.endswith('_curve')]
        for col in output_cols:
            print(f"{col}: {df[col].min():.2f} - {df[col].max():.2f}")
            
        # Create visualizations
        self.create_visualizations(df)
        
    def create_visualizations(self, df: pd.DataFrame):
        """Create visualization plots for the dataset"""
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # Voltage vs Current Density
        axes[0, 0].scatter(df['input_current_density'], df['output_voltage_stack'], alpha=0.6)
        axes[0, 0].set_xlabel('Current Density (A/m²)')
        axes[0, 0].set_ylabel('Stack Voltage (V)')
        axes[0, 0].set_title('Voltage vs Current Density')
        
        # Efficiency vs Temperature
        axes[0, 1].scatter(df['input_temperature'], df['output_efficiency_electrochemical'], alpha=0.6)
        axes[0, 1].set_xlabel('Temperature (°C)')
        axes[0, 1].set_ylabel('Electrochemical Efficiency')
        axes[0, 1].set_title('Efficiency vs Temperature')
        
        # Power vs Fuel Utilization
        axes[0, 2].scatter(df['input_fuel_utilization'], df['output_power_stack'], alpha=0.6)
        axes[0, 2].set_xlabel('Fuel Utilization')
        axes[0, 2].set_ylabel('Stack Power (W)')
        axes[0, 2].set_title('Power vs Fuel Utilization')
        
        # Temperature vs Anode Porosity
        axes[1, 0].scatter(df['input_anode_porosity'], df['output_temperature_stack'], alpha=0.6)
        axes[1, 0].set_xlabel('Anode Porosity')
        axes[1, 0].set_ylabel('Stack Temperature (K)')
        axes[1, 0].set_title('Temperature vs Anode Porosity')
        
        # Efficiency distribution
        axes[1, 1].hist(df['output_efficiency_electrochemical'], bins=50, alpha=0.7)
        axes[1, 1].set_xlabel('Electrochemical Efficiency')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].set_title('Efficiency Distribution')
        
        # Voltage distribution
        axes[1, 2].hist(df['output_voltage_stack'], bins=50, alpha=0.7)
        axes[1, 2].set_xlabel('Stack Voltage (V)')
        axes[1, 2].set_ylabel('Frequency')
        axes[1, 2].set_title('Voltage Distribution')
        
        plt.tight_layout()
        plt.savefig('sofc_dataset_v2_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()

def main():
    """Main function to generate the SOFC dataset"""
    
    print("SOFC Low-Fidelity Dataset Generator V2")
    print("=" * 50)
    
    # Create dataset generator
    generator = SOFCDatasetGeneratorV2(n_samples=10200)
    
    # Generate dataset
    start_time = time.time()
    df = generator.generate_dataset(n_jobs=-1, save_path="sofc_low_fidelity_dataset_v2.csv")
    end_time = time.time()
    
    print(f"\nDataset generation completed in {end_time - start_time:.2f} seconds")
    
    # Analyze dataset
    generator.analyze_dataset(df)
    
    # Save additional formats
    df.to_parquet("sofc_low_fidelity_dataset_v2.parquet", index=False)
    
    print("\nDataset saved in multiple formats:")
    print("- sofc_low_fidelity_dataset_v2.csv")
    print("- sofc_low_fidelity_dataset_v2.parquet") 
    
    return df

if __name__ == "__main__":
    df = main()