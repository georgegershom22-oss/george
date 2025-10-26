#!/usr/bin/env python3
"""
Banking Security Behavior Dataset Generator
===========================================

This script generates a comprehensive dataset for banking security behavior research,
focusing on the Theory of Planned Behavior and the intention-behavior gap.

The dataset includes:
- Time 1 (T1) Variables: Intentions, Attitudes, Subjective Norms, Perceived Behavioral Control
- Time 2 (T2) Variables: Self-Reported Behavior, Objective Behavioral Measures, Behavioral Gap
- Demographics and Control Variables
- Realistic correlations and distributions based on behavioral research

Author: AI Assistant
Date: 2025-10-26
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
from scipy.stats import multivariate_normal
import random
from datetime import datetime, timedelta
import json

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

class BankingSecurityDatasetGenerator:
    def __init__(self, n_participants=1200):
        self.n = n_participants
        self.data = {}
        
    def generate_demographics(self):
        """Generate realistic demographic variables"""
        print("Generating demographic variables...")
        
        # Age (18-75, slightly skewed toward younger adults)
        age_dist = stats.skewnorm(a=-1, loc=40, scale=15)
        ages = np.clip(age_dist.rvs(self.n), 18, 75).astype(int)
        
        # Gender (roughly balanced with some non-binary)
        gender_probs = [0.48, 0.49, 0.03]  # Female, Male, Non-binary/Other
        genders = np.random.choice(['Female', 'Male', 'Non-binary/Other'], 
                                 size=self.n, p=gender_probs)
        
        # Education (1=Less than high school to 7=Doctoral degree)
        education_probs = [0.05, 0.15, 0.25, 0.30, 0.15, 0.08, 0.02]
        education = np.random.choice(range(1, 8), size=self.n, p=education_probs)
        
        # Income (1=<$25k to 8=>$150k)
        income_probs = [0.12, 0.18, 0.20, 0.18, 0.15, 0.10, 0.05, 0.02]
        income = np.random.choice(range(1, 9), size=self.n, p=income_probs)
        
        # Tech savviness (1=Very low to 7=Very high)
        tech_savvy = np.random.normal(4.2, 1.3, self.n)
        tech_savvy = np.clip(np.round(tech_savvy), 1, 7).astype(int)
        
        # Banking frequency (1=Rarely to 7=Multiple times daily)
        banking_freq = np.random.normal(4.8, 1.2, self.n)
        banking_freq = np.clip(np.round(banking_freq), 1, 7).astype(int)
        
        # Previous security incidents (0=None, 1=Minor, 2=Major)
        incident_probs = [0.70, 0.25, 0.05]
        prev_incidents = np.random.choice([0, 1, 2], size=self.n, p=incident_probs)
        
        self.data.update({
            'participant_id': [f'P{i:04d}' for i in range(1, self.n + 1)],
            'age': ages,
            'gender': genders,
            'education': education,
            'income': income,
            'tech_savviness': tech_savvy,
            'banking_frequency': banking_freq,
            'previous_incidents': prev_incidents
        })
        
    def generate_t1_variables(self):
        """Generate Time 1 variables (TPB constructs)"""
        print("Generating Time 1 (T1) TPB variables...")
        
        # Create correlation matrix for TPB constructs
        # Based on meta-analyses: attitudes-intentions (r≈.5), PBC-intentions (r≈.4), etc.
        constructs = ['attitudes', 'subjective_norms', 'pbc', 'intentions']
        corr_matrix = np.array([
            [1.00, 0.35, 0.42, 0.52],  # Attitudes
            [0.35, 1.00, 0.28, 0.38],  # Subjective Norms  
            [0.42, 0.28, 1.00, 0.45],  # PBC
            [0.52, 0.38, 0.45, 1.00]   # Intentions
        ])
        
        # Generate correlated data
        means = [5.1, 4.8, 4.6, 5.3]  # Slightly above midpoint (4) for security behaviors
        stds = [1.2, 1.3, 1.4, 1.1]
        
        # Generate multivariate normal data
        mvn_data = multivariate_normal.rvs(mean=means, cov=np.outer(stds, stds) * corr_matrix, size=self.n)
        
        # Clip to 1-7 scale and round
        for i, construct in enumerate(constructs):
            values = np.clip(np.round(mvn_data[:, i]), 1, 7).astype(int)
            
            # Generate individual items for each construct (3 items each)
            for j in range(1, 4):
                # Add some item-level noise while maintaining construct reliability
                item_noise = np.random.normal(0, 0.3, self.n)
                item_values = values + item_noise
                item_values = np.clip(np.round(item_values), 1, 7).astype(int)
                self.data[f't1_{construct}_{j}'] = item_values
                
            # Store construct mean
            construct_mean = np.mean([self.data[f't1_{construct}_{j}'] for j in range(1, 4)], axis=0)
            self.data[f't1_{construct}_mean'] = construct_mean
            
    def generate_srb_variables(self):
        """Generate Self-Reported Behavior (SRB) variables"""
        print("Generating Self-Reported Behavior (SRB) variables...")
        
        # SRB items as specified
        srb_items = [
            'check_statements',      # Check bank statements for unauthorized transactions
            'strong_passwords',      # Use strong, unique passwords for banking
            'two_factor_auth',      # Enable two-factor authentication
            'logout_properly',      # Log out of banking apps/sites after use
            'verify_alerts'         # Verify text/email alerts before clicking links
        ]
        
        # Generate SRB based on intentions with some noise and individual differences
        intentions_mean = self.data['t1_intentions_mean']
        
        for i, item in enumerate(srb_items):
            # Base behavior on intentions but add noise and individual variation
            base_behavior = intentions_mean + np.random.normal(0, 0.8, self.n)
            
            # Some behaviors are easier/harder than others
            difficulty_adjustments = [0.2, -0.3, -0.8, 0.1, -0.2]  # Relative difficulty
            base_behavior += difficulty_adjustments[i]
            
            # Add influence from PBC (stronger for more difficult behaviors)
            pbc_influence = [0.1, 0.3, 0.5, 0.1, 0.3]
            pbc_mean = self.data['t1_pbc_mean']
            base_behavior += pbc_influence[i] * (pbc_mean - 4)  # Center PBC around midpoint
            
            # Clip and round to 1-7 scale
            behavior_values = np.clip(np.round(base_behavior), 1, 7).astype(int)
            self.data[f'srb_{i+1}_{item}'] = behavior_values
            
        # Calculate overall SRB mean
        srb_means = np.mean([self.data[f'srb_{i+1}_{item}'] for i, item in enumerate(srb_items)], axis=0)
        self.data['srb_total_mean'] = srb_means
        
    def generate_objective_scenarios(self):
        """Generate objective behavioral measure scenarios"""
        print("Generating objective behavioral measure scenarios...")
        
        # Define 5 security scenarios with scoring
        scenarios = [
            {
                'name': 'phishing_sms',
                'description': 'SMS: "Your account is locked. Click here to secure it: bit.ly/secure123"',
                'options': {
                    'click_immediately': 0,
                    'ignore_message': 1, 
                    'call_bank_official': 2,
                    'report_as_spam': 2
                }
            },
            {
                'name': 'fake_email',
                'description': 'Email from "your bank" asking to update personal information via link',
                'options': {
                    'click_and_update': 0,
                    'forward_to_friend': 0,
                    'delete_email': 1,
                    'verify_with_bank': 2,
                    'report_phishing': 2
                }
            },
            {
                'name': 'public_wifi',
                'description': 'Need to check bank balance while on public WiFi at coffee shop',
                'options': {
                    'use_public_wifi': 0,
                    'wait_until_home': 2,
                    'use_mobile_data': 2,
                    'ask_for_password': 1
                }
            },
            {
                'name': 'password_sharing',
                'description': 'Family member asks for your banking password to help with finances',
                'options': {
                    'share_password': 0,
                    'log_in_for_them': 1,
                    'refuse_completely': 2,
                    'create_joint_account': 2
                }
            },
            {
                'name': 'suspicious_charge',
                'description': 'Notice unfamiliar $50 charge on bank statement',
                'options': {
                    'ignore_small_amount': 0,
                    'ask_family_members': 1,
                    'contact_bank_immediately': 2,
                    'wait_and_see': 0
                }
            }
        ]
        
        total_scores = []
        
        for participant in range(self.n):
            participant_score = 0
            
            # Participant's general security knowledge/behavior influences responses
            base_competency = (
                0.3 * self.data['t1_pbc_mean'][participant] +
                0.2 * self.data['tech_savviness'][participant] +
                0.2 * self.data['srb_total_mean'][participant] +
                0.3 * np.random.normal(4, 1)  # Random component
            )
            
            for i, scenario in enumerate(scenarios):
                # Probability of choosing each option based on competency
                option_scores = list(scenario['options'].values())
                max_score = max(option_scores)
                
                # Higher competency = higher probability of best choice
                competency_factor = (base_competency - 1) / 6  # Normalize to 0-1
                
                # Create probability weights favoring higher-scoring options
                weights = []
                for score in option_scores:
                    if score == max_score:
                        weight = 0.4 + 0.4 * competency_factor  # 40-80% chance for best option
                    elif score == 1:
                        weight = 0.3 * (1 - competency_factor)  # Decreases with competency
                    else:  # score == 0
                        weight = 0.3 * (1 - competency_factor)  # Decreases with competency
                    weights.append(weight)
                
                # Normalize weights
                weights = np.array(weights) / sum(weights)
                
                # Choose option and add score
                chosen_idx = np.random.choice(len(option_scores), p=weights)
                participant_score += option_scores[chosen_idx]
                
                # Store individual scenario responses
                option_names = list(scenario['options'].keys())
                self.data[f'obj_scenario_{i+1}_{scenario["name"]}'] = [option_names[chosen_idx] if j == participant else None for j in range(self.n)]
                self.data[f'obj_score_{i+1}_{scenario["name"]}'] = [option_scores[chosen_idx] if j == participant else None for j in range(self.n)]
            
            total_scores.append(participant_score)
        
        # Clean up individual scenario data (fill None values properly)
        for i, scenario in enumerate(scenarios):
            option_names = list(scenario['options'].keys())
            option_scores = list(scenario['options'].values())
            
            responses = []
            scores = []
            
            for participant in range(self.n):
                base_competency = (
                    0.3 * self.data['t1_pbc_mean'][participant] +
                    0.2 * self.data['tech_savviness'][participant] +
                    0.2 * self.data['srb_total_mean'][participant] +
                    0.3 * np.random.normal(4, 1)
                )
                
                competency_factor = (base_competency - 1) / 6
                max_score = max(option_scores)
                
                weights = []
                for score in option_scores:
                    if score == max_score:
                        weight = 0.4 + 0.4 * competency_factor
                    elif score == 1:
                        weight = 0.3 * (1 - competency_factor)
                    else:
                        weight = 0.3 * (1 - competency_factor)
                    weights.append(weight)
                
                weights = np.array(weights) / sum(weights)
                chosen_idx = np.random.choice(len(option_scores), p=weights)
                
                responses.append(option_names[chosen_idx])
                scores.append(option_scores[chosen_idx])
            
            self.data[f'obj_scenario_{i+1}_{scenario["name"]}'] = responses
            self.data[f'obj_score_{i+1}_{scenario["name"]}'] = scores
        
        self.data['objective_total_score'] = total_scores
        
    def calculate_behavioral_gap(self):
        """Calculate the intention-behavior gap using regression residuals"""
        print("Calculating intention-behavior gap...")
        
        intentions = np.array(self.data['t1_intentions_mean'])
        behavior = np.array(self.data['srb_total_mean'])
        
        # Perform regression: behavior ~ intentions
        X = np.column_stack([np.ones(self.n), intentions])  # Add intercept
        beta = np.linalg.lstsq(X, behavior, rcond=None)[0]
        
        # Calculate predicted values and residuals
        predicted = X @ beta
        residuals = behavior - predicted
        
        # Store results
        self.data['predicted_behavior'] = predicted
        self.data['intention_behavior_gap'] = residuals
        
        # Categorize gap for interpretation
        gap_categories = []
        for residual in residuals:
            if residual > 0.5:
                gap_categories.append('Over-performer')
            elif residual < -0.5:
                gap_categories.append('Under-performer')
            else:
                gap_categories.append('As expected')
        
        self.data['gap_category'] = gap_categories
        
        # Store regression statistics
        self.regression_stats = {
            'intercept': beta[0],
            'slope': beta[1],
            'r_squared': np.corrcoef(intentions, behavior)[0, 1] ** 2,
            'residual_std': np.std(residuals)
        }
        
    def add_control_variables(self):
        """Add additional control variables for comprehensive analysis"""
        print("Adding control variables...")
        
        # Risk perception (1=Very low to 7=Very high)
        risk_perception = np.random.normal(4.8, 1.2, self.n)
        risk_perception = np.clip(np.round(risk_perception), 1, 7).astype(int)
        
        # Trust in bank security (1=Very low to 7=Very high)
        bank_trust = np.random.normal(5.2, 1.1, self.n)
        bank_trust = np.clip(np.round(bank_trust), 1, 7).astype(int)
        
        # Security self-efficacy (1=Very low to 7=Very high)
        security_efficacy = np.random.normal(4.5, 1.3, self.n)
        security_efficacy = np.clip(np.round(security_efficacy), 1, 7).astype(int)
        
        # Time since last security training (months)
        training_recency = np.random.exponential(8, self.n)  # Exponential distribution
        training_recency = np.clip(training_recency, 0, 60).astype(int)
        
        # Device type primarily used for banking
        device_probs = [0.15, 0.60, 0.20, 0.05]  # Desktop, Mobile, Tablet, Multiple
        device_types = np.random.choice(['Desktop', 'Mobile', 'Tablet', 'Multiple'], 
                                      size=self.n, p=device_probs)
        
        self.data.update({
            'risk_perception': risk_perception,
            'bank_trust': bank_trust,
            'security_self_efficacy': security_efficacy,
            'months_since_training': training_recency,
            'primary_device': device_types
        })
        
    def add_temporal_variables(self):
        """Add temporal variables to simulate longitudinal data collection"""
        print("Adding temporal variables...")
        
        # T1 data collection dates (spread over 2 months)
        start_date = datetime(2024, 9, 1)
        t1_dates = []
        for _ in range(self.n):
            days_offset = np.random.randint(0, 60)  # 2 months
            t1_date = start_date + timedelta(days=days_offset)
            t1_dates.append(t1_date.strftime('%Y-%m-%d'))
        
        # T2 data collection (4-6 weeks after T1)
        t2_dates = []
        for t1_date_str in t1_dates:
            t1_date = datetime.strptime(t1_date_str, '%Y-%m-%d')
            days_gap = np.random.randint(28, 42)  # 4-6 weeks
            t2_date = t1_date + timedelta(days=days_gap)
            t2_dates.append(t2_date.strftime('%Y-%m-%d'))
        
        # Response times (minutes to complete surveys)
        t1_response_time = np.random.gamma(2, 5, self.n)  # Gamma distribution for response times
        t1_response_time = np.clip(t1_response_time, 3, 45).astype(int)
        
        t2_response_time = np.random.gamma(2, 4, self.n)  # Slightly faster for T2
        t2_response_time = np.clip(t2_response_time, 2, 35).astype(int)
        
        self.data.update({
            't1_date': t1_dates,
            't2_date': t2_dates,
            't1_response_time_minutes': t1_response_time,
            't2_response_time_minutes': t2_response_time
        })
        
    def generate_missing_data(self):
        """Introduce realistic patterns of missing data"""
        print("Introducing realistic missing data patterns...")
        
        # Create missing data patterns (MCAR, MAR, MNAR)
        missing_prob_base = 0.05  # 5% base missing rate
        
        # Some participants drop out between T1 and T2
        dropout_prob = 0.12  # 12% dropout rate
        dropouts = np.random.choice([True, False], size=self.n, p=[dropout_prob, 1-dropout_prob])
        
        # Apply dropout to all T2 variables
        t2_vars = [col for col in self.data.keys() if col.startswith(('srb_', 'obj_', 'intention_behavior_gap', 'predicted_behavior', 'gap_category', 't2_'))]
        
        for var in t2_vars:
            if var in self.data:
                values = self.data[var].copy() if isinstance(self.data[var], list) else list(self.data[var])
                for i, dropout in enumerate(dropouts):
                    if dropout:
                        values[i] = np.nan if isinstance(values[i], (int, float)) else 'Missing'
                self.data[var] = values
        
        # Additional random missing for some variables (MAR pattern)
        sensitive_vars = ['income', 'previous_incidents']
        for var in sensitive_vars:
            if var in self.data:
                additional_missing = np.random.choice([True, False], size=self.n, 
                                                    p=[missing_prob_base * 2, 1 - missing_prob_base * 2])
                values = list(self.data[var])
                for i, missing in enumerate(additional_missing):
                    if missing and not dropouts[i]:  # Don't double-mark dropouts
                        values[i] = np.nan if isinstance(values[i], (int, float)) else 'Missing'
                self.data[var] = values
                
    def generate_dataset(self):
        """Generate the complete dataset"""
        print("Starting dataset generation...")
        print(f"Target sample size: {self.n} participants")
        
        # Generate all components
        self.generate_demographics()
        self.generate_t1_variables()
        self.generate_srb_variables()
        self.generate_objective_scenarios()
        self.calculate_behavioral_gap()
        self.add_control_variables()
        self.add_temporal_variables()
        self.generate_missing_data()
        
        # Create DataFrame
        df = pd.DataFrame(self.data)
        
        print(f"Dataset generated successfully!")
        print(f"Final dataset shape: {df.shape}")
        print(f"Variables included: {len(df.columns)}")
        
        return df
    
    def generate_codebook(self):
        """Generate comprehensive codebook/data dictionary"""
        codebook = {
            "dataset_info": {
                "title": "Banking Security Behavior Dataset",
                "description": "Longitudinal dataset examining the intention-behavior gap in banking security behaviors using Theory of Planned Behavior",
                "sample_size": self.n,
                "time_points": 2,
                "collection_period": "September-December 2024",
                "missing_data": "Multiple patterns: MCAR, MAR, and dropout"
            },
            "variables": {
                # Demographics
                "participant_id": {"type": "string", "description": "Unique participant identifier", "values": "P0001-P9999"},
                "age": {"type": "integer", "description": "Age in years", "range": "18-75"},
                "gender": {"type": "categorical", "description": "Gender identity", "values": ["Female", "Male", "Non-binary/Other"]},
                "education": {"type": "ordinal", "description": "Highest education level", "scale": "1=Less than high school to 7=Doctoral degree"},
                "income": {"type": "ordinal", "description": "Annual household income", "scale": "1=<$25k to 8=>$150k"},
                "tech_savviness": {"type": "ordinal", "description": "Self-reported technology proficiency", "scale": "1=Very low to 7=Very high"},
                "banking_frequency": {"type": "ordinal", "description": "Frequency of online/mobile banking use", "scale": "1=Rarely to 7=Multiple times daily"},
                "previous_incidents": {"type": "ordinal", "description": "Previous security incidents", "values": "0=None, 1=Minor, 2=Major"},
                
                # Time 1 Variables (TPB Constructs)
                "t1_attitudes_1": {"type": "ordinal", "description": "Attitudes toward banking security - Item 1", "scale": "1=Strongly disagree to 7=Strongly agree"},
                "t1_attitudes_2": {"type": "ordinal", "description": "Attitudes toward banking security - Item 2", "scale": "1=Strongly disagree to 7=Strongly agree"},
                "t1_attitudes_3": {"type": "ordinal", "description": "Attitudes toward banking security - Item 3", "scale": "1=Strongly disagree to 7=Strongly agree"},
                "t1_attitudes_mean": {"type": "continuous", "description": "Mean of attitudes items", "range": "1-7"},
                
                "t1_subjective_norms_1": {"type": "ordinal", "description": "Subjective norms - Item 1", "scale": "1=Strongly disagree to 7=Strongly agree"},
                "t1_subjective_norms_2": {"type": "ordinal", "description": "Subjective norms - Item 2", "scale": "1=Strongly disagree to 7=Strongly agree"},
                "t1_subjective_norms_3": {"type": "ordinal", "description": "Subjective norms - Item 3", "scale": "1=Strongly disagree to 7=Strongly agree"},
                "t1_subjective_norms_mean": {"type": "continuous", "description": "Mean of subjective norms items", "range": "1-7"},
                
                "t1_pbc_1": {"type": "ordinal", "description": "Perceived Behavioral Control - Item 1", "scale": "1=Strongly disagree to 7=Strongly agree"},
                "t1_pbc_2": {"type": "ordinal", "description": "Perceived Behavioral Control - Item 2", "scale": "1=Strongly disagree to 7=Strongly agree"},
                "t1_pbc_3": {"type": "ordinal", "description": "Perceived Behavioral Control - Item 3", "scale": "1=Strongly disagree to 7=Strongly agree"},
                "t1_pbc_mean": {"type": "continuous", "description": "Mean of PBC items", "range": "1-7"},
                
                "t1_intentions_1": {"type": "ordinal", "description": "Behavioral intentions - Item 1", "scale": "1=Strongly disagree to 7=Strongly agree"},
                "t1_intentions_2": {"type": "ordinal", "description": "Behavioral intentions - Item 2", "scale": "1=Strongly disagree to 7=Strongly agree"},
                "t1_intentions_3": {"type": "ordinal", "description": "Behavioral intentions - Item 3", "scale": "1=Strongly disagree to 7=Strongly agree"},
                "t1_intentions_mean": {"type": "continuous", "description": "Mean of intentions items", "range": "1-7"},
                
                # Time 2 Variables - Self-Reported Behavior
                "srb_1_check_statements": {"type": "ordinal", "description": "How often: Check bank statements for unauthorized transactions", "scale": "1=Never to 7=Always"},
                "srb_2_strong_passwords": {"type": "ordinal", "description": "How often: Use strong, unique passwords for banking", "scale": "1=Never to 7=Always"},
                "srb_3_two_factor_auth": {"type": "ordinal", "description": "How often: Enable two-factor authentication", "scale": "1=Never to 7=Always"},
                "srb_4_logout_properly": {"type": "ordinal", "description": "How often: Log out of banking apps/sites after use", "scale": "1=Never to 7=Always"},
                "srb_5_verify_alerts": {"type": "ordinal", "description": "How often: Verify text/email alerts before clicking links", "scale": "1=Never to 7=Always"},
                "srb_total_mean": {"type": "continuous", "description": "Mean of all SRB items", "range": "1-7"},
                
                # Objective Behavioral Measures
                "objective_total_score": {"type": "integer", "description": "Total score on objective security scenarios", "range": "0-10"},
                
                # Behavioral Gap Variables
                "predicted_behavior": {"type": "continuous", "description": "Predicted behavior based on T1 intentions", "range": "1-7"},
                "intention_behavior_gap": {"type": "continuous", "description": "Residual score: actual - predicted behavior"},
                "gap_category": {"type": "categorical", "description": "Categorized gap", "values": ["Under-performer", "As expected", "Over-performer"]},
                
                # Control Variables
                "risk_perception": {"type": "ordinal", "description": "Perceived risk of banking security threats", "scale": "1=Very low to 7=Very high"},
                "bank_trust": {"type": "ordinal", "description": "Trust in bank's security measures", "scale": "1=Very low to 7=Very high"},
                "security_self_efficacy": {"type": "ordinal", "description": "Confidence in personal security abilities", "scale": "1=Very low to 7=Very high"},
                "months_since_training": {"type": "integer", "description": "Months since last security training", "range": "0-60"},
                "primary_device": {"type": "categorical", "description": "Primary device for banking", "values": ["Desktop", "Mobile", "Tablet", "Multiple"]},
                
                # Temporal Variables
                "t1_date": {"type": "date", "description": "Date of Time 1 data collection", "format": "YYYY-MM-DD"},
                "t2_date": {"type": "date", "description": "Date of Time 2 data collection", "format": "YYYY-MM-DD"},
                "t1_response_time_minutes": {"type": "integer", "description": "Time to complete T1 survey (minutes)", "range": "3-45"},
                "t2_response_time_minutes": {"type": "integer", "description": "Time to complete T2 survey (minutes)", "range": "2-35"}
            },
            "objective_scenarios": {
                "scenario_1_phishing_sms": {
                    "description": "SMS phishing scenario",
                    "prompt": "You receive this SMS: 'Your account is locked. Click here to secure it: bit.ly/secure123'",
                    "options": {
                        "click_immediately": {"score": 0, "description": "Click the link immediately"},
                        "ignore_message": {"score": 1, "description": "Ignore the message"},
                        "call_bank_official": {"score": 2, "description": "Call bank using official number"},
                        "report_as_spam": {"score": 2, "description": "Report as spam/phishing"}
                    }
                },
                "scenario_2_fake_email": {
                    "description": "Email phishing scenario",
                    "prompt": "Email from 'your bank' asking to update personal information via link",
                    "options": {
                        "click_and_update": {"score": 0, "description": "Click link and update info"},
                        "forward_to_friend": {"score": 0, "description": "Forward to friend for advice"},
                        "delete_email": {"score": 1, "description": "Delete the email"},
                        "verify_with_bank": {"score": 2, "description": "Verify with bank first"},
                        "report_phishing": {"score": 2, "description": "Report as phishing"}
                    }
                },
                "scenario_3_public_wifi": {
                    "description": "Public WiFi banking scenario",
                    "prompt": "Need to check bank balance while on public WiFi at coffee shop",
                    "options": {
                        "use_public_wifi": {"score": 0, "description": "Use public WiFi"},
                        "wait_until_home": {"score": 2, "description": "Wait until home"},
                        "use_mobile_data": {"score": 2, "description": "Use mobile data instead"},
                        "ask_for_password": {"score": 1, "description": "Ask for WiFi password"}
                    }
                },
                "scenario_4_password_sharing": {
                    "description": "Password sharing scenario",
                    "prompt": "Family member asks for your banking password to help with finances",
                    "options": {
                        "share_password": {"score": 0, "description": "Share the password"},
                        "log_in_for_them": {"score": 1, "description": "Log in for them"},
                        "refuse_completely": {"score": 2, "description": "Refuse completely"},
                        "create_joint_account": {"score": 2, "description": "Suggest joint account"}
                    }
                },
                "scenario_5_suspicious_charge": {
                    "description": "Suspicious charge scenario",
                    "prompt": "Notice unfamiliar $50 charge on bank statement",
                    "options": {
                        "ignore_small_amount": {"score": 0, "description": "Ignore small amount"},
                        "ask_family_members": {"score": 1, "description": "Ask family members"},
                        "contact_bank_immediately": {"score": 2, "description": "Contact bank immediately"},
                        "wait_and_see": {"score": 0, "description": "Wait and see"}
                    }
                }
            },
            "analysis_notes": {
                "intention_behavior_gap": "Calculated as unstandardized residuals from regression: SRB_mean ~ Intentions_mean",
                "missing_data_patterns": {
                    "dropout": "12% dropout between T1 and T2",
                    "item_nonresponse": "5% base rate, higher for sensitive items",
                    "mechanisms": "Combination of MCAR, MAR, and MNAR patterns"
                },
                "recommended_analyses": [
                    "Descriptive statistics and correlations",
                    "Regression analysis: Intentions predicting behavior",
                    "Moderation analysis: PBC moderating intention-behavior relationship",
                    "Mediation analysis: Gap mediating PBC effects",
                    "Missing data analysis using multiple imputation"
                ]
            }
        }
        
        return codebook

def main():
    """Main function to generate and save the dataset"""
    print("=" * 60)
    print("BANKING SECURITY BEHAVIOR DATASET GENERATOR")
    print("=" * 60)
    
    # Initialize generator
    generator = BankingSecurityDatasetGenerator(n_participants=1200)
    
    # Generate dataset
    df = generator.generate_dataset()
    
    # Generate codebook
    codebook = generator.generate_codebook()
    
    # Save files
    print("\nSaving dataset files...")
    
    # Save main dataset
    df.to_csv('/workspace/banking_security_dataset.csv', index=False)
    print("✓ Saved: banking_security_dataset.csv")
    
    # Save codebook as JSON
    with open('/workspace/banking_security_codebook.json', 'w') as f:
        json.dump(codebook, f, indent=2)
    print("✓ Saved: banking_security_codebook.json")
    
    # Save summary statistics
    summary_stats = {
        'dataset_shape': df.shape,
        'missing_data_summary': df.isnull().sum().to_dict(),
        'descriptive_statistics': df.describe().to_dict(),
        'regression_statistics': generator.regression_stats
    }
    
    with open('/workspace/banking_security_summary_stats.json', 'w') as f:
        json.dump(summary_stats, f, indent=2, default=str)
    print("✓ Saved: banking_security_summary_stats.json")
    
    # Create SPSS syntax file
    spss_syntax = generate_spss_syntax(df, codebook)
    with open('/workspace/banking_security_spss_syntax.sps', 'w') as f:
        f.write(spss_syntax)
    print("✓ Saved: banking_security_spss_syntax.sps")
    
    # Print summary
    print("\n" + "=" * 60)
    print("DATASET GENERATION COMPLETE")
    print("=" * 60)
    print(f"Sample size: {df.shape[0]:,} participants")
    print(f"Variables: {df.shape[1]} total")
    print(f"Missing data: {df.isnull().sum().sum():,} missing values")
    print(f"Completion rate: {(1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100:.1f}%")
    
    # Key statistics
    print(f"\nKey Statistics:")
    print(f"- Mean intentions (T1): {df['t1_intentions_mean'].mean():.2f} (SD={df['t1_intentions_mean'].std():.2f})")
    print(f"- Mean behavior (T2): {df['srb_total_mean'].mean():.2f} (SD={df['srb_total_mean'].std():.2f})")
    print(f"- Intention-behavior correlation: r={df['t1_intentions_mean'].corr(df['srb_total_mean']):.3f}")
    print(f"- Mean objective score: {df['objective_total_score'].mean():.2f} (SD={df['objective_total_score'].std():.2f})")
    
    gap_counts = df['gap_category'].value_counts()
    print(f"\nBehavioral Gap Distribution:")
    for category, count in gap_counts.items():
        print(f"- {category}: {count} ({count/len(df)*100:.1f}%)")
    
    print(f"\nFiles saved to /workspace/")
    print("Dataset is ready for analysis!")
    
    return df, codebook

def generate_spss_syntax(df, codebook):
    """Generate SPSS syntax for data import and setup"""
    syntax = """* Banking Security Behavior Dataset - SPSS Syntax
