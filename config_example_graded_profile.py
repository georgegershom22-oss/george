#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example Configuration: Continuously Graded Profile
===================================================

Simulates acoustic propagation through continuously varying density
and bulk modulus, representing smooth stratification without sharp
interfaces (e.g., gradual salinity/temperature gradient).

Uses field-variable dependent material properties with analytical field F1(z).
"""

config = {
    # Model identification
    'model_name': 'GradedProfile_Acoustic',
    'job_name': 'graded_profile_tl',
    
    # Geometry
    'dimension': 2,
    'length': 100.0,  # meters
    'height': 50.0,   # meters
    'width': 10.0,
    
    # Frequency sweep
    'freq_start': 100.0,
    'freq_end': 3000.0,
    'freq_inc': 25.0,
    
    # Stratification
    'stratification_type': 'graded',  # Continuous variation
    
    # Graded parameters: linear or exponential profile
    'graded_params': {
        'rho_surface': 1000.0,    # kg/m³ at z=height (top)
        'rho_bottom': 1030.0,     # kg/m³ at z=0 (bottom)
        'K_surface': 2.250e9,     # Pa at z=height
        'K_bottom': 2.318e9,      # Pa at z=0
        'profile': 'linear',      # 'linear' or 'exponential'
    },
    
    # Layers (not used for graded, but kept for compatibility)
    'layers': [],
    
    # Mesh
    'target_elements_per_wavelength': 12,
    
    # Probes
    'probe_in_x': 20.0,
    'probe_out_x': 80.0,  # 60 m separation
    
    # Incident wave
    'incident_density': 1015.0,  # Average value
    'incident_speed': 1500.0,
    'incident_direction': (1.0, 0.0, 0.0),
}

# Expected behavior:
# - Smooth refraction (no sharp reflections)
# - Gradual sound speed variation
# - Ray bending according to Snell's law in continuously stratified medium
# - Lower TL than layered case (less reflection)
# - Typical TL: 5-15 dB over 60 m
