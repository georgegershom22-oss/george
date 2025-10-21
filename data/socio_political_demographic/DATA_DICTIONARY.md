# Data Dictionary - Socio-Political & Demographic Data for SOFC Research

## Overview
This data dictionary provides detailed descriptions of all datasets generated for the research project: **"Harnessing Domestic Gas for Power: A Techno-Economic and Socio-Political Analysis of Solid Oxide Fuel Cells (SOFCs) in Mitigating Nigeria's Electricity Crisis"**

## Dataset Categories

### 1. DEMOGRAPHIC DATA

#### 1.1 population_density_by_state.csv
**Purpose**: Provides state-level population statistics, urbanization rates, and growth projections

| Field Name | Data Type | Description | Unit/Format | Notes |
|------------|-----------|-------------|-------------|-------|
| State | String | Name of Nigerian state | - | All 36 states + FCT |
| Population_2023 | Integer | Estimated population in 2023 | Persons | Based on projected growth from 2006 census |
| Land_Area_km2 | Float | Total land area of state | Square kilometers | - |
| Population_Density_per_km2 | Float | Population per unit area | Persons/km² | Calculated field |
| Urban_Population | Integer | Urban population | Persons | - |
| Rural_Population | Integer | Rural population | Persons | - |
| Urban_Percentage | Float | Urban population percentage | Percentage (%) | - |
| Rural_Percentage | Float | Rural population percentage | Percentage (%) | - |
| Annual_Growth_Rate_Percent | Float | Population annual growth rate | Percentage (%) | - |
| Capital_City | String | State capital | - | - |
| Major_Cities | String | Major urban centers | Comma-separated | - |

**Source**: National Bureau of Statistics (NBS), National Population Commission projections, academic estimates

#### 1.2 lga_population_detailed.csv
**Purpose**: Provides granular Local Government Area (LGA) level demographic and economic data

| Field Name | Data Type | Description | Unit/Format | Notes |
|------------|-----------|-------------|-------------|-------|
| State | String | State name | - | - |
| LGA | String | Local Government Area name | - | Focus on major commercial/industrial LGAs |
| Population_2023 | Integer | LGA population estimate | Persons | - |
| Land_Area_km2 | Float | LGA land area | Square kilometers | - |
| Population_Density_per_km2 | Float | Population density | Persons/km² | - |
| Urban_Population | Integer | Urban population in LGA | Persons | - |
| Rural_Population | Integer | Rural population in LGA | Persons | - |
| Urban_Percentage | Float | Urbanization level | Percentage (%) | - |
| Economic_Activity_Level | String | Economic intensity classification | Very High/High/Medium/Low | Qualitative assessment |
| Grid_Connection_Rate_Percent | Float | Percentage with grid electricity connection | Percentage (%) | Includes non-functional connections |

**Source**: State statistical bureaus, National Population Commission, field surveys

#### 1.3 urban_growth_projections.csv
**Purpose**: Urban population trends and projections to 2030 for targeting analysis

| Field Name | Data Type | Description | Unit/Format | Notes |
|------------|-----------|-------------|-------------|-------|
| State | String | State name | - | - |
| Urban_Population_2020 | Integer | Urban population baseline | Persons | - |
| Urban_Population_2023 | Integer | Current urban population estimate | Persons | - |
| Urban_Population_2025_Projected | Integer | Projected urban population | Persons | Near-term projection |
| Urban_Population_2030_Projected | Integer | Target year projection | Persons | Policy horizon |
| Annual_Growth_Rate_2020_2023_Percent | Float | Recent urban growth rate | Percentage (%) | - |
| Urbanization_Rate_2023_Percent | Float | Current urbanization level | Percentage (%) | - |
| Urbanization_Rate_2030_Projected_Percent | Float | Projected urbanization level | Percentage (%) | - |
| Key_Urban_Centers | String | Major cities driving growth | Comma-separated | - |

**Source**: UN-Habitat Nigeria, NBS urban development reports, state master plans

---

### 2. INDUSTRIAL & COMMERCIAL DATA

#### 2.1 industrial_clusters_major.csv
**Purpose**: Maps major industrial estates and clusters with power demand profiles

