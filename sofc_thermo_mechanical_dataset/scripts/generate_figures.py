#!/usr/bin/env python3
"""
Generate publication-quality figures from SOFC dataset CSV files
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
FIG_DIR = Path(__file__).parent.parent / "figures"
DPI = 300

# Create figures directory if it doesn't exist
FIG_DIR.mkdir(exist_ok=True)

# Set publication-quality style
plt.rcParams['figure.dpi'] = DPI
plt.rcParams['savefig.dpi'] = DPI
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

# Color scheme
COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']


def plot_material_properties():
    """Plot thermophysical properties vs temperature for all materials"""
    
    # Define materials and their files
    materials = {
        'YSZ': 'ysz_thermophysical_properties.csv',
        'Ni-YSZ': 'ni_ysz_thermophysical_properties.csv',
        'LSM': 'lsm_thermophysical_properties.csv',
        'LSCF': 'lscf_thermophysical_properties.csv',
        'Crofer 22 APU': 'crofer22apu_thermophysical_properties.csv',
        'Glass-Ceramic': 'glass_ceramic_sealant_properties.csv'
    }
    
    # Properties to plot
    properties = [
        ('CTE_1e-6_per_K', 'Coefficient of Thermal Expansion (×10⁻⁶/K)'),
        ('Thermal_Conductivity_W_per_mK', 'Thermal Conductivity (W/m·K)'),
        ('Elastic_Modulus_GPa', 'Elastic Modulus (GPa)'),
        ('Specific_Heat_Capacity_J_per_kgK', 'Specific Heat Capacity (J/kg·K)')
    ]
    
    for prop_col, prop_label in properties:
        fig, ax = plt.subplots(figsize=(8, 6))
        
        for i, (mat_name, filename) in enumerate(materials.items()):
            filepath = DATA_DIR / '01_material_properties' / filename
            df = pd.read_csv(filepath, comment='#')
            ax.plot(df['Temperature_C'], df[prop_col], 
                   label=mat_name, linewidth=2, color=COLORS[i % len(COLORS)])
        
        ax.set_xlabel('Temperature (°C)')
        ax.set_ylabel(prop_label)
        ax.set_title(f'{prop_label} vs Temperature')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        filename = prop_col.lower().replace('_', '_') + '.png'
        plt.tight_layout()
        plt.savefig(FIG_DIR / filename, dpi=DPI)
        plt.close()
        print(f"Created: {filename}")


def plot_thermal_cycling():
    """Plot thermal cycling degradation"""
    
    # Rapid cycling
    df_rapid = pd.read_csv(DATA_DIR / '02_experimental_test_data' / 'thermal_cycling_rapid.csv', comment='#')
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # OCV vs cycle
    axes[0, 0].plot(df_rapid['Cycle_Number'], df_rapid['OCV_V'], 'o-', color=COLORS[0], markersize=4)
    axes[0, 0].set_xlabel('Cycle Number')
    axes[0, 0].set_ylabel('OCV (V)')
    axes[0, 0].set_title('Open Circuit Voltage Degradation (Rapid Cycling)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # ASR vs cycle
    axes[0, 1].plot(df_rapid['Cycle_Number'], df_rapid['ASR_Ohm_cm2'], 's-', color=COLORS[1], markersize=4)
    axes[0, 1].set_xlabel('Cycle Number')
    axes[0, 1].set_ylabel('ASR (Ω·cm²)')
    axes[0, 1].set_title('Area Specific Resistance Evolution (Rapid Cycling)')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Power density vs cycle
    axes[1, 0].plot(df_rapid['Cycle_Number'], df_rapid['Power_Density_W_per_cm2'], '^-', color=COLORS[2], markersize=4)
    axes[1, 0].set_xlabel('Cycle Number')
    axes[1, 0].set_ylabel('Power Density (W/cm²)')
    axes[1, 0].set_title('Power Density Degradation (Rapid Cycling)')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Crack count vs cycle
    axes[1, 1].plot(df_rapid['Cycle_Number'], df_rapid['Crack_Count'], 'd-', color=COLORS[3], markersize=4)
    axes[1, 1].set_xlabel('Cycle Number')
    axes[1, 1].set_ylabel('Crack Count')
    axes[1, 1].set_title('Crack Formation (Rapid Cycling)')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'thermal_cycling_rapid_degradation.png', dpi=DPI)
    plt.close()
    print("Created: thermal_cycling_rapid_degradation.png")
    
    # Compare rapid vs slow cycling
    df_slow = pd.read_csv(DATA_DIR / '02_experimental_test_data' / 'thermal_cycling_slow.csv', comment='#')
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(df_rapid['Cycle_Number'], df_rapid['OCV_V'], 'o-', label='Rapid (20°C/min)', markersize=4, color=COLORS[0])
    ax.plot(df_slow['Cycle_Number'], df_slow['OCV_V'], 's-', label='Slow (5°C/min)', markersize=3, color=COLORS[1])
    ax.set_xlabel('Cycle Number')
    ax.set_ylabel('OCV (V)')
    ax.set_title('OCV Degradation: Rapid vs Slow Thermal Cycling')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'thermal_cycling_comparison.png', dpi=DPI)
    plt.close()
    print("Created: thermal_cycling_comparison.png")


def plot_vi_curves():
    """Plot V-I and power curves at different temperatures"""
    
    df = pd.read_csv(DATA_DIR / '03_electrochemical_performance' / 'vi_curves.csv', comment='#')
    
    temps = [600, 650, 700, 750, 800]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # V-I curves
    for i, T in enumerate(temps):
        col_name = f'Voltage_V_{T}C'
        ax1.plot(df['Current_Density_A_per_cm2'], df[col_name], 
                label=f'{T}°C', linewidth=2, color=COLORS[i % len(COLORS)])
    
    ax1.set_xlabel('Current Density (A/cm²)')
    ax1.set_ylabel('Voltage (V)')
    ax1.set_title('V-I Characteristics at Different Temperatures')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Power curves
    for i, T in enumerate(temps):
        col_name = f'Power_Density_W_per_cm2_{T}C'
        ax2.plot(df['Current_Density_A_per_cm2'], df[col_name], 
                label=f'{T}°C', linewidth=2, color=COLORS[i % len(COLORS)])
    
    ax2.set_xlabel('Current Density (A/cm²)')
    ax2.set_ylabel('Power Density (W/cm²)')
    ax2.set_title('Power Density vs Current Density')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'vi_curves.png', dpi=DPI)
    plt.close()
    print("Created: vi_curves.png")


def plot_eis_nyquist():
    """Plot Nyquist plots from EIS data"""
    
    df = pd.read_csv(DATA_DIR / '03_electrochemical_performance' / 'eis_impedance.csv', comment='#')
    
    temps = df['Temperature_C'].unique()
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    for i, T in enumerate(sorted(temps)):
        df_temp = df[df['Temperature_C'] == T]
        ax.plot(df_temp['Z_Real_Ohm_cm2'], -df_temp['Z_Imaginary_Ohm_cm2'], 
               'o-', label=f'{int(T)}°C', markersize=3, color=COLORS[i % len(COLORS)])
    
    ax.set_xlabel('Z\' (Real) [Ω·cm²]')
    ax.set_ylabel('-Z\'\' (Imaginary) [Ω·cm²]')
    ax.set_title('Nyquist Plot - Electrochemical Impedance Spectroscopy')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal', adjustable='box')
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'eis_nyquist.png', dpi=DPI)
    plt.close()
    print("Created: eis_nyquist.png")


def plot_asr_degradation():
    """Plot ASR degradation over time"""
    
    df = pd.read_csv(DATA_DIR / '03_electrochemical_performance' / 'asr_degradation.csv', comment='#')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    conditions = df['Condition'].unique()
    for i, cond in enumerate(conditions):
        df_cond = df[df['Condition'] == cond]
        ax.plot(df_cond['Time_hours'], df_cond['ASR_Ohm_cm2'], 
               'o-', label=cond.replace('_', ' ').title(), 
               markersize=3, color=COLORS[i % len(COLORS)])
    
    ax.set_xlabel('Time (hours)')
    ax.set_ylabel('ASR (Ω·cm²)')
    ax.set_title('Area Specific Resistance Degradation Over Time')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'asr_degradation.png', dpi=DPI)
    plt.close()
    print("Created: asr_degradation.png")


def plot_temperature_distribution():
    """Plot temperature distribution contour from simulation"""
    
    df = pd.read_csv(DATA_DIR / '05_simulation_data' / 'temperature_distribution.csv', comment='#')
    
    # Get data for middle layer (z ~ 0.5)
    df_layer = df[df['Z_mm'] == 0.5]
    
    # Create pivot table for contour plot
    pivot = df_layer.pivot(index='Y_mm', columns='X_mm', values='Temperature_C')
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    contour = ax.contourf(pivot.columns, pivot.index, pivot.values, levels=20, cmap='hot')
    cbar = plt.colorbar(contour, ax=ax)
    cbar.set_label('Temperature (°C)')
    
    ax.set_xlabel('X Position (mm)')
    ax.set_ylabel('Y Position (mm)')
    ax.set_title('Temperature Distribution in SOFC Cell (Mid-plane)')
    ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'temperature_distribution.png', dpi=DPI)
    plt.close()
    print("Created: temperature_distribution.png")


def plot_stress_distribution():
    """Plot stress distribution from simulation"""
    
    df = pd.read_csv(DATA_DIR / '05_simulation_data' / 'stress_distribution.csv', comment='#')
    
    # Plot Von Mises stress for electrolyte layer
    df_electrolyte = df[df['Component'] == 'electrolyte']
    
    if len(df_electrolyte) > 0:
        pivot = df_electrolyte.pivot(index='Y_mm', columns='X_mm', values='Von_Mises_MPa')
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        contour = ax.contourf(pivot.columns, pivot.index, pivot.values, levels=20, cmap='viridis')
        cbar = plt.colorbar(contour, ax=ax)
        cbar.set_label('Von Mises Stress (MPa)')
        
        ax.set_xlabel('X Position (mm)')
        ax.set_ylabel('Y Position (mm)')
        ax.set_title('Von Mises Stress Distribution (Electrolyte Layer)')
        ax.set_aspect('equal')
        
        plt.tight_layout()
        plt.savefig(FIG_DIR / 'stress_distribution.png', dpi=DPI)
        plt.close()
        print("Created: stress_distribution.png")


def plot_failure_probability():
    """Plot failure probability heatmap"""
    
    df = pd.read_csv(DATA_DIR / '05_simulation_data' / 'failure_probability.csv', comment='#')
    
    # Plot for electrolyte (typically most critical)
    df_electrolyte = df[df['Component'] == 'electrolyte']
    
    if len(df_electrolyte) > 0:
        pivot = df_electrolyte.pivot(index='Y_mm', columns='X_mm', values='Failure_Probability')
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        im = ax.imshow(pivot.values, cmap='Reds', aspect='auto', origin='lower',
                      extent=[pivot.columns.min(), pivot.columns.max(), 
                             pivot.index.min(), pivot.index.max()])
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Failure Probability')
        
        ax.set_xlabel('X Position (mm)')
        ax.set_ylabel('Y Position (mm)')
        ax.set_title('Weibull Failure Probability Distribution (Electrolyte)')
        
        plt.tight_layout()
        plt.savefig(FIG_DIR / 'failure_probability_heatmap.png', dpi=DPI)
        plt.close()
        print("Created: failure_probability_heatmap.png")


def plot_stack_voltage():
    """Plot stack voltage over time"""
    
    df = pd.read_csv(DATA_DIR / '06_stack_level_data' / 'stack_voltage_cycling.csv', comment='#')
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Individual cell voltages
    for i in range(1, 6):
        col = f'Cell_{i}_Voltage_V'
        ax1.plot(df['Time_hours'], df[col], label=f'Cell {i}', linewidth=1.5)
    
    ax1.set_xlabel('Time (hours)')
    ax1.set_ylabel('Cell Voltage (V)')
    ax1.set_title('Individual Cell Voltages During Operation')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # Stack voltage and temperature
    ax2_temp = ax2.twinx()
    
    line1 = ax2.plot(df['Time_hours'], df['Stack_Voltage_V'], 
                     color=COLORS[0], linewidth=2, label='Stack Voltage')
    line2 = ax2_temp.plot(df['Time_hours'], df['Temperature_C'], 
                          color=COLORS[1], linewidth=1.5, linestyle='--', label='Temperature')
    
    ax2.set_xlabel('Time (hours)')
    ax2.set_ylabel('Stack Voltage (V)', color=COLORS[0])
    ax2_temp.set_ylabel('Temperature (°C)', color=COLORS[1])
    ax2.set_title('Stack Voltage and Temperature')
    ax2.tick_params(axis='y', labelcolor=COLORS[0])
    ax2_temp.tick_params(axis='y', labelcolor=COLORS[1])
    ax2.grid(True, alpha=0.3)
    
    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc='upper right')
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'stack_voltage_cycling.png', dpi=DPI)
    plt.close()
    print("Created: stack_voltage_cycling.png")


def plot_porosity_comparison():
    """Plot porosity measurements comparison"""
    
    df = pd.read_csv(DATA_DIR / '04_microstructural_data' / 'porosity_measurements.csv', comment='#')
    
    # Group by material and condition
    materials = df['Material'].unique()
    conditions = ['as-sintered', 'after_500h', 'after_2000h', 'after_cycling']
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(materials))
    width = 0.2
    
    for i, cond in enumerate(conditions):
        df_cond = df[df['Condition'] == cond]
        porosities = [df_cond[df_cond['Material'] == mat]['Porosity_percent'].mean() 
                     for mat in materials]
        ax.bar(x + i * width, porosities, width, label=cond.replace('_', ' ').title(), 
               color=COLORS[i % len(COLORS)])
    
    ax.set_xlabel('Material')
    ax.set_ylabel('Porosity (%)')
    ax.set_title('Porosity Evolution Under Different Conditions')
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(materials)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'porosity_comparison.png', dpi=DPI)
    plt.close()
    print("Created: porosity_comparison.png")


def plot_grain_size():
    """Plot grain size evolution"""
    
    df = pd.read_csv(DATA_DIR / '04_microstructural_data' / 'grain_size_data.csv', comment='#')
    
    materials = df['Material'].unique()
    conditions = ['as-sintered', 'after_500h', 'after_2000h', 'after_cycling']
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(conditions))
    width = 0.15
    
    for i, mat in enumerate(materials):
        df_mat = df[df['Material'] == mat]
        sizes = [df_mat[df_mat['Condition'] == cond]['Grain_Size_um'].mean() 
                for cond in conditions]
        ax.bar(x + i * width, sizes, width, label=mat, color=COLORS[i % len(COLORS)])
    
    ax.set_xlabel('Condition')
    ax.set_ylabel('Grain Size (μm)')
    ax.set_title('Grain Size Evolution During Operation')
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels([c.replace('_', ' ').title() for c in conditions], rotation=15)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'grain_size_evolution.png', dpi=DPI)
    plt.close()
    print("Created: grain_size_evolution.png")


def plot_isothermal_aging():
    """Plot isothermal aging results"""
    
    df = pd.read_csv(DATA_DIR / '02_experimental_test_data' / 'isothermal_aging.csv', comment='#')
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # ASR vs time
    axes[0, 0].plot(df['Time_hours'], df['ASR_Ohm_cm2'], color=COLORS[0], linewidth=2)
    axes[0, 0].set_xlabel('Time (hours)')
    axes[0, 0].set_ylabel('ASR (Ω·cm²)')
    axes[0, 0].set_title('ASR Evolution at 800°C')
    axes[0, 0].grid(True, alpha=0.3)
    
    # OCV vs time
    axes[0, 1].plot(df['Time_hours'], df['OCV_V'], color=COLORS[1], linewidth=2)
    axes[0, 1].set_xlabel('Time (hours)')
    axes[0, 1].set_ylabel('OCV (V)')
    axes[0, 1].set_title('OCV Stability at 800°C')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Mass change vs time
    axes[1, 0].plot(df['Time_hours'], df['Mass_Change_percent'], color=COLORS[2], linewidth=2)
    axes[1, 0].set_xlabel('Time (hours)')
    axes[1, 0].set_ylabel('Mass Change (%)')
    axes[1, 0].set_title('Mass Change During Aging')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Conductivity vs time
    axes[1, 1].plot(df['Time_hours'], df['Conductivity_S_per_cm'], color=COLORS[3], linewidth=2)
    axes[1, 1].set_xlabel('Time (hours)')
    axes[1, 1].set_ylabel('Conductivity (S/cm)')
    axes[1, 1].set_title('Conductivity Degradation')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'isothermal_aging.png', dpi=DPI)
    plt.close()
    print("Created: isothermal_aging.png")


def main():
    """Generate all figures"""
    print("=" * 70)
    print("Generating Publication-Quality Figures for SOFC Dataset")
    print("=" * 70)
    
    print("\n1. Material properties vs temperature...")
    plot_material_properties()
    
    print("\n2. Thermal cycling degradation...")
    plot_thermal_cycling()
    
    print("\n3. V-I and power curves...")
    plot_vi_curves()
    
    print("\n4. EIS Nyquist plots...")
    plot_eis_nyquist()
    
    print("\n5. ASR degradation...")
    plot_asr_degradation()
    
    print("\n6. Temperature distribution...")
    plot_temperature_distribution()
    
    print("\n7. Stress distribution...")
    plot_stress_distribution()
    
    print("\n8. Failure probability...")
    plot_failure_probability()
    
    print("\n9. Stack voltage cycling...")
    plot_stack_voltage()
    
    print("\n10. Porosity comparison...")
    plot_porosity_comparison()
    
    print("\n11. Grain size evolution...")
    plot_grain_size()
    
    print("\n12. Isothermal aging...")
    plot_isothermal_aging()
    
    print("\n" + "=" * 70)
    print(f"All figures saved to: {FIG_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
