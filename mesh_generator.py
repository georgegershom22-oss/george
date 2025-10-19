#!/usr/bin/env python
"""
Mesh Generator for Abaqus Acoustic Waveguide

Generates structured 2D mesh for acoustic transmission loss simulations.
Outputs Abaqus input file format with nodes, elements, and node/element sets.

Usage:
    python mesh_generator.py --length 100 --depth 50 --size 0.25 --output mesh.inp
"""

import argparse
import numpy as np


def generate_structured_mesh_2d(length, depth, element_size, 
                                 layer_depths=[15.0, 35.0],
                                 probe_x=[20.0, 80.0]):
    """
    Generate a structured 2D quadrilateral mesh for acoustic waveguide.
    
    Parameters:
    -----------
    length : float
        Domain length in x-direction (m)
    depth : float
        Domain depth in z-direction (m)
    element_size : float
        Target element size (m)
    layer_depths : list
        Z-coordinates of layer interfaces (m)
    probe_x : list
        X-coordinates of probe locations (m)
        
    Returns:
    --------
    mesh_data : dict
        Dictionary containing nodes, elements, and sets
    """
    
    # Calculate number of elements
    nx = int(np.ceil(length / element_size))
    nz = int(np.ceil(depth / element_size))
    
    # Adjust element size for exact fit
    dx = length / nx
    dz = depth / nz
    
    print(f"Mesh generation:")
    print(f"  Domain: {length} m x {depth} m")
    print(f"  Elements: {nx} x {nz} = {nx*nz}")
    print(f"  Nodes: {nx+1} x {nz+1} = {(nx+1)*(nz+1)}")
    print(f"  Element size: {dx:.4f} m x {dz:.4f} m")
    
    # Generate nodes
    nodes = {}
    node_id = 1
    
    for j in range(nz + 1):
        z = j * dz
        for i in range(nx + 1):
            x = i * dx
            nodes[node_id] = (x, z)
            node_id += 1
    
    # Generate elements (AC2D4 - 4-node quads)
    elements = {}
    elem_id = 1
    
    for j in range(nz):
        for i in range(nx):
            # Node connectivity (counterclockwise from bottom-left)
            n1 = j * (nx + 1) + i + 1
            n2 = n1 + 1
            n3 = n2 + (nx + 1)
            n4 = n1 + (nx + 1)
            
            elements[elem_id] = (n1, n2, n3, n4)
            elem_id += 1
    
    # Determine element sets for layers
    layer_elements = {}
    
    for elem_id, (n1, n2, n3, n4) in elements.items():
        # Get element centroid z-coordinate
        z1 = nodes[n1][1]
        z4 = nodes[n4][1]
        z_cent = (z1 + z4) / 2.0
        
        # Assign to layer
        if z_cent < layer_depths[0]:
            layer_name = 'LAYER1'
        elif z_cent < layer_depths[1]:
            layer_name = 'LAYER2'
        else:
            layer_name = 'LAYER3'
        
        if layer_name not in layer_elements:
            layer_elements[layer_name] = []
        layer_elements[layer_name].append(elem_id)
    
    # Generate node sets for boundaries
    node_sets = {}
    
    # Inlet (x=0)
    node_sets['INLET_NODES'] = [j * (nx + 1) + 1 for j in range(nz + 1)]
    
    # Outlet (x=length)
    node_sets['OUTLET_NODES'] = [j * (nx + 1) + (nx + 1) for j in range(nz + 1)]
    
    # Bottom (z=0)
    node_sets['BOTTOM_NODES'] = list(range(1, nx + 2))
    
    # Top (z=depth)
    node_sets['TOP_NODES'] = list(range(nz * (nx + 1) + 1, (nz + 1) * (nx + 1) + 1))
    
    # Probe locations
    for idx, x_probe in enumerate(probe_x):
        i_probe = int(np.round(x_probe / dx))
        probe_name = f'PROBE_{idx+1}'
        node_sets[probe_name] = [j * (nx + 1) + i_probe + 1 for j in range(nz + 1)]
    
    # Also create named sets for IN and OUT
    i_in = int(np.round(probe_x[0] / dx))
    i_out = int(np.round(probe_x[1] / dx))
    node_sets['PROBE_IN'] = [j * (nx + 1) + i_in + 1 for j in range(nz + 1)]
    node_sets['PROBE_OUT'] = [j * (nx + 1) + i_out + 1 for j in range(nz + 1)]
    
    # Generate element-based surfaces for boundary conditions
    surfaces = {}
    
    # Inlet surface (S4 = left face of quad)
    surfaces['INLET_SURF'] = []
    for j in range(nz):
        elem_id = j * nx + 1
        surfaces['INLET_SURF'].append((elem_id, 'S4'))
    
    # Outlet surface (S2 = right face of quad)
    surfaces['OUTLET_SURF'] = []
    for j in range(nz):
        elem_id = (j + 1) * nx
        surfaces['OUTLET_SURF'].append((elem_id, 'S2'))
    
    # Bottom surface (S3 = bottom face of quad)
    surfaces['BOTTOM_SURF'] = []
    for i in range(nx):
        elem_id = i + 1
        surfaces['BOTTOM_SURF'].append((elem_id, 'S3'))
    
    # Top surface (S1 = top face of quad)
    surfaces['TOP_SURF'] = []
    for i in range(nx):
        elem_id = nz * nx - nx + i + 1
        surfaces['TOP_SURF'].append((elem_id, 'S1'))
    
    return {
        'nodes': nodes,
        'elements': elements,
        'layer_elements': layer_elements,
        'node_sets': node_sets,
        'surfaces': surfaces,
        'dimensions': {'length': length, 'depth': depth, 'nx': nx, 'nz': nz, 'dx': dx, 'dz': dz}
    }


