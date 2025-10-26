#!/usr/bin/env python3
"""
Banking Security Dataset Generator
Generates a comprehensive dataset for Q1/SCI research on banking security behaviors
Includes T1 (baseline) and T2 (action) variables with realistic patterns and correlations
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import json
import os

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

class BankingSecurityDatasetGenerator:
    def __init__(self, n_participants=2000):
        self.n_participants = n_participants
        self.data = {}
        
    def generate_demographics(self):
        """Generate demographic variables (T0 - Baseline)"""
        print("Generating demographic variables...")
        
        # Age distribution (18-75, skewed toward working age)
        age = np.random.gamma(2, 8, self.n_participants) + 18
        age = np.clip(age, 18, 75).astype(int)
        
        # Gender (55% female, 40% male, 5% other)
        gender = np.random.choice(['Female', 'Male', 'Other'], 
                                self.n_participants, 
                                p=[0.55, 0.40, 0.05])
        
        # Education level
        education = np.random.choice([
            'High School', 'Some College', 'Bachelor\'s', 'Master\'s', 'PhD'
        ], self.n_participants, p=[0.25, 0.20, 0.35, 0.15, 0.05])
        
        # Income (log-normal distribution)
        income = np.random.lognormal(10.5, 0.8, self.n_participants)
        income = np.clip(income, 20000, 200000)
        
        # Banking experience (years)
        banking_years = np.random.gamma(2, 3, self.n_participants) + 1
        banking_years = np.clip(banking_years, 1, 50).astype(int)
        
        # Previous security incident (binary)
        prev_incident = np.random.binomial(1, 0.15, self.n_participants)
        
        # Technology comfort (1-7 scale)
        tech_comfort = np.random.normal(4.5, 1.5, self.n_participants)
        tech_comfort = np.clip(tech_comfort, 1, 7)
        
        self.data.update({
            'participant_id': range(1, self.n_participants + 1),
            'age': age,
            'gender': gender,
            'education': education,
            'income': income,
            'banking_years': banking_years,
            'prev_incident': prev_incident,
            'tech_comfort': tech_comfort
        })
        
    def generate_t1_intentions(self):
        """Generate T1 Intention variables (baseline measures)"""
        print("Generating T1 Intention variables...")
        
        # TPB variables
        # Attitude toward banking security (1-7 scale)
        attitude = np.random.normal(5.2, 1.2, self.n_participants)
        attitude = np.clip(attitude, 1, 7)
        
        # Subjective norm (perceived social pressure)
        subjective_norm = np.random.normal(4.8, 1.3, self.n_participants)
        subjective_norm = np.clip(subjective_norm, 1, 7)
        
        # Perceived Behavioral Control (PBC) - KEY MODERATOR
        pbc = np.random.normal(4.5, 1.4, self.n_participants)
        pbc = np.clip(pbc, 1, 7)
        
        # Intention to engage in security behaviors (1-7 scale)
        # This will be the predictor for the gap analysis
        intention = 0.3 * attitude + 0.2 * subjective_norm + 0.4 * pbc + np.random.normal(0, 0.8, self.n_participants)
        intention = np.clip(intention, 1, 7)
        
        # Knowledge about banking security (1-7 scale)
        knowledge = np.random.normal(4.0, 1.5, self.n_participants)
        knowledge = np.clip(knowledge, 1, 7)
        
        # Risk perception
        risk_perception = np.random.normal(5.5, 1.1, self.n_participants)
        risk_perception = np.clip(risk_perception, 1, 7)
        
        # Trust in banking institutions
        trust_banking = np.random.normal(4.8, 1.3, self.n_participants)
        trust_banking = np.clip(trust_banking, 1, 7)
        
        self.data.update({
            't1_attitude': attitude,
            't1_subjective_norm': subjective_norm,
            't1_pbc': pbc,
            't1_intention': intention,
            't1_knowledge': knowledge,
            't1_risk_perception': risk_perception,
            't1_trust_banking': trust_banking
        })
        
    def generate_t2_self_reported_behavior(self):
        """Generate T2 Self-Reported Behavior variables (SRB1-SRB5)"""
        print("Generating T2 Self-Reported Behavior variables...")
        
        # Base behavior levels (correlated with T1 intention but with noise)
        base_behavior = 0.6 * self.data['t1_intention'] + np.random.normal(0, 1.2, self.n_participants)
        
        # SRB1: Check bank statement for unauthorized transactions
        srb1 = base_behavior + np.random.normal(0, 0.8, self.n_participants)
        srb1 = np.clip(srb1, 1, 7)
        
        # SRB2: Use strong, unique passwords for banking
        srb2 = base_behavior + np.random.normal(0, 0.8, self.n_participants)
        srb2 = np.clip(srb2, 1, 7)
        
        # SRB3: Enable two-factor authentication
        srb3 = base_behavior + np.random.normal(0, 0.8, self.n_participants)
        srb3 = np.clip(srb3, 1, 7)
        
        # SRB4: Log out of banking apps/sites after use
        srb4 = base_behavior + np.random.normal(0, 0.8, self.n_participants)
        srb4 = np.clip(srb4, 1, 7)
        
        # SRB5: Verify text/email alert before clicking a link
        srb5 = base_behavior + np.random.normal(0, 0.8, self.n_participants)
        srb5 = np.clip(srb5, 1, 7)
        
        # Create composite SRB score
        srb_composite = (srb1 + srb2 + srb3 + srb4 + srb5) / 5
        
        self.data.update({
            't2_srb1_check_statements': srb1,
            't2_srb2_strong_passwords': srb2,
            't2_srb3_two_factor_auth': srb3,
            't2_srb4_logout_after_use': srb4,
            't2_srb5_verify_alerts': srb5,
            't2_srb_composite': srb_composite
        })
        
    def generate_objective_behavioral_measure(self):
        """Generate Objective Behavioral Measure (scenario-based quiz)"""
        print("Generating Objective Behavioral Measure...")
        
        # Create 5 scenario-based questions with realistic scoring
        scenarios = []
        
        # Scenario 1: Phishing SMS
        scenario1_scores = np.random.choice([0, 1, 2], self.n_participants, p=[0.15, 0.25, 0.60])
        scenarios.append(scenario1_scores)
        
        # Scenario 2: Suspicious email
        scenario2_scores = np.random.choice([0, 1, 2], self.n_participants, p=[0.20, 0.30, 0.50])
        scenarios.append(scenario2_scores)
        
        # Scenario 3: Public WiFi banking
        scenario3_scores = np.random.choice([0, 1, 2], self.n_participants, p=[0.25, 0.35, 0.40])
        scenarios.append(scenario3_scores)
        
        # Scenario 4: Password sharing
        scenario4_scores = np.random.choice([0, 1, 2], self.n_participants, p=[0.10, 0.20, 0.70])
        scenarios.append(scenario4_scores)
        
        # Scenario 5: Suspicious app download
        scenario5_scores = np.random.choice([0, 1, 2], self.n_participants, p=[0.18, 0.32, 0.50])
        scenarios.append(scenario5_scores)
        
        # Calculate total objective score
        objective_score = np.sum(scenarios, axis=0)
        
        # Add some correlation with knowledge and intention
        knowledge_effect = 0.3 * (self.data['t1_knowledge'] - 4) / 3
        intention_effect = 0.2 * (self.data['t1_intention'] - 4) / 3
        objective_score = objective_score + knowledge_effect + intention_effect + np.random.normal(0, 0.5, self.n_participants)
        objective_score = np.clip(objective_score, 0, 10)
        
        self.data.update({
            't2_objective_scenario1_phishing_sms': scenarios[0],
            't2_objective_scenario2_suspicious_email': scenarios[1],
            't2_objective_scenario3_public_wifi': scenarios[2],
            't2_objective_scenario4_password_sharing': scenarios[3],
            't2_objective_scenario5_suspicious_app': scenarios[4],
            't2_objective_score': objective_score
        })
        
    def calculate_intention_behavior_gap(self):
        """Calculate the Intention-Behavior Gap (residual score)"""
        print("Calculating Intention-Behavior Gap...")
        
        # Use SRB composite as the behavior measure
        behavior = self.data['t2_srb_composite']
        intention = self.data['t1_intention']
        
        # Calculate regression residuals
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import StandardScaler
        
        # Reshape for sklearn
        X = intention.reshape(-1, 1)
        y = behavior
        
        # Fit regression
        reg = LinearRegression()
        reg.fit(X, y)
        
        # Calculate residuals
        predicted = reg.predict(X)
        residuals = y - predicted
        
        # Store the gap
        self.data['t2_intention_behavior_gap'] = residuals
        
        # Create categorical gap variable
        gap_quartiles = np.percentile(residuals, [25, 50, 75])
        gap_category = np.where(residuals <= gap_quartiles[0], 'Underperformer',
                               np.where(residuals <= gap_quartiles[1], 'Slight Underperformer',
                                       np.where(residuals <= gap_quartiles[2], 'Slight Overperformer',
                                               'Overperformer')))
        
        self.data['t2_gap_category'] = gap_category
        
        # Store regression info for documentation
        self.regression_info = {
            'r_squared': reg.score(X, y),
            'coefficient': reg.coef_[0],
            'intercept': reg.intercept_,
            'mean_residual': np.mean(residuals),
            'std_residual': np.std(residuals)
        }
        
    def add_moderating_effects(self):
        """Add realistic moderating effects and interactions"""
        print("Adding moderating effects...")
        
        # PBC moderation effect on intention-behavior gap
        pbc = self.data['t1_pbc']
        gap = self.data['t2_intention_behavior_gap']
        
        # Higher PBC should reduce the gap (more control = less gap)
        pbc_moderation = -0.3 * (pbc - 4) * (gap - np.mean(gap))
        self.data['t2_gap_pbc_moderated'] = gap + pbc_moderation
        
        # Age effects (older participants might have different patterns)
        age = self.data['age']
        age_effect = 0.1 * (age - 40) / 20  # Normalized age effect
        self.data['t2_gap_age_moderated'] = gap + age_effect
        
        # Previous incident effects
        prev_incident = self.data['prev_incident']
        incident_effect = 0.5 * prev_incident  # Those with incidents show different patterns
        self.data['t2_gap_incident_moderated'] = gap + incident_effect
        
    def generate_additional_variables(self):
        """Generate additional useful variables"""
        print("Generating additional variables...")
        
        # Time between T1 and T2 (weeks)
        time_gap = np.random.normal(4, 1, self.n_participants)  # 4 weeks average
        time_gap = np.clip(time_gap, 2, 8)
        self.data['time_gap_weeks'] = time_gap
        
        # Dropout indicator (some participants might not complete T2)
        dropout = np.random.binomial(1, 0.12, self.n_participants)
        self.data['t2_dropout'] = dropout
        
        # For dropouts, set T2 variables to missing
        for key in self.data.keys():
            if key.startswith('t2_') and key != 't2_dropout' and key != 't2_gap_category':
                self.data[key] = np.where(dropout == 1, np.nan, self.data[key])
        
        # Handle string variables separately
        if 't2_gap_category' in self.data:
            self.data['t2_gap_category'] = np.where(dropout == 1, 'Missing', self.data['t2_gap_category'])
        
        # Create completion status
        self.data['completion_status'] = np.where(dropout == 1, 'Incomplete', 'Complete')
        
        # Add some realistic missing data patterns
        missing_prob = 0.05  # 5% missing data
        for key in ['t2_srb1_check_statements', 't2_srb2_strong_passwords', 
                   't2_srb3_two_factor_auth', 't2_srb4_logout_after_use', 
                   't2_srb5_verify_alerts']:
            missing = np.random.binomial(1, missing_prob, self.n_participants)
            self.data[key] = np.where(missing == 1, np.nan, self.data[key])
        
    def create_dataframe(self):
        """Convert data dictionary to pandas DataFrame"""
        print("Creating DataFrame...")
        
        df = pd.DataFrame(self.data)
        
        # Add some realistic string formatting
        df['participant_id'] = df['participant_id'].astype(str).str.zfill(4)
        df['participant_id'] = 'P' + df['participant_id']
        
        # Round numeric columns appropriately
        numeric_cols = ['income', 'tech_comfort', 't1_attitude', 't1_subjective_norm', 
                       't1_pbc', 't1_intention', 't1_knowledge', 't1_risk_perception', 
                       't1_trust_banking', 't2_srb_composite', 't2_objective_score',
                       't2_intention_behavior_gap', 'time_gap_weeks']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].round(2)
        
        return df
        
    def generate_dataset(self):
        """Generate the complete dataset"""
        print(f"Generating banking security dataset with {self.n_participants} participants...")
        
        self.generate_demographics()
        self.generate_t1_intentions()
        self.generate_t2_self_reported_behavior()
        self.generate_objective_behavioral_measure()
        self.calculate_intention_behavior_gap()
        self.add_moderating_effects()
        self.generate_additional_variables()
        
        df = self.create_dataframe()
        
        print(f"Dataset generated successfully!")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        return df, self.regression_info

def create_codebook():
    """Create comprehensive codebook for the dataset"""
    codebook = {
        "dataset_info": {
            "title": "Banking Security Behavior Dataset",
            "description": "Comprehensive dataset for Q1/SCI research on banking security behaviors",
            "n_participants": 2000,
            "variables": 25,
            "time_points": 2
        },
        "variable_descriptions": {
            "demographics": {
                "participant_id": "Unique participant identifier (P0001-P2000)",
                "age": "Age in years (18-75)",
                "gender": "Gender identity (Female/Male/Other)",
                "education": "Highest education level",
                "income": "Annual household income (USD)",
                "banking_years": "Years of banking experience",
                "prev_incident": "Previous security incident (0=No, 1=Yes)",
                "tech_comfort": "Technology comfort level (1-7 scale)"
            },
            "t1_baseline": {
                "t1_attitude": "Attitude toward banking security (1-7 scale)",
                "t1_subjective_norm": "Perceived social pressure (1-7 scale)",
                "t1_pbc": "Perceived Behavioral Control (1-7 scale)",
                "t1_intention": "Intention to engage in security behaviors (1-7 scale)",
                "t1_knowledge": "Security knowledge level (1-7 scale)",
                "t1_risk_perception": "Perceived risk of security threats (1-7 scale)",
                "t1_trust_banking": "Trust in banking institutions (1-7 scale)"
            },
            "t2_self_reported_behavior": {
                "t2_srb1_check_statements": "Check bank statements for unauthorized transactions (1=Never, 7=Always)",
                "t2_srb2_strong_passwords": "Use strong, unique passwords for banking (1=Never, 7=Always)",
                "t2_srb3_two_factor_auth": "Enable two-factor authentication (1=Never, 7=Always)",
                "t2_srb4_logout_after_use": "Log out of banking apps/sites after use (1=Never, 7=Always)",
                "t2_srb5_verify_alerts": "Verify text/email alerts before clicking links (1=Never, 7=Always)",
                "t2_srb_composite": "Composite self-reported behavior score (average of SRB1-SRB5)"
            },
            "t2_objective_behavior": {
                "t2_objective_scenario1_phishing_sms": "Response to phishing SMS scenario (0=Click, 1=Ignore, 2=Call bank)",
                "t2_objective_scenario2_suspicious_email": "Response to suspicious email scenario (0=Click, 1=Ignore, 2=Call bank)",
                "t2_objective_scenario3_public_wifi": "Response to public WiFi banking scenario (0=Use, 1=Maybe, 2=Avoid)",
                "t2_objective_scenario4_password_sharing": "Response to password sharing scenario (0=Share, 1=Maybe, 2=Refuse)",
                "t2_objective_scenario5_suspicious_app": "Response to suspicious app scenario (0=Download, 1=Maybe, 2=Refuse)",
                "t2_objective_score": "Total objective behavioral score (0-10)"
            },
            "t2_gap_analysis": {
                "t2_intention_behavior_gap": "Residual score from intention-behavior regression (negative=underperformer, positive=overperformer)",
                "t2_gap_category": "Categorical gap classification (Underperformer/Slight Underperformer/Slight Overperformer/Overperformer)",
                "t2_gap_pbc_moderated": "Gap score moderated by PBC",
                "t2_gap_age_moderated": "Gap score moderated by age",
                "t2_gap_incident_moderated": "Gap score moderated by previous incident"
            },
            "additional_variables": {
                "time_gap_weeks": "Time between T1 and T2 measurements (weeks)",
                "t2_dropout": "T2 completion status (0=Complete, 1=Dropout)",
                "completion_status": "Overall completion status (Complete/Incomplete)"
            }
        },
        "scoring_notes": {
            "self_reported_behavior": "All SRB variables use 1-7 Likert scale (1=Never, 7=Always)",
            "objective_behavior": "Scenario responses scored 0-2 (0=risky, 1=neutral, 2=safe)",
            "intention_behavior_gap": "Calculated as residuals from regression of T2 behavior on T1 intention",
            "missing_data": "Approximately 5% missing data in SRB variables, 12% dropout rate"
        },
        "research_applications": {
            "primary_analysis": "Intention-behavior gap prediction using PBC as moderator",
            "secondary_analyses": [
                "Self-report vs objective behavior comparison",
                "Demographic predictors of security behavior",
                "Knowledge-behavior relationship",
                "Risk perception effects",
                "Trust-behavior relationship"
            ],
            "statistical_considerations": [
                "Use multiple imputation for missing data",
                "Account for dropout bias in analyses",
                "Consider moderation effects in gap analysis",
                "Validate self-reports against objective measures"
            ]
        }
    }
    return codebook

def main():
    """Main function to generate and save the dataset"""
    print("=== Banking Security Dataset Generator ===")
    print("Generating comprehensive dataset for Q1/SCI research...")
    
    # Generate dataset
    generator = BankingSecurityDatasetGenerator(n_participants=2000)
    df, regression_info = generator.generate_dataset()
    
    # Create output directory
    os.makedirs('/workspace/dataset_output', exist_ok=True)
    
    # Save dataset in multiple formats
    print("\nSaving dataset...")
    
    # CSV format
    df.to_csv('/workspace/dataset_output/banking_security_dataset.csv', index=False)
    print("✓ Saved as CSV")
    
    # Excel format
    df.to_excel('/workspace/dataset_output/banking_security_dataset.xlsx', index=False)
    print("✓ Saved as Excel")
    
    # JSON format
    df.to_json('/workspace/dataset_output/banking_security_dataset.json', orient='records', indent=2)
    print("✓ Saved as JSON")
    
    # Stata format
    df.to_stata('/workspace/dataset_output/banking_security_dataset.dta', write_index=False)
    print("✓ Saved as Stata")
    
    # Create codebook
    codebook = create_codebook()
    codebook['regression_info'] = regression_info
    
    with open('/workspace/dataset_output/codebook.json', 'w') as f:
        json.dump(codebook, f, indent=2)
    print("✓ Saved codebook")
    
    # Create summary statistics
    summary_stats = {
        'dataset_summary': {
            'n_participants': len(df),
            'n_variables': len(df.columns),
            'completion_rate': (df['completion_status'] == 'Complete').mean(),
            'missing_data_rate': df.isnull().sum().sum() / (len(df) * len(df.columns))
        },
        'descriptive_statistics': df.describe().to_dict(),
        'correlation_matrix': df.select_dtypes(include=[np.number]).corr().to_dict()
    }
    
    with open('/workspace/dataset_output/summary_statistics.json', 'w') as f:
        json.dump(summary_stats, f, indent=2)
    print("✓ Saved summary statistics")
    
    # Create analysis script
    analysis_script = '''
# Banking Security Dataset Analysis Script
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

# Load dataset
df = pd.read_csv('banking_security_dataset.csv')

# Basic descriptive statistics
print("Dataset Overview:")
print(f"Participants: {len(df)}")
print(f"Completion rate: {(df['completion_status'] == 'Complete').mean():.2%}")
print(f"Missing data rate: {df.isnull().sum().sum() / (len(df) * len(df.columns)):.2%}")

# Key findings
print("\\nKey Findings:")
print(f"Mean intention-behavior gap: {df['t2_intention_behavior_gap'].mean():.3f}")
print(f"Gap standard deviation: {df['t2_intention_behavior_gap'].std():.3f}")
print(f"Overperformers: {(df['t2_gap_category'] == 'Overperformer').sum()}")
print(f"Underperformers: {(df['t2_gap_category'] == 'Underperformer').sum()}")

# PBC moderation analysis
print("\\nPBC Moderation Analysis:")
pbc_high = df[df['t1_pbc'] >= df['t1_pbc'].median()]
pbc_low = df[df['t1_pbc'] < df['t1_pbc'].median()]
print(f"High PBC gap mean: {pbc_high['t2_intention_behavior_gap'].mean():.3f}")
print(f"Low PBC gap mean: {pbc_low['t2_intention_behavior_gap'].mean():.3f}")

# Self-report vs objective behavior correlation
print(f"\\nSRB-Objective correlation: {df['t2_srb_composite'].corr(df['t2_objective_score']):.3f}")
'''
    
    with open('/workspace/dataset_output/analysis_script.py', 'w') as f:
        f.write(analysis_script)
    print("✓ Saved analysis script")
    
    print(f"\n=== Dataset Generation Complete ===")
    print(f"Files saved in /workspace/dataset_output/")
    print(f"Dataset shape: {df.shape}")
    print(f"Ready for Q1/SCI research analysis!")

if __name__ == "__main__":
    main()