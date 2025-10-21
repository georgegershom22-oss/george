# SOFC Technical Dataset Summary Report

Generated on: 2025-10-21 03:42:24

## Dataset Overview

### Electrical Efficiency
- Records: 17
- Columns: 8
- Columns: load_percentage, ht_sofc_efficiency_lhv, it_sofc_efficiency_lhv, lt_sofc_efficiency_lhv, operating_temperature_ht, operating_temperature_it, operating_temperature_lt, pressure_bar

### Thermal Efficiency Chp
- Records: 9
- Columns: 8
- Columns: power_rating_kw, electrical_efficiency_percent, thermal_efficiency_percent, total_chp_efficiency_percent, heat_recovery_temperature_c, hot_water_capacity_kw, steam_generation_kg_h, applications

### Degradation Lifespan
- Records: 100
- Columns: 7
- Columns: operating_hours, voltage_loss_percent, degradation_rate_per_1000h, efficiency_retention, power_retention, stack_replacement_needed, estimated_remaining_life_hours

### Fuel Flexibility
- Records: 4
- Columns: 10
- Columns: fuel_type, composition, lhv_mj_kg, efficiency_impact_percent, preprocessing_required, reforming_temperature_c, steam_carbon_ratio, availability_nigeria, cost_naira_per_m3, cost_naira_per_kg

### Power Density
- Records: 11
- Columns: 8
- Columns: power_rating_kw, power_density_kw_m2, power_density_kw_m3, required_area_m2, required_volume_m3, stack_height_m, footprint_m2, system_type

### Startup Ramp Rates
- Records: 9
- Columns: 10
- Columns: power_rating_kw, cold_startup_time_min, warm_startup_time_min, ramp_up_rate_percent_min, ramp_down_rate_percent_min, min_load_percent, max_load_percent, load_following_capability, backup_power_suitable, grid_support_capable

### Nigeria Scenarios
- Records: 5
- Columns: 12
- Columns: scenario_name, location, power_requirement_mw, fuel_source, application, estimated_efficiency_percent, annual_operation_hours, co2_reduction_tons_year, economic_viability, implementation_timeline_months, key_challenges, estimated_cost_usd_million

### Manufacturer Data
- Records: 5
- Columns: 11
- Columns: manufacturer, product_line, power_range_kw, efficiency_lhv_percent, operating_temp_c, fuel_flexibility, degradation_rate_percent_1000h, warranty_years, price_usd_per_kw, availability_nigeria, local_support

## Key Technical Parameters

### Electrical Efficiency
- High-temperature SOFC: 45-62% LHV
- Intermediate-temperature SOFC: 40-58% LHV
- Low-temperature SOFC: 35-55% LHV

### Degradation Rates
- Typical: 0.3-1.8% voltage loss per 1000 hours
- Stack replacement: ~20% voltage loss
- Expected lifespan: 40,000-80,000 hours

### Power Density
- Micro systems (1-10 kW): 0.8-1.2 kW/m²
- Commercial systems (10-100 kW): 1.0-1.5 kW/m²
- Industrial systems (100-1000 kW): 1.2-2.0 kW/m²
- Utility systems (>1000 kW): 1.5-2.5 kW/m²

### Nigeria-Specific Applications
- 5 detailed scenarios across different states
- Power range: 10-100 MW
- Fuel sources: Natural gas, LPG, Bio-methane
- Economic viability: Medium to Very High

