#!/usr/bin/env python3
"""
Real-Time Training & Validation Dataset Generator
Phase 2: Core Real-Time Training & Validation Data

This module generates comprehensive datasets for:
1. High-frequency DIC video streams with speckle patterns
2. Synchronized furnace control and sensor data
3. Real-time displacement and strain computation
4. RL training tuples (state-action-reward-next_state)
5. Multi-objective optimization rewards

Author: AI Assistant
Date: 2024
"""

import numpy as np
import cv2
import h5py
import pandas as pd
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import os
import json
from scipy import ndimage, interpolate
from scipy.spatial.distance import cdist
from skimage import filters, morphology, measure
import matplotlib.pyplot as plt
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

class DICVideoGenerator:
    """Generates high-resolution, high-frame-rate DIC video data with realistic speckle patterns."""
    
    def __init__(self, width=1920, height=1080, fps=120, duration=3600):
        self.width = width
        self.height = height
        self.fps = fps
        self.duration = duration
        self.total_frames = int(fps * duration)
        
    def generate_speckle_pattern(self, base_intensity=128, speckle_density=0.3, 
                                speckle_size_range=(2, 8), temperature_factor=1.0):
        """Generate realistic speckle pattern for high-temperature DIC."""
        # Base pattern with random speckles
        pattern = np.random.poisson(base_intensity, (self.height, self.width))
        
        # Add speckles with size distribution
        num_speckles = int(self.width * self.height * speckle_density)
        for _ in range(num_speckles):
            y = np.random.randint(0, self.height)
            x = np.random.randint(0, self.width)
            size = np.random.randint(*speckle_size_range)
            
            # Create circular speckle
            y_coords, x_coords = np.ogrid[:self.height, :self.width]
            mask = (x_coords - x)**2 + (y_coords - y)**2 <= size**2
            pattern[mask] = np.random.poisson(255 * temperature_factor)
        
        # Add thermal noise and blur
        pattern = ndimage.gaussian_filter(pattern, sigma=0.5)
        pattern = np.clip(pattern + np.random.normal(0, 5, pattern.shape), 0, 255)
        
        return pattern.astype(np.uint8)
    
    def simulate_thermal_deformation(self, base_pattern, frame_idx, temperature_profile, 
                                   material_properties):
        """Simulate realistic thermal deformation of the sample."""
        # Get current temperature
        current_temp = temperature_profile[frame_idx]
        
        # Calculate thermal expansion coefficient based on temperature
        alpha = material_properties['thermal_expansion_base'] * (1 + 
                current_temp / material_properties['thermal_expansion_temp_factor'])
        
        # Simulate non-uniform heating (hotter in center, cooler at edges)
        y_coords, x_coords = np.ogrid[:self.height, :self.width]
        center_y, center_x = self.height // 2, self.width // 2
        
        # Distance from center
        r = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)
        max_r = np.sqrt(center_x**2 + center_y**2)
        
        # Temperature gradient (hotter in center)
        temp_gradient = 1.0 - 0.3 * (r / max_r)
        local_temp = current_temp * temp_gradient
        
        # Calculate displacement field
        displacement_scale = alpha * (local_temp - 20) * 1e-6  # 20°C reference
        
        # Add some realistic warping patterns
        warp_x = displacement_scale * np.sin(2 * np.pi * x_coords / 200) * 0.1
        warp_y = displacement_scale * np.cos(2 * np.pi * y_coords / 200) * 0.1
        
        # Create displacement field
        u_field = warp_x * 10  # Scale to pixels
        v_field = warp_y * 10
        
        # Apply displacement to pattern
        deformed_pattern = self.apply_displacement(base_pattern, u_field, v_field)
        
        return deformed_pattern, u_field, v_field
    
    def apply_displacement(self, image, u_field, v_field):
        """Apply displacement field to image using sub-pixel interpolation."""
        height, width = image.shape
        y_coords, x_coords = np.mgrid[0:height, 0:width]
        
        # Calculate new coordinates
        new_x = x_coords + u_field
        new_y = y_coords + v_field
        
        # Ensure coordinates are within bounds
        new_x = np.clip(new_x, 0, width - 1)
        new_y = np.clip(new_y, 0, height - 1)
        
        # Interpolate
        from scipy.interpolate import griddata
        points = np.column_stack((y_coords.ravel(), x_coords.ravel()))
        values = image.ravel()
        new_points = np.column_stack((new_y.ravel(), new_x.ravel()))
        
        deformed = griddata(points, values, new_points, method='linear', fill_value=0)
        return deformed.reshape(image.shape).astype(np.uint8)
    
    def generate_video_sequence(self, temperature_profile, material_properties, 
                              output_path="dic_video.mp4"):
        """Generate complete DIC video sequence."""
        print(f"Generating DIC video: {self.total_frames} frames at {self.fps} FPS")
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height), isColor=False)
        
        # Generate base speckle pattern
        base_pattern = self.generate_speckle_pattern()
        
        # Store displacement data for later analysis
        displacement_data = []
        
        for frame_idx in tqdm(range(self.total_frames), desc="Generating DIC frames"):
            # Simulate thermal deformation
            deformed_frame, u_field, v_field = self.simulate_thermal_deformation(
                base_pattern, frame_idx, temperature_profile, material_properties
            )
            
            # Add some realistic camera noise
            noise = np.random.normal(0, 2, deformed_frame.shape)
            deformed_frame = np.clip(deformed_frame + noise, 0, 255).astype(np.uint8)
            
            # Write frame
            out.write(deformed_frame)
            
            # Store displacement data
            displacement_data.append({
                'frame': frame_idx,
                'timestamp': frame_idx / self.fps,
                'u_field': u_field,
                'v_field': v_field
            })
        
        out.release()
        
        # Save displacement data
        np.save(output_path.replace('.mp4', '_displacement.npy'), displacement_data)
        
        print(f"DIC video saved to: {output_path}")
        return displacement_data

