#!/usr/bin/env python
"""
Complete Abaqus Acoustic Simulation Runner
==========================================

This script demonstrates how to run complete acoustic transmission loss
simulations from start to finish, including model creation, analysis,
and post-processing.

Features:
- Automated workflow execution
- Multiple simulation scenarios
- Quality validation
- Result comparison
- Parametric studies

Author: AI Assistant
Date: 2025-10-19
Units: SI (m-kg-s-Pa)
"""

import os
import sys
import time
import numpy as np
from abaqus_acoustic_simulation import AcousticSimulation
from abaqus_input_generator import AbaqusInputGenerator
from post_processing_tools import AcousticPostProcessor, process_odb_file


def run_layered_medium_study():
    """Run a complete layered medium study with multiple configurations."""
    print("\n" + "="*60)
    print("LAYERED MEDIUM PARAMETRIC STUDY")
    print("="*60)
    
    # Define different layer configurations
    configurations = [
        {
            'name': 'TwoLayer_Sharp',
            'description': 'Two layers with sharp density contrast',
            'layers': [
                {'name': 'WATER_BOTTOM', 'density': 1030.0, 'bulk_modulus': 2.4e9, 'thickness': 2.0},
                {'name': 'WATER_TOP', 'density': 1020.0, 'bulk_modulus': 2.2e9, 'thickness': 2.0}
            ]
        },
        {
            'name': 'TwoLayer_Mild',
            'description': 'Two layers with mild density contrast',
            'layers': [
                {'name': 'WATER_BOTTOM', 'density': 1027.0, 'bulk_modulus': 2.35e9, 'thickness': 2.0},
                {'name': 'WATER_TOP', 'density': 1023.0, 'bulk_modulus': 2.25e9, 'thickness': 2.0}
            ]
        },
        {
            'name': 'ThreeLayer',
            'description': 'Three layers with varying properties',
            'layers': [
                {'name': 'WATER_BOTTOM', 'density': 1035.0, 'bulk_modulus': 2.5e9, 'thickness': 1.5},
                {'name': 'WATER_MIDDLE', 'density': 1025.0, 'bulk_modulus': 2.3e9, 'thickness': 1.0},
                {'name': 'WATER_TOP', 'density': 1020.0, 'bulk_modulus': 2.2e9, 'thickness': 1.5}
            ]
        }
    ]
    
    results_summary = {}
    
    for config in configurations:
        print(f"\nRunning configuration: {config['name']}")
        print(f"Description: {config['description']}")
        
        try:
            # Create simulation
            sim = AcousticSimulation(model_name=config['name'])
            sim.create_model()
            
            # Create geometry
            sim.create_2d_geometry(length=10.0, height=4.0)
            
            # Create materials
            sim.create_layered_materials(config['layers'])
            
            # Partition and assign sections
            sim.partition_for_layers(config['layers'], dimension='2D')
            sim.assign_layered_sections(config['layers'], dimension='2D')
            
            # Create mesh (adaptive sizing based on highest frequency)
            target_freq = 2000.0
            sim.create_mesh(element_type='AC2D4', target_frequency=target_freq)
            
            # Validate mesh
            elements_per_wavelength = sim.validate_mesh_resolution(target_frequency=target_freq)
            
            # Create assembly
            sim.create_assembly()
            
            # Create analysis step
            sim.create_steady_state_step(freq_start=100.0, freq_end=2000.0, freq_inc=50.0)
            
            # Create loading and boundaries
            sim.create_incident_wave(direction=(1.0, 0.0, 0.0))
            sim.create_non_reflecting_boundaries()
            
            # Create output requests
            sim.create_output_requests()
            
            # Create and submit job
            sim.create_job(job_name=config['name'], num_cpus=2)
            
            print(f"Model created successfully: {config['name']}")
            print(f"Elements per wavelength: {elements_per_wavelength:.1f}")
            
            # Submit job (uncomment to actually run)
            print("To run this simulation:")
            print(f"  sim.run_analysis(wait_for_completion=True)")
            print(f"  results = sim.post_process_transmission_loss()")
            
            results_summary[config['name']] = {
                'status': 'model_created',
                'elements_per_wavelength': elements_per_wavelength,
                'num_layers': len(config['layers']),
                'total_thickness': sum(layer['thickness'] for layer in config['layers'])
            }
            
        except Exception as e:
            print(f"Error creating model {config['name']}: {e}")
            results_summary[config['name']] = {'status': 'failed', 'error': str(e)}
            
    # Print summary
    print("\n" + "="*60)
    print("PARAMETRIC STUDY SUMMARY")
    print("="*60)
    
    for name, result in results_summary.items():
        print(f"\n{name}:")
        print(f"  Status: {result['status']}")
        if result['status'] == 'model_created':
            print(f"  Layers: {result['num_layers']}")
            print(f"  Total thickness: {result['total_thickness']:.1f} m")
            print(f"  Mesh quality: {result['elements_per_wavelength']:.1f} elem/λ")
        elif result['status'] == 'failed':
            print(f"  Error: {result['error']}")
            
    return results_summary


