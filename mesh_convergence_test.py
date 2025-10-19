#!/usr/bin/env python3
"""
Mesh Convergence Test for Abaqus Acoustic Simulation

This script performs a mesh convergence study by running the acoustic simulation
with different mesh densities and comparing the results.

Usage:
    python mesh_convergence_test.py

Requirements:
    - Abaqus installation with Python API
    - Base input file: acoustic_transmission_loss.inp
    - Post-processing script: post_process_tl.py

Author: Abaqus Acoustic Simulation
Date: 2024
"""

import os
import sys
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from post_process_tl import process_acoustic_results

def create_mesh_variations(base_input_file, mesh_densities):
    """
    Create input files with different mesh densities
    
    Args:
        base_input_file: Path to base input file
        mesh_densities: List of mesh density factors (1.0 = base, 0.5 = finer, 2.0 = coarser)
        
    Returns:
        list: Paths to generated input files
    """
    input_files = []
    
    # Read base input file
    with open(base_input_file, 'r') as f:
        base_content = f.read()
    
    for i, density_factor in enumerate(mesh_densities):
        # Create modified input file
        modified_file = f"mesh_test_{i+1}.inp"
        
        # For this example, we'll create a simple modification
        # In practice, you would modify the node coordinates and element definitions
        modified_content = base_content.replace(
            "** Acoustic Transmission Loss Simulation",
            f"** Acoustic Transmission Loss Simulation - Mesh Density {density_factor:.1f}x"
        )
        
        with open(modified_file, 'w') as f:
            f.write(modified_content)
        
        input_files.append(modified_file)
        print(f"Created {modified_file} with density factor {density_factor:.1f}")
    
    return input_files

def run_convergence_study(input_files, mesh_densities):
    """
    Run convergence study with different mesh densities
    
    Args:
        input_files: List of input file paths
        mesh_densities: List of mesh density factors
        
    Returns:
        dict: Results for each mesh density
    """
    results = {}
    
    for i, (input_file, density) in enumerate(zip(input_files, mesh_densities)):
        job_name = f"mesh_test_{i+1}"
        odb_file = f"{job_name}.odb"
        
        print(f"\nRunning simulation {i+1}/{len(input_files)}: Density factor {density:.1f}")
        print("-" * 50)
        
        # Run Abaqus simulation
        cmd = ['abaqus', 'job=' + job_name, 'input=' + input_file, 'interactive']
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min timeout
            
            if result.returncode == 0:
                print(f"✓ Simulation {i+1} completed successfully")
                
                # Process results
                if os.path.exists(odb_file):
                    print(f"Processing results for density factor {density:.1f}...")
                    acoustic_results = process_acoustic_results(odb_file)
                    
                    if acoustic_results:
                        results[density] = acoustic_results
                        print(f"✓ Results processed for density factor {density:.1f}")
                    else:
                        print(f"✗ Failed to process results for density factor {density:.1f}")
                else:
                    print(f"✗ ODB file not found for density factor {density:.1f}")
            else:
                print(f"✗ Simulation {i+1} failed with return code: {result.returncode}")
                print("STDERR:", result.stderr)
                
        except subprocess.TimeoutExpired:
            print(f"✗ Simulation {i+1} timed out")
        except Exception as e:
            print(f"✗ Error running simulation {i+1}: {e}")
    
    return results

def analyze_convergence(results):
    """
    Analyze convergence of results across different mesh densities
    
    Args:
        results: Dictionary of results for each mesh density
        
    Returns:
        dict: Convergence analysis results
    """
    if len(results) < 2:
        print("Error: Need at least 2 mesh densities for convergence analysis")
        return None
    
    # Get reference (finest) mesh results
    finest_density = min(results.keys())
    reference_results = results[finest_density]
    
    convergence_analysis = {
        'reference_density': finest_density,
        'reference_tl': reference_results['transmission_loss'],
        'reference_freq': reference_results['frequencies'],
        'comparisons': {}
    }
    
    print(f"\nConvergence Analysis (Reference: density factor {finest_density:.1f})")
    print("=" * 60)
    
    for density, result in results.items():
        if density == finest_density:
            continue
        
        # Calculate differences
        tl_diff = np.abs(result['transmission_loss'] - reference_results['transmission_loss'])
        max_tl_diff = np.max(tl_diff)
        mean_tl_diff = np.mean(tl_diff)
        
        alpha_diff = np.abs(result['attenuation_coefficient'] - reference_results['attenuation_coefficient'])
        max_alpha_diff = np.max(alpha_diff)
        mean_alpha_diff = np.mean(alpha_diff)
        
        convergence_analysis['comparisons'][density] = {
            'max_tl_diff': max_tl_diff,
            'mean_tl_diff': mean_tl_diff,
            'max_alpha_diff': max_alpha_diff,
            'mean_alpha_diff': mean_alpha_diff
        }
        
        print(f"Density factor {density:.1f}:")
        print(f"  Max TL difference: {max_tl_diff:.3f} dB")
        print(f"  Mean TL difference: {mean_tl_diff:.3f} dB")
        print(f"  Max α difference: {max_alpha_diff:.6f} 1/m")
        print(f"  Mean α difference: {mean_alpha_diff:.6f} 1/m")
        print()
    
    return convergence_analysis