class FurnaceController:
    """Simulates realistic furnace control and sensor data."""
    
    def __init__(self, num_zones=6, num_thermocouples=12):
        self.num_zones = num_zones
        self.num_thermocouples = num_thermocouples
        self.zone_powers = np.zeros(num_zones)
        self.zone_setpoints = np.zeros(num_zones)
        self.thermocouple_temps = np.zeros(num_thermocouples)
        
        # Furnace characteristics
        self.thermal_mass = np.random.uniform(0.8, 1.2, num_zones)
        self.heat_transfer_coeff = np.random.uniform(0.1, 0.3, num_zones)
        self.ambient_temp = 25.0
        
        # Control parameters
        self.max_power = 100.0  # kW
        self.temp_ramp_rate = 5.0  # °C/min
        self.control_dt = 1.0  # seconds
        
    def update_zone_power(self, zone_idx, power_percent):
        """Update power for specific zone."""
        self.zone_powers[zone_idx] = np.clip(power_percent, 0, 100)
    
    def set_zone_temperature(self, zone_idx, target_temp):
        """Set target temperature for zone."""
        self.zone_setpoints[zone_idx] = target_temp
    
    def simulate_thermal_response(self, dt):
        """Simulate thermal response of furnace zones."""
        for zone in range(self.num_zones):
            # Calculate power input
            power_input = self.zone_powers[zone] * self.max_power / 100.0
            
            # Calculate temperature change
            temp_diff = self.zone_setpoints[zone] - self.thermocouple_temps[zone]
            power_required = temp_diff * self.heat_transfer_coeff[zone]
            
            # Update temperature
            temp_change = (power_input - power_required) / self.thermal_mass[zone] * dt
            self.thermocouple_temps[zone] += temp_change
            
            # Add some realistic noise
            noise = np.random.normal(0, 0.5)
            self.thermocouple_temps[zone] += noise
    
    def generate_control_sequence(self, duration, control_strategy='sintering_cycle'):
        """Generate realistic control sequence for sintering cycle."""
        timesteps = int(duration)
        control_data = []
        
        if control_strategy == 'sintering_cycle':
            # Typical ceramic sintering cycle
            phases = [
                {'name': 'heating', 'duration': 0.3, 'temp_range': (25, 800)},
                {'name': 'soak_1', 'duration': 0.1, 'temp_range': (800, 800)},
                {'name': 'heating_2', 'duration': 0.2, 'temp_range': (800, 1400)},
                {'name': 'soak_2', 'duration': 0.2, 'temp_range': (1400, 1400)},
                {'name': 'cooling', 'duration': 0.2, 'temp_range': (1400, 25)}
            ]
        else:
            # Random control for exploration
            phases = [{'name': 'random', 'duration': 1.0, 'temp_range': (25, 1500)}]
        
        current_time = 0
        for phase in phases:
            phase_duration = int(phase['duration'] * duration)
            temp_start, temp_end = phase['temp_range']
            
            for t in range(phase_duration):
                if current_time >= timesteps:
                    break
                    
                # Calculate target temperature
                if phase['name'] == 'random':
                    target_temp = np.random.uniform(25, 1500)
                else:
                    progress = t / phase_duration
                    target_temp = temp_start + (temp_end - temp_start) * progress
                
                # Set all zones to target temperature
                for zone in range(self.num_zones):
                    self.set_zone_temperature(zone, target_temp)
                    # Add some zone-to-zone variation
                    variation = np.random.normal(0, 10)
                    self.zone_setpoints[zone] += variation
                
                # Calculate required power for each zone
                for zone in range(self.num_zones):
                    temp_diff = self.zone_setpoints[zone] - self.thermocouple_temps[zone]
                    power_percent = np.clip(temp_diff * 0.1, 0, 100)
                    self.update_zone_power(zone, power_percent)
                
                # Simulate thermal response
                self.simulate_thermal_response(self.control_dt)
                
                # Record data
                control_data.append({
                    'timestamp': current_time,
                    'zone_powers': self.zone_powers.copy(),
                    'zone_setpoints': self.zone_setpoints.copy(),
                    'thermocouple_temps': self.thermocouple_temps.copy(),
                    'atmospheric_pressure': np.random.uniform(0.95, 1.05),
                    'oxygen_content': np.random.uniform(18, 21),
                    'gas_flow_rate': np.random.uniform(5, 15)
                })
                
                current_time += 1
        
        return control_data

