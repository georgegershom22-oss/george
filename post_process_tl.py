#!/usr/bin/env python3
"""
Abaqus Acoustic Transmission Loss Post-Processing Script

This script processes Abaqus ODB results to calculate:
1. Transmission Loss (TL) as a function of frequency
2. Attenuation coefficient (alpha) from TL measurements

Usage:
    python post_process_tl.py job_name.odb

Requirements:
    - Abaqus Python environment with odbAccess
    - numpy for numerical calculations
    - matplotlib for plotting (optional)

Author: Abaqus Acoustic Simulation
Date: 2024
"""

import sys
import numpy as np
from odbAccess import openOdb
import os

def calculate_complex_magnitude(complex_data):
    """
    Calculate magnitude of complex pressure data
    
    Args:
        complex_data: List of complex pressure values from Abaqus
        
    Returns:
        float: Average magnitude of complex pressure
    """
    magnitudes = []
    for value in complex_data:
        # Abaqus stores complex data as [real, imaginary]
        real_part = value.data[0]
        imag_part = value.data[1]
        magnitude = np.sqrt(real_part**2 + imag_part**2)
        magnitudes.append(magnitude)
    
    return np.mean(magnitudes)

def process_acoustic_results(odb_path, probe_in_name='PROBE_IN', probe_out_name='PROBE_OUT'):
    """
    Process Abaqus acoustic simulation results to calculate TL and alpha
    
    Args:
        odb_path: Path to Abaqus ODB file
        probe_in_name: Name of input probe node set
        probe_out_name: Name of output probe node set
        
    Returns:
        dict: Results containing frequencies, TL, and alpha
    """
    
    # Open the ODB file
    try:
        odb = openOdb(odb_path)
        print(f"Successfully opened ODB: {odb_path}")
    except Exception as e:
        print(f"Error opening ODB file: {e}")
        return None
    
    # Get the steady-state dynamics step
    try:
        step = odb.steps['SSD']
        print(f"Found step: {step.name}")
    except KeyError:
        print("Error: Could not find 'SSD' step in ODB")
        return None
    
    # Get node sets
    try:
        probe_in_set = odb.rootAssembly.nodeSets[probe_in_name]
        probe_out_set = odb.rootAssembly.nodeSets[probe_out_name]
        print(f"Found probe sets: {probe_in_name}, {probe_out_name}")
    except KeyError as e:
        print(f"Error: Could not find node set {e}")
        return None
    
    # Initialize arrays
    frequencies = []
    pressure_in = []
    pressure_out = []
    
    print("Processing frequency frames...")
    
    # Process each frequency frame
    for i, frame in enumerate(step.frames):
        freq = frame.frequency
        frequencies.append(freq)
        
        print(f"Processing frequency {freq:.1f} Hz (frame {i+1}/{len(step.frames)})")
        
        # Get pressure field output
        try:
            pressure_field = frame.fieldOutputs['P']
        except KeyError:
            print(f"Warning: No pressure field found at frequency {freq} Hz")
            continue
        
        # Get pressure values at probe locations
        try:
            p_in_values = pressure_field.getSubset(region=probe_in_set).values
            p_out_values = pressure_field.getSubset(region=probe_out_set).values
            
            # Calculate average pressure magnitudes
            p_in_avg = calculate_complex_magnitude(p_in_values)
            p_out_avg = calculate_complex_magnitude(p_out_values)
            
            pressure_in.append(p_in_avg)
            pressure_out.append(p_out_avg)
            
        except Exception as e:
            print(f"Error processing pressure data at {freq} Hz: {e}")
            continue
    
    # Convert to numpy arrays
    frequencies = np.array(frequencies)
    pressure_in = np.array(pressure_in)
    pressure_out = np.array(pressure_out)
    
    # Calculate Transmission Loss
    # TL = 20 * log10(|P_in| / |P_out|)
    tl = 20.0 * np.log10(pressure_in / pressure_out)
    
    # Calculate attenuation coefficient
    # Distance between probe planes (meters)
    delta_x = 6.0  # Distance from PROBE_IN (x=2.0) to PROBE_OUT (x=8.0)
    
    # alpha_amp = (ln(10)/20) * TL / delta_x
    alpha_amp = (np.log(10) / 20.0) * tl / delta_x
    
    # Close ODB
    odb.close()
    
    # Prepare results
    results = {
        'frequencies': frequencies,
        'pressure_in': pressure_in,
        'pressure_out': pressure_out,
        'transmission_loss': tl,
        'attenuation_coefficient': alpha_amp,
        'delta_x': delta_x
    }
    
    return results

