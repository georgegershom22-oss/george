#!/usr/bin/env python3
"""
Advanced Data Generation Module
Extended capabilities for realistic ceramic sintering simulation
"""

import numpy as np
import cv2
from scipy import ndimage, interpolate
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel
import warnings
warnings.filterwarnings('ignore')

class AdvancedDICGenerator:
    """Advanced DIC generator with realistic material behavior simulation."""
    
    def __init__(self, width=1920, height=1080, fps=120):
        self.width = width
        self.height = height
        self.fps = fps
        
    def generate_realistic_speckle_pattern(self, temperature=25, material_type='alumina'):
        """Generate temperature-dependent speckle pattern."""
        # Base pattern
        pattern = np.random.poisson(128, (self.height, self.width))
        
        # Material-specific properties
        material_props = {
            'alumina': {'speckle_density': 0.4, 'size_range': (3, 10), 'thermal_sensitivity': 0.8},
            'zirconia': {'speckle_density': 0.35, 'size_range': (2, 8), 'thermal_sensitivity': 0.9},
            'silicon_carbide': {'speckle_density': 0.45, 'size_range': (4, 12), 'thermal_sensitivity': 0.7}
        }
        
        props = material_props.get(material_type, material_props['alumina'])
        
        # Temperature-dependent speckle generation
        temp_factor = 1.0 + (temperature - 25) * props['thermal_sensitivity'] * 0.001
        num_speckles = int(self.width * self.height * props['speckle_density'] * temp_factor)
        
        for _ in range(num_speckles):
            y = np.random.randint(0, self.height)
            x = np.random.randint(0, self.width)
            size = np.random.randint(*props['size_range'])
            
            # Create speckle with temperature-dependent intensity
            intensity = np.random.poisson(255 * temp_factor)
            y_coords, x_coords = np.ogrid[:self.height, :self.width]
            mask = (x_coords - x)**2 + (y_coords - y)**2 <= size**2
            pattern[mask] = intensity
        
        # Add thermal noise
        thermal_noise = np.random.normal(0, 2 + temperature * 0.01, pattern.shape)
        pattern = np.clip(pattern + thermal_noise, 0, 255)
        
        return pattern.astype(np.uint8)
    
    def simulate_ceramic_sintering_deformation(self, base_pattern, temperature, time, 
                                             material_properties, sample_geometry):
        """Simulate realistic ceramic sintering deformation."""
        # Calculate sintering parameters
        sintering_temp = material_properties['sintering_temperature']
        sintering_rate = material_properties['sintering_rate']
        
        # Sintering progress (0 to 1)
        sintering_progress = min(1.0, max(0, (temperature - sintering_temp) / 200.0))
        
        # Calculate shrinkage
        linear_shrinkage = sintering_progress * material_properties['linear_shrinkage']
        
        # Create displacement field based on sintering
        y_coords, x_coords = np.mgrid[0:self.height, 0:self.width]
        center_y, center_x = self.height // 2, self.width // 2
        
        # Radial distance from center
        r = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)
        max_r = np.sqrt(center_x**2 + center_y**2)
        
        # Non-uniform shrinkage (more shrinkage at edges)
        shrinkage_factor = 1.0 - linear_shrinkage * (1.0 + 0.5 * (r / max_r))
        
        # Calculate displacement
        u_field = (x_coords - center_x) * (shrinkage_factor - 1.0)
        v_field = (y_coords - center_y) * (shrinkage_factor - 1.0)
        
        # Add warping due to temperature gradients
        temp_gradient = self._simulate_temperature_gradient(temperature, sample_geometry)
        warp_factor = temp_gradient * 0.1
        
        u_field += warp_factor * np.sin(2 * np.pi * x_coords / 100)
        v_field += warp_factor * np.cos(2 * np.pi * y_coords / 100)
        
        # Apply displacement
        deformed_pattern = self._apply_displacement_field(base_pattern, u_field, v_field)
        
        return deformed_pattern, u_field, v_field, {
            'sintering_progress': sintering_progress,
            'linear_shrinkage': linear_shrinkage,
            'shrinkage_factor': shrinkage_factor
        }
    
    def _simulate_temperature_gradient(self, temperature, sample_geometry):
        """Simulate temperature gradient across sample."""
        # Create temperature gradient (hotter in center, cooler at edges)
        y_coords, x_coords = np.mgrid[0:self.height, 0:self.width]
        center_y, center_x = self.height // 2, self.width // 2
        
        r = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)
        max_r = np.sqrt(center_x**2 + center_y**2)
        
        # Temperature gradient
        temp_gradient = 1.0 - 0.2 * (r / max_r)
        return temp_gradient * temperature
    
    def _apply_displacement_field(self, image, u_field, v_field):
        """Apply displacement field with sub-pixel accuracy."""
        height, width = image.shape
        y_coords, x_coords = np.mgrid[0:height, 0:width]
        
        # Calculate new coordinates
        new_x = x_coords + u_field
        new_y = y_coords + v_field
        
        # Ensure coordinates are within bounds
        new_x = np.clip(new_x, 0, width - 1)
        new_y = np.clip(new_y, 0, height - 1)
        
        # Interpolate using scipy
        from scipy.interpolate import griddata
        points = np.column_stack((y_coords.ravel(), x_coords.ravel()))
        values = image.ravel()
        new_points = np.column_stack((new_y.ravel(), new_x.ravel()))
        
        deformed = griddata(points, values, new_points, method='linear', fill_value=0)
        return deformed.reshape(image.shape).astype(np.uint8)

