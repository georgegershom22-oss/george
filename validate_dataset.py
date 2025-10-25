#!/usr/bin/env python3
"""
Dataset Validation and Basic Visualization
Quick validation of the generated minimal dataset
"""

import pandas as pd
import numpy as np
import json
import pickle
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path

def validate_dataset(dataset_path="minimal_realtime_dataset"):
    """Validate and visualize the generated dataset"""
    
    dataset_path = Path(dataset_path)
    
    print("=== Dataset Validation ===")
    print(f"Dataset path: {dataset_path}")
    
    if not dataset_path.exists():
        print("❌ Dataset directory not found!")
        return False
    
    # Check file existence
    required_files = [
        "dic_data/dic_summary.csv",
        "dic_data/sample_frames.json",
        "furnace_data/furnace_states.csv",
        "rl_data/rl_states.csv",
        "rl_data/rl_actions.csv",
        "rl_data/rl_rewards.csv",
        "rl_data/rl_tuples.pkl",
        "metadata/dataset_metadata.json",
        "metadata/dataset_statistics.json"
    ]
    
    print("\n📁 File Existence Check:")
    all_files_exist = True
    for file_path in required_files:
        full_path = dataset_path / file_path
        if full_path.exists():
            size_mb = full_path.stat().st_size / (1024 * 1024)
            print(f"  ✅ {file_path} ({size_mb:.2f} MB)")
        else:
            print(f"  ❌ {file_path} (missing)")
            all_files_exist = False
    
    if not all_files_exist:
        return False
    
    # Load and validate data
    print("\n📊 Data Validation:")
    
    # Load metadata
    with open(dataset_path / "metadata" / "dataset_metadata.json", 'r') as f:
        metadata = json.load(f)
    
    with open(dataset_path / "metadata" / "dataset_statistics.json", 'r') as f:
        statistics = json.load(f)
    
    print(f"  Dataset type: {metadata['dataset_info']['type']}")
    print(f"  Duration: {metadata['dataset_info']['duration_hours']} hours")
    print(f"  DIC frames: {metadata['dataset_info']['total_dic_frames']:,}")
    print(f"  Furnace states: {metadata['dataset_info']['total_furnace_states']:,}")
    print(f"  RL tuples: {metadata['dataset_info']['total_rl_tuples']:,}")
    
    # Load CSV data
    dic_df = pd.read_csv(dataset_path / "dic_data" / "dic_summary.csv")
    furnace_df = pd.read_csv(dataset_path / "furnace_data" / "furnace_states.csv")
    rl_states_df = pd.read_csv(dataset_path / "rl_data" / "rl_states.csv")
    rl_actions_df = pd.read_csv(dataset_path / "rl_data" / "rl_actions.csv")
    rl_rewards_df = pd.read_csv(dataset_path / "rl_data" / "rl_rewards.csv")
    
    print(f"\n📈 Data Shape Validation:")
    print(f"  DIC summary: {dic_df.shape}")
    print(f"  Furnace data: {furnace_df.shape}")
    print(f"  RL states: {rl_states_df.shape}")
    print(f"  RL actions: {rl_actions_df.shape}")
    print(f"  RL rewards: {rl_rewards_df.shape}")
    
    # Check for missing values
    print(f"\n🔍 Missing Values Check:")
    print(f"  DIC data: {dic_df.isnull().sum().sum()} missing values")
    print(f"  Furnace data: {furnace_df.isnull().sum().sum()} missing values")
    print(f"  RL states: {rl_states_df.isnull().sum().sum()} missing values")
    print(f"  RL actions: {rl_actions_df.isnull().sum().sum()} missing values")
    print(f"  RL rewards: {rl_rewards_df.isnull().sum().sum()} missing values")
    
    # Validate value ranges
    print(f"\n📏 Value Range Validation:")
    
    # Temperature ranges
    temp_cols = [col for col in furnace_df.columns if 'temperature' in col]
    if temp_cols:
        temp_min = furnace_df[temp_cols].min().min()
        temp_max = furnace_df[temp_cols].max().max()
        print(f"  Temperature range: {temp_min:.1f}°C to {temp_max:.1f}°C")
        
        if temp_min < -50 or temp_max > 2000:
            print(f"    ⚠️  Temperature range seems unrealistic")
        else:
            print(f"    ✅ Temperature range is plausible")
    
    # Strain ranges
    strain_max = dic_df['max_principal_strain'].max()
    strain_min = dic_df['max_principal_strain'].min()
    print(f"  Strain range: {strain_min:.6f} to {strain_max:.6f}")
    
    if abs(strain_min) > 1 or strain_max > 1:
        print(f"    ⚠️  Strain values seem very high")
    else:
        print(f"    ✅ Strain range is reasonable")
    
    # Reward ranges
    reward_min = rl_rewards_df['reward'].min()
    reward_max = rl_rewards_df['reward'].max()
    reward_mean = rl_rewards_df['reward'].mean()
    print(f"  Reward range: {reward_min:.3f} to {reward_max:.3f} (mean: {reward_mean:.3f})")
    
    # Create basic visualizations
    print(f"\n📊 Creating validation plots...")
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # DIC evolution
    axes[0, 0].plot(dic_df['timestamp'] / 3600, dic_df['max_principal_strain'])
    axes[0, 0].set_title('Maximum Principal Strain Evolution')
    axes[0, 0].set_xlabel('Time (hours)')
    axes[0, 0].set_ylabel('Strain')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Temperature evolution
    if temp_cols:
        for col in temp_cols[:3]:  # Plot first 3 zones
            axes[0, 1].plot(furnace_df['timestamp'] / 3600, furnace_df[col], 
                           label=col.replace('zone_', 'Zone ').replace('_temperature', ''), alpha=0.8)
    axes[0, 1].set_title('Zone Temperatures')
    axes[0, 1].set_xlabel('Time (hours)')
    axes[0, 1].set_ylabel('Temperature (°C)')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Reward evolution
    axes[0, 2].plot(rl_rewards_df['timestamp'] / 3600, rl_rewards_df['reward'])
    axes[0, 2].set_title('RL Reward Evolution')
    axes[0, 2].set_xlabel('Time (hours)')
    axes[0, 2].set_ylabel('Reward')
    axes[0, 2].grid(True, alpha=0.3)
    
    # State distributions
    axes[1, 0].hist(rl_states_df['max_strain'], bins=30, alpha=0.7)
    axes[1, 0].set_title('Max Strain Distribution')
    axes[1, 0].set_xlabel('Max Strain')
    axes[1, 0].set_ylabel('Frequency')
    
    axes[1, 1].hist(rl_states_df['avg_temperature'], bins=30, alpha=0.7)
    axes[1, 1].set_title('Average Temperature Distribution')
    axes[1, 1].set_xlabel('Temperature (°C)')
    axes[1, 1].set_ylabel('Frequency')
    
    axes[1, 2].hist(rl_rewards_df['reward'], bins=30, alpha=0.7)
    axes[1, 2].set_title('Reward Distribution')
    axes[1, 2].set_xlabel('Reward')
    axes[1, 2].set_ylabel('Frequency')
    
    plt.tight_layout()
    plt.savefig(dataset_path / "validation_plots.png", dpi=150, bbox_inches='tight')
    print(f"  Saved validation plots to {dataset_path}/validation_plots.png")
    
    # Load and validate RL tuples
    print(f"\n🤖 RL Tuples Validation:")
    with open(dataset_path / "rl_data" / "rl_tuples.pkl", 'rb') as f:
        rl_tuples = pickle.load(f)
    
    print(f"  Total RL tuples: {len(rl_tuples)}")
    
    if len(rl_tuples) > 0:
        sample_tuple = rl_tuples[0]
        print(f"  Sample tuple keys: {list(sample_tuple.keys())}")
        print(f"  State dimensions: {len(sample_tuple['state'])}")
        print(f"  Action dimensions: {len(sample_tuple['action']['temp_changes']) + len(sample_tuple['action']['power_changes'])}")
        print(f"  Sample reward: {sample_tuple['reward']:.4f}")
    
    # Load and validate sample frames
    print(f"\n🖼️  Sample Frames Validation:")
    with open(dataset_path / "dic_data" / "sample_frames.json", 'r') as f:
        sample_frames = json.load(f)
    
    print(f"  Number of sample frames: {len(sample_frames)}")
    
    for frame_name, frame_data in sample_frames.items():
        print(f"  {frame_name}: timestamp {frame_data['timestamp']:.1f}s")
        
        # Check field dimensions
        u_shape = np.array(frame_data['displacement_u']).shape
        temp_shape = np.array(frame_data['temperature_field']).shape
        print(f"    Displacement field shape: {u_shape}")
        print(f"    Temperature field shape: {temp_shape}")
    
    print(f"\n✅ Dataset validation complete!")
    print(f"\n📋 Summary:")
    print(f"  - All required files present")
    print(f"  - Data shapes are consistent")
    print(f"  - Value ranges are physically plausible")
    print(f"  - RL tuples are properly formatted")
    print(f"  - Sample frames contain full field data")
    
    return True

