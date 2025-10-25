#!/usr/bin/env python3
"""
Minimal Real-Time Dataset Generator
Ultra-lightweight version for demonstration purposes
"""

import numpy as np
import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path
import pickle

class MinimalDatasetGenerator:
    """Ultra-lightweight dataset generator"""
    
    def __init__(self, output_dir: str = "minimal_realtime_dataset"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Minimal parameters
        self.sample_rate_hz = 5           # Very low rate
        self.furnace_rate_hz = 2          # Very low rate
        self.duration_hours = 0.5         # 30 minutes only
        self.image_width = 64             # Very small images
        self.image_height = 64
        self.num_zones = 3                # Fewer zones
        
        # Physical parameters
        self.sample_size_mm = 100
        self.max_temperature = 1600
        self.target_density = 0.95
        
        print(f"Minimal dataset: {self.duration_hours}h, {self.sample_rate_hz}Hz DIC, {self.image_width}x{self.image_height}")
        
    def simulate_thermal_cycle(self, time_hours: float) -> dict:
        """Simple thermal cycle"""
        if time_hours < 0.25:  # Heating
            base_temp = 20 + time_hours * 3200  # Heat to 820°C
            phase = 'heating'
        else:  # Cooling
            base_temp = 820 - (time_hours - 0.25) * 3200  # Cool down
            phase = 'cooling'
            
        return {'base_temperature': base_temp, 'phase': phase}
    
    def generate_simple_fields(self, timestamp: float, thermal_params: dict):
        """Generate simplified displacement and strain fields"""
        temp = thermal_params['base_temperature']
        
        # Simple linear fields
        x = np.linspace(-1, 1, self.image_width)
        y = np.linspace(-1, 1, self.image_height)
        X, Y = np.meshgrid(x, y)
        
        # Thermal expansion
        alpha = 12e-6
        U = alpha * temp * X * self.sample_size_mm / 2
        V = alpha * temp * Y * self.sample_size_mm / 2
        W = 0.1 * (X**2 + Y**2) * temp / 1000  # Simple warpage
        
        # Simple strains
        strain_xx = np.gradient(U, axis=1) / (self.sample_size_mm / self.image_width)
        strain_yy = np.gradient(V, axis=0) / (self.sample_size_mm / self.image_height)
        strain_xy = 0.5 * (np.gradient(U, axis=0) + np.gradient(V, axis=1)) / (self.sample_size_mm / self.image_width)
        
        # Temperature field
        temp_field = temp + 20 * np.exp(-2 * (X**2 + Y**2))
        
        # Quality map
        quality = 0.9 * np.ones_like(X) - 0.1 * np.random.rand(*X.shape)
        
        return {
            'displacement_u': U,
            'displacement_v': V,
            'displacement_w': W,
            'strain_xx': strain_xx,
            'strain_yy': strain_yy,
            'strain_xy': strain_xy,
            'strain_principal_max': strain_xx + strain_yy + np.sqrt((strain_xx - strain_yy)**2 + 4*strain_xy**2)/2,
            'temperature_field': temp_field,
            'quality_map': quality
        }
    
    def generate_furnace_state(self, timestamp: float, thermal_params: dict) -> dict:
        """Generate simple furnace state"""
        base_temp = thermal_params['base_temperature']
        
        zone_temperatures = []
        zone_setpoints = []
        zone_powers = []
        
        for i in range(self.num_zones):
            setpoint = base_temp + 10 * np.sin(i)
            actual = setpoint + 5 * np.random.randn()
            power = min(100, max(0, 50 + 30 * np.random.randn()))
            
            zone_temperatures.append(actual)
            zone_setpoints.append(setpoint)
            zone_powers.append(power)
        
        return {
            'timestamp': timestamp,
            'zone_temperatures': zone_temperatures,
            'zone_setpoints': zone_setpoints,
            'zone_powers': zone_powers,
            'pressure': 1.0 + 0.1 * np.random.randn(),
            'gas_flow_rate': 100 + 10 * np.random.randn()
        }
    
    def calculate_rl_state(self, dic_data: dict, furnace_state: dict, timestamp: float) -> dict:
        """Calculate RL state"""
        return {
            'timestamp': timestamp,
            'max_strain': np.max(dic_data['strain_principal_max']),
            'avg_temperature': np.mean(dic_data['temperature_field']),
            'temp_gradient': np.std(dic_data['temperature_field']),
            'warpage': np.std(dic_data['displacement_w']),
            'dic_quality': np.mean(dic_data['quality_map']),
            'cycle_time': timestamp / 3600,
            'estimated_density': 0.5 + 0.4 * timestamp / (self.duration_hours * 3600)
        }
    
    def generate_rl_action(self, state: dict) -> dict:
        """Generate simple RL action"""
        return {
            'timestamp': state['timestamp'],
            'temp_changes': [2 * np.random.randn() for _ in range(self.num_zones)],
            'power_changes': [5 * np.random.randn() for _ in range(self.num_zones)]
        }
    
    def calculate_reward(self, state: dict, action: dict, next_state: dict) -> float:
        """Calculate simple reward"""
        strain_penalty = -next_state['max_strain']**2
        warpage_penalty = -next_state['warpage']**2
        density_reward = next_state['estimated_density']
        
        return strain_penalty + warpage_penalty + density_reward
    
    def generate_dataset(self):
        """Generate minimal dataset"""
        print("Generating minimal dataset...")
        
        total_seconds = self.duration_hours * 3600
        dic_times = np.arange(0, total_seconds, 1.0/self.sample_rate_hz)
        furnace_times = np.arange(0, total_seconds, 1.0/self.furnace_rate_hz)
        
        print(f"Will generate {len(dic_times)} DIC frames and {len(furnace_times)} furnace states")
        
        # Generate data
        dic_states = []
        furnace_states = []
        rl_data = []
        
        # DIC data
        print("Generating DIC data...")
        for i, timestamp in enumerate(dic_times):
            thermal_params = self.simulate_thermal_cycle(timestamp / 3600)
            dic_data = self.generate_simple_fields(timestamp, thermal_params)
            dic_data['timestamp'] = timestamp
            dic_data['frame_id'] = i
            dic_states.append(dic_data)
            
            if (i + 1) % 10 == 0:
                print(f"  Generated {i+1}/{len(dic_times)} DIC frames")
        
        # Furnace data
        print("Generating furnace data...")
        for i, timestamp in enumerate(furnace_times):
            thermal_params = self.simulate_thermal_cycle(timestamp / 3600)
            furnace_state = self.generate_furnace_state(timestamp, thermal_params)
            furnace_states.append(furnace_state)
            
            if (i + 1) % 5 == 0:
                print(f"  Generated {i+1}/{len(furnace_times)} furnace states")
        
        # RL data
        print("Generating RL data...")
        for i in range(len(furnace_states) - 1):
            furnace_state = furnace_states[i]
            timestamp = furnace_state['timestamp']
            
            # Find closest DIC frame
            dic_idx = min(int(timestamp * self.sample_rate_hz), len(dic_states) - 1)
            dic_data = dic_states[dic_idx]
            
            # Current state
            current_state = self.calculate_rl_state(dic_data, furnace_state, timestamp)
            
            # Action
            action = self.generate_rl_action(current_state)
            
            # Next state
            next_furnace = furnace_states[i + 1]
            next_dic_idx = min(int(next_furnace['timestamp'] * self.sample_rate_hz), len(dic_states) - 1)
            next_dic_data = dic_states[next_dic_idx]
            next_state = self.calculate_rl_state(next_dic_data, next_furnace, next_furnace['timestamp'])
            
            # Reward
            reward = self.calculate_reward(current_state, action, next_state)
            
            rl_tuple = {
                'state': current_state,
                'action': action,
                'reward': reward,
                'next_state': next_state,
                'done': i >= len(furnace_states) - 2
            }
            
            rl_data.append(rl_tuple)
            
            if (i + 1) % 5 == 0:
                print(f"  Generated {i+1}/{len(furnace_states)-1} RL tuples")
        
        print("Saving dataset...")
        self.save_dataset(dic_states, furnace_states, rl_data)
        
        print(f"Dataset generation complete!")
        print(f"Generated {len(dic_states)} DIC frames")
        print(f"Generated {len(furnace_states)} furnace states")
        print(f"Generated {len(rl_data)} RL tuples")
        
        return len(dic_states), len(furnace_states), len(rl_data)
    
    def save_dataset(self, dic_states, furnace_states, rl_data):
        """Save dataset in simple formats"""
        
        # Create directories
        (self.output_dir / "dic_data").mkdir(exist_ok=True)
        (self.output_dir / "furnace_data").mkdir(exist_ok=True)
        (self.output_dir / "rl_data").mkdir(exist_ok=True)
        (self.output_dir / "metadata").mkdir(exist_ok=True)
        
        # Save DIC summary data (not full fields to save space)
        dic_summary = []
        for dic_state in dic_states:
            summary = {
                'timestamp': dic_state['timestamp'],
                'frame_id': dic_state['frame_id'],
                'max_displacement_u': float(np.max(dic_state['displacement_u'])),
                'max_displacement_v': float(np.max(dic_state['displacement_v'])),
                'max_displacement_w': float(np.max(dic_state['displacement_w'])),
                'max_strain_xx': float(np.max(dic_state['strain_xx'])),
                'max_strain_yy': float(np.max(dic_state['strain_yy'])),
                'max_strain_xy': float(np.max(dic_state['strain_xy'])),
                'max_principal_strain': float(np.max(dic_state['strain_principal_max'])),
                'avg_temperature': float(np.mean(dic_state['temperature_field'])),
                'temp_std': float(np.std(dic_state['temperature_field'])),
                'avg_quality': float(np.mean(dic_state['quality_map']))
            }
            dic_summary.append(summary)
        
        dic_df = pd.DataFrame(dic_summary)
        dic_df.to_csv(self.output_dir / "dic_data" / "dic_summary.csv", index=False)
        
        # Save a few full DIC frames as samples
        sample_indices = [0, len(dic_states)//2, len(dic_states)-1]
        sample_frames = {}
        for idx in sample_indices:
            sample_frames[f'frame_{idx}'] = {
                'timestamp': dic_states[idx]['timestamp'],
                'displacement_u': dic_states[idx]['displacement_u'].tolist(),
                'displacement_v': dic_states[idx]['displacement_v'].tolist(),
                'displacement_w': dic_states[idx]['displacement_w'].tolist(),
                'strain_principal_max': dic_states[idx]['strain_principal_max'].tolist(),
                'temperature_field': dic_states[idx]['temperature_field'].tolist(),
                'quality_map': dic_states[idx]['quality_map'].tolist()
            }
        
        with open(self.output_dir / "dic_data" / "sample_frames.json", 'w') as f:
            json.dump(sample_frames, f, indent=2)
        
        # Save furnace data
        furnace_df = pd.DataFrame(furnace_states)
        
        # Expand zone data
        expanded_data = []
        for state in furnace_states:
            row = {
                'timestamp': state['timestamp'],
                'pressure': state['pressure'],
                'gas_flow_rate': state['gas_flow_rate']
            }
            for i, (temp, setpoint, power) in enumerate(zip(state['zone_temperatures'], 
                                                          state['zone_setpoints'], 
                                                          state['zone_powers'])):
                row[f'zone_{i}_temperature'] = temp
                row[f'zone_{i}_setpoint'] = setpoint
                row[f'zone_{i}_power'] = power
            expanded_data.append(row)
        
        furnace_expanded_df = pd.DataFrame(expanded_data)
        furnace_expanded_df.to_csv(self.output_dir / "furnace_data" / "furnace_states.csv", index=False)
        
        # Save RL data
        rl_states = [item['state'] for item in rl_data]
        rl_actions_data = []
        rl_rewards = [item['reward'] for item in rl_data]
        
        for item in rl_data:
            action_row = {'timestamp': item['action']['timestamp']}
            for i, temp_change in enumerate(item['action']['temp_changes']):
                action_row[f'zone_{i}_temp_change'] = temp_change
            for i, power_change in enumerate(item['action']['power_changes']):
                action_row[f'zone_{i}_power_change'] = power_change
            rl_actions_data.append(action_row)
        
        pd.DataFrame(rl_states).to_csv(self.output_dir / "rl_data" / "rl_states.csv", index=False)
        pd.DataFrame(rl_actions_data).to_csv(self.output_dir / "rl_data" / "rl_actions.csv", index=False)
        pd.DataFrame({'timestamp': [item['state']['timestamp'] for item in rl_data], 'reward': rl_rewards}).to_csv(
            self.output_dir / "rl_data" / "rl_rewards.csv", index=False)
        
        # Save complete RL tuples
        with open(self.output_dir / "rl_data" / "rl_tuples.pkl", 'wb') as f:
            pickle.dump(rl_data, f)
        
        # Save metadata
        metadata = {
            'dataset_info': {
                'generation_date': datetime.now().isoformat(),
                'type': 'minimal_demonstration_dataset',
                'duration_hours': self.duration_hours,
                'dic_sample_rate_hz': self.sample_rate_hz,
                'furnace_sample_rate_hz': self.furnace_rate_hz,
                'total_dic_frames': len(dic_states),
                'total_furnace_states': len(furnace_states),
                'total_rl_tuples': len(rl_data)
            },
            'physical_parameters': {
                'sample_size_mm': self.sample_size_mm,
                'max_temperature_C': self.max_temperature,
                'target_density': self.target_density,
                'num_furnace_zones': self.num_zones,
                'image_resolution': f"{self.image_width}x{self.image_height}"
            },
            'data_description': {
                'dic_data': 'Summary statistics and sample full frames',
                'furnace_data': 'Complete time series of furnace control states',
                'rl_data': 'Complete state-action-reward-next_state tuples for training'
            }
        }
        
        with open(self.output_dir / "metadata" / "dataset_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Calculate and save dataset statistics
        stats = self.calculate_dataset_statistics(dic_states, furnace_states, rl_data)
        with open(self.output_dir / "metadata" / "dataset_statistics.json", 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"Minimal dataset saved to {self.output_dir}")
    
    def calculate_dataset_statistics(self, dic_states, furnace_states, rl_data):
        """Calculate dataset statistics"""
        
        # DIC statistics
        max_strains = [np.max(state['strain_principal_max']) for state in dic_states]
        avg_temps = [np.mean(state['temperature_field']) for state in dic_states]
        max_displacements = [np.max(np.sqrt(state['displacement_u']**2 + state['displacement_v']**2)) 
                           for state in dic_states]
        
        # Furnace statistics
        zone_temps = []
        zone_powers = []
        for state in furnace_states:
            zone_temps.extend(state['zone_temperatures'])
            zone_powers.extend(state['zone_powers'])
        
        # RL statistics
        rewards = [item['reward'] for item in rl_data]
        
        return {
            'dic_statistics': {
                'max_strain_range': [float(np.min(max_strains)), float(np.max(max_strains))],
                'temperature_range': [float(np.min(avg_temps)), float(np.max(avg_temps))],
                'displacement_range': [float(np.min(max_displacements)), float(np.max(max_displacements))]
            },
            'furnace_statistics': {
                'temperature_range': [float(np.min(zone_temps)), float(np.max(zone_temps))],
                'power_range': [float(np.min(zone_powers)), float(np.max(zone_powers))]
            },
            'rl_statistics': {
                'reward_range': [float(np.min(rewards)), float(np.max(rewards))],
                'reward_mean': float(np.mean(rewards)),
                'reward_std': float(np.std(rewards))
            }
        }

def main():
    """Main function"""
    print("=== Minimal Real-Time Dataset Generator ===")
    print("Ultra-lightweight demonstration version")
    print()
    
    generator = MinimalDatasetGenerator()
    dic_count, furnace_count, rl_count = generator.generate_dataset()
    
    print("\n=== Dataset Generation Complete ===")
    print(f"Generated:")
    print(f"  - {dic_count} DIC measurement frames")
    print(f"  - {furnace_count} furnace control states") 
    print(f"  - {rl_count} RL training tuples")
    print()
    print("Dataset structure:")
    print("├── dic_data/")
    print("│   ├── dic_summary.csv          # DIC measurement summaries")
    print("│   └── sample_frames.json       # Full field data samples")
    print("├── furnace_data/")
    print("│   └── furnace_states.csv       # Complete furnace time series")
    print("├── rl_data/")
    print("│   ├── rl_states.csv           # RL state vectors")
    print("│   ├── rl_actions.csv          # RL action vectors")
    print("│   ├── rl_rewards.csv          # RL rewards")
    print("│   └── rl_tuples.pkl           # Complete training tuples")
    print("└── metadata/")
    print("    ├── dataset_metadata.json    # Dataset documentation")
    print("    └── dataset_statistics.json  # Statistical summary")
    print()
    print("🎯 Ready for Digital Twin and RL training!")

if __name__ == "__main__":
    main()