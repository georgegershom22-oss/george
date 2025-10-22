# Nigerian SME Innovation Dataset - Detailed Codebook

## Variable Definitions and Coding Schemes

### Section A: Firmographics & Managerial Characteristics

#### A1. Firm Identification
**firm_id** (String)
- **Description:** Unique identifier for each firm
- **Format:** NG_SME_XXXX (where XXXX is a 4-digit number)
- **Range:** NG_SME_0001 to NG_SME_2000
- **Usage:** Primary key for data analysis

#### A2. Geographic Information
**state** (Categorical)
- **Description:** Nigerian state where the firm is located
- **Values:** 36 states + Federal Capital Territory (FCT)
- **Coding:** Full state names as strings
- **Examples:** "Lagos", "Kano", "Rivers", "Abuja"

**geo_political_zone** (Categorical)
- **Description:** Geopolitical zone classification
- **Values:** 
  - North-East: Adamawa, Bauchi, Borno, Gombe, Taraba, Yobe
  - North-West: Kaduna, Kano, Katsina, Kebbi, Sokoto, Zamfara, Jigawa
  - North-Central: Abuja, Benue, Kogi, Kwara, Nasarawa, Niger, Plateau
  - South-East: Abia, Anambra, Ebonyi, Enugu, Imo
  - South-South: Akwa Ibom, Bayelsa, Cross River, Delta, Edo, Rivers
  - South-West: Lagos, Ogun, Ondo, Osun, Oyo, Ekiti

**location_type** (Categorical)
- **Description:** Urban or rural classification
- **Values:** "Urban", "Rural"
- **Distribution:** 70% Urban, 30% Rural (realistic for SME distribution)

#### A3. Industry Classification
**industry** (Categorical)
- **Description:** Primary industry sector
- **Values:** 15 major sectors
- **Distribution:** Weighted based on Nigerian SME reality
  - Manufacturing: 15%
  - Retail Trade: 12%
  - Agriculture: 12%
  - IT Services: 8%
  - Construction: 8%
  - Others: 45%

**isic_code** (String)
- **Description:** International Standard Industrial Classification code
- **Format:** ISIC Rev. 4 codes
- **Examples:** "10-33" (Manufacturing), "47" (Retail Trade), "62-63" (IT Services)

#### A4. Firm Characteristics
**firm_age_category** (Categorical)
- **Description:** Age category in years of operation
- **Values:** "0-2", "3-5", "6-10", "11-15", "16-20", "21-25", "26-30", "31-40", "40+"
- **Distribution:** Skewed towards younger firms (25% in 0-2 years)

**firm_age_years** (Numeric)
- **Description:** Actual years of operation
- **Range:** 1.5 to 45 years
- **Derivation:** Midpoint of age categories with some variation

**employee_size_category** (Categorical)
- **Description:** Employee size category
- **Values:** "1-5", "6-10", "11-25", "26-50", "50+"
- **Distribution:** Heavily skewed towards small firms (40% in 1-5 employees)

**num_employees** (Numeric)
- **Description:** Actual number of full-time employees
- **Range:** 3 to 75 employees
- **Derivation:** Representative values for each category

**annual_turnover_ngn** (Numeric)
- **Description:** Annual turnover in Nigerian Naira
- **Range:** Log-normally distributed
- **Typical Range:** ₦500,000 to ₦500,000,000
- **Correlation:** Positively correlated with firm size

**legal_structure** (Categorical)
- **Description:** Legal form of business organization
- **Values:** 
  - "Sole Proprietorship" (45%)
  - "Limited Liability Company" (35%)
  - "Partnership" (15%)
  - "Cooperative" (5%)

#### A5. Owner/Manager Profile
**owner_age** (Numeric)
- **Description:** Age of primary owner/manager
- **Range:** 25 to 70 years
- **Distribution:** Normal distribution with mean 42, std 12

**owner_gender** (Categorical)
- **Description:** Gender of primary owner/manager
- **Values:** "Male" (65%), "Female" (35%)
- **Note:** Reflects typical SME ownership patterns in Nigeria

**owner_education** (Categorical)
- **Description:** Highest education level
- **Values:** "Primary", "Secondary", "Diploma", "Bachelor", "Master", "PhD"
- **Distribution:** 
  - Bachelor: 35%
  - Diploma: 20%
  - Master: 20%
  - Secondary: 15%
  - Primary: 5%
  - PhD: 5%

**owner_field_of_study** (Categorical)
- **Description:** Field of study for highest education
- **Values:** 12 fields including "Business Administration", "Engineering", "Computer Science", etc.
- **Distribution:** Business Administration most common (20%)

