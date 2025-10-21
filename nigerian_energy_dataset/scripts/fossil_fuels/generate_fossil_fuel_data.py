#!/usr/bin/env python3
"""
Nigerian Fossil Fuel Data Generator
Generates comprehensive fossil fuel datasets including gas reserves, production, flaring, and pricing data
Critical for SOFC feasibility analysis in Nigeria
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

# Set random seed for reproducibility
np.random.seed(42)

def generate_gas_reserves_production_data():
    """Generate natural gas reserves and production data"""
    
    # Major Nigerian gas fields and their characteristics
    gas_fields = {
        'Niger Delta': {
            'proven_reserves_tcf': 120.0,
            'probable_reserves_tcf': 80.0,
            'daily_production_mmscf': 2500,
            'associated_gas_ratio': 0.7,  # 70% associated with oil
            'gas_quality': 'sweet',  # Low sulfur content
            'location': {'lat': 5.5, 'lon': 6.0}
        },
        'Offshore Deep Water': {
            'proven_reserves_tcf': 85.0,
            'probable_reserves_tcf': 120.0,
            'daily_production_mmscf': 1800,
            'associated_gas_ratio': 0.4,
            'gas_quality': 'sweet',
            'location': {'lat': 4.0, 'lon': 5.5}
        },
        'Anambra Basin': {
            'proven_reserves_tcf': 15.0,
            'probable_reserves_tcf': 25.0,
            'daily_production_mmscf': 300,
            'associated_gas_ratio': 0.2,
            'gas_quality': 'sour',  # Higher sulfur content
            'location': {'lat': 6.2, 'lon': 7.1}
        },
        'Chad Basin': {
            'proven_reserves_tcf': 8.0,
            'probable_reserves_tcf': 15.0,
            'daily_production_mmscf': 150,
            'associated_gas_ratio': 0.6,
            'gas_quality': 'sweet',
            'location': {'lat': 12.0, 'lon': 13.5}
        },
        'Benue Trough': {
            'proven_reserves_tcf': 5.0,
            'probable_reserves_tcf': 12.0,
            'daily_production_mmscf': 100,
            'associated_gas_ratio': 0.3,
            'gas_quality': 'sweet',
            'location': {'lat': 7.5, 'lon': 8.8}
        }
    }
    
    reserves_production_data = []
    
    # Generate monthly data for 2020-2024
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    current_date = start_date
    while current_date <= end_date:
        for field_name, field_data in gas_fields.items():
            # Reserves decline over time due to production
            years_since_2020 = (current_date.year - 2020) + (current_date.month - 1) / 12
            
            # Annual decline rates (varies by field maturity)
            decline_rates = {
                'Niger Delta': 0.02,      # 2% per year (mature field)
                'Offshore Deep Water': 0.015,  # 1.5% per year (newer)
                'Anambra Basin': 0.025,   # 2.5% per year (smaller field)
                'Chad Basin': 0.01,      # 1% per year (underdeveloped)
                'Benue Trough': 0.005    # 0.5% per year (exploration stage)
            }
            
            decline_rate = decline_rates.get(field_name, 0.02)
            decline_factor = (1 - decline_rate) ** years_since_2020
            
            # Current reserves
            current_proven = field_data['proven_reserves_tcf'] * decline_factor
            current_probable = field_data['probable_reserves_tcf'] * decline_factor
            
            # Production varies with market conditions and infrastructure
            base_production = field_data['daily_production_mmscf']
            
            # Seasonal variations (maintenance, weather)
            seasonal_factor = get_seasonal_production_factor(current_date.month, field_name)
            
            # Market demand variations
            market_factor = get_market_demand_factor(current_date)
            
            # Infrastructure constraints
            infrastructure_factor = get_infrastructure_factor(field_name, current_date)
            
            current_production = base_production * seasonal_factor * market_factor * infrastructure_factor * decline_factor
            
            # Gas composition (important for SOFC applications)
            gas_composition = get_gas_composition(field_data['gas_quality'])
            
            reserves_production_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'field_name': field_name,
                'proven_reserves_tcf': round(current_proven, 2),
                'probable_reserves_tcf': round(current_probable, 2),
                'total_reserves_tcf': round(current_proven + current_probable, 2),
                'daily_production_mmscf': round(current_production, 2),
                'monthly_production_mmscf': round(current_production * 30, 2),
                'associated_gas_ratio': field_data['associated_gas_ratio'],
                'gas_quality': field_data['gas_quality'],
                'methane_content_percent': gas_composition['methane'],
                'ethane_content_percent': gas_composition['ethane'],
                'propane_content_percent': gas_composition['propane'],
                'co2_content_percent': gas_composition['co2'],
                'h2s_content_ppm': gas_composition['h2s'],
                'heating_value_btu_per_scf': gas_composition['heating_value'],
                'latitude': field_data['location']['lat'],
                'longitude': field_data['location']['lon'],
                'production_cost_usd_per_mscf': get_production_cost(field_name, current_date),
                'wellhead_pressure_psi': np.random.uniform(800, 1500),
                'water_content_ppm': np.random.uniform(50, 200)
            })
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return pd.DataFrame(reserves_production_data)

def get_seasonal_production_factor(month, field_name):
    """Get seasonal production adjustment factor"""
    
    # Offshore fields affected by weather
    if 'Offshore' in field_name:
        if 6 <= month <= 9:  # Rainy season - rougher seas
            return np.random.uniform(0.8, 0.9)
        else:
            return np.random.uniform(0.95, 1.05)
    
    # Onshore fields less affected by weather
    return np.random.uniform(0.9, 1.1)

def get_market_demand_factor(date):
    """Get market demand adjustment factor"""
    
    # Higher demand during dry season (more generator usage)
    month = date.month
    if 11 <= month <= 3:  # Dry season
        return np.random.uniform(1.1, 1.3)
    else:  # Rainy season
        return np.random.uniform(0.9, 1.1)

def get_infrastructure_factor(field_name, date):
    """Get infrastructure constraint factor"""
    
    # Pipeline capacity and maintenance issues
    base_factors = {
        'Niger Delta': 0.95,        # Good infrastructure
        'Offshore Deep Water': 0.85, # Limited pipeline capacity
        'Anambra Basin': 0.7,       # Poor infrastructure
        'Chad Basin': 0.6,          # Very limited infrastructure
        'Benue Trough': 0.5         # Exploration stage
    }
    
    base_factor = base_factors.get(field_name, 0.8)
    
    # Infrastructure improvements over time
    years_since_2020 = date.year - 2020
    improvement_factor = 1 + (years_since_2020 * 0.02)  # 2% annual improvement
    
    # Random maintenance issues
    maintenance_factor = np.random.uniform(0.9, 1.0)
    
    return min(base_factor * improvement_factor * maintenance_factor, 1.0)

def get_gas_composition(gas_quality):
    """Get gas composition based on quality"""
    
    if gas_quality == 'sweet':
        return {
            'methane': np.random.uniform(85, 92),
            'ethane': np.random.uniform(4, 8),
            'propane': np.random.uniform(1, 3),
            'co2': np.random.uniform(1, 3),
            'h2s': np.random.uniform(0, 10),  # ppm
            'heating_value': np.random.uniform(1000, 1100)  # BTU/scf
        }
    else:  # sour gas
        return {
            'methane': np.random.uniform(80, 88),
            'ethane': np.random.uniform(3, 6),
            'propane': np.random.uniform(1, 2),
            'co2': np.random.uniform(3, 8),
            'h2s': np.random.uniform(50, 500),  # ppm
            'heating_value': np.random.uniform(950, 1050)  # BTU/scf
        }

def get_production_cost(field_name, date):
    """Get production cost in USD per thousand standard cubic feet"""
    
    base_costs = {
        'Niger Delta': 0.8,         # Mature, efficient
        'Offshore Deep Water': 2.5,  # High cost offshore
        'Anambra Basin': 1.2,       # Onshore, moderate
        'Chad Basin': 1.8,          # Remote, higher costs
        'Benue Trough': 3.0         # Exploration, high costs
    }
    
    base_cost = base_costs.get(field_name, 1.5)
    
    # Inflation and cost escalation
    years_since_2020 = date.year - 2020
    inflation_factor = (1.08 ** years_since_2020)  # 8% annual cost increase
    
    # Random market variations
    market_factor = np.random.uniform(0.9, 1.1)
    
    return round(base_cost * inflation_factor * market_factor, 2)

def generate_gas_flaring_data():
    """Generate gas flaring data - critical for SOFC opportunity analysis"""
    
    # Major flaring locations in Nigeria
    flaring_sites = {
        'Escravos': {'lat': 5.2, 'lon': 5.1, 'operator': 'Chevron', 'base_flaring_mmscf': 120},
        'Bonny': {'lat': 4.4, 'lon': 7.2, 'operator': 'Shell', 'base_flaring_mmscf': 95},
        'Forcados': {'lat': 5.4, 'lon': 5.4, 'operator': 'Shell', 'base_flaring_mmscf': 80},
        'Brass': {'lat': 4.3, 'lon': 6.2, 'operator': 'Agip', 'base_flaring_mmscf': 70},
        'Qua Iboe': {'lat': 4.5, 'lon': 7.9, 'operator': 'ExxonMobil', 'base_flaring_mmscf': 65},
        'Amenam': {'lat': 4.7, 'lon': 6.8, 'operator': 'Total', 'base_flaring_mmscf': 45},
        'Okwori': {'lat': 5.1, 'lon': 6.3, 'operator': 'Shell', 'base_flaring_mmscf': 40},
        'Utorogu': {'lat': 5.6, 'lon': 5.8, 'operator': 'Shell', 'base_flaring_mmscf': 35},
        'Obite': {'lat': 4.8, 'lon': 6.9, 'operator': 'Shell', 'base_flaring_mmscf': 30},
        'Alakiri': {'lat': 4.6, 'lon': 7.0, 'operator': 'Shell', 'base_flaring_mmscf': 25}
    }
    
    flaring_data = []
    
    # Generate daily data for 2020-2024
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    current_date = start_date
    while current_date <= end_date:
        for site_name, site_data in flaring_sites.items():
            # Base flaring amount
            base_flaring = site_data['base_flaring_mmscf']
            
            # Flaring reduction over time (government pressure and regulations)
            years_since_2020 = (current_date.year - 2020) + (current_date.month - 1) / 12
            reduction_factor = (0.95 ** years_since_2020)  # 5% annual reduction target
            
            # Production-linked variations (more production = more flaring)
            production_factor = np.random.uniform(0.8, 1.2)
            
            # Regulatory compliance variations
            compliance_factor = get_compliance_factor(site_data['operator'], current_date)
            
            # Weather effects (flaring may increase during storms for safety)
            weather_factor = get_weather_flaring_factor(current_date.month)
            
            daily_flaring = base_flaring * reduction_factor * production_factor * compliance_factor * weather_factor
            
            # Calculate environmental impact
            co2_emissions = daily_flaring * 0.0551  # tonnes CO2 per mmscf
            energy_wasted = daily_flaring * 1.037   # GJ per mmscf
            
            # SOFC potential calculation
            sofc_potential_mw = calculate_sofc_potential(daily_flaring)
            
            flaring_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'site_name': site_name,
                'operator': site_data['operator'],
                'latitude': site_data['lat'],
                'longitude': site_data['lon'],
                'daily_flaring_mmscf': round(daily_flaring, 2),
                'monthly_flaring_mmscf': round(daily_flaring * 30, 2),
                'annual_flaring_bcf': round(daily_flaring * 365 / 1000, 2),
                'co2_emissions_tonnes_per_day': round(co2_emissions, 2),
                'energy_wasted_gj_per_day': round(energy_wasted, 2),
                'sofc_potential_mw': round(sofc_potential_mw, 2),
                'distance_to_grid_km': np.random.uniform(5, 50),
                'local_power_demand_mw': np.random.uniform(10, 100),
                'flaring_efficiency_percent': np.random.uniform(95, 99),
                'gas_heating_value_btu_per_scf': np.random.uniform(1000, 1100),
                'regulatory_penalty_usd': get_regulatory_penalty(daily_flaring, current_date)
            })
        
        current_date += timedelta(days=1)
    
    return pd.DataFrame(flaring_data)

def get_compliance_factor(operator, date):
    """Get regulatory compliance factor by operator"""
    
    # Different operators have different compliance records
    compliance_factors = {
        'Shell': 0.85,      # Better compliance
        'Chevron': 0.80,    # Good compliance
        'ExxonMobil': 0.82, # Good compliance
        'Total': 0.75,      # Moderate compliance
        'Agip': 0.70        # Lower compliance
    }
    
    base_factor = compliance_factors.get(operator, 0.75)
    
    # Improving compliance over time due to regulations
    years_since_2020 = date.year - 2020
    improvement = years_since_2020 * 0.02  # 2% annual improvement
    
    return max(base_factor + improvement, 0.5)

def get_weather_flaring_factor(month):
    """Get weather-related flaring adjustment"""
    
    # Higher flaring during rainy season (safety, maintenance)
    if 5 <= month <= 10:  # Rainy season
        return np.random.uniform(1.05, 1.15)
    else:  # Dry season
        return np.random.uniform(0.95, 1.05)

def calculate_sofc_potential(daily_flaring_mmscf):
    """Calculate SOFC power generation potential from flared gas"""
    
    # Conversion factors:
    # 1 mmscf = 1,037 GJ (approximate)
    # SOFC efficiency: ~60% (electrical)
    # 1 GJ = 0.278 MWh
    
    energy_content_gj = daily_flaring_mmscf * 1.037
    electrical_energy_mwh = energy_content_gj * 0.278 * 0.60  # 60% efficiency
    
    # Assuming 24-hour operation
    power_mw = electrical_energy_mwh / 24
    
    # Account for system availability (90%)
    return power_mw * 0.90

def get_regulatory_penalty(daily_flaring, date):
    """Calculate regulatory penalties for flaring"""
    
    # Nigerian flaring penalty structure
    penalty_per_mmscf = 3.5  # USD per thousand scf (as of recent regulations)
    
    # Escalating penalties over time
    years_since_2020 = date.year - 2020
    escalation_factor = (1.1 ** years_since_2020)  # 10% annual increase
    
    return round(daily_flaring * penalty_per_mmscf * escalation_factor, 2)

def generate_pipeline_network_data():
    """Generate gas pipeline network data"""
    
    # Major gas pipelines in Nigeria
    pipelines = {
        'Escravos-Lagos Pipeline System (ELPS)': {
            'length_km': 1100,
            'diameter_inches': 24,
            'capacity_mmscf_per_day': 1000,
            'operator': 'Nigerian Gas Company',
            'start_point': {'name': 'Escravos', 'lat': 5.2, 'lon': 5.1},
            'end_point': {'name': 'Lagos', 'lat': 6.5, 'lon': 3.4},
            'commissioning_year': 1989,
            'status': 'operational'
        },
        'Obiafu-Obrikom-Oben (OB3) Pipeline': {
            'length_km': 150,
            'diameter_inches': 48,
            'capacity_mmscf_per_day': 2200,
            'operator': 'Shell',
            'start_point': {'name': 'Obiafu', 'lat': 5.0, 'lon': 6.5},
            'end_point': {'name': 'Oben', 'lat': 5.2, 'lon': 6.8},
            'commissioning_year': 2010,
            'status': 'operational'
        },
        'Eastern Gas Gathering System (EGGS)': {
            'length_km': 200,
            'diameter_inches': 36,
            'capacity_mmscf_per_day': 800,
            'operator': 'Shell',
            'start_point': {'name': 'Utorogu', 'lat': 5.6, 'lon': 5.8},
            'end_point': {'name': 'Warri', 'lat': 5.5, 'lon': 5.8},
            'commissioning_year': 1995,
            'status': 'operational'
        },
        'Ajaokuta-Kaduna-Kano (AKK) Pipeline': {
            'length_km': 614,
            'diameter_inches': 40,
            'capacity_mmscf_per_day': 2200,
            'operator': 'NNPC',
            'start_point': {'name': 'Ajaokuta', 'lat': 7.6, 'lon': 6.7},
            'end_point': {'name': 'Kano', 'lat': 12.0, 'lon': 8.5},
            'commissioning_year': 2023,
            'status': 'operational'
        },
        'Nigeria-Morocco Gas Pipeline': {
            'length_km': 5660,
            'diameter_inches': 48,
            'capacity_mmscf_per_day': 1000,
            'operator': 'NNPC/ONHYM',
            'start_point': {'name': 'Warri', 'lat': 5.5, 'lon': 5.8},
            'end_point': {'name': 'Tangier', 'lat': 35.8, 'lon': -5.8},
            'commissioning_year': 2030,
            'status': 'under_construction'
        }
    }
    
    pipeline_data = []
    
    # Generate monthly operational data for 2020-2024
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    current_date = start_date
    while current_date <= end_date:
        for pipeline_name, pipeline_info in pipelines.items():
            # Skip if pipeline not yet operational
            if current_date.year < pipeline_info['commissioning_year']:
                continue
            
            # Skip if under construction
            if pipeline_info['status'] == 'under_construction' and current_date.year < 2030:
                continue
            
            # Calculate utilization
            max_capacity = pipeline_info['capacity_mmscf_per_day']
            
            # Utilization varies based on demand, maintenance, etc.
            base_utilization = get_pipeline_utilization(pipeline_name, current_date)
            
            # Maintenance shutdowns
            maintenance_factor = get_maintenance_factor(current_date)
            
            # Market demand
            demand_factor = get_pipeline_demand_factor(pipeline_name, current_date)
            
            actual_utilization = base_utilization * maintenance_factor * demand_factor
            actual_flow = max_capacity * actual_utilization
            
            pipeline_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'pipeline_name': pipeline_name,
                'operator': pipeline_info['operator'],
                'length_km': pipeline_info['length_km'],
                'diameter_inches': pipeline_info['diameter_inches'],
                'max_capacity_mmscf_per_day': max_capacity,
                'actual_flow_mmscf_per_day': round(actual_flow, 2),
                'utilization_percent': round(actual_utilization * 100, 2),
                'start_latitude': pipeline_info['start_point']['lat'],
                'start_longitude': pipeline_info['start_point']['lon'],
                'end_latitude': pipeline_info['end_point']['lat'],
                'end_longitude': pipeline_info['end_point']['lon'],
                'operating_pressure_psi': np.random.uniform(800, 1200),
                'compressor_stations': int(pipeline_info['length_km'] / 100),  # Roughly every 100km
                'maintenance_cost_usd_per_km': np.random.uniform(1000, 5000),
                'throughput_revenue_usd': round(actual_flow * np.random.uniform(2, 4), 2),
                'status': pipeline_info['status']
            })
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return pd.DataFrame(pipeline_data)

def get_pipeline_utilization(pipeline_name, date):
    """Get base pipeline utilization factor"""
    
    # Different pipelines have different utilization patterns
    base_utilizations = {
        'Escravos-Lagos Pipeline System (ELPS)': 0.85,  # High demand Lagos
        'Obiafu-Obrikom-Oben (OB3) Pipeline': 0.90,    # Industrial demand
        'Eastern Gas Gathering System (EGGS)': 0.75,    # Regional supply
        'Ajaokuta-Kaduna-Kano (AKK) Pipeline': 0.60,    # New, building demand
        'Nigeria-Morocco Gas Pipeline': 0.80            # Export pipeline
    }
    
    return base_utilizations.get(pipeline_name, 0.70)

def get_maintenance_factor(date):
    """Get maintenance shutdown factor"""
    
    # Scheduled maintenance typically in dry season
    month = date.month
    if 1 <= month <= 3:  # Dry season maintenance
        return np.random.uniform(0.8, 0.95)
    else:
        return np.random.uniform(0.95, 1.0)

def get_pipeline_demand_factor(pipeline_name, date):
    """Get demand-based utilization factor"""
    
    # Higher demand during dry season (more power generation)
    month = date.month
    if 11 <= month <= 3:  # Dry season
        return np.random.uniform(1.05, 1.15)
    else:
        return np.random.uniform(0.9, 1.05)

def generate_fuel_prices_data():
    """Generate diesel and petrol price data across Nigerian states"""
    
    # Nigerian states
    states = [
        'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa', 'Benue', 'Borno',
        'Cross River', 'Delta', 'Ebonyi', 'Edo', 'Ekiti', 'Enugu', 'FCT', 'Gombe',
        'Imo', 'Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Kogi', 'Kwara',
        'Lagos', 'Nasarawa', 'Niger', 'Ogun', 'Ondo', 'Osun', 'Oyo', 'Plateau',
        'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara'
    ]
    
    fuel_price_data = []
    
    # Generate monthly data for 2020-2024
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    current_date = start_date
    while current_date <= end_date:
        # Base prices (Naira per liter) - varies over time
        base_petrol_price = get_base_fuel_price('petrol', current_date)
        base_diesel_price = get_base_fuel_price('diesel', current_date)
        
        for state in states:
            # State-specific price adjustments
            petrol_adjustment = get_state_price_adjustment(state, 'petrol')
            diesel_adjustment = get_state_price_adjustment(state, 'diesel')
            
            # Regional supply chain costs
            transport_cost = get_transport_cost_factor(state)
            
            # Local market variations
            market_factor = np.random.uniform(0.95, 1.05)
            
            # Final prices
            petrol_price = base_petrol_price * petrol_adjustment * transport_cost * market_factor
            diesel_price = base_diesel_price * diesel_adjustment * transport_cost * market_factor
            
            fuel_price_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'state': state,
                'petrol_price_naira_per_liter': round(petrol_price, 2),
                'diesel_price_naira_per_liter': round(diesel_price, 2),
                'kerosene_price_naira_per_liter': round(diesel_price * 0.85, 2),  # Kerosene typically cheaper
                'lpg_price_naira_per_kg': round(diesel_price * 0.6, 2),  # LPG per kg
                'fuel_scarcity_factor': get_fuel_scarcity_factor(state, current_date),
                'black_market_premium_percent': get_black_market_premium(state, current_date),
                'supply_disruption_days': get_supply_disruption_days(state, current_date),
                'nearest_depot_distance_km': get_depot_distance(state),
                'local_consumption_million_liters': np.random.uniform(5, 50)
            })
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return pd.DataFrame(fuel_price_data)

def get_base_fuel_price(fuel_type, date):
    """Get base fuel price with inflation and global oil price effects"""
    
    # Base prices as of 2020 (Naira per liter)
    base_prices_2020 = {
        'petrol': 125,  # PMS
        'diesel': 180   # AGO
    }
    
    base_price = base_prices_2020.get(fuel_type, 150)
    
    # Inflation and currency devaluation
    years_since_2020 = (date.year - 2020) + (date.month - 1) / 12
    inflation_factor = (1.18 ** years_since_2020)  # 18% annual inflation
    
    # Global oil price volatility
    oil_volatility = np.random.uniform(0.8, 1.3)
    
    # Subsidy removal effects (gradual over time)
    subsidy_factor = 1 + (years_since_2020 * 0.1)  # Gradual subsidy removal
    
    return base_price * inflation_factor * oil_volatility * subsidy_factor

def get_state_price_adjustment(state, fuel_type):
    """Get state-specific price adjustment factors"""
    
    # States closer to refineries/depots have lower prices
    price_adjustments = {
        'Lagos': 0.95,      # Major refinery and port
        'Rivers': 0.96,     # Port Harcourt refinery
        'Delta': 0.97,      # Warri refinery
        'Kaduna': 0.98,     # Kaduna refinery
        'FCT': 1.0,         # Capital, good supply
        'Kano': 1.02,       # Northern commercial center
        'Ogun': 0.99,       # Close to Lagos
        'Anambra': 1.01,    # Commercial hub
        'Borno': 1.15,      # Remote, security issues
        'Yobe': 1.12,       # Remote
        'Zamfara': 1.10,    # Remote, security issues
        'Taraba': 1.08,     # Remote
        'Adamawa': 1.06,    # Remote
        'Bayelsa': 1.03,    # Oil producing but remote
    }
    
    return price_adjustments.get(state, 1.05)  # Default for unlisted states

def get_transport_cost_factor(state):
    """Get transportation cost factor based on distance from supply centers"""
    
    # Distance-based cost factors
    transport_factors = {
        'Lagos': 1.0,       # Major supply hub
        'Rivers': 1.0,      # Port Harcourt hub
        'Delta': 1.0,       # Warri hub
        'Kaduna': 1.02,     # Northern hub
        'FCT': 1.01,        # Central location
        'Kano': 1.05,       # Far from southern supply
        'Borno': 1.20,      # Very remote
        'Yobe': 1.18,       # Very remote
        'Sokoto': 1.15,     # Remote northwest
        'Kebbi': 1.12,      # Remote northwest
        'Zamfara': 1.14,    # Remote, poor roads
        'Jigawa': 1.08,     # Remote north
        'Bauchi': 1.06,     # North central
        'Gombe': 1.07,      # Northeast
        'Taraba': 1.10,     # Remote northeast
        'Adamawa': 1.09,    # Remote northeast
    }
    
    return transport_factors.get(state, 1.05)

def get_fuel_scarcity_factor(state, date):
    """Get fuel scarcity factor (1.0 = normal supply, >1.0 = scarcity)"""
    
    # Base scarcity varies by state infrastructure
    base_scarcity = {
        'Lagos': 1.02,      # Good infrastructure
        'FCT': 1.01,        # Capital priority
        'Rivers': 1.03,     # Oil region
        'Kano': 1.05,       # Northern commercial
        'Borno': 1.25,      # Security issues
        'Yobe': 1.20,       # Remote, security
        'Zamfara': 1.18,    # Security issues
        'Adamawa': 1.12,    # Remote
        'Taraba': 1.15,     # Remote
    }
    
    base = base_scarcity.get(state, 1.08)
    
    # Seasonal variations (higher scarcity during farming/travel seasons)
    month = date.month
    if month in [12, 1, 4, 8]:  # Holiday/farming seasons
        seasonal_factor = np.random.uniform(1.05, 1.15)
    else:
        seasonal_factor = np.random.uniform(0.95, 1.05)
    
    return round(base * seasonal_factor, 2)

def get_black_market_premium(state, date):
    """Get black market price premium percentage"""
    
    # Higher premiums in states with more scarcity
    base_premiums = {
        'Borno': 40,        # High security risk
        'Yobe': 35,         # Remote, limited supply
        'Zamfara': 30,      # Security issues
        'Adamawa': 25,      # Remote
        'Taraba': 28,       # Remote
        'Sokoto': 20,       # Remote northwest
        'Kebbi': 18,        # Remote
        'Jigawa': 15,       # Remote north
        'Bauchi': 12,       # Limited infrastructure
        'Gombe': 14,        # Remote
        'Plateau': 10,      # Central but limited supply
        'Nasarawa': 8,      # Central
        'Benue': 12,        # Agricultural, seasonal demand
        'Kogi': 10,         # Central
        'Kwara': 8,         # Reasonable access
        'Niger': 15,        # Large, sparse
        'FCT': 5,           # Capital, priority supply
        'Lagos': 3,         # Best supply
        'Ogun': 5,          # Close to Lagos
        'Rivers': 4,        # Oil region
        'Delta': 6,         # Oil region
        'Edo': 8,           # Reasonable access
        'Ondo': 10,         # Limited access
        'Ekiti': 12,        # Hilly, limited access
        'Osun': 8,          # Central southwest
        'Oyo': 6,           # Good access
        'Kaduna': 7,        # Northern hub
        'Kano': 8,          # Commercial center
        'Katsina': 12,      # Border, limited supply
        'Anambra': 6,       # Commercial hub
        'Imo': 8,           # Southeast
        'Abia': 9,          # Southeast
        'Enugu': 7,         # Southeast hub
        'Ebonyi': 12,       # Remote southeast
        'Cross River': 10,  # Border, limited supply
        'Akwa Ibom': 8,     # Oil region
        'Bayelsa': 15       # Remote oil region
    }
    
    base_premium = base_premiums.get(state, 10)
    
    # Seasonal variations
    month = date.month
    if month in [12, 1]:  # Holiday season
        seasonal_factor = 1.5
    elif month in [4, 8]:  # Farming seasons
        seasonal_factor = 1.3
    else:
        seasonal_factor = 1.0
    
    return round(base_premium * seasonal_factor, 1)

def get_supply_disruption_days(state, date):
    """Get number of supply disruption days per month"""
    
    # Base disruption days per month
    base_disruptions = {
        'Borno': 8,         # Security issues
        'Yobe': 6,          # Remote, security
        'Adamawa': 5,       # Remote
        'Zamfara': 7,       # Security issues
        'Taraba': 4,        # Remote
        'Sokoto': 3,        # Remote
        'Kebbi': 3,         # Remote
        'Jigawa': 2,        # Remote
        'Bauchi': 2,        # Limited infrastructure
        'Gombe': 3,         # Remote
        'Plateau': 2,       # Central
        'Nasarawa': 1,      # Central
        'Benue': 2,         # Agricultural pressure
        'Kogi': 1,          # Central
        'Kwara': 1,         # Good access
        'Niger': 2,         # Large, sparse
        'FCT': 0,           # Priority supply
        'Lagos': 0,         # Best supply
        'Ogun': 0,          # Close to Lagos
        'Rivers': 1,        # Oil region
        'Delta': 1,         # Oil region
        'Edo': 1,           # Reasonable access
        'Ondo': 2,          # Limited access
        'Ekiti': 2,         # Limited access
        'Osun': 1,          # Central southwest
        'Oyo': 1,           # Good access
        'Kaduna': 1,        # Northern hub
        'Kano': 1,          # Commercial center
        'Katsina': 2,       # Border issues
        'Anambra': 1,       # Commercial hub
        'Imo': 1,           # Southeast
        'Abia': 1,          # Southeast
        'Enugu': 1,         # Southeast hub
        'Ebonyi': 2,        # Remote southeast
        'Cross River': 2,   # Border, limited supply
        'Akwa Ibom': 1,     # Oil region
        'Bayelsa': 3        # Remote oil region
    }
    
    base_days = base_disruptions.get(state, 2)
    
    # Random monthly variation
    variation = np.random.poisson(base_days)
    
    return min(variation, 15)  # Cap at 15 days per month

def get_depot_distance(state):
    """Get distance to nearest fuel depot"""
    
    # Distances in kilometers to nearest major depot
    depot_distances = {
        'Lagos': 5,         # Multiple depots
        'Rivers': 10,       # Port Harcourt depot
        'Delta': 15,        # Warri depot
        'Kaduna': 20,       # Kaduna depot
        'FCT': 25,          # Abuja area
        'Kano': 30,         # Northern depot
        'Ogun': 35,         # Lagos vicinity
        'Edo': 40,          # Benin area
        'Anambra': 45,      # Onitsha area
        'Oyo': 50,          # Ibadan area
        'Imo': 55,          # Southeast
        'Abia': 60,         # Southeast
        'Enugu': 65,        # Southeast
        'Cross River': 120, # Remote southeast
        'Akwa Ibom': 80,    # South south
        'Bayelsa': 90,      # Remote oil region
        'Ondo': 70,         # Southwest
        'Ekiti': 85,        # Southwest hills
        'Osun': 75,         # Southwest
        'Kwara': 95,        # North central
        'Kogi': 100,        # North central
        'Benue': 110,       # North central
        'Nasarawa': 90,     # North central
        'Niger': 120,       # Large, sparse
        'Plateau': 130,     # North central hills
        'Bauchi': 180,      # Northeast
        'Gombe': 200,       # Northeast
        'Taraba': 220,      # Remote northeast
        'Adamawa': 250,     # Remote northeast
        'Borno': 300,       # Very remote
        'Yobe': 280,        # Very remote
        'Jigawa': 150,      # Remote north
        'Katsina': 140,     # Remote north
        'Zamfara': 160,     # Remote northwest
        'Sokoto': 180,      # Remote northwest
        'Kebbi': 200,       # Remote northwest
        'Ebonyi': 100       # Southeast
    }
    
    return depot_distances.get(state, 150)

def main():
    """Generate all fossil fuel datasets"""
    
    print("Generating Nigerian Fossil Fuel Data...")
    
    # Create output directory
    output_dir = "../raw_data/fossil_fuels"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate datasets
    print("1. Generating gas reserves and production data...")
    reserves_df = generate_gas_reserves_production_data()
    reserves_df.to_csv(f"{output_dir}/gas_reserves_production_data.csv", index=False)
    
    print("2. Generating gas flaring data...")
    flaring_df = generate_gas_flaring_data()
    flaring_df.to_csv(f"{output_dir}/gas_flaring_data.csv", index=False)
    
    print("3. Generating pipeline network data...")
    pipeline_df = generate_pipeline_network_data()
    pipeline_df.to_csv(f"{output_dir}/pipeline_network_data.csv", index=False)
    
    print("4. Generating fuel prices data...")
    fuel_prices_df = generate_fuel_prices_data()
    fuel_prices_df.to_csv(f"{output_dir}/fuel_prices_data.csv", index=False)
    
    # Generate summary statistics
    print("5. Generating summary statistics...")
    summary_stats = {
        'gas_reserves_production': {
            'total_proven_reserves_tcf': reserves_df.groupby('date')['proven_reserves_tcf'].sum().mean(),
            'total_probable_reserves_tcf': reserves_df.groupby('date')['probable_reserves_tcf'].sum().mean(),
            'average_daily_production_mmscf': reserves_df.groupby('date')['daily_production_mmscf'].sum().mean(),
            'largest_field': reserves_df.groupby('field_name')['proven_reserves_tcf'].first().idxmax(),
            'average_production_cost_usd_per_mscf': reserves_df['production_cost_usd_per_mscf'].mean()
        },
        'gas_flaring': {
            'total_daily_flaring_mmscf': flaring_df.groupby('date')['daily_flaring_mmscf'].sum().mean(),
            'total_annual_flaring_bcf': flaring_df.groupby('date')['daily_flaring_mmscf'].sum().mean() * 365 / 1000,
            'total_sofc_potential_mw': flaring_df.groupby('date')['sofc_potential_mw'].sum().mean(),
            'annual_co2_emissions_million_tonnes': flaring_df.groupby('date')['co2_emissions_tonnes_per_day'].sum().mean() * 365 / 1000000,
            'largest_flaring_site': flaring_df.groupby('site_name')['daily_flaring_mmscf'].mean().idxmax()
        },
        'pipeline_network': {
            'total_pipeline_length_km': pipeline_df['length_km'].sum() / len(pipeline_df['pipeline_name'].unique()),
            'total_capacity_mmscf_per_day': pipeline_df.groupby('date')['max_capacity_mmscf_per_day'].sum().mean(),
            'average_utilization_percent': pipeline_df['utilization_percent'].mean(),
            'operational_pipelines': len(pipeline_df[pipeline_df['status'] == 'operational']['pipeline_name'].unique())
        },
        'fuel_prices': {
            'average_petrol_price_naira_per_liter': fuel_prices_df['petrol_price_naira_per_liter'].mean(),
            'average_diesel_price_naira_per_liter': fuel_prices_df['diesel_price_naira_per_liter'].mean(),
            'highest_price_state': fuel_prices_df.groupby('state')['petrol_price_naira_per_liter'].mean().idxmax(),
            'lowest_price_state': fuel_prices_df.groupby('state')['petrol_price_naira_per_liter'].mean().idxmin(),
            'average_scarcity_factor': fuel_prices_df['fuel_scarcity_factor'].mean()
        }
    }
    
    with open(f"{output_dir}/summary_statistics.json", 'w') as f:
        json.dump(summary_stats, f, indent=2)
    
    print(f"\nFossil Fuel Data Generation Complete!")
    print(f"Generated {len(reserves_df)} gas reserves/production records")
    print(f"Generated {len(flaring_df)} gas flaring records")
    print(f"Generated {len(pipeline_df)} pipeline network records")
    print(f"Generated {len(fuel_prices_df)} fuel price records")
    print(f"\nFiles saved to: {output_dir}/")

if __name__ == "__main__":
    main()