* Generated automatically - modify as needed
* 
* Import the CSV file first, then run this syntax

* Set up variable labels and value labels

"""
    
    # Variable labels
    syntax += "VARIABLE LABELS\n"
    for var, info in codebook['variables'].items():
        if var in df.columns:
            syntax += f"  {var} '{info['description']}'\n"
    syntax += ".\n\n"
    
    # Value labels for categorical variables
    categorical_vars = {
        'gender': ['Female', 'Male', 'Non-binary/Other'],
        'gap_category': ['Under-performer', 'As expected', 'Over-performer'],
        'primary_device': ['Desktop', 'Mobile', 'Tablet', 'Multiple']
    }
    
    syntax += "VALUE LABELS\n"
    for var, values in categorical_vars.items():
        if var in df.columns:
            syntax += f"  {var}\n"
            for i, value in enumerate(values, 1):
                syntax += f"    {i} '{value}'\n"
    syntax += ".\n\n"
    
    # Missing values
    syntax += "MISSING VALUES\n"
    for col in df.columns:
        if df[col].dtype in ['object', 'string']:
            syntax += f"  {col} ('Missing')\n"
    syntax += ".\n\n"
    
    # Compute scales
    syntax += "* Compute scale scores\n"
    syntax += "COMPUTE t1_attitudes_mean = MEAN(t1_attitudes_1, t1_attitudes_2, t1_attitudes_3).\n"
    syntax += "COMPUTE t1_subjective_norms_mean = MEAN(t1_subjective_norms_1, t1_subjective_norms_2, t1_subjective_norms_3).\n"
    syntax += "COMPUTE t1_pbc_mean = MEAN(t1_pbc_1, t1_pbc_2, t1_pbc_3).\n"
    syntax += "COMPUTE t1_intentions_mean = MEAN(t1_intentions_1, t1_intentions_2, t1_intentions_3).\n"
    syntax += "COMPUTE srb_total_mean = MEAN(srb_1_check_statements, srb_2_strong_passwords, srb_3_two_factor_auth, srb_4_logout_properly, srb_5_verify_alerts).\n"
    syntax += "EXECUTE.\n\n"
    
    # Reliability analysis
    syntax += "* Reliability analysis for scales\n"
    syntax += "RELIABILITY /VARIABLES=t1_attitudes_1 t1_attitudes_2 t1_attitudes_3 /SCALE('Attitudes') ALL.\n"
    syntax += "RELIABILITY /VARIABLES=t1_subjective_norms_1 t1_subjective_norms_2 t1_subjective_norms_3 /SCALE('Subjective Norms') ALL.\n"
    syntax += "RELIABILITY /VARIABLES=t1_pbc_1 t1_pbc_2 t1_pbc_3 /SCALE('PBC') ALL.\n"
    syntax += "RELIABILITY /VARIABLES=t1_intentions_1 t1_intentions_2 t1_intentions_3 /SCALE('Intentions') ALL.\n"
    syntax += "RELIABILITY /VARIABLES=srb_1_check_statements srb_2_strong_passwords srb_3_two_factor_auth srb_4_logout_properly srb_5_verify_alerts /SCALE('SRB') ALL.\n\n"
    
    # Basic analyses
    syntax += "* Basic descriptive statistics\n"
    syntax += "DESCRIPTIVES VARIABLES=age t1_attitudes_mean t1_subjective_norms_mean t1_pbc_mean t1_intentions_mean srb_total_mean objective_total_score intention_behavior_gap\n"
    syntax += "  /STATISTICS=MEAN STDDEV MIN MAX.\n\n"
    
    syntax += "* Correlations\n"
    syntax += "CORRELATIONS\n"
    syntax += "  /VARIABLES=t1_attitudes_mean t1_subjective_norms_mean t1_pbc_mean t1_intentions_mean srb_total_mean objective_total_score\n"
    syntax += "  /PRINT=TWOTAIL NOSIG\n"
    syntax += "  /MISSING=PAIRWISE.\n\n"
    
    syntax += "* Regression analysis - Intentions predicting behavior\n"
    syntax += "REGRESSION\n"
    syntax += "  /MISSING LISTWISE\n"
    syntax += "  /STATISTICS COEFF OUTS R ANOVA\n"
    syntax += "  /CRITERIA=PIN(.05) POUT(.10)\n"
    syntax += "  /NOORIGIN\n"
    syntax += "  /DEPENDENT srb_total_mean\n"
    syntax += "  /METHOD=ENTER t1_intentions_mean.\n\n"
    
    return syntax

if __name__ == "__main__":
    df, codebook = main()