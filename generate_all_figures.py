#!/usr/bin/env python3
"""
Generate all figures in the 3.7 series
Run this script to create all publication-quality vector graphics
"""

import subprocess
import sys

def run_script(script_name):
    """Run a Python script and handle any errors"""
    print(f"\n{'='*60}")
    print(f"Generating {script_name.replace('_', ' ').replace('.py', '').title()}...")
    print('='*60)
    
    try:
        subprocess.run([sys.executable, script_name], check=True)
        print(f"✓ Successfully generated {script_name.replace('.py', '')}")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error generating {script_name}: {e}")
        return False
    return True

def main():
    """Generate all figures in sequence"""
    scripts = [
        'figure_3_7a_block_diagram.py',
        'figure_3_7b1_high_ri.py', 
        'figure_3_7b2_marginal_ri.py',
        'figure_3_7c1_interface_sharpness.py'
    ]
    
    print("\nGenerating Scientific Figures - Acoustic Wave Attenuation Mechanisms")
    print("=" * 70)
    print("This will create both PNG and PDF versions of all figures")
    print("Canvas size: 2000×1400 px (landscape)")
    print("Output formats: PNG (raster) and PDF (vector)")
    
    success_count = 0
    for script in scripts:
        if run_script(script):
            success_count += 1
    
    print("\n" + "=" * 70)
    print(f"Generation complete: {success_count}/{len(scripts)} figures created successfully")
    print("\nGenerated files:")
    print("  - figure_3_7a.png / .pdf  : Composite attenuation concept block diagram")
    print("  - figure_3_7b1.png / .pdf : Mechanism shares vs ω/N (High Ri)")
    print("  - figure_3_7b2.png / .pdf : Mechanism shares vs ω/N (Marginal Ri)")
    print("  - figure_3_7c1.png / .pdf : Mechanism shares vs kδ (interface sharpness)")

if __name__ == "__main__":
    main()