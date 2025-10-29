"""
Visualization script for SOFC dataset
Generates sample visualizations of the 3D field data
"""

import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib import cm
import os

def visualize_sample(dataset_dir='sofc_dataset', sample_idx=0, output_dir='visualizations'):
    """
    Create visualizations for a specific sample.
    
    Args:
        dataset_dir: Path to dataset directory
        sample_idx: Index of sample to visualize
        output_dir: Directory to save visualization images
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Loading sample {sample_idx}...")
    
    with h5py.File(f'{dataset_dir}/sofc_dataset.h5', 'r') as f:
        # Load data
        params = f['inputs/parameters'][sample_idx]
        param_names = [name.decode() for name in f['inputs/parameter_names'][:]]
        
        current_density = f['outputs/current_density'][sample_idx]
        temperature = f['outputs/temperature'][sample_idx]
        stress = f['outputs/von_mises_stress'][sample_idx]
        H2 = f['outputs/H2_concentration'][sample_idx]
        
        x = f['mesh/x'][:]
        y = f['mesh/y'][:]
        z = f['mesh/z'][:]
    
    # Create parameter dictionary
    param_dict = {name: params[i] for i, name in enumerate(param_names)}
    
    print(f"Creating visualizations...")
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    
    # Select middle slice (z-direction, mid-plane)
    z_mid = len(z) // 2
    
    # 1. Current Density Distribution
    ax1 = fig.add_subplot(2, 3, 1)
    im1 = ax1.contourf(x*1000, y*1000, current_density[:, :, z_mid], 
                       levels=20, cmap='viridis')
    ax1.set_xlabel('x [mm]')
    ax1.set_ylabel('y [mm]')
    ax1.set_title('Current Density [A/m²]')
    plt.colorbar(im1, ax=ax1)
    
    # 2. Temperature Distribution
    ax2 = fig.add_subplot(2, 3, 2)
    im2 = ax2.contourf(x*1000, y*1000, temperature[:, :, z_mid], 
                       levels=20, cmap='hot')
    ax2.set_xlabel('x [mm]')
    ax2.set_ylabel('y [mm]')
    ax2.set_title('Temperature [K]')
    plt.colorbar(im2, ax=ax2)
    
    # 3. Von Mises Stress Distribution
    ax3 = fig.add_subplot(2, 3, 3)
    im3 = ax3.contourf(x*1000, y*1000, stress[:, :, z_mid]/1e6, 
                       levels=20, cmap='coolwarm')
    ax3.set_xlabel('x [mm]')
    ax3.set_ylabel('y [mm]')
    ax3.set_title('Von Mises Stress [MPa]')
    plt.colorbar(im3, ax=ax3)
    
    # 4. H2 Concentration Distribution
    ax4 = fig.add_subplot(2, 3, 4)
    im4 = ax4.contourf(x*1000, y*1000, H2[:, :, z_mid], 
                       levels=20, cmap='Blues')
    ax4.set_xlabel('x [mm]')
    ax4.set_ylabel('y [mm]')
    ax4.set_title('H₂ Concentration [mol/m³]')
    plt.colorbar(im4, ax=ax4)
    
    # 5. Temperature Profile Through-Thickness (x-z slice at mid-y)
    y_mid = len(y) // 2
    ax5 = fig.add_subplot(2, 3, 5)
    im5 = ax5.contourf(x*1000, z*1000, temperature[:, y_mid, :].T, 
                       levels=20, cmap='hot')
    ax5.set_xlabel('x [mm]')
    ax5.set_ylabel('z [mm]')
    ax5.set_title('Temperature Through-Thickness [K]')
    plt.colorbar(im5, ax=ax5)
    
    # Add layer boundaries
    ax5.axhline(y=1.5, color='white', linestyle='--', linewidth=1, alpha=0.5)
    ax5.axhline(y=1.8, color='white', linestyle='--', linewidth=1, alpha=0.5)
    ax5.text(5, 0.75, 'Anode', color='white', fontsize=8)
    ax5.text(5, 1.65, 'Elec', color='white', fontsize=8)
    ax5.text(5, 2.4, 'Cathode', color='white', fontsize=8)
    
    # 6. Stress Profile Through-Thickness
    ax6 = fig.add_subplot(2, 3, 6)
    im6 = ax6.contourf(x*1000, z*1000, stress[:, y_mid, :].T/1e6, 
                       levels=20, cmap='coolwarm')
    ax6.set_xlabel('x [mm]')
    ax6.set_ylabel('z [mm]')
    ax6.set_title('Von Mises Stress Through-Thickness [MPa]')
    plt.colorbar(im6, ax=ax6)
    
    # Add layer boundaries
    ax6.axhline(y=1.5, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax6.axhline(y=1.8, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    # Add title with key parameters
    fig.suptitle(f'SOFC Simulation Sample {sample_idx}\n'
                 f'V={param_dict["voltage"]:.2f}V, '
                 f'i={param_dict["current_density"]:.0f} A/m², '
                 f'T_fuel={param_dict["fuel_inlet_temp"]:.0f}K',
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    # Save figure
    output_file = f'{output_dir}/sample_{sample_idx:03d}_visualization.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Visualization saved to: {output_file}")
    
    return output_file


def create_parameter_distribution_plots(dataset_dir='sofc_dataset', output_dir='visualizations'):
    """
    Create plots showing the distribution of input parameters across all samples.
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("Creating parameter distribution plots...")
    
    with h5py.File(f'{dataset_dir}/sofc_dataset.h5', 'r') as f:
        params = f['inputs/parameters'][:]
        param_names = [name.decode() for name in f['inputs/parameter_names'][:]]
    
    # Select key parameters to plot
    key_params = ['voltage', 'current_density', 'fuel_inlet_temp', 
                  'youngs_modulus_anode', 'youngs_modulus_electrolyte',
                  'cte_anode', 'cte_electrolyte', 'cte_cathode']
    
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()
    
    for i, param_name in enumerate(key_params):
        if param_name in param_names:
            idx = param_names.index(param_name)
            data = params[:, idx]
            
            axes[i].hist(data, bins=20, edgecolor='black', alpha=0.7)
            axes[i].set_xlabel(param_name.replace('_', ' ').title())
            axes[i].set_ylabel('Frequency')
            axes[i].grid(True, alpha=0.3)
    
    fig.suptitle('Input Parameter Distributions (Latin Hypercube Sampling)', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_file = f'{output_dir}/parameter_distributions.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Parameter distributions saved to: {output_file}")


if __name__ == "__main__":
    print("=" * 70)
    print("SOFC Dataset Visualization")
    print("=" * 70)
    
    # Create output directory
    output_dir = 'visualizations'
    
    # Visualize first 3 samples
    for i in range(min(3, 100)):
        visualize_sample(sample_idx=i, output_dir=output_dir)
    
    # Create parameter distribution plots
    create_parameter_distribution_plots(output_dir=output_dir)
    
    print("\n" + "=" * 70)
    print("Visualization complete!")
    print(f"Plots saved to: {output_dir}/")
    print("=" * 70)
