# SOFC Technical Dataset for Nigeria Power Generation

## Project Overview

This comprehensive dataset and analysis toolkit provides technical, technological, and operational data for Solid Oxide Fuel Cell (SOFC) systems, specifically tailored for addressing Nigeria's electricity crisis. The dataset supports techno-economic and socio-political analysis of SOFC deployment in Nigeria's challenging power sector environment.

## Dataset Description

### 1. Core Technical Data

#### Performance Characteristics (`data/raw/sofc_performance_characteristics.json`)
- **Electrical Efficiency**: Load-dependent efficiency curves (45-60% LHV)
- **Thermal Efficiency**: CHP configurations with up to 85% total efficiency
- **Degradation Rates**: Lifetime performance decay patterns (0.15-0.5%/1000h)
- **Temperature Dependencies**: Performance variations with operating temperature
- **Operating Ranges**: 650-950°C operating temperatures

#### Fuel Flexibility Specifications (`data/raw/fuel_flexibility_specifications.json`)
- **Fuel Types Covered**:
  - Pipeline Natural Gas (87.5% CH4)
  - Associated Gas (75.2% CH4) - critical for flare reduction
  - LPG (60% C3H8, 38% C4H10)
  - Biogas from Waste (55% CH4, 35% CO2)
  - Upgraded Biomethane (95% CH4)
- **Performance Metrics**: Efficiency, fuel utilization, reforming requirements
- **Nigeria-Specific Data**: Regional availability, flaring volumes, waste potential

#### Power Density & Operational (`data/raw/power_density_operational_characteristics.json`)
- **Power Density Data**:
  - Cell-level: 0.2-0.4 W/cm²
  - Stack-level: 1.5-4.2 kW/liter
  - System-level: 8-14 kW/m² footprint
- **Startup Characteristics**:
  - Cold start: 2-8 hours depending on design
  - Warm start: 45 minutes from 400°C
  - Hot standby: 10 minutes to full load
- **Ramp Rates**: 5%/min up, 10%/min down, 20%/sec emergency
- **Environmental Corrections**: Nigeria temperature/humidity impacts

### 2. Manufacturer Technical Specifications

The dataset includes detailed specifications from 7 major SOFC manufacturers:
- **Bloom Energy** (USA): 250-300kW systems, 53% efficiency
- **Mitsubishi Power** (Japan): Tubular SOFC, up to 90% CHP efficiency
- **Solid Power** (Germany): 1.5-50kW systems, 60% electrical efficiency
- **Convion** (Finland): 60-300kW modular systems, biogas capable
- **Ceres Power** (UK): Low-temperature (600°C) metal-supported cells
- **Elcogen** (Estonia): High power density cells and stacks
- **FuelCell Energy** (USA): 400-1500kW systems, grid-scale applications

Each manufacturer profile includes:
- Power output ranges
- Efficiency specifications
- Dimensional and weight data
- Fuel compatibility
- Warranty and maintenance requirements
- Nigeria suitability ratings (6.5-8.5/10)
- Estimated costs ($3,500-6,000/kW)

### 3. Nigeria-Specific Operational Scenarios

#### Power Sector Context
- Grid capacity: 12,522 MW installed, 7,652 MW available
- Peak demand: 15,000 MW (significant deficit)
- Grid collapse events: 206/year
- Regional demand profiles for Lagos, Kano, Port Harcourt, Abuja

#### Deployment Scenarios
1. **Industrial Backup Power** (500kW typical)
   - 75% capacity factor
   - 4.2-year payback
   - 22% IRR

2. **Commercial Building CHP** (250kW typical)
   - Combined 85% efficiency
   - Hotels, hospitals, shopping centers
   - Absorption cooling integration

3. **Telecom Tower Power** (10kW typical)
   - 99.9% availability
   - 42% cost savings vs diesel
   - 53,000 sites in Nigeria

4. **Agricultural Processing** (100kW typical)
   - Rice mills, cold storage, dairy
   - 25% post-harvest loss reduction
   - Biogas integration potential

5. **Residential Estate Microgrids** (500kW typical)
   - 200 homes served
   - Solar hybrid capability
   - 99.5% availability

6. **Data Center Prime Power** (2MW typical)
   - Tier 3 reliability (99.982%)
   - 30% energy cost savings
   - Green certification eligible

7. **Industrial Park Central Plants** (10MW typical)
   - 50 customers served
   - Multi-service provision (power, steam, cooling)
   - Smart grid integration

8. **Waste-to-Energy Facilities** (500kW typical)
   - 100 tonnes/day waste processing
   - 60% landfill diversion
   - Multiple revenue streams

### 4. Simulated Operational Data

The `scripts/data_generator.py` creates synthetic datasets including:
- **Time-series operational data** (8,760 hourly points)
- **Economic analysis** (24 scenarios)
- **Reliability analysis** (component-level MTBF/MTTR)
- **Sensitivity analysis** (5 key parameters)

## Data Structure

