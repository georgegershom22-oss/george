#!/usr/bin/env python3
"""
Advanced Data Visualization and Analysis Module
Creates comprehensive visualizations for the generated dataset
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import h5py
import os
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class DatasetVisualizer:
    """Comprehensive dataset visualization and analysis"""
    
    def __init__(self, dataset_path: str = "/workspace/dataset"):
        self.dataset_path = dataset_path
        self.output_dir = os.path.join(dataset_path, "visualizations")
        os.makedirs(self.output_dir, exist_ok=True)
        
    def load_dataset(self, hdf5_path: str = "real_time_dataset.h5"):
        """Load dataset from HDF5 file"""
        self.hdf5_path = os.path.join(self.dataset_path, hdf5_path)
        
        with h5py.File(self.hdf5_path, 'r') as f:
            # Load DIC data
            self.dic_frames = f['dic_data/camera1/frames'][:]
            self.dic_metadata = {
                'timestamps': f['dic_data/camera1/timestamps'][:],
                'max_principal_strain': f['dic_data/camera1/max_principal_strain'][:],
                'strain_heterogeneity': f['dic_data/camera1/strain_heterogeneity'][:],
                'max_von_mises': f['dic_data/camera1/max_von_mises'][:],
                'curvature': f['dic_data/camera1/curvature'][:]
            }
            
            # Load furnace data
            self.furnace_times = f['furnace_data/sensors/times'][:]
            self.temperatures = {}
            for i in range(8):
                self.temperatures[f'tc_{i}'] = f[f'furnace_data/sensors/temperatures/tc_{i}'][:]
            
            # Load RL data
            self.rl_states = f['rl_data/states'][:]
            self.rl_actions = f['rl_data/actions'][:]
            self.rl_rewards = f['rl_data/rewards'][:]
            self.rl_timestamps = f['rl_data/timestamps'][:]
            
    def create_comprehensive_dashboard(self):
        """Create comprehensive interactive dashboard"""
        print("Creating comprehensive dashboard...")
        
        # Create subplots
        fig = make_subplots(
            rows=4, cols=3,
            subplot_titles=[
                'Reward Over Time', 'Max Principal Strain', 'Temperature Profile',
                'Density Evolution', 'Strain Heterogeneity', 'Sample Curvature',
                'Action Distribution', 'State Correlation', 'Process Metrics',
                'Thermal Gradient', 'Energy Efficiency', 'Process Stability'
            ],
            specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 1. Reward Over Time
        fig.add_trace(
            go.Scatter(x=self.rl_timestamps, y=self.rl_rewards, mode='lines', name='Reward'),
            row=1, col=1
        )
        
        # 2. Max Principal Strain
        fig.add_trace(
            go.Scatter(x=self.dic_metadata['timestamps'], y=self.dic_metadata['max_principal_strain'], 
                      mode='lines', name='Max Principal Strain'),
            row=1, col=2
        )
        
        # 3. Temperature Profile
        for i in range(8):
            fig.add_trace(
                go.Scatter(x=self.furnace_times, y=self.temperatures[f'tc_{i}'], 
                          mode='lines', name=f'TC {i}', showlegend=False),
                row=1, col=3
            )
        
        # 4. Density Evolution
        density = self.rl_states[:, 7]  # Current density
        fig.add_trace(
            go.Scatter(x=self.rl_timestamps, y=density, mode='lines', name='Density'),
            row=2, col=1
        )
        
        # 5. Strain Heterogeneity
        fig.add_trace(
            go.Scatter(x=self.dic_metadata['timestamps'], y=self.dic_metadata['strain_heterogeneity'], 
                      mode='lines', name='Strain Heterogeneity'),
            row=2, col=2
        )
        
        # 6. Sample Curvature
        fig.add_trace(
            go.Scatter(x=self.dic_metadata['timestamps'], y=self.dic_metadata['curvature'], 
                      mode='lines', name='Curvature'),
            row=2, col=3
        )
        
        # 7. Action Distribution
        actions_flat = self.rl_actions.flatten()
        fig.add_trace(
            go.Histogram(x=actions_flat, name='Action Distribution'),
            row=3, col=1
        )
        
        # 8. State Correlation
        state_df = pd.DataFrame(self.rl_states, columns=[
            'Max Principal Strain', 'Strain Heterogeneity', 'Max Von Mises',
            'Curvature', 'Avg Temperature', 'Temp Gradient', 'Cycle Time', 'Density'
        ])
        corr_matrix = state_df.corr()
        
        fig.add_trace(
            go.Heatmap(z=corr_matrix.values, x=corr_matrix.columns, y=corr_matrix.columns,
                      colorscale='RdBu', zmid=0),
            row=3, col=2
        )
        
        # 9. Process Metrics
        process_metrics = {
            'Energy Efficiency': self.rl_states[:, 12],
            'Process Stability': self.rl_states[:, 13]
        }
        
        for metric, values in process_metrics.items():
            fig.add_trace(
                go.Scatter(x=self.rl_timestamps, y=values, mode='lines', name=metric),
                row=3, col=3
            )
        
        # 10. Thermal Gradient
        thermal_gradient = self.rl_states[:, 6]
        fig.add_trace(
            go.Scatter(x=self.rl_timestamps, y=thermal_gradient, mode='lines', name='Thermal Gradient'),
            row=4, col=1
        )
        
        # 11. Energy Efficiency
        energy_efficiency = self.rl_states[:, 12]
        fig.add_trace(
            go.Scatter(x=self.rl_timestamps, y=energy_efficiency, mode='lines', name='Energy Efficiency'),
            row=4, col=2
        )
        
        # 12. Process Stability
        process_stability = self.rl_states[:, 13]
        fig.add_trace(
            go.Scatter(x=self.rl_timestamps, y=process_stability, mode='lines', name='Process Stability'),
            row=4, col=3
        )
        
        # Update layout
        fig.update_layout(
            title="Real-Time Training & Validation Dataset Dashboard",
            height=1200,
            showlegend=True
        )
        
        # Save dashboard
        fig.write_html(os.path.join(self.output_dir, "comprehensive_dashboard.html"))
        print(f"Dashboard saved to: {os.path.join(self.output_dir, 'comprehensive_dashboard.html')}")
        
    def create_dic_visualization(self):
        """Create DIC-specific visualizations"""
        print("Creating DIC visualizations...")
        
        # Sample frames at different time points
        time_points = [0, len(self.dic_frames)//4, len(self.dic_frames)//2, 3*len(self.dic_frames)//4, len(self.dic_frames)-1]
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        for i, frame_idx in enumerate(time_points):
            if frame_idx < len(self.dic_frames):
                axes[i].imshow(self.dic_frames[frame_idx], cmap='gray')
                axes[i].set_title(f'Frame {frame_idx} (t={self.dic_metadata["timestamps"][frame_idx]:.1f}s)')
                axes[i].axis('off')
        
        # Remove empty subplot
        axes[5].remove()
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "dic_sample_frames.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Strain field evolution
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # Max principal strain over time
        axes[0, 0].plot(self.dic_metadata['timestamps'], self.dic_metadata['max_principal_strain'])
        axes[0, 0].set_title('Max Principal Strain Over Time')
        axes[0, 0].set_xlabel('Time (s)')
        axes[0, 0].set_ylabel('Max Principal Strain')
        
        # Strain heterogeneity
        axes[0, 1].plot(self.dic_metadata['timestamps'], self.dic_metadata['strain_heterogeneity'])
        axes[0, 1].set_title('Strain Heterogeneity Over Time')
        axes[0, 1].set_xlabel('Time (s)')
        axes[0, 1].set_ylabel('Strain Heterogeneity')
        
        # Von Mises strain
        axes[0, 2].plot(self.dic_metadata['timestamps'], self.dic_metadata['max_von_mises'])
        axes[0, 2].set_title('Max Von Mises Strain Over Time')
        axes[0, 2].set_xlabel('Time (s)')
        axes[0, 2].set_ylabel('Max Von Mises Strain')
        
        # Sample curvature
        axes[1, 0].plot(self.dic_metadata['timestamps'], self.dic_metadata['curvature'])
        axes[1, 0].set_title('Sample Curvature Over Time')
        axes[1, 0].set_xlabel('Time (s)')
        axes[1, 0].set_ylabel('Curvature')
        
        # Strain distribution
        axes[1, 1].hist(self.dic_metadata['max_principal_strain'], bins=50, alpha=0.7)
        axes[1, 1].set_title('Max Principal Strain Distribution')
        axes[1, 1].set_xlabel('Max Principal Strain')
        axes[1, 1].set_ylabel('Frequency')
        
        # Strain vs curvature correlation
        axes[1, 2].scatter(self.dic_metadata['max_principal_strain'], self.dic_metadata['curvature'], alpha=0.5)
        axes[1, 2].set_title('Strain vs Curvature Correlation')
        axes[1, 2].set_xlabel('Max Principal Strain')
        axes[1, 2].set_ylabel('Curvature')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "dic_analysis.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_furnace_visualization(self):
        """Create furnace-specific visualizations"""
        print("Creating furnace visualizations...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Temperature profiles
        for i in range(8):
            axes[0, 0].plot(self.furnace_times, self.temperatures[f'tc_{i}'], label=f'TC {i}', alpha=0.7)
        axes[0, 0].set_title('Temperature Profiles')
        axes[0, 0].set_xlabel('Time (s)')
        axes[0, 0].set_ylabel('Temperature (°C)')
        axes[0, 0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Temperature statistics
        temp_array = np.array([self.temperatures[f'tc_{i}'] for i in range(8)])
        temp_mean = np.mean(temp_array, axis=0)
        temp_std = np.std(temp_array, axis=0)
        
        axes[0, 1].plot(self.furnace_times, temp_mean, label='Mean Temperature')
        axes[0, 1].fill_between(self.furnace_times, temp_mean - temp_std, temp_mean + temp_std, alpha=0.3)
        axes[0, 1].set_title('Temperature Statistics')
        axes[0, 1].set_xlabel('Time (s)')
        axes[0, 1].set_ylabel('Temperature (°C)')
        
        # Temperature distribution
        axes[1, 0].hist(temp_array.flatten(), bins=50, alpha=0.7)
        axes[1, 0].set_title('Temperature Distribution')
        axes[1, 0].set_xlabel('Temperature (°C)')
        axes[1, 0].set_ylabel('Frequency')
        
        # Temperature uniformity over time
        temp_range = np.max(temp_array, axis=0) - np.min(temp_array, axis=0)
        axes[1, 1].plot(self.furnace_times, temp_range)
        axes[1, 1].set_title('Temperature Uniformity (Range)')
        axes[1, 1].set_xlabel('Time (s)')
        axes[1, 1].set_ylabel('Temperature Range (°C)')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "furnace_analysis.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_rl_visualization(self):
        """Create RL-specific visualizations"""
        print("Creating RL visualizations...")
        
        fig, axes = plt.subplots(3, 3, figsize=(18, 15))
        
        # Reward over time
        axes[0, 0].plot(self.rl_timestamps, self.rl_rewards)
        axes[0, 0].set_title('Reward Over Time')
        axes[0, 0].set_xlabel('Time (s)')
        axes[0, 0].set_ylabel('Reward')
        
        # State evolution
        state_names = ['Max Principal Strain', 'Strain Heterogeneity', 'Max Von Mises',
                      'Curvature', 'Avg Temperature', 'Temp Gradient', 'Cycle Time', 'Density']
        
        for i in range(8):
            axes[0, 1].plot(self.rl_timestamps, self.rl_states[:, i], label=state_names[i], alpha=0.7)
        axes[0, 1].set_title('State Evolution')
        axes[0, 1].set_xlabel('Time (s)')
        axes[0, 1].set_ylabel('Normalized Value')
        axes[0, 1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Action distribution
        actions_flat = self.rl_actions.flatten()
        axes[0, 2].hist(actions_flat, bins=50, alpha=0.7)
        axes[0, 2].set_title('Action Distribution')
        axes[0, 2].set_xlabel('Action Value')
        axes[0, 2].set_ylabel('Frequency')
        
        # Reward distribution
        axes[1, 0].hist(self.rl_rewards, bins=50, alpha=0.7)
        axes[1, 0].set_title('Reward Distribution')
        axes[1, 0].set_xlabel('Reward')
        axes[1, 0].set_ylabel('Frequency')
        
        # State correlation heatmap
        state_df = pd.DataFrame(self.rl_states, columns=state_names)
        corr_matrix = state_df.corr()
        
        im = axes[1, 1].imshow(corr_matrix, cmap='RdBu', vmin=-1, vmax=1)
        axes[1, 1].set_xticks(range(len(state_names)))
        axes[1, 1].set_yticks(range(len(state_names)))
        axes[1, 1].set_xticklabels(state_names, rotation=45, ha='right')
        axes[1, 1].set_yticklabels(state_names)
        axes[1, 1].set_title('State Correlation Matrix')
        
        # Add colorbar
        plt.colorbar(im, ax=axes[1, 1])
        
        # Action correlation
        action_df = pd.DataFrame(self.rl_actions, columns=[f'Action_{i}' for i in range(6)])
        action_corr = action_df.corr()
        
        im2 = axes[1, 2].imshow(action_corr, cmap='RdBu', vmin=-1, vmax=1)
        axes[1, 2].set_xticks(range(6))
        axes[1, 2].set_yticks(range(6))
        axes[1, 2].set_xticklabels([f'A{i}' for i in range(6)])
        axes[1, 2].set_yticklabels([f'A{i}' for i in range(6)])
        axes[1, 2].set_title('Action Correlation Matrix')
        
        # Add colorbar
        plt.colorbar(im2, ax=axes[1, 2])
        
        # Reward vs state features
        for i in range(3):
            axes[2, i].scatter(self.rl_states[:, i], self.rl_rewards, alpha=0.5)
            axes[2, i].set_xlabel(state_names[i])
            axes[2, i].set_ylabel('Reward')
            axes[2, i].set_title(f'Reward vs {state_names[i]}')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "rl_analysis.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_3d_visualizations(self):
        """Create 3D visualizations"""
        print("Creating 3D visualizations...")
        
        # 3D state space visualization
        fig = plt.figure(figsize=(15, 5))
        
        # State space in 3D
        ax1 = fig.add_subplot(131, projection='3d')
        scatter = ax1.scatter(self.rl_states[:, 0], self.rl_states[:, 1], self.rl_states[:, 2], 
                             c=self.rl_rewards, cmap='viridis', alpha=0.6)
        ax1.set_xlabel('Max Principal Strain')
        ax1.set_ylabel('Strain Heterogeneity')
        ax1.set_zlabel('Max Von Mises')
        ax1.set_title('3D State Space (colored by reward)')
        plt.colorbar(scatter, ax=ax1, label='Reward')
        
        # Action space in 3D
        ax2 = fig.add_subplot(132, projection='3d')
        scatter2 = ax2.scatter(self.rl_actions[:, 0], self.rl_actions[:, 1], self.rl_actions[:, 2], 
                              c=self.rl_rewards, cmap='plasma', alpha=0.6)
        ax2.set_xlabel('Action Zone 0')
        ax2.set_ylabel('Action Zone 1')
        ax2.set_zlabel('Action Zone 2')
        ax2.set_title('3D Action Space (colored by reward)')
        plt.colorbar(scatter2, ax=ax2, label='Reward')
        
        # Time evolution in 3D
        ax3 = fig.add_subplot(133, projection='3d')
        ax3.plot(self.rl_states[:, 0], self.rl_states[:, 1], self.rl_states[:, 2], alpha=0.7)
        ax3.set_xlabel('Max Principal Strain')
        ax3.set_ylabel('Strain Heterogeneity')
        ax3.set_zlabel('Max Von Mises')
        ax3.set_title('State Evolution Trajectory')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "3d_visualizations.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_statistical_analysis(self):
        """Create statistical analysis plots"""
        print("Creating statistical analysis...")
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # Dataset statistics
        stats_data = {
            'Metric': ['Total Samples', 'State Dimension', 'Action Dimension', 'Duration (hours)', 'FPS', 'Sampling Rate'],
            'Value': [len(self.rl_states), self.rl_states.shape[1], self.rl_actions.shape[1], 8.0, 120, 0.083]
        }
        
        axes[0, 0].bar(stats_data['Metric'], stats_data['Value'])
        axes[0, 0].set_title('Dataset Statistics')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Reward statistics
        reward_stats = {
            'Mean': np.mean(self.rl_rewards),
            'Std': np.std(self.rl_rewards),
            'Min': np.min(self.rl_rewards),
            'Max': np.max(self.rl_rewards),
            'Median': np.median(self.rl_rewards)
        }
        
        axes[0, 1].bar(reward_stats.keys(), reward_stats.values())
        axes[0, 1].set_title('Reward Statistics')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # State feature importance (variance)
        state_vars = np.var(self.rl_states, axis=0)
        state_names = ['Max Principal Strain', 'Strain Heterogeneity', 'Max Von Mises',
                      'Curvature', 'Avg Temperature', 'Temp Gradient', 'Cycle Time', 'Density']
        
        axes[0, 2].bar(range(len(state_vars)), state_vars)
        axes[0, 2].set_title('State Feature Variance')
        axes[0, 2].set_xticks(range(len(state_names)))
        axes[0, 2].set_xticklabels(state_names, rotation=45, ha='right')
        
        # Action feature importance
        action_vars = np.var(self.rl_actions, axis=0)
        action_names = [f'Zone {i}' for i in range(6)]
        
        axes[1, 0].bar(range(len(action_vars)), action_vars)
        axes[1, 0].set_title('Action Feature Variance')
        axes[1, 0].set_xticks(range(len(action_names)))
        axes[1, 0].set_xticklabels(action_names)
        
        # Reward distribution by time periods
        time_periods = 4
        period_size = len(self.rl_rewards) // time_periods
        period_rewards = [self.rl_rewards[i*period_size:(i+1)*period_size] for i in range(time_periods)]
        
        axes[1, 1].boxplot(period_rewards, labels=[f'Period {i+1}' for i in range(time_periods)])
        axes[1, 1].set_title('Reward Distribution by Time Periods')
        axes[1, 1].set_ylabel('Reward')
        
        # State correlation with reward
        state_reward_corr = [np.corrcoef(self.rl_states[:, i], self.rl_rewards)[0, 1] for i in range(8)]
        
        axes[1, 2].bar(range(len(state_reward_corr)), state_reward_corr)
        axes[1, 2].set_title('State-Reward Correlation')
        axes[1, 2].set_xticks(range(len(state_names)))
        axes[1, 2].set_xticklabels(state_names, rotation=45, ha='right')
        axes[1, 2].axhline(y=0, color='red', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "statistical_analysis.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_all_visualizations(self):
        """Create all visualizations"""
        print("Creating all visualizations...")
        
        # Load dataset
        self.load_dataset()
        
        # Create visualizations
        self.create_comprehensive_dashboard()
        self.create_dic_visualization()
        self.create_furnace_visualization()
        self.create_rl_visualization()
        self.create_3d_visualizations()
        self.create_statistical_analysis()
        
        print(f"All visualizations saved to: {self.output_dir}")

def main():
    """Main function to create visualizations"""
    visualizer = DatasetVisualizer()
    visualizer.create_all_visualizations()

if __name__ == "__main__":
    main()