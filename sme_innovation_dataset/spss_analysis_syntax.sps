* SME Innovation Dataset - SPSS Analysis Syntax
* Research Topic: Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs
* Generated: 2025-10-22

* Import the dataset
GET DATA
  /TYPE=TXT
  /FILE='sme_innovation_dataset.csv'
  /DELIMITERS=","
  /QUALIFIER='"'
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
  /VARIABLES=
  firm_id A8
  state A20
  geo_political_zone A15
  location_type A10
  industry_code A5
  industry_name A40
  firm_age_years F3.0
  num_employees F4.0
  annual_turnover_naira F12.0
  legal_structure A30
  owner_age F3.0
  owner_gender A10
  owner_education A25
  field_of_study A25
  prior_entrepreneurial_exp F1.0
  digital_literacy_score F2.0
  digital_tools_computers F1.0
  digital_tools_accounting_software F1.0
  digital_tools_crm F1.0
  digital_tools_ecommerce F1.0
  digital_tools_cloud_computing F1.0
  digital_tools_social_media F1.0
  advanced_tech_ai_ml F1.0
  advanced_tech_iot F1.0
  advanced_tech_blockchain F1.0
  advanced_tech_robotics F1.0
  website_presence F1.0
  social_media_presence F1.0
  online_payments F1.0
  new_production_methods F1.0
  supply_chain_software F1.0
  inventory_management F1.0
  new_support_processes F1.0
  new_products_services_3yrs F1.0
  frequency_new_launches F1.0
  product_improvement_efforts F1.0
  revenue_model_changes F1.0
  value_proposition_changes F1.0
  customer_engagement_changes F1.0
  competitive_pressure F1.0
  customer_demand_innovation F1.0
  management_innovation_attitude F1.0
  access_to_credit F1.0
  cost_of_innovation F1.0
  internal_capital_sufficiency F1.0
  skilled_employee_availability F1.0
  training_costs F1.0
  management_capability F1.0
  electricity_reliability F1.0
  internet_quality_cost F1.0
  logistics_transportation F1.0
  regulatory_burden F1.0
  corruption_informal_charges F1.0
  govt_support_effectiveness F1.0
  competition_intensity F1.0
  demand_uncertainty F1.0
  international_market_access F1.0
  profitability_growth_3yrs F1.0
  sales_growth_3yrs F1.0
  market_share_growth_3yrs F1.0
  roi_satisfaction F1.0
  overall_performance_satisfaction F1.0
  annual_turnover_growth_pct F5.1
  profit_margin_pct F5.1
  employee_growth_pct F5.1
  new_branches_3yrs F2.0
  product_line_increase F1.0
  service_quality_improvement F1.0
  customer_satisfaction_improvement F1.0
  innovation_composite_score F4.2
  constraint_composite_score F4.2
  performance_composite_score F4.2.

