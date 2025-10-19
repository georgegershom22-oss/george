#!/usr/bin/env python3
"""
Post-Processing Script for Acoustic Transmission Loss Analysis
===============================================================
Extracts pressure data from Abaqus ODB and calculates:
- Transmission Loss TL(f) 
- Absorption coefficient α(f)
- Phase information
- Statistical metrics

Author: Acoustic Analysis Framework
Date: 2025-10-19
Version: 1.0.0
"""

import numpy as np
import matplotlib.pyplot as plt
from odbAccess import openOdb
import sys
import os
import csv
from scipy import signal, optimize
import pandas as pd


class AcousticPostProcessor:
    """
    Post-processing class for acoustic transmission loss analysis.
    """
    
    def __init__(self, odb_path, probe_separation=6.0):
        """
        Initialize the post-processor.
        
        Parameters:
        -----------
        odb_path : str
            Path to the Abaqus ODB file
        probe_separation : float
            Distance between probe planes (m)
        """
        self.odb_path = odb_path
        self.probe_separation = probe_separation
        self.odb = None
        self.frequencies = []
        self.p_in_complex = []
        self.p_out_complex = []
        self.tl_data = []
        self.alpha_data = []
        
    def open_database(self):
        """Open the ODB file."""
        try:
            self.odb = openOdb(self.odb_path, readOnly=True)
            print(f"Successfully opened ODB: {self.odb_path}")
            return True
        except Exception as e:
            print(f"Error opening ODB: {e}")
            return False
    
    def extract_pressure_data(self, step_name='FREQ_SWEEP'):
        """
        Extract complex pressure data from probe locations.
        
        Parameters:
        -----------
        step_name : str
            Name of the frequency sweep step
        """
        if not self.odb:
            print("ODB not opened. Call open_database() first.")
            return
        
        # Get the step
        try:
            step = self.odb.steps[step_name]
        except KeyError:
            print(f"Step '{step_name}' not found in ODB")
            print(f"Available steps: {list(self.odb.steps.keys())}")
            return
        
        # Get probe node sets
        try:
            probe_in_set = self.odb.rootAssembly.nodeSets['PROBE_IN']
            probe_out_set = self.odb.rootAssembly.nodeSets['PROBE_OUT']
        except KeyError as e:
            print(f"Probe set not found: {e}")
            print(f"Available sets: {list(self.odb.rootAssembly.nodeSets.keys())}")
            return
        
        # Extract data for each frequency
        print(f"Extracting pressure data for {len(step.frames)} frequencies...")
        
        for frame_idx, frame in enumerate(step.frames):
            # Get frequency
            freq = frame.frameValue  # In SSD, frameValue is frequency
            self.frequencies.append(freq)
            
            # Get pressure field
            try:
                p_field = frame.fieldOutputs['P']
            except KeyError:
                print(f"Pressure field 'P' not found in frame {frame_idx}")
                continue
            
            # Extract pressure at probe locations
            # PROBE_IN
            p_in_subset = p_field.getSubset(region=probe_in_set)
            p_in_values = []
            for value in p_in_subset.values:
                # Complex pressure: data[0] = real, data[1] = imaginary
                if len(value.data) >= 2:
                    p_complex = complex(value.data[0], value.data[1])
                else:
                    p_complex = complex(value.data[0], 0.0)
                p_in_values.append(p_complex)
            
            # PROBE_OUT
            p_out_subset = p_field.getSubset(region=probe_out_set)
            p_out_values = []
            for value in p_out_subset.values:
                if len(value.data) >= 2:
                    p_complex = complex(value.data[0], value.data[1])
                else:
                    p_complex = complex(value.data[0], 0.0)
                p_out_values.append(p_complex)
            
            # Calculate spatial averages (RMS for complex values)
            p_in_avg = np.mean(p_in_values)
            p_out_avg = np.mean(p_out_values)
            
            self.p_in_complex.append(p_in_avg)
            self.p_out_complex.append(p_out_avg)
            
            # Progress indicator
            if (frame_idx + 1) % 20 == 0:
                print(f"  Processed {frame_idx + 1}/{len(step.frames)} frequencies")
        
        print(f"Extraction complete. Processed {len(self.frequencies)} frequencies.")
        
    def calculate_transmission_loss(self):
        """
        Calculate transmission loss TL(f) from pressure data.
        
        Returns:
        --------
        tl_array : numpy array
            Transmission loss in dB at each frequency
        """
        if not self.p_in_complex or not self.p_out_complex:
            print("No pressure data available. Run extract_pressure_data() first.")
            return None
        
        self.tl_data = []
        
        for i, freq in enumerate(self.frequencies):
            # Calculate magnitudes
            p_in_mag = abs(self.p_in_complex[i])
            p_out_mag = abs(self.p_out_complex[i])
            
            # Avoid log of zero
            if p_out_mag > 0 and p_in_mag > 0:
                # TL = 20*log10(|p_in|/|p_out|)
                tl = 20.0 * np.log10(p_in_mag / p_out_mag)
            else:
                tl = np.nan
            
            self.tl_data.append(tl)
        
        self.tl_data = np.array(self.tl_data)
        
        # Print summary statistics
        valid_tl = self.tl_data[~np.isnan(self.tl_data)]
        if len(valid_tl) > 0:
            print(f"\nTransmission Loss Statistics:")
            print(f"  Mean TL: {np.mean(valid_tl):.2f} dB")
            print(f"  Min TL: {np.min(valid_tl):.2f} dB")
            print(f"  Max TL: {np.max(valid_tl):.2f} dB")
            print(f"  Std Dev: {np.std(valid_tl):.2f} dB")
        
        return self.tl_data
    
    def calculate_absorption_coefficient(self):
        """
        Calculate absorption coefficient α(f) from TL data.
        
        Returns:
        --------
        alpha_array : numpy array
            Absorption coefficient in Np/m at each frequency
        """
        if len(self.tl_data) == 0:
            print("No TL data available. Run calculate_transmission_loss() first.")
            return None
        
        # α_amplitude = (ln(10)/20) * TL / Δx
        # This gives absorption in Nepers/meter
        ln10_over_20 = np.log(10.0) / 20.0
        
        self.alpha_data = []
        for tl in self.tl_data:
            if not np.isnan(tl):
                alpha = ln10_over_20 * tl / self.probe_separation
            else:
                alpha = np.nan
            self.alpha_data.append(alpha)
        
        self.alpha_data = np.array(self.alpha_data)
        
        # Convert to dB/m if desired
        alpha_db_per_m = self.alpha_data * 8.686  # 1 Np = 8.686 dB
        
        # Print summary
        valid_alpha = self.alpha_data[~np.isnan(self.alpha_data)]
        if len(valid_alpha) > 0:
            print(f"\nAbsorption Coefficient Statistics:")
            print(f"  Mean α: {np.mean(valid_alpha):.6f} Np/m")
            print(f"  Mean α: {np.mean(valid_alpha)*8.686:.4f} dB/m")
            print(f"  Min α: {np.min(valid_alpha):.6f} Np/m")
            print(f"  Max α: {np.max(valid_alpha):.6f} Np/m")
        
        return self.alpha_data
    
    def fit_absorption_models(self):
        """
        Fit classical absorption models to the data.
        
        Models:
        - Classical absorption: α = A*f^2 (viscous + thermal)
        - Relaxation: α = A*f^2/(1+(f/f_r)^2) + B*f^2
        """
        if len(self.alpha_data) == 0:
            print("No absorption data available.")
            return None
        
        # Remove NaN values for fitting
        mask = ~np.isnan(self.alpha_data)
        freqs_fit = np.array(self.frequencies)[mask]
        alpha_fit = self.alpha_data[mask]
        
        # Convert to dB/m/kHz for standard ocean acoustics units
        freqs_khz = freqs_fit / 1000.0
        alpha_db_km = alpha_fit * 8686.0  # Np/m to dB/km
        
        # Model 1: Classical f^2 dependence
        def classical_model(f, A):
            return A * f**2
        
        try:
            popt1, pcov1 = optimize.curve_fit(classical_model, freqs_khz, 
                                             alpha_db_km, p0=[0.001])
            A_classical = popt1[0]
            print(f"\nClassical Model Fit (α = A*f^2):")
            print(f"  A = {A_classical:.6e} dB/km/kHz²")
            
            # Calculate R²
            residuals = alpha_db_km - classical_model(freqs_khz, A_classical)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((alpha_db_km - np.mean(alpha_db_km))**2)
            r_squared = 1 - (ss_res / ss_tot)
            print(f"  R² = {r_squared:.4f}")
            
        except Exception as e:
            print(f"Classical model fitting failed: {e}")
            A_classical = None
        
        # Model 2: Thorp's formula approximation (for seawater)
        def thorp_model(f, scale_factor):
            # Simplified Thorp formula
            alpha_thorp = scale_factor * (
                0.11 * f**2 / (1 + f**2) +  # Boric acid relaxation
                44 * f**2 / (4100 + f**2) +  # MgSO4 relaxation  
                2.75e-4 * f**2  # Pure water
            )
            return alpha_thorp
        
        try:
            popt2, pcov2 = optimize.curve_fit(thorp_model, freqs_khz,
                                             alpha_db_km, p0=[1.0])
            scale_thorp = popt2[0]
            print(f"\nThorp-like Model Fit:")
            print(f"  Scale factor = {scale_thorp:.4f}")
            
        except Exception as e:
            print(f"Thorp model fitting failed: {e}")
            scale_thorp = None
        
        return {
            'classical_A': A_classical,
            'thorp_scale': scale_thorp,
            'frequencies_khz': freqs_khz,
            'alpha_db_km': alpha_db_km
        }
    
    def calculate_phase_velocity(self):
        """
        Calculate phase velocity from phase difference between probes.
        
        Returns:
        --------
        phase_velocity : numpy array
            Phase velocity at each frequency (m/s)
        """
        phase_velocities = []
        
        for i, freq in enumerate(self.frequencies):
            if freq == 0:
                phase_velocities.append(np.nan)
                continue
                
            # Calculate phase difference
            phase_in = np.angle(self.p_in_complex[i])
            phase_out = np.angle(self.p_out_complex[i])
            phase_diff = phase_out - phase_in
            
            # Unwrap phase (handle 2π jumps)
            while phase_diff > np.pi:
                phase_diff -= 2*np.pi
            while phase_diff < -np.pi:
                phase_diff += 2*np.pi
            
            # Calculate wavelength and phase velocity
            # k = phase_diff / Δx
            if abs(phase_diff) > 0:
                k = abs(phase_diff) / self.probe_separation
                wavelength = 2 * np.pi / k
                c_phase = wavelength * freq
            else:
                c_phase = np.nan
            
            phase_velocities.append(c_phase)
        
        return np.array(phase_velocities)
    
    def export_to_csv(self, output_file='tl_results.csv'):
        """
        Export results to CSV file.
        
        Parameters:
        -----------
        output_file : str
            Output CSV filename
        """
        if len(self.frequencies) == 0:
            print("No data to export.")
            return
        
        # Prepare data for export
        data = {
            'Frequency_Hz': self.frequencies,
            'P_in_real': [p.real for p in self.p_in_complex],
            'P_in_imag': [p.imag for p in self.p_in_complex],
            'P_in_magnitude': [abs(p) for p in self.p_in_complex],
            'P_out_real': [p.real for p in self.p_out_complex],
            'P_out_imag': [p.imag for p in self.p_out_complex],
            'P_out_magnitude': [abs(p) for p in self.p_out_complex],
            'TL_dB': self.tl_data,
            'Alpha_Np_per_m': self.alpha_data,
            'Alpha_dB_per_m': self.alpha_data * 8.686
        }
        
        # Add phase velocities if calculated
        c_phase = self.calculate_phase_velocity()
        if c_phase is not None:
            data['Phase_velocity_m_per_s'] = c_phase
        
        # Create DataFrame and export
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        print(f"\nResults exported to: {output_file}")
        
        # Also export summary statistics
        stats_file = output_file.replace('.csv', '_statistics.txt')
        with open(stats_file, 'w') as f:
            f.write("ACOUSTIC TRANSMISSION LOSS ANALYSIS - SUMMARY STATISTICS\n")
            f.write("="*60 + "\n\n")
            f.write(f"ODB File: {self.odb_path}\n")
            f.write(f"Probe Separation: {self.probe_separation} m\n")
            f.write(f"Frequency Range: {min(self.frequencies):.1f} - {max(self.frequencies):.1f} Hz\n")
            f.write(f"Number of Frequencies: {len(self.frequencies)}\n\n")
            
            valid_tl = self.tl_data[~np.isnan(self.tl_data)]
            if len(valid_tl) > 0:
                f.write("TRANSMISSION LOSS:\n")
                f.write(f"  Mean: {np.mean(valid_tl):.2f} dB\n")
                f.write(f"  Std Dev: {np.std(valid_tl):.2f} dB\n")
                f.write(f"  Min: {np.min(valid_tl):.2f} dB\n")
                f.write(f"  Max: {np.max(valid_tl):.2f} dB\n\n")
            
            valid_alpha = self.alpha_data[~np.isnan(self.alpha_data)]
            if len(valid_alpha) > 0:
                f.write("ABSORPTION COEFFICIENT:\n")
                f.write(f"  Mean: {np.mean(valid_alpha):.6f} Np/m\n")
                f.write(f"  Mean: {np.mean(valid_alpha)*8.686:.4f} dB/m\n")
                f.write(f"  Std Dev: {np.std(valid_alpha):.6f} Np/m\n")
                f.write(f"  Min: {np.min(valid_alpha):.6f} Np/m\n")
                f.write(f"  Max: {np.max(valid_alpha):.6f} Np/m\n")
        
        print(f"Statistics exported to: {stats_file}")
    
    def plot_results(self, save_plots=True, show_plots=True):
        """
        Create plots of TL and absorption coefficient.
        
        Parameters:
        -----------
        save_plots : bool
            Save plots to files
        show_plots : bool
            Display plots
        """
        if len(self.frequencies) == 0:
            print("No data to plot.")
            return
        
        # Set up figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Acoustic Transmission Loss Analysis Results', fontsize=16)
        
        # Plot 1: Transmission Loss vs Frequency
        ax1 = axes[0, 0]
        ax1.plot(self.frequencies, self.tl_data, 'b-', linewidth=2, label='Measured TL')
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Transmission Loss (dB)')
        ax1.set_title('Transmission Loss Spectrum')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([min(self.frequencies), max(self.frequencies)])
        
        # Add theoretical curves if available
        if hasattr(self, 'theoretical_tl'):
            ax1.plot(self.frequencies, self.theoretical_tl, 'r--', 
                    label='Theoretical', alpha=0.7)
        ax1.legend()
        
        # Plot 2: Absorption Coefficient vs Frequency (log scale)
        ax2 = axes[0, 1]
        alpha_db_m = self.alpha_data * 8.686
        ax2.loglog(self.frequencies, alpha_db_m, 'g-', linewidth=2)
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Absorption Coefficient (dB/m)')
        ax2.set_title('Absorption Coefficient (Log-Log Scale)')
        ax2.grid(True, alpha=0.3, which='both')
        
        # Add f^2 reference line
        f_ref = np.array(self.frequencies)
        alpha_ref = alpha_db_m[len(alpha_db_m)//2] * (f_ref/f_ref[len(f_ref)//2])**2
        ax2.loglog(f_ref, alpha_ref, 'k--', alpha=0.5, label='f² reference')
        ax2.legend()
        
        # Plot 3: Phase of pressure at probes
        ax3 = axes[1, 0]
        phase_in = [np.angle(p, deg=True) for p in self.p_in_complex]
        phase_out = [np.angle(p, deg=True) for p in self.p_out_complex]
        ax3.plot(self.frequencies, phase_in, 'b-', label='Probe IN', alpha=0.7)
        ax3.plot(self.frequencies, phase_out, 'r-', label='Probe OUT', alpha=0.7)
        ax3.set_xlabel('Frequency (Hz)')
        ax3.set_ylabel('Phase (degrees)')
        ax3.set_title('Pressure Phase at Probe Locations')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        # Plot 4: Phase velocity
        ax4 = axes[1, 1]
        c_phase = self.calculate_phase_velocity()
        valid_mask = ~np.isnan(c_phase)
        ax4.plot(np.array(self.frequencies)[valid_mask], c_phase[valid_mask], 
                'mo-', linewidth=2, markersize=4)
        ax4.set_xlabel('Frequency (Hz)')
        ax4.set_ylabel('Phase Velocity (m/s)')
        ax4.set_title('Frequency-Dependent Phase Velocity')
        ax4.grid(True, alpha=0.3)
        
        # Add reference sound speed lines
        ax4.axhline(y=1500, color='k', linestyle='--', alpha=0.5, label='c=1500 m/s')
        ax4.axhline(y=1480, color='k', linestyle=':', alpha=0.5, label='c=1480 m/s')
        ax4.legend()
        
        plt.tight_layout()
        
        if save_plots:
            plot_file = 'tl_analysis_plots.png'
            plt.savefig(plot_file, dpi=150, bbox_inches='tight')
            print(f"Plots saved to: {plot_file}")
        
        if show_plots:
            plt.show()
        
        return fig
    
    def close_database(self):
        """Close the ODB file."""
        if self.odb:
            self.odb.close()
            print("ODB closed.")


def main():
    """
    Main execution function.
    """
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python extract_tl_alpha.py <odb_file> [probe_separation]")
        print("Example: python extract_tl_alpha.py job.odb 6.0")
        sys.exit(1)
    
    odb_file = sys.argv[1]
    probe_sep = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
    
    # Check if file exists
    if not os.path.exists(odb_file):
        print(f"Error: ODB file '{odb_file}' not found.")
        sys.exit(1)
    
    # Create post-processor
    processor = AcousticPostProcessor(odb_file, probe_sep)
    
    # Run analysis
    print("="*60)
    print("ACOUSTIC TRANSMISSION LOSS POST-PROCESSING")
    print("="*60)
    
    if processor.open_database():
        # Extract data
        processor.extract_pressure_data()
        
        # Calculate TL and absorption
        processor.calculate_transmission_loss()
        processor.calculate_absorption_coefficient()
        
        # Fit models
        fit_results = processor.fit_absorption_models()
        
        # Export results
        output_name = os.path.splitext(odb_file)[0] + '_results.csv'
        processor.export_to_csv(output_name)
        
        # Create plots
        processor.plot_results(save_plots=True, show_plots=False)
        
        # Close database
        processor.close_database()
        
        print("\n" + "="*60)
        print("POST-PROCESSING COMPLETE")
        print("="*60)
    else:
        print("Failed to open ODB file.")
        sys.exit(1)


if __name__ == '__main__':
    main()