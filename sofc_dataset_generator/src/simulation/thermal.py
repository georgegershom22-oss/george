"""
Thermal simulation module for SOFC.
Solves heat transfer equations with electrochemical heat sources.
"""

import numpy as np
import dolfin as df
from typing import Dict, List, Tuple, Optional, Any
import yaml


class ThermalModel:
    """
    Solves thermal equations for SOFC using FEniCS.
    """
    
    def __init__(self, mesh_file: str, parameters: Dict[str, float], 
                 geometry_info: Dict[str, Any], electrochemical_data: Dict[str, Any] = None):
        """
        Initialize thermal model.
        
        Args:
            mesh_file: Path to mesh file
            parameters: Physical and operating parameters
            geometry_info: Geometry and domain information
            electrochemical_data: Results from electrochemical simulation
        """
        self.mesh_file = mesh_file
        self.params = parameters
        self.geometry_info = geometry_info
        self.electrochemical_data = electrochemical_data
        
        # Load mesh
        self.mesh = df.Mesh(mesh_file)
        
        # Physical constants
        self.F = 96485.0  # Faraday constant (C/mol)
        self.R = 8.314   # Gas constant (J/mol·K)
        
        # Domain markers
        self.domain_ids = geometry_info['domain_ids']
        self.boundary_ids = geometry_info['boundary_ids']
        
        # Initialize function spaces and functions
        self._setup_function_spaces()
        self._setup_material_properties()
        
    def _setup_function_spaces(self):
        """Set up function spaces for thermal variables."""
        
        # Function space for temperature (scalar)
        self.V_T = df.FunctionSpace(self.mesh, 'P', 1)
        
        # Function space for heat flux (vector)
        self.V_q = df.VectorFunctionSpace(self.mesh, 'P', 1)
        
        # Solution functions
        self.T = df.Function(self.V_T)  # Temperature
        self.T_n = df.Function(self.V_T)  # Previous time step temperature
        
        # Test function
        self.v_T = df.TestFunction(self.V_T)
        
        # Trial function
        self.dT = df.TrialFunction(self.V_T)
        
    def _setup_material_properties(self):
        """Set up thermal material property functions."""
        
        # Thermal conductivity function
        self.k_thermal = df.Function(df.FunctionSpace(self.mesh, 'DG', 0))
        
        # Density function
        self.rho = df.Function(df.FunctionSpace(self.mesh, 'DG', 0))
        
        # Specific heat function
        self.cp = df.Function(df.FunctionSpace(self.mesh, 'DG', 0))
        
        # Heat source function
        self.Q_source = df.Function(df.FunctionSpace(self.mesh, 'DG', 0))
        
        # Assign material properties based on domains
        self._assign_thermal_properties()
        
    def _assign_thermal_properties(self):
        """Assign thermal properties to different domains."""
        
        # Get thermal conductivities from parameters
        k_anode = self.params.get('anode_thermal_conductivity', 10.0)
        k_electrolyte = self.params.get('electrolyte_thermal_conductivity', 3.0)
        k_cathode = self.params.get('cathode_thermal_conductivity', 5.0)
        k_interconnect = self.params.get('interconnect_thermal_conductivity', 25.0)
        
        # Assign average thermal conductivity (simplified)
        k_avg = (k_anode + k_electrolyte + k_cathode + k_interconnect) / 4
        self.k_thermal.vector()[:] = k_avg
        
        # Material densities (kg/m³)
        rho_ceramic = 6000.0  # YSZ-based materials
        rho_metal = 8000.0    # Interconnect
        rho_avg = (rho_ceramic + rho_metal) / 2
        self.rho.vector()[:] = rho_avg
        
        # Specific heat capacities (J/kg·K)
        cp_ceramic = 500.0
        cp_metal = 600.0
        cp_avg = (cp_ceramic + cp_metal) / 2
        self.cp.vector()[:] = cp_avg
        
        # Initialize heat source (will be updated with electrochemical data)
        self.Q_source.vector()[:] = 0.0
        
    def _calculate_heat_sources(self):
        """Calculate heat sources from electrochemical reactions."""
        
        if self.electrochemical_data is None:
            return
        
        # Extract electrochemical data
        j = self.electrochemical_data.get('current_density')
        eta_a = self.electrochemical_data.get('overpotential_anode')
        eta_c = self.electrochemical_data.get('overpotential_cathode')
        
        if j is None or eta_a is None or eta_c is None:
            return
        
        # Heat generation from overpotentials (activation losses)
        # Q_act = j * (eta_a + eta_c)
        j_mag = df.sqrt(df.dot(j, j))
        Q_activation = j_mag * (df.abs(eta_a) + df.abs(eta_c))
        
        # Heat generation from ohmic losses
        # Q_ohm = j² / sigma_eff
        sigma_eff = (self.params.get('anode_electronic_conductivity', 1e5) + 
                    self.params.get('cathode_electronic_conductivity', 1e3)) / 2
        Q_ohmic = df.dot(j, j) / sigma_eff
        
        # Heat generation from reaction enthalpy
        # For H2 + 1/2 O2 -> H2O: ΔH = -286 kJ/mol
        # Q_reaction = j * ΔH / (n * F) where n = 2 electrons
        delta_H = -286000.0  # J/mol
        n_electrons = 2.0
        Q_reaction = j_mag * abs(delta_H) / (n_electrons * self.F)
        
        # Total heat source
        Q_total = Q_activation + Q_ohmic + Q_reaction
        
        # Project to function space
        self.Q_source = df.project(Q_total, df.FunctionSpace(self.mesh, 'DG', 0))
        
    def solve_steady_state_thermal(self) -> Dict[str, df.Function]:
        """
        Solve steady-state heat transfer equation.
        
        Returns:
            Dictionary containing thermal solution
        """
        
        # Calculate heat sources from electrochemistry
        self._calculate_heat_sources()
        
        # Define variational problem
        # Heat conduction: -div(k*grad(T)) = Q
        a = df.inner(self.k_thermal * df.grad(self.dT), df.grad(self.v_T)) * df.dx
        L = self.Q_source * self.v_T * df.dx
        
        # Apply boundary conditions
        bcs = self._apply_thermal_boundary_conditions()
        
        # Solve linear system
        df.solve(a == L, self.T, bcs)
        
        # Calculate heat flux
        q = self._calculate_heat_flux()
        
        solutions = {
            'temperature': self.T,
            'heat_flux': q
        }
        
        return solutions
        
    def solve_transient_thermal(self, dt: float, t_final: float) -> Dict[str, List[df.Function]]:
        """
        Solve transient heat transfer equation.
        
        Args:
            dt: Time step size
            t_final: Final simulation time
            
        Returns:
            Dictionary containing time series of thermal solutions
        """
        
        # Calculate heat sources
        self._calculate_heat_sources()
        
        # Time stepping parameters
        n_steps = int(t_final / dt)
        
        # Storage for solutions
        T_solutions = []
        q_solutions = []
        
        # Initial condition
        T_inlet = self.params.get('fuel_inlet_temp', 1073.0)
        self.T_n.interpolate(df.Constant(T_inlet))
        
        # Define variational problem for time stepping
        # rho*cp*dT/dt - div(k*grad(T)) = Q
        a = (self.rho * self.cp * self.dT * self.v_T * df.dx + 
             dt * df.inner(self.k_thermal * df.grad(self.dT), df.grad(self.v_T)) * df.dx)
        
        L = (self.rho * self.cp * self.T_n * self.v_T * df.dx + 
             dt * self.Q_source * self.v_T * df.dx)
        
        # Apply boundary conditions
        bcs = self._apply_thermal_boundary_conditions()
        
        # Time stepping loop
        for n in range(n_steps):
            # Solve for current time step
            df.solve(a == L, self.T, bcs)
            
            # Calculate heat flux
            q = self._calculate_heat_flux()
            
            # Store solutions
            T_solutions.append(self.T.copy(deepcopy=True))
            q_solutions.append(q.copy(deepcopy=True))
            
            # Update previous solution
            self.T_n.assign(self.T)
            
            if (n + 1) % 10 == 0:
                print(f"Time step {n+1}/{n_steps} completed")
        
        solutions = {
            'temperature': T_solutions,
            'heat_flux': q_solutions
        }
        
        return solutions
        
    def _apply_thermal_boundary_conditions(self) -> List[df.DirichletBC]:
        """
        Apply thermal boundary conditions.
        
        Returns:
            List of boundary conditions
        """
        bcs = []
        
        # Inlet temperature boundary conditions
        T_fuel_inlet = self.params.get('fuel_inlet_temp', 1073.0)
        T_air_inlet = self.params.get('air_inlet_temp', 1073.0)
        
        # Fuel inlet temperature
        if 'fuel_inlet' in self.boundary_ids:
            bc_fuel = df.DirichletBC(self.V_T, df.Constant(T_fuel_inlet),
                                    self.boundary_ids['fuel_inlet'])
            bcs.append(bc_fuel)
        
        # Air inlet temperature
        if 'air_inlet' in self.boundary_ids:
            bc_air = df.DirichletBC(self.V_T, df.Constant(T_air_inlet),
                                   self.boundary_ids['air_inlet'])
            bcs.append(bc_air)
        
        # External wall heat transfer (Robin BC: -k*dT/dn = h*(T - T_amb))
        # This would require implementing Robin boundary conditions
        # For now, use simplified Dirichlet BC
        T_ambient = 300.0  # Room temperature
        if 'external_walls' in self.boundary_ids:
            bc_ext = df.DirichletBC(self.V_T, df.Constant(T_ambient),
                                   self.boundary_ids['external_walls'])
            bcs.append(bc_ext)
        
        return bcs
        
    def _calculate_heat_flux(self) -> df.Function:
        """
        Calculate heat flux from temperature field.
        
        Returns:
            Heat flux vector function
        """
        
        # Heat flux: q = -k * grad(T)
        q_expr = -self.k_thermal * df.grad(self.T)
        
        # Project to vector function space
        q = df.project(q_expr, self.V_q)
        
        return q
        
    def calculate_thermal_metrics(self, solutions: Dict[str, df.Function]) -> Dict[str, float]:
        """
        Calculate thermal performance metrics.
        
        Args:
            solutions: Dictionary of thermal solution functions
            
        Returns:
            Dictionary of thermal metrics
        """
        
        T = solutions['temperature']
        q = solutions['heat_flux']
        
        # Average temperature
        T_avg = df.assemble(T * df.dx) / df.assemble(df.Constant(1.0) * df.dx)
        
        # Maximum temperature
        T_max = T.vector().max()
        
        # Minimum temperature
        T_min = T.vector().min()
        
        # Temperature gradient magnitude
        grad_T_mag = df.sqrt(df.dot(df.grad(T), df.grad(T)))
        grad_T_avg = df.assemble(grad_T_mag * df.dx) / df.assemble(df.Constant(1.0) * df.dx)
        
        # Heat flux magnitude
        q_mag = df.sqrt(df.dot(q, q))
        q_avg = df.assemble(q_mag * df.dx) / df.assemble(df.Constant(1.0) * df.dx)
        
        # Total heat generation
        Q_total = df.assemble(self.Q_source * df.dx)
        
        metrics = {
            'average_temperature': float(T_avg),
            'maximum_temperature': float(T_max),
            'minimum_temperature': float(T_min),
            'temperature_range': float(T_max - T_min),
            'average_temperature_gradient': float(grad_T_avg),
            'average_heat_flux': float(q_avg),
            'total_heat_generation': float(Q_total)
        }
        
        return metrics
        
    def get_thermal_field_data(self, solutions: Dict[str, df.Function]) -> Dict[str, np.ndarray]:
        """
        Extract thermal field data for export.
        
        Args:
            solutions: Dictionary of thermal solution functions
            
        Returns:
            Dictionary of thermal field arrays
        """
        
        field_data = {}
        
        # Get mesh coordinates
        coords = self.mesh.coordinates()
        
        # Extract thermal fields
        for name, func in solutions.items():
            if func.value_rank() == 0:  # Scalar field
                values = func.compute_vertex_values(self.mesh)
                field_data[name] = values
            elif func.value_rank() == 1:  # Vector field
                values = func.compute_vertex_values(self.mesh)
                n_vertices = self.mesh.num_vertices()
                n_components = func.value_size()
                field_data[name] = values.reshape((n_components, n_vertices)).T
        
        # Add coordinates
        field_data['coordinates'] = coords
        
        return field_data


