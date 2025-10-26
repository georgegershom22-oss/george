#!/usr/bin/env python3
"""
Comprehensive Behavioral Intention Dataset Generator
Based on Theory of Planned Behavior (TPB) and Protection Motivation Theory (PMT)

This script generates a realistic dataset for studying behavioral intentions
regarding bank security practices, including all required constructs with
proper psychometric properties and theoretical relationships.
"""

import pandas as pd
import numpy as np
import random
from scipy import stats
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class BehavioralIntentionDatasetGenerator:
    def __init__(self, n_samples=2000, random_seed=42):
        """
        Initialize the dataset generator
        
        Args:
            n_samples (int): Number of participants in the dataset
            random_seed (int): Random seed for reproducibility
        """
        self.n_samples = n_samples
        self.random_seed = random_seed
        np.random.seed(random_seed)
        random.seed(random_seed)
        
        # Initialize data dictionary
        self.data = {}
        
    def generate_demographics(self):
        """Generate realistic demographic variables"""
        print("Generating demographic variables...")
        
        # Age distribution (18-80, skewed towards middle age)
        age = np.random.gamma(2, 15, self.n_samples)
        age = np.clip(age, 18, 80).astype(int)
        
        # Gender (60% female, 40% male, based on typical survey demographics)
        gender = np.random.choice(['Female', 'Male', 'Other'], 
                                self.n_samples, p=[0.60, 0.38, 0.02])
        
        # Education level
        education = np.random.choice([
            'High School', 'Some College', 'Bachelor\'s Degree', 
            'Master\'s Degree', 'Doctorate/Professional'
        ], self.n_samples, p=[0.25, 0.20, 0.35, 0.15, 0.05])
        
        # Income (correlated with education)
        income_mapping = {
            'High School': (20000, 50000),
            'Some College': (25000, 60000),
            'Bachelor\'s Degree': (35000, 80000),
            'Master\'s Degree': (50000, 120000),
            'Doctorate/Professional': (70000, 200000)
        }
        
        income = np.zeros(self.n_samples)
        for i, edu in enumerate(education):
            low, high = income_mapping[edu]
            inc = np.random.normal((low + high) / 2, (high - low) / 6)
            income[i] = max(15000, int(inc))
        
        # Technology comfort (1-7 scale)
        tech_comfort = np.random.normal(5.2, 1.3, self.n_samples)
        tech_comfort = np.clip(tech_comfort, 1, 7)
        
        # Previous fraud experience
        fraud_experience = np.random.choice([0, 1], self.n_samples, p=[0.75, 0.25])
        
        self.data.update({
            'participant_id': range(1, self.n_samples + 1),
            'age': age,
            'gender': gender,
            'education': education,
            'income': income,
            'tech_comfort': tech_comfort,
            'fraud_experience': fraud_experience
        })
        
    def generate_tpb_constructs(self):
        """Generate Theory of Planned Behavior constructs"""
        print("Generating TPB constructs...")
        
        # Create base personality/attitude factor
        base_attitude = np.random.normal(0, 1, self.n_samples)
        
        # Attitude (ATT) - 3 items
        # Correlate with tech comfort and fraud experience
        att_base = (base_attitude + 
                  0.3 * (self.data['tech_comfort'] - 4) + 
                  0.2 * self.data['fraud_experience'] + 
                  np.random.normal(0, 0.8, self.n_samples))
        
        att1 = np.clip(att_base + np.random.normal(0, 0.5, self.n_samples), 1, 7)
        att2 = np.clip(att_base + np.random.normal(0, 0.5, self.n_samples), 1, 7)
        att3 = np.clip(att_base + np.random.normal(0, 0.5, self.n_samples), 1, 7)
        
        # Subjective Norm (SN) - 2 items
        # Correlate with age and education
        education_numeric = pd.Series(self.data['education']).map({
            'High School': 1, 'Some College': 2, 'Bachelor\'s Degree': 3,
            'Master\'s Degree': 4, 'Doctorate/Professional': 5
        }).values
        
        sn_base = (base_attitude * 0.4 + 
                  0.2 * (self.data['age'] - 40) / 20 + 
                  0.3 * (education_numeric - 3) + 
                  np.random.normal(0, 0.7, self.n_samples))
        
        sn1 = np.clip(sn_base + np.random.normal(0, 0.4, self.n_samples), 1, 7)
        sn2 = np.clip(sn_base + np.random.normal(0, 0.4, self.n_samples), 1, 7)
        
        # Perceived Behavioral Control (PBC) - 3 items
        # Correlate with tech comfort and income
        pbc_base = (base_attitude * 0.3 + 
                   0.4 * (self.data['tech_comfort'] - 4) + 
                   0.2 * (self.data['income'] - 50000) / 50000 + 
                   np.random.normal(0, 0.6, self.n_samples))
        
        pbc1 = np.clip(pbc_base + np.random.normal(0, 0.4, self.n_samples), 1, 7)
        pbc2 = np.clip(pbc_base + np.random.normal(0, 0.4, self.n_samples), 1, 7)
        pbc3 = np.clip(pbc_base + np.random.normal(0, 0.4, self.n_samples), 1, 7)
        
        # Intention (INT) - 2 items
        # Main dependent variable - influenced by all TPB constructs
        intention_base = (0.3 * att_base + 
                         0.25 * sn_base + 
                         0.35 * pbc_base + 
                         np.random.normal(0, 0.5, self.n_samples))
        
        int1 = np.clip(intention_base + np.random.normal(0, 0.3, self.n_samples), 1, 7)
        int2 = np.clip(intention_base + np.random.normal(0, 0.3, self.n_samples), 1, 7)
        
        self.data.update({
            'ATT1': att1,
            'ATT2': att2, 
            'ATT3': att3,
            'SN1': sn1,
            'SN2': sn2,
            'PBC1': pbc1,
            'PBC2': pbc2,
            'PBC3': pbc3,
            'INT1': int1,
            'INT2': int2
        })
        
    def generate_pmt_constructs(self):
        """Generate Protection Motivation Theory constructs"""
        print("Generating PMT constructs...")
        
        # Threat Appraisal
        # Perceived Severity - influenced by income and fraud experience
        severity_base = (0.4 * (self.data['income'] - 50000) / 50000 + 
                       0.3 * self.data['fraud_experience'] + 
                       np.random.normal(0, 0.8, self.n_samples))
        
        perceived_severity = np.clip(severity_base + np.random.normal(0, 0.4, self.n_samples), 1, 7)
        
        # Perceived Vulnerability - influenced by age and tech comfort
        vulnerability_base = (0.3 * (80 - self.data['age']) / 40 +  # older = more vulnerable
                            0.2 * (8 - self.data['tech_comfort']) +  # lower tech comfort = more vulnerable
                            np.random.normal(0, 0.7, self.n_samples))
        
        perceived_vulnerability = np.clip(vulnerability_base + np.random.normal(0, 0.4, self.n_samples), 1, 7)
        
        # Coping Appraisal
        # Self Efficacy - correlate with PBC and tech comfort
        self_efficacy_base = (0.4 * (self.data['PBC1'] + self.data['PBC2'] + self.data['PBC3']) / 3 + 
                             0.3 * (self.data['tech_comfort'] - 4) + 
                             np.random.normal(0, 0.6, self.n_samples))
        
        self_efficacy = np.clip(self_efficacy_base + np.random.normal(0, 0.3, self.n_samples), 1, 7)
        
        # Response Efficacy - correlate with attitude
        response_efficacy_base = (0.4 * (self.data['ATT1'] + self.data['ATT2'] + self.data['ATT3']) / 3 + 
                                 np.random.normal(0, 0.7, self.n_samples))
        
        response_efficacy = np.clip(response_efficacy_base + np.random.normal(0, 0.3, self.n_samples), 1, 7)
        
        # Past Behavior (Habit) - 1 item
        # Correlate with intention but add some noise for realistic gap
        past_behavior_base = (0.6 * (self.data['INT1'] + self.data['INT2']) / 2 + 
                             np.random.normal(0, 0.8, self.n_samples))
        
        past_behavior = np.clip(past_behavior_base + np.random.normal(0, 0.4, self.n_samples), 1, 7)
        
        self.data.update({
            'perceived_severity': perceived_severity,
            'perceived_vulnerability': perceived_vulnerability,
            'self_efficacy': self_efficacy,
            'response_efficacy': response_efficacy,
            'past_behavior': past_behavior
        })
        
    def generate_time2_behavior(self):
        """Generate Time 2 behavioral outcome data"""
        print("Generating Time 2 behavioral outcomes...")
        
        # Create composite scores for main predictors
        attitude_score = (self.data['ATT1'] + self.data['ATT2'] + self.data['ATT3']) / 3
        subjective_norm_score = (self.data['SN1'] + self.data['SN2']) / 2
        pbc_score = (self.data['PBC1'] + self.data['PBC2'] + self.data['PBC3']) / 3
        intention_score = (self.data['INT1'] + self.data['INT2']) / 2
        
        # Behavioral outcome influenced by intention, PBC, and past behavior
        # Add realistic intention-behavior gap
        behavior_base = (0.4 * intention_score + 
                        0.3 * pbc_score + 
                        0.2 * self.data['past_behavior'] + 
                        0.1 * attitude_score + 
                        np.random.normal(0, 0.8, self.n_samples))
        
        # Create multiple behavioral measures
        security_steps_followed = np.clip(behavior_base + np.random.normal(0, 0.3, self.n_samples), 1, 7)
        frequency_last_month = np.clip(behavior_base + np.random.normal(0, 0.4, self.n_samples), 1, 7)
        consistency_score = np.clip(behavior_base + np.random.normal(0, 0.3, self.n_samples), 1, 7)
        
        # Binary outcome (followed security steps: yes/no)
        behavior_binary = (behavior_base > np.percentile(behavior_base, 40)).astype(int)
        
        # Add some missing data for T2 (attrition)
        missing_t2 = np.random.choice([0, 1], self.n_samples, p=[0.85, 0.15])
        
        self.data.update({
            'T2_security_steps_followed': np.where(missing_t2, np.nan, security_steps_followed),
            'T2_frequency_last_month': np.where(missing_t2, np.nan, frequency_last_month),
            'T2_consistency_score': np.where(missing_t2, np.nan, consistency_score),
            'T2_behavior_binary': np.where(missing_t2, np.nan, behavior_binary),
            'T2_missing': missing_t2
        })
        
    def add_data_quality_features(self):
        """Add realistic data quality issues"""
        print("Adding data quality features...")
        
        # Response time simulation (in seconds)
        response_time = np.random.lognormal(3.5, 0.8, self.n_samples)
        self.data['response_time_seconds'] = response_time
        
        # Straight-lining detection (respondents who give same answer)
        straight_line_prob = 0.05  # 5% of respondents
        straight_line = np.random.choice([0, 1], self.n_samples, p=[1-straight_line_prob, straight_line_prob])
        
        # For straight-liners, set all Likert items to same value
        for i in range(self.n_samples):
            if straight_line[i]:
                value = np.random.choice([1, 4, 7], p=[0.1, 0.7, 0.2])  # Mostly middle responses
                for var in ['ATT1', 'ATT2', 'ATT3', 'SN1', 'SN2', 'PBC1', 'PBC2', 'PBC3', 'INT1', 'INT2']:
                    self.data[var][i] = value
        
        self.data['straight_line_respondent'] = straight_line
        
        # Missing data patterns
        missing_prob = 0.02  # 2% missing rate
        for var in ['ATT1', 'ATT2', 'ATT3', 'SN1', 'SN2', 'PBC1', 'PBC2', 'PBC3', 'INT1', 'INT2']:
            missing = np.random.choice([0, 1], self.n_samples, p=[1-missing_prob, missing_prob])
            self.data[var] = np.where(missing, np.nan, self.data[var])
        
        # Social desirability bias (slight inflation of positive responses)
        social_desirability = np.random.normal(0.2, 0.1, self.n_samples)
        for var in ['ATT1', 'ATT2', 'ATT3', 'SN1', 'SN2', 'PBC1', 'PBC2', 'PBC3', 'INT1', 'INT2']:
            self.data[var] = np.clip(self.data[var] + social_desirability, 1, 7)
        
    def create_composite_scores(self):
        """Create composite scores for analysis"""
        print("Creating composite scores...")
        
        # TPB Composite Scores
        self.data['attitude_composite'] = np.nanmean([
            self.data['ATT1'], self.data['ATT2'], self.data['ATT3']
        ], axis=0)
        
        self.data['subjective_norm_composite'] = np.nanmean([
            self.data['SN1'], self.data['SN2']
        ], axis=0)
        
        self.data['pbc_composite'] = np.nanmean([
            self.data['PBC1'], self.data['PBC2'], self.data['PBC3']
        ], axis=0)
        
        self.data['intention_composite'] = np.nanmean([
            self.data['INT1'], self.data['INT2']
        ], axis=0)
        
        # PMT Composite Scores
        self.data['threat_appraisal_composite'] = np.nanmean([
            self.data['perceived_severity'], self.data['perceived_vulnerability']
        ], axis=0)
        
        self.data['coping_appraisal_composite'] = np.nanmean([
            self.data['self_efficacy'], self.data['response_efficacy']
        ], axis=0)
        
    def generate_dataset(self):
        """Generate the complete dataset"""
        print(f"Generating comprehensive behavioral intention dataset with {self.n_samples} participants...")
        
        self.generate_demographics()
        self.generate_tpb_constructs()
        self.generate_pmt_constructs()
        self.generate_time2_behavior()
        self.add_data_quality_features()
        self.create_composite_scores()
        
        # Create DataFrame
        df = pd.DataFrame(self.data)
        
        # Round Likert scale items to integers
        likert_vars = ['ATT1', 'ATT2', 'ATT3', 'SN1', 'SN2', 'PBC1', 'PBC2', 'PBC3', 
                      'INT1', 'INT2', 'perceived_severity', 'perceived_vulnerability',
                      'self_efficacy', 'response_efficacy', 'past_behavior',
                      'T2_security_steps_followed', 'T2_frequency_last_month', 
                      'T2_consistency_score']
        
        for var in likert_vars:
            if var in df.columns:
                df[var] = df[var].round().astype('Int64')
        
        print("Dataset generation complete!")
        return df
    
    def save_dataset(self, df, filename='behavioral_intention_dataset.csv'):
        """Save dataset to CSV"""
        df.to_csv(filename, index=False)
        print(f"Dataset saved as {filename}")
        
    def generate_codebook(self, df, filename='dataset_codebook.txt'):
        """Generate comprehensive codebook"""
        codebook = f"""
BEHAVIORAL INTENTION DATASET CODEBOOK
=====================================

Dataset Overview:
- Sample Size: {len(df)} participants
- Variables: {len(df.columns)} total
- Missing Data: {df.isnull().sum().sum()} total missing values
- Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

VARIABLE DESCRIPTIONS:
=====================

DEMOGRAPHIC VARIABLES:
----------------------
participant_id: Unique identifier for each participant (1 to {len(df)})
age: Participant age in years (18-80)
gender: Gender identity (Female, Male, Other)
education: Highest level of education completed
income: Annual household income in USD
tech_comfort: Comfort with technology (1=Very Uncomfortable, 7=Very Comfortable)
fraud_experience: Previous experience with fraud (0=No, 1=Yes)

THEORY OF PLANNED BEHAVIOR (TPB) CONSTRUCTS:
--------------------------------------------
All items measured on 7-point Likert scales (1=Strongly Disagree, 7=Strongly Agree)

Attitude (ATT):
- ATT1: Following bank security steps is beneficial/harmful
- ATT2: Following bank security steps is wise/foolish  
- ATT3: Following bank security steps is important/unimportant
- attitude_composite: Mean of ATT1, ATT2, ATT3

Subjective Norm (SN):
- SN1: Most people who are important to me think I should follow these steps
- SN2: My family expects me to be diligent with my bank security
- subjective_norm_composite: Mean of SN1, SN2

Perceived Behavioral Control (PBC):
- PBC1: For me, following all the security steps would be easy/difficult
- PBC2: I have the resources, time, and knowledge to follow them
- PBC3: Whether I follow them is entirely up to me
- pbc_composite: Mean of PBC1, PBC2, PBC3

Intention (INT):
- INT1: I intend to follow all recommended security steps in the next 3 months
- INT2: I plan to make an effort to be more diligent
- intention_composite: Mean of INT1, INT2

PROTECTION MOTIVATION THEORY (PMT) CONSTRUCTS:
----------------------------------------------
All items measured on 7-point Likert scales (1=Strongly Disagree, 7=Strongly Agree)

Threat Appraisal:
- perceived_severity: The financial loss from fraud would be severe for me
- perceived_vulnerability: I am at high risk of experiencing bank fraud
- threat_appraisal_composite: Mean of perceived_severity, perceived_vulnerability

Coping Appraisal:
- self_efficacy: I am confident I can perform the security steps correctly
- response_efficacy: I believe these security steps are effective in protecting me
- coping_appraisal_composite: Mean of self_efficacy, response_efficacy

Past Behavior:
- past_behavior: In the past 3 months, how often have you followed recommended security steps? (1=Never, 7=Always)

TIME 2 (T2) BEHAVIORAL OUTCOMES:
-------------------------------
T2_security_steps_followed: Self-reported security behavior (1=Never, 7=Always)
T2_frequency_last_month: Frequency of security behavior in last month (1=Never, 7=Always)
T2_consistency_score: Consistency of security behavior (1=Very Inconsistent, 7=Very Consistent)
T2_behavior_binary: Binary behavioral outcome (0=Did not follow, 1=Followed security steps)
T2_missing: Missing data indicator for T2 (0=Present, 1=Missing)

DATA QUALITY INDICATORS:
-----------------------
response_time_seconds: Time taken to complete survey (in seconds)
straight_line_respondent: Indicator for potential straight-lining (0=No, 1=Yes)

STATISTICAL PROPERTIES:
======================
"""
        
        # Add descriptive statistics
        numeric_vars = df.select_dtypes(include=[np.number]).columns
        desc_stats = df[numeric_vars].describe()
        
        codebook += "\nDescriptive Statistics:\n"
        codebook += desc_stats.to_string()
        
        codebook += f"""

CORRELATION MATRIX (Key Constructs):
===================================
"""
        
        key_constructs = ['attitude_composite', 'subjective_norm_composite', 'pbc_composite', 
                         'intention_composite', 'threat_appraisal_composite', 'coping_appraisal_composite',
                         'past_behavior', 'T2_security_steps_followed']
        
        corr_matrix = df[key_constructs].corr()
        codebook += corr_matrix.to_string()
        
        codebook += f"""

RESEARCH APPLICATIONS:
=====================
1. Test Theory of Planned Behavior model
2. Examine intention-behavior gap
3. Factor analysis of measurement scales
4. Mediation and moderation analyses
5. Protection Motivation Theory integration
6. Demographic differences in security behavior
7. Longitudinal behavior prediction

CITATION:
=========
Generated dataset for behavioral intention research.
Based on Theory of Planned Behavior (Ajzen, 1991) and 
Protection Motivation Theory (Rogers, 1975).

For questions about this dataset, please refer to the 
accompanying analysis scripts and documentation.
"""
        
        with open(filename, 'w') as f:
            f.write(codebook)
        
        print(f"Codebook saved as {filename}")

def main():
    """Main function to generate and save the dataset"""
    # Generate dataset
    generator = BehavioralIntentionDatasetGenerator(n_samples=2000, random_seed=42)
    df = generator.generate_dataset()
    
    # Save dataset
    generator.save_dataset(df, 'behavioral_intention_dataset.csv')
    
    # Generate codebook
    generator.generate_codebook(df, 'dataset_codebook.txt')
    
    # Display basic info
    print(f"\nDataset Summary:")
    print(f"Shape: {df.shape}")
    print(f"Missing values: {df.isnull().sum().sum()}")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Show first few rows
    print(f"\nFirst 5 rows:")
    print(df.head())
    
    return df

if __name__ == "__main__":
    df = main()