**prior_entrepreneurial_experience** (Numeric)
- **Description:** Years of prior entrepreneurial experience
- **Range:** 0 to 20 years
- **Distribution:** Exponential distribution with mean 3 years

**digital_literacy_score** (Numeric)
- **Description:** Self-assessed digital literacy level
- **Range:** 1 to 10 scale
- **Correlation:** Positively correlated with education level, negatively with age
- **Calculation:** Base score + education bonus - age penalty

### Section B: Innovation Adoption (Independent Variables)

#### B1. Technological Innovation
**digital_tools_adoption** (Numeric, 1-5 scale)
- **Description:** Extent of digital tools usage
- **Scale:** 1 = Strongly Disagree, 5 = Strongly Agree
- **Items:** Use of computers, accounting software, CRM, e-commerce platforms, cloud computing, social media
- **Correlation:** Positively correlated with digital literacy and firm size

**advanced_tech_adoption** (Numeric, 1-5 scale)
- **Description:** Use of advanced technologies
- **Scale:** 1 = Strongly Disagree, 5 = Strongly Agree
- **Items:** AI/ML for analytics, IoT in operations, blockchain, robotics
- **Correlation:** Positively correlated with firm size and owner education

**level_of_digitization** (Numeric, 1-5 scale)
- **Description:** Overall digital presence and capabilities
- **Scale:** 1 = Very Low, 5 = Very High
- **Items:** Website presence, social media engagement, online payment systems
- **Correlation:** Positively correlated with digital literacy and urban location

#### B2. Process Innovation
**process_innovation** (Numeric, 1-5 scale)
- **Description:** Adoption of new production/delivery methods
- **Scale:** 1 = Strongly Disagree, 5 = Strongly Agree
- **Items:** New production methods, supply chain software, supporting process improvements
- **Correlation:** Positively correlated with firm size and manufacturing industry

#### B3. Product/Service Innovation
**product_service_innovation** (Numeric, 1-5 scale)
- **Description:** Introduction of new or improved products/services
- **Scale:** 1 = Strongly Disagree, 5 = Strongly Agree
- **Items:** New product launches, service improvements, innovation frequency
- **Correlation:** Positively correlated with IT services and newer firms

#### B4. Business Model Innovation
**business_model_innovation** (Numeric, 1-5 scale)
- **Description:** Changes in revenue models and value propositions
- **Scale:** 1 = Strongly Disagree, 5 = Strongly Agree
- **Items:** Subscription models, freemium, customer engagement strategies
- **Correlation:** Positively correlated with IT services and retail trade

#### B5. Innovation Drivers
**competitive_pressure** (Numeric, 1-5 scale)
- **Description:** Perceived competitive pressure
- **Scale:** 1 = Very Low, 5 = Very High
- **Correlation:** Higher in retail trade and IT services

**customer_demand_innovation** (Numeric, 1-5 scale)
- **Description:** Customer demand for innovation
- **Scale:** 1 = Very Low, 5 = Very High
- **Correlation:** Higher in IT services and urban locations

**mgmt_attitude_innovation** (Numeric, 1-5 scale)
- **Description:** Top management attitude towards innovation
- **Scale:** 1 = Very Negative, 5 = Very Positive
- **Correlation:** Positively correlated with education level and younger age

### Section C: Constraint Assessment (Moderating Variables)

#### C1. Financial Constraints
**financial_constraints** (Numeric, 1-5 scale)
- **Description:** Overall financial constraint level
- **Scale:** 1 = No Constraints, 5 = Severe Constraints
- **Correlation:** Higher for smaller firms and sole proprietorships

**access_to_credit** (Numeric, 1-5 scale)
- **Description:** Access to loans and credit facilities
- **Scale:** 1 = Very Poor, 5 = Excellent
- **Correlation:** Better for larger firms and limited liability companies

**cost_of_innovation** (Numeric, 1-5 scale)
- **Description:** Perceived cost of innovation activities
- **Scale:** 1 = Very Low, 5 = Very High
- **Correlation:** Higher for IT services and rural locations

**sufficiency_internal_capital** (Numeric, 1-5 scale)
- **Description:** Sufficiency of internal capital for investment
- **Scale:** 1 = Very Insufficient, 5 = Very Sufficient
- **Correlation:** Higher for larger and older firms

#### C2. Human Capital Constraints
**human_capital_constraints** (Numeric, 1-5 scale)
- **Description:** Overall human capital constraint level
- **Scale:** 1 = No Constraints, 5 = Severe Constraints
- **Correlation:** Higher in rural areas and IT services

**skilled_employee_difficulty** (Numeric, 1-5 scale)
- **Description:** Difficulty finding skilled employees
- **Scale:** 1 = Very Easy, 5 = Very Difficult
- **Correlation:** Higher in rural areas and IT services

