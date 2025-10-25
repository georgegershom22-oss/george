#!/usr/bin/env python3
"""
Script to run the complete dataset generation process
"""

import os
import sys
import time
import argparse
import json
from datetime import datetime
import multiprocessing as mp
from typing import List, Dict

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_dataset import RealTimeDatasetGenerator
from utils.visualization import DatasetVisualizer

def generate_episode_batch(args):
    """Generate a batch of episodes (for multiprocessing)"""
    generator, episode_start, episode_end = args
    
    print(f"Process {os.getpid()}: Generating episodes {episode_start} to {episode_end-1}")
    
    for episode in range(episode_start, episode_end):
        try:
            episode_data = generator.generate_episode_data(episode)
            generator.save_episode_data(episode_data, episode)
            
            if (episode + 1) % 10 == 0:
                print(f"Process {os.getpid()}: Completed episode {episode + 1}")
                
        except Exception as e:
            print(f"Error generating episode {episode}: {e}")
            continue
    
    return f"Process {os.getpid()}: Completed episodes {episode_start} to {episode_end-1}"

def parallel_generation(base_path: str, total_episodes: int, num_processes: int = None):
    """Generate dataset using multiple processes"""
    if num_processes is None:
        num_processes = min(mp.cpu_count(), 8)  # Limit to 8 processes max
    
    print(f"Using {num_processes} processes for dataset generation")
    
    # Create generator instance
    generator = RealTimeDatasetGenerator(base_path)
    
    # Split episodes among processes
    episodes_per_process = total_episodes // num_processes
    process_args = []
    
    for i in range(num_processes):
        start_episode = i * episodes_per_process
        if i == num_processes - 1:
            end_episode = total_episodes  # Last process handles remaining episodes
        else:
            end_episode = (i + 1) * episodes_per_process
        
        process_args.append((generator, start_episode, end_episode))
    
    # Run parallel generation
    start_time = time.time()
    
    with mp.Pool(processes=num_processes) as pool:
        results = pool.map(generate_episode_batch, process_args)
    
    end_time = time.time()
    
    print("\nParallel generation completed!")
    for result in results:
        print(result)
    
    print(f"Total time: {end_time - start_time:.2f} seconds")
    
    # Generate dataset summary
    generator.generate_dataset_summary()
    
    return generator

def create_sample_visualizations(base_path: str, num_samples: int = 5):
    """Create sample visualizations from the generated dataset"""
    print("Creating sample visualizations...")
    
    visualizer = DatasetVisualizer(base_path)
    
    # Create output directory for visualizations
    viz_dir = os.path.join(base_path, "sample_visualizations")
    os.makedirs(viz_dir, exist_ok=True)
    
    # Generate sample episode overviews
    for i in range(min(num_samples, 10)):
        try:
            output_path = os.path.join(viz_dir, f"episode_{i}_overview.png")
            visualizer.plot_episode_overview(i, output_path)
            print(f"Generated overview for episode {i}")
        except Exception as e:
            print(f"Error generating overview for episode {i}: {e}")
    
    # Generate strain field visualizations
    for i in range(min(num_samples, 5)):
        try:
            output_path = os.path.join(viz_dir, f"episode_{i}_strain_field.png")
            visualizer.visualize_strain_field(i, 0, output_path)
            print(f"Generated strain field visualization for episode {i}")
        except Exception as e:
            print(f"Error generating strain field for episode {i}: {e}")
    
    # Generate dataset statistics
    try:
        output_path = os.path.join(viz_dir, "dataset_statistics.png")
        visualizer.plot_dataset_statistics(output_path)
        print("Generated dataset statistics")
    except Exception as e:
        print(f"Error generating dataset statistics: {e}")
    
    # Create interactive dashboard for first episode
    try:
        fig = visualizer.create_interactive_dashboard(0)
        output_path = os.path.join(viz_dir, "interactive_dashboard.html")
        fig.write_html(output_path)
        print("Generated interactive dashboard")
    except Exception as e:
        print(f"Error generating interactive dashboard: {e}")