| Field Name | Data Type | Description | Unit/Format | Notes |
|------------|-----------|-------------|-------------|-------|
| Cluster_Name | String | Industrial estate/cluster name | - | - |
| State | String | State location | - | - |
| LGA | String | Local Government Area | - | - |
| Type | String | Industry classification | - | E.g., "Mixed Manufacturing" |
| Location_Coordinates | String | Geographic coordinates | Lat, Long | For mapping |
| Number_of_Companies | Integer | Companies in cluster | Count | Approximate |
| Primary_Industries | String | Main industrial activities | Comma-separated | - |
| Estimated_Power_Demand_MW | Float | Peak power requirement | Megawatts (MW) | Aggregate for cluster |
| Current_Power_Supply_MW | Float | Grid supply received | Megawatts (MW) | Actual average supply |
| Power_Deficit_MW | Float | Unmet power demand | Megawatts (MW) | Met by generators |
| Grid_Reliability_Percent | Float | Grid uptime | Percentage (%) | Hours supplied/24 hours |
| Average_Generator_Runtime_Hours_Per_Day | Float | Daily generator operation | Hours | Average across cluster |
| Estimated_Diesel_Consumption_Liters_Per_Day | Integer | Aggregate diesel use | Liters/day | For cost comparison |
| Industrial_Estate_Area_Hectares | Float | Total land area | Hectares | - |
| Gas_Pipeline_Proximity_km | Float | Distance to nearest gas pipeline | Kilometers | Critical for SOFC feasibility |
| SOFC_Suitability_Score | Float | Suitability rating | 1-10 scale | Composite of multiple factors |

**Source**: Corporate Affairs Commission, state investment bureaus, field surveys, industrial associations

#### 2.2 sme_distribution_by_sector.csv
**Purpose**: Small and Medium Enterprise distribution and power needs by state and sector

| Field Name | Data Type | Description | Unit/Format | Notes |
|------------|-----------|-------------|-------------|-------|
| State | String | State name | - | - |
| Total_Registered_SMEs | Integer | Total registered SMEs | Count | CAC registered |
| Manufacturing | Integer | Manufacturing sector SMEs | Count | - |
| Trading_Commerce | Integer | Trading and commerce SMEs | Count | - |
| Services | Integer | Service sector SMEs | Count | - |
| Agriculture_Agro_Processing | Integer | Agriculture/agro-processing SMEs | Count | - |
| ICT_Technology | Integer | ICT and technology SMEs | Count | - |
| Construction | Integer | Construction sector SMEs | Count | - |
| Transportation | Integer | Transportation services SMEs | Count | - |
| Healthcare | Integer | Healthcare services SMEs | Count | - |
| Education | Integer | Education services SMEs | Count | - |
| Hospitality_Tourism | Integer | Hospitality and tourism SMEs | Count | - |
| Average_Power_Need_kW | Float | Average power requirement per SME | Kilowatts (kW) | Weighted average |
| Total_Estimated_Power_Demand_MW | Float | Aggregate SME power demand | Megawatts (MW) | State-level total |
| Current_Backup_Generator_Percentage | Float | SMEs with backup generators | Percentage (%) | Indicates power reliability issues |

**Source**: Corporate Affairs Commission (CAC), National Association of Small and Medium Enterprises (NASME), SMEDAN

#### 2.3 commercial_buildings_infrastructure.csv
**Purpose**: Major commercial facilities with significant power demands

| Field Name | Data Type | Description | Unit/Format | Notes |
|------------|-----------|-------------|-------------|-------|
| Building_Name | String | Facility name | - | - |
| Type | String | Building category | - | E.g., Shopping Mall, Hotel, Office Complex, Airport, Hospital |
| State | String | State location | - | - |
| LGA | String | Local Government Area | - | - |
| City | String | City/town | - | - |
| Floor_Area_sqm | Integer | Total floor area | Square meters | - |
| Estimated_Peak_Power_Demand_kW | Float | Peak power requirement | Kilowatts (kW) | - |
| Current_Power_Source | String | Primary power sources | - | E.g., "Grid + Generators" |
| Backup_Generator_Capacity_kW | Float | Total generator capacity | Kilowatts (kW) | - |
| Monthly_Diesel_Consumption_Liters | Integer | Average monthly diesel use | Liters/month | - |
| Grid_Connection | String | Grid connection status | Yes/No | - |
| Average_Outage_Hours_Per_Day | Float | Daily power outage duration | Hours | - |
| Annual_Energy_Cost_Naira_Millions | Float | Total annual energy expenditure | Million Naira | Grid + diesel |
| Gas_Pipeline_Distance_km | Float | Distance to gas pipeline | Kilometers | - |
| SOFC_Potential_Rating | String | SOFC deployment potential | Very High/High/Medium/Low/Very Low | Qualitative assessment |

