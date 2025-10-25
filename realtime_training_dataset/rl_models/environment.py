#!/usr/bin/env python3
"""
Reinforcement Learning Environment for Furnace Control
Based on the real-time dataset structure
"""

import numpy as np
import gym
from gym import spaces
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional, Any
import pickle
import json
import os
from collections import deque
import matplotlib.pyplot as plt

class FurnaceControlEnv(gym.Env):
    """
    OpenAI Gym environment for furnace control using real-time DIC feedback
    """
    
    def __init__(self, 
                 dataset_path: str,
                 episode_list: List[int],
                 max_steps: int = 3600,
                 reward_weights: Dict[str, float] = None):
        """
        Args:
            dataset_path: Path to the real-time dataset
            episode_list: List of episode indices to use
            max_steps: Maximum steps per episode
            reward_weights: Weights for multi-objective reward
        """
        super(FurnaceControlEnv, self).__init__()
        
        self.dataset_path = dataset_path
        self.episode_list = episode_list
        self.max_steps = max_steps
        self.current_episode_idx = 0
        self.current_step = 0
        
        # Reward weights
        self.reward_weights = reward_weights or {
            'warpage': 1.0,
            'strain': 0.8,
            'density': 1.2,
            'temperature': 0.6,
            'energy': 0.1
        }
        
        # Load dataset metadata
        with open(os.path.join(dataset_path, "dataset_summary.json"), 'r') as f:
            self.metadata = json.load(f)
        
        # Define action and observation spaces
        self.num_zones = 6  # Number of heating zones
        self.action_space = spaces.Box(
            low=-20.0, high=20.0, 
            shape=(self.num_zones,), 
            dtype=np.float32
        )
        
        # State space: [max_strain, strain_std, curvature, temp_std, density, mean_temp, time_ratio]
        self.observation_space = spaces.Box(
            low=np.array([0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0]),
            high=np.array([0.1, 0.05, 1.0, 100.0, 1.0, 1500.0, 1.0]),
            dtype=np.float32
        )
        
        # Initialize environment state
        self.reset()
    
    def reset(self) -> np.ndarray:
        """Reset environment to start of a new episode"""
        # Select next episode
        if self.current_episode_idx >= len(self.episode_list):
            self.current_episode_idx = 0
        
        episode_id = self.episode_list[self.current_episode_idx]
        self.current_episode_idx += 1
        
        # Load episode data
        self.load_episode_data(episode_id)
        
        # Reset step counter
        self.current_step = 0
        
        # Initialize zone powers
        self.zone_powers = np.random.uniform(20, 80, self.num_zones)
        
        # Get initial state
        initial_state = self.get_current_state()
        
        return initial_state
    
    def load_episode_data(self, episode_id: int):
        """Load data for a specific episode"""
        episode_dir = os.path.join(self.dataset_path, f"episode_{episode_id:04d}")
        
        # Load RL data
        with open(os.path.join(episode_dir, "rl_data.pkl"), 'rb') as f:
            self.episode_data = pickle.load(f)
        
        # Load metadata
        with open(os.path.join(episode_dir, "metadata.json"), 'r') as f:
            self.episode_metadata = json.load(f)
        
        self.episode_length = len(self.episode_data['states'])
    
    def get_current_state(self) -> np.ndarray:
        """Get current state observation"""
        if self.current_step >= self.episode_length:
            # Return terminal state
            return np.zeros(7, dtype=np.float32)
        
        state_dict = self.episode_data['states'][self.current_step]
        
        # Convert to numpy array
        state_vector = np.array([
            state_dict['max_principal_strain'],
            state_dict['strain_std'],
            state_dict['sample_curvature'],
            state_dict['temperature_std'],
            state_dict['current_density'],
            state_dict['mean_temperature'] / 1000.0,  # Normalize temperature
            state_dict['time_in_cycle']
        ], dtype=np.float32)
        
        return state_vector
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, Dict]:
        """Execute one step in the environment"""
        # Apply action (power adjustments)
        action = np.clip(action, -20.0, 20.0)
        self.zone_powers = np.clip(self.zone_powers + action, 0.0, 100.0)
        
        # Move to next step
        self.current_step += 1
        
        # Check if episode is done
        done = (self.current_step >= min(self.episode_length, self.max_steps))
        
        # Get next state
        next_state = self.get_current_state()
        
        # Calculate reward
        reward = self.calculate_reward(action, next_state, done)
        
        # Additional info
        info = {
            'zone_powers': self.zone_powers.copy(),
            'episode_step': self.current_step,
            'episode_progress': self.current_step / self.episode_length
        }
        
        return next_state, reward, done, info
    
    def calculate_reward(self, action: np.ndarray, state: np.ndarray, done: bool) -> float:
        """Calculate reward based on multi-objective function"""
        if self.current_step >= self.episode_length:
            return 0.0
        
        # Extract state components
        max_strain = state[0]
        strain_std = state[1]
        curvature = abs(state[2])
        temp_std = state[3]
        density = state[4]
        mean_temp = state[5] * 1000.0  # Denormalize
        
        # Target values
        target_density = 0.95
        target_temp = 1000.0  # °C
        
        # Penalty components
        warpage_penalty = self.reward_weights['warpage'] * curvature
        strain_penalty = self.reward_weights['strain'] * (max_strain + strain_std)
        density_penalty = self.reward_weights['density'] * (target_density - density)**2
        temp_penalty = self.reward_weights['temperature'] * (temp_std / 100.0)
        
        # Energy efficiency bonus
        energy_usage = np.mean(self.zone_powers) / 100.0
        energy_bonus = self.reward_weights['energy'] * (1.0 - energy_usage)
        
        # Temperature control penalty
        temp_control_penalty = 0.1 * abs(mean_temp - target_temp) / target_temp
        
        # Total reward
        reward = 100.0 - (warpage_penalty + strain_penalty + density_penalty + 
                         temp_penalty + temp_control_penalty) + energy_bonus
        
        # Bonus for reaching target density
        if density >= target_density:
            reward += 50.0
        
        # Penalty for excessive strain
        if max_strain > 0.05:
            reward -= 100.0
        
        return reward
    
    def render(self, mode: str = 'human'):
        """Render the environment"""
        if mode == 'human':
            print(f"Step: {self.current_step}")
            print(f"Zone Powers: {self.zone_powers}")
            current_state = self.get_current_state()
            print(f"State: {current_state}")
            print("-" * 50)

