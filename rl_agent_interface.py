"""
Reinforcement Learning Agent Interface
State representation, action space, and reward function for sintering process control
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import time
from scipy import stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

class ProcessPhase(Enum):
    """Process phases for sintering"""
    HEATING = "heating"
    HOLDING = "holding"
    COOLING = "cooling"
    COMPLETE = "complete"

@dataclass
class StateVector:
    """State representation for RL agent"""
    # DIC metrics
    max_principal_strain: float
    strain_heterogeneity: float
    curvature: float
    warpage_rate: float
    max_displacement: float
    
    # Thermal metrics
    avg_temperature: float
    temperature_gradient: float
    zone_temperatures: List[float]
    
    # Process metrics
    current_time: float
    current_density: float
    density_progress: float
    
    # Derived metrics
    process_phase: ProcessPhase
    stability_metric: float
    quality_score: float

@dataclass
class ActionVector:
    """Action representation for RL agent"""
    # Zone temperature changes (°C)
    zone_temp_changes: List[float]
    
    # Power adjustments (%)
    power_adjustments: List[float]
    
    # Atmosphere control
    pressure_change: float  # atm
    flow_rate_change: float  # L/min
    
    # Process control
    hold_time_change: float  # seconds

class RLAgentInterface:
    """
    Interface for RL agent with comprehensive state representation and reward function
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.setup_parameters()
        self.initialize_scalers()
        self.setup_reward_weights()
        self.initialize_state_history()
        
    def setup_parameters(self):
        """Initialize RL parameters"""
        self.n_zones = self.config.get('n_zones', 4)
        self.max_temperature = self.config.get('max_temperature', 1600)
        self.min_temperature = self.config.get('min_temperature', 25)
        self.target_density = self.config.get('target_density', 0.95)
        self.initial_density = self.config.get('initial_density', 0.6)
        
        # State normalization
        self.state_bounds = {
            'max_principal_strain': (0, 0.1),
            'strain_heterogeneity': (0, 0.05),
            'curvature': (0, 0.01),
            'warpage_rate': (0, 0.001),
            'max_displacement': (0, 1.0),
            'avg_temperature': (25, 1600),
            'temperature_gradient': (0, 100),
            'current_density': (0.6, 0.95),
            'density_progress': (0, 1.0)
        }
        
        # Action bounds
        self.action_bounds = {
            'zone_temp_changes': (-20, 20),  # °C
            'power_adjustments': (-10, 10),  # %
            'pressure_change': (-0.1, 0.1),  # atm
            'flow_rate_change': (-5, 5)  # L/min
        }
        
    def initialize_scalers(self):
        """Initialize data scalers for state normalization"""
        self.state_scaler = StandardScaler()
        self.action_scaler = MinMaxScaler()
        
        # Initialize with dummy data
        dummy_states = np.random.random((100, len(self.state_bounds)))
        dummy_actions = np.random.random((100, self.n_zones * 2 + 2))
        
        self.state_scaler.fit(dummy_states)
        self.action_scaler.fit(dummy_actions)
        
    def setup_reward_weights(self):
        """Setup reward function weights"""
        self.reward_weights = {
            'warpage': self.config.get('warpage_weight', 1.0),
            'strain': self.config.get('strain_weight', 0.5),
            'density': self.config.get('density_weight', 2.0),
            'temperature_stability': self.config.get('temp_stability_weight', 0.3),
            'process_efficiency': self.config.get('efficiency_weight', 0.2),
            'quality': self.config.get('quality_weight', 1.5)
        }
        
    def initialize_state_history(self):
        """Initialize state history for trend analysis"""
        self.state_history = []
        self.action_history = []
        self.reward_history = []
        self.max_history_length = 1000
        
    def create_state_vector(self, dic_metrics: Dict, thermal_metrics: Dict, 
                          process_metrics: Dict, additional_metrics: Dict = None) -> StateVector:
        """Create comprehensive state vector from all metrics"""
        
        # Extract DIC metrics
        max_principal_strain = dic_metrics.get('max_principal_strain', 0.0)
        strain_heterogeneity = dic_metrics.get('strain_heterogeneity', 0.0)
        curvature = dic_metrics.get('curvature', 0.0)
        warpage_rate = dic_metrics.get('warpage_rate', 0.0)
        max_displacement = dic_metrics.get('max_displacement', 0.0)
        
        # Extract thermal metrics
        avg_temperature = thermal_metrics.get('average_temperature', 25.0)
        temperature_gradient = thermal_metrics.get('temperature_gradient', 0.0)
        zone_temperatures = thermal_metrics.get('zone_temperatures', [25.0] * self.n_zones)
        
        # Extract process metrics
        current_time = process_metrics.get('current_time', 0.0)
        current_density = process_metrics.get('current_density', self.initial_density)
        density_progress = process_metrics.get('density_progress', 0.0)
        
        # Determine process phase
        process_phase = self.determine_process_phase(current_time, avg_temperature, density_progress)
        
        # Calculate derived metrics
        stability_metric = self.calculate_stability_metric(zone_temperatures, temperature_gradient)
        quality_score = self.calculate_quality_score(max_principal_strain, strain_heterogeneity, 
                                                   curvature, current_density)
        
        return StateVector(
            max_principal_strain=max_principal_strain,
            strain_heterogeneity=strain_heterogeneity,
            curvature=curvature,
            warpage_rate=warpage_rate,
            max_displacement=max_displacement,
            avg_temperature=avg_temperature,
            temperature_gradient=temperature_gradient,
            zone_temperatures=zone_temperatures,
            current_time=current_time,
            current_density=current_density,
            density_progress=density_progress,
            process_phase=process_phase,
            stability_metric=stability_metric,
            quality_score=quality_score
        )
    
    def determine_process_phase(self, current_time: float, avg_temperature: float, 
                              density_progress: float) -> ProcessPhase:
        """Determine current process phase"""
        total_time = self.config.get('total_duration', 3600)
        
        if current_time < total_time * 0.4:
            return ProcessPhase.HEATING
        elif current_time < total_time * 0.6:
            return ProcessPhase.HOLDING
        elif current_time < total_time * 0.9:
            return ProcessPhase.COOLING
        else:
            return ProcessPhase.COMPLETE
    
    def calculate_stability_metric(self, zone_temperatures: List[float], 
                                 temperature_gradient: float) -> float:
        """Calculate process stability metric"""
        # Temperature uniformity
        temp_std = np.std(zone_temperatures)
        temp_uniformity = 1.0 / (1.0 + temp_std)
        
        # Gradient penalty
        gradient_penalty = 1.0 / (1.0 + temperature_gradient)
        
        return (temp_uniformity + gradient_penalty) / 2.0
    
    def calculate_quality_score(self, max_strain: float, strain_heterogeneity: float,
                              curvature: float, current_density: float) -> float:
        """Calculate overall quality score"""
        # Strain quality (lower is better)
        strain_quality = 1.0 / (1.0 + max_strain * 100)
        
        # Heterogeneity penalty (lower is better)
        heterogeneity_quality = 1.0 / (1.0 + strain_heterogeneity * 100)
        
        # Curvature penalty (lower is better)
        curvature_quality = 1.0 / (1.0 + curvature * 1000)
        
        # Density progress (higher is better)
        density_quality = current_density
        
        return (strain_quality + heterogeneity_quality + curvature_quality + density_quality) / 4.0
    
    def normalize_state(self, state: StateVector) -> np.ndarray:
        """Normalize state vector for RL agent"""
        state_array = np.array([
            state.max_principal_strain,
            state.strain_heterogeneity,
            state.curvature,
            state.warpage_rate,
            state.max_displacement,
            state.avg_temperature,
            state.temperature_gradient,
            state.current_density,
            state.density_progress
        ])
        
        # Normalize to [0, 1]
        normalized_state = np.zeros_like(state_array)
        for i, (key, (min_val, max_val)) in enumerate(self.state_bounds.items()):
            if i < len(state_array):
                normalized_state[i] = (state_array[i] - min_val) / (max_val - min_val)
                normalized_state[i] = np.clip(normalized_state[i], 0, 1)
        
        return normalized_state
    
    def create_action_vector(self, zone_temp_changes: List[float], 
                           power_adjustments: List[float],
                           pressure_change: float = 0.0,
                           flow_rate_change: float = 0.0) -> ActionVector:
        """Create action vector for RL agent"""
        return ActionVector(
            zone_temp_changes=zone_temp_changes,
            power_adjustments=power_adjustments,
            pressure_change=pressure_change,
            flow_rate_change=flow_rate_change
        )
    
    def normalize_action(self, action: ActionVector) -> np.ndarray:
        """Normalize action vector for RL agent"""
        action_array = np.array(
            action.zone_temp_changes + 
            action.power_adjustments + 
            [action.pressure_change, action.flow_rate_change]
        )
        
        # Normalize to [0, 1]
        normalized_action = np.zeros_like(action_array)
        for i in range(len(action.zone_temp_changes)):
            normalized_action[i] = (action_array[i] - self.action_bounds['zone_temp_changes'][0]) / \
                                 (self.action_bounds['zone_temp_changes'][1] - self.action_bounds['zone_temp_changes'][0])
        
        for i in range(len(action.power_adjustments)):
            idx = len(action.zone_temp_changes) + i
            normalized_action[idx] = (action_array[idx] - self.action_bounds['power_adjustments'][0]) / \
                                   (self.action_bounds['power_adjustments'][1] - self.action_bounds['power_adjustments'][0])
        
        # Pressure change
        pressure_idx = len(action.zone_temp_changes) + len(action.power_adjustments)
        normalized_action[pressure_idx] = (action_array[pressure_idx] - self.action_bounds['pressure_change'][0]) / \
                                        (self.action_bounds['pressure_change'][1] - self.action_bounds['pressure_change'][0])
        
        # Flow rate change
        flow_idx = pressure_idx + 1
        normalized_action[flow_idx] = (action_array[flow_idx] - self.action_bounds['flow_rate_change'][0]) / \
                                    (self.action_bounds['flow_rate_change'][1] - self.action_bounds['flow_rate_change'][0])
        
        return np.clip(normalized_action, 0, 1)
    
    def calculate_reward(self, state: StateVector, action: ActionVector, 
                        next_state: StateVector) -> float:
        """Calculate comprehensive multi-objective reward"""
        
        # Warpage penalty
        warpage_penalty = -self.reward_weights['warpage'] * state.warpage_rate
        
        # Strain penalty
        strain_penalty = -self.reward_weights['strain'] * state.max_principal_strain
        
        # Density progress reward
        density_reward = self.reward_weights['density'] * state.density_progress
        
        # Temperature stability penalty
        temp_stability_penalty = -self.reward_weights['temperature_stability'] * state.temperature_gradient
        
        # Process efficiency reward
        efficiency_reward = self.calculate_efficiency_reward(state, action)
        
        # Quality reward
        quality_reward = self.reward_weights['quality'] * state.quality_score
        
        # Process phase bonus
        phase_bonus = self.calculate_phase_bonus(state, next_state)
        
        # Action smoothness penalty
        smoothness_penalty = self.calculate_smoothness_penalty(action)
        
        # Total reward
        total_reward = (warpage_penalty + strain_penalty + density_reward + 
                       temp_stability_penalty + efficiency_reward + quality_reward + 
                       phase_bonus - smoothness_penalty)
        
        return total_reward
    
    def calculate_efficiency_reward(self, state: StateVector, action: ActionVector) -> float:
        """Calculate process efficiency reward"""
        # Energy efficiency (penalize large temperature changes)
        temp_change_magnitude = np.sum(np.abs(action.zone_temp_changes))
        energy_penalty = -0.1 * temp_change_magnitude
        
        # Time efficiency (reward progress)
        time_reward = 0.01 * state.density_progress
        
        return energy_penalty + time_reward
    
    def calculate_phase_bonus(self, state: StateVector, next_state: StateVector) -> float:
        """Calculate phase transition bonus"""
        if state.process_phase != next_state.process_phase:
            # Bonus for successful phase transition
            if next_state.process_phase == ProcessPhase.HOLDING:
                return 5.0
            elif next_state.process_phase == ProcessPhase.COOLING:
                return 3.0
            elif next_state.process_phase == ProcessPhase.COMPLETE:
                return 10.0
        
        return 0.0
    
    def calculate_smoothness_penalty(self, action: ActionVector) -> float:
        """Calculate action smoothness penalty"""
        if len(self.action_history) == 0:
            return 0.0
        
        # Compare with previous action
        prev_action = self.action_history[-1]
        
        # Calculate change magnitude
        temp_change = np.sum(np.abs(np.array(action.zone_temp_changes) - 
                                   np.array(prev_action.zone_temp_changes)))
        power_change = np.sum(np.abs(np.array(action.power_adjustments) - 
                                    np.array(prev_action.power_adjustments)))
        
        return 0.01 * (temp_change + power_change)
    
    def update_history(self, state: StateVector, action: ActionVector, reward: float):
        """Update state/action/reward history"""
        self.state_history.append(state)
        self.action_history.append(action)
        self.reward_history.append(reward)
        
        # Maintain history length
        if len(self.state_history) > self.max_history_length:
            self.state_history.pop(0)
            self.action_history.pop(0)
            self.reward_history.pop(0)
    
    def get_state_trends(self, window_size: int = 10) -> Dict:
        """Analyze state trends over time"""
        if len(self.state_history) < window_size:
            return {}
        
        recent_states = self.state_history[-window_size:]
        
        trends = {}
        for key in ['max_principal_strain', 'strain_heterogeneity', 'curvature', 
                   'warpage_rate', 'avg_temperature', 'current_density']:
            values = [getattr(state, key) for state in recent_states]
            slope, intercept, r_value, p_value, std_err = stats.linregress(range(len(values)), values)
            trends[key] = {
                'slope': slope,
                'r_squared': r_value**2,
                'p_value': p_value,
                'trend': 'increasing' if slope > 0 else 'decreasing'
            }
        
        return trends
    
    def get_action_statistics(self) -> Dict:
        """Get action statistics for analysis"""
        if len(self.action_history) == 0:
            return {}
        
        # Zone temperature changes
        temp_changes = np.array([action.zone_temp_changes for action in self.action_history])
        power_changes = np.array([action.power_adjustments for action in self.action_history])
        
        return {
            'zone_temp_stats': {
                'mean': np.mean(temp_changes, axis=0).tolist(),
                'std': np.std(temp_changes, axis=0).tolist(),
                'max': np.max(temp_changes, axis=0).tolist(),
                'min': np.min(temp_changes, axis=0).tolist()
            },
            'power_stats': {
                'mean': np.mean(power_changes, axis=0).tolist(),
                'std': np.std(power_changes, axis=0).tolist(),
                'max': np.max(power_changes, axis=0).tolist(),
                'min': np.min(power_changes, axis=0).tolist()
            },
            'total_actions': len(self.action_history)
        }
    
    def generate_state_action_reward_tuples(self) -> List[Dict]:
        """Generate state-action-reward-next_state tuples for training"""
        tuples = []
        
        for i in range(len(self.state_history) - 1):
            state = self.state_history[i]
            action = self.action_history[i]
            next_state = self.state_history[i + 1]
            reward = self.reward_history[i]
            
            tuple_data = {
                'state': self.normalize_state(state),
                'action': self.normalize_action(action),
                'reward': reward,
                'next_state': self.normalize_state(next_state),
                'done': next_state.process_phase == ProcessPhase.COMPLETE,
                'timestamp': i
            }
            
            tuples.append(tuple_data)
        
        return tuples
    
    def visualize_state_evolution(self, save_path: str = None):
        """Visualize state evolution over time"""
        if len(self.state_history) < 2:
            return
        
        # Prepare data
        times = list(range(len(self.state_history)))
        states_data = {
            'max_principal_strain': [s.max_principal_strain for s in self.state_history],
            'strain_heterogeneity': [s.strain_heterogeneity for s in self.state_history],
            'curvature': [s.curvature for s in self.state_history],
            'warpage_rate': [s.warpage_rate for s in self.state_history],
            'avg_temperature': [s.avg_temperature for s in self.state_history],
            'current_density': [s.current_density for s in self.state_history],
            'quality_score': [s.quality_score for s in self.state_history]
        }
        
        # Create subplots
        fig, axes = plt.subplots(3, 3, figsize=(15, 12))
        axes = axes.flatten()
        
        for i, (key, values) in enumerate(states_data.items()):
            if i < len(axes):
                axes[i].plot(times, values, 'b-', linewidth=2)
                axes[i].set_title(key.replace('_', ' ').title())
                axes[i].set_xlabel('Time Step')
                axes[i].set_ylabel('Value')
                axes[i].grid(True, alpha=0.3)
        
        # Plot rewards
        if len(self.reward_history) > 0:
            axes[-1].plot(times[:-1], self.reward_history, 'r-', linewidth=2)
            axes[-1].set_title('Reward')
            axes[-1].set_xlabel('Time Step')
            axes[-1].set_ylabel('Reward')
            axes[-1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        plt.close()
    
    def export_training_data(self, filename: str):
        """Export training data to file"""
        tuples = self.generate_state_action_reward_tuples()
        
        # Convert to DataFrame
        data = []
        for i, tuple_data in enumerate(tuples):
            row = {
                'timestamp': tuple_data['timestamp'],
                'reward': tuple_data['reward'],
                'done': tuple_data['done']
            }
            
            # Add state features
            for j, value in enumerate(tuple_data['state']):
                row[f'state_{j}'] = value
            
            # Add action features
            for j, value in enumerate(tuple_data['action']):
                row[f'action_{j}'] = value
            
            # Add next state features
            for j, value in enumerate(tuple_data['next_state']):
                row[f'next_state_{j}'] = value
            
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        
        print(f"Training data exported to {filename}")
        print(f"Total tuples: {len(tuples)}")
        print(f"Features: {len(df.columns) - 3}")  # Excluding timestamp, reward, done

class ProcessController:
    """
    Process controller that interfaces with RL agent
    """
    
    def __init__(self, rl_interface: RLAgentInterface, config: Dict):
        self.rl_interface = rl_interface
        self.config = config
        self.current_state = None
        self.process_start_time = time.time()
        
    def update_state(self, dic_metrics: Dict, thermal_metrics: Dict, 
                    process_metrics: Dict) -> StateVector:
        """Update current state from sensor data"""
        self.current_state = self.rl_interface.create_state_vector(
            dic_metrics, thermal_metrics, process_metrics
        )
        return self.current_state
    
    def get_action(self, state: StateVector) -> ActionVector:
        """Get action from RL agent (placeholder for actual RL model)"""
        # This would interface with the actual RL model
        # For now, return a random action for demonstration
        
        zone_temp_changes = np.random.uniform(-5, 5, self.config['n_zones']).tolist()
        power_adjustments = np.random.uniform(-2, 2, self.config['n_zones']).tolist()
        pressure_change = np.random.uniform(-0.01, 0.01)
        flow_rate_change = np.random.uniform(-1, 1)
        
        return self.rl_interface.create_action_vector(
            zone_temp_changes, power_adjustments, pressure_change, flow_rate_change
        )
    
    def execute_action(self, action: ActionVector) -> Dict:
        """Execute action and return results"""
        # This would interface with the actual furnace control system
        # For now, return simulated results
        
        return {
            'zone_temperatures': [25 + np.random.uniform(-2, 2) for _ in range(self.config['n_zones'])],
            'zone_powers': [50 + np.random.uniform(-5, 5) for _ in range(self.config['n_zones'])],
            'pressure': 1.0 + action.pressure_change,
            'flow_rate': 10.0 + action.flow_rate_change,
            'success': True
        }
    
    def run_control_loop(self, dic_metrics: Dict, thermal_metrics: Dict, 
                        process_metrics: Dict) -> Dict:
        """Run one iteration of the control loop"""
        # Update state
        state = self.update_state(dic_metrics, thermal_metrics, process_metrics)
        
        # Get action
        action = self.get_action(state)
        
        # Execute action
        results = self.execute_action(action)
        
        # Calculate reward (simplified)
        reward = self.rl_interface.calculate_reward(state, action, state)
        
        # Update history
        self.rl_interface.update_history(state, action, reward)
        
        return {
            'state': state,
            'action': action,
            'reward': reward,
            'results': results
        }