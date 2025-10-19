#!/usr/bin/env python
"""
Abaqus Input File Generator for Acoustic Transmission Loss
=========================================================

This module generates complete Abaqus input files (.inp) for acoustic transmission loss
simulations using keyword-based approach. This is useful for:
- Batch processing
- Parametric studies
- Integration with external optimization tools
- Running without Abaqus/CAE

Author: AI Assistant
Date: 2025-10-19
Units: SI (m-kg-s-Pa)
"""

import numpy as np
import math


class AbaqusInputGenerator:
    """Generate Abaqus input files for acoustic transmission loss simulations."""
    
    def __init__(self, model_name='AcousticTL'):
        """Initialize the input file generator."""
        self.model_name = model_name
        self.nodes = []
        self.elements = []
        self.node_sets = {}
        self.element_sets = {}
        self.materials = {}
        self.sections = {}
        
        # Analysis parameters
        self.freq_start = 100.0
        self.freq_end = 5000.0
        self.freq_inc = 25.0
        
        # Reference properties
        self.ref_density = 1025.0
        self.ref_sound_speed = 1500.0
        self.ref_bulk_modulus = self.ref_density * self.ref_sound_speed**2
        
    def generate_2d_rectangular_mesh(self, length, height, nx, ny):
        """
        Generate 2D rectangular mesh with AC2D4 elements.
        
        Parameters:
        -----------
        length : float
            Domain length
        height : float
            Domain height
        nx : int
            Number of elements in x-direction
        ny : int
            Number of elements in y-direction
        """
        # Generate nodes
        node_id = 1
        self.nodes = []
        node_map = {}  # (i,j) -> node_id
        
        for j in range(ny + 1):
            for i in range(nx + 1):
                x = i * length / nx
                y = j * height / ny
                self.nodes.append((node_id, x, y))
                node_map[(i, j)] = node_id
                node_id += 1
                
        # Generate elements (AC2D4 - 4-node quadrilaterals)
        elem_id = 1
        self.elements = []
        
        for j in range(ny):
            for i in range(nx):
                # Node connectivity (counter-clockwise)
                n1 = node_map[(i, j)]
                n2 = node_map[(i+1, j)]
                n3 = node_map[(i+1, j+1)]
                n4 = node_map[(i, j+1)]
                
                self.elements.append((elem_id, 'AC2D4', [n1, n2, n3, n4]))
                elem_id += 1
                
        # Create boundary sets
        self._create_2d_boundary_sets(nx, ny, node_map)
        
        print(f"Generated 2D mesh: {len(self.nodes)} nodes, {len(self.elements)} elements")
        
    def _create_2d_boundary_sets(self, nx, ny, node_map):
        """Create boundary node sets for 2D mesh."""
        # Inlet (left boundary)
        inlet_nodes = [node_map[(0, j)] for j in range(ny + 1)]
        self.node_sets['INLET'] = inlet_nodes
        
        # Outlet (right boundary)
        outlet_nodes = [node_map[(nx, j)] for j in range(ny + 1)]
        self.node_sets['OUTLET'] = outlet_nodes
        
        # Bottom boundary
        bottom_nodes = [node_map[(i, 0)] for i in range(nx + 1)]
        self.node_sets['BOTTOM'] = bottom_nodes
        
        # Top boundary
        top_nodes = [node_map[(i, ny)] for i in range(nx + 1)]
        self.node_sets['TOP'] = top_nodes
        
        # Lateral boundaries (top + bottom)
        self.node_sets['LATERAL'] = bottom_nodes + top_nodes
        
        # Probe sets
        probe_in_i = int(0.2 * nx)  # 20% from inlet
        probe_out_i = int(0.8 * nx)  # 80% from inlet
        
        probe_in_nodes = [node_map[(probe_in_i, j)] for j in range(ny + 1)]
        probe_out_nodes = [node_map[(probe_out_i, j)] for j in range(ny + 1)]
        
        self.node_sets['PROBE_IN'] = probe_in_nodes
        self.node_sets['PROBE_OUT'] = probe_out_nodes
        
    def generate_3d_rectangular_mesh(self, length, height, width, nx, ny, nz):
        """
        Generate 3D rectangular mesh with AC3D8 elements.
        
        Parameters:
        -----------
        length, height, width : float
            Domain dimensions
        nx, ny, nz : int
            Number of elements in each direction
        """
        # Generate nodes
        node_id = 1
        self.nodes = []
        node_map = {}  # (i,j,k) -> node_id
        
        for k in range(nz + 1):
            for j in range(ny + 1):
                for i in range(nx + 1):
                    x = i * length / nx
                    y = j * height / ny
                    z = k * width / nz
                    self.nodes.append((node_id, x, y, z))
                    node_map[(i, j, k)] = node_id
                    node_id += 1
                    
        # Generate elements (AC3D8 - 8-node hexahedra)
        elem_id = 1
        self.elements = []
        
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    # Node connectivity for hexahedron
                    n1 = node_map[(i, j, k)]
                    n2 = node_map[(i+1, j, k)]
                    n3 = node_map[(i+1, j+1, k)]
                    n4 = node_map[(i, j+1, k)]
                    n5 = node_map[(i, j, k+1)]
                    n6 = node_map[(i+1, j, k+1)]
                    n7 = node_map[(i+1, j+1, k+1)]
                    n8 = node_map[(i, j+1, k+1)]
                    
                    self.elements.append((elem_id, 'AC3D8', [n1, n2, n3, n4, n5, n6, n7, n8]))
                    elem_id += 1
                    
        # Create boundary sets
        self._create_3d_boundary_sets(nx, ny, nz, node_map)
        
        print(f"Generated 3D mesh: {len(self.nodes)} nodes, {len(self.elements)} elements")
        
    def _create_3d_boundary_sets(self, nx, ny, nz, node_map):
        """Create boundary node sets for 3D mesh."""
        # Inlet (x=0 face)
        inlet_nodes = []
        for k in range(nz + 1):
            for j in range(ny + 1):
                inlet_nodes.append(node_map[(0, j, k)])
        self.node_sets['INLET'] = inlet_nodes
        
        # Outlet (x=length face)
        outlet_nodes = []
        for k in range(nz + 1):
            for j in range(ny + 1):
                outlet_nodes.append(node_map[(nx, j, k)])
        self.node_sets['OUTLET'] = outlet_nodes
        
        # Lateral faces
        lateral_nodes = []
        
        # Bottom face (y=0)
        for k in range(nz + 1):
            for i in range(nx + 1):
                lateral_nodes.append(node_map[(i, 0, k)])
                
        # Top face (y=height)
        for k in range(nz + 1):
            for i in range(nx + 1):
                lateral_nodes.append(node_map[(i, ny, k)])
                
        # Front face (z=0)
        for j in range(ny + 1):
            for i in range(nx + 1):
                lateral_nodes.append(node_map[(i, j, 0)])
                
        # Back face (z=width)
        for j in range(ny + 1):
            for i in range(nx + 1):
                lateral_nodes.append(node_map[(i, j, nz)])
                
        self.node_sets['LATERAL'] = list(set(lateral_nodes))  # Remove duplicates
        
        # Probe sets
        probe_in_i = int(0.2 * nx)
        probe_out_i = int(0.8 * nx)
        
        probe_in_nodes = []
        probe_out_nodes = []
        
        for k in range(nz + 1):
            for j in range(ny + 1):
                probe_in_nodes.append(node_map[(probe_in_i, j, k)])
                probe_out_nodes.append(node_map[(probe_out_i, j, k)])
                
        self.node_sets['PROBE_IN'] = probe_in_nodes
        self.node_sets['PROBE_OUT'] = probe_out_nodes
        
    def add_layered_materials(self, layers):
        """
        Add layered materials.
        
        Parameters:
        -----------
        layers : list of dict
            Each dict contains 'name', 'density', 'bulk_modulus'
        """
        for layer in layers:
            name = layer['name']
            density = layer['density']
            bulk_modulus = layer['bulk_modulus']
            
            self.materials[name] = {
                'density': density,
                'bulk_modulus': bulk_modulus
            }
            
            # Create corresponding section
            self.sections[f"SECTION_{name}"] = {
                'material': name,
                'type': 'SOLID'
            }
            
        print(f"Added {len(layers)} layered materials")
        
    def add_graded_material(self, name, density_profile, bulk_modulus_profile):
        """
        Add graded material with field variable dependencies.
        
        Parameters:
        -----------
        name : str
            Material name
        density_profile : list of tuples
            [(field_value, density), ...]
        bulk_modulus_profile : list of tuples
            [(field_value, bulk_modulus), ...]
        """
        self.materials[name] = {
            'density_profile': density_profile,
            'bulk_modulus_profile': bulk_modulus_profile,
            'field_dependent': True
        }
        
        self.sections[f"SECTION_{name}"] = {
            'material': name,
            'type': 'SOLID'
        }
        
        print(f"Added graded material: {name}")
        
    def create_layered_element_sets(self, layer_heights):
        """
        Create element sets for layered materials.
        
        Parameters:
        -----------
        layer_heights : list of float
            Cumulative heights of layer boundaries
        """
        if not hasattr(self, 'elements') or not self.elements:
            raise ValueError("Mesh must be generated first")
            
        # Find elements in each layer
        layer_elements = [[] for _ in range(len(layer_heights))]
        
        for elem_id, elem_type, connectivity in self.elements:
            # Get element centroid
            node_coords = []
            for node_id in connectivity:
                for nid, x, y, *z in self.nodes:
                    if nid == node_id:
                        node_coords.append((x, y) + (z if z else ()))
                        break
                        
            # Calculate centroid y-coordinate
            centroid_y = sum(coord[1] for coord in node_coords) / len(node_coords)
            
            # Assign to layer
            for i, height in enumerate(layer_heights):
                if centroid_y <= height:
                    layer_elements[i].append(elem_id)
                    break
            else:
                # Element above all specified heights - assign to top layer
                layer_elements[-1].append(elem_id)
                
        # Create element sets
        for i, elements in enumerate(layer_elements):
            if elements:
                set_name = f"LAYER_{i+1}"
                self.element_sets[set_name] = elements
                print(f"Created element set {set_name}: {len(elements)} elements")
                
    def write_input_file(self, filename, analysis_type='2D_LAYERED'):
        """
        Write complete Abaqus input file.
        
        Parameters:
        -----------
        filename : str
            Output filename (.inp)
        analysis_type : str
            '2D_LAYERED', '3D_LAYERED', '2D_GRADED', '3D_GRADED'
        """
        with open(filename, 'w') as f:
            self._write_header(f)
            self._write_nodes(f)
            self._write_elements(f)
            self._write_node_sets(f)
            self._write_element_sets(f)
            self._write_materials(f)
            self._write_sections(f)
            self._write_section_assignments(f, analysis_type)
            
            if 'GRADED' in analysis_type:
                self._write_analytical_field(f)
                self._write_initial_conditions(f)
                
            self._write_step(f)
            self._write_boundary_conditions(f)
            self._write_output_requests(f)
            self._write_end_step(f)
            
        print(f"Input file written: {filename}")
        
    def _write_header(self, f):
        """Write file header."""
        f.write("*HEADING\n")
        f.write(f"** Abaqus Acoustic Transmission Loss Simulation: {self.model_name}\n")
        f.write("** Generated by AbaqusInputGenerator\n")
        f.write("** Units: SI (m-kg-s-Pa)\n")
        f.write("**\n")
        
    def _write_nodes(self, f):
        """Write node definitions."""
        f.write("*NODE\n")
        for node_data in self.nodes:
            if len(node_data) == 3:  # 2D
                f.write(f"{node_data[0]}, {node_data[1]:.6f}, {node_data[2]:.6f}\n")
            else:  # 3D
                f.write(f"{node_data[0]}, {node_data[1]:.6f}, {node_data[2]:.6f}, {node_data[3]:.6f}\n")
                
    def _write_elements(self, f):
        """Write element definitions."""
        f.write("*ELEMENT, TYPE=AC2D4\n" if self.elements[0][1] == 'AC2D4' else "*ELEMENT, TYPE=AC3D8\n")
        
        for elem_id, elem_type, connectivity in self.elements:
            conn_str = ', '.join(map(str, connectivity))
            f.write(f"{elem_id}, {conn_str}\n")
            
    def _write_node_sets(self, f):
        """Write node set definitions."""
        for set_name, nodes in self.node_sets.items():
            f.write(f"*NSET, NSET={set_name}\n")
            
            # Write nodes in groups of 16 per line
            for i in range(0, len(nodes), 16):
                node_group = nodes[i:i+16]
                f.write(', '.join(map(str, node_group)))
                if i + 16 < len(nodes):
                    f.write(',')
                f.write('\n')
                
    def _write_element_sets(self, f):
        """Write element set definitions."""
        for set_name, elements in self.element_sets.items():
            f.write(f"*ELSET, ELSET={set_name}\n")
            
            # Write elements in groups of 16 per line
            for i in range(0, len(elements), 16):
                elem_group = elements[i:i+16]
                f.write(', '.join(map(str, elem_group)))
                if i + 16 < len(elements):
                    f.write(',')
                f.write('\n')
                
    def _write_materials(self, f):
        """Write material definitions."""
        for mat_name, properties in self.materials.items():
            f.write(f"*MATERIAL, NAME={mat_name}\n")
            
            if properties.get('field_dependent', False):
                # Graded material with field dependencies
                f.write("*DENSITY, DEPENDENCIES=1\n")
                for field_val, density in properties['density_profile']:
                    f.write(f"{density:.3f}, {field_val:.3f}\n")
                    
                f.write("*BULK MODULUS, DEPENDENCIES=1\n")
                for field_val, bulk_mod in properties['bulk_modulus_profile']:
                    f.write(f"{bulk_mod:.6e}, {field_val:.3f}\n")
            else:
                # Homogeneous material
                f.write("*DENSITY\n")
                f.write(f"{properties['density']:.3f},\n")
                f.write("*BULK MODULUS\n")
                f.write(f"{properties['bulk_modulus']:.6e},\n")
                
    def _write_sections(self, f):
        """Write section definitions."""
        for section_name, properties in self.sections.items():
            f.write(f"*SOLID SECTION, ELSET=ALL_ELEMENTS, MATERIAL={properties['material']}\n")
            f.write(",\n")  # Thickness (not used for acoustic elements)
            
    def _write_section_assignments(self, f, analysis_type):
        """Write section assignments."""
        if 'LAYERED' in analysis_type:
            # Assign different sections to different layers
            for i, (set_name, elements) in enumerate(self.element_sets.items()):
                if set_name.startswith('LAYER_'):
                    # Find corresponding material
                    layer_num = int(set_name.split('_')[1])
                    mat_names = list(self.materials.keys())
                    if layer_num <= len(mat_names):
                        mat_name = mat_names[layer_num - 1]
                        f.write(f"*SOLID SECTION, ELSET={set_name}, MATERIAL={mat_name}\n")
                        f.write(",\n")
        else:
            # Single section for graded material
            f.write("*SOLID SECTION, ELSET=ALL_ELEMENTS, MATERIAL=GRADED_MATERIAL\n")
            f.write(",\n")
            
    def _write_analytical_field(self, f):
        """Write analytical field for graded materials."""
        f.write("*FIELD, NAME=DEPTH_FIELD\n")
        f.write("*DEFINITION, NAME=DEPTH_FIELD\n")
        f.write("Y\n")  # Field varies with Y coordinate (depth)
        
    def _write_initial_conditions(self, f):
        """Write initial conditions for field variables."""
        f.write("*INITIAL CONDITIONS, TYPE=FIELD, VARIABLE=1\n")
        f.write("ALL_NODES, 1.0\n")  # Initial field value
        
    def _write_step(self, f):
        """Write analysis step."""
        f.write("*STEP, NAME=STEADY_STATE, NLGEOM=NO\n")
        f.write("*STEADY STATE DYNAMICS, DIRECT\n")
        f.write(f"{self.freq_start:.1f}, {self.freq_end:.1f}, {self.freq_inc:.1f}\n")
        
    def _write_boundary_conditions(self, f):
        """Write boundary conditions."""
        # Incident wave
        f.write("** Incident wave loading\n")
        f.write("*INCIDENT WAVE INTERACTION PROPERTY, NAME=PLANEWAVE\n")
        f.write("*INCIDENT WAVE FLUID PROPERTY\n")
        f.write(f"{self.ref_density:.1f}, {self.ref_sound_speed:.1f}\n")
        f.write("*INCIDENT WAVE INTERACTION, NAME=INC1, PROPERTY=PLANEWAVE\n")
        f.write("INLET, 1., 0., 0.\n")  # Direction cosines
        
        # Non-reflecting boundaries
        f.write("** Non-reflecting boundaries\n")
        f.write("*IMPEDANCE, TYPE=NONREFLECTING\n")
        f.write("OUTLET,\n")
        f.write("*IMPEDANCE, TYPE=NONREFLECTING\n")
        f.write("LATERAL,\n")
        
    def _write_output_requests(self, f):
        """Write output requests."""
        f.write("** Output requests\n")
        f.write("*OUTPUT, FIELD, FREQUENCY=1\n")
        f.write("*NODE OUTPUT\n")
        f.write("P\n")
        
        f.write("*OUTPUT, HISTORY, FREQUENCY=1\n")
        f.write("*NODE PRINT, NSET=PROBE_IN\n")
        f.write("P\n")
        f.write("*NODE PRINT, NSET=PROBE_OUT\n")
        f.write("P\n")
        
    def _write_end_step(self, f):
        """Write end step."""
        f.write("*END STEP\n")