class DigitalTwinEnvironment:
    """
    Digital Twin environment for real-time process monitoring and control
    """
    
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.current_state = None
        self.history = deque(maxlen=100)
        
        # Load physics models
        self.thermal_model = ThermalModel()
        self.mechanical_model = MechanicalModel()
        self.sintering_model = SinteringModel()
    
    def update_state(self, 
                    zone_powers: np.ndarray, 
                    dic_data: Dict, 
                    sensor_data: Dict) -> Dict:
        """Update digital twin state with new measurements"""
        
        # Process DIC data
        displacement_field = dic_data.get('displacement_field')
        strain_field = dic_data.get('strain_field')
        
        # Calculate derived metrics
        if strain_field is not None:
            max_strain = np.max(np.sqrt(strain_field[:, :, 0]**2 + strain_field[:, :, 1]**2))
            strain_std = np.std(strain_field)
            curvature = self.calculate_curvature(displacement_field)
        else:
            max_strain = strain_std = curvature = 0.0
        
        # Process temperature data
        temperatures = sensor_data.get('temperatures', [])
        if temperatures:
            mean_temp = np.mean(temperatures)
            temp_std = np.std(temperatures)
        else:
            mean_temp = temp_std = 0.0
        
        # Estimate density using sintering model
        current_density = self.sintering_model.estimate_density(
            mean_temp, sensor_data.get('time_elapsed', 0)
        )
        
        # Update state
        self.current_state = {
            'max_principal_strain': max_strain,
            'strain_std': strain_std,
            'sample_curvature': curvature,
            'temperature_std': temp_std,
            'current_density': current_density,
            'mean_temperature': mean_temp,
            'zone_powers': zone_powers.copy(),
            'timestamp': sensor_data.get('timestamp', 0)
        }
        
        # Add to history
        self.history.append(self.current_state.copy())
        
        return self.current_state
    
    def calculate_curvature(self, displacement_field: np.ndarray) -> float:
        """Calculate sample curvature from displacement field"""
        if displacement_field is None:
            return 0.0
        
        # Out-of-plane displacement
        w_field = displacement_field[:, :, 2]
        
        # Calculate second derivatives (curvature)
        d2w_dx2 = np.gradient(np.gradient(w_field, axis=1), axis=1)
        d2w_dy2 = np.gradient(np.gradient(w_field, axis=0), axis=0)
        
        # Mean curvature
        mean_curvature = np.mean(d2w_dx2 + d2w_dy2)
        
        return mean_curvature
    
    def predict_future_state(self, 
                           control_sequence: np.ndarray, 
                           time_horizon: int) -> List[Dict]:
        """Predict future states given control sequence"""
        predictions = []
        current_state = self.current_state.copy()
        
        for i in range(time_horizon):
            if i < len(control_sequence):
                zone_powers = control_sequence[i]
            else:
                zone_powers = current_state['zone_powers']
            
            # Predict next state using physics models
            next_temp = self.thermal_model.predict_temperature(
                current_state['mean_temperature'], zone_powers
            )
            
            next_strain = self.mechanical_model.predict_strain(
                current_state['max_principal_strain'], next_temp
            )
            
            next_density = self.sintering_model.predict_density(
                current_state['current_density'], next_temp
            )
            
            next_state = {
                'max_principal_strain': next_strain,
                'strain_std': current_state['strain_std'] * 1.01,  # Simplified
                'sample_curvature': current_state['sample_curvature'] * 1.005,
                'temperature_std': current_state['temperature_std'],
                'current_density': next_density,
                'mean_temperature': next_temp,
                'zone_powers': zone_powers,
                'timestamp': current_state['timestamp'] + 1
            }
            
            predictions.append(next_state)
            current_state = next_state
        
        return predictions

