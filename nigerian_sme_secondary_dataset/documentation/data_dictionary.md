# Data Dictionary: Nigerian SME Secondary Dataset

## Macroeconomic Data

### GDP Growth Rate (`gdp_growth_rate.csv`)
| Column Name | Data Type | Unit | Description | Source |
|-------------|-----------|------|-------------|---------|
| Year | Integer | - | Calendar year | World Bank |
| GDP_Growth_Rate_Percent | Float | Percentage | Annual GDP growth rate | World Bank |
| GDP_Nominal_Billion_USD | Float | Billion USD | Nominal GDP in current USD | World Bank |
| GDP_Per_Capita_USD | Float | USD | GDP per capita in current USD | World Bank |
| Population_Million | Float | Million | Total population | World Bank |
| Data_Source | String | - | Primary data source | - |
| Notes | String | - | Contextual information | - |

### Inflation Rate (`inflation_rate.csv`)
| Column Name | Data Type | Unit | Description | Source |
|-------------|-----------|------|-------------|---------|
| Year | Integer | - | Calendar year | NBS |
| Month | Integer | - | Month (1-12) | NBS |
| Inflation_Rate_Percent | Float | Percentage | Headline inflation rate | NBS |
| Food_Inflation_Percent | Float | Percentage | Food component inflation | NBS |
| Core_Inflation_Percent | Float | Percentage | Core inflation (excluding food/energy) | NBS |
| Urban_Inflation_Percent | Float | Percentage | Urban area inflation | NBS |
| Rural_Inflation_Percent | Float | Percentage | Rural area inflation | NBS |
| Data_Source | String | - | Primary data source | NBS |
| Methodology | String | - | Measurement methodology | NBS |

### Interest Rates (`interest_rates.csv`)
| Column Name | Data Type | Unit | Description | Source |
|-------------|-----------|------|-------------|---------|
| Year | Integer | - | Calendar year | CBN |
| Quarter | String | - | Quarter (Q1-Q4) | CBN |
| Monetary_Policy_Rate_Percent | Float | Percentage | CBN policy rate | CBN |
| Prime_Lending_Rate_Percent | Float | Percentage | Average prime lending rate | CBN |
| Deposit_Rate_Percent | Float | Percentage | Average deposit rate | CBN |
| Treasury_Bill_91Day_Percent | Float | Percentage | 91-day treasury bill yield | CBN |
| Bond_Yield_10Year_Percent | Float | Percentage | 10-year government bond yield | CBN |
| Interbank_Rate_Percent | Float | Percentage | Interbank lending rate | CBN |
| Data_Source | String | - | Primary data source | CBN |
| Policy_Context | String | - | Monetary policy context | CBN |

### Broadband Penetration by State (`broadband_penetration_by_state.csv`)
| Column Name | Data Type | Unit | Description | Source |
|-------------|-----------|------|-------------|---------|
| State | String | - | Nigerian state name | NCC |
| Region | String | - | Geopolitical region | NCC |
| 2018_Penetration_Percent | Float | Percentage | 2018 broadband penetration | NCC |
| 2019_Penetration_Percent | Float | Percentage | 2019 broadband penetration | NCC |
| 2020_Penetration_Percent | Float | Percentage | 2020 broadband penetration | NCC |
| 2021_Penetration_Percent | Float | Percentage | 2021 broadband penetration | NCC |
| 2022_Penetration_Percent | Float | Percentage | 2022 broadband penetration | NCC |
| 2023_Penetration_Percent | Float | Percentage | 2023 broadband penetration | NCC |
| 2024_Penetration_Percent | Float | Percentage | 2024 broadband penetration | NCC |
| Population_2023 | Integer | - | 2023 population estimate | NBS |
| Urban_Rural_Classification | String | - | Urban/Mixed/Rural classification | NBS |
| Major_Telecom_Providers | String | - | Primary service providers | NCC |
| Infrastructure_Score | Float | 1-10 scale | Infrastructure quality score | NCC |

