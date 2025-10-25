#!/usr/bin/env python3
"""
Memory-Efficient Real-Time Training & Validation Dataset Generator
Optimized version for resource-constrained environments
"""

import numpy as np
import pandas as pd
import cv2
import h5py
import json
import os
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import pickle
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class CompactDatasetGenerator:
    """Memory-efficient dataset generator"""
    
    def __init__(self, output_dir: str = "compact_realtime_dataset"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Reduced parameters for memory efficiency
        self.sample_rate_hz = 10          # Reduced from 100Hz
        self.furnace_rate_hz = 5          # Reduced from 10Hz
        self.duration_hours = 2           # Reduced from 8 hours
        self.image_width = 512            # Reduced from 2048
        self.image_height = 512           # Reduced from 2048
        self.num_zones = 4                # Reduced from 6 zones
        self.num_cameras = 2              # Keep stereo setup
        
        # Physical parameters
        self.sample_size_mm = 100
        self.max_temperature = 1600
        self.target_density = 0.95
        
        # RL parameters
        self.reward_weights = {
            'warpage': 0.3,
            'strain': 0.25, 
            'density': 0.35,
            'efficiency': 0.1
        }
        
        print(f"Initialized compact dataset generator for {self.duration_hours}h simulation")
        print(f"DIC rate: {self.sample_rate_hz}Hz, Furnace rate: {self.furnace_rate_hz}Hz")
        print(f"Image size: {self.image_width}x{self.image_height}")
        
    def simulate_thermal_cycle(self, time_hours: float) -> dict:
        """Simulate realistic thermal cycle parameters"""
        if time_hours < 0.5:  # Heating phase
            progress = time_hours / 0.5
            base_temp = 20 + progress * 800
            phase = 'heating'
        elif time_hours < 1.5:  # Sintering phase
            progress = (time_hours - 0.5) / 1.0
            base_temp = 820 + progress * 780
            phase = 'sintering'
        else:  # Cooling phase
            progress = (time_hours - 1.5) / 0.5
            base_temp = 1600 - progress * 1580
            phase = 'cooling'
            
        return {
            'base_temperature': base_temp,
            'phase': phase
        }
    
    def generate_displacement_field(self, timestamp: float, thermal_params: dict) -> tuple:
        """Generate realistic displacement fields"""
        x = np.linspace(-self.sample_size_mm/2, self.sample_size_mm/2, self.image_width)
        y = np.linspace(-self.sample_size_mm/2, self.sample_size_mm/2, self.image_height)
        X, Y = np.meshgrid(x, y)
        
        temp = thermal_params['base_temperature']
        alpha_thermal = 12e-6 + 3e-9 * temp
        
        # Density progress
        density_progress = min(0.95, 0.5 + timestamp / (self.duration_hours * 3600) * 0.45)
        shrinkage_rate = 0.15 * (1 - density_progress)
        
        # Temperature gradients
        temp_gradient_x = 5 * np.sin(2 * np.pi * timestamp / 3600)
        temp_gradient_y = 3 * np.cos(2 * np.pi * timestamp / 1800)
        
        # Thermal expansion
        U = alpha_thermal * temp * X + alpha_thermal * temp_gradient_x * X**2 / (2 * self.sample_size_mm)
        V = alpha_thermal * temp * Y + alpha_thermal * temp_gradient_y * Y**2 / (2 * self.sample_size_mm)
        
        # Sintering shrinkage
        U += -shrinkage_rate * X * (1 + 0.1 * np.sin(4 * np.pi * X / self.sample_size_mm))
        V += -shrinkage_rate * Y * (1 + 0.1 * np.cos(4 * np.pi * Y / self.sample_size_mm))
        
        # Warpage
        warpage_amplitude = 0.5 * temp_gradient_x / 100
        W = warpage_amplitude * (X**2 + Y**2) / self.sample_size_mm**2
        
        # Add noise and smooth
        U += 0.01 * np.random.randn(*X.shape)
        V += 0.01 * np.random.randn(*Y.shape)
        W += 0.005 * np.random.randn(*X.shape)
        
        U = gaussian_filter(U, sigma=1)
        V = gaussian_filter(V, sigma=1)
        W = gaussian_filter(W, sigma=1)
        
        return U, V, W
    
    def calculate_strain_fields(self, U: np.ndarray, V: np.ndarray) -> dict:
        """Calculate strain fields from displacement fields"""
        du_dx = np.gradient(U, axis=1)
        du_dy = np.gradient(U, axis=0)
        dv_dx = np.gradient(V, axis=1)
        dv_dy = np.gradient(V, axis=0)
        
        strain_xx = du_dx
        strain_yy = dv_dy
        strain_xy = 0.5 * (du_dy + dv_dx)
        
        strain_avg = 0.5 * (strain_xx + strain_yy)
        strain_diff = 0.5 * np.sqrt((strain_xx - strain_yy)**2 + 4 * strain_xy**2)
        
        return {
            'strain_xx': strain_xx,
            'strain_yy': strain_yy, 
            'strain_xy': strain_xy,
            'strain_principal_max': strain_avg + strain_diff,
            'strain_principal_min': strain_avg - strain_diff
        }
    
    def generate_temperature_field(self, timestamp: float, thermal_params: dict) -> np.ndarray:
        """Generate realistic temperature distribution"""
        x = np.linspace(-1, 1, self.image_width)
        y = np.linspace(-1, 1, self.image_height)
        X, Y = np.meshgrid(x, y)
        
        base_temp = thermal_params['base_temperature']
        
        # Radial gradient
        r = np.sqrt(X**2 + Y**2)
        radial_gradient = 20 * np.exp(-2 * r)
        
        # Time-varying hot spots
        hotspot1 = 15 * np.exp(-10 * ((X - 0.3)**2 + (Y - 0.2)**2)) * np.sin(2 * np.pi * timestamp / 600)
        hotspot2 = 10 * np.exp(-8 * ((X + 0.2)**2 + (Y - 0.3)**2)) * np.cos(2 * np.pi * timestamp / 800)
        
        # Edge cooling
        edge_cooling = -30 * np.maximum(0, r - 0.7)**2
        
        temperature_field = base_temp + radial_gradient + hotspot1 + hotspot2 + edge_cooling
        temperature_field += 2 * np.random.randn(*temperature_field.shape)
        
        return gaussian_filter(temperature_field, sigma=1)
    
    def generate_dic_quality_map(self, U: np.ndarray, V: np.ndarray, temperature: np.ndarray) -> np.ndarray:
        """Generate DIC correlation quality map"""
        deformation_magnitude = np.sqrt(U**2 + V**2)
        
        quality = 0.98 * np.ones_like(U)
        
        # Temperature degradation
        temp_factor = np.clip((1800 - temperature) / 1800, 0.1, 1.0)
        quality *= temp_factor
        
        # Deformation degradation
        deform_factor = np.clip(1 - deformation_magnitude / 5.0, 0.3, 1.0)
        quality *= deform_factor
        
        # Random variations
        quality *= (0.95 + 0.1 * np.random.rand(*U.shape))
        
        # Edge effects
        x = np.linspace(-1, 1, self.image_width)
        y = np.linspace(-1, 1, self.image_height)
        X, Y = np.meshgrid(x, y)
        r = np.sqrt(X**2 + Y**2)
        edge_factor = np.clip(1.2 - r, 0.5, 1.0)
        quality *= edge_factor
        
        return np.clip(quality, 0.1, 0.98)
    
    def generate_furnace_state(self, timestamp: float, thermal_params: dict) -> dict:
        """Generate realistic furnace control data"""
        base_temp = thermal_params['base_temperature']
        phase = thermal_params['phase']
        
        zone_setpoints = []
        zone_temperatures = []
        zone_powers = []
        
        for zone_idx in range(self.num_zones):
            zone_offset = 10 * np.sin(zone_idx * np.pi / self.num_zones)
            setpoint = base_temp + zone_offset
            
            temp_error = 5 * np.random.randn() + 2 * np.sin(2 * np.pi * timestamp / 300)
            actual_temp = setpoint + temp_error
            
            if phase == 'heating':
                power = min(100, 80 + 20 * np.random.rand())
            elif phase == 'sintering':
                power = 60 + 20 * np.random.randn()
            else:
                power = max(0, 20 * np.random.rand())
                
            zone_setpoints.append(setpoint)
            zone_temperatures.append(actual_temp)
            zone_powers.append(max(0, min(100, power)))
        
        # Gas flows
        gas_flows = []
        for i in range(3):
            base_flow = 50 + 20 * i
            flow_variation = 5 * np.sin(2 * np.pi * timestamp / 1200 + i)
            gas_flows.append(base_flow + flow_variation + np.random.randn())
        
        pressure = 1.05 + 0.02 * np.sin(2 * np.pi * timestamp / 600) + 0.005 * np.random.randn()
        
        atmosphere = {
            'Ar': 95.0 + 2 * np.random.randn(),
            'H2': 4.5 + 0.5 * np.random.randn(), 
            'O2': 0.3 + 0.1 * np.random.randn(),
            'N2': 0.2 + 0.05 * np.random.randn()
        }
        
        return {
            'timestamp': timestamp,
            'zone_temperatures': zone_temperatures,
            'zone_setpoints': zone_setpoints,
            'zone_powers': zone_powers,
            'gas_flow_rates': gas_flows,
            'pressure': pressure,
            'atmosphere_composition': atmosphere
        }
    
    def calculate_rl_state(self, dic_data: dict, furnace_state: dict, timestamp: float) -> dict:
        """Calculate RL state representation"""
        
        max_principal_strain = np.max(dic_data['strain_principal_max'])
        strain_heterogeneity = np.std(dic_data['strain_principal_max'])
        sample_curvature = np.std(dic_data['displacement_w'])
        displacement_magnitude = np.mean(np.sqrt(dic_data['displacement_u']**2 + 
                                               dic_data['displacement_v']**2 + 
                                               dic_data['displacement_w']**2))
        
        avg_temperature = np.mean(dic_data['temperature_field'])
        temp_gradient = np.std(dic_data['temperature_field'])
        temp_uniformity = 1.0 / (1.0 + temp_gradient / avg_temperature)
        
        cycle_time = timestamp / 3600
        
        shrinkage = -np.mean(dic_data['displacement_u'] + dic_data['displacement_v']) / self.sample_size_mm
        estimated_density = 0.5 + 0.45 * min(1.0, shrinkage / 0.15)
        densification_rate = 0.1 * avg_temperature / 1600 * (1 - estimated_density)
        
        dic_quality = np.mean(dic_data['quality_map'])
        thermal_stability = 1.0 / (1.0 + temp_gradient / 50)
        
        return {
            'timestamp': timestamp,
            'max_principal_strain': max_principal_strain,
            'strain_heterogeneity': strain_heterogeneity,
            'sample_curvature': sample_curvature,
            'displacement_magnitude': displacement_magnitude,
            'avg_temperature': avg_temperature,
            'temp_gradient': temp_gradient,
            'temp_uniformity': temp_uniformity,
            'cycle_time': cycle_time,
            'estimated_density': estimated_density,
            'densification_rate': densification_rate,
            'dic_quality': dic_quality,
            'thermal_stability': thermal_stability
        }
    
    def generate_rl_action(self, current_state: dict, timestamp: float) -> dict:
        """Generate realistic RL actions"""
        
        zone_temp_changes = []
        power_adjustments = []
        
        for zone_idx in range(self.num_zones):
            temp_change = 0
            power_change = 0
            
            if current_state['max_principal_strain'] > 0.005:
                temp_change -= 5 * (current_state['max_principal_strain'] - 0.005) / 0.005
            
            if current_state['sample_curvature'] > 0.1:
                zone_factor = np.sin(zone_idx * np.pi / self.num_zones)
                temp_change += zone_factor * current_state['sample_curvature'] * 10
            
            if current_state['estimated_density'] < 0.8:
                temp_change += 3
                power_change += 5
            
            temp_change += 2 * np.random.randn()
            power_change += 3 * np.random.randn()
            
            temp_change = np.clip(temp_change, -10, 10)
            power_change = np.clip(power_change, -15, 15)
            
            zone_temp_changes.append(temp_change)
            power_adjustments.append(power_change)
        
        gas_flow_changes = []
        for i in range(3):
            if current_state['avg_temperature'] > 1500:
                flow_change = 2 + np.random.randn()
            else:
                flow_change = np.random.randn()
            gas_flow_changes.append(flow_change)
        
        return {
            'timestamp': timestamp,
            'zone_temp_changes': zone_temp_changes,
            'power_adjustments': power_adjustments,
            'gas_flow_changes': gas_flow_changes
        }
    
    def calculate_reward(self, state: dict, action: dict, next_state: dict) -> dict:
        """Calculate multi-objective reward"""
        
        warpage_penalty = -self.reward_weights['warpage'] * (next_state['sample_curvature']**2)
        strain_penalty = -self.reward_weights['strain'] * (next_state['max_principal_strain']**2)
        
        density_error = abs(next_state['estimated_density'] - self.target_density)
        density_reward = self.reward_weights['density'] * (1.0 - density_error)
        
        avg_power = np.mean([abs(p) for p in action['power_adjustments']])
        efficiency_reward = self.reward_weights['efficiency'] * (1.0 - avg_power / 100)
        
        quality_bonus = 0.1 * next_state['dic_quality'] if next_state['dic_quality'] > 0.8 else 0
        gradient_penalty = -0.05 * (next_state['temp_gradient'] / 100)**2
        
        total_reward = (warpage_penalty + strain_penalty + density_reward + 
                       efficiency_reward + quality_bonus + gradient_penalty)
        
        return {
            'timestamp': next_state['timestamp'],
            'warpage_penalty': warpage_penalty,
            'strain_penalty': strain_penalty,
            'density_reward': density_reward,
            'efficiency_reward': efficiency_reward,
            'total_reward': total_reward
        }
    
    def generate_complete_dataset(self):
        """Generate the complete dataset efficiently"""
        print("Starting compact dataset generation...")
        
        total_seconds = self.duration_hours * 3600
        dic_times = np.arange(0, total_seconds, 1.0/self.sample_rate_hz)
        furnace_times = np.arange(0, total_seconds, 1.0/self.furnace_rate_hz)
        
        print(f"Generating {len(dic_times)} DIC frames and {len(furnace_times)} furnace states...")
        
        # Storage lists
        dic_data_list = []
        furnace_data_list = []
        rl_states_list = []
        rl_actions_list = []
        rl_rewards_list = []
        
        # Generate DIC data
        print("Generating DIC data...")
        for i, timestamp in enumerate(dic_times):
            if i % 100 == 0:
                print(f"  DIC frame {i}/{len(dic_times)} ({100*i/len(dic_times):.1f}%)")
            
            thermal_params = self.simulate_thermal_cycle(timestamp / 3600)
            
            U, V, W = self.generate_displacement_field(timestamp, thermal_params)
            strains = self.calculate_strain_fields(U, V)
            temperature_field = self.generate_temperature_field(timestamp, thermal_params)
            quality_map = self.generate_dic_quality_map(U, V, temperature_field)
            
            dic_data = {
                'timestamp': timestamp,
                'frame_id': i,
                'displacement_u': U,
                'displacement_v': V,
                'displacement_w': W,
                'strain_xx': strains['strain_xx'],
                'strain_yy': strains['strain_yy'],
                'strain_xy': strains['strain_xy'],
                'strain_principal_max': strains['strain_principal_max'],
                'strain_principal_min': strains['strain_principal_min'],
                'temperature_field': temperature_field,
                'quality_map': quality_map
            }
            
            dic_data_list.append(dic_data)
        
        # Generate furnace data
        print("Generating furnace data...")
        for i, timestamp in enumerate(furnace_times):
            if i % 50 == 0:
                print(f"  Furnace state {i}/{len(furnace_times)} ({100*i/len(furnace_times):.1f}%)")
            
            thermal_params = self.simulate_thermal_cycle(timestamp / 3600)
            furnace_state = self.generate_furnace_state(timestamp, thermal_params)
            furnace_data_list.append(furnace_state)
        
        # Generate RL data
        print("Generating RL training data...")
        for i in range(len(furnace_data_list) - 1):
            if i % 50 == 0:
                print(f"  RL tuple {i}/{len(furnace_data_list)-1} ({100*i/(len(furnace_data_list)-1):.1f}%)")
            
            furnace_state = furnace_data_list[i]
            timestamp = furnace_state['timestamp']
            
            # Find closest DIC frame
            dic_idx = int(timestamp * self.sample_rate_hz)
            if dic_idx < len(dic_data_list):
                dic_frame = dic_data_list[dic_idx]
                
                current_state = self.calculate_rl_state(dic_frame, furnace_state, timestamp)
                rl_states_list.append(current_state)
                
                action = self.generate_rl_action(current_state, timestamp)
                rl_actions_list.append(action)
                
                # Calculate next state and reward
                if i < len(furnace_data_list) - 2:
                    next_furnace_state = furnace_data_list[i + 1]
                    next_dic_idx = int(next_furnace_state['timestamp'] * self.sample_rate_hz)
                    if next_dic_idx < len(dic_data_list):
                        next_dic_frame = dic_data_list[next_dic_idx]
                        next_state = self.calculate_rl_state(next_dic_frame, next_furnace_state, 
                                                           next_furnace_state['timestamp'])
                        
                        reward = self.calculate_reward(current_state, action, next_state)
                        rl_rewards_list.append(reward)
        
        print("Saving dataset...")
        self.save_dataset(dic_data_list, furnace_data_list, rl_states_list, rl_actions_list, rl_rewards_list)
        
        print("Dataset generation complete!")
        print(f"Generated {len(dic_data_list)} DIC frames")
        print(f"Generated {len(furnace_data_list)} furnace states")
        print(f"Generated {len(rl_states_list)} RL states")
        print(f"Generated {len(rl_actions_list)} RL actions")
        print(f"Generated {len(rl_rewards_list)} RL rewards")
    
    def save_dataset(self, dic_data_list, furnace_data_list, rl_states_list, rl_actions_list, rl_rewards_list):
        """Save dataset efficiently"""
        
        # Create directories
        (self.output_dir / "dic_data").mkdir(exist_ok=True)
        (self.output_dir / "furnace_data").mkdir(exist_ok=True)
        (self.output_dir / "rl_data").mkdir(exist_ok=True)
        (self.output_dir / "metadata").mkdir(exist_ok=True)
        
        # Save DIC data in HDF5
        print("Saving DIC data...")
        with h5py.File(self.output_dir / "dic_data" / "dic_dataset.h5", 'w') as f:
            # Create groups
            displacement_group = f.create_group('displacements')
            strain_group = f.create_group('strains')
            temperature_group = f.create_group('temperatures')
            quality_group = f.create_group('quality')
            metadata_group = f.create_group('metadata')
            
            # Stack arrays
            timestamps = [frame['timestamp'] for frame in dic_data_list]
            frame_ids = [frame['frame_id'] for frame in dic_data_list]
            
            U_stack = np.stack([frame['displacement_u'] for frame in dic_data_list])
            V_stack = np.stack([frame['displacement_v'] for frame in dic_data_list])
            W_stack = np.stack([frame['displacement_w'] for frame in dic_data_list])
            
            displacement_group.create_dataset('U', data=U_stack, compression='gzip')
            displacement_group.create_dataset('V', data=V_stack, compression='gzip')
            displacement_group.create_dataset('W', data=W_stack, compression='gzip')
            
            strain_xx_stack = np.stack([frame['strain_xx'] for frame in dic_data_list])
            strain_yy_stack = np.stack([frame['strain_yy'] for frame in dic_data_list])
            strain_xy_stack = np.stack([frame['strain_xy'] for frame in dic_data_list])
            strain_max_stack = np.stack([frame['strain_principal_max'] for frame in dic_data_list])
            strain_min_stack = np.stack([frame['strain_principal_min'] for frame in dic_data_list])
            
            strain_group.create_dataset('strain_xx', data=strain_xx_stack, compression='gzip')
            strain_group.create_dataset('strain_yy', data=strain_yy_stack, compression='gzip')
            strain_group.create_dataset('strain_xy', data=strain_xy_stack, compression='gzip')
            strain_group.create_dataset('strain_principal_max', data=strain_max_stack, compression='gzip')
            strain_group.create_dataset('strain_principal_min', data=strain_min_stack, compression='gzip')
            
            temp_stack = np.stack([frame['temperature_field'] for frame in dic_data_list])
            quality_stack = np.stack([frame['quality_map'] for frame in dic_data_list])
            
            temperature_group.create_dataset('temperature_field', data=temp_stack, compression='gzip')
            quality_group.create_dataset('quality_map', data=quality_stack, compression='gzip')
            
            metadata_group.create_dataset('timestamps', data=timestamps)
            metadata_group.create_dataset('frame_ids', data=frame_ids)
            metadata_group.attrs['sample_rate_hz'] = self.sample_rate_hz
            metadata_group.attrs['image_width'] = self.image_width
            metadata_group.attrs['image_height'] = self.image_height
        
        # Save furnace data
        print("Saving furnace data...")
        furnace_df_data = []
        for state in furnace_data_list:
            row = {
                'timestamp': state['timestamp'],
                'pressure': state['pressure']
            }
            for i, (temp, setpoint, power) in enumerate(zip(state['zone_temperatures'], 
                                                          state['zone_setpoints'], 
                                                          state['zone_powers'])):
                row[f'zone_{i}_temperature'] = temp
                row[f'zone_{i}_setpoint'] = setpoint
                row[f'zone_{i}_power'] = power
            
            for i, flow in enumerate(state['gas_flow_rates']):
                row[f'gas_flow_{i}'] = flow
            
            for gas, percentage in state['atmosphere_composition'].items():
                row[f'atmosphere_{gas}'] = percentage
                
            furnace_df_data.append(row)
        
        furnace_df = pd.DataFrame(furnace_df_data)
        furnace_df.to_csv(self.output_dir / "furnace_data" / "furnace_states.csv", index=False)
        
        # Save RL data
        print("Saving RL data...")
        rl_states_df = pd.DataFrame(rl_states_list)
        rl_states_df.to_csv(self.output_dir / "rl_data" / "rl_states.csv", index=False)
        
        rl_actions_data = []
        for action in rl_actions_list:
            row = {'timestamp': action['timestamp']}
            for i, change in enumerate(action['zone_temp_changes']):
                row[f'zone_{i}_temp_change'] = change
            for i, change in enumerate(action['power_adjustments']):
                row[f'zone_{i}_power_change'] = change
            for i, change in enumerate(action['gas_flow_changes']):
                row[f'gas_{i}_flow_change'] = change
            rl_actions_data.append(row)
        
        rl_actions_df = pd.DataFrame(rl_actions_data)
        rl_actions_df.to_csv(self.output_dir / "rl_data" / "rl_actions.csv", index=False)
        
        rl_rewards_df = pd.DataFrame(rl_rewards_list)
        rl_rewards_df.to_csv(self.output_dir / "rl_data" / "rl_rewards.csv", index=False)
        
        # Create RL tuples
        rl_tuples = []
        for i in range(len(rl_states_list) - 1):
            if i < len(rl_actions_list) and i < len(rl_rewards_list):
                tuple_data = {
                    'state': rl_states_list[i],
                    'action': rl_actions_list[i],
                    'reward': rl_rewards_list[i]['total_reward'],
                    'next_state': rl_states_list[i + 1] if i + 1 < len(rl_states_list) else None,
                    'done': i + 1 >= len(rl_states_list) - 1
                }
                rl_tuples.append(tuple_data)
        
        with open(self.output_dir / "rl_data" / "rl_tuples.pkl", 'wb') as f:
            pickle.dump(rl_tuples, f)
        
        # Save metadata
        print("Saving metadata...")
        metadata = {
            'dataset_info': {
                'generation_date': datetime.now().isoformat(),
                'duration_hours': self.duration_hours,
                'dic_sample_rate_hz': self.sample_rate_hz,
                'furnace_sample_rate_hz': self.furnace_rate_hz,
                'total_dic_frames': len(dic_data_list),
                'total_furnace_states': len(furnace_data_list),
                'total_rl_tuples': len(rl_tuples),
                'memory_optimized': True
            },
            'physical_parameters': {
                'sample_size_mm': self.sample_size_mm,
                'max_temperature_C': self.max_temperature,
                'target_density': self.target_density,
                'num_furnace_zones': self.num_zones,
                'num_cameras': self.num_cameras,
                'image_resolution': f"{self.image_width}x{self.image_height}"
            },
            'rl_parameters': {
                'reward_weights': self.reward_weights,
                'state_dimensions': len(rl_states_list[0]) if rl_states_list else 0,
                'action_dimensions': len(rl_actions_list[0]['zone_temp_changes']) + len(rl_actions_list[0]['power_adjustments']) + len(rl_actions_list[0]['gas_flow_changes']) if rl_actions_list else 0
            }
        }
        
        with open(self.output_dir / "metadata" / "dataset_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Compact dataset saved to {self.output_dir}")

def main():
    """Main function"""
    print("=== Compact Real-Time Dataset Generator ===")
    print("Memory-optimized version for resource-constrained environments")
    print()
    
    generator = CompactDatasetGenerator()
    generator.generate_complete_dataset()
    
    print("\n=== Dataset Generation Complete ===")
    print("Compact dataset ready for Digital Twin and RL training!")

if __name__ == "__main__":
    main()