"""
Mechanical simulation module for SOFC.
Solves stress/strain equations with thermal expansion and material property variations.
"""

import numpy as np
import dolfin as df
from typing import Dict, List, Tuple, Optional, Any
import yaml


class MechanicalModel:
    """
    Solves mechanical equations for SOFC using FEniCS.
    """
    
    def __init__(self, mesh_file: str, parameters: Dict[str, float], 
                 geometry_info: Dict[str, Any], thermal_data: Dict[str, Any] = None):
        """
        Initialize mechanical model.
        
        Args:
            mesh_file: Path to mesh file
            parameters: Physical and operating parameters
            geometry_info: Geometry and domain information
            thermal_data: Results from thermal simulation
        """
        self.mesh_file = mesh_file
        self.params = parameters
        self.geometry_info = geometry_info
        self.thermal_data = thermal_data
        
        # Load mesh
        self.mesh = df.Mesh(mesh_file)
        
        # Reference temperature for thermal expansion
        self.T_ref = 298.0  # Room temperature (K)
        
        # Domain markers
        self.domain_ids = geometry_info['domain_ids']
        self.boundary_ids = geometry_info['boundary_ids']
        
        # Initialize function spaces and functions
        self._setup_function_spaces()
        self._setup_material_properties()
        
    def _setup_function_spaces(self):
        """Set up function spaces for mechanical variables."""
        
        # Vector function space for displacement (3D)
        self.V_u = df.VectorFunctionSpace(self.mesh, 'P', 1)
        
        # Tensor function space for stress/strain
        self.V_tensor = df.TensorFunctionSpace(self.mesh, 'P', 1)
        
        # Solution functions
        self.u = df.Function(self.V_u)  # Displacement
        
        # Test and trial functions
        self.v = df.TestFunction(self.V_u)
        self.du = df.TrialFunction(self.V_u)
        
    def _setup_material_properties(self):
        """Set up mechanical material property functions."""
        
        # Young's modulus function
        self.E = df.Function(df.FunctionSpace(self.mesh, 'DG', 0))
        
        # Poisson's ratio function
        self.nu = df.Function(df.FunctionSpace(self.mesh, 'DG', 0))
        
        # Coefficient of thermal expansion function
        self.alpha = df.Function(df.FunctionSpace(self.mesh, 'DG', 0))
        
        # Temperature field (from thermal analysis)
        self.T = df.Function(df.FunctionSpace(self.mesh, 'P', 1))
        
        # Assign material properties
        self._assign_mechanical_properties()
        
    def _assign_mechanical_properties(self):
        """Assign mechanical properties to different domains."""
        
        # Get material properties from parameters
        E_anode = self.params.get('anode_youngs_modulus', 100e9)
        E_electrolyte = self.params.get('electrolyte_youngs_modulus', 200e9)
        E_cathode = self.params.get('cathode_youngs_modulus', 100e9)
        E_interconnect = self.params.get('interconnect_youngs_modulus', 200e9)
        
        alpha_anode = self.params.get('anode_thermal_expansion', 12e-6)
        alpha_electrolyte = self.params.get('electrolyte_thermal_expansion', 10.5e-6)
        alpha_cathode = self.params.get('cathode_thermal_expansion', 12e-6)
        alpha_interconnect = self.params.get('interconnect_thermal_expansion', 12e-6)
        
        # Assign average properties (simplified)
        E_avg = (E_anode + E_electrolyte + E_cathode + E_interconnect) / 4
        alpha_avg = (alpha_anode + alpha_electrolyte + alpha_cathode + alpha_interconnect) / 4
        
        self.E.vector()[:] = E_avg
        self.nu.vector()[:] = 0.3  # Typical Poisson's ratio for ceramics
        self.alpha.vector()[:] = alpha_avg
        
        # Set temperature field
        if self.thermal_data and 'temperature' in self.thermal_data:
            T_thermal = self.thermal_data['temperature']
            # Interpolate thermal solution to mechanical mesh
            self.T.interpolate(T_thermal)
        else:
            # Use inlet temperature as uniform field
            T_inlet = self.params.get('fuel_inlet_temp', 1073.0)
            self.T.interpolate(df.Constant(T_inlet))
            
    def solve_mechanical(self) -> Dict[str, df.Function]:
        """
        Solve mechanical equilibrium equations.
        
        Returns:
            Dictionary containing mechanical solutions
        """
        
        # Define variational problem
        a, L = self._define_mechanical_variational_form()
        
        # Apply boundary conditions
        bcs = self._apply_mechanical_boundary_conditions()
        
        # Solve linear system
        df.solve(a == L, self.u, bcs, 
                solver_parameters={'linear_solver': 'mumps'})
        
        # Calculate stress and strain
        stress = self._calculate_stress()
        strain = self._calculate_strain()
        von_mises = self._calculate_von_mises_stress(stress)
        
        solutions = {
            'displacement': self.u,
            'stress': stress,
            'strain': strain,
            'von_mises_stress': von_mises
        }
        
        return solutions
        
    def _define_mechanical_variational_form(self) -> Tuple[df.Form, df.Form]:
        """
        Define variational formulation for mechanical equilibrium.
        
        Returns:
            Bilinear and linear forms (a, L)
        """
        
        # Strain tensor
        def epsilon(u):
            return 0.5 * (df.nabla_grad(u) + df.nabla_grad(u).T)
        
        # Stress tensor (with thermal expansion)
        def sigma(u, T):
            # Elastic strain
            eps_elastic = epsilon(u) - self.alpha * (T - self.T_ref) * df.Identity(len(u))
            
            # Stress-strain relationship (isotropic)
            lmbda = self.E * self.nu / ((1 + self.nu) * (1 - 2 * self.nu))
            mu = self.E / (2 * (1 + self.nu))
            
            return lmbda * df.tr(eps_elastic) * df.Identity(len(u)) + 2 * mu * eps_elastic
        
        # Variational forms
        a = df.inner(sigma(self.du, self.T), epsilon(self.v)) * df.dx
        L = df.dot(df.Constant((0, 0, 0)), self.v) * df.dx  # No body forces
        
        return a, L
        
    def _apply_mechanical_boundary_conditions(self) -> List[df.DirichletBC]:
        """
        Apply mechanical boundary conditions.
        
        Returns:
            List of boundary conditions
        """
        bcs = []
        
        # Fixed boundary condition (prevent rigid body motion)
        # Fix one corner point in all directions
        def corner_point(x, on_boundary):
            return df.near(x[0], 0.0) and df.near(x[1], 0.0) and df.near(x[2], 0.0)
        
        bc_fixed = df.DirichletBC(self.V_u, df.Constant((0, 0, 0)), corner_point, method='pointwise')
        bcs.append(bc_fixed)
        
        # Symmetry boundary conditions (if applicable)
        # For example, fix x-displacement on x=0 plane
        def x_symmetry(x, on_boundary):
            return on_boundary and df.near(x[0], 0.0)
        
        bc_x_sym = df.DirichletBC(self.V_u.sub(0), df.Constant(0.0), x_symmetry)
        bcs.append(bc_x_sym)
        
        # Fix y-displacement on y=0 plane
        def y_symmetry(x, on_boundary):
            return on_boundary and df.near(x[1], 0.0)
        
        bc_y_sym = df.DirichletBC(self.V_u.sub(1), df.Constant(0.0), y_symmetry)
        bcs.append(bc_y_sym)
        
        return bcs
        
    def _calculate_stress(self) -> df.Function:
        """
        Calculate stress tensor from displacement field.
        
        Returns:
            Stress tensor function
        """
        
        # Strain tensor
        def epsilon(u):
            return 0.5 * (df.nabla_grad(u) + df.nabla_grad(u).T)
        
        # Elastic strain (subtract thermal strain)
        eps_elastic = epsilon(self.u) - self.alpha * (self.T - self.T_ref) * df.Identity(len(self.u))
        
        # Stress-strain relationship
        lmbda = self.E * self.nu / ((1 + self.nu) * (1 - 2 * self.nu))
        mu = self.E / (2 * (1 + self.nu))
        
        stress_expr = lmbda * df.tr(eps_elastic) * df.Identity(len(self.u)) + 2 * mu * eps_elastic
        
        # Project to tensor function space
        stress = df.project(stress_expr, self.V_tensor)
        
        return stress
        
    def _calculate_strain(self) -> df.Function:
        """
        Calculate strain tensor from displacement field.
        
        Returns:
            Strain tensor function
        """
        
        # Total strain tensor
        def epsilon(u):
            return 0.5 * (df.nabla_grad(u) + df.nabla_grad(u).T)
        
        strain_expr = epsilon(self.u)
        
        # Project to tensor function space
        strain = df.project(strain_expr, self.V_tensor)
        
        return strain
        
    def _calculate_von_mises_stress(self, stress: df.Function) -> df.Function:
        """
        Calculate von Mises stress from stress tensor.
        
        Args:
            stress: Stress tensor function
            
        Returns:
            von Mises stress function
        """
        
        # Extract stress components
        s11, s12, s13 = stress[0, 0], stress[0, 1], stress[0, 2]
        s21, s22, s23 = stress[1, 0], stress[1, 1], stress[1, 2]
        s31, s32, s33 = stress[2, 0], stress[2, 1], stress[2, 2]
        
        # von Mises stress formula
        von_mises_expr = df.sqrt(0.5 * ((s11 - s22)**2 + (s22 - s33)**2 + (s33 - s11)**2 + 
                                       6 * (s12**2 + s23**2 + s31**2)))
        
        # Project to scalar function space
        V_scalar = df.FunctionSpace(self.mesh, 'P', 1)
        von_mises = df.project(von_mises_expr, V_scalar)
        
        return von_mises
        
    def calculate_mechanical_metrics(self, solutions: Dict[str, df.Function]) -> Dict[str, float]:
        """
        Calculate mechanical performance metrics.
        
        Args:
            solutions: Dictionary of mechanical solution functions
            
        Returns:
            Dictionary of mechanical metrics
        """
        
        u = solutions['displacement']
        stress = solutions['stress']
        von_mises = solutions['von_mises_stress']
        
        # Maximum displacement magnitude
        u_mag = df.sqrt(df.dot(u, u))
        u_max = u_mag.vector().max()
        
        # Average displacement magnitude
        u_avg = df.assemble(u_mag * df.dx) / df.assemble(df.Constant(1.0) * df.dx)
        
        # Maximum von Mises stress
        von_mises_max = von_mises.vector().max()
        
        # Average von Mises stress
        von_mises_avg = df.assemble(von_mises * df.dx) / df.assemble(df.Constant(1.0) * df.dx)
        
        # Stress concentration factor (max/avg)
        stress_concentration = von_mises_max / (von_mises_avg + 1e-12)
        
        # Maximum principal stress
        stress_eigenvalues = self._calculate_principal_stresses(stress)
        max_principal_stress = max(stress_eigenvalues) if stress_eigenvalues else 0.0
        
        metrics = {
            'maximum_displacement': float(u_max),
            'average_displacement': float(u_avg),
            'maximum_von_mises_stress': float(von_mises_max),
            'average_von_mises_stress': float(von_mises_avg),
            'stress_concentration_factor': float(stress_concentration),
            'maximum_principal_stress': float(max_principal_stress)
        }
        
        return metrics
        
    def _calculate_principal_stresses(self, stress: df.Function) -> List[float]:
        """
        Calculate principal stresses from stress tensor.
        
        Args:
            stress: Stress tensor function
            
        Returns:
            List of principal stress values
        """
        
        # This is a simplified calculation
        # In practice, you would compute eigenvalues of stress tensor at each point
        
        # Get stress tensor values at vertices
        stress_values = stress.compute_vertex_values(self.mesh)
        n_vertices = self.mesh.num_vertices()
        
        # Reshape to tensor format
        stress_tensor = stress_values.reshape((9, n_vertices)).T
        
        principal_stresses = []
        
        # Calculate eigenvalues for a few sample points
        for i in range(0, min(n_vertices, 100), 10):
            # Extract 3x3 stress tensor
            s = stress_tensor[i].reshape((3, 3))
            
            # Calculate eigenvalues
            eigenvals = np.linalg.eigvals(s)
            principal_stresses.extend(eigenvals)
        
        return principal_stresses
        
    def get_mechanical_field_data(self, solutions: Dict[str, df.Function]) -> Dict[str, np.ndarray]:
        """
        Extract mechanical field data for export.
        
        Args:
            solutions: Dictionary of mechanical solution functions
            
        Returns:
            Dictionary of mechanical field arrays
        """
        
        field_data = {}
        
        # Get mesh coordinates
        coords = self.mesh.coordinates()
        
        # Extract mechanical fields
        for name, func in solutions.items():
            if func.value_rank() == 0:  # Scalar field
                values = func.compute_vertex_values(self.mesh)
                field_data[name] = values
            elif func.value_rank() == 1:  # Vector field
                values = func.compute_vertex_values(self.mesh)
                n_vertices = self.mesh.num_vertices()
                n_components = func.value_size()
                field_data[name] = values.reshape((n_components, n_vertices)).T
            elif func.value_rank() == 2:  # Tensor field
                values = func.compute_vertex_values(self.mesh)
                n_vertices = self.mesh.num_vertices()
                n_components = func.value_size()
                field_data[name] = values.reshape((n_components, n_vertices)).T
        
        # Add coordinates
        field_data['coordinates'] = coords
        
        return field_data


