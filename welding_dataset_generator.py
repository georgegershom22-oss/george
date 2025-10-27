#!/usr/bin/env python3
"""
Comprehensive Welding Dataset Generator for ML-Driven Inverse Design
====================================================================

This script generates a realistic, comprehensive dataset for machine learning-driven 
inverse design of welding parameters, focusing on extreme-temperature cycling performance.

Dataset Structure:
- Part 1: Input Parameters (Design Space) - What we can control
- Part 2: Characterization & Quality Metrics - Immediate weld quality
- Part 3: Performance & Validation Metrics - Long-term performance under cycling

Author: AI Assistant
Date: 2025-10-27
"""

import numpy as np
import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

class WeldingDatasetGenerator:
    """Generate comprehensive welding dataset with realistic correlations."""
    
    def __init__(self, n_samples: int = 10000):
        self.n_samples = n_samples
        self.dataset = {}
        self.metadata = {
            'generation_date': datetime.now().isoformat(),
            'n_samples': n_samples,
            'description': 'ML-Driven Inverse Design of Welding Parameters Dataset',
            'version': '1.0.0'
        }
        
    def generate_input_parameters(self) -> pd.DataFrame:
        """Generate Part 1: Input Parameters (Design Space)"""
        print("Generating Part 1: Input Parameters...")
        
        # Material combinations (realistic battery tab welding scenarios)
        materials = [
            ('Copper', 'Aluminum'), ('Copper', 'Nickel'), ('Aluminum', 'Aluminum'),
            ('Nickel', 'Copper'), ('Copper', 'Steel'), ('Aluminum', 'Steel'),
            ('Titanium', 'Copper'), ('Brass', 'Aluminum')
        ]
        
        # Surface finishes and coatings
        surface_finishes = [
            'Bare', 'Nickel-plated', 'Tin-plated', 'Silver-plated', 
            'Oxide-cleaned', 'Anodized', 'Passivated', 'Electropolished'
        ]
        
        # Welding techniques
        welding_techniques = [
            'Ultrasonic Welding', 'Laser Welding', 'Resistance Spot Welding',
            'Friction Stir Welding', 'Electron Beam Welding', 'Cold Welding'
        ]
        
        data = []
        
        for i in range(self.n_samples):
            # Base Materials
            anode_mat, cathode_mat = materials[np.random.randint(0, len(materials))]
            
            # Tab thickness (realistic for battery applications)
            tab_thickness = np.random.uniform(50, 500)  # 50-500 μm
            
            # Surface finish
            anode_finish = surface_finishes[np.random.randint(0, len(surface_finishes))]
            cathode_finish = surface_finishes[np.random.randint(0, len(surface_finishes))]
            
            # Welding technique
            technique = welding_techniques[np.random.randint(0, len(welding_techniques))]
            
            # Process parameters (technique-dependent)
            if technique == 'Ultrasonic Welding':
                power = np.random.uniform(500, 3000)  # W
                amplitude = np.random.uniform(10, 50)  # μm
                force = np.random.uniform(100, 2000)  # N
                time = np.random.uniform(0.1, 2.0)  # s
                speed = np.nan
                pulse_freq = np.nan
            elif technique == 'Laser Welding':
                power = np.random.uniform(100, 2000)  # W (continuous)
                amplitude = np.nan
                force = np.random.uniform(0, 500)  # N (clamping)
                time = np.random.uniform(0.001, 0.1)  # s (pulse duration)
                speed = np.random.uniform(10, 200)  # mm/s
                pulse_freq = np.random.uniform(1, 1000)  # Hz
            elif technique == 'Resistance Spot Welding':
                power = np.random.uniform(1000, 8000)  # W
                amplitude = np.nan
                force = np.random.uniform(500, 5000)  # N
                time = np.random.uniform(0.1, 1.0)  # s
                speed = np.nan
                pulse_freq = np.nan
            else:  # Other techniques
                power = np.random.uniform(200, 4000)
                amplitude = np.random.uniform(5, 100) if np.random.random() > 0.5 else np.nan
                force = np.random.uniform(50, 3000)
                time = np.random.uniform(0.05, 5.0)
                speed = np.random.uniform(5, 300) if np.random.random() > 0.5 else np.nan
                pulse_freq = np.random.uniform(0.1, 500) if np.random.random() > 0.5 else np.nan
            
            # Environmental conditions
            preheat_temp = np.random.uniform(20, 150)  # °C
            ambient_humidity = np.random.uniform(30, 80)  # %
            ambient_temp = np.random.uniform(18, 35)  # °C
            
            # Additional realistic parameters
            electrode_material = np.random.choice(['Copper', 'Tungsten', 'Molybdenum', 'Graphite'])
            shielding_gas = np.random.choice(['Argon', 'Nitrogen', 'Air', 'Helium', 'None'])
            surface_roughness = np.random.uniform(0.1, 5.0)  # μm Ra
            
            sample = {
                'sample_id': f'WLD_{i+1:06d}',
                'anode_material': anode_mat,
                'cathode_material': cathode_mat,
                'tab_thickness_um': round(tab_thickness, 1),
                'anode_surface_finish': anode_finish,
                'cathode_surface_finish': cathode_finish,
                'welding_technique': technique,
                'power_W': round(power, 1),
                'amplitude_um': round(amplitude, 1) if not np.isnan(amplitude) else np.nan,
                'force_N': round(force, 1),
                'time_s': round(time, 3),
                'speed_mm_s': round(speed, 1) if not np.isnan(speed) else np.nan,
                'pulse_frequency_Hz': round(pulse_freq, 1) if not np.isnan(pulse_freq) else np.nan,
                'preheat_temperature_C': round(preheat_temp, 1),
                'ambient_temperature_C': round(ambient_temp, 1),
                'ambient_humidity_percent': round(ambient_humidity, 1),
                'electrode_material': electrode_material,
                'shielding_gas': shielding_gas,
                'surface_roughness_um': round(surface_roughness, 2)
            }
            
            data.append(sample)
        
        return pd.DataFrame(data)
    
    def generate_characterization_metrics(self, input_df: pd.DataFrame) -> pd.DataFrame:
        """Generate Part 2: Characterization & Quality Metrics"""
        print("Generating Part 2: Characterization & Quality Metrics...")
        
        data = []
        
        for idx, row in input_df.iterrows():
            # Create realistic correlations based on physics
            
            # Material-dependent base properties
            mat_properties = self._get_material_properties(row['anode_material'], row['cathode_material'])
            
            # Weld geometry (influenced by process parameters)
            weld_width = self._calculate_weld_width(row)
            weld_depth = self._calculate_weld_depth(row)
            nugget_diameter = self._calculate_nugget_diameter(row)
            
            # Mechanical properties
            tensile_strength = self._calculate_tensile_strength(row, mat_properties)
            shear_strength = self._calculate_shear_strength(row, mat_properties)
            peel_strength = self._calculate_peel_strength(row, mat_properties)
            
            # Electrical properties
            contact_resistance = self._calculate_contact_resistance(row, mat_properties)
            conductivity = self._calculate_conductivity(row, mat_properties)
            
            # Microstructural features
            grain_size = self._calculate_grain_size(row)
            porosity = self._calculate_porosity(row)
            intermetallic_thickness = self._calculate_intermetallic_thickness(row, mat_properties)
            
            # Thermal properties
            thermal_conductivity = self._calculate_thermal_conductivity(row, mat_properties)
            heat_affected_zone = self._calculate_haz_width(row)
            
            # Quality indicators
            weld_quality_score = self._calculate_quality_score(
                tensile_strength, contact_resistance, porosity, intermetallic_thickness
            )
            
            # Defect analysis
            defects = self._generate_defect_analysis(row, porosity)
            
            sample = {
                'sample_id': row['sample_id'],
                'weld_width_mm': round(weld_width, 3),
                'weld_depth_mm': round(weld_depth, 3),
                'nugget_diameter_mm': round(nugget_diameter, 3),
                'tensile_strength_MPa': round(tensile_strength, 1),
                'shear_strength_MPa': round(shear_strength, 1),
                'peel_strength_N_mm': round(peel_strength, 1),
                'contact_resistance_mohm': round(contact_resistance, 4),
                'electrical_conductivity_MS_m': round(conductivity, 2),
                'grain_size_um': round(grain_size, 1),
                'porosity_percent': round(porosity, 2),
                'intermetallic_thickness_um': round(intermetallic_thickness, 2),
                'thermal_conductivity_W_mK': round(thermal_conductivity, 1),
                'heat_affected_zone_mm': round(heat_affected_zone, 3),
                'weld_quality_score': round(weld_quality_score, 2),
                'surface_roughness_post_weld_um': round(np.random.uniform(0.5, 8.0), 2),
                'hardness_HV': round(np.random.uniform(80, 300), 1),
                'crack_density_per_mm2': round(defects['crack_density'], 3),
                'void_fraction_percent': round(defects['void_fraction'], 3),
                'oxidation_level': defects['oxidation_level'],
                'weld_penetration_percent': round(np.random.uniform(60, 98), 1),
                'fusion_zone_area_mm2': round(weld_width * weld_depth * 0.785, 3)
            }
            
            data.append(sample)
        
        return pd.DataFrame(data)
    
    def generate_performance_metrics(self, input_df: pd.DataFrame, char_df: pd.DataFrame) -> pd.DataFrame:
        """Generate Part 3: Performance & Validation Metrics (Extreme Temperature Cycling)"""
        print("Generating Part 3: Performance & Validation Metrics...")
        
        data = []
        
        for idx, (input_row, char_row) in enumerate(zip(input_df.iterrows(), char_df.iterrows())):
            input_row = input_row[1]  # Get the actual row data
            char_row = char_row[1]
            
            # Temperature cycling parameters
            min_temp = np.random.uniform(-40, -20)  # °C
            max_temp = np.random.uniform(80, 150)   # °C
            cycle_count = np.random.randint(100, 10000)
            
            # Performance degradation over cycling
            initial_resistance = char_row['contact_resistance_mohm']
            resistance_drift = self._calculate_resistance_drift(
                input_row, char_row, cycle_count, min_temp, max_temp
            )
            
            # Mechanical degradation
            strength_retention = self._calculate_strength_retention(
                input_row, char_row, cycle_count, min_temp, max_temp
            )
            
            # Fatigue analysis
            fatigue_life = self._calculate_fatigue_life(input_row, char_row, min_temp, max_temp)
            crack_growth_rate = self._calculate_crack_growth_rate(input_row, char_row)
            
            # Thermal cycling specific metrics
            thermal_expansion_mismatch = self._calculate_thermal_expansion_mismatch(input_row)
            stress_concentration = self._calculate_stress_concentration(input_row, char_row)
            
            # Failure analysis
            failure_mode = self._determine_failure_mode(input_row, char_row, cycle_count)
            time_to_failure = self._calculate_time_to_failure(
                input_row, char_row, cycle_count, min_temp, max_temp
            )
            
            # Performance scores (targets for inverse design)
            cycle_life_score = self._calculate_cycle_life_score(cycle_count, fatigue_life)
            reliability_score = self._calculate_reliability_score(
                resistance_drift, strength_retention, failure_mode
            )
            
            sample = {
                'sample_id': input_row['sample_id'],
                'min_cycle_temperature_C': round(min_temp, 1),
                'max_cycle_temperature_C': round(max_temp, 1),
                'total_cycles_tested': cycle_count,
                'initial_contact_resistance_mohm': round(initial_resistance, 4),
                'final_contact_resistance_mohm': round(initial_resistance * (1 + resistance_drift), 4),
                'resistance_drift_percent': round(resistance_drift * 100, 2),
                'tensile_strength_retention_percent': round(strength_retention * 100, 1),
                'shear_strength_retention_percent': round(strength_retention * 0.95 * 100, 1),
                'fatigue_life_cycles': int(fatigue_life),
                'crack_growth_rate_mm_cycle': round(crack_growth_rate, 8),
                'thermal_expansion_mismatch_ppm_K': round(thermal_expansion_mismatch, 2),
                'stress_concentration_factor': round(stress_concentration, 2),
                'primary_failure_mode': failure_mode,
                'time_to_failure_hours': round(time_to_failure, 1),
                'cycle_life_score': round(cycle_life_score, 3),
                'reliability_score': round(reliability_score, 3),
                'temperature_stability_index': round(np.random.uniform(0.6, 0.98), 3),
                'corrosion_resistance_score': round(np.random.uniform(0.7, 0.95), 3),
                'dimensional_stability_um': round(np.random.uniform(0.1, 5.0), 2),
                'interface_adhesion_strength_MPa': round(np.random.uniform(50, 200), 1),
                'oxidation_resistance_score': round(np.random.uniform(0.5, 0.9), 3),
                'creep_resistance_score': round(np.random.uniform(0.6, 0.95), 3)
            }
            
            data.append(sample)
        
        return pd.DataFrame(data)
    
    def _get_material_properties(self, anode_mat: str, cathode_mat: str) -> Dict:
        """Get material-specific properties for realistic calculations."""
        properties = {
            'Copper': {'conductivity': 59.6, 'strength': 220, 'expansion': 16.5},
            'Aluminum': {'conductivity': 37.8, 'strength': 90, 'expansion': 23.1},
            'Nickel': {'conductivity': 14.3, 'strength': 317, 'expansion': 13.4},
            'Steel': {'conductivity': 6.0, 'strength': 400, 'expansion': 11.0},
            'Titanium': {'conductivity': 2.4, 'strength': 434, 'expansion': 8.6},
            'Brass': {'conductivity': 28.0, 'strength': 200, 'expansion': 20.3}
        }
        
        anode_props = properties.get(anode_mat, properties['Copper'])
        cathode_props = properties.get(cathode_mat, properties['Aluminum'])
        
        return {
            'avg_conductivity': (anode_props['conductivity'] + cathode_props['conductivity']) / 2,
            'avg_strength': (anode_props['strength'] + cathode_props['strength']) / 2,
            'expansion_mismatch': abs(anode_props['expansion'] - cathode_props['expansion'])
        }
    
    def _calculate_weld_width(self, row: pd.Series) -> float:
        """Calculate weld width based on process parameters."""
        base_width = 0.5  # mm
        
        # Power influence
        power_factor = (row['power_W'] / 1000) * 0.3
        
        # Time influence
        time_factor = row['time_s'] * 0.2
        
        # Technique-specific adjustments
        if row['welding_technique'] == 'Laser Welding':
            width = base_width + power_factor * 0.5 + time_factor * 0.3
        elif row['welding_technique'] == 'Ultrasonic Welding':
            amplitude_factor = (row['amplitude_um'] / 50) * 0.2 if not pd.isna(row['amplitude_um']) else 0
            width = base_width + power_factor * 0.3 + amplitude_factor
        else:
            width = base_width + power_factor + time_factor * 0.1
        
        return max(0.1, width + np.random.normal(0, 0.05))
    
    def _calculate_weld_depth(self, row: pd.Series) -> float:
        """Calculate weld depth based on process parameters."""
        base_depth = 0.1  # mm
        
        power_factor = (row['power_W'] / 1000) * 0.15
        time_factor = row['time_s'] * 0.1
        thickness_factor = row['tab_thickness_um'] / 1000 * 0.5  # Convert to mm
        
        depth = base_depth + power_factor + time_factor + thickness_factor
        
        return max(0.05, min(depth + np.random.normal(0, 0.02), row['tab_thickness_um'] / 1000))
    
    def _calculate_nugget_diameter(self, row: pd.Series) -> float:
        """Calculate nugget diameter for spot welds."""
        if row['welding_technique'] == 'Resistance Spot Welding':
            base_diameter = 2.0
            force_factor = (row['force_N'] / 1000) * 0.5
            power_factor = (row['power_W'] / 1000) * 0.3
            return base_diameter + force_factor + power_factor + np.random.normal(0, 0.1)
        else:
            return np.random.uniform(1.0, 4.0)
    
    def _calculate_tensile_strength(self, row: pd.Series, mat_props: Dict) -> float:
        """Calculate tensile strength based on materials and process."""
        base_strength = mat_props['avg_strength']
        
        # Process optimization factors
        power_efficiency = min(1.0, row['power_W'] / 2000)
        time_efficiency = min(1.0, row['time_s'] / 1.0)
        
        # Surface finish bonus
        finish_bonus = 1.1 if 'plated' in row['anode_surface_finish'].lower() else 1.0
        
        strength = base_strength * power_efficiency * time_efficiency * finish_bonus
        
        return max(50, strength + np.random.normal(0, strength * 0.1))
    
    def _calculate_shear_strength(self, row: pd.Series, mat_props: Dict) -> float:
        """Calculate shear strength (typically 60-80% of tensile)."""
        tensile = self._calculate_tensile_strength(row, mat_props)
        return tensile * np.random.uniform(0.6, 0.8)
    
    def _calculate_peel_strength(self, row: pd.Series, mat_props: Dict) -> float:
        """Calculate peel strength (force per unit width)."""
        base_peel = 50  # N/mm
        thickness_factor = row['tab_thickness_um'] / 200
        force_factor = row['force_N'] / 1000
        
        return base_peel * thickness_factor * force_factor + np.random.normal(0, 10)
    
    def _calculate_contact_resistance(self, row: pd.Series, mat_props: Dict) -> float:
        """Calculate contact resistance based on materials and process quality."""
        base_resistance = 1.0 / mat_props['avg_conductivity'] * 100  # mΩ
        
        # Surface finish impact
        finish_factor = 0.5 if 'plated' in row['anode_surface_finish'].lower() else 1.0
        
        # Process quality impact
        force_factor = max(0.3, 1000 / row['force_N'])
        roughness_factor = row['surface_roughness_um'] / 2.0
        
        resistance = base_resistance * finish_factor * force_factor * roughness_factor
        
        return max(0.01, resistance + np.random.normal(0, resistance * 0.2))
    
    def _calculate_conductivity(self, row: pd.Series, mat_props: Dict) -> float:
        """Calculate electrical conductivity."""
        base_conductivity = mat_props['avg_conductivity']
        
        # Process-induced changes
        heat_effect = 0.9 if row['power_W'] > 2000 else 0.95
        
        return base_conductivity * heat_effect + np.random.normal(0, base_conductivity * 0.05)
    
    def _calculate_grain_size(self, row: pd.Series) -> float:
        """Calculate grain size based on thermal history."""
        base_grain_size = 10  # μm
        
        # Higher power and longer time = larger grains
        power_factor = (row['power_W'] / 1000) * 2
        time_factor = row['time_s'] * 5
        
        return base_grain_size + power_factor + time_factor + np.random.normal(0, 2)
    
    def _calculate_porosity(self, row: pd.Series) -> float:
        """Calculate porosity percentage."""
        base_porosity = 0.5  # %
        
        # High power, short time can cause porosity
        if row['power_W'] > 2000 and row['time_s'] < 0.1:
            porosity_factor = 2.0
        else:
            porosity_factor = 1.0
        
        # Force helps reduce porosity
        force_factor = max(0.5, 1000 / row['force_N'])
        
        return max(0, base_porosity * porosity_factor * force_factor + np.random.normal(0, 0.2))
    
    def _calculate_intermetallic_thickness(self, row: pd.Series, mat_props: Dict) -> float:
        """Calculate intermetallic layer thickness for dissimilar materials."""
        if row['anode_material'] == row['cathode_material']:
            return np.random.uniform(0, 0.5)  # Minimal for similar materials
        
        base_thickness = 1.0  # μm
        
        # Temperature and time promote intermetallic growth
        power_factor = (row['power_W'] / 1000) * 0.5
        time_factor = row['time_s'] * 2
        
        return base_thickness + power_factor + time_factor + np.random.normal(0, 0.3)
    
    def _calculate_thermal_conductivity(self, row: pd.Series, mat_props: Dict) -> float:
        """Calculate thermal conductivity of the weld."""
        return mat_props['avg_conductivity'] * 0.8 + np.random.normal(0, 5)
    
    def _calculate_haz_width(self, row: pd.Series) -> float:
        """Calculate heat-affected zone width."""
        base_haz = 0.2  # mm
        
        power_factor = (row['power_W'] / 1000) * 0.3
        time_factor = row['time_s'] * 0.1
        
        return base_haz + power_factor + time_factor + np.random.normal(0, 0.05)
    
    def _calculate_quality_score(self, tensile: float, resistance: float, 
                               porosity: float, intermetallic: float) -> float:
        """Calculate overall weld quality score (0-1)."""
        # Normalize metrics (higher is better for tensile, lower for others)
        tensile_norm = min(1.0, tensile / 300)
        resistance_norm = max(0, 1.0 - resistance / 10)
        porosity_norm = max(0, 1.0 - porosity / 5)
        intermetallic_norm = max(0, 1.0 - intermetallic / 10)
        
        return (tensile_norm + resistance_norm + porosity_norm + intermetallic_norm) / 4
    
    def _generate_defect_analysis(self, row: pd.Series, porosity: float) -> Dict:
        """Generate defect analysis data."""
        return {
            'crack_density': max(0, porosity / 10 + np.random.normal(0, 0.1)),
            'void_fraction': porosity + np.random.normal(0, 0.2),
            'oxidation_level': np.random.choice(['Low', 'Medium', 'High'], p=[0.6, 0.3, 0.1])
        }
    
    def _calculate_resistance_drift(self, input_row: pd.Series, char_row: pd.Series,
                                  cycles: int, min_temp: float, max_temp: float) -> float:
        """Calculate resistance drift over thermal cycling."""
        base_drift = 0.01  # 1% base drift
        
        # Cycle count effect
        cycle_factor = (cycles / 5000) * 0.1
        
        # Temperature range effect
        temp_range_factor = (max_temp - min_temp) / 100 * 0.05
        
        # Material mismatch effect
        if input_row['anode_material'] != input_row['cathode_material']:
            mismatch_factor = 0.02
        else:
            mismatch_factor = 0
        
        # Initial quality effect
        quality_factor = (1 - char_row['weld_quality_score']) * 0.1
        
        total_drift = base_drift + cycle_factor + temp_range_factor + mismatch_factor + quality_factor
        
        return max(0, total_drift + np.random.normal(0, total_drift * 0.3))
    
    def _calculate_strength_retention(self, input_row: pd.Series, char_row: pd.Series,
                                    cycles: int, min_temp: float, max_temp: float) -> float:
        """Calculate strength retention after cycling."""
        base_retention = 0.95  # 95% base retention
        
        # Degradation factors
        cycle_degradation = (cycles / 10000) * 0.2
        temp_degradation = (max_temp - min_temp) / 200 * 0.1
        quality_bonus = char_row['weld_quality_score'] * 0.1
        
        retention = base_retention - cycle_degradation - temp_degradation + quality_bonus
        
        return max(0.3, min(1.0, retention + np.random.normal(0, 0.05)))
    
    def _calculate_fatigue_life(self, input_row: pd.Series, char_row: pd.Series,
                              min_temp: float, max_temp: float) -> float:
        """Calculate fatigue life in cycles."""
        base_life = 50000  # cycles
        
        # Quality factor
        quality_factor = char_row['weld_quality_score'] * 2
        
        # Temperature range factor
        temp_factor = max(0.1, 1 - (max_temp - min_temp) / 200)
        
        # Material factor
        strength_factor = char_row['tensile_strength_MPa'] / 200
        
        life = base_life * quality_factor * temp_factor * strength_factor
        
        return max(100, life + np.random.normal(0, life * 0.3))
    
    def _calculate_crack_growth_rate(self, input_row: pd.Series, char_row: pd.Series) -> float:
        """Calculate crack growth rate."""
        base_rate = 1e-6  # mm/cycle
        
        # Quality inversely affects crack growth
        quality_factor = 2 - char_row['weld_quality_score']
        
        # Porosity increases crack growth
        porosity_factor = 1 + char_row['porosity_percent'] / 5
        
        return base_rate * quality_factor * porosity_factor + np.random.normal(0, base_rate * 0.5)
    
    def _calculate_thermal_expansion_mismatch(self, input_row: pd.Series) -> float:
        """Calculate thermal expansion mismatch."""
        mat_props = self._get_material_properties(
            input_row['anode_material'], input_row['cathode_material']
        )
        
        return mat_props['expansion_mismatch'] + np.random.normal(0, 2)
    
    def _calculate_stress_concentration(self, input_row: pd.Series, char_row: pd.Series) -> float:
        """Calculate stress concentration factor."""
        base_factor = 1.5
        
        # Geometry effects
        geometry_factor = char_row['weld_width_mm'] / char_row['weld_depth_mm'] * 0.1
        
        # Defect effects
        defect_factor = char_row['porosity_percent'] / 5 * 0.5
        
        return base_factor + geometry_factor + defect_factor + np.random.normal(0, 0.2)
    
    def _determine_failure_mode(self, input_row: pd.Series, char_row: pd.Series, cycles: int) -> str:
        """Determine primary failure mode."""
        modes = ['Interface Delamination', 'Fatigue Cracking', 'Thermal Degradation', 
                'Oxidation', 'Intermetallic Embrittlement', 'Mechanical Wear']
        
        # Probabilistic based on conditions
        if cycles > 5000:
            return np.random.choice(['Fatigue Cracking', 'Thermal Degradation'], p=[0.7, 0.3])
        elif char_row['intermetallic_thickness_um'] > 5:
            return 'Intermetallic Embrittlement'
        elif char_row['contact_resistance_mohm'] > 5:
            return 'Interface Delamination'
        else:
            return np.random.choice(modes)
    
    def _calculate_time_to_failure(self, input_row: pd.Series, char_row: pd.Series,
                                 cycles: int, min_temp: float, max_temp: float) -> float:
        """Calculate time to failure in hours."""
        cycle_time = 0.5  # hours per cycle (assumed)
        fatigue_life = self._calculate_fatigue_life(input_row, char_row, min_temp, max_temp)
        
        # Time to failure is related to fatigue life
        failure_cycles = min(cycles * 2, fatigue_life * np.random.uniform(0.8, 1.2))
        
        return failure_cycles * cycle_time
    
    def _calculate_cycle_life_score(self, tested_cycles: int, fatigue_life: float) -> float:
        """Calculate cycle life performance score (0-1)."""
        return min(1.0, tested_cycles / fatigue_life)
    
    def _calculate_reliability_score(self, resistance_drift: float, 
                                   strength_retention: float, failure_mode: str) -> float:
        """Calculate overall reliability score (0-1)."""
        resistance_score = max(0, 1 - resistance_drift / 0.5)  # Penalize >50% drift
        strength_score = strength_retention
        
        # Failure mode penalty
        failure_penalties = {
            'Interface Delamination': 0.3,
            'Fatigue Cracking': 0.2,
            'Thermal Degradation': 0.25,
            'Oxidation': 0.15,
            'Intermetallic Embrittlement': 0.35,
            'Mechanical Wear': 0.1
        }
        
        failure_penalty = failure_penalties.get(failure_mode, 0.2)
        
        return max(0, (resistance_score + strength_score) / 2 - failure_penalty)
    
    def generate_complete_dataset(self) -> Dict[str, pd.DataFrame]:
        """Generate the complete dataset with all three parts."""
        print(f"Generating comprehensive welding dataset with {self.n_samples} samples...")
        
        # Generate all three parts
        input_params = self.generate_input_parameters()
        char_metrics = self.generate_characterization_metrics(input_params)
        performance_metrics = self.generate_performance_metrics(input_params, char_metrics)
        
        # Store in dataset dictionary
        self.dataset = {
            'input_parameters': input_params,
            'characterization_metrics': char_metrics,
            'performance_metrics': performance_metrics
        }
        
        # Update metadata
        self.metadata.update({
            'input_parameters_shape': input_params.shape,
            'characterization_metrics_shape': char_metrics.shape,
            'performance_metrics_shape': performance_metrics.shape,
            'total_features': sum([df.shape[1] for df in self.dataset.values()]) - 3,  # Subtract sample_id columns
            'feature_categories': {
                'input_parameters': list(input_params.columns),
                'characterization_metrics': list(char_metrics.columns),
                'performance_metrics': list(performance_metrics.columns)
            }
        })
        
        print("Dataset generation complete!")
        return self.dataset
    
    def save_dataset(self, output_dir: str = 'welding_dataset'):
        """Save the complete dataset to files."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save individual CSV files
        for name, df in self.dataset.items():
            filepath = os.path.join(output_dir, f'{name}.csv')
            df.to_csv(filepath, index=False)
            print(f"Saved {name} to {filepath}")
        
        # Save combined dataset
        combined_df = self.dataset['input_parameters'].copy()
        for name, df in self.dataset.items():
            if name != 'input_parameters':
                # Merge on sample_id
                combined_df = combined_df.merge(df, on='sample_id', how='inner')
        
        combined_path = os.path.join(output_dir, 'complete_dataset.csv')
        combined_df.to_csv(combined_path, index=False)
        print(f"Saved complete dataset to {combined_path}")
        
        # Save metadata
        metadata_path = os.path.join(output_dir, 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        print(f"Saved metadata to {metadata_path}")
        
        return output_dir


def main():
    """Main function to generate the dataset."""
    print("=" * 80)
    print("COMPREHENSIVE WELDING DATASET GENERATOR")
    print("ML-Driven Inverse Design of Welding Parameters")
    print("=" * 80)
    
    # Generate dataset
    generator = WeldingDatasetGenerator(n_samples=10000)
    dataset = generator.generate_complete_dataset()
    
    # Save dataset
    output_dir = generator.save_dataset()
    
    print("\n" + "=" * 80)
    print("DATASET GENERATION SUMMARY")
    print("=" * 80)
    print(f"Total samples: {generator.n_samples}")
    print(f"Output directory: {output_dir}")
    print(f"Total features: {generator.metadata['total_features']}")
    
    for name, df in dataset.items():
        print(f"\n{name.replace('_', ' ').title()}:")
        print(f"  Shape: {df.shape}")
        print(f"  Features: {df.shape[1] - 1}")  # Exclude sample_id
    
    print(f"\nDataset saved successfully to: {os.path.abspath(output_dir)}")
    
    return output_dir


if __name__ == "__main__":
    main()