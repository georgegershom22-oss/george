#!/usr/bin/env python3
"""
Abaqus Acoustic Simulation Runner Script

This script automates the execution of the acoustic transmission loss simulation
and post-processing in Abaqus.

Usage:
    python run_simulation.py

Requirements:
    - Abaqus installation with Python API
    - Input file: acoustic_transmission_loss.inp
    - Post-processing script: post_process_tl.py

Author: Abaqus Acoustic Simulation
Date: 2024
"""

import os
import sys
import subprocess
import time

def run_abaqus_job(input_file, job_name=None):
    """
    Run Abaqus job from input file
    
    Args:
        input_file: Path to Abaqus input file
        job_name: Name for the job (defaults to input file name without extension)
        
    Returns:
        bool: True if job completed successfully, False otherwise
    """
    if job_name is None:
        job_name = os.path.splitext(os.path.basename(input_file))[0]
    
    print(f"Starting Abaqus job: {job_name}")
    print(f"Input file: {input_file}")
    
    # Abaqus command
    cmd = ['abaqus', 'job=' + job_name, 'input=' + input_file, 'interactive']
    
    try:
        # Run Abaqus
        print("Executing Abaqus command:", ' '.join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)  # 1 hour timeout
        
        if result.returncode == 0:
            print("Abaqus job completed successfully!")
            return True
        else:
            print(f"Abaqus job failed with return code: {result.returncode}")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("Abaqus job timed out after 1 hour")
        return False
    except FileNotFoundError:
        print("Error: Abaqus not found. Make sure Abaqus is installed and in PATH")
        return False
    except Exception as e:
        print(f"Error running Abaqus: {e}")
        return False

def check_abaqus_files(job_name):
    """
    Check if Abaqus generated the expected output files
    
    Args:
        job_name: Name of the Abaqus job
        
    Returns:
        dict: Status of various output files
    """
    files_to_check = {
        'odb': f"{job_name}.odb",
        'dat': f"{job_name}.dat",
        'msg': f"{job_name}.msg",
        'sta': f"{job_name}.sta"
    }
    
    status = {}
    for file_type, filename in files_to_check.items():
        status[file_type] = os.path.exists(filename)
        if status[file_type]:
            print(f"✓ {filename} found")
        else:
            print(f"✗ {filename} not found")
    
    return status

def run_post_processing(odb_file):
    """
    Run post-processing script on ODB file
    
    Args:
        odb_file: Path to ODB file
        
    Returns:
        bool: True if post-processing completed successfully
    """
    if not os.path.exists(odb_file):
        print(f"Error: ODB file {odb_file} not found")
        return False
    
    print(f"Running post-processing on {odb_file}")
    
    try:
        # Run post-processing script
        cmd = ['python', 'post_process_tl.py', odb_file]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            print("Post-processing completed successfully!")
            print("STDOUT:", result.stdout)
            return True
        else:
            print(f"Post-processing failed with return code: {result.returncode}")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("Post-processing timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"Error running post-processing: {e}")
        return False

def cleanup_files(job_name, keep_odb=True):
    """
    Clean up temporary Abaqus files
    
    Args:
        job_name: Name of the Abaqus job
        keep_odb: Whether to keep the ODB file
    """
    files_to_remove = [
        f"{job_name}.dat",
        f"{job_name}.msg", 
        f"{job_name}.sta",
        f"{job_name}.lck",
        f"{job_name}.prt",
        f"{job_name}.sim",
        f"{job_name}.com",
        f"{job_name}.log"
    ]
    
    if not keep_odb:
        files_to_remove.append(f"{job_name}.odb")
    
    print("Cleaning up temporary files...")
    for filename in files_to_remove:
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f"Removed {filename}")
            except Exception as e:
                print(f"Warning: Could not remove {filename}: {e}")

def main():
    """
    Main function to run the complete acoustic simulation workflow
    """
    print("="*60)
    print("ABAQUS ACOUSTIC TRANSMISSION LOSS SIMULATION")
    print("="*60)
    
    # Configuration
    input_file = "acoustic_transmission_loss.inp"
    job_name = "acoustic_tl_sim"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        print("Make sure you're running this script from the correct directory")
        sys.exit(1)
    
    print(f"Input file: {input_file}")
    print(f"Job name: {job_name}")
    print()
    
    # Step 1: Run Abaqus simulation
    print("STEP 1: Running Abaqus simulation...")
    print("-" * 40)
    
    start_time = time.time()
    success = run_abaqus_job(input_file, job_name)
    simulation_time = time.time() - start_time
    
    if not success:
        print("Simulation failed. Check Abaqus output for errors.")
        sys.exit(1)
    
    print(f"Simulation completed in {simulation_time:.1f} seconds")
    print()
    
    # Step 2: Check output files
    print("STEP 2: Checking output files...")
    print("-" * 40)
    
    file_status = check_abaqus_files(job_name)
    
    if not file_status['odb']:
        print("Error: ODB file not found. Simulation may have failed.")
        sys.exit(1)
    
    print()
    
    # Step 3: Run post-processing
    print("STEP 3: Running post-processing...")
    print("-" * 40)
    
    odb_file = f"{job_name}.odb"
    post_process_success = run_post_processing(odb_file)
    
    if not post_process_success:
        print("Post-processing failed. Check error messages above.")
        sys.exit(1)
    
    print()
    
    # Step 4: Summary
    print("STEP 4: Simulation Summary")
    print("-" * 40)
    print(f"✓ Abaqus simulation completed successfully")
    print(f"✓ Post-processing completed successfully")
    print(f"✓ Results saved to acoustic_results.csv")
    print(f"✓ Plot saved as acoustic_results.png")
    print(f"✓ Total runtime: {time.time() - start_time:.1f} seconds")
    
    # Ask about cleanup
    print()
    response = input("Clean up temporary files? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        cleanup_files(job_name, keep_odb=True)
        print("Cleanup completed. ODB file kept for further analysis.")
    else:
        print("Temporary files kept.")
    
    print("\nSimulation workflow completed successfully!")

if __name__ == "__main__":
    main()