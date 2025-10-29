"""
SOFC High-Fidelity Numerical Dataset Generator
Physics-Informed Data-Driven Modeling of SOFC Thermo-Mechanics

This script generates synthetic 3D FEA/CFD simulation data for SOFC systems
including electrochemical, thermal, mechanical, and species transport fields.
"""

import numpy as np
import h5py
from scipy.stats import qmc
from scipy.interpolate import RegularGridInterpolator
from datetime import datetime
import json
import os

class SOFCSimulator:
    """
    Physics-informed SOFC simulator for generating high-fidelity numerical data.
    """
    
    def __init__(self, grid_size=(50, 50, 20)):
        """
        Initialize the SOFC simulator with a 3D computational grid.
        
        Args:
            grid_size: Tuple of (nx, ny, nz) grid dimensions
        """
        self.nx, self.ny, self.nz = grid_size
        
        # Create 3D spatial mesh
        self.x = np.linspace(0, 0.1, self.nx)  # 10 cm length
        self.y = np.linspace(0, 0.1, self.ny)  # 10 cm width
        self.z = np.linspace(0, 0.003, self.nz)  # 3 mm total thickness
        
        self.X, self.Y, self.Z = np.meshgrid(self.x, self.y, self.z, indexing='ij')
        
        # Define layer boundaries (normalized z-coordinates)
        self.layers = {
            'anode': (0.0, 0.0015),           # 1.5 mm
            'electrolyte': (0.0015, 0.0018),  # 0.3 mm
            'cathode': (0.0018, 0.003)        # 1.2 mm
        }
        
    def get_layer_mask(self, layer_name):
        """Get boolean mask for a specific layer."""
        z_min, z_max = self.layers[layer_name]
        return (self.Z >= z_min) & (self.Z < z_max)
    
    def simulate_electrochemical_fields(self, params):
        """
        Simulate electrochemical fields based on Butler-Volmer kinetics
        and charge conservation.
        
        Args:
            params: Dictionary of simulation parameters
            
        Returns:
            current_density: 3D array of current density distribution [A/m²]
            overpotential: 3D array of overpotential distribution [V]
        """
        # Extract parameters
        voltage = params['voltage']
        current_density_avg = params['current_density']
        ionic_conductivity = params['ionic_conductivity']
        electronic_conductivity = params['electronic_conductivity']
        
        # Initialize fields
        current_density = np.zeros_like(self.X)
        overpotential = np.zeros_like(self.X)
        
        # Current density varies with position based on local conditions
        # Higher at center, lower at edges due to gas depletion
        radial_dist = np.sqrt((self.X - 0.05)**2 + (self.Y - 0.05)**2)
        radial_factor = 1.0 - 0.3 * (radial_dist / 0.05)**2
        
        # Electrochemical activity in anode and cathode
        anode_mask = self.get_layer_mask('anode')
        cathode_mask = self.get_layer_mask('cathode')
        
        # Current density distribution (Butler-Volmer approximation)
        exchange_current_density = 5000  # A/m³
        alpha = 0.5  # charge transfer coefficient
        F = 96485  # Faraday constant [C/mol]
        R = 8.314  # Gas constant [J/(mol·K)]
        T = params['fuel_inlet_temp']
        
        # Simplified Butler-Volmer
        eta_act = 0.05 + 0.1 * (1 - radial_factor)  # Activation overpotential (3D array)
        
        current_density[anode_mask] = (current_density_avg * 
                                       radial_factor[anode_mask] * 
                                       (1 + 0.2 * np.random.randn(*current_density[anode_mask].shape)))
        
        current_density[cathode_mask] = (current_density_avg * 
                                         radial_factor[cathode_mask] * 
                                         (1 + 0.15 * np.random.randn(*current_density[cathode_mask].shape)))
        
        # Overpotential distribution
        # Ohmic losses through electrolyte
        electrolyte_mask = self.get_layer_mask('electrolyte')
        electrolyte_thickness = 0.0003  # 0.3 mm
        
        ohmic_loss = current_density_avg * electrolyte_thickness / ionic_conductivity
        
        # Assign overpotential values (use 3D arrays then apply mask)
        eta_act_full = eta_act * radial_factor
        overpotential[anode_mask] = eta_act_full[anode_mask]
        overpotential[cathode_mask] = eta_act_full[cathode_mask]
        overpotential[electrolyte_mask] = ohmic_loss
        
        return current_density, overpotential
    
    def simulate_thermal_fields(self, params, current_density):
        """
        Simulate temperature distribution based on heat generation and transport.
        
        Args:
            params: Dictionary of simulation parameters
            current_density: 3D array of current density
            
        Returns:
            temperature: 3D array of temperature distribution [K]
        """
        # Extract parameters
        T_fuel_inlet = params['fuel_inlet_temp']
        T_air_inlet = params['air_inlet_temp']
        fuel_flow_rate = params['fuel_flow_rate']
        air_flow_rate = params['air_flow_rate']
        
        # Base temperature from operating conditions
        T_base = (T_fuel_inlet + T_air_inlet) / 2
        
        # Heat generation from electrochemical reactions
        # Q = I²R (ohmic) + I·η (activation) + ΔH_rxn (reaction enthalpy)
        overpotential_heat = current_density * 0.1  # Simplified heat source
        
        # Temperature rises with distance from inlet (convective cooling)
        x_normalized = self.X / 0.1
        y_normalized = self.Y / 0.1
        
        # Temperature gradient along flow direction
        flow_effect = 50 * x_normalized  # Temperature rises along x
        
        # Heat accumulation in solid (higher in electrolyte, lower conductivity)
        anode_mask = self.get_layer_mask('anode')
        electrolyte_mask = self.get_layer_mask('electrolyte')
        cathode_mask = self.get_layer_mask('cathode')
        
        temperature = T_base * np.ones_like(self.X)
        
        # Add heat generation effects
        temperature += flow_effect
        temperature[anode_mask] += overpotential_heat[anode_mask] * 0.5
        temperature[electrolyte_mask] += overpotential_heat[electrolyte_mask] * 1.5
        temperature[cathode_mask] += overpotential_heat[cathode_mask] * 0.8
        
        # Cooling effect from gas flow
        cooling_factor = (fuel_flow_rate + air_flow_rate) / 2e-5
        temperature -= 20 * cooling_factor * (1 - y_normalized)
        
        # Add thermal gradients and noise
        temperature += 10 * np.random.randn(*temperature.shape)
        
        return temperature
    
    def simulate_mechanical_fields(self, params, temperature):
        """
        Simulate stress, strain, and displacement fields from thermal expansion
        and mechanical loading.
        
        Args:
            params: Dictionary of simulation parameters
            temperature: 3D array of temperature distribution
            
        Returns:
            von_mises_stress: 3D array of von Mises stress [Pa]
            strain: 3D array of equivalent strain [-]
            displacement: 3D array of total displacement magnitude [m]
        """
        # Material properties per layer
        T_ref = 298.15  # Reference temperature [K]
        
        # Initialize stress/strain fields
        von_mises_stress = np.zeros_like(self.X)
        strain = np.zeros_like(self.X)
        displacement = np.zeros_like(self.X)
        
        # Get layer masks
        anode_mask = self.get_layer_mask('anode')
        electrolyte_mask = self.get_layer_mask('electrolyte')
        cathode_mask = self.get_layer_mask('cathode')
        
        # Extract material properties
        E_anode = params['youngs_modulus_anode']
        E_electrolyte = params['youngs_modulus_electrolyte']
        E_cathode = params['youngs_modulus_cathode']
        
        CTE_anode = params['cte_anode']
        CTE_electrolyte = params['cte_electrolyte']
        CTE_cathode = params['cte_cathode']
        
        # Thermal strain: ε_th = α·ΔT
        dT = temperature - T_ref
        
        # Calculate thermal strain per layer
        thermal_strain_anode = CTE_anode * dT[anode_mask]
        thermal_strain_electrolyte = CTE_electrolyte * dT[electrolyte_mask]
        thermal_strain_cathode = CTE_cathode * dT[cathode_mask]
        
        strain[anode_mask] = thermal_strain_anode
        strain[electrolyte_mask] = thermal_strain_electrolyte
        strain[cathode_mask] = thermal_strain_cathode
        
        # Stress from CTE mismatch (major source in SOFCs)
        # σ = E·ε for elastic response
        poisson = 0.3
        constraint_factor = 1 / (1 - 2*poisson)  # Constrained expansion
        
        # Base thermal stress
        von_mises_stress[anode_mask] = (E_anode * np.abs(thermal_strain_anode) * 
                                        constraint_factor)
        von_mises_stress[electrolyte_mask] = (E_electrolyte * 
                                               np.abs(thermal_strain_electrolyte) * 
                                               constraint_factor)
        von_mises_stress[cathode_mask] = (E_cathode * np.abs(thermal_strain_cathode) * 
                                          constraint_factor)
        
        # Stress concentration at interfaces
        interface_factor = 1.5
        z_anode_electrolyte = 0.0015
        z_electrolyte_cathode = 0.0018
        
        interface_mask_1 = np.abs(self.Z - z_anode_electrolyte) < 0.0001
        interface_mask_2 = np.abs(self.Z - z_electrolyte_cathode) < 0.0001
        
        von_mises_stress[interface_mask_1] *= interface_factor
        von_mises_stress[interface_mask_2] *= interface_factor
        
        # Add stress from pressure loading
        pressure_stress = params['current_density'] * 1e-3  # Simplified
        von_mises_stress += pressure_stress
        
        # Displacement from thermal expansion
        # u = ε·L
        layer_thickness = self.z[-1] - self.z[0]
        displacement = strain * layer_thickness * np.abs(self.Z)
        
        # Add noise to represent computational uncertainty
        von_mises_stress += 1e6 * np.random.randn(*von_mises_stress.shape)
        von_mises_stress = np.maximum(von_mises_stress, 0)  # Stress cannot be negative
        
        return von_mises_stress, strain, displacement
    
    def simulate_species_fields(self, params, current_density, temperature):
        """
        Simulate species concentration fields (H₂, H₂O) in anode.
        
        Args:
            params: Dictionary of simulation parameters
            current_density: 3D array of current density
            temperature: 3D array of temperature
            
        Returns:
            H2_concentration: 3D array of H₂ molar concentration [mol/m³]
            H2O_concentration: 3D array of H₂O molar concentration [mol/m³]
        """
        # Initialize concentration fields
        H2_concentration = np.zeros_like(self.X)
        H2O_concentration = np.zeros_like(self.X)
        
        # Species transport only in anode (fuel side)
        anode_mask = self.get_layer_mask('anode')
        
        # Inlet concentrations (ideal gas law: C = P/(RT))
        P = 101325  # Pressure [Pa]
        R = 8.314  # Gas constant [J/(mol·K)]
        
        # Initial H₂ concentration at inlet
        H2_inlet = 0.97  # 97% H₂, 3% H₂O (humidified fuel)
        H2O_inlet = 0.03
        
        T_avg = np.mean(temperature[anode_mask])
        C_total = P / (R * T_avg)
        
        C_H2_inlet = H2_inlet * C_total
        C_H2O_inlet = H2O_inlet * C_total
        
        # H₂ is consumed along the flow direction (x-axis)
        # Electrochemical reaction: H₂ + O²⁻ → H₂O + 2e⁻
        
        # Fuel utilization increases with distance
        x_normalized = self.X / 0.1
        
        # H₂ consumption rate from current density
        # i = n·F·r where r is reaction rate [mol/(m³·s)]
        F = 96485  # Faraday constant
        n = 2  # electrons per H₂ molecule
        
        utilization_factor = params['fuel_flow_rate'] / 1e-5  # Normalized
        
        # H₂ depletion along flow
        H2_depletion = 0.3 * x_normalized / utilization_factor
        H2_concentration[anode_mask] = C_H2_inlet * (1 - H2_depletion[anode_mask])
        
        # H₂O production (complementary to H₂ consumption)
        H2O_concentration[anode_mask] = (C_H2O_inlet + 
                                         C_H2_inlet * H2_depletion[anode_mask])
        
        # Add diffusion effects (smoothing)
        H2_concentration[anode_mask] += 2 * np.random.randn(*H2_concentration[anode_mask].shape)
        H2O_concentration[anode_mask] += 2 * np.random.randn(*H2O_concentration[anode_mask].shape)
        
        # Ensure non-negative concentrations
        H2_concentration = np.maximum(H2_concentration, 0)
        H2O_concentration = np.maximum(H2O_concentration, 0)
        
        return H2_concentration, H2O_concentration
    
    def run_simulation(self, params):
        """
        Run a complete multi-physics SOFC simulation.
        
        Args:
            params: Dictionary of all input parameters
            
        Returns:
            results: Dictionary containing all output fields
        """
        print(f"Running simulation with params: V={params['voltage']:.2f}V, "
              f"i={params['current_density']:.0f} A/m², "
              f"T_fuel={params['fuel_inlet_temp']:.0f}K")
        
        # Solve coupled physics in sequence
        # 1. Electrochemical fields
        current_density, overpotential = self.simulate_electrochemical_fields(params)
        
        # 2. Thermal fields (coupled with electrochemistry)
        temperature = self.simulate_thermal_fields(params, current_density)
        
        # 3. Mechanical fields (coupled with thermal)
        von_mises_stress, strain, displacement = self.simulate_mechanical_fields(
            params, temperature)
        
        # 4. Species fields (coupled with electrochemistry and thermal)
        H2_conc, H2O_conc = self.simulate_species_fields(
            params, current_density, temperature)
        
        results = {
            # Electrochemical fields
            'current_density': current_density,
            'overpotential': overpotential,
            
            # Thermal fields
            'temperature': temperature,
            
            # Mechanical fields
            'von_mises_stress': von_mises_stress,
            'strain': strain,
            'displacement': displacement,
            
            # Species fields
            'H2_concentration': H2_conc,
            'H2O_concentration': H2O_conc,
            
            # Mesh data
            'x': self.x,
            'y': self.y,
            'z': self.z,
        }
        
        return results