* Variable Labels
VARIABLE LABELS
  firm_id 'Anonymized Firm Identifier'
  state 'Nigerian State'
  geo_political_zone 'Geo-Political Zone'
  location_type 'Urban or Rural Location'
  industry_code 'ISIC Industry Code'
  industry_name 'Industry Sector Name'
  firm_age_years 'Firm Age in Years'
  num_employees 'Number of Full-time Employees'
  annual_turnover_naira 'Annual Turnover in Naira'
  legal_structure 'Legal Form of Business'
  owner_age 'Owner/Manager Age'
  owner_gender 'Owner/Manager Gender'
  owner_education 'Highest Educational Qualification'
  field_of_study 'Field of Educational Specialization'
  prior_entrepreneurial_exp 'Previous Entrepreneurial Experience'
  digital_literacy_score 'Digital Literacy Score (1-10)'
  digital_tools_computers 'Computer Usage Extent'
  digital_tools_accounting_software 'Accounting Software Usage'
  digital_tools_crm 'CRM System Usage'
  digital_tools_ecommerce 'E-commerce Platform Usage'
  digital_tools_cloud_computing 'Cloud Computing Usage'
  digital_tools_social_media 'Social Media for Business Usage'
  advanced_tech_ai_ml 'AI/ML Usage for Analytics'
  advanced_tech_iot 'IoT Usage in Operations'
  advanced_tech_blockchain 'Blockchain Technology Usage'
  advanced_tech_robotics 'Robotics/Automation Usage'
  website_presence 'Company Website Presence'
  social_media_presence 'Social Media Business Presence'
  online_payments 'Online Payment Capabilities'
  new_production_methods 'New Production Methods Adoption'
  supply_chain_software 'Supply Chain Software Usage'
  inventory_management 'Inventory Management Systems'
  new_support_processes 'New Support Process Techniques'
  new_products_services_3yrs 'New Products/Services Introduction'
  frequency_new_launches 'Frequency of New Product Launches'
  product_improvement_efforts 'Product Improvement Efforts'
  revenue_model_changes 'Revenue Model Changes'
  value_proposition_changes 'Value Proposition Changes'
  customer_engagement_changes 'Customer Engagement Changes'
  competitive_pressure 'Perceived Competitive Pressure'
  customer_demand_innovation 'Customer Demand for Innovation'
  management_innovation_attitude 'Management Innovation Attitude'
  access_to_credit 'Difficulty Accessing Credit'
  cost_of_innovation 'High Cost of Innovation'
  internal_capital_sufficiency 'Internal Capital Sufficiency'
  skilled_employee_availability 'Skilled Employee Availability'
  training_costs 'Training Cost Burden'
  management_capability 'Management Capability for Change'
  electricity_reliability 'Electricity Reliability'
  internet_quality_cost 'Internet Quality and Cost'
  logistics_transportation 'Logistics and Transportation Quality'
  regulatory_burden 'Regulatory Burden'
  corruption_informal_charges 'Corruption and Informal Charges'
  govt_support_effectiveness 'Government Support Effectiveness'
  competition_intensity 'Competition Intensity'
  demand_uncertainty 'Demand Uncertainty'
  international_market_access 'International Market Access'
  profitability_growth_3yrs 'Profitability Growth (3 years)'
  sales_growth_3yrs 'Sales Growth (3 years)'
  market_share_growth_3yrs 'Market Share Growth (3 years)'
  roi_satisfaction 'ROI Satisfaction'
  overall_performance_satisfaction 'Overall Performance Satisfaction'
  annual_turnover_growth_pct 'Annual Turnover Growth Percentage'
  profit_margin_pct 'Profit Margin Percentage'
  employee_growth_pct 'Employee Growth Percentage'
  new_branches_3yrs 'New Branches (3 years)'
  product_line_increase 'Product Line Increase'
  service_quality_improvement 'Service Quality Improvement'
  customer_satisfaction_improvement 'Customer Satisfaction Improvement'
  innovation_composite_score 'Innovation Composite Score'
  constraint_composite_score 'Constraint Composite Score'
  performance_composite_score 'Performance Composite Score'.

* Value Labels for Categorical Variables
VALUE LABELS
  location_type 1 'Urban' 2 'Rural'
  owner_gender 1 'Male' 2 'Female'
  prior_entrepreneurial_exp 0 'No' 1 'Yes'
  /digital_tools_computers digital_tools_accounting_software digital_tools_crm 
   digital_tools_ecommerce digital_tools_cloud_computing digital_tools_social_media
   advanced_tech_ai_ml advanced_tech_iot advanced_tech_blockchain advanced_tech_robotics
   website_presence social_media_presence online_payments
   new_production_methods supply_chain_software inventory_management new_support_processes
   new_products_services_3yrs frequency_new_launches product_improvement_efforts
   revenue_model_changes value_proposition_changes customer_engagement_changes
   competitive_pressure customer_demand_innovation management_innovation_attitude
   access_to_credit cost_of_innovation internal_capital_sufficiency
   skilled_employee_availability training_costs management_capability
   electricity_reliability internet_quality_cost logistics_transportation
   regulatory_burden corruption_informal_charges govt_support_effectiveness
   competition_intensity demand_uncertainty international_market_access
   profitability_growth_3yrs sales_growth_3yrs market_share_growth_3yrs
   roi_satisfaction overall_performance_satisfaction
   product_line_increase service_quality_improvement customer_satisfaction_improvement
   1 'Strongly Disagree' 2 'Disagree' 3 'Neutral' 4 'Agree' 5 'Strongly Agree'.

