"""
Banking Security Behavior Dataset Generator
Based on Theory of Planned Behavior (TPB) Framework
Generates Time 1 (Predictors) and Time 2 (Behavioral Outcomes) data
"""

import numpy as np
import pandas as pd
from scipy import stats
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Sample size
N = 350

print("="*80)
print("BANKING SECURITY BEHAVIOR DATASET GENERATOR")
print("Theory of Planned Behavior Framework")
print("="*80)
print(f"\nGenerating dataset with N = {N} participants...")

# ============================================================================
# DEMOGRAPHICS & CONTROL VARIABLES
# ============================================================================
print("\n[1/7] Generating demographic variables...")

# Participant ID
participant_id = [f"P{str(i+1).zfill(4)}" for i in range(N)]

# Age: 18-75, normally distributed around 40
age = np.clip(np.random.normal(40, 15, N), 18, 75).astype(int)

# Gender: 0=Male, 1=Female, 2=Other
gender = np.random.choice([0, 1, 2], N, p=[0.48, 0.50, 0.02])

# Education: 1=High School or less, 2=Some College, 3=Bachelor's, 4=Graduate
education = np.random.choice([1, 2, 3, 4], N, p=[0.15, 0.25, 0.40, 0.20])

# Prior fraud experience: 0=No, 1=Yes
prior_fraud = np.random.choice([0, 1], N, p=[0.72, 0.28])

# Tech savviness (1-7 scale)
tech_savvy = np.random.choice(range(1, 8), N, p=[0.05, 0.08, 0.12, 0.20, 0.25, 0.20, 0.10])

# Time between T1 and T2 (days) - typically 30 days
time_lag_days = np.random.normal(30, 3, N).astype(int)

# ============================================================================
# TIME 1 (T1) VARIABLES - PREDICTORS
# ============================================================================
print("[2/7] Generating Time 1 (T1) predictor variables...")

# Base correlation matrix for TPB constructs
# We'll use this to generate correlated data

def generate_correlated_likert(n, n_items, mean_latent, std_latent, correlation_matrix):
    """Generate correlated Likert-scale items"""
    # Generate correlated latent variables
    latent = np.random.multivariate_normal(
        mean=[mean_latent] * n_items,
        cov=correlation_matrix * (std_latent ** 2),
        size=n
    )
    # Convert to Likert scale (1-7)
    items = np.clip(np.round(latent), 1, 7).astype(int)
    return items

# ATTITUDES (ATT1-ATT5)
# "Using strong banking security practices is..."
# 1=Extremely harmful to 7=Extremely beneficial
att_corr = np.array([
    [1.0, 0.7, 0.6, 0.65, 0.6],
    [0.7, 1.0, 0.65, 0.6, 0.65],
    [0.6, 0.65, 1.0, 0.7, 0.6],
    [0.65, 0.6, 0.7, 1.0, 0.65],
    [0.6, 0.65, 0.6, 0.65, 1.0]
])
attitudes = generate_correlated_likert(N, 5, 5.5, 1.0, att_corr)

# SUBJECTIVE NORMS (SN1-SN4)
# "People important to me think I should use strong banking security"
sn_corr = np.array([
    [1.0, 0.75, 0.65, 0.6],
    [0.75, 1.0, 0.7, 0.65],
    [0.65, 0.7, 1.0, 0.7],
    [0.6, 0.65, 0.7, 1.0]
])
subjective_norms = generate_correlated_likert(N, 4, 5.0, 1.1, sn_corr)

# PERCEIVED BEHAVIORAL CONTROL (PBC1-PBC5) - KEY MODERATOR
# "I am confident I can use strong banking security practices"
# This is theorized to moderate the intention-behavior relationship
pbc_corr = np.array([
    [1.0, 0.8, 0.7, 0.65, 0.7],
    [0.8, 1.0, 0.75, 0.7, 0.65],
    [0.7, 0.75, 1.0, 0.7, 0.7],
    [0.65, 0.7, 0.7, 1.0, 0.65],
    [0.7, 0.65, 0.7, 0.65, 1.0]
])
pbc = generate_correlated_likert(N, 5, 5.2, 1.2, pbc_corr)

