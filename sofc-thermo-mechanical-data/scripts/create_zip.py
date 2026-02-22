#!/usr/bin/env python3
"""
Create ZIP archive of all CSV data files.
Generates: sofc_phd_datasets.zip in project root
"""

import zipfile
from pathlib import Path

# Define paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_ZIP = SCRIPT_DIR.parent / "sofc_phd_datasets.zip"

def create_zip():
    """Package all CSV files into a ZIP archive."""
    # Get all CSV files
    csv_files = sorted(DATA_DIR.glob("*.csv"))
    
    if not csv_files:
        print("❌ No CSV files found in data directory")
        return
    
    print(f"\nCreating ZIP archive: {OUTPUT_ZIP.name}")
    print("="*70)
    
    # Create ZIP file
    with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for csv_file in csv_files:
            # Add file to ZIP with relative path
            arcname = f"sofc_data/{csv_file.name}"
            zipf.write(csv_file, arcname=arcname)
            print(f"  ✓ Added {csv_file.name}")
    
    # Get ZIP file size
    size_mb = OUTPUT_ZIP.stat().st_size / (1024 * 1024)
    
    print("="*70)
    print(f"✓ Created {OUTPUT_ZIP.name} ({size_mb:.2f} MB)")
    print(f"  Contains {len(csv_files)} CSV files")
    print(f"  Location: {OUTPUT_ZIP.absolute()}")
    print()


if __name__ == "__main__":
    create_zip()
