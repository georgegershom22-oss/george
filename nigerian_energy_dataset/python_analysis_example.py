#!/usr/bin/env python3
"""
Nigerian Energy Dataset - Analysis Examples
============================================

This script demonstrates how to load and analyze the Nigerian Energy & Resource Dataset
for SOFC (Solid Oxide Fuel Cell) deployment analysis.

Requirements:
    pip install pandas matplotlib seaborn numpy

Author: Dataset Compiler
Date: October 21, 2024
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# Dataset base path
BASE_PATH = Path(__file__).parent


def load_dataset():
    """Load all key datasets into a dictionary."""
    datasets = {
        'generation': pd.read_csv(BASE_PATH / 'electricity_grid/national_generation_capacity.csv'),
        'reliability': pd.read_csv(BASE_PATH / 'electricity_grid/grid_reliability_metrics.csv'),
        'tariffs': pd.read_csv(BASE_PATH / 'electricity_grid/electricity_tariffs_2024.csv'),
        'daily_load': pd.read_csv(BASE_PATH / 'electricity_grid/daily_load_allocation_2024.csv'),
        'gas_reserves': pd.read_csv(BASE_PATH / 'fossil_fuels/gas_reserves_and_production.csv'),
        'gas_flaring': pd.read_csv(BASE_PATH / 'fossil_fuels/gas_flaring_by_location_2024.csv'),
        'pipelines': pd.read_csv(BASE_PATH / 'fossil_fuels/gas_pipeline_infrastructure.csv'),
        'fuel_prices': pd.read_csv(BASE_PATH / 'fossil_fuels/diesel_petrol_prices_by_state.csv'),
        'ag_waste': pd.read_csv(BASE_PATH / 'renewable_resources/agricultural_waste_by_state.csv'),
        'livestock': pd.read_csv(BASE_PATH / 'renewable_resources/livestock_population_by_state.csv'),
        'gas_fields': pd.read_csv(BASE_PATH / 'geospatial/gas_field_coordinates.csv'),
        'sofc_potential': pd.read_csv(BASE_PATH / 'analysis/sofc_deployment_potential.csv'),
        'tech_comparison': pd.read_csv(BASE_PATH / 'analysis/energy_economics_comparison.csv'),
    }
    print("✅ All datasets loaded successfully!")
    print(f"📊 Total datasets: {len(datasets)}")
    for name, df in datasets.items():
        print(f"   - {name}: {len(df)} rows, {len(df.columns)} columns")
    return datasets


def analyze_generation_capacity(data):
    """Analyze power generation capacity by source."""
    print("\n" + "="*70)
    print("POWER GENERATION CAPACITY ANALYSIS")
    print("="*70)
    
    df = data['generation']
    
    # Total capacity by source
    capacity_by_source = df.groupby('Source_Type').agg({
        'Installed_Capacity_MW': 'sum',
        'Available_Capacity_MW': 'sum'
    }).round(2)
    
    print("\n📊 Generation Capacity by Source Type:")
    print(capacity_by_source)
    
    # Capacity utilization
    total_installed = df['Installed_Capacity_MW'].sum()
    total_available = df['Available_Capacity_MW'].sum()
    utilization = (total_available / total_installed * 100)
    
    print(f"\n⚡ Total Installed Capacity: {total_installed:,.1f} MW")
    print(f"⚡ Total Available Capacity: {total_available:,.1f} MW")
    print(f"⚡ Capacity Utilization: {utilization:.1f}%")
    
    # Top 10 power plants
    print("\n🏭 Top 10 Power Plants by Available Capacity:")
    top_plants = df.nlargest(10, 'Available_Capacity_MW')[
        ['Power_Plant', 'State', 'Source_Type', 'Available_Capacity_MW', 'Efficiency_Percent']
    ]
    print(top_plants.to_string(index=False))
    
    return capacity_by_source


def analyze_grid_reliability(data):
    """Analyze grid reliability metrics by region."""
    print("\n" + "="*70)
    print("GRID RELIABILITY ANALYSIS")
    print("="*70)
    
    df = data['reliability']
    
    # Regional statistics
    regional_stats = df.groupby('Region').agg({
        'SAIDI_Hours': 'mean',
        'SAIFI_Events': 'mean',
        'Average_Outage_Duration_Hours': 'mean',
        'Grid_Coverage_Percent': 'mean',
        'Backup_Generator_Penetration_Percent': 'mean'
    }).round(1)
    
    print("\n📉 Grid Reliability by Region:")
    print(regional_stats)
    
    # Worst performing states
    print("\n⚠️  Top 10 States with Highest Outage Hours (SAIDI):")
    worst_states = df.nlargest(10, 'SAIDI_Hours')[
        ['State', 'Region', 'SAIDI_Hours', 'Grid_Coverage_Percent']
    ]
    print(worst_states.to_string(index=False))
    
    # National average
    print(f"\n🇳🇬 National Average Outage Hours: {df['SAIDI_Hours'].mean():,.0f} hours/year")
    print(f"   (That's {df['SAIDI_Hours'].mean()/24:.1f} days or {df['SAIDI_Hours'].mean()/8760*100:.1f}% of the year!)")
    
    return regional_stats


def analyze_gas_flaring(data):
    """Analyze gas flaring data and SOFC potential."""
    print("\n" + "="*70)
    print("GAS FLARING ANALYSIS")
    print("="*70)
    
    df = data['gas_flaring']
    
    # Total flaring
    total_daily_flare = df['Daily_Flare_Volume_mscf'].sum()
    total_annual_flare = df['Annual_Flare_Volume_Bcf'].sum()
    total_co2 = df['Emissions_CO2_tonnes_per_year'].sum()
    total_population_affected = df['Population_Within_5km'].sum()
    
    print(f"\n🔥 Total Daily Flaring: {total_daily_flare:,.1f} million scf/day")
    print(f"🔥 Total Annual Flaring: {total_annual_flare:,.1f} Bcf/year")
    print(f"☁️  Total CO2 Emissions: {total_co2:,.0f} tonnes/year ({total_co2/1e6:.2f} million tonnes)")
    print(f"👥 Population Affected (5km radius): {total_population_affected:,} people")
    
    # SOFC potential from flare gas
    # Assumption: 1 mscf/day = ~1 kW SOFC capacity
    sofc_potential_mw = total_daily_flare / 1000
    print(f"\n⚡ SOFC Potential from Flare Gas: {sofc_potential_mw:,.0f} MW")
    print(f"💰 Investment Required (@$1,400/kW): ${sofc_potential_mw * 1.4:,.0f} million")
    
    # Top flaring sites
    print("\n🔥 Top 10 Gas Flaring Sites:")
    top_flares = df.nlargest(10, 'Daily_Flare_Volume_mscf')[
        ['Location_Name', 'State', 'Operator', 'Daily_Flare_Volume_mscf', 'Emissions_CO2_tonnes_per_year']
    ]
    print(top_flares.to_string(index=False))
    
    # Flaring by state
    state_flaring = df.groupby('State').agg({
        'Daily_Flare_Volume_mscf': 'sum',
        'Emissions_CO2_tonnes_per_year': 'sum'
    }).sort_values('Daily_Flare_Volume_mscf', ascending=False)
    
    print("\n🗺️  Flaring by State:")
    print(state_flaring)
    
    return df


def analyze_sofc_potential(data):
    """Analyze SOFC deployment potential by state and tier."""
    print("\n" + "="*70)
    print("SOFC DEPLOYMENT POTENTIAL ANALYSIS")
    print("="*70)
    
    df = data['sofc_potential']
    
    # Tier summary
    tier_summary = df.groupby('SOFC_Priority_Tier').agg({
        'State': 'count',
        'Estimated_SOFC_Capacity_Potential_MW': 'sum',
        'Estimated_Investment_Million_USD': 'sum',
        'Payback_Period_Years': 'mean'
    }).round(1)
    tier_summary.columns = ['Number_of_States', 'Total_MW', 'Investment_M_USD', 'Avg_Payback_Years']
    
    print("\n🎯 SOFC Deployment Potential by Priority Tier:")
    print(tier_summary)
    
    # Top 10 states
    print("\n🏆 Top 10 States for SOFC Deployment:")
    top_states = df.nlargest(10, 'Estimated_SOFC_Capacity_Potential_MW')[
        ['State', 'Region', 'Estimated_SOFC_Capacity_Potential_MW', 
         'Payback_Period_Years', 'SOFC_Priority_Tier', 'Gas_Pipeline_Access']
    ]
    print(top_states.to_string(index=False))
    
    # Tier 1 focus
    tier1 = df[df['SOFC_Priority_Tier'] == 'Tier_1_Critical']
    print(f"\n⭐ Tier 1 (Critical Priority) States:")
    print(f"   - Number of states: {len(tier1)}")
    print(f"   - Total capacity: {tier1['Estimated_SOFC_Capacity_Potential_MW'].sum():,.0f} MW")
    print(f"   - Investment required: ${tier1['Estimated_Investment_Million_USD'].sum():,.0f} million")
    print(f"   - Average payback: {tier1['Payback_Period_Years'].mean():.1f} years")
    
    return tier_summary


def compare_technologies(data):
    """Compare SOFC with alternative technologies."""
    print("\n" + "="*70)
    print("TECHNOLOGY COMPARISON ANALYSIS")
    print("="*70)
    
    df = data['tech_comparison']
    
    # Key technologies
    key_techs = [
        'SOFC_Natural_Gas', 'SOFC_Biogas', 'SOFC_Flare_Gas',
        'CCGT_Natural_Gas', 'Grid_Diesel', 'Off_Grid_Diesel',
        'Solar_PV_Utility', 'Wind_Onshore'
    ]
    
    comparison = df[df['Technology'].isin(key_techs)][
        ['Technology', 'LCOE_USD_per_MWh', 'Efficiency_Percent', 
         'Emissions_CO2_kg_per_MWh', 'Lifespan_Years']
    ].sort_values('LCOE_USD_per_MWh')
    
    print("\n💰 Technology Comparison (sorted by LCOE):")
    print(comparison.to_string(index=False))
    
    # SOFC advantages
    sofc_avg_lcoe = df[df['Technology'].str.startswith('SOFC')]['LCOE_USD_per_MWh'].mean()
    diesel_avg_lcoe = df[df['Technology'].str.contains('Diesel')]['LCOE_USD_per_MWh'].mean()
    cost_savings = (diesel_avg_lcoe - sofc_avg_lcoe) / diesel_avg_lcoe * 100
    
    print(f"\n💡 Key Insights:")
    print(f"   - SOFC Average LCOE: ${sofc_avg_lcoe:.0f}/MWh")
    print(f"   - Diesel Average LCOE: ${diesel_avg_lcoe:.0f}/MWh")
    print(f"   - SOFC Cost Savings vs Diesel: {cost_savings:.0f}%")
    
    sofc_efficiency = df[df['Technology'].str.startswith('SOFC')]['Efficiency_Percent'].mean()
    print(f"   - SOFC Average Efficiency: {sofc_efficiency:.0f}% (highest thermal technology)")
    
    return comparison


def calculate_market_size(data):
    """Calculate total addressable market for SOFC in Nigeria."""
    print("\n" + "="*70)
    print("MARKET SIZE CALCULATION")
    print("="*70)
    
    reliability = data['reliability']
    sofc_potential = data['sofc_potential']
    
    # Total addressable market
    total_demand_deficit = sofc_potential['Peak_Demand_Deficit_MW'].sum()
    total_sofc_potential = sofc_potential['Estimated_SOFC_Capacity_Potential_MW'].sum()
    total_investment = sofc_potential['Estimated_Investment_Million_USD'].sum()
    
    print(f"\n📈 Total Addressable Market:")
    print(f"   - Peak Demand Deficit (all states): {total_demand_deficit:,.0f} MW")
    print(f"   - SOFC Deployment Potential: {total_sofc_potential:,.0f} MW")
    print(f"   - Required Investment: ${total_investment:,.0f} million (${total_investment/1000:.2f} billion)")
    
    # Market segments
    print(f"\n🎯 Key Market Segments:")
    print(f"   - Industrial Off-Grid: Estimated 1,800 MW")
    print(f"   - Commercial Backup Power: Estimated 1,200 MW")
    print(f"   - Telecom Towers: Estimated 450 MW")
    print(f"   - Flare Gas Capture: Estimated 750 MW")
    print(f"   - Agricultural Biogas: Estimated 800 MW")
    
    # Grid-connected customers
    total_customers = reliability['Total_Customers'].sum()
    avg_coverage = reliability['Grid_Coverage_Percent'].mean()
    
    print(f"\n👥 Customer Base:")
    print(f"   - Grid-connected customers: {total_customers:,}")
    print(f"   - Average grid coverage: {avg_coverage:.1f}%")
    print(f"   - Off-grid population: ~85 million (40% of 210M population)")
    
    return {
        'total_potential_mw': total_sofc_potential,
        'total_investment_musd': total_investment,
        'total_customers': total_customers
    }


def generate_summary_report(data):
    """Generate a comprehensive summary report."""
    print("\n" + "="*70)
    print("COMPREHENSIVE SUMMARY REPORT")
    print("="*70)
    
    print("\n🇳🇬 NIGERIAN ENERGY & SOFC DEPLOYMENT DATASET")
    print("   Version: 1.0")
    print("   Date: October 21, 2024")
    
    # Key statistics
    gen = data['generation']
    reliability = data['reliability']
    gas_reserves = data['gas_reserves']
    flaring = data['gas_flaring']
    sofc = data['sofc_potential']
    
    print("\n" + "-"*70)
    print("KEY STATISTICS")
    print("-"*70)
    
    print("\n⚡ ELECTRICITY GENERATION:")
    print(f"   - Installed Capacity: {gen['Installed_Capacity_MW'].sum():,.0f} MW")
    print(f"   - Available Capacity: {gen['Available_Capacity_MW'].sum():,.0f} MW")
    print(f"   - Capacity Utilization: {gen['Available_Capacity_MW'].sum()/gen['Installed_Capacity_MW'].sum()*100:.1f}%")
    
    print("\n📉 GRID RELIABILITY:")
    print(f"   - Average Outage Hours: {reliability['SAIDI_Hours'].mean():,.0f} hours/year")
    print(f"   - Average Grid Coverage: {reliability['Grid_Coverage_Percent'].mean():.1f}%")
    print(f"   - Generator Penetration: {reliability['Backup_Generator_Penetration_Percent'].mean():.1f}%")
    
    print("\n⛽ GAS RESOURCES (2024):")
    latest_gas = gas_reserves.iloc[-1]
    print(f"   - Proven Reserves: {latest_gas['Proven_Gas_Reserves_Tcf']:.1f} Tcf")
    print(f"   - Annual Production: {latest_gas['Total_Gas_Production_Bcf_per_Year']:.1f} Bcf/year")
    print(f"   - Gas Flared: {latest_gas['Gas_Flared_Bcf_per_Year']:.1f} Bcf/year ({latest_gas['Gas_Flared_Bcf_per_Year']/latest_gas['Total_Gas_Production_Bcf_per_Year']*100:.1f}%)")
    print(f"   - Domestic Supply: {latest_gas['Domestic_Gas_Supply_Bcf_per_Year']:.1f} Bcf/year")
    
    print("\n🔥 GAS FLARING:")
    print(f"   - Total Flare Sites: {len(flaring)}")
    print(f"   - Daily Flaring: {flaring['Daily_Flare_Volume_mscf'].sum():,.0f} mscf/day")
    print(f"   - Annual CO2 Emissions: {flaring['Emissions_CO2_tonnes_per_year'].sum()/1e6:.2f} million tonnes")
    print(f"   - Population Affected: {flaring['Population_Within_5km'].sum():,} people")
    
    print("\n💡 SOFC DEPLOYMENT POTENTIAL:")
    print(f"   - Total Potential: {sofc['Estimated_SOFC_Capacity_Potential_MW'].sum():,.0f} MW")
    print(f"   - Investment Required: ${sofc['Estimated_Investment_Million_USD'].sum():,.0f} million")
    print(f"   - Average Payback (All States): {sofc['Payback_Period_Years'].mean():.1f} years")
    
    tier1 = sofc[sofc['SOFC_Priority_Tier'] == 'Tier_1_Critical']
    print(f"   - Tier 1 States: {len(tier1)} states, {tier1['Estimated_SOFC_Capacity_Potential_MW'].sum():,.0f} MW")
    print(f"   - Tier 1 Payback: {tier1['Payback_Period_Years'].mean():.1f} years")
    
    print("\n" + "="*70)
    print("✅ Analysis Complete!")
    print("="*70)


def main():
    """Main analysis function."""
    print("\n" + "="*70)
    print("NIGERIAN ENERGY & RESOURCE DATASET")
    print("SOFC Deployment Analysis")
    print("="*70)
    
    # Load all datasets
    data = load_dataset()
    
    # Run analyses
    analyze_generation_capacity(data)
    analyze_grid_reliability(data)
    analyze_gas_flaring(data)
    analyze_sofc_potential(data)
    compare_technologies(data)
    calculate_market_size(data)
    
    # Generate summary
    generate_summary_report(data)
    
    print("\n💡 Next Steps:")
    print("   1. Use pandas/matplotlib to create visualizations")
    print("   2. Perform detailed state-by-state analysis")
    print("   3. Build financial models using LCOE data")
    print("   4. Map gas infrastructure and deployment potential")
    print("   5. Develop policy recommendations")
    
    print("\n📚 For more information, see:")
    print("   - README.md: Comprehensive documentation")
    print("   - DATA_DICTIONARY.md: Field definitions and units")
    print("   - SUMMARY_STATISTICS.md: Key statistics and insights")
    print("   - QUICK_START.md: Quick reference guide")


if __name__ == "__main__":
    main()
