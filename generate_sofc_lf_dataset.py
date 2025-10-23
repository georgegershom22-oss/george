"""
Low-Fidelity SOFC Simulation Dataset Generator
Generates 10,200 samples of 1D System-Level Lumped Electrochemical Model data

This script simulates a parametric sweep of SOFC operating conditions and generates
synthetic data similar to what would be obtained from COMSOL Multiphysics 1D simulations.
"""

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import os
from datetime import datetime
import json

# Physical Constants
R = 8.314  # Universal gas constant (J/mol·K)
F = 96485  # Faraday constant (C/mol)
P_atm = 101325  # Atmospheric pressure (Pa)

class SOFCLowFidelityModel:
    """
    1D Lumped Parameter SOFC Model
    Based on electrochemical principles and empirical correlations
    """
    
    def __init__(self, temperature, fuel_utilization, anode_porosity, 
                 anode_thickness=500e-6, cathode_thickness=50e-6, 
                 electrolyte_thickness=10e-6, active_area=100e-4):
        """
        Initialize SOFC model parameters
        
        Parameters:
        -----------
        temperature : float
            Operating temperature (°C)
        fuel_utilization : float
            Fuel utilization factor (0-1)
        anode_porosity : float
            Anode porosity (0-1)
        anode_thickness : float
            Anode thickness (m)
        cathode_thickness : float
            Cathode thickness (m)
        electrolyte_thickness : float
            Electrolyte thickness (m)
        active_area : float
            Active cell area (m²)
        """
        self.T_celsius = temperature
        self.T = temperature + 273.15  # Convert to Kelvin
        self.fuel_util = fuel_utilization
        self.epsilon_a = anode_porosity
        self.L_a = anode_thickness
        self.L_c = cathode_thickness
        self.L_e = electrolyte_thickness
        self.A = active_area
        
        # Gas compositions (mole fractions)
        self.X_H2_in = 0.97  # Hydrogen at anode inlet
        self.X_H2O_in = 0.03  # Water at anode inlet
        self.X_O2 = 0.21  # Oxygen at cathode
        
        # Material properties (temperature-dependent)
        self._calculate_material_properties()
    
    def _calculate_material_properties(self):
        """Calculate temperature-dependent material properties"""
        # Electrolyte ionic conductivity (S/m) - YSZ (Yttria-Stabilized Zirconia)
        self.sigma_e = 3.34e4 * np.exp(-10300 / self.T)
        
        # Electrode electronic conductivity (S/m)
        self.sigma_a = 9.5e7 / self.T * np.exp(-1150 / self.T)  # Anode (Ni-YSZ)
        self.sigma_c = 4.2e7 / self.T * np.exp(-1200 / self.T)  # Cathode (LSM)
        
        # Exchange current density (A/m²) - depends on porosity and temperature
        self.i0_a = 2.8e8 * self.epsilon_a**3 * np.exp(-120000 / (R * self.T))  # Anode
        self.i0_c = 2.0e9 * np.exp(-160000 / (R * self.T))  # Cathode
        
        # Diffusion coefficients (m²/s)
        self.D_H2 = 2.5e-5 * (self.T / 1073)**1.5 * self.epsilon_a**1.5
        self.D_H2O = 2.5e-5 * (self.T / 1073)**1.5 * self.epsilon_a**1.5
        self.D_O2 = 2.2e-5 * (self.T / 1073)**1.5
    
    def nernst_voltage(self, current_density):
        """
        Calculate Nernst voltage (thermodynamic open-circuit voltage)
        Accounts for local gas composition changes due to electrochemical reactions
        """
        # Calculate average fuel utilization along the channel
        # At a given current density, local composition changes
        i = max(current_density, 1e-6)  # Avoid division by zero
        
        # Local hydrogen and water partial pressures (considering fuel utilization)
        # As current increases, H2 is consumed and H2O is produced
        utilization_factor = min(i / 15000, self.fuel_util)  # Limit by design fuel utilization
        
        P_H2 = (self.X_H2_in - utilization_factor * self.X_H2_in) * P_atm
        P_H2O = (self.X_H2O_in + utilization_factor * self.X_H2_in) * P_atm
        P_O2 = self.X_O2 * P_atm
        
        # Ensure positive pressures
        P_H2 = max(P_H2, 0.01 * P_atm)
        P_H2O = max(P_H2O, 0.01 * P_atm)
        
        # Nernst equation
        E_nernst = 1.253 - 2.4516e-4 * self.T + (R * self.T) / (2 * F) * np.log(
            (P_H2 * P_O2**0.5) / P_H2O
        )
        
        return E_nernst
    
    def activation_overpotential(self, current_density):
        """Calculate activation losses (Butler-Volmer)"""
        i = max(current_density, 1e-6)
        
        # Anode activation overpotential
        eta_act_a = (R * self.T) / (2 * F) * np.arcsinh(i / (2 * self.i0_a))
        
        # Cathode activation overpotential
        eta_act_c = (R * self.T) / (4 * F) * np.arcsinh(i / (2 * self.i0_c))
        
        return eta_act_a + eta_act_c
    
    def ohmic_overpotential(self, current_density):
        """Calculate ohmic losses (resistive)"""
        # Electrolyte resistance
        R_e = self.L_e / self.sigma_e
        
        # Electrode resistances (simplified)
        R_a = self.L_a / (3 * self.sigma_a)
        R_c = self.L_c / (3 * self.sigma_c)
        
        # Total area-specific resistance (Ω·m²)
        ASR = R_e + R_a + R_c
        
        eta_ohm = current_density * ASR
        
        return eta_ohm
    
    def concentration_overpotential(self, current_density):
        """Calculate concentration losses (mass transport)"""
        i = max(current_density, 1e-6)
        
        # Limiting current densities
        i_L_a = 2 * F * self.D_H2 * self.X_H2_in * P_atm / (R * self.T * self.L_a)
        i_L_c = 4 * F * self.D_O2 * self.X_O2 * P_atm / (R * self.T * self.L_c)
        
        # Concentration overpotentials
        eta_conc_a = (R * self.T) / (2 * F) * np.log(1 - i / i_L_a) if i < 0.95 * i_L_a else 1.0
        eta_conc_c = (R * self.T) / (4 * F) * np.log(1 - i / i_L_c) if i < 0.95 * i_L_c else 1.0
        
        return abs(eta_conc_a) + abs(eta_conc_c)
    
    def cell_voltage(self, current_density):
        """Calculate cell voltage at given current density"""
        E_nernst = self.nernst_voltage(current_density)
        eta_act = self.activation_overpotential(current_density)
        eta_ohm = self.ohmic_overpotential(current_density)
        eta_conc = self.concentration_overpotential(current_density)
        
        V_cell = E_nernst - eta_act - eta_ohm - eta_conc
        
        return max(V_cell, 0.0)
    
    def generate_vi_curve(self, num_points=50):
        """
        Generate voltage-current (V-I) characteristic curve
        
        Returns:
        --------
        current_densities : array
            Current density values (A/m²)
        voltages : array
            Corresponding cell voltages (V)
        """
        # Current density range (A/m²)
        i_max = 20000  # Maximum current density
        current_densities = np.linspace(0, i_max, num_points)
        
        voltages = np.array([self.cell_voltage(i) for i in current_densities])
        
        # Find maximum power point
        power_densities = voltages * current_densities
        max_power_idx = np.argmax(power_densities)
        
        # Limit curve to before voltage drops too much
        valid_idx = np.where(voltages > 0.3)[0]
        if len(valid_idx) > 0:
            last_valid = valid_idx[-1]
            current_densities = current_densities[:last_valid+1]
            voltages = voltages[:last_valid+1]
        
        return current_densities, voltages
    
    def stack_temperature(self, current_density):
        """
        Calculate stack temperature considering heat generation
        
        Heat sources:
        - Irreversible losses (activation, ohmic, concentration)
        - Reversible heat (entropy change)
        """
        V_cell = self.cell_voltage(current_density)
        E_nernst = self.nernst_voltage(current_density)
        
        # Heat generation rate per unit area (W/m²)
        q_irrev = current_density * (E_nernst - V_cell)  # Irreversible losses
        q_rev = current_density * self.T * 0.000274  # Reversible heat (simplified)
        q_total = q_irrev + q_rev
        
        # Temperature rise estimation (simplified heat transfer)
        # Assuming natural convection and radiation cooling
        h_conv = 25  # Convective heat transfer coefficient (W/m²·K)
        epsilon_rad = 0.8  # Emissivity
        sigma_sb = 5.67e-8  # Stefan-Boltzmann constant
        
        # Equilibrium temperature rise
        T_ambient = 293.15  # K
        delta_T = q_total / (h_conv + 4 * epsilon_rad * sigma_sb * self.T**3)
        
        T_stack = self.T + delta_T * 0.5  # Factor accounting for cooling
        
        return T_stack - 273.15  # Return in Celsius
    
    def electrochemical_efficiency(self, current_density):
        """
        Calculate electrochemical efficiency
        η = V_cell / E_thermoneutral
        """
        V_cell = self.cell_voltage(current_density)
        E_thermoneutral = 1.48  # Thermoneutral voltage for H2/O2 at SOFC temps (V)
        
        eta_elec = V_cell / E_thermoneutral
        
        return min(eta_elec, 1.0)  # Cap at 100%


