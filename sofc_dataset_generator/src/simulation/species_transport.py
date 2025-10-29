"""
Species transport simulation module for SOFC.
Solves mass transport equations for H2, H2O, O2, and N2 species.
"""

import numpy as np
import dolfin as df
from typing import Dict, List, Tuple, Optional, Any
import yaml


class SpeciesTransportModel:
    """
    Solves species transport equations for SOFC using FEniCS.
    """
    
    def __init__(self, mesh_file: str, parameters: Dict[str, float], 
                 geometry_info: Dict[str, Any], electrochemical_data: Dict[str, Any] = None,
                 thermal_data: Dict[str, Any] = None):
        """
        Initialize species transport model.
        
        Args:
            mesh_file: Path to mesh file
            parameters: Physical and operating parameters
            geometry_info: Geometry and domain information
            electrochemical_data: Results from electrochemical simulation
            thermal_data: Results from thermal simulation
        """
        self.mesh_file = mesh_file
        self.params = parameters
        self.geometry_info = geometry_info
        self.electrochemical_data = electrochemical_data
        self.thermal_data = thermal_data
        
        # Load mesh
        self.mesh = df.Mesh(mesh_file)
        
        # Physical constants
        self.R = 8.314   # Gas constant (J/mol·K)
        self.F = 96485.0  # Faraday constant (C/mol)
        
        # Species properties
        self.species_data = self._initialize_species_data()
        
        # Domain markers
        self.domain_ids = geometry_info['domain_ids']
        self.boundary_ids = geometry_info['boundary_ids']
        
        # Initialize function spaces and functions
        self._setup_function_spaces()
        self._setup_transport_properties()
        
    def _initialize_species_data(self) -> Dict[str, Dict[str, float]]:
        """
        Initialize species properties.
        
        Returns:
            Dictionary with species properties
        """
        
        species_data = {
            'H2': {
                'molar_mass': 0.002016,  # kg/mol
                'diffusivity_ref': 1.0e-4,  # m²/s at reference conditions
                'activation_energy': 15000.0  # J/mol for diffusion
            },
            'H2O': {
                'molar_mass': 0.018015,  # kg/mol
                'diffusivity_ref': 8.0e-5,  # m²/s at reference conditions
                'activation_energy': 18000.0  # J/mol for diffusion
            },
            'O2': {
                'molar_mass': 0.031998,  # kg/mol
                'diffusivity_ref': 7.0e-5,  # m²/s at reference conditions
                'activation_energy': 16000.0  # J/mol for diffusion
            },
            'N2': {
                'molar_mass': 0.028014,  # kg/mol
                'diffusivity_ref': 9.0e-5,  # m²/s at reference conditions
                'activation_energy': 15500.0  # J/mol for diffusion
            }
        }
        
        return species_data
        
    def _setup_function_spaces(self):
        """Set up function spaces for species concentrations."""
        
        # Function space for species concentrations (scalar)
        self.V_c = df.FunctionSpace(self.mesh, 'P', 1)
        
        # Function space for species flux (vector)
        self.V_flux = df.VectorFunctionSpace(self.mesh, 'P', 1)
        
        # Mixed function space for all species
        elements = [df.FiniteElement('P', self.mesh.ufl_cell(), 1) for _ in range(4)]
        mixed_element = df.MixedElement(elements)
        self.V_mixed = df.FunctionSpace(self.mesh, mixed_element)
        
        # Solution functions for [H2, H2O, O2, N2] concentrations
        self.c = df.Function(self.V_mixed)
        self.c_H2, self.c_H2O, self.c_O2, self.c_N2 = df.split(self.c)
        
        # Test functions
        self.v_H2, self.v_H2O, self.v_O2, self.v_N2 = df.TestFunctions(self.V_mixed)
        
        # Previous time step (for transient analysis)
        self.c_n = df.Function(self.V_mixed)
        
        # Temperature field (from thermal analysis)
        self.T = df.Function(df.FunctionSpace(self.mesh, 'P', 1))
        
    def _setup_transport_properties(self):
        """Set up transport property functions."""
        
        # Porosity function
        self.porosity = df.Function(df.FunctionSpace(self.mesh, 'DG', 0))
        
        # Tortuosity function
        self.tortuosity = df.Function(df.FunctionSpace(self.mesh, 'DG', 0))
        
        # Effective diffusivity functions for each species
        self.D_eff = {}
        for species in ['H2', 'H2O', 'O2', 'N2']:
            self.D_eff[species] = df.Function(df.FunctionSpace(self.mesh, 'DG', 0))
        
        # Reaction rate functions
        self.R_H2 = df.Function(df.FunctionSpace(self.mesh, 'DG', 0))
        self.R_H2O = df.Function(df.FunctionSpace(self.mesh, 'DG', 0))
        self.R_O2 = df.Function(df.FunctionSpace(self.mesh, 'DG', 0))
        
        # Assign transport properties
        self._assign_transport_properties()
        
    def _assign_transport_properties(self):
        """Assign transport properties to different domains."""
        
        # Get material properties
        anode_porosity = self.params.get('anode_porosity', 0.4)
        cathode_porosity = self.params.get('cathode_porosity', 0.4)
        
        # Assign average porosity (simplified)
        avg_porosity = (anode_porosity + cathode_porosity) / 2
        self.porosity.vector()[:] = avg_porosity
        
        # Tortuosity (Bruggeman correlation: tau = phi^(-0.5))
        tortuosity_value = avg_porosity**(-0.5)
        self.tortuosity.vector()[:] = tortuosity_value
        
        # Set temperature field
        if self.thermal_data and 'temperature' in self.thermal_data:
            T_thermal = self.thermal_data['temperature']
            self.T.interpolate(T_thermal)
        else:
            T_inlet = self.params.get('fuel_inlet_temp', 1073.0)
            self.T.interpolate(df.Constant(T_inlet))
        
        # Calculate effective diffusivities
        self._calculate_effective_diffusivities()
        
        # Calculate reaction rates
        self._calculate_reaction_rates()
        
    def _calculate_effective_diffusivities(self):
        """Calculate temperature-dependent effective diffusivities."""
        
        T_ref = 298.0  # Reference temperature (K)
        
        for species, data in self.species_data.items():
            D_ref = data['diffusivity_ref']
            E_a = data['activation_energy']
            
            # Arrhenius temperature dependence
            D_bulk = D_ref * df.exp(-E_a / self.R * (1/self.T - 1/T_ref))
            
            # Effective diffusivity in porous media
            D_eff_expr = self.porosity / self.tortuosity * D_bulk
            
            # Project to function space
            self.D_eff[species] = df.project(D_eff_expr, df.FunctionSpace(self.mesh, 'DG', 0))
            
    def _calculate_reaction_rates(self):
        """Calculate electrochemical reaction rates."""
        
        if self.electrochemical_data is None:
            # Set zero reaction rates
            self.R_H2.vector()[:] = 0.0
            self.R_H2O.vector()[:] = 0.0
            self.R_O2.vector()[:] = 0.0
            return
        
        # Get current density from electrochemical simulation
        j = self.electrochemical_data.get('current_density')
        
        if j is None:
            self.R_H2.vector()[:] = 0.0
            self.R_H2O.vector()[:] = 0.0
            self.R_O2.vector()[:] = 0.0
            return
        
        # Current density magnitude
        j_mag = df.sqrt(df.dot(j, j))
        
        # Reaction rates from Faraday's law
        # Anode: H2 + O²⁻ → H2O + 2e⁻
        # Cathode: 1/2 O2 + 2e⁻ → O²⁻
        
        # Molar reaction rates (mol/m³·s)
        R_H2_expr = -j_mag / (2 * self.F)  # H2 consumption
        R_H2O_expr = j_mag / (2 * self.F)   # H2O production
        R_O2_expr = -j_mag / (4 * self.F)   # O2 consumption
        
        # Project to function spaces
        self.R_H2 = df.project(R_H2_expr, df.FunctionSpace(self.mesh, 'DG', 0))
        self.R_H2O = df.project(R_H2O_expr, df.FunctionSpace(self.mesh, 'DG', 0))
        self.R_O2 = df.project(R_O2_expr, df.FunctionSpace(self.mesh, 'DG', 0))
        
    def solve_steady_state_transport(self) -> Dict[str, df.Function]:
        """
        Solve steady-state species transport equations.
        
        Returns:
            Dictionary containing species concentration solutions
        """
        
        # Define variational problem
        F = self._define_transport_variational_form()
        
        # Apply boundary conditions
        bcs = self._apply_transport_boundary_conditions()
        
        # Solve nonlinear system
        df.solve(F == 0, self.c, bcs,
                solver_parameters={'newton_solver': {'relative_tolerance': 1e-6,
                                                   'absolute_tolerance': 1e-9,
                                                   'maximum_iterations': 50}})
        
        # Extract individual species concentrations
        c_H2_sol, c_H2O_sol, c_O2_sol, c_N2_sol = self.c.split(deepcopy=True)
        
        # Calculate species fluxes
        fluxes = self._calculate_species_fluxes()
        
        solutions = {
            'h2_concentration': c_H2_sol,
            'h2o_concentration': c_H2O_sol,
            'o2_concentration': c_O2_sol,
            'n2_concentration': c_N2_sol,
            'h2_flux': fluxes['H2'],
            'h2o_flux': fluxes['H2O'],
            'o2_flux': fluxes['O2'],
            'n2_flux': fluxes['N2']
        }
        
        return solutions
        
    def _define_transport_variational_form(self) -> df.Form:
        """
        Define variational formulation for species transport.
        
        Returns:
            Variational form
        """
        
        # Species transport equations: -div(D_eff * grad(c)) + R = 0
        
        # H2 transport
        F_H2 = (df.inner(self.D_eff['H2'] * df.grad(self.c_H2), df.grad(self.v_H2)) * df.dx - 
                self.R_H2 * self.v_H2 * df.dx)
        
        # H2O transport
        F_H2O = (df.inner(self.D_eff['H2O'] * df.grad(self.c_H2O), df.grad(self.v_H2O)) * df.dx - 
                 self.R_H2O * self.v_H2O * df.dx)
        
        # O2 transport
        F_O2 = (df.inner(self.D_eff['O2'] * df.grad(self.c_O2), df.grad(self.v_O2)) * df.dx - 
                self.R_O2 * self.v_O2 * df.dx)
        
        # N2 transport (no reaction)
        F_N2 = df.inner(self.D_eff['N2'] * df.grad(self.c_N2), df.grad(self.v_N2)) * df.dx
        
        # Total variational form
        F = F_H2 + F_H2O + F_O2 + F_N2
        
        return F
        
    def _apply_transport_boundary_conditions(self) -> List[df.DirichletBC]:
        """
        Apply boundary conditions for species transport.
        
        Returns:
            List of boundary conditions
        """
        bcs = []
        
        # Fuel inlet concentrations
        # Assume pure H2 at fuel inlet
        P_fuel = self.params.get('fuel_pressure', 101325.0)  # Pa
        T_fuel = self.params.get('fuel_inlet_temp', 1073.0)   # K
        
        # Concentration from ideal gas law: c = P / (R * T)
        c_H2_inlet = P_fuel / (self.R * T_fuel)
        c_H2O_inlet = 0.0  # Assume dry fuel
        
        if 'fuel_inlet' in self.boundary_ids:
            bc_H2_inlet = df.DirichletBC(self.V_mixed.sub(0), df.Constant(c_H2_inlet),
                                        self.boundary_ids['fuel_inlet'])
            bcs.append(bc_H2_inlet)
            
            bc_H2O_inlet = df.DirichletBC(self.V_mixed.sub(1), df.Constant(c_H2O_inlet),
                                         self.boundary_ids['fuel_inlet'])
            bcs.append(bc_H2O_inlet)
        
        # Air inlet concentrations
        # Assume air composition: 21% O2, 79% N2
        P_air = self.params.get('air_pressure', 101325.0)
        T_air = self.params.get('air_inlet_temp', 1073.0)
        
        c_O2_inlet = 0.21 * P_air / (self.R * T_air)
        c_N2_inlet = 0.79 * P_air / (self.R * T_air)
        
        if 'air_inlet' in self.boundary_ids:
            bc_O2_inlet = df.DirichletBC(self.V_mixed.sub(2), df.Constant(c_O2_inlet),
                                        self.boundary_ids['air_inlet'])
            bcs.append(bc_O2_inlet)
            
            bc_N2_inlet = df.DirichletBC(self.V_mixed.sub(3), df.Constant(c_N2_inlet),
                                        self.boundary_ids['air_inlet'])
            bcs.append(bc_N2_inlet)
        
        return bcs
        
    def _calculate_species_fluxes(self) -> Dict[str, df.Function]:
        """
        Calculate species flux vectors.
        
        Returns:
            Dictionary of species flux functions
        """
        
        fluxes = {}
        
        # Extract concentration solutions
        c_H2, c_H2O, c_O2, c_N2 = self.c.split()
        
        # Calculate fluxes: J = -D_eff * grad(c)
        species_concentrations = {
            'H2': c_H2,
            'H2O': c_H2O,
            'O2': c_O2,
            'N2': c_N2
        }
        
        for species, concentration in species_concentrations.items():
            flux_expr = -self.D_eff[species] * df.grad(concentration)
            flux = df.project(flux_expr, self.V_flux)
            fluxes[species] = flux
        
        return fluxes
        
    def calculate_transport_metrics(self, solutions: Dict[str, df.Function]) -> Dict[str, float]:
        """
        Calculate species transport metrics.
        
        Args:
            solutions: Dictionary of species transport solutions
            
        Returns:
            Dictionary of transport metrics
        """
        
        metrics = {}
        
        # Calculate average concentrations
        for species in ['h2', 'h2o', 'o2', 'n2']:
            conc_key = f'{species}_concentration'
            if conc_key in solutions:
                c = solutions[conc_key]
                c_avg = df.assemble(c * df.dx) / df.assemble(df.Constant(1.0) * df.dx)
                c_max = c.vector().max()
                c_min = c.vector().min()
                
                metrics[f'average_{species}_concentration'] = float(c_avg)
                metrics[f'maximum_{species}_concentration'] = float(c_max)
                metrics[f'minimum_{species}_concentration'] = float(c_min)
        
        # Calculate fuel utilization
        if 'h2_concentration' in solutions:
            c_H2 = solutions['h2_concentration']
            
            # Fuel utilization = (c_inlet - c_outlet) / c_inlet
            # Simplified calculation using average concentration
            c_H2_avg = df.assemble(c_H2 * df.dx) / df.assemble(df.Constant(1.0) * df.dx)
            
            P_fuel = self.params.get('fuel_pressure', 101325.0)
            T_fuel = self.params.get('fuel_inlet_temp', 1073.0)
            c_H2_inlet = P_fuel / (self.R * T_fuel)
            
            fuel_utilization = (c_H2_inlet - c_H2_avg) / c_H2_inlet
            metrics['fuel_utilization'] = float(max(0.0, fuel_utilization))
        
        # Calculate air utilization
        if 'o2_concentration' in solutions:
            c_O2 = solutions['o2_concentration']
            
            c_O2_avg = df.assemble(c_O2 * df.dx) / df.assemble(df.Constant(1.0) * df.dx)
            
            P_air = self.params.get('air_pressure', 101325.0)
            T_air = self.params.get('air_inlet_temp', 1073.0)
            c_O2_inlet = 0.21 * P_air / (self.R * T_air)
            
            air_utilization = (c_O2_inlet - c_O2_avg) / c_O2_inlet
            metrics['air_utilization'] = float(max(0.0, air_utilization))
        
        return metrics
        
    def get_species_field_data(self, solutions: Dict[str, df.Function]) -> Dict[str, np.ndarray]:
        """
        Extract species field data for export.
        
        Args:
            solutions: Dictionary of species solution functions
            
        Returns:
            Dictionary of species field arrays
        """
        
        field_data = {}
        
        # Get mesh coordinates
        coords = self.mesh.coordinates()
        
        # Extract species fields
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


