"""
Parallel SOFC Simulation Script
==============================

This script implements parallel processing for the SOFC simulation
to achieve the target runtime of ~10 minutes per sample.
"""

import numpy as np
import pandas as pd
import time
from joblib import Parallel, delayed
from tqdm import tqdm
import os
import sys
from sofc_simulation import SOFCLowFidelityModel, SOFCDatasetGenerator
from config import *

def simulate_single_sample(sample_id: int, params: dict) -> dict:
    """
    Simulate a single sample (for parallel processing)
    
    Args:
        sample_id: Unique identifier for the sample
        params: Dictionary containing input parameters
        
    Returns:
        Dictionary containing simulation results
    """
    model = SOFCLowFidelityModel()
    
    # Simulate single point
    result = model.simulate_single_point(params)
    
    # Add input parameters to result
    result.update(params)
    result['sample_id'] = sample_id
    
    # Add V-I curve data
    i_range = np.linspace(VI_CURRENT_RANGE[0], VI_CURRENT_RANGE[1], VI_N_POINTS)
    voltages, currents = model.generate_vi_curve(params, i_range)
    result['vi_voltages'] = voltages.tolist()
    result['vi_currents'] = currents.tolist()
    
    return result

def generate_parameter_space_optimized(n_samples: int) -> pd.DataFrame:
    """
    Generate optimized parameter space for parametric sweep
    
    Args:
        n_samples: Number of samples to generate
        
    Returns:
        DataFrame containing parameter combinations
    """
    np.random.seed(42)  # For reproducibility
    
    params = {}
    
    for param_name, param_config in PARAMETER_RANGES.items():
        if param_config['distribution'] == 'normal':
            values = np.random.normal(
                param_config['mean'], 
                param_config['std'], 
                n_samples
            )
            values = np.clip(values, param_config['min'], param_config['max'])
        else:  # uniform
            values = np.random.uniform(
                param_config['min'], 
                param_config['max'], 
                n_samples
            )
        
        params[param_name] = values
    
    return pd.DataFrame(params)

def run_parallel_simulation(n_samples: int = N_SAMPLES, n_jobs: int = N_JOBS):
    """
    Run parallel simulation
    
    Args:
        n_samples: Number of samples to simulate
        n_jobs: Number of parallel jobs (-1 for all cores)
    """
    print("SOFC Parallel Simulation Dataset Generator")
    print("=" * 50)
    print(f"Target samples: {n_samples}")
    print(f"Parallel jobs: {n_jobs if n_jobs > 0 else 'all available cores'}")
    print(f"Expected runtime: ~{n_samples * 10 / 60:.1f} minutes")
    print()
    
    # Generate parameter space
    print("Generating parameter space...")
    start_time = time.time()
    params_df = generate_parameter_space_optimized(n_samples)
    param_gen_time = time.time() - start_time
    print(f"Parameter space generated in {param_gen_time:.2f} seconds")
    
    # Save parameter space
    params_df.to_csv(OUTPUT_FILES['parameters'], index=False)
    print(f"Parameter space saved to {OUTPUT_FILES['parameters']}")
    
    # Prepare data for parallel processing
    param_list = [row.to_dict() for _, row in params_df.iterrows()]
    sample_ids = list(range(n_samples))
    
    # Run parallel simulation
    print("Starting parallel simulations...")
    sim_start_time = time.time()
    
    # Use joblib for parallel processing
    results = Parallel(n_jobs=n_jobs, verbose=1)(
        delayed(simulate_single_sample)(sample_id, params)
        for sample_id, params in zip(sample_ids, param_list)
    )
    
    sim_end_time = time.time()
    total_sim_time = sim_end_time - sim_start_time
    avg_time_per_sample = total_sim_time / len(results)
    
    print(f"\nSimulation completed!")
    print(f"Total simulation time: {total_sim_time:.2f} seconds ({total_sim_time/60:.2f} minutes)")
    print(f"Average time per sample: {avg_time_per_sample:.2f} seconds")
    print(f"Speedup factor: {n_samples * 10 / (total_sim_time/60):.1f}x")
    
    return results