def generate_parameter_samples(num_samples=10200):
    """
    Generate parameter samples for parametric sweep
    Uses Latin Hypercube Sampling for better space coverage
    """
    np.random.seed(42)  # For reproducibility
    
    # Parameter ranges
    param_ranges = {
        'temperature': (700, 900),  # °C
        'fuel_utilization': (0.6, 0.9),  # fraction
        'anode_porosity': (0.25, 0.45),  # fraction
        'anode_thickness': (300e-6, 700e-6),  # m
        'cathode_thickness': (30e-6, 70e-6),  # m
        'electrolyte_thickness': (8e-6, 15e-6),  # m
        'active_area': (80e-4, 120e-4),  # m²
    }
    
    # Latin Hypercube Sampling
    samples = {}
    for param, (min_val, max_val) in param_ranges.items():
        # Generate uniformly distributed samples
        uniform_samples = np.random.uniform(0, 1, num_samples)
        # Scale to parameter range
        samples[param] = min_val + uniform_samples * (max_val - min_val)
    
    return pd.DataFrame(samples)


def simulate_sample(params, sample_id):
    """
    Simulate a single SOFC configuration
    
    Returns:
    --------
    result : dict
        Dictionary containing inputs, outputs, and V-I curve data
    """
    # Create SOFC model
    model = SOFCLowFidelityModel(
        temperature=params['temperature'],
        fuel_utilization=params['fuel_utilization'],
        anode_porosity=params['anode_porosity'],
        anode_thickness=params['anode_thickness'],
        cathode_thickness=params['cathode_thickness'],
        electrolyte_thickness=params['electrolyte_thickness'],
        active_area=params['active_area']
    )
    
    # Generate V-I curve
    current_densities, voltages = model.generate_vi_curve(num_points=25)
    
    # Calculate operating point metrics (at mid-range current density)
    i_operating = 8000  # A/m² (typical operating point)
    V_operating = model.cell_voltage(i_operating)
    T_stack = model.stack_temperature(i_operating)
    eta_elec = model.electrochemical_efficiency(i_operating)
    
    # Calculate additional metrics
    P_max = np.max(voltages * current_densities)
    V_oc = voltages[0]  # Open circuit voltage
    
    result = {
        'sample_id': sample_id,
        # Input parameters
        'temperature': params['temperature'],
        'fuel_utilization': params['fuel_utilization'],
        'anode_porosity': params['anode_porosity'],
        'anode_thickness': params['anode_thickness'] * 1e6,  # Convert to μm
        'cathode_thickness': params['cathode_thickness'] * 1e6,  # Convert to μm
        'electrolyte_thickness': params['electrolyte_thickness'] * 1e6,  # Convert to μm
        'active_area': params['active_area'] * 1e4,  # Convert to cm²
        # Output parameters at operating point
        'operating_current_density': i_operating,
        'operating_voltage': V_operating,
        'stack_temperature': T_stack,
        'electrochemical_efficiency': eta_elec,
        # V-I curve characteristics
        'open_circuit_voltage': V_oc,
        'max_power_density': P_max,
        # V-I curve data (serialized)
        'vi_current_densities': current_densities.tolist(),
        'vi_voltages': voltages.tolist(),
    }
    
    return result


