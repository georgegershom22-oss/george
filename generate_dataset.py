#!/usr/bin/env python3
"""
Main Dataset Generation Script
Phase 2: Core Real-Time Training & Validation Data

This script generates a comprehensive dataset for training and validating
a Digital Twin and Reinforcement Learning system for ceramic sintering.

Usage:
    python generate_dataset.py [--config CONFIG_FILE] [--episodes N] [--output DIR]

Author: AI Assistant
Date: 2024
"""

import argparse
import os
import sys
import time
import yaml
from datetime import datetime
import numpy as np
import pandas as pd

# Import our modules
from dataset_generator import DatasetGenerator
from advanced_data_generator import AdvancedDICGenerator, AdvancedFurnaceSimulator, AdvancedStrainAnalyzer, DataVisualizer
from data_validator import DataValidator
from data_analyzer import DataAnalyzer

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate Real-Time Training & Validation Dataset')
    
    parser.add_argument('--config', '-c', type=str, default='config.yaml',
                       help='Configuration file path (default: config.yaml)')
    parser.add_argument('--episodes', '-e', type=int, default=50,
                       help='Number of episodes to generate (default: 50)')
    parser.add_argument('--output', '-o', type=str, default='real_time_training_dataset',
                       help='Output directory (default: real_time_training_dataset)')
    parser.add_argument('--validate', '-v', action='store_true',
                       help='Run validation after generation')
    parser.add_argument('--analyze', '-a', action='store_true',
                       help='Run analysis after generation')
    parser.add_argument('--visualize', '--viz', action='store_true',
                       help='Generate visualizations during generation')
    parser.add_argument('--material', '-m', type=str, default='alumina',
                       choices=['alumina', 'zirconia', 'silicon_carbide'],
                       help='Material type (default: alumina)')
    parser.add_argument('--duration', '-d', type=int, default=3600,
                       help='Episode duration in seconds (default: 3600)')
    parser.add_argument('--fps', type=int, default=120,
                       help='DIC video frame rate (default: 120)')
    parser.add_argument('--resolution', type=str, default='1920x1080',
                       help='DIC video resolution (default: 1920x1080)')
    
    return parser.parse_args()

def load_config(config_path):
    """Load configuration from file."""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print(f"Loaded configuration from {config_path}")
        return config
    else:
        print(f"Configuration file {config_path} not found. Using defaults.")
        return None

def update_config_with_args(config, args):
    """Update configuration with command line arguments."""
    if config is None:
        config = {}
    
    # Update with command line arguments
    if 'dic' not in config:
        config['dic'] = {}
    
    config['dic']['duration'] = args.duration
    config['dic']['fps'] = args.fps
    
    # Parse resolution
    width, height = map(int, args.resolution.split('x'))
    config['dic']['width'] = width
    config['dic']['height'] = height
    config['dic']['material_type'] = args.material
    
    if 'dataset' not in config:
        config['dataset'] = {}
    
    config['dataset']['num_episodes'] = args.episodes
    config['dataset']['output_dir'] = args.output
    
    return config