# INTENTIONS (INT1-INT4)
# "I intend to use strong banking security practices in the next month"
# Intentions should be predicted by ATT, SN, and PBC
# Generate with realistic TPB relationships
att_mean = attitudes.mean(axis=1)
sn_mean = subjective_norms.mean(axis=1)
pbc_mean = pbc.mean(axis=1)

# TPB model: INT = b0 + b1*ATT + b2*SN + b3*PBC + error
# Standard TPB weights (approximately)
intention_latent = (
    1.5 +  # intercept
    0.35 * att_mean +
    0.25 * sn_mean +
    0.30 * pbc_mean +
    np.random.normal(0, 0.6, N)
)

int_corr = np.array([
    [1.0, 0.8, 0.75, 0.7],
    [0.8, 1.0, 0.8, 0.75],
    [0.75, 0.8, 1.0, 0.75],
    [0.7, 0.75, 0.75, 1.0]
])
intentions_base = generate_correlated_likert(N, 4, 5.0, 1.0, int_corr)
# Adjust intentions to correlate with predictors
intentions = np.clip(
    0.4 * intentions_base + 0.6 * intention_latent[:, np.newaxis],
    1, 7
).astype(int)

# ============================================================================
# TIME 2 (T2) VARIABLES - BEHAVIORAL OUTCOMES (DEPENDENT VARIABLES)
# ============================================================================
print("[3/7] Generating Time 2 (T2) behavioral outcome variables...")

# Mean intention score (will be primary predictor of behavior)
intention_mean = intentions.mean(axis=1)

# SELF-REPORTED BEHAVIOR (SRB1-SRB5)
# Over the last month, how often did you:
# 1. Check your bank statement for unauthorized transactions?
# 2. Use strong, unique passwords for banking?
# 3. Enable two-factor authentication?
# 4. Log out of banking apps/sites after use?
# 5. Verify a text/email alert before clicking a link?

# Key insight: Behavior should correlate with intention, but NOT perfectly
# PBC should moderate this relationship (high PBC = smaller intention-behavior gap)

# Base behavioral tendency from intentions and PBC
behavior_latent = (
    0.8 +
    0.50 * intention_mean +  # Intention effect
    0.20 * pbc_mean +  # Direct PBC effect
    0.10 * (intention_mean * pbc_mean) +  # INTERACTION (moderation)
    0.08 * tech_savvy +  # Tech savviness helps
    0.15 * prior_fraud +  # Prior fraud experience increases behavior
    np.random.normal(0, 0.8, N)  # Random error
)

srb_corr = np.array([
    [1.0, 0.65, 0.55, 0.6, 0.65],
    [0.65, 1.0, 0.6, 0.55, 0.6],
    [0.55, 0.6, 1.0, 0.55, 0.5],
    [0.6, 0.55, 0.55, 1.0, 0.65],
    [0.65, 0.6, 0.5, 0.65, 1.0]
])
srb_base = generate_correlated_likert(N, 5, 4.8, 1.1, srb_corr)

# Blend with behavioral latent variable
srb = np.clip(
    0.35 * srb_base + 0.65 * behavior_latent[:, np.newaxis],
    1, 7
).astype(int)

# ============================================================================
# OBJECTIVE BEHAVIORAL MEASURE - Scenario-Based Quiz
# ============================================================================
print("[4/7] Generating objective behavioral measures (scenario quiz)...")

# Scenario 1: Phishing SMS
# You receive: "Your account is locked. Click here: bit.ly/..."
# a) Click immediately (0), b) Call bank (2), c) Ignore (1)
def scenario1(intention, pbc, tech, prior_fraud):
    # Higher intention, PBC, tech savviness = better choice
    score_tendency = 0.3*intention + 0.4*pbc + 0.2*tech + 0.3*prior_fraud
    if score_tendency + np.random.normal(0, 1.5) > 5.5:
        return 2  # Best choice
    elif score_tendency + np.random.normal(0, 1.2) > 4.0:
        return 1  # Okay choice
    else:
        return 0  # Poor choice

# Scenario 2: Email with attachment
# You receive email "Invoice attached" from unknown sender
# a) Open attachment (0), b) Delete (2), c) Reply asking who sent it (1)
def scenario2(intention, pbc, tech, prior_fraud):
    score_tendency = 0.25*intention + 0.35*pbc + 0.25*tech + 0.35*prior_fraud
    if score_tendency + np.random.normal(0, 1.4) > 5.3:
        return 2
    elif score_tendency + np.random.normal(0, 1.3) > 3.8:
        return 1
    else:
        return 0

