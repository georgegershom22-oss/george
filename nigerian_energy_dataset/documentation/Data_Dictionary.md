# Nigerian Energy & Resource Dataset - Data Dictionary

## Overview
This document provides detailed descriptions of all variables, datasets, and data structures in the Nigerian Energy & Resource Dataset for SOFC analysis.

## Dataset Categories

### 1. Electricity Grid Data

#### 1.1 Generation Capacity (`electricity_generation_capacity.csv`)

| Variable | Type | Description | Units | Range |
|----------|------|-------------|-------|-------|
| year | Integer | Year of data | - | 2020-2024 |
| gas_installed_capacity | Float | Installed gas power capacity | MW | 8,000-9,200 |
| gas_available_capacity | Float | Available gas power capacity | MW | 4,800-5,600 |
| hydro_installed_capacity | Float | Installed hydro power capacity | MW | 2,100 |
| hydro_available_capacity | Float | Available hydro power capacity | MW | 1,800-2,000 |
| solar_installed_capacity | Float | Installed solar power capacity | MW | 50-300 |
| solar_available_capacity | Float | Available solar power capacity | MW | 45-270 |
| wind_installed_capacity | Float | Installed wind power capacity | MW | 10-30 |
| wind_available_capacity | Float | Available wind power capacity | MW | 8-24 |
| coal_installed_capacity | Float | Installed coal power capacity | MW | 0 |
| coal_available_capacity | Float | Available coal power capacity | MW | 0 |
| diesel_installed_capacity | Float | Installed diesel power capacity | MW | 2,000 |
| diesel_available_capacity | Float | Available diesel power capacity | MW | 1,800 |
| total_installed_capacity | Float | Total installed capacity | MW | 12,160-13,630 |
| total_available_capacity | Float | Total available capacity | MW | 8,651-9,894 |
| gas_capacity_factor | Float | Gas capacity utilization factor | - | 0.60-0.61 |
| hydro_capacity_factor | Float | Hydro capacity utilization factor | - | 0.86-0.95 |
| solar_capacity_factor | Float | Solar capacity utilization factor | - | 0.90 |
| wind_capacity_factor | Float | Wind capacity utilization factor | - | 0.80 |
| diesel_capacity_factor | Float | Diesel capacity utilization factor | - | 0.90 |

#### 1.2 Daily Load Allocation (`electricity_daily_load_allocation.csv`)

| Variable | Type | Description | Units | Range |
|----------|------|-------------|-------|-------|
| date | Date | Date of data | YYYY-MM-DD | 2024-01-01 to 2024-12-31 |
| total_demand_mw | Float | Total electricity demand | MW | 3,500-5,500 |
| available_supply_mw | Float | Available electricity supply | MW | 2,100-4,400 |
| load_shedding_mw | Float | Load shedding amount | MW | 0-1,500 |
| supply_factor | Float | Supply reliability factor | - | 0.60-0.80 |
| lagos_demand_mw | Float | Lagos state demand | MW | 875-1,375 |
| abuja_demand_mw | Float | Abuja demand | MW | 525-825 |
| kano_demand_mw | Float | Kano state demand | MW | 420-660 |
| rivers_demand_mw | Float | Rivers state demand | MW | 350-550 |
| oyo_demand_mw | Float | Oyo state demand | MW | 280-440 |
| kaduna_demand_mw | Float | Kaduna state demand | MW | 245-385 |
| other_states_demand_mw | Float | Other states demand | MW | 805-1,265 |

#### 1.3 Reliability Metrics (`electricity_reliability_metrics.csv`)

| Variable | Type | Description | Units | Range |
|----------|------|-------------|-------|-------|
| region | String | State/region name | - | 35 states |
| year | Integer | Year of data | - | 2020-2024 |
| saidi_hours_per_year | Float | System Average Interruption Duration Index | hours/year | 5-50 |
| saifi_interruptions_per_year | Float | System Average Interruption Frequency Index | interruptions/year | 30-250 |
| avg_duration_hours | Float | Average interruption duration | hours | 0.1-2.0 |
| availability_percent | Float | System availability percentage | % | 50-95 |
| customer_base_thousands | Integer | Customer base in thousands | - | 50-500 |

