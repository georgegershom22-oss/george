#!/usr/bin/env python
"""
Mesh Validation and Quality Check for Abaqus Acoustic Simulations

Analyzes mesh quality, resolution, and suitability for acoustic analysis.

Usage:
    python validate_mesh.py acoustic_transmission_loss.inp
"""

import sys
import re
import numpy as np


def parse_abaqus_inp(filename):
    """
    Parse Abaqus input file to extract nodes and elements.
    
    Returns:
    --------
    mesh_info : dict
        Dictionary with nodes, elements, and materials
    """
    
    nodes = {}
    elements = {}
    materials = {}
    current_section = None
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('**'):
                continue
            
            # Detect sections
            if line.upper().startswith('*NODE'):
                current_section = 'nodes'
                continue
            elif line.upper().startswith('*ELEMENT'):
                current_section = 'elements'
                continue
            elif line.upper().startswith('*MATERIAL'):
                match = re.search(r'NAME=(\w+)', line, re.IGNORECASE)
                if match:
                    mat_name = match.group(1)
                    materials[mat_name] = {}
                    current_section = f'material_{mat_name}'
                continue
            elif line.startswith('*'):
                current_section = None
                
                # Extract material properties
                if line.upper().startswith('*DENSITY'):
                    current_section = 'density'
                elif line.upper().startswith('*BULK MODULUS'):
                    current_section = 'bulk_modulus'
                continue
            
            # Parse data based on current section
            if current_section == 'nodes':
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 3:
                    try:
                        node_id = int(parts[0])
                        x = float(parts[1])
                        y = float(parts[2])
                        nodes[node_id] = np.array([x, y])
                    except ValueError:
                        pass
            
            elif current_section == 'elements':
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 5:
                    try:
                        elem_id = int(parts[0])
                        connectivity = [int(p) for p in parts[1:5]]
                        elements[elem_id] = connectivity
                    except ValueError:
                        pass
            
            elif current_section == 'density':
                try:
                    density = float(line.split(',')[0])
                    # Store in last material
                    if materials:
                        last_mat = list(materials.keys())[-1]
                        materials[last_mat]['density'] = density
                except ValueError:
                    pass
            
            elif current_section == 'bulk_modulus':
                try:
                    bulk_mod = float(line.split(',')[0])
                    if materials:
                        last_mat = list(materials.keys())[-1]
                        materials[last_mat]['bulk_modulus'] = bulk_mod
                except ValueError:
                    pass
    
    return {
        'nodes': nodes,
        'elements': elements,
        'materials': materials
    }


def compute_element_quality(nodes, elements):
    """
    Compute element quality metrics.
    
    Returns:
    --------
    quality : dict
        Dictionary with quality metrics
    """
    
    areas = []
    aspect_ratios = []
    edge_lengths = []
    
    for elem_id, connectivity in elements.items():
        # Get node coordinates
        n1, n2, n3, n4 = [nodes[nid] for nid in connectivity]
        
        # Compute area (shoelace formula)
        coords = np.array([n1, n2, n3, n4])
        x = coords[:, 0]
        y = coords[:, 1]
        area = 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
        areas.append(area)
        
        # Compute edge lengths
        edges = [
            np.linalg.norm(n2 - n1),
            np.linalg.norm(n3 - n2),
            np.linalg.norm(n4 - n3),
            np.linalg.norm(n1 - n4)
        ]
        edge_lengths.extend(edges)
        
        # Aspect ratio (max edge / min edge)
        aspect_ratio = max(edges) / min(edges)
        aspect_ratios.append(aspect_ratio)
    
    return {
        'areas': np.array(areas),
        'aspect_ratios': np.array(aspect_ratios),
        'edge_lengths': np.array(edge_lengths)
    }


def validate_acoustic_resolution(edge_lengths, materials, freq_max=5000.0):
    """
    Validate mesh resolution for acoustic analysis.
    
    Parameters:
    -----------
    edge_lengths : array
        Array of element edge lengths
    materials : dict
        Material properties
    freq_max : float
        Maximum frequency (Hz)
        
    Returns:
    --------
    resolution : dict
        Resolution metrics
    """
    
    # Compute sound speeds
    sound_speeds = []
    for mat_name, props in materials.items():
        if 'density' in props and 'bulk_modulus' in props:
            rho = props['density']
            K = props['bulk_modulus']
            c = np.sqrt(K / rho)
            sound_speeds.append(c)
    
    if not sound_speeds:
        return None
    
    c_min = min(sound_speeds)
    c_max = max(sound_speeds)
    
    # Minimum wavelength
    lambda_min = c_min / freq_max
    
    # Recommended element size
    recommended_size = lambda_min / 10.0  # 10 elements per wavelength
    
    # Actual resolution
    h_avg = np.mean(edge_lengths)
    h_max = np.max(edge_lengths)
    h_min = np.min(edge_lengths)
    
    elements_per_wavelength = lambda_min / h_avg
    
    return {
        'c_min': c_min,
        'c_max': c_max,
        'lambda_min': lambda_min,
        'recommended_size': recommended_size,
        'h_avg': h_avg,
        'h_max': h_max,
        'h_min': h_min,
        'elements_per_wavelength': elements_per_wavelength,
        'is_adequate': elements_per_wavelength >= 6.0  # Conservative threshold
    }


