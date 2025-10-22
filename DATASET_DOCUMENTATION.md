# Nigerian SME Innovation Adoption and Constraints Dataset

## Research Context
**Research Topic:** Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs: Implications for Performance and Growth

**Dataset Purpose:** This comprehensive dataset is designed to support machine learning analysis of innovation adoption patterns, constraint factors, and their impact on SME performance in Nigeria.

## Dataset Overview
- **Total Firms:** 2,000 Nigerian SMEs
- **Total Variables:** 66 variables across 4 main sections
- **Geographic Coverage:** All 36 states + FCT, representing all 6 geopolitical zones
- **Industry Coverage:** 15 major industry sectors with ISIC codes
- **Data Quality:** Realistic correlations and relationships based on Nigerian SME characteristics

## File Formats Available
1. **CSV:** `nigerian_sme_innovation_dataset.csv` - Main dataset for analysis
2. **Excel:** `nigerian_sme_innovation_dataset.xlsx` - Multi-sheet workbook with organized sections
3. **JSON:** `nigerian_sme_innovation_dataset.json` - Structured data format

## Dataset Structure

### Section A: Firmographics & Managerial Characteristics (8 variables)
**Purpose:** Firm and owner/manager background information

| Variable Name | Type | Description | Values/Range |
|---------------|------|-------------|--------------|
| `firm_id` | String | Unique firm identifier | NG_SME_0001 to NG_SME_2000 |
| `state` | Categorical | Nigerian state | 36 states + FCT |
| `geo_political_zone` | Categorical | Geopolitical zone | North-East, North-West, North-Central, South-East, South-South, South-West |
| `location_type` | Categorical | Urban/Rural classification | Urban, Rural |
| `industry` | Categorical | Industry sector | 15 sectors (Manufacturing, Retail Trade, IT Services, etc.) |
| `isic_code` | String | ISIC industry code | Standard ISIC codes |
| `firm_age_category` | Categorical | Age category | 0-2, 3-5, 6-10, 11-15, 16-20, 21-25, 26-30, 31-40, 40+ |
| `firm_age_years` | Numeric | Actual years of operation | 1.5 to 45 years |
| `employee_size_category` | Categorical | Employee size category | 1-5, 6-10, 11-25, 26-50, 50+ |
| `num_employees` | Numeric | Actual number of employees | 3 to 75 employees |
| `annual_turnover_ngn` | Numeric | Annual turnover in Naira | Log-normally distributed |
| `legal_structure` | Categorical | Legal form | Sole Proprietorship, Partnership, Limited Liability Company, Cooperative |
| `owner_age` | Numeric | Owner/manager age | 25 to 70 years |
| `owner_gender` | Categorical | Owner/manager gender | Male, Female |
| `owner_education` | Categorical | Education level | Primary, Secondary, Diploma, Bachelor, Master, PhD |
| `owner_field_of_study` | Categorical | Field of study | 12 fields including Business Administration, Engineering, etc. |
| `prior_entrepreneurial_experience` | Numeric | Years of prior experience | 0 to 20 years |
| `digital_literacy_score` | Numeric | Digital skills score | 1 to 10 scale |

### Section B: Innovation Adoption - Independent Variables (10 variables)
**Purpose:** Measures of various types of innovation adoption

| Variable Name | Type | Scale | Description |
|---------------|------|-------|-------------|
| `digital_tools_adoption` | Numeric | 1-5 | Extent of digital tools use (computers, software, e-commerce) |
| `advanced_tech_adoption` | Numeric | 1-5 | Use of advanced technologies (AI/ML, IoT, blockchain) |
| `level_of_digitization` | Numeric | 1-5 | Overall digital presence and capabilities |
| `process_innovation` | Numeric | 1-5 | Adoption of new production/delivery methods |
| `product_service_innovation` | Numeric | 1-5 | Introduction of new/improved products/services |
| `business_model_innovation` | Numeric | 1-5 | Changes in revenue models and value propositions |
| `competitive_pressure` | Numeric | 1-5 | Perceived competitive pressure |
| `customer_demand_innovation` | Numeric | 1-5 | Customer demand for innovation |
| `mgmt_attitude_innovation` | Numeric | 1-5 | Top management attitude towards innovation |