def save_results_optimized(results: list):
    """
    Save results in optimized format
    
    Args:
        results: List of simulation results
    """
    print("Saving results...")
    
    # Save HDF5 dataset
    import h5py
    with h5py.File(OUTPUT_FILES['hdf5'], 'w') as f:
        # Create groups
        inputs_group = f.create_group('inputs')
        outputs_group = f.create_group('outputs')
        vi_curves_group = f.create_group('vi_curves')
        
        # Input parameters
        input_params = list(PARAMETER_RANGES.keys())
        for param in input_params:
            inputs_group.create_dataset(param, data=[r[param] for r in results])
        
        # Output parameters
        output_params = ['voltage', 'power_density', 'efficiency', 'stack_temperature', 
                        'nernst_voltage', 'activation_overpotential', 'ohmic_overpotential', 
                        'concentration_overpotential', 'fuel_consumption_rate']
        for param in output_params:
            outputs_group.create_dataset(param, data=[r[param] for r in results])
        
        # V-I curves
        vi_curves_group.create_dataset('voltages', data=[r['vi_voltages'] for r in results])
        vi_curves_group.create_dataset('currents', data=[r['vi_currents'] for r in results])
        
        # Metadata
        f.attrs['n_samples'] = len(results)
        f.attrs['description'] = 'SOFC Low-Fidelity Simulation Dataset (Parallel)'
        f.attrs['model_type'] = '1D System-Level Lumped Electrochemical Model'
        f.attrs['created'] = time.strftime('%Y-%m-%d %H:%M:%S')
        f.attrs['parallel_jobs'] = N_JOBS
    
    print(f"HDF5 dataset saved to {OUTPUT_FILES['hdf5']}")
    
    # Save CSV dataset (flattened)
    flattened_results = []
    for result in results:
        flat_result = {k: v for k, v in result.items() if k not in ['vi_voltages', 'vi_currents']}
        flattened_results.append(flat_result)
    
    df = pd.DataFrame(flattened_results)
    df.to_csv(OUTPUT_FILES['csv'], index=False)
    print(f"CSV dataset saved to {OUTPUT_FILES['csv']} with {len(df)} samples")
    
    # Generate summary statistics
    print("\nDataset Summary:")
    print(f"Total samples: {len(results)}")
    print(f"Input parameters: {list(PARAMETER_RANGES.keys())}")
    print(f"Output parameters: {list(flattened_results[0].keys()) if flattened_results else 'None'}")
    
    # Generate summary statistics
    summary_stats = df.describe()
    summary_stats.to_csv('sofc_dataset_summary.csv')
    print("Summary statistics saved to sofc_dataset_summary.csv")

def create_visualization(results: list, n_samples: int = 100):
    """
    Create visualization plots
    
    Args:
        results: List of simulation results
        n_samples: Number of samples to include in plots
    """
    print("Creating visualizations...")
    
    import matplotlib.pyplot as plt
    
    # Sample results for plotting
    sample_results = results[:min(n_samples, len(results))]
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # V-I curves
    ax1 = axes[0, 0]
    for i, result in enumerate(sample_results[:20]):  # Plot first 20 curves
        ax1.plot(result['vi_currents'], result['vi_voltages'], alpha=0.7, linewidth=0.8)
    ax1.set_xlabel('Current Density (A/m²)')
    ax1.set_ylabel('Voltage (V)')
    ax1.set_title('V-I Curves (Sample)')
    ax1.grid(True, alpha=0.3)
    
    # Efficiency vs Temperature
    ax2 = axes[0, 1]
    temperatures = [r['temperature'] for r in sample_results]
    efficiencies = [r['efficiency'] for r in sample_results]
    scatter = ax2.scatter(temperatures, efficiencies, c=efficiencies, cmap='viridis', alpha=0.7)
    ax2.set_xlabel('Temperature (°C)')
    ax2.set_ylabel('Efficiency')
    ax2.set_title('Efficiency vs Temperature')
    ax2.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax2, label='Efficiency')
    
    # Power Density vs Current Density
    ax3 = axes[0, 2]
    current_densities = [r['current_density'] for r in sample_results]
    power_densities = [r['power_density'] for r in sample_results]
    ax3.scatter(current_densities, power_densities, alpha=0.7)
    ax3.set_xlabel('Current Density (A/m²)')
    ax3.set_ylabel('Power Density (W/m²)')
    ax3.set_title('Power Density vs Current Density')
    ax3.grid(True, alpha=0.3)
    
    # Stack Temperature vs Current Density
    ax4 = axes[1, 0]
    stack_temperatures = [r['stack_temperature'] for r in sample_results]
    ax4.scatter(current_densities, stack_temperatures, alpha=0.7)
    ax4.set_xlabel('Current Density (A/m²)')
    ax4.set_ylabel('Stack Temperature (°C)')
    ax4.set_title('Stack Temperature vs Current Density')
    ax4.grid(True, alpha=0.3)
    
    # Efficiency vs Fuel Utilization
    ax5 = axes[1, 1]
    fuel_utilizations = [r['fuel_utilization'] for r in sample_results]
    ax5.scatter(fuel_utilizations, efficiencies, alpha=0.7)
    ax5.set_xlabel('Fuel Utilization')
    ax5.set_ylabel('Efficiency')
    ax5.set_title('Efficiency vs Fuel Utilization')
    ax5.grid(True, alpha=0.3)
    
    # Anode Porosity vs Efficiency
    ax6 = axes[1, 2]
    anode_porosities = [r['anode_porosity'] for r in sample_results]
    ax6.scatter(anode_porosities, efficiencies, alpha=0.7)
    ax6.set_xlabel('Anode Porosity')
    ax6.set_ylabel('Efficiency')
    ax6.set_title('Anode Porosity vs Efficiency')
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_FILES['plots'], dpi=300, bbox_inches='tight')
    print(f"Visualization saved to {OUTPUT_FILES['plots']}")

def main():
    """
    Main function for parallel simulation
    """
    # Check if we should run a test first
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("Running test simulation with 100 samples...")
        results = run_parallel_simulation(n_samples=100, n_jobs=2)
        save_results_optimized(results)
        create_visualization(results, n_samples=100)
    else:
        print("Running full simulation with 10,200 samples...")
        results = run_parallel_simulation(n_samples=N_SAMPLES, n_jobs=N_JOBS)
        save_results_optimized(results)
        create_visualization(results, n_samples=1000)

if __name__ == "__main__":
    main()