# Scenario 3: Public WiFi banking
# You're at a café with public WiFi. Need to check balance urgently.
# a) Use public WiFi (0), b) Use mobile data (2), c) Wait until home (2)
def scenario3(intention, pbc, tech, prior_fraud):
    score_tendency = 0.35*intention + 0.30*pbc + 0.20*tech + 0.25*prior_fraud
    if score_tendency + np.random.normal(0, 1.5) > 5.0:
        return 2
    elif score_tendency + np.random.normal(0, 1.3) > 3.5:
        return 1
    else:
        return 0

# Scenario 4: Sharing password
# Friend asks to use your banking app to check something
# a) Share password (0), b) Refuse politely (2), c) Share but change later (1)
def scenario4(intention, pbc, tech, prior_fraud):
    score_tendency = 0.40*intention + 0.35*pbc + 0.15*tech + 0.20*prior_fraud
    if score_tendency + np.random.normal(0, 1.6) > 5.4:
        return 2
    elif score_tendency + np.random.normal(0, 1.2) > 4.0:
        return 1
    else:
        return 0

# Scenario 5: Two-factor authentication prompt
# Bank offers 2FA. Takes 5 mins to set up.
# a) Skip for now (0), b) Set up immediately (2), c) Remind me later (1)
def scenario5(intention, pbc, tech, prior_fraud):
    score_tendency = 0.30*intention + 0.45*pbc + 0.30*tech + 0.15*prior_fraud
    if score_tendency + np.random.normal(0, 1.5) > 5.2:
        return 2
    elif score_tendency + np.random.normal(0, 1.4) > 3.7:
        return 1
    else:
        return 0

# Generate scenario scores
scenario_1 = np.array([scenario1(intention_mean[i], pbc_mean[i], tech_savvy[i], prior_fraud[i]) for i in range(N)])
scenario_2 = np.array([scenario2(intention_mean[i], pbc_mean[i], tech_savvy[i], prior_fraud[i]) for i in range(N)])
scenario_3 = np.array([scenario3(intention_mean[i], pbc_mean[i], tech_savvy[i], prior_fraud[i]) for i in range(N)])
scenario_4 = np.array([scenario4(intention_mean[i], pbc_mean[i], tech_savvy[i], prior_fraud[i]) for i in range(N)])
scenario_5 = np.array([scenario5(intention_mean[i], pbc_mean[i], tech_savvy[i], prior_fraud[i]) for i in range(N)])

# Total objective score (0-10 scale)
objective_score = scenario_1 + scenario_2 + scenario_3 + scenario_4 + scenario_5

# ============================================================================
# BEHAVIORAL GAP CALCULATION (CRITICAL FOR RESEARCH QUESTION)
# ============================================================================
print("[5/7] Calculating Intention-Behavior Gap (residual analysis)...")

# The behavioral gap is operationalized as the residual from regressing
# T2 behavior on T1 intention

# Compute mean SRB as the overall behavioral measure
srb_mean = srb.mean(axis=1)

# Regression: SRB_mean = b0 + b1*Intention_mean + residuals
from sklearn.linear_model import LinearRegression

# Fit the model
X_int = intention_mean.reshape(-1, 1)
y_srb = srb_mean

model = LinearRegression()
model.fit(X_int, y_srb)

# Get predictions and residuals
predicted_behavior = model.predict(X_int)
intention_behavior_gap = y_srb - predicted_behavior

# Positive gap = performed BETTER than intention predicted
# Negative gap = performed WORSE than intention predicted (the problematic gap)

print(f"   Regression R² = {model.score(X_int, y_srb):.3f}")
print(f"   Intention coefficient = {model.coef_[0]:.3f}")
print(f"   Gap: Mean = {intention_behavior_gap.mean():.3f}, SD = {intention_behavior_gap.std():.3f}")

# ============================================================================
# ADDITIONAL CALCULATED VARIABLES
# ============================================================================
print("[6/7] Computing composite scores and additional variables...")

# Composite scores (means)
att_mean = attitudes.mean(axis=1)
sn_mean = subjective_norms.mean(axis=1)
pbc_mean_calc = pbc.mean(axis=1)
int_mean = intention_mean
srb_mean_calc = srb_mean