def run_graded_medium_study():
    """Run graded medium study with different gradient profiles."""
    print("\n" + "="*60)
    print("GRADED MEDIUM STUDY")
    print("="*60)
    
    # Define gradient profiles
    profiles = [
        {
            'name': 'Linear_Gradient',
            'description': 'Linear density and bulk modulus gradients',
            'density_profile': [
                (0.0, 1020.0),    # Surface
                (2.0, 1030.0)     # Bottom
            ],
            'bulk_modulus_profile': [
                (0.0, 2.2e9),     # Surface
                (2.0, 2.4e9)      # Bottom
            ]
        },
        {
            'name': 'Exponential_Gradient',
            'description': 'Exponential-like gradient (piecewise linear approximation)',
            'density_profile': [
                (0.0, 1020.0),    # Surface
                (0.5, 1022.0),    # Shallow
                (1.0, 1025.0),    # Mid
                (1.5, 1028.0),    # Deep
                (2.0, 1032.0)     # Bottom
            ],
            'bulk_modulus_profile': [
                (0.0, 2.2e9),     # Surface
                (0.5, 2.25e9),    # Shallow
                (1.0, 2.3e9),     # Mid
                (1.5, 2.35e9),    # Deep
                (2.0, 2.45e9)     # Bottom
            ]
        }
    ]
    
    results_summary = {}
    
    for profile in profiles:
        print(f"\nRunning profile: {profile['name']}")
        print(f"Description: {profile['description']}")
        
        try:
            # Create simulation
            sim = AcousticSimulation(model_name=profile['name'])
            sim.create_model()
            
            # Create geometry (smaller for graded case)
            sim.create_2d_geometry(length=8.0, height=2.0)
            
            # Create analytical field
            sim.create_analytical_field(name='DepthField', expression='Y')
            
            # Create graded material
            sim.create_graded_material('WATER_GRADED', 
                                     profile['density_profile'],
                                     profile['bulk_modulus_profile'])
            
            # Assign section
            sim.assign_graded_section('WATER_GRADED', 'DepthField')
            
            # Create mesh
            sim.create_mesh(element_type='AC2D4', target_frequency=1500.0)
            
            # Create assembly
            sim.create_assembly()
            
            # Create analysis step
            sim.create_steady_state_step(freq_start=200.0, freq_end=1500.0, freq_inc=100.0)
            
            # Create loading and boundaries
            sim.create_incident_wave(direction=(1.0, 0.0, 0.0))
            sim.create_non_reflecting_boundaries()
            
            # Create output requests
            sim.create_output_requests()
            
            # Create job
            sim.create_job(job_name=profile['name'], num_cpus=2)
            
            print(f"Graded model created successfully: {profile['name']}")
            
            results_summary[profile['name']] = {
                'status': 'model_created',
                'profile_points': len(profile['density_profile'])
            }
            
        except Exception as e:
            print(f"Error creating graded model {profile['name']}: {e}")
            results_summary[profile['name']] = {'status': 'failed', 'error': str(e)}
            
    return results_summary


