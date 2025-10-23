"""
SOFC Dataset Generator
Generates low-fidelity training data through parametric sweeps of SOFC simulations.

This script creates 10,200+ samples by varying key parameters across realistic ranges.
"""

import numpy as np
import pandas as pd
from tqdm import tqdm
import json
import os
from datetime import datetime
import multiprocessing as mp
from functools import partial

from sofc_model import SOFCModel

class SOFCDatasetGenerator:
    """
    Generator for SOFC simulation datasets with parametric sweeps
    """
    
    def __init__(self, n_samples=10200):
        self.n_samples = n_samples
        self.sofc_model = SOFCModel()
        
        # Define parameter ranges for parametric sweep
        self.parameter_ranges = {
            # Operating conditions
            'operating_temperature': (973.15, 1173.15),  # 700-900°C in Kelvin
            'fuel_utilization': (0.70, 0.95),  # 70-95%
            'air_utilization': (0.15, 0.30),  # 15-30%
            
            # Geometric parameters
            'cell_area': (50e-4, 200e-4),  # 50-200 cm²
            'anode_thickness': (300e-6, 800e-6),  # 300-800 μm
            'cathode_thickness': (30e-6, 100e-6),  # 30-100 μm
            'electrolyte_thickness': (5e-6, 20e-6),  # 5-20 μm
            
            # Material properties
            'anode_porosity': (0.25, 0.55),  # 25-55%
            'cathode_porosity': (0.25, 0.55),  # 25-55%
            'anode_tortuosity': (2.0, 5.0),  # 2-5
            'cathode_tortuosity': (2.0, 5.0),  # 2-5
            
            # Electrochemical parameters
            'exchange_current_density_anode': (3000, 10000),  # A/m²
            'exchange_current_density_cathode': (1000, 5000),  # A/m²
            'activation_energy_anode': (100e3, 140e3),  # J/mol
            'activation_energy_cathode': (140e3, 180e3),  # J/mol
            
            # Transport properties
            'ionic_conductivity_ref': (2e4, 5e4),  # S/m
            'electronic_conductivity_anode': (7e4, 12e4),  # S/m
            'electronic_conductivity_cathode': (6e4, 10e4),  # S/m
            
            # Gas composition
            'h2_inlet_fraction': (0.90, 0.99),  # 90-99%
            'h2o_inlet_fraction': (0.01, 0.10),  # 1-10%
            'o2_inlet_fraction': (0.18, 0.23),  # 18-23%
        }
        
        # Fixed parameters (not varied in sweep)
        self.fixed_params = {
            'ref_temperature': 1073.15,  # Reference temperature (K)
        }
    
    def generate_parameter_set(self):
        """
        Generate a random parameter set within defined ranges
        
        Returns:
            Dictionary of parameters for simulation
        """
        params = self.sofc_model.default_params.copy()
        params.update(self.fixed_params)
        
        # Generate random values within ranges
        for param_name, (min_val, max_val) in self.parameter_ranges.items():
            if param_name in ['operating_temperature']:
                # Use normal distribution for temperature (more realistic)
                mean_temp = (min_val + max_val) / 2
                std_temp = (max_val - min_val) / 6  # 99.7% within range
                temp = np.random.normal(mean_temp, std_temp)
                params[param_name] = np.clip(temp, min_val, max_val)
            else:
                # Use uniform distribution for other parameters
                params[param_name] = np.random.uniform(min_val, max_val)
        
        # Ensure consistency constraints
        # H2O fraction should be consistent with H2 fraction
        h2_frac = params['h2_inlet_fraction']
        h2o_frac = params['h2o_inlet_fraction']
        total_fuel = h2_frac + h2o_frac
        if total_fuel > 1.0:
            # Normalize to maintain total <= 1
            params['h2_inlet_fraction'] = h2_frac / total_fuel * 0.98
            params['h2o_inlet_fraction'] = h2o_frac / total_fuel * 0.98
        
        return params
    
    def simulate_single_sample(self, sample_id):
        """
        Simulate a single sample with random parameters
        
        Args:
            sample_id: Unique identifier for the sample
            
        Returns:
            Dictionary containing simulation results
        """
        try:
            # Generate parameter set
            params = self.generate_parameter_set()
            
            # Run simulation
            results = self.sofc_model.simulate_single_case(params)
            
            # Add sample metadata
            results['sample_id'] = sample_id
            results['simulation_time'] = datetime.now().isoformat()
            
            return results
            
        except Exception as e:
            # Handle simulation failures gracefully
            print(f"Warning: Sample {sample_id} failed with error: {str(e)}")
            return None
    
    def generate_dataset_sequential(self, output_dir='sofc_dataset'):
        """
        Generate dataset sequentially (single-threaded)
        
        Args:
            output_dir: Directory to save the dataset
            
        Returns:
            Path to the generated dataset file
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Generating {self.n_samples} SOFC simulation samples...")
        
        results = []
        failed_samples = 0
        
        # Progress bar
        with tqdm(total=self.n_samples, desc="Simulating") as pbar:
            for i in range(self.n_samples):
                result = self.simulate_single_sample(i)
                if result is not None:
                    results.append(result)
                else:
                    failed_samples += 1
                
                pbar.update(1)
                
                # Save intermediate results every 1000 samples
                if (i + 1) % 1000 == 0:
                    self._save_intermediate_results(results, output_dir, i + 1)
        
        print(f"Completed simulation. Failed samples: {failed_samples}")
        
        # Convert to DataFrame and save
        df = pd.DataFrame(results)
        
        # Save main dataset
        dataset_path = os.path.join(output_dir, 'sofc_lf_dataset.csv')
        df.to_csv(dataset_path, index=False)
        
        # Save metadata
        metadata = {
            'total_samples': len(results),
            'failed_samples': failed_samples,
            'parameter_ranges': self.parameter_ranges,
            'fixed_parameters': self.fixed_params,
            'generation_time': datetime.now().isoformat(),
            'model_type': '1D_lumped_electrochemical',
            'fidelity': 'low'
        }
        
        metadata_path = os.path.join(output_dir, 'dataset_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Dataset saved to: {dataset_path}")
        print(f"Metadata saved to: {metadata_path}")
        
        return dataset_path
    
    def generate_dataset_parallel(self, output_dir='sofc_dataset', n_processes=None):
        """
        Generate dataset in parallel (multi-threaded)
        
        Args:
            output_dir: Directory to save the dataset
            n_processes: Number of processes to use (None for auto-detect)
            
        Returns:
            Path to the generated dataset file
        """
        if n_processes is None:
            n_processes = min(mp.cpu_count(), 8)  # Limit to 8 processes
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Generating {self.n_samples} SOFC simulation samples using {n_processes} processes...")
        
        # Create sample IDs
        sample_ids = list(range(self.n_samples))
        
        # Run simulations in parallel
        with mp.Pool(processes=n_processes) as pool:
            results = list(tqdm(
                pool.imap(self.simulate_single_sample, sample_ids),
                total=self.n_samples,
                desc="Simulating"
            ))
        
        # Filter out failed simulations
        successful_results = [r for r in results if r is not None]
        failed_samples = len(results) - len(successful_results)
        
        print(f"Completed simulation. Failed samples: {failed_samples}")
        
        # Convert to DataFrame and save
        df = pd.DataFrame(successful_results)
        
        # Save main dataset
        dataset_path = os.path.join(output_dir, 'sofc_lf_dataset.csv')
        df.to_csv(dataset_path, index=False)
        
        # Save metadata
        metadata = {
            'total_samples': len(successful_results),
            'failed_samples': failed_samples,
            'parameter_ranges': self.parameter_ranges,
            'fixed_parameters': self.fixed_params,
            'generation_time': datetime.now().isoformat(),
            'model_type': '1D_lumped_electrochemical',
            'fidelity': 'low',
            'parallel_processes': n_processes
        }
        
        metadata_path = os.path.join(output_dir, 'dataset_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Dataset saved to: {dataset_path}")
        print(f"Metadata saved to: {metadata_path}")
        
        return dataset_path
    
    def _save_intermediate_results(self, results, output_dir, sample_count):
        """
        Save intermediate results during generation
        
        Args:
            results: List of simulation results
            output_dir: Output directory
            sample_count: Current sample count
        """
        if results:
            df = pd.DataFrame(results)
            intermediate_path = os.path.join(output_dir, f'intermediate_{sample_count}.csv')
            df.to_csv(intermediate_path, index=False)
    
    def analyze_dataset(self, dataset_path):
        """
        Analyze the generated dataset and create summary statistics
        
        Args:
            dataset_path: Path to the dataset CSV file
            
        Returns:
            Dictionary containing analysis results
        """
        df = pd.read_csv(dataset_path)
        
        # Key output variables for analysis
        output_vars = [
            'operating_temperature', 'voltage_op', 'current_density_op',
            'power_density', 'stack_temperature', 'electrochemical_efficiency'
        ]
        
        analysis = {}
        
        for var in output_vars:
            if var in df.columns:
                analysis[var] = {
                    'mean': float(df[var].mean()),
                    'std': float(df[var].std()),
                    'min': float(df[var].min()),
                    'max': float(df[var].max()),
                    'median': float(df[var].median()),
                    'q25': float(df[var].quantile(0.25)),
                    'q75': float(df[var].quantile(0.75))
                }
        
        # Overall dataset statistics
        analysis['dataset_info'] = {
            'total_samples': len(df),
            'total_features': len(df.columns),
            'missing_values': int(df.isnull().sum().sum()),
            'duplicate_rows': int(df.duplicated().sum())
        }
        
        return analysis

def main():
    """
    Main function to generate the SOFC dataset
    """
    # Configuration
    n_samples = 10200
    output_dir = 'sofc_lf_dataset'
    use_parallel = True  # Set to False for sequential processing
    
    # Create generator
    generator = SOFCDatasetGenerator(n_samples=n_samples)
    
    # Generate dataset
    if use_parallel:
        dataset_path = generator.generate_dataset_parallel(output_dir)
    else:
        dataset_path = generator.generate_dataset_sequential(output_dir)
    
    # Analyze dataset
    print("\nAnalyzing generated dataset...")
    analysis = generator.analyze_dataset(dataset_path)
    
    # Save analysis
    analysis_path = os.path.join(output_dir, 'dataset_analysis.json')
    with open(analysis_path, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"Dataset analysis saved to: {analysis_path}")
    
    # Print summary
    print(f"\n=== Dataset Generation Summary ===")
    print(f"Total samples: {analysis['dataset_info']['total_samples']}")
    print(f"Total features: {analysis['dataset_info']['total_features']}")
    print(f"Dataset path: {dataset_path}")
    
    if 'electrochemical_efficiency' in analysis:
        eff_stats = analysis['electrochemical_efficiency']
        print(f"\nElectrochemical Efficiency Statistics:")
        print(f"  Mean: {eff_stats['mean']:.3f}")
        print(f"  Range: {eff_stats['min']:.3f} - {eff_stats['max']:.3f}")
    
    if 'power_density' in analysis:
        power_stats = analysis['power_density']
        print(f"\nPower Density Statistics (W/m²):")
        print(f"  Mean: {power_stats['mean']:.1f}")
        print(f"  Range: {power_stats['min']:.1f} - {power_stats['max']:.1f}")

if __name__ == "__main__":
    main()