### Ease of Doing Business (`ease_of_doing_business.csv`)
| Column Name | Data Type | Unit | Description | Source |
|-------------|-----------|------|-------------|---------|
| Year | Integer | - | Calendar year | World Bank |
| Overall_Rank | Integer | - | Global ranking | World Bank |
| Total_Countries | Integer | - | Total countries ranked | World Bank |
| Overall_Score | Float | 0-100 scale | Overall ease of doing business score | World Bank |
| Starting_Business_Rank | Integer | - | Starting a business ranking | World Bank |
| Starting_Business_Score | Float | 0-100 scale | Starting a business score | World Bank |
| [Additional sub-component columns follow same pattern] | | | | |

## Industry-Specific Data

### Sectoral Growth Rates (`sectoral_growth_rates.csv`)
| Column Name | Data Type | Unit | Description | Source |
|-------------|-----------|------|-------------|---------|
| Year | Integer | - | Calendar year | NBS |
| Quarter | String | - | Quarter (Q1-Q4) | NBS |
| Agriculture_Growth_Percent | Float | Percentage | Agriculture sector growth | NBS |
| Mining_Quarrying_Growth_Percent | Float | Percentage | Mining & quarrying growth | NBS |
| Manufacturing_Growth_Percent | Float | Percentage | Manufacturing sector growth | NBS |
| [Additional sector columns follow same pattern] | | | | |
| Data_Source | String | - | Primary data source | NBS |

### SME Landscape Reports (`sme_landscape_reports.csv`)
| Column Name | Data Type | Unit | Description | Source |
|-------------|-----------|------|-------------|---------|
| Year | Integer | - | Report year | Various |
| Report_Source | String | - | Report publisher | Various |
| Report_Title | String | - | Report title | Various |
| Total_SMEs_Million | Float | Million | Total SME count | Various |
| SME_GDP_Contribution_Percent | Float | Percentage | SME contribution to GDP | Various |
| SME_Employment_Percent | Float | Percentage | SME share of employment | Various |
| Micro_Enterprises_Percent | Float | Percentage | Share of micro enterprises | Various |
| Small_Enterprises_Percent | Float | Percentage | Share of small enterprises | Various |
| Medium_Enterprises_Percent | Float | Percentage | Share of medium enterprises | Various |
| [Additional sectoral and characteristic columns] | | | | |
| Innovation_Adoption_Rate_Percent | Float | Percentage | Innovation adoption rate | Various |
| Data_Quality_Score | Float | 1-10 scale | Data reliability score | - |

### SME Sector Breakdown (`sme_sector_breakdown.csv`)
| Column Name | Data Type | Unit | Description | Source |
|-------------|-----------|------|-------------|---------|
| Sector | String | - | Primary sector | Various |
| Sub_Sector | String | - | Sub-sector classification | Various |
| 2020_SMEs_Thousands | Float | Thousands | 2020 SME count | Various |
| 2021_SMEs_Thousands | Float | Thousands | 2021 SME count | Various |
| 2022_SMEs_Thousands | Float | Thousands | 2022 SME count | Various |
| 2023_SMEs_Thousands | Float | Thousands | 2023 SME count | Various |
| 2024_SMEs_Thousands | Float | Thousands | 2024 SME count | Various |
| Average_Employment_Per_SME | Float | - | Average employees per SME | Various |
| Revenue_Range_Million_NGN | String | - | Typical revenue range | Various |
| Innovation_Intensity_Score | Float | 1-10 scale | Innovation activity level | Various |
| Digital_Readiness_Score | Float | 1-10 scale | Digital transformation readiness | Various |
| Export_Potential_Score | Float | 1-10 scale | Export market potential | Various |
| Growth_Rate_2024_Percent | Float | Percentage | 2024 growth rate | Various |
| Key_Innovation_Areas | String | - | Primary innovation focus areas | Various |
| Major_Constraints | String | - | Key business constraints | Various |
| Technology_Adoption_Level | String | - | Technology adoption category | Various |

## Technology Adoption Indices