def run_frequency_convergence_study():
    """Study convergence with respect to frequency resolution."""
    print("\n" + "="*60)
    print("FREQUENCY CONVERGENCE STUDY")
    print("="*60)
    
    # Different frequency increments
    freq_increments = [100.0, 50.0, 25.0, 10.0]
    
    results_summary = {}
    
    for freq_inc in freq_increments:
        model_name = f"FreqConv_{int(freq_inc)}Hz"
        print(f"\nRunning frequency increment: {freq_inc} Hz")
        
        try:
            # Create simple validation case
            sim = AcousticSimulation(model_name=model_name)
            sim.create_model()
            
            # Simple homogeneous medium
            sim.create_2d_geometry(length=5.0, height=2.0)
            
            layers = [{'name': 'WATER', 'density': 1025.0, 'bulk_modulus': 2.306e9, 'thickness': 2.0}]
            sim.create_layered_materials(layers)
            
            # No partitioning needed for single layer
            sim.assign_layered_sections(layers, dimension='2D')
            
            # Create mesh
            sim.create_mesh(element_type='AC2D4', target_frequency=1000.0)
            
            # Create assembly
            sim.create_assembly()
            
            # Create analysis step with specific frequency increment
            sim.create_steady_state_step(freq_start=200.0, freq_end=1000.0, freq_inc=freq_inc)
            
            # Create loading and boundaries
            sim.create_incident_wave(direction=(1.0, 0.0, 0.0))
            sim.create_non_reflecting_boundaries()
            
            # Create output requests
            sim.create_output_requests()
            
            # Create job
            sim.create_job(job_name=model_name, num_cpus=1)
            
            num_frequencies = int((1000.0 - 200.0) / freq_inc) + 1
            print(f"Model created: {num_frequencies} frequency points")
            
            results_summary[model_name] = {
                'status': 'model_created',
                'freq_increment': freq_inc,
                'num_frequencies': num_frequencies
            }
            
        except Exception as e:
            print(f"Error creating frequency convergence model: {e}")
            results_summary[model_name] = {'status': 'failed', 'error': str(e)}
            
    return results_summary


def run_mesh_convergence_study():
    """Study convergence with respect to mesh density."""
    print("\n" + "="*60)
    print("MESH CONVERGENCE STUDY")
    print("="*60)
    
    # Different elements per wavelength
    elements_per_wavelength = [8, 10, 12, 15, 20]
    target_frequency = 1000.0  # Hz
    
    results_summary = {}
    
    for elem_per_wave in elements_per_wavelength:
        model_name = f"MeshConv_{elem_per_wave}EPW"
        print(f"\nRunning mesh density: {elem_per_wave} elements per wavelength")
        
        try:
            # Create simulation
            sim = AcousticSimulation(model_name=model_name)
            sim.create_model()
            
            # Simple geometry
            sim.create_2d_geometry(length=5.0, height=2.0)
            
            # Single layer
            layers = [{'name': 'WATER', 'density': 1025.0, 'bulk_modulus': 2.306e9, 'thickness': 2.0}]
            sim.create_layered_materials(layers)
            sim.assign_layered_sections(layers, dimension='2D')
            
            # Create mesh with specific density
            sim.create_mesh(element_type='AC2D4', 
                          target_frequency=target_frequency,
                          elements_per_wavelength=elem_per_wave)
            
            # Validate mesh
            actual_epw = sim.validate_mesh_resolution(target_frequency=target_frequency)
            
            # Create assembly
            sim.create_assembly()
            
            # Create analysis step
            sim.create_steady_state_step(freq_start=500.0, freq_end=1500.0, freq_inc=100.0)
            
            # Create loading and boundaries
            sim.create_incident_wave(direction=(1.0, 0.0, 0.0))
            sim.create_non_reflecting_boundaries()
            
            # Create output requests
            sim.create_output_requests()
            
            # Create job
            sim.create_job(job_name=model_name, num_cpus=1)
            
            print(f"Model created: target {elem_per_wave} EPW, actual {actual_epw:.1f} EPW")
            
            results_summary[model_name] = {
                'status': 'model_created',
                'target_epw': elem_per_wave,
                'actual_epw': actual_epw,
                'num_elements': len(sim.part.elements) if sim.part else 0
            }
            
        except Exception as e:
            print(f"Error creating mesh convergence model: {e}")
            results_summary[model_name] = {'status': 'failed', 'error': str(e)}
            
    return results_summary