def print_banner():
    """Print program banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║        Real-Time Training & Validation Dataset Generator                     ║
    ║                    Phase 2: Core Real-Time Data                              ║
    ║                                                                              ║
    ║  🎯 Purpose: Generate comprehensive dataset for Digital Twin and RL training ║
    ║  🔬 Features: DIC video streams, furnace control, strain analysis, RL tuples ║
    ║  🚀 Capabilities: Multi-objective optimization, realistic material behavior  ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_progress(episode, total_episodes, start_time):
    """Print progress information."""
    elapsed = time.time() - start_time
    progress = (episode + 1) / total_episodes
    eta = elapsed / progress - elapsed if progress > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"Episode {episode + 1}/{total_episodes} ({progress*100:.1f}%)")
    print(f"Elapsed: {elapsed/60:.1f} min, ETA: {eta/60:.1f} min")
    print(f"{'='*60}")

def generate_dataset(config, args):
    """Generate the complete dataset."""
    print("🚀 Starting dataset generation...")
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Initialize generator
    generator = DatasetGenerator(config)
    
    # Generate episodes
    start_time = time.time()
    episodes = []
    
    print(f"📊 Generating {args.episodes} episodes...")
    print(f"🎬 DIC Video: {args.resolution} @ {args.fps} FPS")
    print(f"⏱️  Duration: {args.duration} seconds per episode")
    print(f"🧪 Material: {args.material}")
    
    for episode in range(args.episodes):
        print_progress(episode, args.episodes, start_time)
        
        # Generate single episode
        episode_data = generator.generate_single_episode(
            episode_id=episode,
            duration=args.duration,
            material_type=args.material,
            visualize=args.visualize
        )
        
        episodes.extend(episode_data)
        
        # Save intermediate results every 10 episodes
        if (episode + 1) % 10 == 0:
            generator.save_intermediate_results(episodes, args.output, episode + 1)
    
    # Save final dataset
    print("\n💾 Saving final dataset...")
    generator.save_final_dataset(episodes, args.output)
    
    total_time = time.time() - start_time
    print(f"\n✅ Dataset generation complete!")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes")
    print(f"📁 Output directory: {args.output}")
    print(f"📊 Total timesteps: {len(episodes)}")
    print(f"🎬 Episodes: {args.episodes}")
    
    return episodes

def run_validation(dataset_path, config):
    """Run dataset validation."""
    print("\n🔍 Running dataset validation...")
    
    validator = DataValidator(config)
    validation_results = validator.validate_dataset(dataset_path)
    
    # Print validation summary
    print("\n📋 Validation Results:")
    for category, results in validation_results.items():
        if category != 'overall_score':
            status = "✅ PASSED" if results['passed'] else "❌ FAILED"
            print(f"  {category}: {status}")
            if results['issues']:
                for issue in results['issues']:
                    print(f"    - {issue}")
    
    print(f"\n🎯 Overall Score: {validation_results['overall_score']:.2f}")
    
    # Generate validation report
    validator.generate_validation_report(f"{dataset_path}/validation_report.html")
    validator.plot_validation_summary(f"{dataset_path}/validation_summary.png")
    
    return validation_results

def run_analysis(dataset_path):
    """Run dataset analysis."""
    print("\n📈 Running dataset analysis...")
    
    analyzer = DataAnalyzer(dataset_path)
    analyzer.generate_comprehensive_report(f"{dataset_path}/comprehensive_analysis_report.html")
    
    print("✅ Analysis complete! Check the generated reports and plots.")

def generate_summary_report(dataset_path, episodes, validation_results, args):
    """Generate a summary report."""
    print("\n📝 Generating summary report...")
    
    # Calculate basic statistics
    num_episodes = len(set(ep['episode'] for ep in episodes))
    total_timesteps = len(episodes)
    avg_episode_length = total_timesteps / num_episodes
    
    # Calculate reward statistics
    rewards = [ep['reward'] for ep in episodes]
    reward_stats = {
        'mean': np.mean(rewards),
        'std': np.std(rewards),
        'min': np.min(rewards),
        'max': np.max(rewards)
    }
    
    # Generate summary
    summary = {
        'generation_info': {
            'timestamp': datetime.now().isoformat(),
            'material_type': args.material,
            'episodes': args.episodes,
            'duration_per_episode': args.duration,
            'fps': args.fps,
            'resolution': args.resolution
        },
        'dataset_stats': {
            'total_episodes': num_episodes,
            'total_timesteps': total_timesteps,
            'avg_episode_length': avg_episode_length,
            'state_dimension': len(episodes[0]['state']) if episodes else 0,
            'action_dimension': len(episodes[0]['action']) if episodes else 0
        },
        'reward_stats': reward_stats,
        'validation_score': validation_results.get('overall_score', 0) if validation_results else 0,
        'files_generated': [
            'training_data.h5',
            'detailed_data.csv',
            'dataset_summary.json',
            'validation_report.html',
            'validation_summary.png',
            'comprehensive_analysis_report.html',
            'reward_analysis.png',
            'state_analysis.png',
            'action_analysis.png',
            'episode_progression.png',
            'physical_relationships.png'
        ]
    }
    
    # Save summary
    with open(f"{dataset_path}/generation_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 DATASET GENERATION SUMMARY")
    print("="*60)
    print(f"Material Type: {args.material}")
    print(f"Episodes Generated: {num_episodes}")
    print(f"Total Timesteps: {total_timesteps:,}")
    print(f"Average Episode Length: {avg_episode_length:.1f} timesteps")
    print(f"State Dimension: {summary['dataset_stats']['state_dimension']}")
    print(f"Action Dimension: {summary['dataset_stats']['action_dimension']}")
    print(f"Reward Range: [{reward_stats['min']:.2f}, {reward_stats['max']:.2f}]")
    print(f"Validation Score: {validation_results.get('overall_score', 0):.2f}")
    print(f"Output Directory: {dataset_path}")
    print("="*60)

def main():
    """Main function."""
    # Parse arguments
    args = parse_arguments()
    
    # Print banner
    print_banner()
    
    # Load configuration
    config = load_config(args.config)
    config = update_config_with_args(config, args)
    
    # Save updated configuration
    with open(f"{args.output}/config_used.yaml", 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    try:
        # Generate dataset
        episodes = generate_dataset(config, args)
        
        # Run validation if requested
        validation_results = None
        if args.validate:
            validation_results = run_validation(args.output, config)
        
        # Run analysis if requested
        if args.analyze:
            run_analysis(args.output)
        
        # Generate summary report
        generate_summary_report(args.output, episodes, validation_results, args)
        
        print("\n🎉 All tasks completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Generation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during generation: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()