def generate_dataset(num_samples=10200, output_dir='sofc_lf_dataset'):
    """
    Generate complete low-fidelity SOFC dataset
    """
    print(f"Generating Low-Fidelity SOFC Dataset with {num_samples} samples...")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate parameter samples
    print("\n[1/4] Generating parameter samples...")
    param_samples = generate_parameter_samples(num_samples)
    print(f"  ✓ Generated {len(param_samples)} parameter combinations")
    
    # Run simulations
    print("\n[2/4] Running simulations...")
    results = []
    
    for idx in range(len(param_samples)):
        params = param_samples.iloc[idx]
        result = simulate_sample(params, sample_id=idx)
        results.append(result)
        
        # Progress update every 1000 samples
        if (idx + 1) % 1000 == 0:
            print(f"  Progress: {idx + 1}/{num_samples} samples completed ({(idx+1)/num_samples*100:.1f}%)")
    
    print(f"  ✓ Completed {len(results)} simulations")
    
    # Convert to DataFrame
    print("\n[3/4] Processing results...")
    df = pd.DataFrame(results)
    
    # Split into main dataset and V-I curve data
    vi_curve_cols = ['sample_id', 'vi_current_densities', 'vi_voltages']
    df_vi_curves = df[vi_curve_cols].copy()
    
    main_cols = [col for col in df.columns if col not in ['vi_current_densities', 'vi_voltages']]
    df_main = df[main_cols].copy()
    
    # Save main dataset
    main_file = os.path.join(output_dir, 'sofc_lf_main_dataset.csv')
    df_main.to_csv(main_file, index=False)
    print(f"  ✓ Saved main dataset: {main_file}")
    
    # Save V-I curves (as JSON for array data)
    vi_file = os.path.join(output_dir, 'sofc_lf_vi_curves.json')
    df_vi_curves.to_json(vi_file, orient='records', indent=2)
    print(f"  ✓ Saved V-I curves: {vi_file}")
    
    # Generate summary statistics
    print("\n[4/4] Generating summary statistics...")
    summary = generate_summary_statistics(df_main)
    
    summary_file = os.path.join(output_dir, 'dataset_summary.txt')
    with open(summary_file, 'w') as f:
        f.write(summary)
    print(f"  ✓ Saved summary: {summary_file}")
    
    print(f"\n{'='*70}")
    print(f"Dataset Generation Complete!")
    print(f"{'='*70}")
    print(f"Total samples: {len(df_main)}")
    print(f"Output directory: {output_dir}")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    return df_main, df_vi_curves


