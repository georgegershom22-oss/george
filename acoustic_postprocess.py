#!/usr/bin/env python3
"""
Abaqus Acoustic Transmission Loss Post-Processing Script

This script processes Abaqus ODB files from acoustic transmission loss simulations
and calculates:
1. Transmission Loss (TL) as a function of frequency
2. Attenuation coefficient (alpha) as a function of frequency
3. Generates plots and exports data to CSV

Usage:
    python acoustic_postprocess.py job_name.odb [options]

Requirements:
    - Abaqus Python environment (abaqus python or abaqus cae -noGUI)
    - numpy, matplotlib (if available in Abaqus Python)
    - ODB file with pressure field output and history output at probe locations

Author: Generated for Abaqus Acoustic Simulation
"""

import sys
import os
import math
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("Warning: numpy not available, using basic Python math")

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available, no plots will be generated")

# Abaqus-specific imports
try:
    from odbAccess import openOdb
    from abaqusConstants import *
    HAS_ABAQUS = True
except ImportError:
    HAS_ABAQUS = False
    print("Warning: Abaqus odbAccess not available. This script must be run with 'abaqus python'")


class AcousticPostProcessor:
    """
    Post-processor for Abaqus acoustic transmission loss simulations
    """
    
    def __init__(self, odb_path, probe_in_name='PROBE_IN', probe_out_name='PROBE_OUT'):
        """
        Initialize the post-processor
        
        Args:
            odb_path (str): Path to the ODB file
            probe_in_name (str): Name of input probe node set
            probe_out_name (str): Name of output probe node set
        """
        self.odb_path = odb_path
        self.probe_in_name = probe_in_name
        self.probe_out_name = probe_out_name
        self.odb = None
        self.frequencies = []
        self.p_in_magnitudes = []
        self.p_out_magnitudes = []
        self.transmission_loss = []
        self.attenuation_coeff = []
        
    def open_odb(self):
        """Open the ODB file"""
        if not HAS_ABAQUS:
            raise ImportError("Abaqus odbAccess not available")
        
        if not os.path.exists(self.odb_path):
            raise FileNotFoundError(f"ODB file not found: {self.odb_path}")
        
        print(f"Opening ODB file: {self.odb_path}")
        self.odb = openOdb(self.odb_path)
        print(f"ODB opened successfully")
        
    def close_odb(self):
        """Close the ODB file"""
        if self.odb:
            self.odb.close()
            print("ODB closed")
    
    def extract_pressure_data(self, step_name=None):
        """
        Extract pressure data from probe locations
        
        Args:
            step_name (str): Name of the step to process (if None, uses first step)
        """
        if not self.odb:
            raise RuntimeError("ODB not opened")
        
        # Get the step
        if step_name is None:
            step_name = list(self.odb.steps.keys())[0]
        
        if step_name not in self.odb.steps:
            raise ValueError(f"Step '{step_name}' not found in ODB")
        
        step = self.odb.steps[step_name]
        print(f"Processing step: {step_name}")
        print(f"Number of frames: {len(step.frames)}")
        
        # Get node sets
        try:
            probe_in_nodes = self.odb.rootAssembly.nodeSets[self.probe_in_name]
            probe_out_nodes = self.odb.rootAssembly.nodeSets[self.probe_out_name]
        except KeyError as e:
            print(f"Available node sets: {list(self.odb.rootAssembly.nodeSets.keys())}")
            raise KeyError(f"Node set not found: {e}")
        
        print(f"Input probe nodes: {len(probe_in_nodes.nodes)} nodes")
        print(f"Output probe nodes: {len(probe_out_nodes.nodes)} nodes")
        
        # Process each frequency frame
        for frame in step.frames:
            if hasattr(frame, 'frequency'):
                freq = frame.frequency
                self.frequencies.append(freq)
                
                # Get pressure field output
                if 'P' not in frame.fieldOutputs:
                    raise ValueError("Pressure field output 'P' not found in frame")
                
                pressure_field = frame.fieldOutputs['P']
                
                # Extract pressure at input probe
                p_in_subset = pressure_field.getSubset(region=probe_in_nodes)
                p_in_values = []
                for value in p_in_subset.values:
                    # Pressure is complex: value.data = [real, imaginary]
                    real_part = value.data[0]
                    imag_part = value.data[1]
                    magnitude = math.sqrt(real_part**2 + imag_part**2)
                    p_in_values.append(magnitude)
                
                # Extract pressure at output probe
                p_out_subset = pressure_field.getSubset(region=probe_out_nodes)
                p_out_values = []
                for value in p_out_subset.values:
                    real_part = value.data[0]
                    imag_part = value.data[1]
                    magnitude = math.sqrt(real_part**2 + imag_part**2)
                    p_out_values.append(magnitude)
                
                # Average over probe nodes
                p_in_avg = sum(p_in_values) / len(p_in_values)
                p_out_avg = sum(p_out_values) / len(p_out_values)
                
                self.p_in_magnitudes.append(p_in_avg)
                self.p_out_magnitudes.append(p_out_avg)
                
                print(f"Frequency: {freq:8.1f} Hz, P_in: {p_in_avg:.2e} Pa, P_out: {p_out_avg:.2e} Pa")
        
        print(f"Extracted data for {len(self.frequencies)} frequencies")
    
    def calculate_transmission_loss(self, probe_separation_m=190.0):
        """
        Calculate transmission loss and attenuation coefficient
        
        Args:
            probe_separation_m (float): Distance between probes in meters
        """
        if not self.frequencies:
            raise RuntimeError("No frequency data available")
        
        self.transmission_loss = []
        self.attenuation_coeff = []
        
        for i, freq in enumerate(self.frequencies):
            p_in = self.p_in_magnitudes[i]
            p_out = self.p_out_magnitudes[i]
            
            if p_out > 0 and p_in > 0:
                # Transmission Loss in dB
                tl = 20.0 * math.log10(p_in / p_out)
                self.transmission_loss.append(tl)
                
                # Attenuation coefficient (amplitude-based)
                # alpha = (ln(10)/20) * TL / Delta_x
                alpha = (math.log(10) / 20.0) * tl / probe_separation_m
                self.attenuation_coeff.append(alpha)
            else:
                self.transmission_loss.append(0.0)
                self.attenuation_coeff.append(0.0)
                print(f"Warning: Zero pressure at frequency {freq} Hz")
        
        print(f"Calculated TL and attenuation for {len(self.transmission_loss)} frequencies")
    
    def export_to_csv(self, output_file='acoustic_results.csv'):
        """
        Export results to CSV file
        
        Args:
            output_file (str): Output CSV filename
        """
        if not self.frequencies:
            raise RuntimeError("No data to export")
        
        with open(output_file, 'w') as f:
            f.write("Frequency_Hz,P_in_Pa,P_out_Pa,Transmission_Loss_dB,Attenuation_Coeff_per_m\n")
            for i, freq in enumerate(self.frequencies):
                f.write(f"{freq:.2f},{self.p_in_magnitudes[i]:.6e},"
                       f"{self.p_out_magnitudes[i]:.6e},{self.transmission_loss[i]:.4f},"
                       f"{self.attenuation_coeff[i]:.6e}\n")
        
        print(f"Results exported to: {output_file}")
    
    def plot_results(self, output_dir='plots'):
        """
        Generate plots of the results
        
        Args:
            output_dir (str): Directory to save plots
        """
        if not HAS_MATPLOTLIB:
            print("Matplotlib not available, skipping plots")
            return
        
        if not self.frequencies:
            raise RuntimeError("No data to plot")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Plot 1: Transmission Loss vs Frequency
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 2, 1)
        plt.plot(self.frequencies, self.transmission_loss, 'b-', linewidth=2)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Transmission Loss (dB)')
        plt.title('Transmission Loss vs Frequency')
        plt.grid(True, alpha=0.3)
        
        # Plot 2: Attenuation Coefficient vs Frequency
        plt.subplot(2, 2, 2)
        plt.plot(self.frequencies, self.attenuation_coeff, 'r-', linewidth=2)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Attenuation Coefficient (1/m)')
        plt.title('Attenuation Coefficient vs Frequency')
        plt.grid(True, alpha=0.3)
        
        # Plot 3: Pressure Magnitudes
        plt.subplot(2, 2, 3)
        plt.semilogy(self.frequencies, self.p_in_magnitudes, 'g-', label='Input', linewidth=2)
        plt.semilogy(self.frequencies, self.p_out_magnitudes, 'm-', label='Output', linewidth=2)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Pressure Magnitude (Pa)')
        plt.title('Pressure Magnitudes vs Frequency')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot 4: Pressure Ratio
        plt.subplot(2, 2, 4)
        pressure_ratio = [p_in/p_out if p_out > 0 else 0 
                         for p_in, p_out in zip(self.p_in_magnitudes, self.p_out_magnitudes)]
        plt.semilogy(self.frequencies, pressure_ratio, 'k-', linewidth=2)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Pressure Ratio (P_in/P_out)')
        plt.title('Pressure Ratio vs Frequency')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plot_file = os.path.join(output_dir, 'acoustic_transmission_loss.png')
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Plots saved to: {plot_file}")
    
    def print_summary(self):
        """Print summary statistics"""
        if not self.frequencies:
            print("No data available for summary")
            return
        
        print("\n" + "="*60)
        print("ACOUSTIC TRANSMISSION LOSS ANALYSIS SUMMARY")
        print("="*60)
        print(f"Frequency range: {min(self.frequencies):.1f} - {max(self.frequencies):.1f} Hz")
        print(f"Number of frequencies: {len(self.frequencies)}")
        print(f"Frequency increment: {self.frequencies[1] - self.frequencies[0]:.1f} Hz")
        print()
        print(f"Transmission Loss (dB):")
        print(f"  Minimum: {min(self.transmission_loss):.2f} dB")
        print(f"  Maximum: {max(self.transmission_loss):.2f} dB")
        print(f"  Average: {sum(self.transmission_loss)/len(self.transmission_loss):.2f} dB")
        print()
        print(f"Attenuation Coefficient (1/m):")
        print(f"  Minimum: {min(self.attenuation_coeff):.6f} 1/m")
        print(f"  Maximum: {max(self.attenuation_coeff):.6f} 1/m")
        print(f"  Average: {sum(self.attenuation_coeff)/len(self.attenuation_coeff):.6f} 1/m")
        print("="*60)


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python acoustic_postprocess.py job_name.odb [probe_separation_m]")
        print("Example: abaqus python acoustic_postprocess.py acoustic_job.odb 190.0")
        sys.exit(1)
    
    odb_path = sys.argv[1]
    probe_separation = float(sys.argv[2]) if len(sys.argv) > 2 else 190.0
    
    # Initialize post-processor
    processor = AcousticPostProcessor(odb_path)
    
    try:
        # Process the ODB
        processor.open_odb()
        processor.extract_pressure_data()
        processor.calculate_transmission_loss(probe_separation)
        
        # Generate outputs
        processor.export_to_csv()
        processor.plot_results()
        processor.print_summary()
        
    except Exception as e:
        print(f"Error during processing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        processor.close_odb()


if __name__ == "__main__":
    main()


# Alternative function for use within Abaqus/CAE
def process_acoustic_odb(odb_path, probe_separation=190.0, 
                        probe_in='PROBE_IN', probe_out='PROBE_OUT'):
    """
    Convenience function for processing acoustic ODB within Abaqus/CAE
    
    Args:
        odb_path (str): Path to ODB file
        probe_separation (float): Distance between probes in meters
        probe_in (str): Input probe node set name
        probe_out (str): Output probe node set name
    
    Returns:
        dict: Dictionary containing frequencies, TL, and attenuation data
    """
    processor = AcousticPostProcessor(odb_path, probe_in, probe_out)
    
    try:
        processor.open_odb()
        processor.extract_pressure_data()
        processor.calculate_transmission_loss(probe_separation)
        processor.export_to_csv()
        processor.plot_results()
        processor.print_summary()
        
        return {
            'frequencies': processor.frequencies,
            'transmission_loss': processor.transmission_loss,
            'attenuation_coeff': processor.attenuation_coeff,
            'p_in': processor.p_in_magnitudes,
            'p_out': processor.p_out_magnitudes
        }
    
    finally:
        processor.close_odb()


# Example usage in Abaqus/CAE:
"""
# Run this in Abaqus/CAE command line or script:
execfile('acoustic_postprocess.py')
results = process_acoustic_odb('my_acoustic_job.odb', probe_separation=190.0)
print("Processing complete!")
"""