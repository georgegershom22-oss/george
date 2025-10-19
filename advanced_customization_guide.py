#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Advanced Customization Guide for Abaqus Acoustic Simulations
==============================================================

This file demonstrates advanced modifications and customizations
of the acoustic transmission loss simulation framework.

Topics covered:
1. Custom density/bulk modulus profiles (arbitrary functions)
2. Frequency-dependent material properties
3. Anisotropic or directionally-dependent stratification
4. Adding acoustic sources at arbitrary locations
5. Extracting additional outputs (particle velocity, intensity)
6. Coupling with structural elements (elastic walls)
7. Multi-domain simulations (separate fluid regions)
8. Custom post-processing (mode decomposition, far-field patterns)
"""

import numpy as np
from abaqus import *
from abaqusConstants import *

# ============================================================================
# 1. CUSTOM STRATIFICATION PROFILES
# ============================================================================

def create_custom_density_profile(z, profile_type='arctangent'):
    """
    Create arbitrary density profiles
    
    Args:
        z: vertical coordinate [m]
        profile_type: string specifying profile shape
    
    Returns:
        density at z [kg/m³]
    """
    
    if profile_type == 'arctangent':
        # Sharp thermocline with smooth transition
        rho_deep = 1028.0
        rho_surface = 1020.0
        z_thermocline = 50.0  # meters
        thickness = 10.0      # transition thickness
        
        transition = 0.5 * (1.0 + np.tanh((z - z_thermocline) / thickness))
        rho = rho_deep + (rho_surface - rho_deep) * transition
        
    elif profile_type == 'bilinear':
        # Piecewise linear with kink
        if z < 30.0:
            rho = 1028.0 - 0.1 * z  # Gradient in deep layer
        else:
            rho = 1025.0 - 0.5 * (z - 30.0)  # Steeper gradient above
    
    elif profile_type == 'sinusoidal':
        # Periodic stratification (internal waves)
        rho_mean = 1024.0
        amplitude = 3.0
        wavelength = 20.0
        rho = rho_mean + amplitude * np.sin(2 * np.pi * z / wavelength)
    
    elif profile_type == 'exponential_decay':
        # Exponential decay from bottom
        rho_bottom = 1028.0
        rho_infinity = 1020.0
        decay_length = 30.0
        rho = rho_infinity + (rho_bottom - rho_infinity) * np.exp(-z / decay_length)
    
    return rho


def discretize_profile_to_layers(z_range, n_layers, profile_func):
    """
    Convert continuous profile to layered approximation
    
    Args:
        z_range: (z_min, z_max) tuple
        n_layers: number of discrete layers
        profile_func: function(z) -> (rho, K)
    
    Returns:
        layers: list of (z_bottom, z_top, rho, K)
    """
    z_min, z_max = z_range
    z_interfaces = np.linspace(z_min, z_max, n_layers + 1)
    
    layers = []
    for i in range(n_layers):
        z_bottom = z_interfaces[i]
        z_top = z_interfaces[i + 1]
        z_mid = (z_bottom + z_top) / 2.0
        
        # Evaluate properties at layer midpoint
        rho, K = profile_func(z_mid)
        
        layers.append((z_bottom, z_top, rho, K))
    
    return layers


def example_realistic_ocean_profile(z):
    """
    Realistic ocean sound speed profile with mixed layer, thermocline, deep layer
    
    Based on typical mid-latitude ocean:
    - Surface mixed layer: 0-50 m, warm (1520 m/s)
    - Thermocline: 50-200 m, rapid decrease to 1480 m/s
    - Deep isothermal: 200+ m, gradual increase due to pressure (1500 m/s)
    """
    
    # Temperature-salinity-pressure model (simplified)
    if z > 200:
        # Deep layer (pressure effect dominates)
        c = 1480.0 + 0.1 * (z - 200.0)  # ~0.1 m/s per meter depth
    elif z > 50:
        # Thermocline (sharp gradient)
        c = 1520.0 - 40.0 * (z - 50.0) / 150.0
    else:
        # Surface mixed layer
        c = 1520.0
    
    # Convert to rho and K (assume constant salinity)
    # Typical: rho increases with depth (temperature effect)
    if z > 200:
        rho = 1027.0 + 0.01 * (z - 200.0)
    elif z > 50:
        rho = 1024.0 + 3.0 * (z - 50.0) / 150.0
    else:
        rho = 1024.0
    
    K = rho * c**2
    
    return rho, K


# ============================================================================
# 2. FREQUENCY-DEPENDENT PROPERTIES
# ============================================================================

def create_frequency_dependent_material(model, name, rho, K_table):
    """
    Create material with frequency-dependent bulk modulus
    
    Useful for modeling:
    - Dispersion
    - Relaxation processes (e.g., boric acid in seawater)
    - Bubbly media
    
    Args:
        model: Abaqus model object
        name: material name
        rho: density (constant)
        K_table: list of (K, frequency) tuples
    """
    
    mat = model.Material(name=name)
    mat.Density(table=((rho,),))
    
    # Frequency-dependent bulk modulus
    mat.Acoustic(
        acousticMediumFormulation=BULK_MODULUS,
        frequencyDependency=ON,
        bulkTable=tuple(K_table)
    )
    
    return mat


def seawater_relaxation_model(f):
    """
    Frequency-dependent absorption in seawater (boric acid + MgSO4 relaxation)
    
    Args:
        f: frequency [Hz]
    
    Returns:
        K_eff: effective complex bulk modulus [Pa]
    """
    # Simplified model (see Francois-Garrison for full treatment)
    K0 = 2.31e9  # Real part (compressibility)
    
    # Relaxation frequencies
    f1 = 1000.0   # Hz (boric acid)
    f2 = 100000.0 # Hz (MgSO4)
    
    # Loss factors
    eta1 = 0.001
    eta2 = 0.0005
    
    # Frequency-dependent loss
    loss_factor = eta1 * f**2 / (f**2 + f1**2) + eta2 * f**2 / (f**2 + f2**2)
    
    # Complex bulk modulus: K = K0 * (1 - i*loss_factor)
    K_real = K0
    K_imag = -K0 * loss_factor
    
    return complex(K_real, K_imag)


# ============================================================================
# 3. MULTIPLE SOURCES AND RECEIVERS
# ============================================================================

def create_source_array(model, assembly, instance, source_positions, frequencies):
    """
    Create multiple acoustic sources (for beamforming, array processing)
    
    Args:
        source_positions: list of (x, y, z) tuples
        frequencies: array of frequencies for each source (for phased arrays)
    """
    
    for i, pos in enumerate(source_positions):
        x, y, z = pos
        
        # Find nodes near this position
        nodes = []
        tolerance = 0.1  # meters
        for node in instance.nodes:
            dist = np.sqrt((node.coordinates[0]-x)**2 + 
                          (node.coordinates[1]-y)**2 + 
                          (node.coordinates[2]-z)**2)
            if dist < tolerance:
                nodes.append(node)
        
        # Create node set for this source
        set_name = 'Source_{}'.format(i+1)
        assembly.Set(nodes=nodes, name=set_name)
        
        # Apply concentrated force (for monopole source)
        # In steady-state dynamics, this becomes pressure boundary condition
        region = assembly.sets[set_name]
        
        # Note: For true point sources, use *CLOAD or *DLOAD
        # For surface sources, use *DSLOAD


def create_receiver_array(assembly, instance, receiver_positions):
    """
    Create receiver array for directional analysis
    
    Args:
        receiver_positions: list of (x, y, z) tuples
    
    Returns:
        receiver_sets: dict mapping receiver_id -> node set name
    """
    
    receiver_sets = {}
    
    for i, pos in enumerate(receiver_positions):
        x, y, z = pos
        
        # Find closest node
        min_dist = float('inf')
        closest_node = None
        
        for node in instance.nodes:
            dist = np.sqrt((node.coordinates[0]-x)**2 + 
                          (node.coordinates[1]-y)**2 + 
                          (node.coordinates[2]-z)**2)
            if dist < min_dist:
                min_dist = dist
                closest_node = node
        
        # Create node set
        set_name = 'Receiver_{}'.format(i+1)
        assembly.Set(nodes=[closest_node], name=set_name)
        receiver_sets[i+1] = set_name
    
    return receiver_sets


# ============================================================================
# 4. ACOUSTIC-STRUCTURE COUPLING
# ============================================================================

def add_elastic_wall(model, wall_params):
    """
    Add elastic structural elements coupled to acoustic domain
    
    Useful for:
    - Vibrating walls/membranes
    - Acoustic liners
    - Fluid-structure interaction
    
    Args:
        wall_params: dict with wall properties
    """
    
    # Create structural material
    mat_wall = model.Material(name='Wall_Elastic')
    mat_wall.Density(table=((wall_params['density'],),))
    mat_wall.Elastic(table=((wall_params['E'], wall_params['nu']),))
    
    # Add damping (for absorbing walls)
    if 'damping' in wall_params:
        mat_wall.Damping(alpha=wall_params['damping']['alpha'],
                         beta=wall_params['damping']['beta'])
    
    # Create structural section
    model.HomogeneousShellSection(
        name='Section_Wall',
        material='Wall_Elastic',
        thickness=wall_params['thickness']
    )
    
    # Note: In full simulation, you would:
    # 1. Create separate part for wall
    # 2. Assign structural elements (S4, S8R, etc.)
    # 3. Define acoustic-structural interface using *TIE or contact
    # 4. Specify coupling in step definition


def create_acoustic_structural_interface(model, assembly):
    """
    Create coupling between acoustic and structural domains
    """
    
    # Define surfaces at interface
    # acoustic_surface = ...
    # structural_surface = ...
    
    # Create interaction
    # model.SurfaceToSurfaceContactStd(
    #     name='Acoustic_Structural_Coupling',
    #     createStepName='Initial',
    #     master=structural_surface,
    #     slave=acoustic_surface,
    #     sliding=FINITE,
    #     interactionProperty='...'
    # )
    
    pass  # Placeholder for full implementation


# ============================================================================
# 5. ADVANCED POST-PROCESSING
# ============================================================================

def extract_particle_velocity(odb, step_name, frame_index):
    """
    Extract particle velocity from acoustic pressure field
    
    v = (1/(i*omega*rho)) * grad(p)
    
    Args:
        odb: ODB object
        step_name: step name
        frame_index: frame index
    
    Returns:
        velocity field (complex)
    """
    
    step = odb.steps[step_name]
    frame = step.frames[frame_index]
    
    # Get pressure field
    pressure = frame.fieldOutputs['POR']
    
    # Compute gradient (requires custom implementation or UVARM)
    # This is non-trivial in Abaqus post-processing
    # Typically done via:
    # 1. User subroutine UVARM to compute in analysis
    # 2. External script using finite differences
    # 3. Analytical solution for simple geometries
    
    pass  # Placeholder


def compute_acoustic_intensity(p_real, p_imag, v_real, v_imag):
    """
    Compute time-averaged acoustic intensity
    
    I = 0.5 * Re(p * conj(v))
    
    Args:
        p_real, p_imag: pressure (real and imaginary parts)
        v_real, v_imag: velocity (real and imaginary parts)
    
    Returns:
        intensity [W/m²]
    """
    
    # Complex conjugate: conj(v) = v_real - i*v_imag
    I_real = 0.5 * (p_real * v_real + p_imag * v_imag)
    I_imag = 0.5 * (p_imag * v_real - p_real * v_imag)
    
    # Magnitude (for total intensity)
    I_magnitude = np.sqrt(I_real**2 + I_imag**2)
    
    return I_real, I_imag, I_magnitude


def modal_decomposition(pressure_field, z_coords, K_list):
    """
    Decompose pressure field into normal modes (Pekeris waveguide)
    
    Useful for:
    - Understanding propagation mechanisms
    - Identifying trapped vs. leaky modes
    - Computing modal TL
    
    Args:
        pressure_field: complex pressure at discrete z locations
        z_coords: vertical coordinates
        K_list: list of modal wavenumbers (from dispersion relation)
    
    Returns:
        mode_amplitudes: complex amplitudes of each mode
    """
    
    # Mode shapes (eigenfunctions)
    mode_shapes = []
    for k in K_list:
        # Example: sine modes in rigid-rigid waveguide
        mode_shape = np.sin(k * z_coords)
        mode_shapes.append(mode_shape)
    
    mode_shapes = np.array(mode_shapes).T  # Shape: (n_z, n_modes)
    
    # Least-squares fit: p(z) ≈ Σ A_m * ψ_m(z)
    mode_amplitudes, _, _, _ = np.linalg.lstsq(mode_shapes, pressure_field, rcond=None)
    
    return mode_amplitudes


# ============================================================================
# 6. PARAMETRIC STUDIES
# ============================================================================

def run_parametric_study(param_ranges, base_config):
    """
    Automated parametric study (varies density, frequency, etc.)
    
    Args:
        param_ranges: dict of parameter names and ranges
        base_config: baseline configuration
    
    Example:
        param_ranges = {
            'freq_end': [2000, 3000, 5000],
            'rho_bottom': [1020, 1025, 1030]
        }
    """
    
    import itertools
    
    # Generate all combinations
    param_names = list(param_ranges.keys())
    param_values = [param_ranges[name] for name in param_names]
    
    results = []
    
    for combo in itertools.product(*param_values):
        # Create modified config
        config = base_config.copy()
        
        for name, value in zip(param_names, combo):
            setattr(config, name, value)
        
        # Run simulation
        print("Running case: {}".format(dict(zip(param_names, combo))))
        
        # Generate model, run job, post-process
        # ... (call main simulation functions)
        
        # Store results
        # results.append({'params': combo, 'TL': ..., 'alpha': ...})
    
    return results


# ============================================================================
# 7. VALIDATION UTILITIES
# ============================================================================

def compare_with_analytical_solution(numerical_TL, analytical_TL, tolerance=1.0):
    """
    Validate numerical results against analytical solution
    
    Args:
        numerical_TL: array of TL from Abaqus
        analytical_TL: array of TL from theory
        tolerance: acceptable difference [dB]
    
    Returns:
        validation report
    """
    
    difference = np.abs(numerical_TL - analytical_TL)
    max_error = np.max(difference)
    mean_error = np.mean(difference)
    rmse = np.sqrt(np.mean(difference**2))
    
    report = {
        'max_error': max_error,
        'mean_error': mean_error,
        'rmse': rmse,
        'passed': max_error < tolerance
    }
    
    print("Validation Report:")
    print("  Max error:  {:.3f} dB".format(max_error))
    print("  Mean error: {:.3f} dB".format(mean_error))
    print("  RMSE:       {:.3f} dB".format(rmse))
    print("  Status: {}".format("PASS" if report['passed'] else "FAIL"))
    
    return report


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == '__main__':
    
    print("Advanced Customization Guide - Usage Examples")
    print("=" * 60)
    
    # Example 1: Custom density profile
    print("\n1. Custom Density Profile (Arctangent Thermocline)")
    z_test = np.linspace(0, 100, 101)
    rho_test = [create_custom_density_profile(z, 'arctangent') for z in z_test]
    print("   z=0 m:   rho={:.2f} kg/m³".format(rho_test[0]))
    print("   z=50 m:  rho={:.2f} kg/m³".format(rho_test[50]))
    print("   z=100 m: rho={:.2f} kg/m³".format(rho_test[100]))
    
    # Example 2: Discretize continuous profile
    print("\n2. Discretize Profile to 5 Layers")
    layers = discretize_profile_to_layers(
        (0, 100), 5, 
        lambda z: (create_custom_density_profile(z, 'linear'), 2.3e9)
    )
    for i, layer in enumerate(layers):
        z_bot, z_top, rho, K = layer
        print("   Layer {}: z=[{:.1f}, {:.1f}] m, rho={:.1f} kg/m³".format(
            i+1, z_bot, z_top, rho))
    
    # Example 3: Frequency-dependent material
    print("\n3. Frequency-Dependent Material (Seawater Relaxation)")
    freqs = [100, 1000, 10000, 100000]
    for f in freqs:
        K_complex = seawater_relaxation_model(f)
        loss_factor = np.abs(K_complex.imag / K_complex.real)
        print("   f={:6.0f} Hz: loss factor = {:.6f}".format(f, loss_factor))
    
    print("\n" + "=" * 60)
    print("See function docstrings for detailed usage instructions.")
