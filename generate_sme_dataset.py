"""
Nigerian SME Innovation Dataset Generator
==========================================
This script generates a comprehensive synthetic dataset for research on:
"Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs"

Dataset includes:
- Section A: Firmographics & Managerial Characteristics
- Section B: Innovation Adoption (Independent Variables)
- Section C: Constraint Assessment (Moderating Variables)
- Section D: Firm Performance and Growth (Dependent Variables)
"""

import numpy as np
import pandas as pd
from datetime import datetime
import json

# Set random seed for reproducibility
np.random.seed(42)

# Sample size - robust enough for ML
N_SAMPLES = 800

print("=" * 80)
print("NIGERIAN SME INNOVATION DATASET GENERATOR")
print("=" * 80)
print(f"\nGenerating dataset with {N_SAMPLES} SME respondents...")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# SECTION A: FIRMOGRAPHICS & MANAGERIAL CHARACTERISTICS
# ============================================================================

print("Section A: Generating Firmographics & Managerial Characteristics...")

# Nigerian States by Geo-Political Zone
STATES_BY_ZONE = {
    'South West': ['Lagos', 'Ogun', 'Oyo', 'Osun', 'Ondo', 'Ekiti'],
    'South East': ['Abia', 'Anambra', 'Ebonyi', 'Enugu', 'Imo'],
    'South South': ['Akwa Ibom', 'Bayelsa', 'Cross River', 'Delta', 'Edo', 'Rivers'],
    'North Central': ['Benue', 'Kogi', 'Kwara', 'Nasarawa', 'Niger', 'Plateau', 'FCT'],
    'North East': ['Adamawa', 'Bauchi', 'Borno', 'Gombe', 'Taraba', 'Yobe'],
    'North West': ['Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Sokoto', 'Zamfara']
}

# ISIC Industry Classifications
INDUSTRIES = {
    'Manufacturing': 'C',
    'Retail Trade': 'G47',
    'Wholesale Trade': 'G46',
    'Information Technology': 'J62',
    'Professional Services': 'M',
    'Food Services': 'I56',
    'Agriculture': 'A01',
    'Construction': 'F',
    'Transportation': 'H49',
    'Hospitality': 'I55',
    'Education Services': 'P85',
    'Healthcare': 'Q86',
    'Financial Services': 'K64',
    'Real Estate': 'L68',
    'Creative Industries': 'R90'
}

# Generate Firm IDs
firm_ids = [f"SME_{i:04d}" for i in range(1, N_SAMPLES + 1)]

# Geo-Political Zones (weighted by economic activity)
zone_weights = [0.35, 0.20, 0.15, 0.15, 0.08, 0.07]  # SW has most SME activity
zones = np.random.choice(
    list(STATES_BY_ZONE.keys()), 
    size=N_SAMPLES, 
    p=zone_weights
)

# States based on zones
states = [np.random.choice(STATES_BY_ZONE[zone]) for zone in zones]

# Urban/Rural (70% urban as most SMEs are urban)
locations = np.random.choice(['Urban', 'Rural'], size=N_SAMPLES, p=[0.70, 0.30])

# Industries (weighted distribution)
industry_names = list(INDUSTRIES.keys())
industry_weights = [0.18, 0.16, 0.08, 0.12, 0.10, 0.08, 0.06, 0.05, 0.04, 0.05, 0.02, 0.02, 0.02, 0.01, 0.01]
industries = np.random.choice(industry_names, size=N_SAMPLES, p=industry_weights)
isic_codes = [INDUSTRIES[ind] for ind in industries]

# Firm Age (years) - exponential distribution, most firms are young
firm_ages = np.clip(np.random.exponential(scale=7, size=N_SAMPLES), 0.5, 50).astype(int)

# Firm Size - Employees (most are micro/small)
# Micro: 1-10, Small: 11-50, Medium: 51-200
size_category = np.random.choice(['Micro', 'Small', 'Medium'], size=N_SAMPLES, p=[0.60, 0.30, 0.10])
employees = []
for cat in size_category:
    if cat == 'Micro':
        employees.append(np.random.randint(1, 11))
    elif cat == 'Small':
        employees.append(np.random.randint(11, 51))
    else:
        employees.append(np.random.randint(51, 201))

# Annual Turnover (Naira) - correlated with employee count
annual_turnover = []
for emp, cat in zip(employees, size_category):
    if cat == 'Micro':
        base = np.random.uniform(500000, 10000000)  # 500k - 10M
    elif cat == 'Small':
        base = np.random.uniform(10000000, 100000000)  # 10M - 100M
    else:
        base = np.random.uniform(100000000, 500000000)  # 100M - 500M
    
    # Add some correlation with employees
    annual_turnover.append(int(base * (1 + 0.01 * emp)))

# Legal Structure
legal_structures = np.random.choice(
    ['Sole Proprietorship', 'Partnership', 'Limited Liability Company'],
    size=N_SAMPLES,
    p=[0.45, 0.25, 0.30]
)

# Owner/Manager Profile
owner_ages = np.clip(np.random.normal(42, 10, N_SAMPLES), 25, 70).astype(int)
genders = np.random.choice(['Male', 'Female'], size=N_SAMPLES, p=[0.65, 0.35])

education_levels = np.random.choice(
    ['Secondary', 'OND/NCE', 'HND/Bachelor', 'Postgraduate'],
    size=N_SAMPLES,
    p=[0.15, 0.25, 0.45, 0.15]
)

fields_of_study = np.random.choice(
    ['Business/Management', 'Engineering', 'Sciences', 'Arts/Humanities', 
     'Computer Science/IT', 'Social Sciences', 'Education', 'Other'],
    size=N_SAMPLES,
    p=[0.30, 0.15, 0.08, 0.07, 0.18, 0.10, 0.07, 0.05]
)

# Prior entrepreneurial experience (years)
prior_experience = np.clip(np.random.exponential(scale=3, size=N_SAMPLES), 0, 25).astype(int)

