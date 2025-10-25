#!/usr/bin/env python3
"""
Complete Dataset Generation and Validation Pipeline
Executes the full workflow for generating and validating the real-time dataset.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
import json

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        
        elapsed = time.time() - start_time
        print(f"✅ {description} completed successfully in {elapsed:.1f}s")
        
        if result.stdout:
            print("Output:")
            print(result.stdout)
            
        return True
        
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"❌ {description} failed after {elapsed:.1f}s")
        print(f"Error: {e}")
        
        if e.stdout:
            print("Stdout:")
            print(e.stdout)
        if e.stderr:
            print("Stderr:")
            print(e.stderr)
            
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'numpy', 'pandas', 'matplotlib', 'seaborn', 'scipy', 
        'sklearn', 'cv2', 'h5py', 'plotly'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'sklearn':
                import sklearn
            else:
                __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install missing packages:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies satisfied!")
    return True

def check_disk_space():
    """Check available disk space"""
    print("💾 Checking disk space...")
    
    # Get current directory disk usage
    statvfs = os.statvfs('.')
    available_gb = (statvfs.f_bavail * statvfs.f_frsize) / (1024**3)
    
    required_gb = 100  # Estimated requirement
    
    print(f"  Available space: {available_gb:.1f} GB")
    print(f"  Required space: {required_gb} GB")
    
    if available_gb < required_gb:
        print(f"⚠️  Low disk space! Consider freeing up space.")
        response = input("Continue anyway? (y/n): ")
        return response.lower() == 'y'
    
    print("✅ Sufficient disk space available!")
    return True

def main():
    """Main execution pipeline"""
    print("🚀 Real-Time Dataset Generation Pipeline")
    print("=" * 60)
    
    # Pre-flight checks
    if not check_dependencies():
        sys.exit(1)
    
    if not check_disk_space():
        sys.exit(1)
    
    # Pipeline steps
    steps = [
        {
            'command': 'python generate_realtime_dataset.py',
            'description': 'Generate Real-Time Training Dataset',
            'critical': True
        },
        {
            'command': 'python data_validation_tools.py',
            'description': 'Validate and Visualize Dataset',
            'critical': False
        }
    ]
    
    # Track execution
    start_time = time.time()
    successful_steps = 0
    
    for i, step in enumerate(steps, 1):
        print(f"\n📋 Step {i}/{len(steps)}: {step['description']}")
        
        success = run_command(step['command'], step['description'])
        
        if success:
            successful_steps += 1
        elif step['critical']:
            print(f"\n❌ Critical step failed: {step['description']}")
            print("Pipeline execution stopped.")
            sys.exit(1)
        else:
            print(f"\n⚠️  Non-critical step failed: {step['description']}")
            print("Continuing with pipeline...")
    
    # Final summary
    total_time = time.time() - start_time
    
    print(f"\n{'='*60}")
    print("📊 PIPELINE EXECUTION SUMMARY")
    print(f"{'='*60}")
    print(f"Total execution time: {total_time/60:.1f} minutes")
    print(f"Successful steps: {successful_steps}/{len(steps)}")
    
    if successful_steps == len(steps):
        print("🎉 All steps completed successfully!")
        
        # Check if dataset was created
        dataset_path = Path("realtime_training_dataset")
        if dataset_path.exists():
            print(f"\n📁 Dataset created at: {dataset_path.absolute()}")
            
            # Show dataset size
            total_size = sum(f.stat().st_size for f in dataset_path.rglob('*') if f.is_file())
            size_gb = total_size / (1024**3)
            print(f"📏 Dataset size: {size_gb:.2f} GB")
            
            # Show key files
            print("\n📋 Key dataset files:")
            key_files = [
                "dic_data/dic_dataset.h5",
                "furnace_data/furnace_states.csv", 
                "rl_data/rl_tuples.pkl",
                "metadata/dataset_metadata.json",
                "validation_report.json"
            ]
            
            for file_path in key_files:
                full_path = dataset_path / file_path
                if full_path.exists():
                    file_size = full_path.stat().st_size / (1024**2)  # MB
                    print(f"  ✅ {file_path} ({file_size:.1f} MB)")
                else:
                    print(f"  ❌ {file_path} (missing)")
            
            # Load and show metadata
            metadata_path = dataset_path / "metadata" / "dataset_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                print(f"\n📈 Dataset Statistics:")
                dataset_info = metadata.get('dataset_info', {})
                print(f"  Duration: {dataset_info.get('duration_hours', 'N/A')} hours")
                print(f"  DIC frames: {dataset_info.get('total_dic_frames', 'N/A'):,}")
                print(f"  Furnace states: {dataset_info.get('total_furnace_states', 'N/A'):,}")
                print(f"  RL tuples: {dataset_info.get('total_rl_tuples', 'N/A'):,}")
            
            # Show next steps
            print(f"\n🎯 Next Steps:")
            print(f"  1. Explore the interactive dashboard:")
            print(f"     Open: {dataset_path}/visualizations/interactive_dashboard.html")
            print(f"  2. Review validation report:")
            print(f"     Check: {dataset_path}/validation_report.json")
            print(f"  3. Load data for ML training:")
            print(f"     See examples in README.md")
            
        else:
            print("❌ Dataset directory not found!")
            
    else:
        failed_steps = len(steps) - successful_steps
        print(f"⚠️  {failed_steps} step(s) failed")
        print("Check the error messages above for details.")
    
    print(f"\n🏁 Pipeline execution complete!")

if __name__ == "__main__":
    main()