#!/usr/bin/env python3
"""
Training script for RL agents on the real-time furnace control dataset
"""

import numpy as np
import torch
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
import wandb
from tqdm import tqdm

from rl_models.environment import FurnaceControlEnv
from rl_models.agents import PPOAgent, SACAgent, MultiObjectiveAgent
from utils.data_loader import RealTimeDataset, create_data_loaders
from utils.visualization import DatasetVisualizer

class TrainingManager:
    """Manages the training process for RL agents"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.setup_environment()
        self.setup_agent()
        self.setup_logging()
        
        # Training metrics
        self.episode_rewards = []
        self.episode_lengths = []
        self.training_losses = []
        
    def setup_environment(self):
        """Setup training environment"""
        dataset_path = self.config['dataset_path']
        
        # Split episodes for training/validation
        total_episodes = self.config.get('total_episodes', 1000)
        train_split = self.config.get('train_split', 0.8)
        
        train_episodes = list(range(int(total_episodes * train_split)))
        val_episodes = list(range(int(total_episodes * train_split), total_episodes))
        
        # Create environments
        self.train_env = FurnaceControlEnv(
            dataset_path=dataset_path,
            episode_list=train_episodes,
            max_steps=self.config.get('max_steps', 3600),
            reward_weights=self.config.get('reward_weights')
        )
        
        self.val_env = FurnaceControlEnv(
            dataset_path=dataset_path,
            episode_list=val_episodes,
            max_steps=self.config.get('max_steps', 3600),
            reward_weights=self.config.get('reward_weights')
        )
        
        print(f"Training episodes: {len(train_episodes)}")
        print(f"Validation episodes: {len(val_episodes)}")
    
    def setup_agent(self):
        """Setup RL agent"""
        agent_type = self.config['agent_type']
        state_dim = self.train_env.observation_space.shape[0]
        action_dim = self.train_env.action_space.shape[0]
        
        if agent_type == 'ppo':
            self.agent = PPOAgent(
                state_dim=state_dim,
                action_dim=action_dim,
                lr=self.config.get('learning_rate', 3e-4),
                gamma=self.config.get('gamma', 0.99),
                clip_ratio=self.config.get('clip_ratio', 0.2)
            )
        elif agent_type == 'sac':
            self.agent = SACAgent(
                state_dim=state_dim,
                action_dim=action_dim,
                lr=self.config.get('learning_rate', 3e-4),
                gamma=self.config.get('gamma', 0.99),
                alpha=self.config.get('alpha', 0.2)
            )
        elif agent_type == 'multi_objective':
            self.agent = MultiObjectiveAgent(
                state_dim=state_dim,
                action_dim=action_dim,
                num_objectives=self.config.get('num_objectives', 4),
                lr=self.config.get('learning_rate', 3e-4)
            )
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        print(f"Agent type: {agent_type}")
        print(f"State dimension: {state_dim}")
        print(f"Action dimension: {action_dim}")
    
    def setup_logging(self):
        """Setup logging and experiment tracking"""
        if self.config.get('use_wandb', False):
            wandb.init(
                project="furnace-control-rl",
                config=self.config,
                name=f"{self.config['agent_type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
        
        # Create output directory
        self.output_dir = os.path.join(
            self.config.get('output_dir', 'training_results'),
            f"{self.config['agent_type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Save config
        with open(os.path.join(self.output_dir, 'config.json'), 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def train_episode(self, episode: int) -> Dict:
        """Train for one episode"""
        state = self.train_env.reset()
        episode_reward = 0
        episode_length = 0
        
        while True:
            # Get action from agent
            if self.config['agent_type'] == 'ppo':
                action, log_prob, value = self.agent.get_action(state)
                
                # Take step
                next_state, reward, done, info = self.train_env.step(action)
                
                # Store transition
                self.agent.store_transition(state, action, reward, value, log_prob, done)
                
            elif self.config['agent_type'] == 'sac':
                action = self.agent.get_action(state)
                
                # Take step
                next_state, reward, done, info = self.train_env.step(action)
                
                # Store transition
                self.agent.store_transition(state, action, reward, next_state, done)
                
            elif self.config['agent_type'] == 'multi_objective':
                action = self.agent.get_action(state)
                
                # Take step
                next_state, reward, done, info = self.train_env.step(action)
                
                # Decompose reward into objectives (simplified)
                rewards = self.decompose_reward(reward, state, next_state)
                
                # Store transition
                self.agent.store_transition(state, action, rewards, next_state, done)
            
            # Update metrics
            episode_reward += reward
            episode_length += 1
            
            # Move to next state
            state = next_state
            
            if done:
                break
        
        return {
            'episode_reward': episode_reward,
            'episode_length': episode_length,
            'final_density': state[4] if len(state) > 4 else 0.0,
            'max_strain': state[0] if len(state) > 0 else 0.0
        }
    
    def decompose_reward(self, total_reward: float, state: np.ndarray, next_state: np.ndarray) -> List[float]:
        """Decompose total reward into objective-specific rewards"""
        # Extract state components
        max_strain = next_state[0]
        strain_std = next_state[1]
        curvature = abs(next_state[2])
        temp_std = next_state[3]
        density = next_state[4]
        
        # Individual objective rewards
        warpage_reward = -curvature * 100
        strain_reward = -(max_strain + strain_std) * 100
        density_reward = (density - 0.6) * 100  # Progress towards target
        temperature_reward = -temp_std
        
        return [warpage_reward, strain_reward, density_reward, temperature_reward]
    
    def validate(self) -> Dict:
        """Run validation"""
        val_rewards = []
        val_lengths = []
        val_metrics = {
            'final_densities': [],
            'max_strains': [],
            'episode_rewards': []
        }
        
        for _ in range(self.config.get('val_episodes', 10)):
            state = self.val_env.reset()
            episode_reward = 0
            episode_length = 0
            
            while True:
                # Get deterministic action
                if self.config['agent_type'] == 'ppo':
                    action, _, _ = self.agent.get_action(state, deterministic=True)
                else:
                    action = self.agent.get_action(state, deterministic=True)
                
                next_state, reward, done, info = self.val_env.step(action)
                
                episode_reward += reward
                episode_length += 1
                state = next_state
                
                if done:
                    break
            
            val_rewards.append(episode_reward)
            val_lengths.append(episode_length)
            val_metrics['final_densities'].append(state[4] if len(state) > 4 else 0.0)
            val_metrics['max_strains'].append(state[0] if len(state) > 0 else 0.0)
            val_metrics['episode_rewards'].append(episode_reward)
        
        return {
            'mean_reward': np.mean(val_rewards),
            'std_reward': np.std(val_rewards),
            'mean_length': np.mean(val_lengths),
            'mean_final_density': np.mean(val_metrics['final_densities']),
            'mean_max_strain': np.mean(val_metrics['max_strains']),
            'success_rate': np.mean([d >= 0.9 for d in val_metrics['final_densities']])
        }
    
    def update_agent(self, episode: int):
        """Update agent networks"""
        if self.config['agent_type'] == 'ppo':
            # Update every N episodes
            if episode % self.config.get('update_frequency', 10) == 0:
                self.agent.update()
        elif self.config['agent_type'] in ['sac', 'multi_objective']:
            # Update every step (if enough data)
            self.agent.update(batch_size=self.config.get('batch_size', 256))
    
    def train(self):
        """Main training loop"""
        num_episodes = self.config.get('num_episodes', 1000)
        val_frequency = self.config.get('val_frequency', 50)
        save_frequency = self.config.get('save_frequency', 100)
        
        print(f"Starting training for {num_episodes} episodes...")
        
        best_val_reward = -np.inf
        
        for episode in tqdm(range(num_episodes), desc="Training"):
            # Train episode
            episode_metrics = self.train_episode(episode)
            
            # Update agent
            self.update_agent(episode)
            
            # Store metrics
            self.episode_rewards.append(episode_metrics['episode_reward'])
            self.episode_lengths.append(episode_metrics['episode_length'])
            
            # Validation
            if episode % val_frequency == 0:
                val_metrics = self.validate()
                
                print(f"Episode {episode}:")
                print(f"  Train reward: {episode_metrics['episode_reward']:.2f}")
                print(f"  Val reward: {val_metrics['mean_reward']:.2f} ± {val_metrics['std_reward']:.2f}")
                print(f"  Success rate: {val_metrics['success_rate']:.2f}")
                print(f"  Final density: {val_metrics['mean_final_density']:.3f}")
                
                # Log to wandb
                if self.config.get('use_wandb', False):
                    wandb.log({
                        'episode': episode,
                        'train_reward': episode_metrics['episode_reward'],
                        'val_reward_mean': val_metrics['mean_reward'],
                        'val_reward_std': val_metrics['std_reward'],
                        'success_rate': val_metrics['success_rate'],
                        'final_density': val_metrics['mean_final_density'],
                        'max_strain': val_metrics['mean_max_strain']
                    })
                
                # Save best model
                if val_metrics['mean_reward'] > best_val_reward:
                    best_val_reward = val_metrics['mean_reward']
                    self.save_agent('best_model.pth')
            
            # Periodic save
            if episode % save_frequency == 0:
                self.save_agent(f'checkpoint_{episode}.pth')
                self.plot_training_progress()
        
        # Final save and evaluation
        self.save_agent('final_model.pth')
        self.plot_training_progress()
        self.generate_final_report()
        
        print("Training completed!")
    
    def save_agent(self, filename: str):
        """Save agent to file"""
        filepath = os.path.join(self.output_dir, filename)
        self.agent.save(filepath)
    
    def plot_training_progress(self):
        """Plot training progress"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Episode rewards
        axes[0, 0].plot(self.episode_rewards)
        axes[0, 0].set_title('Episode Rewards')
        axes[0, 0].set_xlabel('Episode')
        axes[0, 0].set_ylabel('Reward')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Moving average of rewards
        window = 50
        if len(self.episode_rewards) >= window:
            moving_avg = np.convolve(self.episode_rewards, np.ones(window)/window, mode='valid')
            axes[0, 1].plot(moving_avg)
            axes[0, 1].set_title(f'Moving Average Rewards (window={window})')
            axes[0, 1].set_xlabel('Episode')
            axes[0, 1].set_ylabel('Average Reward')
            axes[0, 1].grid(True, alpha=0.3)
        
        # Episode lengths
        axes[1, 0].plot(self.episode_lengths)
        axes[1, 0].set_title('Episode Lengths')
        axes[1, 0].set_xlabel('Episode')
        axes[1, 0].set_ylabel('Length')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Training losses (if available)
        if hasattr(self.agent, 'training_metrics'):
            if self.agent.training_metrics['total_loss']:
                axes[1, 1].plot(self.agent.training_metrics['total_loss'])
                axes[1, 1].set_title('Training Loss')
                axes[1, 1].set_xlabel('Update Step')
                axes[1, 1].set_ylabel('Loss')
                axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'training_progress.png'), dpi=300)
        plt.close()
    
    def generate_final_report(self):
        """Generate final training report"""
        # Final validation
        final_val_metrics = self.validate()
        
        report = {
            'training_config': self.config,
            'training_summary': {
                'total_episodes': len(self.episode_rewards),
                'final_train_reward': self.episode_rewards[-1] if self.episode_rewards else 0,
                'best_train_reward': max(self.episode_rewards) if self.episode_rewards else 0,
                'mean_episode_length': np.mean(self.episode_lengths) if self.episode_lengths else 0
            },
            'final_validation': final_val_metrics,
            'training_completed': datetime.now().isoformat()
        }
        
        # Save report
        with open(os.path.join(self.output_dir, 'training_report.json'), 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\nFinal Training Report:")
        print(f"Best training reward: {report['training_summary']['best_train_reward']:.2f}")
        print(f"Final validation reward: {final_val_metrics['mean_reward']:.2f}")
        print(f"Success rate: {final_val_metrics['success_rate']:.2f}")
        print(f"Mean final density: {final_val_metrics['mean_final_density']:.3f}")

def main():
    parser = argparse.ArgumentParser(description='Train RL agents for furnace control')
    parser.add_argument('--config', type=str, required=True, help='Path to config file')
    parser.add_argument('--agent', type=str, choices=['ppo', 'sac', 'multi_objective'], 
                       default='ppo', help='Agent type')
    parser.add_argument('--episodes', type=int, default=1000, help='Number of training episodes')
    parser.add_argument('--lr', type=float, default=3e-4, help='Learning rate')
    parser.add_argument('--use_wandb', action='store_true', help='Use Weights & Biases logging')
    
    args = parser.parse_args()
    
    # Load config
    if os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        config = {}
    
    # Override with command line arguments
    config.update({
        'agent_type': args.agent,
        'num_episodes': args.episodes,
        'learning_rate': args.lr,
        'use_wandb': args.use_wandb
    })
    
    # Default config values
    default_config = {
        'dataset_path': '/workspace/realtime_training_dataset',
        'total_episodes': 1000,
        'train_split': 0.8,
        'max_steps': 3600,
        'reward_weights': {
            'warpage': 1.0,
            'strain': 0.8,
            'density': 1.2,
            'temperature': 0.6,
            'energy': 0.1
        },
        'val_episodes': 10,
        'val_frequency': 50,
        'save_frequency': 100,
        'update_frequency': 10,
        'batch_size': 256,
        'gamma': 0.99,
        'clip_ratio': 0.2,
        'alpha': 0.2,
        'num_objectives': 4
    }
    
    # Merge configs
    for key, value in default_config.items():
        if key not in config:
            config[key] = value
    
    # Create trainer and start training
    trainer = TrainingManager(config)
    trainer.train()

if __name__ == "__main__":
    main()