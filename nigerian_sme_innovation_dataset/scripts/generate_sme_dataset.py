"""
Nigerian SME Innovation Adoption Dataset Generator
===================================================
This script generates a synthetic dataset for studying innovation adoption 
and constraints in Nigerian SMEs with implications for performance and growth.

Author: Data Generation System
Date: 2024
Research Topic: Leveraging Machine Learning to Examine Innovation Adoption and 
                Constraints in Nigerian SMEs: Implications for Performance and Growth
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)
fake = Faker('en_NG')  # Nigerian locale
Faker.seed(42)

class NigerianSMEDataGenerator:
    def __init__(self, n_samples=5000):
        """
        Initialize the data generator for Nigerian SME innovation dataset.
        
        Parameters:
        -----------
        n_samples : int
            Number of SME records to generate
        """
        self.n_samples = n_samples
        self.data = {}
        
        # Nigerian states by geopolitical zones
        self.geo_zones = {
            'North-Central': ['Benue', 'Kogi', 'Kwara', 'Nasarawa', 'Niger', 'Plateau', 'FCT'],
            'North-East': ['Adamawa', 'Bauchi', 'Borno', 'Gombe', 'Taraba', 'Yobe'],
            'North-West': ['Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Sokoto', 'Zamfara'],
            'South-East': ['Abia', 'Anambra', 'Ebonyi', 'Enugu', 'Imo'],
            'South-South': ['Akwa Ibom', 'Bayelsa', 'Cross River', 'Delta', 'Edo', 'Rivers'],
            'South-West': ['Ekiti', 'Lagos', 'Ogun', 'Ondo', 'Osun', 'Oyo']
        }
        
        # Industry sectors (ISIC-based)
        self.industries = {
            'Manufacturing': 0.20,
            'Wholesale and Retail Trade': 0.25,
            'Information and Communication': 0.15,
            'Agriculture': 0.10,
            'Accommodation and Food Service': 0.08,
            'Professional Services': 0.07,
            'Construction': 0.05,
            'Transportation and Storage': 0.05,
            'Education': 0.03,
            'Health and Social Work': 0.02
        }
        
        # Educational fields
        self.education_fields = [
            'Business Administration', 'Engineering', 'Computer Science',
            'Accounting', 'Marketing', 'Economics', 'Agriculture',
            'Medicine', 'Law', 'Arts and Humanities', 'Natural Sciences'
        ]

    def generate_firmographics(self):
        """Generate Section A: Firmographics & Managerial Characteristics"""
        print("Generating Firmographics & Managerial Characteristics...")
        
        for i in range(self.n_samples):
            # Firm ID
            self.data.setdefault('firm_id', []).append(f'SME_{str(i+1).zfill(5)}')
            
            # Location
            zone = np.random.choice(list(self.geo_zones.keys()), 
                                  p=[0.10, 0.08, 0.12, 0.15, 0.20, 0.35])  # Lagos heavy
            state = np.random.choice(self.geo_zones[zone])
            self.data.setdefault('state', []).append(state)
            self.data.setdefault('geo_political_zone', []).append(zone)
            
            # Urban/Rural distribution (more urban in SW, SS)
            if zone in ['South-West', 'South-South']:
                urban_prob = 0.75
            elif zone in ['South-East', 'North-Central']:
                urban_prob = 0.60
            else:
                urban_prob = 0.45
            self.data.setdefault('location_type', []).append(
                np.random.choice(['Urban', 'Rural'], p=[urban_prob, 1-urban_prob])
            )
            
            # Industry
            industry = np.random.choice(list(self.industries.keys()), 
                                      p=list(self.industries.values()))
            self.data.setdefault('industry_sector', []).append(industry)
            
            # Firm age (years) - exponential distribution, most firms are young
            firm_age = int(np.random.exponential(scale=5) + 1)
            firm_age = min(firm_age, 50)  # Cap at 50 years
            self.data.setdefault('firm_age_years', []).append(firm_age)
            
            # Firm size - correlated with age and industry
            if industry in ['Manufacturing', 'Construction']:
                size_mean = 25 + firm_age * 1.5
            elif industry in ['Information and Communication', 'Professional Services']:
                size_mean = 10 + firm_age * 0.8
            else:
                size_mean = 15 + firm_age * 1.0
            
            employees = max(1, int(np.random.lognormal(np.log(size_mean), 0.5)))
            employees = min(employees, 250)  # SME definition cap
            self.data.setdefault('num_employees', []).append(employees)
            
            # Annual turnover (in millions of Naira) - correlated with size and industry
            if industry in ['Wholesale and Retail Trade', 'Manufacturing']:
                turnover_base = employees * np.random.uniform(2, 5)
            elif industry in ['Information and Communication', 'Professional Services']:
                turnover_base = employees * np.random.uniform(3, 8)
            else:
                turnover_base = employees * np.random.uniform(1.5, 4)
            
            turnover = round(turnover_base * np.random.uniform(0.8, 1.2), 2)
            self.data.setdefault('annual_turnover_million_naira', []).append(turnover)
            
            # Legal structure - correlated with size
            if employees < 5:
                legal_probs = [0.70, 0.20, 0.10]  # Mostly sole proprietorship
            elif employees < 20:
                legal_probs = [0.40, 0.30, 0.30]
            else:
                legal_probs = [0.20, 0.20, 0.60]  # Mostly limited liability
            
            legal_structure = np.random.choice(
                ['Sole Proprietorship', 'Partnership', 'Limited Liability'],
                p=legal_probs
            )
            self.data.setdefault('legal_structure', []).append(legal_structure)
            
            # Owner/Manager Profile
            # Age - correlated with firm age
            owner_age = max(25, min(70, 35 + firm_age // 2 + np.random.randint(-5, 10)))
            self.data.setdefault('owner_age', []).append(owner_age)
            
            # Gender - slight male bias reflecting current reality
            self.data.setdefault('owner_gender', []).append(
                np.random.choice(['Male', 'Female'], p=[0.65, 0.35])
            )
            
            # Educational level - correlated with industry
            if industry in ['Information and Communication', 'Professional Services', 'Health and Social Work']:
                edu_probs = [0.05, 0.10, 0.15, 0.50, 0.20]  # More higher education
            else:
                edu_probs = [0.10, 0.20, 0.25, 0.35, 0.10]
            
            education = np.random.choice(
                ['No Formal Education', 'Primary', 'Secondary', 'Bachelor', 'Postgraduate'],
                p=edu_probs
            )
            self.data.setdefault('owner_education_level', []).append(education)
            
            # Field of study
            self.data.setdefault('owner_field_of_study', []).append(
                np.random.choice(self.education_fields) if education in ['Bachelor', 'Postgraduate'] else 'N/A'
            )
            
            # Prior entrepreneurial experience (years)
            prior_exp = max(0, owner_age - 25 - firm_age) if np.random.random() > 0.4 else 0
            self.data.setdefault('prior_entrepreneurial_experience_years', []).append(prior_exp)
            
            # Digital literacy score (1-10) - correlated with age, education, industry
            base_digital = 5
            if owner_age < 40:
                base_digital += 1.5
            if education in ['Bachelor', 'Postgraduate']:
                base_digital += 1.5
            if industry in ['Information and Communication', 'Professional Services']:
                base_digital += 1
            
            digital_score = round(min(10, max(1, base_digital + np.random.normal(0, 1))), 1)
            self.data.setdefault('digital_literacy_score', []).append(digital_score)

    def generate_innovation_adoption(self):
        """Generate Section B: Innovation Adoption (Independent Variables)"""
        print("Generating Innovation Adoption Variables...")
        
        for i in range(self.n_samples):
            # Get context from firmographics for correlation
            digital_literacy = self.data['digital_literacy_score'][i]
            industry = self.data['industry_sector'][i]
            employees = self.data['num_employees'][i]
            firm_age = self.data['firm_age_years'][i]
            
            # Base innovation propensity
            innovation_base = digital_literacy / 10 * 3 + np.random.normal(0, 0.5)
            
            # Technological Innovation
            # Digital Tools Adoption (1-5 scale for each tool)
            digital_factor = min(5, max(1, innovation_base + np.random.normal(0, 0.5)))
            
            self.data.setdefault('digital_tools_computers', []).append(
                round(min(5, max(1, digital_factor + np.random.normal(0.5, 0.3))), 1)
            )
            self.data.setdefault('digital_tools_accounting_software', []).append(
                round(min(5, max(1, digital_factor + np.random.normal(0, 0.4))), 1)
            )
            self.data.setdefault('digital_tools_crm', []).append(
                round(min(5, max(1, digital_factor - 0.5 + np.random.normal(0, 0.5))), 1)
            )
            self.data.setdefault('digital_tools_ecommerce', []).append(
                round(min(5, max(1, digital_factor + np.random.normal(0, 0.6))), 1)
            )
            self.data.setdefault('digital_tools_cloud_computing', []).append(
                round(min(5, max(1, digital_factor - 0.3 + np.random.normal(0, 0.5))), 1)
            )
            self.data.setdefault('digital_tools_social_media', []).append(
                round(min(5, max(1, digital_factor + 0.5 + np.random.normal(0, 0.4))), 1)
            )
            
            # Advanced Tech Adoption (lower scores generally)
            adv_factor = max(1, digital_factor - 1.5)
            self.data.setdefault('advanced_tech_ai_ml', []).append(
                round(min(5, max(1, adv_factor + np.random.normal(-0.5, 0.4))), 1)
            )
            self.data.setdefault('advanced_tech_iot', []).append(
                round(min(5, max(1, adv_factor + np.random.normal(-0.3, 0.3))), 1)
            )
            self.data.setdefault('advanced_tech_blockchain', []).append(
                round(min(5, max(1, adv_factor + np.random.normal(-0.8, 0.3))), 1)
            )
            self.data.setdefault('advanced_tech_robotics', []).append(
                round(min(5, max(1, adv_factor + np.random.normal(-1, 0.3))), 1)
            )
            
            # Level of Digitization composite score
            digitization_components = [
                self.data['digital_tools_ecommerce'][i],
                self.data['digital_tools_social_media'][i],
                digital_factor
            ]
            self.data.setdefault('digitization_level_composite', []).append(
                round(np.mean(digitization_components), 2)
            )
            
            # Process Innovation
            process_base = innovation_base + (0.3 if employees > 20 else -0.2)
            
            self.data.setdefault('process_new_production_methods', []).append(
                round(min(5, max(1, process_base + np.random.normal(0, 0.5))), 1)
            )
            self.data.setdefault('process_supply_chain_software', []).append(
                round(min(5, max(1, process_base + np.random.normal(0, 0.4))), 1)
            )
            self.data.setdefault('process_support_techniques', []).append(
                round(min(5, max(1, process_base + np.random.normal(0.2, 0.4))), 1)
            )
            
            # Product/Service Innovation
            product_base = innovation_base + (0.5 if industry in ['Information and Communication', 'Manufacturing'] else 0)
            
            self.data.setdefault('product_new_goods_services_3years', []).append(
                round(min(5, max(1, product_base + np.random.normal(0, 0.5))), 1)
            )
            self.data.setdefault('product_launch_frequency', []).append(
                round(min(5, max(1, product_base + np.random.normal(-0.2, 0.4))), 1)
            )
            
            # Business Model Innovation
            biz_model_base = innovation_base + (0.3 if firm_age < 5 else -0.2)
            
            self.data.setdefault('business_model_revenue_changes', []).append(
                round(min(5, max(1, biz_model_base + np.random.normal(0, 0.5))), 1)
            )
            self.data.setdefault('business_model_value_proposition', []).append(
                round(min(5, max(1, biz_model_base + np.random.normal(0, 0.4))), 1)
            )
            
            # Innovation Drivers
            self.data.setdefault('driver_competitive_pressure', []).append(
                round(min(5, max(1, 3.5 + np.random.normal(0, 0.6))), 1)
            )
            self.data.setdefault('driver_customer_demand', []).append(
                round(min(5, max(1, 3.8 + np.random.normal(0, 0.5))), 1)
            )
            self.data.setdefault('driver_management_attitude', []).append(
                round(min(5, max(1, innovation_base + 0.5 + np.random.normal(0, 0.4))), 1)
            )

    def generate_constraints(self):
        """Generate Section C: Constraint Assessment (Moderating Variables)"""
        print("Generating Constraint Assessment Variables...")
        
        for i in range(self.n_samples):
            # Get context
            zone = self.data['geo_political_zone'][i]
            location_type = self.data['location_type'][i]
            employees = self.data['num_employees'][i]
            turnover = self.data['annual_turnover_million_naira'][i]
            
            # Financial Constraints (higher scores = more constraints)
            financial_base = 3.5 - (turnover / 100)  # Larger firms have fewer constraints
            
            self.data.setdefault('constraint_access_to_credit', []).append(
                round(min(5, max(1, financial_base + np.random.normal(0, 0.6))), 1)
            )
            self.data.setdefault('constraint_innovation_cost', []).append(
                round(min(5, max(1, financial_base + 0.3 + np.random.normal(0, 0.5))), 1)
            )
            self.data.setdefault('constraint_internal_capital', []).append(
                round(min(5, max(1, financial_base - 0.2 + np.random.normal(0, 0.5))), 1)
            )
            
            # Human Capital Constraints
            hc_base = 3.2 + (0.5 if location_type == 'Rural' else -0.2)
            
            self.data.setdefault('constraint_finding_skilled_employees', []).append(
                round(min(5, max(1, hc_base + np.random.normal(0, 0.6))), 1)
            )
            self.data.setdefault('constraint_training_cost', []).append(
                round(min(5, max(1, hc_base + 0.2 + np.random.normal(0, 0.5))), 1)
            )
            self.data.setdefault('constraint_management_capability', []).append(
                round(min(5, max(1, hc_base - 0.3 + np.random.normal(0, 0.5))), 1)
            )
            
            # Infrastructure Constraints (worse in certain zones)
            infra_base = 3.0
            if zone in ['North-East', 'North-West']:
                infra_base += 0.8
            elif zone in ['South-West', 'South-South']:
                infra_base -= 0.5
            if location_type == 'Rural':
                infra_base += 0.6
            
            self.data.setdefault('constraint_electricity_reliability', []).append(
                round(min(5, max(1, infra_base + 0.5 + np.random.normal(0, 0.6))), 1)
            )
            self.data.setdefault('constraint_internet_quality_cost', []).append(
                round(min(5, max(1, infra_base + np.random.normal(0, 0.5))), 1)
            )
            self.data.setdefault('constraint_logistics_transportation', []).append(
                round(min(5, max(1, infra_base + 0.2 + np.random.normal(0, 0.5))), 1)
            )
            
            # Regulatory Constraints
            reg_base = 3.3
            
            self.data.setdefault('constraint_regulations_taxes', []).append(
                round(min(5, max(1, reg_base + np.random.normal(0, 0.6))), 1)
            )
            self.data.setdefault('constraint_corruption_informal_charges', []).append(
                round(min(5, max(1, reg_base + 0.2 + np.random.normal(0, 0.7))), 1)
            )
            self.data.setdefault('constraint_government_support_effectiveness', []).append(
                round(min(5, max(1, 5.5 - reg_base + np.random.normal(0, 0.5))), 1)  # Inverted
            )
            
            # Market Constraints
            market_base = 3.4
            
            self.data.setdefault('constraint_competition_intensity', []).append(
                round(min(5, max(1, market_base + 0.3 + np.random.normal(0, 0.5))), 1)
            )
            self.data.setdefault('constraint_demand_uncertainty', []).append(
                round(min(5, max(1, market_base + np.random.normal(0, 0.6))), 1)
            )
            self.data.setdefault('constraint_international_market_access', []).append(
                round(min(5, max(1, market_base + 0.4 + np.random.normal(0, 0.5))), 1)
            )

    def generate_performance(self):
        """Generate Section D: Firm Performance and Growth (Dependent Variables)"""
        print("Generating Performance and Growth Variables...")
        
        for i in range(self.n_samples):
            # Calculate innovation score (average of innovation variables)
            innovation_vars = [
                self.data['digital_tools_computers'][i],
                self.data['digital_tools_accounting_software'][i],
                self.data['digital_tools_crm'][i],
                self.data['digital_tools_ecommerce'][i],
                self.data['process_new_production_methods'][i],
                self.data['product_new_goods_services_3years'][i],
                self.data['business_model_revenue_changes'][i]
            ]
            innovation_score = np.mean(innovation_vars)
            
            # Calculate constraint score (average of constraint variables)
            constraint_vars = [
                self.data['constraint_access_to_credit'][i],
                self.data['constraint_finding_skilled_employees'][i],
                self.data['constraint_electricity_reliability'][i],
                self.data['constraint_regulations_taxes'][i],
                self.data['constraint_competition_intensity'][i]
            ]
            constraint_score = np.mean(constraint_vars)
            
            # Performance is positively correlated with innovation, negatively with constraints
            performance_base = 2.5 + (innovation_score * 0.6) - (constraint_score * 0.3)
            
            # Add some industry-specific effects
            industry = self.data['industry_sector'][i]
            if industry in ['Information and Communication', 'Professional Services']:
                performance_base += 0.3
            elif industry in ['Agriculture', 'Accommodation and Food Service']:
                performance_base -= 0.2
            
            # Subjective Performance Measures (Likert 1-5)
            perf_noise = 0.4
            
            self.data.setdefault('performance_profitability_growth', []).append(
                round(min(5, max(1, performance_base + np.random.normal(0, perf_noise))), 1)
            )
            self.data.setdefault('performance_sales_growth', []).append(
                round(min(5, max(1, performance_base + 0.1 + np.random.normal(0, perf_noise))), 1)
            )
            self.data.setdefault('performance_market_share_growth', []).append(
                round(min(5, max(1, performance_base - 0.1 + np.random.normal(0, perf_noise))), 1)
            )
            self.data.setdefault('performance_roi', []).append(
                round(min(5, max(1, performance_base + np.random.normal(0, perf_noise))), 1)
            )
            self.data.setdefault('performance_overall_satisfaction', []).append(
                round(min(5, max(1, performance_base + 0.2 + np.random.normal(0, perf_noise))), 1)
            )
            
            # Objective Performance Measures
            # Turnover growth percentage (correlated with subjective measures)
            base_growth = (performance_base - 2.5) * 10  # Convert to percentage
            turnover_growth = round(base_growth + np.random.normal(0, 5), 1)
            self.data.setdefault('objective_turnover_growth_percent', []).append(turnover_growth)
            
            # Profit margin (percentage)
            profit_margin = max(0, min(40, 15 + (performance_base - 2.5) * 5 + np.random.normal(0, 3)))
            self.data.setdefault('objective_profit_margin_percent', []).append(round(profit_margin, 1))
            
            # Employee growth rate
            emp_growth = max(-20, min(50, base_growth * 0.7 + np.random.normal(0, 3)))
            self.data.setdefault('objective_employee_growth_percent', []).append(round(emp_growth, 1))
            
            # Number of new branches/clients
            if self.data['num_employees'][i] > 20:
                new_branches = max(0, int(performance_base - 2 + np.random.normal(0, 1)))
            else:
                new_branches = 0
            self.data.setdefault('objective_new_branches', []).append(new_branches)
            
            new_clients = max(0, int((performance_base - 1) * 10 + np.random.normal(0, 5)))
            self.data.setdefault('objective_new_clients', []).append(new_clients)
            
            # Non-Financial Growth Indicators
            self.data.setdefault('growth_product_lines_increase', []).append(
                round(min(5, max(1, performance_base + np.random.normal(0, 0.5))), 1)
            )
            self.data.setdefault('growth_quality_improvement', []).append(
                round(min(5, max(1, performance_base + 0.3 + np.random.normal(0, 0.4))), 1)
            )
            self.data.setdefault('growth_customer_satisfaction', []).append(
                round(min(5, max(1, performance_base + 0.4 + np.random.normal(0, 0.4))), 1)
            )
            self.data.setdefault('growth_customer_retention_rate', []).append(
                round(min(100, max(20, 60 + (performance_base - 2.5) * 15 + np.random.normal(0, 8))), 1)
            )
            
    def add_calculated_features(self):
        """Add calculated features and composite scores"""
        print("Adding calculated features and composite scores...")
        
        df = pd.DataFrame(self.data)
        
        # Innovation Composite Scores
        tech_cols = [col for col in df.columns if 'digital_tools_' in col or 'advanced_tech_' in col]
        df['innovation_technology_score'] = df[tech_cols].mean(axis=1).round(2)
        
        process_cols = [col for col in df.columns if 'process_' in col]
        df['innovation_process_score'] = df[process_cols].mean(axis=1).round(2)
        
        product_cols = [col for col in df.columns if 'product_' in col]
        df['innovation_product_score'] = df[product_cols].mean(axis=1).round(2)
        
        biz_cols = [col for col in df.columns if 'business_model_' in col]
        df['innovation_business_model_score'] = df[biz_cols].mean(axis=1).round(2)
        
        # Overall Innovation Score
        df['innovation_overall_score'] = df[['innovation_technology_score', 'innovation_process_score',
                                             'innovation_product_score', 'innovation_business_model_score']].mean(axis=1).round(2)
        
        # Constraint Composite Scores
        financial_cols = [col for col in df.columns if 'constraint_' in col and ('credit' in col or 'cost' in col or 'capital' in col)]
        df['constraint_financial_score'] = df[financial_cols].mean(axis=1).round(2)
        
        human_cols = [col for col in df.columns if 'constraint_' in col and ('employee' in col or 'training' in col or 'management' in col)]
        df['constraint_human_capital_score'] = df[human_cols].mean(axis=1).round(2)
        
        infra_cols = [col for col in df.columns if 'constraint_' in col and ('electricity' in col or 'internet' in col or 'logistics' in col)]
        df['constraint_infrastructure_score'] = df[infra_cols].mean(axis=1).round(2)
        
        reg_cols = [col for col in df.columns if 'constraint_' in col and ('regulation' in col or 'corruption' in col or 'government' in col)]
        df['constraint_regulatory_score'] = df[reg_cols].mean(axis=1).round(2)
        
        market_cols = [col for col in df.columns if 'constraint_' in col and ('competition' in col or 'demand' in col or 'international' in col)]
        df['constraint_market_score'] = df[market_cols].mean(axis=1).round(2)
        
        # Overall Constraint Score
        df['constraint_overall_score'] = df[['constraint_financial_score', 'constraint_human_capital_score',
                                             'constraint_infrastructure_score', 'constraint_regulatory_score',
                                             'constraint_market_score']].mean(axis=1).round(2)
        
        # Performance Composite Score
        perf_cols = [col for col in df.columns if 'performance_' in col and 'growth' in col]
        df['performance_subjective_score'] = df[perf_cols].mean(axis=1).round(2)
        
        # Add survey metadata
        df['survey_date'] = pd.to_datetime('2024-01-15') + pd.to_timedelta(np.random.randint(0, 90, size=len(df)), unit='D')
        df['survey_response_time_minutes'] = np.random.normal(45, 10, size=len(df)).round(0).astype(int)
        df['data_quality_score'] = np.random.beta(8, 2, size=len(df)).round(2)  # Most data is high quality
        
        return df
    
    def generate_complete_dataset(self):
        """Generate the complete dataset"""
        print(f"\n{'='*60}")
        print(f"Generating Nigerian SME Innovation Dataset")
        print(f"Number of samples: {self.n_samples}")
        print(f"{'='*60}\n")
        
        # Generate all sections
        self.generate_firmographics()
        self.generate_innovation_adoption()
        self.generate_constraints()
        self.generate_performance()
        
        # Add calculated features and create dataframe
        df = self.add_calculated_features()
        
        print(f"\nDataset generation complete!")
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.shape[1]}")
        print(f"Rows: {df.shape[0]}")
        
        return df

def save_dataset(df, base_path='/workspace/nigerian_sme_innovation_dataset/data/'):
    """Save the dataset in multiple formats"""
    print(f"\n{'='*60}")
    print("Saving dataset...")
    
    # Save as CSV
    csv_path = f"{base_path}nigerian_sme_innovation_data.csv"
    df.to_csv(csv_path, index=False)
    print(f"✓ Saved to CSV: {csv_path}")
    
    # Save as Excel with multiple sheets
    excel_path = f"{base_path}nigerian_sme_innovation_data.xlsx"
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Main data
        df.to_excel(writer, sheet_name='Main_Dataset', index=False)
        
        # Summary statistics
        summary_stats = df.describe().T
        summary_stats.to_excel(writer, sheet_name='Summary_Statistics')
        
        # Data dictionary sample
        data_dict = pd.DataFrame({
            'Variable': df.columns[:10],
            'Type': [df[col].dtype for col in df.columns[:10]],
            'Description': [
                'Unique firm identifier',
                'Nigerian state location',
                'Geopolitical zone',
                'Urban or Rural location',
                'Industry sector (ISIC classification)',
                'Years in operation',
                'Total full-time employees',
                'Annual revenue in millions of Naira',
                'Business legal structure',
                'Age of owner/manager'
            ]
        })
        data_dict.to_excel(writer, sheet_name='Data_Dictionary_Sample', index=False)
    
    print(f"✓ Saved to Excel: {excel_path}")
    
    # Save as Parquet for efficient storage (if available)
    try:
        parquet_path = f"{base_path}nigerian_sme_innovation_data.parquet"
        df.to_parquet(parquet_path, index=False)
        print(f"✓ Saved to Parquet: {parquet_path}")
    except ImportError:
        print("⚠ Parquet format skipped (pyarrow not installed)")
    
    # Create a sample dataset (first 100 records)
    sample_df = df.head(100)
    sample_path = f"{base_path}nigerian_sme_innovation_sample.csv"
    sample_df.to_csv(sample_path, index=False)
    print(f"✓ Saved sample data: {sample_path}")
    
    print(f"{'='*60}\n")
    
    return df

def generate_summary_report(df):
    """Generate a summary report of the dataset"""
    report = []
    report.append("\n" + "="*60)
    report.append("NIGERIAN SME INNOVATION DATASET - SUMMARY REPORT")
    report.append("="*60 + "\n")
    
    report.append("1. DATASET OVERVIEW")
    report.append("-"*40)
    report.append(f"Total Records: {len(df):,}")
    report.append(f"Total Variables: {len(df.columns)}")
    report.append(f"Date Range: {df['survey_date'].min().date()} to {df['survey_date'].max().date()}\n")
    
    report.append("2. GEOGRAPHIC DISTRIBUTION")
    report.append("-"*40)
    for zone, count in df['geo_political_zone'].value_counts().items():
        report.append(f"{zone}: {count:,} ({count/len(df)*100:.1f}%)")
    report.append("")
    
    report.append("3. INDUSTRY DISTRIBUTION")
    report.append("-"*40)
    for industry, count in df['industry_sector'].value_counts().head(5).items():
        report.append(f"{industry}: {count:,} ({count/len(df)*100:.1f}%)")
    report.append("")
    
    report.append("4. FIRM SIZE DISTRIBUTION")
    report.append("-"*40)
    report.append(f"Micro (1-9 employees): {len(df[df['num_employees'] < 10]):,} ({len(df[df['num_employees'] < 10])/len(df)*100:.1f}%)")
    report.append(f"Small (10-49 employees): {len(df[(df['num_employees'] >= 10) & (df['num_employees'] < 50)]):,} ({len(df[(df['num_employees'] >= 10) & (df['num_employees'] < 50)])/len(df)*100:.1f}%)")
    report.append(f"Medium (50-250 employees): {len(df[df['num_employees'] >= 50]):,} ({len(df[df['num_employees'] >= 50])/len(df)*100:.1f}%)\n")
    
    report.append("5. KEY INNOVATION METRICS (Mean Scores, Scale 1-5)")
    report.append("-"*40)
    report.append(f"Overall Innovation Score: {df['innovation_overall_score'].mean():.2f} (SD: {df['innovation_overall_score'].std():.2f})")
    report.append(f"Technology Innovation: {df['innovation_technology_score'].mean():.2f}")
    report.append(f"Process Innovation: {df['innovation_process_score'].mean():.2f}")
    report.append(f"Product Innovation: {df['innovation_product_score'].mean():.2f}")
    report.append(f"Business Model Innovation: {df['innovation_business_model_score'].mean():.2f}\n")
    
    report.append("6. KEY CONSTRAINT METRICS (Mean Scores, Scale 1-5)")
    report.append("-"*40)
    report.append(f"Overall Constraint Score: {df['constraint_overall_score'].mean():.2f} (SD: {df['constraint_overall_score'].std():.2f})")
    report.append(f"Financial Constraints: {df['constraint_financial_score'].mean():.2f}")
    report.append(f"Human Capital Constraints: {df['constraint_human_capital_score'].mean():.2f}")
    report.append(f"Infrastructure Constraints: {df['constraint_infrastructure_score'].mean():.2f}")
    report.append(f"Regulatory Constraints: {df['constraint_regulatory_score'].mean():.2f}")
    report.append(f"Market Constraints: {df['constraint_market_score'].mean():.2f}\n")
    
    report.append("7. PERFORMANCE METRICS")
    report.append("-"*40)
    report.append(f"Subjective Performance Score: {df['performance_subjective_score'].mean():.2f} (SD: {df['performance_subjective_score'].std():.2f})")
    report.append(f"Average Turnover Growth: {df['objective_turnover_growth_percent'].mean():.1f}%")
    report.append(f"Average Profit Margin: {df['objective_profit_margin_percent'].mean():.1f}%")
    report.append(f"Average Employee Growth: {df['objective_employee_growth_percent'].mean():.1f}%")
    report.append(f"Customer Retention Rate: {df['growth_customer_retention_rate'].mean():.1f}%\n")
    
    report.append("8. DATA QUALITY METRICS")
    report.append("-"*40)
    report.append(f"Average Data Quality Score: {df['data_quality_score'].mean():.2f}")
    report.append(f"Average Survey Response Time: {df['survey_response_time_minutes'].mean():.1f} minutes")
    report.append(f"Missing Values: {df.isnull().sum().sum()} ({df.isnull().sum().sum()/(len(df)*len(df.columns))*100:.2f}%)\n")
    
    report.append("="*60)
    
    return "\n".join(report)

if __name__ == "__main__":
    # Initialize generator with 5000 samples
    generator = NigerianSMEDataGenerator(n_samples=5000)
    
    # Generate the complete dataset
    df = generator.generate_complete_dataset()
    
    # Save in multiple formats
    df = save_dataset(df)
    
    # Generate and print summary report
    summary = generate_summary_report(df)
    print(summary)
    
    # Save summary report
    with open('/workspace/nigerian_sme_innovation_dataset/data/dataset_summary_report.txt', 'w') as f:
        f.write(summary)
    
    print("\n✓ Summary report saved to: dataset_summary_report.txt")
    print("\n🎉 Dataset generation complete! All files saved successfully.")