def validate_dataset(base_path: str, num_episodes_to_check: int = 10):
    """Validate the generated dataset"""
    print(f"Validating dataset (checking {num_episodes_to_check} episodes)...")
    
    validation_results = {
        'valid_episodes': 0,
        'invalid_episodes': 0,
        'errors': []
    }
    
    for episode in range(min(num_episodes_to_check, 100)):
        episode_dir = os.path.join(base_path, f"episode_{episode:04d}")
        
        try:
            # Check if all required files exist
            required_files = [
                "dic_data.h5",
                "furnace_data.parquet",
                "rl_data.pkl",
                "metadata.json"
            ]
            
            missing_files = []
            for file in required_files:
                if not os.path.exists(os.path.join(episode_dir, file)):
                    missing_files.append(file)
            
            if missing_files:
                validation_results['invalid_episodes'] += 1
                validation_results['errors'].append(f"Episode {episode}: Missing files {missing_files}")
            else:
                # Try to load data
                import h5py
                import pandas as pd
                import pickle
                
                # Load and check DIC data
                with h5py.File(os.path.join(episode_dir, "dic_data.h5"), 'r') as f:
                    if 'timestamps' not in f or 'displacement_fields' not in f:
                        raise ValueError("Missing DIC data components")
                
                # Load and check furnace data
                furnace_df = pd.read_parquet(os.path.join(episode_dir, "furnace_data.parquet"))
                if furnace_df.empty:
                    raise ValueError("Empty furnace data")
                
                # Load and check RL data
                with open(os.path.join(episode_dir, "rl_data.pkl"), 'rb') as f:
                    rl_data = pickle.load(f)
                    if not all(key in rl_data for key in ['states', 'actions', 'rewards']):
                        raise ValueError("Missing RL data components")
                
                validation_results['valid_episodes'] += 1
                
        except Exception as e:
            validation_results['invalid_episodes'] += 1
            validation_results['errors'].append(f"Episode {episode}: {str(e)}")
    
    print(f"Validation complete:")
    print(f"  Valid episodes: {validation_results['valid_episodes']}")
    print(f"  Invalid episodes: {validation_results['invalid_episodes']}")
    
    if validation_results['errors']:
        print("Errors found:")
        for error in validation_results['errors'][:5]:  # Show first 5 errors
            print(f"  {error}")
        if len(validation_results['errors']) > 5:
            print(f"  ... and {len(validation_results['errors']) - 5} more errors")
    
    return validation_results

def main():
    parser = argparse.ArgumentParser(description='Generate real-time training dataset')
    parser.add_argument('--base_path', type=str, default='/workspace/realtime_training_dataset',
                       help='Base path for dataset')
    parser.add_argument('--episodes', type=int, default=100,
                       help='Number of episodes to generate')
    parser.add_argument('--processes', type=int, default=None,
                       help='Number of processes for parallel generation')
    parser.add_argument('--skip_generation', action='store_true',
                       help='Skip dataset generation (useful for testing other components)')
    parser.add_argument('--skip_visualization', action='store_true',
                       help='Skip visualization generation')
    parser.add_argument('--skip_validation', action='store_true',
                       help='Skip dataset validation')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("REAL-TIME TRAINING DATASET GENERATION")
    print("=" * 60)
    print(f"Base path: {args.base_path}")
    print(f"Episodes: {args.episodes}")
    print(f"Processes: {args.processes or 'auto'}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    total_start_time = time.time()
    
    # Create base directory
    os.makedirs(args.base_path, exist_ok=True)
    
    # Dataset generation
    if not args.skip_generation:
        print("\n1. GENERATING DATASET")
        print("-" * 30)
        
        if args.processes == 1:
            # Single process generation
            generator = RealTimeDatasetGenerator(args.base_path)
            generator.total_episodes = args.episodes
            generator.generate_complete_dataset()
        else:
            # Parallel generation
            generator = parallel_generation(args.base_path, args.episodes, args.processes)
        
        print("Dataset generation completed!")
    else:
        print("\n1. SKIPPING DATASET GENERATION")
    
    # Visualization
    if not args.skip_visualization:
        print("\n2. GENERATING VISUALIZATIONS")
        print("-" * 30)
        create_sample_visualizations(args.base_path)
        print("Visualization generation completed!")
    else:
        print("\n2. SKIPPING VISUALIZATION GENERATION")
    
    # Validation
    if not args.skip_validation:
        print("\n3. VALIDATING DATASET")
        print("-" * 30)
        validation_results = validate_dataset(args.base_path)
        print("Dataset validation completed!")
    else:
        print("\n3. SKIPPING DATASET VALIDATION")
    
    total_end_time = time.time()
    
    print("\n" + "=" * 60)
    print("DATASET GENERATION SUMMARY")
    print("=" * 60)
    print(f"Total time: {total_end_time - total_start_time:.2f} seconds")
    print(f"Episodes generated: {args.episodes}")
    print(f"Dataset location: {args.base_path}")
    print(f"Completion time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Calculate estimated dataset size
    if os.path.exists(args.base_path):
        total_size = 0
        for root, dirs, files in os.walk(args.base_path):
            for file in files:
                total_size += os.path.getsize(os.path.join(root, file))
        
        size_gb = total_size / (1024**3)
        print(f"Dataset size: {size_gb:.2f} GB")
    
    print("=" * 60)
    
    # Save generation log
    generation_log = {
        'generation_time': datetime.now().isoformat(),
        'total_episodes': args.episodes,
        'processes_used': args.processes,
        'total_time_seconds': total_end_time - total_start_time,
        'base_path': args.base_path,
        'skip_generation': args.skip_generation,
        'skip_visualization': args.skip_visualization,
        'skip_validation': args.skip_validation
    }
    
    if not args.skip_validation:
        generation_log['validation_results'] = validation_results
    
    log_path = os.path.join(args.base_path, 'generation_log.json')
    with open(log_path, 'w') as f:
        json.dump(generation_log, f, indent=2)
    
    print(f"Generation log saved to: {log_path}")

if __name__ == "__main__":
    main()