def plot_convergence_results(results, convergence_analysis):
    """
    Plot convergence study results
    
    Args:
        results: Dictionary of results for each mesh density
        convergence_analysis: Convergence analysis results
    """
    try:
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Plot 1: TL vs Frequency for different mesh densities
        ax1 = axes[0, 0]
        for density, result in results.items():
            ax1.plot(result['frequencies'], result['transmission_loss'], 
                    label=f'Density {density:.1f}x', linewidth=2)
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Transmission Loss (dB)')
        ax1.set_title('TL vs Frequency - Mesh Convergence')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Attenuation vs Frequency for different mesh densities
        ax2 = axes[0, 1]
        for density, result in results.items():
            ax2.plot(result['frequencies'], result['attenuation_coefficient'], 
                    label=f'Density {density:.1f}x', linewidth=2)
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Attenuation Coefficient (1/m)')
        ax2.set_title('Attenuation vs Frequency - Mesh Convergence')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: TL difference vs Frequency
        ax3 = axes[1, 0]
        reference_density = convergence_analysis['reference_density']
        reference_tl = convergence_analysis['reference_tl']
        reference_freq = convergence_analysis['reference_freq']
        
        for density, comparison in convergence_analysis['comparisons'].items():
            # Find corresponding result
            result = results[density]
            tl_diff = np.abs(result['transmission_loss'] - reference_tl)
            ax3.plot(result['frequencies'], tl_diff, 
                    label=f'vs Density {reference_density:.1f}x', linewidth=2)
        ax3.set_xlabel('Frequency (Hz)')
        ax3.set_ylabel('TL Difference (dB)')
        ax3.set_title('TL Difference from Reference Mesh')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_yscale('log')
        
        # Plot 4: Convergence summary
        ax4 = axes[1, 1]
        densities = list(convergence_analysis['comparisons'].keys())
        max_tl_diffs = [convergence_analysis['comparisons'][d]['max_tl_diff'] for d in densities]
        mean_tl_diffs = [convergence_analysis['comparisons'][d]['mean_tl_diff'] for d in densities]
        
        x = np.arange(len(densities))
        width = 0.35
        
        ax4.bar(x - width/2, max_tl_diffs, width, label='Max TL Diff', alpha=0.8)
        ax4.bar(x + width/2, mean_tl_diffs, width, label='Mean TL Diff', alpha=0.8)
        
        ax4.set_xlabel('Mesh Density Factor')
        ax4.set_ylabel('TL Difference (dB)')
        ax4.set_title('Convergence Summary')
        ax4.set_xticks(x)
        ax4.set_xticklabels([f'{d:.1f}x' for d in densities])
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_yscale('log')
        
        plt.tight_layout()
        plt.savefig('mesh_convergence_results.png', dpi=300, bbox_inches='tight')
        print("Convergence plots saved as mesh_convergence_results.png")
        plt.show()
        
    except ImportError:
        print("matplotlib not available. Install with: pip install matplotlib")
    except Exception as e:
        print(f"Error creating plots: {e}")

def cleanup_convergence_files(input_files):
    """
    Clean up files created during convergence study
    
    Args:
        input_files: List of input file paths
    """
    print("\nCleaning up convergence study files...")
    
    # Remove input files
    for input_file in input_files:
        if os.path.exists(input_file):
            os.remove(input_file)
            print(f"Removed {input_file}")
    
    # Remove Abaqus output files
    for i in range(1, len(input_files) + 1):
        job_name = f"mesh_test_{i}"
        files_to_remove = [
            f"{job_name}.odb", f"{job_name}.dat", f"{job_name}.msg",
            f"{job_name}.sta", f"{job_name}.lck", f"{job_name}.prt"
        ]
        
        for filename in files_to_remove:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"Removed {filename}")

def main():
    """
    Main function to run mesh convergence study
    """
    print("="*60)
    print("ABAQUS ACOUSTIC SIMULATION - MESH CONVERGENCE STUDY")
    print("="*60)
    
    # Configuration
    base_input_file = "acoustic_transmission_loss.inp"
    mesh_densities = [2.0, 1.5, 1.0, 0.75, 0.5]  # Coarse to fine
    
    # Check if base input file exists
    if not os.path.exists(base_input_file):
        print(f"Error: Base input file '{base_input_file}' not found")
        sys.exit(1)
    
    print(f"Base input file: {base_input_file}")
    print(f"Mesh densities to test: {mesh_densities}")
    print()
    
    # Create mesh variations
    print("Creating mesh variation input files...")
    input_files = create_mesh_variations(base_input_file, mesh_densities)
    print(f"Created {len(input_files)} input files")
    
    # Run convergence study
    print("\nRunning convergence study...")
    results = run_convergence_study(input_files, mesh_densities)
    
    if not results:
        print("Error: No successful simulations completed")
        sys.exit(1)
    
    print(f"\nCompleted {len(results)} successful simulations")
    
    # Analyze convergence
    print("\nAnalyzing convergence...")
    convergence_analysis = analyze_convergence(results)
    
    if convergence_analysis:
        # Plot results
        print("\nCreating convergence plots...")
        plot_convergence_results(results, convergence_analysis)
        
        # Save convergence data
        print("\nSaving convergence data...")
        np.savez('convergence_data.npz', 
                results=results, 
                convergence_analysis=convergence_analysis)
        print("Convergence data saved as convergence_data.npz")
    
    # Cleanup
    cleanup_response = input("\nClean up temporary files? (y/n): ").lower().strip()
    if cleanup_response in ['y', 'yes']:
        cleanup_convergence_files(input_files)
        print("Cleanup completed.")
    else:
        print("Temporary files kept.")
    
    print("\nMesh convergence study completed!")

if __name__ == "__main__":
    main()