class StrainAnalyzer:
    """Computes real-time displacement and strain fields from DIC data."""
    
    def __init__(self, subset_size=32, step_size=16):
        self.subset_size = subset_size
        self.step_size = step_size
        
    def compute_displacement_field(self, ref_image, def_image, method='correlation'):
        """Compute displacement field between reference and deformed images."""
        height, width = ref_image.shape
        u_field = np.zeros((height, width))
        v_field = np.zeros((height, width))
        
        # Sample points for DIC analysis
        y_points = range(0, height - self.subset_size, self.step_size)
        x_points = range(0, width - self.subset_size, self.step_size)
        
        for y in y_points:
            for x in x_points:
                # Extract subset
                ref_subset = ref_image[y:y+self.subset_size, x:x+self.subset_size]
                def_subset = def_image[y:y+self.subset_size, x:x+self.subset_size]
                
                # Compute displacement using normalized cross-correlation
                result = cv2.matchTemplate(def_subset, ref_subset, cv2.TM_CCOEFF_NORMED)
                _, _, _, max_loc = cv2.minMaxLoc(result)
                
                # Calculate displacement
                u = max_loc[0] - x
                v = max_loc[1] - y
                
                # Fill displacement field
                u_field[y:y+self.step_size, x:x+self.step_size] = u
                v_field[y:y+self.step_size, x:x+self.step_size] = v
        
        return u_field, v_field
    
    def compute_strain_field(self, u_field, v_field, subset_size=32):
        """Compute strain field from displacement field."""
        # Compute gradients
        du_dx = np.gradient(u_field, axis=1)
        du_dy = np.gradient(u_field, axis=0)
        dv_dx = np.gradient(v_field, axis=1)
        dv_dy = np.gradient(v_field, axis=0)
        
        # Compute strain components
        exx = du_dx
        eyy = dv_dy
        exy = 0.5 * (du_dy + dv_dx)
        
        # Compute principal strains
        e1 = 0.5 * (exx + eyy) + 0.5 * np.sqrt((exx - eyy)**2 + 4 * exy**2)
        e2 = 0.5 * (exx + eyy) - 0.5 * np.sqrt((exx - eyy)**2 + 4 * exy**2)
        
        # Compute von Mises equivalent strain
        e_vm = np.sqrt(0.5 * ((e1 - e2)**2 + e1**2 + e2**2))
        
        return {
            'exx': exx,
            'eyy': eyy,
            'exy': exy,
            'e1': e1,
            'e2': e2,
            'e_vm': e_vm
        }
    
    def compute_curvature(self, u_field, v_field):
        """Compute sample curvature from displacement field."""
        # Compute second derivatives
        d2u_dx2 = np.gradient(np.gradient(u_field, axis=1), axis=1)
        d2v_dy2 = np.gradient(np.gradient(v_field, axis=0), axis=0)
        
        # Curvature approximation
        curvature = np.sqrt(d2u_dx2**2 + d2v_dy2**2)
        
        return curvature