# Digital Literacy Score (1-10, correlated with education and age)
digital_literacy = []
for edu, age in zip(education_levels, owner_ages):
    base = 5
    if edu == 'Postgraduate':
        base = 7
    elif edu == 'HND/Bachelor':
        base = 6
    elif edu == 'OND/NCE':
        base = 5
    else:
        base = 4
    
    # Younger owners tend to be more digitally literate
    age_factor = (50 - age) / 30  # Decreases with age
    score = base + age_factor + np.random.normal(0, 1)
    digital_literacy.append(np.clip(score, 1, 10))

# ============================================================================
# SECTION B: INNOVATION ADOPTION (INDEPENDENT VARIABLES)
# ============================================================================

print("Section B: Generating Innovation Adoption Variables...")

def likert_correlated(base_score, n, std=0.8):
    """Generate correlated Likert scale responses (1-5)"""
    scores = np.random.normal(base_score, std, n)
    return np.clip(np.round(scores), 1, 5).astype(int)

# Base innovation propensity (latent variable influenced by firm characteristics)
innovation_propensity = []
for i in range(N_SAMPLES):
    score = 2.5  # baseline
    
    # Firm age effect (U-shaped: very young and very old less innovative)
    if 3 <= firm_ages[i] <= 15:
        score += 0.5
    
    # Size effect (larger firms more innovative)
    if size_category[i] == 'Medium':
        score += 0.7
    elif size_category[i] == 'Small':
        score += 0.3
    
    # Education effect
    if education_levels[i] == 'Postgraduate':
        score += 0.6
    elif education_levels[i] == 'HND/Bachelor':
        score += 0.3
    
    # Digital literacy effect
    score += (digital_literacy[i] - 5) / 5
    
    # Industry effect (IT more innovative)
    if industries[i] in ['Information Technology', 'Professional Services', 'Creative Industries']:
        score += 0.5
    
    # Location effect (urban more innovative)
    if locations[i] == 'Urban':
        score += 0.2
    
    # Add noise
    score += np.random.normal(0, 0.5)
    
    innovation_propensity.append(np.clip(score, 1, 5))

# B1: Technological Innovation - Digital Tools Adoption (Likert 1-5)
tech_computers = likert_correlated(np.array(innovation_propensity), N_SAMPLES, 0.6)
tech_accounting_software = likert_correlated(np.array(innovation_propensity) - 0.3, N_SAMPLES, 0.7)
tech_crm = likert_correlated(np.array(innovation_propensity) - 0.5, N_SAMPLES, 0.8)
tech_ecommerce = likert_correlated(np.array(innovation_propensity) - 0.4, N_SAMPLES, 0.8)
tech_cloud = likert_correlated(np.array(innovation_propensity) - 0.6, N_SAMPLES, 0.9)
tech_social_media = likert_correlated(np.array(innovation_propensity) + 0.2, N_SAMPLES, 0.7)

# Advanced Tech Adoption (lower adoption rates)
tech_ai_ml = likert_correlated(np.array(innovation_propensity) - 1.5, N_SAMPLES, 0.8)
tech_iot = likert_correlated(np.array(innovation_propensity) - 1.7, N_SAMPLES, 0.7)
tech_blockchain = likert_correlated(np.array(innovation_propensity) - 2.0, N_SAMPLES, 0.6)
tech_robotics = likert_correlated(np.array(innovation_propensity) - 1.8, N_SAMPLES, 0.6)

# Digital Presence Score (1-5)
digital_website = likert_correlated(np.array(innovation_propensity) - 0.5, N_SAMPLES, 0.9)
digital_social_media = likert_correlated(np.array(innovation_propensity), N_SAMPLES, 0.7)
digital_online_payments = likert_correlated(np.array(innovation_propensity) - 0.7, N_SAMPLES, 0.9)

# B2: Process Innovation
process_new_production = likert_correlated(np.array(innovation_propensity), N_SAMPLES, 0.8)
process_supply_chain_software = likert_correlated(np.array(innovation_propensity) - 0.6, N_SAMPLES, 0.9)
process_inventory_mgmt = likert_correlated(np.array(innovation_propensity) - 0.4, N_SAMPLES, 0.8)
process_hr_software = likert_correlated(np.array(innovation_propensity) - 0.7, N_SAMPLES, 0.9)

# B3: Product/Service Innovation
product_new_services = likert_correlated(np.array(innovation_propensity) + 0.2, N_SAMPLES, 0.8)
product_improvements = likert_correlated(np.array(innovation_propensity) + 0.3, N_SAMPLES, 0.7)
product_launch_frequency = likert_correlated(np.array(innovation_propensity), N_SAMPLES, 0.8)

# B4: Business Model Innovation
bm_revenue_model = likert_correlated(np.array(innovation_propensity) - 0.3, N_SAMPLES, 0.9)
bm_value_proposition = likert_correlated(np.array(innovation_propensity), N_SAMPLES, 0.8)
bm_customer_engagement = likert_correlated(np.array(innovation_propensity) + 0.1, N_SAMPLES, 0.8)

# B5: Innovation Drivers
driver_competition = likert_correlated(3.5, N_SAMPLES, 0.9)
driver_customer_demand = likert_correlated(3.7, N_SAMPLES, 0.8)
driver_management_attitude = np.array(innovation_propensity).astype(int)

# ============================================================================
# SECTION C: CONSTRAINT ASSESSMENT (MODERATING VARIABLES)
# ============================================================================

print("Section C: Generating Constraint Assessment Variables...")

# Base constraint severity (inverse of development - higher in rural, certain zones)
constraint_base = []
for i in range(N_SAMPLES):
    score = 3.0  # baseline moderate constraints
    
    # Location effect
    if locations[i] == 'Rural':
        score += 0.5
    
    # Zone effect (North has more constraints)
    if 'North' in zones[i]:
        score += 0.3
    
    # Size effect (smaller firms face more constraints)
    if size_category[i] == 'Micro':
        score += 0.4
    elif size_category[i] == 'Small':
        score += 0.2
    
    # Add noise
    score += np.random.normal(0, 0.4)
    
    constraint_base.append(np.clip(score, 1, 5))

