#!/usr/bin/env python3
"""
Acoustic Field Visualization Script
====================================
Creates animations and plots of acoustic pressure fields
from Abaqus simulation results.

Author: Acoustic Visualization Framework
Date: 2025-10-19
Version: 1.0.0
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import cm
from matplotlib.colors import Normalize
import matplotlib.patches as patches
from odbAccess import openOdb
import sys
import os


class AcousticFieldVisualizer:
    """
    Visualize acoustic pressure fields and create animations.
    """
    
    def __init__(self, odb_path):
        """
        Initialize visualizer.
        
        Parameters:
        -----------
        odb_path : str
            Path to ODB file
        """
        self.odb_path = odb_path
        self.odb = None
        self.node_coords = {}
        self.pressure_fields = {}
        
    def extract_field_data(self, frequency_index=None, step_name='FREQ_SWEEP'):
        """
        Extract pressure field data at specified frequency.
        
        Parameters:
        -----------
        frequency_index : int
            Index of frequency frame to extract (None for all)
        step_name : str
            Name of the analysis step
        """
        # Open ODB
        self.odb = openOdb(self.odb_path, readOnly=True)
        step = self.odb.steps[step_name]
        
        # Get assembly and instance
        assembly = self.odb.rootAssembly
        instance = assembly.instances[assembly.instances.keys()[0]]
        
        # Extract node coordinates
        for node in instance.nodes:
            self.node_coords[node.label] = node.coordinates
        
        # Select frames to process
        if frequency_index is not None:
            frames_to_process = [step.frames[frequency_index]]
        else:
            frames_to_process = step.frames
        
        # Extract pressure fields
        for frame in frames_to_process:
            freq = frame.frameValue
            self.pressure_fields[freq] = {}
            
            # Get pressure field output
            p_field = frame.fieldOutputs['P']
            
            # Extract values at all nodes
            for value in p_field.values:
                node_label = value.nodeLabel
                if len(value.data) >= 2:
                    # Complex pressure
                    p_real = value.data[0]
                    p_imag = value.data[1]
                    p_magnitude = np.sqrt(p_real**2 + p_imag**2)
                    p_phase = np.arctan2(p_imag, p_real)
                else:
                    p_real = value.data[0]
                    p_imag = 0.0
                    p_magnitude = abs(p_real)
                    p_phase = 0.0 if p_real >= 0 else np.pi
                
                self.pressure_fields[freq][node_label] = {
                    'real': p_real,
                    'imag': p_imag,
                    'magnitude': p_magnitude,
                    'phase': p_phase
                }
        
        self.odb.close()
        print(f"Extracted field data for {len(self.pressure_fields)} frequencies")
    
    def create_2d_contour_plot(self, frequency, component='magnitude', 
                               save_file=None):
        """
        Create 2D contour plot of pressure field.
        
        Parameters:
        -----------
        frequency : float
            Frequency to plot
        component : str
            'magnitude', 'real', 'imag', or 'phase'
        save_file : str
            File path to save plot
        """
        if frequency not in self.pressure_fields:
            print(f"Frequency {frequency} Hz not available")
            return
        
        # Prepare data for plotting
        x_coords = []
        y_coords = []
        values = []
        
        for node_label, coords in self.node_coords.items():
            if node_label in self.pressure_fields[frequency]:
                x_coords.append(coords[0])
                y_coords.append(coords[1])
                values.append(
                    self.pressure_fields[frequency][node_label][component]
                )
        
        # Convert to numpy arrays
        x = np.array(x_coords)
        y = np.array(y_coords)
        z = np.array(values)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create contour plot
        # Generate regular grid for interpolation
        xi = np.linspace(x.min(), x.max(), 200)
        yi = np.linspace(y.min(), y.max(), 50)
        Xi, Yi = np.meshgrid(xi, yi)
        
        # Interpolate to regular grid (simple nearest-neighbor)
        from scipy.interpolate import griddata
        Zi = griddata((x, y), z, (Xi, Yi), method='linear')
        
        # Plot contours
        if component == 'phase':
            levels = np.linspace(-np.pi, np.pi, 21)
            cs = ax.contourf(Xi, Yi, Zi, levels=levels, cmap='hsv')
            cbar_label = 'Phase (radians)'
        else:
            levels = 20
            cs = ax.contourf(Xi, Yi, Zi, levels=levels, cmap='RdBu_r')
            if component == 'magnitude':
                cbar_label = 'Pressure Magnitude (Pa)'
            else:
                cbar_label = f'Pressure {component.capitalize()} (Pa)'
        
        # Add colorbar
        cbar = plt.colorbar(cs, ax=ax)
        cbar.set_label(cbar_label)
        
        # Labels and title
        ax.set_xlabel('X Position (m)')
        ax.set_ylabel('Y Position (m)')
        ax.set_title(f'Acoustic Pressure Field at {frequency:.1f} Hz\n'
                    f'Component: {component.capitalize()}')
        ax.set_aspect('equal')
        
        # Add stratification layers if visible
        if hasattr(self, 'layer_boundaries'):
            for y_boundary in self.layer_boundaries:
                ax.axhline(y=y_boundary, color='black', linestyle='--', 
                          linewidth=0.5, alpha=0.5)
        
        plt.tight_layout()
        
        if save_file:
            plt.savefig(save_file, dpi=150, bbox_inches='tight')
            print(f"Saved plot to {save_file}")
        
        plt.show()
        
        return fig, ax
    
    def create_wave_animation(self, frequency, output_file='wave_animation.mp4'):
        """
        Create animation showing wave propagation.
        
        Parameters:
        -----------
        frequency : float
            Frequency to animate
        output_file : str
            Output video file name
        """
        if frequency not in self.pressure_fields:
            print(f"Frequency {frequency} Hz not available")
            return
        
        # Prepare spatial data
        x_coords = []
        y_coords = []
        p_real = []
        p_imag = []
        
        for node_label, coords in self.node_coords.items():
            if node_label in self.pressure_fields[frequency]:
                x_coords.append(coords[0])
                y_coords.append(coords[1])
                p_real.append(
                    self.pressure_fields[frequency][node_label]['real']
                )
                p_imag.append(
                    self.pressure_fields[frequency][node_label]['imag']
                )
        
        x = np.array(x_coords)
        y = np.array(y_coords)
        p_re = np.array(p_real)
        p_im = np.array(p_imag)
        
        # Create regular grid
        xi = np.linspace(x.min(), x.max(), 200)
        yi = np.linspace(y.min(), y.max(), 50)
        Xi, Yi = np.meshgrid(xi, yi)
        
        from scipy.interpolate import griddata
        P_re_grid = griddata((x, y), p_re, (Xi, Yi), method='linear')
        P_im_grid = griddata((x, y), p_im, (Xi, Yi), method='linear')
        
        # Animation function
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Set up plot limits and labels
        ax.set_xlim(x.min(), x.max())
        ax.set_ylim(y.min(), y.max())
        ax.set_xlabel('X Position (m)')
        ax.set_ylabel('Y Position (m)')
        ax.set_aspect('equal')
        
        # Color scale
        vmax = np.max(np.sqrt(P_re_grid**2 + P_im_grid**2))
        vmin = -vmax
        
        # Initial plot
        phase = 0
        P_instant = P_re_grid * np.cos(phase) - P_im_grid * np.sin(phase)
        im = ax.contourf(Xi, Yi, P_instant, levels=20, 
                        cmap='RdBu_r', vmin=vmin, vmax=vmax)
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Instantaneous Pressure (Pa)')
        
        # Title
        title = ax.set_title(f'Acoustic Wave at {frequency:.1f} Hz, Phase: 0°')
        
        def animate(frame):
            """Update function for animation."""
            phase = frame * 2 * np.pi / 50  # 50 frames per cycle
            P_instant = P_re_grid * np.cos(phase) - P_im_grid * np.sin(phase)
            
            # Clear and redraw
            ax.clear()
            im = ax.contourf(Xi, Yi, P_instant, levels=20,
                           cmap='RdBu_r', vmin=vmin, vmax=vmax)
            ax.set_xlim(x.min(), x.max())
            ax.set_ylim(y.min(), y.max())
            ax.set_xlabel('X Position (m)')
            ax.set_ylabel('Y Position (m)')
            ax.set_aspect('equal')
            ax.set_title(f'Acoustic Wave at {frequency:.1f} Hz, '
                        f'Phase: {np.degrees(phase):.0f}°')
            
            return [im]
        
        # Create animation
        anim = animation.FuncAnimation(fig, animate, frames=50,
                                     interval=50, blit=False, repeat=True)
        
        # Save animation
        try:
            Writer = animation.writers['ffmpeg']
            writer = Writer(fps=20, metadata=dict(artist='Abaqus'), bitrate=1800)
            anim.save(output_file, writer=writer)
            print(f"Animation saved to {output_file}")
        except:
            print("Could not save animation. FFmpeg may not be installed.")
            print("Displaying animation instead...")
            plt.show()
        
        return anim
    
    def plot_stratification_profile(self, materials_data=None):
        """
        Plot the density and sound speed stratification profile.
        
        Parameters:
        -----------
        materials_data : dict
            Dictionary with layer properties
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        if materials_data:
            # Example for layered case
            depths = []
            densities = []
            sound_speeds = []
            
            for layer in materials_data:
                depths.extend([layer['z_min'], layer['z_max']])
                rho = layer['density']
                K = layer['bulk_modulus']
                c = np.sqrt(K / rho)
                densities.extend([rho, rho])
                sound_speeds.extend([c, c])
            
            # Plot density profile
            ax1.plot(densities, depths, 'b-', linewidth=2)
            ax1.set_xlabel('Density (kg/m³)')
            ax1.set_ylabel('Depth (m)')
            ax1.set_title('Density Stratification')
            ax1.grid(True, alpha=0.3)
            ax1.invert_yaxis()
            
            # Plot sound speed profile
            ax2.plot(sound_speeds, depths, 'r-', linewidth=2)
            ax2.set_xlabel('Sound Speed (m/s)')
            ax2.set_ylabel('Depth (m)')
            ax2.set_title('Sound Speed Profile')
            ax2.grid(True, alpha=0.3)
            ax2.invert_yaxis()
        
        else:
            # Example continuous gradient (thermocline)
            z = np.linspace(0, 2, 100)
            z_norm = z / 2.0
            
            # Thermocline profile
            thermocline_center = 0.5
            thermocline_width = 0.2
            profile = 0.5 * (1 + np.tanh((z_norm - thermocline_center) / 
                                        thermocline_width))
            
            rho = 950 + 100 * profile
            K = 2.0e9 + 0.2e9 * profile
            c = np.sqrt(K / rho)
            
            ax1.plot(rho, z, 'b-', linewidth=2)
            ax1.set_xlabel('Density (kg/m³)')
            ax1.set_ylabel('Depth (m)')
            ax1.set_title('Thermocline Density Profile')
            ax1.grid(True, alpha=0.3)
            ax1.invert_yaxis()
            
            ax2.plot(c, z, 'r-', linewidth=2)
            ax2.set_xlabel('Sound Speed (m/s)')
            ax2.set_ylabel('Depth (m)')
            ax2.set_title('Thermocline Sound Speed Profile')
            ax2.grid(True, alpha=0.3)
            ax2.invert_yaxis()
        
        plt.suptitle('Acoustic Medium Stratification', fontsize=14)
        plt.tight_layout()
        plt.show()
        
        return fig
    
    def plot_ray_paths(self, source_depth=0.5, num_rays=20):
        """
        Plot approximate ray paths through stratified medium.
        
        Parameters:
        -----------
        source_depth : float
            Depth of acoustic source (m)
        num_rays : int
            Number of rays to trace
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Simple ray tracing for visualization
        x_max = 10.0
        angles = np.linspace(-30, 30, num_rays)  # Launch angles in degrees
        
        for angle in angles:
            # Very simplified ray path (would need proper ray equations)
            x = np.linspace(0, x_max, 100)
            
            # Initial conditions
            theta0 = np.radians(angle)
            y0 = source_depth
            
            # Simple parabolic approximation for visualization
            # (Real ray tracing would use Snell's law in gradient)
            y = y0 + x * np.tan(theta0) - 0.01 * x**2 * np.cos(theta0)
            
            # Reflect at boundaries
            y = np.abs(y)  # Simple reflection at bottom
            y = np.where(y > 2.0, 4.0 - y, y)  # Reflect at top
            
            # Plot ray
            ax.plot(x, y, 'b-', alpha=0.3, linewidth=0.5)
        
        # Add source
        ax.plot(0, source_depth, 'ro', markersize=10, label='Source')
        
        # Add boundaries
        ax.axhline(y=0, color='black', linewidth=2)
        ax.axhline(y=2.0, color='black', linewidth=2)
        
        # Labels
        ax.set_xlabel('Range (m)')
        ax.set_ylabel('Depth (m)')
        ax.set_title('Ray Paths in Stratified Medium (Simplified)')
        ax.set_xlim(0, x_max)
        ax.set_ylim(-0.1, 2.1)
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.tight_layout()
        plt.show()
        
        return fig


def main():
    """
    Main execution for visualization.
    """
    if len(sys.argv) < 2:
        print("Usage: python visualize_acoustic_field.py <odb_file> [frequency]")
        sys.exit(1)
    
    odb_file = sys.argv[1]
    frequency = float(sys.argv[2]) if len(sys.argv) > 2 else None
    
    # Create visualizer
    viz = AcousticFieldVisualizer(odb_file)
    
    print("="*60)
    print("ACOUSTIC FIELD VISUALIZATION")
    print("="*60)
    
    # Extract field data
    if frequency:
        print(f"Extracting field at {frequency} Hz...")
        viz.extract_field_data(frequency_index=0)  # Simplified
    else:
        print("Extracting all frequency data...")
        viz.extract_field_data()
    
    # Create visualizations
    if viz.pressure_fields:
        freq = list(viz.pressure_fields.keys())[0]
        
        # Contour plots
        print(f"\nCreating contour plots for {freq} Hz...")
        viz.create_2d_contour_plot(freq, component='magnitude',
                                   save_file='pressure_magnitude.png')
        viz.create_2d_contour_plot(freq, component='phase',
                                   save_file='pressure_phase.png')
        
        # Animation
        print("\nCreating wave animation...")
        viz.create_wave_animation(freq)
        
        # Stratification profile
        print("\nPlotting stratification profile...")
        viz.plot_stratification_profile()
        
        # Ray paths
        print("\nPlotting ray paths...")
        viz.plot_ray_paths()
    
    print("\n" + "="*60)
    print("VISUALIZATION COMPLETE")
    print("="*60)


if __name__ == '__main__':
    main()