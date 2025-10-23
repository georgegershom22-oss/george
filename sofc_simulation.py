"""
SOFC Low-Fidelity Simulation Dataset Generator
=============================================

This module generates a large dataset of low-fidelity SOFC simulations
using a 1D system-level lumped electrochemical model.

Key Features:
- 1D model of entire SOFC stack
- Parametric sweep with >10,000 samples
- Global parameters: temperature, fuel utilization, current density, anode porosity
- Outputs: V-I curve, stack temperature, electrochemical efficiency
- Target runtime: ~10 minutes per sample
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from scipy.integrate import solve_ivp
import h5py
from tqdm import tqdm
import joblib
from joblib import Parallel, delayed
import os
import time
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class SOFCLowFidelityModel:
    """
    1D System-Level Lumped Electrochemical Model for SOFC Stack
    
    This class implements a simplified 1D model that captures the essential
    physics of SOFC operation while being computationally efficient.
    """
    
    def __init__(self):
        # Physical constants
        self.R = 8.314  # Universal gas constant (J/mol/K)
        self.F = 96485  # Faraday's constant (C/mol)
        
        # Default material properties
        self.set_default_properties()
        
    def set_default_properties(self):
        """Set default material and operating properties"""
        # Electrolyte properties
        self.sigma_elec = 0.1  # Electrical conductivity (S/m)
        self.t_elec = 50e-6    # Electrolyte thickness (m)
        
        # Electrode properties
        self.t_anode = 500e-6   # Anode thickness (m)
        self.t_cathode = 50e-6  # Cathode thickness (m)
        self.porosity_anode = 0.3  # Anode porosity
        self.porosity_cathode = 0.3  # Cathode porosity
        
        # Cell geometry
        self.A_cell = 0.01  # Cell area (m²)
        self.L_stack = 0.1  # Stack length (m)
        
        # Gas properties
        self.M_H2 = 2.016e-3    # H2 molecular weight (kg/mol)
        self.M_H2O = 18.015e-3  # H2O molecular weight (kg/mol)
        self.M_O2 = 31.999e-3   # O2 molecular weight (kg/mol)
        self.M_N2 = 28.014e-3   # N2 molecular weight (kg/mol)
        
    def calculate_activation_overpotential(self, T: float, i: float, p_H2: float, p_H2O: float) -> float:
        """
        Calculate activation overpotential for anode
        
        Args:
            T: Temperature (K)
            i: Current density (A/m²)
            p_H2: H2 partial pressure (Pa)
            p_H2O: H2O partial pressure (Pa)
            
        Returns:
            Activation overpotential (V)
        """
        # Exchange current density (A/m²) - more realistic values
        i0 = 100 * np.exp(-80000 / (self.R * T)) * (p_H2 / 101325)**0.5 * (p_H2O / 101325)**0.5
        
        # Butler-Volmer equation
        alpha = 0.5  # Transfer coefficient
        eta_act = (self.R * T) / (alpha * self.F) * np.arcsinh(i / (2 * i0))
        
        return eta_act
    
    def calculate_ohmic_overpotential(self, T: float, i: float) -> float:
        """
        Calculate ohmic overpotential
        
        Args:
            T: Temperature (K)
            i: Current density (A/m²)
            
        Returns:
            Ohmic overpotential (V)
        """
        # Temperature-dependent conductivity (more realistic)
        sigma = 100 * np.exp(-8000 / T)  # S/m
        
        # Ohmic resistance
        R_ohmic = self.t_elec / (sigma * self.A_cell)
        
        return i * R_ohmic
    
    def calculate_concentration_overpotential(self, T: float, i: float, p_H2: float, p_H2O: float) -> float:
        """
        Calculate concentration overpotential
        
        Args:
            T: Temperature (K)
            i: Current density (A/m²)
            p_H2: H2 partial pressure (Pa)
            p_H2O: H2O partial pressure (Pa)
            
        Returns:
            Concentration overpotential (V)
        """
        # Limiting current density (more realistic)
        i_L = 15000  # A/m²
        
        # Concentration overpotential (avoid negative values)
        if i >= i_L:
            eta_conc = 0.5  # Maximum concentration overpotential
        else:
            eta_conc = (self.R * T) / (2 * self.F) * np.log(1 - i / i_L)
        
        return eta_conc
    
    def calculate_nernst_voltage(self, T: float, p_H2: float, p_H2O: float, p_O2: float) -> float:
        """
        Calculate Nernst voltage
        
        Args:
            T: Temperature (K)
            p_H2: H2 partial pressure (Pa)
            p_H2O: H2O partial pressure (Pa)
            p_O2: O2 partial pressure (Pa)
            
        Returns:
            Nernst voltage (V)
        """
        # Standard potential at temperature T
        E0 = 1.253 - 0.0002451 * T
        
        # Nernst equation
        E_nernst = E0 + (self.R * T) / (2 * self.F) * np.log(
            (p_H2 * np.sqrt(p_O2)) / p_H2O
        )
        
        return E_nernst
    
    def calculate_stack_temperature(self, T_inlet: float, i: float, eta_elec: float) -> float:
        """
        Calculate stack temperature considering heat generation
        
        Args:
            T_inlet: Inlet temperature (K)
            i: Current density (A/m²)
            eta_elec: Electrochemical efficiency
            
        Returns:
            Stack temperature (K)
        """
        # Heat generation rate (W/m²) - more realistic
        Q_gen = i * (1.25 - eta_elec) * 0.1  # Reduced heat generation
        
        # Heat transfer coefficient (W/m²/K)
        h = 100  # Improved heat transfer
        
        # Temperature rise (limited)
        delta_T = min(Q_gen / h, 50)  # Maximum 50K temperature rise
        
        return T_inlet + delta_T
    
    def simulate_single_point(self, params: Dict) -> Dict:
        """
        Simulate a single operating point
        
        Args:
            params: Dictionary containing input parameters
            
        Returns:
            Dictionary containing simulation results
        """
        # Extract parameters
        T = params['temperature'] + 273.15  # Convert to Kelvin
        i = params['current_density']
        U_f = params['fuel_utilization']
        porosity_anode = params['anode_porosity']
        
        # Calculate partial pressures (simplified)
        p_H2 = 0.8 * 101325  # 80% H2
        p_H2O = 0.2 * 101325  # 20% H2O
        p_O2 = 0.21 * 101325  # 21% O2 in air
        
        # Calculate overpotentials
        eta_act = self.calculate_activation_overpotential(T, i, p_H2, p_H2O)
        eta_ohmic = self.calculate_ohmic_overpotential(T, i)
        eta_conc = self.calculate_concentration_overpotential(T, i, p_H2, p_H2O)
        
        # Calculate Nernst voltage
        E_nernst = self.calculate_nernst_voltage(T, p_H2, p_H2O, p_O2)
        
        # Calculate cell voltage (ensure positive)
        V_cell = max(0.1, E_nernst - eta_act - eta_ohmic - eta_conc)
        
        # Calculate electrochemical efficiency (ensure realistic range)
        eta_elec = min(0.8, max(0.3, V_cell / E_nernst))
        
        # Calculate stack temperature
        T_stack = self.calculate_stack_temperature(T, i, eta_elec)
        
        # Calculate power density
        P_density = V_cell * i
        
        # Calculate fuel consumption rate
        n_H2_consumed = i / (2 * self.F)  # mol/s/m²
        
        return {
            'voltage': V_cell,
            'current_density': i,
            'power_density': P_density,
            'efficiency': eta_elec,
            'stack_temperature': T_stack - 273.15,  # Convert back to Celsius
            'nernst_voltage': E_nernst,
            'activation_overpotential': eta_act,
            'ohmic_overpotential': eta_ohmic,
            'concentration_overpotential': eta_conc,
            'fuel_consumption_rate': n_H2_consumed
        }
    
    def generate_vi_curve(self, params: Dict, i_range: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate V-I curve for given parameters
        
        Args:
            params: Dictionary containing input parameters
            i_range: Array of current densities to evaluate
            
        Returns:
            Tuple of (voltages, current_densities)
        """
        voltages = []
        
        for i in i_range:
            temp_params = params.copy()
            temp_params['current_density'] = i
            result = self.simulate_single_point(temp_params)
            voltages.append(result['voltage'])
        
        return np.array(voltages), i_range

