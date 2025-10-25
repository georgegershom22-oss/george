#!/usr/bin/env python3
"""
Simple test script to verify dataset structure without heavy dependencies
"""

import os
import json
from datetime import datetime

def create_test_episode(base_path: str, episode_id: int):
    """Create a minimal test episode structure"""
    episode_dir = os.path.join(base_path, f"episode_{episode_id:04d}")
    os.makedirs(episode_dir, exist_ok=True)
    
    # Create dummy metadata
    metadata = {
        'episode_id': episode_id,
        'duration': 3600,
        'dic_samples': 360,
        'furnace_samples': 360,
        'rl_samples': 3600,
        'generation_time': datetime.now().isoformat()
    }
    
    with open(os.path.join(episode_dir, "metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Create dummy data files (empty for now)
    dummy_files = [
        "dic_data.h5",
        "furnace_data.parquet", 
        "rl_data.pkl"
    ]
    
    for filename in dummy_files:
        filepath = os.path.join(episode_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f"# Dummy {filename} file for episode {episode_id}\n")
    
    print(f"Created test episode {episode_id}")

def create_dataset_structure(base_path: str):
    """Create the complete dataset directory structure"""
    
    # Main directories
    directories = [
        "dic_data/video_streams",
        "dic_data/displacement_fields", 
        "dic_data/strain_fields",
        "dic_data/metadata",
        "furnace_data/control_commands",
        "furnace_data/temperature_readings",
        "furnace_data/gas_atmosphere",
        "rl_data/states",
        "rl_data/actions", 
        "rl_data/rewards",
        "rl_data/transitions",
        "utils/visualization",
        "utils/preprocessing",
        "config",
        "examples",
        "sample_visualizations",
        "training_results"
    ]
    
    for directory in directories:
        full_path = os.path.join(base_path, directory)
        os.makedirs(full_path, exist_ok=True)
    
    # Create dataset summary
    summary = {
        'dataset_info': {
            'total_episodes': 10,
            'episode_duration': 3600,
            'total_duration_hours': 10,
            'dic_fps': 100,
            'furnace_fps': 10,
            'rl_fps': 1
        },
        'physical_parameters': {
            'sample_size_mm': [50, 50],
            'image_resolution': [2048, 2048],
            'num_cameras': 2,
            'num_heating_zones': 6,
            'num_thermocouples': 12,
            'max_temperature_c': 1200,
            'target_density': 0.95
        },
        'data_volumes': {
            'estimated_total_size_gb': 5,
            'dic_data_gb': 3.5,
            'furnace_data_gb': 1,
            'rl_data_gb': 0.5
        },
        'generation_info': {
            'generated_on': datetime.now().isoformat(),
            'generator_version': '1.0.0'
        }
    }
    
    with open(os.path.join(base_path, "dataset_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Create test episodes
    for episode in range(10):
        create_test_episode(base_path, episode)
    
    print(f"Dataset structure created at: {base_path}")
    print(f"Total directories created: {len(directories)}")
    print("Test episodes: 0-9")

def verify_structure(base_path: str):
    """Verify the dataset structure is correct"""
    print("\nVerifying dataset structure...")
    
    # Check main files
    required_files = [
        "README.md",
        "DATASET_SPECIFICATION.md", 
        "QUICKSTART.md",
        "requirements.txt",
        "dataset_summary.json",
        "generate_dataset.py",
        "run_dataset_generation.py",
        "train_agents.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(os.path.join(base_path, file)):
            missing_files.append(file)
    
    if missing_files:
        print(f"Missing files: {missing_files}")
    else:
        print("✓ All required files present")
    
    # Check episode structure
    episodes_found = 0
    for i in range(10):
        episode_dir = os.path.join(base_path, f"episode_{i:04d}")
        if os.path.exists(episode_dir):
            episodes_found += 1
            
            # Check episode files
            episode_files = ["metadata.json", "dic_data.h5", "furnace_data.parquet", "rl_data.pkl"]
            for file in episode_files:
                if not os.path.exists(os.path.join(episode_dir, file)):
                    print(f"Missing {file} in episode {i}")
    
    print(f"✓ Episodes found: {episodes_found}/10")
    
    # Check directory structure
    key_dirs = ["utils", "rl_models", "config", "examples"]
    for dir_name in key_dirs:
        if os.path.exists(os.path.join(base_path, dir_name)):
            print(f"✓ {dir_name}/ directory exists")
        else:
            print(f"✗ {dir_name}/ directory missing")

if __name__ == "__main__":
    base_path = "/workspace/realtime_training_dataset"
    
    print("Creating test dataset structure...")
    create_dataset_structure(base_path)
    
    print("\nVerifying structure...")
    verify_structure(base_path)
    
    print("\n" + "="*50)
    print("TEST DATASET CREATION COMPLETE")
    print("="*50)
    print(f"Location: {base_path}")
    print("Status: Ready for testing")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run examples: python3 examples/basic_usage.py")
    print("3. Generate full dataset: python3 run_dataset_generation.py --episodes 100")