# Example usage functions
def generate_2d_layered_input():
    """Generate 2D layered medium input file."""
    print("Generating 2D layered medium input file...")
    
    # Create generator
    gen = AbaqusInputGenerator('LayeredMedium2D')
    
    # Set analysis parameters
    gen.freq_start = 100.0
    gen.freq_end = 3000.0
    gen.freq_inc = 50.0
    
    # Generate mesh
    length, height = 10.0, 4.0
    nx, ny = 100, 40  # Elements
    gen.generate_2d_rectangular_mesh(length, height, nx, ny)
    
    # Define layers
    layers = [
        {'name': 'WATER_BOTTOM', 'density': 1030.0, 'bulk_modulus': 2.4e9},
        {'name': 'WATER_TOP', 'density': 1020.0, 'bulk_modulus': 2.2e9}
    ]
    
    gen.add_layered_materials(layers)
    
    # Create layer element sets (bottom layer: 0-2m, top layer: 2-4m)
    gen.create_layered_element_sets([2.0, 4.0])
    
    # Write input file
    gen.write_input_file('layered_medium_2d.inp', '2D_LAYERED')
    
    return gen


def generate_3d_graded_input():
    """Generate 3D graded medium input file."""
    print("Generating 3D graded medium input file...")
    
    # Create generator
    gen = AbaqusInputGenerator('GradedMedium3D')
    
    # Set analysis parameters
    gen.freq_start = 200.0
    gen.freq_end = 2000.0
    gen.freq_inc = 100.0
    
    # Generate mesh
    length, height, width = 8.0, 3.0, 2.0
    nx, ny, nz = 80, 30, 20  # Elements
    gen.generate_3d_rectangular_mesh(length, height, width, nx, ny, nz)
    
    # Define graded material
    density_profile = [
        (0.0, 1020.0),    # Surface
        (1.5, 1025.0),    # Middle
        (3.0, 1030.0)     # Bottom
    ]
    
    bulk_modulus_profile = [
        (0.0, 2.2e9),     # Surface
        (1.5, 2.3e9),     # Middle
        (3.0, 2.4e9)      # Bottom
    ]
    
    gen.add_graded_material('GRADED_MATERIAL', density_profile, bulk_modulus_profile)
    
    # Write input file
    gen.write_input_file('graded_medium_3d.inp', '3D_GRADED')
    
    return gen