class RLStateRepresentation:
    """Creates state representation for RL agent from fused sensor data."""
    
    def __init__(self, state_dim=50):
        self.state_dim = state_dim
        self.feature_names = []
        
    def extract_dic_features(self, strain_data, displacement_data):
        """Extract key features from DIC data."""
        features = {}
        
        # Strain statistics
        features['max_principal_strain'] = np.max(strain_data['e1'])
        features['min_principal_strain'] = np.min(strain_data['e2'])
        features['max_von_mises_strain'] = np.max(strain_data['e_vm'])
        features['mean_von_mises_strain'] = np.mean(strain_data['e_vm'])
        features['strain_std'] = np.std(strain_data['e_vm'])
        features['strain_heterogeneity'] = np.std(strain_data['e_vm']) / (np.mean(strain_data['e_vm']) + 1e-6)
        
        # Displacement statistics
        u_field, v_field = displacement_data['u_field'], displacement_data['v_field']
        features['max_displacement'] = np.max(np.sqrt(u_field**2 + v_field**2))
        features['mean_displacement'] = np.mean(np.sqrt(u_field**2 + v_field**2))
        features['displacement_std'] = np.std(np.sqrt(u_field**2 + v_field**2))
        
        return features
    
    def extract_thermal_features(self, furnace_data):
        """Extract thermal features from furnace data."""
        features = {}
        
        # Temperature statistics
        temps = furnace_data['thermocouple_temps']
        features['max_temperature'] = np.max(temps)
        features['min_temperature'] = np.min(temps)
        features['mean_temperature'] = np.mean(temps)
        features['temp_std'] = np.std(temps)
        features['temp_gradient'] = np.max(temps) - np.min(temps)
        
        # Power statistics
        powers = furnace_data['zone_powers']
        features['total_power'] = np.sum(powers)
        features['power_std'] = np.std(powers)
        features['power_efficiency'] = np.sum(powers) / (np.max(temps) + 1e-6)
        
        return features
    
    def extract_process_features(self, timestamp, cycle_duration):
        """Extract process-related features."""
        features = {}
        
        # Time-based features
        features['cycle_progress'] = timestamp / cycle_duration
        features['time_since_start'] = timestamp
        
        # Estimated density (simplified model)
        # This would be replaced with actual real-time density estimation
        features['estimated_density'] = 0.6 + 0.4 * (timestamp / cycle_duration)
        
        return features
    
    def create_state_vector(self, dic_features, thermal_features, process_features):
        """Create normalized state vector for RL agent."""
        # Combine all features
        all_features = {**dic_features, **thermal_features, **process_features}
        
        # Convert to array and normalize
        feature_values = list(all_features.values())
        feature_array = np.array(feature_values, dtype=np.float32)
        
        # Simple normalization (in practice, use proper scaling)
        feature_array = (feature_array - np.mean(feature_array)) / (np.std(feature_array) + 1e-6)
        
        # Pad or truncate to state_dim
        if len(feature_array) < self.state_dim:
            feature_array = np.pad(feature_array, (0, self.state_dim - len(feature_array)))
        else:
            feature_array = feature_array[:self.state_dim]
        
        return feature_array