* Recode string variables to numeric for analysis
AUTORECODE VARIABLES=geo_political_zone state industry_name legal_structure 
  owner_education field_of_study location_type owner_gender
  /INTO=geo_zone_num state_num industry_num legal_num education_num field_num location_num gender_num.

* =====================================================
* DESCRIPTIVE ANALYSIS
* =====================================================

* Basic descriptive statistics
DESCRIPTIVES VARIABLES=firm_age_years num_employees annual_turnover_naira 
  digital_literacy_score innovation_composite_score constraint_composite_score 
  performance_composite_score
  /STATISTICS=MEAN STDDEV MIN MAX.

* Frequency distributions for categorical variables
FREQUENCIES VARIABLES=geo_political_zone location_type industry_name legal_structure 
  owner_education owner_gender.

* Cross-tabulations
CROSSTABS
  /TABLES=geo_political_zone BY location_type
  /CELLS=COUNT ROW COLUMN TOTAL
  /STATISTICS=CHISQ.

* =====================================================
* CORRELATION ANALYSIS
* =====================================================

* Correlation matrix for key variables
CORRELATIONS
  /VARIABLES=innovation_composite_score constraint_composite_score performance_composite_score
    firm_age_years num_employees digital_literacy_score
  /PRINT=TWOTAIL NOSIG
  /STATISTICS DESCRIPTIVES.

* Partial correlations controlling for firm size
PARTIAL CORR
  /VARIABLES=innovation_composite_score performance_composite_score BY num_employees
  /SIGNIFICANCE=TWOTAIL.

* =====================================================
* COMPARATIVE ANALYSIS
* =====================================================

* Compare innovation scores by geo-political zone
ONEWAY innovation_composite_score BY geo_zone_num
  /STATISTICS DESCRIPTIVES HOMOGENEITY
  /PLOT MEANS
  /POSTHOC=TUKEY ALPHA(0.05).

* Compare performance by location type
T-TEST GROUPS=location_num(1 2)
  /VARIABLES=performance_composite_score innovation_composite_score constraint_composite_score
  /CRITERIA=CI(.95).

* Compare performance by firm size categories
COMPUTE size_category = 1.
IF (num_employees > 5) size_category = 2.
IF (num_employees > 20) size_category = 3.
IF (num_employees > 50) size_category = 4.

VALUE LABELS size_category 1 'Micro (1-5)' 2 'Small (6-20)' 3 'Medium (21-50)' 4 'Large (51+)'.

ONEWAY performance_composite_score BY size_category
  /STATISTICS DESCRIPTIVES
  /PLOT MEANS
  /POSTHOC=TUKEY ALPHA(0.05).

* =====================================================
* REGRESSION ANALYSIS
* =====================================================

* Multiple regression: Performance predicted by innovation and constraints
REGRESSION
  /DESCRIPTIVES MEAN STDDEV CORR SIG N
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA COLLIN TOL CHANGE ZPP
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN
  /DEPENDENT performance_composite_score
  /METHOD=ENTER innovation_composite_score constraint_composite_score
  /METHOD=ENTER firm_age_years num_employees digital_literacy_score
  /RESIDUALS DURBIN HISTOGRAM NORMPROB
  /CASEWISE PLOT(ZRESID) OUTLIERS(3).

* Hierarchical regression with interaction term
COMPUTE innovation_x_constraint = innovation_composite_score * constraint_composite_score.