# C1: Financial Constraints (higher = more constrained)
fin_access_credit = likert_correlated(np.array(constraint_base) + 0.3, N_SAMPLES, 0.8)
fin_cost_innovation = likert_correlated(np.array(constraint_base) + 0.5, N_SAMPLES, 0.7)
fin_internal_capital = 6 - likert_correlated(np.array(constraint_base) + 0.2, N_SAMPLES, 0.8)  # Reverse coded

# C2: Human Capital Constraints
hc_skilled_employees = likert_correlated(np.array(constraint_base) + 0.4, N_SAMPLES, 0.8)
hc_training_cost = likert_correlated(np.array(constraint_base) + 0.3, N_SAMPLES, 0.7)
hc_leadership_capability = 6 - likert_correlated(np.array(constraint_base), N_SAMPLES, 0.9)  # Reverse coded

# C3: Infrastructural Constraints
infra_electricity = likert_correlated(np.array(constraint_base) + 0.8, N_SAMPLES, 0.9)  # Major issue
infra_internet_quality = likert_correlated(np.array(constraint_base) + 0.4, N_SAMPLES, 0.9)
infra_internet_cost = likert_correlated(np.array(constraint_base) + 0.5, N_SAMPLES, 0.8)
infra_logistics = likert_correlated(np.array(constraint_base) + 0.3, N_SAMPLES, 0.8)

# C4: Regulatory and Institutional Constraints
reg_burden = likert_correlated(np.array(constraint_base) + 0.6, N_SAMPLES, 0.9)
reg_corruption = likert_correlated(np.array(constraint_base) + 0.7, N_SAMPLES, 1.0)
reg_govt_support = 6 - likert_correlated(np.array(constraint_base) + 0.4, N_SAMPLES, 1.0)  # Reverse

# C5: Market Constraints
mkt_competition = likert_correlated(3.8, N_SAMPLES, 0.8)  # Generally high
mkt_demand_uncertainty = likert_correlated(np.array(constraint_base) + 0.2, N_SAMPLES, 0.9)
mkt_international_access = 6 - likert_correlated(np.array(constraint_base) + 0.8, N_SAMPLES, 1.0)  # Reverse

# ============================================================================
# SECTION D: FIRM PERFORMANCE AND GROWTH (DEPENDENT VARIABLES)
# ============================================================================

print("Section D: Generating Performance and Growth Variables...")

# Performance is positively influenced by innovation, negatively by constraints
performance_base = []
for i in range(N_SAMPLES):
    # Innovation effect (positive)
    innov_score = innovation_propensity[i]
    
    # Constraint effect (negative)
    const_score = constraint_base[i]
    
    # Combined effect
    perf = 2.0 + (innov_score - 2.5) * 0.6 - (const_score - 3.0) * 0.4
    
    # Firm characteristics
    if size_category[i] == 'Medium':
        perf += 0.3
    
    if firm_ages[i] > 5:  # Established firms perform better
        perf += 0.2
    
    # Add noise
    perf += np.random.normal(0, 0.5)
    
    performance_base.append(np.clip(perf, 1, 5))

# D1: Subjective Performance (Likert 1-5)
perf_profitability = likert_correlated(np.array(performance_base), N_SAMPLES, 0.7)
perf_sales = likert_correlated(np.array(performance_base) + 0.1, N_SAMPLES, 0.7)
perf_market_share = likert_correlated(np.array(performance_base) - 0.2, N_SAMPLES, 0.8)
perf_roi = likert_correlated(np.array(performance_base) - 0.1, N_SAMPLES, 0.8)
perf_satisfaction = likert_correlated(np.array(performance_base), N_SAMPLES, 0.7)

# D2: Objective Performance (some missing data as expected)
# Turnover growth % (last 3 years) - correlated with performance
turnover_growth = []
for perf in performance_base:
    if np.random.random() < 0.70:  # 70% response rate
        growth = (perf - 2.5) * 10 + np.random.normal(5, 15)  # Mean ~5%, influenced by performance
        turnover_growth.append(np.clip(growth, -30, 80))
    else:
        turnover_growth.append(np.nan)

# Profit margin % - correlated with performance
profit_margin = []
for perf in performance_base:
    if np.random.random() < 0.60:  # 60% response rate (more sensitive)
        margin = (perf - 2.5) * 5 + np.random.normal(8, 6)
        profit_margin.append(np.clip(margin, -10, 40))
    else:
        profit_margin.append(np.nan)

# Employee growth rate %
employee_growth = []
for perf in performance_base:
    if np.random.random() < 0.75:  # 75% response rate
        growth = (perf - 2.5) * 8 + np.random.normal(3, 10)
        employee_growth.append(np.clip(growth, -20, 50))
    else:
        employee_growth.append(np.nan)

# New branches (count in last 3 years)
new_branches = []
for perf, size in zip(performance_base, size_category):
    if np.random.random() < 0.80:  # 80% response rate
        prob = (perf - 1) / 8  # Higher performance = more branches
        if size == 'Medium':
            branches = np.random.poisson(prob * 3)
        elif size == 'Small':
            branches = np.random.poisson(prob * 1.5)
        else:
            branches = np.random.poisson(prob * 0.5)
        new_branches.append(min(branches, 10))
    else:
        new_branches.append(np.nan)

# D3: Non-Financial Growth Indicators (Likert 1-5)
growth_product_lines = likert_correlated(np.array(performance_base), N_SAMPLES, 0.8)
growth_quality = likert_correlated(np.array(performance_base) + 0.2, N_SAMPLES, 0.7)
growth_customer_satisfaction = likert_correlated(np.array(performance_base) + 0.3, N_SAMPLES, 0.7)
growth_customer_retention = likert_correlated(np.array(performance_base) + 0.2, N_SAMPLES, 0.7)

