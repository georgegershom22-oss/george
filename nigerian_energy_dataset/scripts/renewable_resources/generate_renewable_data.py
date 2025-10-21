#!/usr/bin/env python3
"""
Nigerian Renewable Resources Data Generator
Generates comprehensive renewable resource datasets for biofuel and biogas potential analysis
Supporting SOFC research with alternative feedstock analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

# Set random seed for reproducibility
np.random.seed(42)

def generate_agricultural_waste_data():
    """Generate agricultural waste data by crop type and state"""
    
    # Major crops in Nigeria and their waste characteristics
    crops = {
        'Rice': {
            'residue_types': ['Rice Husk', 'Rice Straw'],
            'residue_ratios': [0.2, 0.8],  # Husk: 20%, Straw: 80%
            'energy_content_mj_per_kg': [16.5, 14.2],
            'major_states': ['Kebbi', 'Niger', 'Kaduna', 'Taraba', 'Benue', 'Cross River'],
            'production_season': 'wet'
        },
        'Maize': {
            'residue_types': ['Maize Cob', 'Maize Stalk', 'Maize Husk'],
            'residue_ratios': [0.15, 0.7, 0.15],
            'energy_content_mj_per_kg': [17.8, 15.2, 16.1],
            'major_states': ['Kaduna', 'Kano', 'Katsina', 'Plateau', 'Taraba', 'Adamawa'],
            'production_season': 'both'
        },
        'Sugarcane': {
            'residue_types': ['Bagasse', 'Sugarcane Tops'],
            'residue_ratios': [0.8, 0.2],
            'energy_content_mj_per_kg': [19.2, 13.5],
            'major_states': ['Kaduna', 'Kano', 'Kebbi', 'Sokoto', 'Jigawa'],
            'production_season': 'dry'
        },
        'Cassava': {
            'residue_types': ['Cassava Peels', 'Cassava Stems'],
            'residue_ratios': [0.7, 0.3],
            'energy_content_mj_per_kg': [14.8, 16.3],
            'major_states': ['Ogun', 'Ondo', 'Cross River', 'Akwa Ibom', 'Enugu', 'Anambra'],
            'production_season': 'both'
        },
        'Yam': {
            'residue_types': ['Yam Peels', 'Yam Vines'],
            'residue_ratios': [0.6, 0.4],
            'energy_content_mj_per_kg': [15.1, 13.8],
            'major_states': ['Benue', 'Taraba', 'Nasarawa', 'Niger', 'Kwara', 'Oyo'],
            'production_season': 'wet'
        },
        'Sorghum': {
            'residue_types': ['Sorghum Stalks', 'Sorghum Chaff'],
            'residue_ratios': [0.8, 0.2],
            'energy_content_mj_per_kg': [16.7, 15.9],
            'major_states': ['Kano', 'Kaduna', 'Katsina', 'Jigawa', 'Bauchi', 'Borno'],
            'production_season': 'wet'
        },
        'Millet': {
            'residue_types': ['Millet Stalks', 'Millet Chaff'],
            'residue_ratios': [0.75, 0.25],
            'energy_content_mj_per_kg': [16.2, 15.4],
            'major_states': ['Sokoto', 'Kebbi', 'Zamfara', 'Katsina', 'Jigawa', 'Yobe'],
            'production_season': 'wet'
        },
        'Groundnut': {
            'residue_types': ['Groundnut Shells', 'Groundnut Haulms'],
            'residue_ratios': [0.3, 0.7],
            'energy_content_mj_per_kg': [18.5, 14.6],
            'major_states': ['Kano', 'Kaduna', 'Katsina', 'Jigawa', 'Bauchi', 'Taraba'],
            'production_season': 'wet'
        },
        'Cowpea': {
            'residue_types': ['Cowpea Pods', 'Cowpea Stalks'],
            'residue_ratios': [0.4, 0.6],
            'energy_content_mj_per_kg': [17.2, 15.8],
            'major_states': ['Kano', 'Katsina', 'Jigawa', 'Bauchi', 'Borno', 'Yobe'],
            'production_season': 'wet'
        },
        'Oil Palm': {
            'residue_types': ['Palm Kernel Shell', 'Empty Fruit Bunches', 'Palm Fiber'],
            'residue_ratios': [0.2, 0.6, 0.2],
            'energy_content_mj_per_kg': [20.1, 16.8, 18.3],
            'major_states': ['Cross River', 'Akwa Ibom', 'Rivers', 'Delta', 'Edo', 'Ondo'],
            'production_season': 'both'
        }
    }
    
    # Nigerian states
    all_states = [
        'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa', 'Benue', 'Borno',
        'Cross River', 'Delta', 'Ebonyi', 'Edo', 'Ekiti', 'Enugu', 'FCT', 'Gombe',
        'Imo', 'Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Kogi', 'Kwara',
        'Lagos', 'Nasarawa', 'Niger', 'Ogun', 'Ondo', 'Osun', 'Oyo', 'Plateau',
        'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara'
    ]
    
    agricultural_waste_data = []
    
    # Generate annual data for 2020-2024
    for year in range(2020, 2025):
        for crop, crop_info in crops.items():
            for state in all_states:
                # Check if state is a major producer
                if state in crop_info['major_states']:
                    production_factor = np.random.uniform(0.8, 1.2)  # Major producer
                else:
                    production_factor = np.random.uniform(0.1, 0.4)  # Minor producer
                
                # Base production (tonnes per year) - varies by crop and state
                base_production = get_base_crop_production(crop, state)
                annual_production = base_production * production_factor
                
                # Calculate residue generation
                for i, residue_type in enumerate(crop_info['residue_types']):
                    residue_ratio = crop_info['residue_ratios'][i]
                    energy_content = crop_info['energy_content_mj_per_kg'][i]
                    
                    residue_production = annual_production * residue_ratio
                    
                    # Current utilization (most agricultural waste is underutilized)
                    current_utilization = get_current_utilization_rate(residue_type, state)
                    
                    # Available for energy use
                    available_for_energy = residue_production * (1 - current_utilization)
                    
                    # Biogas potential calculation
                    biogas_potential = calculate_biogas_potential(residue_type, available_for_energy)
                    
                    # SOFC feedstock potential (if converted to syngas)
                    sofc_potential = calculate_sofc_feedstock_potential(residue_type, available_for_energy)
                    
                    agricultural_waste_data.append({
                        'year': year,
                        'state': state,
                        'crop': crop,
                        'residue_type': residue_type,
                        'crop_production_tonnes': round(annual_production, 2),
                        'residue_production_tonnes': round(residue_production, 2),
                        'residue_ratio': residue_ratio,
                        'energy_content_mj_per_kg': energy_content,
                        'total_energy_potential_gj': round(residue_production * energy_content, 2),
                        'current_utilization_rate': current_utilization,
                        'available_for_energy_tonnes': round(available_for_energy, 2),
                        'available_energy_potential_gj': round(available_for_energy * energy_content, 2),
                        'biogas_potential_m3': round(biogas_potential, 2),
                        'sofc_feedstock_potential_tonnes': round(sofc_potential, 2),
                        'collection_cost_naira_per_tonne': get_collection_cost(residue_type, state),
                        'transportation_cost_naira_per_tonne_km': get_transportation_cost(residue_type),
                        'storage_requirements': get_storage_requirements(residue_type),
                        'seasonal_availability': get_seasonal_availability(crop_info['production_season']),
                        'moisture_content_percent': get_moisture_content(residue_type),
                        'ash_content_percent': get_ash_content(residue_type),
                        'carbon_content_percent': get_carbon_content(residue_type),
                        'nitrogen_content_percent': get_nitrogen_content(residue_type)
                    })
    
    return pd.DataFrame(agricultural_waste_data)

def get_base_crop_production(crop, state):
    """Get base crop production in tonnes per year"""
    
    # Base production figures (tonnes/year) for major producing states
    base_productions = {
        'Rice': {
            'Kebbi': 800000, 'Niger': 600000, 'Kaduna': 500000, 'Taraba': 400000,
            'Benue': 350000, 'Cross River': 300000
        },
        'Maize': {
            'Kaduna': 1200000, 'Kano': 1000000, 'Katsina': 800000, 'Plateau': 600000,
            'Taraba': 500000, 'Adamawa': 450000
        },
        'Sugarcane': {
            'Kaduna': 500000, 'Kano': 400000, 'Kebbi': 300000, 'Sokoto': 250000,
            'Jigawa': 200000
        },
        'Cassava': {
            'Ogun': 2000000, 'Ondo': 1800000, 'Cross River': 1500000, 'Akwa Ibom': 1200000,
            'Enugu': 1000000, 'Anambra': 900000
        },
        'Yam': {
            'Benue': 1500000, 'Taraba': 800000, 'Nasarawa': 600000, 'Niger': 500000,
            'Kwara': 400000, 'Oyo': 350000
        },
        'Sorghum': {
            'Kano': 800000, 'Kaduna': 700000, 'Katsina': 600000, 'Jigawa': 500000,
            'Bauchi': 400000, 'Borno': 350000
        },
        'Millet': {
            'Sokoto': 400000, 'Kebbi': 350000, 'Zamfara': 300000, 'Katsina': 250000,
            'Jigawa': 200000, 'Yobe': 150000
        },
        'Groundnut': {
            'Kano': 600000, 'Kaduna': 500000, 'Katsina': 400000, 'Jigawa': 300000,
            'Bauchi': 250000, 'Taraba': 200000
        },
        'Cowpea': {
            'Kano': 300000, 'Katsina': 250000, 'Jigawa': 200000, 'Bauchi': 150000,
            'Borno': 120000, 'Yobe': 100000
        },
        'Oil Palm': {
            'Cross River': 800000, 'Akwa Ibom': 700000, 'Rivers': 600000, 'Delta': 500000,
            'Edo': 400000, 'Ondo': 300000
        }
    }
    
    crop_data = base_productions.get(crop, {})
    return crop_data.get(state, 50000)  # Default for non-major producers

def get_current_utilization_rate(residue_type, state):
    """Get current utilization rate of agricultural residues"""
    
    # Most agricultural waste is underutilized in Nigeria
    base_utilization = {
        'Rice Husk': 0.15,           # Some used for parboiling
        'Rice Straw': 0.05,          # Mostly burned in fields
        'Maize Cob': 0.20,           # Some used for fuel
        'Maize Stalk': 0.10,         # Some used for animal feed
        'Maize Husk': 0.05,          # Mostly wasted
        'Bagasse': 0.60,             # Used in sugar mills
        'Sugarcane Tops': 0.30,      # Some used for animal feed
        'Cassava Peels': 0.25,       # Some used for animal feed
        'Cassava Stems': 0.10,       # Mostly wasted
        'Yam Peels': 0.20,           # Some used for animal feed
        'Yam Vines': 0.15,           # Some used for mulching
        'Sorghum Stalks': 0.30,      # Used for construction, fuel
        'Sorghum Chaff': 0.10,       # Mostly wasted
        'Millet Stalks': 0.35,       # Used for construction, fuel
        'Millet Chaff': 0.05,        # Mostly wasted
        'Groundnut Shells': 0.40,    # Some used for fuel
        'Groundnut Haulms': 0.50,    # Used for animal feed
        'Cowpea Pods': 0.30,         # Some used for animal feed
        'Cowpea Stalks': 0.25,       # Some used for fuel
        'Palm Kernel Shell': 0.70,   # Used in palm oil mills
        'Empty Fruit Bunches': 0.40, # Some used for mulching
        'Palm Fiber': 0.30           # Some used for fuel
    }
    
    base_rate = base_utilization.get(residue_type, 0.15)
    
    # Urban states have higher utilization
    urban_states = ['Lagos', 'FCT', 'Kano', 'Rivers', 'Ogun']
    if state in urban_states:
        return min(base_rate * 1.3, 0.8)
    
    return base_rate

def calculate_biogas_potential(residue_type, available_tonnes):
    """Calculate biogas potential in cubic meters"""
    
    # Biogas yield (m3/tonne) for different residues
    biogas_yields = {
        'Rice Husk': 150,
        'Rice Straw': 200,
        'Maize Cob': 180,
        'Maize Stalk': 220,
        'Maize Husk': 160,
        'Bagasse': 170,
        'Sugarcane Tops': 250,
        'Cassava Peels': 300,
        'Cassava Stems': 180,
        'Yam Peels': 280,
        'Yam Vines': 200,
        'Sorghum Stalks': 190,
        'Sorghum Chaff': 140,
        'Millet Stalks': 185,
        'Millet Chaff': 135,
        'Groundnut Shells': 160,
        'Groundnut Haulms': 240,
        'Cowpea Pods': 220,
        'Cowpea Stalks': 210,
        'Palm Kernel Shell': 120,
        'Empty Fruit Bunches': 280,
        'Palm Fiber': 200
    }
    
    yield_per_tonne = biogas_yields.get(residue_type, 180)
    return available_tonnes * yield_per_tonne

def calculate_sofc_feedstock_potential(residue_type, available_tonnes):
    """Calculate SOFC feedstock potential after gasification"""
    
    # Conversion efficiency from biomass to syngas (varies by residue type)
    conversion_efficiencies = {
        'Rice Husk': 0.65,
        'Rice Straw': 0.60,
        'Maize Cob': 0.70,
        'Maize Stalk': 0.62,
        'Maize Husk': 0.68,
        'Bagasse': 0.72,
        'Sugarcane Tops': 0.58,
        'Cassava Peels': 0.55,
        'Cassava Stems': 0.63,
        'Yam Peels': 0.57,
        'Yam Vines': 0.61,
        'Sorghum Stalks': 0.66,
        'Sorghum Chaff': 0.64,
        'Millet Stalks': 0.65,
        'Millet Chaff': 0.63,
        'Groundnut Shells': 0.69,
        'Groundnut Haulms': 0.59,
        'Cowpea Pods': 0.61,
        'Cowpea Stalks': 0.62,
        'Palm Kernel Shell': 0.74,
        'Empty Fruit Bunches': 0.56,
        'Palm Fiber': 0.67
    }
    
    efficiency = conversion_efficiencies.get(residue_type, 0.62)
    return available_tonnes * efficiency

def get_collection_cost(residue_type, state):
    """Get collection cost in Naira per tonne"""
    
    # Base collection costs (Naira per tonne)
    base_costs = {
        'Rice Husk': 5000,           # Easy to collect at mills
        'Rice Straw': 8000,          # Field collection required
        'Maize Cob': 6000,           # Available at processing points
        'Maize Stalk': 10000,        # Field collection
        'Maize Husk': 7000,          # Processing point collection
        'Bagasse': 3000,             # Available at sugar mills
        'Sugarcane Tops': 12000,     # Field collection
        'Cassava Peels': 4000,       # Processing point collection
        'Cassava Stems': 15000,      # Field collection, bulky
        'Yam Peels': 5000,           # Processing point collection
        'Yam Vines': 18000,          # Field collection, scattered
        'Sorghum Stalks': 12000,     # Field collection
        'Sorghum Chaff': 6000,       # Processing point collection
        'Millet Stalks': 14000,      # Field collection
        'Millet Chaff': 7000,        # Processing point collection
        'Groundnut Shells': 4500,    # Processing point collection
        'Groundnut Haulms': 11000,   # Field collection
        'Cowpea Pods': 8000,         # Processing point collection
        'Cowpea Stalks': 13000,      # Field collection
        'Palm Kernel Shell': 2000,   # Available at palm oil mills
        'Empty Fruit Bunches': 3500, # Available at palm oil mills
        'Palm Fiber': 2500           # Available at palm oil mills
    }
    
    base_cost = base_costs.get(residue_type, 8000)
    
    # State-specific cost adjustments (labor, infrastructure)
    state_factors = {
        'Lagos': 1.4,      # High labor costs
        'FCT': 1.3,        # High costs
        'Rivers': 1.2,     # Oil region, higher costs
        'Kano': 1.1,       # Commercial center
        'Kaduna': 1.1,     # Industrial center
        'Borno': 0.7,      # Security issues, lower activity
        'Yobe': 0.8,       # Remote, lower costs
        'Zamfara': 0.8,    # Security issues
        'Sokoto': 0.9,     # Remote
        'Kebbi': 0.9       # Remote
    }
    
    factor = state_factors.get(state, 1.0)
    return round(base_cost * factor, 0)

def get_transportation_cost(residue_type):
    """Get transportation cost in Naira per tonne per km"""
    
    # Transportation costs vary by bulk density and handling requirements
    transport_costs = {
        'Rice Husk': 25,             # Light, bulky
        'Rice Straw': 30,            # Very bulky
        'Maize Cob': 20,             # Dense
        'Maize Stalk': 28,           # Bulky
        'Maize Husk': 22,            # Moderate bulk
        'Bagasse': 18,               # Compact when pressed
        'Sugarcane Tops': 32,        # Very bulky
        'Cassava Peels': 15,         # Dense, wet
        'Cassava Stems': 35,         # Very bulky
        'Yam Peels': 16,             # Dense
        'Yam Vines': 40,             # Very bulky, difficult handling
        'Sorghum Stalks': 26,        # Bulky
        'Sorghum Chaff': 20,         # Moderate bulk
        'Millet Stalks': 28,         # Bulky
        'Millet Chaff': 22,          # Moderate bulk
        'Groundnut Shells': 18,      # Moderate density
        'Groundnut Haulms': 24,      # Bulky
        'Cowpea Pods': 19,           # Moderate density
        'Cowpea Stalks': 25,         # Bulky
        'Palm Kernel Shell': 12,     # Very dense
        'Empty Fruit Bunches': 20,   # Bulky but manageable
        'Palm Fiber': 15             # Moderate density
    }
    
    return transport_costs.get(residue_type, 22)

def get_storage_requirements(residue_type):
    """Get storage requirements"""
    
    storage_reqs = {
        'Rice Husk': 'Covered shed, dry storage',
        'Rice Straw': 'Covered storage, baling required',
        'Maize Cob': 'Ventilated storage, pest control',
        'Maize Stalk': 'Open storage acceptable, chopping required',
        'Maize Husk': 'Covered storage, moisture control',
        'Bagasse': 'Immediate processing or covered storage',
        'Sugarcane Tops': 'Quick processing required, high moisture',
        'Cassava Peels': 'Immediate processing, high moisture',
        'Cassava Stems': 'Drying required, covered storage',
        'Yam Peels': 'Immediate processing, high moisture',
        'Yam Vines': 'Drying required, bulky storage',
        'Sorghum Stalks': 'Covered storage, chopping beneficial',
        'Sorghum Chaff': 'Dry storage, pest control',
        'Millet Stalks': 'Covered storage, chopping required',
        'Millet Chaff': 'Dry storage, pest control',
        'Groundnut Shells': 'Dry storage, pest control',
        'Groundnut Haulms': 'Covered storage, baling beneficial',
        'Cowpea Pods': 'Dry storage, pest control',
        'Cowpea Stalks': 'Covered storage, chopping beneficial',
        'Palm Kernel Shell': 'Covered storage, excellent keeping quality',
        'Empty Fruit Bunches': 'Composting or immediate processing',
        'Palm Fiber': 'Covered storage, moderate keeping quality'
    }
    
    return storage_reqs.get(residue_type, 'Covered storage recommended')

def get_seasonal_availability(production_season):
    """Get seasonal availability pattern"""
    
    if production_season == 'wet':
        return 'Peak: May-October, Limited: November-April'
    elif production_season == 'dry':
        return 'Peak: November-April, Limited: May-October'
    else:  # both seasons
        return 'Year-round availability with two peaks'

def get_moisture_content(residue_type):
    """Get typical moisture content percentage"""
    
    moisture_contents = {
        'Rice Husk': 12, 'Rice Straw': 15, 'Maize Cob': 18, 'Maize Stalk': 25,
        'Maize Husk': 14, 'Bagasse': 50, 'Sugarcane Tops': 70, 'Cassava Peels': 75,
        'Cassava Stems': 60, 'Yam Peels': 80, 'Yam Vines': 65, 'Sorghum Stalks': 20,
        'Sorghum Chaff': 12, 'Millet Stalks': 18, 'Millet Chaff': 10, 'Groundnut Shells': 8,
        'Groundnut Haulms': 22, 'Cowpea Pods': 15, 'Cowpea Stalks': 25, 'Palm Kernel Shell': 7,
        'Empty Fruit Bunches': 65, 'Palm Fiber': 45
    }
    
    return moisture_contents.get(residue_type, 20)

def get_ash_content(residue_type):
    """Get typical ash content percentage"""
    
    ash_contents = {
        'Rice Husk': 18, 'Rice Straw': 12, 'Maize Cob': 2, 'Maize Stalk': 8,
        'Maize Husk': 4, 'Bagasse': 3, 'Sugarcane Tops': 6, 'Cassava Peels': 4,
        'Cassava Stems': 5, 'Yam Peels': 3, 'Yam Vines': 7, 'Sorghum Stalks': 6,
        'Sorghum Chaff': 8, 'Millet Stalks': 7, 'Millet Chaff': 9, 'Groundnut Shells': 3,
        'Groundnut Haulms': 10, 'Cowpea Pods': 5, 'Cowpea Stalks': 8, 'Palm Kernel Shell': 2,
        'Empty Fruit Bunches': 4, 'Palm Fiber': 3
    }
    
    return ash_contents.get(residue_type, 6)

def get_carbon_content(residue_type):
    """Get typical carbon content percentage"""
    
    carbon_contents = {
        'Rice Husk': 38, 'Rice Straw': 42, 'Maize Cob': 46, 'Maize Stalk': 44,
        'Maize Husk': 45, 'Bagasse': 47, 'Sugarcane Tops': 43, 'Cassava Peels': 40,
        'Cassava Stems': 42, 'Yam Peels': 39, 'Yam Vines': 41, 'Sorghum Stalks': 44,
        'Sorghum Chaff': 43, 'Millet Stalks': 43, 'Millet Chaff': 42, 'Groundnut Shells': 48,
        'Groundnut Haulms': 41, 'Cowpea Pods': 45, 'Cowpea Stalks': 43, 'Palm Kernel Shell': 50,
        'Empty Fruit Bunches': 44, 'Palm Fiber': 46
    }
    
    return carbon_contents.get(residue_type, 44)

def get_nitrogen_content(residue_type):
    """Get typical nitrogen content percentage"""
    
    nitrogen_contents = {
        'Rice Husk': 0.5, 'Rice Straw': 0.8, 'Maize Cob': 0.4, 'Maize Stalk': 1.2,
        'Maize Husk': 0.6, 'Bagasse': 0.3, 'Sugarcane Tops': 1.5, 'Cassava Peels': 2.1,
        'Cassava Stems': 1.8, 'Yam Peels': 2.3, 'Yam Vines': 2.0, 'Sorghum Stalks': 0.9,
        'Sorghum Chaff': 1.1, 'Millet Stalks': 0.8, 'Millet Chaff': 1.0, 'Groundnut Shells': 0.7,
        'Groundnut Haulms': 2.5, 'Cowpea Pods': 1.8, 'Cowpea Stalks': 2.2, 'Palm Kernel Shell': 0.4,
        'Empty Fruit Bunches': 0.9, 'Palm Fiber': 0.6
    }
    
    return nitrogen_contents.get(residue_type, 1.2)

def generate_livestock_data():
    """Generate livestock population data for biogas potential"""
    
    # Livestock types and their biogas characteristics
    livestock_types = {
        'Cattle': {
            'manure_production_kg_per_day': 20,
            'biogas_yield_m3_per_kg_manure': 0.04,
            'methane_content_percent': 60,
            'major_states': ['Sokoto', 'Kebbi', 'Katsina', 'Zamfara', 'Kaduna', 'Bauchi']
        },
        'Goats': {
            'manure_production_kg_per_day': 1.5,
            'biogas_yield_m3_per_kg_manure': 0.035,
            'methane_content_percent': 58,
            'major_states': ['Sokoto', 'Katsina', 'Kano', 'Jigawa', 'Bauchi', 'Borno']
        },
        'Sheep': {
            'manure_production_kg_per_day': 2.0,
            'biogas_yield_m3_per_kg_manure': 0.038,
            'methane_content_percent': 59,
            'major_states': ['Sokoto', 'Kebbi', 'Katsina', 'Zamfara', 'Kano', 'Jigawa']
        },
        'Poultry': {
            'manure_production_kg_per_day': 0.15,
            'biogas_yield_m3_per_kg_manure': 0.08,
            'methane_content_percent': 65,
            'major_states': ['Ogun', 'Oyo', 'Lagos', 'Kaduna', 'Kano', 'Rivers']
        },
        'Pigs': {
            'manure_production_kg_per_day': 4.0,
            'biogas_yield_m3_per_kg_manure': 0.06,
            'methane_content_percent': 62,
            'major_states': ['Benue', 'Taraba', 'Plateau', 'Cross River', 'Akwa Ibom', 'Rivers']
        }
    }
    
    # Nigerian states
    all_states = [
        'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa', 'Benue', 'Borno',
        'Cross River', 'Delta', 'Ebonyi', 'Edo', 'Ekiti', 'Enugu', 'FCT', 'Gombe',
        'Imo', 'Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Kogi', 'Kwara',
        'Lagos', 'Nasarawa', 'Niger', 'Ogun', 'Ondo', 'Osun', 'Oyo', 'Plateau',
        'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara'
    ]
    
    livestock_data = []
    
    # Generate annual data for 2020-2024
    for year in range(2020, 2025):
        for livestock_type, livestock_info in livestock_types.items():
            for state in all_states:
                # Base population varies by state and livestock type
                base_population = get_base_livestock_population(livestock_type, state)
                
                # Growth/decline factors
                growth_rate = get_livestock_growth_rate(livestock_type, state)
                years_from_2020 = year - 2020
                current_population = base_population * ((1 + growth_rate) ** years_from_2020)
                
                # Add random annual variation
                annual_variation = np.random.uniform(0.9, 1.1)
                current_population *= annual_variation
                
                # Calculate manure production and biogas potential
                daily_manure_per_animal = livestock_info['manure_production_kg_per_day']
                biogas_yield = livestock_info['biogas_yield_m3_per_kg_manure']
                methane_content = livestock_info['methane_content_percent']
                
                total_daily_manure = current_population * daily_manure_per_animal
                annual_manure = total_daily_manure * 365
                
                # Biogas potential (assuming 70% collection efficiency)
                collection_efficiency = get_manure_collection_efficiency(livestock_type, state)
                collectible_manure = annual_manure * collection_efficiency
                
                annual_biogas_potential = collectible_manure * biogas_yield
                annual_methane_potential = annual_biogas_potential * (methane_content / 100)
                
                # SOFC potential (methane can be reformed to hydrogen)
                sofc_potential_mwh = calculate_livestock_sofc_potential(annual_methane_potential)
                
                livestock_data.append({
                    'year': year,
                    'state': state,
                    'livestock_type': livestock_type,
                    'population': int(current_population),
                    'daily_manure_per_animal_kg': daily_manure_per_animal,
                    'total_daily_manure_tonnes': round(total_daily_manure / 1000, 2),
                    'annual_manure_tonnes': round(annual_manure / 1000, 2),
                    'collection_efficiency_percent': round(collection_efficiency * 100, 1),
                    'collectible_manure_tonnes': round(collectible_manure / 1000, 2),
                    'biogas_yield_m3_per_kg': biogas_yield,
                    'annual_biogas_potential_m3': round(annual_biogas_potential, 2),
                    'methane_content_percent': methane_content,
                    'annual_methane_potential_m3': round(annual_methane_potential, 2),
                    'sofc_potential_mwh_per_year': round(sofc_potential_mwh, 2),
                    'manure_collection_cost_naira_per_tonne': get_manure_collection_cost(livestock_type, state),
                    'biogas_plant_investment_naira_per_m3': get_biogas_plant_cost(),
                    'land_requirement_hectares': get_land_requirement(livestock_type, current_population),
                    'water_requirement_liters_per_day': get_water_requirement(livestock_type, current_population),
                    'feed_requirement_tonnes_per_year': get_feed_requirement(livestock_type, current_population)
                })
    
    return pd.DataFrame(livestock_data)

def get_base_livestock_population(livestock_type, state):
    """Get base livestock population by type and state"""
    
    # Base populations (2020 estimates)
    base_populations = {
        'Cattle': {
            'Sokoto': 2500000, 'Kebbi': 2200000, 'Katsina': 2000000, 'Zamfara': 1800000,
            'Kaduna': 1600000, 'Bauchi': 1400000, 'Kano': 1200000, 'Jigawa': 1000000,
            'Borno': 1500000, 'Yobe': 800000, 'Adamawa': 1300000, 'Taraba': 900000,
            'Plateau': 700000, 'Niger': 1100000, 'FCT': 200000, 'Nasarawa': 600000,
            'Benue': 500000, 'Kwara': 400000, 'Oyo': 300000, 'Osun': 150000,
            'Ondo': 200000, 'Ekiti': 100000, 'Lagos': 50000, 'Ogun': 250000,
            'Delta': 180000, 'Edo': 220000, 'Rivers': 100000, 'Bayelsa': 80000,
            'Cross River': 150000, 'Akwa Ibom': 120000, 'Abia': 100000, 'Imo': 90000,
            'Anambra': 80000, 'Enugu': 110000, 'Ebonyi': 130000, 'Kogi': 350000,
            'Gombe': 600000
        },
        'Goats': {
            'Sokoto': 3000000, 'Katsina': 2800000, 'Kano': 2500000, 'Jigawa': 2200000,
            'Bauchi': 2000000, 'Borno': 2300000, 'Yobe': 1800000, 'Zamfara': 2100000,
            'Kebbi': 1900000, 'Kaduna': 1700000, 'Adamawa': 1600000, 'Taraba': 1200000,
            'Gombe': 1400000, 'Plateau': 800000, 'Niger': 1500000, 'FCT': 300000,
            'Nasarawa': 700000, 'Benue': 600000, 'Kwara': 500000, 'Kogi': 450000,
            'Oyo': 400000, 'Osun': 200000, 'Ondo': 250000, 'Ekiti': 150000,
            'Lagos': 80000, 'Ogun': 300000, 'Delta': 200000, 'Edo': 250000,
            'Rivers': 120000, 'Bayelsa': 100000, 'Cross River': 180000, 'Akwa Ibom': 150000,
            'Abia': 120000, 'Imo': 110000, 'Anambra': 100000, 'Enugu': 130000,
            'Ebonyi': 140000
        },
        'Sheep': {
            'Sokoto': 2200000, 'Kebbi': 2000000, 'Katsina': 1800000, 'Zamfara': 1600000,
            'Kano': 1500000, 'Jigawa': 1400000, 'Bauchi': 1200000, 'Borno': 1300000,
            'Yobe': 1100000, 'Kaduna': 1000000, 'Adamawa': 900000, 'Taraba': 700000,
            'Gombe': 800000, 'Plateau': 400000, 'Niger': 900000, 'FCT': 150000,
            'Nasarawa': 350000, 'Benue': 300000, 'Kwara': 250000, 'Kogi': 200000,
            'Oyo': 180000, 'Osun': 100000, 'Ondo': 120000, 'Ekiti': 80000,
            'Lagos': 30000, 'Ogun': 150000, 'Delta': 80000, 'Edo': 100000,
            'Rivers': 50000, 'Bayelsa': 40000, 'Cross River': 70000, 'Akwa Ibom': 60000,
            'Abia': 50000, 'Imo': 45000, 'Anambra': 40000, 'Enugu': 55000,
            'Ebonyi': 60000
        },
        'Poultry': {
            'Ogun': 15000000, 'Oyo': 12000000, 'Lagos': 10000000, 'Kaduna': 8000000,
            'Kano': 7000000, 'Rivers': 6000000, 'Delta': 5500000, 'Edo': 5000000,
            'Anambra': 4500000, 'Imo': 4000000, 'Abia': 3800000, 'Enugu': 3500000,
            'Cross River': 3200000, 'Akwa Ibom': 3000000, 'Osun': 2800000, 'Ondo': 2500000,
            'Ekiti': 2200000, 'FCT': 2000000, 'Plateau': 1800000, 'Benue': 1600000,
            'Nasarawa': 1400000, 'Kwara': 1200000, 'Kogi': 1000000, 'Niger': 900000,
            'Bauchi': 800000, 'Gombe': 700000, 'Taraba': 600000, 'Adamawa': 550000,
            'Borno': 500000, 'Yobe': 400000, 'Jigawa': 450000, 'Katsina': 500000,
            'Kano': 600000, 'Zamfara': 350000, 'Sokoto': 400000, 'Kebbi': 380000,
            'Bayelsa': 300000, 'Ebonyi': 1500000
        },
        'Pigs': {
            'Benue': 800000, 'Taraba': 600000, 'Plateau': 500000, 'Cross River': 450000,
            'Akwa Ibom': 400000, 'Rivers': 350000, 'Delta': 300000, 'Edo': 280000,
            'Ondo': 250000, 'Ekiti': 200000, 'Ogun': 180000, 'Oyo': 150000,
            'Osun': 120000, 'Lagos': 50000, 'Anambra': 100000, 'Imo': 90000,
            'Abia': 80000, 'Enugu': 70000, 'Ebonyi': 110000, 'Nasarawa': 200000,
            'FCT': 80000, 'Kwara': 60000, 'Kogi': 150000, 'Niger': 100000,
            'Kaduna': 50000, 'Bauchi': 30000, 'Gombe': 25000, 'Adamawa': 80000,
            'Taraba': 120000, 'Borno': 20000, 'Yobe': 15000, 'Jigawa': 10000,
            'Kano': 15000, 'Katsina': 10000, 'Zamfara': 8000, 'Sokoto': 12000,
            'Kebbi': 10000, 'Bayelsa': 40000
        }
    }
    
    livestock_data = base_populations.get(livestock_type, {})
    return livestock_data.get(state, 10000)  # Default for unlisted combinations

def get_livestock_growth_rate(livestock_type, state):
    """Get annual growth rate for livestock population"""
    
    # Base growth rates by livestock type
    base_growth_rates = {
        'Cattle': 0.02,     # 2% annual growth
        'Goats': 0.05,      # 5% annual growth (faster reproduction)
        'Sheep': 0.04,      # 4% annual growth
        'Poultry': 0.08,    # 8% annual growth (commercial expansion)
        'Pigs': 0.03        # 3% annual growth (limited by cultural factors)
    }
    
    base_rate = base_growth_rates.get(livestock_type, 0.03)
    
    # State-specific adjustments
    # Northern states generally better for cattle, goats, sheep
    # Southern states better for poultry, pigs
    northern_states = ['Sokoto', 'Kebbi', 'Katsina', 'Zamfara', 'Kano', 'Jigawa', 'Bauchi', 'Borno', 'Yobe']
    middle_belt = ['Plateau', 'Nasarawa', 'Benue', 'Taraba', 'Adamawa', 'Gombe']
    southern_states = ['Lagos', 'Ogun', 'Oyo', 'Osun', 'Ondo', 'Ekiti', 'Delta', 'Edo', 'Rivers', 'Bayelsa', 
                      'Cross River', 'Akwa Ibom', 'Abia', 'Imo', 'Anambra', 'Enugu', 'Ebonyi']
    
    if livestock_type in ['Cattle', 'Goats', 'Sheep']:
        if state in northern_states:
            return base_rate * 1.2  # Favorable conditions
        elif state in middle_belt:
            return base_rate * 1.0  # Neutral
        else:
            return base_rate * 0.8  # Less favorable
    
    elif livestock_type in ['Poultry', 'Pigs']:
        if state in southern_states:
            return base_rate * 1.1  # Better market access
        elif state in middle_belt:
            return base_rate * 1.0  # Neutral
        else:
            return base_rate * 0.9  # Cultural/market constraints
    
    return base_rate

def get_manure_collection_efficiency(livestock_type, state):
    """Get manure collection efficiency"""
    
    # Base collection efficiencies
    base_efficiencies = {
        'Cattle': 0.3,      # Free-range, difficult collection
        'Goats': 0.2,       # Free-range, scattered
        'Sheep': 0.25,      # Free-range, some herding
        'Poultry': 0.8,     # Confined systems, easy collection
        'Pigs': 0.7         # Confined systems, good collection
    }
    
    base_efficiency = base_efficiencies.get(livestock_type, 0.4)
    
    # State development level affects collection infrastructure
    developed_states = ['Lagos', 'FCT', 'Rivers', 'Kano', 'Kaduna', 'Ogun']
    if state in developed_states:
        return min(base_efficiency * 1.3, 0.9)
    
    return base_efficiency

def calculate_livestock_sofc_potential(annual_methane_m3):
    """Calculate SOFC potential from livestock methane"""
    
    # Methane energy content: 35.8 MJ/m3
    # SOFC efficiency: ~60%
    # 1 MJ = 0.278 kWh
    
    energy_content_mj = annual_methane_m3 * 35.8
    electrical_energy_kwh = energy_content_mj * 0.278 * 0.60  # 60% efficiency
    
    return electrical_energy_kwh / 1000  # Convert to MWh

def get_manure_collection_cost(livestock_type, state):
    """Get manure collection cost in Naira per tonne"""
    
    # Base collection costs
    base_costs = {
        'Cattle': 8000,     # Field collection, transportation
        'Goats': 12000,     # Scattered, difficult collection
        'Sheep': 10000,     # Moderate collection difficulty
        'Poultry': 3000,    # Easy collection from farms
        'Pigs': 4000        # Moderate collection from pens
    }
    
    base_cost = base_costs.get(livestock_type, 6000)
    
    # State cost adjustments
    high_cost_states = ['Lagos', 'FCT', 'Rivers', 'Kano']
    if state in high_cost_states:
        return base_cost * 1.4
    
    return base_cost

def get_biogas_plant_cost():
    """Get biogas plant investment cost per cubic meter capacity"""
    
    # Cost in Naira per m3 of daily biogas capacity
    return np.random.uniform(80000, 120000)

def get_land_requirement(livestock_type, population):
    """Get land requirement in hectares"""
    
    # Land requirements per animal (hectares)
    land_per_animal = {
        'Cattle': 0.5,      # Grazing land
        'Goats': 0.1,       # Less land per animal
        'Sheep': 0.15,      # Moderate land requirement
        'Poultry': 0.001,   # Intensive systems
        'Pigs': 0.01        # Moderate land requirement
    }
    
    land_per = land_per_animal.get(livestock_type, 0.1)
    return population * land_per

def get_water_requirement(livestock_type, population):
    """Get water requirement in liters per day"""
    
    # Water requirements per animal per day (liters)
    water_per_animal = {
        'Cattle': 50,       # High water needs
        'Goats': 5,         # Low water needs
        'Sheep': 8,         # Moderate water needs
        'Poultry': 0.3,     # Low water needs
        'Pigs': 15          # Moderate to high water needs
    }
    
    water_per = water_per_animal.get(livestock_type, 10)
    return population * water_per

def get_feed_requirement(livestock_type, population):
    """Get feed requirement in tonnes per year"""
    
    # Feed requirements per animal per year (tonnes)
    feed_per_animal = {
        'Cattle': 2.5,      # High feed needs (mostly grazing)
        'Goats': 0.4,       # Low feed needs
        'Sheep': 0.6,       # Moderate feed needs
        'Poultry': 0.04,    # Concentrated feed
        'Pigs': 0.8         # Moderate to high feed needs
    }
    
    feed_per = feed_per_animal.get(livestock_type, 0.5)
    return population * feed_per

def main():
    """Generate all renewable resource datasets"""
    
    print("Generating Nigerian Renewable Resources Data...")
    
    # Create output directory
    output_dir = "../raw_data/renewable_resources"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate datasets
    print("1. Generating agricultural waste data...")
    agri_waste_df = generate_agricultural_waste_data()
    agri_waste_df.to_csv(f"{output_dir}/agricultural_waste_data.csv", index=False)
    
    print("2. Generating livestock population data...")
    livestock_df = generate_livestock_data()
    livestock_df.to_csv(f"{output_dir}/livestock_population_data.csv", index=False)
    
    # Generate summary statistics
    print("3. Generating summary statistics...")
    summary_stats = {
        'agricultural_waste': {
            'total_annual_residue_production_million_tonnes': agri_waste_df.groupby('year')['residue_production_tonnes'].sum().mean() / 1000000,
            'total_available_for_energy_million_tonnes': agri_waste_df.groupby('year')['available_for_energy_tonnes'].sum().mean() / 1000000,
            'total_energy_potential_pj': agri_waste_df.groupby('year')['available_energy_potential_gj'].sum().mean() / 1000000,
            'total_biogas_potential_million_m3': agri_waste_df.groupby('year')['biogas_potential_m3'].sum().mean() / 1000000,
            'total_sofc_feedstock_potential_million_tonnes': agri_waste_df.groupby('year')['sofc_feedstock_potential_tonnes'].sum().mean() / 1000000,
            'top_residue_by_volume': agri_waste_df.groupby('residue_type')['residue_production_tonnes'].sum().idxmax(),
            'top_state_by_waste_production': agri_waste_df.groupby('state')['residue_production_tonnes'].sum().idxmax()
        },
        'livestock': {
            'total_cattle_population_millions': livestock_df[livestock_df['livestock_type'] == 'Cattle'].groupby('year')['population'].sum().mean() / 1000000,
            'total_annual_manure_million_tonnes': livestock_df.groupby('year')['annual_manure_tonnes'].sum().mean() / 1000,
            'total_biogas_potential_million_m3': livestock_df.groupby('year')['annual_biogas_potential_m3'].sum().mean() / 1000000,
            'total_sofc_potential_gwh': livestock_df.groupby('year')['sofc_potential_mwh_per_year'].sum().mean() / 1000,
            'top_livestock_state': livestock_df.groupby('state')['population'].sum().idxmax(),
            'most_productive_livestock_type': livestock_df.groupby('livestock_type')['annual_biogas_potential_m3'].sum().idxmax()
        }
    }
    
    with open(f"{output_dir}/summary_statistics.json", 'w') as f:
        json.dump(summary_stats, f, indent=2)
    
    print(f"\nRenewable Resources Data Generation Complete!")
    print(f"Generated {len(agri_waste_df)} agricultural waste records")
    print(f"Generated {len(livestock_df)} livestock population records")
    print(f"\nFiles saved to: {output_dir}/")

if __name__ == "__main__":
    main()