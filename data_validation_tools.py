#!/usr/bin/env python3
"""
Data Validation and Visualization Tools
For Real-Time Training & Validation Dataset

This module provides comprehensive tools to validate and visualize the generated dataset.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import h5py
import pickle
import json
from pathlib import Path
import cv2
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class DatasetValidator:
    """Comprehensive dataset validation and visualization"""
    
    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)
        self.validation_results = {}
        
        # Load all data
        self.load_dataset()
        
    def load_dataset(self):
        """Load all dataset components"""
        print("Loading dataset for validation...")
        
        # Load DIC data
        self.dic_file = h5py.File(self.dataset_path / "dic_data" / "dic_dataset.h5", 'r')
        
        # Load furnace data
        self.furnace_df = pd.read_csv(self.dataset_path / "furnace_data" / "furnace_states.csv")
        with open(self.dataset_path / "furnace_data" / "furnace_states.pkl", 'rb') as f:
            self.furnace_states = pickle.load(f)
        
        # Load RL data
        self.rl_states_df = pd.read_csv(self.dataset_path / "rl_data" / "rl_states.csv")
        self.rl_actions_df = pd.read_csv(self.dataset_path / "rl_data" / "rl_actions.csv")
        self.rl_rewards_df = pd.read_csv(self.dataset_path / "rl_data" / "rl_rewards.csv")
        
        with open(self.dataset_path / "rl_data" / "rl_tuples.pkl", 'rb') as f:
            self.rl_tuples = pickle.load(f)
        
        # Load metadata
        with open(self.dataset_path / "metadata" / "dataset_metadata.json", 'r') as f:
            self.metadata = json.load(f)
        
        print("Dataset loaded successfully!")
    
    def validate_data_integrity(self):
        """Validate data integrity and consistency"""
        print("Validating data integrity...")
        
        results = {}
        
        # Check DIC data shapes and ranges
        dic_shapes = {}
        dic_ranges = {}
        
        for group_name in ['displacements', 'strains', 'temperatures', 'quality']:
            group = self.dic_file[group_name]
            for dataset_name in group.keys():
                data = group[dataset_name][:]
                dic_shapes[f"{group_name}/{dataset_name}"] = data.shape
                dic_ranges[f"{group_name}/{dataset_name}"] = (data.min(), data.max())
        
        results['dic_shapes'] = dic_shapes
        results['dic_ranges'] = dic_ranges
        
        # Check for NaN or infinite values
        nan_counts = {}
        for group_name in ['displacements', 'strains', 'temperatures', 'quality']:
            group = self.dic_file[group_name]
            for dataset_name in group.keys():
                data = group[dataset_name][:]
                nan_count = np.sum(np.isnan(data)) + np.sum(np.isinf(data))
                nan_counts[f"{group_name}/{dataset_name}"] = nan_count
        
        results['nan_counts'] = nan_counts
        
        # Check timestamp synchronization
        dic_timestamps = self.dic_file['metadata']['timestamps'][:]
        furnace_timestamps = self.furnace_df['timestamp'].values
        rl_timestamps = self.rl_states_df['timestamp'].values
        
        results['timestamp_ranges'] = {
            'dic': (dic_timestamps.min(), dic_timestamps.max()),
            'furnace': (furnace_timestamps.min(), furnace_timestamps.max()),
            'rl': (rl_timestamps.min(), rl_timestamps.max())
        }
        
        # Check data continuity
        dic_dt = np.diff(dic_timestamps)
        furnace_dt = np.diff(furnace_timestamps)
        rl_dt = np.diff(rl_timestamps)
        
        results['sampling_rates'] = {
            'dic_mean_hz': 1.0 / np.mean(dic_dt),
            'dic_std_hz': np.std(1.0 / dic_dt),
            'furnace_mean_hz': 1.0 / np.mean(furnace_dt),
            'furnace_std_hz': np.std(1.0 / furnace_dt),
            'rl_mean_hz': 1.0 / np.mean(rl_dt),
            'rl_std_hz': np.std(1.0 / rl_dt)
        }
        
        # Physical plausibility checks
        results['physical_checks'] = self.check_physical_plausibility()
        
        self.validation_results['integrity'] = results
        
        print("Data integrity validation complete!")
        return results
    
    def check_physical_plausibility(self):
        """Check if generated data is physically plausible"""
        checks = {}
        
        # Temperature ranges
        temp_data = self.dic_file['temperatures']['temperature_field'][:]
        checks['temperature_range'] = {
            'min': temp_data.min(),
            'max': temp_data.max(),
            'plausible': 0 <= temp_data.min() and temp_data.max() <= 2000
        }
        
        # Displacement magnitudes
        U = self.dic_file['displacements']['U'][:]
        V = self.dic_file['displacements']['V'][:]
        W = self.dic_file['displacements']['W'][:]
        
        displacement_magnitude = np.sqrt(U**2 + V**2 + W**2)
        checks['displacement_magnitude'] = {
            'max': displacement_magnitude.max(),
            'mean': displacement_magnitude.mean(),
            'plausible': displacement_magnitude.max() < 50  # mm
        }
        
        # Strain ranges
        strain_max = self.dic_file['strains']['strain_principal_max'][:]
        checks['strain_range'] = {
            'max': strain_max.max(),
            'min': strain_max.min(),
            'plausible': -0.5 < strain_max.min() and strain_max.max() < 0.1
        }
        
        # Furnace temperatures
        zone_temps = [col for col in self.furnace_df.columns if 'zone_' in col and 'temperature' in col]
        furnace_temp_max = self.furnace_df[zone_temps].max().max()
        furnace_temp_min = self.furnace_df[zone_temps].min().min()
        
        checks['furnace_temperatures'] = {
            'max': furnace_temp_max,
            'min': furnace_temp_min,
            'plausible': 0 <= furnace_temp_min and furnace_temp_max <= 2000
        }
        
        # RL reward ranges
        checks['rl_rewards'] = {
            'max': self.rl_rewards_df['total_reward'].max(),
            'min': self.rl_rewards_df['total_reward'].min(),
            'mean': self.rl_rewards_df['total_reward'].mean(),
            'plausible': -10 <= self.rl_rewards_df['total_reward'].min() and self.rl_rewards_df['total_reward'].max() <= 5
        }
        
        return checks
    
    def create_comprehensive_visualizations(self):
        """Create comprehensive visualizations of the dataset"""
        print("Creating comprehensive visualizations...")
        
        # Create output directory
        viz_dir = self.dataset_path / "visualizations"
        viz_dir.mkdir(exist_ok=True)
        
        # 1. DIC Field Evolution
        self.plot_dic_field_evolution(viz_dir)
        
        # 2. Thermal Cycle Analysis
        self.plot_thermal_cycle_analysis(viz_dir)
        
        # 3. RL Training Data Analysis
        self.plot_rl_analysis(viz_dir)
        
        # 4. Correlation Analysis
        self.plot_correlation_analysis(viz_dir)
        
        # 5. Data Quality Metrics
        self.plot_data_quality_metrics(viz_dir)
        
        # 6. Interactive Dashboard
        self.create_interactive_dashboard(viz_dir)
        
        print(f"Visualizations saved to {viz_dir}")
    
    def plot_dic_field_evolution(self, output_dir):
        """Plot evolution of DIC fields over time"""
        print("  Creating DIC field evolution plots...")
        
        # Sample time points
        timestamps = self.dic_file['metadata']['timestamps'][:]
        sample_indices = [0, len(timestamps)//4, len(timestamps)//2, 3*len(timestamps)//4, len(timestamps)-1]
        
        # Load displacement and strain data
        U = self.dic_file['displacements']['U'][:]
        V = self.dic_file['displacements']['V'][:]
        W = self.dic_file['displacements']['W'][:]
        strain_max = self.dic_file['strains']['strain_principal_max'][:]
        temp_field = self.dic_file['temperatures']['temperature_field'][:]
        
        # Create multi-panel figure
        fig, axes = plt.subplots(5, 5, figsize=(20, 20))
        
        for i, idx in enumerate(sample_indices):
            time_hours = timestamps[idx] / 3600
            
            # Displacement magnitude
            disp_mag = np.sqrt(U[idx]**2 + V[idx]**2 + W[idx]**2)
            im1 = axes[0, i].imshow(disp_mag, cmap='viridis')
            axes[0, i].set_title(f'Displacement Mag\nt={time_hours:.1f}h')
            plt.colorbar(im1, ax=axes[0, i])
            
            # U displacement
            im2 = axes[1, i].imshow(U[idx], cmap='RdBu_r')
            axes[1, i].set_title(f'U Displacement\nt={time_hours:.1f}h')
            plt.colorbar(im2, ax=axes[1, i])
            
            # V displacement
            im3 = axes[2, i].imshow(V[idx], cmap='RdBu_r')
            axes[2, i].set_title(f'V Displacement\nt={time_hours:.1f}h')
            plt.colorbar(im3, ax=axes[2, i])
            
            # Maximum principal strain
            im4 = axes[3, i].imshow(strain_max[idx], cmap='plasma')
            axes[3, i].set_title(f'Max Principal Strain\nt={time_hours:.1f}h')
            plt.colorbar(im4, ax=axes[3, i])
            
            # Temperature field
            im5 = axes[4, i].imshow(temp_field[idx], cmap='hot')
            axes[4, i].set_title(f'Temperature\nt={time_hours:.1f}h')
            plt.colorbar(im5, ax=axes[4, i])
        
        plt.tight_layout()
        plt.savefig(output_dir / "dic_field_evolution.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot field statistics over time
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Calculate statistics over time (subsample for performance)
        step = max(1, len(timestamps) // 1000)
        time_subset = timestamps[::step] / 3600
        
        disp_mag_mean = []
        strain_max_mean = []
        temp_mean = []
        temp_std = []
        
        for i in range(0, len(timestamps), step):
            disp_mag = np.sqrt(U[i]**2 + V[i]**2 + W[i]**2)
            disp_mag_mean.append(np.mean(disp_mag))
            strain_max_mean.append(np.mean(strain_max[i]))
            temp_mean.append(np.mean(temp_field[i]))
            temp_std.append(np.std(temp_field[i]))
        
        axes[0, 0].plot(time_subset, disp_mag_mean)
        axes[0, 0].set_title('Mean Displacement Magnitude')
        axes[0, 0].set_xlabel('Time (hours)')
        axes[0, 0].set_ylabel('Displacement (mm)')
        
        axes[0, 1].plot(time_subset, strain_max_mean)
        axes[0, 1].set_title('Mean Maximum Principal Strain')
        axes[0, 1].set_xlabel('Time (hours)')
        axes[0, 1].set_ylabel('Strain')
        
        axes[1, 0].plot(time_subset, temp_mean)
        axes[1, 0].set_title('Mean Temperature')
        axes[1, 0].set_xlabel('Time (hours)')
        axes[1, 0].set_ylabel('Temperature (°C)')
        
        axes[1, 1].plot(time_subset, temp_std)
        axes[1, 1].set_title('Temperature Standard Deviation')
        axes[1, 1].set_xlabel('Time (hours)')
        axes[1, 1].set_ylabel('Temperature Std (°C)')
        
        plt.tight_layout()
        plt.savefig(output_dir / "dic_statistics_evolution.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_thermal_cycle_analysis(self, output_dir):
        """Plot thermal cycle and furnace control analysis"""
        print("  Creating thermal cycle analysis plots...")
        
        # Convert timestamps to hours
        self.furnace_df['time_hours'] = self.furnace_df['timestamp'] / 3600
        
        # Zone temperature evolution
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        
        # Zone temperatures
        zone_temp_cols = [col for col in self.furnace_df.columns if 'zone_' in col and 'temperature' in col]
        zone_setpoint_cols = [col for col in self.furnace_df.columns if 'zone_' in col and 'setpoint' in col]
        zone_power_cols = [col for col in self.furnace_df.columns if 'zone_' in col and 'power' in col]
        
        for i, (temp_col, setpoint_col) in enumerate(zip(zone_temp_cols[:3], zone_setpoint_cols[:3])):
            axes[0, 0].plot(self.furnace_df['time_hours'], self.furnace_df[temp_col], 
                           label=f'Zone {i} Actual', alpha=0.8)
            axes[0, 0].plot(self.furnace_df['time_hours'], self.furnace_df[setpoint_col], 
                           '--', label=f'Zone {i} Setpoint', alpha=0.6)
        
        axes[0, 0].set_title('Zone Temperatures vs Setpoints')
        axes[0, 0].set_xlabel('Time (hours)')
        axes[0, 0].set_ylabel('Temperature (°C)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Zone powers
        for i, power_col in enumerate(zone_power_cols[:3]):
            axes[0, 1].plot(self.furnace_df['time_hours'], self.furnace_df[power_col], 
                           label=f'Zone {i} Power', alpha=0.8)
        
        axes[0, 1].set_title('Zone Power Outputs')
        axes[0, 1].set_xlabel('Time (hours)')
        axes[0, 1].set_ylabel('Power (%)')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Gas flows
        gas_flow_cols = [col for col in self.furnace_df.columns if 'gas_flow' in col]
        for i, flow_col in enumerate(gas_flow_cols):
            axes[1, 0].plot(self.furnace_df['time_hours'], self.furnace_df[flow_col], 
                           label=f'Gas Flow {i}', alpha=0.8)
        
        axes[1, 0].set_title('Gas Flow Rates')
        axes[1, 0].set_xlabel('Time (hours)')
        axes[1, 0].set_ylabel('Flow Rate')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Pressure
        axes[1, 1].plot(self.furnace_df['time_hours'], self.furnace_df['pressure'])
        axes[1, 1].set_title('Chamber Pressure')
        axes[1, 1].set_xlabel('Time (hours)')
        axes[1, 1].set_ylabel('Pressure')
        axes[1, 1].grid(True, alpha=0.3)
        
        # Atmosphere composition
        atm_cols = [col for col in self.furnace_df.columns if 'atmosphere_' in col]
        for col in atm_cols:
            gas_name = col.replace('atmosphere_', '')
            axes[2, 0].plot(self.furnace_df['time_hours'], self.furnace_df[col], 
                           label=gas_name, alpha=0.8)
        
        axes[2, 0].set_title('Atmosphere Composition')
        axes[2, 0].set_xlabel('Time (hours)')
        axes[2, 0].set_ylabel('Percentage (%)')
        axes[2, 0].legend()
        axes[2, 0].grid(True, alpha=0.3)
        
        # Temperature uniformity
        temp_std = self.furnace_df[zone_temp_cols].std(axis=1)
        axes[2, 1].plot(self.furnace_df['time_hours'], temp_std)
        axes[2, 1].set_title('Temperature Uniformity (Std Dev)')
        axes[2, 1].set_xlabel('Time (hours)')
        axes[2, 1].set_ylabel('Temperature Std (°C)')
        axes[2, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / "thermal_cycle_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_rl_analysis(self, output_dir):
        """Plot RL training data analysis"""
        print("  Creating RL analysis plots...")
        
        # Convert timestamps to hours
        self.rl_states_df['time_hours'] = self.rl_states_df['timestamp'] / 3600
        self.rl_actions_df['time_hours'] = self.rl_actions_df['timestamp'] / 3600
        self.rl_rewards_df['time_hours'] = self.rl_rewards_df['timestamp'] / 3600
        
        # Create comprehensive RL analysis
        fig, axes = plt.subplots(3, 3, figsize=(18, 15))
        
        # State evolution
        state_cols = ['max_principal_strain', 'strain_heterogeneity', 'sample_curvature', 
                     'avg_temperature', 'estimated_density', 'dic_quality']
        
        for i, col in enumerate(state_cols[:6]):
            row, col_idx = i // 3, i % 3
            if row < 2:
                axes[row, col_idx].plot(self.rl_states_df['time_hours'], self.rl_states_df[col])
                axes[row, col_idx].set_title(f'State: {col}')
                axes[row, col_idx].set_xlabel('Time (hours)')
                axes[row, col_idx].grid(True, alpha=0.3)
        
        # Reward components
        reward_cols = ['warpage_penalty', 'strain_penalty', 'density_reward', 'efficiency_reward', 'total_reward']
        
        for col in reward_cols[:4]:
            axes[2, 0].plot(self.rl_rewards_df['time_hours'], self.rl_rewards_df[col], 
                           label=col, alpha=0.8)
        
        axes[2, 0].set_title('Reward Components')
        axes[2, 0].set_xlabel('Time (hours)')
        axes[2, 0].legend()
        axes[2, 0].grid(True, alpha=0.3)
        
        # Total reward
        axes[2, 1].plot(self.rl_rewards_df['time_hours'], self.rl_rewards_df['total_reward'])
        axes[2, 1].set_title('Total Reward')
        axes[2, 1].set_xlabel('Time (hours)')
        axes[2, 1].grid(True, alpha=0.3)
        
        # Action magnitude
        action_cols = [col for col in self.rl_actions_df.columns if 'temp_change' in col or 'power_change' in col]
        action_magnitude = np.sqrt(self.rl_actions_df[action_cols].pow(2).sum(axis=1))
        
        axes[2, 2].plot(self.rl_actions_df['time_hours'], action_magnitude)
        axes[2, 2].set_title('Action Magnitude')
        axes[2, 2].set_xlabel('Time (hours)')
        axes[2, 2].set_ylabel('Action Magnitude')
        axes[2, 2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / "rl_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # State-action correlation heatmap
        plt.figure(figsize=(12, 8))
        
        # Combine state and action data
        state_action_df = pd.merge(self.rl_states_df, self.rl_actions_df, on='timestamp', how='inner')
        
        # Select key columns for correlation
        key_cols = ['max_principal_strain', 'sample_curvature', 'avg_temperature', 'estimated_density'] + \
                  [col for col in state_action_df.columns if 'temp_change' in col][:3]
        
        correlation_matrix = state_action_df[key_cols].corr()
        
        sns.heatmap(correlation_matrix, annot=True, cmap='RdBu_r', center=0, 
                   square=True, fmt='.2f')
        plt.title('State-Action Correlation Matrix')
        plt.tight_layout()
        plt.savefig(output_dir / "state_action_correlation.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_correlation_analysis(self, output_dir):
        """Plot comprehensive correlation analysis"""
        print("  Creating correlation analysis plots...")
        
        # Load sample DIC data for correlation
        sample_indices = np.linspace(0, len(self.dic_file['metadata']['timestamps'][:]) - 1, 100, dtype=int)
        
        dic_metrics = []
        for idx in sample_indices:
            U = self.dic_file['displacements']['U'][idx]
            V = self.dic_file['displacements']['V'][idx]
            strain_max = self.dic_file['strains']['strain_principal_max'][idx]
            temp = self.dic_file['temperatures']['temperature_field'][idx]
            
            metrics = {
                'timestamp': self.dic_file['metadata']['timestamps'][idx],
                'max_displacement': np.sqrt(U**2 + V**2).max(),
                'mean_strain': np.mean(strain_max),
                'max_strain': np.max(strain_max),
                'temp_mean': np.mean(temp),
                'temp_std': np.std(temp)
            }
            dic_metrics.append(metrics)
        
        dic_sample_df = pd.DataFrame(dic_metrics)
        
        # Merge with furnace data
        furnace_sample = self.furnace_df.iloc[::len(self.furnace_df)//100]  # Sample furnace data
        
        # Create correlation plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Temperature vs strain correlation
        axes[0, 0].scatter(dic_sample_df['temp_mean'], dic_sample_df['max_strain'], alpha=0.6)
        axes[0, 0].set_xlabel('Mean Temperature (°C)')
        axes[0, 0].set_ylabel('Maximum Strain')
        axes[0, 0].set_title('Temperature vs Strain Correlation')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Add correlation coefficient
        corr_coef = np.corrcoef(dic_sample_df['temp_mean'], dic_sample_df['max_strain'])[0, 1]
        axes[0, 0].text(0.05, 0.95, f'r = {corr_coef:.3f}', transform=axes[0, 0].transAxes, 
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Temperature gradient vs displacement
        axes[0, 1].scatter(dic_sample_df['temp_std'], dic_sample_df['max_displacement'], alpha=0.6)
        axes[0, 1].set_xlabel('Temperature Std Dev (°C)')
        axes[0, 1].set_ylabel('Maximum Displacement (mm)')
        axes[0, 1].set_title('Temperature Gradient vs Displacement')
        axes[0, 1].grid(True, alpha=0.3)
        
        corr_coef = np.corrcoef(dic_sample_df['temp_std'], dic_sample_df['max_displacement'])[0, 1]
        axes[0, 1].text(0.05, 0.95, f'r = {corr_coef:.3f}', transform=axes[0, 1].transAxes,
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Reward vs density correlation
        axes[1, 0].scatter(self.rl_states_df['estimated_density'], self.rl_rewards_df['total_reward'], alpha=0.6)
        axes[1, 0].set_xlabel('Estimated Density')
        axes[1, 0].set_ylabel('Total Reward')
        axes[1, 0].set_title('Density vs Reward Correlation')
        axes[1, 0].grid(True, alpha=0.3)
        
        corr_coef = np.corrcoef(self.rl_states_df['estimated_density'][:len(self.rl_rewards_df)], 
                               self.rl_rewards_df['total_reward'])[0, 1]
        axes[1, 0].text(0.05, 0.95, f'r = {corr_coef:.3f}', transform=axes[1, 0].transAxes,
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Multi-objective reward analysis
        reward_components = self.rl_rewards_df[['warpage_penalty', 'strain_penalty', 'density_reward', 'efficiency_reward']]
        
        # PCA of reward components
        scaler = StandardScaler()
        reward_scaled = scaler.fit_transform(reward_components)
        pca = PCA(n_components=2)
        reward_pca = pca.fit_transform(reward_scaled)
        
        scatter = axes[1, 1].scatter(reward_pca[:, 0], reward_pca[:, 1], 
                                   c=self.rl_rewards_df['total_reward'], cmap='viridis', alpha=0.6)
        axes[1, 1].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2f})')
        axes[1, 1].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2f})')
        axes[1, 1].set_title('Reward Components PCA')
        plt.colorbar(scatter, ax=axes[1, 1], label='Total Reward')
        
        plt.tight_layout()
        plt.savefig(output_dir / "correlation_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_data_quality_metrics(self, output_dir):
        """Plot data quality and validation metrics"""
        print("  Creating data quality metrics plots...")
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # DIC quality evolution
        quality_data = self.dic_file['quality']['quality_map'][:]
        timestamps = self.dic_file['metadata']['timestamps'][:] / 3600
        
        # Sample for performance
        step = max(1, len(timestamps) // 1000)
        time_subset = timestamps[::step]
        quality_mean = [np.mean(quality_data[i]) for i in range(0, len(quality_data), step)]
        quality_min = [np.min(quality_data[i]) for i in range(0, len(quality_data), step)]
        
        axes[0, 0].plot(time_subset, quality_mean, label='Mean Quality')
        axes[0, 0].plot(time_subset, quality_min, label='Min Quality')
        axes[0, 0].set_title('DIC Quality Evolution')
        axes[0, 0].set_xlabel('Time (hours)')
        axes[0, 0].set_ylabel('DIC Quality')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Sampling rate consistency
        dic_dt = np.diff(self.dic_file['metadata']['timestamps'][:])
        furnace_dt = np.diff(self.furnace_df['timestamp'].values)
        
        axes[0, 1].hist(1.0/dic_dt, bins=50, alpha=0.7, label='DIC Sampling Rate')
        axes[0, 1].axvline(np.mean(1.0/dic_dt), color='red', linestyle='--', label=f'Mean: {np.mean(1.0/dic_dt):.1f} Hz')
        axes[0, 1].set_title('DIC Sampling Rate Distribution')
        axes[0, 1].set_xlabel('Sampling Rate (Hz)')
        axes[0, 1].set_ylabel('Count')
        axes[0, 1].legend()
        
        axes[0, 2].hist(1.0/furnace_dt, bins=50, alpha=0.7, label='Furnace Sampling Rate')
        axes[0, 2].axvline(np.mean(1.0/furnace_dt), color='red', linestyle='--', label=f'Mean: {np.mean(1.0/furnace_dt):.1f} Hz')
        axes[0, 2].set_title('Furnace Sampling Rate Distribution')
        axes[0, 2].set_xlabel('Sampling Rate (Hz)')
        axes[0, 2].set_ylabel('Count')
        axes[0, 2].legend()
        
        # Data completeness
        completeness_metrics = {
            'DIC Frames': len(self.dic_file['metadata']['timestamps'][:]),
            'Furnace States': len(self.furnace_df),
            'RL States': len(self.rl_states_df),
            'RL Actions': len(self.rl_actions_df),
            'RL Rewards': len(self.rl_rewards_df)
        }
        
        axes[1, 0].bar(completeness_metrics.keys(), completeness_metrics.values())
        axes[1, 0].set_title('Data Completeness')
        axes[1, 0].set_ylabel('Number of Records')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Physical constraint validation
        constraint_checks = self.validation_results.get('integrity', {}).get('physical_checks', {})
        
        if constraint_checks:
            check_names = []
            check_results = []
            
            for check_name, check_data in constraint_checks.items():
                if isinstance(check_data, dict) and 'plausible' in check_data:
                    check_names.append(check_name)
                    check_results.append(1 if check_data['plausible'] else 0)
            
            colors = ['green' if result else 'red' for result in check_results]
            axes[1, 1].bar(check_names, check_results, color=colors)
            axes[1, 1].set_title('Physical Constraint Validation')
            axes[1, 1].set_ylabel('Pass (1) / Fail (0)')
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        # Data distribution normality tests
        # Test key variables for normality
        test_vars = {
            'Max Strain': self.rl_states_df['max_principal_strain'],
            'Temperature': self.rl_states_df['avg_temperature'],
            'Density': self.rl_states_df['estimated_density'],
            'Total Reward': self.rl_rewards_df['total_reward']
        }
        
        normality_results = {}
        for var_name, data in test_vars.items():
            statistic, p_value = stats.normaltest(data.dropna())
            normality_results[var_name] = p_value > 0.05  # Normal if p > 0.05
        
        colors = ['green' if result else 'orange' for result in normality_results.values()]
        axes[1, 2].bar(normality_results.keys(), [1 if result else 0 for result in normality_results.values()], 
                      color=colors)
        axes[1, 2].set_title('Data Normality Tests')
        axes[1, 2].set_ylabel('Normal (1) / Non-normal (0)')
        axes[1, 2].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_dir / "data_quality_metrics.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_interactive_dashboard(self, output_dir):
        """Create interactive Plotly dashboard"""
        print("  Creating interactive dashboard...")
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('DIC Quality Over Time', 'Temperature Evolution', 
                          'RL Reward Components', 'State-Action Relationship',
                          'Strain vs Temperature', 'Density Progress'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Sample data for performance
        sample_step = max(1, len(self.rl_states_df) // 1000)
        sample_df = self.rl_states_df.iloc[::sample_step].copy()
        sample_rewards = self.rl_rewards_df.iloc[::sample_step].copy()
        
        # DIC Quality
        quality_data = self.dic_file['quality']['quality_map'][:]
        timestamps = self.dic_file['metadata']['timestamps'][:] / 3600
        
        step = max(1, len(timestamps) // 500)
        time_subset = timestamps[::step]
        quality_mean = [np.mean(quality_data[i]) for i in range(0, len(quality_data), step)]
        
        fig.add_trace(
            go.Scatter(x=time_subset, y=quality_mean, name='DIC Quality', 
                      line=dict(color='blue')),
            row=1, col=1
        )
        
        # Temperature Evolution
        fig.add_trace(
            go.Scatter(x=sample_df['timestamp']/3600, y=sample_df['avg_temperature'], 
                      name='Avg Temperature', line=dict(color='red')),
            row=1, col=2
        )
        
        # RL Reward Components
        reward_cols = ['warpage_penalty', 'strain_penalty', 'density_reward', 'efficiency_reward']
        colors = ['red', 'orange', 'green', 'blue']
        
        for col, color in zip(reward_cols, colors):
            fig.add_trace(
                go.Scatter(x=sample_rewards['timestamp']/3600, y=sample_rewards[col], 
                          name=col, line=dict(color=color)),
                row=2, col=1
            )
        
        # State-Action Relationship (sample curvature vs actions)
        sample_actions = self.rl_actions_df.iloc[::sample_step].copy()
        action_magnitude = np.sqrt(sample_actions[[col for col in sample_actions.columns if 'temp_change' in col]].pow(2).sum(axis=1))
        
        fig.add_trace(
            go.Scatter(x=sample_df['sample_curvature'], y=action_magnitude, 
                      mode='markers', name='Curvature vs Action',
                      marker=dict(color=sample_df['timestamp']/3600, colorscale='viridis')),
            row=2, col=2
        )
        
        # Strain vs Temperature
        fig.add_trace(
            go.Scatter(x=sample_df['avg_temperature'], y=sample_df['max_principal_strain'],
                      mode='markers', name='Strain vs Temp',
                      marker=dict(color=sample_df['timestamp']/3600, colorscale='plasma')),
            row=3, col=1
        )
        
        # Density Progress
        fig.add_trace(
            go.Scatter(x=sample_df['timestamp']/3600, y=sample_df['estimated_density'],
                      name='Density Progress', line=dict(color='purple')),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=1200,
            title_text="Real-Time Dataset Interactive Dashboard",
            showlegend=True
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Time (hours)", row=1, col=1)
        fig.update_xaxes(title_text="Time (hours)", row=1, col=2)
        fig.update_xaxes(title_text="Time (hours)", row=2, col=1)
        fig.update_xaxes(title_text="Sample Curvature", row=2, col=2)
        fig.update_xaxes(title_text="Temperature (°C)", row=3, col=1)
        fig.update_xaxes(title_text="Time (hours)", row=3, col=2)
        
        fig.update_yaxes(title_text="Quality", row=1, col=1)
        fig.update_yaxes(title_text="Temperature (°C)", row=1, col=2)
        fig.update_yaxes(title_text="Reward", row=2, col=1)
        fig.update_yaxes(title_text="Action Magnitude", row=2, col=2)
        fig.update_yaxes(title_text="Strain", row=3, col=1)
        fig.update_yaxes(title_text="Density", row=3, col=2)
        
        # Save interactive dashboard
        fig.write_html(str(output_dir / "interactive_dashboard.html"))
    
    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        print("Generating validation report...")
        
        report = {
            'validation_summary': {
                'timestamp': datetime.now().isoformat(),
                'dataset_path': str(self.dataset_path),
                'validation_status': 'PASSED'  # Will be updated based on checks
            },
            'data_integrity': self.validation_results.get('integrity', {}),
            'recommendations': [],
            'warnings': [],
            'errors': []
        }
        
        # Check for issues and generate recommendations
        integrity = report['data_integrity']
        
        # Check for NaN values
        if integrity.get('nan_counts'):
            total_nans = sum(integrity['nan_counts'].values())
            if total_nans > 0:
                report['warnings'].append(f"Found {total_nans} NaN/infinite values in dataset")
                report['recommendations'].append("Consider data cleaning or imputation for NaN values")
        
        # Check sampling rates
        if integrity.get('sampling_rates'):
            dic_rate = integrity['sampling_rates'].get('dic_mean_hz', 0)
            furnace_rate = integrity['sampling_rates'].get('furnace_mean_hz', 0)
            
            if abs(dic_rate - 100) > 5:  # Expected 100 Hz
                report['warnings'].append(f"DIC sampling rate ({dic_rate:.1f} Hz) deviates from expected 100 Hz")
            
            if abs(furnace_rate - 10) > 1:  # Expected 10 Hz
                report['warnings'].append(f"Furnace sampling rate ({furnace_rate:.1f} Hz) deviates from expected 10 Hz")
        
        # Check physical plausibility
        if integrity.get('physical_checks'):
            for check_name, check_data in integrity['physical_checks'].items():
                if isinstance(check_data, dict) and not check_data.get('plausible', True):
                    report['errors'].append(f"Physical constraint violation in {check_name}")
                    report['validation_status'] = 'FAILED'
        
        # Generate recommendations based on data characteristics
        if len(self.rl_tuples) > 0:
            report['recommendations'].extend([
                "Dataset is ready for RL training",
                "Consider data augmentation for improved model robustness",
                "Implement cross-validation for model evaluation",
                "Monitor for data drift in real deployment"
            ])
        
        # Save validation report
        report_path = self.dataset_path / "validation_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Validation report saved to {report_path}")
        print(f"Validation Status: {report['validation_status']}")
        
        if report['warnings']:
            print("Warnings:")
            for warning in report['warnings']:
                print(f"  - {warning}")
        
        if report['errors']:
            print("Errors:")
            for error in report['errors']:
                print(f"  - {error}")
        
        return report

def main():
    """Main validation function"""
    dataset_path = "realtime_training_dataset"
    
    if not Path(dataset_path).exists():
        print(f"Dataset path {dataset_path} does not exist!")
        print("Please run the dataset generator first.")
        return
    
    print("=== Dataset Validation and Visualization ===")
    
    # Create validator
    validator = DatasetValidator(dataset_path)
    
    # Run validation
    validator.validate_data_integrity()
    
    # Create visualizations
    validator.create_comprehensive_visualizations()
    
    # Generate report
    validator.generate_validation_report()
    
    print("\n=== Validation Complete ===")
    print("Check the following outputs:")
    print("- visualizations/ folder for all plots")
    print("- validation_report.json for detailed validation results")
    print("- interactive_dashboard.html for interactive exploration")

if __name__ == "__main__":
    main()