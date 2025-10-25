#!/usr/bin/env python3
"""
Advanced Data Generation Module
Generates highly realistic and complex datasets for Digital Twin training
"""

import numpy as np
import cv2
from scipy import signal, interpolate
from scipy.spatial.distance import cdist
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json
import os
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class AdvancedDICGenerator:
    """Advanced DIC data generator with realistic physics"""
    
    def __init__(self, width=1920, height=1080, fps=120, duration_hours=8):
        self.width = width
        self.height = height
        self.fps = fps
        self.duration_hours = duration_hours
        self.total_frames = int(fps * duration_hours * 3600)
        self.dt = 1.0 / fps
        
        # Material properties
        self.youngs_modulus = 200e9  # Pa
        self.poisson_ratio = 0.3
        self.thermal_expansion = 12e-6  # 1/K
        self.density = 7850  # kg/m³
        
        # Sample geometry
        self.sample_width = 0.1  # meters
        self.sample_height = 0.1
        self.sample_thickness = 0.005  # 5mm
        self.pixel_size = self.sample_width / width
        
        # Advanced speckle pattern
        self.speckle_density = 0.4
        self.speckle_size_range = (3, 12)
        self.speckle_intensity_range = (0.2, 0.8)
        
    def generate_advanced_speckle_pattern(self) -> np.ndarray:
        """Generate high-temperature resistant speckle pattern with realistic features"""
        # Create base pattern with multiple layers
        base_pattern = np.zeros((self.height, self.width), dtype=np.float32)
        
        # Layer 1: Fine speckles for high resolution
        for _ in range(int(self.speckle_density * self.width * self.height / 100)):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            size = np.random.randint(2, 6)
            intensity = np.random.uniform(*self.speckle_intensity_range)
            cv2.circle(base_pattern, (x, y), size, intensity, -1)
        
        # Layer 2: Medium speckles for robustness
        for _ in range(int(self.speckle_density * self.width * self.height / 200)):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            size = np.random.randint(6, 15)
            intensity = np.random.uniform(*self.speckle_intensity_range)
            cv2.circle(base_pattern, (x, y), size, intensity, -1)
        
        # Layer 3: Large features for tracking
        for _ in range(int(self.speckle_density * self.width * self.height / 500)):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            size = np.random.randint(15, 30)
            intensity = np.random.uniform(*self.speckle_intensity_range)
            cv2.circle(base_pattern, (x, y), size, intensity, -1)
        
        # Add noise and texture
        noise = np.random.normal(0, 0.05, base_pattern.shape)
        base_pattern = np.clip(base_pattern + noise, 0, 1)
        
        # Convert to uint8
        return (base_pattern * 255).astype(np.uint8)
    
    def generate_thermal_stress_field(self, t: float, x: np.ndarray, y: np.ndarray) -> Dict[str, np.ndarray]:
        """Generate realistic thermal stress field with material properties"""
        # Temperature field (non-uniform heating)
        T_ref = 25.0
        T_center = T_ref + 200.0 * np.sin(2 * np.pi * t / 3600.0) + 50.0 * np.sin(2 * np.pi * t / 1800.0)
        T_edge = T_ref + 100.0 * np.sin(2 * np.pi * t / 3600.0 + np.pi/4)
        
        # Radial temperature distribution
        r = np.sqrt((x - 0.5)**2 + (y - 0.5)**2)
        T_field = T_center * np.exp(-r**2 / 0.2) + T_edge * (1 - np.exp(-r**2 / 0.2))
        
        # Add thermal gradients
        T_field += 20.0 * np.sin(10 * x) * np.cos(8 * y) * np.sin(t / 200.0)
        T_field += 15.0 * np.cos(12 * x) * np.sin(6 * y) * np.cos(t / 300.0)
        
        # Calculate thermal expansion
        dT = T_field - T_ref
        thermal_strain = self.thermal_expansion * dT
        
        # Calculate displacement field (simplified elasticity)
        # Assume plane stress condition
        u = thermal_strain * (x - 0.5) * self.sample_width * 1000  # Convert to pixels
        v = thermal_strain * (y - 0.5) * self.sample_height * 1000
        
        # Add mechanical constraints (clamped edges)
        edge_mask = (x < 0.1) | (x > 0.9) | (y < 0.1) | (y > 0.9)
        u[edge_mask] *= 0.1  # Reduced displacement at edges
        v[edge_mask] *= 0.1
        
        # Add out-of-plane displacement (warping)
        w = 0.1 * thermal_strain * np.sin(np.pi * x) * np.sin(np.pi * y) * 1000
        
        return {
            'u': u,
            'v': v,
            'w': w,
            'temperature': T_field,
            'thermal_strain': thermal_strain
        }
    
    def calculate_advanced_strain_field(self, u: np.ndarray, v: np.ndarray, w: np.ndarray) -> Dict[str, np.ndarray]:
        """Calculate advanced strain field with all components"""
        # Create coordinate grids
        x = np.linspace(0, 1, u.shape[1])
        y = np.linspace(0, 1, u.shape[0])
        X, Y = np.meshgrid(x, y)
        
        # Calculate strain components using finite differences
        du_dx = np.gradient(u, axis=1) / self.pixel_size
        du_dy = np.gradient(u, axis=0) / self.pixel_size
        dv_dx = np.gradient(v, axis=1) / self.pixel_size
        dv_dy = np.gradient(v, axis=0) / self.pixel_size
        dw_dx = np.gradient(w, axis=1) / self.pixel_size
        dw_dy = np.gradient(w, axis=0) / self.pixel_size
        
        # In-plane strain components
        exx = du_dx
        eyy = dv_dy
        exy = 0.5 * (du_dy + dv_dx)
        
        # Out-of-plane strain components
        exz = 0.5 * dw_dx
        eyz = 0.5 * dw_dy
        ezz = -self.poisson_ratio / (1 - self.poisson_ratio) * (exx + eyy)
        
        # Principal strains
        # 3D strain tensor
        strain_tensor = np.zeros((u.shape[0], u.shape[1], 3, 3))
        strain_tensor[:, :, 0, 0] = exx
        strain_tensor[:, :, 1, 1] = eyy
        strain_tensor[:, :, 2, 2] = ezz
        strain_tensor[:, :, 0, 1] = strain_tensor[:, :, 1, 0] = exy
        strain_tensor[:, :, 0, 2] = strain_tensor[:, :, 2, 0] = exz
        strain_tensor[:, :, 1, 2] = strain_tensor[:, :, 2, 1] = eyz
        
        # Calculate principal strains
        eigenvals = np.linalg.eigvals(strain_tensor)
        eigenvals_sorted = np.sort(eigenvals, axis=-1)
        
        max_principal = eigenvals_sorted[:, :, 2]
        min_principal = eigenvals_sorted[:, :, 0]
        mid_principal = eigenvals_sorted[:, :, 1]
        
        # Von Mises equivalent strain
        von_mises = np.sqrt(0.5 * ((exx - eyy)**2 + (eyy - ezz)**2 + (ezz - exx)**2 + 
                                   6 * (exy**2 + exz**2 + eyz**2)))
        
        # Maximum shear strain
        max_shear = (max_principal - min_principal) / 2
        
        # Strain invariants
        I1 = exx + eyy + ezz
        I2 = exx * eyy + eyy * ezz + ezz * exx - exy**2 - exz**2 - eyz**2
        I3 = exx * eyy * ezz + 2 * exy * exz * eyz - exx * eyz**2 - eyy * exz**2 - ezz * exy**2
        
        return {
            'exx': exx, 'eyy': eyy, 'exy': exy,
            'exz': exz, 'eyz': eyz, 'ezz': ezz,
            'max_principal': max_principal,
            'mid_principal': mid_principal,
            'min_principal': min_principal,
            'von_mises': von_mises,
            'max_shear': max_shear,
            'I1': I1, 'I2': I2, 'I3': I3,
            'trace': I1
        }
    
    def generate_advanced_dic_stream(self) -> Tuple[List[np.ndarray], List[Dict]]:
        """Generate advanced DIC video stream with realistic physics"""
        print("Generating advanced DIC video stream...")
        
        # Generate advanced speckle pattern
        base_pattern = self.generate_advanced_speckle_pattern()
        
        # Generate coordinate grids
        x = np.linspace(0, 1, self.width)
        y = np.linspace(0, 1, self.height)
        X, Y = np.meshgrid(x, y)
        
        frames = []
        metadata = []
        
        for frame_idx in range(self.total_frames):
            t = frame_idx * self.dt
            
            # Generate thermal stress field
            stress_field = self.generate_thermal_stress_field(t, X, Y)
            u, v, w = stress_field['u'], stress_field['v'], stress_field['w']
            
            # Generate deformed pattern
            frame = self.apply_advanced_displacement(base_pattern, u, v, w)
            frames.append(frame)
            
            # Calculate advanced strain field
            strain_field = self.calculate_advanced_strain_field(u, v, w)
            
            # Calculate additional metrics
            curvature = self.calculate_advanced_curvature(u, v, w)
            stress_field_calc = self.calculate_stress_field(strain_field)
            
            # Store comprehensive metadata
            metadata.append({
                'timestamp': t,
                'frame_idx': frame_idx,
                'displacement': {'u': u, 'v': v, 'w': w},
                'strain': strain_field,
                'stress': stress_field_calc,
                'temperature': stress_field['temperature'],
                'max_principal_strain': np.max(strain_field['max_principal']),
                'strain_heterogeneity': np.std(strain_field['max_principal']),
                'max_von_mises': np.max(strain_field['von_mises']),
                'max_shear': np.max(strain_field['max_shear']),
                'sample_curvature': curvature,
                'stress_intensity': np.max(stress_field_calc['von_mises_stress']),
                'thermal_gradient': np.max(np.gradient(stress_field['temperature']))
            })
            
            if frame_idx % 1000 == 0:
                print(f"Generated {frame_idx}/{self.total_frames} frames")
        
        return frames, metadata
    
    def apply_advanced_displacement(self, base_pattern: np.ndarray, u: np.ndarray, v: np.ndarray, w: np.ndarray) -> np.ndarray:
        """Apply 3D displacement field to base pattern"""
        h, w = base_pattern.shape
        x, y = np.meshgrid(np.arange(w), np.arange(h))
        
        # Apply displacement with perspective correction
        x_new = x + u
        y_new = y + v
        
        # Add perspective effect from out-of-plane displacement
        z_factor = 1.0 + w / 1000.0  # Perspective scaling
        x_new *= z_factor
        y_new *= z_factor
        
        # Ensure coordinates are within bounds
        x_new = np.clip(x_new, 0, w-1)
        y_new = np.clip(y_new, 0, h-1)
        
        # Interpolate with higher order
        from scipy.interpolate import griddata
        points = np.column_stack((x.ravel(), y.ravel()))
        values = base_pattern.ravel()
        xi = np.column_stack((x_new.ravel(), y_new.ravel()))
        
        deformed = griddata(points, values, xi, method='cubic', fill_value=0)
        return deformed.reshape(h, w).astype(np.uint8)
    
    def calculate_advanced_curvature(self, u: np.ndarray, v: np.ndarray, w: np.ndarray) -> Dict[str, float]:
        """Calculate advanced curvature metrics"""
        # Calculate second derivatives
        d2u_dx2 = np.gradient(np.gradient(u, axis=1), axis=1)
        d2u_dy2 = np.gradient(np.gradient(u, axis=0), axis=0)
        d2v_dx2 = np.gradient(np.gradient(v, axis=1), axis=1)
        d2v_dy2 = np.gradient(np.gradient(v, axis=0), axis=0)
        d2w_dx2 = np.gradient(np.gradient(w, axis=1), axis=1)
        d2w_dy2 = np.gradient(np.gradient(w, axis=0), axis=0)
        
        # Mean curvature
        mean_curvature = np.mean(d2u_dx2 + d2v_dy2)
        
        # Gaussian curvature
        gaussian_curvature = np.mean(d2u_dx2 * d2v_dy2 - d2u_dy2 * d2v_dx2)
        
        # Maximum curvature
        max_curvature = np.max(np.abs(d2w_dx2 + d2w_dy2))
        
        return {
            'mean': mean_curvature,
            'gaussian': gaussian_curvature,
            'max': max_curvature
        }
    
    def calculate_stress_field(self, strain_field: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Calculate stress field from strain field using Hooke's law"""
        E = self.youngs_modulus
        nu = self.poisson_ratio
        
        # Plane stress condition
        exx = strain_field['exx']
        eyy = strain_field['eyy']
        exy = strain_field['exy']
        
        # Stress components
        sxx = E / (1 - nu**2) * (exx + nu * eyy)
        syy = E / (1 - nu**2) * (eyy + nu * exx)
        sxy = E / (1 + nu) * exy
        
        # Principal stresses
        trace = sxx + syy
        det = sxx * syy - sxy**2
        eigenvals = 0.5 * (trace + np.sqrt(trace**2 - 4 * det))
        eigenvals2 = 0.5 * (trace - np.sqrt(trace**2 - 4 * det))
        
        max_principal_stress = np.maximum(eigenvals, eigenvals2)
        min_principal_stress = np.minimum(eigenvals, eigenvals2)
        
        # Von Mises stress
        von_mises_stress = np.sqrt(0.5 * ((sxx - syy)**2 + syy**2 + sxx**2 + 6 * sxy**2))
        
        return {
            'sxx': sxx,
            'syy': syy,
            'sxy': sxy,
            'max_principal': max_principal_stress,
            'min_principal': min_principal_stress,
            'von_mises_stress': von_mises_stress
        }

class AdvancedFurnaceGenerator:
    """Advanced furnace control and sensor data generator"""
    
    def __init__(self, duration_hours=8, sampling_rate=1.0):
        self.duration_hours = duration_hours
        self.sampling_rate = sampling_rate
        self.total_samples = int(sampling_rate * duration_hours * 3600)
        self.dt = 1.0 / sampling_rate
        
        # Advanced furnace configuration
        self.num_zones = 6  # More zones for better control
        self.num_thermocouples = 12  # More sensors
        self.num_gas_sensors = 5
        self.num_pressure_sensors = 3
        
        # Control parameters
        self.max_power = 150.0  # kW
        self.max_temp = 1800.0  # °C
        self.temp_ramp_rate = 10.0  # °C/min
        
        # PID controller parameters
        self.kp = 0.5
        self.ki = 0.1
        self.kd = 0.05
        
    def generate_advanced_control_sequence(self) -> Dict[str, np.ndarray]:
        """Generate advanced furnace control sequence with PID control"""
        print("Generating advanced furnace control sequence...")
        
        times = np.arange(self.total_samples) * self.dt
        
        # Generate complex temperature profiles
        setpoints = {}
        for zone in range(self.num_zones):
            # Different heating profiles for each zone
            if zone == 0:  # Center zone - aggressive heating
                base_temp = 25 + 100 * np.sin(2 * np.pi * times / 3600.0)
                ramp = np.linspace(0, 300, len(times))
                oscillation = 20 * np.sin(2 * np.pi * times / 1800.0)
                setpoints[f'zone_{zone}_setpoint'] = base_temp + ramp + oscillation
            elif zone == 1:  # Edge zone - moderate heating
                base_temp = 25 + 60 * np.sin(2 * np.pi * times / 3600.0 + np.pi/4)
                ramp = np.linspace(0, 200, len(times))
                oscillation = 15 * np.sin(2 * np.pi * times / 1800.0 + np.pi/2)
                setpoints[f'zone_{zone}_setpoint'] = base_temp + ramp + oscillation
            elif zone == 2:  # Corner zone - gradual heating
                base_temp = 25 + 40 * np.sin(2 * np.pi * times / 3600.0 + np.pi/2)
                ramp = np.linspace(0, 150, len(times))
                oscillation = 10 * np.sin(2 * np.pi * times / 1800.0 + np.pi)
                setpoints[f'zone_{zone}_setpoint'] = base_temp + ramp + oscillation
            else:  # Other zones - custom profiles
                base_temp = 25 + 30 * np.sin(2 * np.pi * times / 3600.0 + zone * np.pi/3)
                ramp = np.linspace(0, 100, len(times))
                oscillation = 8 * np.sin(2 * np.pi * times / 1800.0 + zone * np.pi/4)
                setpoints[f'zone_{zone}_setpoint'] = base_temp + ramp + oscillation
        
        # Generate PID-controlled power commands
        power_commands = {}
        for zone in range(self.num_zones):
            setpoint = setpoints[f'zone_{zone}_setpoint']
            
            # Simulate current temperature with thermal lag
            current_temp = np.zeros_like(times)
            current_temp[0] = 25.0  # Initial temperature
            
            # PID control
            integral = 0.0
            derivative = 0.0
            prev_error = 0.0
            
            for i in range(1, len(times)):
                # Calculate error
                error = setpoint[i] - current_temp[i-1]
                
                # PID terms
                integral += error * self.dt
                derivative = (error - prev_error) / self.dt
                
                # PID output
                pid_output = self.kp * error + self.ki * integral + self.kd * derivative
                
                # Convert to power (with saturation)
                power = np.clip(pid_output * 0.1, 0, self.max_power)
                
                # Add control noise
                power += 2.0 * np.random.randn()
                power = np.clip(power, 0, self.max_power)
                
                power_commands[f'zone_{zone}_power'] = power
                
                # Update temperature with thermal response
                tau = 60.0 + 20.0 * np.random.randn()  # Time constant
                current_temp[i] = current_temp[i-1] + self.dt/tau * (setpoint[i] - current_temp[i-1])
                
                prev_error = error
        
        # Generate advanced gas flow control
        gas_flows = {}
        gas_types = ['argon', 'nitrogen', 'hydrogen', 'helium', 'carbon_dioxide']
        for i, gas in enumerate(gas_types):
            base_flow = 15.0 + 10.0 * np.sin(2 * np.pi * times / 1800.0 + i * np.pi/5)
            modulation = 5.0 * np.sin(2 * np.pi * times / 900.0 + i * np.pi/3)
            noise = 1.0 * np.random.randn(len(times))
            gas_flows[f'{gas}_flow_rate'] = np.clip(base_flow + modulation + noise, 0, 100.0)
        
        return {
            'times': times,
            'setpoints': setpoints,
            'power_commands': power_commands,
            'gas_flows': gas_flows
        }
    
    def generate_advanced_sensor_data(self, control_data: Dict) -> Dict[str, np.ndarray]:
        """Generate advanced sensor readings with realistic physics"""
        print("Generating advanced sensor data...")
        
        times = control_data['times']
        setpoints = control_data['setpoints']
        power_commands = control_data['power_commands']
        
        # Generate temperature readings with realistic thermal response
        temperatures = {}
        for tc in range(self.num_thermocouples):
            zone = tc % self.num_zones
            setpoint = setpoints[f'zone_{zone}_setpoint']
            power = power_commands[f'zone_{zone}_power']
            
            # Thermal response with multiple time constants
            tau1 = 30.0 + 10.0 * np.random.randn()  # Fast response
            tau2 = 120.0 + 30.0 * np.random.randn()  # Slow response
            delay = 5.0 + 3.0 * np.random.randn()  # Transport delay
            
            # Two-pole thermal response
            temp_response = np.zeros_like(times)
            temp_fast = np.zeros_like(times)
            temp_slow = np.zeros_like(times)
            
            for i in range(1, len(times)):
                if i > delay:
                    dt = times[i] - times[i-1]
                    
                    # Fast response
                    temp_fast[i] = temp_fast[i-1] + dt/tau1 * (setpoint[i] - temp_fast[i-1])
                    
                    # Slow response
                    temp_slow[i] = temp_slow[i-1] + dt/tau2 * (setpoint[i] - temp_slow[i-1])
                    
                    # Combined response
                    temp_response[i] = 0.7 * temp_fast[i] + 0.3 * temp_slow[i]
                else:
                    temp_response[i] = 25.0
            
            # Add sensor noise and drift
            noise = 0.5 * np.random.randn(len(times))
            drift = 0.1 * np.cumsum(np.random.randn(len(times))) * self.dt
            temperatures[f'tc_{tc}'] = temp_response + noise + drift
        
        # Generate atmospheric gas readings with realistic chemistry
        gas_readings = {}
        gas_types = ['oxygen', 'carbon_monoxide', 'water_vapor', 'nitrogen_oxides', 'sulfur_dioxide']
        
        for i, gas in enumerate(gas_types):
            # Base concentration with chemical reactions
            base_concentration = 1.0 + 0.5 * np.sin(2 * np.pi * times / 900.0 + i * np.pi/4)
            
            # Temperature-dependent reactions
            avg_temp = np.mean([temperatures[f'tc_{j}'] for j in range(self.num_thermocouples)], axis=0)
            temp_factor = 1.0 + 0.1 * (avg_temp - 800) / 400.0
            base_concentration *= temp_factor
            
            # Add noise and fluctuations
            noise = 0.05 * np.random.randn(len(times))
            fluctuations = 0.1 * np.sin(2 * np.pi * times / 300.0 + i * np.pi/6)
            
            gas_readings[f'{gas}_concentration'] = np.clip(base_concentration + noise + fluctuations, 0, 20.0)
        
        # Generate pressure readings with realistic dynamics
        pressure = 1.0 + 0.2 * np.sin(2 * np.pi * times / 600.0) + 0.05 * np.random.randn(len(times))
        
        # Generate vibration data
        vibration = {}
        for axis in ['x', 'y', 'z']:
            base_vibration = 0.1 * np.sin(2 * np.pi * times / 0.1)  # 10 Hz base
            harmonics = 0.05 * np.sin(2 * np.pi * times / 0.05) + 0.02 * np.sin(2 * np.pi * times / 0.02)
            noise = 0.01 * np.random.randn(len(times))
            vibration[f'{axis}_acceleration'] = base_vibration + harmonics + noise
        
        return {
            'times': times,
            'temperatures': temperatures,
            'gas_readings': gas_readings,
            'pressure': pressure,
            'vibration': vibration
        }

class AdvancedRLGenerator:
    """Advanced RL state generator with sophisticated reward functions"""
    
    def __init__(self, dic_data: Tuple, furnace_data: Tuple):
        self.dic_metadata = dic_data[1]
        self.furnace_control = furnace_data[0]
        self.furnace_sensors = furnace_data[1]
        
        # Advanced reward function weights
        self.weights = {
            'warpage_rate': 1.0,
            'max_strain': 0.8,
            'density_error': 2.0,
            'temperature_uniformity': 0.5,
            'energy_efficiency': 0.3,
            'process_stability': 0.4
        }
        
        # Process targets
        self.target_density = 0.95
        self.target_temperature_uniformity = 50.0  # °C
        self.max_allowable_strain = 0.01
        
    def extract_advanced_metrics(self, frame_idx: int) -> Dict[str, float]:
        """Extract advanced metrics for RL state representation"""
        if frame_idx >= len(self.dic_metadata):
            frame_idx = len(self.dic_metadata) - 1
            
        metadata = self.dic_metadata[frame_idx]
        
        # DIC metrics
        max_principal_strain = metadata['max_principal_strain']
        strain_heterogeneity = metadata['strain_heterogeneity']
        max_von_mises = metadata['max_von_mises']
        max_shear = metadata['max_shear']
        curvature = metadata['sample_curvature']
        stress_intensity = metadata['stress_intensity']
        thermal_gradient = metadata['thermal_gradient']
        
        # Thermal metrics
        dic_time = metadata['timestamp']
        furnace_times = self.furnace_sensors['times']
        closest_idx = np.argmin(np.abs(furnace_times - dic_time))
        
        # Temperature statistics
        temps = [self.furnace_sensors['temperatures'][f'tc_{i}'][closest_idx] 
                for i in range(12)]
        avg_temp = np.mean(temps)
        temp_std = np.std(temps)
        temp_range = np.max(temps) - np.min(temps)
        
        # Process metrics
        cycle_time = dic_time / 3600.0
        current_density = self.estimate_advanced_density(max_principal_strain, avg_temp, cycle_time)
        
        # Energy efficiency
        total_power = sum([self.furnace_control['power_commands'][f'zone_{i}'][closest_idx] 
                          for i in range(6)])
        energy_efficiency = 1.0 / (1.0 + total_power / 1000.0)  # Normalized efficiency
        
        # Process stability (inverse of variance)
        process_stability = 1.0 / (1.0 + temp_std / 100.0)
        
        return {
            'max_principal_strain': max_principal_strain,
            'strain_heterogeneity': strain_heterogeneity,
            'max_von_mises': max_von_mises,
            'max_shear': max_shear,
            'curvature': curvature,
            'stress_intensity': stress_intensity,
            'thermal_gradient': thermal_gradient,
            'avg_temperature': avg_temp,
            'temp_std': temp_std,
            'temp_range': temp_range,
            'cycle_time': cycle_time,
            'current_density': current_density,
            'energy_efficiency': energy_efficiency,
            'process_stability': process_stability
        }
    
    def estimate_advanced_density(self, strain: float, temperature: float, time: float) -> float:
        """Advanced density estimation model"""
        # Base density
        base_density = 0.6
        
        # Strain densification (sigmoid function)
        strain_contribution = 0.3 * (1 / (1 + np.exp(-10 * (strain - 0.005))))
        
        # Temperature effect (Arrhenius-like)
        temp_contribution = 0.1 * (1 - np.exp(-(temperature - 800) / 200))
        
        # Time effect (logarithmic)
        time_contribution = 0.05 * np.log(1 + time)
        
        # Interaction effects
        interaction = 0.02 * strain * (temperature - 800) / 1000
        
        density = base_density + strain_contribution + temp_contribution + time_contribution + interaction
        return np.clip(density, 0.0, 1.0)
    
    def calculate_advanced_reward(self, state: Dict[str, float], action: np.ndarray, next_state: Dict[str, float]) -> float:
        """Calculate advanced multi-objective reward function"""
        # Warpage rate (curvature change rate)
        warpage_rate = abs(next_state['curvature'] - state['curvature'])
        
        # Maximum strain penalty
        max_strain_penalty = max(0, next_state['max_principal_strain'] - self.max_allowable_strain)
        
        # Density error
        density_error = (self.target_density - next_state['current_density'])**2
        
        # Temperature uniformity
        temp_uniformity_error = max(0, next_state['temp_range'] - self.target_temperature_uniformity)
        
        # Energy efficiency
        energy_efficiency = next_state['energy_efficiency']
        
        # Process stability
        process_stability = next_state['process_stability']
        
        # Multi-objective reward
        reward = 0.0
        reward -= self.weights['warpage_rate'] * warpage_rate
        reward -= self.weights['max_strain'] * max_strain_penalty
        reward -= self.weights['density_error'] * density_error
        reward -= self.weights['temperature_uniformity'] * temp_uniformity_error
        reward += self.weights['energy_efficiency'] * energy_efficiency
        reward += self.weights['process_stability'] * process_stability
        
        # Bonus for maintaining optimal conditions
        if (next_state['max_principal_strain'] < self.max_allowable_strain and 
            next_state['temp_range'] < self.target_temperature_uniformity and
            next_state['current_density'] > 0.9):
            reward += 1.0
        
        return reward
    
    def generate_advanced_rl_dataset(self) -> List[Dict]:
        """Generate advanced RL dataset with sophisticated state representation"""
        print("Generating advanced RL dataset...")
        
        rl_data = []
        sample_rate = 5  # Higher sampling rate for better resolution
        
        for i in range(0, len(self.dic_metadata) - 1, sample_rate):
            if i + sample_rate >= len(self.dic_metadata):
                break
                
            # Current state
            state = self.extract_advanced_metrics(i)
            
            # Action (furnace control changes)
            action = np.random.randn(6) * 15.0  # 6 zone power changes
            
            # Next state
            next_state = self.extract_advanced_metrics(i + sample_rate)
            
            # Calculate advanced reward
            reward = self.calculate_advanced_reward(state, action, next_state)
            
            # Create advanced state vector
            state_vector = np.array([
                state['max_principal_strain'],
                state['strain_heterogeneity'],
                state['max_von_mises'],
                state['max_shear'],
                state['curvature'],
                state['stress_intensity'],
                state['thermal_gradient'],
                state['avg_temperature'],
                state['temp_std'],
                state['temp_range'],
                state['cycle_time'],
                state['current_density'],
                state['energy_efficiency'],
                state['process_stability']
            ])
            
            next_state_vector = np.array([
                next_state['max_principal_strain'],
                next_state['strain_heterogeneity'],
                next_state['max_von_mises'],
                next_state['max_shear'],
                next_state['curvature'],
                next_state['stress_intensity'],
                next_state['thermal_gradient'],
                next_state['avg_temperature'],
                next_state['temp_std'],
                next_state['temp_range'],
                next_state['cycle_time'],
                next_state['current_density'],
                next_state['energy_efficiency'],
                next_state['process_stability']
            ])
            
            rl_data.append({
                'state': state_vector,
                'action': action,
                'reward': reward,
                'next_state': next_state_vector,
                'timestamp': self.dic_metadata[i]['timestamp'],
                'frame_idx': i,
                'advanced_metrics': {
                    'warpage_rate': abs(next_state['curvature'] - state['curvature']),
                    'density_error': (self.target_density - next_state['current_density'])**2,
                    'temp_uniformity': next_state['temp_range'],
                    'energy_efficiency': next_state['energy_efficiency'],
                    'process_stability': next_state['process_stability']
                }
            })
            
            if i % 1000 == 0:
                print(f"Generated {i}/{len(self.dic_metadata)} advanced RL samples")
        
        return rl_data

def main():
    """Main function to generate the advanced dataset"""
    print("Starting Advanced Real-Time Dataset Generation...")
    print("=" * 60)
    
    # Initialize advanced generators
    dic_generator = AdvancedDICGenerator(duration_hours=8)
    furnace_generator = AdvancedFurnaceGenerator(duration_hours=8)
    
    # Generate advanced DIC data
    print("\n1. Generating Advanced DIC Data Streams...")
    dic_data = dic_generator.generate_advanced_dic_stream()
    
    # Generate advanced furnace data
    print("\n2. Generating Advanced Furnace Control & Sensor Data...")
    furnace_control = furnace_generator.generate_advanced_control_sequence()
    furnace_sensors = furnace_generator.generate_advanced_sensor_data(furnace_control)
    furnace_data = (furnace_control, furnace_sensors)
    
    # Generate advanced RL dataset
    print("\n3. Generating Advanced RL Dataset...")
    rl_generator = AdvancedRLGenerator(dic_data, furnace_data)
    rl_data = rl_generator.generate_advanced_rl_dataset()
    
    print("\n" + "=" * 60)
    print("Advanced Dataset Generation Complete!")
    print(f"Total RL samples: {len(rl_data)}")
    print(f"State dimension: {len(rl_data[0]['state'])}")
    print(f"Action dimension: {len(rl_data[0]['action'])}")
    
    return dic_data, furnace_data, rl_data

if __name__ == "__main__":
    main()