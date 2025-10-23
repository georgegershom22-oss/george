"""
Configuration file for SOFC simulation parameters
"""

# Simulation parameters
N_SAMPLES = 10200
N_JOBS = -1  # Use all available CPU cores
SAVE_PATH = "sofc_low_fidelity_dataset.csv"

# Parameter ranges for parametric sweep
PARAMETER_RANGES = {
    'temperature': {
        'min': 700,  # °C
        'max': 900,  # °C
        'n_points': 20
    },
    'current_density': {
        'min': 1000,  # A/m²
        'max': 5000,  # A/m²
        'n_points': 20
    },
    'fuel_utilization': {
        'min': 0.6,  # 0-1
        'max': 0.9,  # 0-1
        'n_points': 20
    },
    'anode_porosity': {
        'min': 0.2,  # 0-1
        'max': 0.4,  # 0-1
        'n_points': 20
    },
    'air_utilization': {
        'min': 0.15,  # 0-1
        'max': 0.25,  # 0-1
        'n_points': 20
    }
}

# Material properties (can be varied in future studies)
MATERIAL_PROPERTIES = {
    'anode_thickness': 1e-3,  # m
    'cathode_thickness': 1e-3,  # m
    'electrolyte_thickness': 1e-4,  # m
    'sigma_anode': 1000,  # S/m
    'sigma_cathode': 1000,  # S/m
    'alpha_anode': 0.5,
    'alpha_cathode': 0.5,
    'rho_stack': 6000,  # kg/m³
    'cp_stack': 500,  # J/(kg·K)
    'h_conv': 50,  # W/(m²·K)
}

# Stack geometry
STACK_GEOMETRY = {
    'n_cells': 50,
    'cell_area': 0.01,  # m²
    'stack_length': 0.3,  # m
    'stack_diameter': 0.1,  # m
}

# Gas properties
GAS_PROPERTIES = {
    'p_total': 101325,  # Pa
    'p_h2_inlet': 0.8,
    'p_h2o_inlet': 0.2,
    'p_o2_inlet': 0.21,
}