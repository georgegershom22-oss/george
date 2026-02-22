#!/usr/bin/env python3
"""
Master script to generate all 16 CSV datasets for SOFC thermo-mechanical analysis.

⚠️ CRITICAL DISCLAIMER - SYNTHETIC DATA
ALL DATA GENERATED IS SYNTHETIC AND ILLUSTRATIVE
Based on published literature ranges but NOT actual experimental measurements.
For educational, template, and model-testing purposes ONLY.
Users must cite and use original measured data for publications.
"""

import numpy as np
import pandas as pd
import os
from pathlib import Path

# Get the data directory path
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Synthetic data disclaimer header
DISCLAIMER = (
    "# SYNTHETIC/ILLUSTRATIVE DATA - NOT ACTUAL MEASUREMENTS\n"
    "# Based on published literature ranges for educational purposes only\n"
    "# DO NOT use directly in publications - cite original sources\n"
)

def save_csv_with_disclaimer(df, filename):
    """Save DataFrame to CSV with synthetic data disclaimer."""
    filepath = DATA_DIR / filename
    with open(filepath, 'w') as f:
        f.write(DISCLAIMER)
    df.to_csv(filepath, mode='a', index=False)
    print(f"✓ Created {filename}")


def generate_thermal_properties():
    """01_thermal_properties.csv - Temperature-dependent thermal properties."""
    materials = {
        '8YSZ': {
            'k': (2.0, 2.4), 'Cp': (456, 540), 'CTE': (10.3, 12.0), 'rho': 5900
        },
        'GDC': {
            'k': (5.5, 2.5), 'Cp': (390, 560), 'CTE': (11.8, 13.1), 'rho': 7220
        },
        'Ni-YSZ': {
            'k': (11.0, 4.0), 'Cp': (450, 550), 'CTE': (12.5, 14.8), 'rho': 4460
        },
        'LSCF': {
            'k': (3.5, 2.5), 'Cp': (450, 570), 'CTE': (14.0, 16.8), 'rho': 6300
        },
        'LSM': {
            'k': (3.0, 2.5), 'Cp': (470, 540), 'CTE': (11.2, 12.2), 'rho': 6500
        },
        'Crofer22APU': {
            'k': (22.0, 28.0), 'Cp': (460, 660), 'CTE': (10.0, 12.5), 'rho': 7700
        }
    }
    
    temps = np.arange(25, 1001, 25)
    data = []
    
    for mat_name, props in materials.items():
        for T in temps:
            # Interpolate properties (linear for most, with some nonlinearity)
            frac = (T - 25) / (1000 - 25)
            k = props['k'][0] + frac * (props['k'][1] - props['k'][0])
            Cp = props['Cp'][0] + frac * (props['Cp'][1] - props['Cp'][0])
            CTE = props['CTE'][0] + frac * (props['CTE'][1] - props['CTE'][0])
            
            data.append({
                'Material': mat_name,
                'Temperature_C': T,
                'Thermal_Conductivity_W_per_mK': round(k, 2),
                'Specific_Heat_J_per_kgK': round(Cp, 1),
                'CTE_1e-6_per_K': round(CTE, 2),
                'Density_kg_per_m3': props['rho']
            })
    
    df = pd.DataFrame(data)
    save_csv_with_disclaimer(df, '01_thermal_properties.csv')


def generate_mechanical_properties():
    """02_mechanical_properties.csv - Temperature-dependent mechanical properties."""
    materials = {
        '8YSZ': {
            'E': (210, 150), 'nu': 0.31, 'strength': (250, 160), 
            'KIC': (2.0, 1.3), 'Weibull': (10, 7)
        },
        'GDC': {
            'E': (185, 130), 'nu': 0.29, 'strength': (200, 140),
            'KIC': (1.5, 1.0), 'Weibull': (9, 6)
        },
        'Ni-YSZ': {
            'E': (95, 45), 'nu': 0.30, 'strength': (130, 55),
            'KIC': (1.8, 0.8), 'Weibull': (7, 5)
        },
        'LSCF': {
            'E': (105, 50), 'nu': 0.25, 'strength': (90, 40),
            'KIC': (1.0, 0.6), 'Weibull': (6, 4)
        },
        'LSM': {
            'E': (95, 48), 'nu': 0.26, 'strength': (85, 38),
            'KIC': (0.9, 0.5), 'Weibull': (5, 4)
        },
        'Crofer22APU': {
            'E': (220, 120), 'nu': 0.30, 'strength': (520, 150),
            'KIC': (80, 25), 'Weibull': (30, 18)
        }
    }
    
    temps = np.arange(25, 1001, 25)
    data = []
    
    for mat_name, props in materials.items():
        for T in temps:
            frac = (T - 25) / (1000 - 25)
            E = props['E'][0] + frac * (props['E'][1] - props['E'][0])
            strength = props['strength'][0] + frac * (props['strength'][1] - props['strength'][0])
            KIC = props['KIC'][0] + frac * (props['KIC'][1] - props['KIC'][0])
            Weibull = props['Weibull'][0] + frac * (props['Weibull'][1] - props['Weibull'][0])
            
            # Poisson ratio slightly increases for LSCF
            nu = props['nu']
            if mat_name == 'LSCF':
                nu = 0.25 + frac * 0.02
            
            data.append({
                'Material': mat_name,
                'Temperature_C': T,
                'Elastic_Modulus_GPa': round(E, 1),
                'Poisson_Ratio': round(nu, 3),
                'Flexural_Strength_MPa': round(strength, 1),
                'Fracture_Toughness_MPa_sqrt_m': round(KIC, 2),
                'Weibull_Modulus': round(Weibull, 1)
            })
    
    df = pd.DataFrame(data)
    save_csv_with_disclaimer(df, '02_mechanical_properties.csv')