# ============================================================================
# CREATE COMPOSITE INDICES
# ============================================================================

print("\nCalculating Composite Indices...")

# Technology Innovation Index (mean of tech variables)
tech_index = np.mean([
    tech_computers, tech_accounting_software, tech_crm, tech_ecommerce,
    tech_cloud, tech_social_media
], axis=0)

# Advanced Technology Index
advanced_tech_index = np.mean([
    tech_ai_ml, tech_iot, tech_blockchain, tech_robotics
], axis=0)

# Digital Presence Index
digital_presence_index = np.mean([
    digital_website, digital_social_media, digital_online_payments
], axis=0)

# Process Innovation Index
process_innovation_index = np.mean([
    process_new_production, process_supply_chain_software,
    process_inventory_mgmt, process_hr_software
], axis=0)

# Product Innovation Index
product_innovation_index = np.mean([
    product_new_services, product_improvements, product_launch_frequency
], axis=0)

# Overall Innovation Index
overall_innovation_index = np.mean([
    tech_index, process_innovation_index, product_innovation_index,
    digital_presence_index
], axis=0)

# Financial Constraint Index
financial_constraint_index = np.mean([
    fin_access_credit, fin_cost_innovation, 6 - fin_internal_capital
], axis=0)

# Infrastructure Constraint Index
infra_constraint_index = np.mean([
    infra_electricity, infra_internet_quality, infra_internet_cost, infra_logistics
], axis=0)

# Overall Constraint Index
overall_constraint_index = np.mean([
    financial_constraint_index, infra_constraint_index,
    hc_skilled_employees, reg_burden, mkt_demand_uncertainty
], axis=0)

# Overall Performance Index
overall_performance_index = np.mean([
    perf_profitability, perf_sales, perf_market_share, perf_roi, perf_satisfaction
], axis=0)

# ============================================================================
# BUILD MASTER DATAFRAME
# ============================================================================

print("\nAssembling Master Dataset...")

data = {
    # Section A: Firmographics
    'Firm_ID': firm_ids,
    'State': states,
    'Geo_Political_Zone': zones,
    'Location_Type': locations,
    'Industry': industries,
    'ISIC_Code': isic_codes,
    'Firm_Age_Years': firm_ages,
    'Num_Employees': employees,
    'Size_Category': size_category,
    'Annual_Turnover_Naira': annual_turnover,
    'Legal_Structure': legal_structures,
    'Owner_Age': owner_ages,
    'Owner_Gender': genders,
    'Owner_Education': education_levels,
    'Owner_Field_of_Study': fields_of_study,
    'Owner_Prior_Experience_Years': prior_experience,
    'Owner_Digital_Literacy_Score': digital_literacy,
    
    # Section B: Innovation Adoption
    'Tech_Computers': tech_computers,
    'Tech_Accounting_Software': tech_accounting_software,
    'Tech_CRM': tech_crm,
    'Tech_Ecommerce_Platform': tech_ecommerce,
    'Tech_Cloud_Computing': tech_cloud,
    'Tech_Social_Media_Business': tech_social_media,
    'Tech_AI_ML': tech_ai_ml,
    'Tech_IoT': tech_iot,
    'Tech_Blockchain': tech_blockchain,
    'Tech_Robotics': tech_robotics,
    'Digital_Website': digital_website,
    'Digital_Social_Media_Presence': digital_social_media,
    'Digital_Online_Payments': digital_online_payments,
    'Process_New_Production_Methods': process_new_production,
    'Process_Supply_Chain_Software': process_supply_chain_software,
    'Process_Inventory_Management': process_inventory_mgmt,
    'Process_HR_Software': process_hr_software,
    'Product_New_Services_3yrs': product_new_services,
    'Product_Improvements': product_improvements,
    'Product_Launch_Frequency': product_launch_frequency,
    'Business_Model_Revenue_Change': bm_revenue_model,
    'Business_Model_Value_Proposition': bm_value_proposition,
    'Business_Model_Customer_Engagement': bm_customer_engagement,
    'Driver_Competitive_Pressure': driver_competition,
    'Driver_Customer_Demand': driver_customer_demand,
    'Driver_Management_Attitude': driver_management_attitude,
    
    # Section C: Constraints
    'Constraint_Access_Credit': fin_access_credit,
    'Constraint_Cost_Innovation': fin_cost_innovation,
    'Constraint_Internal_Capital': fin_internal_capital,
    'Constraint_Skilled_Employees': hc_skilled_employees,
    'Constraint_Training_Cost': hc_training_cost,
    'Constraint_Leadership_Capability': hc_leadership_capability,
    'Constraint_Electricity': infra_electricity,
    'Constraint_Internet_Quality': infra_internet_quality,
    'Constraint_Internet_Cost': infra_internet_cost,
    'Constraint_Logistics': infra_logistics,
    'Constraint_Regulatory_Burden': reg_burden,
    'Constraint_Corruption': reg_corruption,
    'Constraint_Govt_Support': reg_govt_support,
    'Constraint_Competition_Intensity': mkt_competition,
    'Constraint_Demand_Uncertainty': mkt_demand_uncertainty,
    'Constraint_International_Access': mkt_international_access,
    
    # Section D: Performance
    'Perf_Profitability_Growth': perf_profitability,
    'Perf_Sales_Growth': perf_sales,
    'Perf_Market_Share_Growth': perf_market_share,
    'Perf_ROI': perf_roi,
    'Perf_Overall_Satisfaction': perf_satisfaction,
    'Perf_Turnover_Growth_Pct': turnover_growth,
    'Perf_Profit_Margin_Pct': profit_margin,
    'Perf_Employee_Growth_Pct': employee_growth,
    'Perf_New_Branches_3yrs': new_branches,
    'Growth_Product_Lines': growth_product_lines,
    'Growth_Quality_Improvement': growth_quality,
    'Growth_Customer_Satisfaction': growth_customer_satisfaction,
    'Growth_Customer_Retention': growth_customer_retention,
    
    # Composite Indices
    'Index_Technology_Innovation': tech_index,
    'Index_Advanced_Technology': advanced_tech_index,
    'Index_Digital_Presence': digital_presence_index,
    'Index_Process_Innovation': process_innovation_index,
    'Index_Product_Innovation': product_innovation_index,
    'Index_Overall_Innovation': overall_innovation_index,
    'Index_Financial_Constraints': financial_constraint_index,
    'Index_Infrastructure_Constraints': infra_constraint_index,
    'Index_Overall_Constraints': overall_constraint_index,
    'Index_Overall_Performance': overall_performance_index
}

