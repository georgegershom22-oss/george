#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example Configuration: Sediment Layers
=======================================

Simulates acoustic propagation through water-sediment interface
with multiple sediment layers of increasing density and stiffness.

Typical seabed scenario:
- Water column: 1025 kg/m³, 2.31 GPa (c=1500 m/s)
- Soft sediment: 1400 kg/m³, 3.00 GPa (c=1463 m/s)
- Medium sediment: 1600 kg/m³, 4.50 GPa (c=1677 m/s)
- Hard sediment: 1800 kg/m³, 7.20 GPa (c=2000 m/s)

Strong impedance contrasts → significant reflections and TL
"""

config = {
    # Model identification
    'model_name': 'SedimentLayers_Acoustic',
    'job_name': 'sediment_layers_tl',
    
    # Geometry
    'dimension': 2,
    'length': 150.0,  # meters
    'height': 80.0,   # meters (water + sediment)
    'width': 10.0,
    
    # Frequency sweep
    'freq_start': 100.0,   # Hz
    'freq_end': 5000.0,    # Hz
    'freq_inc': 50.0,      # Hz
    
    # Stratification
    'stratification_type': 'layered',
    
    # Layers: water column + sediment layers
    'layers': [
        # Hard sediment (bottom)
        (0.0,  15.0, 1800.0, 7.20e9),  # c = 2000 m/s
        
        # Medium sediment
        (15.0, 30.0, 1600.0, 4.50e9),  # c = 1677 m/s
        
        # Soft sediment
        (30.0, 50.0, 1400.0, 3.00e9),  # c = 1463 m/s
        
        # Water column (top)
        (50.0, 80.0, 1025.0, 2.31e9),  # c = 1500 m/s
    ],
    
    # Mesh
    'target_elements_per_wavelength': 15,  # Finer mesh for impedance contrasts
    
    # Probes (both in water)
    'probe_in_x': 30.0,   # meters
    'probe_out_x': 120.0, # meters (90 m separation)
    
    # Incident wave (from water)
    'incident_density': 1025.0,
    'incident_speed': 1500.0,
    'incident_direction': (1.0, 0.0, 0.0),
}

# Expected behavior:
# - Strong reflections at water-sediment interface
# - Multiple mode conversions
# - High TL due to impedance mismatch
# - Frequency-dependent interference patterns
# - Typical TL: 40-80 dB over 90 m