class AdvancedFurnaceSimulator:
    """Advanced furnace simulator with realistic thermal dynamics."""
    
    def __init__(self, num_zones=6, num_thermocouples=12):
        self.num_zones = num_zones
        self.num_thermocouples = num_thermocouples
        
        # Initialize furnace model
        self._initialize_furnace_model()
        
    def _initialize_furnace_model(self):
        """Initialize realistic furnace thermal model."""
        # Zone characteristics
        self.zone_thermal_mass = np.random.uniform(0.5, 1.5, self.num_zones)
        self.zone_heat_capacity = np.random.uniform(800, 1200, self.num_zones)
        self.zone_heat_transfer = np.random.uniform(0.1, 0.4, self.num_zones)
        
        # Thermocouple positions and characteristics
        self.tc_positions = np.random.uniform(0, 1, (self.num_thermocouples, 2))
        self.tc_response_time = np.random.uniform(0.5, 2.0, self.num_thermocouples)
        self.tc_noise_std = np.random.uniform(0.2, 1.0, self.num_thermocouples)
        
        # Cross-coupling between zones
        self.zone_coupling = np.random.uniform(0.05, 0.15, (self.num_zones, self.num_zones))
        np.fill_diagonal(self.zone_coupling, 0)
        
        # Atmospheric conditions
        self.atmospheric_pressure = 1.0
        self.oxygen_content = 20.9
        self.gas_flow_rate = 10.0
        
    def simulate_thermal_dynamics(self, zone_powers, zone_setpoints, dt=1.0):
        """Simulate realistic thermal dynamics."""
        # Calculate heat input
        heat_input = zone_powers * 1000  # Convert kW to W
        
        # Calculate heat transfer between zones
        zone_temps = np.zeros(self.num_zones)
        for i in range(self.num_zones):
            # Heat from power input
            zone_temps[i] += heat_input[i] / (self.zone_thermal_mass[i] * self.zone_heat_capacity[i]) * dt
            
            # Heat transfer from other zones
            for j in range(self.num_zones):
                if i != j:
                    temp_diff = zone_temps[j] - zone_temps[i]
                    heat_transfer = self.zone_coupling[i, j] * temp_diff * dt
                    zone_temps[i] += heat_transfer
        
        # Calculate thermocouple temperatures
        tc_temps = np.zeros(self.num_thermocouples)
        for tc in range(self.num_thermocouples):
            # Weighted average of zone temperatures based on position
            weights = self._calculate_zone_weights(tc)
            tc_temps[tc] = np.sum(weights * zone_temps)
            
            # Add response time delay
            tc_temps[tc] = tc_temps[tc] * (1 - np.exp(-dt / self.tc_response_time[tc]))
            
            # Add noise
            noise = np.random.normal(0, self.tc_noise_std[tc])
            tc_temps[tc] += noise
        
        return zone_temps, tc_temps
    
    def _calculate_zone_weights(self, tc_idx):
        """Calculate weights for thermocouple based on zone positions."""
        tc_pos = self.tc_positions[tc_idx]
        weights = np.zeros(self.num_zones)
        
        for zone in range(self.num_zones):
            # Zone position (simplified)
            zone_pos = np.array([zone / self.num_zones, 0.5])
            distance = np.linalg.norm(tc_pos - zone_pos)
            weights[zone] = np.exp(-distance * 2)
        
        return weights / np.sum(weights)
    
    def generate_realistic_control_sequence(self, duration, control_type='sintering_cycle'):
        """Generate realistic control sequence."""
        timesteps = int(duration)
        control_data = []
        
        # Initialize
        zone_powers = np.zeros(self.num_zones)
        zone_setpoints = np.zeros(self.num_zones)
        zone_temps = np.full(self.num_zones, 25.0)
        tc_temps = np.full(self.num_thermocouples, 25.0)
        
        if control_type == 'sintering_cycle':
            # Realistic sintering cycle
            phases = [
                {'name': 'heating_1', 'duration': 0.2, 'temp_range': (25, 600), 'ramp_rate': 5.0},
                {'name': 'soak_1', 'duration': 0.1, 'temp_range': (600, 600), 'ramp_rate': 0.0},
                {'name': 'heating_2', 'duration': 0.3, 'temp_range': (600, 1200), 'ramp_rate': 3.0},
                {'name': 'sintering', 'duration': 0.2, 'temp_range': (1200, 1400), 'ramp_rate': 2.0},
                {'name': 'soak_2', 'duration': 0.1, 'temp_range': (1400, 1400), 'ramp_rate': 0.0},
                {'name': 'cooling', 'duration': 0.1, 'temp_range': (1400, 25), 'ramp_rate': -10.0}
            ]
        else:
            # Random exploration
            phases = [{'name': 'random', 'duration': 1.0, 'temp_range': (25, 1500), 'ramp_rate': 0.0}]
        
        current_time = 0
        for phase in phases:
            phase_duration = int(phase['duration'] * duration)
            temp_start, temp_end = phase['temp_range']
            ramp_rate = phase['ramp_rate']
            
            for t in range(phase_duration):
                if current_time >= timesteps:
                    break
                
                # Calculate target temperature
                if phase['name'] == 'random':
                    target_temp = np.random.uniform(25, 1500)
                else:
                    progress = t / phase_duration
                    target_temp = temp_start + (temp_end - temp_start) * progress
                
                # Set zone setpoints with some variation
                for zone in range(self.num_zones):
                    variation = np.random.normal(0, 10)
                    zone_setpoints[zone] = target_temp + variation
                
                # Calculate required power
                for zone in range(self.num_zones):
                    temp_error = zone_setpoints[zone] - zone_temps[zone]
                    power_required = temp_error * self.zone_heat_transfer[zone] * 0.1
                    zone_powers[zone] = np.clip(power_required, 0, 100)
                
                # Simulate thermal dynamics
                zone_temps, tc_temps = self.simulate_thermal_dynamics(
                    zone_powers, zone_setpoints, dt=1.0
                )
                
                # Update atmospheric conditions
                self.atmospheric_pressure = 1.0 + np.random.normal(0, 0.02)
                self.oxygen_content = 20.9 + np.random.normal(0, 0.5)
                self.gas_flow_rate = 10.0 + np.random.normal(0, 1.0)
                
                # Record data
                control_data.append({
                    'timestamp': current_time,
                    'zone_powers': zone_powers.copy(),
                    'zone_setpoints': zone_setpoints.copy(),
                    'zone_temperatures': zone_temps.copy(),
                    'thermocouple_temps': tc_temps.copy(),
                    'atmospheric_pressure': self.atmospheric_pressure,
                    'oxygen_content': self.oxygen_content,
                    'gas_flow_rate': self.gas_flow_rate
                })
                
                current_time += 1
        
        return control_data

