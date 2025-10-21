"""
SOFC Technical Data Visualization Scripts for Nigeria Analysis
Author: SOFC Research Team
Date: 2025-10-21
Description: Comprehensive visualization tools for SOFC technical and operational data
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class SOFCDataVisualizer:
    """Main class for visualizing SOFC technical data"""
    
    def __init__(self, data_path="../data/raw"):
        self.data_path = Path(data_path)
        self.load_data()
        
    def load_data(self):
        """Load all JSON data files"""
        self.performance_data = self._load_json("sofc_performance_characteristics.json")
        self.fuel_data = self._load_json("fuel_flexibility_specifications.json")
        self.power_density_data = self._load_json("power_density_operational_characteristics.json")
        self.manufacturer_data = self._load_json("manufacturer_technical_specifications.json")
        self.nigeria_scenarios = self._load_json("../processed/nigeria_operational_scenarios.json")
        
    def _load_json(self, filename):
        """Helper function to load JSON files"""
        file_path = self.data_path / filename
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            print(f"Warning: {filename} not found")
            return {}
    
    def plot_efficiency_curves(self, save_path=None):
        """Plot efficiency vs load curves for SOFC systems"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Electrical efficiency vs load
        load_data = self.performance_data['electrical_efficiency']['load_profiles']
        loads = [d['load_percentage'] for d in load_data]
        eff_lhv = [d['efficiency_lhv'] for d in load_data]
        eff_hhv = [d['efficiency_hhv'] for d in load_data]
        voltage = [d['voltage'] for d in load_data]
        
        axes[0, 0].plot(loads, eff_lhv, 'b-', linewidth=2, label='LHV Efficiency')
        axes[0, 0].plot(loads, eff_hhv, 'r--', linewidth=2, label='HHV Efficiency')
        axes[0, 0].set_xlabel('Load (%)', fontsize=12)
        axes[0, 0].set_ylabel('Efficiency (%)', fontsize=12)
        axes[0, 0].set_title('SOFC Electrical Efficiency vs Load', fontsize=14, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Voltage vs load
        ax2 = axes[0, 0].twinx()
        ax2.plot(loads, voltage, 'g:', linewidth=2, label='Cell Voltage')
        ax2.set_ylabel('Cell Voltage (V)', fontsize=12, color='g')
        ax2.tick_params(axis='y', labelcolor='g')
        
        # Temperature dependency
        temp_data = self.performance_data['electrical_efficiency']['temperature_dependency']
        temps = [d['temperature'] for d in temp_data]
        max_eff = [d['max_efficiency_lhv'] for d in temp_data]
        power_red = [d['power_density_reduction'] for d in temp_data]
        
        axes[0, 1].plot(temps, max_eff, 'b-', linewidth=2, marker='o')
        axes[0, 1].set_xlabel('Operating Temperature (°C)', fontsize=12)
        axes[0, 1].set_ylabel('Max Efficiency LHV (%)', fontsize=12, color='b')
        axes[0, 1].set_title('Temperature Impact on Performance', fontsize=14, fontweight='bold')
        axes[0, 1].tick_params(axis='y', labelcolor='b')
        axes[0, 1].grid(True, alpha=0.3)
        
        ax3 = axes[0, 1].twinx()
        ax3.plot(temps, power_red, 'r--', linewidth=2, marker='s')
        ax3.set_ylabel('Power Density Reduction (%)', fontsize=12, color='r')
        ax3.tick_params(axis='y', labelcolor='r')
        
        # Degradation over time
        deg_data = self.performance_data['degradation_rates']['degradation_profiles']
        periods = [d['period'] for d in deg_data]
        voltage_deg = [d['voltage_degradation_rate'] for d in deg_data]
        power_deg = [d['power_degradation_rate'] for d in deg_data]
        
        x = np.arange(len(periods))
        width = 0.35
        
        axes[1, 0].bar(x - width/2, voltage_deg, width, label='Voltage Degradation', color='blue', alpha=0.7)
        axes[1, 0].bar(x + width/2, power_deg, width, label='Power Degradation', color='red', alpha=0.7)
        axes[1, 0].set_xlabel('Operating Period', fontsize=12)
        axes[1, 0].set_ylabel('Degradation Rate (%/1000h)', fontsize=12)
        axes[1, 0].set_title('SOFC Degradation Rates Over Lifetime', fontsize=14, fontweight='bold')
        axes[1, 0].set_xticks(x)
        axes[1, 0].set_xticklabels(periods, rotation=45, ha='right', fontsize=10)
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # CHP efficiency comparison
        chp_configs = self.performance_data['thermal_efficiency']['chp_configurations']
        configs = [c['configuration'] for c in chp_configs]
        elec_eff = [c['electrical_efficiency'] for c in chp_configs]
        thermal_eff = [c['thermal_recovery'] for c in chp_configs]
        total_eff = [c['total_efficiency'] for c in chp_configs]
        
        x = np.arange(len(configs))
        width = 0.25
        
        axes[1, 1].bar(x - width, elec_eff, width, label='Electrical', color='blue', alpha=0.7)
        axes[1, 1].bar(x, thermal_eff, width, label='Thermal', color='red', alpha=0.7)
        axes[1, 1].bar(x + width, total_eff, width, label='Total', color='green', alpha=0.7)
        axes[1, 1].set_xlabel('CHP Configuration', fontsize=12)
        axes[1, 1].set_ylabel('Efficiency (%)', fontsize=12)
        axes[1, 1].set_title('CHP Configuration Efficiencies', fontsize=14, fontweight='bold')
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels(configs, rotation=45, ha='right', fontsize=10)
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
    def plot_fuel_comparison(self, save_path=None):
        """Create comprehensive fuel comparison visualization"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Fuel Composition Comparison', 
                          'Performance by Fuel Type',
                          'Heating Values Comparison',
                          'Nigeria Fuel Availability'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'pie'}]]
        )
        
        # Fuel composition
        fuels = ['pipeline_natural_gas', 'associated_gas', 'lpg', 'biogas_from_waste']
        components = ['methane_ch4', 'ethane_c2h6', 'propane_c3h8', 'carbon_dioxide_co2']
        colors = ['blue', 'red', 'green', 'orange']
        
        for i, comp in enumerate(components):
            values = []
            for fuel in fuels:
                if fuel in self.fuel_data['fuel_types']:
                    comp_value = self.fuel_data['fuel_types'][fuel]['composition'].get(comp, 0)
                    values.append(comp_value)
                else:
                    values.append(0)
            
            fig.add_trace(
                go.Bar(name=comp, x=fuels, y=values, marker_color=colors[i]),
                row=1, col=1
            )
        
        # Performance comparison
        performance_metrics = ['electrical_efficiency_lhv', 'fuel_utilization']
        for metric in performance_metrics:
            values = []
            for fuel in fuels:
                if fuel in self.fuel_data['fuel_types']:
                    perf_value = self.fuel_data['fuel_types'][fuel]['performance'].get(metric, 0)
                    values.append(perf_value)
                else:
                    values.append(0)
            
            fig.add_trace(
                go.Bar(name=metric, x=fuels, y=values),
                row=1, col=2
            )
        
        # Heating values
        heating_values = []
        fuel_names = []
        for fuel in fuels:
            if fuel in self.fuel_data['fuel_types']:
                props = self.fuel_data['fuel_types'][fuel]['properties']
                if 'lower_heating_value_mj_nm3' in props:
                    heating_values.append(props['lower_heating_value_mj_nm3'])
                    fuel_names.append(fuel)
        
        fig.add_trace(
            go.Bar(x=fuel_names, y=heating_values, marker_color='purple'),
            row=2, col=1
        )
        
        # Nigeria availability pie chart
        availability_data = {
            'Natural Gas': 35,
            'Associated Gas': 40,
            'LPG': 15,
            'Biogas Potential': 10
        }
        
        fig.add_trace(
            go.Pie(labels=list(availability_data.keys()), 
                   values=list(availability_data.values()),
                   hole=0.3),
            row=2, col=2
        )
        
        fig.update_layout(height=800, showlegend=True, 
                         title_text="SOFC Fuel Flexibility Analysis for Nigeria",
                         title_font_size=16)
        fig.update_xaxes(title_text="Fuel Type", row=1, col=1)
        fig.update_xaxes(title_text="Fuel Type", row=1, col=2)
        fig.update_xaxes(title_text="Fuel Type", row=2, col=1)
        fig.update_yaxes(title_text="Composition (%)", row=1, col=1)
        fig.update_yaxes(title_text="Performance (%)", row=1, col=2)
        fig.update_yaxes(title_text="LHV (MJ/Nm³)", row=2, col=1)
        
        if save_path:
            fig.write_html(save_path)
        fig.show()
        
    def plot_power_density_analysis(self, save_path=None):
        """Visualize power density characteristics"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # Cell-level power density curves
        planar = self.power_density_data['power_density']['cell_level']['planar_sofc']
        tubular = self.power_density_data['power_density']['cell_level']['tubular_sofc']
        micro = self.power_density_data['power_density']['cell_level']['microtubular_sofc']
        
        axes[0, 0].plot(planar['current_density_ma_cm2'], planar['power_density_mw_cm2'], 
                       'b-', linewidth=2, marker='o', label='Planar')
        axes[0, 0].plot(tubular['current_density_ma_cm2'], tubular['power_density_mw_cm2'], 
                       'r--', linewidth=2, marker='s', label='Tubular')
        axes[0, 0].plot(micro['current_density_ma_cm2'], micro['power_density_mw_cm2'], 
                       'g:', linewidth=2, marker='^', label='Microtubular')
        axes[0, 0].set_xlabel('Current Density (mA/cm²)', fontsize=12)
        axes[0, 0].set_ylabel('Power Density (mW/cm²)', fontsize=12)
        axes[0, 0].set_title('Cell-Level Power Density Comparison', fontsize=14, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # System footprint comparison
        systems = ['100kw_system', '250kw_system', '1mw_system', '5mw_system']
        power = [100, 250, 1000, 5000]
        area = []
        power_density = []
        
        for sys in systems:
            sys_data = self.power_density_data['power_density']['system_level']['footprint'][sys]
            area.append(sys_data['area_m2'])
            power_density.append(sys_data['power_density_kw_m2'])
        
        axes[0, 1].bar(power, area, color='blue', alpha=0.7)
        axes[0, 1].set_xlabel('System Power (kW)', fontsize=12)
        axes[0, 1].set_ylabel('Footprint (m²)', fontsize=12)
        axes[0, 1].set_title('System Footprint vs Power Rating', fontsize=14, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3)
        
        ax_twin = axes[0, 1].twinx()
        ax_twin.plot(power, power_density, 'r-', linewidth=2, marker='o')
        ax_twin.set_ylabel('Power Density (kW/m²)', fontsize=12, color='r')
        ax_twin.tick_params(axis='y', labelcolor='r')
        
        # Startup characteristics
        startup_stages = self.power_density_data['startup_characteristics']['cold_start']['stages']
        stage_names = [s['stage'] for s in startup_stages]
        durations = [s['duration_minutes'] for s in startup_stages]
        temperatures = [s['temperature_c'] for s in startup_stages]
        
        x = np.arange(len(stage_names))
        axes[0, 2].bar(x, durations, color='green', alpha=0.7)
        axes[0, 2].set_xlabel('Startup Stage', fontsize=12)
        axes[0, 2].set_ylabel('Duration (minutes)', fontsize=12, color='green')
        axes[0, 2].set_title('Cold Start Sequence', fontsize=14, fontweight='bold')
        axes[0, 2].set_xticks(x)
        axes[0, 2].set_xticklabels(stage_names, rotation=45, ha='right', fontsize=10)
        axes[0, 2].tick_params(axis='y', labelcolor='green')
        axes[0, 2].grid(True, alpha=0.3)
        
        ax_temp = axes[0, 2].twinx()
        ax_temp.plot(x, temperatures, 'r-', linewidth=2, marker='o')
        ax_temp.set_ylabel('Temperature (°C)', fontsize=12, color='r')
        ax_temp.tick_params(axis='y', labelcolor='r')
        
        # Ramp rates
        ramp_data = self.power_density_data['ramp_rates']['load_following']['response_time']
        steps = ['10% Step', '50% Step', '100% Step']
        times = [ramp_data['10_percent_step_seconds'], 
                ramp_data['50_percent_step_seconds'], 
                ramp_data['100_percent_step_minutes'] * 60]
        
        axes[1, 0].bar(steps, times, color='purple', alpha=0.7)
        axes[1, 0].set_xlabel('Load Step', fontsize=12)
        axes[1, 0].set_ylabel('Response Time (seconds)', fontsize=12)
        axes[1, 0].set_title('Load Following Response Times', fontsize=14, fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Environmental impact on performance
        temp_impact = self.power_density_data['environmental_conditions_nigeria']['ambient_temperature_impact']
        ambient_temps = [d['ambient_temp_c'] for d in temp_impact]
        power_corr = [d['power_output_correction'] for d in temp_impact]
        eff_corr = [d['efficiency_correction'] for d in temp_impact]
        
        axes[1, 1].plot(ambient_temps, power_corr, 'b-', linewidth=2, marker='o', label='Power Output')
        axes[1, 1].plot(ambient_temps, eff_corr, 'r--', linewidth=2, marker='s', label='Efficiency')
        axes[1, 1].axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
        axes[1, 1].set_xlabel('Ambient Temperature (°C)', fontsize=12)
        axes[1, 1].set_ylabel('Correction Factor', fontsize=12)
        axes[1, 1].set_title('Nigeria Climate Impact on Performance', fontsize=14, fontweight='bold')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        # Operational modes efficiency
        modes = self.power_density_data['operational_modes']
        mode_names = ['Baseload', 'Load Following', 'Peaking', 'CHP Mode']
        mode_keys = ['baseload', 'load_following', 'peaking', 'chp_mode']
        efficiencies = []
        availabilities = []
        
        for key in mode_keys:
            if key in modes:
                if 'efficiency_lhv' in modes[key]:
                    efficiencies.append(modes[key]['efficiency_lhv'])
                elif key == 'chp_mode':
                    efficiencies.append(modes[key]['total_efficiency_percent'])
                else:
                    efficiencies.append(0)
                    
                if 'availability_percent' in modes[key]:
                    availabilities.append(modes[key]['availability_percent'])
                elif key == 'chp_mode':
                    availabilities.append(95)  # Assumed value
                else:
                    availabilities.append(0)
        
        x = np.arange(len(mode_names))
        width = 0.35
        
        axes[1, 2].bar(x - width/2, efficiencies, width, label='Efficiency (%)', color='blue', alpha=0.7)
        axes[1, 2].bar(x + width/2, availabilities, width, label='Availability (%)', color='green', alpha=0.7)
        axes[1, 2].set_xlabel('Operational Mode', fontsize=12)
        axes[1, 2].set_ylabel('Percentage (%)', fontsize=12)
        axes[1, 2].set_title('Performance by Operational Mode', fontsize=14, fontweight='bold')
        axes[1, 2].set_xticks(x)
        axes[1, 2].set_xticklabels(mode_names, rotation=45, ha='right', fontsize=10)
        axes[1, 2].legend()
        axes[1, 2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
    def plot_manufacturer_comparison(self, save_path=None):
        """Create manufacturer comparison visualization"""
        manufacturers = self.manufacturer_data['manufacturers']
        
        # Prepare data for comparison
        mfg_names = []
        efficiencies = []
        power_outputs = []
        prices = []
        nigeria_ratings = []
        
        for mfg, data in manufacturers.items():
            if 'products' in data:
                for product_key, product in data['products'].items():
                    if 'electrical_efficiency_lhv' in product:
                        mfg_names.append(f"{mfg}\n{product['model']}")
                        efficiencies.append(product['electrical_efficiency_lhv'])
                        power_outputs.append(product.get('power_output_kw', 0))
                        prices.append(product.get('price_usd_kw', 0))
                        nigeria_ratings.append(data.get('nigeria_suitability', {}).get('rating', 0))
                        break  # Take first product for comparison
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Electrical Efficiency Comparison',
                          'Power Output Range',
                          'Cost per kW',
                          'Nigeria Suitability Rating'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'scatter'}]]
        )
        
        # Efficiency comparison
        fig.add_trace(
            go.Bar(x=mfg_names[:7], y=efficiencies[:7], marker_color='blue'),
            row=1, col=1
        )
        
        # Power output
        fig.add_trace(
            go.Bar(x=mfg_names[:7], y=power_outputs[:7], marker_color='green'),
            row=1, col=2
        )
        
        # Cost comparison
        fig.add_trace(
            go.Bar(x=mfg_names[:7], y=prices[:7], marker_color='red'),
            row=2, col=1
        )
        
        # Nigeria suitability vs efficiency
        fig.add_trace(
            go.Scatter(x=efficiencies[:7], y=nigeria_ratings[:7], 
                      mode='markers+text',
                      marker=dict(size=15, color=power_outputs[:7], 
                                colorscale='Viridis', showscale=True,
                                colorbar=dict(title="Power (kW)")),
                      text=[name.split('\n')[0] for name in mfg_names[:7]],
                      textposition="top center"),
            row=2, col=2
        )
        
        fig.update_xaxes(title_text="Manufacturer/Model", row=1, col=1)
        fig.update_xaxes(title_text="Manufacturer/Model", row=1, col=2)
        fig.update_xaxes(title_text="Manufacturer/Model", row=2, col=1)
        fig.update_xaxes(title_text="Efficiency (%)", row=2, col=2)
        
        fig.update_yaxes(title_text="Efficiency (%)", row=1, col=1)
        fig.update_yaxes(title_text="Power (kW)", row=1, col=2)
        fig.update_yaxes(title_text="Cost (USD/kW)", row=2, col=1)
        fig.update_yaxes(title_text="Nigeria Rating (0-10)", row=2, col=2)
        
        fig.update_layout(height=800, showlegend=False,
                         title_text="SOFC Manufacturer Comparison for Nigeria Deployment",
                         title_font_size=16)
        
        if save_path:
            fig.write_html(save_path)
        fig.show()
        
    def plot_nigeria_scenarios(self, save_path=None):
        """Visualize Nigeria-specific deployment scenarios"""
        scenarios = self.nigeria_scenarios['operational_scenarios']
        
        # Create comprehensive scenario comparison
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Typical System Sizes by Application',
                          'Economic Performance Indicators',
                          'Capacity Factors by Application',
                          'Fuel Options by Scenario',
                          'Nigeria Regional Demand',
                          'Environmental Benefits'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'pie'}],
                   [{'type': 'bar'}, {'type': 'bar'}]]
        )
        
        # System sizes
        app_names = []
        system_sizes = []
        for scenario_key, scenario in scenarios.items():
            if 'typical_size_kw' in scenario:
                app_names.append(scenario_key.replace('_', ' ').title())
                system_sizes.append(scenario['typical_size_kw'])
            elif 'typical_size_mw' in scenario:
                app_names.append(scenario_key.replace('_', ' ').title())
                system_sizes.append(scenario['typical_size_mw'] * 1000)
        
        fig.add_trace(
            go.Bar(x=app_names[:6], y=system_sizes[:6], marker_color='blue'),
            row=1, col=1
        )
        
        # Economic indicators
        economic_metrics = []
        payback_periods = []
        for scenario_key, scenario in scenarios.items():
            if 'economic_parameters' in scenario:
                econ = scenario['economic_parameters']
                if 'payback_period_years' in econ:
                    economic_metrics.append(scenario_key.replace('_', ' ').title())
                    payback_periods.append(econ['payback_period_years'])
        
        fig.add_trace(
            go.Bar(x=economic_metrics[:4], y=payback_periods[:4], marker_color='green'),
            row=1, col=2
        )
        
        # Capacity factors
        capacity_factors = []
        cf_apps = []
        for scenario_key, scenario in scenarios.items():
            if 'performance_metrics' in scenario:
                perf = scenario['performance_metrics']
                if 'capacity_factor' in perf:
                    cf_apps.append(scenario_key.replace('_', ' ').title())
                    capacity_factors.append(perf['capacity_factor'] * 100)
        
        fig.add_trace(
            go.Bar(x=cf_apps[:4], y=capacity_factors[:4], marker_color='purple'),
            row=2, col=1
        )
        
        # Fuel options pie chart
        fuel_counts = {'Natural Gas': 0, 'Biogas': 0, 'LPG': 0, 'Associated Gas': 0}
        for scenario_key, scenario in scenarios.items():
            if 'fuel_options' in scenario:
                if 'natural_gas' in str(scenario['fuel_options']).lower():
                    fuel_counts['Natural Gas'] += 1
                if 'biogas' in str(scenario['fuel_options']).lower():
                    fuel_counts['Biogas'] += 1
                if 'lpg' in str(scenario['fuel_options']).lower():
                    fuel_counts['LPG'] += 1
                if 'associated' in str(scenario['fuel_options']).lower():
                    fuel_counts['Associated Gas'] += 1
        
        fig.add_trace(
            go.Pie(labels=list(fuel_counts.keys()), values=list(fuel_counts.values())),
            row=2, col=2
        )
        
        # Regional demand
        regions = self.nigeria_scenarios['nigeria_power_sector_context']['regional_demand_profiles']
        region_names = list(regions.keys())
        peak_demands = [regions[r]['peak_demand_mw'] for r in region_names]
        
        fig.add_trace(
            go.Bar(x=region_names, y=peak_demands, marker_color='orange'),
            row=3, col=1
        )
        
        # Environmental benefits (for waste-to-energy)
        if 'waste_to_energy_facility' in scenarios:
            env_benefits = scenarios['waste_to_energy_facility']['environmental_benefits']
            benefits = ['Waste Diverted', 'Methane Avoided', 'CO2 Reduced']
            values = [
                env_benefits['waste_diverted_from_landfill_percent'],
                env_benefits['methane_emissions_avoided_tonnes_year'] / 100,  # Scale for visibility
                env_benefits['co2_equivalent_reduction_tonnes_year'] / 1000  # Scale for visibility
            ]
            
            fig.add_trace(
                go.Bar(x=benefits, y=values, marker_color='teal'),
                row=3, col=2
            )
        
        fig.update_xaxes(title_text="Application", row=1, col=1)
        fig.update_xaxes(title_text="Scenario", row=1, col=2)
        fig.update_xaxes(title_text="Application", row=2, col=1)
        fig.update_xaxes(title_text="Region", row=3, col=1)
        fig.update_xaxes(title_text="Benefit Type", row=3, col=2)
        
        fig.update_yaxes(title_text="System Size (kW)", row=1, col=1)
        fig.update_yaxes(title_text="Payback (years)", row=1, col=2)
        fig.update_yaxes(title_text="Capacity Factor (%)", row=2, col=1)
        fig.update_yaxes(title_text="Peak Demand (MW)", row=3, col=1)
        fig.update_yaxes(title_text="Impact (scaled)", row=3, col=2)
        
        fig.update_layout(height=1200, showlegend=False,
                         title_text="SOFC Deployment Scenarios for Nigeria",
                         title_font_size=16)
        
        if save_path:
            fig.write_html(save_path)
        fig.show()

def main():
    """Main function to generate all visualizations"""
    print("Initializing SOFC Data Visualizer...")
    visualizer = SOFCDataVisualizer()
    
    # Create visualization directory
    viz_dir = Path("../visualizations")
    viz_dir.mkdir(exist_ok=True)
    
    print("\nGenerating efficiency curves...")
    visualizer.plot_efficiency_curves(save_path=viz_dir / "efficiency_curves.png")
    
    print("Generating fuel comparison...")
    visualizer.plot_fuel_comparison(save_path=viz_dir / "fuel_comparison.html")
    
    print("Generating power density analysis...")
    visualizer.plot_power_density_analysis(save_path=viz_dir / "power_density.png")
    
    print("Generating manufacturer comparison...")
    visualizer.plot_manufacturer_comparison(save_path=viz_dir / "manufacturer_comparison.html")
    
    print("Generating Nigeria scenarios...")
    visualizer.plot_nigeria_scenarios(save_path=viz_dir / "nigeria_scenarios.html")
    
    print("\nAll visualizations generated successfully!")
    print(f"Visualizations saved to: {viz_dir.absolute()}")

if __name__ == "__main__":
    main()