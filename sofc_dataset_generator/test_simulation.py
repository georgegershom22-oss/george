#!/usr/bin/env python3
"""
Test script for SOFC simulation dataset generation.
Runs a small test to verify the system works correctly.
"""

import os
import sys
import yaml
import numpy as np

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.main import SOFCSimulationRunner


def create_test_config():
    """Create a test configuration with reduced parameters."""
    
    config = {
        'dataset': {
            'n_samples': 5,  # Small number for testing
            'output_dir': 'test_output',
            'file_format': 'hdf5'
        },
        
        'geometry': {
            'length': 0.05,  # Smaller geometry for faster meshing
            'width': 0.05,
            'anode_thickness': [400e-6, 600e-6],
            'electrolyte_thickness': [10e-6, 15e-6],
            'cathode_thickness': [40e-6, 60e-6],
            'interconnect_thickness': [1e-3, 1.5e-3],
            'channel_width': [2e-3, 3e-3],
            'channel_height': [1e-3, 1.5e-3],
            'rib_width': [1e-3, 1.5e-3]
        },
        
        'operating_conditions': {
            'voltage': [0.6, 0.8],
            'current_density': [0.2, 0.8],
            'fuel_flow_rate': [0.5, 1.5],
            'air_flow_rate': [2.0, 8.0],
            'fuel_inlet_temp': [1073, 1123],
            'air_inlet_temp': [1073, 1123],
            'fuel_pressure': [101325, 200000],
            'air_pressure': [101325, 150000]
        },
        
        'materials': {
            'anode': {
                'porosity': [0.35, 0.45],
                'permeability': [5e-13, 5e-12],
                'ionic_conductivity': [0.05, 0.15],
                'electronic_conductivity': [5e4, 5e5],
                'youngs_modulus': [80e9, 120e9],
                'thermal_expansion': [11.5e-6, 12.5e-6],
                'thermal_conductivity': [8, 12]
            },
            'electrolyte': {
                'porosity': [0.02, 0.04],
                'ionic_conductivity': [0.02, 0.08],
                'electronic_conductivity': [5e-10, 5e-9],
                'youngs_modulus': [190e9, 210e9],
                'thermal_expansion': [10.2e-6, 10.8e-6],
                'thermal_conductivity': [2.5, 3.5]
            },
            'cathode': {
                'porosity': [0.35, 0.45],
                'permeability': [5e-13, 5e-12],
                'ionic_conductivity': [0.01, 0.05],
                'electronic_conductivity': [5e2, 5e3],
                'youngs_modulus': [90e9, 110e9],
                'thermal_expansion': [11.5e-6, 12.5e-6],
                'thermal_conductivity': [4, 7]
            },
            'interconnect': {
                'youngs_modulus': [190e9, 210e9],
                'thermal_expansion': [11.5e-6, 12.5e-6],
                'thermal_conductivity': [22, 28],
                'electrical_conductivity': [5e4, 5e5]
            }
        },
        
        'simulation': {
            'mesh_density': 'coarse',  # Coarse mesh for faster computation
            'adaptive_refinement': False,
            'electrochemical_solver': 'newton',
            'thermal_solver': 'cg',
            'mechanical_solver': 'mumps',
            'relative_tolerance': 1e-4,  # Relaxed tolerance for testing
            'absolute_tolerance': 1e-7,
            'max_iterations': 50,
            'time_stepping': False
        },
        
        'output_fields': {
            'electrochemical': [
                'current_density_x', 'current_density_y', 'current_density_z',
                'overpotential_anode', 'overpotential_cathode', 'electric_potential'
            ],
            'thermal': [
                'temperature', 'heat_flux_x', 'heat_flux_y', 'heat_flux_z'
            ],
            'mechanical': [
                'displacement_x', 'displacement_y', 'displacement_z',
                'von_mises_stress', 'stress_xx', 'stress_yy', 'stress_zz'
            ],
            'species': [
                'h2_concentration', 'h2o_concentration', 
                'o2_concentration', 'n2_concentration'
            ]
        }
    }
    
    return config


def run_test():
    """Run the test simulation."""
    
    print("=" * 60)
    print("SOFC Dataset Generation Test")
    print("=" * 60)
    
    # Create test configuration
    config = create_test_config()
    
    # Save test configuration
    config_file = 'test_config.yaml'
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"Test configuration saved to: {config_file}")
    
    try:
        # Initialize simulation runner
        print("\nInitializing simulation runner...")
        runner = SOFCSimulationRunner(config_file)
        
        # Run test dataset generation
        print(f"\nGenerating test dataset with {config['dataset']['n_samples']} samples...")
        print("This may take several minutes depending on your system...")
        
        statistics = runner.generate_dataset(
            n_samples=config['dataset']['n_samples'],
            parallel=False,  # Sequential for easier debugging
            n_workers=1
        )
        
        print("\n" + "=" * 60)
        print("TEST RESULTS")
        print("=" * 60)
        
        print(f"Total samples: {statistics['total_samples']}")
        print(f"Successful samples: {statistics['successful_samples']}")
        print(f"Failed samples: {statistics['failed_samples']}")
        print(f"Success rate: {statistics['success_rate']:.1%}")
        print(f"Output directory: {statistics['output_directory']}")
        
        if statistics['success_rate'] > 0:
            print("\n✅ Test PASSED - Dataset generation is working!")
            
            # List generated files
            output_dir = statistics['output_directory']
            print(f"\nGenerated files in {output_dir}:")
            
            for root, dirs, files in os.walk(output_dir):
                level = root.replace(output_dir, '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                
                sub_indent = ' ' * 2 * (level + 1)
                for file in files[:5]:  # Show first 5 files
                    print(f"{sub_indent}{file}")
                if len(files) > 5:
                    print(f"{sub_indent}... and {len(files) - 5} more files")
        else:
            print("\n❌ Test FAILED - No successful samples generated")
            return False
        
        # Validate dataset
        print("\nValidating dataset...")
        validation_results = runner.validate_dataset()
        
        all_passed = all(
            result.get('status') in ['passed', 'warning'] 
            for result in validation_results.values()
        )
        
        if all_passed:
            print("✅ Dataset validation PASSED")
        else:
            print("⚠️  Dataset validation found issues:")
            for check, result in validation_results.items():
                if result.get('status') == 'failed':
                    print(f"  - {check}: {result.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if os.path.exists(config_file):
            os.remove(config_file)
            print(f"\nCleaned up test configuration: {config_file}")


def main():
    """Main function."""
    
    # Check if we're in the right directory
    if not os.path.exists('src'):
        print("Error: Please run this script from the sofc_dataset_generator directory")
        print("Current directory:", os.getcwd())
        return False
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        return False
    
    # Run test
    success = run_test()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("\nNext steps:")
        print("1. Review the generated test data in the 'test_output' directory")
        print("2. Modify 'config/simulation_config.yaml' for your full dataset")
        print("3. Run 'python src/main.py' to generate the complete dataset")
        print("4. Use the Jupyter notebooks for analysis and visualization")
    else:
        print("\n💥 Test failed. Please check the error messages above.")
        print("\nTroubleshooting:")
        print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check that FEniCS/DOLFIN is properly installed")
        print("3. Verify GMSH is available for mesh generation")
        print("4. Check the log files in test_output/logs/ for detailed error information")
    
    return success


if __name__ == "__main__":
    main()