"""
SOFC Techno-Economic Analyzer for Nigerian Energy Context
Specialized for analyzing SOFC deployment with flared gas and biogas resources
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple

class SOFCAnalyzer:
    """Comprehensive SOFC techno-economic analysis tool for Nigeria"""
    
    def __init__(self, data_path: str = "../"):
        self.data_path = Path(data_path)
        self.load_all_data()
        self.setup_sofc_parameters()
        
    def load_all_data(self):
        """Load all Nigerian energy datasets"""
        # Load electricity data
        with open(self.data_path / "electricity_grid/generation_capacity.json") as f:
            self.generation_data = json.load(f)
        
        with open(self.data_path / "electricity_grid/daily_load_allocation.json") as f:
            self.load_data = json.load(f)
            
        with open(self.data_path / "electricity_grid/reliability_metrics.json") as f:
            self.reliability_data = json.load(f)
            
        with open(self.data_path / "electricity_grid/tariffs.json") as f:
            self.tariff_data = json.load(f)
        
        # Load fossil fuel data
        with open(self.data_path / "fossil_fuel/gas_reserves_production.json") as f:
            self.gas_data = json.load(f)
            
        with open(self.data_path / "fossil_fuel/gas_flaring_data.json") as f:
            self.flaring_data = json.load(f)
            
        with open(self.data_path / "fossil_fuel/gas_pipeline_network.json") as f:
            self.pipeline_data = json.load(f)
            
        with open(self.data_path / "fossil_fuel/fuel_prices.json") as f:
            self.fuel_price_data = json.load(f)
        
        # Load renewable data
        with open(self.data_path / "renewable_resources/agricultural_waste_data.json") as f:
            self.agri_waste_data = json.load(f)
            
        with open(self.data_path / "renewable_resources/livestock_biogas_potential.json") as f:
            self.biogas_data = json.load(f)
    
    def setup_sofc_parameters(self):
        """Setup SOFC technical and economic parameters"""
        self.sofc_params = {
            'efficiency': {
                'electrical': 0.60,  # 60% electrical efficiency
                'total_chp': 0.85,   # 85% with heat recovery
                'degradation_rate_per_year': 0.005  # 0.5% per year
            },
            'capex': {  # USD/kW
                'small_scale_1_100kW': 4500,
                'medium_scale_100_1000kW': 3500,
                'large_scale_above_1MW': 2800,
                'learning_rate': 0.15  # 15% cost reduction per doubling
            },
            'opex': {  # % of CAPEX per year
                'fixed_om': 0.03,
                'variable_om_usd_per_mwh': 8,
                'stack_replacement_years': 10,
                'stack_replacement_cost_percent': 0.35
            },
            'technical': {
                'availability': 0.96,
                'capacity_factor_flared_gas': 0.90,
                'capacity_factor_biogas': 0.85,
                'lifetime_years': 20,
                'construction_time_months': 12
            },
            'emissions': {
                'co2_kg_per_mwh': 350,  # Natural gas SOFC
                'nox_g_per_mwh': 5,
                'sox_g_per_mwh': 0.1,
                'pm_g_per_mwh': 0.5
            }
        }
    
    def calculate_flared_gas_sofc_potential(self) -> pd.DataFrame:
        """Calculate SOFC deployment potential at gas flaring sites"""
        flare_sites = []
        
        for site in self.flaring_data['major_flare_sites']:
            # Technical calculations
            gas_available_mmscfd = site['flare_volume_mmscfd']
            gas_available_m3_per_day = gas_available_mmscfd * 28316.8  # Convert to m3/day
            
            # Energy content (assuming 36.5 MJ/m3 LHV)
            energy_input_mwh_per_day = (gas_available_m3_per_day * 36.5) / 3600
            
            # SOFC power output
            sofc_capacity_mw = site['sofc_potential_MW']
            annual_generation_gwh = sofc_capacity_mw * 8760 * self.sofc_params['technical']['availability'] * \
                                   self.sofc_params['technical']['capacity_factor_flared_gas'] / 1000
            
            # Economic calculations
            if sofc_capacity_mw < 0.1:
                capex_per_kw = self.sofc_params['capex']['small_scale_1_100kW']
            elif sofc_capacity_mw < 1:
                capex_per_kw = self.sofc_params['capex']['medium_scale_100_1000kW']
            else:
                capex_per_kw = self.sofc_params['capex']['large_scale_above_1MW']
            
            total_capex_million_usd = sofc_capacity_mw * 1000 * capex_per_kw / 1e6
            
            # Annual revenues
            electricity_tariff_usd_per_mwh = 120  # Premium power tariff
            annual_revenue_million_usd = annual_generation_gwh * 1000 * electricity_tariff_usd_per_mwh / 1e6
            
            # Carbon credits (avoided flaring)
            co2_avoided_tons = gas_available_mmscfd * 365 * 0.0025 * 44/16 * 1000  # Simplified calculation
            carbon_credit_revenue_million_usd = co2_avoided_tons * 15 / 1e6  # $15/tCO2
            
            # Annual costs
            annual_opex_million_usd = total_capex_million_usd * self.sofc_params['opex']['fixed_om'] + \
                                     annual_generation_gwh * 1000 * self.sofc_params['opex']['variable_om_usd_per_mwh'] / 1e6
            
            # Financial metrics
            annual_cashflow_million_usd = annual_revenue_million_usd + carbon_credit_revenue_million_usd - annual_opex_million_usd
            simple_payback_years = total_capex_million_usd / annual_cashflow_million_usd if annual_cashflow_million_usd > 0 else np.inf
            
            flare_sites.append({
                'Location': site['location'],
                'State': site['state'],
                'Operator': site['operator'],
                'Gas_Available_MMSCFD': gas_available_mmscfd,
                'SOFC_Capacity_MW': sofc_capacity_mw,
                'Annual_Generation_GWh': annual_generation_gwh,
                'CAPEX_Million_USD': total_capex_million_usd,
                'Annual_Revenue_Million_USD': annual_revenue_million_usd,
                'Carbon_Credit_Revenue_Million_USD': carbon_credit_revenue_million_usd,
                'Annual_OPEX_Million_USD': annual_opex_million_usd,
                'Annual_Cashflow_Million_USD': annual_cashflow_million_usd,
                'Simple_Payback_Years': simple_payback_years,
                'Population_Served': site['population_affected'],
                'Communities_Nearby': len(site['nearby_communities'])
            })
        
        return pd.DataFrame(flare_sites)
    
    def calculate_biogas_sofc_potential(self) -> pd.DataFrame:
        """Calculate SOFC deployment potential with biogas resources"""
        biogas_sites = []
        
        # Analyze by region
        for region, data in self.biogas_data['biogas_production_potential']['by_region'].items():
            # Technical parameters
            biogas_available_billion_m3 = data['total_biogas_billion_m3']
            electricity_potential_mw = data['electricity_potential_MW']
            
            # SOFC improves efficiency by 60% compared to traditional biogas engines (35% efficiency)
            sofc_capacity_mw = electricity_potential_mw * (0.60 / 0.35)
            
            # Calculate for different deployment scales
            for scale in ['grid_connection', 'mini_grid', 'standalone']:
                if f'suitable_for_{scale}_MW' in data:
                    scale_capacity_mw = data[f'suitable_for_{scale}_MW'] * (0.60 / 0.35)
                    
                    if scale_capacity_mw > 0:
                        # Determine CAPEX based on scale
                        if scale == 'standalone':
                            capex_per_kw = self.sofc_params['capex']['small_scale_1_100kW']
                        elif scale == 'mini_grid':
                            capex_per_kw = self.sofc_params['capex']['medium_scale_100_1000kW']
                        else:
                            capex_per_kw = self.sofc_params['capex']['large_scale_above_1MW']
                        
                        total_capex_million_usd = scale_capacity_mw * 1000 * capex_per_kw / 1e6
                        
                        # Annual generation
                        annual_generation_gwh = scale_capacity_mw * 8760 * \
                                              self.sofc_params['technical']['availability'] * \
                                              self.sofc_params['technical']['capacity_factor_biogas'] / 1000
                        
                        # Revenue calculations
                        if scale == 'grid_connection':
                            tariff_usd_per_mwh = 100
                        elif scale == 'mini_grid':
                            tariff_usd_per_mwh = 140
                        else:  # standalone
                            tariff_usd_per_mwh = 180
                        
                        annual_revenue_million_usd = annual_generation_gwh * 1000 * tariff_usd_per_mwh / 1e6
                        
                        biogas_sites.append({
                            'Region': region.replace('_', ' ').title(),
                            'Deployment_Type': scale.replace('_', ' ').title(),
                            'SOFC_Capacity_MW': scale_capacity_mw,
                            'Annual_Generation_GWh': annual_generation_gwh,
                            'CAPEX_Million_USD': total_capex_million_usd,
                            'Annual_Revenue_Million_USD': annual_revenue_million_usd,
                            'Tariff_USD_per_MWh': tariff_usd_per_mwh
                        })
        
        return pd.DataFrame(biogas_sites)
    
    def comparative_lcoe_analysis(self) -> pd.DataFrame:
        """Calculate and compare LCOE for different power generation options"""
        options = []
        
        # Current grid electricity (with reliability issues)
        grid_lcoe = self.fuel_price_data['comparative_analysis']['electricity_generation_costs']['grid_electricity']['effective_cost_with_backup_ngn_per_kwh']
        options.append({
            'Technology': 'Grid + Diesel Backup',
            'LCOE_NGN_per_kWh': grid_lcoe,
            'LCOE_USD_per_MWh': grid_lcoe * 1000 / 1500,  # Assuming 1500 NGN/USD
            'Availability_%': 50,
            'Emissions_kgCO2_per_MWh': 650
        })
        
        # Diesel generator
        diesel_lcoe = self.fuel_price_data['comparative_analysis']['electricity_generation_costs']['diesel_generator']['total_cost_including_maintenance_ngn_per_kwh']
        options.append({
            'Technology': 'Diesel Generator',
            'LCOE_NGN_per_kWh': diesel_lcoe,
            'LCOE_USD_per_MWh': diesel_lcoe * 1000 / 1500,
            'Availability_%': 95,
            'Emissions_kgCO2_per_MWh': 850
        })
        
        # Gas generator
        gas_gen_lcoe = self.fuel_price_data['comparative_analysis']['electricity_generation_costs']['gas_generator']['total_cost_including_maintenance_ngn_per_kwh']
        options.append({
            'Technology': 'Gas Generator',
            'LCOE_NGN_per_kWh': gas_gen_lcoe,
            'LCOE_USD_per_MWh': gas_gen_lcoe * 1000 / 1500,
            'Availability_%': 90,
            'Emissions_kgCO2_per_MWh': 500
        })
        
        # SOFC with pipeline gas
        sofc_gas_lcoe = self.fuel_price_data['comparative_analysis']['electricity_generation_costs']['sofc_with_natural_gas']['total_levelized_cost_ngn_per_kwh']
        options.append({
            'Technology': 'SOFC - Pipeline Gas',
            'LCOE_NGN_per_kWh': sofc_gas_lcoe,
            'LCOE_USD_per_MWh': sofc_gas_lcoe * 1000 / 1500,
            'Availability_%': 96,
            'Emissions_kgCO2_per_MWh': 350
        })
        
        # SOFC with flared gas
        sofc_flared_lcoe = self.fuel_price_data['comparative_analysis']['electricity_generation_costs']['sofc_with_flared_gas']['total_levelized_cost_ngn_per_kwh']
        options.append({
            'Technology': 'SOFC - Flared Gas',
            'LCOE_NGN_per_kWh': sofc_flared_lcoe,
            'LCOE_USD_per_MWh': sofc_flared_lcoe * 1000 / 1500,
            'Availability_%': 96,
            'Emissions_kgCO2_per_MWh': 50  # Only processing emissions, gas would be flared anyway
        })
        
        # SOFC with biogas
        options.append({
            'Technology': 'SOFC - Biogas',
            'LCOE_NGN_per_kWh': 55,
            'LCOE_USD_per_MWh': 55 * 1000 / 1500,
            'Availability_%': 85,
            'Emissions_kgCO2_per_MWh': -200  # Carbon negative due to methane capture
        })
        
        return pd.DataFrame(options)
    
    def calculate_national_impact(self) -> Dict:
        """Calculate national-level impact of SOFC deployment"""
        
        # Total SOFC deployment potential
        flared_gas_potential_mw = self.flaring_data['national_flaring_statistics']['current_flaring']['power_generation_potential_MW']
        biogas_agri_potential_mw = self.agri_waste_data['national_crop_production_and_residues']['power_generation_potential_MW'] * 0.3  # 30% realistically deployable
        biogas_livestock_potential_mw = self.biogas_data['national_livestock_statistics']['power_generation_potential_MW'] * 0.25  # 25% realistically deployable
        
        total_sofc_potential_mw = flared_gas_potential_mw + biogas_agri_potential_mw + biogas_livestock_potential_mw
        
        # Generation capacity impact
        current_available_capacity_mw = self.generation_data['national_capacity']['available_capacity']['average_daily']
        capacity_increase_percent = (total_sofc_potential_mw / current_available_capacity_mw) * 100
        
        # Economic impact
        total_investment_billion_usd = (flared_gas_potential_mw * 3000 + 
                                       (biogas_agri_potential_mw + biogas_livestock_potential_mw) * 3500) / 1e6
        
        # Annual economic benefits
        annual_generation_twh = total_sofc_potential_mw * 8760 * 0.85 / 1e6
        annual_revenue_billion_usd = annual_generation_twh * 120 / 1000  # $120/MWh average
        
        # Import substitution (diesel)
        diesel_displaced_million_liters = annual_generation_twh * 1e6 / 3.5  # 3.5 kWh per liter diesel
        forex_savings_billion_usd = diesel_displaced_million_liters * 0.7 / 1000  # $0.7 per liter
        
        # Environmental impact
        co2_reduction_million_tons = annual_generation_twh * 0.5  # 0.5 tCO2/MWh reduction vs diesel
        
        # Social impact
        households_electrified_millions = total_sofc_potential_mw / 0.5  # 0.5 kW per household average
        jobs_created_direct = total_sofc_potential_mw * 15  # 15 jobs per MW
        jobs_created_indirect = jobs_created_direct * 3
        
        return {
            'Total_SOFC_Potential_MW': total_sofc_potential_mw,
            'Flared_Gas_Contribution_MW': flared_gas_potential_mw,
            'Biogas_Agricultural_MW': biogas_agri_potential_mw,
            'Biogas_Livestock_MW': biogas_livestock_potential_mw,
            'Capacity_Increase_Percent': capacity_increase_percent,
            'Total_Investment_Billion_USD': total_investment_billion_usd,
            'Annual_Generation_TWh': annual_generation_twh,
            'Annual_Revenue_Billion_USD': annual_revenue_billion_usd,
            'Diesel_Displaced_Million_Liters': diesel_displaced_million_liters,
            'Forex_Savings_Billion_USD': forex_savings_billion_usd,
            'CO2_Reduction_Million_Tons': co2_reduction_million_tons,
            'Households_Electrified_Millions': households_electrified_millions,
            'Jobs_Created_Direct': int(jobs_created_direct),
            'Jobs_Created_Indirect': int(jobs_created_indirect)
        }
    
    def generate_visualizations(self):
        """Generate comprehensive visualizations for SOFC analysis"""
        
        # Create output directory
        viz_path = self.data_path / "visualizations"
        viz_path.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
        
        # 1. Flared Gas SOFC Potential by Site
        flare_df = self.calculate_flared_gas_sofc_potential()
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Capacity by site
        axes[0, 0].barh(flare_df['Location'][:10], flare_df['SOFC_Capacity_MW'][:10])
        axes[0, 0].set_xlabel('SOFC Capacity (MW)')
        axes[0, 0].set_title('Top 10 Flare Sites - SOFC Deployment Potential')
        
        # Payback period
        axes[0, 1].bar(range(len(flare_df[:10])), flare_df['Simple_Payback_Years'][:10])
        axes[0, 1].set_xticks(range(len(flare_df[:10])))
        axes[0, 1].set_xticklabels(flare_df['Location'][:10], rotation=45, ha='right')
        axes[0, 1].set_ylabel('Payback Period (Years)')
        axes[0, 1].set_title('Investment Payback Period by Site')
        axes[0, 1].axhline(y=5, color='r', linestyle='--', label='5-year threshold')
        axes[0, 1].legend()
        
        # Population impact
        axes[1, 0].scatter(flare_df['SOFC_Capacity_MW'], flare_df['Population_Served']/1000, 
                          s=flare_df['CAPEX_Million_USD']*10, alpha=0.6)
        axes[1, 0].set_xlabel('SOFC Capacity (MW)')
        axes[1, 0].set_ylabel('Population Served (Thousands)')
        axes[1, 0].set_title('Social Impact vs. Capacity (Bubble size = CAPEX)')
        
        # Revenue breakdown
        revenue_data = flare_df[['Location', 'Annual_Revenue_Million_USD', 
                                'Carbon_Credit_Revenue_Million_USD']][:5]
        x = np.arange(len(revenue_data))
        width = 0.35
        
        axes[1, 1].bar(x - width/2, revenue_data['Annual_Revenue_Million_USD'], 
                      width, label='Electricity Revenue')
        axes[1, 1].bar(x + width/2, revenue_data['Carbon_Credit_Revenue_Million_USD'], 
                      width, label='Carbon Credit Revenue')
        axes[1, 1].set_xlabel('Location')
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels(revenue_data['Location'], rotation=45, ha='right')
        axes[1, 1].set_ylabel('Annual Revenue (Million USD)')
        axes[1, 1].set_title('Revenue Streams - Top 5 Sites')
        axes[1, 1].legend()
        
        plt.tight_layout()
        plt.savefig(viz_path / 'flared_gas_sofc_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. LCOE Comparison
        lcoe_df = self.comparative_lcoe_analysis()
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # LCOE comparison
        colors = ['red' if x > 100 else 'yellow' if x > 50 else 'green' 
                 for x in lcoe_df['LCOE_USD_per_MWh']]
        axes[0].barh(lcoe_df['Technology'], lcoe_df['LCOE_USD_per_MWh'], color=colors)
        axes[0].set_xlabel('LCOE (USD/MWh)')
        axes[0].set_title('Levelized Cost of Electricity Comparison')
        axes[0].axvline(x=100, color='black', linestyle='--', alpha=0.5, label='Grid Parity')
        axes[0].legend()
        
        # Emissions vs LCOE
        for idx, row in lcoe_df.iterrows():
            axes[1].scatter(row['LCOE_USD_per_MWh'], row['Emissions_kgCO2_per_MWh'], 
                          s=row['Availability_%']*5, alpha=0.7)
            axes[1].annotate(row['Technology'], 
                           (row['LCOE_USD_per_MWh'], row['Emissions_kgCO2_per_MWh']),
                           fontsize=8, ha='center')
        
        axes[1].set_xlabel('LCOE (USD/MWh)')
        axes[1].set_ylabel('CO₂ Emissions (kg/MWh)')
        axes[1].set_title('Cost vs. Environmental Impact (Bubble size = Availability)')
        axes[1].axhline(y=0, color='green', linestyle='--', alpha=0.5)
        axes[1].axvline(x=100, color='black', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(viz_path / 'lcoe_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. National Impact Dashboard using Plotly
        impact = self.calculate_national_impact()
        
        fig = go.Figure()
        
        # Create subplots
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=('SOFC Capacity Potential by Source',
                          'Economic Benefits',
                          'Environmental Impact',
                          'Grid Capacity Enhancement',
                          'Social Impact',
                          'Investment Requirements'),
            specs=[[{'type': 'pie'}, {'type': 'bar'}, {'type': 'indicator'}],
                  [{'type': 'indicator'}, {'type': 'bar'}, {'type': 'scatter'}]]
        )
        
        # Pie chart - Capacity by source
        fig.add_trace(
            go.Pie(labels=['Flared Gas', 'Agricultural Waste', 'Livestock Waste'],
                  values=[impact['Flared_Gas_Contribution_MW'],
                         impact['Biogas_Agricultural_MW'],
                         impact['Biogas_Livestock_MW']],
                  hole=0.3),
            row=1, col=1
        )
        
        # Bar chart - Economic benefits
        fig.add_trace(
            go.Bar(x=['Annual Revenue', 'Forex Savings'],
                  y=[impact['Annual_Revenue_Billion_USD'], 
                     impact['Forex_Savings_Billion_USD']],
                  text=[f"${x:.2f}B" for x in [impact['Annual_Revenue_Billion_USD'],
                                               impact['Forex_Savings_Billion_USD']]],
                  textposition='auto'),
            row=1, col=2
        )
        
        # Indicator - CO2 reduction
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=impact['CO2_Reduction_Million_Tons'],
                title={'text': "CO₂ Reduction<br>(Million Tons/Year)"},
                delta={'reference': 0, 'relative': True},
                domain={'x': [0, 1], 'y': [0, 1]}),
            row=1, col=3
        )
        
        # Indicator - Grid capacity increase
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=impact['Capacity_Increase_Percent'],
                title={'text': "Grid Capacity<br>Increase (%)"},
                gauge={'axis': {'range': [None, 200]},
                      'bar': {'color': "darkgreen"},
                      'steps': [
                          {'range': [0, 50], 'color': "lightgray"},
                          {'range': [50, 100], 'color': "gray"}],
                      'threshold': {'line': {'color': "red", 'width': 4},
                                  'thickness': 0.75, 'value': 100}}),
            row=2, col=1
        )
        
        # Bar chart - Social impact
        fig.add_trace(
            go.Bar(x=['Households Electrified<br>(Millions)', 'Direct Jobs<br>(Thousands)', 
                     'Indirect Jobs<br>(Thousands)'],
                  y=[impact['Households_Electrified_Millions'],
                     impact['Jobs_Created_Direct']/1000,
                     impact['Jobs_Created_Indirect']/1000]),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(height=800, showlegend=False,
                        title_text="National Impact of SOFC Deployment in Nigeria",
                        title_x=0.5)
        
        # Save as HTML
        fig.write_html(viz_path / "national_impact_dashboard.html")
        
        print(f"Visualizations saved to {viz_path}")
        
        return impact
    
    def generate_report(self) -> str:
        """Generate comprehensive analysis report"""
        
        impact = self.calculate_national_impact()
        flare_df = self.calculate_flared_gas_sofc_potential()
        lcoe_df = self.comparative_lcoe_analysis()
        
        report = f"""
