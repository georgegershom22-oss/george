#!/usr/bin/env python3
"""
Techno-Economic Analysis (TEA) for SOFC Systems in Nigeria
This script performs comprehensive economic analysis comparing SOFC, Diesel, and Solar+Battery systems

Author: Economic Analysis Tool
Date: 2024-10-21
Purpose: Support TEA for "Harnessing Domestic Gas for Power: A Techno-Economic and 
         Socio-Political Analysis of SOFCs in Mitigating Nigeria's Electricity Crisis"
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class SOFCEconomicAnalysis:
    """Comprehensive TEA for SOFC vs Incumbent Technologies"""
    
    def __init__(self, data_path='economic_data'):
        """Initialize with path to economic data folder"""
        self.data_path = Path(data_path)
        self.load_all_data()
        
    def load_all_data(self):
        """Load all CSV datasets"""
        print("Loading economic datasets...")
        
        # Load main datasets
        self.sofc_costs = pd.read_csv(self.data_path / 'sofc_system_costs.csv')
        self.diesel_costs = pd.read_csv(self.data_path / 'diesel_generator_costs.csv')
        self.solar_costs = pd.read_csv(self.data_path / 'solar_battery_costs.csv')
        self.financial_params = pd.read_csv(self.data_path / 'financial_parameters.csv')
        self.fuel_costs = pd.read_csv(self.data_path / 'fuel_costs_comparison.csv')
        self.scenarios = pd.read_csv(self.data_path / 'operational_scenarios.csv')
        self.policies = pd.read_csv(self.data_path / 'incentives_and_policies.csv')
        
        print(f"✓ Loaded {len(self.sofc_costs)} SOFC cost entries")
        print(f"✓ Loaded {len(self.diesel_costs)} Diesel generator entries")
        print(f"✓ Loaded {len(self.solar_costs)} Solar+Battery entries")
        print(f"✓ Loaded {len(self.financial_params)} Financial parameters")
        print(f"✓ Loaded {len(self.fuel_costs)} Fuel types")
        print(f"✓ Loaded {len(self.scenarios)} Operating scenarios")
        print(f"✓ Loaded {len(self.policies)} Policy instruments")
        
    def get_param(self, param_name, default=None):
        """Get financial parameter value by name"""
        param_row = self.financial_params[
            self.financial_params['Parameter'] == param_name
        ]
        if len(param_row) > 0:
            value = param_row.iloc[0]['Value']
            # Handle string values like "60_40"
            if isinstance(value, str) and '_' in value:
                return value
            # Convert to float for numeric values
            try:
                return float(value)
            except (ValueError, TypeError):
                return value
        return default
    
    def calculate_npv(self, capex, annual_cash_flows, discount_rate, years):
        """Calculate Net Present Value"""
        npv = -capex
        for year in range(1, years + 1):
            if isinstance(annual_cash_flows, (list, np.ndarray)):
                cash_flow = annual_cash_flows[year-1]
            else:
                cash_flow = annual_cash_flows
            npv += cash_flow / ((1 + discount_rate) ** year)
        return npv
    
    def calculate_irr(self, capex, annual_cash_flows, years, max_iter=1000):
        """Calculate Internal Rate of Return using Newton-Raphson method"""
        # Initial guess
        irr = 0.1
        
        for _ in range(max_iter):
            npv = -capex
            npv_derivative = 0
            
            for year in range(1, years + 1):
                if isinstance(annual_cash_flows, (list, np.ndarray)):
                    cash_flow = annual_cash_flows[year-1]
                else:
                    cash_flow = annual_cash_flows
                    
                npv += cash_flow / ((1 + irr) ** year)
                npv_derivative -= year * cash_flow / ((1 + irr) ** (year + 1))
            
            if abs(npv) < 1e-6:
                return irr
            
            if abs(npv_derivative) < 1e-10:
                return None
                
            irr = irr - npv / npv_derivative
            
            if irr < -0.99 or irr > 10:  # Bounds check
                return None
        
        return irr
    
    def calculate_lcoe(self, capex, opex_annual, fuel_cost_annual, 
                      energy_output_annual, discount_rate, years,
                      replacement_costs=None):
        """
        Calculate Levelized Cost of Energy (LCOE)
        
        LCOE = Sum of discounted costs / Sum of discounted energy output
        """
        total_discounted_costs = capex
        total_discounted_energy = 0
        
        for year in range(1, years + 1):
            discount_factor = 1 / ((1 + discount_rate) ** year)
            
            # Annual costs
            annual_cost = opex_annual + fuel_cost_annual
            
            # Add replacement costs if applicable
            if replacement_costs and year in replacement_costs:
                annual_cost += replacement_costs[year]
            
            total_discounted_costs += annual_cost * discount_factor
            total_discounted_energy += energy_output_annual * discount_factor
        
        lcoe = total_discounted_costs / total_discounted_energy
        return lcoe
    
    def calculate_payback_period(self, capex, annual_savings):
        """Calculate simple payback period"""
        if annual_savings <= 0:
            return float('inf')
        return capex / annual_savings
    
    def calculate_discounted_payback(self, capex, annual_savings, discount_rate, max_years=30):
        """Calculate discounted payback period"""
        cumulative_pv = -capex
        
        for year in range(1, max_years + 1):
            pv_savings = annual_savings / ((1 + discount_rate) ** year)
            cumulative_pv += pv_savings
            
            if cumulative_pv >= 0:
                return year
        
        return float('inf')
    
    def sofc_analysis(self, system_size_kw=500, scenario='Base_Case_SOFC'):
        """Comprehensive SOFC system analysis"""
        print(f"\n{'='*80}")
        print(f"SOFC SYSTEM ANALYSIS - {system_size_kw} kW - {scenario}")
        print(f"{'='*80}\n")
        
        # Get SOFC costs (use base/average values)
        matching_sofc = self.sofc_costs[
            self.sofc_costs['System_Size_kW'] == system_size_kw
        ]
        if len(matching_sofc) == 0:
            raise ValueError(f"No SOFC data found for {system_size_kw} kW")
        
        # Prefer DOE/FuelCell/Average sources, but use first available if none found
        preferred = matching_sofc[
            matching_sofc['Source'].str.contains('DOE|FuelCell|Average', na=False)
        ]
        sofc_data = preferred.iloc[0] if len(preferred) > 0 else matching_sofc.iloc[0]
        
        # Get scenario parameters
        scenario_data = self.scenarios[
            (self.scenarios['Scenario'] == scenario) &
            (self.scenarios['Technology'] == 'SOFC')
        ].iloc[0]
        
        # Get fuel costs (natural gas)
        gas_fuel = self.fuel_costs[
            self.fuel_costs['Fuel_Type'] == 'Natural_Gas_Industrial'
        ].iloc[0]
        
        # Financial parameters
        discount_rate = self.get_param('Discount_Rate_Real') / 100
        project_lifetime = int(self.get_param('Project_Lifetime_SOFC'))
        capacity_factor = scenario_data['Capacity_Factor']
        
        # CAPEX calculation
        capex = sofc_data['CAPEX_Total_USD']
        
        # Annual energy output
        annual_hours = 8760 * capacity_factor
        annual_energy_kwh = system_size_kw * annual_hours
        
        # Fuel consumption (assuming 50% electrical efficiency for SOFC)
        electrical_efficiency = 0.55  # SOFC electrical efficiency
        fuel_input_kwh_thermal = annual_energy_kwh / electrical_efficiency
        
        # Convert to MSCF (1 MSCF = 1.026 MMBtu = 300.6 kWh)
        mscf_per_kwh_thermal = 1 / 300.6
        annual_fuel_mscf = fuel_input_kwh_thermal * mscf_per_kwh_thermal
        annual_fuel_cost = annual_fuel_mscf * gas_fuel['Price_USD']
        
        # OPEX calculation
        annual_opex = sofc_data['Annual_OPEX_USD_per_kW'] * system_size_kw
        annual_labor = sofc_data['Labor_Cost_USD_per_yr']
        
        # Stack replacement
        stack_replacement_year = int(sofc_data['Stack_Lifetime_Years'])
        stack_replacement_cost = sofc_data['Stack_Replacement_Cost_USD_per_kW'] * system_size_kw
        
        # Total annual costs
        total_annual_cost = annual_fuel_cost + annual_opex + annual_labor
        
        # LCOE calculation with stack replacement
        replacement_costs = {}
        for year in range(stack_replacement_year, project_lifetime, stack_replacement_year):
            replacement_costs[year] = stack_replacement_cost
        
        lcoe = self.calculate_lcoe(
            capex, annual_opex + annual_labor, annual_fuel_cost,
            annual_energy_kwh, discount_rate, project_lifetime,
            replacement_costs
        )
        
        # NPV calculation (assuming electricity sales)
        electricity_price = self.get_param('Electricity_Tariff_Industrial')
        annual_revenue = annual_energy_kwh * electricity_price
        annual_profit = annual_revenue - total_annual_cost
        
        npv = self.calculate_npv(capex, annual_profit, discount_rate, project_lifetime)
        irr = self.calculate_irr(capex, annual_profit, project_lifetime)
        
        # Output results
        results = {
            'Technology': 'SOFC',
            'System_Size_kW': system_size_kw,
            'CAPEX_USD': capex,
            'CAPEX_USD_per_kW': capex / system_size_kw,
            'Annual_Energy_MWh': annual_energy_kwh / 1000,
            'Capacity_Factor': capacity_factor,
            'Annual_Fuel_Cost_USD': annual_fuel_cost,
            'Annual_OPEX_USD': annual_opex,
            'Annual_Labor_USD': annual_labor,
            'Total_Annual_Cost_USD': total_annual_cost,
            'LCOE_USD_per_kWh': lcoe,
            'NPV_USD': npv,
            'IRR_Percent': irr * 100 if irr else None,
            'Payback_Years': self.calculate_payback_period(capex, annual_profit),
            'Project_Lifetime_Years': project_lifetime
        }
        
        self.print_results(results)
        return results
    
    def diesel_analysis(self, system_size_kw=500, scenario='Base_Case_Diesel'):
        """Comprehensive Diesel Generator analysis"""
        print(f"\n{'='*80}")
        print(f"DIESEL GENERATOR ANALYSIS - {system_size_kw} kW - {scenario}")
        print(f"{'='*80}\n")
        
        # Get diesel costs
        matching_diesel = self.diesel_costs[
            self.diesel_costs['System_Size_kW'] == system_size_kw
        ]
        if len(matching_diesel) == 0:
            raise ValueError(f"No diesel data found for {system_size_kw} kW")
        
        # Prefer Nigeria/Average sources
        preferred = matching_diesel[
            matching_diesel['Source'].str.contains('Nigeria|Average', na=False)
        ]
        diesel_data = preferred.iloc[0] if len(preferred) > 0 else matching_diesel.iloc[0]
        
        # Get scenario parameters
        scenario_data = self.scenarios[
            (self.scenarios['Scenario'] == scenario) &
            (self.scenarios['Technology'] == 'Diesel')
        ].iloc[0]
        
        # Financial parameters
        discount_rate = self.get_param('Discount_Rate_Real') / 100
        project_lifetime = int(self.get_param('Project_Lifetime_Diesel'))
        capacity_factor = scenario_data['Capacity_Factor']
        
        # CAPEX calculation
        capex = diesel_data['CAPEX_Total_USD']
        
        # Annual energy output
        annual_hours = 8760 * capacity_factor
        annual_energy_kwh = system_size_kw * annual_hours
        
        # Fuel consumption
        fuel_consumption_l_per_kwh = diesel_data['Fuel_Consumption_L_per_kWh']
        annual_fuel_liters = annual_energy_kwh * fuel_consumption_l_per_kwh
        diesel_price = diesel_data['Diesel_Price_USD_per_L']
        annual_fuel_cost = annual_fuel_liters * diesel_price
        
        # OPEX calculation
        annual_opex = diesel_data['Annual_Maintenance_USD_per_kW'] * system_size_kw
        
        # Major overhaul
        overhaul_interval = int(diesel_data['Overhaul_Interval_Years'])
        overhaul_cost = diesel_data['Major_Overhaul_Cost_USD']
        
        # Total annual costs
        total_annual_cost = annual_fuel_cost + annual_opex
        
        # LCOE calculation with overhaul
        replacement_costs = {}
        for year in range(overhaul_interval, project_lifetime, overhaul_interval):
            replacement_costs[year] = overhaul_cost
        
        lcoe = self.calculate_lcoe(
            capex, annual_opex, annual_fuel_cost,
            annual_energy_kwh, discount_rate, project_lifetime,
            replacement_costs
        )
        
        # NPV calculation
        electricity_price = self.get_param('Electricity_Tariff_Industrial')
        annual_revenue = annual_energy_kwh * electricity_price
        annual_profit = annual_revenue - total_annual_cost
        
        npv = self.calculate_npv(capex, annual_profit, discount_rate, project_lifetime)
        irr = self.calculate_irr(capex, annual_profit, project_lifetime)
        
        results = {
            'Technology': 'Diesel',
            'System_Size_kW': system_size_kw,
            'CAPEX_USD': capex,
            'CAPEX_USD_per_kW': capex / system_size_kw,
            'Annual_Energy_MWh': annual_energy_kwh / 1000,
            'Capacity_Factor': capacity_factor,
            'Annual_Fuel_Cost_USD': annual_fuel_cost,
            'Annual_Fuel_Liters': annual_fuel_liters,
            'Annual_OPEX_USD': annual_opex,
            'Total_Annual_Cost_USD': total_annual_cost,
            'LCOE_USD_per_kWh': lcoe,
            'NPV_USD': npv,
            'IRR_Percent': irr * 100 if irr else None,
            'Payback_Years': self.calculate_payback_period(capex, annual_profit),
            'Project_Lifetime_Years': project_lifetime
        }
        
        self.print_results(results)
        return results
    
    def solar_analysis(self, system_size_kw=500, scenario='Base_Case_Solar'):
        """Comprehensive Solar+Battery analysis"""
        print(f"\n{'='*80}")
        print(f"SOLAR + BATTERY ANALYSIS - {system_size_kw} kW - {scenario}")
        print(f"{'='*80}\n")
        
        # Get solar costs
        matching_solar = self.solar_costs[
            self.solar_costs['System_Size_kW'] == system_size_kw
        ]
        if len(matching_solar) == 0:
            raise ValueError(f"No solar data found for {system_size_kw} kW")
        
        # Prefer Nigeria/Average sources
        preferred = matching_solar[
            matching_solar['Source'].str.contains('Nigeria|Average', na=False)
        ]
        solar_data = preferred.iloc[0] if len(preferred) > 0 else matching_solar.iloc[0]
        
        # Get scenario parameters
        scenario_data = self.scenarios[
            (self.scenarios['Scenario'] == scenario) &
            (self.scenarios['Technology'] == 'Solar_Battery')
        ].iloc[0]
        
        # Financial parameters
        discount_rate = self.get_param('Discount_Rate_Real') / 100
        project_lifetime = int(self.get_param('Project_Lifetime_Solar'))
        capacity_factor = scenario_data['Capacity_Factor']
        
        # CAPEX calculation
        capex = solar_data['Total_CAPEX_USD']
        
        # Annual energy output
        annual_hours = 8760 * capacity_factor
        annual_energy_kwh = system_size_kw * annual_hours
        
        # OPEX calculation (no fuel costs for solar)
        annual_opex = solar_data['Annual_OPEX_USD_per_kW'] * system_size_kw
        annual_fuel_cost = 0  # Solar has no fuel cost
        
        # Battery replacement
        battery_replacement_years = int(solar_data['Battery_Replacement_Years'])
        battery_kwh = solar_data['Battery_Storage_kWh']
        battery_replacement_cost_per_kwh = solar_data['Battery_Replacement_Cost_USD_per_kWh']
        battery_replacement_cost = battery_kwh * battery_replacement_cost_per_kwh
        
        # Total annual costs
        total_annual_cost = annual_opex
        
        # LCOE calculation with battery replacement
        replacement_costs = {}
        for year in range(battery_replacement_years, project_lifetime, battery_replacement_years):
            replacement_costs[year] = battery_replacement_cost
        
        lcoe = self.calculate_lcoe(
            capex, annual_opex, 0,
            annual_energy_kwh, discount_rate, project_lifetime,
            replacement_costs
        )
        
        # NPV calculation
        electricity_price = self.get_param('Electricity_Tariff_Industrial')
        annual_revenue = annual_energy_kwh * electricity_price
        annual_profit = annual_revenue - total_annual_cost
        
        npv = self.calculate_npv(capex, annual_profit, discount_rate, project_lifetime)
        irr = self.calculate_irr(capex, annual_profit, project_lifetime)
        
        results = {
            'Technology': 'Solar+Battery',
            'System_Size_kW': system_size_kw,
            'CAPEX_USD': capex,
            'CAPEX_USD_per_kW': capex / system_size_kw,
            'Battery_Storage_kWh': battery_kwh,
            'Annual_Energy_MWh': annual_energy_kwh / 1000,
            'Capacity_Factor': capacity_factor,
            'Annual_Fuel_Cost_USD': 0,
            'Annual_OPEX_USD': annual_opex,
            'Total_Annual_Cost_USD': total_annual_cost,
            'LCOE_USD_per_kWh': lcoe,
            'NPV_USD': npv,
            'IRR_Percent': irr * 100 if irr else None,
            'Payback_Years': self.calculate_payback_period(capex, annual_profit),
            'Project_Lifetime_Years': project_lifetime
        }
        
        self.print_results(results)
        return results
    
    def print_results(self, results):
        """Print formatted analysis results"""
        print(f"Technology: {results['Technology']}")
        print(f"System Size: {results['System_Size_kW']:.0f} kW")
        print(f"\nCAPEX:")
        print(f"  Total: ${results['CAPEX_USD']:,.0f}")
        print(f"  Per kW: ${results['CAPEX_USD_per_kW']:,.0f}/kW")
        print(f"\nAnnual Operations:")
        print(f"  Energy Output: {results['Annual_Energy_MWh']:,.0f} MWh")
        print(f"  Capacity Factor: {results['Capacity_Factor']:.1%}")
        print(f"  Fuel Cost: ${results['Annual_Fuel_Cost_USD']:,.0f}")
        if 'Annual_OPEX_USD' in results:
            print(f"  O&M Cost: ${results['Annual_OPEX_USD']:,.0f}")
        print(f"  Total Annual Cost: ${results['Total_Annual_Cost_USD']:,.0f}")
        print(f"\nEconomic Metrics:")
        print(f"  LCOE: ${results['LCOE_USD_per_kWh']:.4f}/kWh")
        print(f"  NPV: ${results['NPV_USD']:,.0f}")
        if results['IRR_Percent']:
            print(f"  IRR: {results['IRR_Percent']:.2f}%")
        else:
            print(f"  IRR: Not calculable (negative cash flows)")
        
        if results['Payback_Years'] != float('inf'):
            print(f"  Payback Period: {results['Payback_Years']:.1f} years")
        else:
            print(f"  Payback Period: > {results['Project_Lifetime_Years']} years")
        print(f"  Project Lifetime: {results['Project_Lifetime_Years']} years")
    
    def comparative_analysis(self, system_sizes=[100, 250, 500, 750, 1000]):
        """Compare all three technologies across different system sizes"""
        print(f"\n{'='*80}")
        print(f"COMPARATIVE ANALYSIS ACROSS SYSTEM SIZES")
        print(f"{'='*80}\n")
        
        comparison_results = []
        
        for size in system_sizes:
            print(f"\n--- Analyzing {size} kW systems ---")
            
            # Analyze each technology
            sofc_result = self.sofc_analysis(size, 'Base_Case_SOFC')
            diesel_result = self.diesel_analysis(size, 'Base_Case_Diesel')
            solar_result = self.solar_analysis(size, 'Base_Case_Solar')
            
            comparison_results.append({
                'Size_kW': size,
                'SOFC_LCOE': sofc_result['LCOE_USD_per_kWh'],
                'Diesel_LCOE': diesel_result['LCOE_USD_per_kWh'],
                'Solar_LCOE': solar_result['LCOE_USD_per_kWh'],
                'SOFC_NPV': sofc_result['NPV_USD'],
                'Diesel_NPV': diesel_result['NPV_USD'],
                'Solar_NPV': solar_result['NPV_USD'],
                'SOFC_CAPEX': sofc_result['CAPEX_USD'],
                'Diesel_CAPEX': diesel_result['CAPEX_USD'],
                'Solar_CAPEX': solar_result['CAPEX_USD']
            })
        
        # Create comparison DataFrame
        comparison_df = pd.DataFrame(comparison_results)
        
        print(f"\n{'='*80}")
        print("LCOE COMPARISON (USD/kWh)")
        print(f"{'='*80}")
        print(comparison_df[['Size_kW', 'SOFC_LCOE', 'Diesel_LCOE', 'Solar_LCOE']].to_string(index=False))
        
        print(f"\n{'='*80}")
        print("NPV COMPARISON (USD)")
        print(f"{'='*80}")
        print(comparison_df[['Size_kW', 'SOFC_NPV', 'Diesel_NPV', 'Solar_NPV']].to_string(index=False))
        
        return comparison_df
    
    def sensitivity_analysis(self, system_size_kw=500, parameter='discount_rate', 
                           variation_range=(-30, 30, 10)):
        """
        Perform sensitivity analysis on key parameters
        
        Parameters:
        - parameter: 'discount_rate', 'fuel_price', 'capex', 'capacity_factor'
        - variation_range: (min_%, max_%, step_%)
        """
        print(f"\n{'='*80}")
        print(f"SENSITIVITY ANALYSIS - {parameter.upper()}")
        print(f"{'='*80}\n")
        
        base_results = {
            'SOFC': self.sofc_analysis(system_size_kw, 'Base_Case_SOFC'),
            'Diesel': self.diesel_analysis(system_size_kw, 'Base_Case_Diesel'),
            'Solar': self.solar_analysis(system_size_kw, 'Base_Case_Solar')
        }
        
        # Create variation percentages
        variations = np.arange(variation_range[0], variation_range[1] + 1, variation_range[2])
        
        sensitivity_results = {
            'Variation_%': variations,
            'SOFC_LCOE': [],
            'Diesel_LCOE': [],
            'Solar_LCOE': []
        }
        
        # This is a simplified sensitivity analysis
        # In practice, you would modify the actual parameters and re-run
        for var in variations:
            factor = 1 + (var / 100)
            
            # Simplified approximation
            for tech in ['SOFC', 'Diesel', 'Solar']:
                base_lcoe = base_results[tech]['LCOE_USD_per_kWh']
                
                if parameter == 'discount_rate':
                    # LCOE increases with discount rate
                    new_lcoe = base_lcoe * (0.85 + 0.15 * factor)
                elif parameter == 'fuel_price':
                    # Fuel price affects diesel most, SOFC moderately, solar not at all
                    if tech == 'Diesel':
                        new_lcoe = base_lcoe * (0.3 + 0.7 * factor)
                    elif tech == 'SOFC':
                        new_lcoe = base_lcoe * (0.6 + 0.4 * factor)
                    else:  # Solar
                        new_lcoe = base_lcoe
                elif parameter == 'capex':
                    # CAPEX affects all proportionally
                    new_lcoe = base_lcoe * factor
                elif parameter == 'capacity_factor':
                    # Higher capacity factor reduces LCOE
                    new_lcoe = base_lcoe / factor
                else:
                    new_lcoe = base_lcoe
                
                sensitivity_results[f'{tech}_LCOE'].append(new_lcoe)
        
        sensitivity_df = pd.DataFrame(sensitivity_results)
        print(sensitivity_df.to_string(index=False))
        
        return sensitivity_df
    
    def generate_summary_report(self, output_file='economic_analysis_summary.txt'):
        """Generate comprehensive summary report"""
        print(f"\n{'='*80}")
        print(f"GENERATING COMPREHENSIVE SUMMARY REPORT")
        print(f"{'='*80}\n")
        
        with open(self.data_path.parent / output_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("TECHNO-ECONOMIC ANALYSIS SUMMARY REPORT\n")
            f.write("SOFC vs Incumbent Technologies for Nigeria Power Generation\n")
            f.write("="*80 + "\n\n")
            
            f.write("Project: Harnessing Domestic Gas for Power:\n")
            f.write("         A Techno-Economic and Socio-Political Analysis of\n")
            f.write("         Solid Oxide Fuel Cells (SOFCs) in Mitigating\n")
            f.write("         Nigeria's Electricity Crisis\n\n")
            
            f.write(f"Analysis Date: 2024-10-21\n")
            f.write(f"Data Sources: Multiple (see individual datasets)\n\n")
            
            f.write("="*80 + "\n")
            f.write("KEY FINDINGS\n")
            f.write("="*80 + "\n\n")
            
            # Run quick analyses
            sofc_500 = self.sofc_analysis(500, 'Base_Case_SOFC')
            diesel_500 = self.diesel_analysis(500, 'Base_Case_Diesel')
            solar_500 = self.solar_analysis(500, 'Base_Case_Solar')
            
            f.write(f"For 500 kW systems:\n\n")
            f.write(f"LCOE Comparison:\n")
            f.write(f"  SOFC:    ${sofc_500['LCOE_USD_per_kWh']:.4f}/kWh\n")
            f.write(f"  Diesel:  ${diesel_500['LCOE_USD_per_kWh']:.4f}/kWh\n")
            f.write(f"  Solar:   ${solar_500['LCOE_USD_per_kWh']:.4f}/kWh\n\n")
            
            f.write(f"CAPEX Comparison:\n")
            f.write(f"  SOFC:    ${sofc_500['CAPEX_USD']:,.0f}\n")
            f.write(f"  Diesel:  ${diesel_500['CAPEX_USD']:,.0f}\n")
            f.write(f"  Solar:   ${solar_500['CAPEX_USD']:,.0f}\n\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("DATASETS INCLUDED\n")
            f.write("="*80 + "\n\n")
            
            f.write("1. SOFC System Costs\n")
            f.write(f"   - {len(self.sofc_costs)} cost scenarios\n")
            f.write(f"   - System sizes: 100-1000 kW\n")
            f.write(f"   - CAPEX range: ${self.sofc_costs['CAPEX_USD_per_kW'].min():.0f} - ${self.sofc_costs['CAPEX_USD_per_kW'].max():.0f}/kW\n\n")
            
            f.write("2. Diesel Generator Costs\n")
            f.write(f"   - {len(self.diesel_costs)} cost scenarios\n")
            f.write(f"   - CAPEX range: ${self.diesel_costs['CAPEX_USD_per_kW'].min():.0f} - ${self.diesel_costs['CAPEX_USD_per_kW'].max():.0f}/kW\n")
            f.write(f"   - Fuel consumption: {self.diesel_costs['Fuel_Consumption_L_per_kWh'].min():.2f} - {self.diesel_costs['Fuel_Consumption_L_per_kWh'].max():.2f} L/kWh\n\n")
            
            f.write("3. Solar + Battery Costs\n")
            f.write(f"   - {len(self.solar_costs)} system configurations\n")
            f.write(f"   - CAPEX range: ${self.solar_costs['Total_CAPEX_USD_per_kW'].min():.0f} - ${self.solar_costs['Total_CAPEX_USD_per_kW'].max():.0f}/kW\n")
            f.write(f"   - Storage: 4-6 hours\n\n")
            
            f.write("4. Financial Parameters\n")
            f.write(f"   - {len(self.financial_params)} parameters\n")
            f.write(f"   - Nigeria inflation: {self.get_param('Nigeria_Inflation_Rate'):.1f}%\n")
            f.write(f"   - USD/NGN rate: {self.get_param('USD_NGN_Exchange_Rate'):.0f}\n")
            f.write(f"   - Discount rate: {self.get_param('Discount_Rate_Real'):.1f}%\n\n")
            
            f.write("5. Fuel Costs\n")
            f.write(f"   - {len(self.fuel_costs)} fuel types\n")
            f.write(f"   - Natural gas: ${self.fuel_costs[self.fuel_costs['Fuel_Type']=='Natural_Gas_Industrial']['Price_USD'].values[0]:.2f}/MSCF\n")
            f.write(f"   - Diesel: ${self.fuel_costs[self.fuel_costs['Fuel_Type']=='Diesel_Fuel']['Price_USD'].values[0]:.2f}/L\n\n")
            
            f.write("6. Operating Scenarios\n")
            f.write(f"   - {len(self.scenarios)} scenarios\n")
            f.write(f"   - Base case, optimistic, pessimistic\n")
            f.write(f"   - Various use cases (industrial, commercial, etc.)\n\n")
            
            f.write("7. Policy Instruments\n")
            f.write(f"   - {len(self.policies)} policy/incentive entries\n")
            f.write(f"   - Tax incentives, financing options, regulations\n\n")
            
            f.write("="*80 + "\n")
            f.write("RECOMMENDATIONS\n")
            f.write("="*80 + "\n\n")
            
            f.write("Based on the techno-economic analysis:\n\n")
            
            f.write("1. SOFC Technology shows promise for:\n")
            f.write("   - Baseload power applications (>80% capacity factor)\n")
            f.write("   - Areas with reliable natural gas supply\n")
            f.write("   - High efficiency requirements (combined heat & power)\n")
            f.write("   - Long-term cost stability (lower fuel price volatility)\n\n")
            
            f.write("2. Diesel Generators remain competitive for:\n")
            f.write("   - Backup/emergency power (<40% capacity factor)\n")
            f.write("   - Lower capital availability scenarios\n")
            f.write("   - Short-term/temporary installations\n")
            f.write("   - Remote areas without gas infrastructure\n\n")
            
            f.write("3. Solar + Battery systems are optimal for:\n")
            f.write("   - Daytime load profiles\n")
            f.write("   - Locations with high solar irradiance\n")
            f.write("   - Environmental compliance requirements\n")
            f.write("   - Decreasing costs trajectory\n\n")
            
            f.write("4. Policy Recommendations:\n")
            f.write("   - Implement gas supply guarantees for SOFC projects\n")
            f.write("   - Provide CAPEX subsidies or low-interest financing\n")
            f.write("   - Establish feed-in tariffs for clean generation\n")
            f.write("   - Streamline import duties on fuel cell equipment\n")
            f.write("   - Develop local content and manufacturing capacity\n\n")
            
            f.write("="*80 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*80 + "\n")
        
        print(f"✓ Summary report generated: {output_file}")


def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("SOFC TECHNO-ECONOMIC ANALYSIS TOOL")
    print("="*80 + "\n")
    
    # Initialize analysis
    analysis = SOFCEconomicAnalysis('economic_data')
    
    print("\nDatasets loaded successfully!")
    print("\nYou can now run various analyses:")
    print("  - analysis.sofc_analysis(500)")
    print("  - analysis.diesel_analysis(500)")
    print("  - analysis.solar_analysis(500)")
    print("  - analysis.comparative_analysis([100, 250, 500, 750, 1000])")
    print("  - analysis.sensitivity_analysis(500, 'fuel_price')")
    print("  - analysis.generate_summary_report()")
    
    # Generate summary report automatically
    analysis.generate_summary_report()
    
    # Run a quick comparative analysis
    print("\nRunning comparative analysis for standard system sizes...")
    comparison_df = analysis.comparative_analysis([250, 500, 1000])
    
    # Save comparison results
    comparison_df.to_csv('economic_data/comparison_results.csv', index=False)
    print("\n✓ Comparison results saved to: economic_data/comparison_results.csv")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80 + "\n")
    
    return analysis


if __name__ == "__main__":
    analysis = main()
