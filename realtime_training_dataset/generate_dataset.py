#!/usr/bin/env python3
"""
Comprehensive Real-Time Training Dataset Generator
Generates realistic DIC, furnace control, and RL training data
"""

import numpy as np
import pandas as pd
import cv2
import json
import os
import h5py
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
from scipy import ndimage
from scipy.spatial.distance import cdist
import pickle

class RealTimeDatasetGenerator:
    def __init__(self, base_path: str = "/workspace/realtime_training_dataset"):
        self.base_path = base_path
        self.setup_directories()
        
        # Dataset parameters
        self.total_episodes = 1000
        self.episode_duration = 3600  # seconds (1 hour per episode)
        self.dic_fps = 100  # Hz
        self.furnace_fps = 10  # Hz
        self.rl_fps = 1  # Hz
        
        # Physical parameters
        self.sample_size = (50, 50)  # mm
        self.image_resolution = (2048, 2048)  # pixels
        self.num_cameras = 2
        self.num_heating_zones = 6
        self.num_thermocouples = 12
        
        # Process parameters
        self.max_temperature = 1200  # °C
        self.target_density = 0.95  # relative density
        self.thermal_diffusivity = 1e-6  # m²/s
        
    def setup_directories(self):
        """Create directory structure for the dataset"""
        dirs = [
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
            "utils/preprocessing"
        ]
        
        for dir_path in dirs:
            full_path = os.path.join(self.base_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
    
    def generate_speckle_pattern(self, size: Tuple[int, int]) -> np.ndarray:
        """Generate realistic speckle pattern for DIC"""
        # Base random pattern
        pattern = np.random.random(size)
        
        # Apply Gaussian filtering for realistic speckle size
        pattern = ndimage.gaussian_filter(pattern, sigma=2.0)
        
        # Enhance contrast
        pattern = (pattern - pattern.min()) / (pattern.max() - pattern.min())
        pattern = np.power(pattern, 0.7)  # Gamma correction
        
        # Convert to 8-bit
        return (pattern * 255).astype(np.uint8)
    
    def simulate_thermal_deformation(self, time_step: float, temperature_field: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Simulate thermal expansion and deformation"""
        # Thermal expansion coefficient (1/K)
        alpha = 12e-6
        
        # Reference temperature
        T_ref = 20  # °C
        
        # Calculate thermal strain
        thermal_strain = alpha * (temperature_field - T_ref)
        
        # Generate displacement field (simplified 2D)
        x, y = np.meshgrid(np.linspace(0, self.sample_size[0], self.image_resolution[0]),
                          np.linspace(0, self.sample_size[1], self.image_resolution[1]))
        
        # Displacement components (mm)
        u_displacement = thermal_strain * x * 0.001  # Convert to mm
        v_displacement = thermal_strain * y * 0.001
        w_displacement = np.zeros_like(u_displacement)  # Out-of-plane
        
        # Add sintering shrinkage
        shrinkage_factor = min(time_step / 3600.0, 1.0) * 0.15  # 15% max shrinkage
        u_displacement -= shrinkage_factor * x * 0.001
        v_displacement -= shrinkage_factor * y * 0.001
        
        # Calculate strain components
        du_dx = np.gradient(u_displacement, axis=1)
        du_dy = np.gradient(u_displacement, axis=0)
        dv_dx = np.gradient(v_displacement, axis=1)
        dv_dy = np.gradient(v_displacement, axis=0)
        
        strain_xx = du_dx
        strain_yy = dv_dy
        strain_xy = 0.5 * (du_dy + dv_dx)
        
        displacement = np.stack([u_displacement, v_displacement, w_displacement], axis=2)
        strain = np.stack([strain_xx, strain_yy, strain_xy], axis=2)
        
        return displacement, strain
    
    def generate_temperature_field(self, time_step: float, zone_powers: np.ndarray) -> np.ndarray:
        """Generate realistic temperature field based on heating zones"""
        # Create heating zone layout (6 zones in 2x3 grid)
        zone_centers = np.array([
            [12.5, 12.5], [37.5, 12.5],  # Top row
            [12.5, 25.0], [37.5, 25.0],  # Middle row
            [12.5, 37.5], [37.5, 37.5]   # Bottom row
        ])
        
        # Create coordinate grid
        x, y = np.meshgrid(np.linspace(0, 50, 100), np.linspace(0, 50, 100))
        coords = np.stack([x.flatten(), y.flatten()], axis=1)
        
        # Calculate temperature field
        temperature_field = np.zeros((100, 100))
        
        for i, (center, power) in enumerate(zip(zone_centers, zone_powers)):
            # Distance from zone center
            distances = cdist(coords, center.reshape(1, -1)).flatten()
            
            # Gaussian heating profile
            heating_profile = power * np.exp(-distances**2 / (2 * 8**2))  # 8mm std dev
            temperature_field += heating_profile.reshape(100, 100)
        
        # Add ambient temperature
        temperature_field += 20  # °C
        
        # Apply thermal diffusion (simplified)
        if time_step > 0:
            temperature_field = ndimage.gaussian_filter(temperature_field, sigma=1.0)
        
        return temperature_field
    
    def generate_dic_frame(self, episode: int, frame: int, displacement: np.ndarray) -> np.ndarray:
        """Generate DIC video frame with applied displacement"""
        # Load or generate base speckle pattern
        base_pattern = self.generate_speckle_pattern(self.image_resolution)
        
        # Apply displacement to create deformed image
        x, y = np.meshgrid(np.arange(self.image_resolution[1]), 
                          np.arange(self.image_resolution[0]))
        
        # Scale displacement to pixel coordinates
        scale_x = self.image_resolution[1] / self.sample_size[0]
        scale_y = self.image_resolution[0] / self.sample_size[1]
        
        # Interpolate displacement to image resolution
        disp_x = cv2.resize(displacement[:, :, 0], self.image_resolution) * scale_x
        disp_y = cv2.resize(displacement[:, :, 1], self.image_resolution) * scale_y
        
        # Apply displacement
        x_deformed = x + disp_x
        y_deformed = y + disp_y
        
        # Interpolate deformed pattern
        deformed_pattern = cv2.remap(base_pattern, 
                                   x_deformed.astype(np.float32), 
                                   y_deformed.astype(np.float32), 
                                   cv2.INTER_LINEAR)
        
        # Add noise
        noise = np.random.normal(0, 2, self.image_resolution).astype(np.uint8)
        deformed_pattern = np.clip(deformed_pattern.astype(int) + noise, 0, 255).astype(np.uint8)
        
        return deformed_pattern
    
    def calculate_reward(self, state: Dict, action: np.ndarray, next_state: Dict) -> float:
        """Calculate multi-objective reward for RL training"""
        # Extract key metrics
        max_strain = next_state['max_principal_strain']
        strain_heterogeneity = next_state['strain_std']
        warpage_rate = abs(next_state['sample_curvature'])
        density_error = abs(self.target_density - next_state['current_density'])
        
        # Temperature uniformity
        temp_std = next_state['temperature_std']
        
        # Multi-objective reward weights
        w1 = 1.0    # Warpage penalty
        w2 = 0.8    # Strain penalty
        w3 = 1.2    # Density error penalty
        w4 = 0.6    # Temperature uniformity penalty
        w5 = 0.1    # Energy efficiency bonus
        
        # Calculate reward components
        warpage_penalty = w1 * warpage_rate
        strain_penalty = w2 * (max_strain + strain_heterogeneity)
        density_penalty = w3 * density_error**2
        temp_penalty = w4 * temp_std
        energy_bonus = w5 * (1.0 - np.mean(action) / 100.0)  # Encourage efficiency
        
        # Total reward (higher is better)
        reward = 100.0 - (warpage_penalty + strain_penalty + density_penalty + temp_penalty) + energy_bonus
        
        return reward
    
    def generate_episode_data(self, episode: int) -> Dict:
        """Generate complete data for one episode"""
        print(f"Generating episode {episode + 1}/{self.total_episodes}")
        
        # Episode parameters
        frames_per_episode = self.episode_duration * self.dic_fps
        furnace_samples = self.episode_duration * self.furnace_fps
        rl_samples = self.episode_duration * self.rl_fps
        
        # Initialize data structures
        episode_data = {
            'episode_id': episode,
            'duration': self.episode_duration,
            'dic_data': {
                'timestamps': [],
                'displacement_fields': [],
                'strain_fields': [],
                'video_frames': []
            },
            'furnace_data': {
                'timestamps': [],
                'zone_powers': [],
                'temperatures': [],
                'gas_readings': []
            },
            'rl_data': {
                'states': [],
                'actions': [],
                'rewards': [],
                'next_states': []
            }
        }
        
        # Time vectors
        dic_times = np.linspace(0, self.episode_duration, frames_per_episode)
        furnace_times = np.linspace(0, self.episode_duration, furnace_samples)
        rl_times = np.linspace(0, self.episode_duration, rl_samples)
        
        # Initialize process state
        current_density = 0.6  # Starting relative density
        zone_powers = np.random.uniform(20, 80, self.num_heating_zones)  # Initial powers
        
        # Generate RL trajectory first (lowest frequency)
        for rl_idx, t in enumerate(rl_times):
            # Current state
            temperature_field = self.generate_temperature_field(t, zone_powers)
            displacement, strain = self.simulate_thermal_deformation(t, temperature_field)
            
            # State metrics
            max_strain = np.max(np.sqrt(strain[:, :, 0]**2 + strain[:, :, 1]**2))
            strain_std = np.std(strain)
            sample_curvature = np.mean(np.gradient(np.gradient(displacement[:, :, 2])))
            temp_std = np.std(temperature_field)
            
            # Update density (simplified sintering model)
            density_rate = 0.1 * np.exp(-5000 / (np.mean(temperature_field) + 273.15))
            current_density = min(0.99, current_density + density_rate / 3600.0)
            
            state = {
                'max_principal_strain': max_strain,
                'strain_std': strain_std,
                'sample_curvature': sample_curvature,
                'temperature_std': temp_std,
                'current_density': current_density,
                'mean_temperature': np.mean(temperature_field),
                'time_in_cycle': t / self.episode_duration
            }
            
            # Generate action (RL agent decision)
            if rl_idx < len(rl_times) - 1:
                # Simple control policy for data generation
                action = np.random.normal(0, 5, self.num_heating_zones)  # Power adjustments
                action = np.clip(action, -20, 20)  # Limit adjustment range
                
                # Apply action
                zone_powers = np.clip(zone_powers + action, 0, 100)
                
                # Calculate next state
                next_temp_field = self.generate_temperature_field(rl_times[rl_idx + 1], zone_powers)
                next_displacement, next_strain = self.simulate_thermal_deformation(rl_times[rl_idx + 1], next_temp_field)
                
                next_max_strain = np.max(np.sqrt(next_strain[:, :, 0]**2 + next_strain[:, :, 1]**2))
                next_strain_std = np.std(next_strain)
                next_curvature = np.mean(np.gradient(np.gradient(next_displacement[:, :, 2])))
                next_temp_std = np.std(next_temp_field)
                next_density = min(0.99, current_density + density_rate / 3600.0)
                
                next_state = {
                    'max_principal_strain': next_max_strain,
                    'strain_std': next_strain_std,
                    'sample_curvature': next_curvature,
                    'temperature_std': next_temp_std,
                    'current_density': next_density,
                    'mean_temperature': np.mean(next_temp_field),
                    'time_in_cycle': rl_times[rl_idx + 1] / self.episode_duration
                }
                
                # Calculate reward
                reward = self.calculate_reward(state, action, next_state)
                
                # Store RL data
                episode_data['rl_data']['states'].append(state)
                episode_data['rl_data']['actions'].append(action)
                episode_data['rl_data']['rewards'].append(reward)
                episode_data['rl_data']['next_states'].append(next_state)
        
        # Generate high-frequency DIC and furnace data
        # (Subsample from RL trajectory for consistency)
        for frame_idx, t in enumerate(dic_times[::100]):  # Every 100th frame for storage
            # Interpolate zone powers at this time
            rl_idx = int(t * self.rl_fps)
            if rl_idx < len(zone_powers):
                temp_field = self.generate_temperature_field(t, zone_powers)
                displacement, strain = self.simulate_thermal_deformation(t, temp_field)
                
                # Generate DIC frame
                dic_frame = self.generate_dic_frame(episode, frame_idx, displacement)
                
                # Store DIC data
                episode_data['dic_data']['timestamps'].append(t)
                episode_data['dic_data']['displacement_fields'].append(displacement)
                episode_data['dic_data']['strain_fields'].append(strain)
                episode_data['dic_data']['video_frames'].append(dic_frame)
        
        # Generate furnace control data
        for furnace_idx, t in enumerate(furnace_times[::10]):  # Every 10th sample
            # Interpolate zone powers
            rl_idx = min(int(t * self.rl_fps), len(zone_powers) - 1)
            
            # Temperature readings with noise
            temp_field = self.generate_temperature_field(t, zone_powers)
            thermocouple_temps = []
            for i in range(self.num_thermocouples):
                # Random thermocouple positions
                x_pos = np.random.randint(0, temp_field.shape[1])
                y_pos = np.random.randint(0, temp_field.shape[0])
                temp = temp_field[y_pos, x_pos] + np.random.normal(0, 2)  # 2°C noise
                thermocouple_temps.append(temp)
            
            # Gas atmosphere readings
            gas_readings = {
                'oxygen_ppm': np.random.uniform(0.1, 1.0),
                'moisture_ppm': np.random.uniform(10, 50),
                'pressure_pa': np.random.normal(101325, 100)
            }
            
            # Store furnace data
            episode_data['furnace_data']['timestamps'].append(t)
            episode_data['furnace_data']['zone_powers'].append(zone_powers.copy())
            episode_data['furnace_data']['temperatures'].append(thermocouple_temps)
            episode_data['furnace_data']['gas_readings'].append(gas_readings)
        
        return episode_data
    
    def save_episode_data(self, episode_data: Dict, episode: int):
        """Save episode data to disk in multiple formats"""
        episode_dir = os.path.join(self.base_path, f"episode_{episode:04d}")
        os.makedirs(episode_dir, exist_ok=True)
        
        # Save DIC data
        dic_file = os.path.join(episode_dir, "dic_data.h5")
        with h5py.File(dic_file, 'w') as f:
            f.create_dataset('timestamps', data=episode_data['dic_data']['timestamps'])
            f.create_dataset('displacement_fields', 
                           data=np.array(episode_data['dic_data']['displacement_fields']))
            f.create_dataset('strain_fields', 
                           data=np.array(episode_data['dic_data']['strain_fields']))
            
            # Save video frames
            video_group = f.create_group('video_frames')
            for i, frame in enumerate(episode_data['dic_data']['video_frames']):
                video_group.create_dataset(f'frame_{i:06d}', data=frame)
        
        # Save furnace data
        furnace_df = pd.DataFrame({
            'timestamp': episode_data['furnace_data']['timestamps'],
            'zone_powers': episode_data['furnace_data']['zone_powers'],
            'temperatures': episode_data['furnace_data']['temperatures'],
            'gas_readings': episode_data['furnace_data']['gas_readings']
        })
        furnace_df.to_parquet(os.path.join(episode_dir, "furnace_data.parquet"))
        
        # Save RL data
        rl_file = os.path.join(episode_dir, "rl_data.pkl")
        with open(rl_file, 'wb') as f:
            pickle.dump(episode_data['rl_data'], f)
        
        # Save metadata
        metadata = {
            'episode_id': episode,
            'duration': episode_data['duration'],
            'dic_samples': len(episode_data['dic_data']['timestamps']),
            'furnace_samples': len(episode_data['furnace_data']['timestamps']),
            'rl_samples': len(episode_data['rl_data']['states']),
            'generation_time': datetime.now().isoformat()
        }
        
        with open(os.path.join(episode_dir, "metadata.json"), 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def generate_complete_dataset(self):
        """Generate the complete dataset"""
        print(f"Starting generation of {self.total_episodes} episodes...")
        print(f"Dataset will be saved to: {self.base_path}")
        
        # Generate episodes
        for episode in range(self.total_episodes):
            episode_data = self.generate_episode_data(episode)
            self.save_episode_data(episode_data, episode)
            
            if (episode + 1) % 50 == 0:
                print(f"Completed {episode + 1} episodes")
        
        # Generate dataset summary
        self.generate_dataset_summary()
        print("Dataset generation complete!")
    
    def generate_dataset_summary(self):
        """Generate summary statistics and documentation"""
        summary = {
            'dataset_info': {
                'total_episodes': self.total_episodes,
                'episode_duration': self.episode_duration,
                'total_duration_hours': self.total_episodes * self.episode_duration / 3600,
                'dic_fps': self.dic_fps,
                'furnace_fps': self.furnace_fps,
                'rl_fps': self.rl_fps
            },
            'physical_parameters': {
                'sample_size_mm': self.sample_size,
                'image_resolution': self.image_resolution,
                'num_cameras': self.num_cameras,
                'num_heating_zones': self.num_heating_zones,
                'num_thermocouples': self.num_thermocouples,
                'max_temperature_c': self.max_temperature,
                'target_density': self.target_density
            },
            'data_volumes': {
                'estimated_total_size_gb': 50,
                'dic_data_gb': 35,
                'furnace_data_gb': 10,
                'rl_data_gb': 5
            },
            'generation_info': {
                'generated_on': datetime.now().isoformat(),
                'generator_version': '1.0.0'
            }
        }
        
        with open(os.path.join(self.base_path, "dataset_summary.json"), 'w') as f:
            json.dump(summary, f, indent=2)

if __name__ == "__main__":
    generator = RealTimeDatasetGenerator()
    generator.generate_complete_dataset()