df = pd.DataFrame(data)

# ============================================================================
# SAVE OUTPUTS
# ============================================================================

print("\nSaving Dataset Files...")

# Save main dataset
df.to_csv('/workspace/nigerian_sme_innovation_dataset.csv', index=False)
print("✓ Saved: nigerian_sme_innovation_dataset.csv")

# Save Excel with multiple sheets
with pd.ExcelWriter('/workspace/nigerian_sme_innovation_dataset.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Full_Dataset', index=False)
    
    # Create separate sheets for each section
    firmographics_cols = ['Firm_ID', 'State', 'Geo_Political_Zone', 'Location_Type', 'Industry', 
                          'ISIC_Code', 'Firm_Age_Years', 'Num_Employees', 'Size_Category',
                          'Annual_Turnover_Naira', 'Legal_Structure', 'Owner_Age', 'Owner_Gender',
                          'Owner_Education', 'Owner_Field_of_Study', 'Owner_Prior_Experience_Years',
                          'Owner_Digital_Literacy_Score']
    df[firmographics_cols].to_excel(writer, sheet_name='A_Firmographics', index=False)
    
    innovation_cols = [col for col in df.columns if col.startswith(('Tech_', 'Digital_', 'Process_', 
                                                                     'Product_', 'Business_Model_', 'Driver_'))]
    df[['Firm_ID'] + innovation_cols].to_excel(writer, sheet_name='B_Innovation', index=False)
    
    constraint_cols = [col for col in df.columns if col.startswith('Constraint_')]
    df[['Firm_ID'] + constraint_cols].to_excel(writer, sheet_name='C_Constraints', index=False)
    
    performance_cols = [col for col in df.columns if col.startswith(('Perf_', 'Growth_'))]
    df[['Firm_ID'] + performance_cols].to_excel(writer, sheet_name='D_Performance', index=False)
    
    index_cols = [col for col in df.columns if col.startswith('Index_')]
    df[['Firm_ID'] + index_cols].to_excel(writer, sheet_name='E_Indices', index=False)

print("✓ Saved: nigerian_sme_innovation_dataset.xlsx (with 6 sheets)")

# Save JSON format
df.to_json('/workspace/nigerian_sme_innovation_dataset.json', orient='records', indent=2)
print("✓ Saved: nigerian_sme_innovation_dataset.json")

# ============================================================================
# GENERATE DATA DICTIONARY
# ============================================================================

print("\nGenerating Data Dictionary...")

data_dictionary = {
    'Dataset_Info': {
        'Title': 'Nigerian SME Innovation Adoption and Performance Dataset',
        'Research_Topic': 'Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs',
        'Sample_Size': N_SAMPLES,
        'Generation_Date': datetime.now().strftime('%Y-%m-%d'),
        'Data_Type': 'Synthetic/Simulated',
        'Purpose': 'Academic Research - Statistical Analysis and Machine Learning'
    },
    
    'Sections': {
        'A': 'Firmographics & Managerial Characteristics',
        'B': 'Innovation Adoption (Independent Variables)',
        'C': 'Constraint Assessment (Moderating Variables)',
        'D': 'Firm Performance and Growth (Dependent Variables)',
        'E': 'Composite Indices (Calculated)'
    },
    
    'Variables': {}
}

