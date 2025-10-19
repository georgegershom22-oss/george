#!/usr/bin/env python
"""
Abaqus ODB Post-Processing Script for Transmission Loss Analysis

This script extracts acoustic pressure data from Abaqus ODB files and
computes:
- Transmission Loss TL(f) = 20*log10(|p_in|/|p_out|)
- Attenuation coefficient α(f) = TL(f) * ln(10) / (20 * Δx)

Usage:
    abaqus python extract_transmission_loss.py job_name.odb
    
Or from Abaqus/CAE:
    File > Run Script > extract_transmission_loss.py

Author: Generated for acoustic transmission loss analysis
Date: 2025-10-19
"""

import sys
import os
import numpy as np
from odbAccess import openOdb
from abaqusConstants import *

def extract_complex_pressure(frame, node_set_name, odb):
    """
    Extract complex acoustic pressure from a node set.
    
    Parameters:
    -----------
    frame : OdbFrame
        Frame containing field outputs
    node_set_name : str
        Name of the node set (e.g., 'PROBE_IN', 'PROBE_OUT')
    odb : Odb
        Open ODB object
        
    Returns:
    --------
    p_magnitude : float
        Spatially-averaged pressure magnitude
    p_real : float
        Average real part
    p_imag : float
        Average imaginary part
    """
    try:
        # Get the node set from assembly
        node_set = odb.rootAssembly.nodeSets[node_set_name.upper()]
        
        # Extract pressure field for this node set
        pressure_field = frame.fieldOutputs['POR']
        pressure_subset = pressure_field.getSubset(region=node_set)
        
        # Extract real and imaginary parts
        p_real_list = []
        p_imag_list = []
        
        for value in pressure_subset.values:
            # value.data is a tuple (real, imaginary) for complex pressure
            p_real_list.append(value.data[0])
            p_imag_list.append(value.data[1])
        
        # Compute spatial average
        p_real_avg = np.mean(p_real_list)
        p_imag_avg = np.mean(p_imag_list)
        
        # Magnitude
        p_magnitude = np.sqrt(p_real_avg**2 + p_imag_avg**2)
        
        return p_magnitude, p_real_avg, p_imag_avg
        
    except KeyError as e:
        print(f"ERROR: Node set '{node_set_name}' not found in ODB.")
        print(f"Available node sets: {odb.rootAssembly.nodeSets.keys()}")
        raise e


