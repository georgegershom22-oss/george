#!/usr/bin/env python3
"""
Master script to generate all 15 SOFC thermo-mechanical dataset CSV files.

DISCLAIMER: All data is SYNTHETIC/ILLUSTRATIVE, based on published literature ranges.
DO NOT use as ground truth without independent verification.

Author: SOFC Dataset Package
Date: February 2026
"""

import csv
import os
import math

# Ensure data directory exists
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Common disclaimer header for all CSV files
DISCLAIMER_HEADER = [
    "# SYNTHETIC/ILLUSTRATIVE DATA - Based on published literature ranges",
    "# Topic: Thermo-mechanical behavior of SOFC at high temperatures",
    "# DO NOT use as ground truth without independent verification"
]

def write_csv_with_header(filename, header_lines, column_names, rows):
    """Write CSV file with comment header and data."""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w', newline='') as f:
        # Write comment lines
        for line in header_lines:
            f.write(line + '\n')
        
        # Write data
        writer = csv.writer(f)
        writer.writerow(column_names)
        writer.writerows(rows)
    
    print(f"✓ Generated {filename} ({len(rows)} rows)")


def generate_01_thermal_properties():
    """Generate temperature-dependent thermal properties for 6 materials."""
    materials = [
        ('8YSZ', 5900, 'Hayashi 2005'),
        ('GDC', 7220, 'Sameshima 1999'),
        ('Ni-YSZ', 4460, 'Pihlatie 2009'),
        ('LSCF', 6300, 'Mori & Hishinuma 2003'),
        ('LSM', 6500, 'Atkinson & Selcuk 2000'),
        ('Crofer 22 APU', 7700, 'ThyssenKrupp VDM datasheet')
    ]
    
    temps = list(range(25, 1001, 100))  # 25 to 1000°C in 100°C increments
    
    rows = []
    for mat_name, rho, source in materials:
        for T in temps:
            # Thermal conductivity (W/m·K)
            if mat_name == '8YSZ':
                k = 2.0 + 0.0004 * T
                Cp = 456 + 0.084 * T
                CTE = 10.3 + 0.0017 * T
            elif mat_name == 'GDC':
                k = max(2.5, 5.5 - 0.004 * T + 2e-6 * T**2)
                Cp = 390 + 0.17 * T
                CTE = 11.8 + 0.0013 * T
            elif mat_name == 'Ni-YSZ':
                k = max(4.0, 11.0 - 0.0075 * T + 1.5e-6 * T**2)
                Cp = 450 + 0.1 * T
                CTE = 12.5 + 0.0024 * T
            elif mat_name == 'LSCF':
                k = max(2.5, 3.5 - 0.001 * T)
                Cp = 450 + 0.12 * T
                CTE = 14.0 + 0.0028 * T
            elif mat_name == 'LSM':
                k = max(2.5, 3.0 - 0.0005 * T)
                Cp = 470 + 0.07 * T
                CTE = 11.2 + 0.001 * T
            else:  # Crofer 22 APU
                k = 22.0 + 0.006 * T
                Cp = 460 + 0.2 * T
                CTE = 10.0 + 0.0025 * T
            
            rows.append([mat_name, T, round(k, 2), round(Cp, 1), round(CTE, 2), rho, source])
    
    columns = ['Material', 'Temperature_C', 'Thermal_Conductivity_W_per_mK', 
               'Specific_Heat_J_per_kgK', 'CTE_1e-6_per_K', 'Density_kg_per_m3', 'Source_Basis']
    
    write_csv_with_header('01_thermal_properties.csv', DISCLAIMER_HEADER, columns, rows)


def generate_02_mechanical_properties():
    """Generate temperature-dependent mechanical properties for 6 materials."""
    materials_data = [
        ('8YSZ', 210, 0.31, 250, 2.0, 10, 1.5e-4, 3e-8, 'Selcuk & Atkinson 1997'),
        ('GDC', 200, 0.33, 180, 1.5, 8, 1.6e-4, 3.5e-8, 'Morales 2006'),
        ('Ni-YSZ', 95, 0.30, 130, 1.8, 7, 2e-4, 5e-8, 'Radovic & Lara-Curzio 2004'),
        ('LSCF', 105, 0.26, 90, 1.0, 6, 2.5e-4, 4e-8, 'Mori & Hishinuma 2003'),
        ('LSM', 150, 0.29, 120, 1.2, 8, 1.8e-4, 3e-8, 'Atkinson & Selcuk 2000'),
        ('Crofer 22 APU', 220, 0.30, 520, 80.0, 30, 2e-4, 4e-8, 'ThyssenKrupp VDM datasheet')
    ]
    
    temps = list(range(25, 1001, 100))
    
    rows = []
    for mat_name, E0, nu, sigma0, KIC0, m0, c1, c2, source in materials_data:
        for T in temps:
            # Elastic modulus degradation with temperature
            E = E0 * (1 - c1 * (T - 25) - c2 * (T - 25)**2)
            E = max(E, E0 * 0.3)  # Don't drop below 30% of room temp value
            
            # Scale strength and toughness with modulus
            E_ratio = E / E0
            sigma = sigma0 * (E_ratio ** 0.8)
            KIC = KIC0 * (E_ratio ** 0.5)
            m = max(3, m0 * (E_ratio ** 0.3))
            
            rows.append([mat_name, T, round(E, 1), round(nu, 3), 
                        round(sigma, 1), round(KIC, 2), round(m, 1), source])
    
    columns = ['Material', 'Temperature_C', 'Elastic_Modulus_GPa', 'Poisson_Ratio',
               'Flexural_Strength_MPa', 'Fracture_Toughness_MPa_sqrt_m', 
               'Weibull_Modulus', 'Source_Basis']
    
    write_csv_with_header('02_mechanical_properties.csv', DISCLAIMER_HEADER, columns, rows)


