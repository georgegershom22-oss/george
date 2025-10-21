# Quick Start Guide - SOFC Economic Dataset

## Overview

This comprehensive dataset supports techno-economic analysis of Solid Oxide Fuel Cell (SOFC) systems for power generation in Nigeria, comparing them with diesel generators and solar+battery systems.

**Project:** Harnessing Domestic Gas for Power: A Techno-Economic and Socio-Political Analysis of SOFCs in Mitigating Nigeria's Electricity Crisis

---

## Dataset Files

### Core Data (CSV Files)

1. **`sofc_system_costs.csv`** - SOFC capital and operational costs
   - 15 configurations (100-1000 kW)
   - CAPEX, OPEX, stack replacement costs
   - Multiple scenarios (conservative, base, optimistic)

2. **`diesel_generator_costs.csv`** - Diesel generator costs
   - 15 configurations (100-1000 kW)
   - CAPEX, fuel consumption, maintenance
   - Nigeria-specific pricing

3. **`solar_battery_costs.csv`** - Solar PV + Battery systems
   - 15 configurations (100-1000 kW)
   - Solar panels + 4-6 hour battery storage
   - Installation and replacement costs

4. **`financial_parameters.csv`** - Financial & economic parameters
   - 34 parameters
   - Exchange rates (USD/NGN: 1,625)
   - Inflation, interest rates, tariffs
   - Multiple scenarios included

5. **`fuel_costs_comparison.csv`** - Fuel cost data
   - 13 fuel types
   - Natural gas, diesel, LNG, hydrogen, etc.
   - Price per kWh equivalent

6. **`operational_scenarios.csv`** - Operating scenarios
   - 22 scenarios
   - Different capacity factors (18-98%)
   - Various use cases (industrial, commercial, telecom, etc.)

7. **`incentives_and_policies.csv`** - Policy framework
   - 21 policy instruments
   - Tax incentives, subsidies, regulations
   - Current and proposed policies

8. **`emissions_comparison.csv`** - Environmental data
   - 17 technology-fuel combinations
   - CO₂, CH₄, NOₓ, SOₓ, PM2.5 emissions
   - Lifecycle GHG emissions

---

## Quick Analysis Results

### For 500 kW Systems (Base Case):

| Metric | SOFC | Diesel | Solar+Battery |
|--------|------|--------|---------------|
| **CAPEX** | $1,600,000 | $275,000 | $1,095,000 |
| **CAPEX/kW** | $3,200/kW | $550/kW | $2,190/kW |
| **LCOE** | **$0.116/kWh** | $0.387/kWh | $0.177/kWh |
| **Capacity Factor** | 85% | 70% | 22% |
| **Annual Energy** | 3,723 MWh | 3,066 MWh | 964 MWh |
| **Annual Fuel Cost** | $72,060 | $1,111,425 | $0 |
| **NPV (20yr)** | **$62,192** | -$6,624,745 | -$365,569 |
| **IRR** | **10.57%** | Negative | 5.34% |
| **Payback** | **8.2 years** | >15 years | 13.6 years |

### Key Findings:

✅ **SOFC has the LOWEST LCOE** at $0.116/kWh (half of diesel, lower than solar)

✅ **SOFC is POSITIVE NPV** - profitable over project lifetime

✅ **Diesel is MOST EXPENSIVE** to operate due to high fuel costs

✅ **SOFC best for baseload** (high capacity factor applications)

✅ **Solar best for daytime loads** with lower upfront cost than SOFC

---

## Using the Analysis Tool

### Installation

```bash
# Install required packages
pip install -r requirements.txt

# Or install individually
pip install pandas numpy matplotlib seaborn
```

### Basic Usage

```python
from tea_analysis import SOFCEconomicAnalysis

# Initialize
analysis = SOFCEconomicAnalysis('economic_data')

# Analyze individual technology (500 kW system)
sofc_results = analysis.sofc_analysis(500)
diesel_results = analysis.diesel_analysis(500)
solar_results = analysis.solar_analysis(500)

# Compare across system sizes
comparison = analysis.comparative_analysis([100, 250, 500, 750, 1000])

# Sensitivity analysis
sensitivity = analysis.sensitivity_analysis(500, parameter='fuel_price')

# Generate comprehensive report
analysis.generate_summary_report()
```

### Command Line

```bash
# Run complete analysis
python tea_analysis.py

# This will:
# - Load all datasets
# - Analyze 500 kW base case for all technologies
# - Compare 250, 500, 1000 kW systems
# - Generate summary report
# - Export comparison_results.csv
```

---

## Key Data Points

### SOFC Technology (500 kW)

