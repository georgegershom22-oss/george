"""
SOFC (Solid Oxide Fuel Cell) Low-Fidelity Simulation Framework - Working Version
Generates multi-fidelity training data for machine learning applications.

This module implements a realistic 1D system-level lumped electrochemical model
for SOFC stack simulation with parametric sweep capabilities.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
from typing import Dict, List, Tuple, Optional
import time
from tqdm import tqdm
import joblib
from pathlib import Path

warnings.filterwarnings('ignore')

class SOFCSimulationWorking:
    """
    Realistic 1D System-Level Lumped Electrochemical Model for SOFC Stack
    
    This class implements a physically meaningful model that produces
    realistic varying outputs based on operating conditions.
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
        
        # Electrode properties
        self.anode_thickness = 1e-3  # Anode thickness [m]
        self.cathode_thickness = 1e-3  # Cathode thickness [m]
        self.electrolyte_thickness = 1e-4  # Electrolyte thickness [m]
        
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
        
    def calculate_nernst_potential(self):
        """Calculate Nernst potential based on temperature and gas composition"""
        
        # Standard potential at temperature T
        E0 = 1.253 - 0.000245 * (self.T_op - 273.15)  # [V]
        
        # Gas partial pressures (realistic variation)
        p_h2 = 0.8 * self.p_total * (1 - 0.2 * self.fuel_util)  # Hydrogen partial pressure
        p_h2o = 0.2 * self.p_total * (1 + 0.3 * self.fuel_util)  # Water partial pressure  
        p_o2 = 0.21 * self.p_total * (1 - 0.1 * self.air_util)  # Oxygen partial pressure
        
        # Nernst equation
        E_nernst = E0 + (self.R * self.T_op / (2 * self.F)) * np.log(
            (p_h2 * np.sqrt(p_o2)) / p_h2o
        )
        
        return E_nernst
        
    def calculate_ohmic_overpotential(self):
        """Calculate ohmic overpotential"""
        
        # Temperature-dependent conductivities
        T_ref = 1073.15  # Reference temperature [K]
        
        # Electrolyte conductivity (YSZ)
        sigma_electrolyte = 0.1 * np.exp(-10000 / self.R * (1/self.T_op - 1/T_ref))
        
        # Electronic conductivities (less temperature dependent)
        sigma_anode = 1000 * (1 + 0.001 * (self.T_op - T_ref))
        sigma_cathode = 1000 * (1 + 0.001 * (self.T_op - T_ref))
        
        # Resistances
        R_anode = self.anode_thickness / (sigma_anode * self.cell_area)
        R_cathode = self.cathode_thickness / (sigma_cathode * self.cell_area)
        R_electrolyte = self.electrolyte_thickness / (sigma_electrolyte * self.cell_area)
        
        # Total ohmic resistance per cell
        R_cell = R_anode + R_cathode + R_electrolyte
        
        # Ohmic overpotential
        eta_ohmic = self.i_app * R_cell
        
        return eta_ohmic
        
    def calculate_activation_overpotential(self):
        """Calculate activation overpotential"""
        
        # Temperature-dependent exchange current densities
        T_ref = 1073.15  # Reference temperature [K]
        
        i0_anode = 1000 * np.exp(-50000 / self.R * (1/self.T_op - 1/T_ref))
        i0_cathode = 1000 * np.exp(-60000 / self.R * (1/self.T_op - 1/T_ref))
        
        # Butler-Volmer equation (simplified)
        alpha = 0.5
        eta_act_anode = (self.R * self.T_op / (alpha * self.F)) * np.log(self.i_app / i0_anode)
        eta_act_cathode = (self.R * self.T_op / (alpha * self.F)) * np.log(self.i_app / i0_cathode)
        
        return eta_act_anode, eta_act_cathode
        
    def calculate_concentration_overpotential(self):
        """Calculate concentration overpotential"""
        
        # Limiting current density based on mass transport
        D_eff = 1e-4 * self.anode_porosity**1.5  # Effective diffusivity
        i_lim = (2 * self.F * D_eff * 0.1) / self.anode_thickness
        
        # Concentration overpotential
        if self.i_app >= i_lim:
            eta_conc = 0.5  # Large overpotential when limiting current reached
        else:
            eta_conc = (self.R * self.T_op / (2 * self.F)) * np.log(1 - self.i_app / i_lim)
            
        return eta_conc
        
    def solve_cell_voltage(self):
        """Solve for cell voltage"""
        
        # Nernst potential
        E_nernst = self.calculate_nernst_potential()
        
        # Overpotentials
        eta_ohmic = self.calculate_ohmic_overpotential()
        eta_act_anode, eta_act_cathode = self.calculate_activation_overpotential()
        eta_conc = self.calculate_concentration_overpotential()
        
        # Total cell voltage - NO CLIPPING to allow natural variation
        V_cell = E_nernst - eta_ohmic - eta_act_anode - eta_act_cathode - eta_conc
        
        # Only ensure minimum voltage (no upper limit)
        V_cell = max(0.1, V_cell)
        
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
        
        # Electrical efficiency - NO CLIPPING to allow natural variation
        eta_elec = P_stack / P_fuel if P_fuel > 0 else 0
        
        # Only ensure minimum efficiency
        eta_elec = max(0.1, eta_elec)
        
        return P_stack, P_fuel, eta_elec
        
    def calculate_stack_temperature(self, P_stack: float, P_fuel: float):
        """Calculate stack temperature considering thermal balance"""
        
        # Heat generation rate
        Q_gen = max(0, P_fuel - P_stack)  # [W]
        
        # Heat removal rate (convective cooling)
        A_surface = 2 * np.pi * 0.05 * 0.3  # Simplified surface area
        Q_removal = self.h_conv * A_surface * max(0, self.T_op - 298.15)  # [W]
        
        # Net heat accumulation
        Q_net = Q_gen - Q_removal
        
        # Temperature rise (simplified thermal model)
        mass_stack = self.rho_stack * 0.3 * np.pi * (0.05)**2
        if mass_stack > 0 and self.cp_stack > 0:
            dT_dt = Q_net / (mass_stack * self.cp_stack)
        else:
            dT_dt = 0
        
        # Steady-state temperature
        T_stack = self.T_op + np.clip(dT_dt * 100, -50, 200)
        
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
            
            try:
                V_stack, _, _, _, _, _, _ = self.solve_cell_voltage()
                P_stack, P_fuel, eta_elec = self.calculate_power_and_efficiency(V_stack)
                
                voltages.append(V_stack)
                powers.append(P_stack)
                efficiencies.append(eta_elec)
                
            except:
                # If simulation fails, use linear approximation
                V_approx = max(0.1, 1.0 - i/10000) * self.n_cells
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