#### 1.4 Electricity Tariffs (`electricity_tariffs.csv`)

| Variable | Type | Description | Units | Range |
|----------|------|-------------|-------|-------|
| year | Integer | Year of data | - | 2020-2024 |
| r1_tariff_naira_per_kwh | Float | R1 residential tariff | Naira/kWh | 4.0-5.8 |
| r2_tariff_naira_per_kwh | Float | R2 residential tariff | Naira/kWh | 13.0-18.9 |
| r3_tariff_naira_per_kwh | Float | R3 residential tariff | Naira/kWh | 13.0-18.9 |
| r4_tariff_naira_per_kwh | Float | R4 residential tariff | Naira/kWh | 13.0-18.9 |
| c1_tariff_naira_per_kwh | Float | C1 commercial tariff | Naira/kWh | 13.0-18.9 |
| c2_tariff_naira_per_kwh | Float | C2 commercial tariff | Naira/kWh | 13.0-18.9 |
| c3_tariff_naira_per_kwh | Float | C3 commercial tariff | Naira/kWh | 13.0-18.9 |
| d1_tariff_naira_per_kwh | Float | D1 industrial tariff | Naira/kWh | 13.0-18.9 |
| d2_tariff_naira_per_kwh | Float | D2 industrial tariff | Naira/kWh | 13.0-18.9 |
| d3_tariff_naira_per_kwh | Float | D3 industrial tariff | Naira/kWh | 13.0-18.9 |
| a1_tariff_naira_per_kwh | Float | A1 special tariff | Naira/kWh | 13.0-18.9 |
| a2_tariff_naira_per_kwh | Float | A2 special tariff | Naira/kWh | 13.0-18.9 |
| a3_tariff_naira_per_kwh | Float | A3 special tariff | Naira/kWh | 13.0-18.9 |
| premium_residential_tariff_naira_per_kwh | Float | Premium residential tariff | Naira/kWh | 19.5-28.4 |
| premium_commercial_tariff_naira_per_kwh | Float | Premium commercial tariff | Naira/kWh | 19.5-28.4 |
| premium_industrial_tariff_naira_per_kwh | Float | Premium industrial tariff | Naira/kWh | 19.5-28.4 |

### 2. Fossil Fuel Data

#### 2.1 Natural Gas Reserves & Production (`natural_gas_reserves_production.csv`)

| Variable | Type | Description | Units | Range |
|----------|------|-------------|-------|-------|
| year | Integer | Year of data | - | 2020-2024 |
| proven_reserves_tcf | Float | Proven gas reserves | Tcf | 200-208 |
| daily_production_mmscf | Float | Daily gas production | MMscf/day | 3,000-3,200 |
| annual_production_mmscf | Float | Annual gas production | MMscf/year | 1,095,000-1,168,000 |
| power_generation_mmscf_per_day | Float | Gas for power generation | MMscf/day | 1,050-1,120 |
| industrial_use_mmscf_per_day | Float | Gas for industrial use | MMscf/day | 750-800 |
| export_mmscf_per_day | Float | Gas for export | MMscf/day | 600-640 |
| domestic_consumption_mmscf_per_day | Float | Domestic gas consumption | MMscf/day | 450-480 |
| flared_mmscf_per_day | Float | Gas flared daily | MMscf/day | 150-160 |
| niger_delta_reserves_tcf | Float | Niger Delta reserves | Tcf | 140-146 |
| anambra_basin_reserves_tcf | Float | Anambra Basin reserves | Tcf | 30-31 |
| sokoto_basin_reserves_tcf | Float | Sokoto Basin reserves | Tcf | 20-21 |
| other_reserves_tcf | Float | Other reserves | Tcf | 10-10 |
| reserves_to_production_ratio_years | Float | Reserves to production ratio | years | 182-190 |

#### 2.2 Gas Flaring Data (`gas_flaring_data.csv`)