**CAPEX Breakdown:**
- Stack: $800,000 (50%)
- Balance of Plant: $640,000 (40%)
- Installation: $160,000 (10%)
- **Total: $1,600,000**

**Annual OPEX:**
- Natural gas fuel: ~$72,000
- Maintenance: ~$55,000
- Labor: ~$25,000
- **Total: ~$152,000/year**

**Stack Replacement:** $725,000 every 7 years

**Efficiency:** 55% electrical, 65% total (with heat recovery)

### Diesel Generator (500 kW)

**CAPEX:** $275,000 (much lower upfront)

**Annual OPEX:**
- Diesel fuel: ~$1,111,000 (at $1.45/L)
- Maintenance: ~$30,000
- **Total: ~$1,141,000/year**

**Fuel Consumption:** 0.26 L/kWh

**Major Overhaul:** $58,000 every 5 years

### Solar + Battery (500 kW)

**CAPEX Breakdown:**
- Solar PV: $540,000
- Battery (2000 kWh): $330,000
- Inverter: $90,000
- Installation: $75,000
- **Total: $1,095,000**

**Annual OPEX:** $16,000 (very low - no fuel!)

**Battery Replacement:** $290,000 every 10 years

**Capacity Factor:** 22% (limited by solar availability)

---

## Financial Parameters (Nigeria Context)

**Current (October 2024):**
- Inflation: 24.5%
- Interest rate: 26.75%
- USD/NGN: 1,625 (official)
- Natural gas: $3.20/MSCF (industrial)
- Diesel: $1.45/L (official)
- Electricity tariff: $0.10-0.12/kWh

**Project Finance:**
- Discount rate: 10% (real), 15% (nominal)
- WACC: 12.5-20% (depending on risk)
- Corporate tax: 30%
- SOFC lifetime: 20 years
- Diesel lifetime: 15 years
- Solar lifetime: 25 years

---

## Use Case Recommendations

### ✅ SOFC is BEST for:
- **Baseload power** (>80% capacity factor)
- **24/7 operations** (manufacturing, data centers)
- **Industrial facilities** with continuous loads
- **Locations with reliable gas supply**
- **Combined heat & power** applications
- **Low emissions requirements**
- **Long-term cost stability**

### ✅ Diesel is BEST for:
- **Backup/emergency power** (<40% capacity factor)
- **Peak shaving** applications
- **Temporary installations**
- **Remote areas without gas**
- **Lower upfront capital** constraints
- **Short-term projects** (<5 years)

### ✅ Solar+Battery is BEST for:
- **Daytime loads** (offices, retail)
- **Environmental mandates**
- **High solar irradiance locations**
- **Declining cost trajectory**
- **Zero fuel cost** preference
- **Grid independence** goals

---

## Scenario Analysis

The dataset includes multiple scenarios for different conditions:

### By Grid Reliability:
- **Base Case** (35% grid availability)
- **Optimistic** (45% grid availability)
- **Pessimistic** (25% grid availability)

### By Operation:
- **High Utilization** (95% capacity factor)
- **Island Mode** (off-grid, 0% grid)
- **Hybrid** (with grid support)

### By Application:
- Industrial 24/7
- Commercial office hours
- Telecom towers
- Data centers
- Healthcare facilities
- Mining operations

---

## Sensitivity Insights

### SOFC LCOE Most Sensitive To:
1. **Natural gas price** (±30% → LCOE changes ±12%)
2. **Capacity factor** (±20% → LCOE changes ±20%)
3. **CAPEX** (±30% → LCOE changes ±18%)
4. **Discount rate** (±30% → LCOE changes ±10%)

### Diesel LCOE Most Sensitive To:
1. **Diesel fuel price** (±30% → LCOE changes ±21%)
2. **Capacity factor** (±20% → LCOE changes ±20%)
3. **Operating hours** (higher = better economics)

### When SOFC Breaks Even with Diesel:
- At **>40% capacity factor**, SOFC LCOE < Diesel LCOE
- At **>60% capacity factor**, SOFC has strong advantage
- At **>80% capacity factor**, SOFC is clearly superior

---

## Policy Incentives Available

### Currently Active:
- ✅ **Import duty exemption** (0% on renewable energy equipment)
- ✅ **Pioneer status** (3-5 year corporate tax holiday)
- ✅ **Accelerated depreciation** (95% in year 1)
- ✅ **Gas supply obligation** ($2.50-3.20/MSCF guaranteed)
- ✅ **CBN Green Bond** (12% interest financing)
- ✅ **Power Purchase Agreements** (offtake guarantee)

### Proposed/Potential:
- 📋 **Investment tax credit** (30% of CAPEX proposed)
- 📋 **Carbon pricing** ($10-25/tCO2 by 2030)
- 📋 **Technology innovation fund** (R&D grants)

