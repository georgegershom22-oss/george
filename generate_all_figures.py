#!/usr/bin/env python3
"""
Master script to generate all three figures for shear-dominance analysis.
Runs all figure generation scripts and provides a summary.
"""

import subprocess
import sys
import os

def run_figure_script(script_name):
    """Run a figure generation script and capture output."""
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, check=True)
        print(f"✓ {script_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {script_name} failed:")
        print(f"  stdout: {e.stdout}")
        print(f"  stderr: {e.stderr}")
        return False

def main():
    """Generate all figures and provide summary."""
    print("Generating all figures for shear-dominance analysis...")
    print("=" * 60)
    
    # List of figure scripts
    scripts = [
        'figure_3_6a.py',
        'figure_3_6b.py', 
        'figure_3_6c.py'
    ]
    
    # Run each script
    success_count = 0
    for script in scripts:
        if os.path.exists(script):
            if run_figure_script(script):
                success_count += 1
        else:
            print(f"✗ {script} not found")
    
    print("=" * 60)
    print(f"Summary: {success_count}/{len(scripts)} figures generated successfully")
    
    # List generated files
    if os.path.exists('figures'):
        print("\nGenerated files:")
        for filename in sorted(os.listdir('figures')):
            filepath = os.path.join('figures', filename)
            size = os.path.getsize(filepath)
            print(f"  - {filename} ({size:,} bytes)")
    
    print("\nFigure descriptions:")
    print("  - Figure 3.6A: Shear-dominance index heatmap on (Ri, ω/N)")
    print("  - Figure 3.6B: Time-frequency TL fluctuation intensity (dual panel)")
    print("  - Figure 3.6C: Coherent fraction vs Ri and PSD broadening (dual panel)")
    
    print("\nAll figures include:")
    print("  - PNG format (300 DPI) for high-quality raster output")
    print("  - PDF format (vector) for publication-ready scalable graphics")
    print("  - SVG format (vector) for web use and further editing")

if __name__ == "__main__":
    main()