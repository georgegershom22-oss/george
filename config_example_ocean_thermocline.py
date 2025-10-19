#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example Configuration: Ocean Thermocline
=========================================

Simulates acoustic propagation through an ocean thermocline with
typical temperature-stratified water properties.

Temperature-dependent density and bulk modulus:
- Surface: warmer, lighter (1020 kg/m³, 2.28 GPa)
- Thermocline: transition layer
- Deep: colder, denser (1028 kg/m³, 2.32 GPa)

Typical sound speed profile:
- Surface: ~1520 m/s
- Minimum at thermocline: ~1480 m/s
- Deep: ~1510 m/s (pressure effect)
"""

# Configuration parameters for acoustic simulation
config = {
    # Model identification
    'model_name': 'OceanThermocline_Acoustic',
    'job_name': 'ocean_thermocline_tl',
    
    # Geometry
    'dimension': 2,  # 2D simulation
    'length': 200.0,  # meters (horizontal range)
    'height': 100.0,  # meters (depth)
    'width': 10.0,    # meters (only for 3D)
    
    # Frequency sweep
    'freq_start': 50.0,    # Hz (low frequency for long range)
    'freq_end': 2000.0,    # Hz
    'freq_inc': 10.0,      # Hz
    
    # Stratification type
    'stratification_type': 'layered',  # 'layered' or 'graded'
    
    # Layered configuration: (z_bottom, z_top, density, bulk_modulus)
    # Represents surface mixed layer, thermocline, and deep layer
    'layers': [
        # Deep layer (cold, dense)
        (0.0,   40.0, 1028.0, 2.320e9),  # c ≈ 1502 m/s
        
        # Thermocline (transition)
        (40.0,  60.0, 1024.0, 2.244e9),  # c ≈ 1480 m/s (sound channel axis)
        
        # Upper layer (warm, less dense)
        (60.0, 100.0, 1020.0, 2.357e9),  # c ≈ 1520 m/s
    ],
    
    # Mesh parameters
    'target_elements_per_wavelength': 12,
    
    # Probe locations
    'probe_in_x': 50.0,   # meters
    'probe_out_x': 150.0, # meters (100 m separation)
    
    # Incident wave
    'incident_density': 1024.0,  # kg/m³ (mid-depth reference)
    'incident_speed': 1500.0,    # m/s
    'incident_direction': (1.0, 0.0, 0.0),  # horizontal propagation
}

# Expected behavior:
# - Sound channel effect due to sound speed minimum in thermocline
# - Refraction toward sound speed minimum
# - Frequency-dependent TL due to layer interactions
# - Typical TL: 10-30 dB over 100 m depending on frequency