---

## Environmental Impact

### Emissions Comparison (kg CO₂e per MWh):

| Technology | CO₂e/MWh | vs Nigerian Grid |
|------------|----------|------------------|
| **SOFC (natural gas)** | **425** | **-39%** |
| Diesel generator | 869 | +25% |
| Nigerian grid average | 693 | baseline |
| Solar PV | 52 | -92% |

**Annual CO₂ Reduction (500 kW SOFC vs Diesel):**
- SOFC: 1,582 tonnes CO₂e/year
- Diesel: 2,665 tonnes CO₂e/year
- **Reduction: 1,083 tonnes/year** (40% reduction)

---

## Data Quality Assessment

| Dataset | Quality Rating | Notes |
|---------|---------------|-------|
| SOFC Costs | ★★★☆☆ | Limited Nigerian data, based on international |
| Diesel Costs | ★★★★★ | Extensive local market data |
| Solar Costs | ★★★★☆ | Good data, rapidly declining costs |
| Financial Params | ★★★★☆ | Official sources, volatile conditions |
| Fuel Costs | ★★★★★ | Well-established, regularly updated |

---

## Next Steps

### For Researchers:
1. Read **`README.md`** for comprehensive documentation
2. Review **`data_sources_bibliography.md`** for all sources
3. Run **`tea_analysis.py`** for baseline analysis
4. Modify scenarios in **`operational_scenarios.csv`**
5. Conduct sensitivity analyses

### For Investors:
1. Review **`economic_analysis_summary.txt`** for key findings
2. Check **`comparison_results.csv`** for size comparisons
3. Assess **`incentives_and_policies.csv`** for available support
4. Evaluate project-specific parameters
5. Run custom scenarios

### For Policy Makers:
1. Review LCOE comparisons across technologies
2. Assess **`emissions_comparison.csv`** for environmental impact
3. Evaluate **`incentives_and_policies.csv`** effectiveness
4. Consider gas infrastructure development
5. Assess subsidy/incentive requirements

---

## Files Generated by Analysis

After running `tea_analysis.py`:
- ✅ **`economic_analysis_summary.txt`** - Comprehensive text report
- ✅ **`comparison_results.csv`** - Cross-technology comparison table

---

## Support & Citation

### How to Cite:
```
Economic & Financial Data for SOFC Techno-Economic Analysis in Nigeria (2024).
Dataset for: "Harnessing Domestic Gas for Power: A Techno-Economic and 
Socio-Political Analysis of Solid Oxide Fuel Cells (SOFCs) in Mitigating 
Nigeria's Electricity Crisis"
Version 1.0, October 2024.
```

### Additional Documentation:
- **`README.md`** - Full documentation (comprehensive)
- **`data_sources_bibliography.md`** - All 50+ sources with details
- **`QUICKSTART.md`** - This file

---

## Important Notes

⚠️ **Data Currency:** October 2024 - Update exchange rates and fuel prices regularly

⚠️ **Exchange Rate Volatility:** USD/NGN subject to significant fluctuations

⚠️ **SOFC Experience:** Limited commercial deployments in Nigeria - costs based on international data

⚠️ **Policy Changes:** Nigerian incentive framework evolving - verify current status

⚠️ **Technology Costs:** SOFC and battery costs declining rapidly - dataset may be conservative

---

## Quick Command Reference

```bash
# View dataset summary
head -20 README.md

# Check SOFC costs
cat sofc_system_costs.csv | column -t -s,

# Run analysis
python tea_analysis.py

# View results
cat economic_analysis_summary.txt

# Compare technologies
cat comparison_results.csv

# Check financial parameters
cat financial_parameters.csv | grep -E "Inflation|Exchange|Gas_Price"
```

---

## Contact

**Project Focus:** SOFC techno-economic analysis for Nigeria
**Dataset Version:** 1.0
**Last Updated:** October 21, 2024
**Status:** Complete and ready for analysis

---

## Summary Statistics

📊 **Total Dataset:**
- **8 CSV files** with comprehensive data
- **100+ data points** across technologies
- **34 financial parameters** for Nigeria
- **22 operational scenarios**
- **21 policy instruments**
- **50+ data sources** cited
- **1000+ individual data entries**

💰 **Economic Range:**
- CAPEX: $400 - $5,200/kW
- LCOE: $0.10 - $0.40/kWh
- Project sizes: 100 - 1,000 kW
- Lifetimes: 15 - 25 years

🎯 **Key Result:** 
**SOFC shows lowest LCOE ($0.116/kWh) for baseload applications**, making it economically competitive with diesel ($0.387/kWh) and solar+battery ($0.177/kWh) in Nigeria.

---

**Ready to start? Run:** `python tea_analysis.py`

