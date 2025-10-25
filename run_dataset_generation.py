#!/usr/bin/env python3
"""
Main execution script for Real-Time Training & Validation Dataset Generation

This script orchestrates the complete dataset generation process including:
- High-frequency DIC data streams
- Synchronized furnace control & sensor data
- RL state-action-reward-next_state tuples
- Comprehensive visualization and analysis
"""

import os
import sys
import argparse
import time
from datetime import datetime
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dataset_generator import RealTimeDatasetGenerator
from data_visualizer import DatasetVisualizer
from data_loader import RealTimeDataLoader, DatasetConfig, DataAnalyzer

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Generate Real-Time Training & Validation Dataset')
    parser.add_argument('--duration', type=float, default=8.0, 
                       help='Sample duration in hours (default: 8.0)')
    parser.add_argument('--dic-fps', type=int, default=30, 
                       help='DIC camera frame rate (default: 30)')
    parser.add_argument('--furnace-freq', type=float, default=1.0, 
                       help='Furnace update frequency in Hz (default: 1.0)')
    parser.add_argument('--thermocouples', type=int, default=12, 
                       help='Number of thermocouples (default: 12)')
    parser.add_argument('--heating-zones', type=int, default=6, 
                       help='Number of heating zones (default: 6)')
    parser.add_argument('--image-width', type=int, default=1920, 
                       help='DIC image width (default: 1920)')
    parser.add_argument('--image-height', type=int, default=1080, 
                       help='DIC image height (default: 1080)')
    parser.add_argument('--output-dir', type=str, default='real_time_dataset', 
                       help='Output directory (default: real_time_dataset)')
    parser.add_argument('--skip-generation', action='store_true', 
                       help='Skip dataset generation, only run analysis')
    parser.add_argument('--skip-visualization', action='store_true', 
                       help='Skip visualization generation')
    parser.add_argument('--skip-analysis', action='store_true', 
                       help='Skip data analysis')
    parser.add_argument('--create-animations', action='store_true', 
                       help='Create animated visualizations')
    parser.add_argument('--batch-size', type=int, default=32, 
                       help='Batch size for data loading (default: 32)')
    parser.add_argument('--sequence-length', type=int, default=10, 
                       help='Sequence length for time series models (default: 10)')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("REAL-TIME TRAINING & VALIDATION DATASET GENERATOR")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Configuration:")
    print(f"  Duration: {args.duration} hours")
    print(f"  DIC FPS: {args.dic_fps}")
    print(f"  Furnace Frequency: {args.furnace_freq} Hz")
    print(f"  Thermocouples: {args.thermocouples}")
    print(f"  Heating Zones: {args.heating_zones}")
    print(f"  Image Resolution: {args.image_width}x{args.image_height}")
    print(f"  Output Directory: {args.output_dir}")
    print("=" * 80)
    
    start_time = time.time()
    
    # Step 1: Generate Dataset
    if not args.skip_generation:
        print("\n" + "=" * 60)
        print("STEP 1: GENERATING DATASET")
        print("=" * 60)
        
        generator = RealTimeDatasetGenerator(
            sample_duration_hours=args.duration,
            dic_fps=args.dic_fps,
            furnace_update_freq=args.furnace_freq,
            num_thermocouples=args.thermocouples,
            num_heating_zones=args.heating_zones,
            image_resolution=(args.image_width, args.image_height)
        )
        
        # Generate DIC data
        print("\n1.1 Generating DIC Data Stream...")
        dic_data = generator.generate_dic_data_stream()
        
        # Generate furnace data
        print("\n1.2 Generating Furnace Control Data...")
        furnace_data = generator.generate_furnace_control_data()
        
        # Generate RL data
        print("\n1.3 Generating RL State Representation...")
        rl_data = generator.generate_rl_state_representation(dic_data, furnace_data)
        
        # Save dataset
        print("\n1.4 Saving Complete Dataset...")
        generator.save_dataset(dic_data, furnace_data, rl_data, args.output_dir)
        
        generation_time = time.time() - start_time
        print(f"\nDataset generation completed in {generation_time:.2f} seconds")
        
        # Save generation metadata
        generation_metadata = {
            'generation_time_seconds': generation_time,
            'generation_timestamp': datetime.now().isoformat(),
            'configuration': vars(args),
            'dataset_size_gb': generator._calculate_dataset_size(args.output_dir)
        }
        
        with open(f"{args.output_dir}/generation_metadata.json", 'w') as f:
            json.dump(generation_metadata, f, indent=2)
    
    # Step 2: Generate Visualizations
    if not args.skip_visualization:
        print("\n" + "=" * 60)
        print("STEP 2: GENERATING VISUALIZATIONS")
        print("=" * 60)
        
        visualizer = DatasetVisualizer(args.output_dir)
        
        # Generate static visualizations
        print("\n2.1 Generating DIC Visualizations...")
        visualizer.visualize_dic_data()
        
        print("\n2.2 Generating Furnace Visualizations...")
        visualizer.visualize_furnace_data()
        
        print("\n2.3 Generating RL Visualizations...")
        visualizer.visualize_rl_data()
        
        # Generate animations if requested
        if args.create_animations:
            print("\n2.4 Creating Animations...")
            visualizer.create_animation("displacement", frame_skip=20)
            visualizer.create_animation("strain", frame_skip=20)
            visualizer.create_animation("temperature", frame_skip=20)
        
        print("\nVisualization generation completed")
    
    # Step 3: Data Analysis
    if not args.skip_analysis:
        print("\n" + "=" * 60)
        print("STEP 3: DATA ANALYSIS")
        print("=" * 60)
        
        # Initialize data loader
        config = DatasetConfig(
            dataset_dir=args.output_dir,
            batch_size=args.batch_size,
            sequence_length=args.sequence_length,
            normalize_data=True
        )
        
        data_loader = RealTimeDataLoader(config)
        analyzer = DataAnalyzer(data_loader)
        
        # Generate comprehensive report
        print("\n3.1 Generating Data Quality Report...")
        report = visualizer.generate_data_report()
        
        print("\n3.2 Analyzing Temporal Correlations...")
        correlations = analyzer.analyze_temporal_correlations()
        
        print("\n3.3 Analyzing Frequency Content...")
        frequency_analysis = analyzer.analyze_frequency_content()
        
        print("\n3.4 Analyzing Data Quality...")
        quality_analysis = analyzer.analyze_data_quality()
        
        # Save analysis results
        analysis_results = {
            'correlations': correlations,
            'frequency_analysis': frequency_analysis,
            'quality_analysis': quality_analysis,
            'data_statistics': data_loader.get_data_statistics()
        }
        
        with open(f"{args.output_dir}/analysis_results.json", 'w') as f:
            json.dump(analysis_results, f, indent=2)
        
        print("\nData analysis completed")
    
    # Step 4: Generate Summary Report
    print("\n" + "=" * 60)
    print("STEP 4: GENERATING SUMMARY REPORT")
    print("=" * 60)
    
    # Load metadata
    with open(f"{args.output_dir}/metadata.json", 'r') as f:
        metadata = json.load(f)
    
    # Generate summary
    total_time = time.time() - start_time
    
    summary = {
        'execution_summary': {
            'total_execution_time_seconds': total_time,
            'completion_timestamp': datetime.now().isoformat(),
            'configuration': vars(args),
            'dataset_metadata': metadata
        },
        'dataset_contents': {
            'dic_frames': metadata['total_dic_frames'],
            'furnace_updates': metadata['total_furnace_updates'],
            'rl_tuples': metadata['rl_tuples'],
            'dataset_size_gb': metadata.get('dataset_size_gb', 'Unknown')
        },
        'files_generated': [
            'dic_data.h5 - DIC video frames and displacement/strain data',
            'furnace_data.h5 - Furnace control and sensor data',
            'rl_data.h5 - RL state-action-reward-next_state tuples',
            'metadata.json - Dataset metadata and configuration',
            'dic_displacement_fields.png - DIC displacement field visualizations',
            'dic_strain_fields.png - DIC strain field visualizations',
            'dic_metrics_evolution.png - DIC metrics over time',
            'furnace_temperature_profiles.png - Temperature profile visualizations',
            'furnace_actions.png - Furnace action visualizations',
            'furnace_spatial_layout.png - Spatial layout visualizations',
            'rl_data_evolution.png - RL data evolution visualizations',
            'rl_correlation_matrices.png - Correlation matrix visualizations',
            'rl_reward_analysis.png - Reward function analysis',
            'data_quality_report.json - Comprehensive data quality report',
            'analysis_results.json - Detailed analysis results'
        ]
    }
    
    if args.create_animations:
        summary['files_generated'].extend([
            'displacement_animation.gif - Animated displacement fields',
            'strain_animation.gif - Animated strain fields',
            'temperature_animation.gif - Animated temperature fields'
        ])
    
    # Save summary
    with open(f"{args.output_dir}/execution_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print final summary
    print("\n" + "=" * 80)
    print("EXECUTION COMPLETE")
    print("=" * 80)
    print(f"Total execution time: {total_time:.2f} seconds")
    print(f"Dataset location: {args.output_dir}/")
    print(f"Files generated: {len(summary['files_generated'])}")
    print(f"DIC frames: {metadata['total_dic_frames']:,}")
    print(f"Furnace updates: {metadata['total_furnace_updates']:,}")
    print(f"RL training tuples: {metadata['rl_tuples']:,}")
    print("=" * 80)
    
    print("\nDataset is ready for:")
    print("  - Reinforcement Learning training")
    print("  - Digital Twin validation")
    print("  - Process optimization")
    print("  - Real-time control system development")
    
    print(f"\nSummary report saved to: {args.output_dir}/execution_summary.json")

if __name__ == "__main__":
    main()