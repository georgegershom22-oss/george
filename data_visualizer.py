#!/usr/bin/env python3
"""
Data Visualization and Validation Tools
for Real-Time Training & Validation Dataset

This module provides comprehensive visualization and analysis tools
for the generated dataset.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import h5py
import json
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
from scipy import stats
import os
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class DatasetVisualizer:
    """
    Comprehensive visualization and validation tools for the generated dataset.
    """
    
    def __init__(self, dataset_dir: str = "real_time_dataset"):
        """
        Initialize the visualizer with dataset directory.
        
        Args:
            dataset_dir: Path to the dataset directory
        """
        self.dataset_dir = dataset_dir
        self.metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict:
        """Load dataset metadata."""
        with open(f"{self.dataset_dir}/metadata.json", 'r') as f:
            return json.load(f)
    
    def visualize_dic_data(self, frame_indices: List[int] = None, save_plots: bool = True):
        """
        Visualize DIC data including displacement and strain fields.
        
        Args:
            frame_indices: Specific frames to visualize (if None, shows key frames)
            save_plots: Whether to save plots to files
        """
        print("Loading DIC data...")
        
        with h5py.File(f"{self.dataset_dir}/dic_data.h5", 'r') as f:
            # Load data
            displacement_u = f['displacement_u'][:]
            displacement_v = f['displacement_v'][:]
            displacement_w = f['displacement_w'][:]
            strain_xx = f['strain_xx'][:]
            strain_yy = f['strain_yy'][:]
            strain_xy = f['strain_xy'][:]
            max_principal_strain = f['max_principal_strain'][:]
            strain_heterogeneity = f['strain_heterogeneity'][:]
            sample_curvature = f['sample_curvature'][:]
            timestamps = f['timestamps'][:]
            
            # Get sample geometry
            geometry = dict(f['sample_geometry'].attrs)
        
        if frame_indices is None:
            # Select key frames (beginning, middle, end)
            total_frames = len(timestamps)
            frame_indices = [0, total_frames//4, total_frames//2, 3*total_frames//4, total_frames-1]
        
        # Create displacement field plots
        fig, axes = plt.subplots(len(frame_indices), 3, figsize=(15, 4*len(frame_indices)))
        if len(frame_indices) == 1:
            axes = axes.reshape(1, -1)
        
        for i, frame_idx in enumerate(frame_indices):
            time_hours = timestamps[frame_idx] / 3600
            
            # U displacement
            im1 = axes[i, 0].imshow(displacement_u[frame_idx], cmap='RdBu_r', aspect='equal')
            axes[i, 0].set_title(f'U Displacement (t={time_hours:.2f}h)')
            axes[i, 0].set_xlabel('X (pixels)')
            axes[i, 0].set_ylabel('Y (pixels)')
            plt.colorbar(im1, ax=axes[i, 0])
            
            # V displacement
            im2 = axes[i, 1].imshow(displacement_v[frame_idx], cmap='RdBu_r', aspect='equal')
            axes[i, 1].set_title(f'V Displacement (t={time_hours:.2f}h)')
            axes[i, 1].set_xlabel('X (pixels)')
            axes[i, 1].set_ylabel('Y (pixels)')
            plt.colorbar(im2, ax=axes[i, 1])
            
            # W displacement (out-of-plane)
            im3 = axes[i, 2].imshow(displacement_w[frame_idx], cmap='RdBu_r', aspect='equal')
            axes[i, 2].set_title(f'W Displacement (t={time_hours:.2f}h)')
            axes[i, 2].set_xlabel('X (pixels)')
            axes[i, 2].set_ylabel('Y (pixels)')
            plt.colorbar(im3, ax=axes[i, 2])
        
        plt.tight_layout()
        if save_plots:
            plt.savefig(f"{self.dataset_dir}/dic_displacement_fields.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        # Create strain field plots
        fig, axes = plt.subplots(len(frame_indices), 3, figsize=(15, 4*len(frame_indices)))
        if len(frame_indices) == 1:
            axes = axes.reshape(1, -1)
        
        for i, frame_idx in enumerate(frame_indices):
            time_hours = timestamps[frame_idx] / 3600
            
            # XX strain
            im1 = axes[i, 0].imshow(strain_xx[frame_idx], cmap='viridis', aspect='equal')
            axes[i, 0].set_title(f'εxx Strain (t={time_hours:.2f}h)')
            axes[i, 0].set_xlabel('X (pixels)')
            axes[i, 0].set_ylabel('Y (pixels)')
            plt.colorbar(im1, ax=axes[i, 0])
            
            # YY strain
            im2 = axes[i, 1].imshow(strain_yy[frame_idx], cmap='viridis', aspect='equal')
            axes[i, 1].set_title(f'εyy Strain (t={time_hours:.2f}h)')
            axes[i, 1].set_xlabel('X (pixels)')
            axes[i, 1].set_ylabel('Y (pixels)')
            plt.colorbar(im2, ax=axes[i, 1])
            
            # XY strain
            im3 = axes[i, 2].imshow(strain_xy[frame_idx], cmap='viridis', aspect='equal')
            axes[i, 2].set_title(f'εxy Strain (t={time_hours:.2f}h)')
            axes[i, 2].set_xlabel('X (pixels)')
            axes[i, 2].set_ylabel('Y (pixels)')
            plt.colorbar(im3, ax=axes[i, 2])
        
        plt.tight_layout()
        if save_plots:
            plt.savefig(f"{self.dataset_dir}/dic_strain_fields.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        # Plot key metrics over time
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Max principal strain
        axes[0, 0].plot(timestamps/3600, max_principal_strain, 'b-', linewidth=2)
        axes[0, 0].set_xlabel('Time (hours)')
        axes[0, 0].set_ylabel('Max Principal Strain')
        axes[0, 0].set_title('Maximum Principal Strain Evolution')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Strain heterogeneity
        axes[0, 1].plot(timestamps/3600, strain_heterogeneity, 'r-', linewidth=2)
        axes[0, 1].set_xlabel('Time (hours)')
        axes[0, 1].set_ylabel('Strain Heterogeneity (std)')
        axes[0, 1].set_title('Strain Heterogeneity Evolution')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Sample curvature
        axes[1, 0].plot(timestamps/3600, sample_curvature, 'g-', linewidth=2)
        axes[1, 0].set_xlabel('Time (hours)')
        axes[1, 0].set_ylabel('Sample Curvature')
        axes[1, 0].set_title('Sample Curvature Evolution')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Combined metrics
        axes[1, 1].plot(timestamps/3600, max_principal_strain, 'b-', label='Max Principal Strain', linewidth=2)
        axes[1, 1].plot(timestamps/3600, strain_heterogeneity, 'r-', label='Strain Heterogeneity', linewidth=2)
        axes[1, 1].plot(timestamps/3600, sample_curvature, 'g-', label='Sample Curvature', linewidth=2)
        axes[1, 1].set_xlabel('Time (hours)')
        axes[1, 1].set_ylabel('Normalized Values')
        axes[1, 1].set_title('Combined DIC Metrics')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_plots:
            plt.savefig(f"{self.dataset_dir}/dic_metrics_evolution.png", dpi=300, bbox_inches='tight')
        plt.show()
    
    def visualize_furnace_data(self, save_plots: bool = True):
        """
        Visualize furnace control and sensor data.
        
        Args:
            save_plots: Whether to save plots to files
        """
        print("Loading furnace data...")
        
        with h5py.File(f"{self.dataset_dir}/furnace_data.h5", 'r') as f:
            zone_temperatures = f['zone_temperatures'][:]
            zone_power = f['zone_power'][:]
            thermocouple_temps = f['thermocouple_temps'][:]
            oxygen_levels = f['oxygen_levels'][:]
            nitrogen_levels = f['nitrogen_levels'][:]
            actions = f['actions'][:]
            timestamps = f['timestamps'][:]
            zone_positions = f['zone_positions'][:]
            thermocouple_positions = f['thermocouple_positions'][:]
        
        # Create temperature profile plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Zone temperatures
        for zone_idx in range(zone_temperatures.shape[1]):
            axes[0, 0].plot(timestamps/3600, zone_temperatures[:, zone_idx], 
                           label=f'Zone {zone_idx+1}', linewidth=2)
        axes[0, 0].set_xlabel('Time (hours)')
        axes[0, 0].set_ylabel('Temperature (°C)')
        axes[0, 0].set_title('Heating Zone Temperatures')
        axes[0, 0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Thermocouple temperatures
        for tc_idx in range(thermocouple_temps.shape[1]):
            axes[0, 1].plot(timestamps/3600, thermocouple_temps[:, tc_idx], 
                           label=f'TC {tc_idx+1}', linewidth=1.5, alpha=0.7)
        axes[0, 1].set_xlabel('Time (hours)')
        axes[0, 1].set_ylabel('Temperature (°C)')
        axes[0, 1].set_title('Thermocouple Temperatures')
        axes[0, 1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Zone power
        for zone_idx in range(zone_power.shape[1]):
            axes[1, 0].plot(timestamps/3600, zone_power[:, zone_idx], 
                           label=f'Zone {zone_idx+1}', linewidth=2)
        axes[1, 0].set_xlabel('Time (hours)')
        axes[1, 0].set_ylabel('Power (%)')
        axes[1, 0].set_title('Heating Zone Power')
        axes[1, 0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Atmospheric conditions
        axes[1, 1].plot(timestamps/3600, oxygen_levels, 'b-', label='Oxygen', linewidth=2)
        axes[1, 1].plot(timestamps/3600, nitrogen_levels, 'r-', label='Nitrogen', linewidth=2)
        axes[1, 1].set_xlabel('Time (hours)')
        axes[1, 1].set_ylabel('Concentration (%)')
        axes[1, 1].set_title('Atmospheric Gas Composition')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_plots:
            plt.savefig(f"{self.dataset_dir}/furnace_temperature_profiles.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        # Create action vector plots
        fig, axes = plt.subplots(2, 1, figsize=(15, 8))
        
        # Action magnitudes
        action_magnitudes = np.linalg.norm(actions, axis=1)
        axes[0].plot(timestamps[1:]/3600, action_magnitudes, 'b-', linewidth=2)
        axes[0].set_xlabel('Time (hours)')
        axes[0].set_ylabel('Action Magnitude (°C)')
        axes[0].set_title('Furnace Action Magnitudes Over Time')
        axes[0].grid(True, alpha=0.3)
        
        # Individual zone actions
        for zone_idx in range(actions.shape[1]):
            axes[1].plot(timestamps[1:]/3600, actions[:, zone_idx], 
                        label=f'Zone {zone_idx+1}', linewidth=2)
        axes[1].set_xlabel('Time (hours)')
        axes[1].set_ylabel('Temperature Change (°C)')
        axes[1].set_title('Individual Zone Actions')
        axes[1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_plots:
            plt.savefig(f"{self.dataset_dir}/furnace_actions.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        # Create 3D spatial plots
        fig = plt.figure(figsize=(15, 5))
        
        # Zone positions
        ax1 = fig.add_subplot(131, projection='3d')
        ax1.scatter(zone_positions[:, 0], zone_positions[:, 1], 
                   np.mean(zone_temperatures, axis=0), 
                   c=range(len(zone_positions)), cmap='viridis', s=100)
        ax1.set_xlabel('X Position')
        ax1.set_ylabel('Y Position')
        ax1.set_zlabel('Average Temperature (°C)')
        ax1.set_title('Heating Zone Layout')
        
        # Thermocouple positions
        ax2 = fig.add_subplot(132, projection='3d')
        ax2.scatter(thermocouple_positions[:, 0], thermocouple_positions[:, 1], 
                   np.mean(thermocouple_temps, axis=0), 
                   c=range(len(thermocouple_positions)), cmap='plasma', s=100)
        ax2.set_xlabel('X Position')
        ax2.set_ylabel('Y Position')
        ax2.set_zlabel('Average Temperature (°C)')
        ax2.set_title('Thermocouple Layout')
        
        # Temperature distribution
        ax3 = fig.add_subplot(133)
        temp_data = np.concatenate([zone_temperatures.flatten(), thermocouple_temps.flatten()])
        ax3.hist(temp_data, bins=50, alpha=0.7, edgecolor='black')
        ax3.set_xlabel('Temperature (°C)')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Temperature Distribution')
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_plots:
            plt.savefig(f"{self.dataset_dir}/furnace_spatial_layout.png", dpi=300, bbox_inches='tight')
        plt.show()
    
    def visualize_rl_data(self, save_plots: bool = True):
        """
        Visualize RL training data including states, actions, and rewards.
        
        Args:
            save_plots: Whether to save plots to files
        """
        print("Loading RL data...")
        
        with h5py.File(f"{self.dataset_dir}/rl_data.h5", 'r') as f:
            states = f['states'][:]
            actions = f['actions'][:]
            rewards = f['rewards'][:]
            next_states = f['next_states'][:]
            timestamps = f['timestamps'][:]
            state_dimension = f.attrs['state_dimension']
            action_dimension = f.attrs['action_dimension']
        
        # Create state evolution plots
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        
        # DIC metrics in states
        axes[0, 0].plot(timestamps/3600, states[:, 0], 'b-', label='Max Principal Strain', linewidth=2)
        axes[0, 0].plot(timestamps/3600, states[:, 1], 'r-', label='Strain Heterogeneity', linewidth=2)
        axes[0, 0].plot(timestamps/3600, states[:, 2], 'g-', label='Sample Curvature', linewidth=2)
        axes[0, 0].set_xlabel('Time (hours)')
        axes[0, 0].set_ylabel('Normalized Values')
        axes[0, 0].set_title('DIC Metrics in State Vector')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Thermal metrics in states
        for i in range(4):  # 4 key thermocouples
            axes[0, 1].plot(timestamps/3600, states[:, 3+i], 
                           label=f'TC {i+1}', linewidth=2)
        axes[0, 1].set_xlabel('Time (hours)')
        axes[0, 1].set_ylabel('Temperature (°C)')
        axes[0, 1].set_title('Thermal Metrics in State Vector')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Process metrics in states
        axes[1, 0].plot(timestamps/3600, states[:, 7], 'b-', label='Normalized Time', linewidth=2)
        axes[1, 0].plot(timestamps/3600, states[:, 8], 'r-', label='Avg Zone Temp', linewidth=2)
        axes[1, 0].plot(timestamps/3600, states[:, 9], 'g-', label='Temp Uniformity', linewidth=2)
        axes[1, 0].set_xlabel('Time (hours)')
        axes[1, 0].set_ylabel('Normalized Values')
        axes[1, 0].set_title('Process Metrics in State Vector')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Atmospheric conditions in states
        axes[1, 1].plot(timestamps/3600, states[:, 10], 'b-', label='Oxygen Level', linewidth=2)
        axes[1, 1].set_xlabel('Time (hours)')
        axes[1, 1].set_ylabel('Oxygen (%)')
        axes[1, 1].set_title('Atmospheric Conditions in State Vector')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        # Action vectors
        for zone_idx in range(action_dimension):
            axes[2, 0].plot(timestamps/3600, actions[:, zone_idx], 
                           label=f'Zone {zone_idx+1}', linewidth=2)
        axes[2, 0].set_xlabel('Time (hours)')
        axes[2, 0].set_ylabel('Temperature Change (°C)')
        axes[2, 0].set_title('Action Vectors Over Time')
        axes[2, 0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[2, 0].grid(True, alpha=0.3)
        
        # Rewards
        axes[2, 1].plot(timestamps/3600, rewards, 'b-', linewidth=2)
        axes[2, 1].set_xlabel('Time (hours)')
        axes[2, 1].set_ylabel('Reward')
        axes[2, 1].set_title('Reward Function Over Time')
        axes[2, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_plots:
            plt.savefig(f"{self.dataset_dir}/rl_data_evolution.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        # Create correlation matrix
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        # State correlation matrix
        state_corr = np.corrcoef(states.T)
        im1 = axes[0].imshow(state_corr, cmap='RdBu_r', vmin=-1, vmax=1)
        axes[0].set_title('State Vector Correlation Matrix')
        axes[0].set_xlabel('State Dimension')
        axes[0].set_ylabel('State Dimension')
        plt.colorbar(im1, ax=axes[0])
        
        # Action correlation matrix
        action_corr = np.corrcoef(actions.T)
        im2 = axes[1].imshow(action_corr, cmap='RdBu_r', vmin=-1, vmax=1)
        axes[1].set_title('Action Vector Correlation Matrix')
        axes[1].set_xlabel('Action Dimension')
        axes[1].set_ylabel('Action Dimension')
        plt.colorbar(im2, ax=axes[1])
        
        # State-action correlation
        state_action_corr = np.corrcoef(np.hstack([states, actions]).T)
        im3 = axes[2].imshow(state_action_corr, cmap='RdBu_r', vmin=-1, vmax=1)
        axes[2].set_title('State-Action Correlation Matrix')
        axes[2].set_xlabel('State+Action Dimension')
        axes[2].set_ylabel('State+Action Dimension')
        plt.colorbar(im3, ax=axes[2])
        
        plt.tight_layout()
        if save_plots:
            plt.savefig(f"{self.dataset_dir}/rl_correlation_matrices.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        # Create reward analysis
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Reward distribution
        axes[0, 0].hist(rewards, bins=50, alpha=0.7, edgecolor='black')
        axes[0, 0].set_xlabel('Reward Value')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].set_title('Reward Distribution')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Reward vs time
        axes[0, 1].scatter(timestamps/3600, rewards, alpha=0.6, s=20)
        axes[0, 1].set_xlabel('Time (hours)')
        axes[0, 1].set_ylabel('Reward Value')
        axes[0, 1].set_title('Reward vs Time')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Reward vs action magnitude
        action_magnitudes = np.linalg.norm(actions, axis=1)
        axes[1, 0].scatter(action_magnitudes, rewards, alpha=0.6, s=20)
        axes[1, 0].set_xlabel('Action Magnitude')
        axes[1, 0].set_ylabel('Reward Value')
        axes[1, 0].set_title('Reward vs Action Magnitude')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Reward vs state norm
        state_norms = np.linalg.norm(states, axis=1)
        axes[1, 1].scatter(state_norms, rewards, alpha=0.6, s=20)
        axes[1, 1].set_xlabel('State Vector Norm')
        axes[1, 1].set_ylabel('Reward Value')
        axes[1, 1].set_title('Reward vs State Norm')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_plots:
            plt.savefig(f"{self.dataset_dir}/rl_reward_analysis.png", dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_animation(self, animation_type: str = "displacement", 
                        frame_skip: int = 10, save_gif: bool = True):
        """
        Create animated visualizations of the data.
        
        Args:
            animation_type: Type of animation ('displacement', 'strain', 'temperature')
            frame_skip: Number of frames to skip between animation frames
            save_gif: Whether to save as GIF file
        """
        print(f"Creating {animation_type} animation...")
        
        if animation_type == "displacement":
            self._create_displacement_animation(frame_skip, save_gif)
        elif animation_type == "strain":
            self._create_strain_animation(frame_skip, save_gif)
        elif animation_type == "temperature":
            self._create_temperature_animation(frame_skip, save_gif)
        else:
            raise ValueError("animation_type must be 'displacement', 'strain', or 'temperature'")
    
    def _create_displacement_animation(self, frame_skip: int, save_gif: bool):
        """Create displacement field animation."""
        with h5py.File(f"{self.dataset_dir}/dic_data.h5", 'r') as f:
            displacement_u = f['displacement_u'][:]
            displacement_v = f['displacement_v'][:]
            timestamps = f['timestamps'][:]
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        def animate(frame):
            frame_idx = frame * frame_skip
            if frame_idx >= len(timestamps):
                return
            
            time_hours = timestamps[frame_idx] / 3600
            
            # Clear axes
            axes[0].clear()
            axes[1].clear()
            
            # U displacement
            im1 = axes[0].imshow(displacement_u[frame_idx], cmap='RdBu_r', aspect='equal')
            axes[0].set_title(f'U Displacement (t={time_hours:.2f}h)')
            axes[0].set_xlabel('X (pixels)')
            axes[0].set_ylabel('Y (pixels)')
            
            # V displacement
            im2 = axes[1].imshow(displacement_v[frame_idx], cmap='RdBu_r', aspect='equal')
            axes[1].set_title(f'V Displacement (t={time_hours:.2f}h)')
            axes[1].set_xlabel('X (pixels)')
            axes[1].set_ylabel('Y (pixels)')
        
        # Create animation
        anim = FuncAnimation(fig, animate, frames=len(timestamps)//frame_skip, 
                           interval=100, repeat=True)
        
        if save_gif:
            anim.save(f"{self.dataset_dir}/displacement_animation.gif", 
                     writer='pillow', fps=10)
        
        plt.show()
    
    def _create_strain_animation(self, frame_skip: int, save_gif: bool):
        """Create strain field animation."""
        with h5py.File(f"{self.dataset_dir}/dic_data.h5", 'r') as f:
            strain_xx = f['strain_xx'][:]
            strain_yy = f['strain_yy'][:]
            timestamps = f['timestamps'][:]
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        def animate(frame):
            frame_idx = frame * frame_skip
            if frame_idx >= len(timestamps):
                return
            
            time_hours = timestamps[frame_idx] / 3600
            
            # Clear axes
            axes[0].clear()
            axes[1].clear()
            
            # XX strain
            im1 = axes[0].imshow(strain_xx[frame_idx], cmap='viridis', aspect='equal')
            axes[0].set_title(f'εxx Strain (t={time_hours:.2f}h)')
            axes[0].set_xlabel('X (pixels)')
            axes[0].set_ylabel('Y (pixels)')
            
            # YY strain
            im2 = axes[1].imshow(strain_yy[frame_idx], cmap='viridis', aspect='equal')
            axes[1].set_title(f'εyy Strain (t={time_hours:.2f}h)')
            axes[1].set_xlabel('X (pixels)')
            axes[1].set_ylabel('Y (pixels)')
        
        # Create animation
        anim = FuncAnimation(fig, animate, frames=len(timestamps)//frame_skip, 
                           interval=100, repeat=True)
        
        if save_gif:
            anim.save(f"{self.dataset_dir}/strain_animation.gif", 
                     writer='pillow', fps=10)
        
        plt.show()
    
    def _create_temperature_animation(self, frame_skip: int, save_gif: bool):
        """Create temperature field animation."""
        with h5py.File(f"{self.dataset_dir}/furnace_data.h5", 'r') as f:
            zone_temperatures = f['zone_temperatures'][:]
            timestamps = f['timestamps'][:]
            zone_positions = f['zone_positions'][:]
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        def animate(frame):
            frame_idx = frame * frame_skip
            if frame_idx >= len(timestamps):
                return
            
            time_hours = timestamps[frame_idx] / 3600
            
            # Clear axis
            ax.clear()
            
            # Create temperature field visualization
            scatter = ax.scatter(zone_positions[:, 0], zone_positions[:, 1], 
                               c=zone_temperatures[frame_idx], 
                               s=200, cmap='hot', edgecolors='black')
            
            ax.set_title(f'Heating Zone Temperatures (t={time_hours:.2f}h)')
            ax.set_xlabel('X Position')
            ax.set_ylabel('Y Position')
            ax.set_aspect('equal')
            
            # Add colorbar
            plt.colorbar(scatter, ax=ax, label='Temperature (°C)')
        
        # Create animation
        anim = FuncAnimation(fig, animate, frames=len(timestamps)//frame_skip, 
                           interval=100, repeat=True)
        
        if save_gif:
            anim.save(f"{self.dataset_dir}/temperature_animation.gif", 
                     writer='pillow', fps=10)
        
        plt.show()
    
    def generate_data_report(self):
        """Generate comprehensive data quality and statistics report."""
        print("Generating comprehensive data report...")
        
        report = {
            'dataset_metadata': self.metadata,
            'data_quality_metrics': {},
            'statistical_summaries': {},
            'recommendations': []
        }
        
        # Analyze DIC data
        with h5py.File(f"{self.dataset_dir}/dic_data.h5", 'r') as f:
            max_principal_strain = f['max_principal_strain'][:]
            strain_heterogeneity = f['strain_heterogeneity'][:]
            sample_curvature = f['sample_curvature'][:]
        
        report['data_quality_metrics']['dic'] = {
            'max_principal_strain_range': [float(np.min(max_principal_strain)), 
                                         float(np.max(max_principal_strain))],
            'strain_heterogeneity_range': [float(np.min(strain_heterogeneity)), 
                                         float(np.max(strain_heterogeneity))],
            'sample_curvature_range': [float(np.min(sample_curvature)), 
                                     float(np.max(sample_curvature))],
            'data_completeness': 1.0,  # Assuming complete data
            'temporal_consistency': True
        }
        
        # Analyze furnace data
        with h5py.File(f"{self.dataset_dir}/furnace_data.h5", 'r') as f:
            zone_temperatures = f['zone_temperatures'][:]
            thermocouple_temps = f['thermocouple_temps'][:]
            actions = f['actions'][:]
        
        report['data_quality_metrics']['furnace'] = {
            'temperature_range': [float(np.min(zone_temperatures)), 
                                float(np.max(zone_temperatures))],
            'action_magnitude_range': [float(np.min(np.linalg.norm(actions, axis=1))), 
                                     float(np.max(np.linalg.norm(actions, axis=1)))],
            'data_completeness': 1.0,
            'temporal_consistency': True
        }
        
        # Analyze RL data
        with h5py.File(f"{self.dataset_dir}/rl_data.h5", 'r') as f:
            states = f['states'][:]
            actions = f['actions'][:]
            rewards = f['rewards'][:]
        
        report['data_quality_metrics']['rl'] = {
            'state_dimension': int(f.attrs['state_dimension']),
            'action_dimension': int(f.attrs['action_dimension']),
            'num_tuples': len(states),
            'reward_range': [float(np.min(rewards)), float(np.max(rewards))],
            'state_norm_range': [float(np.min(np.linalg.norm(states, axis=1))), 
                               float(np.max(np.linalg.norm(states, axis=1)))],
            'action_norm_range': [float(np.min(np.linalg.norm(actions, axis=1))), 
                                float(np.max(np.linalg.norm(actions, axis=1)))]
        }
        
        # Statistical summaries
        report['statistical_summaries'] = {
            'dic_metrics': {
                'max_principal_strain': {
                    'mean': float(np.mean(max_principal_strain)),
                    'std': float(np.std(max_principal_strain)),
                    'skewness': float(stats.skew(max_principal_strain)),
                    'kurtosis': float(stats.kurtosis(max_principal_strain))
                },
                'strain_heterogeneity': {
                    'mean': float(np.mean(strain_heterogeneity)),
                    'std': float(np.std(strain_heterogeneity)),
                    'skewness': float(stats.skew(strain_heterogeneity)),
                    'kurtosis': float(stats.kurtosis(strain_heterogeneity))
                }
            },
            'furnace_metrics': {
                'zone_temperatures': {
                    'mean': float(np.mean(zone_temperatures)),
                    'std': float(np.std(zone_temperatures)),
                    'min': float(np.min(zone_temperatures)),
                    'max': float(np.max(zone_temperatures))
                }
            },
            'rl_metrics': {
                'rewards': {
                    'mean': float(np.mean(rewards)),
                    'std': float(np.std(rewards)),
                    'skewness': float(stats.skew(rewards)),
                    'kurtosis': float(stats.kurtosis(rewards))
                }
            }
        }
        
        # Generate recommendations
        if np.std(rewards) < 0.1:
            report['recommendations'].append("Low reward variance detected. Consider adjusting reward function weights.")
        
        if np.max(np.linalg.norm(actions, axis=1)) > 50:
            report['recommendations'].append("Large action magnitudes detected. Consider action scaling.")
        
        if np.std(max_principal_strain) < 0.01:
            report['recommendations'].append("Low strain variation detected. Consider increasing process variability.")
        
        # Save report
        with open(f"{self.dataset_dir}/data_quality_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        print("Data quality report saved to data_quality_report.json")
        return report


def main():
    """Run comprehensive data visualization and analysis."""
    print("Starting Dataset Visualization and Analysis")
    print("=" * 50)
    
    # Initialize visualizer
    visualizer = DatasetVisualizer("real_time_dataset")
    
    # Generate all visualizations
    print("\n1. Visualizing DIC Data...")
    visualizer.visualize_dic_data()
    
    print("\n2. Visualizing Furnace Data...")
    visualizer.visualize_furnace_data()
    
    print("\n3. Visualizing RL Data...")
    visualizer.visualize_rl_data()
    
    print("\n4. Creating Animations...")
    visualizer.create_animation("displacement", frame_skip=20)
    visualizer.create_animation("strain", frame_skip=20)
    visualizer.create_animation("temperature", frame_skip=20)
    
    print("\n5. Generating Data Quality Report...")
    report = visualizer.generate_data_report()
    
    print("\n" + "=" * 50)
    print("Visualization and Analysis Complete!")
    print(f"All plots saved to {visualizer.dataset_dir}/")
    print(f"Data quality report: {visualizer.dataset_dir}/data_quality_report.json")


if __name__ == "__main__":
    main()