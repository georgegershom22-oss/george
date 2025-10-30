"""
SOFC Multi-Physics Simulator
Generates high-fidelity numerical data for SOFC thermo-mechanics
"""

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve
from typing import Dict, Tuple, Optional
import h5py
import os


class SOFCSimulator:
    """
    SOFC Multi-Physics Simulator
    Solves coupled electro-thermal-mechanical-species transport equations
    """
    
    def __init__(self, nx: int = 50, ny: int = 50, nz: int = 30):
        """
        Initialize SOFC simulator with 3D grid
        
        Args:
            nx, ny, nz: Grid resolution in x, y, z directions
        """
        self.nx, self.ny, self.nz = nx, ny, nz
        self.dx = 1e-3  # 1mm cell size
        self.dy = 1e-3
        self.dz = 1e-3
        
        # Layer structure: [anode, electrolyte, cathode, interconnect]
        self.layer_thicknesses = None
        self.layer_indices = None
        
    def setup_geometry(self, params: Dict):
        """
        Setup SOFC layer geometry based on parameters
        
        Args:
            params: Dictionary containing geometric parameters
        """
        # Layer thicknesses (in meters)
        t_anode = params.get('thickness_anode', 500e-6)
        t_electrolyte = params.get('thickness_electrolyte', 10e-6)
        t_cathode = params.get('thickness_cathode', 50e-6)
        t_interconnect = params.get('thickness_interconnect', 100e-6)
        
        self.layer_thicknesses = {
            'anode': t_anode,
            'electrolyte': t_electrolyte,
            'cathode': t_cathode,
            'interconnect': t_interconnect
        }
        
        # Determine layer boundaries in z-direction
        z_total = t_anode + t_electrolyte + t_cathode + 2 * t_interconnect
        self.dz = z_total / self.nz
        
        # Calculate layer indices
        z_anode_end = int(t_anode / self.dz)
        z_electrolyte_end = int((t_anode + t_electrolyte) / self.dz)
        z_cathode_end = int((t_anode + t_electrolyte + t_cathode) / self.dz)
        z_interconnect_end = int((t_anode + t_electrolyte + t_cathode + t_interconnect) / self.dz)
        
        self.layer_indices = {
            'interconnect_bottom': (0, z_interconnect_end),
            'anode': (z_interconnect_end, z_anode_end),
            'electrolyte': (z_anode_end, z_electrolyte_end),
            'cathode': (z_electrolyte_end, z_cathode_end),
            'interconnect_top': (z_cathode_end, self.nz)
        }
        
    def get_material_properties(self, params: Dict, layer: str) -> Dict:
        """
        Get material properties for a specific layer
        
        Args:
            params: Parameters dictionary
            layer: Layer name ('anode', 'cathode', 'electrolyte', 'interconnect')
        """
        prefix = f"{layer}_"
        props = {
            'porosity': params.get(f'{prefix}porosity', 0.3),
            'permeability': params.get(f'{prefix}permeability', 1e-12),
            'ionic_conductivity': params.get(f'{prefix}ionic_conductivity', 10.0),
            'electronic_conductivity': params.get(f'{prefix}electronic_conductivity', 1000.0),
            'youngs_modulus': params.get(f'{prefix}youngs_modulus', 100e9),
            'cte': params.get(f'{prefix}cte', 12e-6),
            'poisson_ratio': params.get(f'{prefix}poisson_ratio', 0.3),
            'thermal_conductivity': params.get(f'{prefix}thermal_conductivity', 2.0),
            'specific_heat': params.get(f'{prefix}specific_heat', 500.0),
            'density': params.get(f'{prefix}density', 6000.0),
        }
        
        # Layer-specific defaults
        if layer == 'electrolyte':
            props['porosity'] = 0.0
            props['electronic_conductivity'] = 0.0
        elif layer == 'interconnect':
            props['ionic_conductivity'] = 0.0
            props['porosity'] = 0.0
            
        return props
    
    def solve_electrochemistry(self, params: Dict, T_field: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Solve electrochemical equations for current density and overpotential
        
        Args:
            params: Parameters dictionary
            T_field: Temperature field [K]
            
        Returns:
            current_density: 3D current density field [A/m²]
            overpotential: 3D overpotential field [V]
        """
        voltage = params.get('voltage', 0.7)  # Cell voltage [V]
        E_rev = params.get('reversible_voltage', 1.1)  # Reversible voltage [V]
        
        # Initialize fields
        current_density = np.zeros((self.nx, self.ny, self.nz))
        overpotential = np.zeros((self.nx, self.ny, self.nz))
        
        # Calculate average temperature for kinetics
        T_avg = np.mean(T_field)
        
        # Butler-Volmer kinetics parameters
        i0_anode = params.get('exchange_current_anode', 1000.0)  # A/m²
        i0_cathode = params.get('exchange_current_cathode', 500.0)  # A/m²
        alpha_anode = params.get('transfer_coefficient_anode', 0.5)
        alpha_cathode = params.get('transfer_coefficient_cathode', 0.5)
        
        # Activation energy for temperature dependence
        Ea_anode = params.get('activation_energy_anode', 120e3)  # J/mol
        Ea_cathode = params.get('activation_energy_cathode', 140e3)  # J/mol
        R_gas = 8.314  # J/(mol·K)
        T_ref = 1073.0  # Reference temperature [K]
        
        # Temperature correction
        temp_factor_anode = np.exp(-Ea_anode / R_gas * (1.0 / T_avg - 1.0 / T_ref))
        temp_factor_cathode = np.exp(-Ea_cathode / R_gas * (1.0 / T_avg - 1.0 / T_ref))
        
        i0_anode_eff = i0_anode * temp_factor_anode
        i0_cathode_eff = i0_cathode * temp_factor_cathode
        
        # Total overpotential (voltage loss)
        eta_total = E_rev - voltage
        
        # Distribute overpotential across layers
        for i in range(self.nx):
            for j in range(self.ny):
                for k in range(self.nz):
                    z_frac = k / self.nz
                    
                    # Determine layer
                    if self.layer_indices['anode'][0] <= k < self.layer_indices['anode'][1]:
                        layer = 'anode'
                        eta_local = eta_total * 0.3 * (1.0 + 0.5 * np.sin(np.pi * z_frac))
                        i0 = i0_anode_eff
                        alpha = alpha_anode
                    elif self.layer_indices['cathode'][0] <= k < self.layer_indices['cathode'][1]:
                        layer = 'cathode'
                        eta_local = eta_total * 0.4 * (1.0 + 0.5 * np.cos(np.pi * z_frac))
                        i0 = i0_cathode_eff
                        alpha = alpha_cathode
                    elif self.layer_indices['electrolyte'][0] <= k < self.layer_indices['electrolyte'][1]:
                        layer = 'electrolyte'
                        eta_local = eta_total * 0.3
                        i0 = (i0_anode_eff + i0_cathode_eff) / 2.0
                        alpha = (alpha_anode + alpha_cathode) / 2.0
                    else:
                        eta_local = 0.0
                        i0 = 0.0
                        alpha = 0.5
                    
                    # Butler-Volmer equation
                    if i0 > 0 and eta_local > 0:
                        current_density[i, j, k] = i0 * (
                            np.exp(alpha * 2 * 96485 * eta_local / (R_gas * T_field[i, j, k])) -
                            np.exp(-(1 - alpha) * 2 * 96485 * eta_local / (R_gas * T_field[i, j, k]))
                        )
                    
                    overpotential[i, j, k] = eta_local
        
        # Add spatial variation
        x_coords = np.linspace(0, 1, self.nx)
        y_coords = np.linspace(0, 1, self.ny)
        X, Y = np.meshgrid(x_coords, y_coords, indexing='ij')
        
        # Spatial current density variation (higher near inlet)
        spatial_factor = 1.0 + 0.2 * (1.0 - X) * (1.0 - Y)
        current_density *= spatial_factor[..., np.newaxis]
        
        return current_density, overpotential
    
    def solve_thermal(self, params: Dict, current_density: np.ndarray) -> np.ndarray:
        """
        Solve thermal transport equation
        
        Args:
            params: Parameters dictionary
            current_density: Current density field [A/m²]
            
        Returns:
            T_field: Temperature field [K]
        """
        # Boundary conditions
        T_inlet_fuel = params.get('T_inlet_fuel', 1073.0)  # K
        T_inlet_air = params.get('T_inlet_air', 1073.0)  # K
        
        # Initial guess
        T_field = np.ones((self.nx, self.ny, self.nz)) * (T_inlet_fuel + T_inlet_air) / 2.0
        
        # Thermal properties (spatially varying)
        k_thermal = np.zeros((self.nx, self.ny, self.nz))
        rho_cp = np.zeros((self.nx, self.ny, self.nz))
        
        for layer_name, (z_start, z_end) in self.layer_indices.items():
            layer = layer_name.replace('_bottom', '').replace('_top', '')
            if layer == 'interconnect':
                layer = 'interconnect'
            
            props = self.get_material_properties(params, layer)
            k_thermal[:, :, z_start:z_end] = props['thermal_conductivity']
            rho_cp[:, :, z_start:z_end] = props['density'] * props['specific_heat']
        
        # Convective flow
        v_fuel = params.get('flow_rate_fuel', 1e-3)  # m/s
        v_air = params.get('flow_rate_air', 2e-3)  # m/s
        
        # Heat generation from electrochemical reactions
        # Joule heating + reaction heat
        V_cell = params.get('voltage', 0.7)
        E_rev = params.get('reversible_voltage', 1.1)
        heat_gen = current_density * (E_rev - V_cell)  # W/m³
        
        # Solve heat equation iteratively
        dt = 0.01
        alpha = k_thermal / rho_cp
        
        for iteration in range(100):
            T_new = T_field.copy()
            
            for i in range(1, self.nx - 1):
                for j in range(1, self.ny - 1):
                    for k in range(1, self.nz - 1):
                        # Conduction
                        d2T_dx2 = (T_field[i+1, j, k] - 2*T_field[i, j, k] + T_field[i-1, j, k]) / self.dx**2
                        d2T_dy2 = (T_field[i, j+1, k] - 2*T_field[i, j, k] + T_field[i, j-1, k]) / self.dy**2
                        d2T_dz2 = (T_field[i, j, k+1] - 2*T_field[i, j, k] + T_field[i, j, k-1]) / self.dz**2
                        
                        conduction = alpha[i, j, k] * (d2T_dx2 + d2T_dy2 + d2T_dz2)
                        
                        # Convection (simplified - fuel side bottom, air side top)
                        if k < self.nz // 2:
                            convection = -v_fuel * (T_field[i, j, k] - T_field[i, j, max(0, k-1)]) / self.dz
                        else:
                            convection = -v_air * (T_field[i, j, k] - T_field[i, j, min(self.nz-1, k+1)]) / self.dz
                        
                        # Heat generation
                        generation = heat_gen[i, j, k] / rho_cp[i, j, k]
                        
                        T_new[i, j, k] = T_field[i, j, k] + dt * (conduction + generation + convection)
            
            # Boundary conditions
            T_new[:, :, 0] = T_inlet_fuel  # Fuel inlet
            T_new[:, :, -1] = T_inlet_air  # Air inlet
            T_new[0, :, :] = T_new[1, :, :]  # Insulated sides
            T_new[-1, :, :] = T_new[-2, :, :]
            T_new[:, 0, :] = T_new[:, 1, :]
            T_new[:, -1, :] = T_new[:, -2, :]
            
            if np.max(np.abs(T_new - T_field)) < 1e-3:
                break
                
            T_field = T_new
        
        return T_field
    
    def solve_mechanics(self, params: Dict, T_field: np.ndarray, T_ref: float = 1073.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Solve mechanical stress/strain equations
        
        Args:
            params: Parameters dictionary
            T_field: Temperature field [K]
            T_ref: Reference temperature for thermal expansion [K]
            
        Returns:
            von_mises_stress: Von Mises stress field [Pa]
            strain: Strain tensor (6 components: xx, yy, zz, xy, xz, yz) [dimensionless]
            displacement: Displacement field (u, v, w) [m]
        """
        # Initialize fields
        von_mises_stress = np.zeros((self.nx, self.ny, self.nz))
        strain = np.zeros((self.nx, self.ny, self.nz, 6))  # xx, yy, zz, xy, xz, yz
        displacement = np.zeros((self.nx, self.ny, self.nz, 3))  # u, v, w
        
        # Thermal strain
        thermal_strain = np.zeros((self.nx, self.ny, self.nz, 3))
        
        for k in range(self.nz):
            # Determine layer
            layer = None
            for layer_name, (z_start, z_end) in self.layer_indices.items():
                if z_start <= k < z_end:
                    layer = layer_name.replace('_bottom', '').replace('_top', '')
                    if layer == 'interconnect':
                        layer = 'interconnect'
                    break
            
            if layer:
                props = self.get_material_properties(params, layer)
                cte = props['cte']
                E = props['youngs_modulus']
                nu = props['poisson_ratio']
                
                # Thermal strain
                delta_T = T_field[:, :, k] - T_ref
                thermal_strain[:, :, k, :] = cte * delta_T[..., np.newaxis]
                
                # Mechanical stress (plane stress assumption for simplicity)
                for i in range(self.nx):
                    for j in range(self.ny):
                        # Principal strains
                        eps_xx = thermal_strain[i, j, k, 0]
                        eps_yy = thermal_strain[i, j, k, 1]
                        eps_zz = thermal_strain[i, j, k, 2]
                        
                        # Stress from Hooke's law (isotropic)
                        # sigma = E / (1 - nu^2) * [eps_xx + nu*eps_yy, nu*eps_xx + eps_yy]
                        sigma_xx = E / (1 - nu**2) * (eps_xx + nu * eps_yy)
                        sigma_yy = E / (1 - nu**2) * (nu * eps_xx + eps_yy)
                        sigma_zz = E * (eps_zz + nu * (eps_xx + eps_yy)) / (1 - 2*nu) if abs(nu) < 0.49 else 0.0
                        sigma_xy = 0.0  # Simplified
                        sigma_xz = 0.0
                        sigma_yz = 0.0
                        
                        # Von Mises stress
                        von_mises_stress[i, j, k] = np.sqrt(
                            0.5 * ((sigma_xx - sigma_yy)**2 + 
                                   (sigma_yy - sigma_zz)**2 + 
                                   (sigma_zz - sigma_xx)**2 + 
                                   6 * (sigma_xy**2 + sigma_xz**2 + sigma_yz**2))
                        )
                        
                        # Store strain tensor (shear strains are zero for this simplified model)
                        eps_xy = 0.0
                        eps_xz = 0.0
                        eps_yz = 0.0
                        strain[i, j, k, :] = [eps_xx, eps_yy, eps_zz, eps_xy, eps_xz, eps_yz]
                        
                        # Displacement (integrated from strain with finite differences)
                        # Start from origin (fixed boundary condition)
                        if i == 0 and j == 0 and k == 0:
                            displacement[i, j, k, :] = 0.0
                        else:
                            if i > 0:
                                displacement[i, j, k, 0] = displacement[i-1, j, k, 0] + eps_xx * self.dx
                            if j > 0:
                                displacement[i, j, k, 1] = displacement[i, j-1, k, 1] + eps_yy * self.dy
                            if k > 0:
                                displacement[i, j, k, 2] = displacement[i, j, k-1, 2] + eps_zz * self.dz
                        
                        # Ensure finite values
                        displacement[i, j, k, :] = np.nan_to_num(displacement[i, j, k, :], 
                                                                  nan=0.0, posinf=1e6, neginf=-1e6)
        
        return von_mises_stress, strain, displacement
    
    def solve_species_transport(self, params: Dict, T_field: np.ndarray, current_density: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Solve species transport for H2 and H2O
        
        Args:
            params: Parameters dictionary
            T_field: Temperature field [K]
            current_density: Current density field [A/m²]
            
        Returns:
            c_H2: H2 concentration field [mol/m³]
            c_H2O: H2O concentration field [mol/m³]
        """
        # Inlet concentrations
        c_H2_inlet = params.get('c_H2_inlet', 40.0)  # mol/m³ (97% H2, 3% H2O)
        c_H2O_inlet = params.get('c_H2O_inlet', 1.2)  # mol/m³
        
        # Initialize fields
        c_H2 = np.ones((self.nx, self.ny, self.nz)) * c_H2_inlet
        c_H2O = np.ones((self.nx, self.ny, self.nz)) * c_H2O_inlet
        
        # Flow velocity
        v_fuel = params.get('flow_rate_fuel', 1e-3)  # m/s
        
        # Diffusion coefficients (temperature dependent)
        D_H2_ref = 1e-4  # m²/s at reference temperature
        D_H2O_ref = 8e-5  # m²/s
        T_ref = 1073.0
        Ea_diff = 20e3  # J/mol
        R_gas = 8.314
        
        # Consumption rate (from electrochemical reaction)
        # H2 + O2- -> H2O + 2e- : 1 mol H2 per 2 F coulombs
        F_faraday = 96485.0  # C/mol
        
        # Solve transport equation
        dt = 0.001
        for iteration in range(50):
            c_H2_new = c_H2.copy()
            c_H2O_new = c_H2O.copy()
            
            for i in range(1, self.nx - 1):
                for j in range(1, self.ny - 1):
                    for k in range(1, self.nz - 1):
                        # Only in anode layer
                        if not (self.layer_indices['anode'][0] <= k < self.layer_indices['anode'][1]):
                            continue
                        
                        T = T_field[i, j, k]
                        D_H2 = D_H2_ref * np.exp(-Ea_diff / R_gas * (1.0 / T - 1.0 / T_ref))
                        D_H2O = D_H2O_ref * np.exp(-Ea_diff / R_gas * (1.0 / T - 1.0 / T_ref))
                        
                        # Diffusion
                        d2c_dx2_H2 = (c_H2[i+1, j, k] - 2*c_H2[i, j, k] + c_H2[i-1, j, k]) / self.dx**2
                        d2c_dy2_H2 = (c_H2[i, j+1, k] - 2*c_H2[i, j, k] + c_H2[i, j-1, k]) / self.dy**2
                        d2c_dz2_H2 = (c_H2[i, j, k+1] - 2*c_H2[i, j, k] + c_H2[i, j, k-1]) / self.dz**2
                        
                        d2c_dx2_H2O = (c_H2O[i+1, j, k] - 2*c_H2O[i, j, k] + c_H2O[i-1, j, k]) / self.dx**2
                        d2c_dy2_H2O = (c_H2O[i, j+1, k] - 2*c_H2O[i, j, k] + c_H2O[i, j-1, k]) / self.dy**2
                        d2c_dz2_H2O = (c_H2O[i, j, k+1] - 2*c_H2O[i, j, k] + c_H2O[i, j, k-1]) / self.dz**2
                        
                        # Convection
                        convection_H2 = -v_fuel * (c_H2[i, j, k] - c_H2[i, j, max(0, k-1)]) / self.dz
                        convection_H2O = -v_fuel * (c_H2O[i, j, k] - c_H2O[i, j, max(0, k-1)]) / self.dz
                        
                        # Reaction consumption (from current density)
                        i_local = current_density[i, j, k]
                        consumption_H2 = -i_local / (2.0 * F_faraday)  # mol/(m²·s)
                        production_H2O = i_local / (2.0 * F_faraday)
                        
                        # Update concentrations
                        c_H2_new[i, j, k] = c_H2[i, j, k] + dt * (
                            D_H2 * (d2c_dx2_H2 + d2c_dy2_H2 + d2c_dz2_H2) + 
                            convection_H2 + 
                            consumption_H2 / self.dz
                        )
                        c_H2O_new[i, j, k] = c_H2O[i, j, k] + dt * (
                            D_H2O * (d2c_dx2_H2O + d2c_dy2_H2O + d2c_dz2_H2O) + 
                            convection_H2O + 
                            production_H2O / self.dz
                        )
                        
                        # Ensure non-negative
                        c_H2_new[i, j, k] = max(0.0, c_H2_new[i, j, k])
                        c_H2O_new[i, j, k] = max(0.0, c_H2O_new[i, j, k])
            
            # Boundary conditions
            c_H2_new[:, :, 0] = c_H2_inlet
            c_H2O_new[:, :, 0] = c_H2O_inlet
            
            if np.max(np.abs(c_H2_new - c_H2)) < 1e-6:
                break
                
            c_H2 = c_H2_new
            c_H2O = c_H2O_new
        
        return c_H2, c_H2O
    
    def simulate(self, params: Dict) -> Dict:
        """
        Run full multi-physics simulation
        
        Args:
            params: Complete parameter dictionary
            
        Returns:
            Dictionary containing all output fields
        """
        # Setup geometry
        self.setup_geometry(params)
        
        # Solve iteratively (electrochemistry and thermal are coupled)
        current_density = None
        T_field = None
        
        # Initial temperature guess
        T_field = np.ones((self.nx, self.ny, self.nz)) * (
            params.get('T_inlet_fuel', 1073.0) + params.get('T_inlet_air', 1073.0)
        ) / 2.0
        
        # Coupled iteration
        for iteration in range(10):
            # Solve electrochemistry
            current_density, overpotential = self.solve_electrochemistry(params, T_field)
            
            # Solve thermal (with updated current density)
            T_field_new = self.solve_thermal(params, current_density)
            
            if np.max(np.abs(T_field_new - T_field)) < 0.1:
                T_field = T_field_new
                break
            T_field = T_field_new
        
        # Solve mechanics (depends on temperature)
        von_mises_stress, strain, displacement = self.solve_mechanics(params, T_field)
        
        # Solve species transport (depends on current density and temperature)
        c_H2, c_H2O = self.solve_species_transport(params, T_field, current_density)
        
        # Collect results
        results = {
            'current_density': current_density,
            'overpotential': overpotential,
            'temperature': T_field,
            'von_mises_stress': von_mises_stress,
            'strain': strain,
            'displacement': displacement,
            'c_H2': c_H2,
            'c_H2O': c_H2O,
            'grid_shape': (self.nx, self.ny, self.nz),
            'layer_indices': self.layer_indices
        }
        
        return results