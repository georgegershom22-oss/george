#!/usr/bin/env python3
"""
Nigerian Electricity Grid Data Generator
Generates comprehensive electricity grid datasets for SOFC research analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

# Set random seed for reproducibility
np.random.seed(42)

def generate_generation_capacity_data():
    """Generate national generation capacity data by source"""
    
    # Based on actual Nigerian electricity generation mix
    generation_sources = {
        'Natural Gas': {'installed_mw': 10500, 'available_factor': 0.65, 'efficiency': 0.45},
        'Hydro': {'installed_mw': 2040, 'available_factor': 0.75, 'efficiency': 0.85},
        'Coal': {'installed_mw': 30, 'available_factor': 0.40, 'efficiency': 0.35},
        'Solar': {'installed_mw': 25, 'available_factor': 0.85, 'efficiency': 0.20},
        'Wind': {'installed_mw': 10, 'available_factor': 0.30, 'efficiency': 0.35},
    }
    
    capacity_data = []
    
    # Generate monthly data for 2020-2024
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    current_date = start_date
    while current_date <= end_date:
        for source, specs in generation_sources.items():
            # Add seasonal and maintenance variations
            seasonal_factor = 1.0
            if source == 'Hydro':
                # Hydro varies with rainy season (May-October)
                month = current_date.month
                if 5 <= month <= 10:  # Rainy season
                    seasonal_factor = 1.2
                else:  # Dry season
                    seasonal_factor = 0.6
            elif source == 'Solar':
                # Solar varies with harmattan season
                month = current_date.month
                if 11 <= month <= 2:  # Harmattan season (dusty)
                    seasonal_factor = 0.7
                else:
                    seasonal_factor = 1.0
            
            # Random maintenance outages
            maintenance_factor = np.random.uniform(0.85, 1.0)
            
            installed_capacity = specs['installed_mw']
            available_capacity = installed_capacity * specs['available_factor'] * seasonal_factor * maintenance_factor
            
            capacity_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'source': source,
                'installed_capacity_mw': installed_capacity,
                'available_capacity_mw': round(available_capacity, 2),
                'availability_factor': round(specs['available_factor'] * seasonal_factor * maintenance_factor, 3),
                'efficiency': specs['efficiency'],
                'fuel_cost_naira_per_mwh': get_fuel_cost(source, current_date),
                'capacity_utilization': round(np.random.uniform(0.3, 0.9), 3)
            })
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return pd.DataFrame(capacity_data)

def get_fuel_cost(source, date):
    """Get fuel cost based on source and date"""
    base_costs = {
        'Natural Gas': 15000,  # Naira per MWh
        'Hydro': 2000,
        'Coal': 25000,
        'Solar': 0,
        'Wind': 0
    }
    
    # Add inflation and volatility
    years_since_2020 = (date.year - 2020)
    inflation_factor = (1.15 ** years_since_2020)  # 15% annual inflation
    volatility = np.random.uniform(0.8, 1.2)
    
    return round(base_costs.get(source, 0) * inflation_factor * volatility, 2)

def generate_grid_supply_data():
    """Generate daily load allocation data"""
    
    # Nigerian electricity distribution companies (DisCos)
    discos = [
        'Abuja', 'Benin', 'Eko', 'Enugu', 'Ibadan', 'Ikeja', 
        'Jos', 'Kaduna', 'Kano', 'Port Harcourt', 'Yola'
    ]
    
    supply_data = []
    
    # Generate daily data for 2023-2024
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    current_date = start_date
    while current_date <= end_date:
        # Total national generation varies between 3000-5500 MW
        total_generation = np.random.uniform(3000, 5500)
        
        for disco in discos:
            # Each DisCo gets allocation based on their capacity and demand
            disco_allocation = get_disco_allocation(disco, total_generation, current_date)
            
            supply_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'disco': disco,
                'allocated_mw': round(disco_allocation, 2),
                'peak_demand_mw': round(disco_allocation * np.random.uniform(1.2, 1.8), 2),
                'energy_delivered_mwh': round(disco_allocation * 24 * np.random.uniform(0.7, 0.95), 2),
                'load_rejection_mw': round(disco_allocation * np.random.uniform(0.1, 0.4), 2),
                'technical_losses_percent': round(np.random.uniform(8, 25), 2),
                'commercial_losses_percent': round(np.random.uniform(15, 40), 2)
            })
        
        current_date += timedelta(days=1)
    
    return pd.DataFrame(supply_data)

def get_disco_allocation(disco, total_generation, date):
    """Calculate DisCo allocation based on capacity and regional factors"""
    
    # Base allocation percentages (roughly based on actual Nigerian DisCo sizes)
    base_allocations = {
        'Ikeja': 0.18,      # Lagos (largest)
        'Eko': 0.15,        # Lagos Island
        'Abuja': 0.12,      # Federal Capital Territory
        'Ibadan': 0.11,     # Oyo, Ogun, Osun, Kwara
        'Enugu': 0.10,      # Southeast
        'Port Harcourt': 0.09,  # Rivers, Bayelsa, Akwa Ibom, Cross River
        'Kano': 0.08,       # Kano, Jigawa, Katsina
        'Benin': 0.07,      # Edo, Delta, Ondo, Ekiti
        'Kaduna': 0.06,     # Kaduna, Kebbi, Sokoto, Zamfara
        'Jos': 0.03,        # Plateau, Bauchi, Gombe
        'Yola': 0.01        # Adamawa, Taraba, Borno, Yobe
    }
    
    base_allocation = base_allocations.get(disco, 0.05)
    
    # Add seasonal variations (industrial demand, weather)
    seasonal_factor = 1.0
    month = date.month
    if disco in ['Ikeja', 'Eko', 'Abuja']:  # Commercial centers
        if 3 <= month <= 5 or 10 <= month <= 12:  # Hot seasons
            seasonal_factor = 1.15  # Higher AC demand
    
    # Add random daily variation
    daily_variation = np.random.uniform(0.85, 1.15)
    
    return total_generation * base_allocation * seasonal_factor * daily_variation

def generate_reliability_metrics():
    """Generate grid reliability metrics (SAIDI/SAIFI) by region"""
    
    # Nigerian states grouped by regions
    regions = {
        'North Central': ['FCT', 'Benue', 'Kogi', 'Kwara', 'Nasarawa', 'Niger', 'Plateau'],
        'North East': ['Adamawa', 'Bauchi', 'Borno', 'Gombe', 'Taraba', 'Yobe'],
        'North West': ['Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Sokoto', 'Zamfara'],
        'South East': ['Abia', 'Anambra', 'Ebonyi', 'Enugu', 'Imo'],
        'South South': ['Akwa Ibom', 'Bayelsa', 'Cross River', 'Delta', 'Edo', 'Rivers'],
        'South West': ['Ekiti', 'Lagos', 'Ogun', 'Ondo', 'Osun', 'Oyo']
    }
    
    reliability_data = []
    
    # Generate monthly data for 2020-2024
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    current_date = start_date
    while current_date <= end_date:
        for region, states in regions.items():
            for state in states:
                # Base reliability varies by region (urban vs rural, infrastructure quality)
                base_saidi, base_saifi = get_base_reliability(region, state)
                
                # Add seasonal variations (weather, maintenance)
                seasonal_factor = get_seasonal_reliability_factor(current_date.month, region)
                
                # Random monthly variation
                monthly_variation = np.random.uniform(0.7, 1.3)
                
                saidi = base_saidi * seasonal_factor * monthly_variation
                saifi = base_saifi * seasonal_factor * monthly_variation
                
                reliability_data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'region': region,
                    'state': state,
                    'saidi_hours': round(saidi, 2),
                    'saifi_interruptions': round(saifi, 2),
                    'caidi_hours': round(saidi / saifi if saifi > 0 else 0, 2),
                    'customers_affected': int(np.random.uniform(10000, 500000)),
                    'major_outages': int(np.random.poisson(2)),
                    'grid_availability_percent': round(100 - (saidi / (30 * 24) * 100), 2)
                })
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return pd.DataFrame(reliability_data)

def get_base_reliability(region, state):
    """Get base SAIDI/SAIFI values by region and state"""
    
    # Base values (hours/month for SAIDI, interruptions/month for SAIFI)
    region_factors = {
        'South West': (120, 15),    # Better infrastructure (Lagos, etc.)
        'South South': (180, 20),   # Oil region, better but gas flaring issues
        'North Central': (200, 25), # Mixed urban/rural
        'South East': (220, 28),    # Industrial but aging infrastructure
        'North West': (280, 35),    # Rural, limited infrastructure
        'North East': (320, 40)     # Security challenges, limited infrastructure
    }
    
    # State-specific adjustments
    state_adjustments = {
        'Lagos': 0.6,    # Best infrastructure
        'FCT': 0.7,      # Capital territory
        'Rivers': 0.8,   # Oil hub
        'Kano': 0.9,     # Major northern city
        'Borno': 1.5,    # Security challenges
        'Yobe': 1.4,     # Remote, limited infrastructure
    }
    
    base_saidi, base_saifi = region_factors.get(region, (250, 30))
    adjustment = state_adjustments.get(state, 1.0)
    
    return base_saidi * adjustment, base_saifi * adjustment

def get_seasonal_reliability_factor(month, region):
    """Get seasonal reliability adjustment factor"""
    
    # Rainy season (May-October) generally worse for reliability
    if 5 <= month <= 10:
        if region in ['South South', 'South East', 'South West']:
            return 1.3  # Heavy rains affect infrastructure
        else:
            return 1.1  # Less impact in northern regions
    
    # Harmattan season (November-February) - dust affects equipment
    if 11 <= month <= 2:
        if region in ['North West', 'North East', 'North Central']:
            return 1.2  # Dust storms affect equipment
        else:
            return 0.9  # Less impact in southern regions
    
    return 1.0  # Neutral months

def generate_electricity_tariffs():
    """Generate electricity tariff data by customer class and DisCo"""
    
    discos = [
        'Abuja', 'Benin', 'Eko', 'Enugu', 'Ibadan', 'Ikeja', 
        'Jos', 'Kaduna', 'Kano', 'Port Harcourt', 'Yola'
    ]
    
    customer_classes = ['Residential', 'Commercial', 'Industrial', 'Special']
    
    tariff_data = []
    
    # Generate quarterly tariff data for 2020-2024
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    current_date = start_date
    while current_date <= end_date:
        for disco in discos:
            for customer_class in customer_classes:
                # Base tariffs (Naira per kWh)
                base_tariff = get_base_tariff(customer_class, disco)
                
                # Add inflation and regulatory adjustments
                years_since_2020 = (current_date.year - 2020)
                inflation_factor = (1.12 ** years_since_2020)  # 12% annual increase
                
                # Quarterly adjustments
                quarterly_adjustment = np.random.uniform(0.95, 1.05)
                
                final_tariff = base_tariff * inflation_factor * quarterly_adjustment
                
                tariff_data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'disco': disco,
                    'customer_class': customer_class,
                    'tariff_naira_per_kwh': round(final_tariff, 2),
                    'fixed_charge_naira': get_fixed_charge(customer_class),
                    'vat_percent': 7.5,
                    'regulatory_charge_percent': 1.5,
                    'effective_tariff_naira_per_kwh': round(final_tariff * 1.09, 2)  # Including VAT and charges
                })
        
        # Move to next quarter
        if current_date.month >= 10:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 3)
    
    return pd.DataFrame(tariff_data)

def get_base_tariff(customer_class, disco):
    """Get base tariff by customer class and DisCo"""
    
    # Base tariffs as of 2020 (Naira per kWh)
    base_tariffs = {
        'Residential': 24.30,
        'Commercial': 35.50,
        'Industrial': 30.20,
        'Special': 45.00  # Premium customers with better service
    }
    
    # DisCo-specific adjustments (based on operational costs)
    disco_factors = {
        'Ikeja': 1.1,      # Lagos - higher costs
        'Eko': 1.1,        # Lagos Island - premium area
        'Abuja': 1.05,     # Capital - slightly higher
        'Port Harcourt': 1.0,  # Oil region - subsidized
        'Yola': 0.9,       # Remote - lower base but poor service
        'Jos': 0.95,       # Plateau - moderate costs
    }
    
    base = base_tariffs.get(customer_class, 30.0)
    factor = disco_factors.get(disco, 1.0)
    
    return base * factor

def get_fixed_charge(customer_class):
    """Get monthly fixed charges by customer class"""
    
    fixed_charges = {
        'Residential': 750,    # Naira per month
        'Commercial': 1500,
        'Industrial': 5000,
        'Special': 2500
    }
    
    return fixed_charges.get(customer_class, 1000)

def main():
    """Generate all electricity grid datasets"""
    
    print("Generating Nigerian Electricity Grid Data...")
    
    # Create output directory
    output_dir = "../raw_data/electricity_grid"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate datasets
    print("1. Generating generation capacity data...")
    capacity_df = generate_generation_capacity_data()
    capacity_df.to_csv(f"{output_dir}/generation_capacity_data.csv", index=False)
    
    print("2. Generating grid supply data...")
    supply_df = generate_grid_supply_data()
    supply_df.to_csv(f"{output_dir}/grid_supply_data.csv", index=False)
    
    print("3. Generating reliability metrics...")
    reliability_df = generate_reliability_metrics()
    reliability_df.to_csv(f"{output_dir}/reliability_metrics.csv", index=False)
    
    print("4. Generating electricity tariffs...")
    tariff_df = generate_electricity_tariffs()
    tariff_df.to_csv(f"{output_dir}/electricity_tariffs.csv", index=False)
    
    # Generate summary statistics
    print("5. Generating summary statistics...")
    summary_stats = {
        'generation_capacity': {
            'total_installed_mw': capacity_df.groupby('date')['installed_capacity_mw'].sum().mean(),
            'total_available_mw': capacity_df.groupby('date')['available_capacity_mw'].sum().mean(),
            'average_availability_factor': capacity_df['availability_factor'].mean(),
            'dominant_source': capacity_df.groupby('source')['installed_capacity_mw'].first().idxmax()
        },
        'grid_supply': {
            'average_daily_generation_mw': supply_df.groupby('date')['allocated_mw'].sum().mean(),
            'total_annual_energy_gwh': supply_df['energy_delivered_mwh'].sum() / 1000,
            'average_technical_losses_percent': supply_df['technical_losses_percent'].mean(),
            'average_commercial_losses_percent': supply_df['commercial_losses_percent'].mean()
        },
        'reliability': {
            'national_average_saidi_hours': reliability_df['saidi_hours'].mean(),
            'national_average_saifi': reliability_df['saifi_interruptions'].mean(),
            'best_performing_region': reliability_df.groupby('region')['saidi_hours'].mean().idxmin(),
            'worst_performing_region': reliability_df.groupby('region')['saidi_hours'].mean().idxmax()
        },
        'tariffs': {
            'average_residential_tariff_naira_per_kwh': tariff_df[tariff_df['customer_class'] == 'Residential']['tariff_naira_per_kwh'].mean(),
            'average_industrial_tariff_naira_per_kwh': tariff_df[tariff_df['customer_class'] == 'Industrial']['tariff_naira_per_kwh'].mean(),
            'tariff_growth_rate_percent': 12.0  # Based on inflation factor used
        }
    }
    
    with open(f"{output_dir}/summary_statistics.json", 'w') as f:
        json.dump(summary_stats, f, indent=2)
    
    print(f"\nElectricity Grid Data Generation Complete!")
    print(f"Generated {len(capacity_df)} generation capacity records")
    print(f"Generated {len(supply_df)} grid supply records")
    print(f"Generated {len(reliability_df)} reliability metric records")
    print(f"Generated {len(tariff_df)} tariff records")
    print(f"\nFiles saved to: {output_dir}/")

if __name__ == "__main__":
    main()