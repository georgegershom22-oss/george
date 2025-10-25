#!/usr/bin/env python3
"""
Basic usage examples for the real-time training dataset
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import RealTimeDataset, StreamingDataLoader, create_data_loaders
from utils.visualization import DatasetVisualizer
from rl_models.environment import FurnaceControlEnv, DigitalTwinEnvironment
from rl_models.agents import PPOAgent, SACAgent

def example_1_load_and_visualize():
    """Example 1: Load dataset and create visualizations"""
    print("Example 1: Loading dataset and creating visualizations")
    print("-" * 50)
    
    base_path = "/workspace/realtime_training_dataset"
    
    # Create visualizer
    visualizer = DatasetVisualizer(base_path)
    
    # Plot episode overview
    print("Creating episode overview...")
    visualizer.plot_episode_overview(0)
    
    # Visualize strain field
    print("Creating strain field visualization...")
    visualizer.visualize_strain_field(0, frame_idx=0)
    
    # Create interactive dashboard
    print("Creating interactive dashboard...")
    fig = visualizer.create_interactive_dashboard(0)
    fig.show()
    
    print("Example 1 completed!\n")

def example_2_pytorch_dataloader():
    """Example 2: Use PyTorch DataLoader for training"""
    print("Example 2: Using PyTorch DataLoader")
    print("-" * 50)
    
    base_path = "/workspace/realtime_training_dataset"
    
    # Define episode splits
    train_episodes = list(range(0, 50))  # First 50 episodes for training
    val_episodes = list(range(50, 70))   # Next 20 for validation
    test_episodes = list(range(70, 80))  # Next 10 for testing
    
    # Create data loaders
    print("Creating data loaders...")
    train_loader, val_loader, test_loader = create_data_loaders(
        base_path, train_episodes, val_episodes, test_episodes,
        batch_size=16, sequence_length=10
    )
    
    print(f"Train batches: {len(train_loader)}")
    print(f"Validation batches: {len(val_loader)}")
    print(f"Test batches: {len(test_loader)}")
    
    # Load a sample batch
    print("\nLoading sample batch...")
    for batch in train_loader:
        print("Batch contents:")
        for key, value in batch.items():
            if hasattr(value, 'shape'):
                print(f"  {key}: {value.shape}")
            else:
                print(f"  {key}: {type(value)}")
        break
    
    print("Example 2 completed!\n")

def example_3_streaming_data():
    """Example 3: Stream data in real-time simulation"""
    print("Example 3: Streaming data simulation")
    print("-" * 50)
    
    base_path = "/workspace/realtime_training_dataset"
    
    # Create streaming data loader
    streamer = StreamingDataLoader(base_path, episode=0, buffer_size=100)
    
    print("Streaming first 10 data points...")
    
    # Stream data
    for i, sample in enumerate(streamer.stream_data(dt=1.0)):
        if i >= 10:  # Only show first 10 samples
            break
        
        print(f"Time {sample['timestamp']:.1f}s:")
        print(f"  State density: {sample['state']['current_density']:.3f}")
        print(f"  Mean temperature: {sample['state']['mean_temperature']:.1f}°C")
        if sample['action'] is not None:
            print(f"  Action (power adj): {np.array(sample['action'])}")
        print()
    
    print("Example 3 completed!\n")

def example_4_rl_environment():
    """Example 4: Use RL environment for training"""
    print("Example 4: RL Environment usage")
    print("-" * 50)
    
    base_path = "/workspace/realtime_training_dataset"
    episode_list = list(range(10))  # Use first 10 episodes
    
    # Create environment
    env = FurnaceControlEnv(base_path, episode_list, max_steps=100)
    
    print(f"Observation space: {env.observation_space}")
    print(f"Action space: {env.action_space}")
    
    # Run a few episodes
    for episode in range(3):
        print(f"\nEpisode {episode + 1}:")
        obs = env.reset()
        total_reward = 0
        steps = 0
        
        for step in range(20):  # Limit steps for demo
            # Take random action
            action = env.action_space.sample()
            obs, reward, done, info = env.step(action)
            
            total_reward += reward
            steps += 1
            
            if step % 5 == 0:  # Print every 5 steps
                print(f"  Step {step}: reward={reward:.2f}, density={obs[4]:.3f}")
            
            if done:
                break
        
        print(f"  Episode reward: {total_reward:.2f}, steps: {steps}")
    
    print("Example 4 completed!\n")

def example_5_train_agent():
    """Example 5: Train a simple RL agent"""
    print("Example 5: Training RL agent")
    print("-" * 50)
    
    base_path = "/workspace/realtime_training_dataset"
    episode_list = list(range(20))  # Use first 20 episodes
    
    # Create environment
    env = FurnaceControlEnv(base_path, episode_list, max_steps=50)
    
    # Create agent
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.shape[0]
    agent = PPOAgent(state_dim, action_dim, lr=1e-3)
    
    print(f"Training agent with state_dim={state_dim}, action_dim={action_dim}")
    
    # Training loop
    episode_rewards = []
    
    for episode in range(10):  # Short training for demo
        obs = env.reset()
        episode_reward = 0
        
        while True:
            # Get action from agent
            action, log_prob, value = agent.get_action(obs)
            
            # Take step
            next_obs, reward, done, info = env.step(action)
            
            # Store transition
            agent.store_transition(obs, action, reward, value, log_prob, done)
            
            episode_reward += reward
            obs = next_obs
            
            if done:
                break
        
        # Update agent every few episodes
        if episode % 5 == 0 and episode > 0:
            agent.update()
        
        episode_rewards.append(episode_reward)
        print(f"Episode {episode + 1}: reward = {episode_reward:.2f}")
    
    # Plot training progress
    plt.figure(figsize=(10, 6))
    plt.plot(episode_rewards)
    plt.title('Training Progress')
    plt.xlabel('Episode')
    plt.ylabel('Episode Reward')
    plt.grid(True, alpha=0.3)
    plt.show()
    
    print("Example 5 completed!\n")

def example_6_digital_twin():
    """Example 6: Use Digital Twin environment"""
    print("Example 6: Digital Twin simulation")
    print("-" * 50)
    
    base_path = "/workspace/realtime_training_dataset"
    
    # Create digital twin
    digital_twin = DigitalTwinEnvironment(base_path)
    
    # Simulate state updates
    print("Simulating digital twin state updates...")
    
    for step in range(5):
        # Simulate sensor data
        zone_powers = np.random.uniform(40, 80, 6)
        dic_data = {
            'displacement_field': np.random.random((100, 100, 3)) * 0.001,
            'strain_field': np.random.random((100, 100, 3)) * 0.0001
        }
        sensor_data = {
            'temperatures': np.random.uniform(800, 1000, 12),
            'timestamp': step * 10,
            'time_elapsed': step * 10
        }
        
        # Update digital twin
        state = digital_twin.update_state(zone_powers, dic_data, sensor_data)
        
        print(f"Step {step + 1}:")
        print(f"  Density: {state['current_density']:.3f}")
        print(f"  Max strain: {state['max_principal_strain']:.6f}")
        print(f"  Mean temp: {state['mean_temperature']:.1f}°C")
        print()
    
    # Predict future states
    print("Predicting future states...")
    control_sequence = np.random.uniform(40, 80, (5, 6))  # 5 steps, 6 zones
    predictions = digital_twin.predict_future_state(control_sequence, 5)
    
    for i, pred in enumerate(predictions):
        print(f"Prediction {i + 1}: density={pred['current_density']:.3f}, "
              f"temp={pred['mean_temperature']:.1f}°C")
    
    print("Example 6 completed!\n")

def main():
    """Run all examples"""
    print("REAL-TIME DATASET USAGE EXAMPLES")
    print("=" * 60)
    
    # Check if dataset exists
    base_path = "/workspace/realtime_training_dataset"
    if not os.path.exists(base_path):
        print(f"Dataset not found at {base_path}")
        print("Please run the dataset generation script first:")
        print("python run_dataset_generation.py --episodes 100")
        return
    
    try:
        # Run examples
        example_1_load_and_visualize()
        example_2_pytorch_dataloader()
        example_3_streaming_data()
        example_4_rl_environment()
        example_5_train_agent()
        example_6_digital_twin()
        
        print("=" * 60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure the dataset has been generated and all dependencies are installed.")

if __name__ == "__main__":
    main()