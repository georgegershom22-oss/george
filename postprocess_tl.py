#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Post-Processing Script for Acoustic Transmission Loss
======================================================

Extracts complex pressure fields from Abaqus ODB and computes:
- TL(f): Transmission Loss vs frequency
- alpha(f): Attenuation coefficient vs frequency

Usage:
    abaqus python postprocess_tl.py [job_name]

Author: Abaqus Acoustic Simulation
Date: 2025-10-19
"""

from odbAccess import *
from abaqusConstants import *
import numpy as np
import sys
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

class PostProcessConfig:
    """Configuration for post-processing"""
    
    def __init__(self):
        # Job name (ODB file)
        self.job_name = 'acoustic_tl_job'
        
        # Probe set names
        self.probe_in_name = 'PROBE_IN'
        self.probe_out_name = 'PROBE_OUT'
        
        # Step name
        self.step_name = 'SSD_FREQUENCYSWEEP'
        
        # Probe separation (for alpha calculation)
        # Will be auto-detected from ODB if possible
        self.probe_separation = None  # meters
        
        # Output files
        self.output_csv = 'transmission_loss.csv'
        self.output_plot_script = 'plot_tl.py'
        
        # Reference impedance (optional, for intensity calculations)
        self.reference_density = 1025.0  # kg/m³
        self.reference_speed = 1500.0    # m/s


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def find_probe_separation(odb, config):
    """Auto-detect probe separation from node coordinates"""
    try:
        assembly = odb.rootAssembly
        
        # Get probe sets
        probe_in = assembly.nodeSets[config.probe_in_name]
        probe_out = assembly.nodeSets[config.probe_out_name]
        
        # Get first node from each set
        node_in = probe_in.nodes[0][0]  # [instance][node_index]
        node_out = probe_out.nodes[0][0]
        
        # Calculate x-coordinate difference
        x_in = node_in.coordinates[0]
        x_out = node_out.coordinates[0]
        
        separation = abs(x_out - x_in)
        
        print("Auto-detected probe separation: {:.3f} m".format(separation))
        return separation
        
    except Exception as e:
        print("Warning: Could not auto-detect probe separation: {}".format(e))
        print("Please set config.probe_separation manually")
        return None


def extract_complex_pressure(field_output, region_name):
    """
    Extract complex pressure from a field output region
    
    Returns:
        complex_pressures: list of complex numbers (one per node)
    """
    try:
        subset = field_output.getSubset(region=region_name)
        values = subset.values
        
        # POR (acoustic pressure) is stored as (real, imaginary) pair
        complex_pressures = []
        for val in values:
            real_part = val.data[0]
            imag_part = val.data[1]
            complex_pressures.append(complex(real_part, imag_part))
        
        return complex_pressures
        
    except KeyError:
        print("Warning: Could not find region '{}'".format(region_name))
        return []


def compute_spatial_average_magnitude(complex_pressures):
    """
    Compute spatial average of pressure magnitude
    
    Args:
        complex_pressures: list of complex pressure values
    
    Returns:
        average magnitude (scalar)
    """
    if len(complex_pressures) == 0:
        return 0.0
    
    magnitudes = [abs(p) for p in complex_pressures]
    return np.mean(magnitudes)


def compute_transmission_loss(p_in_mag, p_out_mag):
    """
    Compute transmission loss in dB
    
    TL(f) = 20 * log10(|p_in| / |p_out|)
    
    Args:
        p_in_mag: inlet pressure magnitude
        p_out_mag: outlet pressure magnitude
    
    Returns:
        TL in dB
    """
    if p_out_mag == 0.0:
        return float('inf')
    
    return 20.0 * np.log10(p_in_mag / p_out_mag)


def compute_attenuation_coefficient(TL, distance, method='amplitude'):
    """
    Compute attenuation coefficient from TL
    
    Args:
        TL: Transmission loss in dB
        distance: probe separation in meters
        method: 'amplitude' or 'intensity'
    
    Returns:
        alpha in Np/m (Nepers per meter) or dB/m
    """
    if method == 'amplitude':
        # alpha_amp = (ln(10)/20) * TL / distance  [Np/m]
        alpha_Np = (np.log(10) / 20.0) * TL / distance
        alpha_dB = TL / distance  # [dB/m]
        return alpha_Np, alpha_dB
    
    elif method == 'intensity':
        # alpha_int = (ln(10)/10) * TL / distance  [Np/m]
        alpha_Np = (np.log(10) / 10.0) * TL / distance
        alpha_dB = TL / distance  # [dB/m]
        return alpha_Np, alpha_dB
    
    else:
        raise ValueError("Method must be 'amplitude' or 'intensity'")


# ============================================================================
# MAIN POST-PROCESSING
# ============================================================================

def postprocess_tl(config):
    """
    Main post-processing function
    
    Extracts pressure data from ODB and computes TL(f) and alpha(f)
    """
    
    print("="*70)
    print("Post-Processing Acoustic Transmission Loss")
    print("="*70)
    
    # Open ODB
    odb_file = config.job_name + '.odb'
    
    if not os.path.exists(odb_file):
        print("ERROR: ODB file not found: {}".format(odb_file))
        print("Please run the simulation first.")
        return
    
    print("\nOpening ODB: {}".format(odb_file))
    odb = openOdb(path=odb_file, readOnly=True)
    
    # Get step
    try:
        step = odb.steps[config.step_name]
    except KeyError:
        print("ERROR: Step '{}' not found in ODB".format(config.step_name))
        print("Available steps:", odb.steps.keys())
        odb.close()
        return
    
    print("Processing step: {}".format(config.step_name))
    
    # Auto-detect probe separation if not specified
    if config.probe_separation is None:
        config.probe_separation = find_probe_separation(odb, config)
        
        if config.probe_separation is None:
            print("ERROR: Probe separation not specified and could not be auto-detected")
            odb.close()
            return
    
    # Initialize result arrays
    frequencies = []
    p_in_magnitudes = []
    p_out_magnitudes = []
    transmission_losses = []
    alpha_amplitude_Np = []
    alpha_amplitude_dB = []
    
    # Process each frame (frequency point)
    print("\nExtracting pressure data from {} frames...".format(len(step.frames)))
    
    assembly = odb.rootAssembly
    
    for i, frame in enumerate(step.frames):
        # Get frequency
        freq = frame.frequency
        frequencies.append(freq)
        
        # Get pressure field output
        try:
            pressure_field = frame.fieldOutputs['POR']
        except KeyError:
            print("Warning: POR not found in frame {}".format(i))
            continue
        
        # Extract pressures at probe locations
        try:
            probe_in_region = assembly.nodeSets[config.probe_in_name]
            probe_out_region = assembly.nodeSets[config.probe_out_name]
        except KeyError as e:
            print("ERROR: Probe set not found: {}".format(e))
            print("Available node sets:", assembly.nodeSets.keys())
            odb.close()
            return
        
        # Get subset for each probe
        p_in_subset = pressure_field.getSubset(region=probe_in_region)
        p_out_subset = pressure_field.getSubset(region=probe_out_region)
        
        # Extract complex values
        p_in_values = []
        for val in p_in_subset.values:
            real_part = val.data[0]
            imag_part = val.data[1]
            p_in_values.append(complex(real_part, imag_part))
        
        p_out_values = []
        for val in p_out_subset.values:
            real_part = val.data[0]
            imag_part = val.data[1]
            p_out_values.append(complex(real_part, imag_part))
        
        # Compute spatial average magnitudes
        p_in_mag = compute_spatial_average_magnitude(p_in_values)
        p_out_mag = compute_spatial_average_magnitude(p_out_values)
        
        p_in_magnitudes.append(p_in_mag)
        p_out_magnitudes.append(p_out_mag)
        
        # Compute TL
        TL = compute_transmission_loss(p_in_mag, p_out_mag)
        transmission_losses.append(TL)
        
        # Compute attenuation coefficients
        alpha_Np, alpha_dB = compute_attenuation_coefficient(
            TL, config.probe_separation, method='amplitude'
        )
        alpha_amplitude_Np.append(alpha_Np)
        alpha_amplitude_dB.append(alpha_dB)
        
        if (i+1) % 20 == 0 or i == 0:
            print("  Frame {}/{}: f={:.1f} Hz, |p_in|={:.3e} Pa, |p_out|={:.3e} Pa, TL={:.2f} dB, alpha={:.4f} Np/m".format(
                i+1, len(step.frames), freq, p_in_mag, p_out_mag, TL, alpha_Np))
    
    # Close ODB
    odb.close()
    
    # Convert to numpy arrays
    frequencies = np.array(frequencies)
    p_in_magnitudes = np.array(p_in_magnitudes)
    p_out_magnitudes = np.array(p_out_magnitudes)
    transmission_losses = np.array(transmission_losses)
    alpha_amplitude_Np = np.array(alpha_amplitude_Np)
    alpha_amplitude_dB = np.array(alpha_amplitude_dB)
    
    # Save results to CSV
    print("\nSaving results to: {}".format(config.output_csv))
    
    with open(config.output_csv, 'w') as f:
        f.write("# Acoustic Transmission Loss Results\n")
        f.write("# Job: {}\n".format(config.job_name))
        f.write("# Probe separation: {:.3f} m\n".format(config.probe_separation))
        f.write("# Columns: Frequency(Hz), |P_in|(Pa), |P_out|(Pa), TL(dB), Alpha(Np/m), Alpha(dB/m)\n")
        f.write("Frequency_Hz,P_in_Pa,P_out_Pa,TL_dB,Alpha_Np_per_m,Alpha_dB_per_m\n")
        
        for i in range(len(frequencies)):
            f.write("{:.2f},{:.6e},{:.6e},{:.6f},{:.8f},{:.6f}\n".format(
                frequencies[i],
                p_in_magnitudes[i],
                p_out_magnitudes[i],
                transmission_losses[i],
                alpha_amplitude_Np[i],
                alpha_amplitude_dB[i]
            ))
    
    # Print summary statistics
    print("\n" + "="*70)
    print("Results Summary")
    print("="*70)
    print("Frequency range: {:.1f} - {:.1f} Hz".format(frequencies[0], frequencies[-1]))
    print("Number of points: {}".format(len(frequencies)))
    print("Probe separation: {:.3f} m".format(config.probe_separation))
    print("\nTransmission Loss (TL):")
    print("  Mean: {:.2f} dB".format(np.mean(transmission_losses)))
    print("  Min:  {:.2f} dB at {:.1f} Hz".format(np.min(transmission_losses), 
                                                    frequencies[np.argmin(transmission_losses)]))
    print("  Max:  {:.2f} dB at {:.1f} Hz".format(np.max(transmission_losses),
                                                    frequencies[np.argmax(transmission_losses)]))
    print("\nAttenuation Coefficient (alpha):")
    print("  Mean: {:.4f} Np/m = {:.3f} dB/m".format(
        np.mean(alpha_amplitude_Np), np.mean(alpha_amplitude_dB)))
    print("  Min:  {:.4f} Np/m = {:.3f} dB/m at {:.1f} Hz".format(
        np.min(alpha_amplitude_Np), np.min(alpha_amplitude_dB),
        frequencies[np.argmin(alpha_amplitude_Np)]))
    print("  Max:  {:.4f} Np/m = {:.3f} dB/m at {:.1f} Hz".format(
        np.max(alpha_amplitude_Np), np.max(alpha_amplitude_dB),
        frequencies[np.argmax(alpha_amplitude_Np)]))
    print("="*70)
    
    # Generate plotting script
    create_plotting_script(config)
    
    print("\nPost-processing complete!")
    print("\nOutput files:")
    print("  - {}".format(config.output_csv))
    print("  - {}".format(config.output_plot_script))
    print("\nTo visualize results, run:")
    print("  python {}".format(config.output_plot_script))


def create_plotting_script(config):
    """Create a standalone Python script for plotting results"""
    
    script_content = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"
Plot Transmission Loss and Attenuation Coefficient
\"\"\"

import numpy as np
import matplotlib.pyplot as plt

# Read data
data = np.loadtxt('{csv}', delimiter=',', skiprows=5)

freq = data[:, 0]
p_in = data[:, 1]
p_out = data[:, 2]
TL = data[:, 3]
alpha_Np = data[:, 4]
alpha_dB = data[:, 5]

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Pressure magnitudes
ax = axes[0, 0]
ax.semilogy(freq, p_in, 'b-', label='Inlet', linewidth=2)
ax.semilogy(freq, p_out, 'r-', label='Outlet', linewidth=2)
ax.set_xlabel('Frequency (Hz)', fontsize=12)
ax.set_ylabel('Pressure Magnitude (Pa)', fontsize=12)
ax.set_title('Pressure Magnitude vs Frequency', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=11)

# Plot 2: Transmission Loss
ax = axes[0, 1]
ax.plot(freq, TL, 'g-', linewidth=2)
ax.set_xlabel('Frequency (Hz)', fontsize=12)
ax.set_ylabel('Transmission Loss (dB)', fontsize=12)
ax.set_title('Transmission Loss vs Frequency', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)

# Plot 3: Attenuation coefficient (Np/m)
ax = axes[1, 0]
ax.plot(freq, alpha_Np, 'm-', linewidth=2)
ax.set_xlabel('Frequency (Hz)', fontsize=12)
ax.set_ylabel('Attenuation Coefficient (Np/m)', fontsize=12)
ax.set_title('Attenuation Coefficient vs Frequency', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)

# Plot 4: Attenuation coefficient (dB/m)
ax = axes[1, 1]
ax.plot(freq, alpha_dB, 'c-', linewidth=2)
ax.set_xlabel('Frequency (Hz)', fontsize=12)
ax.set_ylabel('Attenuation Coefficient (dB/m)', fontsize=12)
ax.set_title('Attenuation Coefficient vs Frequency (dB/m)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('transmission_loss_results.png', dpi=300, bbox_inches='tight')
print("Plot saved: transmission_loss_results.png")
plt.show()
""".format(csv=config.output_csv)
    
    with open(config.output_plot_script, 'w') as f:
        f.write(script_content)
    
    print("Created plotting script: {}".format(config.output_plot_script))


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    
    # Parse command line arguments
    config = PostProcessConfig()
    
    if len(sys.argv) > 1:
        config.job_name = sys.argv[1]
    
    # Run post-processing
    postprocess_tl(config)


if __name__ == '__main__':
    # Handle both direct execution and abaqus python execution
    try:
        main()
    except Exception as e:
        print("ERROR: {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