class RewardFunction:
    """Multi-objective reward function for RL training."""
    
    def __init__(self, weights={'warpage': 1.0, 'strain': 0.5, 'density': 0.3}):
        self.weights = weights
        self.target_density = 0.95
        
    def compute_reward(self, state, action, next_state, strain_data, displacement_data):
        """Compute multi-objective reward."""
        rewards = {}
        
        # Warpage penalty (based on curvature)
        curvature = self._compute_curvature(displacement_data)
        warpage_rate = np.mean(curvature)
        rewards['warpage'] = -self.weights['warpage'] * warpage_rate
        
        # Strain penalty
        max_strain = np.max(strain_data['e_vm'])
        rewards['strain'] = -self.weights['strain'] * max_strain
        
        # Density reward
        current_density = state[0] if len(state) > 0 else 0.5  # Assuming density is first feature
        density_error = (self.target_density - current_density) ** 2
        rewards['density'] = -self.weights['density'] * density_error
        
        # Total reward
        total_reward = sum(rewards.values())
        
        return total_reward, rewards
    
    def _compute_curvature(self, displacement_data):
        """Compute sample curvature."""
        u_field = displacement_data['u_field']
        v_field = displacement_data['v_field']
        
        # Simple curvature approximation
        d2u_dx2 = np.gradient(np.gradient(u_field, axis=1), axis=1)
        d2v_dy2 = np.gradient(np.gradient(v_field, axis=0), axis=0)
        
        curvature = np.sqrt(d2u_dx2**2 + d2v_dy2**2)
        return curvature

