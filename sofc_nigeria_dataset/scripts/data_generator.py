"""
SOFC Technical Data Generator and Analysis Tools
Author: SOFC Research Team
Date: 2025-10-21
Description: Generate synthetic SOFC operational data and perform techno-economic analysis
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import random

class SOFCDataGenerator:
    """Generate synthetic SOFC operational data for Nigeria analysis"""
    
    def __init__(self, base_path="../data"):
        self.base_path = Path(base_path)
        self.simulated_path = self.base_path / "simulated"
        self.simulated_path.mkdir(exist_ok=True)
        
    def generate_operational_timeseries(self, duration_days=365, sampling_hours=1):
        """Generate time-series operational data for SOFC system"""
        print("Generating operational time-series data...")
        
        # Time array
        hours = duration_days * 24
        timestamps = pd.date_range(start='2024-01-01', periods=hours, freq='H')
        
        # Base parameters
        nominal_power = 250  # kW
        nominal_efficiency = 0.58
        
        # Generate realistic load profile
        load_profile = self._generate_load_profile(hours, nominal_power)
        
        # Calculate operational parameters
        data = {
            'timestamp': timestamps.tolist(),
            'load_kw': load_profile,
            'load_factor': (load_profile / nominal_power).tolist(),
            'electrical_efficiency': self._calculate_efficiency(load_profile, nominal_power, nominal_efficiency),
            'fuel_flow_nm3_h': self._calculate_fuel_flow(load_profile, nominal_efficiency),
            'stack_temperature_c': self._generate_temperature_profile(load_profile, nominal_power),
            'ambient_temperature_c': self._generate_ambient_temperature(hours),
            'cell_voltage_v': self._calculate_cell_voltage(load_profile, nominal_power),
            'degradation_factor': self._calculate_degradation(hours),
            'availability': self._generate_availability(hours),
            'grid_frequency_hz': self._generate_grid_frequency(hours),
            'emissions_co2_kg_h': self._calculate_emissions(load_profile, nominal_efficiency)
        }
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(data)
        
        # Calculate cumulative values
        df['cumulative_energy_mwh'] = (df['load_kw'] * 1 / 1000).cumsum()
        df['cumulative_fuel_nm3'] = df['fuel_flow_nm3_h'].cumsum()
        df['cumulative_co2_tonnes'] = (df['emissions_co2_kg_h'] / 1000).cumsum()
        
        # Save to file
        output_file = self.simulated_path / 'operational_timeseries.json'
        df.to_json(output_file, orient='records', date_format='iso')
        
        # Generate summary statistics
        summary = {
            'total_energy_generated_mwh': df['cumulative_energy_mwh'].iloc[-1],
            'average_load_factor': df['load_factor'].mean(),
            'average_efficiency': df['electrical_efficiency'].mean(),
            'total_fuel_consumption_nm3': df['cumulative_fuel_nm3'].iloc[-1],
            'total_co2_emissions_tonnes': df['cumulative_co2_tonnes'].iloc[-1],
            'availability_percent': (df['availability'].sum() / len(df)) * 100,
            'capacity_factor': df['load_factor'].mean(),
            'peak_load_kw': df['load_kw'].max(),
            'minimum_load_kw': df['load_kw'].min()
        }
        
        with open(self.simulated_path / 'operational_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Generated {hours} hours of operational data")
        return df
    
    def _generate_load_profile(self, hours, nominal_power):
        """Generate realistic load profile with daily and seasonal variations"""
        load = np.zeros(hours)
        
        for i in range(hours):
            hour_of_day = i % 24
            day_of_year = (i // 24) % 365
            
            # Daily pattern
            if 6 <= hour_of_day < 9:  # Morning ramp
                base_load = 0.5 + 0.1 * (hour_of_day - 6)
            elif 9 <= hour_of_day < 18:  # Day operation
                base_load = 0.8 + 0.1 * np.sin((hour_of_day - 9) * np.pi / 9)
            elif 18 <= hour_of_day < 22:  # Evening peak
                base_load = 0.9 - 0.05 * (hour_of_day - 18)
            else:  # Night
                base_load = 0.4
            
            # Seasonal variation
            seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * day_of_year / 365)
            
            # Random variation
            random_factor = 1 + np.random.normal(0, 0.05)
            
            # Grid events (occasional dips)
            if np.random.random() < 0.01:  # 1% chance of grid event
                random_factor *= 0.5
            
            load[i] = base_load * seasonal_factor * random_factor * nominal_power
            load[i] = np.clip(load[i], 0.2 * nominal_power, nominal_power)
        
        return load
    
    def _calculate_efficiency(self, load, nominal_power, nominal_efficiency):
        """Calculate efficiency based on load"""
        load_factor = load / nominal_power
        # Efficiency curve: decreases at low loads
        efficiency = nominal_efficiency * (0.85 + 0.15 * load_factor)
        return efficiency.tolist()
    
    def _calculate_fuel_flow(self, load, efficiency):
        """Calculate fuel flow based on load and efficiency"""
        # Assuming natural gas with LHV = 10 kWh/Nm³
        fuel_flow = load / (efficiency * 10)
        return fuel_flow.tolist()
    
    def _generate_temperature_profile(self, load, nominal_power):
        """Generate stack temperature based on load"""
        load_factor = load / nominal_power
        base_temp = 750  # °C
        temp = base_temp + 50 * (load_factor - 0.5) + np.random.normal(0, 2, len(load))
        return temp.tolist()
    
    def _generate_ambient_temperature(self, hours):
        """Generate ambient temperature for Nigeria"""
        temps = []
        for i in range(hours):
            hour_of_day = i % 24
            day_of_year = (i // 24) % 365
            
            # Daily variation
            daily_temp = 27 + 8 * np.sin((hour_of_day - 6) * np.pi / 12)
            
            # Seasonal variation (less pronounced in Nigeria)
            seasonal_temp = 3 * np.sin(2 * np.pi * day_of_year / 365)
            
            temp = daily_temp + seasonal_temp + np.random.normal(0, 1)
            temps.append(temp)
        
        return temps
    
    def _calculate_cell_voltage(self, load, nominal_power):
        """Calculate cell voltage based on load"""
        load_factor = load / nominal_power
        # Voltage decreases with increasing load
        voltage = 0.85 - 0.15 * load_factor + np.random.normal(0, 0.01, len(load))
        return voltage.tolist()
    
    def _calculate_degradation(self, hours):
        """Calculate degradation factor over time"""
        # 0.2% per 1000 hours
        degradation_rate = 0.002 / 1000
        degradation = 1 - (np.arange(hours) * degradation_rate)
        return degradation.tolist()
    
    def _generate_availability(self, hours):
        """Generate availability (1 = available, 0 = not available)"""
        availability = np.ones(hours)
        # Random maintenance events
        for i in range(0, hours, 2000):  # Maintenance every 2000 hours
            if i + 24 < hours:
                availability[i:i+24] = 0  # 24-hour maintenance
        
        # Random trips
        for _ in range(hours // 1000):  # Approximately one trip per 1000 hours
            start = np.random.randint(0, hours - 4)
            availability[start:start+4] = 0
        
        return availability.tolist()
    
    def _generate_grid_frequency(self, hours):
        """Generate grid frequency for Nigeria (nominal 50 Hz)"""
        frequency = 50 + np.random.normal(0, 0.5, hours)
        # Occasional grid events
        for _ in range(hours // 100):
            event_hour = np.random.randint(0, hours)
            frequency[event_hour] = 50 + np.random.uniform(-2, 2)
        
        return np.clip(frequency, 48, 52).tolist()
    
    def _calculate_emissions(self, load, efficiency):
        """Calculate CO2 emissions"""
        # Natural gas emission factor: 2.2 kg CO2/Nm³
        fuel_flow = load / (efficiency * 10)  # Nm³/h
        emissions = fuel_flow * 2.2  # kg CO2/h
        return emissions.tolist()
    
    def generate_economic_analysis(self):
        """Generate comprehensive economic analysis data"""
        print("Generating economic analysis data...")
        
        scenarios = []
        applications = [
            'industrial_backup', 'commercial_chp', 'telecom_tower',
            'agricultural_processing', 'residential_estate', 'data_center'
        ]
        
        for app in applications:
            for size in [100, 250, 500, 1000]:
                scenario = self._generate_economic_scenario(app, size)
                scenarios.append(scenario)
        
        # Save economic analysis
        output_file = self.simulated_path / 'economic_analysis.json'
        with open(output_file, 'w') as f:
            json.dump({'scenarios': scenarios}, f, indent=2)
        
        print(f"Generated {len(scenarios)} economic scenarios")
        return scenarios
    
    def _generate_economic_scenario(self, application, size_kw):
        """Generate economic scenario for specific application and size"""
        # Base assumptions
        capex_per_kw = 4500 - (size_kw / 1000) * 500  # Economy of scale
        electricity_price_ngn_kwh = 85
        gas_price_ngn_nm3 = 120
        
        # Application-specific adjustments
        capacity_factors = {
            'industrial_backup': 0.75,
            'commercial_chp': 0.70,
            'telecom_tower': 0.90,
            'agricultural_processing': 0.60,
            'residential_estate': 0.65,
            'data_center': 0.85
        }
        
        cf = capacity_factors.get(application, 0.70)
        
        # Calculate annual values
        annual_generation_mwh = size_kw * 8760 * cf / 1000
        annual_fuel_consumption_nm3 = annual_generation_mwh * 1000 / (0.55 * 10)  # 55% efficiency, 10 kWh/Nm³
        
        # Costs
        capex_total_million_ngn = size_kw * capex_per_kw / 1000 / 1000
        annual_fuel_cost_million_ngn = annual_fuel_consumption_nm3 * gas_price_ngn_nm3 / 1000000
        annual_om_cost_million_ngn = capex_total_million_ngn * 0.03  # 3% of capex
        
        # Revenues
        annual_electricity_revenue_million_ngn = annual_generation_mwh * electricity_price_ngn_kwh / 1000
        
        # CHP bonus for applicable scenarios
        chp_bonus = 0
        if 'chp' in application or 'commercial' in application:
            chp_bonus = annual_electricity_revenue_million_ngn * 0.3  # 30% additional value from heat
        
        # Financial metrics
        annual_net_revenue = annual_electricity_revenue_million_ngn + chp_bonus - annual_fuel_cost_million_ngn - annual_om_cost_million_ngn
        simple_payback_years = capex_total_million_ngn / annual_net_revenue if annual_net_revenue > 0 else 999
        
        # NPV calculation (10 years, 12% discount rate)
        discount_rate = 0.12
        project_life = 10
        npv = -capex_total_million_ngn
        for year in range(1, project_life + 1):
            npv += annual_net_revenue / ((1 + discount_rate) ** year)
        
        # IRR approximation
        irr = (annual_net_revenue / capex_total_million_ngn) * 100 if capex_total_million_ngn > 0 else 0
        
        return {
            'application': application,
            'size_kw': size_kw,
            'capacity_factor': cf,
            'capex_million_ngn': round(capex_total_million_ngn, 2),
            'annual_generation_mwh': round(annual_generation_mwh, 0),
            'annual_fuel_cost_million_ngn': round(annual_fuel_cost_million_ngn, 2),
            'annual_om_cost_million_ngn': round(annual_om_cost_million_ngn, 2),
            'annual_revenue_million_ngn': round(annual_electricity_revenue_million_ngn + chp_bonus, 2),
            'annual_net_revenue_million_ngn': round(annual_net_revenue, 2),
            'simple_payback_years': round(simple_payback_years, 1),
            'npv_million_ngn': round(npv, 2),
            'irr_percent': round(irr, 1),
            'lcoe_ngn_kwh': round((capex_total_million_ngn * 1000000 / (annual_generation_mwh * project_life * 1000) +
                                  (annual_fuel_cost_million_ngn + annual_om_cost_million_ngn) * 1000000 / (annual_generation_mwh * 1000)), 2)
        }
    
    def generate_reliability_data(self):
        """Generate reliability and maintenance data"""
        print("Generating reliability data...")
        
        components = [
            'stack', 'fuel_processor', 'power_electronics', 'control_system',
            'cooling_system', 'fuel_supply', 'electrical_connections'
        ]
        
        reliability_data = {}
        
        for component in components:
            # Generate failure data
            mtbf_hours = np.random.uniform(10000, 100000)
            mttr_hours = np.random.uniform(4, 48)
            availability = mtbf_hours / (mtbf_hours + mttr_hours)
            
            # Generate maintenance schedule
            preventive_interval_hours = np.random.uniform(2000, 8000)
            preventive_duration_hours = np.random.uniform(2, 12)
            
            reliability_data[component] = {
                'mtbf_hours': round(mtbf_hours, 0),
                'mttr_hours': round(mttr_hours, 1),
                'availability_percent': round(availability * 100, 2),
                'failure_rate_per_year': round(8760 / mtbf_hours, 4),
                'preventive_maintenance_interval_hours': round(preventive_interval_hours, 0),
                'preventive_maintenance_duration_hours': round(preventive_duration_hours, 1),
                'spare_parts_cost_ngn': round(np.random.uniform(50000, 500000), 0),
                'criticality': np.random.choice(['high', 'medium', 'low']),
                'redundancy': np.random.choice(['none', 'n+1', '2n'])
            }
        
        # System-level reliability
        system_availability = np.prod([d['availability_percent']/100 for d in reliability_data.values()])
        
        reliability_summary = {
            'components': reliability_data,
            'system_availability_percent': round(system_availability * 100, 2),
            'annual_downtime_hours': round((1 - system_availability) * 8760, 0),
            'reliability_target_percent': 97.0,
            'maintenance_strategy': 'predictive_with_preventive',
            'remote_monitoring': True,
            'spare_parts_inventory_value_million_ngn': round(sum([d['spare_parts_cost_ngn'] for d in reliability_data.values()]) / 1000000, 2)
        }
        
        # Save reliability data
        output_file = self.simulated_path / 'reliability_analysis.json'
        with open(output_file, 'w') as f:
            json.dump(reliability_summary, f, indent=2)
        
        print("Reliability data generated")
        return reliability_summary
    
    def generate_sensitivity_analysis(self):
        """Generate sensitivity analysis for key parameters"""
        print("Generating sensitivity analysis...")
        
        base_case = {
            'size_kw': 500,
            'efficiency': 0.58,
            'capex_usd_kw': 4500,
            'gas_price_ngn_nm3': 120,
            'electricity_price_ngn_kwh': 85,
            'capacity_factor': 0.75,
            'project_life_years': 15,
            'discount_rate': 0.12
        }
        
        sensitivity_params = {
            'gas_price': np.linspace(80, 160, 9),
            'electricity_price': np.linspace(60, 110, 9),
            'capex': np.linspace(3000, 6000, 9),
            'efficiency': np.linspace(0.50, 0.65, 9),
            'capacity_factor': np.linspace(0.60, 0.90, 9)
        }
        
        results = {}
        
        for param, values in sensitivity_params.items():
            param_results = []
            
            for value in values:
                # Copy base case and modify parameter
                case = base_case.copy()
                
                if param == 'gas_price':
                    case['gas_price_ngn_nm3'] = value
                elif param == 'electricity_price':
                    case['electricity_price_ngn_kwh'] = value
                elif param == 'capex':
                    case['capex_usd_kw'] = value
                elif param == 'efficiency':
                    case['efficiency'] = value
                elif param == 'capacity_factor':
                    case['capacity_factor'] = value
                
                # Calculate NPV
                npv = self._calculate_npv(case)
                lcoe = self._calculate_lcoe(case)
                
                param_results.append({
                    'value': round(value, 2),
                    'npv_million_ngn': round(npv, 2),
                    'lcoe_ngn_kwh': round(lcoe, 2)
                })
            
            results[param] = param_results
        
        # Save sensitivity analysis
        output_file = self.simulated_path / 'sensitivity_analysis.json'
        with open(output_file, 'w') as f:
            json.dump({
                'base_case': base_case,
                'sensitivity_results': results
            }, f, indent=2)
        
        print("Sensitivity analysis completed")
        return results
    
    def _calculate_npv(self, case):
        """Calculate NPV for a given case"""
        size_kw = case['size_kw']
        capex_total = size_kw * case['capex_usd_kw'] * 480 / 1000000  # Convert to million NGN
        
        annual_generation_mwh = size_kw * 8760 * case['capacity_factor'] / 1000
        annual_fuel_consumption_nm3 = annual_generation_mwh * 1000 / (case['efficiency'] * 10)
        
        annual_revenue = annual_generation_mwh * case['electricity_price_ngn_kwh'] / 1000
        annual_fuel_cost = annual_fuel_consumption_nm3 * case['gas_price_ngn_nm3'] / 1000000
        annual_om_cost = capex_total * 0.03
        
        annual_net_cash_flow = annual_revenue - annual_fuel_cost - annual_om_cost
        
        npv = -capex_total
        for year in range(1, case['project_life_years'] + 1):
            npv += annual_net_cash_flow / ((1 + case['discount_rate']) ** year)
        
        return npv
    
    def _calculate_lcoe(self, case):
        """Calculate LCOE for a given case"""
        size_kw = case['size_kw']
        capex_total = size_kw * case['capex_usd_kw'] * 480  # Convert to NGN
        
        annual_generation_kwh = size_kw * 8760 * case['capacity_factor']
        annual_fuel_consumption_nm3 = annual_generation_kwh / (case['efficiency'] * 10)
        
        annual_fuel_cost = annual_fuel_consumption_nm3 * case['gas_price_ngn_nm3']
        annual_om_cost = capex_total * 0.03
        
        # Calculate annualized capital cost
        crf = (case['discount_rate'] * (1 + case['discount_rate'])**case['project_life_years']) / \
              ((1 + case['discount_rate'])**case['project_life_years'] - 1)
        annual_capital_cost = capex_total * crf
        
        total_annual_cost = annual_capital_cost + annual_fuel_cost + annual_om_cost
        lcoe = total_annual_cost / annual_generation_kwh
        
        return lcoe

def main():
    """Main function to generate all synthetic data"""
    print("="*50)
    print("SOFC Technical Data Generation for Nigeria")
    print("="*50)
    
    generator = SOFCDataGenerator()
    
    # Generate operational time-series
    print("\n1. Generating operational time-series data...")
    operational_data = generator.generate_operational_timeseries(duration_days=365)
    print(f"   - Generated {len(operational_data)} hours of data")
    
    # Generate economic analysis
    print("\n2. Generating economic analysis...")
    economic_scenarios = generator.generate_economic_analysis()
    print(f"   - Generated {len(economic_scenarios)} economic scenarios")
    
    # Generate reliability data
    print("\n3. Generating reliability analysis...")
    reliability_data = generator.generate_reliability_data()
    print(f"   - System availability: {reliability_data['system_availability_percent']}%")
    
    # Generate sensitivity analysis
    print("\n4. Generating sensitivity analysis...")
    sensitivity_results = generator.generate_sensitivity_analysis()
    print(f"   - Analyzed {len(sensitivity_results)} parameters")
    
    print("\n" + "="*50)
    print("Data generation complete!")
    print(f"All data saved to: {generator.simulated_path.absolute()}")
    print("="*50)

if __name__ == "__main__":
    main()