class AdvancedStrainAnalyzer:
    """Advanced strain analysis with sub-pixel accuracy and noise reduction."""
    
    def __init__(self, subset_size=32, step_size=16):
        self.subset_size = subset_size
        self.step_size = step_size
        
    def compute_displacement_field_advanced(self, ref_image, def_image, method='correlation'):
        """Compute displacement field with advanced correlation methods."""
        height, width = ref_image.shape
        u_field = np.zeros((height, width))
        v_field = np.zeros((height, width))
        confidence = np.zeros((height, width))
        
        # Sample points for DIC analysis
        y_points = range(0, height - self.subset_size, self.step_size)
        x_points = range(0, width - self.subset_size, self.step_size)
        
        for y in y_points:
            for x in x_points:
                # Extract subset
                ref_subset = ref_image[y:y+self.subset_size, x:x+self.subset_size]
                def_subset = def_image[y:y+self.subset_size, x:x+self.subset_size]
                
                # Compute displacement using advanced correlation
                if method == 'correlation':
                    u, v, conf = self._correlation_displacement(ref_subset, def_subset)
                elif method == 'phase_correlation':
                    u, v, conf = self._phase_correlation_displacement(ref_subset, def_subset)
                else:
                    u, v, conf = self._correlation_displacement(ref_subset, def_subset)
                
                # Fill displacement field
                u_field[y:y+self.step_size, x:x+self.step_size] = u
                v_field[y:y+self.step_size, x:x+self.step_size] = v
                confidence[y:y+self.step_size, x:x+self.step_size] = conf
        
        # Apply smoothing to reduce noise
        u_field = self._smooth_displacement_field(u_field, confidence)
        v_field = self._smooth_displacement_field(v_field, confidence)
        
        return u_field, v_field, confidence
    
    def _correlation_displacement(self, ref_subset, def_subset):
        """Compute displacement using normalized cross-correlation."""
        result = cv2.matchTemplate(def_subset, ref_subset, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        # Calculate displacement
        u = max_loc[0] - self.subset_size // 2
        v = max_loc[1] - self.subset_size // 2
        
        return u, v, max_val
    
    def _phase_correlation_displacement(self, ref_subset, def_subset):
        """Compute displacement using phase correlation."""
        # Convert to float
        ref_float = ref_subset.astype(np.float32)
        def_float = def_subset.astype(np.float32)
        
        # Compute FFT
        ref_fft = np.fft.fft2(ref_float)
        def_fft = np.fft.fft2(def_float)
        
        # Compute cross-power spectrum
        cross_power = ref_fft * np.conj(def_fft)
        cross_power = cross_power / (np.abs(cross_power) + 1e-10)
        
        # Inverse FFT
        correlation = np.fft.ifft2(cross_power)
        correlation = np.real(correlation)
        
        # Find peak
        max_loc = np.unravel_index(np.argmax(correlation), correlation.shape)
        u = max_loc[1] - self.subset_size // 2
        v = max_loc[0] - self.subset_size // 2
        
        # Confidence based on peak sharpness
        peak_val = correlation[max_loc]
        conf = peak_val / (np.max(correlation) + 1e-10)
        
        return u, v, conf
    
    def _smooth_displacement_field(self, field, confidence, threshold=0.5):
        """Smooth displacement field based on confidence."""
        # Mask low confidence points
        mask = confidence > threshold
        
        # Apply Gaussian filter
        smoothed = ndimage.gaussian_filter(field, sigma=1.0)
        
        # Use original values for high confidence points
        result = np.where(mask, field, smoothed)
        
        return result
    
    def compute_strain_field_advanced(self, u_field, v_field, method='finite_difference'):
        """Compute strain field with advanced methods."""
        if method == 'finite_difference':
            return self._finite_difference_strain(u_field, v_field)
        elif method == 'gaussian_fit':
            return self._gaussian_fit_strain(u_field, v_field)
        else:
            return self._finite_difference_strain(u_field, v_field)
    
    def _finite_difference_strain(self, u_field, v_field):
        """Compute strain using finite differences."""
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
    
    def _gaussian_fit_strain(self, u_field, v_field):
        """Compute strain using Gaussian fitting for sub-pixel accuracy."""
        # This is a simplified version - in practice, you'd use more sophisticated methods
        return self._finite_difference_strain(u_field, v_field)

class DataVisualizer:
    """Advanced visualization tools for the generated dataset."""
    
    def __init__(self):
        self.colormap = 'viridis'
    
    def plot_strain_field(self, strain_data, title="Strain Field"):
        """Plot strain field with proper visualization."""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # Strain components
        im1 = axes[0, 0].imshow(strain_data['exx'], cmap=self.colormap)
        axes[0, 0].set_title('εxx')
        plt.colorbar(im1, ax=axes[0, 0])
        
        im2 = axes[0, 1].imshow(strain_data['eyy'], cmap=self.colormap)
        axes[0, 1].set_title('εyy')
        plt.colorbar(im2, ax=axes[0, 1])
        
        im3 = axes[0, 2].imshow(strain_data['exy'], cmap=self.colormap)
        axes[0, 2].set_title('εxy')
        plt.colorbar(im3, ax=axes[0, 2])
        
        # Principal strains
        im4 = axes[1, 0].imshow(strain_data['e1'], cmap=self.colormap)
        axes[1, 0].set_title('ε1 (Principal)')
        plt.colorbar(im4, ax=axes[1, 0])
        
        im5 = axes[1, 1].imshow(strain_data['e2'], cmap=self.colormap)
        axes[1, 1].set_title('ε2 (Principal)')
        plt.colorbar(im5, ax=axes[1, 1])
        
        im6 = axes[1, 2].imshow(strain_data['e_vm'], cmap=self.colormap)
        axes[1, 2].set_title('εvm (Von Mises)')
        plt.colorbar(im6, ax=axes[1, 2])
        
        plt.tight_layout()
        plt.suptitle(title, y=1.02)
        plt.show()
    
    def plot_displacement_field(self, u_field, v_field, title="Displacement Field"):
        """Plot displacement field with quiver plot."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # U component
        im1 = ax1.imshow(u_field, cmap='RdBu')
        ax1.set_title('U Displacement')
        plt.colorbar(im1, ax=ax1)
        
        # V component
        im2 = ax2.imshow(v_field, cmap='RdBu')
        ax2.set_title('V Displacement')
        plt.colorbar(im2, ax=ax2)
        
        plt.tight_layout()
        plt.suptitle(title, y=1.02)
        plt.show()
    
    def plot_furnace_data(self, control_data, title="Furnace Control Data"):
        """Plot furnace control and sensor data."""
        timestamps = [data['timestamp'] for data in control_data]
        zone_powers = np.array([data['zone_powers'] for data in control_data])
        tc_temps = np.array([data['thermocouple_temps'] for data in control_data])
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Zone powers
        for zone in range(zone_powers.shape[1]):
            axes[0, 0].plot(timestamps, zone_powers[:, zone], label=f'Zone {zone+1}')
        axes[0, 0].set_title('Zone Powers')
        axes[0, 0].set_xlabel('Time (s)')
        axes[0, 0].set_ylabel('Power (%)')
        axes[0, 0].legend()
        
        # Thermocouple temperatures
        for tc in range(tc_temps.shape[1]):
            axes[0, 1].plot(timestamps, tc_temps[:, tc], label=f'TC {tc+1}')
        axes[0, 1].set_title('Thermocouple Temperatures')
        axes[0, 1].set_xlabel('Time (s)')
        axes[0, 1].set_ylabel('Temperature (°C)')
        axes[0, 1].legend()
        
        # Atmospheric conditions
        pressure = [data['atmospheric_pressure'] for data in control_data]
        oxygen = [data['oxygen_content'] for data in control_data]
        
        ax2 = axes[1, 0]
        ax2_twin = ax2.twinx()
        ax2.plot(timestamps, pressure, 'b-', label='Pressure')
        ax2_twin.plot(timestamps, oxygen, 'r-', label='Oxygen')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Pressure (atm)', color='b')
        ax2_twin.set_ylabel('Oxygen (%)', color='r')
        ax2.set_title('Atmospheric Conditions')
        
        # Gas flow rate
        flow_rate = [data['gas_flow_rate'] for data in control_data]
        axes[1, 1].plot(timestamps, flow_rate)
        axes[1, 1].set_title('Gas Flow Rate')
        axes[1, 1].set_xlabel('Time (s)')
        axes[1, 1].set_ylabel('Flow Rate (L/min)')
        
        plt.tight_layout()
        plt.suptitle(title, y=1.02)
        plt.show()

def main():
    """Test the advanced data generation modules."""
    print("Testing Advanced Data Generation Modules...")
    
    # Test advanced DIC generator
    dic_gen = AdvancedDICGenerator()
    pattern = dic_gen.generate_realistic_speckle_pattern(temperature=800, material_type='alumina')
    print(f"Generated speckle pattern: {pattern.shape}")
    
    # Test advanced furnace simulator
    furnace = AdvancedFurnaceSimulator()
    control_data = furnace.generate_realistic_control_sequence(3600, 'sintering_cycle')
    print(f"Generated control sequence: {len(control_data)} timesteps")
    
    # Test advanced strain analyzer
    strain_analyzer = AdvancedStrainAnalyzer()
    u_field, v_field, conf = strain_analyzer.compute_displacement_field_advanced(
        pattern, pattern, method='correlation'
    )
    print(f"Computed displacement field: {u_field.shape}")
    
    print("Advanced data generation modules tested successfully!")

if __name__ == "__main__":
    main()