# Variable descriptions
var_descriptions = {
    'Firm_ID': 'Unique anonymized firm identifier',
    'State': 'Nigerian state where firm operates',
    'Geo_Political_Zone': 'Nigerian geo-political zone (South West, South East, South South, North Central, North East, North West)',
    'Location_Type': 'Urban or Rural location',
    'Industry': 'Industry sector classification',
    'ISIC_Code': 'International Standard Industrial Classification code',
    'Firm_Age_Years': 'Years of operation',
    'Num_Employees': 'Number of full-time employees',
    'Size_Category': 'Firm size: Micro (1-10), Small (11-50), Medium (51-200)',
    'Annual_Turnover_Naira': 'Annual revenue in Nigerian Naira',
    'Legal_Structure': 'Legal form of business',
    'Owner_Age': 'Age of primary owner/manager',
    'Owner_Gender': 'Gender of primary owner/manager',
    'Owner_Education': 'Highest educational level',
    'Owner_Field_of_Study': 'Academic field of study',
    'Owner_Prior_Experience_Years': 'Years of prior entrepreneurial experience',
    'Owner_Digital_Literacy_Score': 'Digital literacy score (1-10 scale)',
    
    # Innovation variables (Likert 1-5)
    'Tech_Computers': 'Extent of computer use (1=No use, 5=Extensive use)',
    'Tech_Accounting_Software': 'Use of accounting software (Likert 1-5)',
    'Tech_CRM': 'Use of Customer Relationship Management systems (Likert 1-5)',
    'Tech_Ecommerce_Platform': 'Use of e-commerce platforms (Likert 1-5)',
    'Tech_Cloud_Computing': 'Adoption of cloud computing (Likert 1-5)',
    'Tech_Social_Media_Business': 'Use of social media for business (Likert 1-5)',
    'Tech_AI_ML': 'Use of AI/ML for analytics (Likert 1-5)',
    'Tech_IoT': 'Use of Internet of Things in operations (Likert 1-5)',
    'Tech_Blockchain': 'Adoption of blockchain technology (Likert 1-5)',
    'Tech_Robotics': 'Use of robotics/automation (Likert 1-5)',
    'Digital_Website': 'Has functional business website (Likert 1-5)',
    'Digital_Social_Media_Presence': 'Active social media presence (Likert 1-5)',
    'Digital_Online_Payments': 'Accepts online payments (Likert 1-5)',
    'Process_New_Production_Methods': 'Adopted new production/delivery methods (Likert 1-5)',
    'Process_Supply_Chain_Software': 'Use of supply chain/logistics software (Likert 1-5)',
    'Process_Inventory_Management': 'Use of inventory management systems (Likert 1-5)',
    'Process_HR_Software': 'Use of HR management software (Likert 1-5)',
    'Product_New_Services_3yrs': 'Introduced new/improved products in last 3 years (Likert 1-5)',
    'Product_Improvements': 'Degree of product improvements (Likert 1-5)',
    'Product_Launch_Frequency': 'Frequency of new product launches (Likert 1-5)',
    'Business_Model_Revenue_Change': 'Changes in revenue model (Likert 1-5)',
    'Business_Model_Value_Proposition': 'Changes in value proposition (Likert 1-5)',
    'Business_Model_Customer_Engagement': 'Changes in customer engagement strategies (Likert 1-5)',
    'Driver_Competitive_Pressure': 'Perceived competitive pressure (Likert 1-5)',
    'Driver_Customer_Demand': 'Customer demand for innovation (Likert 1-5)',
    'Driver_Management_Attitude': 'Management attitude towards innovation (Likert 1-5)',
    
    # Constraints (Likert 1-5, higher = more constrained)
    'Constraint_Access_Credit': 'Difficulty accessing credit (Likert 1-5)',
    'Constraint_Cost_Innovation': 'High cost of innovation (Likert 1-5)',
    'Constraint_Internal_Capital': 'Sufficiency of internal capital (Likert 1-5, reverse coded)',
    'Constraint_Skilled_Employees': 'Difficulty finding skilled employees (Likert 1-5)',
    'Constraint_Training_Cost': 'High cost of training staff (Likert 1-5)',
    'Constraint_Leadership_Capability': 'Management capability for change (Likert 1-5, reverse coded)',
    'Constraint_Electricity': 'Poor electricity reliability (Likert 1-5)',
    'Constraint_Internet_Quality': 'Poor internet quality (Likert 1-5)',
    'Constraint_Internet_Cost': 'High internet cost (Likert 1-5)',
    'Constraint_Logistics': 'Poor logistics/transportation (Likert 1-5)',
    'Constraint_Regulatory_Burden': 'Heavy regulatory burden (Likert 1-5)',
    'Constraint_Corruption': 'Corruption and informal charges (Likert 1-5)',
    'Constraint_Govt_Support': 'Effectiveness of government support (Likert 1-5, reverse coded)',
    'Constraint_Competition_Intensity': 'Intensity of competition (Likert 1-5)',
    'Constraint_Demand_Uncertainty': 'Market demand uncertainty (Likert 1-5)',
    'Constraint_International_Access': 'Access to international markets (Likert 1-5, reverse coded)',
    
    # Performance (Likert 1-5 for subjective, % for objective)
    'Perf_Profitability_Growth': 'Profitability growth last 3 years (Likert 1-5)',
    'Perf_Sales_Growth': 'Sales growth last 3 years (Likert 1-5)',
    'Perf_Market_Share_Growth': 'Market share growth (Likert 1-5)',
    'Perf_ROI': 'Return on Investment perception (Likert 1-5)',
    'Perf_Overall_Satisfaction': 'Overall business performance satisfaction (Likert 1-5)',
    'Perf_Turnover_Growth_Pct': 'Actual turnover growth % (last 3 years, may have missing data)',
    'Perf_Profit_Margin_Pct': 'Actual profit margin % (may have missing data)',
    'Perf_Employee_Growth_Pct': 'Employee growth rate % (may have missing data)',
    'Perf_New_Branches_3yrs': 'Number of new branches opened (last 3 years)',
    'Growth_Product_Lines': 'Increase in product/service lines (Likert 1-5)',
    'Growth_Quality_Improvement': 'Product/service quality improvement (Likert 1-5)',
    'Growth_Customer_Satisfaction': 'Customer satisfaction improvement (Likert 1-5)',
    'Growth_Customer_Retention': 'Customer retention improvement (Likert 1-5)',
    
    # Indices (continuous, calculated as means)
    'Index_Technology_Innovation': 'Technology adoption index (mean of tech variables)',
    'Index_Advanced_Technology': 'Advanced technology index (AI, IoT, Blockchain, Robotics)',
    'Index_Digital_Presence': 'Digital presence index (website, social media, online payments)',
    'Index_Process_Innovation': 'Process innovation index',
    'Index_Product_Innovation': 'Product innovation index',
    'Index_Overall_Innovation': 'Overall innovation index (composite)',
    'Index_Financial_Constraints': 'Financial constraints index',
    'Index_Infrastructure_Constraints': 'Infrastructure constraints index',
    'Index_Overall_Constraints': 'Overall constraints index (composite)',
    'Index_Overall_Performance': 'Overall performance index (composite)'
}

for col in df.columns:
    data_dictionary['Variables'][col] = {
        'Description': var_descriptions.get(col, 'Variable description'),
        'Type': str(df[col].dtype),
        'Missing_Count': int(df[col].isna().sum()),
        'Missing_Percentage': round(df[col].isna().sum() / len(df) * 100, 2)
    }
    
    if df[col].dtype in ['int64', 'float64']:
        data_dictionary['Variables'][col]['Min'] = float(df[col].min()) if not df[col].isna().all() else None
        data_dictionary['Variables'][col]['Max'] = float(df[col].max()) if not df[col].isna().all() else None
        data_dictionary['Variables'][col]['Mean'] = float(df[col].mean()) if not df[col].isna().all() else None
        data_dictionary['Variables'][col]['Std'] = float(df[col].std()) if not df[col].isna().all() else None

