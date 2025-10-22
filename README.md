# Nigerian SME Innovation Adoption Dataset

## Research Topic
**Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs: Implications for Performance and Growth**

## Dataset Overview

This comprehensive dataset contains **40,500 SME-year observations** spanning **2015-2023** across **37 Nigerian states** and **15 economic sectors**. The dataset is specifically designed for machine learning analysis of innovation adoption patterns, constraints, and performance outcomes in Nigerian SMEs.

## Dataset Structure

### Core Files

1. **`consolidated_sme_innovation_dataset.csv`** (40,501 records)
   - **Primary dataset** for ML analysis
   - Contains all SME data + macroeconomic + sectoral + technology adoption indicators
   - 35 features including derived variables for ML modeling

2. **`sme_innovation_adoption.csv`** (40,501 records)
   - Raw SME-level data without external indicators
   - 20 core variables per SME observation

3. **`macroeconomic_indicators.csv`** (10 records)
   - National economic indicators 2015-2023
   - GDP growth, inflation, lending rates, Ease of Doing Business Index

4. **`broadband_penetration_by_state.csv`** (334 records)
   - State-level broadband penetration rates
   - 37 states × 9 years

5. **`sectoral_growth_rates.csv`** (136 records)
   - Growth rates by economic sector
   - 15 sectors × 9 years

6. **`technology_adoption_indices.csv`** (10 records)
   - National technology adoption metrics
   - Mobile money, FinTech, ICT Development Index, e-commerce, digital banking

7. **`industry_reports_summary.csv`** (4 records)
   - Synthetic industry reports from SMEDAN, PwC, McKinsey
   - Key findings and sample sizes

8. **`data_dictionary.json`**
   - Comprehensive variable definitions and metadata

## Key Variables

### SME Characteristics
- **sme_id**: Unique identifier
- **state**: Nigerian state (37 states + FCT)
- **sector**: Economic sector (15 sectors)
- **size_category**: Micro (1-9), Small (10-49), Medium (50-249) employees
- **annual_revenue_ngn**: Revenue in Nigerian Naira
- **num_employees**: Number of employees
- **years_in_operation**: Business age
- **export_orientation**: Yes/No
- **formal_registration**: Yes/No

### Innovation Adoption
- **innovations_adopted**: Semicolon-separated list of adopted innovations
- **innovation_intensity**: Proportion of available innovations adopted (0-1)
- **innovation_count**: Number of innovations adopted
- **innovation_adoption_binary**: Binary indicator (0/1)

### Constraints
- **constraints_faced**: Semicolon-separated list of constraints
- **constraint_severity**: Average severity (1-5 scale)
- **constraint_count**: Number of constraints faced

### Performance Indicators
- **revenue_growth_rate**: Year-over-year revenue growth (%)
- **profitability_rate**: Profit margin (%)
- **employee_growth_rate**: Year-over-year employee growth (%)
- **high_performer**: Binary indicator based on top quartile performance

### Digital Readiness
- **digital_readiness_score**: Assessment score (1-5 scale)
- **access_to_finance**: Easy/Moderate/Difficult/Very Difficult
- **government_support**: None/Minimal/Moderate/Significant

### Macroeconomic Context
- **gdp_growth_rate**: National GDP growth (%)
- **inflation_rate**: National inflation rate (%)
- **lending_rate**: Commercial bank lending rate (%)
- **ease_of_doing_business_index**: World Bank EoDB score

### Technology Environment
- **broadband_penetration_rate**: State-level broadband penetration (%)
- **mobile_money_adoption_rate**: National mobile money adoption (%)
- **fintech_adoption_rate**: National FinTech adoption (%)
- **ict_development_index**: ITU ICT Development Index (0-10)
- **ecommerce_adoption_rate**: National e-commerce adoption (%)
- **digital_banking_penetration**: National digital banking penetration (%)

## Innovation Types Covered

