#!/usr/bin/env python3
"""
Comprehensive Nigerian Energy & Resource Dataset Creator
Integrates all generated data into a unified dataset for SOFC analysis
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_all_datasets():
    """Load all generated datasets"""
    
    datasets = {}
    
    # Electricity data
    datasets['electricity_capacity'] = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/electricity_generation_capacity.csv')
    datasets['electricity_load'] = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/electricity_daily_load_allocation.csv')
    datasets['electricity_reliability'] = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/electricity_reliability_metrics.csv')
    datasets['electricity_tariffs'] = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/electricity_tariffs.csv')
    
    # Fossil fuel data
    datasets['gas_reserves'] = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/natural_gas_reserves_production.csv')
    datasets['gas_flaring'] = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/gas_flaring_data.csv')
    datasets['gas_pipelines'] = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/gas_pipeline_network.csv')
    datasets['fuel_prices'] = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/fuel_prices_by_state.csv')
    
    # Renewable resource data
    datasets['agricultural_waste'] = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/agricultural_waste_data.csv')
    datasets['livestock'] = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/livestock_population_data.csv')
    datasets['biomass_summary'] = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/biomass_potential_summary.csv')
    
    return datasets

def create_sofc_analysis_dataset():
    """Create a dataset specifically optimized for SOFC analysis"""
    
    datasets = load_all_datasets()
    
    # Create SOFC-specific analysis dataset
    sofc_data = []
    
    # Get latest year data (2024)
    latest_year = 2024
    
    # Electricity grid analysis
    electricity_capacity_2024 = datasets['electricity_capacity'][datasets['electricity_capacity']['year'] == latest_year].iloc[0]
    electricity_load_2024 = datasets['electricity_load'][datasets['electricity_load']['date'].str.contains('2024')]
    electricity_reliability_2024 = datasets['electricity_reliability'][datasets['electricity_reliability']['year'] == latest_year]
    electricity_tariffs_2024 = datasets['electricity_tariffs'][datasets['electricity_tariffs']['year'] == latest_year].iloc[0]
    
    # Gas data
    gas_reserves_2024 = datasets['gas_reserves'][datasets['gas_reserves']['year'] == latest_year].iloc[0]
    gas_flaring_2024 = datasets['gas_flaring'][datasets['gas_flaring']['year'] == latest_year]
    fuel_prices_2024 = datasets['fuel_prices'][datasets['fuel_prices']['year'] == latest_year]
    
    # Biomass data
    biomass_2024 = datasets['biomass_summary'][datasets['biomass_summary']['year'] == latest_year]
    
    # Create comprehensive SOFC analysis record
    sofc_record = {
        'analysis_year': latest_year,
        'date_created': datetime.now().strftime('%Y-%m-%d'),
        
        # Electricity Grid Context
        'total_installed_capacity_mw': electricity_capacity_2024['total_installed_capacity'],
        'total_available_capacity_mw': electricity_capacity_2024['total_available_capacity'],
        'gas_installed_capacity_mw': electricity_capacity_2024['gas_installed_capacity'],
        'gas_available_capacity_mw': electricity_capacity_2024['gas_available_capacity'],
        'gas_capacity_factor': electricity_capacity_2024['gas_capacity_factor'],
        'average_daily_demand_mw': electricity_load_2024['total_demand_mw'].mean(),
        'average_daily_supply_mw': electricity_load_2024['available_supply_mw'].mean(),
        'average_load_shedding_mw': electricity_load_2024['load_shedding_mw'].mean(),
        'supply_reliability_percent': (electricity_load_2024['available_supply_mw'].mean() / electricity_load_2024['total_demand_mw'].mean()) * 100,
        'average_saidi_hours': electricity_reliability_2024['saidi_hours_per_year'].mean(),
        'average_saifi_interruptions': electricity_reliability_2024['saifi_interruptions_per_year'].mean(),
        'average_availability_percent': electricity_reliability_2024['availability_percent'].mean(),
        'residential_tariff_naira_per_kwh': electricity_tariffs_2024['r4_tariff_naira_per_kwh'],
        'commercial_tariff_naira_per_kwh': electricity_tariffs_2024['c3_tariff_naira_per_kwh'],
        'industrial_tariff_naira_per_kwh': electricity_tariffs_2024['d3_tariff_naira_per_kwh'],
        
        # Natural Gas Context
        'proven_gas_reserves_tcf': gas_reserves_2024['proven_reserves_tcf'],
        'daily_gas_production_mmscf': gas_reserves_2024['daily_production_mmscf'],
        'annual_gas_production_mmscf': gas_reserves_2024['annual_production_mmscf'],
        'gas_for_power_mmscf_per_day': gas_reserves_2024['power_generation_mmscf_per_day'],
        'gas_flaring_mmscf_per_day': gas_reserves_2024['flared_mmscf_per_day'],
        'gas_flaring_percentage': (gas_reserves_2024['flared_mmscf_per_day'] / gas_reserves_2024['daily_production_mmscf']) * 100,
        'total_flaring_sites': len(gas_flaring_2024),
        'total_flaring_annual_mmscf': gas_flaring_2024['annual_flaring_mmscf'].sum(),
        'total_co2_emissions_tonnes': gas_flaring_2024['co2_emissions_tonnes'].sum(),
        'economic_value_lost_usd_millions': gas_flaring_2024['economic_value_lost_usd_millions'].sum(),
        
        # Pipeline Infrastructure
        'total_pipelines': len(datasets['gas_pipelines']),
        'operational_pipelines': len(datasets['gas_pipelines'][datasets['gas_pipelines']['status'] == 'Operational']),
        'total_pipeline_length_km': datasets['gas_pipelines']['length_km'].sum(),
        'total_pipeline_capacity_mmscf_per_day': datasets['gas_pipelines']['capacity_mmscf_per_day'].sum(),
        
        # Fuel Prices
        'average_petrol_price_naira_per_liter': fuel_prices_2024['petrol_price_naira_per_liter'].mean(),
        'average_diesel_price_naira_per_liter': fuel_prices_2024['diesel_price_naira_per_liter'].mean(),
        'price_difference_naira_per_liter': fuel_prices_2024['price_difference_naira'].mean(),
        
        # Biomass Potential
        'total_biomass_energy_potential_twh': biomass_2024['total_energy_potential_twh'].sum(),
        'total_biomass_electricity_potential_mwh': biomass_2024['total_electricity_potential_mwh'].sum(),
        'total_biomass_biogas_potential_million_m3': biomass_2024['total_biogas_potential_m3'].sum() / 1000000,
        
        # SOFC-Specific Analysis Metrics
        'sofc_gas_availability_mmscf_per_day': gas_reserves_2024['daily_production_mmscf'] * 0.4,  # 40% for SOFC
        'sofc_power_potential_mw': gas_reserves_2024['daily_production_mmscf'] * 0.4 * 0.5,  # 0.5 MW per MMscf/day
        'sofc_efficiency_estimate_percent': 60,  # Typical SOFC efficiency
        'sofc_capital_cost_per_mw_usd': 3000000,  # Estimated SOFC cost
        'sofc_operating_cost_per_mwh_usd': 50,  # Estimated operating cost
        'sofc_lifetime_years': 20,  # Typical SOFC lifetime
        
        # Economic Analysis
        'electricity_deficit_mw': electricity_load_2024['total_demand_mw'].mean() - electricity_load_2024['available_supply_mw'].mean(),
        'deficit_percentage': ((electricity_load_2024['total_demand_mw'].mean() - electricity_load_2024['available_supply_mw'].mean()) / electricity_load_2024['total_demand_mw'].mean()) * 100,
        'sofc_potential_deficit_reduction_percent': min(100, (gas_reserves_2024['daily_production_mmscf'] * 0.4 * 0.5) / (electricity_load_2024['total_demand_mw'].mean() - electricity_load_2024['available_supply_mw'].mean()) * 100),
        
        # Environmental Impact
        'co2_reduction_potential_tonnes_per_year': gas_flaring_2024['co2_emissions_tonnes'].sum() * 0.8,  # 80% reduction potential
        'flaring_reduction_potential_percent': 80,
        'renewable_integration_potential_percent': 15  # 15% from biomass
    }
    
    return pd.DataFrame([sofc_record])

def create_regional_analysis_dataset():
    """Create regional analysis dataset for SOFC deployment"""
    
    datasets = load_all_datasets()
    
    # Get 2024 data
    latest_year = 2024
    
    # Electricity reliability by region
    reliability_2024 = datasets['electricity_reliability'][datasets['electricity_reliability']['year'] == latest_year]
    
    # Fuel prices by state
    fuel_prices_2024 = datasets['fuel_prices'][datasets['fuel_prices']['year'] == latest_year]
    
    # Biomass potential by state
    biomass_2024 = datasets['biomass_summary'][datasets['biomass_summary']['year'] == latest_year]
    
    # Gas flaring by state
    flaring_2024 = datasets['gas_flaring'][datasets['gas_flaring']['year'] == latest_year]
    flaring_by_state = flaring_2024.groupby('state').agg({
        'daily_flaring_mmscf': 'sum',
        'annual_flaring_mmscf': 'sum',
        'co2_emissions_tonnes': 'sum',
        'economic_value_lost_usd_millions': 'sum'
    }).reset_index()
    
    # Merge all regional data
    regional_data = []
    
    for state in reliability_2024['region'].unique():
        state_reliability = reliability_2024[reliability_2024['region'] == state].iloc[0]
        state_fuel_prices = fuel_prices_2024[fuel_prices_2024['state'] == state]
        state_biomass = biomass_2024[biomass_2024['state'] == state]
        state_flaring = flaring_by_state[flaring_by_state['state'] == state]
        
        if len(state_fuel_prices) > 0 and len(state_biomass) > 0:
            regional_record = {
                'state': state,
                'year': latest_year,
                
                # Electricity reliability
                'saidi_hours_per_year': state_reliability['saidi_hours_per_year'],
                'saifi_interruptions_per_year': state_reliability['saifi_interruptions_per_year'],
                'availability_percent': state_reliability['availability_percent'],
                'customer_base_thousands': state_reliability['customer_base_thousands'],
                
                # Fuel prices
                'avg_petrol_price_naira_per_liter': state_fuel_prices['petrol_price_naira_per_liter'].mean(),
                'avg_diesel_price_naira_per_liter': state_fuel_prices['diesel_price_naira_per_liter'].mean(),
                
                # Biomass potential
                'biomass_energy_potential_twh': state_biomass['total_energy_potential_twh'].iloc[0] if len(state_biomass) > 0 else 0,
                'biomass_electricity_potential_mwh': state_biomass['total_electricity_potential_mwh'].iloc[0] if len(state_biomass) > 0 else 0,
                
                # Gas flaring
                'daily_flaring_mmscf': state_flaring['daily_flaring_mmscf'].iloc[0] if len(state_flaring) > 0 else 0,
                'annual_flaring_mmscf': state_flaring['annual_flaring_mmscf'].iloc[0] if len(state_flaring) > 0 else 0,
                'co2_emissions_tonnes': state_flaring['co2_emissions_tonnes'].iloc[0] if len(state_flaring) > 0 else 0,
                'economic_value_lost_usd_millions': state_flaring['economic_value_lost_usd_millions'].iloc[0] if len(state_flaring) > 0 else 0,
                
                # SOFC deployment potential
                'sofc_priority_score': 0,  # Will be calculated
                'sofc_gas_availability_mmscf_per_day': state_flaring['daily_flaring_mmscf'].iloc[0] if len(state_flaring) > 0 else 0,
                'sofc_power_potential_mw': (state_flaring['daily_flaring_mmscf'].iloc[0] if len(state_flaring) > 0 else 0) * 0.5,
                'sofc_economic_viability_score': 0  # Will be calculated
            }
            
            # Calculate SOFC priority score (higher is better)
            priority_factors = []
            if state_reliability['availability_percent'] < 70:  # Poor reliability
                priority_factors.append(3)
            elif state_reliability['availability_percent'] < 85:  # Moderate reliability
                priority_factors.append(2)
            else:  # Good reliability
                priority_factors.append(1)
            
            if state_flaring['daily_flaring_mmscf'].iloc[0] if len(state_flaring) > 0 else 0 > 10:  # High flaring
                priority_factors.append(3)
            elif state_flaring['daily_flaring_mmscf'].iloc[0] if len(state_flaring) > 0 else 0 > 5:  # Moderate flaring
                priority_factors.append(2)
            else:  # Low flaring
                priority_factors.append(1)
            
            if state_biomass['total_energy_potential_twh'].iloc[0] if len(state_biomass) > 0 else 0 > 0.1:  # Good biomass potential
                priority_factors.append(2)
            else:
                priority_factors.append(1)
            
            regional_record['sofc_priority_score'] = sum(priority_factors)
            
            # Calculate economic viability score
            if state_fuel_prices['petrol_price_naira_per_liter'].mean() > 200:  # High fuel prices
                regional_record['sofc_economic_viability_score'] = 3
            elif state_fuel_prices['petrol_price_naira_per_liter'].mean() > 150:  # Moderate fuel prices
                regional_record['sofc_economic_viability_score'] = 2
            else:  # Low fuel prices
                regional_record['sofc_economic_viability_score'] = 1
            
            regional_data.append(regional_record)
    
    return pd.DataFrame(regional_data)

def create_time_series_dataset():
    """Create time series dataset for trend analysis"""
    
    datasets = load_all_datasets()
    
    # Create monthly time series data
    time_series_data = []
    
    for year in range(2020, 2025):
        for month in range(1, 13):
            # Electricity data
            electricity_capacity = datasets['electricity_capacity'][datasets['electricity_capacity']['year'] == year]
            electricity_tariffs = datasets['electricity_tariffs'][datasets['electricity_tariffs']['year'] == year]
            
            # Gas data
            gas_reserves = datasets['gas_reserves'][datasets['gas_reserves']['year'] == year]
            gas_flaring = datasets['gas_flaring'][datasets['gas_flaring']['year'] == year]
            
            # Fuel prices (average for the year)
            fuel_prices = datasets['fuel_prices'][datasets['fuel_prices']['year'] == year]
            
            if len(electricity_capacity) > 0 and len(gas_reserves) > 0:
                time_series_record = {
                    'year': year,
                    'month': month,
                    'date': f"{year}-{month:02d}-01",
                    
                    # Electricity trends
                    'total_installed_capacity_mw': electricity_capacity.iloc[0]['total_installed_capacity'],
                    'total_available_capacity_mw': electricity_capacity.iloc[0]['total_available_capacity'],
                    'gas_capacity_mw': electricity_capacity.iloc[0]['gas_installed_capacity'],
                    'gas_capacity_factor': electricity_capacity.iloc[0]['gas_capacity_factor'],
                    'residential_tariff_naira_per_kwh': electricity_tariffs.iloc[0]['r4_tariff_naira_per_kwh'],
                    
                    # Gas trends
                    'proven_gas_reserves_tcf': gas_reserves.iloc[0]['proven_reserves_tcf'],
                    'daily_gas_production_mmscf': gas_reserves.iloc[0]['daily_production_mmscf'],
                    'daily_gas_flaring_mmscf': gas_flaring['daily_flaring_mmscf'].sum(),
                    'flaring_percentage': (gas_flaring['daily_flaring_mmscf'].sum() / gas_reserves.iloc[0]['daily_production_mmscf']) * 100,
                    
                    # Fuel price trends
                    'avg_petrol_price_naira_per_liter': fuel_prices['petrol_price_naira_per_liter'].mean(),
                    'avg_diesel_price_naira_per_liter': fuel_prices['diesel_price_naira_per_liter'].mean(),
                    
                    # SOFC potential trends
                    'sofc_gas_availability_mmscf_per_day': gas_reserves.iloc[0]['daily_production_mmscf'] * 0.4,
                    'sofc_power_potential_mw': gas_reserves.iloc[0]['daily_production_mmscf'] * 0.4 * 0.5,
                    'sofc_economic_viability_index': (fuel_prices['petrol_price_naira_per_liter'].mean() / 100) * (gas_flaring['daily_flaring_mmscf'].sum() / 100)
                }
                
                time_series_data.append(time_series_record)
    
    return pd.DataFrame(time_series_data)

def main():
    """Create comprehensive datasets for SOFC analysis"""
    
    print("Creating comprehensive Nigerian Energy & Resource datasets...")
    
    # Create all datasets
    sofc_analysis_df = create_sofc_analysis_dataset()
    regional_analysis_df = create_regional_analysis_dataset()
    time_series_df = create_time_series_dataset()
    
    # Save datasets
    sofc_analysis_df.to_csv('/workspace/nigerian_energy_dataset/processed_data/sofc_analysis_dataset.csv', index=False)
    regional_analysis_df.to_csv('/workspace/nigerian_energy_dataset/processed_data/regional_sofc_analysis.csv', index=False)
    time_series_df.to_csv('/workspace/nigerian_energy_dataset/processed_data/energy_trends_time_series.csv', index=False)
    
    # Create summary statistics
    summary = {
        'dataset_overview': {
            'total_datasets_created': 3,
            'sofc_analysis_records': len(sofc_analysis_df),
            'regional_analysis_records': len(regional_analysis_df),
            'time_series_records': len(time_series_df),
            'creation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'sofc_analysis_highlights': {
            'total_installed_capacity_mw': float(sofc_analysis_df.iloc[0]['total_installed_capacity_mw']),
            'electricity_deficit_mw': float(sofc_analysis_df.iloc[0]['electricity_deficit_mw']),
            'sofc_power_potential_mw': float(sofc_analysis_df.iloc[0]['sofc_power_potential_mw']),
            'sofc_deficit_reduction_percent': float(sofc_analysis_df.iloc[0]['sofc_potential_deficit_reduction_percent']),
            'gas_flaring_percentage': float(sofc_analysis_df.iloc[0]['gas_flaring_percentage']),
            'co2_reduction_potential_tonnes_per_year': float(sofc_analysis_df.iloc[0]['co2_reduction_potential_tonnes_per_year'])
        },
        'top_sofc_priority_states': {
            'top_5_states': regional_analysis_df.nlargest(5, 'sofc_priority_score')[['state', 'sofc_priority_score', 'sofc_power_potential_mw']].to_dict('records')
        }
    }
    
    # Save summary
    with open('/workspace/nigerian_energy_dataset/processed_data/comprehensive_dataset_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("Comprehensive dataset creation completed!")
    print(f"Created SOFC analysis dataset with {len(sofc_analysis_df)} records")
    print(f"Created regional analysis dataset with {len(regional_analysis_df)} records")
    print(f"Created time series dataset with {len(time_series_df)} records")
    
    return sofc_analysis_df, regional_analysis_df, time_series_df

if __name__ == "__main__":
    main()