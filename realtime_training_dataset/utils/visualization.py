#!/usr/bin/env python3
"""
Visualization utilities for the real-time dataset
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import cv2
import h5py
import pickle
import pandas as pd
import json
import os
from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

class DatasetVisualizer:
    """Comprehensive visualization tools for the dataset"""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.load_metadata()
        
    def load_metadata(self):
        """Load dataset metadata"""
        with open(os.path.join(self.base_path, "dataset_summary.json"), 'r') as f:
            self.metadata = json.load(f)
    
    def plot_episode_overview(self, episode: int, save_path: Optional[str] = None):
        """Create comprehensive overview plot for an episode"""
        # Load episode data
        episode_dir = os.path.join(self.base_path, f"episode_{episode:04d}")
        
        # Load RL data
        with open(os.path.join(episode_dir, "rl_data.pkl"), 'rb') as f:
            rl_data = pickle.load(f)
        
        # Load furnace data
        furnace_data = pd.read_parquet(os.path.join(episode_dir, "furnace_data.parquet"))
        
        # Create subplots
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        fig.suptitle(f'Episode {episode} Overview', fontsize=16)
        
        # Time vectors
        rl_times = np.arange(len(rl_data['states']))
        furnace_times = furnace_data['timestamp'].values
        
        # Plot 1: State evolution
        states_array = np.array([self.state_to_vector(s) for s in rl_data['states']])
        state_names = ['Max Strain', 'Strain Std', 'Curvature', 'Temp Std', 'Density', 'Mean Temp', 'Time Ratio']
        
        for i, name in enumerate(state_names):
            if i < 4:
                axes[0, 0].plot(rl_times, states_array[:, i], label=name, alpha=0.7)
        axes[0, 0].set_title('Mechanical States')
        axes[0, 0].set_xlabel('Time Step')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Thermal states
        axes[0, 1].plot(rl_times, states_array[:, 4], label='Density', color='red')
        axes[0, 1].set_ylabel('Density', color='red')
        ax2 = axes[0, 1].twinx()
        ax2.plot(rl_times, states_array[:, 5], label='Mean Temp', color='blue')
        ax2.set_ylabel('Temperature (°C)', color='blue')
        axes[0, 1].set_title('Thermal States')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Actions
        actions_array = np.array(rl_data['actions'])
        for i in range(min(6, actions_array.shape[1])):
            axes[1, 0].plot(rl_times[:-1], actions_array[:, i], label=f'Zone {i+1}', alpha=0.7)
        axes[1, 0].set_title('Control Actions (Power Adjustments)')
        axes[1, 0].set_xlabel('Time Step')
        axes[1, 0].set_ylabel('Power Change (%)')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Rewards
        rewards = np.array(rl_data['rewards'])
        axes[1, 1].plot(rl_times[:-1], rewards, color='green', linewidth=2)
        axes[1, 1].fill_between(rl_times[:-1], rewards, alpha=0.3, color='green')
        axes[1, 1].set_title('Reward Signal')
        axes[1, 1].set_xlabel('Time Step')
        axes[1, 1].set_ylabel('Reward')
        axes[1, 1].grid(True, alpha=0.3)
        
        # Plot 5: Temperature zones
        zone_powers = np.array([row for row in furnace_data['zone_powers']])
        for i in range(min(6, zone_powers.shape[1])):
            axes[2, 0].plot(furnace_times, zone_powers[:, i], label=f'Zone {i+1}', alpha=0.7)
        axes[2, 0].set_title('Heating Zone Powers')
        axes[2, 0].set_xlabel('Time (s)')
        axes[2, 0].set_ylabel('Power (%)')
        axes[2, 0].legend()
        axes[2, 0].grid(True, alpha=0.3)
        
        # Plot 6: Temperature readings
        temperatures = np.array([row for row in furnace_data['temperatures']])
        temp_mean = np.mean(temperatures, axis=1)
        temp_std = np.std(temperatures, axis=1)
        
        axes[2, 1].plot(furnace_times, temp_mean, label='Mean Temp', color='red', linewidth=2)
        axes[2, 1].fill_between(furnace_times, temp_mean - temp_std, temp_mean + temp_std, 
                               alpha=0.3, color='red', label='±1 Std')
        axes[2, 1].set_title('Temperature Distribution')
        axes[2, 1].set_xlabel('Time (s)')
        axes[2, 1].set_ylabel('Temperature (°C)')
        axes[2, 1].legend()
        axes[2, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def visualize_strain_field(self, episode: int, frame_idx: int = 0, save_path: Optional[str] = None):
        """Visualize strain field for a specific frame"""
        episode_dir = os.path.join(self.base_path, f"episode_{episode:04d}")
        
        # Load DIC data
        with h5py.File(os.path.join(episode_dir, "dic_data.h5"), 'r') as f:
            strain_fields = f['strain_fields'][frame_idx]
            displacement_fields = f['displacement_fields'][frame_idx]
        
        # Create visualization
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle(f'Episode {episode}, Frame {frame_idx} - DIC Analysis', fontsize=16)
        
        # Strain components
        strain_xx = strain_fields[:, :, 0]
        strain_yy = strain_fields[:, :, 1]
        strain_xy = strain_fields[:, :, 2]
        
        # Principal strain
        principal_strain = np.sqrt(strain_xx**2 + strain_yy**2)
        
        # Displacement components
        u_disp = displacement_fields[:, :, 0]
        v_disp = displacement_fields[:, :, 1]
        
        # Displacement magnitude
        disp_magnitude = np.sqrt(u_disp**2 + v_disp**2)
        
        # Plot strain components
        im1 = axes[0, 0].imshow(strain_xx, cmap='RdBu_r', aspect='equal')
        axes[0, 0].set_title('Strain εxx')
        plt.colorbar(im1, ax=axes[0, 0])
        
        im2 = axes[0, 1].imshow(strain_yy, cmap='RdBu_r', aspect='equal')
        axes[0, 1].set_title('Strain εyy')
        plt.colorbar(im2, ax=axes[0, 1])
        
        im3 = axes[0, 2].imshow(strain_xy, cmap='RdBu_r', aspect='equal')
        axes[0, 2].set_title('Shear Strain εxy')
        plt.colorbar(im3, ax=axes[0, 2])
        
        # Plot principal strain
        im4 = axes[1, 0].imshow(principal_strain, cmap='plasma', aspect='equal')
        axes[1, 0].set_title('Principal Strain')
        plt.colorbar(im4, ax=axes[1, 0])
        
        # Plot displacement magnitude
        im5 = axes[1, 1].imshow(disp_magnitude, cmap='viridis', aspect='equal')
        axes[1, 1].set_title('Displacement Magnitude (mm)')
        plt.colorbar(im5, ax=axes[1, 1])
        
        # Plot displacement vectors (subsampled)
        step = 20
        x, y = np.meshgrid(np.arange(0, strain_xx.shape[1], step),
                          np.arange(0, strain_xx.shape[0], step))
        u_sub = u_disp[::step, ::step]
        v_sub = v_disp[::step, ::step]
        
        axes[1, 2].quiver(x, y, u_sub, v_sub, scale=0.1, alpha=0.7)
        axes[1, 2].set_title('Displacement Vectors')
        axes[1, 2].set_aspect('equal')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_interactive_dashboard(self, episode: int) -> go.Figure:
        """Create interactive Plotly dashboard for episode analysis"""
        # Load data
        episode_dir = os.path.join(self.base_path, f"episode_{episode:04d}")
        
        with open(os.path.join(episode_dir, "rl_data.pkl"), 'rb') as f:
            rl_data = pickle.load(f)
        
        furnace_data = pd.read_parquet(os.path.join(episode_dir, "furnace_data.parquet"))
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('State Evolution', 'Reward Signal', 
                          'Control Actions', 'Temperature Zones',
                          'Process Metrics', 'System Health'),
            specs=[[{"secondary_y": True}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": True}, {"secondary_y": False}]]
        )
        
        # Prepare data
        states_array = np.array([self.state_to_vector(s) for s in rl_data['states']])
        actions_array = np.array(rl_data['actions'])
        rewards = np.array(rl_data['rewards'])
        rl_times = np.arange(len(rl_data['states']))
        
        # State evolution
        fig.add_trace(
            go.Scatter(x=rl_times, y=states_array[:, 0], name='Max Strain', line=dict(color='red')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=rl_times, y=states_array[:, 4], name='Density', line=dict(color='blue')),
            row=1, col=1, secondary_y=True
        )
        
        # Reward signal
        fig.add_trace(
            go.Scatter(x=rl_times[:-1], y=rewards, name='Reward', 
                      fill='tonexty', line=dict(color='green')),
            row=1, col=2
        )
        
        # Control actions
        for i in range(min(3, actions_array.shape[1])):
            fig.add_trace(
                go.Scatter(x=rl_times[:-1], y=actions_array[:, i], 
                          name=f'Zone {i+1}', opacity=0.7),
                row=2, col=1
            )
        
        # Temperature zones
        zone_powers = np.array([row for row in furnace_data['zone_powers']])
        for i in range(min(3, zone_powers.shape[1])):
            fig.add_trace(
                go.Scatter(x=furnace_data['timestamp'], y=zone_powers[:, i],
                          name=f'Power Zone {i+1}', opacity=0.7),
                row=2, col=2
            )
        
        # Process metrics
        fig.add_trace(
            go.Scatter(x=rl_times, y=states_array[:, 5], name='Mean Temp', line=dict(color='orange')),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=rl_times, y=states_array[:, 3], name='Temp Std', line=dict(color='purple')),
            row=3, col=1, secondary_y=True
        )
        
        # System health (cumulative reward)
        cumulative_reward = np.cumsum(rewards)
        fig.add_trace(
            go.Scatter(x=rl_times[:-1], y=cumulative_reward, name='Cumulative Reward',
                      line=dict(color='darkgreen', width=3)),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            title=f'Interactive Dashboard - Episode {episode}',
            height=800,
            showlegend=True
        )
        
        return fig
    
    def animate_strain_evolution(self, episode: int, output_path: str, fps: int = 10):
        """Create animation of strain field evolution"""
        episode_dir = os.path.join(self.base_path, f"episode_{episode:04d}")
        
        # Load DIC data
        with h5py.File(os.path.join(episode_dir, "dic_data.h5"), 'r') as f:
            strain_fields = f['strain_fields'][:]
            timestamps = f['timestamps'][:]
        
        # Setup animation
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Calculate principal strain for all frames
        principal_strains = []
        for frame in strain_fields:
            strain_xx = frame[:, :, 0]
            strain_yy = frame[:, :, 1]
            principal = np.sqrt(strain_xx**2 + strain_yy**2)
            principal_strains.append(principal)
        
        principal_strains = np.array(principal_strains)
        
        # Set up the plot
        vmin, vmax = principal_strains.min(), principal_strains.max()
        im = ax.imshow(principal_strains[0], cmap='plasma', vmin=vmin, vmax=vmax, aspect='equal')
        ax.set_title('Principal Strain Evolution')
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Principal Strain')
        
        # Animation function
        def animate(frame):
            im.set_array(principal_strains[frame])
            ax.set_title(f'Principal Strain Evolution - t={timestamps[frame]:.1f}s')
            return [im]
        
        # Create animation
        anim = animation.FuncAnimation(fig, animate, frames=len(principal_strains),
                                     interval=1000//fps, blit=True, repeat=True)
        
        # Save animation
        anim.save(output_path, writer='pillow', fps=fps)
        plt.close()
    
    def state_to_vector(self, state: Dict) -> np.ndarray:
        """Convert state dictionary to vector"""
        return np.array([
            state['max_principal_strain'],
            state['strain_std'],
            state['sample_curvature'],
            state['temperature_std'],
            state['current_density'],
            state['mean_temperature'],
            state['time_in_cycle']
        ])
    
    def plot_dataset_statistics(self, save_path: Optional[str] = None):
        """Plot overall dataset statistics"""
        # Sample episodes for statistics
        sample_episodes = range(0, min(100, self.metadata['dataset_info']['total_episodes']), 10)
        
        all_rewards = []
        all_max_strains = []
        all_densities = []
        episode_lengths = []
        
        for episode in sample_episodes:
            try:
                episode_dir = os.path.join(self.base_path, f"episode_{episode:04d}")
                with open(os.path.join(episode_dir, "rl_data.pkl"), 'rb') as f:
                    rl_data = pickle.load(f)
                
                all_rewards.extend(rl_data['rewards'])
                
                for state in rl_data['states']:
                    all_max_strains.append(state['max_principal_strain'])
                    all_densities.append(state['current_density'])
                
                episode_lengths.append(len(rl_data['states']))
                
            except Exception as e:
                print(f"Error loading episode {episode}: {e}")
                continue
        
        # Create plots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Dataset Statistics', fontsize=16)
        
        # Reward distribution
        axes[0, 0].hist(all_rewards, bins=50, alpha=0.7, color='green')
        axes[0, 0].set_title('Reward Distribution')
        axes[0, 0].set_xlabel('Reward')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Max strain distribution
        axes[0, 1].hist(all_max_strains, bins=50, alpha=0.7, color='red')
        axes[0, 1].set_title('Max Principal Strain Distribution')
        axes[0, 1].set_xlabel('Max Strain')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Density evolution
        axes[0, 2].hist(all_densities, bins=50, alpha=0.7, color='blue')
        axes[0, 2].set_title('Density Distribution')
        axes[0, 2].set_xlabel('Relative Density')
        axes[0, 2].set_ylabel('Frequency')
        axes[0, 2].grid(True, alpha=0.3)
        
        # Episode lengths
        axes[1, 0].hist(episode_lengths, bins=20, alpha=0.7, color='purple')
        axes[1, 0].set_title('Episode Length Distribution')
        axes[1, 0].set_xlabel('Episode Length (steps)')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Reward vs Max Strain scatter
        sample_indices = np.random.choice(len(all_rewards), min(1000, len(all_rewards)), replace=False)
        sample_rewards = [all_rewards[i] for i in sample_indices]
        sample_strains = [all_max_strains[i] for i in sample_indices]
        
        axes[1, 1].scatter(sample_strains, sample_rewards, alpha=0.5, s=10)
        axes[1, 1].set_title('Reward vs Max Strain')
        axes[1, 1].set_xlabel('Max Principal Strain')
        axes[1, 1].set_ylabel('Reward')
        axes[1, 1].grid(True, alpha=0.3)
        
        # Density vs Reward scatter
        sample_densities = [all_densities[i] for i in sample_indices]
        axes[1, 2].scatter(sample_densities, sample_rewards, alpha=0.5, s=10)
        axes[1, 2].set_title('Reward vs Density')
        axes[1, 2].set_xlabel('Relative Density')
        axes[1, 2].set_ylabel('Reward')
        axes[1, 2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

if __name__ == "__main__":
    # Example usage
    visualizer = DatasetVisualizer("/workspace/realtime_training_dataset")
    
    # Create episode overview
    visualizer.plot_episode_overview(0, "episode_0_overview.png")
    
    # Visualize strain field
    visualizer.visualize_strain_field(0, 0, "strain_field_example.png")
    
    # Create interactive dashboard
    fig = visualizer.create_interactive_dashboard(0)
    fig.write_html("interactive_dashboard.html")
    
    # Plot dataset statistics
    visualizer.plot_dataset_statistics("dataset_statistics.png")