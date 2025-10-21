"""
Data Loader and Processor for Nigerian Energy Datasets
Provides easy access to all energy data with pandas DataFrames
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union

class NigerianEnergyDataLoader:
    """Load and process Nigerian energy datasets"""
    
    def __init__(self, data_path: str = "../"):
        self.data_path = Path(data_path)
        self.data_cache = {}
        
    def load_json(self, file_path: str) -> dict:
        """Load JSON file with caching"""
        if file_path not in self.data_cache:
            with open(self.data_path / file_path, 'r') as f:
                self.data_cache[file_path] = json.load(f)
        return self.data_cache[file_path]
    
    def get_generation_capacity_df(self) -> pd.DataFrame:
        """Get generation capacity as DataFrame"""
        data = self.load_json("electricity_grid/generation_capacity.json")
        
        # Extract plant data
        plants = []
        for source, info in data['national_capacity']['installed_capacity']['by_source'].items():
            if 'plants' in info:
                for plant in info['plants']:
                    plant['source'] = source
                    plants.append(plant)
            elif 'projects' in info:
                for project in info['projects']:
                    project['source'] = source
                    plants.append(project)
        
        return pd.DataFrame(plants)
    
    def get_load_allocation_df(self) -> pd.DataFrame:
        """Get distribution company load allocation data"""
        data = self.load_json("electricity_grid/daily_load_allocation.json")
        return pd.DataFrame(data['distribution_companies'])
    
    def get_reliability_metrics_df(self) -> pd.DataFrame:
        """Get regional reliability metrics"""
        data = self.load_json("electricity_grid/reliability_metrics.json")
        return pd.DataFrame(data['regional_metrics'])
    
    def get_tariff_df(self) -> pd.DataFrame:
        """Get electricity tariffs by customer class"""
        data = self.load_json("electricity_grid/tariffs.json")
        
        tariffs = []
        for customer_class, class_data in data['tariff_classes'].items():
            for tariff_type, tariff_info in class_data.items():
                if 'bands' in tariff_info:
                    for band, band_data in tariff_info['bands'].items():
                        tariffs.append({
                            'customer_class': customer_class,
                            'tariff_type': tariff_type,
                            'band': band,
                            'supply_hours': band_data['supply_hours'],
                            'tariff_ngn_per_kwh': band_data['tariff']
                        })
        
        return pd.DataFrame(tariffs)
    
    def get_gas_reserves_df(self) -> pd.DataFrame:
        """Get gas reserves and production data"""
        data = self.load_json("fossil_fuel/gas_reserves_production.json")
        return pd.DataFrame(data['reserves']['major_gas_fields'])
    
    def get_flaring_sites_df(self) -> pd.DataFrame:
        """Get gas flaring sites data"""
        data = self.load_json("fossil_fuel/gas_flaring_data.json")
        return pd.DataFrame(data['major_flare_sites'])
    
    def get_pipeline_df(self) -> pd.DataFrame:
        """Get gas pipeline infrastructure data"""
        data = self.load_json("fossil_fuel/gas_pipeline_network.json")
        
        pipelines = []
        for pipeline in data['existing_pipelines']['transmission_pipelines']:
            pipelines.append({
                'name': pipeline['name'],
                'operator': pipeline['operator'],
                'length_km': pipeline['length_km'],
                'diameter_inches': pipeline['diameter_inches'],
                'capacity_mmscfd': pipeline['capacity_mmscfd'],
                'current_throughput_mmscfd': pipeline['current_throughput_mmscfd'],
                'origin': pipeline['origin'],
                'destination': pipeline['destination'],
                'status': 'Operational'
            })
        
        for pipeline in data['planned_pipelines']:
            pipelines.append({
                'name': pipeline['name'],
                'operator': pipeline['operator'],
                'length_km': pipeline['length_km'],
                'diameter_inches': pipeline.get('diameter_inches', None),
                'capacity_mmscfd': pipeline.get('capacity_mmscfd', None),
                'current_throughput_mmscfd': 0,
                'origin': pipeline.get('route', [{}])[0].get('from', ''),
                'destination': pipeline.get('route', [{}])[-1].get('to', ''),
                'status': pipeline['status']
            })
        
        return pd.DataFrame(pipelines)
    
    def get_fuel_prices_df(self) -> pd.DataFrame:
        """Get current fuel prices across Nigeria"""
        data = self.load_json("fossil_fuel/fuel_prices.json")
        
        prices = []
        
        # Diesel prices
        for location, info in data['diesel_agb']['regional_prices'].items():
            prices.append({
                'fuel_type': 'Diesel',
                'location': location.replace('_', ' ').title(),
                'price_ngn_per_unit': info['price'],
                'unit': 'liter',
                'availability': info['availability']
            })
        
        # Petrol prices
        for location, info in data['petrol_pms']['regional_prices'].items():
            prices.append({
                'fuel_type': 'Petrol',
                'location': location.replace('_', ' ').title(),
                'price_ngn_per_unit': info['price'],
                'unit': 'liter',
                'availability': 'Available'
            })
        
        # Natural gas prices
        prices.append({
            'fuel_type': 'Natural Gas (Power)',
            'location': 'National',
            'price_ngn_per_unit': data['natural_gas']['domestic_pricing']['power_generation']['price_ngn_per_scm'],
            'unit': 'scm',
            'availability': 'Pipeline areas'
        })
        
        return pd.DataFrame(prices)
    
    def get_agricultural_waste_df(self) -> pd.DataFrame:
        """Get agricultural waste data for biofuel"""
        data = self.load_json("renewable_resources/agricultural_waste_data.json")
        
        wastes = []
        for crop, crop_data in data['major_crops_and_residues'].items():
            for residue_type, residue_data in crop_data['residues'].items():
                wastes.append({
                    'crop': crop,
                    'residue_type': residue_type,
                    'generation_million_tons': residue_data['generation_million_tons_per_year'],
                    'available_million_tons': residue_data['available_for_energy_million_tons'],
                    'energy_content_mj_per_kg': residue_data['energy_content_MJ_per_kg'],
                    'biogas_yield_m3_per_ton': residue_data['biogas_yield_m3_per_ton']
                })
        
        return pd.DataFrame(wastes)
    
    def get_livestock_biogas_df(self) -> pd.DataFrame:
        """Get livestock biogas potential data"""
        data = self.load_json("renewable_resources/livestock_biogas_potential.json")
        
        livestock = []
        for animal, animal_data in data['livestock_population_by_type'].items():
            if isinstance(animal_data, dict) and 'population_millions' in animal_data:
                livestock.append({
                    'animal_type': animal,
                    'population_millions': animal_data['population_millions'],
                    'manure_daily_kg_per_head': animal_data['manure_production']['daily_per_head_kg'],
                    'annual_manure_million_tons': animal_data['manure_production']['annual_total_million_tons'],
                    'biogas_yield_m3_per_ton': animal_data['manure_production']['biogas_yield_m3_per_ton_fresh'],
                    'methane_content_percent': animal_data['manure_production']['methane_content_percent']
                })
        
        return pd.DataFrame(livestock)
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics across all datasets"""
        
        # Load all relevant data
        gen_data = self.load_json("electricity_grid/generation_capacity.json")
        flare_data = self.load_json("fossil_fuel/gas_flaring_data.json")
        agri_data = self.load_json("renewable_resources/agricultural_waste_data.json")
        biogas_data = self.load_json("renewable_resources/livestock_biogas_potential.json")
        
        summary = {
            'electricity': {
                'installed_capacity_mw': gen_data['national_capacity']['installed_capacity']['total'],
                'available_capacity_mw': gen_data['national_capacity']['available_capacity']['average_daily'],
                'capacity_utilization_percent': gen_data['national_capacity']['available_capacity']['capacity_factor'] * 100
            },
            'gas_flaring': {
                'daily_flared_mmscfd': flare_data['national_flaring_statistics']['current_flaring']['total_volume_mmscfd'],
                'annual_value_lost_billion_usd': flare_data['national_flaring_statistics']['current_flaring']['economic_value_lost_usd_billion_per_year'],
                'power_potential_mw': flare_data['national_flaring_statistics']['current_flaring']['power_generation_potential_MW']
            },
            'renewable_potential': {
                'agricultural_waste_power_mw': agri_data['national_crop_production_and_residues']['power_generation_potential_MW'],
                'livestock_biogas_power_mw': biogas_data['national_livestock_statistics']['power_generation_potential_MW'],
                'total_biogas_potential_billion_m3': biogas_data['national_livestock_statistics']['total_biogas_potential_billion_m3_per_year']
            }
        }
        
        return summary
    
    def export_to_excel(self, output_file: str = "nigerian_energy_data.xlsx"):
        """Export all datasets to Excel file"""
        output_path = self.data_path / output_file
        
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            # Generation capacity
            self.get_generation_capacity_df().to_excel(
                writer, sheet_name='Generation_Capacity', index=False)
            
            # Load allocation
            self.get_load_allocation_df().to_excel(
                writer, sheet_name='Load_Allocation', index=False)
            
            # Reliability metrics
            self.get_reliability_metrics_df().to_excel(
                writer, sheet_name='Reliability_Metrics', index=False)
            
            # Tariffs
            self.get_tariff_df().to_excel(
                writer, sheet_name='Electricity_Tariffs', index=False)
            
            # Gas reserves
            self.get_gas_reserves_df().to_excel(
                writer, sheet_name='Gas_Reserves', index=False)
            
            # Flaring sites
            self.get_flaring_sites_df().to_excel(
                writer, sheet_name='Gas_Flaring_Sites', index=False)
            
            # Pipelines
            self.get_pipeline_df().to_excel(
                writer, sheet_name='Gas_Pipelines', index=False)
            
            # Fuel prices
            self.get_fuel_prices_df().to_excel(
                writer, sheet_name='Fuel_Prices', index=False)
            
            # Agricultural waste
            self.get_agricultural_waste_df().to_excel(
                writer, sheet_name='Agricultural_Waste', index=False)
            
            # Livestock biogas
            self.get_livestock_biogas_df().to_excel(
                writer, sheet_name='Livestock_Biogas', index=False)
            
            # Summary statistics
            summary_df = pd.DataFrame([self.get_summary_statistics()])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"Data exported to {output_path}")
        return output_path

# Example usage
if __name__ == "__main__":
    loader = NigerianEnergyDataLoader()
    
    # Load various datasets
    print("Loading generation capacity data...")
    gen_df = loader.get_generation_capacity_df()
    print(f"Total plants/projects: {len(gen_df)}")
    print(f"Total capacity: {gen_df['capacity'].sum():,.0f} MW\n")
    
    print("Loading gas flaring data...")
    flare_df = loader.get_flaring_sites_df()
    print(f"Number of major flare sites: {len(flare_df)}")
    print(f"Total gas flared: {flare_df['flare_volume_mmscfd'].sum():,.0f} MMSCFD\n")
    
    print("Loading agricultural waste data...")
    agri_df = loader.get_agricultural_waste_df()
    print(f"Total waste available: {agri_df['available_million_tons'].sum():,.1f} million tons\n")
    
    print("Getting summary statistics...")
    summary = loader.get_summary_statistics()
    for category, stats in summary.items():
        print(f"\n{category.upper()}:")
        for key, value in stats.items():
            print(f"  {key}: {value:,.2f}")
    
    print("\nExporting all data to Excel...")
    loader.export_to_excel()