def generate_summary_statistics(df):
    """Generate summary statistics for the dataset"""
    summary = []
    summary.append("="*70)
    summary.append("SOFC Low-Fidelity Dataset Summary")
    summary.append("="*70)
    summary.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary.append(f"Total Samples: {len(df)}")
    
    summary.append("\n" + "="*70)
    summary.append("INPUT PARAMETERS")
    summary.append("="*70)
    
    input_params = [
        'temperature', 'fuel_utilization', 'anode_porosity',
        'anode_thickness', 'cathode_thickness', 'electrolyte_thickness', 'active_area'
    ]
    
    for param in input_params:
        if param in df.columns:
            summary.append(f"\n{param}:")
            summary.append(f"  Min:    {df[param].min():.6f}")
            summary.append(f"  Max:    {df[param].max():.6f}")
            summary.append(f"  Mean:   {df[param].mean():.6f}")
            summary.append(f"  Std:    {df[param].std():.6f}")
    
    summary.append("\n" + "="*70)
    summary.append("OUTPUT PARAMETERS")
    summary.append("="*70)
    
    output_params = [
        'operating_voltage', 'stack_temperature', 'electrochemical_efficiency',
        'open_circuit_voltage', 'max_power_density'
    ]
    
    for param in output_params:
        if param in df.columns:
            summary.append(f"\n{param}:")
            summary.append(f"  Min:    {df[param].min():.6f}")
            summary.append(f"  Max:    {df[param].max():.6f}")
            summary.append(f"  Mean:   {df[param].mean():.6f}")
            summary.append(f"  Std:    {df[param].std():.6f}")
    
    summary.append("\n" + "="*70)
    summary.append("DATA QUALITY")
    summary.append("="*70)
    summary.append(f"\nMissing values: {df.isnull().sum().sum()}")
    summary.append(f"Duplicate samples: {df.duplicated().sum()}")
    
    summary.append("\n" + "="*70)
    summary.append("CORRELATION ANALYSIS")
    summary.append("="*70)
    summary.append("\nTop 5 correlations with operating_voltage:")
    corr_with_voltage = df.corr()['operating_voltage'].abs().sort_values(ascending=False)
    for param, corr in corr_with_voltage.head(6).items():
        if param != 'operating_voltage':
            summary.append(f"  {param}: {corr:.4f}")
    
    summary.append("\n" + "="*70)
    
    return "\n".join(summary)


if __name__ == "__main__":
    # Generate the dataset
    df_main, df_vi_curves = generate_dataset(num_samples=10200, output_dir='sofc_lf_dataset')
    
    print("\nDataset files created:")
    print("  1. sofc_lf_main_dataset.csv - Main simulation results")
    print("  2. sofc_lf_vi_curves.json - V-I characteristic curves")
    print("  3. dataset_summary.txt - Statistical summary")
    print("\nDataset is ready for use in multi-fidelity machine learning!")
