#!/usr/bin/env python3
"""
SOFC Analysis Suite for Nigerian Energy Dataset
Comprehensive analysis tools for evaluating SOFC deployment opportunities in Nigeria
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import os
from pathlib import Path

class SOFCAnalyzer:
    """Main class for SOFC feasibility analysis using Nigerian energy data"""
    
    def __init__(self, data_dir="../raw_data"):
        self.data_dir = Path(data_dir)
        self.load_datasets()
        
    def load_datasets(self):
        """Load all datasets for analysis"""
        print("Loading Nigerian Energy Datasets...")
        
        # Electricity Grid Data
        self.generation_capacity = pd.read_csv(self.data_dir / "electricity_grid" / "generation_capacity_data.csv")
        self.grid_supply = pd.read_csv(self.data_dir / "electricity_grid" / "grid_supply_data.csv")
        self.reliability_metrics = pd.read_csv(self.data_dir / "electricity_grid" / "reliability_metrics.csv")
        self.electricity_tariffs = pd.read_csv(self.data_dir / "electricity_grid" / "electricity_tariffs.csv")
        
        # Fossil Fuel Data
        self.gas_reserves = pd.read_csv(self.data_dir / "fossil_fuels" / "gas_reserves_production_data.csv")
        self.gas_flaring = pd.read_csv(self.data_dir / "fossil_fuels" / "gas_flaring_data.csv")
        self.pipeline_network = pd.read_csv(self.data_dir / "fossil_fuels" / "pipeline_network_data.csv")
        self.fuel_prices = pd.read_csv(self.data_dir / "fossil_fuels" / "fuel_prices_data.csv")
        
        # Renewable Resources Data
        self.agricultural_waste = pd.read_csv(self.data_dir / "renewable_resources" / "agricultural_waste_data.csv")
        self.livestock_data = pd.read_csv(self.data_dir / "renewable_resources" / "livestock_population_data.csv")
        
        print("All datasets loaded successfully!")
        
    def analyze_sofc_opportunities(self):
        """Comprehensive SOFC opportunity analysis"""
        
        results = {
            'gas_flaring_opportunities': self.analyze_gas_flaring_sofc(),
            'grid_reliability_gaps': self.analyze_grid_reliability_gaps(),
            'feedstock_availability': self.analyze_feedstock_availability(),
            'economic_feasibility': self.analyze_economic_feasibility(),
            'regional_priorities': self.identify_regional_priorities(),
            'sofc_deployment_scenarios': self.generate_deployment_scenarios()
        }
        
        return results
    
    def analyze_gas_flaring_sofc(self):
        """Analyze SOFC opportunities from gas flaring reduction"""
        
        # Convert date column
        self.gas_flaring['date'] = pd.to_datetime(self.gas_flaring['date'])
        
        # Calculate total flaring and SOFC potential
        flaring_summary = self.gas_flaring.groupby(['site_name', 'operator']).agg({
            'daily_flaring_mmscf': 'mean',
            'sofc_potential_mw': 'mean',
            'co2_emissions_tonnes_per_day': 'mean',
            'distance_to_grid_km': 'mean',
            'local_power_demand_mw': 'mean'
        }).reset_index()
        
        # Rank sites by SOFC potential
        flaring_summary = flaring_summary.sort_values('sofc_potential_mw', ascending=False)
        
        # Calculate total national potential
        total_flaring_mmscf = flaring_summary['daily_flaring_mmscf'].sum()
        total_sofc_potential_mw = flaring_summary['sofc_potential_mw'].sum()
        total_co2_reduction = flaring_summary['co2_emissions_tonnes_per_day'].sum() * 365
        
        # Identify high-priority sites (>10 MW SOFC potential)
        high_priority_sites = flaring_summary[flaring_summary['sofc_potential_mw'] >= 10].copy()
        
        # Calculate economic metrics
        high_priority_sites['annual_energy_mwh'] = high_priority_sites['sofc_potential_mw'] * 8760 * 0.85  # 85% capacity factor
        high_priority_sites['revenue_potential_million_naira'] = (
            high_priority_sites['annual_energy_mwh'] * 35 * 1000  # 35 Naira/kWh average
        ) / 1000000
        
        return {
            'total_flaring_mmscf_per_day': total_flaring_mmscf,
            'total_sofc_potential_mw': total_sofc_potential_mw,
            'annual_co2_reduction_tonnes': total_co2_reduction,
            'high_priority_sites': high_priority_sites.to_dict('records'),
            'top_10_sites': flaring_summary.head(10).to_dict('records')
        }
    
    def analyze_grid_reliability_gaps(self):
        """Analyze grid reliability gaps where SOFC could provide backup power"""
        
        # Convert date column
        self.reliability_metrics['date'] = pd.to_datetime(self.reliability_metrics['date'])
        
        # Calculate average reliability metrics by state
        reliability_summary = self.reliability_metrics.groupby(['state', 'region']).agg({
            'saidi_hours': 'mean',
            'saifi_interruptions': 'mean',
            'grid_availability_percent': 'mean',
            'customers_affected': 'mean'
        }).reset_index()
        
        # Identify states with poor reliability (SAIDI > 200 hours/month)
        poor_reliability_states = reliability_summary[
            reliability_summary['saidi_hours'] > 200
        ].sort_values('saidi_hours', ascending=False)
        
        # Calculate SOFC backup power requirements
        poor_reliability_states['backup_power_need_mw'] = (
            poor_reliability_states['customers_affected'] * 0.002  # 2 kW per customer average
        )
        
        # Estimate market size for backup SOFC systems
        poor_reliability_states['market_size_million_naira'] = (
            poor_reliability_states['backup_power_need_mw'] * 2500000  # 2.5M Naira per MW installed
        ) / 1000000
        
        return {
            'poor_reliability_states': poor_reliability_states.to_dict('records'),
            'total_backup_market_mw': poor_reliability_states['backup_power_need_mw'].sum(),
            'total_market_size_billion_naira': poor_reliability_states['market_size_million_naira'].sum() / 1000
        }
    
    def analyze_feedstock_availability(self):
        """Analyze alternative feedstock availability for SOFC"""
        
        # Agricultural waste analysis
        agri_latest = self.agricultural_waste[self.agricultural_waste['year'] == 2024]
        
        agri_summary = agri_latest.groupby('state').agg({
            'available_for_energy_tonnes': 'sum',
            'sofc_feedstock_potential_tonnes': 'sum',
            'available_energy_potential_gj': 'sum'
        }).reset_index()
        
        # Livestock biogas analysis
        livestock_latest = self.livestock_data[self.livestock_data['year'] == 2024]
        
        livestock_summary = livestock_latest.groupby('state').agg({
            'annual_biogas_potential_m3': 'sum',
            'sofc_potential_mwh_per_year': 'sum',
            'collectible_manure_tonnes': 'sum'
        }).reset_index()
        
        # Combine feedstock sources
        feedstock_combined = pd.merge(agri_summary, livestock_summary, on='state', how='outer').fillna(0)
        
        # Calculate total SOFC potential from alternative feedstocks
        feedstock_combined['total_alternative_sofc_mwh'] = (
            feedstock_combined['sofc_feedstock_potential_tonnes'] * 2.5 +  # 2.5 MWh per tonne biomass
            feedstock_combined['sofc_potential_mwh_per_year']
        )
        
        feedstock_combined['equivalent_capacity_mw'] = (
            feedstock_combined['total_alternative_sofc_mwh'] / (8760 * 0.8)  # 80% capacity factor
        )
        
        # Rank states by feedstock potential
        feedstock_combined = feedstock_combined.sort_values('equivalent_capacity_mw', ascending=False)
        
        return {
            'top_feedstock_states': feedstock_combined.head(15).to_dict('records'),
            'total_biomass_potential_mw': feedstock_combined['equivalent_capacity_mw'].sum(),
            'agricultural_waste_contribution_percent': (
                feedstock_combined['sofc_feedstock_potential_tonnes'].sum() * 2.5 / 
                feedstock_combined['total_alternative_sofc_mwh'].sum() * 100
            ),
            'livestock_contribution_percent': (
                feedstock_combined['sofc_potential_mwh_per_year'].sum() / 
                feedstock_combined['total_alternative_sofc_mwh'].sum() * 100
            )
        }
    
    def analyze_economic_feasibility(self):
        """Analyze economic feasibility of SOFC deployment"""
        
        # Get latest electricity tariffs
        tariffs_latest = self.electricity_tariffs[
            pd.to_datetime(self.electricity_tariffs['date']).dt.year == 2024
        ]
        
        # Calculate average tariffs by customer class
        avg_tariffs = tariffs_latest.groupby('customer_class')['effective_tariff_naira_per_kwh'].mean()
        
        # SOFC cost assumptions (based on current technology)
        sofc_capex_naira_per_kw = 1800000  # 1.8M Naira per kW (decreasing with scale)
        sofc_opex_naira_per_kwh = 8  # 8 Naira per kWh O&M
        sofc_lifetime_years = 20
        capacity_factor = 0.85
        
        # Calculate LCOE for different applications
        lcoe_analysis = {}
        
        for customer_class, tariff in avg_tariffs.items():
            # Calculate LCOE
            annual_generation_kwh = 8760 * capacity_factor
            annual_opex = annual_generation_kwh * sofc_opex_naira_per_kwh
            
            # Simple LCOE calculation (without detailed financial modeling)
            total_capex = sofc_capex_naira_per_kw
            total_lifetime_generation = annual_generation_kwh * sofc_lifetime_years
            total_lifetime_opex = annual_opex * sofc_lifetime_years
            
            lcoe = (total_capex + total_lifetime_opex) / total_lifetime_generation
            
            # Economic metrics
            lcoe_analysis[customer_class] = {
                'average_tariff_naira_per_kwh': tariff,
                'sofc_lcoe_naira_per_kwh': lcoe,
                'economic_viability': 'Viable' if lcoe < tariff else 'Not Viable',
                'tariff_premium_percent': ((tariff - lcoe) / lcoe * 100) if lcoe < tariff else 0,
                'payback_period_years': total_capex / (annual_generation_kwh * (tariff - sofc_opex_naira_per_kwh)) if tariff > sofc_opex_naira_per_kwh else 'N/A'
            }
        
        # Gas flaring opportunity economics
        gas_price_usd_per_mmbtu = 3.5  # Assumed gas price
        gas_price_naira_per_mmbtu = gas_price_usd_per_mmbtu * 800  # Exchange rate
        
        # SOFC efficiency and gas consumption
        sofc_efficiency_lhv = 0.60  # 60% efficiency on LHV basis
        gas_consumption_mmbtu_per_mwh = 3.412 / sofc_efficiency_lhv  # MMBtu per MWh
        
        fuel_cost_naira_per_mwh = gas_consumption_mmbtu_per_mwh * gas_price_naira_per_mmbtu
        
        flaring_economics = {
            'fuel_cost_naira_per_mwh': fuel_cost_naira_per_mwh,
            'total_cost_naira_per_mwh': fuel_cost_naira_per_mwh + (sofc_opex_naira_per_kwh * 1000),
            'revenue_naira_per_mwh': avg_tariffs['Industrial'] * 1000,
            'gross_margin_naira_per_mwh': (avg_tariffs['Industrial'] * 1000) - (fuel_cost_naira_per_mwh + (sofc_opex_naira_per_kwh * 1000)),
            'roi_percent': ((avg_tariffs['Industrial'] * 1000) - (fuel_cost_naira_per_mwh + (sofc_opex_naira_per_kwh * 1000))) / (sofc_capex_naira_per_kw) * 100
        }
        
        return {
            'lcoe_by_customer_class': lcoe_analysis,
            'gas_flaring_economics': flaring_economics,
            'sofc_cost_assumptions': {
                'capex_naira_per_kw': sofc_capex_naira_per_kw,
                'opex_naira_per_kwh': sofc_opex_naira_per_kwh,
                'lifetime_years': sofc_lifetime_years,
                'capacity_factor': capacity_factor
            }
        }
    
    def identify_regional_priorities(self):
        """Identify regional priorities for SOFC deployment"""
        
        # Get latest data for each category
        reliability_latest = self.reliability_metrics[
            pd.to_datetime(self.reliability_metrics['date']).dt.year == 2024
        ]
        
        flaring_latest = self.gas_flaring[
            pd.to_datetime(self.gas_flaring['date']).dt.year == 2024
        ]
        
        # Calculate regional scores
        regional_scores = {}
        
        regions = reliability_latest['region'].unique()
        
        for region in regions:
            # Reliability score (higher SAIDI = higher need for backup power)
            region_reliability = reliability_latest[reliability_latest['region'] == region]
            avg_saidi = region_reliability['saidi_hours'].mean()
            reliability_score = min(avg_saidi / 100, 10)  # Normalize to 0-10 scale
            
            # Gas flaring score (higher flaring = more SOFC opportunity)
            region_states = region_reliability['state'].unique()
            region_flaring = flaring_latest[
                flaring_latest['site_name'].isin(['Escravos', 'Bonny', 'Forcados', 'Brass', 'Qua Iboe'])
            ]  # Major flaring sites
            
            if region == 'South South':  # Oil producing region
                flaring_score = 10
            elif region == 'South West':
                flaring_score = 3
            else:
                flaring_score = 1
            
            # Economic score (based on industrial activity and tariffs)
            if region in ['South West', 'South South']:
                economic_score = 9
            elif region == 'North Central':
                economic_score = 7
            elif region == 'South East':
                economic_score = 6
            else:
                economic_score = 4
            
            # Infrastructure score
            if region == 'South West':
                infrastructure_score = 9
            elif region in ['South South', 'North Central']:
                infrastructure_score = 7
            elif region == 'South East':
                infrastructure_score = 6
            else:
                infrastructure_score = 4
            
            # Composite score
            composite_score = (
                reliability_score * 0.3 +
                flaring_score * 0.3 +
                economic_score * 0.25 +
                infrastructure_score * 0.15
            )
            
            regional_scores[region] = {
                'reliability_score': reliability_score,
                'flaring_score': flaring_score,
                'economic_score': economic_score,
                'infrastructure_score': infrastructure_score,
                'composite_score': composite_score,
                'priority_ranking': 0  # Will be filled after sorting
            }
        
        # Rank regions
        sorted_regions = sorted(regional_scores.items(), key=lambda x: x[1]['composite_score'], reverse=True)
        
        for i, (region, scores) in enumerate(sorted_regions):
            regional_scores[region]['priority_ranking'] = i + 1
        
        return regional_scores
    
    def generate_deployment_scenarios(self):
        """Generate SOFC deployment scenarios"""
        
        scenarios = {
            'conservative': {
                'description': 'Focus on high-certainty opportunities with proven economics',
                'target_capacity_mw': 500,
                'timeline_years': 10,
                'applications': ['Gas flaring sites >20 MW', 'Industrial backup power', 'Critical facilities'],
                'investment_billion_naira': 500 * 1.8,  # 500 MW * 1.8M Naira/kW
                'job_creation': 2500,
                'co2_reduction_tonnes_per_year': 500 * 8760 * 0.85 * 0.5  # 500g CO2/kWh avoided
            },
            'moderate': {
                'description': 'Balanced approach including grid support and distributed generation',
                'target_capacity_mw': 1500,
                'timeline_years': 15,
                'applications': ['All gas flaring sites >5 MW', 'Grid support in unreliable areas', 'Commercial backup', 'Biomass SOFC pilots'],
                'investment_billion_naira': 1500 * 1.8,
                'job_creation': 7500,
                'co2_reduction_tonnes_per_year': 1500 * 8760 * 0.85 * 0.5
            },
            'aggressive': {
                'description': 'Comprehensive SOFC deployment across all viable applications',
                'target_capacity_mw': 3000,
                'timeline_years': 20,
                'applications': ['All gas flaring sites', 'Widespread grid support', 'Biomass SOFC systems', 'Residential backup systems'],
                'investment_billion_naira': 3000 * 1.8,
                'job_creation': 15000,
                'co2_reduction_tonnes_per_year': 3000 * 8760 * 0.85 * 0.5
            }
        }
        
        return scenarios
    
    def generate_visualizations(self, output_dir="../processed_data"):
        """Generate comprehensive visualizations"""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        plt.style.use('seaborn-v0_8')
        
        # 1. Gas Flaring SOFC Potential Map
        fig, ax = plt.subplots(figsize=(12, 8))
        
        flaring_summary = self.gas_flaring.groupby('site_name').agg({
            'sofc_potential_mw': 'mean',
            'latitude': 'first',
            'longitude': 'first'
        }).reset_index()
        
        scatter = ax.scatter(flaring_summary['longitude'], flaring_summary['latitude'], 
                          s=flaring_summary['sofc_potential_mw']*10, 
                          c=flaring_summary['sofc_potential_mw'], 
                          cmap='Reds', alpha=0.7)
        
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title('SOFC Potential from Gas Flaring Sites in Nigeria')
        plt.colorbar(scatter, label='SOFC Potential (MW)')
        
        for i, row in flaring_summary.iterrows():
            ax.annotate(row['site_name'], (row['longitude'], row['latitude']), 
                       xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(output_path / 'gas_flaring_sofc_potential.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Regional Reliability vs SOFC Opportunity
        fig, ax = plt.subplots(figsize=(10, 6))
        
        reliability_summary = self.reliability_metrics.groupby('region')['saidi_hours'].mean().sort_values(ascending=False)
        
        bars = ax.bar(range(len(reliability_summary)), reliability_summary.values)
        ax.set_xlabel('Region')
        ax.set_ylabel('Average SAIDI (Hours/Month)')
        ax.set_title('Grid Reliability by Region - SOFC Backup Opportunity')
        ax.set_xticks(range(len(reliability_summary)))
        ax.set_xticklabels(reliability_summary.index, rotation=45)
        
        # Color bars by severity
        for i, bar in enumerate(bars):
            if reliability_summary.values[i] > 250:
                bar.set_color('red')
            elif reliability_summary.values[i] > 150:
                bar.set_color('orange')
            else:
                bar.set_color('green')
        
        plt.tight_layout()
        plt.savefig(output_path / 'regional_reliability_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Feedstock Availability Heatmap
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Agricultural waste by state
        agri_latest = self.agricultural_waste[self.agricultural_waste['year'] == 2024]
        agri_by_state = agri_latest.groupby('state')['sofc_feedstock_potential_tonnes'].sum().sort_values(ascending=False).head(15)
        
        ax1.barh(range(len(agri_by_state)), agri_by_state.values)
        ax1.set_yticks(range(len(agri_by_state)))
        ax1.set_yticklabels(agri_by_state.index)
        ax1.set_xlabel('SOFC Feedstock Potential (Tonnes/Year)')
        ax1.set_title('Agricultural Waste SOFC Potential by State')
        
        # Livestock biogas by state
        livestock_latest = self.livestock_data[self.livestock_data['year'] == 2024]
        livestock_by_state = livestock_latest.groupby('state')['sofc_potential_mwh_per_year'].sum().sort_values(ascending=False).head(15)
        
        ax2.barh(range(len(livestock_by_state)), livestock_by_state.values)
        ax2.set_yticks(range(len(livestock_by_state)))
        ax2.set_yticklabels(livestock_by_state.index)
        ax2.set_xlabel('SOFC Potential (MWh/Year)')
        ax2.set_title('Livestock Biogas SOFC Potential by State')
        
        plt.tight_layout()
        plt.savefig(output_path / 'feedstock_availability_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Economic Feasibility Analysis
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Get average tariffs by customer class
        tariffs_latest = self.electricity_tariffs[
            pd.to_datetime(self.electricity_tariffs['date']).dt.year == 2024
        ]
        avg_tariffs = tariffs_latest.groupby('customer_class')['effective_tariff_naira_per_kwh'].mean()
        
        # SOFC LCOE estimate
        sofc_lcoe = 45  # Naira per kWh (simplified estimate)
        
        x_pos = range(len(avg_tariffs))
        bars1 = ax.bar([x - 0.2 for x in x_pos], avg_tariffs.values, 0.4, label='Current Tariff', alpha=0.8)
        bars2 = ax.bar([x + 0.2 for x in x_pos], [sofc_lcoe] * len(avg_tariffs), 0.4, label='SOFC LCOE', alpha=0.8)
        
        ax.set_xlabel('Customer Class')
        ax.set_ylabel('Cost (Naira/kWh)')
        ax.set_title('SOFC Economic Feasibility by Customer Class')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(avg_tariffs.index, rotation=45)
        ax.legend()
        
        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{height:.1f}', ha='center', va='bottom')
        
        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{height:.1f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(output_path / 'economic_feasibility_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Visualizations saved to {output_path}/")
    
    def export_analysis_results(self, output_dir="../processed_data"):
        """Export comprehensive analysis results"""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Run full analysis
        results = self.analyze_sofc_opportunities()
        
        # Save results as JSON
        with open(output_path / 'sofc_analysis_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Create executive summary
        summary = {
            'analysis_date': datetime.now().isoformat(),
            'key_findings': {
                'total_gas_flaring_sofc_potential_mw': results['gas_flaring_opportunities']['total_sofc_potential_mw'],
                'high_priority_flaring_sites': len(results['gas_flaring_opportunities']['high_priority_sites']),
                'states_with_poor_grid_reliability': len(results['grid_reliability_gaps']['poor_reliability_states']),
                'total_backup_power_market_mw': results['grid_reliability_gaps']['total_backup_market_mw'],
                'biomass_sofc_potential_mw': results['feedstock_availability']['total_biomass_potential_mw'],
                'economically_viable_customer_classes': [
                    class_name for class_name, metrics in results['economic_feasibility']['lcoe_by_customer_class'].items()
                    if metrics['economic_viability'] == 'Viable'
                ]
            },
            'recommendations': {
                'immediate_opportunities': [
                    'Deploy SOFC at major gas flaring sites (>20 MW potential)',
                    'Pilot SOFC backup systems for industrial customers',
                    'Develop biomass SOFC demonstration projects'
                ],
                'policy_support_needed': [
                    'Gas flaring penalties and SOFC incentives',
                    'Grid code modifications for distributed SOFC',
                    'Biomass supply chain development',
                    'Local content requirements for SOFC manufacturing'
                ],
                'priority_regions': list(results['regional_priorities'].keys())[:3]
            }
        }
        
        with open(output_path / 'sofc_executive_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Analysis results exported to {output_path}/")
        return results

def main():
    """Main analysis execution"""
    
    print("Starting SOFC Analysis Suite for Nigerian Energy Dataset...")
    
    # Initialize analyzer
    analyzer = SOFCAnalyzer()
    
    # Run comprehensive analysis
    results = analyzer.export_analysis_results()
    
    # Generate visualizations
    analyzer.generate_visualizations()
    
    print("\nSOFC Analysis Complete!")
    print(f"Key Findings:")
    print(f"- Total Gas Flaring SOFC Potential: {results['gas_flaring_opportunities']['total_sofc_potential_mw']:.0f} MW")
    print(f"- Grid Backup Market Potential: {results['grid_reliability_gaps']['total_backup_market_mw']:.0f} MW")
    print(f"- Biomass SOFC Potential: {results['feedstock_availability']['total_biomass_potential_mw']:.0f} MW")
    print(f"- High Priority Flaring Sites: {len(results['gas_flaring_opportunities']['high_priority_sites'])}")

if __name__ == "__main__":
    main()