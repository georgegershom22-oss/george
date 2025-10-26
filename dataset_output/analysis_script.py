
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
print("\nKey Findings:")
print(f"Mean intention-behavior gap: {df['t2_intention_behavior_gap'].mean():.3f}")
print(f"Gap standard deviation: {df['t2_intention_behavior_gap'].std():.3f}")
print(f"Overperformers: {(df['t2_gap_category'] == 'Overperformer').sum()}")
print(f"Underperformers: {(df['t2_gap_category'] == 'Underperformer').sum()}")

# PBC moderation analysis
print("\nPBC Moderation Analysis:")
pbc_high = df[df['t1_pbc'] >= df['t1_pbc'].median()]
pbc_low = df[df['t1_pbc'] < df['t1_pbc'].median()]
print(f"High PBC gap mean: {pbc_high['t2_intention_behavior_gap'].mean():.3f}")
print(f"Low PBC gap mean: {pbc_low['t2_intention_behavior_gap'].mean():.3f}")

# Self-report vs objective behavior correlation
print(f"\nSRB-Objective correlation: {df['t2_srb_composite'].corr(df['t2_objective_score']):.3f}")