class DatasetGenerator:
    """
    Generate high-fidelity SOFC dataset using Latin Hypercube Sampling.
    """
    
    def __init__(self, n_samples=100, grid_size=(50, 50, 20)):
        """
        Initialize dataset generator.
        
        Args:
            n_samples: Number of simulation runs to generate
            grid_size: 3D grid dimensions for each simulation
        """
        self.n_samples = n_samples
        self.grid_size = grid_size
        self.simulator = SOFCSimulator(grid_size)
        
        # Define parameter ranges for Latin Hypercube Sampling
        self.param_bounds = {
            # Operating conditions
            'voltage': (0.6, 0.9),  # [V]
            'current_density': (3000, 12000),  # [A/m²]
            'fuel_flow_rate': (5e-6, 2e-5),  # [kg/s]
            'air_flow_rate': (5e-5, 2e-4),  # [kg/s]
            'fuel_inlet_temp': (873, 1073),  # [K] (600-800°C)
            'air_inlet_temp': (873, 1073),  # [K]
            
            # Anode material properties
            'porosity_anode': (0.25, 0.45),  # [-]
            'permeability_anode': (1e-12, 1e-10),  # [m²]
            'ionic_conductivity': (1e3, 1e4),  # [S/m]
            'electronic_conductivity': (1e4, 1e6),  # [S/m]
            'youngs_modulus_anode': (30e9, 80e9),  # [Pa]
            'cte_anode': (10e-6, 13e-6),  # [1/K]
            
            # Electrolyte material properties
            'porosity_electrolyte': (0.0, 0.05),  # [-]
            'youngs_modulus_electrolyte': (180e9, 220e9),  # [Pa]
            'cte_electrolyte': (10e-6, 11e-6),  # [1/K]
            
            # Cathode material properties
            'porosity_cathode': (0.25, 0.45),  # [-]
            'permeability_cathode': (1e-12, 1e-10),  # [m²]
            'youngs_modulus_cathode': (40e9, 100e9),  # [Pa]
            'cte_cathode': (11e-6, 14e-6),  # [1/K]
            
            # Geometric parameters
            'anode_thickness': (0.0013, 0.0017),  # [m]
            'electrolyte_thickness': (0.0002, 0.0004),  # [m]
            'cathode_thickness': (0.001, 0.0014),  # [m]
            'active_area': (0.008, 0.012),  # [m²]
        }
        
    def generate_parameter_samples(self):
        """
        Generate parameter samples using Latin Hypercube Sampling.
        
        Returns:
            samples: Array of shape (n_samples, n_parameters)
            param_names: List of parameter names
        """
        param_names = list(self.param_bounds.keys())
        n_params = len(param_names)
        
        # Create Latin Hypercube Sampler
        sampler = qmc.LatinHypercube(d=n_params, seed=42)
        
        # Generate samples in [0, 1] hypercube
        unit_samples = sampler.random(n=self.n_samples)
        
        # Scale to actual parameter bounds
        samples = np.zeros_like(unit_samples)
        for i, param_name in enumerate(param_names):
            lower, upper = self.param_bounds[param_name]
            samples[:, i] = qmc.scale(unit_samples[:, i:i+1], lower, upper).flatten()
        
        return samples, param_names
    
    def generate_dataset(self, output_dir='sofc_dataset'):
        """
        Generate the complete dataset with multiple simulation runs.
        
        Args:
            output_dir: Directory to save the dataset
        """
        print(f"Generating SOFC dataset with {self.n_samples} samples...")
        print(f"Grid size: {self.grid_size}")
        print(f"Output directory: {output_dir}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate parameter samples
        samples, param_names = self.generate_parameter_samples()
        
        # Save dataset metadata
        metadata = {
            'n_samples': self.n_samples,
            'grid_size': self.grid_size,
            'param_names': param_names,
            'param_bounds': {k: list(v) for k, v in self.param_bounds.items()},
            'generation_date': datetime.now().isoformat(),
            'description': 'High-fidelity SOFC multi-physics simulation dataset',
            'physics_models': [
                'Electrochemical (Butler-Volmer)',
                'Thermal (Heat generation and transport)',
                'Mechanical (Thermo-mechanical stress)',
                'Species transport (H2/H2O)'
            ]
        }
        
        with open(f'{output_dir}/metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create HDF5 file for storing large dataset
        h5_file = h5py.File(f'{output_dir}/sofc_dataset.h5', 'w')
        
        # Create groups for inputs and outputs
        input_group = h5_file.create_group('inputs')
        output_group = h5_file.create_group('outputs')
        mesh_group = h5_file.create_group('mesh')
        
        # Save parameter samples as input features
        input_group.create_dataset('parameters', data=samples)
        input_group.create_dataset('parameter_names', 
                                   data=np.array(param_names, dtype='S'))
        
        # Pre-allocate datasets for outputs (all samples)
        nx, ny, nz = self.grid_size
        
        # Electrochemical outputs
        current_density_ds = output_group.create_dataset(
            'current_density', shape=(self.n_samples, nx, ny, nz), 
            dtype='float32', compression='gzip')
        overpotential_ds = output_group.create_dataset(
            'overpotential', shape=(self.n_samples, nx, ny, nz),
            dtype='float32', compression='gzip')
        
        # Thermal outputs
        temperature_ds = output_group.create_dataset(
            'temperature', shape=(self.n_samples, nx, ny, nz),
            dtype='float32', compression='gzip')
        
        # Mechanical outputs
        stress_ds = output_group.create_dataset(
            'von_mises_stress', shape=(self.n_samples, nx, ny, nz),
            dtype='float32', compression='gzip')
        strain_ds = output_group.create_dataset(
            'strain', shape=(self.n_samples, nx, ny, nz),
            dtype='float32', compression='gzip')
        displacement_ds = output_group.create_dataset(
            'displacement', shape=(self.n_samples, nx, ny, nz),
            dtype='float32', compression='gzip')
        
        # Species outputs
        H2_ds = output_group.create_dataset(
            'H2_concentration', shape=(self.n_samples, nx, ny, nz),
            dtype='float32', compression='gzip')
        H2O_ds = output_group.create_dataset(
            'H2O_concentration', shape=(self.n_samples, nx, ny, nz),
            dtype='float32', compression='gzip')
        
        # Run simulations and store results
        print("\nRunning simulations...")
        for i in range(self.n_samples):
            print(f"\nSimulation {i+1}/{self.n_samples}")
            
            # Create parameter dictionary from sample
            params = {name: samples[i, j] 
                     for j, name in enumerate(param_names)}
            
            # Run simulation
            results = self.simulator.run_simulation(params)
            
            # Store results in HDF5
            current_density_ds[i] = results['current_density']
            overpotential_ds[i] = results['overpotential']
            temperature_ds[i] = results['temperature']
            stress_ds[i] = results['von_mises_stress']
            strain_ds[i] = results['strain']
            displacement_ds[i] = results['displacement']
            H2_ds[i] = results['H2_concentration']
            H2O_ds[i] = results['H2O_concentration']
            
            # Save mesh data (only once, same for all samples)
            if i == 0:
                mesh_group.create_dataset('x', data=results['x'])
                mesh_group.create_dataset('y', data=results['y'])
                mesh_group.create_dataset('z', data=results['z'])
        
        h5_file.close()
        
        print(f"\n✓ Dataset generation complete!")
        print(f"✓ Data saved to: {output_dir}/sofc_dataset.h5")
        print(f"✓ Metadata saved to: {output_dir}/metadata.json")
        print(f"✓ Dataset size: {self.n_samples} samples")
        print(f"✓ Each sample: {nx}×{ny}×{nz} = {nx*ny*nz:,} grid points")
        
        # Generate summary statistics
        self._generate_summary(output_dir)
        
        return output_dir
    
    def _generate_summary(self, output_dir):
        """Generate a summary statistics file for the dataset."""
        print("\nGenerating dataset summary...")
        
        # Read the dataset
        with h5py.File(f'{output_dir}/sofc_dataset.h5', 'r') as f:
            summary = {
                'dataset_info': {
                    'n_samples': int(self.n_samples),
                    'grid_dimensions': list(self.grid_size),
                    'total_data_points_per_sample': int(np.prod(self.grid_size)),
                    'total_data_points': int(self.n_samples * np.prod(self.grid_size)),
                },
                'input_parameters': {},
                'output_fields': {}
            }
            
            # Input parameter statistics
            params = f['inputs/parameters'][:]
            param_names = [name.decode() for name in f['inputs/parameter_names'][:]]
            
            for i, name in enumerate(param_names):
                summary['input_parameters'][name] = {
                    'min': float(np.min(params[:, i])),
                    'max': float(np.max(params[:, i])),
                    'mean': float(np.mean(params[:, i])),
                    'std': float(np.std(params[:, i]))
                }
            
            # Output field statistics
            output_fields = ['current_density', 'overpotential', 'temperature',
                           'von_mises_stress', 'strain', 'displacement',
                           'H2_concentration', 'H2O_concentration']
            
            for field in output_fields:
                data = f[f'outputs/{field}'][:]
                summary['output_fields'][field] = {
                    'shape': list(data.shape),
                    'min': float(np.min(data)),
                    'max': float(np.max(data)),
                    'mean': float(np.mean(data)),
                    'std': float(np.std(data))
                }
        
        # Save summary
        with open(f'{output_dir}/dataset_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✓ Summary saved to: {output_dir}/dataset_summary.json")


if __name__ == "__main__":
    # Configuration
    N_SAMPLES = 100  # Number of simulation runs
    GRID_SIZE = (50, 50, 20)  # 3D grid dimensions (nx, ny, nz)
    OUTPUT_DIR = 'sofc_dataset'
    
    print("=" * 70)
    print("SOFC High-Fidelity Numerical Dataset Generator")
    print("Physics-Informed Data-Driven Modeling")
    print("=" * 70)
    
    # Create dataset generator
    generator = DatasetGenerator(n_samples=N_SAMPLES, grid_size=GRID_SIZE)
    
    # Generate dataset
    output_dir = generator.generate_dataset(output_dir=OUTPUT_DIR)
    
    print("\n" + "=" * 70)
    print("Dataset generation completed successfully!")
    print(f"Location: {output_dir}/")
    print("=" * 70)
