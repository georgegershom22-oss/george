#!/usr/bin/env python3
"""
Real-Time Training & Validation Dataset Generator
Phase 2: Core Real-Time Training & Validation Data

This script generates comprehensive datasets for:
1. Real-Time DIC Data Stream (high-frequency, synchronized)
2. Synchronized Furnace Control & Sensor Data
3. State-Action-Reward-Next_State tuples for RL training
"""

import numpy as np
import pandas as pd
import cv2
import h5py
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from scipy.spatial.distance import cdist
import pickle
from pathlib import Path
import threading
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

@dataclass
class DICFrame:
    """Single DIC frame data structure"""
    timestamp: float
    frame_id: int
    displacement_u: np.ndarray  # X displacement field
    displacement_v: np.ndarray  # Y displacement field  
    displacement_w: np.ndarray  # Z displacement field (from stereo)
    strain_xx: np.ndarray       # Normal strain in X
    strain_yy: np.ndarray       # Normal strain in Y
    strain_xy: np.ndarray       # Shear strain
    strain_principal_max: np.ndarray  # Maximum principal strain
    strain_principal_min: np.ndarray  # Minimum principal strain
    temperature_field: np.ndarray     # Temperature distribution
    quality_map: np.ndarray          # DIC correlation quality

@dataclass
class FurnaceState:
    """Furnace control and sensor state"""
    timestamp: float
    zone_temperatures: List[float]    # Measured temperatures per zone
    zone_setpoints: List[float]       # Target temperatures per zone
    zone_powers: List[float]          # Power output per zone (0-100%)
    gas_flow_rates: List[float]       # Protective gas flows
    pressure: float                   # Chamber pressure
    atmosphere_composition: Dict[str, float]  # Gas composition %

@dataclass
class RLState:
    """RL Agent state representation"""
    timestamp: float
    # DIC-derived metrics
    max_principal_strain: float
    strain_heterogeneity: float       # Standard deviation of strain
    sample_curvature: float           # Warpage metric
    displacement_magnitude: float     # Overall deformation
    
    # Thermal metrics
    avg_temperature: float
    temp_gradient: float
    temp_uniformity: float
    
    # Process metrics
    cycle_time: float                 # Time in current cycle
    estimated_density: float          # Real-time density estimate
    densification_rate: float         # Rate of densification
    
    # System health
    dic_quality: float                # Average DIC correlation quality
    thermal_stability: float          # Temperature stability metric

@dataclass
class RLAction:
    """RL Agent action vector"""
    timestamp: float
    zone_temp_changes: List[float]    # Temperature setpoint changes per zone
    power_adjustments: List[float]    # Power adjustments per zone
    gas_flow_changes: List[float]     # Gas flow rate changes
    
@dataclass
class RLReward:
    """Multi-objective reward calculation"""
    timestamp: float
    warpage_penalty: float            # Penalty for sample warpage
    strain_penalty: float             # Penalty for high strains
    density_reward: float             # Reward for achieving target density
    efficiency_reward: float          # Reward for energy efficiency
    total_reward: float               # Combined weighted reward

