# Data Dictionary - Nigerian SME Innovation Secondary Dataset

## Table of Contents
1. [Macroeconomic Variables](#macroeconomic-variables)
2. [Industry-Specific Variables](#industry-specific-variables)
3. [Technology Adoption Variables](#technology-adoption-variables)
4. [Measurement Units and Scales](#measurement-units-and-scales)
5. [Data Types and Formats](#data-types-and-formats)

---

## Macroeconomic Variables

### GDP Growth Rate Dataset

| Variable Name | Description | Type | Unit | Range | Notes |
|--------------|-------------|------|------|--------|--------|
| year | Calendar year | Integer | Year | 2015-2024 | - |
| quarter | Quarter of year | String | Q1-Q4 | Q1-Q4 | - |
| gdp_growth_rate | Real GDP growth rate | Float | % | -6.10 to 5.01 | Year-on-year growth |
| gdp_nominal_billion_naira | Nominal GDP value | Float | Billion ₦ | 23,951 to 110,234 | Current prices |
| gdp_real_billion_naira | Real GDP value | Float | Billion ₦ | 15,417 to 19,193 | Constant 2010 prices |
| oil_gdp_growth | Oil sector GDP growth | Float | % | -22.67 to 25.89 | Includes crude petroleum & natural gas |
| non_oil_gdp_growth | Non-oil sector GDP growth | Float | % | -6.05 to 4.77 | All sectors excluding oil |
| agriculture_gdp | Agriculture sector growth | Float | % | 1.20 to 4.54 | Crop, livestock, forestry, fishing |
| manufacturing_gdp | Manufacturing sector growth | Float | % | -8.78 to 4.17 | All manufacturing activities |
| services_gdp | Services sector growth | Float | % | -6.92 to 9.28 | Trade, ICT, finance, etc. |
| sme_contribution_percent | SME contribution to GDP | Float | % | 44.8 to 51.5 | Estimated SME share |

### Inflation Rates Dataset

| Variable Name | Description | Type | Unit | Range | Notes |
|--------------|-------------|------|------|--------|--------|
| year | Calendar year | Integer | Year | 2015-2024 | - |
| month | Month name | String | Month | Jan-Dec | - |
| headline_inflation | Consumer Price Index inflation | Float | % | 8.36 to 34.19 | Year-on-year change |
| food_inflation | Food sub-index inflation | Float | % | 9.25 to 40.87 | Food and non-alcoholic beverages |
| core_inflation | Core inflation excluding food & energy | Float | % | 7.75 to 28.78 | All items less farm produce & energy |
| imported_inflation | Imported goods inflation | Float | % | 9.0 to 21.8 | Imported items basket |
| energy_inflation | Energy and fuel inflation | Float | % | 6.5 to 19.8 | Electricity, gas, fuel |
| transport_inflation | Transportation inflation | Float | % | 7.8 to 20.6 | Transport services and vehicles |
| health_inflation | Healthcare inflation | Float | % | 6.8 to 19.6 | Medical services and products |
| education_inflation | Education services inflation | Float | % | 7.7 to 20.5 | School fees and education costs |
| communication_inflation | Communication services inflation | Float | % | 3.7 to 16.5 | Telecom and postal services |
| housing_utilities | Housing and utilities inflation | Float | % | 7.4 to 20.2 | Rent, maintenance, utilities |
| clothing_footwear | Clothing and footwear inflation | Float | % | 7.7 to 20.5 | Apparel and shoes |

### Interest Rates Dataset

| Variable Name | Description | Type | Unit | Range | Notes |
|--------------|-------------|------|------|--------|--------|
| monetary_policy_rate | Central Bank policy rate | Float | % | 11.00 to 27.25 | MPR set by CBN |
| prime_lending_rate | Bank prime lending rate | Float | % | 13.83 to 22.67 | Rate for prime customers |
| maximum_lending_rate | Maximum lending rate | Float | % | 26.71 to 32.51 | Ceiling rate for loans |
| interbank_call_rate | Overnight interbank rate | Float | % | 1.50 to 25.13 | Bank-to-bank lending |
| treasury_bill_91_day | 91-day T-bill rate | Float | % | 0.34 to 21.12 | Short-term government security |
| treasury_bill_182_day | 182-day T-bill rate | Float | % | 1.75 to 20.50 | Medium-term government security |
| treasury_bill_364_day | 364-day T-bill rate | Float | % | 2.41 to 20.18 | Long-term government security |
| savings_deposit_rate | Savings account rate | Float | % | 3.63 to 4.87 | Average savings rate |
| sme_lending_rate_average | Average SME lending rate | Float | % | 28.4 to 35.1 | Typical rate for SME loans |

### Broadband Penetration Dataset

| Variable Name | Description | Type | Unit | Range | Notes |
|--------------|-------------|------|------|--------|--------|
| state | Nigerian state name | String | Name | 36 states + FCT | Geographic unit |
| region | Geopolitical zone | String | Zone | 6 zones | North/South divisions |
| 2015-2024 | Annual penetration rate | Float | % | 3.8 to 92.3 | Year columns |
| urban_penetration_2024 | Urban broadband penetration | Float | % | 15.7 to 95.8 | Cities and towns |
| rural_penetration_2024 | Rural broadband penetration | Float | % | 5.8 to 78.5 | Rural areas |
| 3g_coverage | 3G network coverage | Float | % | 50.0 to 98.5 | Population covered |
| 4g_coverage | 4G/LTE network coverage | Float | % | 22.9 to 94.2 | Population covered |
| 5g_coverage | 5G network coverage | Float | % | 0.0 to 15.8 | Population covered |
| fiber_optic_coverage | Fiber optic availability | Float | % | 4.3 to 52.3 | Premises passed |

### Ease of Doing Business Dataset

| Variable Name | Description | Type | Unit | Range | Notes |
|--------------|-------------|------|------|--------|--------|
| global_rank | World ranking | Integer | Rank | 129-170 | Out of 190 economies |
| sub_saharan_africa_rank | Regional ranking | Integer | Rank | 23-36 | Out of 48 SSA countries |
| overall_score | Distance to frontier score | Float | Score | 44.7 to 57.8 | 0-100 scale |
| starting_business_score | Starting a business score | Float | Score | 68.5 to 93.5 | Procedures, time, cost |
| getting_credit | Getting credit score | Float | Score | 25.0 to 82.5 | Credit information, rights |
| protecting_minority_investors | Investor protection score | Float | Score | 42.5 to 69.8 | Disclosure, liability |
| paying_taxes | Paying taxes score | Float | Score | 47.8 to 78.5 | Payments, time, rate |
| trading_across_borders | Trade facilitation score | Float | Score | 20.0 to 31.8 | Time and cost to trade |
| regulatory_quality_index | Regulatory environment | Float | Index | -0.92 to -0.50 | World Bank governance |
| corruption_perception_index | Corruption levels | Integer | Score | 24 to 28 | Transparency International |

---

## Industry-Specific Variables

### Sectoral Growth Rates Dataset

| Variable Name | Description | Type | Unit | Range | Notes |
|--------------|-------------|------|------|--------|--------|
| sector | Main economic sector | String | Name | 6 sectors | Primary classification |
| subsector | Detailed subsector | String | Name | 30+ subsectors | Secondary classification |
| 2015-2024_Q2 | Period growth rates | Float | % | -59.84 to 48.42 | Year-on-year growth |
| sme_contribution_percent | SME share in sector | Float | % | 5.2 to 85.6 | SME participation |
| employment_share_percent | Sector employment share | Float | % | 0.6 to 23.5 | Of total employment |
| innovation_index | Sector innovation score | Float | Index | 2.1 to 4.9 | 1-5 scale |
| digitalization_rate | Digital adoption rate | Float | % | 5.3 to 72.3 | Technology usage |

### SME Landscape Dataset

| Variable Name | Description | Type | Unit | Range | Notes |
|--------------|-------------|------|------|--------|--------|
| total_smes_millions | Total SME count | Float | Millions | 37.07 to 52.69 | Registered and informal |
| micro_enterprises_percent | Micro enterprise share | Float | % | 98.3 to 98.8 | <10 employees |
| small_enterprises_percent | Small enterprise share | Float | % | 1.0 to 1.5 | 10-49 employees |
| medium_enterprises_percent | Medium enterprise share | Float | % | 0.2 | 50-199 employees |
| formal_sector_percent | Formal registration | Float | % | 8.4 to 13.2 | Officially registered |
| informal_sector_percent | Informal operations | Float | % | 86.8 to 91.6 | Unregistered businesses |
| sme_gdp_contribution_percent | GDP contribution | Float | % | 48.03 to 51.35 | Economic output share |
| sme_employment_millions | Total employment | Float | Millions | 59.88 to 78.85 | Direct jobs created |
| sme_export_value_billion_usd | Export value | Float | Billion $ | 0.52 to 1.72 | International trade |
| women_owned_smes_percent | Female ownership | Float | % | 41.0 to 43.7 | Gender distribution |
| youth_owned_smes_percent | Youth ownership | Float | % | 29.5 to 34.9 | Under 35 years |
| tech_enabled_smes_percent | Technology adoption | Float | % | 8.5 to 76.5 | Using digital tools |
| fintech_adoption_rate | Fintech usage | Float | % | 5.2 to 69.8 | Digital financial services |
| e_commerce_participation | E-commerce activity | Float | % | 3.8 to 52.3 | Online sales/purchases |

---

## Technology Adoption Variables

### Mobile Money & Fintech Dataset

| Variable Name | Description | Type | Unit | Range | Notes |
|--------------|-------------|------|------|--------|--------|
| mobile_money_accounts_millions | Active MM accounts | Float | Millions | 21.5 to 253.2 | Registered users |
| mobile_money_agents_thousands | Agent network size | Float | Thousands | 102.3 to 1716.2 | Service points |
| mobile_money_transaction_volume_billion_naira | Transaction count | Float | Billion | 18.5 to 957.2 | Number of transactions |
| mobile_money_transaction_value_billion_naira | Transaction value | Float | Billion ₦ | 245.8 to 25508.6 | Monetary value |
| fintech_companies | Fintech firm count | Integer | Count | 45 to 2138 | Licensed operators |
| digital_wallet_users_millions | E-wallet users | Float | Millions | 5.2 to 262.5 | Active wallets |
| pos_terminals_thousands | POS deployment | Float | Thousands | 155.4 to 3618.8 | Active terminals |
| internet_banking_users_millions | Online banking users | Float | Millions | 8.5 to 326.5 | Active users |
| ussd_banking_users_millions | USSD banking users | Float | Millions | 12.3 to 483.3 | Mobile banking via USSD |
| financial_inclusion_rate | Financial inclusion | Float | % | 56.8 to 93.6 | Adult population |
| unbanked_population_millions | Unbanked adults | Float | Millions | 52.3 to 7.7 | Without accounts |

### ICT Development Index Dataset

| Variable Name | Description | Type | Unit | Range | Notes |
|--------------|-------------|------|------|--------|--------|
| ict_development_index | Composite ICT score | Float | Index | 2.20 to 4.42 | 0-10 scale |
| ict_access_index | ICT infrastructure | Float | Index | 3.82 to 6.08 | Access to ICT |
| ict_use_index | ICT usage intensity | Float | Index | 1.25 to 4.22 | Actual usage |
| ict_skills_index | Digital skills level | Float | Index | 4.73 to 6.18 | Education and literacy |
| global_rank | World ICT ranking | Integer | Rank | 124 to 143 | Out of 176 countries |
| africa_rank | African ranking | Integer | Rank | 19 to 28 | Out of 44 countries |
| mobile_cellular_subscriptions_per_100 | Mobile penetration | Float | Per 100 | 82.2 to 114.3 | Mobile subscriptions |
| internet_users_percent | Internet penetration | Float | % | 27.5 to 70.2 | Population online |
| fixed_broadband_subscriptions_per_100 | Fixed broadband | Float | Per 100 | 0.01 to 0.23 | Fixed connections |
| mobile_broadband_subscriptions_per_100 | Mobile broadband | Float | Per 100 | 11.2 to 95.2 | Mobile data users |
| digital_skills_index | Digital competency | Float | Index | 2.15 to 4.05 | Skills assessment |
| e_government_index | E-gov development | Float | Index | 0.2543 to 0.5502 | 0-1 scale |

---

## Measurement Units and Scales

### Currency Units
- **Nigerian Naira (₦)**: Primary currency for monetary values
- **US Dollar ($)**: Used for international trade values
- **Conversion**: Variable exchange rates (₦150-₦1500 per $1)

### Time Periods
- **Annual**: Yearly aggregates
- **Quarterly**: Q1 (Jan-Mar), Q2 (Apr-Jun), Q3 (Jul-Sep), Q4 (Oct-Dec)
- **Monthly**: Calendar months

### Index Scales
- **Innovation Index**: 1-5 scale (1=lowest, 5=highest)
- **ICT Development Index**: 0-10 scale
- **E-government Index**: 0-1 scale
- **Ease of Doing Business**: 0-100 (distance to frontier)

### Geographic Classifications
- **National**: Country-level aggregates
- **Regional**: Six geopolitical zones
  - North Central
  - North East
  - North West
  - South East
  - South South
  - South West
- **State-level**: 36 states + Federal Capital Territory

---

## Data Types and Formats

### File Formats
- **CSV**: Comma-separated values
- **Encoding**: UTF-8
- **Decimal Separator**: Period (.)
- **Thousand Separator**: None in raw data

### Missing Values
- **Representation**: Empty cells or "N/A"
- **Handling**: Forward fill for time series, interpolation where appropriate

### Data Quality Indicators
- **Complete**: Full time series coverage
- **Consistent**: Standardized units and formats
- **Validated**: Cross-checked for realistic ranges
- **Documented**: All variables explained

### Update Frequency
- **Real-time proxy**: Monthly updates for high-frequency data
- **Quarterly**: GDP and sectoral data
- **Annual**: Development indices and rankings

---

## Usage Notes

1. **Temporal Alignment**: When combining datasets, ensure proper time period matching
2. **Seasonal Adjustment**: Raw data not seasonally adjusted unless specified
3. **Growth Rates**: Calculated as year-on-year percentage changes
4. **Aggregation**: State-level data can be aggregated to regional or national levels
5. **Interpolation**: Acceptable for filling gaps in annual data
6. **Currency Conversion**: Use period-appropriate exchange rates
7. **Index Interpretation**: Higher values generally indicate better performance
8. **Percentage Points**: Changes in rates expressed in percentage points

---

## Contact for Clarifications
For questions about specific variables or methodologies, consult the README file or analysis scripts provided with the dataset.