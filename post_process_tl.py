#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Post-Processing Script for Acoustic Transmission Loss Analysis
==============================================================
Extracts pressure data from Abaqus ODB and calculates:
- Transmission Loss (TL) vs frequency
- Absorption coefficient (α) vs frequency
- Spectral analysis and visualization
"""

from odbAccess import openOdb
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, interpolate
import os
import sys

class TLPostProcessor:
    """
    Post-processor for acoustic transmission loss calculations
    """
    
    def __init__(self, odb_path, probe_separation=6.0):
        """
        Initialize post-processor
        
        Parameters:
        -----------
        odb_path : str
            Path to Abaqus ODB file
        probe_separation : float
            Distance between probe planes in meters
        """
        self.odb_path = odb_path
        self.probe_separation = probe_separation
        self.odb = None
        
        # Storage for results
        self.frequencies = []
        self.p_in_magnitude = []
        self.p_out_magnitude = []
        self.p_in_phase = []
        self.p_out_phase = []
        self.tl = []
        self.alpha_amp = []
        self.alpha_int = []
        
    def open_database(self):
        """Open ODB file for reading"""
        try:
            self.odb = openOdb(self.odb_path, readOnly=True)
            print(f"Opened ODB: {self.odb_path}")
            return True
        except Exception as e:
            print(f"Error opening ODB: {e}")
            return False
            
    def extract_pressure_data(self):
        """Extract complex pressure data from probe locations"""
        
        if not self.odb:
            print("ODB not opened. Call open_database() first.")
            return False
            
        try:
            # Get the frequency sweep step
            step_names = self.odb.steps.keys()
            ssd_step = None
            
            for step_name in step_names:
                if 'Frequency' in step_name or 'SSD' in step_name or 'Sweep' in step_name:
                    ssd_step = self.odb.steps[step_name]
                    break
                    
            if not ssd_step:
                print("No frequency sweep step found in ODB")
                return False
                
            print(f"Processing step: {ssd_step.name}")
            
            # Get probe node sets
            assembly = self.odb.rootAssembly
            
            if 'PROBE_IN' not in assembly.nodeSets or 'PROBE_OUT' not in assembly.nodeSets:
                print("Probe sets not found. Looking for alternative names...")
                # Try to find sets with similar names
                for set_name in assembly.nodeSets.keys():
                    print(f"  Found set: {set_name}")
                return False
                
            probe_in_set = assembly.nodeSets['PROBE_IN']
            probe_out_set = assembly.nodeSets['PROBE_OUT']
            
            # Process each frequency frame
            for frame in ssd_step.frames:
                freq = frame.frequency
                self.frequencies.append(freq)
                
                # Get pressure field output
                if 'P' not in frame.fieldOutputs:
                    print(f"Pressure field 'P' not found in frame at {freq} Hz")
                    continue
                    
                pressure_field = frame.fieldOutputs['P']
                
                # Extract pressure at inlet probe
                p_in_subset = pressure_field.getSubset(region=probe_in_set)
                p_in_complex = self._average_complex_pressure(p_in_subset.values)
                
                # Extract pressure at outlet probe
                p_out_subset = pressure_field.getSubset(region=probe_out_set)
                p_out_complex = self._average_complex_pressure(p_out_subset.values)
                
                # Store magnitude and phase
                self.p_in_magnitude.append(p_in_complex[0])
                self.p_in_phase.append(p_in_complex[1])
                self.p_out_magnitude.append(p_out_complex[0])
                self.p_out_phase.append(p_out_complex[1])
                
                print(f"  Frequency {freq:6.1f} Hz: "
                      f"|P_in| = {p_in_complex[0]:.3e}, "
                      f"|P_out| = {p_out_complex[0]:.3e}")
                      
            print(f"\nExtracted data for {len(self.frequencies)} frequencies")
            return True
            
        except Exception as e:
            print(f"Error extracting pressure data: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def _average_complex_pressure(self, values):
        """
        Calculate spatially averaged complex pressure magnitude and phase
        
        Parameters:
        -----------
        values : list
            ODB field output values
            
        Returns:
        --------
        tuple : (magnitude, phase)
        """
        real_parts = []
        imag_parts = []
        
        for value in values:
            # Complex pressure data stored as (real, imaginary)
            if hasattr(value, 'data'):
                if len(value.data) >= 2:
                    real_parts.append(value.data[0])
                    imag_parts.append(value.data[1])
                elif len(value.data) == 1:
                    # Only magnitude provided
                    real_parts.append(value.data[0])
                    imag_parts.append(0.0)
                    
        # Average complex values
        avg_real = np.mean(real_parts) if real_parts else 0.0
        avg_imag = np.mean(imag_parts) if imag_parts else 0.0
        
        # Calculate magnitude and phase
        magnitude = np.sqrt(avg_real**2 + avg_imag**2)
        phase = np.arctan2(avg_imag, avg_real)
        
        return magnitude, phase
        
    def calculate_transmission_loss(self):
        """Calculate transmission loss from pressure data"""
        
        if not self.p_in_magnitude or not self.p_out_magnitude:
            print("No pressure data available. Extract data first.")
            return False
            
        # Calculate TL for each frequency
        self.tl = []
        
        for p_in, p_out in zip(self.p_in_magnitude, self.p_out_magnitude):
            if p_in > 0 and p_out > 0:
                tl_value = 20.0 * np.log10(p_in / p_out)
            else:
                tl_value = 0.0
            self.tl.append(tl_value)
            
        print(f"\nTransmission Loss calculated for {len(self.tl)} frequencies")
        print(f"TL range: {min(self.tl):.1f} to {max(self.tl):.1f} dB")
        
        return True
        
    def calculate_absorption_coefficient(self):
        """Calculate absorption coefficient from TL data"""
        
        if not self.tl:
            print("No TL data available. Calculate TL first.")
            return False
            
        # Amplitude absorption coefficient: α_amp = (ln(10)/20) * TL / Δx
        ln10_20 = np.log(10) / 20.0
        
        self.alpha_amp = []
        self.alpha_int = []
        
        for tl_value in self.tl:
            # Amplitude-based absorption
            alpha_a = ln10_20 * tl_value / self.probe_separation
            self.alpha_amp.append(alpha_a)
            
            # Intensity-based absorption (half of amplitude-based)
            alpha_i = alpha_a / 2.0
            self.alpha_int.append(alpha_i)
            
        print(f"\nAbsorption coefficient calculated")
        print(f"α_amp range: {min(self.alpha_amp):.4f} to {max(self.alpha_amp):.4f} m⁻¹")
        print(f"α_int range: {min(self.alpha_int):.4f} to {max(self.alpha_int):.4f} m⁻¹")
        
        return True
        
    def fit_absorption_model(self):
        """Fit theoretical absorption models to data"""
        
        if not self.frequencies or not self.alpha_amp:
            print("No data available for fitting")
            return None
            
        frequencies = np.array(self.frequencies)
        alpha_measured = np.array(self.alpha_amp)
        
        # Classical absorption (Stokes-Kirchhoff)
        # α_classical = 2πf²/(ρc³) * (4μ/3 + μ_B + κ(γ-1)/C_p)
        # Simplified: α = A*f²
        
        # Fit power law: α = A*f^n
        log_f = np.log(frequencies[frequencies > 0])
        log_alpha = np.log(alpha_measured[frequencies > 0])
        
        # Linear regression in log-log space
        coeffs = np.polyfit(log_f, log_alpha, 1)
        n_exponent = coeffs[0]
        A_coefficient = np.exp(coeffs[1])
        
        # Generate fitted curve
        alpha_fitted = A_coefficient * frequencies**n_exponent
        
        # Calculate R-squared
        residuals = alpha_measured - alpha_fitted
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((alpha_measured - np.mean(alpha_measured))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        print(f"\nPower law fit: α = {A_coefficient:.3e} * f^{n_exponent:.3f}")
        print(f"R² = {r_squared:.4f}")
        
        return {
            'A': A_coefficient,
            'n': n_exponent,
            'r_squared': r_squared,
            'fitted_values': alpha_fitted
        }
        
    def save_results(self, output_dir='.'):
        """Save results to CSV files"""
        
        if not self.frequencies:
            print("No results to save")
            return False
            
        # Prepare data for export
        data = np.column_stack([
            self.frequencies,
            self.p_in_magnitude,
            self.p_out_magnitude,
            self.tl,
            self.alpha_amp,
            self.alpha_int
        ])
        
        # Create header
        header = 'Frequency [Hz], P_in [Pa], P_out [Pa], TL [dB], Alpha_amp [1/m], Alpha_int [1/m]'
        
        # Save to CSV
        output_file = os.path.join(output_dir, 'transmission_loss_results.csv')
        np.savetxt(output_file, data, delimiter=',', header=header, fmt='%.6e')
        print(f"\nResults saved to: {output_file}")
        
        # Save summary statistics
        summary_file = os.path.join(output_dir, 'tl_summary.txt')
        with open(summary_file, 'w') as f:
            f.write("TRANSMISSION LOSS ANALYSIS SUMMARY\n")
            f.write("="*50 + "\n\n")
            f.write(f"ODB File: {self.odb_path}\n")
            f.write(f"Probe Separation: {self.probe_separation} m\n")
            f.write(f"Frequency Range: {min(self.frequencies):.1f} - {max(self.frequencies):.1f} Hz\n")
            f.write(f"Number of Frequencies: {len(self.frequencies)}\n\n")
            
            f.write("TRANSMISSION LOSS:\n")
            f.write(f"  Mean TL: {np.mean(self.tl):.2f} dB\n")
            f.write(f"  Max TL: {max(self.tl):.2f} dB at {self.frequencies[np.argmax(self.tl)]:.1f} Hz\n")
            f.write(f"  Min TL: {min(self.tl):.2f} dB at {self.frequencies[np.argmin(self.tl)]:.1f} Hz\n\n")
            
            f.write("ABSORPTION COEFFICIENT:\n")
            f.write(f"  Mean α_amp: {np.mean(self.alpha_amp):.4f} m⁻¹\n")
            f.write(f"  Max α_amp: {max(self.alpha_amp):.4f} m⁻¹ at {self.frequencies[np.argmax(self.alpha_amp)]:.1f} Hz\n")
            f.write(f"  Min α_amp: {min(self.alpha_amp):.4f} m⁻¹ at {self.frequencies[np.argmin(self.alpha_amp)]:.1f} Hz\n")
            
        print(f"Summary saved to: {summary_file}")
        return True
        
    def plot_results(self, save_plots=True, show_plots=True):
        """Generate plots of TL and absorption coefficient"""
        
        if not self.frequencies:
            print("No data to plot")
            return False
            
        # Set up figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Acoustic Transmission Loss Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Transmission Loss vs Frequency
        ax1 = axes[0, 0]
        ax1.plot(self.frequencies, self.tl, 'b-', linewidth=2, label='Measured TL')
        ax1.set_xlabel('Frequency (Hz)', fontsize=12)
        ax1.set_ylabel('Transmission Loss (dB)', fontsize=12)
        ax1.set_title('Transmission Loss Spectrum', fontsize=14)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([min(self.frequencies), max(self.frequencies)])
        
        # Add reference lines for classical absorption
        f_array = np.array(self.frequencies)
        tl_f2 = self.tl[len(self.tl)//2] * (f_array/f_array[len(f_array)//2])**2
        ax1.plot(f_array, tl_f2, 'r--', alpha=0.5, label='f² reference')
        ax1.legend()
        
        # Plot 2: Absorption Coefficient vs Frequency
        ax2 = axes[0, 1]
        ax2.plot(self.frequencies, self.alpha_amp, 'g-', linewidth=2, label='α_amplitude')
        ax2.plot(self.frequencies, self.alpha_int, 'r-', linewidth=2, label='α_intensity')
        ax2.set_xlabel('Frequency (Hz)', fontsize=12)
        ax2.set_ylabel('Absorption Coefficient (m⁻¹)', fontsize=12)
        ax2.set_title('Absorption Coefficient Spectrum', fontsize=14)
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # Plot 3: Log-log plot of absorption
        ax3 = axes[1, 0]
        ax3.loglog(self.frequencies, self.alpha_amp, 'bo-', markersize=4, label='Measured')
        
        # Add fitted model
        fit_result = self.fit_absorption_model()
        if fit_result:
            ax3.loglog(self.frequencies, fit_result['fitted_values'], 'r--', 
                      linewidth=2, label=f"Fit: α = {fit_result['A']:.2e}f^{fit_result['n']:.2f}")
        
        ax3.set_xlabel('Frequency (Hz)', fontsize=12)
        ax3.set_ylabel('Absorption Coefficient (m⁻¹)', fontsize=12)
        ax3.set_title('Log-Log Absorption Spectrum', fontsize=14)
        ax3.grid(True, alpha=0.3, which='both')
        ax3.legend()
        
        # Plot 4: Pressure amplitude decay
        ax4 = axes[1, 1]
        ax4.semilogy(self.frequencies, self.p_in_magnitude, 'b-', linewidth=2, label='Input probe')
        ax4.semilogy(self.frequencies, self.p_out_magnitude, 'r-', linewidth=2, label='Output probe')
        ax4.set_xlabel('Frequency (Hz)', fontsize=12)
        ax4.set_ylabel('Pressure Magnitude (Pa)', fontsize=12)
        ax4.set_title('Pressure Amplitude at Probes', fontsize=14)
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        
        plt.tight_layout()
        
        if save_plots:
            plot_file = 'transmission_loss_plots.png'
            plt.savefig(plot_file, dpi=150, bbox_inches='tight')
            print(f"\nPlots saved to: {plot_file}")
            
        if show_plots:
            plt.show()
            
        return True
        
    def generate_report(self):
        """Generate comprehensive HTML report"""
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Acoustic Transmission Loss Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                h2 { color: #34495e; margin-top: 30px; }
                table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background-color: #3498db; color: white; }
                tr:nth-child(even) { background-color: #f2f2f2; }
                .metric { background-color: #ecf0f1; padding: 10px; margin: 10px 0; border-radius: 5px; }
                .value { font-weight: bold; color: #2980b9; }
            </style>
        </head>
        <body>
            <h1>Acoustic Transmission Loss Analysis Report</h1>
            
            <h2>Simulation Parameters</h2>
            <div class="metric">
                <p>ODB File: <span class="value">{odb_file}</span></p>
                <p>Probe Separation: <span class="value">{probe_sep:.2f} m</span></p>
                <p>Frequency Range: <span class="value">{f_min:.1f} - {f_max:.1f} Hz</span></p>
                <p>Number of Frequencies: <span class="value">{n_freq}</span></p>
            </div>
            
            <h2>Key Results</h2>
            <div class="metric">
                <h3>Transmission Loss</h3>
                <p>Mean TL: <span class="value">{tl_mean:.2f} dB</span></p>
                <p>Maximum TL: <span class="value">{tl_max:.2f} dB at {f_tl_max:.1f} Hz</span></p>
                <p>Minimum TL: <span class="value">{tl_min:.2f} dB at {f_tl_min:.1f} Hz</span></p>
            </div>
            
            <div class="metric">
                <h3>Absorption Coefficient</h3>
                <p>Mean α: <span class="value">{alpha_mean:.4f} m⁻¹</span></p>
                <p>Maximum α: <span class="value">{alpha_max:.4f} m⁻¹ at {f_alpha_max:.1f} Hz</span></p>
                <p>Power Law Fit: <span class="value">α = {A:.3e} × f^{n:.3f}</span></p>
                <p>R² Value: <span class="value">{r2:.4f}</span></p>
            </div>
            
            <h2>Frequency-Dependent Results</h2>
            <table>
                <tr>
                    <th>Frequency (Hz)</th>
                    <th>TL (dB)</th>
                    <th>α_amp (m⁻¹)</th>
                    <th>α_int (m⁻¹)</th>
                </tr>
                {table_rows}
            </table>
            
            <h2>Visualization</h2>
            <img src="transmission_loss_plots.png" alt="TL Plots" style="width:100%; max-width:1200px;">
            
        </body>
        </html>
        """
        
        # Generate table rows
        table_rows = ""
        step = max(1, len(self.frequencies) // 20)  # Show max 20 rows
        for i in range(0, len(self.frequencies), step):
            table_rows += f"""
                <tr>
                    <td>{self.frequencies[i]:.1f}</td>
                    <td>{self.tl[i]:.2f}</td>
                    <td>{self.alpha_amp[i]:.4f}</td>
                    <td>{self.alpha_int[i]:.4f}</td>
                </tr>
            """
        
        # Get fit results
        fit_result = self.fit_absorption_model()
        
        # Fill template
        html_filled = html_content.format(
            odb_file=os.path.basename(self.odb_path),
            probe_sep=self.probe_separation,
            f_min=min(self.frequencies),
            f_max=max(self.frequencies),
            n_freq=len(self.frequencies),
            tl_mean=np.mean(self.tl),
            tl_max=max(self.tl),
            f_tl_max=self.frequencies[np.argmax(self.tl)],
            tl_min=min(self.tl),
            f_tl_min=self.frequencies[np.argmin(self.tl)],
            alpha_mean=np.mean(self.alpha_amp),
            alpha_max=max(self.alpha_amp),
            f_alpha_max=self.frequencies[np.argmax(self.alpha_amp)],
            A=fit_result['A'] if fit_result else 0,
            n=fit_result['n'] if fit_result else 0,
            r2=fit_result['r_squared'] if fit_result else 0,
            table_rows=table_rows
        )
        
        # Save HTML report
        with open('tl_report.html', 'w') as f:
            f.write(html_filled)
            
        print("\nHTML report generated: tl_report.html")
        return True
        
    def close_database(self):
        """Close ODB file"""
        if self.odb:
            self.odb.close()
            print("ODB closed")
            
    def run_complete_analysis(self):
        """Execute complete post-processing workflow"""
        
        print("\n" + "="*60)
        print("ACOUSTIC TRANSMISSION LOSS POST-PROCESSING")
        print("="*60 + "\n")
        
        # Open database
        if not self.open_database():
            return False
            
        # Extract data
        if not self.extract_pressure_data():
            self.close_database()
            return False
            
        # Calculate TL
        if not self.calculate_transmission_loss():
            self.close_database()
            return False
            
        # Calculate absorption
        if not self.calculate_absorption_coefficient():
            self.close_database()
            return False
            
        # Fit model
        self.fit_absorption_model()
        
        # Save results
        self.save_results()
        
        # Generate plots
        self.plot_results(save_plots=True, show_plots=False)
        
        # Generate report
        self.generate_report()
        
        # Close database
        self.close_database()
        
        print("\n" + "="*60)
        print("POST-PROCESSING COMPLETED SUCCESSFULLY")
        print("="*60)
        
        return True


# Main execution
if __name__ == "__main__":
    
    # Command line arguments
    if len(sys.argv) > 1:
        odb_file = sys.argv[1]
    else:
        # Default ODB files to look for
        possible_files = ['TL_Layered.odb', 'TL_Graded.odb', 'AcousticTL_Job.odb']
        odb_file = None
        
        for pf in possible_files:
            if os.path.exists(pf):
                odb_file = pf
                break
                
        if not odb_file:
            print("Usage: python post_process_tl.py <odb_file>")
            print("No ODB file found. Please specify the path to your ODB file.")
            sys.exit(1)
    
    # Probe separation distance (meters)
    probe_separation = 6.0  # Default: 8.0 - 2.0 = 6.0 m
    
    if len(sys.argv) > 2:
        probe_separation = float(sys.argv[2])
    
    # Create processor instance
    processor = TLPostProcessor(odb_file, probe_separation)
    
    # Run complete analysis
    success = processor.run_complete_analysis()
    
    if success:
        print("\nAnalysis complete! Check the following output files:")
        print("  - transmission_loss_results.csv : Numerical data")
        print("  - tl_summary.txt : Statistical summary")
        print("  - transmission_loss_plots.png : Visualization")
        print("  - tl_report.html : Complete HTML report")
    else:
        print("\nAnalysis failed. Check error messages above.")
        sys.exit(1)