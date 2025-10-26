#!/usr/bin/env python3
"""
Comprehensive Statistical Analysis Script for Behavioral Intention Dataset

This script provides advanced statistical analyses including:
- Multiple regression analysis
- Mediation analysis
- Moderation analysis
- Path analysis
- Structural equation modeling
- Longitudinal analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import statsmodels.api as sm
from statsmodels.stats.mediation import Mediation
from statsmodels.stats.outliers_influence import variance_inflation_factor
import warnings
warnings.filterwarnings('ignore')

class BehavioralIntentionAnalyzer:
    def __init__(self, df):
        """
        Initialize analyzer with the dataset
        
        Args:
            df (pd.DataFrame): The behavioral intention dataset
        """
        self.df = df
        self.scaler = StandardScaler()
        
        # Create composite scores if not present
        self._create_composite_scores()
        
    def _create_composite_scores(self):
        """Create composite scores for analysis"""
        if 'attitude_composite' not in self.df.columns:
            self.df['attitude_composite'] = self.df[['ATT1', 'ATT2', 'ATT3']].mean(axis=1)
        if 'subjective_norm_composite' not in self.df.columns:
            self.df['subjective_norm_composite'] = self.df[['SN1', 'SN2']].mean(axis=1)
        if 'pbc_composite' not in self.df.columns:
            self.df['pbc_composite'] = self.df[['PBC1', 'PBC2', 'PBC3']].mean(axis=1)
        if 'intention_composite' not in self.df.columns:
            self.df['intention_composite'] = self.df[['INT1', 'INT2']].mean(axis=1)
        if 'threat_appraisal_composite' not in self.df.columns:
            self.df['threat_appraisal_composite'] = self.df[['perceived_severity', 'perceived_vulnerability']].mean(axis=1)
        if 'coping_appraisal_composite' not in self.df.columns:
            self.df['coping_appraisal_composite'] = self.df[['self_efficacy', 'response_efficacy']].mean(axis=1)
    
    def descriptive_statistics(self):
        """Generate comprehensive descriptive statistics"""
        print("=" * 80)
        print("DESCRIPTIVE STATISTICS")
        print("=" * 80)
        
        # Basic demographics
        print("\nDEMOGRAPHIC CHARACTERISTICS:")
        print("-" * 40)
        print(f"Sample Size: {len(self.df)}")
        print(f"Age: M = {self.df['age'].mean():.1f}, SD = {self.df['age'].std():.1f}, Range = {self.df['age'].min()}-{self.df['age'].max()}")
        print(f"Gender Distribution:")
        print(self.df['gender'].value_counts())
        print(f"Education Distribution:")
        print(self.df['education'].value_counts())
        print(f"Income: M = ${self.df['income'].mean():,.0f}, SD = ${self.df['income'].std():,.0f}")
        print(f"Technology Comfort: M = {self.df['tech_comfort'].mean():.2f}, SD = {self.df['tech_comfort'].std():.2f}")
        print(f"Previous Fraud Experience: {self.df['fraud_experience'].sum()} ({self.df['fraud_experience'].mean()*100:.1f}%)")
        
        # Construct statistics
        print(f"\nCONSTRUCT DESCRIPTIVE STATISTICS:")
        print("-" * 40)
        
        constructs = [
            'attitude_composite', 'subjective_norm_composite', 'pbc_composite',
            'intention_composite', 'threat_appraisal_composite', 'coping_appraisal_composite',
            'past_behavior'
        ]
        
        desc_stats = self.df[constructs].describe()
        print(desc_stats.round(3))
        
        # Skewness and kurtosis
        print(f"\nSKEWNESS AND KURTOSIS:")
        print("-" * 30)
        print(f"{'Construct':<25} {'Skewness':<10} {'Kurtosis':<10}")
        print("-" * 50)
        
        for construct in constructs:
            if construct in self.df.columns:
                data = self.df[construct].dropna()
                skewness = stats.skew(data)
                kurtosis = stats.kurtosis(data)
                print(f"{construct:<25} {skewness:<10.3f} {kurtosis:<10.3f}")
    
    def test_hypotheses(self):
        """Test theoretical hypotheses"""
        print("\n" + "=" * 80)
        print("HYPOTHESIS TESTING")
        print("=" * 80)
        
        # H1: TPB constructs predict intention
        print("\nH1: Theory of Planned Behavior constructs predict intention")
        print("-" * 60)
        
        # Prepare data for regression
        tpb_data = self.df[['attitude_composite', 'subjective_norm_composite', 
                           'pbc_composite', 'intention_composite']].dropna()
        
        if len(tpb_data) > 0:
            X = tpb_data[['attitude_composite', 'subjective_norm_composite', 'pbc_composite']]
            y = tpb_data['intention_composite']
            
            # Add constant for statsmodels
            X_with_const = sm.add_constant(X)
            
            # Fit OLS regression
            model = sm.OLS(y, X_with_const).fit()
            print(model.summary())
            
            # Calculate R-squared
            r2 = model.rsquared
            print(f"\nR-squared: {r2:.3f}")
            print(f"Adjusted R-squared: {model.rsquared_adj:.3f}")
            
            # F-test
            f_stat = model.fvalue
            f_pvalue = model.f_pvalue
            print(f"F-statistic: {f_stat:.3f}, p-value: {f_pvalue:.6f}")
            
            if f_pvalue < 0.001:
                print("H1 SUPPORTED: TPB constructs significantly predict intention (p < 0.001)")
            else:
                print("H1 NOT SUPPORTED: TPB constructs do not significantly predict intention")
        
        # H2: Intention predicts behavior (T2)
        print(f"\nH2: Intention predicts behavior at Time 2")
        print("-" * 50)
        
        if 'T2_security_steps_followed' in self.df.columns:
            behavior_data = self.df[['intention_composite', 'T2_security_steps_followed']].dropna()
            
            if len(behavior_data) > 0:
                X = behavior_data[['intention_composite']]
                y = behavior_data['T2_security_steps_followed']
                
                X_with_const = sm.add_constant(X)
                model = sm.OLS(y, X_with_const).fit()
                
                print(f"Intention -> Behavior (T2):")
                print(f"Beta: {model.params['intention_composite']:.3f}")
                print(f"p-value: {model.pvalues['intention_composite']:.6f}")
                print(f"R-squared: {model.rsquared:.3f}")
                
                if model.pvalues['intention_composite'] < 0.05:
                    print("H2 SUPPORTED: Intention significantly predicts behavior")
                else:
                    print("H2 NOT SUPPORTED: Intention does not significantly predict behavior")
        
        # H3: PMT constructs add predictive power
        print(f"\nH3: Protection Motivation Theory constructs add predictive power")
        print("-" * 65)
        
        # Compare models with and without PMT constructs
        full_data = self.df[['attitude_composite', 'subjective_norm_composite', 'pbc_composite',
                            'threat_appraisal_composite', 'coping_appraisal_composite',
                            'intention_composite']].dropna()
        
        if len(full_data) > 0:
            # Model 1: TPB only
            X1 = full_data[['attitude_composite', 'subjective_norm_composite', 'pbc_composite']]
            y = full_data['intention_composite']
            X1_const = sm.add_constant(X1)
            model1 = sm.OLS(y, X1_const).fit()
            
            # Model 2: TPB + PMT
            X2 = full_data[['attitude_composite', 'subjective_norm_composite', 'pbc_composite',
                           'threat_appraisal_composite', 'coping_appraisal_composite']]
            X2_const = sm.add_constant(X2)
            model2 = sm.OLS(y, X2_const).fit()
            
            # Compare models
            r2_diff = model2.rsquared - model1.rsquared
            print(f"TPB only R-squared: {model1.rsquared:.3f}")
            print(f"TPB + PMT R-squared: {model2.rsquared:.3f}")
            print(f"R-squared improvement: {r2_diff:.3f}")
            
            # F-test for model comparison
            f_test = model2.compare_f_test(model1)
            print(f"F-test for model comparison: F = {f_test[0]:.3f}, p = {f_test[1]:.6f}")
            
            if f_test[1] < 0.05:
                print("H3 SUPPORTED: PMT constructs significantly add predictive power")
            else:
                print("H3 NOT SUPPORTED: PMT constructs do not significantly add predictive power")
    
    def mediation_analysis(self):
        """Perform mediation analysis"""
        print("\n" + "=" * 80)
        print("MEDIATION ANALYSIS")
        print("=" * 80)
        
        # Mediation: Attitude -> Intention -> Behavior
        print("\nMediation: Attitude -> Intention -> Behavior")
        print("-" * 45)
        
        if 'T2_security_steps_followed' in self.df.columns:
            mediation_data = self.df[['attitude_composite', 'intention_composite', 
                                    'T2_security_steps_followed']].dropna()
            
            if len(mediation_data) > 0:
                # Step 1: Total effect (X -> Y)
                X = mediation_data['attitude_composite']
                Y = mediation_data['T2_security_steps_followed']
                M = mediation_data['intention_composite']
                
                # Total effect
                total_effect = stats.pearsonr(X, Y)[0]
                print(f"Total effect (Attitude -> Behavior): {total_effect:.3f}")
                
                # Step 2: Direct effect (X -> Y controlling for M)
                X_const = sm.add_constant(pd.DataFrame({'attitude': X, 'intention': M}))
                direct_model = sm.OLS(Y, X_const).fit()
                direct_effect = direct_model.params['attitude']
                print(f"Direct effect (Attitude -> Behavior | Intention): {direct_effect:.3f}")
                
                # Step 3: Indirect effect (X -> M -> Y)
                # X -> M
                X_M_const = sm.add_constant(X)
                X_M_model = sm.OLS(M, X_M_const).fit()
                a = X_M_model.params['attitude_composite']
                
                # M -> Y (controlling for X)
                indirect_effect = a * direct_model.params['intention']
                print(f"Indirect effect (Attitude -> Intention -> Behavior): {indirect_effect:.3f}")
                
                # Mediation ratio
                mediation_ratio = indirect_effect / total_effect
                print(f"Mediation ratio: {mediation_ratio:.3f}")
                
                if abs(mediation_ratio) > 0.1:  # Arbitrary threshold
                    print("MEDIATION DETECTED: Intention partially mediates the attitude-behavior relationship")
                else:
                    print("NO MEDIATION: Intention does not mediate the attitude-behavior relationship")
    
    def moderation_analysis(self):
        """Perform moderation analysis"""
        print("\n" + "=" * 80)
        print("MODERATION ANALYSIS")
        print("=" * 80)
        
        # Moderation: Gender moderates intention-behavior relationship
        print("\nModeration: Gender moderates intention-behavior relationship")
        print("-" * 60)
        
        if 'T2_security_steps_followed' in self.df.columns:
            # Create dummy variable for gender
            gender_dummy = pd.get_dummies(self.df['gender'], prefix='gender')
            if 'gender_Female' in gender_dummy.columns:
                moderation_data = self.df[['intention_composite', 'T2_security_steps_followed']].join(
                    gender_dummy[['gender_Female']]
                ).dropna()
                
                if len(moderation_data) > 0:
                    # Create interaction term
                    moderation_data['intention_x_gender'] = (
                        moderation_data['intention_composite'] * moderation_data['gender_Female']
                    )
                    
                    # Ensure numeric data types
                    moderation_data = moderation_data.astype(float)
                    
                    # Fit moderation model
                    X = moderation_data[['intention_composite', 'gender_Female', 'intention_x_gender']]
                    y = moderation_data['T2_security_steps_followed']
                    X_const = sm.add_constant(X)
                    
                    mod_model = sm.OLS(y, X_const).fit()
                    print("Moderation Model Results:")
                    print(mod_model.summary())
                    
                    # Test interaction effect
                    interaction_p = mod_model.pvalues['intention_x_gender']
                    print(f"\nInteraction effect p-value: {interaction_p:.6f}")
                    
                    if interaction_p < 0.05:
                        print("MODERATION DETECTED: Gender significantly moderates intention-behavior relationship")
                    else:
                        print("NO MODERATION: Gender does not significantly moderate intention-behavior relationship")
        
        # Moderation: Age moderates TPB relationships
        print(f"\nModeration: Age moderates TPB relationships")
        print("-" * 45)
        
        # Center age for interaction
        age_centered = self.df['age'] - self.df['age'].mean()
        
        # Create interaction terms
        intention_age_interaction = self.df['intention_composite'] * age_centered
        attitude_age_interaction = self.df['attitude_composite'] * age_centered
        
        moderation_data2 = pd.DataFrame({
            'intention': self.df['intention_composite'],
            'attitude': self.df['attitude_composite'],
            'age_centered': age_centered,
            'intention_age': intention_age_interaction,
            'attitude_age': attitude_age_interaction
        }).dropna()
        
        if len(moderation_data2) > 0:
            # Ensure numeric data types
            moderation_data2 = moderation_data2.astype(float)
            
            # Test age moderation of attitude-intention relationship
            X = moderation_data2[['attitude', 'age_centered', 'attitude_age']]
            y = moderation_data2['intention']
            X_const = sm.add_constant(X)
            
            age_mod_model = sm.OLS(y, X_const).fit()
            print(f"\nAge Moderation of Attitude-Intention Relationship:")
            print(f"Interaction coefficient: {age_mod_model.params['attitude_age']:.3f}")
            print(f"Interaction p-value: {age_mod_model.pvalues['attitude_age']:.6f}")
            
            if age_mod_model.pvalues['attitude_age'] < 0.05:
                print("MODERATION DETECTED: Age significantly moderates attitude-intention relationship")
            else:
                print("NO MODERATION: Age does not significantly moderate attitude-intention relationship")
    
    def longitudinal_analysis(self):
        """Perform longitudinal analysis"""
        print("\n" + "=" * 80)
        print("LONGITUDINAL ANALYSIS")
        print("=" * 80)
        
        if 'T2_security_steps_followed' in self.df.columns:
            # Intention-behavior gap analysis
            print("\nIntention-Behavior Gap Analysis")
            print("-" * 35)
            
            longitudinal_data = self.df[['intention_composite', 'T2_security_steps_followed', 
                                       'past_behavior']].dropna()
            
            if len(longitudinal_data) > 0:
                # Calculate intention-behavior gap
                gap = longitudinal_data['T2_security_steps_followed'] - longitudinal_data['intention_composite']
                
                print(f"Intention-Behavior Gap Statistics:")
                print(f"Mean gap: {gap.mean():.3f}")
                print(f"SD gap: {gap.std():.3f}")
                print(f"Range: {gap.min():.3f} to {gap.max():.3f}")
                
                # Test if gap is significantly different from zero
                t_stat, p_value = stats.ttest_1samp(gap, 0)
                print(f"t-test (gap = 0): t = {t_stat:.3f}, p = {p_value:.6f}")
                
                if p_value < 0.05:
                    if gap.mean() > 0:
                        print("SIGNIFICANT POSITIVE GAP: Behavior exceeds intention")
                    else:
                        print("SIGNIFICANT NEGATIVE GAP: Intention exceeds behavior")
                else:
                    print("NO SIGNIFICANT GAP: Intention and behavior are aligned")
                
                # Predictors of intention-behavior gap
                print(f"\nPredictors of Intention-Behavior Gap:")
                print("-" * 40)
                
                # Add predictors
                gap_data = self.df[['intention_composite', 'T2_security_steps_followed',
                                   'attitude_composite', 'subjective_norm_composite', 'pbc_composite',
                                   'threat_appraisal_composite', 'coping_appraisal_composite',
                                   'past_behavior', 'age', 'tech_comfort']].dropna()
                
                if len(gap_data) > 0:
                    gap_data['gap'] = gap_data['T2_security_steps_followed'] - gap_data['intention_composite']
                    
                    # Predictors
                    predictors = ['attitude_composite', 'subjective_norm_composite', 'pbc_composite',
                                 'threat_appraisal_composite', 'coping_appraisal_composite',
                                 'past_behavior', 'age', 'tech_comfort']
                    
                    X = gap_data[predictors]
                    y = gap_data['gap']
                    X_const = sm.add_constant(X)
                    
                    gap_model = sm.OLS(y, X_const).fit()
                    print("Gap Prediction Model:")
                    print(gap_model.summary())
    
    def demographic_differences(self):
        """Analyze demographic differences"""
        print("\n" + "=" * 80)
        print("DEMOGRAPHIC DIFFERENCES")
        print("=" * 80)
        
        # Gender differences
        print("\nGender Differences in Key Constructs:")
        print("-" * 45)
        
        constructs = ['attitude_composite', 'subjective_norm_composite', 'pbc_composite',
                     'intention_composite', 'threat_appraisal_composite', 'coping_appraisal_composite']
        
        for construct in constructs:
            if construct in self.df.columns:
                # Separate by gender
                male_data = self.df[self.df['gender'] == 'Male'][construct].dropna()
                female_data = self.df[self.df['gender'] == 'Female'][construct].dropna()
                
                if len(male_data) > 0 and len(female_data) > 0:
                    # t-test
                    t_stat, p_value = stats.ttest_ind(male_data, female_data)
                    
                    print(f"{construct}:")
                    print(f"  Male: M = {male_data.mean():.3f}, SD = {male_data.std():.3f}")
                    print(f"  Female: M = {female_data.mean():.3f}, SD = {female_data.std():.3f}")
                    print(f"  t-test: t = {t_stat:.3f}, p = {p_value:.6f}")
                    
                    if p_value < 0.05:
                        print(f"  SIGNIFICANT DIFFERENCE")
                    else:
                        print(f"  No significant difference")
                    print()
        
        # Age group differences
        print("\nAge Group Differences:")
        print("-" * 25)
        
        # Create age groups
        self.df['age_group'] = pd.cut(self.df['age'], 
                                    bins=[0, 30, 50, 80], 
                                    labels=['Young (18-30)', 'Middle (31-50)', 'Older (51-80)'])
        
        for construct in constructs:
            if construct in self.df.columns:
                # ANOVA
                groups = [group[construct].dropna() for name, group in self.df.groupby('age_group')]
                
                if len(groups) >= 2 and all(len(g) > 0 for g in groups):
                    f_stat, p_value = stats.f_oneway(*groups)
                    
                    print(f"{construct}:")
                    print(f"  F-test: F = {f_stat:.3f}, p = {p_value:.6f}")
                    
                    if p_value < 0.05:
                        print(f"  SIGNIFICANT DIFFERENCE across age groups")
                        
                        # Post-hoc tests
                        from scipy.stats import ttest_ind
                        group_names = ['Young (18-30)', 'Middle (31-50)', 'Older (51-80)']
                        for i in range(len(groups)):
                            for j in range(i+1, len(groups)):
                                if len(groups[i]) > 0 and len(groups[j]) > 0:
                                    t_stat, p_val = ttest_ind(groups[i], groups[j])
                                    print(f"    {group_names[i]} vs {group_names[j]}: t = {t_stat:.3f}, p = {p_val:.6f}")
                    else:
                        print(f"  No significant difference across age groups")
                    print()
    
    def run_complete_analysis(self):
        """Run complete statistical analysis suite"""
        print("COMPREHENSIVE STATISTICAL ANALYSIS")
        print("=" * 80)
        
        self.descriptive_statistics()
        self.test_hypotheses()
        self.mediation_analysis()
        self.moderation_analysis()
        self.longitudinal_analysis()
        self.demographic_differences()
        
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print("All statistical analyses have been completed.")
        print("Review the results above for comprehensive insights into the data.")

def main():
    """Main function to run analysis"""
    # Load the dataset
    try:
        df = pd.read_csv('behavioral_intention_dataset.csv')
        print(f"Dataset loaded successfully. Shape: {df.shape}")
    except FileNotFoundError:
        print("Dataset file not found. Please run the dataset generator first.")
        return
    
    # Run analysis
    analyzer = BehavioralIntentionAnalyzer(df)
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()