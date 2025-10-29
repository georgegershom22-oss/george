#!/usr/bin/env python3
"""
Convenient script to run SOFC dataset generation with different configurations.
"""

import os
import sys
import argparse
import yaml
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.main import SOFCSimulationRunner


def create_quick_config(n_samples=100, output_dir="data/sofc_dataset"):
    """Create a quick configuration for dataset generation."""
    
    config = {
        'dataset': {
            'n_samples': n_samples,
            'output_dir': output_dir,
            'file_format': 'hdf5'
        },
        
        'geometry': {
            'length': 0.1,
            'width': 0.1,
            'anode_thickness': [200e-6, 800e-6],
            'electrolyte_thickness': [8e-6, 20e-6],
            'cathode_thickness': [20e-6, 80e-6],
            'interconnect_thickness': [0.5e-3, 2e-3],
            'channel_width': [1e-3, 5e-3],
            'channel_height': [0.5e-3, 2e-3],
            'rib_width': [0.5e-3, 2e-3]
        },
        
        'operating_conditions': {
            'voltage': [0.6, 0.9],
            'current_density': [0.1, 1.0],
            'fuel_flow_rate': [0.1, 2.0],
            'air_flow_rate': [0.5, 10.0],
            'fuel_inlet_temp': [1073, 1173],
            'air_inlet_temp': [1073, 1173],
            'fuel_pressure': [101325, 300000],
            'air_pressure': [101325, 200000]
        },
        
        'materials': {
            'anode': {
                'porosity': [0.3, 0.5],
                'permeability': [1e-13, 1e-11],
                'ionic_conductivity': [1e-2, 1e-1],
                'electronic_conductivity': [1e4, 1e6],
                'youngs_modulus': [50e9, 150e9],
                'thermal_expansion': [11e-6, 13e-6],
                'thermal_conductivity': [5, 15]
            },
            'electrolyte': {
                'porosity': [0.01, 0.05],
                'ionic_conductivity': [0.01, 0.1],
                'electronic_conductivity': [1e-10, 1e-8],
                'youngs_modulus': [180e9, 220e9],
                'thermal_expansion': [10e-6, 11e-6],
                'thermal_conductivity': [2, 4]
            },
            'cathode': {
                'porosity': [0.3, 0.5],
                'permeability': [1e-13, 1e-11],
                'ionic_conductivity': [1e-3, 1e-1],
                'electronic_conductivity': [1e2, 1e4],
                'youngs_modulus': [80e9, 120e9],
                'thermal_expansion': [11e-6, 13e-6],
                'thermal_conductivity': [3, 8]
            },
            'interconnect': {
                'youngs_modulus': [180e9, 220e9],
                'thermal_expansion': [11e-6, 13e-6],
                'thermal_conductivity': [20, 30],
                'electrical_conductivity': [1e4, 1e6]
            }
        },
        
        'simulation': {
            'mesh_density': 'medium',
            'adaptive_refinement': True,
            'electrochemical_solver': 'newton',
            'thermal_solver': 'cg',
            'mechanical_solver': 'mumps',
            'relative_tolerance': 1e-6,
            'absolute_tolerance': 1e-9,
            'max_iterations': 100,
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
                'stress_xx', 'stress_yy', 'stress_zz', 'stress_xy', 
                'stress_xz', 'stress_yz', 'von_mises_stress',
                'strain_xx', 'strain_yy', 'strain_zz'
            ],
            'species': [
                'h2_concentration', 'h2o_concentration',
                'o2_concentration', 'n2_concentration'
            ]
        }
    }
    
    return config


