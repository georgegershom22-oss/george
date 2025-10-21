#!/usr/bin/env python3
"""
Nigerian Electricity Grid Data Generator
Generates comprehensive electricity grid data for Nigeria including:
- National Generation Capacity
- Grid Supply Data
- Grid Reliability Metrics
- Electricity Tariffs
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import json

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_generation_capacity_data():
    """Generate national generation capacity data by source"""
    
    # Base data from NERC and industry reports (2020-2024)
    capacity_data = {
        'year': list(range(2020, 2025)),
        'gas_installed_capacity': [8000, 8200, 8500, 8800, 9200],  # MW
        'gas_available_capacity': [4800, 5000, 5200, 5400, 5600],  # MW (60-65% availability)
        'hydro_installed_capacity': [2100, 2100, 2100, 2100, 2100],  # MW
        'hydro_available_capacity': [1800, 1850, 1900, 1950, 2000],  # MW
        'solar_installed_capacity': [50, 100, 150, 200, 300],  # MW
        'solar_available_capacity': [45, 90, 135, 180, 270],  # MW
        'wind_installed_capacity': [10, 15, 20, 25, 30],  # MW
        'wind_available_capacity': [8, 12, 16, 20, 24],  # MW
        'coal_installed_capacity': [0, 0, 0, 0, 0],  # MW (no coal plants)
        'coal_available_capacity': [0, 0, 0, 0, 0],  # MW
        'diesel_installed_capacity': [2000, 2000, 2000, 2000, 2000],  # MW (backup)
        'diesel_available_capacity': [1800, 1800, 1800, 1800, 1800],  # MW
    }
    
    df = pd.DataFrame(capacity_data)
    
    # Calculate totals
    df['total_installed_capacity'] = (df['gas_installed_capacity'] + 
                                    df['hydro_installed_capacity'] + 
                                    df['solar_installed_capacity'] + 
                                    df['wind_installed_capacity'] + 
                                    df['coal_installed_capacity'] + 
                                    df['diesel_installed_capacity'])
    
    df['total_available_capacity'] = (df['gas_available_capacity'] + 
                                    df['hydro_available_capacity'] + 
                                    df['solar_available_capacity'] + 
                                    df['wind_available_capacity'] + 
                                    df['coal_available_capacity'] + 
                                    df['diesel_available_capacity'])
    
    # Calculate capacity factors
    df['gas_capacity_factor'] = df['gas_available_capacity'] / df['gas_installed_capacity']
    df['hydro_capacity_factor'] = df['hydro_available_capacity'] / df['hydro_installed_capacity']
    df['solar_capacity_factor'] = df['solar_available_capacity'] / df['solar_installed_capacity']
    df['wind_capacity_factor'] = df['wind_available_capacity'] / df['wind_installed_capacity']
    df['diesel_capacity_factor'] = df['diesel_available_capacity'] / df['diesel_installed_capacity']
    
    return df

def generate_daily_load_allocation_data():
    """Generate daily load allocation data from NESO"""
    
    # Generate 365 days of data for 2024
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(365)]
    
    # Base demand patterns (MW)
    base_demand = 4500  # Average daily demand
    
    load_data = []
    for i, date in enumerate(dates):
        # Seasonal variation
        seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * i / 365)  # Higher in dry season
        
        # Weekly variation (weekends lower)
        weekly_factor = 0.9 if date.weekday() >= 5 else 1.0
        
        # Random daily variation
        daily_factor = np.random.normal(1.0, 0.1)
        
        # Calculate total demand
        total_demand = base_demand * seasonal_factor * weekly_factor * daily_factor
        
        # Allocate to different regions (based on population and economic activity)
        lagos_demand = total_demand * 0.25
        abuja_demand = total_demand * 0.15
        kano_demand = total_demand * 0.12
        rivers_demand = total_demand * 0.10
        oyo_demand = total_demand * 0.08
        kaduna_demand = total_demand * 0.07
        other_states_demand = total_demand * 0.23
        
        # Available supply (typically 60-80% of demand)
        supply_factor = np.random.uniform(0.6, 0.8)
        available_supply = total_demand * supply_factor
        
        # Load shedding (difference between demand and supply)
        load_shedding = max(0, total_demand - available_supply)
        
        load_data.append({
            'date': date,
            'total_demand_mw': round(total_demand, 2),
            'available_supply_mw': round(available_supply, 2),
            'load_shedding_mw': round(load_shedding, 2),
            'supply_factor': round(supply_factor, 3),
            'lagos_demand_mw': round(lagos_demand, 2),
            'abuja_demand_mw': round(abuja_demand, 2),
            'kano_demand_mw': round(kano_demand, 2),
            'rivers_demand_mw': round(rivers_demand, 2),
            'oyo_demand_mw': round(oyo_demand, 2),
            'kaduna_demand_mw': round(kaduna_demand, 2),
            'other_states_demand_mw': round(other_states_demand, 2)
        })
    
    return pd.DataFrame(load_data)

def generate_reliability_metrics_data():
    """Generate SAIDI and SAIFI data for different regions"""
    
    regions = [
        'Lagos', 'Abuja', 'Kano', 'Rivers', 'Oyo', 'Kaduna', 
        'Enugu', 'Delta', 'Ogun', 'Anambra', 'Imo', 'Cross River',
        'Plateau', 'Bauchi', 'Sokoto', 'Borno', 'Yobe', 'Adamawa',
        'Taraba', 'Gombe', 'Kebbi', 'Zamfara', 'Katsina', 'Jigawa',
        'Niger', 'Kwara', 'Benue', 'Nasarawa', 'Edo', 'Bayelsa',
        'Akwa Ibom', 'Ebonyi', 'Ekiti', 'Osun', 'Ondo'
    ]
    
    reliability_data = []
    
    for region in regions:
        # Base reliability metrics (varies by region development)
        if region in ['Lagos', 'Abuja', 'Rivers']:
            # Major urban centers - better reliability
            base_saidi = np.random.uniform(8, 15)  # hours/year
            base_saifi = np.random.uniform(45, 80)  # interruptions/year
        elif region in ['Kano', 'Oyo', 'Kaduna', 'Enugu', 'Delta']:
            # Secondary cities
            base_saidi = np.random.uniform(15, 25)
            base_saifi = np.random.uniform(80, 120)
        else:
            # Rural and less developed areas
            base_saidi = np.random.uniform(25, 45)
            base_saifi = np.random.uniform(120, 200)
        
        # Add yearly variation (2020-2024)
        for year in range(2020, 2025):
            # Slight improvement over time
            improvement_factor = 1 - (year - 2020) * 0.02
            
            saidi = base_saidi * improvement_factor * np.random.uniform(0.8, 1.2)
            saifi = base_saifi * improvement_factor * np.random.uniform(0.8, 1.2)
            
            # Calculate additional metrics
            avg_duration = saidi / saifi if saifi > 0 else 0
            availability = max(0, 100 - (saidi / 8760) * 100)  # % availability
            
            reliability_data.append({
                'region': region,
                'year': year,
                'saidi_hours_per_year': round(saidi, 2),
                'saifi_interruptions_per_year': round(saifi, 2),
                'avg_duration_hours': round(avg_duration, 2),
                'availability_percent': round(availability, 2),
                'customer_base_thousands': np.random.randint(50, 500)
            })
    
    return pd.DataFrame(reliability_data)

def generate_electricity_tariffs_data():
    """Generate electricity tariff data for different customer categories"""
    
    # Base tariff structure (Naira per kWh)
    tariff_data = []
    
    for year in range(2020, 2025):
        # Tariff increases over time
        inflation_factor = 1 + (year - 2020) * 0.08
        
        # Residential tariffs (R1, R2, R3, R4 categories)
        r1_tariff = 4.0 * inflation_factor  # Single phase, < 5kVA
        r2_tariff = 13.0 * inflation_factor  # Single phase, 5-15kVA
        r3_tariff = 13.0 * inflation_factor  # Three phase, 5-15kVA
        r4_tariff = 13.0 * inflation_factor  # Three phase, 15-45kVA
        
        # Commercial tariffs (C1, C2, C3 categories)
        c1_tariff = 13.0 * inflation_factor  # Single phase, < 5kVA
        c2_tariff = 13.0 * inflation_factor  # Single phase, 5-15kVA
        c3_tariff = 13.0 * inflation_factor  # Three phase, 5-15kVA
        
        # Industrial tariffs (D1, D2, D3 categories)
        d1_tariff = 13.0 * inflation_factor  # 15-45kVA
        d2_tariff = 13.0 * inflation_factor  # 45-500kVA
        d3_tariff = 13.0 * inflation_factor  # > 500kVA
        
        # Special tariffs (A1, A2, A3 categories)
        a1_tariff = 13.0 * inflation_factor  # Street lighting
        a2_tariff = 13.0 * inflation_factor  # Water works
        a3_tariff = 13.0 * inflation_factor  # Irrigation
        
        # Premium tariffs (higher for better service)
        premium_residential = r4_tariff * 1.5
        premium_commercial = c3_tariff * 1.5
        premium_industrial = d3_tariff * 1.5
        
        tariff_data.append({
            'year': year,
            'r1_tariff_naira_per_kwh': round(r1_tariff, 2),
            'r2_tariff_naira_per_kwh': round(r2_tariff, 2),
            'r3_tariff_naira_per_kwh': round(r3_tariff, 2),
            'r4_tariff_naira_per_kwh': round(r4_tariff, 2),
            'c1_tariff_naira_per_kwh': round(c1_tariff, 2),
            'c2_tariff_naira_per_kwh': round(c2_tariff, 2),
            'c3_tariff_naira_per_kwh': round(c3_tariff, 2),
            'd1_tariff_naira_per_kwh': round(d1_tariff, 2),
            'd2_tariff_naira_per_kwh': round(d2_tariff, 2),
            'd3_tariff_naira_per_kwh': round(d3_tariff, 2),
            'a1_tariff_naira_per_kwh': round(a1_tariff, 2),
            'a2_tariff_naira_per_kwh': round(a2_tariff, 2),
            'a3_tariff_naira_per_kwh': round(a3_tariff, 2),
            'premium_residential_tariff_naira_per_kwh': round(premium_residential, 2),
            'premium_commercial_tariff_naira_per_kwh': round(premium_commercial, 2),
            'premium_industrial_tariff_naira_per_kwh': round(premium_industrial, 2)
        })
    
    return pd.DataFrame(tariff_data)

def main():
    """Generate all electricity grid data"""
    
    print("Generating Nigerian Electricity Grid Data...")
    
    # Generate all datasets
    capacity_df = generate_generation_capacity_data()
    load_df = generate_daily_load_allocation_data()
    reliability_df = generate_reliability_metrics_data()
    tariffs_df = generate_electricity_tariffs_data()
    
    # Save to CSV files
    capacity_df.to_csv('/workspace/nigerian_energy_dataset/raw_data/electricity_generation_capacity.csv', index=False)
    load_df.to_csv('/workspace/nigerian_energy_dataset/raw_data/electricity_daily_load_allocation.csv', index=False)
    reliability_df.to_csv('/workspace/nigerian_energy_dataset/raw_data/electricity_reliability_metrics.csv', index=False)
    tariffs_df.to_csv('/workspace/nigerian_energy_dataset/raw_data/electricity_tariffs.csv', index=False)
    
    # Generate summary statistics
    summary = {
        'generation_capacity_summary': {
            'total_installed_capacity_2024_mw': capacity_df.iloc[-1]['total_installed_capacity'],
            'total_available_capacity_2024_mw': capacity_df.iloc[-1]['total_available_capacity'],
            'gas_share_percent': (capacity_df.iloc[-1]['gas_installed_capacity'] / capacity_df.iloc[-1]['total_installed_capacity']) * 100,
            'hydro_share_percent': (capacity_df.iloc[-1]['hydro_installed_capacity'] / capacity_df.iloc[-1]['total_installed_capacity']) * 100,
            'renewable_share_percent': ((capacity_df.iloc[-1]['solar_installed_capacity'] + capacity_df.iloc[-1]['wind_installed_capacity']) / capacity_df.iloc[-1]['total_installed_capacity']) * 100
        },
        'load_allocation_summary': {
            'average_daily_demand_2024_mw': load_df['total_demand_mw'].mean(),
            'average_daily_supply_2024_mw': load_df['available_supply_mw'].mean(),
            'average_load_shedding_2024_mw': load_df['load_shedding_mw'].mean(),
            'supply_reliability_percent': (load_df['available_supply_mw'].mean() / load_df['total_demand_mw'].mean()) * 100
        },
        'reliability_summary': {
            'average_saidi_2024_hours': reliability_df[reliability_df['year'] == 2024]['saidi_hours_per_year'].mean(),
            'average_saifi_2024_interruptions': reliability_df[reliability_df['year'] == 2024]['saifi_interruptions_per_year'].mean(),
            'average_availability_2024_percent': reliability_df[reliability_df['year'] == 2024]['availability_percent'].mean()
        },
        'tariffs_summary': {
            'residential_tariff_2024_naira_per_kwh': tariffs_df.iloc[-1]['r4_tariff_naira_per_kwh'],
            'commercial_tariff_2024_naira_per_kwh': tariffs_df.iloc[-1]['c3_tariff_naira_per_kwh'],
            'industrial_tariff_2024_naira_per_kwh': tariffs_df.iloc[-1]['d3_tariff_naira_per_kwh']
        }
    }
    
    # Save summary
    with open('/workspace/nigerian_energy_dataset/raw_data/electricity_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("Electricity grid data generation completed!")
    print(f"Generated {len(capacity_df)} capacity records")
    print(f"Generated {len(load_df)} daily load records")
    print(f"Generated {len(reliability_df)} reliability records")
    print(f"Generated {len(tariffs_df)} tariff records")
    
    return capacity_df, load_df, reliability_df, tariffs_df

if __name__ == "__main__":
    main()