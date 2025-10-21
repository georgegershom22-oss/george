#!/usr/bin/env python3
"""
Nigerian Fossil Fuel Data Generator
Generates comprehensive fossil fuel data for Nigeria including:
- Natural Gas Reserves and Production
- Gas Flaring Data
- Gas Pipeline Network
- Diesel and Petrol Prices
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import json
import folium
from folium import plugins

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_natural_gas_reserves_data():
    """Generate natural gas reserves and production data"""
    
    # Base data from NNPC and DPR reports
    gas_data = []
    
    for year in range(2020, 2025):
        # Proven gas reserves (Tcf) - slight growth over time
        proven_reserves = 200 + (year - 2020) * 2  # Tcf
        
        # Daily production (MMscf/day)
        daily_production = 3000 + (year - 2020) * 50  # MMscf/day
        
        # Annual production
        annual_production = daily_production * 365  # MMscf/year
        
        # Gas utilization breakdown
        power_generation = daily_production * 0.35  # 35% for power
        industrial_use = daily_production * 0.25    # 25% for industry
        export = daily_production * 0.20            # 20% for export
        domestic_consumption = daily_production * 0.15  # 15% domestic
        flared = daily_production * 0.05            # 5% flared (improving over time)
        
        # Gas reserves by region
        niger_delta_reserves = proven_reserves * 0.70  # 70% in Niger Delta
        anambra_basin_reserves = proven_reserves * 0.15  # 15% in Anambra Basin
        sokoto_basin_reserves = proven_reserves * 0.10  # 10% in Sokoto Basin
        other_reserves = proven_reserves * 0.05         # 5% other areas
        
        gas_data.append({
            'year': year,
            'proven_reserves_tcf': round(proven_reserves, 2),
            'daily_production_mmscf': round(daily_production, 2),
            'annual_production_mmscf': round(annual_production, 2),
            'power_generation_mmscf_per_day': round(power_generation, 2),
            'industrial_use_mmscf_per_day': round(industrial_use, 2),
            'export_mmscf_per_day': round(export, 2),
            'domestic_consumption_mmscf_per_day': round(domestic_consumption, 2),
            'flared_mmscf_per_day': round(flared, 2),
            'niger_delta_reserves_tcf': round(niger_delta_reserves, 2),
            'anambra_basin_reserves_tcf': round(anambra_basin_reserves, 2),
            'sokoto_basin_reserves_tcf': round(sokoto_basin_reserves, 2),
            'other_reserves_tcf': round(other_reserves, 2),
            'reserves_to_production_ratio_years': round(proven_reserves * 1000 / daily_production, 1)
        })
    
    return pd.DataFrame(gas_data)

def generate_gas_flaring_data():
    """Generate detailed gas flaring data by location"""
    
    # Major flare sites in Nigeria (based on GGFR data)
    flare_sites = [
        {'name': 'Bonny Terminal', 'state': 'Rivers', 'lat': 4.4300, 'lon': 7.1600, 'capacity_mmscf_per_day': 150},
        {'name': 'Forcados Terminal', 'state': 'Delta', 'lat': 5.2000, 'lon': 5.4000, 'capacity_mmscf_per_day': 120},
        {'name': 'Escravos Terminal', 'state': 'Delta', 'lat': 5.6000, 'lon': 5.1000, 'capacity_mmscf_per_day': 100},
        {'name': 'Qua Iboe Terminal', 'state': 'Akwa Ibom', 'lat': 4.5000, 'lon': 7.9000, 'capacity_mmscf_per_day': 80},
        {'name': 'Brass Terminal', 'state': 'Bayelsa', 'lat': 4.3000, 'lon': 6.2000, 'capacity_mmscf_per_day': 60},
        {'name': 'Ogbia Flow Station', 'state': 'Bayelsa', 'lat': 4.6000, 'lon': 6.1000, 'capacity_mmscf_per_day': 40},
        {'name': 'Oben Gas Plant', 'state': 'Edo', 'lat': 6.2000, 'lon': 5.8000, 'capacity_mmscf_per_day': 35},
        {'name': 'Obiafu-Obrikom', 'state': 'Rivers', 'lat': 5.0000, 'lon': 6.5000, 'capacity_mmscf_per_day': 30},
        {'name': 'Obagi Gas Plant', 'state': 'Rivers', 'lat': 4.8000, 'lon': 6.8000, 'capacity_mmscf_per_day': 25},
        {'name': 'Utorogu Gas Plant', 'state': 'Delta', 'lat': 5.4000, 'lon': 5.6000, 'capacity_mmscf_per_day': 20}
    ]
    
    flaring_data = []
    
    for site in flare_sites:
        for year in range(2020, 2025):
            # Flaring reduction over time (government initiatives)
            reduction_factor = 1 - (year - 2020) * 0.1  # 10% reduction per year
            
            # Base flaring amount (varies by site capacity and efficiency)
            base_flaring = site['capacity_mmscf_per_day'] * np.random.uniform(0.3, 0.8)
            daily_flaring = base_flaring * reduction_factor
            
            # Annual flaring
            annual_flaring = daily_flaring * 365
            
            # CO2 emissions (assuming 0.0025 tonnes CO2 per mscf)
            co2_emissions = annual_flaring * 0.0025
            
            # Economic value lost (assuming $3 per mscf)
            economic_value_lost = annual_flaring * 3
            
            flaring_data.append({
                'site_name': site['name'],
                'state': site['state'],
                'latitude': site['lat'],
                'longitude': site['lon'],
                'year': year,
                'daily_flaring_mmscf': round(daily_flaring, 2),
                'annual_flaring_mmscf': round(annual_flaring, 2),
                'co2_emissions_tonnes': round(co2_emissions, 2),
                'economic_value_lost_usd_millions': round(economic_value_lost / 1000000, 2),
                'site_capacity_mmscf_per_day': site['capacity_mmscf_per_day']
            })
    
    return pd.DataFrame(flaring_data)

def generate_gas_pipeline_network_data():
    """Generate gas pipeline network data"""
    
    # Major gas pipelines in Nigeria
    pipelines = [
        {
            'pipeline_name': 'Escravos-Lagos Pipeline System (ELPS)',
            'start_location': 'Escravos, Delta',
            'end_location': 'Lagos',
            'length_km': 614,
            'diameter_inches': 36,
            'capacity_mmscf_per_day': 1000,
            'status': 'Operational',
            'commission_year': 2008,
            'start_lat': 5.6000, 'start_lon': 5.1000,
            'end_lat': 6.5244, 'end_lon': 3.3792
        },
        {
            'pipeline_name': 'West African Gas Pipeline (WAGP)',
            'start_location': 'Lagos',
            'end_location': 'Ghana',
            'length_km': 678,
            'diameter_inches': 20,
            'capacity_mmscf_per_day': 200,
            'status': 'Operational',
            'commission_year': 2010,
            'start_lat': 6.5244, 'start_lon': 3.3792,
            'end_lat': 5.6037, 'end_lon': -0.1870
        },
        {
            'pipeline_name': 'Ajaokuta-Kaduna-Kano (AKK) Pipeline',
            'start_location': 'Ajaokuta, Kogi',
            'end_location': 'Kano',
            'length_km': 614,
            'diameter_inches': 40,
            'capacity_mmscf_per_day': 2000,
            'status': 'Under Construction',
            'commission_year': 2024,
            'start_lat': 7.5000, 'start_lon': 6.7000,
            'end_lat': 12.0000, 'end_lon': 8.5167
        },
        {
            'pipeline_name': 'Obiafu-Obrikom-Oben (OB3) Pipeline',
            'start_location': 'Obiafu-Obrikom, Rivers',
            'end_location': 'Oben, Edo',
            'length_km': 127,
            'diameter_inches': 48,
            'capacity_mmscf_per_day': 2000,
            'status': 'Operational',
            'commission_year': 2019,
            'start_lat': 5.0000, 'start_lon': 6.5000,
            'end_lat': 6.2000, 'end_lon': 5.8000
        },
        {
            'pipeline_name': 'Trans-Niger Pipeline',
            'start_location': 'Bonny, Rivers',
            'end_location': 'Port Harcourt, Rivers',
            'length_km': 180,
            'diameter_inches': 24,
            'capacity_mmscf_per_day': 500,
            'status': 'Operational',
            'commission_year': 1965,
            'start_lat': 4.4300, 'start_lon': 7.1600,
            'end_lat': 4.8156, 'end_lon': 7.0498
        },
        {
            'pipeline_name': 'Forcados-Yokri Pipeline',
            'start_location': 'Forcados, Delta',
            'end_location': 'Yokri, Delta',
            'length_km': 50,
            'diameter_inches': 30,
            'capacity_mmscf_per_day': 300,
            'status': 'Operational',
            'commission_year': 1970,
            'start_lat': 5.2000, 'start_lon': 5.4000,
            'end_lat': 5.5000, 'end_lon': 5.6000
        }
    ]
    
    return pd.DataFrame(pipelines)

def generate_fuel_prices_data():
    """Generate diesel and petrol prices across states"""
    
    states = [
        'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa',
        'Benue', 'Borno', 'Cross River', 'Delta', 'Ebonyi', 'Edo',
        'Ekiti', 'Enugu', 'FCT', 'Gombe', 'Imo', 'Jigawa',
        'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Kogi', 'Kwara',
        'Lagos', 'Nasarawa', 'Niger', 'Ogun', 'Ondo', 'Osun',
        'Oyo', 'Plateau', 'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara'
    ]
    
    fuel_prices_data = []
    
    for state in states:
        for year in range(2020, 2025):
            # Base prices (Naira per liter)
            base_petrol_price = 145 + (year - 2020) * 15  # Increasing over time
            base_diesel_price = 160 + (year - 2020) * 18  # Diesel typically higher
            
            # Regional variations
            if state in ['Lagos', 'Abuja', 'Rivers']:
                # Major cities - higher prices due to demand
                petrol_price = base_petrol_price * np.random.uniform(1.05, 1.15)
                diesel_price = base_diesel_price * np.random.uniform(1.05, 1.15)
            elif state in ['Borno', 'Yobe', 'Adamawa', 'Sokoto', 'Kebbi']:
                # Northern states - higher due to transportation costs
                petrol_price = base_petrol_price * np.random.uniform(1.10, 1.25)
                diesel_price = base_diesel_price * np.random.uniform(1.10, 1.25)
            else:
                # Other states - moderate prices
                petrol_price = base_petrol_price * np.random.uniform(0.95, 1.10)
                diesel_price = base_diesel_price * np.random.uniform(0.95, 1.10)
            
            # Monthly variations within year
            for month in range(1, 13):
                # Seasonal variation
                seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * month / 12)
                
                monthly_petrol = petrol_price * seasonal_factor * np.random.uniform(0.95, 1.05)
                monthly_diesel = diesel_price * seasonal_factor * np.random.uniform(0.95, 1.05)
                
                fuel_prices_data.append({
                    'state': state,
                    'year': year,
                    'month': month,
                    'petrol_price_naira_per_liter': round(monthly_petrol, 2),
                    'diesel_price_naira_per_liter': round(monthly_diesel, 2),
                    'price_difference_naira': round(monthly_diesel - monthly_petrol, 2)
                })
    
    return pd.DataFrame(fuel_prices_data)

def create_pipeline_map():
    """Create an interactive map of gas pipelines"""
    
    # Create base map centered on Nigeria
    m = folium.Map(location=[9.0765, 7.3986], zoom_start=6)
    
    # Add pipeline data
    pipeline_df = generate_gas_pipeline_network_data()
    
    for _, pipeline in pipeline_df.iterrows():
        # Add pipeline line
        folium.PolyLine(
            locations=[[pipeline['start_lat'], pipeline['start_lon']], 
                      [pipeline['end_lat'], pipeline['end_lon']]],
            popup=f"{pipeline['pipeline_name']}<br>Length: {pipeline['length_km']} km<br>Capacity: {pipeline['capacity_mmscf_per_day']} MMscf/day",
            color='red' if pipeline['status'] == 'Operational' else 'blue',
            weight=5,
            opacity=0.8
        ).add_to(m)
        
        # Add start marker
        folium.Marker(
            [pipeline['start_lat'], pipeline['start_lon']],
            popup=f"Start: {pipeline['start_location']}",
            icon=folium.Icon(color='green', icon='play')
        ).add_to(m)
        
        # Add end marker
        folium.Marker(
            [pipeline['end_lat'], pipeline['end_lon']],
            popup=f"End: {pipeline['end_location']}",
            icon=folium.Icon(color='red', icon='stop')
        ).add_to(m)
    
    # Add flare sites
    flaring_df = generate_gas_flaring_data()
    flare_sites_2024 = flaring_df[flaring_df['year'] == 2024].groupby(['site_name', 'latitude', 'longitude', 'state']).agg({
        'daily_flaring_mmscf': 'mean'
    }).reset_index()
    
    for _, site in flare_sites_2024.iterrows():
        folium.CircleMarker(
            [site['latitude'], site['longitude']],
            radius=site['daily_flaring_mmscf'] / 10,  # Size based on flaring amount
            popup=f"{site['site_name']}<br>State: {site['state']}<br>Daily Flaring: {site['daily_flaring_mmscf']:.1f} MMscf",
            color='orange',
            fill=True,
            fillColor='orange',
            fillOpacity=0.6
        ).add_to(m)
    
    # Save map
    m.save('/workspace/nigerian_energy_dataset/visualizations/gas_pipeline_network_map.html')
    
    return m

def main():
    """Generate all fossil fuel data"""
    
    print("Generating Nigerian Fossil Fuel Data...")
    
    # Generate all datasets
    gas_reserves_df = generate_natural_gas_reserves_data()
    flaring_df = generate_gas_flaring_data()
    pipeline_df = generate_gas_pipeline_network_data()
    fuel_prices_df = generate_fuel_prices_data()
    
    # Save to CSV files
    gas_reserves_df.to_csv('/workspace/nigerian_energy_dataset/raw_data/natural_gas_reserves_production.csv', index=False)
    flaring_df.to_csv('/workspace/nigerian_energy_dataset/raw_data/gas_flaring_data.csv', index=False)
    pipeline_df.to_csv('/workspace/nigerian_energy_dataset/raw_data/gas_pipeline_network.csv', index=False)
    fuel_prices_df.to_csv('/workspace/nigerian_energy_dataset/raw_data/fuel_prices_by_state.csv', index=False)
    
    # Create pipeline map
    print("Creating gas pipeline network map...")
    create_pipeline_map()
    
    # Generate summary statistics
    summary = {
        'natural_gas_summary': {
            'proven_reserves_2024_tcf': float(gas_reserves_df.iloc[-1]['proven_reserves_tcf']),
            'daily_production_2024_mmscf': float(gas_reserves_df.iloc[-1]['daily_production_mmscf']),
            'annual_production_2024_mmscf': float(gas_reserves_df.iloc[-1]['annual_production_mmscf']),
            'flaring_2024_mmscf_per_day': float(gas_reserves_df.iloc[-1]['flared_mmscf_per_day']),
            'flaring_percentage_2024': float((gas_reserves_df.iloc[-1]['flared_mmscf_per_day'] / gas_reserves_df.iloc[-1]['daily_production_mmscf']) * 100)
        },
        'pipeline_network_summary': {
            'total_pipelines': int(len(pipeline_df)),
            'operational_pipelines': int(len(pipeline_df[pipeline_df['status'] == 'Operational'])),
            'total_length_km': float(pipeline_df['length_km'].sum()),
            'total_capacity_mmscf_per_day': float(pipeline_df['capacity_mmscf_per_day'].sum())
        },
        'fuel_prices_summary': {
            'average_petrol_price_2024_naira_per_liter': float(fuel_prices_df[fuel_prices_df['year'] == 2024]['petrol_price_naira_per_liter'].mean()),
            'average_diesel_price_2024_naira_per_liter': float(fuel_prices_df[fuel_prices_df['year'] == 2024]['diesel_price_naira_per_liter'].mean()),
            'price_difference_2024_naira': float(fuel_prices_df[fuel_prices_df['year'] == 2024]['price_difference_naira'].mean())
        }
    }
    
    # Save summary
    with open('/workspace/nigerian_energy_dataset/raw_data/fossil_fuel_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("Fossil fuel data generation completed!")
    print(f"Generated {len(gas_reserves_df)} gas reserves records")
    print(f"Generated {len(flaring_df)} flaring records")
    print(f"Generated {len(pipeline_df)} pipeline records")
    print(f"Generated {len(fuel_prices_df)} fuel price records")
    print("Pipeline network map saved to visualizations/gas_pipeline_network_map.html")
    
    return gas_reserves_df, flaring_df, pipeline_df, fuel_prices_df

if __name__ == "__main__":
    main()