### Section C: Constraint Assessment - Moderating Variables (10 variables)
**Purpose:** Factors that may moderate innovation adoption and performance

#### Financial Constraints
| Variable Name | Type | Scale | Description |
|---------------|------|-------|-------------|
| `financial_constraints` | Numeric | 1-5 | Overall financial constraint level |
| `access_to_credit` | Numeric | 1-5 | Access to loans and credit facilities |
| `cost_of_innovation` | Numeric | 1-5 | Perceived cost of innovation activities |
| `sufficiency_internal_capital` | Numeric | 1-5 | Sufficiency of internal capital for investment |

#### Human Capital Constraints
| Variable Name | Type | Scale | Description |
|---------------|------|-------|-------------|
| `human_capital_constraints` | Numeric | 1-5 | Overall human capital constraint level |
| `skilled_employee_difficulty` | Numeric | 1-5 | Difficulty finding skilled employees |
| `cost_of_training` | Numeric | 1-5 | Cost of training existing staff |
| `mgmt_capability_change` | Numeric | 1-5 | Management capability for change |

#### Infrastructural Constraints
| Variable Name | Type | Scale | Description |
|---------------|------|-------|-------------|
| `infrastructure_constraints` | Numeric | 1-5 | Overall infrastructure constraint level |
| `electricity_reliability` | Numeric | 1-5 | Reliability of electricity supply |
| `internet_quality` | Numeric | 1-5 | Quality of internet connectivity |
| `internet_cost` | Numeric | 1-5 | Cost of internet services |
| `logistics_access` | Numeric | 1-5 | Access to logistics and transportation |

#### Regulatory and Institutional Constraints
| Variable Name | Type | Scale | Description |
|---------------|------|-------|-------------|
| `regulatory_constraints` | Numeric | 1-5 | Overall regulatory constraint level |
| `regulation_burden` | Numeric | 1-5 | Burden of government regulations |
| `corruption_level` | Numeric | 1-5 | Level of corruption and informal charges |
| `gov_support_effectiveness` | Numeric | 1-5 | Effectiveness of government support programs |

#### Market Constraints
| Variable Name | Type | Scale | Description |
|---------------|------|-------|-------------|
| `market_constraints` | Numeric | 1-5 | Overall market constraint level |
| `competition_intensity` | Numeric | 1-5 | Intensity of competition |
| `demand_uncertainty` | Numeric | 1-5 | Uncertainty of demand |
| `intl_market_access` | Numeric | 1-5 | Access to international markets |

### Section D: Firm Performance and Growth - Dependent Variables (11 variables)
**Purpose:** Measures of firm performance and growth outcomes

#### Subjective Performance (1-5 scale)
| Variable Name | Type | Scale | Description |
|---------------|------|-------|-------------|
| `profitability_growth` | Numeric | 1-5 | Perceived profitability growth |
| `sales_growth` | Numeric | 1-5 | Perceived sales growth |
| `market_share_growth` | Numeric | 1-5 | Perceived market share growth |
| `roi_satisfaction` | Numeric | 1-5 | Satisfaction with return on investment |
| `overall_performance_satisfaction` | Numeric | 1-5 | Overall business performance satisfaction |

#### Objective Performance
| Variable Name | Type | Description |
|---------------|------|-------------|
| `turnover_growth_range` | Categorical | Turnover growth category |
| `turnover_growth_percent` | Numeric | Actual turnover growth percentage |
| `profit_growth_percent` | Numeric | Profit growth percentage |
| `employee_growth_percent` | Numeric | Employee growth percentage |
| `new_branches_3years` | Numeric | Number of new branches in 3 years |
| `new_clients_3years` | Numeric | Number of new clients in 3 years |