```
sofc_nigeria_dataset/
├── data/
│   ├── raw/                          # Original JSON datasets
│   │   ├── sofc_performance_characteristics.json
│   │   ├── fuel_flexibility_specifications.json
│   │   ├── power_density_operational_characteristics.json
│   │   └── manufacturer_technical_specifications.json
│   ├── processed/                    # Processed datasets
│   │   └── nigeria_operational_scenarios.json
│   └── simulated/                    # Generated synthetic data
│       ├── operational_timeseries.json
│       ├── economic_analysis.json
│       ├── reliability_analysis.json
│       └── sensitivity_analysis.json
├── scripts/
│   ├── data_visualization.py         # Visualization tools
│   └── data_generator.py             # Data generation tools
├── visualizations/                   # Output visualizations
└── docs/                             # Documentation

```

## Key Technical Findings

### Performance Metrics
- **Electrical Efficiency**: 50-60% (LHV) at rated power
- **CHP Total Efficiency**: Up to 85-90%
- **Degradation**: 0.15-0.5% per 1000 hours
- **Availability**: 95-97.5% for commercial systems
- **Startup Time**: 2-8 hours from cold, 10 minutes from hot standby

### Nigeria-Specific Considerations
- **Temperature Derating**: 3-12% power loss at 40-45°C ambient
- **Fuel Availability**: Abundant natural gas and associated gas
- **Grid Support**: Critical for weak grid stabilization
- **Economic Viability**: 3-5 year payback for most applications

### Cost Projections
- **Current (2023)**: $4,500/kW
- **2025 Projected**: $3,500/kW
- **2030 Target**: $2,000/kW

## Usage Instructions

### 1. Installation

```bash
# Clone or download the dataset
cd sofc_nigeria_dataset

# Install required Python packages
pip install -r requirements.txt
```

### 2. Generate Synthetic Data

```bash
cd scripts
python data_generator.py
```

This will create:
- Operational time-series data (365 days)
- Economic scenarios for different applications
- Reliability analysis
- Sensitivity analysis

### 3. Create Visualizations

```bash
cd scripts
python data_visualization.py
```

This generates:
- Efficiency curves
- Fuel comparison charts
- Power density analysis
- Manufacturer comparisons
- Nigeria deployment scenarios

### 4. Access Raw Data

All JSON files can be directly loaded:

```python
import json

with open('data/raw/sofc_performance_characteristics.json', 'r') as f:
    performance_data = json.load(f)
```

## Applications

This dataset supports:

1. **Techno-Economic Analysis**
   - LCOE calculations
   - NPV and IRR analysis
   - Payback period estimation
   - Sensitivity analysis

2. **System Sizing and Design**
   - Load matching
   - Fuel selection
   - Technology selection
   - Integration planning

3. **Policy Development**
   - Deployment targets
   - Incentive structures
   - Grid code requirements
   - Environmental regulations

4. **Investment Decisions**
   - Market assessment
   - Risk analysis
   - Project financing
   - Technology selection

5. **Academic Research**
   - Performance modeling
   - Optimization studies
   - Environmental impact assessment
   - Grid integration analysis

## Data Sources and Methodology

### Primary Sources
- Academic literature from peer-reviewed journals
- Technical reports from manufacturers
- International Energy Agency (IEA) reports
- Nigeria power sector statistics (TCN, NERC)
- Industry white papers and case studies

### Data Generation Methodology
- **Performance Data**: Based on published specifications and academic literature
- **Cost Data**: Industry surveys and public financial reports
- **Operational Data**: Synthetic generation using realistic load profiles and statistical distributions
- **Nigeria Context**: Government statistics, World Bank data, local energy reports

### Validation Approach
- Cross-referenced multiple sources for consistency
- Applied engineering principles for synthetic data
- Used conservative estimates where data was uncertain
- Incorporated real-world operational constraints

## Limitations and Assumptions

1. **Technology Maturity**: Data reflects current commercial technology (2023-2024)
2. **Nigeria Context**: Assumes gradual infrastructure improvement
3. **Fuel Quality**: Assumes adequate fuel processing available
4. **Economic Parameters**: Based on current exchange rates and energy prices
5. **Grid Conditions**: Assumes minimum grid stability for operation

## Future Updates

Planned enhancements include:
- Real operational data integration
- Advanced degradation models
- Dynamic pricing scenarios
- Climate change impact assessment
- Hybrid system configurations
- Green hydrogen integration

## Citation

If you use this dataset in your research, please cite:

```
SOFC Technical Dataset for Nigeria Power Generation (2025)
Comprehensive Technical and Operational Data for Solid Oxide Fuel Cells
in Nigeria's Electricity Sector
Version 1.0, October 2025
```

## License

This dataset is provided for research and educational purposes. Commercial use requires permission.

## Contact

For questions, corrections, or contributions, please contact the research team.

## Acknowledgments

This dataset was developed to support research on "Harnessing Domestic Gas for Power: A Techno-Economic and Socio-Political Analysis of Solid Oxide Fuel Cells (SOFCs) in Mitigating Nigeria's Electricity Crisis."

---

*Last Updated: October 21, 2025*
*Version: 1.0*