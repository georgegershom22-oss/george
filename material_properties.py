#!/usr/bin/env python3
"""
Material Properties Utility for Acoustic Transmission Loss Simulations

This utility provides functions for generating and managing material properties
for acoustic simulations, including realistic oceanographic profiles.

Usage:
    python material_properties.py [options]
    
    # Or import as module:
    from material_properties import *
    profile = create_standard_ocean_profile(depth_max=200)

Features:
- Standard oceanographic profiles
- Custom stratification profiles
- Sound speed calculations
- Bulk modulus derivation from sound speed and density
- Export to Abaqus format

Author: Generated for Abaqus Acoustic Simulation
"""

import numpy as np
import matplotlib.pyplot as plt
import json
import argparse
from typing import List, Dict, Tuple, Optional
import math


class AcousticMaterialProperties:
    """
    Class for managing acoustic material properties
    """
    
    def __init__(self):
        self.profiles = {}
        
        # Physical constants
        self.SEAWATER_REFERENCE = {
            'density': 1025.0,      # kg/m³
            'sound_speed': 1500.0,  # m/s
            'bulk_modulus': 2.31e9, # Pa
            'temperature': 15.0,    # °C
            'salinity': 35.0        # psu
        }
    
    def sound_speed_from_bulk_density(self, bulk_modulus: float, density: float) -> float:
        """
        Calculate sound speed from bulk modulus and density
        
        Args:
            bulk_modulus (float): Bulk modulus in Pa
            density (float): Density in kg/m³
            
        Returns:
            float: Sound speed in m/s
        """
        return math.sqrt(bulk_modulus / density)
    
    def bulk_modulus_from_sound_density(self, sound_speed: float, density: float) -> float:
        """
        Calculate bulk modulus from sound speed and density
        
        Args:
            sound_speed (float): Sound speed in m/s
            density (float): Density in kg/m³
            
        Returns:
            float: Bulk modulus in Pa
        """
        return density * sound_speed**2
    
    def mackenzie_sound_speed(self, temperature: float, salinity: float, depth: float) -> float:
        """
        Calculate sound speed using Mackenzie equation
        
        Args:
            temperature (float): Temperature in °C
            salinity (float): Salinity in psu
            depth (float): Depth in meters
            
        Returns:
            float: Sound speed in m/s
        """
        T = temperature
        S = salinity
        D = depth
        
        # Mackenzie equation (1981)
        c = (1448.96 + 4.591*T - 5.304e-2*T**2 + 2.374e-4*T**3 +
             1.340*(S-35) + 1.630e-2*D + 1.675e-7*D**2 -
             1.025e-2*T*(S-35) - 7.139e-13*T*D**3)
        
        return c
    
    def unesco_density(self, temperature: float, salinity: float, pressure: float) -> float:
        """
        Calculate seawater density using UNESCO equation of state
        
        Args:
            temperature (float): Temperature in °C
            salinity (float): Salinity in psu
            pressure (float): Pressure in dbar (approximately depth in meters)
            
        Returns:
            float: Density in kg/m³
        """
        T = temperature
        S = salinity
        P = pressure
        
        # UNESCO equation of state (simplified version)
        # Density at atmospheric pressure
        rho0 = (999.842594 + 6.793952e-2*T - 9.095290e-3*T**2 +
                1.001685e-4*T**3 - 1.120083e-6*T**4 + 6.536332e-9*T**5 +
                (8.24493e-1 - 4.0899e-3*T + 7.6438e-5*T**2 -
                 8.2467e-7*T**3 + 5.3875e-9*T**4)*S +
                (-5.72466e-3 + 1.0227e-4*T - 1.6546e-6*T**2)*S**(3/2) +
                4.8314e-4*S**2)
        
        # Pressure correction (simplified)
        K = (19652.21 + 148.4206*T - 2.327105*T**2 + 1.360477e-2*T**3 -
             5.155288e-5*T**4 + (54.6746 - 0.603459*T + 1.09987e-2*T**2 -
             6.1670e-5*T**3)*S + (7.944e-2 + 1.6483e-2*T - 5.3009e-4*T**2)*S**(3/2))
        
        # Apply pressure correction
        rho = rho0 / (1 - P/K)
        
        return rho
    
    def create_standard_ocean_profile(self, depth_max: float = 200.0, 
                                    num_layers: int = 20) -> Dict:
        """
        Create a standard ocean acoustic profile
        
        Args:
            depth_max (float): Maximum depth in meters
            num_layers (int): Number of layers
            
        Returns:
            dict: Profile data with depths, densities, sound speeds, bulk moduli
        """
        depths = np.linspace(0, depth_max, num_layers + 1)
        
        # Standard ocean temperature profile
        temperatures = []
        for d in depths:
            if d < 20:
                # Surface mixed layer
                T = 20.0
            elif d < 100:
                # Thermocline
                T = 20.0 - 15.0 * (d - 20) / 80.0
            else:
                # Deep water
                T = 5.0 - 3.0 * (d - 100) / (depth_max - 100)
            temperatures.append(max(T, 2.0))  # Minimum 2°C
        
        # Standard salinity (approximately constant)
        salinities = [35.0] * len(depths)
        
        # Calculate properties
        densities = []
        sound_speeds = []
        bulk_moduli = []
        
        for i, (d, T, S) in enumerate(zip(depths, temperatures, salinities)):
            # Pressure approximation (1 dbar ≈ 1 m depth)
            P = d
            
            # Calculate density and sound speed
            rho = self.unesco_density(T, S, P)
            c = self.mackenzie_sound_speed(T, S, d)
            K = self.bulk_modulus_from_sound_density(c, rho)
            
            densities.append(rho)
            sound_speeds.append(c)
            bulk_moduli.append(K)
        
        profile = {
            'name': 'Standard Ocean Profile',
            'depths': depths.tolist(),
            'temperatures': temperatures,
            'salinities': salinities,
            'densities': densities,
            'sound_speeds': sound_speeds,
            'bulk_moduli': bulk_moduli
        }
        
        return profile
    
    def create_layered_profile(self, layer_specs: List[Dict]) -> Dict:
        """
        Create a layered profile from specifications
        
        Args:
            layer_specs (list): List of layer specifications with keys:
                - depth_range: (start, end) depths in meters
                - density: density in kg/m³ (optional)
                - sound_speed: sound speed in m/s (optional)
                - bulk_modulus: bulk modulus in Pa (optional)
                - temperature: temperature in °C (optional)
                - salinity: salinity in psu (optional)
        
        Returns:
            dict: Layered profile data
        """
        layers = []
        
        for i, spec in enumerate(layer_specs):
            depth_start, depth_end = spec['depth_range']
            depth_center = (depth_start + depth_end) / 2
            
            layer = {
                'layer_id': i + 1,
                'depth_range': (depth_start, depth_end),
                'depth_center': depth_center
            }
            
            # Determine properties based on available data
            if 'density' in spec and 'bulk_modulus' in spec:
                layer['density'] = spec['density']
                layer['bulk_modulus'] = spec['bulk_modulus']
                layer['sound_speed'] = self.sound_speed_from_bulk_density(
                    spec['bulk_modulus'], spec['density'])
            
            elif 'density' in spec and 'sound_speed' in spec:
                layer['density'] = spec['density']
                layer['sound_speed'] = spec['sound_speed']
                layer['bulk_modulus'] = self.bulk_modulus_from_sound_density(
                    spec['sound_speed'], spec['density'])
            
            elif 'temperature' in spec and 'salinity' in spec:
                T = spec['temperature']
                S = spec['salinity']
                layer['temperature'] = T
                layer['salinity'] = S
                layer['density'] = self.unesco_density(T, S, depth_center)
                layer['sound_speed'] = self.mackenzie_sound_speed(T, S, depth_center)
                layer['bulk_modulus'] = self.bulk_modulus_from_sound_density(
                    layer['sound_speed'], layer['density'])
            
            else:
                # Use default values with depth variation
                base_density = 1000.0 + 0.15 * depth_center
                base_sound_speed = 1480.0 + 0.1 * depth_center
                layer['density'] = base_density
                layer['sound_speed'] = base_sound_speed
                layer['bulk_modulus'] = self.bulk_modulus_from_sound_density(
                    base_sound_speed, base_density)
            
            layers.append(layer)
        
        profile = {
            'name': 'Layered Profile',
            'type': 'layered',
            'layers': layers
        }
        
        return profile
    
    def create_gradient_profile(self, depth_max: float = 200.0,
                              density_params: Tuple[float, float] = (1000.0, 0.15),
                              sound_speed_params: Tuple[float, float] = (1480.0, 0.1),
                              num_points: int = 50) -> Dict:
        """
        Create a continuous gradient profile
        
        Args:
            depth_max (float): Maximum depth in meters
            density_params (tuple): (base_density, gradient) in kg/m³ and kg/m³/m
            sound_speed_params (tuple): (base_speed, gradient) in m/s and m/s/m
            num_points (int): Number of points for the profile
            
        Returns:
            dict: Gradient profile data
        """
        depths = np.linspace(0, depth_max, num_points)
        
        rho_base, rho_grad = density_params
        c_base, c_grad = sound_speed_params
        
        densities = rho_base + rho_grad * depths
        sound_speeds = c_base + c_grad * depths
        bulk_moduli = [self.bulk_modulus_from_sound_density(c, rho) 
                      for c, rho in zip(sound_speeds, densities)]
        
        profile = {
            'name': 'Gradient Profile',
            'type': 'gradient',
            'depths': depths.tolist(),
            'densities': densities.tolist(),
            'sound_speeds': sound_speeds.tolist(),
            'bulk_moduli': bulk_moduli,
            'density_params': density_params,
            'sound_speed_params': sound_speed_params
        }
        
        return profile
    
    def export_to_abaqus_layered(self, profile: Dict, filename: str = 'materials_layered.inp'):
        """
        Export layered profile to Abaqus input format
        
        Args:
            profile (dict): Layered profile data
            filename (str): Output filename
        """
        with open(filename, 'w') as f:
            f.write("** Acoustic Material Properties - Layered\n")
            f.write("** Generated by material_properties.py\n**\n")
            
            for layer in profile['layers']:
                layer_id = layer['layer_id']
                f.write(f"*Material, name=WATER_LAYER_{layer_id}\n")
                f.write("*Density\n")
                f.write(f"{layer['density']:.3f},\n")
                f.write("*Bulk Modulus\n")
                f.write(f"{layer['bulk_modulus']:.6e},\n")
                f.write("**\n")
        
        print(f"Layered materials exported to: {filename}")
    
    def export_to_abaqus_gradient(self, profile: Dict, filename: str = 'materials_gradient.inp'):
        """
        Export gradient profile to Abaqus input format with field variables
        
        Args:
            profile (dict): Gradient profile data
            filename (str): Output filename
        """
        with open(filename, 'w') as f:
            f.write("** Acoustic Material Properties - Gradient\n")
            f.write("** Generated by material_properties.py\n**\n")
            
            f.write("*Material, name=WATER_GRADIENT\n")
            f.write("*Density, dependencies=1\n")
            
            # Write density table
            for depth, density in zip(profile['depths'], profile['densities']):
                f.write(f"{density:.3f}, {depth:.2f}\n")
            
            f.write("*Bulk Modulus, dependencies=1\n")
            
            # Write bulk modulus table
            for depth, bulk_mod in zip(profile['depths'], profile['bulk_moduli']):
                f.write(f"{bulk_mod:.6e}, {depth:.2f}\n")
            
            f.write("**\n")
            f.write("** Analytical field for depth (F1 = z-coordinate)\n")
            f.write("*Field, name=DEPTH_FIELD\n")
            f.write("*Field Output, variable=COORD\n")
            f.write("**\n")
        
        print(f"Gradient materials exported to: {filename}")
    
    def plot_profile(self, profile: Dict, save_plot: bool = True, 
                    plot_filename: str = 'acoustic_profile.png'):
        """
        Plot acoustic profile
        
        Args:
            profile (dict): Profile data
            save_plot (bool): Whether to save the plot
            plot_filename (str): Plot filename
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("Matplotlib not available for plotting")
            return
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 8))
        
        if profile['type'] == 'layered':
            # Extract data for plotting
            depths = []
            densities = []
            sound_speeds = []
            bulk_moduli = []
            
            for layer in profile['layers']:
                depth_start, depth_end = layer['depth_range']
                depths.extend([depth_start, depth_end])
                densities.extend([layer['density'], layer['density']])
                sound_speeds.extend([layer['sound_speed'], layer['sound_speed']])
                bulk_moduli.extend([layer['bulk_modulus'], layer['bulk_modulus']])
        
        else:  # gradient
            depths = profile['depths']
            densities = profile['densities']
            sound_speeds = profile['sound_speeds']
            bulk_moduli = profile['bulk_moduli']
        
        # Plot density
        axes[0].plot(densities, depths, 'b-', linewidth=2)
        axes[0].set_xlabel('Density (kg/m³)')
        axes[0].set_ylabel('Depth (m)')
        axes[0].set_title('Density Profile')
        axes[0].invert_yaxis()
        axes[0].grid(True, alpha=0.3)
        
        # Plot sound speed
        axes[1].plot(sound_speeds, depths, 'r-', linewidth=2)
        axes[1].set_xlabel('Sound Speed (m/s)')
        axes[1].set_ylabel('Depth (m)')
        axes[1].set_title('Sound Speed Profile')
        axes[1].invert_yaxis()
        axes[1].grid(True, alpha=0.3)
        
        # Plot bulk modulus
        bulk_moduli_gpa = [K/1e9 for K in bulk_moduli]
        axes[2].plot(bulk_moduli_gpa, depths, 'g-', linewidth=2)
        axes[2].set_xlabel('Bulk Modulus (GPa)')
        axes[2].set_ylabel('Depth (m)')
        axes[2].set_title('Bulk Modulus Profile')
        axes[2].invert_yaxis()
        axes[2].grid(True, alpha=0.3)
        
        plt.suptitle(f"Acoustic Profile: {profile['name']}")
        plt.tight_layout()
        
        if save_plot:
            plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
            print(f"Profile plot saved to: {plot_filename}")
        
        plt.show()
    
    def save_profile(self, profile: Dict, filename: str):
        """
        Save profile to JSON file
        
        Args:
            profile (dict): Profile data
            filename (str): JSON filename
        """
        with open(filename, 'w') as f:
            json.dump(profile, f, indent=2)
        print(f"Profile saved to: {filename}")
    
    def load_profile(self, filename: str) -> Dict:
        """
        Load profile from JSON file
        
        Args:
            filename (str): JSON filename
            
        Returns:
            dict: Profile data
        """
        with open(filename, 'r') as f:
            profile = json.load(f)
        print(f"Profile loaded from: {filename}")
        return profile


def create_example_profiles():
    """Create example profiles for demonstration"""
    props = AcousticMaterialProperties()
    
    # Standard ocean profile
    ocean_profile = props.create_standard_ocean_profile(depth_max=200, num_layers=20)
    props.save_profile(ocean_profile, 'standard_ocean_profile.json')
    props.plot_profile(ocean_profile, plot_filename='standard_ocean_profile.png')
    
    # Layered profile
    layer_specs = [
        {'depth_range': (0, 50), 'density': 1000.0, 'sound_speed': 1483.0},
        {'depth_range': (50, 100), 'density': 1015.0, 'sound_speed': 1489.0},
        {'depth_range': (100, 150), 'density': 1025.0, 'sound_speed': 1497.0},
        {'depth_range': (150, 200), 'density': 1030.0, 'sound_speed': 1500.0}
    ]
    
    layered_profile = props.create_layered_profile(layer_specs)
    props.save_profile(layered_profile, 'layered_profile.json')
    props.export_to_abaqus_layered(layered_profile, 'layered_materials.inp')
    props.plot_profile(layered_profile, plot_filename='layered_profile.png')
    
    # Gradient profile
    gradient_profile = props.create_gradient_profile(
        depth_max=200,
        density_params=(1000.0, 0.15),
        sound_speed_params=(1483.0, 0.085),
        num_points=50
    )
    props.save_profile(gradient_profile, 'gradient_profile.json')
    props.export_to_abaqus_gradient(gradient_profile, 'gradient_materials.inp')
    props.plot_profile(gradient_profile, plot_filename='gradient_profile.png')
    
    print("\nExample profiles created:")
    print("- standard_ocean_profile.json")
    print("- layered_profile.json")
    print("- gradient_profile.json")
    print("- layered_materials.inp")
    print("- gradient_materials.inp")


def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description='Generate acoustic material properties')
    parser.add_argument('--examples', action='store_true',
                       help='Create example profiles')
    parser.add_argument('--depth-max', type=float, default=200.0,
                       help='Maximum depth in meters')
    parser.add_argument('--layers', type=int, default=4,
                       help='Number of layers for layered profile')
    parser.add_argument('--plot', action='store_true',
                       help='Generate plots')
    
    args = parser.parse_args()
    
    if args.examples:
        create_example_profiles()
    else:
        print("Use --examples to create example profiles")
        print("Or import this module: from material_properties import *")


if __name__ == "__main__":
    main()