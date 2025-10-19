#!/usr/bin/env python
"""
Post-Processing Utilities for Acoustic Transmission Loss Analysis
================================================================

This module provides utilities for post-processing Abaqus acoustic simulation
results, including calculation of transmission loss, absorption coefficient,
and visualization tools.

Author: Generated for acoustic transmission loss analysis
Date: 2024
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import pandas as pd
import os

class AcousticPostProcessor:
    """Post-process acoustic simulation results"""
    
    def __init__(self, results_data=None):
        """
        Initialize post-processor
        
        Args:
            results_data: Dictionary with simulation results
        """
        self.results = results_data
        self.frequency = None
        self.pressure_in = None
        self.pressure_out = None
        self.TL = None
        self.alpha_amp = None
        
        if results_data is not None:
            self.load_results(results_data)
            
    def load_results(self, results_data):
        """Load results from simulation data"""
        self.frequency = np.array(results_data['frequency'])
        self.pressure_in = np.array(results_data['pressure_in'])
        self.pressure_out = np.array(results_data['pressure_out'])
        
        # Calculate TL and alpha
        self.calculate_transmission_loss()
        self.calculate_absorption_coefficient()
        
    def calculate_transmission_loss(self):
        """Calculate transmission loss in dB"""
        if self.pressure_in is None or self.pressure_out is None:
            raise ValueError("Pressure data not loaded")
            
        # Avoid division by zero
        pressure_out_safe = np.where(self.pressure_out == 0, 1e-10, self.pressure_out)
        
        # Calculate TL = 20*log10(|P_in|/|P_out|)
        self.TL = 20 * np.log10(np.abs(self.pressure_in) / np.abs(pressure_out_safe))
        
        return self.TL
        
    def calculate_absorption_coefficient(self, delta_x=8.0):
        """
        Calculate absorption coefficient
        
        Args:
            delta_x: Distance between probe points (m)
        """
        if self.TL is None:
            self.calculate_transmission_loss()
            
        # alpha_amp = (ln(10)/20) * TL / delta_x
        self.alpha_amp = (np.log(10) / 20.0) * self.TL / delta_x
        
        return self.alpha_amp
        
    def calculate_intensity_absorption(self, delta_x=8.0):
        """
        Calculate intensity-based absorption coefficient
        
        Args:
            delta_x: Distance between probe points (m)
        """
        if self.TL is None:
            self.calculate_transmission_loss()
            
        # alpha_int = (ln(10)/10) * TL / delta_x
        alpha_int = (np.log(10) / 10.0) * self.TL / delta_x
        
        return alpha_int
        
    def smooth_data(self, window_size=5):
        """Apply smoothing to reduce noise in results"""
        if self.TL is None:
            self.calculate_transmission_loss()
            
        # Apply moving average filter
        self.TL_smooth = signal.savgol_filter(self.TL, window_size, 2)
        
        if self.alpha_amp is not None:
            self.alpha_amp_smooth = signal.savgol_filter(self.alpha_amp, window_size, 2)
            
        return self.TL_smooth, self.alpha_amp_smooth
        
    def plot_transmission_loss(self, smooth=True, save_path=None):
        """Plot transmission loss vs frequency"""
        plt.figure(figsize=(10, 6))
        
        if smooth and hasattr(self, 'TL_smooth'):
            plt.plot(self.frequency, self.TL_smooth, 'b-', linewidth=2, label='Smoothed')
            plt.plot(self.frequency, self.TL, 'r--', alpha=0.7, label='Raw')
        else:
            plt.plot(self.frequency, self.TL, 'b-', linewidth=2)
            
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Transmission Loss (dB)')
        plt.title('Acoustic Transmission Loss')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
    def plot_absorption_coefficient(self, smooth=True, save_path=None):
        """Plot absorption coefficient vs frequency"""
        plt.figure(figsize=(10, 6))
        
        if smooth and hasattr(self, 'alpha_amp_smooth'):
            plt.plot(self.frequency, self.alpha_amp_smooth, 'g-', linewidth=2, label='Smoothed')
            plt.plot(self.frequency, self.alpha_amp, 'r--', alpha=0.7, label='Raw')
        else:
            plt.plot(self.frequency, self.alpha_amp, 'g-', linewidth=2)
            
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Absorption Coefficient (1/m)')
        plt.title('Acoustic Absorption Coefficient')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
    def plot_pressure_amplitudes(self, save_path=None):
        """Plot pressure amplitudes at probe locations"""
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        plt.plot(self.frequency, np.abs(self.pressure_in), 'b-', linewidth=2)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Pressure Amplitude (Pa)')
        plt.title('Inlet Pressure')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(1, 2, 2)
        plt.plot(self.frequency, np.abs(self.pressure_out), 'r-', linewidth=2)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Pressure Amplitude (Pa)')
        plt.title('Outlet Pressure')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
    def plot_comparison(self, other_results, labels=None, save_path=None):
        """Compare results from different simulations"""
        if labels is None:
            labels = ['Simulation 1', 'Simulation 2']
            
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        plt.plot(self.frequency, self.TL, 'b-', linewidth=2, label=labels[0])
        if hasattr(other_results, 'TL'):
            plt.plot(other_results.frequency, other_results.TL, 'r-', linewidth=2, label=labels[1])
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Transmission Loss (dB)')
        plt.title('Transmission Loss Comparison')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.subplot(1, 2, 2)
        plt.plot(self.frequency, self.alpha_amp, 'b-', linewidth=2, label=labels[0])
        if hasattr(other_results, 'alpha_amp'):
            plt.plot(other_results.frequency, other_results.alpha_amp, 'r-', linewidth=2, label=labels[1])
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Absorption Coefficient (1/m)')
        plt.title('Absorption Coefficient Comparison')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
    def export_results(self, filename="acoustic_results.csv"):
        """Export results to CSV file"""
        data = {
            'Frequency_Hz': self.frequency,
            'Pressure_In_Pa': np.abs(self.pressure_in),
            'Pressure_Out_Pa': np.abs(self.pressure_out),
            'Transmission_Loss_dB': self.TL,
            'Absorption_Coefficient_1m': self.alpha_amp
        }
        
        if hasattr(self, 'TL_smooth'):
            data['TL_Smooth_dB'] = self.TL_smooth
        if hasattr(self, 'alpha_amp_smooth'):
            data['Alpha_Smooth_1m'] = self.alpha_amp_smooth
            
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Results exported to {filename}")
        
    def calculate_statistics(self):
        """Calculate statistical measures of the results"""
        stats = {}
        
        if self.TL is not None:
            stats['TL_mean'] = np.mean(self.TL)
            stats['TL_std'] = np.std(self.TL)
            stats['TL_min'] = np.min(self.TL)
            stats['TL_max'] = np.max(self.TL)
            
        if self.alpha_amp is not None:
            stats['alpha_mean'] = np.mean(self.alpha_amp)
            stats['alpha_std'] = np.std(self.alpha_amp)
            stats['alpha_min'] = np.min(self.alpha_amp)
            stats['alpha_max'] = np.max(self.alpha_amp)
            
        return stats
        
    def validate_results(self, expected_TL_range=(0, 50), expected_alpha_range=(0, 1)):
        """
        Validate results for reasonable values
        
        Args:
            expected_TL_range: Expected TL range in dB
            expected_alpha_range: Expected alpha range in 1/m
        """
        warnings = []
        
        if self.TL is not None:
            if np.any(self.TL < expected_TL_range[0]) or np.any(self.TL > expected_TL_range[1]):
                warnings.append(f"TL values outside expected range {expected_TL_range}")
                
        if self.alpha_amp is not None:
            if np.any(self.alpha_amp < expected_alpha_range[0]) or np.any(self.alpha_amp > expected_alpha_range[1]):
                warnings.append(f"Alpha values outside expected range {expected_alpha_range}")
                
        if np.any(np.isnan(self.TL)) or np.any(np.isinf(self.TL)):
            warnings.append("NaN or Inf values found in TL")
            
        if np.any(np.isnan(self.alpha_amp)) or np.any(np.isinf(self.alpha_amp)):
            warnings.append("NaN or Inf values found in alpha")
            
        return warnings


def load_abaqus_results(odb_path):
    """
    Load results directly from Abaqus ODB file
    
    Args:
        odb_path: Path to .odb file
        
    Returns:
        AcousticPostProcessor object with loaded results
    """
    try:
        from abaqus import *
        from abaqusConstants import *
        from odbAccess import openOdb
        
        # Open ODB
        odb = openOdb(odb_path)
        
        # Get step
        step = odb.steps['SSD_Step']
        
        # Initialize arrays
        frequencies = []
        pressure_in = []
        pressure_out = []
        
        # Extract data from each frame
        for frame in step.frames:
            freq = frame.frequency
            frequencies.append(freq)
            
            # Get pressure at probe locations
            try:
                p_in_field = frame.fieldOutputs['P'].getSubset(region=odb.rootAssembly.nodeSets['PROBE_IN'])
                p_out_field = frame.fieldOutputs['P'].getSubset(region=odb.rootAssembly.nodeSets['PROBE_OUT'])
                
                # Calculate average magnitude
                p_in_mag = np.mean([np.sqrt(v.data[0]**2 + v.data[1]**2) for v in p_in_field.values])
                p_out_mag = np.mean([np.sqrt(v.data[0]**2 + v.data[1]**2) for v in p_out_field.values])
                
                pressure_in.append(p_in_mag)
                pressure_out.append(p_out_mag)
                
            except:
                # Fallback values if extraction fails
                pressure_in.append(1.0)
                pressure_out.append(1.0)
        
        # Close ODB
        odb.close()
        
        # Create results dictionary
        results_data = {
            'frequency': np.array(frequencies),
            'pressure_in': np.array(pressure_in),
            'pressure_out': np.array(pressure_out)
        }
        
        return AcousticPostProcessor(results_data)
        
    except Exception as e:
        print(f"Error loading ODB file: {e}")
        return None


def batch_process_results(result_files, output_dir="results"):
    """
    Process multiple result files in batch
    
    Args:
        result_files: List of result file paths
        output_dir: Output directory for processed results
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    processors = []
    
    for i, file_path in enumerate(result_files):
        print(f"Processing file {i+1}/{len(result_files)}: {file_path}")
        
        if file_path.endswith('.odb'):
            processor = load_abaqus_results(file_path)
        elif file_path.endswith('.csv'):
            data = pd.read_csv(file_path)
            results_data = {
                'frequency': data['Frequency_Hz'].values,
                'pressure_in': data['Pressure_In_Pa'].values,
                'pressure_out': data['Pressure_Out_Pa'].values
            }
            processor = AcousticPostProcessor(results_data)
        else:
            print(f"Unsupported file format: {file_path}")
            continue
            
        if processor is not None:
            processors.append(processor)
            
            # Generate plots
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            processor.plot_transmission_loss(save_path=os.path.join(output_dir, f"{base_name}_TL.png"))
            processor.plot_absorption_coefficient(save_path=os.path.join(output_dir, f"{base_name}_alpha.png"))
            processor.plot_pressure_amplitudes(save_path=os.path.join(output_dir, f"{base_name}_pressure.png"))
            
            # Export results
            processor.export_results(os.path.join(output_dir, f"{base_name}_processed.csv"))
            
    return processors


if __name__ == "__main__":
    # Example usage
    print("Acoustic Post-Processing Utilities")
    print("="*40)
    
    # Create sample data for demonstration
    freq = np.linspace(100, 5000, 200)
    pressure_in = 1000 * np.exp(-0.001 * freq)  # Decaying pressure
    pressure_out = pressure_in * 0.1  # 20 dB loss
    
    sample_data = {
        'frequency': freq,
        'pressure_in': pressure_in,
        'pressure_out': pressure_out
    }
    
    # Create post-processor
    processor = AcousticPostProcessor(sample_data)
    
    # Generate plots
    processor.plot_transmission_loss()
    processor.plot_absorption_coefficient()
    processor.plot_pressure_amplitudes()
    
    # Export results
    processor.export_results("sample_results.csv")
    
    # Print statistics
    stats = processor.calculate_statistics()
    print("\nStatistics:")
    for key, value in stats.items():
        print(f"  {key}: {value:.4f}")
        
    # Validate results
    warnings = processor.validate_results()
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("\nNo validation warnings")