#!/bin/bash
################################################################################
# Abaqus Acoustic Transmission Loss - Complete Workflow Script
################################################################################
# This script automates the entire simulation workflow:
#   1. Run Abaqus analysis
#   2. Post-process results
#   3. Generate visualizations
#
# Usage:
#   ./run_simulation.sh [job_name] [num_cpus]
#
# Example:
#   ./run_simulation.sh acoustic_TL 4
################################################################################

set -e  # Exit on error

# Default parameters
JOB_NAME="${1:-acoustic_transmission_loss}"
NUM_CPUS="${2:-4}"
INPUT_FILE="${JOB_NAME}.inp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "================================================================================"
echo -e "${BLUE}ABAQUS ACOUSTIC TRANSMISSION LOSS - AUTOMATED WORKFLOW${NC}"
echo "================================================================================"
echo "Job name:       ${JOB_NAME}"
echo "Input file:     ${INPUT_FILE}"
echo "CPUs:           ${NUM_CPUS}"
echo "================================================================================"

# Check if input file exists
if [ ! -f "${INPUT_FILE}" ]; then
    echo -e "${RED}ERROR: Input file '${INPUT_FILE}' not found!${NC}"
    echo "Available .inp files:"
    ls -1 *.inp 2>/dev/null || echo "  (none found)"
    exit 1
fi

# Check if Abaqus is available
if ! command -v abaqus &> /dev/null; then
    echo -e "${RED}ERROR: 'abaqus' command not found!${NC}"
    echo "Please ensure Abaqus is installed and in your PATH."
    exit 1
fi

################################################################################
# STEP 1: Run Abaqus Analysis
################################################################################
echo ""
echo -e "${GREEN}STEP 1: Running Abaqus Analysis${NC}"
echo "--------------------------------------------------------------------------------"
echo "Command: abaqus job=${JOB_NAME} input=${INPUT_FILE} cpus=${NUM_CPUS} interactive"
echo ""

# Clean up old results
if [ -f "${JOB_NAME}.odb" ]; then
    echo -e "${YELLOW}WARNING: Removing existing ODB file${NC}"
    rm -f "${JOB_NAME}.odb"
fi

# Remove old status files
rm -f "${JOB_NAME}".{dat,msg,sta,log,com,prt,sim,stt}

# Run Abaqus
abaqus job="${JOB_NAME}" input="${INPUT_FILE}" cpus="${NUM_CPUS}" interactive

# Check if job completed successfully
if [ ! -f "${JOB_NAME}.odb" ]; then
    echo -e "${RED}ERROR: Abaqus analysis failed!${NC}"
    echo "Check the following files for details:"
    echo "  - ${JOB_NAME}.dat (data file)"
    echo "  - ${JOB_NAME}.msg (message file)"
    echo "  - ${JOB_NAME}.sta (status file)"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Abaqus analysis completed successfully${NC}"
echo "  ODB file: ${JOB_NAME}.odb"

################################################################################
# STEP 2: Post-Process Results
################################################################################
echo ""
echo -e "${GREEN}STEP 2: Post-Processing Results${NC}"
echo "--------------------------------------------------------------------------------"

if [ ! -f "extract_transmission_loss.py" ]; then
    echo -e "${RED}ERROR: Post-processing script 'extract_transmission_loss.py' not found!${NC}"
    exit 1
fi

echo "Command: abaqus python extract_transmission_loss.py ${JOB_NAME}.odb"
echo ""

abaqus python extract_transmission_loss.py "${JOB_NAME}.odb"

# Check if CSV was created
CSV_FILE="${JOB_NAME}_transmission_loss.csv"
if [ ! -f "${CSV_FILE}" ]; then
    echo -e "${RED}ERROR: Post-processing failed - CSV file not created${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Post-processing completed${NC}"
echo "  CSV file: ${CSV_FILE}"

################################################################################
# STEP 3: Generate Visualizations
################################################################################
echo ""
echo -e "${GREEN}STEP 3: Generating Visualizations${NC}"
echo "--------------------------------------------------------------------------------"

if [ ! -f "plot_transmission_loss.py" ]; then
    echo -e "${YELLOW}WARNING: Visualization script 'plot_transmission_loss.py' not found${NC}"
    echo "Skipping visualization step."
else
    # Check if Python and matplotlib are available
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${YELLOW}WARNING: Python not found - skipping visualization${NC}"
        PYTHON_CMD=""
    fi
    
    if [ -n "${PYTHON_CMD}" ]; then
        echo "Command: ${PYTHON_CMD} plot_transmission_loss.py ${CSV_FILE}"
        echo ""
        
        ${PYTHON_CMD} plot_transmission_loss.py "${CSV_FILE}" || {
            echo -e "${YELLOW}WARNING: Visualization failed (matplotlib may not be installed)${NC}"
            echo "You can still plot manually using the CSV file."
        }
        
        # Check for output images
        if ls ${JOB_NAME}_*.png 1> /dev/null 2>&1; then
            echo ""
            echo -e "${GREEN}✓ Visualizations generated${NC}"
            echo "  Images:"
            for img in ${JOB_NAME}_*.png; do
                echo "    - ${img}"
            done
        fi
    fi
fi

################################################################################
# Summary
################################################################################
echo ""
echo "================================================================================"
echo -e "${GREEN}WORKFLOW COMPLETED SUCCESSFULLY!${NC}"
echo "================================================================================"
echo "Generated files:"
echo "  - ${JOB_NAME}.odb            (Abaqus output database)"
echo "  - ${CSV_FILE}                (Transmission loss data)"
if ls ${JOB_NAME}_*.png 1> /dev/null 2>&1; then
    echo "  - ${JOB_NAME}_*.png          (Visualization plots)"
fi
echo ""
echo "To view results:"
echo "  1. Open ODB in Abaqus/Viewer:  abaqus viewer odb=${JOB_NAME}.odb"
echo "  2. View CSV data:              cat ${CSV_FILE} | head"
if ls ${JOB_NAME}_*.png 1> /dev/null 2>&1; then
    echo "  3. View plots:                 [image viewer] ${JOB_NAME}_comprehensive.png"
fi
echo ""
echo "For detailed documentation, see: README_ABAQUS_ACOUSTIC.md"
echo "================================================================================"