| Variable | Type | Description | Units | Range |
|----------|------|-------------|-------|-------|
| site_name | String | Flare site name | - | 10 major sites |
| state | String | State location | - | Rivers, Delta, Bayelsa, etc. |
| latitude | Float | Site latitude | degrees | 4.3-6.2 |
| longitude | Float | Site longitude | degrees | 5.1-7.9 |
| year | Integer | Year of data | - | 2020-2024 |
| daily_flaring_mmscf | Float | Daily flaring amount | MMscf/day | 5-120 |
| annual_flaring_mmscf | Float | Annual flaring amount | MMscf/year | 1,825-43,800 |
| co2_emissions_tonnes | Float | CO2 emissions | tonnes/year | 4.6-109.5 |
| economic_value_lost_usd_millions | Float | Economic value lost | USD millions | 5.5-131.4 |
| site_capacity_mmscf_per_day | Integer | Site flaring capacity | MMscf/day | 20-150 |

#### 2.3 Gas Pipeline Network (`gas_pipeline_network.csv`)

| Variable | Type | Description | Units | Range |
|----------|------|-------------|-------|-------|
| pipeline_name | String | Pipeline name | - | 6 major pipelines |
| start_location | String | Start location | - | Various cities |
| end_location | String | End location | - | Various cities |
| length_km | Integer | Pipeline length | km | 50-678 |
| diameter_inches | Integer | Pipeline diameter | inches | 20-48 |
| capacity_mmscf_per_day | Integer | Pipeline capacity | MMscf/day | 200-2,000 |
| status | String | Pipeline status | - | Operational, Under Construction |
| commission_year | Integer | Commission year | - | 1965-2024 |
| start_lat | Float | Start latitude | degrees | 4.3-7.5 |
| start_lon | Float | Start longitude | degrees | 3.4-6.7 |
| end_lat | Float | End latitude | degrees | 5.6-12.0 |
| end_lon | Float | End longitude | degrees | -0.2-8.5 |

#### 2.4 Fuel Prices (`fuel_prices_by_state.csv`)

| Variable | Type | Description | Units | Range |
|----------|------|-------------|-------|-------|
| state | String | State name | - | 37 states + FCT |
| year | Integer | Year of data | - | 2020-2024 |
| month | Integer | Month of data | - | 1-12 |
| petrol_price_naira_per_liter | Float | Petrol price | Naira/liter | 145-250 |
| diesel_price_naira_per_liter | Float | Diesel price | Naira/liter | 160-280 |
| price_difference_naira | Float | Price difference | Naira/liter | 15-30 |

### 3. Renewable Resource Data

#### 3.1 Agricultural Waste (`agricultural_waste_data.csv`)

| Variable | Type | Description | Units | Range |
|----------|------|-------------|-------|-------|
| state | String | State name | - | 37 states + FCT |
| year | Integer | Year of data | - | 2020-2024 |
| crop | String | Crop type | - | 13 crop types |
| crop_production_tonnes | Float | Crop production | tonnes/year | 1,000-500,000 |
| residue_production_tonnes | Float | Residue production | tonnes/year | 600-1,100,000 |
| dry_residue_tonnes | Float | Dry residue amount | tonnes/year | 480-880,000 |
| energy_content_mj_per_kg | Float | Energy content | MJ/kg | 13.8-20.5 |
| moisture_content | Float | Moisture content | - | 0.08-0.25 |
| energy_potential_gj | Float | Energy potential | GJ/year | 6,624-18,040,000 |
| biogas_potential_m3 | Float | Biogas potential | m³/year | 96,000-176,000,000 |
| electricity_potential_kwh | Float | Electricity potential | kWh/year | 192,000-352,000,000 |

#### 3.2 Livestock Population (`livestock_population_data.csv`)

