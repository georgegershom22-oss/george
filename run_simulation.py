#!/usr/bin/env python3
"""
SOFC Simulation Runner Script
============================

This script provides a convenient interface to run the SOFC simulation
with different options and configurations.
"""

import argparse
import sys
import os
import time
from parallel_simulation import run_parallel_simulation, save_results_optimized, create_visualization

def main():
    parser = argparse.ArgumentParser(description='SOFC Low-Fidelity Dataset Generator')
    parser.add_argument('--samples', type=int, default=10200, 
                       help='Number of samples to generate (default: 10200)')
    parser.add_argument('--jobs', type=int, default=-1, 
                       help='Number of parallel jobs (-1 for all cores, default: -1)')
    parser.add_argument('--test', action='store_true', 
                       help='Run test simulation with 100 samples')
    parser.add_argument('--no-viz', action='store_true', 
                       help='Skip visualization generation')
    parser.add_argument('--output-dir', type=str, default='.', 
                       help='Output directory for results (default: current directory)')
    
    args = parser.parse_args()
    
    # Change to output directory if specified
    if args.output_dir != '.':
        os.makedirs(args.output_dir, exist_ok=True)
        os.chdir(args.output_dir)
    
    # Determine number of samples
    if args.test:
        n_samples = 100
        n_jobs = min(2, args.jobs if args.jobs > 0 else 2)
        print("Running TEST simulation with 100 samples...")
    else:
        n_samples = args.samples
        n_jobs = args.jobs
        print(f"Running FULL simulation with {n_samples} samples...")
    
    # Print configuration
    print("=" * 60)
    print("SOFC Low-Fidelity Dataset Generator")
    print("=" * 60)
    print(f"Samples: {n_samples}")
    print(f"Parallel jobs: {n_jobs if n_jobs > 0 else 'all available cores'}")
    print(f"Output directory: {os.getcwd()}")
    print(f"Expected runtime: ~{n_samples * 10 / 60:.1f} minutes")
    print("=" * 60)
    
    # Confirm before starting (skip for automated runs)
    if not args.test and n_samples > 1000:
        print(f"\nGenerating {n_samples} samples (~{n_samples * 10 / 60:.1f} minutes)...")
        print("Starting simulation...")
    
    # Run simulation
    start_time = time.time()
    
    try:
        results = run_parallel_simulation(n_samples=n_samples, n_jobs=n_jobs)
        
        # Save results
        save_results_optimized(results)
        
        # Create visualizations
        if not args.no_viz:
            create_visualization(results, n_samples=min(1000, n_samples))
        
        total_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("SIMULATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Total runtime: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        print(f"Average time per sample: {total_time/n_samples:.2f} seconds")
        print(f"Generated files:")
        print(f"  - sofc_lf_dataset.h5 (HDF5 format)")
        print(f"  - sofc_lf_dataset.csv (CSV format)")
        print(f"  - sofc_parameter_space.csv (Input parameters)")
        print(f"  - sofc_dataset_summary.csv (Statistics)")
        if not args.no_viz:
            print(f"  - sofc_sample_results.png (Visualizations)")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during simulation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()