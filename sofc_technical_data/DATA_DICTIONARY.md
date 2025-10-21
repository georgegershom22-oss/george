# SOFC Technical Dataset - Data Dictionary

This document provides detailed definitions for all variables in the SOFC Technical Dataset.

---

## 1. SOFC Performance Characteristics

**File:** `sofc_performance_characteristics.csv`  
**Records:** 224

| Variable Name | Type | Unit | Range | Description |
|--------------|------|------|-------|-------------|
| Manufacturer | String | - | - | SOFC system manufacturer name |
| System_Size_kW | Integer | kW | 100-2000 | Rated electrical power output of the SOFC system |
| Load_Percentage | Integer | % | 25-100 | Operating load as percentage of rated capacity |
| Actual_Power_Output_kW | Float | kW | 25-2000 | Actual electrical power output at specified load |
| Electrical_Efficiency_LHV | Float | - | 0.50-0.65 | Electrical efficiency based on fuel Lower Heating Value (unitless fraction) |
| Thermal_Efficiency | Float | - | 0.20-0.35 | Thermal/heat recovery efficiency (unitless fraction) |
| CHP_Total_Efficiency | Float | - | 0.75-0.95 | Combined Heat and Power total efficiency (unitless fraction) |
| Operating_Temperature_C | Float | °C | 600-850 | Typical SOFC stack operating temperature |
| Cell_Voltage_V | Float | V | 0.60-0.80 | Average single cell voltage under load |
| Power_Density_Volumetric_kW_per_m3 | Float | kW/m³ | 340-450 | Volumetric power density of SOFC stack |
| Power_Density_Area_kW_per_m2 | Float | kW/m² | 0.65-0.90 | Area-specific power density of SOFC stack |
| Stack_Degradation_pct_per_1000h | Float | %/1000h | 0.10-0.30 | Performance degradation rate per 1000 operating hours |
| Expected_Stack_Lifetime_hours | Integer | hours | 40000-80000 | Expected stack lifetime before replacement |
| System_Lifetime_years | Float | years | 15-25 | Expected total system lifetime with stack replacements |
| Fuel_Utilization_Factor | Float | - | 0.70-0.90 | Fraction of fuel input that is electrochemically converted |
| Air_Utilization_Factor | Float | - | 0.15-0.35 | Fraction of oxygen in inlet air that is consumed |

**Notes:**
- Efficiency values are based on Lower Heating Value (LHV) of fuel
- All efficiencies are unitless fractions (multiply by 100 for percentage)
- Load_Percentage: 100% = rated capacity, 75% = 75% of rated capacity, etc.
- Stack degradation is instantaneous rate; actual degradation varies with operating conditions

---

## 2. Fuel Flexibility Specifications

**File:** `sofc_fuel_flexibility.csv`  
**Records:** 77

| Variable Name | Type | Unit | Range | Description |
|--------------|------|------|-------|-------------|
| Manufacturer | String | - | - | SOFC system manufacturer name |
| Fuel_Type | String | - | - | Type of fuel (e.g., Pipeline Natural Gas, LPG, Bio-methane) |
| CH4_Content_pct | Float | % | 0-98 | Methane content in fuel by volume |
| C2H6_Content_pct | Float | % | 0-15 | Ethane content in fuel by volume |
| CO2_Content_pct | Float | % | 0-40 | Carbon dioxide content in fuel by volume |
| N2_Content_pct | Float | % | 0-50 | Nitrogen content in fuel by volume |
| H2_Content_pct | Float | % | 0-35 | Hydrogen content in fuel by volume |
| Sulfur_Content_ppm | Float | ppm | 1-500 | Sulfur content (parts per million by volume) |
| Lower_Heating_Value_MJ_per_kg | Float | MJ/kg | 35-55 | Lower Heating Value (LHV) of fuel |
| Reforming_Required | String | - | - | Type of reforming required (Internal/External/Partial) |
| Pre_Treatment_Requirements | String | - | - | Required fuel pre-treatment processes |
| Relative_Efficiency_Impact | Float | - | 0.85-1.05 | Efficiency multiplier relative to standard natural gas (1.0 = no impact) |
| Fuel_Compatibility_Rating | String | - | - | Qualitative compatibility rating (Excellent/Good/Moderate/Limited) |
| Degradation_Impact_Multiplier | Float | - | 1.0-1.5 | Stack degradation rate multiplier for this fuel (1.0 = no additional degradation) |
| Minimum_Purity_Requirements | String | - | - | Minimum fuel purity specifications |
| Cost_Premium_Factor | Float | - | 1.0-1.5 | Relative cost multiplier for fuel processing (1.0 = no additional cost) |

