#!/usr/bin/env python3
"""
Banking Security Behavior Dataset Generator
Generates a comprehensive dataset for studying the intention-behavior gap in banking security practices.

This script creates:
- T1 variables: Intentions, PBC, attitudes, subjective norms
- T2 Action variables: Self-reported behaviors, objective scores, intention-behavior gap
- Demographic and contextual variables
- Realistic relationships between variables
"""

import pandas as pd
import numpy as np
import random
from scipy import stats
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Set random seeds for reproducibility
np.random.seed(42)
random.seed(42)

def generate_demographics(n=2000):
    """Generate realistic demographic variables"""
    demographics = {}
    
    # Age (18-75, weighted toward middle-aged)
    demographics['age'] = np.random.beta(2, 5, n) * 57 + 18
    demographics['age'] = np.round(demographics['age']).astype(int)
    
    # Gender (60% female, 40% male)
    demographics['gender'] = np.random.choice(['Female', 'Male'], n, p=[0.6, 0.4])
    
    # Education (ordinal scale 1-5)
    demographics['education'] = np.random.choice([1, 2, 3, 4, 5], n, p=[0.1, 0.2, 0.3, 0.3, 0.1])
    
    # Income (ordinal scale 1-6)
    demographics['income'] = np.random.choice([1, 2, 3, 4, 5, 6], n, p=[0.15, 0.2, 0.25, 0.2, 0.15, 0.05])
    
    # Banking experience (years)
    demographics['banking_experience'] = np.random.exponential(5, n) + 1
    demographics['banking_experience'] = np.clip(demographics['banking_experience'], 1, 30)
    
    # Technology comfort (1-7 scale)
    demographics['tech_comfort'] = np.random.normal(4.5, 1.5, n)
    demographics['tech_comfort'] = np.clip(demographics['tech_comfort'], 1, 7)
    
    # Previous security incident (binary)
    demographics['previous_incident'] = np.random.choice([0, 1], n, p=[0.7, 0.3])
    
    return pd.DataFrame(demographics)

def generate_t1_variables(n=2000, demographics=None):
    """Generate T1 baseline variables (intentions, PBC, attitudes, subjective norms)"""
    t1_data = {}
    
    # Base values influenced by demographics
    base_intention = 4.0
    base_pbc = 4.2
    base_attitude = 4.5
    base_subjective_norm = 3.8
    
    # Adjust based on demographics
    if demographics is not None:
        # Higher education and tech comfort increase intentions and PBC
        education_effect = (demographics['education'] - 3) * 0.3
        tech_effect = (demographics['tech_comfort'] - 4.5) * 0.2
        age_effect = (demographics['age'] - 45) / 100  # Slight age effect
        incident_effect = demographics['previous_incident'] * 0.5
        
        base_intention += education_effect + tech_effect + incident_effect
        base_pbc += education_effect + tech_effect
        base_attitude += education_effect + tech_effect + incident_effect
        base_subjective_norm += education_effect + age_effect
    
    # Generate variables with realistic correlations
    # Intentions (1-7 scale)
    t1_data['intention'] = np.random.normal(base_intention, 1.2, n)
    t1_data['intention'] = np.clip(t1_data['intention'], 1, 7)
    
    # Perceived Behavioral Control (1-7 scale)
    # PBC should correlate with intention but not perfectly
    pbc_correlation = 0.6
    t1_data['pbc'] = base_pbc + pbc_correlation * (t1_data['intention'] - base_intention) + np.random.normal(0, 0.8, n)
    t1_data['pbc'] = np.clip(t1_data['pbc'], 1, 7)
    
    # Attitude toward banking security (1-7 scale)
    attitude_correlation = 0.7
    t1_data['attitude'] = base_attitude + attitude_correlation * (t1_data['intention'] - base_intention) + np.random.normal(0, 0.6, n)
    t1_data['attitude'] = np.clip(t1_data['attitude'], 1, 7)
    
    # Subjective Norm (1-7 scale)
    norm_correlation = 0.5
    t1_data['subjective_norm'] = base_subjective_norm + norm_correlation * (t1_data['intention'] - base_intention) + np.random.normal(0, 0.9, n)
    t1_data['subjective_norm'] = np.clip(t1_data['subjective_norm'], 1, 7)
    
    return pd.DataFrame(t1_data)