#### Non-Financial Growth Indicators (1-5 scale)
| Variable Name | Type | Scale | Description |
|---------------|------|-------|-------------|
| `product_service_lines_increase` | Numeric | 1-5 | Increase in product/service lines |
| `quality_improvement` | Numeric | 1-5 | Improvement in product/service quality |
| `customer_satisfaction_improvement` | Numeric | 1-5 | Improvement in customer satisfaction |
| `customer_retention_improvement` | Numeric | 1-5 | Improvement in customer retention |

### Derived Variables
| Variable Name | Type | Description |
|---------------|------|-------------|
| `innovation_index` | Numeric | Composite innovation score (average of innovation variables) |
| `constraint_index` | Numeric | Composite constraint score (average of constraint variables) |
| `performance_index` | Numeric | Composite performance score (average of performance variables) |

## Data Generation Methodology

### Realistic Correlations
The dataset includes realistic correlations based on Nigerian SME characteristics:

1. **Innovation Adoption Correlations:**
   - Higher digital literacy → Higher innovation adoption
   - Urban location → Higher digitization levels
   - Larger firms → More advanced technology adoption
   - IT services firms → Higher innovation across all types

2. **Constraint Correlations:**
   - Rural location → Higher infrastructure constraints
   - Smaller firms → Higher financial constraints
   - Limited liability companies → Higher regulatory constraints
   - IT services → Higher human capital constraints

3. **Performance Correlations:**
   - Innovation adoption → Higher performance
   - Constraint levels → Lower performance
   - Firm size and age → Moderate performance impact

### Statistical Distributions
- **Firm Age:** Skewed towards younger firms (most SMEs are relatively new)
- **Firm Size:** Heavily skewed towards small firms (1-10 employees)
- **Geographic Distribution:** 70% urban, 30% rural
- **Industry Distribution:** Manufacturing and retail trade most common
- **Education Levels:** Normal distribution with peak at Bachelor's degree

## Usage Recommendations

### For Machine Learning Analysis
1. **Classification Tasks:**
   - Predict innovation adoption levels
   - Classify performance categories
   - Identify constraint severity levels

2. **Regression Tasks:**
   - Predict performance metrics
   - Model innovation adoption drivers
   - Analyze constraint impacts

3. **Clustering:**
   - Segment SMEs by innovation patterns
   - Group by constraint profiles
   - Identify performance clusters

### Data Preprocessing
1. **Categorical Variables:** Use appropriate encoding (one-hot, label encoding)
2. **Scale Variables:** Standardize for algorithms requiring normalized inputs
3. **Missing Values:** Dataset is complete, but consider validation strategies
4. **Outliers:** Check for extreme values in financial metrics

### Research Applications
1. **Innovation Studies:** Analyze adoption patterns and drivers
2. **Constraint Analysis:** Identify key barriers to SME growth
3. **Performance Modeling:** Understand factors affecting SME success
4. **Policy Analysis:** Evaluate impact of different constraint types
5. **Regional Analysis:** Compare performance across geopolitical zones

## Technical Notes

### Data Quality
- All variables are complete (no missing values)
- Realistic value ranges based on Nigerian SME context
- Proper correlation structures maintained
- Balanced representation across categories

### File Formats
- **CSV:** Best for statistical software (R, Python, SPSS)
- **Excel:** Multi-sheet format for easy exploration
- **JSON:** Structured format for web applications

### Computational Requirements
- Dataset size: ~2MB (CSV), ~3MB (Excel), ~5MB (JSON)
- Memory: ~50MB when loaded into pandas
- Processing: Suitable for standard statistical software

## Citation and Usage
This dataset is generated for research purposes focusing on Nigerian SME innovation adoption and constraints. When using this dataset, please acknowledge the research context and methodology.

## Contact and Support
For questions about the dataset structure or usage, refer to the comprehensive variable descriptions above. The dataset is designed to be self-explanatory with clear variable names and descriptions.