class SpeciesTransportSolver:
    """
    High-level interface for species transport simulations.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize species transport solver with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def solve_for_parameters(self, mesh_file: str, parameters: Dict[str, float],
                           geometry_info: Dict[str, Any], 
                           electrochemical_data: Dict[str, Any] = None,
                           thermal_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Solve species transport problem for given parameters.
        
        Args:
            mesh_file: Path to mesh file
            parameters: Physical and operating parameters
            geometry_info: Geometry information
            electrochemical_data: Electrochemical simulation results
            thermal_data: Thermal simulation results
            
        Returns:
            Dictionary containing species transport solutions and metrics
        """
        
        # Create species transport model
        model = SpeciesTransportModel(mesh_file, parameters, geometry_info, 
                                    electrochemical_data, thermal_data)
        
        # Solve species transport equations
        solutions = model.solve_steady_state_transport()
        
        # Calculate metrics
        metrics = model.calculate_transport_metrics(solutions)
        
        # Extract field data
        field_data = model.get_species_field_data(solutions)
        
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
        'anode_porosity': 0.4,
        'cathode_porosity': 0.4,
        'fuel_pressure': 101325.0,
        'air_pressure': 101325.0,
        'fuel_inlet_temp': 1073.0,
        'air_inlet_temp': 1073.0
    }
    
    # Mock geometry info
    geometry_info = {
        'domain_ids': {'anode': 1, 'electrolyte': 2, 'cathode': 3},
        'boundary_ids': {'fuel_inlet': 10, 'air_inlet': 12}
    }
    
    print("Species transport solver module loaded successfully")
    print("Parameters:", parameters)
    print("Geometry info:", geometry_info)