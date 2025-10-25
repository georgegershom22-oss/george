"""
Real-Time DIC Dataset Generator for High-Temperature Sintering Process
Generates comprehensive training and validation data for RL-based process control
"""

import numpy as np
import cv2
import h5py
import pandas as pd
from scipy import ndimage, interpolate
from scipy.spatial.distance import cdist
from skimage import filters, morphology, measure
from skimage.feature import peak_local_maxima
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class DICDatasetGenerator:
    """
    Comprehensive DIC dataset generator for high-temperature sintering processes
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.setup_parameters()
        self.initialize_cameras()
        self.initialize_furnace()
        self.initialize_sample()
        
    def setup_parameters(self):
        """Initialize all simulation parameters"""
        # Video parameters
        self.fps = self.config.get('fps', 120)  # High frame rate for DIC
        self.duration = self.config.get('duration', 3600)  # 1 hour process
        self.total_frames = self.fps * self.duration
        self.resolution = self.config.get('resolution', (2048, 2048))
        
        # DIC parameters
        self.speckle_density = self.config.get('speckle_density', 0.15)
        self.speckle_size_range = self.config.get('speckle_size_range', (3, 8))
        self.subset_size = self.config.get('subset_size', 21)
        self.step_size = self.config.get('step_size', 5)
        
        # Sample parameters
        self.sample_size = self.config.get('sample_size', (50, 50, 2))  # mm
        self.material = self.config.get('material', 'ceramic')
        self.initial_density = self.config.get('initial_density', 0.6)
        self.target_density = self.config.get('target_density', 0.95)
        
        # Thermal parameters
        self.room_temp = 25  # °C
        self.max_temp = self.config.get('max_temp', 1600)  # °C
        self.heating_rate = self.config.get('heating_rate', 10)  # °C/min
        self.cooling_rate = self.config.get('cooling_rate', 5)  # °C/min
        
        # Furnace zones
        self.n_zones = self.config.get('n_zones', 4)
        self.zone_positions = np.linspace(0, self.sample_size[0], self.n_zones + 1)
        
    def initialize_cameras(self):
        """Initialize dual camera setup for 3D DIC"""
        # Camera 1: Front view
        self.cam1_pos = np.array([0, -100, 50])  # mm
        self.cam1_angle = np.array([0, 0, 0])  # degrees
        
        # Camera 2: Side view (stereo)
        self.cam2_pos = np.array([50, -100, 50])  # mm
        self.cam2_angle = np.array([0, 0, 30])  # degrees
        
        # Camera intrinsics (simplified)
        self.focal_length = 50  # mm
        self.sensor_size = (36, 24)  # mm
        self.pixel_size = 0.005  # mm/pixel
        
    def initialize_furnace(self):
        """Initialize furnace control system"""
        self.thermocouples = {
            'TC1': np.array([12.5, 12.5, 0]),  # Sample center
            'TC2': np.array([12.5, 37.5, 0]),  # Sample edge
            'TC3': np.array([37.5, 12.5, 0]),  # Sample corner
            'TC4': np.array([25, 25, 0]),      # Sample middle
            'TC5': np.array([0, 25, 0]),       # Furnace wall
            'TC6': np.array([50, 25, 0]),      # Furnace wall
        }
        
        # Initialize zone temperatures
        self.zone_temps = np.full(self.n_zones, self.room_temp)
        self.zone_powers = np.zeros(self.n_zones)
        
        # Atmospheric conditions
        self.atmosphere = {
            'gas_type': 'Argon',
            'pressure': 1.0,  # atm
            'flow_rate': 10.0,  # L/min
            'oxygen_content': 0.001  # ppm
        }
        
    def initialize_sample(self):
        """Initialize sample geometry and properties"""
        # Create sample mesh
        x = np.linspace(0, self.sample_size[0], 100)
        y = np.linspace(0, self.sample_size[1], 100)
        self.X, self.Y = np.meshgrid(x, y)
        self.Z = np.zeros_like(self.X)  # Initially flat
        
        # Initialize material properties
        self.density_map = np.full_like(self.X, self.initial_density)
        self.temperature_map = np.full_like(self.X, self.room_temp)
        
        # Initialize displacement fields
        self.U = np.zeros_like(self.X)  # X displacement
        self.V = np.zeros_like(self.Y)  # Y displacement
        self.W = np.zeros_like(self.Z)  # Z displacement (out-of-plane)
        
        # Initialize strain fields
        self.epsilon_xx = np.zeros_like(self.X)
        self.epsilon_yy = np.zeros_like(self.Y)
        self.epsilon_xy = np.zeros_like(self.X)
        
    def generate_speckle_pattern(self, frame_idx: int) -> np.ndarray:
        """Generate high-temperature resistant speckle pattern"""
        # Create base pattern
        pattern = np.zeros(self.resolution, dtype=np.uint8)
        
        # Generate random speckle centers
        n_speckles = int(self.resolution[0] * self.resolution[1] * self.speckle_density)
        centers_x = np.random.randint(0, self.resolution[0], n_speckles)
        centers_y = np.random.randint(0, self.resolution[1], n_speckles)
        
        # Add speckles with varying sizes
        for cx, cy in zip(centers_x, centers_y):
            size = np.random.randint(*self.speckle_size_range)
            intensity = np.random.randint(50, 255)
            
            # Create circular speckle
            y, x = np.ogrid[:self.resolution[0], :self.resolution[1]]
            mask = (x - cx)**2 + (y - cy)**2 <= size**2
            pattern[mask] = intensity
        
        # Add high-temperature effects (oxidation, thermal noise)
        if frame_idx > 0:
            # Simulate thermal noise
            noise = np.random.normal(0, 10, pattern.shape)
            pattern = np.clip(pattern.astype(float) + noise, 0, 255).astype(np.uint8)
            
            # Simulate oxidation (darkening)
            oxidation_factor = min(frame_idx / (self.total_frames * 0.1), 1.0)
            pattern = (pattern * (1 - oxidation_factor * 0.3)).astype(np.uint8)
        
        return pattern
    
    def apply_thermal_deformation(self, frame_idx: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Apply thermal deformation to sample"""
        # Calculate current temperature profile
        time_sec = frame_idx / self.fps
        temp_progress = min(time_sec / (self.duration * 0.6), 1.0)  # Heating phase
        
        # Update zone temperatures
        for i in range(self.n_zones):
            target_temp = self.room_temp + (self.max_temp - self.room_temp) * temp_progress
            self.zone_temps[i] = target_temp + np.random.normal(0, 5)  # Add noise
        
        # Calculate temperature field
        temp_field = self.calculate_temperature_field()
        
        # Calculate thermal expansion
        alpha = 8e-6  # Thermal expansion coefficient (1/K)
        delta_T = temp_field - self.room_temp
        
        # Calculate displacement fields
        U = alpha * delta_T * self.X * 0.1  # X displacement
        V = alpha * delta_T * self.Y * 0.1  # Y displacement
        
        # Add warpage (bending due to temperature gradients)
        warpage_factor = 0.001 * temp_progress
        W = warpage_factor * (self.X - self.sample_size[0]/2)**2 + \
            warpage_factor * (self.Y - self.sample_size[1]/2)**2
        
        # Add random thermal noise
        noise_scale = 0.01 * temp_progress
        U += np.random.normal(0, noise_scale, U.shape)
        V += np.random.normal(0, noise_scale, V.shape)
        W += np.random.normal(0, noise_scale, W.shape)
        
        return U, V, W
    
    def calculate_temperature_field(self) -> np.ndarray:
        """Calculate 2D temperature field based on zone temperatures"""
        temp_field = np.zeros_like(self.X)
        
        for i in range(self.n_zones):
            # Zone influence function
            zone_center = (self.zone_positions[i] + self.zone_positions[i+1]) / 2
            zone_width = self.zone_positions[i+1] - self.zone_positions[i]
            
            # Gaussian influence
            influence = np.exp(-((self.X - zone_center) / (zone_width/3))**2)
            temp_field += influence * self.zone_temps[i]
        
        # Normalize
        temp_field /= np.sum([np.exp(-((self.X - (self.zone_positions[i] + self.zone_positions[i+1]) / 2) / 
                                      ((self.zone_positions[i+1] - self.zone_positions[i])/3))**2) 
                             for i in range(self.n_zones)], axis=0)
        
        return temp_field
    
    def calculate_strain_fields(self, U: np.ndarray, V: np.ndarray, W: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate strain fields from displacement fields"""
        # Calculate gradients
        dx = self.X[0, 1] - self.X[0, 0]
        dy = self.Y[1, 0] - self.Y[0, 0]
        
        # Strain components
        epsilon_xx = np.gradient(U, dx, axis=1)
        epsilon_yy = np.gradient(V, dy, axis=0)
        epsilon_xy = 0.5 * (np.gradient(U, dy, axis=0) + np.gradient(V, dx, axis=1))
        
        return epsilon_xx, epsilon_yy, epsilon_xy
    
    def generate_camera_view(self, pattern: np.ndarray, U: np.ndarray, V: np.ndarray, W: np.ndarray, 
                           camera_pos: np.ndarray, camera_angle: np.ndarray) -> np.ndarray:
        """Generate camera view with applied deformation"""
        # Create coordinate mapping
        h, w = pattern.shape
        x_coords, y_coords = np.meshgrid(np.arange(w), np.arange(h))
        
        # Apply displacement
        x_deformed = x_coords + U * (w / self.sample_size[0])
        y_deformed = y_coords + V * (h / self.sample_size[1])
        
        # Apply perspective transformation (simplified)
        # Add out-of-plane displacement effect
        z_effect = W * 0.1  # Scale factor
        x_deformed += z_effect * np.cos(np.radians(camera_angle[2]))
        y_deformed += z_effect * np.sin(np.radians(camera_angle[2]))
        
        # Interpolate pattern
        from scipy.interpolate import griddata
        points = np.column_stack([x_coords.ravel(), y_coords.ravel()])
        values = pattern.ravel()
        query_points = np.column_stack([x_deformed.ravel(), y_deformed.ravel()])
        
        # Handle out-of-bounds
        valid_mask = ((query_points[:, 0] >= 0) & (query_points[:, 0] < w) & 
                     (query_points[:, 1] >= 0) & (query_points[:, 1] < h))
        
        deformed_pattern = np.zeros_like(pattern)
        if np.any(valid_mask):
            valid_query = query_points[valid_mask]
            valid_values = griddata(points, values, valid_query, method='linear', fill_value=0)
            deformed_pattern.flat[valid_mask] = valid_values
        
        # Add camera noise and blur
        noise = np.random.normal(0, 5, deformed_pattern.shape)
        blurred = cv2.GaussianBlur(deformed_pattern, (3, 3), 0)
        
        return np.clip(blurred + noise, 0, 255).astype(np.uint8)
    
    def generate_furnace_data(self, frame_idx: int) -> Dict:
        """Generate synchronized furnace control and sensor data"""
        time_sec = frame_idx / self.fps
        timestamp = datetime.now() + timedelta(seconds=time_sec)
        
        # Calculate process phase
        heating_phase = min(time_sec / (self.duration * 0.4), 1.0)
        holding_phase = max(0, min((time_sec - self.duration * 0.4) / (self.duration * 0.2), 1.0))
        cooling_phase = max(0, min((time_sec - self.duration * 0.6) / (self.duration * 0.4), 1.0))
        
        # Generate zone temperatures with realistic dynamics
        zone_temps = []
        zone_powers = []
        
        for i in range(self.n_zones):
            if heating_phase > 0:
                target_temp = self.room_temp + (self.max_temp - self.room_temp) * heating_phase
                power = min(100, heating_phase * 120)  # Power percentage
            elif holding_phase > 0:
                target_temp = self.max_temp
                power = 80  # Maintain temperature
            else:
                target_temp = self.max_temp - (self.max_temp - self.room_temp) * cooling_phase
                power = max(0, 80 - cooling_phase * 80)
            
            # Add realistic noise and dynamics
            actual_temp = target_temp + np.random.normal(0, 2)
            actual_power = power + np.random.normal(0, 5)
            
            zone_temps.append(actual_temp)
            zone_powers.append(max(0, min(100, actual_power)))
        
        # Generate thermocouple readings
        tc_readings = {}
        for tc_name, tc_pos in self.thermocouples.items():
            # Interpolate temperature at thermocouple position
            tc_temp = self.interpolate_temperature(tc_pos, zone_temps)
            tc_readings[tc_name] = tc_temp + np.random.normal(0, 1)
        
        # Generate atmospheric data
        atmosphere_data = {
            'gas_type': self.atmosphere['gas_type'],
            'pressure': self.atmosphere['pressure'] + np.random.normal(0, 0.01),
            'flow_rate': self.atmosphere['flow_rate'] + np.random.normal(0, 0.5),
            'oxygen_content': self.atmosphere['oxygen_content'] + abs(np.random.normal(0, 0.0001))
        }
        
        return {
            'timestamp': timestamp.isoformat(),
            'frame_idx': frame_idx,
            'zone_temperatures': zone_temps,
            'zone_powers': zone_powers,
            'thermocouple_readings': tc_readings,
            'atmosphere': atmosphere_data,
            'process_phase': {
                'heating': heating_phase,
                'holding': holding_phase,
                'cooling': cooling_phase
            }
        }
    
    def interpolate_temperature(self, position: np.ndarray, zone_temps: List[float]) -> float:
        """Interpolate temperature at given position"""
        x, y, z = position
        
        # Find nearest zones
        zone_centers = [(self.zone_positions[i] + self.zone_positions[i+1]) / 2 
                       for i in range(self.n_zones)]
        
        # Simple linear interpolation
        if x <= zone_centers[0]:
            return zone_temps[0]
        elif x >= zone_centers[-1]:
            return zone_temps[-1]
        else:
            for i in range(len(zone_centers) - 1):
                if zone_centers[i] <= x <= zone_centers[i+1]:
                    t = (x - zone_centers[i]) / (zone_centers[i+1] - zone_centers[i])
                    return zone_temps[i] * (1 - t) + zone_temps[i+1] * t
        
        return zone_temps[0]
    
    def calculate_density_evolution(self, frame_idx: int, temp_field: np.ndarray) -> np.ndarray:
        """Calculate density evolution during sintering"""
        time_sec = frame_idx / self.fps
        
        # Sintering kinetics (simplified)
        activation_energy = 200000  # J/mol
        gas_constant = 8.314  # J/(mol·K)
        
        # Convert temperature to Kelvin
        temp_kelvin = temp_field + 273.15
        
        # Sintering rate
        sintering_rate = np.exp(-activation_energy / (gas_constant * temp_kelvin))
        
        # Time step
        dt = 1.0 / self.fps
        
        # Update density
        density_increase = sintering_rate * dt * 0.01  # Scale factor
        self.density_map += density_increase
        
        # Ensure density doesn't exceed target
        self.density_map = np.clip(self.density_map, self.initial_density, self.target_density)
        
        return self.density_map
    
    def generate_rl_state(self, frame_idx: int, U: np.ndarray, V: np.ndarray, W: np.ndarray,
                         epsilon_xx: np.ndarray, epsilon_yy: np.ndarray, epsilon_xy: np.ndarray,
                         furnace_data: Dict) -> Dict:
        """Generate state representation for RL agent"""
        
        # Key DIC metrics
        max_principal_strain = np.max(np.sqrt(epsilon_xx**2 + epsilon_yy**2 + epsilon_xy**2))
        strain_heterogeneity = np.std(np.sqrt(epsilon_xx**2 + epsilon_yy**2 + epsilon_xy**2))
        
        # Calculate curvature (simplified)
        curvature = np.mean(np.abs(np.gradient(np.gradient(W, axis=0), axis=0) + 
                                  np.gradient(np.gradient(W, axis=1), axis=1)))
        
        # Thermal metrics
        avg_temp = np.mean(list(furnace_data['thermocouple_readings'].values()))
        temp_gradient = np.std(list(furnace_data['thermocouple_readings'].values()))
        
        # Process metrics
        current_time = frame_idx / self.fps
        current_density = np.mean(self.density_map)
        
        # Warpage rate (simplified)
        warpage_rate = np.mean(np.abs(W)) if frame_idx > 0 else 0
        
        return {
            'frame_idx': frame_idx,
            'timestamp': furnace_data['timestamp'],
            'dic_metrics': {
                'max_principal_strain': float(max_principal_strain),
                'strain_heterogeneity': float(strain_heterogeneity),
                'curvature': float(curvature),
                'warpage_rate': float(warpage_rate)
            },
            'thermal_metrics': {
                'average_temperature': float(avg_temp),
                'temperature_gradient': float(temp_gradient),
                'zone_temperatures': furnace_data['zone_temperatures']
            },
            'process_metrics': {
                'current_time': float(current_time),
                'current_density': float(current_density),
                'density_progress': float((current_density - self.initial_density) / 
                                        (self.target_density - self.initial_density))
            },
            'displacement_fields': {
                'U_max': float(np.max(np.abs(U))),
                'V_max': float(np.max(np.abs(V))),
                'W_max': float(np.max(np.abs(W)))
            }
        }
    
    def calculate_reward(self, state: Dict, action: Dict, next_state: Dict) -> float:
        """Calculate multi-objective reward function"""
        # Weights for different objectives
        w1 = 1.0  # Warpage rate weight
        w2 = 0.5  # Max strain weight
        w3 = 2.0  # Density progress weight
        w4 = 0.3  # Temperature stability weight
        
        # Current state metrics
        warpage_rate = state['dic_metrics']['warpage_rate']
        max_strain = state['dic_metrics']['max_principal_strain']
        density_progress = state['process_metrics']['density_progress']
        temp_gradient = state['thermal_metrics']['temperature_gradient']
        
        # Calculate reward components
        warpage_penalty = -w1 * warpage_rate
        strain_penalty = -w2 * max_strain
        density_reward = w3 * density_progress
        temp_stability_penalty = -w4 * temp_gradient
        
        # Total reward
        total_reward = warpage_penalty + strain_penalty + density_reward + temp_stability_penalty
        
        # Add bonus for reaching target density
        if density_progress > 0.95:
            total_reward += 10.0
        
        return total_reward
    
    def generate_action_space(self) -> Dict:
        """Generate possible actions for RL agent"""
        return {
            'zone_temperature_changes': {
                'zone_1': {'min': -10, 'max': 10, 'step': 1},  # °C
                'zone_2': {'min': -10, 'max': 10, 'step': 1},
                'zone_3': {'min': -10, 'max': 10, 'step': 1},
                'zone_4': {'min': -10, 'max': 10, 'step': 1}
            },
            'power_adjustments': {
                'zone_1': {'min': -5, 'max': 5, 'step': 1},  # %
                'zone_2': {'min': -5, 'max': 5, 'step': 1},
                'zone_3': {'min': -5, 'max': 5, 'step': 1},
                'zone_4': {'min': -5, 'max': 5, 'step': 1}
            },
            'atmosphere_control': {
                'pressure_change': {'min': -0.1, 'max': 0.1, 'step': 0.01},  # atm
                'flow_rate_change': {'min': -2, 'max': 2, 'step': 0.1}  # L/min
            }
        }
    
    def generate_complete_dataset(self) -> Dict:
        """Generate complete dataset with all components"""
        print("Generating comprehensive DIC dataset...")
        
        dataset = {
            'metadata': {
                'config': self.config,
                'generation_time': datetime.now().isoformat(),
                'total_frames': self.total_frames,
                'fps': self.fps,
                'duration': self.duration
            },
            'video_data': {
                'camera_1': [],
                'camera_2': []
            },
            'dic_data': {
                'displacement_fields': [],
                'strain_fields': [],
                'temperature_fields': [],
                'density_fields': []
            },
            'furnace_data': [],
            'rl_data': {
                'states': [],
                'actions': [],
                'rewards': [],
                'next_states': []
            }
        }
        
        # Generate action space
        action_space = self.generate_action_space()
        
        # Generate data for each frame
        for frame_idx in range(0, self.total_frames, 10):  # Sample every 10th frame for efficiency
            print(f"Processing frame {frame_idx}/{self.total_frames}")
            
            # Generate speckle pattern
            pattern = self.generate_speckle_pattern(frame_idx)
            
            # Apply thermal deformation
            U, V, W = self.apply_thermal_deformation(frame_idx)
            
            # Calculate strain fields
            epsilon_xx, epsilon_yy, epsilon_xy = self.calculate_strain_fields(U, V, W)
            
            # Calculate temperature field
            temp_field = self.calculate_temperature_field()
            
            # Calculate density evolution
            density_field = self.calculate_density_evolution(frame_idx, temp_field)
            
            # Generate camera views
            cam1_view = self.generate_camera_view(pattern, U, V, W, self.cam1_pos, self.cam1_angle)
            cam2_view = self.generate_camera_view(pattern, U, V, W, self.cam2_pos, self.cam2_angle)
            
            # Generate furnace data
            furnace_data = self.generate_furnace_data(frame_idx)
            
            # Generate RL state
            state = self.generate_rl_state(frame_idx, U, V, W, epsilon_xx, epsilon_yy, epsilon_xy, furnace_data)
            
            # Generate random action (for demonstration)
            action = self.generate_random_action(action_space)
            
            # Store data
            dataset['video_data']['camera_1'].append(cam1_view)
            dataset['video_data']['camera_2'].append(cam2_view)
            
            dataset['dic_data']['displacement_fields'].append({
                'U': U.tolist(),
                'V': V.tolist(),
                'W': W.tolist()
            })
            
            dataset['dic_data']['strain_fields'].append({
                'epsilon_xx': epsilon_xx.tolist(),
                'epsilon_yy': epsilon_yy.tolist(),
                'epsilon_xy': epsilon_xy.tolist()
            })
            
            dataset['dic_data']['temperature_fields'].append(temp_field.tolist())
            dataset['dic_data']['density_fields'].append(density_field.tolist())
            
            dataset['furnace_data'].append(furnace_data)
            dataset['rl_data']['states'].append(state)
            dataset['rl_data']['actions'].append(action)
            
            # Calculate reward (simplified for first iteration)
            if frame_idx > 0:
                prev_state = dataset['rl_data']['states'][-2]
                reward = self.calculate_reward(prev_state, action, state)
                dataset['rl_data']['rewards'].append(reward)
            else:
                dataset['rl_data']['rewards'].append(0.0)
        
        return dataset
    
    def generate_random_action(self, action_space: Dict) -> Dict:
        """Generate random action for demonstration"""
        action = {}
        
        # Zone temperature changes
        action['zone_temperature_changes'] = {}
        for zone, params in action_space['zone_temperature_changes'].items():
            action['zone_temperature_changes'][zone] = np.random.uniform(
                params['min'], params['max']
            )
        
        # Power adjustments
        action['power_adjustments'] = {}
        for zone, params in action_space['power_adjustments'].items():
            action['power_adjustments'][zone] = np.random.uniform(
                params['min'], params['max']
            )
        
        # Atmosphere control
        action['atmosphere_control'] = {}
        for param, params in action_space['atmosphere_control'].items():
            action['atmosphere_control'][param] = np.random.uniform(
                params['min'], params['max']
            )
        
        return action
    
    def save_dataset(self, dataset: Dict, filename: str):
        """Save dataset to HDF5 file"""
        print(f"Saving dataset to {filename}...")
        
        with h5py.File(filename, 'w') as f:
            # Save metadata
            f.attrs['config'] = json.dumps(self.config)
            f.attrs['generation_time'] = dataset['metadata']['generation_time']
            f.attrs['total_frames'] = dataset['metadata']['total_frames']
            f.attrs['fps'] = dataset['metadata']['fps']
            f.attrs['duration'] = dataset['metadata']['duration']
            
            # Save video data
            video_group = f.create_group('video_data')
            video_group.create_dataset('camera_1', data=np.array(dataset['video_data']['camera_1']))
            video_group.create_dataset('camera_2', data=np.array(dataset['video_data']['camera_2']))
            
            # Save DIC data
            dic_group = f.create_group('dic_data')
            
            # Displacement fields
            disp_group = dic_group.create_group('displacement_fields')
            U_data = np.array([frame['U'] for frame in dataset['dic_data']['displacement_fields']])
            V_data = np.array([frame['V'] for frame in dataset['dic_data']['displacement_fields']])
            W_data = np.array([frame['W'] for frame in dataset['dic_data']['displacement_fields']])
            
            disp_group.create_dataset('U', data=U_data)
            disp_group.create_dataset('V', data=V_data)
            disp_group.create_dataset('W', data=W_data)
            
            # Strain fields
            strain_group = dic_group.create_group('strain_fields')
            eps_xx_data = np.array([frame['epsilon_xx'] for frame in dataset['dic_data']['strain_fields']])
            eps_yy_data = np.array([frame['epsilon_yy'] for frame in dataset['dic_data']['strain_fields']])
            eps_xy_data = np.array([frame['epsilon_xy'] for frame in dataset['dic_data']['strain_fields']])
            
            strain_group.create_dataset('epsilon_xx', data=eps_xx_data)
            strain_group.create_dataset('epsilon_yy', data=eps_yy_data)
            strain_group.create_dataset('epsilon_xy', data=eps_xy_data)
            
            # Temperature and density fields
            dic_group.create_dataset('temperature_fields', data=np.array(dataset['dic_data']['temperature_fields']))
            dic_group.create_dataset('density_fields', data=np.array(dataset['dic_data']['density_fields']))
            
            # Save furnace data
            furnace_group = f.create_group('furnace_data')
            for i, furnace_frame in enumerate(dataset['furnace_data']):
                frame_group = furnace_group.create_group(f'frame_{i}')
                frame_group.attrs['timestamp'] = furnace_frame['timestamp']
                frame_group.attrs['frame_idx'] = furnace_frame['frame_idx']
                frame_group.create_dataset('zone_temperatures', data=furnace_frame['zone_temperatures'])
                frame_group.create_dataset('zone_powers', data=furnace_frame['zone_powers'])
                
                # Thermocouple readings
                tc_group = frame_group.create_group('thermocouple_readings')
                for tc_name, tc_value in furnace_frame['thermocouple_readings'].items():
                    tc_group.attrs[tc_name] = tc_value
                
                # Atmosphere data
                atm_group = frame_group.create_group('atmosphere')
                for param, value in furnace_frame['atmosphere'].items():
                    atm_group.attrs[param] = value
            
            # Save RL data
            rl_group = f.create_group('rl_data')
            
            # States
            states_group = rl_group.create_group('states')
            for i, state in enumerate(dataset['rl_data']['states']):
                state_group = states_group.create_group(f'state_{i}')
                state_group.attrs['frame_idx'] = state['frame_idx']
                state_group.attrs['timestamp'] = state['timestamp']
                
                # DIC metrics
                dic_metrics_group = state_group.create_group('dic_metrics')
                for metric, value in state['dic_metrics'].items():
                    dic_metrics_group.attrs[metric] = value
                
                # Thermal metrics
                thermal_metrics_group = state_group.create_group('thermal_metrics')
                for metric, value in state['thermal_metrics'].items():
                    if isinstance(value, list):
                        thermal_metrics_group.create_dataset(metric, data=value)
                    else:
                        thermal_metrics_group.attrs[metric] = value
                
                # Process metrics
                process_metrics_group = state_group.create_group('process_metrics')
                for metric, value in state['process_metrics'].items():
                    process_metrics_group.attrs[metric] = value
            
            # Actions
            actions_group = rl_group.create_group('actions')
            for i, action in enumerate(dataset['rl_data']['actions']):
                action_group = actions_group.create_group(f'action_{i}')
                
                # Zone temperature changes
                zone_temp_group = action_group.create_group('zone_temperature_changes')
                for zone, value in action['zone_temperature_changes'].items():
                    zone_temp_group.attrs[zone] = value
                
                # Power adjustments
                power_group = action_group.create_group('power_adjustments')
                for zone, value in action['power_adjustments'].items():
                    power_group.attrs[zone] = value
                
                # Atmosphere control
                atm_control_group = action_group.create_group('atmosphere_control')
                for param, value in action['atmosphere_control'].items():
                    atm_control_group.attrs[param] = value
            
            # Rewards
            rl_group.create_dataset('rewards', data=dataset['rl_data']['rewards'])
        
        print(f"Dataset saved successfully to {filename}")

def main():
    """Main function to generate the dataset"""
    # Configuration
    config = {
        'fps': 120,
        'duration': 3600,  # 1 hour
        'resolution': (1024, 1024),  # Reduced for faster generation
        'speckle_density': 0.15,
        'speckle_size_range': (3, 8),
        'subset_size': 21,
        'step_size': 5,
        'sample_size': (50, 50, 2),
        'material': 'ceramic',
        'initial_density': 0.6,
        'target_density': 0.95,
        'max_temp': 1600,
        'heating_rate': 10,
        'cooling_rate': 5,
        'n_zones': 4
    }
    
    # Create generator
    generator = DICDatasetGenerator(config)
    
    # Generate dataset
    dataset = generator.generate_complete_dataset()
    
    # Save dataset
    generator.save_dataset(dataset, 'dic_training_dataset.h5')
    
    print("Dataset generation complete!")
    print(f"Total frames: {len(dataset['video_data']['camera_1'])}")
    print(f"Dataset size: {len(dataset['rl_data']['states'])} states")
    print(f"Action space: {len(dataset['rl_data']['actions'])} actions")

if __name__ == "__main__":
    main()