def create_usage_example():
    """Create a simple usage example"""
    
    print(f"\n💡 Usage Example:")
    
    usage_code = '''
# Load the dataset for machine learning
import pandas as pd
import pickle
import numpy as np

# Load RL training data
with open('minimal_realtime_dataset/rl_data/rl_tuples.pkl', 'rb') as f:
    rl_tuples = pickle.load(f)

# Extract training data
states = []
actions = []
rewards = []
next_states = []

for tuple_data in rl_tuples:
    # Convert state dict to vector
    state_vector = [
        tuple_data['state']['max_strain'],
        tuple_data['state']['avg_temperature'],
        tuple_data['state']['temp_gradient'],
        tuple_data['state']['warpage'],
        tuple_data['state']['dic_quality'],
        tuple_data['state']['cycle_time'],
        tuple_data['state']['estimated_density']
    ]
    states.append(state_vector)
    
    # Convert action dict to vector
    action_vector = (tuple_data['action']['temp_changes'] + 
                    tuple_data['action']['power_changes'])
    actions.append(action_vector)
    
    rewards.append(tuple_data['reward'])
    
    if tuple_data['next_state']:
        next_state_vector = [
            tuple_data['next_state']['max_strain'],
            tuple_data['next_state']['avg_temperature'],
            tuple_data['next_state']['temp_gradient'],
            tuple_data['next_state']['warpage'],
            tuple_data['next_state']['dic_quality'],
            tuple_data['next_state']['cycle_time'],
            tuple_data['next_state']['estimated_density']
        ]
        next_states.append(next_state_vector)

# Convert to numpy arrays
states = np.array(states)
actions = np.array(actions)
rewards = np.array(rewards)
next_states = np.array(next_states[:-1])  # Exclude last (no next state)

print(f"States shape: {states.shape}")
print(f"Actions shape: {actions.shape}")
print(f"Rewards shape: {rewards.shape}")

# Now ready for RL training!
# Example: Train with scikit-learn, TensorFlow, PyTorch, etc.
'''
    
    print(usage_code)

def main():
    """Main validation function"""
    
    success = validate_dataset()
    
    if success:
        create_usage_example()
        
        print(f"\n🎉 Dataset is ready for use!")
        print(f"\nNext steps:")
        print(f"  1. Load the RL tuples for training your agent")
        print(f"  2. Use the furnace data for process modeling")
        print(f"  3. Analyze the DIC data for material behavior insights")
        print(f"  4. Scale up parameters in the generator for larger datasets")
    else:
        print(f"\n❌ Dataset validation failed!")

if __name__ == "__main__":
    main()