**cost_of_training** (Numeric, 1-5 scale)
- **Description:** Cost of training existing staff
- **Scale:** 1 = Very Low, 5 = Very High
- **Correlation:** Higher for IT services and rural locations

**mgmt_capability_change** (Numeric, 1-5 scale)
- **Description:** Management capability for change
- **Scale:** 1 = Very Poor, 5 = Excellent
- **Correlation:** Positively correlated with education and experience

#### C3. Infrastructural Constraints
**infrastructure_constraints** (Numeric, 1-5 scale)
- **Description:** Overall infrastructure constraint level
- **Scale:** 1 = No Constraints, 5 = Severe Constraints
- **Correlation:** Higher in rural areas and northern zones

**electricity_reliability** (Numeric, 1-5 scale)
- **Description:** Reliability of electricity supply
- **Scale:** 1 = Very Unreliable, 5 = Very Reliable
- **Correlation:** Better in urban areas and Lagos state

**internet_quality** (Numeric, 1-5 scale)
- **Description:** Quality of internet connectivity
- **Scale:** 1 = Very Poor, 5 = Excellent
- **Correlation:** Better in urban areas, Lagos, and Abuja

**internet_cost** (Numeric, 1-5 scale)
- **Description:** Cost of internet services
- **Scale:** 1 = Very Low, 5 = Very High
- **Correlation:** Higher in rural areas

**logistics_access** (Numeric, 1-5 scale)
- **Description:** Access to logistics and transportation
- **Scale:** 1 = Very Poor, 5 = Excellent
- **Correlation:** Better in urban areas and Lagos

#### C4. Regulatory and Institutional Constraints
**regulatory_constraints** (Numeric, 1-5 scale)
- **Description:** Overall regulatory constraint level
- **Scale:** 1 = No Constraints, 5 = Severe Constraints
- **Correlation:** Higher for limited liability companies

**regulation_burden** (Numeric, 1-5 scale)
- **Description:** Burden of government regulations
- **Scale:** 1 = Very Low, 5 = Very High
- **Correlation:** Higher for limited liability companies

**corruption_level** (Numeric, 1-5 scale)
- **Description:** Level of corruption and informal charges
- **Scale:** 1 = Very Low, 5 = Very High
- **Correlation:** Slightly higher in rural areas

**gov_support_effectiveness** (Numeric, 1-5 scale)
- **Description:** Effectiveness of government support programs
- **Scale:** 1 = Very Ineffective, 5 = Very Effective
- **Correlation:** Better in urban areas

#### C5. Market Constraints
**market_constraints** (Numeric, 1-5 scale)
- **Description:** Overall market constraint level
- **Scale:** 1 = No Constraints, 5 = Severe Constraints
- **Correlation:** Higher in manufacturing and rural areas

**competition_intensity** (Numeric, 1-5 scale)
- **Description:** Intensity of competition
- **Scale:** 1 = Very Low, 5 = Very High
- **Correlation:** Higher in retail trade, IT services, and urban areas

**demand_uncertainty** (Numeric, 1-5 scale)
- **Description:** Uncertainty of demand
- **Scale:** 1 = Very Low, 5 = Very High
- **Correlation:** Higher in agriculture and newer firms

**intl_market_access** (Numeric, 1-5 scale)
- **Description:** Access to international markets
- **Scale:** 1 = Very Poor, 5 = Excellent
- **Correlation:** Better for larger firms, manufacturing, and urban areas

### Section D: Firm Performance and Growth (Dependent Variables)

#### D1. Subjective Performance (1-5 scale)
**profitability_growth** (Numeric, 1-5 scale)
- **Description:** Perceived profitability growth over last 3 years
- **Scale:** 1 = Declining, 5 = Rapidly Growing
- **Correlation:** Positively correlated with innovation, negatively with constraints

**sales_growth** (Numeric, 1-5 scale)
- **Description:** Perceived sales growth over last 3 years
- **Scale:** 1 = Declining, 5 = Rapidly Growing
- **Correlation:** Similar to profitability growth

**market_share_growth** (Numeric, 1-5 scale)
- **Description:** Perceived market share growth over last 3 years
- **Scale:** 1 = Declining, 5 = Rapidly Growing
- **Correlation:** Positively correlated with innovation

**roi_satisfaction** (Numeric, 1-5 scale)
- **Description:** Satisfaction with return on investment
- **Scale:** 1 = Very Dissatisfied, 5 = Very Satisfied
- **Correlation:** Positively correlated with performance