**Notes:**
- Fuel composition percentages should sum to ~100% (minor impurities may cause small variations)
- Sulfur_Content_ppm: SOFC typically requires <10 ppm sulfur (desulfurization needed for higher values)
- Relative_Efficiency_Impact: <1.0 indicates reduced efficiency, >1.0 indicates improved efficiency
- LHV (Lower Heating Value) excludes heat of vaporization of water in combustion products

---

## 3. Operational Characteristics

**File:** `sofc_operational_characteristics.csv`  
**Records:** 280

| Variable Name | Type | Unit | Range | Description |
|--------------|------|------|-------|-------------|
| Manufacturer | String | - | - | SOFC system manufacturer name |
| System_Size_kW | Integer | kW | 100-2000 | Rated electrical power output of the SOFC system |
| Operational_Mode | String | - | - | Operating mode (Base Load/Load Following/Peak Shaving/Backup Power/CHP Mode) |
| Cold_Start_Time_hours | Float | hours | 12-60 | Time required to reach full power from ambient temperature |
| Warm_Start_Time_hours | Float | hours | 1-8 | Time required to reach full power from reduced temperature standby |
| Hot_Start_Time_minutes | Float | minutes | 10-60 | Time required to reach full power from hot standby |
| Ramp_Up_Rate_pct_per_min | Float | %/min | 2-10 | Maximum rate of power increase (% of rated power per minute) |
| Ramp_Down_Rate_pct_per_min | Float | %/min | 3-12 | Maximum rate of power decrease (% of rated power per minute) |
| Minimum_Load_pct | Integer | % | 15-25 | Minimum stable operating load as percentage of rated power |
| Optimal_Load_pct | Integer | % | 75-100 | Optimal operating load for efficiency and longevity |
| Load_Change_Response_Time_sec | Float | seconds | 30-120 | Time to respond to 10% load change command |
| Cycling_Capability | String | - | - | Ability to handle start/stop cycles (Excellent/Good/Moderate/Limited) |
| Starts_Per_Year_Recommended | Integer | starts/year | 10-200 | Maximum recommended number of start/stop cycles per year |
| Mode_Suitability_Rating | String | - | - | Suitability for specified operational mode (Excellent/Good/Moderate/Limited) |
| Mode_Efficiency_Factor | Float | - | 0.90-1.05 | Efficiency multiplier for specified mode (1.0 = baseline) |
| Continuous_Operation_Capability | String | - | Yes/No | Ability to operate continuously without shutdown |
| Black_Start_Capable | String | - | Yes/No/Limited | Ability to start without external power (energize dead grid) |
| Grid_Forming_Capable | String | - | Yes/No/Limited | Ability to establish and maintain grid frequency/voltage |
| Island_Mode_Operation | String | - | Yes/No/Limited | Ability to operate disconnected from main grid |

**Notes:**
- Cold start: System at ambient temperature
- Warm start: System maintained at reduced temperature (typically 400-500°C)
- Hot start: System at or near operating temperature (>700°C)
- Ramp rates are instantaneous maximum rates; sustained ramps may be lower
- Cycling_Capability reflects thermal stress tolerance and control system sophistication

---

## 4. Degradation & Lifecycle Data

**File:** `sofc_degradation_lifecycle.csv`  
**Records:** 77

| Variable Name | Type | Unit | Range | Description |
|--------------|------|------|-------|-------------|
| Manufacturer | String | - | - | SOFC system manufacturer name |
| Operating_Hours | Integer | hours | 0-80000 | Cumulative operating hours |
| Operating_Years | Float | years | 0-9.1 | Cumulative operating years (assuming 8760 hours/year) |
| Cell_Voltage_Retention_pct | Float | % | 70-100 | Percentage of initial cell voltage retained |
| Power_Output_Retention_pct | Float | % | 70-100 | Percentage of initial power output retained |
| Efficiency_Retention_pct | Float | % | 85-100 | Percentage of initial efficiency retained |
| Degradation_Rate_Current_pct_per_1000h | Float | %/1000h | 0.10-0.25 | Current instantaneous degradation rate |
| Estimated_Remaining_Life_hours | Integer | hours | 0-80000 | Estimated remaining hours before end-of-life |
| Recommended_Maintenance_Action | String | - | - | Recommended maintenance at this operating point |
| End_of_Life_Criteria_Met | String | - | Yes/No/Approaching | Whether end-of-life threshold has been reached |