**Source**: Facility management companies, real estate databases, industry surveys

---

### 3. POLICY & REGULATORY DATA

#### 3.1 national_energy_policy_summary.csv
**Purpose**: Overview of relevant national policies and their alignment with SOFC deployment

| Field Name | Data Type | Description | Unit/Format | Notes |
|------------|-----------|-------------|-------------|-------|
| Policy_Area | String | Policy domain | - | E.g., "Renewable Energy", "Gas Utilization" |
| Policy_Name | String | Specific policy/regulation name | - | - |
| Year_Enacted | Integer | Year of enactment | YYYY | - |
| Issuing_Authority | String | Responsible government body | - | - |
| Key_Targets | String | Main policy targets | - | Quantitative where available |
| Target_Year | Integer | Target achievement year | YYYY | - |
| Current_Progress_Percent | Float | Implementation progress | Percentage (%) | As of 2023 |
| Relevance_to_SOFC | String | SOFC relevance level | Very High/High/Medium/Low | - |
| Implementation_Status | String | Current status | Active/Partial/Delayed/Suspended | - |
| Budget_Allocation_Billion_Naira | Float | Allocated budget | Billion Naira | If applicable |
| Key_Challenges | String | Implementation obstacles | - | Brief description |

**Source**: Federal Ministry of Power, Federal Ministry of Petroleum Resources, NERC, policy documents

#### 3.2 regulatory_framework_analysis.csv
**Purpose**: Detailed analysis of regulatory requirements for SOFC deployment

| Field Name | Data Type | Description | Unit/Format | Notes |
|------------|-----------|-------------|-------------|-------|
| Regulatory_Body | String | Responsible agency | - | - |
| Regulation_Type | String | Type of regulation | - | E.g., "Generation License", "Environmental Compliance" |
| Document_Title | String | Regulation name | - | - |
| Year | Integer | Year enacted/updated | YYYY | - |
| Key_Provisions_for_SOFC | String | Relevant provisions | - | Summary |
| Licensing_Requirement | String | License needed | Yes/No + details | - |
| Fee_Structure_Naira | Integer | Application/license fees | Naira | If applicable |
| Processing_Time_Months | String | Approval timeline | Months range | E.g., "6-12" |
| Compliance_Burden_Rating | String | Difficulty of compliance | Very High/High/Medium/Low | Qualitative assessment |
| Investor_Friendliness_Score | Float | Ease of compliance | 1-10 scale | Higher is better |
| Clarity_of_Regulation_Score | Float | Regulatory clarity | 1-10 scale | Higher is clearer |
| Gaps_Identified | String | Regulatory gaps or ambiguities | - | Key issues |

**Source**: NERC, DPR, NCDMB, Federal Ministry of Environment, legal analysis

#### 3.3 import_duty_tax_structure.csv
**Purpose**: Import duties and taxes for SOFC equipment and components

| Field Name | Data Type | Description | Unit/Format | Notes |
|------------|-----------|-------------|-------------|-------|
| Equipment_Category | String | Equipment type | - | - |
| HS_Code | String | Harmonized System code | - | International classification |
| Description | String | Detailed description | - | - |
| Standard_Import_Duty_Percent | Float | Base import duty | Percentage (%) | - |
| VAT_Percent | Float | Value Added Tax | Percentage (%) | Currently 7.5% |
| Levies_and_Surcharges_Percent | Float | Additional charges | Percentage (%) | Various levies |
| Total_Tax_Burden_Percent | Float | Total tax before waivers | Percentage (%) | Sum of all charges |
| Renewable_Energy_Waiver_Eligible | String | Waiver eligibility | Yes/No/Partial | - |
| Waived_Duty_Percent | Float | Duty waived if eligible | Percentage (%) | - |
| Net_Tax_Burden_With_Waiver_Percent | Float | Effective tax rate | Percentage (%) | After waivers |
| Documentation_Required | String | Import documentation | Comma-separated | - |
| Clearance_Complexity | String | Clearance difficulty | High/Medium/Low | - |
| Average_Clearance_Time_Days | String | Typical clearance duration | Days range | E.g., "14-21" |

