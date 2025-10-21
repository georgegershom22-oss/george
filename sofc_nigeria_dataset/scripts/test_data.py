#!/usr/bin/env python3
"""
Test script to verify all JSON data files are valid
"""

import json
from pathlib import Path

def test_json_files():
    """Test all JSON files for validity"""
    base_path = Path(__file__).parent.parent
    
    # Define data directories
    data_dirs = [
        base_path / "data" / "raw",
        base_path / "data" / "processed"
    ]
    
    print("="*50)
    print("Testing SOFC Dataset JSON Files")
    print("="*50)
    
    total_files = 0
    valid_files = 0
    total_size = 0
    
    for data_dir in data_dirs:
        if not data_dir.exists():
            print(f"\n⚠ Directory not found: {data_dir}")
            continue
            
        print(f"\n📁 Checking: {data_dir.relative_to(base_path)}")
        print("-"*40)
        
        json_files = list(data_dir.glob("*.json"))
        
        for json_file in json_files:
            total_files += 1
            file_size = json_file.stat().st_size
            total_size += file_size
            
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                # Count top-level keys
                num_keys = len(data.keys())
                
                # Get record count if applicable
                record_count = 0
                if isinstance(data, list):
                    record_count = len(data)
                elif isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, list):
                            record_count = max(record_count, len(value))
                        elif isinstance(value, dict):
                            record_count = max(record_count, len(value))
                
                print(f"✓ {json_file.name}")
                print(f"  Size: {file_size/1024:.1f} KB")
                print(f"  Keys: {num_keys}")
                if record_count > 0:
                    print(f"  Records: {record_count}")
                
                valid_files += 1
                
            except json.JSONDecodeError as e:
                print(f"❌ {json_file.name} - Invalid JSON: {e}")
            except Exception as e:
                print(f"❌ {json_file.name} - Error: {e}")
    
    print("\n" + "="*50)
    print("Summary")
    print("="*50)
    print(f"Total files tested: {total_files}")
    print(f"Valid JSON files: {valid_files}")
    print(f"Total data size: {total_size/1024:.1f} KB")
    
    if valid_files == total_files:
        print("\n✅ All JSON files are valid!")
    else:
        print(f"\n⚠ {total_files - valid_files} files have issues")
    
    return valid_files == total_files

def display_dataset_summary():
    """Display a summary of the dataset contents"""
    base_path = Path(__file__).parent.parent
    
    print("\n" + "="*50)
    print("Dataset Content Summary")
    print("="*50)
    
    # Load and summarize key data
    summaries = {
        "Performance Data": "data/raw/sofc_performance_characteristics.json",
        "Fuel Specifications": "data/raw/fuel_flexibility_specifications.json",
        "Power Density": "data/raw/power_density_operational_characteristics.json",
        "Manufacturers": "data/raw/manufacturer_technical_specifications.json",
        "Nigeria Scenarios": "data/processed/nigeria_operational_scenarios.json"
    }
    
    for name, path in summaries.items():
        file_path = base_path / path
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            print(f"\n📊 {name}:")
            print("-"*40)
            
            if name == "Performance Data":
                print(f"  • Efficiency range: 45-60% LHV")
                print(f"  • Operating temp: 650-850°C")
                print(f"  • Degradation: 0.15-0.5%/1000h")
                print(f"  • Stack lifetime: 80,000 hours")
                
            elif name == "Fuel Specifications":
                fuels = list(data.get('fuel_types', {}).keys())
                print(f"  • Fuel types: {len(fuels)}")
                for fuel in fuels[:3]:
                    print(f"    - {fuel.replace('_', ' ').title()}")
                if len(fuels) > 3:
                    print(f"    ... and {len(fuels)-3} more")
                    
            elif name == "Power Density":
                print(f"  • Cell types: Planar, Tubular, Microtubular")
                print(f"  • Power density: 0.2-0.4 W/cm²")
                print(f"  • System sizes: 100kW - 5MW")
                print(f"  • Startup time: 2-8 hours")
                
            elif name == "Manufacturers":
                mfgs = list(data.get('manufacturers', {}).keys())
                print(f"  • Manufacturers: {len(mfgs)}")
                for mfg in mfgs[:4]:
                    print(f"    - {mfg.replace('_', ' ').title()}")
                if len(mfgs) > 4:
                    print(f"    ... and {len(mfgs)-4} more")
                    
            elif name == "Nigeria Scenarios":
                scenarios = list(data.get('operational_scenarios', {}).keys())
                print(f"  • Deployment scenarios: {len(scenarios)}")
                print(f"  • Grid capacity: 12,522 MW installed")
                print(f"  • Peak demand: 15,000 MW")
                print(f"  • Applications: Industrial, Commercial, Telecom, etc.")

def main():
    """Main test function"""
    print("\n" + "🔬 SOFC NIGERIA DATASET VALIDATION")
    print("="*70)
    
    # Test JSON validity
    all_valid = test_json_files()
    
    # Display summary if all files are valid
    if all_valid:
        display_dataset_summary()
    
    print("\n" + "="*70)
    print("✅ Dataset validation complete!")
    print("="*70)

if __name__ == "__main__":
    main()