def generate_03_creep_parameters():
    """Generate Norton power-law creep parameters for Ni-YSZ anode."""
    rows = [
        ['Ni-8YSZ', 40, 30, 750, 2.4, 235, 2.1e-9, 'H2-H2O', 'Diffusional + dislocation', 'Huang et al. 1998'],
        ['Ni-8YSZ', 40, 30, 800, 2.6, 240, 3.8e-9, 'H2-H2O', 'Diffusional + dislocation', 'Huang et al. 1998'],
        ['Ni-8YSZ', 40, 30, 900, 3.1, 250, 1.2e-8, 'H2-H2O', 'Dislocation creep', 'Huang et al. 1998'],
        ['Ni-8YSZ', 40, 30, 1000, 3.8, 265, 4.5e-8, 'H2-H2O', 'Dislocation creep', 'Huang et al. 1998'],
        ['Ni-8YSZ', 56, 20, 800, 3.2, 260, 5.2e-9, 'H2-H2O', 'Dislocation creep', 'FZ Jülich (Yakabe 2001)'],
        ['Ni-8YSZ', 56, 20, 850, 3.5, 270, 1.1e-8, 'H2-H2O', 'Dislocation creep', 'FZ Jülich (Yakabe 2001)'],
        ['Ni-8YSZ', 56, 20, 900, 3.9, 280, 2.8e-8, 'H2-H2O', 'Dislocation creep', 'FZ Jülich (Yakabe 2001)'],
        ['Ni-8YSZ', 56, 20, 1000, 4.5, 295, 9.5e-8, 'H2-H2O', 'Dislocation creep', 'FZ Jülich (Yakabe 2001)'],
        ['Ni-8YSZ', 30, 35, 800, 2.8, 220, 1.5e-9, 'H2-H2O', 'Diffusional', 'Tohoku Univ (Clague 2012)'],
        ['Ni-8YSZ', 30, 35, 900, 3.4, 235, 6.8e-9, 'H2-H2O', 'Dislocation creep', 'Tohoku Univ (Clague 2012)'],
        ['Ni-3YSZ', 40, 25, 800, 3.6, 275, 7.2e-9, 'H2-H2O', 'Dislocation creep', 'FZ Jülich (Yakabe 2001)'],
        ['Ni-3YSZ', 40, 25, 850, 4.1, 285, 1.8e-8, 'H2-H2O', 'Dislocation creep', 'FZ Jülich (Yakabe 2001)'],
        ['Ni-3YSZ', 40, 25, 900, 4.8, 300, 5.2e-8, 'H2-H2O', 'Power-law breakdown', 'FZ Jülich (Yakabe 2001)'],
    ]
    
    columns = ['Material', 'Ni_vol_pct', 'Porosity_pct', 'Temperature_C', 
               'Stress_Exponent_n', 'Activation_Energy_kJ_per_mol', 
               'Pre_Exponential_A', 'Atmosphere', 'Creep_Mechanism', 'Source_Basis']
    
    write_csv_with_header('03_creep_parameters_norton.csv', DISCLAIMER_HEADER, columns, rows)


def generate_04_creep_curves():
    """Generate simulated creep strain vs time curves."""
    time_hours = [i * 5 for i in range(101)]  # 0 to 500 hours in 5-hour steps
    
    rows = []
    for t in time_hours:
        # Different stress-temperature conditions with power-law creep
        # Strain = initial_elastic + coefficient * t^exponent
        strain_5MPa_750C = 0.05 + 0.012 * (t ** 0.35)
        strain_10MPa_800C = 0.10 + 0.028 * (t ** 0.40)
        strain_15MPa_800C = 0.15 + 0.055 * (t ** 0.42)
        strain_20MPa_850C = 0.20 + 0.095 * (t ** 0.45)
        strain_10MPa_900C = 0.10 + 0.075 * (t ** 0.48)
        
        rows.append([t, 
                    round(strain_5MPa_750C, 4),
                    round(strain_10MPa_800C, 4),
                    round(strain_15MPa_800C, 4),
                    round(strain_20MPa_850C, 4),
                    round(strain_10MPa_900C, 4)])
    
    columns = ['Time_hours', 'Strain_pct_5MPa_750C', 'Strain_pct_10MPa_800C',
               'Strain_pct_15MPa_800C', 'Strain_pct_20MPa_850C', 'Strain_pct_10MPa_900C']
    
    write_csv_with_header('04_creep_curves_NiYSZ.csv', DISCLAIMER_HEADER, columns, rows)