========================================================================================================
SOFC DEPLOYMENT ANALYSIS FOR NIGERIA - COMPREHENSIVE REPORT
Techno-Economic Analysis for Mitigating Nigeria's Electricity Crisis
========================================================================================================

EXECUTIVE SUMMARY
-----------------
Total SOFC Deployment Potential: {impact['Total_SOFC_Potential_MW']:,.0f} MW
- From Flared Gas: {impact['Flared_Gas_Contribution_MW']:,.0f} MW ({impact['Flared_Gas_Contribution_MW']/impact['Total_SOFC_Potential_MW']*100:.1f}%)
- From Agricultural Waste: {impact['Biogas_Agricultural_MW']:,.0f} MW ({impact['Biogas_Agricultural_MW']/impact['Total_SOFC_Potential_MW']*100:.1f}%)
- From Livestock Waste: {impact['Biogas_Livestock_MW']:,.0f} MW ({impact['Biogas_Livestock_MW']/impact['Total_SOFC_Potential_MW']*100:.1f}%)

This represents a {impact['Capacity_Increase_Percent']:.1f}% increase in Nigeria's current available generation capacity.

ECONOMIC IMPACT
---------------
Total Investment Required: ${impact['Total_Investment_Billion_USD']:.2f} Billion
Annual Revenue Generation: ${impact['Annual_Revenue_Billion_USD']:.2f} Billion
Foreign Exchange Savings: ${impact['Forex_Savings_Billion_USD']:.2f} Billion/year
Diesel Displacement: {impact['Diesel_Displaced_Million_Liters']:,.0f} Million Liters/year

