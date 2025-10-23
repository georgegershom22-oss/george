"""
Configuration file for SOFC simulation parameters
"""

# Simulation parameters
N_SAMPLES = 10200
BATCH_SIZE = 100
N_JOBS = -1  # Use all available cores

# Parameter ranges
PARAMETER_RANGES = {
    'temperature': {
        'min': 700,  # °C
        'max': 900,  # °C
        'distribution': 'normal',  # 'normal' or 'uniform'
        'mean': 800,  # For normal distribution
        'std': 50     # For normal distribution
    },
    'current_density': {
        'min': 1000,  # A/m²
        'max': 10000,  # A/m²
        'distribution': 'uniform'
    },
    'fuel_utilization': {
        'min': 0.6,  # dimensionless
        'max': 0.9,  # dimensionless
        'distribution': 'uniform'
    },
    'anode_porosity': {
        'min': 0.2,  # dimensionless
        'max': 0.4,  # dimensionless
        'distribution': 'uniform'
    }
}

# V-I curve parameters
VI_CURRENT_RANGE = (1000, 10000)  # A/m²
VI_N_POINTS = 50

# Output file settings
OUTPUT_FILES = {
    'hdf5': 'sofc_lf_dataset.h5',
    'csv': 'sofc_lf_dataset.csv',
    'parameters': 'sofc_parameter_space.csv',
    'plots': 'sofc_sample_results.png'
}

# Model parameters
MODEL_PARAMS = {
    'R': 8.314,  # Universal gas constant (J/mol/K)
    'F': 96485,  # Faraday's constant (C/mol)
    'sigma_elec': 0.1,  # Electrical conductivity (S/m)
    't_elec': 50e-6,  # Electrolyte thickness (m)
    't_anode': 500e-6,  # Anode thickness (m)
    't_cathode': 50e-6,  # Cathode thickness (m)
    'A_cell': 0.01,  # Cell area (m²)
    'L_stack': 0.1,  # Stack length (m)
}

# Gas composition (mole fractions)
GAS_COMPOSITION = {
    'H2': 0.8,
    'H2O': 0.2,
    'O2': 0.21,
    'N2': 0.79
}