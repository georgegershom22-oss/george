"""
Export SOFC JSON data to CSV format for easier analysis
Author: SOFC Research Team
Date: 2025-10-21
"""

import json
import pandas as pd
from pathlib import Path

def export_performance_data():
    """Export performance characteristics to CSV"""
    with open('../data/raw/sofc_performance_characteristics.json', 'r') as f:
        data = json.load(f)
    
    # Electrical efficiency vs load
    load_data = pd.DataFrame(data['electrical_efficiency']['load_profiles'])
    load_data.to_csv('../data/processed/efficiency_vs_load.csv', index=False)
    
    # Temperature dependency
    temp_data = pd.DataFrame(data['electrical_efficiency']['temperature_dependency'])
    temp_data.to_csv('../data/processed/temperature_dependency.csv', index=False)
    
    # Degradation rates
    deg_data = pd.DataFrame(data['degradation_rates']['degradation_profiles'])
    deg_data.to_csv('../data/processed/degradation_rates.csv', index=False)
    
    # CHP configurations
    chp_data = pd.DataFrame(data['thermal_efficiency']['chp_configurations'])
    chp_data.to_csv('../data/processed/chp_configurations.csv', index=False)
    
    print("✓ Performance data exported to CSV")

def export_fuel_data():
    """Export fuel specifications to CSV"""
    with open('../data/raw/fuel_flexibility_specifications.json', 'r') as f:
        data = json.load(f)
    
    fuel_summary = []
    for fuel_type, fuel_data in data['fuel_types'].items():
        summary = {
            'fuel_type': fuel_type,
            'methane_percent': fuel_data['composition'].get('methane_ch4', 0),
            'co2_percent': fuel_data['composition'].get('carbon_dioxide_co2', 0),
            'lhv_mj_nm3': fuel_data['properties'].get('lower_heating_value_mj_nm3', 0),
            'efficiency_lhv': fuel_data['performance'].get('electrical_efficiency_lhv', 0),
            'fuel_utilization': fuel_data['performance'].get('fuel_utilization', 0)
        }
        fuel_summary.append(summary)
    
    df = pd.DataFrame(fuel_summary)
    df.to_csv('../data/processed/fuel_comparison.csv', index=False)
    
    print("✓ Fuel data exported to CSV")

def export_manufacturer_data():
    """Export manufacturer specifications to CSV"""
    with open('../data/raw/manufacturer_technical_specifications.json', 'r') as f:
        data = json.load(f)
    
    manufacturer_summary = []
    for mfg_name, mfg_data in data['manufacturers'].items():
        for product_name, product_data in mfg_data.get('products', {}).items():
            if isinstance(product_data, dict) and 'power_output_kw' in product_data:
                summary = {
                    'manufacturer': mfg_name,
                    'model': product_data.get('model', ''),
                    'power_kw': product_data.get('power_output_kw', 0),
                    'efficiency_lhv': product_data.get('electrical_efficiency_lhv', 0),
                    'price_usd_kw': product_data.get('price_usd_kw', 0),
                    'warranty_years': product_data.get('warranty_years', 0),
                    'nigeria_rating': mfg_data.get('nigeria_suitability', {}).get('rating', 0)
                }
                manufacturer_summary.append(summary)
    
    df = pd.DataFrame(manufacturer_summary)
    df.to_csv('../data/processed/manufacturer_comparison.csv', index=False)
    
    print("✓ Manufacturer data exported to CSV")

def export_nigeria_scenarios():
    """Export Nigeria operational scenarios to CSV"""
    with open('../data/processed/nigeria_operational_scenarios.json', 'r') as f:
        data = json.load(f)
    
    # Regional demand profiles
    regions = []
    for region, region_data in data['nigeria_power_sector_context']['regional_demand_profiles'].items():
        region_data['region'] = region
        regions.append(region_data)
    
    df_regions = pd.DataFrame(regions)
    df_regions.to_csv('../data/processed/nigeria_regional_demand.csv', index=False)
    
    # Operational scenarios summary
    scenarios = []
    for scenario_name, scenario_data in data['operational_scenarios'].items():
        if 'typical_size_kw' in scenario_data:
            summary = {
                'scenario': scenario_name,
                'size_kw': scenario_data.get('typical_size_kw', 0),
                'description': scenario_data.get('description', '')
            }
            
            # Add performance metrics if available
            if 'performance_metrics' in scenario_data:
                perf = scenario_data['performance_metrics']
                summary['capacity_factor'] = perf.get('capacity_factor', 0)
                summary['efficiency'] = perf.get('electrical_efficiency', 0)
            
            # Add economic parameters if available
            if 'economic_parameters' in scenario_data:
                econ = scenario_data['economic_parameters']
                summary['payback_years'] = econ.get('payback_period_years', 0)
                summary['irr_percent'] = econ.get('irr_percent', 0)
            
            scenarios.append(summary)
    
    df_scenarios = pd.DataFrame(scenarios)
    df_scenarios.to_csv('../data/processed/deployment_scenarios.csv', index=False)
    
    print("✓ Nigeria scenarios exported to CSV")

def export_power_density_data():
    """Export power density data to CSV"""
    with open('../data/raw/power_density_operational_characteristics.json', 'r') as f:
        data = json.load(f)
    
    # Cell-level power density
    cell_types = []
    for cell_type in ['planar_sofc', 'tubular_sofc', 'microtubular_sofc']:
        cell_data = data['power_density']['cell_level'][cell_type]
        for i, current in enumerate(cell_data['current_density_ma_cm2']):
            cell_types.append({
                'cell_type': cell_type,
                'current_density_ma_cm2': current,
                'voltage_v': cell_data['voltage_v'][i],
                'power_density_mw_cm2': cell_data['power_density_mw_cm2'][i],
                'temperature_c': cell_data['operating_temperature_c']
            })
    
    df_cells = pd.DataFrame(cell_types)
    df_cells.to_csv('../data/processed/cell_power_density.csv', index=False)
    
    # System footprints
    systems = []
    for system_name, system_data in data['power_density']['system_level']['footprint'].items():
        system_data['system'] = system_name
        systems.append(system_data)
    
    df_systems = pd.DataFrame(systems)
    df_systems.to_csv('../data/processed/system_footprints.csv', index=False)
    
    print("✓ Power density data exported to CSV")

def main():
    """Main function to export all data to CSV"""
    print("="*50)
    print("Exporting SOFC Data to CSV Format")
    print("="*50)
    
    # Create processed directory if it doesn't exist
    Path('../data/processed').mkdir(exist_ok=True, parents=True)
    
    try:
        export_performance_data()
        export_fuel_data()
        export_manufacturer_data()
        export_nigeria_scenarios()
        export_power_density_data()
        
        print("\n" + "="*50)
        print("✓ All data successfully exported to CSV!")
        print("  Files saved in: data/processed/")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ Error during export: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()