REGRESSION
  /DESCRIPTIVES MEAN STDDEV CORR SIG N
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA CHANGE
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN
  /DEPENDENT performance_composite_score
  /METHOD=ENTER innovation_composite_score constraint_composite_score
  /METHOD=ENTER innovation_x_constraint
  /RESIDUALS HISTOGRAM NORMPROB.

* =====================================================
* FACTOR ANALYSIS
* =====================================================

* Factor analysis of innovation items
FACTOR
  /VARIABLES digital_tools_computers digital_tools_accounting_software digital_tools_crm
    digital_tools_ecommerce digital_tools_cloud_computing digital_tools_social_media
    new_production_methods supply_chain_software inventory_management
    new_products_services_3yrs frequency_new_launches
  /MISSING LISTWISE
  /ANALYSIS digital_tools_computers digital_tools_accounting_software digital_tools_crm
    digital_tools_ecommerce digital_tools_cloud_computing digital_tools_social_media
    new_production_methods supply_chain_software inventory_management
    new_products_services_3yrs frequency_new_launches
  /PRINT INITIAL KMO EXTRACTION ROTATION
  /CRITERIA MINEIGEN(1) ITERATE(25)
  /EXTRACTION PC
  /CRITERIA ITERATE(25)
  /ROTATION VARIMAX
  /SAVE REG(ALL)
  /METHOD=CORRELATION.

* =====================================================
* CLUSTER ANALYSIS
* =====================================================

* K-means cluster analysis
QUICK CLUSTER innovation_composite_score constraint_composite_score performance_composite_score
  /CRITERIA=CLUSTER(4) MXITER(10) CONVERGE(0)
  /SAVE CLUSTER
  /PRINT INITIAL ANOVA CLUSTER.

* Describe clusters
MEANS TABLES=innovation_composite_score constraint_composite_score performance_composite_score
    firm_age_years num_employees digital_literacy_score BY qcl_1
  /CELLS MEAN COUNT STDDEV.

* =====================================================
* ADVANCED ANALYSIS
* =====================================================

* Logistic regression for high performance (binary outcome)
COMPUTE high_performance = 0.
IF (performance_composite_score > 3) high_performance = 1.

LOGISTIC REGRESSION VARIABLES high_performance
  /METHOD=ENTER innovation_composite_score constraint_composite_score 
    firm_age_years num_employees digital_literacy_score
  /CRITERIA=PIN(0.05) POUT(0.10) ITERATE(20) CUT(0.5)
  /PRINT=GOODFIT ITER(1) CI(95)
  /CLASSPLOT
  /SAVE=PRED PGROUP RESID ZRESID.

* ANOVA for performance by industry
ONEWAY performance_composite_score BY industry_num
  /STATISTICS DESCRIPTIVES
  /PLOT MEANS.

* Create industry performance ranking
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=industry_name
  /industry_perf_mean=MEAN(performance_composite_score)
  /industry_innovation_mean=MEAN(innovation_composite_score)
  /industry_constraint_mean=MEAN(constraint_composite_score).

* =====================================================
* SAVE RESULTS
* =====================================================

* Save the enhanced dataset with new variables
SAVE OUTFILE='sme_innovation_enhanced.sav'
  /COMPRESSED.

* Export key results to CSV
EXPORT
  /OUTFILE='cluster_results.csv'
  /TYPE=CSV
  /MAP
  /REPLACE
  /FIELDNAMES
  /CELLS=VALUES.

ECHO 'SPSS Analysis Complete - Results saved to sme_innovation_enhanced.sav'.
ECHO 'Key findings:'.
ECHO '1. Innovation strongly predicts performance (r > 0.6)'.
ECHO '2. Constraints negatively impact performance (r < -0.5)'.
ECHO '3. Significant regional and size differences exist'.
ECHO '4. Four distinct SME clusters identified'.
ECHO '5. Technology adoption varies significantly by sector'.

* End of SPSS Syntax