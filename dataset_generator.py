#!/usr/bin/env python3
"""
Real-Time Training & Validation Dataset Generator
for Digital Twin and Reinforcement Learning System

This module generates comprehensive datasets including:
- High-frequency DIC data streams
- Synchronized furnace control & sensor data
- RL state-action-reward-next_state tuples
- Multi-objective optimization rewards
"""

import numpy as np
import pandas as pd
import h5py
import json
import cv2
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from scipy import signal, interpolate
from scipy.spatial.distance import cdist
import os
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class RealTimeDatasetGenerator:
    """
    Generates comprehensive real-time training and validation datasets
    for Digital Twin and Reinforcement Learning applications.
    """
    
    def __init__(self, 
                 sample_duration_hours: float = 8.0,
                 dic_fps: int = 30,
                 furnace_update_freq: float = 1.0,
                 num_thermocouples: int = 12,
                 num_heating_zones: int = 6,
                 image_resolution: Tuple[int, int] = (1920, 1080)):
        """
        Initialize the dataset generator.
        
        Args:
            sample_duration_hours: Duration of the sintering process in hours
            dic_fps: DIC camera frame rate (frames per second)
            furnace_update_freq: Furnace control update frequency (Hz)
            num_thermocouples: Number of temperature sensors
            num_heating_zones: Number of furnace heating zones
            image_resolution: DIC camera resolution (width, height)
        """
        self.sample_duration_hours = sample_duration_hours
        self.dic_fps = dic_fps
        self.furnace_update_freq = furnace_update_freq
        self.num_thermocouples = num_thermocouples
        self.num_heating_zones = num_heating_zones
        self.image_resolution = image_resolution
        
        # Calculate total samples
        self.total_dic_frames = int(sample_duration_hours * 3600 * dic_fps)
        self.total_furnace_updates = int(sample_duration_hours * 3600 * furnace_update_freq)
        
        # Time vectors
        self.dic_timestamps = np.linspace(0, sample_duration_hours * 3600, self.total_dic_frames)
        self.furnace_timestamps = np.linspace(0, sample_duration_hours * 3600, self.total_furnace_updates)
        
        # Initialize random state for reproducibility
        np.random.seed(42)
        
    def generate_dic_data_stream(self) -> Dict:
        """
        Generate high-frequency DIC data stream with synchronized video and derived data.
        
        Returns:
            Dictionary containing video frames, displacement maps, strain maps, and metadata
        """
        print("Generating DIC data stream...")
        
        # Create sample geometry (rectangular sample with speckle pattern)
        width, height = self.image_resolution
        sample_width = int(width * 0.6)  # Sample occupies 60% of frame width
        sample_height = int(height * 0.4)  # Sample occupies 40% of frame height
        sample_x = (width - sample_width) // 2
        sample_y = (height - sample_height) // 2
        
        # Generate speckle pattern for DIC
        speckle_pattern = self._generate_speckle_pattern(sample_width, sample_height)
        
        # Initialize displacement and strain fields
        displacement_u = np.zeros((self.total_dic_frames, sample_height, sample_width))
        displacement_v = np.zeros((self.total_dic_frames, sample_height, sample_width))
        displacement_w = np.zeros((self.total_dic_frames, sample_height, sample_width))
        
        strain_xx = np.zeros((self.total_dic_frames, sample_height, sample_width))
        strain_yy = np.zeros((self.total_dic_frames, sample_height, sample_width))
        strain_xy = np.zeros((self.total_dic_frames, sample_height, sample_width))
        
        # Generate realistic displacement patterns based on sintering physics
        for frame_idx in range(self.total_dic_frames):
            t = self.dic_timestamps[frame_idx]
            
            # Simulate sintering-induced shrinkage and warpage
            u_field, v_field, w_field = self._simulate_sintering_displacement(
                sample_width, sample_height, t, self.sample_duration_hours * 3600
            )
            
            displacement_u[frame_idx] = u_field
            displacement_v[frame_idx] = v_field
            displacement_w[frame_idx] = w_field
            
            # Calculate strain fields from displacement gradients
            strain_xx[frame_idx], strain_yy[frame_idx], strain_xy[frame_idx] = \
                self._calculate_strain_fields(u_field, v_field)
        
        # Generate video frames with speckle pattern and displacement
        video_frames = self._generate_video_frames(
            speckle_pattern, displacement_u, displacement_v, 
            sample_x, sample_y, sample_width, sample_height
        )
        
        # Calculate key DIC metrics
        max_principal_strain = self._calculate_max_principal_strain(strain_xx, strain_yy, strain_xy)
        strain_heterogeneity = self._calculate_strain_heterogeneity(strain_xx, strain_yy, strain_xy)
        sample_curvature = self._calculate_sample_curvature(displacement_w)
        
        dic_data = {
            'video_frames': video_frames,
            'displacement_u': displacement_u,
            'displacement_v': displacement_v,
            'displacement_w': displacement_w,
            'strain_xx': strain_xx,
            'strain_yy': strain_yy,
            'strain_xy': strain_xy,
            'max_principal_strain': max_principal_strain,
            'strain_heterogeneity': strain_heterogeneity,
            'sample_curvature': sample_curvature,
            'timestamps': self.dic_timestamps,
            'sample_geometry': {
                'width': sample_width,
                'height': sample_height,
                'x_offset': sample_x,
                'y_offset': sample_y
            }
        }
        
        print(f"Generated {self.total_dic_frames} DIC frames at {self.dic_fps} FPS")
        return dic_data
    
    def generate_furnace_control_data(self) -> Dict:
        """
        Generate synchronized furnace control and sensor data.
        
        Returns:
            Dictionary containing action vectors, temperature readings, and process metrics
        """
        print("Generating furnace control and sensor data...")
        
        # Generate realistic temperature profiles for each heating zone
        zone_temperatures = np.zeros((self.total_furnace_updates, self.num_heating_zones))
        zone_power = np.zeros((self.total_furnace_updates, self.num_heating_zones))
        
        # Define sintering temperature profile
        for zone_idx in range(self.num_heating_zones):
            # Different zones have different temperature profiles
            base_temp = 1200 + zone_idx * 50  # Base temperature varies by zone
            ramp_rate = 5 + zone_idx * 0.5  # Different ramp rates
            
            for t_idx, t in enumerate(self.furnace_timestamps):
                # Heating phase (0-30% of process)
                if t < 0.3 * self.sample_duration_hours * 3600:
                    temp = base_temp + ramp_rate * t / 60  # Ramp in °C/min
                # Sintering phase (30-70% of process)
                elif t < 0.7 * self.sample_duration_hours * 3600:
                    temp = base_temp + ramp_rate * 0.3 * self.sample_duration_hours * 60
                # Cooling phase (70-100% of process)
                else:
                    temp = (base_temp + ramp_rate * 0.3 * self.sample_duration_hours * 60) * \
                           (1 - (t - 0.7 * self.sample_duration_hours * 3600) / 
                            (0.3 * self.sample_duration_hours * 3600))
                
                zone_temperatures[t_idx, zone_idx] = temp
                zone_power[t_idx, zone_idx] = min(100, max(0, (temp - 20) / 10))  # Power as % of max
        
        # Generate thermocouple readings (with noise and spatial variation)
        thermocouple_temps = np.zeros((self.total_furnace_updates, self.num_thermocouples))
        for tc_idx in range(self.num_thermocouples):
            # Thermocouples are influenced by nearby zones
            zone_weights = np.random.dirichlet(np.ones(self.num_heating_zones))
            base_temp = np.average(zone_temperatures, axis=1, weights=zone_weights)
            
            # Add realistic noise and spatial variation
            noise = np.random.normal(0, 2, self.total_furnace_updates)  # ±2°C noise
            spatial_variation = 5 * np.sin(2 * np.pi * tc_idx / self.num_thermocouples) * \
                               np.exp(-self.furnace_timestamps / (self.sample_duration_hours * 3600))
            
            thermocouple_temps[:, tc_idx] = base_temp + noise + spatial_variation
        
        # Generate atmospheric gas readings
        oxygen_levels = 20.9 + 2 * np.sin(2 * np.pi * self.furnace_timestamps / 3600) + \
                       np.random.normal(0, 0.5, self.total_furnace_updates)
        nitrogen_levels = 78.1 - oxygen_levels + np.random.normal(0, 0.3, self.total_furnace_updates)
        
        # Generate action vectors (changes in furnace parameters)
        actions = np.zeros((self.total_furnace_updates, self.num_heating_zones))
        for t_idx in range(1, self.total_furnace_updates):
            # Actions are changes in temperature setpoints
            actions[t_idx] = zone_temperatures[t_idx] - zone_temperatures[t_idx-1]
        
        furnace_data = {
            'zone_temperatures': zone_temperatures,
            'zone_power': zone_power,
            'thermocouple_temps': thermocouple_temps,
            'oxygen_levels': oxygen_levels,
            'nitrogen_levels': nitrogen_levels,
            'actions': actions,
            'timestamps': self.furnace_timestamps,
            'zone_positions': self._generate_zone_positions(),
            'thermocouple_positions': self._generate_thermocouple_positions()
        }
        
        print(f"Generated {self.total_furnace_updates} furnace control updates at {self.furnace_update_freq} Hz")
        return furnace_data
    
    def generate_rl_state_representation(self, dic_data: Dict, furnace_data: Dict) -> Dict:
        """
        Generate RL state representation by fusing DIC, thermal, and process metrics.
        
        Args:
            dic_data: DIC data stream from generate_dic_data_stream()
            furnace_data: Furnace control data from generate_furnace_control_data()
            
        Returns:
            Dictionary containing state vectors, actions, rewards, and next states
        """
        print("Generating RL state representation...")
        
        # Interpolate DIC data to match furnace update frequency
        dic_interp = self._interpolate_dic_to_furnace_frequency(dic_data, furnace_data)
        
        # Generate state vectors
        states = []
        actions = []
        rewards = []
        next_states = []
        
        for t_idx in range(self.total_furnace_updates - 1):
            # Current state
            state = self._create_state_vector(
                dic_interp, furnace_data, t_idx, 
                self.sample_duration_hours * 3600
            )
            
            # Action (already calculated in furnace_data)
            action = furnace_data['actions'][t_idx + 1]
            
            # Next state
            next_state = self._create_state_vector(
                dic_interp, furnace_data, t_idx + 1,
                self.sample_duration_hours * 3600
            )
            
            # Calculate reward
            reward = self._calculate_multi_objective_reward(
                dic_interp, furnace_data, t_idx, state, action, next_state
            )
            
            states.append(state)
            actions.append(action)
            rewards.append(reward)
            next_states.append(next_state)
        
        rl_data = {
            'states': np.array(states),
            'actions': np.array(actions),
            'rewards': np.array(rewards),
            'next_states': np.array(next_states),
            'timestamps': furnace_data['timestamps'][:-1],
            'state_dimension': len(states[0]),
            'action_dimension': len(actions[0])
        }
        
        print(f"Generated {len(states)} RL state-action-reward-next_state tuples")
        return rl_data
    
    def _generate_speckle_pattern(self, width: int, height: int) -> np.ndarray:
        """Generate a high-contrast speckle pattern for DIC."""
        # Create random speckle pattern
        speckle = np.random.rand(height, width)
        
        # Apply threshold to create binary pattern
        threshold = 0.5
        speckle = (speckle > threshold).astype(np.uint8) * 255
        
        # Apply Gaussian blur to create smooth transitions
        speckle = cv2.GaussianBlur(speckle, (3, 3), 0)
        
        return speckle
    
    def _simulate_sintering_displacement(self, width: int, height: int, 
                                       time: float, total_time: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Simulate realistic sintering-induced displacement fields."""
        # Create coordinate grids
        x = np.linspace(0, 1, width)
        y = np.linspace(0, 1, height)
        X, Y = np.meshgrid(x, y)
        
        # Normalized time (0 to 1)
        t_norm = time / total_time
        
        # Shrinkage due to sintering (isotropic)
        shrinkage_factor = 0.05 * (1 - np.exp(-3 * t_norm))  # 5% total shrinkage
        
        # Warpage due to temperature gradients (anisotropic)
        warpage_factor = 0.02 * np.sin(2 * np.pi * t_norm) * np.exp(-2 * t_norm)
        
        # Displacement fields
        u = -shrinkage_factor * X + warpage_factor * (X - 0.5) * (Y - 0.5)
        v = -shrinkage_factor * Y + warpage_factor * (X - 0.5) * (Y - 0.5)
        w = warpage_factor * 10 * ((X - 0.5)**2 + (Y - 0.5)**2)  # Out-of-plane displacement
        
        # Add noise for realism
        noise_scale = 0.001
        u += np.random.normal(0, noise_scale, u.shape)
        v += np.random.normal(0, noise_scale, v.shape)
        w += np.random.normal(0, noise_scale, w.shape)
        
        return u, v, w
    
    def _calculate_strain_fields(self, u: np.ndarray, v: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate strain fields from displacement gradients."""
        # Calculate gradients
        du_dx = np.gradient(u, axis=1)
        dv_dy = np.gradient(v, axis=0)
        du_dy = np.gradient(u, axis=0)
        dv_dx = np.gradient(v, axis=1)
        
        # Strain components
        strain_xx = du_dx
        strain_yy = dv_dy
        strain_xy = 0.5 * (du_dy + dv_dx)
        
        return strain_xx, strain_yy, strain_xy
    
    def _calculate_max_principal_strain(self, strain_xx: np.ndarray, 
                                      strain_yy: np.ndarray, 
                                      strain_xy: np.ndarray) -> np.ndarray:
        """Calculate maximum principal strain."""
        # Principal strain calculation
        trace = strain_xx + strain_yy
        det = strain_xx * strain_yy - strain_xy**2
        
        # Maximum principal strain
        max_principal = 0.5 * (trace + np.sqrt(trace**2 - 4 * det))
        
        return np.max(max_principal, axis=(1, 2))  # Max over spatial dimensions
    
    def _calculate_strain_heterogeneity(self, strain_xx: np.ndarray, 
                                      strain_yy: np.ndarray, 
                                      strain_xy: np.ndarray) -> np.ndarray:
        """Calculate strain heterogeneity (standard deviation)."""
        # Calculate equivalent strain
        equiv_strain = np.sqrt(2 * (strain_xx**2 + strain_yy**2 + 2 * strain_xy**2))
        
        # Calculate standard deviation over spatial dimensions
        heterogeneity = np.std(equiv_strain, axis=(1, 2))
        
        return heterogeneity
    
    def _calculate_sample_curvature(self, displacement_w: np.ndarray) -> np.ndarray:
        """Calculate sample curvature from out-of-plane displacement."""
        curvatures = []
        
        for frame_idx in range(displacement_w.shape[0]):
            w = displacement_w[frame_idx]
            
            # Calculate second derivatives
            d2w_dx2 = np.gradient(np.gradient(w, axis=1), axis=1)
            d2w_dy2 = np.gradient(np.gradient(w, axis=0), axis=0)
            
            # Mean curvature
            curvature = 0.5 * (d2w_dx2 + d2w_dy2)
            curvatures.append(np.mean(np.abs(curvature)))
        
        return np.array(curvatures)
    
    def _generate_video_frames(self, speckle_pattern: np.ndarray, 
                             displacement_u: np.ndarray, displacement_v: np.ndarray,
                             sample_x: int, sample_y: int, 
                             sample_width: int, sample_height: int) -> np.ndarray:
        """Generate video frames with displaced speckle pattern."""
        frames = []
        
        for frame_idx in range(self.total_dic_frames):
            # Create base frame
            frame = np.zeros((self.image_resolution[1], self.image_resolution[0]), dtype=np.uint8)
            
            # Apply displacement to speckle pattern
            u = displacement_u[frame_idx]
            v = displacement_v[frame_idx]
            
            # Create coordinate grids
            x_coords, y_coords = np.meshgrid(
                np.arange(sample_width), np.arange(sample_height)
            )
            
            # Apply displacement
            x_displaced = x_coords + u
            y_displaced = y_coords + v
            
            # Interpolate displaced pattern
            from scipy.interpolate import griddata
            points = np.column_stack((x_coords.ravel(), y_coords.ravel()))
            values = speckle_pattern.ravel()
            displaced_coords = np.column_stack((x_displaced.ravel(), y_displaced.ravel()))
            
            displaced_pattern = griddata(
                points, values, displaced_coords, 
                method='linear', fill_value=0
            ).reshape(sample_height, sample_width)
            
            # Place in frame
            frame[sample_y:sample_y+sample_height, sample_x:sample_x+sample_width] = displaced_pattern
            
            frames.append(frame)
        
        return np.array(frames)
    
    def _interpolate_dic_to_furnace_frequency(self, dic_data: Dict, furnace_data: Dict) -> Dict:
        """Interpolate DIC data to match furnace update frequency."""
        interp_data = {}
        
        # Interpolate key metrics
        for key in ['max_principal_strain', 'strain_heterogeneity', 'sample_curvature']:
            if key in dic_data:
                f = interpolate.interp1d(
                    dic_data['timestamps'], dic_data[key], 
                    kind='linear', bounds_error=False, fill_value='extrapolate'
                )
                interp_data[key] = f(furnace_data['timestamps'])
        
        return interp_data
    
    def _create_state_vector(self, dic_interp: Dict, furnace_data: Dict, 
                           t_idx: int, total_time: float) -> np.ndarray:
        """Create state vector for RL agent."""
        state = []
        
        # DIC metrics
        state.extend([
            dic_interp['max_principal_strain'][t_idx],
            dic_interp['strain_heterogeneity'][t_idx],
            dic_interp['sample_curvature'][t_idx]
        ])
        
        # Thermal metrics (key thermocouples)
        key_thermocouples = [0, 3, 6, 9]  # Select 4 key thermocouples
        for tc_idx in key_thermocouples:
            state.append(furnace_data['thermocouple_temps'][t_idx, tc_idx])
        
        # Process metrics
        current_time = furnace_data['timestamps'][t_idx]
        state.extend([
            current_time / total_time,  # Normalized time
            np.mean(furnace_data['zone_temperatures'][t_idx]),  # Average zone temperature
            np.std(furnace_data['zone_temperatures'][t_idx]),   # Temperature uniformity
            furnace_data['oxygen_levels'][t_idx],  # Atmospheric conditions
        ])
        
        return np.array(state)
    
    def _calculate_multi_objective_reward(self, dic_interp: Dict, furnace_data: Dict, 
                                        t_idx: int, state: np.ndarray, 
                                        action: np.ndarray, next_state: np.ndarray) -> float:
        """Calculate multi-objective reward function."""
        # Weights for different objectives
        w1 = 1.0  # Warpage rate weight
        w2 = 0.5  # Max strain weight
        w3 = 2.0  # Density target weight
        
        # Warpage rate (change in curvature)
        if t_idx > 0:
            warpage_rate = abs(dic_interp['sample_curvature'][t_idx] - dic_interp['sample_curvature'][t_idx-1])
        else:
            warpage_rate = 0
        
        # Max strain
        max_strain = dic_interp['max_principal_strain'][t_idx]
        
        # Target density (simulated based on temperature and time)
        current_temp = np.mean(furnace_data['zone_temperatures'][t_idx])
        current_time = furnace_data['timestamps'][t_idx] / (self.sample_duration_hours * 3600)
        
        # Simulate density evolution
        target_density = 0.95  # 95% theoretical density target
        current_density = 0.6 + 0.3 * (1 - np.exp(-3 * current_time)) + \
                         0.05 * (current_temp - 1200) / 200  # Simplified model
        
        density_error = (target_density - current_density) ** 2
        
        # Calculate reward
        reward = -(w1 * warpage_rate + w2 * max_strain + w3 * density_error)
        
        return reward
    
    def _generate_zone_positions(self) -> np.ndarray:
        """Generate heating zone positions."""
        # Circular arrangement of heating zones
        angles = np.linspace(0, 2 * np.pi, self.num_heating_zones, endpoint=False)
        radius = 0.5
        positions = np.column_stack([
            radius * np.cos(angles),
            radius * np.sin(angles)
        ])
        return positions
    
    def _generate_thermocouple_positions(self) -> np.ndarray:
        """Generate thermocouple positions."""
        # Grid arrangement of thermocouples
        grid_size = int(np.ceil(np.sqrt(self.num_thermocouples)))
        positions = []
        
        for i in range(self.num_thermocouples):
            row = i // grid_size
            col = i % grid_size
            x = (col - grid_size/2) / grid_size
            y = (row - grid_size/2) / grid_size
            positions.append([x, y])
        
        return np.array(positions)
    
    def save_dataset(self, dic_data: Dict, furnace_data: Dict, rl_data: Dict, 
                    output_dir: str = "dataset"):
        """Save the complete dataset to files."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save DIC data
        print("Saving DIC data...")
        with h5py.File(f"{output_dir}/dic_data.h5", 'w') as f:
            f.create_dataset('video_frames', data=dic_data['video_frames'], compression='gzip')
            f.create_dataset('displacement_u', data=dic_data['displacement_u'], compression='gzip')
            f.create_dataset('displacement_v', data=dic_data['displacement_v'], compression='gzip')
            f.create_dataset('displacement_w', data=dic_data['displacement_w'], compression='gzip')
            f.create_dataset('strain_xx', data=dic_data['strain_xx'], compression='gzip')
            f.create_dataset('strain_yy', data=dic_data['strain_yy'], compression='gzip')
            f.create_dataset('strain_xy', data=dic_data['strain_xy'], compression='gzip')
            f.create_dataset('max_principal_strain', data=dic_data['max_principal_strain'])
            f.create_dataset('strain_heterogeneity', data=dic_data['strain_heterogeneity'])
            f.create_dataset('sample_curvature', data=dic_data['sample_curvature'])
            f.create_dataset('timestamps', data=dic_data['timestamps'])
            
            # Save metadata
            geometry_group = f.create_group('sample_geometry')
            for key, value in dic_data['sample_geometry'].items():
                geometry_group.attrs[key] = value
        
        # Save furnace data
        print("Saving furnace data...")
        with h5py.File(f"{output_dir}/furnace_data.h5", 'w') as f:
            f.create_dataset('zone_temperatures', data=furnace_data['zone_temperatures'], compression='gzip')
            f.create_dataset('zone_power', data=furnace_data['zone_power'], compression='gzip')
            f.create_dataset('thermocouple_temps', data=furnace_data['thermocouple_temps'], compression='gzip')
            f.create_dataset('oxygen_levels', data=furnace_data['oxygen_levels'])
            f.create_dataset('nitrogen_levels', data=furnace_data['nitrogen_levels'])
            f.create_dataset('actions', data=furnace_data['actions'])
            f.create_dataset('timestamps', data=furnace_data['timestamps'])
            f.create_dataset('zone_positions', data=furnace_data['zone_positions'])
            f.create_dataset('thermocouple_positions', data=furnace_data['thermocouple_positions'])
        
        # Save RL data
        print("Saving RL data...")
        with h5py.File(f"{output_dir}/rl_data.h5", 'w') as f:
            f.create_dataset('states', data=rl_data['states'], compression='gzip')
            f.create_dataset('actions', data=rl_data['actions'], compression='gzip')
            f.create_dataset('rewards', data=rl_data['rewards'])
            f.create_dataset('next_states', data=rl_data['next_states'], compression='gzip')
            f.create_dataset('timestamps', data=rl_data['timestamps'])
            f.attrs['state_dimension'] = rl_data['state_dimension']
            f.attrs['action_dimension'] = rl_data['action_dimension']
        
        # Save metadata
        metadata = {
            'generation_time': datetime.now().isoformat(),
            'sample_duration_hours': self.sample_duration_hours,
            'dic_fps': self.dic_fps,
            'furnace_update_freq': self.furnace_update_freq,
            'num_thermocouples': self.num_thermocouples,
            'num_heating_zones': self.num_heating_zones,
            'image_resolution': self.image_resolution,
            'total_dic_frames': self.total_dic_frames,
            'total_furnace_updates': self.total_furnace_updates,
            'rl_tuples': len(rl_data['states'])
        }
        
        with open(f"{output_dir}/metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Dataset saved to {output_dir}/")
        print(f"Total size: {self._calculate_dataset_size(output_dir):.2f} GB")
    
    def _calculate_dataset_size(self, output_dir: str) -> float:
        """Calculate total dataset size in GB."""
        total_size = 0
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
        return total_size / (1024**3)  # Convert to GB


def main():
    """Generate the complete dataset."""
    print("Starting Real-Time Training & Validation Dataset Generation")
    print("=" * 60)
    
    # Initialize generator
    generator = RealTimeDatasetGenerator(
        sample_duration_hours=8.0,
        dic_fps=30,
        furnace_update_freq=1.0,
        num_thermocouples=12,
        num_heating_zones=6,
        image_resolution=(1920, 1080)
    )
    
    # Generate datasets
    print("\n1. Generating DIC Data Stream...")
    dic_data = generator.generate_dic_data_stream()
    
    print("\n2. Generating Furnace Control Data...")
    furnace_data = generator.generate_furnace_control_data()
    
    print("\n3. Generating RL State Representation...")
    rl_data = generator.generate_rl_state_representation(dic_data, furnace_data)
    
    print("\n4. Saving Complete Dataset...")
    generator.save_dataset(dic_data, furnace_data, rl_data, "real_time_dataset")
    
    print("\n" + "=" * 60)
    print("Dataset Generation Complete!")
    print(f"Generated {len(rl_data['states'])} RL training tuples")
    print(f"DIC data: {generator.total_dic_frames} frames at {generator.dic_fps} FPS")
    print(f"Furnace data: {generator.total_furnace_updates} updates at {generator.furnace_update_freq} Hz")


if __name__ == "__main__":
    main()