| Variable | Type | Description | Units | Range |
|----------|------|-------------|-------|-------|
| state | String | State name | - | 37 states + FCT |
| year | Integer | Year of data | - | 2020-2024 |
| livestock_type | String | Livestock type | - | 7 types |
| population_thousands | Float | Population | thousands | 100-100,000 |
| daily_manure_production_kg | Float | Daily manure production | kg/day | 10-1,250,000 |
| annual_manure_production_tonnes | Float | Annual manure production | tonnes/year | 3,650-456,250,000 |
| daily_biogas_potential_m3 | Float | Daily biogas potential | m³/day | 4-500,000 |
| annual_biogas_potential_m3 | Float | Annual biogas potential | m³/year | 1,460-182,500,000 |
| annual_methane_production_m3 | Float | Annual methane production | m³/year | 876-109,500,000 |
| annual_electricity_potential_kwh | Float | Annual electricity potential | kWh/year | 2,920-365,000,000 |
| annual_energy_potential_gj | Float | Annual energy potential | GJ/year | 29.2-7,300,000 |
| methane_content | Float | Methane content | - | 0.6-0.7 |

#### 3.3 Biomass Potential Summary (`biomass_potential_summary.csv`)

| Variable | Type | Description | Units | Range |
|----------|------|-------------|-------|-------|
| state | String | State name | - | 37 states + FCT |
| year | Integer | Year of data | - | 2020-2024 |
| energy_potential_gj | Float | Agricultural energy potential | GJ/year | 0-18,040,000 |
| biogas_potential_m3 | Float | Agricultural biogas potential | m³/year | 0-176,000,000 |
| electricity_potential_kwh | Float | Agricultural electricity potential | kWh/year | 0-352,000,000 |
| annual_energy_potential_gj | Float | Livestock energy potential | GJ/year | 0-7,300,000 |
| annual_biogas_potential_m3 | Float | Livestock biogas potential | m³/year | 0-182,500,000 |
| annual_electricity_potential_kwh | Float | Livestock electricity potential | kWh/year | 0-365,000,000 |
| total_energy_potential_gj | Float | Total energy potential | GJ/year | 0-25,340,000 |
| total_biogas_potential_m3 | Float | Total biogas potential | m³/year | 0-358,500,000 |
| total_electricity_potential_kwh | Float | Total electricity potential | kWh/year | 0-717,000,000 |
| total_energy_potential_twh | Float | Total energy potential | TWh/year | 0-7.04 |
| total_electricity_potential_mwh | Float | Total electricity potential | MWh/year | 0-717,000 |

### 4. SOFC Analysis Datasets

#### 4.1 SOFC Analysis Dataset (`sofc_analysis_dataset.csv`)

