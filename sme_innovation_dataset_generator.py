#!/usr/bin/env python3
"""
SME Innovation Dataset Generator
Generates a comprehensive dataset for analyzing innovation adoption and constraints in Nigerian SMEs
Based on the research topic: "Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs: Implications for Performance and Growth"

Author: AI Assistant
Date: 2025-10-22
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

class SMEInnovationDatasetGenerator:
    def __init__(self, n_samples: int = 2000):
        """
        Initialize the dataset generator
        
        Args:
            n_samples: Number of SME records to generate
        """
        self.n_samples = n_samples
        self.data = {}
        
        # Nigerian states and geo-political zones
        self.nigerian_states = {
            'North Central': ['Abuja', 'Benue', 'Kogi', 'Kwara', 'Nasarawa', 'Niger', 'Plateau'],
            'North East': ['Adamawa', 'Bauchi', 'Borno', 'Gombe', 'Taraba', 'Yobe'],
            'North West': ['Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Sokoto', 'Zamfara'],
            'South East': ['Abia', 'Anambra', 'Ebonyi', 'Enugu', 'Imo'],
            'South South': ['Akwa Ibom', 'Bayelsa', 'Cross River', 'Delta', 'Edo', 'Rivers'],
            'South West': ['Ekiti', 'Lagos', 'Ogun', 'Ondo', 'Osun', 'Oyo']
        }
        
        # Industry sectors with ISIC codes
        self.industries = {
            'A01': 'Agriculture, Forestry and Fishing',
            'C10': 'Food Products Manufacturing',
            'C13': 'Textiles Manufacturing',
            'C20': 'Chemical Products Manufacturing',
            'C25': 'Metal Products Manufacturing',
            'F41': 'Construction',
            'G47': 'Retail Trade',
            'H49': 'Transportation and Storage',
            'I55': 'Accommodation Services',
            'I56': 'Food and Beverage Services',
            'J58': 'Publishing Activities',
            'J62': 'IT Services',
            'K64': 'Financial Services',
            'M69': 'Professional Services',
            'M73': 'Advertising and Market Research',
            'N77': 'Rental and Leasing',
            'P85': 'Education Services',
            'Q86': 'Health Services',
            'R93': 'Sports and Recreation'
        }
        
        # Educational levels
        self.education_levels = [
            'No Formal Education', 'Primary Education', 'Secondary Education',
            'OND/NCE', 'HND/Bachelor', 'Master', 'PhD'
        ]
        
        # Fields of study
        self.fields_of_study = [
            'Business/Management', 'Engineering', 'Computer Science/IT', 'Economics/Finance',
            'Agriculture', 'Medicine/Health', 'Education', 'Arts/Humanities', 'Law',
            'Sciences', 'Social Sciences', 'Other'
        ]
        
    def generate_firmographics(self) -> Dict:
        """Generate Section A: Firmographics & Managerial Characteristics"""
        
        data = {}
        
        # Firm ID (Anonymized)
        data['firm_id'] = [f"SME_{str(i).zfill(4)}" for i in range(1, self.n_samples + 1)]
        
        # Location data
        states = []
        geo_zones = []
        urban_rural = []
        
        for _ in range(self.n_samples):
            zone = np.random.choice(list(self.nigerian_states.keys()), 
                                  p=[0.15, 0.10, 0.20, 0.15, 0.15, 0.25])  # Lagos/SW bias
            state = np.random.choice(self.nigerian_states[zone])
            
            # Urban/Rural distribution (more urban in SW, SS; more rural in North)
            if zone in ['South West', 'South South']:
                urban_prob = 0.75
            elif zone in ['South East', 'North Central']:
                urban_prob = 0.60
            else:
                urban_prob = 0.40
                
            location_type = np.random.choice(['Urban', 'Rural'], p=[urban_prob, 1-urban_prob])
            
            states.append(state)
            geo_zones.append(zone)
            urban_rural.append(location_type)
        
        data['state'] = states
        data['geo_political_zone'] = geo_zones
        data['location_type'] = urban_rural
        
        # Industry/Sector
        industry_weights = [0.12, 0.08, 0.06, 0.04, 0.05, 0.08, 0.15, 0.06, 0.05, 0.08, 
                           0.03, 0.07, 0.04, 0.06, 0.03, 0.02, 0.03, 0.03, 0.02]
        # Normalize weights to sum to 1
        industry_weights = np.array(industry_weights)
        industry_weights = industry_weights / industry_weights.sum()
        
        industry_codes = list(self.industries.keys())
        data['industry_code'] = np.random.choice(industry_codes, size=self.n_samples, p=industry_weights)
        data['industry_name'] = [self.industries[code] for code in data['industry_code']]
        
        # Firm Age (skewed towards younger firms)
        data['firm_age_years'] = np.random.gamma(2, 3, self.n_samples).astype(int)
        data['firm_age_years'] = np.clip(data['firm_age_years'], 1, 50)
        
        # Firm Size (employees and turnover)
        # Generate correlated employee count and turnover
        base_employees = np.random.lognormal(2, 1, self.n_samples)
        data['num_employees'] = np.clip(base_employees, 1, 200).astype(int)
        
        # Annual turnover (correlated with employees, with industry effects)
        turnover_base = data['num_employees'] * np.random.uniform(500000, 2000000, self.n_samples)
        
        # Industry multipliers for turnover
        industry_multipliers = {
            'J62': 1.5, 'K64': 2.0, 'M69': 1.3, 'C20': 1.4,  # Higher value industries
            'A01': 0.7, 'I56': 0.8, 'G47': 0.9  # Lower margin industries
        }
        
        for i, code in enumerate(data['industry_code']):
            multiplier = industry_multipliers.get(code, 1.0)
            turnover_base[i] *= multiplier
            
        data['annual_turnover_naira'] = turnover_base.astype(int)
        
        # Legal Structure
        legal_structures = ['Sole Proprietorship', 'Partnership', 'Limited Liability Company']
        # Larger firms more likely to be LLCs
        legal_probs = []
        for emp_count in data['num_employees']:
            if emp_count <= 5:
                legal_probs.append([0.6, 0.25, 0.15])
            elif emp_count <= 20:
                legal_probs.append([0.3, 0.3, 0.4])
            else:
                legal_probs.append([0.1, 0.2, 0.7])
        
        data['legal_structure'] = [np.random.choice(legal_structures, p=prob) 
                                  for prob in legal_probs]
        
        # Owner/Manager Profile
        data['owner_age'] = np.random.normal(42, 12, self.n_samples).astype(int)
        data['owner_age'] = np.clip(data['owner_age'], 25, 70)
        
        data['owner_gender'] = np.random.choice(['Male', 'Female'], size=self.n_samples, p=[0.65, 0.35])
        
        # Education level (correlated with industry and location)
        education_probs = []
        for i in range(self.n_samples):
            if data['industry_code'][i] in ['J62', 'K64', 'M69', 'P85', 'Q86']:  # Knowledge industries
                probs = [0.02, 0.03, 0.10, 0.15, 0.45, 0.20, 0.05]
            elif data['location_type'][i] == 'Urban':
                probs = [0.05, 0.08, 0.20, 0.25, 0.30, 0.10, 0.02]
            else:  # Rural
                probs = [0.15, 0.20, 0.30, 0.20, 0.12, 0.03, 0.00]
            education_probs.append(probs)
        
        data['owner_education'] = [np.random.choice(self.education_levels, p=prob) 
                                  for prob in education_probs]
        
        # Field of study (correlated with industry)
        field_mapping = {
            'J62': 'Computer Science/IT', 'K64': 'Economics/Finance', 'M69': 'Business/Management',
            'C10': 'Engineering', 'C13': 'Engineering', 'A01': 'Agriculture', 'Q86': 'Medicine/Health'
        }
        
        data['field_of_study'] = []
        for i, code in enumerate(data['industry_code']):
            if code in field_mapping and np.random.random() < 0.6:
                data['field_of_study'].append(field_mapping[code])
            else:
                data['field_of_study'].append(np.random.choice(self.fields_of_study))
        
        # Prior entrepreneurial experience
        data['prior_entrepreneurial_exp'] = np.random.choice([0, 1], size=self.n_samples, p=[0.4, 0.6])
        
        # Digital literacy score (1-10, correlated with education and age)
        digital_literacy = []
        for i in range(self.n_samples):
            base_score = 5
            
            # Education effect
            edu_level = data['owner_education'][i]
            if edu_level in ['Master', 'PhD']:
                base_score += 2
            elif edu_level in ['HND/Bachelor']:
                base_score += 1
            elif edu_level in ['No Formal Education', 'Primary Education']:
                base_score -= 2
            
            # Age effect (younger = more digital)
            age = data['owner_age'][i]
            if age < 35:
                base_score += 1
            elif age > 55:
                base_score -= 1
            
            # Industry effect
            if data['industry_code'][i] in ['J62', 'J58', 'M73']:
                base_score += 1
            
            # Add noise
            score = base_score + np.random.normal(0, 1)
            digital_literacy.append(max(1, min(10, round(score))))
        
        data['digital_literacy_score'] = digital_literacy
        
        return data
    
    def generate_innovation_adoption(self) -> Dict:
        """Generate Section B: Innovation Adoption (Independent Variables)"""
        
        data = {}
        
        # Helper function to generate correlated Likert responses
        def generate_likert_cluster(base_tendency, n_items, correlation=0.6):
            """Generate correlated Likert scale responses"""
            responses = []
            for i in range(self.n_samples):
                # Individual's base tendency (1-5)
                individual_base = base_tendency[i] + np.random.normal(0, 0.8)
                individual_base = max(1, min(5, individual_base))
                
                item_responses = []
                for _ in range(n_items):
                    # Correlated response with some noise
                    response = individual_base + np.random.normal(0, 0.5)
                    response = max(1, min(5, round(response)))
                    item_responses.append(response)
                responses.append(item_responses)
            return responses
        
        # Base innovation tendency (influenced by firm characteristics)
        innovation_tendency = []
        for i in range(self.n_samples):
            base = 2.5  # Neutral starting point
            
            # Digital literacy effect
            base += (self.data['digital_literacy_score'][i] - 5) * 0.2
            
            # Education effect
            edu = self.data['owner_education'][i]
            if edu in ['Master', 'PhD']:
                base += 0.8
            elif edu in ['HND/Bachelor']:
                base += 0.4
            elif edu in ['No Formal Education', 'Primary Education']:
                base -= 0.6
            
            # Industry effect
            if self.data['industry_code'][i] in ['J62', 'J58', 'M73', 'K64']:
                base += 0.6
            elif self.data['industry_code'][i] in ['A01', 'G47']:
                base -= 0.3
            
            # Firm size effect
            if self.data['num_employees'][i] > 20:
                base += 0.4
            elif self.data['num_employees'][i] < 5:
                base -= 0.2
            
            # Location effect
            if self.data['location_type'][i] == 'Urban':
                base += 0.3
            
            innovation_tendency.append(max(1, min(5, base)))
        
        # Technological Innovation
        tech_items = [
            'digital_tools_computers', 'digital_tools_accounting_software', 'digital_tools_crm',
            'digital_tools_ecommerce', 'digital_tools_cloud_computing', 'digital_tools_social_media'
        ]
        
        tech_responses = generate_likert_cluster(np.array(innovation_tendency), len(tech_items))
        for i, item in enumerate(tech_items):
            data[item] = [resp[i] for resp in tech_responses]
        
        # Advanced Tech Adoption (generally lower adoption)
        advanced_tech_items = [
            'advanced_tech_ai_ml', 'advanced_tech_iot', 'advanced_tech_blockchain', 'advanced_tech_robotics'
        ]
        
        advanced_tendency = np.array(innovation_tendency) - 1.0  # Lower baseline
        advanced_responses = generate_likert_cluster(advanced_tendency, len(advanced_tech_items))
        for i, item in enumerate(advanced_tech_items):
            data[item] = [resp[i] for resp in advanced_responses]
        
        # Digital Presence Score (composite)
        digital_presence_items = ['website_presence', 'social_media_presence', 'online_payments']
        digital_responses = generate_likert_cluster(np.array(innovation_tendency), len(digital_presence_items))
        for i, item in enumerate(digital_presence_items):
            data[item] = [resp[i] for resp in digital_responses]
        
        # Process Innovation
        process_items = [
            'new_production_methods', 'supply_chain_software', 'inventory_management',
            'new_support_processes'
        ]
        
        process_responses = generate_likert_cluster(np.array(innovation_tendency), len(process_items))
        for i, item in enumerate(process_items):
            data[item] = [resp[i] for resp in process_responses]
        
        # Product/Service Innovation
        product_items = [
            'new_products_services_3yrs', 'frequency_new_launches', 'product_improvement_efforts'
        ]
        
        product_responses = generate_likert_cluster(np.array(innovation_tendency), len(product_items))
        for i, item in enumerate(product_items):
            data[item] = [resp[i] for resp in product_responses]
        
        # Business Model Innovation
        business_model_items = [
            'revenue_model_changes', 'value_proposition_changes', 'customer_engagement_changes'
        ]
        
        bm_responses = generate_likert_cluster(np.array(innovation_tendency) - 0.3, len(business_model_items))
        for i, item in enumerate(business_model_items):
            data[item] = [resp[i] for resp in bm_responses]
        
        # Innovation Drivers
        driver_items = [
            'competitive_pressure', 'customer_demand_innovation', 'management_innovation_attitude'
        ]
        
        driver_responses = generate_likert_cluster(np.array(innovation_tendency) + 0.5, len(driver_items))
        for i, item in enumerate(driver_items):
            data[item] = [resp[i] for resp in driver_responses]
        
        return data
    
    def generate_constraints(self) -> Dict:
        """Generate Section C: Constraint Assessment (Moderating Variables)"""
        
        data = {}
        
        # Base constraint levels (higher = more constrained)
        constraint_tendency = []
        for i in range(self.n_samples):
            base = 3.0  # Moderate constraint baseline
            
            # Firm size effect (smaller firms more constrained)
            if self.data['num_employees'][i] < 5:
                base += 0.8
            elif self.data['num_employees'][i] > 20:
                base -= 0.5
            
            # Location effect (rural more constrained)
            if self.data['location_type'][i] == 'Rural':
                base += 0.6
            
            # Geo-political zone effect
            if self.data['geo_political_zone'][i] in ['North East', 'North West']:
                base += 0.4
            elif self.data['geo_political_zone'][i] == 'South West':
                base -= 0.3
            
            # Legal structure effect
            if self.data['legal_structure'][i] == 'Sole Proprietorship':
                base += 0.4
            
            constraint_tendency.append(max(1, min(5, base)))
        
        def generate_constraint_cluster(base_tendency, n_items, correlation=0.5):
            responses = []
            for i in range(self.n_samples):
                individual_base = base_tendency[i] + np.random.normal(0, 0.6)
                individual_base = max(1, min(5, individual_base))
                
                item_responses = []
                for _ in range(n_items):
                    response = individual_base + np.random.normal(0, 0.7)
                    response = max(1, min(5, round(response)))
                    item_responses.append(response)
                responses.append(item_responses)
            return responses
        
        # Financial Constraints
        financial_items = [
            'access_to_credit', 'cost_of_innovation', 'internal_capital_sufficiency'
        ]
        
        financial_responses = generate_constraint_cluster(constraint_tendency, len(financial_items))
        for i, item in enumerate(financial_items):
            data[item] = [resp[i] for resp in financial_responses]
        
        # Human Capital Constraints
        human_capital_items = [
            'skilled_employee_availability', 'training_costs', 'management_capability'
        ]
        
        hc_responses = generate_constraint_cluster(constraint_tendency, len(human_capital_items))
        for i, item in enumerate(human_capital_items):
            data[item] = [resp[i] for resp in hc_responses]
        
        # Infrastructural Constraints
        infra_tendency = []
        for i, base in enumerate(constraint_tendency):
            # Infrastructure worse in rural and northern areas
            if self.data['location_type'][i] == 'Rural':
                base += 0.8
            if self.data['geo_political_zone'][i] in ['North East', 'North West']:
                base += 0.6
            infra_tendency.append(base)
        
        infra_items = [
            'electricity_reliability', 'internet_quality_cost', 'logistics_transportation'
        ]
        
        infra_responses = generate_constraint_cluster(infra_tendency, len(infra_items))
        for i, item in enumerate(infra_items):
            data[item] = [resp[i] for resp in infra_responses]
        
        # Regulatory and Institutional Constraints
        regulatory_items = [
            'regulatory_burden', 'corruption_informal_charges', 'govt_support_effectiveness'
        ]
        
        reg_responses = generate_constraint_cluster(constraint_tendency, len(regulatory_items))
        for i, item in enumerate(regulatory_items):
            data[item] = [resp[i] for resp in reg_responses]
        
        # Market Constraints
        market_items = [
            'competition_intensity', 'demand_uncertainty', 'international_market_access'
        ]
        
        market_responses = generate_constraint_cluster(constraint_tendency, len(market_items))
        for i, item in enumerate(market_items):
            data[item] = [resp[i] for resp in market_responses]
        
        return data
    
    def generate_performance(self) -> Dict:
        """Generate Section D: Firm Performance and Growth (Dependent Variables)"""
        
        data = {}
        
        # Calculate innovation scores for each firm
        innovation_scores = []
        for i in range(self.n_samples):
            # Average innovation adoption across all categories
            tech_score = np.mean([
                self.data['digital_tools_computers'][i], self.data['digital_tools_accounting_software'][i],
                self.data['digital_tools_crm'][i], self.data['digital_tools_ecommerce'][i],
                self.data['digital_tools_cloud_computing'][i], self.data['digital_tools_social_media'][i]
            ])
            
            process_score = np.mean([
                self.data['new_production_methods'][i], self.data['supply_chain_software'][i],
                self.data['inventory_management'][i], self.data['new_support_processes'][i]
            ])
            
            product_score = np.mean([
                self.data['new_products_services_3yrs'][i], self.data['frequency_new_launches'][i],
                self.data['product_improvement_efforts'][i]
            ])
            
            overall_innovation = np.mean([tech_score, process_score, product_score])
            innovation_scores.append(overall_innovation)
        
        # Calculate constraint scores
        constraint_scores = []
        for i in range(self.n_samples):
            financial_constraint = np.mean([
                self.data['access_to_credit'][i], self.data['cost_of_innovation'][i],
                self.data['internal_capital_sufficiency'][i]
            ])
            
            infra_constraint = np.mean([
                self.data['electricity_reliability'][i], self.data['internet_quality_cost'][i],
                self.data['logistics_transportation'][i]
            ])
            
            overall_constraint = np.mean([financial_constraint, infra_constraint])
            constraint_scores.append(overall_constraint)
        
        # Generate performance based on innovation and constraints
        performance_tendency = []
        for i in range(self.n_samples):
            base_performance = 2.5  # Neutral baseline
            
            # Innovation effect (positive)
            base_performance += (innovation_scores[i] - 2.5) * 0.8
            
            # Constraint effect (negative)
            base_performance -= (constraint_scores[i] - 2.5) * 0.6
            
            # Firm characteristics effects
            if self.data['num_employees'][i] > 20:
                base_performance += 0.3
            
            if self.data['owner_education'][i] in ['Master', 'PhD']:
                base_performance += 0.2
            
            if self.data['location_type'][i] == 'Urban':
                base_performance += 0.2
            
            # Industry effects
            if self.data['industry_code'][i] in ['J62', 'K64', 'M69']:
                base_performance += 0.3
            
            performance_tendency.append(max(1, min(5, base_performance)))
        
        def generate_performance_cluster(base_tendency, n_items, correlation=0.7):
            responses = []
            for i in range(self.n_samples):
                individual_base = base_tendency[i] + np.random.normal(0, 0.5)
                individual_base = max(1, min(5, individual_base))
                
                item_responses = []
                for _ in range(n_items):
                    response = individual_base + np.random.normal(0, 0.4)
                    response = max(1, min(5, round(response)))
                    item_responses.append(response)
                responses.append(item_responses)
            return responses
        
        # Subjective Performance (Likert Scale)
        subjective_items = [
            'profitability_growth_3yrs', 'sales_growth_3yrs', 'market_share_growth_3yrs',
            'roi_satisfaction', 'overall_performance_satisfaction'
        ]
        
        subjective_responses = generate_performance_cluster(performance_tendency, len(subjective_items))
        for i, item in enumerate(subjective_items):
            data[item] = [resp[i] for resp in subjective_responses]
        
        # Objective Performance (with realistic ranges and missing data)
        # Annual turnover growth (percentage)
        turnover_growth = []
        for i, perf in enumerate(performance_tendency):
            if np.random.random() < 0.3:  # 30% missing data
                turnover_growth.append(np.nan)
            else:
                # Base growth rate influenced by performance
                base_growth = (perf - 2.5) * 10  # -25% to +25% range
                growth = base_growth + np.random.normal(0, 15)
                growth = max(-50, min(100, growth))  # Cap at reasonable limits
                turnover_growth.append(round(growth, 1))
        
        data['annual_turnover_growth_pct'] = turnover_growth
        
        # Profit margin (percentage of turnover)
        profit_margins = []
        for i, perf in enumerate(performance_tendency):
            if np.random.random() < 0.4:  # 40% missing data (sensitive info)
                profit_margins.append(np.nan)
            else:
                base_margin = (perf - 2.5) * 8 + 10  # 2% to 30% range
                margin = base_margin + np.random.normal(0, 5)
                margin = max(-5, min(50, margin))
                profit_margins.append(round(margin, 1))
        
        data['profit_margin_pct'] = profit_margins
        
        # Employee growth rate
        employee_growth = []
        for i, perf in enumerate(performance_tendency):
            if np.random.random() < 0.2:  # 20% missing data
                employee_growth.append(np.nan)
            else:
                base_growth = (perf - 2.5) * 15
                growth = base_growth + np.random.normal(0, 20)
                growth = max(-30, min(200, growth))
                employee_growth.append(round(growth, 1))
        
        data['employee_growth_pct'] = employee_growth
        
        # Number of new branches/locations
        new_branches = []
        for i, perf in enumerate(performance_tendency):
            if self.data['num_employees'][i] < 10:  # Small firms less likely to expand
                prob_expansion = max(0, (perf - 2) * 0.1)
            else:
                prob_expansion = max(0, (perf - 2) * 0.2)
            
            if np.random.random() < prob_expansion:
                branches = np.random.poisson(1) + 1
            else:
                branches = 0
            new_branches.append(branches)
        
        data['new_branches_3yrs'] = new_branches
        
        # Non-Financial Growth Indicators
        non_financial_items = [
            'product_line_increase', 'service_quality_improvement', 'customer_satisfaction_improvement'
        ]
        
        nf_responses = generate_performance_cluster(performance_tendency, len(non_financial_items))
        for i, item in enumerate(non_financial_items):
            data[item] = [resp[i] for resp in nf_responses]
        
        return data
    
    def generate_dataset(self) -> pd.DataFrame:
        """Generate the complete dataset"""
        
        print("Generating firmographics and managerial characteristics...")
        self.data.update(self.generate_firmographics())
        
        print("Generating innovation adoption measures...")
        self.data.update(self.generate_innovation_adoption())
        
        print("Generating constraint assessments...")
        self.data.update(self.generate_constraints())
        
        print("Generating performance and growth measures...")
        self.data.update(self.generate_performance())
        
        # Create DataFrame
        df = pd.DataFrame(self.data)
        
        # Add some derived variables
        df['innovation_composite_score'] = (
            df[['digital_tools_computers', 'digital_tools_accounting_software', 'digital_tools_crm',
               'new_production_methods', 'new_products_services_3yrs']].mean(axis=1)
        )
        
        df['constraint_composite_score'] = (
            df[['access_to_credit', 'electricity_reliability', 'skilled_employee_availability']].mean(axis=1)
        )
        
        df['performance_composite_score'] = (
            df[['profitability_growth_3yrs', 'sales_growth_3yrs', 'overall_performance_satisfaction']].mean(axis=1)
        )
        
        return df
    
    def create_data_dictionary(self) -> pd.DataFrame:
        """Create a comprehensive data dictionary"""
        
        dictionary_data = []
        
        # Section A: Firmographics
        section_a = [
            ('firm_id', 'Categorical', 'Anonymized firm identifier', 'SME_0001 to SME_2000'),
            ('state', 'Categorical', 'Nigerian state where firm is located', '36 Nigerian states + FCT'),
            ('geo_political_zone', 'Categorical', 'Geo-political zone', 'North Central, North East, North West, South East, South South, South West'),
            ('location_type', 'Categorical', 'Urban or rural location', 'Urban, Rural'),
            ('industry_code', 'Categorical', 'ISIC industry classification code', 'A01, C10, C13, etc.'),
            ('industry_name', 'Categorical', 'Industry sector name', 'Agriculture, Manufacturing, Services, etc.'),
            ('firm_age_years', 'Continuous', 'Years since firm establishment', '1-50 years'),
            ('num_employees', 'Continuous', 'Number of full-time employees', '1-200 employees'),
            ('annual_turnover_naira', 'Continuous', 'Annual turnover in Nigerian Naira', 'Varies by firm size and industry'),
            ('legal_structure', 'Categorical', 'Legal form of business', 'Sole Proprietorship, Partnership, Limited Liability Company'),
            ('owner_age', 'Continuous', 'Age of owner/manager', '25-70 years'),
            ('owner_gender', 'Categorical', 'Gender of owner/manager', 'Male, Female'),
            ('owner_education', 'Ordinal', 'Highest educational qualification', 'No Formal Education to PhD'),
            ('field_of_study', 'Categorical', 'Field of educational specialization', 'Business, Engineering, IT, etc.'),
            ('prior_entrepreneurial_exp', 'Binary', 'Previous entrepreneurial experience', '0=No, 1=Yes'),
            ('digital_literacy_score', 'Ordinal', 'Self-assessed digital literacy', '1-10 scale')
        ]
        
        # Section B: Innovation Adoption (Likert scales 1-5)
        section_b = [
            ('digital_tools_computers', 'Ordinal', 'Extent of computer usage', '1=Strongly Disagree to 5=Strongly Agree'),
            ('digital_tools_accounting_software', 'Ordinal', 'Use of accounting software', '1-5 Likert scale'),
            ('digital_tools_crm', 'Ordinal', 'Use of CRM systems', '1-5 Likert scale'),
            ('digital_tools_ecommerce', 'Ordinal', 'Use of e-commerce platforms', '1-5 Likert scale'),
            ('digital_tools_cloud_computing', 'Ordinal', 'Use of cloud computing', '1-5 Likert scale'),
            ('digital_tools_social_media', 'Ordinal', 'Use of social media for business', '1-5 Likert scale'),
            ('advanced_tech_ai_ml', 'Ordinal', 'Use of AI/ML for analytics', '1-5 Likert scale'),
            ('advanced_tech_iot', 'Ordinal', 'Use of IoT in operations', '1-5 Likert scale'),
            ('advanced_tech_blockchain', 'Ordinal', 'Use of blockchain technology', '1-5 Likert scale'),
            ('advanced_tech_robotics', 'Ordinal', 'Use of robotics/automation', '1-5 Likert scale'),
            ('website_presence', 'Ordinal', 'Company website presence', '1-5 Likert scale'),
            ('social_media_presence', 'Ordinal', 'Social media business presence', '1-5 Likert scale'),
            ('online_payments', 'Ordinal', 'Online payment capabilities', '1-5 Likert scale'),
            ('new_production_methods', 'Ordinal', 'Adoption of new production methods', '1-5 Likert scale'),
            ('supply_chain_software', 'Ordinal', 'Use of supply chain software', '1-5 Likert scale'),
            ('inventory_management', 'Ordinal', 'Use of inventory management systems', '1-5 Likert scale'),
            ('new_support_processes', 'Ordinal', 'New techniques for support processes', '1-5 Likert scale'),
            ('new_products_services_3yrs', 'Ordinal', 'Introduction of new products/services', '1-5 Likert scale'),
            ('frequency_new_launches', 'Ordinal', 'Frequency of new product launches', '1-5 Likert scale'),
            ('product_improvement_efforts', 'Ordinal', 'Product improvement efforts', '1-5 Likert scale'),
            ('revenue_model_changes', 'Ordinal', 'Changes in revenue models', '1-5 Likert scale'),
            ('value_proposition_changes', 'Ordinal', 'Changes in value proposition', '1-5 Likert scale'),
            ('customer_engagement_changes', 'Ordinal', 'Changes in customer engagement', '1-5 Likert scale'),
            ('competitive_pressure', 'Ordinal', 'Perceived competitive pressure', '1-5 Likert scale'),
            ('customer_demand_innovation', 'Ordinal', 'Customer demand for innovation', '1-5 Likert scale'),
            ('management_innovation_attitude', 'Ordinal', 'Management attitude towards innovation', '1-5 Likert scale')
        ]
        
        # Section C: Constraints (Likert scales 1-5, higher = more constrained)
        section_c = [
            ('access_to_credit', 'Ordinal', 'Difficulty accessing credit/loans', '1-5 scale (5=Very Difficult)'),
            ('cost_of_innovation', 'Ordinal', 'High cost of innovation', '1-5 scale (5=Very High Cost)'),
            ('internal_capital_sufficiency', 'Ordinal', 'Insufficient internal capital', '1-5 scale (5=Very Insufficient)'),
            ('skilled_employee_availability', 'Ordinal', 'Difficulty finding skilled employees', '1-5 scale (5=Very Difficult)'),
            ('training_costs', 'Ordinal', 'High cost of training staff', '1-5 scale (5=Very High Cost)'),
            ('management_capability', 'Ordinal', 'Insufficient management capability', '1-5 scale (5=Very Insufficient)'),
            ('electricity_reliability', 'Ordinal', 'Poor electricity reliability', '1-5 scale (5=Very Poor)'),
            ('internet_quality_cost', 'Ordinal', 'Poor internet quality/high cost', '1-5 scale (5=Very Poor/Expensive)'),
            ('logistics_transportation', 'Ordinal', 'Poor logistics/transportation', '1-5 scale (5=Very Poor)'),
            ('regulatory_burden', 'Ordinal', 'High regulatory burden', '1-5 scale (5=Very High Burden)'),
            ('corruption_informal_charges', 'Ordinal', 'Corruption and informal charges', '1-5 scale (5=Very High)'),
            ('govt_support_effectiveness', 'Ordinal', 'Ineffective government support', '1-5 scale (5=Very Ineffective)'),
            ('competition_intensity', 'Ordinal', 'Intense competition', '1-5 scale (5=Very Intense)'),
            ('demand_uncertainty', 'Ordinal', 'High demand uncertainty', '1-5 scale (5=Very Uncertain)'),
            ('international_market_access', 'Ordinal', 'Poor international market access', '1-5 scale (5=Very Poor)')
        ]
        
        # Section D: Performance (Likert scales 1-5 for subjective, various for objective)
        section_d = [
            ('profitability_growth_3yrs', 'Ordinal', 'Profitability growth (last 3 years)', '1-5 Likert scale'),
            ('sales_growth_3yrs', 'Ordinal', 'Sales growth (last 3 years)', '1-5 Likert scale'),
            ('market_share_growth_3yrs', 'Ordinal', 'Market share growth (last 3 years)', '1-5 Likert scale'),
            ('roi_satisfaction', 'Ordinal', 'Return on Investment satisfaction', '1-5 Likert scale'),
            ('overall_performance_satisfaction', 'Ordinal', 'Overall performance satisfaction', '1-5 Likert scale'),
            ('annual_turnover_growth_pct', 'Continuous', 'Annual turnover growth percentage', '-50% to +100% (30% missing)'),
            ('profit_margin_pct', 'Continuous', 'Profit margin percentage', '-5% to +50% (40% missing)'),
            ('employee_growth_pct', 'Continuous', 'Employee growth percentage', '-30% to +200% (20% missing)'),
            ('new_branches_3yrs', 'Continuous', 'Number of new branches (last 3 years)', '0-5+ branches'),
            ('product_line_increase', 'Ordinal', 'Increase in product/service lines', '1-5 Likert scale'),
            ('service_quality_improvement', 'Ordinal', 'Service quality improvement', '1-5 Likert scale'),
            ('customer_satisfaction_improvement', 'Ordinal', 'Customer satisfaction improvement', '1-5 Likert scale')
        ]
        
        # Composite scores
        composite_scores = [
            ('innovation_composite_score', 'Continuous', 'Composite innovation adoption score', 'Average of key innovation indicators'),
            ('constraint_composite_score', 'Continuous', 'Composite constraint score', 'Average of key constraint indicators'),
            ('performance_composite_score', 'Continuous', 'Composite performance score', 'Average of key performance indicators')
        ]
        
        # Combine all sections
        all_variables = section_a + section_b + section_c + section_d + composite_scores
        
        for var_name, var_type, description, value_range in all_variables:
            dictionary_data.append({
                'Variable_Name': var_name,
                'Data_Type': var_type,
                'Description': description,
                'Value_Range': value_range,
                'Section': 'A' if var_name in [x[0] for x in section_a] else
                          'B' if var_name in [x[0] for x in section_b] else
                          'C' if var_name in [x[0] for x in section_c] else
                          'D' if var_name in [x[0] for x in section_d] else 'Derived'
            })
        
        return pd.DataFrame(dictionary_data)

def main():
    """Main function to generate the dataset"""
    
    print("=" * 60)
    print("SME Innovation Dataset Generator")
    print("Research Topic: Leveraging Machine Learning to Examine Innovation")
    print("Adoption and Constraints in Nigerian SMEs")
    print("=" * 60)
    
    # Generate dataset
    generator = SMEInnovationDatasetGenerator(n_samples=2000)
    
    print(f"\nGenerating dataset with {generator.n_samples} SME records...")
    df = generator.generate_dataset()
    
    print(f"\nDataset generated successfully!")
    print(f"Shape: {df.shape}")
    print(f"Columns: {len(df.columns)}")
    
    # Create data dictionary
    print("\nCreating data dictionary...")
    data_dict = generator.create_data_dictionary()
    
    # Save files
    output_dir = "sme_innovation_dataset"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save main dataset
    df.to_csv(f"{output_dir}/sme_innovation_dataset.csv", index=False)
    df.to_excel(f"{output_dir}/sme_innovation_dataset.xlsx", index=False)
    
    # Save data dictionary
    data_dict.to_csv(f"{output_dir}/data_dictionary.csv", index=False)
    data_dict.to_excel(f"{output_dir}/data_dictionary.xlsx", index=False)
    
    # Generate summary statistics
    print("\nGenerating summary statistics...")
    summary_stats = df.describe(include='all')
    summary_stats.to_csv(f"{output_dir}/summary_statistics.csv")
    
    # Create correlation matrix for key variables
    key_vars = [
        'innovation_composite_score', 'constraint_composite_score', 'performance_composite_score',
        'firm_age_years', 'num_employees', 'digital_literacy_score'
    ]
    
    correlation_matrix = df[key_vars].corr()
    correlation_matrix.to_csv(f"{output_dir}/correlation_matrix.csv")
    
    print(f"\nFiles saved to '{output_dir}/' directory:")
    print("- sme_innovation_dataset.csv")
    print("- sme_innovation_dataset.xlsx")
    print("- data_dictionary.csv")
    print("- data_dictionary.xlsx")
    print("- summary_statistics.csv")
    print("- correlation_matrix.csv")
    
    # Display basic info
    print("\n" + "=" * 60)
    print("DATASET OVERVIEW")
    print("=" * 60)
    
    print(f"\nTotal Records: {len(df)}")
    print(f"Total Variables: {len(df.columns)}")
    
    print(f"\nGeographic Distribution:")
    print(df['geo_political_zone'].value_counts())
    
    print(f"\nIndustry Distribution (Top 10):")
    print(df['industry_name'].value_counts().head(10))
    
    print(f"\nFirm Size Distribution:")
    print(f"Employees - Mean: {df['num_employees'].mean():.1f}, Median: {df['num_employees'].median():.1f}")
    print(f"Age - Mean: {df['firm_age_years'].mean():.1f}, Median: {df['firm_age_years'].median():.1f}")
    
    print(f"\nKey Composite Scores:")
    print(f"Innovation Score - Mean: {df['innovation_composite_score'].mean():.2f}")
    print(f"Constraint Score - Mean: {df['constraint_composite_score'].mean():.2f}")
    print(f"Performance Score - Mean: {df['performance_composite_score'].mean():.2f}")
    
    print(f"\nMissing Data Summary:")
    missing_data = df.isnull().sum()
    missing_vars = missing_data[missing_data > 0]
    if len(missing_vars) > 0:
        for var, count in missing_vars.items():
            print(f"{var}: {count} ({count/len(df)*100:.1f}%)")
    else:
        print("No missing data in core variables")
    
    print("\n" + "=" * 60)
    print("Dataset generation completed successfully!")
    print("Ready for machine learning analysis and statistical modeling.")
    print("=" * 60)

if __name__ == "__main__":
    main()