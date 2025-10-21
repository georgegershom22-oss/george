# Data Dictionary - Nigerian Energy & Resource Dataset

## Overview
This document provides detailed descriptions of all data fields, units, and structures used in the Nigerian Energy Dataset for SOFC analysis.

---

## 1. ELECTRICITY GRID DATA

### generation_capacity.json

#### Structure: national_capacity.installed_capacity
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| total | float | MW | Total installed generation capacity |
| by_source | object | - | Breakdown by energy source |
| by_source.{source}.capacity | float | MW | Installed capacity for specific source |
| by_source.{source}.percentage | float | % | Percentage of total capacity |
| by_source.{source}.plants | array | - | List of power plants |

#### Plant Details
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| name | string | - | Power plant name |
| capacity | float | MW | Installed capacity |
| location | string | - | State or region |
| status | string | - | Operational/Under construction/Planned |
| commissioned | integer | year | Year of commissioning |

#### Available Capacity
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| average_daily | float | MW | Average available capacity per day |
| peak_available | float | MW | Maximum available capacity |
| minimum_available | float | MW | Minimum available capacity |
| capacity_factor | float | ratio | Actual output / installed capacity |

### daily_load_allocation.json

#### Distribution Companies (DisCos)
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| disco | string | - | Distribution company name |
| region | string | - | Service area |
| allocated_load | float | MW | Daily allocated electricity |
| peak_demand | float | MW | Peak electricity demand |
| supply_gap | float | MW | Deficit (demand - allocation) |
| customers | integer | count | Number of customers |
| collection_efficiency | float | ratio | Revenue collection rate |

### reliability_metrics.json

#### Regional Metrics
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| SAIDI | float | minutes/year | System Average Interruption Duration Index |
| SAIFI | float | interruptions/year | System Average Interruption Frequency Index |
| average_daily_supply_hours | float | hours | Average electricity supply per day |
| outage_frequency_per_week | integer | count | Number of outages per week |
| grid_availability | float | ratio | Fraction of time grid is available |

### tariffs.json

#### Tariff Structure
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| customer_class | string | - | Residential/Commercial/Industrial |
| tariff_type | string | - | R1, R2, C1, D1, etc. |
| band | string | - | Service band (A-E) |
| supply_hours | string | hours/day | Expected daily supply |
| tariff | float | NGN/kWh | Electricity price |

---

## 2. FOSSIL FUEL DATA

### gas_reserves_production.json

#### Reserves
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| proven_reserves.total_tcf | float | Tcf | Trillion cubic feet of gas |
| proven_reserves.total_bcm | float | BCM | Billion cubic meters |
| reserve_life_years | float | years | Reserves / annual production |

#### Major Gas Fields
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| name | string | - | Gas field name |
| operator | string | - | Operating company |
| reserves_tcf | float | Tcf | Field reserves |
| production_mmscfd | float | MMSCFD | Million standard cubic feet per day |
| location | string | - | State/region |

### gas_flaring_data.json (CRITICAL FOR SOFC)

#### National Flaring Statistics
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| total_volume_mmscfd | float | MMSCFD | Daily flared gas volume |
| total_volume_bcf_per_year | float | BCF/year | Annual flared volume |
| co2_emissions_million_tons | float | Mt CO2/year | CO2 from flaring |
| economic_value_lost_usd | float | USD billion/year | Economic loss |
| **power_generation_potential_MW** | **float** | **MW** | **SOFC potential from flared gas** |

#### Major Flare Sites (KEY FOR SOFC DEPLOYMENT)
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| location | string | - | Flare site name |
| coordinates.lat/lon | float | degrees | GPS coordinates |
| **flare_volume_mmscfd** | **float** | **MMSCFD** | **Gas available for SOFC** |
| **sofc_potential_MW** | **float** | **MW** | **Calculated SOFC capacity** |
| population_affected | integer | people | Nearby population |
| nearby_communities | array | - | List of affected communities |

#### Flare Gas Composition
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| methane_CH4 | float | fraction | Methane content (0.85 typical) |
| heating_value | float | MJ/m³ | Lower heating value |
| suitability_for_sofc | string | - | Assessment for SOFC use |

### gas_pipeline_network.json

#### Pipeline Specifications
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| name | string | - | Pipeline name |
| length_km | float | km | Pipeline length |
| diameter_inches | float | inches | Pipe diameter |
| capacity_mmscfd | float | MMSCFD | Design capacity |
| current_throughput | float | MMSCFD | Actual flow rate |

### fuel_prices.json