def main():
    """Main function for dataset generation."""
    
    parser = argparse.ArgumentParser(
        description='Generate SOFC High-Fidelity Simulation Dataset',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate small test dataset
  python run_dataset_generation.py --samples 10 --test
  
  # Generate medium dataset with custom output
  python run_dataset_generation.py --samples 500 --output my_dataset
  
  # Generate large dataset with parallel processing
  python run_dataset_generation.py --samples 2000 --parallel --workers 8
  
  # Use existing configuration file
  python run_dataset_generation.py --config config/simulation_config.yaml
        """
    )
    
    parser.add_argument('--samples', type=int, default=100,
                       help='Number of samples to generate (default: 100)')
    
    parser.add_argument('--output', type=str, default=None,
                       help='Output directory (default: data/sofc_dataset_YYYYMMDD_HHMMSS)')
    
    parser.add_argument('--config', type=str, default=None,
                       help='Path to configuration file (default: create automatically)')
    
    parser.add_argument('--parallel', action='store_true', default=True,
                       help='Use parallel processing (default: True)')
    
    parser.add_argument('--workers', type=int, default=None,
                       help='Number of worker processes (default: auto)')
    
    parser.add_argument('--test', action='store_true', default=False,
                       help='Run in test mode with coarse mesh and relaxed tolerances')
    
    parser.add_argument('--validate', action='store_true', default=True,
                       help='Validate dataset after generation (default: True)')
    
    parser.add_argument('--visualize', action='store_true', default=False,
                       help='Generate visualization and analysis after completion')
    
    args = parser.parse_args()
    
    print("🚀 SOFC High-Fidelity Dataset Generator")
    print("=" * 50)
    
    # Determine output directory
    if args.output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"data/sofc_dataset_{timestamp}"
    else:
        output_dir = args.output
    
    # Create or load configuration
    if args.config is None:
        print("📋 Creating automatic configuration...")
        config = create_quick_config(args.samples, output_dir)
        
        # Adjust for test mode
        if args.test:
            print("🧪 Test mode: Using coarse mesh and relaxed tolerances")
            config['simulation']['mesh_density'] = 'coarse'
            config['simulation']['relative_tolerance'] = 1e-4
            config['simulation']['adaptive_refinement'] = False
        
        # Save temporary config
        config_file = 'temp_config.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"📄 Configuration saved to: {config_file}")
        
    else:
        config_file = args.config
        print(f"📄 Using configuration file: {config_file}")
    
    try:
        # Initialize runner
        print("🔧 Initializing simulation runner...")
        runner = SOFCSimulationRunner(config_file)
        
        # Display configuration summary
        print(f"\n📊 Dataset Configuration:")
        print(f"   Samples: {args.samples}")
        print(f"   Output: {output_dir}")
        print(f"   Parallel: {args.parallel}")
        if args.workers:
            print(f"   Workers: {args.workers}")
        print(f"   Test mode: {args.test}")
        
        # Generate dataset
        print(f"\n🏃 Starting dataset generation...")
        print(f"   This may take from minutes to hours depending on:")
        print(f"   - Number of samples ({args.samples})")
        print(f"   - Mesh density ({'coarse' if args.test else 'medium'})")
        print(f"   - System performance")
        print(f"   - Parallel processing ({'enabled' if args.parallel else 'disabled'})")
        
        statistics = runner.generate_dataset(
            n_samples=args.samples,
            parallel=args.parallel,
            n_workers=args.workers
        )
        
        # Display results
        print("\n" + "=" * 50)
        print("📈 GENERATION RESULTS")
        print("=" * 50)
        
        print(f"✅ Total samples: {statistics['total_samples']}")
        print(f"✅ Successful: {statistics['successful_samples']}")
        print(f"❌ Failed: {statistics['failed_samples']}")
        print(f"📊 Success rate: {statistics['success_rate']:.1%}")
        print(f"📁 Output directory: {statistics['output_directory']}")
        
        # Validate if requested
        if args.validate and statistics['success_rate'] > 0:
            print("\n🔍 Validating dataset...")
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
                        print(f"   - {check}: {result.get('error', 'Unknown error')}")
        
        # Generate visualizations if requested
        if args.visualize and statistics['success_rate'] > 0:
            print("\n📊 Generating visualizations...")
            try:
                from src.visualization.visualizer import SOFCVisualizer
                
                visualizer = SOFCVisualizer(statistics['output_directory'])
                report_path = visualizer.generate_analysis_report()
                print(f"📈 Analysis report generated: {report_path}")
                
            except Exception as e:
                print(f"⚠️  Visualization failed: {e}")
        
        # Success summary
        if statistics['success_rate'] > 0.8:
            print("\n🎉 Dataset generation completed successfully!")
        elif statistics['success_rate'] > 0.5:
            print("\n⚠️  Dataset generation completed with some failures")
        else:
            print("\n❌ Dataset generation had significant failures")
        
        print(f"\n📋 Next steps:")
        print(f"   1. Review generated data in: {statistics['output_directory']}")
        print(f"   2. Check logs for any errors: {statistics['output_directory']}/logs/")
        print(f"   3. Use Jupyter notebooks for analysis: notebooks/dataset_analysis.ipynb")
        print(f"   4. Load ML dataset: {statistics.get('ml_dataset_file', 'N/A')}")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️  Generation interrupted by user")
        return False
        
    except Exception as e:
        print(f"\n💥 Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup temporary config
        if args.config is None and os.path.exists('temp_config.yaml'):
            os.remove('temp_config.yaml')


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)