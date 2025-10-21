# Nigerian Energy Dataset - Data Dictionary

## Complete Field Definitions and Metadata

### Electricity Grid Data

#### Generation Capacity Data (`generation_capacity_data.csv`)

| Field Name | Data Type | Description | Units | Range/Values |
|------------|-----------|-------------|-------|--------------|
| `date` | Date | Monthly observation date | YYYY-MM-DD | 2020-01-01 to 2024-12-31 |
| `source` | String | Power generation source | - | Natural Gas, Hydro, Coal, Solar, Wind |
| `installed_capacity_mw` | Float | Total installed generation capacity | MW | 10-10500 |
| `available_capacity_mw` | Float | Actually available capacity | MW | 5-8000 |
| `availability_factor` | Float | Ratio of available to installed capacity | Decimal | 0.3-1.0 |
| `efficiency` | Float | Generation efficiency | Decimal | 0.20-0.85 |
| `fuel_cost_naira_per_mwh` | Float | Fuel cost per MWh generated | Naira/MWh | 0-35000 |
| `capacity_utilization` | Float | Actual utilization of available capacity | Decimal | 0.3-0.9 |

#### Grid Supply Data (`grid_supply_data.csv`)

| Field Name | Data Type | Description | Units | Range/Values |
|------------|-----------|-------------|-------|--------------|
| `date` | Date | Daily observation date | YYYY-MM-DD | 2023-01-01 to 2024-12-31 |
| `disco` | String | Distribution Company | - | Abuja, Benin, Eko, Enugu, Ibadan, Ikeja, Jos, Kaduna, Kano, Port Harcourt, Yola |
| `allocated_mw` | Float | Power allocated to DisCo | MW | 50-1200 |
| `peak_demand_mw` | Float | Peak demand in DisCo area | MW | 80-2000 |
| `energy_delivered_mwh` | Float | Actual energy delivered | MWh | 800-25000 |
| `load_rejection_mw` | Float | Load rejected due to constraints | MW | 5-500 |
| `technical_losses_percent` | Float | Technical transmission/distribution losses | Percent | 8-25 |
| `commercial_losses_percent` | Float | Commercial losses (theft, billing) | Percent | 15-40 |

#### Reliability Metrics (`reliability_metrics.csv`)

| Field Name | Data Type | Description | Units | Range/Values |
|------------|-----------|-------------|-------|--------------|
| `date` | Date | Monthly observation date | YYYY-MM-DD | 2020-01-01 to 2024-12-31 |
| `region` | String | Geopolitical region | - | North Central, North East, North West, South East, South South, South West |
| `state` | String | Nigerian state | - | All 36 states + FCT |
| `saidi_hours` | Float | System Average Interruption Duration Index | Hours/month | 50-400 |
| `saifi_interruptions` | Float | System Average Interruption Frequency Index | Interruptions/month | 5-50 |
| `caidi_hours` | Float | Customer Average Interruption Duration Index | Hours/interruption | 2-15 |
| `customers_affected` | Integer | Number of customers affected by outages | Count | 10000-500000 |
| `major_outages` | Integer | Number of major outages (>1 hour) | Count | 0-10 |
| `grid_availability_percent` | Float | Percentage of time grid is available | Percent | 60-98 |

#### Electricity Tariffs (`electricity_tariffs.csv`)

| Field Name | Data Type | Description | Units | Range/Values |
|------------|-----------|-------------|-------|--------------|
| `date` | Date | Quarterly tariff effective date | YYYY-MM-DD | 2020-01-01 to 2024-12-31 |
| `disco` | String | Distribution Company | - | All 11 DisCos |
| `customer_class` | String | Customer category | - | Residential, Commercial, Industrial, Special |
| `tariff_naira_per_kwh` | Float | Base electricity tariff | Naira/kWh | 15-60 |
| `fixed_charge_naira` | Float | Monthly fixed charge | Naira/month | 750-5000 |
| `vat_percent` | Float | Value Added Tax rate | Percent | 7.5 |
| `regulatory_charge_percent` | Float | Regulatory charges | Percent | 1.5 |
| `effective_tariff_naira_per_kwh` | Float | All-inclusive tariff rate | Naira/kWh | 18-70 |

### Fossil Fuel Data

#### Gas Reserves & Production (`gas_reserves_production_data.csv`)

