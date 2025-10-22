# Secondary Dataset for Nigerian SME Innovation Research
## Data Dictionary and Documentation

### Research Topic
**Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs: Implications for Performance and Growth**

### Dataset Overview
This comprehensive secondary dataset covers macroeconomic indicators, technology adoption metrics, sectoral performance, regional variations, and innovation barriers for Nigerian SMEs from 2015-2024. The data synthesizes patterns from World Bank, Central Bank of Nigeria (CBN), National Bureau of Statistics (NBS), SMEDAN, and other authoritative sources.

---

## File Descriptions

### 1. macroeconomic_indicators.csv
**Purpose**: National-level macroeconomic context for SME operations  
**Time Period**: 2015-2024 (Annual)  
**Source Models**: World Bank, CBN, NBS, Ease of Doing Business Reports

| Variable | Description | Unit | Source |
|----------|-------------|------|--------|
| Year | Calendar year | Year | - |
| GDP_Growth_Rate_Percent | Annual GDP growth rate | Percentage | World Bank/NBS |
| Inflation_Rate_Percent | Consumer price inflation (year-on-year) | Percentage | NBS |
| Lending_Interest_Rate_Percent | Average commercial bank lending rate | Percentage | CBN |
| Ease_of_Doing_Business_Score | World Bank EODB score (0-100, higher is better) | Score | World Bank |
| Ease_of_Doing_Business_Rank | Global ranking for ease of doing business | Rank | World Bank |
| Real_GDP_Billion_USD | Gross Domestic Product in constant USD | Billion USD | World Bank |
| GDP_Per_Capita_USD | GDP divided by population | USD | World Bank |
| Unemployment_Rate_Percent | National unemployment rate | Percentage | NBS |
| Exchange_Rate_NGN_USD | Naira to US Dollar exchange rate (average) | NGN per USD | CBN |
| Foreign_Direct_Investment_Million_USD | Net FDI inflows | Million USD | World Bank |

**Key Insights**:
- Captures recession period (2016) and recovery trajectory
- Shows exchange rate depreciation impacts on SME costs
- High lending rates indicate credit accessibility challenges

---

### 2. broadband_penetration_by_state.csv
**Purpose**: State-level digital infrastructure and connectivity  
**Time Period**: 2015-2024 (Annual)  
**Coverage**: 10 major states across 6 geopolitical regions  
**Source Models**: NCC, NBS, ITU

| Variable | Description | Unit | Source |
|----------|-------------|------|--------|
| State | Nigerian state name | Text | - |
| Region | Geopolitical zone | Text | - |
| Year | Calendar year | Year | - |
| Broadband_Penetration_Percent | Percentage of population with broadband access | Percentage | NCC |
| Mobile_Penetration_Percent | Mobile phone subscriptions per 100 inhabitants | Percentage | NCC |
| Internet_Users_Percent | Population using internet | Percentage | ITU |
| Population_Million | State population estimate | Million | NBS |
| Urban_Rural_Ratio | Urban population / rural population | Ratio | NBS |
| Electricity_Access_Percent | Households with electricity access | Percentage | NERC/NBS |

**Key Insights**:
- Lagos and Abuja show highest digital infrastructure
- North East and North West lag significantly (digital divide)
- Strong correlation between urbanization and connectivity
- Electricity access constraint affects ICT adoption

**Regional Classifications**:
- **South West**: Lagos, Oyo (Commercial hubs)
- **South East**: Enugu, Anambra (Trading centers)
- **South South**: Rivers (Oil-producing region)
- **North Central**: Abuja (Federal capital)
- **North West**: Kano, Kaduna (Agricultural/industrial)
- **North East**: Borno, Bauchi (Security-challenged areas)

---

### 3. sectoral_growth_rates.csv
**Purpose**: Economic performance by industry sector  
**Time Period**: 2015-2024 (Annual)  
**Source Models**: NBS Sectoral Reports

| Variable | Description | Unit | Source |
|----------|-------------|------|--------|
| Year | Calendar year | Year | - |
| [Sector]_Growth_Percent | Annual growth rate for each sector | Percentage | NBS |
| [Sector]_GDP_Contribution_Percent | Sector's share of total GDP | Percentage | NBS |