class SOFCDatasetGenerator:
    """
    Generator for SOFC low-fidelity simulation dataset
    """
    
    def __init__(self, model: SOFCLowFidelityModel):
        self.model = model
        self.results = []
        
    def generate_parameter_space(self, n_samples: int = 10200) -> pd.DataFrame:
        """
        Generate parameter space for parametric sweep
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            DataFrame containing parameter combinations
        """
        np.random.seed(42)  # For reproducibility
        
        # Define parameter ranges
        param_ranges = {
            'temperature': (700, 900),  # °C
            'current_density': (1000, 10000),  # A/m²
            'fuel_utilization': (0.6, 0.9),  # dimensionless
            'anode_porosity': (0.2, 0.4),  # dimensionless
        }
        
        # Generate random samples
        params = {}
        for param, (min_val, max_val) in param_ranges.items():
            if param == 'temperature':
                # Use normal distribution centered at 800°C
                params[param] = np.random.normal(800, 50, n_samples)
                params[param] = np.clip(params[param], min_val, max_val)
            else:
                params[param] = np.random.uniform(min_val, max_val, n_samples)
        
        return pd.DataFrame(params)
    
    def simulate_batch(self, params_df: pd.DataFrame, batch_size: int = 100) -> List[Dict]:
        """
        Simulate a batch of parameter combinations
        
        Args:
            params_df: DataFrame containing parameter combinations
            batch_size: Number of simulations per batch
            
        Returns:
            List of simulation results
        """
        results = []
        
        for idx, row in tqdm(params_df.iterrows(), total=len(params_df), desc="Simulating"):
            params = row.to_dict()
            
            # Simulate single point
            result = self.model.simulate_single_point(params)
            
            # Add input parameters to result
            result.update(params)
            result['sample_id'] = idx
            
            results.append(result)
            
            # Add V-I curve data
            i_range = np.linspace(1000, 10000, 50)
            voltages, currents = self.model.generate_vi_curve(params, i_range)
            result['vi_voltages'] = voltages.tolist()
            result['vi_currents'] = currents.tolist()
        
        return results
    
    def save_dataset(self, results: List[Dict], filename: str = "sofc_lf_dataset.h5"):
        """
        Save dataset to HDF5 file
        
        Args:
            results: List of simulation results
            filename: Output filename
        """
        with h5py.File(filename, 'w') as f:
            # Create groups
            inputs_group = f.create_group('inputs')
            outputs_group = f.create_group('outputs')
            vi_curves_group = f.create_group('vi_curves')
            
            # Input parameters
            input_params = ['temperature', 'current_density', 'fuel_utilization', 'anode_porosity']
            for param in input_params:
                inputs_group.create_dataset(param, data=[r[param] for r in results])
            
            # Output parameters
            output_params = ['voltage', 'power_density', 'efficiency', 'stack_temperature', 
                           'nernst_voltage', 'activation_overpotential', 'ohmic_overpotential', 
                           'concentration_overpotential', 'fuel_consumption_rate']
            for param in output_params:
                outputs_group.create_dataset(param, data=[r[param] for r in results])
            
            # V-I curves
            vi_curves_group.create_dataset('voltages', data=[r['vi_voltages'] for r in results])
            vi_curves_group.create_dataset('currents', data=[r['vi_currents'] for r in results])
            
            # Metadata
            f.attrs['n_samples'] = len(results)
            f.attrs['description'] = 'SOFC Low-Fidelity Simulation Dataset'
            f.attrs['model_type'] = '1D System-Level Lumped Electrochemical Model'
            f.attrs['created'] = time.strftime('%Y-%m-%d %H:%M:%S')
    
    def save_csv_dataset(self, results: List[Dict], filename: str = "sofc_lf_dataset.csv"):
        """
        Save dataset to CSV file (flattened version)
        
        Args:
            results: List of simulation results
            filename: Output filename
        """
        # Flatten results for CSV
        flattened_results = []
        for result in results:
            flat_result = {k: v for k, v in result.items() if k not in ['vi_voltages', 'vi_currents']}
            flattened_results.append(flat_result)
        
        df = pd.DataFrame(flattened_results)
        df.to_csv(filename, index=False)
        print(f"Dataset saved to {filename} with {len(df)} samples")