def compute_transmission_loss(odb_path, probe_in='PROBE_IN', probe_out='PROBE_OUT', 
                              delta_x=60.0, output_file=None):
    """
    Compute transmission loss and attenuation coefficient from ODB.
    
    Parameters:
    -----------
    odb_path : str
        Path to the ODB file
    probe_in : str
        Name of inlet probe node set
    probe_out : str
        Name of outlet probe node set
    delta_x : float
        Distance between probes in meters (default: 60m for x=20m to x=80m)
    output_file : str, optional
        Output CSV file name (default: derived from odb_path)
        
    Returns:
    --------
    results : dict
        Dictionary containing frequency arrays and TL/alpha values
    """
    
    print("="*80)
    print("ACOUSTIC TRANSMISSION LOSS POST-PROCESSING")
    print("="*80)
    print(f"ODB file: {odb_path}")
    print(f"Probe IN: {probe_in}")
    print(f"Probe OUT: {probe_out}")
    print(f"Probe spacing: {delta_x:.2f} m")
    print("="*80)
    
    # Open ODB
    if not os.path.exists(odb_path):
        raise IOError(f"ODB file not found: {odb_path}")
    
    odb = openOdb(path=odb_path, readOnly=True)
    
    # Get the steady-state dynamics step
    step_name = None
    for name in odb.steps.keys():
        if 'ACOUSTIC' in name.upper() or 'SSD' in name.upper() or 'SWEEP' in name.upper():
            step_name = name
            break
    
    if step_name is None:
        # Use first step
        step_name = odb.steps.keys()[0]
        print(f"WARNING: Using first step: {step_name}")
    else:
        print(f"Processing step: {step_name}")
    
    step = odb.steps[step_name]
    
    # Initialize arrays
    frequencies = []
    p_in_mag = []
    p_out_mag = []
    p_in_real = []
    p_in_imag = []
    p_out_real = []
    p_out_imag = []
    
    # Loop through all frames (frequencies)
    print(f"\nProcessing {len(step.frames)} frequency points...")
    
    for i, frame in enumerate(step.frames):
        # Get frequency (check different possible attributes)
        if hasattr(frame, 'frequency'):
            freq = frame.frequency
        elif hasattr(frame, 'frameValue'):
            freq = frame.frameValue
        else:
            freq = i  # fallback to frame index
        
        frequencies.append(freq)
        
        # Extract pressures at probes
        try:
            p_in, pr_in, pi_in = extract_complex_pressure(frame, probe_in, odb)
            p_out, pr_out, pi_out = extract_complex_pressure(frame, probe_out, odb)
            
            p_in_mag.append(p_in)
            p_out_mag.append(p_out)
            p_in_real.append(pr_in)
            p_in_imag.append(pi_in)
            p_out_real.append(pr_out)
            p_out_imag.append(pi_out)
            
            if i % 20 == 0:
                print(f"  Frame {i:3d}: f={freq:7.1f} Hz, |P_in|={p_in:.2e} Pa, |P_out|={p_out:.2e} Pa")
        
        except Exception as e:
            print(f"ERROR at frame {i} (f={freq} Hz): {e}")
            # Append NaN to maintain array alignment
            p_in_mag.append(np.nan)
            p_out_mag.append(np.nan)
            p_in_real.append(np.nan)
            p_in_imag.append(np.nan)
            p_out_real.append(np.nan)
            p_out_imag.append(np.nan)
    
    # Close ODB
    odb.close()
    
    # Convert to numpy arrays
    frequencies = np.array(frequencies)
    p_in_mag = np.array(p_in_mag)
    p_out_mag = np.array(p_out_mag)
    
    # Compute transmission loss (dB)
    # TL = 20 * log10(|p_in| / |p_out|)
    with np.errstate(divide='ignore', invalid='ignore'):
        TL = 20.0 * np.log10(p_in_mag / p_out_mag)
    
    # Compute attenuation coefficient (amplitude basis)
    # α_amp = TL * ln(10) / (20 * Δx)  [units: Np/m or dB/m depending on convention]
    alpha_amp_Npm = TL * np.log(10) / (20.0 * delta_x)  # Nepers per meter
    alpha_amp_dBm = TL / delta_x  # dB per meter
    
    # Compute attenuation coefficient (intensity basis)
    # α_int = TL * ln(10) / (10 * Δx)
    alpha_int_Npm = TL * np.log(10) / (10.0 * delta_x)  # Nepers per meter
    
    # Statistics
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    print(f"Frequency range: {frequencies[0]:.1f} - {frequencies[-1]:.1f} Hz")
    print(f"Number of points: {len(frequencies)}")
    print(f"\nTransmission Loss (TL):")
    print(f"  Mean: {np.nanmean(TL):.2f} dB")
    print(f"  Min:  {np.nanmin(TL):.2f} dB at {frequencies[np.nanargmin(TL)]:.1f} Hz")
    print(f"  Max:  {np.nanmax(TL):.2f} dB at {frequencies[np.nanargmax(TL)]:.1f} Hz")
    print(f"\nAttenuation Coefficient (amplitude basis):")
    print(f"  Mean: {np.nanmean(alpha_amp_dBm):.4f} dB/m = {np.nanmean(alpha_amp_Npm):.6f} Np/m")
    print(f"  Min:  {np.nanmin(alpha_amp_dBm):.4f} dB/m")
    print(f"  Max:  {np.nanmax(alpha_amp_dBm):.4f} dB/m")
    print("="*80)
    
    # Prepare output
    results = {
        'frequency': frequencies,
        'TL_dB': TL,
        'alpha_dB_per_m': alpha_amp_dBm,
        'alpha_Np_per_m': alpha_amp_Npm,
        'alpha_int_Np_per_m': alpha_int_Npm,
        'p_in_magnitude': p_in_mag,
        'p_out_magnitude': p_out_mag,
        'p_in_real': np.array(p_in_real),
        'p_in_imag': np.array(p_in_imag),
        'p_out_real': np.array(p_out_real),
        'p_out_imag': np.array(p_out_imag),
    }
    
    # Save to CSV
    if output_file is None:
        output_file = odb_path.replace('.odb', '_transmission_loss.csv')
    
    print(f"\nSaving results to: {output_file}")
    
    header = "Frequency_Hz,TL_dB,alpha_dB_per_m,alpha_Np_per_m,alpha_int_Np_per_m," \
             "p_in_mag_Pa,p_out_mag_Pa,p_in_real_Pa,p_in_imag_Pa,p_out_real_Pa,p_out_imag_Pa"
    
    data = np.column_stack([
        frequencies, TL, alpha_amp_dBm, alpha_amp_Npm, alpha_int_Npm,
        p_in_mag, p_out_mag,
        np.array(p_in_real), np.array(p_in_imag),
        np.array(p_out_real), np.array(p_out_imag)
    ])
    
    np.savetxt(output_file, data, delimiter=',', header=header, comments='')
    
    print(f"SUCCESS: Results saved to {output_file}")
    print("="*80)
    
    return results


def main():
    """Main entry point for command-line usage."""
    
    if len(sys.argv) < 2:
        print("Usage: abaqus python extract_transmission_loss.py <odb_file> [probe_in] [probe_out] [delta_x]")
        print("\nExample:")
        print("  abaqus python extract_transmission_loss.py acoustic_transmission_loss.odb")
        print("  abaqus python extract_transmission_loss.py job.odb PROBE_IN PROBE_OUT 60.0")
        sys.exit(1)
    
    odb_path = sys.argv[1]
    
    # Optional arguments
    probe_in = sys.argv[2] if len(sys.argv) > 2 else 'PROBE_IN'
    probe_out = sys.argv[3] if len(sys.argv) > 3 else 'PROBE_OUT'
    delta_x = float(sys.argv[4]) if len(sys.argv) > 4 else 60.0
    
    # Run analysis
    try:
        results = compute_transmission_loss(odb_path, probe_in, probe_out, delta_x)
        print("\nPost-processing completed successfully!")
        
    except Exception as e:
        print(f"\nERROR: Post-processing failed!")
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