**Notes:**
- Degradation typically shows bi-linear behavior: higher initial rate, then lower steady-state rate
- Cell_Voltage_Retention: End-of-life typically defined as 80% retention (20% loss)
- Power_Output_Retention tracks cell voltage retention closely
- Efficiency_Retention degrades more slowly than voltage (typically 50% of voltage loss)
- Degradation rates are average values; actual rates vary with operating conditions
- End-of-life threshold: typically 80% voltage retention or 70% power retention

---

## 5. Nigeria-Specific Adaptations

**File:** `nigeria_specific_adaptations.csv`  
**Records:** 40

| Variable Name | Type | Unit | Range | Description |
|--------------|------|------|-------|-------------|
| Location | String | - | - | Nigerian city/region and climate descriptor |
| Fuel_Source | String | - | - | Available fuel source in this location |
| Average_Temperature_C | Float | °C | 24-38 | Average ambient temperature |
| Average_Humidity_pct | Float | % | 15-90 | Average relative humidity |
| Fuel_Availability_pct | Float | % | 40-95 | Percentage of time fuel is available |
| Fuel_Quality_Rating | String | - | - | Fuel quality consistency (Excellent/Good/Variable/Poor) |
| Typical_Sulfur_Content_ppm | Float | ppm | 2-200 | Typical sulfur content in local fuel |
| Corrosion_Risk_Level | String | - | - | Environmental corrosion risk (High/Moderate/Low) |
| Cooling_Requirements | String | - | - | Enhanced cooling needs (Enhanced/Standard/Minimal) |
| Performance_Derating_Factor | Float | - | 0.90-1.00 | Overall performance multiplier due to local conditions |
| Additional_Maintenance_Factor | Float | - | 1.0-1.4 | Maintenance frequency multiplier (1.0 = standard) |
| Recommended_BOP_Enhancements | String | - | - | Recommended Balance of Plant enhancements |
| Grid_Stability_Score | Integer | - | 1-10 | Grid reliability score (1=very poor, 10=excellent) |
| Estimated_Grid_Outages_per_month | Integer | outages/month | 10-40 | Estimated number of grid interruptions per month |
| Suitability_for_Island_Operation | String | - | - | Importance of island/off-grid capability (Essential/Beneficial/Optional) |
| Local_Technical_Support_Availability | String | - | - | Availability of technical expertise (Good/Moderate/Limited) |

**Notes:**
- Performance_Derating_Factor: Multiply rated performance by this factor for local conditions
- Additional_Maintenance_Factor: 1.2 = 20% more frequent maintenance than standard
- Grid_Stability_Score based on: frequency stability, voltage quality, outage frequency
- BOP = Balance of Plant (all components except fuel cell stack)
- High humidity + temperature = highest corrosion risk
- Coastal regions (Lagos, Port Harcourt) have highest humidity and corrosion risk

---

## 6. System Sizing Reference

**File:** `system_sizing_reference.csv`  
**Records:** 10

