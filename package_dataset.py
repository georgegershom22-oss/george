#!/usr/bin/env python3
"""
Dataset Packaging Script
========================

This script packages the complete welding dataset for distribution.
Creates compressed archives and generates final documentation.

Author: AI Assistant
Date: 2025-10-27
"""

import os
import shutil
import tarfile
import zipfile
from datetime import datetime
import json

def create_dataset_package():
    """Create a complete dataset package for distribution."""
    
    print("=" * 80)
    print("WELDING DATASET PACKAGING")
    print("=" * 80)
    
    # Define package contents
    package_files = [
        'welding_dataset/',
        'welding_dataset_generator.py',
        'analysis_tools.py',
        'dataset_documentation.md',
        'example_usage.ipynb',
        'requirements.txt',
        'README.md'
    ]
    
    # Create package directory
    package_dir = 'welding_dataset_complete'
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # Copy files to package directory
    print("Copying files to package directory...")
    for file_path in package_files:
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                dest_path = os.path.join(package_dir, os.path.basename(file_path))
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(file_path, dest_path)
            else:
                shutil.copy2(file_path, package_dir)
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (not found)")
    
    # Generate package manifest
    manifest = {
        'package_name': 'Comprehensive Welding Dataset for ML-Driven Inverse Design',
        'version': '1.0.0',
        'creation_date': datetime.now().isoformat(),
        'total_samples': 10000,
        'total_features': 61,
        'files': {
            'data': [
                'welding_dataset/input_parameters.csv',
                'welding_dataset/characterization_metrics.csv', 
                'welding_dataset/performance_metrics.csv',
                'welding_dataset/complete_dataset.csv'
            ],
            'metadata': [
                'welding_dataset/metadata.json'
            ],
            'analysis': [
                'welding_dataset/correlation_matrix.png',
                'welding_dataset/feature_importance_*.png',
                'welding_dataset/parameter_distributions.png',
                'welding_dataset/performance_distributions.png',
                'welding_dataset/material_performance.png',
                'welding_dataset/technique_performance.png',
                'welding_dataset/pca_analysis.png',
                'welding_dataset/cluster_analysis.png',
                'welding_dataset/interactive_dashboard.html'
            ],
            'code': [
                'welding_dataset_generator.py',
                'analysis_tools.py'
            ],
            'documentation': [
                'README.md',
                'dataset_documentation.md',
                'example_usage.ipynb',
                'requirements.txt'
            ]
        },
        'description': 'Complete package for ML-driven inverse design of welding parameters',
        'applications': [
            'Inverse design optimization',
            'Process parameter prediction',
            'Material selection guidance',
            'Quality prediction modeling',
            'Multi-objective optimization'
        ],
        'license': 'MIT',
        'citation': {
            'title': 'Comprehensive Welding Dataset for ML-Driven Inverse Design',
            'author': 'AI Assistant',
            'year': 2025,
            'version': '1.0.0'
        }
    }
    
    # Save manifest
    with open(os.path.join(package_dir, 'MANIFEST.json'), 'w') as f:
        json.dump(manifest, f, indent=2)
    print("  ✓ MANIFEST.json")
    
    # Create installation instructions
    install_instructions = """# Installation Instructions

## Quick Start

1. Extract the dataset package
2. Install dependencies: `pip install -r requirements.txt`
3. Load the dataset: `python3 -c "import pandas as pd; data = pd.read_csv('welding_dataset/complete_dataset.csv'); print(data.shape)"`
4. Run analysis: `python3 analysis_tools.py`
5. Explore examples: Open `example_usage.ipynb` in Jupyter

## Files Overview

- `welding_dataset/`: Main dataset files (CSV format)
- `welding_dataset_generator.py`: Dataset generation script
- `analysis_tools.py`: Comprehensive analysis tools
- `example_usage.ipynb`: Interactive examples and tutorials
- `README.md`: Complete documentation
- `requirements.txt`: Python dependencies

## Dataset Structure

- **Input Parameters** (19 features): Process parameters you can control
- **Characterization Metrics** (21 features): Immediate weld quality measurements  
- **Performance Metrics** (22 features): Long-term cycling performance data

Total: 10,000 samples × 61 features

## Support

For questions or issues, refer to the documentation files or the example notebook.
"""
    
    with open(os.path.join(package_dir, 'INSTALL.md'), 'w') as f:
        f.write(install_instructions)
    print("  ✓ INSTALL.md")
    
    # Create compressed archives
    print("\nCreating compressed archives...")
    
    # Create ZIP archive
    zip_filename = f'{package_dir}.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, '.')
                zipf.write(file_path, arc_path)
    
    zip_size = os.path.getsize(zip_filename) / (1024 * 1024)  # MB
    print(f"  ✓ {zip_filename} ({zip_size:.1f} MB)")
    
    # Create TAR.GZ archive
    tar_filename = f'{package_dir}.tar.gz'
    with tarfile.open(tar_filename, 'w:gz') as tarf:
        tarf.add(package_dir, arcname=package_dir)
    
    tar_size = os.path.getsize(tar_filename) / (1024 * 1024)  # MB
    print(f"  ✓ {tar_filename} ({tar_size:.1f} MB)")
    
    # Generate final summary
    print("\n" + "=" * 80)
    print("PACKAGING COMPLETE!")
    print("=" * 80)
    print(f"Package Directory: {package_dir}/")
    print(f"ZIP Archive: {zip_filename} ({zip_size:.1f} MB)")
    print(f"TAR.GZ Archive: {tar_filename} ({tar_size:.1f} MB)")
    print(f"\nDataset Summary:")
    print(f"  - Total Samples: {manifest['total_samples']:,}")
    print(f"  - Total Features: {manifest['total_features']}")
    print(f"  - Data Files: {len(manifest['files']['data'])}")
    print(f"  - Analysis Files: {len(manifest['files']['analysis'])}")
    print(f"  - Documentation Files: {len(manifest['files']['documentation'])}")
    
    print(f"\nReady for download and distribution! 🚀")
    
    return package_dir, zip_filename, tar_filename

if __name__ == "__main__":
    create_dataset_package()