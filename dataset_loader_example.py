"""
Example script for loading and visualizing the SOFC dataset
"""

import h5py
import numpy as np
import json

def load_dataset_info(dataset_dir='sofc_dataset'):
    """Load and display dataset information."""
    
    print("=" * 70)
    print("SOFC Dataset Information")
    print("=" * 70)
    
    # Load metadata
    with open(f'{dataset_dir}/metadata.json', 'r') as f:
        metadata = json.load(f)
    
    print("\n📊 Dataset Metadata:")
    print(f"  • Number of samples: {metadata['n_samples']}")
    print(f"  • Grid size: {metadata['grid_size']}")
    print(f"  • Generation date: {metadata['generation_date']}")
    print(f"  • Number of parameters: {len(metadata['param_names'])}")
    
    print("\n🔬 Physics Models:")
    for model in metadata['physics_models']:
        print(f"  • {model}")
    
    # Load summary statistics
    with open(f'{dataset_dir}/dataset_summary.json', 'r') as f:
        summary = json.load(f)
    
    print("\n📈 Dataset Statistics:")
    print(f"  • Total data points: {summary['dataset_info']['total_data_points']:,}")
    print(f"  • Points per sample: {summary['dataset_info']['total_data_points_per_sample']:,}")
    
    print("\n🎯 Input Parameter Ranges:")
    for param, stats in summary['input_parameters'].items():
        print(f"  • {param:30s}: [{stats['min']:.2e}, {stats['max']:.2e}] "
              f"(μ={stats['mean']:.2e}, σ={stats['std']:.2e})")
    
    print("\n📉 Output Field Statistics:")
    for field, stats in summary['output_fields'].items():
        print(f"  • {field:25s}: [{stats['min']:.2e}, {stats['max']:.2e}] "
              f"(μ={stats['mean']:.2e}, σ={stats['std']:.2e})")
    
    print("\n" + "=" * 70)


def load_sample(dataset_dir='sofc_dataset', sample_idx=0):
    """
    Load a specific sample from the dataset.
    
    Args:
        dataset_dir: Path to dataset directory
        sample_idx: Index of sample to load
        
    Returns:
        Dictionary containing input parameters and output fields
    """
    with h5py.File(f'{dataset_dir}/sofc_dataset.h5', 'r') as f:
        # Load input parameters
        params = f['inputs/parameters'][sample_idx]
        param_names = [name.decode() for name in f['inputs/parameter_names'][:]]
        
        # Load output fields
        current_density = f['outputs/current_density'][sample_idx]
        overpotential = f['outputs/overpotential'][sample_idx]
        temperature = f['outputs/temperature'][sample_idx]
        stress = f['outputs/von_mises_stress'][sample_idx]
        strain = f['outputs/strain'][sample_idx]
        displacement = f['outputs/displacement'][sample_idx]
        H2 = f['outputs/H2_concentration'][sample_idx]
        H2O = f['outputs/H2O_concentration'][sample_idx]
        
        # Load mesh
        x = f['mesh/x'][:]
        y = f['mesh/y'][:]
        z = f['mesh/z'][:]
    
    # Create parameter dictionary
    param_dict = {name: params[i] for i, name in enumerate(param_names)}
    
    sample = {
        'parameters': param_dict,
        'outputs': {
            'current_density': current_density,
            'overpotential': overpotential,
            'temperature': temperature,
            'von_mises_stress': stress,
            'strain': strain,
            'displacement': displacement,
            'H2_concentration': H2,
            'H2O_concentration': H2O,
        },
        'mesh': {
            'x': x,
            'y': y,
            'z': z,
        }
    }
    
    return sample


def demonstrate_data_access():
    """Demonstrate how to access and use the dataset."""
    
    print("\n🔍 Loading Dataset Example...")
    
    # Load first sample
    sample = load_sample(sample_idx=0)
    
    print("\n✓ Sample loaded successfully!")
    print(f"\n📋 Input Parameters (Sample 0):")
    for param, value in list(sample['parameters'].items())[:5]:
        print(f"  • {param:30s}: {value:.4e}")
    print("  ...")
    
    print(f"\n📊 Output Field Shapes:")
    for field_name, field_data in sample['outputs'].items():
        print(f"  • {field_name:25s}: {field_data.shape}")
    
    # Show some statistics
    temp = sample['outputs']['temperature']
    stress = sample['outputs']['von_mises_stress']
    
    print(f"\n🌡️  Temperature Field:")
    print(f"  • Min: {np.min(temp):.2f} K")
    print(f"  • Max: {np.max(temp):.2f} K")
    print(f"  • Mean: {np.mean(temp):.2f} K")
    
    print(f"\n⚡ Von Mises Stress Field:")
    print(f"  • Min: {np.min(stress):.2e} Pa")
    print(f"  • Max: {np.max(stress):.2e} Pa")
    print(f"  • Mean: {np.mean(stress):.2e} Pa")
    
    print("\n✅ Data access demonstration complete!")


if __name__ == "__main__":
    # Load and display dataset information
    load_dataset_info()
    
    # Demonstrate data access
    demonstrate_data_access()
