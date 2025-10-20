import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np
from matplotlib.colors import to_rgba

# Set up the style parameters
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial'],
    'font.size': 16,
    'axes.linewidth': 0.8,
    'grid.linewidth': 0.8,
    'grid.alpha': 0.3,
    'lines.linewidth': 3
})

# Define the color scheme
colors = {
    'classical': '#6B7280',
    'conversion': '#F4A261', 
    'interfacial': '#6A4C93',
    'shear': '#2A9D8F',
    'grid': '#E5E7EB',
    'conversion_band': to_rgba('#F4A261', 0.2),
    'text': '#374151'
}

def create_figure_3_7a():
    """Create Figure 3.7A - Composite attenuation concept (block diagram)"""
    fig, ax = plt.subplots(figsize=(20, 14))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    # Title
    ax.text(10, 13.5, 'Figure 3.7A — Composite attenuation concept', 
            fontsize=28, fontweight='bold', ha='center', color=colors['text'])
    
    # (A) Inputs column (left)
    inputs_box = FancyBboxPatch((0.5, 8), 3, 4, 
                               boxstyle="round,pad=0.1", 
                               facecolor='white', edgecolor='black', linewidth=1.5)
    ax.add_patch(inputs_box)
    ax.text(2, 11.8, 'Inputs', fontsize=22, fontweight='bold', ha='center')
    
    # Input variables
    inputs = ['ω/N (frequency ratio)', 'Ri (stability)', 'kδ (interface optical thickness)', 
              'CZ, At (impedance/Atwood)', 'θ (incidence)', 'r (range)']
    y_positions = [11.2, 10.8, 10.4, 10.0, 9.6, 9.2]
    
    for i, (input_text, y_pos) in enumerate(zip(inputs, y_positions)):
        # Bullet point
        ax.plot(1.2, y_pos, 'o', markersize=4, color='black')
        ax.text(1.4, y_pos, input_text, fontsize=16, va='center')
        # Arrow to central module
        ax.annotate('', xy=(4.5, 10), xytext=(1.2, y_pos),
                   arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))
    
    # (B) Similarity space cue (center-top)
    similarity_box = FancyBboxPatch((4.5, 9.5), 5.2, 3.2, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='white', edgecolor='black', linewidth=1.5)
    ax.add_patch(similarity_box)
    
    # Similarity space axes
    ax.plot([5, 9.2], [10.5, 10.5], 'k-', linewidth=1)  # x-axis
    ax.plot([5, 5], [10.5, 12.2], 'k-', linewidth=1)    # y-axis
    
    # Axis labels
    ax.text(7.1, 10.2, 'ω/N', fontsize=16, ha='center')
    ax.text(4.6, 11.35, 'Ri', fontsize=16, ha='center', rotation=90)
    
    # Axis ticks and labels
    ax.plot([5, 5], [10.4, 10.6], 'k-', linewidth=1)
    ax.plot([9.2, 9.2], [10.4, 10.6], 'k-', linewidth=1)
    ax.text(5, 10.1, '0.2', fontsize=14, ha='center')
    ax.text(9.2, 10.1, '2.2', fontsize=14, ha='center')
    
    ax.plot([4.8, 5.2], [10.5, 10.5], 'k-', linewidth=1)
    ax.plot([4.8, 5.2], [12.2, 12.2], 'k-', linewidth=1)
    ax.text(4.6, 10.5, '0', fontsize=14, ha='center')
    ax.text(4.6, 12.2, '2', fontsize=14, ha='center')
    
    # Soft regions
    conversion_region = patches.Ellipse((7.1, 11.2), 2.5, 0.8, 
                                       facecolor=colors['conversion_band'], 
                                       alpha=0.3, edgecolor='none')
    ax.add_patch(conversion_region)
    ax.text(7.1, 11.2, 'conversion belt', fontsize=14, ha='center', alpha=0.7)
    
    shear_region = patches.Ellipse((6.5, 10.8), 1.8, 0.6, 
                                  facecolor=to_rgba(colors['shear'], 0.3), 
                                  alpha=0.3, edgecolor='none')
    ax.add_patch(shear_region)
    ax.text(6.5, 10.8, 'shear-favored', fontsize=14, ha='center', alpha=0.7)
    
    # (C) Mechanism weighting module (center-middle)
    weighting_box = FancyBboxPatch((4.5, 6.5), 5.6, 2.6, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='white', edgecolor='black', linewidth=1.5)
    ax.add_patch(weighting_box)
    ax.text(7.3, 8.8, 'Mechanism weighting (shares sum to 1)', 
            fontsize=22, fontweight='bold', ha='center')
    
    # Stacked horizontal bar
    bar_y = 8.2
    bar_width = 4.5
    bar_height = 0.3
    
    # Classical (grey) - 35%
    classical_bar = patches.Rectangle((5.2, bar_y), bar_width * 0.35, bar_height, 
                                     facecolor=colors['classical'], edgecolor='black', linewidth=0.5)
    ax.add_patch(classical_bar)
    ax.text(5.2 + bar_width * 0.35/2, bar_y + bar_height/2, 'Classical', 
            fontsize=16, ha='center', va='center', color='white', fontweight='bold')
    
    # Mode conversion (amber) - 45%
    conversion_bar = patches.Rectangle((5.2 + bar_width * 0.35, bar_y), bar_width * 0.45, bar_height, 
                                      facecolor=colors['conversion'], edgecolor='black', linewidth=0.5)
    ax.add_patch(conversion_bar)
    ax.text(5.2 + bar_width * 0.35 + bar_width * 0.45/2, bar_y + bar_height/2, 'Conversion', 
            fontsize=16, ha='center', va='center', color='white', fontweight='bold')
    
    # Interfacial (purple) - 10%
    interfacial_bar = patches.Rectangle((5.2 + bar_width * 0.8, bar_y), bar_width * 0.10, bar_height, 
                                       facecolor=colors['interfacial'], edgecolor='black', linewidth=0.5)
    ax.add_patch(interfacial_bar)
    ax.text(5.2 + bar_width * 0.8 + bar_width * 0.10/2, bar_y + bar_height/2, 'Interfacial', 
            fontsize=16, ha='center', va='center', color='white', fontweight='bold')
    
    # Shear (teal) - 10%
    shear_bar = patches.Rectangle((5.2 + bar_width * 0.9, bar_y), bar_width * 0.10, bar_height, 
                                 facecolor=colors['shear'], edgecolor='black', linewidth=0.5)
    ax.add_patch(shear_bar)
    ax.text(5.2 + bar_width * 0.9 + bar_width * 0.10/2, bar_y + bar_height/2, 'Shear', 
            fontsize=16, ha='center', va='center', color='white', fontweight='bold')
    
    # Sum notation
    ax.text(9.8, bar_y + bar_height/2, 'Σwi = 1', fontsize=16, ha='center', va='center', 
            bbox=dict(boxstyle="round,pad=0.1", facecolor='white', edgecolor='black'))
    
    # Guidance text
    ax.text(7.3, 7.8, 'shares guided by §3.2 similarity & §3.4–3.6 scalings', 
            fontsize=14, ha='center', style='italic')
    
    # (D) Combination node (center-bottom)
    sigma_x, sigma_y = 7.3, 5.8
    ax.text(sigma_x, sigma_y, 'Σ', fontsize=48, ha='center', va='center', fontweight='bold')
    ax.text(sigma_x, sigma_y - 0.4, 'Composite attenuation', fontsize=18, ha='center', va='center')
    
    # Arrow from weighting box to combination node
    ax.annotate('', xy=(sigma_x, sigma_y + 0.3), xytext=(7.3, 6.5),
               arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    # Priors and posterior arrows
    ax.annotate('priors', xy=(5.5, 7.5), xytext=(sigma_x - 0.5, sigma_y + 0.3),
               arrowprops=dict(arrowstyle='->', lw=1.5, color='black', linestyle='--'))
    ax.annotate('posterior (with data)', xy=(9.5, 4.5), xytext=(sigma_x + 0.5, sigma_y + 0.3),
               arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    # (E) Outputs column (right)
    outputs_box = FancyBboxPatch((16.5, 8), 3.6, 4, 
                                boxstyle="round,pad=0.1", 
                                facecolor='white', edgecolor='black', linewidth=1.5)
    ax.add_patch(outputs_box)
    ax.text(18.3, 11.8, 'Predicted / measured outputs', fontsize=22, fontweight='bold', ha='center')
    
    # Output icons
    # TL(ω) curve
    omega_tl = np.linspace(0.2, 2.2, 50)
    tl_curve = 0.3 * np.exp(-(omega_tl - 1.0)**2 / 0.5) + 0.1
    ax.plot(17 + omega_tl * 0.8, 11.2 + tl_curve * 0.3, 'k-', linewidth=2)
    ax.text(18.3, 10.8, 'TL(ω)', fontsize=16, ha='center')
    
    # Coherence γ²(ω)
    gamma_curve = 0.8 - 0.4 * np.exp(-(omega_tl - 1.0)**2 / 0.3)
    ax.plot(17 + omega_tl * 0.8, 10.4 + gamma_curve * 0.3, 'k-', linewidth=2)
    ax.text(18.3, 10.0, 'γ²(ω)', fontsize=16, ha='center')
    
    # PSD(ω) width
    psd_narrow = 0.2 * np.exp(-(omega_tl - 1.0)**2 / 0.1) + 0.1
    psd_broad = 0.15 * np.exp(-(omega_tl - 1.0)**2 / 0.8) + 0.05
    ax.plot(17 + omega_tl * 0.8, 9.6 + psd_narrow * 0.3, 'k-', linewidth=2)
    ax.plot(17 + omega_tl * 0.8, 9.2 + psd_broad * 0.3, 'k--', linewidth=2)
    ax.text(18.3, 8.8, 'PSD(ω)', fontsize=16, ha='center')
    
    # Design implications
    ax.text(18.3, 8.2, 'Design implications:', fontsize=16, ha='center', fontweight='bold')
    ax.text(18.3, 7.8, 'Choose ω, θ, Ri, kδ to target\nmechanisms; update priors with data.', 
            fontsize=14, ha='center', style='italic')
    
    # Legend (bottom-right)
    legend_x = 15
    legend_y = 3
    legend_items = ['Classical', 'Mode conversion', 'Interfacial', 'Shear-mediated']
    legend_colors = [colors['classical'], colors['conversion'], colors['interfacial'], colors['shear']]
    
    for i, (item, color) in enumerate(zip(legend_items, legend_colors)):
        y_pos = legend_y - i * 0.4
        ax.plot(legend_x, y_pos, 's', markersize=8, color=color)
        ax.text(legend_x + 0.3, y_pos, item, fontsize=16, va='center')
    
    # Caption
    ax.text(10, 1.5, 'Figure 3.7A. Composite attenuation concept. Similarity variables feed a mechanism-weighting module that yields shares summing to unity; these combine into a composite prediction of attenuation and observables used to set priors and design experiments.', 
            fontsize=15, ha='center', style='italic', wrap=True)
    
    plt.tight_layout()
    plt.savefig('figure_3_7a.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_figure_3_7b1():
    """Create Figure 3.7B1 - Mechanism shares vs ω/N (High Ri, continuous)"""
    fig, ax = plt.subplots(figsize=(20, 14))
    
    # Set up axes
    omega = np.linspace(0.2, 2.2, 200)
    
    # Define mechanism shares (high Ri case)
    classical = 0.35 + 0.1 * (omega - 0.2) / 2.0  # Baseline ~0.35-0.45, slowly rising
    conversion = 0.45 * np.exp(-((omega - 1.0) / 0.6)**2)  # Dome centered at ω/N≈1, peak ~0.45-0.60
    interfacial = 0.05 + 0.05 * np.sin(omega * np.pi)  # Small and nearly flat, ≤0.10
    shear = 0.05 + 0.05 * np.exp(-((omega - 1.0) / 0.3)**2)  # Low, slight shoulder near 1, ≤0.10
    
    # Normalize to sum to 1
    total = classical + conversion + interfacial + shear
    classical = classical / total
    conversion = conversion / total
    interfacial = interfacial / total
    shear = shear / total
    
    # Create stacked area plot
    ax.fill_between(omega, 0, classical, color=colors['classical'], alpha=0.8, label='Classical')
    ax.fill_between(omega, classical, classical + conversion, color=colors['conversion'], alpha=0.8, label='Mode conversion')
    ax.fill_between(omega, classical + conversion, classical + conversion + interfacial, color=colors['interfacial'], alpha=0.8, label='Interfacial')
    ax.fill_between(omega, classical + conversion + interfacial, classical + conversion + interfacial + shear, color=colors['shear'], alpha=0.8, label='Shear-mediated')
    
    # Add conversion band overlay
    ax.axvspan(0.8, 1.2, alpha=0.2, color=colors['conversion'], zorder=0)
    ax.axvline(x=1.0, color='#9CA3AF', linestyle=':', linewidth=1.2, zorder=1)
    
    # Formatting
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(0, 1)
    ax.set_xlabel('ω/N', fontsize=22)
    ax.set_ylabel('Share (0–1)', fontsize=22)
    ax.set_title('Figure 3.7B1 — Mechanism shares vs ω/N (High Ri)', fontsize=28, fontweight='bold', pad=20)
    
    # Set ticks
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.tick_params(axis='both', which='major', labelsize=16)
    
    # Grid
    ax.grid(True, color=colors['grid'], linewidth=0.8, alpha=0.3)
    
    # Annotations
    ax.annotate('conversion peak near ω/N ≈ 1', xy=(1.0, 0.8), xytext=(1.5, 0.9),
               arrowprops=dict(arrowstyle='->', lw=1.5, color='black'),
               fontsize=16, ha='center')
    ax.annotate('classical baseline', xy=(0.5, 0.4), xytext=(0.3, 0.2),
               arrowprops=dict(arrowstyle='->', lw=1.5, color='black'),
               fontsize=16, ha='center')
    ax.annotate('secondary shear (stable)', xy=(1.1, 0.15), xytext=(1.8, 0.25),
               arrowprops=dict(arrowstyle='->', lw=1.5, color='black'),
               fontsize=16, ha='center')
    
    # Legend
    ax.legend(loc='upper right', fontsize=16, frameon=False)
    
    # Caption
    ax.text(10, 0.1, 'Figure 3.7B1. Under high Ri and continuous stratification, mode conversion dominates near ω/N ≈ 1; classical loss is the baseline; shear and interfacial contributions are secondary.', 
            fontsize=15, ha='center', style='italic', transform=ax.transAxes)
    
    plt.tight_layout()
    plt.savefig('figure_3_7b1.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_figure_3_7b2():
    """Create Figure 3.7B2 - Mechanism shares vs ω/N (Marginal Ri, continuous)"""
    fig, ax = plt.subplots(figsize=(20, 14))
    
    # Set up axes
    omega = np.linspace(0.2, 2.2, 200)
    
    # Define mechanism shares (marginal Ri case)
    classical = 0.25 + 0.1 * (omega - 0.2) / 2.0  # Reduced pedestal ~0.25-0.35
    conversion = 0.4 * np.exp(-((omega - 1.0) / 0.6)**2)  # Still domed, peak ~0.35-0.50
    interfacial = 0.05 + 0.05 * np.sin(omega * np.pi)  # Still small, ≤0.10
    shear = 0.15 + 0.3 * np.exp(-((omega - 1.0) / 0.4)**2)  # Broad rise in 0.8-1.3, peak ~0.30-0.45
    
    # Normalize to sum to 1
    total = classical + conversion + interfacial + shear
    classical = classical / total
    conversion = conversion / total
    interfacial = interfacial / total
    shear = shear / total
    
    # Create stacked area plot
    ax.fill_between(omega, 0, classical, color=colors['classical'], alpha=0.8, label='Classical')
    ax.fill_between(omega, classical, classical + conversion, color=colors['conversion'], alpha=0.8, label='Mode conversion')
    ax.fill_between(omega, classical + conversion, classical + conversion + interfacial, color=colors['interfacial'], alpha=0.8, label='Interfacial')
    ax.fill_between(omega, classical + conversion + interfacial, classical + conversion + interfacial + shear, color=colors['shear'], alpha=0.8, label='Shear-mediated')
    
    # Add conversion band overlay
    ax.axvspan(0.8, 1.2, alpha=0.2, color=colors['conversion'], zorder=0)
    ax.axvline(x=1.0, color='#9CA3AF', linestyle=':', linewidth=1.2, zorder=1)
    
    # Formatting
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(0, 1)
    ax.set_xlabel('ω/N', fontsize=22)
    ax.set_ylabel('Share (0–1)', fontsize=22)
    ax.set_title('Figure 3.7B2 — Mechanism shares vs ω/N (Marginal Ri)', fontsize=28, fontweight='bold', pad=20)
    
    # Set ticks
    ax.set_xticks([0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.tick_params(axis='both', which='major', labelsize=16)
    
    # Grid
    ax.grid(True, color=colors['grid'], linewidth=0.8, alpha=0.3)
    
    # Annotations
    ax.annotate('shear-mediated share expands and can rival conversion near ω/N ∼ 1', 
               xy=(1.0, 0.6), xytext=(1.5, 0.8),
               arrowprops=dict(arrowstyle='->', lw=1.5, color='black'),
               fontsize=16, ha='center')
    
    # Legend
    ax.legend(loc='upper right', fontsize=16, frameon=False)
    
    # Caption
    ax.text(10, 0.1, 'Figure 3.7B2. For marginal Ri, shear-mediated loss broadens around the conversion band and can rival conversion near ω/N ∼ 1; classical share correspondingly diminishes.', 
            fontsize=15, ha='center', style='italic', transform=ax.transAxes)
    
    plt.tight_layout()
    plt.savefig('figure_3_7b2.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_figure_3_7c1():
    """Create Figure 3.7C1 - Mechanism shares vs kδ (interface sharpness) at fixed ω/N"""
    fig, ax = plt.subplots(figsize=(20, 14))
    
    # Set up axes (log scale)
    kdelta = np.logspace(-1, np.log10(3), 200)  # 0.1 to 3 on log scale
    
    # Define mechanism shares at fixed ω/N = 1.0
    interfacial = 0.65 * np.exp(-(kdelta - 0.1) / 0.5)  # High at low kδ, decreases to ~0.10
    classical = 0.2 + 0.25 * (1 - np.exp(-(kdelta - 0.1) / 0.5))  # Complementary increase
    conversion = 0.25 + 0.05 * np.exp(-((kdelta - 1.0) / 0.8)**2)  # Roughly constant with mild bump
    shear = 0.05 + 0.05 * np.random.random(len(kdelta)) * 0.1  # Small and nearly flat
    
    # Normalize to sum to 1
    total = classical + conversion + interfacial + shear
    classical = classical / total
    conversion = conversion / total
    interfacial = interfacial / total
    shear = shear / total
    
    # Create stacked area plot
    ax.fill_between(kdelta, 0, classical, color=colors['classical'], alpha=0.8, label='Classical')
    ax.fill_between(kdelta, classical, classical + conversion, color=colors['conversion'], alpha=0.8, label='Mode conversion')
    ax.fill_between(kdelta, classical + conversion, classical + conversion + interfacial, color=colors['interfacial'], alpha=0.8, label='Interfacial')
    ax.fill_between(kdelta, classical + conversion + interfacial, classical + conversion + interfacial + shear, color=colors['shear'], alpha=0.8, label='Shear-mediated')
    
    # Formatting
    ax.set_xlim(0.1, 3)
    ax.set_ylim(0, 1)
    ax.set_xlabel('kδ', fontsize=22)
    ax.set_ylabel('Share (0–1)', fontsize=22)
    ax.set_title('Figure 3.7C1 — Mechanism shares vs kδ (interface sharpness), fixed ω/N = 1', fontsize=28, fontweight='bold', pad=20)
    
    # Set ticks (log scale)
    ax.set_xscale('log')
    ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 3])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.tick_params(axis='both', which='major', labelsize=16)
    
    # Grid
    ax.grid(True, color=colors['grid'], linewidth=0.8, alpha=0.3)
    
    # Add mini gauge beneath x-axis
    gauge_y = -0.15
    ax.text(0.1, gauge_y, 'thin', fontsize=14, ha='center', transform=ax.transAxes)
    ax.text(0.5, gauge_y, 'resonant', fontsize=14, ha='center', transform=ax.transAxes)
    ax.text(0.9, gauge_y, 'thick', fontsize=14, ha='center', transform=ax.transAxes)
    
    # Add vertical lines at gauge positions
    ax.axvline(x=0.1, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=1.0, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=3.0, color='gray', linestyle='--', alpha=0.5)
    
    # Legend
    ax.legend(loc='upper right', fontsize=16, frameon=False)
    
    # Caption
    ax.text(10, 0.1, 'Figure 3.7C1. Interfacial share peaks for sharp, high-contrast transitions (low kδ) and decays as the interface becomes diffuse (large kδ). Classical share increases complementarily; conversion and shear change little at fixed ω/N.', 
            fontsize=15, ha='center', style='italic', transform=ax.transAxes)
    
    plt.tight_layout()
    plt.savefig('figure_3_7c1.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

if __name__ == "__main__":
    print("Generating Figure 3.7A...")
    create_figure_3_7a()
    print("✓ Figure 3.7A saved as figure_3_7a.png")
    
    print("Generating Figure 3.7B1...")
    create_figure_3_7b1()
    print("✓ Figure 3.7B1 saved as figure_3_7b1.png")
    
    print("Generating Figure 3.7B2...")
    create_figure_3_7b2()
    print("✓ Figure 3.7B2 saved as figure_3_7b2.png")
    
    print("Generating Figure 3.7C1...")
    create_figure_3_7c1()
    print("✓ Figure 3.7C1 saved as figure_3_7c1.png")
    
    print("\nAll figures generated successfully!")