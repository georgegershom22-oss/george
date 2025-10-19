#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Advanced Visualization for Acoustic Field Results
=================================================
Creates publication-quality plots and animations from Abaqus ODB files
for acoustic transmission loss simulations.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import cm
from scipy import signal, interpolate
from odbAccess import openOdb
import os
import sys


class AcousticFieldVisualizer:
    """
    Comprehensive visualization tools for acoustic simulation results
    """
    
    def __init__(self, odb_path):
        """
        Initialize visualizer with ODB file
        
        Parameters:
        -----------
        odb_path : str
            Path to Abaqus ODB file
        """
        self.odb_path = odb_path
        self.odb = None
        self.frequencies = []
        self.pressure_fields = {}
        self.node_coordinates = {}
        
    def open_database(self):
        """Open ODB file for visualization"""
        try:
            self.odb = openOdb(self.odb_path, readOnly=True)
            print(f"Opened ODB: {self.odb_path}")
            
            # Get node coordinates
            self._extract_node_coordinates()
            return True
            
        except Exception as e:
            print(f"Error opening ODB: {e}")
            return False
            
    def _extract_node_coordinates(self):
        """Extract node coordinates from the model"""
        assembly = self.odb.rootAssembly
        
        for instance_name in assembly.instances.keys():
            instance = assembly.instances[instance_name]
            self.node_coordinates[instance_name] = {}
            
            for node in instance.nodes:
                self.node_coordinates[instance_name][node.label] = node.coordinates
                
        print(f"Extracted coordinates for {len(self.node_coordinates)} instances")
        
    def extract_pressure_fields(self, frequency_indices=None):
        """
        Extract pressure field data at specified frequencies
        
        Parameters:
        -----------
        frequency_indices : list
            Indices of frequencies to extract (None = all)
        """
        if not self.odb:
            print("ODB not opened")
            return False
            
        # Find frequency sweep step
        ssd_step = None
        for step_name in self.odb.steps.keys():
            if 'Frequency' in step_name or 'SSD' in step_name:
                ssd_step = self.odb.steps[step_name]
                break
                
        if not ssd_step:
            print("No frequency sweep step found")
            return False
            
        # Extract pressure at each frequency
        frame_count = len(ssd_step.frames)
        
        if frequency_indices is None:
            frequency_indices = range(frame_count)
            
        for idx in frequency_indices:
            if idx >= frame_count:
                continue
                
            frame = ssd_step.frames[idx]
            freq = frame.frequency
            self.frequencies.append(freq)
            
            if 'P' not in frame.fieldOutputs:
                print(f"No pressure field at frequency {freq} Hz")
                continue
                
            pressure_field = frame.fieldOutputs['P']
            
            # Store pressure values with coordinates
            pressure_data = {}
            for value in pressure_field.values:
                node_label = value.nodeLabel
                instance_name = value.instance.name if hasattr(value, 'instance') else 'DEFAULT'
                
                # Complex pressure (real, imaginary)
                if hasattr(value, 'data'):
                    if len(value.data) >= 2:
                        p_real = value.data[0]
                        p_imag = value.data[1]
                    else:
                        p_real = value.data[0]
                        p_imag = 0.0
                        
                    p_magnitude = np.sqrt(p_real**2 + p_imag**2)
                    p_phase = np.arctan2(p_imag, p_real)
                    
                    # Get coordinates
                    if instance_name in self.node_coordinates:
                        if node_label in self.node_coordinates[instance_name]:
                            coords = self.node_coordinates[instance_name][node_label]
                            
                            pressure_data[node_label] = {
                                'x': coords[0],
                                'y': coords[1] if len(coords) > 1 else 0,
                                'z': coords[2] if len(coords) > 2 else 0,
                                'magnitude': p_magnitude,
                                'phase': p_phase,
                                'real': p_real,
                                'imag': p_imag
                            }
                            
            self.pressure_fields[freq] = pressure_data
            print(f"Extracted pressure field at {freq:.1f} Hz ({len(pressure_data)} points)")
            
        return True
        
    def plot_pressure_field_2d(self, frequency, field_type='magnitude', 
                               save_path=None, show_plot=True):
        """
        Create 2D contour plot of pressure field
        
        Parameters:
        -----------
        frequency : float
            Frequency to plot
        field_type : str
            'magnitude', 'phase', 'real', or 'imag'
        save_path : str
            Path to save figure
        show_plot : bool
            Whether to display the plot
        """
        if frequency not in self.pressure_fields:
            print(f"No data for frequency {frequency} Hz")
            return False
            
        data = self.pressure_fields[frequency]
        
        # Extract coordinates and values
        x_coords = []
        y_coords = []
        values = []
        
        for node_data in data.values():
            x_coords.append(node_data['x'])
            y_coords.append(node_data['y'])
            values.append(node_data[field_type])
            
        # Create grid for interpolation
        x_unique = np.unique(x_coords)
        y_unique = np.unique(y_coords)
        X, Y = np.meshgrid(x_unique, y_unique)
        
        # Interpolate to regular grid
        from scipy.interpolate import griddata
        Z = griddata((x_coords, y_coords), values, (X, Y), method='cubic')
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Custom colormap for acoustic pressure
        if field_type == 'magnitude':
            cmap = 'viridis'
            label = 'Pressure Magnitude (Pa)'
        elif field_type == 'phase':
            cmap = 'hsv'
            label = 'Phase (rad)'
        else:
            cmap = 'RdBu_r'
            label = f'Pressure {field_type.capitalize()} (Pa)'
            
        # Contour plot
        levels = 50
        contour = ax.contourf(X, Y, Z, levels=levels, cmap=cmap)
        
        # Add contour lines
        contour_lines = ax.contour(X, Y, Z, levels=10, colors='black', 
                                   alpha=0.3, linewidths=0.5)
        
        # Colorbar
        cbar = plt.colorbar(contour, ax=ax)
        cbar.set_label(label, rotation=270, labelpad=20)
        
        # Labels and title
        ax.set_xlabel('X Position (m)', fontsize=12)
        ax.set_ylabel('Y Position (m)', fontsize=12)
        ax.set_title(f'Acoustic Pressure Field at {frequency:.1f} Hz', 
                    fontsize=14, fontweight='bold')
        
        # Add grid
        ax.grid(True, alpha=0.2)
        ax.set_aspect('equal')
        
        # Tight layout
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved plot to {save_path}")
            
        if show_plot:
            plt.show()
            
        return fig
        
    def plot_wave_propagation(self, frequency, n_snapshots=8, save_path=None):
        """
        Create snapshots of wave propagation at different phases
        
        Parameters:
        -----------
        frequency : float
            Frequency to visualize
        n_snapshots : int
            Number of phase snapshots
        save_path : str
            Path to save figure
        """
        if frequency not in self.pressure_fields:
            print(f"No data for frequency {frequency} Hz")
            return False
            
        data = self.pressure_fields[frequency]
        
        # Create subplots
        fig, axes = plt.subplots(2, 4, figsize=(16, 8))
        axes = axes.flatten()
        
        # Phase angles for snapshots
        phases = np.linspace(0, 2*np.pi, n_snapshots, endpoint=False)
        
        for idx, phase_shift in enumerate(phases):
            ax = axes[idx]
            
            # Calculate instantaneous pressure
            x_coords = []
            y_coords = []
            p_instant = []
            
            for node_data in data.values():
                x_coords.append(node_data['x'])
                y_coords.append(node_data['y'])
                
                # Instantaneous pressure: p(t) = |p| * cos(ωt + φ)
                p_inst = node_data['magnitude'] * np.cos(node_data['phase'] + phase_shift)
                p_instant.append(p_inst)
                
            # Interpolate to grid
            x_unique = np.unique(x_coords)
            y_unique = np.unique(y_coords)
            X, Y = np.meshgrid(x_unique, y_unique)
            
            from scipy.interpolate import griddata
            Z = griddata((x_coords, y_coords), p_instant, (X, Y), method='cubic')
            
            # Plot
            im = ax.contourf(X, Y, Z, levels=30, cmap='RdBu_r', 
                           vmin=-np.max(np.abs(Z)), vmax=np.max(np.abs(Z)))
            ax.set_title(f'Phase: {phase_shift*180/np.pi:.0f}°', fontsize=10)
            ax.set_xlabel('X (m)', fontsize=8)
            ax.set_ylabel('Y (m)', fontsize=8)
            ax.set_aspect('equal')
            
        # Overall title
        fig.suptitle(f'Wave Propagation at {frequency:.1f} Hz', 
                    fontsize=14, fontweight='bold')
        
        # Add colorbar
        fig.subplots_adjust(right=0.9)
        cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
        cbar = fig.colorbar(im, cax=cbar_ax)
        cbar.set_label('Instantaneous Pressure (Pa)', rotation=270, labelpad=15)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved propagation plot to {save_path}")
            
        return fig
        
    def plot_intensity_vector_field(self, frequency, save_path=None):
        """
        Plot acoustic intensity vector field
        
        Parameters:
        -----------
        frequency : float
            Frequency to visualize
        save_path : str
            Path to save figure
        """
        if frequency not in self.pressure_fields:
            print(f"No data for frequency {frequency} Hz")
            return False
            
        data = self.pressure_fields[frequency]
        
        # Calculate intensity vectors (simplified - requires velocity data)
        # Here we approximate using pressure gradient
        
        x_coords = []
        y_coords = []
        p_real = []
        p_imag = []
        
        for node_data in data.values():
            x_coords.append(node_data['x'])
            y_coords.append(node_data['y'])
            p_real.append(node_data['real'])
            p_imag.append(node_data['imag'])
            
        # Create regular grid
        x_unique = np.unique(x_coords)
        y_unique = np.unique(y_coords)
        X, Y = np.meshgrid(x_unique, y_unique)
        
        from scipy.interpolate import griddata
        P_real = griddata((x_coords, y_coords), p_real, (X, Y), method='cubic')
        P_imag = griddata((x_coords, y_coords), p_imag, (X, Y), method='cubic')
        
        # Calculate gradients (approximate particle velocity)
        dPr_dx, dPr_dy = np.gradient(P_real)
        dPi_dx, dPi_dy = np.gradient(P_imag)
        
        # Intensity components (simplified)
        Ix = P_real * dPi_dx - P_imag * dPr_dx
        Iy = P_real * dPi_dy - P_imag * dPr_dy
        
        # Magnitude
        I_mag = np.sqrt(Ix**2 + Iy**2)
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Left: Intensity magnitude
        im1 = ax1.contourf(X, Y, I_mag, levels=30, cmap='hot')
        plt.colorbar(im1, ax=ax1, label='Intensity Magnitude')
        ax1.set_title('Acoustic Intensity Magnitude')
        ax1.set_xlabel('X Position (m)')
        ax1.set_ylabel('Y Position (m)')
        ax1.set_aspect('equal')
        
        # Right: Intensity vectors
        skip = 5  # Skip points for clarity
        im2 = ax2.contourf(X, Y, I_mag, levels=30, cmap='hot', alpha=0.5)
        ax2.quiver(X[::skip, ::skip], Y[::skip, ::skip], 
                  Ix[::skip, ::skip], Iy[::skip, ::skip],
                  color='black', alpha=0.7)
        ax2.set_title('Acoustic Intensity Vectors')
        ax2.set_xlabel('X Position (m)')
        ax2.set_ylabel('Y Position (m)')
        ax2.set_aspect('equal')
        
        fig.suptitle(f'Acoustic Intensity Field at {frequency:.1f} Hz', 
                    fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved intensity plot to {save_path}")
            
        return fig
        
    def create_frequency_animation(self, output_file='acoustic_animation.mp4'):
        """
        Create animation showing pressure field evolution with frequency
        
        Parameters:
        -----------
        output_file : str
            Output video file name
        """
        if not self.pressure_fields:
            print("No pressure field data available")
            return False
            
        frequencies = sorted(self.pressure_fields.keys())
        
        # Setup figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Get data range for consistent scaling
        all_values = []
        for freq_data in self.pressure_fields.values():
            for node_data in freq_data.values():
                all_values.append(node_data['magnitude'])
        vmin, vmax = min(all_values), max(all_values)
        
        # Animation function
        def animate(frame_idx):
            ax.clear()
            
            freq = frequencies[frame_idx]
            data = self.pressure_fields[freq]
            
            # Extract data
            x_coords = []
            y_coords = []
            values = []
            
            for node_data in data.values():
                x_coords.append(node_data['x'])
                y_coords.append(node_data['y'])
                values.append(node_data['magnitude'])
                
            # Interpolate
            x_unique = np.unique(x_coords)
            y_unique = np.unique(y_coords)
            X, Y = np.meshgrid(x_unique, y_unique)
            
            from scipy.interpolate import griddata
            Z = griddata((x_coords, y_coords), values, (X, Y), method='cubic')
            
            # Plot
            im = ax.contourf(X, Y, Z, levels=30, cmap='viridis', 
                           vmin=vmin, vmax=vmax)
            ax.set_title(f'Pressure Field at {freq:.1f} Hz', fontsize=14)
            ax.set_xlabel('X Position (m)')
            ax.set_ylabel('Y Position (m)')
            ax.set_aspect('equal')
            
            return [im]
            
        # Create animation
        anim = animation.FuncAnimation(fig, animate, frames=len(frequencies),
                                     interval=200, blit=False)
        
        # Save animation
        try:
            anim.save(output_file, writer='ffmpeg', fps=5, bitrate=1800)
            print(f"Animation saved to {output_file}")
        except:
            print("Could not save animation (ffmpeg may not be installed)")
            
        plt.close()
        return anim
        
    def plot_stratification_effect(self, frequencies_to_plot=None):
        """
        Visualize the effect of stratification on wave propagation
        
        Parameters:
        -----------
        frequencies_to_plot : list
            List of frequencies to include in comparison
        """
        if frequencies_to_plot is None:
            # Default: plot 4 evenly spaced frequencies
            available = sorted(self.pressure_fields.keys())
            if len(available) >= 4:
                indices = np.linspace(0, len(available)-1, 4, dtype=int)
                frequencies_to_plot = [available[i] for i in indices]
            else:
                frequencies_to_plot = available
                
        n_freq = len(frequencies_to_plot)
        
        # Create subplot grid
        fig, axes = plt.subplots(2, n_freq, figsize=(4*n_freq, 8))
        
        if n_freq == 1:
            axes = axes.reshape(2, 1)
            
        for col, freq in enumerate(frequencies_to_plot):
            if freq not in self.pressure_fields:
                continue
                
            data = self.pressure_fields[freq]
            
            # Extract coordinates and values
            x_coords = []
            y_coords = []
            magnitude = []
            phase = []
            
            for node_data in data.values():
                x_coords.append(node_data['x'])
                y_coords.append(node_data['y'])
                magnitude.append(node_data['magnitude'])
                phase.append(node_data['phase'])
                
            # Create grid
            x_unique = np.unique(x_coords)
            y_unique = np.unique(y_coords)
            X, Y = np.meshgrid(x_unique, y_unique)
            
            from scipy.interpolate import griddata
            Z_mag = griddata((x_coords, y_coords), magnitude, (X, Y), method='cubic')
            Z_phase = griddata((x_coords, y_coords), phase, (X, Y), method='cubic')
            
            # Top row: Magnitude
            ax_mag = axes[0, col]
            im_mag = ax_mag.contourf(X, Y, Z_mag, levels=30, cmap='viridis')
            ax_mag.set_title(f'{freq:.0f} Hz', fontsize=10)
            ax_mag.set_aspect('equal')
            
            if col == 0:
                ax_mag.set_ylabel('Y (m)', fontsize=10)
            ax_mag.set_xlabel('X (m)', fontsize=10)
            
            plt.colorbar(im_mag, ax=ax_mag, orientation='horizontal', pad=0.05)
            
            # Bottom row: Phase
            ax_phase = axes[1, col]
            im_phase = ax_phase.contourf(X, Y, Z_phase, levels=30, cmap='hsv')
            ax_phase.set_aspect('equal')
            
            if col == 0:
                ax_phase.set_ylabel('Y (m)', fontsize=10)
            ax_phase.set_xlabel('X (m)', fontsize=10)
            
            plt.colorbar(im_phase, ax=ax_phase, orientation='horizontal', pad=0.05)
            
        # Add overall labels
        fig.text(0.08, 0.7, 'Magnitude', rotation=90, fontsize=12, 
                ha='center', va='center')
        fig.text(0.08, 0.3, 'Phase', rotation=90, fontsize=12, 
                ha='center', va='center')
        
        fig.suptitle('Frequency-Dependent Stratification Effects', 
                    fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        return fig
        
    def close_database(self):
        """Close ODB file"""
        if self.odb:
            self.odb.close()
            print("ODB closed")


# Standalone plotting functions
def plot_material_profiles(density_profile, sound_speed_profile, depths, 
                          save_path=None):
    """
    Plot density and sound speed profiles
    
    Parameters:
    -----------
    density_profile : array-like
        Density values (kg/m³)
    sound_speed_profile : array-like
        Sound speed values (m/s)
    depths : array-like
        Depth values (m)
    save_path : str
        Path to save figure
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 6))
    
    # Density profile
    ax1.plot(density_profile, depths, 'b-', linewidth=2)
    ax1.set_xlabel('Density (kg/m³)', fontsize=12)
    ax1.set_ylabel('Depth (m)', fontsize=12)
    ax1.set_title('Density Profile', fontsize=14)
    ax1.grid(True, alpha=0.3)
    ax1.invert_yaxis()
    
    # Sound speed profile
    ax2.plot(sound_speed_profile, depths, 'r-', linewidth=2)
    ax2.set_xlabel('Sound Speed (m/s)', fontsize=12)
    ax2.set_ylabel('Depth (m)', fontsize=12)
    ax2.set_title('Sound Speed Profile', fontsize=14)
    ax2.grid(True, alpha=0.3)
    ax2.invert_yaxis()
    
    plt.suptitle('Stratified Medium Properties', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved profile plot to {save_path}")
        
    return fig


def plot_ray_paths(ray_data, domain_bounds, save_path=None):
    """
    Plot acoustic ray paths through stratified medium
    
    Parameters:
    -----------
    ray_data : dict
        Dictionary containing ray path coordinates
    domain_bounds : tuple
        (x_min, x_max, y_min, y_max)
    save_path : str
        Path to save figure
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot each ray
    for ray_id, ray_coords in ray_data.items():
        x = ray_coords['x']
        y = ray_coords['y']
        ax.plot(x, y, '-', linewidth=1.5, alpha=0.7, label=f'Ray {ray_id}')
        
    # Domain boundaries
    ax.set_xlim(domain_bounds[0], domain_bounds[1])
    ax.set_ylim(domain_bounds[2], domain_bounds[3])
    
    ax.set_xlabel('Range (m)', fontsize=12)
    ax.set_ylabel('Depth (m)', fontsize=12)
    ax.set_title('Acoustic Ray Paths in Stratified Medium', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.invert_yaxis()
    ax.legend(loc='best')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved ray path plot to {save_path}")
        
    return fig


# Main execution
if __name__ == "__main__":
    
    # Check command line arguments
    if len(sys.argv) > 1:
        odb_file = sys.argv[1]
    else:
        # Look for ODB files
        possible_files = ['TL_Layered.odb', 'TL_Graded.odb', 'AcousticTL_Job.odb']
        odb_file = None
        
        for pf in possible_files:
            if os.path.exists(pf):
                odb_file = pf
                break
                
        if not odb_file:
            print("Usage: python visualize_acoustic_fields.py <odb_file>")
            print("No ODB file found.")
            sys.exit(1)
            
    print("\n" + "="*60)
    print("ACOUSTIC FIELD VISUALIZATION")
    print("="*60 + "\n")
    
    # Create visualizer
    viz = AcousticFieldVisualizer(odb_file)
    
    # Open database
    if not viz.open_database():
        sys.exit(1)
        
    # Extract pressure fields (first 5 frequencies for demo)
    print("\nExtracting pressure fields...")
    viz.extract_pressure_fields(frequency_indices=range(5))
    
    # Generate visualizations
    if viz.pressure_fields:
        
        # Get first available frequency
        first_freq = sorted(viz.pressure_fields.keys())[0]
        
        print(f"\nGenerating visualizations for {first_freq:.1f} Hz...")
        
        # 1. Pressure magnitude field
        viz.plot_pressure_field_2d(first_freq, field_type='magnitude',
                                   save_path='pressure_magnitude.png',
                                   show_plot=False)
        
        # 2. Wave propagation snapshots
        viz.plot_wave_propagation(first_freq, n_snapshots=8,
                                 save_path='wave_propagation.png')
        
        # 3. Intensity vector field
        viz.plot_intensity_vector_field(first_freq,
                                       save_path='intensity_field.png')
        
        # 4. Stratification effects
        fig = viz.plot_stratification_effect()
        plt.savefig('stratification_effects.png', dpi=150, bbox_inches='tight')
        
        # 5. Animation (optional - requires ffmpeg)
        # viz.create_frequency_animation('acoustic_evolution.mp4')
        
        print("\nVisualization files created:")
        print("  - pressure_magnitude.png")
        print("  - wave_propagation.png")
        print("  - intensity_field.png")
        print("  - stratification_effects.png")
        
    # Close database
    viz.close_database()
    
    print("\n" + "="*60)
    print("VISUALIZATION COMPLETED")
    print("="*60)