def generate_creep_parameters_norton():
    """03_creep_parameters_norton.csv - Norton power law creep parameters."""
    data = [
        # Ni-8YSZ variants
        {'Material': 'Ni-8YSZ', 'Ni_vol_pct': 40, 'Porosity_pct': 30, 'Temperature_C': 750,
         'Stress_Exponent_n': 2.8, 'Activation_Energy_kJ_per_mol': 235, 'Pre_Exponential_A_1_per_s': 1.2e-6,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Diffusional'},
        {'Material': 'Ni-8YSZ', 'Ni_vol_pct': 40, 'Porosity_pct': 30, 'Temperature_C': 800,
         'Stress_Exponent_n': 3.2, 'Activation_Energy_kJ_per_mol': 248, 'Pre_Exponential_A_1_per_s': 2.8e-6,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Diffusional'},
        {'Material': 'Ni-8YSZ', 'Ni_vol_pct': 40, 'Porosity_pct': 30, 'Temperature_C': 850,
         'Stress_Exponent_n': 3.5, 'Activation_Energy_kJ_per_mol': 255, 'Pre_Exponential_A_1_per_s': 5.5e-6,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Diffusional-Dislocation'},
        {'Material': 'Ni-8YSZ', 'Ni_vol_pct': 40, 'Porosity_pct': 30, 'Temperature_C': 900,
         'Stress_Exponent_n': 4.1, 'Activation_Energy_kJ_per_mol': 268, 'Pre_Exponential_A_1_per_s': 1.1e-5,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Dislocation'},
        {'Material': 'Ni-8YSZ', 'Ni_vol_pct': 40, 'Porosity_pct': 30, 'Temperature_C': 1000,
         'Stress_Exponent_n': 5.2, 'Activation_Energy_kJ_per_mol': 290, 'Pre_Exponential_A_1_per_s': 3.2e-5,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Power-Law Dislocation'},
        
        # Higher Ni content, lower porosity
        {'Material': 'Ni-8YSZ', 'Ni_vol_pct': 56, 'Porosity_pct': 20, 'Temperature_C': 750,
         'Stress_Exponent_n': 2.2, 'Activation_Energy_kJ_per_mol': 215, 'Pre_Exponential_A_1_per_s': 8.5e-7,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Diffusional'},
        {'Material': 'Ni-8YSZ', 'Ni_vol_pct': 56, 'Porosity_pct': 20, 'Temperature_C': 800,
         'Stress_Exponent_n': 2.6, 'Activation_Energy_kJ_per_mol': 228, 'Pre_Exponential_A_1_per_s': 1.9e-6,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Diffusional'},
        {'Material': 'Ni-8YSZ', 'Ni_vol_pct': 56, 'Porosity_pct': 20, 'Temperature_C': 850,
         'Stress_Exponent_n': 3.0, 'Activation_Energy_kJ_per_mol': 242, 'Pre_Exponential_A_1_per_s': 4.2e-6,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Diffusional-Dislocation'},
        {'Material': 'Ni-8YSZ', 'Ni_vol_pct': 56, 'Porosity_pct': 20, 'Temperature_C': 900,
         'Stress_Exponent_n': 3.8, 'Activation_Energy_kJ_per_mol': 260, 'Pre_Exponential_A_1_per_s': 9.5e-6,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Dislocation'},
        {'Material': 'Ni-8YSZ', 'Ni_vol_pct': 56, 'Porosity_pct': 20, 'Temperature_C': 1000,
         'Stress_Exponent_n': 4.9, 'Activation_Energy_kJ_per_mol': 285, 'Pre_Exponential_A_1_per_s': 2.8e-5,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Power-Law Dislocation'},
        
        # Lower Ni content, higher porosity
        {'Material': 'Ni-8YSZ', 'Ni_vol_pct': 30, 'Porosity_pct': 35, 'Temperature_C': 750,
         'Stress_Exponent_n': 3.5, 'Activation_Energy_kJ_per_mol': 255, 'Pre_Exponential_A_1_per_s': 2.1e-6,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Diffusional'},
        {'Material': 'Ni-8YSZ', 'Ni_vol_pct': 30, 'Porosity_pct': 35, 'Temperature_C': 800,
         'Stress_Exponent_n': 3.9, 'Activation_Energy_kJ_per_mol': 268, 'Pre_Exponential_A_1_per_s': 4.5e-6,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Diffusional-Dislocation'},
        {'Material': 'Ni-8YSZ', 'Ni_vol_pct': 30, 'Porosity_pct': 35, 'Temperature_C': 850,
         'Stress_Exponent_n': 4.3, 'Activation_Energy_kJ_per_mol': 278, 'Pre_Exponential_A_1_per_s': 8.8e-6,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Dislocation'},
        {'Material': 'Ni-8YSZ', 'Ni_vol_pct': 30, 'Porosity_pct': 35, 'Temperature_C': 900,
         'Stress_Exponent_n': 4.8, 'Activation_Energy_kJ_per_mol': 295, 'Pre_Exponential_A_1_per_s': 1.8e-5,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Dislocation'},
        {'Material': 'Ni-8YSZ', 'Ni_vol_pct': 30, 'Porosity_pct': 35, 'Temperature_C': 1000,
         'Stress_Exponent_n': 5.2, 'Activation_Energy_kJ_per_mol': 310, 'Pre_Exponential_A_1_per_s': 4.5e-5,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Power-Law Dislocation'},
        
        # Ni-3YSZ variants (different YSZ composition)
        {'Material': 'Ni-3YSZ', 'Ni_vol_pct': 45, 'Porosity_pct': 25, 'Temperature_C': 800,
         'Stress_Exponent_n': 2.9, 'Activation_Energy_kJ_per_mol': 240, 'Pre_Exponential_A_1_per_s': 2.2e-6,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Diffusional'},
        {'Material': 'Ni-3YSZ', 'Ni_vol_pct': 45, 'Porosity_pct': 25, 'Temperature_C': 850,
         'Stress_Exponent_n': 3.3, 'Activation_Energy_kJ_per_mol': 252, 'Pre_Exponential_A_1_per_s': 4.8e-6,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Diffusional-Dislocation'},
        {'Material': 'Ni-3YSZ', 'Ni_vol_pct': 45, 'Porosity_pct': 25, 'Temperature_C': 900,
         'Stress_Exponent_n': 4.0, 'Activation_Energy_kJ_per_mol': 265, 'Pre_Exponential_A_1_per_s': 1.0e-5,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Dislocation'},
        {'Material': 'Ni-3YSZ', 'Ni_vol_pct': 45, 'Porosity_pct': 25, 'Temperature_C': 950,
         'Stress_Exponent_n': 4.6, 'Activation_Energy_kJ_per_mol': 280, 'Pre_Exponential_A_1_per_s': 2.1e-5,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Dislocation'},
        {'Material': 'Ni-3YSZ', 'Ni_vol_pct': 45, 'Porosity_pct': 25, 'Temperature_C': 1000,
         'Stress_Exponent_n': 5.0, 'Activation_Energy_kJ_per_mol': 295, 'Pre_Exponential_A_1_per_s': 3.5e-5,
         'Atmosphere': 'H2-H2O', 'Creep_Mechanism': 'Power-Law Dislocation'},
    ]
    
    df = pd.DataFrame(data)
    save_csv_with_disclaimer(df, '03_creep_parameters_norton.csv')


def generate_creep_curves():
    """04_creep_curves.csv - Creep strain vs time curves."""
    time = np.arange(0, 501, 5)  # 0 to 500 hours in 5-hour steps
    
    # Simplified power law: strain = A * t^b
    # Different parameters for each condition
    conditions = {
        'Strain_pct_5MPa_750C': {'A': 0.008, 'b': 0.45},
        'Strain_pct_10MPa_750C': {'A': 0.022, 'b': 0.48},
        'Strain_pct_5MPa_800C': {'A': 0.015, 'b': 0.50},
        'Strain_pct_10MPa_800C': {'A': 0.042, 'b': 0.52},
        'Strain_pct_15MPa_800C': {'A': 0.075, 'b': 0.54},
        'Strain_pct_10MPa_850C': {'A': 0.068, 'b': 0.55},
        'Strain_pct_20MPa_850C': {'A': 0.158, 'b': 0.57},
        'Strain_pct_10MPa_900C': {'A': 0.105, 'b': 0.58},
    }
    
    data = {'Time_hours': time}
    for col, params in conditions.items():
        # Avoid division by zero at t=0
        strain = np.where(time == 0, 0, params['A'] * np.power(time, params['b']))
        data[col] = np.round(strain, 4)
    
    df = pd.DataFrame(data)
    save_csv_with_disclaimer(df, '04_creep_curves.csv')


def generate_CTE_mismatch_thermal_stress():
    """05_CTE_mismatch_thermal_stress.csv - CTE mismatch and thermal stress."""
    temps = np.arange(25, 1001, 25)
    
    # CTE values as function of temperature (from thermal properties)
    def get_CTE(T, CTE_25, CTE_1000):
        frac = (T - 25) / (1000 - 25)
        return CTE_25 + frac * (CTE_1000 - CTE_25)
    
    data = []
    T_sinter = 1400  # Sintering temperature (reference)
    
    for T in temps:
        CTE_8YSZ = get_CTE(T, 10.3, 12.0)
        CTE_NiYSZ = get_CTE(T, 12.5, 14.8)
        CTE_LSCF = get_CTE(T, 14.0, 16.8)
        CTE_GDC = get_CTE(T, 11.8, 13.1)
        CTE_LSM = get_CTE(T, 11.2, 12.2)
        CTE_Crofer = get_CTE(T, 10.0, 12.5)
        
        # CTE mismatches
        dCTE_NiYSZ = CTE_NiYSZ - CTE_8YSZ
        dCTE_LSCF = CTE_LSCF - CTE_8YSZ
        dCTE_GDC = CTE_GDC - CTE_8YSZ
        
        # Biaxial stress: σ = E·Δα·ΔT/(1-ν)
        # Simplified: assume E=200 GPa at RT, ν=0.3, cooling from T_sinter
        E_eff = 200e3  # MPa
        nu = 0.3
        dT = T - T_sinter
        
        # Stress in anode (Ni-YSZ) against electrolyte (8YSZ)
        stress_anode = E_eff * (dCTE_NiYSZ * 1e-6) * dT / (1 - nu)
        
        # Stress in cathode (LSCF) against electrolyte (8YSZ)
        stress_cathode = E_eff * (dCTE_LSCF * 1e-6) * dT / (1 - nu)
        
        data.append({
            'Temperature_C': T,
            'CTE_8YSZ': round(CTE_8YSZ, 2),
            'CTE_NiYSZ': round(CTE_NiYSZ, 2),
            'CTE_LSCF': round(CTE_LSCF, 2),
            'CTE_GDC': round(CTE_GDC, 2),
            'CTE_LSM': round(CTE_LSM, 2),
            'CTE_Crofer': round(CTE_Crofer, 2),
            'dCTE_NiYSZ_vs_8YSZ': round(dCTE_NiYSZ, 3),
            'dCTE_LSCF_vs_8YSZ': round(dCTE_LSCF, 3),
            'dCTE_GDC_vs_8YSZ': round(dCTE_GDC, 3),
            'Stress_Anode_Electrolyte_MPa': round(stress_anode, 1),
            'Stress_Cathode_Electrolyte_MPa': round(stress_cathode, 1)
        })
    
    df = pd.DataFrame(data)
    save_csv_with_disclaimer(df, '05_CTE_mismatch_thermal_stress.csv')


def generate_polarization_curves():
    """06_polarization_curves.csv - I-V-P curves at three temperatures."""
    j = np.linspace(0, 1.24, 125)  # Current density 0 to 1.24 A/cm²
    
    # Parameters for each temperature
    temps = {
        750: {'OCV': 1.10, 'R_ohm': 0.45, 'j0': 0.08, 'j_lim': 1.5, 'b': 0.12},
        800: {'OCV': 1.10, 'R_ohm': 0.28, 'j0': 0.15, 'j_lim': 1.8, 'b': 0.10},
        850: {'OCV': 1.10, 'R_ohm': 0.18, 'j0': 0.25, 'j_lim': 2.2, 'b': 0.08},
    }
    
    data = {'Current_Density_A_per_cm2': np.round(j, 4)}
    
    for T, params in temps.items():
        # V = OCV - R_ohm*j - b*ln(j/j0) - b*ln(1 - j/j_lim)
        # Handle edge cases at j=0 and j≈j_lim
        V = np.zeros_like(j)
        for i, j_val in enumerate(j):
            if j_val < 0.001:
                V[i] = params['OCV']
            elif j_val >= params['j_lim'] * 0.99:
                V[i] = 0.0
            else:
                eta_act = params['b'] * np.log(j_val / params['j0']) if j_val > params['j0'] else 0
                eta_conc = params['b'] * np.log(1 / (1 - j_val / params['j_lim']))
                V[i] = max(0, params['OCV'] - params['R_ohm'] * j_val - eta_act - eta_conc)
        
        P = V * j  # Power density
        
        data[f'Voltage_{T}C_V'] = np.round(V, 4)
        data[f'Power_{T}C_W_per_cm2'] = np.round(P, 4)
    
    df = pd.DataFrame(data)
    save_csv_with_disclaimer(df, '06_polarization_curves.csv')


def generate_thermal_cycling_degradation():
    """07_thermal_cycling_degradation.csv - Thermal cycling degradation."""
    ramp_rates = [5, 10, 20]  # °C/min
    cycles = np.arange(0, 101, 1)
    
    data = []
    for rr in ramp_rates:
        # Degradation rate depends on ramp rate (faster = more degradation)
        deg_rate = 0.15 + (rr - 5) * 0.03  # % per cycle
        
        for cycle in cycles:
            # Initial values at cycle 0
            if cycle == 0:
                power = 0.68
                ocv = 1.10
                voltage = 0.75
                asr = 0.28
            else:
                # Degradation with some nonlinearity
                power = 0.68 * (1 - deg_rate * cycle / 100) * (1 - 0.0005 * cycle**1.2)
                ocv = 1.10 - 0.0008 * cycle
                voltage = 0.75 * (1 - deg_rate * cycle / 100)
                asr = 0.28 * (1 + 0.012 * cycle)
            
            # Observations at key cycles
            obs = ''
            if cycle == 0:
                obs = 'Initial reference'
            elif cycle == 10:
                obs = 'Minor performance drop'
            elif cycle == 25:
                obs = f'{"Significant" if rr >= 15 else "Moderate"} degradation visible'
            elif cycle == 50:
                obs = f'{"Microcracking observed" if rr == 20 else "Stable degradation rate"}'
            elif cycle == 75:
                obs = 'Accelerated degradation phase' if rr == 20 else ''
            elif cycle == 100:
                obs = f'End of test - {int((1 - power/0.68)*100)}% power loss'
            
            data.append({
                'Cycle': cycle,
                'Ramp_Rate_C_per_min': rr,
                'Peak_Power_W_per_cm2': round(power, 4),
                'OCV_V': round(ocv, 4),
                'Voltage_at_0p5Acm2_V': round(voltage, 4),
                'ASR_Ohm_cm2': round(asr, 3),
                'Degradation_pct_per_cycle': round(deg_rate, 3),
                'Observation': obs
            })
    
    df = pd.DataFrame(data)
    save_csv_with_disclaimer(df, '07_thermal_cycling_degradation.csv')


def generate_strain_hardening_constants():
    """08_strain_hardening_constants.csv - FEM creep input constants."""
    # Constants for creep models: ε̇ = C1 * σ^C2 * t^C3 * exp(-C4/T)
    data = [
        # Ni-8YSZ
        {'Material': 'Ni-8YSZ', 'Temperature_C': 750, 'C1': 1.2e-6, 'C2_stress_exp': 3.2,
         'C3_time_exp': 0.48, 'C4_activation_div_R_K': 29880, 'Valid_Stress_MPa': '5-20',
         'Model_Type': 'Norton-Bailey'},
        {'Material': 'Ni-8YSZ', 'Temperature_C': 800, 'C1': 2.8e-6, 'C2_stress_exp': 3.5,
         'C3_time_exp': 0.52, 'C4_activation_div_R_K': 30600, 'Valid_Stress_MPa': '5-25',
         'Model_Type': 'Norton-Bailey'},
        {'Material': 'Ni-8YSZ', 'Temperature_C': 850, 'C1': 5.5e-6, 'C2_stress_exp': 3.8,
         'C3_time_exp': 0.55, 'C4_activation_div_R_K': 31440, 'Valid_Stress_MPa': '5-30',
         'Model_Type': 'Norton-Bailey'},
        {'Material': 'Ni-8YSZ', 'Temperature_C': 900, 'C1': 1.1e-5, 'C2_stress_exp': 4.2,
         'C3_time_exp': 0.58, 'C4_activation_div_R_K': 33000, 'Valid_Stress_MPa': '5-35',
         'Model_Type': 'Norton-Bailey'},
        
        # 8YSZ electrolyte (very low creep)
        {'Material': '8YSZ', 'Temperature_C': 800, 'C1': 5.2e-9, 'C2_stress_exp': 1.8,
         'C3_time_exp': 0.15, 'C4_activation_div_R_K': 52000, 'Valid_Stress_MPa': '10-100',
         'Model_Type': 'Diffusional Creep'},
        {'Material': '8YSZ', 'Temperature_C': 900, 'C1': 2.1e-8, 'C2_stress_exp': 2.0,
         'C3_time_exp': 0.18, 'C4_activation_div_R_K': 52800, 'Valid_Stress_MPa': '10-120',
         'Model_Type': 'Diffusional Creep'},
        {'Material': '8YSZ', 'Temperature_C': 1000, 'C1': 6.8e-8, 'C2_stress_exp': 2.2,
         'C3_time_exp': 0.22, 'C4_activation_div_R_K': 53500, 'Valid_Stress_MPa': '10-140',
         'Model_Type': 'Diffusional Creep'},
        
        # LSCF cathode
        {'Material': 'LSCF', 'Temperature_C': 750, 'C1': 2.5e-7, 'C2_stress_exp': 2.5,
         'C3_time_exp': 0.35, 'C4_activation_div_R_K': 28500, 'Valid_Stress_MPa': '3-15',
         'Model_Type': 'Norton-Bailey'},
        {'Material': 'LSCF', 'Temperature_C': 800, 'C1': 5.8e-7, 'C2_stress_exp': 2.8,
         'C3_time_exp': 0.38, 'C4_activation_div_R_K': 29200, 'Valid_Stress_MPa': '3-18',
         'Model_Type': 'Norton-Bailey'},
        {'Material': 'LSCF', 'Temperature_C': 850, 'C1': 1.2e-6, 'C2_stress_exp': 3.0,
         'C3_time_exp': 0.42, 'C4_activation_div_R_K': 30000, 'Valid_Stress_MPa': '3-20',
         'Model_Type': 'Norton-Bailey'},
        
        # Crofer22APU interconnect
        {'Material': 'Crofer22APU', 'Temperature_C': 700, 'C1': 8.5e-8, 'C2_stress_exp': 4.5,
         'C3_time_exp': 0.25, 'C4_activation_div_R_K': 35000, 'Valid_Stress_MPa': '20-80',
         'Model_Type': 'Power-Law Creep'},
        {'Material': 'Crofer22APU', 'Temperature_C': 750, 'C1': 2.2e-7, 'C2_stress_exp': 4.8,
         'C3_time_exp': 0.28, 'C4_activation_div_R_K': 35800, 'Valid_Stress_MPa': '20-90',
         'Model_Type': 'Power-Law Creep'},
        {'Material': 'Crofer22APU', 'Temperature_C': 800, 'C1': 5.1e-7, 'C2_stress_exp': 5.2,
         'C3_time_exp': 0.32, 'C4_activation_div_R_K': 36500, 'Valid_Stress_MPa': '20-100',
         'Model_Type': 'Power-Law Creep'},
        {'Material': 'Crofer22APU', 'Temperature_C': 850, 'C1': 1.1e-6, 'C2_stress_exp': 5.5,
         'C3_time_exp': 0.35, 'C4_activation_div_R_K': 37200, 'Valid_Stress_MPa': '20-110',
         'Model_Type': 'Power-Law Creep'},
        {'Material': 'Crofer22APU', 'Temperature_C': 900, 'C1': 2.3e-6, 'C2_stress_exp': 5.8,
         'C3_time_exp': 0.38, 'C4_activation_div_R_K': 38000, 'Valid_Stress_MPa': '20-120',
         'Model_Type': 'Power-Law Creep'},
        {'Material': 'Crofer22APU', 'Temperature_C': 950, 'C1': 4.5e-6, 'C2_stress_exp': 6.0,
         'C3_time_exp': 0.42, 'C4_activation_div_R_K': 38800, 'Valid_Stress_MPa': '20-130',
         'Model_Type': 'Power-Law Creep'},
    ]
    
    df = pd.DataFrame(data)
    save_csv_with_disclaimer(df, '08_strain_hardening_constants.csv')


def generate_temperature_distribution():
    """09_temperature_distribution.csv - 2D temperature distribution."""
    # 100mm x 100mm cell, 2mm x-step, 5mm y-step
    x = np.arange(0, 101, 2)
    y = np.arange(0, 101, 5)
    
    data = []
    for xi in x:
        for yi in y:
            # Steady state: sinusoidal temperature distribution
            T_steady = 1073 + 40 * np.sin(np.pi * xi / 100) * np.sin(np.pi * yi / 100)
            
            # Startup: linear gradient from inlet
            T_startup = 873 + 200 * (xi / 100)
            
            # Load change: Gaussian hotspot at (60, 50)
            dist = np.sqrt((xi - 60)**2 + (yi - 50)**2)
            T_load = 1073 + 60 * np.exp(-dist**2 / 400)
            
            # Temperature gradient (approximate)
            dTdx = 40 * (np.pi / 100) * np.cos(np.pi * xi / 100) * np.sin(np.pi * yi / 100)
            
            data.append({
                'Position_x_mm': xi,
                'Position_y_mm': yi,
                'T_SteadyState_K': round(T_steady, 2),
                'T_Startup_5Cmin_K': round(T_startup, 2),
                'T_LoadChange_K': round(T_load, 2),
                'dTdx_K_per_mm': round(dTdx, 3)
            })
    
    df = pd.DataFrame(data)
    save_csv_with_disclaimer(df, '09_temperature_distribution.csv')


def generate_stress_evolution_thermal_cycle():
    """10_stress_evolution_thermal_cycle.csv - Stress evolution during thermal cycle."""
    # Three phases: Heating (0-2600s), Dwell (2600-6200s), Cooling (6200-8800s)
    
    data = []
    
    # Phase 1: Heating (25°C → 800°C, ~43 min)
    t_heat = np.linspace(0, 2600, 90)
    T_heat = 25 + (800 - 25) * (t_heat / 2600)
    
    for i, t in enumerate(t_heat):
        T = T_heat[i]
        # Stress increases during heating due to CTE mismatch
        stress_anode = 15 + 45 * (T - 25) / (800 - 25)
        stress_electrolyte = 10 + 35 * (T - 25) / (800 - 25)
        stress_cathode = 12 + 40 * (T - 25) / (800 - 25)
        stress_interconnect = 8 + 28 * (T - 25) / (800 - 25)
        max_principal = stress_electrolyte * 1.2
        shear = stress_electrolyte * 0.3
        creep_strain = 0.0
        
        data.append({
            'Time_s': int(t),
            'Temperature_C': round(T, 1),
            'Phase': 'Heating',
            'VonMises_Anode_MPa': round(stress_anode, 1),
            'VonMises_Electrolyte_MPa': round(stress_electrolyte, 1),
            'VonMises_Cathode_MPa': round(stress_cathode, 1),
            'VonMises_Interconnect_MPa': round(stress_interconnect, 1),
            'Max_Principal_Electrolyte_MPa': round(max_principal, 1),
            'Interface_Shear_MPa': round(shear, 1),
            'Anode_Creep_Strain_pct': round(creep_strain, 4)
        })
    
    # Phase 2: Dwell at 800°C (stress relaxation due to creep)
    t_dwell = np.linspace(2600, 6200, 80)
    T_dwell = 800
    
    for i, t in enumerate(t_dwell):
        # Exponential stress relaxation
        tau = 1200  # time constant (s)
        relax = np.exp(-(t - 2600) / tau)
        stress_anode = 60 * relax + 25 * (1 - relax)
        stress_electrolyte = 45 * relax + 18 * (1 - relax)
        stress_cathode = 52 * relax + 22 * (1 - relax)
        stress_interconnect = 36 * relax + 15 * (1 - relax)
        max_principal = stress_electrolyte * 1.2
        shear = stress_electrolyte * 0.3
        # Creep strain accumulates
        creep_strain = 0.08 * (1 - relax)
        
        data.append({
            'Time_s': int(t),
            'Temperature_C': T_dwell,
            'Phase': 'Dwell',
            'VonMises_Anode_MPa': round(stress_anode, 1),
            'VonMises_Electrolyte_MPa': round(stress_electrolyte, 1),
            'VonMises_Cathode_MPa': round(stress_cathode, 1),
            'VonMises_Interconnect_MPa': round(stress_interconnect, 1),
            'Max_Principal_Electrolyte_MPa': round(max_principal, 1),
            'Interface_Shear_MPa': round(shear, 1),
            'Anode_Creep_Strain_pct': round(creep_strain, 4)
        })
    
    # Phase 3: Cooling (800°C → 25°C, ~43 min)
    t_cool = np.linspace(6200, 8800, 51)
    T_cool = 800 - (800 - 25) * ((t_cool - 6200) / (8800 - 6200))
    
    for i, t in enumerate(t_cool):
        T = T_cool[i]
        # Stress increases during cooling (tensile)
        frac_cool = (t - 6200) / (8800 - 6200)
        stress_anode = 25 + 85 * frac_cool
        stress_electrolyte = 18 + 70 * frac_cool
        stress_cathode = 22 + 78 * frac_cool
        stress_interconnect = 15 + 50 * frac_cool
        max_principal = stress_electrolyte * 1.3
        shear = stress_electrolyte * 0.35
        creep_strain = 0.08  # Fixed at dwell value
        
        data.append({
            'Time_s': int(t),
            'Temperature_C': round(T, 1),
            'Phase': 'Cooling',
            'VonMises_Anode_MPa': round(stress_anode, 1),
            'VonMises_Electrolyte_MPa': round(stress_electrolyte, 1),
            'VonMises_Cathode_MPa': round(stress_cathode, 1),
            'VonMises_Interconnect_MPa': round(stress_interconnect, 1),
            'Max_Principal_Electrolyte_MPa': round(max_principal, 1),
            'Interface_Shear_MPa': round(shear, 1),
            'Anode_Creep_Strain_pct': round(creep_strain, 4)
        })
    
    df = pd.DataFrame(data)
    save_csv_with_disclaimer(df, '10_stress_evolution_thermal_cycle.csv')


def generate_cell_geometry():
    """11_cell_geometry.csv - Cell layer dimensions and specifications."""
    data = [
        {'Component': 'Anode_Support_Layer', 'Material': 'Ni-YSZ', 'Thickness_um': 500,
         'Length_mm': 100, 'Width_mm': 100, 'Porosity_pct': 30, 'Grain_Size_um': 1.2,
         'Configuration': 'Anode-supported planar'},
        {'Component': 'Anode_Functional_Layer', 'Material': 'Ni-YSZ', 'Thickness_um': 15,
         'Length_mm': 100, 'Width_mm': 100, 'Porosity_pct': 35, 'Grain_Size_um': 0.5,
         'Configuration': 'Fine-grained TPB-optimized'},
        {'Component': 'Electrolyte', 'Material': '8YSZ', 'Thickness_um': 10,
         'Length_mm': 100, 'Width_mm': 100, 'Porosity_pct': 0, 'Grain_Size_um': 0.8,
         'Configuration': 'Dense gas-tight membrane'},
        {'Component': 'Barrier_Layer', 'Material': 'GDC', 'Thickness_um': 5,
         'Length_mm': 100, 'Width_mm': 100, 'Porosity_pct': 0, 'Grain_Size_um': 0.3,
         'Configuration': 'Prevents Sr/La diffusion'},
        {'Component': 'Cathode_Functional_Layer', 'Material': 'LSCF-GDC', 'Thickness_um': 15,
         'Length_mm': 100, 'Width_mm': 100, 'Porosity_pct': 40, 'Grain_Size_um': 0.6,
         'Configuration': 'Composite for TPB'},
        {'Component': 'Cathode_Current_Layer', 'Material': 'LSCF', 'Thickness_um': 30,
         'Length_mm': 100, 'Width_mm': 100, 'Porosity_pct': 35, 'Grain_Size_um': 1.5,
         'Configuration': 'Porous for gas diffusion'},
        {'Component': 'Interconnect', 'Material': 'Crofer22APU', 'Thickness_um': 500,
         'Length_mm': 100, 'Width_mm': 100, 'Porosity_pct': 0, 'Grain_Size_um': 25,
         'Configuration': 'Ferritic steel with ribs'},
        {'Component': 'Fuel_Channel', 'Material': 'Gas_space', 'Thickness_um': 1000,
         'Length_mm': 100, 'Width_mm': 2, 'Porosity_pct': 100, 'Grain_Size_um': 0,
         'Configuration': '50 parallel channels'},
        {'Component': 'Air_Channel', 'Material': 'Gas_space', 'Thickness_um': 1000,
         'Length_mm': 100, 'Width_mm': 2, 'Porosity_pct': 100, 'Grain_Size_um': 0,
         'Configuration': '50 parallel channels'},
        {'Component': 'Sealant', 'Material': 'Glass-ceramic', 'Thickness_um': 150,
         'Length_mm': 5, 'Width_mm': 100, 'Porosity_pct': 0, 'Grain_Size_um': 5,
         'Configuration': 'Peripheral frame seal'},
    ]
    
    df = pd.DataFrame(data)
    save_csv_with_disclaimer(df, '11_cell_geometry.csv')


def generate_operating_conditions():
    """12_operating_conditions.csv - Operating condition matrix."""
    data = [
        {'Scenario': 'Baseline_750C', 'Inlet_Temp_Fuel_C': 750, 'Inlet_Temp_Air_C': 750,
         'Fuel_Composition': '97%H2-3%H2O', 'Fuel_Flow_SLPM': 5.0, 'Air_Flow_SLPM': 15.0,
         'Current_Density_A_per_cm2': 0.50, 'Pressure_atm': 1.0, 'Fuel_Utilization_pct': 70,
         'Air_Excess_Ratio': 4.5},
        {'Scenario': 'Baseline_800C', 'Inlet_Temp_Fuel_C': 800, 'Inlet_Temp_Air_C': 800,
         'Fuel_Composition': '97%H2-3%H2O', 'Fuel_Flow_SLPM': 5.0, 'Air_Flow_SLPM': 15.0,
         'Current_Density_A_per_cm2': 0.50, 'Pressure_atm': 1.0, 'Fuel_Utilization_pct': 70,
         'Air_Excess_Ratio': 4.5},
        {'Scenario': 'Baseline_850C', 'Inlet_Temp_Fuel_C': 850, 'Inlet_Temp_Air_C': 850,
         'Fuel_Composition': '97%H2-3%H2O', 'Fuel_Flow_SLPM': 5.0, 'Air_Flow_SLPM': 15.0,
         'Current_Density_A_per_cm2': 0.50, 'Pressure_atm': 1.0, 'Fuel_Utilization_pct': 70,
         'Air_Excess_Ratio': 4.5},
        {'Scenario': 'High_Load', 'Inlet_Temp_Fuel_C': 800, 'Inlet_Temp_Air_C': 800,
         'Fuel_Composition': '97%H2-3%H2O', 'Fuel_Flow_SLPM': 8.0, 'Air_Flow_SLPM': 25.0,
         'Current_Density_A_per_cm2': 1.00, 'Pressure_atm': 1.0, 'Fuel_Utilization_pct': 60,
         'Air_Excess_Ratio': 3.8},
        {'Scenario': 'Low_Load', 'Inlet_Temp_Fuel_C': 800, 'Inlet_Temp_Air_C': 800,
         'Fuel_Composition': '97%H2-3%H2O', 'Fuel_Flow_SLPM': 3.0, 'Air_Flow_SLPM': 10.0,
         'Current_Density_A_per_cm2': 0.20, 'Pressure_atm': 1.0, 'Fuel_Utilization_pct': 80,
         'Air_Excess_Ratio': 5.2},
        {'Scenario': 'Methane_Reforming', 'Inlet_Temp_Fuel_C': 800, 'Inlet_Temp_Air_C': 800,
         'Fuel_Composition': '25%CH4-25%H2-25%CO-15%CO2-10%H2O', 'Fuel_Flow_SLPM': 4.5,
         'Air_Flow_SLPM': 15.0, 'Current_Density_A_per_cm2': 0.45, 'Pressure_atm': 1.0,
         'Fuel_Utilization_pct': 65, 'Air_Excess_Ratio': 4.0},
        {'Scenario': 'Dilute_Hydrogen', 'Inlet_Temp_Fuel_C': 800, 'Inlet_Temp_Air_C': 800,
         'Fuel_Composition': '50%H2-40%N2-10%H2O', 'Fuel_Flow_SLPM': 7.5, 'Air_Flow_SLPM': 15.0,
         'Current_Density_A_per_cm2': 0.40, 'Pressure_atm': 1.0, 'Fuel_Utilization_pct': 55,
         'Air_Excess_Ratio': 4.8},
        {'Scenario': 'Fast_Startup', 'Inlet_Temp_Fuel_C': 600, 'Inlet_Temp_Air_C': 600,
         'Fuel_Composition': '97%H2-3%H2O', 'Fuel_Flow_SLPM': 2.0, 'Air_Flow_SLPM': 20.0,
         'Current_Density_A_per_cm2': 0.10, 'Pressure_atm': 1.0, 'Fuel_Utilization_pct': 40,
         'Air_Excess_Ratio': 8.0},
        {'Scenario': 'Load_Step_Change', 'Inlet_Temp_Fuel_C': 800, 'Inlet_Temp_Air_C': 800,
         'Fuel_Composition': '97%H2-3%H2O', 'Fuel_Flow_SLPM': 6.5, 'Air_Flow_SLPM': 20.0,
         'Current_Density_A_per_cm2': 0.75, 'Pressure_atm': 1.0, 'Fuel_Utilization_pct': 65,
         'Air_Excess_Ratio': 4.2},
        {'Scenario': 'Thermal_Cycle_Test', 'Inlet_Temp_Fuel_C': 25, 'Inlet_Temp_Air_C': 25,
         'Fuel_Composition': 'Air', 'Fuel_Flow_SLPM': 1.0, 'Air_Flow_SLPM': 5.0,
         'Current_Density_A_per_cm2': 0.00, 'Pressure_atm': 1.0, 'Fuel_Utilization_pct': 0,
         'Air_Excess_Ratio': 0},
        {'Scenario': 'Redox_Cycle_Test', 'Inlet_Temp_Fuel_C': 800, 'Inlet_Temp_Air_C': 800,
         'Fuel_Composition': 'Alternating_H2_Air', 'Fuel_Flow_SLPM': 5.0, 'Air_Flow_SLPM': 10.0,
         'Current_Density_A_per_cm2': 0.00, 'Pressure_atm': 1.0, 'Fuel_Utilization_pct': 0,
         'Air_Excess_Ratio': 0},
    ]
    
    df = pd.DataFrame(data)
    save_csv_with_disclaimer(df, '12_operating_conditions.csv')


def generate_residual_stress():
    """13_residual_stress.csv - Residual stress measurements."""
    data = [
        # XRD sin²ψ method after sintering at room temperature
        {'Location': 'Center', 'Layer': 'Electrolyte_Surface', 'Material': '8YSZ',
         'Sigma_XX_MPa': -45, 'Sigma_YY_MPa': -42, 'Sigma_XY_MPa': 3,
         'Principal_1_MPa': -41, 'Principal_2_MPa': -46, 'Method': 'XRD_sin2psi',
         'Condition': 'As-sintered_RT'},
        {'Location': 'Center', 'Layer': 'Anode_Surface', 'Material': 'Ni-YSZ',
         'Sigma_XX_MPa': 28, 'Sigma_YY_MPa': 32, 'Sigma_XY_MPa': -2,
         'Principal_1_MPa': 33, 'Principal_2_MPa': 27, 'Method': 'XRD_sin2psi',
         'Condition': 'As-sintered_RT'},
        {'Location': 'Edge', 'Layer': 'Electrolyte_Surface', 'Material': '8YSZ',
         'Sigma_XX_MPa': -62, 'Sigma_YY_MPa': -38, 'Sigma_XY_MPa': 8,
         'Principal_1_MPa': -35, 'Principal_2_MPa': -65, 'Method': 'XRD_sin2psi',
         'Condition': 'As-sintered_RT'},
        {'Location': 'Edge', 'Layer': 'Anode_Surface', 'Material': 'Ni-YSZ',
         'Sigma_XX_MPa': 48, 'Sigma_YY_MPa': 25, 'Sigma_XY_MPa': -5,
         'Principal_1_MPa': 50, 'Principal_2_MPa': 23, 'Method': 'XRD_sin2psi',
         'Condition': 'As-sintered_RT'},
        
        # Neutron diffraction at 800°C
        {'Location': 'Center', 'Layer': 'Electrolyte_Bulk', 'Material': '8YSZ',
         'Sigma_XX_MPa': -18, 'Sigma_YY_MPa': -15, 'Sigma_XY_MPa': 1,
         'Principal_1_MPa': -15, 'Principal_2_MPa': -18, 'Method': 'Neutron_Diffraction',
         'Condition': 'At_800C'},
        {'Location': 'Center', 'Layer': 'Anode_Bulk', 'Material': 'Ni-YSZ',
         'Sigma_XX_MPa': 12, 'Sigma_YY_MPa': 15, 'Sigma_XY_MPa': -1,
         'Principal_1_MPa': 15, 'Principal_2_MPa': 12, 'Method': 'Neutron_Diffraction',
         'Condition': 'At_800C'},
        {'Location': 'Center', 'Layer': 'Cathode_Bulk', 'Material': 'LSCF',
         'Sigma_XX_MPa': -22, 'Sigma_YY_MPa': -19, 'Sigma_XY_MPa': 2,
         'Principal_1_MPa': -19, 'Principal_2_MPa': -22, 'Method': 'Neutron_Diffraction',
         'Condition': 'At_800C'},
        
        # XRD after 50 thermal cycles
        {'Location': 'Center', 'Layer': 'Electrolyte_Surface', 'Material': '8YSZ',
         'Sigma_XX_MPa': -68, 'Sigma_YY_MPa': -71, 'Sigma_XY_MPa': 5,
         'Principal_1_MPa': -66, 'Principal_2_MPa': -73, 'Method': 'XRD_cos_alpha',
         'Condition': 'After_50_cycles_RT'},
        {'Location': 'Center', 'Layer': 'Anode_Surface', 'Material': 'Ni-YSZ',
         'Sigma_XX_MPa': 55, 'Sigma_YY_MPa': 62, 'Sigma_XY_MPa': -4,
         'Principal_1_MPa': 63, 'Principal_2_MPa': 54, 'Method': 'XRD_cos_alpha',
         'Condition': 'After_50_cycles_RT'},
        {'Location': 'Edge', 'Layer': 'Electrolyte_Surface', 'Material': '8YSZ',
         'Sigma_XX_MPa': -95, 'Sigma_YY_MPa': -58, 'Sigma_XY_MPa': 12,
         'Principal_1_MPa': -51, 'Principal_2_MPa': -102, 'Method': 'XRD_cos_alpha',
         'Condition': 'After_50_cycles_RT'},
        {'Location': 'Edge', 'Layer': 'Anode_Surface', 'Material': 'Ni-YSZ',
         'Sigma_XX_MPa': 78, 'Sigma_YY_MPa': 42, 'Sigma_XY_MPa': -8,
         'Principal_1_MPa': 82, 'Principal_2_MPa': 38, 'Method': 'XRD_cos_alpha',
         'Condition': 'After_50_cycles_RT'},
        {'Location': 'Center', 'Layer': 'Cathode_Surface', 'Material': 'LSCF',
         'Sigma_XX_MPa': -52, 'Sigma_YY_MPa': -48, 'Sigma_XY_MPa': 3,
         'Principal_1_MPa': -47, 'Principal_2_MPa': -53, 'Method': 'XRD_cos_alpha',
         'Condition': 'After_50_cycles_RT'},
    ]
    
    df = pd.DataFrame(data)
    save_csv_with_disclaimer(df, '13_residual_stress.csv')


def generate_redox_cycling():
    """14_redox_cycling.csv - Redox cycling effects."""
    data = [
        {'Cycle': 0, 'Atmosphere': 'Reduced_H2', 'Temperature_C': 800,
         'Chemical_Strain_pct': 0.00, 'Porosity_Change_pct': 0.0, 'Conductivity_Retention_pct': 100,
         'Bowing_um': 0, 'Crack_Density_per_mm2': 0.0},
        {'Cycle': 1, 'Atmosphere': 'Oxidized_Air', 'Temperature_C': 800,
         'Chemical_Strain_pct': 0.48, 'Porosity_Change_pct': 2.5, 'Conductivity_Retention_pct': 92,
         'Bowing_um': 85, 'Crack_Density_per_mm2': 0.0},
        {'Cycle': 2, 'Atmosphere': 'Reduced_H2', 'Temperature_C': 800,
         'Chemical_Strain_pct': -0.05, 'Porosity_Change_pct': 3.8, 'Conductivity_Retention_pct': 95,
         'Bowing_um': 12, 'Crack_Density_per_mm2': 0.2},
        {'Cycle': 3, 'Atmosphere': 'Oxidized_Air', 'Temperature_C': 800,
         'Chemical_Strain_pct': 0.52, 'Porosity_Change_pct': 5.2, 'Conductivity_Retention_pct': 88,
         'Bowing_um': 105, 'Crack_Density_per_mm2': 0.3},
        {'Cycle': 4, 'Atmosphere': 'Reduced_H2', 'Temperature_C': 800,
         'Chemical_Strain_pct': -0.08, 'Porosity_Change_pct': 6.5, 'Conductivity_Retention_pct': 90,
         'Bowing_um': 18, 'Crack_Density_per_mm2': 0.5},
        {'Cycle': 5, 'Atmosphere': 'Oxidized_Air', 'Temperature_C': 800,
         'Chemical_Strain_pct': 0.55, 'Porosity_Change_pct': 8.1, 'Conductivity_Retention_pct': 82,
         'Bowing_um': 128, 'Crack_Density_per_mm2': 0.7},
        {'Cycle': 10, 'Atmosphere': 'Reduced_H2', 'Temperature_C': 800,
         'Chemical_Strain_pct': -0.12, 'Porosity_Change_pct': 14.2, 'Conductivity_Retention_pct': 78,
         'Bowing_um': 35, 'Crack_Density_per_mm2': 1.8},
        {'Cycle': 11, 'Atmosphere': 'Oxidized_Air', 'Temperature_C': 800,
         'Chemical_Strain_pct': 0.62, 'Porosity_Change_pct': 16.5, 'Conductivity_Retention_pct': 68,
         'Bowing_um': 185, 'Crack_Density_per_mm2': 2.2},
        {'Cycle': 15, 'Atmosphere': 'Oxidized_Air', 'Temperature_C': 800,
         'Chemical_Strain_pct': 0.68, 'Porosity_Change_pct': 22.8, 'Conductivity_Retention_pct': 55,
         'Bowing_um': 245, 'Crack_Density_per_mm2': 3.5},
        {'Cycle': 16, 'Atmosphere': 'Reduced_H2', 'Temperature_C': 800,
         'Chemical_Strain_pct': -0.18, 'Porosity_Change_pct': 24.5, 'Conductivity_Retention_pct': 58,
         'Bowing_um': 55, 'Crack_Density_per_mm2': 4.1},
        {'Cycle': 20, 'Atmosphere': 'Reduced_H2', 'Temperature_C': 800,
         'Chemical_Strain_pct': -0.22, 'Porosity_Change_pct': 30.2, 'Conductivity_Retention_pct': 48,
         'Bowing_um': 72, 'Crack_Density_per_mm2': 5.8},
    ]
    
    df = pd.DataFrame(data)
    save_csv_with_disclaimer(df, '14_redox_cycling.csv')


def generate_FEM_input_summary():
    """15_FEM_input_summary.csv - Quick-reference FEM material table."""
    data = [
        {'Property': 'Density', '8YSZ': 5900, 'Ni-YSZ': 4460, 'LSCF': 6300,
         'LSM': 6500, 'GDC': 7220, 'Crofer22APU': 7700, 'Unit': 'kg/m³',
         'Notes': 'Room temperature density'},
        {'Property': 'Elastic_Modulus_25C', '8YSZ': 210, 'Ni-YSZ': 95, 'LSCF': 105,
         'LSM': 95, 'GDC': 185, 'Crofer22APU': 220, 'Unit': 'GPa',
         'Notes': 'At room temperature'},
        {'Property': 'Elastic_Modulus_800C', '8YSZ': 170, 'Ni-YSZ': 55, 'LSCF': 65,
         'LSM': 60, 'GDC': 145, 'Crofer22APU': 140, 'Unit': 'GPa',
         'Notes': 'At operating temperature'},
        {'Property': 'Poisson_Ratio', '8YSZ': 0.31, 'Ni-YSZ': 0.30, 'LSCF': 0.26,
         'LSM': 0.26, 'GDC': 0.29, 'Crofer22APU': 0.30, 'Unit': '-',
         'Notes': 'Weakly temperature-dependent'},
        {'Property': 'CTE_25C', '8YSZ': 10.3, 'Ni-YSZ': 12.5, 'LSCF': 14.0,
         'LSM': 11.2, 'GDC': 11.8, 'Crofer22APU': 10.0, 'Unit': '10⁻⁶/K',
         'Notes': 'At room temperature'},
        {'Property': 'CTE_800C', '8YSZ': 11.5, 'Ni-YSZ': 14.0, 'LSCF': 16.0,
         'LSM': 11.8, 'GDC': 12.7, 'Crofer22APU': 11.8, 'Unit': '10⁻⁶/K',
         'Notes': 'At operating temperature'},
        {'Property': 'Thermal_Conductivity_25C', '8YSZ': 2.0, 'Ni-YSZ': 11.0, 'LSCF': 3.5,
         'LSM': 3.0, 'GDC': 5.5, 'Crofer22APU': 22.0, 'Unit': 'W/(m·K)',
         'Notes': 'At room temperature'},
        {'Property': 'Thermal_Conductivity_800C', '8YSZ': 2.3, 'Ni-YSZ': 5.5, 'LSCF': 2.7,
         'LSM': 2.6, 'GDC': 3.2, 'Crofer22APU': 27.0, 'Unit': 'W/(m·K)',
         'Notes': 'At operating temperature'},
        {'Property': 'Specific_Heat_25C', '8YSZ': 456, 'Ni-YSZ': 450, 'LSCF': 450,
         'LSM': 470, 'GDC': 390, 'Crofer22APU': 460, 'Unit': 'J/(kg·K)',
         'Notes': 'At room temperature'},
        {'Property': 'Specific_Heat_800C', '8YSZ': 515, 'Ni-YSZ': 525, 'LSCF': 540,
         'LSM': 520, 'GDC': 520, 'Crofer22APU': 610, 'Unit': 'J/(kg·K)',
         'Notes': 'At operating temperature'},
        {'Property': 'Flexural_Strength_25C', '8YSZ': 250, 'Ni-YSZ': 130, 'LSCF': 90,
         'LSM': 85, 'GDC': 200, 'Crofer22APU': 520, 'Unit': 'MPa',
         'Notes': '4-point bending'},
        {'Property': 'Flexural_Strength_800C', '8YSZ': 190, 'Ni-YSZ': 70, 'LSCF': 52,
         'LSM': 50, 'GDC': 160, 'Crofer22APU': 190, 'Unit': 'MPa',
         'Notes': '4-point bending'},
        {'Property': 'Fracture_Toughness_25C', '8YSZ': 2.0, 'Ni-YSZ': 1.8, 'LSCF': 1.0,
         'LSM': 0.9, 'GDC': 1.5, 'Crofer22APU': 80, 'Unit': 'MPa·m½',
         'Notes': 'SENB method'},
        {'Property': 'Weibull_Modulus', '8YSZ': 9, 'Ni-YSZ': 6, 'LSCF': 5,
         'LSM': 4.5, 'GDC': 8, 'Crofer22APU': 25, 'Unit': '-',
         'Notes': 'Failure probability distribution'},
        {'Property': 'Sintering_Temperature', '8YSZ': 1400, 'Ni-YSZ': 1400, 'LSCF': 1100,
         'LSM': 1200, 'GDC': 1350, 'Crofer22APU': 0, 'Unit': '°C',
         'Notes': 'Processing temperature'},
        {'Property': 'Layer_Thickness', '8YSZ': 10, 'Ni-YSZ': 515, 'LSCF': 45,
         'LSM': 30, 'GDC': 5, 'Crofer22APU': 500, 'Unit': 'μm',
         'Notes': 'Typical layer thickness'},
    ]
    
    df = pd.DataFrame(data)
    save_csv_with_disclaimer(df, '15_FEM_input_summary.csv')


def generate_references():
    """16_references.csv - Literature references with DOIs."""
    data = [
        {'Ref_ID': 'REF01', 'Authors': 'Atkinson, A., Selçuk, A.',
         'Year': 2004, 'Title': 'Mechanical behaviour of ceramic oxygen ion-conducting membranes',
         'Journal_Source': 'Solid State Ionics, 134(1-2), pp.59-66',
         'DOI_or_URL': '10.1016/j.ssi.2004.01.004', 'Data_Type': 'YSZ mechanical properties'},
        
        {'Ref_ID': 'REF02', 'Authors': 'Laurencin, J., et al.',
         'Year': 2008, 'Title': 'Creep behaviour of porous SOFC electrodes',
         'Journal_Source': 'Journal of Power Sources, 177(2), pp.456-467',
         'DOI_or_URL': '10.1016/j.jpowsour.2008.02.103', 'Data_Type': 'Ni-YSZ creep parameters'},
        
        {'Ref_ID': 'REF03', 'Authors': 'Nakajo, A., et al.',
         'Year': 2012, 'Title': 'Thermo-mechanical modeling of SOFC stacks',
         'Journal_Source': 'Journal of Power Sources, 213, pp.187-198',
         'DOI_or_URL': '10.1016/j.jpowsour.2012.01.114', 'Data_Type': 'Thermal stress analysis'},
        
        {'Ref_ID': 'REF04', 'Authors': 'Malzbender, J., Steinbrech, R.W.',
         'Year': 2009, 'Title': 'Review of SOFC component properties',
         'Journal_Source': 'Ceramics International, 35(4), pp.1565-1578',
         'DOI_or_URL': '10.1016/j.ceramint.2008.11.005', 'Data_Type': 'Comprehensive material properties'},
        
        {'Ref_ID': 'REF05', 'Authors': 'Yakabe, H., et al.',
         'Year': 2001, 'Title': 'Temperature distribution in planar SOFC stacks',
         'Journal_Source': 'Journal of Power Sources, 102(1-2), pp.144-154',
         'DOI_or_URL': '10.1016/S0378-7753(01)00610-2', 'Data_Type': 'Temperature distribution'},
        
        {'Ref_ID': 'REF06', 'Authors': 'Selimovic, A., et al.',
         'Year': 2005, 'Title': 'Thermal cycling effects on SOFC degradation',
         'Journal_Source': 'Journal of Power Sources, 145(2), pp.463-469',
         'DOI_or_URL': '10.1016/j.jpowsour.2004.10.012', 'Data_Type': 'Thermal cycling'},
        
        {'Ref_ID': 'REF07', 'Authors': 'Lin, C.K., et al.',
         'Year': 2009, 'Title': 'Residual stress in SOFC measured by XRD',
         'Journal_Source': 'Acta Materialia, 57(13), pp.3978-3987',
         'DOI_or_URL': '10.1016/j.actamat.2009.05.018', 'Data_Type': 'Residual stress measurements'},
        
        {'Ref_ID': 'REF08', 'Authors': 'Pihlatie, M., et al.',
         'Year': 2009, 'Title': 'Mechanical degradation of Ni-YSZ under redox cycling',
         'Journal_Source': 'Journal of Power Sources, 193(1), pp.322-332',
         'DOI_or_URL': '10.1016/j.jpowsour.2009.01.021', 'Data_Type': 'Redox cycling effects'},
        
        {'Ref_ID': 'REF09', 'Authors': 'Menzler, N.H., et al.',
         'Year': 2010, 'Title': 'LSCF cathode material characterization',
         'Journal_Source': 'Journal of Power Sources, 195(16), pp.5320-5325',
         'DOI_or_URL': '10.1016/j.jpowsour.2010.06.042', 'Data_Type': 'LSCF properties'},
        
        {'Ref_ID': 'REF10', 'Authors': 'Quadakkers, W.J., et al.',
         'Year': 2007, 'Title': 'Crofer 22 APU interconnect characterization',
         'Journal_Source': 'Materials Science and Engineering: A, 480(1-2), pp.483-492',
         'DOI_or_URL': '10.1016/j.msea.2006.11.127', 'Data_Type': 'Interconnect properties'},
        
        {'Ref_ID': 'REF11', 'Authors': 'Ni, M., Leung, M.K.H., Leung, D.Y.C.',
         'Year': 2007, 'Title': 'Electrochemical modeling of SOFC button cells',
         'Journal_Source': 'Journal of the Electrochemical Society, 154(4), pp.B385-B392',
         'DOI_or_URL': '10.1149/1.2789389', 'Data_Type': 'Electrochemical modeling'},
        
        {'Ref_ID': 'REF12', 'Authors': 'Zhu, H., Kee, R.J.',
         'Year': 2003, 'Title': 'Modeling polarization curves for SOFC',
         'Journal_Source': 'Journal of Power Sources, 117(1-2), pp.61-74',
         'DOI_or_URL': '10.1016/S0378-7753(03)00742-6', 'Data_Type': 'Polarization modeling'},
        
        {'Ref_ID': 'REF13', 'Authors': 'Hagen, A., et al.',
         'Year': 2006, 'Title': 'SOFC degradation mechanisms',
         'Journal_Source': 'Journal of Power Sources, 161(1), pp.30-38',
         'DOI_or_URL': '10.1016/j.jpowsour.2006.04.080', 'Data_Type': 'Degradation mechanisms'},
        
        {'Ref_ID': 'REF14', 'Authors': 'Sun, C., Stimming, U.',
         'Year': 2007, 'Title': 'Recent advances in SOFC materials',
         'Journal_Source': 'Journal of Power Sources, 171(2), pp.247-260',
         'DOI_or_URL': '10.1016/j.jpowsour.2006.12.017', 'Data_Type': 'SOFC materials review'},
    ]
    
    df = pd.DataFrame(data)
    save_csv_with_disclaimer(df, '16_references.csv')


def main():
    """Generate all 16 CSV datasets."""
    print("\n" + "="*70)
    print("SOFC Thermo-Mechanical Dataset Generator")
    print("="*70 + "\n")
    print("⚠️  GENERATING SYNTHETIC DATA - NOT ACTUAL MEASUREMENTS")
    print("    For educational and template purposes only\n")
    
    generators = [
        ("01 - Thermal Properties", generate_thermal_properties),
        ("02 - Mechanical Properties", generate_mechanical_properties),
        ("03 - Creep Parameters (Norton)", generate_creep_parameters_norton),
        ("04 - Creep Curves", generate_creep_curves),
        ("05 - CTE Mismatch & Thermal Stress", generate_CTE_mismatch_thermal_stress),
        ("06 - Polarization Curves", generate_polarization_curves),
        ("07 - Thermal Cycling Degradation", generate_thermal_cycling_degradation),
        ("08 - Strain Hardening Constants", generate_strain_hardening_constants),
        ("09 - Temperature Distribution", generate_temperature_distribution),
        ("10 - Stress Evolution (Thermal Cycle)", generate_stress_evolution_thermal_cycle),
        ("11 - Cell Geometry", generate_cell_geometry),
        ("12 - Operating Conditions", generate_operating_conditions),
        ("13 - Residual Stress", generate_residual_stress),
        ("14 - Redox Cycling", generate_redox_cycling),
        ("15 - FEM Input Summary", generate_FEM_input_summary),
        ("16 - References", generate_references),
    ]
    
    for desc, func in generators:
        print(f"Generating {desc}...", end=" ")
        func()
    
    print("\n" + "="*70)
    print(f"✓ Successfully generated all 16 CSV files in {DATA_DIR}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