def generate_05_CTE_mismatch():
    """Generate CTE mismatch and estimated biaxial thermal stress."""
    temps = list(range(25, 1001, 100))
    T_sinter = 1400  # Sintering temperature in °C
    
    rows = []
    for T in temps:
        # Calculate CTE for each material at this temperature
        CTE_8YSZ = 10.3 + 0.0017 * T
        CTE_GDC = 11.8 + 0.0013 * T
        CTE_NiYSZ = 12.5 + 0.0024 * T
        CTE_LSCF = 14.0 + 0.0028 * T
        CTE_LSM = 11.2 + 0.001 * T
        CTE_Crofer = 10.0 + 0.0025 * T
        
        # CTE mismatches at key interfaces
        Delta_CTE_anode_electrolyte = abs(CTE_NiYSZ - CTE_8YSZ)
        Delta_CTE_cathode_electrolyte_LSCF = abs(CTE_LSCF - CTE_8YSZ)
        Delta_CTE_cathode_electrolyte_LSM = abs(CTE_LSM - CTE_8YSZ)
        
        # Thermal stress calculation: sigma = E_eff * Delta_alpha * Delta_T / (1 - nu)
        # Using effective properties and cooling from sintering temp
        Delta_T = T_sinter - T
        E_eff_anode = 120  # Effective modulus at interface in GPa
        E_eff_cathode = 140
        nu_eff = 0.3
        
        # Convert to MPa (Delta_CTE is in 1e-6/K, E in GPa, DeltaT in K)
        stress_anode_electrolyte = (E_eff_anode * 1000 * Delta_CTE_anode_electrolyte * 1e-6 * Delta_T) / (1 - nu_eff)
        stress_cathode_LSCF = (E_eff_cathode * 1000 * Delta_CTE_cathode_electrolyte_LSCF * 1e-6 * Delta_T) / (1 - nu_eff)
        stress_cathode_LSM = (E_eff_cathode * 1000 * Delta_CTE_cathode_electrolyte_LSM * 1e-6 * Delta_T) / (1 - nu_eff)
        
        rows.append([T, 
                    round(CTE_8YSZ, 2), round(CTE_GDC, 2), round(CTE_NiYSZ, 2),
                    round(CTE_LSCF, 2), round(CTE_LSM, 2), round(CTE_Crofer, 2),
                    round(Delta_CTE_anode_electrolyte, 2),
                    round(Delta_CTE_cathode_electrolyte_LSCF, 2),
                    round(Delta_CTE_cathode_electrolyte_LSM, 2),
                    round(stress_anode_electrolyte, 1),
                    round(stress_cathode_LSCF, 1),
                    round(stress_cathode_LSM, 1)])
    
    columns = ['Temperature_C', 'CTE_8YSZ', 'CTE_GDC', 'CTE_NiYSZ', 'CTE_LSCF', 'CTE_LSM', 'CTE_Crofer',
               'Delta_CTE_Anode_Electrolyte', 'Delta_CTE_LSCF_Electrolyte', 'Delta_CTE_LSM_Electrolyte',
               'Thermal_Stress_Anode_Interface_MPa', 'Thermal_Stress_LSCF_Interface_MPa', 
               'Thermal_Stress_LSM_Interface_MPa']
    
    write_csv_with_header('05_CTE_mismatch_thermal_stress.csv', DISCLAIMER_HEADER, columns, rows)