def create_input_file_examples():
    """Create example input files for different scenarios."""
    print("\n" + "="*60)
    print("CREATING INPUT FILE EXAMPLES")
    print("="*60)
    
    try:
        # 2D Layered medium
        print("Creating 2D layered medium input file...")
        gen1 = AbaqusInputGenerator('LayeredMedium2D')
        gen1.generate_2d_rectangular_mesh(10.0, 4.0, 100, 40)
        
        layers = [
            {'name': 'WATER_BOTTOM', 'density': 1030.0, 'bulk_modulus': 2.4e9},
            {'name': 'WATER_TOP', 'density': 1020.0, 'bulk_modulus': 2.2e9}
        ]
        gen1.add_layered_materials(layers)
        gen1.create_layered_element_sets([2.0, 4.0])
        gen1.write_input_file('layered_medium_2d.inp', '2D_LAYERED')
        
        # 3D Graded medium
        print("Creating 3D graded medium input file...")
        gen2 = AbaqusInputGenerator('GradedMedium3D')
        gen2.generate_3d_rectangular_mesh(8.0, 3.0, 2.0, 40, 15, 10)
        
        density_profile = [(0.0, 1020.0), (1.5, 1025.0), (3.0, 1030.0)]
        bulk_modulus_profile = [(0.0, 2.2e9), (1.5, 2.3e9), (3.0, 2.4e9)]
        gen2.add_graded_material('GRADED_MATERIAL', density_profile, bulk_modulus_profile)
        gen2.write_input_file('graded_medium_3d.inp', '3D_GRADED')
        
        # Validation case
        print("Creating validation case input file...")
        gen3 = AbaqusInputGenerator('ValidationCase')
        gen3.generate_2d_rectangular_mesh(5.0, 2.0, 50, 20)
        
        validation_layers = [{'name': 'WATER', 'density': 1025.0, 'bulk_modulus': 2.306e9}]
        gen3.add_layered_materials(validation_layers)
        
        all_elements = [elem[0] for elem in gen3.elements]
        gen3.element_sets['ALL_ELEMENTS'] = all_elements
        gen3.write_input_file('validation_case.inp', '2D_LAYERED')
        
        print("Input files created successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error creating input files: {e}")
        return False