with open('/workspace/data_dictionary.json', 'w') as f:
    json.dump(data_dictionary, f, indent=2)

print("✓ Saved: data_dictionary.json")

# ============================================================================
# GENERATE SUMMARY STATISTICS REPORT
# ============================================================================

print("\nGenerating Summary Statistics Report...")

summary_report = []

summary_report.append("=" * 80)
summary_report.append("NIGERIAN SME INNOVATION DATASET - SUMMARY REPORT")
summary_report.append("=" * 80)
summary_report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
summary_report.append(f"Sample Size: {N_SAMPLES} SMEs")
summary_report.append("\n" + "=" * 80)
summary_report.append("SECTION A: FIRMOGRAPHICS")
summary_report.append("=" * 80)

summary_report.append(f"\nGeo-Political Zones Distribution:")
summary_report.append(df['Geo_Political_Zone'].value_counts().to_string())

summary_report.append(f"\n\nTop 10 States:")
summary_report.append(df['State'].value_counts().head(10).to_string())

summary_report.append(f"\n\nLocation Type:")
summary_report.append(df['Location_Type'].value_counts().to_string())

summary_report.append(f"\n\nIndustry Distribution:")
summary_report.append(df['Industry'].value_counts().to_string())

summary_report.append(f"\n\nFirm Size Categories:")
summary_report.append(df['Size_Category'].value_counts().to_string())

summary_report.append(f"\n\nLegal Structure:")
summary_report.append(df['Legal_Structure'].value_counts().to_string())

summary_report.append(f"\n\nFirm Age Statistics:")
summary_report.append(df['Firm_Age_Years'].describe().to_string())

summary_report.append(f"\n\nOwner Education:")
summary_report.append(df['Owner_Education'].value_counts().to_string())

summary_report.append(f"\n\nOwner Gender:")
summary_report.append(df['Owner_Gender'].value_counts().to_string())

summary_report.append("\n\n" + "=" * 80)
summary_report.append("SECTION B: INNOVATION ADOPTION")
summary_report.append("=" * 80)

summary_report.append(f"\n\nInnovation Indices (Scale 1-5):")
summary_report.append(f"Overall Innovation Index: {df['Index_Overall_Innovation'].mean():.2f} ± {df['Index_Overall_Innovation'].std():.2f}")
summary_report.append(f"Technology Innovation Index: {df['Index_Technology_Innovation'].mean():.2f} ± {df['Index_Technology_Innovation'].std():.2f}")
summary_report.append(f"Process Innovation Index: {df['Index_Process_Innovation'].mean():.2f} ± {df['Index_Process_Innovation'].std():.2f}")
summary_report.append(f"Product Innovation Index: {df['Index_Product_Innovation'].mean():.2f} ± {df['Index_Product_Innovation'].std():.2f}")
summary_report.append(f"Digital Presence Index: {df['Index_Digital_Presence'].mean():.2f} ± {df['Index_Digital_Presence'].std():.2f}")
summary_report.append(f"Advanced Technology Index: {df['Index_Advanced_Technology'].mean():.2f} ± {df['Index_Advanced_Technology'].std():.2f}")

summary_report.append("\n\n" + "=" * 80)
summary_report.append("SECTION C: CONSTRAINTS")
summary_report.append("=" * 80)

summary_report.append(f"\n\nConstraint Indices (Scale 1-5, higher = more constrained):")
summary_report.append(f"Overall Constraints Index: {df['Index_Overall_Constraints'].mean():.2f} ± {df['Index_Overall_Constraints'].std():.2f}")
summary_report.append(f"Financial Constraints Index: {df['Index_Financial_Constraints'].mean():.2f} ± {df['Index_Financial_Constraints'].std():.2f}")
summary_report.append(f"Infrastructure Constraints Index: {df['Index_Infrastructure_Constraints'].mean():.2f} ± {df['Index_Infrastructure_Constraints'].std():.2f}")

summary_report.append(f"\n\nTop 5 Constraints (by mean severity):")
constraint_cols = [col for col in df.columns if col.startswith('Constraint_')]
constraint_means = df[constraint_cols].mean().sort_values(ascending=False)
summary_report.append(constraint_means.head().to_string())

summary_report.append("\n\n" + "=" * 80)
summary_report.append("SECTION D: PERFORMANCE")
summary_report.append("=" * 80)

summary_report.append(f"\n\nPerformance Indices (Scale 1-5):")
summary_report.append(f"Overall Performance Index: {df['Index_Overall_Performance'].mean():.2f} ± {df['Index_Overall_Performance'].std():.2f}")
summary_report.append(f"Profitability Growth: {df['Perf_Profitability_Growth'].mean():.2f} ± {df['Perf_Profitability_Growth'].std():.2f}")
summary_report.append(f"Sales Growth: {df['Perf_Sales_Growth'].mean():.2f} ± {df['Perf_Sales_Growth'].std():.2f}")
summary_report.append(f"ROI Perception: {df['Perf_ROI'].mean():.2f} ± {df['Perf_ROI'].std():.2f}")

summary_report.append(f"\n\nObjective Performance Metrics (with missing data):")
summary_report.append(f"Turnover Growth %: {df['Perf_Turnover_Growth_Pct'].mean():.2f} ± {df['Perf_Turnover_Growth_Pct'].std():.2f} (n={df['Perf_Turnover_Growth_Pct'].notna().sum()})")
summary_report.append(f"Profit Margin %: {df['Perf_Profit_Margin_Pct'].mean():.2f} ± {df['Perf_Profit_Margin_Pct'].std():.2f} (n={df['Perf_Profit_Margin_Pct'].notna().sum()})")
summary_report.append(f"Employee Growth %: {df['Perf_Employee_Growth_Pct'].mean():.2f} ± {df['Perf_Employee_Growth_Pct'].std():.2f} (n={df['Perf_Employee_Growth_Pct'].notna().sum()})")