def generate_06_polarization_curves():
    """Generate I-V and power density curves at three temperatures."""
    current_densities = [i * 0.02 for i in range(61)]  # 0 to 1.2 A/cm² in 0.02 steps
    
    rows = []
    for i_A_cm2 in current_densities:
        # Open circuit voltages at each temperature
        OCV_750 = 1.10
        OCV_800 = 1.08
        OCV_850 = 1.06
        
        # Activation overpotential: eta_act = a + b*log(i)
        if i_A_cm2 > 0:
            eta_act_750 = 0.15 + 0.08 * math.log10(i_A_cm2 + 0.001)
            eta_act_800 = 0.12 + 0.06 * math.log10(i_A_cm2 + 0.001)
            eta_act_850 = 0.10 + 0.05 * math.log10(i_A_cm2 + 0.001)
        else:
            eta_act_750 = eta_act_800 = eta_act_850 = 0
        
        # Ohmic overpotential: eta_ohm = R_ohm * i
        R_ohm_750 = 0.25  # Ohm·cm²
        R_ohm_800 = 0.18
        R_ohm_850 = 0.14
        eta_ohm_750 = R_ohm_750 * i_A_cm2
        eta_ohm_800 = R_ohm_800 * i_A_cm2
        eta_ohm_850 = R_ohm_850 * i_A_cm2
        
        # Concentration overpotential: eta_conc = c * exp(d * i)
        eta_conc_750 = 0.02 * math.exp(2.5 * i_A_cm2) - 0.02
        eta_conc_800 = 0.015 * math.exp(2.0 * i_A_cm2) - 0.015
        eta_conc_850 = 0.01 * math.exp(1.8 * i_A_cm2) - 0.01
        
        # Cell voltage: V = OCV - eta_act - eta_ohm - eta_conc
        V_750 = max(0, OCV_750 - eta_act_750 - eta_ohm_750 - eta_conc_750)
        V_800 = max(0, OCV_800 - eta_act_800 - eta_ohm_800 - eta_conc_800)
        V_850 = max(0, OCV_850 - eta_act_850 - eta_ohm_850 - eta_conc_850)
        
        # Power density: P = V * i
        P_750 = V_750 * i_A_cm2
        P_800 = V_800 * i_A_cm2
        P_850 = V_850 * i_A_cm2
        
        rows.append([round(i_A_cm2, 3), 
                    round(V_750, 4), round(P_750, 4),
                    round(V_800, 4), round(P_800, 4),
                    round(V_850, 4), round(P_850, 4),
                    'H2 97% + H2O 3%'])
    
    columns = ['Current_Density_A_per_cm2', 
               'Voltage_750C_V', 'Power_750C_W_per_cm2',
               'Voltage_800C_V', 'Power_800C_W_per_cm2',
               'Voltage_850C_V', 'Power_850C_W_per_cm2',
               'Fuel_Composition']
    
    write_csv_with_header('06_polarization_curves.csv', DISCLAIMER_HEADER, columns, rows)


def generate_07_thermal_cycling():
    """Generate degradation data for thermal cycling at three ramp rates."""
    cycles = [0, 1, 2, 5, 10, 20, 30, 50, 75, 100]
    ramp_rates = [5, 10, 20]  # °C/min
    
    rows = []
    for ramp in ramp_rates:
        # Degradation increases with ramp rate
        degradation_factor = 0.001 * (ramp / 5) ** 1.5
        
        for cycle in cycles:
            # Initial values at cycle 0
            peak_power_0 = 0.62  # W/cm²
            OCV_0 = 1.08  # V
            V_05A_0 = 0.75  # V at 0.5 A/cm²
            ASR_0 = 0.18  # Ohm·cm²
            
            # Performance degradation (exponential + linear)
            deg_pct = 100 * (1 - math.exp(-degradation_factor * cycle) + 0.0002 * cycle)
            
            # Apply degradation
            peak_power = peak_power_0 * (1 - deg_pct / 100)
            OCV = OCV_0 - 0.0005 * deg_pct
            V_05A = V_05A_0 * (1 - deg_pct / 100)
            ASR = ASR_0 * (1 + deg_pct / 50)
            
            # Observation notes
            if cycle == 0:
                obs = "Fresh cell"
            elif cycle <= 5:
                obs = "Initial degradation phase"
            elif cycle <= 30:
                obs = "Moderate degradation"
            elif cycle <= 75:
                obs = "Accelerated degradation"
            else:
                obs = "Significant performance loss"
            
            rows.append([cycle, ramp, 
                        round(peak_power, 4), round(OCV, 4), 
                        round(V_05A, 4), round(ASR, 4),
                        round(deg_pct, 2), obs])
    
    columns = ['Cycle_Number', 'Ramp_Rate_C_per_min', 'Peak_Power_W_per_cm2', 
               'OCV_V', 'Voltage_at_0.5A_per_cm2_V', 'ASR_Ohm_cm2',
               'Cumulative_Degradation_pct', 'Observation']
    
    write_csv_with_header('07_thermal_cycling_degradation.csv', DISCLAIMER_HEADER, columns, rows)