**Source**: Federal Ministry of Finance, Nigeria Customs Service, Customs and Excise Tariff

#### 3.4 gas_pricing_structure.csv
**Purpose**: Gas pricing for different consumer categories relevant to SOFC operations

| Field Name | Data Type | Description | Unit/Format | Notes |
|------------|-----------|-------------|-------------|-------|
| Consumer_Category | String | Customer type | - | E.g., "Power Generation (Large)", "Industrial (Medium)" |
| Supply_Contract_Type | String | Contract type | - | E.g., "Gas Supply Agreement", "Retail Contract" |
| Gas_Price_USD_per_MMBTU | Float | Gas price | USD/MMBTU | Million British Thermal Units |
| Gas_Price_Naira_per_SCF | Float | Gas price | Naira/SCF | Standard Cubic Feet |
| Transportation_Cost_USD_per_MMBTU | Float | Pipeline transportation cost | USD/MMBTU | Additional to wellhead price |
| Total_Delivered_Cost_USD_per_MMBTU | Float | Total gas cost delivered | USD/MMBTU | Gas price + transportation |
| Contract_Duration_Years | String | Typical contract length | Years range | - |
| Volume_Commitment_MMSCFD | String | Volume commitments | MMSCFD range | Million Standard Cubic Feet per Day |
| Supply_Reliability_Percent | Float | Historical supply reliability | Percentage (%) | - |
| Price_Review_Period_Months | String | Price review frequency | Months | - |
| Price_Indexation | String | Pricing mechanism | - | E.g., "Crude oil prices", "Market pricing" |
| Alternative_Fuel_Cost_Diesel_USD_per_MMBTU | Float | Diesel equivalent cost | USD/MMBTU | For comparison |
| Cost_Advantage_Percent | Float | Gas savings vs diesel | Percentage (%) | Cost difference |
| Regulatory_Framework | String | Governing regulations | - | - |
| Key_Challenges | String | Supply challenges | - | - |

**Source**: Federal Ministry of Petroleum Resources, DPR, gas suppliers, industry reports

#### 3.5 government_priorities_alignment.csv
**Purpose**: Maps SOFC deployment to government priorities and development goals

| Field Name | Data Type | Description | Unit/Format | Notes |
|------------|-----------|-------------|-------------|-------|
| Government_Priority | String | Priority area | - | E.g., "Energy Access", "Industrial Development" |
| Policy_Document | String | Source policy document | - | - |
| Priority_Level | String | Importance level | Very High/High/Medium | - |
| Target_Metric | String | Measurable target | - | - |
| Current_Status | String | Current achievement | - | - |
| SOFC_Contribution_Potential_Score_1_10 | Float | SOFC contribution potential | 1-10 scale | Higher means greater contribution |
| Alignment_with_SOFC_Deployment | String | Alignment level | Very High/High/Medium/Low | - |
| Key_Ministries_Involved | String | Responsible ministries | Semicolon-separated | - |
| Budget_Allocation_Billion_Naira | Float | Budget allocated | Billion Naira | If applicable |
| Political_Support_Level | String | Political backing | Very High/High/Medium | - |
| Implementation_Gaps | String | Key challenges | - | - |
| How_SOFC_Helps | String | SOFC contribution mechanism | - | Explanation |

**Source**: National Development Plans, sectoral policies, ministry strategic plans

---

### 4. SOCIAL PERCEPTION DATA

#### 4.1 stakeholder_survey_results.csv
**Purpose**: Survey results from key stakeholders on SOFC awareness, acceptance, and concerns

| Field Name | Data Type | Description | Unit/Format | Notes |
|------------|-----------|-------------|-------------|-------|
| Respondent_ID | String | Unique respondent identifier | - | E.g., "IND001", "POL002" |
| Stakeholder_Category | String | Stakeholder type | - | E.g., "Industrial Manager", "Policymaker", "Community Leader" |
| State | String | State location | - | - |
| Organization_Type | String | Organization classification | - | - |
| Years_of_Experience | Integer | Professional experience | Years | - |
| Awareness_of_SOFC_Technology | String | SOFC awareness | Yes/Partial/No | - |
| Awareness_Level_Score_1_10 | Float | Awareness depth | 1-10 scale | 1=No knowledge, 10=Expert |
| Willingness_to_Adopt_Score_1_10 | Float | Adoption willingness | 1-10 scale | 1=Not at all, 10=Immediately |
| Perceived_Reliability_vs_Grid_Score_1_10 | Float | Perceived reliability vs grid | 1-10 scale | - |
| Perceived_Reliability_vs_Diesel_Score_1_10 | Float | Perceived reliability vs diesel | 1-10 scale | - |
| Primary_Concern | String | Main concern/barrier | - | Free text |
| Secondary_Concern | String | Second concern/barrier | - | Free text |
| Key_Benefit_Expected | String | Expected main benefit | - | Free text |
| Investment_Capacity_Million_Naira | Float | Investment capacity | Million Naira | For applicable stakeholders |
| Preferred_Financing_Model | String | Financing preference | - | E.g., "Lease/PPA", "Direct purchase" |
| Decision_Timeline_Months | String | Decision timeframe | Months range | - |
| Technical_Knowledge_Score_1_10 | Float | Technical understanding | 1-10 scale | - |
| Environmental_Concern_Score_1_10 | Float | Environmental priorities | 1-10 scale | - |
| Regulatory_Awareness_Score_1_10 | Float | Regulatory knowledge | 1-10 scale | - |

**Source**: Primary surveys conducted August-October 2023 (simulated for research purposes)

#### 4.2 stakeholder_interview_summaries.csv
**Purpose**: Detailed summaries of in-depth stakeholder interviews

| Field Name | Data Type | Description | Unit/Format | Notes |
|------------|-----------|-------------|-------------|-------|
| Interview_ID | String | Unique interview identifier | - | E.g., "INT001" |
| Date | Date | Interview date | YYYY-MM-DD | - |
| Stakeholder_Name | String | Interviewee name | - | Representative names |
| Position | String | Job title/role | - | - |
| Organization | String | Organization name | - | - |
| State | String | Location | - | - |
| Interview_Duration_Minutes | Integer | Interview length | Minutes | - |
| Key_Quotes | String | Notable quotes | - | Excerpts |
| Main_Concerns | String | Primary concerns raised | - | Summary |
| Opportunities_Identified | String | Opportunities seen | - | Summary |
| Recommendations | String | Stakeholder recommendations | - | Summary |
| Adoption_Readiness_Score_1_10 | Float | Readiness to adopt/support | 1-10 scale | - |
| Supporting_Policies_Needed | String | Policy recommendations | - | Summary |
| Collaboration_Willingness | String | Willingness to collaborate | Very High/High/Medium/Low | - |

**Source**: In-depth interviews August-October 2023 (simulated for research purposes)

#### 4.3 technology_adoption_barriers.csv
**Purpose**: Comprehensive analysis of barriers to SOFC adoption in Nigeria

| Field Name | Data Type | Description | Unit/Format | Notes |
|------------|-----------|-------------|-------------|-------|
| Barrier_Category | String | Type of barrier | - | E.g., "Financial", "Technical", "Regulatory" |
| Specific_Barrier | String | Detailed barrier description | - | - |
| Severity_Score_1_10 | Float | Barrier severity | 1-10 scale | 10=Most severe |
| Prevalence_Percent | Float | How widespread | Percentage (%) | Stakeholders affected |
| Primary_Affected_Stakeholder | String | Most affected group | - | - |
| Secondary_Affected_Stakeholder | String | Secondary affected group | - | - |
| Geographic_Concentration | String | Geographic distribution | - | Where most severe |
| Root_Cause | String | Underlying cause | - | - |
| Current_Mitigation_Efforts | String | Existing efforts to address | - | - |
| Mitigation_Effectiveness_Score_1_10 | Float | Effectiveness of current efforts | 1-10 scale | - |
| Recommended_Solutions | String | Proposed solutions | - | - |
| Implementation_Timeline_Years | String | Time to address | Years range | - |
| Estimated_Cost_to_Mitigate_Million_USD | Float | Cost to overcome barrier | Million USD | - |
| Responsibility_for_Mitigation | String | Who should address | - | - |