def generate_validation_case():
    """Generate simple validation case."""
    print("Generating validation case...")
    
    # Create generator
    gen = AbaqusInputGenerator('ValidationCase')
    
    # Small domain for quick validation
    length, height = 5.0, 2.0
    nx, ny = 50, 20
    gen.generate_2d_rectangular_mesh(length, height, nx, ny)
    
    # Single homogeneous material (water)
    layers = [{'name': 'WATER', 'density': 1025.0, 'bulk_modulus': 2.306e9}]
    gen.add_layered_materials(layers)
    
    # All elements in one set
    all_elements = [elem[0] for elem in gen.elements]
    gen.element_sets['ALL_ELEMENTS'] = all_elements
    
    # High frequency resolution for validation
    gen.freq_start = 500.0
    gen.freq_end = 1500.0
    gen.freq_inc = 10.0
    
    # Write input file
    gen.write_input_file('validation_case.inp', '2D_LAYERED')
    
    return gen


if __name__ == "__main__":
    print("Abaqus Input File Generator")
    print("=" * 40)
    
    try:
        # Generate example input files
        gen1 = generate_2d_layered_input()
        gen2 = generate_3d_graded_input()
        gen3 = generate_validation_case()
        
        print("\n" + "=" * 40)
        print("INPUT FILES GENERATED SUCCESSFULLY")
        print("=" * 40)
        print("Generated files:")
        print("- layered_medium_2d.inp (2D layered)")
        print("- graded_medium_3d.inp (3D graded)")
        print("- validation_case.inp (validation)")
        print("\nTo run in Abaqus/Standard:")
        print("abaqus job=layered_medium_2d input=layered_medium_2d.inp")
        
    except Exception as e:
        print(f"Error generating input files: {e}")
        import traceback
        traceback.print_exc()