class DatasetGenerator:
    """Main class for generating comprehensive training dataset."""
    
    def __init__(self, config_path=None):
        if isinstance(config_path, dict):
            # If config_path is a dict, use it directly
            self.config = config_path
        else:
            # Otherwise, load from file
            self.config = self._load_config(config_path)
        
        self.dic_generator = DICVideoGenerator(**self.config['dic'])
        self.furnace_controller = FurnaceController(**self.config['furnace'])
        self.strain_analyzer = StrainAnalyzer(**self.config['strain'])
        self.state_representation = RLStateRepresentation(**self.config['rl_state'])
        self.reward_function = RewardFunction(**self.config['reward'])
        
    def _load_config(self, config_path):
        """Load configuration or use defaults."""
        default_config = {
            'dic': {
                'width': 1920,
                'height': 1080,
                'fps': 120,
                'duration': 3600
            },
            'furnace': {
                'num_zones': 6,
                'num_thermocouples': 12
            },
            'strain': {
                'subset_size': 32,
                'step_size': 16
            },
            'rl_state': {
                'state_dim': 50
            },
            'reward': {
                'weights': {'warpage': 1.0, 'strain': 0.5, 'density': 0.3}
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        
        return default_config
    
    def generate_complete_dataset(self, output_dir="dataset", num_episodes=100):
        """Generate complete training dataset."""
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Generating {num_episodes} episodes of training data...")
        
        # Material properties for realistic simulation
        material_properties = {
            'thermal_expansion_base': 8e-6,
            'thermal_expansion_temp_factor': 1000,
            'youngs_modulus': 200e9,
            'poisson_ratio': 0.3
        }
        
        all_episodes = []
        
        for episode in tqdm(range(num_episodes), desc="Generating episodes"):
            # Generate furnace control sequence
            control_data = self.furnace_controller.generate_control_sequence(
                duration=self.config['dic']['duration'],
                control_strategy='sintering_cycle'
            )
            
            # Extract temperature profile
            temperature_profile = [data['thermocouple_temps'].mean() for data in control_data]
            
            # Generate DIC video and displacement data
            displacement_data = self.dic_generator.generate_video_sequence(
                temperature_profile, material_properties,
                output_path=os.path.join(output_dir, f"episode_{episode:03d}_dic.mp4")
            )
            
            # Process each timestep
            episode_data = []
            for t, (control, disp) in enumerate(zip(control_data, displacement_data)):
                # Compute strain field
                if t == 0:
                    # Use first frame as reference
                    ref_image = self.dic_generator.generate_speckle_pattern()
                else:
                    # Use previous frame as reference
                    ref_image = prev_image
                
                def_image = self.dic_generator.generate_speckle_pattern()
                u_field, v_field = self.strain_analyzer.compute_displacement_field(
                    ref_image, def_image
                )
                
                strain_data = self.strain_analyzer.compute_strain_field(u_field, v_field)
                
                # Create state representation
                dic_features = self.state_representation.extract_dic_features(
                    strain_data, {'u_field': u_field, 'v_field': v_field}
                )
                thermal_features = self.state_representation.extract_thermal_features(control)
                process_features = self.state_representation.extract_process_features(
                    t, len(control_data)
                )
                
                state = self.state_representation.create_state_vector(
                    dic_features, thermal_features, process_features
                )
                
                # Create action (change in furnace parameters)
                if t == 0:
                    action = np.zeros(self.furnace_controller.num_zones)
                else:
                    prev_powers = control_data[t-1]['zone_powers']
                    current_powers = control['zone_powers']
                    action = current_powers - prev_powers
                
                # Compute reward
                reward, reward_components = self.reward_function.compute_reward(
                    state, action, state, strain_data, {'u_field': u_field, 'v_field': v_field}
                )
                
                # Store timestep data
                timestep_data = {
                    'episode': episode,
                    'timestep': t,
                    'timestamp': control['timestamp'],
                    'state': state,
                    'action': action,
                    'reward': reward,
                    'reward_components': reward_components,
                    'control_data': control,
                    'strain_data': strain_data,
                    'displacement_data': {'u_field': u_field, 'v_field': v_field},
                    'dic_features': dic_features,
                    'thermal_features': thermal_features,
                    'process_features': process_features
                }
                
                episode_data.append(timestep_data)
                prev_image = def_image
            
            all_episodes.extend(episode_data)
        
        # Save complete dataset
        self._save_dataset(all_episodes, output_dir)
        
        print(f"Dataset generation complete! Saved to {output_dir}")
        return all_episodes
    
    def generate_single_episode(self, episode_id, duration, material_type='alumina', visualize=False):
        """Generate a single episode for testing."""
        # Create temporary config for single episode
        temp_config = self.config.copy()
        temp_config['dic']['duration'] = duration
        
        # Generate furnace control sequence
        control_data = self.furnace_controller.generate_control_sequence(
            duration=duration,
            control_strategy='sintering_cycle'
        )
        
        # Extract temperature profile
        temperature_profile = [data['thermocouple_temps'].mean() for data in control_data]
        
        # Material properties
        material_properties = {
            'thermal_expansion_base': 8e-6,
            'thermal_expansion_temp_factor': 1000,
            'youngs_modulus': 200e9,
            'poisson_ratio': 0.3
        }
        
        # Process each timestep
        episode_data = []
        for t, control in enumerate(control_data):
            # Generate simple displacement data for testing
            u_field = np.random.randn(100, 100) * 0.1
            v_field = np.random.randn(100, 100) * 0.1
            
            strain_data = self.strain_analyzer.compute_strain_field(u_field, v_field)
            
            # Create state representation
            dic_features = self.state_representation.extract_dic_features(
                strain_data, {'u_field': u_field, 'v_field': v_field}
            )
            thermal_features = self.state_representation.extract_thermal_features(control)
            process_features = self.state_representation.extract_process_features(
                t, len(control_data)
            )
            
            state = self.state_representation.create_state_vector(
                dic_features, thermal_features, process_features
            )
            
            # Create action
            if t == 0:
                action = np.zeros(self.furnace_controller.num_zones)
            else:
                prev_powers = control_data[t-1]['zone_powers']
                current_powers = control['zone_powers']
                action = current_powers - prev_powers
            
            # Compute reward
            reward, reward_components = self.reward_function.compute_reward(
                state, action, state, strain_data, {'u_field': u_field, 'v_field': v_field}
            )
            
            # Store timestep data
            timestep_data = {
                'episode': episode_id,
                'timestep': t,
                'timestamp': control['timestamp'],
                'state': state,
                'action': action,
                'reward': reward,
                'reward_components': reward_components,
                'control_data': control,
                'strain_data': strain_data,
                'displacement_data': {'u_field': u_field, 'v_field': v_field},
                'dic_features': dic_features,
                'thermal_features': thermal_features,
                'process_features': process_features
            }
            
            episode_data.append(timestep_data)
        
        return episode_data
    
    def _save_dataset(self, episodes, output_dir):
        """Save dataset in multiple formats."""
        # Save as HDF5 for efficient access
        h5_path = os.path.join(output_dir, "training_data.h5")
        with h5py.File(h5_path, 'w') as f:
            # Create datasets
            num_episodes = len(episodes)
            state_dim = len(episodes[0]['state'])
            action_dim = len(episodes[0]['action'])
            
            # Main data arrays
            states = np.array([ep['state'] for ep in episodes])
            actions = np.array([ep['action'] for ep in episodes])
            rewards = np.array([ep['reward'] for ep in episodes])
            timestamps = np.array([ep['timestamp'] for ep in episodes])
            
            f.create_dataset('states', data=states)
            f.create_dataset('actions', data=actions)
            f.create_dataset('rewards', data=rewards)
            f.create_dataset('timestamps', data=timestamps)
            f.create_dataset('episodes', data=[ep['episode'] for ep in episodes])
            f.create_dataset('timesteps', data=[ep['timestep'] for ep in episodes])
            
            # Metadata
            f.attrs['num_episodes'] = num_episodes
            f.attrs['state_dim'] = state_dim
            f.attrs['action_dim'] = action_dim
            f.attrs['total_timesteps'] = len(episodes)
        
        # Save as JSON for easy inspection
        json_path = os.path.join(output_dir, "dataset_summary.json")
        summary = {
            'num_episodes': len(set(ep['episode'] for ep in episodes)),
            'total_timesteps': len(episodes),
            'state_dim': state_dim,
            'action_dim': action_dim,
            'feature_names': list(episodes[0]['dic_features'].keys()) + 
                           list(episodes[0]['thermal_features'].keys()) + 
                           list(episodes[0]['process_features'].keys()),
            'reward_components': list(episodes[0]['reward_components'].keys()),
            'generation_time': datetime.now().isoformat()
        }
        
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Save detailed CSV for analysis
        csv_path = os.path.join(output_dir, "detailed_data.csv")
        df_data = []
        for ep in episodes:
            row = {
                'episode': ep['episode'],
                'timestep': ep['timestep'],
                'timestamp': ep['timestamp'],
                'reward': ep['reward'],
                **ep['reward_components'],
                **ep['dic_features'],
                **ep['thermal_features'],
                **ep['process_features']
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        df.to_csv(csv_path, index=False)
        
        print(f"Dataset saved in multiple formats:")
        print(f"  - HDF5: {h5_path}")
        print(f"  - JSON summary: {json_path}")
        print(f"  - CSV: {csv_path}")

def main():
    """Main function to generate dataset."""
    generator = DatasetGenerator()
    
    # Generate comprehensive dataset
    episodes = generator.generate_complete_dataset(
        output_dir="real_time_training_dataset",
        num_episodes=50  # Adjust based on computational resources
    )
    
    print(f"\nDataset generation complete!")
    print(f"Total episodes: {len(set(ep['episode'] for ep in episodes))}")
    print(f"Total timesteps: {len(episodes)}")
    print(f"State dimension: {len(episodes[0]['state'])}")
    print(f"Action dimension: {len(episodes[0]['action'])}")

if __name__ == "__main__":
    main()