def generate_t2_self_reported_behavior(n=2000, t1_data=None, demographics=None):
    """Generate T2 Self-Reported Behavior variables (SRB1-SRB5)"""
    srb_data = {}
    
    # Base behavior levels influenced by T1 intentions and demographics
    base_behavior = 4.0
    
    if t1_data is not None:
        # Strong correlation with T1 intentions
        intention_effect = (t1_data['intention'] - 4.0) * 0.6
        base_behavior += intention_effect
    
    if demographics is not None:
        # Demographics influence behavior
        education_effect = (demographics['education'] - 3) * 0.2
        tech_effect = (demographics['tech_comfort'] - 4.5) * 0.15
        incident_effect = demographics['previous_incident'] * 0.3
        
        base_behavior += education_effect + tech_effect + incident_effect
    
    # Generate each SRB variable with slight variations
    behaviors = {
        'SRB1_check_statements': 'Check bank statement for unauthorized transactions',
        'SRB2_unique_passwords': 'Use strong, unique passwords for banking',
        'SRB3_two_factor': 'Enable two-factor authentication',
        'SRB4_logout': 'Log out of banking apps/sites after use',
        'SRB5_verify_alerts': 'Verify text/email alert before clicking a link'
    }
    
    for i, (var_name, description) in enumerate(behaviors.items()):
        # Each behavior has slightly different base rates
        behavior_base = base_behavior + np.random.normal(0, 0.3, n)
        
        # Add some random variation and ensure realistic distribution
        behavior_score = behavior_base + np.random.normal(0, 1.0, n)
        behavior_score = np.clip(behavior_score, 1, 7)
        
        # Round to nearest integer (1-7 scale)
        srb_data[var_name] = np.round(behavior_score).astype(int)
    
    return pd.DataFrame(srb_data)

def generate_objective_score(n=2000, t1_data=None, demographics=None):
    """Generate objective behavioral measure through scenario-based quiz"""
    objective_data = {}
    
    # Base objective score influenced by T1 variables and demographics
    base_score = 6.0  # Out of 10 possible points
    
    if t1_data is not None:
        # PBC is the strongest predictor of objective behavior
        pbc_effect = (t1_data['pbc'] - 4.0) * 1.5
        intention_effect = (t1_data['intention'] - 4.0) * 0.8
        attitude_effect = (t1_data['attitude'] - 4.0) * 0.6
        
        base_score += pbc_effect + intention_effect + attitude_effect
    
    if demographics is not None:
        # Demographics influence objective performance
        education_effect = (demographics['education'] - 3) * 0.8
        tech_effect = (demographics['tech_comfort'] - 4.5) * 0.6
        experience_effect = (demographics['banking_experience'] - 10) / 20
        incident_effect = demographics['previous_incident'] * 1.0
        
        base_score += education_effect + tech_effect + experience_effect + incident_effect
    
    # Generate objective score (0-10 scale)
    objective_score = base_score + np.random.normal(0, 2.0, n)
    objective_score = np.clip(objective_score, 0, 10)
    
    # Round to nearest integer
    objective_data['objective_score'] = np.round(objective_score).astype(int)
    
    return pd.DataFrame(objective_data)

def calculate_intention_behavior_gap(t1_intention, t2_behavior):
    """Calculate intention-behavior gap using regression residuals"""
    from sklearn.linear_model import LinearRegression
    
    # Create composite behavior score from SRB variables
    behavior_composite = t2_behavior.mean(axis=1)
    
    # Fit regression: T2 behavior ~ T1 intention
    X = t1_intention.values.reshape(-1, 1)
    y = behavior_composite.values
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Calculate residuals
    predicted_behavior = model.predict(X)
    residuals = y - predicted_behavior
    
    return residuals

def generate_contextual_variables(n=2000, demographics=None):
    """Generate additional contextual variables"""
    context_data = {}
    
    # Time between T1 and T2 (weeks)
    context_data['time_gap_weeks'] = np.random.normal(4, 1, n)
    context_data['time_gap_weeks'] = np.clip(context_data['time_gap_weeks'], 2, 8)
    
    # Recent security news exposure (1-7 scale)
    context_data['security_news_exposure'] = np.random.normal(3.5, 1.5, n)
    context_data['security_news_exposure'] = np.clip(context_data['security_news_exposure'], 1, 7)
    
    # Banking app usage frequency (1-7 scale)
    context_data['app_usage_frequency'] = np.random.normal(5.0, 1.2, n)
    context_data['app_usage_frequency'] = np.clip(context_data['app_usage_frequency'], 1, 7)
    
    # Perceived threat level (1-7 scale)
    context_data['perceived_threat'] = np.random.normal(4.2, 1.3, n)
    context_data['perceived_threat'] = np.clip(context_data['perceived_threat'], 1, 7)
    
    # Social influence (1-7 scale)
    context_data['social_influence'] = np.random.normal(3.8, 1.4, n)
    context_data['social_influence'] = np.clip(context_data['social_influence'], 1, 7)
    
    return pd.DataFrame(context_data)

def main():
    """Generate the complete banking security dataset"""
    print("Generating Banking Security Behavior Dataset...")
    print("=" * 50)
    
    # Set sample size
    n = 2000
    
    # Generate demographic variables
    print("1. Generating demographic variables...")
    demographics = generate_demographics(n)
    
    # Generate T1 variables
    print("2. Generating T1 baseline variables...")
    t1_data = generate_t1_variables(n, demographics)
    
    # Generate T2 self-reported behavior
    print("3. Generating T2 self-reported behavior variables...")
    t2_srb = generate_t2_self_reported_behavior(n, t1_data, demographics)
    
    # Generate objective score
    print("4. Generating objective behavioral measure...")
    objective_data = generate_objective_score(n, t1_data, demographics)
    
    # Calculate intention-behavior gap
    print("5. Calculating intention-behavior gap...")
    intention_behavior_gap = calculate_intention_behavior_gap(t1_data['intention'], t2_srb)
    
    # Generate contextual variables
    print("6. Generating contextual variables...")
    context_data = generate_contextual_variables(n, demographics)
    
    # Combine all data
    print("7. Combining all data...")
    dataset = pd.concat([
        demographics,
        t1_data,
        t2_srb,
        objective_data,
        context_data
    ], axis=1)
    
    # Add intention-behavior gap
    dataset['intention_behavior_gap'] = intention_behavior_gap
    
    # Add participant ID
    dataset['participant_id'] = range(1, n + 1)
    
    # Reorder columns for better organization
    column_order = ['participant_id'] + list(demographics.columns) + list(t1_data.columns) + \
                   list(t2_srb.columns) + list(objective_data.columns) + \
                   list(context_data.columns) + ['intention_behavior_gap']
    
    dataset = dataset[column_order]
    
    # Save dataset
    print("8. Saving dataset...")
    dataset.to_csv('/workspace/banking_security_dataset.csv', index=False)
    
    # Generate summary statistics
    print("\nDataset Summary:")
    print("=" * 50)
    print(f"Sample size: {len(dataset)}")
    print(f"Variables: {len(dataset.columns)}")
    print("\nVariable Descriptions:")
    print("-" * 30)
    
    variable_descriptions = {
        'participant_id': 'Unique participant identifier',
        'age': 'Age in years (18-75)',
        'gender': 'Gender (Female/Male)',
        'education': 'Education level (1=High school, 5=Graduate degree)',
        'income': 'Income level (1=Under $25k, 6=Over $150k)',
        'banking_experience': 'Years of banking experience',
        'tech_comfort': 'Technology comfort level (1-7)',
        'previous_incident': 'Previous security incident (0=No, 1=Yes)',
        'intention': 'T1: Intention to practice security behaviors (1-7)',
        'pbc': 'T1: Perceived Behavioral Control (1-7)',
        'attitude': 'T1: Attitude toward security behaviors (1-7)',
        'subjective_norm': 'T1: Subjective norm (1-7)',
        'SRB1_check_statements': 'T2: Check statements for unauthorized transactions (1-7)',
        'SRB2_unique_passwords': 'T2: Use strong, unique passwords (1-7)',
        'SRB3_two_factor': 'T2: Enable two-factor authentication (1-7)',
        'SRB4_logout': 'T2: Log out after use (1-7)',
        'SRB5_verify_alerts': 'T2: Verify alerts before clicking (1-7)',
        'objective_score': 'T2: Objective behavioral score (0-10)',
        'time_gap_weeks': 'Time between T1 and T2 (weeks)',
        'security_news_exposure': 'Recent security news exposure (1-7)',
        'app_usage_frequency': 'Banking app usage frequency (1-7)',
        'perceived_threat': 'Perceived security threat level (1-7)',
        'social_influence': 'Social influence on security behaviors (1-7)',
        'intention_behavior_gap': 'Intention-behavior gap (residual score)'
    }
    
    for var, desc in variable_descriptions.items():
        if var in dataset.columns:
            print(f"{var}: {desc}")
    
    print(f"\nDataset saved to: /workspace/banking_security_dataset.csv")
    print(f"File size: {dataset.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    # Display basic statistics
    print("\nBasic Statistics:")
    print("-" * 20)
    print(dataset.describe())
    
    return dataset

if __name__ == "__main__":
    dataset = main()