# Standardized scores (z-scores) for analysis
att_z = (att_mean - att_mean.mean()) / att_mean.std()
sn_z = (sn_mean - sn_mean.mean()) / sn_mean.std()
pbc_z = (pbc_mean_calc - pbc_mean_calc.mean()) / pbc_mean_calc.std()
int_z = (int_mean - int_mean.mean()) / int_mean.std()
srb_z = (srb_mean_calc - srb_mean_calc.mean()) / srb_mean_calc.std()
obj_z = (objective_score - objective_score.mean()) / objective_score.std()

# Behavioral consistency score (how consistent are SRB responses?)
# Lower SD = more consistent
srb_consistency = srb.std(axis=1)

# Gap magnitude (absolute value)
gap_magnitude = np.abs(intention_behavior_gap)

# Gap direction: 1 = over-performer, 0 = matched, -1 = under-performer
gap_direction = np.where(intention_behavior_gap > 0.3, 1, 
                         np.where(intention_behavior_gap < -0.3, -1, 0))

# ============================================================================
# CREATE DATAFRAME
# ============================================================================
print("[7/7] Assembling final dataset...")

data = {
    # Identifiers
    'ParticipantID': participant_id,
    
    # Demographics & Controls
    'Age': age,
    'Gender': gender,  # 0=Male, 1=Female, 2=Other
    'Education': education,  # 1=HS, 2=Some College, 3=Bachelor, 4=Graduate
    'Prior_Fraud_Experience': prior_fraud,  # 0=No, 1=Yes
    'Tech_Savviness': tech_savvy,  # 1-7
    'T1_T2_TimeLag_Days': time_lag_days,
    
    # TIME 1: Attitudes (1-7 scale)
    'T1_ATT1': attitudes[:, 0],
    'T1_ATT2': attitudes[:, 1],
    'T1_ATT3': attitudes[:, 2],
    'T1_ATT4': attitudes[:, 3],
    'T1_ATT5': attitudes[:, 4],
    'T1_ATT_Mean': att_mean,
    'T1_ATT_Z': att_z,
    
    # TIME 1: Subjective Norms (1-7 scale)
    'T1_SN1': subjective_norms[:, 0],
    'T1_SN2': subjective_norms[:, 1],
    'T1_SN3': subjective_norms[:, 2],
    'T1_SN4': subjective_norms[:, 3],
    'T1_SN_Mean': sn_mean,
    'T1_SN_Z': sn_z,
    
    # TIME 1: Perceived Behavioral Control (1-7 scale) ***KEY MODERATOR***
    'T1_PBC1': pbc[:, 0],
    'T1_PBC2': pbc[:, 1],
    'T1_PBC3': pbc[:, 2],
    'T1_PBC4': pbc[:, 3],
    'T1_PBC5': pbc[:, 4],
    'T1_PBC_Mean': pbc_mean_calc,
    'T1_PBC_Z': pbc_z,
    
    # TIME 1: Intentions (1-7 scale)
    'T1_INT1': intentions[:, 0],
    'T1_INT2': intentions[:, 1],
    'T1_INT3': intentions[:, 2],
    'T1_INT4': intentions[:, 3],
    'T1_INT_Mean': int_mean,
    'T1_INT_Z': int_z,
    
    # TIME 2: Self-Reported Behavior (1-7 scale) ***PRIMARY DV***
    'T2_SRB1_CheckStatements': srb[:, 0],
    'T2_SRB2_StrongPasswords': srb[:, 1],
    'T2_SRB3_TwoFactorAuth': srb[:, 2],
    'T2_SRB4_LogOut': srb[:, 3],
    'T2_SRB5_VerifyAlerts': srb[:, 4],
    'T2_SRB_Mean': srb_mean_calc,
    'T2_SRB_Z': srb_z,
    'T2_SRB_Consistency': srb_consistency,
    
    # TIME 2: Objective Behavioral Measure (0-2 per scenario, 0-10 total)
    'T2_Scenario1_PhishingSMS': scenario_1,
    'T2_Scenario2_EmailAttachment': scenario_2,
    'T2_Scenario3_PublicWiFi': scenario_3,
    'T2_Scenario4_PasswordSharing': scenario_4,
    'T2_Scenario5_Enable2FA': scenario_5,
    'T2_Objective_Score': objective_score,
    'T2_Objective_Z': obj_z,
    
    # TIME 2: BEHAVIORAL GAP (THE CORE CONSTRUCT) ***CRITICAL DV***
    'T2_Intention_Behavior_Gap': intention_behavior_gap,
    'T2_Gap_Magnitude': gap_magnitude,
    'T2_Gap_Direction': gap_direction,  # 1=over, 0=matched, -1=under
}