def generate_08_strain_hardening():
    """Generate time-hardening creep constants for FEM software."""
    rows = [
        ['Ni-8YSZ', 750, 2.1e-9, 2.4, 235000, 8.314, '5-20 MPa', 'Norton power-law', 'Huang et al. 1998'],
        ['Ni-8YSZ', 800, 3.8e-9, 2.6, 240000, 8.314, '5-25 MPa', 'Norton power-law', 'Huang et al. 1998'],
        ['Ni-8YSZ', 900, 1.2e-8, 3.1, 250000, 8.314, '5-30 MPa', 'Norton power-law', 'Huang et al. 1998'],
        ['Ni-8YSZ', 1000, 4.5e-8, 3.8, 265000, 8.314, '5-35 MPa', 'Norton power-law', 'Huang et al. 1998'],
        ['8YSZ', 800, 1.2e-11, 1.8, 400000, 8.314, '10-100 MPa', 'Coble creep', 'Kilo et al. 2003'],
        ['8YSZ', 900, 5.5e-11, 1.9, 410000, 8.314, '10-120 MPa', 'Coble creep', 'Kilo et al. 2003'],
        ['8YSZ', 1000, 2.8e-10, 2.1, 425000, 8.314, '10-150 MPa', 'Nabarro-Herring', 'Kilo et al. 2003'],
        ['LSCF', 800, 5.2e-10, 2.2, 280000, 8.314, '5-40 MPa', 'Grain boundary sliding', 'Mori et al. 2005'],
        ['LSCF', 900, 2.8e-9, 2.5, 295000, 8.314, '5-50 MPa', 'Dislocation creep', 'Mori et al. 2005'],
        ['Crofer 22 APU', 750, 1.8e-14, 5.2, 320000, 8.314, '20-200 MPa', 'Dislocation creep', 'ThyssenKrupp VDM'],
        ['Crofer 22 APU', 800, 8.5e-14, 5.5, 330000, 8.314, '20-220 MPa', 'Dislocation creep', 'ThyssenKrupp VDM'],
        ['Crofer 22 APU', 850, 3.2e-13, 5.8, 340000, 8.314, '20-240 MPa', 'Power-law breakdown', 'ThyssenKrupp VDM'],
    ]
    
    columns = ['Material', 'Temperature_C', 'C1_Pre_Exponential', 'C2_Stress_Exponent',
               'C3_Activation_Energy_J_per_mol', 'C4_Gas_Constant_J_per_molK',
               'Valid_Stress_Range_MPa', 'Model_Type', 'Source_Basis']
    
    write_csv_with_header('08_strain_hardening_FEM_input.csv', DISCLAIMER_HEADER, columns, rows)


def generate_09_temperature_distribution():
    """Generate 2D temperature field on 100mm × 100mm cell surface."""
    rows = []
    
    for x in range(0, 101, 5):  # 0 to 100 mm in 5 mm steps
        for y in range(0, 101, 5):
            # Steady-state: hottest at center, cooler at edges
            r = math.sqrt((x - 50)**2 + (y - 50)**2)
            T_ss = 1073 + 100 * math.exp(-r / 30)  # Peak 1173 K at center
            
            # Startup: gradient from inlet (bottom) to outlet (top)
            T_startup = 973 + 2 * y + 50 * math.exp(-r / 35)
            
            # Load step: asymmetric due to current distribution
            T_load = 1073 + 80 * math.exp(-(x - 60)**2 / 400) * math.exp(-(y - 50)**2 / 300)
            
            # Temperature gradient in x-direction
            dTdx = -100 * math.exp(-r / 30) * (x - 50) / (30 * r) if r > 0 else 0
            
            rows.append([x, y, round(T_ss, 1), round(T_startup, 1), 
                        round(T_load, 1), round(dTdx, 3)])
    
    columns = ['Position_x_mm', 'Position_y_mm', 'T_SteadyState_K', 
               'T_Startup_K', 'T_LoadStep_K', 'dTdx_K_per_mm']
    
    write_csv_with_header('09_temperature_distribution.csv', DISCLAIMER_HEADER, columns, rows)


def generate_10_stress_evolution():
    """Generate stress evolution during one thermal cycle."""
    rows = []
    
    # Phase 1: Heating (0 to 2600 s, 25 to 800°C)
    for t in range(0, 2601, 200):
        T = 25 + (800 - 25) * (t / 2600)
        phase = "Heating"
        
        # Thermal stress builds up during heating
        stress_factor = t / 2600
        VM_anode = 45 + 85 * stress_factor
        VM_electrolyte = 120 + 180 * stress_factor
        VM_cathode = 35 + 75 * stress_factor
        VM_interconnect = 80 + 140 * stress_factor
        max_principal = 180 + 220 * stress_factor
        shear = 25 + 50 * stress_factor
        creep = 0
        
        rows.append([t, round(T, 1), phase, round(VM_anode, 1), 
                    round(VM_electrolyte, 1), round(VM_cathode, 1),
                    round(VM_interconnect, 1), round(max_principal, 1),
                    round(shear, 1), round(creep, 4)])
    
    # Phase 2: Dwell at 800°C (2600 to 6200 s)
    for t in range(2600, 6201, 200):
        T = 800
        phase = "Dwell"
        
        # Stress relaxation due to creep
        time_dwell = (t - 2600) / 3600  # hours
        relaxation = math.exp(-time_dwell / 2)
        
        VM_anode = 130 * relaxation + 50 * (1 - relaxation)
        VM_electrolyte = 300 * relaxation + 120 * (1 - relaxation)
        VM_cathode = 110 * relaxation + 45 * (1 - relaxation)
        VM_interconnect = 220 * relaxation + 90 * (1 - relaxation)
        max_principal = 400 * relaxation + 150 * (1 - relaxation)
        shear = 75 * relaxation + 30 * (1 - relaxation)
        creep = 0.15 * (1 - relaxation)
        
        rows.append([t, round(T, 1), phase, round(VM_anode, 1),
                    round(VM_electrolyte, 1), round(VM_cathode, 1),
                    round(VM_interconnect, 1), round(max_principal, 1),
                    round(shear, 1), round(creep, 4)])
    
    # Phase 3: Cooling (6200 to 8800 s, 800 to 25°C)
    for t in range(6200, 8801, 200):
        T = 800 - (800 - 25) * ((t - 6200) / 2600)
        phase = "Cooling"
        
        # Stress builds up again during cooling (reverse thermal expansion)
        stress_factor = (t - 6200) / 2600
        VM_anode = 60 + 95 * stress_factor
        VM_electrolyte = 140 + 210 * stress_factor
        VM_cathode = 50 + 85 * stress_factor
        VM_interconnect = 100 + 160 * stress_factor
        max_principal = 170 + 250 * stress_factor
        shear = 35 + 60 * stress_factor
        creep = 0.12  # Accumulated creep strain
        
        rows.append([t, round(T, 1), phase, round(VM_anode, 1),
                    round(VM_electrolyte, 1), round(VM_cathode, 1),
                    round(VM_interconnect, 1), round(max_principal, 1),
                    round(shear, 1), round(creep, 4)])
    
    columns = ['Time_s', 'Temperature_C', 'Phase', 'VonMises_Anode_MPa',
               'VonMises_Electrolyte_MPa', 'VonMises_Cathode_MPa', 
               'VonMises_Interconnect_MPa', 'Max_Principal_Electrolyte_MPa',
               'Interface_Shear_MPa', 'Creep_Strain_pct']
    
    write_csv_with_header('10_stress_evolution_thermal_cycle.csv', DISCLAIMER_HEADER, columns, rows)