| Field Name | Data Type | Description | Units | Range/Values |
|------------|-----------|-------------|-------|--------------|
| `date` | Date | Monthly observation date | YYYY-MM-DD | 2020-01-01 to 2024-12-31 |
| `field_name` | String | Gas field name | - | Niger Delta, Offshore Deep Water, Anambra Basin, Chad Basin, Benue Trough |
| `proven_reserves_tcf` | Float | Proven gas reserves | Trillion cubic feet | 5-120 |
| `probable_reserves_tcf` | Float | Probable gas reserves | Trillion cubic feet | 12-120 |
| `total_reserves_tcf` | Float | Total reserves (proven + probable) | Trillion cubic feet | 17-240 |
| `daily_production_mmscf` | Float | Daily gas production | Million standard cubic feet | 50-2500 |
| `monthly_production_mmscf` | Float | Monthly gas production | Million standard cubic feet | 1500-75000 |
| `associated_gas_ratio` | Float | Ratio of associated to total gas | Decimal | 0.2-0.7 |
| `gas_quality` | String | Gas quality classification | - | sweet, sour |
| `methane_content_percent` | Float | Methane content in gas | Percent | 80-92 |
| `ethane_content_percent` | Float | Ethane content in gas | Percent | 3-8 |
| `propane_content_percent` | Float | Propane content in gas | Percent | 1-3 |
| `co2_content_percent` | Float | CO2 content in gas | Percent | 1-8 |
| `h2s_content_ppm` | Float | Hydrogen sulfide content | Parts per million | 0-500 |
| `heating_value_btu_per_scf` | Float | Higher heating value | BTU per standard cubic foot | 950-1100 |
| `latitude` | Float | Field latitude coordinate | Degrees | 4.0-13.5 |
| `longitude` | Float | Field longitude coordinate | Degrees | 3.0-14.0 |
| `production_cost_usd_per_mscf` | Float | Production cost | USD per thousand scf | 0.8-3.5 |
| `wellhead_pressure_psi` | Float | Wellhead pressure | Pounds per square inch | 800-1500 |
| `water_content_ppm` | Float | Water content in gas | Parts per million | 50-200 |

#### Gas Flaring Data (`gas_flaring_data.csv`)

| Field Name | Data Type | Description | Units | Range/Values |
|------------|-----------|-------------|-------|--------------|
| `date` | Date | Daily observation date | YYYY-MM-DD | 2020-01-01 to 2024-12-31 |
| `site_name` | String | Flaring site name | - | Escravos, Bonny, Forcados, Brass, Qua Iboe, etc. |
| `operator` | String | Operating company | - | Shell, Chevron, ExxonMobil, Total, Agip |
| `latitude` | Float | Site latitude coordinate | Degrees | 4.3-5.6 |
| `longitude` | Float | Site longitude coordinate | Degrees | 5.1-7.9 |
| `daily_flaring_mmscf` | Float | Daily gas flaring volume | Million standard cubic feet | 15-120 |
| `monthly_flaring_mmscf` | Float | Monthly gas flaring volume | Million standard cubic feet | 450-3600 |
| `annual_flaring_bcf` | Float | Annual gas flaring volume | Billion cubic feet | 5.5-44 |
| `co2_emissions_tonnes_per_day` | Float | Daily CO2 emissions from flaring | Tonnes CO2/day | 0.8-6.6 |
| `energy_wasted_gj_per_day` | Float | Daily energy wasted | Gigajoules/day | 15.5-124 |
| `sofc_potential_mw` | Float | **SOFC power generation potential** | MW | 1.5-12 |
| `distance_to_grid_km` | Float | Distance to nearest grid connection | Kilometers | 5-50 |
| `local_power_demand_mw` | Float | Local area power demand | MW | 10-100 |
| `flaring_efficiency_percent` | Float | Flaring combustion efficiency | Percent | 95-99 |
| `gas_heating_value_btu_per_scf` | Float | Heating value of flared gas | BTU per scf | 1000-1100 |
| `regulatory_penalty_usd` | Float | Daily regulatory penalty | USD | 50-500 |

#### Pipeline Network (`pipeline_network_data.csv`)

| Field Name | Data Type | Description | Units | Range/Values |
|------------|-----------|-------------|-------|--------------|
| `date` | Date | Monthly observation date | YYYY-MM-DD | 2020-01-01 to 2024-12-31 |
| `pipeline_name` | String | Pipeline system name | - | ELPS, OB3, EGGS, AKK, Nigeria-Morocco |
| `operator` | String | Pipeline operator | - | NGC, Shell, NNPC, NNPC/ONHYM |
| `length_km` | Float | Pipeline length | Kilometers | 150-5660 |
| `diameter_inches` | Float | Pipeline diameter | Inches | 24-48 |
| `max_capacity_mmscf_per_day` | Float | Maximum daily capacity | Million scf/day | 800-2200 |
| `actual_flow_mmscf_per_day` | Float | Actual daily throughput | Million scf/day | 480-1980 |
| `utilization_percent` | Float | Capacity utilization | Percent | 45-95 |
| `start_latitude` | Float | Pipeline start point latitude | Degrees | 5.0-12.0 |
| `start_longitude` | Float | Pipeline start point longitude | Degrees | 3.4-8.5 |
| `end_latitude` | Float | Pipeline end point latitude | Degrees | 5.2-35.8 |
| `end_longitude` | Float | Pipeline end point longitude | Degrees | -5.8-8.8 |
| `operating_pressure_psi` | Float | Operating pressure | Pounds per square inch | 800-1200 |
| `compressor_stations` | Integer | Number of compressor stations | Count | 2-56 |
| `maintenance_cost_usd_per_km` | Float | Annual maintenance cost per km | USD/km/year | 1000-5000 |
| `throughput_revenue_usd` | Float | Daily throughput revenue | USD | 960-7920 |
| `status` | String | Operational status | - | operational, under_construction |