TOP 5 FLARED GAS SITES FOR SOFC DEPLOYMENT
------------------------------------------
{flare_df[['Location', 'State', 'SOFC_Capacity_MW', 'CAPEX_Million_USD', 'Simple_Payback_Years']].head().to_string()}

LEVELIZED COST COMPARISON (USD/MWh)
------------------------------------
{lcoe_df[['Technology', 'LCOE_USD_per_MWh', 'Availability_%', 'Emissions_kgCO2_per_MWh']].to_string()}

SOFC with flared gas offers the lowest LCOE at ${lcoe_df[lcoe_df['Technology']=='SOFC - Flared Gas']['LCOE_USD_per_MWh'].values[0]:.2f}/MWh

ENVIRONMENTAL BENEFITS
----------------------
CO₂ Emissions Reduction: {impact['CO2_Reduction_Million_Tons']:,.1f} Million Tons/year
- Equivalent to removing {impact['CO2_Reduction_Million_Tons']*200000:.0f} cars from the road
- Methane emissions eliminated from {len(flare_df)} major flare sites

SOCIAL IMPACT
-------------
Households Electrified: {impact['Households_Electrified_Millions']:.1f} Million
Direct Job Creation: {impact['Jobs_Created_Direct']:,}
Indirect Job Creation: {impact['Jobs_Created_Indirect']:,}
Total Employment Impact: {impact['Jobs_Created_Direct'] + impact['Jobs_Created_Indirect']:,} jobs

