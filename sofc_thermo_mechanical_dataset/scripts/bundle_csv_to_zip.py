#!/usr/bin/env python3
"""
Bundle all CSV files into a ZIP archive
"""

import os
import zipfile
from pathlib import Path
from datetime import datetime

# Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_FILE = Path(__file__).parent.parent / "sofc_thermo_mechanical_data.zip"


def bundle_csvs():
    """Walk through data directory and bundle all CSV files into ZIP"""
    
    csv_files = []
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith('.csv'):
                filepath = Path(root) / file
                # Store relative path from data directory
                rel_path = filepath.relative_to(DATA_DIR.parent)
                csv_files.append((filepath, rel_path))
    
    # Create ZIP file
    print("=" * 70)
    print("Bundling CSV files into ZIP archive")
    print("=" * 70)
    print(f"\nOutput: {OUTPUT_FILE}")
    print(f"Found {len(csv_files)} CSV files\n")
    
    with zipfile.ZipFile(OUTPUT_FILE, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filepath, arcname in sorted(csv_files):
            zipf.write(filepath, arcname)
            print(f"  Added: {arcname}")
    
    # Get file size
    size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    
    print("\n" + "=" * 70)
    print(f"Successfully created: {OUTPUT_FILE.name}")
    print(f"Total size: {size_mb:.2f} MB")
    print(f"Total files: {len(csv_files)}")
    print(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Print summary by category
    print("\nFiles by category:")
    categories = {}
    for _, arcname in csv_files:
        category = arcname.parts[1]  # data/XX_category/file.csv
        categories[category] = categories.get(category, 0) + 1
    
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count} files")
    
    return len(csv_files)


if __name__ == "__main__":
    try:
        num_files = bundle_csvs()
        print(f"\n✓ Success! Bundled {num_files} CSV files")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise
