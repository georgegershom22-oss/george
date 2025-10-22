# Nigerian SME Innovation Dataset - Data Dictionary

## Research Topic
**Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs: Implications for Performance and Growth**

## Dataset Overview
This comprehensive dataset captures innovation adoption patterns, operational constraints, and performance metrics for Nigerian Small and Medium Enterprises (SMEs). The dataset is structured to support machine learning analysis of the relationships between innovation, constraints, and firm performance.

---

## Section A: Firmographics & Managerial Characteristics

### Firm Identification & Location
| Variable | Type | Description | Values/Range |
|----------|------|-------------|--------------|
| firm_id | String | Unique anonymized firm identifier | SME_00001 to SME_99999 |
| state | String | Nigerian state location | 36 states + FCT |
| geo_political_zone | String | Geopolitical zone | North-Central, North-East, North-West, South-East, South-South, South-West |
| location_type | String | Urban or rural classification | Urban, Rural |

### Firm Characteristics
| Variable | Type | Description | Values/Range |
|----------|------|-------------|--------------|
| industry_sector | String | Industry classification (ISIC-based) | Manufacturing, Wholesale and Retail Trade, Information and Communication, etc. |
| firm_age_years | Integer | Years since establishment | 1-50 years |
| num_employees | Integer | Total full-time employees | 1-250 |
| annual_turnover_million_naira | Float | Annual revenue in millions of Naira | 0.1-10,000 |
| legal_structure | String | Business legal form | Sole Proprietorship, Partnership, Limited Liability |

### Owner/Manager Profile
| Variable | Type | Description | Values/Range |
|----------|------|-------------|--------------|
| owner_age | Integer | Age of owner/manager | 25-70 years |
| owner_gender | String | Gender of owner/manager | Male, Female |
| owner_education_level | String | Highest education attained | No Formal Education, Primary, Secondary, Bachelor, Postgraduate |
| owner_field_of_study | String | Field of academic study | Business Administration, Engineering, Computer Science, etc. (N/A if < Bachelor) |
| prior_entrepreneurial_experience_years | Integer | Years of prior business experience | 0-45 years |
| digital_literacy_score | Float | Self-assessed digital competency | 1.0-10.0 |

---

## Section B: Innovation Adoption (Independent Variables)
*All innovation variables measured on Likert scale: 1 = Strongly Disagree/Never, 5 = Strongly Agree/Always*

### Technological Innovation
| Variable | Type | Description | Scale |
|----------|------|-------------|-------|
| digital_tools_computers | Float | Extent of computer usage | 1-5 |
| digital_tools_accounting_software | Float | Use of accounting software | 1-5 |
| digital_tools_crm | Float | Customer Relationship Management adoption | 1-5 |
| digital_tools_ecommerce | Float | E-commerce platform usage | 1-5 |
| digital_tools_cloud_computing | Float | Cloud services adoption | 1-5 |
| digital_tools_social_media | Float | Social media for business | 1-5 |
| advanced_tech_ai_ml | Float | AI/ML analytics usage | 1-5 |
| advanced_tech_iot | Float | Internet of Things implementation | 1-5 |
| advanced_tech_blockchain | Float | Blockchain technology adoption | 1-5 |
| advanced_tech_robotics | Float | Robotics/automation usage | 1-5 |
| digitization_level_composite | Float | Overall digitization score | 1-5 |

### Process Innovation
| Variable | Type | Description | Scale |
|----------|------|-------------|-------|
| process_new_production_methods | Float | Adoption of new production/delivery methods | 1-5 |
| process_supply_chain_software | Float | Supply chain management software usage | 1-5 |
| process_support_techniques | Float | New support process techniques | 1-5 |

### Product/Service Innovation
| Variable | Type | Description | Scale |
|----------|------|-------------|-------|
| product_new_goods_services_3years | Float | New products/services in last 3 years | 1-5 |
| product_launch_frequency | Float | Frequency of new product launches | 1-5 |

### Business Model Innovation
| Variable | Type | Description | Scale |
|----------|------|-------------|-------|
| business_model_revenue_changes | Float | Changes in revenue models | 1-5 |
| business_model_value_proposition | Float | Value proposition modifications | 1-5 |

### Innovation Drivers
| Variable | Type | Description | Scale |
|----------|------|-------------|-------|
| driver_competitive_pressure | Float | Perceived competitive pressure | 1-5 |
| driver_customer_demand | Float | Customer demand for innovation | 1-5 |
| driver_management_attitude | Float | Management's innovation attitude | 1-5 |

---

## Section C: Constraint Assessment (Moderating Variables)
*All constraint variables measured on Likert scale: 1 = No constraint, 5 = Severe constraint*

### Financial Constraints
| Variable | Type | Description | Scale |
|----------|------|-------------|-------|
| constraint_access_to_credit | Float | Difficulty accessing loans/credit | 1-5 |
| constraint_innovation_cost | Float | High cost of innovation | 1-5 |
| constraint_internal_capital | Float | Insufficient internal funds for R&D | 1-5 |

### Human Capital Constraints
| Variable | Type | Description | Scale |
|----------|------|-------------|-------|
| constraint_finding_skilled_employees | Float | Difficulty finding qualified staff | 1-5 |
| constraint_training_cost | Float | High cost of staff training | 1-5 |
| constraint_management_capability | Float | Limited management capability for change | 1-5 |