**overall_performance_satisfaction** (Numeric, 1-5 scale)
- **Description:** Overall business performance satisfaction
- **Scale:** 1 = Very Dissatisfied, 5 = Very Satisfied
- **Correlation:** Composite of other performance measures

#### D2. Objective Performance
**turnover_growth_range** (Categorical)
- **Description:** Turnover growth category
- **Values:** 
  - "Declining (>-10%)"
  - "Declining (0 to -10%)"
  - "Slow Growth (0-10%)"
  - "Moderate Growth (10-25%)"
  - "Strong Growth (25-50%)"
  - "Rapid Growth (>50%)"

**turnover_growth_percent** (Numeric)
- **Description:** Actual turnover growth percentage
- **Range:** -30% to 100%
- **Distribution:** Normal distribution with mean 15%, std 25%

**profit_growth_percent** (Numeric)
- **Description:** Profit growth percentage
- **Range:** -50% to 80%
- **Correlation:** Correlated with turnover growth

**employee_growth_percent** (Numeric)
- **Description:** Employee growth percentage
- **Range:** -20% to 60%
- **Correlation:** Positively correlated with performance

**new_branches_3years** (Numeric)
- **Description:** Number of new branches in last 3 years
- **Range:** 0 to 5
- **Distribution:** Poisson distribution

**new_clients_3years** (Numeric)
- **Description:** Number of new clients in last 3 years
- **Range:** 0 to 50
- **Distribution:** Poisson distribution

#### D3. Non-Financial Growth Indicators (1-5 scale)
**product_service_lines_increase** (Numeric, 1-5 scale)
- **Description:** Increase in product/service lines
- **Scale:** 1 = No Increase, 5 = Significant Increase
- **Correlation:** Positively correlated with innovation

**quality_improvement** (Numeric, 1-5 scale)
- **Description:** Improvement in product/service quality
- **Scale:** 1 = No Improvement, 5 = Significant Improvement
- **Correlation:** Positively correlated with process innovation

**customer_satisfaction_improvement** (Numeric, 1-5 scale)
- **Description:** Improvement in customer satisfaction
- **Scale:** 1 = No Improvement, 5 = Significant Improvement
- **Correlation:** Positively correlated with performance

**customer_retention_improvement** (Numeric, 1-5 scale)
- **Description:** Improvement in customer retention
- **Scale:** 1 = No Improvement, 5 = Significant Improvement
- **Correlation:** Positively correlated with performance

### Derived Variables

**innovation_index** (Numeric)
- **Description:** Composite innovation score
- **Calculation:** Average of digital_tools_adoption, process_innovation, product_service_innovation, business_model_innovation
- **Range:** 1 to 5
- **Usage:** Single measure of overall innovation adoption

**constraint_index** (Numeric)
- **Description:** Composite constraint score
- **Calculation:** Average of financial_constraints, human_capital_constraints, infrastructure_constraints, regulatory_constraints, market_constraints
- **Range:** 1 to 5
- **Usage:** Single measure of overall constraint level

**performance_index** (Numeric)
- **Description:** Composite performance score
- **Calculation:** Average of profitability_growth, sales_growth, market_share_growth, overall_performance_satisfaction
- **Range:** 1 to 5
- **Usage:** Single measure of overall performance

## Data Quality Notes

### Completeness
- All 2,000 records are complete (no missing values)
- All variables have valid values within specified ranges
- No data entry errors or inconsistencies

### Validity
- All categorical variables have valid category values
- All numeric variables are within specified ranges
- Logical relationships between variables are maintained

### Reliability
- Consistent measurement scales across similar variables
- Realistic correlation patterns based on Nigerian SME context
- Appropriate statistical distributions for each variable type

### Representativeness
- Geographic distribution reflects Nigerian population patterns
- Industry distribution matches Nigerian SME sector composition
- Firm size distribution typical of SME populations
- Owner characteristics reflect Nigerian demographic patterns

## Usage Guidelines

### Data Analysis
1. **Descriptive Analysis:** Use appropriate measures for each variable type
2. **Correlation Analysis:** Check for expected relationships between variables
3. **Regression Analysis:** Consider variable interactions and multicollinearity
4. **Clustering:** Use standardized variables for distance-based algorithms
5. **Classification:** Consider class imbalance in categorical target variables

### Statistical Software
- **R:** Use factor() for categorical variables, scale() for standardization
- **Python:** Use pandas for data manipulation, scikit-learn for ML
- **SPSS:** Use appropriate measurement levels for each variable
- **Stata:** Use proper variable labels and value labels

### Research Applications
- **Innovation Studies:** Focus on Section B variables
- **Constraint Analysis:** Use Section C variables
- **Performance Studies:** Analyze Section D variables
- **Policy Analysis:** Combine all sections for comprehensive analysis