def save_results_to_csv(results, output_file='acoustic_results.csv'):
    """
    Save results to CSV file
    
    Args:
        results: Dictionary containing simulation results
        output_file: Output CSV filename
    """
    import csv
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['Frequency (Hz)', 'Pressure In (Pa)', 'Pressure Out (Pa)', 
                        'Transmission Loss (dB)', 'Attenuation Coefficient (1/m)'])
        
        # Write data
        for i in range(len(results['frequencies'])):
            writer.writerow([
                results['frequencies'][i],
                results['pressure_in'][i],
                results['pressure_out'][i],
                results['transmission_loss'][i],
                results['attenuation_coefficient'][i]
            ])
    
    print(f"Results saved to {output_file}")

def plot_results(results, save_plot=True):
    """
    Plot transmission loss and attenuation coefficient
    
    Args:
        results: Dictionary containing simulation results
        save_plot: Whether to save plot to file
    """
    try:
        import matplotlib.pyplot as plt
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Plot Transmission Loss
        ax1.plot(results['frequencies'], results['transmission_loss'], 'b-', linewidth=2)
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Transmission Loss (dB)')
        ax1.set_title('Acoustic Transmission Loss vs Frequency')
        ax1.grid(True, alpha=0.3)
        
        # Plot Attenuation Coefficient
        ax2.plot(results['frequencies'], results['attenuation_coefficient'], 'r-', linewidth=2)
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Attenuation Coefficient (1/m)')
        ax2.set_title('Attenuation Coefficient vs Frequency')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_plot:
            plt.savefig('acoustic_results.png', dpi=300, bbox_inches='tight')
            print("Plot saved as acoustic_results.png")
        
        plt.show()
        
    except ImportError:
        print("matplotlib not available. Install with: pip install matplotlib")
    except Exception as e:
        print(f"Error creating plot: {e}")

def print_summary(results):
    """
    Print summary of results
    
    Args:
        results: Dictionary containing simulation results
    """
    print("\n" + "="*60)
    print("ACOUSTIC TRANSMISSION LOSS ANALYSIS SUMMARY")
    print("="*60)
    
    print(f"Frequency range: {results['frequencies'][0]:.1f} - {results['frequencies'][-1]:.1f} Hz")
    print(f"Number of frequencies: {len(results['frequencies'])}")
    print(f"Probe separation distance: {results['delta_x']:.1f} m")
    
    print(f"\nTransmission Loss Statistics:")
    print(f"  Minimum TL: {np.min(results['transmission_loss']):.2f} dB")
    print(f"  Maximum TL: {np.max(results['transmission_loss']):.2f} dB")
    print(f"  Average TL: {np.mean(results['transmission_loss']):.2f} dB")
    
    print(f"\nAttenuation Coefficient Statistics:")
    print(f"  Minimum α: {np.min(results['attenuation_coefficient']):.4f} 1/m")
    print(f"  Maximum α: {np.max(results['attenuation_coefficient']):.4f} 1/m")
    print(f"  Average α: {np.mean(results['attenuation_coefficient']):.4f} 1/m")
    
    print("\nTop 5 frequencies with highest TL:")
    sorted_indices = np.argsort(results['transmission_loss'])[::-1]
    for i in range(min(5, len(sorted_indices))):
        idx = sorted_indices[i]
        print(f"  {results['frequencies'][idx]:.1f} Hz: {results['transmission_loss'][idx]:.2f} dB")

def main():
    """
    Main function to process Abaqus acoustic results
    """
    if len(sys.argv) != 2:
        print("Usage: python post_process_tl.py <odb_file>")
        print("Example: python post_process_tl.py acoustic_transmission_loss.odb")
        sys.exit(1)
    
    odb_file = sys.argv[1]
    
    if not os.path.exists(odb_file):
        print(f"Error: ODB file '{odb_file}' not found")
        sys.exit(1)
    
    print("Starting Abaqus Acoustic Post-Processing...")
    print(f"Processing ODB file: {odb_file}")
    
    # Process the results
    results = process_acoustic_results(odb_file)
    
    if results is None:
        print("Error: Failed to process results")
        sys.exit(1)
    
    # Print summary
    print_summary(results)
    
    # Save results to CSV
    save_results_to_csv(results)
    
    # Create plots
    plot_results(results)
    
    print("\nPost-processing completed successfully!")

if __name__ == "__main__":
    main()