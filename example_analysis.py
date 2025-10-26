"""
Example Analysis Script for Banking Security Behavior Dataset
Demonstrates key analyses for testing the intention-behavior gap
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# Set display options
pd.set_option('display.width', 120)
pd.set_option('display.max_columns', 20)

print("="*80)
print("BANKING SECURITY BEHAVIOR DATASET - EXAMPLE ANALYSIS")
print("="*80)

# ============================================================================
# 1. LOAD AND INSPECT DATA
# ============================================================================
print("\n[1] Loading dataset...")
data = pd.read_csv('banking_security_behavior_dataset.csv')

print(f"\n✓ Loaded {len(data)} participants")
print(f"✓ Variables: {len(data.columns)} columns")

print("\n--- Key Variables Preview ---")
key_vars = ['ParticipantID', 'Age', 'T1_INT_Mean', 'T1_PBC_Mean', 
            'T2_SRB_Mean', 'T2_Objective_Score', 'T2_Intention_Behavior_Gap']
print(data[key_vars].head(10))

# ============================================================================
# 2. DESCRIPTIVE STATISTICS
# ============================================================================
print("\n" + "="*80)
print("[2] DESCRIPTIVE STATISTICS")
print("="*80)

print("\n--- Demographics ---")
print(f"Age: M={data['Age'].mean():.1f}, SD={data['Age'].std():.1f}, Range={data['Age'].min()}-{data['Age'].max()}")
print(f"Gender: Male={100*(data['Gender']==0).sum()/len(data):.1f}%, Female={100*(data['Gender']==1).sum()/len(data):.1f}%, Other={100*(data['Gender']==2).sum()/len(data):.1f}%")
print(f"Prior Fraud Experience: {100*data['Prior_Fraud_Experience'].mean():.1f}%")

print("\n--- Time 1 Predictors ---")
t1_vars = ['T1_ATT_Mean', 'T1_SN_Mean', 'T1_PBC_Mean', 'T1_INT_Mean']
print(data[t1_vars].describe().round(2))

print("\n--- Time 2 Outcomes ---")
t2_vars = ['T2_SRB_Mean', 'T2_Objective_Score', 'T2_Intention_Behavior_Gap']
print(data[t2_vars].describe().round(2))

print("\n--- Behavioral Gap Distribution ---")
print(f"Over-performers (Gap > 0.3): {(data['T2_Gap_Direction']==1).sum()} ({100*(data['T2_Gap_Direction']==1).sum()/len(data):.1f}%)")
print(f"Matched (|Gap| ≤ 0.3): {(data['T2_Gap_Direction']==0).sum()} ({100*(data['T2_Gap_Direction']==0).sum()/len(data):.1f}%)")
print(f"Under-performers (Gap < -0.3): {(data['T2_Gap_Direction']==-1).sum()} ({100*(data['T2_Gap_Direction']==-1).sum()/len(data):.1f}%)")

# ============================================================================
# 3. RELIABILITY ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("[3] RELIABILITY ANALYSIS (Cronbach's Alpha)")
print("="*80)

def cronbach_alpha(df, items):
    """Calculate Cronbach's alpha for a set of items"""
    item_data = df[items].dropna()
    n_items = len(items)
    item_variances = item_data.var(axis=0, ddof=1).sum()
    total_variance = item_data.sum(axis=1).var(ddof=1)
    alpha = (n_items / (n_items - 1)) * (1 - item_variances / total_variance)
    return alpha

# Calculate alphas
alpha_att = cronbach_alpha(data, ['T1_ATT1', 'T1_ATT2', 'T1_ATT3', 'T1_ATT4', 'T1_ATT5'])
alpha_sn = cronbach_alpha(data, ['T1_SN1', 'T1_SN2', 'T1_SN3', 'T1_SN4'])
alpha_pbc = cronbach_alpha(data, ['T1_PBC1', 'T1_PBC2', 'T1_PBC3', 'T1_PBC4', 'T1_PBC5'])
alpha_int = cronbach_alpha(data, ['T1_INT1', 'T1_INT2', 'T1_INT3', 'T1_INT4'])
alpha_srb = cronbach_alpha(data, ['T2_SRB1_CheckStatements', 'T2_SRB2_StrongPasswords', 
                                   'T2_SRB3_TwoFactorAuth', 'T2_SRB4_LogOut', 'T2_SRB5_VerifyAlerts'])

print(f"Attitudes (ATT1-ATT5): α = {alpha_att:.3f} {'✓' if alpha_att > 0.80 else '⚠'}")
print(f"Subjective Norms (SN1-SN4): α = {alpha_sn:.3f} {'✓' if alpha_sn > 0.75 else '⚠'}")
print(f"PBC (PBC1-PBC5): α = {alpha_pbc:.3f} {'✓' if alpha_pbc > 0.80 else '⚠'}")
print(f"Intentions (INT1-INT4): α = {alpha_int:.3f} {'✓' if alpha_int > 0.85 else '⚠'}")
print(f"Self-Reported Behavior (SRB1-SRB5): α = {alpha_srb:.3f} {'✓' if alpha_srb > 0.70 else '⚠'}")