class SOFCDatasetGeneratorWorking:
    """
    Generator for creating large-scale SOFC simulation datasets - Working Version
    """
    
    def __init__(self, n_samples: int = 10200):
        self.n_samples = n_samples
        self.simulator = SOFCSimulationWorking()
        
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
        
    def generate_dataset(self, n_jobs: int = -1, save_path: str = "sofc_dataset_working.csv"):
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
        plt.savefig('sofc_dataset_working_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()

def main():
    """Main function to generate the SOFC dataset"""
    
    print("SOFC Low-Fidelity Dataset Generator - Working Version")
    print("=" * 60)
    
    # Create dataset generator
    generator = SOFCDatasetGeneratorWorking(n_samples=10200)
    
    # Generate dataset
    start_time = time.time()
    df = generator.generate_dataset(n_jobs=-1, save_path="sofc_low_fidelity_dataset_working.csv")
    end_time = time.time()
    
    print(f"\nDataset generation completed in {end_time - start_time:.2f} seconds")
    
    # Analyze dataset
    generator.analyze_dataset(df)
    
    # Save additional formats
    df.to_parquet("sofc_low_fidelity_dataset_working.parquet", index=False)
    
    print("\nDataset saved in multiple formats:")
    print("- sofc_low_fidelity_dataset_working.csv")
    print("- sofc_low_fidelity_dataset_working.parquet") 
    
    return df

if __name__ == "__main__":
    df = main()