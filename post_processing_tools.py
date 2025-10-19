#!/usr/bin/env python
"""
Post-Processing Tools for Abaqus Acoustic Transmission Loss
==========================================================

This module provides comprehensive post-processing tools for analyzing
acoustic transmission loss results from Abaqus simulations.

Features:
- ODB file reading and data extraction
- Transmission loss and absorption coefficient calculation
- Frequency response analysis
- Visualization and plotting
- Data export to various formats
- Quality assessment tools

Author: AI Assistant
Date: 2025-10-19
Units: SI (m-kg-s-Pa)
"""

import sys
import os
import numpy as np
import math
import csv
from collections import defaultdict

try:
    from odbAccess import openOdb
    ABAQUS_AVAILABLE = True
except ImportError:
    print("Warning: odbAccess not available. Some functions will not work.")
    ABAQUS_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    print("Warning: matplotlib not available. Plotting functions disabled.")
    MATPLOTLIB_AVAILABLE = False


class AcousticPostProcessor:
    """Post-processing class for acoustic transmission loss analysis."""
    
    def __init__(self, odb_path=None):
        """
        Initialize post-processor.
        
        Parameters:
        -----------
        odb_path : str
            Path to Abaqus ODB file
        """
        self.odb_path = odb_path
        self.odb = None
        self.results = {}
        self.frequencies = []
        self.probe_data = {}
        
    def open_odb(self, odb_path=None):
        """
        Open Abaqus ODB file.
        
        Parameters:
        -----------
        odb_path : str
            Path to ODB file (optional if set in __init__)
        """
        if not ABAQUS_AVAILABLE:
            raise ImportError("odbAccess module not available")
            
        if odb_path:
            self.odb_path = odb_path
            
        if not self.odb_path:
            raise ValueError("ODB path not specified")
            
        try:
            self.odb = openOdb(self.odb_path)
            print(f"Opened ODB: {self.odb_path}")
            
            # Get basic info
            step_names = list(self.odb.steps.keys())
            print(f"Available steps: {step_names}")
            
            if 'SteadyState' in step_names or 'STEADY_STATE' in step_names:
                step_name = 'SteadyState' if 'SteadyState' in step_names else 'STEADY_STATE'
                step = self.odb.steps[step_name]
                print(f"Step '{step_name}' has {len(step.frames)} frames")
                
                # Get frequency range
                if step.frames:
                    freq_start = step.frames[0].frequency
                    freq_end = step.frames[-1].frequency
                    print(f"Frequency range: {freq_start:.1f} - {freq_end:.1f} Hz")
                    
        except Exception as e:
            print(f"Error opening ODB: {e}")
            raise
            
    def close_odb(self):
        """Close ODB file."""
        if self.odb:
            self.odb.close()
            self.odb = None
            print("ODB closed")
            
    def extract_probe_data(self, step_name='SteadyState', probe_sets=None):
        """
        Extract pressure data from probe locations.
        
        Parameters:
        -----------
        step_name : str
            Name of analysis step
        probe_sets : list
            List of probe set names (default: ['PROBE_IN', 'PROBE_OUT'])
        """
        if not self.odb:
            raise ValueError("ODB not opened")
            
        if probe_sets is None:
            probe_sets = ['PROBE_IN', 'PROBE_OUT']
            
        # Try different step name variations
        available_steps = list(self.odb.steps.keys())
        if step_name not in available_steps:
            for alt_name in ['STEADY_STATE', 'SteadyState', 'Step-1']:
                if alt_name in available_steps:
                    step_name = alt_name
                    break
            else:
                raise ValueError(f"Step not found. Available: {available_steps}")
                
        step = self.odb.steps[step_name]
        
        # Initialize data storage
        self.frequencies = []
        self.probe_data = {probe: {'real': [], 'imag': [], 'magnitude': [], 'phase': []} 
                          for probe in probe_sets}
        
        print(f"Extracting data from {len(step.frames)} frames...")
        
        for frame_idx, frame in enumerate(step.frames):
            freq = frame.frequency
            self.frequencies.append(freq)
            
            # Get pressure field
            try:
                p_field = frame.fieldOutputs['P']
            except KeyError:
                print(f"Warning: Pressure field 'P' not found in frame {frame_idx}")
                continue
                
            # Extract data for each probe
            for probe_name in probe_sets:
                try:
                    # Try different ways to access node sets
                    probe_set = None
                    for possible_name in [probe_name, f'ASSEMBLY__{probe_name}', f'PART-1-1__{probe_name}']:
                        if possible_name in self.odb.rootAssembly.nodeSets:
                            probe_set = self.odb.rootAssembly.nodeSets[possible_name]
                            break
                            
                    if probe_set is None:
                        print(f"Warning: Probe set '{probe_name}' not found")
                        # Add dummy values
                        self.probe_data[probe_name]['real'].append(0.0)
                        self.probe_data[probe_name]['imag'].append(0.0)
                        self.probe_data[probe_name]['magnitude'].append(0.0)
                        self.probe_data[probe_name]['phase'].append(0.0)
                        continue
                        
                    # Get pressure subset
                    p_subset = p_field.getSubset(region=probe_set)
                    
                    # Extract complex pressure values
                    pressure_values = []
                    for value in p_subset.values:
                        real_part = value.data[0] if len(value.data) > 0 else 0.0
                        imag_part = value.data[1] if len(value.data) > 1 else 0.0
                        pressure_values.append(complex(real_part, imag_part))
                        
                    if pressure_values:
                        # Calculate spatial average
                        avg_pressure = np.mean(pressure_values)
                        
                        self.probe_data[probe_name]['real'].append(avg_pressure.real)
                        self.probe_data[probe_name]['imag'].append(avg_pressure.imag)
                        self.probe_data[probe_name]['magnitude'].append(abs(avg_pressure))
                        self.probe_data[probe_name]['phase'].append(np.angle(avg_pressure))
                    else:
                        # No data found
                        self.probe_data[probe_name]['real'].append(0.0)
                        self.probe_data[probe_name]['imag'].append(0.0)
                        self.probe_data[probe_name]['magnitude'].append(0.0)
                        self.probe_data[probe_name]['phase'].append(0.0)
                        
                except Exception as e:
                    print(f"Warning: Error extracting data for {probe_name}: {e}")
                    # Add dummy values
                    self.probe_data[probe_name]['real'].append(0.0)
                    self.probe_data[probe_name]['imag'].append(0.0)
                    self.probe_data[probe_name]['magnitude'].append(0.0)
                    self.probe_data[probe_name]['phase'].append(0.0)
                    
        # Convert to numpy arrays
        self.frequencies = np.array(self.frequencies)
        for probe in probe_sets:
            for key in self.probe_data[probe]:
                self.probe_data[probe][key] = np.array(self.probe_data[probe][key])
                
        print(f"Extracted data for {len(self.frequencies)} frequencies")
        print(f"Probe sets processed: {list(self.probe_data.keys())}")
        
    def calculate_transmission_loss(self, probe_in='PROBE_IN', probe_out='PROBE_OUT', 
                                   probe_separation=None):
        """
        Calculate transmission loss from probe data.
        
        Parameters:
        -----------
        probe_in : str
            Name of input probe set
        probe_out : str
            Name of output probe set
        probe_separation : float
            Distance between probes in meters (for absorption coefficient)
            
        Returns:
        --------
        dict : Results containing TL, alpha, and related data
        """
        if not self.probe_data:
            raise ValueError("No probe data available. Run extract_probe_data() first.")
            
        if probe_in not in self.probe_data or probe_out not in self.probe_data:
            raise ValueError(f"Probe data not found for {probe_in} or {probe_out}")
            
        # Get pressure magnitudes
        pin_mag = self.probe_data[probe_in]['magnitude']
        pout_mag = self.probe_data[probe_out]['magnitude']
        
        # Avoid division by zero
        pout_mag = np.maximum(pout_mag, 1e-20)
        
        # Calculate transmission loss (dB)
        TL = 20 * np.log10(pin_mag / pout_mag)
        
        # Calculate absorption coefficient
        alpha_amp = None
        if probe_separation is not None:
            alpha_amp = (np.log(10) / 20.0) * TL / probe_separation
            
        # Store results
        self.results = {
            'frequencies': self.frequencies,
            'pin_magnitude': pin_mag,
            'pout_magnitude': pout_mag,
            'transmission_loss': TL,
            'probe_separation': probe_separation
        }
        
        if alpha_amp is not None:
            self.results['alpha_amplitude'] = alpha_amp
            
        # Calculate intensity-based absorption coefficient
        alpha_int = (np.log(10) / 10.0) * TL / probe_separation if probe_separation else None
        if alpha_int is not None:
            self.results['alpha_intensity'] = alpha_int
            
        print(f"Transmission loss calculated:")
        print(f"  Frequency range: {self.frequencies[0]:.1f} - {self.frequencies[-1]:.1f} Hz")
        print(f"  TL range: {np.min(TL):.2f} - {np.max(TL):.2f} dB")
        if probe_separation:
            print(f"  Probe separation: {probe_separation:.3f} m")
            print(f"  Alpha range: {np.min(alpha_amp):.4f} - {np.max(alpha_amp):.4f} /m")
            
        return self.results
        
    def calculate_phase_velocity(self, probe_in='PROBE_IN', probe_out='PROBE_OUT', 
                                probe_separation=None):
        """
        Calculate phase velocity from probe data.
        
        Parameters:
        -----------
        probe_in : str
            Name of input probe set
        probe_out : str
            Name of output probe set
        probe_separation : float
            Distance between probes in meters
            
        Returns:
        --------
        numpy.ndarray : Phase velocity vs frequency
        """
        if not self.probe_data:
            raise ValueError("No probe data available")
            
        if probe_separation is None:
            raise ValueError("Probe separation required for phase velocity calculation")
            
        # Get phase data
        phase_in = self.probe_data[probe_in]['phase']
        phase_out = self.probe_data[probe_out]['phase']
        
        # Calculate phase difference (unwrap to handle 2π jumps)
        phase_diff = np.unwrap(phase_out - phase_in)
        
        # Calculate wavenumber
        k = -phase_diff / probe_separation  # Negative because wave travels from in to out
        
        # Calculate phase velocity
        omega = 2 * np.pi * self.frequencies
        phase_velocity = omega / k
        
        # Handle division by zero
        phase_velocity = np.where(np.abs(k) > 1e-10, phase_velocity, np.inf)
        
        self.results['phase_velocity'] = phase_velocity
        self.results['wavenumber'] = k
        self.results['phase_difference'] = phase_diff
        
        print(f"Phase velocity calculated:")
        print(f"  Range: {np.min(phase_velocity[np.isfinite(phase_velocity)]):.1f} - "
              f"{np.max(phase_velocity[np.isfinite(phase_velocity)]):.1f} m/s")
              
        return phase_velocity
        
    def analyze_frequency_response(self, frequency_bands=None):
        """
        Analyze transmission loss in frequency bands.
        
        Parameters:
        -----------
        frequency_bands : list of tuples
            [(f_low, f_high, 'band_name'), ...] 
            Default: standard octave bands
            
        Returns:
        --------
        dict : Band-averaged results
        """
        if not self.results:
            raise ValueError("No results available. Calculate transmission loss first.")
            
        if frequency_bands is None:
            # Standard 1/3 octave bands (simplified)
            frequency_bands = [
                (100, 200, '100-200 Hz'),
                (200, 400, '200-400 Hz'),
                (400, 800, '400-800 Hz'),
                (800, 1600, '800-1600 Hz'),
                (1600, 3200, '1600-3200 Hz'),
                (3200, 6400, '3200-6400 Hz')
            ]
            
        band_results = {}
        
        for f_low, f_high, band_name in frequency_bands:
            # Find frequencies in band
            mask = (self.frequencies >= f_low) & (self.frequencies <= f_high)
            
            if np.any(mask):
                band_freqs = self.frequencies[mask]
                band_TL = self.results['transmission_loss'][mask]
                
                band_results[band_name] = {
                    'frequency_range': (f_low, f_high),
                    'frequencies': band_freqs,
                    'mean_TL': np.mean(band_TL),
                    'std_TL': np.std(band_TL),
                    'min_TL': np.min(band_TL),
                    'max_TL': np.max(band_TL),
                    'num_points': len(band_freqs)
                }
                
                if 'alpha_amplitude' in self.results:
                    band_alpha = self.results['alpha_amplitude'][mask]
                    band_results[band_name]['mean_alpha'] = np.mean(band_alpha)
                    band_results[band_name]['std_alpha'] = np.std(band_alpha)
                    
        print(f"Frequency band analysis completed for {len(band_results)} bands")
        
        return band_results
        
    def export_results(self, filename, format='csv'):
        """
        Export results to file.
        
        Parameters:
        -----------
        filename : str
            Output filename
        format : str
            Export format ('csv', 'txt', 'json')
        """
        if not self.results:
            raise ValueError("No results to export")
            
        if format.lower() == 'csv':
            self._export_csv(filename)
        elif format.lower() == 'txt':
            self._export_txt(filename)
        elif format.lower() == 'json':
            self._export_json(filename)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def _export_csv(self, filename):
        """Export results to CSV format."""
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            header = ['Frequency_Hz', 'Pin_Magnitude', 'Pout_Magnitude', 'Transmission_Loss_dB']
            if 'alpha_amplitude' in self.results:
                header.append('Alpha_Amplitude_per_m')
            if 'alpha_intensity' in self.results:
                header.append('Alpha_Intensity_per_m')
            if 'phase_velocity' in self.results:
                header.append('Phase_Velocity_m_per_s')
                
            writer.writerow(header)
            
            # Data
            for i in range(len(self.frequencies)):
                row = [
                    self.frequencies[i],
                    self.results['pin_magnitude'][i],
                    self.results['pout_magnitude'][i],
                    self.results['transmission_loss'][i]
                ]
                
                if 'alpha_amplitude' in self.results:
                    row.append(self.results['alpha_amplitude'][i])
                if 'alpha_intensity' in self.results:
                    row.append(self.results['alpha_intensity'][i])
                if 'phase_velocity' in self.results:
                    row.append(self.results['phase_velocity'][i])
                    
                writer.writerow(row)
                
        print(f"Results exported to CSV: {filename}")
        
    def _export_txt(self, filename):
        """Export results to text format."""
        with open(filename, 'w') as f:
            f.write("Abaqus Acoustic Transmission Loss Results\n")
            f.write("=" * 50 + "\n\n")
            
            if self.odb_path:
                f.write(f"ODB file: {self.odb_path}\n")
            f.write(f"Number of frequencies: {len(self.frequencies)}\n")
            f.write(f"Frequency range: {self.frequencies[0]:.1f} - {self.frequencies[-1]:.1f} Hz\n")
            
            if 'probe_separation' in self.results and self.results['probe_separation']:
                f.write(f"Probe separation: {self.results['probe_separation']:.3f} m\n")
                
            f.write("\n" + "=" * 50 + "\n")
            f.write("Data:\n")
            f.write("=" * 50 + "\n")
            
            # Column headers
            f.write(f"{'Freq (Hz)':>10} {'Pin':>12} {'Pout':>12} {'TL (dB)':>10}")
            if 'alpha_amplitude' in self.results:
                f.write(f" {'Alpha (/m)':>12}")
            f.write("\n")
            
            # Data rows
            for i in range(len(self.frequencies)):
                f.write(f"{self.frequencies[i]:10.1f} "
                       f"{self.results['pin_magnitude'][i]:12.6e} "
                       f"{self.results['pout_magnitude'][i]:12.6e} "
                       f"{self.results['transmission_loss'][i]:10.3f}")
                       
                if 'alpha_amplitude' in self.results:
                    f.write(f" {self.results['alpha_amplitude'][i]:12.6f}")
                f.write("\n")
                
        print(f"Results exported to text: {filename}")
        
    def _export_json(self, filename):
        """Export results to JSON format."""
        import json
        
        # Convert numpy arrays to lists for JSON serialization
        export_data = {}
        for key, value in self.results.items():
            if isinstance(value, np.ndarray):
                export_data[key] = value.tolist()
            else:
                export_data[key] = value
                
        # Add metadata
        export_data['metadata'] = {
            'odb_path': self.odb_path,
            'num_frequencies': len(self.frequencies),
            'frequency_range': [float(self.frequencies[0]), float(self.frequencies[-1])]
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        print(f"Results exported to JSON: {filename}")
        
    def plot_results(self, save_plots=True, show_plots=False, output_dir='.'):
        """
        Create plots of transmission loss results.
        
        Parameters:
        -----------
        save_plots : bool
            Save plots to files
        show_plots : bool
            Display plots interactively
        output_dir : str
            Directory for saved plots
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Warning: matplotlib not available. Cannot create plots.")
            return
            
        if not self.results:
            raise ValueError("No results to plot")
            
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Acoustic Transmission Loss Analysis', fontsize=16)
        
        # Plot 1: Transmission Loss
        axes[0, 0].semilogx(self.frequencies, self.results['transmission_loss'], 'b-', linewidth=2)
        axes[0, 0].set_xlabel('Frequency (Hz)')
        axes[0, 0].set_ylabel('Transmission Loss (dB)')
        axes[0, 0].set_title('Transmission Loss vs Frequency')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Pressure Magnitudes
        axes[0, 1].loglog(self.frequencies, self.results['pin_magnitude'], 'r-', 
                         label='Input', linewidth=2)
        axes[0, 1].loglog(self.frequencies, self.results['pout_magnitude'], 'g-', 
                         label='Output', linewidth=2)
        axes[0, 1].set_xlabel('Frequency (Hz)')
        axes[0, 1].set_ylabel('Pressure Magnitude (Pa)')
        axes[0, 1].set_title('Pressure Magnitudes')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Absorption Coefficient (if available)
        if 'alpha_amplitude' in self.results:
            axes[1, 0].semilogx(self.frequencies, self.results['alpha_amplitude'], 'k-', linewidth=2)
            axes[1, 0].set_xlabel('Frequency (Hz)')
            axes[1, 0].set_ylabel('Absorption Coefficient (/m)')
            axes[1, 0].set_title('Absorption Coefficient vs Frequency')
            axes[1, 0].grid(True, alpha=0.3)
        else:
            axes[1, 0].text(0.5, 0.5, 'Absorption coefficient\nnot calculated\n(probe separation needed)', 
                           ha='center', va='center', transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('Absorption Coefficient')
            
        # Plot 4: Phase Velocity (if available)
        if 'phase_velocity' in self.results:
            # Filter out infinite values for plotting
            finite_mask = np.isfinite(self.results['phase_velocity'])
            if np.any(finite_mask):
                axes[1, 1].semilogx(self.frequencies[finite_mask], 
                                   self.results['phase_velocity'][finite_mask], 'm-', linewidth=2)
                axes[1, 1].set_xlabel('Frequency (Hz)')
                axes[1, 1].set_ylabel('Phase Velocity (m/s)')
                axes[1, 1].set_title('Phase Velocity vs Frequency')
                axes[1, 1].grid(True, alpha=0.3)
            else:
                axes[1, 1].text(0.5, 0.5, 'Phase velocity\ndata not valid', 
                               ha='center', va='center', transform=axes[1, 1].transAxes)
        else:
            axes[1, 1].text(0.5, 0.5, 'Phase velocity\nnot calculated', 
                           ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Phase Velocity')
            
        plt.tight_layout()
        
        if save_plots:
            plot_filename = os.path.join(output_dir, 'transmission_loss_analysis.png')
            plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
            print(f"Plot saved: {plot_filename}")
            
        if show_plots:
            plt.show()
        else:
            plt.close()
            
    def quality_assessment(self):
        """
        Perform quality assessment of results.
        
        Returns:
        --------
        dict : Quality assessment metrics
        """
        if not self.results:
            raise ValueError("No results available for assessment")
            
        assessment = {}
        
        # Check for data validity
        TL = self.results['transmission_loss']
        pin = self.results['pin_magnitude']
        pout = self.results['pout_magnitude']
        
        # Basic statistics
        assessment['data_points'] = len(self.frequencies)
        assessment['frequency_range'] = (float(self.frequencies[0]), float(self.frequencies[-1]))
        assessment['TL_range'] = (float(np.min(TL)), float(np.max(TL)))
        assessment['TL_mean'] = float(np.mean(TL))
        assessment['TL_std'] = float(np.std(TL))
        
        # Quality checks
        assessment['warnings'] = []
        
        # Check for zero pressures
        zero_pin = np.sum(pin == 0)
        zero_pout = np.sum(pout == 0)
        if zero_pin > 0:
            assessment['warnings'].append(f"{zero_pin} zero input pressures detected")
        if zero_pout > 0:
            assessment['warnings'].append(f"{zero_pout} zero output pressures detected")
            
        # Check for negative TL (gain instead of loss)
        negative_TL = np.sum(TL < 0)
        if negative_TL > 0:
            assessment['warnings'].append(f"{negative_TL} frequencies show gain instead of loss")
            
        # Check for excessive TL (possible numerical issues)
        excessive_TL = np.sum(TL > 100)  # > 100 dB seems excessive
        if excessive_TL > 0:
            assessment['warnings'].append(f"{excessive_TL} frequencies show TL > 100 dB")
            
        # Check frequency spacing consistency
        freq_diffs = np.diff(self.frequencies)
        if len(set(np.round(freq_diffs, 1))) > 1:
            assessment['warnings'].append("Inconsistent frequency spacing detected")
            
        # Overall quality score (0-100)
        score = 100
        score -= len(assessment['warnings']) * 10  # Penalty for warnings
        score -= min(zero_pin + zero_pout, 50)     # Penalty for zero values
        assessment['quality_score'] = max(score, 0)
        
        print(f"Quality Assessment:")
        print(f"  Data points: {assessment['data_points']}")
        print(f"  Frequency range: {assessment['frequency_range'][0]:.1f} - {assessment['frequency_range'][1]:.1f} Hz")
        print(f"  TL range: {assessment['TL_range'][0]:.2f} - {assessment['TL_range'][1]:.2f} dB")
        print(f"  Quality score: {assessment['quality_score']}/100")
        
        if assessment['warnings']:
            print("  Warnings:")
            for warning in assessment['warnings']:
                print(f"    - {warning}")
        else:
            print("  No warnings detected")
            
        return assessment


# Standalone functions for batch processing
def process_odb_file(odb_path, probe_separation=None, output_prefix=None):
    """
    Process a single ODB file and generate all outputs.
    
    Parameters:
    -----------
    odb_path : str
        Path to ODB file
    probe_separation : float
        Distance between probes in meters
    output_prefix : str
        Prefix for output files (default: ODB filename without extension)
        
    Returns:
    --------
    dict : Processing results
    """
    if output_prefix is None:
        output_prefix = os.path.splitext(os.path.basename(odb_path))[0]
        
    print(f"Processing ODB file: {odb_path}")
    
    # Create post-processor
    processor = AcousticPostProcessor(odb_path)
    
    try:
        # Open ODB and extract data
        processor.open_odb()
        processor.extract_probe_data()
        
        # Calculate transmission loss
        results = processor.calculate_transmission_loss(probe_separation=probe_separation)
        
        # Calculate phase velocity if probe separation is known
        if probe_separation:
            processor.calculate_phase_velocity(probe_separation=probe_separation)
            
        # Frequency band analysis
        band_results = processor.analyze_frequency_response()
        
        # Quality assessment
        quality = processor.quality_assessment()
        
        # Export results
        processor.export_results(f"{output_prefix}_results.csv", format='csv')
        processor.export_results(f"{output_prefix}_results.txt", format='txt')
        
        # Create plots
        if MATPLOTLIB_AVAILABLE:
            processor.plot_results(save_plots=True, show_plots=False)
            
        processor.close_odb()
        
        print(f"Processing completed successfully for {odb_path}")
        
        return {
            'results': results,
            'band_results': band_results,
            'quality': quality,
            'output_prefix': output_prefix
        }
        
    except Exception as e:
        print(f"Error processing {odb_path}: {e}")
        if processor.odb:
            processor.close_odb()
        return None


def batch_process_odb_files(odb_directory, probe_separation=None, pattern="*.odb"):
    """
    Process multiple ODB files in a directory.
    
    Parameters:
    -----------
    odb_directory : str
        Directory containing ODB files
    probe_separation : float
        Distance between probes in meters
    pattern : str
        File pattern to match (default: "*.odb")
        
    Returns:
    --------
    dict : Results for all processed files
    """
    import glob
    
    odb_files = glob.glob(os.path.join(odb_directory, pattern))
    
    if not odb_files:
        print(f"No ODB files found in {odb_directory} matching {pattern}")
        return {}
        
    print(f"Found {len(odb_files)} ODB files to process")
    
    all_results = {}
    
    for odb_file in odb_files:
        result = process_odb_file(odb_file, probe_separation=probe_separation)
        if result:
            all_results[os.path.basename(odb_file)] = result
            
    print(f"Batch processing completed. Processed {len(all_results)} files successfully.")
    
    return all_results


if __name__ == "__main__":
    print("Abaqus Acoustic Post-Processing Tools")
    print("=" * 40)
    
    # Example usage
    if len(sys.argv) > 1:
        odb_path = sys.argv[1]
        probe_sep = float(sys.argv[2]) if len(sys.argv) > 2 else None
        
        print(f"Processing: {odb_path}")
        result = process_odb_file(odb_path, probe_separation=probe_sep)
        
        if result:
            print("Processing completed successfully!")
        else:
            print("Processing failed!")
    else:
        print("Usage: python post_processing_tools.py <odb_file> [probe_separation]")
        print("Example: python post_processing_tools.py simulation.odb 6.0")