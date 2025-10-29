"""
Parameter sampling module for SOFC simulation dataset generation.
Uses Latin Hypercube Sampling to efficiently explore the parameter space.
"""

import numpy as np
import pandas as pd
from pyDOE2 import lhs
from scipy.stats import uniform, norm
import yaml
from typing import Dict, List, Tuple, Any
import os


class SOFCParameterSampler:
    """
    Generates parameter samples for SOFC simulations using Latin Hypercube Sampling.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the parameter sampler with configuration.
        
        Args:
            config_path: Path to the YAML configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.parameter_ranges = self._extract_parameter_ranges()
        self.parameter_names = list(self.parameter_ranges.keys())
        self.n_parameters = len(self.parameter_names)
        
    def _extract_parameter_ranges(self) -> Dict[str, Tuple[float, float]]:
        """
        Extract parameter ranges from configuration.
        
        Returns:
            Dictionary mapping parameter names to (min, max) tuples
        """
        ranges = {}
        
        # Geometry parameters
        geom = self.config['geometry']
        ranges.update({
            'anode_thickness': geom['anode_thickness'],
            'electrolyte_thickness': geom['electrolyte_thickness'],
            'cathode_thickness': geom['cathode_thickness'],
            'interconnect_thickness': geom['interconnect_thickness'],
            'channel_width': geom['channel_width'],
            'channel_height': geom['channel_height'],
            'rib_width': geom['rib_width']
        })
        
        # Operating conditions
        op_cond = self.config['operating_conditions']
        ranges.update({
            'voltage': op_cond['voltage'],
            'current_density': op_cond['current_density'],
            'fuel_flow_rate': op_cond['fuel_flow_rate'],
            'air_flow_rate': op_cond['air_flow_rate'],
            'fuel_inlet_temp': op_cond['fuel_inlet_temp'],
            'air_inlet_temp': op_cond['air_inlet_temp'],
            'fuel_pressure': op_cond['fuel_pressure'],
            'air_pressure': op_cond['air_pressure']
        })
        
        # Material properties
        materials = self.config['materials']
        
        # Anode properties
        anode = materials['anode']
        ranges.update({
            'anode_porosity': anode['porosity'],
            'anode_permeability': anode['permeability'],
            'anode_ionic_conductivity': anode['ionic_conductivity'],
            'anode_electronic_conductivity': anode['electronic_conductivity'],
            'anode_youngs_modulus': anode['youngs_modulus'],
            'anode_thermal_expansion': anode['thermal_expansion'],
            'anode_thermal_conductivity': anode['thermal_conductivity']
        })
        
        # Electrolyte properties
        electrolyte = materials['electrolyte']
        ranges.update({
            'electrolyte_porosity': electrolyte['porosity'],
            'electrolyte_ionic_conductivity': electrolyte['ionic_conductivity'],
            'electrolyte_electronic_conductivity': electrolyte['electronic_conductivity'],
            'electrolyte_youngs_modulus': electrolyte['youngs_modulus'],
            'electrolyte_thermal_expansion': electrolyte['thermal_expansion'],
            'electrolyte_thermal_conductivity': electrolyte['thermal_conductivity']
        })
        
        # Cathode properties
        cathode = materials['cathode']
        ranges.update({
            'cathode_porosity': cathode['porosity'],
            'cathode_permeability': cathode['permeability'],
            'cathode_ionic_conductivity': cathode['ionic_conductivity'],
            'cathode_electronic_conductivity': cathode['electronic_conductivity'],
            'cathode_youngs_modulus': cathode['youngs_modulus'],
            'cathode_thermal_expansion': cathode['thermal_expansion'],
            'cathode_thermal_conductivity': cathode['thermal_conductivity']
        })
        
        # Interconnect properties
        interconnect = materials['interconnect']
        ranges.update({
            'interconnect_youngs_modulus': interconnect['youngs_modulus'],
            'interconnect_thermal_expansion': interconnect['thermal_expansion'],
            'interconnect_thermal_conductivity': interconnect['thermal_conductivity'],
            'interconnect_electrical_conductivity': interconnect['electrical_conductivity']
        })
        
        return ranges
    
    def generate_samples(self, n_samples: int, sampling_method: str = 'lhs', 
                        seed: int = None) -> pd.DataFrame:
        """
        Generate parameter samples using specified sampling method.
        
        Args:
            n_samples: Number of samples to generate
            sampling_method: Sampling method ('lhs', 'random', 'sobol')
            seed: Random seed for reproducibility
            
        Returns:
            DataFrame with parameter samples
        """
        if seed is not None:
            np.random.seed(seed)
        
        if sampling_method == 'lhs':
            samples = self._latin_hypercube_sampling(n_samples)
        elif sampling_method == 'random':
            samples = self._random_sampling(n_samples)
        elif sampling_method == 'sobol':
            samples = self._sobol_sampling(n_samples)
        else:
            raise ValueError(f"Unknown sampling method: {sampling_method}")
        
        # Convert to DataFrame with parameter names
        df = pd.DataFrame(samples, columns=self.parameter_names)
        
        # Add sample ID
        df['sample_id'] = range(len(df))
        
        return df
    
    def _latin_hypercube_sampling(self, n_samples: int) -> np.ndarray:
        """
        Generate samples using Latin Hypercube Sampling.
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            Array of parameter samples
        """
        # Generate LHS samples in [0,1]^n_parameters
        lhs_samples = lhs(self.n_parameters, samples=n_samples, criterion='maximin')
        
        # Scale to parameter ranges
        scaled_samples = np.zeros_like(lhs_samples)
        
        for i, param_name in enumerate(self.parameter_names):
            min_val, max_val = self.parameter_ranges[param_name]
            
            # Handle log-scale parameters (permeability, conductivity)
            if 'permeability' in param_name or 'conductivity' in param_name:
                # Use log-uniform distribution
                log_min, log_max = np.log10(min_val), np.log10(max_val)
                scaled_samples[:, i] = 10**(log_min + lhs_samples[:, i] * (log_max - log_min))
            else:
                # Use uniform distribution
                scaled_samples[:, i] = min_val + lhs_samples[:, i] * (max_val - min_val)
        
        return scaled_samples
    
    def _random_sampling(self, n_samples: int) -> np.ndarray:
        """
        Generate samples using random sampling.
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            Array of parameter samples
        """
        samples = np.random.random((n_samples, self.n_parameters))
        
        # Scale to parameter ranges
        scaled_samples = np.zeros_like(samples)
        
        for i, param_name in enumerate(self.parameter_names):
            min_val, max_val = self.parameter_ranges[param_name]
            
            if 'permeability' in param_name or 'conductivity' in param_name:
                log_min, log_max = np.log10(min_val), np.log10(max_val)
                scaled_samples[:, i] = 10**(log_min + samples[:, i] * (log_max - log_min))
            else:
                scaled_samples[:, i] = min_val + samples[:, i] * (max_val - min_val)
        
        return scaled_samples
    
    def _sobol_sampling(self, n_samples: int) -> np.ndarray:
        """
        Generate samples using Sobol sequence (placeholder - requires sobol_seq package).
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            Array of parameter samples
        """
        # For now, fall back to LHS
        # In practice, you would use: from sobol_seq import i4_sobol_generate
        return self._latin_hypercube_sampling(n_samples)
    
    def validate_samples(self, samples: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate generated samples and compute statistics.
        
        Args:
            samples: DataFrame with parameter samples
            
        Returns:
            Dictionary with validation statistics
        """
        stats = {}
        
        for param_name in self.parameter_names:
            if param_name in samples.columns:
                values = samples[param_name]
                min_val, max_val = self.parameter_ranges[param_name]
                
                stats[param_name] = {
                    'mean': float(values.mean()),
                    'std': float(values.std()),
                    'min': float(values.min()),
                    'max': float(values.max()),
                    'range_min': min_val,
                    'range_max': max_val,
                    'in_range': bool(values.min() >= min_val and values.max() <= max_val)
                }
        
        return stats
    
    def save_samples(self, samples: pd.DataFrame, output_path: str):
        """
        Save parameter samples to file.
        
        Args:
            samples: DataFrame with parameter samples
            output_path: Path to save the samples
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save as CSV
        samples.to_csv(output_path, index=False)
        
        # Also save validation statistics
        stats_path = output_path.replace('.csv', '_stats.yaml')
        stats = self.validate_samples(samples)
        
        with open(stats_path, 'w') as f:
            yaml.dump(stats, f, default_flow_style=False)
    
    def load_samples(self, input_path: str) -> pd.DataFrame:
        """
        Load parameter samples from file.
        
        Args:
            input_path: Path to load the samples from
            
        Returns:
            DataFrame with parameter samples
        """
        return pd.read_csv(input_path)
    
    def get_parameter_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all parameters.
        
        Returns:
            Dictionary with parameter information
        """
        info = {}
        
        for param_name, (min_val, max_val) in self.parameter_ranges.items():
            info[param_name] = {
                'min': min_val,
                'max': max_val,
                'range': max_val - min_val,
                'log_scale': 'permeability' in param_name or 'conductivity' in param_name,
                'units': self._get_parameter_units(param_name)
            }
        
        return info
    
    def _get_parameter_units(self, param_name: str) -> str:
        """
        Get units for a parameter.
        
        Args:
            param_name: Name of the parameter
            
        Returns:
            Units string
        """
        unit_map = {
            'thickness': 'm',
            'width': 'm',
            'height': 'm',
            'voltage': 'V',
            'current_density': 'A/cm²',
            'flow_rate': 'SLPM',
            'temp': 'K',
            'pressure': 'Pa',
            'porosity': '-',
            'permeability': 'm²',
            'conductivity': 'S/m',
            'youngs_modulus': 'Pa',
            'thermal_expansion': '1/K',
            'thermal_conductivity': 'W/m·K'
        }
        
        for key, unit in unit_map.items():
            if key in param_name:
                return unit
        
        return '-'


if __name__ == "__main__":
    # Example usage
    config_path = "../../config/simulation_config.yaml"
    
    # Initialize sampler
    sampler = SOFCParameterSampler(config_path)
    
    # Generate samples
    n_samples = 100
    samples = sampler.generate_samples(n_samples, sampling_method='lhs', seed=42)
    
    print(f"Generated {len(samples)} parameter samples")
    print(f"Parameters: {list(samples.columns)}")
    print("\nFirst 5 samples:")
    print(samples.head())
    
    # Validate samples
    stats = sampler.validate_samples(samples)
    print(f"\nValidation: All parameters in range: {all(s['in_range'] for s in stats.values())}")
    
    # Save samples
    output_path = "../../data/parameter_samples.csv"
    sampler.save_samples(samples, output_path)
    print(f"Samples saved to {output_path}")