def generate_11_cell_geometry():
    """Generate layer dimensions for anode-supported planar SOFC."""
    rows = [
        ['Anode support', 'Ni-8YSZ', 500, 100, 100, 'Load-bearing structural layer'],
        ['Anode functional layer (AFL)', 'Ni-8YSZ', 15, 100, 100, 'Electrochemically active anode'],
        ['Electrolyte', '8YSZ', 10, 100, 100, 'Dense oxygen ion conductor'],
        ['GDC buffer layer', 'GDC', 5, 100, 100, 'Prevents Sr diffusion / interdiffusion'],
        ['Cathode functional layer (CFL)', 'LSCF', 15, 100, 100, 'Electrochemically active cathode'],
        ['Cathode current collector', 'LSM', 30, 100, 100, 'Electronic conductor'],
        ['Interconnect', 'Crofer 22 APU', 500, 100, 100, 'Bipolar plate / gas separator'],
        ['Fuel channel', 'Gas flow', 1000, 3, 100, 'H2 + H2O distribution'],
        ['Air channel', 'Gas flow', 1000, 2, 100, 'Air (O2 + N2) distribution'],
        ['Sealant', 'Glass-ceramic', 50, 5, 105, 'Edge sealing / gas separation'],
    ]
    
    columns = ['Layer_Name', 'Material', 'Thickness_um', 'Length_mm', 
               'Width_mm', 'Function']
    
    write_csv_with_header('11_cell_geometry.csv', DISCLAIMER_HEADER, columns, rows)


def generate_12_operating_conditions():
    """Generate test matrix with 12 operating scenarios."""
    rows = [
        ['SS-01', 'Steady-state', 750, 0.5, 97, 3, 21, 0, 'Baseline performance', 1.0],
        ['SS-02', 'Steady-state', 800, 0.5, 97, 3, 21, 0, 'Mid-temperature operation', 1.0],
        ['SS-03', 'Steady-state', 850, 0.5, 97, 3, 21, 0, 'High-temperature operation', 1.0],
        ['SS-04', 'Steady-state', 800, 0.3, 97, 3, 21, 0, 'Low current density', 1.0],
        ['SS-05', 'Steady-state', 800, 0.8, 97, 3, 21, 0, 'High current density', 1.0],
        ['DYN-01', 'Load cycling', 800, '0.2-0.8', 97, 3, 21, 0, 'Dynamic load variation (1 hour cycles)', 1.0],
        ['DYN-02', 'Load step', 800, '0.3→0.7', 97, 3, 21, 0, 'Sudden load increase', 1.0],
        ['TC-01', 'Thermal cycling', '25-800', 0.5, 97, 3, 21, 0, 'Startup-shutdown (5°C/min ramp)', 1.0],
        ['TC-02', 'Thermal cycling', '25-800', 0.5, 97, 3, 21, 0, 'Rapid thermal cycling (20°C/min)', 1.0],
        ['REDOX-01', 'Redox cycling', 800, 0, 97, 3, 0, 5, 'Oxidation: switch to air on anode side', 0.2],
        ['REDOX-02', 'Redox cycling', 800, 0.5, 97, 3, 21, 0, 'Re-reduction: restore H2 fuel', 0.9],
        ['DEG-01', 'Long-term', 800, 0.5, 97, 3, 21, 0, 'Degradation study (1000 hours)', 0.85],
    ]
    
    columns = ['Test_ID', 'Mode', 'Temperature_C', 'Current_Density_A_per_cm2',
               'H2_pct', 'H2O_pct', 'O2_pct', 'Exposure_Time_min',
               'Description', 'Fuel_Utilization']
    
    write_csv_with_header('12_operating_conditions.csv', DISCLAIMER_HEADER, columns, rows)


