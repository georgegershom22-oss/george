#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example Configuration: 3D Acoustic Waveguide
=============================================

Simulates 3D acoustic propagation in a stratified waveguide,
allowing for out-of-plane spreading and more realistic geometry.

Uses 3D acoustic elements (AC3D8) with vertical stratification.
Computationally more expensive but captures full 3D effects.
"""

config = {
    # Model identification
    'model_name': 'Waveguide3D_Acoustic',
    'job_name': 'waveguide_3d_tl',
    
    # Geometry
    'dimension': 3,  # 3D simulation
    'length': 80.0,  # meters (x-direction, propagation)
    'height': 40.0,  # meters (z-direction, stratification)
    'width': 30.0,   # meters (y-direction, lateral)
    
    # Frequency sweep
    'freq_start': 200.0,
    'freq_end': 2000.0,
    'freq_inc': 50.0,
    
    # Stratification
    'stratification_type': 'layered',
    
    # Layers (vertical stratification)
    'layers': [
        # Bottom layer (denser)
        (0.0,  12.0, 1027.0, 2.310e9),  # c ≈ 1500 m/s
        
        # Middle layer
        (12.0, 25.0, 1018.0, 2.282e9),  # c ≈ 1498 m/s
        
        # Top layer (lighter)
        (25.0, 40.0, 1010.0, 2.256e9),  # c ≈ 1494 m/s
    ],
    
    # Mesh (coarser for 3D to manage computational cost)
    'target_elements_per_wavelength': 10,
    
    # Probes
    'probe_in_x': 20.0,
    'probe_out_x': 60.0,  # 40 m separation
    
    # Incident wave
    'incident_density': 1020.0,
    'incident_speed': 1500.0,
    'incident_direction': (1.0, 0.0, 0.0),  # x-direction
}

# Expected behavior:
# - 3D spreading losses in addition to stratification effects
# - Lateral modes and wave front curvature
# - More realistic representation of waveguide propagation
# - Higher computational cost (more elements)
# - Typical TL: 15-25 dB over 40 m (includes spreading + stratification)

# Note: 3D simulations require significantly more memory and time.
# Consider reducing frequency points or domain size for initial tests.