class ThermalModel:
    """Simplified thermal model for digital twin"""
    
    def __init__(self):
        self.thermal_diffusivity = 1e-6  # m²/s
        self.heat_capacity = 500  # J/kg·K
    
    def predict_temperature(self, current_temp: float, zone_powers: np.ndarray) -> float:
        """Predict temperature based on zone powers"""
        # Simplified model: weighted average of zone powers
        target_temp = np.mean(zone_powers) * 12.0 + 20.0  # Linear mapping
        
        # First-order response
        tau = 60.0  # Time constant in seconds
        dt = 1.0    # Time step
        
        next_temp = current_temp + (target_temp - current_temp) * (dt / tau)
        
        return next_temp

class MechanicalModel:
    """Simplified mechanical model for strain prediction"""
    
    def __init__(self):
        self.thermal_expansion = 12e-6  # 1/K
        self.elastic_modulus = 200e9    # Pa
    
    def predict_strain(self, current_strain: float, temperature: float) -> float:
        """Predict strain based on temperature"""
        # Thermal strain component
        thermal_strain = self.thermal_expansion * (temperature - 20.0) / 1000.0
        
        # Add some dynamics
        next_strain = 0.9 * current_strain + 0.1 * thermal_strain
        
        return max(0.0, next_strain)

class SinteringModel:
    """Simplified sintering model for density prediction"""
    
    def __init__(self):
        self.activation_energy = 300000  # J/mol
        self.gas_constant = 8.314        # J/mol·K
        self.pre_exponential = 1e6
    
    def predict_density(self, current_density: float, temperature: float) -> float:
        """Predict density evolution"""
        # Arrhenius-type sintering rate
        rate = self.pre_exponential * np.exp(-self.activation_energy / 
                                           (self.gas_constant * (temperature + 273.15)))
        
        # Density evolution (simplified)
        dt = 1.0  # Time step in seconds
        density_rate = rate * (0.99 - current_density) * dt / 3600.0
        
        next_density = min(0.99, current_density + density_rate)
        
        return next_density
    
    def estimate_density(self, temperature: float, time_elapsed: float) -> float:
        """Estimate current density based on thermal history"""
        # Simplified estimation
        max_density = 0.99
        rate_factor = np.exp(-200000 / (8.314 * (temperature + 273.15)))
        
        density = 0.6 + (max_density - 0.6) * (1 - np.exp(-rate_factor * time_elapsed / 3600.0))
        
        return min(max_density, density)

if __name__ == "__main__":
    # Example usage
    dataset_path = "/workspace/realtime_training_dataset"
    episode_list = list(range(10))  # Use first 10 episodes
    
    # Create environment
    env = FurnaceControlEnv(dataset_path, episode_list)
    
    # Test environment
    obs = env.reset()
    print(f"Initial observation: {obs}")
    
    for step in range(10):
        action = env.action_space.sample()  # Random action
        obs, reward, done, info = env.step(action)
        
        print(f"Step {step}: reward={reward:.2f}, done={done}")
        
        if done:
            break
    
    # Test digital twin
    digital_twin = DigitalTwinEnvironment(dataset_path)
    
    # Simulate state update
    zone_powers = np.array([50, 60, 55, 65, 58, 62])
    dic_data = {'displacement_field': np.random.random((100, 100, 3))}
    sensor_data = {'temperatures': [800, 820, 810, 830], 'timestamp': 100}
    
    state = digital_twin.update_state(zone_powers, dic_data, sensor_data)
    print(f"Digital twin state: {state}")