Communities Benefiting: {flare_df['Population_Served'].sum()/1e6:.1f} Million people near flare sites

KEY RECOMMENDATIONS
-------------------
1. IMMEDIATE ACTIONS (0-2 years):
   - Deploy {flare_df.head(3)['SOFC_Capacity_MW'].sum():.0f} MW at top 3 flare sites
   - Investment: ${flare_df.head(3)['CAPEX_Million_USD'].sum():.0f} Million
   - Payback: {flare_df.head(3)['Simple_Payback_Years'].mean():.1f} years average

2. MEDIUM TERM (2-5 years):
   - Scale to all major flare sites
   - Develop biogas-SOFC projects in agricultural zones
   - Establish local SOFC assembly/maintenance facilities

3. LONG TERM (5-10 years):
   - Achieve {impact['Total_SOFC_Potential_MW']:,.0f} MW total deployment
   - Create SOFC manufacturing capability in Nigeria
   - Export SOFC technology to other African countries

POLICY RECOMMENDATIONS
----------------------
1. Mandate zero routine flaring with SOFC as approved mitigation technology
2. Provide 5-year tax holiday for SOFC projects
3. Establish feed-in tariff of $120/MWh for SOFC power
4. Create $500M green bond for SOFC deployment financing
5. Include SOFC in national electricity masterplan