def generate_13_residual_stress():
    """Generate XRD / neutron diffraction residual stress data."""
    rows = [
        ['As-sintered', 'Anode', 'Center', -45, 15, 280, 'XRD sin²ψ', 'Compressive, Ni phase'],
        ['As-sintered', 'Anode', 'Edge', -62, 18, 220, 'XRD sin²ψ', 'Edge effect / gradient'],
        ['As-sintered', 'Electrolyte', 'Center', 185, 25, 850, 'Neutron diffraction', 'Tensile, constrained'],
        ['As-sintered', 'Electrolyte', 'Edge', 210, 30, 780, 'Neutron diffraction', 'Higher at edge'],
        ['As-sintered', 'Cathode', 'Center', -28, 12, 320, 'XRD', 'Compressive'],
        ['As-sintered', 'Cathode', 'Edge', -35, 14, 290, 'XRD', 'Edge effect'],
        ['After reduction', 'Anode', 'Center', -120, 22, 450, 'Neutron diffraction', 'Ni expansion → compression'],
        ['After reduction', 'Electrolyte', 'Center', 285, 35, 950, 'Neutron diffraction', 'Increased tensile'],
        ['After 100 cycles', 'Anode', 'Center', -85, 28, 520, 'Neutron diffraction', 'Partial relaxation'],
        ['After 100 cycles', 'Electrolyte', 'Center', 245, 40, 880, 'Neutron diffraction', 'Creep relaxation'],
        ['After 100 cycles', 'Cathode', 'Center', -18, 16, 340, 'XRD', 'Relaxation + microcracking'],
        ['After 100 cycles', 'Interface (Anode/Electrolyte)', 'Center', 95, 45, 620, 'Synchrotron XRD', 'Shear component present'],
    ]
    
    columns = ['Condition', 'Layer', 'Location', 'Stress_In_Plane_MPa',
               'Uncertainty_MPa', 'Peak_Count', 'Measurement_Technique', 'Notes']
    
    write_csv_with_header('13_residual_stress.csv', DISCLAIMER_HEADER, columns, rows)


def generate_14_redox_cycling():
    """Generate chemical expansion and degradation during redox cycling."""
    rows = [
        [0, 'Initial', 0, 0, 0, 0.62, 0.18, 'Fresh reduced cell'],
        [1, 'Oxidation', 5, 0.42, 2.8, 0, 0, 'Anode exposed to air → NiO formation'],
        [1, 'Re-reduction', 10, -0.38, -2.5, 0.58, 0.21, 'NiO → Ni, but microstructural damage'],
        [2, 'Oxidation', 5, 0.40, 2.6, 0, 0, 'Repeated oxidation'],
        [2, 'Re-reduction', 10, -0.36, -2.3, 0.54, 0.24, 'Further degradation'],
        [5, 'Re-reduction', 10, -0.30, -2.0, 0.45, 0.32, 'Cumulative damage, particle coarsening'],
        [10, 'Re-reduction', 10, -0.22, -1.5, 0.35, 0.45, 'Significant Ni agglomeration'],
        [15, 'Re-reduction', 10, -0.18, -1.2, 0.28, 0.58, 'Loss of percolation pathways'],
        [20, 'Re-reduction', 10, -0.14, -0.9, 0.21, 0.75, 'Severe degradation, delamination risk'],
        [20, 'Final', 0, -0.12, -0.8, 0.19, 0.82, 'Post-mortem sample'],
        [20, 'Observation', 0, 0, 0, 0, 0, 'SEM shows Ni particle size increased from 0.5 to 3 μm'],
    ]
    
    columns = ['Cycle_Number', 'Phase', 'Exposure_Time_min', 'Volume_Change_pct',
               'In_Plane_Strain_pct', 'Peak_Power_W_per_cm2', 'ASR_Ohm_cm2', 'Notes']
    
    write_csv_with_header('14_redox_cycling.csv', DISCLAIMER_HEADER, columns, rows)


