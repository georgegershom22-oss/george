#!/usr/bin/env python3
"""
Main script to generate SOFC high-fidelity numerical dataset
"""

import argparse
import os
from dataset_generator import DatasetGenerator


def main():
    parser = argparse.ArgumentParser(
        description='Generate SOFC High-Fidelity Numerical Dataset'
    )
    parser.add_argument(
        '--n-samples',
        type=int,
        default=100,
        help='Number of simulation runs to generate (default: 100)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='sofc_dataset',
        help='Output directory for dataset (default: sofc_dataset)'
    )
    parser.add_argument(
        '--grid-resolution',
        type=int,
        nargs=3,
        default=[50, 50, 30],
        metavar=('NX', 'NY', 'NZ'),
        help='Grid resolution nx ny nz (default: 50 50 30)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Batch size for processing (default: 10)'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("SOFC High-Fidelity Numerical Dataset Generator")
    print("=" * 70)
    print(f"Number of samples: {args.n_samples}")
    print(f"Grid resolution: {tuple(args.grid_resolution)}")
    print(f"Output directory: {args.output_dir}")
    print(f"Random seed: {args.seed}")
    print("=" * 70)
    
    # Initialize generator
    generator = DatasetGenerator(grid_resolution=tuple(args.grid_resolution))
    
    # Generate dataset
    hdf5_path = generator.generate_dataset(
        n_samples=args.n_samples,
        output_dir=args.output_dir,
        random_seed=args.seed,
        batch_size=args.batch_size
    )
    
    # Print summary
    print("\n" + "=" * 70)
    print("Dataset Generation Complete!")
    print("=" * 70)
    print(f"Dataset saved to: {hdf5_path}")
    
    # Load and display info
    info = generator.load_dataset_info(hdf5_path)
    print(f"\nDataset Information:")
    print(f"  - Number of samples: {info['n_samples']}")
    print(f"  - Grid resolution: {info['grid_resolution']}")
    print(f"  - Number of input parameters: {len(info['parameter_names'])}")
    print(f"  - Output fields: {len(info['output_fields'])}")
    print(f"\nOutput fields:")
    for field in info['output_fields']:
        print(f"  - {field}")
    
    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print("1. Review the dataset: Check sofc_dataset/sofc_dataset.h5")
    print("2. Check metadata: sofc_dataset/metadata.json")
    print("3. Check parameter ranges: sofc_dataset/parameter_ranges.csv")
    print("\nYou can load the dataset using:")
    print("  import h5py")
    print("  with h5py.File('sofc_dataset/sofc_dataset.h5', 'r') as f:")
    print("      inputs = f['inputs/parameters'][:]")
    print("      temperatures = f['outputs/temperature'][:]")
    print("=" * 70)


if __name__ == '__main__':
    main()