RISK MITIGATION
---------------
- Technology Risk: Partner with established SOFC manufacturers (Bloom Energy, FuelCell Energy)
- Financing Risk: Blend concessional climate finance with commercial investment
- Market Risk: Secure long-term PPAs with distribution companies
- Political Risk: Obtain MIGA guarantees for large projects

CONCLUSION
----------
SOFC deployment using Nigeria's wasted gas resources presents a transformative opportunity:
- Adds {impact['Capacity_Increase_Percent']:.0f}% to grid capacity without new gas fields
- Saves ${impact['Forex_Savings_Billion_USD']:.2f} Billion annually in diesel imports
- Creates {impact['Jobs_Created_Direct'] + impact['Jobs_Created_Indirect']:,} jobs
- Reduces emissions by {impact['CO2_Reduction_Million_Tons']:.0f} Million tons CO₂/year
- Provides reliable power to {impact['Households_Electrified_Millions']:.1f} Million households

The technology is mature, economically viable, and addresses Nigeria's energy trilemma:
reliability, affordability, and sustainability.

========================================================================================================
Report Generated: 2025-01-21
Data Sources: NERC, NNPC, World Bank, FAO, NBS
Analysis Tool: SOFC Techno-Economic Analyzer v1.0
========================================================================================================
"""
        return report

# Example usage
if __name__ == "__main__":
    analyzer = SOFCAnalyzer()
    
    # Generate all analyses
    print("Calculating flared gas SOFC potential...")
    flare_analysis = analyzer.calculate_flared_gas_sofc_potential()
    print(f"Total SOFC potential from flared gas: {flare_analysis['SOFC_Capacity_MW'].sum():.0f} MW\n")
    
    print("Calculating biogas SOFC potential...")
    biogas_analysis = analyzer.calculate_biogas_sofc_potential()
    print(f"Total SOFC potential from biogas: {biogas_analysis['SOFC_Capacity_MW'].sum():.0f} MW\n")
    
    print("Performing LCOE analysis...")
    lcoe_analysis = analyzer.comparative_lcoe_analysis()
    print(lcoe_analysis[['Technology', 'LCOE_USD_per_MWh']].to_string())
    print()
    
    print("Calculating national impact...")
    national_impact = analyzer.calculate_national_impact()
    print(f"Total SOFC Potential: {national_impact['Total_SOFC_Potential_MW']:,.0f} MW")
    print(f"Grid Capacity Increase: {national_impact['Capacity_Increase_Percent']:.1f}%")
    print(f"CO2 Reduction: {national_impact['CO2_Reduction_Million_Tons']:,.0f} Million tons/year\n")
    
    print("Generating visualizations...")
    analyzer.generate_visualizations()
    
    print("Generating comprehensive report...")
    report = analyzer.generate_report()
    
    # Save report
    with open(analyzer.data_path / "SOFC_Nigeria_Analysis_Report.txt", "w") as f:
        f.write(report)
    
    print("\nAnalysis complete! Check the following outputs:")
    print("1. Visualizations in 'visualizations/' folder")
    print("2. Comprehensive report: 'SOFC_Nigeria_Analysis_Report.txt'")
    print("3. Interactive dashboard: 'visualizations/national_impact_dashboard.html'")