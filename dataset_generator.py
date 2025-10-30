"""
Dataset Generator for SOFC Multi-Physics Data
Generates and saves simulation results in HDF5 format
"""

import numpy as np
import h5py
import os
from tqdm import tqdm
from typing import Dict, List, Tuple
import json
from datetime import datetime

from sofc_simulator import SOFCSimulator
from parameter_sampling import ParameterSampler


class DatasetGenerator:
    """
    Generate and save SOFC simulation dataset
    """
    
    def __init__(self, grid_resolution: Tuple[int, int, int] = (50, 50, 30)):
        """
        Initialize dataset generator
        
        Args:
            grid_resolution: (nx, ny, nz) grid resolution
        """
        self.grid_resolution = grid_resolution
        self.simulator = SOFCSimulator(*grid_resolution)
        self.sampler = ParameterSampler()
    
    def generate_dataset(self, n_samples: int, output_dir: str = 'dataset', 
                        random_seed: int = 42, batch_size: int = 10):
        """
        Generate complete dataset
        
        Args:
            n_samples: Number of simulation runs
            output_dir: Directory to save dataset
            random_seed: Random seed for reproducibility
            batch_size: Number of simulations to process before saving
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate parameter sets
        print(f"Generating {n_samples} parameter sets using Latin Hypercube Sampling...")
        parameter_sets = self.sampler.sample_parameters(n_samples, random_seed)
        
        # Save parameter ranges reference
        self.sampler.save_parameter_ranges(os.path.join(output_dir, 'parameter_ranges.csv'))
        
        # Create HDF5 file
        hdf5_path = os.path.join(output_dir, 'sofc_dataset.h5')
        
        print(f"Starting simulation runs...")
        print(f"Grid resolution: {self.grid_resolution}")
        
        # Create HDF5 file structure
        with h5py.File(hdf5_path, 'w') as f:
            # Create groups
            f.create_group('inputs')
            f.create_group('outputs')
            f.create_group('metadata')
            
            # Store parameter names
            param_names = list(parameter_sets[0].keys())
            f.create_dataset('metadata/parameter_names', 
                           data=[name.encode() for name in param_names])
            f.create_dataset('metadata/grid_resolution', data=self.grid_resolution)
            f.create_dataset('metadata/n_samples', data=n_samples)
            f.create_dataset('metadata/generation_date', 
                           data=datetime.now().isoformat().encode())
            
            # Pre-allocate output arrays (will grow)
            nx, ny, nz = self.grid_resolution
            
            # Input parameters
            n_params = len(param_names)
            input_chunk_size = min(batch_size, n_samples)
            inputs_dset = f.create_dataset('inputs/parameters', 
                                          shape=(n_samples, n_params),
                                          dtype=np.float64,
                                          chunks=(input_chunk_size, n_params),
                                          compression='gzip',
                                          compression_opts=9)
            
            # Output fields
            outputs = {
                'current_density': (n_samples, nx, ny, nz),
                'overpotential': (n_samples, nx, ny, nz),
                'temperature': (n_samples, nx, ny, nz),
                'von_mises_stress': (n_samples, nx, ny, nz),
                'strain_xx': (n_samples, nx, ny, nz),
                'strain_yy': (n_samples, nx, ny, nz),
                'strain_zz': (n_samples, nx, ny, nz),
                'strain_xy': (n_samples, nx, ny, nz),
                'strain_xz': (n_samples, nx, ny, nz),
                'strain_yz': (n_samples, nx, ny, nz),
                'displacement_u': (n_samples, nx, ny, nz),
                'displacement_v': (n_samples, nx, ny, nz),
                'displacement_w': (n_samples, nx, ny, nz),
                'c_H2': (n_samples, nx, ny, nz),
                'c_H2O': (n_samples, nx, ny, nz),
            }
            
            output_datasets = {}
            chunk_nx = max(1, min(nx//2, nx))
            chunk_ny = max(1, min(ny//2, ny))
            chunk_nz = max(1, min(nz//2, nz))
            chunk_samples = min(batch_size, n_samples)
            
            for name, shape in outputs.items():
                output_datasets[name] = f.create_dataset(
                    f'outputs/{name}',
                    shape=shape,
                    dtype=np.float32,  # Float32 to save space
                    chunks=(chunk_samples, chunk_nx, chunk_ny, chunk_nz),
                    compression='gzip',
                    compression_opts=9
                )
            
            # Store parameter values for each sample
            param_array = np.array([[params[name] for name in param_names] 
                                   for params in parameter_sets])
            inputs_dset[:] = param_array
            
            # Run simulations
            failed_indices = []
            for i in tqdm(range(n_samples), desc="Running simulations"):
                try:
                    params = parameter_sets[i]
                    
                    # Run simulation
                    results = self.simulator.simulate(params)
                    
                    # Store outputs
                    output_datasets['current_density'][i] = results['current_density'].astype(np.float32)
                    output_datasets['overpotential'][i] = results['overpotential'].astype(np.float32)
                    output_datasets['temperature'][i] = results['temperature'].astype(np.float32)
                    output_datasets['von_mises_stress'][i] = results['von_mises_stress'].astype(np.float32)
                    output_datasets['strain_xx'][i] = results['strain'][:, :, :, 0].astype(np.float32)
                    output_datasets['strain_yy'][i] = results['strain'][:, :, :, 1].astype(np.float32)
                    output_datasets['strain_zz'][i] = results['strain'][:, :, :, 2].astype(np.float32)
                    output_datasets['strain_xy'][i] = results['strain'][:, :, :, 3].astype(np.float32)
                    output_datasets['strain_xz'][i] = results['strain'][:, :, :, 4].astype(np.float32)
                    output_datasets['strain_yz'][i] = results['strain'][:, :, :, 5].astype(np.float32)
                    output_datasets['displacement_u'][i] = results['displacement'][:, :, :, 0].astype(np.float32)
                    output_datasets['displacement_v'][i] = results['displacement'][:, :, :, 1].astype(np.float32)
                    output_datasets['displacement_w'][i] = results['displacement'][:, :, :, 2].astype(np.float32)
                    output_datasets['c_H2'][i] = results['c_H2'].astype(np.float32)
                    output_datasets['c_H2O'][i] = results['c_H2O'].astype(np.float32)
                    
                except Exception as e:
                    print(f"\nError in simulation {i}: {e}")
                    failed_indices.append(i)
            
            # Save failed indices if any
            if failed_indices:
                f.create_dataset('metadata/failed_indices', data=failed_indices)
                print(f"\nWarning: {len(failed_indices)} simulations failed")
            
            # Save statistics
            self._compute_and_save_statistics(f, output_datasets)
        
        print(f"\nDataset saved to: {hdf5_path}")
        print(f"Dataset size: {os.path.getsize(hdf5_path) / (1024**3):.2f} GB")
        
        # Create metadata JSON
        metadata = {
            'n_samples': n_samples,
            'grid_resolution': self.grid_resolution,
            'n_parameters': n_params,
            'parameter_names': param_names,
            'output_fields': list(outputs.keys()),
            'generation_date': datetime.now().isoformat(),
            'random_seed': random_seed,
            'failed_simulations': len(failed_indices)
        }
        
        with open(os.path.join(output_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return hdf5_path
    
    def _compute_and_save_statistics(self, h5file: h5py.File, output_datasets: Dict):
        """
        Compute and save statistics for each output field
        
        Args:
            h5file: Open HDF5 file handle
            output_datasets: Dictionary of output datasets
        """
        stats_group = h5file.create_group('metadata/statistics')
        
        for name, dataset in output_datasets.items():
            # Compute statistics (sample a subset for large datasets)
            n_samples = dataset.shape[0]
            sample_size = min(100, n_samples)
            sample_indices = np.sort(np.random.choice(n_samples, sample_size, replace=False))
            
            sample_data = dataset[sample_indices]
            
            # Handle NaN and Inf values
            finite_data = sample_data[np.isfinite(sample_data)]
            if len(finite_data) == 0:
                finite_data = np.array([0.0])
            
            stats_group.create_dataset(f'{name}/mean', data=float(np.mean(finite_data)))
            stats_group.create_dataset(f'{name}/std', data=float(np.std(finite_data)))
            stats_group.create_dataset(f'{name}/min', data=float(np.min(finite_data)))
            stats_group.create_dataset(f'{name}/max', data=float(np.max(finite_data)))
    
    def load_dataset_info(self, hdf5_path: str) -> Dict:
        """
        Load dataset metadata without loading full dataset
        
        Args:
            hdf5_path: Path to HDF5 file
            
        Returns:
            Dictionary with dataset information
        """
        with h5py.File(hdf5_path, 'r') as f:
            info = {
                'n_samples': int(f['metadata/n_samples'][()]),
                'grid_resolution': tuple(f['metadata/grid_resolution'][:]),
                'parameter_names': [name.decode() for name in f['metadata/parameter_names'][:]],
                'output_fields': list(f['outputs'].keys()),
            }
            
            # Get statistics if available
            if 'metadata/statistics' in f:
                stats = {}
                for field in info['output_fields']:
                    if field in f['metadata/statistics']:
                        stats[field] = {
                            'mean': float(f[f'metadata/statistics/{field}/mean'][()]),
                            'std': float(f[f'metadata/statistics/{field}/std'][()]),
                            'min': float(f[f'metadata/statistics/{field}/min'][()]),
                            'max': float(f[f'metadata/statistics/{field}/max'][()]),
                        }
                info['statistics'] = stats
        
        return info