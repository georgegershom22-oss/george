#!/usr/bin/env python3
"""
Comprehensive Behavioral Intention Dataset Generator
Based on Theory of Planned Behavior (TPB) and Protection Motivation Theory (PMT)
Context: Bank Security Behavior

This script generates a realistic dataset for studying behavioral intentions
and actual behavior in the context of following bank security recommendations.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import json
from scipy.stats import truncnorm, multivariate_normal
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

class BehavioralDatasetGenerator:
    def __init__(self, n_participants=1200):
        """
        Initialize the dataset generator
        
        Args:
            n_participants (int): Number of participants to generate
        """
        self.n_participants = n_participants
        self.data = {}
        
        # Define the theoretical constructs and their items
        self.constructs = {
            'ATT': {
                'items': ['ATT1', 'ATT2', 'ATT3'],
                'labels': [
                    'Following bank security steps is beneficial',
                    'Following bank security steps is wise', 
                    'Following bank security steps is important'
                ],
                'mean': 5.8,
                'std': 0.9
            },
            'SN': {
                'items': ['SN1', 'SN2', 'SN3'],
                'labels': [
                    'Most people important to me think I should follow security steps',
                    'My family expects me to be diligent with bank security',
                    'People whose opinions I value would approve of my following security steps'
                ],
                'mean': 5.2,
                'std': 1.1
            },
            'PBC': {
                'items': ['PBC1', 'PBC2', 'PBC3'],
                'labels': [
                    'Following all security steps would be easy for me',
                    'I have the resources, time, and knowledge to follow security steps',
                    'Whether I follow security steps is entirely up to me'
                ],
                'mean': 5.0,
                'std': 1.2
            },
            'INT': {
                'items': ['INT1', 'INT2', 'INT3'],
                'labels': [
                    'I intend to follow all recommended security steps in the next 3 months',
                    'I plan to make an effort to be more diligent with bank security',
                    'I will try to follow all bank security recommendations consistently'
                ],
                'mean': 5.5,
                'std': 1.0
            },
            'PS': {  # Perceived Severity
                'items': ['PS1', 'PS2', 'PS3'],
                'labels': [
                    'The financial loss from fraud would be severe for me',
                    'Bank fraud would cause serious problems in my life',
                    'The consequences of bank fraud would be significant for me'
                ],
                'mean': 6.2,
                'std': 0.8
            },
            'PV': {  # Perceived Vulnerability
                'items': ['PV1', 'PV2', 'PV3'],
                'labels': [
                    'I am at high risk of experiencing bank fraud',
                    'It is likely that I could become a victim of bank fraud',
                    'I am vulnerable to bank fraud attacks'
                ],
                'mean': 4.1,
                'std': 1.3
            },
            'SE': {  # Self-Efficacy
                'items': ['SE1', 'SE2', 'SE3'],
                'labels': [
                    'I am confident I can perform security steps correctly',
                    'I have the ability to follow all recommended security measures',
                    'I can successfully implement bank security practices'
                ],
                'mean': 5.3,
                'std': 1.0
            },
            'RE': {  # Response Efficacy
                'items': ['RE1', 'RE2', 'RE3'],
                'labels': [
                    'I believe security steps are effective in protecting me',
                    'Following security recommendations will prevent fraud',
                    'Bank security measures are reliable protection methods'
                ],
                'mean': 5.6,
                'std': 0.9
            }
        }
        
    def generate_demographics(self):
        """Generate realistic demographic variables"""
        print("Generating demographic variables...")
        
        # Age: Normal distribution, truncated between 18-80
        age_mean, age_std = 42, 15
        a, b = (18 - age_mean) / age_std, (80 - age_mean) / age_std
        ages = truncnorm.rvs(a, b, loc=age_mean, scale=age_std, size=self.n_participants)
        self.data['Age'] = np.round(ages).astype(int)
        
        # Gender: Roughly balanced with slight female majority
        genders = np.random.choice(['Male', 'Female', 'Other'], 
                                 size=self.n_participants, 
                                 p=[0.47, 0.51, 0.02])
        self.data['Gender'] = genders
        
        # Education levels
        education_levels = ['High School', 'Some College', 'Bachelor\'s', 'Master\'s', 'PhD', 'Other']
        education_probs = [0.15, 0.25, 0.35, 0.20, 0.04, 0.01]
        self.data['Education'] = np.random.choice(education_levels, 
                                                size=self.n_participants, 
                                                p=education_probs)
        
        # Income brackets (annual household income in USD)
        income_brackets = ['<30k', '30k-50k', '50k-75k', '75k-100k', '100k-150k', '>150k']
        income_probs = [0.18, 0.22, 0.25, 0.20, 0.10, 0.05]
        self.data['Income'] = np.random.choice(income_brackets, 
                                             size=self.n_participants, 
                                             p=income_probs)
        
        # Banking experience (years)
        banking_exp_mean, banking_exp_std = 15, 8
        a, b = (1 - banking_exp_mean) / banking_exp_std, (50 - banking_exp_mean) / banking_exp_std
        banking_exp = truncnorm.rvs(a, b, loc=banking_exp_mean, scale=banking_exp_std, 
                                   size=self.n_participants)
        self.data['Banking_Experience_Years'] = np.round(banking_exp, 1)
        
        # Technology comfort level (1-7 scale)
        tech_comfort_mean = 4.8
        tech_comfort = np.random.normal(tech_comfort_mean, 1.2, self.n_participants)
        self.data['Tech_Comfort'] = np.clip(np.round(tech_comfort), 1, 7).astype(int)
        
        # Previous fraud experience
        fraud_experience = np.random.choice(['Yes', 'No'], 
                                          size=self.n_participants, 
                                          p=[0.23, 0.77])
        self.data['Previous_Fraud_Experience'] = fraud_experience
        
    def generate_past_behavior(self):
        """Generate past behavior variable with realistic distribution"""
        print("Generating past behavior data...")
        
        # Past behavior tends to be slightly positive but with variation
        # Influenced by demographics and other factors
        base_past_behavior = np.random.normal(4.2, 1.4, self.n_participants)
        
        # Adjust based on demographics
        for i in range(self.n_participants):
            # Higher education tends to correlate with better security behavior
            if self.data['Education'][i] in ['Master\'s', 'PhD']:
                base_past_behavior[i] += 0.5
            elif self.data['Education'][i] == 'High School':
                base_past_behavior[i] -= 0.3
                
            # Age effect (middle-aged more cautious)
            if 35 <= self.data['Age'][i] <= 55:
                base_past_behavior[i] += 0.3
            elif self.data['Age'][i] < 25:
                base_past_behavior[i] -= 0.4
                
            # Previous fraud experience increases caution
            if self.data['Previous_Fraud_Experience'][i] == 'Yes':
                base_past_behavior[i] += 0.8
                
            # Technology comfort affects ability to follow security steps
            tech_effect = (self.data['Tech_Comfort'][i] - 4) * 0.2
            base_past_behavior[i] += tech_effect
        
        self.data['Past_Behavior'] = np.clip(np.round(base_past_behavior), 1, 7).astype(int)
        
    def generate_correlated_constructs(self):
        """Generate TPB and PMT construct responses with realistic correlations"""
        print("Generating correlated construct responses...")
        
        # Define correlation matrix based on theoretical expectations
        construct_names = list(self.constructs.keys())
        n_constructs = len(construct_names)
        
        # Create correlation matrix
        correlation_matrix = np.eye(n_constructs)
        
        # Set theoretically expected correlations
        correlations = {
            ('ATT', 'INT'): 0.65,    # Attitude strongly predicts intention
            ('SN', 'INT'): 0.45,     # Subjective norm moderately predicts intention
            ('PBC', 'INT'): 0.58,    # PBC strongly predicts intention
            ('ATT', 'SN'): 0.35,     # Attitude and subjective norm moderate correlation
            ('ATT', 'PBC'): 0.42,    # Attitude and PBC moderate correlation
            ('SN', 'PBC'): 0.28,     # SN and PBC weak-moderate correlation
            ('PS', 'PV'): 0.48,      # Perceived severity and vulnerability moderate correlation
            ('SE', 'PBC'): 0.72,     # Self-efficacy and PBC strong correlation (conceptually similar)
            ('SE', 'RE'): 0.55,      # Self-efficacy and response efficacy moderate correlation
            ('ATT', 'RE'): 0.60,     # Attitude and response efficacy moderate-strong correlation
            ('PS', 'INT'): 0.35,     # Threat appraisal affects intention
            ('PV', 'INT'): 0.25,     # Vulnerability perception affects intention
            ('SE', 'INT'): 0.52,     # Self-efficacy affects intention
            ('RE', 'INT'): 0.48,     # Response efficacy affects intention
        }
        
        # Fill correlation matrix
        for i, construct1 in enumerate(construct_names):
            for j, construct2 in enumerate(construct_names):
                if i != j:
                    key = (construct1, construct2)
                    reverse_key = (construct2, construct1)
                    if key in correlations:
                        correlation_matrix[i, j] = correlations[key]
                    elif reverse_key in correlations:
                        correlation_matrix[i, j] = correlations[reverse_key]
                    else:
                        # Default small correlation for unspecified pairs
                        correlation_matrix[i, j] = np.random.uniform(0.05, 0.25)
        
        # Generate means for each construct (average across items)
        construct_means = [self.constructs[name]['mean'] for name in construct_names]
        construct_stds = [self.constructs[name]['std'] for name in construct_names]
        
        # Ensure correlation matrix is positive semidefinite
        # Add small value to diagonal to ensure positive definiteness
        correlation_matrix += np.eye(n_constructs) * 0.01
        
        # Create covariance matrix
        cov_matrix = np.outer(construct_stds, construct_stds) * correlation_matrix
        
        # Generate correlated construct scores
        construct_scores = multivariate_normal.rvs(
            mean=construct_means, 
            cov=cov_matrix,
            size=self.n_participants
        )
        
        # Adjust scores based on past behavior and demographics
        for i in range(self.n_participants):
            past_behavior_effect = (self.data['Past_Behavior'][i] - 4) * 0.3
            
            # Past behavior strongly influences PBC and intention
            construct_scores[i, construct_names.index('PBC')] += past_behavior_effect * 1.2
            construct_scores[i, construct_names.index('INT')] += past_behavior_effect * 1.0
            construct_scores[i, construct_names.index('SE')] += past_behavior_effect * 0.8
            
            # Previous fraud experience affects threat appraisal
            if self.data['Previous_Fraud_Experience'][i] == 'Yes':
                construct_scores[i, construct_names.index('PS')] += 0.6
                construct_scores[i, construct_names.index('PV')] += 0.8
                
        # Generate individual item responses for each construct
        for construct_idx, construct_name in enumerate(construct_names):
            construct_mean = construct_scores[:, construct_idx]
            items = self.constructs[construct_name]['items']
            
            # Generate item-level responses with some measurement error
            for item_idx, item_name in enumerate(items):
                # Add item-specific variation
                item_variation = np.random.normal(0, 0.3, self.n_participants)
                
                # Some items might be systematically higher/lower
                if item_idx == 0:  # First item tends to be slightly higher
                    item_bias = 0.1
                elif item_idx == len(items) - 1:  # Last item might be slightly lower
                    item_bias = -0.05
                else:
                    item_bias = 0
                
                item_scores = construct_mean + item_variation + item_bias
                
                # Clip to 1-7 scale and round
                self.data[item_name] = np.clip(np.round(item_scores), 1, 7).astype(int)
    
    def generate_time2_behavior(self):
        """Generate Time 2 actual behavior data (3 months later)"""
        print("Generating Time 2 behavioral outcomes...")
        
        # Calculate intention scores (average of INT items)
        intention_scores = (self.data['INT1'] + self.data['INT2'] + self.data['INT3']) / 3
        
        # Calculate PBC scores
        pbc_scores = (self.data['PBC1'] + self.data['PBC2'] + self.data['PBC3']) / 3
        
        # Actual behavior is influenced by intention, PBC, and past behavior
        # But with some intention-behavior gap
        base_behavior = (
            0.45 * intention_scores +
            0.25 * pbc_scores +
            0.40 * self.data['Past_Behavior'] +
            np.random.normal(0, 0.8, self.n_participants)
        )
        
        # Add some random life events that might disrupt behavior
        disruption_events = np.random.binomial(1, 0.15, self.n_participants)  # 15% experience disruption
        base_behavior -= disruption_events * np.random.uniform(0.5, 2.0, self.n_participants)
        
        # Some people exceed their intentions
        positive_surprises = np.random.binomial(1, 0.12, self.n_participants)  # 12% exceed expectations
        base_behavior += positive_surprises * np.random.uniform(0.3, 1.2, self.n_participants)
        
        self.data['T2_Actual_Behavior'] = np.clip(np.round(base_behavior), 1, 7).astype(int)
        
        # Generate specific behavioral indicators
        behavior_items = {
            'T2_Check_URLs': 'How often did you check website URLs before entering login info?',
            'T2_Use_2FA': 'How often did you use two-factor authentication when available?',
            'T2_Update_Passwords': 'How often did you update/change your banking passwords?',
            'T2_Monitor_Accounts': 'How often did you monitor your accounts for suspicious activity?',
            'T2_Secure_Networks': 'How often did you avoid banking on public/unsecured networks?'
        }
        
        for item_name, item_label in behavior_items.items():
            # Each item correlated with overall behavior but with some variation
            item_scores = (
                0.7 * self.data['T2_Actual_Behavior'] +
                np.random.normal(0, 1.0, self.n_participants)
            )
            self.data[item_name] = np.clip(np.round(item_scores), 1, 7).astype(int)
    
    def add_additional_variables(self):
        """Add additional control and contextual variables"""
        print("Adding additional control variables...")
        
        # Participant ID
        self.data['Participant_ID'] = [f'P{str(i+1).zfill(4)}' for i in range(self.n_participants)]
        
        # Data collection timestamps
        base_date = datetime(2024, 1, 15)
        t1_dates = [base_date + timedelta(days=random.randint(0, 45)) for _ in range(self.n_participants)]
        t2_dates = [t1_date + timedelta(days=random.randint(85, 105)) for t1_date in t1_dates]
        
        self.data['T1_Date'] = [date.strftime('%Y-%m-%d') for date in t1_dates]
        self.data['T2_Date'] = [date.strftime('%Y-%m-%d') for date in t2_dates]
        
        # Bank type
        bank_types = ['National Bank', 'Regional Bank', 'Credit Union', 'Online Bank']
        self.data['Primary_Bank_Type'] = np.random.choice(bank_types, 
                                                        size=self.n_participants,
                                                        p=[0.45, 0.25, 0.20, 0.10])
        
        # Number of bank accounts
        self.data['Number_Bank_Accounts'] = np.random.choice([1, 2, 3, 4, 5], 
                                                           size=self.n_participants,
                                                           p=[0.25, 0.35, 0.25, 0.10, 0.05])
        
        # Online banking frequency
        online_freq = ['Daily', 'Several times/week', 'Weekly', 'Monthly', 'Rarely']
        self.data['Online_Banking_Frequency'] = np.random.choice(online_freq,
                                                               size=self.n_participants,
                                                               p=[0.15, 0.30, 0.25, 0.20, 0.10])
        
        # Mobile banking usage
        self.data['Uses_Mobile_Banking'] = np.random.choice(['Yes', 'No'],
                                                          size=self.n_participants,
                                                          p=[0.78, 0.22])
        
        # Financial literacy (self-reported, 1-7 scale)
        fin_literacy = np.random.normal(4.6, 1.1, self.n_participants)
        self.data['Financial_Literacy'] = np.clip(np.round(fin_literacy), 1, 7).astype(int)
        
        # Risk tolerance (1-7 scale, 1=very risk averse, 7=very risk tolerant)
        risk_tolerance = np.random.normal(3.8, 1.3, self.n_participants)
        self.data['Risk_Tolerance'] = np.clip(np.round(risk_tolerance), 1, 7).astype(int)
        
        # Trust in bank security (1-7 scale)
        bank_trust = np.random.normal(5.1, 1.0, self.n_participants)
        self.data['Trust_Bank_Security'] = np.clip(np.round(bank_trust), 1, 7).astype(int)
        
    def generate_complete_dataset(self):
        """Generate the complete dataset"""
        print(f"Generating comprehensive behavioral dataset with {self.n_participants} participants...")
        print("=" * 70)
        
        # Generate all components
        self.generate_demographics()
        self.generate_past_behavior()
        self.generate_correlated_constructs()
        self.generate_time2_behavior()
        self.add_additional_variables()
        
        # Convert to DataFrame
        df = pd.DataFrame(self.data)
        
        # Reorder columns for better organization
        id_cols = ['Participant_ID', 'T1_Date', 'T2_Date']
        demo_cols = ['Age', 'Gender', 'Education', 'Income', 'Banking_Experience_Years', 
                    'Tech_Comfort', 'Previous_Fraud_Experience']
        context_cols = ['Primary_Bank_Type', 'Number_Bank_Accounts', 'Online_Banking_Frequency',
                       'Uses_Mobile_Banking', 'Financial_Literacy', 'Risk_Tolerance', 'Trust_Bank_Security']
        
        # TPB constructs
        tpb_cols = []
        for construct in ['ATT', 'SN', 'PBC', 'INT']:
            tpb_cols.extend(self.constructs[construct]['items'])
        
        # PMT constructs
        pmt_cols = []
        for construct in ['PS', 'PV', 'SE', 'RE']:
            pmt_cols.extend(self.constructs[construct]['items'])
        
        past_behavior_cols = ['Past_Behavior']
        
        # T2 behavior outcomes
        t2_cols = ['T2_Actual_Behavior', 'T2_Check_URLs', 'T2_Use_2FA', 
                  'T2_Update_Passwords', 'T2_Monitor_Accounts', 'T2_Secure_Networks']
        
        # Reorder DataFrame
        column_order = (id_cols + demo_cols + context_cols + 
                       tpb_cols + pmt_cols + past_behavior_cols + t2_cols)
        
        df = df[column_order]
        
        print(f"Dataset generated successfully!")
        print(f"Shape: {df.shape}")
        print(f"Columns: {len(df.columns)}")
        
        return df

def main():
    """Main function to generate and save the dataset"""
    
    # Generate dataset
    generator = BehavioralDatasetGenerator(n_participants=1200)
    dataset = generator.generate_complete_dataset()
    
    # Save dataset
    dataset.to_csv('/workspace/behavioral_intention_dataset.csv', index=False)
    print(f"\nDataset saved to: /workspace/behavioral_intention_dataset.csv")
    
    # Generate summary statistics
    print("\n" + "="*70)
    print("DATASET SUMMARY")
    print("="*70)
    
    print(f"Total participants: {len(dataset)}")
    print(f"Total variables: {len(dataset.columns)}")
    
    print("\nDemographic Summary:")
    print(f"Age: M={dataset['Age'].mean():.1f}, SD={dataset['Age'].std():.1f}, Range={dataset['Age'].min()}-{dataset['Age'].max()}")
    print(f"Gender distribution:\n{dataset['Gender'].value_counts()}")
    print(f"Education distribution:\n{dataset['Education'].value_counts()}")
    
    print("\nKey Construct Means (1-7 scale):")
    constructs = ['ATT1', 'ATT2', 'ATT3', 'SN1', 'SN2', 'SN3', 
                 'PBC1', 'PBC2', 'PBC3', 'INT1', 'INT2', 'INT3']
    
    for construct in constructs:
        mean_val = dataset[construct].mean()
        std_val = dataset[construct].std()
        print(f"{construct}: M={mean_val:.2f}, SD={std_val:.2f}")
    
    print(f"\nPast Behavior: M={dataset['Past_Behavior'].mean():.2f}, SD={dataset['Past_Behavior'].std():.2f}")
    print(f"T2 Actual Behavior: M={dataset['T2_Actual_Behavior'].mean():.2f}, SD={dataset['T2_Actual_Behavior'].std():.2f}")
    
    # Calculate correlations for validation
    print("\nKey Correlations (for validation):")
    att_mean = (dataset['ATT1'] + dataset['ATT2'] + dataset['ATT3']) / 3
    int_mean = (dataset['INT1'] + dataset['INT2'] + dataset['INT3']) / 3
    pbc_mean = (dataset['PBC1'] + dataset['PBC2'] + dataset['PBC3']) / 3
    
    print(f"Attitude-Intention: r={att_mean.corr(int_mean):.3f}")
    print(f"PBC-Intention: r={pbc_mean.corr(int_mean):.3f}")
    print(f"Intention-T2 Behavior: r={int_mean.corr(dataset['T2_Actual_Behavior']):.3f}")
    print(f"Past Behavior-T2 Behavior: r={dataset['Past_Behavior'].corr(dataset['T2_Actual_Behavior']):.3f}")
    
    return dataset

if __name__ == "__main__":
    dataset = main()