| Variable | Type | Description | Units | Range |
|----------|------|-------------|-------|-------|
| analysis_year | Integer | Analysis year | - | 2024 |
| total_installed_capacity_mw | Float | Total installed capacity | MW | 13,630 |
| total_available_capacity_mw | Float | Total available capacity | MW | 9,894 |
| gas_installed_capacity_mw | Float | Gas installed capacity | MW | 9,200 |
| gas_available_capacity_mw | Float | Gas available capacity | MW | 5,600 |
| gas_capacity_factor | Float | Gas capacity factor | - | 0.61 |
| average_daily_demand_mw | Float | Average daily demand | MW | 4,500 |
| average_daily_supply_mw | Float | Average daily supply | MW | 2,925 |
| average_load_shedding_mw | Float | Average load shedding | MW | 1,575 |
| supply_reliability_percent | Float | Supply reliability | % | 65 |
| average_saidi_hours | Float | Average SAIDI | hours/year | 20 |
| average_saifi_interruptions | Float | Average SAIFI | interruptions/year | 100 |
| average_availability_percent | Float | Average availability | % | 75 |
| residential_tariff_naira_per_kwh | Float | Residential tariff | Naira/kWh | 18.9 |
| commercial_tariff_naira_per_kwh | Float | Commercial tariff | Naira/kWh | 18.9 |
| industrial_tariff_naira_per_kwh | Float | Industrial tariff | Naira/kWh | 18.9 |
| proven_gas_reserves_tcf | Float | Proven gas reserves | Tcf | 208 |
| daily_gas_production_mmscf | Float | Daily gas production | MMscf/day | 3,200 |
| annual_gas_production_mmscf | Float | Annual gas production | MMscf/year | 1,168,000 |
| gas_for_power_mmscf_per_day | Float | Gas for power | MMscf/day | 1,120 |
| gas_flaring_mmscf_per_day | Float | Gas flaring | MMscf/day | 160 |
| gas_flaring_percentage | Float | Gas flaring percentage | % | 5 |
| total_flaring_sites | Integer | Total flaring sites | - | 10 |
| total_flaring_annual_mmscf | Float | Total annual flaring | MMscf/year | 58,400 |
| total_co2_emissions_tonnes | Float | Total CO2 emissions | tonnes/year | 146,000 |
| economic_value_lost_usd_millions | Float | Economic value lost | USD millions | 175.2 |
| total_pipelines | Integer | Total pipelines | - | 6 |
| operational_pipelines | Integer | Operational pipelines | - | 5 |
| total_pipeline_length_km | Float | Total pipeline length | km | 2,200 |
| total_pipeline_capacity_mmscf_per_day | Float | Total pipeline capacity | MMscf/day | 5,700 |
| average_petrol_price_naira_per_liter | Float | Average petrol price | Naira/liter | 200 |
| average_diesel_price_naira_per_liter | Float | Average diesel price | Naira/liter | 220 |
| price_difference_naira_per_liter | Float | Price difference | Naira/liter | 20 |
| total_biomass_energy_potential_twh | Float | Total biomass energy potential | TWh/year | 2.5 |
| total_biomass_electricity_potential_mwh | Float | Total biomass electricity potential | MWh/year | 500,000 |
| total_biomass_biogas_potential_million_m3 | Float | Total biomass biogas potential | Million m³/year | 180 |
| sofc_gas_availability_mmscf_per_day | Float | SOFC gas availability | MMscf/day | 1,280 |
| sofc_power_potential_mw | Float | SOFC power potential | MW | 640 |
| sofc_efficiency_estimate_percent | Float | SOFC efficiency estimate | % | 60 |
| sofc_capital_cost_per_mw_usd | Float | SOFC capital cost | USD/MW | 3,000,000 |
| sofc_operating_cost_per_mwh_usd | Float | SOFC operating cost | USD/MWh | 50 |
| sofc_lifetime_years | Integer | SOFC lifetime | years | 20 |
| electricity_deficit_mw | Float | Electricity deficit | MW | 1,575 |
| deficit_percentage | Float | Deficit percentage | % | 35 |
| sofc_potential_deficit_reduction_percent | Float | SOFC deficit reduction potential | % | 43 |
| co2_reduction_potential_tonnes_per_year | Float | CO2 reduction potential | tonnes/year | 116,800 |
| flaring_reduction_potential_percent | Float | Flaring reduction potential | % | 80 |
| renewable_integration_potential_percent | Float | Renewable integration potential | % | 15 |

#### 4.2 Regional SOFC Analysis (`regional_sofc_analysis.csv`)

| Variable | Type | Description | Units | Range |
|----------|------|-------------|-------|-------|
| state | String | State name | - | 34 states |
| year | Integer | Year of data | - | 2024 |
| saidi_hours_per_year | Float | SAIDI | hours/year | 5-50 |
| saifi_interruptions_per_year | Float | SAIFI | interruptions/year | 30-250 |
| availability_percent | Float | Availability | % | 50-95 |
| customer_base_thousands | Integer | Customer base | thousands | 50-500 |
| avg_petrol_price_naira_per_liter | Float | Average petrol price | Naira/liter | 150-250 |
| avg_diesel_price_naira_per_liter | Float | Average diesel price | Naira/liter | 170-270 |
| biomass_energy_potential_twh | Float | Biomass energy potential | TWh/year | 0-0.5 |
| biomass_electricity_potential_mwh | Float | Biomass electricity potential | MWh/year | 0-1,000 |
| daily_flaring_mmscf | Float | Daily flaring | MMscf/day | 0-50 |
| annual_flaring_mmscf | Float | Annual flaring | MMscf/year | 0-18,250 |
| co2_emissions_tonnes | Float | CO2 emissions | tonnes/year | 0-45,625 |
| economic_value_lost_usd_millions | Float | Economic value lost | USD millions | 0-54.75 |
| sofc_priority_score | Integer | SOFC priority score | - | 4-10 |
| sofc_gas_availability_mmscf_per_day | Float | SOFC gas availability | MMscf/day | 0-50 |
| sofc_power_potential_mw | Float | SOFC power potential | MW | 0-25 |
| sofc_economic_viability_score | Integer | SOFC economic viability score | - | 1-3 |

