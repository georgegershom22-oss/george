#!/usr/bin/env python3
"""
Example script showing how to load and use the SOFC dataset
"""

import h5py
import numpy as np
import matplotlib.pyplot as plt


def load_sample(hdf5_path: str, sample_idx: int = 0):
    """
    Load a single sample from the dataset
    
    Args:
        hdf5_path: Path to HDF5 dataset
        sample_idx: Index of sample to load
        
    Returns:
        Dictionary containing inputs and outputs for the sample
    """
    with h5py.File(hdf5_path, 'r') as f:
        # Load input parameters
        param_names = [name.decode() for name in f['metadata/parameter_names'][:]]
        inputs = dict(zip(param_names, f['inputs/parameters'][sample_idx, :]))
        
        # Load output fields
        outputs = {
            'current_density': f['outputs/current_density'][sample_idx],
            'temperature': f['outputs/temperature'][sample_idx],
            'von_mises_stress': f['outputs/von_mises_stress'][sample_idx],
            'c_H2': f['outputs/c_H2'][sample_idx],
            'c_H2O': f['outputs/c_H2O'][sample_idx],
            'strain': np.array([
                f['outputs/strain_xx'][sample_idx],
                f['outputs/strain_yy'][sample_idx],
                f['outputs/strain_zz'][sample_idx],
            ]),
            'displacement': np.array([
                f['outputs/displacement_u'][sample_idx],
                f['outputs/displacement_v'][sample_idx],
                f['outputs/displacement_w'][sample_idx],
            ]),
        }
        
        grid_resolution = tuple(f['metadata/grid_resolution'][:])
        
    return {
        'inputs': inputs,
        'outputs': outputs,
        'grid_resolution': grid_resolution
    }


def visualize_sample(sample_data: dict, output_dir: str = 'visualizations'):
    """
    Create visualizations for a sample
    
    Args:
        sample_data: Dictionary from load_sample
        output_dir: Directory to save plots
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    outputs = sample_data['outputs']
    nx, ny, nz = sample_data['grid_resolution']
    z_mid = nz // 2
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    # Plot fields at mid-plane
    fields = [
        ('temperature', outputs['temperature'][:, :, z_mid], 'Temperature [K]', 'hot'),
        ('current_density', outputs['current_density'][:, :, z_mid], 'Current Density [A/m²]', 'plasma'),
        ('von_mises_stress', outputs['von_mises_stress'][:, :, z_mid], 'Von Mises Stress [Pa]', 'viridis'),
        ('c_H2', outputs['c_H2'][:, :, z_mid], 'H₂ Concentration [mol/m³]', 'Blues'),
        ('c_H2O', outputs['c_H2O'][:, :, z_mid], 'H₂O Concentration [mol/m³]', 'Oranges'),
        ('displacement_magnitude', 
         np.sqrt(outputs['displacement'][0]**2 + outputs['displacement'][1]**2 + outputs['displacement'][2]**2)[:, :, z_mid],
         'Displacement Magnitude [m]', 'coolwarm'),
    ]
    
    for idx, (name, data, label, cmap) in enumerate(fields):
        im = axes[idx].imshow(data, cmap=cmap, origin='lower')
        axes[idx].set_title(f'{label} (z={z_mid}/{nz})')
        axes[idx].set_xlabel('x')
        axes[idx].set_ylabel('y')
        plt.colorbar(im, ax=axes[idx])
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/sample_visualization.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Saved visualization to {output_dir}/sample_visualization.png")


def batch_load_for_training(hdf5_path: str, n_samples: int = None):
    """
    Load dataset in batches for machine learning training
    
    Args:
        hdf5_path: Path to HDF5 dataset
        n_samples: Number of samples to load (None = all)
        
    Returns:
        Tuple of (X, y) where X is inputs and y is outputs
    """
    with h5py.File(hdf5_path, 'r') as f:
        n_total = int(f['metadata/n_samples'][()])
        n_load = n_samples if n_samples is not None else n_total
        n_load = min(n_load, n_total)
        
        # Load input parameters (flatten to 1D)
        X = f['inputs/parameters'][:n_load]  # Shape: (n_samples, n_params)
        
        # Load selected output fields (you can choose which ones to use)
        # For this example, we'll use temperature and stress
        outputs = {
            'temperature': f['outputs/temperature'][:n_load],
            'von_mises_stress': f['outputs/von_mises_stress'][:n_load],
            'current_density': f['outputs/current_density'][:n_load],
        }
        
    return X, outputs


if __name__ == '__main__':
    # Example usage
    dataset_path = 'sofc_dataset/sofc_dataset.h5'
    
    try:
        # Load and visualize a sample
        print("Loading sample 0...")
        sample = load_sample(dataset_path, sample_idx=0)
        
        print(f"Input parameters for sample 0:")
        inputs = sample['inputs']
        print(f"  Voltage: {inputs['voltage']:.3f} V")
        print(f"  Fuel Flow Rate: {inputs['flow_rate_fuel']:.6f} m/s")
        print(f"  Air Flow Rate: {inputs['flow_rate_air']:.6f} m/s")
        print(f"  Inlet Temperature (Fuel): {inputs['T_inlet_fuel']:.1f} K")
        print(f"  Inlet Temperature (Air): {inputs['T_inlet_air']:.1f} K")
        
        outputs = sample['outputs']
        print(f"\nOutput statistics:")
        print(f"  Temperature: {np.mean(outputs['temperature']):.1f} ± {np.std(outputs['temperature']):.1f} K")
        print(f"  Current Density: {np.mean(outputs['current_density']):.4f} A/m²")
        print(f"  Max Stress: {np.max(outputs['von_mises_stress'])/1e6:.2f} MPa")
        
        # Create visualization
        print("\nCreating visualization...")
        visualize_sample(sample)
        
        # Example of loading for training
        print("\nLoading dataset for training (first 10 samples)...")
        X, y = batch_load_for_training(dataset_path, n_samples=10)
        print(f"Input shape: {X.shape}")
        print(f"Output shapes:")
        for key, val in y.items():
            print(f"  {key}: {val.shape}")
        
    except FileNotFoundError:
        print(f"Dataset not found at {dataset_path}")
        print("Please run generate_dataset.py first to create the dataset.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()