**Sectors Covered**:
1. **Agriculture**: Largest employer, declining GDP share
2. **Manufacturing**: Struggled during recession, recovering slowly
3. **Trade**: Retail and wholesale distribution
4. **ICT**: Fastest-growing sector (10-16% annually)
5. **Financial Services**: Banking and insurance
6. **Real Estate**: Property development and management
7. **Construction**: Infrastructure and building
8. **Professional Services**: Consulting, legal, accounting
9. **Transportation**: Logistics and passenger services
10. **Education**: Private education providers
11. **Healthcare**: Private healthcare services
12. **Hospitality**: Hotels, restaurants, tourism
13. **Energy**: Power generation and distribution
14. **Mining**: Oil and gas extraction
15. **Oil & Gas**: Petroleum sector GDP contribution

**Key Insights**:
- ICT sector shows consistent double-digit growth (innovation driver)
- Manufacturing vulnerability during economic downturns
- Service sectors (professional, healthcare, education) show resilience
- Declining oil/gas GDP contribution (diversification trend)

---

### 4. technology_adoption_indices.csv
**Purpose**: FinTech, mobile money, and digital payment ecosystem  
**Time Period**: 2015-2024 (Annual)  
**Source Models**: CBN, ITU, EFInA, GSMA

| Variable | Description | Unit | Source |
|----------|-------------|------|--------|
| Year | Calendar year | Year | - |
| ICT_Development_Index | ITU composite index (0-10) | Index | ITU |
| Mobile_Money_Users_Million | Active mobile money users | Million | GSMA/CBN |
| Mobile_Money_Transaction_Value_Billion_NGN | Total transaction value | Billion NGN | CBN |
| Mobile_Money_Accounts_Million | Registered mobile money accounts | Million | CBN |
| FinTech_Adoption_Rate_Percent | Population using FinTech services | Percentage | EFInA/CBN |
| Digital_Payment_Volume_Million_Transactions | Total digital payment transactions | Million | CBN |
| E_Commerce_GMV_Billion_NGN | Gross merchandise value of e-commerce | Billion NGN | Statista/Industry |
| Bank_Account_Penetration_Percent | Adults with bank accounts | Percentage | EFInA |
| Mobile_Banking_Users_Million | Active mobile banking users | Million | CBN |
| POS_Terminals_Thousands | Point-of-sale terminals deployed | Thousands | NIBSS |
| ATM_Per_100K_Adults | ATM density per 100,000 adults | Number | CBN |
| Internet_Banking_Users_Million | Active internet banking users | Million | CBN |
| USSD_Banking_Users_Million | Users of USSD banking (*901#, etc.) | Million | CBN |
| Mobile_App_Downloads_Financial_Million | Financial app downloads | Million | App Annie/Industry |
| Blockchain_Crypto_Users_Thousands | Cryptocurrency/blockchain users | Thousands | Industry Estimates |

**Key Insights**:
- Explosive FinTech growth (12% to 78% adoption in 10 years)
- Mobile money critical for financial inclusion
- USSD banking bridges smartphone gap
- Emerging blockchain/crypto adoption among youth

---

### 5. sme_landscape_indicators.csv
**Purpose**: SME sector structure and performance metrics  
**Time Period**: 2015-2024 (Annual)  
**Source Models**: SMEDAN, NBS, PwC Nigeria, McKinsey

| Variable | Description | Unit | Source |
|----------|-------------|------|--------|
| Year | Calendar year | Year | - |
| Total_SMEs_Million | Number of registered and informal SMEs | Million | SMEDAN/NBS |
| SME_GDP_Contribution_Percent | SME contribution to GDP | Percentage | NBS |
| SME_Employment_Million | Jobs provided by SMEs | Million | NBS |
| Formal_SMEs_Percent | Percentage formally registered | Percentage | SMEDAN |
| Informal_SMEs_Percent | Percentage operating informally | Percentage | SMEDAN |
| SME_Survival_Rate_5Years_Percent | SMEs surviving 5+ years | Percentage | SMEDAN |
| New_SME_Registrations_Thousands | Annual new business registrations | Thousands | CAC |
| SME_Closure_Rate_Percent | Annual business closure rate | Percentage | SMEDAN |
| Access_to_Finance_Percent | SMEs with formal credit access | Percentage | World Bank/SMEDAN |
| SME_Export_Value_Billion_NGN | Export value from SMEs | Billion NGN | NBS |
| Women_Owned_SMEs_Percent | Female-owned businesses | Percentage | SMEDAN |
| Youth_Owned_SMEs_Percent | Owner aged 18-35 years | Percentage | SMEDAN |
| Tech_Enabled_SMEs_Percent | SMEs using digital tools/platforms | Percentage | PwC/McKinsey |
| SME_Innovation_Rate_Percent | SMEs introducing new products/processes | Percentage | SMEDAN |
| Average_SME_Size_Employees | Mean number of employees | Number | NBS |
| SME_Digitalization_Index | Digital adoption composite score (0-10) | Index | Industry Analysis |
| SME_Training_Access_Percent | SMEs accessing training programs | Percentage | SMEDAN |
| SME_Loan_Default_Rate_Percent | Default rate on SME loans | Percentage | CBN |
| SME_Credit_to_GDP_Percent | SME credit as percentage of GDP | Percentage | CBN |
| Microfinance_Penetration_Percent | SMEs accessing microfinance | Percentage | CBN |

**Key Insights**:
- 76-84% informality rate (major constraint)
- Rising tech-enabled SMEs (8.7% to 49.7%)
- Low access to finance (5-9% with formal credit)
- Increasing women and youth entrepreneurship
- High loan default rates reflect business vulnerability

---

### 6. innovation_adoption_barriers.csv
**Purpose**: Regional variation in innovation constraints  
**Time Period**: 2015-2024 (Annual)  
**Coverage**: 6 geopolitical regions  
**Source Models**: SMEDAN, World Bank Enterprise Surveys, NBS

| Variable | Description | Unit | Source |
|----------|-------------|------|--------|
| Year | Calendar year | Year | - |
| Region | Geopolitical zone | Text | - |
| High_Cost_Barrier_Percent | SMEs citing high cost as barrier | Percentage | Enterprise Survey |
| Lack_Technical_Skills_Percent | Insufficient technical capacity | Percentage | Enterprise Survey |
| Poor_Infrastructure_Percent | Infrastructure inadequacy | Percentage | Enterprise Survey |
| Limited_Awareness_Percent | Low awareness of innovations | Percentage | Enterprise Survey |
| Regulatory_Constraints_Percent | Regulatory barriers | Percentage | Enterprise Survey |
| Cultural_Resistance_Percent | Cultural/social resistance | Percentage | Enterprise Survey |
| Lack_Finance_Access_Percent | Credit access constraints | Percentage | Enterprise Survey |
| Cybersecurity_Concerns_Percent | Security/privacy fears | Percentage | Enterprise Survey |
| Unreliable_Power_Supply_Percent | Electricity supply issues | Percentage | Enterprise Survey |
| Poor_Internet_Connectivity_Percent | Internet access problems | Percentage | Enterprise Survey |
| Lack_Government_Support_Percent | Insufficient policy support | Percentage | Enterprise Survey |
| High_Tax_Burden_Percent | Tax burden concerns | Percentage | Enterprise Survey |
| Limited_Market_Access_Percent | Market penetration challenges | Percentage | Enterprise Survey |
| Competition_MNCs_Percent | Competition from large firms | Percentage | Enterprise Survey |
| Corruption_Bureaucracy_Percent | Corruption and red tape | Percentage | Enterprise Survey |

**Key Insights**:
- **Highest barriers**: Lack of finance (62-90%), corruption (55-85%), cost (52-82%)
- **Regional disparities**: North East/West face 1.5-2x higher barriers than South West
- **Improving trends**: All barriers declining 15-30% over decade
- **Power supply**: Critical constraint (48-83% across regions)
- **Skills gap**: 56-86% report technical skills shortage

**Regional Rankings (Best to Worst)**:
1. South West (Lagos, Oyo)
2. South South (Rivers)
3. South East (Enugu, Anambra)
4. North Central (Abuja)
5. North West (Kano, Kaduna)
6. North East (Borno, Bauchi)

---

### 7. regional_summary_statistics.csv
**Purpose**: Comprehensive regional ecosystem indicators  
**Time Period**: 2015-2024 (Annual)  
**Coverage**: 6 geopolitical regions  
**Source Models**: Multiple (NBS, SMEDAN, CBN, Academia)

| Variable | Description | Unit | Source |
|----------|-------------|------|--------|
| Year | Calendar year | Year | - |
| Region | Geopolitical zone | Text | - |
| Total_SMEs_Thousands | Number of SMEs in region | Thousands | SMEDAN |
| SME_Density_Per_1000_Population | SMEs per 1,000 residents | Number | Calculated |
| Average_SME_Revenue_Million_NGN | Mean annual SME revenue | Million NGN | NBS |
| SME_Formal_Registration_Percent | Formally registered SMEs | Percentage | SMEDAN |
| Bank_Branch_Density_Per_100K | Bank branches per 100,000 population | Number | CBN |
| Venture_Capital_Investment_Million_NGN | VC/PE investment in region | Million NGN | AVCA/Industry |
| Business_Incubators_Count | Number of business incubators | Count | Nigeria Hub Map |
| Innovation_Hubs_Count | Number of innovation/tech hubs | Count | Nigeria Hub Map |
| University_Industry_Collaboration_Index | Academia-industry linkage strength (0-10) | Index | Research Analysis |
| R_D_Expenditure_Percent_GDP | Regional R&D spending as % of GDP | Percentage | NBS/UNESCO |
| Patent_Applications_Count | Annual patent applications | Count | IP Office |
| Trademark_Registrations_Count | Annual trademark registrations | Count | IP Office |
| Startup_Ecosystem_Rank | Regional startup ecosystem ranking (1-6) | Rank | Industry Analysis |
| Digital_Infrastructure_Score | Digital infrastructure quality (0-15) | Score | Composite Index |
| Business_Support_Services_Score | Business services availability (0-10) | Score | Composite Index |

**Key Insights**:
- **South West dominance**: 34% of SMEs, highest revenue, #1 ecosystem
- **Innovation concentration**: 60-70% of hubs, incubators in Lagos/Abuja
- **VC investment**: 70-80% flows to South West
- **North-South divide**: 2-3x gap in most metrics
- **Patent activity**: Concentrated in universities in South West/South East

---

### 8. policy_and_external_factors.csv
**Purpose**: Government interventions and institutional environment  
**Time Period**: 2015-2024 (Annual)  
**Source Models**: Federal Budget, CBN, SMEDAN, Transparency International

| Variable | Description | Unit | Source |
|----------|-------------|------|--------|
| Year | Calendar year | Year | - |
| Government_SME_Budget_Billion_NGN | Government SME development budget | Billion NGN | Federal Budget |
| Tax_Incentives_For_SMEs_Billion_NGN | Value of tax relief for SMEs | Billion NGN | FIRS |
| SME_Credit_Guarantee_Scheme_Billion_NGN | Credit guarantee fund value | Billion NGN | CBN |
| SMEDAN_Beneficiaries_Thousands | SMEs receiving SMEDAN support | Thousands | SMEDAN |
| BOI_SME_Loans_Billion_NGN | Bank of Industry lending to SMEs | Billion NGN | BOI |
| CBN_Intervention_Funds_Billion_NGN | CBN intervention schemes | Billion NGN | CBN |
| Entrepreneurship_Training_Programs_Count | Training programs conducted | Count | SMEDAN |
| Digital_Literacy_Programs_Count | Digital skills training programs | Count | NITDA |
| Trade_Facilitation_Index | Ease of cross-border trade (0-10) | Index | World Bank |
| Regulatory_Burden_Index | Compliance cost burden (0-10, higher=worse) | Index | World Bank |
| Political_Stability_Index | Political stability score (0-10) | Index | World Bank |
| Security_Risk_Index | Security environment risk (0-10, higher=worse) | Index | Global Risk |
| Corruption_Perception_Index | Transparency International CPI | Score (0-100) | Transparency Intl |
| Regional_Integration_Score | ECOWAS integration progress (0-10) | Score | AfDB |
| Export_Promotion_Score | Export support effectiveness (0-10) | Score | NEPC |
| Infrastructure_Quality_Index | Overall infrastructure quality (0-10) | Index | World Bank |
| Power_Sector_Reform_Index | Electricity sector reform progress (0-10) | Index | NERC |
| Telecoms_Competition_Index | Telecom market competitiveness (0-10) | Index | NCC |
| Financial_Inclusion_Target_Achievement_Percent | Progress toward 95% target | Percentage | CBN |
| MSME_Policy_Implementation_Score | Policy implementation effectiveness (0-10) | Score | SMEDAN |

**Key Insights**:
- **Rising interventions**: Government budget increased 3.7x (2015-2024)
- **CBN leadership**: Largest intervention provider (NGN 234B to 901B)
- **Implementation gap**: Policy scores (4.6-7.1) lag ambitions
- **Governance challenges**: Corruption (CPI 24-28), security (7.0-7.5 risk)
- **Financial inclusion progress**: 42% to 77% toward 95% target

---

## Data Quality and Limitations

### Strengths
1. **Temporal depth**: 10-year panel enables trend analysis and forecasting
2. **Multi-dimensional**: Captures economic, technological, institutional, regional factors
3. **ML-ready**: Structured format suitable for regression, classification, clustering
4. **Policy-relevant**: Includes intervention variables for impact evaluation

### Limitations
1. **Synthetic data**: Based on realistic patterns but not actual historical data
2. **Aggregation**: State-level data may mask intra-state variations
3. **Informal sector**: Under-captured due to measurement challenges
4. **Missing variables**: Some micro-level SME characteristics not included
5. **Causality**: Correlational data; requires careful modeling for causal inference

### Data Generation Methodology
- **Macroeconomic trends**: Modeled on World Bank/IMF historical patterns for Nigeria
- **Sectoral growth**: Based on NBS sectoral reports and growth trajectories
- **Regional disparities**: Incorporates known North-South development gaps
- **Technology adoption**: Reflects Nigeria's FinTech boom and mobile penetration surge
- **Barriers**: Based on World Bank Enterprise Survey response distributions

---

## Recommended Machine Learning Applications

### 1. Classification Tasks
- **Innovation adopter profiling**: Classify SMEs into early/late adopters based on regional, sectoral, size characteristics
- **Survival prediction**: Predict 5-year survival probability using macroeconomic, access to finance, infrastructure variables
- **Credit risk modeling**: Classify default risk categories for lending decisions

### 2. Regression Tasks
- **Performance prediction**: Predict SME revenue/growth using innovation barriers, technology adoption, policy support
- **Constraint impact analysis**: Quantify impact of each barrier on SME performance metrics
- **Digital infrastructure ROI**: Estimate broadband penetration impact on sectoral growth

### 3. Clustering Tasks
- **Regional segmentation**: Cluster states by ecosystem maturity, infrastructure, barrier profiles
- **SME typology**: Identify distinct SME archetypes based on formality, tech use, sector, size
- **Policy effectiveness**: Group policy interventions by impact profiles

### 4. Time Series Forecasting
- **Technology diffusion**: Forecast FinTech adoption curves by region
- **Macroeconomic scenarios**: Predict SME outcomes under different GDP/inflation scenarios
- **Infrastructure planning**: Forecast broadband penetration targets

### 5. Causal Inference
- **Policy impact evaluation**: Estimate causal effect of CBN interventions on access to finance
- **Infrastructure treatment effects**: Use regional variations for difference-in-differences analysis
- **Innovation constraints**: Identify binding constraints using constraint relaxation experiments

---

## Variable Relationships and Key Hypotheses

### Hypothesized Relationships
1. **Digital infrastructure → Innovation adoption** (positive, strong)
2. **Access to finance → SME survival rate** (positive, moderate)
3. **Corruption/bureaucracy → Innovation barriers** (positive, strong)
4. **ICT sector growth → FinTech adoption** (positive, strong)
5. **Government interventions → SME formalization** (positive, moderate)
6. **Regional ecosystem maturity → Average SME revenue** (positive, strong)
7. **Electricity access → Technology adoption** (positive, strong)
8. **Lending rates → SME credit access** (negative, moderate)

### Control Variables
- **Region**: Controls for geographic/cultural factors
- **Year**: Controls for time trends and macro shocks
- **Sector**: Controls for industry-specific dynamics
- **Urban-rural ratio**: Controls for urbanization effects

---

## Citation and Usage

### Suggested Citation
```
Nigerian SME Innovation Secondary Dataset (2015-2024). Synthetic dataset 
for research on "Leveraging Machine Learning to Examine Innovation Adoption 
and Constraints in Nigerian SMEs: Implications for Performance and Growth." 
Generated October 2025.
```

### Ethical Considerations
- Data is **synthetic** and should not be misrepresented as actual records
- Use for **exploratory analysis, methodology testing, and hypothesis generation**
- Validate findings with actual primary data collection
- Acknowledge data limitations in research outputs

### Data Update Schedule
- This is a **static synthetic dataset** (2015-2024)
- For live data, refer to:
  - **NBS**: https://nigerianstat.gov.ng
  - **CBN**: https://www.cbn.gov.ng
  - **SMEDAN**: https://smedan.gov.ng
  - **World Bank**: https://data.worldbank.org

---

## Technical Specifications

### File Format
- **Format**: CSV (Comma-separated values)
- **Encoding**: UTF-8
- **Missing values**: No missing values in this synthetic dataset
- **Decimal separator**: Period (.)
- **Date format**: YYYY (year only)

### Data Types
- **Year**: Integer
- **Region/State**: String (categorical)
- **Percentages**: Float (0-100 scale)
- **Indices/Scores**: Float (various scales noted in descriptions)
- **Counts**: Integer
- **Currency**: Float (NGN/USD as specified)

### Recommended Software
- **Python**: pandas, scikit-learn, statsmodels, matplotlib
- **R**: tidyverse, caret, randomForest, ggplot2
- **Stata**: Suitable for panel data econometrics
- **SPSS**: For exploratory analysis and visualization
- **Tableau/Power BI**: For interactive dashboards

---

## Contact and Support

For questions about this dataset or suggestions for improvements:
- **Purpose**: Academic research on Nigerian SME innovation
- **Methodology**: Synthetic data generation based on literature review
- **Last Updated**: October 22, 2025
- **Version**: 1.0

---

## Appendix: Acronyms and Abbreviations

| Acronym | Full Name |
|---------|-----------|
| AfDB | African Development Bank |
| ATM | Automated Teller Machine |
| AVCA | African Private Equity and Venture Capital Association |
| BOI | Bank of Industry |
| CAC | Corporate Affairs Commission |
| CBN | Central Bank of Nigeria |
| CPI | Corruption Perception Index |
| ECOWAS | Economic Community of West African States |
| EFInA | Enhancing Financial Innovation and Access |
| EODB | Ease of Doing Business |
| FDI | Foreign Direct Investment |
| FIRS | Federal Inland Revenue Service |
| GDP | Gross Domestic Product |
| GMV | Gross Merchandise Value |
| GSMA | Global System for Mobile Communications Association |
| ICT | Information and Communication Technology |
| IP | Intellectual Property |
| ITU | International Telecommunication Union |
| MNC | Multinational Corporation |
| MSME | Micro, Small, and Medium Enterprise |
| NBS | National Bureau of Statistics |
| NCC | Nigerian Communications Commission |
| NEPC | Nigerian Export Promotion Council |
| NERC | Nigerian Electricity Regulatory Commission |
| NGN | Nigerian Naira |
| NIBSS | Nigeria Inter-Bank Settlement System |
| NITDA | National Information Technology Development Agency |
| POS | Point of Sale |
| PwC | PricewaterhouseCoopers |
| R&D | Research and Development |
| SME | Small and Medium Enterprise |
| SMEDAN | Small and Medium Enterprises Development Agency of Nigeria |
| USD | United States Dollar |
| USSD | Unstructured Supplementary Service Data |
| VC | Venture Capital |
| PE | Private Equity |

---

**END OF DATA DICTIONARY**
