#!/usr/bin/env python3
"""
Techno-Economic Analysis (TEA) Calculator for SOFC Systems in Nigeria
Comprehensive financial modeling and sensitivity analysis

This module performs detailed TEA calculations including:
- Net Present Value (NPV)
- Internal Rate of Return (IRR)
- Levelized Cost of Electricity (LCOE)
- Payback Period
- Sensitivity Analysis
- Monte Carlo Simulation
"""

import numpy as np
import pandas as pd
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class SOFCTEACalculator:
    """
    Comprehensive TEA calculator for SOFC systems
    """
    
    def __init__(self, system_size_kw=500, analysis_period=20):
        self.system_size_kw = system_size_kw
        self.analysis_period = analysis_period
        self.base_year = 2024
        
        # Load economic parameters
        self.load_base_parameters()
        
    def load_base_parameters(self):
        """
        Load base economic and technical parameters
        """
        # SOFC Technical Parameters
        self.sofc_params = {
            'electrical_efficiency': 0.55,     # 55% electrical efficiency
            'thermal_efficiency': 0.35,        # 35% thermal efficiency (CHP)
            'capacity_factor': 0.85,           # 85% capacity factor
            'degradation_rate': 0.5,           # 0.5% per 1000 hours
            'stack_lifetime': 80000,           # 80,000 hours
            'system_lifetime': 20,             # 20 years
            'availability': 0.95               # 95% availability
        }
        
        # Economic Parameters (Nigeria context)
        self.economic_params = {
            'discount_rate': 0.15,             # 15% WACC
            'inflation_rate': 0.185,           # 18.5% Nigeria inflation
            'usd_inflation': 0.035,            # 3.5% USD inflation
            'exchange_rate': 1650,             # USD/NGN
            'exchange_volatility': 0.25,       # 25% annual volatility
            'tax_rate': 0.30,                  # 30% corporate tax
            'depreciation_period': 10          # 10-year depreciation
        }
        
        # Cost Parameters
        self.cost_params = {
            'capex_usd_per_kw': self.get_capex_by_size(self.system_size_kw),
            'opex_fixed_usd_per_kw_year': 70,  # Fixed O&M
            'opex_variable_usd_per_mwh': 5,    # Variable O&M
            'fuel_cost_usd_per_mmbtu': 2.50,   # Natural gas cost
            'fuel_heat_rate': 7.5,             # MMBtu/MWh (HHV)
            'stack_replacement_cost': 600,     # USD/kW
            'stack_replacement_interval': 10   # years
        }
        
        # Revenue Parameters
        self.revenue_params = {
            'electricity_tariff': 0.12,        # USD/kWh (industrial rate)
            'thermal_value': 0.05,             # USD/kWh thermal equivalent
            'capacity_payment': 50,            # USD/kW/year
            'green_certificate': 0.02,         # USD/kWh (carbon credits)
            'escalation_rate': 0.03            # 3% annual escalation
        }
    
    def get_capex_by_size(self, capacity_kw):
        """
        Get CAPEX based on system size with economies of scale
        """
        if capacity_kw <= 100:
            return 2300
        elif capacity_kw <= 250:
            return 1950
        elif capacity_kw <= 500:
            return 1750
        elif capacity_kw <= 1000:
            return 1630
        else:
            return 1500  # Extrapolated for larger systems
    
    def calculate_annual_generation(self):
        """
        Calculate annual electricity generation
        """
        hours_per_year = 8760
        annual_generation_mwh = (
            self.system_size_kw * 
            hours_per_year * 
            self.sofc_params['capacity_factor'] * 
            self.sofc_params['availability']
        ) / 1000
        
        return annual_generation_mwh
    
    def calculate_annual_costs(self, year):
        """
        Calculate annual costs for a given year
        """
        # Inflation adjustment
        inflation_factor = (1 + self.economic_params['inflation_rate']) ** (year - 1)
        
        # Fixed O&M costs
        fixed_om = (
            self.cost_params['opex_fixed_usd_per_kw_year'] * 
            self.system_size_kw * 
            inflation_factor
        )
        
        # Variable O&M costs
        annual_generation = self.calculate_annual_generation()
        variable_om = (
            self.cost_params['opex_variable_usd_per_mwh'] * 
            annual_generation * 
            inflation_factor
        )
        
        # Fuel costs
        fuel_consumption_mmbtu = annual_generation * self.cost_params['fuel_heat_rate']
        fuel_cost = (
            fuel_consumption_mmbtu * 
            self.cost_params['fuel_cost_usd_per_mmbtu'] * 
            inflation_factor
        )
        
        # Stack replacement (if applicable)
        stack_replacement = 0
        if year % self.cost_params['stack_replacement_interval'] == 0 and year > 0:
            stack_replacement = (
                self.cost_params['stack_replacement_cost'] * 
                self.system_size_kw * 
                inflation_factor
            )
        
        total_annual_cost = fixed_om + variable_om + fuel_cost + stack_replacement
        
        return {
            'fixed_om': fixed_om,
            'variable_om': variable_om,
            'fuel_cost': fuel_cost,
            'stack_replacement': stack_replacement,
            'total': total_annual_cost
        }
    
    def calculate_annual_revenues(self, year):
        """
        Calculate annual revenues for a given year
        """
        # Revenue escalation
        escalation_factor = (1 + self.revenue_params['escalation_rate']) ** (year - 1)
        
        annual_generation = self.calculate_annual_generation()
        
        # Electricity sales revenue
        electricity_revenue = (
            annual_generation * 1000 *  # Convert to kWh
            self.revenue_params['electricity_tariff'] * 
            escalation_factor
        )
        
        # Thermal energy revenue (CHP)
        thermal_generation = annual_generation * (
            self.sofc_params['thermal_efficiency'] / 
            self.sofc_params['electrical_efficiency']
        )
        thermal_revenue = (
            thermal_generation * 1000 * 
            self.revenue_params['thermal_value'] * 
            escalation_factor
        )
        
        # Capacity payments
        capacity_revenue = (
            self.system_size_kw * 
            self.revenue_params['capacity_payment'] * 
            escalation_factor
        )
        
        # Green certificates/carbon credits
        green_revenue = (
            annual_generation * 1000 * 
            self.revenue_params['green_certificate'] * 
            escalation_factor
        )
        
        total_revenue = electricity_revenue + thermal_revenue + capacity_revenue + green_revenue
        
        return {
            'electricity': electricity_revenue,
            'thermal': thermal_revenue,
            'capacity': capacity_revenue,
            'green_certificates': green_revenue,
            'total': total_revenue
        }
    
    def calculate_depreciation(self, year):
        """
        Calculate annual depreciation (straight-line method)
        """
        if year <= self.economic_params['depreciation_period']:
            capex = self.cost_params['capex_usd_per_kw'] * self.system_size_kw
            return capex / self.economic_params['depreciation_period']
        else:
            return 0
    
    def calculate_taxes(self, ebitda, depreciation):
        """
        Calculate taxes based on EBITDA and depreciation
        """
        taxable_income = max(0, ebitda - depreciation)
        return taxable_income * self.economic_params['tax_rate']
    
    def calculate_cash_flows(self):
        """
        Calculate annual cash flows for the project
        """
        cash_flows = []
        
        # Initial investment (Year 0)
        initial_investment = -(
            self.cost_params['capex_usd_per_kw'] * self.system_size_kw
        )
        cash_flows.append(initial_investment)
        
        # Annual cash flows (Years 1-20)
        for year in range(1, self.analysis_period + 1):
            revenues = self.calculate_annual_revenues(year)
            costs = self.calculate_annual_costs(year)
            
            # EBITDA
            ebitda = revenues['total'] - costs['total']
            
            # Depreciation
            depreciation = self.calculate_depreciation(year)
            
            # Taxes
            taxes = self.calculate_taxes(ebitda, depreciation)
            
            # Net cash flow (EBITDA - Taxes)
            net_cash_flow = ebitda - taxes
            
            cash_flows.append(net_cash_flow)
        
        return np.array(cash_flows)
    
    def calculate_npv(self, discount_rate=None):
        """
        Calculate Net Present Value
        """
        if discount_rate is None:
            discount_rate = self.economic_params['discount_rate']
        
        cash_flows = self.calculate_cash_flows()
        
        # Calculate NPV
        npv = 0
        for i, cf in enumerate(cash_flows):
            npv += cf / (1 + discount_rate) ** i
        
        return npv
    
    def calculate_irr(self):
        """
        Calculate Internal Rate of Return
        """
        cash_flows = self.calculate_cash_flows()
        
        # Use scipy to solve for IRR
        def npv_function(rate):
            return sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))
        
        try:
            irr = fsolve(npv_function, 0.1)[0]
            return irr
        except:
            return np.nan
    
    def calculate_payback_period(self):
        """
        Calculate simple and discounted payback periods
        """
        cash_flows = self.calculate_cash_flows()
        initial_investment = abs(cash_flows[0])
        
        # Simple payback
        cumulative_cf = 0
        simple_payback = np.nan
        for i in range(1, len(cash_flows)):
            cumulative_cf += cash_flows[i]
            if cumulative_cf >= initial_investment:
                simple_payback = i - 1 + (initial_investment - (cumulative_cf - cash_flows[i])) / cash_flows[i]
                break
        
        # Discounted payback
        cumulative_dcf = 0
        discounted_payback = np.nan
        discount_rate = self.economic_params['discount_rate']
        
        for i in range(1, len(cash_flows)):
            discounted_cf = cash_flows[i] / (1 + discount_rate) ** i
            cumulative_dcf += discounted_cf
            if cumulative_dcf >= initial_investment:
                prev_cumulative = cumulative_dcf - discounted_cf
                discounted_payback = i - 1 + (initial_investment - prev_cumulative) / discounted_cf
                break
        
        return simple_payback, discounted_payback
    
    def calculate_lcoe(self):
        """
        Calculate Levelized Cost of Electricity
        """
        discount_rate = self.economic_params['discount_rate']
        
        # Present value of costs
        pv_costs = abs(self.calculate_cash_flows()[0])  # Initial investment
        
        for year in range(1, self.analysis_period + 1):
            annual_costs = self.calculate_annual_costs(year)['total']
            pv_costs += annual_costs / (1 + discount_rate) ** year
        
        # Present value of generation
        pv_generation = 0
        annual_generation_mwh = self.calculate_annual_generation()
        
        for year in range(1, self.analysis_period + 1):
            pv_generation += (annual_generation_mwh * 1000) / (1 + discount_rate) ** year
        
        lcoe = pv_costs / pv_generation
        return lcoe
    
    def sensitivity_analysis(self, variables, ranges):
        """
        Perform sensitivity analysis on key variables
        """
        base_npv = self.calculate_npv()
        results = {}
        
        for variable, range_values in zip(variables, ranges):
            npv_values = []
            
            for value in range_values:
                # Temporarily modify the parameter
                original_value = self.modify_parameter(variable, value)
                
                # Calculate NPV with modified parameter
                npv = self.calculate_npv()
                npv_values.append(npv)
                
                # Restore original value
                self.modify_parameter(variable, original_value)
            
            results[variable] = {
                'range': range_values,
                'npv_values': npv_values,
                'sensitivity': [(npv - base_npv) / base_npv * 100 for npv in npv_values]
            }
        
        return results
    
    def modify_parameter(self, parameter, value):
        """
        Modify a parameter and return the original value
        """
        if parameter == 'capex':
            original = self.cost_params['capex_usd_per_kw']
            self.cost_params['capex_usd_per_kw'] = value
            return original
        elif parameter == 'fuel_cost':
            original = self.cost_params['fuel_cost_usd_per_mmbtu']
            self.cost_params['fuel_cost_usd_per_mmbtu'] = value
            return original
        elif parameter == 'electricity_tariff':
            original = self.revenue_params['electricity_tariff']
            self.revenue_params['electricity_tariff'] = value
            return original
        elif parameter == 'discount_rate':
            original = self.economic_params['discount_rate']
            self.economic_params['discount_rate'] = value
            return original
        else:
            return None
    
    def monte_carlo_simulation(self, n_iterations=10000):
        """
        Perform Monte Carlo simulation for risk analysis
        """
        np.random.seed(42)  # For reproducibility
        
        npv_results = []
        irr_results = []
        lcoe_results = []
        
        for _ in range(n_iterations):
            # Sample random variables
            capex_factor = np.random.triangular(0.8, 1.0, 1.3)  # -20% to +30%
            fuel_cost_factor = np.random.lognormal(0, 0.2)      # Lognormal distribution
            tariff_factor = np.random.normal(1.0, 0.1)          # ±10% normal
            discount_factor = np.random.uniform(0.9, 1.4)       # 10% to 22%
            
            # Apply factors
            original_capex = self.cost_params['capex_usd_per_kw']
            original_fuel = self.cost_params['fuel_cost_usd_per_mmbtu']
            original_tariff = self.revenue_params['electricity_tariff']
            original_discount = self.economic_params['discount_rate']
            
            self.cost_params['capex_usd_per_kw'] = original_capex * capex_factor
            self.cost_params['fuel_cost_usd_per_mmbtu'] = original_fuel * fuel_cost_factor
            self.revenue_params['electricity_tariff'] = original_tariff * tariff_factor
            self.economic_params['discount_rate'] = original_discount * discount_factor
            
            # Calculate metrics
            npv = self.calculate_npv()
            irr = self.calculate_irr()
            lcoe = self.calculate_lcoe()
            
            npv_results.append(npv)
            irr_results.append(irr)
            lcoe_results.append(lcoe)
            
            # Restore original values
            self.cost_params['capex_usd_per_kw'] = original_capex
            self.cost_params['fuel_cost_usd_per_mmbtu'] = original_fuel
            self.revenue_params['electricity_tariff'] = original_tariff
            self.economic_params['discount_rate'] = original_discount
        
        return {
            'npv': np.array(npv_results),
            'irr': np.array(irr_results),
            'lcoe': np.array(lcoe_results)
        }
    
    def generate_financial_summary(self):
        """
        Generate comprehensive financial summary
        """
        # Calculate key metrics
        npv = self.calculate_npv()
        irr = self.calculate_irr()
        lcoe = self.calculate_lcoe()
        simple_payback, discounted_payback = self.calculate_payback_period()
        
        # Cash flow analysis
        cash_flows = self.calculate_cash_flows()
        
        summary = {
            'system_parameters': {
                'capacity_kw': self.system_size_kw,
                'analysis_period': self.analysis_period,
                'capacity_factor': self.sofc_params['capacity_factor'],
                'annual_generation_mwh': self.calculate_annual_generation()
            },
            'financial_metrics': {
                'npv_usd': npv,
                'irr_percent': irr * 100 if not np.isnan(irr) else np.nan,
                'lcoe_usd_per_kwh': lcoe,
                'simple_payback_years': simple_payback,
                'discounted_payback_years': discounted_payback
            },
            'cost_breakdown': {
                'total_capex_usd': self.cost_params['capex_usd_per_kw'] * self.system_size_kw,
                'capex_per_kw': self.cost_params['capex_usd_per_kw'],
                'annual_opex_year1': self.calculate_annual_costs(1)['total'],
                'fuel_cost_percentage': (
                    self.calculate_annual_costs(1)['fuel_cost'] / 
                    self.calculate_annual_costs(1)['total'] * 100
                )
            },
            'revenue_breakdown': {
                'annual_revenue_year1': self.calculate_annual_revenues(1)['total'],
                'electricity_tariff': self.revenue_params['electricity_tariff'],
                'thermal_value': self.revenue_params['thermal_value']
            },
            'economic_assumptions': {
                'discount_rate': self.economic_params['discount_rate'],
                'inflation_rate': self.economic_params['inflation_rate'],
                'tax_rate': self.economic_params['tax_rate'],
                'fuel_cost_usd_per_mmbtu': self.cost_params['fuel_cost_usd_per_mmbtu']
            }
        }
        
        return summary
    
    def export_results(self, filename='sofc_tea_results.xlsx'):
        """
        Export TEA results to Excel
        """
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Financial summary
            summary = self.generate_financial_summary()
            summary_df = pd.DataFrame([
                {'Metric': 'NPV (USD)', 'Value': f"${summary['financial_metrics']['npv_usd']:,.0f}"},
                {'Metric': 'IRR (%)', 'Value': f"{summary['financial_metrics']['irr_percent']:.1f}%"},
                {'Metric': 'LCOE (USD/kWh)', 'Value': f"${summary['financial_metrics']['lcoe_usd_per_kwh']:.3f}"},
                {'Metric': 'Simple Payback (years)', 'Value': f"{summary['financial_metrics']['simple_payback_years']:.1f}"},
                {'Metric': 'Discounted Payback (years)', 'Value': f"{summary['financial_metrics']['discounted_payback_years']:.1f}"},
                {'Metric': 'Total CAPEX (USD)', 'Value': f"${summary['cost_breakdown']['total_capex_usd']:,.0f}"},
                {'Metric': 'CAPEX per kW', 'Value': f"${summary['cost_breakdown']['capex_per_kw']:,.0f}"},
                {'Metric': 'Annual Generation (MWh)', 'Value': f"{summary['system_parameters']['annual_generation_mwh']:,.0f}"}
            ])
            summary_df.to_excel(writer, sheet_name='Financial_Summary', index=False)
            
            # Annual cash flows
            cash_flows = self.calculate_cash_flows()
            years = list(range(0, self.analysis_period + 1))
            
            cash_flow_data = []
            for year in years:
                if year == 0:
                    cash_flow_data.append({
                        'Year': year,
                        'Cash_Flow_USD': cash_flows[year],
                        'Cumulative_Cash_Flow_USD': cash_flows[year],
                        'Discounted_Cash_Flow_USD': cash_flows[year],
                        'Cumulative_DCF_USD': cash_flows[year]
                    })
                else:
                    dcf = cash_flows[year] / (1 + self.economic_params['discount_rate']) ** year
                    cash_flow_data.append({
                        'Year': year,
                        'Cash_Flow_USD': cash_flows[year],
                        'Cumulative_Cash_Flow_USD': sum(cash_flows[:year+1]),
                        'Discounted_Cash_Flow_USD': dcf,
                        'Cumulative_DCF_USD': cash_flow_data[-1]['Cumulative_DCF_USD'] + dcf
                    })
            
            cash_flow_df = pd.DataFrame(cash_flow_data)
            cash_flow_df.to_excel(writer, sheet_name='Cash_Flows', index=False)
            
            # Sensitivity analysis
            variables = ['capex', 'fuel_cost', 'electricity_tariff', 'discount_rate']
            ranges = [
                np.linspace(1400, 2600, 11),  # CAPEX: $1400-2600/kW
                np.linspace(2.0, 4.0, 11),    # Fuel: $2-4/MMBtu
                np.linspace(0.08, 0.16, 11),  # Tariff: $0.08-0.16/kWh
                np.linspace(0.10, 0.22, 11)   # Discount: 10-22%
            ]
            
            sensitivity_results = self.sensitivity_analysis(variables, ranges)
            
            for variable in variables:
                sens_df = pd.DataFrame({
                    'Parameter_Value': sensitivity_results[variable]['range'],
                    'NPV_USD': sensitivity_results[variable]['npv_values'],
                    'NPV_Change_Percent': sensitivity_results[variable]['sensitivity']
                })
                sens_df.to_excel(writer, sheet_name=f'Sensitivity_{variable}', index=False)
        
        print(f"TEA results exported to {filename}")

def main():
    """
    Main function to run TEA calculations
    """
    print("Running SOFC Techno-Economic Analysis...")
    
    # Create TEA calculator for different system sizes
    system_sizes = [100, 250, 500, 1000]
    
    for size in system_sizes:
        print(f"\nAnalyzing {size}kW SOFC system...")
        
        tea = SOFCTEACalculator(system_size_kw=size)
        summary = tea.generate_financial_summary()
        
        print(f"NPV: ${summary['financial_metrics']['npv_usd']:,.0f}")
        print(f"IRR: {summary['financial_metrics']['irr_percent']:.1f}%")
        print(f"LCOE: ${summary['financial_metrics']['lcoe_usd_per_kwh']:.3f}/kWh")
        print(f"Payback: {summary['financial_metrics']['simple_payback_years']:.1f} years")
        
        # Export results for the 500kW system
        if size == 500:
            tea.export_results(f'sofc_tea_results_{size}kw.xlsx')
    
    print("\nTEA analysis completed!")

if __name__ == "__main__":
    main()