def print_validation_report(mesh_info, quality, resolution):
    """Print comprehensive validation report."""
    
    print("="*80)
    print("ABAQUS ACOUSTIC MESH VALIDATION REPORT")
    print("="*80)
    
    # Mesh statistics
    print("\n1. MESH STATISTICS")
    print("-" * 80)
    print(f"  Total nodes:          {len(mesh_info['nodes']):>10,}")
    print(f"  Total elements:       {len(mesh_info['elements']):>10,}")
    print(f"  Materials:            {len(mesh_info['materials']):>10}")
    
    # Material properties
    print("\n2. MATERIAL PROPERTIES")
    print("-" * 80)
    print(f"  {'Material':<20} {'ρ (kg/m³)':<12} {'K (GPa)':<12} {'c (m/s)':<12}")
    print(f"  {'-'*20} {'-'*12} {'-'*12} {'-'*12}")
    
    for mat_name, props in mesh_info['materials'].items():
        if 'density' in props and 'bulk_modulus' in props:
            rho = props['density']
            K = props['bulk_modulus']
            c = np.sqrt(K / rho)
            print(f"  {mat_name:<20} {rho:<12.1f} {K/1e9:<12.3f} {c:<12.1f}")
    
    # Element quality
    print("\n3. ELEMENT QUALITY")
    print("-" * 80)
    print(f"  Element areas:")
    print(f"    Mean:               {np.mean(quality['areas']):>10.4f} m²")
    print(f"    Min:                {np.min(quality['areas']):>10.4f} m²")
    print(f"    Max:                {np.max(quality['areas']):>10.4f} m²")
    print(f"    Std dev:            {np.std(quality['areas']):>10.4f} m²")
    
    print(f"\n  Aspect ratios:")
    print(f"    Mean:               {np.mean(quality['aspect_ratios']):>10.2f}")
    print(f"    Min:                {np.min(quality['aspect_ratios']):>10.2f}")
    print(f"    Max:                {np.max(quality['aspect_ratios']):>10.2f}")
    
    bad_aspect = np.sum(quality['aspect_ratios'] > 5.0)
    if bad_aspect > 0:
        print(f"    ⚠ WARNING: {bad_aspect} elements with aspect ratio > 5.0")
    else:
        print(f"    ✓ All elements have aspect ratio ≤ 5.0")
    
    print(f"\n  Edge lengths:")
    print(f"    Mean:               {np.mean(quality['edge_lengths']):>10.4f} m")
    print(f"    Min:                {np.min(quality['edge_lengths']):>10.4f} m")
    print(f"    Max:                {np.max(quality['edge_lengths']):>10.4f} m")
    
    # Acoustic resolution
    if resolution:
        print("\n4. ACOUSTIC RESOLUTION ANALYSIS")
        print("-" * 80)
        print(f"  Sound speed range:    {resolution['c_min']:.1f} - {resolution['c_max']:.1f} m/s")
        print(f"  Minimum wavelength:   {resolution['lambda_min']:.4f} m  (at f_max = 5000 Hz)")
        print(f"  Recommended size:     {resolution['recommended_size']:.4f} m  (λ/10)")
        print(f"\n  Actual mesh:")
        print(f"    Average element size: {resolution['h_avg']:.4f} m")
        print(f"    Elements per λ_min:   {resolution['elements_per_wavelength']:.1f}")
        
        print(f"\n  Resolution check:")
        if resolution['is_adequate']:
            print(f"    ✓ ADEQUATE: Mesh resolution is sufficient for acoustic analysis")
        else:
            print(f"    ⚠ WARNING: Mesh may be too coarse for accurate results")
            print(f"              Recommend refining to h ≤ {resolution['recommended_size']:.4f} m")
    
    # Overall assessment
    print("\n5. OVERALL ASSESSMENT")
    print("-" * 80)
    
    issues = []
    warnings = []
    
    # Check for issues
    if bad_aspect > len(quality['aspect_ratios']) * 0.05:
        issues.append("More than 5% of elements have poor aspect ratio (>5)")
    
    if resolution and not resolution['is_adequate']:
        issues.append("Mesh resolution insufficient for frequency range")
    
    if not mesh_info['materials']:
        issues.append("No materials defined in input file")
    
    # Check for warnings
    if resolution and resolution['elements_per_wavelength'] < 8:
        warnings.append("Elements per wavelength < 8 (recommend ≥10 for high accuracy)")
    
    if len(mesh_info['elements']) < 1000:
        warnings.append("Mesh may be too coarse (< 1000 elements)")
    
    if issues:
        print("  ❌ ISSUES FOUND:")
        for issue in issues:
            print(f"     - {issue}")
    
    if warnings:
        print("  ⚠ WARNINGS:")
        for warning in warnings:
            print(f"     - {warning}")
    
    if not issues and not warnings:
        print("  ✓ PASSED: Mesh is suitable for acoustic analysis")
    
    print("\n" + "="*80)


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_mesh.py <input_file.inp>")
        print("\nExample:")
        print("  python validate_mesh.py acoustic_transmission_loss.inp")
        sys.exit(1)
    
    inp_file = sys.argv[1]
    
    try:
        print(f"Parsing input file: {inp_file}")
        mesh_info = parse_abaqus_inp(inp_file)
        
        print(f"Computing element quality...")
        quality = compute_element_quality(mesh_info['nodes'], mesh_info['elements'])
        
        print(f"Analyzing acoustic resolution...")
        resolution = validate_acoustic_resolution(
            quality['edge_lengths'],
            mesh_info['materials'],
            freq_max=5000.0
        )
        
        print("\n")
        print_validation_report(mesh_info, quality, resolution)
        
    except Exception as e:
        print(f"\nERROR: Validation failed!")
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