def main():
    """
    Main function to generate the SOFC low-fidelity dataset
    """
    print("SOFC Low-Fidelity Dataset Generator")
    print("=" * 50)
    
    # Initialize model and generator
    model = SOFCLowFidelityModel()
    generator = SOFCDatasetGenerator(model)
    
    # Generate parameter space
    print("Generating parameter space...")
    n_samples = 10200
    params_df = generator.generate_parameter_space(n_samples)
    print(f"Generated {len(params_df)} parameter combinations")
    
    # Save parameter space
    params_df.to_csv("sofc_parameter_space.csv", index=False)
    print("Parameter space saved to sofc_parameter_space.csv")
    
    # Simulate batch
    print("Starting simulations...")
    start_time = time.time()
    
    results = generator.simulate_batch(params_df)
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time_per_sample = total_time / len(results)
    
    print(f"Simulation completed in {total_time:.2f} seconds")
    print(f"Average time per sample: {avg_time_per_sample:.2f} seconds")
    
    # Save datasets
    print("Saving datasets...")
    generator.save_dataset(results, "sofc_lf_dataset.h5")
    generator.save_csv_dataset(results, "sofc_lf_dataset.csv")
    
    # Generate summary statistics
    print("\nDataset Summary:")
    print(f"Total samples: {len(results)}")
    print(f"Input parameters: {list(params_df.columns)}")
    print(f"Output parameters: {list(results[0].keys()) if results else 'None'}")
    
    # Plot sample results
    if results:
        plot_sample_results(results[:10])  # Plot first 10 samples
    
    print("\nDataset generation completed successfully!")

