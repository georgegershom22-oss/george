#!/usr/bin/env python3
"""
Master script to generate all Figure 3.8 scientific plots for thesis
Follows the shared house style specifications exactly.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_script(script_name):
    """Run a Python script and return success status"""
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, cwd='/workspace')
        if result.returncode == 0:
            print(f"✓ {script_name} - Success")
            return True
        else:
            print(f"✗ {script_name} - Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ {script_name} - Exception: {e}")
        return False

def main():
    print("=" * 60)
    print("GENERATING SCIENTIFIC FIGURES 3.8A-D FOR THESIS")
    print("=" * 60)
    print()
    
    # List of figure scripts in order
    figures = [
        ('figure_3_8a.py', 'Predicted dominant pathway in (Ri, ω/N)'),
        ('figure_3_8b.py', 'Layered regime map in (CZ, kδ)'),
        ('figure_3_8c.py', 'Apparent attenuation vs ω/N'),
        ('figure_3_8d.py', 'Notch depth vs kδ')
    ]
    
    success_count = 0
    
    for script, description in figures:
        print(f"Generating {script}: {description}")
        if run_script(script):
            success_count += 1
        print()
    
    print("=" * 60)
    print("GENERATION SUMMARY")
    print("=" * 60)
    print(f"Successfully generated: {success_count}/{len(figures)} figures")
    
    # List generated files
    print("\\nGenerated files:")
    for script, _ in figures:
        base_name = script.replace('.py', '')
        formats = ['.pdf', '.png', '.svg']
        for fmt in formats:
            file_path = f"/workspace/{base_name}{fmt}"
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path) / 1024  # KB
                print(f"  ✓ {base_name}{fmt} ({file_size:.1f} KB)")
            else:
                print(f"  ✗ {base_name}{fmt} (missing)")
    
    print("\\nFigure specifications:")
    print("  • Canvas: 2000×1400 px (landscape), white background")
    print("  • Typeface: Helvetica/Arial")
    print("  • Titles: 28 pt bold")
    print("  • Axis labels: 22 pt")
    print("  • Tick labels: 16 pt")
    print("  • Grid: light gray #E5E7EB (0.8 px)")
    print("  • Export formats: PDF (vector), PNG (300 dpi), SVG (vector)")
    
    if success_count == len(figures):
        print("\\n🎉 All figures generated successfully!")
        print("Ready for thesis inclusion.")
    else:
        print(f"\\n⚠️  {len(figures) - success_count} figures failed to generate.")
        print("Check error messages above.")

if __name__ == "__main__":
    main()