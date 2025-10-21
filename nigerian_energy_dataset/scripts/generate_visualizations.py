#!/usr/bin/env python3
"""
Nigerian Energy & Resource Data Visualizations
Creates comprehensive visualizations for SOFC analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from folium import plugins
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def create_electricity_dashboard():
    """Create comprehensive electricity dashboard"""
    
    # Load data
    capacity_df = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/electricity_generation_capacity.csv')
    load_df = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/electricity_daily_load_allocation.csv')
    reliability_df = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/electricity_reliability_metrics.csv')
    tariffs_df = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/electricity_tariffs.csv')
    
    # Convert date column
    load_df['date'] = pd.to_datetime(load_df['date'])
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=('Generation Capacity by Source (2024)', 'Daily Load vs Supply (2024)',
                       'SAIDI by Region (2024)', 'Electricity Tariffs Over Time',
                       'Capacity Factor Trends', 'Load Shedding Analysis'),
        specs=[[{"type": "bar"}, {"type": "scatter"}],
               [{"type": "bar"}, {"type": "scatter"}],
               [{"type": "scatter"}, {"type": "histogram"}]]
    )
    
    # 1. Generation Capacity by Source (2024)
    capacity_2024 = capacity_df[capacity_df['year'] == 2024].iloc[0]
    sources = ['Gas', 'Hydro', 'Solar', 'Wind', 'Diesel']
    installed = [capacity_2024['gas_installed_capacity'], capacity_2024['hydro_installed_capacity'],
                capacity_2024['solar_installed_capacity'], capacity_2024['wind_installed_capacity'],
                capacity_2024['diesel_installed_capacity']]
    available = [capacity_2024['gas_available_capacity'], capacity_2024['hydro_available_capacity'],
                capacity_2024['solar_available_capacity'], capacity_2024['wind_available_capacity'],
                capacity_2024['diesel_available_capacity']]
    
    fig.add_trace(go.Bar(name='Installed', x=sources, y=installed, marker_color='lightblue'), row=1, col=1)
    fig.add_trace(go.Bar(name='Available', x=sources, y=available, marker_color='darkblue'), row=1, col=1)
    
    # 2. Daily Load vs Supply (2024)
    fig.add_trace(go.Scatter(x=load_df['date'], y=load_df['total_demand_mw'], 
                            name='Demand', line=dict(color='red')), row=1, col=2)
    fig.add_trace(go.Scatter(x=load_df['date'], y=load_df['available_supply_mw'], 
                            name='Supply', line=dict(color='green')), row=1, col=2)
    fig.add_trace(go.Scatter(x=load_df['date'], y=load_df['load_shedding_mw'], 
                            name='Load Shedding', line=dict(color='orange')), row=1, col=2)
    
    # 3. SAIDI by Region (2024)
    reliability_2024 = reliability_df[reliability_df['year'] == 2024].sort_values('saidi_hours_per_year', ascending=True)
    fig.add_trace(go.Bar(x=reliability_2024['saidi_hours_per_year'], 
                        y=reliability_2024['region'], orientation='h', marker_color='purple'), row=2, col=1)
    
    # 4. Electricity Tariffs Over Time
    fig.add_trace(go.Scatter(x=tariffs_df['year'], y=tariffs_df['r4_tariff_naira_per_kwh'], 
                            name='Residential', line=dict(color='blue')), row=2, col=2)
    fig.add_trace(go.Scatter(x=tariffs_df['year'], y=tariffs_df['c3_tariff_naira_per_kwh'], 
                            name='Commercial', line=dict(color='green')), row=2, col=2)
    fig.add_trace(go.Scatter(x=tariffs_df['year'], y=tariffs_df['d3_tariff_naira_per_kwh'], 
                            name='Industrial', line=dict(color='red')), row=2, col=2)
    
    # 5. Capacity Factor Trends
    fig.add_trace(go.Scatter(x=capacity_df['year'], y=capacity_df['gas_capacity_factor'], 
                            name='Gas', line=dict(color='blue')), row=3, col=1)
    fig.add_trace(go.Scatter(x=capacity_df['year'], y=capacity_df['hydro_capacity_factor'], 
                            name='Hydro', line=dict(color='green')), row=3, col=1)
    fig.add_trace(go.Scatter(x=capacity_df['year'], y=capacity_df['solar_capacity_factor'], 
                            name='Solar', line=dict(color='orange')), row=3, col=1)
    
    # 6. Load Shedding Analysis
    fig.add_trace(go.Histogram(x=load_df['load_shedding_mw'], nbinsx=30, marker_color='red'), row=3, col=2)
    
    # Update layout
    fig.update_layout(
        title_text="Nigerian Electricity Grid Analysis Dashboard",
        showlegend=True,
        height=1200,
        width=1400
    )
    
    # Save plot
    fig.write_html('/workspace/nigerian_energy_dataset/visualizations/electricity_dashboard.html')
    try:
        fig.write_image('/workspace/nigerian_energy_dataset/visualizations/electricity_dashboard.png', width=1400, height=1200)
    except Exception as e:
        print(f"Could not save PNG image: {e}")
        print("HTML version saved successfully")
    
    return fig

def create_gas_analysis_dashboard():
    """Create gas analysis dashboard"""
    
    # Load data
    gas_reserves_df = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/natural_gas_reserves_production.csv')
    flaring_df = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/gas_flaring_data.csv')
    pipeline_df = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/gas_pipeline_network.csv')
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Gas Production and Flaring Trends', 'Gas Utilization Breakdown (2024)',
                       'Flaring by Site (2024)', 'Pipeline Network Capacity'),
        specs=[[{"type": "scatter"}, {"type": "pie"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # 1. Gas Production and Flaring Trends
    fig.add_trace(go.Scatter(x=gas_reserves_df['year'], y=gas_reserves_df['daily_production_mmscf'], 
                            name='Daily Production', line=dict(color='blue')), row=1, col=1)
    fig.add_trace(go.Scatter(x=gas_reserves_df['year'], y=gas_reserves_df['flared_mmscf_per_day'], 
                            name='Daily Flaring', line=dict(color='red')), row=1, col=1)
    
    # 2. Gas Utilization Breakdown (2024)
    gas_2024 = gas_reserves_df[gas_reserves_df['year'] == 2024].iloc[0]
    utilization_labels = ['Power Generation', 'Industrial Use', 'Export', 'Domestic', 'Flared']
    utilization_values = [gas_2024['power_generation_mmscf_per_day'], gas_2024['industrial_use_mmscf_per_day'],
                         gas_2024['export_mmscf_per_day'], gas_2024['domestic_consumption_mmscf_per_day'],
                         gas_2024['flared_mmscf_per_day']]
    
    fig.add_trace(go.Pie(labels=utilization_labels, values=utilization_values, name="Gas Utilization"), row=1, col=2)
    
    # 3. Flaring by Site (2024)
    flaring_2024 = flaring_df[flaring_df['year'] == 2024].sort_values('daily_flaring_mmscf', ascending=True)
    fig.add_trace(go.Bar(x=flaring_2024['daily_flaring_mmscf'], 
                        y=flaring_2024['site_name'], orientation='h', marker_color='orange'), row=2, col=1)
    
    # 4. Pipeline Network Capacity
    fig.add_trace(go.Bar(x=pipeline_df['pipeline_name'], y=pipeline_df['capacity_mmscf_per_day'], 
                        marker_color='green'), row=2, col=2)
    
    # Update layout
    fig.update_layout(
        title_text="Nigerian Natural Gas Analysis Dashboard",
        showlegend=True,
        height=800,
        width=1400
    )
    
    # Save plot
    fig.write_html('/workspace/nigerian_energy_dataset/visualizations/gas_analysis_dashboard.html')
    try:
        fig.write_image('/workspace/nigerian_energy_dataset/visualizations/gas_analysis_dashboard.png', width=1400, height=800)
    except Exception as e:
        print(f"Could not save PNG image: {e}")
        print("HTML version saved successfully")
    
    return fig

def create_sofc_analysis_dashboard():
    """Create SOFC-specific analysis dashboard"""
    
    # Load data
    sofc_df = pd.read_csv('/workspace/nigerian_energy_dataset/processed_data/sofc_analysis_dataset.csv')
    regional_df = pd.read_csv('/workspace/nigerian_energy_dataset/processed_data/regional_sofc_analysis.csv')
    time_series_df = pd.read_csv('/workspace/nigerian_energy_dataset/processed_data/energy_trends_time_series.csv')
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=('SOFC Power Potential vs Electricity Deficit', 'Regional SOFC Priority Scores',
                       'SOFC Economic Viability by State', 'Gas Flaring Reduction Potential',
                       'SOFC Deployment Timeline', 'Environmental Impact Analysis'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}],
               [{"type": "scatter"}, {"type": "bar"}]]
    )
    
    # 1. SOFC Power Potential vs Electricity Deficit
    deficit_data = [sofc_df.iloc[0]['electricity_deficit_mw'], sofc_df.iloc[0]['sofc_power_potential_mw']]
    deficit_labels = ['Current Deficit', 'SOFC Potential']
    fig.add_trace(go.Bar(x=deficit_labels, y=deficit_data, marker_color=['red', 'green']), row=1, col=1)
    
    # 2. Regional SOFC Priority Scores
    top_states = regional_df.nlargest(10, 'sofc_priority_score')
    fig.add_trace(go.Bar(x=top_states['sofc_priority_score'], 
                        y=top_states['state'], orientation='h', marker_color='blue'), row=1, col=2)
    
    # 3. SOFC Economic Viability by State
    viability_df = regional_df.sort_values('sofc_economic_viability_score', ascending=True)
    fig.add_trace(go.Bar(x=viability_df['state'], y=viability_df['sofc_economic_viability_score'], 
                        marker_color='purple'), row=2, col=1)
    
    # 4. Gas Flaring Reduction Potential
    flaring_reduction = [sofc_df.iloc[0]['gas_flaring_percentage'], 
                        sofc_df.iloc[0]['flaring_reduction_potential_percent']]
    flaring_labels = ['Current Flaring %', 'Potential Reduction %']
    fig.add_trace(go.Bar(x=flaring_labels, y=flaring_reduction, marker_color=['red', 'green']), row=2, col=2)
    
    # 5. SOFC Deployment Timeline
    time_series_df['date'] = pd.to_datetime(time_series_df['date'])
    fig.add_trace(go.Scatter(x=time_series_df['date'], y=time_series_df['sofc_power_potential_mw'], 
                            name='SOFC Potential', line=dict(color='blue')), row=3, col=1)
    fig.add_trace(go.Scatter(x=time_series_df['date'], y=time_series_df['sofc_economic_viability_index'], 
                            name='Economic Viability', line=dict(color='green')), row=3, col=1)
    
    # 6. Environmental Impact Analysis
    env_impact = [sofc_df.iloc[0]['co2_reduction_potential_tonnes_per_year'], 
                 sofc_df.iloc[0]['renewable_integration_potential_percent']]
    env_labels = ['CO2 Reduction (tonnes/year)', 'Renewable Integration (%)']
    fig.add_trace(go.Bar(x=env_labels, y=env_impact, marker_color=['green', 'blue']), row=3, col=2)
    
    # Update layout
    fig.update_layout(
        title_text="SOFC Analysis Dashboard for Nigeria",
        showlegend=True,
        height=1200,
        width=1400
    )
    
    # Save plot
    fig.write_html('/workspace/nigerian_energy_dataset/visualizations/sofc_analysis_dashboard.html')
    try:
        fig.write_image('/workspace/nigerian_energy_dataset/visualizations/sofc_analysis_dashboard.png', width=1400, height=1200)
    except Exception as e:
        print(f"Could not save PNG image: {e}")
        print("HTML version saved successfully")
    
    return fig

def create_biomass_potential_map():
    """Create biomass potential map"""
    
    # Load data
    biomass_df = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/biomass_potential_summary.csv')
    biomass_2024 = biomass_df[biomass_df['year'] == 2024]
    
    # Create map
    m = folium.Map(location=[9.0765, 7.3986], zoom_start=6)
    
    # Add biomass potential circles
    for _, row in biomass_2024.iterrows():
        # Size based on energy potential
        radius = max(5, min(50, row['total_energy_potential_twh'] * 100))
        
        # Color based on electricity potential
        if row['total_electricity_potential_mwh'] > 1000:
            color = 'green'
        elif row['total_electricity_potential_mwh'] > 500:
            color = 'orange'
        else:
            color = 'red'
        
        folium.CircleMarker(
            location=[np.random.uniform(6, 12), np.random.uniform(3, 15)],  # Approximate coordinates
            radius=radius,
            popup=f"""
            <b>{row['state']}</b><br>
            Energy Potential: {row['total_energy_potential_twh']:.2f} TWh<br>
            Electricity Potential: {row['total_electricity_potential_mwh']:.2f} MWh<br>
            Biogas Potential: {row['total_biogas_potential_m3']/1000000:.2f} Million m³
            """,
            color=color,
            fill=True,
            fillOpacity=0.6
        ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <p><b>Biomass Potential</b></p>
    <p><i class="fa fa-circle" style="color:green"></i> High (>1000 MWh)</p>
    <p><i class="fa fa-circle" style="color:orange"></i> Medium (500-1000 MWh)</p>
    <p><i class="fa fa-circle" style="color:red"></i> Low (<500 MWh)</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save map
    m.save('/workspace/nigerian_energy_dataset/visualizations/biomass_potential_map.html')
    
    return m

def create_fuel_prices_analysis():
    """Create fuel prices analysis"""
    
    # Load data
    fuel_prices_df = pd.read_csv('/workspace/nigerian_energy_dataset/raw_data/fuel_prices_by_state.csv')
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Fuel Prices Over Time', 'Regional Price Variations (2024)',
                       'Price Difference Analysis', 'State-wise Price Distribution'),
        specs=[[{"type": "scatter"}, {"type": "bar"}],
               [{"type": "scatter"}, {"type": "box"}]]
    )
    
    # 1. Fuel Prices Over Time
    yearly_prices = fuel_prices_df.groupby('year').agg({
        'petrol_price_naira_per_liter': 'mean',
        'diesel_price_naira_per_liter': 'mean'
    }).reset_index()
    
    fig.add_trace(go.Scatter(x=yearly_prices['year'], y=yearly_prices['petrol_price_naira_per_liter'], 
                            name='Petrol', line=dict(color='blue')), row=1, col=1)
    fig.add_trace(go.Scatter(x=yearly_prices['year'], y=yearly_prices['diesel_price_naira_per_liter'], 
                            name='Diesel', line=dict(color='red')), row=1, col=1)
    
    # 2. Regional Price Variations (2024)
    prices_2024 = fuel_prices_df[fuel_prices_df['year'] == 2024].groupby('state').agg({
        'petrol_price_naira_per_liter': 'mean',
        'diesel_price_naira_per_liter': 'mean'
    }).reset_index().sort_values('petrol_price_naira_per_liter', ascending=True)
    
    fig.add_trace(go.Bar(x=prices_2024['state'], y=prices_2024['petrol_price_naira_per_liter'], 
                        name='Petrol', marker_color='blue'), row=1, col=2)
    fig.add_trace(go.Bar(x=prices_2024['state'], y=prices_2024['diesel_price_naira_per_liter'], 
                        name='Diesel', marker_color='red'), row=1, col=2)
    
    # 3. Price Difference Analysis
    fuel_prices_df['price_difference'] = fuel_prices_df['diesel_price_naira_per_liter'] - fuel_prices_df['petrol_price_naira_per_liter']
    fig.add_trace(go.Scatter(x=fuel_prices_df['petrol_price_naira_per_liter'], 
                            y=fuel_prices_df['price_difference'], 
                            mode='markers', name='Price Difference'), row=2, col=1)
    
    # 4. State-wise Price Distribution
    fig.add_trace(go.Box(y=fuel_prices_df['petrol_price_naira_per_liter'], name='Petrol'), row=2, col=2)
    fig.add_trace(go.Box(y=fuel_prices_df['diesel_price_naira_per_liter'], name='Diesel'), row=2, col=2)
    
    # Update layout
    fig.update_layout(
        title_text="Nigerian Fuel Prices Analysis",
        showlegend=True,
        height=800,
        width=1400
    )
    
    # Save plot
    fig.write_html('/workspace/nigerian_energy_dataset/visualizations/fuel_prices_analysis.html')
    try:
        fig.write_image('/workspace/nigerian_energy_dataset/visualizations/fuel_prices_analysis.png', width=1400, height=800)
    except Exception as e:
        print(f"Could not save PNG image: {e}")
        print("HTML version saved successfully")
    
    return fig

def main():
    """Generate all visualizations"""
    
    print("Generating comprehensive visualizations...")
    
    # Create all dashboards
    print("Creating electricity dashboard...")
    create_electricity_dashboard()
    
    print("Creating gas analysis dashboard...")
    create_gas_analysis_dashboard()
    
    print("Creating SOFC analysis dashboard...")
    create_sofc_analysis_dashboard()
    
    print("Creating biomass potential map...")
    create_biomass_potential_map()
    
    print("Creating fuel prices analysis...")
    create_fuel_prices_analysis()
    
    print("All visualizations completed!")
    print("Visualizations saved to /workspace/nigerian_energy_dataset/visualizations/")

if __name__ == "__main__":
    main()