summary_report.append("\n\n" + "=" * 80)
summary_report.append("KEY CORRELATIONS")
summary_report.append("=" * 80)

# Calculate key correlations
corr_innov_perf = df['Index_Overall_Innovation'].corr(df['Index_Overall_Performance'])
corr_const_perf = df['Index_Overall_Constraints'].corr(df['Index_Overall_Performance'])
corr_innov_const = df['Index_Overall_Innovation'].corr(df['Index_Overall_Constraints'])

summary_report.append(f"\n\nInnovation → Performance: r = {corr_innov_perf:.3f}")
summary_report.append(f"Constraints → Performance: r = {corr_const_perf:.3f}")
summary_report.append(f"Innovation → Constraints: r = {corr_innov_const:.3f}")

summary_report.append("\n\n" + "=" * 80)
summary_report.append("DATA QUALITY NOTES")
summary_report.append("=" * 80)

summary_report.append("\n- This is a SYNTHETIC dataset generated for research purposes")
summary_report.append("- Realistic correlations have been built in:")
summary_report.append("  * Higher innovation → better performance")
summary_report.append("  * Higher constraints → lower performance")
summary_report.append("  * Larger firms → more innovative")
summary_report.append("  * Urban location → more innovative")
summary_report.append("  * Higher education → higher digital literacy")
summary_report.append("  * Rural/Northern areas → more constraints")
summary_report.append("\n- Missing data patterns:")
summary_report.append(f"  * Turnover growth: {df['Perf_Turnover_Growth_Pct'].isna().sum()} missing ({df['Perf_Turnover_Growth_Pct'].isna().sum()/N_SAMPLES*100:.1f}%)")
summary_report.append(f"  * Profit margin: {df['Perf_Profit_Margin_Pct'].isna().sum()} missing ({df['Perf_Profit_Margin_Pct'].isna().sum()/N_SAMPLES*100:.1f}%)")
summary_report.append(f"  * Employee growth: {df['Perf_Employee_Growth_Pct'].isna().sum()} missing ({df['Perf_Employee_Growth_Pct'].isna().sum()/N_SAMPLES*100:.1f}%)")
summary_report.append(f"  * New branches: {df['Perf_New_Branches_3yrs'].isna().sum()} missing ({df['Perf_New_Branches_3yrs'].isna().sum()/N_SAMPLES*100:.1f}%)")

summary_report.append("\n\n" + "=" * 80)
summary_report.append("RECOMMENDED ANALYSES")
summary_report.append("=" * 80)

summary_report.append("\n1. Regression Analysis:")
summary_report.append("   - Dependent: Performance indices")
summary_report.append("   - Independent: Innovation indices")
summary_report.append("   - Moderators: Constraint indices")
summary_report.append("   - Controls: Firm age, size, location, industry")

summary_report.append("\n2. Machine Learning Models:")
summary_report.append("   - Classification: High vs Low performers")
summary_report.append("   - Regression: Predict performance scores")
summary_report.append("   - Clustering: Identify SME archetypes")
summary_report.append("   - Feature importance: Key innovation drivers")

summary_report.append("\n3. Structural Equation Modeling:")
summary_report.append("   - Test mediation and moderation effects")
summary_report.append("   - Validate composite indices")

summary_report.append("\n4. Comparative Analysis:")
summary_report.append("   - By firm size (Micro/Small/Medium)")
summary_report.append("   - By location (Urban/Rural)")
summary_report.append("   - By geo-political zone")
summary_report.append("   - By industry sector")

summary_report.append("\n\n" + "=" * 80)
summary_report.append("END OF REPORT")
summary_report.append("=" * 80)

report_text = "\n".join(summary_report)

with open('/workspace/summary_report.txt', 'w') as f:
    f.write(report_text)

print("✓ Saved: summary_report.txt")

# ============================================================================
# PRINT SUMMARY TO CONSOLE
# ============================================================================

print("\n" + "=" * 80)
print("DATASET GENERATION COMPLETE!")
print("=" * 80)
print("\nFiles Created:")
print("  1. nigerian_sme_innovation_dataset.csv (Main dataset)")
print("  2. nigerian_sme_innovation_dataset.xlsx (Excel with 6 sheets)")
print("  3. nigerian_sme_innovation_dataset.json (JSON format)")
print("  4. data_dictionary.json (Complete variable documentation)")
print("  5. summary_report.txt (Statistical summary)")

print(f"\nDataset Overview:")
print(f"  • Total Observations: {N_SAMPLES}")
print(f"  • Total Variables: {len(df.columns)}")
print(f"  • Firmographics: {len([c for c in df.columns if not c.startswith(('Tech_', 'Digital_', 'Process_', 'Product_', 'Business_', 'Driver_', 'Constraint_', 'Perf_', 'Growth_', 'Index_'))])}")
print(f"  • Innovation Variables: {len([c for c in df.columns if c.startswith(('Tech_', 'Digital_', 'Process_', 'Product_', 'Business_', 'Driver_'))])}")
print(f"  • Constraint Variables: {len([c for c in df.columns if c.startswith('Constraint_')])}")
print(f"  • Performance Variables: {len([c for c in df.columns if c.startswith(('Perf_', 'Growth_'))])}")
print(f"  • Composite Indices: {len([c for c in df.columns if c.startswith('Index_')])}")

print(f"\nKey Statistics:")
print(f"  • Innovation Index (mean): {df['Index_Overall_Innovation'].mean():.2f}/5.00")
print(f"  • Constraints Index (mean): {df['Index_Overall_Constraints'].mean():.2f}/5.00")
print(f"  • Performance Index (mean): {df['Index_Overall_Performance'].mean():.2f}/5.00")
print(f"  • Innovation-Performance Correlation: {corr_innov_perf:.3f}")

print("\n" + "=" * 80)
print("Ready for analysis! Don't hold nothing back! 🚀")
print("=" * 80)
