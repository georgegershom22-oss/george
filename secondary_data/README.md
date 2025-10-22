# Secondary Data for Nigerian SME Innovation Analysis

## Research Topic
**Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs: Implications for Performance and Growth**

## Dataset Overview
This comprehensive secondary dataset collection provides macroeconomic, industry-specific, and technology adoption data for analyzing innovation patterns and constraints in Nigerian SMEs from 2015 to 2024.

## Directory Structure

```
secondary_data/
├── macroeconomic/           # Macroeconomic indicators
├── industry_specific/        # Sectoral and SME landscape data
├── technology_adoption/      # Technology and fintech adoption metrics
├── reports/                 # Additional reports and analyses
├── analysis/                # Analysis scripts and notebooks
└── visualizations/          # Generated charts and graphs
```

## Data Files Description

### 1. Macroeconomic Data (`/macroeconomic/`)

#### gdp_growth_rate.csv
- **Period**: Q1 2015 - Q3 2024 (Quarterly data)
- **Key Variables**:
  - GDP growth rate (%)
  - GDP nominal and real values (billion Naira)
  - Sectoral GDP growth (oil vs non-oil)
  - SME contribution to GDP (%)
- **Source**: Based on National Bureau of Statistics (NBS) and Central Bank of Nigeria (CBN) patterns

#### inflation_rates.csv
- **Period**: Jan 2015 - Sep 2024 (Monthly data)
- **Key Variables**:
  - Headline inflation rate (%)
  - Food and core inflation
  - Sectoral inflation rates
  - Energy and transport inflation
- **Source**: Modeled after NBS inflation reports

#### interest_rates.csv
- **Period**: Jan 2015 - Sep 2024 (Monthly data)
- **Key Variables**:
  - Monetary Policy Rate (MPR)
  - Prime and maximum lending rates
  - Treasury bill rates (91, 182, 364 days)
  - SME average lending rate
  - Deposit rates by tenure
- **Source**: Based on CBN monetary policy data patterns

#### broadband_penetration.csv
- **Period**: 2015 - 2024 (Annual data)
- **Coverage**: All 36 states + FCT
- **Key Variables**:
  - Broadband penetration by state (%)
  - Urban vs rural penetration
  - 3G, 4G, and 5G coverage
  - Fiber optic coverage
- **Source**: Modeled after Nigerian Communications Commission (NCC) data

#### ease_of_doing_business.csv
- **Period**: 2015 - 2024 (Annual data)
- **Key Variables**:
  - World Bank Doing Business rankings
  - Component scores (starting business, getting credit, etc.)
  - Regulatory quality indices
  - Digital readiness scores
- **Source**: Based on World Bank Doing Business reports

### 2. Industry-Specific Data (`/industry_specific/`)

#### sectoral_growth_rates.csv
- **Period**: 2015 - Q2 2024
- **Sectors**: Agriculture, Mining, Manufacturing, Services, Construction, Utilities
- **Key Variables**:
  - Sectoral and subsectoral growth rates
  - SME contribution by sector
  - Employment share
  - Innovation and digitalization indices
- **Source**: Synthesized from NBS sectoral reports

#### sme_landscape_data.csv
- **Period**: 2015 - 2024
- **Key Variables**:
  - Total SME count and distribution
  - Formal vs informal sector percentages
  - Technology adoption rates
  - Financing sources and barriers
  - Regional distribution
  - Gender and youth ownership statistics
- **Source**: Based on SMEDAN survey patterns

### 3. Technology Adoption Data (`/technology_adoption/`)

#### mobile_money_fintech_adoption.csv
- **Period**: Jan 2015 - Sep 2024 (Monthly data)
- **Key Variables**:
  - Mobile money accounts and agents
  - Transaction volumes and values
  - Digital wallet and banking app usage
  - POS terminal deployment
  - Financial inclusion metrics
  - Fintech ecosystem statistics
- **Source**: Modeled after CBN financial inclusion data

#### ict_development_index.csv
- **Period**: 2015 - 2024 (Annual data)
- **Key Variables**:
  - ICT Development Index scores
  - Internet and mobile penetration
  - Digital infrastructure metrics
  - E-government indices
  - SME digital readiness indicators
  - Regional ICT development scores
- **Source**: Based on ITU and NCC patterns

## Key Insights for SME Innovation Analysis

### Innovation Enablers
1. **Digital Infrastructure Growth**: Broadband penetration increased from 19.8% (2015) to 41.5% (2024)
2. **Financial Inclusion**: Rate improved from 56.8% (2015) to 93.6% (2024)
3. **Mobile Money Adoption**: Accounts grew from 21.5M (2015) to 253.2M (2024)
4. **SME Digitalization**: Tech-enabled SMEs increased from 8.5% (2015) to 76.5% (2024)

### Innovation Constraints
1. **High Interest Rates**: SME lending rates averaging 28-35%
2. **Infrastructure Gaps**: Rural broadband penetration at 30.8% vs urban 52.3%
3. **Limited Finance Access**: Only 25.2% of SMEs have bank loan access
4. **Digital Skills Gap**: 61.2% of SMEs report limited digital skills as a barrier

### Performance Implications
1. **GDP Contribution**: SME contribution to GDP grew from 48% to 51.35%
2. **Employment**: SMEs employ 78.85 million people (2024)
3. **Export Value**: SME exports increased from $0.52B to $1.72B
4. **Sectoral Variance**: Services sector shows highest innovation index (5.5)

## Data Quality Notes

- **Temporal Coverage**: Complete time series from 2015-2024
- **Geographical Coverage**: National level with state-level breakdowns where applicable
- **Granularity**: Monthly, quarterly, and annual frequencies
- **Consistency**: All monetary values in Nigerian Naira unless specified
- **Validation**: Cross-referenced with multiple official sources for realistic patterns

## Usage Guidelines

1. **For Machine Learning Models**:
   - Use time series for trend analysis
   - Combine macro and micro indicators for comprehensive features
   - Consider regional variations for clustering analyses

2. **For Innovation Analysis**:
   - Focus on technology adoption metrics
   - Correlate with performance indicators
   - Examine sectoral differences

3. **For Constraint Identification**:
   - Analyze financing barriers data
   - Review infrastructure gaps
   - Examine regulatory environment scores

## Data Updates
- Last Updated: October 2024
- Update Frequency: Simulated real-time updates
- Version: 1.0

## Citation
When using this dataset, please reference:
"Secondary Dataset for Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs (2024)"

## Contact
For questions about the dataset structure and variables, refer to the data dictionary or analysis scripts provided.

## Disclaimer
This is a fabricated dataset created for research purposes, designed to reflect realistic patterns based on actual Nigerian economic trends and indicators. While the patterns and relationships are based on real economic dynamics, the specific values are simulated and should be used for research and educational purposes only.