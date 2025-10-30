#!/usr/bin/env python3
"""
Utility script to inspect and visualize SOFC dataset
"""

import argparse
import h5py
import numpy as np
import matplotlib.pyplot as plt
from dataset_generator import DatasetGenerator


def plot_sample_fields(hdf5_path: str, sample_idx: int = 0, output_dir: str = 'plots'):
    """
    Plot all output fields for a sample
    
    Args:
        hdf5_path: Path to HDF5 dataset
        sample_idx: Index of sample to plot
        output_dir: Directory to save plots
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    with h5py.File(hdf5_path, 'r') as f:
        n_samples = int(f['metadata/n_samples'][()])
        if sample_idx >= n_samples:
            print(f"Error: sample_idx {sample_idx} >= n_samples {n_samples}")
            return
        
        grid_res = tuple(f['metadata/grid_resolution'][:])
        nx, ny, nz = grid_res
        
        # Get middle slice for 2D visualization
        z_mid = nz // 2
        
        # Fields to plot
        fields = {
            'temperature': 'Temperature [K]',
            'current_density': 'Current Density [A/m²]',
            'von_mises_stress': 'Von Mises Stress [Pa]',
            'c_H2': 'H₂ Concentration [mol/m³]',
            'c_H2O': 'H₂O Concentration [mol/m³]',
        }
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        for idx, (field_name, field_label) in enumerate(fields.items()):
            if idx >= len(axes):
                break
                
            data = f[f'outputs/{field_name}'][sample_idx, :, :, z_mid]
            
            im = axes[idx].imshow(data, cmap='viridis', origin='lower')
            axes[idx].set_title(f'{field_label} (Sample {sample_idx}, z={z_mid}/{nz})')
            axes[idx].set_xlabel('x')
            axes[idx].set_ylabel('y')
            plt.colorbar(im, ax=axes[idx])
        
        # Remove unused subplot
        axes[-1].remove()
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'sample_{sample_idx}_fields.png'), dpi=150)
        plt.close()
        
        print(f"Saved plots to {output_dir}/sample_{sample_idx}_fields.png")


def print_statistics(hdf5_path: str):
    """
    Print dataset statistics
    
    Args:
        hdf5_path: Path to HDF5 dataset
    """
    generator = DatasetGenerator()
    info = generator.load_dataset_info(hdf5_path)
    
    print("=" * 70)
    print("Dataset Statistics")
    print("=" * 70)
    print(f"Number of samples: {info['n_samples']}")
    print(f"Grid resolution: {info['grid_resolution']}")
    print(f"Number of input parameters: {len(info['parameter_names'])}")
    print(f"\nInput Parameters:")
    for i, param in enumerate(info['parameter_names'], 1):
        print(f"  {i:2d}. {param}")
    
    print(f"\nOutput Fields ({len(info['output_fields'])}):")
    for field in info['output_fields']:
        print(f"  - {field}")
    
    if 'statistics' in info:
        print("\nField Statistics:")
        for field, stats in info['statistics'].items():
            print(f"\n  {field}:")
            print(f"    Mean: {stats['mean']:.4e}")
            print(f"    Std:  {stats['std']:.4e}")
            print(f"    Min:  {stats['min']:.4e}")
            print(f"    Max:  {stats['max']:.4e}")


def main():
    parser = argparse.ArgumentParser(
        description='Inspect SOFC Dataset'
    )
    parser.add_argument(
        'dataset',
        type=str,
        help='Path to HDF5 dataset file'
    )
    parser.add_argument(
        '--plot',
        action='store_true',
        help='Generate visualization plots'
    )
    parser.add_argument(
        '--sample-idx',
        type=int,
        default=0,
        help='Sample index to plot (default: 0)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='plots',
        help='Output directory for plots (default: plots)'
    )
    
    args = parser.parse_args()
    
    # Print statistics
    print_statistics(args.dataset)
    
    # Generate plots if requested
    if args.plot:
        print(f"\nGenerating plots for sample {args.sample_idx}...")
        plot_sample_fields(args.dataset, args.sample_idx, args.output_dir)


if __name__ == '__main__':
    main()