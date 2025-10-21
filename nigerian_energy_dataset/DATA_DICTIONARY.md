# Data Dictionary
## Nigerian Energy & Resource Dataset

**Version:** 1.0  
**Last Updated:** October 21, 2024

This document provides complete definitions, units, and value ranges for all fields in the dataset.

---

## TABLE OF CONTENTS

1. [Electricity Grid Data](#electricity-grid-data)
2. [Fossil Fuels Data](#fossil-fuels-data)
3. [Renewable Resources Data](#renewable-resources-data)
4. [Geospatial Data](#geospatial-data)
5. [Analysis Files](#analysis-files)
6. [Common Units and Abbreviations](#common-units-and-abbreviations)

---

## ELECTRICITY GRID DATA

### National Generation Capacity

| Field Name | Data Type | Unit | Description | Value Range | Null Allowed |
|------------|-----------|------|-------------|-------------|--------------|
| Power_Plant | String | - | Official name of power generation facility | - | No |
| Location | String | - | City/town where facility is located | - | No |
| State | String | - | Nigerian state | 36 states + FCT | No |
| Source_Type | String | - | Primary energy source | Gas, Hydro | No |
| Installed_Capacity_MW | Float | MW | Nameplate generation capacity | 30-3050 | No |
| Available_Capacity_MW | Float | MW | Current operational capacity | 0-650 | No |
| Operational_Status | String | - | Current operational state | Operational, Under Construction | No |
| Commission_Year | Integer | Year | Year facility began operations | 1968-2025 | No |
| Operator | String | - | Entity operating the facility | Various | No |
| Efficiency_Percent | Float | % | Net electrical efficiency | 32-88 | No |
| Fuel_Type | String | - | Specific fuel used | Natural Gas, Hydro | No |
| Capacity_Factor_Percent | Float | % | Actual output / potential output | 0-72.5 | No |

**Notes:**
- Available_Capacity < Installed_Capacity due to maintenance, age, and fuel constraints
- Capacity_Factor = 0 for plants under construction
- Efficiency_Percent for hydro includes mechanical and electrical losses

---

### Daily Load Allocation 2024

| Field Name | Data Type | Unit | Description | Value Range | Null Allowed |
|------------|-----------|------|-------------|-------------|--------------|
| Date | Date | YYYY-MM-DD | Date of observation | 2024 only | No |
| Peak_Generation_MW | Float | MW | Maximum generation during day | 4000-5000 | No |
| Off_Peak_Generation_MW | Float | MW | Minimum generation during day | 3000-3750 | No |
| Average_Daily_Generation_MW | Float | MW | Mean generation over 24 hours | 3500-4500 | No |
| Total_Generation_MWh | Float | MWh | Total energy generated in day | 85000-103000 | No |
| Peak_Demand_MW | Float | MW | Maximum demand during day | 7800-8500 | No |
| Energy_Sent_Out_MWh | Float | MWh | Energy delivered after losses | 80000-99000 | No |
| Grid_Frequency_Hz | Float | Hz | Average grid frequency | 49.8-50.1 | No |
| System_Collapse_Events | Integer | Count | Number of grid collapses | 0-2 | No |
| Gas_Constraint_MW | Float | MW | Generation lost to gas shortages | 998-1623 | No |
| Water_Management_MW | Float | MW | Generation lost to water issues | 235-445 | No |
| Grid_Constraint_MW | Float | MW | Generation lost to grid limits | 305-565 | No |
| Distribution_Constraint_MW | Float | MW | Generation lost to DisCo limits | 1045-1720 | No |

**Notes:**
- Total_Generation_MWh = Average_Daily_Generation_MW × 24
- Energy_Sent_Out < Total_Generation due to transmission losses (~4-7%)
- System_Collapse_Events = complete grid shutdown events
- Constraint fields represent capacity available but not dispatched

---

### Grid Reliability Metrics

| Field Name | Data Type | Unit | Description | Value Range | Null Allowed |
|------------|-----------|------|-------------|-------------|--------------|
| State | String | - | Nigerian state | 36 states + FCT | No |
| Region | String | - | Geopolitical zone | 6 zones | No |
| Year | Integer | Year | Year of data | 2024 | No |
| SAIDI_Hours | Float | Hours/Year | System Average Interruption Duration Index | 2340-5234 | No |
| SAIFI_Events | Float | Events/Year | System Average Interruption Frequency Index | 142-238 | No |
| Average_Outage_Duration_Hours | Float | Hours | Mean duration per outage | 16.5-22.0 | No |
| Total_Customers | Integer | Count | Number of grid-connected customers | 356000-3245000 | No |
| Grid_Coverage_Percent | Float | % | Population with grid access | 43.6-85.6 | No |
| Off_Grid_Population_Percent | Float | % | Population without grid access | 14.4-56.4 | No |
| Backup_Generator_Penetration_Percent | Float | % | Households/businesses with generators | 32.1-75.8 | No |
| Estimated_Outage_Cost_Million_USD | Float | Million USD | Annual economic cost of outages | 167-1246 | No |

**Notes:**
- SAIDI = Total outage hours experienced by all customers / Total customers
- SAIFI = Total number of outages / Total customers
- Average_Outage_Duration = SAIDI / SAIFI
- Estimated costs based on lost productivity, generator fuel costs, and equipment damage

---

### Electricity Tariffs 2024

| Field Name | Data Type | Unit | Description | Value Range | Null Allowed |
|------------|-----------|------|-------------|-------------|--------------|
| Distribution_Company | String | - | DisCo name | 11 DisCos | No |
| Customer_Class | String | - | Customer category | Residential, Commercial, Industrial, Special | No |
| Tariff_Class | String | - | Specific tariff code | Various codes | No |
| Fixed_Charge_NGN | Float | NGN | Monthly fixed charge | 500-25000 | No |
| Energy_Charge_NGN_per_kWh | Float | NGN/kWh | Variable charge per unit consumed | 56-145 | No |
| Monthly_Service_Charge_NGN | Float | NGN | Monthly service fee | 1000-40000 | No |
| Minimum_Monthly_Charge_NGN | Float | NGN | Minimum monthly bill | 2500-125000 | No |
| Peak_Rate_NGN_per_kWh | Float | NGN/kWh | Time-of-use peak rate | 0-165 | Yes |
| Off_Peak_Rate_NGN_per_kWh | Float | NGN/kWh | Time-of-use off-peak rate | 0-125 | Yes |
| VAT_Percent | Float | % | Value Added Tax | 7.5 | No |
| Effective_Date | Date | YYYY-MM-DD | Date tariff became effective | 2024-01-01 | No |
| Subsidy_Percent | Float | % | Government subsidy rate | 0-50 | No |

**Notes:**
- Peak/Off-Peak rates only apply to Maximum Demand (MD) customers
- 0 value indicates flat-rate tariff (no TOU pricing)
- Residential customers generally on flat rates
- Industrial customers primarily on MD tariffs with TOU

---

## FOSSIL FUELS DATA

### Gas Reserves and Production

| Field Name | Data Type | Unit | Description | Value Range | Null Allowed |
|------------|-----------|------|-------------|-------------|--------------|
| Year | Integer | Year | Calendar year | 2015-2024 | No |
| Proven_Gas_Reserves_Tcf | Float | Tcf | Proven recoverable reserves (P90) | 192-211 | No |
| Probable_Reserves_Tcf | Float | Tcf | Probable reserves (P50) | 45-55 | No |
| Possible_Reserves_Tcf | Float | Tcf | Possible reserves (P10) | 68-83 | No |
| Total_Gas_Production_Bcf_per_Year | Float | Bcf/Year | Total gas produced (all sources) | 1678-2013 | No |
| Marketed_Production_Bcf_per_Year | Float | Bcf/Year | Gas actually brought to market | 1235-1567 | No |
| Gas_Flared_Bcf_per_Year | Float | Bcf/Year | Gas flared at source | 260-302 | No |
| Gas_Reinjected_Bcf_per_Year | Float | Bcf/Year | Gas reinjected for reservoir pressure | 149-169 | No |
| Domestic_Gas_Supply_Bcf_per_Year | Float | Bcf/Year | Gas for domestic consumption | 457-736 | No |
| Gas_Export_LNG_Bcf_per_Year | Float | Bcf/Year | Gas exported as LNG | 334-386 | No |
| Associated_Gas_Percent | Float | % | Gas produced with oil | 66-72 | No |
| Non_Associated_Gas_Percent | Float | % | Gas from gas-only wells | 28-34 | No |
| Reserves_to_Production_Ratio_Years | Float | Years | Years of reserves at current production | 105-118 | No |

**Notes:**
- Tcf = Trillion cubic feet, Bcf = Billion cubic feet
- Marketed Production = Total Production - Flared - Reinjected
- Associated gas percentages declining as new gas fields develop

---

### Gas Flaring by Location 2024

| Field Name | Data Type | Unit | Description | Value Range | Null Allowed |
|------------|-----------|------|-------------|-------------|--------------|
| Flare_Site_ID | String | - | Unique identifier for flare site | FL-001 to FL-030 | No |
| Location_Name | String | - | Common name of location | Various | No |
| State | String | - | Nigerian state | Delta, Rivers, Bayelsa, Edo, Akwa Ibom | No |
| Operator | String | - | Oil company operating the field | Shell, Chevron, Agip, Mobil, etc. | No |
| Latitude | Float | Degrees | GPS latitude coordinate | 3.4 to 6.2 | No |
| Longitude | Float | Degrees | GPS longitude coordinate | 4.2 to 8.1 | No |
| Daily_Flare_Volume_mscf | Float | mscf/day | Million standard cubic feet flared daily | 12-53 | No |
| Annual_Flare_Volume_Bcf | Float | Bcf/year | Annual flaring volume | 4.5-19.3 | No |
| Associated_Field | String | - | Oil/gas field name | Various | No |
| Field_Production_Capacity_bbl_per_day | Float | bbl/day | Oil production capacity of field | 42000-220000 | No |
| Gas_to_Oil_Ratio_scf_per_bbl | Float | scf/bbl | Volume of gas per barrel of oil | 1180-1780 | No |
| Flare_Intensity_Percent | Float | % | Percent of produced gas that is flared | 8.7-21.3 | No |
| Emissions_CO2_tonnes_per_year | Float | tonnes/year | CO2 emissions from flaring | 262740-1117560 | No |
| Emissions_CH4_tonnes_per_year | Float | tonnes/year | Methane emissions (incomplete combustion) | 3420-14550 | No |
| Environmental_Impact_Score | Float | Score (1-10) | Composite environmental damage score | 4.2-9.2 | No |
| Population_Within_5km | Integer | Count | People living within 5km radius | 8700-52300 | No |
| Health_Impact_Index | Float | Score (1-10) | Public health impact indicator | 4.5-8.4 | No |

**Notes:**
- mscf = thousand standard cubic feet, Bcf = Billion cubic feet
- Annual volume = Daily volume × 365
- CO2 emissions assume 0.058 tonnes CO2 per mscf flared
- CH4 emissions assume 1-2% incomplete combustion
- Scores based on proximity to population, ecosystem sensitivity

---

### Gas Pipeline Infrastructure

| Field Name | Data Type | Unit | Description | Value Range | Null Allowed |
|------------|-----------|------|-------------|-------------|--------------|
| Pipeline_Name | String | - | Official pipeline name | Various | No |
| Pipeline_ID | String | - | Abbreviated identifier | Various | No |
| Start_Location | String | - | Pipeline origin point | Various | No |
| End_Location | String | - | Pipeline destination | Various | No |
| Length_km | Float | km | Pipeline length | 28-4400 | No |
| Diameter_inches | Float | inches | Internal pipeline diameter | 16-56 | No |
| Capacity_mscf_per_day | Float | mscf/day | Maximum daily throughput | 170-2200 | No |
| Current_Throughput_mscf_per_day | Float | mscf/day | Actual daily flow | 0-1620 | No |
| Utilization_Percent | Float | % | Current flow / capacity | 0-92.1 | No |
| Operator | String | - | Pipeline operator | NGC, Shell, Chevron, etc. | No |
| Construction_Year | Integer | Year | Year pipeline completed | 1968-2025 | No |
| Last_Maintenance_Year | Integer | Year | Most recent major maintenance | 2021-2024 | Yes |
| Condition_Status | String | - | Physical condition assessment | Excellent, Good, Fair | No |
| Pressure_PSI | Float | PSI | Operating pressure | 800-1400 | No |
| Number_of_Compressor_Stations | Integer | Count | Compressor stations along route | 0-45 | No |
| Gas_Quality_HHV_BTU_per_scf | Float | BTU/scf | Higher heating value of gas | 1035-1060 | No |
| Leakage_Rate_Percent | Float | % | Estimated annual leakage | 0.0-1.5 | No |

**Notes:**
- mscf = thousand standard cubic feet
- Utilization = 0 for pipelines under construction
- HHV (Higher Heating Value) indicates gas quality/energy content
- Leakage rates estimated from age and condition

---

### Diesel and Petrol Prices by State

| Field Name | Data Type | Unit | Description | Value Range | Null Allowed |
|------------|-----------|------|-------------|-------------|--------------|
| State | String | - | Nigerian state | 36 states + FCT | No |
| Region | String | - | Geopolitical zone | 6 zones | No |
| Diesel_Retail_Price_NGN_per_Litre | Float | NGN/L | Automotive diesel (AGO) price | 1250-1395 | No |
| Petrol_Retail_Price_NGN_per_Litre | Float | NGN/L | Premium motor spirit (PMS) price | 617-685 | No |
| Kerosene_Price_NGN_per_Litre | Float | NGN/L | Dual purpose kerosene (DPK) price | 950-1065 | No |
| LPG_Price_NGN_per_kg | Float | NGN/kg | Liquefied petroleum gas price | 1180-1295 | No |
| CNG_Price_NGN_per_scm | Float | NGN/scm | Compressed natural gas price | 230-298 | No |
| Distance_from_Depot_km | Float | km | Distance to nearest fuel depot | 0-1245 | No |
| Transport_Premium_Percent | Float | % | Price increase due to transport | 0-11.6 | No |
| Black_Market_Diesel_Premium_Percent | Float | % | Black market price premium | 15-35 | No |
| Scarcity_Frequency_Days_per_Month | Float | Days | Days with fuel scarcity per month | 2-11 | No |
| Price_Updated_Date | Date | YYYY-MM-DD | Date prices recorded | 2024-10-15 | No |

**Notes:**
- Prices are retail pump prices including all taxes and margins
- Transport premium = (Distance from depot / 100 km) × 0.4%
- Black market prices emerge during scarcity periods
- CNG prices where available (limited distribution)

---

## RENEWABLE RESOURCES DATA

### Agricultural Waste by State

| Field Name | Data Type | Unit | Description | Value Range | Null Allowed |
|------------|-----------|------|-------------|-------------|--------------|
| State | String | - | Nigerian state | 36 states | No |
| Region | String | - | Geopolitical zone | 6 zones | No |
| Rice_Production_tonnes | Float | tonnes | Annual rice production | 12000-856000 | No |
| Rice_Husk_Available_tonnes | Float | tonnes | Rice husk residue (20% of production) | 2400-171200 | No |
| Maize_Production_tonnes | Float | tonnes | Annual maize production | 45000-1245000 | No |
| Maize_Cobs_Available_tonnes | Float | tonnes | Maize cob residue (20% of production) | 9000-249000 | No |
| Sugarcane_Production_tonnes | Float | tonnes | Annual sugarcane production | 5600-67000 | No |
| Sugarcane_Bagasse_tonnes | Float | tonnes | Bagasse residue (20% of production) | 1120-13400 | No |
| Cassava_Production_tonnes | Float | tonnes | Annual cassava production | 234000-2345000 | No |
| Cassava_Peels_tonnes | Float | tonnes | Cassava peel residue (20% of production) | 46800-469000 | No |
| Yam_Production_tonnes | Float | tonnes | Annual yam production | 67000-1890000 | No |
| Yam_Peels_tonnes | Float | tonnes | Yam peel residue (20% of production) | 13400-378000 | No |
| Palm_Oil_Production_tonnes | Float | tonnes | Annual palm oil production | 2800-89000 | No |
| Palm_Kernel_Shell_tonnes | Float | tonnes | Palm kernel shell residue (50% of production) | 1400-44500 | No |
| Cotton_Production_tonnes | Float | tonnes | Annual cotton production | 800-42000 | No |
| Cotton_Stalk_tonnes | Float | tonnes | Cotton stalk residue (200% of production) | 1600-84000 | No |
| Sorghum_Production_tonnes | Float | tonnes | Annual sorghum production | 15000-523000 | No |
| Sorghum_Straw_tonnes | Float | tonnes | Sorghum straw residue (200% of production) | 30000-1046000 | No |
| Total_Biomass_Potential_tonnes | Float | tonnes | Sum of all agricultural residues | 111380-1785650 | No |
| Biomass_Energy_Potential_TJ | Float | TJ | Energy content (16.2 MJ/kg average) | 2140-34307 | No |
| Current_Utilization_Percent | Float | % | Percent of residue currently used | 5.8-22.5 | No |
| Year | Integer | Year | Year of agricultural data | 2023 | No |

**Notes:**
- Residue percentages based on crop-specific residue-to-product ratios
- Total biomass assumes 60% collection efficiency
- Energy potential: Rice husk 16 MJ/kg, Maize cobs 17 MJ/kg, Bagasse 18 MJ/kg, etc.
- Current utilization mainly for cooking fuel and animal feed

---

### Livestock Population by State

| Field Name | Data Type | Unit | Description | Value Range | Null Allowed |
|------------|-----------|------|-------------|-------------|--------------|
| State | String | - | Nigerian state | 36 states | No |
| Region | String | - | Geopolitical zone | 6 zones | No |
| Cattle_Population | Integer | Head | Number of cattle | 45000-3450000 | No |
| Sheep_Population | Integer | Head | Number of sheep | 67000-3120000 | No |
| Goat_Population | Integer | Head | Number of goats | 234000-4560000 | No |
| Pig_Population | Integer | Head | Number of pigs | 19000-234000 | No |
| Poultry_Population | Integer | Head | Number of poultry (chickens, etc.) | 9600000-34500000 | No |
| Cattle_Manure_tonnes_per_year | Float | tonnes/year | Annual cattle manure production | 76500-5865000 | No |
| Sheep_Manure_tonnes_per_year | Float | tonnes/year | Annual sheep manure production | 3350-156000 | No |
| Goat_Manure_tonnes_per_year | Float | tonnes/year | Annual goat manure production | 11700-228000 | No |
| Pig_Manure_tonnes_per_year | Float | tonnes/year | Annual pig manure production | 3420-42120 | No |
| Poultry_Manure_tonnes_per_year | Float | tonnes/year | Annual poultry manure production | 43200-155250 | No |
| Total_Manure_Available_tonnes | Float | tonnes | Total annual manure (all sources) | 253370-6330650 | No |
| Biogas_Potential_million_m3 | Float | Million m³ | Potential biogas from manure | 12.7-316.5 | No |
| Energy_Potential_TJ | Float | TJ | Energy content of biogas (22 MJ/m³) | 279-6962 | No |
| Current_Biogas_Systems | Integer | Count | Number of operational biogas systems | 98-567 | No |
| Biogas_Utilization_Percent | Float | % | Percent of potential currently utilized | 0.8-7.3 | No |
| Year | Integer | Year | Year of livestock census | 2023 | No |

**Notes:**
- Manure production rates (kg/head/day): Cattle 17, Sheep 0.5, Goats 0.5, Pigs 1.8, Poultry 0.11
- Biogas yield: 0.05 m³ per kg manure (average across species)
- Energy content: 22 MJ/m³ biogas
- Higher utilization in South East/South South due to existing biogas programs

---

## GEOSPATIAL DATA

### Gas Field Coordinates

| Field Name | Data Type | Unit | Description | Value Range | Null Allowed |
|------------|-----------|------|-------------|-------------|--------------|
| Field_Name | String | - | Official name of oil/gas field | Various | No |
| Operator | String | - | Company operating the field | Shell, Chevron, Mobil, Agip, etc. | No |
| State | String | - | Nigerian state (or Offshore) | Various + Offshore | No |
| Region | String | - | Geographic region | South South primarily | No |
| Latitude | Float | Degrees | GPS latitude (decimal degrees) | 3.3 to 6.2 | No |
| Longitude | Float | Degrees | GPS longitude (decimal degrees) | 4.2 to 8.1 | No |
| Field_Type | String | - | Field location classification | Onshore, Offshore, Swamp, Deepwater | No |
| Discovery_Year | Integer | Year | Year field was discovered | 1953-2008 | No |
| Production_Start | Integer | Year | Year production began | 1956-2024 | No |
| Daily_Production_bbl | Float | bbl/day | Current oil production | 0-250000 | No |
| Gas_Reserves_Bcf | Float | Bcf | Estimated gas reserves in field | 0-4280 | No |
| Oil_Reserves_MMbbl | Float | MMbbl | Estimated oil reserves in field | 0-1680 | No |
| Water_Depth_m | Float | meters | Water depth (offshore fields) | 0-1600 | No |
| Development_Status | String | - | Current development stage | Producing, Under Construction | No |
| Associated_Processing_Facility | String | - | Terminal or processing plant | Various | No |
| Distance_to_Grid_km | Float | km | Distance to nearest grid connection | 3-95 | No |
| Distance_to_Major_City_km | Float | km | Distance to nearest major city | 3-142 | No |
| Environmental_Sensitivity_Score | Float | Score (1-10) | Ecosystem sensitivity indicator | 5.6-8.5 | No |

**Notes:**
- bbl = barrels, Bcf = Billion cubic feet, MMbbl = Million barrels
- Water depth = 0 for onshore/swamp fields
- Environmental sensitivity considers mangroves, wetlands, fisheries
- Grid distance critical for SOFC deployment feasibility

---

## ANALYSIS FILES

### SOFC Deployment Potential

| Field Name | Data Type | Unit | Description | Value Range | Null Allowed |
|------------|-----------|------|-------------|-------------|--------------|
| State | String | - | Nigerian state | 36 states | No |
| Region | String | - | Geopolitical zone | 6 zones | No |
| Gas_Proximity_Score | Float | Score (1-10) | Access to gas supply | 4.8-9.8 | No |
| Grid_Reliability_Score | Float | Score (1-10) | Current grid quality (inverse of need) | 4.4-7.6 | No |
| Industrial_Demand_MW | Float | MW | Industrial electricity demand | 150-2850 | No |
| Commercial_Demand_MW | Float | MW | Commercial electricity demand | 60-1940 | No |
| Peak_Demand_Deficit_MW | Float | MW | Unmet peak demand | 818-3325 | No |
| Gas_Pipeline_Access | String | - | Pipeline connectivity status | Yes, Partial, No | No |
| Distance_to_Gas_Source_km | Float | km | Distance to nearest gas field/pipeline | 8-1124 | No |
| Estimated_SOFC_Capacity_Potential_MW | Float | MW | Feasible SOFC deployment capacity | 50-1200 | No |
| SOFC_Priority_Tier | String | - | Deployment priority classification | Tier_1 to Tier_5 | No |
| Population_Density_per_km2 | Float | persons/km² | State population density | 85-3200 | No |
| GDP_Contribution_Percent | Float | % | Contribution to national GDP | 0.4-28.5 | No |
| Industrial_Zones | Integer | Count | Number of industrial estates | 1-12 | No |
| Manufacturing_Facilities | Integer | Count | Number of manufacturing plants | 18-456 | No |
| Data_Centers | Integer | Count | Number of data centers | 0-12 | No |
| Hospitals | Integer | Count | Number of major hospitals | 4-89 | No |
| Universities | Integer | Count | Number of universities | 1-12 | No |
| SOFC_Implementation_Complexity | String | - | Implementation difficulty | Low, Medium, High, Very High | No |
| Estimated_Investment_Million_USD | Float | Million USD | Capital investment required | 70-1680 | No |
| Payback_Period_Years | Float | Years | Estimated investment payback period | 3.8-12.3 | No |

**Notes:**
- Gas proximity score: Distance-based + pipeline access
- Grid reliability score: Based on SAIDI/SAIFI (lower SAIDI = higher score)
- Priority tiers: Tier 1 = immediate deployment, Tier 5 = defer
- Investment: $1,400/kW average SOFC capital cost
- Payback: Based on diesel displacement savings

---

### Energy Economics Comparison

| Field Name | Data Type | Unit | Description | Value Range | Null Allowed |
|------------|-----------|------|-------------|-------------|--------------|
| Technology | String | - | Power generation technology name | Various | No |
| Capacity_Factor_Percent | Float | % | Average annual capacity utilization | 18-90 | No |
| Efficiency_Percent | Float | % | Net electrical efficiency (LHV) | 15-90 | No |
| Capital_Cost_USD_per_kW | Float | USD/kW | Overnight capital cost | 420-6500 | No |
| O&M_Cost_USD_per_kW_year | Float | USD/kW/year | Annual operations & maintenance cost | 15-280 | No |
| Fuel_Cost_USD_per_MWh | Float | USD/MWh | Fuel cost per unit energy generated | 0-95 | No |
| LCOE_USD_per_MWh | Float | USD/MWh | Levelized cost of electricity | 48-210 | No |
| Lifespan_Years | Integer | Years | Expected operational lifespan | 10-60 | No |
| Ramp_Rate_Percent_per_Minute | Float | %/minute | Load change rate capability | 1-50 | Yes |
| Startup_Time_Minutes | Float | Minutes | Time from cold start to full load | 2-720 | Yes |
| Minimum_Load_Percent | Float | % | Minimum stable operating load | 0-70 | No |
| Emissions_CO2_kg_per_MWh | Float | kg CO2/MWh | CO2 emissions per unit energy | 0-820 | No |
| Emissions_NOx_g_per_MWh | Float | g NOx/MWh | Nitrogen oxide emissions | 0-2400 | No |
| Emissions_SOx_g_per_MWh | Float | g SOx/MWh | Sulfur oxide emissions | 0-1800 | No |
| Water_Usage_L_per_MWh | Float | L/MWh | Water consumption per unit energy | 0-2500 | Yes |
| Land_Use_m2_per_MW | Float | m²/MW | Land requirement per MW capacity | 120-45000 | No |
| Technology_Maturity | String | - | Development stage | Emerging, Mature | No |
| Grid_Integration_Complexity | String | - | Grid connection difficulty | Very Low, Low, Medium, High | No |
| Fuel_Flexibility | String | - | Ability to use multiple fuels | Very Low, Low, Medium, High | No |
| Local_Manufacturing_Potential | String | - | Potential for Nigerian manufacturing | Very Low, Low, Medium, High | No |

**Notes:**
- LCOE calculated using 7% discount rate, 85% capacity factor for baseload
- Efficiency: LHV (Lower Heating Value) basis
- Ramp rate, startup time = N/A for renewables (intermittent)
- Water usage = N/A for hydro (non-consumptive use)
- SOFC data based on current commercial offerings (Bloom Energy, etc.)

---

## COMMON UNITS AND ABBREVIATIONS

### Energy Units
- **kW** = kilowatt (1,000 watts)
- **MW** = megawatt (1,000 kilowatts)
- **kWh** = kilowatt-hour (energy)
- **MWh** = megawatt-hour (1,000 kWh)
- **TJ** = terajoule (1,000,000 MJ)
- **BTU** = British Thermal Unit
- **MJ** = megajoule

### Gas Units
- **scf** = standard cubic feet
- **mscf** = thousand standard cubic feet
- **Bcf** = billion cubic feet
- **Tcf** = trillion cubic feet
- **m³** = cubic meters
- **HHV** = Higher Heating Value
- **LHV** = Lower Heating Value

### Volume Units
- **bbl** = barrel (oil) = 159 liters
- **MMbbl** = million barrels
- **L** = liter
- **kg** = kilogram
- **tonne** = metric ton = 1,000 kg

### Electrical Terms
- **Hz** = Hertz (frequency)
- **PSI** = pounds per square inch
- **SAIDI** = System Average Interruption Duration Index
- **SAIFI** = System Average Interruption Frequency Index
- **LCOE** = Levelized Cost of Electricity

### Organizations
- **NERC** = Nigerian Electricity Regulatory Commission
- **TCN** = Transmission Company of Nigeria
- **NNPC** = Nigerian National Petroleum Corporation
- **NGC** = Nigerian Gas Company
- **DPR** = Department of Petroleum Resources
- **DisCo** = Distribution Company
- **GenCo** = Generation Company
- **NBS** = National Bureau of Statistics

### Technology Terms
- **SOFC** = Solid Oxide Fuel Cell
- **CCGT** = Combined Cycle Gas Turbine
- **OCGT** = Open Cycle Gas Turbine
- **NIPP** = National Integrated Power Project
- **IPP** = Independent Power Producer
- **LNG** = Liquefied Natural Gas
- **CNG** = Compressed Natural Gas
- **LPG** = Liquefied Petroleum Gas

### Geographic
- **FCT** = Federal Capital Territory (Abuja)
- **States**: 36 states in Nigeria across 6 geopolitical zones
  - North West, North East, North Central
  - South West, South South, South East

---

## DATA TYPES LEGEND

- **String**: Text data
- **Integer**: Whole numbers
- **Float**: Decimal numbers
- **Date**: Date values (YYYY-MM-DD format)

---

## NULL VALUES

- **No**: Field must have a value (required)
- **Yes**: Field may be empty in some records (optional)

---

**Document Version:** 1.0  
**Last Updated:** October 21, 2024

For questions about field definitions or units, refer to the main README.md file.
