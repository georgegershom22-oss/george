# Nigerian SME Secondary Dataset: Core Dataset 3

## Overview
This comprehensive secondary dataset supports research on "Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs: Implications for Performance and Growth." The dataset provides macro-contextual data and validation metrics for understanding the broader economic, technological, and institutional environment in which Nigerian SMEs operate.

## Research Context
The dataset is designed to provide macro-level context for analyzing:
- Innovation adoption patterns among Nigerian SMEs
- Structural constraints affecting SME performance
- Technology diffusion and digital transformation trends
- Economic and institutional factors influencing SME growth
- Regional variations in business environment quality

## Dataset Structure

### 1. Macroeconomic Data
**Purpose**: Provides economic context for SME performance analysis
**Time Coverage**: 2010-2024
**Geographic Coverage**: National level with some state-level breakdowns

#### Components:
- **GDP Growth Rate** (`gdp_growth_rate.csv`)
  - Annual GDP growth rates, nominal GDP, per capita GDP
  - Population data for contextual analysis
  - Source: World Bank, NBS

- **Inflation Rate** (`inflation_rate.csv`)
  - Consumer Price Index data (headline, food, core inflation)
  - Urban vs rural inflation differentials
  - Monthly granularity for recent years
  - Source: National Bureau of Statistics (NBS)

- **Interest Rates** (`interest_rates.csv`)
  - Monetary policy rates, lending rates, deposit rates
  - Treasury bill and bond yields
  - Quarterly data with policy context
  - Source: Central Bank of Nigeria (CBN)

- **Broadband Penetration by State** (`broadband_penetration_by_state.csv`)
  - State-level broadband penetration rates (2018-2024)
  - Infrastructure quality scores
  - Urban/rural classifications
  - Major telecom provider coverage
  - Source: Nigerian Communications Commission (NCC)

- **Ease of Doing Business** (`ease_of_doing_business.csv`)
  - World Bank Doing Business indicators (2010-2020)
  - Sub-component scores for different business processes
  - Nigeria's global ranking and score evolution
  - Source: World Bank

### 2. Industry-Specific Data
**Purpose**: Sectoral context for SME performance analysis
**Time Coverage**: 2018-2024
**Geographic Coverage**: National with sectoral breakdowns

#### Components:
- **Sectoral Growth Rates** (`sectoral_growth_rates.csv`)
  - Quarterly growth rates by economic sector
  - 19 major economic sectors covered
  - Alignment with NBS sectoral classifications
  - Source: National Bureau of Statistics (NBS)

- **SME Landscape Reports** (`sme_landscape_reports.csv`)
  - Comprehensive SME statistics from multiple sources
  - Total SME counts, GDP contribution, employment share
  - Size distribution (micro, small, medium enterprises)
  - Sectoral distribution and key constraints
  - Innovation adoption rates and digital readiness
  - Sources: SMEDAN, PwC, McKinsey, World Bank, IFC, AfDB, UNDP

- **SME Sector Breakdown** (`sme_sector_breakdown.csv`)
  - Detailed sectoral analysis of SME distribution
  - Sub-sector level data with employment and revenue metrics
  - Innovation intensity and digital readiness scores
  - Technology adoption levels by sector
  - Growth trajectories and key constraints

### 3. Technology Adoption Indices
**Purpose**: Digital transformation and technology diffusion metrics
**Time Coverage**: 2018-2024
**Geographic Coverage**: National with some regional variations

#### Components:
- **Mobile Money/FinTech Adoption** (`mobile_money_fintech_adoption.csv`)
  - Mobile money user penetration and transaction volumes
  - Digital banking adoption metrics
  - FinTech ecosystem development indicators
  - Payment infrastructure data (POS, ATM, agent banking)
  - Cryptocurrency adoption trends
  - Source: Central Bank of Nigeria (CBN), Nigerian Communications Commission (NCC)

- **ICT Development Index** (`ict_development_index.csv`)
  - ITU ICT Development Index scores and rankings
  - Sub-indices for ICT access, use, and skills
  - Telecommunications infrastructure metrics
  - Internet and broadband penetration data
  - Educational attainment indicators
  - Source: International Telecommunication Union (ITU)

- **Digital Transformation Metrics** (`digital_transformation_metrics.csv`)
  - E-government development indices
  - Digital competitiveness rankings
  - Cybersecurity and AI readiness scores
  - Cloud computing and IoT adoption rates
  - Digital skills and literacy indicators
  - Innovation ecosystem metrics
  - Sources: UN, World Economic Forum, ITU

## Data Quality and Reliability

### Data Sources
- **Primary Sources**: Central Bank of Nigeria (CBN), National Bureau of Statistics (NBS), Nigerian Communications Commission (NCC)
- **International Sources**: World Bank, International Telecommunication Union (ITU), United Nations, World Economic Forum
- **Industry Sources**: SMEDAN, PwC, McKinsey & Company, International Finance Corporation (IFC), African Development Bank (AfDB)

### Data Quality Scores
Each dataset includes quality scores (1-10 scale) based on:
- Source reliability and methodology transparency
- Data completeness and consistency
- Update frequency and timeliness
- Cross-validation with alternative sources

### Limitations and Considerations
1. **Coverage Gaps**: Some rural areas may be underrepresented in technology adoption metrics
2. **Informal Sector**: SME data may not fully capture informal business activities
3. **Methodology Changes**: Some indicators have evolved methodologies over time
4. **Regional Variations**: National averages may mask significant regional differences
5. **Data Lag**: Some indicators have reporting delays of 6-12 months

## Usage Guidelines

### For Machine Learning Applications
- Use macroeconomic indicators as contextual features for SME performance models
- Technology adoption indices can serve as innovation diffusion proxies
- Sectoral data enables industry-specific model development
- Time series nature supports longitudinal analysis and forecasting

### For Validation and Benchmarking
- Cross-validate SME survey data against official statistics
- Use for external validity checks of primary research findings
- Benchmark regional or sectoral performance against national trends
- Validate innovation adoption patterns against technology diffusion data

### Statistical Considerations
- Account for autocorrelation in time series data
- Consider seasonal adjustments for quarterly data
- Apply appropriate transformations for skewed distributions
- Use robust methods for handling missing data points

## File Formats and Structure
- **Format**: CSV files with UTF-8 encoding
- **Missing Values**: Represented as empty cells or "NA"
- **Date Formats**: ISO 8601 standard (YYYY-MM-DD) where applicable
- **Numeric Precision**: Up to 2 decimal places for percentages, 3 for indices
- **Headers**: Descriptive column names with units specified

## Updates and Maintenance
- **Update Frequency**: Quarterly for current indicators, annual for historical revisions
- **Version Control**: Each update includes version timestamp and change log
- **Data Validation**: Automated checks for consistency and outlier detection
- **Documentation**: Methodology notes updated with each data release

## Citation and Attribution
When using this dataset, please cite:
"Nigerian SME Secondary Dataset: Core Dataset 3 for Innovation Adoption Analysis, [Version], [Date], compiled from multiple sources including CBN, NBS, World Bank, and industry reports."

## Contact Information
For questions about data methodology, updates, or specific indicators, please refer to the original source documentation or contact the respective data providers.

---
*Last Updated: October 2024*
*Dataset Version: 1.0*
*Total Records: 2,847 across all files*
*Time Span: 2010-2024*