def write_abaqus_mesh(mesh_data, filename, include_materials=True):
    """
    Write mesh data to Abaqus input file format.
    
    Parameters:
    -----------
    mesh_data : dict
        Mesh data from generate_structured_mesh_2d
    filename : str
        Output .inp filename
    include_materials : bool
        Whether to include material definitions
    """
    
    with open(filename, 'w') as f:
        f.write("*HEADING\n")
        f.write("** Acoustic Mesh for Transmission Loss Simulation\n")
        f.write(f"** Generated by mesh_generator.py\n")
        f.write(f"** Domain: {mesh_data['dimensions']['length']} m x {mesh_data['dimensions']['depth']} m\n")
        f.write(f"** Mesh: {mesh_data['dimensions']['nx']} x {mesh_data['dimensions']['nz']} elements\n")
        f.write("**\n")
        
        # Write nodes
        f.write("** ============================================================================\n")
        f.write("** NODES\n")
        f.write("** ============================================================================\n")
        f.write("*NODE\n")
        for node_id, (x, z) in sorted(mesh_data['nodes'].items()):
            f.write(f"{node_id}, {x:.6f}, {z:.6f}\n")
        
        # Write elements
        f.write("**\n")
        f.write("** ============================================================================\n")
        f.write("** ELEMENTS (AC2D4 - 4-node acoustic quadrilateral)\n")
        f.write("** ============================================================================\n")
        f.write("*ELEMENT, TYPE=AC2D4, ELSET=ALL_ELEMENTS\n")
        for elem_id, connectivity in sorted(mesh_data['elements'].items()):
            f.write(f"{elem_id}, {connectivity[0]}, {connectivity[1]}, {connectivity[2]}, {connectivity[3]}\n")
        
        # Write layer element sets
        f.write("**\n")
        f.write("** ============================================================================\n")
        f.write("** ELEMENT SETS FOR LAYERS\n")
        f.write("** ============================================================================\n")
        for layer_name, elem_list in sorted(mesh_data['layer_elements'].items()):
            f.write(f"*ELSET, ELSET={layer_name}\n")
            # Write in groups of 16
            for i in range(0, len(elem_list), 16):
                chunk = elem_list[i:i+16]
                f.write(", ".join(map(str, chunk)))
                if i + 16 < len(elem_list):
                    f.write(",\n")
                else:
                    f.write("\n")
        
        # Write node sets
        f.write("**\n")
        f.write("** ============================================================================\n")
        f.write("** NODE SETS\n")
        f.write("** ============================================================================\n")
        for set_name, node_list in sorted(mesh_data['node_sets'].items()):
            f.write(f"*NSET, NSET={set_name}\n")
            # Write in groups of 16
            for i in range(0, len(node_list), 16):
                chunk = node_list[i:i+16]
                f.write(", ".join(map(str, chunk)))
                if i + 16 < len(node_list):
                    f.write(",\n")
                else:
                    f.write("\n")
        
        # Write surfaces
        f.write("**\n")
        f.write("** ============================================================================\n")
        f.write("** SURFACES\n")
        f.write("** ============================================================================\n")
        for surf_name, surf_list in sorted(mesh_data['surfaces'].items()):
            f.write(f"*SURFACE, NAME={surf_name}, TYPE=ELEMENT\n")
            for elem_id, face in surf_list:
                f.write(f"{elem_id}, {face}\n")
        
        # Optionally write material definitions
        if include_materials:
            f.write("**\n")
            f.write("** ============================================================================\n")
            f.write("** MATERIAL DEFINITIONS\n")
            f.write("** ============================================================================\n")
            f.write("**\n")
            f.write("** LAYER 1: Surface water (warm, less dense)\n")
            f.write("*MATERIAL, NAME=WATER_SURFACE\n")
            f.write("*DENSITY\n")
            f.write("1023.0,\n")
            f.write("*BULK MODULUS\n")
            f.write("2.364e9,\n")
            f.write("**\n")
            f.write("** LAYER 2: Thermocline\n")
            f.write("*MATERIAL, NAME=WATER_THERMOCLINE\n")
            f.write("*DENSITY\n")
            f.write("1026.0,\n")
            f.write("*BULK MODULUS\n")
            f.write("2.278e9,\n")
            f.write("**\n")
            f.write("** LAYER 3: Deep water (cold, dense)\n")
            f.write("*MATERIAL, NAME=WATER_DEEP\n")
            f.write("*DENSITY\n")
            f.write("1028.0,\n")
            f.write("*BULK MODULUS\n")
            f.write("2.221e9,\n")
            f.write("**\n")
            f.write("** ============================================================================\n")
            f.write("** SECTION ASSIGNMENTS\n")
            f.write("** ============================================================================\n")
            f.write("*SOLID SECTION, ELSET=LAYER1, MATERIAL=WATER_SURFACE\n")
            f.write("*SOLID SECTION, ELSET=LAYER2, MATERIAL=WATER_THERMOCLINE\n")
            f.write("*SOLID SECTION, ELSET=LAYER3, MATERIAL=WATER_DEEP\n")
        
        f.write("**\n")
        f.write("** End of mesh definition\n")
        f.write("**\n")
    
    print(f"\nMesh written to: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate structured 2D mesh for Abaqus acoustic simulation'
    )
    parser.add_argument('--length', type=float, default=100.0,
                       help='Domain length in x-direction (m), default=100')
    parser.add_argument('--depth', type=float, default=50.0,
                       help='Domain depth in z-direction (m), default=50')
    parser.add_argument('--size', type=float, default=0.25,
                       help='Element size (m), default=0.25')
    parser.add_argument('--layer-depths', type=float, nargs=2, default=[15.0, 35.0],
                       help='Z-coordinates of layer interfaces (m), default=[15, 35]')
    parser.add_argument('--probe-x', type=float, nargs=2, default=[20.0, 80.0],
                       help='X-coordinates of probe locations (m), default=[20, 80]')
    parser.add_argument('--output', type=str, default='acoustic_mesh.inp',
                       help='Output filename, default=acoustic_mesh.inp')
    parser.add_argument('--no-materials', action='store_true',
                       help='Do not include material definitions')
    
    args = parser.parse_args()
    
    # Generate mesh
    mesh_data = generate_structured_mesh_2d(
        length=args.length,
        depth=args.depth,
        element_size=args.size,
        layer_depths=args.layer_depths,
        probe_x=args.probe_x
    )
    
    # Write to file
    write_abaqus_mesh(mesh_data, args.output, include_materials=not args.no_materials)
    
    print("\nMesh generation completed successfully!")
    print(f"\nTo use this mesh in your simulation:")
    print(f"  1. Include it in your main .inp: *INCLUDE, INPUT={args.output}")
    print(f"  2. Or copy the contents into your main input file")


if __name__ == '__main__':
    main()