#### Price Data
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| diesel.national_average | float | NGN/liter | Average diesel price |
| petrol.official_pump_price | float | NGN/liter | Petrol price |
| natural_gas.price_usd | float | USD/MMBtu | Gas price |
| **sofc_fuel_cost** | **float** | **NGN/kWh** | **Fuel cost for SOFC** |

---

## 3. RENEWABLE RESOURCES DATA

### agricultural_waste_data.json

#### Crop Residues
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| crop | string | - | Crop type |
| annual_production | float | million tons | Crop production |
| residue_type | string | - | Type of waste (husk, straw, etc.) |
| generation_million_tons | float | Mt/year | Residue generated |
| energy_content_MJ_per_kg | float | MJ/kg | Energy density |
| **biogas_yield_m3_per_ton** | **float** | **m³/ton** | **Biogas potential** |
| available_for_energy | float | Mt/year | Available after other uses |

### livestock_biogas_potential.json

#### Livestock Population
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| animal_type | string | - | Cattle/Goats/Sheep/etc. |
| population_millions | float | million heads | Animal population |
| manure_daily_per_head | float | kg/day | Manure production rate |
| **biogas_yield_m3_per_ton** | **float** | **m³/ton** | **Biogas from manure** |
| methane_content_percent | float | % | CH4 in biogas |

#### Biogas Production Potential
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| collectable_manure | float | Mt/year | Recoverable manure |
| biogas_potential | float | billion m³/year | Total biogas |
| **electricity_potential_MW** | **float** | **MW** | **Power generation capacity** |

---

## 4. CALCULATED FIELDS FOR SOFC ANALYSIS

### SOFC Technical Parameters
| Parameter | Value | Unit | Description |
|-----------|-------|------|-------------|
| Electrical Efficiency | 60 | % | SOFC electrical efficiency |
| Total CHP Efficiency | 85 | % | With heat recovery |
| Availability | 96 | % | Annual availability |
| Lifetime | 20 | years | System lifetime |

### SOFC Economic Parameters
| Parameter | Value | Unit | Description |
|-----------|-------|------|-------------|
| CAPEX Small Scale | 4,500 | USD/kW | 1-100 kW systems |
| CAPEX Medium Scale | 3,500 | USD/kW | 100-1,000 kW |
| CAPEX Large Scale | 2,800 | USD/kW | >1 MW systems |
| OPEX Fixed | 3 | % CAPEX/year | Annual O&M |
| Stack Replacement | 35 | % CAPEX | At 10 years |

### Key Conversion Factors
| From | To | Factor | Notes |
|------|-----|--------|-------|
| MMSCFD | m³/day | 28,316.8 | Standard conditions |
| m³ gas | kWh (SOFC) | 10.8 | At 60% efficiency |
| MW capacity | Households | 2,000 | 0.5 kW/household |
| tCO2 avoided | Cars equivalent | 0.2 | Cars removed from road |
| USD | NGN | 1,500 | Exchange rate (Jan 2025) |

---

## 5. DATA QUALITY NOTES

### Reliability Ratings
- **High**: Official government statistics, operator reports
- **Medium**: Industry estimates, survey data
- **Low**: Extrapolated or modeled data

### Update Frequency
- Electricity data: Monthly updates available
- Gas flaring: Satellite monitoring provides daily data
- Prices: Weekly updates from market sources
- Agricultural/Livestock: Annual census data

### Known Limitations
1. Grid reliability data based on surveys in some regions
2. Gas flaring volumes have ±15% uncertainty
3. Agricultural waste availability varies seasonally
4. Livestock manure collection rates are estimates

---

## 6. SOFC-SPECIFIC CALCULATIONS

### Power Generation from Flared Gas
```
SOFC Power (MW) = Gas Flow (MMSCFD) × 28.32 (m³/MSCF) × 
                   36.5 (MJ/m³) × 0.60 (efficiency) / 
                   (24 × 3.6) (MJ/MWh)
```

### Biogas to Electricity
```
Power (MW) = Biogas (m³/day) × 0.60 (CH4 fraction) × 
             35.8 (MJ/m³ CH4) × 0.60 (SOFC efficiency) / 
             (24 × 3.6) (MJ/MWh)
```

### LCOE Calculation
```
LCOE ($/MWh) = (CAPEX × CRF + Annual OPEX + Fuel Cost) / 
                Annual Generation
                
Where CRF = i(1+i)^n / ((1+i)^n - 1)
i = discount rate, n = lifetime years
```

---

*This data dictionary provides the foundation for understanding and utilizing the Nigerian Energy Dataset for SOFC techno-economic analysis. All data has been validated against multiple sources where possible.*