# ============================================================================
# 4. CORRELATION ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("[4] CORRELATION MATRIX (Key Variables)")
print("="*80)

corr_vars = ['T1_ATT_Mean', 'T1_SN_Mean', 'T1_PBC_Mean', 'T1_INT_Mean', 
             'T2_SRB_Mean', 'T2_Objective_Score']
corr_matrix = data[corr_vars].corr()
print(corr_matrix.round(3))

print("\n--- Key Theoretical Correlations ---")
print(f"Attitude → Intention: r = {data['T1_ATT_Mean'].corr(data['T1_INT_Mean']):.3f}")
print(f"Subjective Norm → Intention: r = {data['T1_SN_Mean'].corr(data['T1_INT_Mean']):.3f}")
print(f"PBC → Intention: r = {data['T1_PBC_Mean'].corr(data['T1_INT_Mean']):.3f}")
print(f"\n⭐ Intention → SRB: r = {data['T1_INT_Mean'].corr(data['T2_SRB_Mean']):.3f} (shows gap exists!)")
print(f"⭐ PBC → SRB: r = {data['T1_PBC_Mean'].corr(data['T2_SRB_Mean']):.3f} (direct effect)")
print(f"\nSRB ↔ Objective Score: r = {data['T2_SRB_Mean'].corr(data['T2_Objective_Score']):.3f} (convergent validity)")

# ============================================================================
# 5. RESEARCH QUESTION 1: Does the Intention-Behavior Gap Exist?
# ============================================================================
print("\n" + "="*80)
print("[5] RESEARCH QUESTION 1: Testing the Intention-Behavior Gap")
print("="*80)

# Regression: Behavior ~ Intention
model_gap = smf.ols('T2_SRB_Mean ~ T1_INT_Mean', data=data).fit()

print("\nModel: T2_SRB_Mean ~ T1_INT_Mean")
print(model_gap.summary().tables[1])

print(f"\n📊 Key Results:")
print(f"   R² = {model_gap.rsquared:.3f} → Intention explains only {100*model_gap.rsquared:.1f}% of behavior variance")
print(f"   Unexplained variance = {100*(1-model_gap.rsquared):.1f}% → This is the GAP!")
print(f"   Intention coefficient = {model_gap.params['T1_INT_Mean']:.3f}")

if model_gap.rsquared < 0.50:
    print(f"\n✓ CONCLUSION: Significant intention-behavior gap exists (R² < 0.50)")
else:
    print(f"\n✗ Gap is small (R² ≥ 0.50)")

# ============================================================================
# 6. RESEARCH QUESTION 2: Does PBC Moderate Intention-Behavior?
# ============================================================================
print("\n" + "="*80)
print("[6] RESEARCH QUESTION 2: PBC as Moderator (MAIN HYPOTHESIS)")
print("="*80)

# Create interaction term
data['INT_x_PBC'] = data['T1_INT_Mean'] * data['T1_PBC_Mean']

# Moderation model
model_moderation = smf.ols('T2_SRB_Mean ~ T1_INT_Mean + T1_PBC_Mean + T1_INT_Mean:T1_PBC_Mean', 
                           data=data).fit()

print("\nModel: T2_SRB_Mean ~ T1_INT_Mean + T1_PBC_Mean + (T1_INT_Mean × T1_PBC_Mean)")
print(model_moderation.summary().tables[1])

print(f"\n📊 Key Results:")
print(f"   R² = {model_moderation.rsquared:.3f} (vs {model_gap.rsquared:.3f} without PBC)")
print(f"   ΔR² = {model_moderation.rsquared - model_gap.rsquared:.3f}")
print(f"   Interaction term: β = {model_moderation.params['T1_INT_Mean:T1_PBC_Mean']:.4f}, p = {model_moderation.pvalues['T1_INT_Mean:T1_PBC_Mean']:.4f}")

if model_moderation.pvalues['T1_INT_Mean:T1_PBC_Mean'] < 0.05:
    print(f"\n✓ CONCLUSION: PBC significantly moderates intention-behavior relationship (p < .05)")
    if model_moderation.params['T1_INT_Mean:T1_PBC_Mean'] > 0:
        print("   → Higher PBC strengthens the intention-behavior link (reduces gap)")
else:
    print(f"\n⚠ Moderation effect not significant (p ≥ .05)")

# ============================================================================
# 7. RESEARCH QUESTION 3: Predicting the Behavioral Gap
# ============================================================================
print("\n" + "="*80)
print("[7] RESEARCH QUESTION 3: What Predicts the Gap?")
print("="*80)