df = pd.DataFrame(data)

# ============================================================================
# DATA QUALITY CHECKS
# ============================================================================
print("\n" + "="*80)
print("DATA QUALITY CHECKS")
print("="*80)

print(f"\n✓ Total participants: {len(df)}")
print(f"✓ No missing values: {df.isnull().sum().sum() == 0}")
print(f"✓ All Likert items in range 1-7: {df.filter(regex='T[12]_(ATT|SN|PBC|INT|SRB)[0-9]').apply(lambda x: x.min() >= 1 and x.max() <= 7).all()}")

print("\n--- Key Correlations (Theory Check) ---")
print(f"Attitude → Intention: r = {df['T1_ATT_Mean'].corr(df['T1_INT_Mean']):.3f}")
print(f"Subjective Norm → Intention: r = {df['T1_SN_Mean'].corr(df['T1_INT_Mean']):.3f}")
print(f"PBC → Intention: r = {df['T1_PBC_Mean'].corr(df['T1_INT_Mean']):.3f}")
print(f"Intention → Behavior (SRB): r = {df['T1_INT_Mean'].corr(df['T2_SRB_Mean']):.3f}")
print(f"PBC → Behavior (SRB): r = {df['T1_PBC_Mean'].corr(df['T2_SRB_Mean']):.3f}")
print(f"Intention → Objective Score: r = {df['T1_INT_Mean'].corr(df['T2_Objective_Score']):.3f}")
print(f"SRB ↔ Objective Score: r = {df['T2_SRB_Mean'].corr(df['T2_Objective_Score']):.3f}")

print("\n--- Behavioral Gap Statistics ---")
print(f"Mean Gap: {df['T2_Intention_Behavior_Gap'].mean():.4f}")
print(f"SD Gap: {df['T2_Intention_Behavior_Gap'].std():.4f}")
print(f"Over-performers (Gap>0.3): {(df['T2_Gap_Direction']==1).sum()} ({(df['T2_Gap_Direction']==1).sum()/len(df)*100:.1f}%)")
print(f"Matched performers (|Gap|<0.3): {(df['T2_Gap_Direction']==0).sum()} ({(df['T2_Gap_Direction']==0).sum()/len(df)*100:.1f}%)")
print(f"Under-performers (Gap<-0.3): {(df['T2_Gap_Direction']==-1).sum()} ({(df['T2_Gap_Direction']==-1).sum()/len(df)*100:.1f}%)")

print("\n--- Descriptive Statistics ---")
print(f"Age: M={df['Age'].mean():.1f}, SD={df['Age'].std():.1f}, Range={df['Age'].min()}-{df['Age'].max()}")
print(f"T1 Intentions: M={df['T1_INT_Mean'].mean():.2f}, SD={df['T1_INT_Mean'].std():.2f}")
print(f"T1 PBC: M={df['T1_PBC_Mean'].mean():.2f}, SD={df['T1_PBC_Mean'].std():.2f}")
print(f"T2 Self-Reported Behavior: M={df['T2_SRB_Mean'].mean():.2f}, SD={df['T2_SRB_Mean'].std():.2f}")
print(f"T2 Objective Score: M={df['T2_Objective_Score'].mean():.2f}, SD={df['T2_Objective_Score'].std():.2f}")

# ============================================================================
# SAVE DATASET
# ============================================================================
output_file = '/workspace/banking_security_behavior_dataset.csv'
df.to_csv(output_file, index=False)
print("\n" + "="*80)
print(f"✓ Dataset saved: {output_file}")
print("="*80)

# Quick preview
print("\nFirst 5 rows (selected columns):")
preview_cols = ['ParticipantID', 'Age', 'Gender', 'T1_INT_Mean', 'T1_PBC_Mean', 
                'T2_SRB_Mean', 'T2_Objective_Score', 'T2_Intention_Behavior_Gap']
print(df[preview_cols].head().to_string(index=False))

print("\n✓ Dataset generation complete!")