class MechanicalSolver:
    """
    High-level interface for mechanical simulations.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize mechanical solver with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def solve_for_parameters(self, mesh_file: str, parameters: Dict[str, float],
                           geometry_info: Dict[str, Any], 
                           thermal_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Solve mechanical problem for given parameters.
        
        Args:
            mesh_file: Path to mesh file
            parameters: Physical and operating parameters
            geometry_info: Geometry information
            thermal_data: Thermal simulation results
            
        Returns:
            Dictionary containing mechanical solutions and metrics
        """
        
        # Create mechanical model
        model = MechanicalModel(mesh_file, parameters, geometry_info, thermal_data)
        
        # Solve mechanical equations
        solutions = model.solve_mechanical()
        
        # Calculate metrics
        metrics = model.calculate_mechanical_metrics(solutions)
        
        # Extract field data
        field_data = model.get_mechanical_field_data(solutions)
        
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
        'anode_youngs_modulus': 100e9,
        'electrolyte_youngs_modulus': 200e9,
        'cathode_youngs_modulus': 100e9,
        'interconnect_youngs_modulus': 200e9,
        'anode_thermal_expansion': 12e-6,
        'electrolyte_thermal_expansion': 10.5e-6,
        'cathode_thermal_expansion': 12e-6,
        'interconnect_thermal_expansion': 12e-6,
        'fuel_inlet_temp': 1073.0
    }
    
    # Mock geometry info
    geometry_info = {
        'domain_ids': {'anode': 1, 'electrolyte': 2, 'cathode': 3},
        'boundary_ids': {}
    }
    
    print("Mechanical solver module loaded successfully")
    print("Parameters:", parameters)
    print("Geometry info:", geometry_info)