"""
Parameter Sampling for SOFC Dataset Generation
Uses Latin Hypercube Sampling to explore parameter space
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


class ParameterSampler:
    """
    Generate parameter sets using Latin Hypercube Sampling
    """
    
    def __init__(self):
        """Initialize parameter ranges"""
        self.parameter_ranges = self._define_parameter_ranges()
    
    def _define_parameter_ranges(self) -> Dict[str, Tuple[float, float]]:
        """
        Define valid ranges for all input parameters
        
        Returns:
            Dictionary mapping parameter names to (min, max) tuples
        """
        ranges = {
            # Operating Conditions
            'voltage': (0.6, 0.9),  # V
            'reversible_voltage': (1.0, 1.2),  # V
            'flow_rate_fuel': (0.5e-3, 2.0e-3),  # m/s
            'flow_rate_air': (1.0e-3, 4.0e-3),  # m/s
            'T_inlet_fuel': (1023.0, 1123.0),  # K
            'T_inlet_air': (1023.0, 1123.0),  # K
            
            # Geometric Parameters
            'thickness_anode': (300e-6, 700e-6),  # m
            'thickness_electrolyte': (5e-6, 20e-6),  # m
            'thickness_cathode': (30e-6, 80e-6),  # m
            'thickness_interconnect': (80e-6, 150e-6),  # m
            
            # Anode Material Properties
            'anode_porosity': (0.2, 0.4),
            'anode_permeability': (1e-13, 1e-11),  # m²
            'anode_ionic_conductivity': (5.0, 20.0),  # S/m
            'anode_electronic_conductivity': (500.0, 2000.0),  # S/m
            'anode_youngs_modulus': (80e9, 150e9),  # Pa
            'anode_cte': (10e-6, 15e-6),  # 1/K
            'anode_thermal_conductivity': (1.5, 3.0),  # W/(m·K)
            
            # Electrolyte Material Properties
            'electrolyte_ionic_conductivity': (8.0, 15.0),  # S/m
            'electrolyte_youngs_modulus': (200e9, 300e9),  # Pa
            'electrolyte_cte': (10e-6, 12e-6),  # 1/K
            'electrolyte_thermal_conductivity': (2.0, 4.0),  # W/(m·K)
            
            # Cathode Material Properties
            'cathode_porosity': (0.25, 0.45),
            'cathode_permeability': (1e-13, 1e-11),  # m²
            'cathode_ionic_conductivity': (3.0, 10.0),  # S/m
            'cathode_electronic_conductivity': (300.0, 1000.0),  # S/m
            'cathode_youngs_modulus': (50e9, 120e9),  # Pa
            'cathode_cte': (11e-6, 16e-6),  # 1/K
            'cathode_thermal_conductivity': (1.0, 2.5),  # W/(m·K)
            
            # Interconnect Material Properties
            'interconnect_electronic_conductivity': (5000.0, 15000.0),  # S/m
            'interconnect_youngs_modulus': (150e9, 250e9),  # Pa
            'interconnect_cte': (10e-6, 13e-6),  # 1/K
            'interconnect_thermal_conductivity': (15.0, 25.0),  # W/(m·K)
            
            # Electrochemical Parameters
            'exchange_current_anode': (500.0, 2000.0),  # A/m²
            'exchange_current_cathode': (200.0, 1000.0),  # A/m²
            'transfer_coefficient_anode': (0.4, 0.6),
            'transfer_coefficient_cathode': (0.4, 0.6),
            'activation_energy_anode': (100e3, 140e3),  # J/mol
            'activation_energy_cathode': (120e3, 160e3),  # J/mol
            
            # Species Transport
            'c_H2_inlet': (35.0, 45.0),  # mol/m³
            'c_H2O_inlet': (0.5, 2.0),  # mol/m³
        }
        
        return ranges
    
    def sample_parameters(self, n_samples: int, random_seed: int = 42) -> List[Dict]:
        """
        Generate parameter sets using Latin Hypercube Sampling
        
        Args:
            n_samples: Number of parameter sets to generate
            random_seed: Random seed for reproducibility
            
        Returns:
            List of parameter dictionaries
        """
        np.random.seed(random_seed)
        
        param_names = list(self.parameter_ranges.keys())
        n_params = len(param_names)
        
        # Generate Latin Hypercube samples in [0, 1] space
        lhs_samples = self._lhs(n_params, n_samples, random_seed)
        
        # Scale to actual parameter ranges
        parameter_sets = []
        for i in range(n_samples):
            params = {}
            for j, param_name in enumerate(param_names):
                min_val, max_val = self.parameter_ranges[param_name]
                # Map from [0, 1] to [min, max]
                params[param_name] = min_val + lhs_samples[i, j] * (max_val - min_val)
            
            # Add fixed parameters (not varied)
            params['anode_poisson_ratio'] = 0.3
            params['anode_specific_heat'] = 500.0
            params['anode_density'] = 6000.0
            params['electrolyte_poisson_ratio'] = 0.28
            params['electrolyte_specific_heat'] = 600.0
            params['electrolyte_density'] = 6000.0
            params['cathode_poisson_ratio'] = 0.3
            params['cathode_specific_heat'] = 500.0
            params['cathode_density'] = 5500.0
            params['interconnect_poisson_ratio'] = 0.3
            params['interconnect_specific_heat'] = 500.0
            params['interconnect_density'] = 7500.0
            
            parameter_sets.append(params)
        
        return parameter_sets
    
    def save_parameter_ranges(self, filepath: str):
        """
        Save parameter ranges to CSV for reference
        
        Args:
            filepath: Path to save CSV file
        """
        data = []
        for param_name, (min_val, max_val) in self.parameter_ranges.items():
            data.append({
                'parameter': param_name,
                'min_value': min_val,
                'max_value': max_val,
                'unit': self._get_unit(param_name)
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
    
    @staticmethod
    def _lhs(n_params: int, n_samples: int, random_seed: int) -> np.ndarray:
        """
        Generate Latin Hypercube Samples
        
        Args:
            n_params: Number of parameters (dimensions)
            n_samples: Number of samples
            random_seed: Random seed
            
        Returns:
            Array of shape (n_samples, n_params) with values in [0, 1]
        """
        np.random.seed(random_seed)
        
        # Create LHS grid
        samples = np.zeros((n_samples, n_params))
        
        for i in range(n_params):
            # Divide range [0, 1] into n_samples intervals
            intervals = np.linspace(0, 1, n_samples + 1)
            
            # Randomly sample one value from each interval
            for j in range(n_samples):
                samples[j, i] = np.random.uniform(intervals[j], intervals[j + 1])
        
        # Randomly permute each column independently
        for i in range(n_params):
            samples[:, i] = np.random.permutation(samples[:, i])
        
        return samples
    
    @staticmethod
    def _get_unit(param_name: str) -> str:
        """Get unit for a parameter"""
        units = {
            'voltage': 'V',
            'reversible_voltage': 'V',
            'flow_rate_fuel': 'm/s',
            'flow_rate_air': 'm/s',
            'T_inlet_fuel': 'K',
            'T_inlet_air': 'K',
            'thickness_anode': 'm',
            'thickness_electrolyte': 'm',
            'thickness_cathode': 'm',
            'thickness_interconnect': 'm',
            'porosity': '-',
            'permeability': 'm²',
            'ionic_conductivity': 'S/m',
            'electronic_conductivity': 'S/m',
            'youngs_modulus': 'Pa',
            'cte': '1/K',
            'thermal_conductivity': 'W/(m·K)',
            'exchange_current': 'A/m²',
            'transfer_coefficient': '-',
            'activation_energy': 'J/mol',
            'c_H2_inlet': 'mol/m³',
            'c_H2O_inlet': 'mol/m³',
        }
        
        for key, unit in units.items():
            if key in param_name:
                return unit
        return '-'