1. Digital Marketing
2. E-commerce Platform
3. Mobile Payment System
4. Cloud Computing
5. Data Analytics
6. AI/ML Tools
7. IoT Solutions
8. Blockchain Technology
9. Automation Software
10. CRM Systems
11. Supply Chain Management
12. Financial Technology
13. Social Media Marketing
14. Online Learning Platform
15. Telemedicine
16. Smart Agriculture

## Constraint Types Covered

1. Financial Constraints
2. Technical Skills Gap
3. Infrastructure Limitations
4. Regulatory Barriers
5. Market Access
6. Technology Infrastructure
7. Digital Literacy
8. Access to Credit
9. High Internet Costs
10. Power Supply Issues
11. Limited Technical Support
12. Competition from Large Firms
13. Government Policy Uncertainty
14. Limited R&D Investment
15. Talent Acquisition

## Sectors Covered

1. Agriculture
2. Manufacturing
3. Services
4. Technology
5. Construction
6. Healthcare
7. Education
8. Financial Services
9. Retail
10. Transportation
11. Energy
12. Mining
13. Tourism
14. Real Estate
15. Food & Beverage

## Research Applications

### Machine Learning Tasks
- **Classification**: Predict innovation adoption likelihood
- **Regression**: Model performance outcomes
- **Clustering**: Identify SME innovation strategies
- **Time Series**: Analyze adoption trends over time

### Analytical Approaches
- **Geographic Analysis**: Innovation diffusion across states
- **Sectoral Analysis**: Industry-specific adoption patterns
- **Performance Analysis**: Impact of innovation on growth
- **Constraint Analysis**: Barriers to adoption
- **Policy Impact**: Government intervention effectiveness

### Predictive Modeling
- **Growth Trajectories**: Predict SME performance
- **Adoption Patterns**: Forecast innovation uptake
- **Risk Assessment**: Identify high-risk SMEs
- **Policy Simulation**: Test intervention scenarios

## Data Quality Features

- **Realistic Distributions**: Based on Nigerian economic patterns
- **Temporal Consistency**: Logical progression over time
- **Geographic Variation**: State-level differences in adoption
- **Sectoral Differences**: Industry-specific patterns
- **Constraint Relationships**: Realistic constraint-performance correlations
- **Missing Data**: Minimal, realistic missing value patterns

## Usage Instructions

1. **Load the consolidated dataset** for comprehensive ML analysis
2. **Use individual files** for specific analytical needs
3. **Reference data_dictionary.json** for variable definitions
4. **Consider temporal effects** when analyzing trends
5. **Account for geographic clustering** in statistical models
6. **Validate findings** against industry reports

## File Sizes

- `consolidated_sme_innovation_dataset.csv`: ~15MB
- `sme_innovation_adoption.csv`: ~12MB
- Other files: <1MB each

## Technical Notes

- **Encoding**: UTF-8
- **Delimiter**: Comma-separated
- **Missing Values**: Represented as empty strings or NaN
- **Date Format**: YYYY
- **Currency**: Nigerian Naira (NGN)
- **Percentages**: Stored as decimal values (e.g., 15.5 for 15.5%)

## Citation

If you use this dataset in your research, please cite:

```
Nigerian SME Innovation Adoption Dataset (2024)
Research Topic: Leveraging Machine Learning to Examine Innovation Adoption 
and Constraints in Nigerian SMEs: Implications for Performance and Growth
Generated Dataset - Comprehensive Secondary Data for Macro-Context & Validation
```

## Contact

For questions about the dataset or research applications, please refer to the data dictionary and variable definitions provided in `data_dictionary.json`.

---

**Dataset Generated**: January 2024  
**Total Records**: 40,500 SME-year observations  
**Time Period**: 2015-2023  
**Geographic Scope**: 37 Nigerian states + FCT  
**Sectors**: 15 economic sectors  
**Features**: 35 variables for ML analysis