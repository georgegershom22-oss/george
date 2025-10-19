"""
Main script to generate all Figure 3.6 plots for shear-dominance analysis
Generates high-quality vector (PDF/SVG) and raster (PNG) outputs
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for batch processing

import matplotlib.pyplot as plt
from figure_3_6a import create_figure_3_6a
from figure_3_6b import create_figure_3_6b
from figure_3_6c import create_figure_3_6c
import os

def main():
    """Generate all three figures"""
    
    # Set matplotlib parameters for consistent rendering
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    plt.rcParams['mathtext.fontset'] = 'stixsans'
    plt.rcParams['axes.linewidth'] = 2
    plt.rcParams['lines.linewidth'] = 3
    
    print("=" * 60)
    print("Generating Figure 3.6 series for shear-dominance analysis")
    print("=" * 60)
    
    # Create output directory
    output_dir = "figures"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Generate Figure 3.6A
    print("\nGenerating Figure 3.6A - Shear-dominance index...")
    fig_a = create_figure_3_6a()
    fig_a.savefig(os.path.join(output_dir, 'figure_3_6a.png'), 
                  dpi=300, bbox_inches='tight', facecolor='white')
    fig_a.savefig(os.path.join(output_dir, 'figure_3_6a.pdf'), 
                  bbox_inches='tight', facecolor='white')
    fig_a.savefig(os.path.join(output_dir, 'figure_3_6a.svg'), 
                  bbox_inches='tight', facecolor='white')
    plt.close(fig_a)
    print("✓ Figure 3.6A saved (PNG, PDF, SVG)")
    
    # Generate Figure 3.6B
    print("\nGenerating Figure 3.6B - Time-frequency TL fluctuation...")
    fig_b = create_figure_3_6b()
    fig_b.savefig(os.path.join(output_dir, 'figure_3_6b.png'), 
                  dpi=300, bbox_inches='tight', facecolor='white')
    fig_b.savefig(os.path.join(output_dir, 'figure_3_6b.pdf'), 
                  bbox_inches='tight', facecolor='white')
    fig_b.savefig(os.path.join(output_dir, 'figure_3_6b.svg'), 
                  bbox_inches='tight', facecolor='white')
    plt.close(fig_b)
    print("✓ Figure 3.6B saved (PNG, PDF, SVG)")
    
    # Generate Figure 3.6C
    print("\nGenerating Figure 3.6C - Coherent fraction & PSD broadening...")
    fig_c = create_figure_3_6c()
    fig_c.savefig(os.path.join(output_dir, 'figure_3_6c.png'), 
                  dpi=300, bbox_inches='tight', facecolor='white')
    fig_c.savefig(os.path.join(output_dir, 'figure_3_6c.pdf'), 
                  bbox_inches='tight', facecolor='white')
    fig_c.savefig(os.path.join(output_dir, 'figure_3_6c.svg'), 
                  bbox_inches='tight', facecolor='white')
    plt.close(fig_c)
    print("✓ Figure 3.6C saved (PNG, PDF, SVG)")
    
    print("\n" + "=" * 60)
    print("All figures generated successfully!")
    print(f"Output location: ./{output_dir}/")
    print("\nFile formats:")
    print("  - PNG: High-resolution raster (300 DPI) for presentations")
    print("  - PDF: Vector format for publication")
    print("  - SVG: Editable vector format for further customization")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✓ Generation complete. All figures ready for use.")