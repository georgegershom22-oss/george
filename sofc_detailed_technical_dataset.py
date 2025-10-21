#!/usr/bin/env python3
"""
SOFC Detailed Technical Specifications Dataset Generator
Comprehensive technical specifications, performance curves, and operational data
"""

import pandas as pd
import numpy as np
import json
import random
from datetime import datetime
import os

class SOFCDetailedTechnicalGenerator:
    def __init__(self):
        self.datasets = {}
        
    def generate_detailed_performance_curves(self):
        """Generate detailed performance curves and operating characteristics"""
        print("Generating detailed performance curves...")
        
        # Generate performance curves for different operating conditions
        performance_data = []
        
        # Temperature ranges
        temperatures = np.arange(600, 1001, 25)  # 600-1000°C
        
        for temp in temperatures:
            # Current density vs voltage curves
            current_densities = np.arange(0.1, 1.6, 0.1)  # A/cm²
            
            for current_density in current_densities:
                # Voltage calculation based on Nernst equation and losses
                nernst_voltage = 1.18 - 0.00045 * temp  # V
                
                # Ohmic losses
                ohmic_resistance = 0.1 + (1000 - temp) * 0.0002  # Ohm·cm²
                ohmic_loss = current_density * ohmic_resistance
                
                # Activation losses
                activation_loss = 0.05 * np.log(current_density / 0.1)
                
                # Concentration losses
                concentration_loss = 0.02 * (current_density ** 2)
                
                # Total voltage
                cell_voltage = nernst_voltage - ohmic_loss - activation_loss - concentration_loss
                cell_voltage = max(0.3, cell_voltage)  # Minimum practical voltage
                
                # Power density
                power_density = cell_voltage * current_density  # W/cm²
                
                # Efficiency calculation
                efficiency = (cell_voltage / 1.25) * 100  # % (assuming 1.25V theoretical)
                
                # Fuel utilization
                fuel_utilization = min(85, 60 + current_density * 20)  # %
                
                performance_data.append({
                    'temperature_c': temp,
                    'current_density_a_cm2': round(current_density, 2),
                    'cell_voltage_v': round(cell_voltage, 3),
                    'power_density_w_cm2': round(power_density, 2),
                    'efficiency_percent': round(efficiency, 1),
                    'fuel_utilization_percent': round(fuel_utilization, 1),
                    'ohmic_loss_v': round(ohmic_loss, 3),
                    'activation_loss_v': round(activation_loss, 3),
                    'concentration_loss_v': round(concentration_loss, 3),
                    'nernst_voltage_v': round(nernst_voltage, 3)
                })
        
        return pd.DataFrame(performance_data)
    
    def generate_material_specifications(self):
        """Generate detailed material specifications and properties"""
        print("Generating material specifications...")
        
        materials = [
            {
                'component': 'Anode',
                'material_type': 'Ni-YSZ (Nickel-Yttria Stabilized Zirconia)',
                'thickness_mm': 0.5,
                'porosity_percent': 35,
                'electrical_conductivity_s_cm': 1000,
                'thermal_conductivity_w_mk': 10,
                'coefficient_thermal_expansion_1_k': 12.5e-6,
                'mechanical_strength_mpa': 200,
                'operating_temperature_range_c': '600-1000',
                'cost_usd_per_kg': 150,
                'supplier_availability': 'Multiple',
                'local_manufacturing_potential': 'Medium'
            },
            {
                'component': 'Cathode',
                'material_type': 'LSM-YSZ (Lanthanum Strontium Manganite)',
                'thickness_mm': 0.05,
                'porosity_percent': 30,
                'electrical_conductivity_s_cm': 100,
                'thermal_conductivity_w_mk': 2,
                'coefficient_thermal_expansion_1_k': 11.0e-6,
                'mechanical_strength_mpa': 150,
                'operating_temperature_range_c': '600-1000',
                'cost_usd_per_kg': 800,
                'supplier_availability': 'Limited',
                'local_manufacturing_potential': 'Low'
            },
            {
                'component': 'Electrolyte',
                'material_type': 'YSZ (Yttria Stabilized Zirconia)',
                'thickness_mm': 0.01,
                'porosity_percent': 0,
                'electrical_conductivity_s_cm': 0.01,
                'thermal_conductivity_w_mk': 2.5,
                'coefficient_thermal_expansion_1_k': 10.5e-6,
                'mechanical_strength_mpa': 300,
                'operating_temperature_range_c': '600-1000',
                'cost_usd_per_kg': 200,
                'supplier_availability': 'Good',
                'local_manufacturing_potential': 'High'
            },
            {
                'component': 'Interconnect',
                'material_type': 'Crofer 22 APU (Ferritic Steel)',
                'thickness_mm': 2.0,
                'porosity_percent': 0,
                'electrical_conductivity_s_cm': 10000,
                'thermal_conductivity_w_mk': 25,
                'coefficient_thermal_expansion_1_k': 12.0e-6,
                'mechanical_strength_mpa': 400,
                'operating_temperature_range_c': '600-800',
                'cost_usd_per_kg': 50,
                'supplier_availability': 'Good',
                'local_manufacturing_potential': 'High'
            },
            {
                'component': 'Seal',
                'material_type': 'Glass-Ceramic Seal',
                'thickness_mm': 0.1,
                'porosity_percent': 0,
                'electrical_conductivity_s_cm': 0,
                'thermal_conductivity_w_mk': 1.5,
                'coefficient_thermal_expansion_1_k': 9.0e-6,
                'mechanical_strength_mpa': 100,
                'operating_temperature_range_c': '600-800',
                'cost_usd_per_kg': 300,
                'supplier_availability': 'Limited',
                'local_manufacturing_potential': 'Medium'
            }
        ]
        
        return pd.DataFrame(materials)
    
    def generate_operational_parameters(self):
        """Generate detailed operational parameters and control strategies"""
        print("Generating operational parameters...")
        
        operational_data = []
        power_ratings = [1, 5, 10, 25, 50, 100, 250, 500, 1000, 2000, 5000]  # kW
        
        for power in power_ratings:
            # Operating parameters
            operating_temperature = random.uniform(750, 850)  # °C
            operating_pressure = random.uniform(1.0, 2.5)  # bar
            
            # Flow rates
            fuel_flow_rate = power * random.uniform(0.8, 1.2)  # m³/h
            air_flow_rate = fuel_flow_rate * random.uniform(6, 8)  # m³/h
            
            # Steam-to-carbon ratio
            steam_carbon_ratio = random.uniform(2.0, 3.0)
            
            # Control parameters
            temperature_control_accuracy = random.uniform(2, 5)  # °C
            pressure_control_accuracy = random.uniform(0.1, 0.3)  # bar
            flow_control_accuracy = random.uniform(2, 5)  # %
            
            # Safety parameters
            max_operating_temperature = operating_temperature + 50  # °C
            min_operating_temperature = operating_temperature - 100  # °C
            max_operating_pressure = operating_pressure * 1.5  # bar
            min_operating_pressure = operating_pressure * 0.8  # bar
            
            # Efficiency parameters
            electrical_efficiency = random.uniform(50, 60)  # %
            thermal_efficiency = random.uniform(25, 35)  # %
            fuel_utilization = random.uniform(75, 85)  # %
            air_utilization = random.uniform(15, 25)  # %
            
            # Maintenance parameters
            inspection_interval_hours = random.uniform(2000, 4000)  # hours
            major_overhaul_interval_hours = random.uniform(20000, 40000)  # hours
            stack_replacement_interval_hours = random.uniform(40000, 80000)  # hours
            
            operational_data.append({
                'power_rating_kw': power,
                'operating_temperature_c': round(operating_temperature, 1),
                'operating_pressure_bar': round(operating_pressure, 2),
                'fuel_flow_rate_m3_h': round(fuel_flow_rate, 2),
                'air_flow_rate_m3_h': round(air_flow_rate, 2),
                'steam_carbon_ratio': round(steam_carbon_ratio, 2),
                'temperature_control_accuracy_c': round(temperature_control_accuracy, 1),
                'pressure_control_accuracy_bar': round(pressure_control_accuracy, 2),
                'flow_control_accuracy_percent': round(flow_control_accuracy, 1),
                'max_operating_temperature_c': round(max_operating_temperature, 1),
                'min_operating_temperature_c': round(min_operating_temperature, 1),
                'max_operating_pressure_bar': round(max_operating_pressure, 2),
                'min_operating_pressure_bar': round(min_operating_pressure, 2),
                'electrical_efficiency_percent': round(electrical_efficiency, 1),
                'thermal_efficiency_percent': round(thermal_efficiency, 1),
                'fuel_utilization_percent': round(fuel_utilization, 1),
                'air_utilization_percent': round(air_utilization, 1),
                'inspection_interval_hours': round(inspection_interval_hours, 0),
                'major_overhaul_interval_hours': round(major_overhaul_interval_hours, 0),
                'stack_replacement_interval_hours': round(stack_replacement_interval_hours, 0),
                'startup_time_minutes': round(random.uniform(30, 120), 1),
                'shutdown_time_minutes': round(random.uniform(15, 60), 1),
                'load_following_capability_percent_min': round(random.uniform(2, 8), 1)
            })
        
        return pd.DataFrame(operational_data)
    
    def generate_control_systems_data(self):
        """Generate control systems and automation specifications"""
        print("Generating control systems data...")
        
        control_data = []
        system_types = ['Micro-CHP', 'Small Commercial', 'Industrial', 'Utility Scale']
        
        for system_type in system_types:
            # Control system complexity
            if system_type == 'Micro-CHP':
                control_points = random.randint(50, 100)
                automation_level = random.uniform(60, 80)
                remote_monitoring = random.choice([True, False])
            elif system_type == 'Small Commercial':
                control_points = random.randint(100, 200)
                automation_level = random.uniform(70, 85)
                remote_monitoring = True
            elif system_type == 'Industrial':
                control_points = random.randint(200, 500)
                automation_level = random.uniform(80, 95)
                remote_monitoring = True
            else:  # Utility Scale
                control_points = random.randint(500, 1000)
                automation_level = random.uniform(90, 98)
                remote_monitoring = True
            
            # Control system components
            plc_units = max(1, control_points // 100)
            hmi_stations = max(1, control_points // 200)
            scada_systems = 1 if control_points > 100 else 0
            
            # Communication protocols
            protocols = ['Modbus TCP/IP', 'OPC UA', 'Ethernet/IP']
            if system_type in ['Industrial', 'Utility Scale']:
                protocols.extend(['Profibus', 'Foundation Fieldbus'])
            
            # Safety systems
            safety_integrity_level = random.choice(['SIL 2', 'SIL 3'])
            emergency_shutdown_systems = random.randint(1, 3)
            fire_detection_systems = random.randint(1, 2)
            
            # Data logging and analytics
            data_logging_frequency = random.choice(['1 second', '5 seconds', '10 seconds'])
            historical_data_retention_days = random.randint(365, 1095)  # 1-3 years
            predictive_maintenance = random.choice([True, False])
            
            control_data.append({
                'system_type': system_type,
                'control_points': control_points,
                'automation_level_percent': round(automation_level, 1),
                'remote_monitoring': remote_monitoring,
                'plc_units': plc_units,
                'hmi_stations': hmi_stations,
                'scada_systems': scada_systems,
                'communication_protocols': ', '.join(protocols),
                'safety_integrity_level': safety_integrity_level,
                'emergency_shutdown_systems': emergency_shutdown_systems,
                'fire_detection_systems': fire_detection_systems,
                'data_logging_frequency': data_logging_frequency,
                'historical_data_retention_days': historical_data_retention_days,
                'predictive_maintenance': predictive_maintenance,
                'cybersecurity_level': random.choice(['Basic', 'Enhanced', 'Advanced']),
                'redundancy_level': random.choice(['None', 'Partial', 'Full']),
                'control_system_cost_usd': round(control_points * random.uniform(50, 150), 0)
            })
        
        return pd.DataFrame(control_data)
    
    def generate_maintenance_schedules(self):
        """Generate detailed maintenance schedules and procedures"""
        print("Generating maintenance schedules...")
        
        maintenance_data = []
        maintenance_tasks = [
            'Daily Visual Inspection',
            'Weekly Performance Check',
            'Monthly System Calibration',
            'Quarterly Filter Replacement',
            'Semi-Annual Stack Inspection',
            'Annual Major Overhaul',
            'Biennial Stack Replacement',
            'Emergency Repairs'
        ]
        
        for task in maintenance_tasks:
            # Task frequency and duration
            if 'Daily' in task:
                frequency_hours = 24
                duration_hours = random.uniform(0.5, 2)
                skill_level = 'Basic'
            elif 'Weekly' in task:
                frequency_hours = 168
                duration_hours = random.uniform(2, 4)
                skill_level = 'Intermediate'
            elif 'Monthly' in task:
                frequency_hours = 720
                duration_hours = random.uniform(4, 8)
                skill_level = 'Advanced'
            elif 'Quarterly' in task:
                frequency_hours = 2160
                duration_hours = random.uniform(8, 16)
                skill_level = 'Advanced'
            elif 'Semi-Annual' in task:
                frequency_hours = 4320
                duration_hours = random.uniform(16, 32)
                skill_level = 'Expert'
            elif 'Annual' in task:
                frequency_hours = 8760
                duration_hours = random.uniform(32, 80)
                skill_level = 'Expert'
            elif 'Biennial' in task:
                frequency_hours = 17520
                duration_hours = random.uniform(80, 160)
                skill_level = 'Expert'
            else:  # Emergency
                frequency_hours = 0  # As needed
                duration_hours = random.uniform(4, 24)
                skill_level = 'Expert'
            
            # Required tools and equipment
            if 'Inspection' in task:
                tools = 'Multimeter, Thermometer, Pressure Gauge, Visual Inspection Kit'
            elif 'Calibration' in task:
                tools = 'Calibration Equipment, Multimeter, Oscilloscope'
            elif 'Filter' in task:
                tools = 'Filter Replacement Kit, Basic Hand Tools'
            elif 'Stack' in task:
                tools = 'Specialized Stack Tools, Lifting Equipment, Testing Equipment'
            elif 'Overhaul' in task:
                tools = 'Complete Tool Set, Lifting Equipment, Testing Equipment, Replacement Parts'
            else:  # Emergency
                tools = 'Emergency Repair Kit, Basic Tools, Replacement Parts'
            
            # Required personnel
            if skill_level == 'Basic':
                personnel = '1 Technician'
            elif skill_level == 'Intermediate':
                personnel = '1-2 Technicians'
            elif skill_level == 'Advanced':
                personnel = '2-3 Technicians + 1 Engineer'
            else:  # Expert
                personnel = '3-5 Technicians + 2 Engineers + Specialist'
            
            # Cost estimates (USD)
            if 'Daily' in task:
                cost = random.uniform(50, 150)
            elif 'Weekly' in task:
                cost = random.uniform(200, 500)
            elif 'Monthly' in task:
                cost = random.uniform(500, 1500)
            elif 'Quarterly' in task:
                cost = random.uniform(1000, 3000)
            elif 'Semi-Annual' in task:
                cost = random.uniform(5000, 15000)
            elif 'Annual' in task:
                cost = random.uniform(20000, 50000)
            elif 'Biennial' in task:
                cost = random.uniform(100000, 300000)
            else:  # Emergency
                cost = random.uniform(1000, 10000)
            
            maintenance_data.append({
                'maintenance_task': task,
                'frequency_hours': round(frequency_hours, 0),
                'duration_hours': round(duration_hours, 1),
                'skill_level_required': skill_level,
                'required_tools': tools,
                'required_personnel': personnel,
                'estimated_cost_usd': round(cost, 0),
                'estimated_cost_naira': round(cost * 1500, 0),
                'criticality_level': random.choice(['Low', 'Medium', 'High', 'Critical']),
                'can_be_delayed': 'No' if 'Emergency' in task else random.choice(['Yes', 'No']),
                'requires_shutdown': 'No' if 'Visual' in task else 'Yes',
                'spare_parts_required': 'No' if 'Inspection' in task else 'Yes'
            })
        
        return pd.DataFrame(maintenance_data)
    
    def generate_safety_specifications(self):
        """Generate safety specifications and risk assessment data"""
        print("Generating safety specifications...")
        
        safety_data = []
        hazard_types = [
            'High Temperature',
            'High Pressure',
            'Flammable Gas',
            'Electrical Shock',
            'Toxic Gas Release',
            'Fire/Explosion',
            'Mechanical Injury',
            'Noise Exposure'
        ]
        
        for hazard in hazard_types:
            # Risk assessment
            if hazard in ['High Temperature', 'High Pressure']:
                probability = random.uniform(0.1, 0.3)
                severity = random.uniform(0.7, 0.9)
            elif hazard in ['Flammable Gas', 'Fire/Explosion']:
                probability = random.uniform(0.05, 0.2)
                severity = random.uniform(0.8, 1.0)
            elif hazard == 'Electrical Shock':
                probability = random.uniform(0.1, 0.4)
                severity = random.uniform(0.6, 0.8)
            elif hazard == 'Toxic Gas Release':
                probability = random.uniform(0.02, 0.1)
                severity = random.uniform(0.9, 1.0)
            else:  # Mechanical, Noise
                probability = random.uniform(0.2, 0.5)
                severity = random.uniform(0.3, 0.6)
            
            risk_level = probability * severity
            
            # Safety measures
            if risk_level > 0.5:
                safety_level = 'High'
                measures = 'Multiple layers of protection, Emergency shutdown, Continuous monitoring'
            elif risk_level > 0.2:
                safety_level = 'Medium'
                measures = 'Standard safety systems, Regular inspections, Training required'
            else:
                safety_level = 'Low'
                measures = 'Basic safety measures, Standard procedures'
            
            # Safety equipment
            if hazard == 'High Temperature':
                equipment = 'Thermal insulation, Temperature sensors, Cooling systems'
            elif hazard == 'High Pressure':
                equipment = 'Pressure relief valves, Pressure sensors, Pressure vessels'
            elif hazard in ['Flammable Gas', 'Fire/Explosion']:
                equipment = 'Gas detectors, Fire suppression systems, Explosion-proof equipment'
            elif hazard == 'Electrical Shock':
                equipment = 'Ground fault protection, Insulation, Electrical safety equipment'
            elif hazard == 'Toxic Gas Release':
                equipment = 'Gas detection systems, Ventilation, Personal protective equipment'
            else:
                equipment = 'Standard safety equipment, Personal protective equipment'
            
            safety_data.append({
                'hazard_type': hazard,
                'probability': round(probability, 3),
                'severity': round(severity, 3),
                'risk_level': round(risk_level, 3),
                'safety_level': safety_level,
                'safety_measures': measures,
                'safety_equipment': equipment,
                'mitigation_effectiveness': round(random.uniform(0.7, 0.95), 2),
                'monitoring_required': random.choice(['Continuous', 'Periodic', 'On-demand']),
                'training_required': random.choice(['Basic', 'Advanced', 'Specialized']),
                'regulatory_compliance': random.choice(['OSHA', 'IEC', 'NFPA', 'Local'])
            })
        
        return pd.DataFrame(safety_data)
    
    def generate_all_datasets(self):
        """Generate all detailed technical datasets"""
        print("Starting detailed technical dataset generation...")
        
        # Generate all datasets
        self.datasets['detailed_performance_curves'] = self.generate_detailed_performance_curves()
        self.datasets['material_specifications'] = self.generate_material_specifications()
        self.datasets['operational_parameters'] = self.generate_operational_parameters()
        self.datasets['control_systems'] = self.generate_control_systems_data()
        self.datasets['maintenance_schedules'] = self.generate_maintenance_schedules()
        self.datasets['safety_specifications'] = self.generate_safety_specifications()
        
        print("All detailed technical datasets generated successfully!")
        return self.datasets
    
    def save_datasets(self, output_dir='/workspace/sofc_datasets'):
        """Save all datasets to CSV and JSON formats"""
        print(f"Saving detailed technical datasets to {output_dir}...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Save each dataset
        for name, df in self.datasets.items():
            # CSV format
            csv_path = os.path.join(output_dir, f"{name}.csv")
            df.to_csv(csv_path, index=False)
            
            # JSON format
            json_path = os.path.join(output_dir, f"{name}.json")
            df.to_json(json_path, orient='records', indent=2)
            
            print(f"Saved {name}: {len(df)} records")
        
        print(f"All detailed technical datasets saved to {output_dir}")

if __name__ == "__main__":
    # Initialize generator
    generator = SOFCDetailedTechnicalGenerator()
    
    # Generate all datasets
    datasets = generator.generate_all_datasets()
    
    # Save datasets
    generator.save_datasets()
    
    print("\n" + "="*70)
    print("DETAILED SOFC TECHNICAL DATASET GENERATION COMPLETE")
    print("="*70)
    print("Generated datasets:")
    for name, df in datasets.items():
        print(f"  - {name}: {len(df)} records")
    print(f"\nAll files saved to: /workspace/sofc_datasets/")
    print("="*70)