#### 4.3 Energy Trends Time Series (`energy_trends_time_series.csv`)

| Variable | Type | Description | Units | Range |
|----------|------|-------------|-------|-------|
| year | Integer | Year of data | - | 2020-2024 |
| month | Integer | Month of data | - | 1-12 |
| date | String | Date | YYYY-MM-DD | 2020-01-01 to 2024-12-01 |
| total_installed_capacity_mw | Float | Total installed capacity | MW | 12,160-13,630 |
| total_available_capacity_mw | Float | Total available capacity | MW | 8,651-9,894 |
| gas_capacity_mw | Float | Gas capacity | MW | 8,000-9,200 |
| gas_capacity_factor | Float | Gas capacity factor | - | 0.60-0.61 |
| residential_tariff_naira_per_kwh | Float | Residential tariff | Naira/kWh | 13.0-18.9 |
| proven_gas_reserves_tcf | Float | Proven gas reserves | Tcf | 200-208 |
| daily_gas_production_mmscf | Float | Daily gas production | MMscf/day | 3,000-3,200 |
| daily_gas_flaring_mmscf | Float | Daily gas flaring | MMscf/day | 150-160 |
| flaring_percentage | Float | Flaring percentage | % | 5 |
| avg_petrol_price_naira_per_liter | Float | Average petrol price | Naira/liter | 145-250 |
| avg_diesel_price_naira_per_liter | Float | Average diesel price | Naira/liter | 160-280 |
| sofc_gas_availability_mmscf_per_day | Float | SOFC gas availability | MMscf/day | 1,200-1,280 |
| sofc_power_potential_mw | Float | SOFC power potential | MW | 600-640 |
| sofc_economic_viability_index | Float | SOFC economic viability index | - | 0.5-2.0 |

## Data Quality Notes

### 1. Data Sources
- **Official Sources**: NERC, TCN, NNPC, DPR, NBS
- **International Sources**: World Bank, FAO, GGFR
- **Industry Reports**: Various energy sector reports

### 2. Data Validation
- **Range Checks**: All values within realistic bounds
- **Consistency Checks**: Cross-referenced related metrics
- **Trend Analysis**: Logical progression over time
- **Expert Review**: Industry knowledge incorporated

### 3. Limitations
- **Estimates**: Some data estimated based on trends
- **Regional Variation**: May not capture all local factors
- **Temporal**: Future projections based on current trends
- **Assumptions**: SOFC parameters based on industry standards

### 4. Recommendations
- **Validation**: Verify key assumptions with local data
- **Updates**: Regular updates as new data becomes available
- **Sensitivity Analysis**: Test key assumptions and parameters
- **Stakeholder Input**: Incorporate local knowledge and feedback

## Usage Guidelines

### 1. Data Access
- **Format**: CSV files for easy import into analysis tools
- **Encoding**: UTF-8 encoding for international characters
- **Missing Values**: Represented as NaN or empty cells
- **Units**: All units clearly specified in column names

### 2. Analysis Considerations
- **Temporal**: Consider time trends and seasonality
- **Spatial**: Account for regional variations
- **Correlations**: Check relationships between variables
- **Outliers**: Identify and investigate unusual values

### 3. Reporting
- **Attribution**: Cite data sources appropriately
- **Limitations**: Acknowledge data limitations
- **Assumptions**: State key assumptions clearly
- **Uncertainty**: Quantify uncertainty where possible

This data dictionary provides comprehensive information for effective use of the Nigerian Energy & Resource Dataset in SOFC research and analysis.