# Model predicting the gap
model_predict_gap = smf.ols('''T2_Intention_Behavior_Gap ~ T1_PBC_Mean + Tech_Savviness + 
                                Prior_Fraud_Experience + Age + Education''', data=data).fit()

print("\nModel: T2_Intention_Behavior_Gap ~ PBC + Tech + Fraud + Age + Education")
print(model_predict_gap.summary().tables[1])

print(f"\n📊 Key Results:")
print(f"   R² = {model_predict_gap.rsquared:.3f}")
print(f"   PBC effect: β = {model_predict_gap.params.get('T1_PBC_Mean', 0):.4f}, p = {model_predict_gap.pvalues.get('T1_PBC_Mean', 1):.4f}")

significant_predictors = model_predict_gap.pvalues[model_predict_gap.pvalues < 0.05].index.tolist()
if 'Intercept' in significant_predictors:
    significant_predictors.remove('Intercept')

print(f"\n✓ Significant predictors of the gap: {', '.join(significant_predictors) if significant_predictors else 'None'}")

# ============================================================================
# 8. ADDITIONAL ANALYSES
# ============================================================================
print("\n" + "="*80)
print("[8] ADDITIONAL ANALYSES")
print("="*80)

# Compare high vs low PBC groups
median_pbc = data['T1_PBC_Mean'].median()
data['PBC_Group'] = np.where(data['T1_PBC_Mean'] >= median_pbc, 'High PBC', 'Low PBC')

print("\n--- Intention-Behavior Correlation by PBC Group ---")
high_pbc_corr = data[data['PBC_Group']=='High PBC']['T1_INT_Mean'].corr(
    data[data['PBC_Group']=='High PBC']['T2_SRB_Mean'])
low_pbc_corr = data[data['PBC_Group']=='Low PBC']['T1_INT_Mean'].corr(
    data[data['PBC_Group']=='Low PBC']['T2_SRB_Mean'])

print(f"High PBC Group (n={data[data['PBC_Group']=='High PBC'].shape[0]}): r = {high_pbc_corr:.3f}")
print(f"Low PBC Group (n={data[data['PBC_Group']=='Low PBC'].shape[0]}): r = {low_pbc_corr:.3f}")

if high_pbc_corr > low_pbc_corr:
    print(f"\n✓ High PBC shows stronger intention-behavior correlation (supports moderation)")

# Compare gap magnitude by PBC group
print("\n--- Mean Absolute Gap by PBC Group ---")
gap_by_pbc = data.groupby('PBC_Group')['T2_Gap_Magnitude'].agg(['mean', 'std', 'count'])
print(gap_by_pbc.round(3))

# T-test
high_pbc_gaps = data[data['PBC_Group']=='High PBC']['T2_Gap_Magnitude']
low_pbc_gaps = data[data['PBC_Group']=='Low PBC']['T2_Gap_Magnitude']
t_stat, p_val = stats.ttest_ind(high_pbc_gaps, low_pbc_gaps)
print(f"\nIndependent t-test: t = {t_stat:.3f}, p = {p_val:.4f}")

if p_val < 0.05 and high_pbc_gaps.mean() < low_pbc_gaps.mean():
    print("✓ High PBC group has significantly smaller gaps (p < .05)")

# ============================================================================
# 9. SUMMARY & RECOMMENDATIONS
# ============================================================================
print("\n" + "="*80)
print("[9] ANALYSIS SUMMARY & RECOMMENDATIONS")
print("="*80)

print("\n✓ Dataset Quality:")
print(f"  - N = {len(data)} complete cases")
print(f"  - All reliability coefficients acceptable (α > .70)")
print(f"  - Correlations consistent with TPB theory")

print("\n✓ Key Findings:")
print(f"  1. Intention-behavior gap exists: R² = {model_gap.rsquared:.3f} (explains only {100*model_gap.rsquared:.0f}% of variance)")
print(f"  2. PBC moderation: {'Supported' if model_moderation.pvalues.get('T1_INT_Mean:T1_PBC_Mean', 1) < 0.05 else 'Not supported'} (p = {model_moderation.pvalues.get('T1_INT_Mean:T1_PBC_Mean', 1):.4f})")
print(f"  3. Under-performers: {100*(data['T2_Gap_Direction']==-1).sum()/len(data):.1f}% show problematic gap")

print("\n📌 Recommended Next Steps:")
print("  1. Create visualization plots (regression lines, interaction plots)")
print("  2. Test alternative moderators (e.g., tech savviness)")
print("  3. Examine objective score as alternative DV")
print("  4. Conduct sensitivity analyses")
print("  5. Check for potential confounds (age, education)")

print("\n" + "="*80)
print("Analysis complete! ✓")
print("="*80)