#### Fuel Prices (`fuel_prices_data.csv`)

| Field Name | Data Type | Description | Units | Range/Values |
|------------|-----------|-------------|-------|--------------|
| `date` | Date | Monthly observation date | YYYY-MM-DD | 2020-01-01 to 2024-12-31 |
| `state` | String | Nigerian state | - | All 36 states + FCT |
| `petrol_price_naira_per_liter` | Float | Petrol (PMS) retail price | Naira/liter | 120-400 |
| `diesel_price_naira_per_liter` | Float | Diesel (AGO) retail price | Naira/liter | 180-600 |
| `kerosene_price_naira_per_liter` | Float | Kerosene (DPK) retail price | Naira/liter | 150-500 |
| `lpg_price_naira_per_kg` | Float | LPG retail price | Naira/kg | 100-350 |
| `fuel_scarcity_factor` | Float | Scarcity multiplier (1.0 = normal) | Decimal | 1.0-1.3 |
| `black_market_premium_percent` | Float | Black market price premium | Percent | 3-60 |
| `supply_disruption_days` | Integer | Days of supply disruption per month | Days | 0-15 |
| `nearest_depot_distance_km` | Float | Distance to nearest fuel depot | Kilometers | 5-300 |
| `local_consumption_million_liters` | Float | Monthly local consumption | Million liters | 5-50 |

### Renewable Resources Data

#### Agricultural Waste (`agricultural_waste_data.csv`)

| Field Name | Data Type | Description | Units | Range/Values |
|------------|-----------|-------------|-------|--------------|
| `year` | Integer | Observation year | Year | 2020-2024 |
| `state` | String | Nigerian state | - | All 36 states + FCT |
| `crop` | String | Crop type | - | Rice, Maize, Sugarcane, Cassava, Yam, Sorghum, Millet, Groundnut, Cowpea, Oil Palm |
| `residue_type` | String | Type of agricultural residue | - | 22 different residue types |
| `crop_production_tonnes` | Float | Annual crop production | Tonnes/year | 1000-2000000 |
| `residue_production_tonnes` | Float | Annual residue production | Tonnes/year | 200-1600000 |
| `residue_ratio` | Float | Residue to crop production ratio | Decimal | 0.15-0.8 |
| `energy_content_mj_per_kg` | Float | Energy content of residue | MJ/kg | 13.5-20.1 |
| `total_energy_potential_gj` | Float | Total energy potential | Gigajoules/year | 2700-32000000 |
| `current_utilization_rate` | Float | Current utilization of residue | Decimal | 0.05-0.7 |
| `available_for_energy_tonnes` | Float | Residue available for energy use | Tonnes/year | 150-1280000 |
| `available_energy_potential_gj` | Float | Available energy potential | Gigajoules/year | 2000-25600000 |
| `biogas_potential_m3` | Float | Biogas production potential | Cubic meters/year | 20250-358400000 |
| `sofc_feedstock_potential_tonnes` | Float | **SOFC feedstock potential after gasification** | Tonnes/year | 85-832000 |
| `collection_cost_naira_per_tonne` | Float | Collection cost | Naira/tonne | 2000-25000 |
| `transportation_cost_naira_per_tonne_km` | Float | Transportation cost | Naira/tonne/km | 12-40 |
| `storage_requirements` | String | Storage requirements description | Text | Various storage specifications |
| `seasonal_availability` | String | Seasonal availability pattern | Text | Seasonal patterns |
| `moisture_content_percent` | Float | Moisture content | Percent | 7-80 |
| `ash_content_percent` | Float | Ash content | Percent | 2-18 |
| `carbon_content_percent` | Float | Carbon content | Percent | 38-50 |
| `nitrogen_content_percent` | Float | Nitrogen content | Percent | 0.3-2.5 |

#### Livestock Population (`livestock_population_data.csv`)

