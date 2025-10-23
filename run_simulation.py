#!/usr/bin/env python3
"""
Script to run SOFC low-fidelity dataset generation
"""

import sys
import time
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

from sofc_simulation import SOFCDatasetGenerator
import config

def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(description='Generate SOFC low-fidelity dataset')
    parser.add_argument('--samples', type=int, default=config.N_SAMPLES,
                       help='Number of samples to generate')
    parser.add_argument('--jobs', type=int, default=config.N_JOBS,
                       help='Number of parallel jobs')
    parser.add_argument('--output', type=str, default=config.SAVE_PATH,
                       help='Output file path')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick test with 100 samples')
    
    args = parser.parse_args()
    
    if args.quick:
        n_samples = 100
        print("Running quick test with 100 samples...")
    else:
        n_samples = args.samples
        
    print("SOFC Low-Fidelity Dataset Generator")
    print("=" * 50)
    print(f"Target samples: {n_samples}")
    print(f"Parallel jobs: {args.jobs}")
    print(f"Output file: {args.output}")
    print()
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize generator
    generator = SOFCDatasetGenerator(n_samples=n_samples)
    
    # Run simulation
    start_time = time.time()
    try:
        df = generator.generate_dataset(
            n_jobs=args.jobs, 
            save_path=args.output
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n✅ Dataset generation completed successfully!")
        print(f"⏱️  Total time: {duration:.2f} seconds")
        print(f"📊 Generated samples: {len(df)}")
        print(f"⚡ Average time per sample: {duration/len(df):.3f} seconds")
        
        # Basic validation
        print(f"\n📋 Dataset validation:")
        print(f"   - Shape: {df.shape}")
        print(f"   - Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        print(f"   - Missing values: {df.isnull().sum().sum()}")
        
        # Check output ranges
        output_cols = [col for col in df.columns if col.startswith('output_') and not col.endswith('_curve')]
        print(f"\n📈 Output parameter ranges:")
        for col in output_cols:
            if col in df.columns:
                print(f"   - {col}: {df[col].min():.3f} to {df[col].max():.3f}")
        
        # Save additional formats
        base_name = output_path.stem
        parquet_path = output_path.parent / f"{base_name}.parquet"
        h5_path = output_path.parent / f"{base_name}.h5"
        
        print(f"\n💾 Saving additional formats:")
        try:
            df.to_parquet(parquet_path, index=False)
            print(f"   - {parquet_path}")
        except Exception as e:
            print(f"   - Parquet save failed: {e}")
        
        try:
            df.to_hdf(h5_path, key="sofc_data", mode="w")
            print(f"   - {h5_path}")
        except Exception as e:
            print(f"   - HDF5 save failed: {e}")
        
        # Generate summary statistics
        summary_path = output_path.parent / f"{base_name}_summary.txt"
        with open(summary_path, 'w') as f:
            f.write("SOFC Low-Fidelity Dataset Summary\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Total samples: {len(df)}\n")
            f.write(f"Generation time: {duration:.2f} seconds\n")
            f.write(f"Average time per sample: {duration/len(df):.3f} seconds\n\n")
            
            f.write("Input Parameters:\n")
            input_cols = [col for col in df.columns if col.startswith('input_')]
            for col in input_cols:
                f.write(f"  {col}: {df[col].min():.3f} to {df[col].max():.3f}\n")
            
            f.write("\nOutput Parameters:\n")
            for col in output_cols:
                if col in df.columns:
                    f.write(f"  {col}: {df[col].min():.3f} to {df[col].max():.3f}\n")
        
        print(f"   - {summary_path}")
        
        # Create visualization if not quick test
        if not args.quick:
            print(f"\n📊 Generating visualizations...")
            generator.analyze_dataset(df)
            print(f"   - sofc_dataset_analysis.png")
        
        print(f"\n🎉 Dataset generation completed successfully!")
        print(f"📁 All files saved in: {output_path.parent}")
        
    except Exception as e:
        print(f"\n❌ Error during dataset generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()