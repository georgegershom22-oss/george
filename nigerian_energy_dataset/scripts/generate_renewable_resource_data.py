#!/usr/bin/env python3
"""
Nigerian Renewable Resource Data Generator
Generates comprehensive renewable resource data for Nigeria including:
- Agricultural Waste Data (crop residues)
- Livestock Population Data (for biogas potential)
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import json

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_agricultural_waste_data():
    """Generate agricultural waste data by state and crop type"""
    
    # Nigerian states
    states = [
        'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa',
        'Benue', 'Borno', 'Cross River', 'Delta', 'Ebonyi', 'Edo',
        'Ekiti', 'Enugu', 'FCT', 'Gombe', 'Imo', 'Jigawa',
        'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Kogi', 'Kwara',
        'Lagos', 'Nasarawa', 'Niger', 'Ogun', 'Ondo', 'Osun',
        'Oyo', 'Plateau', 'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara'
    ]
    
    # Major crops in Nigeria with their residue production factors
    crops = {
        'rice': {'residue_factor': 1.5, 'energy_content_mj_per_kg': 15.5, 'moisture_content': 0.15},
        'maize': {'residue_factor': 1.2, 'energy_content_mj_per_kg': 17.2, 'moisture_content': 0.12},
        'sorghum': {'residue_factor': 1.3, 'energy_content_mj_per_kg': 16.8, 'moisture_content': 0.14},
        'millet': {'residue_factor': 1.1, 'energy_content_mj_per_kg': 16.5, 'moisture_content': 0.13},
        'cassava': {'residue_factor': 0.8, 'energy_content_mj_per_kg': 14.2, 'moisture_content': 0.20},
        'yam': {'residue_factor': 0.6, 'energy_content_mj_per_kg': 13.8, 'moisture_content': 0.18},
        'sweet_potato': {'residue_factor': 0.7, 'energy_content_mj_per_kg': 14.5, 'moisture_content': 0.16},
        'cocoa': {'residue_factor': 2.0, 'energy_content_mj_per_kg': 18.5, 'moisture_content': 0.10},
        'groundnut': {'residue_factor': 1.8, 'energy_content_mj_per_kg': 17.8, 'moisture_content': 0.08},
        'soybean': {'residue_factor': 1.6, 'energy_content_mj_per_kg': 17.0, 'moisture_content': 0.11},
        'sugarcane': {'residue_factor': 0.3, 'energy_content_mj_per_kg': 19.2, 'moisture_content': 0.25},
        'cotton': {'residue_factor': 2.2, 'energy_content_mj_per_kg': 16.0, 'moisture_content': 0.12},
        'palm_oil': {'residue_factor': 1.0, 'energy_content_mj_per_kg': 20.5, 'moisture_content': 0.15}
    }
    
    agricultural_waste_data = []
    
    for state in states:
        for year in range(2020, 2025):
            # Base agricultural production varies by state and year
            # Major agricultural states have higher production
            if state in ['Kano', 'Kaduna', 'Katsina', 'Jigawa', 'Bauchi', 'Gombe']:
                # Northern states - major grain producers
                base_production_factor = np.random.uniform(0.8, 1.2)
            elif state in ['Oyo', 'Ogun', 'Osun', 'Ondo', 'Ekiti', 'Kwara']:
                # Southwestern states - mixed agriculture
                base_production_factor = np.random.uniform(0.6, 1.0)
            elif state in ['Rivers', 'Delta', 'Bayelsa', 'Akwa Ibom', 'Cross River']:
                # South-south states - oil palm and cassava
                base_production_factor = np.random.uniform(0.4, 0.8)
            elif state in ['Enugu', 'Anambra', 'Imo', 'Abia', 'Ebonyi']:
                # Southeastern states - mixed agriculture
                base_production_factor = np.random.uniform(0.5, 0.9)
            else:
                # Other states
                base_production_factor = np.random.uniform(0.3, 0.7)
            
            # Yearly variation (slight growth trend)
            yearly_factor = 1 + (year - 2020) * 0.02
            
            for crop, crop_data in crops.items():
                # Base production (tonnes per year) - varies by crop and state
                base_production = {
                    'rice': 50000, 'maize': 80000, 'sorghum': 30000, 'millet': 20000,
                    'cassava': 100000, 'yam': 60000, 'sweet_potato': 15000,
                    'cocoa': 10000, 'groundnut': 25000, 'soybean': 15000,
                    'sugarcane': 5000, 'cotton': 8000, 'palm_oil': 20000
                }
                
                production = base_production[crop] * base_production_factor * yearly_factor
                
                # Calculate residue production
                residue_production = production * crop_data['residue_factor']
                
                # Calculate energy potential
                dry_residue = residue_production * (1 - crop_data['moisture_content'])
                energy_potential = dry_residue * crop_data['energy_content_mj_per_kg'] / 1000  # GJ
                
                # Calculate biogas potential (assuming 200 m³ biogas per tonne dry matter)
                biogas_potential = dry_residue * 200  # m³
                
                # Calculate electricity potential (assuming 2 kWh per m³ biogas)
                electricity_potential = biogas_potential * 2  # kWh
                
                agricultural_waste_data.append({
                    'state': state,
                    'year': year,
                    'crop': crop,
                    'crop_production_tonnes': round(production, 2),
                    'residue_production_tonnes': round(residue_production, 2),
                    'dry_residue_tonnes': round(dry_residue, 2),
                    'energy_content_mj_per_kg': crop_data['energy_content_mj_per_kg'],
                    'moisture_content': crop_data['moisture_content'],
                    'energy_potential_gj': round(energy_potential, 2),
                    'biogas_potential_m3': round(biogas_potential, 2),
                    'electricity_potential_kwh': round(electricity_potential, 2)
                })
    
    return pd.DataFrame(agricultural_waste_data)

def generate_livestock_population_data():
    """Generate livestock population data by state for biogas potential"""
    
    states = [
        'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa',
        'Benue', 'Borno', 'Cross River', 'Delta', 'Ebonyi', 'Edo',
        'Ekiti', 'Enugu', 'FCT', 'Gombe', 'Imo', 'Jigawa',
        'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Kogi', 'Kwara',
        'Lagos', 'Nasarawa', 'Niger', 'Ogun', 'Ondo', 'Osun',
        'Oyo', 'Plateau', 'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara'
    ]
    
    # Livestock types with manure production rates
    livestock_types = {
        'cattle': {
            'manure_production_kg_per_head_per_day': 25,
            'biogas_production_m3_per_kg_manure': 0.04,
            'methane_content': 0.6
        },
        'sheep': {
            'manure_production_kg_per_head_per_day': 2.5,
            'biogas_production_m3_per_kg_manure': 0.05,
            'methane_content': 0.6
        },
        'goats': {
            'manure_production_kg_per_head_per_day': 2.0,
            'biogas_production_m3_per_kg_manure': 0.05,
            'methane_content': 0.6
        },
        'pigs': {
            'manure_production_kg_per_head_per_day': 5.0,
            'biogas_production_m3_per_kg_manure': 0.06,
            'methane_content': 0.65
        },
        'poultry': {
            'manure_production_kg_per_head_per_day': 0.1,
            'biogas_production_m3_per_kg_manure': 0.08,
            'methane_content': 0.7
        },
        'donkeys': {
            'manure_production_kg_per_head_per_day': 15,
            'biogas_production_m3_per_kg_manure': 0.04,
            'methane_content': 0.6
        },
        'horses': {
            'manure_production_kg_per_head_per_day': 20,
            'biogas_production_m3_per_kg_manure': 0.04,
            'methane_content': 0.6
        }
    }
    
    livestock_data = []
    
    for state in states:
        for year in range(2020, 2025):
            # Base population varies by state (Northern states have more livestock)
            if state in ['Kano', 'Katsina', 'Jigawa', 'Bauchi', 'Gombe', 'Sokoto', 'Kebbi', 'Zamfara']:
                # Northern states - major livestock producers
                population_factor = np.random.uniform(1.2, 1.8)
            elif state in ['Kaduna', 'Niger', 'Plateau', 'Nasarawa', 'Taraba', 'Adamawa', 'Yobe', 'Borno']:
                # Middle belt and northeastern states
                population_factor = np.random.uniform(0.8, 1.4)
            elif state in ['Oyo', 'Ogun', 'Osun', 'Ondo', 'Ekiti', 'Kwara', 'Lagos']:
                # Southwestern states
                population_factor = np.random.uniform(0.4, 0.8)
            elif state in ['Enugu', 'Anambra', 'Imo', 'Abia', 'Ebonyi', 'Delta', 'Edo']:
                # Southeastern states
                population_factor = np.random.uniform(0.3, 0.7)
            else:
                # Other states
                population_factor = np.random.uniform(0.2, 0.6)
            
            # Yearly growth (slight increase over time)
            yearly_factor = 1 + (year - 2020) * 0.03
            
            for livestock, livestock_data_info in livestock_types.items():
                # Base population (thousands of heads)
                base_population = {
                    'cattle': 5000, 'sheep': 15000, 'goats': 20000, 'pigs': 2000,
                    'poultry': 50000, 'donkeys': 1000, 'horses': 500
                }
                
                population = base_population[livestock] * population_factor * yearly_factor
                
                # Calculate manure production
                daily_manure = population * livestock_data_info['manure_production_kg_per_head_per_day']
                annual_manure = daily_manure * 365 / 1000  # tonnes per year
                
                # Calculate biogas potential
                daily_biogas = daily_manure * livestock_data_info['biogas_production_m3_per_kg_manure']
                annual_biogas = daily_biogas * 365  # m³ per year
                
                # Calculate methane production
                annual_methane = annual_biogas * livestock_data_info['methane_content']
                
                # Calculate electricity potential (assuming 2 kWh per m³ biogas)
                annual_electricity = annual_biogas * 2  # kWh per year
                
                # Calculate energy content (assuming 20 MJ per m³ biogas)
                annual_energy = annual_biogas * 20 / 1000  # GJ per year
                
                livestock_data.append({
                    'state': state,
                    'year': year,
                    'livestock_type': livestock,
                    'population_thousands': round(population, 2),
                    'daily_manure_production_kg': round(daily_manure, 2),
                    'annual_manure_production_tonnes': round(annual_manure, 2),
                    'daily_biogas_potential_m3': round(daily_biogas, 2),
                    'annual_biogas_potential_m3': round(annual_biogas, 2),
                    'annual_methane_production_m3': round(annual_methane, 2),
                    'annual_electricity_potential_kwh': round(annual_electricity, 2),
                    'annual_energy_potential_gj': round(annual_energy, 2),
                    'methane_content': livestock_data_info['methane_content']
                })
    
    return pd.DataFrame(livestock_data)

def generate_biomass_potential_summary():
    """Generate summary of total biomass potential by state"""
    
    # Load the generated data
    agricultural_df = generate_agricultural_waste_data()
    livestock_df = generate_livestock_population_data()
    
    # Aggregate agricultural waste by state and year
    agricultural_summary = agricultural_df.groupby(['state', 'year']).agg({
        'energy_potential_gj': 'sum',
        'biogas_potential_m3': 'sum',
        'electricity_potential_kwh': 'sum'
    }).reset_index()
    
    # Aggregate livestock data by state and year
    livestock_summary = livestock_df.groupby(['state', 'year']).agg({
        'annual_energy_potential_gj': 'sum',
        'annual_biogas_potential_m3': 'sum',
        'annual_electricity_potential_kwh': 'sum'
    }).reset_index()
    
    # Merge agricultural and livestock data
    biomass_summary = pd.merge(
        agricultural_summary, 
        livestock_summary, 
        on=['state', 'year'], 
        how='outer'
    ).fillna(0)
    
    # Calculate totals
    biomass_summary['total_energy_potential_gj'] = (
        biomass_summary['energy_potential_gj'] + 
        biomass_summary['annual_energy_potential_gj']
    )
    
    biomass_summary['total_biogas_potential_m3'] = (
        biomass_summary['biogas_potential_m3'] + 
        biomass_summary['annual_biogas_potential_m3']
    )
    
    biomass_summary['total_electricity_potential_kwh'] = (
        biomass_summary['electricity_potential_kwh'] + 
        biomass_summary['annual_electricity_potential_kwh']
    )
    
    # Convert to more useful units
    biomass_summary['total_energy_potential_twh'] = biomass_summary['total_energy_potential_gj'] / 3600
    biomass_summary['total_electricity_potential_mwh'] = biomass_summary['total_electricity_potential_kwh'] / 1000
    
    return biomass_summary

def main():
    """Generate all renewable resource data"""
    
    print("Generating Nigerian Renewable Resource Data...")
    
    # Generate all datasets
    agricultural_waste_df = generate_agricultural_waste_data()
    livestock_df = generate_livestock_population_data()
    biomass_summary_df = generate_biomass_potential_summary()
    
    # Save to CSV files
    agricultural_waste_df.to_csv('/workspace/nigerian_energy_dataset/raw_data/agricultural_waste_data.csv', index=False)
    livestock_df.to_csv('/workspace/nigerian_energy_dataset/raw_data/livestock_population_data.csv', index=False)
    biomass_summary_df.to_csv('/workspace/nigerian_energy_dataset/raw_data/biomass_potential_summary.csv', index=False)
    
    # Generate summary statistics
    summary = {
        'agricultural_waste_summary': {
            'total_crops_analyzed': len(agricultural_waste_df['crop'].unique()),
            'total_states': len(agricultural_waste_df['state'].unique()),
            'total_years': len(agricultural_waste_df['year'].unique()),
            'total_records': len(agricultural_waste_df)
        },
        'livestock_summary': {
            'total_livestock_types': len(livestock_df['livestock_type'].unique()),
            'total_states': len(livestock_df['state'].unique()),
            'total_years': len(livestock_df['year'].unique()),
            'total_records': len(livestock_df)
        },
        'biomass_potential_2024': {
            'total_energy_potential_twh': float(biomass_summary_df[biomass_summary_df['year'] == 2024]['total_energy_potential_twh'].sum()),
            'total_electricity_potential_mwh': float(biomass_summary_df[biomass_summary_df['year'] == 2024]['total_electricity_potential_mwh'].sum()),
            'total_biogas_potential_million_m3': float(biomass_summary_df[biomass_summary_df['year'] == 2024]['total_biogas_potential_m3'].sum() / 1000000)
        },
        'top_biomass_states_2024': {
            'top_5_states_by_energy_potential': biomass_summary_df[biomass_summary_df['year'] == 2024].nlargest(5, 'total_energy_potential_twh')[['state', 'total_energy_potential_twh']].to_dict('records')
        }
    }
    
    # Save summary
    with open('/workspace/nigerian_energy_dataset/raw_data/renewable_resource_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("Renewable resource data generation completed!")
    print(f"Generated {len(agricultural_waste_df)} agricultural waste records")
    print(f"Generated {len(livestock_df)} livestock records")
    print(f"Generated {len(biomass_summary_df)} biomass summary records")
    
    return agricultural_waste_df, livestock_df, biomass_summary_df

if __name__ == "__main__":
    main()