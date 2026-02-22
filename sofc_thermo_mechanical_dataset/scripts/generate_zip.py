#!/usr/bin/env python3
"""
Package all CSV data files into a single ZIP archive for distribution.

DISCLAIMER: All data is SYNTHETIC/ILLUSTRATIVE, based on published literature ranges.

Output: sofc_data.zip containing all 15 CSV files with disclaimer
"""

import os
import zipfile
from datetime import datetime

def create_readme_for_zip():
    """Create a README.txt to include in the ZIP file."""
    readme_content = """SOFC Thermo-Mechanical Dataset Package
=======================================

IMPORTANT DISCLAIMER
--------------------
ALL DATA IN THIS PACKAGE IS SYNTHETIC/ILLUSTRATIVE AND FOR EDUCATIONAL PURPOSES ONLY

- All CSV files contain SYNTHETIC DATA generated based on published literature ranges
- This data is NOT experimental data from actual SOFC measurements
- DO NOT use this data as ground truth for research or engineering without independent verification
- The data demonstrates typical ranges and trends for SOFC thermo-mechanical investigations

Dataset Contents
----------------
This ZIP archive contains 15 CSV files with temperature-dependent properties, 
creep behavior, thermal cycling degradation, and FEM inputs for SOFC materials.

Files included:
01_thermal_properties.csv           - Temperature-dependent thermal properties
02_mechanical_properties.csv        - Elastic modulus, strength, toughness
03_creep_parameters_norton.csv      - Norton power-law creep parameters
04_creep_curves_NiYSZ.csv          - Simulated creep strain vs time
05_CTE_mismatch_thermal_stress.csv - CTE and interfacial thermal stress
06_polarization_curves.csv         - I-V and power density curves
07_thermal_cycling_degradation.csv - Performance over thermal cycles
08_strain_hardening_FEM_input.csv  - Time-hardening creep for FEM
09_temperature_distribution.csv    - 2D temperature field on cell
10_stress_evolution_thermal_cycle.csv - Stress during heating-dwell-cooling
11_cell_geometry.csv               - Layer dimensions
12_operating_conditions.csv        - Test matrix scenarios
13_residual_stress.csv             - Post-sintering residual stress
14_redox_cycling.csv               - Chemical expansion during redox
15_FEM_input_summary.csv          - Quick-reference property table

Materials Covered
-----------------
- 8YSZ (Electrolyte)
- GDC (Buffer layer)
- Ni-YSZ (Anode)
- LSCF (Cathode)
- LSM (Cathode)
- Crofer 22 APU (Interconnect)

Data Format
-----------
All CSV files include:
- Comment header lines (starting with #) stating synthetic nature
- Column headers with units
- Data in SI or explicitly stated units

For More Information
--------------------
See the full repository at: https://github.com/georgegershom22-oss/george
- Complete documentation in README.md
- Python visualization scripts in scripts/ directory
- Links to real open-access SOFC datasets in open_data_sources.md

Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """

Version: 1.0
"""
    return readme_content


def generate_zip():
    """Package all CSV files into a ZIP archive."""
    # Paths
    script_dir = os.path.dirname(__file__)
    data_dir = os.path.join(script_dir, '..', 'data')
    output_dir = os.path.join(script_dir, '..')
    zip_filename = os.path.join(output_dir, 'sofc_data.zip')
    
    # Get all CSV files
    csv_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.csv')])
    
    if not csv_files:
        print("❌ ERROR: No CSV files found in data/ directory")
        print("   Run generate_all_datasets.py first to create the dataset files")
        return
    
    # Create ZIP file
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add README
        readme_content = create_readme_for_zip()
        zipf.writestr('README.txt', readme_content)
        print("✓ Added README.txt to archive")
        
        # Add all CSV files
        for csv_file in csv_files:
            file_path = os.path.join(data_dir, csv_file)
            arcname = csv_file  # Store in root of ZIP
            zipf.write(file_path, arcname=arcname)
            print(f"✓ Added {csv_file}")
    
    # Get file size
    size_bytes = os.path.getsize(zip_filename)
    size_kb = size_bytes / 1024
    
    print()
    print("=" * 60)
    print(f"✓ Successfully created: {os.path.basename(zip_filename)}")
    print(f"  Location: {output_dir}")
    print(f"  Size: {size_kb:.1f} KB")
    print(f"  Files: {len(csv_files)} CSV files + README.txt")
    print("=" * 60)
    print()
    print("REMINDER: All data is SYNTHETIC/ILLUSTRATIVE")
    print("For real SOFC datasets, see open_data_sources.md")


if __name__ == '__main__':
    generate_zip()
