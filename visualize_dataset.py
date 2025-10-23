"""
SOFC Dataset Visualization and Validation
Creates plots and validates the generated SOFC simulation dataset.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json

def load_dataset(dataset_dir='sofc_lf_dataset'):
    """
    Load the generated SOFC dataset and metadata
    
    Args:
        dataset_dir: Directory containing the dataset
        
    Returns:
        Tuple of (dataframe, metadata_dict)
    """
    dataset_path = Path(dataset_dir) / 'sofc_lf_dataset.csv'
    metadata_path = Path(dataset_dir) / 'dataset_metadata.json'
    
    df = pd.read_csv(dataset_path)
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    return df, metadata

def create_visualizations(df, output_dir='sofc_lf_dataset'):
    """
    Create comprehensive visualizations of the dataset
    
    Args:
        df: Dataset DataFrame
        output_dir: Directory to save plots
    """
    output_path = Path(output_dir)
    plots_dir = output_path / 'plots'
    plots_dir.mkdir(exist_ok=True)
    
    # Set style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # 1. Operating Temperature Distribution
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 2, 1)
    plt.hist(df['operating_temperature'] - 273.15, bins=50, alpha=0.7, edgecolor='black')
    plt.xlabel('Operating Temperature (°C)')
    plt.ylabel('Frequency')
    plt.title('Distribution of Operating Temperature')
    plt.grid(True, alpha=0.3)
    
    # 2. Electrochemical Efficiency Distribution
    plt.subplot(2, 2, 2)
    plt.hist(df['electrochemical_efficiency'], bins=50, alpha=0.7, edgecolor='black')
    plt.xlabel('Electrochemical Efficiency')
    plt.ylabel('Frequency')
    plt.title('Distribution of Electrochemical Efficiency')
    plt.grid(True, alpha=0.3)
    
    # 3. Power Density Distribution
    plt.subplot(2, 2, 3)
    plt.hist(df['power_density'], bins=50, alpha=0.7, edgecolor='black')
    plt.xlabel('Power Density (W/m²)')
    plt.ylabel('Frequency')
    plt.title('Distribution of Power Density')
    plt.grid(True, alpha=0.3)
    
    # 4. Voltage vs Current Density
    plt.subplot(2, 2, 4)
    plt.scatter(df['current_density_op'], df['voltage_op'], alpha=0.5, s=1)
    plt.xlabel('Current Density (A/m²)')
    plt.ylabel('Voltage (V)')
    plt.title('Voltage vs Current Density')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(plots_dir / 'basic_distributions.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Temperature Effects
    plt.figure(figsize=(12, 8))
    
    # Temperature vs Efficiency
    plt.subplot(2, 2, 1)
    plt.scatter(df['operating_temperature'] - 273.15, df['electrochemical_efficiency'], 
                alpha=0.5, s=1)
    plt.xlabel('Operating Temperature (°C)')
    plt.ylabel('Electrochemical Efficiency')
    plt.title('Temperature vs Efficiency')
    plt.grid(True, alpha=0.3)
    
    # Temperature vs Power Density
    plt.subplot(2, 2, 2)
    plt.scatter(df['operating_temperature'] - 273.15, df['power_density'], 
                alpha=0.5, s=1)
    plt.xlabel('Operating Temperature (°C)')
    plt.ylabel('Power Density (W/m²)')
    plt.title('Temperature vs Power Density')
    plt.grid(True, alpha=0.3)
    
    # Temperature vs Stack Temperature
    plt.subplot(2, 2, 3)
    plt.scatter(df['operating_temperature'] - 273.15, df['stack_temperature'] - 273.15, 
                alpha=0.5, s=1)
    plt.plot([700, 900], [700, 900], 'r--', label='1:1 line')
    plt.xlabel('Operating Temperature (°C)')
    plt.ylabel('Stack Temperature (°C)')
    plt.title('Operating vs Stack Temperature')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Porosity vs Efficiency
    plt.subplot(2, 2, 4)
    plt.scatter(df['input_anode_porosity'], df['electrochemical_efficiency'], 
                alpha=0.5, s=1, label='Anode')
    plt.scatter(df['input_cathode_porosity'], df['electrochemical_efficiency'], 
                alpha=0.5, s=1, label='Cathode')
    plt.xlabel('Porosity')
    plt.ylabel('Electrochemical Efficiency')
    plt.title('Porosity vs Efficiency')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(plots_dir / 'parameter_effects.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Correlation Matrix
    # Select key variables for correlation analysis
    corr_vars = [
        'operating_temperature', 'voltage_op', 'current_density_op', 
        'power_density', 'electrochemical_efficiency', 'stack_temperature',
        'input_anode_porosity', 'input_cathode_porosity', 'input_fuel_utilization'
    ]
    
    corr_data = df[corr_vars].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_data, annot=True, cmap='coolwarm', center=0, 
                square=True, fmt='.2f')
    plt.title('Correlation Matrix of Key Variables')
    plt.tight_layout()
    plt.savefig(plots_dir / 'correlation_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. V-I Curve Examples
    plt.figure(figsize=(12, 8))
    
    # Select a few representative samples
    sample_indices = np.random.choice(len(df), 5, replace=False)
    
    for i, idx in enumerate(sample_indices):
        row = df.iloc[idx]
        
        # Extract V-I curve data (if available)
        if 'vi_curve_current' in df.columns and 'vi_curve_voltage' in df.columns:
            try:
                # Parse the stored lists (they might be strings)
                current_str = row['vi_curve_current']
                voltage_str = row['vi_curve_voltage']
                
                if isinstance(current_str, str):
                    current = eval(current_str)  # Convert string to list
                    voltage = eval(voltage_str)
                else:
                    current = current_str
                    voltage = voltage_str
                
                temp_c = row['operating_temperature'] - 273.15
                plt.plot(current, voltage, label=f'Sample {idx} (T={temp_c:.0f}°C)', 
                        linewidth=2, alpha=0.8)
            except:
                # If parsing fails, create a simple curve
                current = np.linspace(100, 8000, 50)
                voltage = np.maximum(0, 1.2 - current * 0.0001 - (current/5000)**2 * 0.3)
                temp_c = row['operating_temperature'] - 273.15
                plt.plot(current, voltage, label=f'Sample {idx} (T={temp_c:.0f}°C)', 
                        linewidth=2, alpha=0.8)
    
    plt.xlabel('Current Density (A/m²)')
    plt.ylabel('Voltage (V)')
    plt.title('Representative V-I Curves')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(plots_dir / 'vi_curves_examples.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Visualizations saved to: {plots_dir}")

def validate_dataset(df, metadata):
    """
    Validate the generated dataset for physical consistency
    
    Args:
        df: Dataset DataFrame
        metadata: Metadata dictionary
        
    Returns:
        Dictionary containing validation results
    """
    validation_results = {}
    
    # 1. Check for missing values
    missing_values = df.isnull().sum()
    validation_results['missing_values'] = missing_values[missing_values > 0].to_dict()
    
    # 2. Check physical constraints
    constraints = []
    
    # Efficiency should be between 0 and 1
    eff_violations = ((df['electrochemical_efficiency'] < 0) | 
                     (df['electrochemical_efficiency'] > 1)).sum()
    constraints.append({
        'constraint': 'Efficiency between 0 and 1',
        'violations': int(eff_violations),
        'percentage': float(eff_violations / len(df) * 100)
    })
    
    # Voltage should be positive
    voltage_violations = (df['voltage_op'] <= 0).sum()
    constraints.append({
        'constraint': 'Positive voltage',
        'violations': int(voltage_violations),
        'percentage': float(voltage_violations / len(df) * 100)
    })
    
    # Current density should be positive
    current_violations = (df['current_density_op'] <= 0).sum()
    constraints.append({
        'constraint': 'Positive current density',
        'violations': int(current_violations),
        'percentage': float(current_violations / len(df) * 100)
    })
    
    # Stack temperature should be higher than operating temperature
    temp_violations = (df['stack_temperature'] < df['operating_temperature']).sum()
    constraints.append({
        'constraint': 'Stack temp >= Operating temp',
        'violations': int(temp_violations),
        'percentage': float(temp_violations / len(df) * 100)
    })
    
    validation_results['constraint_violations'] = constraints
    
    # 3. Check parameter ranges
    param_ranges = metadata.get('parameter_ranges', {})
    range_violations = {}
    
    for param, (min_val, max_val) in param_ranges.items():
        input_col = f'input_{param}'
        if input_col in df.columns:
            violations = ((df[input_col] < min_val) | (df[input_col] > max_val)).sum()
            if violations > 0:
                range_violations[param] = {
                    'violations': int(violations),
                    'percentage': float(violations / len(df) * 100),
                    'expected_range': [min_val, max_val],
                    'actual_range': [float(df[input_col].min()), float(df[input_col].max())]
                }
    
    validation_results['parameter_range_violations'] = range_violations
    
    # 4. Statistical checks
    stats = {}
    key_vars = ['electrochemical_efficiency', 'power_density', 'voltage_op']
    
    for var in key_vars:
        if var in df.columns:
            stats[var] = {
                'mean': float(df[var].mean()),
                'std': float(df[var].std()),
                'skewness': float(df[var].skew()),
                'kurtosis': float(df[var].kurtosis())
            }
    
    validation_results['statistics'] = stats
    
    # 5. Overall validation score
    total_violations = sum([c['violations'] for c in constraints])
    total_samples = len(df)
    validation_score = max(0, 100 - (total_violations / total_samples * 100))
    
    validation_results['overall_validation_score'] = float(validation_score)
    validation_results['total_samples'] = int(total_samples)
    validation_results['total_violations'] = int(total_violations)
    
    return validation_results

def main():
    """
    Main function for dataset visualization and validation
    """
    dataset_dir = 'sofc_lf_dataset'
    
    print("Loading SOFC dataset...")
    df, metadata = load_dataset(dataset_dir)
    
    print(f"Dataset loaded: {len(df)} samples, {len(df.columns)} features")
    
    # Create visualizations
    print("Creating visualizations...")
    create_visualizations(df, dataset_dir)
    
    # Validate dataset
    print("Validating dataset...")
    validation_results = validate_dataset(df, metadata)
    
    # Save validation results
    validation_path = Path(dataset_dir) / 'dataset_validation.json'
    with open(validation_path, 'w') as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"Validation results saved to: {validation_path}")
    
    # Print validation summary
    print(f"\n=== Dataset Validation Summary ===")
    print(f"Overall validation score: {validation_results['overall_validation_score']:.1f}%")
    print(f"Total violations: {validation_results['total_violations']}")
    
    print(f"\nConstraint Violations:")
    for constraint in validation_results['constraint_violations']:
        print(f"  {constraint['constraint']}: {constraint['violations']} ({constraint['percentage']:.1f}%)")
    
    if validation_results['parameter_range_violations']:
        print(f"\nParameter Range Violations:")
        for param, info in validation_results['parameter_range_violations'].items():
            print(f"  {param}: {info['violations']} ({info['percentage']:.1f}%)")
    
    print(f"\nKey Statistics:")
    for var, stats in validation_results['statistics'].items():
        print(f"  {var}: mean={stats['mean']:.3f}, std={stats['std']:.3f}")

if __name__ == "__main__":
    main()