#!/bin/bash
################################################################################
# Automated Abaqus Acoustic Simulation Runner
################################################################################
# Usage: ./run_simulation.sh [job_name]
#
# This script:
#   1. Generates the Abaqus model
#   2. Submits the job
#   3. Waits for completion
#   4. Runs post-processing
#   5. Generates plots
################################################################################

set -e  # Exit on error

# Default job name
JOB_NAME=${1:-acoustic_tl_job}

echo "========================================================================"
echo "Abaqus Acoustic Transmission Loss Simulation"
echo "========================================================================"
echo "Job name: $JOB_NAME"
echo ""

# Check if Abaqus is available
if ! command -v abaqus &> /dev/null; then
    echo "ERROR: Abaqus command not found!"
    echo "Please ensure Abaqus is installed and in your PATH."
    exit 1
fi

# Step 1: Generate model
echo "[1/5] Generating Abaqus model..."
abaqus cae noGUI=abaqus_acoustic_tl_simulation.py 2>&1 | tee model_generation.log

if [ $? -ne 0 ]; then
    echo "ERROR: Model generation failed! Check model_generation.log"
    exit 1
fi

# Check if input file was created
if [ ! -f "${JOB_NAME}.inp" ]; then
    echo "ERROR: Input file ${JOB_NAME}.inp not found!"
    exit 1
fi

echo "Model generated successfully: ${JOB_NAME}.inp"
echo ""

# Step 2: Submit job
echo "[2/5] Submitting Abaqus job..."
echo "This may take several minutes to hours depending on model size..."

# Check for existing ODB and ask to overwrite
if [ -f "${JOB_NAME}.odb" ]; then
    read -p "ODB file exists. Overwrite? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f ${JOB_NAME}.odb ${JOB_NAME}.dat ${JOB_NAME}.msg ${JOB_NAME}.sta
        echo "Removed existing output files."
    else
        echo "Aborted. Please specify a different job name."
        exit 0
    fi
fi

# Submit job (background mode with monitoring)
abaqus job=${JOB_NAME} cpus=4 interactive 2>&1 | tee ${JOB_NAME}_run.log

if [ $? -ne 0 ]; then
    echo "ERROR: Job submission failed! Check ${JOB_NAME}_run.log"
    exit 1
fi

echo "Job completed successfully."
echo ""

# Step 3: Check for errors
echo "[3/5] Checking for errors..."

if [ -f "${JOB_NAME}.dat" ]; then
    ERROR_COUNT=$(grep -i "error" ${JOB_NAME}.dat | wc -l)
    WARNING_COUNT=$(grep -i "warning" ${JOB_NAME}.dat | wc -l)
    
    echo "  Errors found: $ERROR_COUNT"
    echo "  Warnings found: $WARNING_COUNT"
    
    if [ $ERROR_COUNT -gt 0 ]; then
        echo ""
        echo "ERRORS detected in .dat file:"
        grep -i "error" ${JOB_NAME}.dat
        echo ""
        echo "Review ${JOB_NAME}.dat for details."
        exit 1
    fi
    
    if [ $WARNING_COUNT -gt 0 ]; then
        echo ""
        echo "WARNINGS detected (check ${JOB_NAME}.dat for details)"
    fi
else
    echo "WARNING: .dat file not found. Cannot check for errors."
fi

echo ""

# Step 4: Post-process
echo "[4/5] Post-processing results..."

if [ ! -f "${JOB_NAME}.odb" ]; then
    echo "ERROR: ODB file ${JOB_NAME}.odb not found!"
    exit 1
fi

abaqus python postprocess_tl.py ${JOB_NAME} 2>&1 | tee postprocess.log

if [ $? -ne 0 ]; then
    echo "ERROR: Post-processing failed! Check postprocess.log"
    exit 1
fi

echo "Post-processing completed."
echo ""

# Step 5: Generate plots (if matplotlib available)
echo "[5/5] Generating plots..."

if command -v python3 &> /dev/null; then
    if python3 -c "import matplotlib" &> /dev/null; then
        python3 plot_tl.py 2>&1 | tee plot.log
        
        if [ $? -eq 0 ]; then
            echo "Plots generated successfully."
        else
            echo "WARNING: Plot generation failed. Check plot.log"
        fi
    else
        echo "WARNING: matplotlib not available. Skipping plots."
        echo "Install with: pip install matplotlib"
    fi
else
    echo "WARNING: Python 3 not found. Skipping plots."
fi

echo ""
echo "========================================================================"
echo "Simulation Complete!"
echo "========================================================================"
echo ""
echo "Output files:"
echo "  - ${JOB_NAME}.odb          (Abaqus results database)"
echo "  - ${JOB_NAME}.dat          (Analysis log)"
echo "  - transmission_loss.csv    (TL and alpha data)"
echo "  - plot_tl.py               (Plotting script)"
if [ -f "transmission_loss_results.png" ]; then
    echo "  - transmission_loss_results.png (Plots)"
fi
echo ""
echo "To view results:"
echo "  - Open ODB: abaqus viewer odb=${JOB_NAME}.odb"
echo "  - View CSV: cat transmission_loss.csv"
echo "  - Re-plot: python3 plot_tl.py"
echo ""
echo "========================================================================"