### Infrastructure Constraints
| Variable | Type | Description | Scale |
|----------|------|-------------|-------|
| constraint_electricity_reliability | Float | Unreliable power supply | 1-5 |
| constraint_internet_quality_cost | Float | Poor/expensive internet | 1-5 |
| constraint_logistics_transportation | Float | Logistics/transportation challenges | 1-5 |

### Regulatory & Institutional Constraints
| Variable | Type | Description | Scale |
|----------|------|-------------|-------|
| constraint_regulations_taxes | Float | Burden of regulations and taxes | 1-5 |
| constraint_corruption_informal_charges | Float | Corruption and informal payments | 1-5 |
| constraint_government_support_effectiveness | Float | Ineffective government support (inverted) | 1-5 |

### Market Constraints
| Variable | Type | Description | Scale |
|----------|------|-------------|-------|
| constraint_competition_intensity | Float | Intense market competition | 1-5 |
| constraint_demand_uncertainty | Float | Uncertain market demand | 1-5 |
| constraint_international_market_access | Float | Limited access to international markets | 1-5 |

---

## Section D: Firm Performance & Growth (Dependent Variables)

### Subjective Performance Measures
*Measured on Likert scale: 1 = Very Poor, 5 = Excellent*

| Variable | Type | Description | Scale |
|----------|------|-------------|-------|
| performance_profitability_growth | Float | Profitability growth (last 3 years) | 1-5 |
| performance_sales_growth | Float | Sales growth (last 3 years) | 1-5 |
| performance_market_share_growth | Float | Market share growth | 1-5 |
| performance_roi | Float | Return on investment | 1-5 |
| performance_overall_satisfaction | Float | Overall business performance satisfaction | 1-5 |

### Objective Performance Measures
| Variable | Type | Description | Unit |
|----------|------|-------------|------|
| objective_turnover_growth_percent | Float | Annual turnover growth rate | % |
| objective_profit_margin_percent | Float | Net profit margin | % |
| objective_employee_growth_percent | Float | Employee growth rate | % |
| objective_new_branches | Integer | Number of new branches opened | Count |
| objective_new_clients | Integer | Number of new clients acquired | Count |

### Non-Financial Growth Indicators
| Variable | Type | Description | Scale/Unit |
|----------|------|-------------|-----------|
| growth_product_lines_increase | Float | Increase in product/service lines | 1-5 |
| growth_quality_improvement | Float | Product/service quality improvement | 1-5 |
| growth_customer_satisfaction | Float | Customer satisfaction improvement | 1-5 |
| growth_customer_retention_rate | Float | Customer retention rate | % |

---

## Calculated Composite Scores

### Innovation Scores
| Variable | Type | Description | Range |
|----------|------|-------------|-------|
| innovation_technology_score | Float | Average of all technology innovation variables | 1-5 |
| innovation_process_score | Float | Average of process innovation variables | 1-5 |
| innovation_product_score | Float | Average of product innovation variables | 1-5 |
| innovation_business_model_score | Float | Average of business model innovation variables | 1-5 |
| innovation_overall_score | Float | Overall innovation composite score | 1-5 |

### Constraint Scores
| Variable | Type | Description | Range |
|----------|------|-------------|-------|
| constraint_financial_score | Float | Average of financial constraint variables | 1-5 |
| constraint_human_capital_score | Float | Average of human capital constraint variables | 1-5 |
| constraint_infrastructure_score | Float | Average of infrastructure constraint variables | 1-5 |
| constraint_regulatory_score | Float | Average of regulatory constraint variables | 1-5 |
| constraint_market_score | Float | Average of market constraint variables | 1-5 |
| constraint_overall_score | Float | Overall constraint composite score | 1-5 |

### Performance Score
| Variable | Type | Description | Range |
|----------|------|-------------|-------|
| performance_subjective_score | Float | Average of subjective performance measures | 1-5 |

---

## Survey Metadata
| Variable | Type | Description | Values/Range |
|----------|------|-------------|--------------|
| survey_date | DateTime | Date survey was completed | 2024-01-15 to 2024-04-15 |
| survey_response_time_minutes | Integer | Time taken to complete survey | 15-90 minutes |
| data_quality_score | Float | Data quality assessment score | 0.0-1.0 |

---

## Usage Guidelines

### For Machine Learning Applications:
1. **Target Variables**: Use performance and growth variables as dependent variables
2. **Features**: Innovation adoption variables as primary features
3. **Moderators**: Constraint variables can be used as interaction terms
4. **Control Variables**: Firmographics for controlling firm-specific effects

### Data Preprocessing Recommendations:
1. Scale Likert variables (already 1-5) can be used as-is or normalized
2. Categorical variables should be one-hot encoded
3. Consider log transformation for turnover and employee count
4. Check for multicollinearity among innovation variables
5. Use composite scores to reduce dimensionality if needed

### Missing Data:
- This synthetic dataset has no missing values
- In real applications, consider multiple imputation for missing Likert responses
- "N/A" in field_of_study indicates education below Bachelor level

### Statistical Considerations:
- Likert scales treated as continuous for regression analyses
- Consider ordinal regression for individual Likert items as outcomes
- Use robust standard errors to account for heteroscedasticity
- Consider multilevel models if clustering by state/zone

---

## Citation
When using this dataset, please reference:
"Nigerian SME Innovation Adoption Dataset (2024): A Synthetic Dataset for Machine Learning Analysis of Innovation, Constraints, and Performance"

## License
This synthetic dataset is provided for research and educational purposes.

## Contact
For questions about the dataset structure or variables, please refer to this documentation or the accompanying analysis notebooks.