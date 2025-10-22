#!/usr/bin/env python3
"""
Nigerian SME Innovation Adoption and Constraints Dataset Generator
Research Topic: Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs: Implications for Performance and Growth

This script generates a comprehensive dataset with realistic patterns and correlations
based on Nigerian SME characteristics and innovation adoption patterns.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

class NigerianSMEDatasetGenerator:
    def __init__(self, n_firms=2000):
        self.n_firms = n_firms
        self.data = {}
        
        # Nigerian states and geopolitical zones
        self.states_zones = {
            'Abia': 'South-East', 'Anambra': 'South-East', 'Ebonyi': 'South-East', 
            'Enugu': 'South-East', 'Imo': 'South-East',
            'Akwa Ibom': 'South-South', 'Bayelsa': 'South-South', 'Cross River': 'South-South',
            'Delta': 'South-South', 'Edo': 'South-South', 'Rivers': 'South-South',
            'Lagos': 'South-West', 'Ogun': 'South-West', 'Ondo': 'South-West',
            'Osun': 'South-West', 'Oyo': 'South-West', 'Ekiti': 'South-West',
            'Abuja': 'North-Central', 'Benue': 'North-Central', 'Kogi': 'North-Central',
            'Kwara': 'North-Central', 'Nasarawa': 'North-Central', 'Niger': 'North-Central', 'Plateau': 'North-Central',
            'Adamawa': 'North-East', 'Bauchi': 'North-East', 'Borno': 'North-East',
            'Gombe': 'North-East', 'Taraba': 'North-East', 'Yobe': 'North-East',
            'Kaduna': 'North-West', 'Kano': 'North-West', 'Katsina': 'North-West',
            'Kebbi': 'North-West', 'Sokoto': 'North-West', 'Zamfara': 'North-West', 'Jigawa': 'North-West'
        }
        
        # Industry sectors with ISIC codes
        self.industries = {
            'Manufacturing': '10-33', 'Retail Trade': '47', 'Wholesale Trade': '46',
            'IT Services': '62-63', 'Agriculture': '01-03', 'Construction': '41-43',
            'Hospitality': '55-56', 'Transportation': '49-53', 'Financial Services': '64-66',
            'Professional Services': '70-75', 'Education': '85', 'Healthcare': '86-88',
            'Food & Beverage': '10-11', 'Textiles': '13-15', 'Mining': '05-09'
        }
        
        # Legal structures
        self.legal_structures = ['Sole Proprietorship', 'Partnership', 'Limited Liability Company', 'Cooperative']
        
        # Educational levels
        self.education_levels = ['Primary', 'Secondary', 'Diploma', 'Bachelor', 'Master', 'PhD']
        
        # Fields of study
        self.fields_of_study = [
            'Business Administration', 'Engineering', 'Computer Science', 'Economics',
            'Accounting', 'Marketing', 'Agriculture', 'Medicine', 'Law', 'Education',
            'No Formal Education', 'Other'
        ]

    def generate_firmographics(self):
        """Generate Section A: Firmographics & Managerial Characteristics"""
        print("Generating firmographics data...")
        
        # Firm ID
        self.data['firm_id'] = [f'NG_SME_{i+1:04d}' for i in range(self.n_firms)]
        
        # Location
        states = list(self.states_zones.keys())
        self.data['state'] = np.random.choice(states, self.n_firms)
        self.data['geo_political_zone'] = [self.states_zones[state] for state in self.data['state']]
        
        # Urban/Rural distribution (bias towards urban for SMEs)
        urban_prob = 0.7
        self.data['location_type'] = np.random.choice(['Urban', 'Rural'], self.n_firms, p=[urban_prob, 1-urban_prob])
        
        # Industry distribution
        industry_weights = [0.15, 0.12, 0.10, 0.08, 0.12, 0.08, 0.06, 0.05, 0.04, 0.05, 0.03, 0.02, 0.05, 0.03, 0.02]
        self.data['industry'] = np.random.choice(list(self.industries.keys()), self.n_firms, p=industry_weights)
        self.data['isic_code'] = [self.industries[ind] for ind in self.data['industry']]
        
        # Firm age (years of operation) - realistic distribution
        # Most SMEs are relatively young
        age_weights = [0.25, 0.20, 0.15, 0.12, 0.10, 0.08, 0.05, 0.03, 0.02]
        age_ranges = ['0-2', '3-5', '6-10', '11-15', '16-20', '21-25', '26-30', '31-40', '40+']
        self.data['firm_age_category'] = np.random.choice(age_ranges, self.n_firms, p=age_weights)
        
        # Convert to actual years for analysis
        age_mapping = {'0-2': 1.5, '3-5': 4, '6-10': 8, '11-15': 13, '16-20': 18, 
                      '21-25': 23, '26-30': 28, '31-40': 35, '40+': 45}
        self.data['firm_age_years'] = np.array([age_mapping[cat] for cat in self.data['firm_age_category']])
        
        # Firm size (employees) - realistic distribution
        # Most SMEs are small
        size_weights = [0.40, 0.30, 0.20, 0.08, 0.02]
        size_categories = ['1-5', '6-10', '11-25', '26-50', '50+']
        self.data['employee_size_category'] = np.random.choice(size_categories, self.n_firms, p=size_weights)
        
        # Convert to actual numbers
        size_mapping = {'1-5': 3, '6-10': 8, '11-25': 18, '26-50': 38, '50+': 75}
        self.data['num_employees'] = np.array([size_mapping[cat] for cat in self.data['employee_size_category']])
        
        # Annual turnover (in Naira) - correlated with size
        turnover_base = np.random.lognormal(12, 1.5, self.n_firms)  # Base turnover
        size_multipliers = [1, 2, 5, 15, 50]
        size_indices = np.random.choice(5, self.n_firms, p=size_weights)
        size_multiplier = np.array([size_multipliers[i] for i in size_indices])
        self.data['annual_turnover_ngn'] = turnover_base * size_multiplier
        
        # Legal structure
        legal_weights = [0.45, 0.15, 0.35, 0.05]  # Most are sole proprietorship or LLC
        self.data['legal_structure'] = np.random.choice(self.legal_structures, self.n_firms, p=legal_weights)
        
        # Owner/Manager Profile
        self.data['owner_age'] = np.clip(np.random.normal(42, 12, self.n_firms).astype(int), 25, 70)
        
        # Gender distribution
        self.data['owner_gender'] = np.random.choice(['Male', 'Female'], self.n_firms, p=[0.65, 0.35])
        
        # Education level
        edu_weights = [0.05, 0.15, 0.20, 0.35, 0.20, 0.05]
        self.data['owner_education'] = np.random.choice(self.education_levels, self.n_firms, p=edu_weights)
        
        # Field of study
        field_weights = [0.20, 0.15, 0.10, 0.10, 0.10, 0.08, 0.05, 0.03, 0.02, 0.02, 0.10, 0.05]
        self.data['owner_field_of_study'] = np.random.choice(self.fields_of_study, self.n_firms, p=field_weights)
        
        # Prior entrepreneurial experience (years)
        self.data['prior_entrepreneurial_experience'] = np.clip(np.random.exponential(3, self.n_firms), 0, 20)
        
        # Digital literacy score (1-10)
        # Correlated with education and age
        base_literacy = np.random.normal(6, 2, self.n_firms)
        edu_bonuses = [0, 0, 1, 2, 3, 4]
        edu_indices = [self.education_levels.index(edu) for edu in self.data['owner_education']]
        edu_bonus = np.array([edu_bonuses[i] for i in edu_indices])
        age_penalty = (self.data['owner_age'] - 30) * 0.02  # Slight penalty for older age
        self.data['digital_literacy_score'] = np.clip(base_literacy + edu_bonus - age_penalty, 1, 10)

    def generate_innovation_adoption(self):
        """Generate Section B: Innovation Adoption (Independent Variables)"""
        print("Generating innovation adoption data...")
        
        # Create innovation scores that are correlated with firm characteristics
        base_innovation = np.random.normal(3, 1, self.n_firms)
        
        # Technological Innovation
        tech_innovation = base_innovation.copy()
        
        # Digital Tools Adoption (1-5 scale)
        digital_tools = tech_innovation + np.random.normal(0, 0.5, self.n_firms)
        digital_tools += (self.data['digital_literacy_score'] - 5) * 0.3  # Correlated with digital literacy
        digital_tools += (self.data['firm_age_years'] - 10) * 0.02  # Slightly higher for older firms
        self.data['digital_tools_adoption'] = np.clip(digital_tools, 1, 5)
        
        # Advanced Tech Adoption (1-5 scale)
        advanced_tech = tech_innovation + np.random.normal(0, 0.7, self.n_firms)
        advanced_tech += (self.data['annual_turnover_ngn'] / 1000000) * 0.1  # Higher for larger firms
        advanced_tech += np.array([1 if edu == 'Master' else 0 for edu in self.data['owner_education']]) * 0.5
        advanced_tech += np.array([1 if edu == 'PhD' else 0 for edu in self.data['owner_education']]) * 0.8
        self.data['advanced_tech_adoption'] = np.clip(advanced_tech, 1, 5)
        
        # Level of Digitization (1-5 scale)
        digitization = tech_innovation + np.random.normal(0, 0.6, self.n_firms)
        digitization += (self.data['digital_literacy_score'] - 5) * 0.4
        digitization += np.array([1 if loc == 'Urban' else 0 for loc in self.data['location_type']]) * 0.3
        self.data['level_of_digitization'] = np.clip(digitization, 1, 5)
        
        # Process Innovation (1-5 scale)
        process_innovation = base_innovation + np.random.normal(0, 0.6, self.n_firms)
        process_innovation += np.array([1 if emp > 10 else 0 for emp in self.data['num_employees']]) * 0.4  # Larger firms more likely
        process_innovation += np.array([1 if ind == 'Manufacturing' else 0 for ind in self.data['industry']]) * 0.3
        self.data['process_innovation'] = np.clip(process_innovation, 1, 5)
        
        # Product/Service Innovation (1-5 scale)
        product_innovation = base_innovation + np.random.normal(0, 0.7, self.n_firms)
        product_innovation += np.array([1 if ind == 'IT Services' else 0 for ind in self.data['industry']]) * 0.5
        product_innovation += np.array([1 if ind == 'Manufacturing' else 0 for ind in self.data['industry']]) * 0.3
        product_innovation += np.array([1 if age < 5 else 0 for age in self.data['firm_age_years']]) * 0.2  # Newer firms more innovative
        self.data['product_service_innovation'] = np.clip(product_innovation, 1, 5)
        
        # Business Model Innovation (1-5 scale)
        business_model_innovation = base_innovation + np.random.normal(0, 0.8, self.n_firms)
        business_model_innovation += np.array([1 if ind == 'IT Services' else 0 for ind in self.data['industry']]) * 0.6
        business_model_innovation += np.array([1 if ind == 'Retail Trade' else 0 for ind in self.data['industry']]) * 0.3
        self.data['business_model_innovation'] = np.clip(business_model_innovation, 1, 5)
        
        # Innovation Drivers
        # Competitive pressure (1-5 scale)
        competitive_pressure = np.random.normal(3.5, 1, self.n_firms)
        competitive_pressure += np.array([1 if ind == 'Retail Trade' else 0 for ind in self.data['industry']]) * 0.5
        competitive_pressure += np.array([1 if ind == 'IT Services' else 0 for ind in self.data['industry']]) * 0.3
        self.data['competitive_pressure'] = np.clip(competitive_pressure, 1, 5)
        
        # Customer demand for innovation (1-5 scale)
        customer_demand = np.random.normal(3.2, 1, self.n_firms)
        customer_demand += np.array([1 if ind == 'IT Services' else 0 for ind in self.data['industry']]) * 0.6
        customer_demand += np.array([1 if loc == 'Urban' else 0 for loc in self.data['location_type']]) * 0.3
        self.data['customer_demand_innovation'] = np.clip(customer_demand, 1, 5)
        
        # Top management attitude (1-5 scale)
        mgmt_attitude = base_innovation + np.random.normal(0, 0.8, self.n_firms)
        mgmt_attitude += np.array([1 if edu == 'Master' else 0 for edu in self.data['owner_education']]) * 0.4
        mgmt_attitude += np.array([1 if edu == 'PhD' else 0 for edu in self.data['owner_education']]) * 0.6
        mgmt_attitude += np.array([1 if age < 40 else 0 for age in self.data['owner_age']]) * 0.2
        self.data['mgmt_attitude_innovation'] = np.clip(mgmt_attitude, 1, 5)

    def generate_constraints(self):
        """Generate Section C: Constraint Assessment (Moderating Variables)"""
        print("Generating constraint assessment data...")
        
        # Financial Constraints (1-5 scale, higher = more constrained)
        financial_constraints = np.random.normal(3.5, 1, self.n_firms)
        financial_constraints += np.array([1 if turnover < 5000000 else 0 for turnover in self.data['annual_turnover_ngn']]) * 0.5  # Smaller firms more constrained
        financial_constraints += np.array([1 if legal == 'Sole Proprietorship' else 0 for legal in self.data['legal_structure']]) * 0.3
        self.data['financial_constraints'] = np.clip(financial_constraints, 1, 5)
        
        # Access to credit (1-5 scale, higher = better access)
        credit_access = np.random.normal(2.8, 1, self.n_firms)
        credit_access += np.array([1 if turnover > 10000000 else 0 for turnover in self.data['annual_turnover_ngn']]) * 0.8  # Larger firms better access
        credit_access += np.array([1 if legal == 'Limited Liability Company' else 0 for legal in self.data['legal_structure']]) * 0.5
        credit_access += np.array([1 if loc == 'Urban' else 0 for loc in self.data['location_type']]) * 0.3
        self.data['access_to_credit'] = np.clip(credit_access, 1, 5)
        
        # Cost of innovation (1-5 scale, higher = more expensive)
        innovation_cost = np.random.normal(3.2, 0.8, self.n_firms)
        innovation_cost += np.array([1 if ind == 'IT Services' else 0 for ind in self.data['industry']]) * 0.3
        innovation_cost += np.array([1 if loc == 'Rural' else 0 for loc in self.data['location_type']]) * 0.2
        self.data['cost_of_innovation'] = np.clip(innovation_cost, 1, 5)
        
        # Sufficiency of internal capital (1-5 scale, higher = more sufficient)
        internal_capital = np.random.normal(2.5, 1, self.n_firms)
        internal_capital += np.array([1 if turnover > 5000000 else 0 for turnover in self.data['annual_turnover_ngn']]) * 0.6
        internal_capital += np.array([1 if age > 5 else 0 for age in self.data['firm_age_years']]) * 0.3
        self.data['sufficiency_internal_capital'] = np.clip(internal_capital, 1, 5)
        
        # Human Capital Constraints (1-5 scale, higher = more constrained)
        human_capital_constraints = np.random.normal(3.3, 1, self.n_firms)
        human_capital_constraints += np.array([1 if loc == 'Rural' else 0 for loc in self.data['location_type']]) * 0.4
        human_capital_constraints += np.array([1 if ind == 'IT Services' else 0 for ind in self.data['industry']]) * 0.5
        human_capital_constraints += np.array([1 if turnover < 2000000 else 0 for turnover in self.data['annual_turnover_ngn']]) * 0.3
        self.data['human_capital_constraints'] = np.clip(human_capital_constraints, 1, 5)
        
        # Difficulty finding skilled employees (1-5 scale, higher = more difficult)
        skilled_employee_difficulty = np.random.normal(3.6, 1, self.n_firms)
        skilled_employee_difficulty += np.array([1 if loc == 'Rural' else 0 for loc in self.data['location_type']]) * 0.5
        skilled_employee_difficulty += np.array([1 if ind == 'IT Services' else 0 for ind in self.data['industry']]) * 0.4
        self.data['skilled_employee_difficulty'] = np.clip(skilled_employee_difficulty, 1, 5)
        
        # Cost of training staff (1-5 scale, higher = more expensive)
        training_cost = np.random.normal(3.4, 0.9, self.n_firms)
        training_cost += np.array([1 if ind == 'IT Services' else 0 for ind in self.data['industry']]) * 0.3
        training_cost += np.array([1 if loc == 'Rural' else 0 for loc in self.data['location_type']]) * 0.2
        self.data['cost_of_training'] = np.clip(training_cost, 1, 5)
        
        # Management capability for change (1-5 scale, higher = better capability)
        mgmt_capability = np.random.normal(3.2, 1, self.n_firms)
        mgmt_capability += np.array([1 if edu == 'Master' else 0 for edu in self.data['owner_education']]) * 0.4
        mgmt_capability += np.array([1 if edu == 'PhD' else 0 for edu in self.data['owner_education']]) * 0.6
        mgmt_capability += np.array([1 if exp > 5 else 0 for exp in self.data['prior_entrepreneurial_experience']]) * 0.3
        self.data['mgmt_capability_change'] = np.clip(mgmt_capability, 1, 5)
        
        # Infrastructural Constraints (1-5 scale, higher = more constrained)
        infrastructure_constraints = np.random.normal(3.8, 1, self.n_firms)
        infrastructure_constraints += np.array([1 if loc == 'Rural' else 0 for loc in self.data['location_type']]) * 0.6
        infrastructure_constraints += np.array([1 if zone == 'North-East' else 0 for zone in self.data['geo_political_zone']]) * 0.3
        infrastructure_constraints += np.array([1 if zone == 'North-West' else 0 for zone in self.data['geo_political_zone']]) * 0.2
        self.data['infrastructure_constraints'] = np.clip(infrastructure_constraints, 1, 5)
        
        # Electricity reliability (1-5 scale, higher = more reliable)
        electricity_reliability = np.random.normal(2.5, 1, self.n_firms)
        electricity_reliability += np.array([1 if loc == 'Urban' else 0 for loc in self.data['location_type']]) * 0.5
        electricity_reliability += np.array([1 if state == 'Lagos' else 0 for state in self.data['state']]) * 0.3
        self.data['electricity_reliability'] = np.clip(electricity_reliability, 1, 5)
        
        # Internet connectivity quality (1-5 scale, higher = better)
        internet_quality = np.random.normal(2.8, 1, self.n_firms)
        internet_quality += np.array([1 if loc == 'Urban' else 0 for loc in self.data['location_type']]) * 0.6
        internet_quality += np.array([1 if state == 'Lagos' else 0 for state in self.data['state']]) * 0.4
        internet_quality += np.array([1 if state == 'Abuja' else 0 for state in self.data['state']]) * 0.3
        self.data['internet_quality'] = np.clip(internet_quality, 1, 5)
        
        # Internet cost (1-5 scale, higher = more expensive)
        internet_cost = np.random.normal(3.2, 0.8, self.n_firms)
        internet_cost += np.array([1 if loc == 'Rural' else 0 for loc in self.data['location_type']]) * 0.3
        self.data['internet_cost'] = np.clip(internet_cost, 1, 5)
        
        # Logistics and transportation access (1-5 scale, higher = better access)
        logistics_access = np.random.normal(3.0, 1, self.n_firms)
        logistics_access += np.array([1 if loc == 'Urban' else 0 for loc in self.data['location_type']]) * 0.5
        logistics_access += np.array([1 if state == 'Lagos' else 0 for state in self.data['state']]) * 0.4
        self.data['logistics_access'] = np.clip(logistics_access, 1, 5)
        
        # Regulatory and Institutional Constraints (1-5 scale, higher = more constrained)
        regulatory_constraints = np.random.normal(3.6, 1, self.n_firms)
        regulatory_constraints += np.array([1 if legal == 'Limited Liability Company' else 0 for legal in self.data['legal_structure']]) * 0.3
        regulatory_constraints += np.array([1 if turnover > 10000000 else 0 for turnover in self.data['annual_turnover_ngn']]) * 0.2
        self.data['regulatory_constraints'] = np.clip(regulatory_constraints, 1, 5)
        
        # Government regulation burden (1-5 scale, higher = more burden)
        regulation_burden = np.random.normal(3.4, 1, self.n_firms)
        regulation_burden += np.array([1 if legal == 'Limited Liability Company' else 0 for legal in self.data['legal_structure']]) * 0.4
        self.data['regulation_burden'] = np.clip(regulation_burden, 1, 5)
        
        # Corruption and informal charges (1-5 scale, higher = more corruption)
        corruption_level = np.random.normal(3.2, 1, self.n_firms)
        corruption_level += np.array([1 if loc == 'Rural' else 0 for loc in self.data['location_type']]) * 0.2
        self.data['corruption_level'] = np.clip(corruption_level, 1, 5)
        
        # Government support effectiveness (1-5 scale, higher = more effective)
        gov_support_effectiveness = np.random.normal(2.8, 1, self.n_firms)
        gov_support_effectiveness += np.array([1 if loc == 'Urban' else 0 for loc in self.data['location_type']]) * 0.3
        self.data['gov_support_effectiveness'] = np.clip(gov_support_effectiveness, 1, 5)
        
        # Market Constraints (1-5 scale, higher = more constrained)
        market_constraints = np.random.normal(3.3, 1, self.n_firms)
        market_constraints += np.array([1 if ind == 'Manufacturing' else 0 for ind in self.data['industry']]) * 0.3
        market_constraints += np.array([1 if loc == 'Rural' else 0 for loc in self.data['location_type']]) * 0.2
        self.data['market_constraints'] = np.clip(market_constraints, 1, 5)
        
        # Competition intensity (1-5 scale, higher = more intense)
        competition_intensity = np.random.normal(3.5, 1, self.n_firms)
        competition_intensity += np.array([1 if ind == 'Retail Trade' else 0 for ind in self.data['industry']]) * 0.4
        competition_intensity += np.array([1 if ind == 'IT Services' else 0 for ind in self.data['industry']]) * 0.3
        competition_intensity += np.array([1 if loc == 'Urban' else 0 for loc in self.data['location_type']]) * 0.2
        self.data['competition_intensity'] = np.clip(competition_intensity, 1, 5)
        
        # Demand uncertainty (1-5 scale, higher = more uncertain)
        demand_uncertainty = np.random.normal(3.2, 1, self.n_firms)
        demand_uncertainty += np.array([1 if ind == 'Agriculture' else 0 for ind in self.data['industry']]) * 0.4
        demand_uncertainty += np.array([1 if age < 3 else 0 for age in self.data['firm_age_years']]) * 0.3
        self.data['demand_uncertainty'] = np.clip(demand_uncertainty, 1, 5)
        
        # International market access (1-5 scale, higher = better access)
        intl_market_access = np.random.normal(2.5, 1, self.n_firms)
        intl_market_access += np.array([1 if turnover > 20000000 else 0 for turnover in self.data['annual_turnover_ngn']]) * 0.8
        intl_market_access += np.array([1 if ind == 'Manufacturing' else 0 for ind in self.data['industry']]) * 0.4
        intl_market_access += np.array([1 if loc == 'Urban' else 0 for loc in self.data['location_type']]) * 0.3
        self.data['intl_market_access'] = np.clip(intl_market_access, 1, 5)

    def generate_performance_metrics(self):
        """Generate Section D: Firm Performance and Growth (Dependent Variables)"""
        print("Generating performance metrics...")
        
        # Create base performance that correlates with innovation and constraints
        base_performance = np.random.normal(3.2, 1, self.n_firms)
        
        # Innovation impact on performance
        innovation_impact = (
            self.data['digital_tools_adoption'] * 0.3 +
            self.data['process_innovation'] * 0.25 +
            self.data['product_service_innovation'] * 0.35 +
            self.data['business_model_innovation'] * 0.2
        ) / 4
        
        # Constraint impact on performance (negative)
        constraint_impact = (
            self.data['financial_constraints'] * -0.2 +
            self.data['human_capital_constraints'] * -0.15 +
            self.data['infrastructure_constraints'] * -0.25 +
            self.data['regulatory_constraints'] * -0.1 +
            self.data['market_constraints'] * -0.15
        ) / 5
        
        # Size and age impact
        size_impact = np.log(self.data['num_employees']) * 0.1
        age_impact = np.log(self.data['firm_age_years']) * 0.05
        
        # Calculate final performance scores
        performance_score = base_performance + innovation_impact + constraint_impact + size_impact + age_impact
        
        # Subjective Performance (1-5 scale)
        self.data['profitability_growth'] = np.clip(performance_score + np.random.normal(0, 0.5, self.n_firms), 1, 5)
        self.data['sales_growth'] = np.clip(performance_score + np.random.normal(0, 0.4, self.n_firms), 1, 5)
        self.data['market_share_growth'] = np.clip(performance_score + np.random.normal(0, 0.6, self.n_firms), 1, 5)
        self.data['roi_satisfaction'] = np.clip(performance_score + np.random.normal(0, 0.5, self.n_firms), 1, 5)
        self.data['overall_performance_satisfaction'] = np.clip(performance_score + np.random.normal(0, 0.3, self.n_firms), 1, 5)
        
        # Objective Performance (ranges for sensitivity)
        # Annual turnover growth rate (%)
        turnover_growth = np.random.normal(15, 25, self.n_firms)  # Base growth
        turnover_growth += innovation_impact * 5  # Innovation boost
        turnover_growth += constraint_impact * 3  # Constraint penalty
        turnover_growth = np.clip(turnover_growth, -30, 100)
        
        # Convert to ranges
        turnover_growth_ranges = []
        for growth in turnover_growth:
            if growth < -10:
                turnover_growth_ranges.append('Declining (>-10%)')
            elif growth < 0:
                turnover_growth_ranges.append('Declining (0 to -10%)')
            elif growth < 10:
                turnover_growth_ranges.append('Slow Growth (0-10%)')
            elif growth < 25:
                turnover_growth_ranges.append('Moderate Growth (10-25%)')
            elif growth < 50:
                turnover_growth_ranges.append('Strong Growth (25-50%)')
            else:
                turnover_growth_ranges.append('Rapid Growth (>50%)')
        
        self.data['turnover_growth_range'] = turnover_growth_ranges
        self.data['turnover_growth_percent'] = turnover_growth
        
        # Profit growth rate (%)
        profit_growth = turnover_growth + np.random.normal(-5, 10, self.n_firms)
        profit_growth = np.clip(profit_growth, -50, 80)
        self.data['profit_growth_percent'] = profit_growth
        
        # Employee growth rate (%)
        employee_growth = np.random.normal(8, 20, self.n_firms)
        employee_growth += innovation_impact * 3
        employee_growth += constraint_impact * 2
        employee_growth = np.clip(employee_growth, -20, 60)
        self.data['employee_growth_percent'] = employee_growth
        
        # Number of new branches/clients (last 3 years)
        new_branches = np.random.poisson(0.5, self.n_firms)
        new_branches += (performance_score > 3.5).astype(int) * np.random.poisson(0.3, self.n_firms)
        self.data['new_branches_3years'] = new_branches
        
        new_clients = np.random.poisson(15, self.n_firms)
        new_clients += (performance_score > 3.5).astype(int) * np.random.poisson(10, self.n_firms)
        self.data['new_clients_3years'] = new_clients
        
        # Non-Financial Growth Indicators (1-5 scale)
        self.data['product_service_lines_increase'] = np.clip(performance_score + np.random.normal(0, 0.4, self.n_firms), 1, 5)
        self.data['quality_improvement'] = np.clip(performance_score + np.random.normal(0, 0.3, self.n_firms), 1, 5)
        self.data['customer_satisfaction_improvement'] = np.clip(performance_score + np.random.normal(0, 0.4, self.n_firms), 1, 5)
        self.data['customer_retention_improvement'] = np.clip(performance_score + np.random.normal(0, 0.3, self.n_firms), 1, 5)

    def generate_dataset(self):
        """Generate the complete dataset"""
        print(f"Generating Nigerian SME Innovation Dataset with {self.n_firms} firms...")
        
        self.generate_firmographics()
        self.generate_innovation_adoption()
        self.generate_constraints()
        self.generate_performance_metrics()
        
        # Create DataFrame
        df = pd.DataFrame(self.data)
        
        # Add some additional derived variables
        df['innovation_index'] = (
            df['digital_tools_adoption'] + df['process_innovation'] + 
            df['product_service_innovation'] + df['business_model_innovation']
        ) / 4
        
        df['constraint_index'] = (
            df['financial_constraints'] + df['human_capital_constraints'] + 
            df['infrastructure_constraints'] + df['regulatory_constraints'] + 
            df['market_constraints']
        ) / 5
        
        df['performance_index'] = (
            df['profitability_growth'] + df['sales_growth'] + 
            df['market_share_growth'] + df['overall_performance_satisfaction']
        ) / 4
        
        return df

    def save_dataset(self, df, base_filename='nigerian_sme_innovation_dataset'):
        """Save dataset in multiple formats"""
        print("Saving dataset...")
        
        # Save as CSV
        csv_filename = f"{base_filename}.csv"
        df.to_csv(csv_filename, index=False)
        print(f"Saved as CSV: {csv_filename}")
        
        # Save as Excel with multiple sheets
        excel_filename = f"{base_filename}.xlsx"
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Complete_Dataset', index=False)
            
            # Create summary sheets
            summary_stats = df.describe()
            summary_stats.to_excel(writer, sheet_name='Summary_Statistics')
            
            # Innovation variables only
            innovation_cols = [col for col in df.columns if 'innovation' in col.lower() or 'adoption' in col.lower() or 'digital' in col.lower()]
            df[innovation_cols].to_excel(writer, sheet_name='Innovation_Variables', index=False)
            
            # Constraint variables only
            constraint_cols = [col for col in df.columns if 'constraint' in col.lower() or 'access' in col.lower() or 'difficulty' in col.lower()]
            df[constraint_cols].to_excel(writer, sheet_name='Constraint_Variables', index=False)
            
            # Performance variables only
            performance_cols = [col for col in df.columns if 'growth' in col.lower() or 'performance' in col.lower() or 'satisfaction' in col.lower()]
            df[performance_cols].to_excel(writer, sheet_name='Performance_Variables', index=False)
        
        print(f"Saved as Excel: {excel_filename}")
        
        # Save as JSON
        json_filename = f"{base_filename}.json"
        df.to_json(json_filename, orient='records', indent=2)
        print(f"Saved as JSON: {json_filename}")
        
        return csv_filename, excel_filename, json_filename

def main():
    """Main function to generate the dataset"""
    print("="*80)
    print("NIGERIAN SME INNOVATION ADOPTION AND CONSTRAINTS DATASET GENERATOR")
    print("Research Topic: Leveraging Machine Learning to Examine Innovation Adoption")
    print("and Constraints in Nigerian SMEs: Implications for Performance and Growth")
    print("="*80)
    
    # Generate dataset
    generator = NigerianSMEDatasetGenerator(n_firms=2000)
    df = generator.generate_dataset()
    
    # Save dataset
    csv_file, excel_file, json_file = generator.save_dataset(df)
    
    # Print summary
    print("\n" + "="*80)
    print("DATASET GENERATION COMPLETE")
    print("="*80)
    print(f"Total firms: {len(df)}")
    print(f"Total variables: {len(df.columns)}")
    print(f"Files created:")
    print(f"  - {csv_file}")
    print(f"  - {excel_file}")
    print(f"  - {json_file}")
    
    print("\nDataset Overview:")
    print(f"Firmographics: {len([col for col in df.columns if col in ['firm_id', 'state', 'industry', 'firm_age_years', 'num_employees', 'owner_age', 'owner_gender', 'owner_education']])} variables")
    print(f"Innovation Variables: {len([col for col in df.columns if 'innovation' in col.lower() or 'adoption' in col.lower() or 'digital' in col.lower()])} variables")
    print(f"Constraint Variables: {len([col for col in df.columns if 'constraint' in col.lower() or 'access' in col.lower() or 'difficulty' in col.lower()])} variables")
    print(f"Performance Variables: {len([col for col in df.columns if 'growth' in col.lower() or 'performance' in col.lower() or 'satisfaction' in col.lower()])} variables")
    
    print("\nSample of first 5 rows:")
    print(df.head())
    
    return df

if __name__ == "__main__":
    df = main()