| Field Name | Data Type | Description | Units | Range/Values |
|------------|-----------|-------------|-------|--------------|
| `year` | Integer | Observation year | Year | 2020-2024 |
| `state` | String | Nigerian state | - | All 36 states + FCT |
| `livestock_type` | String | Type of livestock | - | Cattle, Goats, Sheep, Poultry, Pigs |
| `population` | Integer | Livestock population | Head | 8000-3500000 |
| `daily_manure_per_animal_kg` | Float | Daily manure production per animal | kg/day/animal | 0.15-20 |
| `total_daily_manure_tonnes` | Float | Total daily manure production | Tonnes/day | 1.2-52500 |
| `annual_manure_tonnes` | Float | Annual manure production | Tonnes/year | 438-19162500 |
| `collection_efficiency_percent` | Float | Manure collection efficiency | Percent | 20-104 |
| `collectible_manure_tonnes` | Float | Collectible manure quantity | Tonnes/year | 87.6-15330000 |
| `biogas_yield_m3_per_kg` | Float | Biogas yield per kg manure | m³/kg | 0.035-0.08 |
| `annual_biogas_potential_m3` | Float | Annual biogas potential | Cubic meters/year | 3066-1226400000 |
| `methane_content_percent` | Float | Methane content in biogas | Percent | 58-65 |
| `annual_methane_potential_m3` | Float | Annual methane potential | Cubic meters/year | 1778-797160000 |
| `sofc_potential_mwh_per_year` | Float | **Annual SOFC potential from livestock** | MWh/year | 1.1-47700 |
| `manure_collection_cost_naira_per_tonne` | Float | Manure collection cost | Naira/tonne | 3000-16800 |
| `biogas_plant_investment_naira_per_m3` | Float | Biogas plant investment cost | Naira/m³ capacity | 80000-120000 |
| `land_requirement_hectares` | Float | Land requirement for livestock | Hectares | 8-1750000 |
| `water_requirement_liters_per_day` | Float | Daily water requirement | Liters/day | 1200-175000000 |
| `feed_requirement_tonnes_per_year` | Float | Annual feed requirement | Tonnes/year | 3200-8750000 |

## Data Quality Indicators

### Completeness Scores
- **Temporal Coverage**: 100% for all time periods
- **Geographic Coverage**: 100% for all Nigerian states
- **Sectoral Coverage**: 95% of major energy sectors included
- **Data Validation**: 98% consistency across cross-referenced fields

### Data Source Categories
- **A (Official)**: Government agencies, regulatory bodies (15% of data)
- **B (Industry)**: Company reports, industry associations (25% of data)
- **C (Synthetic)**: Statistically generated based on patterns (60% of data)

### Uncertainty Levels
- **Low (<5% error)**: Official government statistics, major company data
- **Medium (5-15% error)**: Industry estimates, derived calculations
- **High (>15% error)**: Synthetic data in data-sparse regions

## Special Field Definitions

### SOFC-Specific Calculations

#### `sofc_potential_mw` (Gas Flaring)
**Calculation**: Daily flaring (mmscf) × 1.037 (GJ/mmscf) × 0.278 (MWh/GJ) × 0.60 (SOFC efficiency) × 0.90 (availability) ÷ 24 hours

#### `sofc_feedstock_potential_tonnes` (Agricultural Waste)  
**Calculation**: Available biomass (tonnes) × gasification efficiency (0.55-0.74) based on feedstock type

#### `sofc_potential_mwh_per_year` (Livestock)
**Calculation**: Annual methane (m³) × 35.8 (MJ/m³) × 0.278 (kWh/MJ) × 0.60 (SOFC efficiency) ÷ 1000

### Regional Classifications
- **North Central**: FCT, Benue, Kogi, Kwara, Nasarawa, Niger, Plateau
- **North East**: Adamawa, Bauchi, Borno, Gombe, Taraba, Yobe  
- **North West**: Jigawa, Kaduna, Kano, Katsina, Kebbi, Sokoto, Zamfara
- **South East**: Abia, Anambra, Ebonyi, Enugu, Imo
- **South South**: Akwa Ibom, Bayelsa, Cross River, Delta, Edo, Rivers
- **South West**: Ekiti, Lagos, Ogun, Ondo, Osun, Oyo

### Currency and Units
- **Currency**: Nigerian Naira (₦) as of dataset compilation period
- **Energy Units**: Consistent use of MJ, GJ, kWh, MWh throughout
- **Gas Units**: Standard cubic feet (scf), million scf (mmscf), billion scf (bcf)
- **Coordinates**: Decimal degrees (WGS84 datum)

---

*This data dictionary provides comprehensive field definitions for all variables in the Nigerian Energy Dataset. For additional technical details or clarifications, refer to the methodology documentation or contact the dataset maintainers.*