def generate_15_FEM_input_summary():
    """Generate quick-reference table for FEM input."""
    rows = [
        ['Elastic Modulus (800°C)', 189.4, 181.6, 79.2, 86.9, 135.8, 188.0, 'GPa', 'Temperature-dependent'],
        ['Poisson Ratio', 0.31, 0.33, 0.30, 0.26, 0.29, 0.30, '-', 'Assumed constant'],
        ['CTE (800°C)', 11.66, 12.84, 14.42, 16.24, 12.00, 12.00, '1e-6/K', 'Average 25-800°C'],
        ['Thermal Conductivity (800°C)', 2.32, 3.22, 6.40, 2.70, 2.60, 26.80, 'W/m·K', 'At operating temp'],
        ['Specific Heat (800°C)', 523, 526, 530, 546, 526, 620, 'J/kg·K', 'At operating temp'],
        ['Density', 5900, 7220, 4460, 6300, 6500, 7700, 'kg/m³', 'Constant'],
        ['Flexural Strength (800°C)', 226.2, 163.6, 108.3, 74.5, 108.6, 445.2, 'MPa', 'Temperature-dependent'],
        ['Fracture Toughness (800°C)', 1.81, 1.36, 1.50, 0.83, 1.09, 68.47, 'MPa√m', 'Temperature-dependent'],
        ['Weibull Modulus (800°C)', 9.1, 7.3, 5.9, 5.0, 7.3, 25.7, '-', 'Temperature-dependent'],
        ['Creep: Stress Exponent (800°C)', 1.8, 1.5, 2.6, 2.2, 1.6, 5.5, '-', 'Norton power-law'],
        ['Creep: Activation Energy', 400, 380, 240, 280, 290, 330, 'kJ/mol', 'Norton power-law'],
        ['Creep: Pre-exponential (800°C)', 1.2e-11, 8.5e-12, 3.8e-9, 5.2e-10, 4.0e-10, 8.5e-14, '1/Pa^n/s', 'Norton power-law'],
        ['Thermal Expansion (25→800°C)', 0.90, 1.00, 1.12, 1.26, 0.93, 0.93, '%', 'Integrated CTE'],
        ['Max Service Temperature', 1000, 900, 1000, 900, 1000, 900, '°C', 'Material limit'],
        ['Electrical Conductivity (800°C)', 0.05, 8, 5000, 150, 180, 10000, 'S/cm', 'Order of magnitude'],
        ['Ionic Conductivity (800°C)', 0.08, 0.12, 0.0001, 0.0001, 0.0001, 0, 'S/cm', 'Oxygen ion conduction'],
        ['Layer Thickness (typical)', 10, 5, 500, 15, 30, 500, 'μm', 'Anode-supported design'],
        ['Porosity (typical)', 0, 0, 30, 35, 30, 0, '%', 'Electrode porosity'],
        ['Particle Size (typical)', 0.5, 0.3, 0.5, 0.8, 1.2, '-', 'μm', 'As-fabricated'],
        ['TPB Length Density', '-', '-', 3.5, 8.2, 5.1, '-', 'μm/μm³', 'Electrochemically active'],
        ['Sintering Temperature', 1400, 1350, 1400, 1100, 1200, 1050, '°C', 'Fabrication'],
        ['Operating Voltage Range', '-', '-', '-', '-', '-', '-', 'V', '0.6-0.9 V typical'],
        ['Fuel Utilization', '-', '-', '-', '-', '-', '-', '%', '80-90% typical'],
        ['Air Stoichiometry', '-', '-', '-', '-', '-', '-', '-', '3-6 typical'],
        ['H2 Composition', '-', '-', '-', '-', '-', '-', '%', '95-97% H2 + 3-5% H2O'],
        ['Current Density Range', '-', '-', '-', '-', '-', '-', 'A/cm²', '0.3-0.8 typical operation'],
        ['Area-Specific Resistance (800°C)', '-', '-', '-', '-', '-', '-', 'Ω·cm²', '0.15-0.25 total'],
        ['Cell Active Area', '-', '-', '-', '-', '-', '-', 'cm²', '100 (10×10 cm design)'],
        ['Stack Power Density', '-', '-', '-', '-', '-', '-', 'W/cm²', '0.4-0.6 at 0.7V'],
        ['Lifetime Target', '-', '-', '-', '-', '-', '-', 'hours', '40,000-80,000 for stationary'],
    ]
    
    columns = ['Property', '8YSZ', 'GDC', 'Ni-YSZ', 'LSCF', 'LSM', 'Crofer 22 APU',
               'Unit', 'Notes']
    
    write_csv_with_header('15_FEM_input_summary.csv', DISCLAIMER_HEADER, columns, rows)


def main():
    """Generate all 15 CSV dataset files."""
    print("=" * 60)
    print("SOFC Thermo-Mechanical Dataset Generator")
    print("=" * 60)
    print("\nWARNING: All data is SYNTHETIC/ILLUSTRATIVE")
    print("Based on published literature ranges for educational use only\n")
    
    print("Generating dataset files in:", DATA_DIR)
    print()
    
    # Generate all datasets
    generate_01_thermal_properties()
    generate_02_mechanical_properties()
    generate_03_creep_parameters()
    generate_04_creep_curves()
    generate_05_CTE_mismatch()
    generate_06_polarization_curves()
    generate_07_thermal_cycling()
    generate_08_strain_hardening()
    generate_09_temperature_distribution()
    generate_10_stress_evolution()
    generate_11_cell_geometry()
    generate_12_operating_conditions()
    generate_13_residual_stress()
    generate_14_redox_cycling()
    generate_15_FEM_input_summary()
    
    print()
    print("=" * 60)
    print("✓ All 15 CSV files generated successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run visualization scripts: python plot_*.py")
    print("2. Package data: python generate_zip.py")
    print("3. See README.md for full documentation")


if __name__ == '__main__':
    main()
