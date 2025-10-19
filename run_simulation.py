#!/usr/bin/env python3
"""
Master Script for Abaqus Acoustic Transmission Loss Simulation

This script provides a complete automated workflow for acoustic transmission loss
simulations in Abaqus, from model creation through post-processing.

Usage:
    python run_simulation.py [options]

Examples:
    # Run both layered and gradient models with default parameters
    python run_simulation.py --both
    
    # Run only layered model with custom frequency range
    python run_simulation.py --layered --freq-start 200 --freq-end 2000 --freq-inc 50
    
    # Run with custom geometry and submit jobs
    python run_simulation.py --gradient --length 300 --width 15 --submit

Author: Generated for Abaqus Acoustic Simulation
"""

import os
import sys
import argparse
import subprocess
import time
import json
from pathlib import Path


class AcousticSimulationRunner:
    """
    Master class for running complete acoustic transmission loss simulations
    """
    
    def __init__(self):
        self.config = {
            'geometry': {
                'length': 200.0,  # m
                'width': 10.0,    # m
                'element_size': 2.0  # m
            },
            'frequency': {
                'start': 100.0,   # Hz
                'end': 5000.0,    # Hz
                'increment': 25.0  # Hz
            },
            'materials': {
                'layered': [
                    {'depth_range': (0, 50), 'density': 1000.0, 'bulk_modulus': 2.2e9},
                    {'depth_range': (50, 100), 'density': 1015.0, 'bulk_modulus': 2.25e9},
                    {'depth_range': (100, 150), 'density': 1025.0, 'bulk_modulus': 2.3e9},
                    {'depth_range': (150, 200), 'density': 1030.0, 'bulk_modulus': 2.32e9}
                ],
                'gradient': {
                    'density_base': 1000.0,      # kg/m³
                    'density_gradient': 0.15,    # kg/m³/m
                    'bulk_base': 2.2e9,          # Pa
                    'bulk_gradient': 600000.0    # Pa/m
                }
            },
            'probes': {
                'separation': 190.0  # m
            }
        }
        
        self.jobs = {}
        self.results = {}
    
    def parse_arguments(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description='Run Abaqus acoustic transmission loss simulations',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python run_simulation.py --both --submit
  python run_simulation.py --layered --freq-start 200 --freq-end 2000
  python run_simulation.py --gradient --length 300 --width 15
            """)
        
        # Model selection
        model_group = parser.add_mutually_exclusive_group(required=True)
        model_group.add_argument('--layered', action='store_true',
                               help='Run layered stratification model')
        model_group.add_argument('--gradient', action='store_true',
                               help='Run continuous gradient model')
        model_group.add_argument('--both', action='store_true',
                               help='Run both layered and gradient models')
        
        # Geometry parameters
        parser.add_argument('--length', type=float, default=200.0,
                          help='Waveguide length in meters (default: 200)')
        parser.add_argument('--width', type=float, default=10.0,
                          help='Waveguide width in meters (default: 10)')
        parser.add_argument('--element-size', type=float, default=2.0,
                          help='Target element size in meters (default: 2.0)')
        
        # Frequency parameters
        parser.add_argument('--freq-start', type=float, default=100.0,
                          help='Start frequency in Hz (default: 100)')
        parser.add_argument('--freq-end', type=float, default=5000.0,
                          help='End frequency in Hz (default: 5000)')
        parser.add_argument('--freq-inc', type=float, default=25.0,
                          help='Frequency increment in Hz (default: 25)')
        
        # Execution options
        parser.add_argument('--create-only', action='store_true',
                          help='Only create models, do not submit jobs')
        parser.add_argument('--submit', action='store_true',
                          help='Submit jobs after creation')
        parser.add_argument('--wait', action='store_true',
                          help='Wait for job completion')
        parser.add_argument('--post-process', action='store_true',
                          help='Run post-processing after completion')
        
        # Advanced options
        parser.add_argument('--cpus', type=int, default=1,
                          help='Number of CPUs for parallel processing')
        parser.add_argument('--memory', type=str, default='4gb',
                          help='Memory allocation (e.g., "8gb")')
        parser.add_argument('--output-dir', type=str, default='results',
                          help='Output directory for results')
        
        # Configuration
        parser.add_argument('--config', type=str,
                          help='JSON configuration file')
        parser.add_argument('--save-config', type=str,
                          help='Save current configuration to file')
        
        return parser.parse_args()
    
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                loaded_config = json.load(f)
                self.config.update(loaded_config)
            print(f"Loaded configuration from: {config_file}")
    
    def save_config(self, config_file):
        """Save current configuration to JSON file"""
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"Saved configuration to: {config_file}")
    
    def update_config_from_args(self, args):
        """Update configuration from command line arguments"""
        self.config['geometry']['length'] = args.length
        self.config['geometry']['width'] = args.width
        self.config['geometry']['element_size'] = args.element_size
        
        self.config['frequency']['start'] = args.freq_start
        self.config['frequency']['end'] = args.freq_end
        self.config['frequency']['increment'] = args.freq_inc
    
    def validate_config(self):
        """Validate configuration parameters"""
        errors = []
        
        # Geometry validation
        if self.config['geometry']['length'] <= 0:
            errors.append("Length must be positive")
        if self.config['geometry']['width'] <= 0:
            errors.append("Width must be positive")
        if self.config['geometry']['element_size'] <= 0:
            errors.append("Element size must be positive")
        
        # Frequency validation
        if self.config['frequency']['start'] <= 0:
            errors.append("Start frequency must be positive")
        if self.config['frequency']['end'] <= self.config['frequency']['start']:
            errors.append("End frequency must be greater than start frequency")
        if self.config['frequency']['increment'] <= 0:
            errors.append("Frequency increment must be positive")
        
        # Mesh resolution check
        freq_max = self.config['frequency']['end']
        c_min = 1483  # Approximate minimum sound speed
        wavelength_min = c_min / freq_max
        elements_per_wavelength = wavelength_min / self.config['geometry']['element_size']
        
        if elements_per_wavelength < 6:
            print(f"Warning: Only {elements_per_wavelength:.1f} elements per wavelength at {freq_max} Hz")
            print(f"Recommended element size: {wavelength_min/10:.2f} m")
        
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(errors))
    
    def create_input_files(self, model_type):
        """Create Abaqus input files"""
        print(f"Creating {model_type} input file...")
        
        if model_type == 'layered':
            template_file = 'acoustic_transmission_loss_layered.inp'
            output_file = f'acoustic_{model_type}_{int(time.time())}.inp'
        else:
            template_file = 'acoustic_transmission_loss_gradient.inp'
            output_file = f'acoustic_{model_type}_{int(time.time())}.inp'
        
        # Copy and modify template
        if os.path.exists(template_file):
            with open(template_file, 'r') as f:
                content = f.read()
            
            # Update frequency parameters
            freq_start = self.config['frequency']['start']
            freq_end = self.config['frequency']['end']
            freq_inc = self.config['frequency']['increment']
            
            content = content.replace('100., 5000., 25.', f'{freq_start}, {freq_end}, {freq_inc}.')
            
            with open(output_file, 'w') as f:
                f.write(content)
            
            print(f"Created input file: {output_file}")
            return output_file
        else:
            print(f"Template file not found: {template_file}")
            return None
    
    def create_cae_model(self, model_type):
        """Create model using CAE Python script"""
        print(f"Creating {model_type} model using CAE...")
        
        # Prepare CAE script
        cae_script = f"""
# Import the model builder
execfile('create_acoustic_model.py')

# Create builder with custom parameters
builder = AcousticModelBuilder('AcousticTL_{model_type.title()}')
builder.length = {self.config['geometry']['length']}
builder.width = {self.config['geometry']['width']}
builder.element_size = {self.config['geometry']['element_size']}
builder.freq_start = {self.config['frequency']['start']}
builder.freq_end = {self.config['frequency']['end']}
builder.freq_inc = {self.config['frequency']['increment']}

# Build the model
if '{model_type}' == 'layered':
    job_name = builder.build_layered_model()
else:
    job_name = builder.build_gradient_model()

print(f"Created job: {{job_name}}")
"""
        
        script_file = f'create_{model_type}_model.py'
        with open(script_file, 'w') as f:
            f.write(cae_script)
        
        # Run CAE script
        cmd = ['abaqus', 'cae', '-noGUI', script_file]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print(f"CAE model creation successful")
                # Extract job name from output
                for line in result.stdout.split('\n'):
                    if 'Created job:' in line:
                        job_name = line.split(':')[1].strip()
                        return job_name
            else:
                print(f"CAE model creation failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("CAE model creation timed out")
        except Exception as e:
            print(f"Error running CAE: {e}")
        
        return None
    
    def submit_job(self, job_name, cpus=1, memory='4gb'):
        """Submit Abaqus job"""
        print(f"Submitting job: {job_name}")
        
        cmd = ['abaqus', 'job=' + job_name, f'cpus={cpus}', f'memory={memory}']
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Job {job_name} submitted successfully")
                return True
            else:
                print(f"Job submission failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error submitting job: {e}")
            return False
    
    def wait_for_completion(self, job_name, timeout=3600):
        """Wait for job completion"""
        print(f"Waiting for job completion: {job_name}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check if ODB file exists
            odb_file = f"{job_name}.odb"
            if os.path.exists(odb_file):
                print(f"Job {job_name} completed successfully")
                return True
            
            # Check for error files
            error_files = [f"{job_name}.abq", f"{job_name}.exception"]
            for error_file in error_files:
                if os.path.exists(error_file):
                    print(f"Job {job_name} failed - check {error_file}")
                    return False
            
            time.sleep(30)  # Check every 30 seconds
        
        print(f"Job {job_name} timed out after {timeout} seconds")
        return False
    
    def post_process_results(self, job_name):
        """Run post-processing on completed job"""
        print(f"Post-processing results for: {job_name}")
        
        odb_file = f"{job_name}.odb"
        if not os.path.exists(odb_file):
            print(f"ODB file not found: {odb_file}")
            return False
        
        # Run post-processing script
        probe_separation = self.config['probes']['separation']
        cmd = ['abaqus', 'python', 'acoustic_postprocess.py', odb_file, str(probe_separation)]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                print(f"Post-processing completed for {job_name}")
                print(result.stdout)
                return True
            else:
                print(f"Post-processing failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("Post-processing timed out")
            return False
        except Exception as e:
            print(f"Error in post-processing: {e}")
            return False
    
    def run_simulation(self, model_type, args):
        """Run complete simulation for specified model type"""
        print(f"\n{'='*60}")
        print(f"RUNNING {model_type.upper()} SIMULATION")
        print(f"{'='*60}")
        
        # Create model
        if os.path.exists('create_acoustic_model.py'):
            job_name = self.create_cae_model(model_type)
        else:
            input_file = self.create_input_files(model_type)
            if input_file:
                job_name = input_file.replace('.inp', '')
            else:
                print(f"Failed to create {model_type} model")
                return False
        
        if not job_name:
            print(f"Failed to create {model_type} model")
            return False
        
        self.jobs[model_type] = job_name
        
        # Submit job if requested
        if args.submit or args.wait or args.post_process:
            if not self.submit_job(job_name, args.cpus, args.memory):
                return False
        
        # Wait for completion if requested
        if args.wait or args.post_process:
            if not self.wait_for_completion(job_name):
                return False
        
        # Post-process if requested
        if args.post_process:
            if not self.post_process_results(job_name):
                return False
        
        print(f"{model_type.upper()} simulation setup complete")
        return True
    
    def generate_summary_report(self, output_dir):
        """Generate summary report of all simulations"""
        os.makedirs(output_dir, exist_ok=True)
        
        report_file = os.path.join(output_dir, 'simulation_summary.txt')
        
        with open(report_file, 'w') as f:
            f.write("ABAQUS ACOUSTIC TRANSMISSION LOSS SIMULATION SUMMARY\n")
            f.write("="*60 + "\n\n")
            
            f.write("Configuration:\n")
            f.write(f"  Geometry: {self.config['geometry']['length']} x {self.config['geometry']['width']} m\n")
            f.write(f"  Element size: {self.config['geometry']['element_size']} m\n")
            f.write(f"  Frequency range: {self.config['frequency']['start']}-{self.config['frequency']['end']} Hz\n")
            f.write(f"  Frequency increment: {self.config['frequency']['increment']} Hz\n")
            f.write(f"  Probe separation: {self.config['probes']['separation']} m\n\n")
            
            f.write("Jobs Created:\n")
            for model_type, job_name in self.jobs.items():
                f.write(f"  {model_type.title()}: {job_name}\n")
            
            f.write("\nFiles Generated:\n")
            for model_type, job_name in self.jobs.items():
                f.write(f"  {job_name}.inp - Abaqus input file\n")
                if os.path.exists(f"{job_name}.odb"):
                    f.write(f"  {job_name}.odb - Results database\n")
                if os.path.exists("acoustic_results.csv"):
                    f.write(f"  acoustic_results.csv - Processed results\n")
            
            f.write(f"\nTo submit jobs manually:\n")
            for model_type, job_name in self.jobs.items():
                f.write(f"  abaqus job={job_name} cpus=4 memory=8gb\n")
            
            f.write(f"\nTo post-process results:\n")
            for model_type, job_name in self.jobs.items():
                f.write(f"  abaqus python acoustic_postprocess.py {job_name}.odb {self.config['probes']['separation']}\n")
        
        print(f"Summary report saved to: {report_file}")
    
    def run(self):
        """Main execution method"""
        args = self.parse_arguments()
        
        # Load configuration if specified
        if args.config:
            self.load_config(args.config)
        
        # Update configuration from arguments
        self.update_config_from_args(args)
        
        # Save configuration if requested
        if args.save_config:
            self.save_config(args.save_config)
        
        # Validate configuration
        try:
            self.validate_config()
        except ValueError as e:
            print(f"Configuration error: {e}")
            return 1
        
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Run simulations
        success = True
        
        if args.both:
            success &= self.run_simulation('layered', args)
            success &= self.run_simulation('gradient', args)
        elif args.layered:
            success &= self.run_simulation('layered', args)
        elif args.gradient:
            success &= self.run_simulation('gradient', args)
        
        # Generate summary report
        self.generate_summary_report(args.output_dir)
        
        if success:
            print(f"\n{'='*60}")
            print("SIMULATION SETUP COMPLETED SUCCESSFULLY")
            print(f"{'='*60}")
            print(f"Results will be saved to: {args.output_dir}")
            
            if not (args.submit or args.wait):
                print("\nTo submit jobs:")
                for model_type, job_name in self.jobs.items():
                    print(f"  abaqus job={job_name} cpus={args.cpus} memory={args.memory}")
            
            return 0
        else:
            print("Some simulations failed")
            return 1


def main():
    """Main function"""
    runner = AcousticSimulationRunner()
    return runner.run()


if __name__ == "__main__":
    sys.exit(main())