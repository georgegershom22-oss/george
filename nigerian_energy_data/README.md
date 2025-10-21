# Nigerian Energy & Resource Dataset

## Comprehensive Data for SOFC Techno-Economic Analysis

This dataset has been compiled specifically for the thesis: **"Harnessing Domestic Gas for Power: A Techno-Economic and Socio-Political Analysis of Solid Oxide Fuel Cells (SOFCs) in Mitigating Nigeria's Electricity Crisis"**

### Dataset Overview

This repository contains comprehensive energy data for Nigeria, focusing on:
- Electricity grid infrastructure and performance
- Natural gas resources and flaring data (critical for SOFC deployment)
- Renewable resource potential (agricultural waste and livestock for biogas)
- Economic and pricing data
- Technical specifications for energy infrastructure

### Directory Structure

```
nigerian_energy_data/
├── electricity_grid/          # Grid capacity, reliability, tariffs
├── fossil_fuel/              # Gas reserves, flaring, pipelines, prices
├── renewable_resources/      # Agricultural waste and livestock biogas data
├── analysis/                 # Python analysis tools and scripts
├── visualizations/           # Generated charts and dashboards
├── raw_data/                # Original unprocessed data (if available)
└── processed_data/          # Cleaned and processed datasets
```

### Key Datasets

#### 1. Electricity Grid Data

- **generation_capacity.json**: National generation capacity by source (13,014 MW installed, 4,500 MW available)
- **daily_load_allocation.json**: Distribution company allocations and demand gaps
- **reliability_metrics.json**: SAIDI, SAIFI metrics by region (national average: 50% availability)
- **tariffs.json**: Electricity tariffs by customer class and service band

#### 2. Fossil Fuel Data (Critical for SOFC)

- **gas_reserves_production.json**: 209.5 Tcf proven reserves, 8,000 MMSCFD production
- **gas_flaring_data.json**: **1,300 MMSCFD flared gas - 3,900 MW SOFC potential**
- **gas_pipeline_network.json**: Existing and planned pipeline infrastructure
- **fuel_prices.json**: Current diesel, petrol, and natural gas prices

#### 3. Renewable Resources (Biogas for SOFC)

- **agricultural_waste_data.json**: 125.5 million tons/year waste, 8,500 MW potential
- **livestock_biogas_potential.json**: 18.5 billion m³/year biogas potential, 6,200 MW

### Key Findings for SOFC Deployment

#### Total SOFC Deployment Potential: 18,600 MW
- From flared gas: 3,900 MW (currently wasted)
- From agricultural waste: 8,500 MW
- From livestock biogas: 6,200 MW

#### Economic Benefits
- Investment required: $56 billion
- Annual revenue potential: $16.7 billion
- Diesel displacement: 4.8 billion liters/year
- Foreign exchange savings: $3.4 billion/year

#### Environmental Impact
- CO₂ reduction: 53 million tons/year
- Elimination of gas flaring at 12+ major sites
- 95% reduction in local air pollutants vs diesel generators

#### Social Benefits
- 37.2 million households electrified
- 279,000 direct jobs created
- 837,000 indirect jobs created

### Analysis Tools

The repository includes Python analysis scripts:

1. **sofc_techno_economic_analyzer.py**: Comprehensive SOFC analysis tool
   - Calculates deployment potential at flare sites
   - Performs LCOE analysis
   - Generates national impact assessment
   - Creates visualizations and reports

2. **data_loader.py**: Data access and processing utility
   - Loads all JSON datasets as pandas DataFrames
   - Provides summary statistics
   - Exports to Excel format

### Quick Start

#### Installation
```bash
pip install -r requirements.txt
```

#### Run Analysis
```python
from analysis.sofc_techno_economic_analyzer import SOFCAnalyzer

# Initialize analyzer
analyzer = SOFCAnalyzer()

# Generate comprehensive report
report = analyzer.generate_report()

# Create visualizations
analyzer.generate_visualizations()

# Calculate national impact
impact = analyzer.calculate_national_impact()
```

#### Load Data
```python
from analysis.data_loader import NigerianEnergyDataLoader

# Initialize loader
loader = NigerianEnergyDataLoader()

# Get specific datasets
flaring_df = loader.get_flaring_sites_df()
generation_df = loader.get_generation_capacity_df()

# Export all data to Excel
loader.export_to_excel("nigeria_energy_data.xlsx")
```

### Data Sources

- Nigerian Electricity Regulatory Commission (NERC)
- Nigerian National Petroleum Corporation (NNPC)
- Transmission Company of Nigeria (TCN)
- World Bank Global Gas Flaring Reduction Partnership
- Food and Agriculture Organization (FAO)
- National Bureau of Statistics (NBS)
- Federal Ministry of Agriculture and Rural Development

### Critical Insights for SOFC Thesis

1. **Gas Flaring Sites**: 12 major sites with 1,300 MMSCFD wasted gas ideal for SOFC
2. **Grid Deficit**: 8,500 MW gap between demand and supply
3. **Diesel Dependence**: 14.5 million liters/day consumed for backup power
4. **Economic Loss**: $2.3 billion/year from gas flaring alone
5. **SOFC Advantages**: 
   - 60% efficiency vs 35% for gas turbines
   - Modular deployment (100 kW to 100 MW)
   - Low emissions and noise
   - Suitable for Nigeria's gas quality

### Visualization Outputs

The analysis tools generate:
- Flared gas SOFC deployment analysis charts
- LCOE comparison across technologies
- National impact dashboard (HTML interactive)
- Regional potential heat maps
- Investment and payback analyses

### Key Recommendations

1. **Priority Deployment**: Start with Bonny, Forcados, and Escravos terminals (730 MW, $1.38B investment)
2. **Policy Support**: Zero routine flaring mandate with SOFC as approved technology
3. **Financing**: Blend climate finance with commercial investment
4. **Local Content**: Establish SOFC assembly and maintenance facilities

### Contact and Citation

For questions about this dataset or collaboration opportunities, please reference:

**Dataset**: Nigerian Energy & Resource Data for SOFC Analysis (2025)
**Purpose**: Supporting thesis on SOFC deployment for Nigeria's electricity crisis
**Version**: 1.0
**Last Updated**: January 21, 2025

### License

This dataset is compiled from publicly available sources and is intended for academic and research purposes. Please cite original sources when using this data.

---

*This comprehensive dataset demonstrates that SOFC technology, utilizing Nigeria's wasted gas resources, presents a transformative opportunity to add 100%+ to current grid capacity while creating jobs, saving foreign exchange, and reducing emissions.*