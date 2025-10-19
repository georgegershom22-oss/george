#!/usr/bin/env python
"""
Visualization Script for Acoustic Transmission Loss Results

Reads CSV output from extract_transmission_loss.py and generates publication-quality plots.

Usage:
    python plot_transmission_loss.py acoustic_transmission_loss_transmission_loss.csv
    
Requirements:
    - matplotlib
    - numpy
    - pandas (optional, for nicer CSV reading)
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Set plot style
plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'seaborn-darkgrid')
plt.rcParams['figure.dpi'] = 150
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['legend.fontsize'] = 9


def load_transmission_loss_data(csv_file):
    """Load transmission loss data from CSV file."""
    
    if not os.path.exists(csv_file):
        raise IOError(f"CSV file not found: {csv_file}")
    
    # Load data
    data = np.genfromtxt(csv_file, delimiter=',', names=True, comments='#')
    
    return data


def plot_transmission_loss_analysis(data, output_prefix=None):
    """
    Create comprehensive plots of transmission loss analysis.
    
    Parameters:
    -----------
    data : structured numpy array
        Data loaded from CSV with fields: Frequency_Hz, TL_dB, alpha_dB_per_m, etc.
    output_prefix : str, optional
        Prefix for output image files
    """
    
    frequency = data['Frequency_Hz']
    TL = data['TL_dB']
    alpha_dB = data['alpha_dB_per_m']
    alpha_Np = data['alpha_Np_per_m']
    p_in = data['p_in_mag_Pa']
    p_out = data['p_out_mag_Pa']
    
    # ========================================================================
    # Figure 1: Comprehensive 4-panel plot
    # ========================================================================
    fig = plt.figure(figsize=(14, 10))
    gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    # Panel 1: Transmission Loss vs Frequency
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(frequency, TL, 'b-', linewidth=1.5, label='Transmission Loss')
    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('Transmission Loss (dB)')
    ax1.set_title('Acoustic Transmission Loss: Three-Layer Stratified Medium', fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='best')
    
    # Add frequency bands
    ax1.axvspan(100, 500, alpha=0.1, color='green', label='Low freq')
    ax1.axvspan(500, 2000, alpha=0.1, color='yellow')
    ax1.axvspan(2000, 5000, alpha=0.1, color='red')
    
    # Panel 2: Attenuation Coefficient (dB/m)
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(frequency, alpha_dB * 1000, 'r-', linewidth=1.5)  # Convert to dB/km
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Attenuation Coefficient (dB/km)')
    ax2.set_title('Attenuation Coefficient (dB basis)')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([frequency[0], frequency[-1]])
    
    # Panel 3: Attenuation Coefficient (Np/m)
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.plot(frequency, alpha_Np * 1000, 'g-', linewidth=1.5)  # Convert to Np/km
    ax3.set_xlabel('Frequency (Hz)')
    ax3.set_ylabel('Attenuation Coefficient (Np/km)')
    ax3.set_title('Attenuation Coefficient (Neper basis)')
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim([frequency[0], frequency[-1]])
    
    # Panel 4: Pressure Magnitudes
    ax4 = fig.add_subplot(gs[2, 0])
    ax4.semilogy(frequency, p_in, 'b-', linewidth=1.5, label='Inlet (x=20m)', alpha=0.8)
    ax4.semilogy(frequency, p_out, 'r-', linewidth=1.5, label='Outlet (x=80m)', alpha=0.8)
    ax4.set_xlabel('Frequency (Hz)')
    ax4.set_ylabel('Pressure Magnitude (Pa)')
    ax4.set_title('Probe Pressure Magnitudes')
    ax4.grid(True, alpha=0.3, which='both')
    ax4.legend(loc='best')
    ax4.set_xlim([frequency[0], frequency[-1]])
    
    # Panel 5: Transmission Ratio (linear scale)
    ax5 = fig.add_subplot(gs[2, 1])
    transmission_ratio = p_out / p_in
    ax5.plot(frequency, transmission_ratio, 'm-', linewidth=1.5)
    ax5.set_xlabel('Frequency (Hz)')
    ax5.set_ylabel('Transmission Ratio (|p_out|/|p_in|)')
    ax5.set_title('Acoustic Transmission Ratio')
    ax5.grid(True, alpha=0.3)
    ax5.set_xlim([frequency[0], frequency[-1]])
    ax5.set_ylim([0, np.nanmax(transmission_ratio) * 1.1])
    
    # Add text box with simulation parameters
    textstr = '\n'.join([
        'Simulation Parameters:',
        f'Frequency range: {frequency[0]:.0f}-{frequency[-1]:.0f} Hz',
        f'Probe spacing: 60 m',
        f'Mean TL: {np.nanmean(TL):.2f} dB',
        f'Mean α: {np.nanmean(alpha_dB)*1000:.3f} dB/km',
    ])
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax1.text(0.02, 0.98, textstr, transform=ax1.transAxes, fontsize=9,
             verticalalignment='top', bbox=props, family='monospace')
    
    plt.tight_layout()
    
    if output_prefix:
        filename = f"{output_prefix}_comprehensive.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Saved: {filename}")
    
    # ========================================================================
    # Figure 2: Detailed TL plot with spectral features
    # ========================================================================
    fig2, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(frequency, TL, 'b-', linewidth=2, label='TL(f)')
    
    # Mark peaks and troughs
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(TL, prominence=0.5)
    troughs, _ = find_peaks(-TL, prominence=0.5)
    
    if len(peaks) > 0:
        ax.plot(frequency[peaks], TL[peaks], 'r^', markersize=8, label='Peaks (constructive)')
    if len(troughs) > 0:
        ax.plot(frequency[troughs], TL[troughs], 'gv', markersize=8, label='Troughs (destructive)')
    
    ax.set_xlabel('Frequency (Hz)', fontsize=12)
    ax.set_ylabel('Transmission Loss (dB)', fontsize=12)
    ax.set_title('Transmission Loss with Interference Features\nThree-Layer Ocean Thermocline Model', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=10)
    ax.set_xlim([frequency[0], frequency[-1]])
    
    # Add horizontal lines for reference
    ax.axhline(y=0, color='k', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.axhline(y=np.nanmean(TL), color='orange', linestyle='--', linewidth=1, 
               alpha=0.7, label=f'Mean TL = {np.nanmean(TL):.2f} dB')
    
    plt.tight_layout()
    
    if output_prefix:
        filename = f"{output_prefix}_detailed.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Saved: {filename}")
    
    # ========================================================================
    # Figure 3: Phase information (if available in data)
    # ========================================================================
    if 'p_in_real_Pa' in data.dtype.names and 'p_in_imag_Pa' in data.dtype.names:
        fig3, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Phase at inlet
        phase_in = np.arctan2(data['p_in_imag_Pa'], data['p_in_real_Pa']) * 180 / np.pi
        ax1.plot(frequency, phase_in, 'b-', linewidth=1.5)
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Phase (degrees)')
        ax1.set_title('Pressure Phase at Inlet Probe (x=20m)')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([frequency[0], frequency[-1]])
        
        # Phase at outlet
        phase_out = np.arctan2(data['p_out_imag_Pa'], data['p_out_real_Pa']) * 180 / np.pi
        ax2.plot(frequency, phase_out, 'r-', linewidth=1.5)
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Phase (degrees)')
        ax2.set_title('Pressure Phase at Outlet Probe (x=80m)')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([frequency[0], frequency[-1]])
        
        plt.tight_layout()
        
        if output_prefix:
            filename = f"{output_prefix}_phase.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Saved: {filename}")
    
    plt.show()


def print_summary_statistics(data):
    """Print statistical summary of the transmission loss data."""
    
    print("\n" + "="*80)
    print("TRANSMISSION LOSS ANALYSIS - SUMMARY STATISTICS")
    print("="*80)
    
    frequency = data['Frequency_Hz']
    TL = data['TL_dB']
    alpha_dB = data['alpha_dB_per_m']
    
    print(f"\nFrequency Range:")
    print(f"  Min: {frequency[0]:.2f} Hz")
    print(f"  Max: {frequency[-1]:.2f} Hz")
    print(f"  Points: {len(frequency)}")
    
    print(f"\nTransmission Loss (TL):")
    print(f"  Mean:   {np.nanmean(TL):8.3f} dB")
    print(f"  Std:    {np.nanstd(TL):8.3f} dB")
    print(f"  Min:    {np.nanmin(TL):8.3f} dB  @ {frequency[np.nanargmin(TL)]:7.1f} Hz")
    print(f"  Max:    {np.nanmax(TL):8.3f} dB  @ {frequency[np.nanargmax(TL)]:7.1f} Hz")
    print(f"  Median: {np.nanmedian(TL):8.3f} dB")
    
    print(f"\nAttenuation Coefficient:")
    print(f"  Mean:   {np.nanmean(alpha_dB*1000):8.4f} dB/km  = {np.nanmean(data['alpha_Np_per_m']*1000):8.6f} Np/km")
    print(f"  Std:    {np.nanstd(alpha_dB*1000):8.4f} dB/km")
    print(f"  Min:    {np.nanmin(alpha_dB*1000):8.4f} dB/km  @ {frequency[np.nanargmin(alpha_dB)]:7.1f} Hz")
    print(f"  Max:    {np.nanmax(alpha_dB*1000):8.4f} dB/km  @ {frequency[np.nanargmax(alpha_dB)]:7.1f} Hz")
    
    # Frequency-band averages
    low_mask = (frequency >= 100) & (frequency < 500)
    mid_mask = (frequency >= 500) & (frequency < 2000)
    high_mask = (frequency >= 2000) & (frequency <= 5000)
    
    print(f"\nFrequency Band Averages:")
    print(f"  Low  (100-500 Hz):   TL = {np.nanmean(TL[low_mask]):6.2f} dB,  α = {np.nanmean(alpha_dB[low_mask]*1000):7.3f} dB/km")
    print(f"  Mid  (500-2000 Hz):  TL = {np.nanmean(TL[mid_mask]):6.2f} dB,  α = {np.nanmean(alpha_dB[mid_mask]*1000):7.3f} dB/km")
    print(f"  High (2000-5000 Hz): TL = {np.nanmean(TL[high_mask]):6.2f} dB,  α = {np.nanmean(alpha_dB[high_mask]*1000):7.3f} dB/km")
    
    print("="*80 + "\n")


def main():
    """Main entry point."""
    
    if len(sys.argv) < 2:
        print("Usage: python plot_transmission_loss.py <csv_file>")
        print("\nExample:")
        print("  python plot_transmission_loss.py acoustic_transmission_loss_transmission_loss.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    # Derive output prefix from input filename
    output_prefix = csv_file.replace('.csv', '').replace('_transmission_loss', '')
    
    try:
        # Load data
        print(f"Loading data from: {csv_file}")
        data = load_transmission_loss_data(csv_file)
        
        # Print statistics
        print_summary_statistics(data)
        
        # Generate plots
        print("Generating plots...")
        plot_transmission_loss_analysis(data, output_prefix)
        
        print("\nVisualization completed successfully!")
        
    except Exception as e:
        print(f"\nERROR: Visualization failed!")
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