class ThermalSolver:
    """
    High-level interface for thermal simulations.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize thermal solver with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def solve_for_parameters(self, mesh_file: str, parameters: Dict[str, float],
                           geometry_info: Dict[str, Any], 
                           electrochemical_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Solve thermal problem for given parameters.
        
        Args:
            mesh_file: Path to mesh file
            parameters: Physical and operating parameters
            geometry_info: Geometry information
            electrochemical_data: Electrochemical simulation results
            
        Returns:
            Dictionary containing thermal solutions and metrics
        """
        
        # Create thermal model
        model = ThermalModel(mesh_file, parameters, geometry_info, electrochemical_data)
        
        # Solve based on configuration
        time_stepping = self.config['simulation'].get('time_stepping', False)
        
        if time_stepping:
            dt = self.config['simulation'].get('dt', 0.1)
            t_final = self.config['simulation'].get('t_final', 100.0)
            solutions = model.solve_transient_thermal(dt, t_final)
            
            # Use final solution for metrics
            final_solutions = {
                'temperature': solutions['temperature'][-1],
                'heat_flux': solutions['heat_flux'][-1]
            }
        else:
            solutions = model.solve_steady_state_thermal()
            final_solutions = solutions
        
        # Calculate metrics
        metrics = model.calculate_thermal_metrics(final_solutions)
        
        # Extract field data
        field_data = model.get_thermal_field_data(final_solutions)
        
        result = {
            'solutions': solutions,
            'metrics': metrics,
            'field_data': field_data,
            'parameters': parameters.copy()
        }
        
        return result


if __name__ == "__main__":
    # Example usage
    config_path = "../../config/simulation_config.yaml"
    
    # Mock parameters for testing
    parameters = {
        'fuel_inlet_temp': 1073.0,
        'air_inlet_temp': 1073.0,
        'anode_thermal_conductivity': 10.0,
        'electrolyte_thermal_conductivity': 3.0,
        'cathode_thermal_conductivity': 5.0,
        'interconnect_thermal_conductivity': 25.0
    }
    
    # Mock geometry info
    geometry_info = {
        'domain_ids': {'anode': 1, 'electrolyte': 2, 'cathode': 3},
        'boundary_ids': {'fuel_inlet': 10, 'air_inlet': 12, 'external_walls': 16}
    }
    
    print("Thermal solver module loaded successfully")
    print("Parameters:", parameters)
    print("Geometry info:", geometry_info)