| Variable Name | Type | Unit | Range | Description |
|--------------|------|------|-------|-------------|
| Application_Type | String | - | - | Type of facility/application |
| Peak_Load_kW | Float | kW | 50-10000 | Maximum electrical demand |
| Average_Load_kW | Float | kW | 25-8000 | Average electrical demand |
| Load_Factor | Float | - | 0.40-0.90 | Ratio of average to peak load (unitless) |
| Daily_Load_Variation | String | - | - | Degree of daily load variability (Very Low/Low/Medium/High) |
| Heat_Demand_Level | String | - | - | Thermal energy requirement level (None/Low/Medium/High/Very High) |
| Recommended_SOFC_Size_BaseLoad_kW | Float | kW | 30-9000 | Recommended SOFC size for base load operation (110% of average) |
| Recommended_SOFC_Size_PeakShave_kW | Float | kW | 40-7000 | Recommended SOFC size for peak shaving (70% of peak) |
| Recommended_SOFC_Size_Backup_kW | Float | kW | 30-6000 | Recommended SOFC size for backup power (60% of peak, critical loads) |
| Number_of_Units_100kW | Integer | units | 1-90 | Number of 100kW modules required for base load |
| Number_of_Units_250kW | Integer | units | 1-36 | Number of 250kW modules required for base load |
| Number_of_Units_500kW | Integer | units | 1-18 | Number of 500kW modules required for base load |
| Estimated_Footprint_m2 | Float | m² | 5-60 | Estimated floor space requirement |
| Estimated_Volume_m3 | Float | m³ | 1-25 | Estimated volume requirement |
| CHP_Suitability | String | - | - | Suitability for CHP application (Excellent/Good/Moderate/Limited) |
| Annual_Operating_Hours | Integer | hours/year | 3500-8000 | Expected annual operating hours |
| Annual_Energy_Demand_MWh | Float | MWh/year | 200-70000 | Total annual electrical energy demand |
| Critical_Load_Percentage | Float | % | 30-80 | Percentage of load that is critical (must be maintained) |

**Notes:**
- Load_Factor = Average_Load / Peak_Load
- Base load sizing: 110% of average load for optimal efficiency and reliability margin
- Peak shaving sizing: 60-80% of peak load, grid supplies remainder of peak
- Backup sizing: Sized to critical loads only (typically 60-80% of total for most facilities)
- Module recommendations rounded up to ensure adequate capacity
- Footprint and volume are estimates; actual requirements vary by manufacturer and BOP design
- CHP suitability based on heat demand level and load factor
- Critical loads: Essential services that cannot be interrupted (e.g., hospital ICU, data center servers)

---

## Data Quality Notes

### Precision & Accuracy

**High Confidence (±2-5%):**
- Electrical efficiency
- Operating temperatures
- Power density
- Fuel composition impacts

**Medium Confidence (±10-15%):**
- Degradation rates (varies with operating conditions)
- Start-up times (manufacturer and size dependent)
- Ramp rates (control system dependent)

**Lower Confidence (±20-30%):**
- System lifetime (limited long-term field data)
- Nigeria-specific derating (limited local deployment data)
- Fuel availability percentages (regional variation)

### Missing Data Indicators

- **Blank/Empty:** Data not applicable or not available
- **"N/A":** Not applicable for this configuration
- **"Variable":** Highly dependent on site-specific conditions
- **"Limited":** Capability exists but not recommended for primary operation

### Units Convention

- **Efficiency:** Unitless fraction (0-1), NOT percentage (multiply by 100 for %)
- **Temperature:** Degrees Celsius (°C)
- **Power:** Kilowatts (kW) or Megawatts (MW)
- **Time:** Hours or minutes as specified
- **Pressure:** Not included (assumed adequate fuel pressure available)
- **Concentration:** ppm (parts per million) by volume for gases

---

## Recommended Data Validation

Before using this data for critical design decisions:

1. **Verify manufacturer specifications** directly for selected technology
2. **Conduct fuel analysis** for specific Nigerian gas source
3. **Measure site environmental conditions** (temperature, humidity, altitude)
4. **Assess grid stability** with local utility data
5. **Validate economic assumptions** with current market prices
6. **Consult local regulations** for emissions, grid interconnection, gas use

---

## Glossary

**APG:** Associated Petroleum Gas - natural gas found in association with crude oil deposits

**BOP:** Balance of Plant - all system components except the fuel cell stack

**CHP:** Combined Heat and Power - simultaneous generation of electricity and useful heat

**Cold Start:** Starting SOFC system from ambient temperature

**Degradation:** Gradual loss of performance over operating lifetime

**Fuel Utilization:** Fraction of fuel chemically converted in the fuel cell (vs. burned in afterburner)

**Hot Start:** Starting SOFC system from near-operating temperature

**Island Mode:** Operation disconnected from main electrical grid

**LHV:** Lower Heating Value - energy content of fuel excluding latent heat of water vapor

**Load Factor:** Ratio of average load to peak load

**Ramp Rate:** Rate of power change (increase or decrease)

**SOFC:** Solid Oxide Fuel Cell - ceramic fuel cell operating at 600-1000°C

**Stack:** Assembly of individual fuel cells connected in series/parallel

**Warm Start:** Starting SOFC system from reduced-temperature standby mode

---

**END OF DATA DICTIONARY**