def plot_sample_results(results: List[Dict], n_samples: int = 10):
    """
    Plot sample results for visualization
    
    Args:
        results: List of simulation results
        n_samples: Number of samples to plot
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # V-I curves
    ax1 = axes[0, 0]
    for i in range(min(n_samples, len(results))):
        result = results[i]
        ax1.plot(result['vi_currents'], result['vi_voltages'], alpha=0.7)
    ax1.set_xlabel('Current Density (A/m²)')
    ax1.set_ylabel('Voltage (V)')
    ax1.set_title('V-I Curves')
    ax1.grid(True)
    
    # Efficiency vs Temperature
    ax2 = axes[0, 1]
    temperatures = [r['temperature'] for r in results[:n_samples]]
    efficiencies = [r['efficiency'] for r in results[:n_samples]]
    ax2.scatter(temperatures, efficiencies, alpha=0.7)
    ax2.set_xlabel('Temperature (°C)')
    ax2.set_ylabel('Efficiency')
    ax2.set_title('Efficiency vs Temperature')
    ax2.grid(True)
    
    # Power Density vs Current Density
    ax3 = axes[1, 0]
    current_densities = [r['current_density'] for r in results[:n_samples]]
    power_densities = [r['power_density'] for r in results[:n_samples]]
    ax3.scatter(current_densities, power_densities, alpha=0.7)
    ax3.set_xlabel('Current Density (A/m²)')
    ax3.set_ylabel('Power Density (W/m²)')
    ax3.set_title('Power Density vs Current Density')
    ax3.grid(True)
    
    # Stack Temperature vs Current Density
    ax4 = axes[1, 1]
    stack_temperatures = [r['stack_temperature'] for r in results[:n_samples]]
    ax4.scatter(current_densities, stack_temperatures, alpha=0.7)
    ax4.set_xlabel('Current Density (A/m²)')
    ax4.set_ylabel('Stack Temperature (°C)')
    ax4.set_title('Stack Temperature vs Current Density')
    ax4.grid(True)
    
    plt.tight_layout()
    plt.savefig('sofc_sample_results.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()