### Mobile Money/FinTech Adoption (`mobile_money_fintech_adoption.csv`)
| Column Name | Data Type | Unit | Description | Source |
|-------------|-----------|------|-------------|---------|
| Year | Integer | - | Calendar year | CBN/NCC |
| Quarter | String | - | Quarter (Q1-Q4) | CBN/NCC |
| Mobile_Money_Users_Million | Float | Million | Active mobile money users | CBN |
| Mobile_Money_Penetration_Percent | Float | Percentage | Mobile money penetration rate | CBN |
| Mobile_Money_Transaction_Volume_Billion_NGN | Float | Billion NGN | Transaction volume | CBN |
| Mobile_Money_Transaction_Count_Million | Float | Million | Number of transactions | CBN |
| Digital_Banking_Users_Million | Float | Million | Digital banking users | CBN |
| Digital_Banking_Penetration_Percent | Float | Percentage | Digital banking penetration | CBN |
| FinTech_Adoption_Index | Float | 0-100 scale | Composite FinTech adoption index | CBN |
| [Additional payment infrastructure columns] | | | | |
| Cryptocurrency_Adoption_Percent | Float | Percentage | Cryptocurrency adoption rate | CBN |
| Regional_Variation_Index | Float | 1-10 scale | Regional variation measure | CBN |

### ICT Development Index (`ict_development_index.csv`)
| Column Name | Data Type | Unit | Description | Source |
|-------------|-----------|------|-------------|---------|
| Year | Integer | - | Calendar year | ITU |
| ITU_ICT_Development_Index_Score | Float | 0-10 scale | Overall ICT development score | ITU |
| ITU_ICT_Development_Index_Rank | Integer | - | Global ranking | ITU |
| Total_Countries | Integer | - | Total countries ranked | ITU |
| ICT_Access_Sub_Index | Float | 0-10 scale | ICT access sub-index | ITU |
| ICT_Use_Sub_Index | Float | 0-10 scale | ICT use sub-index | ITU |
| ICT_Skills_Sub_Index | Float | 0-10 scale | ICT skills sub-index | ITU |
| [Additional telecommunications and education indicators] | | | | |
| Methodology_Version | String | - | ITU methodology version | ITU |

### Digital Transformation Metrics (`digital_transformation_metrics.csv`)
| Column Name | Data Type | Unit | Description | Source |
|-------------|-----------|------|-------------|---------|
| Year | Integer | - | Calendar year | UN/WEF/ITU |
| Quarter | String | - | Quarter (Q1-Q4) | UN/WEF/ITU |
| E_Government_Development_Index | Float | 0-1 scale | E-government development level | UN |
| Digital_Competitiveness_Ranking | Integer | - | Global digital competitiveness rank | WEF |
| Cybersecurity_Index_Score | Float | 0-1 scale | National cybersecurity index | ITU |
| AI_Readiness_Index | Float | 1-10 scale | Artificial intelligence readiness | WEF |
| Blockchain_Adoption_Score | Float | 1-10 scale | Blockchain technology adoption | WEF |
| Cloud_Computing_Adoption_Percent | Float | Percentage | Cloud computing adoption rate | Various |
| IoT_Device_Penetration_Per_1000 | Float | Per 1000 people | IoT device penetration | Various |
| [Additional digital transformation indicators] | | | | |
| Composite_Digital_Index | Float | 1-10 scale | Composite digital transformation index | - |

## Data Quality Indicators

### Quality Scores (1-10 Scale)
- **10**: Official government statistics, internationally verified
- **8-9**: Reputable international organizations (World Bank, UN, ITU)
- **6-7**: Established consulting firms and industry reports
- **4-5**: Academic studies and specialized surveys
- **1-3**: Estimated or modeled data with limited verification

### Missing Data Codes
- **Empty cell**: Data not available for that period
- **NA**: Not applicable for that category
- **NR**: Not reported by source
- **Est**: Estimated value based on trends or models

### Update Frequencies
- **Real-time**: Mobile money, payment system data
- **Monthly**: Inflation, some financial indicators
- **Quarterly**: GDP, sectoral growth, interest rates
- **Annual**: Doing business, ICT development, most SME surveys
- **Irregular**: Special reports and studies

## Relationships Between Datasets

### Temporal Alignment
- All datasets cover overlapping periods (2018-2024 minimum)
- Quarterly data can be aggregated to annual for cross-dataset analysis
- Some indicators have monthly granularity for detailed time series analysis

### Geographic Consistency
- National-level indicators are consistent across all datasets
- State-level data available for broadband penetration
- Regional aggregations follow standard Nigerian geopolitical zones

### Sectoral Mappings
- SME sector classifications align with NBS economic sector definitions
- Technology adoption data can be mapped to specific SME sectors
- Innovation indicators correspond to sectoral innovation intensity scores

---
*Data Dictionary Version: 1.0*
*Last Updated: October 2024*
*Total Variables: 247 across all datasets*