class RealTimeDatasetGenerator:
    """Main class for generating comprehensive real-time datasets"""
    
    def __init__(self, output_dir: str = "realtime_dataset"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Dataset parameters
        self.sample_rate_hz = 100         # DIC sampling rate
        self.furnace_rate_hz = 10         # Furnace control rate
        self.duration_hours = 8           # Total simulation duration
        self.image_width = 2048           # DIC camera resolution
        self.image_height = 2048
        self.num_zones = 6                # Number of furnace zones
        self.num_cameras = 2              # Stereo DIC setup
        
        # Physical parameters
        self.sample_size_mm = 100         # Sample dimensions
        self.max_temperature = 1600       # Max furnace temperature (°C)
        self.target_density = 0.95        # Target relative density
        
        # RL parameters
        self.reward_weights = {
            'warpage': 0.3,
            'strain': 0.25, 
            'density': 0.35,
            'efficiency': 0.1
        }
        
        # Initialize data storage
        self.dic_frames: List[DICFrame] = []
        self.furnace_states: List[FurnaceState] = []
        self.rl_states: List[RLState] = []
        self.rl_actions: List[RLAction] = []
        self.rl_rewards: List[RLReward] = []
        
        print(f"Initialized dataset generator for {self.duration_hours}h simulation")
        print(f"DIC rate: {self.sample_rate_hz}Hz, Furnace rate: {self.furnace_rate_hz}Hz")
        
    def generate_speckle_pattern(self) -> np.ndarray:
        """Generate realistic speckle pattern for DIC"""
        # Create base random pattern
        pattern = np.random.rand(self.image_height, self.image_width)
        
        # Add different speckle sizes
        for scale in [2, 4, 8, 16]:
            speckles = np.random.rand(self.image_height//scale, self.image_width//scale)
            speckles = cv2.resize(speckles, (self.image_width, self.image_height))
            pattern += 0.3 * speckles
            
        # Normalize and add contrast
        pattern = (pattern - pattern.min()) / (pattern.max() - pattern.min())
        pattern = np.power(pattern, 0.7)  # Gamma correction for realistic contrast
        
        return (pattern * 255).astype(np.uint8)
    
    def simulate_thermal_cycle(self, time_hours: float) -> Dict[str, float]:
        """Simulate realistic thermal cycle parameters"""
        # Multi-stage heating profile
        if time_hours < 1.0:  # Heating phase
            progress = time_hours / 1.0
            base_temp = 20 + progress * 800  # Heat to 820°C
            ramp_rate = 800  # °C/hour
        elif time_hours < 5.0:  # Sintering phase
            progress = (time_hours - 1.0) / 4.0
            base_temp = 820 + progress * 780  # Heat to 1600°C
            ramp_rate = 195  # °C/hour
        elif time_hours < 6.5:  # Hold phase
            base_temp = 1600
            ramp_rate = 0
        else:  # Cooling phase
            progress = (time_hours - 6.5) / 1.5
            base_temp = 1600 - progress * 1580  # Cool to 20°C
            ramp_rate = -1053  # °C/hour
            
        return {
            'base_temperature': base_temp,
            'ramp_rate': ramp_rate,
            'phase': 'heating' if time_hours < 1 else 'sintering' if time_hours < 5 else 'hold' if time_hours < 6.5 else 'cooling'
        }
    
    def generate_displacement_field(self, timestamp: float, thermal_params: Dict) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate realistic displacement fields from thermal expansion and sintering"""
        x = np.linspace(-self.sample_size_mm/2, self.sample_size_mm/2, self.image_width)
        y = np.linspace(-self.sample_size_mm/2, self.sample_size_mm/2, self.image_height)
        X, Y = np.meshgrid(x, y)
        
        # Thermal expansion coefficient (temperature dependent)
        temp = thermal_params['base_temperature']
        alpha_thermal = 12e-6 + 3e-9 * temp  # Realistic CTE variation
        
        # Sintering shrinkage (density dependent)
        density_progress = min(0.95, 0.5 + timestamp / (self.duration_hours * 3600) * 0.45)
        shrinkage_rate = 0.15 * (1 - density_progress)  # 15% max shrinkage
        
        # Temperature gradients cause non-uniform expansion
        temp_gradient_x = 5 * np.sin(2 * np.pi * timestamp / 3600)  # °C/mm gradient
        temp_gradient_y = 3 * np.cos(2 * np.pi * timestamp / 1800)
        
        # Calculate displacements
        # Thermal expansion
        u_thermal = alpha_thermal * temp * X + alpha_thermal * temp_gradient_x * X**2 / (2 * self.sample_size_mm)
        v_thermal = alpha_thermal * temp * Y + alpha_thermal * temp_gradient_y * Y**2 / (2 * self.sample_size_mm)
        
        # Sintering shrinkage (isotropic with some anisotropy)
        u_shrinkage = -shrinkage_rate * X * (1 + 0.1 * np.sin(4 * np.pi * X / self.sample_size_mm))
        v_shrinkage = -shrinkage_rate * Y * (1 + 0.1 * np.cos(4 * np.pi * Y / self.sample_size_mm))
        
        # Warpage from temperature gradients
        warpage_amplitude = 0.5 * temp_gradient_x / 100  # mm warpage per °C/mm gradient
        w_warpage = warpage_amplitude * (X**2 + Y**2) / self.sample_size_mm**2
        
        # Combine effects
        U = u_thermal + u_shrinkage + 0.01 * np.random.randn(*X.shape)  # Add noise
        V = v_thermal + v_shrinkage + 0.01 * np.random.randn(*Y.shape)
        W = w_warpage + 0.005 * np.random.randn(*X.shape)
        
        # Apply smoothing (realistic DIC filtering)
        U = gaussian_filter(U, sigma=2)
        V = gaussian_filter(V, sigma=2)
        W = gaussian_filter(W, sigma=2)
        
        return U, V, W
    
    def calculate_strain_fields(self, U: np.ndarray, V: np.ndarray) -> Dict[str, np.ndarray]:
        """Calculate strain fields from displacement fields"""
        # Calculate gradients using central differences
        du_dx = np.gradient(U, axis=1)
        du_dy = np.gradient(U, axis=0)
        dv_dx = np.gradient(V, axis=1)
        dv_dy = np.gradient(V, axis=0)
        
        # Engineering strains
        strain_xx = du_dx
        strain_yy = dv_dy
        strain_xy = 0.5 * (du_dy + dv_dx)
        
        # Principal strains
        strain_avg = 0.5 * (strain_xx + strain_yy)
        strain_diff = 0.5 * np.sqrt((strain_xx - strain_yy)**2 + 4 * strain_xy**2)
        
        strain_principal_max = strain_avg + strain_diff
        strain_principal_min = strain_avg - strain_diff
        
        return {
            'strain_xx': strain_xx,
            'strain_yy': strain_yy, 
            'strain_xy': strain_xy,
            'strain_principal_max': strain_principal_max,
            'strain_principal_min': strain_principal_min
        }
    
    def generate_temperature_field(self, timestamp: float, thermal_params: Dict) -> np.ndarray:
        """Generate realistic temperature distribution across sample"""
        x = np.linspace(-1, 1, self.image_width)
        y = np.linspace(-1, 1, self.image_height)
        X, Y = np.meshgrid(x, y)
        
        base_temp = thermal_params['base_temperature']
        
        # Radial temperature gradient (hotter in center)
        r = np.sqrt(X**2 + Y**2)
        radial_gradient = 20 * np.exp(-2 * r)  # 20°C max gradient
        
        # Time-varying hot spots
        hotspot1 = 15 * np.exp(-10 * ((X - 0.3)**2 + (Y - 0.2)**2)) * np.sin(2 * np.pi * timestamp / 600)
        hotspot2 = 10 * np.exp(-8 * ((X + 0.2)**2 + (Y - 0.3)**2)) * np.cos(2 * np.pi * timestamp / 800)
        
        # Edge cooling effects
        edge_cooling = -30 * np.maximum(0, r - 0.7)**2
        
        temperature_field = base_temp + radial_gradient + hotspot1 + hotspot2 + edge_cooling
        
        # Add realistic noise
        temperature_field += 2 * np.random.randn(*temperature_field.shape)
        
        return gaussian_filter(temperature_field, sigma=1)
    
    def generate_dic_quality_map(self, U: np.ndarray, V: np.ndarray, temperature: np.ndarray) -> np.ndarray:
        """Generate DIC correlation quality map based on conditions"""
        # Quality degrades with high temperature and large deformations
        deformation_magnitude = np.sqrt(U**2 + V**2)
        
        # Base quality (0.7 to 0.98)
        quality = 0.98 * np.ones_like(U)
        
        # Degrade with temperature (speckle pattern changes)
        temp_factor = np.clip((1800 - temperature) / 1800, 0.1, 1.0)
        quality *= temp_factor
        
        # Degrade with large deformations
        deform_factor = np.clip(1 - deformation_magnitude / 5.0, 0.3, 1.0)
        quality *= deform_factor
        
        # Add some random variations
        quality *= (0.95 + 0.1 * np.random.rand(*U.shape))
        
        # Edge effects (lower quality near boundaries)
        x = np.linspace(-1, 1, self.image_width)
        y = np.linspace(-1, 1, self.image_height)
        X, Y = np.meshgrid(x, y)
        r = np.sqrt(X**2 + Y**2)
        edge_factor = np.clip(1.2 - r, 0.5, 1.0)
        quality *= edge_factor
        
        return np.clip(quality, 0.1, 0.98)
    
    def generate_furnace_state(self, timestamp: float, thermal_params: Dict) -> FurnaceState:
        """Generate realistic furnace control and sensor data"""
        base_temp = thermal_params['base_temperature']
        phase = thermal_params['phase']
        
        # Zone temperatures (with realistic variations and control lag)
        zone_setpoints = []
        zone_temperatures = []
        zone_powers = []
        
        for zone_idx in range(self.num_zones):
            # Different zones have different setpoints for gradient control
            zone_offset = 10 * np.sin(zone_idx * np.pi / self.num_zones)  # ±10°C variation
            setpoint = base_temp + zone_offset
            
            # Actual temperature lags setpoint with some overshoot/undershoot
            temp_error = 5 * np.random.randn() + 2 * np.sin(2 * np.pi * timestamp / 300)  # Control oscillation
            actual_temp = setpoint + temp_error
            
            # Power output based on PID control simulation
            if phase == 'heating':
                power = min(100, 80 + 20 * np.random.rand())  # High power during heating
            elif phase == 'hold':
                power = 30 + 10 * np.random.randn()  # Moderate power to maintain
            else:
                power = max(0, 20 * np.random.rand())  # Low/no power during cooling
                
            zone_setpoints.append(setpoint)
            zone_temperatures.append(actual_temp)
            zone_powers.append(max(0, min(100, power)))
        
        # Gas flow rates (protective atmosphere)
        gas_flows = []
        for i in range(3):  # 3 gas lines
            base_flow = 50 + 20 * i  # Different base flows
            flow_variation = 5 * np.sin(2 * np.pi * timestamp / 1200 + i)  # Slow variations
            gas_flows.append(base_flow + flow_variation + np.random.randn())
        
        # Chamber pressure
        pressure = 1.05 + 0.02 * np.sin(2 * np.pi * timestamp / 600) + 0.005 * np.random.randn()
        
        # Atmosphere composition
        atmosphere = {
            'Ar': 95.0 + 2 * np.random.randn(),
            'H2': 4.5 + 0.5 * np.random.randn(), 
            'O2': 0.3 + 0.1 * np.random.randn(),
            'N2': 0.2 + 0.05 * np.random.randn()
        }
        
        return FurnaceState(
            timestamp=timestamp,
            zone_temperatures=zone_temperatures,
            zone_setpoints=zone_setpoints,
            zone_powers=zone_powers,
            gas_flow_rates=gas_flows,
            pressure=pressure,
            atmosphere_composition=atmosphere
        )
    
    def calculate_rl_state(self, dic_frame: DICFrame, furnace_state: FurnaceState, timestamp: float) -> RLState:
        """Calculate RL state representation from DIC and furnace data"""
        
        # DIC-derived metrics
        max_principal_strain = np.max(dic_frame.strain_principal_max)
        strain_heterogeneity = np.std(dic_frame.strain_principal_max)
        
        # Sample curvature (warpage metric)
        sample_curvature = np.std(dic_frame.displacement_w)
        
        # Overall displacement magnitude
        displacement_magnitude = np.mean(np.sqrt(dic_frame.displacement_u**2 + 
                                               dic_frame.displacement_v**2 + 
                                               dic_frame.displacement_w**2))
        
        # Thermal metrics
        avg_temperature = np.mean(dic_frame.temperature_field)
        temp_gradient = np.std(dic_frame.temperature_field)
        temp_uniformity = 1.0 / (1.0 + temp_gradient / avg_temperature)  # Higher is more uniform
        
        # Process metrics
        cycle_time = timestamp / 3600  # Hours into cycle
        
        # Density estimation (simplified model based on temperature history and shrinkage)
        shrinkage = -np.mean(dic_frame.displacement_u + dic_frame.displacement_v) / self.sample_size_mm
        estimated_density = 0.5 + 0.45 * min(1.0, shrinkage / 0.15)  # 50% to 95% density
        
        # Densification rate (change in density)
        densification_rate = 0.1 * avg_temperature / 1600 * (1 - estimated_density)  # Arrhenius-like
        
        # System health metrics
        dic_quality = np.mean(dic_frame.quality_map)
        thermal_stability = 1.0 / (1.0 + temp_gradient / 50)  # Normalized stability metric
        
        return RLState(
            timestamp=timestamp,
            max_principal_strain=max_principal_strain,
            strain_heterogeneity=strain_heterogeneity,
            sample_curvature=sample_curvature,
            displacement_magnitude=displacement_magnitude,
            avg_temperature=avg_temperature,
            temp_gradient=temp_gradient,
            temp_uniformity=temp_uniformity,
            cycle_time=cycle_time,
            estimated_density=estimated_density,
            densification_rate=densification_rate,
            dic_quality=dic_quality,
            thermal_stability=thermal_stability
        )
    
    def generate_rl_action(self, current_state: RLState, timestamp: float) -> RLAction:
        """Generate realistic RL actions based on current state"""
        
        # Simple rule-based controller for realistic actions
        zone_temp_changes = []
        power_adjustments = []
        
        for zone_idx in range(self.num_zones):
            # Temperature control based on strain and warpage
            temp_change = 0
            power_change = 0
            
            # Reduce temperature if strain is too high
            if current_state.max_principal_strain > 0.005:
                temp_change -= 5 * (current_state.max_principal_strain - 0.005) / 0.005
            
            # Adjust for warpage (curvature)
            if current_state.sample_curvature > 0.1:
                # Adjust zones differently to counteract warpage
                zone_factor = np.sin(zone_idx * np.pi / self.num_zones)
                temp_change += zone_factor * current_state.sample_curvature * 10
            
            # Density-based control
            if current_state.estimated_density < 0.8:
                temp_change += 3  # Increase temperature to promote densification
                power_change += 5
            
            # Add some exploration noise
            temp_change += 2 * np.random.randn()
            power_change += 3 * np.random.randn()
            
            # Limit changes
            temp_change = np.clip(temp_change, -10, 10)
            power_change = np.clip(power_change, -15, 15)
            
            zone_temp_changes.append(temp_change)
            power_adjustments.append(power_change)
        
        # Gas flow adjustments
        gas_flow_changes = []
        for i in range(3):
            # Adjust protective gas based on temperature
            if current_state.avg_temperature > 1500:
                flow_change = 2 + np.random.randn()  # Increase protective gas
            else:
                flow_change = np.random.randn()  # Small random adjustments
            gas_flow_changes.append(flow_change)
        
        return RLAction(
            timestamp=timestamp,
            zone_temp_changes=zone_temp_changes,
            power_adjustments=power_adjustments,
            gas_flow_changes=gas_flow_changes
        )
    
    def calculate_reward(self, state: RLState, action: RLAction, next_state: RLState) -> RLReward:
        """Calculate multi-objective reward for RL training"""
        
        # Warpage penalty (minimize sample curvature)
        warpage_penalty = -self.reward_weights['warpage'] * (next_state.sample_curvature**2)
        
        # Strain penalty (minimize maximum strains)
        strain_penalty = -self.reward_weights['strain'] * (next_state.max_principal_strain**2)
        
        # Density reward (maximize densification toward target)
        density_error = abs(next_state.estimated_density - self.target_density)
        density_reward = self.reward_weights['density'] * (1.0 - density_error)
        
        # Efficiency reward (minimize energy usage while achieving goals)
        avg_power = np.mean([abs(p) for p in action.power_adjustments])
        efficiency_reward = self.reward_weights['efficiency'] * (1.0 - avg_power / 100)
        
        # Bonus for maintaining DIC quality
        quality_bonus = 0.1 * next_state.dic_quality if next_state.dic_quality > 0.8 else 0
        
        # Penalty for excessive temperature gradients
        gradient_penalty = -0.05 * (next_state.temp_gradient / 100)**2
        
        total_reward = (warpage_penalty + strain_penalty + density_reward + 
                       efficiency_reward + quality_bonus + gradient_penalty)
        
        return RLReward(
            timestamp=next_state.timestamp,
            warpage_penalty=warpage_penalty,
            strain_penalty=strain_penalty,
            density_reward=density_reward,
            efficiency_reward=efficiency_reward,
            total_reward=total_reward
        )
    
    def generate_complete_dataset(self):
        """Generate the complete real-time dataset"""
        print("Starting complete dataset generation...")
        
        # Time vectors
        total_seconds = self.duration_hours * 3600
        dic_times = np.arange(0, total_seconds, 1.0/self.sample_rate_hz)
        furnace_times = np.arange(0, total_seconds, 1.0/self.furnace_rate_hz)
        
        print(f"Generating {len(dic_times)} DIC frames and {len(furnace_times)} furnace states...")
        
        # Generate DIC data stream
        print("Generating DIC data stream...")
        for i, timestamp in enumerate(dic_times):
            if i % 1000 == 0:
                print(f"  DIC frame {i}/{len(dic_times)} ({100*i/len(dic_times):.1f}%)")
            
            thermal_params = self.simulate_thermal_cycle(timestamp / 3600)
            
            # Generate displacement fields
            U, V, W = self.generate_displacement_field(timestamp, thermal_params)
            
            # Calculate strain fields
            strains = self.calculate_strain_fields(U, V)
            
            # Generate temperature field
            temperature_field = self.generate_temperature_field(timestamp, thermal_params)
            
            # Generate quality map
            quality_map = self.generate_dic_quality_map(U, V, temperature_field)
            
            # Create DIC frame
            dic_frame = DICFrame(
                timestamp=timestamp,
                frame_id=i,
                displacement_u=U,
                displacement_v=V,
                displacement_w=W,
                strain_xx=strains['strain_xx'],
                strain_yy=strains['strain_yy'],
                strain_xy=strains['strain_xy'],
                strain_principal_max=strains['strain_principal_max'],
                strain_principal_min=strains['strain_principal_min'],
                temperature_field=temperature_field,
                quality_map=quality_map
            )
            
            self.dic_frames.append(dic_frame)
        
        # Generate furnace control data
        print("Generating furnace control data...")
        for i, timestamp in enumerate(furnace_times):
            if i % 100 == 0:
                print(f"  Furnace state {i}/{len(furnace_times)} ({100*i/len(furnace_times):.1f}%)")
            
            thermal_params = self.simulate_thermal_cycle(timestamp / 3600)
            furnace_state = self.generate_furnace_state(timestamp, thermal_params)
            self.furnace_states.append(furnace_state)
        
        # Generate RL training data
        print("Generating RL training data...")
        
        # Synchronize DIC and furnace data for RL states
        for i, furnace_state in enumerate(self.furnace_states[:-1]):  # Exclude last to have next_state
            if i % 100 == 0:
                print(f"  RL tuple {i}/{len(self.furnace_states)-1} ({100*i/(len(self.furnace_states)-1):.1f}%)")
            
            # Find closest DIC frame
            timestamp = furnace_state.timestamp
            dic_idx = int(timestamp * self.sample_rate_hz)
            if dic_idx < len(self.dic_frames):
                dic_frame = self.dic_frames[dic_idx]
                
                # Calculate current state
                current_state = self.calculate_rl_state(dic_frame, furnace_state, timestamp)
                self.rl_states.append(current_state)
                
                # Generate action
                action = self.generate_rl_action(current_state, timestamp)
                self.rl_actions.append(action)
                
                # Calculate next state and reward
                if i < len(self.furnace_states) - 2:
                    next_furnace_state = self.furnace_states[i + 1]
                    next_dic_idx = int(next_furnace_state.timestamp * self.sample_rate_hz)
                    if next_dic_idx < len(self.dic_frames):
                        next_dic_frame = self.dic_frames[next_dic_idx]
                        next_state = self.calculate_rl_state(next_dic_frame, next_furnace_state, 
                                                           next_furnace_state.timestamp)
                        
                        # Calculate reward
                        reward = self.calculate_reward(current_state, action, next_state)
                        self.rl_rewards.append(reward)
        
        print("Dataset generation complete!")
        print(f"Generated {len(self.dic_frames)} DIC frames")
        print(f"Generated {len(self.furnace_states)} furnace states") 
        print(f"Generated {len(self.rl_states)} RL states")
        print(f"Generated {len(self.rl_actions)} RL actions")
        print(f"Generated {len(self.rl_rewards)} RL rewards")
    
    def save_dataset(self):
        """Save the complete dataset in multiple formats"""
        print("Saving dataset...")
        
        # Create subdirectories
        (self.output_dir / "dic_data").mkdir(exist_ok=True)
        (self.output_dir / "furnace_data").mkdir(exist_ok=True)
        (self.output_dir / "rl_data").mkdir(exist_ok=True)
        (self.output_dir / "raw_images").mkdir(exist_ok=True)
        (self.output_dir / "metadata").mkdir(exist_ok=True)
        
        # Save DIC data in HDF5 format (efficient for large arrays)
        print("Saving DIC data...")
        with h5py.File(self.output_dir / "dic_data" / "dic_dataset.h5", 'w') as f:
            # Create groups
            displacement_group = f.create_group('displacements')
            strain_group = f.create_group('strains')
            temperature_group = f.create_group('temperatures')
            quality_group = f.create_group('quality')
            metadata_group = f.create_group('metadata')
            
            # Stack all frames into arrays
            timestamps = [frame.timestamp for frame in self.dic_frames]
            frame_ids = [frame.frame_id for frame in self.dic_frames]
            
            # Displacement arrays
            U_stack = np.stack([frame.displacement_u for frame in self.dic_frames])
            V_stack = np.stack([frame.displacement_v for frame in self.dic_frames])
            W_stack = np.stack([frame.displacement_w for frame in self.dic_frames])
            
            displacement_group.create_dataset('U', data=U_stack, compression='gzip')
            displacement_group.create_dataset('V', data=V_stack, compression='gzip')
            displacement_group.create_dataset('W', data=W_stack, compression='gzip')
            
            # Strain arrays
            strain_xx_stack = np.stack([frame.strain_xx for frame in self.dic_frames])
            strain_yy_stack = np.stack([frame.strain_yy for frame in self.dic_frames])
            strain_xy_stack = np.stack([frame.strain_xy for frame in self.dic_frames])
            strain_max_stack = np.stack([frame.strain_principal_max for frame in self.dic_frames])
            strain_min_stack = np.stack([frame.strain_principal_min for frame in self.dic_frames])
            
            strain_group.create_dataset('strain_xx', data=strain_xx_stack, compression='gzip')
            strain_group.create_dataset('strain_yy', data=strain_yy_stack, compression='gzip')
            strain_group.create_dataset('strain_xy', data=strain_xy_stack, compression='gzip')
            strain_group.create_dataset('strain_principal_max', data=strain_max_stack, compression='gzip')
            strain_group.create_dataset('strain_principal_min', data=strain_min_stack, compression='gzip')
            
            # Temperature and quality
            temp_stack = np.stack([frame.temperature_field for frame in self.dic_frames])
            quality_stack = np.stack([frame.quality_map for frame in self.dic_frames])
            
            temperature_group.create_dataset('temperature_field', data=temp_stack, compression='gzip')
            quality_group.create_dataset('quality_map', data=quality_stack, compression='gzip')
            
            # Metadata
            metadata_group.create_dataset('timestamps', data=timestamps)
            metadata_group.create_dataset('frame_ids', data=frame_ids)
            metadata_group.attrs['sample_rate_hz'] = self.sample_rate_hz
            metadata_group.attrs['image_width'] = self.image_width
            metadata_group.attrs['image_height'] = self.image_height
            metadata_group.attrs['sample_size_mm'] = self.sample_size_mm
        
        # Save furnace data as CSV and pickle
        print("Saving furnace data...")
        furnace_df_data = []
        for state in self.furnace_states:
            row = {
                'timestamp': state.timestamp,
                'pressure': state.pressure
            }
            # Add zone data
            for i, (temp, setpoint, power) in enumerate(zip(state.zone_temperatures, 
                                                          state.zone_setpoints, 
                                                          state.zone_powers)):
                row[f'zone_{i}_temperature'] = temp
                row[f'zone_{i}_setpoint'] = setpoint
                row[f'zone_{i}_power'] = power
            
            # Add gas flows
            for i, flow in enumerate(state.gas_flow_rates):
                row[f'gas_flow_{i}'] = flow
            
            # Add atmosphere composition
            for gas, percentage in state.atmosphere_composition.items():
                row[f'atmosphere_{gas}'] = percentage
                
            furnace_df_data.append(row)
        
        furnace_df = pd.DataFrame(furnace_df_data)
        furnace_df.to_csv(self.output_dir / "furnace_data" / "furnace_states.csv", index=False)
        
        # Save detailed furnace data as pickle
        with open(self.output_dir / "furnace_data" / "furnace_states.pkl", 'wb') as f:
            pickle.dump(self.furnace_states, f)
        
        # Save RL training data
        print("Saving RL training data...")
        
        # States
        rl_states_df = pd.DataFrame([asdict(state) for state in self.rl_states])
        rl_states_df.to_csv(self.output_dir / "rl_data" / "rl_states.csv", index=False)
        
        # Actions  
        rl_actions_data = []
        for action in self.rl_actions:
            row = {'timestamp': action.timestamp}
            for i, change in enumerate(action.zone_temp_changes):
                row[f'zone_{i}_temp_change'] = change
            for i, change in enumerate(action.power_adjustments):
                row[f'zone_{i}_power_change'] = change
            for i, change in enumerate(action.gas_flow_changes):
                row[f'gas_{i}_flow_change'] = change
            rl_actions_data.append(row)
        
        rl_actions_df = pd.DataFrame(rl_actions_data)
        rl_actions_df.to_csv(self.output_dir / "rl_data" / "rl_actions.csv", index=False)
        
        # Rewards
        rl_rewards_df = pd.DataFrame([asdict(reward) for reward in self.rl_rewards])
        rl_rewards_df.to_csv(self.output_dir / "rl_data" / "rl_rewards.csv", index=False)
        
        # Create state-action-reward-next_state tuples for RL training
        rl_tuples = []
        for i in range(len(self.rl_states) - 1):
            if i < len(self.rl_actions) and i < len(self.rl_rewards):
                tuple_data = {
                    'state': asdict(self.rl_states[i]),
                    'action': asdict(self.rl_actions[i]),
                    'reward': self.rl_rewards[i].total_reward,
                    'next_state': asdict(self.rl_states[i + 1]) if i + 1 < len(self.rl_states) else None,
                    'done': i + 1 >= len(self.rl_states) - 1
                }
                rl_tuples.append(tuple_data)
        
        with open(self.output_dir / "rl_data" / "rl_tuples.pkl", 'wb') as f:
            pickle.dump(rl_tuples, f)
        
        # Save sample raw images (speckle patterns with deformation)
        print("Saving sample raw images...")
        speckle_base = self.generate_speckle_pattern()
        
        # Save a few deformed images at different time points
        sample_indices = [0, len(self.dic_frames)//4, len(self.dic_frames)//2, 
                         3*len(self.dic_frames)//4, len(self.dic_frames)-1]
        
        for idx in sample_indices:
            if idx < len(self.dic_frames):
                frame = self.dic_frames[idx]
                
                # Create deformed speckle pattern
                y_coords, x_coords = np.mgrid[0:self.image_height, 0:self.image_width]
                
                # Apply displacement (simplified warping)
                scale_factor = 10  # Amplify displacement for visibility
                x_new = x_coords + scale_factor * frame.displacement_u
                y_new = y_coords + scale_factor * frame.displacement_v
                
                # Ensure coordinates are within bounds
                x_new = np.clip(x_new, 0, self.image_width - 1)
                y_new = np.clip(y_new, 0, self.image_height - 1)
                
                # Interpolate to get deformed image
                deformed_image = cv2.remap(speckle_base, x_new.astype(np.float32), 
                                         y_new.astype(np.float32), cv2.INTER_LINEAR)
                
                # Add temperature-based intensity changes
                temp_effect = (frame.temperature_field - 20) / 1580  # Normalize temperature
                intensity_change = 30 * temp_effect  # ±30 intensity units
                deformed_image = np.clip(deformed_image.astype(float) + intensity_change, 0, 255).astype(np.uint8)
                
                # Save both cameras (stereo setup)
                cv2.imwrite(str(self.output_dir / "raw_images" / f"camera_0_frame_{idx:06d}.png"), 
                           deformed_image)
                
                # Second camera with slight perspective difference
                M = cv2.getRotationMatrix2D((self.image_width/2, self.image_height/2), 0.5, 1.0)
                camera2_image = cv2.warpAffine(deformed_image, M, (self.image_width, self.image_height))
                cv2.imwrite(str(self.output_dir / "raw_images" / f"camera_1_frame_{idx:06d}.png"), 
                           camera2_image)
        
        # Save metadata and documentation
        print("Saving metadata...")
        metadata = {
            'dataset_info': {
                'generation_date': datetime.now().isoformat(),
                'duration_hours': self.duration_hours,
                'dic_sample_rate_hz': self.sample_rate_hz,
                'furnace_sample_rate_hz': self.furnace_rate_hz,
                'total_dic_frames': len(self.dic_frames),
                'total_furnace_states': len(self.furnace_states),
                'total_rl_tuples': len(rl_tuples)
            },
            'physical_parameters': {
                'sample_size_mm': self.sample_size_mm,
                'max_temperature_C': self.max_temperature,
                'target_density': self.target_density,
                'num_furnace_zones': self.num_zones,
                'num_cameras': self.num_cameras
            },
            'rl_parameters': {
                'reward_weights': self.reward_weights,
                'state_dimensions': len(asdict(self.rl_states[0])) if self.rl_states else 0,
                'action_dimensions': len(self.rl_actions[0].zone_temp_changes) + len(self.rl_actions[0].power_adjustments) + len(self.rl_actions[0].gas_flow_changes) if self.rl_actions else 0
            },
            'data_formats': {
                'dic_data': 'HDF5 format with compression',
                'furnace_data': 'CSV and pickle formats',
                'rl_data': 'CSV for individual components, pickle for tuples',
                'raw_images': 'PNG format, stereo camera setup'
            }
        }
        
        with open(self.output_dir / "metadata" / "dataset_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Dataset saved to {self.output_dir}")
        print("Dataset structure:")
        print("├── dic_data/")
        print("│   └── dic_dataset.h5")
        print("├── furnace_data/")
        print("│   ├── furnace_states.csv")
        print("│   └── furnace_states.pkl")
        print("├── rl_data/")
        print("│   ├── rl_states.csv")
        print("│   ├── rl_actions.csv")
        print("│   ├── rl_rewards.csv")
        print("│   └── rl_tuples.pkl")
        print("├── raw_images/")
        print("│   ├── camera_0_frame_*.png")
        print("│   └── camera_1_frame_*.png")
        print("└── metadata/")
        print("    └── dataset_metadata.json")

def main():
    """Main function to generate the complete dataset"""
    print("=== Real-Time Training & Validation Dataset Generator ===")
    print("Phase 2: Core Real-Time Training & Validation Data")
    print()
    
    # Create generator
    generator = RealTimeDatasetGenerator(output_dir="realtime_training_dataset")
    
    # Generate complete dataset
    generator.generate_complete_dataset()
    
    # Save dataset
    generator.save_dataset()
    
    print("\n=== Dataset Generation Complete ===")
    print("The dataset includes:")
    print("1. High-frequency DIC data stream (100Hz)")
    print("2. Synchronized furnace control & sensor data (10Hz)")
    print("3. Complete RL state-action-reward-next_state tuples")
    print("4. Raw stereo camera images with realistic deformation")
    print("5. Comprehensive metadata and documentation")
    print("\nReady for Digital Twin and RL agent training!")

if __name__ == "__main__":
    main()