**Source**: Stakeholder consultations, literature review, expert analysis

#### 4.4 public_perception_survey.csv
**Purpose**: General public awareness and perception of fuel cell technology

| Field Name | Data Type | Description | Unit/Format | Notes |
|------------|-----------|-------------|-------------|-------|
| Survey_ID | String | Unique survey identifier | - | E.g., "PUB001" |
| Region | String | Geopolitical region | - | E.g., "South West", "North Central" |
| State | String | State location | - | - |
| Urban_Rural | String | Settlement type | Urban/Semi-urban/Rural | - |
| Gender | String | Respondent gender | Male/Female | - |
| Age_Group | String | Age bracket | - | E.g., "25-34", "45-54" |
| Education_Level | String | Highest education | - | E.g., "University", "Secondary" |
| Employment_Status | String | Employment type | - | - |
| Heard_of_Fuel_Cells | String | Fuel cell awareness | Yes/Partial/No | - |
| Heard_of_SOFC_Specifically | String | SOFC-specific awareness | Yes/Partial/No | - |
| Source_of_Information | String | Where heard about it | - | E.g., "Internet/Social Media", "Television" |
| Perceived_Safety_Score_1_10 | Float | Perceived safety | 1-10 scale | - |
| Perceived_Cost_vs_Diesel | String | Cost perception | - | Free text response |
| Perceived_Reliability_vs_Grid_Score_1_10 | Float | Reliability perception | 1-10 scale | - |
| Willingness_to_Work_in_SOFC_Industry | String | Employment interest | Yes/Maybe/No | - |
| Environmental_Concern_Score_1_10 | Float | Environmental priority | 1-10 scale | - |
| Support_Government_Investment_in_SOFC | String | Support for public investment | Yes/Unsure/No | - |
| Primary_Energy_Concern | String | Main energy concern | - | Free text |
| Trust_in_New_Technology_Score_1_10 | Float | Technology trust | 1-10 scale | - |
| Preferred_Information_Source | String | Trusted information source | - | - |

**Source**: Public survey September-October 2023 (simulated for research purposes)

---

## Data Quality and Limitations

### Data Sources
1. **Official Statistics**: National Bureau of Statistics, National Population Commission
2. **Regulatory Bodies**: NERC, DPR, NCDMB
3. **Industry Associations**: Manufacturers Association of Nigeria, Nigerian Gas Association
4. **Government Ministries**: Power, Petroleum Resources, Environment, Finance
5. **Academic Research**: Universities and research institutions
6. **Field Surveys**: Simulated stakeholder consultations

### Limitations
1. **Population Data**: Based on projections from 2006 census; 2023 census data not yet officially published
2. **Industrial Data**: Some estimates based on partial reporting and industry surveys
3. **SME Data**: Informal sector not fully captured in CAC registrations
4. **Social Perception**: Simulated survey and interview data representative of expected stakeholder positions
5. **Policy Data**: Policies subject to change; implementation status as of 2023
6. **Gas Pricing**: Subject to market fluctuations and policy changes

### Data Generation Methodology
This dataset was generated using:
- Published government statistics where available
- Academic literature and research reports
- Industry benchmarks and international comparisons
- Expert knowledge of Nigerian energy and industrial sectors
- Realistic simulations for survey and interview data
- Geospatial and demographic modeling

### Usage Recommendations
1. Cross-reference with latest official statistics when available
2. Use state-level data as indicators; verify specific LGA data for critical decisions
3. Treat social perception data as representative scenarios rather than actual survey results
4. Update policy information regularly as regulations evolve
5. Validate industrial cluster data with local sources before investment decisions

---

## Data Update Schedule
- **Demographic Data**: Annual updates recommended
- **Industrial Data**: Bi-annual updates
- **Policy Data**: Quarterly monitoring for changes
- **Social Perception**: Continuous monitoring as deployment progresses

## Contact and Feedback
For questions, corrections, or additional data requirements, please refer to the research project documentation.

---

**Last Updated**: October 2023  
**Dataset Version**: 1.0  
**Research Project**: SOFC Techno-Economic and Socio-Political Analysis for Nigeria
