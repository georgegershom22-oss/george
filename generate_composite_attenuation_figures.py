#!/usr/bin/env python3
"""
Generate Figures 3.7A, 3.7B1, 3.7B2, and 3.7C1 for composite attenuation concept.
Canvas: 2000×1400 px (landscape), white background.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
from matplotlib.patches import ConnectionPatch
import matplotlib.lines as mlines

# Define color palette
colors = {
    'classical': '#6B7280',      # neutral dark grey
    'conversion': '#F4A261',      # amber
    'interfacial': '#6A4C93',     # purple  
    'shear': '#2A9D8F',          # teal
    'grid': '#E5E7EB',           # light grey
    'dotted': '#9CA3AF',         # dotted centerline
    'dark_amber': '#C06A00',      # darker amber for curves
    'text': '#000000'             # black text
}

# Common figure settings
def setup_figure():
    """Create figure with standard dimensions and font settings."""
    fig = plt.figure(figsize=(20, 14), dpi=100)
    fig.patch.set_facecolor('white')
    
    # Set default font
    plt.rcParams['font.family'] = ['Helvetica', 'Arial', 'sans-serif']
    plt.rcParams['font.size'] = 16
    
    return fig

def create_figure_3_7A():
    """Create Figure 3.7A - Composite attenuation concept block diagram."""
    fig = setup_figure()
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 2000)
    ax.set_ylim(0, 1400)
    ax.axis('off')
    
    # Title
    ax.text(1000, 1350, 'Figure 3.7A — Composite attenuation concept', 
            ha='center', va='top', fontsize=28, fontweight='bold')
    
    # A. Inputs column (left)
    input_box = FancyBboxPatch((100, 500), 250, 400,
                                boxstyle="round,pad=10",
                                facecolor='#f8f9fa',
                                edgecolor='#6B7280',
                                linewidth=2)
    ax.add_patch(input_box)
    
    ax.text(225, 870, 'Inputs', ha='center', fontsize=22, fontweight='bold')
    
    # Input items with bullet points
    inputs = [
        ('ω/N', '(frequency ratio)'),
        ('Ri', '(stability)'),
        ('kδ', '(interface optical thickness)'),
        ('C_Z, A_t', '(contrast)'),
        ('θ, r', '(geometry)')
    ]
    
    y_pos = 810
    for param, desc in inputs:
        # Bullet point
        ax.plot(140, y_pos, 'o', color='#6B7280', markersize=6)
        # Parameter text
        ax.text(160, y_pos, param, va='center', fontsize=20, style='italic')
        # Description
        ax.text(230, y_pos, desc, va='center', fontsize=14, color='#6B7280')
        
        # Arrow to central module
        arrow = FancyArrowPatch((360, y_pos), (580, 700),
                                connectionstyle="arc3,rad=0.2",
                                arrowstyle='->', lw=1.5,
                                color='#6B7280', alpha=0.7)
        ax.add_patch(arrow)
        
        y_pos -= 70
    
    # B. Similarity space cue (center-top)
    sim_box = Rectangle((600, 900), 520, 320,
                        facecolor='#f8f9fa',
                        edgecolor='#6B7280',
                        linewidth=1.5)
    ax.add_patch(sim_box)
    
    ax.text(860, 1180, 'Similarity Space', ha='center', fontsize=18, fontweight='bold')
    
    # Mini axes for similarity space
    ax.text(620, 920, '0', fontsize=12)
    ax.text(620, 1180, '2', fontsize=12)
    ax.text(640, 920, 'Ri', fontsize=14, rotation=90, va='bottom')
    
    ax.text(620, 920, '0.2', fontsize=12, ha='center')
    ax.text(1100, 920, '2.2', fontsize=12, ha='center')
    ax.text(860, 905, 'ω/N', fontsize=14, ha='center')
    
    # Overlay soft regions
    conv_region = Rectangle((750, 950), 150, 200,
                           facecolor=colors['conversion'], alpha=0.15)
    ax.add_patch(conv_region)
    ax.text(825, 1050, 'conversion\nbelt', ha='center', fontsize=14, alpha=0.7)
    
    shear_region = Rectangle((920, 1000), 150, 150,
                           facecolor=colors['shear'], alpha=0.15)
    ax.add_patch(shear_region)
    ax.text(995, 1075, 'shear-\nfavored', ha='center', fontsize=14, alpha=0.7)
    
    # C. Mechanism weighting module (center-middle)
    weight_box = FancyBboxPatch((580, 550), 560, 260,
                                boxstyle="round,pad=10",
                                facecolor='white',
                                edgecolor='#6B7280',
                                linewidth=2)
    ax.add_patch(weight_box)
    
    ax.text(860, 780, 'Mechanism weighting (shares sum to 1)',
            ha='center', fontsize=22, fontweight='bold')
    
    # Stacked bar chart
    bar_y = 680
    bar_height = 40
    bar_x = 640
    bar_width = 440
    
    # Example shares for visualization
    shares = {
        'classical': 0.35,
        'conversion': 0.40,
        'interfacial': 0.10,
        'shear': 0.15
    }
    
    x_pos = bar_x
    for mech, share in shares.items():
        width = bar_width * share
        rect = Rectangle((x_pos, bar_y), width, bar_height,
                        facecolor=colors[mech], edgecolor='none')
        ax.add_patch(rect)
        
        # Label each section if wide enough
        if width > 60:
            ax.text(x_pos + width/2, bar_y + bar_height/2, 
                   mech.capitalize()[:4], ha='center', va='center',
                   fontsize=12, color='white', fontweight='bold')
        
        x_pos += width
    
    # Sum notation
    ax.text(1120, bar_y + 20, 'Σw_i = 1', fontsize=16, style='italic')
    
    # Note about similarity and scaling
    ax.text(860, 590, 'shares guided by §3.2 similarity & §3.4–3.6 scalings',
            ha='center', fontsize=14, style='italic', alpha=0.8)
    
    # D. Combination node (center-bottom)
    sigma_node = plt.Circle((860, 450), 40, facecolor='#f8f9fa',
                           edgecolor='#6B7280', linewidth=2)
    ax.add_patch(sigma_node)
    ax.text(860, 450, 'Σ', fontsize=28, ha='center', va='center')
    ax.text(860, 380, 'Composite attenuation', ha='center', fontsize=18)
    
    # Arrow from weighting to combination
    arrow = FancyArrowPatch((860, 550), (860, 490),
                           arrowstyle='->', lw=2,
                           color='#6B7280')
    ax.add_patch(arrow)
    
    # Priors back-arrow (dotted)
    arrow = FancyArrowPatch((820, 450), (700, 550),
                           connectionstyle="arc3,rad=-0.3",
                           arrowstyle='->', lw=1.5,
                           linestyle='--', color='#6B7280', alpha=0.7)
    ax.add_patch(arrow)
    ax.text(720, 480, 'priors', fontsize=14, style='italic', alpha=0.8)
    
    # Forward arrow
    arrow = FancyArrowPatch((900, 450), (1300, 450),
                           arrowstyle='->', lw=2,
                           color='#6B7280')
    ax.add_patch(arrow)
    ax.text(1100, 470, 'posterior\n(with data)', ha='center', fontsize=14, style='italic')
    
    # E. Outputs column (right)
    output_box = FancyBboxPatch((1320, 500), 360, 400,
                                boxstyle="round,pad=10",
                                facecolor='#f8f9fa',
                                edgecolor='#6B7280',
                                linewidth=2)
    ax.add_patch(output_box)
    
    ax.text(1500, 870, 'Predicted / Measured Outputs',
            ha='center', fontsize=22, fontweight='bold')
    
    # Output items with icons
    outputs = [
        'TL(ω) curve',
        'Coherence γ²(ω)',
        'PSD(ω) width'
    ]
    
    y_pos = 790
    for output in outputs:
        # Simple icon representation
        ax.plot([1360, 1420], [y_pos, y_pos-10], color='#6B7280', lw=2)
        ax.text(1440, y_pos, output, va='center', fontsize=18)
        y_pos -= 80
    
    # Design implications note
    ax.text(1500, 420, 'Design implications:', ha='center', fontsize=16, fontweight='bold')
    ax.text(1500, 380, 'Choose ω, θ, Ri, kδ to target mechanisms;\nupdate priors with data.',
            ha='center', fontsize=14, style='italic')
    
    # Legend (bottom-right)
    legend_y = 200
    legend_x = 1400
    for i, (mech, color) in enumerate(colors.items()):
        if mech in ['classical', 'conversion', 'interfacial', 'shear']:
            rect = Rectangle((legend_x, legend_y - i*30), 30, 20,
                           facecolor=color, edgecolor='none')
            ax.add_patch(rect)
            ax.text(legend_x + 40, legend_y - i*30 + 10, mech.capitalize(),
                   va='center', fontsize=16)
    
    # Caption
    ax.text(1000, 100, 
           'Figure 3.7A. Composite attenuation concept. Similarity variables feed a mechanism-weighting module that yields\n'
           'shares summing to unity; these combine into a composite prediction of attenuation and observables used to set\n'
           'priors and design experiments.',
           ha='center', fontsize=15, style='italic')
    
    plt.tight_layout()
    plt.savefig('figure_3_7A.png', dpi=100, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Figure 3.7A created successfully")

def create_figure_3_7B1():
    """Create Figure 3.7B1 - Mechanism shares vs ω/N (High Ri, continuous)."""
    fig = setup_figure()
    ax = fig.add_subplot(111)
    
    # Title
    ax.set_title('Figure 3.7B1 — Mechanism shares vs ω/N (High Ri, continuous)',
                 fontsize=28, fontweight='bold', pad=20)
    
    # Axes setup
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(0, 1)
    ax.set_xlabel('ω/N', fontsize=22)
    ax.set_ylabel('Share', fontsize=22)
    
    # Set ticks
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    
    # Tick labels font size
    ax.tick_params(axis='both', labelsize=16)
    
    # Grid
    ax.grid(True, color=colors['grid'], linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)
    
    # Create smooth frequency array
    omega_N = np.linspace(0.2, 2.2, 200)
    
    # Define mechanism shares for High Ri case
    # Classical: baseline pedestal ~0.35-0.45
    classical_share = 0.40 + 0.05 * (omega_N - 1.2)**2 / 2
    classical_share = np.clip(classical_share, 0.35, 0.45)
    
    # Mode conversion: broad dome centered at ω/N ≈ 1
    conversion_share = 0.50 * np.exp(-0.8 * (omega_N - 1.0)**2)
    conversion_share = np.clip(conversion_share, 0.1, 0.55)
    
    # Shear-mediated: low in high Ri
    shear_share = 0.08 * np.exp(-2 * (omega_N - 1.0)**2) + 0.02
    shear_share = np.clip(shear_share, 0, 0.10)
    
    # Interfacial: minimal in continuous case
    interfacial_share = 0.05 * np.ones_like(omega_N)
    
    # Normalize to ensure sum = 1
    total = classical_share + conversion_share + shear_share + interfacial_share
    classical_share /= total
    conversion_share /= total
    shear_share /= total
    interfacial_share /= total
    
    # Create stacked area plot (bottom to top order)
    ax.fill_between(omega_N, 0, classical_share,
                   color=colors['classical'], alpha=1, label='Classical')
    
    bottom = classical_share
    ax.fill_between(omega_N, bottom, bottom + conversion_share,
                   color=colors['conversion'], alpha=1, label='Mode conversion')
    
    bottom += conversion_share
    ax.fill_between(omega_N, bottom, bottom + interfacial_share,
                   color=colors['interfacial'], alpha=1, label='Interfacial')
    
    bottom += interfacial_share
    ax.fill_between(omega_N, bottom, bottom + shear_share,
                   color=colors['shear'], alpha=1, label='Shear-mediated')
    
    # Conversion window overlay
    ax.axvspan(0.8, 1.2, alpha=0.2, color=colors['conversion'], zorder=0)
    ax.axvline(x=1.0, color=colors['dotted'], linestyle='--', linewidth=1.2, alpha=0.7)
    
    # Annotations
    ax.annotate('conversion peak\nnear ω/N ≈ 1', xy=(1.0, 0.7), xytext=(1.3, 0.8),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                fontsize=18, ha='center')
    
    ax.annotate('classical baseline', xy=(1.8, 0.2), xytext=(1.6, 0.1),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                fontsize=18, ha='center')
    
    # Legend
    ax.legend(loc='upper right', fontsize=16, frameon=False)
    
    # Caption
    fig.text(0.5, 0.05,
            'Figure 3.7B1. Under high Ri and continuous stratification, mode conversion dominates near ω/N ≈ 1;\n'
            'classical loss is the baseline; shear and interfacial contributions are secondary.',
            ha='center', fontsize=15, style='italic')
    
    plt.tight_layout()
    plt.savefig('figure_3_7B1.png', dpi=100, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Figure 3.7B1 created successfully")

def create_figure_3_7B2():
    """Create Figure 3.7B2 - Mechanism shares vs ω/N (Marginal Ri, continuous)."""
    fig = setup_figure()
    ax = fig.add_subplot(111)
    
    # Title
    ax.set_title('Figure 3.7B2 — Mechanism shares vs ω/N (Marginal Ri, continuous)',
                 fontsize=28, fontweight='bold', pad=20)
    
    # Axes setup
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(0, 1)
    ax.set_xlabel('ω/N', fontsize=22)
    ax.set_ylabel('Share', fontsize=22)
    
    # Set ticks
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    
    # Tick labels font size
    ax.tick_params(axis='both', labelsize=16)
    
    # Grid
    ax.grid(True, color=colors['grid'], linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)
    
    # Create smooth frequency array
    omega_N = np.linspace(0.2, 2.2, 200)
    
    # Define mechanism shares for Marginal Ri case
    # Classical: reduced pedestal in conversion band
    classical_base = 0.35 * np.ones_like(omega_N)
    classical_dip = 0.10 * np.exp(-2 * ((omega_N - 1.0)/0.25)**2)
    classical_share = classical_base - classical_dip
    classical_share = np.clip(classical_share, 0.25, 0.40)
    
    # Mode conversion: still domed but slightly lower peak
    conversion_share = 0.42 * np.exp(-0.8 * (omega_N - 1.0)**2)
    conversion_share = np.clip(conversion_share, 0.08, 0.42)
    
    # Shear-mediated: broad rise in conversion band
    shear_share = 0.35 * np.exp(-1.5 * ((omega_N - 1.05)/0.35)**2) + 0.05
    shear_share = np.clip(shear_share, 0.05, 0.38)
    
    # Interfacial: still small for continuous background
    interfacial_share = 0.06 * np.ones_like(omega_N)
    
    # Normalize to ensure sum = 1
    total = classical_share + conversion_share + shear_share + interfacial_share
    classical_share /= total
    conversion_share /= total
    shear_share /= total
    interfacial_share /= total
    
    # Create stacked area plot (bottom to top order)
    ax.fill_between(omega_N, 0, classical_share,
                   color=colors['classical'], alpha=1, label='Classical')
    
    bottom = classical_share
    ax.fill_between(omega_N, bottom, bottom + conversion_share,
                   color=colors['conversion'], alpha=1, label='Mode conversion')
    
    bottom += conversion_share
    ax.fill_between(omega_N, bottom, bottom + interfacial_share,
                   color=colors['interfacial'], alpha=1, label='Interfacial')
    
    bottom += interfacial_share
    ax.fill_between(omega_N, bottom, bottom + shear_share,
                   color=colors['shear'], alpha=1, label='Shear-mediated')
    
    # Conversion window overlay
    ax.axvspan(0.8, 1.2, alpha=0.2, color=colors['conversion'], zorder=0)
    ax.axvline(x=1.0, color=colors['dotted'], linestyle='--', linewidth=1.2, alpha=0.7)
    
    # Annotation
    ax.annotate('shear-mediated share expands\nand can rival conversion\nnear ω/N ~ 1',
                xy=(1.05, 0.75), xytext=(1.5, 0.85),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                fontsize=18, ha='center')
    
    # Legend
    ax.legend(loc='upper right', fontsize=16, frameon=False)
    
    # Caption
    fig.text(0.5, 0.05,
            'Figure 3.7B2. For marginal Ri, shear-mediated loss broadens around the conversion band and can\n'
            'rival conversion near ω/N ~ 1; classical share correspondingly diminishes.',
            ha='center', fontsize=15, style='italic')
    
    plt.tight_layout()
    plt.savefig('figure_3_7B2.png', dpi=100, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Figure 3.7B2 created successfully")

def create_figure_3_7C1():
    """Create Figure 3.7C1 - Mechanism shares vs kδ (interface sharpness) at fixed ω/N."""
    fig = setup_figure()
    ax = fig.add_subplot(111)
    
    # Title
    ax.set_title('Figure 3.7C1 — Mechanism shares vs kδ (interface sharpness), fixed ω/N = 1',
                 fontsize=28, fontweight='bold', pad=20)
    
    # Axes setup
    ax.set_xscale('log')
    ax.set_xlim(0.1, 3)
    ax.set_ylim(0, 1)
    ax.set_xlabel('kδ', fontsize=22)
    ax.set_ylabel('Share', fontsize=22)
    
    # Set ticks
    ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 3])
    ax.set_xticklabels(['0.1', '0.2', '0.5', '1', '2', '3'])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    
    # Tick labels font size
    ax.tick_params(axis='both', labelsize=16)
    
    # Grid
    ax.grid(True, color=colors['grid'], linewidth=0.8, alpha=0.7, which='major')
    ax.set_axisbelow(True)
    
    # Create log-spaced kδ array
    k_delta = np.logspace(np.log10(0.1), np.log10(3), 200)
    
    # Define mechanism shares vs kδ
    # Interfacial: highest for sharp layers (low kδ), decreases with kδ
    interfacial_share = 0.60 * np.exp(-0.8 * np.log10(k_delta/0.1)**2) + 0.05
    interfacial_share = np.clip(interfacial_share, 0.10, 0.60)
    
    # Classical: complementary increase as kδ grows
    classical_share = 0.20 + 0.25 * (1 - np.exp(-k_delta/1.5))
    classical_share = np.clip(classical_share, 0.20, 0.45)
    
    # Mode conversion: roughly constant at fixed ω/N = 1
    conversion_share = 0.25 + 0.03 * np.exp(-2 * (np.log10(k_delta) - 0)**2)
    conversion_share = np.clip(conversion_share, 0.20, 0.30)
    
    # Shear-mediated: small and nearly flat
    shear_share = 0.07 * np.ones_like(k_delta)
    
    # Normalize to ensure sum = 1
    total = classical_share + conversion_share + shear_share + interfacial_share
    classical_share /= total
    conversion_share /= total
    shear_share /= total
    interfacial_share /= total
    
    # Create stacked area plot (bottom to top order)
    ax.fill_between(k_delta, 0, classical_share,
                   color=colors['classical'], alpha=1, label='Classical')
    
    bottom = classical_share
    ax.fill_between(k_delta, bottom, bottom + conversion_share,
                   color=colors['conversion'], alpha=1, label='Mode conversion')
    
    bottom += conversion_share
    ax.fill_between(k_delta, bottom, bottom + interfacial_share,
                   color=colors['interfacial'], alpha=1, label='Interfacial')
    
    bottom += interfacial_share
    ax.fill_between(k_delta, bottom, bottom + shear_share,
                   color=colors['shear'], alpha=1, label='Shear-mediated')
    
    # Add bracket/gauge beneath x-axis
    ax.text(0.1, -0.12, 'thin', ha='center', fontsize=14, transform=ax.get_xaxis_transform())
    ax.text(1.0, -0.12, 'resonant', ha='center', fontsize=14, transform=ax.get_xaxis_transform())
    ax.text(3.0, -0.12, 'thick', ha='center', fontsize=14, transform=ax.get_xaxis_transform())
    
    # Add arrows for the gauge
    ax.annotate('', xy=(0.15, -0.08), xytext=(0.8, -0.08),
                xycoords='data', textcoords='data',
                arrowprops=dict(arrowstyle='<->', color='black', lw=1),
                transform=ax.get_xaxis_transform())
    ax.annotate('', xy=(1.2, -0.08), xytext=(2.8, -0.08),
                xycoords='data', textcoords='data',
                arrowprops=dict(arrowstyle='<->', color='black', lw=1),
                transform=ax.get_xaxis_transform())
    
    # Legend
    ax.legend(loc='upper right', fontsize=16, frameon=False)
    
    # Caption
    fig.text(0.5, 0.05,
            'Figure 3.7C1. Interfacial share peaks for sharp, high-contrast transitions (low kδ) and decays as the\n'
            'interface becomes diffuse (large kδ). Classical share increases complementarily; conversion and\n'
            'shear change little at fixed ω/N.',
            ha='center', fontsize=15, style='italic')
    
    plt.tight_layout()
    plt.savefig('figure_3_7C1.png', dpi=100, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Figure 3.7C1 created successfully")

def main():
    """Generate all four figures."""
    print("Generating composite attenuation concept figures...")
    
    # Create each figure
    create_figure_3_7A()
    create_figure_3_7B1()
    create_figure_3_7B2()
    create_figure_3_7C1()
    
    print("\nAll figures generated successfully!")
    print("Files created:")
    print("  - figure_3_7A.png: Composite attenuation concept block diagram")
    print("  - figure_3_7B1.png: Mechanism shares vs ω/N (High Ri)")
    print("  - figure_3_7B2.png: Mechanism shares vs ω/N (Marginal Ri)")
    print("  - figure_3_7C1.png: Mechanism shares vs kδ (interface sharpness)")

if __name__ == "__main__":
    main()