def demonstrate_post_processing():
    """Demonstrate post-processing capabilities with synthetic data."""
    print("\n" + "="*60)
    print("POST-PROCESSING DEMONSTRATION")
    print("="*60)
    
    try:
        # Create synthetic data to demonstrate post-processing
        frequencies = np.linspace(100, 2000, 39)  # 50 Hz increment
        
        # Synthetic pressure data with realistic transmission loss
        pin_magnitude = np.ones_like(frequencies) * 1000.0  # 1000 Pa input
        
        # Transmission loss increases with frequency (typical behavior)
        TL_theoretical = 10 * np.log10(frequencies / 100.0) + 5 * np.sin(frequencies / 500.0)
        pout_magnitude = pin_magnitude / (10**(TL_theoretical / 20.0))
        
        # Create synthetic probe data
        probe_data = {
            'PROBE_IN': {
                'magnitude': pin_magnitude,
                'real': pin_magnitude * np.cos(np.zeros_like(frequencies)),
                'imag': pin_magnitude * np.sin(np.zeros_like(frequencies)),
                'phase': np.zeros_like(frequencies)
            },
            'PROBE_OUT': {
                'magnitude': pout_magnitude,
                'real': pout_magnitude * np.cos(-frequencies * 0.01),  # Phase lag
                'imag': pout_magnitude * np.sin(-frequencies * 0.01),
                'phase': -frequencies * 0.01
            }
        }
        
        # Create post-processor with synthetic data
        processor = AcousticPostProcessor()
        processor.frequencies = frequencies
        processor.probe_data = probe_data
        
        # Calculate transmission loss
        probe_separation = 6.0  # meters
        results = processor.calculate_transmission_loss(probe_separation=probe_separation)
        
        # Calculate phase velocity
        processor.calculate_phase_velocity(probe_separation=probe_separation)
        
        # Frequency band analysis
        band_results = processor.analyze_frequency_response()
        
        # Quality assessment
        quality = processor.quality_assessment()
        
        # Export results
        processor.export_results('synthetic_results.csv', format='csv')
        processor.export_results('synthetic_results.txt', format='txt')
        
        # Create plots
        processor.plot_results(save_plots=True, show_plots=False)
        
        print("Post-processing demonstration completed!")
        print("Generated files:")
        print("- synthetic_results.csv")
        print("- synthetic_results.txt")
        print("- transmission_loss_analysis.png")
        
        # Print some results
        print(f"\nResults summary:")
        print(f"  Frequency range: {frequencies[0]:.0f} - {frequencies[-1]:.0f} Hz")
        print(f"  TL range: {np.min(results['transmission_loss']):.2f} - {np.max(results['transmission_loss']):.2f} dB")
        print(f"  Quality score: {quality['quality_score']}/100")
        
        return True
        
    except Exception as e:
        print(f"Error in post-processing demonstration: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to run complete simulation workflow."""
    print("ABAQUS ACOUSTIC TRANSMISSION LOSS SIMULATION")
    print("=" * 60)
    print("Complete Workflow Demonstration")
    print("=" * 60)
    
    start_time = time.time()
    
    # Track results
    all_results = {}
    
    try:
        # 1. Run layered medium study
        print("\n1. LAYERED MEDIUM PARAMETRIC STUDY")
        layered_results = run_layered_medium_study()
        all_results['layered_study'] = layered_results
        
        # 2. Run graded medium study
        print("\n2. GRADED MEDIUM STUDY")
        graded_results = run_graded_medium_study()
        all_results['graded_study'] = graded_results
        
        # 3. Run convergence studies
        print("\n3. CONVERGENCE STUDIES")
        freq_conv_results = run_frequency_convergence_study()
        mesh_conv_results = run_mesh_convergence_study()
        all_results['frequency_convergence'] = freq_conv_results
        all_results['mesh_convergence'] = mesh_conv_results
        
        # 4. Create input file examples
        print("\n4. INPUT FILE GENERATION")
        input_success = create_input_file_examples()
        all_results['input_files'] = {'status': 'success' if input_success else 'failed'}
        
        # 5. Demonstrate post-processing
        print("\n5. POST-PROCESSING DEMONSTRATION")
        postproc_success = demonstrate_post_processing()
        all_results['post_processing'] = {'status': 'success' if postproc_success else 'failed'}
        
        # Final summary
        elapsed_time = time.time() - start_time
        
        print("\n" + "="*60)
        print("WORKFLOW COMPLETION SUMMARY")
        print("="*60)
        
        total_models = 0
        successful_models = 0
        
        for study_name, study_results in all_results.items():
            if isinstance(study_results, dict) and 'status' not in study_results:
                # It's a parametric study
                study_total = len(study_results)
                study_success = sum(1 for r in study_results.values() 
                                  if isinstance(r, dict) and r.get('status') == 'model_created')
                total_models += study_total
                successful_models += study_success
                
                print(f"\n{study_name.upper()}:")
                print(f"  Models created: {study_success}/{study_total}")
                
                for model_name, result in study_results.items():
                    status = result.get('status', 'unknown')
                    print(f"    {model_name}: {status}")
            else:
                # It's a single task
                status = study_results.get('status', 'unknown')
                print(f"\n{study_name.upper()}: {status}")
                
        print(f"\nOVERALL STATISTICS:")
        print(f"  Total models created: {successful_models}/{total_models}")
        print(f"  Success rate: {successful_models/total_models*100:.1f}%" if total_models > 0 else "  No models to create")
        print(f"  Total execution time: {elapsed_time:.1f} seconds")
        
        print(f"\nGENERATED FILES:")
        print(f"  - layered_medium_2d.inp")
        print(f"  - graded_medium_3d.inp")
        print(f"  - validation_case.inp")
        print(f"  - synthetic_results.csv")
        print(f"  - synthetic_results.txt")
        print(f"  - transmission_loss_analysis.png")
        
        print(f"\nTO RUN SIMULATIONS:")
        print(f"  1. Submit jobs in Abaqus/CAE or use:")
        print(f"     abaqus job=<job_name> input=<input_file>")
        print(f"  2. Post-process results:")
        print(f"     python post_processing_tools.py <job_name>.odb <probe_separation>")
        
        return all_results
        
    except Exception as e:
        print(f"\nERROR in main workflow: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("Starting complete Abaqus acoustic simulation workflow...")
    results = main()
    
    if results:
        print("\nWorkflow completed successfully!")
    else:
        print("\nWorkflow completed with errors.")
        sys.exit(1)